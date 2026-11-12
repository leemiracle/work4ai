# Page: Healthcare Marketplace Overview

# Healthcare Marketplace Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [.github/workflows/claude-skill-review.yml](.github/workflows/claude-skill-review.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [README.md](README.md)
- [icd10-codes/.claude-plugin/plugin.json](icd10-codes/.claude-plugin/plugin.json)

</details>



## Purpose and Scope

This document provides a high-level introduction to the `anthropics/healthcare` repository, which serves as a Claude Code marketplace containing healthcare-focused Skills and MCP Servers. It covers the repository's architecture, the distinction between Skills and MCP Servers, and how components are discovered and installed.

For detailed information about specific components:
- Marketplace architecture and plugin system: see [Marketplace Architecture](#2)
- Individual healthcare skills: see [Healthcare Skills](#3)
- External data sources: see [MCP Servers and External Data](#4)
- Development workflows: see [CI/CD and Automation](#5)

## What is the Healthcare Marketplace?

The Healthcare Marketplace is a curated collection of Claude Code plugins designed for healthcare workflows. It contains two types of components:

1. **Skills**: AI-powered capabilities that guide Claude through complex healthcare tasks (clinical trial protocol generation, prior authorization review, FHIR API development)
2. **MCP Servers**: External data connectors that provide access to healthcare databases and registries (CMS coverage policies, NPI provider data, PubMed literature, ICD-10 codes)

The marketplace uses a plugin-based architecture where components are registered in a central `marketplace.json` file and can be independently installed and composed to accomplish healthcare workflows.

Sources: [README.md:1-63](), [.claude-plugin/marketplace.json:1-74]()

## Repository Structure

The repository follows a standardized directory layout where each component type has a specific naming convention and structure:

```mermaid
graph TB
    subgraph "Repository Root"
        MP["<b>.claude-plugin/marketplace.json</b><br/>Central registry"]
        README["<b>README.md</b><br/>User documentation"]
        
        subgraph "Skills (suffix: -skill/)"
            CTP["<b>clinical-trial-protocol-skill/</b><br/>SKILL.md + references/ + scripts/"]
            PAR["<b>prior-auth-review-skill/</b><br/>SKILL.md + assets/"]
            FHIR["<b>fhir-developer-skill/</b><br/>SKILL.md + references/ + scripts/"]
        end
        
        subgraph "MCP Servers (suffix: /)"
            CMS["<b>cms-coverage/</b><br/>.claude-plugin/plugin.json"]
            NPI["<b>npi-registry/</b><br/>.claude-plugin/plugin.json"]
            PM["<b>pubmed/</b><br/>.claude-plugin/plugin.json"]
            ICD["<b>icd10-codes/</b><br/>.claude-plugin/plugin.json"]
        end
        
        subgraph "Infrastructure (.github/workflows/)"
            SR["<b>claude-skill-review.yml</b><br/>Automated skill reviews"]
            CR["<b>claude-code-review.yml</b><br/>Code review on @mention"]
            REL["<b>release.yml</b><br/>Package and release"]
        end
    end
    
    MP -->|"registers"| CTP
    MP -->|"registers"| PAR
    MP -->|"registers"| FHIR
    MP -->|"registers"| CMS
    MP -->|"registers"| NPI
    MP -->|"registers"| PM
    MP -->|"registers"| ICD
    
    SR -->|"validates changes to"| CTP
    SR -->|"validates changes to"| PAR
    SR -->|"validates changes to"| FHIR
    REL -->|"packages"| CTP
    REL -->|"packages"| PAR
    REL -->|"packages"| FHIR
```

**Directory Naming Conventions:**
- Skills: `*-skill/` directories containing `SKILL.md` files
- MCP Servers: subdirectories with `.claude-plugin/plugin.json` files
- CI/CD: `.github/workflows/` containing GitHub Actions definitions

Sources: [.claude-plugin/marketplace.json:11-73](), [.github/workflows/claude-skill-review.yml:29-30](), [.github/workflows/release.yml:21-29]()

## Marketplace Registry Architecture

The marketplace.json file serves as the single source of truth for all available plugins. It defines metadata and source locations for both Skills and MCP Servers:

```mermaid
graph LR
    subgraph "marketplace.json Structure"
        ROOT["<b>root</b><br/>name: healthcare<br/>owner: Anthropic<br/>version: 1.0.0"]
        PLUGINS["<b>plugins[]</b><br/>Array of 7 plugin definitions"]
        
        ROOT --> PLUGINS
        
        PLUGINS --> S1["<b>clinical-trial-protocol</b><br/>source: ./<br/>skills: [./clinical-trial-protocol-skill]"]
        PLUGINS --> S2["<b>prior-auth-review</b><br/>source: ./<br/>skills: [./prior-auth-review-skill]"]
        PLUGINS --> S3["<b>fhir-developer</b><br/>source: ./<br/>skills: [./fhir-developer-skill]"]
        PLUGINS --> M1["<b>cms-coverage</b><br/>source: ./cms-coverage"]
        PLUGINS --> M2["<b>npi-registry</b><br/>source: ./npi-registry"]
        PLUGINS --> M3["<b>pubmed</b><br/>source: ./pubmed"]
        PLUGINS --> M4["<b>icd10-codes</b><br/>source: ./icd10-codes"]
    end
    
    subgraph "Implementation Files"
        S1 --> FILE1["<b>clinical-trial-protocol-skill/SKILL.md</b>"]
        S2 --> FILE2["<b>prior-auth-review-skill/SKILL.md</b>"]
        S3 --> FILE3["<b>fhir-developer-skill/SKILL.md</b>"]
        M1 --> FILE4["<b>cms-coverage/.claude-plugin/plugin.json</b>"]
        M2 --> FILE5["<b>npi-registry/.claude-plugin/plugin.json</b>"]
        M3 --> FILE6["<b>pubmed/.claude-plugin/plugin.json</b>"]
        M4 --> FILE7["<b>icd10-codes/.claude-plugin/plugin.json</b>"]
    end
```

**Key Configuration Patterns:**

| Component Type | `source` Field | Implementation | Example |
|---------------|----------------|----------------|---------|
| Skill | `./` (root) | `skills` array with paths | `"skills": ["./clinical-trial-protocol-skill"]` |
| MCP Server | `./subdirectory` | `plugin.json` in subdirectory | `"source": "./icd10-codes"` |

Skills use inline source definitions where the marketplace.json directly specifies skill paths, while MCP Servers use subdirectory sources that contain separate plugin.json files with server URLs.

Sources: [.claude-plugin/marketplace.json:11-73](), [icd10-codes/.claude-plugin/plugin.json:1-15]()

## Component Inventory

The marketplace currently provides 3 Skills and 4 MCP Servers:

### Skills

| Plugin Name | Directory | Purpose | Requirements |
|------------|-----------|---------|--------------|
| `clinical-trial-protocol` | `clinical-trial-protocol-skill/` | Generate FDA/NIH-compliant clinical trial protocols | Python with scipy, numpy |
| `prior-auth-review` | `prior-auth-review-skill/` | Automate payer review of prior authorization requests | None |
| `fhir-developer` | `fhir-developer-skill/` | FHIR R4 API development guide with SMART authorization | None |

### MCP Servers

| Plugin Name | Directory | External URL | Purpose |
|------------|-----------|--------------|---------|
| `cms-coverage` | `cms-coverage/` | `https://mcp.deepsense.ai/cms_coverage/mcp` | Access CMS Coverage Database (LCDs/NCDs) |
| `npi-registry` | `npi-registry/` | `https://mcp.deepsense.ai/npi_registry/mcp` | Access US National Provider Identifier Registry |
| `pubmed` | `pubmed/` | `https://pubmed.mcp.claude.com/mcp` | Search biomedical literature from PubMed |
| `icd10-codes` | `icd10-codes/` | `https://mcp.deepsense.ai/icd10_codes/mcp` | Access ICD-10-CM and ICD-10-PCS code sets |

**Note:** MCP Servers are hosted on external infrastructure (DeepSense.ai and Claude infrastructure) and accessed via HTTPS endpoints defined in their respective `plugin.json` files.

Sources: [.claude-plugin/marketplace.json:11-73](), [README.md:18-58](), [icd10-codes/.claude-plugin/plugin.json:9-14]()

## User Installation Workflow

Users discover and install components through Claude Code commands that interact with the marketplace registry:

```mermaid
sequenceDiagram
    participant User
    participant ClaudeCode as "Claude Code Client"
    participant Marketplace as "marketplace.json"
    participant GitHub as "anthropics/healthcare repo"
    participant Skill as "SKILL.md files"
    participant MCP as "MCP Server plugin.json"
    
    User->>ClaudeCode: /plugin marketplace add anthropics/healthcare
    ClaudeCode->>GitHub: Clone repository
    ClaudeCode->>Marketplace: Read .claude-plugin/marketplace.json
    Marketplace-->>ClaudeCode: Return 7 plugin definitions
    
    User->>ClaudeCode: /plugin install fhir-developer@healthcare
    ClaudeCode->>Marketplace: Lookup fhir-developer plugin
    Marketplace-->>ClaudeCode: source: ./, skills: [./fhir-developer-skill]
    ClaudeCode->>Skill: Load fhir-developer-skill/SKILL.md
    Skill-->>ClaudeCode: Skill installed
    
    User->>ClaudeCode: claude mcp add-from-marketplace anthropics/healthcare/icd10-codes
    ClaudeCode->>Marketplace: Lookup icd10-codes plugin
    Marketplace-->>ClaudeCode: source: ./icd10-codes
    ClaudeCode->>MCP: Load icd10-codes/.claude-plugin/plugin.json
    MCP-->>ClaudeCode: mcpServers.ICD10 Codes.url
    ClaudeCode->>ClaudeCode: Configure MCP connection
```

**Installation Commands:**

```bash
# Add marketplace to Claude Code
/plugin marketplace add anthropics/healthcare

# Install individual skills
/plugin install clinical-trial-protocol@healthcare
/plugin install prior-auth-review@healthcare
/plugin install fhir-developer@healthcare

# Add MCP servers
claude mcp add-from-marketplace anthropics/healthcare/cms-coverage
claude mcp add-from-marketplace anthropics/healthcare/npi-registry
claude mcp add-from-marketplace anthropics/healthcare/pubmed
claude mcp add-from-marketplace anthropics/healthcare/icd10-codes
```

Sources: [README.md:6-58](), [.claude-plugin/marketplace.json:11-73](), [icd10-codes/.claude-plugin/plugin.json:9-14]()

## Quality Assurance Infrastructure

The repository includes automated CI/CD workflows that ensure skill quality and manage releases:

```mermaid
graph TB
    subgraph "GitHub Events"
        PR["<b>Pull Request</b><br/>opened/synchronize/reopened"]
        TAG["<b>Git Tag Push</b><br/>v* pattern"]
    end
    
    subgraph "claude-skill-review.yml"
        DSJ["<b>detect-skills job</b><br/>git diff origin/base...HEAD<br/>find SKILL.md files"]
        RSJ["<b>review-skill job</b><br/>matrix strategy<br/>anthropics/claude-code-action@v1"]
        
        DSJ -->|"outputs.skills<br/>outputs.has_skills"| RSJ
    end
    
    subgraph "release.yml"
        PKG["<b>release job</b><br/>Find *-skill/ directories<br/>Create zip archives"]
        GHR["<b>GitHub Release</b><br/>Attach *-skill-*.zip<br/>Draft release"]
        
        PKG --> GHR
    end
    
    PR -->|"triggers"| DSJ
    TAG -->|"triggers"| PKG
    
    RSJ -->|"posts feedback to"| PR
```

### Workflow Importance

| Workflow File | Importance Score | Primary Function |
|--------------|------------------|------------------|
| `claude-skill-review.yml` | 49.07 | Detects skill changes and runs Claude-powered reviews on each modified skill |
| `release.yml` | 1.08 | Packages skills into zip files and creates GitHub releases for distribution |

The `detect-skills` job uses git diff to identify changed files and locate `SKILL.md` files ([.github/workflows/claude-skill-review.yml:26-53]()), while the `review-skill` job employs a matrix strategy to parallelize reviews across multiple skills ([.github/workflows/claude-skill-review.yml:55-87]()). The release workflow scans for directories matching the `*-skill/` pattern and creates distributable packages ([.github/workflows/release.yml:18-42]()).

Sources: [.github/workflows/claude-skill-review.yml:1-88](), [.github/workflows/release.yml:1-43]()

## Plugin Categories and Tags

The marketplace organizes plugins using categories and tags for discoverability:

| Plugin | Category | Tags |
|--------|----------|------|
| `clinical-trial-protocol` | healthcare | clinical-trials, fda, protocol, regulatory |
| `prior-auth-review` | healthcare | prior-auth, insurance, medical-necessity, cms |
| `fhir-developer` | healthcare | fhir, hl7, api, interoperability, smart-on-fhir |
| `cms-coverage` | healthcare | medicare, coverage, cms, policy, ncd, lcd |
| `npi-registry` | healthcare | npi, provider, registry, hipaa |
| `pubmed` | healthcare | pubmed, literature, research, medical, pmc |
| `icd10-codes` | healthcare | icd-10, diagnosis, procedure, billing, medical-coding |

All components share the `healthcare` category, with tags providing fine-grained classification for search and filtering.

Sources: [.claude-plugin/marketplace.json:11-73]()

## Getting Started

To begin using the Healthcare Marketplace:

1. **Add the marketplace** to Claude Code to enable discovery of all 7 plugins
2. **Install skills** based on your workflow needs (clinical research, insurance, or API development)
3. **Configure MCP servers** to provide Skills with access to external healthcare data sources
4. **Invoke skills** through Claude Code to execute healthcare workflows

For detailed usage of individual components:
- Skills documentation: see [Healthcare Skills](#3)
- MCP Servers configuration: see [MCP Servers and External Data](#4)
- Contributing new components: see [Developer Guide](#6)

Sources: [README.md:1-63]()

---

# Page: Marketplace Architecture

# Marketplace Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [README.md](README.md)
- [cms-coverage/.claude-plugin/plugin.json](cms-coverage/.claude-plugin/plugin.json)
- [icd10-codes/.claude-plugin/plugin.json](icd10-codes/.claude-plugin/plugin.json)
- [npi-registry/.claude-plugin/plugin.json](npi-registry/.claude-plugin/plugin.json)
- [pubmed/.claude-plugin/plugin.json](pubmed/.claude-plugin/plugin.json)

</details>



## Purpose and Scope

This document explains the plugin system architecture that enables Skills and MCP Servers to be discovered, installed, and executed within Claude Code. It covers the structure of the marketplace registry, the plugin configuration patterns, and how the system resolves sources during installation.

For details on the distinction between Skills and MCP Servers as plugin types, see [Skills vs MCP Servers](#2.1). For end-user installation commands and workflows, see [Installation and Usage](#2.2).

---

## Plugin System Overview

The Healthcare Marketplace uses a **plugin architecture** where the `.claude-plugin/marketplace.json` file serves as the central registry. This registry catalogs all available plugins (both Skills and MCP Servers) and provides metadata for discovery and installation.

The architecture follows a three-tier model:

1. **Discovery Layer**: User-facing commands (`/plugin marketplace add`, `/plugin install`, `claude mcp add-from-marketplace`)
2. **Marketplace Layer**: Central registry at [`.claude-plugin/marketplace.json:1-74`]()
3. **Implementation Layer**: Actual skill directories and MCP plugin configurations

### Architecture Model

```mermaid
graph TB
    subgraph DiscoveryLayer["Discovery Layer"]
        UserCommands["User Commands<br/>/plugin marketplace add<br/>/plugin install<br/>claude mcp add-from-marketplace"]
    end
    
    subgraph MarketplaceLayer["Marketplace Layer"]
        Registry[".claude-plugin/marketplace.json<br/>Central Registry"]
        
        subgraph PluginEntries["Plugin Entries"]
            SkillPlugins["Skill Plugins<br/>source: './'<br/>skills: ['./path-to-skill']"]
            MCPPlugins["MCP Plugins<br/>source: './subdirectory'"]
        end
    end
    
    subgraph ImplementationLayer["Implementation Layer"]
        SkillDirs["Skill Directories<br/>clinical-trial-protocol-skill/<br/>prior-auth-review-skill/<br/>fhir-developer-skill/"]
        
        MCPConfigs["MCP Configurations<br/>cms-coverage/.claude-plugin/plugin.json<br/>npi-registry/.claude-plugin/plugin.json<br/>pubmed/.claude-plugin/plugin.json<br/>icd10-codes/.claude-plugin/plugin.json"]
    end
    
    subgraph ExternalServices["External Services"]
        DeepSense["mcp.deepsense.ai<br/>CMS, NPI, ICD-10 HTTP servers"]
        ClaudeInfra["pubmed.mcp.claude.com<br/>PubMed HTTP server"]
    end
    
    UserCommands --> Registry
    Registry --> PluginEntries
    SkillPlugins --> SkillDirs
    MCPPlugins --> MCPConfigs
    MCPConfigs --> DeepSense
    MCPConfigs --> ClaudeInfra
```

**Sources**: [`.claude-plugin/marketplace.json:1-74`](), [`README.md:7-58`]()

---

## Marketplace Registry Structure

The marketplace registry at `.claude-plugin/marketplace.json` contains three top-level sections:

| Field | Type | Purpose |
|-------|------|---------|
| `name` | string | Marketplace identifier used in commands (e.g., `healthcare`) |
| `owner` | object | Contact information with `name` and `email` fields |
| `metadata` | object | Version and description of the marketplace |
| `plugins` | array | List of all available plugin definitions |

Each plugin entry in the `plugins` array has the following structure:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Plugin identifier used in installation commands |
| `source` | string | Yes | Relative path to plugin implementation |
| `description` | string | Yes | Human-readable description |
| `category` | string | Yes | Classification (e.g., `healthcare`) |
| `tags` | string[] | Yes | Searchable keywords |
| `strict` | boolean | Skills only | Whether strict mode is enabled |
| `skills` | string[] | Skills only | Paths to skill directories |

### Plugin Entry Examples

The registry distinguishes between Skills and MCP Servers through the presence of the `skills` field:

**Skill Plugin Entry** (lines 12-22):
```json
{
  "name": "clinical-trial-protocol",
  "source": "./",
  "skills": ["./clinical-trial-protocol-skill"]
}
```

**MCP Server Plugin Entry** (lines 46-51):
```json
{
  "name": "cms-coverage",
  "source": "./cms-coverage"
}
```

Skills use `source: "./"` (repository root) and specify explicit skill paths in the `skills` array. MCP Servers use `source: "./subdirectory"` and omit the `skills` field, relying on a nested `plugin.json` file.

**Sources**: [`.claude-plugin/marketplace.json:1-74`]()

---

## Source Resolution Patterns

The marketplace implements two distinct source resolution patterns based on plugin type:

### Skill Source Resolution

```mermaid
graph LR
    MarketplaceEntry["marketplace.json<br/>name: 'clinical-trial-protocol'<br/>source: './'<br/>skills: ['./clinical-trial-protocol-skill']"]
    
    SourceRoot["Repository Root<br/>(current directory)"]
    
    SkillDir["clinical-trial-protocol-skill/<br/>SKILL.md<br/>references/<br/>scripts/"]
    
    MarketplaceEntry -->|"resolves source"| SourceRoot
    MarketplaceEntry -->|"resolves skills[0]"| SkillDir
```

When installing a skill:
1. The `source` field (typically `"./"`) is resolved relative to `marketplace.json`
2. Each entry in the `skills` array is resolved relative to the source path
3. The skill directory must contain a `SKILL.md` file defining the skill's capabilities

Example from [`.claude-plugin/marketplace.json:12-22`]():
- `name`: `"clinical-trial-protocol"`
- `source`: `"./"` → resolves to repository root
- `skills[0]`: `"./clinical-trial-protocol-skill"` → resolves to `clinical-trial-protocol-skill/` directory

### MCP Source Resolution

```mermaid
graph LR
    MarketplaceEntry["marketplace.json<br/>name: 'cms-coverage'<br/>source: './cms-coverage'"]
    
    MCPDir["cms-coverage/"]
    
    PluginJSON["cms-coverage/.claude-plugin/plugin.json<br/>mcpServers.type: 'http'<br/>mcpServers.url: 'https://...'"]
    
    ExternalServer["https://mcp.deepsense.ai/cms_coverage/mcp"]
    
    MarketplaceEntry -->|"resolves source"| MCPDir
    MCPDir -->|"reads configuration"| PluginJSON
    PluginJSON -->|"connects to"| ExternalServer
```

When installing an MCP Server:
1. The `source` field points to a subdirectory containing the MCP configuration
2. The system reads `.claude-plugin/plugin.json` within that subdirectory
3. The `plugin.json` specifies the HTTP endpoint for the external MCP server

Example from [`.claude-plugin/marketplace.json:46-51`]() and [`cms-coverage/.claude-plugin/plugin.json:1-15`]():
- Marketplace `source`: `"./cms-coverage"` → resolves to `cms-coverage/` directory
- Plugin config: `cms-coverage/.claude-plugin/plugin.json`
- MCP server URL: `"https://mcp.deepsense.ai/cms_coverage/mcp"`

**Sources**: [`.claude-plugin/marketplace.json:11-73`](), [`cms-coverage/.claude-plugin/plugin.json:1-15`](), [`npi-registry/.claude-plugin/plugin.json:1-15`](), [`pubmed/.claude-plugin/plugin.json:1-15`](), [`icd10-codes/.claude-plugin/plugin.json:1-15`]()

---

## MCP Plugin Configuration

MCP plugins use a separate `plugin.json` file within their source directory. This file follows a standard structure:

| Field | Type | Purpose |
|-------|------|---------|
| `name` | string | Plugin identifier (matches marketplace entry) |
| `version` | string | Semantic version |
| `description` | string | Detailed description of capabilities |
| `author` | object | Provider information (`name`, `url`) |
| `mcpServers` | object | Server definitions keyed by display name |

### MCP Server Definition

Each entry in the `mcpServers` object has:

| Field | Type | Value |
|-------|------|-------|
| `type` | string | Always `"http"` for remote servers |
| `url` | string | Full HTTPS endpoint for the MCP protocol |

### MCP Server Endpoints

```mermaid
graph TB
    subgraph LocalConfig["Local MCP Configurations"]
        CMS["cms-coverage/.claude-plugin/plugin.json"]
        NPI["npi-registry/.claude-plugin/plugin.json"]
        ICD["icd10-codes/.claude-plugin/plugin.json"]
        PM["pubmed/.claude-plugin/plugin.json"]
    end
    
    subgraph DeepSenseInfra["DeepSense.ai Infrastructure"]
        CMSEndpoint["https://mcp.deepsense.ai/cms_coverage/mcp"]
        NPIEndpoint["https://mcp.deepsense.ai/npi_registry/mcp"]
        ICDEndpoint["https://mcp.deepsense.ai/icd10_codes/mcp"]
    end
    
    subgraph ClaudeInfra["Anthropic Infrastructure"]
        PMEndpoint["https://pubmed.mcp.claude.com/mcp"]
    end
    
    CMS -->|"mcpServers.url"| CMSEndpoint
    NPI -->|"mcpServers.url"| NPIEndpoint
    ICD -->|"mcpServers.url"| ICDEndpoint
    PM -->|"mcpServers.url"| PMEndpoint
```

The marketplace hosts MCP servers from two external providers:

**DeepSense.ai Servers** (lines 10-12 in respective plugin.json files):
- CMS Coverage: `mcp.deepsense.ai/cms_coverage/mcp`
- NPI Registry: `mcp.deepsense.ai/npi_registry/mcp`
- ICD-10 Codes: `mcp.deepsense.ai/icd10_codes/mcp`

**Anthropic Servers** (lines 10-12 in pubmed plugin.json):
- PubMed: `pubmed.mcp.claude.com/mcp`

**Sources**: [`cms-coverage/.claude-plugin/plugin.json:1-15`](), [`npi-registry/.claude-plugin/plugin.json:1-15`](), [`pubmed/.claude-plugin/plugin.json:1-15`](), [`icd10-codes/.claude-plugin/plugin.json:1-15`]()

---

## Plugin Distribution and Packaging

The release workflow packages skills into distributable zip files when version tags are pushed to the repository.

### Release Workflow

```mermaid
graph LR
    TagPush["git push tag 'v*'"]
    
    DetectSkills["Scan *-skill/ directories"]
    
    CreateZips["Create {skill-name}-{version}.zip<br/>for each skill"]
    
    DraftRelease["Create GitHub Draft Release<br/>with zip artifacts"]
    
    TagPush -->|"triggers .github/workflows/release.yml"| DetectSkills
    DetectSkills --> CreateZips
    CreateZips --> DraftRelease
```

The workflow at [`.github/workflows/release.yml:1-43`]() performs the following steps:

1. **Skill Detection** (lines 20-29): Scans for directories matching `*-skill/` pattern
2. **Packaging** (lines 24-27): Creates zip file for each skill with format `{skill-name}-{tag}.zip`
3. **Release Creation** (lines 35-42): Attaches zip files to a draft GitHub Release

Example packaging logic from [`.github/workflows/release.yml:19-29`]():
```bash
for skill_dir in *-skill/; do
  skill_name="${skill_dir%/}"
  cd "$skill_name"
  zip -r "../${skill_name}-${GITHUB_REF_NAME}.zip" .
  cd ..
done
```

This produces artifacts like:
- `clinical-trial-protocol-skill-v1.0.0.zip`
- `prior-auth-review-skill-v1.0.0.zip`
- `fhir-developer-skill-v1.0.0.zip`

**Sources**: [`.github/workflows/release.yml:1-43`]()

---

## Marketplace Metadata

The marketplace registry includes version metadata and ownership information:

**Version Information** ([`.claude-plugin/marketplace.json:7-9`]()):
- `version`: `"1.0.0"` - Semantic version of the marketplace itself
- `description`: Brief description of the marketplace's purpose

**Owner Information** ([`.claude-plugin/marketplace.json:3-6`]()):
- `name`: `"Anthropic"` - Organization maintaining the marketplace
- `email`: `"support@anthropic.com"` - Support contact

**Marketplace Identifier** ([`.claude-plugin/marketplace.json:2`]()):
- `name`: `"healthcare"` - Used in commands like `/plugin marketplace add anthropics/healthcare`

The full marketplace reference format is `{github_org}/{marketplace_name}`, which resolves to the repository `https://github.com/anthropics/healthcare` and reads the marketplace registry from `.claude-plugin/marketplace.json`.

**Sources**: [`.claude-plugin/marketplace.json:1-10`](), [`README.md:8-9`]()

---

## Summary

The marketplace architecture implements a clear separation of concerns:

- **Marketplace Registry** (`.claude-plugin/marketplace.json`): Central catalog for discovery
- **Skill Plugins**: Self-contained in repository with inline source resolution
- **MCP Plugins**: Pointer configurations to external HTTP services
- **Release Workflow**: Automated packaging of skills into distributable artifacts

This design enables modular plugin distribution where skills are versioned and packaged locally, while MCP servers remain as lightweight configuration wrappers around external data services.

---

# Page: Skills vs MCP Servers

# Skills vs MCP Servers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [README.md](README.md)
- [cms-coverage/.claude-plugin/plugin.json](cms-coverage/.claude-plugin/plugin.json)
- [icd10-codes/.claude-plugin/plugin.json](icd10-codes/.claude-plugin/plugin.json)
- [npi-registry/.claude-plugin/plugin.json](npi-registry/.claude-plugin/plugin.json)
- [pubmed/.claude-plugin/plugin.json](pubmed/.claude-plugin/plugin.json)

</details>



## Purpose and Scope

This document clarifies the architectural distinction between **Skills** and **MCP Servers** in the Healthcare Marketplace. Skills are AI-powered capabilities that extend Claude's functionality for specific healthcare workflows, while MCP Servers are external data connectors that provide access to healthcare databases and APIs. Understanding this separation is critical for developers contributing to the marketplace and users deciding which components to install.

For information about installing these components, see [Installation and Usage](#2.2). For detailed documentation of individual skills, see [Healthcare Skills](#3). For MCP server details, see [MCP Servers and External Data](#4).

## Core Distinction

Skills and MCP Servers serve fundamentally different roles in the Healthcare Marketplace architecture:

| Aspect | Skills | MCP Servers |
|--------|--------|-------------|
| **Purpose** | Provide AI-powered capabilities and workflows | Expose external data sources and APIs |
| **Execution** | Run as Claude Code skills within Claude's environment | Run as HTTP services on external infrastructure |
| **Primary Content** | Instructions, prompts, reference documents, scripts | API endpoint configurations and connection metadata |
| **Installation Command** | `/plugin install <name>@healthcare` | `claude mcp add-from-marketplace anthropics/healthcare/<name>` |
| **Configuration File** | `SKILL.md` in skill directory | `plugin.json` in MCP subdirectory |
| **Source Pattern** | Inline (`"source": "./"`) with explicit skill paths | Subdirectory (`"source": "./subdirectory"`) |
| **Dependencies** | Can depend on MCP servers for data access | Independent, no dependencies |
| **Hosting Location** | Code files in this repository | External services (DeepSense.ai, Claude infrastructure) |

**Sources:** [.claude-plugin/marketplace.json:1-74](), [README.md:1-63]()

## Configuration Architecture

### Skills Configuration Pattern

Skills use a two-level configuration structure. The marketplace registry points to skill directories, which contain `SKILL.md` files defining the AI capabilities.

```mermaid
graph TB
    subgraph "Marketplace Registry"
        MKT["marketplace.json<br/>(.claude-plugin/)"]
    end
    
    subgraph "Skill Plugin Entry"
        ENTRY["Plugin Object"]
        NAME["name: 'clinical-trial-protocol'"]
        SOURCE["source: './'"]
        SKILLS["skills: ['./clinical-trial-protocol-skill']"]
        
        ENTRY --> NAME
        ENTRY --> SOURCE
        ENTRY --> SKILLS
    end
    
    subgraph "Skill Implementation"
        DIR["clinical-trial-protocol-skill/"]
        SKILL_MD["SKILL.md<br/>(instructions & prompts)"]
        REF["references/<br/>(knowledge base)"]
        SCRIPTS["scripts/<br/>(utilities)"]
        
        DIR --> SKILL_MD
        DIR --> REF
        DIR --> SCRIPTS
    end
    
    MKT --> ENTRY
    SKILLS --> DIR
    
    style MKT fill:#f9f9f9
    style ENTRY fill:#fff4e1
    style DIR fill:#e1f5ff
```

**Diagram: Skill Configuration Structure**

The marketplace entry for the `clinical-trial-protocol` skill demonstrates this pattern:

```json
{
  "name": "clinical-trial-protocol",
  "source": "./",
  "description": "Generate FDA/NIH-compliant clinical trial protocols...",
  "category": "healthcare",
  "tags": ["clinical-trials", "fda", "protocol", "regulatory"],
  "strict": false,
  "skills": [
    "./clinical-trial-protocol-skill"
  ]
}
```

**Sources:** [.claude-plugin/marketplace.json:12-22]()

Key characteristics:
- **Inline Source**: The `"source": "./"` field indicates the skill code is in the same repository
- **Skills Array**: The `"skills"` field explicitly lists directories containing `SKILL.md` files
- **No URL**: Skills have no external endpoint configuration
- **Local Execution**: All skill logic runs within Claude Code's environment

### MCP Server Configuration Pattern

MCP Servers use a three-level configuration structure. The marketplace points to subdirectories, which contain `plugin.json` files defining HTTP endpoints.

```mermaid
graph TB
    subgraph "Marketplace Registry"
        MKT2["marketplace.json<br/>(.claude-plugin/)"]
    end
    
    subgraph "MCP Plugin Entry"
        ENTRY2["Plugin Object"]
        NAME2["name: 'cms-coverage'"]
        SOURCE2["source: './cms-coverage'"]
        NO_SKILLS["No 'skills' field"]
        
        ENTRY2 --> NAME2
        ENTRY2 --> SOURCE2
        ENTRY2 --> NO_SKILLS
    end
    
    subgraph "MCP Implementation"
        SUBDIR["cms-coverage/"]
        PLUGIN_DIR[".claude-plugin/"]
        PLUGIN_JSON["plugin.json"]
        MCP_CONFIG["mcpServers:<br/>{type: 'http',<br/>url: 'https://...' }"]
        
        SUBDIR --> PLUGIN_DIR
        PLUGIN_DIR --> PLUGIN_JSON
        PLUGIN_JSON --> MCP_CONFIG
    end
    
    subgraph "External Service"
        EXT["DeepSense.ai Infrastructure<br/>https://mcp.deepsense.ai/cms_coverage/mcp"]
    end
    
    MKT2 --> ENTRY2
    SOURCE2 --> SUBDIR
    MCP_CONFIG -.->|"HTTP requests"| EXT
    
    style MKT2 fill:#f9f9f9
    style ENTRY2 fill:#e1ffe1
    style SUBDIR fill:#e1f5ff
    style EXT fill:#ffe1e1
```

**Diagram: MCP Server Configuration Structure**

The marketplace entry for the `cms-coverage` MCP server demonstrates this pattern:

```json
{
  "name": "cms-coverage",
  "source": "./cms-coverage",
  "description": "Access the CMS Coverage Database",
  "category": "healthcare",
  "tags": ["medicare", "coverage", "cms", "policy", "ncd", "lcd"]
}
```

The corresponding `plugin.json` file in the subdirectory:

```json
{
  "name": "cms-coverage",
  "version": "1.0.0",
  "description": "The CMS Coverage Connector gives Claude access to Medicare Part B coverage policies...",
  "author": {
    "name": "deepsense.ai",
    "url": "https://deepsense.ai"
  },
  "mcpServers": {
    "CMS Coverage": {
      "type": "http",
      "url": "https://mcp.deepsense.ai/cms_coverage/mcp"
    }
  }
}
```

**Sources:** [.claude-plugin/marketplace.json:45-51](), [cms-coverage/.claude-plugin/plugin.json:1-15]()

Key characteristics:
- **Subdirectory Source**: The `"source": "./cms-coverage"` field points to a subdirectory
- **No Skills Field**: MCP entries omit the `"skills"` array entirely
- **External URL**: The `plugin.json` file contains `mcpServers` with HTTP endpoints
- **Remote Execution**: Data access happens via HTTP requests to external services

## Complete Marketplace Registry Structure

The following diagram maps all plugins in the marketplace registry, showing the clear separation between Skills and MCP Servers:

```mermaid
graph TB
    subgraph "marketplace.json"
        MP["Healthcare Marketplace"]
    end
    
    subgraph "Skills (source: './')"
        CTP["clinical-trial-protocol<br/>skills: ['./clinical-trial-protocol-skill']"]
        PAR["prior-auth-review<br/>skills: ['./prior-auth-review-skill']"]
        FHIR["fhir-developer<br/>skills: ['./fhir-developer-skill']"]
    end
    
    subgraph "MCP Servers (source: './subdir')"
        CMS["cms-coverage<br/>source: './cms-coverage'"]
        NPI["npi-registry<br/>source: './npi-registry'"]
        PM["pubmed<br/>source: './pubmed'"]
        ICD["icd10-codes<br/>source: './icd10-codes'"]
    end
    
    subgraph "Implementation Files"
        CTP_DIR["clinical-trial-protocol-skill/<br/>SKILL.md + references/ + scripts/"]
        PAR_DIR["prior-auth-review-skill/<br/>SKILL.md + assets/"]
        FHIR_DIR["fhir-developer-skill/<br/>SKILL.md + references/ + scripts/"]
        
        CMS_JSON["cms-coverage/.claude-plugin/plugin.json<br/>url: mcp.deepsense.ai/cms_coverage"]
        NPI_JSON["npi-registry/.claude-plugin/plugin.json<br/>url: mcp.deepsense.ai/npi_registry"]
        PM_JSON["pubmed/.claude-plugin/plugin.json<br/>url: pubmed.mcp.claude.com"]
        ICD_JSON["icd10-codes/.claude-plugin/plugin.json<br/>url: mcp.deepsense.ai/icd10_codes"]
    end
    
    MP --> CTP
    MP --> PAR
    MP --> FHIR
    MP --> CMS
    MP --> NPI
    MP --> PM
    MP --> ICD
    
    CTP --> CTP_DIR
    PAR --> PAR_DIR
    FHIR --> FHIR_DIR
    
    CMS --> CMS_JSON
    NPI --> NPI_JSON
    PM --> PM_JSON
    ICD --> ICD_JSON
    
    style MP fill:#f9f9f9
    style CTP fill:#fff4e1
    style PAR fill:#fff4e1
    style FHIR fill:#fff4e1
    style CMS fill:#e1ffe1
    style NPI fill:#e1ffe1
    style PM fill:#e1ffe1
    style ICD fill:#e1ffe1
```

**Diagram: Complete Marketplace Plugin Registry**

**Sources:** [.claude-plugin/marketplace.json:11-73]()

## Installation and Discovery Workflow

Skills and MCP Servers use different commands for installation, reflecting their distinct execution models:

### Skills Installation

```bash
# Add marketplace to Claude Code
/plugin marketplace add anthropics/healthcare

# Install a skill
/plugin install clinical-trial-protocol@healthcare
/plugin install prior-auth-review@healthcare
/plugin install fhir-developer@healthcare
```

When installing a skill:
1. Claude Code reads the marketplace registry at `.claude-plugin/marketplace.json`
2. Locates the plugin entry with matching `name`
3. Resolves the `"source": "./"` to the repository root
4. Loads each directory listed in the `skills` array
5. Reads the `SKILL.md` file to understand the skill's capabilities
6. Makes the skill available for activation during conversations

**Sources:** [README.md:7-15](), [.claude-plugin/marketplace.json:12-43]()

### MCP Server Installation

```bash
# Add MCP servers from the marketplace
claude mcp add-from-marketplace anthropics/healthcare/cms-coverage
claude mcp add-from-marketplace anthropics/healthcare/npi-registry
claude mcp add-from-marketplace anthropics/healthcare/pubmed
claude mcp add-from-marketplace anthropics/healthcare/icd10-codes
```

When installing an MCP server:
1. Claude Code reads the marketplace registry at `.claude-plugin/marketplace.json`
2. Locates the plugin entry with matching `name`
3. Resolves the `"source"` to the subdirectory (e.g., `./cms-coverage`)
4. Reads the `plugin.json` file in the subdirectory's `.claude-plugin/` folder
5. Extracts the `mcpServers` configuration with HTTP endpoint URLs
6. Configures the MCP client to make HTTP requests to the external service
7. Makes the MCP server's tools available to Claude

**Sources:** [README.md:52-58](), [cms-coverage/.claude-plugin/plugin.json:9-14](), [npi-registry/.claude-plugin/plugin.json:9-14](), [pubmed/.claude-plugin/plugin.json:9-14](), [icd10-codes/.claude-plugin/plugin.json:9-14]()

## How Skills and MCP Servers Complement Each Other

Skills frequently depend on MCP Servers to access external data, creating a composition pattern where AI capabilities leverage data connectors:

```mermaid
graph LR
    subgraph "Skills (AI Capabilities)"
        CTP_SKILL["clinical-trial-protocol-skill<br/>(Generate protocols)"]
        PAR_SKILL["prior-auth-review-skill<br/>(Review auth requests)"]
    end
    
    subgraph "MCP Servers (Data Access)"
        PM_MCP["PubMed MCP<br/>(Biomedical literature)"]
        CMS_MCP["CMS Coverage MCP<br/>(Medicare policies)"]
        NPI_MCP["NPI Registry MCP<br/>(Provider lookup)"]
        ICD_MCP["ICD-10 Codes MCP<br/>(Diagnosis codes)"]
    end
    
    CTP_SKILL -->|"Research phase:<br/>search literature"| PM_MCP
    
    PAR_SKILL -->|"Validate provider"| NPI_MCP
    PAR_SKILL -->|"Check coverage"| CMS_MCP
    PAR_SKILL -->|"Validate diagnosis"| ICD_MCP
    
    style CTP_SKILL fill:#fff4e1
    style PAR_SKILL fill:#fff4e1
    style PM_MCP fill:#e1ffe1
    style CMS_MCP fill:#e1ffe1
    style NPI_MCP fill:#e1ffe1
    style ICD_MCP fill:#e1ffe1
```

**Diagram: Skill-MCP Dependency Patterns**

### Dependency Examples

**Clinical Trial Protocol Skill** uses PubMed MCP:
- Step 1 (Research phase) searches PubMed for relevant clinical studies
- The skill provides protocol generation logic
- The MCP provides access to 35+ million biomedical citations

**Prior Authorization Review Skill** uses three MCP servers:
- NPI Registry MCP validates healthcare provider credentials
- ICD-10 Codes MCP validates diagnosis codes
- CMS Coverage MCP checks Medicare coverage policies
- The skill provides the review workflow and decision logic
- The MCPs provide the authoritative data sources

**FHIR Developer Skill** is self-contained:
- Contains knowledge base in `references/` directory
- Includes scaffolding script in `scripts/setup_fhir_project.py`
- Does not depend on any MCP servers
- Demonstrates that skills can function independently

**Sources:** [README.md:19-43](), High-Level System Architecture Diagrams (Diagram 3)

## Technical Implementation Differences

### Skills: File-Based Knowledge and Code

Skills are implemented as directories containing:

```
clinical-trial-protocol-skill/
├── SKILL.md                          # Main skill definition
├── references/                        # Knowledge base
│   ├── FDA-Clinical-Protocol-Template.md
│   ├── clinical-trials-gov-schema.md
│   └── statistical-methods.md
└── scripts/                           # Utility scripts
    └── sample_size_calculator.py
```

The `SKILL.md` file contains:
- Natural language instructions for Claude
- Workflow steps and decision trees
- Reference document pointers
- Script execution patterns
- Human-in-the-loop requirements

### MCP Servers: HTTP Endpoint Configurations

MCP servers are implemented as configuration files:

```
cms-coverage/
└── .claude-plugin/
    └── plugin.json                    # HTTP endpoint config
```

The `plugin.json` file contains:
- Server name and version metadata
- Author information
- `mcpServers` object with:
  - `type`: Always `"http"` for remote servers
  - `url`: Full HTTPS endpoint (e.g., `https://mcp.deepsense.ai/cms_coverage/mcp`)

**Sources:** [cms-coverage/.claude-plugin/plugin.json:1-15](), [npi-registry/.claude-plugin/plugin.json:1-15](), [pubmed/.claude-plugin/plugin.json:1-15](), [icd10-codes/.claude-plugin/plugin.json:1-15]()

## MCP Server HTTP Endpoints

The Healthcare Marketplace integrates with two external MCP hosting providers:

| MCP Server | URL | Provider | Purpose |
|------------|-----|----------|---------|
| CMS Coverage | `https://mcp.deepsense.ai/cms_coverage/mcp` | DeepSense.ai | Medicare policies |
| NPI Registry | `https://mcp.deepsense.ai/npi_registry/mcp` | DeepSense.ai | Provider lookups |
| ICD-10 Codes | `https://mcp.deepsense.ai/icd10_codes/mcp` | DeepSense.ai | Diagnosis codes |
| PubMed | `https://pubmed.mcp.claude.com/mcp` | Anthropic | Literature search |

These URLs are embedded in the respective `plugin.json` files and represent live HTTP services that Claude's MCP client communicates with at runtime.

**Sources:** [cms-coverage/.claude-plugin/plugin.json:12](), [npi-registry/.claude-plugin/plugin.json:12](), [icd10-codes/.claude-plugin/plugin.json:12](), [pubmed/.claude-plugin/plugin.json:12]()

## Release and Distribution

Skills and MCP Servers follow different release workflows:

### Skills: Packaged as Artifacts

The release workflow packages skills into distributable zip files:

```yaml
- name: Create skill zip files
  run: |
    for skill_dir in *-skill/; do
      if [ -d "$skill_dir" ]; then
        skill_name="${skill_dir%/}"
        echo "Packaging $skill_name..."
        cd "$skill_name"
        zip -r "../${skill_name}-${GITHUB_REF_NAME}.zip" .
        cd ..
      fi
    done
```

This creates artifacts like:
- `clinical-trial-protocol-skill-v1.0.0.zip`
- `prior-auth-review-skill-v1.0.0.zip`
- `fhir-developer-skill-v1.0.0.zip`

**Sources:** [.github/workflows/release.yml:18-29]()

### MCP Servers: Configuration-Only Distribution

MCP servers are not packaged as artifacts. Their distribution consists of:
1. The `plugin.json` configuration file in the repository
2. The external HTTP service (already running on DeepSense.ai or Anthropic infrastructure)

When users install an MCP server, they receive the connection configuration, not the server code itself. The actual MCP server implementation runs on external infrastructure and is maintained separately from this repository.

**Sources:** [.github/workflows/release.yml:1-43]() (note: only packages `*-skill/` directories, not MCP subdirectories)

## Summary

| Characteristic | Skills | MCP Servers |
|----------------|--------|-------------|
| **Definition** | AI-powered workflows and capabilities | External data connectors |
| **Registry Entry** | `"source": "./"` with `"skills"` array | `"source": "./subdirectory"` without skills |
| **Configuration** | `SKILL.md` in skill directory | `plugin.json` with `mcpServers` object |
| **Content** | Instructions, reference docs, scripts | HTTP endpoint URLs |
| **Execution** | Runs in Claude Code environment | HTTP requests to external services |
| **Installation** | `/plugin install <name>@healthcare` | `claude mcp add-from-marketplace` |
| **Dependencies** | May depend on MCP servers | Independent |
| **Distribution** | Zip files in GitHub releases | Configuration only |
| **Examples** | `clinical-trial-protocol`, `prior-auth-review`, `fhir-developer` | `cms-coverage`, `npi-registry`, `pubmed`, `icd10-codes` |

This architectural separation enables modular healthcare workflows where AI capabilities (Skills) compose external data sources (MCP Servers) without tight coupling.

**Sources:** [.claude-plugin/marketplace.json:1-74](), [README.md:1-63](), all MCP `plugin.json` files

---

# Page: Installation and Usage

# Installation and Usage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [README.md](README.md)
- [icd10-codes/.claude-plugin/plugin.json](icd10-codes/.claude-plugin/plugin.json)

</details>



This document explains the commands and workflows for installing and using the Healthcare Marketplace in Claude Code. It covers adding the marketplace registry, installing skills, and configuring MCP servers.

For the distinction between Skills and MCP Servers, see [Skills vs MCP Servers](#2.1). For detailed documentation of individual skills, see [Healthcare Skills](#3). For MCP server specifics, see [MCP Servers and External Data](#4).

---

## Installation Overview

The Healthcare Marketplace follows a three-stage installation pattern: (1) add the marketplace registry, (2) install skills, and (3) configure MCP servers. Each stage uses distinct commands and modifies different parts of the Claude Code environment.

```mermaid
flowchart LR
    subgraph "Stage 1: Marketplace Registry"
        CMD1["/plugin marketplace add<br/>anthropics/healthcare"]
        REG["Registers marketplace:<br/>.claude-plugin/marketplace.json"]
        CMD1 --> REG
    end
    
    subgraph "Stage 2: Skill Installation"
        CMD2["/plugin install<br/>&lt;skill-name&gt;@healthcare"]
        SKILL_FILES["Loads skill directory:<br/>*-skill/SKILL.md<br/>*-skill/references/<br/>*-skill/scripts/"]
        CMD2 --> SKILL_FILES
    end
    
    subgraph "Stage 3: MCP Configuration"
        CMD3["claude mcp add-from-marketplace<br/>anthropics/healthcare/&lt;mcp-name&gt;"]
        MCP_FILES["Configures MCP endpoint:<br/>*/.claude-plugin/plugin.json<br/>mcpServers.url"]
        CMD3 --> MCP_FILES
    end
    
    REG -.->|"enables"| CMD2
    REG -.->|"enables"| CMD3
```

**Installation Flow Stages**

Sources: [README.md:7-58](), [.claude-plugin/marketplace.json:1-74]()

---

## Adding the Marketplace

The marketplace must be registered before any skills or MCP servers can be installed. This command downloads the marketplace registry from the repository.

```bash
/plugin marketplace add anthropics/healthcare
```

This command:
- Fetches [.claude-plugin/marketplace.json:1-74]() from the `anthropics/healthcare` repository
- Registers seven plugins: three skills and four MCP servers
- Makes the `@healthcare` namespace available for plugin installation

The marketplace registry defines all available plugins with their metadata:

| Plugin Name | Type | Description | Plugin ID |
|------------|------|-------------|-----------|
| `clinical-trial-protocol` | Skill | FDA/NIH-compliant clinical trial protocols | `clinical-trial-protocol@healthcare` |
| `prior-auth-review` | Skill | Prior authorization request review | `prior-auth-review@healthcare` |
| `fhir-developer` | Skill | FHIR R4 API development guide | `fhir-developer@healthcare` |
| `cms-coverage` | MCP | CMS Coverage Database access | `anthropics/healthcare/cms-coverage` |
| `npi-registry` | MCP | National Provider Identifier lookup | `anthropics/healthcare/npi-registry` |
| `pubmed` | MCP | PubMed biomedical literature search | `anthropics/healthcare/pubmed` |
| `icd10-codes` | MCP | ICD-10-CM/PCS code lookups | `anthropics/healthcare/icd10-codes` |

Sources: [.claude-plugin/marketplace.json:11-73](), [README.md:7-9]()

---

## Installing Skills

Skills are installed individually using the `/plugin install` command with the skill's plugin ID and marketplace namespace.

### Syntax

```bash
/plugin install <skill-name>@healthcare
```

The `@healthcare` suffix references the marketplace added in the previous step. The `<skill-name>` must match one of the skill plugin names in [.claude-plugin/marketplace.json:13-43]().

### Available Skills

```bash
# Install FHIR Developer skill
/plugin install fhir-developer@healthcare

# Install Prior Authorization Review skill
/plugin install prior-auth-review@healthcare

# Install Clinical Trial Protocol Generator skill
/plugin install clinical-trial-protocol@healthcare
```

### Skill Installation Mapping

```mermaid
flowchart TD
    subgraph "marketplace.json Skill Entries"
        E1["plugins[0]:<br/>name: clinical-trial-protocol<br/>skills: [./clinical-trial-protocol-skill]"]
        E2["plugins[1]:<br/>name: prior-auth-review<br/>skills: [./prior-auth-review-skill]"]
        E3["plugins[2]:<br/>name: fhir-developer<br/>skills: [./fhir-developer-skill]"]
    end
    
    subgraph "Repository File Structure"
        D1["clinical-trial-protocol-skill/<br/>SKILL.md<br/>references/<br/>scripts/sample_size_calculator.py"]
        D2["prior-auth-review-skill/<br/>SKILL.md<br/>assets/"]
        D3["fhir-developer-skill/<br/>SKILL.md<br/>references/<br/>scripts/setup_fhir_project.py"]
    end
    
    subgraph "Claude Code Environment"
        S1["Skill: clinical-trial-protocol<br/>Waypoint-based protocol generation"]
        S2["Skill: prior-auth-review<br/>Two-subskill PA review"]
        S3["Skill: fhir-developer<br/>FHIR R4 knowledge + scaffolding"]
    end
    
    E1 -->|"source: ./<br/>resolves to"| D1
    E2 -->|"source: ./<br/>resolves to"| D2
    E3 -->|"source: ./<br/>resolves to"| D3
    
    D1 --> S1
    D2 --> S2
    D3 --> S3
```

**Skill Installation File Resolution**

The `source: ./` field in [.claude-plugin/marketplace.json:14]() indicates skills are located at the repository root. The `skills` array ([.claude-plugin/marketplace.json:19-21]()) specifies the relative path to each skill directory.

Sources: [.claude-plugin/marketplace.json:11-43](), [README.md:10-15]()

---

## Configuring MCP Servers

MCP servers provide external data access and must be configured separately using the `claude mcp` command. Unlike skills, MCP servers connect to HTTP endpoints rather than loading local code.

### Syntax

```bash
claude mcp add-from-marketplace anthropics/healthcare/<mcp-name>
```

### Available MCP Servers

```bash
# CMS Coverage Database
claude mcp add-from-marketplace anthropics/healthcare/cms-coverage

# NPI Registry
claude mcp add-from-marketplace anthropics/healthcare/npi-registry

# PubMed Literature
claude mcp add-from-marketplace anthropics/healthcare/pubmed

# ICD-10 Codes
claude mcp add-from-marketplace anthropics/healthcare/icd10-codes
```

### MCP Server Configuration Structure

```mermaid
flowchart LR
    subgraph "marketplace.json MCP Entries"
        M1["plugins[3]:<br/>name: cms-coverage<br/>source: ./cms-coverage"]
        M2["plugins[4]:<br/>name: npi-registry<br/>source: ./npi-registry"]
        M3["plugins[5]:<br/>name: pubmed<br/>source: ./pubmed"]
        M4["plugins[6]:<br/>name: icd10-codes<br/>source: ./icd10-codes"]
    end
    
    subgraph "plugin.json Files"
        P1["cms-coverage/.claude-plugin/plugin.json<br/>mcpServers.type: http<br/>url: mcp.deepsense.ai/cms_coverage/mcp"]
        P2["npi-registry/.claude-plugin/plugin.json<br/>mcpServers.type: http<br/>url: mcp.deepsense.ai/npi_registry/mcp"]
        P3["pubmed/.claude-plugin/plugin.json<br/>mcpServers.type: http<br/>url: pubmed.mcp.claude.com/mcp"]
        P4["icd10-codes/.claude-plugin/plugin.json<br/>mcpServers.type: http<br/>url: mcp.deepsense.ai/icd10_codes/mcp"]
    end
    
    subgraph "External Endpoints"
        E1["DeepSense.ai Infrastructure:<br/>CMS Coverage API"]
        E2["DeepSense.ai Infrastructure:<br/>NPI Registry API"]
        E3["Claude Infrastructure:<br/>PubMed API"]
        E4["DeepSense.ai Infrastructure:<br/>ICD-10 API"]
    end
    
    M1 --> P1
    M2 --> P2
    M3 --> P3
    M4 --> P4
    
    P1 -.->|"HTTPS"| E1
    P2 -.->|"HTTPS"| E2
    P3 -.->|"HTTPS"| E3
    P4 -.->|"HTTPS"| E4
```

**MCP Server Configuration Resolution**

MCP entries in [.claude-plugin/marketplace.json:45-73]() use subdirectory sources (e.g., `./cms-coverage`). Each subdirectory contains a `plugin.json` file that specifies the HTTP endpoint. For example, [icd10-codes/.claude-plugin/plugin.json:9-14]() defines the `mcpServers` object with `type: http` and the external URL.

Sources: [.claude-plugin/marketplace.json:45-73](), [icd10-codes/.claude-plugin/plugin.json:1-15](), [README.md:52-58]()

---

## MCP Server Endpoints Reference

| MCP Name | Provider | Endpoint URL | Purpose |
|----------|----------|--------------|---------|
| `cms-coverage` | DeepSense.ai | `https://mcp.deepsense.ai/cms_coverage/mcp` | Medicare Local/National Coverage Determinations |
| `npi-registry` | DeepSense.ai | `https://mcp.deepsense.ai/npi_registry/mcp` | Healthcare provider validation |
| `pubmed` | Claude Infrastructure | `https://pubmed.mcp.claude.com/mcp` | Biomedical literature search |
| `icd10-codes` | DeepSense.ai | `https://mcp.deepsense.ai/icd10_codes/mcp` | Diagnosis/procedure code lookups |

Sources: [README.md:46-51](), [icd10-codes/.claude-plugin/plugin.json:9-14]()

---

## Skill Requirements

Some skills have external dependencies that must be installed separately:

| Skill | Requirements | Installation |
|-------|--------------|--------------|
| `fhir-developer` | None | No additional setup |
| `prior-auth-review` | None | No additional setup |
| `clinical-trial-protocol` | Python with `scipy` and `numpy` | `pip install scipy numpy` |

The Clinical Trial Protocol Generator requires Python dependencies for the sample size calculator script ([clinical-trial-protocol-skill/scripts/sample_size_calculator.py]()). See [Sample Size Calculator](#3.1.2) for details.

Sources: [README.md:19-42]()

---

## Complete Installation Example

Below is a complete workflow for installing the marketplace, all skills, and all MCP servers:

```bash
# Step 1: Add marketplace
/plugin marketplace add anthropics/healthcare

# Step 2: Install all skills
/plugin install fhir-developer@healthcare
/plugin install prior-auth-review@healthcare
/plugin install clinical-trial-protocol@healthcare

# Step 3: Configure all MCP servers
claude mcp add-from-marketplace anthropics/healthcare/cms-coverage
claude mcp add-from-marketplace anthropics/healthcare/npi-registry
claude mcp add-from-marketplace anthropics/healthcare/pubmed
claude mcp add-from-marketplace anthropics/healthcare/icd10-codes

# Step 4: Install Python dependencies for Clinical Trial Protocol
pip install scipy numpy
```

Sources: [README.md:7-58]()

---

## Verification

After installation, skills appear in Claude Code's skill menu and can be invoked during conversations. MCP servers appear in the MCP server list and are accessible via tool calls.

To verify skill installation:
- Check that skill names appear in the `/plugin list` output
- Attempt to invoke a skill during a conversation

To verify MCP configuration:
- Check that MCP servers appear in the MCP server list
- Skills that depend on MCP servers (e.g., Prior Authorization Review using `cms-coverage`) should function correctly

Sources: [README.md:7-58]()

---

## Uninstallation

Skills can be removed using:
```bash
/plugin uninstall <skill-name>@healthcare
```

MCP servers can be removed using:
```bash
claude mcp remove <mcp-name>
```

The marketplace itself can be removed using:
```bash
/plugin marketplace remove anthropics/healthcare
```

Note: Removing the marketplace does not automatically uninstall skills or MCP servers that were already installed from it.

Sources: [README.md:7-58]()

---

# Page: Healthcare Skills

# Healthcare Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [README.md](README.md)
- [clinical-trial-protocol-skill/README.md](clinical-trial-protocol-skill/README.md)
- [icd10-codes/.claude-plugin/plugin.json](icd10-codes/.claude-plugin/plugin.json)
- [prior-auth-review-skill/README.md](prior-auth-review-skill/README.md)

</details>



## Purpose and Scope

This document provides an overview of the three healthcare skills available in the marketplace: Clinical Trial Protocol Generator, Prior Authorization Review, and FHIR Developer Guide. It explains their respective domains, architectural patterns, and when to use each skill.

For detailed information about the marketplace architecture and installation procedures, see [Marketplace Architecture](#2). For comprehensive documentation of each individual skill's workflow and features, see subsections [Clinical Trial Protocol Generator](#3.1), [Prior Authorization Review](#3.2), and [FHIR Developer Guide](#3.3). For information about the external data sources these skills use, see [MCP Servers and External Data](#4).

## What are Skills?

Skills are Claude AI capabilities that provide specialized domain knowledge and workflow automation. Unlike MCP Servers (which provide external data access), skills embed instructions, reference materials, and multi-step workflows directly into Claude's context. Each skill is:

- **Self-contained**: Contains all necessary instructions, templates, and reference materials in its directory
- **Declarative**: Defined by a `SKILL.md` file that Claude reads to understand capabilities
- **Composable**: Can invoke MCP servers for external data access
- **Version-controlled**: Distributed as packaged artifacts via GitHub releases

Skills are registered in [.claude-plugin/marketplace.json:11-44]() and installed using `/plugin install <skill-name>@healthcare` commands.

**Sources:** [.claude-plugin/marketplace.json:1-74](), [README.md:1-63]()

## The Three Healthcare Skills

### Clinical Trial Protocol Generator

**Plugin ID:** `clinical-trial-protocol@healthcare`

**Domain:** Clinical research and regulatory affairs

**Use Case:** Generate FDA/NIH-compliant clinical trial protocols for medical devices (IDE pathway) or drugs (IND pathway). Supports Phase 2 and Phase 3 trials with statistical power analysis and research-driven protocol development.

**Architecture:** Waypoint-based pipeline with 6 sequential steps (00-initialize through 05-generate)

**Dependencies:** Python with `scipy` and `numpy`, ClinicalTrials.gov MCP Server, WebSearch

**Sources:** [README.md:37-42](), [clinical-trial-protocol-skill/README.md:1-55](), [.claude-plugin/marketplace.json:12-22]()

### Prior Authorization Review

**Plugin ID:** `prior-auth-review@healthcare`

**Domain:** Insurance and medical billing

**Use Case:** Automate health insurance payer review of prior authorization requests. Validates medical necessity against coverage policies and generates draft authorization decisions for human review.

**Architecture:** Two-subskill pattern with mandatory human decision gates between assessment and finalization

**Dependencies:** NPI Registry MCP, ICD-10 Codes MCP, CMS Coverage MCP, WebFetch for CPT code validation

**Sources:** [README.md:28-34](), [prior-auth-review-skill/README.md:1-78](), [.claude-plugin/marketplace.json:23-33]()

### FHIR Developer Guide

**Plugin ID:** `fhir-developer@healthcare`

**Domain:** Healthcare interoperability and API development

**Use Case:** Build FHIR R4-compliant healthcare APIs with specialized knowledge of resource structures, coding systems (LOINC, SNOMED CT, RxNorm), SMART on FHIR authorization, and validation patterns.

**Architecture:** Knowledge base with reference materials and a Python scaffolding tool (`setup_fhir_project.py`)

**Dependencies:** None (self-contained knowledge base)

**Sources:** [README.md:19-25](), [.claude-plugin/marketplace.json:34-44]()

## Skill Directory Structure and Registration

The following diagram shows how skill directories map to marketplace registry entries and their key files:

```mermaid
graph TB
    subgraph "Repository Root"
        MP["marketplace.json"]
        
        subgraph "clinical-trial-protocol-skill/"
            CTP_SKILL["SKILL.md"]
            CTP_README["README.md"]
            CTP_REF["references/"]
            CTP_SCRIPTS["scripts/<br/>sample_size_calculator.py"]
            CTP_WAYPOINTS["waypoints/ (runtime)"]
        end
        
        subgraph "prior-auth-review-skill/"
            PAR_SKILL["SKILL.md"]
            PAR_README["README.md"]
            PAR_ASSETS["assets/<br/>rubric.md<br/>sample/"]
            PAR_WAYPOINTS["waypoints/ (runtime)"]
            PAR_OUTPUTS["outputs/ (runtime)"]
        end
        
        subgraph "fhir-developer-skill/"
            FHIR_SKILL["SKILL.md"]
            FHIR_README["README.md"]
            FHIR_REF["references/"]
            FHIR_SCRIPTS["scripts/<br/>setup_fhir_project.py"]
        end
    end
    
    MP -->|"plugins[0]<br/>name: clinical-trial-protocol<br/>skills: [./clinical-trial-protocol-skill]"| CTP_SKILL
    MP -->|"plugins[1]<br/>name: prior-auth-review<br/>skills: [./prior-auth-review-skill]"| PAR_SKILL
    MP -->|"plugins[2]<br/>name: fhir-developer<br/>skills: [./fhir-developer-skill]"| FHIR_SKILL
    
    CTP_SKILL -.->|"references"| CTP_REF
    CTP_SKILL -.->|"executes"| CTP_SCRIPTS
    CTP_SKILL -.->|"writes to"| CTP_WAYPOINTS
    
    PAR_SKILL -.->|"references"| PAR_ASSETS
    PAR_SKILL -.->|"writes to"| PAR_WAYPOINTS
    PAR_SKILL -.->|"writes to"| PAR_OUTPUTS
    
    FHIR_SKILL -.->|"references"| FHIR_REF
    FHIR_SKILL -.->|"executes"| FHIR_SCRIPTS
```

Each skill directory contains:
- `SKILL.md`: Primary instruction file that Claude reads
- `README.md`: Human-readable documentation
- `references/` or `assets/`: Supporting materials (templates, guidance documents, sample data)
- `scripts/`: Python utilities for statistical calculations or code generation
- Runtime directories: `waypoints/`, `outputs/` created during skill execution

**Sources:** [.claude-plugin/marketplace.json:11-44](), [clinical-trial-protocol-skill/README.md:37-44](), [prior-auth-review-skill/README.md:27-66]()

## Skill-to-MCP Dependencies

The following diagram maps each skill to its external data dependencies via MCP servers:

```mermaid
graph LR
    subgraph "Skills"
        CTP["clinical-trial-protocol"]
        PAR["prior-auth-review"]
        FHIR["fhir-developer"]
    end
    
    subgraph "MCP Servers"
        CT["ClinicalTrials.gov<br/>(not in marketplace)"]
        PM["pubmed<br/>mcp.deepsense.ai"]
        CMS["cms-coverage<br/>mcp.deepsense.ai/cms_coverage"]
        NPI["npi-registry<br/>mcp.deepsense.ai/npi_registry"]
        ICD["icd10-codes<br/>mcp.deepsense.ai/icd10_codes"]
    end
    
    subgraph "Non-MCP Resources"
        WS["WebSearch<br/>(FDA guidance)"]
        WF["WebFetch<br/>(CMS Fee Schedule)"]
    end
    
    CTP -->|"Step 1: search trials"| CT
    CTP -->|"Step 1: find FDA docs"| WS
    CTP -.->|"optional literature"| PM
    
    PAR -->|"validate provider NPI"| NPI
    PAR -->|"validate ICD-10 codes"| ICD
    PAR -->|"search coverage policies"| CMS
    PAR -->|"validate CPT codes"| WF
    
    FHIR -.->|"no dependencies"| FHIR
```

**Dependency Patterns:**

| Skill | Required MCPs | Optional MCPs | Non-MCP Resources |
|-------|---------------|---------------|-------------------|
| `clinical-trial-protocol` | ClinicalTrials.gov | `pubmed` | WebSearch (FDA) |
| `prior-auth-review` | `npi-registry`, `icd10-codes`, `cms-coverage` | `pubmed` | WebFetch (CPT) |
| `fhir-developer` | None | None | None |

The Clinical Trial Protocol skill requires ClinicalTrials.gov data but this MCP server is not included in the marketplace (accessed via alternative methods). The Prior Authorization Review skill is the most MCP-dependent, requiring three separate external data sources. The FHIR Developer skill is entirely self-contained with no external dependencies.

**Sources:** [clinical-trial-protocol-skill/README.md:48-50](), [prior-auth-review-skill/README.md:33-37](), [README.md:44-58]()

## Domain-Specific Characteristics

### Clinical Research Domain

**Workflow Model:** Sequential waypoint pipeline

The Clinical Trial Protocol Generator uses a stateful, resumable workflow where each step produces a waypoint file that subsequent steps consume. This enables:
- Token efficiency by breaking large protocol generation into manageable chunks
- Resumption from any step if interrupted
- Iterative refinement of individual sections

**Key Files:**
- `waypoints/intervention_metadata.json` (Step 0 output)
- `waypoints/01_clinical_research_summary.json` (Step 1 output)
- `waypoints/02_protocol_foundation.md` through `04_protocol_operations.md` (Steps 2-4)
- `outputs/protocol_complete.md` (Step 5 final output)

**Sources:** [clinical-trial-protocol-skill/README.md:36-44]()

### Insurance/Billing Domain

**Workflow Model:** Two-phase with human oversight

The Prior Authorization Review skill separates automated assessment from final decision-making, ensuring human professionals retain control over authorization determinations:

**Subskill 1 (Intake & Assessment):**
- Automated validation and policy matching
- Generates `waypoints/assessment.json` with APPROVE or PEND recommendation
- Never recommends DENY (configurable in `assets/rubric.md`)

**Subskill 2 (Decision & Notification):**
- Loads assessment from Subskill 1
- Requires explicit human confirmation, rejection, or override
- Generates `waypoints/decision.json` and `outputs/notification_letter.txt`

**Human Decision Gates:**
1. After assessment generation (between subskills)
2. During decision finalization (within Subskill 2)

**Sources:** [prior-auth-review-skill/README.md:27-66]()

### Interoperability Domain

**Workflow Model:** Reference-based consultation

The FHIR Developer Guide skill provides on-demand expertise rather than executing a predefined workflow. It contains:
- FHIR R4 resource structure specifications
- Coding system knowledge (LOINC, SNOMED CT, RxNorm, ICD-10)
- SMART on FHIR OAuth 2.0 patterns
- RESTful API patterns and validation rules
- `scripts/setup_fhir_project.py` for FastAPI project scaffolding

Unlike the other skills, FHIR Developer does not produce waypoint files or follow a step-based process. It augments Claude's general coding capabilities with healthcare-specific API knowledge.

**Sources:** [README.md:19-25]()

## Skill Comparison Matrix

| Dimension | Clinical Trial Protocol | Prior Authorization Review | FHIR Developer Guide |
|-----------|------------------------|---------------------------|---------------------|
| **Primary Users** | Clinical researchers, regulatory affairs | Health insurance payers, medical reviewers | Software engineers, API developers |
| **Output Type** | Protocol document (Markdown) | Assessment + decision records (JSON), notification letter (text) | Code (Python/FastAPI), guidance |
| **Execution Pattern** | Sequential pipeline | Two-phase with decision gate | Interactive consultation |
| **State Management** | Waypoint files, resumable | Waypoint files, requires progression | Stateless |
| **Human Interaction** | Optional (can review at any step) | Required (mandatory decision confirmation) | Continuous (developer-guided) |
| **External Data** | ClinicalTrials.gov, FDA guidance, optional PubMed | NPI, ICD-10, CMS coverage, CPT codes | None |
| **Python Requirements** | Yes (`scipy`, `numpy`) | No | No (generates Python code) |
| **Disclaimers** | FDA/IRB approval required | Human review required, draft only | None (general development guidance) |
| **Regulatory Scope** | FDA IDE/IND pathways | Medicare LCDs/NCDs | HL7 FHIR R4 specification |

**Sources:** [clinical-trial-protocol-skill/README.md:1-55](), [prior-auth-review-skill/README.md:1-78](), [README.md:19-42]()

## Installation and Activation

All three skills are installed using the same command pattern:

```bash
# Install individual skills
/plugin install clinical-trial-protocol@healthcare
/plugin install prior-auth-review@healthcare
/plugin install fhir-developer@healthcare
```

Installation requires prior marketplace registration:

```bash
/plugin marketplace add anthropics/healthcare
```

Once installed, skills are automatically available to Claude. No explicit activation command is needed. Claude determines when to use each skill based on user requests and the skill's declared capabilities in its `SKILL.md` file.

For skills with MCP dependencies, users must separately install the required MCP servers using:

```bash
claude mcp add-from-marketplace anthropics/healthcare/<mcp-name>
```

See [Installation and Usage](#2.2) for complete installation workflows.

**Sources:** [README.md:7-15](), [README.md:52-58]()

---

# Page: Clinical Trial Protocol Generator

# Clinical Trial Protocol Generator

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/release.yml](.github/workflows/release.yml)
- [README.md](README.md)
- [clinical-trial-protocol-skill/README.md](clinical-trial-protocol-skill/README.md)
- [clinical-trial-protocol-skill/SKILL.md](clinical-trial-protocol-skill/SKILL.md)
- [clinical-trial-protocol-skill/scripts/sample_size_calculator.py](clinical-trial-protocol-skill/scripts/sample_size_calculator.py)
- [prior-auth-review-skill/README.md](prior-auth-review-skill/README.md)

</details>



## Purpose and Scope

This document describes the Clinical Trial Protocol Generator skill, a Claude Code capability that generates FDA/NIH-compliant clinical trial protocols for medical devices and drugs. The skill uses a modular, waypoint-based architecture to produce comprehensive protocol documents through six sequential steps, from intervention initialization through final protocol generation.

This page covers the skill's architecture, workflow execution, file structure, and technical implementation details. For information about how to install and use this skill, see [Installation and Usage](#2.2). For details on the automated review of this skill during development, see [Skill Review Workflow](#5.1).

**Sources:** [clinical-trial-protocol-skill/README.md:1-55](), [clinical-trial-protocol-skill/SKILL.md:1-22]()

## Overview

The Clinical Trial Protocol Generator produces preliminary clinical trial protocols based on NIH/FDA guidelines and similar trial research. It supports both medical device (IDE pathway) and drug (IND pathway) protocols with appropriate regulatory terminology.

**Target Users:** Clinical researchers, regulatory affairs professionals, protocol writers

**Key Capabilities:**
- **Device & Drug Support:** Handles both medical devices (IDE) and investigational drugs (IND)
- **Token Efficiency:** Modular protocol development to manage output limits
- **Resume from Any Step:** Interrupted workflows continue from last completed waypoint
- **Sample Size Calculation:** Statistical power analysis via Python script
- **Research-Driven:** Leverages ClinicalTrials.gov MCP and FDA guidance documents

**Important Disclaimers:** This tool generates preliminary protocols only. Professional biostatistician review, FDA Pre-Submission meetings, IRB approval, and legal review are required before proceeding with clinical studies.

**Sources:** [clinical-trial-protocol-skill/README.md:6-25](), [clinical-trial-protocol-skill/SKILL.md:22-28]()

## Architecture Overview

### Execution Modes

The skill operates in two distinct modes controlled at startup:

```mermaid
graph TD
    Start["Skill Invoked"]
    Menu["Mode Selection Menu"]
    ResearchMode["Research Only Mode<br/>(Steps 0-1)"]
    FullMode["Full Protocol Mode<br/>(Steps 0-5)"]
    ResearchOut["Research Summary Artifact<br/>waypoints/research_summary.md"]
    ProtocolOut["Complete Protocol<br/>waypoints/protocol_complete.md"]
    Continue["Continue to Full Protocol?"]
    
    Start --> Menu
    Menu -->|"Option 1"| ResearchMode
    Menu -->|"Option 2"| FullMode
    
    ResearchMode --> ResearchOut
    ResearchOut --> Continue
    Continue -->|"Yes"| FullMode
    Continue -->|"No"| End
    
    FullMode --> ProtocolOut
    ProtocolOut --> End["Exit"]
```

**Diagram: Execution Mode Decision Flow**

**Sources:** [clinical-trial-protocol-skill/SKILL.md:156-194](), [clinical-trial-protocol-skill/SKILL.md:196-300]()

### Waypoint-Based Design

All workflow state is persisted in the `waypoints/` directory as JSON and Markdown files. This enables resumability and step independence.

```mermaid
graph LR
    subgraph "waypoints/ Directory"
        IM["intervention_metadata.json<br/>Status, intervention info"]
        R1["01_clinical_research_summary.json<br/>Similar trials, FDA guidance"]
        P2["02_protocol_foundation.md<br/>Sections 1-6"]
        P3["03_protocol_intervention.md<br/>Sections 7-8"]
        P4["04_protocol_operations.md<br/>Sections 9-12"]
        PD["02_protocol_draft.md<br/>Concatenated protocol"]
        PM["02_protocol_metadata.json<br/>Protocol metadata"]
        SS["02_sample_size_calculation.json<br/>Statistical calculations"]
        RS["research_summary.md<br/>Research Only output"]
    end
    
    Step0["Step 0: Initialize"] --> IM
    Step1["Step 1: Research"] --> R1
    Step1 --> RS
    Step2["Step 2: Foundation"] --> P2
    Step2 --> SS
    Step3["Step 3: Intervention"] --> P3
    Step4["Step 4: Operations"] --> P4
    Step4 --> PD
    Step4 --> PM
```

**Diagram: Waypoint File Creation by Step**

**Sources:** [clinical-trial-protocol-skill/SKILL.md:46-59](), [clinical-trial-protocol-skill/SKILL.md:383-397]()

## Modular Subskill Architecture

Each workflow step is implemented as an independent subskill in the `references/` directory. Subskills are loaded on-demand only when their step executes, minimizing context usage.

```mermaid
graph TB
    subgraph "references/ Subskill Files"
        S0["00-initialize-intervention.md<br/>Collect device/drug information"]
        S1["01-research-protocols.md<br/>ClinicalTrials.gov search,<br/>FDA guidance research"]
        S2["02-protocol-foundation.md<br/>Generate sections 1-6:<br/>Summary, Objectives,<br/>Design, Population"]
        S3["03-protocol-intervention.md<br/>Generate sections 7-8:<br/>Administration,<br/>Dose Modifications"]
        S4["04-protocol-operations.md<br/>Generate sections 9-12:<br/>Assessments, Statistics,<br/>Regulatory, References"]
        S5["05-generate-document.md<br/>Final concatenation"]
    end
    
    subgraph "scripts/ Utility Scripts"
        SSC["sample_size_calculator.py<br/>Statistical power analysis<br/>scipy, numpy"]
    end
    
    subgraph "assets/ Reference Templates"
        TPL["FDA-Clinical-Protocol-Template.md<br/>Protocol structure guidance"]
    end
    
    Orchestrator["SKILL.md Orchestrator"] -->|"Step 0"| S0
    Orchestrator -->|"Step 1"| S1
    Orchestrator -->|"Step 2"| S2
    Orchestrator -->|"Step 3"| S3
    Orchestrator -->|"Step 4"| S4
    Orchestrator -->|"Step 5"| S5
    
    S2 -->|"Invokes"| SSC
    S2 -.->|"References"| TPL
    S3 -.->|"References"| TPL
    S4 -.->|"References"| TPL
```

**Diagram: Modular Subskill Components and Dependencies**

The orchestrator in `SKILL.md` implements a lazy loading strategy where subskill files are read only when their step is ready to execute, not in advance.

**Sources:** [clinical-trial-protocol-skill/SKILL.md:64-76](), [clinical-trial-protocol-skill/SKILL.md:78-84](), [clinical-trial-protocol-skill/SKILL.md:316-324]()

## Workflow Steps

### Step Execution Pipeline

```mermaid
stateDiagram-v2
    [*] --> CheckWaypoints
    
    CheckWaypoints: Check waypoints/intervention_metadata.json
    CheckWaypoints --> Step0: No metadata exists
    CheckWaypoints --> Resume: Metadata exists
    Resume --> Step0: Step 0 incomplete
    Resume --> Step1: Step 0 complete
    Resume --> Step2: Steps 0-1 complete
    Resume --> Step3: Steps 0-2 complete
    Resume --> Step4: Steps 0-3 complete
    Resume --> Step5: Steps 0-4 complete
    
    state "Step 0: Initialize" as Step0 {
        [*] --> CollectInfo
        CollectInfo: Collect intervention info
        CollectInfo --> SaveMetadata
        SaveMetadata: Write intervention_metadata.json
        SaveMetadata --> [*]
    }
    
    state "Step 1: Research" as Step1 {
        [*] --> SearchTrials
        SearchTrials: Search ClinicalTrials.gov MCP
        SearchTrials --> SearchFDA
        SearchFDA: Search FDA databases
        SearchFDA --> SaveResearch
        SaveResearch: Write 01_clinical_research_summary.json
        SaveResearch --> [*]
    }
    
    state "Step 2: Foundation" as Step2 {
        [*] --> SampleSize
        SampleSize: Run sample_size_calculator.py
        SampleSize --> GenerateSections
        GenerateSections: Generate protocol sections 1-6
        GenerateSections --> SaveFoundation
        SaveFoundation: Write 02_protocol_foundation.md
        SaveFoundation --> [*]
    }
    
    state "Step 3: Intervention" as Step3 {
        [*] --> GenerateIntervention
        GenerateIntervention: Generate protocol sections 7-8
        GenerateIntervention --> SaveIntervention
        SaveIntervention: Write 03_protocol_intervention.md
        SaveIntervention --> [*]
    }
    
    state "Step 4: Operations" as Step4 {
        [*] --> GenerateOperations
        GenerateOperations: Generate protocol sections 9-12
        GenerateOperations --> SaveOperations
        SaveOperations: Write 04_protocol_operations.md
        SaveOperations --> ConcatenateDraft
        ConcatenateDraft: Create 02_protocol_draft.md
        ConcatenateDraft --> PauseMenu
        PauseMenu: Display Protocol Completion Menu
        PauseMenu --> [*]
    }
    
    state "Step 5: Generate" as Step5 {
        [*] --> Concatenate
        Concatenate: Concatenate all sections
        Concatenate --> SaveFinal
        SaveFinal: Write protocol_complete.md
        SaveFinal --> [*]
    }
    
    Step0 --> Step1
    Step1 --> ExitPoint1
    ExitPoint1: Research Only Exit Point
    ExitPoint1 --> Step2: Full Protocol Mode
    ExitPoint1 --> [*]: Exit after research
    
    Step2 --> Step3
    Step3 --> Step4
    Step4 --> UserDecision
    UserDecision: User reviews draft
    UserDecision --> Step5: Continue
    UserDecision --> [*]: Exit
    
    Step5 --> [*]
```

**Diagram: Complete Workflow State Machine**

**Sources:** [clinical-trial-protocol-skill/SKILL.md:303-369](), [clinical-trial-protocol-skill/README.md:36-44]()

### Step-by-Step Breakdown

| Step | Name | Description | Input Waypoints | Output Waypoints | Script Dependencies |
|------|------|-------------|-----------------|------------------|---------------------|
| 0 | Initialize | Collect device/drug information, indication, initial context | None | `intervention_metadata.json` | None |
| 1 | Research | Search similar trials, find FDA guidance | `intervention_metadata.json` | `01_clinical_research_summary.json`, `research_summary.md` (Research Only mode) | None |
| 2 | Foundation | Generate protocol sections 1-6 (Summary, Objectives, Design, Population) | `intervention_metadata.json`, `01_clinical_research_summary.json` | `02_protocol_foundation.md`, `02_sample_size_calculation.json`, `02_protocol_metadata.json` | `sample_size_calculator.py` |
| 3 | Intervention | Generate protocol sections 7-8 (Administration, Dose Modifications) | `intervention_metadata.json`, `01_clinical_research_summary.json`, `02_protocol_metadata.json` | `03_protocol_intervention.md` | None |
| 4 | Operations | Generate protocol sections 9-12 (Assessments, Statistics, Regulatory) | All previous waypoints | `04_protocol_operations.md`, `02_protocol_draft.md` (concatenated) | None |
| 5 | Generate | Create final professional protocol document | All protocol section files | `protocol_complete.md` | None |

**Sources:** [clinical-trial-protocol-skill/SKILL.md:64-76](), [clinical-trial-protocol-skill/README.md:36-44]()

## File Structure and Code Mapping

### Directory Layout

```
clinical-trial-protocol-skill/
├── SKILL.md                           # Main orchestrator (execution control)
├── README.md                          # User-facing documentation
├── requirements.txt                   # Python dependencies (scipy, numpy)
├── references/                        # Subskill implementation files
│   ├── 00-initialize-intervention.md
│   ├── 01-research-protocols.md
│   ├── 02-protocol-foundation.md
│   ├── 03-protocol-intervention.md
│   ├── 04-protocol-operations.md
│   └── 05-generate-document.md
├── scripts/                           # Utility scripts
│   └── sample_size_calculator.py      # Statistical power calculations
├── assets/                            # Reference templates
│   └── FDA-Clinical-Protocol-Template.md
└── waypoints/                         # Runtime state (user-created)
    ├── intervention_metadata.json
    ├── 01_clinical_research_summary.json
    ├── 02_protocol_foundation.md
    ├── 03_protocol_intervention.md
    ├── 04_protocol_operations.md
    ├── 02_protocol_draft.md
    ├── 02_protocol_metadata.json
    ├── 02_sample_size_calculation.json
    ├── research_summary.md
    └── protocol_complete.md
```

**Sources:** [clinical-trial-protocol-skill/SKILL.md:46-84]()

### Data Flow Between Components

```mermaid
graph TB
    subgraph "External Data Sources"
        CT_MCP["ClinicalTrials.gov MCP<br/>search_clinical_trials()<br/>get_trial_details()"]
        FDA_WS["FDA Databases<br/>(WebSearch)<br/>510(k), PMA, Drugs@FDA"]
    end
    
    subgraph "Step 1 Execution"
        S1["references/<br/>01-research-protocols.md"]
        S1 -->|"Queries"| CT_MCP
        S1 -->|"Searches"| FDA_WS
        S1 -->|"Writes"| W1["waypoints/<br/>01_clinical_research_summary.json"]
    end
    
    subgraph "Step 2 Execution"
        S2["references/<br/>02-protocol-foundation.md"]
        S2 -->|"Reads"| W1
        S2 -->|"Invokes"| SSC["scripts/<br/>sample_size_calculator.py<br/>calculate_continuous_sample_size()<br/>calculate_binary_sample_size()"]
        S2 -->|"Writes"| W2A["waypoints/<br/>02_protocol_foundation.md"]
        S2 -->|"Writes"| W2B["waypoints/<br/>02_sample_size_calculation.json"]
        S2 -->|"Writes"| W2C["waypoints/<br/>02_protocol_metadata.json"]
    end
    
    subgraph "Step 3 Execution"
        S3["references/<br/>03-protocol-intervention.md"]
        S3 -->|"Reads"| W1
        S3 -->|"Reads"| W2C
        S3 -->|"Writes"| W3["waypoints/<br/>03_protocol_intervention.md"]
    end
    
    subgraph "Step 4 Execution"
        S4["references/<br/>04-protocol-operations.md"]
        S4 -->|"Reads"| W1
        S4 -->|"Reads"| W2C
        S4 -->|"Writes"| W4["waypoints/<br/>04_protocol_operations.md"]
        S4 -->|"Concatenates & Writes"| WD["waypoints/<br/>02_protocol_draft.md"]
    end
    
    subgraph "Step 5 Execution"
        S5["references/<br/>05-generate-document.md"]
        S5 -->|"Reads & Concatenates"| W2A
        S5 -->|"Reads & Concatenates"| W3
        S5 -->|"Reads & Concatenates"| W4
        S5 -->|"Writes"| WF["waypoints/<br/>protocol_complete.md"]
    end
    
    W1 -.->|"Read by"| S2
    W1 -.->|"Read by"| S3
    W1 -.->|"Read by"| S4
    W2C -.->|"Read by"| S3
    W2C -.->|"Read by"| S4
```

**Diagram: Data Flow and Component Dependencies**

**Sources:** [clinical-trial-protocol-skill/SKILL.md:86-122](), [clinical-trial-protocol-skill/SKILL.md:316-324]()

## Statistical Sample Size Calculator

The `sample_size_calculator.py` script provides validated statistical power calculations for clinical trials.

### Supported Calculations

| Endpoint Type | Statistical Test | Functions |
|---------------|------------------|-----------|
| **Continuous** | Two-sample t-test | `calculate_continuous_sample_size()` |
| **Binary** | Two-proportion z-test | `calculate_binary_sample_size()` |

**Sources:** [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:1-162]()

### Script Interface

The calculator is invoked as a Python subprocess from Step 2:

```bash
python scripts/sample_size_calculator.py \
  --type continuous \
  --effect-size 5.0 \
  --std-dev 15.0 \
  --alpha 0.05 \
  --power 0.80 \
  --dropout 0.15 \
  --allocation 1.0 \
  --design superiority \
  --output waypoints/02_sample_size_calculation.json
```

**Parameters:**
- `--type`: `continuous` or `binary`
- `--effect-size`: Expected mean difference (continuous endpoints)
- `--std-dev`: Standard deviation (continuous endpoints)
- `--p1`, `--p2`: Expected proportions (binary endpoints)
- `--alpha`: Type I error rate (default: 0.05)
- `--power`: Statistical power (default: 0.80)
- `--dropout`: Expected dropout rate (default: 0.15)
- `--allocation`: Treatment:control ratio (default: 1.0 for equal allocation)
- `--design`: `superiority` or `non-inferiority`

**Sources:** [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:324-409]()

### Output Format

The script outputs structured JSON:

```json
{
  "endpoint_type": "continuous",
  "study_design": "superiority",
  "statistical_test": "Two-sample t-test (two-sided)",
  "effect_size": 5.0,
  "standard_deviation": 15.0,
  "cohens_d": 0.333,
  "alpha": 0.05,
  "power": 0.80,
  "allocation_ratio": "1:1",
  "dropout_rate": 0.15,
  "sample_size": {
    "treatment_arm": 142,
    "control_arm": 142,
    "total": 284,
    "total_with_dropout": 335,
    "treatment_with_dropout": 168,
    "control_with_dropout": 168
  },
  "sensitivity_analysis": {
    "power_90_percent": { "total": 358, "total_with_dropout": 422 },
    "effect_size_reduced_10_percent": { "total": 350, "total_with_dropout": 412 }
  },
  "assumptions": [...],
  "disclaimers": [...]
}
```

**Sources:** [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:120-161](), [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:280-321]()

### Statistical Methods

#### Continuous Endpoints

The continuous sample size calculation [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:16-161]() uses the two-sample t-test power formula:

- **Cohen's d**: `effect_size / std_dev`
- **Equal allocation**: `n = 2 * (z_alpha + z_beta)^2 / d^2`
- **Unequal allocation**: `n = ((1 + 1/r)^2) * ((z_alpha + z_beta)^2) / d^2`

Where:
- `z_alpha`: Z-score for Type I error (two-sided: `alpha/2`, one-sided: `alpha`)
- `z_beta`: Z-score for power (`1 - beta`)
- `r`: Allocation ratio (treatment:control)

#### Binary Endpoints

The binary sample size calculation [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:164-321]() uses the two-proportion z-test:

- **Pooled proportion**: `p_pooled = (p1 + r*p2) / (1 + r)`
- **Effect size**: `|p2 - p1|`
- **Sample size**: `n = [z_alpha * sqrt(p_pooled*(1-p_pooled)*(1+1/r)) + z_beta * sqrt(p1*(1-p1)/r + p2*(1-p2))]^2 / (p2-p1)^2`

**Sources:** [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:16-321]()

## Dependencies and Prerequisites

### Required MCP Servers

```mermaid
graph LR
    CTP["Clinical Trial Protocol Skill"]
    
    subgraph "MCP Server Dependencies"
        CT["ClinicalTrials.gov MCP<br/>search_clinical_trials()<br/>get_trial_details()"]
    end
    
    subgraph "Built-in Capabilities"
        WS["WebSearch<br/>FDA database URLs"]
    end
    
    CTP -->|"Step 1: Required"| CT
    CTP -->|"Step 1: Built-in"| WS
    
    CT -->|"Queries"| CTGOV["ClinicalTrials.gov API"]
    WS -->|"Searches"| FDA["FDA Databases<br/>510(k), PMA, De Novo,<br/>Drugs@FDA, Orange Book"]
```

**Diagram: External Dependencies**

**Installation:**
```bash
# Install ClinicalTrials.gov MCP via drag-and-drop of .mcpb file
# or configure manually in Claude Desktop settings
```

**Verification:** Step 1 automatically tests MCP connectivity at startup.

**Sources:** [clinical-trial-protocol-skill/SKILL.md:86-107](), [clinical-trial-protocol-skill/SKILL.md:109-115]()

### Python Dependencies

The skill requires Python with statistical computing libraries:

**Installation:**
```bash
pip install -r requirements.txt
```

**Required packages:**
- `scipy >= 1.11.0` - Statistical calculations (power analysis, t-tests, z-tests)
- `numpy >= 1.24.0` - Numerical operations

These dependencies are checked by the sample size calculator [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:42-47]() and [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:190-195]().

**Sources:** [clinical-trial-protocol-skill/SKILL.md:123-135](), [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:42-47]()

## Orchestrator Execution Logic

The main orchestrator in `SKILL.md` implements critical execution control patterns.

### Lazy Loading Strategy

The orchestrator uses on-demand loading to minimize context usage:

```python
# INCORRECT: Pre-reading all subskills
for step in range(6):
    subskill_content = read_file(f"references/0{step}-*.md")  # DON'T DO THIS

# CORRECT: Read only when executing
if current_step == 2:
    subskill_content = read_file("references/02-protocol-foundation.md")
    execute_subskill(subskill_content)
```

**Key Principle:** Subskill files are read only at the moment their step executes, never in advance.

**Sources:** [clinical-trial-protocol-skill/SKILL.md:8-20](), [clinical-trial-protocol-skill/SKILL.md:316-324]()

### Resume Capability

The workflow automatically detects completed steps and resumes:

```mermaid
graph TD
    Start["Skill Invoked"]
    CheckMeta{"waypoints/<br/>intervention_metadata.json<br/>exists?"}
    CheckSteps{"Check<br/>completed_steps array"}
    
    Start --> CheckMeta
    CheckMeta -->|"No"| Step0["Start at Step 0"]
    CheckMeta -->|"Yes"| CheckSteps
    
    CheckSteps -->|"[]"| Step0
    CheckSteps -->|"[0]"| Step1["Resume at Step 1"]
    CheckSteps -->|"[0,1]"| Step2["Resume at Step 2"]
    CheckSteps -->|"[0,1,2]"| Step3["Resume at Step 3"]
    CheckSteps -->|"[0,1,2,3]"| Step4["Resume at Step 4"]
    CheckSteps -->|"[0,1,2,3,4]"| Step5["Resume at Step 5"]
    
    Step0 --> Execute["Execute from current step"]
    Step1 --> Execute
    Step2 --> Execute
    Step3 --> Execute
    Step4 --> Execute
    Step5 --> Execute
```

**Diagram: Resume Logic Based on Waypoint State**

The `intervention_metadata.json` file tracks completion status:

```json
{
  "intervention_name": "Novel Cardiac Pacemaker",
  "intervention_type": "device",
  "indication": "Bradycardia",
  "completed_steps": [0, 1, 2],
  "current_step": 3,
  "initial_context": "..."
}
```

**Sources:** [clinical-trial-protocol-skill/SKILL.md:305-307](), [clinical-trial-protocol-skill/SKILL.md:431-435]()

### Error Handling Patterns

```mermaid
graph TD
    ExecuteStep["Execute Step N"]
    CheckSuccess{"Step<br/>Successful?"}
    MCPCheck{"MCP Server<br/>Available?"}
    
    ExecuteStep --> CheckSuccess
    CheckSuccess -->|"No"| MCPCheck
    
    MCPCheck -->|"No"| ShowInstall["Display MCP<br/>installation instructions"]
    MCPCheck -->|"Yes"| ShowError["Display error message"]
    
    ShowInstall --> RetryPrompt["Ask user:<br/>Retry? (Yes/No)"]
    ShowError --> RetryPrompt
    
    RetryPrompt -->|"Yes"| ExecuteStep
    RetryPrompt -->|"No"| SaveState["Save current state<br/>in waypoints"]
    
    SaveState --> ExitGraceful["Exit orchestrator<br/>User can resume later"]
    
    CheckSuccess -->|"Yes"| UpdateMeta["Update<br/>intervention_metadata.json"]
    UpdateMeta --> NextStep["Proceed to next step"]
```

**Diagram: Error Handling Flow**

**Sources:** [clinical-trial-protocol-skill/SKILL.md:417-435]()

## Waypoint File Formats

### JSON Waypoints (Steps 0-1)

JSON waypoints store structured data for programmatic access:

**`intervention_metadata.json`** [clinical-trial-protocol-skill/SKILL.md:51]():
```json
{
  "intervention_name": "string",
  "intervention_type": "device|drug",
  "indication": "string",
  "completed_steps": [0, 1, 2],
  "current_step": 3,
  "initial_context": "Detailed technical specifications...",
  "timestamp": "ISO 8601 datetime"
}
```

**`01_clinical_research_summary.json`** [clinical-trial-protocol-skill/SKILL.md:52]():
```json
{
  "similar_trials": [
    {
      "nct_id": "NCT12345678",
      "title": "string",
      "phase": "string",
      "status": "string",
      "key_findings": "string"
    }
  ],
  "fda_pathway": {
    "recommended_pathway": "510(k)|PMA|IND|NDA",
    "regulatory_basis": "string",
    "guidance_documents": []
  },
  "study_design_recommendations": {
    "suggested_study_type": "RCT|single-arm",
    "phase_recommendation": "1|2|3",
    "primary_endpoint_suggestions": []
  }
}
```

**`02_sample_size_calculation.json`** [clinical-trial-protocol-skill/SKILL.md:58]():
- Output from `sample_size_calculator.py`
- Contains sample size calculations, sensitivity analyses, assumptions, disclaimers

**Sources:** [clinical-trial-protocol-skill/SKILL.md:383-388]()

### Markdown Waypoints (Steps 2-5)

Markdown waypoints store human-readable protocol sections:

**`02_protocol_foundation.md`** [clinical-trial-protocol-skill/SKILL.md:53]():
- Protocol Sections 1-6
- Summary, Objectives, Study Design, Study Population, Inclusion/Exclusion Criteria

**`03_protocol_intervention.md`** [clinical-trial-protocol-skill/SKILL.md:54]():
- Protocol Sections 7-8
- Intervention/Treatment Administration, Dose Modifications, Prohibited Medications

**`04_protocol_operations.md`** [clinical-trial-protocol-skill/SKILL.md:55]():
- Protocol Sections 9-12
- Study Assessments, Statistical Analysis, Regulatory/Ethical Considerations, References

**`02_protocol_draft.md`** [clinical-trial-protocol-skill/SKILL.md:56]():
- Complete concatenated protocol from Steps 2-4
- Generated by Step 4 for user review before final generation

**`protocol_complete.md`** (Step 5 output):
- Final professional protocol document
- Generated by Step 5 with proper formatting and section numbering

**Sources:** [clinical-trial-protocol-skill/SKILL.md:389-397]()

## Data Minimization Strategy

To manage token limits, each step implements aggressive summarization:

**Keep:**
- Top-N results only (5-10 maximum)
- Key facts and identifiers (NCT numbers, endpoint types)
- Concise rationale (2-3 sentences per item)

**Discard:**
- Raw MCP query results (not needed after analysis)
- Full FDA guidance text (only excerpts/citations retained)
- Lower-ranked search results
- Verbose descriptions beyond summary level

**Step Independence:**
Each subskill is designed to:
- Read only from waypoint files, not conversation history
- Produce complete output in single execution
- Not depend on conversation context from previous steps
- Be runnable standalone with appropriate waypoint inputs

**Sources:** [clinical-trial-protocol-skill/SKILL.md:399-408](), [clinical-trial-protocol-skill/SKILL.md:410-415]()

## Protocol Completion Menu

After Step 4 completes, the workflow pauses to allow user review before final generation:

```
✅ PROTOCOL COMPLETE: Protocol Draft Generated

Protocol Details:
  • Study Design: [Design from metadata]
  • Sample Size: [N subjects from metadata]
  • Primary Endpoint: [Endpoint from metadata]
  • Study Duration: [Duration from metadata]

Protocol file: waypoints/02_protocol_draft.md
File size: [Size in KB]

📋 WHAT WOULD YOU LIKE TO DO NEXT?

1. 📄 Review Protocol in Artifact - click on the .md file above

2. 📄 Concatenate Final Protocol (Step 5)

3. ⏸️  Exit and Review Later
```

**User Options:**
1. **Review in Artifact:** Pause and inspect the draft protocol sections
2. **Concatenate Protocol:** Execute Step 5 to generate final document
3. **Exit and Review Later:** Save state and exit (can resume with Step 5 anytime)

**Sources:** [clinical-trial-protocol-skill/SKILL.md:332-369]()

## FDA Protocol Template

The skill references FDA protocol templates stored in `assets/`:

**Template Purpose:**
- Provides protocol structure and content guidance
- Defines required sections for FDA submissions
- System automatically detects available `.md` templates in `assets/` directory

**Referenced by Steps:**
- Step 2 (Foundation): Sections 1-6 structure
- Step 3 (Intervention): Sections 7-8 structure
- Step 4 (Operations): Sections 9-12 structure

**Sources:** [clinical-trial-protocol-skill/SKILL.md:117-122]()

## Integration with Marketplace

The Clinical Trial Protocol Generator is registered in the marketplace registry:

**Marketplace Entry:**
```json
{
  "name": "clinical-trial-protocol",
  "source": "./",
  "skills": ["./clinical-trial-protocol-skill"],
  "description": "Generate FDA/NIH-compliant clinical trial protocols",
  "requirements": "Python with scipy and numpy"
}
```

**Installation Command:**
```bash
/plugin install clinical-trial-protocol@healthcare
```

**Sources:** [README.md:7-15](), [README.md:37-42]()

---

# Page: Workflow Steps and Waypoints

# Workflow Steps and Waypoints

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [clinical-trial-protocol-skill/README.md](clinical-trial-protocol-skill/README.md)
- [clinical-trial-protocol-skill/SKILL.md](clinical-trial-protocol-skill/SKILL.md)
- [clinical-trial-protocol-skill/references/00-initialize-intervention.md](clinical-trial-protocol-skill/references/00-initialize-intervention.md)
- [clinical-trial-protocol-skill/references/01-research-protocols.md](clinical-trial-protocol-skill/references/01-research-protocols.md)
- [clinical-trial-protocol-skill/references/02-protocol-foundation.md](clinical-trial-protocol-skill/references/02-protocol-foundation.md)
- [clinical-trial-protocol-skill/references/03-protocol-intervention.md](clinical-trial-protocol-skill/references/03-protocol-intervention.md)
- [clinical-trial-protocol-skill/scripts/sample_size_calculator.py](clinical-trial-protocol-skill/scripts/sample_size_calculator.py)
- [prior-auth-review-skill/README.md](prior-auth-review-skill/README.md)

</details>



## Purpose and Scope

This document provides a detailed technical reference for the Clinical Trial Protocol Generator skill's workflow architecture, including the six sequential steps, the waypoint files they produce, and the resume/restart mechanisms. This covers the modular execution flow, step-by-step waypoint generation, and the on-demand subskill loading pattern.

For overall skill architecture and prerequisites, see [Clinical Trial Protocol Generator](#3.1). For the sample size calculator script, see [Sample Size Calculator](#3.1.2). For the FDA protocol template, see [FDA Protocol Template](#3.1.3).

---

## Workflow Overview

The Clinical Trial Protocol Generator uses a **waypoint-based architecture** where each step produces persistent JSON or Markdown files in the `waypoints/` directory. This design enables:

- **Resume capability**: Users can restart from any completed step
- **Memory efficiency**: Each step only loads required data from waypoints, not conversation history
- **Step independence**: Steps read only from waypoint files, not prior Claude responses
- **Token optimization**: Large protocol sections split across multiple files

The skill supports two execution modes:
1. **Research Only Mode**: Executes steps 0-1, generates research summary artifact
2. **Full Protocol Mode**: Executes all steps 0-5, generates complete protocol document

Sources: [clinical-trial-protocol-skill/SKILL.md:22-43](), [clinical-trial-protocol-skill/README.md:35-44]()

---

## Execution Modes and Step Mapping

### Mode Selection Flow

```mermaid
stateDiagram-v2
    [*] --> CheckExisting: "Skill invoked"
    
    CheckExisting --> ModeSelection: "intervention_metadata.json exists?"
    CheckExisting --> ModeSelection: "No existing metadata"
    
    state ModeSelection {
        [*] --> DisplayMenu: "Display mode selection menu"
        DisplayMenu --> ResearchOnly: "User selects option 1"
        DisplayMenu --> FullProtocol: "User selects option 2"
        DisplayMenu --> Exit: "User selects option 3"
    }
    
    ResearchOnly --> Steps01: "Execute steps 0-1"
    FullProtocol --> Steps05: "Execute steps 0-5"
    Exit --> [*]
    
    state Steps01 {
        [*] --> Step0_Init
        Step0_Init --> Step1_Research
        Step1_Research --> GenerateSummary
        GenerateSummary --> OfferContinue
        OfferContinue --> ContinueToFull: "User chooses continue"
        OfferContinue --> ExitResearch: "User chooses exit"
    }
    
    ContinueToFull --> Steps05
    ExitResearch --> [*]
    
    state Steps05 {
        [*] --> Step0_Check
        Step0_Check --> Step1_Check
        Step1_Check --> Step2_Foundation
        Step2_Foundation --> Step3_Intervention
        Step3_Intervention --> Step4_Operations
        Step4_Operations --> PauseReview: "Display completion menu"
        PauseReview --> Step5_Concatenate: "User selects concatenate"
        PauseReview --> ExitDraft: "User selects exit"
        Step5_Concatenate --> FinalSummary
    }
    
    FinalSummary --> [*]
    ExitDraft --> [*]
```

Sources: [clinical-trial-protocol-skill/SKILL.md:156-195](), [clinical-trial-protocol-skill/SKILL.md:198-300]()

---

## Step-by-Step Breakdown

### Step 0: Initialize Intervention

**Subskill File**: `references/00-initialize-intervention.md`

**Purpose**: Collects intervention metadata and creates the foundational waypoint file used by all subsequent steps.

**Execution Logic**:
1. Determines intervention type (device or drug)
2. Collects intervention details through user prompts
3. Optional: Accepts custom protocol template upload
4. Optional: Asks clarifying questions (max 3-5, only if needed)
5. Generates filesystem-safe `intervention_id`
6. Creates `waypoints/intervention_metadata.json`

**Waypoint Created**:

| File | Structure | Key Fields |
|------|-----------|------------|
| `waypoints/intervention_metadata.json` | JSON object | `intervention_id`, `intervention_type` (device/drug), `intervention_name`, `intervention_description`, `indication`, `target_population`, `initial_context`, `user_provided_template`, `discovery_clarifications`, `completed_steps` |

**Template Handling**: If user provides a custom template, it is stored in:
```json
{
  "user_provided_template": {
    "provided": true,
    "file_path": "path/to/user/template.md",
    "file_name": "template.md"
  }
}
```

This template path is used by steps 2-3 instead of default `assets/` templates.

Sources: [clinical-trial-protocol-skill/references/00-initialize-intervention.md:1-201](), [clinical-trial-protocol-skill/SKILL.md:46-63]()

---

### Step 1: Research Protocols

**Subskill File**: `references/01-research-protocols.md`

**Purpose**: Conducts regulatory research and clinical trial analysis using MCP servers and FDA databases to inform protocol design.

**Execution Logic**:

#### For Devices
1. Query **Product Classification Database** for device class (I/II/III) and product code
2. Based on class, execute pathway-specific research:
   - **Class III**: PMA Database research (3-5 approved PMAs)
   - **Class I/II**: 510(k) Database research (3-5 predicates)
   - **Novel devices**: De Novo Database research
3. Assess IDE risk (Significant Risk vs Non-Significant Risk per 21 CFR 812.3(m))
4. Search ClinicalTrials.gov for similar trials

#### For Drugs/Biologics
1. Query **Drugs@FDA** and **Orange Book** for drug classification
2. Based on classification, execute pathway-specific research:
   - **Generic**: ANDA research (reference listed drug from Orange Book)
   - **Modified product**: 505(b)(2) research
   - **New chemical entity**: NDA research
   - **Biologic**: BLA research (Purple Book)
3. Assess IND requirements and clinical hold risks per 21 CFR 312.42
4. Search ClinicalTrials.gov for similar trials

#### All Interventions
5. Search for published protocols (via ClinicalTrials.gov MCP only)
6. Synthesize findings into recommendations

**MCP Tools Used**:
- `search_clinical_trials(condition, intervention, status, phase, max_results)`
- `get_trial_details(nct_id)`

**Waypoint Created**:

| File | Size | Key Content |
|------|------|-------------|
| `waypoints/01_clinical_research_summary.json` | ~10-15KB | Top 5-10 similar trials, regulatory pathway determination, design recommendations, endpoint suggestions, sample size considerations |

**Data Minimization Strategy**:
- **Keep**: Top 5-10 trials (NCT IDs, structured summaries), regulatory pathway info, design/endpoint recommendations
- **Discard**: Full trial details, raw MCP results, lower-ranked search results

Sources: [clinical-trial-protocol-skill/references/01-research-protocols.md:1-414](), [clinical-trial-protocol-skill/SKILL.md:217-220]()

---

### Step 2: Protocol Foundation (Sections 1-6)

**Subskill File**: `references/02-protocol-foundation.md`

**Purpose**: Generates title page and protocol sections 1-6 (Summary, Introduction, Objectives, Design, Population).

**Execution Logic**:
1. Loads `intervention_metadata.json` and `01_clinical_research_summary.json`
2. Discovers protocol template:
   - **Priority 1**: User-provided template (if `user_provided_template.provided === true`)
   - **Priority 2**: Template(s) in `assets/` directory
   - If multiple in `assets/`, prompts user to select
3. Reads selected template for structure guidance
4. Generates comprehensive content (~1,500 lines):
   - **Title Page**: Metadata table, protocol ID, sponsor info, regulatory identifiers
   - **Statement of Compliance**: ICH GCP, CFR references, IRB requirements
   - **Section 1**: Synopsis table (20 rows), Schema diagram, Schedule of Activities (20-30 rows × 12-20 columns)
   - **Section 2**: Introduction (rationale, background, risk/benefit assessment) - 400 lines
   - **Section 3**: Objectives & Endpoints table
   - **Section 4**: Study Design (overall design, rationale, dose justification)
   - **Section 5**: Study Population (10-15 inclusion criteria, 15-30 exclusion criteria with detailed tables)

**Template Structure Extraction**: The subskill extracts and includes the exact Table of Contents structure from the template (lines 188-368 in the template).

**Waypoints Created**:

| File | Size | Content |
|------|------|---------|
| `waypoints/02_protocol_foundation.md` | ~100KB (~1,500 lines) | Title Page + Sections 1-6 in markdown |
| `waypoints/02_protocol_metadata.json` | ~1KB | Protocol version, study design, enrollment target, primary endpoint, completion status tracking |

**Quality Requirements**:
- Synopsis table must match objectives/endpoints table
- Schedule of Activities: 20-30 rows, 12-20 columns with visit windows
- Inclusion criteria: 10-15 detailed items with specific lab value tables
- Exclusion criteria: 15-30 items covering all categories (prior therapy, infections, contraindications, etc.)

Sources: [clinical-trial-protocol-skill/references/02-protocol-foundation.md:1-837](), [clinical-trial-protocol-skill/SKILL.md:321-322]()

---

### Step 3: Protocol Intervention (Sections 6-7)

**Subskill File**: `references/03-protocol-intervention.md`

**Purpose**: Generates intervention-specific protocol sections 6-7 (Intervention Administration, Discontinuation).

**Prerequisite Check**: Verifies `waypoints/02_protocol_metadata.json` shows `step_2_status === "completed"`.

**Execution Logic**:
1. Loads protocol template path from `intervention_metadata.json` (uses same template as Step 2)
2. Reads `02_protocol_foundation.md` for context
3. Generates intervention-specific content (~1,200 lines):

#### Section 6: Study Intervention
- **For Devices** (300 lines):
  - Device identification & regulatory status (FDA class, K-number/PMA/IDE)
  - Detailed device description (physical characteristics, materials, components, mechanism)
  - Instructions for Use summary (patient selection, pre-procedure, procedure steps, post-procedure)
  - Device training requirements
  
- **For Drugs/Biologics** (300 lines):
  - Drug identification & regulatory status (IND/NDA/BLA)
  - Formulation details
  - Mechanism of action (100 lines: target, interaction, downstream effects)
  - Pharmacokinetics/pharmacodynamics summary
  - Dosing details (dose calculation, administration, pre-medications)

- **Dose Modifications** (300 lines, if applicable):
  - Dose level table (Level 0, -1, -2, -3)
  - Toxicity-specific modification tables:
    - Hematologic toxicity (neutropenia, thrombocytopenia, anemia)
    - Hepatic toxicity (ALT/AST, bilirubin)
    - Renal toxicity (creatinine, CrCl)
    - Intervention-specific toxicity (immune-related for immunotherapy, neuropathy for chemo, etc.)
  - General toxicity management guidelines

- **Preparation/Handling/Storage** (100 lines)
- **Randomization & Blinding** (50 lines)
- **Compliance Monitoring** (30 lines)
- **Concomitant Therapy** (50 lines)

#### Section 7: Discontinuation
- Discontinuation of intervention (criteria, post-discontinuation procedures)
- Participant withdrawal (criteria, procedures)
- Lost to follow-up (definition, contact attempt procedures)

**Waypoint Created**:

| File | Size | Content |
|------|------|---------|
| `waypoints/03_protocol_intervention.md` | ~1,200 lines | Sections 6-7 only |

**Metadata Update**: Sets `step_3_status: "completed"` in `02_protocol_metadata.json`.

Sources: [clinical-trial-protocol-skill/references/03-protocol-intervention.md:1-742](), [clinical-trial-protocol-skill/SKILL.md:323-324]()

---

### Step 4: Protocol Operations (Sections 8-10)

**Subskill File**: `references/04-protocol-operations.md` (referenced but not provided in context)

**Purpose**: Generates operational protocol sections 8-10 (Assessments, Statistics, Regulatory/Operational).

**Expected Content** (based on template structure):
- **Section 8**: Study Assessments and Procedures (efficacy assessments, safety assessments, AE/SAE definitions and reporting)
- **Section 9**: Statistical Considerations (hypotheses, sample size determination, analysis populations, statistical analyses)
- **Section 10**: Supporting Documentation (regulatory/ethical considerations, monitoring, QA/QC, data handling)

**Sample Size Calculation Integration**: Step 4 invokes `scripts/sample_size_calculator.py` for statistical power analysis (see [Sample Size Calculator](#3.1.2)).

**Waypoint Expected**:

| File | Content |
|------|---------|
| `waypoints/04_protocol_operations.md` | Sections 8-10 |
| `waypoints/02_protocol_draft.md` | Concatenated Sections 1-10 (complete protocol) |

**Pause Point**: After Step 4 completes, the orchestrator displays the Protocol Completion Menu with options:
1. Review protocol in artifact
2. Continue to Step 5 (concatenation)
3. Exit and review later

Sources: [clinical-trial-protocol-skill/SKILL.md:324](), [clinical-trial-protocol-skill/SKILL.md:332-369]()

---

### Step 5: Generate Final Protocol

**Subskill File**: `references/05-concatenate-protocol.md` (referenced but not provided in context)

**Purpose**: Concatenates all protocol sections into a single final document.

**Execution Logic**:
1. Reads all section files:
   - `02_protocol_foundation.md` (Sections 1-6)
   - `03_protocol_intervention.md` (Sections 6-7)
   - `04_protocol_operations.md` (Sections 8-10)
2. Concatenates in order
3. Adds References section (Section 11)
4. Applies final formatting

**Waypoint Created**:

| File | Expected Size | Content |
|------|---------------|---------|
| `waypoints/protocol_complete.md` | ~150-200KB | Complete protocol with all sections 1-11 |

Sources: [clinical-trial-protocol-skill/SKILL.md:362-364](), [clinical-trial-protocol-skill/README.md:44]()

---

## Waypoint Architecture

### Directory Structure

```
clinical-trial-protocol-skill/
├── waypoints/
│   ├── intervention_metadata.json          # Step 0 output
│   ├── 01_clinical_research_summary.json   # Step 1 output
│   ├── 02_protocol_foundation.md           # Step 2 output (Sections 1-6)
│   ├── 02_protocol_metadata.json           # Step 2 metadata
│   ├── 02_sample_size_calculation.json     # Step 2 statistical calc
│   ├── 03_protocol_intervention.md         # Step 3 output (Sections 6-7)
│   ├── 04_protocol_operations.md           # Step 4 output (Sections 8-10)
│   ├── 02_protocol_draft.md                # Step 4 concatenation
│   ├── protocol_complete.md                # Step 5 final output
│   └── research_summary.md                 # Research Only mode artifact
```

Sources: [clinical-trial-protocol-skill/SKILL.md:48-59]()

---

### Waypoint Dependency Graph

```mermaid
graph TD
    Step0["Step 0: Initialize<br/>00-initialize-intervention.md"] --> WP0["intervention_metadata.json<br/>• intervention_id<br/>• intervention_type<br/>• intervention_name<br/>• user_provided_template<br/>• completed_steps"]
    
    WP0 --> Step1["Step 1: Research<br/>01-research-protocols.md"]
    Step1 --> WP1["01_clinical_research_summary.json<br/>• similar_trials (top 5-10)<br/>• regulatory_pathway<br/>• design_recommendations<br/>• endpoint_suggestions"]
    
    WP0 --> Step2["Step 2: Foundation<br/>02-protocol-foundation.md"]
    WP1 --> Step2
    TemplateDir["assets/*.md OR<br/>user_provided_template.file_path"] --> Step2
    
    Step2 --> WP2A["02_protocol_foundation.md<br/>Title Page + Sections 1-6<br/>~1,500 lines"]
    Step2 --> WP2B["02_protocol_metadata.json<br/>• protocol_version<br/>• study_design<br/>• primary_endpoint<br/>• step_N_status"]
    Step2 --> WP2C["02_sample_size_calculation.json<br/>• endpoint_type<br/>• sample_size<br/>• power, alpha<br/>• sensitivity_analysis"]
    
    WP0 --> Step3["Step 3: Intervention<br/>03-protocol-intervention.md"]
    WP1 --> Step3
    WP2A --> Step3
    WP2B --> Step3
    TemplateDir --> Step3
    
    Step3 --> WP3["03_protocol_intervention.md<br/>Sections 6-7<br/>~1,200 lines"]
    Step3 --> UpdateWP2B["Updates 02_protocol_metadata.json<br/>step_3_status: completed"]
    
    WP0 --> Step4["Step 4: Operations<br/>04-protocol-operations.md"]
    WP1 --> Step4
    WP2A --> Step4
    WP2B --> Step4
    WP2C --> Step4
    WP3 --> Step4
    TemplateDir --> Step4
    
    Step4 --> WP4A["04_protocol_operations.md<br/>Sections 8-10"]
    Step4 --> WP4B["02_protocol_draft.md<br/>Concatenated Sections 1-10"]
    
    WP2A --> Step5["Step 5: Concatenate<br/>05-concatenate-protocol.md"]
    WP3 --> Step5
    WP4A --> Step5
    
    Step5 --> WP5["protocol_complete.md<br/>Complete protocol<br/>All sections 1-11"]
    
    WP1 --> ResearchMode["Research Only Mode<br/>Generate Summary"]
    ResearchMode --> WPR["research_summary.md<br/>Formatted research artifact"]
    
    style WP0 fill:#f9f9f9,stroke:#333
    style WP1 fill:#f9f9f9,stroke:#333
    style WP2A fill:#f9f9f9,stroke:#333
    style WP2B fill:#f9f9f9,stroke:#333
    style WP2C fill:#f9f9f9,stroke:#333
    style WP3 fill:#f9f9f9,stroke:#333
    style WP4A fill:#f9f9f9,stroke:#333
    style WP4B fill:#f9f9f9,stroke:#333
    style WP5 fill:#f9f9f9,stroke:#333
    style WPR fill:#f9f9f9,stroke:#333
```

Sources: [clinical-trial-protocol-skill/SKILL.md:46-59](), [clinical-trial-protocol-skill/README.md:35-44]()

---

## Resume Capability

### How Resume Works

The orchestrator checks `waypoints/intervention_metadata.json` at startup to determine which steps have been completed:

```json
{
  "intervention_id": "cardiosync-pacemaker",
  "protocol_status": "intervention_complete",
  "completed_steps": [0, 1, 2, 3]
}
```

**Resume Logic**:
1. Read `intervention_metadata.json`
2. Check `completed_steps` array
3. Determine next incomplete step
4. Display resume message showing:
   - Intervention name and type
   - Completed steps list
   - Next step to execute
5. Skip completed steps, execute from next step

**Example Resume Message** (from orchestrator):
```
✓ Found existing protocol in progress: CardioSync Pacemaker
  Type: Device
  Completed: Steps 0, 1, 2, 3
  Next: Step 4 (Protocol Operations)
```

Sources: [clinical-trial-protocol-skill/SKILL.md:165-169](), [clinical-trial-protocol-skill/SKILL.md:305-307]()

---

## Step Independence and On-Demand Loading

### Lazy Loading Pattern

The orchestrator follows a **strict on-demand loading** pattern to minimize context usage:

**❌ INCORRECT** (Pre-loading):
```
1. Read all subskill files (00-initialize through 05-concatenate)
2. Execute steps in sequence
```

**✅ CORRECT** (On-demand):
```
1. For each step N:
   a. Check if step N is completed (skip if yes)
   b. Read ONLY references/0N-*.md at execution time
   c. Execute subskill instructions
   d. Mark step N complete
```

**Code Reference**: The orchestrator explicitly warns against pre-reading:
> "Do NOT pre-read subskill files - Subskills are loaded on-demand only when their step executes"

**Why this matters**:
- Pre-reading all 6 subskill files (~5,000 lines total) wastes context
- Each step file is 500-1,000 lines
- Steps only need their specific instructions when executing
- Subskills read from waypoints, not conversation history

Sources: [clinical-trial-protocol-skill/SKILL.md:8-20](), [clinical-trial-protocol-skill/SKILL.md:479-486]()

---

### Step-to-File Mapping

```mermaid
graph LR
    subgraph Orchestrator["SKILL.md (Orchestrator)"]
        MainLoop["Execution Loop:<br/>For step in [0..5]"]
    end
    
    subgraph "Step Files (references/)"
        File0["00-initialize-intervention.md"]
        File1["01-research-protocols.md"]
        File2["02-protocol-foundation.md"]
        File3["03-protocol-intervention.md"]
        File4["04-protocol-operations.md"]
        File5["05-concatenate-protocol.md"]
    end
    
    subgraph "Waypoints Directory"
        WP0["intervention_metadata.json"]
        WP1["01_clinical_research_summary.json"]
        WP2["02_protocol_foundation.md<br/>02_protocol_metadata.json"]
        WP3["03_protocol_intervention.md"]
        WP4["04_protocol_operations.md<br/>02_protocol_draft.md"]
        WP5["protocol_complete.md"]
    end
    
    MainLoop -->|"Step 0 executes"| File0
    MainLoop -->|"Step 1 executes"| File1
    MainLoop -->|"Step 2 executes"| File2
    MainLoop -->|"Step 3 executes"| File3
    MainLoop -->|"Step 4 executes"| File4
    MainLoop -->|"Step 5 executes"| File5
    
    File0 -->|"Creates"| WP0
    File1 -->|"Reads WP0<br/>Creates"| WP1
    File2 -->|"Reads WP0, WP1<br/>Creates"| WP2
    File3 -->|"Reads WP0, WP1, WP2<br/>Creates"| WP3
    File4 -->|"Reads all prior WPs<br/>Creates"| WP4
    File5 -->|"Reads WP2, WP3, WP4<br/>Creates"| WP5
```

Sources: [clinical-trial-protocol-skill/SKILL.md:317-325](), [clinical-trial-protocol-skill/SKILL.md:479-486]()

---

## Data Flow Through Waypoints

### Information Propagation

Each step reads specific waypoint fields and passes data forward:

| Step | Reads From | Writes To | Key Data Passed Forward |
|------|-----------|-----------|-------------------------|
| 0 | User input | `intervention_metadata.json` | `intervention_type`, `intervention_name`, `indication`, `user_provided_template` |
| 1 | `intervention_metadata.json` | `01_clinical_research_summary.json` | Regulatory pathway, similar trials (NCT IDs), design recommendations, endpoint suggestions |
| 2 | `intervention_metadata.json`<br/>`01_clinical_research_summary.json`<br/>Template file | `02_protocol_foundation.md`<br/>`02_protocol_metadata.json`<br/>`02_sample_size_calculation.json` | Protocol structure, study design, primary endpoint, sample size, inclusion/exclusion criteria |
| 3 | All Step 2 waypoints<br/>Template file | `03_protocol_intervention.md` | Intervention details, dose modifications, discontinuation criteria |
| 4 | All prior waypoints | `04_protocol_operations.md`<br/>`02_protocol_draft.md` | Assessments, statistics, operational procedures |
| 5 | `02_protocol_foundation.md`<br/>`03_protocol_intervention.md`<br/>`04_protocol_operations.md` | `protocol_complete.md` | Final concatenated protocol |

### Critical Data Transformations

**Step 0 → Step 1**:
- `intervention_type` determines research pathway (device vs drug regulatory research)
- `indication` drives ClinicalTrials.gov search queries

**Step 1 → Step 2**:
- `similar_trials` inform study design selection and endpoint choices
- `regulatory_pathway` determines terminology (IDE vs IND, 510(k) vs NDA)
- `design_recommendations` populate Section 4 (Study Design)

**Step 2 → Step 3**:
- `primary_endpoint` from Section 3 determines dose modification criteria
- `study_design` (RCT vs single-arm) determines randomization/blinding content
- `user_provided_template` path determines which template to use

**Step 3 → Step 4**:
- Intervention administration details inform assessment timing in Schedule of Activities
- Dose modification tables inform safety monitoring frequency

Sources: [clinical-trial-protocol-skill/SKILL.md:46-59](), [clinical-trial-protocol-skill/references/02-protocol-foundation.md:25-29](), [clinical-trial-protocol-skill/references/03-protocol-intervention.md:40-48]()

---

## Sample Size Calculation Integration

### Invocation Point

The sample size calculator is invoked during **Step 2** when generating the Protocol Foundation (specifically Section 9: Statistical Considerations).

**Script Path**: `scripts/sample_size_calculator.py`

**Command-Line Interface**:
```bash
python sample_size_calculator.py --type [continuous|binary] \
    --effect-size X --std-dev Y \
    --alpha 0.05 --power 0.80 --dropout 0.15 \
    --output waypoints/02_sample_size_calculation.json
```

**Function Calls**:
- `calculate_continuous_sample_size()` for continuous endpoints (e.g., mean change in lab value)
- `calculate_binary_sample_size()` for binary endpoints (e.g., response rate, event occurrence)

**Output Fields** (saved to `waypoints/02_sample_size_calculation.json`):
```json
{
  "endpoint_type": "continuous",
  "study_design": "superiority",
  "statistical_test": "Two-sample t-test (two-sided)",
  "effect_size": 5.0,
  "standard_deviation": 15.0,
  "cohens_d": 0.333,
  "alpha": 0.05,
  "power": 0.80,
  "allocation_ratio": "1:1",
  "dropout_rate": 0.15,
  "sample_size": {
    "treatment_arm": 142,
    "control_arm": 142,
    "total": 284,
    "total_with_dropout": 335
  },
  "sensitivity_analysis": {
    "power_90_percent": { "total": 356, "total_with_dropout": 420 },
    "effect_size_reduced_10_percent": { "total": 351, "total_with_dropout": 414 }
  }
}
```

This waypoint is read by Step 2 to populate Section 9.2 (Sample Size Determination) with calculated values and sensitivity analyses.

Sources: [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:1-459](), [clinical-trial-protocol-skill/SKILL.md:58]()

---

## Error Handling and Validation

### Step Prerequisite Validation

Each step validates that prior steps are completed before executing:

**Step 2 Validation** (from `02-protocol-foundation.md`):
```
Check if waypoints/intervention_metadata.json exists
Check if waypoints/01_clinical_research_summary.json exists
If missing → Error: "Cannot draft protocol without previous phase data"
```

**Step 3 Validation** (from `03-protocol-intervention.md`):
```
Read waypoints/02_protocol_metadata.json
Verify step_2_status === "completed"
Verify waypoints/02_protocol_foundation.md exists
If not completed → Error: "Step 2 must be completed before Step 3"
```

### Existing Waypoint Handling

If a step's waypoint file already exists:

**Option 1**: Skip step with message `"✓ Step [X] already complete"`

**Option 2**: Prompt user:
```
Warning: Step N appears to be already completed.
Would you like to:
  1. Skip Step N and continue
  2. Regenerate Step N (will overwrite existing content)
  3. Exit
```

### MCP Server Unavailability

**Detection Point**: Step 1 (when attempting to call `search_clinical_trials`)

**Error Handling**:
```
Error: ClinicalTrials.gov MCP Server not available
Installation instructions: [display MCP installation steps]
Action: Retry step? (Yes/No)
```

**No Fallback**: MCP server is required; step cannot proceed without it.

Sources: [clinical-trial-protocol-skill/SKILL.md:419-435](), [clinical-trial-protocol-skill/references/03-protocol-intervention.md:25-38](), [clinical-trial-protocol-skill/references/02-protocol-foundation.md:792-815]()

---

## Quality Checks Per Step

### Step 2 Quality Requirements

From `02-protocol-foundation.md`:

- [ ] Title page includes all required elements (metadata table, protocol ID, confidentiality statement, sponsor info, regulatory IDs)
- [ ] Synopsis table matches objectives/endpoints table exactly
- [ ] Schedule of Activities: 20-30 rows × 12-20 columns with proper visit windows
- [ ] Inclusion criteria: 10-15 detailed items with specific lab value tables
- [ ] Exclusion criteria: 15-30 items covering all categories
- [ ] Study design rationale references Step 1 findings
- [ ] Background section leverages Step 1 research extensively
- [ ] Intervention-specific terminology (device vs drug) used correctly
- [ ] Protocol foundation length: ~1,500 lines
- [ ] File created successfully at `waypoints/02_protocol_foundation.md`

### Step 3 Quality Requirements

From `03-protocol-intervention.md`:

- [ ] Section 6 includes all required subsections (6.1-6.6)
- [ ] Intervention-specific content (device vs drug terminology)
- [ ] Dose modifications section appropriate for intervention type
- [ ] Section 7 includes all three subsections (7.1-7.3)
- [ ] Content length: ~1,200 lines
- [ ] File created at `waypoints/03_protocol_intervention.md`
- [ ] Protocol metadata updated correctly

### Step 1 Quality Requirements

From `01-research-protocols.md`:

**All Interventions**:
- [ ] At least 3-5 similar trials identified
- [ ] Study designs appropriate for intervention type
- [ ] Primary endpoint recommendations clear
- [ ] Sample size considerations provided
- [ ] FDA guidance relevant to intervention/indication

**Devices Only**:
- [ ] Device classification (Class I/II/III) determined
- [ ] Product code found
- [ ] Regulatory pathway identified (510(k)/De Novo/PMA/Exempt)
- [ ] Predicates identified (3-5 for 510(k)) OR De Novo/PMA precedents
- [ ] IDE risk determination (SR/NSR) with rationale

**Drugs/Biologics Only**:
- [ ] Classification complete (OTC/Rx, controlled schedule, NCE status)
- [ ] Regulatory pathway identified (NDA/ANDA/505(b)(2)/BLA)
- [ ] Reference drug identified (Orange Book/Purple Book)
- [ ] IND requirements and clinical hold risks assessed
- [ ] ICH guideline requirements documented

Sources: [clinical-trial-protocol-skill/references/02-protocol-foundation.md:817-831](), [clinical-trial-protocol-skill/references/03-protocol-intervention.md:726-736](), [clinical-trial-protocol-skill/references/01-research-protocols.md:375-413]()

---

# Page: Sample Size Calculator

# Sample Size Calculator

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [clinical-trial-protocol-skill/README.md](clinical-trial-protocol-skill/README.md)
- [clinical-trial-protocol-skill/SKILL.md](clinical-trial-protocol-skill/SKILL.md)
- [clinical-trial-protocol-skill/scripts/sample_size_calculator.py](clinical-trial-protocol-skill/scripts/sample_size_calculator.py)
- [prior-auth-review-skill/README.md](prior-auth-review-skill/README.md)

</details>



## Purpose and Scope

This document describes the `sample_size_calculator.py` script, a statistical power analysis tool that calculates sample sizes for clinical trial protocols. The calculator supports both continuous and binary primary endpoints using validated statistical methods.

For information about the overall Clinical Trial Protocol Generator workflow, see [Clinical Trial Protocol Generator](#3.1). For details on how the calculator integrates into the protocol generation steps, see [Workflow Steps and Waypoints](#3.1.1).

**Sources:** [clinical-trial-protocol-skill/README.md:1-55](), [clinical-trial-protocol-skill/SKILL.md:1-85]()

---

## Overview

The sample size calculator is a standalone Python utility that performs statistical power calculations to determine the number of participants needed for a clinical trial. It is invoked during Step 2 (Protocol Foundation) of the Clinical Trial Protocol Generator workflow.

**Key Capabilities:**
- Two-sample t-test calculations for continuous endpoints
- Two-proportion z-test calculations for binary endpoints
- Support for superiority and non-inferiority study designs
- Unequal allocation ratio support (e.g., 2:1 treatment:control)
- Dropout rate adjustment
- Sensitivity analysis (90% power and 10% effect size reduction)

**Dependencies:**
- `scipy >= 1.11.0` - Statistical distributions and calculations
- `numpy >= 1.24.0` - Numerical operations

**Sources:** [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:1-15](), [clinical-trial-protocol-skill/README.md:46-51]()

---

## Integration with Clinical Trial Protocol Workflow

The calculator is invoked during Step 2 of the waypoint-based protocol generation workflow. Results are stored in `waypoints/02_sample_size_calculation.json` for use in protocol sections.

```mermaid
graph TB
    subgraph "Step 2: Protocol Foundation"
        S2["references/02-protocol-foundation.md"]
        
        S2 --> Calc["scripts/sample_size_calculator.py"]
        
        subgraph "Calculator Functions"
            Calc_Main["main()"]
            Calc_Cont["calculate_continuous_sample_size()"]
            Calc_Bin["calculate_binary_sample_size()"]
        end
        
        Calc --> Calc_Main
        Calc_Main --> Calc_Cont
        Calc_Main --> Calc_Bin
        
        Calc_Cont --> Output["waypoints/02_sample_size_calculation.json"]
        Calc_Bin --> Output
        
        Output --> Protocol["waypoints/02_protocol_foundation.md<br/>Sections 1-6"]
    end
    
    Input["User provides:<br/>- Endpoint type<br/>- Effect size<br/>- Statistical parameters"] --> S2
    
    S2 -.->|reads| Meta["waypoints/intervention_metadata.json"]
    S2 -.->|reads| Research["waypoints/01_clinical_research_summary.json"]
```

**Workflow Integration Details:**

| Aspect | Description |
|--------|-------------|
| **Execution Point** | Step 2 - Protocol Foundation generation |
| **Input Source** | Interactive user prompts during protocol development |
| **Output Location** | `waypoints/02_sample_size_calculation.json` |
| **Referenced By** | Protocol Sections 3 (Study Design), 9 (Statistical Analysis) |
| **Resumable** | Yes - calculation results persist in waypoint file |

**Sources:** [clinical-trial-protocol-skill/SKILL.md:46-60](), [clinical-trial-protocol-skill/README.md:36-44]()

---

## Calculation Methods

### Continuous Endpoints

The `calculate_continuous_sample_size()` function implements two-sample t-test power calculations for continuous outcomes (e.g., blood pressure change, tumor size reduction).

```mermaid
graph LR
    Input["Input Parameters"] --> Validate["Validate scipy<br/>availability"]
    
    Validate --> CalcD["Calculate Cohen's d<br/>d = effect_size / std_dev"]
    
    CalcD --> Sidedness{"Study Design?"}
    Sidedness -->|superiority| TwoSided["alpha_adj = alpha/2<br/>Two-sided test"]
    Sidedness -->|"non-inferiority"| OneSided["alpha_adj = alpha<br/>One-sided test"]
    
    TwoSided --> ZScores["Calculate Z-scores<br/>z_alpha = ppf(1-alpha_adj)<br/>z_beta = ppf(power)"]
    OneSided --> ZScores
    
    ZScores --> SampleCalc["n = 2*(z_alpha+z_beta)^2 / d^2<br/>(or adjusted for allocation)"]
    
    SampleCalc --> Dropout["Adjust for dropout<br/>n_total = n / (1-dropout_rate)"]
    
    Dropout --> Sensitivity["Sensitivity analysis:<br/>- 90% power<br/>- 10% reduced effect"]
    
    Sensitivity --> Result["Return dictionary<br/>with sample sizes"]
```

**Formula Implementation:**

For equal allocation (1:1):
```
n_per_arm = 2 * (z_alpha + z_beta)² / d²
```

For unequal allocation (r:1):
```
n_per_arm = ((1 + 1/r)² * (z_alpha + z_beta)²) / d²
```

Where:
- `d` = Cohen's d effect size (effect_size / std_dev)
- `z_alpha` = Z-score for Type I error rate
- `z_beta` = Z-score for power (1 - Type II error)
- `r` = allocation_ratio (treatment:control)

**Sources:** [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:16-161]()

---

### Binary Endpoints

The `calculate_binary_sample_size()` function implements two-proportion z-test power calculations for binary outcomes (e.g., response rate, event occurrence).

```mermaid
graph TB
    Input["Input: p1, p2<br/>(control, treatment proportions)"] --> Validate["Validate:<br/>0 < p1, p2 < 1"]
    
    Validate --> Pooled["Calculate pooled proportion<br/>p_pooled = (p1 + r*p2)/(1+r)"]
    
    Pooled --> ZScores["Z-scores:<br/>z_alpha = ppf(1-alpha_adj)<br/>z_beta = ppf(power)"]
    
    ZScores --> Formula{"Allocation?"}
    
    Formula -->|"1:1"| Equal["numerator = (z_alpha*sqrt(2*p_pooled*(1-p_pooled)) +<br/>z_beta*sqrt(p1*(1-p1)+p2*(1-p2)))^2"]
    
    Formula -->|"r:1"| Unequal["numerator = (z_alpha*sqrt(p_pooled*(1-p_pooled)*(1+1/r)) +<br/>z_beta*sqrt(p1*(1-p1)/r+p2*(1-p2)))^2"]
    
    Equal --> SampleSize["n_treatment = ceil(numerator / (p2-p1)^2)"]
    Unequal --> SampleSize
    
    SampleSize --> Dropout["Adjust for dropout"]
    
    Dropout --> Sensitivity["Sensitivity analysis"]
    
    Sensitivity --> Result["Return dictionary"]
```

**Formula Implementation:**

For equal allocation:
```
numerator = [z_alpha * sqrt(2*p_pooled*(1-p_pooled)) + 
             z_beta * sqrt(p1*(1-p1) + p2*(1-p2))]²
n_treatment = numerator / (p2 - p1)²
```

For unequal allocation:
```
numerator = [z_alpha * sqrt(p_pooled*(1-p_pooled)*(1+1/r)) + 
             z_beta * sqrt(p1*(1-p1)/r + p2*(1-p2))]²
n_treatment = numerator / (p2 - p1)²
```

**Sources:** [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:164-321]()

---

## Input Parameters

### Command-Line Interface

The calculator accepts parameters via command-line arguments through the `argparse` interface defined in `main()`.

**Common Parameters (Both Endpoint Types):**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--type` | choice | *required* | Endpoint type: `"continuous"` or `"binary"` |
| `--alpha` | float | 0.05 | Type I error rate (significance level) |
| `--power` | float | 0.80 | Statistical power (1 - Type II error) |
| `--dropout` | float | 0.15 | Expected dropout rate (15%) |
| `--allocation` | float | 1.0 | Allocation ratio treatment:control (1.0 = equal) |
| `--design` | choice | "superiority" | Study design: `"superiority"` or `"non-inferiority"` |
| `--output` | str | None | Output JSON file path (stdout if not specified) |

**Continuous Endpoint Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--effect-size` | float | Yes | Expected mean difference between groups |
| `--std-dev` | float | Yes | Standard deviation (pooled or common) |

**Binary Endpoint Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--p1` | float | Yes | Expected proportion in control group (0 < p1 < 1) |
| `--p2` | float | Yes | Expected proportion in treatment group (0 < p2 < 1) |

**Sources:** [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:324-410]()

---

## Output Format

Both calculation functions return a structured dictionary with comprehensive results and metadata. The output is serialized to JSON format.

### Continuous Endpoint Output Structure

```json
{
  "endpoint_type": "continuous",
  "study_design": "superiority",
  "statistical_test": "Two-sample t-test (two-sided)",
  "effect_size": 5.0,
  "standard_deviation": 15.0,
  "cohens_d": 0.333,
  "alpha": 0.05,
  "power": 0.80,
  "allocation_ratio": "1:1",
  "dropout_rate": 0.15,
  "sample_size": {
    "treatment_arm": 142,
    "control_arm": 142,
    "total": 284,
    "total_with_dropout": 334,
    "treatment_with_dropout": 167,
    "control_with_dropout": 167
  },
  "sensitivity_analysis": {
    "power_90_percent": {
      "total": 380,
      "total_with_dropout": 448
    },
    "effect_size_reduced_10_percent": {
      "total": 350,
      "total_with_dropout": 412
    }
  },
  "assumptions": [...],
  "disclaimers": [...]
}
```

**Sources:** [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:120-161]()

---

### Binary Endpoint Output Structure

```json
{
  "endpoint_type": "binary",
  "study_design": "superiority",
  "statistical_test": "Two-proportion z-test (two-sided)",
  "control_proportion": 0.60,
  "treatment_proportion": 0.75,
  "effect_size": 0.15,
  "alpha": 0.05,
  "power": 0.80,
  "allocation_ratio": "1:1",
  "dropout_rate": 0.15,
  "sample_size": {
    "treatment_arm": 146,
    "control_arm": 146,
    "total": 292,
    "total_with_dropout": 344,
    "treatment_with_dropout": 172,
    "control_with_dropout": 172
  },
  "sensitivity_analysis": {...},
  "assumptions": [...],
  "disclaimers": [...]
}
```

**Key Output Fields:**

| Field | Description |
|-------|-------------|
| `sample_size.total` | Total sample size needed (before dropout adjustment) |
| `sample_size.total_with_dropout` | Total sample size adjusted for expected dropout |
| `sample_size.treatment_arm` | Participants needed in treatment arm |
| `sample_size.control_arm` | Participants needed in control arm |
| `sensitivity_analysis.power_90_percent` | Sample size for 90% power (vs. default 80%) |
| `sensitivity_analysis.effect_size_reduced_10_percent` | Sample size if effect is 10% smaller |
| `assumptions` | List of statistical assumptions made |
| `disclaimers` | Professional review requirements |

**Sources:** [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:280-321]()

---

## Usage Examples

### Example 1: Continuous Endpoint (Blood Pressure Reduction)

Calculate sample size for a device that reduces systolic blood pressure by 5 mmHg on average, with a standard deviation of 15 mmHg.

```bash
python scripts/sample_size_calculator.py \
  --type continuous \
  --effect-size 5.0 \
  --std-dev 15.0 \
  --alpha 0.05 \
  --power 0.80 \
  --dropout 0.15 \
  --output waypoints/02_sample_size_calculation.json
```

**Expected Output:** ~334 total participants (167 per arm with 15% dropout)

---

### Example 2: Binary Endpoint (Response Rate)

Calculate sample size for a drug expected to increase response rate from 60% (control) to 75% (treatment).

```bash
python scripts/sample_size_calculator.py \
  --type binary \
  --p1 0.60 \
  --p2 0.75 \
  --alpha 0.05 \
  --power 0.80 \
  --dropout 0.15
```

**Expected Output:** ~344 total participants (172 per arm with 15% dropout)

---

### Example 3: Unequal Allocation (2:1 Ratio)

Calculate sample size with 2:1 allocation favoring treatment arm (common in Phase 2 trials).

```bash
python scripts/sample_size_calculator.py \
  --type continuous \
  --effect-size 5.0 \
  --std-dev 15.0 \
  --allocation 2.0 \
  --power 0.80 \
  --dropout 0.15
```

**Expected Output:** Different sample sizes for treatment vs. control arms

**Sources:** [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:328-339]()

---

## Statistical Foundations

### Two-Sample T-Test (Continuous Endpoints)

The calculator implements the standard power calculation formula for comparing two means:

**Statistical Test:** Two-sample t-test with equal variances assumption

**Effect Size Metric:** Cohen's d
```
d = (μ₁ - μ₂) / σ
```

Where:
- μ₁, μ₂ = population means for treatment and control
- σ = pooled standard deviation

**Sample Size Formula:**
```
n = 2 * (z_α + z_β)² / d²
```

**Assumptions:**
- Normally distributed continuous outcome
- Equal variances between groups
- Independent observations
- Effect size is clinically meaningful and realistic

**Implementation:** [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:49-76]()

---

### Two-Proportion Z-Test (Binary Endpoints)

The calculator implements power calculations for comparing two proportions.

**Statistical Test:** Two-proportion z-test using normal approximation

**Effect Size:** Absolute difference in proportions
```
Δ = p₂ - p₁
```

**Pooled Proportion:**
```
p_pooled = (p₁ + r*p₂) / (1 + r)
```

**Sample Size Formula:**
```
numerator = [z_α * sqrt(p_pooled*(1-p_pooled)*(1+1/r)) + 
             z_β * sqrt(p₁*(1-p₁)/r + p₂*(1-p₂))]²
n_treatment = numerator / (p₂ - p₁)²
```

**Assumptions:**
- Binary outcome (success/failure, event/no event)
- Independent observations
- Large enough sample for normal approximation (n*p > 5 and n*(1-p) > 5)
- Effect size is clinically meaningful and realistic

**Implementation:** [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:210-239]()

---

## Sensitivity Analysis

Both calculation functions include two sensitivity analyses to help assess robustness of sample size estimates.

```mermaid
graph LR
    Base["Base Calculation<br/>power=0.80"] --> SA1["Sensitivity 1:<br/>power=0.90<br/>(higher power)"]
    Base --> SA2["Sensitivity 2:<br/>effect * 0.90<br/>(10% reduction)"]
    
    SA1 --> Result1["z_beta_90 = ppf(0.90)<br/>recalculate n"]
    SA2 --> Result2["Reduce effect by 10%<br/>recalculate n"]
    
    Result1 --> Output["sensitivity_analysis dict"]
    Result2 --> Output
```

**Sensitivity 1: Higher Power (90%)**
- Rationale: Assess sample size needed for greater statistical power
- Typical Use: Conservative planning or high-stakes trials
- Implementation: [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:93-104]()

**Sensitivity 2: Effect Size Reduced by 10%**
- Rationale: Assess robustness if true effect is smaller than expected
- Typical Use: Account for optimistic effect size estimates
- Implementation: [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:107-118]()

**Sources:** [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:93-118](), [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:246-278]()

---

## Dropout Rate Adjustment

All sample size calculations include adjustment for expected participant dropout.

**Formula:**
```
n_with_dropout = ceil(n_calculated / (1 - dropout_rate))
```

**Default Dropout Rate:** 15% (0.15)

**Rationale:** Clinical trials typically experience participant dropout due to:
- Loss to follow-up
- Withdrawal of consent
- Protocol violations
- Adverse events
- Death (in long-term studies)

**Application:** Dropout adjustment is applied to:
- Total sample size
- Treatment arm sample size
- Control arm sample size
- All sensitivity analysis results

**Example:**
```
Base calculation: 284 participants needed
Dropout rate: 15%
Adjusted sample size: 284 / (1 - 0.15) = 334 participants
```

**Implementation:** [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:88-90](), [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:242-244]()

---

## Error Handling

The calculator implements robust error handling for common issues.

```mermaid
graph TD
    Start["Script execution"] --> CheckScipy{"scipy<br/>installed?"}
    
    CheckScipy -->|No| ErrorScipy["Return error dict:<br/>'scipy not installed'"]
    CheckScipy -->|Yes| CheckType{"Endpoint<br/>type?"}
    
    CheckType -->|continuous| CheckCont{"effect_size AND<br/>std_dev provided?"}
    CheckType -->|binary| CheckBin{"p1 AND p2<br/>provided?"}
    
    CheckCont -->|No| ErrorArgs["parser.error:<br/>'--effect-size and --std-dev required'"]
    CheckBin -->|No| ErrorArgs2["parser.error:<br/>'--p1 and --p2 required'"]
    
    CheckCont -->|Yes| ValidateCont["Calculate continuous<br/>sample size"]
    CheckBin -->|Yes| ValidateBin{"0 < p1, p2 < 1?"}
    
    ValidateBin -->|No| ErrorRange["Return error dict:<br/>'Proportions must be between 0 and 1'"]
    ValidateBin -->|Yes| CalcBin["Calculate binary<br/>sample size"]
    
    ValidateCont --> CheckError{"'error' key<br/>in result?"}
    CalcBin --> CheckError
    ErrorScipy --> CheckError
    ErrorRange --> CheckError
    
    CheckError -->|Yes| Exit1["Print to stderr<br/>sys.exit(1)"]
    CheckError -->|No| Output{"--output<br/>specified?"}
    
    Output -->|Yes| WriteFile["Write JSON to file"]
    Output -->|No| Stdout["Print JSON to stdout"]
    
    WriteFile --> Success["Exit 0"]
    Stdout --> Success
```

**Error Conditions:**

| Condition | Error Message | Exit Code |
|-----------|---------------|-----------|
| `scipy` not installed | "scipy not installed. Run: pip install scipy statsmodels numpy" | 1 |
| Missing required args (continuous) | "--effect-size and --std-dev required for continuous endpoints" | 2 |
| Missing required args (binary) | "--p1 and --p2 required for binary endpoints" | 2 |
| Invalid proportions | "Proportions must be between 0 and 1 (exclusive)" | 1 |

**Sources:** [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:42-47](), [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:197-199](), [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:410-444]()

---

## Validation and Disclaimers

The calculator output includes standardized assumptions and disclaimers emphasizing the preliminary nature of calculations.

**Assumptions Array:**

For continuous endpoints:
- Normally distributed continuous outcome
- Equal variances between groups
- Independent observations
- Effect size is clinically meaningful and realistic

For binary endpoints:
- Binary outcome (success/failure, event/no event)
- Independent observations
- Large enough sample for normal approximation
- Effect size is clinically meaningful and realistic

**Disclaimers Array:**
- Sample size calculation is preliminary and based on assumptions
- Final sample size requires biostatistician review and validation
- FDA Pre-Submission meeting may require adjustments
- Consider pilot study to validate assumptions

**Regulatory Context:**

Sample size calculations generated by this tool are **preliminary estimates only**. Before proceeding with a clinical trial, the following professional reviews are required:

1. **Biostatistician Review:** Independent validation of sample size, power calculations, and statistical methods
2. **FDA Pre-Submission Meeting:** Q-Submission (devices) or Pre-IND (drugs) to discuss study design and sample size
3. **IRB Review:** Institutional Review Board assessment of risk/benefit ratio relative to sample size
4. **Regulatory Consultant:** Specialized expertise for specific indication and regulatory pathway

**Sources:** [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:149-160](), [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:309-320](), [clinical-trial-protocol-skill/README.md:27-34]()

---

## Code Entity Reference

**Primary Functions:**

| Function | Lines | Purpose |
|----------|-------|---------|
| `calculate_continuous_sample_size()` | [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:16-161]() | Two-sample t-test power calculation |
| `calculate_binary_sample_size()` | [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:164-321]() | Two-proportion z-test power calculation |
| `main()` | [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:324-458]() | CLI argument parsing and execution |

**Key Dependencies:**

| Module | Usage |
|--------|-------|
| `scipy.stats` | `norm.ppf()` for Z-score calculations |
| `math` | `ceil()` for rounding up sample sizes, `sqrt()` for variance calculations |
| `argparse` | Command-line interface |
| `json` | Output serialization |

**Sources:** [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:1-458]()

---

# Page: FDA Protocol Template

# FDA Protocol Template

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [clinical-trial-protocol-skill/SKILL.md](clinical-trial-protocol-skill/SKILL.md)
- [clinical-trial-protocol-skill/assets/FDA-Clinical-Protocol-Template.md](clinical-trial-protocol-skill/assets/FDA-Clinical-Protocol-Template.md)
- [clinical-trial-protocol-skill/scripts/sample_size_calculator.py](clinical-trial-protocol-skill/scripts/sample_size_calculator.py)

</details>



## Purpose and Scope

This page documents the FDA-Clinical-Protocol-Template.md file, which serves as the structural and content reference guide for generating clinical trial protocols. The template is based on NIH/FDA standards for Phase 2 and 3 clinical trials conducted under an IND (Investigational New Drug) or IDE (Investigational Device Exemption).

For information about how the template is used in the protocol generation workflow, see [Workflow Steps and Waypoints](#3.1.1). For details on protocol generation execution, see [Clinical Trial Protocol Generator](#3.1).

## Template Overview

The FDA Protocol Template is a comprehensive, 1,800+ line markdown document that defines the complete structure and content requirements for clinical trial protocols compliant with ICH-E6 Good Clinical Practice guidelines.

**Location**: [clinical-trial-protocol-skill/assets/FDA-Clinical-Protocol-Template.md:1-1869]()

**Purpose**: 
- Provide standardized protocol structure meeting FDA/NIH requirements
- Guide content development for each protocol section
- Ensure regulatory compliance and completeness
- Support transparent reporting per CONSORT standards

**Detection**: The skill automatically detects any `.md` files in the `assets/` directory and uses them as templates during protocol generation ([clinical-trial-protocol-skill/SKILL.md:118-122]()).

Sources: [clinical-trial-protocol-skill/assets/FDA-Clinical-Protocol-Template.md:1-27](), [clinical-trial-protocol-skill/SKILL.md:117-122]()

## Template Document Structure

The template consists of four primary components arranged hierarchically:

```mermaid
graph TB
    subgraph "FDA-Clinical-Protocol-Template.md"
        PREFACE["PREFACE<br/>(lines 1-10)"]
        RESOURCES["RESOURCES<br/>(lines 26-158)"]
        COVER["COVER PAGE<br/>(lines 159-187)"]
        TOC["TABLE OF CONTENTS<br/>(lines 188-368)"]
        
        subgraph "12 Main Sections"
            S0["STATEMENT OF COMPLIANCE<br/>(370-387)"]
            S1["1. PROTOCOL SUMMARY<br/>(388-486)"]
            S2["2. INTRODUCTION<br/>(489-560)"]
            S3["3. OBJECTIVES & ENDPOINTS<br/>(561-582)"]
            S4["4. STUDY DESIGN<br/>(584-639)"]
            S5["5. STUDY POPULATION<br/>(640-790)"]
            S6["6. STUDY INTERVENTION<br/>(792-927)"]
            S7["7. DISCONTINUATION<br/>(928-997)"]
            S8["8. ASSESSMENTS & PROCEDURES<br/>(998-1345)"]
            S9["9. STATISTICAL CONSIDERATIONS<br/>(1346-1533)"]
            S10["10. SUPPORTING DOCUMENTATION<br/>(1534-1843)"]
            S11["11. REFERENCES<br/>(1844-1868)"]
        end
    end
    
    PREFACE --> S0
    RESOURCES --> S0
    COVER --> S0
    TOC --> S0
    S0 --> S1
    S1 --> S2
    S2 --> S3
    S3 --> S4
    S4 --> S5
    S5 --> S6
    S6 --> S7
    S7 --> S8
    S8 --> S9
    S9 --> S10
    S10 --> S11
```

Sources: [clinical-trial-protocol-skill/assets/FDA-Clinical-Protocol-Template.md:1-187](), [clinical-trial-protocol-skill/assets/FDA-Clinical-Protocol-Template.md:188-368]()

## Instructional Conventions

The template uses distinct text formatting to differentiate between instructions and example content:

| Convention | Purpose | Action Required |
|------------|---------|-----------------|
| **Italicized text** | Instructional/explanatory guidance | DELETE before finalizing protocol |
| `[Regular bracketed text]` | Example text that can be adapted | MODIFY to fit study specifics or DELETE if not applicable |
| `<Angle brackets>` | Placeholder for specific information | REPLACE with actual study details |
| Section headers with "No text to be entered" | Organizational structure only | KEEP header, populate subsections |
| Footnotes | Additional context for instructions | DELETE with instruction text |

**Critical Rule**: All sections must be included in the protocol in the same order. If a section is not applicable, include the header with "Not applicable" notation ([clinical-trial-protocol-template.md:11-13]()).

**Version Control**: Each revision must update the version number and date in the footer, with amendments tracked in Section 10.4 Protocol Amendment History ([clinical-trial-protocol-template.md:23-24]()).

Sources: [clinical-trial-protocol-skill/assets/FDA-Clinical-Protocol-Template.md:11-24]()

## Template Sections Mapped to Workflow Steps

The template sections align with the skill's 6-step protocol generation workflow:

```mermaid
graph LR
    subgraph "Workflow Steps → Template Sections"
        STEP0["Step 0:<br/>00-initialize-intervention.md"]
        STEP1["Step 1:<br/>01-research-protocols.md"]
        STEP2["Step 2:<br/>02-protocol-foundation.md"]
        STEP3["Step 3:<br/>03-protocol-intervention.md"]
        STEP4["Step 4:<br/>04-protocol-operations.md"]
        STEP5["Step 5:<br/>05-generate-document.md"]
    end
    
    subgraph "Template Sections"
        T1_3["Sections 1-3:<br/>Summary, Introduction,<br/>Objectives"]
        T4_6["Sections 4-6:<br/>Design, Population,<br/>Intervention"]
        T7_8["Sections 7-8:<br/>Discontinuation,<br/>Assessments"]
        T9_12["Sections 9-12:<br/>Statistics, Operations,<br/>References"]
    end
    
    subgraph "Waypoint Outputs"
        W0["intervention_metadata.json"]
        W1["01_clinical_research_summary.json"]
        W2["02_protocol_foundation.md"]
        W3["03_protocol_intervention.md"]
        W4["04_protocol_operations.md<br/>02_protocol_draft.md"]
        W5["protocol_complete.md"]
    end
    
    STEP0 --> W0
    STEP1 --> W1
    STEP2 --> W2
    STEP2 --> T1_3
    STEP3 --> W3
    STEP3 --> T4_6
    STEP4 --> W4
    STEP4 --> T7_8
    STEP4 --> T9_12
    STEP5 --> W5
```

| Workflow Step | Template Sections Referenced | Output Waypoint |
|---------------|------------------------------|-----------------|
| Step 0 (Initialize) | Cover page, intervention description | `intervention_metadata.json` |
| Step 1 (Research) | Section 2.2 (Background), regulatory references | `01_clinical_research_summary.json` |
| Step 2 (Foundation) | Sections 1-6 (Summary, Introduction, Objectives, Design, Population) | `02_protocol_foundation.md` |
| Step 3 (Intervention) | Sections 6-7 (Study Intervention, Discontinuation) | `03_protocol_intervention.md` |
| Step 4 (Operations) | Sections 8-12 (Assessments, Statistics, Supporting Documentation) | `04_protocol_operations.md` |
| Step 5 (Generate) | All sections concatenated with proper formatting | `protocol_complete.md` |

Sources: [clinical-trial-protocol-skill/SKILL.md:66-76](), [clinical-trial-protocol-skill/SKILL.md:321-325]()

## Key Template Sections Detail

### Section 1: Protocol Summary (Lines 388-486)

Contains the high-level study overview required for ClinicalTrials.gov registration:

**Key Components**:
- **Synopsis** (Section 1.1): Structured table with title, description, objectives, endpoints, population, phase, sites, intervention, duration ([lines 392-410]())
- **Schema** (Section 1.2): Visual diagram showing study flow and randomization ([lines 411-450]())
- **Schedule of Activities** (Section 1.3): Detailed visit schedule table with procedures and timepoints ([lines 451-486]())

**Template Features**:
- Provides example tables and flow diagrams
- Aligns terminology with ClinicalTrials.gov fields
- Includes footnote formatting for special conditions

Sources: [clinical-trial-protocol-skill/assets/FDA-Clinical-Protocol-Template.md:388-486]()

### Section 2: Introduction (Lines 489-560)

Establishes scientific rationale and safety profile:

**Subsections**:
- **2.1 Study Rationale** ([lines 495-499]()): Problem statement and reason for trial
- **2.2 Background** ([lines 501-515]()): Nonclinical findings, clinical research history, literature review
- **2.3 Risk/Benefit Assessment** ([lines 517-560]()): Known risks, potential benefits, overall assessment

**Usage in Workflow**: Step 2 populates this section using data from:
- Clinical research summary (Step 1 output)
- FDA guidance documents
- Similar trial designs and outcomes

Sources: [clinical-trial-protocol-skill/assets/FDA-Clinical-Protocol-Template.md:489-560]()

### Section 3: Objectives and Endpoints (Lines 561-582)

Defines study goals and measurements in a structured table format:

```mermaid
graph TB
    OBJ_END["Section 3: Objectives & Endpoints<br/>(lines 561-582)"]
    
    subgraph "Table Structure"
        COL1["Column 1:<br/>OBJECTIVES"]
        COL2["Column 2:<br/>ENDPOINTS"]
        COL3["Column 3:<br/>JUSTIFICATION"]
    end
    
    subgraph "Row Categories"
        PRIMARY["Primary Objective → Primary Endpoint"]
        SECONDARY["Secondary Objectives → Secondary Endpoints"]
        TERTIARY["Tertiary/Exploratory → Exploratory Endpoints"]
    end
    
    OBJ_END --> COL1
    OBJ_END --> COL2
    OBJ_END --> COL3
    
    COL1 --> PRIMARY
    COL1 --> SECONDARY
    COL1 --> TERTIARY
    COL2 --> PRIMARY
    COL2 --> SECONDARY
    COL2 --> TERTIARY
```

**Critical Alignment**: Objectives must align with "Primary Purpose" in ClinicalTrials.gov, and endpoints must align with "Outcome Measures" ([line 563]()).

**Guidance Provided**:
- Primary endpoints should measure clinically meaningful therapeutic effect ([line 575]())
- Secondary endpoints should be short list to preserve statistical power ([line 577]())
- Exploratory endpoints require explicit labeling ([lines 579-581]())

Sources: [clinical-trial-protocol-skill/assets/FDA-Clinical-Protocol-Template.md:561-582]()

### Section 5: Study Population (Lines 640-790)

Defines eligibility criteria and recruitment strategy:

**Critical Subsections**:
- **5.1 Inclusion Criteria** ([lines 662-689]()): Must satisfy NIH Policy on Inclusion of Women and Minorities
- **5.2 Exclusion Criteria** ([lines 691-720]()): Requires justification for excluding specific populations; limited English proficiency cannot be exclusion
- **5.5 Strategies for Recruitment and Retention** ([lines 760-790]()): Must include target enrollment by gender, race, ethnicity

**Special Considerations**:
- Same criterion cannot be both inclusion AND exclusion ([line 654]())
- Reproductive status requires specific contraception requirements ([line 658]())
- Vulnerable populations require additional safeguards ([line 786]())

Sources: [clinical-trial-protocol-skill/assets/FDA-Clinical-Protocol-Template.md:640-790]()

### Section 9: Statistical Considerations (Lines 1346-1533)

Provides framework for statistical analysis plan:

**Key Subsections**:

| Subsection | Lines | Purpose |
|------------|-------|---------|
| 9.1 Statistical Hypotheses | 1354-1365 | Formal null/alternative hypotheses for primary and secondary endpoints |
| 9.2 Sample Size Determination | 1367-1394 | Power calculations with assumptions and justifications |
| 9.3 Populations for Analyses | 1396-1410 | ITT, modified ITT, per-protocol, safety datasets |
| 9.4.2 Primary Endpoint Analysis | 1433-1454 | Statistical procedures, covariates, missing data handling |
| 9.4.6 Planned Interim Analyses | 1497-1512 | Halting guidelines, DSMB review, Type I error adjustment |

**Integration with Sample Size Calculator**: Section 9.2 sample size requirements are calculated using [scripts/sample_size_calculator.py:1-459]() during Step 2 of protocol generation. The calculator outputs are stored in `waypoints/02_sample_size_calculation.json` and referenced in the protocol.

Sources: [clinical-trial-protocol-skill/assets/FDA-Clinical-Protocol-Template.md:1346-1533](), [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:1-161]()

### Section 10: Supporting Documentation (Lines 1534-1843)

Covers regulatory, ethical, and operational requirements:

**Major Subsections**:

```mermaid
graph TB
    SEC10["Section 10:<br/>Supporting Documentation"]
    
    subgraph "Regulatory & Ethical"
        S10_1_1["10.1.1 Informed Consent<br/>(lines 1545-1572)"]
        S10_1_2["10.1.2 Study Discontinuation<br/>(lines 1574-1600)"]
        S10_1_3["10.1.3 Confidentiality<br/>(lines 1602-1644)"]
    end
    
    subgraph "Oversight"
        S10_1_5["10.1.5 Key Roles<br/>(lines 1664-1684)"]
        S10_1_6["10.1.6 Safety Oversight<br/>(lines 1686-1694)"]
        S10_1_7["10.1.7 Clinical Monitoring<br/>(lines 1696-1730)"]
    end
    
    subgraph "Data Management"
        S10_1_9["10.1.9 Data Handling<br/>(lines 1762-1808)"]
        S10_1_10["10.1.10 Protocol Deviations<br/>(lines 1810-1828)"]
        S10_1_11["10.1.11 Publication Policy<br/>(lines 1830-1843)"]
    end
    
    SEC10 --> S10_1_1
    SEC10 --> S10_1_2
    SEC10 --> S10_1_3
    SEC10 --> S10_1_5
    SEC10 --> S10_1_6
    SEC10 --> S10_1_7
    SEC10 --> S10_1_9
    SEC10 --> S10_1_10
    SEC10 --> S10_1_11
```

**Compliance Requirements**:
- Informed consent must comply with 45 CFR Part 46, 21 CFR Part 50, 21 CFR Part 56 ([line 1550]())
- Data handling must follow 21 CFR Part 11 (Electronic Records) ([line 1792]())
- Publication must comply with NIH Public Access Policy and FDAAA ([lines 1834-1843]())

Sources: [clinical-trial-protocol-skill/assets/FDA-Clinical-Protocol-Template.md:1534-1843]()

## Regulatory Resources Section

The template includes extensive regulatory references (lines 26-158) that are removed before finalization but used during protocol development:

**Key Resource Categories**:

| Category | Examples | Lines |
|----------|----------|-------|
| CFR Regulations | 21 CFR Part 11, 50, 56, 312, 812; 45 CFR Part 46 | 33-56 |
| FDA Guidance | ICH-E6 GCP, E9 Statistics, Electronic Source Data | 57-80 |
| NIH Policies | Data Sharing, Inclusion of Women/Minorities, Financial COI | 104-130 |
| OHRP Guidelines | IRBs, Informed Consent, Vulnerable Populations | 132-146 |
| Standards | CONSORT Statement, ISO 14155:2011, ICMJE Recommendations | 148-157 |

**Usage**: Step 1 (research protocols) uses these resources to identify applicable FDA guidance documents and regulatory pathways for the specific intervention type.

Sources: [clinical-trial-protocol-skill/assets/FDA-Clinical-Protocol-Template.md:26-157]()

## Template Usage in Protocol Generation

The template serves multiple functions throughout the protocol generation workflow:

### 1. Structural Reference
Each subskill references the template to determine:
- Required sections and subsections
- Ordering and hierarchy
- Section dependencies

### 2. Content Guidance
Instructions within each section guide content development:
- What information to include
- How to format tables and lists
- Required regulatory language

### 3. Regulatory Compliance
The template ensures protocols include all elements required by:
- ICH-E6 Good Clinical Practice guidelines
- FDA 21 CFR Part 312 (IND) or 21 CFR Part 812 (IDE)
- NIH policies on data sharing, inclusion, and publication

### 4. Quality Assurance
Template structure enables automated validation:
- All required sections present
- Proper section numbering
- Complete table of contents

Sources: [clinical-trial-protocol-skill/SKILL.md:117-122](), [clinical-trial-protocol-skill/assets/FDA-Clinical-Protocol-Template.md:1-27]()

## Example Text Patterns

The template provides reusable example text for common protocol elements:

### Consent Process Example (Lines 1569-1571)
```
[Informed consent is a process that is initiated prior to the individual's 
agreeing to participate in the study and continues throughout the individual's 
study participation...]
```

### Study Discontinuation Example (Lines 1582-1598)
```
[This study may be temporarily suspended or prematurely terminated if there 
is sufficient reasonable cause. Written notification, documenting the reason 
for study suspension or termination, will be provided...]
```

### Safety Monitoring Example (Lines 1691-1693)
```
[Safety oversight will be under the direction of a Data and Safety Monitoring 
Board (DSMB) composed of individuals with the appropriate expertise...]
```

These examples can be adapted by replacing placeholders (e.g., `<specify name>`, `<insert timeline>`) with study-specific details during Steps 2-4 of protocol generation.

Sources: [clinical-trial-protocol-skill/assets/FDA-Clinical-Protocol-Template.md:1569-1571](), [clinical-trial-protocol-skill/assets/FDA-Clinical-Protocol-Template.md:1582-1598](), [clinical-trial-protocol-skill/assets/FDA-Clinical-Protocol-Template.md:1691-1693]()

---

# Page: Prior Authorization Review

# Prior Authorization Review

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/release.yml](.github/workflows/release.yml)
- [README.md](README.md)
- [clinical-trial-protocol-skill/README.md](clinical-trial-protocol-skill/README.md)
- [prior-auth-review-skill/README.md](prior-auth-review-skill/README.md)

</details>



## Purpose and Scope

This document covers the **Prior Authorization Review** skill, which automates health insurance payer review of prior authorization (PA) requests using AI-powered clinical reasoning and coverage policy matching. The skill implements a two-subskill architecture with mandatory human decision gates to generate draft authorization recommendations for payer organizations.

**Target Users:** Health insurance payer professionals (Medicare Advantage, Commercial, Medicaid MCO staff) performing clinical review and authorization decisions.

For information about the other healthcare skills, see [Clinical Trial Protocol Generator](#3.1) and [FHIR Developer Guide](#3.3). For details on the specific MCP servers this skill depends on, see [CMS Coverage Database](#4.1), [NPI Registry](#4.2), and [ICD-10 Codes](#4.4).

For detailed documentation of each subskill:
- [Intake & Assessment Subskill](#3.2.1) - Request validation and medical necessity assessment
- [Decision & Notification Subskill](#3.2.2) - Human oversight and final authorization

**Sources:** [README.md:1-63](), [prior-auth-review-skill/README.md:1-78]()

---

## Skill Architecture Overview

The Prior Authorization Review skill is structured as two sequential subskills that enforce separation between automated assessment and human decision-making. This architecture ensures that AI recommendations never become final decisions without explicit human confirmation.

### Installation

```bash
# Add the marketplace
/plugin marketplace add anthropics/healthcare

# Install the skill
/plugin install prior-auth-review@healthcare
```

### Key Characteristics

| Characteristic | Description |
|---------------|-------------|
| **Plugin ID** | `prior-auth-review@healthcare` |
| **Target Domain** | Insurance/Billing - Payer Prior Authorization |
| **Architecture** | Two-subskill sequential workflow |
| **Decision Model** | AI recommends APPROVE/PEND only (configurable) |
| **Human Oversight** | Required at decision finalization gate |
| **Primary Outputs** | `assessment.json`, `decision.json`, `notification_letter.txt` |
| **MCP Dependencies** | NPI Registry, ICD-10 Codes, CMS Coverage Database |

**Sources:** [README.md:28-33](), [prior-auth-review-skill/README.md:1-26]()

---

## Two-Subskill Workflow Architecture

The skill implements a checkpoint-based workflow where each subskill produces waypoint files that subsequent stages consume. This enables resumption from any point and creates a complete audit trail.

### Complete Workflow Diagram

```mermaid
graph TD
    subgraph Input["Input Data"]
        PA_REQUEST["PA Request<br/>(member, provider,<br/>service, clinical docs)"]
    end
    
    subgraph Subskill1["Subskill 1: Intake & Assessment"]
        COLLECT["Collect PA Request Info"]
        NPI_VAL["Validate Provider<br/>via NPI MCP"]
        ICD_VAL["Validate ICD-10 Codes<br/>via ICD-10 MCP"]
        CPT_VAL["Validate CPT/HCPCS<br/>via WebFetch CMS Fee Schedule"]
        POLICY["Search Coverage Policies<br/>via CMS Coverage MCP"]
        EXTRACT["Extract Clinical Evidence<br/>from Documentation"]
        MAP["Map Evidence to<br/>Policy Criteria"]
        ASSESS["Perform Medical<br/>Necessity Assessment"]
        RECOMMEND["Generate Recommendation<br/>(APPROVE/PEND)"]
        
        COLLECT --> NPI_VAL
        NPI_VAL --> ICD_VAL
        ICD_VAL --> CPT_VAL
        CPT_VAL --> POLICY
        POLICY --> EXTRACT
        EXTRACT --> MAP
        MAP --> ASSESS
        ASSESS --> RECOMMEND
    end
    
    subgraph Waypoint1["Waypoint Output"]
        ASSESSMENT_JSON["waypoints/assessment.json<br/>Consolidated assessment<br/>+ AI recommendation"]
    end
    
    subgraph Gate1["Human Review Gate"]
        HUMAN_REVIEW["Professional reviews<br/>AI recommendation<br/>and supporting evidence"]
    end
    
    subgraph Subskill2["Subskill 2: Decision & Notification"]
        LOAD["Load assessment.json"]
        PRESENT["Present Recommendation<br/>for Human Review"]
        HUMAN_ACTION["Human Action:<br/>Confirm/Reject/Override"]
        GEN_AUTH["Generate Authorization Number<br/>(if approved)"]
        GEN_DOC_REQ["Generate Documentation Requests<br/>(if pended)"]
        LETTER["Create Provider<br/>Notification Letter"]
        AUDIT["Document Complete<br/>Audit Trail"]
        
        LOAD --> PRESENT
        PRESENT --> HUMAN_ACTION
        HUMAN_ACTION -->|Approved| GEN_AUTH
        HUMAN_ACTION -->|Pended| GEN_DOC_REQ
        GEN_AUTH --> LETTER
        GEN_DOC_REQ --> LETTER
        LETTER --> AUDIT
    end
    
    subgraph Waypoint2["Final Outputs"]
        DECISION_JSON["waypoints/decision.json<br/>Final decision record"]
        NOTIFICATION["outputs/notification_letter.txt<br/>Provider notification"]
    end
    
    PA_REQUEST --> COLLECT
    RECOMMEND --> ASSESSMENT_JSON
    ASSESSMENT_JSON --> HUMAN_REVIEW
    HUMAN_REVIEW --> LOAD
    AUDIT --> DECISION_JSON
    AUDIT --> NOTIFICATION
    
    style HUMAN_REVIEW fill:#f9f9f9,stroke:#333,stroke-width:3px
    style HUMAN_ACTION fill:#f9f9f9,stroke:#333,stroke-width:3px
    style ASSESSMENT_JSON fill:#e8e8e8,stroke:#333
    style DECISION_JSON fill:#e8e8e8,stroke:#333
    style NOTIFICATION fill:#e8e8e8,stroke:#333
```

**Sources:** [prior-auth-review-skill/README.md:27-66]()

---

## MCP Server Dependencies and Data Flow

The skill integrates four external data sources to perform comprehensive validation and policy matching. Each MCP server is called at a specific point in the workflow.

### MCP Integration Architecture

```mermaid
graph LR
    subgraph PriorAuthSkill["prior-auth-review-skill/"]
        SKILL_MD["SKILL.md<br/>Workflow instructions"]
        RUBRIC["rubric.md<br/>Decision logic configuration"]
    end
    
    subgraph ExternalMCP["External MCP Servers"]
        NPI_MCP["NPI Registry MCP<br/>mcp.deepsense.ai/npi_registry<br/>Provider credential validation"]
        ICD_MCP["ICD-10 MCP<br/>mcp.deepsense.ai/icd10_codes<br/>Diagnosis code validation"]
        CMS_MCP["CMS Coverage MCP<br/>mcp.deepsense.ai/cms_coverage<br/>LCD/NCD policy search"]
        CMS_FEE["CMS Fee Schedule<br/>WebFetch to cms.gov<br/>CPT/HCPCS validation"]
    end
    
    subgraph ValidationFlow["Validation Pipeline"]
        PROVIDER_VAL["Provider Validation<br/>NPI lookup"]
        DIAGNOSIS_VAL["Diagnosis Validation<br/>ICD-10 batch lookup"]
        PROCEDURE_VAL["Procedure Validation<br/>CPT/HCPCS lookup"]
        POLICY_MATCH["Policy Matching<br/>LCD/NCD search"]
    end
    
    subgraph Waypoints["Waypoint Files"]
        ASSESS_JSON["waypoints/assessment.json"]
        DECISION_JSON["waypoints/decision.json"]
    end
    
    SKILL_MD --> PROVIDER_VAL
    SKILL_MD --> DIAGNOSIS_VAL
    SKILL_MD --> PROCEDURE_VAL
    SKILL_MD --> POLICY_MATCH
    
    PROVIDER_VAL --> NPI_MCP
    DIAGNOSIS_VAL --> ICD_MCP
    PROCEDURE_VAL --> CMS_FEE
    POLICY_MATCH --> CMS_MCP
    
    PROVIDER_VAL --> ASSESS_JSON
    DIAGNOSIS_VAL --> ASSESS_JSON
    PROCEDURE_VAL --> ASSESS_JSON
    POLICY_MATCH --> ASSESS_JSON
    
    ASSESS_JSON --> DECISION_JSON
    RUBRIC --> POLICY_MATCH
```

### MCP Server Usage Table

| MCP Server | Purpose | Called During | Data Retrieved |
|-----------|---------|---------------|----------------|
| **NPI Registry** | Validate provider credentials | Subskill 1 - Initial validation | Provider name, specialty, credentials, practice location |
| **ICD-10 Codes** | Validate diagnosis codes | Subskill 1 - Batch validation | ICD-10 code descriptions, validity status |
| **CMS Coverage** | Retrieve coverage policies | Subskill 1 - Policy search | Medicare LCDs/NCDs, coverage criteria |
| **CMS Fee Schedule** | Validate CPT/HCPCS codes | Subskill 1 - Code validation | Procedure descriptions, pricing information |

**Note:** The CMS Fee Schedule is accessed via WebFetch rather than a dedicated MCP server, as shown in the diagram.

**Sources:** [prior-auth-review-skill/README.md:33-41](), [README.md:44-58]()

---

## Data Validation Pipeline

Each validation step produces structured data that feeds into the medical necessity assessment. The pipeline executes sequentially to build a complete evidence profile.

### Validation Sequence Diagram

```mermaid
sequenceDiagram
    participant User as Payer Professional
    participant Skill as Prior Auth Skill
    participant NPI as NPI Registry MCP
    participant ICD as ICD-10 MCP
    participant CMS_FEE as CMS Fee Schedule
    participant CMS_COV as CMS Coverage MCP
    
    User->>Skill: Provide PA request details
    
    Note over Skill: Subskill 1 begins
    
    Skill->>NPI: Query provider by NPI
    NPI-->>Skill: Provider credentials
    
    Note over Skill: Batch validation
    Skill->>ICD: Validate ICD-10 codes (batch)
    ICD-->>Skill: Code descriptions + validity
    
    Skill->>CMS_FEE: Validate CPT/HCPCS codes
    CMS_FEE-->>Skill: Procedure descriptions
    
    Skill->>CMS_COV: Search coverage policies<br/>(diagnosis + procedure)
    CMS_COV-->>Skill: Matching LCDs/NCDs
    
    Note over Skill: Evidence extraction
    Skill->>Skill: Extract clinical data<br/>from documentation
    
    Note over Skill: Medical necessity assessment
    Skill->>Skill: Map evidence to<br/>policy criteria
    Skill->>Skill: Generate recommendation<br/>(APPROVE/PEND)
    
    Skill-->>User: waypoints/assessment.json
    
    Note over User,Skill: Human Review Gate
    User->>User: Review AI recommendation<br/>and supporting evidence
    
    User->>Skill: Proceed to Subskill 2
    
    Note over Skill: Subskill 2 begins
    Skill->>Skill: Load assessment.json
    Skill->>User: Present recommendation<br/>for confirmation
    User->>Skill: Confirm/Reject/Override
    
    Skill->>Skill: Generate authorization number<br/>OR documentation requests
    Skill->>Skill: Create notification letter
    Skill-->>User: waypoints/decision.json<br/>outputs/notification_letter.txt
```

### Batch Validation Strategy

The ICD-10 validation uses batch processing to minimize MCP calls. All diagnosis codes from the PA request are validated in a single batch operation, as referenced in [prior-auth-review-skill/README.md:35]().

**Sources:** [prior-auth-review-skill/README.md:33-44]()

---

## Human Decision Points and AI Behavior

The skill enforces two explicit human decision points to ensure appropriate oversight and prevent automated decision-making without review.

### Decision Gate Architecture

| Decision Point | Location | Purpose | Human Actions Available |
|---------------|----------|---------|------------------------|
| **Post-Assessment Review** | Between Subskills 1 and 2 | Review AI recommendation and supporting evidence before finalizing | Proceed to decision, request additional review, abandon workflow |
| **Final Decision Confirmation** | Within Subskill 2 | Explicitly confirm, reject, or override AI recommendation | Confirm (accept), Reject (deny), Override (modify with justification) |

### AI Recommendation Behavior

**Default Decision Logic:**
- AI recommends **APPROVE** when clinical evidence meets policy criteria
- AI recommends **PEND** when documentation is insufficient
- AI **NEVER** recommends DENY by default (configurable in `rubric.md`)

**Rationale:** This conservative approach ensures that denial decisions always involve explicit human judgment, reducing risk of inappropriate automated denials.

### Decision Logic Diagram

```mermaid
graph TD
    START["Medical Necessity Assessment"]
    
    EVIDENCE_CHECK{"Clinical evidence<br/>meets policy<br/>criteria?"}
    DOC_CHECK{"Documentation<br/>complete and<br/>sufficient?"}
    
    APPROVE["AI Recommendation:<br/>APPROVE"]
    PEND["AI Recommendation:<br/>PEND<br/>(request additional documentation)"]
    
    HUMAN_GATE["Human Review Gate"]
    
    HUMAN_DECISION{"Human Action"}
    
    CONFIRM["Confirm Recommendation"]
    REJECT["Reject Recommendation<br/>(manual DENY)"]
    OVERRIDE["Override Recommendation<br/>(with documented justification)"]
    
    FINAL_APPROVE["Final Decision: APPROVE<br/>Generate auth number"]
    FINAL_PEND["Final Decision: PEND<br/>Generate doc requests"]
    FINAL_DENY["Final Decision: DENY<br/>Document denial rationale"]
    
    NOTIFICATION["Generate Provider<br/>Notification Letter"]
    
    START --> EVIDENCE_CHECK
    EVIDENCE_CHECK -->|Yes| DOC_CHECK
    EVIDENCE_CHECK -->|No| PEND
    DOC_CHECK -->|Yes| APPROVE
    DOC_CHECK -->|No| PEND
    
    APPROVE --> HUMAN_GATE
    PEND --> HUMAN_GATE
    
    HUMAN_GATE --> HUMAN_DECISION
    
    HUMAN_DECISION -->|Confirm APPROVE| CONFIRM
    HUMAN_DECISION -->|Confirm PEND| CONFIRM
    HUMAN_DECISION -->|Reject| REJECT
    HUMAN_DECISION -->|Override| OVERRIDE
    
    CONFIRM -->|From APPROVE| FINAL_APPROVE
    CONFIRM -->|From PEND| FINAL_PEND
    REJECT --> FINAL_DENY
    OVERRIDE --> FINAL_APPROVE
    OVERRIDE --> FINAL_PEND
    OVERRIDE --> FINAL_DENY
    
    FINAL_APPROVE --> NOTIFICATION
    FINAL_PEND --> NOTIFICATION
    FINAL_DENY --> NOTIFICATION
    
    style HUMAN_GATE fill:#f9f9f9,stroke:#333,stroke-width:3px
    style HUMAN_DECISION fill:#f9f9f9,stroke:#333,stroke-width:3px
```

**Configuration:** The decision logic is defined in `rubric.md` within the skill directory and can be customized to match specific payer policies.

**Sources:** [prior-auth-review-skill/README.md:17-26](), [prior-auth-review-skill/README.md:45-66]()

---

## Outputs and Artifacts

The skill generates three primary artifacts that document the complete review process and support audit requirements.

### Output Files Structure

```mermaid
graph TD
    subgraph SkillDirectory["prior-auth-review-skill/"]
        SKILL["SKILL.md"]
        RUBRIC["rubric.md"]
        ASSETS["assets/<br/>Reference materials"]
    end
    
    subgraph RuntimeDirectories["Runtime Directories (Created)"]
        WAYPOINTS["waypoints/"]
        OUTPUTS["outputs/"]
    end
    
    subgraph WaypointFiles["waypoints/"]
        ASSESSMENT["assessment.json<br/>• PA request details<br/>• Validation results<br/>• Coverage policies<br/>• Clinical evidence<br/>• AI recommendation<br/>• Supporting rationale"]
        
        DECISION["decision.json<br/>• Final decision<br/>• Human action taken<br/>• Authorization number<br/>• Timestamp<br/>• Override justification<br/>• Audit trail"]
    end
    
    subgraph OutputFiles["outputs/"]
        NOTIFICATION["notification_letter.txt<br/>• Provider notification<br/>• Decision details<br/>• Authorization number<br/>• Documentation requests<br/>• Appeal rights"]
    end
    
    SKILL -->|Subskill 1 creates| ASSESSMENT
    ASSESSMENT -->|Subskill 2 reads| DECISION
    DECISION -->|Generates| NOTIFICATION
    
    RUBRIC -.->|Configures| ASSESSMENT
    ASSETS -.->|References| SKILL
```

### File Descriptions

#### `waypoints/assessment.json`

**Generated By:** Subskill 1 (Intake & Assessment)  
**Purpose:** Complete assessment record with AI recommendation  
**Consumed By:** Subskill 2 (Decision & Notification)

**Key Fields:**
- `pa_request` - Member info, requested service, provider details
- `validation_results` - NPI, ICD-10, CPT/HCPCS validation outcomes
- `coverage_policies` - Matching LCDs/NCDs with criteria
- `clinical_evidence` - Structured clinical data from documentation
- `medical_necessity_assessment` - Evidence mapping to policy criteria
- `recommendation` - AI recommendation (APPROVE/PEND)
- `rationale` - Detailed explanation of recommendation

#### `waypoints/decision.json`

**Generated By:** Subskill 2 (Decision & Notification)  
**Purpose:** Final decision record with complete audit trail  
**Used For:** Regulatory compliance, appeals, audit defense

**Key Fields:**
- `ai_recommendation` - Original AI recommendation from assessment
- `human_action` - Confirm/Reject/Override
- `final_decision` - APPROVE/PEND/DENY
- `authorization_number` - Generated if approved
- `documentation_requests` - Specific items needed if pended
- `denial_rationale` - Explanation if denied
- `override_justification` - Required if human overrode AI
- `timestamp` - Decision finalization time
- `reviewer_identifier` - Human reviewer (if captured)

#### `outputs/notification_letter.txt`

**Generated By:** Subskill 2 (Decision & Notification)  
**Purpose:** Provider communication of authorization decision  
**Delivered To:** Healthcare provider who submitted PA request

**Contents:**
- Decision outcome (approved/pended/denied)
- Authorization number and validity period (if approved)
- Specific documentation requests (if pended)
- Denial explanation and policy citation (if denied)
- Appeal rights and process information

**Sources:** [prior-auth-review-skill/README.md:42-66]()

---

## Demo Mode and Sample Data

The skill includes sample case files for demonstration and testing purposes. Demo mode allows users to understand the workflow without requiring live MCP connections for all services.

### Sample Data Location

Sample case files are located in `assets/sample/` within the skill directory, as referenced in [prior-auth-review-skill/README.md:72]().

### Demo Mode Behavior

| Component | Live Mode | Demo Mode |
|-----------|-----------|-----------|
| **NPI Registry Lookup** | MCP call to NPI Registry | Skipped for sample provider |
| **ICD-10 Validation** | MCP call to ICD-10 server | Executes normally |
| **CMS Coverage Search** | MCP call to CMS Coverage | Executes normally |
| **CPT/HCPCS Validation** | WebFetch to CMS Fee Schedule | Executes normally |

**Demo Case:** The sample data includes a pre-configured lung biopsy case that demonstrates:
- Complete PA request structure
- Clinical documentation format
- Coverage policy matching
- Medical necessity assessment
- Recommendation generation

**Purpose:** Allows payer organizations to evaluate the skill's capabilities before integrating with production systems.

**Sources:** [prior-auth-review-skill/README.md:72-78]()

---

## Important Disclaimers and Limitations

### Coverage Policy Source

The skill uses **Medicare LCDs/NCDs** via the CMS Coverage MCP Connector. For commercial or Medicare Advantage plans, payer-specific policies may differ and are not automatically applied. Payer organizations must:
- Configure custom policy sources if needed
- Validate that Medicare policies align with their coverage determinations
- Override AI recommendations when payer-specific policies differ

### Responsibility and Liability

As stated in [prior-auth-review-skill/README.md:19-26]():

> **DRAFT RECOMMENDATIONS ONLY:** This skill generates draft recommendations only. The payer organization remains fully responsible for all final authorization decisions.

> **HUMAN REVIEW REQUIRED:** All AI-generated recommendations require review and confirmation by appropriate professionals before becoming final decisions. Users may accept, reject, or override any recommendation with documented justification.

> **AI DECISION BEHAVIOR:** In default mode, AI recommends APPROVE or PEND only - never recommends DENY. Decision logic is configurable in the skill's rubric.md file.

### Professional Standards

Payer organizations using this skill must ensure:
- Human reviewers have appropriate clinical credentials and training
- Decision workflows comply with state and federal regulations
- Audit trails meet regulatory documentation requirements
- Appeal processes are properly implemented
- Override justifications are appropriately documented

**Sources:** [prior-auth-review-skill/README.md:17-26]()

---

## Skill Files and Directory Structure

The skill directory contains all configuration, instructions, and reference materials needed for operation.

### Directory Layout

```
prior-auth-review-skill/
├── SKILL.md                    # Main skill instructions (workflow)
├── README.md                   # Skill overview and documentation
├── rubric.md                   # Decision logic configuration
├── assets/                     # Reference materials
│   ├── sample/                 # Sample case files for demo mode
│   └── [other references]      # Coverage policy templates, etc.
├── waypoints/                  # Runtime directory (created during execution)
│   ├── assessment.json         # Subskill 1 output
│   └── decision.json           # Subskill 2 output
└── outputs/                    # Runtime directory (created during execution)
    └── notification_letter.txt # Provider notification
```

**Key Configuration Files:**
- **SKILL.md** - Contains the complete workflow instructions for both subskills
- **rubric.md** - Defines the medical necessity assessment criteria and decision logic
- **assets/** - Houses reference materials and sample data for demonstrations

**Sources:** [prior-auth-review-skill/README.md:1-78]()

---

## Related Documentation

For detailed information on each subskill's implementation:
- **[Intake & Assessment Subskill](#3.2.1)** - Validation pipeline, MCP integration, and recommendation generation
- **[Decision & Notification Subskill](#3.2.2)** - Human oversight process, decision finalization, and notification generation

For information on the external data sources:
- **[CMS Coverage Database](#4.1)** - Medicare LCD/NCD policy retrieval
- **[NPI Registry](#4.2)** - Provider credential validation
- **[ICD-10 Codes](#4.4)** - Diagnosis code validation

For marketplace and installation details:
- **[Marketplace Architecture](#2)** - Plugin system overview
- **[Installation and Usage](#2.2)** - Command reference

**Sources:** [README.md:1-63](), [prior-auth-review-skill/README.md:1-78]()

---

# Page: Intake & Assessment Subskill

# Intake & Assessment Subskill

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/release.yml](.github/workflows/release.yml)
- [README.md](README.md)
- [clinical-trial-protocol-skill/README.md](clinical-trial-protocol-skill/README.md)
- [prior-auth-review-skill/README.md](prior-auth-review-skill/README.md)

</details>



## Purpose and Scope

This page documents **Subskill 1: Intake & Assessment** of the Prior Authorization Review skill. This subskill automates the initial intake, validation, and clinical assessment phases of a prior authorization (PA) request workflow for health insurance payers.

The Intake & Assessment subskill collects PA request information, validates all identifiers and codes through external data sources, searches applicable coverage policies, performs medical necessity assessment, and generates a preliminary recommendation. It produces a structured assessment document that requires human review before proceeding to the decision phase.

For information about finalizing the authorization decision and generating provider notifications, see [Decision & Notification Subskill](#3.2.2). For overall context on the Prior Authorization Review skill architecture, see [Prior Authorization Review](#3.2).

**Sources:** [prior-auth-review-skill/README.md:27-45]()

---

## Workflow Overview

The Intake & Assessment subskill follows a sequential validation and analysis pipeline, integrating multiple MCP servers to verify data integrity before performing clinical assessment.

### End-to-End Process Flow

```mermaid
sequenceDiagram
    participant User as "Payer Professional"
    participant Skill as "Intake & Assessment Subskill"
    participant NPI as "NPI Registry MCP"
    participant ICD as "ICD-10 Codes MCP"
    participant WebFetch as "WebFetch<br/>(CMS Fee Schedule)"
    participant CMS as "CMS Coverage MCP"
    participant FS as "File System"

    User->>Skill: "Initiate PA request intake"
    Skill->>User: "Request PA details"
    User->>Skill: "Provide member, service, provider, clinical docs"
    
    rect rgb(240, 240, 240)
        Note over Skill,NPI: Validation Phase
        Skill->>NPI: "Validate provider NPI"
        NPI-->>Skill: "Provider credentials & specialty"
        
        Skill->>ICD: "Batch validate ICD-10 codes"
        ICD-->>Skill: "Code descriptions & validity"
        
        Skill->>WebFetch: "Validate CPT/HCPCS codes"
        WebFetch-->>Skill: "Code descriptions & fee schedule"
    end
    
    rect rgb(240, 240, 240)
        Note over Skill,CMS: Policy Search Phase
        Skill->>CMS: "Search coverage policies (LCD/NCD)"
        CMS-->>Skill: "Applicable policies & criteria"
    end
    
    rect rgb(240, 240, 240)
        Note over Skill: Clinical Assessment Phase
        Skill->>Skill: "Extract clinical data from docs"
        Skill->>Skill: "Map evidence to policy criteria"
        Skill->>Skill: "Assess medical necessity"
        Skill->>Skill: "Generate recommendation"
    end
    
    Skill->>FS: "Write waypoints/assessment.json"
    Skill->>User: "Present assessment & recommendation"
    
    Note over User: Human Decision Point:<br/>Review before proceeding<br/>to Subskill 2
```

**Sources:** [prior-auth-review-skill/README.md:27-45]()

---

## Input Collection

The subskill collects comprehensive information about the prior authorization request through interactive prompts or file ingestion.

### Required Data Elements

| Category | Data Elements | Purpose |
|----------|---------------|---------|
| **Member Information** | Member ID, Name, Date of Birth, Plan Type | Identify beneficiary and applicable coverage |
| **Service Details** | CPT/HCPCS codes, ICD-10 diagnosis codes, Requested quantity/frequency | Define requested service and medical indication |
| **Provider Information** | NPI number, Name, Specialty, Facility | Validate ordering provider credentials |
| **Clinical Documentation** | Progress notes, test results, prior treatment history | Support medical necessity assessment |

### Sample Data Mode

When processing demonstration cases from `assets/sample/`, the skill operates in a modified mode:

- **NPI Lookup Bypass**: Skips NPI MCP validation for pre-configured sample providers
- **Full MCP Execution**: ICD-10 and CMS Coverage MCPs execute normally
- **Demo Workflow**: Demonstrates complete assessment pipeline with lung biopsy case

**Sources:** [prior-auth-review-skill/README.md:72-78]()

---

## Validation Pipeline

The subskill performs three types of validation using external data sources to ensure data integrity before clinical assessment.

### Validation Architecture

```mermaid
graph TB
    Input["PA Request Input"]
    
    subgraph "Validation Layer"
        V1["NPI Validation"]
        V2["ICD-10 Validation"]
        V3["CPT/HCPCS Validation"]
    end
    
    subgraph "MCP Servers & External Sources"
        NPI_MCP["npi-registry MCP<br/>mcp.deepsense.ai/npi_registry"]
        ICD_MCP["icd10-codes MCP<br/>mcp.deepsense.ai/icd10_codes"]
        CMS_FS["CMS Fee Schedule<br/>WebFetch HTTPS"]
    end
    
    subgraph "Validated Data Store"
        VP["Provider:<br/>credentials, specialty, address"]
        VD["Diagnoses:<br/>descriptions, validity"]
        VC["Procedures:<br/>descriptions, billing codes"]
    end
    
    Input --> V1
    Input --> V2
    Input --> V3
    
    V1 --> NPI_MCP
    V2 --> ICD_MCP
    V3 --> CMS_FS
    
    NPI_MCP --> VP
    ICD_MCP --> VD
    CMS_FS --> VC
    
    VP --> Assessment["Medical Necessity<br/>Assessment"]
    VD --> Assessment
    VC --> Assessment
```

**Sources:** [prior-auth-review-skill/README.md:34-37]()

### Provider Credential Validation

The NPI (National Provider Identifier) validation confirms the requesting provider's credentials and specialty.

**Process:**
1. Extract NPI number from PA request
2. Query NPI Registry MCP via `npi-registry` connector
3. Retrieve provider taxonomy, specialty, practice location
4. Verify provider is authorized to request the service type

**MCP Integration:** Uses the `npi-registry` MCP server (see [NPI Registry](#4.2) for server details)

**Sources:** [prior-auth-review-skill/README.md:34](), [README.md:49]()

### ICD-10 Code Validation

Diagnosis codes are validated in batch mode to ensure they are current and properly formed.

**Process:**
1. Extract all ICD-10 codes from PA request (typically 1-4 codes)
2. Submit batch validation request to ICD-10 MCP
3. Receive code descriptions and validity status
4. Flag any invalid or deprecated codes for manual review

**Batch Processing:** Multiple codes validated in a single MCP call for efficiency

**MCP Integration:** Uses the `icd10-codes` MCP server (see [ICD-10 Codes](#4.4) for server details)

**Sources:** [prior-auth-review-skill/README.md:35]()

### CPT/HCPCS Code Validation

Procedure and service codes are validated against the CMS Fee Schedule via WebFetch.

**Process:**
1. Extract CPT/HCPCS codes from PA request
2. Fetch code definitions from CMS Physician Fee Schedule (HTTPS endpoint)
3. Verify codes are billable and retrieve RVU values
4. Confirm codes match service description

**Data Source:** CMS Physician Fee Schedule (MPFS) published tables

**Sources:** [prior-auth-review-skill/README.md:36]()

---

## Coverage Policy Search

After validation, the subskill searches for applicable Medicare coverage policies that govern the requested service.

### Policy Retrieval Process

```mermaid
graph LR
    subgraph "Input Parameters"
        CPT["CPT/HCPCS Codes"]
        ICD["ICD-10 Codes"]
        LOC["Service Location"]
    end
    
    subgraph "CMS Coverage MCP"
        Search["Coverage Policy Search"]
        LCD["Local Coverage<br/>Determinations (LCDs)"]
        NCD["National Coverage<br/>Determinations (NCDs)"]
    end
    
    subgraph "Retrieved Policies"
        Policy["Policy Document:<br/>- Coverage criteria<br/>- Medical necessity rules<br/>- Documentation requirements<br/>- Frequency limits"]
    end
    
    CPT --> Search
    ICD --> Search
    LOC --> Search
    
    Search --> LCD
    Search --> NCD
    
    LCD --> Policy
    NCD --> Policy
    
    Policy --> Criteria["Structured Criteria<br/>for Assessment"]
```

**Sources:** [prior-auth-review-skill/README.md:37]()

### Coverage Determination Hierarchy

1. **National Coverage Determinations (NCDs)**: Federal Medicare policies that apply nationwide
2. **Local Coverage Determinations (LCDs)**: MAC-specific policies for particular jurisdictions
3. **Priority**: NCDs take precedence over LCDs when both exist for the same service

**MCP Integration:** Uses the `cms-coverage` MCP server (see [CMS Coverage Database](#4.1) for server details)

**Important Limitation:** Policies retrieved are Medicare LCDs/NCDs only. Commercial payer and Medicare Advantage plan-specific policies may differ and are not applied by this skill.

**Sources:** [prior-auth-review-skill/README.md:25-26]()

---

## Medical Necessity Assessment

The core clinical reasoning phase maps submitted evidence against policy criteria to determine whether the request meets medical necessity standards.

### Assessment Workflow

```mermaid
graph TD
    Docs["Clinical Documentation"]
    Policy["Coverage Policy Criteria"]
    
    subgraph "Evidence Extraction"
        Parse["Parse clinical notes"]
        Extract["Extract structured data:<br/>- Symptoms/findings<br/>- Prior treatments<br/>- Test results<br/>- Severity indicators"]
    end
    
    subgraph "Criteria Mapping"
        Map["Map evidence to policy criteria"]
        Eval["Evaluate each criterion:<br/>- Met<br/>- Not Met<br/>- Insufficient Documentation"]
    end
    
    subgraph "Decision Logic"
        AllMet{"All criteria<br/>satisfied?"}
        MissingDocs{"Missing critical<br/>documentation?"}
        Approve["Recommendation: APPROVE"]
        Pend["Recommendation: PEND<br/>(request additional info)"]
    end
    
    Docs --> Parse
    Parse --> Extract
    
    Extract --> Map
    Policy --> Map
    
    Map --> Eval
    Eval --> AllMet
    
    AllMet -->|Yes| Approve
    AllMet -->|No| MissingDocs
    MissingDocs -->|Yes| Pend
    MissingDocs -->|No| Pend
    
    Approve --> Output["assessment.json"]
    Pend --> Output
```

**Sources:** [prior-auth-review-skill/README.md:38-41]()

### Clinical Evidence Extraction

The subskill extracts structured clinical data from unstructured documentation:

**Extracted Elements:**
- **Clinical Findings**: Symptoms, exam findings, imaging results
- **Prior Treatments**: Medications tried, therapies completed, surgical history
- **Severity Indicators**: Functional impairment, pain scales, quality of life measures
- **Timeline**: Onset, progression, acute vs. chronic status

### Criteria Matching Logic

Each coverage policy criterion is evaluated against extracted evidence:

| Criterion Status | Definition | Example |
|------------------|------------|---------|
| **Met** | Evidence clearly satisfies requirement | "Failed 3 months conservative therapy" documented when policy requires conservative treatment failure |
| **Not Met** | Evidence contradicts or fails to satisfy requirement | No documentation of prior imaging when policy requires it |
| **Insufficient** | Ambiguous or incomplete documentation | Mentions "prior treatment" but doesn't specify type or duration |

**Sources:** [prior-auth-review-skill/README.md:38-39]()

---

## Recommendation Generation

Based on medical necessity assessment, the subskill generates one of two recommendations following a conservative decision logic.

### Decision Logic Behavior

```mermaid
graph TD
    Start["Assessment Complete"]
    
    AllCriteria{"All policy criteria<br/>clearly met?"}
    Evidence{"Sufficient clinical<br/>evidence documented?"}
    
    Approve["RECOMMENDATION:<br/>APPROVE"]
    Pend["RECOMMENDATION:<br/>PEND"]
    
    Start --> AllCriteria
    
    AllCriteria -->|Yes| Evidence
    AllCriteria -->|No| Pend
    
    Evidence -->|Yes| Approve
    Evidence -->|No| Pend
    
    Approve --> Rationale1["Generate approval rationale:<br/>- Criteria satisfied<br/>- Supporting evidence<br/>- Policy citations"]
    
    Pend --> Rationale2["Generate pend rationale:<br/>- Unmet criteria<br/>- Missing documentation<br/>- Required information list"]
```

**Sources:** [prior-auth-review-skill/README.md:40-41]()

### AI Decision Constraints

**Default Behavior:** The skill recommends only `APPROVE` or `PEND`, never `DENY`

**Rationale:**
- Conservative approach ensures human review of negative determinations
- Prevents AI from making potentially harmful denial decisions
- Allows payer organization to maintain full control over denials

**Configurability:** Decision logic can be modified in the skill's `rubric.md` file for organization-specific requirements

**Sources:** [prior-auth-review-skill/README.md:23]()

### Recommendation Components

Each recommendation includes:

1. **Decision**: APPROVE or PEND
2. **Rationale**: Detailed explanation linking evidence to policy
3. **Policy Citations**: Specific LCD/NCD sections applied
4. **Evidence Summary**: Key clinical findings that support the decision
5. **Next Steps**: 
   - If APPROVE: Proceed to Subskill 2 for finalization
   - If PEND: List of required additional documentation

**Sources:** [prior-auth-review-skill/README.md:40-41]()

---

## Output Format

The subskill generates a structured JSON assessment document stored in the waypoint directory.

### Assessment Document Structure

**File Path:** `waypoints/assessment.json`

**Document Schema:**

```json
{
  "request_metadata": {
    "member_id": "string",
    "member_name": "string",
    "service_date": "YYYY-MM-DD",
    "requesting_provider_npi": "string"
  },
  "validation_results": {
    "provider": {
      "npi_valid": true,
      "name": "string",
      "specialty": "string"
    },
    "diagnosis_codes": [
      {
        "code": "string",
        "description": "string",
        "valid": true
      }
    ],
    "procedure_codes": [
      {
        "code": "string",
        "description": "string",
        "valid": true
      }
    ]
  },
  "coverage_policies": [
    {
      "policy_type": "LCD | NCD",
      "policy_number": "string",
      "title": "string",
      "criteria": ["array of strings"]
    }
  ],
  "clinical_assessment": {
    "extracted_evidence": {
      "symptoms": ["array of strings"],
      "prior_treatments": ["array of strings"],
      "test_results": ["array of strings"]
    },
    "criteria_evaluation": [
      {
        "criterion": "string",
        "status": "Met | Not Met | Insufficient",
        "evidence": "string"
      }
    ]
  },
  "recommendation": {
    "decision": "APPROVE | PEND",
    "rationale": "string",
    "policy_citations": ["array of strings"],
    "next_steps": "string"
  }
}
```

**Sources:** [prior-auth-review-skill/README.md:43]()

### Waypoint Architecture

The assessment document serves as a **waypoint** in the Prior Authorization workflow:

- **Purpose**: Enable workflow resumption and provide audit trail
- **Persistence**: Stored to disk for recovery from interruptions
- **Handoff**: Consumed by Subskill 2 (Decision & Notification) after human review
- **Audit**: Complete record of validation, evidence, and reasoning

**Sources:** [prior-auth-review-skill/README.md:43]()

---

## Human Decision Point

Upon completion of the assessment, the workflow pauses for mandatory human review before proceeding to the decision phase.

### Review Requirements

```mermaid
graph LR
    Assessment["assessment.json<br/>Generated"]
    
    subgraph "Human Review"
        Present["Present to<br/>Payer Professional"]
        Review["Review:<br/>- Validation results<br/>- Evidence extraction<br/>- Criteria mapping<br/>- Recommendation"]
        Decision{"Accept AI<br/>recommendation?"}
    end
    
    subgraph "Next Actions"
        Proceed["Proceed to<br/>Subskill 2"]
        Override["Override and<br/>document reasoning"]
        Reject["Reject and<br/>re-assess"]
    end
    
    Assessment --> Present
    Present --> Review
    Review --> Decision
    
    Decision -->|Yes| Proceed
    Decision -->|Need changes| Override
    Decision -->|Fundamentally flawed| Reject
```

**Sources:** [prior-auth-review-skill/README.md:45]()

### Professional Responsibilities

The reviewing professional must:

1. **Verify Validation**: Confirm NPI, ICD-10, and CPT/HCPCS validations are correct
2. **Review Evidence Extraction**: Ensure clinical data was accurately extracted from documentation
3. **Assess Criteria Mapping**: Validate that evidence was correctly mapped to policy criteria
4. **Evaluate Recommendation**: Determine if the APPROVE/PEND recommendation is appropriate
5. **Document Decision**: If overriding, document the professional's reasoning

**No Auto-Approval:** The skill never finalizes a decision autonomously. Human confirmation is always required before proceeding to Subskill 2.

**Sources:** [prior-auth-review-skill/README.md:20-22](), [prior-auth-review-skill/README.md:45]()

---

## Integration with MCP Servers

The Intake & Assessment subskill integrates with three MCP servers and one web data source to perform validation and policy retrieval.

### MCP Dependency Map

| MCP Server | Purpose | API Called | Data Retrieved |
|------------|---------|------------|----------------|
| **NPI Registry** | Provider validation | `npi-registry` MCP | Provider credentials, taxonomy, specialty, location |
| **ICD-10 Codes** | Diagnosis validation | `icd10-codes` MCP (batch mode) | Code descriptions, validity status |
| **CMS Coverage** | Policy search | `cms-coverage` MCP | LCDs, NCDs, coverage criteria |
| **WebFetch** | CPT/HCPCS validation | HTTPS to CMS Fee Schedule | Procedure descriptions, billing codes |

**Installation:** All MCP servers must be installed prior to using this subskill (see [Installation and Usage](#2.2))

**Sources:** [prior-auth-review-skill/README.md:34-37](), [README.md:44-58]()

---

## Error Handling and Edge Cases

The subskill implements defensive error handling for common validation and assessment issues.

### Validation Failures

| Error Condition | Handling Strategy | User Impact |
|-----------------|-------------------|-------------|
| **Invalid NPI** | Flag provider validation failure, allow manual override | Professional must confirm provider manually |
| **Unknown ICD-10 Code** | Flag code as invalid, request clarification | Pend request until valid diagnosis provided |
| **CPT Not in Fee Schedule** | Flag code validation failure | Pend request or manual code verification |
| **No Coverage Policy Found** | Flag missing policy, allow manual policy attachment | Professional must provide policy or approve based on clinical judgment |

### Assessment Edge Cases

- **Incomplete Documentation**: Generates PEND recommendation with specific documentation requests
- **Conflicting Evidence**: Highlights contradictions for professional review
- **Multiple Applicable Policies**: Evaluates all policies, uses most restrictive criteria
- **Experimental/Investigational Services**: Flags for manual review (coverage policies may exclude)

**Sources:** [prior-auth-review-skill/README.md:40-41]()

---

## Summary

The Intake & Assessment subskill automates the data-intensive phases of prior authorization review, performing validation, policy search, and medical necessity assessment to generate a preliminary recommendation. It integrates with NPI Registry, ICD-10 Codes, and CMS Coverage MCP servers to ensure data integrity, then applies clinical reasoning to map evidence against policy criteria. The output is a structured assessment document that requires human review before proceeding to the decision phase in Subskill 2.

**Key Characteristics:**
- **Conservative Decision Logic**: Only recommends APPROVE or PEND, never DENY
- **Multi-Source Validation**: Leverages three MCP servers plus web data
- **Structured Output**: JSON waypoint format enables audit trail and workflow resumption
- **Human Oversight**: Mandatory review gate before decision finalization

**Sources:** [prior-auth-review-skill/README.md:27-45]()

---

# Page: Decision & Notification Subskill

# Decision & Notification Subskill

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/release.yml](.github/workflows/release.yml)
- [README.md](README.md)
- [clinical-trial-protocol-skill/README.md](clinical-trial-protocol-skill/README.md)
- [prior-auth-review-skill/README.md](prior-auth-review-skill/README.md)

</details>



## Purpose and Scope

This document describes **Subskill 2** of the Prior Authorization Review skill, which handles the decision finalization and provider notification stages of the prior authorization workflow. This subskill enforces human oversight requirements by requiring explicit confirmation of AI-generated recommendations before finalizing authorization decisions and generating provider notifications.

For documentation of the initial assessment and recommendation generation, see [Intake & Assessment Subskill](#3.2.1). For general information about the Prior Auth Review skill's architecture, see [Prior Authorization Review](#3.2).

**Sources:** [prior-auth-review-skill/README.md:47-66]()

---

## Overview

Subskill 2 operates as a **human-in-the-loop decision gate** that prevents automatic authorization decisions. The subskill loads the assessment generated by Subskill 1, presents the AI recommendation to a human reviewer, captures their explicit decision (confirm, reject, or override), and generates the appropriate provider notification documentation.

This design ensures that all authorization decisions remain under human control while leveraging AI to structure the review process and documentation.

**Key Characteristics:**

| Characteristic | Description |
|----------------|-------------|
| **Input Artifact** | `waypoints/assessment.json` from Subskill 1 |
| **Human Interaction** | Required - no automatic decision finalization |
| **Decision Options** | Confirm, Reject, or Override AI recommendation |
| **Output Artifacts** | `waypoints/decision.json`, `outputs/notification_letter.txt` |
| **Audit Trail** | Complete documentation of decision rationale |

**Sources:** [prior-auth-review-skill/README.md:47-66]()

---

## Decision Workflow

The subskill implements a strict human-confirmation workflow that requires active user input before any decision is finalized.

```mermaid
stateDiagram-v2
    [*] --> LoadAssessment: "Subskill 2 invoked"
    
    LoadAssessment --> PresentRecommendation: "Read waypoints/assessment.json"
    
    state PresentRecommendation {
        [*] --> DisplayEvidence: "Show AI recommendation"
        DisplayEvidence --> AwaitHumanInput: "Present APPROVE/PEND with clinical rationale"
    }
    
    AwaitHumanInput --> Confirm: "User confirms recommendation"
    AwaitHumanInput --> Reject: "User rejects recommendation"
    AwaitHumanInput --> Override: "User overrides with different decision"
    
    state Confirm {
        [*] --> AcceptRecommendation: "Use AI recommendation as-is"
        AcceptRecommendation --> FinalizeConfirm
    }
    
    state Reject {
        [*] --> RequestJustification: "Capture rejection reason"
        RequestJustification --> FinalizeReject
    }
    
    state Override {
        [*] --> RequestOverride: "Capture new decision + rationale"
        RequestOverride --> FinalizeOverride
    }
    
    FinalizeConfirm --> GenerateArtifacts
    FinalizeReject --> GenerateArtifacts
    FinalizeOverride --> GenerateArtifacts
    
    state GenerateArtifacts {
        [*] --> CreateDecisionRecord: "Write waypoints/decision.json"
        CreateDecisionRecord --> GenerateNotification: "Write outputs/notification_letter.txt"
        GenerateNotification --> AuditTrail: "Document complete decision path"
    }
    
    GenerateArtifacts --> [*]: "Decision finalized"
    
    note right of AwaitHumanInput
        No automatic finalization -
        human action required to proceed
    end note
```

**Sources:** [prior-auth-review-skill/README.md:47-66]()

---

## Human Decision Point Requirements

The subskill enforces a **mandatory human decision gate** that distinguishes it from fully automated systems. No authorization decision is finalized without explicit human action.

### Decision Options

| Decision | Description | When Used | Documentation Required |
|----------|-------------|-----------|----------------------|
| **Confirm** | Accept AI recommendation as-is | Reviewer agrees with AI assessment and supporting evidence | Standard decision record with AI rationale |
| **Reject** | Decline to authorize based on AI recommendation | Reviewer determines the recommendation should not be followed | Rejection reason and alternative action |
| **Override** | Change AI recommendation to different decision | Reviewer has additional clinical context or policy knowledge | Override justification with clinical/policy rationale |

### Audit Trail Capture

Every decision path creates a complete audit trail documenting:

- **Original AI Recommendation:** APPROVE or PEND decision from Subskill 1
- **Human Action:** Confirm, Reject, or Override with timestamp
- **Final Decision:** The actual authorization determination
- **Rationale:** Clinical reasoning, policy citations, or override justification
- **Reviewer Identity:** Professional responsible for decision (implementation-specific)

**Sources:** [prior-auth-review-skill/README.md:47-66]()

---

## Decision Finalization Process

Once the human reviewer provides their input, the subskill generates the decision artifacts and supporting documentation.

```mermaid
graph TB
    subgraph "Input: waypoints/assessment.json"
        A1["ai_recommendation: APPROVE|PEND"]
        A2["clinical_evidence"]
        A3["policy_criteria_mapping"]
        A4["medical_necessity_assessment"]
    end
    
    subgraph "Human Decision Gate"
        H1["User reviews AI recommendation"]
        H2["User selects: Confirm/Reject/Override"]
        H3["User provides rationale if override/reject"]
    end
    
    subgraph "Decision Logic"
        D1["Determine final_decision"]
        D2["Generate authorization_number if APPROVE"]
        D3["Generate documentation_requests if PEND"]
        D4["Document decision_path"]
    end
    
    subgraph "Output: waypoints/decision.json"
        O1["final_decision: APPROVE|PEND|DENY"]
        O2["authorization_number or pend_reasons"]
        O3["decision_timestamp"]
        O4["human_action: confirm|reject|override"]
        O5["override_rationale if applicable"]
        O6["complete_audit_trail"]
    end
    
    A1 --> H1
    A2 --> H1
    A3 --> H1
    A4 --> H1
    
    H1 --> H2
    H2 --> H3
    H3 --> D1
    
    D1 --> D2
    D1 --> D3
    D1 --> D4
    
    D2 --> O1
    D2 --> O2
    D3 --> O2
    D4 --> O3
    D4 --> O4
    D4 --> O5
    D4 --> O6
```

### Approval Path

For **APPROVE** decisions (confirmed or overridden to approve):

1. Generate unique authorization number
2. Record approved service details (CPT codes, quantities, dates)
3. Document authorization validity period
4. Create decision record linking to supporting evidence

### Pend Path

For **PEND** decisions (additional information needed):

1. Generate list of required documentation
2. Specify clinical information gaps from policy criteria
3. Set pend expiration date
4. Create instructions for provider resubmission

### Denial Path

For **DENY** decisions (overridden to deny):

1. Document denial rationale with policy citations
2. Reference specific policy criteria not met
3. Include appeal rights information
4. Create structured denial reasoning

**Note:** The AI does not recommend DENY by default - denial decisions require human override with documented justification.

**Sources:** [prior-auth-review-skill/README.md:19-24](), [prior-auth-review-skill/README.md:47-66]()

---

## Notification Letter Generation

After the decision is finalized, the subskill generates a provider notification letter in `outputs/notification_letter.txt`.

### Notification Structure

```mermaid
graph TD
    subgraph "Decision Data"
        DD1["waypoints/decision.json"]
        DD2["waypoints/assessment.json"]
    end
    
    subgraph "Letter Generation"
        LG1["Header: Member, Provider, Service Info"]
        LG2["Decision Section: APPROVE|PEND|DENY"]
        LG3["Rationale Section"]
        LG4["Next Steps Section"]
        LG5["Footer: Contact Info, Appeal Rights"]
    end
    
    subgraph "Notification Types"
        NT1["Approval Letter:<br/>Authorization Number<br/>Approved Services<br/>Validity Period"]
        NT2["Pend Letter:<br/>Documentation Requests<br/>Resubmission Instructions<br/>Pend Expiration"]
        NT3["Denial Letter:<br/>Denial Rationale<br/>Policy Citations<br/>Appeal Process"]
    end
    
    DD1 --> LG1
    DD2 --> LG1
    DD1 --> LG2
    DD1 --> LG3
    DD1 --> LG4
    
    LG2 --> NT1
    LG2 --> NT2
    LG2 --> NT3
    
    LG5 --> NT1
    LG5 --> NT2
    LG5 --> NT3
```

### Notification Content Elements

**Approval Notifications:**
- Authorization number and effective dates
- Approved CPT/HCPCS codes and quantities
- Service location and frequency limits
- Provider instructions for claim submission

**Pend Notifications:**
- Specific documentation requirements
- Clinical information gaps identified
- Resubmission deadline
- Contact information for questions

**Denial Notifications:**
- Policy-based denial rationale
- Clinical criteria not met
- Appeal rights and process
- Reconsideration options

**Sources:** [prior-auth-review-skill/README.md:60-64]()

---

## Output Artifacts

Subskill 2 produces two primary output files that document the decision and provide provider communication.

### Decision Record: waypoints/decision.json

```mermaid
graph LR
    subgraph "waypoints/decision.json Structure"
        DR1["final_decision"]
        DR2["authorization_details"]
        DR3["human_action_metadata"]
        DR4["audit_trail"]
        DR5["timestamps"]
    end
    
    DR1 -->|"APPROVE"| DR2A["authorization_number<br/>approved_services<br/>validity_period"]
    DR1 -->|"PEND"| DR2B["documentation_requests<br/>pend_reasons<br/>resubmit_deadline"]
    DR1 -->|"DENY"| DR2C["denial_rationale<br/>policy_citations<br/>appeal_info"]
    
    DR3 --> DR3A["action: confirm|reject|override"]
    DR3 --> DR3B["rationale"]
    DR3 --> DR3C["reviewer_notes"]
    
    DR4 --> DR4A["ai_recommendation"]
    DR4 --> DR4B["human_decision"]
    DR4 --> DR4C["override_justification"]
```

**File Location:** `waypoints/decision.json`

**Purpose:** Structured decision record for audit, compliance, and system integration

**Key Fields:**
- `final_decision`: APPROVE, PEND, or DENY
- `human_action`: confirm, reject, or override
- `authorization_number`: Generated for approvals
- `override_rationale`: Required for overrides
- `complete_audit_trail`: Links back to assessment.json

**Sources:** [prior-auth-review-skill/README.md:60-64]()

### Provider Notification: outputs/notification_letter.txt

**File Location:** `outputs/notification_letter.txt`

**Purpose:** Human-readable provider communication in standard letter format

**Characteristics:**
- Plain text format for easy transmission
- Professional medical communication style
- Includes all regulatory required elements
- Ready for provider portal or fax delivery

**Sources:** [prior-auth-review-skill/README.md:60-64]()

---

## Integration with Subskill 1

Subskill 2 operates as the second stage of a two-phase workflow, consuming the output of Subskill 1.

### Data Flow Between Subskills

| Artifact | Producer | Consumer | Purpose |
|----------|----------|----------|---------|
| `waypoints/assessment.json` | Subskill 1 | Subskill 2 | AI recommendation with supporting evidence |
| `waypoints/decision.json` | Subskill 2 | External systems | Final decision record with audit trail |
| `outputs/notification_letter.txt` | Subskill 2 | Provider portal | Provider communication |

### Workflow Continuity

```mermaid
sequenceDiagram
    participant U as "User"
    participant S1 as "Subskill 1:<br/>Intake & Assessment"
    participant WP as "waypoints/"
    participant S2 as "Subskill 2:<br/>Decision & Notification"
    participant OUT as "outputs/"
    
    U->>S1: "Submit PA request data"
    S1->>S1: "Validate codes, check coverage"
    S1->>S1: "Assess medical necessity"
    S1->>WP: "Write assessment.json"
    
    Note over S1,WP: Human Decision Point 1:<br/>Review AI recommendation
    
    U->>S2: "Invoke decision subskill"
    S2->>WP: "Read assessment.json"
    S2->>U: "Present AI recommendation"
    
    Note over U,S2: Human Decision Point 2:<br/>Confirm/Reject/Override
    
    U->>S2: "Provide decision + rationale"
    S2->>S2: "Finalize decision logic"
    S2->>WP: "Write decision.json"
    S2->>OUT: "Write notification_letter.txt"
    S2->>U: "Decision finalized"
```

**Sources:** [prior-auth-review-skill/README.md:27-66]()

---

## Compliance and Audit Considerations

The subskill's design supports regulatory compliance through comprehensive documentation and human accountability.

### Audit Trail Completeness

Every decision contains:

1. **AI Component:** Original recommendation with confidence assessment
2. **Human Component:** Reviewer action and rationale
3. **Final Determination:** Actual authorization decision
4. **Temporal Record:** Timestamps for each stage
5. **Policy Citations:** Coverage criteria applied

### Regulatory Alignment

| Requirement | Implementation |
|-------------|----------------|
| **Human Decision Authority** | No automatic finalization - all decisions require human action |
| **Explainability** | AI recommendation includes clinical reasoning and policy mapping |
| **Override Documentation** | All overrides require documented justification |
| **Appeal Support** | Complete decision record supports appeal review |
| **Data Integrity** | Immutable waypoint files preserve decision history |

**Sources:** [prior-auth-review-skill/README.md:17-26]()

---

## Limitations and Disclaimers

### Coverage Policy Scope

The skill uses Medicare LCDs/NCDs from the CMS Coverage MCP Connector. For commercial or Medicare Advantage plans, payer-specific policies may differ and are not automatically applied. Organizations must configure the skill to use their own coverage criteria.

### AI Decision Behavior

By default, the AI recommends only APPROVE or PEND decisions - it does not recommend DENY. This prevents automatic denials and ensures that any denial decision requires explicit human judgment with documented rationale.

**Note:** Decision logic is configurable through the skill's internal rubric, but the human-in-the-loop requirement remains mandatory regardless of configuration.

**Sources:** [prior-auth-review-skill/README.md:17-26]()

---

## Summary

Subskill 2 implements the **decision finalization and provider notification** phases of the prior authorization workflow with mandatory human oversight. Key design principles include:

- **No Automatic Decisions:** Human confirmation required for all finalizations
- **Flexible Decision Options:** Confirm, reject, or override AI recommendations
- **Complete Audit Trail:** Comprehensive documentation of decision rationale
- **Structured Outputs:** Machine-readable decision records and human-readable notifications
- **Compliance Support:** Design supports regulatory requirements for transparency and accountability

The subskill ensures that AI serves as a decision support tool rather than an autonomous decision-maker, preserving human judgment while improving workflow efficiency and documentation quality.

**Sources:** [prior-auth-review-skill/README.md:1-78](), [README.md:28-35]()

---

# Page: FHIR Developer Guide

# FHIR Developer Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/release.yml](.github/workflows/release.yml)
- [README.md](README.md)
- [fhir-developer-skill/SKILL.md](fhir-developer-skill/SKILL.md)
- [fhir-developer-skill/references/bundles.md](fhir-developer-skill/references/bundles.md)
- [fhir-developer-skill/references/pagination.md](fhir-developer-skill/references/pagination.md)
- [fhir-developer-skill/references/resource-examples.md](fhir-developer-skill/references/resource-examples.md)
- [fhir-developer-skill/references/smart-auth.md](fhir-developer-skill/references/smart-auth.md)

</details>



## Purpose and Scope

This document provides an overview of the FHIR Developer skill, a specialized knowledge base and tooling for building HL7 FHIR R4-compliant healthcare APIs. The skill enables rapid development of FHIR REST endpoints, including resource validation, error handling, authorization, and API operations.

For detailed information on specific topics, see:
- FHIR R4 resource structures, required fields, and value sets: [FHIR R4 Resource Structures](#3.3.1)
- RESTful endpoint patterns, HTTP status codes, and Bundle operations: [FHIR API Patterns](#3.3.2)
- OAuth 2.0 flows and scope enforcement: [SMART on FHIR Authorization](#3.3.3)
- FastAPI project scaffolding: [FHIR Project Scaffolding Tool](#3.3.4)

**Sources:** [fhir-developer-skill/SKILL.md:1-11](), [README.md:19-25]()

## Skill Overview

The FHIR Developer skill provides specialized knowledge for building healthcare interoperability endpoints compliant with the HL7 FHIR R4 specification. Unlike the Clinical Trial Protocol Generator ([3.1](#3.1)) which focuses on research protocols, or Prior Authorization Review ([3.2](#3.2)) which handles insurance workflows, this skill is targeted at software engineers building healthcare data exchange systems.

The skill operates as a comprehensive reference guide with no external MCP server dependencies. All knowledge is embedded in the skill's reference documentation and can be used immediately after installation via:

```bash
/plugin install fhir-developer@healthcare
```

**Sources:** [README.md:19-25](), [fhir-developer-skill/SKILL.md:1-11]()

## Skill Architecture

### File Structure

```mermaid
graph TD
    SKILL["fhir-developer-skill/SKILL.md"]
    
    REF1["references/resource-examples.md"]
    REF2["references/smart-auth.md"]
    REF3["references/pagination.md"]
    REF4["references/bundles.md"]
    
    SCRIPT["scripts/setup_fhir_project.py"]
    
    SKILL -->|"Quick Reference Tables"| QUICK["HTTP Status Codes<br/>Required Fields<br/>Value Sets<br/>Coding Systems"]
    SKILL -->|"Validation Patterns"| VALID["operation_outcome()<br/>VALID_OBS_STATUS<br/>Pydantic Models"]
    SKILL -->|"References"| REF1
    SKILL -->|"References"| REF2
    SKILL -->|"References"| REF3
    SKILL -->|"References"| REF4
    SKILL -->|"Tooling"| SCRIPT
    
    REF1 -->|"Complete JSON"| RES["Patient<br/>Observation<br/>Encounter<br/>Condition<br/>MedicationRequest"]
    REF2 -->|"OAuth Flows"| AUTH["EHR Launch<br/>Standalone Launch<br/>Backend Services"]
    REF3 -->|"Search Results"| PAGE["_count/_offset<br/>Link Relations<br/>Bundle Responses"]
    REF4 -->|"Multi-Resource"| BUNDLE["Transaction (Atomic)<br/>Batch (Independent)"]
```

**Sources:** [fhir-developer-skill/SKILL.md:1-295](), [fhir-developer-skill/references/resource-examples.md:1-197](), [fhir-developer-skill/references/smart-auth.md:1-204](), [fhir-developer-skill/references/pagination.md:1-106](), [fhir-developer-skill/references/bundles.md:1-161]()

## Knowledge Domains

The skill provides expert guidance across four primary domains:

### 1. Resource Structures and Validation

Covers the seven core FHIR resources used in most healthcare APIs:

| Resource | Required Fields | Cardinality Source |
|----------|----------------|-------------------|
| `Patient` | None | All fields 0..1 or 0..* |
| `Observation` | `status`, `code` | [SKILL.md:30-38]() |
| `Encounter` | `status`, `class` | [SKILL.md:30-38]() |
| `Condition` | `subject` | [SKILL.md:30-38]() |
| `MedicationRequest` | `status`, `intent`, `medication[x]`, `subject` | [SKILL.md:30-38]() |
| `Medication` | None | All fields optional |
| `Bundle` | `type` | [SKILL.md:30-38]() |

The skill emphasizes the critical distinction between cardinality `0..1` (optional) and `1..1` (required), as documented in [fhir-developer-skill/SKILL.md:43-53](). A common error is treating `subject` or `period` on `Encounter` as required when they are actually optional (0..1 cardinality).

**Sources:** [fhir-developer-skill/SKILL.md:30-53](), [fhir-developer-skill/references/resource-examples.md:1-197]()

### 2. HTTP Status Codes and Error Handling

The skill provides definitive mappings for FHIR-specific status codes:

```mermaid
graph LR
    REQ["HTTP Request"]
    
    REQ -->|"Malformed JSON"| E400["400 Bad Request<br/>OperationOutcome"]
    REQ -->|"Missing/Invalid Token"| E401["401 Unauthorized<br/>RFC 6750"]
    REQ -->|"Valid Token, Wrong Scope"| E403["403 Forbidden<br/>OperationOutcome"]
    REQ -->|"Resource Not Found"| E404["404 Not Found<br/>OperationOutcome"]
    REQ -->|"ETag Mismatch"| E412["412 Precondition Failed<br/>If-Match Header"]
    REQ -->|"Missing Required Field"| E422["422 Unprocessable Entity<br/>OperationOutcome"]
    REQ -->|"Invalid Enum Value"| E422B["422 Unprocessable Entity<br/>OperationOutcome"]
    
    REQ -->|"Successful Read"| S200["200 OK"]
    REQ -->|"Successful Create"| S201["201 Created<br/>Location Header"]
    REQ -->|"Successful Delete"| S204["204 No Content"]
```

The `operation_outcome()` helper function pattern is standardized in [fhir-developer-skill/SKILL.md:103-107]() for Python/FastAPI implementations.

**Sources:** [fhir-developer-skill/SKILL.md:17-28](), [fhir-developer-skill/references/resource-examples.md:130-160]()

### 3. Value Sets and Coding Systems

The skill includes comprehensive enum definitions for status codes and coding system URLs:

**Status Value Sets:**
- `Observation.status`: `registered | preliminary | final | amended | corrected | cancelled | entered-in-error | unknown` ([SKILL.md:63-64]())
- `Encounter.status`: `planned | arrived | triaged | in-progress | onleave | finished | cancelled | entered-in-error | unknown` ([SKILL.md:66-67]())
- `MedicationRequest.intent`: `proposal | plan | order | original-order | reflex-order | filler-order | instance-order | option` ([SKILL.md:86-87]())

**Coding System URLs:**
| System | URL |
|--------|-----|
| LOINC | `http://loinc.org` |
| SNOMED CT | `http://snomed.info/sct` |
| RxNorm | `http://www.nlm.nih.gov/research/umls/rxnorm` |
| ICD-10 | `http://hl7.org/fhir/sid/icd-10` |

Invalid enum values must return `422 Unprocessable Entity` with an `OperationOutcome` resource, as specified in [fhir-developer-skill/SKILL.md:58]().

**Sources:** [fhir-developer-skill/SKILL.md:56-91](), [fhir-developer-skill/SKILL.md:157-168]()

### 4. Data Type Patterns

The skill distinguishes between `Coding` (direct) and `CodeableConcept` (wrapped) types, a common source of implementation errors:

```mermaid
graph TB
    subgraph "Coding (Direct)"
        EC["Encounter.class"]
        EC_JSON["{<br/>  'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode',<br/>  'code': 'AMB'<br/>}"]
        EC --> EC_JSON
    end
    
    subgraph "CodeableConcept (Wrapped)"
        OC["Observation.code"]
        CC["Condition.code"]
        MR["MedicationRequest.medicationCodeableConcept"]
        
        OC_JSON["{<br/>  'coding': [{<br/>    'system': 'http://loinc.org',<br/>    'code': '8480-6'<br/>  }],<br/>  'text': 'Systolic BP'<br/>}"]
        
        OC --> OC_JSON
        CC --> OC_JSON
        MR --> OC_JSON
    end
```

**Sources:** [fhir-developer-skill/SKILL.md:183-198]()

## Validation Implementation Patterns

The skill provides production-ready validation code in both Python/FastAPI and TypeScript/Express:

### Python FastAPI Pattern

The canonical validation pattern uses the `operation_outcome()` helper and explicit status code constants:

```python
# Defined in SKILL.md:103-107
def operation_outcome(severity: str, code: str, diagnostics: str)

# Validation set defined in SKILL.md:109-110
VALID_OBS_STATUS = {"registered", "preliminary", "final", "amended",
                    "corrected", "cancelled", "entered-in-error", "unknown"}

# Endpoint implementation pattern in SKILL.md:112-124
@app.post("/Observation", status_code=201)
async def create_observation(data: dict):
    # Returns JSONResponse with status_code=422 and OperationOutcome
```

### Pydantic v2 Models

The skill specifies the correct Pydantic v2 pattern using `Literal` (not the deprecated `const=True`):

```python
# From SKILL.md:144-153
from typing import Literal
from pydantic import BaseModel

class Patient(BaseModel):
    resourceType: Literal["Patient"] = "Patient"
    gender: Literal["male", "female", "other", "unknown"] | None = None
```

**Sources:** [fhir-developer-skill/SKILL.md:94-153]()

## Tooling: Project Scaffolding

The skill includes a project generation script that creates a complete FastAPI FHIR server:

```bash
python scripts/setup_fhir_project.py my_fhir_api
```

This script generates:
- Correct Pydantic v2 models with `Literal` types
- `OperationOutcome` helper functions
- Patient CRUD endpoints
- Proper `Content-Type: application/fhir+json` headers
- `Location` and `ETag` header handling

**Sources:** [fhir-developer-skill/SKILL.md:286-294]()

## When to Use This Skill

The skill is designed for four primary use cases, as documented in [fhir-developer-skill/SKILL.md:4-11]():

1. **Creating FHIR REST endpoints** for `Patient`, `Observation`, `Encounter`, `Condition`, `MedicationRequest`
2. **Validating FHIR resources** and returning proper HTTP status codes and error responses
3. **Implementing SMART on FHIR authorization** and OAuth scopes
4. **Working with Bundles**, transactions, batch operations, or search pagination

The skill does not use external MCP servers (unlike Prior Authorization Review which uses NPI Registry, ICD-10, and CMS Coverage MCPs). All knowledge is self-contained.

**Sources:** [fhir-developer-skill/SKILL.md:1-11](), [README.md:19-25]()

## Common Implementation Pitfalls

The skill explicitly documents frequent errors in FHIR API development:

```mermaid
graph LR
    M1["Making subject/period<br/>required on Encounter"]
    M2["Using CodeableConcept<br/>for Encounter.class"]
    M3["Returning 400<br/>for ETag mismatch"]
    M4["Returning 400<br/>for invalid enum"]
    M5["Missing Content-Type<br/>header"]
    M6["Missing Location<br/>header on create"]
    
    M1 -->|"Correct"| C1["Both are 0..1 optional<br/>Only status and class required"]
    M2 -->|"Correct"| C2["class uses Coding directly:<br/>{system: '...', code: 'AMB'}"]
    M3 -->|"Correct"| C3["412 Precondition Failed<br/>for If-Match failures"]
    M4 -->|"Correct"| C4["422 Unprocessable Entity<br/>for validation errors"]
    M5 -->|"Correct"| C5["application/fhir+json<br/>on all responses"]
    M6 -->|"Correct"| C6["Location: /Patient/{id}<br/>with 201 Created"]
```

**Sources:** [fhir-developer-skill/SKILL.md:207-216]()

## Implementation Checklist

The skill provides an 8-point checklist for FHIR API compliance:

1. Set `Content-Type: application/fhir+json` on all responses
2. Return `meta.versionId` and `meta.lastUpdated` on resources
3. Return `Location` header on create: `/Patient/{id}`
4. Return `ETag` header: `W/"{versionId}"`
5. Use OperationOutcome for all error responses
6. Validate required fields → 422 for missing
7. Validate enum values → 422 for invalid
8. Search returns Bundle with `type: "searchset"`

**Sources:** [fhir-developer-skill/SKILL.md:273-283]()

## RESTful Endpoint Patterns

Standard FHIR endpoint structure:

| Method | Path | Purpose | Status Code |
|--------|------|---------|-------------|
| POST | `/[ResourceType]` | Create | 201 + Location |
| GET | `/[ResourceType]/[id]` | Read | 200 |
| PUT | `/[ResourceType]/[id]` | Update | 200 |
| DELETE | `/[ResourceType]/[id]` | Delete | 204 |
| GET | `/[ResourceType]?param=value` | Search | 200 + Bundle |
| GET | `/metadata` | CapabilityStatement | 200 |
| POST | `/` | Bundle transaction/batch | 200/400 |

**Sources:** [fhir-developer-skill/SKILL.md:235-245]()

## Reference Documentation Structure

The skill organizes detailed implementation guidance in four reference files:

```mermaid
graph TD
    MAIN["SKILL.md<br/>Quick Reference"]
    
    RES["references/resource-examples.md"]
    SMART["references/smart-auth.md"]
    PAGE["references/pagination.md"]
    BUNDLE["references/bundles.md"]
    
    MAIN -->|"Complete JSON structures"| RES
    MAIN -->|"OAuth flows & scopes"| SMART
    MAIN -->|"Search result pagination"| PAGE
    MAIN -->|"Transaction vs batch"| BUNDLE
    
    RES -->|"8 resource types"| R1["Patient, Observation<br/>Encounter, Condition<br/>MedicationRequest, Medication<br/>OperationOutcome, CapabilityStatement"]
    
    SMART -->|"3 flows"| S1["EHR Launch<br/>Standalone Launch<br/>Backend Services"]
    SMART -->|"Scope syntax"| S2["patient/*.rs<br/>user/Encounter.cruds<br/>system/*.rs"]
    
    PAGE -->|"Parameters"| P1["_count, _offset, _page"]
    PAGE -->|"Link relations"| P2["self, first, previous<br/>next, last"]
    
    BUNDLE -->|"Atomicity"| B1["Transaction: all-or-nothing<br/>Batch: partial success"]
```

**Sources:** [fhir-developer-skill/SKILL.md:262-270](), [fhir-developer-skill/references/resource-examples.md:1-6](), [fhir-developer-skill/references/smart-auth.md:1-11](), [fhir-developer-skill/references/pagination.md:1-10](), [fhir-developer-skill/references/bundles.md:1-8]()

## Integration with Marketplace

The skill is registered in the marketplace as a standalone capability with no dependencies:

```json
{
  "name": "fhir-developer",
  "source": "./",
  "skills": ["./fhir-developer-skill"]
}
```

Installation command: `/plugin install fhir-developer@healthcare`

Unlike other skills in the marketplace, FHIR Developer does not require Python dependencies (Clinical Trial Protocol) or MCP servers (Prior Authorization Review). It is a pure knowledge skill.

**Sources:** [README.md:19-25]()

---

# Page: FHIR R4 Resource Structures

# FHIR R4 Resource Structures

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [fhir-developer-skill/SKILL.md](fhir-developer-skill/SKILL.md)
- [fhir-developer-skill/references/bundles.md](fhir-developer-skill/references/bundles.md)
- [fhir-developer-skill/references/pagination.md](fhir-developer-skill/references/pagination.md)
- [fhir-developer-skill/references/resource-examples.md](fhir-developer-skill/references/resource-examples.md)
- [fhir-developer-skill/references/smart-auth.md](fhir-developer-skill/references/smart-auth.md)

</details>



## Purpose and Scope

This document provides technical specifications for FHIR R4 resource structures, including required/optional fields, data types, value sets, and coding systems. It covers the structural elements of FHIR resources themselves—what fields exist, which are mandatory, and what values they accept.

For information about RESTful API endpoints, HTTP methods, and pagination, see [FHIR API Patterns](#3.3.2). For OAuth flows and scope enforcement, see [SMART on FHIR Authorization](#3.3.3). For project scaffolding tools, see [FHIR Project Scaffolding Tool](#3.3.4).

## Cardinality and Required Fields

FHIR uses cardinality notation to specify whether fields are required or optional. The validation logic must enforce only fields with cardinality starting with "1".

| Cardinality | Required | Validation |
|-------------|----------|------------|
| `0..1` | NO | Field is optional, may appear once |
| `0..*` | NO | Field is optional, may appear multiple times |
| `1..1` | YES | Field is required, must appear exactly once |
| `1..*` | YES | Field is required, must appear at least once |

**Critical Rule**: Only validate fields with cardinality `1..1` or `1..*` as required. A common mistake is making `subject` or `period` required on `Encounter` when they are `0..1` (optional).

Sources: [fhir-developer-skill/SKILL.md:43-53]()

### Cardinality Enforcement Pattern

```mermaid
graph TB
    Input["Incoming Resource JSON"]
    CheckRT["Check resourceType field"]
    LoadSchema["Load Resource Schema"]
    CheckCard["For each field with cardinality 1..1 or 1..*"]
    CheckPresent{"Field present?"}
    CheckEnum{"Enum value valid?"}
    Return422["Return 422 Unprocessable Entity<br/>OperationOutcome"]
    Return201["Return 201 Created<br/>with Location header"]
    
    Input --> CheckRT
    CheckRT --> LoadSchema
    LoadSchema --> CheckCard
    CheckCard --> CheckPresent
    CheckPresent -->|No| Return422
    CheckPresent -->|Yes| CheckEnum
    CheckEnum -->|Invalid| Return422
    CheckEnum -->|Valid| Return201
    
    style Return422 stroke-width:2px
    style Return201 stroke-width:2px
```

Sources: [fhir-developer-skill/SKILL.md:94-124]()

## Core Resource Types

### Resource Required Fields Matrix

The following table summarizes which fields are actually required (cardinality `1..1` or `1..*`) for each major resource type:

| Resource | Required Fields | Optional Fields (Examples) |
|----------|----------------|---------------------------|
| `Patient` | *(none)* | `identifier`, `name`, `gender`, `birthDate` |
| `Observation` | `status`, `code` | `subject`, `effectiveDateTime`, `value[x]` |
| `Encounter` | `status`, `class` | `subject`, `period`, `participant` |
| `Condition` | `subject` | `code`, `clinicalStatus`, `verificationStatus` |
| `MedicationRequest` | `status`, `intent`, `medication[x]`, `subject` | `dosageInstruction`, `authoredOn` |
| `Medication` | *(none)* | `code`, `form`, `ingredient` |
| `Bundle` | `type` | `entry`, `total`, `link` |
| `OperationOutcome` | `issue` (1..*) | N/A |

Sources: [fhir-developer-skill/SKILL.md:30-39](), [fhir-developer-skill/references/resource-examples.md:1-197]()

### Resource Dependency Graph

```mermaid
graph LR
    Patient["Patient<br/>(no required fields)"]
    Observation["Observation<br/>Required: status, code"]
    Encounter["Encounter<br/>Required: status, class"]
    Condition["Condition<br/>Required: subject"]
    MedRequest["MedicationRequest<br/>Required: status, intent,<br/>medication[x], subject"]
    Medication["Medication<br/>(no required fields)"]
    
    Observation -.->|"subject (0..1)"| Patient
    Encounter -.->|"subject (0..1)"| Patient
    Condition -->|"subject (1..1)"| Patient
    MedRequest -->|"subject (1..1)"| Patient
    MedRequest -.->|"medication[x] (1..1)<br/>can reference"| Medication
```

Sources: [fhir-developer-skill/references/resource-examples.md:15-128]()

## Patient Resource Structure

`Patient` has no required fields. All elements are optional (cardinality `0..1` or `0..*`).

**Key Fields**:
- `identifier` (0..*): External identifiers (MRN, SSN, etc.)
- `name` (0..*): HumanName elements with `family`, `given`
- `gender` (0..1): Enum - see [Value Sets](#value-sets-and-enumerations)
- `birthDate` (0..1): ISO 8601 date format

**Example Structure**:
```json
{
  "resourceType": "Patient",
  "id": "example",
  "meta": {"versionId": "1", "lastUpdated": "2024-01-15T10:30:00Z"},
  "identifier": [{"system": "http://hospital.example.org/mrn", "value": "12345"}],
  "name": [{"family": "Smith", "given": ["John"]}],
  "gender": "male",
  "birthDate": "1990-05-15"
}
```

Sources: [fhir-developer-skill/SKILL.md:33](), [fhir-developer-skill/references/resource-examples.md:15-29]()

## Observation Resource Structure

`Observation` requires `status` (1..1) and `code` (1..1). All other fields are optional.

**Required Fields**:
- `status` (1..1): Observation status enum
- `code` (1..1): CodeableConcept describing what was measured

**Common Optional Fields**:
- `subject` (0..1): Reference to Patient
- `effectiveDateTime` (0..1): When observation was made
- `valueQuantity` (0..1): Measured value with units
- `category` (0..*): Classification (e.g., vital-signs)

**Example Structure**:
```json
{
  "resourceType": "Observation",
  "status": "final",
  "category": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "vital-signs"}]}],
  "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6", "display": "Systolic blood pressure"}]},
  "subject": {"reference": "Patient/123"},
  "effectiveDateTime": "2024-01-15T10:30:00Z",
  "valueQuantity": {"value": 120, "unit": "mmHg", "system": "http://unitsofmeasure.org", "code": "mm[Hg]"}
}
```

Sources: [fhir-developer-skill/SKILL.md:34](), [fhir-developer-skill/references/resource-examples.md:31-45]()

## Encounter Resource Structure

`Encounter` requires `status` (1..1) and `class` (1..1). **Important**: `subject` and `period` are `0..1` (optional), not required.

**Required Fields**:
- `status` (1..1): Encounter status enum
- `class` (1..1): **Coding** (not CodeableConcept) - see [Data Type Patterns](#data-type-patterns)

**Common Optional Fields**:
- `subject` (0..1): Reference to Patient
- `period` (0..1): Start and end times
- `participant` (0..*): Practitioners involved

**Critical Note**: `class` uses `Coding` directly, not wrapped in `CodeableConcept`.

**Example Structure**:
```json
{
  "resourceType": "Encounter",
  "status": "in-progress",
  "class": {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "AMB", "display": "ambulatory"},
  "subject": {"reference": "Patient/123"},
  "period": {"start": "2024-01-15T09:00:00Z"}
}
```

Sources: [fhir-developer-skill/SKILL.md:35,52](), [fhir-developer-skill/references/resource-examples.md:47-61]()

## Condition Resource Structure

`Condition` requires only `subject` (1..1). Notably, `code` and `clinicalStatus` are optional despite being commonly used.

**Required Fields**:
- `subject` (1..1): Reference to Patient

**Common Optional Fields**:
- `code` (0..1): SNOMED CT diagnosis code
- `clinicalStatus` (0..1): active | inactive | resolved
- `verificationStatus` (0..1): confirmed | unconfirmed
- `onsetDateTime` (0..1): When condition started

**Example Structure**:
```json
{
  "resourceType": "Condition",
  "clinicalStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active"}]},
  "verificationStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-ver-status", "code": "confirmed"}]},
  "code": {"coding": [{"system": "http://snomed.info/sct", "code": "73211009", "display": "Diabetes mellitus"}]},
  "subject": {"reference": "Patient/123"},
  "onsetDateTime": "2020-03-15"
}
```

Sources: [fhir-developer-skill/SKILL.md:36](), [fhir-developer-skill/references/resource-examples.md:63-78]()

## MedicationRequest Resource Structure

`MedicationRequest` requires `status` (1..1), `intent` (1..1), `medication[x]` (1..1), and `subject` (1..1).

**Required Fields**:
- `status` (1..1): active | on-hold | cancelled | completed
- `intent` (1..1): proposal | plan | order
- `medication[x]` (1..1): Either `medicationCodeableConcept` or `medicationReference`
- `subject` (1..1): Reference to Patient

**Common Optional Fields**:
- `authoredOn` (0..1): When prescription was written
- `dosageInstruction` (0..*): Dosing details

**Choice Type Pattern**: The `medication[x]` field demonstrates FHIR's choice type pattern - exactly one of `medicationCodeableConcept` or `medicationReference` must be present.

**Example with CodeableConcept**:
```json
{
  "resourceType": "MedicationRequest",
  "status": "active",
  "intent": "order",
  "medicationCodeableConcept": {
    "coding": [{"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "1049502", "display": "Acetaminophen 325 MG"}]
  },
  "subject": {"reference": "Patient/456"}
}
```

**Example with Reference**:
```json
{
  "resourceType": "MedicationRequest",
  "status": "active",
  "intent": "order",
  "medicationReference": {"reference": "Medication/123"},
  "subject": {"reference": "Patient/456"}
}
```

Sources: [fhir-developer-skill/SKILL.md:37](), [fhir-developer-skill/references/resource-examples.md:80-111]()

## Bundle Resource Structure

`Bundle` requires only `type` (1..1). It serves as a container for collections of resources.

**Required Fields**:
- `type` (1..1): Bundle type enum (see [Value Sets](#bundle-type-values))

**Common Optional Fields**:
- `entry` (0..*): Resources contained in bundle
- `total` (0..1): Total matching results (for searchset)
- `link` (0..*): Navigation links (for pagination)

**Bundle Types**: `transaction`, `batch`, `searchset`, `history`, `collection`, `document`, `message`

For transaction vs batch semantics, see [FHIR API Patterns](#3.3.2).

Sources: [fhir-developer-skill/SKILL.md:39](), [fhir-developer-skill/references/bundles.md:1-161]()

## OperationOutcome Resource Structure

`OperationOutcome` is used for all error responses. It requires `issue` (1..*) - at least one issue must be present.

**Required Fields**:
- `issue` (1..*): Array of issue elements, each containing:
  - `severity` (1..1): fatal | error | warning | information
  - `code` (1..1): Error code from defined value set

**Common Optional Fields**:
- `issue.diagnostics` (0..1): Human-readable description
- `issue.expression` (0..*): FHIRPath to problematic field

**Example with Single Issue**:
```json
{
  "resourceType": "OperationOutcome",
  "issue": [{
    "severity": "error",
    "code": "not-found",
    "diagnostics": "Patient/999 not found"
  }]
}
```

**Example with Multiple Issues**:
```json
{
  "resourceType": "OperationOutcome",
  "issue": [
    {"severity": "error", "code": "required", "diagnostics": "Observation.status is required", "expression": ["Observation.status"]},
    {"severity": "error", "code": "required", "diagnostics": "Observation.code is required", "expression": ["Observation.code"]}
  ]
}
```

Sources: [fhir-developer-skill/SKILL.md:103-107](), [fhir-developer-skill/references/resource-examples.md:130-159]()

## Data Type Patterns

### Coding vs CodeableConcept

FHIR uses two distinct patterns for coded values. Understanding the difference is critical.

```mermaid
graph TB
    subgraph "Coding (Direct)"
        CodingStruct["Coding structure"]
        CodingFields["system: URL<br/>code: string<br/>display: string (optional)"]
        CodingStruct --> CodingFields
    end
    
    subgraph "CodeableConcept (Wrapper)"
        CCStruct["CodeableConcept structure"]
        CCCoding["coding: Coding[] (0..*)"]
        CCText["text: string (0..1)"]
        CCStruct --> CCCoding
        CCStruct --> CCText
        CCCoding --> CodingFields
    end
    
    EncClass["Encounter.class<br/>Uses: Coding"]
    ObsCode["Observation.code<br/>Uses: CodeableConcept"]
    CondCode["Condition.code<br/>Uses: CodeableConcept"]
    
    EncClass --> CodingStruct
    ObsCode --> CCStruct
    CondCode --> CCStruct
```

**Coding** - Direct structure with single code:
```json
{"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "AMB"}
```

**CodeableConcept** - Wrapper allowing multiple codings plus text:
```json
{
  "coding": [
    {"system": "http://loinc.org", "code": "8480-6"},
    {"system": "http://snomed.info/sct", "code": "271649006"}
  ],
  "text": "Systolic BP"
}
```

**Usage by Resource**:
- `Encounter.class` uses **Coding** directly
- `Observation.code` uses **CodeableConcept**
- `Condition.code` uses **CodeableConcept**
- Most other coded fields use **CodeableConcept**

Sources: [fhir-developer-skill/SKILL.md:183-193,212]()

### Reference Type

`Reference` creates links between resources.

**Structure**:
```json
{
  "reference": "Patient/123",
  "display": "John Smith",
  "type": "Patient"
}
```

**Fields**:
- `reference` (0..1): Literal reference (relative or absolute URL)
- `display` (0..1): Human-readable description
- `type` (0..1): Resource type being referenced
- `identifier` (0..1): Logical identifier when reference unknown

Sources: [fhir-developer-skill/SKILL.md:195-198]()

### Identifier Type

`Identifier` represents external business identifiers (MRN, SSN, NPI, etc.).

**Structure**:
```json
{
  "system": "http://hospital.example.org/mrn",
  "value": "12345",
  "type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v2-0203", "code": "MR"}]},
  "period": {"start": "2020-01-01"}
}
```

**Fields**:
- `system` (0..1): Namespace for the identifier
- `value` (0..1): The actual identifier value
- `type` (0..1): CodeableConcept describing identifier type
- `period` (0..1): Time period when identifier is valid

Sources: [fhir-developer-skill/SKILL.md:200-203]()

### Quantity Type

`Quantity` represents measured values with units.

**Structure**:
```json
{
  "value": 120,
  "unit": "mmHg",
  "system": "http://unitsofmeasure.org",
  "code": "mm[Hg]"
}
```

**Fields**:
- `value` (0..1): Numeric value
- `unit` (0..1): Human-readable unit
- `system` (0..1): System defining coded unit (typically UCUM)
- `code` (0..1): Coded form of unit

Sources: [fhir-developer-skill/references/resource-examples.md:43]()

## Value Sets and Enumerations

Value sets define the allowed string values for enum-like fields. Invalid values must return `422 Unprocessable Entity`.

### Patient.gender Values

`male | female | other | unknown`

Sources: [fhir-developer-skill/SKILL.md:60-61]()

### Observation.status Values

`registered | preliminary | final | amended | corrected | cancelled | entered-in-error | unknown`

**Validation Pattern** from [fhir-developer-skill/SKILL.md:109-122]():
```python
VALID_OBS_STATUS = {"registered", "preliminary", "final", "amended",
                    "corrected", "cancelled", "entered-in-error", "unknown"}

if data["status"] not in VALID_OBS_STATUS:
    return JSONResponse(status_code=422, content=operation_outcome(
        "error", "value", f"Invalid status '{data['status']}'"
    ))
```

Sources: [fhir-developer-skill/SKILL.md:63-64]()

### Encounter.status Values

`planned | arrived | triaged | in-progress | onleave | finished | cancelled | entered-in-error | unknown`

Sources: [fhir-developer-skill/SKILL.md:66-67]()

### Encounter.class Common Codes

| Code | Display | Use Case |
|------|---------|----------|
| `AMB` | ambulatory | Outpatient visits |
| `IMP` | inpatient encounter | Hospital admissions |
| `EMER` | emergency | Emergency department |
| `VR` | virtual | Telehealth |

**System**: `http://terminology.hl7.org/CodeSystem/v3-ActCode`

Sources: [fhir-developer-skill/SKILL.md:69-75]()

### Condition.clinicalStatus Values

`active | recurrence | relapse | inactive | remission | resolved`

**System**: `http://terminology.hl7.org/CodeSystem/condition-clinical`

Sources: [fhir-developer-skill/SKILL.md:77-78]()

### Condition.verificationStatus Values

`unconfirmed | provisional | differential | confirmed | refuted | entered-in-error`

**System**: `http://terminology.hl7.org/CodeSystem/condition-ver-status`

Sources: [fhir-developer-skill/SKILL.md:80-81]()

### MedicationRequest.status Values

`active | on-hold | cancelled | completed | entered-in-error | stopped | draft | unknown`

Sources: [fhir-developer-skill/SKILL.md:83-84]()

### MedicationRequest.intent Values

`proposal | plan | order | original-order | reflex-order | filler-order | instance-order | option`

Sources: [fhir-developer-skill/SKILL.md:86-87]()

### Bundle.type Values

`document | message | transaction | transaction-response | batch | batch-response | history | searchset | collection`

**Common Usage**:
- `transaction`: All-or-nothing atomic operations
- `batch`: Independent operations with partial success
- `searchset`: Search results with pagination
- `history`: Resource version history

Sources: [fhir-developer-skill/SKILL.md:89-90]()

## Coding Systems

FHIR uses standard medical coding systems identified by canonical URLs.

### Coding System URLs

| System | URL | Purpose |
|--------|-----|---------|
| LOINC | `http://loinc.org` | Lab tests and observations |
| SNOMED CT | `http://snomed.info/sct` | Clinical terminology |
| RxNorm | `http://www.nlm.nih.gov/research/umls/rxnorm` | Medications |
| ICD-10 | `http://hl7.org/fhir/sid/icd-10` | Diagnoses and procedures |
| v3-ActCode | `http://terminology.hl7.org/CodeSystem/v3-ActCode` | Encounter classes |
| Observation Category | `http://terminology.hl7.org/CodeSystem/observation-category` | Observation classifications |
| Condition Clinical | `http://terminology.hl7.org/CodeSystem/condition-clinical` | Condition clinical status |
| Condition Ver Status | `http://terminology.hl7.org/CodeSystem/condition-ver-status` | Condition verification |

Sources: [fhir-developer-skill/SKILL.md:157-168]()

### Common LOINC Codes (Vital Signs)

| Code | Description |
|------|-------------|
| `8867-4` | Heart rate |
| `8480-6` | Systolic blood pressure |
| `8462-4` | Diastolic blood pressure |
| `8310-5` | Body temperature |
| `2708-6` | Oxygen saturation (SpO2) |

**Example Usage**:
```json
{
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "8480-6",
      "display": "Systolic blood pressure"
    }],
    "text": "Systolic BP"
  }
}
```

Sources: [fhir-developer-skill/SKILL.md:170-177]()

### Coding System Usage Diagram

```mermaid
graph LR
    ObsCode["Observation.code"]
    CondCode["Condition.code"]
    MedCode["MedicationRequest.<br/>medicationCodeableConcept"]
    EncClass["Encounter.class"]
    
    LOINC["http://loinc.org<br/>Lab tests,<br/>vital signs"]
    SNOMED["http://snomed.info/sct<br/>Diagnoses,<br/>procedures"]
    RxNorm["http://www.nlm.nih.gov/<br/>research/umls/rxnorm<br/>Medications"]
    ActCode["http://terminology.hl7.org/<br/>CodeSystem/v3-ActCode<br/>Encounter types"]
    
    ObsCode -->|"typically uses"| LOINC
    CondCode -->|"typically uses"| SNOMED
    MedCode -->|"typically uses"| RxNorm
    EncClass -->|"uses"| ActCode
```

Sources: [fhir-developer-skill/SKILL.md:157-168]()

## Validation Implementation Patterns

### Python/FastAPI Validation

The skill provides a complete validation pattern using FastAPI and Pydantic v2.

**OperationOutcome Helper** from [fhir-developer-skill/SKILL.md:103-107]():
```python
def operation_outcome(severity: str, code: str, diagnostics: str):
    return {
        "resourceType": "OperationOutcome",
        "issue": [{"severity": severity, "code": code, "diagnostics": diagnostics}]
    }
```

**Required Field Validation** from [fhir-developer-skill/SKILL.md:112-124]():
```python
@app.post("/Observation", status_code=201)
async def create_observation(data: dict):
    if not data.get("status"):
        return JSONResponse(status_code=422, content=operation_outcome(
            "error", "required", "Observation.status is required"
        ), media_type="application/fhir+json")

    if data["status"] not in VALID_OBS_STATUS:
        return JSONResponse(status_code=422, content=operation_outcome(
            "error", "value", f"Invalid status '{data['status']}'"
        ), media_type="application/fhir+json")
    # ... create resource
```

Sources: [fhir-developer-skill/SKILL.md:94-124]()

### Pydantic v2 Models

**Critical**: Use `Literal` for enums, not deprecated `const=True`.

**Example** from [fhir-developer-skill/SKILL.md:144-153]():
```python
from typing import Literal
from pydantic import BaseModel

class Patient(BaseModel):
    resourceType: Literal["Patient"] = "Patient"
    id: str | None = None
    gender: Literal["male", "female", "other", "unknown"] | None = None
```

This pattern:
- Uses `Literal` for resourceType to ensure exact match
- Uses `Literal` for gender enum values
- Uses `| None` for optional fields (Python 3.10+ syntax)

Sources: [fhir-developer-skill/SKILL.md:144-153]()

### TypeScript/Express Validation

**Example** from [fhir-developer-skill/SKILL.md:126-142]():
```typescript
const VALID_OBS_STATUS = new Set(['registered', 'preliminary', 'final', 'amended',
  'corrected', 'cancelled', 'entered-in-error', 'unknown']);

app.post('/Observation', (req, res) => {
  if (!req.body.status) {
    return res.status(422).contentType('application/fhir+json')
      .json(operationOutcome('error', 'required', 'Observation.status is required'));
  }
  if (!VALID_OBS_STATUS.has(req.body.status)) {
    return res.status(422).contentType('application/fhir+json')
      .json(operationOutcome('error', 'value', `Invalid status '${req.body.status}'`));
  }
  // ... create resource
});
```

Sources: [fhir-developer-skill/SKILL.md:126-142]()

## Common Mistakes

### Mistake Matrix

| Mistake | Correct Approach | Status Code |
|---------|------------------|-------------|
| Making `subject` or `period` required on Encounter | Both are 0..1 (optional). Only `status` and `class` required | 422 if validated incorrectly |
| Using CodeableConcept for `Encounter.class` | `class` uses Coding directly: `{"system": "...", "code": "AMB"}` | N/A |
| Returning 400 for ETag mismatch | Use `412 Precondition Failed` for If-Match failures | 412, not 400 |
| Returning 400 for invalid enum values | Use `422 Unprocessable Entity` for validation errors | 422, not 400 |
| Forgetting Content-Type header | Always set `Content-Type: application/fhir+json` | N/A |
| Missing Location header on create | Return `Location: /Patient/{id}` with 201 Created | N/A |
| Using Pydantic v1 `const=True` | Use `Literal["Patient"]` in Pydantic v2 | N/A |

Sources: [fhir-developer-skill/SKILL.md:207-216]()

### Field Requirement Confusion

```mermaid
graph TD
    Dev["Developer reads FHIR spec"]
    SeeSubject["Sees subject field<br/>on Encounter"]
    Assume{"Assumes required<br/>because commonly used?"}
    Wrong["Makes subject required<br/>in validation"]
    Right["Checks cardinality: 0..1<br/>Makes subject optional"]
    Error422["Client gets 422 error<br/>for valid Encounter"]
    Success201["Client gets 201<br/>Encounter created"]
    
    Dev --> SeeSubject
    SeeSubject --> Assume
    Assume -->|"Yes (incorrect)"| Wrong
    Assume -->|"No (correct)"| Right
    Wrong --> Error422
    Right --> Success201
    
    style Error422 stroke-width:2px
    style Wrong stroke-width:2px
```

Sources: [fhir-developer-skill/SKILL.md:52,211]()

## Resource Examples Reference

Complete JSON examples for all resource types are available in [fhir-developer-skill/references/resource-examples.md:1-197](). This includes:

- **Patient** [lines 15-29](): No required fields example
- **Observation** [lines 31-45](): Vital signs with LOINC codes
- **Encounter** [lines 47-61](): Ambulatory visit with Coding class
- **Condition** [lines 63-78](): Diabetes with SNOMED CT
- **MedicationRequest** [lines 80-111](): Two patterns (CodeableConcept and Reference)
- **Medication** [lines 113-128](): RxNorm medication code
- **OperationOutcome** [lines 130-159](): Single and multiple issues
- **CapabilityStatement** [lines 161-197](): Server metadata

Sources: [fhir-developer-skill/SKILL.md:220-232](), [fhir-developer-skill/references/resource-examples.md:1-197]()

---

# Page: FHIR API Patterns

# FHIR API Patterns

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [fhir-developer-skill/SKILL.md](fhir-developer-skill/SKILL.md)
- [fhir-developer-skill/references/bundles.md](fhir-developer-skill/references/bundles.md)
- [fhir-developer-skill/references/pagination.md](fhir-developer-skill/references/pagination.md)
- [fhir-developer-skill/references/resource-examples.md](fhir-developer-skill/references/resource-examples.md)
- [fhir-developer-skill/references/smart-auth.md](fhir-developer-skill/references/smart-auth.md)

</details>



## Purpose and Scope

This page documents the RESTful API patterns used in FHIR R4 implementations, including HTTP endpoint conventions, status code selection, error handling with OperationOutcome, Bundle transaction/batch semantics, pagination, and conditional operations. These patterns apply when building FHIR servers that expose Patient, Observation, Encounter, Condition, and other healthcare resources via HTTP.

For FHIR resource field requirements and value sets, see [FHIR R4 Resource Structures](#3.3.1). For OAuth 2.0 authorization flows and scope enforcement, see [SMART on FHIR Authorization](#3.3.3). For FastAPI project scaffolding, see [FHIR Project Scaffolding Tool](#3.3.4).

---

## RESTful Endpoint Structure

FHIR follows a resource-oriented REST architecture with standardized endpoint patterns. All endpoints are relative to a FHIR base URL (e.g., `https://fhir.example.org/`).

### Standard CRUD Endpoints

```mermaid
graph LR
    subgraph "Client Operations"
        CREATE["POST /Patient"]
        READ["GET /Patient/123"]
        UPDATE["PUT /Patient/123"]
        DELETE["DELETE /Patient/123"]
        SEARCH["GET /Patient?name=Smith"]
        META["GET /metadata"]
    end
    
    subgraph "Server Responses"
        CREATE_RESP["201 Created<br/>Location: /Patient/123"]
        READ_RESP["200 OK<br/>Patient resource"]
        UPDATE_RESP["200 OK<br/>Updated Patient"]
        DELETE_RESP["204 No Content"]
        SEARCH_RESP["200 OK<br/>Bundle (type: searchset)"]
        META_RESP["200 OK<br/>CapabilityStatement"]
    end
    
    CREATE --> CREATE_RESP
    READ --> READ_RESP
    UPDATE --> UPDATE_RESP
    DELETE --> DELETE_RESP
    SEARCH --> SEARCH_RESP
    META --> META_RESP
```

**Diagram: FHIR REST Endpoint Mappings**

Sources: [fhir-developer-skill/SKILL.md:235-245]()

### Endpoint Pattern Reference

| HTTP Method | Endpoint Pattern | Operation | Success Status |
|-------------|-----------------|-----------|----------------|
| `POST` | `/[ResourceType]` | Create new resource | `201 Created` |
| `GET` | `/[ResourceType]/[id]` | Read by ID | `200 OK` |
| `PUT` | `/[ResourceType]/[id]` | Update existing | `200 OK` |
| `DELETE` | `/[ResourceType]/[id]` | Delete resource | `204 No Content` |
| `GET` | `/[ResourceType]?param=value` | Search | `200 OK` (Bundle) |
| `GET` | `/metadata` | Server capabilities | `200 OK` (CapabilityStatement) |
| `POST` | `/` | Bundle transaction/batch | `200 OK` (Bundle response) |

The `POST /` endpoint handles Bundle submissions for atomic transactions or batch operations (see [Bundle Operations](#bundle-operations-transaction-vs-batch) below).

Sources: [fhir-developer-skill/SKILL.md:235-245]()

---

## HTTP Status Code Selection

FHIR servers must return precise HTTP status codes to distinguish between malformed requests, validation errors, authentication failures, and business rule violations.

### Status Code Decision Tree

```mermaid
graph TD
    REQUEST["Incoming Request"]
    
    REQUEST --> AUTH_CHECK{"Valid OAuth<br/>Token?"}
    AUTH_CHECK -->|No token or expired| AUTH_401["401 Unauthorized<br/>WWW-Authenticate header"]
    AUTH_CHECK -->|Valid token| SCOPE_CHECK{"Sufficient<br/>Scopes?"}
    
    SCOPE_CHECK -->|No| AUTH_403["403 Forbidden<br/>OperationOutcome"]
    SCOPE_CHECK -->|Yes| PARSE_CHECK{"Valid JSON<br/>& resourceType?"}
    
    PARSE_CHECK -->|No| BAD_400["400 Bad Request<br/>OperationOutcome"]
    PARSE_CHECK -->|Yes| EXISTS_CHECK{"Resource<br/>Exists?"}
    
    EXISTS_CHECK -->|No (for GET/PUT/DELETE)| NOT_FOUND["404 Not Found<br/>OperationOutcome"]
    EXISTS_CHECK -->|Yes or N/A| ETAG_CHECK{"If-Match<br/>header?"}
    
    ETAG_CHECK -->|Mismatch| PRECOND_412["412 Precondition Failed<br/>OperationOutcome"]
    ETAG_CHECK -->|Match or absent| VALIDATE{"Required fields<br/>& enum values?"}
    
    VALIDATE -->|Invalid| UNPROC_422["422 Unprocessable Entity<br/>OperationOutcome"]
    VALIDATE -->|Valid| SUCCESS["200 OK / 201 Created<br/>/ 204 No Content"]
```

**Diagram: HTTP Status Code Decision Flow**

Sources: [fhir-developer-skill/SKILL.md:18-28]()

### Status Code Reference

| Code | When to Use | Example Scenario |
|------|-------------|------------------|
| `200 OK` | Successful read, update, or search | `GET /Patient/123` returns existing patient |
| `201 Created` | Successful resource creation | `POST /Observation` creates new vital sign |
| `204 No Content` | Successful deletion | `DELETE /Patient/123` removes patient |
| `400 Bad Request` | Malformed JSON, wrong resourceType | `POST /Patient` with `{"resourceType": "Observ"}` |
| `401 Unauthorized` | Missing, expired, revoked, malformed token | Missing `Authorization` header |
| `403 Forbidden` | Valid token but insufficient scopes | Token has `patient/Patient.rs` but client attempts `POST /Patient` |
| `404 Not Found` | Resource doesn't exist | `GET /Patient/999` when ID 999 not found |
| `412 Precondition Failed` | If-Match ETag mismatch | Update with `If-Match: W/"1"` but current version is 2 |
| `422 Unprocessable Entity` | Missing required fields, invalid enum values, business rules | `POST /Observation` without `status` field |

**Critical Distinction**: Use `400` for syntax errors (malformed JSON, wrong resourceType), but `422` for semantic validation failures (missing required fields, invalid enum values). Use `412` (not `400`) for ETag mismatches on conditional updates.

Sources: [fhir-developer-skill/SKILL.md:18-28](), [fhir-developer-skill/SKILL.md:209-216]()

---

## OperationOutcome Error Handling

All error responses (4xx and 5xx status codes) MUST include an `OperationOutcome` resource in the response body. This provides structured, machine-readable error information.

### OperationOutcome Structure

```mermaid
graph TB
    OO["OperationOutcome<br/>(resourceType)"]
    ISSUES["issue: array"]
    ISSUE1["issue[0]"]
    ISSUE2["issue[1]"]
    
    SEV["severity: error|warning|info"]
    CODE["code: required|value|not-found|..."]
    DIAG["diagnostics: human-readable message"]
    EXPR["expression: JSON path to field (optional)"]
    
    OO --> ISSUES
    ISSUES --> ISSUE1
    ISSUES --> ISSUE2
    
    ISSUE1 --> SEV
    ISSUE1 --> CODE
    ISSUE1 --> DIAG
    ISSUE1 --> EXPR
```

**Diagram: OperationOutcome Resource Structure**

Sources: [fhir-developer-skill/references/resource-examples.md:130-159]()

### Implementation Pattern

The skill provides a helper function pattern for generating OperationOutcome responses:

[fhir-developer-skill/SKILL.md:103-107]()

```python
def operation_outcome(severity: str, code: str, diagnostics: str):
    return {
        "resourceType": "OperationOutcome",
        "issue": [{"severity": severity, "code": code, "diagnostics": diagnostics}]
    }
```

### Common Error Codes

| Code | Meaning | HTTP Status |
|------|---------|-------------|
| `required` | Missing required field | 422 |
| `value` | Invalid enum value or data type | 422 |
| `not-found` | Resource ID doesn't exist | 404 |
| `invalid` | Malformed request syntax | 400 |
| `conflict` | Version conflict (concurrent update) | 409 |
| `processing` | Server processing error | 500 |
| `security` | Authorization failure | 401/403 |
| `business-rule` | Domain-specific validation failure | 422 |

### Multiple Validation Errors

OperationOutcome can include multiple issues in a single response. The `expression` field uses FHIRPath or JSON path syntax to identify the problematic field:

[fhir-developer-skill/references/resource-examples.md:151-159]()

```json
{
  "resourceType": "OperationOutcome",
  "issue": [
    {
      "severity": "error",
      "code": "required",
      "diagnostics": "Observation.status is required",
      "expression": ["Observation.status"]
    },
    {
      "severity": "error",
      "code": "required",
      "diagnostics": "Observation.code is required",
      "expression": ["Observation.code"]
    }
  ]
}
```

Sources: [fhir-developer-skill/SKILL.md:103-124](), [fhir-developer-skill/references/resource-examples.md:130-159]()

---

## Bundle Operations: Transaction vs Batch

FHIR supports submitting multiple operations in a single HTTP request via Bundle resources posted to the base URL (`POST /`). The `type` field determines atomicity semantics.

### Transaction vs Batch Semantics

```mermaid
graph TB
    BUNDLE_REQUEST["POST /<br/>Bundle resource"]
    
    TYPE_CHECK{"Bundle.type?"}
    BUNDLE_REQUEST --> TYPE_CHECK
    
    TRANSACTION["type: transaction"]
    BATCH["type: batch"]
    TYPE_CHECK --> TRANSACTION
    TYPE_CHECK --> BATCH
    
    TRANS_PROC["Process all entries<br/>in order (DELETE→POST→PUT→GET)"]
    TRANS_VALIDATE{"All entries<br/>valid?"}
    TRANS_SUCCESS["Commit all changes<br/>Return transaction-response"]
    TRANS_FAIL["Rollback all changes<br/>Return 400 + OperationOutcome"]
    
    TRANSACTION --> TRANS_PROC
    TRANS_PROC --> TRANS_VALIDATE
    TRANS_VALIDATE -->|Yes| TRANS_SUCCESS
    TRANS_VALIDATE -->|No| TRANS_FAIL
    
    BATCH_PROC["Process each entry<br/>independently"]
    BATCH_RESULT["Return batch-response<br/>with per-entry status codes"]
    
    BATCH --> BATCH_PROC
    BATCH_PROC --> BATCH_RESULT
```

**Diagram: Bundle Processing Flow**

Sources: [fhir-developer-skill/references/bundles.md:1-161]()

### Comparison Table

| Feature | Transaction | Batch |
|---------|-------------|-------|
| **Atomicity** | All-or-nothing (atomic) | Independent entries |
| **Failure Handling** | Entire bundle fails, all rolled back | Partial success allowed |
| **Response Type** | `transaction-response` | `batch-response` |
| **HTTP Status** | 200 (success) or 400 (any failure) | 200 (always, even with partial failures) |
| **Use Case** | Related data that must succeed together | Independent operations |
| **Processing Order** | DELETE → POST → PUT/PATCH → GET | Entry order preserved |

### Transaction Example

Transactions ensure that a Patient and related Observation are created together or not at all. References within the bundle use temporary URNs (`urn:uuid:...`) that are resolved during processing.

[fhir-developer-skill/references/bundles.md:23-54]()

**Request:**
```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "fullUrl": "urn:uuid:patient-1",
      "resource": {
        "resourceType": "Patient",
        "name": [{"family": "Smith", "given": ["John"]}]
      },
      "request": {"method": "POST", "url": "Patient"}
    },
    {
      "fullUrl": "urn:uuid:observation-1",
      "resource": {
        "resourceType": "Observation",
        "status": "final",
        "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6"}]},
        "subject": {"reference": "urn:uuid:patient-1"}
      },
      "request": {"method": "POST", "url": "Observation"}
    }
  ]
}
```

If the Observation is invalid (e.g., missing `status`), the server returns `400 Bad Request` with an OperationOutcome, and the Patient is NOT created.

[fhir-developer-skill/references/bundles.md:82-93]()

### Batch Example

Batches allow mixed read/write operations with independent outcomes. Each entry in the response has its own status code.

[fhir-developer-skill/references/bundles.md:99-150]()

**Request:**
```json
{
  "resourceType": "Bundle",
  "type": "batch",
  "entry": [
    {"request": {"method": "GET", "url": "Patient/123"}},
    {"request": {"method": "GET", "url": "Patient/999"}},
    {
      "resource": {
        "resourceType": "Observation",
        "status": "final",
        "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6"}]}
      },
      "request": {"method": "POST", "url": "Observation"}
    }
  ]
}
```

**Response (200 OK with mixed results):**
```json
{
  "resourceType": "Bundle",
  "type": "batch-response",
  "entry": [
    {
      "resource": {"resourceType": "Patient", "id": "123"},
      "response": {"status": "200 OK"}
    },
    {
      "response": {
        "status": "404 Not Found",
        "outcome": {
          "resourceType": "OperationOutcome",
          "issue": [{"severity": "error", "code": "not-found"}]
        }
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/789/_history/1"
      }
    }
  ]
}
```

### Transaction Processing Order

Transactions process entries in a specific order regardless of their position in the entry array. This ensures references resolve correctly:

1. **DELETE** operations
2. **POST** (create) operations
3. **PUT/PATCH** (update) operations
4. **GET** (read) operations

This ordering allows a transaction to delete an old resource, create a new one with the same identifier, and then read it back in a single atomic operation.

Sources: [fhir-developer-skill/references/bundles.md:1-161]()

---

## Pagination Patterns

All search endpoints MUST support pagination to prevent performance issues with large result sets. Search results are returned as Bundle resources with `type: "searchset"` and navigation links.

### Pagination Flow

```mermaid
sequenceDiagram
    participant Client
    participant Server
    participant Database
    
    Client->>Server: GET /Patient?name=Smith&_count=10
    Server->>Database: Query with LIMIT 11 OFFSET 0
    Database-->>Server: 11 results (10 + 1 to detect has_more)
    Server->>Server: Trim to 10 results<br/>Detect has_more=true
    Server-->>Client: Bundle with self, next links<br/>10 entries
    
    Client->>Server: GET /Patient?name=Smith&_count=10&_offset=10
    Server->>Database: Query with LIMIT 11 OFFSET 10
    Database-->>Server: 11 results
    Server->>Server: Trim to 10 results<br/>Detect has_more=true
    Server-->>Client: Bundle with self, previous, next links<br/>10 entries
    
    Client->>Server: GET /Patient?name=Smith&_count=10&_offset=20
    Server->>Database: Query with LIMIT 11 OFFSET 20
    Database-->>Server: 3 results (no more pages)
    Server-->>Client: Bundle with self, previous links<br/>3 entries
```

**Diagram: Pagination Request/Response Cycle**

Sources: [fhir-developer-skill/references/pagination.md:1-106]()

### Pagination Parameters

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `_count` | Results per page | Server-defined (10-100) | `_count=25` |
| `_offset` | Starting index (0-based) | 0 | `_offset=50` |
| `_page` | Page number (1-based, alternative to offset) | 1 | `_page=3` |

### Link Relations

Every paginated Bundle includes a `link` array with navigation URIs:

| Relation | Present When | Description |
|----------|--------------|-------------|
| `self` | Always | Current page URL with all parameters |
| `first` | Optional | First page of results |
| `previous` | Offset > 0 | Previous page |
| `next` | More results exist | Next page |
| `last` | Optional | Last page (requires total count) |

### Implementation Pattern

The skill demonstrates pagination using the "query limit + 1" technique to detect whether more results exist without a separate count query:

[fhir-developer-skill/references/pagination.md:59-95]()

```python
@app.get("/Patient")
async def search_patients(
    name: str = None,
    _count: int = 10,
    _offset: int = 0
):
    # Query with limit + 1 to detect if there are more results
    results = db.query_patients(name=name, limit=_count + 1, offset=_offset)
    has_more = len(results) > _count
    results = results[:_count]  # Trim to requested count

    base_url = f"{BASE_URL}/Patient"
    params = f"name={name}&_count={_count}" if name else f"_count={_count}"

    links = [
        {"relation": "self", "url": f"{base_url}?{params}&_offset={_offset}"}
    ]

    if _offset > 0:
        prev_offset = max(0, _offset - _count)
        links.append({"relation": "previous", "url": f"{base_url}?{params}&_offset={prev_offset}"})

    if has_more:
        links.append({"relation": "next", "url": f"{base_url}?{params}&_offset={_offset + _count}"})

    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": db.count_patients(name=name),
        "link": links,
        "entry": [
            {"fullUrl": f"{base_url}/{p['id']}", "resource": p, "search": {"mode": "match"}}
            for p in results
        ]
    }
```

### Bundle Structure

[fhir-developer-skill/references/pagination.md:14-37]()

```json
{
  "resourceType": "Bundle",
  "type": "searchset",
  "total": 150,
  "link": [
    {"relation": "self", "url": "https://fhir.example.org/Patient?name=Smith&_count=10"},
    {"relation": "next", "url": "https://fhir.example.org/Patient?name=Smith&_count=10&_offset=10"}
  ],
  "entry": [
    {
      "fullUrl": "https://fhir.example.org/Patient/123",
      "resource": {"resourceType": "Patient", "id": "123"},
      "search": {"mode": "match"}
    }
  ]
}
```

### Additional Search Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `_sort` | Sort by field (prefix `-` for descending) | `_sort=-date,name` |
| `_elements` | Return only specified fields | `_elements=name,birthDate` |
| `_summary` | Return summary view | `_summary=true` |
| `_include` | Include referenced resources | `_include=Observation:patient` |
| `_revinclude` | Include resources that reference this | `_revinclude=Observation:patient` |

Sources: [fhir-developer-skill/references/pagination.md:1-106]()

---

## Conditional Operations

FHIR supports conditional operations using HTTP headers to implement optimistic locking and conditional creation patterns.

### If-Match: Optimistic Locking

The `If-Match` header enables optimistic concurrency control. Clients include the resource's ETag to ensure they're updating the version they expect.

```mermaid
graph TB
    CLIENT_READ["Client: GET /Patient/123"]
    SERVER_RESP["Server: 200 OK<br/>ETag: W/\"1\"<br/>versionId: 1"]
    
    CLIENT_UPDATE["Client: PUT /Patient/123<br/>If-Match: W/\"1\""]
    VERSION_CHECK{"Current version<br/>still 1?"}
    
    SUCCESS["Server: 200 OK<br/>ETag: W/\"2\"<br/>Updated resource"]
    CONFLICT["Server: 412 Precondition Failed<br/>OperationOutcome"]
    
    CLIENT_READ --> SERVER_RESP
    SERVER_RESP --> CLIENT_UPDATE
    CLIENT_UPDATE --> VERSION_CHECK
    VERSION_CHECK -->|Yes| SUCCESS
    VERSION_CHECK -->|No (someone else updated)| CONFLICT
```

**Diagram: If-Match Conditional Update Flow**

Sources: [fhir-developer-skill/SKILL.md:249-258]()

**Pattern:**
- Client sends: `If-Match: W/"1"`
- ETag matches current version → update succeeds (200 OK)
- ETag mismatch → return `412 Precondition Failed` (NOT 400)

The `W/` prefix indicates a "weak" ETag, which is standard for FHIR resources.

### If-None-Exist: Conditional Create

The `If-None-Exist` header allows clients to create a resource only if a matching resource doesn't already exist, based on business identifiers.

**Pattern:**
- Client sends: `If-None-Exist: identifier=http://hospital.org/mrn|12345`
- Match exists → return existing resource (200 OK) without creating
- No match → create new resource (201 Created)

Example:
```http
POST /Patient
If-None-Exist: identifier=http://hospital.org/mrn|12345
Content-Type: application/fhir+json

{
  "resourceType": "Patient",
  "identifier": [{"system": "http://hospital.org/mrn", "value": "12345"}],
  "name": [{"family": "Smith"}]
}
```

This prevents duplicate Patient records when the same MRN is submitted multiple times.

Sources: [fhir-developer-skill/SKILL.md:249-258]()

---

## HTTP Headers and Content Negotiation

FHIR servers must implement specific HTTP header conventions for proper interoperability.

### Required Response Headers

| Header | When | Value | Purpose |
|--------|------|-------|---------|
| `Content-Type` | All responses | `application/fhir+json` | Indicates FHIR JSON format |
| `Location` | 201 Created | `/Patient/{id}` | URI of newly created resource |
| `ETag` | All resource reads/updates | `W/"{versionId}"` | Supports optimistic locking |
| `Last-Modified` | Optional | HTTP date | Resource last update time |
| `WWW-Authenticate` | 401 Unauthorized | `Bearer realm="..."` | OAuth token requirements (RFC 6750) |

### Content-Type Header

All FHIR responses MUST set `Content-Type: application/fhir+json`. Some servers also accept `application/json`, but the FHIR-specific media type is preferred for strict conformance.

[fhir-developer-skill/SKILL.md:275]()

Example in FastAPI:
```python
return JSONResponse(
    status_code=422,
    content=operation_outcome("error", "required", "Observation.status is required"),
    media_type="application/fhir+json"
)
```

### Location Header

Create operations (201 Created) MUST include a `Location` header with the full URI of the created resource, including the server-assigned ID.

[fhir-developer-skill/SKILL.md:277]()

Example:
```http
HTTP/1.1 201 Created
Location: https://fhir.example.org/Patient/abc123
Content-Type: application/fhir+json
```

### ETag Header and Versioning

All read and update operations should return an `ETag` header and include `meta.versionId` and `meta.lastUpdated` in the resource:

[fhir-developer-skill/SKILL.md:276-278]()

```http
HTTP/1.1 200 OK
ETag: W/"3"
Content-Type: application/fhir+json

{
  "resourceType": "Patient",
  "id": "123",
  "meta": {
    "versionId": "3",
    "lastUpdated": "2024-01-15T14:30:00Z"
  },
  ...
}
```

The `versionId` increments with each update, enabling version history and optimistic locking via If-Match.

### Implementation Checklist

The skill provides a checklist for ensuring correct HTTP patterns:

[fhir-developer-skill/SKILL.md:273-283]()

1. Set `Content-Type: application/fhir+json` on all responses
2. Return `meta.versionId` and `meta.lastUpdated` on resources
3. Return `Location` header on create: `/Patient/{id}`
4. Return `ETag` header: `W/"{versionId}"`
5. Use OperationOutcome for all error responses
6. Validate required fields → 422 for missing
7. Validate enum values → 422 for invalid
8. Search returns Bundle with `type: "searchset"`

Sources: [fhir-developer-skill/SKILL.md:18-28](), [fhir-developer-skill/SKILL.md:249-258](), [fhir-developer-skill/SKILL.md:273-283]()

---

# Page: SMART on FHIR Authorization

# SMART on FHIR Authorization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [fhir-developer-skill/SKILL.md](fhir-developer-skill/SKILL.md)
- [fhir-developer-skill/references/bundles.md](fhir-developer-skill/references/bundles.md)
- [fhir-developer-skill/references/pagination.md](fhir-developer-skill/references/pagination.md)
- [fhir-developer-skill/references/resource-examples.md](fhir-developer-skill/references/resource-examples.md)
- [fhir-developer-skill/references/smart-auth.md](fhir-developer-skill/references/smart-auth.md)

</details>



## Purpose and Scope

This document covers OAuth 2.0-based authorization for FHIR APIs using the SMART on FHIR framework. It explains how to implement authorization flows, enforce scope-based access control, and handle authentication tokens. For information about FHIR resource structures and validation, see [FHIR R4 Resource Structures](#3.3.1). For RESTful endpoint patterns and error handling, see [FHIR API Patterns](#3.3.2).

SMART on FHIR is the standard authorization framework for healthcare APIs, enabling patient-facing apps, provider-facing clinical tools, and automated backend services to securely access FHIR data with granular permissions.

**Sources:** [fhir-developer-skill/references/smart-auth.md:1-4]()

---

## Architecture Overview

```mermaid
graph TB
    subgraph "Client Applications"
        EHR["EHR Launch App"]
        SA["Standalone App"]
        BACKEND["Backend Service"]
    end
    
    subgraph "Discovery"
        WELL_KNOWN["/.well-known/smart-configuration"]
        METADATA["/metadata<br/>(CapabilityStatement)"]
    end
    
    subgraph "Authorization Server"
        AUTH_EP["/authorize endpoint"]
        TOKEN_EP["/token endpoint"]
    end
    
    subgraph "FHIR Server"
        PATIENT_EP["/Patient"]
        OBS_EP["/Observation"]
        ENC_EP["/Encounter"]
    end
    
    subgraph "Scope Enforcement"
        PARSE["parse_smart_scopes()"]
        CHECK["check_scope()"]
    end
    
    EHR -->|"1. Discover endpoints"| WELL_KNOWN
    SA -->|"1. Discover endpoints"| WELL_KNOWN
    BACKEND -->|"1. Discover endpoints"| WELL_KNOWN
    
    WELL_KNOWN -->|"authorization_endpoint<br/>token_endpoint"| AUTH_EP
    WELL_KNOWN -->|"authorization_endpoint<br/>token_endpoint"| TOKEN_EP
    
    METADATA -->|"security.extension<br/>oauth-uris"| AUTH_EP
    METADATA -->|"security.extension<br/>oauth-uris"| TOKEN_EP
    
    EHR -->|"2. Authorize with<br/>launch + scope"| AUTH_EP
    SA -->|"2. Authorize with<br/>launch/patient + scope"| AUTH_EP
    BACKEND -->|"2. JWT assertion +<br/>client_credentials"| TOKEN_EP
    
    AUTH_EP -->|"3. auth code"| EHR
    AUTH_EP -->|"3. auth code"| SA
    
    EHR -->|"4. Exchange code"| TOKEN_EP
    SA -->|"4. Exchange code"| TOKEN_EP
    
    TOKEN_EP -->|"5. access_token +<br/>patient context"| EHR
    TOKEN_EP -->|"5. access_token +<br/>patient context"| SA
    TOKEN_EP -->|"5. access_token"| BACKEND
    
    EHR -->|"6. Bearer token"| PATIENT_EP
    SA -->|"6. Bearer token"| OBS_EP
    BACKEND -->|"6. Bearer token"| ENC_EP
    
    PATIENT_EP --> PARSE
    OBS_EP --> PARSE
    ENC_EP --> PARSE
    
    PARSE --> CHECK
    CHECK -->|"401 invalid_token<br/>403 insufficient_scope"| EHR
    CHECK -->|"401 invalid_token<br/>403 insufficient_scope"| SA
    CHECK -->|"401 invalid_token<br/>403 insufficient_scope"| BACKEND
```

**Diagram: SMART on FHIR Authorization Architecture**

The system uses two discovery mechanisms: `/.well-known/smart-configuration` ([smart-auth.md:13-31]()) provides OAuth endpoint URLs, while `/metadata` returns a `CapabilityStatement` with embedded authorization URIs ([resource-examples.md:175-184]()). Client apps obtain access tokens through different flows depending on their launch context, and the FHIR server enforces scopes using `parse_smart_scopes()` and `check_scope()` functions ([smart-auth.md:167-195]()).

**Sources:** [fhir-developer-skill/references/smart-auth.md:13-31](), [fhir-developer-skill/references/resource-examples.md:175-184](), [fhir-developer-skill/SKILL.md:24-25]()

---

## Discovery and Configuration

### Well-Known Configuration Endpoint

Servers MUST publish authorization configuration at `/.well-known/smart-configuration`:

| Field | Description |
|-------|-------------|
| `authorization_endpoint` | URL for OAuth authorize requests |
| `token_endpoint` | URL for token exchange |
| `token_endpoint_auth_methods_supported` | Supported client authentication methods |
| `scopes_supported` | List of supported scopes |
| `capabilities` | Feature flags (e.g., `launch-ehr`, `permission-v2`) |

**Example response structure:**

```json
{
  "authorization_endpoint": "https://auth.example.org/authorize",
  "token_endpoint": "https://auth.example.org/token",
  "token_endpoint_auth_methods_supported": ["client_secret_basic", "private_key_jwt"],
  "scopes_supported": ["openid", "fhirUser", "launch", "launch/patient",
                       "patient/*.rs", "user/*.cruds", "offline_access"],
  "capabilities": ["launch-ehr", "launch-standalone", "client-public",
                   "client-confidential-symmetric", "permission-v2", "sso-openid-connect"]
}
```

**Sources:** [fhir-developer-skill/references/smart-auth.md:13-31]()

### CapabilityStatement Integration

The `/metadata` endpoint returns a `CapabilityStatement` with OAuth URIs embedded in the `security.extension` field using the `http://fhir-registry.smarthealthit.org/StructureDefinition/oauth-uris` extension. This provides an alternative discovery mechanism integrated with FHIR's standard metadata endpoint.

**Sources:** [fhir-developer-skill/references/resource-examples.md:162-196]()

---

## Scope Syntax

### SMART v2 (Current Standard)

The v2 scope syntax uses granular permissions with explicit CRUD actions:

```
<context>/<resource>.<permissions>

context: patient | user | system
resource: Patient | Observation | * (wildcard)
permissions: c (create) | r (read) | u (update) | d (delete) | s (search)
```

| Scope | Meaning |
|-------|---------|
| `patient/Patient.rs` | Read and search Patient for current patient context |
| `patient/Observation.rs` | Read and search Observations for current patient |
| `patient/*.rs` | Read and search all resources for current patient |
| `user/Encounter.cruds` | Full CRUD + search on Encounters the user can access |
| `system/*.rs` | Backend service: read/search all resources |

**Sources:** [fhir-developer-skill/references/smart-auth.md:35-52]()

### SMART v1 (Legacy)

The v1 syntax uses coarser permissions:

```
<context>/<resource>.<read|write|*>
```

| v1 Scope | Equivalent v2 |
|----------|---------------|
| `patient/Patient.read` | `patient/Patient.rs` |
| `patient/Patient.write` | `patient/Patient.cud` |
| `patient/Patient.*` | `patient/Patient.cruds` |

FHIR servers should support both v1 and v2 scopes during the transition period. The `parse_smart_scopes()` function handles conversion from v1 to v2 format ([smart-auth.md:167-181]()).

**Sources:** [fhir-developer-skill/references/smart-auth.md:53-62]()

### Context Types

| Scope Type | Use Case | Context Required |
|------------|----------|------------------|
| `patient/` | Patient-facing apps | `patient` launch context |
| `user/` | Provider-facing apps | User's access permissions |
| `system/` | Backend services | Pre-configured policy |

**Sources:** [fhir-developer-skill/references/smart-auth.md:63-70]()

---

## Launch Context Scopes

```mermaid
graph LR
    subgraph "Launch Scopes"
        LAUNCH["launch"]
        LAUNCH_PAT["launch/patient"]
        LAUNCH_ENC["launch/encounter"]
    end
    
    subgraph "Identity Scopes"
        OPENID["openid"]
        FHIR_USER["fhirUser"]
    end
    
    subgraph "Token Lifetime"
        OFFLINE["offline_access"]
        ONLINE["online_access"]
    end
    
    subgraph "Token Response"
        PAT_CLAIM["patient claim"]
        ENC_CLAIM["encounter claim"]
        ID_TOKEN["id_token with fhirUser"]
        REFRESH["refresh_token"]
    end
    
    LAUNCH -->|"Provides"| PAT_CLAIM
    LAUNCH -->|"Provides"| ENC_CLAIM
    LAUNCH_PAT -->|"Provides"| PAT_CLAIM
    LAUNCH_ENC -->|"Provides"| ENC_CLAIM
    OPENID -->|"Provides"| ID_TOKEN
    FHIR_USER -->|"Provides"| ID_TOKEN
    OFFLINE -->|"Provides"| REFRESH
    ONLINE -->|"Provides"| REFRESH
```

**Diagram: Launch Context Scope to Token Claim Mapping**

| Scope | Provides | In Token Response |
|-------|----------|-------------------|
| `launch` | EHR launch context | `patient`, `encounter` fields |
| `launch/patient` | Standalone patient selection | `patient` field |
| `launch/encounter` | Standalone encounter selection | `encounter` field |
| `openid fhirUser` | User identity | `id_token` with `fhirUser` claim |
| `offline_access` | Refresh token (persistent) | `refresh_token` |
| `online_access` | Refresh token (session-bound) | `refresh_token` |

**Sources:** [fhir-developer-skill/references/smart-auth.md:72-81]()

---

## EHR Launch Flow

```mermaid
sequenceDiagram
    participant EHR as "EHR System"
    participant App as "Client App"
    participant Well as "/.well-known/smart-configuration"
    participant Auth as "/authorize"
    participant Token as "/token"
    participant User as "End User"
    
    EHR->>App: "GET /launch?iss=https://fhir.hospital.org<br/>&launch=abc123"
    App->>Well: "GET /.well-known/smart-configuration"
    Well-->>App: "{authorization_endpoint, token_endpoint}"
    
    App->>Auth: "GET /authorize?<br/>response_type=code&<br/>client_id=my-app&<br/>redirect_uri=https://app.example.com/callback&<br/>scope=launch patient/Patient.rs&<br/>state=xyz789&<br/>aud=https://fhir.hospital.org&<br/>launch=abc123"
    
    Auth->>User: "Authenticate & Authorize"
    User-->>Auth: "Approved"
    
    Auth-->>App: "GET /callback?code=auth_code&state=xyz789"
    
    App->>Token: "POST /token<br/>grant_type=authorization_code&<br/>code=auth_code&<br/>redirect_uri=https://app.example.com/callback&<br/>client_id=my-app"
    
    Token-->>App: "{access_token, patient: 123, encounter: 456}"
```

**Diagram: EHR Launch Sequence with OAuth Parameters**

### Step-by-Step Process

1. **EHR launches app** with `iss` (FHIR server base URL) and `launch` token
2. **App discovers endpoints** from `/.well-known/smart-configuration`
3. **App requests authorization** with:
   - `response_type=code` (authorization code flow)
   - `client_id` (registered app identifier)
   - `redirect_uri` (callback URL)
   - `scope` (requested permissions including `launch`)
   - `state` (CSRF protection token)
   - `aud` (FHIR server base URL)
   - `launch` (opaque token from EHR)
4. **User authenticates and authorizes** the requested scopes
5. **Authorization server redirects** with authorization code
6. **App exchanges code for token** using `grant_type=authorization_code`
7. **Token response includes context**: `access_token`, `patient`, `encounter`

**Sources:** [fhir-developer-skill/references/smart-auth.md:82-124]()

---

## Backend Services Authentication

```mermaid
graph TD
    subgraph "Backend Service"
        CLIENT["Client Application"]
        KEYS["Private Key<br/>(RS384, ES384)"]
        JWT_CREATE["jwt.encode()"]
    end
    
    subgraph "JWT Claims"
        ISS["iss: CLIENT_ID"]
        SUB["sub: CLIENT_ID"]
        AUD["aud: TOKEN_ENDPOINT"]
        EXP["exp: now + 300"]
        JTI["jti: uuid"]
    end
    
    subgraph "Token Endpoint"
        TOKEN_EP["/token"]
        VALIDATE["Validate JWT signature"]
    end
    
    subgraph "Grant Parameters"
        GRANT["grant_type:<br/>client_credentials"]
        SCOPE["scope: system/*.rs"]
        ASSERTION_TYPE["client_assertion_type:<br/>jwt-bearer"]
        ASSERTION["client_assertion:<br/>signed JWT"]
    end
    
    CLIENT --> KEYS
    KEYS --> JWT_CREATE
    
    ISS --> JWT_CREATE
    SUB --> JWT_CREATE
    AUD --> JWT_CREATE
    EXP --> JWT_CREATE
    JTI --> JWT_CREATE
    
    JWT_CREATE --> ASSERTION
    
    GRANT --> TOKEN_EP
    SCOPE --> TOKEN_EP
    ASSERTION_TYPE --> TOKEN_EP
    ASSERTION --> TOKEN_EP
    
    TOKEN_EP --> VALIDATE
    VALIDATE -->|"Valid"| ACCESS_TOKEN["access_token"]
    VALIDATE -->|"Invalid"| ERROR["401 invalid_client"]
```

**Diagram: Backend Services JWT Assertion Flow with Code Entities**

Backend services use the `client_credentials` grant type with JWT assertions for system-to-system authentication. The implementation creates a signed JWT with specific claims and exchanges it for an access token without user interaction.

### Implementation Pattern

The backend service implementation follows this pattern from [smart-auth.md:130-158]():

1. **Create JWT assertion** with claims:
   - `iss` and `sub`: both set to `CLIENT_ID`
   - `aud`: set to `TOKEN_ENDPOINT`
   - `exp`: expiration (typically 5 minutes)
   - `jti`: unique identifier (UUID)

2. **Sign JWT** using `RS384` or `ES384` algorithm with private key

3. **POST to token endpoint** with parameters:
   - `grant_type=client_credentials`
   - `scope=system/*.rs` (or other system/ scopes)
   - `client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer`
   - `client_assertion=<signed_jwt>`

4. **Receive access token** in response

**Sources:** [fhir-developer-skill/references/smart-auth.md:126-158]()

---

## Scope Enforcement Implementation

```mermaid
graph TB
    subgraph "Incoming Request"
        REQ["Request with<br/>Authorization: Bearer token"]
        TOKEN_SCOPES["token_scopes string<br/>(e.g., 'patient/Patient.rs user/Observation.cruds')"]
    end
    
    subgraph "parse_smart_scopes Function"
        SPLIT["Split by whitespace"]
        REGEX["Regex match:<br/>(patient|user|system)/(\w+|\*).([cruds]+|read|write|\*)"]
        V1_CONVERT["Convert v1 to v2:<br/>read → rs<br/>write → cud<br/>* → cruds"]
        BUILD_DICT["Build permissions dict:<br/>{resource: set(permissions)}"]
    end
    
    subgraph "check_scope Function"
        ACTION_MAP["action_map:<br/>{'create': 'c', 'read': 'r',<br/>'update': 'u', 'delete': 'd',<br/>'search': 's'}"]
        CHECK_RESOURCE["Check resource in permissions"]
        CHECK_WILDCARD["Check '*' in permissions"]
        VERIFY["Verify required permission"]
    end
    
    subgraph "Response"
        ALLOW["200 OK / 201 Created"]
        ERR_401["401 Unauthorized<br/>invalid_token"]
        ERR_403["403 Forbidden<br/>insufficient_scope"]
    end
    
    REQ --> TOKEN_SCOPES
    TOKEN_SCOPES --> SPLIT
    SPLIT --> REGEX
    REGEX --> V1_CONVERT
    V1_CONVERT --> BUILD_DICT
    
    BUILD_DICT --> CHECK_RESOURCE
    BUILD_DICT --> CHECK_WILDCARD
    CHECK_RESOURCE --> VERIFY
    CHECK_WILDCARD --> VERIFY
    
    ACTION_MAP --> VERIFY
    
    VERIFY -->|"Permission found"| ALLOW
    VERIFY -->|"Token invalid"| ERR_401
    VERIFY -->|"Permission missing"| ERR_403
```

**Diagram: Scope Parsing and Enforcement Flow with Function Names**

### parse_smart_scopes Function

The `parse_smart_scopes()` function ([smart-auth.md:167-181]()) converts a space-delimited scope string into a structured permissions dictionary:

```python
def parse_smart_scopes(token_scopes: str) -> dict:
    """Parse SMART scopes into a permissions structure."""
    permissions = {}
    for scope in token_scopes.split():
        match = re.match(r'(patient|user|system)/(\w+|\*)\.([cruds]+|read|write|\*)', scope)
        if match:
            context, resource, perms = match.groups()
            if perms == 'read': perms = 'rs'
            elif perms == 'write': perms = 'cud'
            elif perms == '*': perms = 'cruds'

            if resource not in permissions:
                permissions[resource] = set()
            permissions[resource].update(perms)
    return permissions
```

**Key operations:**
- Regex captures context (`patient`/`user`/`system`), resource type, and permissions
- Converts v1 syntax (`read`, `write`, `*`) to v2 (`rs`, `cud`, `cruds`)
- Returns dict like `{'Patient': {'r', 's'}, 'Observation': {'c', 'r', 'u', 'd', 's'}}`

**Sources:** [fhir-developer-skill/references/smart-auth.md:167-181]()

### check_scope Function

The `check_scope()` function ([smart-auth.md:183-195]()) verifies that a token has the required permission for an action:

```python
async def check_scope(request: Request, resource_type: str, action: str):
    """Verify the token has required scope for the action."""
    token_scopes = request.state.token_scopes
    permissions = parse_smart_scopes(token_scopes)

    action_map = {'create': 'c', 'read': 'r', 'update': 'u', 'delete': 'd', 'search': 's'}
    required = action_map.get(action, action)

    allowed = permissions.get(resource_type, set()) | permissions.get('*', set())

    if required not in allowed:
        raise HTTPException(status_code=403, detail=f"Insufficient scope. Required: {resource_type}.{required}")
```

**Key operations:**
- Maps action names to single-letter permission codes
- Checks both specific resource type and wildcard (`*`) permissions
- Raises `403 Forbidden` if permission not found

**Sources:** [fhir-developer-skill/references/smart-auth.md:183-195]()

---

## Authorization Error Handling

### HTTP Status Codes

The FHIR server returns specific status codes for authorization failures as defined in [SKILL.md:24-25]():

| Status | Error Code | When |
|--------|------------|------|
| `401 Unauthorized` | `invalid_token` | Token expired, malformed, revoked, or missing (RFC 6750) |
| `403 Forbidden` | `insufficient_scope` | Valid token but missing required scope |
| `403 Forbidden` | `access_denied` | Resource outside patient compartment |

### Error Response Format

All authorization errors MUST return an `OperationOutcome` resource:

```json
{
  "resourceType": "OperationOutcome",
  "issue": [{
    "severity": "error",
    "code": "security",
    "diagnostics": "Insufficient scope. Required: Patient.r"
  }]
}
```

**Sources:** [fhir-developer-skill/references/smart-auth.md:197-204](), [fhir-developer-skill/SKILL.md:24-25]()

### Token Validation Sequence

```mermaid
graph TD
    REQ["Incoming FHIR Request"]
    HEADER["Extract Authorization header"]
    BEARER["Verify Bearer format"]
    DECODE["Decode JWT / validate"]
    EXPIRED["Check expiration"]
    REVOKED["Check revocation"]
    PARSE["parse_smart_scopes()"]
    CHECK["check_scope()"]
    COMPARTMENT["Check patient compartment"]
    
    REQ --> HEADER
    HEADER -->|"Missing"| ERR_401_MISSING["401: Missing token"]
    HEADER -->|"Present"| BEARER
    BEARER -->|"Invalid format"| ERR_401_MALFORMED["401: Malformed token"]
    BEARER -->|"Valid"| DECODE
    DECODE -->|"Invalid signature"| ERR_401_INVALID["401: Invalid token"]
    DECODE -->|"Valid"| EXPIRED
    EXPIRED -->|"Expired"| ERR_401_EXPIRED["401: Token expired"]
    EXPIRED -->|"Valid"| REVOKED
    REVOKED -->|"Revoked"| ERR_401_REVOKED["401: Token revoked"]
    REVOKED -->|"Valid"| PARSE
    PARSE --> CHECK
    CHECK -->|"Insufficient scope"| ERR_403_SCOPE["403: Insufficient scope"]
    CHECK -->|"Valid scope"| COMPARTMENT
    COMPARTMENT -->|"Outside compartment"| ERR_403_ACCESS["403: Access denied"]
    COMPARTMENT -->|"Valid"| SUCCESS["Process request"]
```

**Diagram: Token Validation and Error Flow**

The validation flow ensures that:
1. Authorization header is present and properly formatted
2. Token signature is valid and not expired or revoked
3. Token scopes include the required permission for the action
4. Resource is within the authorized patient compartment (for `patient/` scopes)

**Sources:** [fhir-developer-skill/references/smart-auth.md:197-204](), [fhir-developer-skill/SKILL.md:24-25]()

---

## Token Lifecycle Management

### Access Token Properties

| Property | Typical Value | Notes |
|----------|---------------|-------|
| `access_token` | JWT string | Bearer token for API requests |
| `token_type` | `Bearer` | Always "Bearer" for SMART |
| `expires_in` | `3600` | Seconds until expiration (typically 1 hour) |
| `scope` | Space-delimited string | Actual granted scopes (may differ from requested) |
| `patient` | Patient ID | Present when `launch` or `launch/patient` used |
| `encounter` | Encounter ID | Present when `launch` scope used |

### Refresh Token Flow

For long-lived sessions, clients request `offline_access` or `online_access` scope to receive a `refresh_token`:

```
POST /token
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token&
refresh_token=<refresh_token_value>&
client_id=my-app
```

**Response:**
```json
{
  "access_token": "new_token_here",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "new_refresh_token"
}
```

**Differences:**
- `offline_access`: Refresh token persists beyond session (for long-term access)
- `online_access`: Refresh token expires when user session ends

**Sources:** [fhir-developer-skill/references/smart-auth.md:115-123]()

---

## Integration with FHIR API Patterns

Authorization integrates with FHIR RESTful operations as documented in [FHIR API Patterns](#3.3.2):

### Authorization Header

All FHIR requests MUST include the `Authorization` header:

```
GET /Patient/123
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Scope-to-Operation Mapping

| HTTP Method | FHIR Operation | Required Permission |
|-------------|----------------|---------------------|
| `POST /Patient` | Create | `c` (create) |
| `GET /Patient/123` | Read | `r` (read) |
| `PUT /Patient/123` | Update | `u` (update) |
| `DELETE /Patient/123` | Delete | `d` (delete) |
| `GET /Patient?name=Smith` | Search | `s` (search) |

### Middleware Integration

FastAPI middleware validates authorization before processing requests:

```python
from fastapi import Request, HTTPException

async def auth_middleware(request: Request, call_next):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    token = auth_header[7:]  # Strip "Bearer "
    # Validate token, extract scopes
    request.state.token_scopes = extract_scopes(token)
    
    response = await call_next(request)
    return response
```

This middleware runs before endpoint handlers, ensuring all requests are authenticated.

**Sources:** [fhir-developer-skill/references/smart-auth.md:162-195](), [fhir-developer-skill/SKILL.md:24-25]()

---

# Page: FHIR Project Scaffolding Tool

# FHIR Project Scaffolding Tool

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [fhir-developer-skill/SKILL.md](fhir-developer-skill/SKILL.md)
- [fhir-developer-skill/references/bundles.md](fhir-developer-skill/references/bundles.md)
- [fhir-developer-skill/references/pagination.md](fhir-developer-skill/references/pagination.md)
- [fhir-developer-skill/scripts/setup_fhir_project.py](fhir-developer-skill/scripts/setup_fhir_project.py)

</details>



## Purpose and Scope

This document covers the `setup_fhir_project.py` script, a command-line tool that generates a complete, production-ready FHIR R4 API server using FastAPI and Pydantic v2. The script creates a working project structure with correct FHIR patterns, validation logic, and error handling.

For detailed information about the FHIR resource structures and validation rules implemented by the generated code, see [FHIR R4 Resource Structures](#3.3.1). For FHIR API endpoint patterns and HTTP semantics, see [FHIR API Patterns](#3.3.2).

**Sources:** [fhir-developer-skill/SKILL.md:286-294](), [fhir-developer-skill/scripts/setup_fhir_project.py:1-10]()

---

## Quick Start

The scaffolding tool is located at `scripts/setup_fhir_project.py` and requires Python 3.10+. It accepts a single argument specifying the project directory name.

**Basic Usage:**
```bash
python scripts/setup_fhir_project.py my_fhir_api
cd my_fhir_api
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

After running these commands, the API server is accessible at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

**Sources:** [fhir-developer-skill/scripts/setup_fhir_project.py:228-232](), [fhir-developer-skill/SKILL.md:290-294]()

---

## Generated Project Structure

The script creates a complete FastAPI project with the following directory layout:

```mermaid
graph TB
    root["project_root/"]
    
    req["requirements.txt"]
    
    app["app/"]
    app_init["__init__.py"]
    main["main.py"]
    helpers["helpers.py"]
    
    models["models/"]
    models_init["__init__.py"]
    fhir_types["fhir_types.py"]
    
    routes["routes/"]
    routes_init["__init__.py"]
    patient["patient.py"]
    
    tests["tests/"]
    test_patient["test_patient.py"]
    
    root --> req
    root --> app
    root --> tests
    
    app --> app_init
    app --> main
    app --> helpers
    app --> models
    app --> routes
    
    models --> models_init
    models --> fhir_types
    
    routes --> routes_init
    routes --> patient
    
    tests --> test_patient
    
    style root fill:#f9f9f9
    style app fill:#e8f4f8
    style models fill:#e8f4f8
    style routes fill:#e8f4f8
    style tests fill:#fff4e6
```

**Directory Structure:**

| Path | Purpose | Key Contents |
|------|---------|--------------|
| `requirements.txt` | Python dependencies | fastapi, uvicorn, pydantic, httpx, pytest |
| `app/main.py` | FastAPI application entry point | `FastAPI` app instance, `/metadata` endpoint |
| `app/helpers.py` | FHIR response utilities | `operation_outcome()`, `fhir_response()` |
| `app/models/fhir_types.py` | Pydantic v2 FHIR models | `Patient`, `Observation`, `Bundle`, `OperationOutcome` |
| `app/routes/patient.py` | Patient resource endpoints | CRUD operations, search functionality |
| `tests/test_patient.py` | Pytest test suite | Create, read, search test cases |

**Sources:** [fhir-developer-skill/scripts/setup_fhir_project.py:12-15]()

---

## Core Components

### Requirements and Dependencies

The generated `requirements.txt` specifies version-pinned dependencies:

```
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
httpx>=0.24.0
pytest>=7.0.0
```

These versions ensure Pydantic v2 compatibility, which is critical for the `Literal` type syntax used throughout the models.

**Sources:** [fhir-developer-skill/scripts/setup_fhir_project.py:17-20]()

---

### FHIR Data Models

```mermaid
graph LR
    subgraph "Base Types"
        Meta["Meta"]
        HumanName["HumanName"]
        Coding["Coding"]
        CodeableConcept["CodeableConcept"]
        Reference["Reference"]
        Quantity["Quantity"]
    end
    
    subgraph "Resource Types"
        Patient["Patient"]
        Observation["Observation"]
        Bundle["Bundle"]
        OperationOutcome["OperationOutcome"]
    end
    
    subgraph "Nested Types"
        BundleEntry["BundleEntry"]
        OperationOutcomeIssue["OperationOutcomeIssue"]
    end
    
    Patient --> Meta
    Patient --> HumanName
    
    Observation --> Meta
    Observation --> CodeableConcept
    Observation --> Reference
    Observation --> Quantity
    
    CodeableConcept --> Coding
    
    Bundle --> BundleEntry
    BundleEntry -.->|contains| Patient
    BundleEntry -.->|contains| Observation
    
    OperationOutcome --> OperationOutcomeIssue
```

The `app/models/fhir_types.py` module defines Pydantic v2 models with correct FHIR R4 patterns:

**Key Model Features:**

| Model | Required Fields | Literal Types | Special Behaviors |
|-------|----------------|---------------|-------------------|
| `Patient` | *(none)* | `resourceType="Patient"`, `gender` enum | Auto-generated UUID ID |
| `Observation` | `status`, `code` | `resourceType="Observation"`, `status` enum | Required status validation |
| `Bundle` | `type` | `resourceType="Bundle"`, `type` enum | Contains list of `BundleEntry` |
| `OperationOutcome` | `issue` | `resourceType="OperationOutcome"` | Error response structure |

**Pydantic v2 Pattern:**
The models use `Literal` types for enumerations and `Field(default_factory=...)` for auto-generated values, following Pydantic v2 syntax:

```python
# Example from generated code
class Patient(BaseModel):
    resourceType: Literal["Patient"] = "Patient"
    id: str | None = Field(default_factory=lambda: str(uuid.uuid4()))
    gender: Literal["male", "female", "other", "unknown"] | None = None
```

**Sources:** [fhir-developer-skill/scripts/setup_fhir_project.py:27-97](), [fhir-developer-skill/SKILL.md:144-153]()

---

### Helper Functions

The `app/helpers.py` module provides two utility functions for FHIR-compliant responses:

**`operation_outcome(status_code, severity, code, diagnostics)`**

Returns a FHIR OperationOutcome error response with the correct `application/fhir+json` content type. Used for all error scenarios (404, 422, etc.).

**`fhir_response(content, status_code, headers)`**

Returns a successful FHIR JSON response with the correct content type and optional headers (e.g., `Location`, `ETag`).

Both functions ensure responses always set `Content-Type: application/fhir+json`, a critical FHIR requirement.

**Sources:** [fhir-developer-skill/scripts/setup_fhir_project.py:99-122]()

---

### FastAPI Application

```mermaid
graph TB
    client["HTTP Client"]
    
    subgraph "FastAPI Application"
        app["FastAPI()<br/>app/main.py"]
        metadata["/metadata<br/>GET"]
        patient_router["patient.router<br/>app/routes/patient.py"]
        
        app --> metadata
        app --> patient_router
        
        subgraph "Patient Routes"
            create["POST /Patient"]
            read["GET /Patient/{id}"]
            update["PUT /Patient/{id}"]
            delete["DELETE /Patient/{id}"]
            search["GET /Patient"]
            
            patient_router --> create
            patient_router --> read
            patient_router --> update
            patient_router --> delete
            patient_router --> search
        end
    end
    
    subgraph "Storage"
        patients["patients: dict[str, Patient]"]
    end
    
    client -->|requests| app
    create -->|stores| patients
    read -->|retrieves| patients
    update -->|updates| patients
    delete -->|removes| patients
    search -->|queries| patients
```

The generated `app/main.py` creates a FastAPI application with:

1. **Capability Statement Endpoint** (`/metadata`): Returns a FHIR CapabilityStatement describing server capabilities, FHIR version (4.0.1), and supported resources.

2. **Router Integration**: Includes the Patient router using `app.include_router(patient.router)`, enabling modular route organization.

The application follows a standard FastAPI pattern where each FHIR resource type can be implemented in a separate router module.

**Sources:** [fhir-developer-skill/scripts/setup_fhir_project.py:124-144]()

---

### Patient CRUD Endpoints

The `app/routes/patient.py` module implements complete CRUD operations for the Patient resource:

**HTTP Request Flow:**

```mermaid
sequenceDiagram
    participant C as Client
    participant R as patient.router
    participant S as patients storage
    participant H as helpers module
    
    Note over C,H: CREATE Patient
    C->>R: POST /Patient<br/>{resourceType, name, gender}
    R->>R: Validate with Pydantic
    R->>R: Generate Meta with versionId
    R->>S: Store patient[id] = Patient
    R->>H: fhir_response(201)
    H->>C: 201 Created<br/>Location: /Patient/{id}<br/>ETag: W/"1"
    
    Note over C,H: READ Patient
    C->>R: GET /Patient/123
    R->>S: Retrieve patients[123]
    alt Patient exists
        R->>H: fhir_response(200)
        H->>C: 200 OK<br/>Patient resource
    else Not found
        R->>H: operation_outcome(404)
        H->>C: 404 Not Found<br/>OperationOutcome
    end
    
    Note over C,H: SEARCH Patients
    C->>R: GET /Patient?name=Smith&gender=male
    R->>S: Filter patients by criteria
    R->>R: Build Bundle with entries
    R->>H: fhir_response(Bundle)
    H->>C: 200 OK<br/>Bundle with searchset
```

**Endpoint Implementation Details:**

| Endpoint | Method | Response | Headers | Storage Operation |
|----------|--------|----------|---------|-------------------|
| `/Patient` | POST | 201 Created | `Location`, `ETag` | `patients[id] = patient` |
| `/Patient/{id}` | GET | 200 OK / 404 | *(none)* | `patients[id]` lookup |
| `/Patient/{id}` | PUT | 200 OK / 404 | *(none)* | `patients[id] = updated`, increment `versionId` |
| `/Patient/{id}` | DELETE | 204 No Content / 404 | *(none)* | `del patients[id]` |
| `/Patient?name=&gender=` | GET | 200 OK Bundle | *(none)* | Filter `patients.values()` |

The search endpoint supports two query parameters: `name` (substring match on `HumanName.family`) and `gender` (exact match). Results are returned as a Bundle with `type="searchset"`.

**Sources:** [fhir-developer-skill/scripts/setup_fhir_project.py:146-195]()

---

### Test Suite

The generated `tests/test_patient.py` provides basic test coverage using FastAPI's `TestClient`:

**Test Cases:**

1. **`test_create_patient()`**: Verifies POST returns 201 status and includes `Location` header
2. **`test_read_not_found()`**: Verifies GET for nonexistent resource returns 404 with OperationOutcome
3. **`test_search()`**: Verifies search returns 200 with Bundle resourceType

These tests demonstrate the correct testing pattern for FHIR APIs and can be extended for additional resources and validation scenarios.

**Sources:** [fhir-developer-skill/scripts/setup_fhir_project.py:197-218]()

---

## Usage Workflow

```mermaid
graph LR
    start["Developer"]
    run["Run setup_fhir_project.py"]
    created["Project created"]
    venv["Create virtual environment"]
    install["pip install -r requirements.txt"]
    run_server["uvicorn app.main:app --reload"]
    test["pytest tests/"]
    extend["Add Observation, Encounter routes"]
    
    start --> run
    run --> created
    created --> venv
    venv --> install
    install --> run_server
    install --> test
    run_server --> extend
    test --> extend
```

**Step-by-Step Workflow:**

1. **Generate Project:**
   ```bash
   python scripts/setup_fhir_project.py my_fhir_api
   ```

2. **Setup Environment:**
   ```bash
   cd my_fhir_api
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Development Server:**
   ```bash
   uvicorn app.main:app --reload
   ```
   The server starts at `http://localhost:8000` with auto-reload on file changes.

5. **Access API Documentation:**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`
   - Capability Statement: `http://localhost:8000/metadata`

6. **Run Tests:**
   ```bash
   pytest tests/
   ```

**Sources:** [fhir-developer-skill/scripts/setup_fhir_project.py:220-226]()

---

## Key Design Patterns

### Pydantic v2 Compliance

The scaffolding tool generates models using Pydantic v2 syntax exclusively:

- **`Literal` for Enums:** `gender: Literal["male", "female", "other", "unknown"]` instead of deprecated `const=True`
- **Union Types:** `str | None` instead of `Optional[str]`
- **Field Factories:** `Field(default_factory=lambda: str(uuid.uuid4()))` for auto-generated values
- **`model_dump()`:** Replaces `dict()` for serialization

This ensures compatibility with FastAPI 0.100+ and Pydantic 2.0+.

**Sources:** [fhir-developer-skill/scripts/setup_fhir_project.py:28-96](), [fhir-developer-skill/SKILL.md:144-153]()

---

### FHIR-Compliant Error Handling

All error responses use OperationOutcome resources with appropriate HTTP status codes:

| Error Scenario | Status Code | OperationOutcome Code | Example |
|----------------|-------------|----------------------|---------|
| Resource not found | 404 | `not-found` | `Patient/999 not found` |
| Missing required field | 422 | `required` | `Observation.status is required` |
| Invalid enum value | 422 | `value` | `Invalid status 'invalid'` |

The `operation_outcome()` helper ensures consistent error response structure across all endpoints.

**Sources:** [fhir-developer-skill/scripts/setup_fhir_project.py:104-112](), [fhir-developer-skill/SKILL.md:103-124]()

---

### HTTP Header Management

The generated code correctly implements FHIR HTTP header requirements:

1. **Content-Type:** All responses include `Content-Type: application/fhir+json`
2. **Location Header:** POST responses include `Location: /Patient/{id}`
3. **ETag Header:** Create responses include `ETag: W/"{versionId}"` for versioning support

These headers enable proper HTTP caching, conditional requests, and client-side resource location tracking.

**Sources:** [fhir-developer-skill/scripts/setup_fhir_project.py:159-161]()

---

## Extensibility

The scaffolded project provides a foundation for adding additional FHIR resources:

**Adding a New Resource Type:**

1. **Add Model:** Define the resource in `app/models/fhir_types.py` (e.g., `Encounter`, `Condition`)
2. **Create Router:** Add `app/routes/encounter.py` following the Patient router pattern
3. **Register Router:** Include in `app/main.py` with `app.include_router(encounter.router)`
4. **Update Capability Statement:** Add resource to `/metadata` response
5. **Add Tests:** Create `tests/test_encounter.py`

The modular architecture allows independent development of each resource type without cross-dependencies.

**Sources:** [fhir-developer-skill/scripts/setup_fhir_project.py:127-143]()

---

## Relationship to FHIR Developer Skill

The scaffolding tool is one of two primary outputs of the FHIR Developer Skill (see [FHIR Developer Guide](#3.3)):

- **SKILL.md Knowledge Base:** Provides reference documentation for FHIR R4 structures, validation rules, and coding systems
- **`setup_fhir_project.py` Script:** Generates working code implementing those patterns

Together, these components enable developers to quickly bootstrap FHIR-compliant APIs with correct validation logic, error handling, and RESTful semantics.

**Sources:** [fhir-developer-skill/SKILL.md:1-11](), [fhir-developer-skill/SKILL.md:286-294]()

---

# Page: MCP Servers and External Data

# MCP Servers and External Data

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [README.md](README.md)
- [cms-coverage/.claude-plugin/plugin.json](cms-coverage/.claude-plugin/plugin.json)
- [icd10-codes/.claude-plugin/plugin.json](icd10-codes/.claude-plugin/plugin.json)
- [npi-registry/.claude-plugin/plugin.json](npi-registry/.claude-plugin/plugin.json)
- [pubmed/.claude-plugin/plugin.json](pubmed/.claude-plugin/plugin.json)

</details>



This document provides an overview of the four Model Context Protocol (MCP) servers available in the healthcare marketplace. These servers provide Claude with access to specialized healthcare data sources including Medicare coverage policies, provider registries, biomedical literature, and diagnostic codes. Each MCP server is hosted on external infrastructure and accessed via HTTP, enabling skills to leverage authoritative healthcare data without embedding it in the repository.

For information about how Skills use these MCP servers, see [Healthcare Skills](#3). For details on the marketplace architecture and plugin configuration, see [Marketplace Architecture](#2).

## Overview

The healthcare marketplace provides four MCP servers that enable access to external healthcare data sources:

| MCP Server | Purpose | Data Source | Hosting |
|------------|---------|-------------|---------|
| **CMS Coverage** | Medicare coverage policies | National and Local Coverage Determinations | DeepSense.ai |
| **NPI Registry** | Healthcare provider validation | US National Provider Identifier database | DeepSense.ai |
| **PubMed** | Biomedical literature search | PubMed citations and PMC full-text | Claude Infrastructure |
| **ICD-10 Codes** | Diagnosis and procedure codes | ICD-10-CM and ICD-10-PCS code sets | DeepSense.ai |

These MCP servers are consumed by skills to perform domain-specific healthcare workflows. The Prior Authorization Review skill uses three MCPs (CMS Coverage, NPI Registry, ICD-10 Codes) for validation and policy lookups, while the Clinical Trial Protocol Generator optionally uses PubMed for literature research.

**Sources:** [README.md:44-58](), [.claude-plugin/marketplace.json:45-73]()

## MCP Server Architecture

MCP servers follow a distinct configuration pattern from skills. Each MCP server is defined in two locations:

1. **Marketplace Registry Entry**: In [.claude-plugin/marketplace.json]() with `source` pointing to a subdirectory
2. **MCP Plugin Configuration**: In `<mcp-name>/.claude-plugin/plugin.json` specifying the HTTP endpoint

```mermaid
graph TB
    MP["marketplace.json"]
    
    subgraph "MCP Definitions in Marketplace"
        CMS_MP["cms-coverage entry<br/>source: ./cms-coverage"]
        NPI_MP["npi-registry entry<br/>source: ./npi-registry"]
        PM_MP["pubmed entry<br/>source: ./pubmed"]
        ICD_MP["icd10-codes entry<br/>source: ./icd10-codes"]
    end
    
    subgraph "Plugin Configurations"
        CMS_PLUGIN["cms-coverage/.claude-plugin/plugin.json<br/>mcpServers.CMS Coverage<br/>type: http"]
        NPI_PLUGIN["npi-registry/.claude-plugin/plugin.json<br/>mcpServers.NPI Registry<br/>type: http"]
        PM_PLUGIN["pubmed/.claude-plugin/plugin.json<br/>mcpServers.PubMed<br/>type: http"]
        ICD_PLUGIN["icd10-codes/.claude-plugin/plugin.json<br/>mcpServers.ICD10 Codes<br/>type: http"]
    end
    
    subgraph "External Infrastructure"
        DS["DeepSense.ai Servers<br/>mcp.deepsense.ai"]
        CL["Claude Infrastructure<br/>pubmed.mcp.claude.com"]
    end
    
    MP --> CMS_MP
    MP --> NPI_MP
    MP --> PM_MP
    MP --> ICD_MP
    
    CMS_MP --> CMS_PLUGIN
    NPI_MP --> NPI_PLUGIN
    PM_MP --> PM_PLUGIN
    ICD_MP --> ICD_PLUGIN
    
    CMS_PLUGIN -->|"url: https://mcp.deepsense.ai/cms_coverage/mcp"| DS
    NPI_PLUGIN -->|"url: https://mcp.deepsense.ai/npi_registry/mcp"| DS
    ICD_PLUGIN -->|"url: https://mcp.deepsense.ai/icd10_codes/mcp"| DS
    PM_PLUGIN -->|"url: https://pubmed.mcp.claude.com/mcp"| CL
```

**Diagram: MCP Server Configuration and Hosting Architecture**

This architecture decouples marketplace discovery metadata from runtime configuration. The marketplace registry provides human-readable descriptions and tags, while the `plugin.json` files specify the technical details for HTTP communication.

**Sources:** [.claude-plugin/marketplace.json:45-73](), [cms-coverage/.claude-plugin/plugin.json:1-15](), [npi-registry/.claude-plugin/plugin.json:1-15](), [pubmed/.claude-plugin/plugin.json:1-15](), [icd10-codes/.claude-plugin/plugin.json:1-15]()

## MCP Server Catalog

The following table summarizes the configuration details for each MCP server:

| MCP Server | Directory | plugin.json mcpServers Key | HTTP Endpoint |
|------------|-----------|---------------------------|---------------|
| CMS Coverage | `cms-coverage/` | `"CMS Coverage"` | `https://mcp.deepsense.ai/cms_coverage/mcp` |
| NPI Registry | `npi-registry/` | `"NPI Registry"` | `https://mcp.deepsense.ai/npi_registry/mcp` |
| PubMed | `pubmed/` | `"PubMed"` | `https://pubmed.mcp.claude.com/mcp` |
| ICD-10 Codes | `icd10-codes/` | `"ICD10 Codes"` | `https://mcp.deepsense.ai/icd10_codes/mcp` |

Each `plugin.json` follows this structure:

```json
{
  "name": "mcp-name",
  "version": "1.0.0",
  "description": "Description of data source",
  "author": {
    "name": "Organization",
    "url": "https://example.com"
  },
  "mcpServers": {
    "Display Name": {
      "type": "http",
      "url": "https://hostname/path/mcp"
    }
  }
}
```

**Sources:** [cms-coverage/.claude-plugin/plugin.json:1-15](), [npi-registry/.claude-plugin/plugin.json:1-15](), [pubmed/.claude-plugin/plugin.json:1-15](), [icd10-codes/.claude-plugin/plugin.json:1-15]()

## Skill Dependencies on MCP Servers

Skills declare MCP server usage through documentation and workflow design, but not through explicit dependency configuration. The following diagram shows which skills integrate with which MCP servers:

```mermaid
graph LR
    subgraph "Skills"
        CTP["clinical-trial-protocol-skill"]
        PAR["prior-auth-review-skill"]
        FHIR["fhir-developer-skill"]
    end
    
    subgraph "MCP Servers"
        CMS["cms-coverage<br/>Medicare Coverage Policies"]
        NPI["npi-registry<br/>Provider Validation"]
        PM["pubmed<br/>Literature Search"]
        ICD["icd10-codes<br/>Diagnosis/Procedure Codes"]
    end
    
    PAR -->|"validates provider NPI"| NPI
    PAR -->|"validates diagnosis codes"| ICD
    PAR -->|"checks Medicare coverage"| CMS
    
    CTP -.->|"optional: research background"| PM
    
    FHIR -.->|"no MCP dependencies"| FHIR
```

**Diagram: Skill-to-MCP Server Dependencies**

The Prior Authorization Review skill has mandatory dependencies on three MCP servers (NPI Registry, ICD-10 Codes, CMS Coverage) for its validation workflow. The Clinical Trial Protocol Generator optionally uses PubMed for literature research in Step 1. The FHIR Developer skill is self-contained and does not require external data sources.

**Sources:** [.claude-plugin/marketplace.json:11-73](), [README.md:27-42]()

## Installation and Usage

### Adding MCP Servers from the Marketplace

MCP servers are installed using the `claude mcp add-from-marketplace` command with the marketplace owner and MCP name:

```bash
# Add individual MCP servers
claude mcp add-from-marketplace anthropics/healthcare/cms-coverage
claude mcp add-from-marketplace anthropics/healthcare/npi-registry
claude mcp add-from-marketplace anthropics/healthcare/pubmed
claude mcp add-from-marketplace anthropics/healthcare/icd10-codes
```

The marketplace must be added first using `/plugin marketplace add anthropics/healthcare` before MCP servers can be installed.

**Sources:** [README.md:52-58]()

### MCP Server Naming Convention

MCP servers in the marketplace use a hyphenated naming convention:
- Marketplace name in [marketplace.json:45-73](): `"cms-coverage"`, `"npi-registry"`, `"pubmed"`, `"icd10-codes"`
- Directory name: `cms-coverage/`, `npi-registry/`, `pubmed/`, `icd10-codes/`
- Command syntax: `anthropics/healthcare/cms-coverage`

This differs from skill naming which uses `@` for marketplace scoping (e.g., `prior-auth-review@healthcare`).

**Sources:** [README.md:44-58](), [.claude-plugin/marketplace.json:45-73]()

## MCP Server Providers

### DeepSense.ai Infrastructure

Three MCP servers are hosted on DeepSense.ai infrastructure at `mcp.deepsense.ai`:

- **CMS Coverage**: `https://mcp.deepsense.ai/cms_coverage/mcp`
- **NPI Registry**: `https://mcp.deepsense.ai/npi_registry/mcp`
- **ICD-10 Codes**: `https://mcp.deepsense.ai/icd10_codes/mcp`

These servers provide access to publicly available US healthcare datasets including Medicare policies, provider registries, and medical coding systems.

**Sources:** [cms-coverage/.claude-plugin/plugin.json:12](), [npi-registry/.claude-plugin/plugin.json:12](), [icd10-codes/.claude-plugin/plugin.json:12]()

### Claude Infrastructure

The PubMed MCP server is hosted on Claude infrastructure:

- **PubMed**: `https://pubmed.mcp.claude.com/mcp`

This server provides access to PubMed's biomedical citations and PubMed Central's full-text archive.

**Sources:** [pubmed/.claude-plugin/plugin.json:12]()

## Detailed MCP Server Documentation

For comprehensive documentation on each MCP server's capabilities, data models, and usage patterns, see the following pages:

- [CMS Coverage Database](#4.1) - Medicare LCDs/NCDs and coverage policy lookup
- [NPI Registry](#4.2) - Healthcare provider validation and lookup
- [PubMed Literature Search](#4.3) - Biomedical citation search and full-text access
- [ICD-10 Codes](#4.4) - Diagnosis and procedure code validation

Each page provides detailed information on the data available, query patterns, and integration examples with skills.

**Sources:** [.claude-plugin/marketplace.json:45-73]()

---

# Page: CMS Coverage Database

# CMS Coverage Database

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/release.yml](.github/workflows/release.yml)
- [README.md](README.md)
- [clinical-trial-protocol-skill/README.md](clinical-trial-protocol-skill/README.md)
- [cms-coverage/.claude-plugin/plugin.json](cms-coverage/.claude-plugin/plugin.json)
- [npi-registry/.claude-plugin/plugin.json](npi-registry/.claude-plugin/plugin.json)
- [prior-auth-review-skill/README.md](prior-auth-review-skill/README.md)
- [pubmed/.claude-plugin/plugin.json](pubmed/.claude-plugin/plugin.json)

</details>



This page documents the CMS Coverage MCP server, which provides programmatic access to Medicare Part B coverage policies including National Coverage Determinations (NCDs) and Local Coverage Determinations (LCDs). This MCP server enables skills to query coverage criteria, eligibility requirements, and medical necessity guidelines from the Centers for Medicare & Medicaid Services (CMS) database.

For information about how the Prior Authorization Review skill uses this MCP server, see [Prior Authorization Review](#3.2). For information about other MCP servers in the marketplace, see [MCP Servers and External Data](#4).

**Sources:** [cms-coverage/.claude-plugin/plugin.json:1-15](), [README.md:44-58]()

## Overview

The CMS Coverage MCP server is a remote HTTP-based Model Context Protocol server that connects Claude Code to the CMS Coverage Database. It is hosted and maintained by DeepSense.ai at `https://mcp.deepsense.ai/cms_coverage/mcp` and provides read-only access to Medicare coverage policies.

The server enables skills to programmatically:
- Search for coverage policies by procedure code (CPT/HCPCS)
- Retrieve National Coverage Determinations (NCDs)
- Retrieve Local Coverage Determinations (LCDs)
- Query coverage criteria and medical necessity requirements
- Access billing and coding guidelines

This MCP server is critical for healthcare workflows that require coverage verification, particularly prior authorization review processes where determining whether Medicare will cover a service is essential.

**Sources:** [cms-coverage/.claude-plugin/plugin.json:1-15](), [README.md:46-48]()

## Medicare Coverage Policies

### National Coverage Determinations (NCDs)

NCDs are nationwide Medicare coverage policies created by CMS that apply uniformly across all Medicare contractors and states. They establish whether Medicare will cover specific medical services, procedures, or technologies based on medical evidence and regulatory standards.

**Characteristics:**
- **Scope**: National (applies to all Medicare beneficiaries)
- **Authority**: CMS headquarters
- **Precedence**: Override conflicting LCDs
- **Use Cases**: Novel technologies, controversial procedures, high-cost items

### Local Coverage Determinations (LCDs)

LCDs are regional coverage policies created by Medicare Administrative Contractors (MACs) that apply within specific geographic jurisdictions. They provide more granular coverage criteria for services not addressed by NCDs.

**Characteristics:**
- **Scope**: Regional (specific MAC jurisdiction)
- **Authority**: Medicare Administrative Contractors
- **Precedence**: Cannot conflict with NCDs
- **Use Cases**: Common procedures, local medical practice variations

**Sources:** [cms-coverage/.claude-plugin/plugin.json:3-4](), [prior-auth-review-skill/README.md:25-26]()

## MCP Server Architecture

### Configuration Structure

The CMS Coverage MCP server follows the standard MCP plugin configuration pattern used across all remote MCP servers in the healthcare marketplace.

**MCP Server Configuration**
```mermaid
graph TD
    subgraph "Repository"
        DIR["cms-coverage/"]
        PLUGIN["cms-coverage/.claude-plugin/plugin.json"]
    end
    
    subgraph "Plugin Configuration"
        NAME["name: cms-coverage"]
        VERSION["version: 1.0.0"]
        DESC["description: Medicare coverage policies<br/>(NCDs/LCDs)"]
        AUTHOR["author: deepsense.ai"]
    end
    
    subgraph "MCP Server Definition"
        SERVER["mcpServers['CMS Coverage']"]
        TYPE["type: http"]
        URL["url: https://mcp.deepsense.ai/cms_coverage/mcp"]
    end
    
    subgraph "External Infrastructure"
        DEEPSENSE["DeepSense.ai MCP Infrastructure"]
        CMS_DB["CMS Coverage Database"]
    end
    
    DIR --> PLUGIN
    PLUGIN --> NAME
    PLUGIN --> VERSION
    PLUGIN --> DESC
    PLUGIN --> AUTHOR
    PLUGIN --> SERVER
    SERVER --> TYPE
    SERVER --> URL
    
    URL --> DEEPSENSE
    DEEPSENSE --> CMS_DB
```

**Sources:** [cms-coverage/.claude-plugin/plugin.json:1-15]()

### Plugin Metadata

| Field | Value | Purpose |
|-------|-------|---------|
| `name` | `"cms-coverage"` | Unique identifier for marketplace registration |
| `version` | `"1.0.0"` | Semantic version number |
| `description` | Medicare Part B coverage policies | Human-readable description |
| `author.name` | `"deepsense.ai"` | Hosting organization |
| `author.url` | `"https://deepsense.ai"` | Organization website |
| `mcpServers["CMS Coverage"].type` | `"http"` | MCP transport protocol |
| `mcpServers["CMS Coverage"].url` | `"https://mcp.deepsense.ai/cms_coverage/mcp"` | MCP endpoint |

**Sources:** [cms-coverage/.claude-plugin/plugin.json:1-15]()

## Integration with Prior Authorization Review

The Prior Authorization Review skill uses the CMS Coverage MCP server as a primary data source during the Intake & Assessment phase (Subskill 1). The integration enables automated lookup of coverage policies based on the requested procedure codes.

### Coverage Policy Search Workflow

```mermaid
sequenceDiagram
    participant PA as "Prior Auth Review<br/>Subskill 1"
    participant CMS as "CMS Coverage MCP<br/>mcp.deepsense.ai"
    participant DB as "CMS Coverage Database"
    
    Note over PA: Extract CPT/HCPCS code<br/>from PA request
    
    PA->>CMS: search_coverage_policy(code)
    CMS->>DB: Query NCD/LCD by code
    DB-->>CMS: Return matching policies
    CMS-->>PA: Coverage policies with criteria
    
    Note over PA: Parse coverage criteria<br/>(indications, contraindications)
    
    Note over PA: Map clinical evidence<br/>to policy requirements
    
    Note over PA: Generate medical necessity<br/>assessment
```

**Sources:** [prior-auth-review-skill/README.md:28-42]()

### Data Flow in Prior Auth Assessment

The following diagram shows how the CMS Coverage MCP integrates with other data sources during prior authorization assessment:

```mermaid
graph TB
    subgraph "Input"
        PA_REQ["Prior Auth Request<br/>(provider, member, service)"]
    end
    
    subgraph "Validation Phase"
        NPI_MCP["NPI Registry MCP<br/>Validate provider credentials"]
        ICD_MCP["ICD-10 MCP<br/>Validate diagnosis codes"]
        CPT_WEB["WebFetch<br/>Validate CPT codes"]
    end
    
    subgraph "Coverage Policy Phase"
        CMS_MCP["CMS Coverage MCP<br/>Search coverage policies"]
        LCD["Local Coverage Determinations"]
        NCD["National Coverage Determinations"]
    end
    
    subgraph "Assessment Phase"
        EXTRACT["Extract Clinical Data<br/>from documentation"]
        MAP["Map Evidence to<br/>Policy Criteria"]
        ASSESS["Medical Necessity<br/>Assessment"]
    end
    
    subgraph "Output"
        REC["Recommendation<br/>(APPROVE/PEND)"]
        WAYPOINT["waypoints/assessment.json"]
    end
    
    PA_REQ --> NPI_MCP
    PA_REQ --> ICD_MCP
    PA_REQ --> CPT_WEB
    
    PA_REQ --> CMS_MCP
    CMS_MCP --> LCD
    CMS_MCP --> NCD
    
    LCD --> MAP
    NCD --> MAP
    
    PA_REQ --> EXTRACT
    EXTRACT --> MAP
    
    MAP --> ASSESS
    ASSESS --> REC
    REC --> WAYPOINT
```

**Sources:** [prior-auth-review-skill/README.md:32-42]()

### Code References

The Prior Authorization Review skill's interaction with the CMS Coverage MCP occurs during Subskill 1 (Intake & Assessment). While the exact MCP tool invocation code is generated at runtime by Claude, the skill's documentation specifies the integration point:

- **Skill Definition**: [prior-auth-review-skill/SKILL.md]() (referenced but not provided in files)
- **Documentation**: [prior-auth-review-skill/README.md:38]() - "Searches coverage policies via CMS Coverage MCP Connector"
- **Output**: Results stored in `waypoints/assessment.json` alongside other validation data

**Sources:** [prior-auth-review-skill/README.md:28-46]()

## Installation and Usage

### Adding to Claude Code

The CMS Coverage MCP server is installed using the marketplace command:

```bash
claude mcp add-from-marketplace anthropics/healthcare/cms-coverage
```

This command:
1. Retrieves the plugin configuration from [cms-coverage/.claude-plugin/plugin.json:1-15]()
2. Registers the HTTP MCP server with Claude Code
3. Makes CMS Coverage tools available to all skills

**Sources:** [README.md:52-58]()

### Marketplace Registration

The CMS Coverage MCP is registered in the central marketplace registry at [.claude-plugin/marketplace.json]() (not provided in files) with the following entry structure:

```json
{
  "name": "cms-coverage",
  "source": "./cms-coverage",
  "description": "Access the CMS Coverage Database"
}
```

The `source` field points to the `cms-coverage/` directory, which contains the `plugin.json` configuration that specifies the actual MCP server endpoint.

**Sources:** [README.md:44-58](), [cms-coverage/.claude-plugin/plugin.json:1-15]()

## Limitations and Considerations

### Coverage Policy Scope

The CMS Coverage MCP server provides access to **Medicare Part B coverage policies only**. Important limitations include:

| Limitation | Implication |
|------------|-------------|
| Medicare-specific | Policies do not apply to commercial insurers or Medicare Advantage plans |
| Part B focus | Part A (hospital) and Part D (prescription drug) coverage not included |
| Point-in-time data | Coverage policies change; real-time updates depend on data refresh frequency |
| Regional variation | LCDs vary by MAC jurisdiction; correct jurisdiction must be identified |

**Sources:** [prior-auth-review-skill/README.md:25-26]()

### Prior Authorization Disclaimer

The Prior Authorization Review skill includes an explicit disclaimer about the limitations of using CMS coverage policies:

> **COVERAGE POLICY LIMITATIONS:** Coverage policies are sourced from Medicare LCDs/NCDs via CMS Coverage MCP Connector. If this review is for a commercial or Medicare Advantage plan, payer-specific policies may differ and were not applied.

This means organizations using the Prior Auth Review skill for non-Medicare cases must:
1. Recognize that CMS policies may not match their plan's policies
2. Supplement or override CMS policies with payer-specific coverage criteria
3. Validate recommendations against their own coverage determinations

**Sources:** [prior-auth-review-skill/README.md:25-26]()

### External Dependency

The CMS Coverage MCP server is **externally hosted infrastructure** maintained by DeepSense.ai. This creates operational dependencies:

- **Availability**: Skills relying on CMS Coverage will fail if the MCP endpoint is unavailable
- **Data freshness**: Coverage policy updates depend on DeepSense.ai's data refresh schedule
- **API stability**: Changes to the MCP server interface could break skill integrations
- **Authentication**: The endpoint is currently publicly accessible; future versions may require authentication

**Sources:** [cms-coverage/.claude-plugin/plugin.json:6-8](), [cms-coverage/.claude-plugin/plugin.json:10-12]()

## Related MCP Servers

The CMS Coverage MCP server is one of four MCP servers in the healthcare marketplace. Other related servers include:

- **[NPI Registry](#4.2)**: Validates healthcare provider credentials
- **[ICD-10 Codes](#4.4)**: Validates diagnosis and procedure codes
- **[PubMed](#4.3)**: Searches biomedical literature

The Prior Authorization Review skill uses all four MCP servers together to perform comprehensive validation and assessment.

**Sources:** [README.md:44-58]()

---

# Page: NPI Registry

# NPI Registry

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/release.yml](.github/workflows/release.yml)
- [README.md](README.md)
- [clinical-trial-protocol-skill/README.md](clinical-trial-protocol-skill/README.md)
- [cms-coverage/.claude-plugin/plugin.json](cms-coverage/.claude-plugin/plugin.json)
- [npi-registry/.claude-plugin/plugin.json](npi-registry/.claude-plugin/plugin.json)
- [prior-auth-review-skill/README.md](prior-auth-review-skill/README.md)
- [pubmed/.claude-plugin/plugin.json](pubmed/.claude-plugin/plugin.json)

</details>



## Purpose and Scope

This document describes the NPI Registry MCP Server, which provides Claude Code skills with access to the US National Provider Identifier (NPI) Registry. The NPI Registry contains information about all HIPAA-covered healthcare providers in the United States, including individual practitioners, healthcare organizations, and their credentials, specialties, and practice locations.

For information about how skills integrate with MCP servers in general, see [MCP Servers and External Data](#4). For the Prior Authorization Review skill that uses this registry to validate providers, see [Prior Authorization Review](#3.2). For other healthcare data sources, see [CMS Coverage Database](#4.1), [PubMed Literature Search](#4.3), and [ICD-10 Codes](#4.4).

**Sources:** [README.md:1-63](), [npi-registry/.claude-plugin/plugin.json:1-16]()

---

## Overview

The NPI Registry MCP Server is an HTTP-based Model Context Protocol server that provides programmatic access to the National Plan and Provider Enumeration System (NPPES) dataset maintained by the Centers for Medicare & Medicaid Services (CMS). Every healthcare provider who conducts electronic health transactions covered by HIPAA must have a National Provider Identifier, making this registry the authoritative source for provider verification in the United States.

### Key Capabilities

| Capability | Description | Use Case |
|------------|-------------|----------|
| Provider Lookup | Search providers by NPI, name, or taxonomy | Validate provider credentials in prior authorization requests |
| Organization Search | Find healthcare organizations and facilities | Verify institutional provider information |
| Credential Verification | Retrieve provider specialties, licenses, and identifiers | Confirm provider qualifications for specific procedures |
| Practice Location | Access provider addresses and contact information | Support provider network validation and communication |

The NPI Registry server is hosted externally by DeepSense.ai and accessed via HTTPS, following the distributed MCP architecture pattern where data sources are maintained separately from the skills repository.

**Sources:** [README.md:46-58](), [npi-registry/.claude-plugin/plugin.json:1-16]()

---

## Technical Architecture

### Plugin Configuration Structure

The NPI Registry MCP Server follows the standard MCP plugin architecture, with configuration stored in a dedicated directory structure:

```
npi-registry/
└── .claude-plugin/
    └── plugin.json
```

The `plugin.json` file defines the MCP server endpoint and metadata:

**Diagram: NPI Registry Plugin Configuration**

```mermaid
graph TB
    PluginJSON["npi-registry/.claude-plugin/plugin.json"]
    
    subgraph "Plugin Metadata"
        Name["name: 'npi-registry'"]
        Version["version: '1.0.0'"]
        Description["description: 'US National Provider<br/>Identifier Registry access'"]
        Author["author: deepsense.ai"]
    end
    
    subgraph "MCP Server Definition"
        ServerName["mcpServers['NPI Registry']"]
        Type["type: 'http'"]
        URL["url: 'https://mcp.deepsense.ai/<br/>npi_registry/mcp'"]
    end
    
    PluginJSON --> Name
    PluginJSON --> Version
    PluginJSON --> Description
    PluginJSON --> Author
    PluginJSON --> ServerName
    ServerName --> Type
    ServerName --> URL
```

**Sources:** [npi-registry/.claude-plugin/plugin.json:1-16]()

### Service Architecture

**Diagram: NPI Registry Service Flow**

```mermaid
graph LR
    subgraph "Claude Code Environment"
        Skill["Prior Auth Review Skill<br/>(prior-auth-review-skill/)"]
        Claude["Claude AI Runtime"]
    end
    
    subgraph "MCP Layer"
        MCPClient["MCP Client<br/>(HTTP Transport)"]
        PluginConfig["plugin.json<br/>mcpServers['NPI Registry']"]
    end
    
    subgraph "External Infrastructure"
        DSServer["DeepSense.ai MCP Server<br/>mcp.deepsense.ai/npi_registry/mcp"]
        NPPESData["NPPES Registry<br/>(CMS Dataset)"]
    end
    
    Skill -->|"requests provider lookup"| Claude
    Claude -->|"invokes MCP tools"| MCPClient
    MCPClient -->|"reads endpoint"| PluginConfig
    MCPClient -->|"HTTPS POST<br/>JSON-RPC 2.0"| DSServer
    DSServer -->|"queries"| NPPESData
    NPPESData -->|"provider records"| DSServer
    DSServer -->|"JSON response"| MCPClient
    MCPClient -->|"structured data"| Claude
    Claude -->|"validation results"| Skill
```

The NPI Registry server implements the Model Context Protocol over HTTP, using JSON-RPC 2.0 for request/response communication. The external server at `mcp.deepsense.ai` maintains the connection to CMS's NPPES data, handling queries and returning structured provider information.

**Sources:** [npi-registry/.claude-plugin/plugin.json:9-14](), [README.md:46-58]()

---

## Integration with Prior Authorization Review Skill

The Prior Authorization Review skill is the primary consumer of the NPI Registry MCP server. It uses provider lookup to validate that healthcare providers submitting prior authorization requests have valid credentials and appropriate specialties.

### Provider Validation Workflow

**Diagram: NPI Validation in Prior Auth Workflow**

```mermaid
sequenceDiagram
    participant User
    participant Subskill1["Subskill 1: Intake & Assessment<br/>(prior-auth-review-skill/SKILL.md)"]
    participant NPIRegistry["NPI Registry MCP<br/>(mcp.deepsense.ai/npi_registry)"]
    participant Assessment["waypoints/assessment.json"]
    
    User->>Subskill1: "Provide PA request with<br/>Rendering Provider NPI"
    Subskill1->>NPIRegistry: "Lookup provider by NPI"
    
    alt Provider Found
        NPIRegistry-->>Subskill1: "Provider record:<br/>name, specialty, address"
        Subskill1->>Subskill1: "Validate specialty matches<br/>requested procedure"
        Subskill1->>Assessment: "Write validated_provider"
    else Provider Not Found
        NPIRegistry-->>Subskill1: "NPI not found error"
        Subskill1->>Assessment: "Write validation_error"
        Subskill1->>User: "PEND - Invalid provider NPI"
    end
```

The validation occurs early in the Prior Auth Review workflow, during the Intake & Assessment phase. The skill collects the rendering provider's NPI from the authorization request and queries the NPI Registry to:

1. Confirm the NPI is valid and active
2. Retrieve the provider's name and credentials
3. Verify the provider's specialty taxonomy matches the requested procedure type
4. Document the provider's practice location for audit purposes

**Sources:** [prior-auth-review-skill/README.md:27-44]()

### Code Integration Points

The Prior Authorization Review skill references NPI validation in its workflow documentation. When the skill executes Subskill 1 (Intake & Assessment), it:

- Collects provider NPI from the authorization request
- Invokes the NPI Registry MCP server through Claude's MCP client
- Validates the returned provider record against the request
- Stores validation results in `waypoints/assessment.json`

The skill documentation explicitly lists "Validates provider credentials via NPI MCP Connector" as a core capability of Subskill 1 [prior-auth-review-skill/README.md:34]().

### Sample Data Handling

The Prior Auth Review skill includes sample case files in `assets/sample/` for demonstration purposes. When operating in demo mode with sample data, the skill skips NPI MCP lookups for the sample provider only, while executing all other MCP calls (ICD-10, CMS Coverage) normally [prior-auth-review-skill/README.md:73-77](). This allows users to test the workflow without requiring live NPI Registry access.

**Sources:** [prior-auth-review-skill/README.md:27-78]()

---

## Installation and Configuration

### Adding the NPI Registry to Claude Code

The NPI Registry MCP server is added to Claude Code through the marketplace system. Users install it from the Healthcare marketplace using the MCP add command:

```bash
claude mcp add-from-marketplace anthropics/healthcare/npi-registry
```

This command:
1. Resolves the marketplace path to the plugin configuration
2. Reads [npi-registry/.claude-plugin/plugin.json:1-16]()
3. Registers the HTTP MCP server endpoint with Claude Code
4. Makes NPI Registry tools available to all skills

**Sources:** [README.md:52-58]()

### Marketplace Registration

The NPI Registry is registered in the Healthcare marketplace's central registry at `.claude-plugin/marketplace.json` (not included in the provided files but referenced in system architecture). The marketplace entry defines:

| Property | Value |
|----------|-------|
| Name | `npi-registry` |
| Type | MCP Server |
| Source Path | `./npi-registry` |
| Description | Access US National Provider Identifier Registry |

Skills that depend on the NPI Registry should document it as a requirement, as the Prior Authorization Review skill does in its README [prior-auth-review-skill/README.md:34]().

**Sources:** [README.md:44-58](), [npi-registry/.claude-plugin/plugin.json:1-16]()

---

## Provider Data Structure

### NPI Registry Fields

While the exact API schema is maintained by the external DeepSense.ai server, the NPI Registry provides access to NPPES fields including:

**Individual Providers:**
- NPI number (10-digit unique identifier)
- Provider name (first, middle, last, credentials)
- Taxonomy codes (specialty classifications)
- License numbers and issuing states
- Practice locations (primary and secondary addresses)
- Contact information (phone, fax)

**Organizational Providers:**
- NPI number
- Organization name (legal business name)
- Organization taxonomy codes
- Authorized official information
- Practice locations
- Subpart organization indicators

### Taxonomy Codes

Healthcare Provider Taxonomy codes are used to classify provider types and specialties. Common taxonomies relevant to prior authorization include:

| Taxonomy Code | Classification | Example Use Case |
|---------------|----------------|------------------|
| 207Q00000X | Family Medicine | Primary care services |
| 207RC0000X | Cardiovascular Disease | Cardiac procedures |
| 208D00000X | General Practice | General medical services |
| 261QR0200X | Radiology Clinic | Imaging procedures |

The NPI Registry returns taxonomy codes that the Prior Authorization Review skill uses to validate that the rendering provider's specialty is appropriate for the requested procedure.

**Sources:** [prior-auth-review-skill/README.md:34](), [npi-registry/.claude-plugin/plugin.json:4]()

---

## Usage Patterns and Best Practices

### Provider Validation Pattern

When validating providers using the NPI Registry, skills should follow this pattern:

1. **Extract NPI** from authorization request or clinical documentation
2. **Query NPI Registry** using the provider's NPI number
3. **Verify Response** confirms provider is active and valid
4. **Check Taxonomy** ensures provider specialty matches requested service
5. **Document Results** in waypoint or output files for audit trail

### Error Handling

Skills integrating with the NPI Registry should handle common error conditions:

| Error Condition | Handling Strategy | Example Response |
|-----------------|-------------------|------------------|
| NPI not found | Recommend PEND status | Request valid provider NPI from submitter |
| Multiple matches | Use additional filters | Match by provider name and location |
| Inactive provider | Flag validation error | Provider NPI is inactive in registry |
| Service unavailable | Retry with backoff | Temporary connectivity issue with NPI Registry |

The Prior Authorization Review skill implements error handling by documenting validation errors in `waypoints/assessment.json` and recommending PEND status when provider validation fails [prior-auth-review-skill/README.md:41-44]().

### Performance Considerations

The NPI Registry is accessed via HTTPS, which introduces network latency. Skills should:

- Cache provider lookups within a session when the same NPI appears multiple times
- Batch validate multiple providers if the MCP server supports batch operations
- Display progress indicators for user-facing workflows
- Implement timeouts for external service calls

**Sources:** [prior-auth-review-skill/README.md:27-44](), [npi-registry/.claude-plugin/plugin.json:11-14]()

---

## Relationship to Other MCP Servers

**Diagram: MCP Servers in Prior Authorization Workflow**

```mermaid
graph TD
    PARequest["Prior Authorization Request"]
    
    Subskill1["Subskill 1: Intake & Assessment<br/>(prior-auth-review-skill/SKILL.md)"]
    
    NPIRegistry["NPI Registry MCP<br/>npi-registry/.claude-plugin/plugin.json"]
    ICD10["ICD-10 MCP<br/>icd10-codes/.claude-plugin/plugin.json"]
    CMSCoverage["CMS Coverage MCP<br/>cms-coverage/.claude-plugin/plugin.json"]
    WebFetch["WebFetch Tool<br/>(CMS Fee Schedule)"]
    
    Assessment["waypoints/assessment.json"]
    
    PARequest --> Subskill1
    
    Subskill1 -->|"Validate provider credentials"| NPIRegistry
    Subskill1 -->|"Validate diagnosis codes"| ICD10
    Subskill1 -->|"Search coverage policies"| CMSCoverage
    Subskill1 -->|"Validate CPT/HCPCS codes"| WebFetch
    
    NPIRegistry --> Assessment
    ICD10 --> Assessment
    CMSCoverage --> Assessment
    WebFetch --> Assessment
```

The NPI Registry works alongside other MCP servers in the Healthcare marketplace to support comprehensive prior authorization workflows:

- **NPI Registry** validates healthcare providers
- **ICD-10 Codes** ([#4.4](#4.4)) validates diagnosis codes
- **CMS Coverage** ([#4.1](#4.1)) retrieves Medicare coverage policies
- **PubMed** ([#4.3](#4.3)) provides clinical literature for protocol generation

Each MCP server is independently maintained and accessed through the same MCP protocol, allowing skills to compose multiple data sources without tight coupling.

**Sources:** [prior-auth-review-skill/README.md:33-41](), [README.md:44-58](), [npi-registry/.claude-plugin/plugin.json:1-16](), [cms-coverage/.claude-plugin/plugin.json:1-16]()

---

## External Infrastructure

The NPI Registry MCP server is hosted by DeepSense.ai at `https://mcp.deepsense.ai/npi_registry/mcp` [npi-registry/.claude-plugin/plugin.json:12](). This external hosting model provides several benefits:

1. **Centralized Data Management**: DeepSense.ai maintains the connection to CMS's NPPES dataset and handles updates
2. **Scalability**: The external server can handle multiple concurrent requests from different Claude Code users
3. **No Local Dependencies**: Skills don't need to download or maintain the ~7GB NPPES dataset locally
4. **Consistent API**: All users access the same standardized interface regardless of their local environment

The external server infrastructure is separate from the Anthropic-hosted PubMed MCP server (`https://pubmed.mcp.claude.com/mcp`) [pubmed/.claude-plugin/plugin.json:12](), demonstrating the flexible hosting model for MCP servers.

**Sources:** [npi-registry/.claude-plugin/plugin.json:11-14](), [pubmed/.claude-plugin/plugin.json:11-14](), [README.md:46-51]()

---

# Page: PubMed Literature Search

# PubMed Literature Search

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/release.yml](.github/workflows/release.yml)
- [README.md](README.md)
- [clinical-trial-protocol-skill/README.md](clinical-trial-protocol-skill/README.md)
- [cms-coverage/.claude-plugin/plugin.json](cms-coverage/.claude-plugin/plugin.json)
- [npi-registry/.claude-plugin/plugin.json](npi-registry/.claude-plugin/plugin.json)
- [prior-auth-review-skill/README.md](prior-auth-review-skill/README.md)
- [pubmed/.claude-plugin/plugin.json](pubmed/.claude-plugin/plugin.json)

</details>



## Purpose and Scope

This document describes the PubMed MCP Server, which provides access to the National Library of Medicine's biomedical literature database. The server enables Claude to search PubMed citations, retrieve article metadata and abstracts, and access full-text content from PubMed Central (PMC) when available.

For information about other MCP servers in the marketplace, see:
- CMS Coverage Database ([4.1](#4.1))
- NPI Registry ([4.2](#4.2))
- ICD-10 Codes ([4.4](#4.4))

For skills that use this MCP server, see:
- Clinical Trial Protocol Generator ([3.1](#3.1))

**Sources:** [pubmed/.claude-plugin/plugin.json:1-15](), [README.md:44-58]()

---

## MCP Server Configuration

The PubMed MCP Server is a remote HTTP-based service hosted by Anthropic. Unlike the healthcare-domain-specific MCP servers (CMS Coverage, NPI Registry, ICD-10), PubMed is maintained directly by Anthropic infrastructure.

### Plugin Metadata

| Property | Value |
|----------|-------|
| **Name** | `pubmed` |
| **Version** | 1.0.0 |
| **Type** | HTTP MCP Server |
| **Endpoint** | `https://pubmed.mcp.claude.com/mcp` |
| **Author** | Anthropic |
| **Marketplace ID** | `anthropics/healthcare/pubmed` |

**Sources:** [pubmed/.claude-plugin/plugin.json:1-15]()

### Configuration Structure

```mermaid
graph TD
    MP["marketplace.json<br/>Marketplace Registry"]
    PJ["pubmed/.claude-plugin/plugin.json<br/>MCP Configuration"]
    EP["https://pubmed.mcp.claude.com/mcp<br/>MCP Server Endpoint"]
    
    subgraph "Repository Structure"
        MP --> |"references"| PJ
        PJ --> |"url: https://pubmed.mcp.claude.com/mcp"| EP
    end
    
    subgraph "External Infrastructure"
        EP --> PM["PubMed Database<br/>NLM/NIH"]
        EP --> PMC["PubMed Central<br/>Full-Text Archive"]
    end
    
    subgraph "Installation"
        CMD["claude mcp add-from-marketplace<br/>anthropics/healthcare/pubmed"]
        CMD --> MP
    end
```

**Sources:** [pubmed/.claude-plugin/plugin.json:1-15](), [README.md:55-58]()

---

## MCP Server Architecture

The PubMed MCP Server follows the standard HTTP-based MCP pattern used throughout the healthcare marketplace. It exposes tools and resources via the Model Context Protocol, allowing Claude to interact with PubMed's APIs programmatically.

### System Integration Diagram

```mermaid
graph TB
    subgraph "Claude Code Environment"
        USER["User"]
        CLAUDE["Claude AI"]
    end
    
    subgraph "Healthcare Marketplace"
        CTP["clinical-trial-protocol-skill<br/>Step 1: Research Phase"]
        PAR["prior-auth-review-skill<br/>(Optional Usage)"]
    end
    
    subgraph "MCP Layer"
        PLUGIN["pubmed/.claude-plugin/plugin.json<br/>MCP Configuration"]
    end
    
    subgraph "Anthropic Infrastructure"
        MCP["PubMed MCP Server<br/>pubmed.mcp.claude.com"]
    end
    
    subgraph "External Data Source"
        PUBMED["PubMed API<br/>E-utilities"]
        PMC["PubMed Central API<br/>Full-Text Content"]
    end
    
    USER --> CLAUDE
    CLAUDE --> CTP
    CLAUDE --> PAR
    CTP --> |"uses"| PLUGIN
    PAR -.-> |"optional"| PLUGIN
    PLUGIN --> |"HTTP MCP Protocol"| MCP
    MCP --> |"NCBI API calls"| PUBMED
    MCP --> |"NCBI API calls"| PMC
```

**Sources:** [pubmed/.claude-plugin/plugin.json:1-15](), [README.md:44-58](), [clinical-trial-protocol-skill/README.md:48-50]()

---

## Available Capabilities

The PubMed MCP Server provides access to the complete biomedical literature indexed in PubMed and archived in PubMed Central. The server description indicates the following capabilities:

### Core Features

| Feature | Description | Use Case |
|---------|-------------|----------|
| **Article Search** | Query PubMed database using keywords, MeSH terms, author names, journals | Finding relevant clinical studies, review articles, case reports |
| **Metadata Retrieval** | Access citation information (title, authors, journal, publication date, DOI) | Building reference lists, tracking publications |
| **Abstract Access** | Retrieve structured abstracts for indexed articles | Quick review of study methods and findings |
| **Full-Text Content** | Access complete article text when available in PMC Open Access subset | Deep analysis of study protocols, results, discussion |
| **Related Research** | Find similar articles using PubMed's "Similar Articles" algorithm | Literature review, finding comparable studies |

**Sources:** [pubmed/.claude-plugin/plugin.json:4]()

### MCP Tools Pattern

While the specific tool names are not documented in the repository, HTTP-based MCP servers typically expose tools following this pattern:

```mermaid
graph LR
    subgraph "Expected MCP Tools"
        SEARCH["search_articles<br/>Query: string<br/>Max results: int"]
        GET["get_article<br/>PMID: string"]
        RELATED["find_related<br/>PMID: string"]
        FULLTEXT["get_fulltext<br/>PMCID: string"]
    end
    
    subgraph "Response Objects"
        RESULTS["Search Results<br/>- PMID list<br/>- Citation count<br/>- Metadata"]
        ARTICLE["Article Details<br/>- Title, Authors<br/>- Abstract<br/>- MeSH terms"]
        FULL["Full Text<br/>- HTML/XML<br/>- Sections<br/>- References"]
    end
    
    SEARCH --> RESULTS
    GET --> ARTICLE
    RELATED --> RESULTS
    FULLTEXT --> FULL
```

**Sources:** [pubmed/.claude-plugin/plugin.json:4]()

---

## Integration with Healthcare Skills

The PubMed MCP Server is designed as shared infrastructure across multiple healthcare skills. Its primary documented integration is with the Clinical Trial Protocol Generator skill.

### Clinical Trial Protocol Generator Usage

The PubMed server supports the research phase (Step 1) of protocol generation, though the workflow notes indicate primary research happens via ClinicalTrials.gov MCP:

**Workflow Context:**

| Workflow Step | Description | PubMed Role |
|---------------|-------------|-------------|
| **Step 0: Initialize** | Collect intervention metadata | Not used |
| **Step 1: Research** | Search ClinicalTrials.gov, find FDA guidance | Optional literature review |
| **Step 2-5: Generation** | Build protocol sections | Not used |

The clinical trial protocol skill lists these research requirements:
- ClinicalTrials.gov MCP Server (primary research source)
- WebSearch for FDA guidance documents
- PubMed (available but not explicitly required)

**Sources:** [clinical-trial-protocol-skill/README.md:37-50]()

### Prior Authorization Review Usage

The PubMed server is available to the Prior Authorization Review skill for optional use cases:

```mermaid
graph TD
    subgraph "Prior Auth Workflow"
        INTAKE["Subskill 1:<br/>Intake & Assessment"]
        DECISION["Subskill 2:<br/>Decision & Notification"]
    end
    
    subgraph "Data Sources"
        NPI["NPI Registry<br/>(Required)"]
        ICD["ICD-10 Codes<br/>(Required)"]
        CMS["CMS Coverage<br/>(Required)"]
        PM["PubMed<br/>(Optional)"]
    end
    
    subgraph "Use Cases for PubMed"
        EVIDENCE["Clinical Evidence<br/>Lookup"]
        RESEARCH["Off-Label<br/>Research"]
        POLICY["Policy Support<br/>Citations"]
    end
    
    INTAKE --> NPI
    INTAKE --> ICD
    INTAKE --> CMS
    INTAKE -.-> PM
    PM -.-> EVIDENCE
    PM -.-> RESEARCH
    PM -.-> POLICY
    DECISION --> INTAKE
```

**Sources:** [prior-auth-review-skill/README.md:27-66]()

---

## Installation and Configuration

### Adding to Claude Code

Install the PubMed MCP Server using the marketplace command:

```bash
claude mcp add-from-marketplace anthropics/healthcare/pubmed
```

This command:
1. Queries the marketplace registry at `.claude-plugin/marketplace.json`
2. Locates the `pubmed` MCP definition
3. Reads the configuration from `pubmed/.claude-plugin/plugin.json`
4. Registers the HTTP endpoint `https://pubmed.mcp.claude.com/mcp` with Claude

**Sources:** [README.md:52-58]()

### Verification

After installation, verify the MCP server is available by checking that Claude can access biomedical literature search capabilities. The server requires no authentication or local configuration—it's a public service hosted by Anthropic.

**Plugin Configuration Details:**

[pubmed/.claude-plugin/plugin.json:1-15]() contains the complete MCP server definition:

```json
{
  "name": "pubmed",
  "version": "1.0.0",
  "description": "Provides access to PubMed's biomedical citations...",
  "author": {
    "name": "Anthropic",
    "url": "https://www.anthropic.com/"
  },
  "mcpServers": {
    "PubMed": {
      "type": "http",
      "url": "https://pubmed.mcp.claude.com/mcp"
    }
  }
}
```

**Sources:** [pubmed/.claude-plugin/plugin.json:1-15]()

---

## Data Sources and Infrastructure

### Backend Architecture

```mermaid
graph TB
    subgraph "Anthropic Infrastructure"
        MCP["pubmed.mcp.claude.com<br/>MCP Server Instance"]
    end
    
    subgraph "NCBI Infrastructure (NIH/NLM)"
        EUTIL["E-utilities API<br/>eutils.ncbi.nlm.nih.gov"]
        ENTREZ["Entrez Programming Utilities<br/>PubMed, PMC databases"]
        MEDLINE["MEDLINE Database<br/>33M+ citations"]
        PMCOA["PMC Open Access Subset<br/>3M+ full-text articles"]
    end
    
    MCP --> |"HTTP API calls"| EUTIL
    EUTIL --> ENTREZ
    ENTREZ --> MEDLINE
    ENTREZ --> PMCOA
```

### Data Coverage

| Database | Content | Scale | Access |
|----------|---------|-------|--------|
| **PubMed** | Biomedical citations and abstracts | 33+ million records | Complete via MCP |
| **PubMed Central** | Full-text journal articles | 3+ million articles | Open Access subset only |
| **MEDLINE** | Curated subset with MeSH indexing | 27+ million records | Via PubMed queries |

**Sources:** [pubmed/.claude-plugin/plugin.json:4]()

### Hosting and Maintenance

Unlike the healthcare-specific MCP servers (CMS Coverage, NPI Registry, ICD-10) which are hosted by DeepSense.ai, the PubMed MCP server is maintained directly by Anthropic:

| Aspect | Detail |
|--------|--------|
| **Hosting** | Anthropic infrastructure (`pubmed.mcp.claude.com`) |
| **Maintenance** | Anthropic |
| **Endpoint Type** | HTTP MCP Server |
| **Authentication** | None required (public service) |
| **Rate Limiting** | Managed by Anthropic MCP infrastructure |

**Sources:** [pubmed/.claude-plugin/plugin.json:6-8](), [README.md:50]()

---

## Comparison with Other MCP Servers

### MCP Server Comparison Matrix

| MCP Server | Host | Domain | Required For |
|------------|------|--------|--------------|
| **PubMed** | Anthropic | Biomedical literature | None (optional) |
| **CMS Coverage** | DeepSense.ai | Medicare policies | Prior Auth Review |
| **NPI Registry** | DeepSense.ai | Provider credentials | Prior Auth Review |
| **ICD-10 Codes** | DeepSense.ai | Diagnosis codes | Prior Auth Review |

```mermaid
graph TB
    subgraph "Infrastructure Providers"
        ANT["Anthropic<br/>pubmed.mcp.claude.com"]
        DS["DeepSense.ai<br/>mcp.deepsense.ai"]
    end
    
    subgraph "MCP Servers"
        PM["PubMed<br/>Optional for research"]
        CMS["CMS Coverage<br/>Required for Prior Auth"]
        NPI["NPI Registry<br/>Required for Prior Auth"]
        ICD["ICD-10 Codes<br/>Required for Prior Auth"]
    end
    
    subgraph "Skills"
        CTP["clinical-trial-protocol-skill"]
        PAR["prior-auth-review-skill"]
    end
    
    ANT --> PM
    DS --> CMS
    DS --> NPI
    DS --> ICD
    
    PM -.-> CTP
    PM -.-> PAR
    CMS --> PAR
    NPI --> PAR
    ICD --> PAR
```

**Sources:** [README.md:44-58](), [cms-coverage/.claude-plugin/plugin.json:1-15](), [npi-registry/.claude-plugin/plugin.json:1-15](), [pubmed/.claude-plugin/plugin.json:1-15]()

---

# Page: ICD-10 Codes

# ICD-10 Codes

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [README.md](README.md)
- [cms-coverage/.claude-plugin/plugin.json](cms-coverage/.claude-plugin/plugin.json)
- [icd10-codes/.claude-plugin/plugin.json](icd10-codes/.claude-plugin/plugin.json)
- [npi-registry/.claude-plugin/plugin.json](npi-registry/.claude-plugin/plugin.json)
- [pubmed/.claude-plugin/plugin.json](pubmed/.claude-plugin/plugin.json)

</details>



## Purpose and Scope

This document describes the **ICD-10 Codes MCP Server**, an external data connector that provides Claude with access to the International Classification of Diseases, 10th Revision (ICD-10) code sets. The server exposes both ICD-10-CM (Clinical Modification) diagnosis codes and ICD-10-PCS (Procedure Coding System) procedure codes for medical classification and billing purposes.

For information about other healthcare data sources, see [CMS Coverage Database](#4.1), [NPI Registry](#4.2), and [PubMed Literature Search](#4.3). For information about how skills use this MCP server, see [Prior Authorization Review](#3.2) and specifically [Intake & Assessment Subskill](#3.2.1).

## Overview

The ICD-10 Codes MCP server is a remote HTTP-based connector hosted by deepsense.ai that provides programmatic access to standardized medical classification codes. Unlike inline skills which run within Claude's environment, this MCP server operates as an external service, allowing Claude to query diagnosis and procedure codes without embedding the entire code set locally.

**Key Characteristics:**

| Aspect | Details |
|--------|---------|
| **Plugin Name** | `icd10-codes` |
| **Plugin Type** | MCP Server (external data connector) |
| **Hosting** | DeepSense.ai infrastructure |
| **Protocol** | HTTP/HTTPS |
| **Code Sets** | ICD-10-CM (diagnosis), ICD-10-PCS (procedure) |
| **Primary Use Case** | Prior authorization code validation |

Sources: [.claude-plugin/marketplace.json:66-72](), [icd10-codes/.claude-plugin/plugin.json:1-16]()

## MCP Server Architecture

### Plugin Configuration Structure

The ICD-10 Codes connector follows the standard MCP server configuration pattern used throughout the healthcare marketplace:

```mermaid
graph TD
    MP["marketplace.json<br/>(.claude-plugin/)"]
    PLUGIN["plugin.json<br/>(icd10-codes/.claude-plugin/)"]
    EXT["DeepSense.ai MCP Server<br/>mcp.deepsense.ai/icd10_codes/mcp"]
    
    MP -->|"source: ./icd10-codes"| PLUGIN
    PLUGIN -->|"url (HTTP)"| EXT
    
    subgraph "Marketplace Registry"
        MP
    end
    
    subgraph "Local Configuration"
        PLUGIN
    end
    
    subgraph "External Infrastructure"
        EXT
    end
```

**Diagram: ICD-10 MCP Server Configuration Chain**

Sources: [.claude-plugin/marketplace.json:66-72](), [icd10-codes/.claude-plugin/plugin.json:1-16]()

### Configuration Files

#### Marketplace Registration

The marketplace entry defines the plugin metadata and discovery information:

[.claude-plugin/marketplace.json:66-72]()

```json
{
  "name": "icd10-codes",
  "source": "./icd10-codes",
  "description": "Access ICD-10-CM and ICD-10-PCS code sets",
  "category": "healthcare",
  "tags": ["icd-10", "diagnosis", "procedure", "billing", "medical-coding"]
}
```

#### Plugin Specification

The plugin configuration specifies the HTTP endpoint and server details:

[icd10-codes/.claude-plugin/plugin.json:1-16]()

| Field | Value | Purpose |
|-------|-------|---------|
| `name` | `"icd10-codes"` | Plugin identifier |
| `version` | `"1.0.0"` | Plugin version |
| `author.name` | `"deepsense.ai"` | Service provider |
| `mcpServers.type` | `"http"` | Connection protocol |
| `mcpServers.url` | `"https://mcp.deepsense.ai/icd10_codes/mcp"` | API endpoint |

Sources: [icd10-codes/.claude-plugin/plugin.json:1-16]()

## ICD-10 Code Sets

The ICD-10 system consists of two distinct but complementary code sets, both accessible through this MCP server:

```mermaid
graph LR
    subgraph "ICD-10-CM (Diagnosis Codes)"
        CM_CHARS["Format: 3-7 alphanumeric characters<br/>Example: E11.65"]
        CM_USE["Usage: Classify diseases, symptoms,<br/>external causes, conditions"]
        CM_BILLING["Billing: Required for claims"]
    end
    
    subgraph "ICD-10-PCS (Procedure Codes)"
        PCS_CHARS["Format: 7 alphanumeric characters<br/>Example: 0JH60XZ"]
        PCS_USE["Usage: Classify inpatient procedures<br/>and surgeries"]
        PCS_BILLING["Billing: Hospital/facility claims"]
    end
    
    MCP["ICD-10 Codes MCP Server<br/>mcp.deepsense.ai/icd10_codes/mcp"]
    
    MCP -->|"lookup_diagnosis"| CM_CHARS
    MCP -->|"lookup_procedure"| PCS_CHARS
```

**Diagram: ICD-10 Code Set Structure**

### ICD-10-CM (Clinical Modification)

ICD-10-CM codes are used to classify diagnoses, symptoms, and conditions in all healthcare settings (inpatient, outpatient, emergency, physician offices).

**Characteristics:**
- **Format**: 3-7 alphanumeric characters (e.g., `E11.65` for Type 2 diabetes with hyperglycemia)
- **Structure**: Category (first 3 chars) + subcategories + extensions
- **Use Cases**: 
  - Diagnosis documentation
  - Medical billing and claims
  - Prior authorization justification
  - Epidemiological tracking
  
**Example Codes:**
| Code | Description |
|------|-------------|
| `E11.65` | Type 2 diabetes mellitus with hyperglycemia |
| `I10` | Essential (primary) hypertension |
| `J44.0` | Chronic obstructive pulmonary disease with acute lower respiratory infection |

### ICD-10-PCS (Procedure Coding System)

ICD-10-PCS codes classify inpatient procedures performed in hospital settings.

**Characteristics:**
- **Format**: Exactly 7 alphanumeric characters (e.g., `0JH60XZ`)
- **Structure**: Each position has specific meaning (body system, root operation, body part, approach, device, qualifier)
- **Use Cases**:
  - Hospital inpatient procedure coding
  - Surgical procedure classification
  - Prior authorization for procedures

Sources: [icd10-codes/.claude-plugin/plugin.json:4]()

## Integration with Prior Authorization Review

The ICD-10 Codes MCP server is a critical dependency for the Prior Authorization Review skill, specifically used in the intake and assessment phase to validate diagnosis codes submitted with authorization requests.

```mermaid
graph TD
    PAR["Prior Authorization Review Skill<br/>prior-auth-review-skill/"]
    SUBSKILL1["Subskill 1:<br/>Intake & Assessment"]
    
    ICD_MCP["ICD-10 Codes MCP<br/>mcp.deepsense.ai/icd10_codes/mcp"]
    NPI_MCP["NPI Registry MCP"]
    CMS_MCP["CMS Coverage MCP"]
    
    PAR --> SUBSKILL1
    
    SUBSKILL1 -->|"Validate diagnosis codes"| ICD_MCP
    SUBSKILL1 -->|"Validate provider NPI"| NPI_MCP
    SUBSKILL1 -->|"Check coverage policy"| CMS_MCP
    
    ICD_MCP -->|"Code exists?<br/>Description matches?"| VALIDATION["Validation Result"]
    
    VALIDATION -->|"Valid"| ASSESSMENT["Generate approval<br/>recommendation"]
    VALIDATION -->|"Invalid"| DENIAL["Flag for denial"]
```

**Diagram: ICD-10 MCP Integration in Prior Authorization Workflow**

### Validation Workflow

During prior authorization review, the ICD-10 Codes MCP server is queried to:

1. **Verify Code Existence**: Confirm the submitted ICD-10 code exists in the official code set
2. **Validate Description**: Ensure the diagnosis description matches the code
3. **Check Code Currency**: Verify the code is current (not deprecated or outdated)
4. **Assess Medical Necessity**: Support evaluation of whether the diagnosis justifies the requested service

**Example Query Pattern:**

When a prior authorization request includes diagnosis code `E11.65`, the skill queries the ICD-10 MCP to:
- Confirm `E11.65` is a valid ICD-10-CM code
- Retrieve the official description ("Type 2 diabetes mellitus with hyperglycemia")
- Determine if the diagnosis supports the requested treatment or procedure

Sources: [README.md:28-32](), [.claude-plugin/marketplace.json:23-32]()

## Installation and Usage

### Adding the MCP Server

The ICD-10 Codes MCP server is installed separately from skills using the MCP marketplace command:

```bash
claude mcp add-from-marketplace anthropics/healthcare/icd10-codes
```

This command:
1. Reads the marketplace registry at [.claude-plugin/marketplace.json:66-72]()
2. Locates the plugin source at `./icd10-codes`
3. Loads the plugin configuration from [icd10-codes/.claude-plugin/plugin.json:1-16]()
4. Registers the HTTP endpoint `https://mcp.deepsense.ai/icd10_codes/mcp` with Claude

**Note**: Unlike the CMS Coverage, NPI Registry, and PubMed servers, the ICD-10 Codes server is **not** listed in the README's MCP installation instructions [README.md:44-58](). However, it is registered in the marketplace and available for installation.

### Prerequisites

| Requirement | Details |
|-------------|---------|
| **Network Access** | HTTPS connectivity to `mcp.deepsense.ai` |
| **Authentication** | Managed by Claude Code environment |
| **Dependencies** | None - external HTTP service |

Sources: [README.md:52-58](), [icd10-codes/.claude-plugin/plugin.json:9-14]()

## Query Patterns and Use Cases

### Common Query Types

```mermaid
graph LR
    subgraph "Query Operations"
        LOOKUP["lookup_code()"]
        SEARCH["search_codes()"]
        VALIDATE["validate_code()"]
        DESCRIBE["get_description()"]
    end
    
    subgraph "Response Data"
        CODE["Code: E11.65"]
        DESC["Description: Type 2 diabetes..."]
        VALID["Valid: true/false"]
        CATEGORY["Category: Endocrine diseases"]
    end
    
    LOOKUP --> CODE
    LOOKUP --> DESC
    SEARCH --> CODE
    VALIDATE --> VALID
    DESCRIBE --> DESC
    DESCRIBE --> CATEGORY
```

**Diagram: ICD-10 MCP Server Query Operations**

### Use Case 1: Prior Authorization Code Validation

**Scenario**: A prior authorization request includes diagnosis code `E11.65` for a glucose monitoring device.

**Workflow**:
1. Skill queries ICD-10 MCP: `lookup_code("E11.65", type="diagnosis")`
2. Server returns: `{"code": "E11.65", "description": "Type 2 diabetes mellitus with hyperglycemia", "valid": true}`
3. Skill validates the code exists and description matches the request
4. Code validation informs the medical necessity assessment

### Use Case 2: Diagnosis Code Search

**Scenario**: Searching for diabetes-related diagnosis codes.

**Workflow**:
1. Skill queries: `search_codes("diabetes mellitus type 2", type="diagnosis")`
2. Server returns multiple matching codes:
   - `E11` (Type 2 diabetes mellitus without complications)
   - `E11.65` (Type 2 diabetes mellitus with hyperglycemia)
   - `E11.9` (Type 2 diabetes mellitus without complications)
3. User selects appropriate code based on patient condition

### Use Case 3: Procedure Code Lookup

**Scenario**: Validating a procedure code for prior authorization of a surgical intervention.

**Workflow**:
1. Skill queries: `lookup_code("0JH60XZ", type="procedure")`
2. Server returns ICD-10-PCS code details
3. Skill confirms procedure classification matches authorization request

Sources: [.claude-plugin/marketplace.json:66-72](), [icd10-codes/.claude-plugin/plugin.json:1-16]()

## Technical Architecture

### Service Infrastructure

```mermaid
graph TB
    subgraph "Claude Code Environment"
        SKILL["prior-auth-review-skill"]
        MCP_CLIENT["MCP Client<br/>(built into Claude)"]
    end
    
    subgraph "DeepSense.ai Infrastructure"
        ENDPOINT["HTTPS Endpoint<br/>mcp.deepsense.ai/icd10_codes/mcp"]
        DATABASE["ICD-10 Code Database<br/>(CM + PCS)"]
    end
    
    SKILL -->|"MCP protocol"| MCP_CLIENT
    MCP_CLIENT -->|"HTTPS requests"| ENDPOINT
    ENDPOINT -->|"queries"| DATABASE
    DATABASE -->|"code data"| ENDPOINT
    ENDPOINT -->|"JSON response"| MCP_CLIENT
    MCP_CLIENT -->|"structured data"| SKILL
```

**Diagram: ICD-10 MCP Server Request Flow**

### Configuration Mapping

The following table maps configuration fields to their roles in the system:

| Configuration Path | Field | Value | System Role |
|-------------------|-------|-------|-------------|
| `marketplace.json` | `plugins[6].name` | `"icd10-codes"` | Marketplace identifier |
| `marketplace.json` | `plugins[6].source` | `"./icd10-codes"` | Local config directory |
| `plugin.json` | `name` | `"icd10-codes"` | Plugin name (matches marketplace) |
| `plugin.json` | `mcpServers.type` | `"http"` | Connection protocol |
| `plugin.json` | `mcpServers.url` | `"https://mcp.deepsense.ai/icd10_codes/mcp"` | API endpoint URL |
| `plugin.json` | `author.name` | `"deepsense.ai"` | Service provider |

Sources: [.claude-plugin/marketplace.json:66-72](), [icd10-codes/.claude-plugin/plugin.json:1-16]()

## Comparison with Other MCP Servers

The ICD-10 Codes MCP server is one of four healthcare data connectors in the marketplace:

| MCP Server | Purpose | Provider | Code Sets |
|------------|---------|----------|-----------|
| **ICD-10 Codes** | Diagnosis/procedure codes | deepsense.ai | ICD-10-CM, ICD-10-PCS |
| CMS Coverage | Medicare coverage policies | deepsense.ai | NCDs, LCDs |
| NPI Registry | Provider identification | deepsense.ai | NPI database |
| PubMed | Biomedical literature | Anthropic | PubMed, PMC |

**Shared Infrastructure Pattern**: The ICD-10, CMS Coverage, and NPI Registry servers all:
- Use the same hosting provider (deepsense.ai)
- Share the same URL pattern (`mcp.deepsense.ai/<service>/mcp`)
- Follow identical plugin configuration structures
- Support the Prior Authorization Review skill

**Unique Characteristics**: The ICD-10 server is distinct in providing:
- Two separate code sets (CM and PCS) within a single endpoint
- Standardized medical classification codes used across all healthcare settings
- Alphanumeric code validation beyond simple lookups

Sources: [.claude-plugin/marketplace.json:45-72](), [cms-coverage/.claude-plugin/plugin.json:1-15](), [npi-registry/.claude-plugin/plugin.json:1-15](), [pubmed/.claude-plugin/plugin.json:1-15]()

## Release and Versioning

The ICD-10 Codes MCP server follows the standard marketplace release workflow:

### Version Information

| Aspect | Details |
|--------|---------|
| Current Version | `1.0.0` [icd10-codes/.claude-plugin/plugin.json:3]() |
| Marketplace Version | `1.0.0` [.claude-plugin/marketplace.json:8]() |
| Release Workflow | Not packaged (external service) |

### Update Process

Unlike skills which are packaged into zip files during releases [.github/workflows/release.yml:18-42](), MCP server configurations are not included in the release artifacts. Updates to the ICD-10 MCP server involve:

1. **Configuration Updates**: Changes to [icd10-codes/.claude-plugin/plugin.json:1-16]()
2. **Marketplace Updates**: Version bumps in [.claude-plugin/marketplace.json:66-72]()
3. **External Service Updates**: Backend changes managed by deepsense.ai (transparent to users)

The external service at `https://mcp.deepsense.ai/icd10_codes/mcp` can be updated independently of the plugin configuration, allowing code set updates without requiring marketplace version changes.

Sources: [icd10-codes/.claude-plugin/plugin.json:3](), [.github/workflows/release.yml:1-43]()

---

# Page: CI/CD and Automation

# CI/CD and Automation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/claude-code-review.yml](.github/workflows/claude-code-review.yml)
- [.github/workflows/claude-skill-review.yml](.github/workflows/claude-skill-review.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [README.md](README.md)

</details>



## Purpose and Scope

This section documents the continuous integration and continuous deployment (CI/CD) infrastructure that ensures quality and automates release management for the healthcare marketplace. The system consists of three GitHub Actions workflows that provide automated skill reviews, code reviews, and release packaging.

For detailed documentation of specific workflows, see:
- Skill Review Workflow: [#5.1](#5.1)
- Code Review Workflow: [#5.2](#5.2)
- Release Workflow: [#5.3](#5.3)

---

## Architecture Overview

The healthcare marketplace employs three distinct automated workflows that operate at different stages of the development lifecycle. Each workflow serves a specific quality assurance or deployment purpose:

| Workflow | File | Trigger | Primary Purpose | Importance Score |
|----------|------|---------|----------------|------------------|
| Skill Review | `claude-skill-review.yml` | PR events (opened, synchronize, ready_for_review, reopened) | Automated review of skill changes using Claude | 49.07 |
| Code Review | `claude-code-review.yml` | PR events (opened, synchronize, ready_for_review, reopened) | General code review capabilities | 1.62 |
| Release | `release.yml` | Version tags (`v*`) | Package skills into distributable artifacts | 1.08 |

The skill review workflow dominates the CI/CD infrastructure in terms of importance, serving as the primary quality gate for all skill modifications.

**Sources:** [.github/workflows/claude-skill-review.yml:1-88](), [.github/workflows/claude-code-review.yml:1-45](), [.github/workflows/release.yml:1-43]()

---

## Workflow Architecture

### CI/CD Pipeline Flow

```mermaid
graph TB
    subgraph "Trigger Events"
        PR["Pull Request<br/>opened/synchronize/<br/>ready_for_review/reopened"]
        TAG["Git Tag Push<br/>v*"]
    end
    
    subgraph "Skill Review Workflow<br/>claude-skill-review.yml"
        DETECT["Job: detect-skills<br/>Scans for SKILL.md changes"]
        REVIEW["Job: review-skill<br/>Matrix strategy<br/>Parallelized reviews"]
        DETECT -->|"outputs: skills, has_skills"| REVIEW
    end
    
    subgraph "Code Review Workflow<br/>claude-code-review.yml"
        CLAUDE_REV["Job: claude-review<br/>General code feedback"]
    end
    
    subgraph "Release Workflow<br/>release.yml"
        PACKAGE["Job: release<br/>Package *-skill/ directories"]
        ZIP["Create .zip files<br/>Pattern: skill-name-vX.Y.Z.zip"]
        GH_RELEASE["Create Draft Release<br/>softprops/action-gh-release@v1"]
        PACKAGE --> ZIP
        ZIP --> GH_RELEASE
    end
    
    subgraph "Claude Code Integration"
        ACTION["anthropics/claude-code-action@v1"]
        PLUGIN_SKILL["Plugin: skill-creator<br/>from anthropic-agent-skills"]
        PLUGIN_CODE["Plugin: code-review<br/>from claude-code-plugins"]
        ACTION --> PLUGIN_SKILL
        ACTION --> PLUGIN_CODE
    end
    
    subgraph "GitHub Resources"
        PR_COMMENTS["PR Comments"]
        RELEASES["GitHub Releases"]
    end
    
    PR -->|"triggers"| DETECT
    PR -->|"triggers"| CLAUDE_REV
    TAG -->|"triggers"| PACKAGE
    
    REVIEW -->|"uses"| ACTION
    CLAUDE_REV -->|"uses"| ACTION
    
    PLUGIN_SKILL -->|"posts feedback"| PR_COMMENTS
    PLUGIN_CODE -->|"posts feedback"| PR_COMMENTS
    
    GH_RELEASE -->|"creates draft"| RELEASES
```

**Sources:** [.github/workflows/claude-skill-review.yml:3-10](), [.github/workflows/claude-code-review.yml:3-11](), [.github/workflows/release.yml:3-6]()

---

## Workflow Trigger Patterns

### Pull Request Triggers

Both the skill review and code review workflows use identical trigger configurations:

```yaml
on:
  pull_request:
    types: [opened, synchronize, ready_for_review, reopened]
```

These events ensure that automation runs:
- **opened**: When a new PR is created
- **synchronize**: When new commits are pushed to the PR branch
- **ready_for_review**: When a draft PR is marked ready
- **reopened**: When a closed PR is reopened

The workflows also support `workflow_call` to enable reusable workflow patterns from other repositories.

**Sources:** [.github/workflows/claude-skill-review.yml:3-10](), [.github/workflows/claude-code-review.yml:3-11]()

### Release Triggers

The release workflow uses tag-based triggers:

```yaml
on:
  push:
    tags:
      - 'v*'
```

Any tag matching the pattern `v*` (e.g., `v1.0.0`, `v2.1.3`) triggers the release process. This follows semantic versioning conventions and allows manual control over when releases are published.

**Sources:** [.github/workflows/release.yml:3-6]()

---

## Claude Code Action Integration

All three workflows leverage the `anthropics/claude-code-action@v1` GitHub Action to invoke Claude-powered automation. The action requires specific configuration parameters:

### Configuration Parameters

| Parameter | Purpose | Example Value |
|-----------|---------|---------------|
| `claude_code_oauth_token` | Authentication for Claude API | `${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}` |
| `plugin_marketplaces` | Marketplace URLs to load plugins from | `https://github.com/anthropics/skills.git` |
| `plugins` | Specific plugins to install | `example-skills@anthropic-agent-skills` |
| `claude_args` | Command-line arguments for Claude | `--allowedTools "Bash,Read,Glob"` |
| `prompt` | Task description for Claude | Text describing the review task |

### Secret Management

The workflows require the `CLAUDE_CODE_OAUTH_TOKEN` secret, which must be configured at the repository level. The skill review workflow accepts this as a workflow input for reusability:

```yaml
workflow_call:
  secrets:
    CLAUDE_CODE_OAUTH_TOKEN:
      required: true
```

**Sources:** [.github/workflows/claude-skill-review.yml:6-9](), [.github/workflows/claude-skill-review.yml:76-84](), [.github/workflows/claude-code-review.yml:34-44]()

---

## Job Architecture and Dependencies

### Skill Review Job Dependencies

```mermaid
graph LR
    subgraph "detect-skills Job"
        CHECKOUT1["actions/checkout@v4<br/>fetch-depth: 0"]
        GIT_DIFF["git diff command<br/>origin/base_ref...HEAD"]
        FIND_SKILLS["find command<br/>Locate SKILL.md files"]
        MATCH_LOGIC["Shell script<br/>Match changed files to skills"]
        JSON_OUTPUT["jq command<br/>Output JSON array"]
        
        CHECKOUT1 --> GIT_DIFF
        CHECKOUT1 --> FIND_SKILLS
        GIT_DIFF --> MATCH_LOGIC
        FIND_SKILLS --> MATCH_LOGIC
        MATCH_LOGIC --> JSON_OUTPUT
    end
    
    subgraph "Job Outputs"
        OUT_SKILLS["output: skills<br/>JSON array of skill paths"]
        OUT_HAS["output: has_skills<br/>boolean flag"]
    end
    
    JSON_OUTPUT --> OUT_SKILLS
    JSON_OUTPUT --> OUT_HAS
    
    subgraph "review-skill Job"
        CONDITION["if: has_skills == true"]
        MATRIX["strategy: matrix<br/>skill: fromJson(skills)"]
        PARALLEL["Parallel execution<br/>fail-fast: false"]
    end
    
    OUT_HAS --> CONDITION
    OUT_SKILLS --> MATRIX
    MATRIX --> PARALLEL
```

The `detect-skills` job produces structured outputs that control the `review-skill` job:
- **needs**: `review-skill` depends on `detect-skills` completing first
- **conditional execution**: Only runs if `has_skills == 'true'`
- **matrix strategy**: Parallelizes reviews across all detected skills

**Sources:** [.github/workflows/claude-skill-review.yml:12-53](), [.github/workflows/claude-skill-review.yml:55-67]()

---

## Permission Model

GitHub Actions workflows require explicit permissions to interact with repository resources. The healthcare marketplace workflows use a least-privilege model:

### Skill Review Permissions

```yaml
permissions:
  contents: read       # Read repository files
  pull-requests: write # Post PR comments
  issues: write        # Write to issue tracker
  id-token: write      # OIDC token for authentication
```

### Code Review Permissions

```yaml
permissions:
  contents: read       # Read repository files
  pull-requests: read  # Read PR metadata
  issues: read         # Read issue metadata
  id-token: write      # OIDC token for authentication
```

### Release Permissions

```yaml
permissions:
  contents: write      # Create releases and upload assets
```

The skill review workflow requires write access to post feedback comments, while the code review workflow uses read-only access. The release workflow needs write access to create GitHub releases.

**Sources:** [.github/workflows/claude-skill-review.yml:63-67](), [.github/workflows/claude-code-review.yml:22-26](), [.github/workflows/release.yml:8-9]()

---

## Development Lifecycle Integration

### Quality Gates in the Pull Request Flow

```mermaid
stateDiagram-v2
    [*] --> PR_Created
    
    state PR_Created {
        [*] --> Skill_Review_Triggered
        [*] --> Code_Review_Available
    }
    
    Skill_Review_Triggered --> detect_skills_job
    
    state detect_skills_job {
        [*] --> Git_Diff_Analysis
        Git_Diff_Analysis --> SKILL_MD_Discovery
        SKILL_MD_Discovery --> Match_Changed_Files
        Match_Changed_Files --> Output_Skills_JSON
    }
    
    Output_Skills_JSON --> Conditional_Check
    
    state Conditional_Check <<choice>>
    Conditional_Check --> review_skill_job: has_skills == true
    Conditional_Check --> Skip_Review: has_skills == false
    
    state review_skill_job {
        [*] --> Matrix_Setup
        Matrix_Setup --> Parallel_Reviews
        
        state Parallel_Reviews {
            Skill_A: Review skill A
            Skill_B: Review skill B
            Skill_C: Review skill C
            --
            [*] --> Skill_A
            [*] --> Skill_B
            [*] --> Skill_C
        }
        
        Parallel_Reviews --> Post_Feedback
    }
    
    Code_Review_Available --> Manual_Trigger: @claude mention
    Manual_Trigger --> claude_review_job
    
    review_skill_job --> Human_Review
    claude_review_job --> Human_Review
    Skip_Review --> Human_Review
    
    Human_Review --> Approval
    Human_Review --> Request_Changes
    Request_Changes --> PR_Updated
    PR_Updated --> Skill_Review_Triggered
    
    Approval --> [*]
```

**Sources:** [.github/workflows/claude-skill-review.yml:1-88](), [.github/workflows/claude-code-review.yml:1-45]()

---

## Release Process

The release workflow automates skill packaging when version tags are pushed:

### Release Job Steps

1. **Checkout**: Retrieve repository code at the tagged commit
2. **Package Skills**: Scan for directories matching `*-skill/` pattern
3. **Create Archives**: Generate zip files with naming pattern `{skill-name}-{tag}.zip`
4. **Draft Release**: Create GitHub release with auto-generated notes

### Packaging Logic

The workflow uses shell scripting to locate and package skills:

```bash
for skill_dir in *-skill/; do
  if [ -d "$skill_dir" ]; then
    skill_name="${skill_dir%/}"
    cd "$skill_name"
    zip -r "../${skill_name}-${GITHUB_REF_NAME}.zip" .
    cd ..
  fi
done
```

This pattern ensures that any directory ending in `-skill/` is automatically packaged without manual configuration. The `GITHUB_REF_NAME` variable contains the tag name (e.g., `v1.2.0`).

**Sources:** [.github/workflows/release.yml:18-33]()

---

## Workflow Execution Context

### Environment Variables

The workflows rely on GitHub-provided context variables:

| Variable | Description | Usage |
|----------|-------------|-------|
| `github.base_ref` | Base branch name (target of PR) | Git diff comparison: `origin/${{ github.base_ref }}` |
| `github.event.pull_request.number` | PR number | Included in Claude prompts for context |
| `github.repository` | Repository full name | Passed to code review plugin |
| `GITHUB_REF_NAME` | Tag or branch name | Used in release artifact naming |

### Matrix Strategy Configuration

The `review-skill` job uses GitHub's matrix strategy for parallelization:

```yaml
strategy:
  matrix:
    skill: ${{ fromJson(needs.detect-skills.outputs.skills) }}
  fail-fast: false
```

Key characteristics:
- **Dynamic matrix**: Populated from the `detect-skills` job output
- **fail-fast: false**: All skill reviews complete even if one fails
- **Parallel execution**: GitHub Actions runs multiple jobs concurrently

**Sources:** [.github/workflows/claude-skill-review.yml:59-62](), [.github/workflows/claude-skill-review.yml:83-87]()

---

## Integration with Claude Skills

### Skill Review Plugin Integration

The skill review workflow uses the `skill-creator` plugin from the `anthropic-agent-skills` marketplace:

```yaml
plugin_marketplaces: 'https://github.com/anthropics/skills.git'
plugins: 'example-skills@anthropic-agent-skills'
```

The prompt instructs Claude to:
1. Use the `skill-creator` skill to perform the review
2. Analyze changes with `git diff origin/${{ github.base_ref }} -- ${{ matrix.skill }}/`
3. Provide full reviews for new skills, or focused reviews for modifications
4. Post feedback using `gh pr comment` command

### Allowed Tools Configuration

The workflows restrict Claude's tool access for security:

```yaml
claude_args: '--allowedTools "Bash(gh pr comment:*),Bash(git:*),Read,Glob,Grep,Skill"'
```

Permitted operations:
- **Bash(gh pr comment:\*)**: Post PR comments via GitHub CLI
- **Bash(git:\*)**: Execute git commands for diff analysis
- **Read, Glob, Grep**: File system operations for code inspection
- **Skill**: Invoke other Claude skills

**Sources:** [.github/workflows/claude-skill-review.yml:76-87](), [.github/workflows/claude-code-review.yml:37-41]()

---

## Workflow Outputs and Artifacts

### Skill Review Outputs

The `detect-skills` job produces outputs consumed by downstream jobs:

```yaml
outputs:
  skills: ${{ steps.detect.outputs.skills }}
  has_skills: ${{ steps.detect.outputs.has_skills }}
```

Example output format:
```json
{
  "skills": ["clinical-trial-protocol-skill", "prior-auth-review-skill"],
  "has_skills": "true"
}
```

### Release Artifacts

The release workflow creates distributable packages:
- **Format**: ZIP archives
- **Naming**: `{skill-name}-{tag}.zip` (e.g., `fhir-developer-skill-v1.0.0.zip`)
- **Contents**: Complete skill directory including `SKILL.md`, `references/`, `scripts/`, and `assets/`
- **Attachment**: Uploaded to GitHub release as downloadable assets

**Sources:** [.github/workflows/claude-skill-review.yml:14-16](), [.github/workflows/claude-skill-review.yml:46-52](), [.github/workflows/release.yml:18-42]()

---

## Error Handling and Robustness

### Fail-Fast Strategy

The skill review workflow disables fail-fast behavior to ensure comprehensive feedback:

```yaml
fail-fast: false
```

This configuration ensures that if one skill fails review, other skills continue to be reviewed. Developers receive feedback on all modified skills rather than stopping at the first failure.

### Conditional Execution

The `review-skill` job includes a conditional guard:

```yaml
if: needs.detect-skills.outputs.has_skills == 'true'
```

This prevents unnecessary job execution when no skills are modified in a PR, conserving CI resources and reducing noise in the Actions log.

### Draft Release Strategy

The release workflow creates draft releases rather than immediately publishing:

```yaml
draft: true
prerelease: false
```

This allows manual verification of release artifacts before making them publicly available.

**Sources:** [.github/workflows/claude-skill-review.yml:57](), [.github/workflows/claude-skill-review.yml:62](), [.github/workflows/release.yml:41-42]()

---

## Summary

The healthcare marketplace CI/CD infrastructure provides three automated workflows that ensure quality and streamline releases:

1. **Skill Review**: Automated Claude-powered reviews of skill changes with intelligent change detection and parallel execution
2. **Code Review**: General-purpose code feedback triggered by PR events
3. **Release**: Automated packaging and distribution of skills via version tags

The skill review workflow serves as the primary quality gate with the highest importance score (49.07), implementing sophisticated detection logic, matrix-based parallelization, and integration with the `skill-creator` plugin. All workflows leverage the `anthropics/claude-code-action` for consistent Claude integration patterns.

**Sources:** [.github/workflows/claude-skill-review.yml:1-88](), [.github/workflows/claude-code-review.yml:1-45](), [.github/workflows/release.yml:1-43]()

---

# Page: Skill Review Workflow

# Skill Review Workflow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/claude-skill-review.yml](.github/workflows/claude-skill-review.yml)

</details>



## Purpose and Scope

This document provides comprehensive documentation of the automated skill review system implemented in [.github/workflows/claude-skill-review.yml](). The skill review workflow is the primary quality assurance mechanism for healthcare skills in this repository, using Claude itself to review skill changes before they are merged.

This page covers the overall workflow architecture, job orchestration, and integration patterns. For detailed information about the skill detection algorithm, see [5.1.1](#5.1.1). For information about the matrix review strategy and parallel execution, see [5.1.2](#5.1.2). For general code review capabilities triggered by `@claude` mentions, see [5.2](#5.2).

**Sources:** [.github/workflows/claude-skill-review.yml:1-88]()

## Workflow Overview

The skill review workflow is the most critical component of the CI/CD infrastructure (importance: 49.07). It implements an AI-powered quality gate that automatically reviews every skill change in pull requests, ensuring healthcare skills meet quality standards before merging.

The workflow operates as a two-stage pipeline:

1. **Detection Stage** - Identifies which skills have been modified in a pull request
2. **Review Stage** - Executes parallel Claude-powered reviews for each affected skill

This architecture enables efficient, targeted reviews that scale across multiple skills without requiring manual expert review on every change.

**Sources:** [.github/workflows/claude-skill-review.yml:1-88]()

## Workflow Triggers

The workflow is triggered by GitHub pull request events and supports both automatic and reusable execution patterns.

### Trigger Events

| Event Type | Description | Configuration |
|------------|-------------|---------------|
| `pull_request.opened` | New PR created | Runs immediately on PR creation |
| `pull_request.synchronize` | New commits pushed to PR | Re-runs on each push |
| `pull_request.ready_for_review` | Draft PR marked ready | Runs when draft status removed |
| `pull_request.reopened` | Closed PR reopened | Runs on PR reopen |
| `workflow_call` | Called from another workflow | Requires `CLAUDE_CODE_OAUTH_TOKEN` secret |

The workflow does **not** trigger on draft pull requests until they are marked ready for review, preventing unnecessary reviews during active development.

**Sources:** [.github/workflows/claude-skill-review.yml:3-9]()

## Architecture Diagram

```mermaid
graph TB
    subgraph "GitHub Events"
        PR["pull_request<br/>[opened, synchronize,<br/>ready_for_review, reopened]"]
        WC["workflow_call<br/>(Reusable Workflow)"]
    end
    
    subgraph "Job: detect-skills"
        CO1["actions/checkout@v4<br/>fetch-depth: 0"]
        GD["git diff origin/base_ref...HEAD"]
        FIND["find . -name SKILL.md"]
        MATCH["Match changed files<br/>to skill directories"]
        OUT["outputs.skills: JSON array<br/>outputs.has_skills: boolean"]
        
        CO1 --> GD
        CO1 --> FIND
        GD --> MATCH
        FIND --> MATCH
        MATCH --> OUT
    end
    
    subgraph "Job: review-skill"
        COND["if: has_skills == true"]
        MAT["strategy.matrix.skill<br/>fromJson(skills)"]
        CO2["actions/checkout@v4<br/>fetch-depth: 0"]
        CA["anthropics/claude-code-action@v1"]
        PLUGIN["plugin: skill-creator<br/>from anthropic-agent-skills"]
        GD2["git diff origin/base_ref<br/>-- skill/"]
        COMMENT["gh pr comment<br/>(Post feedback)"]
        
        COND --> MAT
        MAT --> CO2
        CO2 --> CA
        CA --> PLUGIN
        PLUGIN --> GD2
        GD2 --> COMMENT
    end
    
    PR --> CO1
    WC --> CO1
    OUT --> COND
    
    style OUT fill:#f9f9f9,stroke:#333,stroke-width:2px
    style CA fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Workflow Execution Flow**

This diagram shows the complete execution path from trigger events through skill detection and parallel review jobs. The `detect-skills` job produces JSON outputs that drive the `review-skill` job's matrix strategy.

**Sources:** [.github/workflows/claude-skill-review.yml:1-88]()

## Job: detect-skills

The `detect-skills` job is responsible for identifying which skills have been modified in a pull request. It runs on `ubuntu-latest` and produces outputs consumed by the `review-skill` job.

### Outputs

| Output Key | Type | Description |
|------------|------|-------------|
| `skills` | JSON array | List of skill directory paths that have changes |
| `has_skills` | boolean | `"true"` if any skills changed, `"false"` otherwise |

### Execution Steps

1. **Repository Checkout** - Uses `actions/checkout@v4` with `fetch-depth: 0` to access full git history for diff operations
2. **Change Detection** - Runs bash script to identify changed skill directories
3. **Output Generation** - Produces JSON array of affected skills or empty array if none

The detection algorithm uses git diff to compare the PR branch against the base branch, then cross-references changed file paths with directories containing `SKILL.md` files. This ensures only skills with actual modifications are reviewed.

For detailed implementation of the detection algorithm, see [5.1.1](#5.1.1).

**Sources:** [.github/workflows/claude-skill-review.yml:12-53]()

## Job: review-skill

The `review-skill` job executes Claude-powered reviews for each detected skill using a matrix strategy for parallel execution. It only runs when `needs.detect-skills.outputs.has_skills == 'true'`.

### Matrix Strategy Configuration

```yaml
strategy:
  matrix:
    skill: ${{ fromJson(needs.detect-skills.outputs.skills) }}
  fail-fast: false
```

The matrix dynamically expands based on the JSON array from `detect-skills`, creating one parallel job per skill. The `fail-fast: false` setting ensures that if one skill review fails, others continue to completion.

### Required Permissions

| Permission | Scope | Purpose |
|------------|-------|---------|
| `contents` | read | Access repository files and git history |
| `pull-requests` | write | Post review comments on pull requests |
| `issues` | write | Comment on related issues |
| `id-token` | write | OIDC token for authentication |

**Sources:** [.github/workflows/claude-skill-review.yml:55-67]()

## Claude Code Integration

The workflow integrates with Claude through the `anthropics/claude-code-action@v1` GitHub Action, configured with specific plugins and tools for skill review.

### Action Configuration Diagram

```mermaid
graph LR
    subgraph "claude-code-action@v1"
        AUTH["claude_code_oauth_token<br/>(from secrets)"]
        MKT["plugin_marketplaces:<br/>github.com/anthropics/skills.git"]
        PLUG["plugins:<br/>example-skills@anthropic-agent-skills"]
        TOOLS["allowedTools:<br/>Bash(gh pr comment),<br/>Bash(git),<br/>Read, Glob, Grep, Skill"]
        PROMPT["prompt:<br/>Use skill-creator skill<br/>to review $skill"]
    end
    
    AUTH --> MKT
    MKT --> PLUG
    PLUG --> TOOLS
    TOOLS --> PROMPT
    
    style PROMPT fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Claude Code Action Configuration Components**

**Sources:** [.github/workflows/claude-skill-review.yml:75-87]()

### Configuration Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `claude_code_oauth_token` | `${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}` | OAuth authentication for Claude Code service |
| `plugin_marketplaces` | `https://github.com/anthropics/skills.git` | Plugin source repository |
| `plugins` | `example-skills@anthropic-agent-skills` | Specific skill-creator plugin to load |
| `claude_args` | Tool allowlist | Restricts Claude to specific tool usage |
| `prompt` | Multi-line template | Instructions for reviewing the skill |

**Sources:** [.github/workflows/claude-skill-review.yml:77-87]()

## Allowed Tools

The workflow restricts Claude to a specific set of tools to ensure reviews are safe and focused:

| Tool Category | Specific Tool | Purpose |
|---------------|---------------|---------|
| Bash (restricted) | `gh pr comment:*` | Post review feedback as PR comments |
| Bash (restricted) | `git:*` | Execute git commands for diff inspection |
| File Operations | `Read` | Read skill files |
| File Operations | `Glob` | Pattern-based file discovery |
| File Operations | `Grep` | Search file contents |
| Skill Execution | `Skill` | Execute the skill-creator skill |

The bash tool is restricted to only `gh` and `git` commands, preventing arbitrary command execution. This security model ensures the review process cannot modify repository state or execute untrusted code.

**Sources:** [.github/workflows/claude-skill-review.yml:81]()

## Review Process

The review process follows a structured prompt that guides Claude through skill evaluation:

### Review Instructions

The prompt template instantiated for each skill:

```
Use the skill-creator skill to review the **{skill_name}** skill in PR #{pr_number}.

Use `git diff origin/{base_ref} -- {skill_path}/` to see what changed. 
If this is a new skill, provide a full review. 
If it's changes to an existing skill, focus on the changes.

Post your feedback as a comment using `gh pr comment`. Use the skill title in the header.
```

### Execution Flow

```mermaid
sequenceDiagram
    participant GHA as "GitHub Actions"
    participant CA as "claude-code-action@v1"
    participant Claude as "Claude (with skill-creator)"
    participant Git as "Git Commands"
    participant GH as "GitHub API"
    
    GHA->>CA: Start with matrix.skill
    CA->>Claude: Load skill-creator plugin
    Claude->>Git: git diff origin/base -- skill/
    Git-->>Claude: Changed files and hunks
    Claude->>Claude: Execute skill-creator skill
    Claude->>Claude: Analyze SKILL.md, references, scripts
    Claude->>GH: gh pr comment (post feedback)
    GH-->>CA: Comment created
    CA-->>GHA: Job complete
```

**Skill Review Sequence**

This sequence diagram shows the interaction between GitHub Actions, the Claude Code action, and external tools during skill review.

**Sources:** [.github/workflows/claude-skill-review.yml:82-87]()

## Skill-Creator Plugin

The workflow loads the `skill-creator` skill from the `example-skills@anthropic-agent-skills` marketplace. This skill specializes in:

- **SKILL.md Validation** - Checking format, completeness, and clarity of skill documentation
- **Reference Material Review** - Evaluating supporting documentation in the `references/` directory
- **Script Analysis** - Reviewing Python scripts or other executable components
- **Waypoint Structure** - Validating multi-step workflow architectures (for skills like Clinical Trial Protocol)
- **Dependency Verification** - Ensuring MCP server references are valid and properly configured
- **Best Practice Compliance** - Comparing against established patterns from other skills

The plugin provides domain-specific expertise beyond general code review, focusing on healthcare skill quality criteria.

**Sources:** [.github/workflows/claude-skill-review.yml:79-80]()

## New vs. Modified Skills

The review process adapts based on whether a skill is new or being modified:

### New Skill Review

For skills where `SKILL.md` did not exist in the base branch:
- **Full Documentation Review** - Complete evaluation of SKILL.md structure and content
- **Reference Completeness** - Verification that all necessary reference materials are included
- **Example Validation** - Ensuring examples are correct and useful
- **Marketplace Integration** - Checking that marketplace.json registration is correct

### Modified Skill Review

For existing skills with changes:
- **Diff-Focused Analysis** - Reviewing only the changed sections and their implications
- **Backward Compatibility** - Ensuring changes don't break existing workflows
- **Documentation Sync** - Verifying that code changes are reflected in documentation
- **Regression Prevention** - Identifying potential issues introduced by modifications

The prompt explicitly instructs Claude to "focus on the changes" for existing skills, ensuring efficient reviews that don't redundantly check unchanged portions.

**Sources:** [.github/workflows/claude-skill-review.yml:85-86]()

## Feedback Delivery

Review feedback is delivered as GitHub pull request comments using the `gh pr comment` command.

### Comment Format

Comments follow a structured format:
- **Header** - Includes the skill title for easy identification
- **Summary** - High-level assessment of the skill quality
- **Detailed Feedback** - Specific issues, suggestions, and recommendations
- **Action Items** - Clear next steps for the PR author

### Example Comment Structure

```
## Review: clinical-trial-protocol-skill

**Summary**: The skill follows the waypoint architecture correctly, but needs 
improvements in error handling and documentation clarity.

**Detailed Feedback**:
- ✅ SKILL.md structure is complete
- ⚠️ Step 3 waypoint missing error handling for invalid ClinicalTrials.gov IDs
- ⚠️ sample_size_calculator.py lacks input validation
- ✅ Reference materials are comprehensive

**Recommendations**:
1. Add try-catch blocks in Step 3 for API failures
2. Validate calculator inputs (alpha, power, effect_size ranges)
3. Update SKILL.md to document error scenarios
```

**Sources:** [.github/workflows/claude-skill-review.yml:87]()

## Parallelization and Performance

The matrix strategy enables efficient parallel execution when multiple skills are modified:

### Parallelization Diagram

```mermaid
graph TB
    DS["detect-skills<br/>Output: [skill-a, skill-b, skill-c]"]
    
    subgraph "Parallel Matrix Jobs"
        RS1["review-skill<br/>matrix.skill = skill-a"]
        RS2["review-skill<br/>matrix.skill = skill-b"]
        RS3["review-skill<br/>matrix.skill = skill-c"]
    end
    
    DS --> RS1
    DS --> RS2
    DS --> RS3
    
    RS1 --> C1["Comment on PR<br/>(skill-a feedback)"]
    RS2 --> C2["Comment on PR<br/>(skill-b feedback)"]
    RS3 --> C3["Comment on PR<br/>(skill-c feedback)"]
```

**Matrix Strategy Parallelization**

When a pull request modifies multiple skills, GitHub Actions spawns concurrent jobs, each reviewing a single skill. This approach:

- **Reduces Latency** - Total review time is dominated by the slowest skill review, not the sum of all reviews
- **Isolates Failures** - `fail-fast: false` ensures one failing review doesn't block others
- **Scales Linearly** - Adding more skills to a PR doesn't proportionally increase review time

For a detailed explanation of the matrix strategy implementation, see [5.1.2](#5.1.2).

**Sources:** [.github/workflows/claude-skill-review.yml:59-62]()

## Workflow Dependencies

The `review-skill` job explicitly depends on `detect-skills` using the `needs` keyword:

```yaml
review-skill:
  needs: detect-skills
  if: needs.detect-skills.outputs.has_skills == 'true'
```

This dependency ensures:
1. **Sequential Execution** - `detect-skills` completes before any `review-skill` jobs start
2. **Conditional Execution** - Review jobs only run when skills are detected
3. **Data Flow** - Outputs from `detect-skills` are available to `review-skill`

If no skills are detected (`has_skills == 'false'`), the entire `review-skill` job is skipped, preventing unnecessary resource consumption.

**Sources:** [.github/workflows/claude-skill-review.yml:56-57]()

## Reusable Workflow Pattern

The workflow supports the `workflow_call` trigger, enabling it to be called from other workflows:

```yaml
on:
  workflow_call:
    secrets:
      CLAUDE_CODE_OAUTH_TOKEN:
        required: true
```

This allows other CI/CD workflows to programmatically trigger skill reviews as part of larger automation pipelines. The calling workflow must provide the `CLAUDE_CODE_OAUTH_TOKEN` secret.

**Example usage in calling workflow:**

```yaml
jobs:
  run-skill-review:
    uses: ./.github/workflows/claude-skill-review.yml
    secrets:
      CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
```

**Sources:** [.github/workflows/claude-skill-review.yml:6-9]()

## Error Handling

The workflow implements several error handling strategies:

| Scenario | Handling Strategy |
|----------|-------------------|
| No skills detected | Skip `review-skill` job entirely (conditional execution) |
| Git diff fails | Job fails, PR shows failed check |
| Claude Code API unavailable | Job fails, can be manually rerun |
| Single skill review fails | Other skills continue due to `fail-fast: false` |
| Comment posting fails | Job fails, but review analysis completes |

The workflow does not include explicit retry logic; failures are surfaced to developers through GitHub's standard check status UI.

**Sources:** [.github/workflows/claude-skill-review.yml:55-88]()

## Integration with Development Lifecycle

The skill review workflow integrates into the pull request lifecycle as shown:

```mermaid
stateDiagram-v2
    [*] --> PR_Opened
    PR_Opened --> Workflow_Triggered
    
    state Workflow_Triggered {
        [*] --> detect_skills
        detect_skills --> review_skill: has_skills=true
        detect_skills --> [*]: has_skills=false
        
        state review_skill {
            [*] --> Matrix_Spawn
            Matrix_Spawn --> Parallel_Reviews
            Parallel_Reviews --> Post_Comments
            Post_Comments --> [*]
        }
    }
    
    Workflow_Triggered --> PR_Updated: New commits pushed
    PR_Updated --> Workflow_Triggered: Re-run workflow
    
    Workflow_Triggered --> Human_Review: Comments posted
    Human_Review --> Approval: LGTM
    Human_Review --> Revision: Changes requested
    Revision --> PR_Updated
    
    Approval --> [*]
```

**Skill Review in PR Lifecycle**

The workflow creates a feedback loop between automated AI review and human judgment, ensuring skill quality before merge.

**Sources:** [.github/workflows/claude-skill-review.yml:1-88]()

## Summary

The skill review workflow provides automated quality assurance for healthcare skills through:

- **Two-stage pipeline** - Detection followed by targeted review
- **Parallel execution** - Matrix strategy for multiple skills
- **AI-powered analysis** - Claude with skill-creator plugin
- **Structured feedback** - GitHub PR comments with actionable recommendations
- **Security controls** - Restricted tool access and permission scoping
- **Efficient triggering** - Only runs on relevant PR events

This workflow is the primary quality gate preventing defective skills from reaching production, with an importance score of 49.07 reflecting its critical role in the healthcare marketplace ecosystem.

**Sources:** [.github/workflows/claude-skill-review.yml:1-88]()

---

# Page: Skill Detection Algorithm

# Skill Detection Algorithm

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/claude-skill-review.yml](.github/workflows/claude-skill-review.yml)

</details>



## Purpose and Scope

This document details the **detect-skills** job implementation in the Claude Skill Review workflow, which identifies which skills have been modified in a pull request. The algorithm uses git diff analysis combined with SKILL.md file discovery to produce a filtered list of affected skills for review.

For information about how the detected skills are reviewed in parallel, see [Matrix Review Strategy](#5.1.2). For the overall skill review workflow architecture, see [Skill Review Workflow](#5.1).

---

## Overview

The `detect-skills` job serves as a **filtering stage** in the skill review pipeline. It prevents unnecessary reviews by identifying only the skills that have changed in a pull request, enabling the downstream `review-skill` job to execute reviews in parallel only for affected skills.

**Key Responsibilities:**
- Identify all skill directories in the repository
- Determine which files changed in the PR
- Match changed files to skill directories
- Output a JSON array of affected skill paths
- Set a boolean flag indicating whether any skills were affected

The job runs on every pull request event ([.github/workflows/claude-skill-review.yml:3-5]()) and produces outputs consumed by the matrix review job.

Sources: [.github/workflows/claude-skill-review.yml:12-53]()

---

## Detection Algorithm Flow

The detection algorithm executes in three sequential phases: **changed file identification**, **skill directory discovery**, and **intersection matching**. The following diagram illustrates the complete detection flow:

### Algorithm Execution Flow

```mermaid
flowchart TD
    Start["detect-skills Job Starts"]
    Checkout["Checkout repository<br/>actions/checkout@v4<br/>fetch-depth: 0"]
    
    Phase1["Phase 1: Get Changed Files"]
    GitDiff["git diff --name-only<br/>origin/$base_ref...HEAD"]
    ChangedFiles["changed_files variable<br/>(newline-separated list)"]
    
    Phase2["Phase 2: Find All Skills"]
    FindSkill["find . -name SKILL.md -type f"]
    ExtractDir["xargs dirname<br/>sed 's|^./||'"]
    SkillDirs["skill_dirs variable<br/>(list of paths)"]
    
    Phase3["Phase 3: Match Skills to Changes"]
    LoopSkills["for skill_dir in skill_dirs"]
    LoopFiles["for file in changed_files"]
    CheckMatch{"Does file path<br/>start with skill_dir/?"}
    AddSkill["affected_skills+=skill_dir<br/>break inner loop"]
    
    Phase4["Phase 4: Format Output"]
    CheckEmpty{"affected_skills<br/>array empty?"}
    EmptyOutput["skills=[]<br/>has_skills=false"]
    FormatJSON["sort -u | jq -R -s -c<br/>'split(\n) | map(select(length > 0))'"]
    PopulatedOutput["skills=JSON_ARRAY<br/>has_skills=true"]
    
    WriteOutput["Write to GITHUB_OUTPUT"]
    End["Job Complete<br/>Outputs Available"]
    
    Start --> Checkout
    Checkout --> Phase1
    Phase1 --> GitDiff
    GitDiff --> ChangedFiles
    ChangedFiles --> Phase2
    
    Phase2 --> FindSkill
    FindSkill --> ExtractDir
    ExtractDir --> SkillDirs
    SkillDirs --> Phase3
    
    Phase3 --> LoopSkills
    LoopSkills --> LoopFiles
    LoopFiles --> CheckMatch
    CheckMatch -->|"Yes: file matches skill_dir/*"| AddSkill
    CheckMatch -->|"No"| LoopFiles
    AddSkill --> LoopSkills
    LoopSkills -->|"All skills checked"| Phase4
    
    Phase4 --> CheckEmpty
    CheckEmpty -->|"Yes"| EmptyOutput
    CheckEmpty -->|"No"| FormatJSON
    FormatJSON --> PopulatedOutput
    
    EmptyOutput --> WriteOutput
    PopulatedOutput --> WriteOutput
    WriteOutput --> End
```

Sources: [.github/workflows/claude-skill-review.yml:23-53]()

---

## Phase 1: Changed File Identification

The algorithm begins by identifying all files modified in the pull request using `git diff`:

```bash
git diff --name-only origin/${{ github.base_ref }}...HEAD
```

**Key Parameters:**
- `--name-only`: Returns only file paths, not diff content
- `origin/${{ github.base_ref }}`: The target branch (typically `main`)
- `...HEAD`: Three-dot notation compares the merge base to the PR branch head
- Result stored in `changed_files` variable

This command produces a newline-separated list of file paths relative to the repository root, such as:

```
clinical-trial-protocol-skill/SKILL.md
clinical-trial-protocol-skill/scripts/sample_size_calculator.py
prior-auth-review-skill/assets/template.md
```

Sources: [.github/workflows/claude-skill-review.yml:26-27]()

---

## Phase 2: Skill Directory Discovery

The algorithm identifies all valid skill directories by locating `SKILL.md` files:

```bash
find . -name "SKILL.md" -type f | xargs -I {} dirname {} | sed 's|^\./||'
```

**Pipeline Breakdown:**

| Command | Purpose | Example Output |
|---------|---------|---------------|
| `find . -name "SKILL.md" -type f` | Locate all SKILL.md files recursively | `./clinical-trial-protocol-skill/SKILL.md` |
| `xargs -I {} dirname {}` | Extract parent directory of each file | `./clinical-trial-protocol-skill` |
| `sed 's\|^\./\|\|'` | Remove leading `./` prefix | `clinical-trial-protocol-skill` |

The result is stored in the `skill_dirs` variable as a space-separated list of skill directory paths.

**Why SKILL.md?** The presence of a `SKILL.md` file is the authoritative marker that a directory contains a skill definition. This convention ensures the algorithm only processes valid skills, not arbitrary directories.

Sources: [.github/workflows/claude-skill-review.yml:29-30]()

---

## Phase 3: Intersection Matching

The algorithm uses nested loops to match changed files against skill directories:

```bash
affected_skills=()
for skill_dir in $skill_dirs; do
  for file in $changed_files; do
    if [[ "$file" == "$skill_dir/"* ]] || [[ "$file" == "$skill_dir" ]]; then
      affected_skills+=("$skill_dir")
      break
    fi
  done
done
```

**Matching Logic:**

The pattern `[[ "$file" == "$skill_dir/"* ]]` uses bash string matching to check if a changed file path **starts with** the skill directory path followed by a forward slash. This ensures:
- Files directly in the skill directory match (e.g., `clinical-trial-protocol-skill/SKILL.md`)
- Files in subdirectories match (e.g., `clinical-trial-protocol-skill/scripts/calculator.py`)
- Files in sibling directories do not match (e.g., `prior-auth-review-skill/` does not match `clinical-trial-protocol-skill/`)

The alternative condition `[[ "$file" == "$skill_dir" ]]` handles the edge case where the skill directory itself is listed as changed (rare but possible in some git operations).

**Performance Optimization:** The `break` statement exits the inner loop immediately after matching, preventing redundant checks once a skill is identified as affected.

Sources: [.github/workflows/claude-skill-review.yml:32-41]()

---

## Phase 4: Output Formatting

The final phase converts the detected skills into structured outputs for the GitHub Actions workflow:

### Output Generation Logic

```mermaid
flowchart LR
    Input["affected_skills array"]
    Check{"Array length > 0?"}
    
    subgraph "Empty Path"
        Empty1["skills=[]"]
        Empty2["has_skills=false"]
    end
    
    subgraph "Populated Path"
        Sort["printf + sort -u<br/>(remove duplicates)"]
        JQ["jq -R -s -c<br/>'split(\n) | map(select(length > 0))'"]
        Pop1["skills=JSON_ARRAY"]
        Pop2["has_skills=true"]
    end
    
    Output["Write to GITHUB_OUTPUT"]
    
    Input --> Check
    Check -->|"No (length = 0)"| Empty1
    Empty1 --> Empty2
    Empty2 --> Output
    
    Check -->|"Yes"| Sort
    Sort --> JQ
    JQ --> Pop1
    Pop1 --> Pop2
    Pop2 --> Output
```

### JSON Transformation Pipeline

For non-empty results, the script uses a Unix pipeline to produce valid JSON:

```bash
unique_skills=$(printf '%s\n' "${affected_skills[@]}" | sort -u | jq -R -s -c 'split("\n") | map(select(length > 0))')
```

**Transformation Steps:**

1. **`printf '%s\n' "${affected_skills[@]}"`**: Expand bash array to newline-separated strings
2. **`sort -u`**: Remove duplicate entries (deduplication)
3. **`jq -R -s -c`**: Read raw strings (`-R`), slurp into single input (`-s`), compact output (`-c`)
4. **`'split("\n") | map(select(length > 0))'`**: Split on newlines, filter empty strings

**Example Output:**
```json
["clinical-trial-protocol-skill","prior-auth-review-skill"]
```

Sources: [.github/workflows/claude-skill-review.yml:44-53]()

---

## Output Schema

The `detect-skills` job produces two outputs defined at [.github/workflows/claude-skill-review.yml:14-16]():

| Output Name | Type | Purpose | Example Value |
|------------|------|---------|---------------|
| `skills` | JSON Array (string) | List of affected skill directory paths | `["clinical-trial-protocol-skill"]` |
| `has_skills` | Boolean (string) | Flag indicating whether any skills were affected | `"true"` or `"false"` |

**GitHub Actions Output Mechanism:**

Outputs are written to the special `$GITHUB_OUTPUT` file using the format:
```bash
echo "skills=$unique_skills" >> $GITHUB_OUTPUT
echo "has_skills=true" >> $GITHUB_OUTPUT
```

These outputs are accessible to downstream jobs via the `needs` context:
```yaml
needs.detect-skills.outputs.skills
needs.detect-skills.outputs.has_skills
```

Sources: [.github/workflows/claude-skill-review.yml:14-16, 46-47, 50-51]()

---

## Integration with Review Job

The `review-skill` job consumes the `detect-skills` outputs to determine execution behavior:

### Conditional Execution and Matrix Strategy

```mermaid
flowchart TD
    DetectJob["detect-skills job<br/>completes"]
    Output["outputs:<br/>skills: JSON array<br/>has_skills: boolean"]
    
    Condition{"has_skills == 'true'?"}
    Skip["review-skill job<br/>skipped<br/>(no skills changed)"]
    
    Matrix["Matrix Strategy<br/>fromJson(needs.detect-skills.outputs.skills)"]
    Parallel["Parallel Jobs Created<br/>(one per skill)"]
    
    Job1["review-skill<br/>matrix.skill = skill-1"]
    Job2["review-skill<br/>matrix.skill = skill-2"]
    JobN["review-skill<br/>matrix.skill = skill-N"]
    
    DetectJob --> Output
    Output --> Condition
    Condition -->|"No"| Skip
    Condition -->|"Yes"| Matrix
    Matrix --> Parallel
    Parallel --> Job1
    Parallel --> Job2
    Parallel --> JobN
```

**Integration Points:**

1. **Conditional Execution** ([.github/workflows/claude-skill-review.yml:57]()):
   ```yaml
   if: needs.detect-skills.outputs.has_skills == 'true'
   ```
   The `review-skill` job only runs if at least one skill was affected.

2. **Matrix Strategy** ([.github/workflows/claude-skill-review.yml:59-61]()):
   ```yaml
   strategy:
     matrix:
       skill: ${{ fromJson(needs.detect-skills.outputs.skills) }}
   ```
   The `skills` JSON array is deserialized using `fromJson()` and used to create a matrix dimension, spawning one review job per skill.

3. **Skill Context** ([.github/workflows/claude-skill-review.yml:83]()):
   ```yaml
   prompt: |
     Use the skill-creator skill to review the **${{ matrix.skill }}** skill...
   ```
   Each matrix job receives a specific `matrix.skill` value (e.g., `clinical-trial-protocol-skill`) used to target the review.

This integration enables efficient, parallel reviews while avoiding unnecessary computation for unchanged skills.

Sources: [.github/workflows/claude-skill-review.yml:55-62, 83]()

---

## Edge Cases and Error Handling

### Empty Skill Changes

When no skills are affected, the algorithm outputs:
```bash
echo "skills=[]" >> $GITHUB_OUTPUT
echo "has_skills=false" >> $GITHUB_OUTPUT
echo "No skill changes detected"
```

This causes the `review-skill` job to be skipped entirely, as shown in the conditional `if: needs.detect-skills.outputs.has_skills == 'true'`.

### New Skill Addition

When a pull request adds a new skill directory:
1. `find . -name "SKILL.md"` discovers the new `SKILL.md` file
2. All files in the new directory match the skill path pattern
3. The new skill appears in the `skills` output
4. A full review is triggered (no previous state exists for diff comparison)

### Duplicate Prevention

The `sort -u` command ensures that even if multiple files in the same skill directory are modified, the skill only appears once in the output array. This prevents duplicate review jobs from being spawned.

### Repository Depth

The `fetch-depth: 0` parameter ([.github/workflows/claude-skill-review.yml:21]()) ensures the full git history is fetched, allowing `git diff` to accurately compare against the base branch even for deep commit histories.

Sources: [.github/workflows/claude-skill-review.yml:18-21, 44-53]()

---

## Performance Characteristics

| Metric | Complexity | Notes |
|--------|-----------|-------|
| **Time Complexity** | O(S × F) | S = number of skills, F = number of changed files |
| **Space Complexity** | O(S + F) | Storage for skill list and changed files list |
| **Worst Case** | All skills modified | Still completes in <5 seconds for typical repos |
| **Best Case** | No skills modified | Job completes immediately, downstream reviews skipped |

The nested loop approach is acceptable because:
- Healthcare marketplace has a small number of skills (currently 3)
- PRs typically modify a limited number of files (<50)
- Early `break` statement optimizes the common case

For repositories with hundreds of skills, alternative approaches (e.g., hash-based matching) might be necessary.

Sources: [.github/workflows/claude-skill-review.yml:32-41]()

---

# Page: Matrix Review Strategy

# Matrix Review Strategy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/claude-skill-review.yml](.github/workflows/claude-skill-review.yml)

</details>



## Purpose and Scope

This document explains how the `review-skill` job in the Claude Skill Review workflow uses GitHub Actions matrix strategy to parallelize skill reviews across multiple changed skills. For information about how skills are detected before the matrix strategy runs, see [Skill Detection Algorithm](#5.1.1). For the overall workflow architecture, see [Skill Review Workflow](#5.1).

The matrix strategy enables the workflow to review multiple skills concurrently, scaling from zero to many skill reviews based on what changed in a pull request. Each skill receives an independent Claude-powered review posted as a separate PR comment.

---

## Matrix Strategy Configuration

The `review-skill` job uses GitHub Actions' matrix strategy to dynamically create parallel jobs for each detected skill:

```yaml
strategy:
  matrix:
    skill: ${{ fromJson(needs.detect-skills.outputs.skills) }}
  fail-fast: false
```

**Sources:** [.github/workflows/claude-skill-review.yml:59-62]()

### Dynamic Matrix Population

The matrix is populated from the `detect-skills` job output using the `fromJson()` function:

| Component | Value | Purpose |
|-----------|-------|---------|
| `needs.detect-skills.outputs.skills` | JSON array (e.g., `["clinical-trial-protocol-skill", "prior-auth-review-skill"]`) | List of skill directories with changes |
| `fromJson()` | GitHub Actions function | Converts JSON string to array for matrix expansion |
| `matrix.skill` | Individual skill path | Available as a variable in each matrix job |

The matrix strategy creates one job instance per skill in the array. If the `skills` output is `["skill-a", "skill-b", "skill-c"]`, GitHub Actions spawns three parallel `review-skill` jobs with `matrix.skill` set to `skill-a`, `skill-b`, and `skill-c` respectively.

**Sources:** [.github/workflows/claude-skill-review.yml:60-61]()

### Fail-Fast Disabled

The `fail-fast: false` configuration ensures that all skill reviews complete even if one fails:

```mermaid
graph LR
    M["matrix expansion"] --> J1["review-skill<br/>(skill-a)"]
    M --> J2["review-skill<br/>(skill-b)"]
    M --> J3["review-skill<br/>(skill-c)"]
    
    J1 --> F1["✓ Success"]
    J2 --> F2["✗ Failure"]
    J3 --> F3["✓ Success"]
    
    F2 -.->|"does NOT cancel"| J1
    F2 -.->|"does NOT cancel"| J3
```

**Diagram: Independent Job Execution with fail-fast: false**

Without `fail-fast: false`, a failure in one skill review would cancel all other in-progress reviews. This configuration allows developers to receive feedback on all changed skills, even if one skill has issues.

**Sources:** [.github/workflows/claude-skill-review.yml:62]()

---

## Matrix Expansion and Job Execution

### Job Conditional Logic

The `review-skill` job only runs when skills are detected:

```yaml
review-skill:
  needs: detect-skills
  if: needs.detect-skills.outputs.has_skills == 'true'
```

**Sources:** [.github/workflows/claude-skill-review.yml:55-57]()

This creates a dependency chain:

```mermaid
stateDiagram-v2
    [*] --> detect_skills
    
    state detect_skills {
        [*] --> scan_changes: "git diff + SKILL.md discovery"
        scan_changes --> set_outputs: "outputs.skills = JSON array<br/>outputs.has_skills = true/false"
    }
    
    detect_skills --> check_condition: "needs.detect-skills"
    
    state check_condition <<choice>>
    check_condition --> skip_review: "has_skills == 'false'"
    check_condition --> matrix_expansion: "has_skills == 'true'"
    
    state matrix_expansion {
        [*] --> fromJson: "Parse outputs.skills"
        fromJson --> spawn_jobs: "Create N parallel jobs"
    }
    
    matrix_expansion --> review_skill_instances
    
    state review_skill_instances {
        parallel_1: "review-skill (matrix.skill = skill-a)"
        parallel_2: "review-skill (matrix.skill = skill-b)"
        parallel_3: "review-skill (matrix.skill = skill-c)"
    }
    
    review_skill_instances --> [*]
    skip_review --> [*]
```

**Diagram: Conditional Matrix Execution Flow**

**Sources:** [.github/workflows/claude-skill-review.yml:55-57]()

### Concrete Execution Example

Consider a pull request that modifies three files:
- `clinical-trial-protocol-skill/SKILL.md`
- `prior-auth-review-skill/assets/template.md`
- `README.md`

The execution proceeds as follows:

| Step | Job | Action | Output |
|------|-----|--------|--------|
| 1 | `detect-skills` | Runs git diff, finds SKILL.md files | `skills = ["clinical-trial-protocol-skill", "prior-auth-review-skill"]`<br/>`has_skills = "true"` |
| 2 | Matrix expansion | Parses JSON array | Creates 2 job instances |
| 3a | `review-skill` (matrix.skill = clinical-trial-protocol-skill) | Runs Claude review | Posts PR comment for clinical trial skill |
| 3b | `review-skill` (matrix.skill = prior-auth-review-skill) | Runs Claude review | Posts PR comment for prior auth skill |

Steps 3a and 3b execute in parallel. The `README.md` change does not trigger a skill review.

**Sources:** [.github/workflows/claude-skill-review.yml:23-53]()

---

## Claude Code Action Integration

Each matrix job invokes the `anthropics/claude-code-action@v1` with skill-specific parameters:

```mermaid
graph TB
    subgraph "Matrix Job Instance (matrix.skill = 'prior-auth-review-skill')"
        checkout["actions/checkout@v4<br/>fetch-depth: 0"]
        action["anthropics/claude-code-action@v1"]
        
        checkout --> action
    end
    
    subgraph "Action Configuration"
        token["claude_code_oauth_token:<br/>CLAUDE_CODE_OAUTH_TOKEN secret"]
        marketplace["plugin_marketplaces:<br/>'https://github.com/anthropics/skills.git'"]
        plugins["plugins:<br/>'example-skills@anthropic-agent-skills'"]
        args["claude_args:<br/>'--allowedTools Bash(gh pr comment:*),Bash(git:*),Read,Glob,Grep,Skill'"]
        prompt["prompt:<br/>Use skill-creator to review ${{ matrix.skill }}"]
        
        action --> token
        action --> marketplace
        action --> plugins
        action --> args
        action --> prompt
    end
    
    subgraph "Claude Execution"
        load_plugin["Load skill-creator plugin<br/>from example-skills marketplace"]
        run_git_diff["Execute: git diff origin/main -- prior-auth-review-skill/"]
        analyze["Claude analyzes changes<br/>using skill-creator"]
        post_comment["Execute: gh pr comment<br/>Posts review feedback"]
        
        prompt --> load_plugin
        load_plugin --> run_git_diff
        run_git_diff --> analyze
        analyze --> post_comment
    end
```

**Diagram: Claude Code Action Execution Flow per Matrix Job**

**Sources:** [.github/workflows/claude-skill-review.yml:70-87]()

### Action Parameters

The action is configured with the following parameters:

```yaml
- name: Run Claude Skill Review
  uses: anthropics/claude-code-action@v1
  with:
    claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    plugin_marketplaces: 'https://github.com/anthropics/skills.git'
    plugins: 'example-skills@anthropic-agent-skills'
    claude_args: '--allowedTools "Bash(gh pr comment:*),Bash(git:*),Read,Glob,Grep,Skill"'
    prompt: |
      Use the skill-creator skill to review the **${{ matrix.skill }}** skill in PR #${{ github.event.pull_request.number }}.
      
      Use `git diff origin/${{ github.base_ref }} -- ${{ matrix.skill }}/` to see what changed.
      If this is a new skill, provide a full review. If it's changes to an existing skill, focus on the changes.
      
      Post your feedback as a comment using `gh pr comment`. Use the skill title in the header.
```

**Sources:** [.github/workflows/claude-skill-review.yml:75-87]()

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `claude_code_oauth_token` | `${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}` | Authenticates with Claude API |
| `plugin_marketplaces` | `https://github.com/anthropics/skills.git` | Loads the anthropic-agent-skills marketplace |
| `plugins` | `example-skills@anthropic-agent-skills` | Installs the skill-creator skill |
| `claude_args` | `--allowedTools "Bash(gh pr comment:*),Bash(git:*),Read,Glob,Grep,Skill"` | Grants Claude permission to run git, gh CLI, file operations, and skills |
| `prompt` | Dynamic prompt with `${{ matrix.skill }}` | Instructs Claude to review the specific skill |

### Prompt Template Substitution

The prompt template uses GitHub Actions context variables to customize each matrix job:

- `${{ matrix.skill }}`: Replaced with the skill directory (e.g., `clinical-trial-protocol-skill`)
- `${{ github.event.pull_request.number }}`: The PR number being reviewed
- `${{ github.base_ref }}`: The base branch (typically `main`)

For a matrix job reviewing `prior-auth-review-skill` in PR #42 against the `main` branch, the prompt becomes:

```
Use the skill-creator skill to review the **prior-auth-review-skill** skill in PR #42.

Use `git diff origin/main -- prior-auth-review-skill/` to see what changed.
If this is a new skill, provide a full review. If it's changes to an existing skill, focus on the changes.

Post your feedback as a comment using `gh pr comment`. Use the skill title in the header.
```

**Sources:** [.github/workflows/claude-skill-review.yml:82-87]()

---

## Permissions and Security

The `review-skill` job requires specific GitHub permissions to interact with the repository and pull request:

```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write
  id-token: write
```

**Sources:** [.github/workflows/claude-skill-review.yml:63-67]()

| Permission | Scope | Usage |
|------------|-------|-------|
| `contents: read` | Repository files | Checkout code, read SKILL.md files, run git diff |
| `pull-requests: write` | PR comments | Post skill review feedback via `gh pr comment` |
| `issues: write` | Issue comments | Required for PR commenting (PRs are a type of issue) |
| `id-token: write` | OIDC tokens | Enable GitHub Actions OIDC authentication if needed by the action |

### Security Boundary

The `claude_args` parameter restricts which tools Claude can invoke:

```
--allowedTools "Bash(gh pr comment:*),Bash(git:*),Read,Glob,Grep,Skill"
```

This whitelist ensures Claude can only:
- Run `gh pr comment` commands (post PR comments)
- Run `git` commands (analyze changes)
- Read files (`Read`, `Glob`, `Grep`)
- Use skills (`Skill`)

Claude cannot execute arbitrary bash commands, modify files, or push commits.

**Sources:** [.github/workflows/claude-skill-review.yml:81]()

---

## Parallel Review Timeline

When multiple skills change in a single PR, the matrix strategy significantly reduces review time:

```mermaid
gantt
    title Review Timeline Comparison
    dateFormat YYYY-MM-DD HH:mm
    axisFormat %H:%M
    
    section Sequential (without matrix)
    detect-skills           :done, detect1, 2024-01-01 00:00, 30s
    review skill-a          :done, review1a, after detect1, 2m
    review skill-b          :done, review1b, after review1a, 2m
    review skill-c          :done, review1c, after review1b, 2m
    
    section Parallel (with matrix)
    detect-skills           :done, detect2, 2024-01-01 00:10, 30s
    review skill-a (parallel) :done, review2a, after detect2, 2m
    review skill-b (parallel) :done, review2b, after detect2, 2m
    review skill-c (parallel) :done, review2c, after detect2, 2m
```

**Diagram: Sequential vs Parallel Review Timeline**

In this example:
- **Sequential approach**: 6 minutes 30 seconds total (detect + 3 × 2-minute reviews)
- **Matrix approach**: 2 minutes 30 seconds total (detect + 2-minute longest review)

The actual time savings depend on the number of skills and GitHub Actions runner availability.

**Sources:** [.github/workflows/claude-skill-review.yml:59-62]()

---

## Matrix Strategy Code Reference

The complete matrix strategy configuration appears in the workflow file:

```yaml
review-skill:
  needs: detect-skills
  if: needs.detect-skills.outputs.has_skills == 'true'
  runs-on: ubuntu-latest
  strategy:
    matrix:
      skill: ${{ fromJson(needs.detect-skills.outputs.skills) }}
    fail-fast: false
  permissions:
    contents: read
    pull-requests: write
    issues: write
    id-token: write
  
  steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      with:
        fetch-depth: 0
    
    - name: Run Claude Skill Review
      uses: anthropics/claude-code-action@v1
      with:
        claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
        plugin_marketplaces: 'https://github.com/anthropics/skills.git'
        plugins: 'example-skills@anthropic-agent-skills'
        claude_args: '--allowedTools "Bash(gh pr comment:*),Bash(git:*),Read,Glob,Grep,Skill"'
        prompt: |
          Use the skill-creator skill to review the **${{ matrix.skill }}** skill in PR #${{ github.event.pull_request.number }}.
          
          Use `git diff origin/${{ github.base_ref }} -- ${{ matrix.skill }}/` to see what changed.
          If this is a new skill, provide a full review. If it's changes to an existing skill, focus on the changes.
          
          Post your feedback as a comment using `gh pr comment`. Use the skill title in the header.
```

**Sources:** [.github/workflows/claude-skill-review.yml:55-88]()

---

## Summary

The matrix review strategy enables scalable, parallel skill reviews:

1. **Dynamic Matrix**: Populated from `detect-skills` job output via `fromJson()`
2. **Parallel Execution**: Each skill reviewed independently in a separate job
3. **Fail-Safe**: `fail-fast: false` ensures all reviews complete
4. **Scoped Reviews**: Each matrix job receives a skill-specific prompt using `matrix.skill`
5. **Security**: Restricted permissions and tool allowlist prevent unauthorized actions

This architecture allows the workflow to scale from zero to many skill reviews without manual configuration, providing automated quality feedback for every skill change.

**Sources:** [.github/workflows/claude-skill-review.yml:55-88]()

---

# Page: Code Review Workflow

# Code Review Workflow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/claude-code-review.yml](.github/workflows/claude-code-review.yml)
- [.github/workflows/claude.yml](.github/workflows/claude.yml)

</details>



## Purpose and Scope

This document describes the code review automation system implemented via GitHub Actions workflows. The system provides two complementary approaches to Claude-powered code reviews:

1. **Automatic reviews** triggered by pull request events
2. **On-demand reviews** triggered by `@claude` mentions in comments

For skill-specific reviews that validate healthcare skill changes, see [Skill Review Workflow](#5.1). For packaging and releasing skills, see [Release Workflow](#5.3).

**Sources:** [.github/workflows/claude-code-review.yml:1-45](), [.github/workflows/claude.yml:1-51]()

---

## Workflow Architecture

The code review system consists of two independent GitHub Actions workflows that both leverage the `anthropics/claude-code-action` but serve different purposes and have different triggers.

### Code Review Workflow Comparison

| Aspect | `claude-code-review.yml` | `claude.yml` |
|--------|-------------------------|--------------|
| **Trigger** | PR lifecycle events (opened, synchronized, reopened, ready_for_review) | `@claude` mentions in comments/reviews |
| **Scope** | Automatic code review for all PRs | General-purpose Claude assistant |
| **Plugin** | `code-review@claude-code-plugins` | None (uses comment instructions) |
| **Prompt** | Fixed: `/code-review:code-review` | Dynamic: extracted from comment |
| **Primary Use** | Automated quality assurance | Ad-hoc developer assistance |
| **Importance** | 1.62 | 1.56 |

**Sources:** [.github/workflows/claude-code-review.yml:3-12](), [.github/workflows/claude.yml:3-19]()

---

## Automatic Code Review Workflow

The `claude-code-review.yml` workflow provides automated code review on every pull request update.

### Workflow Trigger Diagram

```mermaid
graph TD
    subgraph "GitHub Events"
        PR_OPEN["Pull Request Opened"]
        PR_SYNC["Pull Request Synchronized<br/>(new commits pushed)"]
        PR_READY["Pull Request Ready for Review<br/>(draft -> ready)"]
        PR_REOPEN["Pull Request Reopened"]
    end
    
    subgraph "GitHub Actions"
        TRIGGER["Workflow Trigger:<br/>claude-code-review.yml"]
        CHECKOUT["Checkout Repository<br/>actions/checkout@v4<br/>fetch-depth: 1"]
        CLAUDE["Claude Code Review Job<br/>anthropics/claude-code-action@v1"]
    end
    
    subgraph "Claude Code Service"
        MARKETPLACE["Load Plugin Marketplace:<br/>github.com/anthropics/claude-code.git"]
        PLUGIN["Load Plugin:<br/>code-review@claude-code-plugins"]
        EXECUTE["Execute Prompt:<br/>/code-review:code-review"]
    end
    
    subgraph "GitHub Output"
        COMMENT["Post Review Comment<br/>to PR"]
    end
    
    PR_OPEN --> TRIGGER
    PR_SYNC --> TRIGGER
    PR_READY --> TRIGGER
    PR_REOPEN --> TRIGGER
    
    TRIGGER --> CHECKOUT
    CHECKOUT --> CLAUDE
    
    CLAUDE --> MARKETPLACE
    MARKETPLACE --> PLUGIN
    PLUGIN --> EXECUTE
    
    EXECUTE --> COMMENT
```

**Sources:** [.github/workflows/claude-code-review.yml:3-12](), [.github/workflows/claude-code-review.yml:28-43]()

### Job Configuration

The `claude-review` job runs on `ubuntu-latest` with specific permissions required for accessing repository contents and posting comments.

#### Required Permissions

```yaml
permissions:
  contents: read        # Read repository files
  pull-requests: read   # Read PR metadata
  issues: read          # Read issue metadata (PRs are issues)
  id-token: write       # OIDC authentication with Claude Code
```

**Sources:** [.github/workflows/claude-code-review.yml:21-26]()

#### Step Breakdown

| Step | Action | Configuration | Purpose |
|------|--------|---------------|---------|
| `Checkout repository` | `actions/checkout@v4` | `fetch-depth: 1` | Shallow clone for performance |
| `Run Claude Code Review` | `anthropics/claude-code-action@v1` | Multiple parameters | Execute code review |

**Sources:** [.github/workflows/claude-code-review.yml:28-43]()

### Claude Code Action Parameters

The workflow configures the `claude-code-action` with the following parameters:

```yaml
claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
plugin_marketplaces: 'https://github.com/anthropics/claude-code.git'
plugins: 'code-review@claude-code-plugins'
prompt: '/code-review:code-review ${{ github.repository }}/pull/${{ github.event.pull_request.number }}'
```

| Parameter | Value | Description |
|-----------|-------|-------------|
| `claude_code_oauth_token` | Secret: `CLAUDE_CODE_OAUTH_TOKEN` | Authentication token for Claude Code service |
| `plugin_marketplaces` | `anthropics/claude-code.git` | Repository containing the code-review plugin |
| `plugins` | `code-review@claude-code-plugins` | Specific plugin identifier to load |
| `prompt` | `/code-review:code-review <PR_URL>` | Command to execute with PR context |

**Sources:** [.github/workflows/claude-code-review.yml:37-43]()

### Optional Filtering Configurations

The workflow includes commented-out configurations for optional filtering:

#### File Path Filtering

```yaml
# Optional: Only run on specific file changes
# paths:
#   - "src/**/*.ts"
#   - "src/**/*.tsx"
#   - "src/**/*.js"
#   - "src/**/*.jsx"
```

When enabled, the workflow only runs if files matching these patterns are changed.

**Sources:** [.github/workflows/claude-code-review.yml:6-11]()

#### PR Author Filtering

```yaml
# Optional: Filter by PR author
# if: |
#   github.event.pull_request.user.login == 'external-contributor' ||
#   github.event.pull_request.user.login == 'new-developer' ||
#   github.event.pull_request.author_association == 'FIRST_TIME_CONTRIBUTOR'
```

When enabled, the workflow only runs for specific authors or first-time contributors.

**Sources:** [.github/workflows/claude-code-review.yml:15-19]()

---

## On-Demand @claude Workflow

The `claude.yml` workflow provides general-purpose Claude assistance triggered by mentioning `@claude` in various GitHub contexts.

### Trigger Event Diagram

```mermaid
graph LR
    subgraph "GitHub Event Sources"
        ISS_COMMENT["Issue Comment<br/>types: created"]
        PR_COMMENT["PR Review Comment<br/>types: created"]
        PR_REVIEW["PR Review<br/>types: submitted"]
        ISSUE_OPEN["Issue Opened/Assigned<br/>types: opened, assigned"]
    end
    
    subgraph "Condition Check"
        CHECK{"Contains<br/>@claude?"}
    end
    
    subgraph "Workflow Execution"
        RUN["Execute claude job"]
    end
    
    ISS_COMMENT --> CHECK
    PR_COMMENT --> CHECK
    PR_REVIEW --> CHECK
    ISSUE_OPEN --> CHECK
    
    CHECK -->|"Yes"| RUN
    CHECK -->|"No"| SKIP["Skip execution"]
```

**Sources:** [.github/workflows/claude.yml:3-19]()

### Event Types and Trigger Conditions

The workflow responds to four different GitHub event types, each with specific trigger conditions:

| Event Type | Types | Trigger Condition | Context |
|------------|-------|-------------------|---------|
| `issue_comment` | `created` | Comment body contains `@claude` | Regular issue or PR comments |
| `pull_request_review_comment` | `created` | Comment body contains `@claude` | PR line-specific comments |
| `pull_request_review` | `submitted` | Review body contains `@claude` | Full PR review submission |
| `issues` | `opened`, `assigned` | Issue body/title contains `@claude` | New issues |

**Sources:** [.github/workflows/claude.yml:4-19]()

### Conditional Execution Logic

The `claude` job only executes when the triggering event contains an `@claude` mention:

```yaml
if: |
  (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
  (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@claude')) ||
  (github.event_name == 'pull_request_review' && contains(github.event.review.body, '@claude')) ||
  (github.event_name == 'issues' && (contains(github.event.issue.body, '@claude') || contains(github.event.issue.title, '@claude')))
```

This multi-condition check ensures the workflow only runs when explicitly invoked by users.

**Sources:** [.github/workflows/claude.yml:15-19]()

### Job Configuration

#### Permissions

The `@claude` workflow requires an additional permission compared to the automatic review workflow:

```yaml
permissions:
  contents: read
  pull-requests: read
  issues: read
  id-token: write
  actions: read    # Required for Claude to read CI results on PRs
```

The `actions: read` permission allows Claude to access CI/CD workflow results, enabling it to provide context-aware assistance based on test failures or build errors.

**Sources:** [.github/workflows/claude.yml:21-26]()

### Claude Code Action Configuration

The `@claude` workflow uses a simpler configuration than the automatic review workflow:

```yaml
claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
additional_permissions: |
  actions: read
```

| Parameter | Value | Description |
|-----------|-------|-------------|
| `claude_code_oauth_token` | Secret: `CLAUDE_CODE_OAUTH_TOKEN` | Authentication token |
| `additional_permissions` | `actions: read` | Grants CI result access |
| `prompt` | (not specified) | Claude uses the comment text as instructions |

The absence of a hardcoded `prompt` parameter allows Claude to dynamically interpret the user's request from the comment body.

**Sources:** [.github/workflows/claude.yml:33-41]()

### Optional Customization

The workflow includes commented examples for custom behavior:

```yaml
# Optional: Give a custom prompt to Claude. If this is not specified, 
# Claude will perform the instructions specified in the comment that tagged it.
# prompt: 'Update the pull request description to include a summary of changes.'

# Optional: Add claude_args to customize behavior and configuration
# claude_args: '--allowed-tools Bash(gh pr:*)'
```

These allow repositories to:
- Override the default comment-based prompt
- Restrict or configure available tools (e.g., limit to specific `gh` commands)

**Sources:** [.github/workflows/claude.yml:43-49]()

---

## Workflow Execution Flow

The following diagram shows the end-to-end execution flow for both workflows:

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant GH as GitHub
    participant WF as Workflow Runner
    participant Action as claude-code-action
    participant Claude as Claude Code Service
    participant PR as Pull Request
    
    Note over Dev,PR: Automatic Review Flow
    Dev->>GH: Create/Update Pull Request
    GH->>WF: Trigger claude-code-review.yml
    WF->>Action: Run with code-review plugin
    Action->>Claude: POST /code-review:code-review <PR_URL>
    Claude->>Claude: Analyze PR diff
    Claude->>Action: Return review feedback
    Action->>PR: Post comment with review
    
    Note over Dev,PR: @claude Mention Flow
    Dev->>GH: Comment "@claude review this function"
    GH->>WF: Trigger claude.yml (if contains @claude)
    WF->>Action: Run with comment text
    Action->>Claude: Execute comment instructions
    Claude->>Claude: Process request with PR context
    Claude->>Action: Return response
    Action->>PR: Post reply comment
```

**Sources:** [.github/workflows/claude-code-review.yml:1-45](), [.github/workflows/claude.yml:1-51]()

---

## Integration with Claude Code Action

Both workflows use the `anthropics/claude-code-action@v1` action, which provides the integration layer between GitHub Actions and the Claude Code service.

### Action Version and Repository

```yaml
uses: anthropics/claude-code-action@v1
```

The action is maintained at `https://github.com/anthropics/claude-code-action` and provides:
- Authentication with Claude Code service via OAuth tokens
- Plugin marketplace loading and management
- Prompt execution and response handling
- GitHub comment posting

**Sources:** [.github/workflows/claude-code-review.yml:36](), [.github/workflows/claude.yml:35]()

### Required Secret Configuration

Both workflows require the `CLAUDE_CODE_OAUTH_TOKEN` secret to be configured in the repository settings:

| Secret Name | Purpose | Where to Obtain |
|-------------|---------|-----------------|
| `CLAUDE_CODE_OAUTH_TOKEN` | Authentication token for Claude Code API | Generated from Claude Code dashboard |

This secret must be added via **Settings > Secrets and variables > Actions > Repository secrets**.

**Sources:** [.github/workflows/claude-code-review.yml:38](), [.github/workflows/claude.yml:37]()

---

## Usage Patterns

### When to Use Automatic Reviews

The `claude-code-review.yml` workflow is most effective for:

- **Consistent quality checks**: Every PR receives the same level of automated review
- **Early feedback**: Developers get feedback immediately upon pushing changes
- **Reduced review burden**: Human reviewers can focus on higher-level concerns
- **Onboarding**: New contributors receive automated guidance

### When to Use @claude Mentions

The `claude.yml` workflow is most effective for:

- **Specific questions**: "Explain the logic in this function"
- **Targeted improvements**: "Suggest performance optimizations for this code"
- **Documentation**: "Write a docstring for this class"
- **Context-aware debugging**: Claude can read CI failures with `actions: read` permission
- **One-off tasks**: "Update the PR description with a summary"

### Combining Both Workflows

The workflows are designed to work together:

1. Automatic review (`claude-code-review.yml`) provides baseline quality checks
2. Developer reviews feedback and makes changes
3. Developer can use `@claude` mentions for specific clarifications or improvements
4. Final human review confirms all concerns are addressed

**Sources:** [.github/workflows/claude-code-review.yml:1-45](), [.github/workflows/claude.yml:1-51]()

---

## Relationship to Skill Review Workflow

While the Code Review Workflow provides general code review capabilities, the [Skill Review Workflow](#5.1) (importance: 49.07) is specifically designed for healthcare skill validation:

| Aspect | Code Review Workflow | Skill Review Workflow |
|--------|---------------------|----------------------|
| **Target** | General code changes | Healthcare skill changes (SKILL.md files) |
| **Detection** | All PR events | Git diff analysis to detect changed skills |
| **Plugin** | `code-review` | `skill-creator` |
| **Execution** | Single job | Matrix strategy (parallel per skill) |
| **Validation** | Code quality | Skill-specific healthcare domain validation |
| **Importance** | 1.62 | 49.07 |

For healthcare-specific skill changes, the Skill Review Workflow provides deeper domain validation. The Code Review Workflow serves as a general-purpose supplement for non-skill code changes or ad-hoc developer assistance.

**Sources:** [.github/workflows/claude-code-review.yml:1-45]()

---

## File Structure Summary

```
.github/workflows/
├── claude-code-review.yml    # Automatic PR reviews with code-review plugin
├── claude.yml                 # @claude mention-triggered assistance
└── claude-skill-review.yml    # Healthcare skill-specific reviews (see 5.1)
```

**Sources:** [.github/workflows/claude-code-review.yml:1](), [.github/workflows/claude.yml:1]()

---

# Page: Release Workflow

# Release Workflow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/claude-skill-review.yml](.github/workflows/claude-skill-review.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [README.md](README.md)

</details>



## Purpose and Scope

This document describes the release workflow that packages healthcare skills into distributable artifacts and creates GitHub releases. The workflow is defined in [.github/workflows/release.yml]() and executes when version tags are pushed to the repository.

For information about the automated skill review process that occurs before merging, see [Skill Review Workflow](#5.1). For general code review capabilities, see [Code Review Workflow](#5.2).

**Sources:** [.github/workflows/release.yml:1-43]()

---

## Workflow Trigger

The release workflow activates when a git tag matching the pattern `v*` is pushed to the repository. This tag-based trigger ensures releases are created intentionally through version tagging rather than on every merge.

```yaml
on:
  push:
    tags:
      - 'v*'
```

### Version Tag Pattern

Valid tags that trigger the workflow:
- `v1.0.0` - Standard semantic version
- `v2.1.3-beta` - Pre-release version
- `v0.0.1` - Initial version
- `v2024.01.15` - Date-based version

The tag name becomes part of the release artifact filenames through the `GITHUB_REF_NAME` environment variable.

**Sources:** [.github/workflows/release.yml:3-6]()

---

## Workflow Architecture

```mermaid
graph TB
    subgraph "Trigger Event"
        TAG["Git Tag Push<br/>(v* pattern)"]
    end
    
    subgraph "Release Job"
        CHECKOUT["actions/checkout@v4<br/>Fetch repository"]
        DISCOVER["Skill Discovery<br/>Find *-skill/ directories"]
        ZIP["Packaging Loop<br/>Create zip archives"]
        RELEASE["softprops/action-gh-release@v1<br/>Create GitHub release"]
        
        CHECKOUT --> DISCOVER
        DISCOVER --> ZIP
        ZIP --> RELEASE
    end
    
    subgraph "Outputs"
        ARTIFACTS["Zip Files<br/>skill-name-vX.Y.Z.zip"]
        NOTES["Auto-generated<br/>Release Notes"]
        DRAFT["Draft Release<br/>(requires manual publish)"]
        
        RELEASE --> ARTIFACTS
        RELEASE --> NOTES
        RELEASE --> DRAFT
    end
    
    TAG --> CHECKOUT
```

**Diagram: Release Workflow Execution Flow**

The workflow consists of a single `release` job that runs on `ubuntu-latest` with `contents: write` permissions to create releases and upload artifacts.

**Sources:** [.github/workflows/release.yml:8-43]()

---

## Skill Discovery and Packaging

### Directory Pattern Matching

The workflow identifies skills using a bash glob pattern that matches directories ending with `-skill/`:

```bash
for skill_dir in *-skill/; do
  if [ -d "$skill_dir" ]; then
    # Process skill
  fi
done
```

This pattern discovers:
- `clinical-trial-protocol-skill/`
- `prior-auth-review-skill/`
- `fhir-developer-skill/`

Any new skill added to the repository following this naming convention is automatically included in releases without workflow modifications.

**Sources:** [.github/workflows/release.yml:21-29]()

### Zip Archive Creation

Each skill is packaged into a separate zip file with the naming format:

```
{skill-directory-name}-{tag-name}.zip
```

For example, with tag `v1.2.0`:
- `clinical-trial-protocol-skill-v1.2.0.zip`
- `prior-auth-review-skill-v1.2.0.zip`
- `fhir-developer-skill-v1.2.0.zip`

The packaging process:
1. Changes to the skill directory: `cd "$skill_name"`
2. Creates recursive zip: `zip -r "../${skill_name}-${GITHUB_REF_NAME}.zip" .`
3. Returns to repository root: `cd ..`

All files within the skill directory are included, preserving the directory structure within the archive.

**Sources:** [.github/workflows/release.yml:23-27]()

---

## Packaged Skill Contents

```mermaid
graph LR
    subgraph "Repository Structure"
        REPO["Repository Root"]
        CTP["clinical-trial-protocol-skill/"]
        PAR["prior-auth-review-skill/"]
        FHIR["fhir-developer-skill/"]
        
        REPO --> CTP
        REPO --> PAR
        REPO --> FHIR
    end
    
    subgraph "Packaging Process"
        SCAN["Scan for *-skill/ dirs"]
        ZIP1["zip -r ctp.zip ."]
        ZIP2["zip -r par.zip ."]
        ZIP3["zip -r fhir.zip ."]
    end
    
    subgraph "Release Artifacts"
        ART1["clinical-trial-protocol-skill-v1.0.0.zip"]
        ART2["prior-auth-review-skill-v1.0.0.zip"]
        ART3["fhir-developer-skill-v1.0.0.zip"]
    end
    
    CTP --> SCAN
    PAR --> SCAN
    FHIR --> SCAN
    
    SCAN --> ZIP1
    SCAN --> ZIP2
    SCAN --> ZIP3
    
    ZIP1 --> ART1
    ZIP2 --> ART2
    ZIP3 --> ART3
```

**Diagram: Skill Packaging Transformation**

Each zip file contains the complete skill implementation:

| Skill Directory | Contents Included |
|----------------|-------------------|
| `clinical-trial-protocol-skill/` | `SKILL.md`, `references/`, `scripts/sample_size_calculator.py` |
| `prior-auth-review-skill/` | `SKILL.md`, `assets/` |
| `fhir-developer-skill/` | `SKILL.md`, `references/`, `scripts/setup_fhir_project.py` |

**Sources:** [.github/workflows/release.yml:19-33](), [README.md:19-42]()

---

## GitHub Release Creation

### Release Configuration

The workflow uses the `softprops/action-gh-release@v1` action to create a GitHub release with the following configuration:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `files` | `*-skill-*.zip` | Glob pattern matching all packaged skills |
| `generate_release_notes` | `true` | Auto-generate notes from commit history |
| `draft` | `true` | Create as draft requiring manual publish |
| `prerelease` | `false` | Mark as production release |

**Sources:** [.github/workflows/release.yml:35-42]()

### Draft Release Workflow

The release is created as a **draft** to enable manual review before publication:

```mermaid
stateDiagram-v2
    [*] --> TagPushed: Developer pushes v* tag
    TagPushed --> WorkflowExecutes: Workflow triggered
    WorkflowExecutes --> DraftCreated: Release job completes
    DraftCreated --> ManualReview: Maintainer reviews
    ManualReview --> Published: Approve and publish
    ManualReview --> Edited: Modify release notes
    Edited --> Published: Publish
    Published --> [*]: Users can download
```

**Diagram: Draft Release Lifecycle**

This manual gate allows maintainers to:
- Review auto-generated release notes
- Add additional context or breaking change warnings
- Verify all skill artifacts are properly packaged
- Ensure the release corresponds to the intended version

**Sources:** [.github/workflows/release.yml:41-42]()

---

## Auto-Generated Release Notes

The `generate_release_notes: true` parameter instructs GitHub to automatically create release notes from the commit history since the previous tag. The generated notes include:

- **Commit List**: All commits between the previous tag and current tag
- **Contributors**: List of contributors to this release
- **Pull Requests**: Links to merged PRs

Example generated notes structure:
```markdown
## What's Changed
* Add sample size calculator to clinical trial protocol by @contributor1 in #123
* Update prior auth review skill with new validation by @contributor2 in #124

## New Contributors
* @contributor1 made their first contribution in #123

**Full Changelog**: v1.0.0...v1.1.0
```

Maintainers can supplement these auto-generated notes with:
- High-level feature summaries
- Breaking changes or migration notes
- Known issues or limitations

**Sources:** [.github/workflows/release.yml:40]()

---

## Permissions and Security

The workflow requires specific GitHub Actions permissions:

```yaml
permissions:
  contents: write
```

The `contents: write` permission enables:
- Creating releases
- Uploading release artifacts
- Modifying release notes

This permission is scoped to the workflow execution and does not grant broader repository access. The workflow runs in an isolated environment and cannot access secrets or perform unauthorized operations.

**Sources:** [.github/workflows/release.yml:8-9]()

---

## Integration with Development Lifecycle

```mermaid
graph TB
    subgraph "Development Phase"
        DEV["Developer creates<br/>feature branch"]
        PR["Opens pull request"]
        REVIEW["Skill Review Workflow<br/>claude-skill-review.yml"]
        MERGE["Merge to main"]
    end
    
    subgraph "Release Phase"
        TAG["Create version tag<br/>git tag v1.0.0"]
        PUSH["Push tag to GitHub<br/>git push origin v1.0.0"]
        WORKFLOW["Release Workflow<br/>release.yml executes"]
        DRAFT["Draft release created"]
    end
    
    subgraph "Publication Phase"
        MANUAL["Maintainer review"]
        PUBLISH["Publish release"]
        DOWNLOAD["Users download<br/>skill zip files"]
    end
    
    DEV --> PR
    PR --> REVIEW
    REVIEW --> MERGE
    MERGE --> TAG
    TAG --> PUSH
    PUSH --> WORKFLOW
    WORKFLOW --> DRAFT
    DRAFT --> MANUAL
    MANUAL --> PUBLISH
    PUBLISH --> DOWNLOAD
```

**Diagram: Release Workflow in Development Lifecycle**

### Pre-Release Quality Gates

Before reaching the release workflow, skills pass through:

1. **Local Development**: Developer creates/modifies skill
2. **Pull Request**: Changes submitted for review
3. **Automated Skill Review**: [claude-skill-review.yml]() validates skill quality (see [Skill Review Workflow](#5.1))
4. **Human Review**: Maintainer approves PR
5. **Merge**: Changes integrated to `main` branch

The release workflow assumes all quality checks have passed and focuses solely on packaging and distribution.

**Sources:** [.github/workflows/release.yml:1-43](), [.github/workflows/claude-skill-review.yml:1-88]()

---

## Release Artifact Usage

### Distribution Methods

The packaged skills can be distributed through multiple channels:

| Method | Description | Use Case |
|--------|-------------|----------|
| GitHub Releases | Direct download from release page | Manual installation, archival |
| Marketplace Registry | Reference in `.claude-plugin/marketplace.json` | Automated installation via Claude Code |
| Git Clone | Direct repository access | Development, contribution |

### Marketplace Integration

While the release workflow creates distributable zip files, the primary distribution mechanism is through the marketplace registry:

```json
{
  "name": "clinical-trial-protocol",
  "source": "./",
  "skills": ["./clinical-trial-protocol-skill"]
}
```

Users install skills using the marketplace command:
```bash
/plugin install clinical-trial-protocol@healthcare
```

This command references the source repository, not the release artifacts. The release artifacts serve as versioned snapshots for archival and offline distribution purposes.

**Sources:** [README.md:8-14]()

---

## Workflow Execution Example

### Step-by-Step Execution

When a developer pushes tag `v2.1.0`:

```bash
$ git tag v2.1.0
$ git push origin v2.1.0
```

The workflow executes:

1. **Checkout** ([line 15-16]()):
   ```bash
   actions/checkout@v4
   # Repository cloned to workspace
   ```

2. **Skill Discovery** ([line 21]()):
   ```bash
   for skill_dir in *-skill/; do
   # Finds: clinical-trial-protocol-skill/
   #        prior-auth-review-skill/
   #        fhir-developer-skill/
   ```

3. **Packaging Loop** ([line 23-27]()):
   ```bash
   cd clinical-trial-protocol-skill
   zip -r ../clinical-trial-protocol-skill-v2.1.0.zip .
   cd ..
   # Repeats for each skill
   ```

4. **List Artifacts** ([line 32-33]()):
   ```bash
   ls -la *-skill-*.zip
   # Output:
   # clinical-trial-protocol-skill-v2.1.0.zip
   # prior-auth-review-skill-v2.1.0.zip
   # fhir-developer-skill-v2.1.0.zip
   ```

5. **Create Release** ([line 35-42]()):
   ```bash
   softprops/action-gh-release@v1
   # Uploads: all *-skill-*.zip files
   # Status: draft (requires manual publish)
   ```

**Sources:** [.github/workflows/release.yml:14-42]()

---

## Error Handling and Debugging

### Common Issues

| Issue | Symptom | Resolution |
|-------|---------|------------|
| No skills found | Empty artifact list | Verify skill directories follow `*-skill/` naming |
| Zip creation fails | Workflow fails at packaging step | Check file permissions in skill directories |
| Release creation fails | `softprops/action-gh-release` error | Verify `contents: write` permission enabled |
| Tag mismatch | Unexpected version in filenames | Ensure tag follows `v*` pattern |

### Debugging Commands

To test packaging locally before creating a release:

```bash
# Test skill discovery
ls -d *-skill/

# Test zip creation for one skill
cd clinical-trial-protocol-skill
zip -r ../test-package.zip .
cd ..

# Verify archive contents
unzip -l test-package.zip
```

### Workflow Logs

Review workflow execution logs at:
```
https://github.com/anthropics/healthcare/actions/workflows/release.yml
```

The logs show:
- Discovered skill directories
- Created zip files with sizes
- Release creation status
- Artifact upload results

**Sources:** [.github/workflows/release.yml:19-33]()

---

## Comparison with Other Workflows

```mermaid
graph TB
    subgraph "Skill Review Workflow"
        SR_TRIGGER["PR opened/synchronized"]
        SR_JOBS["detect-skills + review-skill<br/>(matrix strategy)"]
        SR_OUTPUT["PR comments with feedback"]
        
        SR_TRIGGER --> SR_JOBS
        SR_JOBS --> SR_OUTPUT
    end
    
    subgraph "Code Review Workflow"
        CR_TRIGGER["@claude mention in PR"]
        CR_JOBS["claude-review job"]
        CR_OUTPUT["General code feedback"]
        
        CR_TRIGGER --> CR_JOBS
        CR_JOBS --> CR_OUTPUT
    end
    
    subgraph "Release Workflow"
        RL_TRIGGER["Version tag push"]
        RL_JOBS["release job<br/>(single execution)"]
        RL_OUTPUT["Draft release + zip files"]
        
        RL_TRIGGER --> RL_JOBS
        RL_JOBS --> RL_OUTPUT
    end
```

**Diagram: Workflow Comparison**

| Aspect | Skill Review | Code Review | Release |
|--------|-------------|-------------|---------|
| Trigger | PR events | `@claude` mention | Version tag |
| Parallelization | Matrix (per skill) | Single job | Single job |
| Human interaction | Review feedback | Code suggestions | Manual publish |
| External services | Claude Code API | Claude Code API | GitHub Releases |
| Importance score | 49.07 | 1.62 | 8.89 |

The release workflow has moderate importance (8.89) compared to skill review (49.07) because:
- It executes less frequently (only on version tags)
- It requires manual final approval (draft releases)
- It performs mechanical packaging rather than quality validation

**Sources:** [.github/workflows/release.yml:1-43](), [.github/workflows/claude-skill-review.yml:1-88]()

---

## Future Enhancements

While the current release workflow is functional, potential improvements include:

### Semantic Version Validation

Add a step to validate that the tag follows semantic versioning conventions:
```bash
if [[ ! $GITHUB_REF_NAME =~ ^v[0-9]+\.[0-9]+\.[0-9]+.*$ ]]; then
  echo "Invalid version tag format"
  exit 1
fi
```

### Checksum Generation

Generate SHA256 checksums for each zip file:
```bash
sha256sum *-skill-*.zip > checksums.txt
```

### Automated Testing Before Release

Run skill validation tests before packaging:
```bash
- name: Test skills
  run: |
    for skill_dir in *-skill/; do
      # Run skill-specific tests
    done
```

These enhancements would increase release reliability and security without significantly complicating the workflow.

**Sources:** [.github/workflows/release.yml:1-43]()

---

# Page: Developer Guide

# Developer Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [.github/workflows/claude-skill-review.yml](.github/workflows/claude-skill-review.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [README.md](README.md)
- [icd10-codes/.claude-plugin/plugin.json](icd10-codes/.claude-plugin/plugin.json)

</details>



This guide is for developers who want to contribute skills or MCP servers to the healthcare marketplace, modify the marketplace configuration, or understand the development and release workflow. 

For detailed instructions on creating individual skills, see [Creating a New Skill](#6.1). For MCP server integration, see [Adding an MCP Server](#6.2). For testing guidance, see [Testing and Quality Assurance](#6.3). For an overview of the marketplace architecture, see [Marketplace Architecture](#2).

---

## Repository Structure

The healthcare marketplace repository follows a standardized directory structure that separates skills, MCP servers, and infrastructure:

```
anthropics/healthcare/
├── .claude-plugin/
│   └── marketplace.json              # Central registry of all plugins
├── .github/
│   └── workflows/
│       ├── claude-skill-review.yml   # Automated skill review
│       ├── claude-code-review.yml    # General code review
│       └── release.yml               # Release packaging
├── clinical-trial-protocol-skill/
│   ├── SKILL.md                      # Skill definition
│   ├── references/                   # Knowledge artifacts
│   └── scripts/                      # Helper scripts
├── prior-auth-review-skill/
│   ├── SKILL.md
│   └── assets/
├── fhir-developer-skill/
│   ├── SKILL.md
│   ├── references/
│   └── scripts/
├── cms-coverage/
│   └── .claude-plugin/
│       └── plugin.json               # MCP server configuration
├── npi-registry/
│   └── .claude-plugin/
│       └── plugin.json
├── pubmed/
│   └── .claude-plugin/
│       └── plugin.json
├── icd10-codes/
│   └── .claude-plugin/
│       └── plugin.json
└── README.md
```

### Directory Conventions

| Component Type | Directory Pattern | Required Files | Purpose |
|---------------|------------------|----------------|---------|
| **Skill** | `*-skill/` | `SKILL.md` | Contains skill definition and supporting artifacts |
| **MCP Server** | `*/` (no suffix) | `.claude-plugin/plugin.json` | Points to external HTTP MCP endpoint |
| **Marketplace** | `.claude-plugin/` | `marketplace.json` | Central registry for discovery |
| **CI/CD** | `.github/workflows/` | `*.yml` | Automated workflows |

**Sources:** [.claude-plugin/marketplace.json:1-74](), [icd10-codes/.claude-plugin/plugin.json:1-15]()

---

## Development Workflow

The development lifecycle follows a structured pull request workflow with automated quality gates:

```mermaid
graph TD
    Dev["Developer<br/>Local Environment"]
    Fork["Fork Repository"]
    Branch["Create Feature Branch"]
    Code["Add/Modify Skill or MCP"]
    LocalTest["Test Locally"]
    Push["Push to GitHub"]
    PR["Open Pull Request"]
    
    DetectJob["detect-skills Job<br/>(claude-skill-review.yml:12-53)"]
    ReviewJob["review-skill Job<br/>(claude-skill-review.yml:55-87)"]
    ClaudeAction["anthropics/claude-code-action@v1<br/>(line 76)"]
    PRComment["PR Comment Feedback"]
    
    HumanReview["Human Code Review"]
    Revisions["Address Feedback"]
    Approval["Approval & Merge"]
    
    Tag["Push v* Tag"]
    ReleaseJob["release Job<br/>(release.yml:12-42)"]
    ZipFiles["Create Skill Zips<br/>(release.yml:18-29)"]
    GHRelease["GitHub Release Draft<br/>(release.yml:35-42)"]
    
    Dev --> Fork
    Fork --> Branch
    Branch --> Code
    Code --> LocalTest
    LocalTest --> Push
    Push --> PR
    
    PR --> DetectJob
    DetectJob -->|"has_skills=true"| ReviewJob
    ReviewJob --> ClaudeAction
    ClaudeAction --> PRComment
    PRComment --> HumanReview
    
    HumanReview -->|"Changes Requested"| Revisions
    Revisions --> DetectJob
    HumanReview -->|"Approved"| Approval
    
    Approval --> Tag
    Tag --> ReleaseJob
    ReleaseJob --> ZipFiles
    ZipFiles --> GHRelease
```

**Sources:** [.github/workflows/claude-skill-review.yml:1-88](), [.github/workflows/release.yml:1-43]()

### Step-by-Step Workflow

**1. Fork and Clone**
```bash
git clone https://github.com/YOUR_USERNAME/healthcare.git
cd healthcare
git remote add upstream https://github.com/anthropics/healthcare.git
```

**2. Create Feature Branch**
```bash
git checkout -b add-my-skill
```

**3. Make Changes**
- Add skill directory with `SKILL.md` (for skills)
- Add MCP directory with `.claude-plugin/plugin.json` (for MCP servers)
- Update `.claude-plugin/marketplace.json` to register the plugin

**4. Test Locally**
- Install skill using local marketplace path
- Verify skill behavior matches expected outcomes
- Test MCP server connectivity (for MCP additions)

**5. Submit Pull Request**
```bash
git add .
git commit -m "Add: my-skill description"
git push origin add-my-skill
# Open PR on GitHub
```

**6. Automated Review Triggers**
The PR automatically triggers the `claude-skill-review` workflow which:
- Detects changed skills using [.github/workflows/claude-skill-review.yml:23-53]()
- Reviews each skill via Claude using [.github/workflows/claude-skill-review.yml:75-87]()
- Posts feedback as PR comments

**7. Address Feedback and Merge**
- Respond to Claude's automated review
- Make requested changes
- Obtain human approval
- Merge to main branch

**8. Release**
- Create and push version tag: `git tag v1.0.0 && git push --tags`
- Release workflow automatically packages skills into zip files
- GitHub release draft is created with artifacts

**Sources:** [.github/workflows/claude-skill-review.yml:1-88](), [.github/workflows/release.yml:1-43]()

---

## Automated Skill Review System

The most critical quality gate is the `claude-skill-review.yml` workflow, which uses Claude itself to review healthcare skills.

```mermaid
graph LR
    subgraph "Trigger Events"
        PROpen["pull_request:<br/>opened"]
        PRSync["pull_request:<br/>synchronize"]
        PRReady["pull_request:<br/>ready_for_review"]
        PRReopen["pull_request:<br/>reopened"]
    end
    
    subgraph "detect-skills Job"
        Checkout1["actions/checkout@v4<br/>(line 19)"]
        GitDiff["git diff --name-only<br/>(line 27)"]
        FindSkills["find SKILL.md files<br/>(line 30)"]
        MatchChanges["Match changed files<br/>to skill dirs (line 34-41)"]
        OutputJSON["Output JSON array<br/>(line 45-46)"]
    end
    
    subgraph "review-skill Job (Matrix)"
        MatrixSetup["strategy.matrix.skill<br/>(line 60-61)"]
        Checkout2["actions/checkout@v4<br/>(line 71)"]
        ClaudeAction["anthropics/claude-code-action@v1<br/>(line 76)"]
        SkillCreator["plugin: example-skills@<br/>anthropic-agent-skills<br/>(line 80)"]
        GitDiffPrompt["git diff origin/BASE<br/>-- SKILL_DIR/ (line 85)"]
        GHComment["gh pr comment (line 87)"]
    end
    
    PROpen --> Checkout1
    PRSync --> Checkout1
    PRReady --> Checkout1
    PRReopen --> Checkout1
    
    Checkout1 --> GitDiff
    GitDiff --> FindSkills
    FindSkills --> MatchChanges
    MatchChanges --> OutputJSON
    
    OutputJSON -->|"has_skills=true"| MatrixSetup
    MatrixSetup --> Checkout2
    Checkout2 --> ClaudeAction
    ClaudeAction --> SkillCreator
    SkillCreator --> GitDiffPrompt
    GitDiffPrompt --> GHComment
```

### Skill Detection Algorithm

The `detect-skills` job identifies which skills were modified in a PR:

**Algorithm Flow:**
1. **Fetch Changed Files** - Uses `git diff --name-only` to compare PR branch against base branch [.github/workflows/claude-skill-review.yml:27]()
2. **Find Skill Directories** - Locates all directories containing `SKILL.md` files [.github/workflows/claude-skill-review.yml:30]()
3. **Match Changes to Skills** - Iterates through skill directories and checks if any changed files fall under each skill path [.github/workflows/claude-skill-review.yml:34-41]()
4. **Output JSON Array** - Converts affected skills to JSON array for matrix strategy [.github/workflows/claude-skill-review.yml:45-46]()

**Example Detection:**
```bash
# Changed files: clinical-trial-protocol-skill/SKILL.md
# Skill directories: clinical-trial-protocol-skill/, prior-auth-review-skill/
# Output: skills=["clinical-trial-protocol-skill"]
# has_skills=true
```

**Sources:** [.github/workflows/claude-skill-review.yml:23-53]()

### Claude Review Process

The `review-skill` job uses a matrix strategy to review each detected skill in parallel:

**Configuration:**
- **Matrix Variable:** `matrix.skill` contains skill directory path [.github/workflows/claude-skill-review.yml:60-61]()
- **Claude Action:** `anthropics/claude-code-action@v1` [.github/workflows/claude-skill-review.yml:76]()
- **Plugin Marketplace:** `https://github.com/anthropics/skills.git` [.github/workflows/claude-skill-review.yml:79]()
- **Active Plugin:** `example-skills@anthropic-agent-skills` (skill-creator skill) [.github/workflows/claude-skill-review.yml:80]()
- **Allowed Tools:** `Bash(gh pr comment:*)`, `Bash(git:*)`, `Read`, `Glob`, `Grep`, `Skill` [.github/workflows/claude-skill-review.yml:81]()

**Review Prompt Template:**
```
Use the skill-creator skill to review the **{matrix.skill}** skill in PR #{pr_number}.

Use `git diff origin/{base_ref} -- {matrix.skill}/` to see what changed.
If this is a new skill, provide a full review.
If it's changes to an existing skill, focus on the changes.

Post your feedback as a comment using `gh pr comment`.
Use the skill title in the header.
```

Claude analyzes the skill definition, supporting artifacts, and changes, then posts structured feedback directly to the PR.

**Sources:** [.github/workflows/claude-skill-review.yml:55-88]()

---

## Release Packaging

The `release.yml` workflow automates skill packaging when version tags are pushed:

```mermaid
graph TD
    TagPush["Git Tag Push<br/>Pattern: v*<br/>(release.yml:5-6)"]
    CheckoutCode["actions/checkout@v4<br/>(release.yml:16)"]
    
    FindSkills["Find Directories<br/>Pattern: *-skill/<br/>(release.yml:21)"]
    
    subgraph "For Each Skill Directory"
        ExtractName["Extract skill_name<br/>from directory<br/>(release.yml:23)"]
        ZipSkill["cd skill_dir<br/>zip -r ../{name}-{tag}.zip .<br/>(release.yml:25-26)"]
    end
    
    ListZips["List Created Zips<br/>ls -la *-skill-*.zip<br/>(release.yml:32-33)"]
    
    CreateRelease["softprops/action-gh-release@v1<br/>(release.yml:36)"]
    AttachFiles["Attach: *-skill-*.zip<br/>(release.yml:38-39)"]
    DraftMode["draft: true<br/>(release.yml:41)"]
    
    TagPush --> CheckoutCode
    CheckoutCode --> FindSkills
    FindSkills --> ExtractName
    ExtractName --> ZipSkill
    ZipSkill --> ListZips
    ListZips --> CreateRelease
    CreateRelease --> AttachFiles
    AttachFiles --> DraftMode
```

### Packaging Logic

The release job scans for skill directories and creates zip archives:

**Directory Pattern:** `*-skill/` [.github/workflows/release.yml:21]()

**Naming Convention:** `{skill-name}-{tag-version}.zip`
- Example: `clinical-trial-protocol-skill-v1.0.0.zip`

**Contents:** All files within the skill directory are included in the zip

**Release Mode:** Draft releases are created automatically, requiring manual publishing [.github/workflows/release.yml:41]()

**Sources:** [.github/workflows/release.yml:1-43]()

---

## Marketplace Registration

All skills and MCP servers must be registered in `.claude-plugin/marketplace.json`:

### Skill Registration Schema

```json
{
  "name": "skill-identifier",
  "source": "./",
  "description": "Brief description",
  "category": "healthcare",
  "tags": ["tag1", "tag2"],
  "strict": false,
  "skills": [
    "./skill-directory-name"
  ]
}
```

**Key Fields:**
| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Plugin identifier used in install commands |
| `source` | Yes | Relative path to skill source (use `./` for inline skills) |
| `description` | Yes | User-facing description shown in marketplace |
| `category` | Yes | Category for organization (use `"healthcare"`) |
| `tags` | No | Searchable tags |
| `strict` | No | Skill strictness mode (typically `false`) |
| `skills` | Yes | Array of skill directory paths |

**Sources:** [.claude-plugin/marketplace.json:12-43]()

### MCP Server Registration Schema

```json
{
  "name": "mcp-identifier",
  "source": "./mcp-directory",
  "description": "MCP server description",
  "category": "healthcare",
  "tags": ["tag1", "tag2"]
}
```

MCP servers reference a subdirectory containing `.claude-plugin/plugin.json` which defines the HTTP endpoint:

```json
{
  "name": "mcp-name",
  "version": "1.0.0",
  "description": "Server description",
  "author": {
    "name": "Organization",
    "url": "https://example.com"
  },
  "mcpServers": {
    "Server Name": {
      "type": "http",
      "url": "https://example.com/mcp/endpoint"
    }
  }
}
```

**Sources:** [.claude-plugin/marketplace.json:45-72](), [icd10-codes/.claude-plugin/plugin.json:1-15]()

---

## Prerequisites and Setup

### Required Tools

| Tool | Purpose | Installation |
|------|---------|--------------|
| **Git** | Version control | `brew install git` or https://git-scm.com/ |
| **GitHub CLI** | PR operations (used by workflows) | `brew install gh` or https://cli.github.com/ |
| **Claude Code** | Local testing of skills | Install Claude desktop app |
| **Python 3.8+** | For skills with Python scripts | https://www.python.org/ |

### Local Testing Setup

**1. Clone Repository:**
```bash
git clone https://github.com/anthropics/healthcare.git
cd healthcare
```

**2. Install Skills Locally:**
```bash
# Add marketplace using local path
/plugin marketplace add file:///path/to/healthcare

# Install specific skill
/plugin install skill-name@healthcare
```

**3. Test Skill Functionality:**
- Invoke the skill in Claude Code
- Verify expected behavior
- Check that MCP servers are accessible (if applicable)
- Review generated outputs

**4. Validate Marketplace Configuration:**
```bash
# Verify JSON syntax
cat .claude-plugin/marketplace.json | python -m json.tool

# Check skill directories exist
ls -la *-skill/
```

### Permissions Required

For contributing to the repository:
- **Fork Permission:** Ability to fork the repository
- **PR Creation:** Ability to open pull requests against `anthropics/healthcare`

For automated workflows (GitHub secrets):
- `CLAUDE_CODE_OAUTH_TOKEN` - Required for `claude-code-action` in skill reviews [.github/workflows/claude-skill-review.yml:8-9]()

**Sources:** [.github/workflows/claude-skill-review.yml:1-88](), [README.md:1-63]()

---

## Code Review Workflow

In addition to automated skill reviews, the repository supports on-demand code reviews via `@claude` mentions:

**Trigger:** Mention `@claude` in a PR comment
**Workflow:** `.github/workflows/claude-code-review.yml`
**Plugin:** `code-review` plugin

This provides general code review capabilities beyond skill-specific validation.

For details on the skill review workflow, see [Skill Review Workflow](#5.1). For release workflow details, see [Release Workflow](#5.3).

**Sources:** [.github/workflows/claude-skill-review.yml:1-88]()

---

## Contributing Guidelines

### Skill Contributions

1. **Review Existing Skills** - Examine `clinical-trial-protocol-skill/`, `prior-auth-review-skill/`, and `fhir-developer-skill/` for examples
2. **Follow Directory Pattern** - Use `{skill-name}-skill/` naming convention
3. **Create SKILL.md** - Define skill using the SKILL.md format
4. **Add Supporting Files** - Include reference materials in `references/`, scripts in `scripts/`, and assets in `assets/`
5. **Register in Marketplace** - Add entry to `.claude-plugin/marketplace.json`
6. **Test Locally** - Verify skill works as expected before submitting PR

See [Creating a New Skill](#6.1) for detailed instructions.

### MCP Server Contributions

1. **Create MCP Directory** - Use descriptive directory name (no `-skill` suffix)
2. **Add plugin.json** - Create `.claude-plugin/plugin.json` with HTTP endpoint configuration
3. **Verify Endpoint** - Ensure MCP server is accessible and operational
4. **Register in Marketplace** - Add entry to `.claude-plugin/marketplace.json`
5. **Document Usage** - Update README.md with server description and installation commands

See [Adding an MCP Server](#6.2) for detailed instructions.

### Pull Request Best Practices

| Practice | Recommendation |
|----------|----------------|
| **Branch Naming** | Use descriptive names: `add-radiology-skill`, `fix-fhir-template` |
| **Commit Messages** | Follow conventional commits: `Add:`, `Fix:`, `Update:`, `Docs:` |
| **PR Description** | Explain what changed, why, and how to test |
| **Skill Changes** | One skill per PR for cleaner reviews |
| **Breaking Changes** | Document in PR description and update version |

**Sources:** [.github/workflows/claude-skill-review.yml:1-88](), [README.md:1-63]()

---

# Page: Creating a New Skill

# Creating a New Skill

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [clinical-trial-protocol-skill/README.md](clinical-trial-protocol-skill/README.md)
- [clinical-trial-protocol-skill/SKILL.md](clinical-trial-protocol-skill/SKILL.md)
- [clinical-trial-protocol-skill/scripts/sample_size_calculator.py](clinical-trial-protocol-skill/scripts/sample_size_calculator.py)
- [icd10-codes/.claude-plugin/plugin.json](icd10-codes/.claude-plugin/plugin.json)
- [prior-auth-review-skill/README.md](prior-auth-review-skill/README.md)

</details>



This guide provides step-by-step instructions for creating a new Claude Code skill and integrating it into the healthcare marketplace. Skills are AI-powered capabilities that orchestrate complex healthcare workflows by combining Claude's reasoning with external data sources and tools.

For information about the distinction between Skills and MCP Servers, see [Skills vs MCP Servers](#2.1). For testing and quality assurance guidance, see [Testing and Quality Assurance](#6.3). For understanding how skills are automatically reviewed, see [Skill Review Workflow](#5.1).

---

## Skill Architecture Overview

Skills in the healthcare marketplace follow a standardized structure that enables automated discovery, review, and distribution. Each skill is a self-contained directory with specific required files.

### Skill Directory Structure

```mermaid
graph TB
    subgraph "Root Repository"
        MKT[".claude-plugin/marketplace.json"]
    end
    
    subgraph "Skill Directory: my-healthcare-skill/"
        SKILL["SKILL.md<br/>(Required)"]
        README["README.md<br/>(Required)"]
        
        subgraph "Optional Components"
            REF["references/<br/>(Subskills)"]
            SCRIPTS["scripts/<br/>(Python tools)"]
            ASSETS["assets/<br/>(Templates, samples)"]
            WAYPT["waypoints/<br/>(Runtime state)"]
        end
    end
    
    subgraph "CI/CD Detection"
        DETECT["detect-skills job"]
        REVIEW["review-skill job"]
    end
    
    MKT -->|"skills: ['./my-healthcare-skill']"| SKILL
    SKILL -->|"Defines behavior"| README
    DETECT -->|"Scans for SKILL.md"| SKILL
    SKILL -->|"Triggers review"| REVIEW
```

**Sources:** [.claude-plugin/marketplace.json:1-74](), [clinical-trial-protocol-skill/SKILL.md:1-10]()

---

## Step 1: Create Skill Directory

Create a new directory following the naming convention `{skill-name}-skill/`. The suffix `-skill` is important for automated detection.

```bash
mkdir prior-auth-review-skill
cd prior-auth-review-skill
```

The directory name should be:
- **Descriptive**: Clearly indicates the skill's purpose
- **Kebab-case**: Use hyphens, not underscores or spaces
- **Suffixed**: End with `-skill` for consistency

**Sources:** [.claude-plugin/marketplace.json:20-21](), [.claude-plugin/marketplace.json:30-31]()

---

## Step 2: Create SKILL.md (Required)

The `SKILL.md` file is the skill's execution specification. It defines how Claude should behave when the skill is invoked.

### SKILL.md Structure

```mermaid
graph LR
    subgraph "SKILL.md Components"
        FM["Frontmatter<br/>(YAML)"]
        CTRL["Execution Control<br/>Section"]
        OV["Overview<br/>Section"]
        ARCH["Architecture<br/>Section"]
        PREREQ["Prerequisites<br/>Section"]
        USAGE["Usage<br/>Section"]
        IMPL["Implementation<br/>Requirements"]
    end
    
    FM -->|"name, description"| CTRL
    CTRL -->|"Defines startup behavior"| OV
    OV -->|"What skill does"| ARCH
    ARCH -->|"Waypoints, subskills"| PREREQ
    PREREQ -->|"MCP servers, deps"| USAGE
    USAGE -->|"User workflows"| IMPL
```

**Sources:** [clinical-trial-protocol-skill/SKILL.md:1-508]()

### Required Frontmatter

Every `SKILL.md` must begin with YAML frontmatter:

```yaml
---
name: my-healthcare-skill
description: Brief description of when this skill should be used. Include trigger phrases like "Create a [X]", "Help me [Y]", or specific healthcare use cases.
---
```

**Frontmatter Fields:**
- `name`: Must match the directory name (without `-skill` suffix)
- `description`: Should include natural language triggers that help Claude decide when to invoke this skill

**Sources:** [clinical-trial-protocol-skill/SKILL.md:1-4]()

### Execution Control Section

Immediately after the frontmatter, define how Claude should execute the skill:

```markdown
## ⚠️ EXECUTION CONTROL - READ THIS FIRST

**CRITICAL: This skill follows a [PATTERN] approach:**

1. **Display welcome message FIRST**
2. **Collect required inputs**
3. **Execute workflow steps sequentially**
4. **DO NOT pre-read subskill files** - Load on-demand only

**Why this matters:**
- Pre-reading wastes context and memory
- Subskills load only when actually needed
- Workflow handles resuming from existing waypoints
```

This section prevents Claude from loading all dependencies upfront, which would waste context window.

**Sources:** [clinical-trial-protocol-skill/SKILL.md:8-21]()

### Waypoint-Based Architecture

If your skill uses multi-step workflows, define waypoint files for state persistence:

```markdown
### Waypoint-Based Design

All analysis data is stored in `waypoints/` directory:

\`\`\`
waypoints/
├── intervention_metadata.json    # Initial inputs and status
├── 01_research_summary.json      # Step 1 outputs
├── 02_protocol_draft.md          # Step 2 outputs
└── 03_final_document.md          # Step 3 outputs
\`\`\`
```

**Waypoint Benefits:**
- **Resumability**: Users can stop and restart without losing progress
- **Transparency**: All intermediate data is visible and editable
- **Debugging**: Each step's outputs can be inspected independently

**Sources:** [clinical-trial-protocol-skill/SKILL.md:43-59]()

### Prerequisites Section

Document all external dependencies:

```markdown
## Prerequisites

### 1. MCP Server Dependencies

**cms-coverage MCP Server:**
- Purpose: Access Medicare coverage policies
- Tools used: `search_coverage_policies`, `get_policy_details`
- Installation: `claude mcp add-from-marketplace anthropics/healthcare/cms-coverage`

### 2. Python Dependencies

**Installation:**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

**Required packages:**
- scipy >= 1.11.0
- numpy >= 1.24.0
```

**Sources:** [clinical-trial-protocol-skill/SKILL.md:85-135]()

### Implementation Requirements

End with explicit execution instructions:

```markdown
## Implementation Requirements

When this skill is invoked:

1. **Display welcome message** with mode selection
2. **Wait for user confirmation** before proceeding
3. **Execute steps sequentially:**
   - Read subskill file only when step is ready to execute
   - Do NOT read files in advance
   - Execute all instructions within the subskill
4. **Handle errors gracefully:**
   - Offer retry or exit options
   - Save progress in waypoints
5. **Track progress:**
   - Update metadata after each step
   - Show progress indicators
```

**Sources:** [clinical-trial-protocol-skill/SKILL.md:460-508]()

---

## Step 3: Create README.md (Required)

The `README.md` provides user-facing documentation. It should be clear and concise, focusing on what the skill does and how to use it.

### README.md Structure

```markdown
# [Skill Name]

[One-sentence description of what the skill does]

## Overview

**Target Users:** [Who should use this skill]

**Key Features:**
- Feature 1
- Feature 2
- Feature 3

## Disclaimers

> **[IMPORTANT DISCLAIMER]**
>
> [Clearly state limitations, when human review is required, etc.]

## Workflow Steps

| Step | Name | Description | Output |
| ---- | ---- | ----------- | ------ |
| 0 | [Step name] | [What it does] | `waypoint_file.json` |
| 1 | [Step name] | [What it does] | `waypoint_file.md` |

## Requirements

- **Python Dependencies** - `package1`, `package2`
- **MCP Servers** - [Required MCP servers]

## Getting Started

See [SKILL.md](SKILL.md) for complete installation and usage instructions.
```

**Sources:** [clinical-trial-protocol-skill/README.md:1-55](), [prior-auth-review-skill/README.md:1-78]()

---

## Step 4: Register in Marketplace

Add your skill to [.claude-plugin/marketplace.json:11-44]() in the `plugins` array:

```json
{
  "name": "my-healthcare-skill",
  "source": "./",
  "description": "Brief description matching SKILL.md frontmatter",
  "category": "healthcare",
  "tags": ["tag1", "tag2", "tag3"],
  "strict": false,
  "skills": [
    "./my-healthcare-skill"
  ]
}
```

### Marketplace Registration Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier, should match directory name without `-skill` suffix |
| `source` | Yes | Always `"./"` for skills (indicates repository root) |
| `description` | Yes | User-facing description, shown in skill listings |
| `category` | Yes | Always `"healthcare"` for this marketplace |
| `tags` | Yes | Array of searchable tags (e.g., `["fhir", "api", "interoperability"]`) |
| `strict` | Yes | Always `false` for skills (allows flexible invocation) |
| `skills` | Yes | Array with single path: `["./my-healthcare-skill"]` |

**Sources:** [.claude-plugin/marketplace.json:11-44]()

### Skill vs MCP Registration

```mermaid
graph TB
    subgraph "Skill Registration"
        SKILL_REG["Plugin Entry"]
        SKILL_SOURCE["source: './'"]
        SKILL_PATH["skills: ['./my-skill']"]
        SKILL_DIR["my-skill/<br/>SKILL.md"]
    end
    
    subgraph "MCP Registration"
        MCP_REG["Plugin Entry"]
        MCP_SOURCE["source: './my-mcp'"]
        MCP_NO_SKILLS["No 'skills' field"]
        MCP_DIR["my-mcp/<br/>.claude-plugin/plugin.json"]
    end
    
    SKILL_REG --> SKILL_SOURCE
    SKILL_SOURCE --> SKILL_PATH
    SKILL_PATH --> SKILL_DIR
    
    MCP_REG --> MCP_SOURCE
    MCP_SOURCE --> MCP_NO_SKILLS
    MCP_NO_SKILLS --> MCP_DIR
```

**Key Difference:** Skills have a `skills` array pointing to skill directories; MCP servers do not.

**Sources:** [.claude-plugin/marketplace.json:11-72]()

---

## Step 5: Add Optional Components

### Subskills (references/ directory)

For multi-step workflows, create modular subskills in the `references/` directory:

```
my-healthcare-skill/
└── references/
    ├── 00-initialize.md
    ├── 01-research.md
    ├── 02-analysis.md
    └── 03-generate.md
```

**Subskill Pattern:**
- Each subskill is a standalone markdown file
- Loaded on-demand by the orchestrator (SKILL.md)
- Contains specific instructions for one workflow step
- Reads from and writes to waypoint files

**Example subskill structure:**
```markdown
# Step 1: Research Phase

## Input
- Read from: `waypoints/metadata.json`

## Process
1. Perform X using Y tool
2. Extract Z data
3. Summarize findings

## Output
- Write to: `waypoints/01_research.json`
- Format: {...}
```

**Sources:** [clinical-trial-protocol-skill/SKILL.md:65-76]()

### Scripts (scripts/ directory)

Add Python or shell scripts for computational tasks:

```python
# scripts/sample_size_calculator.py
"""
Statistical calculations for clinical trial sample sizing.
"""

def calculate_continuous_sample_size(
    effect_size: float,
    std_dev: float,
    alpha: float = 0.05,
    power: float = 0.80
) -> Dict[str, Any]:
    # Implementation...
```

**Script Guidelines:**
- Include docstrings and type hints
- Provide CLI interface with argparse
- Output JSON for easy parsing by Claude
- Include requirements.txt if dependencies needed

**Sources:** [clinical-trial-protocol-skill/scripts/sample_size_calculator.py:1-459]()

### Assets (assets/ directory)

Store templates, samples, or reference documents:

```
assets/
├── templates/
│   └── protocol-template.md
├── samples/
│   └── sample-case.json
└── references/
    └── fda-guidance.md
```

**Sources:** [clinical-trial-protocol-skill/SKILL.md:118-122]()

---

## Step 6: Skill Detection and Review Integration

### How Skills Are Detected

The CI/CD system automatically detects new or modified skills:

```mermaid
graph LR
    subgraph "detect-skills Job"
        DIFF["git diff<br/>--name-only"]
        FIND["find . -name SKILL.md"]
        MATCH["Match changed paths<br/>with SKILL.md locations"]
        OUTPUT["Output: skills array<br/>has_skills boolean"]
    end
    
    subgraph "review-skill Job"
        MATRIX["Matrix strategy:<br/>skill = skills array"]
        CLAUDE["anthropics/claude-code-action@v1"]
        PLUGIN["skill-creator plugin"]
        COMMENT["Post review comment<br/>on PR"]
    end
    
    DIFF --> MATCH
    FIND --> MATCH
    MATCH --> OUTPUT
    OUTPUT -->|"if has_skills = true"| MATRIX
    MATRIX --> CLAUDE
    CLAUDE --> PLUGIN
    PLUGIN --> COMMENT
```

**Detection Logic:**
1. Get changed files from `git diff` between PR base and head
2. Find all `SKILL.md` files in repository
3. Extract skill directory (parent of `SKILL.md`)
4. Check if skill directory appears in changed files
5. Output skill name (directory name) if changes detected

**Sources:** High-level diagrams (Diagram 2), inferred from workflow descriptions

### Skill Review Criteria

The automated review checks:
- **SKILL.md completeness**: Frontmatter, sections, implementation requirements
- **README.md clarity**: User-facing documentation, disclaimers
- **Marketplace registration**: Proper JSON format, required fields
- **Dependencies**: MCP servers listed, Python packages documented
- **Waypoint usage**: State management, resumability

For detailed review process, see [Skill Review Workflow](#5.1).

**Sources:** High-level diagrams (Diagram 2, Diagram 5)

---

## Complete Skill Creation Workflow

```mermaid
stateDiagram-v2
    [*] --> CreateDirectory: mkdir my-skill
    CreateDirectory --> WriteSKILL: Create SKILL.md
    WriteSKILL --> WriteREADME: Create README.md
    WriteREADME --> AddComponents: Add references/, scripts/, assets/
    AddComponents --> RegisterMarketplace: Update marketplace.json
    RegisterMarketplace --> CreatePR: Open pull request
    
    CreatePR --> AutoReview: CI triggers skill review
    AutoReview --> ReviewFeedback: Claude posts comments
    
    state ReviewFeedback {
        [*] --> AddressComments
        AddressComments --> PushChanges
        PushChanges --> ReReview
        ReReview --> [*]
    }
    
    ReviewFeedback --> HumanApproval: Changes addressed
    HumanApproval --> Merge: LGTM
    Merge --> TagRelease: Create v* tag
    TagRelease --> ReleasePackage: Release workflow runs
    ReleasePackage --> [*]: Skill published
```

**Sources:** High-level diagrams (Diagram 5)

---

## Best Practices

### Context Window Management

**Problem:** Skills with many subskills can exceed Claude's context window.

**Solution:** Use lazy loading:
```markdown
## Implementation Requirements

4. **For each step execution (LAZY LOADING):**
   - ONLY when a step is ready to execute, read the corresponding subskill file
   - Do NOT read subskill files in advance
   - Execute all instructions within the subskill before proceeding
```

**Sources:** [clinical-trial-protocol-skill/SKILL.md:479-486]()

### State Persistence

**Always use waypoint files for:**
- User inputs collected in early steps
- Intermediate analysis results
- Configuration and metadata
- Step completion tracking

**Waypoint file naming:**
- JSON for structured data: `metadata.json`, `config.json`
- Markdown for documents: `01_research.md`, `02_draft.md`
- Prefix with step number for clarity: `00_init.json`, `01_data.json`

**Sources:** [clinical-trial-protocol-skill/SKILL.md:48-59]()

### Human-in-the-Loop Design

For sensitive decisions (medical, regulatory, financial):
```markdown
**Human Decision Point:** After [step/analysis] is generated, the professional reviews the AI recommendation before proceeding to the next phase.
```

Example from prior authorization skill:
- Subskill 1 generates recommendation
- Human reviews and confirms/rejects
- Subskill 2 finalizes decision only after human approval

**Sources:** [prior-auth-review-skill/README.md:45-66]()

### Error Handling

```markdown
## Error Handling

### MCP Server Unavailable
- Detected in: Step [X]
- Action: Display error with installation instructions
- Allow user to retry after installing

### Step Fails
- Display error message from subskill
- Ask user: "Retry step? (Yes/No)"
- Save current state for resume capability
```

**Sources:** [clinical-trial-protocol-skill/SKILL.md:417-435]()

---

## Testing Your Skill Locally

Before submitting a pull request:

1. **Validate JSON syntax:**
   ```bash
   python -m json.tool .claude-plugin/marketplace.json
   ```

2. **Test SKILL.md frontmatter:**
   ```python
   import yaml
   with open('my-skill/SKILL.md') as f:
       content = f.read()
       frontmatter = content.split('---')[1]
       parsed = yaml.safe_load(frontmatter)
       assert 'name' in parsed
       assert 'description' in parsed
   ```

3. **Invoke skill in Claude Code:**
   - Install marketplace locally
   - Test each workflow path
   - Verify waypoint files are created correctly
   - Check error handling

4. **Review generated artifacts:**
   - Check waypoint files for completeness
   - Verify output files are properly formatted
   - Test resume capability (interrupt and restart)

**Sources:** Inferred from best practices and workflow descriptions

---

## Example: Minimal Skill Implementation

Here's a minimal but complete skill:

### Directory Structure
```
simple-diagnosis-skill/
├── SKILL.md
└── README.md
```

### SKILL.md
```markdown
---
name: simple-diagnosis-skill
description: Generate differential diagnosis lists. Use when user says "Help me with differential diagnosis for [symptoms]" or "What could cause [symptoms]".
---

# Simple Diagnosis Skill

## ⚠️ EXECUTION CONTROL

1. Display welcome message
2. Collect patient symptoms
3. Generate differential diagnosis
4. Display results

## Overview

This skill helps generate differential diagnosis lists based on patient symptoms.

## How to Use

When invoked:
1. Ask user for: chief complaint, symptoms, duration, severity
2. Generate differential diagnosis list (most to least likely)
3. Include red flags and suggested workup

## Implementation Requirements

When this skill is invoked:
1. Greet user and explain the skill
2. Collect symptoms using structured questions
3. Generate diagnosis list with:
   - Likelihood (high/medium/low)
   - Key distinguishing features
   - Recommended workup
4. Emphasize limitations: AI-generated, requires clinical judgment
```

### README.md
```markdown
# Simple Diagnosis Skill

Generate differential diagnosis lists based on patient symptoms.

## Overview

**Target Users:** Medical students, clinicians

**Key Features:**
- Structured symptom collection
- Evidence-based diagnosis suggestions
- Workup recommendations

## Disclaimer

> **NOT MEDICAL ADVICE:** This tool provides educational differential diagnosis suggestions only. All clinical decisions require professional judgment and patient-specific context.

## Getting Started

See [SKILL.md](SKILL.md) for usage instructions.
```

### Marketplace Entry
```json
{
  "name": "simple-diagnosis",
  "source": "./",
  "description": "Generate differential diagnosis lists for clinical symptoms",
  "category": "healthcare",
  "tags": ["diagnosis", "clinical-reasoning", "education"],
  "strict": false,
  "skills": [
    "./simple-diagnosis-skill"
  ]
}
```

**Sources:** Example synthesized from patterns in [clinical-trial-protocol-skill/SKILL.md:1-508]() and [.claude-plugin/marketplace.json:11-44]()

---

## Summary Checklist

Before submitting your skill for review:

- [ ] **Directory created** with `-skill` suffix
- [ ] **SKILL.md exists** with valid YAML frontmatter
- [ ] **SKILL.md has** execution control, overview, architecture, prerequisites, implementation sections
- [ ] **README.md exists** with overview, disclaimers, getting started
- [ ] **Marketplace entry added** to `.claude-plugin/marketplace.json`
- [ ] **All fields required** in marketplace entry (name, source, description, category, tags, strict, skills)
- [ ] **Dependencies documented** (MCP servers, Python packages)
- [ ] **Waypoint files used** for state persistence (if multi-step)
- [ ] **Error handling included** in SKILL.md
- [ ] **Disclaimers present** for medical/regulatory content
- [ ] **Tested locally** in Claude Code environment

**Sources:** Synthesized from all referenced files

---

# Page: Adding an MCP Server

# Adding an MCP Server

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [cms-coverage/.claude-plugin/plugin.json](cms-coverage/.claude-plugin/plugin.json)
- [icd10-codes/.claude-plugin/plugin.json](icd10-codes/.claude-plugin/plugin.json)
- [npi-registry/.claude-plugin/plugin.json](npi-registry/.claude-plugin/plugin.json)
- [pubmed/.claude-plugin/plugin.json](pubmed/.claude-plugin/plugin.json)

</details>



## Purpose and Scope

This document provides a step-by-step guide for integrating a new external data source as an MCP (Model Context Protocol) server into the healthcare marketplace. It covers the directory structure requirements, `plugin.json` configuration format, and registration in `marketplace.json`.

For information about creating skills that consume MCP servers, see [Creating a New Skill](#6.1). For understanding the conceptual differences between skills and MCP servers, see [Skills vs MCP Servers](#2.1).

## MCP Server Architecture Overview

MCP servers in the healthcare marketplace use a two-tier configuration system that separates marketplace metadata from server implementation details. This architecture enables distributed hosting where the marketplace registry resides in the repository while actual MCP servers run on external infrastructure.

### Two-Tier Configuration Model

```mermaid
graph TB
    subgraph "Repository: anthropics/healthcare"
        MKT["marketplace.json<br/>.claude-plugin/"]
        
        subgraph "MCP Server Directory"
            DIR["<mcp-name>/<br/>(e.g., cms-coverage/)"]
            PLUGIN[".claude-plugin/plugin.json"]
        end
    end
    
    subgraph "External Infrastructure"
        HTTP["HTTP MCP Server<br/>(e.g., https://mcp.deepsense.ai/cms_coverage/mcp)"]
    end
    
    MKT -->|"references source: ./cms-coverage"| DIR
    DIR -->|"contains"| PLUGIN
    PLUGIN -->|"defines url"| HTTP
    
    USER["User Command:<br/>claude mcp add-from-marketplace<br/>anthropics/healthcare/cms-coverage"] --> MKT
```

**Sources:** [.claude-plugin/marketplace.json:1-74](), [cms-coverage/.claude-plugin/plugin.json:1-15]()

The marketplace entry in `marketplace.json` contains only discovery metadata (name, description, tags), while the `plugin.json` file in the server's subdirectory specifies the actual server endpoint and connection details.

## Directory Structure Requirements

An MCP server must follow this exact directory layout:

```
<mcp-server-name>/
└── .claude-plugin/
    └── plugin.json
```

The directory name becomes the server's identifier in the marketplace and must match the `source` field in `marketplace.json`. For example:

| Directory Name | Source in marketplace.json | User-facing name |
|---------------|---------------------------|------------------|
| `cms-coverage` | `"source": "./cms-coverage"` | `cms-coverage` |
| `npi-registry` | `"source": "./npi-registry"` | `npi-registry` |
| `pubmed` | `"source": "./pubmed"` | `pubmed` |
| `icd10-codes` | `"source": "./icd10-codes"` | `icd10-codes` |

**Sources:** [.claude-plugin/marketplace.json:46-72](), [cms-coverage/.claude-plugin/plugin.json:1-15]()

The `.claude-plugin` subdirectory is mandatory and must contain exactly one file: `plugin.json`.

## Creating plugin.json

The `plugin.json` file defines the MCP server's connection configuration and metadata. It must be placed at `<mcp-server-name>/.claude-plugin/plugin.json`.

### Required Fields

```mermaid
graph LR
    PLUGIN["plugin.json"]
    
    NAME["name<br/>(string)"]
    VERSION["version<br/>(string)"]
    DESC["description<br/>(string)"]
    AUTHOR["author<br/>(object)"]
    MCP["mcpServers<br/>(object)"]
    
    PLUGIN --> NAME
    PLUGIN --> VERSION
    PLUGIN --> DESC
    PLUGIN --> AUTHOR
    PLUGIN --> MCP
    
    AUTHOR --> ANAME["author.name"]
    AUTHOR --> AURL["author.url"]
    
    MCP --> SERVER["Server Display Name"]
    SERVER --> TYPE["type: 'http'"]
    SERVER --> URL["url: 'https://...'"]
```

**Sources:** [icd10-codes/.claude-plugin/plugin.json:1-15](), [cms-coverage/.claude-plugin/plugin.json:1-15]()

### Configuration Template

The following template shows the complete structure with all required fields:

```json
{
  "name": "mcp-server-name",
  "version": "1.0.0",
  "description": "Brief description of what this MCP server provides",
  "author": {
    "name": "Organization Name",
    "url": "https://example.com"
  },
  "mcpServers": {
    "Display Name": {
      "type": "http",
      "url": "https://your-mcp-server.example.com/mcp"
    }
  }
}
```

**Sources:** [icd10-codes/.claude-plugin/plugin.json:1-15](), [npi-registry/.claude-plugin/plugin.json:1-15]()

### Field Specifications

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `name` | string | Identifier matching directory name | `"icd10-codes"` |
| `version` | string | Semantic version | `"1.0.0"` |
| `description` | string | Human-readable explanation of server capabilities | `"Access ICD-10-CM and ICD-10-PCS code sets"` |
| `author.name` | string | Organization or individual providing the server | `"deepsense.ai"` |
| `author.url` | string | Website URL for the provider | `"https://deepsense.ai"` |
| `mcpServers` | object | Dictionary of server configurations (typically one entry) | See below |

**Sources:** [icd10-codes/.claude-plugin/plugin.json:1-15](), [cms-coverage/.claude-plugin/plugin.json:1-15]()

### mcpServers Configuration

The `mcpServers` object contains one or more server definitions. Each key is a human-readable display name, and the value specifies connection details:

```json
"mcpServers": {
  "ICD10 Codes": {
    "type": "http",
    "url": "https://mcp.deepsense.ai/icd10_codes/mcp"
  }
}
```

**Current Implementation Patterns:**

All four existing MCP servers use `"type": "http"` with HTTPS endpoints:

| MCP Server | Display Name | URL Pattern |
|-----------|--------------|-------------|
| `icd10-codes` | `"ICD10 Codes"` | `https://mcp.deepsense.ai/icd10_codes/mcp` |
| `cms-coverage` | `"CMS Coverage"` | `https://mcp.deepsense.ai/cms_coverage/mcp` |
| `npi-registry` | `"NPI Registry"` | `https://mcp.deepsense.ai/npi_registry/mcp` |
| `pubmed` | `"PubMed"` | `https://pubmed.mcp.claude.com/mcp` |

**Sources:** [icd10-codes/.claude-plugin/plugin.json:9-14](), [cms-coverage/.claude-plugin/plugin.json:9-14](), [npi-registry/.claude-plugin/plugin.json:9-14](), [pubmed/.claude-plugin/plugin.json:9-14]()

The `/mcp` suffix in URLs is a convention used by the existing servers but not technically required.

## Registering in marketplace.json

After creating the `plugin.json` file, register the MCP server in the marketplace registry at [.claude-plugin/marketplace.json:1-74]().

### Marketplace Entry Structure

Add a new entry to the `plugins` array:

```json
{
  "name": "your-mcp-name",
  "source": "./your-mcp-name",
  "description": "User-facing description",
  "category": "healthcare",
  "tags": ["tag1", "tag2", "tag3"]
}
```

**Sources:** [.claude-plugin/marketplace.json:45-72]()

### Field Requirements

| Field | Required | Purpose | Notes |
|-------|----------|---------|-------|
| `name` | Yes | Unique identifier | Must match directory name |
| `source` | Yes | Relative path to MCP directory | Must be `"./<directory-name>"` |
| `description` | Yes | User-visible summary | Keep under 200 characters |
| `category` | Yes | Marketplace category | Use `"healthcare"` for this marketplace |
| `tags` | Yes | Searchable keywords | Array of lowercase strings |
| `skills` | No | **Omit for MCP servers** | Only present for skill entries |
| `strict` | No | **Omit for MCP servers** | Only relevant for skills |

**Sources:** [.claude-plugin/marketplace.json:45-72]()

### Distinguishing MCP Server Entries from Skill Entries

The critical difference between skill entries and MCP server entries in `marketplace.json` is the presence of the `skills` array:

```mermaid
graph TD
    ENTRY["marketplace.json plugin entry"]
    
    HAS_SKILLS{"Has 'skills' array?"}
    
    ENTRY --> HAS_SKILLS
    
    HAS_SKILLS -->|Yes| SKILL["Skill Entry<br/>source points to repo root<br/>skills array lists skill paths"]
    HAS_SKILLS -->|No| MCP["MCP Server Entry<br/>source points to subdirectory<br/>containing plugin.json"]
    
    SKILL_EX["Example:<br/>{<br/>  'name': 'fhir-developer',<br/>  'source': './',<br/>  'skills': ['./fhir-developer-skill']<br/>}"]
    
    MCP_EX["Example:<br/>{<br/>  'name': 'cms-coverage',<br/>  'source': './cms-coverage',<br/>  (no skills field)<br/>}"]
    
    SKILL --> SKILL_EX
    MCP --> MCP_EX
```

**Sources:** [.claude-plugin/marketplace.json:11-72]()

MCP server entries must:
- **Not** include a `skills` array
- **Not** include a `strict` field
- Use `source` pointing to a subdirectory (e.g., `"./cms-coverage"`)

Skill entries must:
- Include a `skills` array with at least one path
- Use `source` pointing to repository root (`"./"`)
- May include a `strict` field

### Example MCP Server Registration

Here is the complete marketplace entry for the ICD-10 MCP server:

```json
{
  "name": "icd10-codes",
  "source": "./icd10-codes",
  "description": "Access ICD-10-CM and ICD-10-PCS code sets",
  "category": "healthcare",
  "tags": ["icd-10", "diagnosis", "procedure", "billing", "medical-coding"]
}
```

**Sources:** [.claude-plugin/marketplace.json:66-72]()

Note the absence of `skills`, `strict`, and other skill-specific fields.

## MCP Server Types

The MCP protocol supports multiple transport types. The healthcare marketplace currently uses only the HTTP type.

### HTTP Type

All existing MCP servers use `"type": "http"` with HTTPS endpoints hosted on external infrastructure:

```mermaid
graph LR
    CLIENT["Claude Client"]
    MCP_HTTP["HTTP MCP Server<br/>type: 'http'<br/>url: 'https://...'"]
    BACKEND["Backend Service<br/>(Database, API, etc.)"]
    
    CLIENT -->|"HTTPS Requests<br/>(MCP protocol over HTTP)"| MCP_HTTP
    MCP_HTTP -->|"Internal queries"| BACKEND
    MCP_HTTP -->|"JSON Responses"| CLIENT
```

**Sources:** [icd10-codes/.claude-plugin/plugin.json:10-13](), [cms-coverage/.claude-plugin/plugin.json:10-13]()

The HTTP type requires:
- A publicly accessible HTTPS endpoint
- MCP protocol implementation at the endpoint
- No local process management (server runs independently)

### Infrastructure Hosting Patterns

Current MCP servers are hosted on two infrastructure providers:

| Provider | Servers | URL Pattern |
|----------|---------|-------------|
| DeepSense.ai | `cms-coverage`, `npi-registry`, `icd10-codes` | `https://mcp.deepsense.ai/<server>/mcp` |
| Claude Infrastructure | `pubmed` | `https://pubmed.mcp.claude.com/mcp` |

**Sources:** [cms-coverage/.claude-plugin/plugin.json:12](), [npi-registry/.claude-plugin/plugin.json:12](), [icd10-codes/.claude-plugin/plugin.json:12](), [pubmed/.claude-plugin/plugin.json:12]()

When adding a new MCP server, you must:
1. Deploy the MCP server implementation to accessible infrastructure
2. Obtain an HTTPS endpoint
3. Configure the endpoint in `plugin.json`

## Discovery and Installation Flow

Users install MCP servers using the Claude CLI command. The installation flow resolves the two-tier configuration:

```mermaid
sequenceDiagram
    participant User
    participant CLI as "Claude CLI"
    participant Repo as "GitHub Repo<br/>anthropics/healthcare"
    participant Server as "MCP Server<br/>(External)"
    
    User->>CLI: claude mcp add-from-marketplace<br/>anthropics/healthcare/cms-coverage
    CLI->>Repo: Fetch marketplace.json
    Repo-->>CLI: {plugins: [{name: "cms-coverage",<br/>source: "./cms-coverage"}]}
    CLI->>Repo: Fetch cms-coverage/.claude-plugin/plugin.json
    Repo-->>CLI: {mcpServers: {"CMS Coverage":<br/>{type: "http", url: "https://..."}}}
    CLI->>CLI: Configure local MCP client
    CLI->>Server: Test connection
    Server-->>CLI: Connection successful
    CLI-->>User: MCP server 'cms-coverage' added
```

**Sources:** [.claude-plugin/marketplace.json:45-51](), [cms-coverage/.claude-plugin/plugin.json:1-15]()

The installation process:
1. Parses `marketplace.json` to find the entry matching `cms-coverage`
2. Uses the `source` field to locate `./cms-coverage/.claude-plugin/plugin.json`
3. Reads the `mcpServers` configuration from `plugin.json`
4. Configures the local MCP client with the HTTP endpoint
5. Tests connectivity to the external server

## Complete Example: Adding a New MCP Server

To add a hypothetical "FDA Drugs" MCP server that provides access to the FDA drug database:

### Step 1: Create Directory Structure

```
fda-drugs/
└── .claude-plugin/
    └── plugin.json
```

### Step 2: Create plugin.json

```json
{
  "name": "fda-drugs",
  "version": "1.0.0",
  "description": "Access FDA-approved drug information including indications, dosing, and safety data.",
  "author": {
    "name": "FDA Data Provider",
    "url": "https://example-fda-provider.com"
  },
  "mcpServers": {
    "FDA Drugs": {
      "type": "http",
      "url": "https://mcp.example.com/fda_drugs/mcp"
    }
  }
}
```

**Sources:** Template derived from [icd10-codes/.claude-plugin/plugin.json:1-15]()

### Step 3: Register in marketplace.json

Add to the `plugins` array in [.claude-plugin/marketplace.json:11-73]():

```json
{
  "name": "fda-drugs",
  "source": "./fda-drugs",
  "description": "Access FDA-approved drug information",
  "category": "healthcare",
  "tags": ["fda", "drugs", "medications", "pharmacology", "prescribing"]
}
```

**Sources:** Template derived from [.claude-plugin/marketplace.json:66-72]()

### Step 4: Commit and Deploy

1. Commit both files to the repository
2. Ensure the MCP server at `https://mcp.example.com/fda_drugs/mcp` is operational
3. Users can now install with: `claude mcp add-from-marketplace anthropics/healthcare/fda-drugs`

## Validation Checklist

Before submitting a new MCP server, verify:

| Check | Location | Requirement |
|-------|----------|-------------|
| Directory name matches | Directory, `marketplace.json`, `plugin.json` | All three must use identical naming |
| `.claude-plugin` subdirectory exists | `<mcp-name>/.claude-plugin/` | Exact spelling, lowercase |
| `plugin.json` is valid JSON | `<mcp-name>/.claude-plugin/plugin.json` | Syntax must be correct |
| All required fields present | `plugin.json` | `name`, `version`, `description`, `author`, `mcpServers` |
| MCP server URL is HTTPS | `plugin.json` `mcpServers.<name>.url` | Must use `https://` |
| No `skills` array in marketplace entry | `marketplace.json` | MCP servers omit this field |
| `source` points to subdirectory | `marketplace.json` | Must be `"./<mcp-name>"` |
| Tags are relevant and lowercase | `marketplace.json` | Improves discoverability |

**Sources:** [.claude-plugin/marketplace.json:45-72](), [icd10-codes/.claude-plugin/plugin.json:1-15]()

## Integration with Skills

Skills can declare dependencies on MCP servers in their `SKILL.md` files. However, the marketplace configuration does not enforce these dependencies - skills dynamically discover available MCP servers at runtime.

For example, the Prior Authorization Review skill uses three MCP servers but does not declare them in configuration files:

```mermaid
graph TD
    SKILL["prior-auth-review-skill<br/>(Skill)"]
    
    NPI["npi-registry<br/>(MCP Server)"]
    ICD["icd10-codes<br/>(MCP Server)"]
    CMS["cms-coverage<br/>(MCP Server)"]
    
    SKILL -->|"Runtime queries<br/>validate provider"| NPI
    SKILL -->|"Runtime queries<br/>validate diagnosis"| ICD
    SKILL -->|"Runtime queries<br/>check coverage"| CMS
    
    MARKET["marketplace.json"]
    
    MARKET -->|"Lists independently"| SKILL
    MARKET -->|"Lists independently"| NPI
    MARKET -->|"Lists independently"| ICD
    MARKET -->|"Lists independently"| CMS
```

**Sources:** Derived from architecture diagrams and [.claude-plugin/marketplace.json:23-72]()

Skills and MCP servers remain decoupled in the marketplace configuration, allowing:
- Independent versioning and deployment
- Skills to work with subset of available MCP servers
- MCP servers to be reused across multiple skills
- Users to install only the components they need

## Testing Your MCP Server

After configuration, test the MCP server using:

1. **Syntax validation:** Validate both JSON files using `jq` or similar tools
2. **Marketplace parsing:** Verify Claude CLI can parse the marketplace entry
3. **Server connectivity:** Ensure the HTTPS endpoint responds to MCP protocol requests
4. **Skill integration:** Test with skills that will consume the MCP server

The automated skill review workflow ([claude-skill-review.yml]()), documented in [Skill Review Workflow](#5.1), does not validate MCP server configurations. Manual testing is required.

**Sources:** Context from system architecture diagrams

---

**Related Documentation:**
- For creating skills that use MCP servers, see [Creating a New Skill](#6.1)
- For understanding when to create an MCP server vs a skill, see [Skills vs MCP Servers](#2.1)
- For the complete list of available MCP servers, see [MCP Servers and External Data](#4)

---

# Page: Testing and Quality Assurance

# Testing and Quality Assurance

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/claude-skill-review.yml](.github/workflows/claude-skill-review.yml)
- [clinical-trial-protocol-skill/README.md](clinical-trial-protocol-skill/README.md)
- [prior-auth-review-skill/README.md](prior-auth-review-skill/README.md)

</details>



## Purpose and Scope

This document explains the testing and quality assurance processes for contributing to the Healthcare Marketplace. It covers local testing practices for skills and the automated review system that ensures quality before merge. 

For information about creating new skills, see [Creating a New Skill](#6.1). For details on the complete CI/CD pipeline including releases, see [CI/CD and Automation](#5).

---

## Local Testing

Before submitting a pull request, developers should validate their skills locally to ensure functionality and compliance with marketplace standards.

### Testing Skill Functionality

Skills should be tested within the Claude Code environment to verify their behavior matches the documented workflow:

**For Skills with Sequential Steps (e.g., Clinical Trial Protocol)**

Test each waypoint in the workflow by executing steps individually and verifying the output files are created correctly. The clinical trial protocol skill creates intermediate waypoints like `intervention_metadata.json`, `01_clinical_research_summary.json`, and various markdown sections [clinical-trial-protocol-skill/README.md:36-44]().

```mermaid
graph LR
    Dev["Developer<br/>Local Machine"]
    Claude["Claude Code<br/>Environment"]
    
    Dev -->|"Installs skill locally"| Claude
    Claude -->|"Executes step 0"| Step0["intervention_metadata.json"]
    Claude -->|"Executes step 1"| Step1["01_clinical_research_summary.json"]
    Claude -->|"Executes step 2"| Step2["02_protocol_foundation.md"]
    
    Dev -->|"Verifies outputs"| Step0
    Dev -->|"Verifies outputs"| Step1
    Dev -->|"Verifies outputs"| Step2
    
    Step0 -.->|"Can resume from"| Claude
    Step1 -.->|"Can resume from"| Claude
    Step2 -.->|"Can resume from"| Claude
```

**For Skills with Subskills (e.g., Prior Authorization Review)**

Test each subskill independently, including human decision points. The prior authorization skill requires testing both automated assessment (Subskill 1) and human-confirmed decision finalization (Subskill 2) [prior-auth-review-skill/README.md:27-66]().

**For Skills with Sample Data**

Use provided sample files when available. The prior authorization skill includes sample cases in `assets/sample/` that skip certain MCP lookups while executing the full workflow [prior-auth-review-skill/README.md:71-77]().

Sources: [clinical-trial-protocol-skill/README.md](), [prior-auth-review-skill/README.md]()

### Validating SKILL.md Format

The `SKILL.md` file must follow marketplace conventions:

| Requirement | Description | Example |
|------------|-------------|---------|
| **Front Matter** | YAML metadata block with skill metadata | `name`, `description`, `tags`, `requirements` |
| **Installation Section** | Commands to install the skill | `/plugin install skill-name@healthcare` |
| **Usage Section** | Step-by-step usage instructions | Numbered workflow steps |
| **Disclaimers** | Required warnings for healthcare skills | Regulatory disclaimers, professional review requirements |

All skills containing healthcare decision support must include disclaimers stating that:
- Generated outputs are preliminary/draft only
- Professional review is required
- The tool does not substitute for medical/legal/regulatory advice

Sources: [clinical-trial-protocol-skill/README.md:19-34](), [prior-auth-review-skill/README.md:17-26]()

### Testing with MCP Servers

Skills that integrate MCP servers should be tested with actual MCP connections:

```mermaid
graph TB
    subgraph "Local Testing Environment"
        Skill["Skill Under Test"]
        Claude["Claude Code Client"]
    end
    
    subgraph "External MCP Servers"
        NPI["NPI Registry<br/>mcp.deepsense.ai/npi_registry"]
        ICD["ICD-10 Codes<br/>mcp.deepsense.ai/icd10_codes"]
        CMS["CMS Coverage<br/>mcp.deepsense.ai/cms_coverage"]
        PubMed["PubMed<br/>pubmed.mcp.claude.com"]
    end
    
    Claude -->|"Loads"| Skill
    Skill -->|"Calls MCP tools"| NPI
    Skill -->|"Calls MCP tools"| ICD
    Skill -->|"Calls MCP tools"| CMS
    Skill -->|"Calls MCP tools"| PubMed
    
    NPI -.->|"Returns data"| Skill
    ICD -.->|"Returns data"| Skill
    CMS -.->|"Returns data"| Skill
    PubMed -.->|"Returns data"| Skill
```

Verify that:
- MCP server connections are established successfully
- Tool calls return expected data formats
- Error handling works when MCP servers are unavailable
- Skills gracefully handle missing or incomplete MCP data

Sources: [prior-auth-review-skill/README.md:33-41](), [clinical-trial-protocol-skill/README.md:47-50]()

---

## Automated Quality Assurance

The marketplace uses automated skill reviews powered by Claude to ensure quality before merging changes. This system is implemented in the `claude-skill-review.yml` workflow.

### Workflow Overview

The skill review workflow executes on pull request events and consists of two jobs that run sequentially:

```mermaid
graph TB
    PR["Pull Request<br/>opened/synchronize/ready_for_review"]
    
    subgraph "detect-skills Job"
        Checkout1["actions/checkout@v4<br/>fetch-depth: 0"]
        GitDiff["git diff --name-only<br/>origin/base_ref...HEAD"]
        FindSkills["find . -name SKILL.md"]
        MatchChanges["Match changed files<br/>to skill directories"]
        Output["Output JSON array<br/>of affected skills"]
        
        Checkout1 --> GitDiff
        GitDiff --> FindSkills
        FindSkills --> MatchChanges
        MatchChanges --> Output
    end
    
    subgraph "review-skill Job"
        Matrix["Matrix Strategy<br/>skill: fromJson(skills)"]
        Checkout2["actions/checkout@v4"]
        ClaudeAction["anthropics/claude-code-action@v1"]
        Plugin["skill-creator plugin"]
        Review["Claude reviews skill<br/>using git diff"]
        Comment["gh pr comment<br/>Posts feedback"]
        
        Matrix --> Checkout2
        Checkout2 --> ClaudeAction
        ClaudeAction --> Plugin
        Plugin --> Review
        Review --> Comment
    end
    
    PR --> detect-skills
    Output -.->|"has_skills: true"| review-skill
```

Sources: [.github/workflows/claude-skill-review.yml:1-88]()

### The detect-skills Job

The `detect-skills` job identifies which skills have been modified in a pull request [.github/workflows/claude-skill-review.yml:12-53]().

**Skill Detection Algorithm:**

1. **Get Changed Files** - Uses `git diff` to list all files modified between the base branch and PR HEAD [.github/workflows/claude-skill-review.yml:27]()
2. **Discover Skills** - Finds all directories containing a `SKILL.md` file using `find` command [.github/workflows/claude-skill-review.yml:30]()
3. **Match Changes** - Iterates through skill directories and checks if any changed files belong to each skill [.github/workflows/claude-skill-review.yml:33-41]()
4. **Output JSON Array** - Produces a JSON array of affected skill paths and a boolean flag [.github/workflows/claude-skill-review.yml:44-52]()

```mermaid
flowchart TD
    Start["Start detect-skills"]
    GetDiff["Execute git diff<br/>--name-only origin/base...HEAD"]
    FindSkills["Execute find . -name SKILL.md<br/>Extract parent directories"]
    InitArray["Initialize empty array:<br/>affected_skills=()"]
    
    LoopSkills{"For each<br/>skill_dir"}
    LoopFiles{"For each<br/>changed file"}
    CheckMatch{"Does file path<br/>start with skill_dir?"}
    AddSkill["Add skill_dir to<br/>affected_skills array"]
    
    RemoveDupes["Remove duplicates<br/>using sort -u"]
    ConvertJSON["Convert to JSON using jq:<br/>jq -R -s -c 'split...'"]
    SetOutputs["Set GITHUB_OUTPUT:<br/>skills=json_array<br/>has_skills=true/false"]
    End["End detect-skills"]
    
    Start --> GetDiff
    GetDiff --> FindSkills
    FindSkills --> InitArray
    InitArray --> LoopSkills
    
    LoopSkills -->|"skill_dir"| LoopFiles
    LoopFiles -->|"file"| CheckMatch
    CheckMatch -->|"Yes"| AddSkill
    AddSkill --> LoopSkills
    CheckMatch -->|"No"| LoopFiles
    LoopFiles -->|"Done"| LoopSkills
    
    LoopSkills -->|"Done"| RemoveDupes
    RemoveDupes --> ConvertJSON
    ConvertJSON --> SetOutputs
    SetOutputs --> End
```

**Job Outputs:**

| Output | Type | Purpose |
|--------|------|---------|
| `skills` | JSON array | List of skill directory paths (e.g., `["clinical-trial-protocol-skill"]`) |
| `has_skills` | boolean | Whether any skills were modified (gates the review-skill job) |

Sources: [.github/workflows/claude-skill-review.yml:12-53]()

### The review-skill Job

The `review-skill` job executes Claude-powered reviews for each affected skill using a matrix strategy [.github/workflows/claude-skill-review.yml:55-88]().

**Matrix Strategy Configuration:**

```yaml
strategy:
  matrix:
    skill: ${{ fromJson(needs.detect-skills.outputs.skills) }}
  fail-fast: false
```

This configuration creates parallel jobs for each skill, allowing multiple skills to be reviewed simultaneously without blocking each other [.github/workflows/claude-skill-review.yml:59-62]().

**Claude Code Action Integration:**

The job uses `anthropics/claude-code-action@v1` with the following configuration [.github/workflows/claude-skill-review.yml:75-87]():

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `claude_code_oauth_token` | Secret | Authenticates with Claude Code service |
| `plugin_marketplaces` | `https://github.com/anthropics/skills.git` | Loads skill-creator plugin marketplace |
| `plugins` | `example-skills@anthropic-agent-skills` | Installs skill-creator plugin |
| `claude_args` | Allowed tools configuration | Permits Bash, Read, Glob, Grep, Skill tools |
| `prompt` | Review instructions | Directs Claude to review the specific skill |

**Review Process:**

```mermaid
sequenceDiagram
    participant GHA as "GitHub Actions"
    participant CCA as "claude-code-action@v1"
    participant Claude as "Claude AI"
    participant Plugin as "skill-creator plugin"
    participant GitHub as "GitHub API"
    
    GHA->>CCA: Trigger with skill path
    CCA->>Claude: Load marketplace and plugins
    Claude->>Plugin: Load skill-creator
    
    Note over Claude,Plugin: Prompt: "Review the {skill} skill in PR #{number}"
    
    Claude->>GHA: Execute git diff origin/base -- skill/
    GHA-->>Claude: Return changed files
    
    Claude->>Plugin: Use skill-creator review capabilities
    Plugin->>Claude: Analyze SKILL.md structure
    Plugin->>Claude: Validate requirements
    Plugin->>Claude: Check documentation quality
    
    Claude->>GitHub: gh pr comment {feedback}
    GitHub-->>GHA: Comment posted
```

**Allowed Tools:**

The workflow grants Claude access to specific tools [.github/workflows/claude-skill-review.yml:81]():

- **Bash(gh pr comment:*)** - Post comments to the pull request
- **Bash(git:*)** - Execute git commands to inspect changes
- **Read** - Read file contents
- **Glob** - Find files matching patterns
- **Grep** - Search file contents
- **Skill** - Use the skill-creator plugin for review

**Permissions:**

The job requires the following GitHub permissions [.github/workflows/claude-skill-review.yml:63-67]():

```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write
  id-token: write
```

Sources: [.github/workflows/claude-skill-review.yml:55-88]()

---

## Interpreting Review Feedback

Claude posts review feedback as pull request comments with the skill name in the header. Feedback typically covers:

### Structure and Format

- **SKILL.md completeness** - Presence of required sections (installation, usage, requirements)
- **Front matter validity** - YAML metadata format and required fields
- **Markdown syntax** - Proper heading hierarchy, code blocks, tables

### Documentation Quality

- **Clarity** - Instructions are clear and unambiguous
- **Completeness** - All workflow steps are documented
- **Accuracy** - Requirements match actual dependencies
- **Disclaimers** - Healthcare skills include necessary warnings

### Technical Correctness

- **MCP integration** - Proper use of MCP server tools
- **File paths** - References to scripts, templates, and waypoint files are correct
- **Dependencies** - Python packages, external services listed accurately

### Best Practices

- **Modularity** - Skills follow waypoint or subskill patterns for resumability
- **Error handling** - Skills handle missing data or failed MCP calls gracefully
- **Human oversight** - Decision points are clearly marked for skills involving clinical judgment

**Responding to Feedback:**

1. **Address all comments** - Make requested changes or explain why changes aren't needed
2. **Re-push commits** - The workflow automatically re-reviews on new commits
3. **Request clarification** - Use PR comments to ask questions about feedback
4. **Resolve conversations** - Mark GitHub conversations as resolved once addressed

Sources: [.github/workflows/claude-skill-review.yml:82-87]()

---

## Quality Standards and Best Practices

### Documentation Standards

| Standard | Requirement | Example |
|----------|-------------|---------|
| **Disclaimers** | All healthcare decision support skills must include regulatory disclaimers | "PRELIMINARY PROTOCOL ONLY", "HUMAN REVIEW REQUIRED" |
| **Professional Review** | Must state that professional consultation is required | "Professional consultation with clinical trial experts... is essential" |
| **Not Medical Advice** | Must clarify the tool does not substitute professional advice | "Generated protocols do not substitute for professional biostatistician review" |
| **Requirements** | List all dependencies clearly | Python packages, MCP servers, external services |

### Workflow Design Standards

**Waypoint Pattern (for multi-step processes):**

Skills with long workflows should use waypoints to enable resumption and avoid token limits:

- Each step produces a named output file (JSON or Markdown)
- Steps can be executed independently
- Workflow can resume from any waypoint
- Waypoint files use consistent naming (e.g., `00_`, `01_`, `02_` prefixes)

Example: Clinical Trial Protocol skill [clinical-trial-protocol-skill/README.md:36-44]()

**Subskill Pattern (for human-in-the-loop processes):**

Skills requiring human decisions should separate automated analysis from decision execution:

- Subskill 1: Automated assessment, generates recommendation
- Human decision point: Review and confirm
- Subskill 2: Execute decision, generate outputs

Example: Prior Authorization Review skill [prior-auth-review-skill/README.md:27-66]()

### MCP Integration Standards

When integrating MCP servers:

1. **Document requirements** - List all MCP servers in SKILL.md requirements section
2. **Validate data** - Check MCP responses for required fields before using
3. **Handle errors** - Gracefully handle MCP unavailability or incomplete data
4. **Batch operations** - Use batch validation when processing multiple codes (e.g., ICD-10)

```mermaid
graph LR
    Skill["Skill Logic"]
    Check{"MCP<br/>available?"}
    Call["Call MCP tool"]
    Validate{"Response<br/>valid?"}
    Process["Process data"]
    Fallback["Use fallback<br/>or skip"]
    Error["Log error<br/>and continue"]
    
    Skill --> Check
    Check -->|"Yes"| Call
    Check -->|"No"| Fallback
    Call --> Validate
    Validate -->|"Yes"| Process
    Validate -->|"No"| Error
    Error --> Fallback
```

### Testing Before Submission

Complete the following checklist before submitting a pull request:

- [ ] Skill executes successfully in Claude Code environment
- [ ] All workflow steps produce expected outputs
- [ ] SKILL.md includes all required sections
- [ ] Healthcare disclaimers are present and prominent
- [ ] MCP server dependencies are listed in requirements
- [ ] Sample data (if applicable) works correctly
- [ ] Waypoint files use consistent naming
- [ ] Human decision points are clearly documented
- [ ] Skill is registered in `.claude-plugin/marketplace.json`

Sources: [clinical-trial-protocol-skill/README.md](), [prior-auth-review-skill/README.md](), [.github/workflows/claude-skill-review.yml]()