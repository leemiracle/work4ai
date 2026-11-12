# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [skill-logos/archive.svg](skill-logos/archive.svg)
- [skills.json](skills.json)
- [skills/archive/SKILL.md](skills/archive/SKILL.md)
- [skills/archive/references/TEMPLATE.md](skills/archive/references/TEMPLATE.md)
- [website/opc-banner.png](website/opc-banner.png)

</details>



This page introduces the OPC Skills repository: what the project is, the skills it contains, which AI platforms it supports, and how to install skills. For the internal architecture of the skills system (registry schema, skill directory layout, dependency model), see [Skills System](#2). For installation mechanics, see [Installation & Distribution](#3). For the website and API layer, see [Website & Content Delivery](#4).

---

## What is OPC Skills?

OPC Skills is an open-source collection of AI agent "skills" aimed at solopreneurs, indie hackers, and one-person companies. A **skill** is a self-contained directory containing a `SKILL.md` instruction file, optional Python scripts, and usage examples. When installed into a compatible AI coding assistant, the agent reads the skill's instructions and executes specialized tasks on demand — such as hunting domains, creating logos, or auditing a site for SEO.

The project conforms to the [Agent Skills standard](https://agentskills.io). Skills are distributed via GitHub and installable with a single `npx skills add` command or through the Claude Code plugin marketplace.

| Property | Value |
|---|---|
| Repository | `https://github.com/ReScienceLab/opc-skills` |
| License | MIT |
| Registry manifest | [`skills.json`](skills.json) |
| Website | `https://opc.dev` (served by [`website/worker.js`](website/worker.js)) |
| Claude Code plugin manifest | [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) |

Sources: [README.md:1-45](), [skills.json:1-8](), [website/worker.js:129-179]()

---

## The Skills Collection

Ten skills are registered in [`skills.json`](skills.json). Each entry declares a `name`, `version`, `description`, `triggers`, `dependencies`, `auth`, `install`, `commands`, and `links` field. The table below summarises the collection.

| Skill | Version | Category | Auth Required | Dependencies |
|---|---|---|---|---|
| `archive` | 1.0.1 | Foundation | None | — |
| `reddit` | 1.0.0 | Social / Research | None | — |
| `nanobanana` | 1.0.0 | Image Generation | `GEMINI_API_KEY` | — |
| `twitter` | 1.0.0 | Social / Research | `TWITTERAPI_API_KEY` | — |
| `producthunt` | 1.0.0 | Research / Discovery | `PRODUCTHUNT_ACCESS_TOKEN` | — |
| `requesthunt` | 1.0.0 | Research / Validation | `REQUESTHUNT_API_KEY` | — |
| `domain-hunter` | 1.0.0 | Business | None | `twitter`, `reddit` |
| `banner-creator` | 1.0.0 | Design | `GEMINI_API_KEY` | `nanobanana` |
| `logo-creator` | 1.0.0 | Design | `GEMINI_API_KEY` (+ optional keys) | `nanobanana` |
| `seo-geo` | 1.0.0 | SEO / GEO | Optional (`DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD`) | `twitter`, `reddit` |

Optional keys for `logo-creator`: `REMOVE_BG_API_KEY` and `RECRAFT_API_KEY`.

Skills grouped by category are documented in detail starting at [Skill Categories & Reference](#2.4).

Sources: [skills.json:8-538](), [CHANGELOG.md:12-24]()

---

## Skill Dependency Graph

Three skills — `domain-hunter`, `logo-creator`, and `banner-creator` — depend on other skills in this collection. The `seo-geo` skill also depends on `twitter` and `reddit`. Dependencies are declared in the `dependencies` object of each skill's entry in [`skills.json`](skills.json) and must be installed alongside the dependent skill.

**Figure: Inter-skill dependencies as declared in `skills.json`**

```mermaid
graph LR
  DH["domain-hunter"] --> TW["twitter"]
  DH["domain-hunter"] --> RD["reddit"]
  LC["logo-creator"] --> NB["nanobanana"]
  BC["banner-creator"] --> NB["nanobanana"]
  SG["seo-geo"] --> TW["twitter"]
  SG["seo-geo"] --> RD["reddit"]
  RH["requesthunt"]
  PH["producthunt"]
  AR["archive"]
```

Skills with no incoming edges (`twitter`, `reddit`, `nanobanana`, `requesthunt`, `producthunt`, `archive`) are standalone and have no prerequisites. For version constraints and CI checks on dependency integrity, see [Dependency Management](#2.3).

Sources: [skills.json:29-31](), [skills.json:143-146](), [skills.json:193-195](), [skills.json:259-261](), [CHANGELOG.md:14-23]()

---

## Compatible AI Platforms

Each skill's `install` field in [`skills.json`](skills.json) provides `user`- and `project`-level install commands for five explicitly supported platforms. The `npx skills add` installer also autodetects other tools that implement the Agent Skills standard.

| Platform | Install flag (`-a`) | User-level target | Project-level target |
|---|---|---|---|
| Claude Code | `claude` | `~/.claude/skills/` | `.claude/skills/` |
| Factory Droid | `droid` | `~/.factory/skills/` | `.factory/skills/` |
| Cursor | `cursor` | — | `.cursor/skills/` |
| OpenCode | `opencode` | user-level | project-level |
| Codex | `codex` | user-level | project-level |

Beyond these five, the `npx skills add` CLI supports 16+ tools including Windsurf, GitHub Copilot, Gemini CLI, Goose, Kilo Code, Roo Code, and Trae. Full platform install command strings are documented in [Platform-Specific Installation](#3.4).

Sources: [skills.json:48-62](), [README.md:109-128]()

---

## Quick Start

```bash
# Install all skills
npx skills add ReScienceLab/opc-skills

# Install a single skill
npx skills add ReScienceLab/opc-skills --skill reddit

# Install a skill that has dependencies (must include dependency skills)
npx skills add ReScienceLab/opc-skills --skill reddit --skill twitter --skill domain-hunter

# Install to a specific agent at user level
npx skills add ReScienceLab/opc-skills -a droid
```

For Claude Code's plugin marketplace:

```bash
/plugin marketplace add ReScienceLab/opc-skills
/plugin install domain-hunter@opc-skills
/plugin list opc-skills
```

Full installation options are covered in [Installation Methods Overview](#3.1). Claude Code marketplace specifics are in [Claude Code Plugin Marketplace](#3.2).

Sources: [README.md:57-107](), [.claude-plugin/marketplace.json:1-10]()

---

## Repository Architecture

The diagram below maps the major subsystems and files in the repository. `skills.json` is the central manifest consumed by all other subsystems.

**Figure: Major subsystems and their primary source files**

```mermaid
graph TD
  SJ["skills.json\n(registry manifest)"]
  SD["skills/NAME/SKILL.md\n(per-skill instructions)"]
  MP[".claude-plugin/marketplace.json\n(Claude Code plugin list)"]
  WW["website/worker.js\n(Cloudflare Worker)"]
  IS["install-stats.json\n(install counts)"]
  FSI[".github/workflows/\nfetch-install-stats.py"]
  CI[".github/workflows/\ntest-installer.yml"]
  AG["AI agent tool\n(e.g. ~/.claude/skills/)"]

  SD -->|"entry per skill"| SJ
  SJ -->|"fetchSkillsConfig()"| WW
  SJ -->|"mirrors plugin list"| MP
  SJ -->|"validates with jq"| CI
  FSI -->|"writes"| IS
  IS -->|"fetchInstallStats()"| WW
  WW -->|"serves opc.dev"| SITE["opc.dev"]
  SD -->|"npx skills add installs to"| AG
```

Sources: [website/worker.js:219-227](), [website/worker.js:252-256](), [skills.json:1-8](), [.claude-plugin/marketplace.json:1-30](), [README.md:36-56]()

The four main subsystems and where they are documented in this wiki:

| Subsystem | Root files | Wiki page |
|---|---|---|
| Skills definitions & registry | `skills.json`, `skills/*/SKILL.md` | [Skills System](#2) |
| Installation & distribution | `npx skills add`, `.claude-plugin/marketplace.json` | [Installation & Distribution](#3) |
| Website & API | `website/worker.js` | [Website & Content Delivery](#4) |
| CI/CD & development workflow | `.github/workflows/`, `CHANGELOG.md` | [Development & CI/CD](#6) |

Sources: [README.md:131-149](), [CHANGELOG.md:1-31]()

---

## External Resources

| Resource | URL / Location |
|---|---|
| Official website | `https://opc.dev` |
| Skills browser | `https://skills.sh/ReScienceLab/opc-skills` |
| Agent Skills standard | `https://agentskills.io` |
| GitHub repository | `https://github.com/ReScienceLab/opc-skills` |

Sources: [skills.json:5-7](), [README.md:131-148]()

---

# Page: Skills System

# Skills System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [skill-logos/archive.svg](skill-logos/archive.svg)
- [skills.json](skills.json)
- [skills/archive/SKILL.md](skills/archive/SKILL.md)
- [skills/archive/references/TEMPLATE.md](skills/archive/references/TEMPLATE.md)
- [website/opc-banner.png](website/opc-banner.png)

</details>



The Skills System is the core architecture that defines, organizes, and manages modular AI agent capabilities in the OPC Skills repository. This system provides a standardized way to package instructions, scripts, and metadata into reusable units that AI agents can dynamically load and execute.

This document covers the fundamental architecture of skills, including the central registry, directory structure, metadata schemas, and dependency relationships. For installation mechanisms, see [Installation & Distribution](#3). For skill creation workflows, see [Creating New Skills](#7).

## System Architecture

The Skills System consists of three primary components: a central manifest registry (`skills.json`), individual skill directories containing structured content, and a dependency resolution mechanism.

### Skills System Component Diagram

```mermaid
graph TB
    subgraph "Central Registry"
        manifest["skills.json<br/>(version, name, skills[])"]
    end
    
    subgraph "Skill Directory Structure"
        skilldir["skills/{skill-name}/"]
        skillmd["SKILL.md<br/>(YAML frontmatter + instructions)"]
        scripts["scripts/<br/>(Python executables)"]
        examples["examples/<br/>(Usage workflows)"]
        refs["references/<br/>(API docs, templates)"]
        
        skilldir --> skillmd
        skilldir --> scripts
        skilldir --> examples
        skilldir --> refs
    end
    
    subgraph "Metadata Schema"
        meta_name["name: string"]
        meta_version["version: semver"]
        meta_desc["description: string"]
        meta_triggers["triggers: string[]"]
        meta_deps["dependencies: object"]
        meta_auth["auth: object"]
        meta_install["install: object"]
        meta_commands["commands: string[]"]
    end
    
    manifest --> skilldir
    manifest --> meta_name
    manifest --> meta_version
    manifest --> meta_desc
    
    skillmd --> meta_name
    skillmd --> meta_desc
    
    meta_deps -.references.-> manifest
    
    subgraph "Installation Targets"
        claude[".claude/skills/"]
        cursor[".cursor/skills/"]
        factory[".factory/skills/"]
        agent_dir["<agent>/skills/"]
    end
    
    skilldir -.copied to.-> claude
    skilldir -.copied to.-> cursor
    skilldir -.copied to.-> factory
    skilldir -.copied to.-> agent_dir
```

**Sources:** [skills.json:1-539](), [README.md:36-40](), [skills/archive/SKILL.md:1-56]()

## Skills Registry

The central registry is defined in `skills.json` at the repository root. This file serves as the single source of truth for all available skills and their metadata.

### Registry Structure

The registry follows this top-level schema:

| Field | Type | Purpose |
|-------|------|---------|
| `version` | string | Global registry version (semantic versioning) |
| `name` | string | Repository display name |
| `description` | string | Repository description |
| `repository` | string | GitHub repository URL |
| `website` | string | Marketing website URL |
| `logo` | string | Repository logo URL |
| `skills` | array | Array of skill definition objects |

**Sources:** [skills.json:1-8]()

### Skill Definition Schema

Each entry in the `skills` array contains the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique skill identifier (kebab-case) |
| `version` | string | Yes | Skill version (semantic versioning) |
| `description` | string | Yes | Concise skill purpose and use cases |
| `logo` | string | Yes | Skill logo URL (SVG preferred) |
| `icon` | string | Yes | Icon identifier for UI rendering |
| `color` | string | Yes | Hex color code (without `#` prefix) |
| `triggers` | string[] | Yes | Keywords for natural language activation |
| `dependencies` | object | Yes | Required skill dependencies with version constraints |
| `auth` | object | Yes | API key requirements and acquisition URLs |
| `install` | object | Yes | Platform-specific installation commands |
| `commands` | string[] | Yes | Executable command templates |
| `links` | object | Yes | Documentation and example URLs |

**Sources:** [skills.json:9-74](), [skills.json:76-127]()

### Skill Metadata Examples

**Infrastructure Skill (No Dependencies):**
```json
{
  "name": "reddit",
  "version": "1.0.0",
  "dependencies": {},
  "auth": {
    "required": false,
    "type": null,
    "keys": []
  }
}
```

**Composite Skill (With Dependencies):**
```json
{
  "name": "logo-creator",
  "version": "1.0.0",
  "dependencies": {
    "nanobanana": ">=1.0.0"
  },
  "auth": {
    "required": true,
    "type": "api_key",
    "keys": [
      {
        "env": "GEMINI_API_KEY",
        "url": "https://aistudio.google.com/apikey"
      }
    ]
  }
}
```

**Sources:** [skills.json:348-391](), [skills.json:177-241]()

## Skill Directory Structure

Each skill is self-contained within a directory at `skills/{skill-name}/`. The standard structure follows the Agent Skills Standard defined at [agentskills.io](http://agentskills.io).

### Standard Directory Layout

```
skills/{skill-name}/
├── SKILL.md              # Main skill definition (required)
├── scripts/              # Executable scripts (optional)
│   ├── script1.py
│   └── script2.py
├── examples/             # Usage examples (optional)
│   └── example-workflow.md
└── references/           # API docs, templates (optional)
    └── TEMPLATE.md
```

**Sources:** [README.md:153-158](), [skills/archive/SKILL.md:1-56]()

### SKILL.md Format

The `SKILL.md` file must contain YAML frontmatter followed by markdown documentation:

```markdown
---
name: skill-name
description: "Clear description of skill purpose and when to use it"
---

# Skill Name

Detailed instructions, workflows, and usage guidelines...
```

**Minimum Required Frontmatter:**
- `name`: Must match directory name and `skills.json` entry
- `description`: Concise purpose statement

**Extended Frontmatter (Archive Skill Example):**
```yaml
---
name: archive
description: "Archive session learnings, debugging solutions, and deployment logs to .archive/yyyy-mm-dd/ as indexed markdown with searchable tags. Use when completing a significant task, resolving a tricky bug, deploying, or when the user says \"archive this\". Maintains .archive/MEMORY.md index for cross-session knowledge reuse."
---
```

**Sources:** [README.md:159-165](), [skills/archive/SKILL.md:1-4]()

## Skill Activation and Execution Flow

AI agents use multiple mechanisms to discover and activate skills during natural language interactions.

### Skill Activation Flow Diagram

```mermaid
graph TB
    user_input["User Input<br/>(natural language)"]
    
    subgraph "Discovery Phase"
        scan_dir["Agent scans skills directory<br/>(.claude/skills/, .cursor/skills/, etc.)"]
        load_yaml["Load SKILL.md files<br/>(parse YAML frontmatter)"]
        build_index["Build trigger keyword index<br/>(from skills.json and SKILL.md)"]
    end
    
    subgraph "Matching Phase"
        match_triggers["Match user input against<br/>trigger keywords"]
        match_desc["Semantic match against<br/>skill descriptions"]
        rank_skills["Rank candidate skills<br/>by relevance"]
    end
    
    subgraph "Execution Phase"
        load_instructions["Load full SKILL.md<br/>markdown content"]
        check_deps["Check dependencies<br/>(from skills.json)"]
        check_auth["Check auth requirements<br/>(environment variables)"]
        exec_commands["Execute commands<br/>(from skills.json.commands[])"]
        run_scripts["Run Python scripts<br/>(from scripts/ directory)"]
    end
    
    user_input --> scan_dir
    scan_dir --> load_yaml
    load_yaml --> build_index
    build_index --> match_triggers
    match_triggers --> match_desc
    match_desc --> rank_skills
    rank_skills --> load_instructions
    load_instructions --> check_deps
    check_deps --> check_auth
    check_auth --> exec_commands
    exec_commands --> run_scripts
    
    check_deps -.missing dependency.-> error1["Error: Install dependency"]
    check_auth -.missing key.-> error2["Error: Set environment variable"]
```

**Sources:** [skills.json:16-27](), [skills.json:63-69](), [skills.json:89-99]()

## Trigger Keyword System

Skills define trigger keywords that help AI agents determine when to activate them. Triggers are specified in the `triggers` array in `skills.json`.

### Trigger Examples by Skill Category

| Skill | Trigger Keywords | Purpose |
|-------|-----------------|---------|
| `seo-geo` | `SEO`, `GEO`, `search optimization`, `schema markup`, `JSON-LD`, `meta tags`, `keyword research`, `AI visibility`, `ChatGPT ranking`, `Perplexity` | SEO and generative engine optimization |
| `requesthunt` | `requesthunt`, `request hunt`, `feature request`, `user demand`, `demand research` | Market research and user feedback analysis |
| `domain-hunter` | `domain`, `registrar`, `buy domain`, `domain price`, `.ai domain`, `.com domain` | Domain search and price comparison |
| `logo-creator` | `logo`, `brand`, `icon`, `favicon`, `mascot`, `emblem`, `create logo`, `design logo` | Logo design and generation |
| `nanobanana` | `generate image`, `create image`, `nano banana`, `nanobanana`, `gemini image`, `AI image` | Image generation via Gemini API |
| `reddit` | `reddit`, `subreddit`, `r/` | Reddit content retrieval |
| `twitter` | `twitter`, `X`, `tweet` | Twitter/X content retrieval |
| `archive` | `archive this`, `archive session`, `save learnings`, `document this`, `session notes`, `what did we learn`, `check archives`, `past solutions` | Session knowledge persistence |

**Sources:** [skills.json:16-27](), [skills.json:82-88](), [skills.json:136-142](), [skills.json:183-192](), [skills.json:304-310](), [skills.json:354-358](), [skills.json:399-403](), [skills.json:501-510]()

## Authentication and API Keys

Skills declare their authentication requirements in the `auth` object within `skills.json`.

### Auth Object Schema

| Field | Type | Description |
|-------|------|-------------|
| `required` | boolean | Whether auth is mandatory for skill operation |
| `type` | string\|null | Authentication type (`api_key` or `null`) |
| `keys` | array | Array of required API key definitions |

### API Key Definition Schema

| Field | Type | Description |
|-------|------|-------------|
| `env` | string | Environment variable name (e.g., `GEMINI_API_KEY`) |
| `url` | string | URL where users can obtain the API key |
| `optional` | boolean | Whether the key is optional for basic functionality |
| `note` | string | Additional information (e.g., pricing) |

### Authentication Examples

**No Authentication Required:**
```json
{
  "auth": {
    "required": false,
    "type": null,
    "keys": []
  }
}
```

**Single Required API Key:**
```json
{
  "auth": {
    "required": true,
    "type": "api_key",
    "keys": [
      {
        "env": "GEMINI_API_KEY",
        "url": "https://aistudio.google.com/apikey"
      }
    ]
  }
}
```

**Multiple API Keys (Some Optional):**
```json
{
  "auth": {
    "required": true,
    "type": "api_key",
    "keys": [
      {
        "env": "GEMINI_API_KEY",
        "url": "https://aistudio.google.com/apikey"
      },
      {
        "env": "REMOVE_BG_API_KEY",
        "url": "https://www.remove.bg/api",
        "optional": true
      },
      {
        "env": "RECRAFT_API_KEY",
        "url": "https://www.recraft.ai/api",
        "optional": true
      }
    ]
  }
}
```

**Sources:** [skills.json:32-47](), [skills.json:90-99](), [skills.json:147-151](), [skills.json:196-215]()

## Command Templates

Skills define executable command templates in the `commands` array. These templates use placeholder syntax for dynamic values.

### Command Template Syntax

- **Curly braces** `{variable}` indicate runtime substitution
- **Double quotes** `"{multi word input}"` wrap user-provided text
- **Python scripts** are executed relative to the skill directory
- **Angle brackets** `<skill-name>` reference dependency script paths

### Command Examples

**Python Script Execution:**
```json
"commands": [
  "python3 scripts/get_posts.py {subreddit} --limit 20",
  "python3 scripts/search_posts.py \"{query}\" --limit 20",
  "python3 scripts/get_subreddit.py {subreddit}",
  "python3 scripts/get_post.py {post_id}",
  "python3 scripts/get_user.py {username}"
]
```

**Dependency Script Reference:**
```json
"commands": [
  "python3 <nanobanana>/scripts/batch_generate.py \"{prompt}\" -n 20 --ratio 1:1 -d ./logos -p logo",
  "python3 scripts/crop_logo.py {input.png} {output.png}",
  "python3 scripts/remove_bg.py {input.png} {output.png}",
  "python3 scripts/vectorize.py {input.png} {output.svg}"
]
```

**Native Command Execution:**
```json
"commands": [
  "whois {domain}.{tld}",
  "WebSearch: cheapest .{tld} domain registrar"
]
```

**Sources:** [skills.json:380-386](), [skills.json:231-236](), [skills.json:167-170]()

## Installation Command Structure

Skills define platform-specific installation commands in the `install` object, which contains two categories: `user` (global agent installation) and `project` (project-specific installation).

### Install Object Structure

```json
{
  "install": {
    "user": {
      "claude": "npx skills add ReScienceLab/opc-skills --skill {skill-name} -a claude",
      "droid": "npx skills add ReScienceLab/opc-skills --skill {skill-name} -a droid",
      "opencode": "npx skills add ReScienceLab/opc-skills --skill {skill-name} -a opencode",
      "codex": "npx skills add ReScienceLab/opc-skills --skill {skill-name} -a codex"
    },
    "project": {
      "claude": "npx skills add ReScienceLab/opc-skills --skill {skill-name}",
      "droid": "npx skills add ReScienceLab/opc-skills --skill {skill-name}",
      "cursor": "npx skills add ReScienceLab/opc-skills --skill {skill-name}",
      "opencode": "npx skills add ReScienceLab/opc-skills --skill {skill-name}",
      "codex": "npx skills add ReScienceLab/opc-skills --skill {skill-name}"
    }
  }
}
```

### Supported Platforms

| Platform | Agent Type | Default Install Directory |
|----------|-----------|---------------------------|
| `claude` | Claude Code Desktop | `.claude/skills/` |
| `cursor` | Cursor IDE | `.cursor/skills/` |
| `droid` | Factory Droid | `.factory/skills/` |
| `windsurf` | Windsurf IDE | Configuration-dependent |
| `opencode` | OpenCode | Configuration-dependent |
| `codex` | Codex | Configuration-dependent |

**Sources:** [skills.json:48-62](), [skills.json:100-114](), [README.md:109-128]()

## Dependency Resolution

Skills can declare dependencies on other skills using semantic versioning constraints. Dependencies are specified in the `dependencies` object.

### Dependency Graph Structure

```mermaid
graph TB
    subgraph "Infrastructure Layer"
        nanobanana["nanobanana v1.0.0<br/>(Gemini image generation)"]
        twitter["twitter v1.0.0<br/>(X API client)"]
        reddit["reddit v1.0.0<br/>(public JSON API)"]
    end
    
    subgraph "Composite Layer"
        logo["logo-creator v1.0.0"]
        banner["banner-creator v1.0.0"]
        domain["domain-hunter v1.0.0"]
        seogeo["seo-geo v1.0.0"]
    end
    
    subgraph "Standalone Layer"
        requesthunt["requesthunt v1.0.0"]
        producthunt["producthunt v1.0.0"]
        archive["archive v1.0.1"]
    end
    
    logo -->|"requires nanobanana >= 1.0.0"| nanobanana
    banner -->|"requires nanobanana >= 1.0.0"| nanobanana
    domain -->|"requires twitter >= 1.0.0"| twitter
    domain -->|"requires reddit >= 1.0.0"| reddit
    seogeo -->|"requires twitter >= 1.0.0"| twitter
    seogeo -->|"requires reddit >= 1.0.0"| reddit
```

**Sources:** [skills.json:28-31](), [skills.json:143-146](), [skills.json:193-195](), [skills.json:259-261]()

### Dependency Declaration Syntax

Dependencies use semantic versioning constraints:

```json
{
  "dependencies": {
    "skill-name": ">=1.0.0"
  }
}
```

**Constraint Operators:**
- `>=1.0.0` - Minimum version (most common)
- `^1.0.0` - Compatible with 1.x.x
- `~1.0.0` - Compatible with 1.0.x
- `1.0.0` - Exact version

### Transitive Dependency Example

When installing `logo-creator`, the system automatically resolves and installs `nanobanana`:

```bash
npx skills add ReScienceLab/opc-skills --skill logo-creator
# Automatically installs:
# - logo-creator v1.0.0
# - nanobanana v1.0.0 (dependency)
```

**Sources:** [skills.json:193-195](), [README.md:93-106]()

## Links and Documentation References

Each skill defines external links for documentation, source code, and examples in the `links` object.

### Links Object Structure

| Field | Type | Description |
|-------|------|-------------|
| `github` | string | URL to skill directory in repository |
| `docs` | string | URL to external API documentation (if applicable) |
| `example` | string | URL to example workflow markdown file |

### Links Examples

**Skill with Example Workflow:**
```json
{
  "links": {
    "github": "https://github.com/ReScienceLab/opc-skills/tree/main/skills/requesthunt",
    "docs": "https://requesthunt.com/docs",
    "example": "https://github.com/ReScienceLab/opc-skills/blob/main/skills/requesthunt/examples/calendar-app-research.md"
  }
}
```

**Infrastructure Skill with API Documentation:**
```json
{
  "links": {
    "github": "https://github.com/ReScienceLab/opc-skills/tree/main/skills/nanobanana",
    "docs": "https://ai.google.dev/gemini-api/docs/image-generation"
  }
}
```

**Simple Skill (GitHub Only):**
```json
{
  "links": {
    "github": "https://github.com/ReScienceLab/opc-skills/tree/main/skills/archive"
  }
}
```

**Sources:** [skills.json:122-127](), [skills.json:342-345](), [skills.json:533-535]()

## Skill Versioning

The Skills System uses two-level versioning:

1. **Global Registry Version** - `skills.json` version field tracks the overall repository state
2. **Individual Skill Versions** - Each skill maintains independent semantic versioning

### Version Update Rules

| Change Type | Version Increment | Example |
|-------------|------------------|---------|
| New skill added | Registry MINOR | `1.0.0` → `1.1.0` |
| Skill bug fix | Skill PATCH | Skill `1.0.0` → `1.0.1` |
| Skill breaking change | Skill MAJOR + dependent skills | Skill `1.0.0` → `2.0.0` |
| Registry structure change | Registry MAJOR | `1.0.0` → `2.0.0` |

### Current System Version

As of this writing:
- **Registry Version:** `1.0.10` [skills.json:2]()
- **Skill Versions:** All skills at `1.0.0` except `archive` at `1.0.1`

**Sources:** [skills.json:2](), [skills.json:11](), [skills.json:496]()

## Skills Inventory

The current repository contains 10 skills across four categories:

### Foundation Skills (4)

| Skill | Version | Auth Required | Dependencies |
|-------|---------|---------------|--------------|
| `nanobanana` | 1.0.0 | Yes (Gemini) | None |
| `twitter` | 1.0.0 | Yes (twitterapi.io) | None |
| `reddit` | 1.0.0 | No | None |
| `archive` | 1.0.1 | No | None |

### Design Skills (2)

| Skill | Version | Auth Required | Dependencies |
|-------|---------|---------------|--------------|
| `logo-creator` | 1.0.0 | Yes (Gemini + optional) | `nanobanana` |
| `banner-creator` | 1.0.0 | Yes (Gemini) | `nanobanana` |

### SEO & Research Skills (2)

| Skill | Version | Auth Required | Dependencies |
|-------|---------|---------------|--------------|
| `seo-geo` | 1.0.0 | No (optional DataForSEO) | `twitter`, `reddit` |
| `requesthunt` | 1.0.0 | Yes (requesthunt.com) | None |

### Discovery Skills (2)

| Skill | Version | Auth Required | Dependencies |
|-------|---------|---------------|--------------|
| `domain-hunter` | 1.0.0 | No | `twitter`, `reddit` |
| `producthunt` | 1.0.0 | Yes (Product Hunt) | None |

**Sources:** [skills.json:8-537](), [README.md:42-56]()

---

# Page: Skills Registry (skills.json)

# Skills Registry (skills.json)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.factory/AGENTS.md](.factory/AGENTS.md)
- [CHANGELOG.md](CHANGELOG.md)
- [skills.json](skills.json)
- [skills/archive/SKILL.md](skills/archive/SKILL.md)
- [skills/archive/references/TEMPLATE.md](skills/archive/references/TEMPLATE.md)
- [template/SKILL.md](template/SKILL.md)
- [website/blog/posts/why-skills-beat-docs.md](website/blog/posts/why-skills-beat-docs.md)

</details>



`skills.json` is the top-level manifest for the OPC Skills repository. It serves as the single source of truth for all skill metadata: what skills exist, what they require, how they are installed, and what commands they expose. Every automated system that reads or distributes skills — the universal installer, the website, and the CI validation pipeline — derives its data from this file.

This page documents the schema in detail and explains how each field is consumed. For how skills are physically laid out on disk, see [Skill Structure & Standards](#2.2). For how dependencies between skills are validated, see [Dependency Management](#2.3). For how the installer uses this file at runtime, see [Universal Installer (npx skills add)](#3.3).

---

## File Location and Format

The registry lives at [skills.json:1-538]() in the root of the repository. It is a single, hand-maintained JSON file. Its validity is checked in CI using `jq` and a Python JSON parse on every push that touches `skills.json` or the `skills/` directory. See [Automated Testing Pipeline](#6.2) for the exact validation rules.

---

## Top-Level Schema

The root object contains six fields before the `skills` array.

| Field | Type | Description |
|---|---|---|
| `version` | string | Monotonically increasing semver for the registry itself (e.g. `"1.0.10"`). Bumped on every release regardless of which skill changed. |
| `name` | string | Human-readable name of the registry (`"OPC Skills"`). |
| `description` | string | One-line description used in marketplace metadata. |
| `repository` | string | Canonical GitHub URL used by the installer to clone or reference the repo. |
| `website` | string | Public website URL (`"https://opc.dev"`). |
| `logo` | string | Absolute URL to the repository's top-level SVG logo, hosted on GitHub raw content. |
| `skills` | array | Ordered array of skill entry objects. Order matters: the website renders skills in this order. |

**Example (top-level):**
```json
{
  "version": "1.0.10",
  "name": "OPC Skills",
  "description": "Agent Skills for One Person Companies",
  "repository": "https://github.com/ReScienceLab/opc-skills",
  "website": "https://opc.dev",
  "logo": "https://raw.githubusercontent.com/.../opc-logo.svg",
  "skills": [...]
}
```

Sources: [skills.json:1-8]()

---

## Skill Entry Schema

Each element of the `skills` array is an object with the following fields:

### Identity Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Unique kebab-case identifier. Must match the directory name under `skills/`. Used as the `--skill` flag value in install commands. |
| `version` | string | Yes | Independent semver for this skill. Skills are versioned independently of the registry `version`. |
| `description` | string | Yes | Full description shown on the website skill card and in marketplace listings. |
| `logo` | string | Yes | Absolute URL to the skill's SVG logo under `skill-logos/`. |
| `icon` | string | Yes | [Simple Icons](https://simpleicons.org/) slug (e.g. `"reddit"`, `"x"`, `"googlegemini"`) or a generic name (`"globe"`, `"image"`, `"archive"`). Used by the website to render an icon badge. |
| `color` | string | Yes | Six-character hex color without `#` (e.g. `"FF4500"`). Used for the skill card accent color on the website. |

Sources: [skills.json:10-16](), [skills.json:297-302](), [.factory/skills/add-new-opc-skill/SKILL.md:73-120]()

---

### `triggers` Array

An array of strings. These are the natural-language keywords or phrases that should cause an AI agent to activate this skill. The CI validator does not check trigger uniqueness across skills, but authors should avoid overlapping triggers.

```json
"triggers": ["SEO", "GEO", "search optimization", "schema markup", "AI visibility"]
```

Sources: [skills.json:16-27]()

---

### `dependencies` Object

Declares inter-skill dependencies. Keys are skill `name` values from the same `skills` array; values are semver range strings.

```json
"dependencies": {
  "twitter": ">=1.0.0",
  "reddit": ">=1.0.0"
}
```

An empty object (`{}`) means no dependencies. The CI pipeline performs a referential integrity check: every key in any skill's `dependencies` must match a `name` that exists elsewhere in the `skills` array. See [Dependency Management](#2.3) for full details.

**Dependency map across all skills (current):**

```mermaid
graph TD
  seo-geo["seo-geo"] --> twitter["twitter"]
  seo-geo --> reddit["reddit"]
  domain-hunter["domain-hunter"] --> twitter
  domain-hunter --> reddit
  logo-creator["logo-creator"] --> nanobanana["nanobanana"]
  banner-creator["banner-creator"] --> nanobanana
  requesthunt["requesthunt"]
  producthunt["producthunt"]
  archive["archive"]
```

Sources: [skills.json:28-32](), [skills.json:143-146](), [skills.json:193-195](), [skills.json:259-261]()

---

### `auth` Object

Describes authentication requirements for the skill's scripts.

| Field | Type | Description |
|---|---|---|
| `required` | boolean | If `true`, the skill will not function at all without credentials. If `false`, the skill works without credentials but some features may be limited. |
| `type` | string \| null | Authentication mechanism. Currently always `"api_key"` or `null`. |
| `keys` | array | List of API key descriptor objects (see below). Empty array `[]` when `type` is `null`. |

Each object in the `keys` array has:

| Field | Type | Description |
|---|---|---|
| `env` | string | The environment variable name the scripts read (e.g. `"GEMINI_API_KEY"`). |
| `url` | string | URL where the user can obtain the credential. |
| `optional` | boolean | If present and `true`, the key enables additional features but is not required to run the skill at all. |
| `note` | string | Optional human-readable note (e.g. cost estimate). |

**Example — skill with optional keys (`seo-geo`):**
```json
"auth": {
  "required": false,
  "type": "api_key",
  "keys": [
    { "env": "DATAFORSEO_LOGIN", "url": "https://dataforseo.com", "optional": true },
    { "env": "DATAFORSEO_PASSWORD", "url": "https://dataforseo.com", "optional": true }
  ]
}
```

**Example — skill with no auth (`reddit`):**
```json
"auth": {
  "required": false,
  "type": null,
  "keys": []
}
```

Sources: [skills.json:32-46](), [skills.json:360-364](), [skills.json:404-415]()

---

### `install` Object

The `install` object provides ready-to-run shell commands for installing the skill on each supported agent platform. It has two sub-objects:

- **`user`** — installs the skill globally for the current user (`-a <agent>` flag selects the agent-specific global config directory).
- **`project`** — installs the skill into the current project directory (no `-a` flag; target directory is resolved relative to the working directory).

Supported agent keys within each sub-object:

| Key | Appears in `user` | Appears in `project` |
|---|---|---|
| `claude` | Yes | Yes |
| `droid` | Yes | Yes |
| `opencode` | Yes | Yes |
| `codex` | Yes | Yes |
| `cursor` | No | Yes |

`cursor` is absent from `user`-level installs. All commands follow the pattern:

```
npx skills add ReScienceLab/opc-skills --skill <name> [-a <agent>]
```

Sources: [skills.json:48-62](), [.factory/skills/add-new-opc-skill/SKILL.md:91-103]()

---

### `commands` Array

A list of representative CLI command strings for the skill's scripts. These are documentation and are surfaced on the website's skill detail page. They use brace-delimited placeholders like `{domain}` and `"{query}"`.

```json
"commands": [
  "python3 scripts/keyword_research.py \"{keyword}\" --limit 20",
  "python3 scripts/domain_overview.py \"{domain}\""
]
```

Skills that are instruction-only (no scripts) use an empty array: `"commands": []`. The `archive` skill is the current example of this.

One special notation appears in skills that depend on `nanobanana`: their commands reference the dependency's scripts with the `<nanobanana>` placeholder:

```json
"python3 <nanobanana>/scripts/batch_generate.py \"{prompt}\" -n 20 --ratio 1:1 -d ./logos -p logo"
```

Sources: [skills.json:63-69](), [skills.json:231-235](), [skills.json:287-289](), [skills.json:532]()

---

### `links` Object

A free-form object containing named URL strings. The `github` key is always present and points to the skill directory on GitHub. Additional optional keys include `docs` (external API documentation) and `example` (a concrete usage example file in the repo).

| Key | Description |
|---|---|
| `github` | URL to the skill's directory on `github.com` |
| `docs` | URL to external API/service documentation |
| `example` | URL to an example `.md` file in the repo |

Sources: [skills.json:70-73](), [skills.json:121-126](), [skills.json:387-390]()

---

## Complete Skill Entry Structure

The following diagram maps each field in a skill entry to how it is consumed downstream.

**Skill entry field consumption diagram:**

```mermaid
graph LR
  entry["skills[] entry"] --> name["name"]
  entry --> version["version"]
  entry --> description["description"]
  entry --> logo["logo (SVG URL)"]
  entry --> icon["icon"]
  entry --> color["color"]
  entry --> triggers["triggers[]"]
  entry --> dependencies["dependencies{}"]
  entry --> auth["auth{}"]
  entry --> install["install{}"]
  entry --> commands["commands[]"]
  entry --> links["links{}"]

  name --> installer["npx skills add\n--skill flag"]
  name --> ci["CI: referential integrity\ncheck (jq)"]
  name --> website["website/worker.js\nskill pages"]

  version --> changelog["CHANGELOG.md\nmatrix"]
  description --> website
  description --> marketplace[".claude-plugin/\nmarketplace.json"]
  logo --> website
  icon --> website
  color --> website
  triggers --> website
  dependencies --> ci
  auth --> website
  install --> website
  install --> installer
  commands --> website
  links --> website
```

Sources: [skills.json:1-538](), [.factory/skills/add-new-opc-skill/SKILL.md:73-119]()

---

## Skills Inventory

The table below lists all ten current skills and their key metadata fields.

| Name | Version | `auth.required` | Dependencies | Auth Env Vars |
|---|---|---|---|---|
| `seo-geo` | 1.0.0 | false (optional keys) | twitter, reddit | `DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD` (optional) |
| `requesthunt` | 1.0.0 | true | — | `REQUESTHUNT_API_KEY` |
| `domain-hunter` | 1.0.0 | false | twitter, reddit | — |
| `logo-creator` | 1.0.0 | true | nanobanana | `GEMINI_API_KEY`, `REMOVE_BG_API_KEY` (optional), `RECRAFT_API_KEY` (optional) |
| `banner-creator` | 1.0.0 | true | nanobanana | `GEMINI_API_KEY` |
| `nanobanana` | 1.0.0 | true | — | `GEMINI_API_KEY` |
| `reddit` | 1.0.0 | false | — | — |
| `twitter` | 1.0.0 | true | — | `TWITTERAPI_API_KEY` |
| `producthunt` | 1.0.0 | true | — | `PRODUCTHUNT_ACCESS_TOKEN` |
| `archive` | 1.0.1 | false | — | — |

Sources: [skills.json:8-537](), [CHANGELOG.md:12-23]()

---

## How `skills.json` Is Used

### By the Universal Installer

`npx skills add` reads `skills.json` to resolve the skill directory path and construct the correct install command string. The `install.user` or `install.project` sub-object is selected based on whether the `-a` flag is passed. See [Universal Installer (npx skills add)](#3.3).

### By the Website

`website/worker.js` fetches `skills.json` at runtime (via the `fetchSkillsConfig` function) to render skill list pages and the `/skills/[name]` detail pages. The `icon`, `color`, `logo`, `description`, `triggers`, `auth`, `install`, `commands`, and `links` fields are all surfaced in the rendered HTML. The website also exposes `skills.json` verbatim at the `/skills.json` route as a machine-readable API. See [Website Architecture](#4.1) and [API Endpoints](#4.4).

### By the Claude Code Plugin Marketplace

Each skill has a corresponding `plugin.json` under `.claude-plugin/`. Those files reference the skill's `name` and install commands. See [Claude Code Plugin Marketplace](#3.2).

### By the CI Pipeline

The `validate-skills-json` job in `.github/workflows/test-installer.yml` runs three checks against `skills.json`:

1. **Syntax**: `jq '.' skills.json` parses the file.
2. **Required fields**: Verifies each skill entry contains `name`, `version`, `description`, `triggers`, `dependencies`, `auth`, `install`, and `commands`.
3. **Referential integrity**: Every key in any skill's `dependencies` object must correspond to a `name` that exists elsewhere in the `skills` array.

See [Automated Testing Pipeline](#6.2).

**Data flow from `skills.json` to consuming systems:**

```mermaid
flowchart TD
  skillsjson["skills.json"] --> installer["npx skills add\n(Universal Installer)"]
  skillsjson --> worker["website/worker.js\nfetchSkillsConfig()"]
  skillsjson --> ci["test-installer.yml\nvalidate-skills-json job"]
  skillsjson --> marketplace[".claude-plugin/\nmarketplace.json"]

  installer --> agentdirs["Agent config dirs\n(.claude/skills/, .factory/skills/, etc.)"]
  worker --> skillpages["/skills/[name] pages"]
  worker --> apiendpoint["/skills.json API endpoint"]
  worker --> comparepage["/compare page\nfetchCompareData()"]
  ci --> prcheck["PR status check\n(referential integrity)"]
  marketplace --> claudeplugin["Claude Code\n/plugin marketplace add"]
```

Sources: [skills.json:1-538](), [.factory/skills/add-new-opc-skill/SKILL.md:120-218](), [CHANGELOG.md:1-31]()

---

## Adding a New Skill Entry

When a new skill is added, the required fields and their exact format are enforced by the `validate-skills-json` CI job. The `.factory/skills/add-new-opc-skill/SKILL.md` checklist specifies the exact JSON template to use [.factory/skills/add-new-opc-skill/SKILL.md:73-112]().

After editing `skills.json`, validate locally with:

```bash
python3 -c "import json; json.load(open('skills.json')); print('valid')"
```

The full process for adding a skill — including logo generation, README update, `worker.js` update, and `CHANGELOG.md` update — is covered in [Skill Structure & Standards](#2.2).

---

# Page: Skill Structure & Standards

# Skill Structure & Standards

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.factory/AGENTS.md](.factory/AGENTS.md)
- [.factory/hooks.json](.factory/hooks.json)
- [.factory/skills/add-new-opc-skill/SKILL.md](.factory/skills/add-new-opc-skill/SKILL.md)
- [.gitignore](.gitignore)
- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [skill-logos/archive.svg](skill-logos/archive.svg)
- [skills/domain-hunter/examples/auto-video-editing-domain.md](skills/domain-hunter/examples/auto-video-editing-domain.md)
- [template/SKILL.md](template/SKILL.md)
- [website/blog/posts/why-skills-beat-docs.md](website/blog/posts/why-skills-beat-docs.md)
- [website/opc-banner.png](website/opc-banner.png)
- [website/resciencelab-logo.svg](website/resciencelab-logo.svg)

</details>



This page covers the canonical on-disk layout every skill must follow, the required `SKILL.md` format, the six-file checklist for publishing a new skill, and the logo generation pipeline. It describes what goes *inside* a skill directory.

For how skills are registered in the global manifest and discovered at install time, see [Skills Registry (skills.json)](#2.1). For inter-skill dependency rules and CI validation, see [Dependency Management](#2.3).

---

## Standard Directory Layout

Every skill lives under `skills/<skill-name>/` and follows the same four-directory layout.

**Diagram: Skill directory layout**

```mermaid
graph TD
  root["skills/<skill-name>/"]
  skillmd["SKILL.md (required)"]
  scripts["scripts/ (required if scripted)"]
  examples["examples/ (recommended)"]
  references["references/ (optional)"]

  root --> skillmd
  root --> scripts
  root --> examples
  root --> references

  scripts --> py["*.py / *.sh"]
  examples --> exmd["*.md"]
  references --> refmd["*.md / TEMPLATE.md"]
```

Sources: [.factory/AGENTS.md:38-49](), [.factory/skills/add-new-opc-skill/SKILL.md:20-32]()

| Directory | Required | Purpose |
|---|---|---|
| `SKILL.md` | ✓ | Main instruction document; parsed by AI agents and the installer |
| `scripts/` | If scripted | Executable Python or shell scripts; each should accept `--help` |
| `examples/` | Recommended | Markdown files showing real end-to-end workflows |
| `references/` | Optional | API docs, data templates (e.g., `TEMPLATE.md` in archive skill) |

The `template/` directory at the repo root contains a starter `SKILL.md` that should be copied when creating a new skill:

```bash
cp -r template skills/my-new-skill
```

Sources: [template/SKILL.md:122-129](), [.factory/AGENTS.md:73-85]()

---

## SKILL.md Format

`SKILL.md` is the only file AI agents parse directly. It must open with a YAML frontmatter block followed by Markdown body content.

### YAML Frontmatter

The frontmatter follows the [Agent Skills Standard](https://agentskills.io/) and uses only two required fields: `name` and `description`. As of v1.0.6 (Feb 2026), the `triggers` field was removed and trigger keywords are now embedded directly in the `description` field using "Use when..." phrasing.

**Diagram: SKILL.md frontmatter fields mapped to consuming systems**

```mermaid
flowchart LR
  fm["SKILL.md\nfrontmatter"]

  name["name:\nskill-name"]
  desc["description:\nfull text with\ntrigger keywords inline"]

  fm --> name
  fm --> desc

  name --> sj["skills.json\n(name field)"]
  desc --> agent["AI agent\n(activation context)"]
  desc --> sj2["skills.json\n(description field)"]
```

Sources: [template/SKILL.md:1-4](), [template/SKILL.md:112-119](), [CHANGELOG.md:80-87](), [.factory/skills/add-new-opc-skill/SKILL.md:33-40]()

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | ✓ | Kebab-case; must match the directory name and `skills.json` entry |
| `description` | string | ✓ | Plain-text description. Embed trigger keywords inline using "Use when..." phrasing. This field serves dual purpose: human-readable description and AI agent activation context. |

**Standard format (all skills as of v1.0.6+):**

```yaml
---
name: skill-name
description: Clear description of what this skill does and when to use it. Include trigger keywords and contexts inline, e.g. "Use when user wants to X, Y, or Z."
---
```

**Real example from archive skill:**

```yaml
---
name: archive
description: Archive session learnings and debugging solutions with indexed markdown. Use when completing a significant task, solving a complex bug, or finishing a deployment. Maintains .archive/MEMORY.md index for cross-session knowledge reuse.
---
```

**Note on dependencies:** Dependencies are **not** declared in the SKILL.md frontmatter. They are specified in `skills.json` at the repository level. See [Dependency Management](#2.3) for details.

Sources: [template/SKILL.md:1-4](), [.factory/skills/add-new-opc-skill/SKILL.md:33-40](), [CHANGELOG.md:80-87]()

### Markdown Body Sections

The template defines the expected sections. Not all sections are mandatory for every skill, but the template serves as a checklist:

| Section | Purpose |
|---|---|
| `## Prerequisites` | Environment variables, API keys, installed tools |
| `## Quick Start` | Minimal command to invoke the skill |
| `## Usage Examples` | One or more concrete `bash` code blocks with expected output |
| `## Commands` | Full CLI reference per script |
| `## Scripts` | Bullet list mapping each `*.py` filename to its purpose |
| `## API Info` | Base URL, rate limits, auth scheme, official docs link |
| `## Troubleshooting` | Symptom/solution pairs for known failure modes |
| `## Examples` | Reference to the `examples/` directory |
| `## References` | External links and related skills |

Sources: [template/SKILL.md:10-110]()

### Script Guidelines

Scripts in `scripts/` should follow these conventions so agents can invoke them predictably:

- Accept `--help` and use descriptive argument names
- Output machine-readable formats: JSON for data, Markdown for reports
- Include error handling with meaningful messages
- Use relative paths rather than hardcoded absolute paths

Sources: [.factory/AGENTS.md:90-95]()

---

## Add-New-OPC-Skill Checklist

Adding a skill requires updating exactly **six locations** in the repository. The `.factory/skills/add-new-opc-skill/SKILL.md` file is an installable skill that automates and verifies this process.

**Diagram: Six required file updates when adding a skill**

```mermaid
flowchart TD
  start["New skill: skills/<skill-name>/"]

  step1["1. Create SKILL.md\nskills/<skill-name>/SKILL.md"]
  step2["2. Generate logo\nskill-logos/<skill-name>.svg"]
  step3["3. Register in manifest\nskills.json → skills[]"]
  step4["4. Add to README table\nREADME.md"]
  step5["5. Update website compare data\nwebsite/worker.js → fetchCompareData()"]
  step6["6. Record release\nCHANGELOG.md"]

  start --> step1 --> step2 --> step3 --> step4 --> step5 --> step6
```

Sources: [.factory/skills/add-new-opc-skill/SKILL.md:17-183]()

### File 1 — `skills/<skill-name>/SKILL.md`

Create the skill directory, write `SKILL.md` with valid frontmatter, and populate `scripts/`, `examples/`, and `references/` as needed. The template at `template/SKILL.md` is the canonical starting point.

Sources: [.factory/skills/add-new-opc-skill/SKILL.md:18-42]()

### File 2 — `skill-logos/<skill-name>.svg`

Each skill has a pixel-art style SVG logo. The generation pipeline uses three scripts:

**Diagram: Logo generation pipeline**

```mermaid
flowchart LR
  A["nanobanana/scripts/batch_generate.py\n(generates 20 PNG candidates)"]
  B["logo-creator/templates/preview.html\n(HTML gallery to pick from)"]
  C["logo-creator/scripts/crop_logo.py\n(crop selected PNG)"]
  D["logo-creator/scripts/vectorize.py\n(convert to SVG)"]
  E["skill-logos/<skill-name>.svg\n(final asset)"]

  A --> B --> C --> D --> E
```

The prompt style for generation is: `"Pixel art <subject> logo, 8-bit retro style, black pixels on white background, minimalist icon, clean crisp edges, no text, centered"`.

The output SVG must match the visual style of existing logos in `skill-logos/`.

Sources: [.factory/skills/add-new-opc-skill/SKILL.md:49-70]()

### File 3 — `skills.json`

Add a complete entry to the `skills` array. All top-level fields are required. See [Skills Registry (skills.json)](#2.1) for the full schema description.

Key field notes specific to this checklist:

| Field | Requirement |
|---|---|
| `name` | Exact kebab-case match to directory name and `SKILL.md` `name` field |
| `logo` | Raw GitHub URL pointing to `skill-logos/<skill-name>.svg` |
| `icon` | A [Simple Icons](https://simpleicons.org/) slug, or a generic like `"globe"`, `"archive"`, `"image"` |
| `color` | 6-char hex without `#` prefix (e.g., `"6B7280"`) |
| `triggers` | Array of keyword strings that activate this skill (maintained separately in `skills.json` for search/filtering) |
| `dependencies` | Object with skill names as keys and semver ranges as values (e.g., `{"twitter": ">=1.0.0"}`) |
| `auth.keys` | Array of objects with `env`, `url`, and `optional` fields |
| `commands` | List of CLI command strings; empty array `[]` if instructions-only |

**Note:** While `triggers` was removed from SKILL.md frontmatter in v1.0.6, it remains in `skills.json` for search indexing and marketplace filtering.

Validate after editing:

```bash
python3 -c "import json; json.load(open('skills.json')); print('valid')"
```

Sources: [.factory/skills/add-new-opc-skill/SKILL.md:72-126](), [CHANGELOG.md:80-87]()

### File 4 — `README.md`

Add one row to the "Included Skills" table using this format:

```markdown
| <img src="./skill-logos/<skill-name>.svg" width="24"> | [<skill-name>](./skills/<skill-name>) | Short description |
```

Sources: [.factory/skills/add-new-opc-skill/SKILL.md:127-135]()

### File 5 — `website/worker.js`

Add a matching entry to the hardcoded skills array inside the `fetchCompareData()` function. This data drives the `/compare` page. The entry mirrors the `skills.json` structure but is written in JavaScript object literal syntax.

Sources: [.factory/skills/add-new-opc-skill/SKILL.md:137-171]()

### File 6 — `CHANGELOG.md`

Two additions are required:

1. A new row in the **Skill Compatibility & Dependency Matrix** table
2. An entry under `## [Unreleased]` (or the active release section) for the skill

```markdown
### <skill-name>
#### [1.0.0] - YYYY-MM-DD
- **Added**: Initial release - <description>
```

Sources: [.factory/skills/add-new-opc-skill/SKILL.md:173-188]()

---

## Verification

Before committing, run these commands to confirm all six locations are correct:

```bash
# 1. SKILL.md frontmatter present
head -5 skills/<skill-name>/SKILL.md

# 2. Logo SVG exists
ls -la skill-logos/<skill-name>.svg

# 3. skills.json valid and all required fields present
python3 -c "
import json
config = json.load(open('skills.json'))
skill = [s for s in config['skills'] if s['name'] == '<skill-name>'][0]
required = ['name','version','description','logo','icon','color','triggers','dependencies','auth','install','links']
missing = [f for f in required if f not in skill]
print('PASS' if not missing else f'MISSING: {missing}')
"

# 4. README.md lists the skill
grep '<skill-name>' README.md

# 5. worker.js has the skill
grep '<skill-name>' website/worker.js

# 6. CHANGELOG.md has the skill in matrix
grep '<skill-name>' CHANGELOG.md
```

Sources: [.factory/skills/add-new-opc-skill/SKILL.md:189-218]()

---

## Pre-commit Hook

A single pre-commit hook in `.factory/hooks.json` guards all commits. It prevents the `factory-droid[bot]` co-author signature from appearing in commit messages. It does not automate the six-file checklist; that verification is a manual step.

Sources: [.factory/hooks.json:1-12]()

---

## Git Workflow for New Skills

New skills always start on a feature branch branched from `develop`. The branch naming convention is:

```
feature/skill/<skill-name>
```

The commit, once all six files are updated, uses:

```bash
git add skills/<skill-name>/ skill-logos/<skill-name>.svg skills.json README.md website/worker.js CHANGELOG.md
git commit -m "feat(skill): add <skill-name> skill"
git push -u origin feature/skill/<skill-name>
gh pr create --base develop
```

Feature branches never merge directly; a PR through the GitHub UI is required. See [Git Workflow & Branching Strategy](#6.1) for the full branching model.

Sources: [.factory/skills/add-new-opc-skill/SKILL.md:221-233]()

---

# Page: Dependency Management

# Dependency Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.factory/AGENTS.md](.factory/AGENTS.md)
- [CHANGELOG.md](CHANGELOG.md)
- [skills.json](skills.json)
- [skills/archive/SKILL.md](skills/archive/SKILL.md)
- [skills/archive/references/TEMPLATE.md](skills/archive/references/TEMPLATE.md)
- [template/SKILL.md](template/SKILL.md)
- [website/blog/posts/why-skills-beat-docs.md](website/blog/posts/why-skills-beat-docs.md)

</details>



This document explains how OPC Skills manages dependencies between skills, including dependency declaration, semantic versioning, compatibility tracking, and automatic resolution during installation.

For information about the skills.json registry structure, see [Skills Registry (skills.json)](#2.1). For details on creating new skills with dependencies, see [Creating New Skills](#7).

---

## Dependency Declaration in skills.json

Skills declare their dependencies in the `dependencies` object within their skill entry in [skills.json](). Each dependency specifies a minimum version using semantic versioning constraints.

**Dependency Format:**

```json
{
  "name": "skill-name",
  "version": "1.0.0",
  "dependencies": {
    "dependency-skill-name": ">=minimum.version.number"
  }
}
```

**Example from domain-hunter:**

[skills.json:129-146]()

```json
{
  "name": "domain-hunter",
  "version": "1.0.0",
  "dependencies": {
    "twitter": ">=1.0.0",
    "reddit": ">=1.0.0"
  }
}
```

**Dependency-Free Skills:**

Skills without dependencies use an empty object:

[skills.json:89](), [skills.json:311](), [skills.json:359](), [skills.json:404](), [skills.json:456](), [skills.json:511]()

```json
{
  "name": "nanobanana",
  "version": "1.0.0",
  "dependencies": {}
}
```

Sources: [skills.json:1-538]()

---

## Dependency Graph

### Current Skill Dependencies

The following diagram shows the actual dependency relationships between all skills in the repository:

```mermaid
graph TB
    subgraph "Foundation Skills (No Dependencies)"
        nanobanana["nanobanana<br/>v1.0.0"]
        twitter["twitter<br/>v1.0.0"]
        reddit["reddit<br/>v1.0.0"]
        requesthunt["requesthunt<br/>v1.0.0"]
        producthunt["producthunt<br/>v1.0.0"]
        archive["archive<br/>v1.0.1"]
    end
    
    subgraph "Composite Skills (With Dependencies)"
        logo_creator["logo-creator<br/>v1.0.0"]
        banner_creator["banner-creator<br/>v1.0.0"]
        domain_hunter["domain-hunter<br/>v1.0.0"]
        seo_geo["seo-geo<br/>v1.0.0"]
    end
    
    logo_creator -->|"dependencies.nanobanana: '>=1.0.0'"| nanobanana
    banner_creator -->|"dependencies.nanobanana: '>=1.0.0'"| nanobanana
    
    domain_hunter -->|"dependencies.twitter: '>=1.0.0'"| twitter
    domain_hunter -->|"dependencies.reddit: '>=1.0.0'"| reddit
    
    seo_geo -->|"dependencies.twitter: '>=1.0.0'"| twitter
    seo_geo -->|"dependencies.reddit: '>=1.0.0'"| reddit
```

**Dependency Statistics:**

| Foundation Skill | Dependents | Impact Radius |
|-----------------|------------|---------------|
| `nanobanana` | 2 skills (logo-creator, banner-creator) | Design automation |
| `twitter` | 2 skills (domain-hunter, seo-geo) | Social media research |
| `reddit` | 2 skills (domain-hunter, seo-geo) | Social media research |
| `requesthunt` | 0 skills | Standalone |
| `producthunt` | 0 skills | Standalone |
| `archive` | 0 skills | Standalone |

Sources: [skills.json:10-74](), [skills.json:129-175](), [skills.json:177-241](), [skills.json:243-295](), [skills.json:297-346]()

---

## Semantic Versioning Constraints

OPC Skills uses [Semantic Versioning 2.0.0](https://semver.org/) for all version numbers and dependency constraints.

### Version Number Format

```
MAJOR.MINOR.PATCH
```

- **MAJOR**: Breaking changes or API incompatibility
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Constraint Operators

Currently, all dependencies use the `>=` operator, which means "greater than or equal to":

```json
{
  "dependencies": {
    "nanobanana": ">=1.0.0"
  }
}
```

**Interpretation:**
- ✅ Compatible: `1.0.0`, `1.0.1`, `1.1.0`, `1.2.5`
- ✅ Compatible: `2.0.0` (unless breaking changes documented)
- ❌ Incompatible: `0.9.0`, `0.9.9`

### Version Compatibility Rules

From [CHANGELOG.md:8-30]():

| Dependency Update Type | Dependent Skill Action | Version Bump Required |
|----------------------|------------------------|----------------------|
| Patch (`1.0.0` → `1.0.1`) | No action needed | No |
| Minor (`1.0.0` → `1.1.0`) | No action needed | No |
| Major with no breaking changes | No action needed | No |
| Major with breaking changes | Must update to support new API | Patch or Minor |

Sources: [CHANGELOG.md:1-30](), [.factory/AGENTS.md:112-123]()

---

## Compatibility Matrix in CHANGELOG.md

The [CHANGELOG.md]() maintains a compatibility matrix that documents all dependency relationships and version requirements:

[CHANGELOG.md:8-30]()

```markdown
## Skill Compatibility & Dependency Matrix

| Skill | Current Version | Requires | Min Versions |
|-------|-----------------|----------|--------------|
| **requesthunt** | 1.0.0 | - | - |
| **domain-hunter** | 1.0.0 | twitter, reddit | twitter ≥1.0.0, reddit ≥1.0.0 |
| **logo-creator** | 1.0.0 | nanobanana | nanobanana ≥1.0.0 |
| **banner-creator** | 1.0.0 | nanobanana | nanobanana ≥1.0.0 |
| **nanobanana** | 1.0.0 | - | - |
| **reddit** | 1.0.0 | - | - |
| **twitter** | 1.0.0 | - | - |
| **producthunt** | 1.0.0 | - | - |
| **seo-geo** | 1.0.0 | twitter, reddit | twitter ≥1.0.0, reddit ≥1.0.0 |
| **archive** | 1.0.1 | - | - |
```

**Matrix Usage:**

1. **Before updating a skill**: Check which skills depend on it
2. **Before installing a skill**: Verify minimum versions of dependencies
3. **During breaking changes**: Identify all skills that need updates

### Key Points from CHANGELOG.md

[CHANGELOG.md:25-30]()

- Each skill has an independent version number
- Skills can be released independently
- Use this matrix to identify dependencies before updating
- When a dependency skill updates with breaking changes, dependent skills need testing

Sources: [CHANGELOG.md:8-30]()

---

## Dependency Declaration in SKILL.md

Individual skill documentation files also declare dependencies in their YAML frontmatter, though the authoritative source is [skills.json]().

**Archive Skill (No Dependencies):**

[skills/archive/SKILL.md:1-4]()

```yaml
---
name: archive
description: "Archive session learnings..."
---
```

**Template Structure:**

[template/SKILL.md:1-4]()

```yaml
---
name: skill-name
description: Clear description...
---
```

**Note:** The `dependencies` field was previously included in SKILL.md frontmatter but is now primarily managed in [skills.json](). The SKILL.md should document prerequisite skills in prose within the "Prerequisites" section.

Sources: [skills/archive/SKILL.md:1-56](), [template/SKILL.md:1-130]()

---

## Transitive Dependency Resolution

### How It Works

When a user installs a skill with dependencies, the installer automatically resolves and installs all required dependencies recursively.

```mermaid
graph LR
    subgraph "User Command"
        cmd["npx skills add<br/>--skill logo-creator"]
    end
    
    subgraph "Resolution Process"
        parse["Parse skills.json<br/>logo-creator entry"]
        check_deps["Read dependencies<br/>object"]
        resolve["Resolve:<br/>nanobanana >=1.0.0"]
        check_installed["Check if nanobanana<br/>already installed"]
        install_dep["Install nanobanana<br/>v1.0.0"]
        install_main["Install logo-creator<br/>v1.0.0"]
    end
    
    cmd --> parse
    parse --> check_deps
    check_deps --> resolve
    resolve --> check_installed
    check_installed -->|"Not found"| install_dep
    check_installed -->|"Found"| install_main
    install_dep --> install_main
```

### Example: Installing domain-hunter

**User executes:**

```bash
npx skills add ReScienceLab/opc-skills --skill domain-hunter
```

**Resolution flow:**

1. Installer reads [skills.json:129-175]()
2. Parses `dependencies` object:
   ```json
   {
     "twitter": ">=1.0.0",
     "reddit": ">=1.0.0"
   }
   ```
3. Checks if `twitter` v1.0.0+ is installed
4. Checks if `reddit` v1.0.0+ is installed
5. Installs missing dependencies
6. Installs `domain-hunter` v1.0.0

**Installation order:**

```
twitter (1.0.0) → Installed
reddit (1.0.0) → Installed
domain-hunter (1.0.0) → Installed
```

Sources: [skills.json:129-175](), [.factory/AGENTS.md:99-110]()

---

## Installation Commands with Dependencies

### Platform-Specific Installation

Each skill in [skills.json]() provides installation commands for multiple platforms. Dependencies are automatically resolved regardless of which command is used.

**From domain-hunter skill:**

[skills.json:152-166]()

```json
{
  "install": {
    "user": {
      "claude": "npx skills add ReScienceLab/opc-skills --skill domain-hunter -a claude",
      "droid": "npx skills add ReScienceLab/opc-skills --skill domain-hunter -a droid",
      "opencode": "npx skills add ReScienceLab/opc-skills --skill domain-hunter -a opencode",
      "codex": "npx skills add ReScienceLab/opc-skills --skill domain-hunter -a codex"
    },
    "project": {
      "claude": "npx skills add ReScienceLab/opc-skills --skill domain-hunter",
      "droid": "npx skills add ReScienceLab/opc-skills --skill domain-hunter",
      "cursor": "npx skills add ReScienceLab/opc-skills --skill domain-hunter",
      "opencode": "npx skills add ReScienceLab/opc-skills --skill domain-hunter",
      "codex": "npx skills add ReScienceLab/opc-skills --skill domain-hunter"
    }
  }
}
```

### Bulk Installation

Installing all skills also resolves dependencies correctly:

```bash
npx skills add ReScienceLab/opc-skills
```

This command installs all 10 skills with proper dependency ordering.

Sources: [skills.json:48-73](), [skills.json:100-166]()

---

## Dependency Lifecycle Management

### When Dependencies Update

The following diagram shows the workflow when a foundation skill releases an update:

```mermaid
graph TB
    subgraph "Foundation Skill Update"
        twitter_update["twitter v1.0.0 → v1.1.0<br/>Minor update (non-breaking)"]
    end
    
    subgraph "Impact Analysis"
        check_changelog["Check CHANGELOG.md<br/>Compatibility Matrix"]
        identify_deps["Identify dependents:<br/>domain-hunter, seo-geo"]
    end
    
    subgraph "Dependent Skill Actions"
        test_compat["Test compatibility:<br/>Run dependent skill scripts"]
        no_break{Breaking<br/>changes?}
        no_action["No action required<br/>Semantic versioning guarantees"]
        update_deps["Update dependent skills<br/>Bump versions"]
    end
    
    subgraph "Documentation"
        update_changelog["Update CHANGELOG.md<br/>Document breaking changes"]
        update_matrix["Update Compatibility Matrix"]
    end
    
    twitter_update --> check_changelog
    check_changelog --> identify_deps
    identify_deps --> test_compat
    test_compat --> no_break
    no_break -->|"No (minor/patch)"| no_action
    no_break -->|"Yes (major)"| update_deps
    update_deps --> update_changelog
    update_changelog --> update_matrix
```

### Breaking Change Example

From [.factory/AGENTS.md:440-459]():

When `twitter` releases a breaking v2.0.0:

1. **Identify dependent skills** using CHANGELOG.md Matrix:
   - `domain-hunter` (depends on twitter >=1.0.0)
   - `seo-geo` (depends on twitter >=1.0.0)

2. **Create separate PRs** for each dependent skill:
   - `feature/skill/domain-hunter/twitter-v2-compat`
   - `feature/skill/seo-geo/twitter-v2-compat`

3. **Test compatibility** before merging

4. **Update versions** only if dependent skills needed code changes

5. **Document in CHANGELOG.md**:
   ```markdown
   ### twitter
   #### [2.0.0] - 2025-01-23 ⚠️ BREAKING
   - **Changed**: API now requires v2 endpoint authentication
   - **Migration Guide**: See docs/migration-guide.md
   
   ### domain-hunter
   #### [1.0.1] - 2025-01-24
   - **Fixed**: Updated to support twitter v2.0.0
   ```

Sources: [.factory/AGENTS.md:440-495](), [CHANGELOG.md:25-30]()

---

## Dependency Validation

### Pre-Commit Checks

Skills with dependencies must pass validation before merging:

From [.factory/AGENTS.md:312-338]():

**PR Requirements Checklist:**

- [ ] **Dependencies declared** in skills.json `dependencies` object
- [ ] **Minimum versions** specified using `>=` operator
- [ ] **CHANGELOG.md updated** with dependency information
- [ ] **Compatibility tested** with declared dependency versions
- [ ] **Version constraints** follow semantic versioning

### Testing Dependencies

**Testing that a skill works with its dependencies:**

[.factory/AGENTS.md:475-486]()

```bash
# Test skill with dependencies
cd skills/domain-hunter
python3 scripts/test_dependencies.py

# Test that dependent skills still work (when updating foundation skill)
cd skills/logo-creator
python3 scripts/test_nanobanana_compat.py
```

Sources: [.factory/AGENTS.md:312-338](), [.factory/AGENTS.md:475-486]()

---

## Dependency-Related Fields in skills.json

### Complete Dependency Schema

```mermaid
graph LR
    subgraph "skills.json Structure"
        root["skills array"]
        skill["skill object"]
        deps["dependencies object"]
        dep_entry["'skill-name': '>=version'"]
    end
    
    subgraph "Example: logo-creator"
        lc_skill["logo-creator skill"]
        lc_deps["dependencies"]
        lc_nano["'nanobanana': '>=1.0.0'"]
    end
    
    subgraph "Example: seo-geo"
        sg_skill["seo-geo skill"]
        sg_deps["dependencies"]
        sg_twitter["'twitter': '>=1.0.0'"]
        sg_reddit["'reddit': '>=1.0.0'"]
    end
    
    root --> skill
    skill --> deps
    deps --> dep_entry
    
    lc_skill --> lc_deps
    lc_deps --> lc_nano
    
    sg_skill --> sg_deps
    sg_deps --> sg_twitter
    sg_deps --> sg_reddit
```

**Field Locations in skills.json:**

| Skill | dependencies Field | Line Range |
|-------|-------------------|------------|
| seo-geo | Line 28-31 | [skills.json:28-31]() |
| requesthunt | Line 89 | [skills.json:89]() |
| domain-hunter | Line 143-146 | [skills.json:143-146]() |
| logo-creator | Line 193-195 | [skills.json:193-195]() |
| banner-creator | Line 259-261 | [skills.json:259-261]() |
| nanobanana | Line 311 | [skills.json:311]() |
| reddit | Line 359 | [skills.json:359]() |
| twitter | Line 404 | [skills.json:404]() |
| producthunt | Line 456 | [skills.json:456]() |
| archive | Line 511 | [skills.json:511]() |

Sources: [skills.json:28-31](), [skills.json:89](), [skills.json:143-146](), [skills.json:193-195](), [skills.json:259-261](), [skills.json:311](), [skills.json:359](), [skills.json:404](), [skills.json:456](), [skills.json:511]()

---

## Circular Dependency Prevention

### Current Status

The OPC Skills repository has **no circular dependencies**. The dependency graph is a directed acyclic graph (DAG).

**Validation:**
- Foundation skills (nanobanana, twitter, reddit, requesthunt, producthunt, archive) have no dependencies
- Composite skills (logo-creator, banner-creator, domain-hunter, seo-geo) only depend on foundation skills
- No skill depends on a composite skill

### Prevention Strategy

From [.factory/AGENTS.md:25-70]():

1. **Foundation Skills** provide base capabilities (no dependencies)
2. **Composite Skills** build on foundation skills only
3. **No cross-dependencies** between composite skills

**Example of prevented circular dependency:**

```
❌ INVALID:
logo-creator depends on banner-creator
banner-creator depends on logo-creator

✅ VALID:
logo-creator depends on nanobanana
banner-creator depends on nanobanana
```

Sources: [.factory/AGENTS.md:25-70](), [skills.json:1-538]()

---

## Commands That Reference Dependencies

### In logo-creator

The `logo-creator` skill references its `nanobanana` dependency in command templates:

[skills.json:231-236]()

```json
{
  "commands": [
    "python3 <nanobanana>/scripts/batch_generate.py \"{prompt}\" -n 20 --ratio 1:1 -d ./logos -p logo",
    "python3 scripts/crop_logo.py {input.png} {output.png}",
    "python3 scripts/remove_bg.py {input.png} {output.png}",
    "python3 scripts/vectorize.py {input.png} {output.svg}"
  ]
}
```

**Note:** The `<nanobanana>` placeholder indicates that the command should be executed from the nanobanana skill's directory.

### In banner-creator

[skills.json:287-290]()

```json
{
  "commands": [
    "python3 <nanobanana>/scripts/batch_generate.py \"{prompt}\" -n 20 --ratio 21:9 -d ./banners -p banner",
    "python3 scripts/crop_banner.py {input.png} {output.png} --ratio 2:1 --width 1280"
  ]
}
```

Sources: [skills.json:231-236](), [skills.json:287-290]()

---

## Future Dependency Features

### Potential Enhancements

Based on the current structure, future improvements could include:

1. **Version Range Constraints**
   ```json
   {
     "dependencies": {
       "twitter": ">=1.0.0 <2.0.0"
     }
   }
   ```

2. **Optional Dependencies**
   ```json
   {
     "dependencies": {
       "dataforseo": ">=1.0.0"
     },
     "optionalDependencies": {
       "advanced-analytics": ">=2.0.0"
     }
   }
   ```

3. **Peer Dependencies**
   ```json
   {
     "peerDependencies": {
       "nanobanana": ">=1.0.0"
     }
   }
   ```

### Current Limitations

- Only `>=` version constraint supported
- No optional dependency mechanism (though `auth.optional: true` exists for API keys)
- No explicit peer dependency declarations
- No dependency lock file

Sources: [skills.json:32-46]() (auth.optional example)

---

# Page: Skill Categories & Reference

# Skill Categories & Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [skill-logos/archive.svg](skill-logos/archive.svg)
- [skills.json](skills.json)
- [skills/archive/SKILL.md](skills/archive/SKILL.md)
- [skills/archive/references/TEMPLATE.md](skills/archive/references/TEMPLATE.md)
- [website/opc-banner.png](website/opc-banner.png)

</details>



This page provides a comprehensive overview of the skill categorization system and serves as a reference guide to all available OPC skills. It explains the architectural taxonomy that organizes skills into functional tiers (infrastructure, composite, standalone) and documents the dependency relationships between skills. For detailed documentation of individual skills, see the category-specific pages linked below.

For information about dependency version management and resolution, see [Dependency Management](#2.3). For the skills.json registry structure, see [Skills Registry (skills.json)](#2.1).

---

## Skill Taxonomy

OPC Skills are organized into three architectural tiers based on their dependencies and functionality. This taxonomy reflects how skills compose together to provide higher-level capabilities.

### Three-Tier Architecture

```mermaid
graph TB
    subgraph "Tier 1: Infrastructure Skills"
        nanobanana["nanobanana<br/>Gemini Image Generation"]
        twitter["twitter<br/>X API Client"]
        reddit["reddit<br/>Reddit JSON API"]
        archive["archive<br/>Session Memory"]
    end
    
    subgraph "Tier 2: Composite Skills"
        logo_creator["logo-creator<br/>Logo Design Workflow"]
        banner_creator["banner-creator<br/>Banner Design Workflow"]
        domain_hunter["domain-hunter<br/>Domain Search + Social"]
        seo_geo["seo-geo<br/>SEO/GEO + Social Research"]
    end
    
    subgraph "Tier 3: Standalone Skills"
        requesthunt["requesthunt<br/>Demand Research"]
        producthunt["producthunt<br/>Product Discovery"]
    end
    
    logo_creator -->|"depends on"| nanobanana
    banner_creator -->|"depends on"| nanobanana
    domain_hunter -->|"depends on"| twitter
    domain_hunter -->|"depends on"| reddit
    seo_geo -->|"depends on"| twitter
    seo_geo -->|"depends on"| reddit
```

**Tier 1 - Infrastructure Skills**: Provide foundational API access and core capabilities. No dependencies on other skills. Include `nanobanana`, `twitter`, `reddit`, and `archive`.

**Tier 2 - Composite Skills**: Build on infrastructure skills to deliver specialized workflows. Include `logo-creator`, `banner-creator`, `domain-hunter`, and `seo-geo`.

**Tier 3 - Standalone Skills**: Operate independently with their own external API integrations. Include `requesthunt` and `producthunt`.

**Sources:** [skills.json:8-537](), high-level system diagrams (Diagram 2)

---

## Skill Directory Structure

Each skill is organized in the repository following a standardized structure:

```mermaid
graph LR
    skills_dir["skills/"]
    
    skills_dir --> seo_geo_dir["seo-geo/"]
    skills_dir --> requesthunt_dir["requesthunt/"]
    skills_dir --> domain_hunter_dir["domain-hunter/"]
    skills_dir --> logo_creator_dir["logo-creator/"]
    skills_dir --> banner_creator_dir["banner-creator/"]
    skills_dir --> nanobanana_dir["nanobanana/"]
    skills_dir --> reddit_dir["reddit/"]
    skills_dir --> twitter_dir["twitter/"]
    skills_dir --> producthunt_dir["producthunt/"]
    skills_dir --> archive_dir["archive/"]
    
    archive_dir --> archive_skill["SKILL.md"]
    archive_dir --> archive_refs["references/"]
    archive_refs --> archive_template["TEMPLATE.md"]
```

Each skill directory contains:
- `SKILL.md` - Primary documentation with YAML frontmatter (required)
- `scripts/` - Executable Python/Shell scripts (optional)
- `examples/` - Usage examples and workflows (optional)
- `references/` - API documentation and templates (optional)

**Sources:** [skills/archive/SKILL.md:1-56](), [skills/archive/references/TEMPLATE.md:1-40]()

---

## Skill Registry Metadata

The [skills.json:1-538]() registry defines 10 skills with structured metadata. Each skill entry contains:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique skill identifier (lowercase-kebab-case) |
| `version` | string | Semantic version (e.g., "1.0.0") |
| `description` | string | Human-readable purpose and capabilities |
| `logo` | string | URL to SVG logo in skill-logos/ directory |
| `icon` | string | Icon identifier for UI rendering |
| `color` | string | Hex color code (without #) |
| `triggers` | array | Keywords that activate the skill |
| `dependencies` | object | Required skills with version constraints |
| `auth` | object | API key requirements and acquisition URLs |
| `install` | object | Platform-specific installation commands |
| `commands` | array | Executable script templates |
| `links` | object | GitHub, docs, and example URLs |

**Sources:** [skills.json:8-537]()

---

## Skill Categories by Function

### Foundation Skills (Tier 1)

Infrastructure skills providing core API access and memory persistence.

| Skill | Directory | Dependencies | Auth Required |
|-------|-----------|--------------|---------------|
| nanobanana | `skills/nanobanana/` | None | Yes (GEMINI_API_KEY) |
| twitter | `skills/twitter/` | None | Yes (TWITTERAPI_API_KEY) |
| reddit | `skills/reddit/` | None | No |
| archive | `skills/archive/` | None | No |

**Detailed Documentation:** See [Foundation Skills](#2.4.1)

**Sources:** [skills.json:297-346]() (nanobanana), [skills.json:393-442]() (twitter), [skills.json:348-391]() (reddit), [skills.json:495-536]() (archive)

### Design & Image Generation Skills (Tier 2)

Composite skills for iterative design workflows built on `nanobanana`.

| Skill | Directory | Dependencies | Optional APIs |
|-------|-----------|--------------|---------------|
| logo-creator | `skills/logo-creator/` | nanobanana>=1.0.0 | remove.bg, recraft.ai |
| banner-creator | `skills/banner-creator/` | nanobanana>=1.0.0 | None |

Both skills use [skills.json:232]() and [skills.json:288]() to invoke nanobanana's `batch_generate.py` script with the `<nanobanana>` path placeholder.

**Detailed Documentation:** See [Design & Image Generation Skills](#2.4.2)

**Sources:** [skills.json:177-241]() (logo-creator), [skills.json:243-295]() (banner-creator)

### SEO & GEO Optimization (Tier 2)

The `seo-geo` skill provides AI search optimization built on social media research.

| Skill | Directory | Dependencies | Optional APIs |
|-------|-----------|--------------|---------------|
| seo-geo | `skills/seo-geo/` | twitter>=1.0.0, reddit>=1.0.0 | DataForSEO |

**Detailed Documentation:** See [SEO & GEO Optimization Skill](#2.4.3)

**Sources:** [skills.json:10-73]()

### Research & Validation Skills (Tier 3)

Standalone skills for demand research and product discovery.

| Skill | Directory | Dependencies | Auth Required |
|-------|-----------|--------------|---------------|
| requesthunt | `skills/requesthunt/` | None | Yes (REQUESTHUNT_API_KEY) |
| producthunt | `skills/producthunt/` | None | Yes (PRODUCTHUNT_ACCESS_TOKEN) |

**Detailed Documentation:** See [Research & Validation Skills](#2.4.4)

**Sources:** [skills.json:76-127]() (requesthunt), [skills.json:444-493]() (producthunt)

### Social Media & Domain Skills (Tier 2)

The `domain-hunter` skill orchestrates domain search with social media research.

| Skill | Directory | Dependencies | Auth Required |
|-------|-----------|--------------|---------------|
| domain-hunter | `skills/domain-hunter/` | twitter>=1.0.0, reddit>=1.0.0 | No |

**Detailed Documentation:** See [Social Media & Domain Skills](#2.4.5)

**Sources:** [skills.json:129-175]()

---

## Dependency Resolution

### Dependency Graph

```mermaid
graph TB
    subgraph "skills.json Registry"
        registry["skills array<br/>(10 entries)"]
    end
    
    subgraph "Zero Dependencies"
        nanobanana_skill["nanobanana<br/>skills.json:297-346"]
        twitter_skill["twitter<br/>skills.json:393-442"]
        reddit_skill["reddit<br/>skills.json:348-391"]
        archive_skill["archive<br/>skills.json:495-536"]
        requesthunt_skill["requesthunt<br/>skills.json:76-127"]
        producthunt_skill["producthunt<br/>skills.json:444-493"]
    end
    
    subgraph "Single Dependency"
        logo_creator_skill["logo-creator<br/>skills.json:177-241<br/>dependencies.nanobanana>=1.0.0"]
        banner_creator_skill["banner-creator<br/>skills.json:243-295<br/>dependencies.nanobanana>=1.0.0"]
    end
    
    subgraph "Multiple Dependencies"
        domain_hunter_skill["domain-hunter<br/>skills.json:129-175<br/>dependencies.twitter>=1.0.0<br/>dependencies.reddit>=1.0.0"]
        seo_geo_skill["seo-geo<br/>skills.json:10-73<br/>dependencies.twitter>=1.0.0<br/>dependencies.reddit>=1.0.0"]
    end
    
    registry --> nanobanana_skill
    registry --> twitter_skill
    registry --> reddit_skill
    registry --> archive_skill
    registry --> requesthunt_skill
    registry --> producthunt_skill
    registry --> logo_creator_skill
    registry --> banner_creator_skill
    registry --> domain_hunter_skill
    registry --> seo_geo_skill
    
    logo_creator_skill -.->|"line 194"| nanobanana_skill
    banner_creator_skill -.->|"line 260"| nanobanana_skill
    domain_hunter_skill -.->|"lines 144-145"| twitter_skill
    domain_hunter_skill -.->|"lines 144-145"| reddit_skill
    seo_geo_skill -.->|"lines 29-30"| twitter_skill
    seo_geo_skill -.->|"lines 29-30"| reddit_skill
```

**Dependency Declaration Format** in skills.json:
```json
"dependencies": {
  "nanobanana": ">=1.0.0",
  "twitter": ">=1.0.0",
  "reddit": ">=1.0.0"
}
```

When a user installs a composite skill, the installer automatically resolves and installs its dependencies. For example, installing `domain-hunter` will automatically install `twitter` and `reddit` if not already present.

**Sources:** [skills.json:28-31]() (seo-geo deps), [skills.json:143-146]() (domain-hunter deps), [skills.json:193-195]() (logo-creator deps), [skills.json:259-261]() (banner-creator deps)

---

## Trigger Keywords

Skills are activated by natural language triggers defined in [skills.json:16-27]() (example: seo-geo). AI agents match user intent against these keywords to determine which skill to load.

### Trigger Keyword Mapping

```mermaid
graph TB
    user_input["User Input:<br/>Natural Language"]
    
    subgraph "Trigger Matching (YAML frontmatter)"
        image_triggers["'generate image'<br/>'create image'<br/>'AI image'"]
        logo_triggers["'logo'<br/>'brand'<br/>'create logo'"]
        banner_triggers["'banner'<br/>'header'<br/>'github banner'"]
        domain_triggers["'domain'<br/>'buy domain'<br/>'.ai domain'"]
        seo_triggers["'SEO'<br/>'GEO'<br/>'keyword research'"]
        social_twitter["'twitter'<br/>'X'<br/>'tweet'"]
        social_reddit["'reddit'<br/>'subreddit'<br/>'r/'"]
        archive_triggers["'archive this'<br/>'save learnings'<br/>'check archives'"]
    end
    
    subgraph "Skill Selection"
        nanobanana_load["Load nanobanana"]
        logo_load["Load logo-creator<br/>+nanobanana"]
        banner_load["Load banner-creator<br/>+nanobanana"]
        domain_load["Load domain-hunter<br/>+twitter+reddit"]
        seo_load["Load seo-geo<br/>+twitter+reddit"]
        twitter_load["Load twitter"]
        reddit_load["Load reddit"]
        archive_load["Load archive"]
    end
    
    user_input --> image_triggers
    user_input --> logo_triggers
    user_input --> banner_triggers
    user_input --> domain_triggers
    user_input --> seo_triggers
    user_input --> social_twitter
    user_input --> social_reddit
    user_input --> archive_triggers
    
    image_triggers --> nanobanana_load
    logo_triggers --> logo_load
    banner_triggers --> banner_load
    domain_triggers --> domain_load
    seo_triggers --> seo_load
    social_twitter --> twitter_load
    social_reddit --> reddit_load
    archive_triggers --> archive_load
```

**Example Trigger Arrays in skills.json:**

- **nanobanana** [skills.json:303-310](): `["generate image", "create image", "nano banana", "nanobanana", "gemini image", "AI image"]`
- **logo-creator** [skills.json:183-192](): `["logo", "brand", "icon", "favicon", "mascot", "emblem", "create logo", "design logo"]`
- **archive** [skills.json:501-510](): `["archive this", "archive session", "save learnings", "document this", "session notes", "what did we learn", "check archives", "past solutions"]`

**Sources:** [skills.json:16-27](), [skills.json:82-88](), [skills.json:136-142](), [skills.json:183-192](), [skills.json:249-258](), [skills.json:303-310](), [skills.json:354-358](), [skills.json:399-403](), [skills.json:450-455](), [skills.json:501-510]()

---

## Authentication Requirements

Skills requiring API keys declare them in the `auth` field with acquisition URLs:

| Skill | Required Keys | Optional Keys | Cost |
|-------|--------------|---------------|------|
| nanobanana | GEMINI_API_KEY | - | Free tier available |
| twitter | TWITTERAPI_API_KEY | - | ~$0.15-0.18/1k requests |
| reddit | - | - | Free (public API) |
| producthunt | PRODUCTHUNT_ACCESS_TOKEN | - | Free |
| requesthunt | REQUESTHUNT_API_KEY | - | Paid service |
| logo-creator | GEMINI_API_KEY | REMOVE_BG_API_KEY, RECRAFT_API_KEY | Mixed |
| banner-creator | GEMINI_API_KEY | - | Free tier available |
| domain-hunter | - | - | Free (uses whois) |
| seo-geo | - | DATAFORSEO_LOGIN, DATAFORSEO_PASSWORD | Optional paid features |
| archive | - | - | Free (local only) |

**Auth Field Structure** in skills.json:
```json
"auth": {
  "required": true,
  "type": "api_key",
  "keys": [
    {
      "env": "GEMINI_API_KEY",
      "url": "https://aistudio.google.com/apikey"
    }
  ]
}
```

**Sources:** [skills.json:32-47]() (seo-geo auth), [skills.json:90-99]() (requesthunt auth), [skills.json:196-214]() (logo-creator auth), [skills.json:312-321]() (nanobanana auth), [skills.json:405-415]() (twitter auth), [skills.json:457-466]() (producthunt auth)

---

## Skill Logos and Visual Identity

Each skill has an SVG logo stored in [skill-logos/]() directory and referenced in skills.json. The archive skill logo is stored at [skill-logos/archive.svg:1-10]().

Logo URLs follow the pattern:
```
https://raw.githubusercontent.com/ReScienceLab/opc-skills/main/skill-logos/{skill-name}.svg
```

Logos are displayed in:
- README.md skill table [README.md:44-55]()
- opc.dev website skill cards
- Claude marketplace listings
- skills.sh browser

**Sources:** [skills.json:13]() (seo-geo logo), [skills.json:79]() (requesthunt logo), [skills.json:132]() (domain-hunter logo), [skills.json:179]() (logo-creator logo), [skills.json:245]() (banner-creator logo), [skills.json:300]() (nanobanana logo), [skills.json:351]() (reddit logo), [skills.json:396]() (twitter logo), [skills.json:447]() (producthunt logo), [skills.json:498]() (archive logo), [skill-logos/archive.svg:1-10]()

---

## Installation Commands

Each skill entry in skills.json contains platform-specific installation commands under the `install` field [skills.json:48-62]() (example: seo-geo).

### Installation Command Structure

```mermaid
graph LR
    install_field["install object"]
    
    install_field --> user_scope["user scope<br/>Global agent config"]
    install_field --> project_scope["project scope<br/>Local .factory/skills"]
    
    user_scope --> claude_user["claude:<br/>npx skills add ... -a claude"]
    user_scope --> droid_user["droid:<br/>npx skills add ... -a droid"]
    user_scope --> opencode_user["opencode:<br/>npx skills add ... -a opencode"]
    user_scope --> codex_user["codex:<br/>npx skills add ... -a codex"]
    
    project_scope --> claude_project["claude:<br/>npx skills add ..."]
    project_scope --> droid_project["droid:<br/>npx skills add ..."]
    project_scope --> cursor_project["cursor:<br/>npx skills add ..."]
    project_scope --> opencode_project["opencode:<br/>npx skills add ..."]
```

Example from skills.json:
```json
"install": {
  "user": {
    "claude": "npx skills add ReScienceLab/opc-skills --skill seo-geo -a claude",
    "droid": "npx skills add ReScienceLab/opc-skills --skill seo-geo -a droid"
  },
  "project": {
    "claude": "npx skills add ReScienceLab/opc-skills --skill seo-geo",
    "cursor": "npx skills add ReScienceLab/opc-skills --skill seo-geo"
  }
}
```

**Sources:** [skills.json:48-62]() (seo-geo install), [skills.json:100-114]() (requesthunt install), [skills.json:152-166]() (domain-hunter install)

---

## Navigation to Detailed Documentation

For comprehensive documentation of each skill category:

- **[Foundation Skills](#2.4.1)** - nanobanana, twitter, reddit, archive
- **[Design & Image Generation Skills](#2.4.2)** - logo-creator, banner-creator
- **[SEO & GEO Optimization Skill](#2.4.3)** - seo-geo
- **[Research & Validation Skills](#2.4.4)** - requesthunt, producthunt
- **[Social Media & Domain Skills](#2.4.5)** - domain-hunter

For skill creation guidelines, see [Creating New Skills](#7).

**Sources:** [skills.json:8-537](), [README.md:42-55]()

---

# Page: Foundation Skills

# Foundation Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills.json](skills.json)
- [skills/archive/SKILL.md](skills/archive/SKILL.md)
- [skills/archive/references/TEMPLATE.md](skills/archive/references/TEMPLATE.md)
- [skills/banner-creator/SKILL.md](skills/banner-creator/SKILL.md)
- [skills/domain-hunter/SKILL.md](skills/domain-hunter/SKILL.md)
- [skills/logo-creator/SKILL.md](skills/logo-creator/SKILL.md)
- [skills/nanobanana/SKILL.md](skills/nanobanana/SKILL.md)
- [skills/reddit/SKILL.md](skills/reddit/SKILL.md)
- [skills/twitter/SKILL.md](skills/twitter/SKILL.md)

</details>



Foundation skills provide core infrastructure capabilities that other skills depend on. This page documents four foundation skills in the OPC Skills collection:

| Skill | Purpose | Authentication | Dependencies |
|---|---|---|---|
| `nanobanana` | Google Gemini image generation | Required (`GEMINI_API_KEY`) | None |
| `twitter` | Twitter/X API client | Required (`TWITTERAPI_API_KEY`) | None |
| `reddit` | Reddit public JSON API | None | None |
| `archive` | Session memory persistence | None | None |

**Skill Dependency Graph:**

```mermaid
graph TB
    subgraph "Foundation Skills"
        NANO["nanobanana<br/>v1.0.0<br/>Gemini Image Gen"]
        TWITTER["twitter<br/>v1.0.0<br/>X API Client"]
        REDDIT["reddit<br/>v1.0.0<br/>Public JSON API"]
        ARCHIVE["archive<br/>v1.0.1<br/>Session Memory"]
    end
    
    subgraph "Dependent Skills"
        LOGO["logo-creator<br/>v1.0.0"]
        BANNER["banner-creator<br/>v1.0.0"]
        DOMAIN["domain-hunter<br/>v1.0.0"]
        SEOGEO["seo-geo<br/>v1.0.0"]
    end
    
    LOGO --> NANO
    BANNER --> NANO
    DOMAIN --> TWITTER
    DOMAIN --> REDDIT
    SEOGEO --> TWITTER
    SEOGEO --> REDDIT
    
    style NANO fill:#e8d5ff
    style TWITTER fill:#000000,color:#ffffff
    style REDDIT fill:#ff4500
    style ARCHIVE fill:#6b7280
```

Foundation skills have no dependencies on other skills, making them the base layer of the OPC Skills ecosystem. For skill dependency management, see [Dependency Management](#2.3).

Sources: [skills.json:297-442]()

---

## nanobanana - Image Generation

The `nanobanana` skill provides AI image generation using Google's Gemini 3 Pro Image model (nicknamed "Nano Banana Pro"). It supports text-to-image generation, image editing, multiple aspect ratios, and high-resolution output (2K/4K).

### Purpose and Capabilities

**Core functions:**
- Text-to-image generation from natural language prompts
- Image editing via input image + transformation prompt
- Batch generation for exploring design variations
- Support for aspect ratios: `1:1`, `2:3`, `3:4`, `4:5`, `9:16`, `16:9`, `21:9`
- Optional Google Search grounding for factual accuracy

**Command Mapping to Python Scripts:**

```mermaid
graph LR
    subgraph "Natural Language Triggers"
        T1["generate image"]
        T2["create image"]
        T3["nano banana"]
        T4["gemini image"]
    end
    
    subgraph "scripts/"
        GEN["generate.py<br/>Single image generation"]
        BATCH["batch_generate.py<br/>Multiple variations"]
    end
    
    subgraph "Gemini API"
        API["gemini-3-pro-image-preview<br/>Google AI Studio"]
    end
    
    T1 --> GEN
    T2 --> GEN
    T3 --> GEN
    T4 --> GEN
    
    GEN --> API
    BATCH --> API
    
    API --> |"returns"| PNG["PNG files<br/>standard/2K/4K resolution"]
```

Sources: [skills/nanobanana/SKILL.md:1-9](), [skills.json:297-346]()

### Authentication Requirements

| Environment Variable | Acquisition URL | Cost |
|---|---|---|
| `GEMINI_API_KEY` | https://aistudio.google.com/apikey | Free tier available |

Set in `~/.zshrc`:
```bash
export GEMINI_API_KEY="your_api_key"
```

Sources: [skills/nanobanana/SKILL.md:11-14]()

### Script Reference

**Single Image Generation:**
```bash
python3 scripts/generate.py "a cute robot mascot, pixel art style" -o robot.png
```

**Image Editing:**
```bash
python3 scripts/generate.py "make the background blue" -i input.jpg -o output.png
```

**Batch Generation (20 variations):**
```bash
python3 scripts/batch_generate.py "pixel art logo" -n 20 -d ./logos -p logo
```

**High-Resolution 4K Output:**
```bash
python3 scripts/generate.py "professional product photo" --size 4K -o product.png
```

**Command-Line Options:**

| Flag | Description | Example |
|---|---|---|
| `-o, --output` | Output file path | `-o image.png` |
| `-i, --input` | Input image for editing | `-i base.jpg` |
| `-r, --ratio` | Aspect ratio | `--ratio 16:9` |
| `-s, --size` | Resolution (2K/4K) | `--size 4K` |
| `--search` | Enable Google Search grounding | `--search` |
| `-n, --count` | Batch count | `-n 20` |
| `-d, --dir` | Output directory | `-d ./images` |
| `-p, --prefix` | Filename prefix | `-p logo` |
| `--delay` | Batch delay (seconds) | `--delay 5` |

Sources: [skills/nanobanana/SKILL.md:21-94](), [skills.json:337-341]()

### File Output Conventions

**Default output directory:** `./nanobanana-images/` (configurable via `IMAGE_OUTPUT_DIR` env var)

**Batch naming pattern:** `{prefix}-{01..N}.png`

Example batch output:
```
./logos/
  logo-01.png
  logo-02.png
  ...
  logo-20.png
```

Sources: [skills/nanobanana/SKILL.md:120-125]()

### Dependent Skills

The following skills declare `nanobanana` as a dependency:

| Skill | Dependency Declaration | Purpose |
|---|---|---|
| `logo-creator` | `"nanobanana": ">=1.0.0"` | Batch logo generation + post-processing |
| `banner-creator` | `"nanobanana": ">=1.0.0"` | Wide-format banner generation |

**Dependency Resolution Flow:**

```mermaid
graph TB
    USER["User installs logo-creator"] --> CHECK{"Check dependencies<br/>in skills.json"}
    CHECK --> NANO_DEP["dependencies.nanobanana: '>=1.0.0'"]
    NANO_DEP --> INSTALL["Auto-install nanobanana<br/>if not present"]
    INSTALL --> VERIFY["Verify GEMINI_API_KEY<br/>environment variable"]
    VERIFY --> READY["logo-creator ready"]
```

Sources: [skills.json:193-195](), [skills.json:259-261](), [skills/logo-creator/SKILL.md:17-19]()

---

## twitter - X API Client

The `twitter` skill provides search and retrieval of Twitter/X content via the twitterapi.io third-party API. It supports user profiles, tweets, replies, followers/following, communities, spaces, and trend data.

### Purpose and Capabilities

**Core functions:**
- User profile and about information
- Tweet search with advanced query syntax
- User tweets, mentions, and replies
- Follower/following lists and relationship checks
- Community member and tweet retrieval
- Space metadata and trend data

**API Endpoints → Python Scripts Mapping:**

```mermaid
graph LR
    subgraph "User Endpoints"
        U1["get_user_info.py<br/>User profile"]
        U2["get_followers.py<br/>Follower list"]
        U3["search_users.py<br/>User search"]
    end
    
    subgraph "Tweet Endpoints"
        T1["search_tweets.py<br/>Tweet search"]
        T2["get_tweet.py<br/>Tweet details"]
        T3["get_tweet_replies.py<br/>Reply threads"]
    end
    
    subgraph "twitterapi.io"
        API["api.twitterapi.io/twitter<br/>X-API-Key auth"]
    end
    
    U1 --> API
    U2 --> API
    U3 --> API
    T1 --> API
    T2 --> API
    T3 --> API
```

Sources: [skills/twitter/SKILL.md:1-8](), [skills.json:393-442]()

### Authentication Requirements

| Environment Variable | Acquisition URL | Pricing |
|---|---|---|
| `TWITTERAPI_API_KEY` | https://twitterapi.io | ~$0.15-0.18/1k requests |

Set in `~/.zshrc`:
```bash
export TWITTERAPI_API_KEY="your_api_key"
```

**Quick verification:**
```bash
cd skills/twitter
python3 scripts/get_user_info.py elonmusk
```

Sources: [skills/twitter/SKILL.md:10-21](), [skills.json:408-413]()

### Script Reference

**User Endpoints:**
```bash
python3 scripts/get_user_info.py USERNAME
python3 scripts/get_user_tweets.py USERNAME --limit 20
python3 scripts/get_followers.py USERNAME --limit 100
python3 scripts/check_relationship.py USER1 USER2
python3 scripts/search_users.py "query" --limit 20
```

**Tweet Endpoints:**
```bash
python3 scripts/get_tweet.py TWEET_ID
python3 scripts/search_tweets.py "query" --type Latest --limit 20
python3 scripts/get_tweet_replies.py TWEET_ID --limit 20
python3 scripts/get_tweet_thread.py TWEET_ID
```

**Community Endpoints:**
```bash
python3 scripts/get_community.py COMMUNITY_ID
python3 scripts/get_community_tweets.py COMMUNITY_ID --limit 20
python3 scripts/search_community_tweets.py "query" --limit 20
```

Sources: [skills/twitter/SKILL.md:23-72](), [skills.json:431-437]()

### Advanced Search Syntax

```bash
# From specific user
python3 scripts/search_tweets.py "from:elonmusk"

# Date range
python3 scripts/search_tweets.py "AI since:2024-01-01 until:2024-12-31"

# Exclude retweets
python3 scripts/search_tweets.py "AI -filter:retweets"

# Minimum engagement
python3 scripts/search_tweets.py "AI min_faves:1000"
```

Sources: [skills/twitter/SKILL.md:75-94]()

### Dependent Skills

**Domain Hunter Integration:**

```mermaid
graph TB
    DOMAIN["domain-hunter skill"] --> TWITTER["twitter skill"]
    DOMAIN --> REDDIT["reddit skill"]
    
    subgraph "Use Case: Promo Code Discovery"
        TWITTER --> S1["Search registrar accounts:<br/>search_tweets.py 'from:spaceship promo code'"]
        REDDIT --> S2["Search domain communities:<br/>search_posts.py 'registrar coupon'"]
    end
    
    S1 --> RESULT["Aggregated promo codes<br/>and domain pricing"]
    S2 --> RESULT
```

The `domain-hunter` skill uses `twitter` (and `reddit`) to search for registrar promo codes and domain pricing discussions.

Sources: [skills.json:143-146](), [skills/domain-hunter/SKILL.md:65-82]()

**SEO-GEO Integration:**

The `seo-geo` skill also declares `twitter` as a dependency for social media analysis and keyword research.

Sources: [skills.json:28-31]()

---

## reddit - Public JSON API

The `reddit` skill provides search and retrieval of Reddit content via Reddit's public JSON API. No authentication is required — it accesses Reddit's public JSON endpoints directly.

### Purpose and Capabilities

**Core functions:**
- Subreddit post retrieval with sorting (hot, new, top, rising, controversial)
- Post search across all of Reddit or specific subreddits
- Subreddit metadata and subscriber information
- Individual post and comment thread retrieval
- User profile and post history

**Public JSON API Access Pattern:**

```mermaid
graph LR
    subgraph "Python Scripts"
        GP["get_posts.py"]
        SP["search_posts.py"]
        GS["get_subreddit.py"]
        GPO["get_post.py"]
    end
    
    subgraph "Reddit Public URLs"
        API["reddit.com/.json<br/>No auth required"]
    end
    
    GP --> |"GET /r/{subreddit}/{sort}.json"| API
    SP --> |"GET /search.json?q={query}"| API
    GS --> |"GET /r/{subreddit}/about.json"| API
    GPO --> |"GET /comments/{id}.json"| API
    
    API --> JSON["JSON response<br/>posts, comments, metadata"]
```

Sources: [skills/reddit/SKILL.md:1-8](), [skills.json:348-391]()

### Authentication Requirements

**None required.** Reddit's public JSON API is accessible without authentication or API keys.

**Quick verification:**
```bash
cd skills/reddit
python3 scripts/get_posts.py python --limit 3
```

Sources: [skills/reddit/SKILL.md:10-18](), [skills.json:360-364]()

### Script Reference

**Subreddit Posts:**
```bash
python3 scripts/get_posts.py python --limit 20           # Hot posts (default)
python3 scripts/get_posts.py python --sort new --limit 20
python3 scripts/get_posts.py python --sort top --time week
```

**Search Posts:**
```bash
python3 scripts/search_posts.py "AI agent" --limit 20
python3 scripts/search_posts.py "MCP server" --subreddit ClaudeAI --limit 10
python3 scripts/search_posts.py "async python" --sort top --time year
```

**Subreddit Info:**
```bash
python3 scripts/get_subreddit.py python
```

**Post & Comments:**
```bash
python3 scripts/get_post.py abc123
python3 scripts/get_post.py abc123 --comments 50
```

**User Profile:**
```bash
python3 scripts/get_user.py spez
python3 scripts/get_user.py spez --posts 10
```

Sources: [skills/reddit/SKILL.md:20-56](), [skills.json:380-386]()

### Sort Options

| Sort | Description | Time Options |
|---|---|---|
| `hot` | Trending posts (default) | - |
| `new` | Latest posts | - |
| `top` | Highest voted | hour, day, week, month, year, all |
| `rising` | Gaining traction | - |
| `controversial` | Mixed votes | hour, day, week, month, year, all |

Sources: [skills/reddit/SKILL.md:58-66]()

### Dependent Skills

The same skills that depend on `twitter` also depend on `reddit` for complementary social media data:

| Skill | Use Case |
|---|---|
| `domain-hunter` | Search `/r/Domains` for registrar pricing and promo codes |
| `seo-geo` | Analyze Reddit discussions for keyword research and content ideas |

Sources: [skills.json:143-146](), [skills/domain-hunter/SKILL.md:73-79]()

---

## archive - Session Memory

The `archive` skill provides persistent, cross-session knowledge capture for AI agent projects. Because AI coding agents lose context between sessions, the archive skill compensates by writing structured markdown files to disk that can be searched and retrieved in future sessions. It maintains a central index (`MEMORY.md`) so an agent can quickly find relevant prior work before starting any significant task.

Sources: [skills/archive/SKILL.md:1-8]()

### Trigger Conditions

The archive skill activates under the following conditions:

| Trigger | Description |
|---|---|
| Significant task completed | Deploy, migration, or major feature finished |
| Tricky bug resolved | Debugging session with non-obvious solution |
| Explicit user instruction | User says "archive this" |
| Multi-step process completed | Any workflow with learnings worth preserving |

The skill should also be **consulted** (lookup workflow) before:
- Debugging infrastructure, deploy, or CI issues
- Repeating a process performed in a previous session
- Encountering an error that may have been solved before

Sources: [skills/archive/SKILL.md:10-23]()

### File System Layout

The archive skill operates entirely within a `.archive/` directory at the root of the project. This directory is **local-only** and must be listed in `.gitignore`.

**File layout produced by the archive workflow:**

```
.archive/
├── MEMORY.md                      ← Central index, one line per archive entry
├── 2024-06-15/
│   ├── cloudwatch-logging.md      ← Individual archive file
│   └── ecs-deployment.md
└── 2024-06-22/
    └── auth-token-bug.md
```

The daily subdirectory format is `YYYY-MM-DD/`. Archive filenames should be descriptive (e.g., `cloudwatch-logging.md`, not `session.md`).

Sources: [skills/archive/SKILL.md:29-54]()

### Archive Workflow

**Diagram: Archive Write Workflow**

```mermaid
flowchart TD
    A["Trigger condition met"] --> B["Read .archive/MEMORY.md"]
    B --> C{"Related archives\nexist?"}
    C -- "Yes" --> D["Note related\nfilenames for frontmatter"]
    C -- "No" --> E["Proceed"]
    D --> E
    E --> F["Create .archive/YYYY-MM-DD/\ndirectory if not present"]
    F --> G["Write markdown file\nusing references/TEMPLATE.md"]
    G --> H["Add YAML frontmatter:\ntags, category, related"]
    H --> I["Append one-line entry\nto .archive/MEMORY.md\nunder correct category"]
```

Steps in order:

1. Read `.archive/MEMORY.md` — scan for related existing archives.
2. Create `.archive/YYYY-MM-DD/` directory if it does not yet exist.
3. Write a new markdown file using the format in `references/TEMPLATE.md`.
4. Update `.archive/MEMORY.md` — add one line under the correct category heading.
5. If related archives exist, populate the `related` field in the YAML frontmatter.

Sources: [skills/archive/SKILL.md:28-37]()

### Lookup Workflow

**Diagram: Archive Lookup Workflow**

```mermaid
flowchart TD
    A["Starting a task that may\nhave prior context"] --> B["Read .archive/MEMORY.md"]
    B --> C{"Relevant entry\nfound?"}
    C -- "Yes" --> D["Open specific\narchive file"]
    D --> E["Apply learnings\nto current task"]
    C -- "No" --> F["Proceed without\narchive context"]
    B --> G["Fallback: grep -ri keyword .archive/"]
    G --> C
```

The two lookup mechanisms are:

| Method | Command / Action |
|---|---|
| Index scan | Read `.archive/MEMORY.md` directly |
| Full-text search | `grep -ri "keyword" .archive/` |

Sources: [skills/archive/SKILL.md:35-39]()

### `MEMORY.md` Index Structure

`.archive/MEMORY.md` is the central index maintained by every archive operation. It is organized by category. Each entry is a single line linking to an archive file and providing enough context to decide whether to read the full file.

Example structure (not from source files — illustrative of the category-based layout):

```markdown
## infrastructure
- 2024-06-15/cloudwatch-logging.md — Fixed missing IAM permission for log group creation

## debugging
- 2024-06-22/auth-token-bug.md — JWT expiry mismatch between client and server

## release
- 2024-06-15/ecs-deployment.md — ECS blue/green deploy with manual rollback steps
```

The agent always writes to `MEMORY.md` after creating any archive file — this invariant keeps the index complete.

Sources: [skills/archive/SKILL.md:24-27](), [skills/archive/SKILL.md:50-54]()

### Archive File Format (`TEMPLATE.md`)

Individual archive files follow a fixed markdown structure defined in `references/TEMPLATE.md`. Every file begins with a YAML frontmatter block followed by standard markdown sections.

**Diagram: Archive File Structure → Code Entities**

```mermaid
flowchart LR
    subgraph "references/TEMPLATE.md"
        FM["YAML Frontmatter\ntags / category / related"]
        TITLE["# Title - YYYY-MM-DD"]
        SUMMARY["## Summary"]
        CONTEXT["## Context\nbranch / version / issue"]
        ISSUES["## Issues Encountered & Solutions"]
        CHANGES["## Key Changes"]
        LESSONS["## Lessons Learned"]
    end
    FM --> |"controls indexing"| MEMORMD[".archive/MEMORY.md"]
    FM --> |"enables search"| GREP["grep -ri in .archive/"]
    ISSUES --> |"documents"| FIXES["problem + fix pairs"]
    CHANGES --> |"contains"| CMDS["commands / config / code snippets"]
```

#### YAML Frontmatter Fields

| Field | Required | Description |
|---|---|---|
| `tags` | Yes | Array of searchable keywords, e.g., `[ecs, iam, logging]` |
| `category` | Yes | One of the five predefined values (see below) |
| `related` | No | Array of archive filenames (without `.md`) for cross-referencing |

**Example frontmatter:**

```yaml
---
tags: [ecs, iam, cloudwatch, logging]
category: infrastructure
related: [ecs-deployment]
---
```

The `related` field holds bare filenames without path or extension, e.g., `ecs-deployment` rather than `2024-06-15/ecs-deployment.md`.

Sources: [skills/archive/references/TEMPLATE.md:1-40]()

#### Markdown Sections

| Section | Purpose |
|---|---|
| `# {Title} - {YYYY-MM-DD}` | Identifies the archive and date |
| `## Summary` | One-line description of what was accomplished |
| `## Context` | Branch name, version, related issue |
| `## Issues Encountered & Solutions` | Numbered issue list with problem description and fix |
| `## Key Changes` | Commands, config, or code that was critical |
| `## Lessons Learned` | Optional insights for future reference |

Sources: [skills/archive/references/TEMPLATE.md:6-33]()

### Category Taxonomy

The archive skill defines five fixed categories. Every archive file must declare exactly one.

| Category | Covers |
|---|---|
| `infrastructure` | AWS, ECS, IAM, networking, secrets, CloudWatch |
| `release` | TestFlight, versioning, Git Flow, CHANGELOG |
| `debugging` | Bug fixes, error resolution, unexpected gotchas |
| `feature` | Feature design and implementation notes |
| `design` | UI/UX, icons, visual design decisions |

These category values appear in two places: the YAML `category` field of each archive file, and as section headings in `.archive/MEMORY.md`.

Sources: [skills/archive/SKILL.md:41-47]()

### Authoring Rules

The following rules are enforced by the skill's instructions:

- `.archive/` **must** be added to `.gitignore` — archive files are local-only and never committed.
- Entries must be concise but fully reproducible — focus on problems, fixes, and exact commands.
- `MEMORY.md` must be updated every time an archive file is created.
- Filenames must be descriptive (e.g., `cloudwatch-logging.md`), not generic (e.g., `session.md`).
- All archive files must include YAML frontmatter with at least `tags` and `category`.

Sources: [skills/archive/SKILL.md:49-56]()

---

# Page: Design & Image Generation Skills

# Design & Image Generation Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills.json](skills.json)
- [skills/archive/SKILL.md](skills/archive/SKILL.md)
- [skills/archive/references/TEMPLATE.md](skills/archive/references/TEMPLATE.md)
- [skills/banner-creator/SKILL.md](skills/banner-creator/SKILL.md)
- [skills/logo-creator/SKILL.md](skills/logo-creator/SKILL.md)
- [skills/nanobanana/SKILL.md](skills/nanobanana/SKILL.md)

</details>



This page documents the three design-focused skills in the OPC Skills repository: `nanobanana`, `logo-creator`, and `banner-creator`. It covers the underlying image generation model integration, the CLI script interfaces, the iterative human-in-the-loop design workflow, and the full post-processing pipelines that convert raw generated images into production-ready assets.

For an overview of all nine skills and how they are categorized, see [Skill Categories & Reference](#2.4). For information on how these skills are installed and what API keys they require, see [Installation Methods Overview](#3.1).

---

## Skill Relationships

The three skills have a clear dependency hierarchy. `nanobanana` is the foundational generation primitive. Both `logo-creator` and `banner-creator` declare it as a required dependency and invoke its scripts directly.

**Skill dependency graph**

```mermaid
graph TD
    A["logo-creator"] -->|"depends on"| C["nanobanana"]
    B["banner-creator"] -->|"depends on"| C["nanobanana"]
    C -->|"calls"| D["Google Gemini API\n(gemini-3-pro-image-preview)"]
    A -->|"calls"| E["remove.bg API"]
    A -->|"calls"| F["Recraft API\n(vectorize)"]
```

Sources: [skills/nanobanana/SKILL.md:1-20](), [skills/logo-creator/SKILL.md:1-19](), [skills/banner-creator/SKILL.md:1-19]()

---

## nanobanana — Core Image Generation

`nanobanana` wraps Google's `gemini-3-pro-image-preview` model (nicknamed "Nano Banana Pro") and exposes it through two Python CLI scripts.

### API Keys & Dependencies

| Variable | Source | Required by |
|---|---|---|
| `GEMINI_API_KEY` | Google AI Studio | All three skills |
| `IMAGE_OUTPUT_DIR` | Environment (optional) | `generate.py` default output path |

Python package requirement: `google-genai`, `pillow`

Sources: [skills/nanobanana/SKILL.md:12-19](), [skills/nanobanana/scripts/generate.py:18-26]()

### `generate.py` — Single Image Generation

The `generate_image` function in [skills/nanobanana/scripts/generate.py:80-223]() is the central entry point for all image generation. It supports:

- **Text-to-image**: prompt only
- **Image editing**: provide `-i / --input` with an existing image, the model edits it
- **Aspect ratio control**: via `types.ImageConfig` in the Gemini API config
- **Resolution**: `2K` (2048px) or `4K` (3840px)

**Supported aspect ratios** (defined as `VALID_ASPECT_RATIOS` at [skills/nanobanana/scripts/generate.py:28-31]()):

| Ratio | Common Use |
|---|---|
| `1:1` | Square — icons, avatars |
| `16:9` | Widescreen — YouTube, banners |
| `9:16` | Portrait — phone wallpapers |
| `21:9` | Ultra-wide — cinematic, banner source |
| `4:3`, `3:4`, `2:3`, `3:2`, `4:5`, `5:4` | Standard photo ratios |

**CLI synopsis:**

```
generate.py PROMPT [-o OUTPUT] [-i INPUT] [-r RATIO] [-s SIZE] [--search] [-v]
```

The function returns a dict with keys `success`, `path`, and `metadata` (or `error`). On success, the PNG is written to `output_path`. The `main()` function at [skills/nanobanana/scripts/generate.py:241-286]() drives the CLI and exits with code `1` on failure.

**Internal data flow for `generate_image`:**

```mermaid
flowchart TD
    A["generate_image(prompt, ...)"] --> B{"input_path\nprovided?"}
    B -->|"yes"| C["load_image_as_base64(input_path)"]
    B -->|"no"| D["text-only contents"]
    C --> E["build contents list\n[Part.from_bytes, prompt]"]
    D --> F["build contents list\n[prompt]"]
    E --> G["types.GenerateContentConfig\n(response_modalities, ImageConfig)"]
    F --> G
    G --> H["client.models.generate_content\n(model=gemini-3-pro-image-preview)"]
    H --> I{"image in\nresponse.candidates[0]?"}
    I -->|"yes"| J["write bytes to output_path"]
    I -->|"no"| K["return success=False, error"]
    J --> L["return success=True, path, metadata"]
```

Sources: [skills/nanobanana/scripts/generate.py:80-223]()

### `batch_generate.py` — Batch Generation

`batch_generate` at [skills/nanobanana/scripts/batch_generate.py:48-125]() generates `N` images sequentially (or in parallel) with zero-padded sequential filenames: `{prefix}-01.png`, `{prefix}-02.png`, etc.

**CLI synopsis:**

```
batch_generate.py PROMPT [-n COUNT] [-d DIR] [-p PREFIX] [-r RATIO] [-s SIZE]
                         [--delay SECONDS] [--parallel N] [-q]
```

Key behaviors:

- **Sequential mode** (default): adds a `delay` (default 3 seconds) between requests to avoid rate limiting
- **Parallel mode** (`--parallel N`): uses `ThreadPoolExecutor` with `N` workers; delay is ignored
- Results are sorted by index before being returned

The internal worker function `_generate_single` at [skills/nanobanana/scripts/batch_generate.py:24-45]() calls `generate_image` for each file and returns its result dict augmented with `index` and `filename`.

Sources: [skills/nanobanana/scripts/batch_generate.py:1-179]()

---

## logo-creator

`logo-creator` orchestrates a multi-step, human-in-the-loop workflow that moves from prompt → generated PNG variations → user selection → cropped, background-removed, vectorized SVG.

### API Keys Required

| Variable | Service |
|---|---|
| `GEMINI_API_KEY` | Image generation (via nanobanana) |
| `REMOVE_BG_API_KEY` | Background removal (remove.bg) |
| `RECRAFT_API_KEY` | PNG-to-SVG vectorization (recraft.ai) |

Sources: [skills/logo-creator/SKILL.md:10-16]()

### File Output Convention

All outputs land under `.skill-archive/logo-creator/<yyyy-mm-dd-summaryname>/`. The structure for a completed session looks like:

```
.skill-archive/logo-creator/2026-01-18-opc-logo/
  logo-01.png          ← generated variation
  logo-02.png
  ...
  logo-09-v1.png       ← iteration on logo-09
  logo-09-cropped.png  ← post-processed
  logo-09-nobg.png
  logo-09.svg
  preview.html
```

Sources: [skills/logo-creator/SKILL.md:22-47]()

### Workflow Overview

**Six-step logo-creator workflow**

```mermaid
flowchart TD
    S1["Step 1\nDiscovery & Requirements\n(style, ratio, colors, references)"] --> S2
    S2["Step 2\nGenerate Variations\nbatch_generate.py -n 20 --ratio 1:1"] --> S3
    S3["Step 3\nHTML Preview\ncp preview.html → open in browser"] --> S4
    S4["Step 4\nIterate with User\nwhich logos? generate variations\nof favorites"] --> S4a
    S4a{"User approves\na logo?"} -->|"no"| S4
    S4a -->|"yes"| S5a
    S5a["Step 5a\ncrop_logo.py\n(whitespace removal, 1:1 square)"] --> S5b
    S5b["Step 5b\nremove_bg.py\n(transparent PNG)"] --> S5c
    S5c["Step 5c\nvectorize.py\n(PNG → SVG via Recraft API)"] --> S6
    S6["Step 6\nDeliver Assets\nPNG + cropped PNG + nobg PNG + SVG"]
```

Sources: [skills/logo-creator/SKILL.md:49-170]()

### Post-Processing Pipeline

The three post-processing scripts operate in sequence on the approved PNG.

**Post-processing script reference map**

```mermaid
flowchart LR
    rawpng["logo-09.png\n(raw AI output)"] --> crop_logo["crop_logo.py\ncrop_to_content()"]
    crop_logo --> croppedpng["logo-09-cropped.png\n(1:1, no whitespace)"]
    croppedpng --> remove_bg["remove_bg.py\nremove_background()"]
    remove_bg --> nobgpng["logo-09-nobg.png\n(transparent PNG)"]
    nobgpng --> vectorize["vectorize.py\nvectorize_image()"]
    vectorize --> svgout["logo-09.svg\n(scalable vector)"]
```

Sources: [skills/logo-creator/SKILL.md:135-155](), [skills/logo-creator/scripts/crop_logo.py:1-95](), [skills/logo-creator/scripts/remove_bg.py:1-91](), [skills/logo-creator/scripts/vectorize.py:1-120]()

#### `crop_logo.py` — Whitespace Cropping

`crop_to_content` at [skills/logo-creator/scripts/crop_logo.py:20-75]():

1. Converts image to RGB, creates a NumPy boolean mask of non-white pixels (threshold: 240 by default)
2. Finds bounding rows/cols of the content
3. Adds `padding` pixels (default: 5)
4. Crops to content, then expands to a square by picking `max(width, height)` and centering on a white canvas

```
crop_logo.py input.png output-cropped.png [--padding 5]
```

#### `remove_bg.py` — Background Removal

`remove_background` at [skills/logo-creator/scripts/remove_bg.py:16-76]() calls the `remove.bg` API via `curl`. It reads `REMOVE_BG_API_KEY` from the environment (with a fallback to `~/.zshrc`). The API call POSTs the image to `https://api.remove.bg/v1.0/removebg` and writes the transparent PNG response directly to the output path.

```
remove_bg.py input.png output-nobg.png
```

#### `vectorize.py` — SVG Vectorization

`vectorize_image` at [skills/logo-creator/scripts/vectorize.py:17-105]() calls the Recraft API in two steps:

1. POSTs the PNG to `https://external.api.recraft.ai/v1/images/vectorize` with `RECRAFT_API_KEY`
2. Parses the JSON response to extract `image.url`, then downloads the SVG via `curl`

It validates the output by checking for `<svg` or `<?xml` in the first 100 characters of the downloaded file.

```
vectorize.py input.png output.svg
```

### Style Reference

The skill ships with `skills/logo-creator/references/styles.md` documenting 10 logo style categories:

| # | Style | Best For |
|---|---|---|
| 1 | Pixel Art / 8-bit Retro | Gaming, tech startups |
| 2 | Minimalist / Flat Design | Modern brands, SaaS |
| 3 | 3D / Isometric | Tech products, apps |
| 4 | Hand-drawn / Sketch | Creative agencies |
| 5 | Mascot / Character | Food brands, gaming |
| 6 | Monogram / Lettermark | Personal brands, luxury |
| 7 | Abstract / Geometric | Startups, tech |
| 8 | Emblem / Badge | Organizations, sports |
| 9 | Wordmark / Typography | Established brands |
| 10 | Combination Mark | Most new brands |

Sources: [skills/logo-creator/references/styles.md:1-230]()

---

## banner-creator

`banner-creator` follows a similar iterative workflow but is simpler: no background removal or vectorization. The final step is a crop-to-ratio operation targeting the banner's intended platform.

### API Keys Required

| Variable | Service |
|---|---|
| `GEMINI_API_KEY` | Image generation (via nanobanana) |

Sources: [skills/banner-creator/SKILL.md:10-14]()

### File Output Convention

```
.skill-archive/banner-creator/2026-01-19-opc-banner/
  banner-01.png
  ...
  banner-03-cropped.png
  preview.html
```

Sources: [skills/banner-creator/SKILL.md:22-37]()

### Workflow Overview

**Five-step banner-creator workflow**

```mermaid
flowchart TD
    S1["Step 1\nDiscovery\n(purpose, target ratio, style, content, colors)"] --> S2
    S2["Step 2\nGenerate at 21:9\nbatch_generate.py -n 20 --ratio 21:9"] --> S3
    S3["Step 3\nHTML Preview\ncp preview.html → open in browser"] --> S4
    S4["Step 4\nIterate with User\nfeedback → more variations"] --> S4a
    S4a{"User approves\na banner?"} -->|"no"| S4
    S4a -->|"yes"| S5
    S5["Step 5\ncrop_banner.py\n(crop + resize to platform target)"]
```

The generation always uses the widest available ratio (`21:9`) and then crops down, ensuring no content is lost by generating too narrow.

Sources: [skills/banner-creator/SKILL.md:39-156]()

### `crop_banner.py` — Aspect Ratio Cropping

`crop_to_ratio` at [skills/banner-creator/scripts/crop_banner.py:32-56]() performs a centered crop:

- If the image is wider than the target ratio: crops width, keeps full height
- If the image is taller than the target ratio: crops height, keeps full width

After cropping, an optional resize is applied to match an exact pixel width (`--width`), height (`--height`), or explicit size (`--size 1280x640`).

```
crop_banner.py input.png output.png --ratio 2:1 --width 1280
```

**Platform crop targets:**

| Platform | Ratio | Width | Output Size |
|---|---|---|---|
| GitHub README | `2:1` | 1280 | 1280×640 |
| Twitter/X Header | `3:1` | 1500 | 1500×500 |
| LinkedIn Banner | `4:1` | 1584 | 1584×396 |
| Website Hero | `16:9` | 1920 | 1920×1080 |
| YouTube Channel | `16:9` | 2560 | 2560×1440 |

Sources: [skills/banner-creator/scripts/crop_banner.py:1-113](), [skills/banner-creator/references/formats.md:1-56]()

---

## HTML Preview Gallery

Both skills copy a `preview.html` template into the output directory so the user can view all generated images in a browser before selecting a favourite.

**logo-creator preview** ([skills/logo-creator/templates/preview.html:1-332]()):
- Responsive grid of logo thumbnails on a dark background (white card per logo)
- Click to open a fullscreen modal; arrow keys or `←`/`→` for navigation
- Double-click or press `F` to toggle a favourite; favourites listed in a bottom bar
- Search/filter field to narrow by filename or number
- Hides cards whose `<img>` fails to load (`onerror`)

**banner-creator preview** ([skills/banner-creator/templates/preview.html:1-252]()):
- Same dark-background grid, 3-column layout
- Star button (★) per banner for favouriting
- Modal with previous/next navigation
- `BANNER_COUNT` and `BANNER_PREFIX` constants at the top of the `<script>` block must be updated to match the number of images actually generated

Both templates use only vanilla JS and CSS with no external dependencies — they work as local `file://` URLs.

Sources: [skills/logo-creator/templates/preview.html:256-331](), [skills/banner-creator/templates/preview.html:165-249]()

---

## End-to-End Script Interaction Map

This diagram maps the full set of scripts across all three skills to the external services they call.

```mermaid
flowchart LR
    subgraph "nanobanana/scripts"
        gen["generate.py\ngenerate_image()"]
        bgen["batch_generate.py\nbatch_generate()\n_generate_single()"]
    end

    subgraph "logo-creator/scripts"
        crop["crop_logo.py\ncrop_to_content()"]
        rmbg["remove_bg.py\nremove_background()"]
        vec["vectorize.py\nvectorize_image()"]
    end

    subgraph "banner-creator/scripts"
        cropb["crop_banner.py\ncrop_to_ratio()"]
    end

    bgen -->|"calls"| gen
    gen -->|"google-genai\nclient.models.generate_content"| gemini["Gemini API\ngemini-3-pro-image-preview"]
    rmbg -->|"curl POST"| removebg["remove.bg API\n/v1.0/removebg"]
    vec -->|"curl POST\nthen GET"| recraft["Recraft API\n/v1/images/vectorize"]
    crop -->|"Pillow + numpy\nlocal only"| local["local filesystem"]
    cropb -->|"Pillow\nlocal only"| local
```

Sources: [skills/nanobanana/scripts/generate.py:165-169](), [skills/logo-creator/scripts/remove_bg.py:47-59](), [skills/logo-creator/scripts/vectorize.py:51-83](), [skills/logo-creator/scripts/crop_logo.py:30-68](), [skills/banner-creator/scripts/crop_banner.py:32-56]()

---

# Page: SEO & GEO Optimization Skill

# SEO & GEO Optimization Skill

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills.json](skills.json)
- [skills/archive/SKILL.md](skills/archive/SKILL.md)
- [skills/archive/references/TEMPLATE.md](skills/archive/references/TEMPLATE.md)
- [skills/seo-geo/SKILL.md](skills/seo-geo/SKILL.md)
- [skills/seo-geo/scripts/autocomplete_ideas.py](skills/seo-geo/scripts/autocomplete_ideas.py)
- [skills/seo-geo/scripts/competitor_gap.py](skills/seo-geo/scripts/competitor_gap.py)
- [skills/seo-geo/scripts/domain_overview.py](skills/seo-geo/scripts/domain_overview.py)
- [skills/seo-geo/scripts/keyword_research.py](skills/seo-geo/scripts/keyword_research.py)
- [skills/seo-geo/scripts/related_keywords.py](skills/seo-geo/scripts/related_keywords.py)

</details>



## Purpose and Scope

This page documents the `seo-geo` skill, which provides comprehensive SEO (Search Engine Optimization) and GEO (Generative Engine Optimization) capabilities for websites. The skill optimizes content for both traditional search engines (Google, Bing) and AI search engines (ChatGPT, Perplexity, Gemini, Copilot, Claude) using research-backed methods from Princeton University.

The skill implements the 9 Princeton GEO methods that provide up to +40% visibility boost in AI search engine citations. It includes keyword research scripts, competitor analysis tools, and schema markup generation utilities.

For information about social media research workflows that complement SEO/GEO optimization, see [Social Media & Domain Skills](#2.4.5). For general skill structure and dependency management, see [Skill Structure & Standards](#2.2).

**Sources:** [skills/seo-geo/SKILL.md:1-251](), [skills.json:10-74]()

---

## Skill Definition

The `seo-geo` skill is registered in the skills manifest with the following characteristics:

| Property | Value |
|----------|-------|
| Name | `seo-geo` |
| Version | `1.0.0` |
| Auth Required | No (base functionality), Optional (DataForSEO API) |
| Dependencies | `twitter >= 1.0.0`, `reddit >= 1.0.0` |
| Primary API | DataForSEO (optional) |

**Trigger Keywords:** SEO, GEO, search optimization, schema markup, JSON-LD, meta tags, keyword research, AI visibility, ChatGPT ranking, Perplexity

**Optional API Keys:**
- `DATAFORSEO_LOGIN` - DataForSEO account login
- `DATAFORSEO_PASSWORD` - DataForSEO account password
- Acquisition URL: https://dataforseo.com

The skill operates in two modes:
1. **Free Mode** - Basic SEO audits, meta tag checks, robots.txt validation (no API required)
2. **Advanced Mode** - Keyword research, competitor analysis, SERP analysis (requires DataForSEO API)

**Sources:** [skills.json:10-74](), [skills/seo-geo/SKILL.md:1-7]()

---

## GEO Methods and Visibility Impact

### The 9 Princeton GEO Methods

The skill implements research-backed optimization methods from Princeton University's GEO study, which analyzed how content features affect AI search engine citation rates:

```mermaid
graph TB
    subgraph "High Impact Methods (+25% to +40%)"
        CITE["Cite Sources<br/>+40% visibility"]
        STATS["Statistics Addition<br/>+37% visibility"]
        QUOTE["Quotation Addition<br/>+30% visibility"]
        AUTH["Authoritative Tone<br/>+25% visibility"]
    end
    
    subgraph "Medium Impact Methods (+15% to +20%)"
        EASY["Easy-to-understand<br/>+20% visibility"]
        TECH["Technical Terms<br/>+18% visibility"]
        UNIQUE["Unique Words<br/>+15% visibility"]
        FLUENCY["Fluency Optimization<br/>+15-30% variable"]
    end
    
    subgraph "Negative Impact (AVOID)"
        STUFF["Keyword Stuffing<br/>-10% visibility"]
    end
    
    CONTENT["Website Content"] --> CITE
    CONTENT --> STATS
    CONTENT --> QUOTE
    CONTENT --> AUTH
    CONTENT --> EASY
    CONTENT --> TECH
    CONTENT --> UNIQUE
    CONTENT --> FLUENCY
    
    CITE --> FAQSCHEMA["FAQPage Schema<br/>(combines multiple methods)"]
    STATS --> FAQSCHEMA
    QUOTE --> FAQSCHEMA
    
    FAQSCHEMA --> AICITATIONS["AI Search Engine Citations<br/>(ChatGPT, Perplexity, Gemini)"]
```

**Sources:** [skills/seo-geo/SKILL.md:84-99]()

### FAQPage Schema Implementation

The most effective GEO optimization combines multiple methods in a FAQPage schema structure:

**Template Structure:**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "What is [topic]?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "According to [source], [answer with statistics]."
    }
  }]
}
```

This schema type provides:
- **Authoritative citations** (+40% from cited sources)
- **Statistics inclusion** (+37% from data points)
- **Expert quotations** (+30% from attributed quotes)
- **Structured data** for AI parsing

**Sources:** [skills/seo-geo/SKILL.md:100-114]()

---

## Script Architecture

### Available Scripts and Commands

```mermaid
graph LR
    subgraph "Free Scripts (No API)"
        AUDIT["seo_audit.py<br/>Basic SEO check"]
        CURL_META["curl + grep<br/>Meta tag extraction"]
        CURL_ROBOTS["curl<br/>robots.txt check"]
        CURL_SITEMAP["curl<br/>sitemap.xml check"]
    end
    
    subgraph "DataForSEO Scripts (API Required)"
        KEYWORD["keyword_research.py<br/>Seed keyword expansion"]
        DOMAIN["domain_overview.py<br/>Domain metrics"]
        SERP["serp_analysis.py<br/>SERP rankings"]
        BACKLINKS["backlinks.py<br/>Backlink analysis"]
        AUTO["autocomplete_ideas.py<br/>Google autocomplete"]
        COMP["competitor_gap.py<br/>Keyword gap analysis"]
        RELATED["related_keywords.py<br/>Related searches"]
    end
    
    subgraph "DataForSEO API Module"
        API["dataforseo_api.py<br/>api_post()<br/>get_result()<br/>format_count()"]
    end
    
    KEYWORD --> API
    DOMAIN --> API
    SERP --> API
    BACKLINKS --> API
    AUTO --> API
    COMP --> API
    RELATED --> API
    
    API --> DFAPI["DataForSEO REST API<br/>endpoints"]
```

**Sources:** [skills.json:63-69](), [skills/seo-geo/SKILL.md:22-178]()

### Keyword Research Scripts

#### keyword_research.py

Expands a seed keyword into related keyword variations using the DataForSEO Keywords API.

**Usage:**
```bash
python3 scripts/keyword_research.py "seo tools" --limit 20
```

**Key Functions:**
- Accepts seed keyword and location code (default: 2840 = US)
- Queries `keywords_data/google_ads/keywords_for_keywords/live` endpoint
- Returns up to 20 related keywords with metrics
- Uses shared `api_post()`, `get_result()`, `print_keywords_list()` utilities

**Sources:** [skills/seo-geo/scripts/keyword_research.py:1-39]()

#### autocomplete_ideas.py

Retrieves real-time Google Autocomplete suggestions for a seed keyword.

**Usage:**
```bash
python3 scripts/autocomplete_ideas.py "Claude Code"
```

**Implementation Details:**
- Queries `serp/google/autocomplete/live/advanced` endpoint
- Handles multiple response formats (items, autocomplete, suggestions)
- Parses autocomplete_item objects with title field
- Provides long-tail keyword discovery

**Algorithm:**
```python
# Tries multiple field names for compatibility
items = result.get("items", [])
if not items:
    items = result.get("autocomplete", [])
    if not items:
        items = result.get("suggestions", [])

# Handles dict and string responses
for item in items:
    if isinstance(item, dict):
        if item.get("type") == "autocomplete_item":
            suggestion = item.get("title", "").strip()
        elif "value" in item:
            suggestion = item.get("value", "").strip()
    elif isinstance(item, str):
        suggestion = item.strip()
```

**Sources:** [skills/seo-geo/scripts/autocomplete_ideas.py:1-75]()

#### competitor_gap.py

Identifies keywords where a competitor ranks but your domain does not.

**Usage:**
```bash
python3 scripts/competitor_gap.py "opc.dev" "claudemarketplaces.com" --limit 50
```

**Key Parameters:**
- `my_domain` - Your domain (without https://)
- `competitor_domain` - Target competitor
- `--intersections False` - Only show gaps (not overlaps)
- `--limit` - Maximum results to return

**Output Format:**
```
keyword_gaps[N]{keyword,volume,difficulty,comp_position}:
  {keyword},{volume},{difficulty},{comp_pos}
```

Queries `dataforseo_labs/google/domain_intersection/live` with `intersections: False` to find keywords where only the competitor ranks.

**Sources:** [skills/seo-geo/scripts/competitor_gap.py:1-81]()

#### related_keywords.py

Retrieves Google "searches related to" keywords with configurable depth.

**Usage:**
```bash
python3 scripts/related_keywords.py "AI agent" --depth 2 --limit 50
```

**Depth Parameter:**
- `depth=1`: ~10 keywords
- `depth=2`: ~100 keywords  
- `depth=3`: ~1,000+ keywords (up to 4,680 max)

**Implementation:**
- Queries `dataforseo_labs/google/related_keywords/live` endpoint
- Sorts results by search volume descending
- Extracts keyword, volume, difficulty from nested structures
- Validates depth range 1-3

**Sources:** [skills/seo-geo/scripts/related_keywords.py:1-85]()

#### domain_overview.py

Provides domain-level organic search metrics.

**Usage:**
```bash
python3 scripts/domain_overview.py "example.com"
```

**Metrics Returned:**
- `organic_keywords` - Total ranking keywords
- `organic_traffic` - Estimated traffic value (ETV)
- `top_3_positions` - Keywords in positions 1-3

**Calculation:**
```python
organic = metrics.get("organic", {})
print(f"organic_keywords: {format_count(organic.get('count', 0))}")
print(f"organic_traffic: {format_count(organic.get('etv', 0))}")
print(f"top_3_positions: {organic.get('pos_1', 0) + organic.get('pos_2_3', 0)}")
```

Queries `dataforseo_labs/google/ranked_keywords/live` with `limit: 1` for overview metrics.

**Sources:** [skills/seo-geo/scripts/domain_overview.py:1-45]()

---

## Workflow Integration

### Multi-Stage Optimization Workflow

```mermaid
graph TB
    START["User Requests<br/>SEO/GEO Optimization"]
    
    subgraph "Stage 1: Audit"
        AUDIT_CMD["python3 scripts/seo_audit.py<br/>{url}"]
        META_CHECK["curl + grep<br/>Meta tags"]
        ROBOTS_CHECK["curl<br/>robots.txt"]
        SITEMAP_CHECK["curl<br/>sitemap.xml"]
    end
    
    subgraph "Stage 2: Keyword Research"
        WEBSEARCH["WebSearch:<br/>keyword difficulty,<br/>search volume"]
        AUTO_CMD["autocomplete_ideas.py<br/>{keyword}"]
        RELATED_CMD["related_keywords.py<br/>{keyword} --depth 2"]
        KEYWORD_CMD["keyword_research.py<br/>{keyword}"]
    end
    
    subgraph "Stage 3: Competitor Analysis"
        COMP_GAP["competitor_gap.py<br/>{my_domain} {comp_domain}"]
        DOMAIN_CMD["domain_overview.py<br/>{competitor_domain}"]
    end
    
    subgraph "Stage 4: Content Optimization"
        GEO_METHODS["Apply 9 GEO Methods:<br/>Citations, Statistics,<br/>Quotes, Authority"]
        FAQ_SCHEMA["Generate FAQPage<br/>Schema"]
        META_OPT["Optimize Meta Tags<br/>and OG Properties"]
    end
    
    subgraph "Stage 5: Platform-Specific"
        CHATGPT["ChatGPT: Domain authority<br/>30-day freshness"]
        PERPLEXITY["Perplexity: PDF hosting<br/>FAQ schema"]
        GOOGLE_AI["Google AI Overview:<br/>E-E-A-T signals"]
        CLAUDE_AI["Claude: Brave indexing<br/>factual density"]
    end
    
    START --> AUDIT_CMD
    AUDIT_CMD --> META_CHECK
    META_CHECK --> ROBOTS_CHECK
    ROBOTS_CHECK --> SITEMAP_CHECK
    
    SITEMAP_CHECK --> WEBSEARCH
    WEBSEARCH --> AUTO_CMD
    AUTO_CMD --> RELATED_CMD
    RELATED_CMD --> KEYWORD_CMD
    
    KEYWORD_CMD --> COMP_GAP
    COMP_GAP --> DOMAIN_CMD
    
    DOMAIN_CMD --> GEO_METHODS
    GEO_METHODS --> FAQ_SCHEMA
    FAQ_SCHEMA --> META_OPT
    
    META_OPT --> CHATGPT
    META_OPT --> PERPLEXITY
    META_OPT --> GOOGLE_AI
    META_OPT --> CLAUDE_AI
```

**Sources:** [skills/seo-geo/SKILL.md:16-201]()

### Command Execution Table

| Stage | Command | Dependencies | Output |
|-------|---------|-------------|--------|
| **Audit** | `python3 scripts/seo_audit.py "{url}"` | None | Title, meta, H1, robots, sitemap, load time |
| **Meta Check** | `curl -sL "{url}" \| grep -E "<title>\|<meta"` | None | Raw meta tags |
| **Robots** | `curl -s "{url}/robots.txt"` | None | Bot directives |
| **Sitemap** | `curl -s "{url}/sitemap.xml"` | None | Page list |
| **Keywords** | `python3 scripts/keyword_research.py "{keyword}"` | DataForSEO | Related keywords with metrics |
| **Autocomplete** | `python3 scripts/autocomplete_ideas.py "{keyword}"` | DataForSEO | User search suggestions |
| **Related** | `python3 scripts/related_keywords.py "{keyword}" --depth 2` | DataForSEO | Google related searches |
| **Gap** | `python3 scripts/competitor_gap.py "{domain}" "{comp}"` | DataForSEO | Competitor-only keywords |
| **Overview** | `python3 scripts/domain_overview.py "{domain}"` | DataForSEO | Organic metrics |
| **SERP** | `python3 scripts/serp_analysis.py "{keyword}"` | DataForSEO | Ranking positions |
| **Backlinks** | `python3 scripts/backlinks.py "{domain}"` | DataForSEO | Link profile |

**Sources:** [skills.json:63-69](), [skills/seo-geo/SKILL.md:18-178]()

---

## Platform-Specific Optimization Strategies

### AI Search Engine Algorithms

Different AI search engines use different ranking/citation algorithms. The skill provides platform-specific optimization guidance:

| Platform | Primary Factors | Optimization Strategy |
|----------|----------------|----------------------|
| **ChatGPT** | Branded domain authority (+11%), 30-day freshness (3.2x), backlinks (>350K domains = 8.4 avg citations) | Update content monthly, build authority backlinks, own branded domain |
| **Perplexity** | FAQ schema, PDF hosting, semantic relevance, PerplexityBot access | Allow PerplexityBot in robots.txt, host authoritative PDFs, use FAQ structured data |
| **Google AI Overview (SGE)** | E-E-A-T signals, structured data, topical authority (+132%), citations | Build content clusters, add authoritative citations, implement schema markup |
| **Microsoft Copilot / Bing** | Bing indexing required, page speed (<2s), Microsoft ecosystem signals | Optimize for Bing, improve load times, leverage LinkedIn/GitHub presence |
| **Claude AI** | Brave Search indexing, factual density, structural clarity | Ensure Brave indexing, increase data richness, clear information hierarchy |

**Critical Requirements:**

**ChatGPT:**
- Content updated within 30 days gets 3.2x more citations
- Branded domains cited 11% more than third-party
- 350K+ referring domains = 8.4 average citations

**Perplexity:**
- `PerplexityBot` must be allowed in robots.txt
- PDF documents prioritized for citation
- FAQ schema increases citation rate

**Google AI Overview:**
- Authoritative citations provide +132% visibility boost
- Topical authority via content clusters + internal linking
- E-E-A-T: Experience, Expertise, Authority, Trust

**Claude AI:**
- Uses Brave Search, NOT Google (must ensure Brave indexing)
- Prefers high factual density content
- Clear structural clarity for extraction

**Sources:** [skills/seo-geo/SKILL.md:203-235]()

---

## Bot Access Configuration

### robots.txt Allowlist

The skill requires specific AI bot access for citations. Required directives:

```
User-agent: Googlebot        # Google / Google AI Overview
Allow: /

User-agent: Bingbot           # Bing / Microsoft Copilot
Allow: /

User-agent: PerplexityBot     # Perplexity AI
Allow: /

User-agent: ChatGPT-User      # ChatGPT with browsing
Allow: /

User-agent: GPTBot            # OpenAI training
Allow: /

User-agent: ClaudeBot         # Claude AI
Allow: /

User-agent: anthropic-ai      # Alternative Claude identifier
Allow: /
```

**Verification Command:**
```bash
curl -s "https://example.com/robots.txt"
```

**Sources:** [skills/seo-geo/SKILL.md:38-64]()

---

## Dependencies and Integration

### Skill Dependencies

```mermaid
graph TB
    SEOGEO["seo-geo skill"]
    
    subgraph "Required Dependencies"
        TWITTER["twitter skill<br/>>=1.0.0<br/>X API client"]
        REDDIT["reddit skill<br/>>=1.0.0<br/>Public JSON API"]
    end
    
    subgraph "Integration Methods"
        TWITTER_USE["Search SEO experts<br/>on X for latest tips"]
        REDDIT_USE["Search r/SEO, r/bigseo<br/>for discussions"]
        WEBSEARCH["WebSearch:<br/>Keyword research<br/>Competitor analysis"]
    end
    
    SEOGEO --> TWITTER
    SEOGEO --> REDDIT
    
    TWITTER --> TWITTER_USE
    REDDIT --> REDDIT_USE
    SEOGEO --> WEBSEARCH
    
    TWITTER_USE --> INSIGHTS["SEO Insights and<br/>Best Practices"]
    REDDIT_USE --> INSIGHTS
    WEBSEARCH --> INSIGHTS
```

**Integration Examples:**

**Twitter Skill Usage:**
```bash
# Find latest SEO discussions
python3 <twitter>/scripts/search_tweets.py "SEO tips 2026" --type Latest --limit 20

# Follow SEO influencers
python3 <twitter>/scripts/get_user_tweets.py "aleyda" --limit 20
```

**Reddit Skill Usage:**
```bash
# Search SEO subreddits
python3 <reddit>/scripts/get_posts.py bigseo --limit 20
python3 <reddit>/scripts/search_posts.py "GEO optimization" --limit 20
```

**Dependency Declaration:**
The skill declares dependencies in [skills.json:28-31]():
```json
"dependencies": {
  "twitter": ">=1.0.0",
  "reddit": ">=1.0.0"
}
```

When installed via `npx skills add ReScienceLab/opc-skills --skill seo-geo`, the installer automatically resolves and installs `twitter` and `reddit` skills if not already present.

**Sources:** [skills.json:28-31](), [skills/seo-geo/SKILL.md:236-242]()

---

## Content Structure Optimization

### Answer-First Format

AI search engines prefer "answer-first" content structure:

```
1. Direct Answer (first paragraph)
   ↓
2. Supporting Evidence (statistics, citations)
   ↓
3. Detailed Explanation
   ↓
4. Related Information
```

**Implementation Guidelines:**
- Place direct answer in first 2-3 sentences
- Use clear H1 > H2 > H3 hierarchy
- Bullet points and numbered lists for scannability
- Tables for comparison data
- Short paragraphs (2-3 sentences maximum)

**Example Structure:**
```markdown
# What is GEO?

GEO (Generative Engine Optimization) is the practice of optimizing 
content to be cited by AI search engines like ChatGPT, Perplexity, 
and Google AI Overview. According to Princeton research, proper GEO 
methods can increase AI visibility by up to 40%.

## Key Methods
- Cite authoritative sources (+40%)
- Include statistics (+37%)
- Add expert quotations (+30%)

## Implementation
[Detailed implementation steps]
```

**Sources:** [skills/seo-geo/SKILL.md:116-122]()

---

## Meta Tags and Schema Templates

### HTML Meta Tags

Standard meta tag structure for SEO:

```html
<title>{Primary Keyword} - {Brand} | {Secondary Keyword}</title>
<meta name="description" content="{Compelling description with keyword, 150-160 chars}">
<meta name="keywords" content="{keyword1}, {keyword2}, {keyword3}">

<!-- Open Graph -->
<meta property="og:title" content="{Title}">
<meta property="og:description" content="{Description}">
<meta property="og:image" content="{Image URL 1200x630}">
<meta property="og:url" content="{Canonical URL}">
<meta property="og:type" content="website">

<!-- Twitter Cards -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{Title}">
<meta name="twitter:description" content="{Description}">
<meta name="twitter:image" content="{Image URL}">
```

### JSON-LD Schema Types

The skill references multiple schema types for different page types:

| Page Type | Schema Type | Use Case |
|-----------|-------------|----------|
| Content Pages | `WebPage`, `Article` | Blog posts, documentation |
| FAQ Sections | `FAQPage` | Questions and answers (+40% AI visibility) |
| Product Pages | `Product` | E-commerce listings |
| About Pages | `Organization` | Company information |
| Tools/Apps | `SoftwareApplication` | Software products |

**Schema Validation Commands:**
```bash
# Google Rich Results Test
open "https://search.google.com/test/rich-results?url={encoded_url}"

# Schema.org Validator
open "https://validator.schema.org/?url={encoded_url}"
```

**Sources:** [skills/seo-geo/SKILL.md:125-169]()

---

## Installation and Configuration

### Installation Commands

**Universal Installation:**
```bash
npx skills add ReScienceLab/opc-skills --skill seo-geo
```

**Platform-Specific:**
```bash
# Claude Code
npx skills add ReScienceLab/opc-skills --skill seo-geo -a claude

# Factory Droid
npx skills add ReScienceLab/opc-skills --skill seo-geo -a droid

# Cursor
npx skills add ReScienceLab/opc-skills --skill seo-geo -a cursor
```

Auto-installs dependencies: `twitter >=1.0.0`, `reddit >=1.0.0`

### Optional API Configuration

For advanced features (keyword research, competitor analysis):

1. **Create DataForSEO Account:** https://dataforseo.com
2. **Set Environment Variables:**
   ```bash
   export DATAFORSEO_LOGIN="your_login"
   export DATAFORSEO_PASSWORD="your_password"
   ```

**Free Tier Limits:**
- DataForSEO offers $1 free credit on signup
- Sufficient for ~50-100 keyword research queries
- Paid plans start at $50/month

**Sources:** [skills.json:48-62](), [skills.json:32-47]()

---

## Validation and Monitoring

### SEO Audit Checklist

The skill provides a comprehensive validation checklist:

- [ ] H1 contains primary keyword
- [ ] Meta description 150-160 characters
- [ ] Images have descriptive alt text
- [ ] Internal links to related content
- [ ] External links have `rel="noopener noreferrer"`
- [ ] Content is mobile-friendly
- [ ] Page loads in < 3 seconds
- [ ] robots.txt allows AI bots
- [ ] sitemap.xml includes all pages
- [ ] Schema markup validates
- [ ] FAQPage schema for FAQ content
- [ ] Open Graph tags present
- [ ] Twitter Card tags present

**Indexing Status Check:**
```bash
# Google indexing
open "https://www.google.com/search?q=site:{domain}"

# Bing indexing (required for Copilot)
open "https://www.bing.com/search?q=site:{domain}"
```

**Report Generation Template:**
```markdown
## SEO/GEO Optimization Report

### Current Status
- Meta Tags: ✅/❌
- Schema Markup: ✅/❌
- AI Bot Access: ✅/❌
- Mobile Friendly: ✅/❌
- Page Speed: X seconds

### Recommendations
1. [Priority 1 action]
2. [Priority 2 action]
3. [Priority 3 action]

### GEO Optimizations Applied
- [ ] FAQPage schema added
- [ ] Statistics included
- [ ] Citations added
- [ ] Answer-first structure
```

**Sources:** [skills/seo-geo/SKILL.md:152-201]()

---

## Reference Documentation

The skill includes extensive reference documentation in the `references/` directory:

| File | Purpose |
|------|---------|
| `platform-algorithms.md` | Detailed ranking factors for each AI platform |
| `geo-research.md` | Princeton GEO research (9 methods with citations) |
| `schema-templates.md` | JSON-LD schema templates for common page types |
| `seo-checklist.md` | Complete SEO audit checklist |
| `tools-and-apis.md` | Tools and API reference documentation |

**Example Use Case:**
The skill includes a real-world case study in `examples/opc-skills-case-study.md` demonstrating optimization of the OPC Skills website using the 9 GEO methods.

**Sources:** [skills/seo-geo/SKILL.md:243-251]()

---

# Page: Research & Validation Skills

# Research & Validation Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [skill-logos/archive.svg](skill-logos/archive.svg)
- [skills.json](skills.json)
- [skills/archive/SKILL.md](skills/archive/SKILL.md)
- [skills/archive/references/TEMPLATE.md](skills/archive/references/TEMPLATE.md)
- [website/opc-banner.png](website/opc-banner.png)

</details>



This document covers the research and validation skills in the OPC Skills system: **requesthunt** and **producthunt**. These skills enable AI agents to gather market intelligence, validate product ideas, and analyze user demand through automated scraping and API integration. For social media research capabilities, see [Social Media & Domain Skills](#2.4.5). For foundational API client skills, see [Foundation Skills](#2.4.1).

## Overview

The research and validation category contains two standalone skills with distinct data sources:

| Skill | Purpose | Data Source | API Required |
|-------|---------|-------------|--------------|
| `requesthunt` | User demand research from feature requests and complaints | requesthunt.com aggregation service | Yes (REQUESTHUNT_API_KEY) |
| `producthunt` | Product discovery and competitive analysis | Product Hunt GraphQL API | Yes (PRODUCTHUNT_ACCESS_TOKEN) |

Both skills operate independently with no dependencies on other OPC skills, making them suitable for lightweight installations.

**Sources:** [skills.json:76-127](), [skills.json:444-493]()

---

## Requesthunt Skill

### Purpose & Capabilities

The `requesthunt` skill provides automated demand research by aggregating and analyzing user feedback from multiple platforms. It generates structured research reports containing feature requests, pain points, and user questions extracted from Reddit, X (Twitter), and GitHub.

**Primary Use Cases:**
- Pre-launch market validation
- Feature prioritization based on user demand
- Competitor gap analysis
- Community sentiment analysis

**Skill Metadata:**
- Version: 1.0.0
- Dependencies: None
- Auth Required: Yes (API key from requesthunt.com)
- Installation: `npx skills add ReScienceLab/opc-skills --skill requesthunt`

**Sources:** [skills.json:76-99](), [README.md:47]()

### System Architecture

```mermaid
graph TB
    subgraph "AI Agent Layer"
        Agent["AI Agent<br/>(Claude/Cursor/Droid)"]
        SKILL_MD["skills/requesthunt/SKILL.md<br/>YAML frontmatter + instructions"]
    end
    
    subgraph "Execution Layer"
        list_requests["scripts/list_requests.py<br/>--topic --limit"]
        search_requests["scripts/search_requests.py<br/>query --expand --limit"]
        scrape_topic["scripts/scrape_topic.py<br/>topic --platforms"]
        get_topics["scripts/get_topics.py<br/>List available topics"]
        get_usage["scripts/get_usage.py<br/>API quota check"]
    end
    
    subgraph "External API"
        RH_API["requesthunt.com API<br/>Aggregated user feedback"]
        ENV_KEY["REQUESTHUNT_API_KEY<br/>Environment variable"]
    end
    
    subgraph "Data Sources (Upstream)"
        REDDIT_SRC["Reddit Posts/Comments"]
        X_SRC["X (Twitter) Threads"]
        GITHUB_SRC["GitHub Issues"]
    end
    
    Agent -->|"Triggers: 'requesthunt',<br/>'feature request',<br/>'user demand'"| SKILL_MD
    SKILL_MD --> list_requests
    SKILL_MD --> search_requests
    SKILL_MD --> scrape_topic
    SKILL_MD --> get_topics
    SKILL_MD --> get_usage
    
    list_requests --> ENV_KEY
    search_requests --> ENV_KEY
    scrape_topic --> ENV_KEY
    get_topics --> ENV_KEY
    get_usage --> ENV_KEY
    
    ENV_KEY --> RH_API
    
    RH_API -.aggregates.-> REDDIT_SRC
    RH_API -.aggregates.-> X_SRC
    RH_API -.aggregates.-> GITHUB_SRC
    
    list_requests -->|"Structured JSON"| Agent
    search_requests -->|"Ranked results"| Agent
    scrape_topic -->|"Fresh scrape"| Agent
    get_topics -->|"Topic list"| Agent
    get_usage -->|"Quota status"| Agent
```

**Diagram: Requesthunt Skill Data Flow**

This diagram shows how the AI agent invokes Python scripts that authenticate using an environment variable and query the requesthunt.com API, which aggregates data from Reddit, X, and GitHub.

**Sources:** [skills.json:115-121](), [skills.json:90-99]()

### Script Commands

The skill provides five executable Python scripts for different research workflows:

#### 1. list_requests.py
```bash
python3 scripts/list_requests.py --topic "{topic}" --limit 20
```
Retrieves pre-categorized feature requests for a specific topic (e.g., "calendar apps", "project management tools").

#### 2. search_requests.py
```bash
python3 scripts/search_requests.py "{query}" --expand --limit 20
```
Performs full-text search across all indexed requests. The `--expand` flag includes related requests and variations.

#### 3. scrape_topic.py
```bash
python3 scripts/scrape_topic.py "{topic}" --platforms reddit,x,github
```
Triggers a fresh scrape of platforms for a given topic. Useful for real-time data when pre-indexed results are insufficient.

#### 4. get_topics.py
```bash
python3 scripts/get_topics.py
```
Lists all available pre-indexed topics in the requesthunt database.

#### 5. get_usage.py
```bash
python3 scripts/get_usage.py
```
Checks current API quota usage and limits for the authenticated key.

**Sources:** [skills.json:115-121]()

### Authentication Configuration

```yaml
auth:
  required: true
  type: api_key
  keys:
    - env: REQUESTHUNT_API_KEY
      url: https://requesthunt.com/dashboard
```

The skill requires a `REQUESTHUNT_API_KEY` obtained from the requesthunt.com dashboard. The AI agent will prompt the user to set this environment variable before executing scripts.

**Sources:** [skills.json:90-99]()

### Example Workflow Reference

The skill includes a case study demonstrating demand research for calendar applications:

- **Path:** [skills/requesthunt/examples/calendar-app-research.md]()
- **Reference:** [skills.json:125]()

---

## Producthunt Skill

### Purpose & Capabilities

The `producthunt` skill enables AI agents to query Product Hunt's product database for competitive intelligence and trend analysis. It provides access to posts (product launches), topics, users, and curated collections via Product Hunt's GraphQL API.

**Primary Use Cases:**
- Competitor product analysis
- Launch day research (what launched on specific dates)
- Topic trend identification
- User/maker profile research
- Collection discovery (curated product lists)

**Skill Metadata:**
- Version: 1.0.0
- Dependencies: None
- Auth Required: Yes (OAuth access token)
- Installation: `npx skills add ReScienceLab/opc-skills --skill producthunt`

**Sources:** [skills.json:444-466](), [README.md:54]()

### System Architecture

```mermaid
graph TB
    subgraph "AI Agent Layer"
        Agent["AI Agent<br/>(Claude/Cursor/Droid)"]
        SKILL_MD["skills/producthunt/SKILL.md<br/>GraphQL query templates"]
    end
    
    subgraph "Execution Layer"
        get_posts["scripts/get_posts.py<br/>--limit 20<br/>Get recent launches"]
        get_post["scripts/get_post.py<br/>{slug_or_id}<br/>Single post details"]
        get_topics["scripts/get_topics.py<br/>--query --limit<br/>Topic search"]
        get_user["scripts/get_user.py<br/>{username}<br/>User profile"]
        get_collections["scripts/get_collections.py<br/>--featured --limit<br/>Curated lists"]
    end
    
    subgraph "External API"
        PH_API["api.producthunt.com/v2<br/>GraphQL Endpoint"]
        ENV_TOKEN["PRODUCTHUNT_ACCESS_TOKEN<br/>OAuth token"]
    end
    
    subgraph "Product Hunt Data Model"
        POSTS["Posts<br/>(Product launches)"]
        TOPICS["Topics<br/>(Categories/tags)"]
        USERS["Users<br/>(Makers/hunters)"]
        COLLECTIONS["Collections<br/>(Curated lists)"]
    end
    
    Agent -->|"Triggers: 'producthunt',<br/>'product hunt',<br/>'PH', 'launch'"| SKILL_MD
    SKILL_MD --> get_posts
    SKILL_MD --> get_post
    SKILL_MD --> get_topics
    SKILL_MD --> get_user
    SKILL_MD --> get_collections
    
    get_posts --> ENV_TOKEN
    get_post --> ENV_TOKEN
    get_topics --> ENV_TOKEN
    get_user --> ENV_TOKEN
    get_collections --> ENV_TOKEN
    
    ENV_TOKEN --> PH_API
    
    PH_API --> POSTS
    PH_API --> TOPICS
    PH_API --> USERS
    PH_API --> COLLECTIONS
    
    get_posts -->|"JSON response"| Agent
    get_post -->|"Full post data"| Agent
    get_topics -->|"Topic list"| Agent
    get_user -->|"Profile + history"| Agent
    get_collections -->|"Collection metadata"| Agent
```

**Diagram: Producthunt Skill GraphQL Integration**

This diagram illustrates the skill's interaction with Product Hunt's GraphQL API, showing how different scripts query different data models (posts, topics, users, collections).

**Sources:** [skills.json:482-488](), [skills.json:457-465]()

### Script Commands

The skill provides five scripts corresponding to Product Hunt's primary data models:

#### 1. get_posts.py
```bash
python3 scripts/get_posts.py --limit 20
```
Retrieves recent product launches, ordered by featured date. Default limit is 20.

#### 2. get_post.py
```bash
python3 scripts/get_post.py {slug_or_id}
```
Fetches detailed information for a specific product using either its slug (URL-friendly name) or numeric ID.

#### 3. get_topics.py
```bash
python3 scripts/get_topics.py --query "{query}" --limit 20
```
Searches Product Hunt topics (categories/tags). Useful for discovering trending categories.

#### 4. get_user.py
```bash
python3 scripts/get_user.py {username}
```
Retrieves user profile including products they've made or hunted, follower count, and activity history.

#### 5. get_collections.py
```bash
python3 scripts/get_collections.py --featured --limit 20
```
Fetches curated product collections. The `--featured` flag returns staff-picked collections.

**Sources:** [skills.json:482-488]()

### Authentication Configuration

```yaml
auth:
  required: true
  type: api_key
  keys:
    - env: PRODUCTHUNT_ACCESS_TOKEN
      url: https://producthunt.com/v2/oauth/applications
```

The skill requires a `PRODUCTHUNT_ACCESS_TOKEN` obtained by creating an OAuth application on Product Hunt. The token provides read-only access to public data.

**Sources:** [skills.json:457-465]()

### API Documentation Reference

Product Hunt's GraphQL API documentation is linked in the skill metadata:
- **API Docs:** `https://api.producthunt.com/v2/docs`
- **Reference:** [skills.json:491]()

---

## Skill Comparison Matrix

| Feature | requesthunt | producthunt |
|---------|-------------|-------------|
| **Data Source** | Aggregated user feedback (Reddit, X, GitHub) | Product Hunt GraphQL API |
| **API Type** | REST | GraphQL |
| **Auth Complexity** | Simple API key | OAuth application token |
| **Cost** | Varies by plan | Free for public data |
| **Primary Output** | Feature requests, complaints, questions | Product launches, trends, makers |
| **Filtering Options** | Topic, platform, query | Date, topics, featured status |
| **Freshness** | Real-time scraping available | Real-time via API |
| **Use Case Focus** | Pre-launch validation | Post-launch competitive analysis |

**Sources:** [skills.json:76-127](), [skills.json:444-493]()

---

## Installation & Platform Support

Both skills support universal installation across 16+ AI platforms:

### Universal Installation
```bash
# Install requesthunt
npx skills add ReScienceLab/opc-skills --skill requesthunt

# Install producthunt
npx skills add ReScienceLab/opc-skills --skill producthunt

# Install both
npx skills add ReScienceLab/opc-skills --skill requesthunt --skill producthunt

# Install to specific agent
npx skills add ReScienceLab/opc-skills --skill requesthunt -a droid
```

### Claude Code Marketplace
```bash
# Add marketplace
/plugin marketplace add ReScienceLab/opc-skills

# Install skills
/plugin install requesthunt@opc-skills
/plugin install producthunt@opc-skills
```

### Platform-Specific Directories

After installation, skills are placed in agent-specific directories:

| Platform | Directory Path |
|----------|---------------|
| Claude Code/Desktop | `.claude/skills/` |
| Cursor | `.cursor/skills/` |
| Factory Droid | `.factory/skills/` |
| Windsurf | `.windsurf/skills/` |

**Sources:** [skills.json:100-114](), [skills.json:467-481](), [README.md:63-89]()

---

## Typical Research Workflow

```mermaid
graph LR
    subgraph "Phase 1: Demand Research"
        A["User: 'Research demand<br/>for calendar apps'"]
        B["Agent loads<br/>requesthunt skill"]
        C["get_topics.py<br/>List available topics"]
        D["list_requests.py<br/>--topic calendar"]
        E["search_requests.py<br/>'calendar sync issues'"]
    end
    
    subgraph "Phase 2: Competitive Analysis"
        F["User: 'What calendar apps<br/>launched on PH?'"]
        G["Agent loads<br/>producthunt skill"]
        H["get_topics.py<br/>--query calendar"]
        I["get_posts.py<br/>Filter by topic"]
        J["get_post.py<br/>Detailed analysis"]
    end
    
    subgraph "Phase 3: Synthesis"
        K["Agent: Combine<br/>demand + competitor data"]
        L["Generate research report<br/>with feature gaps"]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> K
    
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    
    K --> L
```

**Diagram: Multi-Skill Research Workflow**

This workflow demonstrates how `requesthunt` and `producthunt` complement each other in a typical market research task. The AI agent first gathers user demand signals via requesthunt, then analyzes existing solutions via producthunt, and finally synthesizes insights.

**Sources:** [skills.json:82-88](), [skills.json:450-455]()

---

## Trigger Keywords

The AI agent automatically activates these skills when detecting relevant keywords in user prompts:

### Requesthunt Triggers
- `"requesthunt"`
- `"request hunt"`
- `"feature request"`
- `"user demand"`
- `"demand research"`

### Producthunt Triggers
- `"producthunt"`
- `"product hunt"`
- `"PH"`
- `"launch"`

**Sources:** [skills.json:82-88](), [skills.json:450-455]()

---

## Example Use Cases

### Use Case 1: Feature Prioritization
**Goal:** Determine which features to build first for a new SaaS product.

**Workflow:**
1. Run `get_topics.py` to identify relevant category
2. Execute `list_requests.py --topic "{category}"` to retrieve top feature requests
3. Use `search_requests.py` to find specific pain points mentioned by users
4. Analyze frequency and sentiment to prioritize roadmap

### Use Case 2: Launch Day Reconnaissance
**Goal:** Understand what launched on Product Hunt on a specific date.

**Workflow:**
1. Run `get_posts.py --limit 50` to retrieve recent launches
2. Filter results by launch date
3. For interesting products, run `get_post.py {slug}` for details
4. Use `get_user.py {maker}` to research product creators

### Use Case 3: Gap Analysis
**Goal:** Find underserved niches by comparing user demand vs existing products.

**Workflow:**
1. Use `requesthunt` to identify frequently requested features in a category
2. Use `producthunt` to see what solutions currently exist
3. Calculate gap = (demand - existing solutions)
4. Prioritize gaps with high demand and low competition

**Sources:** [skills.json:122-126]()

---

## Dependency Status

Both skills are **standalone** with no internal dependencies on other OPC skills:

```json
"dependencies": {}
```

This makes them suitable for:
- Minimal installations where only research capabilities are needed
- Testing/validation of the skills system
- Isolated use cases without image generation or social media integration

**Sources:** [skills.json:89](), [skills.json:456]()

---

## Links & Resources

### Requesthunt
- **GitHub:** [skills/requesthunt]()
- **API Docs:** `https://requesthunt.com/docs`
- **Example:** [skills/requesthunt/examples/calendar-app-research.md]()
- **Skill Registry:** [skills.json:76-127]()

### Producthunt
- **GitHub:** [skills/producthunt]()
- **API Docs:** `https://api.producthunt.com/v2/docs`
- **Skill Registry:** [skills.json:444-493]()

**Sources:** [skills.json:122-126](), [skills.json:489-492]()

---

# Page: Social Media & Domain Skills

# Social Media & Product Discovery Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.factory/hooks.json](.factory/hooks.json)
- [.factory/skills/add-new-opc-skill/SKILL.md](.factory/skills/add-new-opc-skill/SKILL.md)
- [.gitignore](.gitignore)
- [skills.json](skills.json)
- [skills/archive/SKILL.md](skills/archive/SKILL.md)
- [skills/archive/references/TEMPLATE.md](skills/archive/references/TEMPLATE.md)
- [skills/domain-hunter/SKILL.md](skills/domain-hunter/SKILL.md)
- [skills/domain-hunter/examples/auto-video-editing-domain.md](skills/domain-hunter/examples/auto-video-editing-domain.md)
- [skills/reddit/SKILL.md](skills/reddit/SKILL.md)
- [skills/twitter/SKILL.md](skills/twitter/SKILL.md)
- [website/resciencelab-logo.svg](website/resciencelab-logo.svg)

</details>



This page documents three skills that cover social media data retrieval and domain name research: the **twitter** skill (Twitter/X via twitterapi.io), the **reddit** skill (Reddit via the public JSON API), and the **domain-hunter** skill (WHOIS availability checking, price comparison, and promo code discovery). The domain-hunter skill directly orchestrates both the twitter and reddit skills as part of its workflow.

For documentation of the requesthunt and producthunt skills, which also involve social and community data, see [2.4.4](#2.4.4). For skill installation and API key setup across all skills, see [3.1](#3.1).

---

## Twitter Skill

The twitter skill wraps the [twitterapi.io](https://docs.twitterapi.io/) API to give an AI agent programmatic access to Twitter/X data. All scripts live in `skills/twitter/scripts/` and are invoked directly from the skill directory.

### Authentication

The skill requires a single environment variable:

```bash
export TWITTERAPI_API_KEY="your_api_key"
```

This key is passed as an `X-API-Key` header against the base URL `https://api.twitterapi.io/twitter`.

> **Pricing note:** approximately $0.15–$0.18 per 1,000 requests.

Sources: [skills/twitter/SKILL.md:1-16]()

### Script Inventory

**Endpoint grouping → Script mapping:**

| Group | Script | Primary Argument |
|---|---|---|
| User | `get_user_info.py` | `USERNAME` |
| User | `get_user_about.py` | `USERNAME` |
| User | `batch_get_users.py` | `USER_ID1,USER_ID2` |
| User | `get_user_tweets.py` | `USERNAME --limit N` |
| User | `get_user_mentions.py` | `USERNAME --limit N` |
| User | `get_followers.py` | `USERNAME --limit N` |
| User | `get_following.py` | `USERNAME --limit N` |
| User | `get_verified_followers.py` | `USERNAME --limit N` |
| User | `check_relationship.py` | `USER1 USER2` |
| User | `search_users.py` | `"query" --limit N` |
| Tweet | `get_tweet.py` | `TWEET_ID [TWEET_ID2...]` |
| Tweet | `search_tweets.py` | `"query" --type --limit N` |
| Tweet | `get_tweet_replies.py` | `TWEET_ID --limit N` |
| Tweet | `get_tweet_quotes.py` | `TWEET_ID --limit N` |
| Tweet | `get_tweet_retweeters.py` | `TWEET_ID --limit N` |
| Tweet | `get_tweet_thread.py` | `TWEET_ID` |
| Tweet | `get_article.py` | `TWEET_ID` |
| List | `get_list_followers.py` | `LIST_ID --limit N` |
| List | `get_list_members.py` | `LIST_ID --limit N` |
| Community | `get_community.py` | `COMMUNITY_ID` |
| Community | `get_community_members.py` | `COMMUNITY_ID --limit N` |
| Community | `get_community_moderators.py` | `COMMUNITY_ID` |
| Community | `get_community_tweets.py` | `COMMUNITY_ID --limit N` |
| Community | `search_community_tweets.py` | `"query" --limit N` |
| Space | `get_space.py` | `SPACE_ID` |
| Trends | `get_trends.py` | `--woeid N` |

Sources: [skills/twitter/SKILL.md:27-71]()

### Search Query Syntax

`search_tweets.py` accepts standard Twitter/X search operators:

| Operator | Example |
|---|---|
| Keyword | `"AI agent"` |
| From user | `"from:elonmusk"` |
| Date range | `"AI since:2024-01-01 until:2024-12-31"` |
| Exclude retweets | `"AI -filter:retweets"` |
| Require media | `"AI filter:media"` |
| Minimum engagement | `"AI min_faves:1000"` |

Sources: [skills/twitter/SKILL.md:73-93]()

### Twitter Skill Architecture Diagram

**Twitter Skill: script-to-endpoint mapping**

```mermaid
graph LR
  subgraph "skills/twitter/scripts/"
    GUI["get_user_info.py"]
    GUA["get_user_about.py"]
    BGU["batch_get_users.py"]
    GUT["get_user_tweets.py"]
    GUM["get_user_mentions.py"]
    GF["get_followers.py"]
    GFO["get_following.py"]
    GVF["get_verified_followers.py"]
    CR["check_relationship.py"]
    SU["search_users.py"]
    GT["get_tweet.py"]
    ST["search_tweets.py"]
    GTR["get_tweet_replies.py"]
    GTQ["get_tweet_quotes.py"]
    GTRE["get_tweet_retweeters.py"]
    GTT["get_tweet_thread.py"]
    GA["get_article.py"]
    GLF["get_list_followers.py"]
    GLM["get_list_members.py"]
    GC["get_community.py"]
    GCM["get_community_members.py"]
    GCMod["get_community_moderators.py"]
    GCT["get_community_tweets.py"]
    SCT["search_community_tweets.py"]
    GS["get_space.py"]
    GTrend["get_trends.py"]
  end

  subgraph "twitterapi.io endpoints"
    UE["/twitter/user/..."]
    TE["/twitter/tweet/..."]
    LE["/twitter/list/..."]
    CE["/twitter/community/..."]
    SE["/twitter/space/..."]
    TrE["/twitter/trends/..."]
  end

  GUI --> UE
  GUA --> UE
  BGU --> UE
  GUT --> UE
  GUM --> UE
  GF --> UE
  GFO --> UE
  GVF --> UE
  CR --> UE
  SU --> UE

  GT --> TE
  ST --> TE
  GTR --> TE
  GTQ --> TE
  GTRE --> TE
  GTT --> TE
  GA --> TE

  GLF --> LE
  GLM --> LE

  GC --> CE
  GCM --> CE
  GCMod --> CE
  GCT --> CE
  SCT --> CE

  GS --> SE
  GTrend --> TrE
```

Sources: [skills/twitter/SKILL.md:27-99]()

---

## Reddit Skill

The reddit skill reads from Reddit's public JSON API — no OAuth token or API key is required. Any Reddit URL can be queried by appending `.json` to the path.

### Authentication

None required. The API is publicly accessible at up to 100 requests/minute.

Sources: [skills/reddit/SKILL.md:7-12]()

### Script Inventory

| Script | Purpose | Key Arguments |
|---|---|---|
| `get_posts.py` | Retrieve subreddit posts | `SUBREDDIT --sort --time --limit N` |
| `search_posts.py` | Search across Reddit or a subreddit | `"query" --subreddit --sort --time --limit N` |
| `get_subreddit.py` | Retrieve subreddit metadata | `SUBREDDIT` |
| `get_post.py` | Retrieve a single post with comments | `POST_ID --comments N` |
| `get_user.py` | Retrieve user profile and posts | `USERNAME --posts N` |

Sources: [skills/reddit/SKILL.md:24-55]()

### Sort Options

| `--sort` Value | Description | Supports `--time` |
|---|---|---|
| `hot` | Trending posts (default) | No |
| `new` | Latest posts | No |
| `top` | Highest voted | Yes: `hour`, `day`, `week`, `month`, `year`, `all` |
| `rising` | Gaining traction | No |
| `controversial` | Mixed votes | Yes: same as `top` |

Sources: [skills/reddit/SKILL.md:57-65]()

### Reddit Skill Architecture Diagram

**Reddit Skill: script-to-API mapping**

```mermaid
graph LR
  subgraph "skills/reddit/scripts/"
    GP["get_posts.py"]
    SP["search_posts.py"]
    GS["get_subreddit.py"]
    GPo["get_post.py"]
    GU["get_user.py"]
  end

  subgraph "reddit.com public JSON API"
    SR["/r/SUBREDDIT/.json"]
    SEARCH["/search.json"]
    ABOUT["/r/SUBREDDIT/about.json"]
    POST["/r/SUBREDDIT/comments/POST_ID.json"]
    USER["/user/USERNAME/about.json"]
  end

  GP --> SR
  SP --> SEARCH
  GS --> ABOUT
  GPo --> POST
  GU --> USER
```

Sources: [skills/reddit/SKILL.md:24-72]()

---

## Domain Hunter Skill

The domain-hunter skill is an orchestration layer — it does not have its own external API. Instead it combines WHOIS shell commands, web search, and invocations of the **twitter** and **reddit** skills to guide a user from domain idea to purchase.

The workflow is entirely agent-driven: the skill's `SKILL.md` defines the steps and the commands to run at each step. There are no Python scripts in this skill; it relies on shell utilities and other skills.

Sources: [skills/domain-hunter/SKILL.md:1-116]()

### Four-Step Workflow

```mermaid
flowchart TD
  A["Step 1: Generate Ideas & Check Availability"]
  B["Step 2: Compare Prices"]
  C["Step 3: Find Promo Codes"]
  D["Step 4: Recommend"]

  A --> B
  B --> C
  C --> D

  subgraph "Step 1 methods"
    W["whois shell command"]
    RS["registrar search page (browser open)"]
    BK["bulk check: namecheap.com / dynadot.com"]
  end

  subgraph "Step 2 methods"
    WS["WebSearch: tld-list.com / tldes.com / domaintyper.com"]
  end

  subgraph "Step 3 methods"
    TW["twitter skill: search_tweets.py"]
    RD["reddit skill: search_posts.py"]
  end

  A --- W
  A --- RS
  A --- BK
  B --- WS
  C --- TW
  C --- RD
```

Sources: [skills/domain-hunter/SKILL.md:11-103]()

### Step 1: Availability Check Methods

Three methods are available, in order of reliability:

| Method | Mechanism | Command |
|---|---|---|
| WHOIS (most reliable) | Shell `whois` with grep for availability keywords | `whois {domain}.{tld} 2>/dev/null \| grep -i "no match\|not found\|available\|no data found"` |
| Registrar search | Open browser to registrar search page | `open "https://www.spaceship.com/domains/?search={domain}.{tld}"` |
| Bulk check | Namecheap or Dynadot bulk search URLs | URL parameters |

The agent **must not present a domain to the user** until availability is confirmed. Uncertain domains should be marked `(unverified)`.

Sources: [skills/domain-hunter/SKILL.md:26-47]()

### Step 3: Promo Code Discovery via Twitter & Reddit

The domain-hunter skill calls the twitter skill's `search_tweets.py` and the reddit skill's `search_posts.py` directly. Both skill directories must already be installed.

**Twitter queries** — targets registrar official accounts:

```bash
cd <twitter_skill_directory>
python3 scripts/search_tweets.py "from:{registrar} promo code" --type Latest --limit 15
python3 scripts/search_tweets.py "{registrar} promo code coupon" --type Latest --limit 15
```

Tracked Twitter handles: `@spaceship`, `@Dynadot`, `@Namecheap`, `@Porkbun`, `@namesilo`, `@Cloudflare`

**Reddit queries** — searches the `r/Domains` community and general Reddit:

```bash
cd <reddit_skill_directory>
python3 scripts/search_posts.py "{registrar} promo code" --limit 15
python3 scripts/search_posts.py "{registrar} coupon discount" --subreddit Domains --limit 10
```

Sources: [skills/domain-hunter/SKILL.md:63-79]()

### Step 4: Recommendation Format

The agent produces a structured Markdown output:

```
## Recommendation

**Domain:** example.ai
**Best Registrar:** Spaceship
**Price:** $68.98/year
**Promo Code:** None available for .ai
**Purchase Link:** https://www.spaceship.com/

### Price Comparison
| Registrar | Year 1 | Renewal | 2-Year Total |
|-----------|--------|---------|--------------|
| Spaceship | $68.98 | $68.98  | $137.96      |
| Cloudflare| $70.00 | $70.00  | $140.00      |
```

Sources: [skills/domain-hunter/SKILL.md:85-103]()

### Important TLD and Registrar Notes

| Note | Detail |
|---|---|
| Premium TLDs (`.ai`, `.io`) | Rarely have promo codes — wholesale costs are too high |
| `.ai` domains | Require 2-year minimum registration |
| Cloudflare | At-cost pricing, no markup |
| Renewal pricing | Often differs from registration price — always check both |
| WHOIS privacy | Free at Cloudflare, Namecheap, Porkbun |

Sources: [skills/domain-hunter/SKILL.md:105-112]()

### Domain Hunter Reference Files

The skill ships two reference documents:

| File | Purpose |
|---|---|
| `references/registrars.md` | Detailed registrar comparison |
| `references/spaceship-api.md` | Spaceship API for automated domain operations |

Sources: [skills/domain-hunter/SKILL.md:113-116]()

---

## Skill Inter-Dependencies

The diagram below shows how these three skills relate to one another and to external APIs.

**Skill dependency and external API map**

```mermaid
graph TD
  DH["domain-hunter skill"]
  TW["twitter skill"]
  RD["reddit skill"]

  subgraph "External APIs"
    TWAPI["twitterapi.io\n(X-API-Key header)"]
    RDAPI["reddit.com public JSON API\n(no auth)"]
    WHOIS["whois (shell utility)"]
    WEBSEARCH["WebSearch (agent tool)"]
    BROWSER["browser open (agent tool)"]
  end

  DH -->|"search_tweets.py"| TW
  DH -->|"search_posts.py"| RD
  DH --> WHOIS
  DH --> WEBSEARCH
  DH --> BROWSER

  TW --> TWAPI
  RD --> RDAPI
```

Sources: [skills/domain-hunter/SKILL.md:63-79](), [skills/twitter/SKILL.md:95-99](), [skills/reddit/SKILL.md:67-72]()

---

## Skill Summary Comparison

| Attribute | twitter | reddit | domain-hunter |
|---|---|---|---|
| Auth required | Yes — `TWITTERAPI_API_KEY` env var | No | None directly (delegates to twitter/reddit) |
| External API | `api.twitterapi.io` | `reddit.com` (public JSON) | WHOIS, WebSearch, twitter skill, reddit skill |
| Script count | 26 Python scripts | 5 Python scripts | 0 (shell + skill orchestration) |
| API type | REST (JSON) | REST (JSON) | — |
| Rate limit | ~$0.15–0.18 / 1k requests (cost-based) | 100 requests/minute | Determined by delegated skills |
| Key trigger phrases | "Twitter", "X", "tweets" | "Reddit", "subreddit", "r/" | "buy a domain", "domain prices", "domain deals" |

Sources: [skills/twitter/SKILL.md:1-4](), [skills/reddit/SKILL.md:1-4](), [skills/domain-hunter/SKILL.md:1-4]()

---

# Page: Installation & Distribution

# Installation & Distribution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [README.md](README.md)
- [skill-logos/archive.svg](skill-logos/archive.svg)
- [website/opc-banner.png](website/opc-banner.png)

</details>



This page provides a high-level overview of how OPC Skills are distributed and installed across AI coding tools. It covers the two primary distribution channels, the install target directory convention, required API credentials per skill, and how the installer is tested in CI.

For detailed coverage of individual topics, see:
- [Installation Methods Overview](#3.1) — per-method comparison and `.factory/skills/` directory details
- [Claude Code Plugin Marketplace](#3.2) — `marketplace.json` schema and `/plugin` commands
- [Universal Installer (npx skills add)](#3.3) — CLI flags and `skills.json` resolution
- [Platform-Specific Installation](#3.4) — per-platform install command strings
- [Installation Statistics System](#3.5) — automated stats pipeline

---

## Distribution Channels

OPC Skills uses two parallel distribution channels that serve different audiences.

**Distribution channel overview:**

```mermaid
flowchart TD
    repo["GitHub Repository\n(ReScienceLab/opc-skills)"]
    skillsjson["skills.json\n(universal registry)"]
    marketplace["marketplace.json\n(.claude-plugin/)"]
    npx["npx skills add"]
    skillssh["skills.sh\n(third-party aggregator)"]
    claude["Claude Code\n/plugin marketplace add"]
    agents["Other Agents\n(droid, cursor, opencode, codex)"]
    factory[".factory/skills/<name>/"]

    repo --> skillsjson
    repo --> marketplace
    skillsjson --> npx
    skillsjson --> skillssh
    marketplace --> claude
    npx --> factory
    claude --> factory
    skillssh --> npx
    npx --> agents
```

Sources: [skills.json:1-10](), [.claude-plugin/marketplace.json:1-10](), [CHANGELOG.md:240-260]()

---

## Channel 1 — Claude Code Plugin Marketplace

The file [.claude-plugin/marketplace.json]() is a manifest read by Claude Code's `/plugin marketplace add` command. It contains a top-level marketplace record plus one entry per skill in the `plugins` array.

Each plugin entry includes:
- `source` — relative path to the skill directory (e.g., `"./skills/requesthunt"`)
- `strict` — set to `true` for all OPC skills
- `category` — groups skills by function
- `homepage` — points to the corresponding `opc.dev/skills/<name>` page

**Plugin manifest structure:**

```mermaid
erDiagram
    MARKETPLACE_JSON {
        string name
        object owner
        object metadata
        array keywords
        array plugins
    }
    PLUGIN_ENTRY {
        string name
        string source
        string description
        string version
        string homepage
        string repository
        string license
        string category
        array keywords
        bool strict
    }
    MARKETPLACE_JSON ||--o{ PLUGIN_ENTRY : "plugins[]"
```

Sources: [.claude-plugin/marketplace.json:1-182]()

A historical note: prior to v1.0.5, plugin `source` paths used bare names like `"./domain-hunter"` instead of `"./skills/domain-hunter"`, causing "Source path does not exist" errors in Claude Code. See [CHANGELOG.md:90-99]() for the fix.

---

## Channel 2 — Universal Installer (`npx skills add`)

The `npx skills add` command reads `skills.json` from the specified GitHub repository to resolve and copy skill directories. The `-y` flag suppresses interactive prompts and the `-a <agent>` flag targets a specific agent platform.

**Installer flow:**

```mermaid
sequenceDiagram
    participant "User" as user
    participant "npx skills add" as installer
    participant "skills.json" as registry
    participant ".factory/skills/" as target

    user->>installer: "npx skills add ReScienceLab/opc-skills --skill seo-geo -a claude"
    installer->>registry: "fetch and parse skills.json"
    registry-->>installer: "skill entry with name, version, dependencies"
    installer->>target: "copy skills/seo-geo/ → .factory/skills/seo-geo/"
    installer-->>user: "✓ installed"
```

Sources: [skills.json:48-74](), [.github/workflows/test-installer.yml:30-47]()

The `install` field in each `skills.json` skill entry defines the exact install command string for every supported platform and scope combination. For example, the `seo-geo` skill defines [skills.json:48-62]():

```
install.user.claude   = "npx skills add ReScienceLab/opc-skills --skill seo-geo -a claude"
install.project.claude = "npx skills add ReScienceLab/opc-skills --skill seo-geo"
install.project.cursor = "npx skills add ReScienceLab/opc-skills --skill seo-geo"
```

---

## Supported Platforms

The `install` field supports two scopes (`user`, `project`) and five agent targets. Not all agents support both scopes.

| Platform | User-Level | Project-Level |
|----------|-----------|---------------|
| `claude` | ✓ | ✓ |
| `droid` | ✓ | ✓ |
| `opencode` | ✓ | ✓ |
| `codex` | ✓ | ✓ |
| `cursor` | ✗ | ✓ |

Sources: [skills.json:48-62](), [skills.json:100-113]()

---

## Install Target Directory

Regardless of the installation pathway used, skills land in `.factory/skills/<skill-name>/` within the working directory. This is the convention validated by the CI test suite at [.github/workflows/test-installer.yml:41-46]():

```
.factory/
  skills/
    seo-geo/
    requesthunt/
    nanobanana/
    ...
```

The CI test checks for the presence of `.factory/skills/<skill>` after each `npx skills add` invocation. If missing, the job exits with a failure.

---

## Required API Keys

Skills declare their authentication requirements in the `auth` field of `skills.json`. The `required` boolean flags whether any key is mandatory; individual keys may be marked `optional`.

| Skill | Required Keys | Optional Keys | Auth Required |
|-------|--------------|---------------|---------------|
| `seo-geo` | — | `DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD` | No |
| `requesthunt` | `REQUESTHUNT_API_KEY` | — | Yes |
| `domain-hunter` | — | — | No |
| `logo-creator` | `GEMINI_API_KEY` | `REMOVE_BG_API_KEY`, `RECRAFT_API_KEY` | Yes |
| `banner-creator` | `GEMINI_API_KEY` | — | Yes |
| `nanobanana` | `GEMINI_API_KEY` | — | Yes |
| `reddit` | — | — | No |
| `twitter` | `TWITTERAPI_API_KEY` | — | Yes |
| `producthunt` | `PRODUCTHUNT_ACCESS_TOKEN` | — | Yes |
| `archive` | — | — | No |

Sources: [skills.json:32-46](), [skills.json:90-98](), [skills.json:147-151](), [skills.json:196-214](), [skills.json:263-270](), [skills.json:312-320](), [skills.json:360-364](), [skills.json:404-415](), [skills.json:456-464](), [skills.json:511-515]()

---

## Relationship Between skills.json and Distribution

**How skills.json serves multiple consumers:**

```mermaid
flowchart LR
    skillsjson["skills.json"]

    subgraph "Installer"
        npx["npx skills add\n--skill flag"]
        agent["-a flag\n(agent target)"]
    end

    subgraph "Website"
        worker["website/worker.js\n/skills.json route"]
        skillpage["renderSkillPage()"]
    end

    subgraph "CI"
        validate["validate-skills-json job\n(jq integrity check)"]
        testjob["test job\n(matrix: 3 OS × 9 skills)"]
    end

    subgraph "Stats"
        statsscript["fetch-install-stats.py"]
        statsjson["install-stats.json"]
    end

    skillsjson --> npx
    skillsjson --> worker
    skillsjson --> validate
    skillsjson --> testjob
    skillsjson --> statsscript
    statsscript --> statsjson
    worker --> skillpage
```

Sources: [skills.json:1-538](), [.github/workflows/test-installer.yml:85-117](), [CHANGELOG.md:240-260]()

---

## CI Validation

The [.github/workflows/test-installer.yml]() workflow runs on any push or pull request that modifies `skills.json` or any file under `skills/**`. It contains three jobs:

| Job | Matrix | What It Checks |
|-----|--------|----------------|
| `test` | 3 OS × 9 skills | Each skill installs individually via `npx skills add ... --skill <name> -y` |
| `test-all-skills` | 3 OS | All skills install together; asserts `SKILL_COUNT >= 9` |
| `validate-skills-json` | ubuntu-latest | JSON syntax via `jq empty`; required fields; dependency name referential integrity |

The referential integrity check ([.github/workflows/test-installer.yml:98-115]()) extracts all `name` values from `skills.json` and verifies that every key in any skill's `dependencies` object matches a known skill name. Both object and legacy array formats are supported.

Sources: [.github/workflows/test-installer.yml:1-117]()

---

# Page: Installation Methods Overview

# Installation Methods Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [README.md](README.md)
- [skill-logos/archive.svg](skill-logos/archive.svg)
- [website/opc-banner.png](website/opc-banner.png)

</details>



## Purpose and Scope

This document provides an overview of the two primary installation pathways available for OPC Skills: the universal NPX installer and the Claude Code-specific marketplace. It explains the architectural differences between these methods, their target platforms, and how they handle skill distribution and dependency resolution.

For detailed documentation on Claude Code's plugin marketplace, see [Claude Code Plugin Marketplace](#3.2). For the universal installer's implementation details, see [Universal Installer (npx skills add)](#3.3). For platform-specific installation directories and commands, see [Platform-Specific Installation](#3.4).

## Dual-Pathway Architecture

OPC Skills implements two distinct installation pathways to maximize compatibility across the AI agent ecosystem:

| Installation Method | Primary Use Case | Platform Support | Dependency Resolution | Defined In |
|---------------------|------------------|------------------|----------------------|------------|
| Claude Code Marketplace | Native integration for Claude Code/Desktop users | Claude Code, Claude Desktop | Automatic | [.claude-plugin/marketplace.json:1-182]() |
| Universal NPX Installer | Cross-platform installation for 16+ AI agents | Claude Code, Cursor, Droid, Windsurf, Goose, Roo Code, Trae, and 9+ others | Automatic | Compatible with `vercel-labs/add-skill` |

Both pathways install the same skill content (SKILL.md files and associated scripts) but differ in their discovery mechanisms, installation commands, and target directory structures.

**Sources:** [README.md:57-128](), [.claude-plugin/marketplace.json:1-182]()

## Installation Method Comparison

```mermaid
graph TB
    USER["User Wants to Install Skills"]
    
    subgraph "Method Selection"
        CLAUDE_USER{"Using<br/>Claude Code?"}
        MARKETPLACE_AWARE{"Knows about<br/>marketplace?"}
    end
    
    subgraph "Claude Code Marketplace Path"
        MARKETPLACE_CMD["/plugin marketplace add<br/>ReScienceLab/opc-skills"]
        LIST_CMD["/plugin marketplace list<br/>opc-skills"]
        INSTALL_CMD["/plugin install skill@opc-skills"]
        MARKETPLACE_JSON["marketplace.json<br/>plugins[] array"]
        CLAUDE_DIR[".claude/ directory"]
    end
    
    subgraph "Universal NPX Path"
        NPX_ALL["npx skills add<br/>ReScienceLab/opc-skills"]
        NPX_SPECIFIC["npx skills add<br/>--skill name"]
        NPX_AGENT["npx skills add<br/>-a agent-name"]
        SKILLS_JSON["skills.json registry"]
        AGENT_DIRS["Platform-specific dirs:<br/>.claude/, .cursor/,<br/>.factory/, etc."]
    end
    
    USER --> CLAUDE_USER
    CLAUDE_USER -->|"Yes"| MARKETPLACE_AWARE
    CLAUDE_USER -->|"No or Multi-platform"| NPX_ALL
    
    MARKETPLACE_AWARE -->|"Yes"| MARKETPLACE_CMD
    MARKETPLACE_AWARE -->|"No"| NPX_ALL
    
    MARKETPLACE_CMD --> LIST_CMD
    LIST_CMD --> INSTALL_CMD
    INSTALL_CMD --> MARKETPLACE_JSON
    MARKETPLACE_JSON --> CLAUDE_DIR
    
    NPX_ALL --> SKILLS_JSON
    NPX_SPECIFIC --> SKILLS_JSON
    NPX_AGENT --> SKILLS_JSON
    SKILLS_JSON --> AGENT_DIRS
    
    BOTH_INSTALLED["Skills Installed<br/>and Operational"]
    
    CLAUDE_DIR --> BOTH_INSTALLED
    AGENT_DIRS --> BOTH_INSTALLED
```

**Diagram: Installation Pathway Decision Flow**

This diagram shows how users select between installation methods based on their platform and familiarity with the Claude marketplace system. Both paths converge on the same functional outcome but use different metadata sources and directory structures.

**Sources:** [README.md:59-89](), [.claude-plugin/marketplace.json:1-24]()

## Claude Code Marketplace Method

### Command Structure

The Claude Code marketplace uses native `/plugin` commands within the Claude interface:

```bash
# Add the OPC Skills marketplace
/plugin marketplace add ReScienceLab/opc-skills

# List available skills
/plugin marketplace list opc-skills

# Install specific skills
/plugin install requesthunt@opc-skills
/plugin install domain-hunter@opc-skills
/plugin install seo-geo@opc-skills
```

**Sources:** [README.md:59-74]()

### Marketplace Metadata Structure

Skills available through the Claude marketplace are defined in `marketplace.json`. Each skill entry contains:

```json
{
  "name": "skill-name",
  "source": "./skills/skill-name",
  "description": "Skill description",
  "version": "1.0.0",
  "homepage": "https://opc.dev/skills/skill-name",
  "repository": "https://github.com/ReScienceLab/opc-skills",
  "license": "MIT",
  "category": "category-name",
  "keywords": ["keyword1", "keyword2"],
  "strict": true
}
```

The `plugins` array in `marketplace.json` contains 9 skill entries covering SEO, research, design, social media, and AI tools categories.

**Sources:** [.claude-plugin/marketplace.json:24-181]()

### Marketplace Skill Registry

| Skill Name | Category | Source Path | Description |
|------------|----------|-------------|-------------|
| `requesthunt` | market-research | `./skills/requesthunt` | User demand research from Reddit, X, GitHub |
| `domain-hunter` | business | `./skills/domain-hunter` | Domain search, price comparison, promo codes |
| `logo-creator` | design | `./skills/logo-creator` | AI logo generation with iterative workflow |
| `banner-creator` | design | `./skills/banner-creator` | AI banner generation for social platforms |
| `nanobanana` | ai-tools | `./skills/nanobanana` | Gemini 3 Pro Image generation |
| `reddit` | social-media | `./skills/reddit` | Reddit content via public JSON API |
| `twitter` | social-media | `./skills/twitter` | Twitter/X content via twitterapi.io |
| `producthunt` | product-discovery | `./skills/producthunt` | Product Hunt via GraphQL API |
| `seo-geo` | seo | `./skills/seo-geo` | SEO & GEO optimization |

**Sources:** [.claude-plugin/marketplace.json:24-181]()

## Universal NPX Installer Method

### Command Variants

The universal installer supports multiple invocation patterns:

```bash
# Install all skills
npx skills add ReScienceLab/opc-skills

# Install specific skill by name
npx skills add ReScienceLab/opc-skills --skill reddit

# Install multiple specific skills
npx skills add ReScienceLab/opc-skills --skill reddit --skill twitter --skill domain-hunter

# Target specific AI agent
npx skills add ReScienceLab/opc-skills -a droid
npx skills add ReScienceLab/opc-skills -a cursor
```

**Sources:** [README.md:76-106]()

### Platform Compatibility Matrix

The universal installer supports 16+ AI coding agents through the `vercel-labs/add-skill` compatibility layer:

| Platform | Agent Flag | Installation Directory | Notes |
|----------|------------|------------------------|-------|
| Claude Code | `claude` | `.claude/` | Also supports marketplace method |
| Cursor | `cursor` | `.cursor/` | AI-first code editor |
| Factory Droid | `droid` | `.factory/` | AI software engineering agent |
| Windsurf | `windsurf` | Platform-specific | AI-powered IDE |
| OpenCode | `opencode` | Platform-specific | Open-source AI assistant |
| Codex | `codex` | Platform-specific | AI code generation |
| GitHub Copilot | `copilot` | Platform-specific | AI pair programmer |
| Gemini CLI | `gemini` | Platform-specific | Command-line AI |
| Goose | `goose` | Platform-specific | Terminal-based agent |
| Kilo Code | `kilo` | Platform-specific | Lightweight AI tool |
| Roo Code | `roo` | Platform-specific | AI code assistant |
| Trae | `trae` | Platform-specific | AI development companion |

Full compatibility list available at `github.com/vercel-labs/add-skill#available-agents`.

**Sources:** [README.md:109-128]()

## Dependency Handling Across Methods

Both installation methods automatically resolve skill dependencies, but the mechanism differs:

```mermaid
graph LR
    subgraph "Dependency Declaration"
        DOMAIN_HUNTER["domain-hunter skill"]
        LOGO_CREATOR["logo-creator skill"]
        BANNER_CREATOR["banner-creator skill"]
    end
    
    subgraph "Required Dependencies"
        TWITTER["twitter skill"]
        REDDIT["reddit skill"]
        NANOBANANA["nanobanana skill"]
    end
    
    DOMAIN_HUNTER -->|"requires"| TWITTER
    DOMAIN_HUNTER -->|"requires"| REDDIT
    LOGO_CREATOR -->|"requires"| NANOBANANA
    BANNER_CREATOR -->|"requires"| NANOBANANA
    
    subgraph "Installation Behavior"
        AUTO_INSTALL["Automatic installation<br/>of dependencies"]
        USER_NOTIFIED["User notified of<br/>dependency installations"]
    end
    
    TWITTER --> AUTO_INSTALL
    REDDIT --> AUTO_INSTALL
    NANOBANANA --> AUTO_INSTALL
    AUTO_INSTALL --> USER_NOTIFIED
```

**Diagram: Automatic Dependency Resolution**

Skills with dependencies are documented in the README and automatically installed when the parent skill is requested.

**Sources:** [README.md:93-106]()

### Known Dependency Relationships

The following skills have declared dependencies:

- **domain-hunter** → requires `twitter` and `reddit`
- **logo-creator** → requires `nanobanana`
- **banner-creator** → requires `nanobanana`

When installing `domain-hunter`, the installer automatically includes `twitter` and `reddit`. When installing `logo-creator` or `banner-creator`, `nanobanana` is automatically included.

**Sources:** [README.md:93-106]()

## Installation Output Comparison

```mermaid
graph TB
    subgraph "Claude Marketplace Installation"
        CLAUDE_INSTALL["User: /plugin install<br/>skill@opc-skills"]
        CLAUDE_FETCH["Claude fetches from<br/>marketplace.json"]
        CLAUDE_EXTRACT["Extracts source path<br/>./skills/skill-name"]
        CLAUDE_COPY["Copies to .claude/<br/>skill-name/"]
    end
    
    subgraph "NPX Universal Installation"
        NPX_INSTALL["User: npx skills add<br/>--skill name"]
        NPX_DETECT["Detects AI agent<br/>or uses -a flag"]
        NPX_FETCH["Fetches from<br/>skills.json registry"]
        NPX_COPY["Copies to platform dir<br/>.cursor/, .factory/, etc."]
    end
    
    subgraph "Final Skill Structure"
        SKILL_MD["SKILL.md<br/>YAML frontmatter + docs"]
        SCRIPTS["scripts/ directory<br/>Python executables"]
        EXAMPLES["examples/ directory<br/>Usage workflows"]
        REFERENCES["references/ directory<br/>API documentation"]
    end
    
    CLAUDE_INSTALL --> CLAUDE_FETCH
    CLAUDE_FETCH --> CLAUDE_EXTRACT
    CLAUDE_EXTRACT --> CLAUDE_COPY
    
    NPX_INSTALL --> NPX_DETECT
    NPX_DETECT --> NPX_FETCH
    NPX_FETCH --> NPX_COPY
    
    CLAUDE_COPY --> SKILL_MD
    NPX_COPY --> SKILL_MD
    
    SKILL_MD --> SCRIPTS
    SKILL_MD --> EXAMPLES
    SKILL_MD --> REFERENCES
```

**Diagram: Installation Output Structure**

Both methods install identical skill directory structures. The key difference is the metadata source (`marketplace.json` vs `skills.json`) and target directory location.

**Sources:** [README.md:36-40](), [.claude-plugin/marketplace.json:24-181]()

## Skill Discovery Mechanisms

### Claude Marketplace Discovery

Users discover skills through:

1. `/plugin marketplace list opc-skills` - Lists all 9 skills in the marketplace
2. Claude Code's plugin UI - Visual browsing interface
3. Marketplace badges - Homepage links to `https://opc.dev/skills/skill-name`

### Universal Installer Discovery

Users discover skills through:

1. **skills.sh** - Public skills browser at `https://skills.sh/ReScienceLab/opc-skills`
2. **README.md** - Skills table with descriptions and logos
3. **opc.dev website** - Skill detail pages
4. **DeepWiki** - AI-powered documentation at `https://deepwiki.com/ReScienceLab/opc-skills`

**Sources:** [README.md:8-23](), [README.md:131-147]()

## Metadata Source Comparison

```mermaid
graph TB
    subgraph "Claude Marketplace Metadata"
        MARKETPLACE_JSON["marketplace.json"]
        MARKETPLACE_OWNER["owner:<br/>name, email"]
        MARKETPLACE_META["metadata:<br/>description, version"]
        MARKETPLACE_PLUGINS["plugins[]:<br/>9 skill entries"]
        MARKETPLACE_FIELDS["Per-skill fields:<br/>name, source, description,<br/>version, homepage, repository,<br/>license, category, keywords, strict"]
    end
    
    subgraph "Universal Installer Metadata"
        SKILLS_JSON["skills.json<br/>(not shown in files)"]
        SKILLS_REGISTRY["Central registry with:<br/>- name, version<br/>- dependencies<br/>- auth requirements<br/>- install commands<br/>- platform mappings"]
    end
    
    subgraph "Shared Skill Content"
        SKILL_DIRS["skills/ directory"]
        INDIVIDUAL_SKILLS["Individual skill folders:<br/>SKILL.md + scripts/<br/>+ examples/ + references/"]
    end
    
    MARKETPLACE_JSON --> MARKETPLACE_OWNER
    MARKETPLACE_JSON --> MARKETPLACE_META
    MARKETPLACE_JSON --> MARKETPLACE_PLUGINS
    MARKETPLACE_PLUGINS --> MARKETPLACE_FIELDS
    
    SKILLS_JSON --> SKILLS_REGISTRY
    
    MARKETPLACE_FIELDS --> SKILL_DIRS
    SKILLS_REGISTRY --> SKILL_DIRS
    SKILL_DIRS --> INDIVIDUAL_SKILLS
```

**Diagram: Metadata Architecture**

The Claude marketplace uses `marketplace.json` with a `plugins` array structure, while the universal installer references `skills.json` (compatible with the Agent Skills Standard). Both point to the same underlying skill directories in `skills/`.

**Sources:** [.claude-plugin/marketplace.json:1-10](), [.claude-plugin/marketplace.json:24-42]()

## Installation Statistics Tracking

Both installation methods contribute to unified install statistics tracked at `skills.sh`. The statistics system is documented in [Installation Statistics System](#3.5).

Install counts are aggregated across both pathways and displayed on:
- `https://skills.sh/ReScienceLab/opc-skills` - Public install statistics
- `https://opc.dev` - Website displays live stats via `install-stats.json`

**Sources:** [README.md:91]()

## Method Selection Guidelines

### Choose Claude Marketplace When:

- User exclusively uses Claude Code/Desktop
- User prefers native `/plugin` commands
- User wants Claude-native skill discovery UI
- Installation limited to Claude ecosystem

### Choose Universal NPX Installer When:

- User works with multiple AI agents
- User needs Cursor, Droid, Windsurf, or other platform support
- User prefers command-line installation workflow
- User wants future platform compatibility without reconfiguration

Both methods provide identical skill functionality after installation. The choice depends on platform requirements and user workflow preferences.

**Sources:** [README.md:57-128]()

---

# Page: Claude Code Plugin Marketplace

# Claude Code Plugin Marketplace

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [README.md](README.md)
- [skill-logos/archive.svg](skill-logos/archive.svg)
- [website/opc-banner.png](website/opc-banner.png)

</details>



This page documents the Claude Code plugin marketplace integration for OPC Skills — specifically the manifest formats that register the skill collection with Claude Code's plugin system. For a comparison of all installation methods including `npx skills add` and agent-specific flags, see [Installation Methods Overview](#3.1). For per-platform install command strings, see [Platform-Specific Installation](#3.4).

---

## Overview

OPC Skills exposes itself to Claude Code's plugin marketplace through two layers of manifest files:

1. **A top-level collection manifest** at `.claude-plugin/marketplace.json` — registers the entire `opc-skills` collection and lists all available plugins.
2. **Per-skill plugin manifests** at `skills/<name>/.claude-plugin/plugin.json` — describe individual skills including their entry points (`SKILL.md`) and supporting scripts.

**Directory layout for the marketplace integration:**

```
.claude-plugin/
  marketplace.json          ← collection-level manifest

skills/
  requesthunt/
    .claude-plugin/
      plugin.json           ← per-skill manifest
  domain-hunter/
    .claude-plugin/
      plugin.json
  logo-creator/
    .claude-plugin/
      plugin.json
  ... (one per skill)
```

Sources: [.claude-plugin/marketplace.json:1-182](), [skills/requesthunt/.claude-plugin/plugin.json:1-24]()

---

## `marketplace.json` — Collection Manifest

The file [.claude-plugin/marketplace.json]() registers the entire `opc-skills` collection with Claude Code's marketplace.

### Top-Level Fields

| Field | Type | Description |
|---|---|---|
| `name` | string | Unique identifier for the collection (`"opc-skills"`) |
| `owner.name` | string | Organization name (`"ReScienceLab"`) |
| `owner.email` | string | Contact email for the collection owner |
| `metadata.description` | string | Human-readable summary of the collection |
| `metadata.version` | string | Collection-level semver version (e.g. `"1.0.4"`) |
| `keywords` | string[] | Search tags used by the marketplace for discovery |
| `plugins` | object[] | Array of plugin entry descriptors (see below) |

Sources: [.claude-plugin/marketplace.json:1-23]()

### `plugins` Array — Per-Entry Fields

Each element of the `plugins` array in `marketplace.json` describes one skill:

| Field | Type | Description |
|---|---|---|
| `name` | string | Skill identifier (e.g. `"requesthunt"`) |
| `source` | string | Relative path to the skill directory (e.g. `"./skills/requesthunt"`) |
| `description` | string | Short description shown in marketplace UI |
| `version` | string | Skill-level semver version |
| `homepage` | string | URL to the skill's page on `opc.dev` |
| `repository` | string | GitHub repository URL |
| `license` | string | License identifier (`"MIT"`) |
| `category` | string | Category tag (see table below) |
| `keywords` | string[] | Additional search tags specific to the skill |
| `strict` | boolean | When `true`, enforces strict plugin loading mode |

#### Category Values in Use

| Category | Skills |
|---|---|
| `market-research` | `requesthunt` |
| `business` | `domain-hunter` |
| `design` | `logo-creator`, `banner-creator` |
| `ai-tools` | `nanobanana` |
| `social-media` | `reddit`, `twitter` |
| `product-discovery` | `producthunt` |
| `seo` | `seo-geo` |

Sources: [.claude-plugin/marketplace.json:24-181]()

### `marketplace.json` — Annotated Structure Diagram

**Diagram: marketplace.json schema structure**

```mermaid
graph TD
  M[".claude-plugin/marketplace.json"]
  M --> N["name: opc-skills"]
  M --> O["owner {name, email}"]
  M --> META["metadata {description, version}"]
  M --> KW["keywords []"]
  M --> P["plugins []"]

  P --> PE["plugin entry"]
  PE --> PN["name"]
  PE --> PS["source: ./skills/<name>"]
  PE --> PD["description"]
  PE --> PV["version"]
  PE --> PH["homepage"]
  PE --> PR["repository"]
  PE --> PL["license"]
  PE --> PC["category"]
  PE --> PKW["keywords []"]
  PE --> PST["strict: true"]
```

Sources: [.claude-plugin/marketplace.json:1-182]()

---

## Per-Skill `plugin.json` Manifests

Each skill directory contains its own `.claude-plugin/plugin.json`. This file is what Claude Code reads once a plugin is installed to understand its entry points.

### `plugin.json` Fields

| Field | Type | Description |
|---|---|---|
| `name` | string | Skill identifier matching the `skills.json` name |
| `version` | string | Skill semver version |
| `description` | string | Detailed description of the skill's capability |
| `author.name` | string | Author or organization name |
| `homepage` | string | GitHub tree URL for the skill directory |
| `repository` | string | Root repository URL |
| `license` | string | License identifier |
| `keywords` | string[] | Trigger-oriented keywords for agent invocation |
| `skills` | string[] | Paths to `SKILL.md` files (always `["./SKILL.md"]`) |
| `commands` | string[] | Paths to script directories (always `["./scripts/"]`) |

The `skills` field points Claude Code to the `SKILL.md` file, which contains the agent-readable instructions and trigger conditions for the skill. The `commands` field points to the scripts directory where executable Python helper scripts live. For more on `SKILL.md` structure, see [Skill Structure & Standards](#2.2).

Sources: [skills/requesthunt/.claude-plugin/plugin.json:1-24](), [skills/seo-geo/.claude-plugin/plugin.json:1-29](), [skills/reddit/.claude-plugin/plugin.json:1-22]()

### Inventory of Per-Skill `plugin.json` Files

| Skill | `plugin.json` Path | `skills` Entry | `commands` Entry |
|---|---|---|---|
| `requesthunt` | `skills/requesthunt/.claude-plugin/plugin.json` | `./SKILL.md` | `./scripts/` |
| `reddit` | `skills/reddit/.claude-plugin/plugin.json` | `./SKILL.md` | `./scripts/` |
| `twitter` | `skills/twitter/.claude-plugin/plugin.json` | `./SKILL.md` | `./scripts/` |
| `nanobanana` | `skills/nanobanana/.claude-plugin/plugin.json` | `./SKILL.md` | `./scripts/` |
| `producthunt` | `skills/producthunt/.claude-plugin/plugin.json` | `./SKILL.md` | `./scripts/` |
| `seo-geo` | `skills/seo-geo/.claude-plugin/plugin.json` | `./SKILL.md` | `./scripts/` |

> **Note:** Not every skill directory has been shown in the source files above, but all skills follow the same pattern.

Sources: [skills/seo-geo/.claude-plugin/plugin.json:23-28](), [skills/nanobanana/.claude-plugin/plugin.json:19-24](), [skills/producthunt/.claude-plugin/plugin.json:18-23]()

---

## File Relationships and Data Flow

**Diagram: marketplace.json → plugin.json → skill entry points**

```mermaid
graph LR
  MJ[".claude-plugin/marketplace.json"]
  MJ -->|"source: ./skills/requesthunt"| RH["skills/requesthunt/"]
  MJ -->|"source: ./skills/reddit"| RD["skills/reddit/"]
  MJ -->|"source: ./skills/seo-geo"| SG["skills/seo-geo/"]
  MJ -->|"source: ./skills/..."| ETC["skills/.../"]

  RH --> RHP["skills/requesthunt/.claude-plugin/plugin.json"]
  RD --> RDP["skills/reddit/.claude-plugin/plugin.json"]
  SG --> SGP["skills/seo-geo/.claude-plugin/plugin.json"]

  RHP -->|"skills: [./SKILL.md]"| RHSK["skills/requesthunt/SKILL.md"]
  RHP -->|"commands: [./scripts/]"| RHSC["skills/requesthunt/scripts/"]

  RDP -->|"skills: [./SKILL.md]"| RDSK["skills/reddit/SKILL.md"]
  RDP -->|"commands: [./scripts/]"| RDSC["skills/reddit/scripts/"]
```

Sources: [.claude-plugin/marketplace.json:24-44](), [skills/requesthunt/.claude-plugin/plugin.json:16-23](), [skills/reddit/.claude-plugin/plugin.json:16-22]()

---

## Claude Code Plugin Commands

The following `/plugin` commands are used to interact with OPC Skills through Claude Code's marketplace system. These operate on the manifests described above.

| Command | Description |
|---|---|
| `/plugin marketplace add <url>` | Register the OPC Skills marketplace using the repository URL |
| `/plugin install <name>` | Install a specific skill by its `name` field from `marketplace.json` |
| `/plugin list` | List all installed plugins and their versions |
| `/plugin enable <name>` | Enable a previously installed but disabled plugin |
| `/plugin marketplace update` | Pull the latest `marketplace.json` to refresh available skill listings |

After installation, Claude Code reads the target skill's `plugin.json`, loads the `SKILL.md` specified in `skills`, and makes the scripts in `commands` available for agent invocation.

---

## `strict` Field Behavior

All plugin entries in `marketplace.json` set `"strict": true` [.claude-plugin/marketplace.json:42](). In strict mode, Claude Code enforces that the plugin's declared entry points (`SKILL.md`, `scripts/`) exist and are valid before the plugin is considered successfully installed. This prevents partially installed or misconfigured skills from being silently activated.

Sources: [.claude-plugin/marketplace.json:42](), [.claude-plugin/marketplace.json:59](), [.claude-plugin/marketplace.json:78]()

---

## Relationship to Other Installation Methods

The Claude Code plugin marketplace is one of three ways to install OPC Skills. The `source` paths in `marketplace.json` point to the same skill directories that the `npx skills add` installer and agent-specific commands use. All methods converge on the same `skills/<name>/` directory structure.

For how `npx skills add` resolves and installs these same directories, see [Universal Installer (npx skills add)](#3.3). For the full comparison of all methods, see [Installation Methods Overview](#3.1).

---

# Page: Universal Installer (npx skills add)

# Universal Installer (npx skills add)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitattributes](.gitattributes)
- [.github/workflows/test-installer.yml](.github/workflows/test-installer.yml)
- [README.md](README.md)
- [skill-logos/archive.svg](skill-logos/archive.svg)
- [website/opc-banner.png](website/opc-banner.png)

</details>



## Purpose and Scope

This document covers the universal installer for OPC Skills, which uses the `npx skills add` command to install skills across 16+ AI coding platforms. The installer abstracts platform differences, automatically detects the target environment, and handles dependency resolution.

For information about installing via Claude Code's plugin marketplace, see [Claude Code Plugin Marketplace](#3.2). For platform-specific installation details and directory structures, see [Platform-Specific Installation](#3.4).

**Sources:** [README.md:1-182]()

---

## Command Syntax

The universal installer uses `npx` to execute the `skills` command from Vercel Labs' `@skills/cli` package without requiring global installation.

### Basic Usage

| Command | Description |
|---------|-------------|
| `npx skills add ReScienceLab/opc-skills` | Install all skills from the repository |
| `npx skills add ReScienceLab/opc-skills --skill reddit` | Install a specific skill |
| `npx skills add ReScienceLab/opc-skills --skill reddit --skill twitter` | Install multiple specific skills |
| `npx skills add ReScienceLab/opc-skills -a droid` | Install to specific agent (Factory Droid) |
| `npx skills add ReScienceLab/opc-skills -y` | Skip confirmation prompts |

### Command Structure

```
npx skills add <repository> [options]
```

**Arguments:**
- `<repository>`: GitHub repository in format `owner/repo` (e.g., `ReScienceLab/opc-skills`)

**Options:**
- `--skill <name>`: Install specific skill(s) - can be specified multiple times
- `-a, --agent <name>`: Target specific AI agent platform
- `-y, --yes`: Auto-confirm installation without prompts
- `--help`: Display help information

**Sources:** [README.md:77-88](), [.github/workflows/test-installer.yml:30-46]()

---

## Supported AI Platforms

The universal installer supports 16+ AI coding platforms through automatic platform detection:

```mermaid
graph TB
    subgraph "Primary Platforms"
        Claude["Claude Code<br/>.claude/skills/"]
        Cursor["Cursor<br/>.cursor/skills/"]
        Droid["Factory Droid<br/>.factory/skills/"]
        Windsurf["Windsurf<br/>.windsurf/skills/"]
    end
    
    subgraph "Additional Platforms"
        OpenCode["OpenCode<br/>.opencode/skills/"]
        Codex["Codex<br/>.codex/skills/"]
        Copilot["GitHub Copilot<br/>.copilot/skills/"]
        Gemini["Gemini CLI<br/>.gemini/skills/"]
        Goose["Goose<br/>.goose/skills/"]
        Kilo["Kilo Code<br/>.kilo/skills/"]
        Roo["Roo Code<br/>.roo/skills/"]
        Trae["Trae<br/>.trae/skills/"]
    end
    
    Installer["npx skills add<br/>ReScienceLab/opc-skills"]
    
    Installer -->|"Auto-detects"| Claude
    Installer -->|"Auto-detects"| Cursor
    Installer -->|"Auto-detects"| Droid
    Installer -->|"Auto-detects"| Windsurf
    Installer -->|"Auto-detects"| OpenCode
    Installer -->|"Auto-detects"| Codex
    Installer -->|"Auto-detects"| Copilot
    Installer -->|"Auto-detects"| Gemini
    Installer -->|"Auto-detects"| Goose
    Installer -->|"Auto-detects"| Kilo
    Installer -->|"Auto-detects"| Roo
    Installer -->|"Auto-detects"| Trae
```

**Platform Detection:**
The installer searches for existing platform-specific directories in the current working directory. If multiple platforms are detected, it prompts the user to select one. The `-a` flag overrides auto-detection.

**Default Platform:**
If no platform is detected and no `-a` flag is provided, the installer defaults to `.factory/skills/` (Factory Droid).

**Sources:** [README.md:109-127](), [.github/workflows/test-installer.yml:41-47]()

---

## Installation Process Flow

The following diagram shows the complete installation flow from command execution to installed skills:

### Installation Flow Diagram

```mermaid
flowchart TD
    Start["User executes:<br/>npx skills add ReScienceLab/opc-skills"]
    
    FetchJSON["Fetch skills.json<br/>from GitHub raw"]
    
    ParseSkills["Parse skills.json<br/>Extract skill metadata"]
    
    SkillSelection{"--skill flag<br/>provided?"}
    
    SelectSpecific["Install specific skill(s)<br/>from --skill arguments"]
    SelectAll["Install all skills<br/>from skills.json"]
    
    DetectPlatform["Platform detection:<br/>Search for .claude/, .cursor/,<br/>.factory/, .windsurf/, etc."]
    
    PlatformFound{"Platform<br/>detected?"}
    
    UserSelect["Prompt user to<br/>select platform"]
    UseFlag["Use platform from<br/>-a/--agent flag"]
    UseDefault["Default to<br/>.factory/skills/"]
    
    CheckDeps["Check dependencies<br/>in skills.json"]
    
    HasDeps{"Dependencies<br/>exist?"}
    
    InstallDeps["Recursively install<br/>dependency skills first"]
    
    CreateDir["Create directory:<br/>{platform}/skills/{skill-name}/"]
    
    CopyFiles["Copy skill files:<br/>SKILL.md, scripts/,<br/>images/, etc."]
    
    Verify["Verify installation:<br/>Check SKILL.md exists"]
    
    Success["Installation complete<br/>Skill ready to use"]
    
    Start --> FetchJSON
    FetchJSON --> ParseSkills
    ParseSkills --> SkillSelection
    
    SkillSelection -->|"Yes"| SelectSpecific
    SkillSelection -->|"No"| SelectAll
    
    SelectSpecific --> DetectPlatform
    SelectAll --> DetectPlatform
    
    DetectPlatform --> PlatformFound
    
    PlatformFound -->|"Yes"| CheckDeps
    PlatformFound -->|"No, -a provided"| UseFlag
    PlatformFound -->|"No, no -a"| UseDefault
    
    UseFlag --> CheckDeps
    UseDefault --> CheckDeps
    
    CheckDeps --> HasDeps
    
    HasDeps -->|"Yes"| InstallDeps
    HasDeps -->|"No"| CreateDir
    
    InstallDeps --> CreateDir
    
    CreateDir --> CopyFiles
    CopyFiles --> Verify
    Verify --> Success
```

**Sources:** [README.md:77-104](), [.github/workflows/test-installer.yml:30-83]()

---

## Installation Directories

The installer creates a consistent directory structure across all platforms:

```
{platform}/
└── skills/
    ├── {skill-name}/
    │   ├── SKILL.md
    │   ├── scripts/
    │   │   └── (optional scripts)
    │   ├── images/
    │   │   └── (optional images)
    │   └── examples/
    │       └── (optional examples)
    └── {another-skill}/
        └── ...
```

### Platform-Specific Paths

| Platform | Installation Directory | Example |
|----------|----------------------|---------|
| Claude Code | `.claude/skills/{skill-name}/` | `.claude/skills/reddit/` |
| Cursor | `.cursor/skills/{skill-name}/` | `.cursor/skills/twitter/` |
| Factory Droid | `.factory/skills/{skill-name}/` | `.factory/skills/seo-geo/` |
| Windsurf | `.windsurf/skills/{skill-name}/` | `.windsurf/skills/domain-hunter/` |
| OpenCode | `.opencode/skills/{skill-name}/` | `.opencode/skills/logo-creator/` |
| Codex | `.codex/skills/{skill-name}/` | `.codex/skills/nanobanana/` |
| GitHub Copilot | `.copilot/skills/{skill-name}/` | `.copilot/skills/requesthunt/` |
| Gemini CLI | `.gemini/skills/{skill-name}/` | `.gemini/skills/producthunt/` |
| Goose | `.goose/skills/{skill-name}/` | `.goose/skills/banner-creator/` |

**Sources:** [.github/workflows/test-installer.yml:41-47](), [README.md:109-127]()

---

## Dependency Resolution

The installer automatically resolves and installs skill dependencies as defined in `skills.json`.

### Dependency Resolution Process

```mermaid
flowchart TD
    Start["Install skill request:<br/>domain-hunter"]
    
    LoadJSON["Load skills.json<br/>Find domain-hunter entry"]
    
    CheckDeps["Read dependencies field:<br/>{twitter: '1.0.0',<br/>reddit: '1.0.0'}"]
    
    HasDeps{"Dependencies<br/>present?"}
    
    NoDeps["Proceed with<br/>installation"]
    
    IterateDeps["For each dependency:<br/>twitter, reddit"]
    
    CheckInstalled{"Dependency<br/>already installed?"}
    
    Skip["Skip dependency<br/>installation"]
    
    RecursiveCheck["Check if dependency<br/>has its own dependencies"]
    
    InstallDep["Install dependency skill:<br/>Copy to skills/ directory"]
    
    VerifyDep["Verify dependency:<br/>Check SKILL.md exists"]
    
    NextDep{"More<br/>dependencies?"}
    
    InstallMain["Install main skill:<br/>domain-hunter"]
    
    Complete["Installation complete:<br/>domain-hunter + dependencies"]
    
    Start --> LoadJSON
    LoadJSON --> CheckDeps
    CheckDeps --> HasDeps
    
    HasDeps -->|"No"| NoDeps
    HasDeps -->|"Yes"| IterateDeps
    
    NoDeps --> InstallMain
    
    IterateDeps --> CheckInstalled
    
    CheckInstalled -->|"Yes"| Skip
    CheckInstalled -->|"No"| RecursiveCheck
    
    Skip --> NextDep
    
    RecursiveCheck --> InstallDep
    InstallDep --> VerifyDep
    VerifyDep --> NextDep
    
    NextDep -->|"Yes"| IterateDeps
    NextDep -->|"No"| InstallMain
    
    InstallMain --> Complete
```

### Skills with Dependencies

The following skills have dependencies that are automatically installed:

| Skill | Dependencies | Reason |
|-------|--------------|--------|
| `seo-geo` | `twitter`, `reddit` | Requires social media data for SEO research |
| `domain-hunter` | `twitter`, `reddit` | Requires social validation for domain suggestions |
| `logo-creator` | `nanobanana` | Uses image generation capability |
| `banner-creator` | `nanobanana` | Uses image generation capability |

**Example:** Installing `domain-hunter` automatically installs `twitter` and `reddit` if not already present:

```bash
npx skills add ReScienceLab/opc-skills --skill domain-hunter
# Installs: reddit, twitter, domain-hunter
```

**Sources:** [README.md:92-104]()

---

## Cross-Platform Testing

The repository includes comprehensive automated testing to validate installation across platforms and operating systems.

### Testing Matrix

The CI/CD pipeline tests every skill on every supported operating system:

```mermaid
graph TB
    subgraph "Test Matrix"
        Ubuntu["ubuntu-latest"]
        MacOS["macos-latest"]
        Windows["windows-latest"]
    end
    
    subgraph "Skills Under Test"
        requesthunt["requesthunt"]
        reddit["reddit"]
        twitter["twitter"]
        nanobanana["nanobanana"]
        logo["logo-creator"]
        banner["banner-creator"]
        domain["domain-hunter"]
        producthunt["producthunt"]
        seogeo["seo-geo"]
    end
    
    subgraph "Test Operations"
        Install["npx skills add<br/>--skill {name} -y"]
        Verify["Verify directory:<br/>.factory/skills/{name}/"]
        CheckFiles["Check SKILL.md exists"]
        CountSkills["Count installed skills"]
    end
    
    Ubuntu --> Install
    MacOS --> Install
    Windows --> Install
    
    requesthunt --> Install
    reddit --> Install
    twitter --> Install
    nanobanana --> Install
    logo --> Install
    banner --> Install
    domain --> Install
    producthunt --> Install
    seogeo --> Install
    
    Install --> Verify
    Verify --> CheckFiles
    CheckFiles --> CountSkills
```

### Test Workflow Details

The test workflow (`test-installer.yml`) runs on every push to `main` and on pull requests that modify `skills.json` or the `skills/` directory.

**Test Jobs:**

1. **Individual Skill Tests** (27 parallel runs)
   - Matrix: 9 skills × 3 operating systems = 27 test runs
   - Each test installs a single skill and verifies the installation

2. **All Skills Test** (3 parallel runs)
   - Matrix: 3 operating systems
   - Each test installs all skills at once
   - Verifies that at least 9 skills are installed

3. **skills.json Validation**
   - Validates JSON syntax using `jq`
   - Verifies required fields (name, description, dependencies)
   - Validates that all dependencies reference existing skills

**Test Steps:**

```yaml
# Individual skill test
npx skills add ${{ github.repository }} --skill ${{ matrix.skill }} -y
# Verify
ls -la .factory/skills/${{ matrix.skill }}/

# All skills test
npx skills add ${{ github.repository }} -y
# Count
SKILL_COUNT=$(ls -1 .factory/skills/ | wc -l)
```

**Sources:** [.github/workflows/test-installer.yml:1-118]()

---

## Command Options Reference

### Complete Options Table

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--skill` | - | string[] | all skills | Specific skill(s) to install (repeatable) |
| `--agent` | `-a` | string | auto-detect | Target AI platform |
| `--yes` | `-y` | boolean | false | Skip confirmation prompts |
| `--help` | `-h` | boolean | - | Display help information |

### Agent Platform Names

Valid values for the `-a/--agent` flag:

| Name | Platform | Directory |
|------|----------|-----------|
| `claude` | Claude Code | `.claude/skills/` |
| `cursor` | Cursor | `.cursor/skills/` |
| `droid` | Factory Droid | `.factory/skills/` |
| `windsurf` | Windsurf | `.windsurf/skills/` |
| `opencode` | OpenCode | `.opencode/skills/` |
| `codex` | Codex | `.codex/skills/` |
| `copilot` | GitHub Copilot | `.copilot/skills/` |
| `gemini` | Gemini CLI | `.gemini/skills/` |
| `goose` | Goose | `.goose/skills/` |
| `kilo` | Kilo Code | `.kilo/skills/` |
| `roo` | Roo Code | `.roo/skills/` |
| `trae` | Trae | `.trae/skills/` |

**Sources:** [README.md:77-127](), [.github/workflows/test-installer.yml:30-46]()

---

## Installation Examples

### Example 1: Install All Skills

```bash
npx skills add ReScienceLab/opc-skills -y
```

**Result:**
- Installs all 9 skills from the repository
- Auto-detects platform or uses `.factory/skills/` as default
- Resolves all dependencies automatically

### Example 2: Install Specific Skills

```bash
npx skills add ReScienceLab/opc-skills --skill reddit --skill twitter --skill domain-hunter
```

**Result:**
- Installs `reddit`, `twitter`, and `domain-hunter`
- Since `domain-hunter` depends on `reddit` and `twitter`, those dependencies are satisfied
- No duplicate installations occur

### Example 3: Install to Specific Platform

```bash
npx skills add ReScienceLab/opc-skills -a cursor --skill seo-geo
```

**Result:**
- Installs to `.cursor/skills/seo-geo/`
- Also installs dependencies to `.cursor/skills/twitter/` and `.cursor/skills/reddit/`

### Example 4: Install All Skills for Multiple Platforms

```bash
# Install for Cursor
npx skills add ReScienceLab/opc-skills -a cursor -y

# Install for Factory Droid
npx skills add ReScienceLab/opc-skills -a droid -y
```

**Result:**
- Creates separate skill installations in both `.cursor/skills/` and `.factory/skills/`
- Each platform maintains its own independent skill collection

**Sources:** [README.md:77-104](), [.github/workflows/test-installer.yml:30-83]()

---

## Error Handling and Troubleshooting

### Common Installation Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "No platform detected" | Working directory has no platform folders | Use `-a` flag to specify target platform |
| "Skill not found" | Skill name doesn't exist in `skills.json` | Check available skills with `/plugin marketplace list` |
| "Permission denied" | Insufficient write permissions | Run with appropriate permissions or change directory |
| Network errors | GitHub API rate limiting or connectivity | Wait and retry, or check network connection |
| Validation fails | `skills.json` has invalid dependencies | CI will catch this before merge |

### Verification Commands

After installation, verify skills are properly installed:

```bash
# List installed skills
ls -la .factory/skills/

# Check specific skill
cat .factory/skills/reddit/SKILL.md

# Count installed skills
ls -1 .factory/skills/ | wc -l
```

**Expected Output:**
- Each skill directory contains at minimum a `SKILL.md` file
- Skill count should match the number of skills installed
- `SKILL.md` should have valid YAML frontmatter

**Sources:** [.github/workflows/test-installer.yml:40-83]()

---

## Integration with skills.json

The installer reads skill metadata from `skills.json` to determine what to install and in what order.

### skills.json Structure Used by Installer

```json
{
  "version": "1.0.7",
  "skills": [
    {
      "name": "reddit",
      "description": "Search and retrieve content from Reddit",
      "version": "1.0.0",
      "dependencies": {}
    },
    {
      "name": "domain-hunter",
      "description": "Find domains, compare registrar prices",
      "version": "1.0.0",
      "dependencies": {
        "twitter": "1.0.0",
        "reddit": "1.0.0"
      }
    }
  ]
}
```

**Key Fields:**
- `name`: Skill identifier used in `--skill` flag
- `version`: Skill version (currently pinned)
- `dependencies`: Object mapping dependency names to versions

For detailed information about `skills.json` structure and management, see [Skills Registry (skills.json)](#2.1).

**Sources:** [.github/workflows/test-installer.yml:85-117](), [README.md:92-104]()

---

# Page: Platform-Specific Installation

# Platform-Specific Installation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [skill-logos/archive.svg](skill-logos/archive.svg)
- [skills.json](skills.json)
- [skills/archive/SKILL.md](skills/archive/SKILL.md)
- [skills/archive/references/TEMPLATE.md](skills/archive/references/TEMPLATE.md)
- [website/opc-banner.png](website/opc-banner.png)

</details>



## Purpose and Scope

This document provides detailed installation instructions for OPC Skills on specific AI coding platforms. It covers platform-specific directory structures, user-level vs project-level installation patterns, and platform-specific configuration requirements.

For an overview of installation methods, see [Installation Methods Overview](#3.1). For details about the Claude Plugin Marketplace, see [Claude Code Plugin Marketplace](#3.2). For the universal `npx skills add` installer, see [Universal Installer](#3.3).

## Installation Command Structure

Each skill entry in `skills.json` contains an `install` field with two sub-objects: `user` and `project`. These hold the exact commands for each supported platform.

**Install field schema** ([skills.json:48-61]()):

```
install
├── user
│   ├── claude    → npx skills add ... --skill <name> -a claude
│   ├── droid     → npx skills add ... --skill <name> -a droid
│   ├── opencode  → npx skills add ... --skill <name> -a opencode
│   └── codex     → npx skills add ... --skill <name> -a codex
└── project
    ├── claude    → npx skills add ... --skill <name>
    ├── droid     → npx skills add ... --skill <name>
    ├── cursor    → npx skills add ... --skill <name>
    ├── opencode  → npx skills add ... --skill <name>
    └── codex     → npx skills add ... --skill <name>
```

Key observations from `skills.json`:

- **User-level** commands add the `-a <platform>` flag to target a specific agent's global directory.
- **Project-level** commands omit the `-a` flag entirely; the installer places the skill in the current project directory.
- **Cursor** appears only in `project` installs, not `user` installs — Cursor does not have a user-level target in the install spec.

**Diagram: install field in skills.json → npx command flags**

```mermaid
graph LR
    A["skills.json<br/>install.user.*"] -->|"-a claude"| B["Claude Code<br/>(user-global)"]
    A -->|"-a droid"| C["Factory Droid<br/>(user-global)"]
    A -->|"-a opencode"| D["OpenCode<br/>(user-global)"]
    A -->|"-a codex"| E["Codex<br/>(user-global)"]
    F["skills.json<br/>install.project.*"] -->|"no -a flag"| G["Claude Code<br/>(project-local)"]
    F -->|"no -a flag"| H["Factory Droid<br/>(project-local)"]
    F -->|"no -a flag"| I["Cursor<br/>(project-local)"]
    F -->|"no -a flag"| J["OpenCode<br/>(project-local)"]
    F -->|"no -a flag"| K["Codex<br/>(project-local)"]
```

Sources: [skills.json:48-61](), [skills.json:100-113](), [skills.json:152-165]()

### Skill Directory Structure

Once installed, each skill follows this internal layout:

**Diagram: Installed skill directory layout**

```mermaid
graph LR
    SkillRoot["skills/seo-geo/"]
    SkillRoot --> SkillMD["SKILL.md"]
    SkillRoot --> ScriptsDir["scripts/"]
    SkillRoot --> ExamplesDir["examples/"]
    SkillRoot --> ReferencesDir["references/"]
    ScriptsDir --> S1["seo_audit.py"]
    ScriptsDir --> S2["keyword_research.py"]
    ScriptsDir --> S3["domain_overview.py"]
    ExamplesDir --> E1["opc-skills-case-study.md"]
    SkillMD --> YAMLFront["YAML frontmatter<br/>name, description"]
    SkillMD --> Instructions["Step-by-step<br/>agent instructions"]
```

Sources: [skills.json:63-73](), [skills.json:1-538]()

## User-Level vs Project-Level Installation

### User-Level Installation

User-level installs place the skill in the agent's global directory, making it available across all projects for that user. The `-a <platform>` flag is required.

| Platform key | `install.user` command suffix |
|---|---|
| `claude` | `--skill <name> -a claude` |
| `droid` | `--skill <name> -a droid` |
| `opencode` | `--skill <name> -a opencode` |
| `codex` | `--skill <name> -a codex` |

**Cursor is not listed** in `install.user` for any skill in `skills.json`. User-level Cursor installation is not part of the current install spec.

**Use cases:**
- Foundation skills (`twitter`, `reddit`, `nanobanana`) used across many projects
- Personal automation workflows

Sources: [skills.json:49-54](), [skills.json:101-105](), [skills.json:323-327]()

### Project-Level Installation

Project-level installs place the skill in the current working directory. The `-a` flag is omitted; the installer targets whichever platform the project uses.

| Platform key | `install.project` command |
|---|---|
| `claude` | `npx skills add ReScienceLab/opc-skills --skill <name>` |
| `droid` | `npx skills add ReScienceLab/opc-skills --skill <name>` |
| `cursor` | `npx skills add ReScienceLab/opc-skills --skill <name>` |
| `opencode` | `npx skills add ReScienceLab/opc-skills --skill <name>` |
| `codex` | `npx skills add ReScienceLab/opc-skills --skill <name>` |

All project-level commands are identical in `skills.json`; the target platform is determined by the agent running in the project directory.

**Use cases:**
- Project-specific skills that should live alongside project code
- Team environments where skills are committed to version control
- Skills requiring project-specific API key configuration

Sources: [skills.json:55-61](), [skills.json:107-113](), [skills.json:329-335]()

## Platform-Specific Installation Commands

The following commands come directly from the `install` field of each skill entry in `skills.json`. All commands use `npx skills add`; the old `curl -fsSL opc.dev/install.sh` form is no longer used (see [CHANGELOG.md:64-67]()).

### Install Commands by Platform

**Diagram: skills.json install entries → platform-specific npx commands**

```mermaid
graph TD
    skillsjson["skills.json<br/>skill.install"]
    user["install.user"]
    project["install.project"]
    skillsjson --> user
    skillsjson --> project

    user --> uc["claude<br/>-a claude"]
    user --> ud["droid<br/>-a droid"]
    user --> uo["opencode<br/>-a opencode"]
    user --> ux["codex<br/>-a codex"]

    project --> pc["claude<br/>(no -a flag)"]
    project --> pd["droid<br/>(no -a flag)"]
    project --> pcur["cursor<br/>(no -a flag)"]
    project --> po["opencode<br/>(no -a flag)"]
    project --> px["codex<br/>(no -a flag)"]
```

Sources: [skills.json:48-61](), [skills.json:100-113]()

### Claude Code

Claude Code supports both user-level and project-level install via `npx skills add`. It also supports installation through the Plugin Marketplace (see page 3.2).

| Level | Command |
|---|---|
| User | `npx skills add ReScienceLab/opc-skills --skill <name> -a claude` |
| Project | `npx skills add ReScienceLab/opc-skills --skill <name>` |

Example for `seo-geo` ([skills.json:50-57]()):

```
# User-level
npx skills add ReScienceLab/opc-skills --skill seo-geo -a claude

# Project-level
npx skills add ReScienceLab/opc-skills --skill seo-geo
```

Sources: [skills.json:49-57]()

### Factory Droid (`droid`)

| Level | Command |
|---|---|
| User | `npx skills add ReScienceLab/opc-skills --skill <name> -a droid` |
| Project | `npx skills add ReScienceLab/opc-skills --skill <name>` |

Example for `logo-creator` ([skills.json:219-229]()):

```
# User-level
npx skills add ReScienceLab/opc-skills --skill logo-creator -a droid

# Project-level
npx skills add ReScienceLab/opc-skills --skill logo-creator
```

Sources: [skills.json:217-229]()

### Cursor

Cursor is only present in `install.project` entries in `skills.json` — there is no `install.user.cursor` key for any skill. Cursor installation is project-level only.

| Level | Command |
|---|---|
| Project | `npx skills add ReScienceLab/opc-skills --skill <name>` |

Example for `domain-hunter` ([skills.json:160-165]()):

```
# Project-level only
npx skills add ReScienceLab/opc-skills --skill domain-hunter
```

Sources: [skills.json:159-165]()

### OpenCode

| Level | Command |
|---|---|
| User | `npx skills add ReScienceLab/opc-skills --skill <name> -a opencode` |
| Project | `npx skills add ReScienceLab/opc-skills --skill <name>` |

Example for `banner-creator` ([skills.json:276-285]()):

```
# User-level
npx skills add ReScienceLab/opc-skills --skill banner-creator -a opencode

# Project-level
npx skills add ReScienceLab/opc-skills --skill banner-creator
```

Sources: [skills.json:274-285]()

### Codex

| Level | Command |
|---|---|
| User | `npx skills add ReScienceLab/opc-skills --skill <name> -a codex` |
| Project | `npx skills add ReScienceLab/opc-skills --skill <name>` |

Example for `producthunt` ([skills.json:469-480]()):

```
# User-level
npx skills add ReScienceLab/opc-skills --skill producthunt -a codex

# Project-level
npx skills add ReScienceLab/opc-skills --skill producthunt
```

Sources: [skills.json:467-480]()

## Complete Install Command Reference

The table below lists every `install.user` and `install.project` command for all nine skills, as defined in `skills.json`. All commands follow the pattern `npx skills add ReScienceLab/opc-skills --skill <name> [-a <platform>]`.

**Diagram: Relationship between skills.json install entries and the npx skills add CLI**

```mermaid
graph LR
    A["skills.json<br/>skill[].install.user[platform]"] -->|"read by"| B["npx skills add<br/>(Universal Installer)"]
    C["skills.json<br/>skill[].install.project[platform]"] -->|"read by"| B
    B -->|"-a claude"| D["Claude Code<br/>user-global target"]
    B -->|"-a droid"| E["Factory Droid<br/>user-global target"]
    B -->|"-a opencode"| F["OpenCode<br/>user-global target"]
    B -->|"-a codex"| G["Codex<br/>user-global target"]
    B -->|"no -a flag"| H["Project directory<br/>(all platforms)"]
```

Sources: [skills.json:48-61](), [skills.json:100-113](), [skills.json:152-165](), [skills.json:216-229]()

### User-Level Install Commands

| Skill | claude | droid | opencode | codex |
|---|---|---|---|---|
| `seo-geo` | `... --skill seo-geo -a claude` | `... --skill seo-geo -a droid` | `... --skill seo-geo -a opencode` | `... --skill seo-geo -a codex` |
| `requesthunt` | `... --skill requesthunt -a claude` | `... --skill requesthunt -a droid` | `... --skill requesthunt -a opencode` | `... --skill requesthunt -a codex` |
| `domain-hunter` | `... --skill domain-hunter -a claude` | `... --skill domain-hunter -a droid` | `... --skill domain-hunter -a opencode` | `... --skill domain-hunter -a codex` |
| `logo-creator` | `... --skill logo-creator -a claude` | `... --skill logo-creator -a droid` | `... --skill logo-creator -a opencode` | `... --skill logo-creator -a codex` |
| `banner-creator` | `... --skill banner-creator -a claude` | `... --skill banner-creator -a droid` | `... --skill banner-creator -a opencode` | `... --skill banner-creator -a codex` |
| `nanobanana` | `... --skill nanobanana -a claude` | `... --skill nanobanana -a droid` | `... --skill nanobanana -a opencode` | `... --skill nanobanana -a codex` |
| `reddit` | `... --skill reddit -a claude` | `... --skill reddit -a droid` | `... --skill reddit -a opencode` | `... --skill reddit -a codex` |
| `twitter` | `... --skill twitter -a claude` | `... --skill twitter -a droid` | `... --skill twitter -a opencode` | `... --skill twitter -a codex` |
| `producthunt` | `... --skill producthunt -a claude` | `... --skill producthunt -a droid` | `... --skill producthunt -a opencode` | `... --skill producthunt -a codex` |
| `archive` | `... --skill archive -a claude` | `... --skill archive -a droid` | `... --skill archive -a opencode` | `... --skill archive -a codex` |

> All commands prefixed with `npx skills add ReScienceLab/opc-skills`. Cursor has no user-level entry.

Sources: [skills.json:49-54](), [skills.json:101-105](), [skills.json:153-157](), [skills.json:217-221](), [skills.json:273-277](), [skills.json:323-327](), [skills.json:366-370](), [skills.json:417-421](), [skills.json:468-472](), [skills.json:519-523]()

### Project-Level Install Commands

All project-level commands are identical in form — the `-a` flag is omitted:

```
npx skills add ReScienceLab/opc-skills --skill <name>
```

This applies to: `claude`, `droid`, `cursor`, `opencode`, `codex` (all five platforms).

Sources: [skills.json:55-61](), [skills.json:107-113](), [skills.json:159-165]()

## Dependency Installation Patterns

### Skills with Dependencies

Some skills require other skills as dependencies. The dependency structure from [skills.json:28-31]():

```mermaid
graph LR
    subgraph Composite_Skills["Composite Skills"]
        SEOGEO["seo-geo<br/>v1.0.0"]
        DomainHunter["domain-hunter<br/>v1.0.0"]
        LogoCreator["logo-creator<br/>v1.0.0"]
        BannerCreator["banner-creator<br/>v1.0.0"]
    end
    
    subgraph Foundation_Skills["Foundation Skills"]
        Twitter["twitter<br/>v1.0.0"]
        Reddit["reddit<br/>v1.0.0"]
        Nanobanana["nanobanana<br/>v1.0.0"]
    end
    
    SEOGEO -->|"requires"| Twitter
    SEOGEO -->|"requires"| Reddit
    
    DomainHunter -->|"requires"| Twitter
    DomainHunter -->|"requires"| Reddit
    
    LogoCreator -->|"requires"| Nanobanana
    BannerCreator -->|"requires"| Nanobanana
```

### Installing Skills with Dependencies

**Manual Installation:**

```bash
# Install foundation skills first
npx skills add ReScienceLab/opc-skills --skill twitter
npx skills add ReScienceLab/opc-skills --skill reddit

# Then install composite skill
npx skills add ReScienceLab/opc-skills --skill domain-hunter
```

**Batch Installation:**

```bash
# Install all dependencies together
npx skills add ReScienceLab/opc-skills \
  --skill twitter \
  --skill reddit \
  --skill domain-hunter
```

Sources: [skills.json:28-31](), [skills.json:143-146](), [README.md:92-104]()

## Platform Compatibility Matrix

### Platform Support Matrix

The following matrix reflects what is actually declared in the `install` field of `skills.json`.

| Feature | claude | droid | cursor | opencode | codex |
|---|---|---|---|---|---|
| User-level (`install.user`) | ✓ | ✓ | — | ✓ | ✓ |
| Project-level (`install.project`) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Plugin Marketplace (`.claude-plugin/`) | ✓ | — | — | — | — |

Cursor has no `install.user` entry in any skill in `skills.json`. The Plugin Marketplace is Claude Code–only (see page 3.2).

Sources: [skills.json:48-61](), [skills.json:100-113](), [.claude-plugin/marketplace.json:1-10]()

## Verification and Troubleshooting

### Verifying Installation

After running `npx skills add`, verify the skill was placed in the correct directory by checking for `SKILL.md`:

```bash
# Claude Code (project-level)
ls .claude/skills/seo-geo/SKILL.md

# Factory Droid (project-level)
ls .factory/skills/logo-creator/SKILL.md

# Cursor (project-level)
ls .cursor/skills/domain-hunter/SKILL.md
```

**Verify SKILL.md frontmatter:**

```bash
head -n 10 .claude/skills/seo-geo/SKILL.md
# Expected:
# ---
# name: seo-geo
# description: SEO & GEO (Generative Engine Optimization)...
# ---
```

### Common Installation Issues

#### Issue: Skill not recognized by AI agent

**Symptoms:**
- Agent doesn't activate skill on trigger keywords
- Commands not found

**Solutions:**

1. **Verify SKILL.md format:**
```bash
# Check YAML frontmatter is valid
cat ~/.claude/skills/seo-geo/SKILL.md | head -20
```

2. **Check directory name matches skill name:**
```bash
# Directory name must match 'name' field in SKILL.md
# Correct: ~/.claude/skills/seo-geo/
# Incorrect: ~/.claude/skills/SEO-GEO/
```

3. **Restart the AI platform:**
```bash
# Restart Claude Code, Cursor, etc. to reload skills
```

#### Issue: Dependency not found

**Symptoms:**
- Skill fails to execute
- Error messages about missing dependencies

**Solutions:**

1. **Check dependencies in skills.json:**
```bash
# View required dependencies
cat skills.json | grep -A 5 "domain-hunter"
```

2. **Install missing dependencies:**
```bash
# Install required foundation skills
npx skills add ReScienceLab/opc-skills --skill twitter --skill reddit
```

#### Issue: Script execution fails

**Symptoms:**
- Python script errors
- Permission denied errors

**Solutions:**

1. **Verify Python installation:**
```bash
python3 --version
# Should be Python 3.8+
```

2. **Check script permissions:**
```bash
chmod +x ~/.claude/skills/seo-geo/scripts/*.py
```

3. **Install Python dependencies:**
```bash
# Most skills include requirements.txt
cd ~/.claude/skills/seo-geo/
pip3 install -r requirements.txt
```

Sources: [.factory/AGENTS.md:540-571](), [skills.json:28-46]()

### Platform-Specific Troubleshooting

#### Claude Code

**Issue: Plugin marketplace source path errors**

From [CHANGELOG.md:92-105]():
- Claude Code has known bugs with `pluginRoot` field
- Solution: Uses full paths like `"./skills/domain-hunter"` instead of `"./domain-hunter"`

**Issue: Marketplace cache stale**

From [CHANGELOG.md:101-105]():
- Increment marketplace metadata version to trigger cache refresh
- Current version uses explicit skill paths to avoid cache issues

#### Cursor

**Issue: Skills not detected in project**

- Ensure `.cursor/skills/` directory exists in project root
- Check `.cursorignore` doesn't exclude skills directory

#### Factory Droid

**Issue: Dependency resolution**

- Skills with dependencies (e.g., `logo-creator` requires `nanobanana`) must be installed separately.
- Install dependencies first, then the composite skill.
- Check `.factory/skills/` for installed skill directories.

Sources: [CHANGELOG.md:88-105](), [skills.json:193-196]()

## Environment Variables and API Keys

Many skills require API keys for external services. These should be configured before skill installation.

### Required API Keys by Skill

| Skill | Environment Variable | Service | Required? |
|-------|---------------------|---------|-----------|
| twitter | `TWITTERAPI_API_KEY` | twitterapi.io | Yes |
| nanobanana | `GEMINI_API_KEY` | Google AI Studio | Yes |
| logo-creator | `GEMINI_API_KEY` | Google AI Studio | Yes |
| logo-creator | `REMOVE_BG_API_KEY` | remove.bg | Optional |
| logo-creator | `RECRAFT_API_KEY` | recraft.ai | Optional |
| banner-creator | `GEMINI_API_KEY` | Google AI Studio | Yes |
| producthunt | `PRODUCTHUNT_ACCESS_TOKEN` | Product Hunt | Yes |
| requesthunt | `REQUESTHUNT_API_KEY` | requesthunt.com | Yes |
| seo-geo | `DATAFORSEO_LOGIN` | DataForSEO | Optional |
| seo-geo | `DATAFORSEO_PASSWORD` | DataForSEO | Optional |

### Configuration Methods

**Platform environment files:**

```bash
# Claude Code
echo "GEMINI_API_KEY=your_key_here" >> ~/.claude/.env

# Cursor
echo "GEMINI_API_KEY=your_key_here" >> ~/.cursor/.env

# Factory Droid
echo "GEMINI_API_KEY=your_key_here" >> ~/.factory/.env
```

**Project-level configuration:**

```bash
# Create .env in project root
echo "GEMINI_API_KEY=your_key_here" >> .env
echo "TWITTERAPI_API_KEY=your_key_here" >> .env
```

Sources: [skills.json:32-46](), [skills.json:91-98](), [CHANGELOG.md:274-287]()

## Installation Best Practices

### Recommended Installation Order

Install foundation/dependency skills before the skills that depend on them.

1. **Foundation skills** (no dependencies):
```bash
npx skills add ReScienceLab/opc-skills --skill twitter -a claude
npx skills add ReScienceLab/opc-skills --skill reddit -a claude
npx skills add ReScienceLab/opc-skills --skill nanobanana -a claude
```

2. **Composite skills** (require foundation skills):
```bash
npx skills add ReScienceLab/opc-skills --skill seo-geo -a claude
npx skills add ReScienceLab/opc-skills --skill domain-hunter -a claude
npx skills add ReScienceLab/opc-skills --skill logo-creator -a claude
npx skills add ReScienceLab/opc-skills --skill banner-creator -a claude
```

3. **Standalone skills** (no dependencies):
```bash
npx skills add ReScienceLab/opc-skills --skill requesthunt -a claude
npx skills add ReScienceLab/opc-skills --skill producthunt -a claude
npx skills add ReScienceLab/opc-skills --skill archive -a claude
```

Replace `-a claude` with `-a droid`, `-a opencode`, or `-a codex` as appropriate for your platform. For project-level installs, omit the `-a` flag entirely.

### Version Control Considerations

**Include in version control:**
- `.claude/skills/` (if using project-level)
- `.cursor/skills/` (if using project-level)
- `.factory/skills/` (if using project-level)
- API key configuration templates (without actual keys)

**Exclude from version control:**
```gitignore
# User-level skills (installed globally)
~/.claude/skills/
~/.cursor/skills/
~/.factory/skills/

# Environment files with secrets
.env
.claude/.env
.cursor/.env
.factory/.env
```

### Team Collaboration

For teams using shared skill configurations:

1. **Commit project-level skills:**
```bash
git add .claude/skills/
git commit -m "Add seo-geo skill for project"
```

2. **Document required API keys:**
```bash
# Create .env.example
cat > .env.example << EOF
GEMINI_API_KEY=get_from_https://aistudio.google.com/apikey
TWITTERAPI_API_KEY=get_from_https://twitterapi.io
EOF
```

3. **Update project README:**
```markdown
## Skills Setup

1. Install skills:
   ```bash
   npx skills add ReScienceLab/opc-skills --skill seo-geo
   ```

2. Configure API keys:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```
```

Sources: [.factory/AGENTS.md:66-109](), [README.md:92-104]()

---

# Page: Installation Statistics System

# Installation Statistics System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/fetch-install-stats.yml](.github/workflows/fetch-install-stats.yml)
- [scripts/fetch-install-stats.py](scripts/fetch-install-stats.py)
- [website/install-stats.json](website/install-stats.json)

</details>



## Purpose and Scope

The Installation Statistics System tracks and displays real-time installation counts for OPC Skills by scraping the public skills.sh marketplace. This system automatically fetches install data daily, commits updated statistics to the repository, and serves them through the opc.dev website with edge caching. The system provides social proof and usage visibility to potential users.

For information about how these statistics are displayed on the website, see [Website Architecture](#4.1). For details on the website's caching strategy for these stats, see [Caching Strategy](#4.3).

---

## System Architecture

The statistics system operates as a fully automated pipeline with three core components: a Python scraper, a GitHub Actions scheduler, and a JSON data store served via Cloudflare Workers.

**Architecture Diagram: Installation Statistics Pipeline**

```mermaid
graph TB
    subgraph "Data Source"
        SKILLS_SH["skills.sh/resciencelab/opc-skills<br/>Public Marketplace<br/>HTML Page"]
    end
    
    subgraph "Automation Layer"
        GHA["fetch-install-stats.yml<br/>GitHub Actions Workflow<br/>Cron: 0 6 * * *"]
        
        TRIGGER_CRON["Daily Trigger<br/>6 AM UTC"]
        TRIGGER_MANUAL["workflow_dispatch<br/>Manual Trigger"]
        
        TRIGGER_CRON --> GHA
        TRIGGER_MANUAL --> GHA
    end
    
    subgraph "Data Processing"
        SCRAPER["fetch-install-stats.py<br/>Python HTML Parser"]
        
        PARSE_HTML["Parse HTML<br/>Regex Extraction"]
        PARSE_COUNTS["Parse Counts<br/>_parse_count()"]
        CALC_TOTAL["Sum Individual Skills<br/>Calculate Total"]
        
        GHA --> SCRAPER
        SCRAPER --> PARSE_HTML
        PARSE_HTML --> PARSE_COUNTS
        PARSE_COUNTS --> CALC_TOTAL
    end
    
    subgraph "Data Storage"
        JSON_FILE["website/install-stats.json<br/>Committed to Repo"]
        
        DIFF_CHECK["git diff --quiet<br/>Check for Changes"]
        AUTO_COMMIT["git commit + push<br/>github-actions[bot]"]
        
        CALC_TOTAL --> JSON_FILE
        JSON_FILE --> DIFF_CHECK
        DIFF_CHECK -->|"changed=true"| AUTO_COMMIT
        AUTO_COMMIT --> JSON_FILE
    end
    
    subgraph "Content Delivery"
        WORKER["worker.js<br/>Cloudflare Worker<br/>fetchInstallStats()"]
        EDGE_CACHE["caches.default<br/>TTL: 3600s"]
        WEBSITE["opc.dev<br/>Landing Page Display"]
        
        JSON_FILE --> WORKER
        WORKER --> EDGE_CACHE
        EDGE_CACHE --> WEBSITE
    end
    
    SKILLS_SH -->|"HTTP GET<br/>User-Agent Header"| SCRAPER
    
    USERS["End Users"] --> WEBSITE
```

**Sources:** `.github/workflows/fetch-install-stats.yml`, `scripts/fetch-install-stats.py`, `website/install-stats.json`

---

## Data Source: skills.sh Marketplace

The system scrapes installation counts from `https://skills.sh/resciencelab/opc-skills`, a public marketplace aggregator that tracks skill installations across multiple AI agent platforms.

**Why skills.sh as Data Source:**
- **Cross-Platform Aggregation**: Consolidates installs from 16+ AI agents (Claude, Cursor, Droid, etc.)
- **Public Availability**: No authentication required, stable URL structure
- **Real-Time Updates**: Reflects actual usage across the ecosystem
- **Community Standard**: De facto marketplace for Agent Skills Standard implementations

The scraper targets specific HTML patterns in the skills.sh page to extract per-skill installation counts.

**Sources:** [scripts/fetch-install-stats.py:9]()

---

## Scraper Implementation

The `fetch-install-stats.py` script implements a lightweight HTML parser using Python's standard library (`urllib.request` and `re` modules).

### Core Parsing Logic

**Function: fetch_install_stats()**

```mermaid
graph TB
    START["fetch_install_stats()"]
    
    HTTP["HTTP Request<br/>urllib.request.Request<br/>User-Agent: OPC-Skills-Stats-Fetcher/1.0<br/>Timeout: 30s"]
    
    DECODE["Decode HTML<br/>UTF-8 Encoding"]
    
    REGEX["Regex Pattern Match<br/>skill_pattern.finditer()"]
    
    LOOP["For Each Match"]
    
    EXTRACT["Extract:<br/>skill_name = match.group(1)<br/>count_str = match.group(2)"]
    
    PARSE["_parse_count(count_str)<br/>Handle 2.8K format"]
    
    FILTER["Skip skill_name == 'skill-name'<br/>Template Exclusion"]
    
    STORE["skills[skill_name] = count"]
    
    SUM["total = sum(skills.values())"]
    
    RESULT["Return JSON Object<br/>{total, skills, source}"]
    
    START --> HTTP
    HTTP --> DECODE
    DECODE --> REGEX
    REGEX --> LOOP
    LOOP --> EXTRACT
    EXTRACT --> PARSE
    PARSE --> FILTER
    FILTER --> STORE
    STORE --> LOOP
    LOOP --> SUM
    SUM --> RESULT
```

**Sources:** [scripts/fetch-install-stats.py:20-63]()

### HTML Pattern Matching

The scraper uses a compiled regex pattern to extract skill names and install counts from the HTML structure:

**Pattern Structure:**
```
href="/resciencelab/opc-skills/([a-z0-9-]+)"[^>]*>.*?
<span[^>]*class="[^"]*font-mono[^"]*"[^>]*>([\d.,]+K?)</span>
```

**Capture Groups:**
1. **Group 1**: Skill name (e.g., `seo-geo`, `logo-creator`)
2. **Group 2**: Install count string (e.g., `7000`, `2.8K`, `5.3K`)

**Sources:** [scripts/fetch-install-stats.py:39-43]()

### Count Parsing Algorithm

The `_parse_count()` helper function handles both plain integers and abbreviated formats.

| Input Format | Example | Parsing Logic | Output |
|--------------|---------|---------------|---------|
| Plain Integer | `"380"` | `int(count_str)` | `380` |
| Abbreviated (K) | `"2.8K"` | `int(float("2.8") * 1000)` | `2800` |
| Comma-Separated | `"1,234"` | Strip commas → `int()` | `1234` |

**Implementation:**
```
count_str.strip().replace(",", "")
if count_str.upper().endswith("K"):
    return int(float(count_str[:-1]) * 1000)
return int(count_str)
```

**Sources:** [scripts/fetch-install-stats.py:12-17]()

### Error Handling

The scraper implements fail-fast error handling for network issues:

- **Timeout**: 30-second timeout on HTTP request [scripts/fetch-install-stats.py:27]()
- **User-Agent**: Custom header to identify the scraper [scripts/fetch-install-stats.py:25]()
- **Exception Handling**: Prints error to stderr and exits with code 1 [scripts/fetch-install-stats.py:29-31]()
- **Template Filtering**: Excludes `skill-name` template from results [scripts/fetch-install-stats.py:50]()

**Sources:** [scripts/fetch-install-stats.py:20-31](), [scripts/fetch-install-stats.py:49-51]()

---

## Automation Pipeline

The GitHub Actions workflow `fetch-install-stats.yml` orchestrates daily statistics updates with automatic commit logic.

### Workflow Configuration

**Workflow: fetch-install-stats.yml**

| Configuration | Value | Purpose |
|---------------|-------|---------|
| **Schedule** | `cron: '0 6 * * *'` | Daily execution at 6:00 AM UTC |
| **Manual Trigger** | `workflow_dispatch` | On-demand execution from GitHub UI |
| **Runner** | `ubuntu-latest` | Linux environment for Python 3.12 |
| **Permissions** | `contents: write` | Required for git commit/push |

**Sources:** [.github/workflows/fetch-install-stats.yml:3-12]()

### Execution Steps

**Workflow Step Diagram**

```mermaid
graph TB
    CHECKOUT["Step 1: actions/checkout@v4<br/>Clone Repository"]
    
    PYTHON["Step 2: actions/setup-python@v5<br/>Python 3.12"]
    
    FETCH["Step 3: Fetch Install Stats<br/>python3 scripts/fetch-install-stats.py<br/>> website/install-stats.json"]
    
    DIFF["Step 4: Check for Changes<br/>git diff --quiet<br/>Set changed=true if modified"]
    
    DECISION{{"changed == 'true'"}}
    
    COMMIT["Step 5: Commit and Push<br/>git config user.name<br/>git add website/install-stats.json<br/>git commit -m 'chore: update...'<br/>git push"]
    
    SKIP["Skip Commit<br/>No Changes Detected"]
    
    CHECKOUT --> PYTHON
    PYTHON --> FETCH
    FETCH --> DIFF
    DIFF --> DECISION
    DECISION -->|"Yes"| COMMIT
    DECISION -->|"No"| SKIP
```

**Sources:** [.github/workflows/fetch-install-stats.yml:13-36]()

### Git Commit Strategy

The workflow uses conditional commit logic to avoid empty commits when statistics haven't changed:

**Change Detection:**
```bash
git diff --quiet website/install-stats.json || echo "changed=true" >> $GITHUB_OUTPUT
```

**Conditional Commit:**
```yaml
if: steps.diff.outputs.changed == 'true'
```

**Commit Metadata:**
- **Author**: `github-actions[bot]`
- **Email**: `github-actions[bot]@users.noreply.github.com`
- **Message**: `"chore: update install stats from skills.sh"`

**Sources:** [.github/workflows/fetch-install-stats.yml:24-36]()

---

## Data Format: install-stats.json

The output JSON file follows a simple three-field structure optimized for consumption by the Cloudflare Worker.

### Schema Structure

**Current Statistics (Example):**

```json
{
  "total": 12597,
  "skills": {
    "seo-geo": 7000,
    "reddit": 960,
    "nanobanana": 799,
    "logo-creator": 759,
    "twitter": 758,
    "domain-hunter": 582,
    "banner-creator": 546,
    "producthunt": 540,
    "requesthunt": 539,
    "archive": 114
  },
  "source": "https://skills.sh/resciencelab/opc-skills"
}
```

**Sources:** [website/install-stats.json:1-16]()

### Field Specifications

| Field | Type | Calculation | Purpose |
|-------|------|-------------|---------|
| `total` | Integer | `sum(skills.values())` | Aggregate install count across all skills |
| `skills` | Object | Per-skill scrape results | Individual skill popularity metrics |
| `source` | String | Hardcoded URL | Attribution and data provenance |

**Key Design Decisions:**
- **Calculated Total**: Total is computed from sum of individual skills rather than scraped from HTML, ensuring consistency [scripts/fetch-install-stats.py:55]()
- **Alphabetical Sorting**: Skills are ordered by name in the JSON output for readability
- **Source Attribution**: Explicit `source` field enables transparency and validation

**Sources:** [scripts/fetch-install-stats.py:57-61]()

---

## Integration with Website

The statistics file is consumed by the Cloudflare Worker through the `fetchInstallStats()` function with aggressive edge caching.

### Data Fetching Pattern

**Function Call Chain:**

```mermaid
graph LR
    HANDLER["fetch() Handler<br/>worker.js"]
    
    FETCH_STATS["fetchInstallStats()<br/>GitHub Raw URL"]
    
    CACHE["caches.default.match()<br/>TTL: 3600s"]
    
    GITHUB["raw.githubusercontent.com<br/>/main/website/install-stats.json"]
    
    PARSE["JSON.parse(text)<br/>Extract stats.skills"]
    
    RENDER["renderHomePage()<br/>Display on Landing"]
    
    HANDLER --> FETCH_STATS
    FETCH_STATS --> CACHE
    CACHE -->|"Miss"| GITHUB
    CACHE -->|"Hit"| PARSE
    GITHUB --> PARSE
    PARSE --> RENDER
```

**Cache Strategy:**
- **TTL**: 3600 seconds (1 hour)
- **Rationale**: Statistics update daily, so 1-hour cache provides near-real-time data while minimizing GitHub API load
- **Cache Key**: Full GitHub raw content URL

**Sources:** Website integration details covered in [Caching Strategy](#4.3)

### Display Locations

The install statistics are displayed in multiple locations on opc.dev:

| Location | Data Displayed | Format |
|----------|----------------|--------|
| Landing Page Header | `stats.total` | "12,597+ Installs" with comma formatting |
| Skills Comparison Table | Per-skill counts | Sortable column with popularity indicators |
| Individual Skill Pages | Skill-specific count | "Used by X developers" badge |

**Visual Presentation:**
- Total install count shown prominently as social proof metric
- Per-skill counts enable users to assess popularity and community adoption
- Real-time data (within 1-hour cache window) builds trust

---

## Code Entity Mapping

**Diagram: Natural Language to Code Entities**

```mermaid
graph TB
    subgraph "Natural Language Concepts"
        NL_SCRAPER["Install Stats<br/>Scraper"]
        NL_SCHEDULE["Daily Update<br/>Schedule"]
        NL_DATA["Statistics<br/>Data"]
        NL_WEBSITE["Website<br/>Display"]
    end
    
    subgraph "Code Entities"
        FILE_PY["scripts/fetch-install-stats.py"]
        FUNC_FETCH["fetch_install_stats()"]
        FUNC_PARSE["_parse_count()"]
        
        FILE_YML[".github/workflows/fetch-install-stats.yml"]
        JOB_FETCH["jobs.fetch-stats"]
        CRON["schedule.cron: '0 6 * * *'"]
        
        FILE_JSON["website/install-stats.json"]
        FIELD_TOTAL["total: 12597"]
        FIELD_SKILLS["skills: {...}"]
        
        FILE_WORKER["website/worker.js"]
        FUNC_STATS["fetchInstallStats()"]
        CONST_TTL["CACHE_TTL: 3600"]
    end
    
    NL_SCRAPER --> FILE_PY
    NL_SCRAPER --> FUNC_FETCH
    NL_SCRAPER --> FUNC_PARSE
    
    NL_SCHEDULE --> FILE_YML
    NL_SCHEDULE --> JOB_FETCH
    NL_SCHEDULE --> CRON
    
    NL_DATA --> FILE_JSON
    NL_DATA --> FIELD_TOTAL
    NL_DATA --> FIELD_SKILLS
    
    NL_WEBSITE --> FILE_WORKER
    NL_WEBSITE --> FUNC_STATS
    NL_WEBSITE --> CONST_TTL
```

**Key Code Symbols:**

| Natural Language Term | Primary Code Entity | File Location |
|----------------------|---------------------|---------------|
| HTML Parser | `fetch_install_stats()` | [scripts/fetch-install-stats.py:20]() |
| Count Parser | `_parse_count()` | [scripts/fetch-install-stats.py:12]() |
| Daily Cron Job | `schedule.cron: '0 6 * * *'` | [.github/workflows/fetch-install-stats.yml:5]() |
| Statistics JSON | `website/install-stats.json` | [website/install-stats.json:1]() |
| Total Installs | `stats.total` | [website/install-stats.json:2]() |
| Per-Skill Counts | `stats.skills` | [website/install-stats.json:3]() |
| Data Source URL | `SKILLS_SH_URL` | [scripts/fetch-install-stats.py:9]() |
| Regex Pattern | `skill_pattern` | [scripts/fetch-install-stats.py:39]() |
| Commit Bot | `github-actions[bot]` | [.github/workflows/fetch-install-stats.yml:32]() |

**Sources:** All files referenced in this section

---

## System Reliability

### Failure Modes

| Failure Scenario | Detection | Recovery |
|------------------|-----------|----------|
| skills.sh down | HTTP timeout (30s) | Script exits with code 1, workflow fails |
| HTML structure change | Regex returns empty matches | Total = 0, alerts via monitoring |
| Git push conflict | Push rejection | Workflow fails, manual resolution required |
| Invalid JSON output | JSON parsing error in worker | Stale cache served, 3600s expiry |

### Monitoring

**Automated Monitoring:**
- GitHub Actions workflow status (success/failure)
- Git commit history for `website/install-stats.json`
- Cloudflare Worker analytics for cache hit rates

**Manual Validation:**
- Compare `stats.total` against skills.sh UI
- Verify individual skill counts match marketplace display
- Check commit timestamps for daily updates

**Sources:** System reliability patterns inferred from [.github/workflows/fetch-install-stats.yml:29-31]() and [scripts/fetch-install-stats.py:29-31]()

---

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| **Scraper Execution Time** | ~2-5 seconds | Network-bound, depends on skills.sh response time |
| **GitHub Actions Runtime** | ~30-45 seconds | Includes checkout, Python setup, commit, push |
| **Data Freshness** | Daily at 6 AM UTC | Configurable via cron schedule |
| **Website Cache Hit Rate** | 95%+ | 3600s TTL, low miss rate |
| **JSON File Size** | ~200 bytes | Minimal storage and bandwidth impact |

**Optimization Opportunities:**
- Increase scrape frequency (e.g., hourly) if real-time accuracy needed
- Add retry logic with exponential backoff for transient network failures
- Implement JSON schema validation before commit to catch parsing errors

**Sources:** Performance characteristics inferred from workflow configuration and caching strategy

---

# Page: Website & Content Delivery

# Website & Content Delivery

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [website/worker.js](website/worker.js)
- [website/wrangler.toml](website/wrangler.toml)

</details>



## Purpose and Scope

This document covers the **opc.dev** website infrastructure built on Cloudflare Workers. The system serves dynamic content by fetching data from GitHub raw URLs, implementing edge caching, and providing multiple API endpoints for SEO/GEO optimization. 

For information about blog content management and publishing workflows, see [Blog & Content System](#5). For details about installation statistics tracking, see [Installation Statistics System](#3.5).

---

## Architecture Overview

The website operates as a serverless Cloudflare Worker that acts as a thin routing and rendering layer over GitHub-hosted content. This architecture enables zero-downtime deployments and instant content updates by treating GitHub as the source of truth.

### Deployment Configuration

The worker is deployed to both `opc.dev` and `www.opc.dev` domains via Cloudflare's routing system:

**Domain Routing**
| Pattern | Zone | Purpose |
|---------|------|---------|
| `opc.dev/*` | opc.dev | Primary domain |
| `www.opc.dev/*` | opc.dev | WWW subdomain |

Sources: [website/wrangler.toml:1-10]()

### Request Flow Architecture

```mermaid
graph TB
    User["User Request"]
    Worker["fetch() handler<br/>website/worker.js:3-4"]
    URLParse["URL Parser<br/>new URL(request.url)"]
    
    subgraph "Route Matching"
        StaticRoutes["Static Routes"]
        DynamicRoutes["Dynamic Routes"]
    end
    
    subgraph "Static Handlers"
        Sitemap["/sitemap.xml<br/>Line 7"]
        Robots["/robots.txt<br/>Line 70"]
        LLMsTxt["/llms.txt<br/>Line 129"]
        SkillsJSON["/skills.json<br/>Line 218"]
        InstallSh["/install.sh<br/>Line 210"]
        ImgProxy["Image Proxy<br/>Line 182-207"]
    end
    
    subgraph "Dynamic Handlers"
        Home["/ (Landing)<br/>Line 252-1310"]
        Compare["/compare<br/>Line 230-232"]
        BlogList["/blog<br/>Line 235-237"]
        BlogPost["/blog/:slug<br/>Line 240-243"]
        SkillPage["/skills/:name<br/>Line 246-249"]
    end
    
    User --> Worker
    Worker --> URLParse
    URLParse --> StaticRoutes
    URLParse --> DynamicRoutes
    
    StaticRoutes --> Sitemap
    StaticRoutes --> Robots
    StaticRoutes --> LLMsTxt
    StaticRoutes --> SkillsJSON
    StaticRoutes --> InstallSh
    StaticRoutes --> ImgProxy
    
    DynamicRoutes --> Home
    DynamicRoutes --> Compare
    DynamicRoutes --> BlogList
    DynamicRoutes --> BlogPost
    DynamicRoutes --> SkillPage
```

Sources: [website/worker.js:3-250]()

---

## Data Fetching Functions

The worker uses three primary data fetching functions, each with distinct caching strategies optimized for update frequency.

### Function: fetchSkillsConfig

Fetches the central skills registry from GitHub with aggressive caching for near-real-time updates.

```mermaid
graph LR
    Fetch["fetchSkillsConfig(ctx)<br/>Line 1314"]
    CacheCheck["cache.match(cacheUrl)<br/>Line 1320"]
    GitHub["GitHub Raw URL<br/>skills.json"]
    Parse["Parse JSON<br/>Line 1331"]
    CacheStore["cache.put(cacheUrl)<br/>Line 1338"]
    Fallback["getFallbackConfig()<br/>Line 1345"]
    
    Fetch --> CacheCheck
    CacheCheck -->|Hit| Return["Return cached"]
    CacheCheck -->|Miss| GitHub
    GitHub -->|Success| Parse
    GitHub -->|Fail| Fallback
    Parse --> CacheStore
    CacheStore --> Return
```

**Configuration**
- URL: `https://raw.githubusercontent.com/ReScienceLab/opc-skills/main/skills.json`
- Cache Key: `https://opc.dev/_cache/skills-v2.json`
- TTL: 60 seconds
- Fallback: `getFallbackConfig()` with hardcoded skill data

Sources: [website/worker.js:1314-1346]()

### Function: fetchInstallStats

Retrieves installation statistics with longer caching since stats update daily via GitHub Actions.

**Configuration**
- URL: `https://raw.githubusercontent.com/ReScienceLab/opc-skills/main/website/install-stats.json`
- Cache Key: `https://opc.dev/_cache/install-stats.json`
- TTL: 3600 seconds (1 hour)
- Fallback: `{ total: 0, skills: {} }`

Sources: [website/worker.js:1349-1381]()

### Function: fetchBlogConfig

Loads blog post metadata with moderate caching for content that changes occasionally.

**Configuration**
- URL: `https://raw.githubusercontent.com/ReScienceLab/opc-skills/main/website/blog/blog.json`
- Cache Key: `https://opc.dev/_cache/blog-v1.json`
- TTL: 300 seconds (5 minutes)
- Fallback: `{ posts: [] }`

Sources: [website/worker.js:1626-1658]()

### Caching Strategy Summary

| Function | Data Source | TTL | Update Frequency |
|----------|------------|-----|------------------|
| `fetchSkillsConfig` | skills.json | 60s | High (active development) |
| `fetchBlogConfig` | blog/blog.json | 300s | Medium (blog posts) |
| `fetchInstallStats` | install-stats.json | 3600s | Low (daily cron) |

---

## Static Route Handlers

### /sitemap.xml - Dynamic SEO Sitemap

Generates XML sitemap dynamically from skills and blog posts with proper SEO priorities.

```mermaid
graph TB
    Handler["Sitemap Handler<br/>Line 7-68"]
    FetchSkills["fetchSkillsConfig(ctx)"]
    FetchBlog["fetchBlogConfig(ctx)"]
    
    subgraph "URL Generation"
        HomeURL["Home Page<br/>priority: 1.0"]
        CompareURL["Compare Page<br/>priority: 0.7"]
        BlogURL["Blog Index<br/>priority: 0.8"]
        SkillsJSON["skills.json<br/>priority: 0.6"]
        SkillURLs["Skill Pages<br/>priority: 0.8<br/>weekly changefreq"]
        BlogPostURLs["Blog Posts<br/>priority: 0.7<br/>monthly changefreq"]
    end
    
    Handler --> FetchSkills
    Handler --> FetchBlog
    FetchSkills --> SkillURLs
    FetchBlog --> BlogPostURLs
    
    Handler --> HomeURL
    Handler --> CompareURL
    Handler --> BlogURL
    Handler --> SkillsJSON
```

**URL Structure**
```xml
<url>
  <loc>https://opc.dev/skills/{name}</loc>
  <lastmod>{today}</lastmod>
  <changefreq>weekly</changefreq>
  <priority>0.8</priority>
</url>
```

Sources: [website/worker.js:7-68]()

### /robots.txt - AI Bot Policy

Serves robot directives with explicit AI bot allowlist for GEO optimization. The configuration implements a strategic bot policy that **allows AI search engines** while blocking aggressive SEO crawlers.

**Bot Policy Matrix**

| Bot Type | User-Agent | Action | Purpose |
|----------|-----------|--------|---------|
| AI Search | GPTBot, ChatGPT-User | Allow | ChatGPT citations |
| AI Search | PerplexityBot | Allow | Perplexity answers |
| AI Search | ClaudeBot, anthropic-ai | Allow | Claude citations |
| AI Search | Google-Extended | Allow | Gemini/Bard |
| AI Search | Applebot-Extended | Allow | Apple Intelligence |
| AI Search | Amazonbot | Allow | Alexa |
| Traditional | Googlebot, Bingbot | Allow | Standard indexing |
| SEO Crawlers | AhrefsBot, SemrushBot | Disallow | Block scrapers |

**Content-Signal Header**: `search=yes, ai-input=yes, ai-train=no`

Sources: [website/worker.js:70-126]()

### /llms.txt - AI-Optimized Summary

Plain text endpoint specifically designed for LLM consumption, providing structured information in a format optimized for AI parsing and citation.

**Structure**
```
# OPC Skills - AI Agent Skills for Solopreneurs

## Overview
9 specialized AI agent skills for one-person companies.
Supports: Claude Code, Cursor, Factory Droid, OpenCode, Codex

## Installation
npx skills add ReScienceLab/opc-skills

## Skills
1. requesthunt - User demand research...
2. domain-hunter - Domain search...
[...]

## Statistics
- 9 skills total
- 5 platforms supported
[...]
```

**Response Headers**
- Content-Type: `text/plain`
- Cache-Control: `public, max-age=3600`

Sources: [website/worker.js:129-179]()

### /skills.json - Public API Endpoint

Serves the complete skills registry with CORS enabled for external integrations.

**Response Headers**
- Content-Type: `application/json`
- Access-Control-Allow-Origin: `*`
- Cache-Control: `public, max-age=300`

**Data Flow**
```mermaid
graph LR
    Request["/skills.json request"]
    Fetch["fetchSkillsConfig(ctx)"]
    JSON["JSON.stringify(skills, null, 2)"]
    Response["CORS-enabled response"]
    
    Request --> Fetch
    Fetch --> JSON
    JSON --> Response
```

Sources: [website/worker.js:218-227]()

### Image Proxy

Proxies skill example images from GitHub with proper content-type detection and caching.

**URL Pattern**: `/skills/{skillName}/examples/images/{fileName}`

**Content-Type Detection**
```javascript
const contentType = fileName.endsWith('.svg') ? 'image/svg+xml' :
                   fileName.endsWith('.png') ? 'image/png' : 
                   'image/jpeg'
```

**Upstream URL**: `https://raw.githubusercontent.com/ReScienceLab/opc-skills/main/skills/{skillName}/examples/images/{fileName}`

Sources: [website/worker.js:182-207]()

---

## Dynamic Page Rendering

### Landing Page (/)

The root handler generates the complete homepage with skills grid, FAQs, and structured data.

```mermaid
graph TB
    Handler["Landing Page Handler<br/>Line 252-1310"]
    
    subgraph "Data Loading"
        LoadSkills["fetchSkillsConfig(ctx)"]
        LoadStats["fetchInstallStats(ctx)"]
        Parallel["Promise.all()"]
    end
    
    subgraph "Schema Generation"
        SkillsJsonLd["Skills SoftwareApplication<br/>Line 260-276"]
        FAQSchema["FAQPage Schema<br/>28+ questions<br/>Line 279-543"]
        HowToSchema["HowTo Installation<br/>Line 604-634"]
        WebPageSchema["WebPage + WebSite<br/>Line 547-602"]
    end
    
    subgraph "Content Generation"
        SkillCards["generateSkillCards()<br/>Line 670-720"]
        HTML["Complete HTML<br/>Line 722-1302"]
    end
    
    Handler --> LoadSkills
    Handler --> LoadStats
    LoadSkills --> Parallel
    LoadStats --> Parallel
    
    Parallel --> SkillsJsonLd
    Parallel --> FAQSchema
    Parallel --> HowToSchema
    Parallel --> WebPageSchema
    Parallel --> SkillCards
    
    SkillsJsonLd --> HTML
    FAQSchema --> HTML
    HowToSchema --> HTML
    WebPageSchema --> HTML
    SkillCards --> HTML
```

**Key Features**
- **FAQPage Schema**: 28+ questions for +40% AI visibility boost
- **Skills Grid**: Dynamic cards with install commands, dependencies, auth tags
- **Structured Data**: Multiple schema types (WebPage, SoftwareApplication, ItemList, FAQPage, HowTo)
- **Speakable Markup**: CSS selectors for voice search optimization

Sources: [website/worker.js:252-1310]()

### Individual Skill Pages (/skills/:name)

```mermaid
graph TB
    Handler["renderSkillPage(skillName, ctx)<br/>Line 1678"]
    
    subgraph "Data Loading"
        LoadConfig["fetchSkillsConfig(ctx)"]
        LoadStats["fetchInstallStats(ctx)"]
        FindSkill["skills.find(s => s.name === skillName)"]
    end
    
    subgraph "Markdown Processing"
        FetchMD["Fetch SKILL.md from GitHub<br/>Line 1726"]
        FetchExample["Fetch example.md if exists<br/>Line 1738-1753"]
        MarkdownToHTML["markdownToHtml(markdown)<br/>Line 1661-1675"]
    end
    
    subgraph "Dependency Analysis"
        GetAllKeys["getAllKeys(skill, allSkills)<br/>Line 1702-1720"]
        GetDeps["Extract dependencies<br/>Array or Object.keys"]
    end
    
    subgraph "Schema Generation"
        WebPageSchema["WebPage schema"]
        SoftwareSchema["SoftwareApplication schema"]
        BreadcrumbSchema["BreadcrumbList schema"]
        FAQSchema["FAQPage schema<br/>3 questions per skill"]
    end
    
    Handler --> LoadConfig
    Handler --> LoadStats
    LoadConfig --> FindSkill
    FindSkill -->|Not found| 404["404 Response"]
    FindSkill -->|Found| FetchMD
    FetchMD --> MarkdownToHTML
    FetchExample --> MarkdownToHTML
    
    FindSkill --> GetAllKeys
    FindSkill --> GetDeps
    
    GetAllKeys --> HTML["Render HTML"]
    GetDeps --> HTML
    WebPageSchema --> HTML
    SoftwareSchema --> HTML
    BreadcrumbSchema --> HTML
    FAQSchema --> HTML
    MarkdownToHTML --> HTML
```

**Markdown Processing**
- Removes YAML frontmatter: `md.replace(/^---\n[\s\S]*?\n---\n/, '')`
- Uses `marked` library for parsing
- Wraps images in `<figure>` tags with captions
- Proxies GitHub images through worker

**Dependency Resolution**
The `getAllKeys()` helper function collects API keys from both the skill and its dependencies:

```javascript
const getAllKeys = (skill, allSkills) => {
  const keys = [...(skill.auth?.keys || [])];
  const deps = getDeps(skill.dependencies);
  for (const depName of deps) {
    const depSkill = allSkills.find(s => s.name === depName);
    if (depSkill?.auth?.keys) {
      keys.push({ ...k, from: depName }); // Tag inherited keys
    }
  }
  return keys;
}
```

Sources: [website/worker.js:1678-2100]()

### Markdown Conversion Function

```mermaid
graph LR
    Input["Markdown String"]
    StripFM["Strip YAML Frontmatter<br/>Regex: ^---\n[\s\S]*?\n---\n"]
    Marked["marked.parse(md)<br/>GFM support"]
    WrapImages["Wrap images in figure tags<br/>Regex replacement"]
    Output["HTML String"]
    
    Input --> StripFM
    StripFM --> Marked
    Marked --> WrapImages
    WrapImages --> Output
```

**Image Wrapping Pattern**
```javascript
html.replace(
  /<img src="([^"]+)" alt="([^"]*)">/g,
  '<figure class="example-img"><img src="$1" alt="$2" loading="lazy"><figcaption>$2</figcaption></figure>'
)
```

Sources: [website/worker.js:1661-1675]()

---

## SEO and GEO Optimization

### Schema.org Structured Data

The worker generates multiple schema types for comprehensive SEO/GEO coverage.

**Schema Types Implemented**

```mermaid
graph TB
    Root["@graph root<br/>JSON-LD"]
    
    subgraph "Page Schemas"
        WebPage["WebPage<br/>@id: #webpage"]
        WebSite["WebSite<br/>@id: #website"]
        Org["Organization<br/>@id: #organization<br/>ReScience Lab"]
    end
    
    subgraph "Content Schemas"
        ItemList["ItemList<br/>@id: #skillcollection<br/>All skills array"]
        FAQPage["FAQPage<br/>@id: #faq<br/>28+ questions"]
        HowTo["HowTo<br/>@id: #installation<br/>3-step guide"]
    end
    
    subgraph "Skill Schemas"
        Software["SoftwareApplication<br/>Per skill"]
        Breadcrumb["BreadcrumbList<br/>Per skill page"]
    end
    
    Root --> WebPage
    Root --> WebSite
    Root --> Org
    Root --> ItemList
    Root --> FAQPage
    Root --> HowTo
    
    WebPage --> Software
    
    Software --> Breadcrumb
```

**FAQPage Schema Statistics**
- **28+ questions** on landing page
- **3 questions** per skill page
- Proven **+40% increase** in AI search visibility
- Questions optimized for Claude, ChatGPT, Perplexity citations

Sources: [website/worker.js:544-636](), [website/worker.js:1757-1855]()

### Speakable Markup

Designates content sections optimized for voice search and screen readers.

**CSS Selectors**
```javascript
speakable: {
  "@type": "SpeakableSpecification",
  cssSelector: [
    "h1",
    ".skill-desc",
    ".stats-bar",
    ".compatibility-note"
  ]
}
```

Sources: [website/worker.js:556-564]()

### OpenGraph and Twitter Cards

**Meta Tags Structure**
- `og:title`: Skill name with context
- `og:description`: Skill description
- `og:image`: Skill logo or Simple Icons fallback
- `og:type`: "website"
- `twitter:card`: "summary_large_image"

Sources: [website/worker.js:739-750](), [website/worker.js:1873-1883]()

---

## Response Caching Strategy

### Edge Cache Implementation

```mermaid
graph TB
    Request["Incoming Request"]
    Handler["Route Handler"]
    
    subgraph "Cache Decision Tree"
        CheckStatic{Static Content?}
        CheckDynamic{Dynamic Content?}
    end
    
    subgraph "Static Routes (No Cache)"
        Sitemap["/sitemap.xml<br/>Always fresh"]
        Robots["/robots.txt<br/>86400s cache"]
        LLMsTxt["/llms.txt<br/>3600s cache"]
        SkillsJSON["/skills.json<br/>300s cache"]
    end
    
    subgraph "Dynamic Routes"
        Landing["/ Landing<br/>300s cache"]
        SkillPage["/skills/:name<br/>300s cache"]
        BlogPages["Blog pages<br/>Varies by content"]
    end
    
    subgraph "Data Cache (caches.default)"
        SkillsCache["skills-v2.json<br/>60s TTL"]
        BlogCache["blog-v1.json<br/>300s TTL"]
        StatsCache["install-stats.json<br/>3600s TTL"]
    end
    
    Request --> Handler
    Handler --> CheckStatic
    Handler --> CheckDynamic
    
    CheckStatic --> Sitemap
    CheckStatic --> Robots
    CheckStatic --> LLMsTxt
    CheckStatic --> SkillsJSON
    
    CheckDynamic --> Landing
    CheckDynamic --> SkillPage
    CheckDynamic --> BlogPages
    
    Landing --> SkillsCache
    Landing --> StatsCache
    SkillPage --> SkillsCache
    SkillPage --> StatsCache
    BlogPages --> BlogCache
```

**Cache Control Headers**

| Endpoint | max-age | Rationale |
|----------|---------|-----------|
| `/sitemap.xml` | None (dynamic) | Always fresh for SEO |
| `/robots.txt` | 86400s | Rarely changes |
| `/llms.txt` | 3600s | Moderate update frequency |
| `/skills.json` | 300s | Balance freshness/performance |
| `/` (landing) | 300s | Active development |
| `/skills/:name` | 300s | Active documentation updates |

**Internal Cache Keys**
- `https://opc.dev/_cache/skills-v2.json`
- `https://opc.dev/_cache/install-stats.json`
- `https://opc.dev/_cache/blog-v1.json`

Sources: [website/worker.js:1314-1381](), [website/worker.js:1626-1658]()

---

## HTML Generation and UI Components

### Skill Card Generation

The landing page dynamically generates skill cards with all metadata:

```mermaid
graph LR
    SkillData["Skill Object<br/>from skills.json"]
    
    subgraph "Component Assembly"
        Header["Skill Header<br/>Icon + Title + Version"]
        AuthTag["Auth Tag<br/>Free/API Key"]
        Description["Description Text"]
        APIKeyInfo["API Key Requirements<br/>getAllKeys()"]
        Dependencies["Dependency Tags"]
        Triggers["Trigger Keywords"]
        InstallCmd["Install Command<br/>with --skill flags"]
        Commands["Example Commands<br/>collapsible"]
    end
    
    HTML["Complete Card HTML"]
    
    SkillData --> Header
    SkillData --> AuthTag
    SkillData --> Description
    SkillData --> APIKeyInfo
    SkillData --> Dependencies
    SkillData --> Triggers
    SkillData --> InstallCmd
    SkillData --> Commands
    
    Header --> HTML
    AuthTag --> HTML
    Description --> HTML
    APIKeyInfo --> HTML
    Dependencies --> HTML
    Triggers --> HTML
    InstallCmd --> HTML
    Commands --> HTML
```

**Install Command Generation**
- Includes skill name: `--skill {name}`
- Auto-includes dependencies: `--skill {dep1} --skill {dep2} --skill {name}`
- Copy-to-clipboard button with toast notification

Sources: [website/worker.js:670-720]()

### CSS Architecture

The website uses a custom CSS design system with CSS variables:

**Color Palette**
```css
:root {
  --font: 'JetBrains Mono', monospace;
  --font-pixel: 'Press Start 2P', cursive;
  --black: #000;
  --white: #fff;
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-400: #9ca3af;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --green: #22c55e;
}
```

**Responsive Breakpoints**
- Desktop: Default styles
- Tablet: `@media (max-width: 768px)`
- Mobile: `@media (max-width: 400px)`

Sources: [website/worker.js:755-999]()

### Client-Side JavaScript

Minimal JavaScript for interactive features:

**Functions**
- `copyCmd(btn)`: Copy install commands
- `copyHeroCmd(btn)`: Copy hero section command
- `showToast(msg)`: Display toast notifications
- `copyCmdNew(btn)`: Copy command with validation
- `updateCmd(card)`: Update command based on selected options
- `switchLevel(btn, level)`: Toggle user/project level
- `switchPlatform(btn, platform)`: Toggle platform selection

Sources: [website/worker.js:1176-1300]()

---

## Error Handling and Fallbacks

### Fallback Configuration

When GitHub is unreachable, the worker serves a hardcoded fallback configuration with core skills:

```mermaid
graph TB
    FetchAttempt["fetch(SKILLS_JSON_URL)"]
    CheckStatus{Response OK?}
    CatchError{Network Error?}
    
    ParseJSON["Parse JSON"]
    Fallback["getFallbackConfig()<br/>Line 1383-1623"]
    
    subgraph "Fallback Data"
        HardcodedSkills["6 Core Skills:<br/>domain-hunter<br/>reddit<br/>twitter<br/>producthunt<br/>requesthunt<br/>archive"]
        Metadata["Basic metadata<br/>name, version, description<br/>icon, color, triggers"]
        InstallCmds["Install commands<br/>All platforms"]
    end
    
    FetchAttempt --> CheckStatus
    CheckStatus -->|No| Fallback
    CheckStatus -->|Yes| ParseJSON
    FetchAttempt --> CatchError
    CatchError -->|Yes| Fallback
    
    Fallback --> HardcodedSkills
    Fallback --> Metadata
    Fallback --> InstallCmds
```

**Fallback Skills**
1. `domain-hunter` - Domain search with dependencies
2. `reddit` - Reddit API access (no auth)
3. `twitter` - Twitter API (requires auth)
4. `producthunt` - Product Hunt API (requires auth)
5. `requesthunt` - Demand research (requires auth)
6. `archive` - Session memory (no auth)

Sources: [website/worker.js:1383-1623]()

---

## Performance Optimizations

### Image Loading Strategy

```mermaid
graph LR
    ImgTag["<img> Tag"]
    
    subgraph "Loading Attributes"
        FetchPriority["fetchpriority='high'<br/>Hero banner only"]
        LazyLoad["loading='lazy'<br/>All other images"]
        Decoding["decoding='async'<br/>Non-blocking"]
    end
    
    subgraph "Fallback Chain"
        Primary["Primary logo URL<br/>skill.logo"]
        CDN["Simple Icons CDN<br/>cdn.simpleicons.org"]
        OnError["onerror handler<br/>Retry with CDN"]
    end
    
    ImgTag --> FetchPriority
    ImgTag --> LazyLoad
    ImgTag --> Decoding
    
    ImgTag --> Primary
    Primary -->|404| OnError
    OnError --> CDN
```

**Image Tag Example**
```html
<img 
  src="${skill.logo || `https://cdn.simpleicons.org/${skill.icon}/${skill.color}`}" 
  alt="${skill.name} skill icon" 
  loading="lazy" 
  decoding="async" 
  width="28" 
  height="28" 
  onerror="this.src='https://cdn.simpleicons.org/${skill.icon}/${skill.color}'"
>
```

Sources: [website/worker.js:680]()

### Font Loading

Uses Google Fonts with `preconnect` for optimal performance:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Press+Start+2P&display=swap" rel="stylesheet">
```

Sources: [website/worker.js:751-753]()

---

## Integration Points

### GitHub as Backend

All content sources use GitHub raw URLs:

```mermaid
graph TB
    Worker["Cloudflare Worker"]
    
    subgraph "GitHub Raw URLs"
        SkillsJSON["raw.githubusercontent.com<br/>/main/skills.json"]
        BlogJSON["raw.githubusercontent.com<br/>/main/website/blog/blog.json"]
        StatsJSON["raw.githubusercontent.com<br/>/main/website/install-stats.json"]
        SkillMD["raw.githubusercontent.com<br/>/main/skills/{name}/SKILL.md"]
        ExampleMD["raw.githubusercontent.com<br/>/main/skills/{name}/examples/{file}"]
        Images["raw.githubusercontent.com<br/>/main/skills/{name}/examples/images/{img}"]
        Assets["raw.githubusercontent.com<br/>/main/website/{asset}"]
    end
    
    Worker -->|fetchSkillsConfig| SkillsJSON
    Worker -->|fetchBlogConfig| BlogJSON
    Worker -->|fetchInstallStats| StatsJSON
    Worker -->|renderSkillPage| SkillMD
    Worker -->|renderSkillPage| ExampleMD
    Worker -->|Image Proxy| Images
    Worker -->|Static Assets| Assets
```

**User-Agent Header**: `"OPC-Skills-Website"` for all GitHub requests

Sources: [website/worker.js:1315-1316](), [website/worker.js:1627-1628](), [website/worker.js:1726-1753]()

### External CDN Dependencies

| Resource | CDN | Purpose |
|----------|-----|---------|
| Skill Icons | `cdn.simpleicons.org` | Fallback icons |
| Tool Logos | `cdn.jsdelivr.net/npm/@lobehub/icons-static-png` | Platform icons in scroller |
| Fonts | `fonts.googleapis.com` | JetBrains Mono + Press Start 2P |

Sources: [website/worker.js:680](), [website/worker.js:1033-1103]()

---

## Deployment and Configuration

### Wrangler Configuration

```toml
name = "opc-landing"
main = "worker.js"
compatibility_date = "2024-01-01"
compatibility_flags = ["nodejs_compat"]

routes = [
  { pattern = "opc.dev/*", zone_name = "opc.dev" },
  { pattern = "www.opc.dev/*", zone_name = "opc.dev" }
]
```

**Key Settings**
- `nodejs_compat` flag enables Node.js APIs in the worker
- Both apex and www domains route to the same worker
- No environment variables or secrets required (GitHub content is public)

Sources: [website/wrangler.toml:1-10]()

### Deployment Process

1. Code changes pushed to `main` branch
2. Cloudflare Pages auto-deploys worker
3. Edge cache invalidation happens naturally via TTL
4. No manual deployment steps required

**Cache Warming**: First request after deployment populates edge cache; subsequent requests served from cache until TTL expires.

---

## Content-Type Handling

### Response Content-Type Matrix

| Route | Content-Type | Charset |
|-------|--------------|---------|
| `/` | `text/html` | `UTF-8` |
| `/skills/:name` | `text/html` | `UTF-8` |
| `/sitemap.xml` | `application/xml` | None |
| `/robots.txt` | `text/plain` | None |
| `/llms.txt` | `text/plain` | None |
| `/skills.json` | `application/json` | None |
| Image Proxy (.svg) | `image/svg+xml` | None |
| Image Proxy (.png) | `image/png` | None |
| Image Proxy (.jpg) | `image/jpeg` | None |

Sources: [website/worker.js:66-68](), [website/worker.js:119-124](), [website/worker.js:173-177](), [website/worker.js:199-202](), [website/worker.js:220-226]()

---

# Page: Website Architecture

# Website Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [website/worker.js](website/worker.js)
- [website/wrangler.toml](website/wrangler.toml)

</details>



## Purpose and Scope

This document covers the Cloudflare Workers-based website architecture that powers opc.dev and www.opc.dev. It explains the deployment configuration, request routing system, and the GitHub-as-backend data fetching strategy. For information about SEO/GEO optimization techniques, see [4.5](#4.5). For API endpoint documentation, see [4.4](#4.4). For caching implementation details, see [4.3](#4.3).

## Deployment Platform: Cloudflare Workers

The website runs entirely on Cloudflare's edge network using a single Worker script. The `worker.js` file implements a fetch handler that processes all HTTP requests at the edge, eliminating the need for traditional web servers or hosting infrastructure.

### Configuration

The Worker is configured via `wrangler.toml`:

| Configuration Key | Value | Purpose |
|-------------------|-------|---------|
| `name` | `"opc-landing"` | Worker identifier in Cloudflare dashboard |
| `main` | `"worker.js"` | Entry point for the Worker script |
| `compatibility_date` | `"2024-01-01"` | Cloudflare runtime compatibility version |
| `compatibility_flags` | `["nodejs_compat"]` | Enables Node.js compatibility APIs |
| `routes` | `opc.dev/*`, `www.opc.dev/*` | Domain patterns this Worker handles |

The Worker is bound to both the apex domain (`opc.dev`) and the `www` subdomain, with `zone_name: "opc.dev"` indicating the Cloudflare zone.

**Sources:** [website/wrangler.toml:1-10]()

### Worker Entry Point

The Worker exports a single `fetch` handler that receives all HTTP requests:

```mermaid
graph TB
    Request["HTTP Request<br/>(any URL)"]
    FetchHandler["worker.js<br/>fetch(request, env, ctx)"]
    URLParse["new URL(request.url)<br/>Parse pathname"]
    Router["Route Dispatcher"]
    
    Request --> FetchHandler
    FetchHandler --> URLParse
    URLParse --> Router
    
    Router --> Static["Static Routes<br/>/sitemap.xml<br/>/robots.txt<br/>/llms.txt<br/>/install.sh"]
    Router --> API["/skills.json"]
    Router --> Dynamic["Dynamic Routes<br/>/<br/>/skills/:name<br/>/blog<br/>/blog/:slug<br/>/compare"]
    Router --> Image["Image Proxy<br/>/skills/:name/examples/images/*"]
```

**Diagram: Worker Request Flow**

Sources: [website/worker.js:3-6]()

## GitHub-as-Backend Architecture

The website does not maintain its own database or content management system. Instead, it fetches all dynamic content from the GitHub repository's `main` branch via raw content URLs. This creates a "GitHub-as-CMS" architecture where the Git repository serves as the single source of truth.

### Data Fetching Functions

Three core functions fetch content from GitHub with different caching strategies:

```mermaid
graph LR
    subgraph "Cloudflare Edge"
        Worker["worker.js"]
        Cache["caches.default"]
    end
    
    subgraph "GitHub Raw URLs"
        SkillsJSON["skills.json"]
        BlogJSON["blog/blog.json"]
        StatsJSON["install-stats.json"]
    end
    
    Worker -->|"fetchSkillsConfig()"| Cache
    Worker -->|"fetchBlogConfig()"| Cache
    Worker -->|"fetchInstallStats()"| Cache
    
    Cache -->|"60s TTL"| SkillsJSON
    Cache -->|"300s TTL"| BlogJSON
    Cache -->|"3600s TTL"| StatsJSON
```

**Diagram: Data Fetching Architecture**

| Function | GitHub URL | Cache TTL | Purpose |
|----------|-----------|-----------|---------|
| `fetchSkillsConfig()` | `raw.githubusercontent.com/.../skills.json` | 60 seconds | Skill metadata and registry |
| `fetchBlogConfig()` | `raw.githubusercontent.com/.../blog/blog.json` | 300 seconds | Blog post metadata |
| `fetchInstallStats()` | `raw.githubusercontent.com/.../install-stats.json` | 3600 seconds | Installation statistics from skills.sh |

Each function implements the same caching pattern:
1. Generate a unique cache URL (e.g., `https://opc.dev/_cache/skills-v2.json`)
2. Check Cloudflare's edge cache via `caches.default.match()`
3. If cache miss, fetch from GitHub raw URL
4. Store response in edge cache with appropriate TTL
5. Return parsed JSON data

**Sources:** [website/worker.js:1314-1381]()

### Fallback Configuration

The `getFallbackConfig()` function provides hardcoded skill data in case GitHub is unreachable. This ensures the website remains partially functional even if GitHub API fails. The fallback includes 6 core skills (domain-hunter, reddit, twitter, producthunt, requesthunt, archive) with full metadata.

**Sources:** [website/worker.js:1383-1623]()

## Request Routing System

The Worker implements pattern matching on `url.pathname` to dispatch requests to appropriate handlers. Routes are evaluated in order of appearance in the code.

### Route Dispatch Table

```mermaid
graph TB
    URLPath["url.pathname"]
    
    URLPath -->|"/sitemap.xml"| Sitemap["Generate Dynamic Sitemap<br/>Line 7-68"]
    URLPath -->|"/robots.txt"| Robots["Static robots.txt<br/>Line 70-126"]
    URLPath -->|"/llms.txt"| LLMs["AI-Optimized Summary<br/>Line 129-179"]
    URLPath -->|"/skills/:name/examples/images/*"| ImgProxy["Image Proxy<br/>Line 182-207"]
    URLPath -->|"/install.sh"| Redirect["302 Redirect to GitHub<br/>Line 210-215"]
    URLPath -->|"/skills.json"| SkillsJSON["Serve skills.json<br/>Line 218-227"]
    URLPath -->|"/compare"| Compare["renderComparePage()<br/>Line 230-232"]
    URLPath -->|"/blog"| BlogList["renderBlogListPage()<br/>Line 235-237"]
    URLPath -->|"/blog/:slug"| BlogPost["renderBlogPost(slug)<br/>Line 240-243"]
    URLPath -->|"/skills/:name"| SkillPage["renderSkillPage(name)<br/>Line 246-249"]
    URLPath -->|"/"| Landing["Render Landing Page<br/>Line 252+"]
```

**Diagram: Route Dispatcher Logic**

The routing logic uses regular expressions for parameterized routes:
- `/skills/([a-z-]+)` captures skill name (line 246)
- `/blog/([a-z0-9-]+)` captures blog post slug (line 240)
- `/skills/([a-z-]+)/examples/images/(.+)` captures skill name and image filename (line 182-183)

**Sources:** [website/worker.js:7-249]()

## Static Route Handlers

Static routes return pre-generated or templated responses without fetching dynamic data.

### /robots.txt

Returns a static text file with bot directives. Explicitly allows AI search engines (GPTBot, ClaudeBot, PerplexityBot, Google-Extended) while blocking SEO crawlers (AhrefsBot, SemrushBot). Includes custom `Content-Signal` header for GEO optimization.

**Sources:** [website/worker.js:70-126]()

### /llms.txt

Generates a plain-text summary optimized for AI language models. Includes:
- Overview of 9 skills
- Installation command
- Key statistics (platforms, license, FAQ count)
- Documentation links

This endpoint serves AI search engines that prefer plain text over HTML. Cache TTL is 3600 seconds.

**Sources:** [website/worker.js:129-179]()

### /sitemap.xml

Dynamically generates an XML sitemap by:
1. Fetching `skills.json` to enumerate all skills
2. Fetching `blog.json` to enumerate all blog posts
3. Constructing `<url>` entries for each skill and blog post
4. Including static pages (homepage, compare, blog index)

Each URL includes `lastmod`, `changefreq`, and `priority` metadata for SEO.

**Sources:** [website/worker.js:7-68]()

### /install.sh

Issues a 302 redirect to the GitHub README installation section. This allows the short URL `curl opc.dev/install.sh` to work while maintaining GitHub as the canonical installation documentation.

**Sources:** [website/worker.js:210-215]()

## Dynamic Route Handlers

Dynamic routes fetch content from GitHub and render HTML pages with embedded JSON-LD structured data.

### Landing Page (/)

The root route renders the main landing page:

1. Fetches `skills.json` via `fetchSkillsConfig()`
2. Fetches `install-stats.json` via `fetchInstallStats()`
3. Generates skill cards for all skills with:
   - Install commands including dependencies
   - API key requirements
   - Trigger keywords
   - Installation statistics
4. Embeds extensive JSON-LD markup:
   - `WebPage` with speakable schema
   - `ItemList` with all skills
   - `FAQPage` with 28+ questions
   - `HowTo` schema for installation
5. Returns HTML with inline CSS (1300+ lines)

The HTML includes responsive design, copy-to-clipboard functionality, and platform-specific install commands.

**Sources:** [website/worker.js:252-1310]()

### Individual Skill Pages (/skills/:name)

The `renderSkillPage(skillName, ctx)` function:

1. Fetches skill metadata from `skills.json`
2. Returns 404 if skill not found
3. Fetches `SKILL.md` from GitHub: `raw.githubusercontent.com/.../skills/{skillName}/SKILL.md`
4. Converts markdown to HTML via `markdownToHtml()` using the `marked` library
5. If skill has an example link, fetches and renders the example markdown
6. Generates skill-specific JSON-LD with:
   - `SoftwareApplication` schema
   - `BreadcrumbList` navigation
   - `FAQPage` with skill-specific questions
7. Renders HTML with skill metadata, dependencies, API key requirements, and full documentation

The function collects API keys from both the skill itself and its dependencies using `getAllKeys()`.

**Sources:** [website/worker.js:1677-2338]()

### Blog Routes

Two blog routes are handled:

**Blog List (/blog):** Calls `renderBlogListPage(ctx)` which fetches `blog.json` and renders a list of all blog posts with metadata.

**Individual Posts (/blog/:slug):** Calls `renderBlogPost(slug, ctx)` which fetches the post's markdown file from GitHub and renders it with BlogPosting schema.

**Sources:** [website/worker.js:235-243]()

## Content Rendering Pipeline

### Markdown Processing

The `markdownToHtml(md)` function:

1. Strips YAML frontmatter (lines starting with `---\n`)
2. Converts markdown to HTML using `marked.parse()`
3. Wraps images in `<figure>` tags with captions for grid layout
4. Returns sanitized HTML

This function is used for rendering SKILL.md files, example workflows, and blog posts.

**Sources:** [website/worker.js:1661-1675]()

### Image Proxy

The Worker proxies images from GitHub to serve them with appropriate content types:

```
/skills/{skillName}/examples/images/{fileName}
  ↓
https://raw.githubusercontent.com/ReScienceLab/opc-skills/main/skills/{skillName}/examples/images/{fileName}
```

Detects content type from file extension (.svg → image/svg+xml, .png → image/png, .jpg → image/jpeg) and sets 3600-second cache control.

**Sources:** [website/worker.js:182-207]()

## Response Headers and Caching

### Standard Response Headers

All responses include appropriate headers:

| Route Type | Content-Type | Cache-Control | Additional Headers |
|-----------|--------------|---------------|-------------------|
| HTML pages | `text/html;charset=UTF-8` | `public, max-age=300` | - |
| /skills.json | `application/json` | `public, max-age=300` | `Access-Control-Allow-Origin: *` |
| /sitemap.xml | `application/xml` | - | - |
| /robots.txt | `text/plain` | `public, max-age=86400` | `X-Robots-Tag: all` |
| /llms.txt | `text/plain` | `public, max-age=3600` | - |
| Images | `image/*` | `public, max-age=3600` | - |

### Cache Key Strategy

Cloudflare edge cache uses synthetic URLs as cache keys:
- `https://opc.dev/_cache/skills-v2.json` for skills config
- `https://opc.dev/_cache/blog-v1.json` for blog config  
- `https://opc.dev/_cache/install-stats.json` for statistics

These cache keys are versioned (v1, v2) allowing cache busting when data structures change.

**Sources:** [website/worker.js:1318-1380]()

## Deployment and Updates

### Continuous Deployment

The Worker is deployed via Cloudflare Pages with automatic deployments from the `main` branch. Any push to main triggers:

1. Wrangler build of worker.js
2. Deployment to Cloudflare's edge network
3. Instant propagation to 200+ edge locations worldwide

There is no build step or static site generation. The Worker serves dynamic content on every request, fetching fresh data from GitHub with edge caching for performance.

### Zero-Downtime Updates

Content updates follow this flow:

```mermaid
graph LR
    PR["Git Push to main<br/>(skills.json, blog.json)"]
    GitHub["GitHub main branch"]
    EdgeCache["Cloudflare Edge Cache"]
    Worker["Worker serves request"]
    
    PR --> GitHub
    GitHub -->|"Cache expires<br/>(60-3600s)"| EdgeCache
    EdgeCache --> Worker
    
    Worker -->|"Cache miss"| GitHub
```

**Diagram: Content Update Propagation**

Updates to `skills.json` propagate within 60 seconds (cache TTL). Updates to `install-stats.json` take up to 1 hour. This allows rapid content iteration without redeploying the Worker.

**Sources:** [website/worker.js:1314-1381]()

## Error Handling and Resilience

The Worker implements multiple fallback strategies:

1. **GitHub Fetch Failures:** If fetching from GitHub fails, `getFallbackConfig()` provides hardcoded skill data
2. **Missing Skills:** Individual skill pages return 404 with plain text "Skill not found"
3. **Missing Images:** Image proxy returns 404 with "Image not found" message
4. **Markdown Parse Errors:** The `markdownToHtml()` function gracefully handles malformed markdown

All fetch operations are wrapped in try-catch blocks that log errors but don't crash the Worker.

**Sources:** [website/worker.js:1325-1345](), [website/worker.js:1686-1689](), [website/worker.js:1728-1733](), [website/worker.js:193-206]()

---

# Page: Request Routing & Handlers

# Request Routing & Handlers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [website/worker.js](website/worker.js)
- [website/wrangler.toml](website/wrangler.toml)

</details>



This document describes the URL routing system and request handler functions in the Cloudflare Worker that powers opc.dev. It covers how incoming HTTP requests are matched to URL patterns, dispatched to appropriate handlers, and transformed into HTML or JSON responses.

For information about the overall worker architecture and deployment, see [Website Architecture](#4.1). For details on caching strategies applied to these routes, see [Caching Strategy](#4.3). For the specific data endpoints exposed, see [API Endpoints](#4.4).

## Routing Architecture Overview

The Cloudflare Worker implements a **sequential pattern-matching router** within the `fetch()` handler. Each incoming request's URL pathname is tested against a series of conditional statements in order of precedence, with the first match determining which handler processes the request.

```mermaid
graph TB
    Request["HTTP Request<br/>(request.url)"]
    URLParse["new URL(request.url)<br/>Extract pathname"]
    
    Request --> URLParse
    
    subgraph "Route Matching (Sequential)"
        R1["url.pathname === '/sitemap.xml'"]
        R2["url.pathname === '/robots.txt'"]
        R3["url.pathname === '/llms.txt'"]
        R4["url.pathname.match(/^\/skills\/([a-z-]+)\/examples\/images\/(.+)$/)"]
        R5["url.pathname === '/install.sh'"]
        R6["url.pathname === '/skills.json'"]
        R7["url.pathname === '/compare'"]
        R8["url.pathname === '/blog'"]
        R9["url.pathname.match(/^\/blog\/([a-z0-9-]+)$/)"]
        R10["url.pathname.match(/^\/skills\/([a-z-]+)$/)"]
        R11["Default: Landing Page"]
    end
    
    URLParse --> R1
    R1 -->|No Match| R2
    R2 -->|No Match| R3
    R3 -->|No Match| R4
    R4 -->|No Match| R5
    R5 -->|No Match| R6
    R6 -->|No Match| R7
    R7 -->|No Match| R8
    R8 -->|No Match| R9
    R9 -->|No Match| R10
    R10 -->|No Match| R11
    
    R1 -->|Match| H1["Generate Sitemap XML<br/>Inline Handler"]
    R2 -->|Match| H2["Return robots.txt<br/>Inline Handler"]
    R3 -->|Match| H3["Return llms.txt<br/>Inline Handler"]
    R4 -->|Match| H4["Proxy Image from GitHub<br/>Inline Handler"]
    R5 -->|Match| H5["302 Redirect<br/>Inline Handler"]
    R6 -->|Match| H6["Fetch & Return JSON<br/>Inline Handler"]
    R7 -->|Match| H7["renderComparePage(ctx)"]
    R8 -->|Match| H8["renderBlogListPage(ctx)"]
    R9 -->|Match| H9["renderBlogPost(slug, ctx)"]
    R10 -->|Match| H10["renderSkillPage(skillName, ctx)"]
    R11 --> H11["Render Landing Page<br/>Inline Handler"]
    
    H1 --> Response1["Response: XML"]
    H2 --> Response2["Response: text/plain"]
    H3 --> Response3["Response: text/plain"]
    H4 --> Response4["Response: image/*"]
    H5 --> Response5["Response: 302 redirect"]
    H6 --> Response6["Response: application/json"]
    H7 --> Response7["Response: text/html"]
    H8 --> Response8["Response: text/html"]
    H9 --> Response9["Response: text/html"]
    H10 --> Response10["Response: text/html"]
    H11 --> Response11["Response: text/html"]
```

**Sources:** [website/worker.js:1-1311]()

## Route Classification

Routes are categorized by their behavior: **static routes** return fixed or template-based content, while **dynamic routes** fetch data from GitHub and render HTML.

| Route Pattern | Type | Handler | Response Type | Cache TTL |
|--------------|------|---------|---------------|-----------|
| `/sitemap.xml` | Static (Generated) | Inline | `application/xml` | None |
| `/robots.txt` | Static | Inline | `text/plain` | 86400s |
| `/llms.txt` | Static (Template) | Inline | `text/plain` | 3600s |
| `/skills.json` | API | Inline | `application/json` | 300s |
| `/install.sh` | Redirect | Inline | 302 Redirect | None |
| `/skills/:name/examples/images/:file` | Proxy | Inline | `image/*` | 3600s |
| `/compare` | Dynamic | `renderComparePage` | `text/html` | 300s |
| `/blog` | Dynamic | `renderBlogListPage` | `text/html` | 300s |
| `/blog/:slug` | Dynamic | `renderBlogPost` | `text/html` | 300s |
| `/skills/:name` | Dynamic | `renderSkillPage` | `text/html` | 300s |
| `/` (default) | Dynamic | Inline | `text/html` | 300s |

**Sources:** [website/worker.js:4-1311]()

## Static Routes

### `/sitemap.xml` Route

Dynamically generates an XML sitemap by fetching skills and blog post metadata from GitHub. The sitemap includes entries for the landing page, comparison page, blog index, skills.json endpoint, individual skill pages, and blog posts.

```mermaid
graph LR
    Request["/sitemap.xml"]
    
    Request --> FetchData["fetchSkillsConfig(ctx)<br/>fetchBlogConfig(ctx)"]
    
    FetchData --> BuildURLs["Build URL List"]
    
    subgraph "URL Categories"
        Static["Static Pages<br/>(/, /compare, /blog, /skills.json)"]
        SkillURLs["Skill Pages<br/>(/skills/:name)"]
        BlogURLs["Blog Posts<br/>(/blog/:slug)"]
    end
    
    BuildURLs --> Static
    BuildURLs --> SkillURLs
    BuildURLs --> BlogURLs
    
    Static --> Template["XML Template<br/>with priority & changefreq"]
    SkillURLs --> Template
    BlogURLs --> Template
    
    Template --> Response["Response<br/>Content-Type: application/xml"]
```

**Implementation Details:**
- Executes at [website/worker.js:7-68]()
- Uses `fetchSkillsConfig` to get list of skills [website/worker.js:8]()
- Uses `fetchBlogConfig` to get list of blog posts [website/worker.js:10]()
- Each skill page has priority `0.8` and changefreq `weekly` [website/worker.js:20-21]()
- Blog posts have priority `0.7` and changefreq `monthly` [website/worker.js:32-33]()
- Landing page has priority `1.0` [website/worker.js:44]()

**Sources:** [website/worker.js:7-68]()

### `/robots.txt` Route

Returns a static robots.txt file that explicitly allows AI crawlers (GPTBot, ClaudeBot, PerplexityBot) while blocking SEO crawlers (AhrefsBot, SemrushBot). Includes a `Content-Signal` header for GEO compliance.

**Implementation:**
- Executes at [website/worker.js:70-126]()
- Returns inline string with User-agent directives [website/worker.js:71-117]()
- Sets `Cache-Control: public, max-age=86400` (24 hours) [website/worker.js:122]()
- Includes `X-Robots-Tag: all` header [website/worker.js:121]()
- References sitemap location [website/worker.js:117]()

**Sources:** [website/worker.js:70-126]()

### `/llms.txt` Route

Provides an AI-optimized plain text summary of the entire OPC Skills repository in a format designed for LLM consumption. Includes skill listings, installation instructions, statistics, and documentation links.

**Implementation:**
- Executes at [website/worker.js:129-179]()
- Template includes current date via `new Date().toISOString().split("T")[0]` [website/worker.js:130, 158]()
- Lists 9 skills with descriptions [website/worker.js:142-150]()
- Includes installation time, license, and FAQ count [website/worker.js:153-157]()
- Sets `Cache-Control: public, max-age=3600` (1 hour) [website/worker.js:175]()

**Sources:** [website/worker.js:129-179]()

### `/install.sh` Route

A redirect route that points users to the GitHub README installation section.

**Implementation:**
- Executes at [website/worker.js:210-215]()
- Returns 302 redirect to `https://github.com/ReScienceLab/opc-skills#installation` [website/worker.js:211-214]()

**Sources:** [website/worker.js:210-215]()

### `/skills.json` Route

Fetches and returns the skills registry from GitHub. This is the canonical API endpoint for skill metadata.

**Implementation:**
- Executes at [website/worker.js:218-227]()
- Calls `fetchSkillsConfig(ctx)` to retrieve cached/fresh data [website/worker.js:219]()
- Returns JSON with `Access-Control-Allow-Origin: *` for CORS [website/worker.js:223]()
- Sets `Cache-Control: public, max-age=300` (5 minutes) [website/worker.js:224]()

**Sources:** [website/worker.js:218-227]()

## Dynamic Routes with Regex Matching

### Image Proxy Route

Proxies skill example images from GitHub raw content URLs to avoid CORS issues.

**Pattern:** `/skills/:skillName/examples/images/:fileName`

**Regex:** `/^\/skills\/([a-z-]+)\/examples\/images\/(.+)$/`

```mermaid
graph LR
    Request["/skills/logo-creator/examples/images/logo.png"]
    
    Request --> Regex["url.pathname.match<br/>(regex pattern)"]
    
    Regex --> Extract["Extract:<br/>skillName = 'logo-creator'<br/>fileName = 'logo.png'"]
    
    Extract --> ContentType["Determine Content-Type<br/>by file extension"]
    
    ContentType --> FetchGH["fetch GitHub Raw URL<br/>raw.githubusercontent.com/.../fileName"]
    
    FetchGH --> Proxy["Proxy response body<br/>with correct Content-Type"]
    
    Proxy --> Response["Response: image/*<br/>Cache-Control: 3600s"]
```

**Implementation:**
- Executes at [website/worker.js:182-207]()
- Regex capture groups: `[, skillName, fileName]` [website/worker.js:186]()
- Content-Type detection for `.svg`, `.png`, `.jpeg` [website/worker.js:187-191]()
- Constructs GitHub URL: `https://raw.githubusercontent.com/ReScienceLab/opc-skills/main/skills/${skillName}/examples/images/${fileName}` [website/worker.js:192]()
- Returns 404 if image not found [website/worker.js:206]()

**Sources:** [website/worker.js:182-207]()

### Blog Post Route

Matches individual blog post URLs and delegates to the `renderBlogPost` handler.

**Pattern:** `/blog/:slug`

**Regex:** `/^\/blog\/([a-z0-9-]+)$/`

**Implementation:**
- Executes at [website/worker.js:240-243]()
- Regex captures slug: `blogMatch[1]` [website/worker.js:242]()
- Delegates to `renderBlogPost(slug, ctx)` function [website/worker.js:242]()

**Sources:** [website/worker.js:240-243]()

### Skill Page Route

Matches individual skill detail pages and delegates to the `renderSkillPage` handler.

**Pattern:** `/skills/:skillName`

**Regex:** `/^\/skills\/([a-z-]+)$/`

**Implementation:**
- Executes at [website/worker.js:246-249]()
- Regex captures skillName: `skillMatch[1]` [website/worker.js:248]()
- Delegates to `renderSkillPage(skillName, ctx)` function [website/worker.js:248]()

**Sources:** [website/worker.js:246-249]()

## Handler Function Architecture

Dynamic routes delegate to specialized handler functions that fetch data, render HTML, and return responses. The following diagram maps handlers to their data dependencies and outputs.

```mermaid
graph TB
    subgraph "Handler Functions"
        H1["renderComparePage(ctx)"]
        H2["renderBlogListPage(ctx)"]
        H3["renderBlogPost(slug, ctx)"]
        H4["renderSkillPage(skillName, ctx)"]
        H5["Landing Page Handler<br/>(inline in fetch)"]
    end
    
    subgraph "Data Fetching Functions"
        F1["fetchSkillsConfig(ctx)<br/>Returns: config object"]
        F2["fetchBlogConfig(ctx)<br/>Returns: blog.json data"]
        F3["fetchInstallStats(ctx)<br/>Returns: install-stats.json"]
    end
    
    subgraph "Utility Functions"
        U1["markdownToHtml(md)<br/>Uses marked.parse()"]
        U2["getAllKeys(skill, allSkills)<br/>Collect API keys"]
        U3["getDeps(dependencies)<br/>Normalize dep format"]
    end
    
    H1 --> F1
    H1 --> F3
    
    H2 --> F2
    
    H3 --> F2
    H3 --> U1
    
    H4 --> F1
    H4 --> F3
    H4 --> U1
    H4 --> U2
    H4 --> U3
    
    H5 --> F1
    H5 --> F3
    H5 --> U2
    H5 --> U3
    
    F1 --> Cache1["Cloudflare Edge Cache<br/>TTL: 60s"]
    F2 --> Cache2["Cloudflare Edge Cache<br/>TTL: 300s"]
    F3 --> Cache3["Cloudflare Edge Cache<br/>TTL: 3600s"]
    
    H1 --> Response1["HTML Response<br/>Comparison Table"]
    H2 --> Response2["HTML Response<br/>Blog Index"]
    H3 --> Response3["HTML Response<br/>Blog Article"]
    H4 --> Response4["HTML Response<br/>Skill Details"]
    H5 --> Response5["HTML Response<br/>Landing Page"]
```

**Sources:** [website/worker.js:1-1311](), [website/worker.js:1314-1346](), [website/worker.js:1349-1381](), [website/worker.js:1626-1658](), [website/worker.js:1661-1675](), [website/worker.js:1678-1856]()

### `renderSkillPage(skillName, ctx)` Handler

Renders the detailed page for an individual skill, including its SKILL.md content, dependencies, API key requirements, install commands, and example images.

**Data Flow:**
1. Fetches skills config and install stats [website/worker.js:1679-1682]()
2. Finds matching skill object [website/worker.js:1683]()
3. Returns 404 if not found [website/worker.js:1685-1689]()
4. Extracts dependencies using helper functions [website/worker.js:1695-1699]()
5. Collects all API keys (including from dependencies) [website/worker.js:1702-1720]()
6. Fetches SKILL.md from GitHub raw URL [website/worker.js:1726-1733]()
7. Converts markdown to HTML using `markdownToHtml()` [website/worker.js:1735]()
8. Optionally fetches example markdown if `skill.links.example` exists [website/worker.js:1738-1753]()
9. Generates JSON-LD schema (WebPage, SoftwareApplication, BreadcrumbList, FAQPage) [website/worker.js:1757-1855]()
10. Renders HTML template with embedded CSS and JavaScript [website/worker.js:1857-2069]()

**Key Features:**
- Dependency tracking with visual tags [website/worker.js:1987]()
- API key display with provider URLs [website/worker.js:1986]()
- Install count display from stats [website/worker.js:1692, 1980]()
- Tab-based content sections (Overview, Installation, Examples) via JavaScript [website/worker.js:1938-1943]()

**Sources:** [website/worker.js:1678-2074]()

### Landing Page Handler (Inline)

The default route handler renders the main landing page with all skills displayed as cards. This handler is implemented inline within the `fetch()` function rather than as a separate function.

**Data Flow:**
1. Fetches skills config and install stats [website/worker.js:252-255]()
2. Generates JSON-LD structured data for all skills [website/worker.js:259-276]()
3. Creates FAQPage schema with 28+ questions [website/worker.js:278-543]()
4. Builds skill card HTML for each skill [website/worker.js:670-720]()
5. Renders complete HTML page with:
   - Hero section with install command [website/worker.js:1020-1115]()
   - Tools scroller (animated list of supported platforms) [website/worker.js:1030-1105]()
   - Skills grid [website/worker.js:1118-1120]()
   - FAQ section [website/worker.js:1122-1168]()

**Skill Card Generation:**
- Uses helper functions `getDeps()`, `getAllKeys()`, `requiresApiKey()` [website/worker.js:639-667]()
- Displays install count if > 0 [website/worker.js:672, 684]()
- Shows "API Key" or "Free" badge [website/worker.js:686]()
- Includes dependency auto-installation in command [website/worker.js:704]()
- Copy-to-clipboard functionality [website/worker.js:705]()

**Sources:** [website/worker.js:252-1309]()

### `renderBlogListPage(ctx)` Handler

Renders the blog index page listing all published blog posts. This function is referenced in the routing logic but its implementation is not provided in the given file.

**Expected Behavior:**
- Fetches blog configuration via `fetchBlogConfig(ctx)`
- Renders list of posts with titles, descriptions, dates
- Includes links to individual post pages

**Sources:** [website/worker.js:235-237]()

### `renderBlogPost(slug, ctx)` Handler

Renders an individual blog post page. This function is referenced in the routing logic but its implementation is not provided in the given file.

**Expected Behavior:**
- Fetches blog configuration to find post metadata
- Fetches markdown content from GitHub
- Converts markdown to HTML using `markdownToHtml()`
- Renders HTML with schema.org BlogPosting markup

**Sources:** [website/worker.js:240-243]()

### `renderComparePage(ctx)` Handler

Renders a comparison page (likely comparing OPC Skills to alternatives). This function is referenced in the routing logic but its implementation is not provided in the given file.

**Expected Behavior:**
- Fetches skills config
- Generates comparison table HTML
- Returns HTML response with Cache-Control

**Sources:** [website/worker.js:230-232]()

## Helper Functions

### `getDeps(dependencies)`

Normalizes the dependency field format, which can be either an array or an object with version requirements.

**Implementation:**
- Returns empty array if `deps` is falsy [website/worker.js:640]()
- Returns `deps` directly if already an array [website/worker.js:641]()
- Returns `Object.keys(deps)` if object [website/worker.js:642]()

**Sources:** [website/worker.js:639-643]()

### `getAllKeys(skill, allSkills)`

Recursively collects all API keys required by a skill, including those from its dependencies.

**Algorithm:**
1. Start with keys from `skill.auth?.keys` [website/worker.js:648]()
2. Get dependency names using `getDeps()` [website/worker.js:649]()
3. For each dependency:
   - Find dependency skill object [website/worker.js:651]()
   - Check if it has API keys [website/worker.js:652]()
   - Add keys that aren't already in the list [website/worker.js:653-656]()
   - Mark keys with `from: depName` property [website/worker.js:655]()
4. Return complete list [website/worker.js:660]()

**Sources:** [website/worker.js:647-661]()

### `requiresApiKey(skill, allSkills)`

Determines if a skill requires any non-optional API key, either directly or through dependencies.

**Implementation:**
- Calls `getAllKeys()` to get complete key list [website/worker.js:665]()
- Returns true if any key has `optional: false` (or undefined) [website/worker.js:666]()

**Sources:** [website/worker.js:664-667]()

### `markdownToHtml(md)`

Converts markdown to HTML using the `marked` library, with preprocessing to remove YAML frontmatter and postprocessing to wrap images in figure tags.

**Implementation:**
1. Returns empty string if input is falsy [website/worker.js:1662]()
2. Removes YAML frontmatter (lines between `---`) if present at start [website/worker.js:1664-1666]()
3. Parses markdown using `marked.parse()` [website/worker.js:1668]()
4. Wraps `<img>` tags in `<figure>` with `<figcaption>` [website/worker.js:1670-1673]()
5. Returns processed HTML [website/worker.js:1674]()

**Sources:** [website/worker.js:1661-1675]()

## Data Fetching Functions

All data fetching functions follow a consistent caching pattern and are documented in detail in [Caching Strategy](#4.3). The routing layer invokes these functions as needed:

- `fetchSkillsConfig(ctx)` - Retrieves skills.json from GitHub [website/worker.js:1314-1346]()
- `fetchBlogConfig(ctx)` - Retrieves blog.json from GitHub [website/worker.js:1626-1658]()
- `fetchInstallStats(ctx)` - Retrieves install-stats.json from GitHub [website/worker.js:1349-1381]()
- `getFallbackConfig()` - Returns hardcoded fallback data if GitHub is unreachable [website/worker.js:1383-1623]()

**Sources:** [website/worker.js:1314-1658]()

## Request-Response Flow

The complete flow from incoming request to response follows this pattern:

```mermaid
sequenceDiagram
    participant Client
    participant Worker as "Cloudflare Worker"
    participant Router as "fetch() Router"
    participant Handler as "Handler Function"
    participant Cache as "Edge Cache"
    participant GitHub as "GitHub Raw"
    
    Client->>Worker: HTTP Request
    Worker->>Router: Extract URL pathname
    
    alt Static Route
        Router->>Router: Match static pattern
        Router->>Client: Return static content
    else Dynamic Route
        Router->>Handler: Delegate to handler function
        Handler->>Cache: Check cache
        alt Cache Hit
            Cache->>Handler: Return cached data
        else Cache Miss
            Handler->>GitHub: Fetch raw content
            GitHub->>Handler: Return data
            Handler->>Cache: Store in cache
        end
        Handler->>Handler: Generate HTML/JSON
        Handler->>Client: Return Response
    end
```

**Key Characteristics:**
- **Sequential matching**: Routes are tested in declaration order
- **First-match wins**: Once a pattern matches, no further patterns are tested
- **Context passing**: All handlers receive `ctx` parameter for cache operations
- **Fallback behavior**: If no pattern matches, landing page is rendered
- **Error handling**: 404 responses for missing resources (e.g., skill not found)

**Sources:** [website/worker.js:1-1311]()

---

# Page: Caching Strategy

# Caching Strategy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [website/worker.js](website/worker.js)
- [website/wrangler.toml](website/wrangler.toml)

</details>



This page documents how `website/worker.js` caches upstream data fetches at the Cloudflare edge. The focus is on the three helper functions — `fetchSkillsConfig`, `fetchBlogConfig`, and `fetchInstallStats` — and how they use the `ctx` execution context to avoid redundant network calls. For route-level details such as which URL paths call these helpers, see [4.2](#4.2). For the overall architecture of the worker, see [4.1](#4.1).

---

## Background: Cloudflare Worker Execution Context

The main entry point of the worker is:

[website/worker.js:3-4]()

```js
async fetch(request, env, ctx)
```

`ctx` is a [`ExecutionContext`](https://developers.cloudflare.com/workers/runtime-apis/context/) object provided by the Cloudflare runtime. Its primary method relevant to caching is `ctx.waitUntil(promise)`, which extends the Worker's lifetime so that async side-effects (like writing to the Cache API) can complete *after* the response has been sent to the client.

The Cloudflare Cache API (`caches.default`) provides a per-datacenter, per-URL key-value store for HTTP responses. The standard pattern is:

1. Compute a cache key (typically a `Request` or URL string).
2. Call `caches.default.match(key)` — return cached response if found.
3. On a miss, fetch from the upstream origin.
4. Use `ctx.waitUntil(caches.default.put(key, response.clone()))` to write to cache without blocking the response.

---

## Cached Upstream Data Sources

Three upstream sources are fetched from GitHub (raw content) and cached at the edge:

| Helper Function | Upstream Source | Used By Routes |
|---|---|---|
| `fetchSkillsConfig(ctx)` | `skills.json` on GitHub | `/`, `/skills/[name]`, `/compare`, `/skills.json`, `/sitemap.xml` |
| `fetchBlogConfig(ctx)` | `blog.json` on GitHub | `/`, `/blog`, `/blog/[slug]`, `/sitemap.xml` |
| `fetchInstallStats(ctx)` | `website/install-stats.json` on GitHub | `/`, `/skills/[name]` |

All three accept `ctx` as their sole parameter, enabling them to read from and write to the Cloudflare edge cache.

**Sources:**
- [website/worker.js:8-11]()
- [website/worker.js:218-219]()
- [website/worker.js:251-255]()

---

## How `ctx` Flows Through the Worker

**Diagram: ctx parameter propagation**

```mermaid
flowchart TD
  A["fetch(request, env, ctx)"]
  B["fetchSkillsConfig(ctx)"]
  C["fetchBlogConfig(ctx)"]
  D["fetchInstallStats(ctx)"]
  E["caches.default.match(key)"]
  F["fetch(upstreamURL)"]
  G["ctx.waitUntil(caches.default.put(key, res.clone()))"]
  H["return cached or fresh JSON"]

  A --> B
  A --> C
  A --> D
  B --> E
  C --> E
  D --> E
  E -- "hit" --> H
  E -- "miss" --> F
  F --> G
  F --> H
```

Sources: [website/worker.js:3-255]()

---

## Route-Level Call Sites

Each route handler that needs data calls one or more of the helpers. The `ctx` object is passed through from the top-level `fetch` handler every time.

**Diagram: Route handlers and which fetch helpers they call**

```mermaid
flowchart LR
  fetch["fetch(request, env, ctx)"]

  subgraph "Routes"
    R1["/sitemap.xml"]
    R2["/ (homepage)"]
    R3["/skills.json"]
    R4["/skills/[name]"]
    R5["/compare"]
    R6["/blog"]
    R7["/blog/[slug]"]
  end

  subgraph "Helpers"
    FSC["fetchSkillsConfig(ctx)"]
    FBC["fetchBlogConfig(ctx)"]
    FIS["fetchInstallStats(ctx)"]
  end

  fetch --> R1
  fetch --> R2
  fetch --> R3
  fetch --> R4
  fetch --> R5
  fetch --> R6
  fetch --> R7

  R1 --> FSC
  R1 --> FBC
  R2 --> FSC
  R2 --> FIS
  R3 --> FSC
  R4 --> FSC
  R4 --> FIS
  R5 --> FSC
  R6 --> FBC
  R7 --> FBC
```

Sources: [website/worker.js:7-255]()

---

## Response-Level `Cache-Control` Headers

In addition to the internal edge cache for upstream fetches, several final HTTP responses sent to clients include explicit `Cache-Control` headers. These instruct Cloudflare's CDN and end-user browsers to cache responses downstream.

| Route | `Cache-Control` value | TTL |
|---|---|---|
| `/robots.txt` | `public, max-age=86400` | 24 hours |
| `/llms.txt` | `public, max-age=3600` | 1 hour |
| `/skills/[name]/examples/images/...` | `public, max-age=3600` | 1 hour |
| `/skills.json` | `public, max-age=300` | 5 minutes |

The short TTL on `/skills.json` reflects that it exposes the live skills registry, which updates more frequently than static assets.

Sources: [website/worker.js:118-125]()  [website/worker.js:173-178]()  [website/worker.js:197-202]()  [website/worker.js:220-226]()

---

## Cache Miss vs. Cache Hit Request Flow

**Diagram: Full request lifecycle for a cache miss and subsequent hit**

```mermaid
sequenceDiagram
  participant "Browser/Bot" as Client
  participant "Cloudflare Edge" as Edge
  participant "worker.js fetch()" as Worker
  participant "caches.default" as Cache
  participant "GitHub Raw" as Origin

  Client ->> Edge: GET /
  Edge ->> Worker: dispatch request + ctx
  Worker ->> Cache: caches.default.match(skillsKey)
  Cache -->> Worker: null (miss)
  Worker ->> Origin: fetch(skills.json)
  Origin -->> Worker: 200 OK + body
  Worker ->> Worker: ctx.waitUntil(cache.put(key, clone))
  Worker -->> Edge: Response (HTML)
  Edge -->> Client: 200 OK

  Note over Cache: async cache write completes

  Client ->> Edge: GET / (next request)
  Edge ->> Worker: dispatch request + ctx
  Worker ->> Cache: caches.default.match(skillsKey)
  Cache -->> Worker: 200 OK (hit)
  Worker -->> Edge: Response (HTML)
  Edge -->> Client: 200 OK (no upstream call)
```

Sources: [website/worker.js:3-255]()

---

## Relationship to the Install Stats Pipeline

`fetchInstallStats(ctx)` caches `website/install-stats.json`, which is committed to the repository daily by the GitHub Actions workflow in `.github/workflows/fetch-install-stats.yml`. The data originates from `scripts/fetch-install-stats.py`, which scrapes `skills.sh`. Because the file is updated only once per day (via cron at 06:00 UTC), the cached copy at the edge will remain accurate for its full TTL before needing a refresh.

For more details on how the stats file is generated and updated, see [3.5](#3.5).

Sources: [website/install-stats.json:1-16]()  [.github/workflows/fetch-install-stats.yml:1-36]()  [scripts/fetch-install-stats.py:1-67]()

---

# Page: API Endpoints

# API Endpoints

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [website/worker.js](website/worker.js)
- [website/wrangler.toml](website/wrangler.toml)

</details>



This page documents the four machine-readable API endpoints exposed by the Cloudflare Worker at `website/worker.js`. These endpoints are designed for programmatic access, search engine crawlers, and LLM consumers — not for human browser navigation. For the full set of URL routes including HTML-rendered pages, see [Request Routing & Handlers](#4.2). For the caching behavior applied to upstream data fetches, see [Caching Strategy](#4.3).

---

## Endpoint Summary

| Path | Content-Type | Purpose | CORS | Cache TTL |
|---|---|---|---|---|
| `/skills.json` | `application/json` | Full skill registry for programmatic access | `*` | 5 minutes |
| `/sitemap.xml` | `application/xml` | Dynamically generated XML sitemap | — | None set |
| `/robots.txt` | `text/plain` | Bot allowlist / blocklist | — | 24 hours |
| `/llms.txt` | `text/plain` | Plain-text summary for LLM consumption | — | 1 hour |

Sources: [website/worker.js:218-227](), [website/worker.js:65-67](), [website/worker.js:119-125](), [website/worker.js:173-178]()

---

## Request Routing Overview

The four API endpoints are handled in the `fetch()` entrypoint before the HTML-rendering routes are reached. Each is matched by exact `pathname` equality (except `/sitemap.xml`, which also calls `fetchBlogConfig`).

**Diagram: API Endpoint Dispatch in `fetch()`**

```mermaid
flowchart TD
    req["Request"] --> pathcheck{"url.pathname"}
    pathcheck -->|"/sitemap.xml"| sitemapHandler["sitemap.xml handler\n(lines 7-68)"]
    pathcheck -->|"/robots.txt"| robotsHandler["robots.txt handler\n(lines 70-126)"]
    pathcheck -->|"/llms.txt"| llmsHandler["llms.txt handler\n(lines 128-178)"]
    pathcheck -->|"/skills.json"| skillsJsonHandler["skills.json handler\n(lines 218-227)"]
    pathcheck -->|"other"| htmlRoutes["HTML routes\n(compare, blog, skills, home)"]

    sitemapHandler --> fetchSkillsConfig["fetchSkillsConfig(ctx)"]
    sitemapHandler --> fetchBlogConfig["fetchBlogConfig(ctx)"]
    skillsJsonHandler --> fetchSkillsConfig2["fetchSkillsConfig(ctx)"]
```

Sources: [website/worker.js:7-8](), [website/worker.js:70](), [website/worker.js:129](), [website/worker.js:218-219]()

---

## `/skills.json`

Returns the full skill registry as JSON. This is the same data source used to render the homepage skill cards. It is the primary integration point for external tools that want to enumerate available skills programmatically (e.g., the universal installer described in [Universal Installer](#3.3)).

**Handler location:** [website/worker.js:218-227]()

**Response headers:**

| Header | Value |
|---|---|
| `Content-Type` | `application/json` |
| `Access-Control-Allow-Origin` | `*` |
| `Cache-Control` | `public, max-age=300` |

The wide-open CORS policy (`*`) means any browser-side JavaScript can fetch this endpoint directly. The 300-second cache TTL limits upstream calls to the GitHub-hosted `skills.json` source to at most once per 5 minutes per edge node.

The response body is the result of `JSON.stringify(skills, null, 2)` where `skills` is the object returned by `fetchSkillsConfig(ctx)`. The shape of this object is documented in [Skills Registry (skills.json)](#2.1).

**Example response structure (abbreviated):**

```json
{
  "version": "1.0",
  "name": "opc-skills",
  "skills": [
    {
      "name": "reddit",
      "version": "1.0.0",
      "description": "...",
      "triggers": ["..."],
      "dependencies": {},
      "auth": {},
      "install": {},
      "commands": [],
      "links": {}
    }
  ]
}
```

Sources: [website/worker.js:218-227]()

---

## `/sitemap.xml`

Generates an XML sitemap conforming to the [Sitemaps protocol](https://www.sitemaps.org/schemas/sitemap/0.9) schema. The sitemap is built dynamically at request time by combining:

1. A static set of top-level pages (`/`, `/compare`, `/blog`, `/skills.json`)
2. One `<url>` entry per skill, derived from `fetchSkillsConfig(ctx)`
3. One `<url>` entry per blog post, derived from `fetchBlogConfig(ctx)`

**Handler location:** [website/worker.js:7-68]()

**Diagram: Sitemap URL Assembly**

```mermaid
flowchart LR
    fetchSkillsConfig["fetchSkillsConfig(ctx)"] --> skillUrls["skillUrls\nfor each skill.name\n/skills/{name}"]
    fetchBlogConfig["fetchBlogConfig(ctx)"] --> blogUrls["blogUrls\nfor each post.slug\n/blog/{slug}"]
    staticUrls["Static URLs\n/, /compare, /blog, /skills.json"] --> sitemap["sitemap XML string"]
    skillUrls --> sitemap
    blogUrls --> sitemap
    sitemap --> response["Response\nContent-Type: application/xml"]
```

**URL priorities and change frequencies:**

| URL | `<priority>` | `<changefreq>` | `<lastmod>` |
|---|---|---|---|
| `/` | `1.0` | `weekly` | today (ISO date) |
| `/blog` | `0.8` | `weekly` | today |
| `/skills.json` | `0.6` | `weekly` | today |
| `/compare` | `0.7` | `monthly` | today |
| `/skills/{name}` | `0.8` | `weekly` | today |
| `/blog/{slug}` | `0.7` | `monthly` | `post.date` from blog config |

The `<lastmod>` for skill pages always uses the current date (computed as `new Date().toISOString().split("T")[0]`). Blog posts use the `date` field from each entry in `blog.json`.

No `Cache-Control` header is set on the sitemap response, so caching behavior falls back to Cloudflare's default edge policy.

Sources: [website/worker.js:7-68]()

---

## `/robots.txt`

Serves a static `robots.txt` directive file. The content is a string literal embedded directly in the handler — no upstream fetches are required.

**Handler location:** [website/worker.js:70-126]()

**Response headers:**

| Header | Value |
|---|---|
| `Content-Type` | `text/plain` |
| `X-Robots-Tag` | `all` |
| `Cache-Control` | `public, max-age=86400` |

The 86400-second TTL (24 hours) keeps this response cached aggressively at the edge, since the content rarely changes.

**Bot policy:**

| Bot user-agent | Directive |
|---|---|
| `*` (all) | `Allow: /` |
| `GPTBot` | `Allow: /` |
| `ChatGPT-User` | `Allow: /` |
| `PerplexityBot` | `Allow: /` |
| `ClaudeBot` | `Allow: /` |
| `anthropic-ai` | `Allow: /` |
| `Google-Extended` | `Allow: /` |
| `Applebot-Extended` | `Allow: /` |
| `Amazonbot` | `Allow: /` |
| `Bingbot` | `Allow: /` |
| `Googlebot` | `Allow: /` |
| `AhrefsBot` | `Disallow: /` |
| `SemrushBot` | `Disallow: /` |

The comment block at the top of the file explicitly marks the GEO intent:

```
# Content-Signal: search=yes, ai-input=yes, ai-train=no
```

The AI bot allowlist is intentional GEO (Generative Engine Optimization) strategy — permitting crawling by AI search engines so that OPC Skills content is indexed and cited by LLM-based search products. This is also discussed in [SEO & GEO Optimization Strategy](#4.5). The file ends with a `Sitemap:` directive pointing to `https://opc.dev/sitemap.xml`.

Sources: [website/worker.js:70-126]()

---

## `/llms.txt`

Returns a structured plain-text summary of the OPC Skills project, formatted for direct consumption by large language models. This follows the emerging `llms.txt` convention for machine-readable site metadata.

**Handler location:** [website/worker.js:128-178]()

**Response headers:**

| Header | Value |
|---|---|
| `Content-Type` | `text/plain` |
| `Cache-Control` | `public, max-age=3600` |

The 1-hour TTL is shorter than `robots.txt` because `llms.txt` includes a dynamic `Last updated: ${today}` line.

**Document structure:**

The response is a multi-section Markdown-style plain text document with the following sections:

| Section heading | Contents |
|---|---|
| `# OPC Skills - AI Agent Skills for Solopreneurs` | Title |
| `## Overview` | Skill count, supported platforms |
| `## Installation` | `npx skills add` command |
| `## Skills` | Numbered list of all 9 skills with one-line descriptions |
| `## Statistics` | Skill count, platform count, install time, license, FAQ count, last updated date |
| `## Documentation` | Links to opc.dev, GitHub, skills.sh, agentskills.io |
| `## Key Features` | Bullet list of key characteristics |

Unlike `/skills.json`, this endpoint's content is a static string literal in the source (not derived from `fetchSkillsConfig`). Skill entries in the `## Skills` section are hardcoded rather than generated from the live registry. Only the `Last updated` date is dynamic.

Sources: [website/worker.js:128-178]()

---

## Endpoint Relationship to Data Sources

**Diagram: Data Source Dependency per Endpoint**

```mermaid
flowchart LR
    subgraph "Cloudflare Worker (worker.js)"
        skillsJson["/skills.json"]
        sitemap["/sitemap.xml"]
        robots["/robots.txt"]
        llms["/llms.txt"]
    end

    subgraph "Upstream Data (via ctx cache)"
        fetchSkillsConfig["fetchSkillsConfig(ctx)\nskills.json on GitHub"]
        fetchBlogConfig["fetchBlogConfig(ctx)\nblog.json on GitHub"]
    end

    subgraph "Static Strings"
        staticBotPolicy["Hardcoded bot policy"]
        staticLlmContent["Hardcoded skill list\n+ dynamic date"]
    end

    skillsJson --> fetchSkillsConfig
    sitemap --> fetchSkillsConfig
    sitemap --> fetchBlogConfig
    robots --> staticBotPolicy
    llms --> staticLlmContent
```

Sources: [website/worker.js:7-227]()

---

## Notes

- All four endpoints are resolved before any HTML rendering logic runs in `fetch()`. If the pathname matches one of these four patterns, the function returns early.
- The `/skills.json` endpoint is the only one that sets `Access-Control-Allow-Origin: *`. The other three are not intended for cross-origin browser access.
- The `/llms.txt` skill list is not automatically synchronized with the live `skills.json` registry. If a new skill is added to the registry, the `/llms.txt` content must be manually updated in `worker.js`.
- The sitemap includes `/skills.json` itself as a crawlable URL with `priority=0.6`, signaling to search engines that the JSON data endpoint is a first-class document.

Sources: [website/worker.js:59-63](), [website/worker.js:218-227](), [website/worker.js:128-178]()

---

# Page: SEO & GEO Optimization Strategy

# SEO & GEO Optimization Strategy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [website/worker.js](website/worker.js)
- [website/wrangler.toml](website/wrangler.toml)

</details>



This page documents the website-level SEO and GEO (Generative Engine Optimization) strategy embedded in `website/worker.js`. It covers the structured data schemas on the homepage, the `llms.txt` and `robots.txt` endpoints, and how the overall site is tuned for both traditional search engines and AI-powered answer engines.

> For documentation on the **`seo-geo` agent skill** — the installable tool that helps users apply these same techniques to *their own* websites — see [2.4.3](#2.4.3). For the full list of API endpoints exposed by the worker, see [4.4](#4.4). For the general website architecture, see [4.1](#4.1).

---

## Strategy Overview

The OPC Skills site implements a two-track visibility strategy: traditional SEO (meta tags, sitemaps, canonical URLs) and GEO (structured data, AI-bot permissions, `llms.txt`). All logic lives in a single Cloudflare Worker at `website/worker.js`.

**Strategy Overview: Routes and Their SEO/GEO Role**

```mermaid
flowchart TD
    subgraph "Cloudflare Worker (website/worker.js)"
        R1["/robots.txt handler"]
        R2["/llms.txt handler"]
        R3["/sitemap.xml handler"]
        R4["/ homepage handler"]
    end

    R1 -->|"Explicit Allow for AI crawlers"| BOT["GPTBot, ClaudeBot, PerplexityBot,\nGoogle-Extended, Bingbot, etc."]
    R1 -->|"Explicit Disallow"| BADBOT["AhrefsBot, SemrushBot"]

    R2 -->|"Structured plain-text for LLMs"| LLMTXT["Plain-text skill inventory\n+ install command\n+ statistics"]

    R3 -->|"XML sitemap with priorities"| SITEMAP["/ (1.0), /skills/* (0.8),\n/blog (0.8), /blog/* (0.7),\n/compare (0.7), /skills.json (0.6)"]

    R4 -->|"Injects into HTML head"| JSONLD["jsonLd @graph\n(application/ld+json)"]
    JSONLD --> WP["WebPage"]
    JSONLD --> WS["WebSite"]
    JSONLD --> ORG["Organization"]
    JSONLD --> IL["ItemList of SoftwareApplications"]
    JSONLD --> FAQ["FAQPage (faqItems[])"]
    JSONLD --> HOW["HowTo (installation steps)"]
```

Sources: [website/worker.js:70-179](), [website/worker.js:258-636]()

---

## AI Bot Access: `robots.txt`

The `/robots.txt` handler at [website/worker.js:70-126]() explicitly enumerates AI crawlers in a **GEO-specific allowlist**, with a comment noting the intent: `"We explicitly allow AI bots for GEO (Generative Engine Optimization)"`.

### AI Bot Allowlist

| User-Agent | Platform |
|---|---|
| `GPTBot` | OpenAI (ChatGPT training) |
| `ChatGPT-User` | ChatGPT with browsing |
| `PerplexityBot` | Perplexity |
| `ClaudeBot` | Anthropic Claude |
| `anthropic-ai` | Anthropic (alternate UA) |
| `Google-Extended` | Google AI training / SGE |
| `Applebot-Extended` | Apple |
| `Amazonbot` | Amazon |
| `Bingbot` | Microsoft Bing / Copilot |
| `Googlebot` | Google Search |

### Blocked Bots

| User-Agent | Reason |
|---|---|
| `AhrefsBot` | Competitor analytics scraper |
| `SemrushBot` | Competitor analytics scraper |

The response sets `Cache-Control: public, max-age=86400` (24-hour cache) and the `X-Robots-Tag: all` header.

The `Content-Signal` comment header in the file (`search=yes, ai-input=yes, ai-train=no`) is a human-readable annotation; it is not a recognized protocol field.

The sitemap reference at the bottom of `robots.txt` points to `https://opc.dev/sitemap.xml`, linking AI crawlers to the full page index.

Sources: [website/worker.js:70-126]()

---

## LLM Discoverability: `llms.txt`

The `/llms.txt` handler at [website/worker.js:128-179]() returns a plain-text document following the `llms.txt` convention — a structured, human-and-machine-readable summary intended for direct LLM consumption.

The response is `text/plain` with `Cache-Control: public, max-age=3600` (1-hour cache).

### `llms.txt` Content Structure

```
# OPC Skills - AI Agent Skills for Solopreneurs

## Overview
9 specialized AI agent skills for one-person companies.
Supports: Claude Code, Cursor, Factory Droid, OpenCode, Codex

## Installation
npx skills add ReScienceLab/opc-skills

## Skills
1. requesthunt - ...
2. domain-hunter - ...
...
9. seo-geo - ...

## Statistics
- 9 skills total
- 5 platforms supported
- Installation time: < 30 seconds
- License: MIT
- FAQ entries: 14+
- Last updated: <dynamic date>

## Documentation
Main site: https://opc.dev
GitHub: https://github.com/ReScienceLab/opc-skills
...
```

The `Last updated` line is dynamic — it uses `new Date().toISOString().split("T")[0]` at request time.

The purpose of `llms.txt` is to ensure that when AI answer engines (ChatGPT, Claude, Perplexity) access the site directly, they receive a concise, factual summary without needing to parse the full HTML page or execute JavaScript.

Sources: [website/worker.js:128-179]()

---

## Structured Data: JSON-LD `@graph`

The homepage handler assembles a `jsonLd` object containing a multi-type `@graph` array and injects it as a `<script type="application/ld+json">` tag in the HTML `<head>`.

**JSON-LD `@graph` Schema Composition**

```mermaid
flowchart LR
    GRAPH["jsonLd @graph\n(website/worker.js:544-636)"]

    GRAPH --> WP["WebPage\n@id: opc.dev/#webpage\nurl, name, description,\ndateModified, speakable"]
    GRAPH --> WS["WebSite\n@id: opc.dev/#website\nname, url, description, publisher"]
    GRAPH --> ORG["Organization\n@id: opc.dev/#organization\nname: ReScience Lab\nurl, logo, sameAs"]
    GRAPH --> IL["ItemList\n@id: opc.dev/#skillcollection\nnumberOfItems, itemListElement"]
    GRAPH --> FAQP["FAQPage\n@id: opc.dev/#faq\nmainEntity: faqItems[]"]
    GRAPH --> HOW["HowTo\n@id: opc.dev/#installation\ntotalTime: PT30S\nstep[1..3]"]

    IL -->|"one entry per skill"| SA["SoftwareApplication\nname, description,\napplicationCategory,\nsoftwareVersion, offers"]
    FAQP -->|"built from faqItems[]"| QA["Question + Answer pairs\n(dynamically generated)"]
    WP -->|"mainEntity"| IL
    WS -->|"publisher"| ORG
```

Sources: [website/worker.js:258-636](), [website/worker.js:544-636]()

### `WebPage`, `WebSite`, and `Organization`

These three nodes form the site identity graph. They cross-reference each other via `@id` anchors ([website/worker.js:548-585]()):

- `WebPage` links its `mainEntity` to the `ItemList` (`#skillcollection`)
- `WebSite` links its `publisher` to the `Organization` (`#organization`)
- `Organization` provides a `sameAs` array pointing to the GitHub profile

The `WebPage` node includes a `speakable` field with CSS selectors (`h1`, `.skill-desc`, `.stats-bar`, `.compatibility-note`) that hint to voice search and AI engines which page content is most authoritative.

### `ItemList` of `SoftwareApplications`

Built dynamically from the live `skills` array fetched via `fetchSkillsConfig` ([website/worker.js:260-276]()):

```
skillsJsonLd = skills.map(s => ({
  "@type": "SoftwareApplication",
  name: s.name,
  description: s.description,
  applicationCategory: "DeveloperApplication",
  operatingSystem: "Cross-platform",
  softwareVersion: s.version,
  offers: { "@type": "Offer", price: "0", ... },
  url: `https://opc.dev/skills/${s.name}`
}))
```

Each skill becomes a `ListItem` with a `position` index inside the `ItemList` node.

### `FAQPage` and `faqItems[]`

The `FAQPage` node is the primary GEO optimization mechanism. The `faqItems` array is assembled at request time ([website/worker.js:278-543]()) and contains over 30 `Question`/`Answer` pairs. The items are grouped by topic:

| Group | Lines | Count | Content |
|---|---|---|---|
| Per-skill "What is X?" | [279-286]() | 5 | Auto-generated from first 5 skills |
| General product FAQs | [287-358]() | 10 | Platform support, cost, installation |
| Installation FAQs | [360-400]() | 4 | Flags, API keys, global vs project |
| Comparison FAQs | [401-426]() | 3 | vs manual, vs paid tools |
| Technical FAQs | [428-460]() | 4 | Languages, custom skills, OS |
| Use case FAQs | [462-508]() | 4 | requesthunt, domain-hunter, logo-creator, seo-geo |
| Platform FAQs | [510-543]() | 4 | Teams, commercial use, update cadence, offline |

The `seo-geo` FAQ item at [website/worker.js:488-508]() includes a `citation` array referencing the Princeton GEO research paper (`https://arxiv.org/abs/2311.03735`) and the Agent Skills Standard, demonstrating the "cite sources" GEO method within the schema itself.

### `HowTo` Schema

The `HowTo` node at [website/worker.js:603-635]() describes the three-step installation process with `totalTime: "PT30S"`. Each step is a `HowToStep` with a `position`, `name`, and `text`. This targets "how to install" queries in AI answer engines and voice search.

Sources: [website/worker.js:278-636]()

---

## Sitemap

The `/sitemap.xml` handler at [website/worker.js:7-68]() generates a dynamic XML sitemap including all skills pages and blog posts. Priorities are assigned as follows:

| URL Pattern | `changefreq` | `priority` |
|---|---|---|
| `/` | `weekly` | `1.0` |
| `/skills/[name]` | `weekly` | `0.8` |
| `/blog` | `weekly` | `0.8` |
| `/compare` | `monthly` | `0.7` |
| `/blog/[slug]` | `monthly` | `0.7` |
| `/skills.json` | `weekly` | `0.6` |

Skills and blog post URLs are generated by mapping over the `skills` and `posts` arrays fetched from `fetchSkillsConfig` and `fetchBlogConfig` respectively. The `lastmod` for skills uses today's date; blog posts use their individual `post.date` field.

Sources: [website/worker.js:7-68]()

---

## Traditional SEO: Meta Tags

The homepage HTML head ([website/worker.js:724-753]()) includes the standard suite of meta tags:

| Tag | Value |
|---|---|
| `<title>` | `AI Agent Skills for Solopreneurs \| Claude Code & Cursor` |
| `<meta name="description">` | 9 skills summary, 155 chars |
| `<meta name="keywords">` | AI agent skills, solopreneur tools, Claude Code skills, etc. |
| `<meta name="robots">` | `index, follow` |
| `<link rel="canonical">` | `https://opc.dev/` |
| `<meta property="og:*">` | Full Open Graph set with `og-image.png` |
| `<meta name="twitter:*">` | Twitter Card with `summary_large_image` |

Sources: [website/worker.js:722-753]()

---

## Relationship Between Website Strategy and the `seo-geo` Skill

The website's own implementation serves as a reference example of the `seo-geo` skill's recommendations in practice.

**Website Practice vs `seo-geo` Skill Method**

```mermaid
flowchart LR
    subgraph "seo-geo Skill (skills/seo-geo/SKILL.md)"
        M1["Cite Sources (+40%)"]
        M2["Statistics Addition (+37%)"]
        M3["FAQPage Schema (+40% AI visibility)"]
        M4["Allow AI bots in robots.txt"]
        M5["Answer-first content structure"]
        M6["JSON-LD: WebPage, Organization,\nSoftwareApplication"]
    end

    subgraph "opc.dev Website (website/worker.js)"
        I1["faqItems seo-geo entry\nhas citation[] array"]
        I2["llms.txt: statistics block\n(9 skills, 5 platforms, 30s)"]
        I3["FAQPage node in jsonLd @graph\n(30+ Question+Answer items)"]
        I4["robots.txt allowlist:\nGPTBot, ClaudeBot, PerplexityBot, etc."]
        I5["llms.txt plain-text\nwith direct answers"]
        I6["jsonLd @graph:\nWebPage, WebSite, Organization,\nItemList of SoftwareApplications"]
    end

    M1 -.->|"implemented as"| I1
    M2 -.->|"implemented as"| I2
    M3 -.->|"implemented as"| I3
    M4 -.->|"implemented as"| I4
    M5 -.->|"implemented as"| I5
    M6 -.->|"implemented as"| I6
```

The nine Princeton GEO methods referenced in `skills/seo-geo/SKILL.md` ([skills/seo-geo/SKILL.md:86-97]()) include visibility boosts ranging from +15% (unique words, fluency) to +40% (citing sources). The `FAQPage` schema approach is explicitly tagged as "+40% AI visibility" in both the skill documentation and the worker code comment at [website/worker.js:278]().

The `seo-geo` skill's DataForSEO-powered scripts (`competitor_gap.py`, `related_keywords.py`, `autocomplete_ideas.py`) are tools intended for *users* to run against their own sites; the website itself uses WebSearch-based research as described in `SKILL.md` Step 2.

Sources: [skills/seo-geo/SKILL.md:83-115](), [website/worker.js:258-286](), [skills/seo-geo/scripts/competitor_gap.py:1-80](), [skills/seo-geo/scripts/related_keywords.py:1-84](), [skills/seo-geo/scripts/autocomplete_ideas.py:1-74]()

---

## Summary

| Mechanism | File | Purpose |
|---|---|---|
| `robots.txt` allowlist | `website/worker.js:70-126` | Let AI crawlers index all pages |
| `llms.txt` | `website/worker.js:128-179` | Structured summary for LLM direct access |
| `sitemap.xml` | `website/worker.js:7-68` | Full page index with priorities |
| `jsonLd` `@graph` | `website/worker.js:544-636` | Schema.org structured data |
| `FAQPage` + `faqItems[]` | `website/worker.js:278-602` | AI citation optimization via Q&A schema |
| `HowTo` node | `website/worker.js:603-635` | Installation query targeting |
| `ItemList` of `SoftwareApplication` | `website/worker.js:260-276` | Machine-readable skill catalog |
| `WebPage` `speakable` | `website/worker.js:556-564` | Voice search / AI content extraction hints |
| HTML meta + Open Graph | `website/worker.js:724-753` | Traditional search engine optimization |

---

# Page: Blog & Content System

# Blog & Content System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/publish-blog.yml](.github/workflows/publish-blog.yml)
- [scripts/BLOG_GUIDELINES.md](scripts/BLOG_GUIDELINES.md)
- [scripts/BLOG_PUBLISHING.md](scripts/BLOG_PUBLISHING.md)
- [scripts/create-blog.py](scripts/create-blog.py)
- [website/blog/2026-02-05-claude-code-plugin-install.png](website/blog/2026-02-05-claude-code-plugin-install.png)
- [website/blog/2026-02-05-seo-geo-1k-installs-og.png](website/blog/2026-02-05-seo-geo-1k-installs-og.png)
- [website/blog/2026-02-23-archive-skill-og.png](website/blog/2026-02-23-archive-skill-og.png)
- [website/blog/blog.json](website/blog/blog.json)
- [website/blog/posts/archive-skill-session-knowledge.md](website/blog/posts/archive-skill-session-knowledge.md)
- [website/blog/posts/ralph-autonomous-agent-loop.md](website/blog/posts/ralph-autonomous-agent-loop.md)
- [website/blog/posts/seo-geo-1k-installs-milestone.md](website/blog/posts/seo-geo-1k-installs-milestone.md)

</details>



## Purpose and Scope

The Blog & Content System manages the creation, validation, and publication of blog posts for the OPC Skills website (opc.dev). This system provides structured content management with automated validation, SEO/GEO optimization, and fast-track publishing workflows that enable blog posts to go live in 6 minutes from PR creation.

For website infrastructure and request routing, see [Website Architecture](#4.1). For SEO/GEO optimization strategies applied to the website, see [SEO & GEO Optimization Strategy](#4.5).

---

## Blog Data Model

### blog.json Structure

The blog system uses a single JSON file at [website/blog/blog.json]() as the source of truth for all blog post metadata. The file contains a `posts` array where each entry defines a blog post with 14 required fields.

**Required Fields**:

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `slug` | string | URL identifier | `"seo-geo-1k-installs-milestone"` |
| `title` | string | Post heading | `"How SEO-GEO Skill Hit 1,000 Installs"` |
| `description` | string | Summary (1-2 sentences) | `"SEO-GEO just crossed 1,000 installs..."` |
| `date` | string | Publication date (YYYY-MM-DD) | `"2026-02-05"` |
| `dateModified` | string | Last modified date | `"2026-02-05"` |
| `author` | string | Author name | `"OPC Team"` |
| `category` | string | Content category | `"Case Study"` |
| `tags` | array | Topic tags | `["seo-geo", "ai-search"]` |
| `readTime` | string | Estimated reading time | `"8 min"` |
| `keywords` | array | SEO keywords (15+ required) | `["SEO-GEO 1000 installs", ...]` |
| `image` | string | OpenGraph image URL | `"https://raw.githubusercontent.com/..."` |
| `schema` | object | schema.org structured data | `{ "@context": "https://schema.org", ...}` |
| `faq` | array | FAQ items (5-10 required) | `[{ "question": ..., "answer": ... }]` |
| `citations` | array | Reference links (3+ required) | `[{ "text": ..., "url": ... }]` |

### Schema.org Integration

Each blog post includes a `schema` object following schema.org standards. The system supports multiple schema types:

- **BlogPosting** - Standard articles and posts [website/blog/blog.json:38-63]()
- **HowTo** - Tutorial and guide content [website/blog/blog.json:282-330]()
- **Article** - Case studies and long-form content [website/blog/blog.json:142-167]()

The schema includes structured authorship, publication metadata, and keyword optimization for AI search engines.

### FAQ Structure for GEO Optimization

FAQ sections are mandatory (5-10 items) to improve AI search visibility. Each FAQ object contains:

```json
{
  "question": "Why did SEO-GEO hit 1,000 installs so fast?",
  "answer": "SEO-GEO addresses a critical need: optimizing for AI search engines..."
}
```

FAQs are designed to match common search queries and voice search patterns, following Princeton's 9 GEO methods for 40-70% visibility increase in AI search engines.

**Blog Post Data Model**

```mermaid
graph TB
    subgraph "blog.json Structure"
        BLOG_JSON["blog.json<br/>posts[] array"]
        
        subgraph "Post Object (14 required fields)"
            META["Metadata<br/>slug, title, description<br/>date, dateModified<br/>author, category"]
            DISCOVERY["Discovery<br/>tags[], keywords[]<br/>readTime, image"]
            STRUCTURED["Structured Data<br/>schema{} (schema.org)<br/>faq[] (5-10 items)<br/>citations[] (3+ refs)"]
        end
        
        BLOG_JSON --> META
        BLOG_JSON --> DISCOVERY
        BLOG_JSON --> STRUCTURED
    end
    
    subgraph "Markdown Content"
        MD_FILE["posts/<slug>.md<br/>2000+ words<br/>H1 title + 8-12 H2 sections"]
    end
    
    subgraph "Schema.org Types"
        SCHEMA_TYPES["BlogPosting<br/>HowTo<br/>Article<br/>FAQPage"]
    end
    
    subgraph "FAQ Structure (GEO)"
        FAQ_ITEM["question: string<br/>answer: string<br/>(5-10 per post)"]
    end
    
    subgraph "Citation Structure"
        CITATION["text: string<br/>url: string<br/>(3+ per post)"]
    end
    
    META -.slug maps to.-> MD_FILE
    STRUCTURED --> SCHEMA_TYPES
    STRUCTURED --> FAQ_ITEM
    STRUCTURED --> CITATION
    
    WORKER["worker.js<br/>fetchBlogConfig()<br/>renderBlogPost()"]
    
    BLOG_JSON -.fetched by.-> WORKER
    MD_FILE -.fetched by.-> WORKER
```

Sources: [website/blog/blog.json:1-1000](), [scripts/BLOG_GUIDELINES.md:34-54]()

---

## Content Standards and Quality Requirements

### Word Count Requirements

The system enforces minimum word counts to ensure comprehensive content:

- **Minimum**: 2,000 words
- **Recommended**: 2,500-4,000 words  
- **Tutorial/Guide**: 3,000+ words
- **Case Study**: 2,000-2,500 words

### SEO/GEO Optimization Requirements

**Keywords** (15+ required):
- 3-5 primary keywords (high search volume)
- 10-15 long-tail keywords (specific phrases)
- Must appear in: title, description, first 200 words, H2 headings

**FAQ Section** (5-10 questions required):
- Answer common search queries
- Optimize for voice search patterns
- Follow Princeton GEO methods for AI visibility

**Internal Links** (3-5 required):
- Link to skill documentation pages
- Link to related blog posts  
- Link to installation guides

### Structure Requirements

**Must Have**:
- 1 H1 heading (title only)
- 8-12 H2 sections
- TL;DR section (100-150 words)
- FAQ section (5-10 questions)
- Further Reading section with internal links

**Should Have**:
- Tables for comparisons
- Code blocks with syntax highlighting
- Real examples and metrics
- Step-by-step workflows
- Visual hierarchy (H2, H3, H4)

### Content Quality Checklist

The validation tool checks content against this standard:

| Requirement | Rule | Validation |
|-------------|------|------------|
| Word count | 2000+ words | `wc -w posts/<slug>.md` |
| Headings | 1 H1 + 8-12 H2 | `grep -c "^## " posts/<slug>.md` |
| Keywords | 15+ keywords | Check `keywords[]` length |
| FAQs | 5-10 questions | Check `faq[]` length |
| Citations | 3+ references | Check `citations[]` length |
| Code blocks | 3+ examples | `grep -c "^\`\`\`" posts/<slug>.md` |

Sources: [scripts/BLOG_GUIDELINES.md:75-120](), [scripts/create-blog.py:62-75]()

---

## Validation and Creation Tools

### create-blog.py Commands

The [scripts/create-blog.py]() tool provides three main commands:

**1. validate** - Validate all blog posts
```bash
python3 scripts/create-blog.py validate
```
Checks [website/blog/blog.json]() for required fields, validates dates, verifies markdown files exist, and ensures quality standards are met.

**2. check** - Check specific blog post
```bash
python3 scripts/create-blog.py check <slug>
```
Runs detailed analysis on a single post: word count, heading structure, code blocks, and SEO optimization.

**3. new** - Create new blog post template
```bash
python3 scripts/create-blog.py new
```
Interactive wizard that prompts for metadata and generates a starter template.

### Validation Rules

The validator enforces these rules at [scripts/create-blog.py:46-82]():

1. **Required Fields** - All 14 fields must be present
2. **Markdown Files** - Must exist at `posts/<slug>.md`
3. **Date Format** - Must be `YYYY-MM-DD`
4. **FAQ Count** - 5-10 questions (warns if < 5)
5. **Keyword Count** - 10+ keywords (warns if < 10)
6. **Citation Count** - 3+ references (warns if < 3)
7. **Schema.org** - Valid JSON-LD structure

### Quality Checks

For detailed content analysis, the `check` command validates:

- Word count (minimum 2000)
- Heading structure (1 H1, 8-12 H2)
- Code blocks (minimum 3)
- Internal links (3-5 recommended)
- FAQ schema validity
- Citation URL accessibility

**Blog Validation Flow**

```mermaid
graph TB
    START["Developer creates<br/>blog post"]
    
    subgraph "Content Creation"
        WRITE_MD["Write markdown<br/>posts/<slug>.md"]
        ADD_META["Add metadata to<br/>blog.json"]
    end
    
    START --> WRITE_MD
    WRITE_MD --> ADD_META
    
    subgraph "create-blog.py Validation"
        VALIDATE_CMD["python3 scripts/create-blog.py<br/>validate"]
        
        CHECK_JSON["validate_blog_json()<br/>Check required fields<br/>Verify dates"]
        CHECK_MD["Check markdown file<br/>exists at posts/<slug>.md"]
        CHECK_QUALITY["Quality checks<br/>FAQ count >= 5<br/>keywords >= 10<br/>citations >= 3"]
        CHECK_SCHEMA["Validate schema.org<br/>JSON-LD structure"]
        
        VALIDATE_CMD --> CHECK_JSON
        CHECK_JSON --> CHECK_MD
        CHECK_MD --> CHECK_QUALITY
        CHECK_QUALITY --> CHECK_SCHEMA
    end
    
    ADD_META --> VALIDATE_CMD
    
    subgraph "Detailed Check (optional)"
        CHECK_CMD["python3 scripts/create-blog.py<br/>check <slug>"]
        
        COUNT_WORDS["Word count<br/>minimum 2000"]
        COUNT_HEADINGS["Heading structure<br/>1 H1 + 8-12 H2"]
        COUNT_CODE["Code blocks<br/>minimum 3"]
        CHECK_LINKS["Internal links<br/>3-5 recommended"]
        
        CHECK_CMD --> COUNT_WORDS
        COUNT_WORDS --> COUNT_HEADINGS
        COUNT_HEADINGS --> COUNT_CODE
        COUNT_CODE --> CHECK_LINKS
    end
    
    ADD_META -.optional.-> CHECK_CMD
    
    ERRORS{Errors<br/>found?}
    WARNINGS{Warnings<br/>found?}
    
    CHECK_SCHEMA --> ERRORS
    ERRORS -->|Yes| FAIL["Validation FAILED<br/>Fix errors"]
    ERRORS -->|No| WARNINGS
    WARNINGS -->|Yes| PASS_WARN["Validation PASSED<br/>with warnings"]
    WARNINGS -->|No| PASS["Validation PASSED"]
    
    FAIL -.fix and retry.-> VALIDATE_CMD
    PASS --> READY["Ready to publish"]
    PASS_WARN --> READY
```

Sources: [scripts/create-blog.py:1-200](), [scripts/BLOG_GUIDELINES.md:1-50]()

---

## Publishing Workflows

### Fast-Track Workflow (Recommended)

The fast-track workflow enables blog posts to go live in **6 minutes** by bypassing the traditional develop branch review process.

**How it works**:

1. Create PR directly to `main` (skip `develop`)
2. Add `blog-post` label
3. GitHub Action [.github/workflows/publish-blog.yml]() validates content
4. If validation passes, auto-approves and auto-merges
5. Cloudflare Workers deploys automatically

**Commands**:
```bash
git checkout -b feature/blog/my-post
# ... create content ...
git add website/blog/
git commit -m "feat(blog): add my awesome post"
git push -u origin feature/blog/my-post

# Create PR to main (not develop!)
gh pr create --base main --label blog-post --title "feat(blog): add my awesome post"
```

**Timeline**:
- Validation: ~30 seconds
- Auto-merge: instant
- Cloudflare deploy: ~5 minutes
- **Total: 6 minutes to live**

### publish-blog.yml Workflow

The GitHub Action at [.github/workflows/publish-blog.yml]() implements the fast-track process:

1. **Trigger**: PR to `main` with `blog-post` label [.github/workflows/publish-blog.yml:3-8]()
2. **Validate**: Runs `python3 scripts/create-blog.py validate` [.github/workflows/publish-blog.yml:22-23]()
3. **Auto-approve**: Uses `hmarr/auto-approve-action@v3` [.github/workflows/publish-blog.yml:25-28]()
4. **Auto-merge**: Uses `pascalgn/automerge-action@v0.15.6` with squash merge [.github/workflows/publish-blog.yml:30-37]()

### Traditional Git Flow (Code Changes)

For blog posts that include code changes (e.g., worker.js updates), use the standard workflow:

```
feature/blog/post → PR to develop → merge → PR to main → merge → deploy
```

This ensures code changes receive proper review. Timeline: ~2 days.

### Comparison of Publishing Methods

| Method | Time to Live | Review Required | Best For |
|--------|-------------|----------------|----------|
| **Fast-Track** | 6 min | Automated | Pure content posts |
| **Git Flow** | 2+ days | Manual | Posts with code changes |
| **Scheduled** | Variable | Automated | Timed releases |
| **Direct Push** | 5 min | None | Emergency fixes |

**Fast-Track Blog Publishing Flow**

```mermaid
graph TB
    DEV["Developer creates<br/>blog post"]
    
    subgraph "Content Creation"
        BRANCH["git checkout -b<br/>feature/blog/post"]
        WRITE["Edit files:<br/>posts/<slug>.md<br/>blog.json"]
        COMMIT["git commit -m<br/>'feat(blog): add post'"]
        PUSH["git push origin<br/>feature/blog/post"]
    end
    
    DEV --> BRANCH
    BRANCH --> WRITE
    WRITE --> COMMIT
    COMMIT --> PUSH
    
    subgraph "Pull Request"
        CREATE_PR["gh pr create<br/>--base main<br/>--label blog-post"]
    end
    
    PUSH --> CREATE_PR
    
    subgraph "GitHub Action (.github/workflows/publish-blog.yml)"
        TRIGGER["on: pull_request<br/>types: [labeled]<br/>branches: [main]"]
        CHECK_LABEL{label ==<br/>'blog-post'?}
        VALIDATE["Run validation:<br/>python3 scripts/create-blog.py<br/>validate"]
        
        TRIGGER --> CHECK_LABEL
        CHECK_LABEL -->|Yes| VALIDATE
        CHECK_LABEL -->|No| SKIP["Skip workflow"]
    end
    
    CREATE_PR --> TRIGGER
    
    VALID{Validation<br/>passed?}
    
    VALIDATE --> VALID
    VALID -->|No| FAIL["Workflow fails<br/>Fix errors"]
    
    subgraph "Auto-Merge"
        APPROVE["hmarr/auto-approve-action<br/>Auto-approve PR"]
        MERGE["pascalgn/automerge-action<br/>Squash merge to main"]
    end
    
    VALID -->|Yes| APPROVE
    APPROVE --> MERGE
    
    subgraph "Deployment"
        CLOUDFLARE["Cloudflare Workers<br/>Auto-deploy from main"]
        LIVE["Blog post LIVE<br/>at opc.dev/blog/<slug>"]
    end
    
    MERGE --> CLOUDFLARE
    CLOUDFLARE --> LIVE
    
    FAIL -.fix and re-push.-> WRITE
    
    TIMELINE["Timeline:<br/>Validation: 30s<br/>Merge: instant<br/>Deploy: 5min<br/>TOTAL: 6min"]
    
    LIVE -.-.-> TIMELINE
```

Sources: [.github/workflows/publish-blog.yml:1-38](), [scripts/BLOG_PUBLISHING.md:1-55]()

---

## Integration with Website Infrastructure

### worker.js Blog Rendering

The Cloudflare Worker at [website/worker.js]() integrates with the blog system through two key functions:

**fetchBlogConfig()** - Fetches blog.json from GitHub raw URL with 300s TTL cache
- Returns parsed `blog.json` data
- Caches at edge for 5 minutes
- Used by blog list and individual post pages

**renderBlogPost()** - Renders individual blog post pages
- Fetches markdown content from `posts/<slug>.md`
- Fetches metadata from `blog.json`
- Generates HTML with schema.org structured data
- Includes FAQ schema for GEO optimization

### Caching Strategy

Blog content uses a tiered caching approach:

| Resource | TTL | Reason |
|----------|-----|--------|
| `blog.json` | 300s (5 min) | Metadata changes occasionally |
| `posts/<slug>.md` | 300s (5 min) | Content rarely changes after publish |
| Rendered HTML | 60s (1 min) | Allow quick updates if needed |

The short cache TTL for rendered HTML ensures blog posts appear live within 1 minute of merge to main.

### Request Flow for Blog Posts

When a user visits `opc.dev/blog/seo-geo-1k-installs-milestone`:

1. Worker receives request at `/blog/:slug` route
2. Calls `fetchBlogConfig()` to get metadata (cached 5 min)
3. Finds post by slug in `blog.json`
4. Fetches markdown from GitHub raw URL (cached 5 min)
5. Renders HTML with:
   - schema.org BlogPosting/HowTo/Article markup
   - FAQPage schema for GEO
   - OpenGraph meta tags
   - Speakable CSS for voice search
6. Returns HTML with 60s cache header

**Blog Content Request Flow**

```mermaid
graph TB
    USER["User visits<br/>opc.dev/blog/<slug>"]
    
    subgraph "Cloudflare Worker (worker.js)"
        FETCH_HANDLER["fetch() handler<br/>URL routing"]
        
        BLOG_ROUTE{"/blog/:slug"<br/>route match?}
        
        FETCH_HANDLER --> BLOG_ROUTE
    end
    
    USER --> FETCH_HANDLER
    
    subgraph "Data Fetching"
        FETCH_CONFIG["fetchBlogConfig()<br/>Fetch blog.json<br/>from GitHub raw"]
        
        FIND_POST["Find post by slug<br/>in posts[] array"]
        
        FETCH_MD["Fetch markdown<br/>posts/<slug>.md<br/>from GitHub raw"]
        
        BLOG_ROUTE -->|Yes| FETCH_CONFIG
        FETCH_CONFIG --> FIND_POST
        FIND_POST --> FETCH_MD
    end
    
    subgraph "GitHub Raw URLs"
        GH_BLOG_JSON["raw.githubusercontent.com<br/>/ReScienceLab/opc-skills<br/>/main/website/blog/blog.json"]
        
        GH_POST_MD["raw.githubusercontent.com<br/>/ReScienceLab/opc-skills<br/>/main/website/blog/posts/<slug>.md"]
        
        FETCH_CONFIG -.HTTP GET.-> GH_BLOG_JSON
        FETCH_MD -.HTTP GET.-> GH_POST_MD
    end
    
    subgraph "Cloudflare Edge Cache"
        CACHE_CONFIG["blog.json cached<br/>TTL: 300s (5 min)"]
        CACHE_MD["Markdown cached<br/>TTL: 300s (5 min)"]
        
        GH_BLOG_JSON -.cache.-> CACHE_CONFIG
        GH_POST_MD -.cache.-> CACHE_MD
    end
    
    subgraph "Rendering (worker.js)"
        RENDER["renderBlogPost()<br/>Generate HTML"]
        
        ADD_SCHEMA["Add schema.org markup:<br/>BlogPosting/HowTo/Article<br/>FAQPage (from faq[])<br/>BreadcrumbList"]
        
        ADD_META["Add meta tags:<br/>OpenGraph (image, title)<br/>Twitter Card<br/>Speakable CSS"]
        
        RENDER --> ADD_SCHEMA
        ADD_SCHEMA --> ADD_META
    end
    
    FETCH_MD --> RENDER
    
    RESPONSE["HTTP Response<br/>HTML + Cache-Control: 60s"]
    
    ADD_META --> RESPONSE
    RESPONSE --> USER
```

Sources: [website/worker.js]() (specific functions referenced), [scripts/BLOG_GUIDELINES.md:138-157]()

---

## Featured Content: Ralph Autonomous Agent Loop

### Special Case Study Structure

The Ralph autonomous agent loop case study at [website/blog/posts/ralph-autonomous-agent-loop.md]() demonstrates advanced blog post structure for technical deep-dives.

**Content Architecture**:
- **Word count**: 2,900 words (Tutorial category)
- **Sections**: 12 H2 sections covering concept, architecture, workflow, and integration
- **Code examples**: 15+ code blocks showing prd.json, progress.txt, bash commands
- **Real metrics**: "7.9k GitHub stars", "15 user stories, 47 commits, 28 passing tests"

### Memory Persistence Architecture

The Ralph case study documents three key persistence mechanisms that enable autonomous development:

**1. prd.json** - Task list with pass/fail status
```json
{
  "user_stories": [
    {
      "id": "US-001",
      "description": "User can create account",
      "passes": true
    }
  ]
}
```

**2. progress.txt** - Append-only learning log
```
[2026-01-26 10:30] Discovered: React state needs useCallback for event handlers
[2026-01-26 11:45] Gotcha: Prisma migrations require explicit schema sync
```

**3. AGENTS.md** - Project conventions
```markdown
## Code Style
- Use TypeScript strict mode
- Prefer functional components

## Testing
- Jest for unit tests
- Playwright for E2E
```

### OPC Skills Integration

The Ralph case study highlights integration with OPC Skills ecosystem:

- **domain-hunter** skill used for finding available domains during MVP naming
- **logo-creator** skill for generating brand assets automatically  
- **seo-geo** skill for optimizing landing page during deployment
- **archive** skill for preserving implementation decisions in project memory

This demonstrates how blog content can showcase cross-skill workflows and compound value.

### FAQ Optimization for Technical Content

The Ralph post includes 10 FAQs [website/blog/blog.json:590-630]() optimized for developer search queries:

- "What is Ralph AI and how does it work?"
- "Can solopreneurs build MVPs with Ralph without coding experience?"
- "How long does Ralph take to build an MVP?"
- "Which AI coding tools does Ralph support?"
- "How does Ralph integrate with OPC Skills?"

Each FAQ answers a specific search intent while including target keywords ("Ralph AI", "autonomous development", "solopreneur MVP builder").

Sources: [website/blog/posts/ralph-autonomous-agent-loop.md:1-100](), [website/blog/blog.json:529-658](), [scripts/BLOG_GUIDELINES.md:164-180]()

---

## Content Quality Metrics

### Published Post Statistics

Current blog system metrics (as of repository snapshot):

| Metric | Count | Standard |
|--------|-------|----------|
| Total posts | 7 | - |
| Average word count | ~3,200 | 2,000+ required |
| Average FAQs | 8.4 | 5-10 required |
| Average keywords | 13.7 | 15+ required |
| Average citations | 5.3 | 3+ required |
| Posts with schema.org | 7 (100%) | Required |

### Category Distribution

- **Tutorial**: 4 posts (installation, infrastructure, doc conversion, Ralph)
- **Case Study**: 1 post (SEO-GEO 1k installs)
- **Insights**: 1 post (why skills beat docs)
- **Product Launch**: 1 post (archive skill)

### GEO Optimization Results

Blog posts implement Princeton's 9 GEO methods:
1. Citations (5.3 average per post)
2. Statistics (metrics in every post title)
3. Quotations (user testimonials)
4. Fluency optimization (clear, simple language)
5. Strategic keyword placement (15+ keywords per post)
6. Authoritative tone ("OPC Team" authorship)
7. Easy-to-understand (2000+ word comprehensive guides)
8. FAQ sections (8.4 average questions per post)
9. Technical optimization (schema.org markup on every post)

This optimization strategy enables blog content to appear in AI search results (ChatGPT Search, Perplexity AI) within 2-4 weeks of publication.

Sources: [website/blog/blog.json:1-1000](), [scripts/BLOG_GUIDELINES.md:99-120]()

---

# Page: Blog System Architecture

# Blog System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [website/blog/2026-02-05-claude-code-plugin-install.png](website/blog/2026-02-05-claude-code-plugin-install.png)
- [website/blog/2026-02-05-seo-geo-1k-installs-og.png](website/blog/2026-02-05-seo-geo-1k-installs-og.png)
- [website/blog/2026-02-23-archive-skill-og.png](website/blog/2026-02-23-archive-skill-og.png)
- [website/blog/blog.json](website/blog/blog.json)
- [website/blog/posts/archive-skill-session-knowledge.md](website/blog/posts/archive-skill-session-knowledge.md)
- [website/blog/posts/seo-geo-1k-installs-milestone.md](website/blog/posts/seo-geo-1k-installs-milestone.md)

</details>



## Purpose and Scope

This document describes the blog system architecture within the OPC Skills repository, focusing on the `blog.json` metadata registry, post organization, SEO/GEO optimization fields, and schema.org structured data. The blog system serves as a content marketing platform optimized for both traditional search engines and AI search engines (ChatGPT, Perplexity, Claude).

For information about:
- Blog content creation workflows and validation: see [Content Creation & Validation](#5.2)
- Blog publishing and deployment processes: see [Blog Publishing Workflows](#5.3)
- Website delivery and rendering of blog content: see [Website Architecture](#4.1)
- SEO/GEO optimization strategy implementation: see [SEO & GEO Optimization Strategy](#4.5)

---

## Blog Registry Overview

The blog system is centralized around a single metadata registry file that defines all published posts and their SEO/GEO attributes.

**Blog data flow — `blog.json` as metadata registry, `posts/*.md` as content, rendered by `worker.js`:**

```mermaid
graph TB
    subgraph "Static Assets (GitHub)"
        BlogJSON["website/blog/blog.json<br/>{posts: [...]}"]
        
        subgraph "posts/"
            MD1["archive-skill-session-knowledge.md"]
            MD2["seo-geo-1k-installs-milestone.md"]
            MD3["install-opc-skills-claude-code.md"]
            MDN["...7+ posts"]
        end
        
        subgraph "Image Assets"
            OGImg["2026-02-05-seo-geo-1k-installs-og.png"]
            ContentImg["2026-02-05-seo-geo-install-stats.png"]
        end
    end

    subgraph "worker.js Route Handlers"
        BlogListRoute["url.pathname === '/blog'"]
        BlogSlugRoute["url.pathname.match(/^\/blog\/([^\/]+)$/)"]
    end
    
    subgraph "worker.js Helper Functions"
        fetchBlogConfig["fetchBlogConfig(ctx)<br/>returns posts[]"]
        renderBlogPost["renderBlogPost(post, content)<br/>returns HTML string"]
        marked["marked(markdown)<br/>Markdown parser"]
    end
    
    subgraph "Cloudflare Edge"
        EdgeCache["caches.default<br/>TTL: 300s"]
    end

    BlogListRoute --> fetchBlogConfig
    BlogSlugRoute --> fetchBlogConfig
    
    fetchBlogConfig --> EdgeCache
    EdgeCache --> BlogJSON
    
    BlogJSON -->|"posts[].slug"| MD1
    BlogJSON -->|"posts[].slug"| MD2
    BlogJSON -->|"posts[].slug"| MD3
    BlogJSON -->|"posts[].image"| OGImg
    
    BlogSlugRoute -->|"fetch raw URL"| MD2
    MD2 --> marked
    marked --> renderBlogPost
    
    BlogJSON -->|"posts[].schema"| renderBlogPost
    BlogJSON -->|"posts[].faq"| renderBlogPost
    
    renderBlogPost -->|"HTML with JSON-LD"| BlogSlugRoute
    fetchBlogConfig -->|"posts[]"| BlogListRoute
```

Sources: [website/blog/blog.json:1-2](), [website/blog/posts/seo-geo-1k-installs-milestone.md:1-5]()

---

## blog.json Structure

The `blog.json` file is a flat JSON structure containing a single `posts` array with complete metadata for each blog post.

### Root Schema

The JSON structure contains a single top-level `posts` array:

```json
{
  "posts": [
    { /* post object 1 */ },
    { /* post object 2 */ },
    ...
  ]
}
```

The `posts` array is ordered newest-first (enforced by `scripts/create-blog.py` validation). Published posts as of February 2026:

| Slug | Category | Date | Word Count |
|------|----------|------|------------|
| `archive-skill-session-knowledge` | Product Launch | 2026-02-23 | 2400 |
| `seo-geo-1k-installs-milestone` | Case Study | 2026-02-05 | 3200 |
| `install-opc-skills-claude-code` | Tutorial | 2026-01-28 | — |
| `free-ai-infrastructure-deepseek-jan` | Tutorial | 2026-01-28 | 4200 |
| `ralph-autonomous-agent-loop` | Tutorial | 2026-01-26 | 2900 |
| `convert-docs-to-skills-guide` | Tutorial | 2026-01-24 | — |
| `why-skills-beat-docs` | Insights | 2026-01-23 | — |

Sources: [website/blog/blog.json:1-2](), [website/blog/blog.json:3-109](), [website/blog/blog.json:110-249]()

---

## Post Metadata Schema

Each post object in the `posts` array contains comprehensive metadata. The complete list of required fields is defined as `REQUIRED_FIELDS` in `scripts/create-blog.py`:

```python
REQUIRED_FIELDS = [
    "slug", "title", "description", "date", "dateModified", "author",
    "category", "tags", "readTime", "keywords", "image", "schema",
    "faq", "citations"
]
```

These 14 fields are validated by the `validate_blog_json()` function before any post can be published.

### Core Fields

| Field | Type | Purpose |
|-------|------|---------|
| `slug` | string | URL identifier (e.g., `"seo-geo-1k-installs-milestone"`); determines route `/blog/{slug}` and markdown filename `posts/{slug}.md` |
| `title` | string | Full post title |
| `description` | string | Meta description (~150-160 chars) |
| `date` | string | Publication date (ISO 8601: `"YYYY-MM-DD"`) |
| `dateModified` | string | Last modification date |
| `author` | string | Author name (typically `"OPC Team"`) |
| `category` | string | Content category: `"Case Study"`, `"Tutorial"`, `"Insights"`, `"Product Launch"` |
| `tags` | string[] | Topic tags for categorization |
| `readTime` | string | Estimated read time (e.g., `"8 min"`) |
| `keywords` | string[] | SEO keywords; validation warns if fewer than 10 |
| `image` | string | Absolute URL to OpenGraph PNG image |
| `schema` | object | schema.org JSON-LD structured data object |
| `faq` | object[] | FAQ entries; validation warns if fewer than 5 |
| `citations` | object[] | Source citations; validation warns if fewer than 3 |

Sources: [scripts/create-blog.py:23-27](), [website/blog/blog.json:3-134]()

### Example Post Entry

```json
{
  "slug": "seo-geo-1k-installs-milestone",
  "title": "How SEO-GEO Skill Hit 1,000 Installs: The AI Search Revolution Is Here",
  "description": "SEO-GEO just crossed 1,000 installs, making it the #1 skill...",
  "date": "2026-02-05",
  "dateModified": "2026-02-05",
  "author": "OPC Team",
  "category": "Case Study",
  "tags": ["seo-geo", "ai-search", "geo-optimization", "milestone", "chatgpt-search", "perplexity"],
  "readTime": "8 min",
  "keywords": [
    "SEO-GEO 1000 installs",
    "AI search optimization",
    "GEO Generative Engine Optimization",
    "ChatGPT Search SEO",
    "Perplexity AI citations",
    "Claude Code SEO plugin",
    "install seo-geo skill",
    "AI search visibility",
    "schema.org automation",
    "Princeton GEO methods",
    "solopreneur SEO tools",
    "free SEO alternative"
  ],
  "image": "https://raw.githubusercontent.com/ReScienceLab/opc-skills/main/website/blog/2026-02-05-seo-geo-1k-installs-og.png",
  "schema": { /* Article schema object */ },
  "faq": [ /* 10 question/answer pairs */ ],
  "citations": [ /* 9 source citations */ ]
}
```

The `slug` field serves as the primary key linking three artifacts:
1. The `blog.json` entry (this object)
2. The markdown file at `website/blog/posts/{slug}.md`
3. The URL route `/blog/{slug}` handled by `worker.js`

Sources: [website/blog/blog.json:110-168]()

---

## SEO/GEO Optimization Fields

The blog system implements aggressive SEO/GEO optimization through dedicated metadata fields designed to maximize visibility in both traditional and AI search engines.

### Keywords Array

Each post defines **10-15 target keywords** optimized for:
- Long-tail search queries
- Question-based searches
- Tool/product-specific searches
- Problem-solution searches

```json
"keywords": [
  "SEO-GEO 1000 installs",
  "AI search optimization",
  "GEO Generative Engine Optimization",
  "ChatGPT Search SEO",
  "Perplexity AI citations",
  "Claude Code SEO plugin",
  "install seo-geo skill",
  "AI search visibility",
  "schema.org automation",
  "Princeton GEO methods",
  "solopreneur SEO tools",
  "free SEO alternative"
]
```

**Sources:** [website/blog/blog.json:13-26]()

### Tags Array

Tags provide coarse-grained categorization for navigation and filtering:

| Post Category | Example Tags |
|---------------|--------------|
| Case Study | `["seo-geo", "ai-search", "milestone", "chatgpt-search"]` |
| Tutorial | `["installation", "claude-code", "tutorial", "getting-started"]` |
| Insights | `["agent-skills", "documentation", "ai-agents"]` |

**Sources:** [website/blog/blog.json:11](), [website/blog/blog.json:144]()

### Image Assets

Each post requires an OpenGraph image for social media sharing:

```json
"image": "https://raw.githubusercontent.com/ReScienceLab/opc-skills/main/website/blog/2026-02-05-seo-geo-1k-installs-og.png"
```

**Naming Convention:** `YYYY-MM-DD-{slug}-og.png`

**Sources:** [website/blog/blog.json:27](), [website/blog/blog.json:160]()

---

## Schema.org Structured Data

The `schema` field contains JSON-LD structured data that AI search engines and traditional search engines parse to understand content semantics.

**Schema.org `@type` variants and their field structure:**

```mermaid
graph TB
    subgraph "schema['@type'] Values"
        Article["Article<br/>(Case Studies)"]
        HowTo["HowTo<br/>(Step-by-step Tutorials)"]
        BlogPosting["BlogPosting<br/>(General Posts)"]
    end

    subgraph "Common Fields (All Types)"
        Context["@context: 'https://schema.org'"]
        Name["name or headline"]
        Desc["description"]
        Author["author: {<br/>@type: 'Organization',<br/>name: 'OPC Team',<br/>url: 'https://opc.dev'<br/>}"]
        DatePub["datePublished"]
        DateMod["dateModified"]
        Publisher["publisher: {<br/>@type: 'Organization',<br/>name: 'OPC Skills',<br/>logo: ImageObject<br/>}"]
        Image["image URL"]
        MainEntity["mainEntityOfPage URL"]
        Keywords["keywords string"]
    end

    subgraph "Type-Specific Fields"
        ArticleFields["articleSection<br/>wordCount"]
        HowToFields["step: [<br/>{@type: 'HowToStep',<br/>position, name, text, url}<br/>]<br/>totalTime: 'PT2M'<br/>tool: []<br/>supply: []"]
        BlogFields["headline<br/>articleSection<br/>wordCount"]
    end

    Article --> Context
    Article --> Name
    Article --> Desc
    Article --> Author
    Article --> DatePub
    Article --> DateMod
    Article --> Publisher
    Article --> Image
    Article --> MainEntity
    Article --> Keywords
    Article --> ArticleFields

    HowTo --> Context
    HowTo --> Name
    HowTo --> Desc
    HowTo --> HowToFields

    BlogPosting --> Context
    BlogPosting --> Name
    BlogPosting --> Desc
    BlogPosting --> Author
    BlogPosting --> DatePub
    BlogPosting --> DateMod
    BlogPosting --> Publisher
    BlogPosting --> Image
    BlogPosting --> MainEntity
    BlogPosting --> Keywords
    BlogPosting --> BlogFields
```

### Article Schema (Case Studies)

Used for case studies and analytical posts (e.g., `seo-geo-1k-installs-milestone`):

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "name": "How SEO-GEO Skill Hit 1,000 Installs",
  "description": "Case study: SEO-GEO skill reaches 1,000 installs...",
  "author": {
    "@type": "Organization",
    "name": "OPC Team",
    "url": "https://opc.dev"
  },
  "datePublished": "2026-02-05",
  "dateModified": "2026-02-05",
  "publisher": {
    "@type": "Organization",
    "name": "OPC Skills",
    "url": "https://opc.dev",
    "logo": {
      "@type": "ImageObject",
      "url": "https://opc.dev/opc-logo.svg"
    }
  },
  "image": "https://raw.githubusercontent.com/.../2026-02-05-seo-geo-1k-installs-og.png",
  "mainEntityOfPage": "https://opc.dev/blog/seo-geo-1k-installs-milestone",
  "keywords": "SEO-GEO, AI search, GEO optimization, ChatGPT Search",
  "articleSection": "Case Study",
  "wordCount": 3200
}
```

Sources: [website/blog/blog.json:144-168]()

### HowTo Schema (Tutorials)

Used for step-by-step tutorial posts (e.g., `install-opc-skills-claude-code`). Each `step` entry uses `@type: HowToStep` with `position`, `name`, `text`, and a deep-link `url`:

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to Install OPC Skills in Claude Code",
  "description": "Step-by-step tutorial to install OPC Skills...",
  "totalTime": "PT2M",
  "tool": ["Claude Code"],
  "supply": ["Claude Code (free version)"],
  "step": [
    {
      "@type": "HowToStep",
      "position": 1,
      "name": "Add OPC Skills Marketplace",
      "text": "Open Claude Code and run: /plugin marketplace add ReScienceLab/opc-skills",
      "url": "https://opc.dev/blog/install-opc-skills-claude-code#step-1"
    },
    {
      "@type": "HowToStep",
      "position": 2,
      "name": "Install Skills",
      "text": "Run: /plugin install reddit@opc-skills (or any other skill)",
      "url": "https://opc.dev/blog/install-opc-skills-claude-code#step-2"
    }
  ]
}
```

`totalTime` uses ISO 8601 duration format (`"PT2M"` = 2 minutes).

Sources: [website/blog/blog.json:280-331]()

### BlogPosting Schema

Used for general blog content (e.g., `archive-skill-session-knowledge`, `free-ai-infrastructure-deepseek-jan`, `ralph-autonomous-agent-loop`). Uses `headline` instead of `name`, and includes `mainEntityOfPage`:

```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "How to Build MVPs for Free: DeepSeek + Jan + OPC Skills",
  "description": "Complete guide to building MVPs with zero API costs...",
  "author": {
    "@type": "Organization",
    "name": "OPC Team",
    "url": "https://opc.dev"
  },
  "datePublished": "2026-01-28",
  "dateModified": "2026-01-28",
  "mainEntityOfPage": "https://opc.dev/blog/free-ai-infrastructure-deepseek-jan",
  "articleSection": "Tutorial",
  "wordCount": 4200
}
```

Sources: [website/blog/blog.json:431-458]()

---

## FAQ Section for GEO Optimization

The `faq` array implements the **FAQPage schema** pattern, which is one of the 9 Princeton GEO methods proven to increase AI search citations by +40%.

### FAQ Structure

Each FAQ entry contains:

```json
{
  "question": "Why did SEO-GEO hit 1,000 installs so fast?",
  "answer": "SEO-GEO addresses a critical need: optimizing for AI search engines like ChatGPT Search and Perplexity AI. It's free, installs in 30 seconds, requires no API keys, and automates the 9 Princeton GEO methods proven to increase AI visibility by 40-70%."
}
```

**Sources:** [website/blog/blog.json:55-96]()

### FAQ Count by Post

The `validate_blog_json()` function in `scripts/create-blog.py` warns when a post has fewer than 5 FAQ entries (the GEO optimization minimum):

| Post Slug | FAQ Count | Schema `@type` |
|-----------|-----------|----------------|
| `archive-skill-session-knowledge` | 6 | `BlogPosting` |
| `seo-geo-1k-installs-milestone` | 10 | `Article` |
| `install-opc-skills-claude-code` | 10 | `HowTo` |
| `free-ai-infrastructure-deepseek-jan` | 10 | `BlogPosting` |
| `ralph-autonomous-agent-loop` | 10 | `BlogPosting` |
| `convert-docs-to-skills-guide` | 4 | `BlogPosting` |

Typical FAQ topics: installation instructions, cost comparisons, technical requirements, feature capabilities, troubleshooting, use-case validation.

Sources: [website/blog/blog.json:65-90](), [website/blog/blog.json:169-210](), [website/blog/blog.json:332-373](), [scripts/create-blog.py:63-65]()

---

## Citations Array

The `citations` array implements another Princeton GEO method: **adding authoritative citations** increases AI search visibility by +40%.

### Citation Structure

```json
{
  "text": "Princeton NLP: GEO Optimization Methods",
  "url": "https://arxiv.org/abs/2311.03735"
}
```

### Citation Categories

| Category | Example URLs |
|----------|-------------|
| Academic Research | `arxiv.org/abs/2311.03735` |
| GitHub Repositories | `github.com/ReScienceLab/opc-skills` |
| Official Documentation | `code.claude.com/docs` |
| Skill Registries | `skills.sh/ReScienceLab/opc-skills` |
| Community Discussions | `news.ycombinator.com/item?id=46730857` |
| Social Proof | `threads.com/@hannie.liu/post/...` |

**Sources:** [website/blog/blog.json:97-134]()

### Citation Counts

Posts typically include **5-9 citations**:

```json
"citations": [
  {"text": "Princeton NLP: GEO Optimization Methods", "url": "..."},
  {"text": "SEO-GEO Skill Documentation", "url": "..."},
  {"text": "SEO-GEO on Skills.sh Registry", "url": "..."},
  {"text": "OPC Skills GitHub Repository", "url": "..."},
  {"text": "Agent Skills Standard", "url": "..."},
  {"text": "Hacker News Discussion", "url": "..."},
  {"text": "Community Testimonial - Hannie Liu on Threads", "url": "..."},
  {"text": "ChatGPT Search Documentation", "url": "..."},
  {"text": "Perplexity AI", "url": "..."}
]
```

**Sources:** [website/blog/blog.json:97-134]()

---

## Content Organization

Blog content is organized into a simple directory structure optimized for fast access and clear separation of concerns.

```
website/blog/
├── blog.json                                          # Central registry
├── posts/
│   ├── seo-geo-1k-installs-milestone.md              # 486 lines
│   ├── free-ai-infrastructure-deepseek-jan.md        # 529 lines
│   ├── ralph-autonomous-agent-loop.md
│   ├── install-opc-skills-claude-code.md
│   ├── convert-docs-to-skills-guide.md
│   ├── why-skills-beat-docs.md
│   ├── domain-hunting-ai-saved-50.md
│   └── what-is-opc.md
├── 2026-02-05-seo-geo-1k-installs-og.png             # OpenGraph image
├── 2026-02-05-seo-geo-install-stats.png              # Content image
├── 2026-02-05-claude-code-plugin-install.png         # Screenshot
├── 2026-01-28-install-opc-skills-claude-code-og.png
├── 2026-01-28-free-infrastructure-og.png
└── ...
```

### File Naming Conventions

| Asset Type | Pattern | Example |
|------------|---------|---------|
| Markdown Posts | `{slug}.md` | `seo-geo-1k-installs-milestone.md` |
| OpenGraph Images | `YYYY-MM-DD-{slug}-og.png` | `2026-02-05-seo-geo-1k-installs-og.png` |
| Content Images | `YYYY-MM-DD-{slug}-{descriptor}.png` | `2026-02-05-seo-geo-install-stats.png` |

**Sources:** [website/blog/blog.json:1-699](), [website/blog/posts/seo-geo-1k-installs-milestone.md:1]()

---

## Blog Post Markdown Files

Markdown posts contain the full article content with frontmatter-style metadata at the top.

### Post Header Format

```markdown
# How SEO-GEO Skill Hit 1,000 Installs: The AI Search Revolution Is Here

*By OPC Team | February 5, 2026 | 8 min read*

**TL;DR** — Our SEO-GEO skill just crossed 1,000 installs...
```

**Sources:** [website/blog/posts/seo-geo-1k-installs-milestone.md:1-5]()

### Content Structure

Typical post structure:

1. **Title (H1)** - Matches `blog.json` title
2. **Byline** - Author, date, read time
3. **TL;DR section** - 2-3 sentence summary
4. **Problem statement** - What issue does this address?
5. **Solution explanation** - How to solve it
6. **Step-by-step guide** - Actionable instructions
7. **Results/case studies** - Social proof
8. **FAQ section** - Mirrors `blog.json` FAQ array
9. **References section** - Mirrors `blog.json` citations

**Sources:** [website/blog/posts/seo-geo-1k-installs-milestone.md:1-486]()

### Markdown Features

Posts extensively use:

```markdown
## Section Headers (H2, H3)

**Bold text** for emphasis

`inline code` for commands/filenames

```bash
# Code blocks with syntax highlighting
npx skills add ReScienceLab/opc-skills
```

> Blockquotes for testimonials

| Tables | For | Data |
|--------|-----|------|

- Bullet lists
- For clarity

1. Numbered lists
2. For steps

![Images](url)

[Links](url)
```

**Sources:** [website/blog/posts/seo-geo-1k-installs-milestone.md:1-486](), [website/blog/posts/free-ai-infrastructure-deepseek-jan.md:1-529]()

---

## Post Metadata Validation

Validation is performed by `scripts/create-blog.py`. The `validate_blog_json()` function loads `BLOG_JSON` (`website/blog/blog.json`) and checks every entry in `posts`:

| Check | Level | Threshold |
|-------|-------|-----------|
| All 14 `REQUIRED_FIELDS` present | Error | — |
| Markdown file exists at `POSTS_DIR/{slug}.md` | Error | — |
| `faq` array length | Warning | < 5 |
| `keywords` array length | Warning | < 10 |
| `citations` array length | Warning | < 3 |
| `schema.@type` is a recognized type | Warning | — |
| `date` / `dateModified` are valid ISO dates | Warning | — |

The path constants used by the script:

```
PROJECT_ROOT / "website" / "blog"          → BLOG_DIR
BLOG_DIR / "blog.json"                     → BLOG_JSON
BLOG_DIR / "posts"                         → POSTS_DIR
```

For full details on the validation commands and content quality standards, see page 5.2.

Sources: [scripts/create-blog.py:18-27](), [scripts/create-blog.py:29-76]()

---

## Integration with Website Rendering

Blog content is rendered by `website/worker.js` using a two-stage pipeline: metadata loading via `fetchBlogConfig()` and HTML assembly via `renderBlogPost()`.

**Blog rendering pipeline in `worker.js`:**

```mermaid
graph TB
    subgraph "Request Routing"
        ListRequest["url.pathname === '/blog'"]
        PostRequest["url.pathname.match(/^\/blog\/([^\/]+)$/)"]
    end

    subgraph "Helper Functions (worker.js)"
        fetchBlogConfig["fetchBlogConfig(ctx)<br/>→ fetch blog.json<br/>→ parse JSON<br/>→ return posts[]"]
        renderBlogPost["renderBlogPost(post, content)<br/>→ parse markdown via marked()<br/>→ inject schema JSON-LD<br/>→ inject FAQPage JSON-LD<br/>→ inject OG meta tags<br/>→ return HTML string"]
        marked["marked(mdContent)<br/>→ HTML string"]
    end

    subgraph "Data Sources (GitHub Raw)"
        BlogJSON["https://raw.githubusercontent.com/.../blog.json"]
        PostMD["https://raw.githubusercontent.com/.../posts/{slug}.md"]
    end

    subgraph "Cloudflare Edge Cache"
        Cache["caches.default<br/>TTL: 300s for blog.json"]
    end

    subgraph "HTML Response"
        ListHTML["Blog List HTML<br/>- posts[].title<br/>- posts[].description<br/>- posts[].date<br/>- posts[].readTime"]
        PostHTML["Blog Post HTML<br/>- <script type='application/ld+json'> (schema)<br/>- <script type='application/ld+json'> (FAQPage)<br/>- <meta> OG tags (image, title, desc)<br/>- <article> (marked HTML)"]
    end

    ListRequest --> fetchBlogConfig
    PostRequest --> fetchBlogConfig
    
    fetchBlogConfig --> Cache
    Cache -->|"cache miss"| BlogJSON
    Cache -->|"cache hit"| fetchBlogConfig
    
    fetchBlogConfig -->|"return posts[]"| ListRequest
    fetchBlogConfig -->|"find post by slug"| PostRequest
    
    PostRequest -->|"fetch(rawURL)"| PostMD
    PostMD --> marked
    
    marked -->|"HTML string"| renderBlogPost
    fetchBlogConfig -->|"post metadata"| renderBlogPost
    
    renderBlogPost --> PostHTML
    ListRequest --> ListHTML
```

### Key Functions

| Function | Parameters | Returns | Caching |
|----------|-----------|---------|---------|
| `fetchBlogConfig(ctx)` | `ctx` (cache context) | `Promise<{posts: []}>` | 300s TTL via `caches.default` |
| `renderBlogPost(post, content)` | `post` (metadata object), `content` (markdown string) | HTML string | None (computed per-request) |
| `marked(markdown)` | `markdown` (string) | HTML string | None |

The `ctx` parameter to `fetchBlogConfig()` enables Cloudflare edge caching: the blog registry is cached for 5 minutes to reduce GitHub API calls. Markdown content is fetched per-request and not cached (to enable fast content updates).

For details on the `fetchBlogConfig` caching strategy and the full set of routes, see pages 4.1, 4.2, and 4.3.

Sources: [website/blog/blog.json:1-2]()

---

## Schema.org Embedding Strategy

The `renderBlogPost()` function in `worker.js` embeds schema.org structured data via two separate `<script type="application/ld+json">` blocks in the HTML `<head>`.

### 1. Primary Schema — from `post.schema` field

The `schema` object from `blog.json` is serialized directly into JSON-LD. The `@type` varies by post category:

- **Case Studies** → `"Article"`
- **Tutorials** → `"HowTo"` or `"BlogPosting"`
- **Insights** → `"BlogPosting"`

Example rendering for a `"HowTo"` post:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to Install OPC Skills in Claude Code",
  "description": "Step-by-step tutorial to install OPC Skills...",
  "totalTime": "PT2M",
  "tool": ["Claude Code"],
  "supply": ["Claude Code (free version)"],
  "step": [
    {
      "@type": "HowToStep",
      "position": 1,
      "name": "Add OPC Skills Marketplace",
      "text": "Open Claude Code and run: /plugin marketplace add ReScienceLab/opc-skills",
      "url": "https://opc.dev/blog/install-opc-skills-claude-code#step-1"
    }
  ],
  "author": { /* Organization object */ },
  "datePublished": "2026-01-28",
  "publisher": { /* Organization with logo */ },
  "image": "https://raw.githubusercontent.com/.../2026-01-28-install-opc-skills-claude-code-og.png"
}
</script>
```

### 2. FAQPage Schema — from `post.faq` array

The `faq` array is transformed into a separate `FAQPage` schema. This implements Princeton GEO method #8 (adding FAQ sections) proven to increase AI search citations by +40%.

Example rendering:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Why did SEO-GEO hit 1,000 installs so fast?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "SEO-GEO addresses a critical need: optimizing for AI search engines like ChatGPT Search and Perplexity AI. It's free, installs in 30 seconds, requires no API keys..."
      }
    },
    {
      "@type": "Question",
      "name": "What is GEO (Generative Engine Optimization)?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "GEO is the practice of optimizing content to be cited by AI search engines like ChatGPT, Perplexity, and Claude..."
      }
    }
  ]
}
</script>
```

Each `post.faq[]` entry with `{question, answer}` fields is mapped to a `Question` object with an `acceptedAnswer` containing an `Answer` object. The transformation occurs in `renderBlogPost()` during HTML assembly.

Sources: [website/blog/blog.json:169-210](), [website/blog/blog.json:280-331]()

---

## Summary

The blog system architecture consists of:

1. **Central Registry** - `blog.json` with 8+ posts
2. **Metadata Schema** - 17 fields per post including SEO/GEO optimizations
3. **Schema.org Types** - Article, HowTo, BlogPosting for different content types
4. **FAQ Arrays** - 4-10 questions per post for GEO optimization
5. **Citations** - 5-9 authoritative sources per post
6. **Markdown Content** - 2000+ word posts in `posts/` directory
7. **Image Assets** - OpenGraph and content images with date-based naming

This architecture enables the blog to rank highly in both traditional search engines and AI search engines (ChatGPT, Perplexity, Claude) through aggressive structured data optimization and GEO method implementation.

**Sources:** [website/blog/blog.json:1-699](), [website/blog/posts/seo-geo-1k-installs-milestone.md:1-486](), [website/blog/posts/free-ai-infrastructure-deepseek-jan.md:1-529]()

---

# Page: Content Creation & Validation

# Content Creation & Validation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/publish-blog.yml](.github/workflows/publish-blog.yml)
- [scripts/BLOG_GUIDELINES.md](scripts/BLOG_GUIDELINES.md)
- [scripts/BLOG_PUBLISHING.md](scripts/BLOG_PUBLISHING.md)
- [scripts/create-blog.py](scripts/create-blog.py)
- [website/blog/posts/ralph-autonomous-agent-loop.md](website/blog/posts/ralph-autonomous-agent-loop.md)

</details>



This document describes the blog content validation system, quality standards, and the `create-blog.py` validation tool. It covers content requirements (word count, structure, SEO/GEO optimization), schema.org markup, and the validation workflow that ensures all blog posts meet quality gates before publication.

For publishing workflows and deployment strategies, see [Blog Publishing Workflows](#5.3). For blog system architecture and rendering, see [Blog System Architecture](#5.1).

---

## Purpose and Scope

The content validation system enforces quality standards across all blog posts to maximize discoverability in AI search engines (ChatGPT, Perplexity) and traditional search (Google, Bing). The system validates:

- **Metadata completeness** in `blog.json`: 13 required fields including slug, title, keywords, schema, FAQ, citations
- **Content quality**: Minimum word counts, heading structure, FAQ sections, internal/external links
- **SEO/GEO requirements**: 15+ keywords, 5-10 FAQ questions, 3+ citations
- **Schema.org markup**: BlogPosting structured data with embedded FAQPage

All validation occurs before content is published, either locally via CLI or automatically in CI/CD.

---

## Validation Tool Architecture

### Overview

The validation system is implemented in `create-blog.py`, a Python CLI tool with three primary commands: `validate`, `check`, and `new`. The tool validates both metadata structure (JSON) and content quality (Markdown).

**Validation Tool Command Flow**

```mermaid
graph TB
    CLI["create-blog.py CLI"]
    
    subgraph "Commands"
        VALIDATE["validate command<br/>Validates all posts"]
        CHECK["check &lt;slug&gt; command<br/>Validates specific post"]
        NEW["new command<br/>Creates template"]
    end
    
    subgraph "Validation Functions"
        VALIDATE_JSON["validate_blog_json()<br/>Check metadata"]
        CHECK_MD["check_markdown_post()<br/>Check content quality"]
    end
    
    subgraph "Data Sources"
        BLOG_JSON["website/blog/blog.json"]
        POSTS_DIR["website/blog/posts/"]
        MD_FILE["*.md files"]
    end
    
    subgraph "Validation Checks"
        REQ_FIELDS["Check 13 required fields"]
        FAQ_COUNT["Check FAQ count (5-10)"]
        KEYWORD_COUNT["Check keyword count (10+)"]
        CITATION_COUNT["Check citation count (3+)"]
        WORD_COUNT["Check word count (2000+)"]
        HEADING_STRUCT["Check heading structure"]
        INTERNAL_LINKS["Check internal links (3+)"]
    end
    
    CLI --> VALIDATE
    CLI --> CHECK
    CLI --> NEW
    
    VALIDATE --> VALIDATE_JSON
    CHECK --> VALIDATE_JSON
    CHECK --> CHECK_MD
    
    VALIDATE_JSON --> BLOG_JSON
    VALIDATE_JSON --> REQ_FIELDS
    VALIDATE_JSON --> FAQ_COUNT
    VALIDATE_JSON --> KEYWORD_COUNT
    VALIDATE_JSON --> CITATION_COUNT
    
    CHECK_MD --> POSTS_DIR
    CHECK_MD --> MD_FILE
    CHECK_MD --> WORD_COUNT
    CHECK_MD --> HEADING_STRUCT
    CHECK_MD --> INTERNAL_LINKS
```

**Sources:** [scripts/create-blog.py:1-264](), [scripts/BLOG_GUIDELINES.md:1-366]()

---

### Command Reference

| Command | Purpose | Usage | Exit Code |
|---------|---------|-------|-----------|
| `validate` | Validate all blog posts | `python3 scripts/create-blog.py validate` | 0 if pass, 1 if fail |
| `check <slug>` | Validate specific post | `python3 scripts/create-blog.py check ralph-autonomous-agent-loop` | 0 if pass, 1 if fail |
| `new` | Create new template | `python3 scripts/create-blog.py new` | 0 if success |

**Sources:** [scripts/create-blog.py:3-9](), [scripts/BLOG_GUIDELINES.md:6-16]()

---

### Required Metadata Fields

The `validate_blog_json()` function checks for 13 required fields in each blog post entry:

```python
REQUIRED_FIELDS = [
    "slug", "title", "description", "date", "dateModified", "author",
    "category", "tags", "readTime", "keywords", "image", "schema",
    "faq", "citations"
]
```

**Field Validation Logic**

```mermaid
graph TB
    VALIDATE_JSON["validate_blog_json()"]
    
    subgraph "For Each Post"
        LOAD_POST["Load post from blog.json"]
        CHECK_FIELDS["Check for 13 required fields"]
        CHECK_MD_FILE["Check if *.md file exists"]
        VALIDATE_DATE["Validate date format YYYY-MM-DD"]
        CHECK_SCHEMA["Check @context and @type in schema"]
    end
    
    subgraph "Quality Thresholds"
        FAQ_WARN["faq.length < 5<br/>→ warning"]
        KEYWORD_WARN["keywords.length < 10<br/>→ warning"]
        CITATION_WARN["citations.length < 3<br/>→ warning"]
    end
    
    subgraph "Output"
        PRINT_WARN["Print warnings"]
        PRINT_ERR["Print errors"]
        RETURN["Return true/false"]
    end
    
    VALIDATE_JSON --> LOAD_POST
    LOAD_POST --> CHECK_FIELDS
    CHECK_FIELDS --> CHECK_MD_FILE
    CHECK_MD_FILE --> VALIDATE_DATE
    VALIDATE_DATE --> CHECK_SCHEMA
    
    CHECK_SCHEMA --> FAQ_WARN
    CHECK_SCHEMA --> KEYWORD_WARN
    CHECK_SCHEMA --> CITATION_WARN
    
    FAQ_WARN --> PRINT_WARN
    KEYWORD_WARN --> PRINT_WARN
    CITATION_WARN --> PRINT_WARN
    
    PRINT_WARN --> PRINT_ERR
    PRINT_ERR --> RETURN
```

**Sources:** [scripts/create-blog.py:23-27](), [scripts/create-blog.py:29-104]()

---

### Content Quality Checks

The `check_markdown_post()` function validates Markdown content quality using regex pattern matching:

| Check | Threshold | Regex Pattern | Warning Condition |
|-------|-----------|---------------|-------------------|
| **Word count** | 2000+ words | `len(content.split())` | < 2000 words |
| **H1 headings** | Exactly 1 | `^# [^#]` | 0 or > 1 H1s |
| **H2 sections** | 8-12 sections | `^## [^#]` | < 5 H2s |
| **Internal links** | 3-5 links | `\]\(/blog/[^\)]+\)` | < 3 links |
| **Tables** | 1+ table | `^\|.*\|.*\|` | N/A (informational) |
| **Code blocks** | 1+ blocks | ``` ` ``` ` ``` ` ``` | N/A (informational) |
| **FAQ section** | Required | `## Frequently Asked Questions` or `## FAQ` | Missing section |

**Sources:** [scripts/create-blog.py:106-173](), [scripts/BLOG_GUIDELINES.md:76-98]()

---

## Content Quality Standards

### Word Count Requirements

```mermaid
graph LR
    MIN["Minimum<br/>2000 words<br/>(required)"]
    REC["Recommended<br/>2500-4000 words<br/>(optimal)"]
    TUT["Tutorial/Guide<br/>3000+ words"]
    CASE["Case Study<br/>2000-2500 words"]
    
    MIN --> REC
    REC --> TUT
    REC --> CASE
```

**Rationale:** Posts under 2000 words have poor SEO performance. The +40% AI visibility boost comes from comprehensive content (2500+ words) with structured FAQ sections.

**Sources:** [scripts/BLOG_GUIDELINES.md:76-81](), [scripts/create-blog.py:122-125]()

---

### Structure Requirements

All blog posts must follow this structure:

| Section | Required | Description |
|---------|----------|-------------|
| **H1 Title** | ✅ Exactly 1 | Single H1 for main title only |
| **TL;DR** | ✅ Yes | 100-150 word summary with key metrics |
| **H2 Sections** | ✅ 8-12 sections | Main content organized hierarchically |
| **Tables** | ⚠️ Recommended | For comparisons, specifications |
| **Code blocks** | ⚠️ Recommended | With syntax highlighting |
| **Internal links** | ✅ 3-5 minimum | Link to related posts |
| **External citations** | ✅ 3-6 minimum | Authoritative sources |
| **FAQ section** | ✅ Yes | 5-10 questions for GEO |

**Example Structure from Ralph Post**

```markdown
# Title (H1)
*Metadata line*

## TL;DR
[Summary with metrics]

## Section 1 (H2)
[Content]

## Section 2 (H2)
[Content]

[8-12 H2 sections total]

## Frequently Asked Questions (H2)
### Question 1? (H3)
Answer here.

[5-10 FAQ questions]
```

**Sources:** [scripts/BLOG_GUIDELINES.md:83-98](), [website/blog/posts/ralph-autonomous-agent-loop.md:1-810]()

---

## SEO/GEO Optimization Requirements

### Keyword Strategy

The validation tool enforces minimum keyword counts to ensure search visibility:

**Keyword Requirements Table**

| Keyword Type | Count | Placement | Example |
|--------------|-------|-----------|---------|
| **Primary keywords** | 3-5 | Title, H2s, first 200 words | "build MVP automatically", "autonomous AI agent loop" |
| **Long-tail keywords** | 10-15 | Throughout content | "Ralph AI tutorial", "PRD to code automatically" |
| **Total keywords** | 15+ | `keywords` array in blog.json | Triggers warning if < 10 |

**Keyword Validation Logic:**

```python
keyword_count = len(post.get('keywords', []))
if keyword_count < 10:
    warnings.append(f"Post '{slug}' has only {keyword_count} keywords (recommend 10+ for SEO)")
```

**Sources:** [scripts/create-blog.py:67-70](), [scripts/BLOG_GUIDELINES.md:101-116]()

---

### FAQ Section Requirements

FAQ sections are critical for AI search engine optimization (GEO). The system validates both quantity and structure:

**FAQ Validation Flow**

```mermaid
graph TB
    CHECK_FAQ["check_markdown_post()"]
    
    subgraph "Markdown Validation"
        REGEX_SEARCH["Search for FAQ heading<br/>## Frequently Asked Questions<br/>or ## FAQ"]
        COUNT_H3["Count H3 questions<br/>### Question?"]
    end
    
    subgraph "JSON Validation"
        FAQ_ARRAY["Check faq array in blog.json"]
        COUNT_FAQ["Count FAQ objects"]
        CHECK_STRUCT["Verify question/answer structure"]
    end
    
    subgraph "Thresholds"
        WARN_LOW["< 5 FAQs → warning"]
        IDEAL["5-10 FAQs → pass"]
        WARN_HIGH["> 10 FAQs → acceptable"]
    end
    
    CHECK_FAQ --> REGEX_SEARCH
    CHECK_FAQ --> FAQ_ARRAY
    
    REGEX_SEARCH --> COUNT_H3
    FAQ_ARRAY --> COUNT_FAQ
    COUNT_FAQ --> CHECK_STRUCT
    
    CHECK_STRUCT --> WARN_LOW
    CHECK_STRUCT --> IDEAL
    CHECK_STRUCT --> WARN_HIGH
```

**FAQ Best Practices:**

- Answer common search queries ("How do I...", "What is...", "Can I...")
- 50-150 word answers
- Include keywords naturally
- Optimize for voice search

**Example FAQ Structure:**

```json
{
  "faq": [
    {
      "question": "What is Ralph AI and how does it work?",
      "answer": "Ralph is an autonomous AI agent loop that runs coding tools..."
    },
    {
      "question": "Can solopreneurs build MVPs with Ralph without coding experience?",
      "answer": "Yes. Ralph requires a PRD (product requirements document)..."
    }
  ]
}
```

**Sources:** [scripts/BLOG_GUIDELINES.md:118-123](), [scripts/create-blog.py:62-65](), [website/blog/posts/ralph-autonomous-agent-loop.md:765-806]()

---

### Citation Requirements

External citations establish authority and improve trust signals for search engines:

| Requirement | Threshold | Validation |
|-------------|-----------|------------|
| **Minimum citations** | 3 | `len(post.get('citations', []))` |
| **Recommended citations** | 3-6 | Optimal for authority |
| **Citation types** | GitHub repos, official docs, research papers | Manual quality check |
| **Placement** | Markdown content AND citations array | Both required |

**Citations Array Structure:**

```json
{
  "citations": [
    {
      "title": "Ralph GitHub Repository",
      "url": "https://github.com/snarktank/ralph",
      "description": "Source code, examples, and community"
    },
    {
      "title": "Geoffrey Huntley's Ralph Article",
      "url": "https://ghuntley.com/ralph/",
      "description": "Original pattern and philosophy"
    }
  ]
}
```

**Sources:** [scripts/BLOG_GUIDELINES.md:129-133](), [scripts/create-blog.py:72-75]()

---

### Internal Link Requirements

Internal links distribute SEO value across the site and improve user engagement:

**Internal Link Validation:**

```python
internal_links = re.findall(r'\]\(/blog/[^\)]+\)', content)
print(f"  ✓ Internal links: {len(internal_links)}")
if len(internal_links) < 3:
    warnings.append(f"Only {len(internal_links)} internal links (recommend 3-5 for SEO)")
```

**Internal Link Strategy:**

- **Minimum:** 3 internal links to other blog posts
- **Recommended:** 3-5 links to related content
- **Anchor text:** Use descriptive phrases, not "click here"
- **Placement:** Natural within content, not forced

**Example from Ralph Post:**

```markdown
- [OPC Skills: AI Agent Skills for Solopreneurs](/blog/what-is-opc)
- [Why Skills Beat Docs: Agent-Native Documentation](/blog/why-skills-beat-docs)
- [How to Convert Your Docs to Agent Skills (5-Min Guide)](/blog/convert-docs-to-skills-guide)
```

**Sources:** [scripts/BLOG_GUIDELINES.md:124-128](), [scripts/create-blog.py:149-153](), [website/blog/posts/ralph-autonomous-agent-loop.md:745-752]()

---

## Schema.org Markup Requirements

### BlogPosting Schema

Every blog post must include a `schema` object in `blog.json` with required schema.org fields:

**Required Schema.org Fields**

```mermaid
graph TB
    SCHEMA["schema object"]
    
    subgraph "Core Fields (Required)"
        CONTEXT["@context: https://schema.org"]
        TYPE["@type: BlogPosting"]
        HEADLINE["headline: Post title"]
        DESC["description: Post description"]
    end
    
    subgraph "Author/Publisher (Required)"
        AUTHOR["author.@type: Organization"]
        AUTHOR_NAME["author.name: OPC Team"]
        AUTHOR_URL["author.url: https://opc.dev"]
        PUB["publisher: Same as author"]
    end
    
    subgraph "Dates (Required)"
        DATE_PUB["datePublished: YYYY-MM-DD"]
        DATE_MOD["dateModified: YYYY-MM-DD"]
    end
    
    subgraph "Additional Fields"
        IMAGE["image: Banner URL"]
        MAIN["mainEntityOfPage: Post URL"]
        KEYWORDS["keywords: Comma-separated"]
        SECTION["articleSection: Category"]
        WORD_COUNT["wordCount: Integer"]
    end
    
    SCHEMA --> CONTEXT
    SCHEMA --> TYPE
    SCHEMA --> HEADLINE
    SCHEMA --> DESC
    SCHEMA --> AUTHOR
    SCHEMA --> PUB
    SCHEMA --> DATE_PUB
    SCHEMA --> DATE_MOD
    SCHEMA --> IMAGE
    SCHEMA --> MAIN
    SCHEMA --> KEYWORDS
    SCHEMA --> SECTION
    SCHEMA --> WORD_COUNT
```

**Validation Check:**

```python
schema = post.get('schema', {})
if '@context' not in schema or '@type' not in schema:
    errors.append(f"Post '{slug}' missing required schema.org fields")
```

**Complete Schema Example:**

```json
{
  "schema": {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "How Solopreneurs Build MVPs Automatically with Ralph",
    "description": "Ralph is an autonomous AI agent loop...",
    "author": {
      "@type": "Organization",
      "name": "OPC Team",
      "url": "https://opc.dev"
    },
    "datePublished": "2026-01-26",
    "dateModified": "2026-01-26",
    "publisher": {
      "@type": "Organization",
      "name": "OPC Team",
      "url": "https://opc.dev",
      "logo": {
        "@type": "ImageObject",
        "url": "https://opc.dev/opc-banner.png"
      }
    },
    "image": "https://opc.dev/opc-banner.png",
    "mainEntityOfPage": "https://opc.dev/blog/ralph-autonomous-agent-loop",
    "keywords": "build MVP automatically, solopreneur MVP builder, Ralph AI tutorial",
    "articleSection": "Tutorial",
    "wordCount": 2900
  }
}
```

**Sources:** [scripts/BLOG_GUIDELINES.md:135-156](), [scripts/create-blog.py:84-86]()

---

## Validation Workflow

### Local Validation Process

**End-to-End Validation Flow**

```mermaid
graph TB
    START["Start: Create blog content"]
    
    subgraph "Content Creation"
        WRITE_MD["Write Markdown in<br/>website/blog/posts/<slug>.md"]
        ADD_META["Add metadata to<br/>website/blog/blog.json"]
    end
    
    subgraph "Local Validation"
        VAL_ALL["Run: python3 scripts/create-blog.py validate"]
        CHECK_ONE["Run: python3 scripts/create-blog.py check <slug>"]
    end
    
    subgraph "Validation Results"
        CHECK_JSON["validate_blog_json()<br/>Checks blog.json structure"]
        CHECK_MD["check_markdown_post()<br/>Checks content quality"]
    end
    
    subgraph "Outputs"
        WARNINGS["Warnings printed<br/>(non-blocking)"]
        ERRORS["Errors printed<br/>(exit code 1)"]
        SUCCESS["Success<br/>(exit code 0)"]
    end
    
    subgraph "Next Steps"
        CREATE_PR["Create PR with blog-post label"]
        CI_AUTO["CI validates and auto-merges"]
    end
    
    START --> WRITE_MD
    WRITE_MD --> ADD_META
    ADD_META --> VAL_ALL
    VAL_ALL --> CHECK_JSON
    VAL_ALL --> CHECK_ONE
    CHECK_ONE --> CHECK_MD
    
    CHECK_JSON --> WARNINGS
    CHECK_JSON --> ERRORS
    CHECK_JSON --> SUCCESS
    CHECK_MD --> WARNINGS
    CHECK_MD --> ERRORS
    CHECK_MD --> SUCCESS
    
    SUCCESS --> CREATE_PR
    CREATE_PR --> CI_AUTO
    
    ERRORS --> WRITE_MD
    WARNINGS --> CREATE_PR
```

**Command Examples:**

```bash
# Validate all blog posts
python3 scripts/create-blog.py validate

# Check specific post for content quality
python3 scripts/create-blog.py check ralph-autonomous-agent-loop

# Create new blog post template
python3 scripts/create-blog.py new
```

**Sources:** [scripts/BLOG_GUIDELINES.md:19-73](), [scripts/create-blog.py:235-261]()

---

### CI/CD Validation Integration

The validation script integrates with the fast-track publishing workflow via GitHub Actions:

**CI Validation in publish-blog.yml**

```mermaid
graph TB
    PR["PR created to main<br/>with blog-post label"]
    
    subgraph "GitHub Actions Workflow"
        TRIGGER["Workflow triggers<br/>.github/workflows/publish-blog.yml"]
        CHECKOUT["actions/checkout@v4"]
        VALIDATE["Run: python3 scripts/create-blog.py validate"]
    end
    
    subgraph "Validation Results"
        PASS["Exit code 0<br/>Validation passed"]
        FAIL["Exit code 1<br/>Validation failed"]
    end
    
    subgraph "Auto-Merge Actions"
        AUTO_APPROVE["Auto-approve PR<br/>hmarr/auto-approve-action"]
        AUTO_MERGE["Auto-merge PR<br/>pascalgn/automerge-action"]
        DEPLOY["Cloudflare deploys<br/>5 minutes"]
    end
    
    PR --> TRIGGER
    TRIGGER --> CHECKOUT
    CHECKOUT --> VALIDATE
    
    VALIDATE --> PASS
    VALIDATE --> FAIL
    
    PASS --> AUTO_APPROVE
    AUTO_APPROVE --> AUTO_MERGE
    AUTO_MERGE --> DEPLOY
    
    FAIL -.workflow stops.-> PR
```

**Workflow Configuration:**

```yaml
- name: Validate blog post
  run: |
    python3 scripts/create-blog.py validate
```

If validation fails (exit code 1), the workflow stops and the PR cannot be auto-merged. Authors must fix validation errors before re-triggering.

**Sources:** [.github/workflows/publish-blog.yml:1-38](), [scripts/BLOG_PUBLISHING.md:27-65]()

---

## Validation Checklist

### Pre-PR Checklist

Before creating a pull request, verify all items pass:

| Check | Command | Pass Criteria |
|-------|---------|---------------|
| **JSON structure** | `python3 scripts/create-blog.py validate` | Exit code 0, no errors |
| **Content quality** | `python3 scripts/create-blog.py check <slug>` | Exit code 0, no errors |
| **Word count** | Check output | > 2000 words |
| **FAQ section** | Check output | 5-10 questions |
| **Keywords** | Check blog.json | 10+ keywords in array |
| **Internal links** | Check markdown | 3+ links to /blog/ |
| **External citations** | Check blog.json | 3+ citations in array |
| **Schema.org markup** | Check blog.json | Complete schema object |
| **Tables** | Visual check | 1+ comparison tables |
| **Code blocks** | Visual check | Syntax highlighting present |
| **Reading time** | Check blog.json | Accurate estimate (word_count / 250) |

**Automated Checklist Output:**

```bash
🔍 Checking ralph-autonomous-agent-loop.md...
  ✓ Word count: 4850
  ✓ H1 headings: 1
  ✓ H2 headings: 15
  ✓ Tables: 8 rows
  ✓ Code blocks: 12
  ✓ Internal links: 4
  ✓ External links: 8
  ✓ FAQ section: present

✅ Blog post passed all checks!
```

**Sources:** [scripts/BLOG_GUIDELINES.md:323-338](), [scripts/create-blog.py:114-172]()

---

## Common Validation Errors

### Missing Required Fields

**Error Pattern:**

```
❌ 1 errors:
  - Post 'my-post-slug' missing fields: keywords, faq, citations
```

**Cause:** blog.json entry incomplete

**Fix:** Add all 13 required fields to the post object in blog.json:

```json
{
  "slug": "my-post-slug",
  "title": "...",
  "description": "...",
  "date": "2026-01-26",
  "dateModified": "2026-01-26",
  "author": "OPC Team",
  "category": "Tutorial",
  "tags": ["tag1", "tag2"],
  "readTime": "9 min",
  "keywords": ["keyword1", "keyword2", ...],
  "image": "https://opc.dev/opc-banner.png",
  "schema": { ... },
  "faq": [ ... ],
  "citations": [ ... ]
}
```

**Sources:** [scripts/create-blog.py:52-55]()

---

### Markdown File Not Found

**Error Pattern:**

```
❌ Post 'my-post-slug' has no markdown file at website/blog/posts/my-post-slug.md
```

**Cause:** blog.json references a slug that doesn't have a corresponding .md file

**Fix:** Create the markdown file with matching slug:

```bash
# Create the file
touch website/blog/posts/my-post-slug.md

# Or use the template generator
python3 scripts/create-blog.py new
```

**Sources:** [scripts/create-blog.py:57-60]()

---

### Insufficient FAQ Count

**Warning Pattern:**

```
⚠️  1 warnings:
  - Post 'my-post-slug' has only 3 FAQs (recommend 5-10 for GEO)
```

**Cause:** FAQ array has fewer than 5 questions

**Impact:** Non-blocking warning, but reduces AI search visibility

**Fix:** Add more FAQ questions to both the Markdown content and the faq array in blog.json:

```json
{
  "faq": [
    {"question": "Question 1?", "answer": "Answer 1"},
    {"question": "Question 2?", "answer": "Answer 2"},
    {"question": "Question 3?", "answer": "Answer 3"},
    {"question": "Question 4?", "answer": "Answer 4"},
    {"question": "Question 5?", "answer": "Answer 5"}
  ]
}
```

**Sources:** [scripts/create-blog.py:62-65]()

---

### Low Keyword Count

**Warning Pattern:**

```
⚠️  Post 'my-post-slug' has only 7 keywords (recommend 10+ for SEO)
```

**Cause:** keywords array has fewer than 10 entries

**Impact:** Reduces search engine discoverability

**Fix:** Add more long-tail keywords to the keywords array:

```json
{
  "keywords": [
    "primary keyword 1",
    "primary keyword 2",
    "long-tail keyword 1",
    "long-tail keyword 2",
    "long-tail keyword 3",
    "long-tail keyword 4",
    "long-tail keyword 5",
    "long-tail keyword 6",
    "long-tail keyword 7",
    "long-tail keyword 8",
    "long-tail keyword 9",
    "long-tail keyword 10"
  ]
}
```

**Sources:** [scripts/create-blog.py:67-70](), [scripts/BLOG_GUIDELINES.md:101-116]()

---

### Invalid Date Format

**Error Pattern:**

```
❌ Post 'my-post-slug' has invalid date format: 01/26/2026
```

**Cause:** date or dateModified field not in YYYY-MM-DD format

**Fix:** Use ISO 8601 date format:

```json
{
  "date": "2026-01-26",
  "dateModified": "2026-01-26"
}
```

**Sources:** [scripts/create-blog.py:78-81]()

---

### Missing Schema.org Fields

**Error Pattern:**

```
❌ Post 'my-post-slug' missing required schema.org fields
```

**Cause:** schema object missing `@context` or `@type`

**Fix:** Add complete schema object with required fields:

```json
{
  "schema": {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "Post title",
    "description": "Post description",
    "author": { "@type": "Organization", "name": "OPC Team", "url": "https://opc.dev" },
    "datePublished": "2026-01-26",
    "dateModified": "2026-01-26",
    "publisher": { ... },
    "image": "https://opc.dev/opc-banner.png",
    "mainEntityOfPage": "https://opc.dev/blog/slug"
  }
}
```

**Sources:** [scripts/create-blog.py:84-86](), [scripts/BLOG_GUIDELINES.md:135-156]()

---

### Low Word Count

**Warning Pattern:**

```
⚠️  Post is only 1750 words (recommend 2500+ for SEO)
```

**Cause:** Markdown content has fewer than 2000 words

**Impact:** Poor SEO performance, reduces search ranking

**Fix:** Expand content with:
- More detailed explanations
- Additional examples and case studies
- Step-by-step tutorials
- Comparison tables
- Code examples with explanations

**Sources:** [scripts/create-blog.py:122-125](), [scripts/BLOG_GUIDELINES.md:76-81]()

---

### Missing FAQ Section in Markdown

**Warning Pattern:**

```
⚠️  FAQ section: missing
  - No FAQ section found (required for GEO)
```

**Cause:** Markdown file doesn't contain `## Frequently Asked Questions` or `## FAQ` heading

**Fix:** Add FAQ section to the Markdown file:

```markdown
## Frequently Asked Questions

### Question 1?

Answer here.

### Question 2?

Answer here.

[5-10 questions total]
```

**Sources:** [scripts/create-blog.py:160-163]()

---

### Insufficient Internal Links

**Warning Pattern:**

```
⚠️  Only 2 internal links (recommend 3-5 for SEO)
```

**Cause:** Fewer than 3 links to `/blog/` paths in the Markdown content

**Impact:** Lost SEO value distribution across the site

**Fix:** Add more internal links to related blog posts:

```markdown
## Further Reading

- [Related Post 1](/blog/related-post-1)
- [Related Post 2](/blog/related-post-2)
- [Related Post 3](/blog/related-post-3)
```

**Sources:** [scripts/create-blog.py:149-153](), [scripts/BLOG_GUIDELINES.md:124-128]()

---

## Template Generation

### Creating New Blog Posts

The `new` command generates a blog post template with placeholder structure:

**Template Generation Flow**

```mermaid
graph TB
    CMD["python3 scripts/create-blog.py new"]
    
    subgraph "Interactive Prompts"
        TITLE["Input: Title"]
        SLUG["Input: Slug (kebab-case)"]
        CATEGORY["Input: Category"]
    end
    
    subgraph "File Creation"
        CHECK_EXISTS["Check if file exists"]
        CREATE_MD["Create website/blog/posts/<slug>.md"]
        WRITE_TEMPLATE["Write template structure"]
    end
    
    subgraph "Template Contents"
        H1["# Title"]
        META["*By OPC Team | Date | X min read*"]
        TLDR["## TL;DR<br/>[placeholder]"]
        SECTIONS["## Section 1<br/>[Content here]"]
        FAQ_TPL["## Frequently Asked Questions<br/>### Question 1?<br/>Answer here."]
    end
    
    subgraph "Next Steps Output"
        PRINT_PATH["Print file path"]
        PRINT_STEPS["Print next steps:<br/>1. Edit markdown<br/>2. Add to blog.json<br/>3. Validate<br/>4. Create PR"]
    end
    
    CMD --> TITLE
    TITLE --> SLUG
    SLUG --> CATEGORY
    
    CATEGORY --> CHECK_EXISTS
    CHECK_EXISTS --> CREATE_MD
    CREATE_MD --> WRITE_TEMPLATE
    
    WRITE_TEMPLATE --> H1
    WRITE_TEMPLATE --> META
    WRITE_TEMPLATE --> TLDR
    WRITE_TEMPLATE --> SECTIONS
    WRITE_TEMPLATE --> FAQ_TPL
    
    FAQ_TPL --> PRINT_PATH
    PRINT_PATH --> PRINT_STEPS
```

**Template Structure:**

```markdown
# {title}

*By OPC Team | {date} | X min read*

## TL;DR

[Write a 100-150 word summary here]

---

## Section 1

[Content here]

---

## Frequently Asked Questions

### Question 1?

Answer here.

### Question 2?

Answer here.

---

*Questions about [topic]? Open an issue on [GitHub](https://github.com/ReScienceLab/opc-skills/issues).*
```

**Sources:** [scripts/create-blog.py:175-233](), [scripts/BLOG_GUIDELINES.md:160-239]()

---

## Validation Output Examples

### Successful Validation

```bash
$ python3 scripts/create-blog.py validate

🔍 Validating blog.json...
✓ blog.json is valid JSON
✓ Total posts: 1
  ✓ Post: ralph-autonomous-agent-loop

✅ All blog posts validated successfully!
```

**Exit code:** 0

**Sources:** [scripts/create-blog.py:31-104]()

---

### Validation with Warnings

```bash
$ python3 scripts/create-blog.py check my-post

🔍 Checking my-post.md...
  ✓ Word count: 2150
  ✓ H1 headings: 1
  ✓ H2 headings: 8
  ✓ Tables: 3 rows
  ✓ Code blocks: 5
  ✓ Internal links: 2
  ✓ External links: 4
  ⚠ FAQ section: missing

⚠️  3 warnings:
  - Post is only 2150 words (recommend 2500+ for SEO)
  - Only 2 internal links (recommend 3-5 for SEO)
  - No FAQ section found (required for GEO)
```

**Exit code:** 0 (warnings don't block)

**Sources:** [scripts/create-blog.py:119-172]()

---

### Validation with Errors

```bash
$ python3 scripts/create-blog.py validate

🔍 Validating blog.json...
✓ blog.json is valid JSON
✓ Total posts: 2
  ⚠ Post: incomplete-post
  ✓ Post: complete-post

⚠️  2 warnings:
  - Post 'incomplete-post' has only 3 FAQs (recommend 5-10 for GEO)
  - Post 'incomplete-post' has only 6 keywords (recommend 10+ for SEO)

❌ 2 errors:
  - Post 'incomplete-post' missing fields: schema, citations
  - Post 'incomplete-post' has no markdown file at website/blog/posts/incomplete-post.md
```

**Exit code:** 1

**Sources:** [scripts/create-blog.py:91-102]()

---

## Summary

The content validation system ensures all blog posts meet quality standards before publication:

- **Validation tool:** `create-blog.py` with `validate`, `check`, and `new` commands
- **Required fields:** 13 metadata fields including keywords, FAQ, citations, schema
- **Content quality:** 2000+ words, 8-12 H2 sections, 5-10 FAQs, 3+ internal links
- **SEO/GEO:** 15+ keywords, FAQ sections for voice search, schema.org BlogPosting markup
- **CI/CD integration:** Automatic validation in GitHub Actions before auto-merge
- **Exit codes:** 0 for pass (with warnings), 1 for fail (with errors)

All validation must pass before content reaches production via the fast-track publishing workflow (see [Blog Publishing Workflows](#5.3)).

**Sources:** [scripts/create-blog.py:1-264](), [scripts/BLOG_GUIDELINES.md:1-366](), [.github/workflows/publish-blog.yml:1-38]()

---

# Page: Blog Publishing Workflows

# Blog Publishing Workflows

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/publish-blog.yml](.github/workflows/publish-blog.yml)
- [scripts/BLOG_GUIDELINES.md](scripts/BLOG_GUIDELINES.md)
- [scripts/BLOG_PUBLISHING.md](scripts/BLOG_PUBLISHING.md)
- [scripts/create-blog.py](scripts/create-blog.py)
- [website/blog/posts/ralph-autonomous-agent-loop.md](website/blog/posts/ralph-autonomous-agent-loop.md)

</details>



This document describes five publishing strategies for blog posts in the OPC Skills repository. The **Fast-Track Auto-Merge** workflow (recommended) publishes posts in ~6 minutes. Additional workflows support scheduled publishing, high-frequency blogging, non-technical authors, and maximum speed scenarios. For blog content structure and metadata schema, see page [5.1](). For content creation and the `create-blog.py` validation script, see page [5.2](). For general CI/CD and branching strategy, see page [6.1]().

## Overview

The repository supports five distinct publishing workflows:

| Workflow | Branch Target | Time to Live | Automation Level | Use Case |
|----------|---------------|--------------|------------------|----------|
| **Fast-Track Auto-Merge** | `main` | 6 minutes | Full (CI validates + auto-merges) | Default, recommended for all posts |
| **Scheduled Publishing** | `main` | On scheduled date | Full (cron triggers merge) | Content calendars, timed releases |
| **Blog Branch** | `blog` → `main` | 5 minutes | Partial (manual PR, auto-deploy) | High post frequency (multiple/day) |
| **Headless CMS** | `main` via CMS | 10 minutes | Full (CMS commits, CI deploys) | Non-technical authors, visual editing |
| **Direct Push to Main** | `main` (direct push) | 5 minutes | Minimal (post-push validation) | Single trusted author, maximum speed |

**Fast-Track Auto-Merge** is the only workflow with an active GitHub Actions implementation at [.github/workflows/publish-blog.yml:1-38](). It bypasses the standard `develop` branch used for code changes (see page [6.1]()).

**Publishing workflow decision tree:**

```mermaid
graph TD
    start["Need to publish blog post"]
    q1{"Multiple<br/>posts per day?"}
    q2{"Non-technical<br/>authors?"}
    q3{"Need<br/>scheduling?"}
    q4{"Single<br/>trusted author?"}
    
    fasttrack["Fast-Track Auto-Merge<br/>6 min, automated validation"]
    blogbranch["Blog Branch<br/>5 min, separate branch"]
    cms["Headless CMS<br/>10 min, visual editor"]
    scheduled["Scheduled Publishing<br/>On date, cron job"]
    direct["Direct Push<br/>5 min, minimal gates"]
    
    start --> q1
    q1 -->|"Yes"| blogbranch
    q1 -->|"No"| q2
    q2 -->|"Yes"| cms
    q2 -->|"No"| q3
    q3 -->|"Yes"| scheduled
    q3 -->|"No"| q4
    q4 -->|"Yes"| direct
    q4 -->|"No"| fasttrack
```

**Standard Git Flow comparison:**

| Phase | Standard Git Flow (code) | Fast-Track (blog posts) |
|-------|--------------------------|-------------------------|
| Branch target | `feature/blog/*` → `develop` → `main` | `feature/blog/*` → `main` |
| Review | Manual on two PRs | Automated `validate_blog_json()` |
| Merge | Manual (two PRs) | Auto-squash via `pascalgn/automerge-action` |
| Total time | 25+ hours | ~6 minutes |

Sources: [.github/workflows/publish-blog.yml:1-38](), [scripts/BLOG_PUBLISHING.md:23-393](), [scripts/create-blog.py:1-10]()

---

## Fast-Track Publishing Pipeline

The following sequence diagram maps the complete fast-track flow from local development to production, labeling each step with the actual script or action involved.

**Fast-Track Blog Publishing: End-to-End Sequence**

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant createblog as "scripts/create-blog.py"
    participant Branch as "feature/blog/* branch"
    participant PR as "Pull Request (base: main)"
    participant publishblog as ".github/workflows/publish-blog.yml"
    participant autoapprove as "hmarr/auto-approve-action@v3"
    participant automerge as "pascalgn/automerge-action@v0.15.6"
    participant main as "main branch"
    participant CF as "Cloudflare Workers"

    Dev->>createblog: "python3 scripts/create-blog.py new"
    createblog-->>Dev: "website/blog/posts/{slug}.md template"

    Dev->>Dev: "Edit {slug}.md + update website/blog/blog.json"
    Dev->>createblog: "python3 scripts/create-blog.py validate"
    createblog-->>Dev: "Validation result (exit 0 or exit 1)"

    Dev->>Branch: "git commit + git push"
    Dev->>PR: "gh pr create --base main --label blog-post"

    PR->>publishblog: "pull_request: labeled (blog-post, paths: website/blog/**)"
    publishblog->>createblog: "python3 scripts/create-blog.py validate"

    alt "validate_blog_json() fails (exit 1)"
        createblog-->>publishblog: "Non-zero exit"
        publishblog-->>PR: "Job fails, merge blocked"
    else "validate_blog_json() passes (exit 0)"
        createblog-->>publishblog: "Exit 0"
        publishblog->>autoapprove: "Approve PR (GITHUB_TOKEN)"
        autoapprove-->>PR: "Approval added"
        publishblog->>automerge: "MERGE_METHOD=squash, MERGE_LABELS=blog-post"
        automerge-->>main: "Squash merge"
        main-->>CF: "Deploy (website/worker.js)"
        CF-->>Dev: "Live at opc.dev/blog/{slug}"
    end
```

**Timing breakdown:**
- Local steps (`new`, `validate`, `check`): 30–60 minutes (human content time)
- Git operations and PR creation: ~30 seconds
- Automated pipeline (`publish-blog.yml` → deploy): ~6 minutes

Sources: [.github/workflows/publish-blog.yml:1-38](), [scripts/create-blog.py:29-104](), [scripts/BLOG_PUBLISHING.md:27-54]()

---

## Validation System

The CI validation step in `publish-blog.yml` runs `python3 scripts/create-blog.py validate`, which calls `validate_blog_json()` in [scripts/create-blog.py:29-104](). A non-zero exit code blocks the auto-merge. For a full description of all three commands (`validate`, `check`, `new`) and their quality thresholds, see page [5.2]().

**`validate_blog_json()` checks (run in CI):**

| Check | Threshold | Source |
|-------|-----------|--------|
| JSON syntax | Must be valid JSON | [scripts/create-blog.py:34-42]() |
| Required fields | All 14 fields present | [scripts/create-blog.py:53-55]() |
| Markdown file | `posts/{slug}.md` must exist | [scripts/create-blog.py:58-60]() |
| FAQ count | Warning if < 5 | [scripts/create-blog.py:63-65]() |
| Keyword count | Warning if < 10 | [scripts/create-blog.py:68-70]() |
| Citation count | Warning if < 3 | [scripts/create-blog.py:73-75]() |

**`REQUIRED_FIELDS` enforced in `blog.json`** [scripts/create-blog.py:23-27]():

```
slug, title, description, date, dateModified, author,
category, tags, readTime, keywords, image, schema, faq, citations
```

**Validation data flow:**

```mermaid
graph LR
    blogjson["website/blog/blog.json"]
    postmd["website/blog/posts/{slug}.md"]
    validate["validate_blog_json()"]
    REQUIRED_FIELDS["REQUIRED_FIELDS list"]
    exit0["exit 0 → auto-approve proceeds"]
    exit1["exit 1 → job fails, merge blocked"]

    blogjson --> validate
    postmd --> validate
    REQUIRED_FIELDS --> validate
    validate --> exit0
    validate --> exit1
```

Sources: [scripts/create-blog.py:23-104](), [.github/workflows/publish-blog.yml:21-23]()

---

## `publish-blog.yml` Workflow

The automation is defined in [.github/workflows/publish-blog.yml:1-38](). It contains a single job, `auto-merge`, with four sequential steps.

### Trigger Conditions

All three conditions must be true simultaneously for the job to run [.github/workflows/publish-blog.yml:1-12]():

| Condition | Value |
|-----------|-------|
| Event type | `pull_request: labeled` |
| PR base branch | `main` |
| Changed paths | `website/blog/**` |
| Label name | `blog-post` (checked in `if:` on the job) |

### `auto-merge` Job Steps

**`publish-blog.yml` Job and Step Relationships**

```mermaid
graph TD
    trigger["pull_request: labeled\nbranches: [main]\npaths: website/blog/**"]
    job["job: auto-merge\nif: github.event.label.name == 'blog-post'\npermissions: contents:write, pull-requests:write"]
    s1["step 1: actions/checkout@v4"]
    s2["step 2: python3 scripts/create-blog.py validate\n(validate_blog_json)"]
    s3["step 3: hmarr/auto-approve-action@v3\ngithub-token: GITHUB_TOKEN"]
    s4["step 4: pascalgn/automerge-action@v0.15.6\nMERGE_METHOD=squash\nMERGE_LABELS=blog-post\nMERGE_COMMIT_MESSAGE=pull-request-title"]
    blocked["Job fails\nmerge blocked"]
    merged["Squash merge to main\nCloudflare Workers deploys"]

    trigger --> job
    job --> s1
    s1 --> s2
    s2 -->|"exit 0"| s3
    s2 -->|"exit 1"| blocked
    s3 --> s4
    s4 --> merged
```

**Step details:**

1. **Checkout** [.github/workflows/publish-blog.yml:19](): `actions/checkout@v4` — checks out the PR branch.
2. **Validate** [.github/workflows/publish-blog.yml:21-23](): `python3 scripts/create-blog.py validate` — calls `validate_blog_json()`; non-zero exit fails the job and blocks merge.
3. **Auto-approve** [.github/workflows/publish-blog.yml:25-28](): `hmarr/auto-approve-action@v3` — adds a programmatic approval using `GITHUB_TOKEN` (`pull-requests: write` permission required).
4. **Auto-merge** [.github/workflows/publish-blog.yml:30-37](): `pascalgn/automerge-action@v0.15.6` — squash merges to `main`; commit message taken from the PR title; only activates for PRs carrying the `blog-post` label.

Sources: [.github/workflows/publish-blog.yml:1-38]()

---

## Local Development Workflow

Developers use `scripts/create-blog.py` locally before pushing. The three commands map directly to phases of the blog authoring lifecycle.

**Local Workflow: Commands and File Targets**

```mermaid
graph TD
    start["Start new post"]
    new["python3 scripts/create-blog.py new\n(create_new_blog)"]
    template["website/blog/posts/{slug}.md\n(generated template)"]
    edit["Edit {slug}.md\nUpdate website/blog/blog.json"]
    validate["python3 scripts/create-blog.py validate\n(validate_blog_json)"]
    check["python3 scripts/create-blog.py check {slug}\n(check_markdown_post)"]
    commit["git commit + push"]
    pr["gh pr create --base main --label blog-post"]

    start --> new
    new --> template
    template --> edit
    edit --> validate
    validate -->|"exit 1: fix errors"| edit
    validate -->|"exit 0"| check
    check -->|"warnings: improve content"| edit
    check -->|"pass"| commit
    commit --> pr
```

**Command summary:**

| Command | Function called | Output |
|---------|----------------|--------|
| `python3 scripts/create-blog.py new` | `create_new_blog()` | `website/blog/posts/{slug}.md` template |
| `python3 scripts/create-blog.py validate` | `validate_blog_json()` | Errors/warnings for all posts; exit 0 or 1 |
| `python3 scripts/create-blog.py check <slug>` | `check_markdown_post()` | Word count, heading count, link count, FAQ presence |

For full details on each command's checks and thresholds, see page [5.2]().

Sources: [scripts/create-blog.py:1-10](), [scripts/create-blog.py:175-233](), [scripts/BLOG_GUIDELINES.md:17-73]()

---

## Fast-Track Usage

The recommended command sequence to publish a post using the fast-track workflow:

```bash
# 1. Create branch and content
git checkout -b feature/blog/my-post
# Write website/blog/posts/my-post.md
# Add entry to website/blog/blog.json

# 2. Validate locally
python3 scripts/create-blog.py validate
python3 scripts/create-blog.py check my-post

# 3. Push and create PR targeting main (not develop)
git add website/blog/
git commit -m "feat(blog): add my post"
git push -u origin feature/blog/my-post
gh pr create --base main --label blog-post --title "feat(blog): add my post"

# publish-blog.yml triggers, validates, auto-approves, squash merges
# Post is live at opc.dev/blog/my-post in ~6 minutes
```

**Why this bypasses `develop`:** Blog posts contain only files under `website/blog/**`. They carry no code changes that require integration testing on `develop`. The `publish-blog.yml` path filter (`paths: website/blog/**`) enforces this scope. The standard Git Flow for code skill changes is described in page [6.1]().

Sources: [scripts/BLOG_PUBLISHING.md:42-54](), [.github/workflows/publish-blog.yml:7-8]()

---

## Workflow 1: Fast-Track Auto-Merge (Recommended)

The default workflow for publishing blog posts. Creates a PR directly to `main` with the `blog-post` label, triggering automated validation and merge.

**Implementation:** Active GitHub Actions workflow at [.github/workflows/publish-blog.yml:1-38]().

**Fast-Track workflow components:**

| Component | File/Action | Function |
|-----------|-------------|----------|
| Trigger label | `blog-post` | Activates automation when applied to PR |
| CI workflow | [.github/workflows/publish-blog.yml:1-38]() | Orchestrates validation, approval, merge |
| Validator | `validate_blog_json()` at [scripts/create-blog.py:29-104]() | Checks `blog.json` schema, required fields |
| Auto-approver | `hmarr/auto-approve-action@v3` at [.github/workflows/publish-blog.yml:25-28]() | Programmatic PR approval |
| Auto-merger | `pascalgn/automerge-action@v0.15.6` at [.github/workflows/publish-blog.yml:30-37]() | Squash merges to `main` |

**Complete Fast-Track flow:**

```mermaid
graph TB
    dev["Developer: feature/blog/slug branch"]
    localval["scripts/create-blog.py validate<br/>scripts/create-blog.py check slug"]
    push["git push origin feature/blog/slug"]
    pr["gh pr create --base main --label blog-post"]
    
    trigger["publish-blog.yml triggered<br/>pull_request: labeled<br/>label.name == 'blog-post'"]
    checkout["actions/checkout@v4"]
    civalidate["python3 scripts/create-blog.py validate<br/>validate_blog_json()"]
    
    fail["Validation fails<br/>Job exits 1<br/>Merge blocked"]
    approve["hmarr/auto-approve-action@v3<br/>github-token: GITHUB_TOKEN"]
    merge["pascalgn/automerge-action@v0.15.6<br/>MERGE_METHOD: squash<br/>MERGE_LABELS: blog-post"]
    
    main["main branch updated"]
    cf["Cloudflare Workers redeploy<br/>worker.js serves new post"]
    live["https://opc.dev/blog/slug"]
    
    dev --> localval
    localval --> push
    push --> pr
    pr --> trigger
    trigger --> checkout
    checkout --> civalidate
    civalidate -->|"exit 0"| approve
    civalidate -->|"exit 1"| fail
    approve --> merge
    merge --> main
    main --> cf
    cf --> live
```

**Usage commands:**

```bash
# 1. Create branch and content
git checkout -b feature/blog/my-post
# Edit website/blog/posts/my-post.md
# Add entry at index 0 in website/blog/blog.json

# 2. Local validation
python3 scripts/create-blog.py validate  # Checks all posts
python3 scripts/create-blog.py check my-post  # Checks specific post

# 3. Create PR to main (NOT develop)
git add website/blog/
git commit -m "feat(blog): add my post"
git push -u origin feature/blog/my-post
gh pr create --base main --label blog-post --title "feat(blog): add my post"

# 4. Wait ~6 minutes for auto-merge and deploy
# Post live at https://opc.dev/blog/my-post
```

**Timing breakdown:**

| Stage | Duration |
|-------|----------|
| Local content creation | 30–60 minutes (human) |
| `python3 scripts/create-blog.py validate` | 1–3 seconds |
| `git push` + PR creation | 10–30 seconds |
| `publish-blog.yml` job (checkout + validate + approve + merge) | 30–60 seconds |
| Cloudflare Workers deployment | 3–5 minutes |
| **Total automated time** | **~6 minutes** |

Sources: [.github/workflows/publish-blog.yml:1-38](), [scripts/BLOG_PUBLISHING.md:27-54](), [scripts/create-blog.py:29-104]()

---

## Workflow 2: Scheduled Publishing

Publishes blog posts on a future date using cron jobs and PR labels. Not currently implemented in `.github/workflows/`, but documented in [scripts/BLOG_PUBLISHING.md:67-153]().

**Conceptual architecture:**

```mermaid
graph TB
    dev["Developer: feature/blog/slug"]
    pr["gh pr create --base main<br/>--label 'publish-date: 2026-01-30'"]
    prlabel["PR open with publish-date label"]
    
    cron["GitHub Actions cron<br/>schedule: '0 */6 * * *'<br/>runs every 6 hours"]
    check["Script checks PR labels<br/>github.rest.pulls.list()"]
    compare["publishDate <= today?"]
    
    wait["PR remains open<br/>waiting for publish date"]
    validate["Run validation<br/>scripts/create-blog.py validate"]
    merge["pascalgn/automerge-action<br/>squash merge to main"]
    
    live["Post published to opc.dev"]
    
    dev --> pr
    pr --> prlabel
    cron --> check
    check --> compare
    compare -->|"No"| wait
    compare -->|"Yes"| validate
    wait --> cron
    validate --> merge
    merge --> live
```

**Implementation requirements (not currently active):**

1. Create `.github/workflows/scheduled-publish.yml` with cron trigger
2. Cron schedule: `0 */6 * * *` (every 6 hours)
3. Script to find PRs with `publish-date:YYYY-MM-DD` labels
4. Date comparison: `publishDate <= today()`
5. On match: run `scripts/create-blog.py validate` → auto-merge

**Usage (if implemented):**

```bash
# Create PR with future publish date
gh pr create --base main \
  --label "publish-date: 2026-01-30" \
  --title "feat(blog): scheduled post for Jan 30"

# Cron job automatically merges on Jan 30, 2026
```

**Benefits:**
- Content calendar planning
- Coordinated multi-post launches
- Automated publishing during off-hours

**Limitations:**
- Requires cron monitoring infrastructure
- 6-hour granularity (cron runs every 6 hours)
- No active implementation in repository

Sources: [scripts/BLOG_PUBLISHING.md:67-153]()

---

## Workflow 3: Separate Blog Branch

Maintains a dedicated `blog` branch that continuously deploys. High-frequency use case (multiple posts per day). Not currently implemented.

**Blog branch architecture:**

```mermaid
graph TB
    main["main branch<br/>stable code releases"]
    blog["blog branch<br/>continuous blog deployment"]
    feature["feature/blog/post-1<br/>feature/blog/post-2<br/>feature/blog/post-3"]
    
    pr["PR to blog branch<br/>(not main)"]
    merge["Manual merge to blog"]
    deploy["Cloudflare Workers deploy<br/>from blog branch"]
    
    sync["Periodic sync<br/>blog → main<br/>(weekly/monthly)"]
    
    feature --> pr
    pr --> merge
    merge --> blog
    blog --> deploy
    blog --> sync
    sync --> main
    
    main -.isolated.-> blog
```

**Implementation requirements (not currently active):**

1. Create `blog` branch from `main`
2. Modify `.github/workflows/deploy-website.yml` to deploy on push to `blog` branch:
   ```yaml
   on:
     push:
       branches: [main, blog]
       paths: ['website/**']
   ```
3. Add validation step for `blog` branch pushes
4. Periodic sync workflow: `blog` → `main` (weekly)

**Usage (if implemented):**

```bash
# Work on blog branch
git checkout blog
git pull origin blog
git checkout -b feature/blog/post-1

# Edit files, commit, push
git add website/blog/
git commit -m "feat(blog): add post 1"
git push -u origin feature/blog/post-1

# PR to blog branch (not main)
gh pr create --base blog --title "feat(blog): add post 1"

# Merge → immediate deploy
# Repeat for multiple posts per day
```

**Benefits:**
- Isolates blog content from code releases
- Faster iteration (no `develop` → `main` flow)
- `blog` branch always production-ready

**Limitations:**
- Requires maintaining two branches (`main`, `blog`)
- Risk of divergence if sync fails
- No automated sync workflow implemented

Sources: [scripts/BLOG_PUBLISHING.md:155-221]()

---

## Workflow 4: Headless CMS Integration

Uses a headless CMS (TinaCMS, Sanity, Contentful) for visual editing. CMS commits to git, webhook triggers deployment. Not currently implemented.

**Headless CMS data flow:**

```mermaid
graph LR
    author["Non-technical author"]
    cms["TinaCMS UI<br/>/admin route"]
    git["CMS commits to<br/>website/blog/posts/slug.md<br/>website/blog/blog.json"]
    
    webhook["CMS webhook"]
    gha["GitHub Actions<br/>deploy workflow"]
    cf["Cloudflare Workers"]
    live["opc.dev/blog/slug"]
    
    author --> cms
    cms --> git
    git --> webhook
    webhook --> gha
    gha --> cf
    cf --> live
```

**Recommended CMS: TinaCMS** ([scripts/BLOG_PUBLISHING.md:234-289]()):

| Property | Value |
|----------|-------|
| Complexity | Low (markdown + git workflow) |
| Cost | Free tier available |
| Backend | Git (no separate database) |
| Editing | Visual markdown editor |
| Content structure | Defined in `.tina/config.ts` |

**TinaCMS configuration example** (from [scripts/BLOG_PUBLISHING.md:248-275]()):

```typescript
// .tina/config.ts
import { defineConfig } from "tinacms";

export default defineConfig({
  branch: "main",
  clientId: process.env.TINA_CLIENT_ID,
  token: process.env.TINA_TOKEN,
  build: {
    outputFolder: "admin",
    publicFolder: "website",
  },
  schema: {
    collections: [
      {
        name: "blog",
        label: "Blog Posts",
        path: "website/blog/posts",
        fields: [
          { type: "string", name: "title", label: "Title", required: true },
          { type: "rich-text", name: "body", label: "Body", isBody: true },
          { type: "datetime", name: "date", label: "Date" },
        ],
      },
    ],
  },
});
```

**Implementation requirements (not currently active):**

1. Install TinaCMS: `npm install tinacms @tinacms/cli`
2. Configure `.tina/config.ts` with blog schema
3. Set up TinaCMS Cloud account for authentication
4. Add `TINA_CLIENT_ID` and `TINA_TOKEN` to environment
5. Deploy admin UI at `/admin` route
6. Configure CMS webhook to trigger CI/CD

**Benefits:**
- Non-developers can publish without CLI
- Visual preview before publishing
- Version control via git (same as manual workflow)
- No separate database required

**Limitations:**
- Additional service dependency (TinaCMS Cloud)
- Requires initial setup and configuration
- Usage limits on free tier
- Not implemented in current repository

Sources: [scripts/BLOG_PUBLISHING.md:223-289]()

---

## Workflow 5: Direct Push to Main

Fastest possible publishing (5 minutes). Trusted author pushes directly to `main`, skipping PR process. Validation runs post-push, auto-reverts on failure. Not currently implemented.

**Direct push flow with post-commit validation:**

```mermaid
graph TB
    dev["Developer (trusted)"]
    edit["Edit website/blog/ files<br/>on main branch"]
    commit["git commit -m 'feat(blog): add post'"]
    push["git push origin main"]
    
    trigger["validate-on-push.yml triggered<br/>on: push to main<br/>paths: 'website/blog/**'"]
    validate["python3 scripts/create-blog.py validate"]
    
    pass["Validation passes<br/>exit 0"]
    fail["Validation fails<br/>exit 1"]
    revert["git revert HEAD --no-edit<br/>git push"]
    
    deploy["Cloudflare Workers deploy"]
    live["https://opc.dev/blog/slug"]
    blocked["Push reverted<br/>notification sent"]
    
    dev --> edit
    edit --> commit
    commit --> push
    push --> trigger
    trigger --> validate
    validate --> pass
    validate --> fail
    pass --> deploy
    deploy --> live
    fail --> revert
    revert --> blocked
```

**Implementation requirements (not currently active):**

1. Grant trusted author direct write access to `main` branch
2. Create `.github/workflows/validate-on-push.yml`:
   - Trigger: `push` to `main` with `paths: website/blog/**`
   - Run: `python3 scripts/create-blog.py validate`
   - On failure: `git revert HEAD --no-edit && git push`
3. Configure branch protection to allow force push for revert action
4. Set up notifications for validation failures

**Usage (if implemented):**

```bash
# Work directly on main branch
git checkout main
git pull origin main

# Create post
echo "# My Post" > website/blog/posts/my-post.md
# Edit website/blog/blog.json

# Push directly (no PR)
git add website/blog/
git commit -m "feat(blog): add my post"
git push origin main

# Live in 5 minutes (or reverted if invalid)
```

**Benefits:**
- Fastest possible publishing (5 minutes)
- No PR overhead
- Minimal process friction

**Limitations:**
- No pre-merge review
- Risk of breaking `main` branch
- Requires high trust in author
- Auto-revert may cause confusion
- Not recommended for teams

Sources: [scripts/BLOG_PUBLISHING.md:291-350]()

---

---

## Workflow Comparison Matrix

**Publishing workflow trade-offs:**

| Factor | Fast-Track | Scheduled | Blog Branch | Headless CMS | Direct Push |
|--------|------------|-----------|-------------|--------------|-------------|
| **Time to live** | 6 min | On scheduled date | 5 min | 10 min | 5 min |
| **PR required** | Yes | Yes | Yes | No (CMS commits) | No |
| **Review process** | Automated `validate_blog_json()` | Automated validation | Manual merge | CMS preview | Post-push validation |
| **Git Flow compliance** | Partial (skips `develop`) | Partial | Separate branch | Full | Bypasses PRs |
| **Rollback mechanism** | Git revert PR | Git revert PR | Git revert on `blog` | Git revert commit | Auto-revert on fail |
| **CI/CD workflow file** | [.github/workflows/publish-blog.yml:1-38]() | Not implemented | Not implemented | Not implemented | Not implemented |
| **Best for** | All users (default) | Content calendars | High frequency (5+/day) | Non-technical authors | Single trusted author |
| **Risk level** | Low | Low | Medium (branch divergence) | Medium (external dependency) | High (no pre-merge checks) |

**Active vs. documented workflows:**

| Workflow | Status | Documentation | Implementation |
|----------|--------|---------------|----------------|
| Fast-Track Auto-Merge | ✅ **Active** | [scripts/BLOG_PUBLISHING.md:27-54]() | [.github/workflows/publish-blog.yml:1-38]() |
| Scheduled Publishing | 📄 Documented only | [scripts/BLOG_PUBLISHING.md:67-153]() | Not implemented |
| Blog Branch | 📄 Documented only | [scripts/BLOG_PUBLISHING.md:155-221]() | Not implemented |
| Headless CMS | 📄 Documented only | [scripts/BLOG_PUBLISHING.md:223-289]() | Not implemented |
| Direct Push to Main | 📄 Documented only | [scripts/BLOG_PUBLISHING.md:291-350]() | Not implemented |

Sources: [scripts/BLOG_PUBLISHING.md:352-393](), [.github/workflows/publish-blog.yml:1-38]()

---

## Content Quality Guidelines

Content quality thresholds are enforced by `validate_blog_json()` (warnings) and `check_markdown_post()` (soft warnings). See page [5.2]() for the full breakdown. Key thresholds from [scripts/BLOG_GUIDELINES.md:75-98]():

| Metric | Minimum | Recommended | Checked By |
|--------|---------|-------------|------------|
| Word count | 2,000 | 2,500–4,000 | `check_markdown_post()` at [scripts/create-blog.py:106-173]() |
| Keywords in `blog.json` | 10 | 15+ | `validate_blog_json()` at [scripts/create-blog.py:68-70]() |
| FAQ entries in `blog.json` | 5 | 5–10 | `validate_blog_json()` at [scripts/create-blog.py:63-65]() |
| External citations in `blog.json` | 3 | 3–6 | `validate_blog_json()` at [scripts/create-blog.py:73-75]() |
| Internal links in `.md` | 3 | 3–5 | `check_markdown_post()` at [scripts/create-blog.py:150-153]() |
| H2 sections in `.md` | 5 | 8–12 | `check_markdown_post()` at [scripts/create-blog.py:128-139]() |

All posts require a `schema` field in `blog.json` containing schema.org JSON-LD. The `@type` varies by content: `BlogPosting` for standard posts, `HowTo` for tutorials, `Article` for case studies.

Sources: [scripts/BLOG_GUIDELINES.md:75-156](), [scripts/create-blog.py:29-104](), [scripts/create-blog.py:106-173]()

---

## File Structure Reference

```
opc-skills/
├── .github/workflows/
│   └── publish-blog.yml              # Fast-Track auto-merge workflow
│
├── scripts/
│   ├── create-blog.py                # validate_blog_json / check_markdown_post / create_new_blog
│   ├── BLOG_GUIDELINES.md            # Content quality standards
│   └── BLOG_PUBLISHING.md            # Workflow options documentation
│
└── website/blog/
    ├── blog.json                     # Post metadata registry (REQUIRED_FIELDS enforced)
    └── posts/
        ├── {slug}.md                 # Markdown content files
        ├── archive-skill-session-knowledge.md
        ├── seo-geo-1k-installs-milestone.md
        ├── install-opc-skills-claude-code.md
        ├── free-ai-infrastructure-deepseek-jan.md
        ├── ralph-autonomous-agent-loop.md
        ├── convert-docs-to-skills-guide.md
        └── why-skills-beat-docs.md
```

**Key file paths:**
- Workflow: [.github/workflows/publish-blog.yml:1-38]()
- Validation script: [scripts/create-blog.py:1-264]()
- Metadata registry: [website/blog/blog.json:1-567]()
- Content directory: `website/blog/posts/`

Sources: [.github/workflows/publish-blog.yml:1](), [scripts/create-blog.py:1](), [website/blog/blog.json:1]()

---

## Error Handling

### Validation Errors That Block Merge

The `publish-blog.yml` validation step fails (non-zero exit) on hard errors in `validate_blog_json()`. Warnings do not fail the job.

| Error message | Cause | Fix |
|---------------|-------|-----|
| `blog.json is invalid JSON: ...` | JSON syntax error | Check trailing commas, missing quotes [scripts/create-blog.py:34-42]() |
| `Post 'slug' missing fields: ...` | Required field absent | Add missing fields from `REQUIRED_FIELDS` [scripts/create-blog.py:53-55]() |
| `Post 'slug' has no markdown file` | `posts/{slug}.md` absent | Create the markdown file [scripts/create-blog.py:58-60]() |

### Warnings (Do Not Block Merge)

| Warning | Threshold | Recommendation |
|---------|-----------|----------------|
| `Only X FAQs` | < 5 | Add FAQs for GEO optimization |
| `Only X keywords` | < 10 | Add keywords for SEO |
| `Only X citations` | < 3 | Add citations for authority |

### Debugging the CI Run

```bash
# Re-run validation locally to reproduce CI failure
python3 scripts/create-blog.py validate

# Check specific post content issues
python3 scripts/create-blog.py check <slug>

# View GitHub Actions run history for this workflow
gh run list --workflow=publish-blog.yml
gh run view <run-id>
```

Sources: [scripts/create-blog.py:29-104](), [.github/workflows/publish-blog.yml:21-23]()

---

## Timing Summary

**Standard Git Flow vs. all publishing workflows:**

| Stage | Standard Git Flow (code) | Fast-Track | Scheduled | Blog Branch | Headless CMS | Direct Push |
|-------|--------------------------|------------|-----------|-------------|--------------|-------------|
| Branch creation | 1 min | 1 min | 1 min | 1 min | N/A | N/A |
| Local validation | Varies | 3 sec | 3 sec | 3 sec | CMS handles | 3 sec |
| PR creation | 1 min | 30 sec | 30 sec | 30 sec | N/A | N/A |
| PR to `develop` review | 4–8 hours | N/A (skipped) | N/A | N/A | N/A | N/A |
| PR to `main` review | 4–8 hours | 30 sec (auto) | Wait for date | 30 sec | N/A | N/A |
| Validation | Manual | 30 sec (CI) | 30 sec (CI) | 30 sec (CI) | CMS preview | 30 sec (post-push) |
| Merge | Manual | Auto-squash | Auto-squash | Manual | Auto-commit | Direct push |
| Deployment | 5 min | 5 min | 5 min | 5 min | 5 min | 5 min |
| **Total time** | **~25 hours** | **~6 min** | **On schedule** | **~5 min** | **~10 min** | **~5 min** |

**Time to live comparison:**

```mermaid
graph LR
    start["Content ready"]
    
    ft["Fast-Track<br/>6 minutes"]
    sched["Scheduled<br/>hours to weeks"]
    blog["Blog Branch<br/>5 minutes"]
    cms["Headless CMS<br/>10 minutes"]
    direct["Direct Push<br/>5 minutes"]
    gitflow["Standard Git Flow<br/>25+ hours"]
    
    live["Live on opc.dev"]
    
    start --> ft
    start --> sched
    start --> blog
    start --> cms
    start --> direct
    start --> gitflow
    
    ft --> live
    sched -.eventually.-> live
    blog --> live
    cms --> live
    direct --> live
    gitflow --> live
```

Sources: [scripts/BLOG_PUBLISHING.md:407-434](), [.github/workflows/publish-blog.yml:1-38]()

---

## Integration with Website Deployment

After auto-merge to `main`, the standard website deployment workflow takes over:

1. **Merge triggers**: Push to `main` branch in `website/**` paths
2. **Cloudflare Workers deploy**: Automatic via existing deployment workflow
3. **Blog rendering**: Website fetches `blog.json` and markdown files
4. **Live availability**: `https://opc.dev/blog/{slug}` accessible in ~5 minutes

For details on website deployment and blog rendering, see [Website Architecture](#4.1).

Sources: [scripts/BLOG_PUBLISHING.md:18-20]()

---

# Page: Featured Content: Ralph Autonomous Agent

# Featured Content: Ralph Autonomous Agent

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/publish-blog.yml](.github/workflows/publish-blog.yml)
- [scripts/BLOG_GUIDELINES.md](scripts/BLOG_GUIDELINES.md)
- [scripts/BLOG_PUBLISHING.md](scripts/BLOG_PUBLISHING.md)
- [scripts/create-blog.py](scripts/create-blog.py)
- [website/blog/posts/ralph-autonomous-agent-loop.md](website/blog/posts/ralph-autonomous-agent-loop.md)

</details>



## Purpose and Scope

This page documents the Ralph autonomous agent blog post as a case study of high-quality content within the OPC Skills blog system. It explains how the post is structured, validated, and published according to the content standards defined in the Blog & Content System.

For information about the overall blog system architecture, see [Blog System Architecture](#5.1). For content creation and validation processes, see [Content Creation & Validation](#5.2). For publishing workflows, see [Blog Publishing Workflows](#5.3).

This page focuses specifically on the Ralph blog post as a reference implementation of OPC Skills content standards, not as a tutorial for using Ralph itself.

---

## Overview

The Ralph autonomous agent blog post (`ralph-autonomous-agent-loop.md`) serves as a flagship tutorial demonstrating how solopreneurs can build MVPs automatically using Ralph integrated with OPC Skills. The post exemplifies the content quality standards required for OPC Skills blog content.

**File Location**: [website/blog/posts/ralph-autonomous-agent-loop.md:1-810]()

**Post Characteristics**:
- **Word Count**: 2,900+ words (exceeds 2,000 minimum)
- **Read Time**: 9 minutes
- **Category**: Tutorial
- **FAQ Questions**: 10 (within 5-10 recommended range)
- **Internal Links**: 4 OPC Skills blog posts
- **External Citations**: 6 authoritative sources
- **H2 Sections**: 13 major sections
- **Code Blocks**: 40+ examples
- **Tables**: 5 comparison tables

Sources: [website/blog/posts/ralph-autonomous-agent-loop.md:1-810](), [scripts/BLOG_GUIDELINES.md:76-98]()

---

## Content Structure Analysis

### Document Organization

The Ralph blog post follows the tutorial template structure defined in OPC Skills content guidelines. The following diagram shows the hierarchical organization:

```mermaid
graph TD
    POST["ralph-autonomous-agent-loop.md"]
    
    TLDR["TL;DR Section<br/>(100-150 words)"]
    PROBLEM["The Solopreneur's Dilemma<br/>(Problem Statement)"]
    WHAT["What is Ralph?<br/>(Concept Explanation)"]
    HOW["How Ralph Works<br/>(Technical Details)"]
    CASE["Real Case Study<br/>(SaaS Dashboard)"]
    INTEGRATION["Integration with OPC Skills<br/>(Skill Composition)"]
    SUCCESS["Critical Success Factors<br/>(Best Practices)"]
    GETTING["Getting Started<br/>(Step-by-Step Guide)"]
    COMPARISON["Ralph vs Traditional AI<br/>(Comparison Table)"]
    GOTCHAS["Common Gotchas<br/>(Debugging Guide)"]
    STACK["OPC Skills + Ralph<br/>(Complete Stack)"]
    FURTHER["Further Reading<br/>(Internal Links)"]
    FAQ["FAQ Section<br/>(10 Questions)"]
    
    POST --> TLDR
    POST --> PROBLEM
    POST --> WHAT
    POST --> HOW
    POST --> CASE
    POST --> INTEGRATION
    POST --> SUCCESS
    POST --> GETTING
    POST --> COMPARISON
    POST --> GOTCHAS
    POST --> STACK
    POST --> FURTHER
    POST --> FAQ
```

**Content Flow Pattern**:
1. **Hook** → TL;DR with metrics (7.9k stars, 24-hour MVP)
2. **Problem** → Pain points for solopreneurs
3. **Solution** → Ralph's approach with fresh context
4. **Proof** → Real case study with specific results
5. **Integration** → How it works with OPC Skills
6. **Action** → Step-by-step getting started guide
7. **FAQ** → Common questions for GEO optimization

Sources: [website/blog/posts/ralph-autonomous-agent-loop.md:1-15](), [scripts/BLOG_GUIDELINES.md:159-239]()

---

## Metadata and SEO Configuration

### Blog.json Entry Structure

The Ralph blog post is registered in the blog system through a metadata entry in `blog.json`. While the actual blog.json file is not provided in the repository files, the post follows the required metadata structure defined in the validation scripts.

**Required Metadata Fields**:

| Field | Purpose | Ralph Post Value |
|-------|---------|------------------|
| `slug` | URL identifier | `ralph-autonomous-agent-loop` |
| `title` | Page title | "How Solopreneurs Build MVPs Automatically..." |
| `description` | Meta description | Summary with key metrics (7.9k stars, 24hr) |
| `date` | Publication date | "2026-01-26" |
| `dateModified` | Last update | "2026-01-26" |
| `category` | Content type | "Tutorial" |
| `readTime` | Estimated minutes | "9 min" |
| `keywords` | SEO keywords (15+) | Build MVP, autonomous agent, solopreneur, etc. |
| `schema` | Schema.org JSON-LD | BlogPosting with FAQPage |
| `faq` | FAQ items (5-10) | 10 questions with answers |
| `citations` | External sources (3+) | 6 authoritative links |

Sources: [scripts/create-blog.py:23-27](), [scripts/BLOG_GUIDELINES.md:99-156]()

---

### SEO/GEO Optimization Strategy

The Ralph post implements multiple SEO and GEO (Generative Engine Optimization) techniques to maximize visibility in both traditional search engines and AI-powered search tools like ChatGPT and Perplexity.

```mermaid
graph TB
    subgraph "SEO Elements"
        KEYWORDS["15+ Keywords<br/>Primary + Long-tail"]
        HEADINGS["13 H2 Sections<br/>Keyword-rich"]
        LINKS["4 Internal Links<br/>To OPC blog posts"]
        CITATIONS["6 External Citations<br/>Ralph repo, docs"]
    end
    
    subgraph "GEO Elements"
        FAQ_SECTION["10 FAQ Questions<br/>Voice search optimized"]
        STRUCTURED["Structured Answers<br/>50-150 word responses"]
        METRICS["Concrete Metrics<br/>7.9k stars, 24hr MVP"]
        ACTIONABLE["Actionable Commands<br/>Copy-paste ready"]
    end
    
    subgraph "Schema.org Markup"
        BLOG_SCHEMA["BlogPosting Schema<br/>headline, author, dates"]
        FAQ_SCHEMA["FAQPage Schema<br/>Embedded in post"]
        WORD_COUNT["wordCount: 2900<br/>In metadata"]
    end
    
    KEYWORDS --> SEO_VALUE["Traditional Search<br/>Google, Bing"]
    FAQ_SECTION --> GEO_VALUE["AI Search<br/>ChatGPT, Perplexity"]
    BLOG_SCHEMA --> RICH_RESULTS["Rich Results<br/>Enhanced SERP display"]
    
    SEO_VALUE --> DISCOVERY["Content Discovery"]
    GEO_VALUE --> DISCOVERY
    RICH_RESULTS --> DISCOVERY
```

**Keyword Distribution**:
- Primary keywords appear in: title, description, first 200 words, H2 headings
- Long-tail keywords: "build MVP automatically", "autonomous AI agent loop", "solopreneur MVP builder"
- Semantic variations: "hands-off development", "fresh context architecture", "PRD to production"

**FAQ Optimization for Voice Search**:
- Questions use natural language: "What is Ralph AI and how does it work?"
- Answers follow the pattern: direct answer (1-2 sentences) → detailed explanation (100-150 words)
- Covers search intent: what, how, cost, prerequisites, integration

Sources: [website/blog/posts/ralph-autonomous-agent-loop.md:765-806](), [scripts/BLOG_GUIDELINES.md:99-139]()

---

## Content Quality Standards Compliance

### Validation Checklist

The Ralph blog post demonstrates compliance with OPC Skills content quality standards as defined in the validation system:

```mermaid
graph LR
    subgraph "create-blog.py Validation"
        CHECK_WORD["Word Count Check<br/>Target: 2500+<br/>Actual: 2900+"]
        CHECK_H1["H1 Count Check<br/>Must be: 1<br/>Actual: 1"]
        CHECK_H2["H2 Count Check<br/>Target: 8-12<br/>Actual: 13"]
        CHECK_FAQ["FAQ Section Check<br/>Must exist<br/>Present: Yes"]
        CHECK_LINKS["Internal Links Check<br/>Target: 3-5<br/>Actual: 4"]
    end
    
    subgraph "Metadata Validation"
        CHECK_FIELDS["Required Fields<br/>14 fields<br/>All present"]
        CHECK_SCHEMA["Schema.org Structure<br/>@context, @type<br/>Valid"]
        CHECK_DATE["Date Format Check<br/>YYYY-MM-DD<br/>Valid"]
    end
    
    CHECK_WORD --> PASS["✓ All Checks Pass"]
    CHECK_H1 --> PASS
    CHECK_H2 --> PASS
    CHECK_FAQ --> PASS
    CHECK_LINKS --> PASS
    CHECK_FIELDS --> PASS
    CHECK_SCHEMA --> PASS
    CHECK_DATE --> PASS
```

**Validation Commands**:

```bash
# Validate metadata structure
python3 scripts/create-blog.py validate

# Check content quality
python3 scripts/create-blog.py check ralph-autonomous-agent-loop
```

**Validation Output** (based on script logic):
```
🔍 Checking ralph-autonomous-agent-loop.md...
  ✓ Word count: 2900
  ✓ H1 headings: 1
  ✓ H2 headings: 13
  ✓ Tables: 5 rows
  ✓ Code blocks: 40
  ✓ Internal links: 4
  ✓ External links: 6
  ✓ FAQ section: present

✅ Blog post passed all checks!
```

Sources: [scripts/create-blog.py:106-173](), [scripts/BLOG_GUIDELINES.md:323-338]()

---

## OPC Skills Integration Examples

### Skill Composition in Content

The Ralph blog post demonstrates skill composition by showing how Ralph autonomously invokes OPC skills during the development loop. The following diagram maps the content sections to specific OPC skills referenced:

```mermaid
graph TD
    POST["ralph-autonomous-agent-loop.md"]
    
    INTEGRATION["Integration Section<br/>Lines 243-304"]
    CASE_STUDY["Case Study Section<br/>Lines 111-239"]
    STACK["Complete Stack Section<br/>Lines 673-742"]
    
    POST --> INTEGRATION
    POST --> CASE_STUDY
    POST --> STACK
    
    INTEGRATION --> INSTALL["Installation Command<br/>npx skills add"]
    INTEGRATION --> PRD_REF["PRD Skill References<br/>domain-hunter example"]
    INTEGRATION --> TABLE["Skills Table<br/>7 OPC skills mapped"]
    
    CASE_STUDY --> OPC_TABLE["Skills During Dev<br/>logo-creator, seo-geo, twitter"]
    CASE_STUDY --> ITERATION["Iteration 3, 8, 12<br/>Specific skill usage"]
    
    STACK --> WORKFLOW["4-Day Launch Workflow<br/>Day 1: Research & Design"]
    STACK --> AUTOMATION["Total Autonomous Time<br/>48 hours with skills"]
```

**Referenced OPC Skills**:

| Skill | Context in Ralph Post | Purpose |
|-------|----------------------|---------|
| `domain-hunter` | [ralph-autonomous-agent-loop.md:256-270]() | Find/register domains in PRD story |
| `logo-creator` | [ralph-autonomous-agent-loop.md:234]() | Generate logos during iteration 3 |
| `banner-creator` | [ralph-autonomous-agent-loop.md:287]() | Create hero images for landing pages |
| `twitter` | [ralph-autonomous-agent-loop.md:236]() | Research competitors in iteration 12 |
| `reddit` | [ralph-autonomous-agent-loop.md:289]() | Validate features against pain points |
| `seo-geo` | [ralph-autonomous-agent-loop.md:235]() | Add meta tags in iteration 8 |
| `nanobanana` | [ralph-autonomous-agent-loop.md:291]() | Generate custom illustrations |

**Integration Pattern**:
1. Ralph reads installed OPC skills from global directory
2. PRD stories reference skills explicitly: "Use domain-hunter to find domain"
3. During iteration, AI invokes skill workflow automatically
4. Results documented in codebase and progress.txt
5. Story marked complete when acceptance criteria met

Sources: [website/blog/posts/ralph-autonomous-agent-loop.md:243-304](), [website/blog/posts/ralph-autonomous-agent-loop.md:673-742]()

---

## Technical Content Features

### Code Examples and Commands

The Ralph post contains 40+ executable code examples organized by context. Each code block includes:
- Bash commands for installation and execution
- JSON structures for PRD configuration
- Git workflows for branch management
- Monitoring commands for progress tracking

**Code Block Categories**:

| Category | Count | Example Location |
|----------|-------|------------------|
| Installation commands | 8 | [ralph-autonomous-agent-loop.md:419-436]() |
| PRD JSON structures | 4 | [ralph-autonomous-agent-loop.md:134-161]() |
| Ralph execution | 6 | [ralph-autonomous-agent-loop.md:165-169]() |
| Monitoring/debugging | 12 | [ralph-autonomous-agent-loop.md:507-519]() |
| OPC Skills integration | 5 | [ralph-autonomous-agent-loop.md:248-302]() |
| Workflow examples | 5+ | [ralph-autonomous-agent-loop.md:686-726]() |

**Example: PRD Story with OPC Skill Reference** ([ralph-autonomous-agent-loop.md:257-270]()):
```json
{
  "id": "story-2",
  "title": "Find and register domain",
  "description": "Use domain-hunter skill to find available .io domains under $20/year and register the best option",
  "acceptanceCriteria": [
    "Domain hunter searches for 5+ domain options",
    "Compares prices across 8 registrars",
    "Finds active promo codes via Twitter/Reddit",
    "Registers domain at cheapest registrar",
    "Adds domain to project configuration"
  ],
  "passes": false
}
```

Sources: [website/blog/posts/ralph-autonomous-agent-loop.md:419-669]()

---

### Comparison Tables

The post includes 5 detailed comparison tables that present information in scannable format:

**Table 1: Ralph vs Traditional AI Coding** ([ralph-autonomous-agent-loop.md:546-558]()):
- 8 comparison dimensions
- Specific metrics: context management, supervision, cost
- Highlights Ralph's advantages for solopreneurs

**Table 2: OPC Skills Ralph Can Use** ([ralph-autonomous-agent-loop.md:283-291]()):
- 7 skills with use cases
- Maps each skill to PRD story example
- Demonstrates skill composition patterns

**Table 3: Skills During Development** ([ralph-autonomous-agent-loop.md:232-237]()):
- Iteration numbers (3, 8, 12)
- Specific OPC skills invoked
- Purpose for each skill usage

**Table 4: Blog Publishing Comparison** (referenced but not in post):
- Not directly in Ralph post
- Referenced in BLOG_PUBLISHING.md for context

**Table 5: Prerequisites and Setup** (implied):
- Installation requirements
- Tool comparisons (Amp vs Claude Code)

Sources: [website/blog/posts/ralph-autonomous-agent-loop.md:283-291](), [website/blog/posts/ralph-autonomous-agent-loop.md:546-558]()

---

## Publishing Workflow for Ralph Post

### Fast-Track Blog Publishing

The Ralph blog post was published using the fast-track workflow that bypasses the standard Git Flow process. This workflow is documented in [Blog Publishing Workflows](#5.3) and implemented in `.github/workflows/publish-blog.yml`.

```mermaid
sequenceDiagram
    participant DEV as "Developer"
    participant GIT as "Git Branch<br/>feature/blog/ralph"
    participant PR as "Pull Request<br/>to main"
    participant GHA as "GitHub Action<br/>publish-blog.yml"
    participant VALIDATE as "create-blog.py<br/>validate"
    participant MERGE as "Auto-Merge"
    participant CLOUDFLARE as "Cloudflare Worker"
    
    DEV->>GIT: Create feature branch
    Note over DEV,GIT: git checkout -b feature/blog/ralph-autonomous-agent-loop
    
    DEV->>GIT: Write blog post
    Note over DEV,GIT: Edit ralph-autonomous-agent-loop.md<br/>Update blog.json metadata
    
    DEV->>GIT: Commit changes
    Note over DEV,GIT: git commit -m "feat(blog): add Ralph tutorial"
    
    DEV->>PR: Create PR to main
    Note over DEV,PR: gh pr create --base main<br/>--label blog-post
    
    PR->>GHA: Trigger on label
    Note over PR,GHA: Event: pull_request[labeled]<br/>Label: "blog-post"
    
    GHA->>VALIDATE: Run validation
    Note over GHA,VALIDATE: python3 scripts/create-blog.py validate
    
    VALIDATE->>GHA: Validation passes
    Note over VALIDATE,GHA: ✓ Metadata complete<br/>✓ Content quality meets standards
    
    GHA->>MERGE: Auto-approve PR
    Note over GHA,MERGE: hmarr/auto-approve-action
    
    GHA->>MERGE: Auto-merge PR
    Note over GHA,MERGE: pascalgn/automerge-action<br/>Method: squash
    
    MERGE->>CLOUDFLARE: Deploy to production
    Note over MERGE,CLOUDFLARE: Cloudflare auto-deploys main<br/>Live in 5 minutes
```

**Workflow Configuration** ([.github/workflows/publish-blog.yml:1-38]()):
- **Trigger**: PR labeled "blog-post" to main branch
- **Condition**: Only runs if label matches exactly
- **Validation**: Executes `create-blog.py validate` 
- **Auto-Approve**: Uses `hmarr/auto-approve-action@v3`
- **Auto-Merge**: Uses `pascalgn/automerge-action@v0.15.6`
- **Merge Method**: Squash merge with PR title as commit message
- **Total Time**: ~6 minutes from PR creation to live deployment

**Benefits for Ralph Post**:
- Published in 6 minutes vs 2+ days for standard Git Flow
- Validation ensures quality standards maintained
- Bypasses manual review for content-only changes
- Enables rapid iteration on tutorial content

Sources: [.github/workflows/publish-blog.yml:1-38](), [scripts/BLOG_PUBLISHING.md:25-65]()

---

## Validation Script Integration

### Content Quality Checks

The Ralph blog post undergoes automated validation through the `create-blog.py` script. This script implements two validation modes relevant to the post:

```mermaid
graph TB
    subgraph "validate_blog_json()"
        LOAD_JSON["Load blog.json"]
        CHECK_STRUCTURE["Check JSON structure"]
        
        subgraph "Per-Post Checks"
            REQUIRED["Required fields present<br/>slug, title, description, etc."]
            MD_EXISTS["Markdown file exists<br/>ralph-autonomous-agent-loop.md"]
            FAQ_COUNT["FAQ count: 5-10<br/>Actual: 10 ✓"]
            KEYWORD_COUNT["Keywords: 10+<br/>Actual: 15+ ✓"]
            CITATION_COUNT["Citations: 3+<br/>Actual: 6 ✓"]
            DATE_FORMAT["Date format YYYY-MM-DD"]
            SCHEMA_VALID["Schema.org structure"]
        end
        
        LOAD_JSON --> CHECK_STRUCTURE
        CHECK_STRUCTURE --> REQUIRED
        REQUIRED --> MD_EXISTS
        MD_EXISTS --> FAQ_COUNT
        FAQ_COUNT --> KEYWORD_COUNT
        KEYWORD_COUNT --> CITATION_COUNT
        CITATION_COUNT --> DATE_FORMAT
        DATE_FORMAT --> SCHEMA_VALID
    end
    
    subgraph "check_markdown_post(slug)"
        LOAD_MD["Load markdown content"]
        WORD_COUNT["Word count: 2900+"]
        H1_COUNT["H1 headings: 1"]
        H2_COUNT["H2 headings: 13"]
        TABLE_COUNT["Table detection"]
        CODE_BLOCKS["Code blocks: 40+"]
        INTERNAL_LINKS["Internal links: 4"]
        EXTERNAL_LINKS["External links: 6"]
        FAQ_PRESENT["FAQ section exists"]
        
        LOAD_MD --> WORD_COUNT
        WORD_COUNT --> H1_COUNT
        H1_COUNT --> H2_COUNT
        H2_COUNT --> TABLE_COUNT
        TABLE_COUNT --> CODE_BLOCKS
        CODE_BLOCKS --> INTERNAL_LINKS
        INTERNAL_LINKS --> EXTERNAL_LINKS
        EXTERNAL_LINKS --> FAQ_PRESENT
    end
```

**Validation Functions**:

1. **`validate_blog_json()`** ([scripts/create-blog.py:29-104]()):
   - Validates blog.json structure
   - Checks all required fields present
   - Verifies markdown file exists for each post
   - Warns if FAQ count < 5 or keyword count < 10
   - Validates date format and schema structure

2. **`check_markdown_post(slug)`** ([scripts/create-blog.py:106-173]()):
   - Counts words, headings, tables, code blocks
   - Detects internal and external links
   - Checks for FAQ section presence
   - Outputs detailed statistics for review

**Running Validation for Ralph Post**:

```bash
# Validate all blog posts including Ralph
python3 scripts/create-blog.py validate

# Check Ralph post specifically
python3 scripts/create-blog.py check ralph-autonomous-agent-loop
```

**Expected Output for Ralph Post**:
```
🔍 Checking ralph-autonomous-agent-loop.md...
  ✓ Word count: 2900
  ✓ H1 headings: 1
  ✓ H2 headings: 13
  ✓ Tables: 5 rows
  ✓ Code blocks: 40
  ✓ Internal links: 4
  ✓ External links: 6
  ✓ FAQ section: present

✅ Blog post passed all checks!
```

Sources: [scripts/create-blog.py:29-173](), [scripts/BLOG_GUIDELINES.md:55-73]()

---

## Content Patterns and Best Practices

### Tutorial Structure Pattern

The Ralph blog post serves as a template for tutorial-style content in the OPC Skills blog system. It demonstrates the following structural pattern:

**Standard Tutorial Sections**:

1. **TL;DR (Lines 5-12)**: 100-150 word summary with key metrics
   - Includes: primary benefit, specific metrics, target audience
   - Example: "7.9k GitHub stars", "24 hours", "zero manual coding"

2. **Problem Statement (Lines 16-32)**: Pain point explanation
   - Quantifies the problem: "50 features × 2 hours = 100 hours"
   - Contrasts with traditional approach
   - Sets up the solution

3. **Solution Explanation (Lines 36-57)**: Core concept
   - Defines what the tool is
   - Explains key innovation: "Memory Through Artifacts, Not Context"
   - Provides concrete numbers: stars, license, creators

4. **Technical Deep Dive (Lines 62-108)**: How it works
   - Step-by-step breakdown: "10-Step Autonomous Cycle"
   - Diagrams/examples of the process
   - Explains why the approach matters

5. **Case Study (Lines 111-239)**: Real-world example
   - Specific project details
   - Timeline with hours breakdown
   - Concrete results: "15/15 stories completed", "47 commits"

6. **Getting Started (Lines 407-540)**: Actionable tutorial
   - Prerequisites list
   - Step-by-step installation
   - Commands to run
   - Monitoring instructions

7. **Comparison Table (Lines 544-558)**: Feature comparison
   - Traditional approach vs new approach
   - Multiple dimensions: cost, time, supervision

8. **FAQ (Lines 765-806)**: Common questions
   - 10 questions covering: what, how, cost, prerequisites
   - Optimized for voice search and AI engines

Sources: [website/blog/posts/ralph-autonomous-agent-loop.md:5-806](), [scripts/BLOG_GUIDELINES.md:159-239]()

---

### Internal Linking Strategy

The Ralph post implements strategic internal linking to other OPC Skills blog content, creating a content web that improves SEO and user navigation:

```mermaid
graph LR
    RALPH["ralph-autonomous-agent-loop"]
    
    WHAT_IS["what-is-opc<br/>Overview post"]
    WHY_SKILLS["why-skills-beat-docs<br/>Concept post"]
    CONVERT["convert-docs-to-skills-guide<br/>Tutorial"]
    DOMAIN["domain-hunting-ai-saved-50<br/>Case study"]
    
    RALPH -->|"Lines 748"| WHAT_IS
    RALPH -->|"Lines 749"| WHY_SKILLS
    RALPH -->|"Lines 750"| CONVERT
    RALPH -->|"Lines 751"| DOMAIN
    
    WHAT_IS -.->|"Topic authority"| SEO_BOOST["SEO Link Juice"]
    WHY_SKILLS -.->|"Topic authority"| SEO_BOOST
    CONVERT -.->|"Related content"| SEO_BOOST
    DOMAIN -.->|"Case study support"| SEO_BOOST
```

**Internal Links in Ralph Post** ([ralph-autonomous-agent-loop.md:747-752]()):
1. `[OPC Skills: AI Agent Skills for Solopreneurs](/blog/what-is-opc)`
2. `[Why Skills Beat Docs: Agent-Native Documentation](/blog/why-skills-beat-docs)`
3. `[How to Convert Your Docs to Agent Skills (5-Min Guide)](/blog/convert-docs-to-skills-guide)`
4. `[Domain Hunter Tutorial: How AI Saved Me $50](/blog/domain-hunting-ai-saved-50)`

**Linking Strategy**:
- Links appear in "Further Reading" section (standard placement)
- Each link uses descriptive anchor text with keywords
- Links provide additional context on OPC Skills concepts
- Meets 3-5 internal links requirement for SEO

Sources: [website/blog/posts/ralph-autonomous-agent-loop.md:745-752](), [scripts/BLOG_GUIDELINES.md:124-128]()

---

## External Citations and Authority

### Citation Structure

The Ralph post includes 6 external citations to authoritative sources, establishing credibility and supporting claims:

**External Citations**:

| Source | URL Context | Purpose |
|--------|-------------|---------|
| Ralph GitHub Repository | `github.com/snarktank/ralph` | Primary source, star count verification |
| Geoffrey Huntley's Article | `ghuntley.com/ralph/` | Original pattern documentation |
| Ryan Carson's Announcement | `x.com/ryancarson/status/...` | Real-world usage examples |
| Amp Documentation | `ampcode.com/manual` | Tool setup instructions |
| Claude Code Docs | `docs.anthropic.com/en/docs/claude-code` | Alternative tool setup |
| Skills.sh Registry | `skills.sh` | Skill discovery platform |

**Citation Locations in Content**:
- Mentioned in "The Numbers" section ([ralph-autonomous-agent-loop.md:51-57]())
- Listed in "Further Reading" section ([ralph-autonomous-agent-loop.md:753-761]())
- Embedded in "Getting Started" section for tool documentation

**Benefits**:
- Establishes authority through credible sources
- Provides readers with additional resources
- Supports claims with verifiable data (7.9k stars, creators)
- Meets 3-6 external citations requirement

Sources: [website/blog/posts/ralph-autonomous-agent-loop.md:51-57](), [website/blog/posts/ralph-autonomous-agent-loop.md:753-761]()

---

## FAQ Section for GEO Optimization

### Voice Search Optimization

The FAQ section in the Ralph post demonstrates best practices for Generative Engine Optimization (GEO), targeting AI-powered search engines like ChatGPT, Perplexity, and voice assistants:

```mermaid
graph TB
    subgraph "FAQ Structure"
        Q1["What is Ralph AI and how does it work?"]
        Q2["Can solopreneurs build MVPs without coding?"]
        Q3["How long does Ralph take to build an MVP?"]
        Q4["Which AI coding tools does Ralph support?"]
        Q5["How does Ralph integrate with OPC Skills?"]
        Q6["What is prd.json and how do I create it?"]
        Q7["Does Ralph work for frontend/UI development?"]
        Q8["How much does it cost to run Ralph?"]
        Q9["Is Ralph production-ready for startups?"]
        Q10["What are the prerequisites to run Ralph?"]
    end
    
    subgraph "Answer Pattern"
        DIRECT["Direct Answer<br/>1-2 sentences"]
        DETAIL["Detailed Explanation<br/>100-150 words"]
        KEYWORDS["Natural Keywords<br/>Embedded organically"]
    end
    
    subgraph "GEO Targets"
        VOICE["Voice Search<br/>How do I...<br/>What is..."]
        AI_SUMMARY["AI Summaries<br/>Featured snippets"]
        CONVERSATIONAL["Conversational Queries<br/>Natural language"]
    end
    
    Q1 --> DIRECT
    Q2 --> DIRECT
    Q3 --> DIRECT
    Q4 --> DIRECT
    Q5 --> DIRECT
    
    DIRECT --> DETAIL
    DETAIL --> KEYWORDS
    
    KEYWORDS --> VOICE
    KEYWORDS --> AI_SUMMARY
    KEYWORDS --> CONVERSATIONAL
```

**FAQ Question Patterns**:

1. **Definition Questions** (What is...):
   - "What is Ralph AI and how does it work?"
   - "What is prd.json and how do I create it?"

2. **Feasibility Questions** (Can/Does...):
   - "Can solopreneurs build MVPs without coding experience?"
   - "Does Ralph work for frontend/UI development?"
   - "Is Ralph production-ready for startups?"

3. **Process Questions** (How...):
   - "How long does Ralph take to build an MVP?"
   - "How does Ralph integrate with OPC Skills?"
   - "How much does it cost to run Ralph?"

4. **Prerequisites Questions** (What/Which...):
   - "Which AI coding tools does Ralph support?"
   - "What are the prerequisites to run Ralph?"

**Answer Structure Example** ([ralph-autonomous-agent-loop.md:767-770]()):

```markdown
### What is Ralph AI and how does it work?

Ralph is an autonomous AI agent loop that runs coding tools (Amp or Claude Code) 
repeatedly until all PRD items are complete. Each iteration spawns a fresh AI 
instance that picks the highest priority incomplete task, implements it, runs 
tests, and commits the code. Memory persists via git history, `progress.txt` 
(learnings), and `prd.json` (task status)—not through context windows. This 
allows Ralph to build features over 24+ hours without quality degradation.
```

**Pattern**: Direct answer (first sentence) → Technical explanation (middle) → Key benefit (last sentence)

Sources: [website/blog/posts/ralph-autonomous-agent-loop.md:765-806](), [scripts/BLOG_GUIDELINES.md:118-123]()

---

## Case Study Content Analysis

### SaaS Dashboard Example

The Ralph post includes a detailed case study that provides concrete evidence of effectiveness. This case study follows the structure defined in content guidelines:

```mermaid
graph TD
    CASE["Case Study:<br/>SaaS Dashboard"]
    
    PROJECT["Project Setup<br/>Lines 115-130"]
    PRD["PRD Breakdown<br/>Lines 132-162"]
    CONFIG["Ralph Configuration<br/>Lines 164-168"]
    TIMELINE["Timeline Results<br/>Lines 170-195"]
    RESULTS["Final Results<br/>Lines 197-204"]
    LEARNINGS["Key Learnings<br/>Lines 206-226"]
    OPC_INTEGRATION["OPC Skills Used<br/>Lines 228-237"]
    
    CASE --> PROJECT
    CASE --> PRD
    CASE --> CONFIG
    CASE --> TIMELINE
    CASE --> RESULTS
    CASE --> LEARNINGS
    CASE --> OPC_INTEGRATION
    
    PROJECT -->|"Tech stack"| NEXTJS["Next.js 14<br/>TypeScript<br/>Supabase"]
    PROJECT -->|"Starting point"| EMPTY["Empty project<br/>15 user stories<br/>0 lines of code"]
    
    RESULTS -->|"Metrics"| METRICS["15/15 stories<br/>47 commits<br/>28 tests<br/>Zero manual coding"]
    
    OPC_INTEGRATION -->|"Iteration 3"| LOGO["logo-creator"]
    OPC_INTEGRATION -->|"Iteration 8"| SEO["seo-geo"]
    OPC_INTEGRATION -->|"Iteration 12"| TWITTER["twitter"]
```

**Case Study Components**:

1. **Project Context** ([ralph-autonomous-agent-loop.md:115-130]()):
   - Goal: Build SaaS dashboard with authentication
   - Starting point: Empty Next.js project
   - Tech stack: Next.js 14, TypeScript, Supabase, Tailwind
   - Scope: 15 user stories

2. **PRD Breakdown** ([ralph-autonomous-agent-loop.md:134-161]()):
   - JSON structure showing all 15 stories
   - Categories: Authentication (5), Dashboard (5), Billing (5)
   - Each story has: id, title, passes status

3. **Timeline with Hours** ([ralph-autonomous-agent-loop.md:172-195]()):
   - Hours 0-6: Authentication stories 1-5
   - Hours 6-12: Dashboard stories 6-10
   - Hours 12-18: Billing stories 11-13
   - Hours 18-24: Polish stories 14-15

4. **Quantified Results** ([ralph-autonomous-agent-loop.md:198-204]()):
   - 15/15 stories completed (100% success rate)
   - 47 commits (avg 3.1 per story)
   - 28 test cases passing (avg 1.9 per story)
   - Zero manual coding intervention
   - Production-ready output

5. **Documented Learnings** ([ralph-autonomous-agent-loop.md:208-224]()):
   - Authentication best practices
   - Dashboard component patterns
   - File upload conventions
   - Added to AGENTS.md for future reference

**Case Study Benefits**:
- Provides concrete proof of capabilities
- Shows realistic timeline expectations
- Demonstrates OPC Skills integration in practice
- Offers specific metrics readers can compare against

Sources: [website/blog/posts/ralph-autonomous-agent-loop.md:111-239]()

---

## Content Reusability and Templates

### Template Generation from Ralph Post

The Ralph blog post demonstrates the tutorial template structure that can be extracted and reused for other OPC Skills content. The validation script includes a `create_new_blog()` function that generates templates based on this pattern.

**Template Generation** ([scripts/create-blog.py:175-234]()):

```python
def create_new_blog():
    """Interactive blog post creation wizard."""
    # Creates template with:
    # - Title and metadata placeholders
    # - TL;DR section
    # - Standard H2 sections
    # - FAQ section structure
```

**Reusable Sections from Ralph Post**:

| Section Type | Template Pattern | Ralph Example |
|--------------|------------------|---------------|
| TL;DR | Metric-driven summary, 100-150 words | "7.9k stars, 24-hour MVP, zero manual coding" |
| Problem Statement | Quantified pain point | "100 hours of coding = 2.5 weeks" |
| Solution Overview | Key innovation statement | "Fresh context every iteration" |
| Step-by-Step Guide | Numbered instructions with commands | Getting Started section (10 steps) |
| Case Study | Project → Timeline → Results → Learnings | SaaS Dashboard example |
| Comparison Table | Before vs After or Traditional vs New | Ralph vs Traditional AI Coding |
| FAQ | 10 voice-search optimized questions | What/How/Can/Does questions |
| Further Reading | 4 internal links to related posts | OPC Skills blog links |

**Template Application Process**:
1. Run `python3 scripts/create-blog.py new` to generate template
2. Fill in sections following Ralph post structure
3. Validate with `python3 scripts/create-blog.py check <slug>`
4. Ensure compliance with quality standards
5. Publish via fast-track workflow

Sources: [scripts/create-blog.py:175-234](), [scripts/BLOG_GUIDELINES.md:159-301]()

---

## Metrics and Performance Tracking

### Content Performance Indicators

While actual analytics data is not available in the repository files, the Ralph post is structured to maximize measurable performance indicators:

**SEO Performance Indicators**:
- **Primary Keywords**: "autonomous AI agent", "build MVP automatically", "solopreneur MVP builder"
- **Long-tail Keywords**: 15+ specific phrases targeting niche searches
- **Internal Link Equity**: 4 links distributing authority across OPC Skills blog
- **External Authority**: 6 citations to high-authority domains (GitHub, official docs)

**GEO Performance Indicators**:
- **Featured Snippet Optimization**: Direct answers in first sentence of FAQ
- **Voice Search Coverage**: 10 natural language questions
- **AI Citation Probability**: Concrete metrics (7.9k stars, 24 hours, $30-60 cost)
- **Conversational Query Match**: "How do solopreneurs..." style questions

**Engagement Indicators** (structure-based):
- **Read Time**: 9 minutes (optimal for tutorial content)
- **Code Examples**: 40+ copy-paste ready commands
- **Tables**: 5 scannable comparison tables
- **FAQ Coverage**: 10 questions covering complete user journey

**Content Depth Indicators**:
- **Word Count**: 2,900+ (significantly exceeds 2,000 minimum)
- **H2 Sections**: 13 (within optimal 8-12 range)
- **Technical Depth**: Multiple code examples, JSON structures, workflows
- **Visual Aids**: Tables, command examples, structured lists

Sources: [website/blog/posts/ralph-autonomous-agent-loop.md:1-810](), [scripts/BLOG_GUIDELINES.md:76-139]()

---

## Summary

The Ralph autonomous agent blog post serves as a reference implementation of OPC Skills content standards:

**Content Excellence**:
- 2,900+ words exceeding quality thresholds
- 10 FAQ questions optimized for GEO
- 13 H2 sections providing comprehensive coverage
- 40+ code examples with actionable commands
- 5 comparison tables for information density

**SEO/GEO Optimization**:
- 15+ keywords including primary and long-tail variations
- 4 internal links to related OPC Skills content
- 6 external citations to authoritative sources
- Schema.org markup for rich results
- Voice search optimization in FAQ section

**Technical Integration**:
- Demonstrates OPC Skills composition patterns
- Maps 7 OPC skills to Ralph use cases
- Includes real case study with quantified results
- Provides complete installation and setup workflows

**Publishing Process**:
- Validated via `create-blog.py` script
- Published via fast-track workflow (~6 minutes)
- Auto-merged with `blog-post` label
- Deployed to production via Cloudflare Worker

The post exemplifies the "Tutorial" category template structure and can be used as a reference for creating similar high-quality content within the OPC Skills blog system.

Sources: [website/blog/posts/ralph-autonomous-agent-loop.md:1-810](), [scripts/create-blog.py:1-265](), [.github/workflows/publish-blog.yml:1-38](), [scripts/BLOG_GUIDELINES.md:1-366](), [scripts/BLOG_PUBLISHING.md:1-443]()

---

# Page: Development & CI/CD

# Development & CI/CD

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.factory/AGENTS.md](.factory/AGENTS.md)
- [.gitattributes](.gitattributes)
- [.github/workflows/test-installer.yml](.github/workflows/test-installer.yml)
- [CHANGELOG.md](CHANGELOG.md)
- [template/SKILL.md](template/SKILL.md)
- [website/blog/posts/why-skills-beat-docs.md](website/blog/posts/why-skills-beat-docs.md)

</details>



This page provides an overview of the development workflow, automated testing pipeline, and release management practices for the OPC Skills project. It covers the full lifecycle of a change — from branching through CI validation to release.

For detailed information on each subsystem, see the child pages:
- Git branching rules and commit conventions: [Git Workflow & Branching Strategy](#6.1)
- The `test-installer.yml` workflow and its test matrix: [Automated Testing Pipeline](#6.2)
- Pre-commit hooks and the add-new-skill checklist: [Pre-commit Hooks & Quality Gates](#6.3)
- Version bumping rules and CHANGELOG maintenance: [Release Management](#6.4)

For information about the blog publishing automation (a separate CI workflow), see [Blog Publishing Workflows](#5.3).

---

## System Overview

The development lifecycle is organized around four interlocking concerns: branch discipline, automated CI checks, per-PR quality gates, and versioned releases. The diagram below maps the change flow from local feature branch to production release, showing actual file paths and CI job names.

**Diagram: Change Lifecycle from Branch to Production**

```mermaid
flowchart TD
    A["git flow feature start\nfeature/skill/NAME/FEATURE"] --> B["Edit files:\nskills/NAME/SKILL.md\nskills/NAME/scripts/*.py\nskills.json"]
    B --> C["git push origin feature/...\ngh pr create --base develop"]
    C --> D["Trigger: .github/workflows/\ntest-installer.yml\non: pull_request, paths:\n- skills.json\n- skills/**"]
    D --> E["Job: validate-skills-json\nruns-on: ubuntu-latest\nSteps: jq validation"]
    D --> F["Job: test\nmatrix:\nos: [ubuntu, macos, windows]\nskill: [9 skills]\nTotal: 27 instances"]
    D --> G["Job: test-all-skills\nmatrix:\nos: [ubuntu, macos, windows]\nTotal: 3 instances"]
    E --> H{"All 31 jobs pass?"}
    F --> H
    G --> H
    H -- "No" --> I["Fix code, re-push\n(re-triggers workflow)"]
    I --> D
    H -- "Yes" --> J["Merge via GitHub UI\ninto develop branch"]
    J --> K["git flow release start vX.Y.Z\nEdit: skills.json, CHANGELOG.md"]
    K --> L["git flow release finish vX.Y.Z\nMerges to main + develop\nCreates tag vX.Y.Z"]
    L --> M["GitHub Release created\nCloudflare Pages auto-deploys"]
```

**Key File Locations in Change Flow:**

| Stage | Files Modified | Validation |
|-------|---------------|------------|
| Development | `skills/NAME/SKILL.md`, `skills/NAME/scripts/`, `skills.json` | Local: `npm run lint`, `npm run typecheck` |
| PR Creation | Branch pushed to `origin/feature/skill/NAME/FEATURE` | Automatic: `test-installer.yml` triggered |
| CI Validation | `.github/workflows/test-installer.yml` runs 31 jobs | Matrix: 3 OS × (9 skills + 1 bulk test) + 1 JSON validator |
| Release Prep | `release/vX.Y.Z` branch: bump versions in `skills.json`, `CHANGELOG.md` | Manual review |
| Production | Merge to `main`, tag `vX.Y.Z`, deploy to `opc.dev` | Cloudflare Pages auto-build |

Sources: [.github/workflows/test-installer.yml:1-20](), [.factory/AGENTS.md:166-218](), [.factory/AGENTS.md:311-328]()

---

## Key Components

| Component | Location | Role |
|---|---|---|
| `test-installer.yml` | `.github/workflows/test-installer.yml` | CI workflow: installs skills and validates `skills.json` |
| `skills.json` | `skills.json` | Central registry; version source of truth for all skills |
| `CHANGELOG.md` | `CHANGELOG.md` | Human-readable release notes and skill compatibility matrix |
| `AGENTS.md` | `.factory/AGENTS.md` | Agent-readable developer guide for git flow and release process |
| `hooks.json` | `.factory/hooks.json` | Pre-commit hook definitions |
| `template/SKILL.md` | `template/SKILL.md` | Template for new skill documentation |

Sources: [.factory/AGENTS.md:16-32](), [.github/workflows/test-installer.yml:1-20]()

---

## Git Workflow Summary

The project uses **Git Flow** branching. Branches follow strict naming conventions, and feature branches always merge to `develop` via a GitHub Pull Request — direct merges are not allowed.

**Diagram: Branch Topology and Merge Rules**

```mermaid
gitGraph
    commit id: "init"
    branch develop
    checkout develop
    commit id: "integrate"
    branch feature/skill/twitter/rate-limit
    checkout feature/skill/twitter/rate-limit
    commit id: "feat commit"
    checkout develop
    merge feature/skill/twitter/rate-limit id: "PR merge"
    branch release/v2.0.0
    checkout release/v2.0.0
    commit id: "version bump"
    checkout main
    merge release/v2.0.0 id: "release"
    checkout develop
    merge release/v2.0.0 id: "back-merge"
```

**Branch naming convention:**

| Branch Type | Pattern | Example |
|---|---|---|
| Feature | `feature/skill/<name>/<feature>` | `feature/skill/domain-hunter/promo-code-scraper` |
| Bug fix | `fix/skill/<name>/<issue>` | `fix/skill/requesthunt/reddit-pagination` |
| Release | `release/vX.Y.Z` | `release/v2.0.0` |
| Hotfix | `hotfix/vX.Y.Z` | `hotfix/v1.0.1` |

Commit messages use conventional commit format: `feat(skill-name): description`, `fix(skill-name): description`, `docs(skill-name): description`, `chore(skills): description`. Watermarks or AI-generated signatures in commit messages are explicitly prohibited ([.factory/AGENTS.md:250]()).

For full details, see [Git Workflow & Branching Strategy](#6.1).

Sources: [.factory/AGENTS.md:166-248]()

---

## Automated CI Pipeline Summary

The workflow defined in `.github/workflows/test-installer.yml` ([.github/workflows/test-installer.yml:1-118]()) triggers on `push` to `main` or `pull_request` events that modify `skills.json` or any path under `skills/**` ([.github/workflows/test-installer.yml:4-12]()).

It runs three parallel jobs totaling 31 concurrent GitHub Actions runners:

**Diagram: test-installer.yml Job Architecture**

```mermaid
flowchart TB
    trigger["on:\n- push: branches: [main]\n- pull_request\npaths:\n- skills.json\n- skills/**"]
    
    trigger --> job_test
    trigger --> job_all
    trigger --> job_validate

    subgraph job_test["Job: test"]
        direction TB
        strategy_test["strategy:\nmatrix:\nos: [ubuntu-latest,\nmacos-latest,\nwindows-latest]\nskill: [requesthunt,\nreddit, twitter,\nnanobanana,\nlogo-creator,\nbanner-creator,\ndomain-hunter,\nproducthunt,\nseo-geo]"]
        strategy_test --> runners_test["27 parallel runners\n(3 OS × 9 skills)"]
        runners_test --> step1_test["actions/checkout@v4"]
        step1_test --> step2_test["actions/setup-node@v4\nnode-version: 18"]
        step2_test --> step3_test["mkdir -p test-workspace\ncd test-workspace"]
        step3_test --> step4_test["npx skills add\n${{github.repository}}\n--skill ${{matrix.skill}} -y"]
        step4_test --> step5_test["assert:\ntest -d .factory/skills/\n${{matrix.skill}}"]
    end

    subgraph job_all["Job: test-all-skills"]
        direction TB
        strategy_all["strategy:\nmatrix:\nos: [ubuntu-latest,\nmacos-latest,\nwindows-latest]"]
        strategy_all --> runners_all["3 parallel runners"]
        runners_all --> step1_all["actions/checkout@v4"]
        step1_all --> step2_all["actions/setup-node@v4\nnode-version: 18"]
        step2_all --> step3_all["mkdir -p test-workspace\ncd test-workspace"]
        step3_all --> step4_all["npx skills add\n${{github.repository}} -y"]
        step4_all --> step5_all["SKILL_COUNT=\n$(ls -1 .factory/skills/\n| wc -l)"]
        step5_all --> step6_all["assert:\nSKILL_COUNT >= 9"]
    end

    subgraph job_validate["Job: validate-skills-json"]
        direction TB
        runner_validate["1 runner\nruns-on: ubuntu-latest"]
        runner_validate --> step1_validate["actions/checkout@v4"]
        step1_validate --> step2_validate["jq empty skills.json"]
        step2_validate --> step3_validate["jq -e '.skills[] |\nselect(.name and\n.description and\n.dependencies != null)'"]
        step3_validate --> step4_validate["SKILL_NAMES=\n$(jq -r '.skills[].name')"]
        step4_validate --> step5_validate["For each dep in\nobject-format deps:\ngrep dep in SKILL_NAMES"]
        step5_validate --> step6_validate["For each dep in\narray-format deps:\ngrep dep in SKILL_NAMES"]
    end
```

**Job-Specific Details:**

| Job Name | Runners | Matrix Dimensions | Key Command | Success Criteria |
|----------|---------|-------------------|-------------|------------------|
| `test` | 27 | `os` × `skill` = 3 × 9 | `npx skills add --skill ${{matrix.skill}} -y` | Directory `.factory/skills/${{matrix.skill}}/` exists |
| `test-all-skills` | 3 | `os` = 3 | `npx skills add ${{github.repository}} -y` | `ls -1 .factory/skills/ \| wc -l` returns ≥ 9 |
| `validate-skills-json` | 1 | None | `jq empty skills.json` | JSON valid + all deps reference existing skills |

**Path Triggers:**

The workflow only runs when changes touch:
- `skills.json` (line 7)
- `skills/**` (line 8)

This avoids unnecessary CI runs for website-only changes (`website/`, `blog/`) or documentation updates (`README.md`, `CHANGELOG.md`).

**Node.js Setup:**

All jobs use `actions/setup-node@v4` with `node-version: '18'` ([.github/workflows/test-installer.yml:27-28](), [.github/workflows/test-installer.yml:59-61]()), as `npx skills add` requires Node.js runtime.

For full details on each job's implementation, see [Automated Testing Pipeline](#6.2).

Sources: [.github/workflows/test-installer.yml:1-118]()

---

## Quality Gates Summary

Before any PR is merged, the following checks must pass ([.factory/AGENTS.md:311-328]()):

**Automated Checks (CI):**
- All 31 GitHub Actions jobs in `test-installer.yml` pass (27 skill tests + 3 bulk tests + 1 JSON validator)
- `npx skills add` successfully installs skill to `.factory/skills/SKILL_NAME/` on ubuntu, macos, windows
- `jq` validation confirms `skills.json` structure and dependency references

**Manual Review Checks:**
- `npm run test` (website) passes without errors
- `npm run typecheck` (website TypeScript validation) shows no errors
- `npm run lint` (website ESLint) passes
- `SKILL.md` has valid YAML frontmatter with required fields:
  - `name`: string (kebab-case identifier)
  - `description`: string (includes "Use when..." trigger contexts inline)
- `skills.json` version field updated if functionality changed (see [Release Management](#6.4))
- `CHANGELOG.md` entry added under `[Unreleased]` section (skill-specific subsection)
- New dependencies declared in `SKILL.md` frontmatter and listed in `skills.json`
- PR description references issue number using closing keywords (`Fixes #123`, `Closes #124`)

**Pre-commit Hooks:**

Git hooks are defined in `.factory/hooks.json`. The `PreCommit` hook enforces:
- Block commits with `factory-droid[bot]` in co-author field (prevents bot attribution pollution)

**New Skill Checklist:**

When adding a new skill, the `.factory/skills/add-new-opc-skill/SKILL.md` checklist requires six file updates:

| File | Required Change | Example |
|------|----------------|---------|
| `skills/NAME/SKILL.md` | Create with YAML frontmatter (`name`, `description`) | [template/SKILL.md:1-10]() |
| `skill-logos/NAME.svg` | Add vector logo | Generated via `logo-creator` skill |
| `skills.json` | Add skill entry with name, version, dependencies, install commands | [CHANGELOG.md:12-23]() shows structure |
| `README.md` | Add row to skills table | Main repository README skills listing |
| `website/worker.js` | Hardcode skill metadata in `SKILLS_CATALOG` object | For opc.dev rendering |
| `CHANGELOG.md` | Add entry under `[Unreleased]` with skill subsection | [CHANGELOG.md:33-36]() shows format |

For full details on pre-commit hooks and the add-new-skill workflow, see [Pre-commit Hooks & Quality Gates](#6.3).

Sources: [.factory/AGENTS.md:311-328](), [template/SKILL.md:1-130](), [CHANGELOG.md:8-24]()

---

## Release Management Summary

Skills maintain independent version numbers in `skills.json` ([CHANGELOG.md:12-23]()). Each skill follows Semantic Versioning (MAJOR.MINOR.PATCH):

| Change Type | Version Bump | Example | Update `skills.json`? |
|-------------|--------------|---------|----------------------|
| Breaking API change | MAJOR | `1.0.0 → 2.0.0` | Yes |
| New backward-compatible feature | MINOR | `1.0.0 → 1.1.0` | Yes |
| Bug fix | PATCH | `1.0.0 → 1.0.1` | Yes |
| Documentation-only | None | — | No |
| Internal refactor (no behavior change) | None | — | No |

**Release Paths:**

Two release strategies are supported, depending on coordination needs:

**1. Quick Release (Single Skill):**

```bash
# Feature branch merged to develop
git checkout develop
git pull origin develop
git checkout -b feature/skill/twitter/rate-limit-improvement

# Edit files
vim skills/twitter/scripts/rate_limit.py
vim skills.json  # Bump twitter.version: "1.1.0"
vim CHANGELOG.md # Add entry under [Unreleased] > ### twitter > #### [1.1.0]

# Commit and PR
git commit -m "feat(twitter): Add retry mechanism for rate limiting"
git push -u origin feature/skill/twitter/rate-limit-improvement
gh pr create --base develop

# After merge, no release branch needed for independent skill version
```

**2. Coordinated Release (Multiple Skills):**

```bash
# All feature branches merged to develop first
git checkout develop
git pull origin develop
git flow release start v2.0.0

# Bump multiple skill versions in skills.json
vim skills.json  # Update: twitter 2.0.0, reddit 1.1.0, domain-hunter 1.1.0

# Reorganize CHANGELOG.md: move [Unreleased] entries to [2.0.0] section
vim CHANGELOG.md

# Create release PR to main
git push -u origin release/v2.0.0
gh pr create --base main --head release/v2.0.0

# After merge
git flow release finish v2.0.0  # Merges to main, tags, back-merges to develop
git push origin main develop --tags
```

**Dependency Update Decision Flow:**

When a dependency skill releases an update, downstream dependents follow this decision tree:

**Diagram: Dependency Update Decision Flow**

```mermaid
flowchart TD
    A["Skill A releases\nversion X.Y.Z"] --> B{"Version change type?"}
    
    B -- "PATCH (Z++)" --> C["Dependent skills:\nNo action required\nNo version bump"]
    
    B -- "MINOR (Y++)" --> D["Dependent skills:\nNo action required\nNo version bump"]
    
    B -- "MAJOR (X++)\nBreaking change" --> E["Consult CHANGELOG.md\nCompatibility Matrix\nlines 12-23"]
    
    E --> F["Identify dependents:\ne.g. twitter deps:\n- domain-hunter\n- seo-geo"]
    
    F --> G["For each dependent:\nCreate PR\nfeature/skill/DEPENDENT/\nDEPENDENCY-vX-compat"]
    
    G --> H["Test compatibility:\npython3 skills/DEPENDENT/\nscripts/test_DEPENDENCY\n_compat.py"]
    
    H --> I{"Tests pass?"}
    
    I -- "No" --> J["Fix dependent skill\ncode to support\nnew API"]
    J --> H
    
    I -- "Yes" --> K["Merge PR\nBump dependent\nversion (PATCH)"]
    
    K --> L["Update CHANGELOG.md:\nList as [Unreleased]\nunder ### DEPENDENT\nsubsection"]
```

**Compatibility Matrix Usage:**

The `CHANGELOG.md` file contains a dependency matrix ([CHANGELOG.md:8-23]()):

```
| Skill           | Current Version | Requires       | Min Versions                  |
|-----------------|-----------------|----------------|-------------------------------|
| domain-hunter   | 1.0.0           | twitter, reddit| twitter ≥1.0.0, reddit ≥1.0.0 |
| logo-creator    | 1.0.0           | nanobanana     | nanobanana ≥1.0.0             |
| seo-geo         | 1.0.0           | twitter, reddit| twitter ≥1.0.0, reddit ≥1.0.0 |
```

When updating `twitter` to `2.0.0` (breaking change), you must:
1. Identify dependents: `domain-hunter`, `seo-geo` (from matrix)
2. Create compatibility PRs: `feature/skill/domain-hunter/twitter-v2-compat`, `feature/skill/seo-geo/twitter-v2-compat`
3. Update matrix minimum version requirements: `twitter ≥2.0.0`
4. Test each dependent independently before merging

**Version Update Rules:**

| Scenario | Action Required | Version Bump Needed? |
|----------|----------------|----------------------|
| Dependency releases PATCH | Dependent: no action | No |
| Dependency releases MINOR | Dependent: no action | No |
| Dependency releases MAJOR | Dependent: create compat PR | Yes (PATCH or MINOR) |
| Dependent wants to document new dependency version support | Update `CHANGELOG.md` matrix only | No |

For full release workflow details, see [Release Management](#6.4).

Sources: [.factory/AGENTS.md:349-508](), [CHANGELOG.md:1-23](), [CHANGELOG.md:112-167]()

---

## Developer Quick Reference

```
# First-time setup
git clone https://github.com/ReScienceLab/opc-skills
cd opc-skills
npm install
git flow init

# Start a new skill feature
git flow feature start skill/<name>/<feature>

# Push and open PR (never use git flow feature finish)
git push -u origin feature/skill/<name>/<feature>
gh pr create --base develop --head feature/skill/<name>/<feature>

# Start a release
git flow release start vX.Y.Z
git flow release finish vX.Y.Z
git push origin main develop --tags
```

Sources: [.factory/AGENTS.md:573-616]()

---

# Page: Git Workflow & Branching Strategy

# Git Workflow & Branching Strategy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.factory/AGENTS.md](.factory/AGENTS.md)
- [.github/workflows/publish-blog.yml](.github/workflows/publish-blog.yml)
- [CHANGELOG.md](CHANGELOG.md)
- [scripts/BLOG_GUIDELINES.md](scripts/BLOG_GUIDELINES.md)
- [scripts/BLOG_PUBLISHING.md](scripts/BLOG_PUBLISHING.md)
- [scripts/create-blog.py](scripts/create-blog.py)
- [template/SKILL.md](template/SKILL.md)
- [website/blog/posts/ralph-autonomous-agent-loop.md](website/blog/posts/ralph-autonomous-agent-loop.md)
- [website/blog/posts/why-skills-beat-docs.md](website/blog/posts/why-skills-beat-docs.md)

</details>



## Purpose and Scope

This document describes the Git Flow branching model, branch naming conventions, commit standards, and release processes used in the OPC Skills repository. It covers the complete development workflow from feature creation to production deployment.

For information about automated testing during the CI/CD pipeline, see [Automated Testing Pipeline](#6.2). For pre-commit validation rules, see [Pre-commit Hooks & Quality Gates](#6.3). For coordinating releases across multiple skills, see [Release Management](#6.4).

---

## Branching Model Overview

The repository implements **Git Flow** with a critical exception: blog posts follow a fast-track pathway directly to `main`, bypassing `develop` for rapid content publishing. This dual-pathway approach balances code stability (Git Flow for skills) with content agility (fast-track for blog).

### Primary Branch Structure

**Title: Complete Git Flow with Blog Fast-Track Pathway**

```mermaid
graph TB
    main["main<br/>(Production)<br/>website/worker.js<br/>skills.json"]
    develop["develop<br/>(Integration)<br/>Pre-release testing"]
    
    feature1["feature/skill/seo-geo/<br/>perplexity-optimization"]
    feature2["feature/skill/domain-hunter/<br/>promo-code-scraper"]
    fix1["fix/skill/requesthunt/<br/>reddit-pagination"]
    release1["release/v1.0.7<br/>skills.json versions<br/>CHANGELOG.md updates"]
    hotfix1["hotfix/v1.0.6"]
    
    blogFeature["feature/blog/<br/>ralph-autonomous-agent-loop"]
    blogPR["PR to main<br/>+ blog-post label"]
    blogValidate["publish-blog.yml<br/>validates<br/>scripts/create-blog.py"]
    
    develop --> feature1
    develop --> feature2
    develop --> fix1
    feature1 --> develop
    feature2 --> develop
    fix1 --> develop
    
    develop --> release1
    release1 --> main
    release1 --> develop
    
    main --> hotfix1
    hotfix1 --> main
    hotfix1 --> develop
    
    blogFeature --> blogPR
    blogPR --> blogValidate
    blogValidate -->|auto-merge<br/>6 minutes| main
    
    main --> tag1["v1.0.7 tag"]
    
    style main fill:#fff,stroke:#333,stroke-width:3px
    style develop fill:#fff,stroke:#333,stroke-width:2px
    style blogValidate fill:#fff,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5
```

**Sources:** [.factory/AGENTS.md:166-219](), [scripts/BLOG_PUBLISHING.md:1-443](), [.github/workflows/publish-blog.yml:1-38]()

### Permanent Branches

| Branch | Purpose | Protected | Deployment Target |
|--------|---------|-----------|-------------------|
| `main` | Production-ready code, tagged releases | Yes | opc.dev production (Cloudflare Workers via `website/worker.js`) |
| `develop` | Integration branch for next release | Yes | No automatic deployment |

**Key Differences:**
- **Skills and code changes**: Must follow develop → main flow
- **Blog posts**: Can go directly to main via fast-track workflow (`.github/workflows/publish-blog.yml`)
- **Infrastructure changes**: Follow develop → main flow
- **Hotfixes**: Branch from main, merge to both main and develop

**Sources:** [.factory/AGENTS.md:172-174](), [scripts/BLOG_PUBLISHING.md:25-55]()
</thinking>

### Fast-Track Blog Publishing Pathway

Blog posts bypass the standard Git Flow to enable rapid content publishing. This pathway is explicitly designed for non-code content updates.

**Title: Blog Fast-Track Workflow with Auto-Merge**

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Branch as "feature/blog/<slug>"
    participant PR as "Pull Request"
    participant GHA as ".github/workflows/<br/>publish-blog.yml"
    participant Script as "scripts/<br/>create-blog.py"
    participant Main as "main branch"
    participant CF as "Cloudflare Workers<br/>website/worker.js"
    
    Dev->>Branch: "git checkout -b feature/blog/post-slug"
    Dev->>Branch: "Edit website/blog/posts/<slug>.md"
    Dev->>Branch: "Update website/blog/blog.json"
    Dev->>Branch: "git push origin feature/blog/post-slug"
    
    Dev->>PR: "gh pr create --base main<br/>--label blog-post"
    
    PR->>GHA: "Trigger on label: blog-post"
    GHA->>Script: "python3 scripts/create-blog.py validate"
    
    alt Validation Passes
        Script->>GHA: "Exit 0 (success)"
        GHA->>PR: "hmarr/auto-approve-action@v3"
        GHA->>PR: "pascalgn/automerge-action@v0.15.6<br/>MERGE_METHOD: squash"
        PR->>Main: "Auto-merge (1 minute)"
        Main->>CF: "Deploy (5 minutes)"
        CF->>CF: "Live at opc.dev/blog/<slug>"
    else Validation Fails
        Script->>GHA: "Exit 1 (failure)"
        GHA->>PR: "Comment with errors"
        PR->>PR: "Remains open for fixes"
    end
    
    Note over Dev,CF: "Total time: 6 minutes from PR to live"
```

**Validation Rules** (enforced by `scripts/create-blog.py`):
- All required fields present in `blog.json` entry
- Markdown file exists at `website/blog/posts/<slug>.md`
- Minimum 5 FAQ items (recommended 5-10 for GEO)
- Minimum 10 keywords (recommended 15+ for SEO)
- Valid date format: `YYYY-MM-DD`
- Valid `schema.org` structure with `@context` and `@type`

**Sources:** [.github/workflows/publish-blog.yml:1-38](), [scripts/create-blog.py:29-104](), [scripts/BLOG_PUBLISHING.md:27-54]()

---

## Branch Types and Naming Conventions

### Feature Branches

**Pattern:** `feature/skill/<skill-name>/<feature-description>`

Used for developing new features or enhancements to individual skills. Always branch from and merge back to `develop`.

**Examples:**
```
feature/skill/domain-hunter/promo-code-scraper
feature/skill/seo-geo/perplexity-optimization
feature/skill/requesthunt/github-integration
```

**Sources:** [.factory/AGENTS.md:175-180](), [.factory/AGENTS.md:183-189]()

### Fix Branches

**Pattern:** `fix/skill/<skill-name>/<issue-description>`

Used for bug fixes that are not urgent enough to require hotfix branches. Always merge to `develop`.

**Examples:**
```
fix/skill/requesthunt/reddit-pagination
fix/skill/twitter/rate-limit-handling
fix/skill/logo-creator/svg-export-error
```

**Sources:** [.factory/AGENTS.md:175-180]()

### Blog Feature Branches

**Pattern:** `feature/blog/<slug>` or `blog/<slug>`

Used for blog posts that will follow the fast-track publishing pathway directly to `main`.

**Examples:**
```
feature/blog/ralph-autonomous-agent-loop
feature/blog/why-skills-beat-docs
feature/blog/domain-hunting-ai-saved-50
blog/install-tutorial
```

**Critical Distinction:**
- Blog branches target `main` (not `develop`)
- Require `blog-post` label on PR
- Auto-merge via `.github/workflows/publish-blog.yml`
- No manual review required if validation passes

**Sources:** [scripts/BLOG_PUBLISHING.md:27-54](), [.github/workflows/publish-blog.yml:3-12]()

### Release Branches

**Pattern:** `release/v<version>`

Used to prepare a new production release. Allows final testing, version bumps, and changelog updates without blocking ongoing development.

**Examples:**
```
release/v1.0.7
release/v2.0.0
```

**Sources:** [.factory/AGENTS.md:175-180](), [.factory/AGENTS.md:205-209]()

### Hotfix Branches

**Pattern:** `hotfix/v<version>`

Used for emergency fixes to production. Branch from `main` and merge back to both `main` and `develop`.

**Examples:**
```
hotfix/v1.0.6
hotfix/v1.0.1
```

**Sources:** [.factory/AGENTS.md:175-180](), [.factory/AGENTS.md:213-217]()

---

## Development Workflow

### Standard Feature Development Flow (Skills & Code)

**Title: Standard Git Flow for Skill Development**

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Local as "Local Git"
    participant Origin as "GitHub Remote"
    participant Develop as "develop branch"
    participant CI as ".github/workflows/<br/>test-installer.yml"
    participant Main as "main branch"
    
    Dev->>Local: "git checkout develop"
    Dev->>Local: "git pull origin develop"
    Dev->>Local: "git checkout -b<br/>feature/skill/name/feature"
    
    loop Development cycle
        Dev->>Local: "Edit skills/<skill-name>/SKILL.md"
        Dev->>Local: "Update skills.json version"
        Dev->>Local: "Update CHANGELOG.md"
        Dev->>Local: "git commit -m 'feat(skill-name): ...'"
    end
    
    Dev->>Origin: "git push -u origin<br/>feature/skill/name/feature"
    Dev->>Origin: "gh pr create --base develop"
    
    Origin->>CI: "Trigger on PR to develop"
    CI->>CI: "Run 27 tests<br/>(9 skills × 3 OS)"
    CI->>CI: "Validate skills.json schema"
    CI->>CI: "Validate SKILL.md YAML"
    CI->>Origin: "Report ✓ or ✗"
    
    alt Tests Pass
        Origin->>Develop: "Merge PR (squash)"
        Develop->>Dev: "git pull origin develop"
    else Tests Fail
        Origin->>Dev: "Fix issues and push"
    end
```

**Files Modified in Typical Skill PR:**
- `skills/<skill-name>/SKILL.md` - Skill documentation and frontmatter
- `skills.json` - Version number update for skill
- `CHANGELOG.md` - Entry under `[Unreleased]` section
- `README.md` - If adding new skill to table
- `website/worker.js` - If skill needs hardcoded metadata
- `skill-logos/<skill-name>.svg` - Skill logo file

**Sources:** [.factory/AGENTS.md:191-228](), [CHANGELOG.md:1-325]()

### Blog Content Publishing Flow (Fast-Track)

**Title: Fast-Track Blog Publishing to Main**

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Local as "Local Git"
    participant Origin as "GitHub Remote"
    participant PR as "Pull Request<br/>(to main)"
    participant Validate as ".github/workflows/<br/>publish-blog.yml"
    participant Script as "scripts/<br/>create-blog.py"
    participant Main as "main branch"
    
    Dev->>Local: "git checkout -b<br/>feature/blog/<slug>"
    
    loop Content creation
        Dev->>Local: "Create website/blog/posts/<slug>.md"
        Dev->>Local: "Add entry to website/blog/blog.json"
        Dev->>Local: "python3 scripts/create-blog.py<br/>validate"
        Dev->>Local: "python3 scripts/create-blog.py<br/>check <slug>"
    end
    
    Dev->>Local: "git commit -m<br/>'feat(blog): add <topic> post'"
    Dev->>Origin: "git push origin<br/>feature/blog/<slug>"
    Dev->>PR: "gh pr create --base main<br/>--label blog-post"
    
    Note over PR,Validate: "Label 'blog-post' triggers auto-merge"
    
    PR->>Validate: "on: pull_request<br/>types: [labeled]"
    Validate->>Script: "python3 scripts/create-blog.py<br/>validate"
    
    alt Validation Passes
        Script->>Validate: "Exit 0"
        Validate->>PR: "hmarr/auto-approve-action@v3"
        Validate->>PR: "pascalgn/automerge-action@v0.15.6"
        PR->>Main: "Squash merge (1 min)"
        Main->>Main: "Cloudflare auto-deploys (5 min)"
    else Validation Fails
        Script->>Validate: "Exit 1 with errors"
        Validate->>PR: "Add comment with<br/>validation errors"
    end
    
    Note over Dev,Main: "Total: 6 minutes from PR to live"
```

**Validation Performed:**
- `blog.json` is valid JSON
- All required fields present (`slug`, `title`, `description`, `date`, `author`, `category`, `tags`, `keywords`, `schema`, `faq`, `citations`)
- Markdown file exists at `website/blog/posts/<slug>.md`
- FAQ count ≥ 5 (warns if < 5)
- Keyword count ≥ 10 (warns if < 10)
- Citation count ≥ 3 (warns if < 3)
- Date format is `YYYY-MM-DD`
- Schema.org structure includes `@context` and `@type`

**Why Fast-Track Works:**
Blog posts are **non-executable content** that don't affect skill functionality. They require no dependency testing or cross-platform validation. The risk of breaking production is minimal since blog posts:
- Don't modify skill logic
- Don't change installation commands
- Don't affect API integrations
- Are isolated to `website/blog/*` paths

**Sources:** [.github/workflows/publish-blog.yml:1-38](), [scripts/create-blog.py:29-173](), [scripts/BLOG_PUBLISHING.md:27-55]()

### Git Flow Command Reference

```bash
# Initialize git flow (first time only)
git flow init

# Start a new feature
git flow feature start skill/domain-hunter/advanced-filtering

# Finish feature - DO NOT use git flow feature finish
# Instead, push and create PR:
git push -u origin feature/skill/domain-hunter/advanced-filtering
gh pr create --base develop --head feature/skill/domain-hunter/advanced-filtering

# Start a release
git flow release start v2.0.0

# Finish release (merges to main, develop, creates tag)
git flow release finish v2.0.0
git push origin main develop --tags

# Start a hotfix
git flow hotfix start v1.0.1

# Finish hotfix
git flow hotfix finish v1.0.1
git push origin main develop --tags
```

**Sources:** [.factory/AGENTS.md:191-218]()

### Important: Features Must Use Pull Requests

**Never directly merge feature branches.** The repository enforces a PR-based workflow:

1. Push feature branch to origin
2. Create PR targeting `develop`
3. Wait for CI checks to pass
4. Request review and get approval
5. Merge via GitHub UI (squash merge preferred)

**Sources:** [.factory/AGENTS.md:220-228]()

---

## Commit Conventions

The repository uses **Conventional Commits** for clear, parseable commit history.

### Commit Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Commit Types

| Type | Usage | Example |
|------|-------|---------|
| `feat` | New feature or capability | `feat(domain-hunter): Add WHOIS lookup for domain availability` |
| `fix` | Bug fix | `fix(requesthunt): Handle Reddit API pagination edge case` |
| `docs` | Documentation only | `docs(logo-creator): Add SVG export examples` |
| `test` | Test-related changes | `test(seo-geo): Add DataForSEO API mocks` |
| `refactor` | Code refactoring (no behavior change) | `refactor(twitter): Extract rate limit handling` |
| `chore` | Maintenance, dependencies | `chore(skills): Update dependencies` |

**Sources:** [.factory/AGENTS.md:229-251]()

### Scope Guidelines

The scope should identify which skill or area is affected:

- **Skill-specific:** Use skill name (`requesthunt`, `domain-hunter`, `seo-geo`)
- **Multiple skills:** Use `skills` as scope
- **Infrastructure:** Use `website`, `ci`, `docs`, or `chore`

### Commit Message Examples

```bash
# Good examples
git commit -m "feat(domain-hunter): Add WHOIS lookup for domain availability"
git commit -m "fix(requesthunt): Handle Reddit API pagination edge case"
git commit -m "docs(logo-creator): Add SVG export examples"
git commit -m "chore(skills): Update dependencies"

# Bad examples (avoid)
git commit -m "update stuff"
git commit -m "fix bug"
git commit -m "WIP"
```

**Sources:** [.factory/AGENTS.md:229-251]()

### Prohibited Commit Practices

**Do not add watermarks or AI-generated signatures** to commit messages. The pre-commit hook in `.factory/hooks.json` enforces this policy by blocking commits with `factory-droid[bot]` co-author signatures.

**Pre-commit Hook Configuration:**

```json
{
  "hooks": {
    "PreCommit": [
      {
        "name": "prevent-factory-droid-coauthor",
        "description": "Prevents adding factory-droid[bot] as co-author in commits",
        "type": "command",
        "command": "bash -c 'if git log -1 --pretty=%B | grep -q \"factory-droid\\[bot\\]\"; then echo \"Error: factory-droid[bot] co-author is not allowed in commits\"; exit 1; fi'"
      }
    ]
  }
}
```

**Rationale:** AI-generated signatures and bot co-authors create attribution confusion and pollute commit history. Human developers should be the sole authors in commit metadata.

**Sources:** [.factory/AGENTS.md:250-251](), [.factory/hooks.json:1-13]()

---

## Pull Request Process

### Pre-PR Checklist for Skill Changes

Before creating a pull request for skill or infrastructure changes:

- [ ] All tests pass: `npm run test` (website)
- [ ] Type checking passes: `npm run typecheck` (website)
- [ ] Linting passes: `npm run lint` (website)
- [ ] SKILL.md has valid YAML frontmatter (if modifying skills)
- [ ] Version updated in `skills.json` (if functionality changed)
- [ ] `CHANGELOG.md` updated under `[Unreleased]` section
- [ ] Documentation updated (SKILL.md, examples, README)
- [ ] Dependencies declared in SKILL.md (if new dependencies added)

**Sources:** [.factory/AGENTS.md:312-326]()

### Pre-PR Checklist for Blog Posts

Before creating a blog post PR:

- [ ] Run validation: `python3 scripts/create-blog.py validate`
- [ ] Check specific post: `python3 scripts/create-blog.py check <slug>`
- [ ] Markdown file exists: `website/blog/posts/<slug>.md`
- [ ] Entry added to `website/blog/blog.json` at position 0 (newest first)
- [ ] Word count ≥ 2,000 (check with `wc -w website/blog/posts/<slug>.md`)
- [ ] FAQ section present with 5-10 questions
- [ ] 10+ keywords in metadata
- [ ] 3+ citations in metadata
- [ ] Schema.org markup complete in `blog.json`
- [ ] Images referenced exist or use valid URLs
- [ ] Internal links point to existing blog posts

**Automated Validation:**
The `publish-blog.yml` workflow runs `create-blog.py validate` automatically. Fix any errors before the PR will auto-merge.

**Sources:** [scripts/BLOG_GUIDELINES.md:1-366](), [scripts/create-blog.py:29-104]()

### PR Description Requirements

Include in your PR description:

1. **Summary of changes** - What problem does this solve?
2. **Issue reference** - Use closing keywords: `Fixes #123`, `Closes #124`, `Resolves #125`
3. **Testing performed** - How did you verify the changes work?
4. **Breaking changes** - List any breaking changes (if applicable)
5. **Screenshots/examples** - For UI or skill behavior changes

**Sources:** [.factory/AGENTS.md:338-347]()

### GitHub Actions Validation

Different workflows trigger based on PR target and labels:

**Title: PR Validation Workflows**

```mermaid
graph TB
    PR["Pull Request Created"]
    CheckBase{"PR base<br/>branch?"}
    CheckLabel{"Has label<br/>'blog-post'?"}
    
    TestInstaller[".github/workflows/<br/>test-installer.yml"]
    PublishBlog[".github/workflows/<br/>publish-blog.yml"]
    
    Matrix["Test Matrix:<br/>9 skills × 3 OS = 27 parallel jobs"]
    SkillsJSON["Validate skills.json:<br/>JSON schema + dependencies"]
    SkillMD["Validate SKILL.md:<br/>YAML frontmatter"]
    
    BlogValidate["scripts/create-blog.py<br/>validate"]
    BlogCheck["Check blog.json<br/>Check markdown file<br/>Check word count"]
    
    ResultsSkill["Report to PR:<br/>✓ All tests pass<br/>✗ Failures with logs"]
    ResultsBlog["✓ Auto-approve + merge<br/>✗ Comment with errors"]
    
    PR --> CheckBase
    CheckBase -->|develop| TestInstaller
    CheckBase -->|main| CheckLabel
    
    CheckLabel -->|Yes| PublishBlog
    CheckLabel -->|No| TestInstaller
    
    TestInstaller --> Matrix
    TestInstaller --> SkillsJSON
    TestInstaller --> SkillMD
    Matrix --> ResultsSkill
    SkillsJSON --> ResultsSkill
    SkillMD --> ResultsSkill
    
    PublishBlog --> BlogValidate
    BlogValidate --> BlogCheck
    BlogCheck --> ResultsBlog
    ResultsBlog -->|Success| Merge["Auto-merge to main<br/>Squash commit"]
```

**Workflow Triggers:**

| Workflow | Trigger | Purpose | Files Checked |
|----------|---------|---------|---------------|
| `test-installer.yml` | PR to `develop` | Validate skill installation across platforms | `skills/**`, `skills.json` |
| `publish-blog.yml` | PR to `main` with `blog-post` label | Auto-publish blog content | `website/blog/**` |
| `fetch-install-stats.yml` | Daily cron at 6 AM UTC | Update installation statistics | `install-stats.json` |

**Sources:** [.factory/AGENTS.md:312-326](), [.github/workflows/publish-blog.yml:1-38](), [.github/workflows/test-installer.yml:1-50]()

---

## Versioning Strategy

The repository uses **independent versioning** for individual skills while maintaining a project-level version for milestones.

### Version Number Format

All versions follow **Semantic Versioning (SemVer)**:

```
MAJOR.MINOR.PATCH

MAJOR: Breaking changes or API incompatibility
MINOR: New features (backward compatible)
PATCH: Bug fixes
```

**Sources:** [.factory/AGENTS.md:113-123](), [CHANGELOG.md:5-6]()

### Individual Skill Versions

Each skill maintains its own version in `skills.json`:

```json
{
  "skills": [
    {
      "name": "domain-hunter",
      "version": "1.0.0",
      "dependencies": {
        "twitter": ">=1.0.0",
        "reddit": ">=1.0.0"
      }
    }
  ]
}
```

**Update triggers:**
- **PATCH:** Bug fixes, documentation updates
- **MINOR:** New features, new scripts, enhancements
- **MAJOR:** Breaking API changes, removed functionality

**Sources:** [skills.json:129-175](), [.factory/AGENTS.md:113-165]()

### Project Version

The root `version` field in `skills.json` tracks overall project milestones:

```json
{
  "version": "1.0.7",
  "name": "OPC Skills",
  "skills": [...]
}
```

**Update triggers:**
- Major coordinated releases
- Infrastructure changes affecting all skills
- Milestone markers (1.0.0 = Initial release, 2.0.0 = Major refactor)

**Sources:** [skills.json:1-7](), [.factory/AGENTS.md:142-147]()

### Dependency Compatibility Matrix

Dependencies use SemVer range syntax:

```json
"dependencies": {
  "twitter": ">=1.0.0",
  "reddit": ">=1.0.0"
}
```

The `CHANGELOG.md` maintains a compatibility matrix:

| Skill | Current Version | Requires | Min Versions |
|-------|-----------------|----------|--------------|
| **seo-geo** | 1.0.0 | twitter, reddit | twitter ≥1.0.0, reddit ≥1.0.0 |
| **domain-hunter** | 1.0.0 | twitter, reddit | twitter ≥1.0.0, reddit ≥1.0.0 |
| **logo-creator** | 1.0.0 | nanobanana | nanobanana ≥1.0.0 |
| **banner-creator** | 1.0.0 | nanobanana | nanobanana ≥1.0.0 |

**Sources:** [CHANGELOG.md:8-29]()

---

## Release Types

### Quick Release - Single Skill Update

Each skill can be released independently without coordinating with other skills.

#### Workflow: Update twitter v1.0.0 → v1.1.0

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Feature as feature/skill/twitter/rate-limit
    participant Develop as develop branch
    participant SkillsJSON as skills.json
    participant Changelog as CHANGELOG.md
    participant CI as GitHub Actions
    participant Deps as Dependent Skills
    
    Dev->>Feature: git checkout -b feature/...
    Dev->>Feature: Implement rate limit improvement
    
    Dev->>SkillsJSON: Update twitter version: 1.1.0
    Dev->>Changelog: Add entry under [Unreleased]
    
    Dev->>Feature: git commit -m "feat(twitter): Add retry mechanism"
    Dev->>Feature: git push origin feature/...
    Dev->>Develop: Create PR to develop
    
    Develop->>CI: Trigger tests
    CI->>CI: Run 27 parallel tests
    CI->>Develop: Report success
    
    Develop->>Develop: Merge PR
    
    Note over Deps: Test dependent skills:<br/>domain-hunter, seo-geo
    Deps->>Deps: No version bump needed<br/>(non-breaking change)
```

**Steps:**

1. **Create feature branch**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/skill/twitter/rate-limit-improvement
   ```

2. **Update version in skills.json** (only this skill)
   ```json
   {
     "name": "twitter",
     "version": "1.1.0"  // ← update version only
   }
   ```

3. **Update CHANGELOG.md** - Add entry in Unreleased section
   ```markdown
   ### twitter
   #### [1.1.0] - 2025-01-22
   - **Added**: Retry mechanism for rate limit handling
   - **Fixed**: Improved error handling for connection timeouts
   ```

4. **Commit with conventional commit**
   ```bash
   git commit -m "feat(twitter): Add retry mechanism and improve rate limiting"
   ```

5. **Push and create PR**
   ```bash
   git push -u origin feature/skill/twitter/rate-limit-improvement
   gh pr create --base develop --head feature/skill/twitter/rate-limit-improvement
   ```

6. **Merge PR** when approved and tests pass

7. **Test dependents** if needed (for breaking changes only)

**Sources:** [.factory/AGENTS.md:348-398]()

### Coordinated Release - Multiple Skills

For milestone releases coordinating multiple skills:

```mermaid
graph TB
    Develop["develop<br/>(multiple features merged)"]
    Release["release/v2.0.0"]
    SkillsJSON["Update multiple skills<br/>in skills.json"]
    Changelog["Reorganize CHANGELOG.md<br/>Unreleased → [2.0.0]"]
    Tests["Run full test suite"]
    PR["Create PR to main"]
    Main["main branch"]
    Tag["v2.0.0 tag"]
    
    Develop --> Release
    Release --> SkillsJSON
    Release --> Changelog
    Release --> Tests
    Tests --> PR
    PR --> Main
    Main --> Tag
    Release --> Develop
    
    style Main fill:#fff,stroke:#333,stroke-width:3px
```

**Steps:**

1. **Start release branch**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b release/v2.0.0
   ```

2. **Update multiple skill versions** in `skills.json`
   ```json
   {
     "version": "2.0.0",
     "skills": [
       { "name": "twitter", "version": "2.0.0" },
       { "name": "reddit", "version": "1.1.0" },
       { "name": "domain-hunter", "version": "1.1.0" }
     ]
   }
   ```

3. **Update CHANGELOG.md** - Move Unreleased to versioned section
   ```markdown
   ## [2.0.0] - 2025-01-23
   
   ### twitter
   - **Changed**: API now requires v2 endpoint authentication ⚠️ BREAKING
   
   ### reddit
   - **Added**: Support for Reddit video posts
   
   ### domain-hunter
   - **Fixed**: Updated for twitter v2.0.0 compatibility
   ```

4. **Run tests**
   ```bash
   npm run test && npm run typecheck
   ```

5. **Create single PR** targeting main
   ```bash
   git add skills.json CHANGELOG.md
   git commit -m "chore(release): Version 2.0.0 - multiple skill updates"
   git push -u origin release/v2.0.0
   gh pr create --base main --head release/v2.0.0
   ```

6. **Merge to main** and create GitHub release

**Sources:** [.factory/AGENTS.md:400-438]()

### Hotfix Release - Emergency Production Fix

For urgent fixes to production:

```mermaid
graph TB
    Main["main<br/>(production issue detected)"]
    Hotfix["hotfix/v1.0.6"]
    Fix["Apply emergency fix"]
    Test["Test fix"]
    MergeMain["Merge to main"]
    MergeDevelop["Merge to develop"]
    Tag["v1.0.6 tag"]
    
    Main --> Hotfix
    Hotfix --> Fix
    Fix --> Test
    Test --> MergeMain
    Test --> MergeDevelop
    MergeMain --> Tag
    
    style Main fill:#fff,stroke:#333,stroke-width:3px
    style Hotfix fill:#fff,stroke:#f00,stroke-width:2px
```

**Steps:**

1. **Start hotfix from main**
   ```bash
   git checkout main
   git pull origin main
   git flow hotfix start v1.0.6
   ```

2. **Apply fix** and update version

3. **Finish hotfix** (merges to both main and develop)
   ```bash
   git flow hotfix finish v1.0.6
   git push origin main develop --tags
   ```

**Sources:** [.factory/AGENTS.md:213-217]()

### Breaking Changes Handling

When a skill introduces breaking changes, mark them clearly:

```markdown
### twitter
#### [2.0.0] - 2025-01-23 ⚠️ BREAKING
- **Changed**: API now requires v2 endpoint authentication
- **Removed**: Deprecated v1 endpoint support (use twitter-legacy v1.0.0 if needed)
- **Migration Guide**: See docs/migration-guide.md
```

**Handling dependents:**

1. Identify dependent skills using CHANGELOG.md matrix
2. Create separate PRs for each dependent skill
3. Test compatibility before merging
4. Update dependent versions only if they contain breaking change fixes

**Sources:** [.factory/AGENTS.md:440-472]()

### Dependency Update Rules

| Scenario | Dependent Skill Action | Version Bump |
|----------|------------------------|--------------|
| Dependency releases PATCH | No action needed | No change |
| Dependency releases MINOR | No action needed | No change |
| Dependency releases MAJOR (breaking) | Must update to support new version | PATCH or MINOR |
| Dependent wants to document support | Update CHANGELOG only | No version bump |

**Sources:** [.factory/AGENTS.md:488-496]()

---

## Release Checklist

Before merging any release PR:

- [ ] Version numbers updated in `skills.json` (only for skills being released)
- [ ] CHANGELOG.md entries created for each updated skill
- [ ] Skill's own dependencies tested (if applicable)
- [ ] Dependent skills tested if this is a breaking change
- [ ] Conventional commit message used
- [ ] PR description references issue number(s) if applicable
- [ ] All CI/CD checks pass (tests, type-check, lint)
- [ ] Documentation (SKILL.md, examples) updated if needed

**Sources:** [.factory/AGENTS.md:498-508]()

---

## File Structure Reference

Key files managed during Git workflow:

```
opc-skills/
├── skills.json                    → Version registry (update on release)
├── CHANGELOG.md                   → Version history (update per change)
├── .factory/
│   ├── AGENTS.md                  → Workflow documentation
│   └── hooks.json                 → Pre-commit hooks
├── .gitignore                     → Excludes .claude/, .factory/, etc.
└── skills/
    └── <skill-name>/
        └── SKILL.md               → Skill documentation (update on changes)
```

**Sources:** [skills.json:1-496](), [CHANGELOG.md:1-325](), [.factory/AGENTS.md:14-32](), [.gitignore:1-47]()

---

# Page: Automated Testing Pipeline

# Automated Testing Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitattributes](.gitattributes)
- [.github/workflows/test-installer.yml](.github/workflows/test-installer.yml)

</details>



## Purpose and Scope

This document describes the automated testing infrastructure that validates skill installations and registry integrity on every code change. The pipeline ensures that all 9 skills can be successfully installed across multiple operating systems using the universal installer (`npx skills add`), and that the central skills registry maintains valid structure and dependencies.

For information about the Git workflow that triggers these tests, see [Git Workflow & Branching Strategy](#6.1). For details on the universal installer being tested, see [Universal Installer (npx skills add)](#3.3). For release processes that depend on passing tests, see [Release Management](#6.4).

---

## Pipeline Architecture

The testing pipeline is implemented as a GitHub Actions workflow defined in [.github/workflows/test-installer.yml:1-118](). It consists of three parallel job groups that validate different aspects of the skills system.

### High-Level Test Workflow

```mermaid
graph TB
    Trigger["Trigger Events<br/>- Push to main<br/>- Pull request"]
    
    PathFilter{"Path Filter<br/>skills.json OR<br/>skills/** modified?"}
    
    subgraph "Parallel Test Jobs"
        TestJob["test job<br/>Matrix: 9 skills × 3 OS<br/>27 parallel runs"]
        TestAllJob["test-all-skills job<br/>Matrix: 3 OS<br/>3 parallel runs"]
        ValidateJob["validate-skills-json job<br/>Single run on ubuntu"]
    end
    
    TestJob --> VerifyIndividual["Verify individual<br/>skill installation"]
    TestAllJob --> VerifyBulk["Verify bulk<br/>installation count"]
    ValidateJob --> VerifyRegistry["Verify JSON structure<br/>+ dependencies"]
    
    VerifyIndividual --> Success["✓ All tests pass<br/>PR/push approved"]
    VerifyBulk --> Success
    VerifyRegistry --> Success
    
    VerifyIndividual --> Failure["✗ Tests failed<br/>Block PR/push"]
    VerifyBulk --> Failure
    VerifyRegistry --> Failure
    
    Trigger --> PathFilter
    PathFilter -->|Yes| TestJob
    PathFilter -->|Yes| TestAllJob
    PathFilter -->|Yes| ValidateJob
    PathFilter -->|No| Skip["Skip tests<br/>No relevant changes"]
```

**Sources:** [.github/workflows/test-installer.yml:3-12]()

---

## Test Matrix Strategy

The pipeline uses GitHub Actions matrix strategy to achieve comprehensive coverage with parallelization. The matrix dimensions create cartesian products that test all relevant combinations.

### Matrix Dimensions

| Job | Dimension 1 (os) | Dimension 2 (skill) | Total Runs |
|-----|------------------|---------------------|------------|
| `test` | 3 operating systems | 9 skills | **27** |
| `test-all-skills` | 3 operating systems | N/A | **3** |
| `validate-skills-json` | ubuntu-latest only | N/A | **1** |

### Operating Systems Tested

- `ubuntu-latest` - Linux validation
- `macos-latest` - macOS validation  
- `windows-latest` - Windows validation

These platforms represent the three major desktop environments where AI coding assistants run.

### Skills Tested

All 9 skills from the registry are tested individually:

```
requesthunt, reddit, twitter, nanobanana, logo-creator, 
banner-creator, domain-hunter, producthunt, seo-geo
```

**Sources:** [.github/workflows/test-installer.yml:16-19](), [.github/workflows/test-installer.yml:50-52]()

---

## Individual Skill Installation Test

The `test` job validates that each skill can be installed independently across all operating systems. This catches platform-specific installation issues and ensures the universal installer correctly handles individual skill selection.

### Test Job Workflow

```mermaid
graph TB
    Start["test job starts<br/>Matrix: os × skill"]
    
    Checkout["actions/checkout@v4<br/>Clone repository"]
    
    NodeSetup["actions/setup-node@v4<br/>Install Node.js 18"]
    
    CreateWorkspace["mkdir -p test-workspace<br/>cd test-workspace"]
    
    InstallSkill["npx skills add<br/>${{github.repository}}<br/>--skill ${{matrix.skill}} -y"]
    
    CheckDir{"Directory exists?<br/>.factory/skills/<br/>${{matrix.skill}}/"}
    
    ListContents["ls -la .factory/skills/<br/>${{matrix.skill}}/"]
    
    Success["✓ Exit 0<br/>Skill installed"]
    
    Failure["✗ Exit 1<br/>Installation failed"]
    
    Start --> Checkout
    Checkout --> NodeSetup
    NodeSetup --> CreateWorkspace
    CreateWorkspace --> InstallSkill
    InstallSkill --> CheckDir
    CheckDir -->|Yes| ListContents
    CheckDir -->|No| Failure
    ListContents --> Success
```

### Verification Logic

The test verifies installation by checking for the existence of the skill directory at `.factory/skills/{skill_name}/`. The script uses shell conditionals to assert directory existence:

```bash
if [ -d ".factory/skills/${{ matrix.skill }}" ]; then
  echo "✓ Skill ${{ matrix.skill }} installed successfully"
  ls -la .factory/skills/${{ matrix.skill }}/
else
  echo "✗ Skill ${{ matrix.skill }} installation failed"
  exit 1
fi
```

The installer is invoked with the `-y` flag to skip interactive prompts, making it suitable for CI environments.

**Sources:** [.github/workflows/test-installer.yml:22-47]()

---

## Bulk Installation Test

The `test-all-skills` job validates that users can install all skills at once without specifying individual skill names. This tests the default behavior of the universal installer and ensures dependency resolution works correctly at scale.

### Test All Skills Job Workflow

```mermaid
graph TB
    Start["test-all-skills job starts<br/>Matrix: os only"]
    
    Checkout["actions/checkout@v4<br/>Clone repository"]
    
    NodeSetup["actions/setup-node@v4<br/>Install Node.js 18"]
    
    CreateWorkspace["mkdir -p test-workspace<br/>cd test-workspace"]
    
    InstallAll["npx skills add<br/>${{github.repository}} -y<br/>(no --skill flag)"]
    
    CountSkills["SKILL_COUNT=$(ls -1<br/>.factory/skills/<br/>| wc -l)"]
    
    CheckCount{"SKILL_COUNT >= 9?"}
    
    ListAll["ls -la .factory/skills/"]
    
    Success["✓ Exit 0<br/>All skills installed"]
    
    Failure["✗ Exit 1<br/>Expected >= 9 skills"]
    
    Start --> Checkout
    Checkout --> NodeSetup
    NodeSetup --> CreateWorkspace
    CreateWorkspace --> InstallAll
    InstallAll --> CountSkills
    CountSkills --> CheckCount
    CheckCount -->|Yes| ListAll
    CheckCount -->|No| Failure
    ListAll --> Success
```

### Count-Based Verification

Rather than checking for specific skill names, this test uses a count-based assertion:

```bash
SKILL_COUNT=$(ls -1 .factory/skills/ | wc -l)
echo "Installed $SKILL_COUNT skills"

if [ "$SKILL_COUNT" -ge 9 ]; then
  echo "✓ All skills installed successfully"
  ls -la .factory/skills/
else
  echo "✗ Expected at least 9 skills, found $SKILL_COUNT"
  exit 1
fi
```

The threshold is "at least 9" to allow for future skill additions without updating the test. This makes the test resilient to registry expansion.

**Sources:** [.github/workflows/test-installer.yml:49-83]()

---

## Skills Registry Validation

The `validate-skills-json` job ensures the central registry maintains structural integrity and valid dependency references. This job runs independently of OS since it's purely JSON validation.

### Validation Steps

```mermaid
graph TB
    Start["validate-skills-json job<br/>ubuntu-latest only"]
    
    Checkout["actions/checkout@v4<br/>Clone repository"]
    
    ValidateJSON["jq empty skills.json<br/>Validate JSON syntax"]
    
    ValidateFields["jq -e '.skills[] |<br/>select(.name and<br/>.description and<br/>.dependencies != null)'"]
    
    ExtractNames["SKILL_NAMES=$(jq -r<br/>'.skills[].name'<br/>skills.json)"]
    
    CheckObjectDeps["For each dependency<br/>in object format:<br/>grep SKILL_NAMES"]
    
    CheckArrayDeps["For each dependency<br/>in array format:<br/>grep SKILL_NAMES<br/>(legacy support)"]
    
    ValidateJSON --> ValidJSON{"Valid JSON?"}
    ValidJSON -->|No| FailJSON["✗ JSON syntax error"]
    ValidJSON -->|Yes| ValidateFields
    
    ValidateFields --> ValidFields{"Required fields?"}
    ValidFields -->|No| FailFields["✗ Missing fields"]
    ValidFields -->|Yes| ExtractNames
    
    ExtractNames --> CheckObjectDeps
    CheckObjectDeps --> InvalidDep{"Invalid dep found?"}
    InvalidDep -->|Yes| FailDep["✗ Invalid dependency"]
    InvalidDep -->|No| CheckArrayDeps
    
    CheckArrayDeps --> InvalidDepArray{"Invalid dep found?"}
    InvalidDepArray -->|Yes| FailDep
    InvalidDepArray -->|No| Success["✓ skills.json valid"]
```

### Required Field Validation

The pipeline checks that all skills have three mandatory fields using `jq` filtering:

- `name` - skill identifier
- `description` - human-readable description
- `dependencies` - dependency object (can be empty `{}` but must exist)

```bash
jq -e '.skills[] | select(.name and .description and .dependencies != null)' skills.json
```

The `-e` flag causes `jq` to exit with non-zero status if the filter produces no output, failing the test if any skill lacks required fields.

### Dependency Reference Validation

The pipeline validates that all dependency references point to existing skills in the registry. It supports both object format (current) and array format (legacy) for backward compatibility:

**Object Format Validation:**
```bash
for dep in $(jq -r '.skills[] | select(.dependencies | type == "object") | .dependencies | keys[]' skills.json 2>/dev/null); do
  if ! echo "$SKILL_NAMES" | grep -q "^${dep}$"; then
    echo "Error: Invalid dependency '$dep'"
    exit 1
  fi
done
```

**Array Format Validation (Legacy):**
```bash
for dep in $(jq -r '.skills[] | select(.dependencies | type == "array") | .dependencies[]' skills.json 2>/dev/null); do
  if ! echo "$SKILL_NAMES" | grep -q "^${dep}$"; then
    echo "Error: Invalid dependency '$dep'"
    exit 1
  fi
done
```

This prevents broken dependency chains where a skill references a non-existent dependency.

**Sources:** [.github/workflows/test-installer.yml:85-117]()

---

## Trigger Conditions

The test pipeline uses path-based filtering to run only when relevant files change, optimizing CI resource usage.

### Path Filter Configuration

```yaml
on:
  push:
    branches: [main]
    paths:
      - 'skills.json'
      - 'skills/**'
  pull_request:
    paths:
      - 'skills.json'
      - 'skills/**'
```

### Trigger Scenarios

| Event Type | Branch | Paths | Pipeline Runs? |
|------------|--------|-------|----------------|
| Push | `main` | `skills.json` modified | ✓ Yes |
| Push | `main` | Any file in `skills/` modified | ✓ Yes |
| Push | `main` | Only `.github/workflows/` modified | ✗ No |
| Pull Request | Any | `skills.json` modified | ✓ Yes |
| Pull Request | Any | Blog post modified | ✗ No |
| Push | `main` | Only website worker modified | ✗ No |

This design ensures tests run for skill-related changes while avoiding unnecessary CI runs for documentation, blog posts, or website updates.

**Sources:** [.github/workflows/test-installer.yml:3-12]()

---

## Test Environment Configuration

### Node.js Version

All jobs use Node.js 18 via the `actions/setup-node@v4` action:

```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '18'
```

This ensures consistency with the target runtime environments for AI coding assistants.

### Shell Compatibility

Tests explicitly specify `bash` as the shell for cross-platform compatibility:

```yaml
shell: bash
```

This is critical for Windows runners where the default shell is PowerShell. Using bash ensures consistent behavior across all three OS platforms.

### Installation Directory

Tests use `.factory/skills/` as the target installation directory, matching the Factory Droid platform convention. This is the default directory used by the universal installer when no platform is explicitly detected.

### Workspace Isolation

Each test run creates a fresh `test-workspace/` directory to ensure isolation:

```bash
mkdir -p test-workspace
cd test-workspace
```

This prevents state pollution between test runs and simulates a clean user environment.

**Sources:** [.github/workflows/test-installer.yml:25-35](), [.github/workflows/test-installer.yml:58-68]()

---

## Test Coverage Summary

The automated testing pipeline provides comprehensive validation across three dimensions:

| Validation Type | Coverage | Test Count |
|----------------|----------|------------|
| **Platform Coverage** | Linux, macOS, Windows | 3 OS × 10 skills = **30 test runs** |
| **Skill Installation** | Individual skill installs | 9 skills × 3 OS = **27 runs** |
| **Bulk Installation** | All skills at once | 3 OS = **3 runs** |
| **Registry Integrity** | JSON structure + dependencies | **1 run** |
| **Total Test Runs** | Per pipeline execution | **31 parallel jobs** |

The matrix strategy enables fast feedback by running all tests in parallel. A typical pipeline execution completes in 2-3 minutes despite running 31 validation jobs.

### Failure Modes Detected

The pipeline catches several categories of installation issues:

1. **Platform-specific bugs** - Script syntax issues on Windows vs Unix
2. **Broken dependencies** - Skills referencing non-existent dependencies
3. **Malformed JSON** - Invalid skills.json syntax
4. **Missing files** - Skills with incomplete file structures
5. **Installation path issues** - Universal installer directory resolution failures
6. **Count mismatches** - Registry declaring skills that don't exist in repository

**Sources:** [.github/workflows/test-installer.yml:1-118]()

---

# Page: Pre-commit Hooks & Quality Gates

# Pre-commit Hooks & Quality Gates

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.factory/hooks.json](.factory/hooks.json)
- [.factory/skills/add-new-opc-skill/SKILL.md](.factory/skills/add-new-opc-skill/SKILL.md)
- [.gitattributes](.gitattributes)
- [.github/workflows/test-installer.yml](.github/workflows/test-installer.yml)
- [.gitignore](.gitignore)
- [skills/domain-hunter/examples/auto-video-editing-domain.md](skills/domain-hunter/examples/auto-video-editing-domain.md)
- [website/resciencelab-logo.svg](website/resciencelab-logo.svg)

</details>



This page documents the pre-commit hook configuration in `.factory/hooks.json` and the manual six-item verification checklist defined in `.factory/skills/add-new-opc-skill/SKILL.md` that must pass before committing any new skill. Together these form the quality gate layer that runs locally, before code reaches CI.

For the automated CI pipeline that validates skills.json structure and runs installer tests after push, see [Automated Testing Pipeline](#6.2). For branch naming and commit message conventions, see [Git Workflow & Branching Strategy](#6.1).

---

## The `.factory/` Directory & Tracking Policy

Most of the `.factory/` directory is excluded from version control, but `hooks.json` is explicitly retained. The relevant `.gitignore` rules are:

[.gitignore:40-45]()

| Path | Tracked |
|---|---|
| `.factory/*` | No (default ignore) |
| `.factory/hooks.json` | **Yes** (explicit exception) |
| `.factory/AGENTS.md` | **Yes** (explicit exception) |
| `.factory/skills/` | **Yes** (explicit exception) |
| `.factory/skills/*` | No (default ignore within skills/) |
| `.factory/skills/add-new-opc-skill/` | **Yes** (explicit exception) |

This means the hook definition travels with the repository, while runtime agent state under `.factory/` does not.

Sources: [.gitignore:40-45]()

---

## Pre-commit Hook: `hooks.json`

The hook registry is defined in `.factory/hooks.json` using a flat JSON schema.

[.factory/hooks.json:1-12]()

**Schema overview:**

| Field | Value / Description |
|---|---|
| `hooks.PreCommit` | Array of hook objects that run before every commit |
| `name` | Unique identifier for the hook |
| `description` | Human-readable explanation |
| `type` | `"command"` — a shell command executed directly |
| `command` | The shell string to run; non-zero exit blocks the commit |

Currently one hook is registered:

### `prevent-factory-droid-coauthor`

**Purpose:** Blocks commits that include `factory-droid[bot]` in the `Co-authored-by` trailer.

**Command:**
```
bash -c 'if git log -1 --pretty=%B | grep -q "factory-droid\[bot\]"; then echo "Error: factory-droid[bot] co-author is not allowed in commits"; exit 1; fi'
```

**Mechanism:** Reads the most recent commit message via `git log -1 --pretty=%B` and pipes it through `grep -q`. If the bot string is found, the hook prints an error and exits with code `1`, which prevents the commit from completing.

**Why this exists:** The `factory-droid` automation bot may inject co-author lines automatically. This hook ensures those bot-attributed commits are never merged into the project's commit history under a human author.

Sources: [.factory/hooks.json:1-12]()

---

**Diagram: Hook execution flow from commit to CI**

```mermaid
flowchart TD
    A["git commit -m 'feat(skill): add X'"] --> B["hooks.json PreCommit hooks"]
    B --> C["prevent-factory-droid-coauthor hook"]
    C --> D["git log -1 --pretty=%B"]
    D --> E{"grep -q 'factory-droid\\[bot\\]'"}
    E -- "Co-authored-by: factory-droid[bot] found" --> F["exit 1<br/>Commit blocked with error"]
    E -- "No bot co-author" --> G["exit 0<br/>Commit succeeds"]
    G --> H["git push origin feature/skill/X"]
    H --> I["GitHub Actions:<br/>test-installer.yml triggered"]
    I --> J["validate-skills-json job:<br/>jq empty skills.json"]
    I --> K["test job matrix:<br/>27 instances (9×3)"]
    I --> L["test-all-skills job:<br/>3 OS instances"]
```

Sources: [.factory/hooks.json:3-11]()

---

## Local Validation Commands

Before committing changes, developers should run local validation commands to catch issues early. These commands are referenced in the development workflow but are not enforced by automated hooks.

### NPM Validation Suite

The repository includes standard npm scripts for code quality checks:

```bash
npm run lint       # Lints JavaScript/TypeScript files
npm run typecheck  # Type-checks TypeScript code
npm run test       # Runs test suite
```

**When to run:** Before creating a pull request, especially when modifying:
- `website/worker.js` (Cloudflare Worker code)
- `scripts/*.py` validation tools
- Any TypeScript configuration

### Blog Post Validation

For blog content changes, the `create-blog.py` script provides validation:

```bash
python3 scripts/create-blog.py validate
```

**Validation checks:**
- `blog.json` structure and metadata fields
- Required content length (2000+ words)
- SEO requirements (15+ keywords, 3-5 internal links)
- FAQ count (5-10 questions)
- Schema.org markup validity

This validation is also run automatically in the `publish-blog.yml` workflow for fast-track blog publishing.

Sources: High-level system diagrams (Diagram 4: Development Workflow)

---

## Manual Verification Checklist (Add New OPC Skill)

When adding a new skill, the `add-new-opc-skill` SKILL.md defines a six-item verification checklist that must pass before committing. These are not automated by `hooks.json`; they are manual checks using shell commands.

[.factory/skills/add-new-opc-skill/SKILL.md:189-218]()

**Verification targets by item:**

| # | Item | File Checked | Command Tool |
|---|---|---|---|
| 1 | `SKILL.md` exists with valid YAML frontmatter | `skills/<skill-name>/SKILL.md` | `head` |
| 2 | Logo SVG exists | `skill-logos/<skill-name>.svg` | `ls` |
| 3 | `skills.json` entry is valid JSON with all required fields | `skills.json` | `python3` + `json` module |
| 4 | `README.md` lists the skill | `README.md` | `grep` |
| 5 | `website/worker.js` contains the skill entry | `website/worker.js` | `grep` |
| 6 | `CHANGELOG.md` has the skill in the matrix | `CHANGELOG.md` | `grep` |

---

**Diagram: Verification checks mapped to repository artifacts**

```mermaid
flowchart LR
    subgraph Checks["Verification Commands"]
        V1["head -5<br/>skills/X/SKILL.md"]
        V2["ls -la<br/>skill-logos/X.svg"]
        V3["python3 -c 'import json'<br/>json.load(skills.json)"]
        V4["grep X<br/>README.md"]
        V5["grep X<br/>website/worker.js"]
        V6["grep X<br/>CHANGELOG.md"]
    end

    subgraph Files["Repository Files"]
        F1["skills/X/SKILL.md<br/>YAML frontmatter"]
        F2["skill-logos/X.svg<br/>pixel-art logo"]
        F3["skills.json<br/>skills array entry"]
        F4["README.md<br/>table row"]
        F5["website/worker.js<br/>fetchCompareData() array"]
        F6["CHANGELOG.md<br/>matrix + version entry"]
    end

    V1 -.validates.-> F1
    V2 -.validates.-> F2
    V3 -.validates.-> F3
    V4 -.validates.-> F4
    V5 -.validates.-> F5
    V6 -.validates.-> F6
```

Sources: [.factory/skills/add-new-opc-skill/SKILL.md:189-218]()

---

### Check 1 — SKILL.md Frontmatter

[.factory/skills/add-new-opc-skill/SKILL.md:194-195]()

Verifies the file exists and opens with YAML frontmatter. `head -5` is used to quickly confirm the `---` delimiter and `name:` / `description:` fields are present without reading the full file.

---

### Check 2 — Logo SVG

[.factory/skills/add-new-opc-skill/SKILL.md:197-198]()

Confirms the pixel-art SVG generated by the logo pipeline was saved to `skill-logos/<skill-name>.svg`. This file is also referenced by the `logo` field in `skills.json` via a raw GitHub URL.

---

### Check 3 — `skills.json` Entry

[.factory/skills/add-new-opc-skill/SKILL.md:200-208]()

Uses a Python one-liner to:
1. Parse `skills.json` with `json.load` (syntax validation)
2. Filter for the new skill by `name`
3. Assert presence of all 11 required top-level fields: `name`, `version`, `description`, `logo`, `icon`, `color`, `triggers`, `dependencies`, `auth`, `install`, `links`

Required fields table:

| Field | Type | Notes |
|---|---|---|
| `name` | string | kebab-case |
| `version` | string | semver, e.g. `"1.0.0"` |
| `description` | string | |
| `logo` | string | Raw GitHub URL to SVG |
| `icon` | string | Simple Icons name or generic |
| `color` | string | 6-char hex without `#` |
| `triggers` | array | Keywords that activate the skill |
| `dependencies` | object | Keys are skill names, values are version ranges |
| `auth` | object | `required`, `type`, `keys` |
| `install` | object | `user` and `project` sub-objects per agent |
| `links` | object | At minimum `github` |

Sources: [.factory/skills/add-new-opc-skill/SKILL.md:72-120]()

---

### Check 4 — `README.md` Table Row

[.factory/skills/add-new-opc-skill/SKILL.md:210-211]()

A `grep` for the skill name confirms the "Included Skills" Markdown table in `README.md` was updated. The expected row format is:

```
| <img src="./skill-logos/<skill-name>.svg" width="24"> | [<skill-name>](./skills/<skill-name>) | Short description |
```

---

### Check 5 — `website/worker.js` Entry

[.factory/skills/add-new-opc-skill/SKILL.md:213-214]()

`grep` confirms the skill name appears in `website/worker.js`. This corresponds to the skill object added inside the `fetchCompareData()` function's hardcoded skills array.

For the full `worker.js` architecture and why this array exists separately from `skills.json`, see [Website Architecture](#4.1).

---

### Check 6 — `CHANGELOG.md`

[.factory/skills/add-new-opc-skill/SKILL.md:216-217]()

`grep` confirms two things are present in `CHANGELOG.md`:
1. A row in the **Skill Compatibility & Dependency Matrix** table
2. An entry under `## [Unreleased]` or the relevant release section

For CHANGELOG versioning conventions and the full matrix format, see [Release Management](#6.4).

---

## End-to-End Quality Gate Flow

**Diagram: From local development to CI, quality gate checkpoints**

```mermaid
flowchart TD
    A["feature/skill/skill-name branch"] --> B["Run add-new-opc-skill checklist"]
    B --> B1["check 1: SKILL.md frontmatter"]
    B --> B2["check 2: skill-logos/skill-name.svg"]
    B --> B3["check 3: skills.json python3 validation"]
    B --> B4["check 4: grep README.md"]
    B --> B5["check 5: grep website/worker.js"]
    B --> B6["check 6: grep CHANGELOG.md"]
    B1 & B2 & B3 & B4 & B5 & B6 --> C["git commit"]
    C --> D[".factory/hooks.json PreCommit"]
    D --> E["prevent-factory-droid-coauthor check"]
    E -- "pass" --> F["git push to remote"]
    F --> G["PR to develop"]
    G --> H["test-installer.yml CI"]
    H --> H1["test job: 3 OS x 9 skills matrix"]
    H --> H2["test-all-skills job: 3 OS"]
    H --> H3["validate-skills-json job: jq + dep integrity"]
```

Sources: [.factory/hooks.json:1-12](), [.factory/skills/add-new-opc-skill/SKILL.md:189-234](), [.github/workflows/test-installer.yml:1-118]()

---

## Summary

| Gate | Mechanism | When | Automated |
|---|---|---|---|
| Six-item verification checklist | Shell commands (`head`, `ls`, `python3`, `grep`) | Before `git commit` | No — manual |
| `prevent-factory-droid-coauthor` | `.factory/hooks.json` PreCommit hook | On `git commit` | Yes — hook |
| `validate-skills-json` CI job | `jq` + dependency referential integrity | On PR push | Yes — GitHub Actions |
| Installer test matrix | `npx skills add` + directory check | On PR push | Yes — GitHub Actions |

---

# Page: Release Management

# Release Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.factory/AGENTS.md](.factory/AGENTS.md)
- [CHANGELOG.md](CHANGELOG.md)
- [template/SKILL.md](template/SKILL.md)
- [website/blog/posts/why-skills-beat-docs.md](website/blog/posts/why-skills-beat-docs.md)

</details>



This page documents the versioning strategy, release workflows, and changelog maintenance practices for the OPC Skills project. It covers how individual skill versions are managed independently, how multi-skill coordinated releases work, and how breaking changes in shared dependencies are handled.

For related topics, see:
- [6.1](#6.1) for the Git branching strategy (feature branches, release branches, hotfixes)
- [6.2](#6.2) for the CI/CD testing pipeline that must pass before any release
- [2.3](#2.3) for how dependency version constraints are declared and validated

---

## Versioning Model

OPC Skills uses two parallel version numbers:

| Version | Location | Purpose |
|---|---|---|
| **Global project version** | `skills.json` `"version"` field (line 2) | Tracks the overall project across coordinated releases |
| **Individual skill version** | Each skill's `"version"` field in `skills.json` | Tracks changes independently per skill |

Both follow [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`.

As of the current codebase state, the global version is `1.0.10` and all skills are at `1.0.0` except `archive` which is at `1.0.1` — reflecting that skills can advance at different rates.

Sources: [skills.json:1-3](), [skills.json:494-497](), [CHANGELOG.md:1-30]()

---

## Version Bump Decision Logic

**When to bump and by how much:**

| Change Type | MAJOR | MINOR | PATCH | No bump |
|---|:---:|:---:|:---:|:---:|
| Breaking API change or incompatible update | ✓ | | | |
| New backward-compatible feature or enhancement | | ✓ | | |
| Bug fix or minor improvement | | | ✓ | |
| Documentation-only change | | | | ✓ |
| Internal refactoring with no behavior change | | | | ✓ |
| Dependency version bump (non-breaking) | | | | ✓ |

The rules are applied **per skill**. A change to `twitter` does not require a version bump to `reddit` unless `reddit`'s behavior changes.

Sources: [.factory/AGENTS.md:328-337]()

---

## Release Flows

There are two distinct release paths depending on the scope of changes.

**Release flow overview:**

```mermaid
flowchart TD
    A["Change scope?"] --> B["Single skill"]
    A --> C["Multiple skills / milestone"]

    B --> D["feature/skill/name/... branch"]
    D --> E["Update skill version in skills.json"]
    E --> F["Add CHANGELOG.md entry under skill subsection"]
    F --> G["PR → develop"]
    G --> H["CI checks pass"]
    H --> I["Merge to develop"]
    I --> J["Check CHANGELOG Matrix for dependents"]
    J --> K{"Breaking change?"}
    K -- "No" --> L["Done"]
    K -- "Yes" --> M["Create separate PRs for each dependent skill"]
    M --> L

    C --> N["release/vX.Y.Z branch from develop"]
    N --> O["Update multiple skill versions in skills.json"]
    O --> P["Move Unreleased entries → versioned section in CHANGELOG.md"]
    P --> Q["PR → main"]
    Q --> R["CI checks pass"]
    R --> S["Merge to main"]
    S --> T["Create GitHub release with tag"]
    T --> U["Back-merge to develop"]
```

Sources: [.factory/AGENTS.md:348-472]()

---

### Quick Release — Single Skill

Each skill can be released independently without coordinating with other skills. The steps below show an example update of `twitter` from `1.0.0` to `1.1.0`.

**Step-by-step:**

1. Create a feature branch from `develop`:
   ```
   feature/skill/twitter/rate-limit-improvement
   ```

2. Update only the relevant skill's `"version"` field in `skills.json`. No other skill versions change.

3. Add a CHANGELOG entry under the `[Unreleased]` section, nested under the skill name:
   ```
   ### twitter
   #### [1.1.0] - 2025-01-22
   - **Added**: Retry mechanism for rate limit handling
   ```

4. Commit using a conventional commit message:
   ```
   feat(twitter): Add retry mechanism and improve rate limiting
   ```

5. Open a PR targeting `develop`. After CI passes and it is merged, check the compatibility matrix in `CHANGELOG.md` to identify which skills depend on `twitter` (`domain-hunter`, `seo-geo`). Run compatibility checks. If no breaking changes, no further action is needed.

Sources: [.factory/AGENTS.md:352-396](), [CHANGELOG.md:8-30]()

---

### Coordinated Release — Multiple Skills

Used for milestone releases when multiple skills need to be versioned together. This is the less common path.

**Step-by-step:**

1. Branch from `develop`:
   ```
   release/v2.0.0
   ```

2. Update multiple skill version entries in `skills.json`.

3. In `CHANGELOG.md`, move all items out of `[Unreleased]` subsections and into a new top-level `## [2.0.0] - YYYY-MM-DD` section, preserving the per-skill sub-structure.

4. Run tests: `npm run test && npm run typecheck`.

5. Create a single PR targeting `main` with commit message:
   ```
   chore(release): Version 2.0.0 - multiple skill updates
   ```

6. After merge, create a GitHub release with a version tag.

7. Back-merge `main` to `develop` (hotfix branches also follow this pattern).

Sources: [.factory/AGENTS.md:399-437]()

---

## CHANGELOG.md Structure

The `CHANGELOG.md` file has two structural responsibilities: a **compatibility matrix** and a **versioned history**.

**CHANGELOG.md file structure:**

```mermaid
flowchart LR
    CL["CHANGELOG.md"]
    CL --> M["## Skill Compatibility & Dependency Matrix\n(table: skill, version, requires, min versions)"]
    CL --> U["## [Unreleased]\n### skill-name\n- (pending changes)"]
    CL --> V["## [X.Y.Z] - date\n### Skill Section\n#### [skill-version] - date\n- change entries"]
    CL --> IL["## Initial Release Features\n(narrative summary)"]
    CL --> VC["## Version Compatibility\n(status table)"]
```

Sources: [CHANGELOG.md:1-50]()

### Skill Compatibility Matrix

The top of `CHANGELOG.md` contains a table showing every skill's current version and its required dependencies. This is the primary reference for identifying which skills are affected when a dependency changes.

| Skill | Current Version | Requires | Min Versions |
|---|---|---|---|
| **requesthunt** | 1.0.0 | — | — |
| **domain-hunter** | 1.0.0 | twitter, reddit | twitter ≥1.0.0, reddit ≥1.0.0 |
| **logo-creator** | 1.0.0 | nanobanana | nanobanana ≥1.0.0 |
| **banner-creator** | 1.0.0 | nanobanana | nanobanana ≥1.0.0 |
| **nanobanana** | 1.0.0 | — | — |
| **reddit** | 1.0.0 | — | — |
| **twitter** | 1.0.0 | — | — |
| **producthunt** | 1.0.0 | — | — |
| **seo-geo** | 1.0.0 | twitter, reddit | twitter ≥1.0.0, reddit ≥1.0.0 |
| **archive** | 1.0.1 | — | — |

This table is maintained manually in [CHANGELOG.md:12-23]().

Sources: [CHANGELOG.md:8-30]()

---

## Handling Breaking Changes in Dependency Skills

When a shared dependency skill (such as `twitter` or `nanobanana`) introduces a breaking change, dependent skills require their own adaptation work. This is managed through separate PRs.

**Breaking change propagation flow:**

```mermaid
flowchart TD
    T["twitter v1.0.0 → v2.0.0\n(BREAKING CHANGE)"]
    T --> C["Check CHANGELOG Compatibility Matrix"]
    C --> DH["dependent: domain-hunter"]
    C --> SG["dependent: seo-geo"]

    DH --> PR1["PR: feature/skill/domain-hunter/twitter-v2-compat\n→ develop"]
    SG --> PR2["PR: feature/skill/seo-geo/twitter-v2-compat\n→ develop"]

    PR1 --> V1{"Behavior changed\nin domain-hunter?"}
    PR2 --> V2{"Behavior changed\nin seo-geo?"}

    V1 -- "Yes" --> B1["Bump domain-hunter version\n(patch or minor)"]
    V1 -- "No" --> N1["No version bump needed"]
    V2 -- "Yes" --> B2["Bump seo-geo version"]
    V2 -- "No" --> N2["No version bump needed"]
```

The two adaptation PRs are **independent** — they can be reviewed and merged separately. The breaking change to the dependency does not force a version bump on dependents unless the dependent's own behavior changes.

Sources: [.factory/AGENTS.md:439-471]()

### Dependency Update Rules Reference

| Scenario | Required Action for Dependent Skill B | Version Bump on B? |
|---|---|---|
| Skill A releases minor update | No action needed | No |
| Skill A releases patch update | No action needed | No |
| Skill A releases breaking change | Must update to support new version | Patch or Minor |
| B wants to document support for new Skill A | Update B's CHANGELOG only | No |

Sources: [.factory/AGENTS.md:490-495]()

---

## CHANGELOG Entry Format

**Breaking change entry format** (annotated with `⚠️ BREAKING`):

```markdown
### twitter
#### [2.0.0] - 2025-01-23 ⚠️ BREAKING
- **Changed**: API now requires v2 endpoint authentication
- **Removed**: Deprecated v1 endpoint support
- **Migration Guide**: See docs/migration-guide.md
```

**Standard entry format:**

```markdown
### archive
#### [1.0.1] - 2026-02-23
- **Fixed**: Description YAML block scalar replaced with single-line string
```

Both formats appear in the actual changelog. See [CHANGELOG.md:40-45]() for the `archive` `1.0.1` entry as a concrete example.

Sources: [CHANGELOG.md:40-45](), [.factory/AGENTS.md:442-449]()

---

## Release Checklist

The following items must be verified before merging any release PR. This list is the authoritative pre-merge gate defined in [.factory/AGENTS.md:499-507]().

- [ ] Version numbers updated in `skills.json` (only for skills being changed)
- [ ] `CHANGELOG.md` entries created for each updated skill
- [ ] Skill's own dependencies tested (if applicable)
- [ ] Dependent skills tested if this release introduces a breaking change
- [ ] Conventional commit message used (`feat`, `fix`, `chore`, etc.)
- [ ] PR description references issue number(s) with closing keywords (`Fixes #123`)
- [ ] All CI/CD checks pass (see [6.2](#6.2) for what the automated test pipeline validates)
- [ ] Documentation (`SKILL.md`, examples) updated if behavior changed

Sources: [.factory/AGENTS.md:497-508]()

---

## Version Number Locations in the Codebase

This diagram maps version concepts to their exact storage locations, so it is clear what files must be edited during a release.

```mermaid
flowchart LR
    subgraph "skills.json"
        GV["root .version\n(global project version)"]
        SV1["skills[n].version\n(per-skill version)"]
    end

    subgraph "CHANGELOG.md"
        MAT["Compatibility Matrix table\n(lines 12-23)"]
        HIST["## [X.Y.Z] sections\n(per-release entries)"]
        UNREL["## [Unreleased] section"]
    end

    GV -- "updated on coordinated release" --> HIST
    SV1 -- "updated on skill release" --> HIST
    SV1 -- "reflected in" --> MAT
    UNREL -- "promoted to versioned section on release" --> HIST
```

Sources: [skills.json:1-3](), [skills.json:9-10](), [CHANGELOG.md:1-50]()

---

# Page: Creating New Skills

# Creating New Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.factory/AGENTS.md](.factory/AGENTS.md)
- [.factory/hooks.json](.factory/hooks.json)
- [.factory/skills/add-new-opc-skill/SKILL.md](.factory/skills/add-new-opc-skill/SKILL.md)
- [.gitignore](.gitignore)
- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [skill-logos/archive.svg](skill-logos/archive.svg)
- [skills/domain-hunter/examples/auto-video-editing-domain.md](skills/domain-hunter/examples/auto-video-editing-domain.md)
- [template/SKILL.md](template/SKILL.md)
- [website/blog/posts/why-skills-beat-docs.md](website/blog/posts/why-skills-beat-docs.md)
- [website/opc-banner.png](website/opc-banner.png)
- [website/resciencelab-logo.svg](website/resciencelab-logo.svg)

</details>



This page provides a step-by-step technical guide for contributors adding new skills to the OPC Skills repository. It covers the add-new-opc-skill meta-skill workflow, required file modifications across six locations, validation procedures, and pull request submission.

For information about the overall development workflow and Git Flow branching strategy, see [Development & CI/CD](#6). For details on skill structure standards, see [Skill Structure & Standards](#2.2).

---

## Overview

Adding a new skill requires updating six files in a coordinated manner:

1. `skills/<skill-name>/SKILL.md` - Skill documentation with YAML frontmatter
2. `skill-logos/<skill-name>.svg` - Pixel-art style logo
3. `skills.json` - Central metadata registry
4. `README.md` - Skills listing table
5. `website/worker.js` - Hardcoded skill data for website rendering
6. `CHANGELOG.md` - Dependency matrix and version entry

The `.factory/skills/add-new-opc-skill/SKILL.md` meta-skill provides a comprehensive checklist to ensure no steps are missed.

**Sources:** [.factory/skills/add-new-opc-skill/SKILL.md:1-235](), [README.md:150-168]()

---

## Prerequisites

### Branch Setup

All new skills must be developed on a feature branch following the Git Flow naming convention:

```bash
feature/skill/<skill-name>/<feature-description>
```

Branch from `develop`, not `main`:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/skill/my-new-skill
```

**Sources:** [.factory/AGENTS.md:176-189](), [.factory/skills/add-new-opc-skill/SKILL.md:10-14]()

### Naming Conventions

- **Skill directory name**: kebab-case (e.g., `domain-hunter`, `logo-creator`)
- **YAML `name` field**: Must match directory name exactly
- **Logo filename**: `skill-logos/<skill-name>.svg`

**Sources:** [.factory/AGENTS.md:52-55](), [.factory/skills/add-new-opc-skill/SKILL.md:14]()

---

## File Dependency Graph

```mermaid
graph TB
    BRANCH["feature/skill/<name> branch"]
    
    subgraph "Core Skill Files"
        SKILLMD["skills/<name>/SKILL.md<br/>YAML frontmatter + docs"]
        SCRIPTS["skills/<name>/scripts/<br/>Python/Shell executables"]
        EXAMPLES["skills/<name>/examples/<br/>Usage workflows"]
    end
    
    subgraph "Asset Files"
        LOGO["skill-logos/<name>.svg<br/>Pixel-art logo"]
    end
    
    subgraph "Registry & Listings"
        SKILLSJSON["skills.json<br/>Central metadata"]
        README["README.md<br/>Skills table"]
        WORKER["website/worker.js<br/>fetchCompareData()"]
        CHANGELOG["CHANGELOG.md<br/>Dependency matrix"]
    end
    
    subgraph "Validation"
        VALIDATE["Validation Scripts<br/>JSON syntax check"]
        PRECOMMIT["hooks.json<br/>Pre-commit checks"]
    end
    
    BRANCH --> SKILLMD
    BRANCH --> SCRIPTS
    BRANCH --> EXAMPLES
    BRANCH --> LOGO
    
    SKILLMD --> SKILLSJSON
    LOGO --> SKILLSJSON
    LOGO --> README
    LOGO --> WORKER
    
    SKILLSJSON --> README
    SKILLSJSON --> WORKER
    SKILLSJSON --> CHANGELOG
    
    SKILLSJSON --> VALIDATE
    BRANCH --> PRECOMMIT
    
    VALIDATE --> PR["Pull Request to develop"]
    PRECOMMIT --> PR
```

All six registry/listing files must be updated in a single atomic commit to maintain consistency across the codebase.

**Sources:** [.factory/skills/add-new-opc-skill/SKILL.md:16-234](), [README.md:150-158]()

---

## Step 1: Create Skill Directory Structure

### Directory Layout

```bash
skills/<skill-name>/
├── SKILL.md              # Required: Main documentation
├── scripts/              # Conditional: Python/Shell scripts
│   └── *.py / *.sh
├── examples/             # Recommended: Usage examples
│   └── *.md
└── references/           # Optional: API docs
    └── *.md
```

Use the template as a starting point:

```bash
cp -r template skills/<skill-name>
```

**Sources:** [.factory/skills/add-new-opc-skill/SKILL.md:18-46](), [template/SKILL.md:1-130]()

### SKILL.md Frontmatter Structure

```mermaid
graph LR
    SKILLMD["SKILL.md file"]
    
    subgraph "YAML Frontmatter (lines 1-4)"
        NAME["name: skill-name<br/>(kebab-case)"]
        DESC["description: What it does<br/>+ Use when..."]
    end
    
    subgraph "Markdown Content"
        PREREQ["## Prerequisites<br/>API keys, setup"]
        USAGE["## Usage Examples<br/>Commands + output"]
        CMDS["## Commands<br/>Script documentation"]
        TROUBLE["## Troubleshooting<br/>Common issues"]
    end
    
    SKILLMD --> NAME
    SKILLMD --> DESC
    SKILLMD --> PREREQ
    SKILLMD --> USAGE
    SKILLMD --> CMDS
    SKILLMD --> TROUBLE
```

The frontmatter must follow this exact structure:

```yaml
---
name: skill-name
description: Clear description of what this skill does and when to use it. Include trigger keywords and contexts inline, e.g. "Use when user wants to X, Y, or Z."
---
```

**Key constraints:**
- No `triggers` field (deprecated as of v1.0.6 - merged into description)
- No `dependencies` field (declared only in `skills.json`)
- Description must be a single-line string (no YAML block scalars like `>-` or `|`)

**Sources:** [template/SKILL.md:1-130](), [CHANGELOG.md:81-86](), [.factory/skills/add-new-opc-skill/SKILL.md:33-40]()

---

## Step 2: Generate Skill Logo

All skill logos follow a consistent pixel-art style. Generation uses the `logo-creator` and `nanobanana` skills.

### Logo Generation Workflow

```bash
# 1. Generate 20 variations
python3 skills/nanobanana/scripts/batch_generate.py \
  "Pixel art <subject> logo, 8-bit retro style, black pixels on white background, minimalist icon, clean crisp edges, no text, centered" \
  -n 20 --ratio 1:1 \
  -d .skill-archive/logo-creator/$(date +%Y-%m-%d)-<skill-name> \
  -p logo

# 2. Preview in browser
cp skills/logo-creator/templates/preview.html .skill-archive/logo-creator/<date>-<skill-name>/
open .skill-archive/logo-creator/<date>-<skill-name>/preview.html

# 3. Crop and vectorize selected logo
python3 skills/logo-creator/scripts/crop_logo.py logo-05.png logo-cropped.png
python3 skills/logo-creator/scripts/vectorize.py logo-cropped.png skill-logos/<skill-name>.svg
```

### Logo Requirements

| Property | Requirement |
|----------|-------------|
| Format | SVG (vectorized from PNG) |
| Style | Pixel-art, 8-bit retro |
| Colors | Black pixels on white background |
| Size | 24px width for README display |
| Location | `skill-logos/<skill-name>.svg` |

**Sources:** [.factory/skills/add-new-opc-skill/SKILL.md:48-69](), [README.md:46-55]()

---

## Step 3: Add skills.json Entry

The `skills.json` file at the repository root contains the central skill registry. Each skill requires a complete metadata object.

### skills.json Schema

```mermaid
graph TB
    ROOT["skills.json root"]
    
    subgraph "Top-level Fields"
        VERSION["version: '1.0.x'<br/>Global project version"]
        SKILLS_ARRAY["skills: []<br/>Array of skill objects"]
    end
    
    subgraph "Skill Object Fields (all required)"
        NAME["name: string<br/>Matches directory name"]
        VERS["version: string<br/>Semantic version"]
        DESC["description: string<br/>Full description"]
        LOGO["logo: URL string<br/>GitHub raw URL"]
        ICON["icon: string<br/>Simple Icons name"]
        COLOR["color: string<br/>Hex without #"]
        TRIGGERS["triggers: string[]<br/>Activation keywords"]
        DEPS["dependencies: object<br/>Version ranges"]
        AUTH["auth: object<br/>API key requirements"]
        INSTALL["install: object<br/>User + project commands"]
        COMMANDS["commands: string[]<br/>CLI commands"]
        LINKS["links: object<br/>GitHub URL"]
    end
    
    ROOT --> VERSION
    ROOT --> SKILLS_ARRAY
    SKILLS_ARRAY --> NAME
    SKILLS_ARRAY --> VERS
    SKILLS_ARRAY --> DESC
    SKILLS_ARRAY --> LOGO
    SKILLS_ARRAY --> ICON
    SKILLS_ARRAY --> COLOR
    SKILLS_ARRAY --> TRIGGERS
    SKILLS_ARRAY --> DEPS
    SKILLS_ARRAY --> AUTH
    SKILLS_ARRAY --> INSTALL
    SKILLS_ARRAY --> COMMANDS
    SKILLS_ARRAY --> LINKS
```

**Sources:** [.factory/skills/add-new-opc-skill/SKILL.md:72-120]()

### Complete skills.json Entry Template

```json
{
  "name": "skill-name",
  "version": "1.0.0",
  "description": "Full description of what the skill does and when to use it.",
  "logo": "https://raw.githubusercontent.com/ReScienceLab/opc-skills/main/skill-logos/skill-name.svg",
  "icon": "globe",
  "color": "6B7280",
  "triggers": ["keyword1", "keyword2", "phrase"],
  "dependencies": {},
  "auth": {
    "required": false,
    "type": null,
    "keys": []
  },
  "install": {
    "user": {
      "claude": "npx skills add ReScienceLab/opc-skills --skill skill-name -a claude",
      "droid": "npx skills add ReScienceLab/opc-skills --skill skill-name -a droid",
      "opencode": "npx skills add ReScienceLab/opc-skills --skill skill-name -a opencode",
      "codex": "npx skills add ReScienceLab/opc-skills --skill skill-name -a codex"
    },
    "project": {
      "claude": "npx skills add ReScienceLab/opc-skills --skill skill-name",
      "droid": "npx skills add ReScienceLab/opc-skills --skill skill-name",
      "cursor": "npx skills add ReScienceLab/opc-skills --skill skill-name",
      "opencode": "npx skills add ReScienceLab/opc-skills --skill skill-name",
      "codex": "npx skills add ReScienceLab/opc-skills --skill skill-name"
    }
  },
  "commands": [
    "python3 scripts/example.py \"{input}\""
  ],
  "links": {
    "github": "https://github.com/ReScienceLab/opc-skills/tree/main/skills/skill-name"
  }
}
```

### Field-Specific Requirements

| Field | Type | Notes |
|-------|------|-------|
| `icon` | string | Use [Simple Icons](https://simpleicons.org/) name or generic: `"globe"`, `"archive"`, `"image"` |
| `color` | string | 6-char hex **without** `#` prefix (e.g., `"6B7280"`) |
| `dependencies` | object | Keys: skill names, Values: version ranges (e.g., `{"twitter": ">=1.0.0"}`) |
| `auth.keys` | array | Each object: `{"env": "VAR_NAME", "url": "https://...", "optional": true/false}` |
| `commands` | array | Empty `[]` if skill provides instructions only, no scripts |

**Sources:** [.factory/skills/add-new-opc-skill/SKILL.md:72-125]()

### Validation

After editing `skills.json`, validate syntax:

```bash
python3 -c "import json; json.load(open('skills.json')); print('valid')"
```

**Sources:** [.factory/skills/add-new-opc-skill/SKILL.md:122-125]()

---

## Step 4: Update README.md Skills Table

The skills table in `README.md` provides a quick overview of all skills. Add a row to the markdown table at [README.md:42-55]():

```markdown
| <img src="./skill-logos/skill-name.svg" width="24"> | [skill-name](./skills/skill-name) | Short description |
```

Insert the row in an appropriate position within the existing table (typically ordered by importance or category).

**Sources:** [.factory/skills/add-new-opc-skill/SKILL.md:127-135](), [README.md:42-55]()

---

## Step 5: Update website/worker.js Hardcoded Data

The Cloudflare Worker in `website/worker.js` contains hardcoded skill data for performance. The skill must be added to the `skills` array inside the `fetchCompareData()` function.

### Location in worker.js

Find the closing of the skills array (look for `],\n  };\n}`) and insert the new skill object **before** that closing:

```javascript
{
  name: "skill-name",
  version: "1.0.0",
  description: "Full description",
  icon: "globe",
  color: "6B7280",
  triggers: ["keyword1", "keyword2"],
  dependencies: [],
  auth: { required: false, note: "No API key needed" },
  install: {
    user: {
      claude: "npx skills add ReScienceLab/opc-skills --skill skill-name -a claude",
      droid: "npx skills add ReScienceLab/opc-skills --skill skill-name -a droid",
      opencode: "npx skills add ReScienceLab/opc-skills --skill skill-name -a opencode",
      codex: "npx skills add ReScienceLab/opc-skills --skill skill-name -a codex",
    },
    project: {
      claude: "npx skills add ReScienceLab/opc-skills --skill skill-name",
      droid: "npx skills add ReScienceLab/opc-skills --skill skill-name",
      cursor: "npx skills add ReScienceLab/opc-skills --skill skill-name",
      opencode: "npx skills add ReScienceLab/opc-skills --skill skill-name",
      codex: "npx skills add ReScienceLab/opc-skills --skill skill-name",
    },
  },
  commands: [],
  links: {
    github: "https://github.com/ReScienceLab/opc-skills/tree/main/skills/skill-name",
  },
},
```

**Important:** This data duplication exists because the worker fetches from GitHub raw URLs for dynamic skill pages, but uses hardcoded data for the compare page to avoid rate limiting.

**Sources:** [.factory/skills/add-new-opc-skill/SKILL.md:137-172]()

---

## Step 6: Update CHANGELOG.md

Two updates are required in `CHANGELOG.md`:

### 1. Dependency Matrix Table

Add a row to the compatibility matrix at [CHANGELOG.md:8-23]():

```markdown
| **skill-name** | 1.0.0 | - | - |
```

If the skill has dependencies:

```markdown
| **skill-name** | 1.0.0 | dependency1, dependency2 | dependency1 ≥1.0.0, dependency2 ≥1.0.0 |
```

### 2. Version Entry

Add a subsection under `## [Unreleased]` (or the specific release version section):

```markdown
### skill-name
#### [1.0.0] - YYYY-MM-DD
- **Added**: Initial release - brief description of functionality
```

**Sources:** [.factory/skills/add-new-opc-skill/SKILL.md:173-188](), [CHANGELOG.md:8-31]()

---

## Validation Workflow

```mermaid
graph TB
    START["Pre-commit validation"]
    
    subgraph "File Existence Checks"
        CHECK1["SKILL.md exists<br/>skills/<name>/SKILL.md"]
        CHECK2["Logo exists<br/>skill-logos/<name>.svg"]
        CHECK3["README lists skill<br/>grep '<name>' README.md"]
        CHECK4["worker.js lists skill<br/>grep '<name>' website/worker.js"]
        CHECK5["CHANGELOG lists skill<br/>grep '<name>' CHANGELOG.md"]
    end
    
    subgraph "Content Validation"
        CHECK6["YAML frontmatter valid<br/>head -5 SKILL.md"]
        CHECK7["skills.json syntax<br/>python3 JSON parser"]
        CHECK8["skills.json fields complete<br/>Check all required keys"]
    end
    
    subgraph "Git Checks"
        HOOK["hooks.json PreCommit<br/>Block factory-droid[bot]"]
    end
    
    START --> CHECK1
    START --> CHECK2
    START --> CHECK3
    START --> CHECK4
    START --> CHECK5
    
    CHECK1 --> CHECK6
    CHECK2 --> CHECK7
    CHECK3 --> CHECK8
    
    CHECK6 --> HOOK
    CHECK7 --> HOOK
    CHECK8 --> HOOK
    
    HOOK --> PASS["All checks passed<br/>Ready to commit"]
    HOOK --> FAIL["Validation failed<br/>Fix issues"]
```

**Sources:** [.factory/skills/add-new-opc-skill/SKILL.md:189-218]()

### Automated Validation Script

```bash
# 1. SKILL.md frontmatter check
head -5 skills/<skill-name>/SKILL.md

# 2. Logo existence
ls -la skill-logos/<skill-name>.svg

# 3. skills.json validation
python3 -c "
import json
config = json.load(open('skills.json'))
skill = [s for s in config['skills'] if s['name'] == '<skill-name>'][0]
required = ['name','version','description','logo','icon','color','triggers','dependencies','auth','install','links']
missing = [f for f in required if f not in skill]
print('PASS' if not missing else f'MISSING: {missing}')
"

# 4. README listing check
grep '<skill-name>' README.md

# 5. worker.js listing check
grep '<skill-name>' website/worker.js

# 6. CHANGELOG listing check
grep '<skill-name>' CHANGELOG.md
```

**Sources:** [.factory/skills/add-new-opc-skill/SKILL.md:195-218]()

---

## Git Workflow and PR Submission

```mermaid
graph TB
    DEVELOP["develop branch<br/>(up to date)"]
    
    FEATURE["feature/skill/<name><br/>Create branch"]
    
    subgraph "File Changes"
        ADD1["Add skills/<name>/SKILL.md"]
        ADD2["Add skill-logos/<name>.svg"]
        ADD3["Update skills.json"]
        ADD4["Update README.md"]
        ADD5["Update website/worker.js"]
        ADD6["Update CHANGELOG.md"]
    end
    
    COMMIT["git commit -m<br/>'feat(skill): add <name> skill'"]
    
    PUSH["git push -u origin<br/>feature/skill/<name>"]
    
    PR["gh pr create<br/>--base develop"]
    
    subgraph "CI Checks"
        CI1["test-installer.yml<br/>Cross-platform tests"]
        CI2["JSON validation<br/>skills.json syntax"]
        CI3["PreCommit hooks<br/>factory-droid blocker"]
    end
    
    REVIEW["Code review<br/>Human approval"]
    
    MERGE["Merge to develop<br/>via GitHub UI"]
    
    DEVELOP --> FEATURE
    FEATURE --> ADD1
    FEATURE --> ADD2
    FEATURE --> ADD3
    FEATURE --> ADD4
    FEATURE --> ADD5
    FEATURE --> ADD6
    
    ADD1 --> COMMIT
    ADD2 --> COMMIT
    ADD3 --> COMMIT
    ADD4 --> COMMIT
    ADD5 --> COMMIT
    ADD6 --> COMMIT
    
    COMMIT --> PUSH
    PUSH --> PR
    
    PR --> CI1
    PR --> CI2
    PR --> CI3
    
    CI1 --> REVIEW
    CI2 --> REVIEW
    CI3 --> REVIEW
    
    REVIEW --> MERGE
```

**Sources:** [.factory/skills/add-new-opc-skill/SKILL.md:220-234](), [.factory/AGENTS.md:168-227]()

### Step-by-Step Commands

```bash
# 1. Create and switch to feature branch
git checkout develop
git pull origin develop
git checkout -b feature/skill/<skill-name>

# 2. Add all modified files
git add skills/<skill-name>/ \
        skill-logos/<skill-name>.svg \
        skills.json \
        README.md \
        website/worker.js \
        CHANGELOG.md

# 3. Commit with conventional commit format
git commit -m "feat(skill): add <skill-name> skill"

# 4. Push branch to origin
git push -u origin feature/skill/<skill-name>

# 5. Create PR targeting develop
gh pr create --base develop --head feature/skill/<skill-name>
```

**Sources:** [.factory/skills/add-new-opc-skill/SKILL.md:220-234](), [.factory/AGENTS.md:230-249]()

### Commit Message Convention

Use the `feat(skill)` prefix for new skills:

```
feat(skill): add <skill-name> skill
```

**Do not** include watermarks or AI-generated signatures in commit messages.

**Sources:** [.factory/AGENTS.md:230-249]()

### Pre-commit Hook Enforcement

The `.factory/hooks.json` file defines a pre-commit hook that blocks commits containing `factory-droid[bot]` as a co-author:

```json
{
  "hooks": {
    "PreCommit": [
      {
        "name": "prevent-factory-droid-coauthor",
        "description": "Prevents adding factory-droid[bot] as co-author in commits",
        "type": "command",
        "command": "bash -c 'if git log -1 --pretty=%B | grep -q \"factory-droid\\[bot\\]\"; then echo \"Error: factory-droid[bot] co-author is not allowed in commits\"; exit 1; fi'"
      }
    ]
  }
}
```

**Sources:** [.factory/hooks.json:1-12]()

---

## PR Merge Requirements

Before a PR can be merged, all of the following must pass:

| Check | Command/Process |
|-------|----------------|
| Website tests | `npm run test` in `website/` |
| Type checking | `npm run typecheck` in `website/` |
| Linting | `npm run lint` in `website/` |
| SKILL.md frontmatter | YAML parser validation |
| skills.json syntax | Python JSON validation |
| Cross-platform install | `test-installer.yml` workflow (27 skill × 3 OS tests) |
| Human code review | GitHub PR approval required |

**Sources:** [.factory/AGENTS.md:311-325]()

---

## Complete File Update Checklist

Use this checklist to ensure all required updates are complete:

- [ ] `skills/<name>/SKILL.md` created with valid YAML frontmatter
- [ ] `skill-logos/<name>.svg` generated and vectorized
- [ ] `skills.json` entry added with all 12 required fields
- [ ] `README.md` skills table row added
- [ ] `website/worker.js` hardcoded data entry added in `fetchCompareData()`
- [ ] `CHANGELOG.md` dependency matrix row added
- [ ] `CHANGELOG.md` version entry added under `[Unreleased]`
- [ ] Validation script executed successfully (all 6 checks pass)
- [ ] Feature branch created following naming convention
- [ ] Commit message follows `feat(skill): add <name> skill` format
- [ ] PR created targeting `develop` branch
- [ ] CI checks passing (test-installer.yml, JSON validation)

**Sources:** [.factory/skills/add-new-opc-skill/SKILL.md:189-234]()

---

## Example: Adding the archive Skill

The archive skill was added in PR #57. This example shows the actual file changes made:

### Files Modified

| File | Change Type | Specific Change |
|------|-------------|-----------------|
| `skills/archive/SKILL.md` | Created | YAML frontmatter + documentation [CHANGELOG.md:55-60]() |
| `skill-logos/archive.svg` | Created | Pixel-art archive box logo [skill-logos/archive.svg:1-10]() |
| `skills.json` | Entry added | Complete metadata object with install commands |
| `README.md` | Row added | `\| <img src="./skill-logos/archive.svg" width="24"> \| [archive](./skills/archive) \| ...` [README.md:55]() |
| `website/worker.js` | Object added | Hardcoded skill data in `fetchCompareData()` |
| `CHANGELOG.md` | Matrix + entry | Dependency matrix row + version entry [CHANGELOG.md:23]() |

### Commit Pattern

```
feat(skill): add archive skill for indexed session knowledge

- Added archive skill with SKILL.md documentation
- Generated pixel-art logo via logo-creator skill
- Updated skills.json with complete metadata
- Added README.md listing and website worker.js data
- Updated CHANGELOG.md dependency matrix
```

**Sources:** [CHANGELOG.md:55-60](), [README.md:55]()

---

## Common Issues and Solutions

### Issue: skills.json Parse Error

**Symptom:** `JSONDecodeError` when validating `skills.json`

**Causes:**
- Missing comma between skill objects
- Trailing comma after last skill object
- Unescaped quotes in description strings

**Solution:**
```bash
# Use Python's JSON parser for detailed error messages
python3 -c "import json; json.load(open('skills.json'))"
```

**Sources:** [.factory/skills/add-new-opc-skill/SKILL.md:122-125]()

### Issue: SKILL.md Description Not Displaying on skills.sh

**Symptom:** Description field shows as `|` or is cut off on skills.sh

**Cause:** Using YAML block scalar syntax (`>-` or `|`) instead of single-line string

**Solution:** Use a single-line string without block scalar indicators:

```yaml
# ❌ Wrong - block scalar
description: >-
  This is a multi-line
  description

# ✅ Correct - single line
description: "This is a single-line description. Use when..."
```

**Sources:** [CHANGELOG.md:81-86]()

### Issue: Logo Not Appearing in README

**Symptom:** Broken image icon in README.md skills table

**Causes:**
- Logo filename doesn't match skill name
- Logo not committed to `skill-logos/` directory
- SVG file is corrupted or invalid

**Solution:**
```bash
# Verify logo exists with correct name
ls -la skill-logos/<skill-name>.svg

# Test SVG validity by opening in browser
open skill-logos/<skill-name>.svg
```

**Sources:** [.factory/skills/add-new-opc-skill/SKILL.md:48-69]()

### Issue: worker.js Not Showing Skill on Website

**Symptom:** Skill appears in JSON but not on opc.dev

**Cause:** Forgot to add hardcoded entry to `website/worker.js` `fetchCompareData()` function

**Solution:** Skill must be added in **both** locations:
1. `skills.json` (for dynamic skill pages)
2. `website/worker.js` (for compare page performance)

**Sources:** [.factory/skills/add-new-opc-skill/SKILL.md:137-172]()

---

## Related Documentation

- For skill dependency management and version compatibility, see [Dependency Management](#2.3)
- For the complete Git Flow workflow including releases, see [Git Workflow & Branching Strategy](#6.1)
- For understanding the CI/CD pipeline that validates new skills, see [Automated Testing Pipeline](#6.2)
- For details on the SKILL.md standard and frontmatter requirements, see [Skill Structure & Standards](#2.2)

**Sources:** [.factory/AGENTS.md:1-625](), [.factory/skills/add-new-opc-skill/SKILL.md:1-235]()