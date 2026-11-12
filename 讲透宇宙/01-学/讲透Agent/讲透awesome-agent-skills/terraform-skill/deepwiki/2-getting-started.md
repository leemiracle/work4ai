<!-- source: DeepWiki mcp.deepwiki.com · repo antonbabenko/terraform-skill · page 2 Getting Started · fetched 2026-10-26 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [README.md](README.md)

</details>



## Purpose and Scope

This document provides an overview of how to install and begin using the terraform-skill in Claude Code. It covers the initial setup process, verification steps, and your first interactions with the skill. For detailed installation procedures, see [Installation](#2.1). For comprehensive usage patterns and activation triggers, see [Using the Skill](#2.2).

---

## Installation Overview

The terraform-skill is distributed through the Claude Code marketplace and can be installed using either the marketplace command or manual installation methods. The skill uses [.claude-plugin/marketplace.json:1-29]() as its plugin definition file, which Claude Code reads to discover and activate the skill.

### Installation Methods

There are three primary installation methods, listed in order of recommendation:

| Method | Command | Use Case |
|--------|---------|----------|
| **Marketplace Install** | `/plugin marketplace add antonbabenko/terraform-skill` | Production use, automatic updates |
| **Direct Install** | `/plugin install terraform-skill@antonbabenko` | After marketplace add |
| **Manual Clone** | `git clone https://github.com/antonbabenko/terraform-skill ~/.claude/skills/terraform-skill` | Development, testing, offline use |

The marketplace installation method automatically handles version updates and ensures the skill is properly registered with Claude Code. Manual installation requires placing the repository in Claude's skills directory (`~/.claude/skills/`).

**Sources:** [README.md:38-63]()

---

## Installation Workflow

The following diagram illustrates how the skill is discovered and loaded by Claude Code during installation:

```mermaid
graph TB
    subgraph "Installation Phase"
        USER["User executes:<br/>/plugin marketplace add<br/>antonbabenko/terraform-skill"]
        CLONE["Claude Code clones repository<br/>to ~/.claude/skills/terraform-skill"]
        DISCOVER["Scan for<br/>.claude-plugin/marketplace.json"]
    end
    
    subgraph "Registration Phase"
        PARSE["Parse marketplace.json<br/>Extract metadata fields:<br/>- name: antonbabenko<br/>- version: 1.5.0<br/>- plugins array"]
        REGISTER["Register plugin:<br/>name: terraform-skill<br/>description: Use when working with...<br/>keywords: terraform, opentofu, etc."]
        INDEX["Index activation triggers:<br/>- Terraform<br/>- OpenTofu<br/>- modules<br/>- testing<br/>- CI/CD"]
    end
    
    subgraph "Content Loading"
        LOCATE["Locate skill content:<br/>source: ./"]
        READY["Skill ready:<br/>SKILL.md available<br/>references/*.md on-demand"]
    end
    
    USER --> CLONE
    CLONE --> DISCOVER
    DISCOVER --> PARSE
    PARSE --> REGISTER
    REGISTER --> INDEX
    INDEX --> LOCATE
    LOCATE --> READY
    
    READY --> AVAILABLE["Skill available for queries"]
```

**Sources:** [.claude-plugin/marketplace.json:1-29](), [README.md:38-54]()

---

## Skill Discovery and Activation

Once installed, Claude Code uses the plugin metadata to determine when to activate the skill. The activation logic is defined in [.claude-plugin/marketplace.json:14-16]():

```mermaid
flowchart LR
    subgraph "User Query Space"
        Q1["Create a Terraform module"]
        Q2["Write OpenTofu tests"]
        Q3["Setup CI/CD pipeline"]
        Q4["Review IaC configuration"]
        Q5["Debug state issues"]
    end
    
    subgraph "Keyword Matching Engine"
        KEYWORDS["Keywords from marketplace.json:18-24<br/>- terraform<br/>- opentofu<br/>- infrastructure-as-code<br/>- testing<br/>- ci-cd<br/>- modules"]
        DESC["Description triggers from line 15:<br/>- creating modules<br/>- writing tests<br/>- setting up CI/CD pipelines<br/>- reviewing configurations<br/>- debugging state issues"]
    end
    
    subgraph "Activation Decision"
        MATCH["Match detected"]
        LOAD["Load SKILL.md"]
        CONTEXT["Add to Claude context:<br/>~4.4K tokens core content"]
    end
    
    Q1 --> KEYWORDS
    Q2 --> KEYWORDS
    Q3 --> DESC
    Q4 --> DESC
    Q5 --> DESC
    
    KEYWORDS --> MATCH
    DESC --> MATCH
    MATCH --> LOAD
    LOAD --> CONTEXT
```

**Sources:** [.claude-plugin/marketplace.json:14-25]()

---

## Verification Steps

After installation, verify that the skill is properly configured and accessible:

### 1. Check Installation Status

```bash
# List installed skills
/plugin list
```

Expected output should include `terraform-skill@antonbabenko` with version `1.5.0` or later.

### 2. Test Skill Activation

Use one of the recommended test queries from [README.md:66-70]():

```
"Create a Terraform module with testing for an S3 bucket"
```

Claude should respond using Terraform best practices and module structure patterns from the skill content.

### 3. Verify Content Loading

The skill uses a progressive disclosure pattern (see [Progressive Disclosure Pattern](#3.2)). On first activation, Claude loads:

| Content Layer | Size | Source File |
|--------------|------|-------------|
| **Metadata** | ~100 tokens | `.claude-plugin/marketplace.json` |
| **Core Skill** | ~4.4K tokens | `SKILL.md` |
| **References** (on-demand) | 0-7K tokens | `references/*.md` |

**Sources:** [README.md:65-72]()

---

## First Interactions

### Example Query Patterns

The skill is designed to respond to various Terraform/OpenTofu development tasks. Here are common interaction patterns from [README.md:74-86]():

| Task Category | Example Query | Expected Skill Behavior |
|--------------|---------------|------------------------|
| **Module Creation** | "Create a Terraform module for AWS VPC with native tests" | Provides module structure, naming conventions, test framework setup |
| **Code Review** | "Review this Terraform configuration following best practices" | Analyzes against patterns from `SKILL.md` and `references/code-patterns.md` |
| **CI/CD Setup** | "Create a GitHub Actions workflow for Terraform with cost estimation" | Generates workflow from `references/ci-cd-workflows.md` templates |
| **Testing Strategy** | "Help me choose between native tests and Terratest for my modules" | Provides decision matrix from testing strategy framework |

### Response Flow

```mermaid
sequenceDiagram
    participant U as "User"
    participant C as "Claude Code"
    participant MP as "marketplace.json"
    participant SK as "SKILL.md"
    participant RF as "references/*.md"
    
    U->>C: "Create a module with tests"
    C->>MP: "Check activation triggers"
    MP-->>C: "Match: 'modules', 'tests'"
    C->>SK: "Load core content"
    SK-->>C: "Testing Strategy Framework<br/>Module Development Patterns"
    
    Note over C: "Determine if deep dive needed"
    
    C->>RF: "Load module-patterns.md<br/>(on-demand)"
    RF-->>C: "+7K tokens module guidance"
    
    C->>U: "Response with:<br/>- Module structure<br/>- Test framework choice<br/>- Example code"
```

**Sources:** [README.md:74-86](), [.claude-plugin/marketplace.json:14-16]()

---

## File Structure Mapping

Understanding where the skill content resides helps with troubleshooting and local development:

```mermaid
graph LR
    subgraph "Installation Directory"
        ROOT["~/.claude/skills/terraform-skill/"]
    end
    
    subgraph "Plugin Definition"
        MP["/.claude-plugin/marketplace.json<br/>Plugin metadata, version 1.5.0<br/>Activation triggers"]
    end
    
    subgraph "Core Content"
        SKILL["/SKILL.md<br/>~4.4K tokens<br/>Always loaded on activation"]
    end
    
    subgraph "Reference Library"
        REF_DIR["/references/"]
        MOD["module-patterns.md<br/>~7K tokens"]
        QUICK["quick-reference.md<br/>~3.8K tokens"]
        CODE["code-patterns.md<br/>~5.1K tokens"]
        CI["ci-cd-workflows.md<br/>~2.3K tokens"]
        SEC["security-compliance.md<br/>~2.5K tokens"]
    end
    
    subgraph "Documentation"
        README["/README.md<br/>Installation guide<br/>Quick start examples"]
    end
    
    ROOT --> MP
    ROOT --> SKILL
    ROOT --> REF_DIR
    ROOT --> README
    
    REF_DIR --> MOD
    REF_DIR --> QUICK
    REF_DIR --> CODE
    REF_DIR --> CI
    REF_DIR --> SEC
    
    MP -.->|"source: ./"| SKILL
```

**Sources:** [.claude-plugin/marketplace.json:16](), [README.md:1-212]()

---

## Troubleshooting Initial Setup

### Skill Not Found

If Claude doesn't recognize the skill after installation:

1. Verify the installation directory exists: `ls -la ~/.claude/skills/terraform-skill/`
2. Check that `.claude-plugin/marketplace.json` is present
3. Restart Claude Code to refresh the skill index

### Skill Not Activating

If queries don't trigger the skill:

1. Use explicit keyword triggers from [.claude-plugin/marketplace.json:18-24]()
2. Try queries that match the description pattern in [.claude-plugin/marketplace.json:15]()
3. Check Claude Code logs for activation errors

### Outdated Content

The skill version is defined in [.claude-plugin/marketplace.json:6]() and [.claude-plugin/marketplace.json:26](). If you need the latest version:

```bash
# For marketplace installations
/plugin update terraform-skill@antonbabenko

# For manual installations
cd ~/.claude/skills/terraform-skill
git pull origin master
```

**Sources:** [.claude-plugin/marketplace.json:6](), [.claude-plugin/marketplace.json:18-26]()

---

## Next Steps

After successful installation and verification:

- **Learn Usage Patterns**: See [Using the Skill](#2.2) for detailed interaction examples and activation triggers
- **Explore Content**: Review [Core Skill Content](#4.1) to understand available guidance topics
- **Integration**: See [CI/CD Workflows](#4.5) for pipeline integration examples
- **Advanced Topics**: Explore [Module Development Patterns](#4.2) and [Security & Compliance](#4.6)

For local development and contributions, see [Development Guide](#5).

**Sources:** [README.md:1-212]()

---

