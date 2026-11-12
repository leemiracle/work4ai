# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [README.md](README.md)
- [SKILL.md](SKILL.md)

</details>



This document provides a high-level introduction to **terraform-skill**, a Claude skill that delivers Terraform and OpenTofu best practices guidance directly within Claude Code. It explains the system's purpose, architecture, and how it provides progressive, context-aware infrastructure-as-code expertise.

**Scope:** This overview covers the system's purpose, integration model, and architectural approach. For detailed information on specific topics, see:
- Installation and usage instructions: [Getting Started](#2)
- Technical architecture details: [Core Architecture](#3)
- Content organization and knowledge base: [Knowledge Base](#4)
- Development and contribution process: [Development Guide](#5)

---

## System Purpose

terraform-skill is a **skill plugin for Claude Code** that provides comprehensive Terraform and OpenTofu guidance. It delivers:

- **Context-aware expertise** - Automatically activated when working with Terraform/OpenTofu code
- **Progressive disclosure** - Loads detailed information only when needed to optimize token usage
- **Production-tested patterns** - Based on terraform-best-practices.com and enterprise experience
- **Version-specific guidance** - Covers Terraform 1.0+ and OpenTofu 1.6+ features

The system operates as a **knowledge base with intelligent routing**, using a three-tier progressive disclosure pattern to provide 56-70% token reduction compared to loading all content upfront.

**Sources:** [.claude-plugin/marketplace.json:1-29](), [SKILL.md:1-17](), [README.md:1-8]()

---

## Integration Model

### Claude Code Skill System

The following diagram shows how terraform-skill integrates into the Claude Code environment:

```mermaid
graph TB
    subgraph "Claude Code Environment"
        USER["User Query"]
        CLAUDE["Claude AI Agent"]
        SKILLS_DIR["~/.claude/skills/"]
    end
    
    subgraph "terraform-skill Repository"
        MARKETPLACE[".claude-plugin/marketplace.json<br/>Plugin Definition"]
        SKILL_MD["SKILL.md<br/>Core Content (~4.4K tokens)"]
        REFERENCES["references/*.md<br/>Detailed Guides (~24K tokens)"]
    end
    
    subgraph "Discovery & Activation"
        METADATA["Metadata Scan<br/>name, description, keywords"]
        TRIGGERS["Activation Triggers<br/>terraform, opentofu, testing, ci-cd"]
    end
    
    USER --> CLAUDE
    CLAUDE --> SKILLS_DIR
    SKILLS_DIR --> MARKETPLACE
    
    MARKETPLACE --> METADATA
    METADATA --> TRIGGERS
    
    TRIGGERS -->|"Match: Working with Terraform/OpenTofu"| SKILL_MD
    SKILL_MD -.->|"On-demand load"| REFERENCES
    
    CLAUDE -->|"Uses loaded content"| RESPONSE["Response with<br/>Best Practices"]
```

**Discovery Process:**

1. **Plugin Definition** - [.claude-plugin/marketplace.json:12-28]() defines the skill metadata:
   - `name`: "terraform-skill"
   - `description`: Activation criteria for Claude
   - `keywords`: ["terraform", "opentofu", "infrastructure-as-code", "testing", "ci-cd", "modules"]
   - `source`: "./" - Points to repository root

2. **Activation Triggers** - [SKILL.md:14-28]() specifies when to activate:
   - Creating Terraform/OpenTofu configurations or modules
   - Setting up testing infrastructure
   - Implementing CI/CD for IaC
   - Reviewing or refactoring Terraform projects

3. **Content Loading** - Progressive three-stage loading:
   - Stage 1: Metadata (~100 tokens)
   - Stage 2: Core SKILL.md (~4,400 tokens)
   - Stage 3: References on-demand (0-7K tokens per file)

**Sources:** [.claude-plugin/marketplace.json:1-29](), [SKILL.md:1-17](), [README.md:40-72]()

---

## System Architecture

### Component Overview

The following diagram maps the system's file structure to functional components:

```mermaid
graph TB
    subgraph "Integration Layer"
        MARKETPLACE_JSON[".claude-plugin/marketplace.json<br/>Version: 1.5.0<br/>Importance: 28.17"]
    end
    
    subgraph "Core Content Layer"
        SKILL_MD["SKILL.md<br/>~4,400 tokens<br/>Importance: 10.14"]
        
        subgraph "Core Sections"
            WHEN_USE["When to Use (lines 14-28)"]
            PRINCIPLES["Core Principles (lines 30-66)"]
            TESTING["Testing Strategy (lines 116-172)"]
            STRUCTURE["Code Structure (lines 173-227)"]
            MODULES["Module Development (lines 315-350)"]
            CICD["CI/CD Integration (lines 352-370)"]
            SECURITY["Security & Compliance (lines 372-397)"]
        end
    end
    
    subgraph "Reference Layer - Progressive Disclosure"
        REF_MODULE["references/module-patterns.md<br/>~7K tokens<br/>Importance: 2.70"]
        REF_QUICK["references/quick-reference.md<br/>~3.8K tokens<br/>Importance: 2.70"]
        REF_CODE["references/code-patterns.md<br/>~5.1K tokens<br/>Importance: 2.00"]
        REF_CICD["references/ci-cd-workflows.md<br/>~2.3K tokens<br/>Importance: 0.70"]
        REF_SEC["references/security-compliance.md<br/>~2.5K tokens<br/>Importance: 0.70"]
    end
    
    subgraph "Documentation Layer"
        README_MD["README.md<br/>User Documentation<br/>Importance: 6.24"]
        CLAUDE_MD["CLAUDE.md<br/>Contributor Guide<br/>Importance: 2.94"]
    end
    
    MARKETPLACE_JSON -->|"defines"| SKILL_MD
    
    SKILL_MD --> WHEN_USE
    SKILL_MD --> PRINCIPLES
    SKILL_MD --> TESTING
    SKILL_MD --> STRUCTURE
    SKILL_MD --> MODULES
    SKILL_MD --> CICD
    SKILL_MD --> SECURITY
    
    TESTING -.->|"line 170: references"| REF_QUICK
    STRUCTURE -.->|"line 227: references"| REF_CODE
    MODULES -.->|"line 349: references"| REF_MODULE
    CICD -.->|"line 369: references"| REF_CICD
    SECURITY -.->|"line 397: references"| REF_SEC
    
    README_MD -.->|"documents"| MARKETPLACE_JSON
    CLAUDE_MD -.->|"guides development of"| SKILL_MD
```

**Component Responsibilities:**

| Component | Purpose | Token Budget | When Loaded |
|-----------|---------|--------------|-------------|
| `marketplace.json` | Plugin discovery & metadata | ~100 | Always (by Claude) |
| `SKILL.md` | Core patterns & decision frameworks | ~4,400 | On skill activation |
| `module-patterns.md` | Detailed module guidance | ~7,000 | Complex module questions |
| `quick-reference.md` | Command cheat sheets | ~3,800 | Command lookup |
| `code-patterns.md` | Version-specific features | ~5,100 | Modern Terraform features |
| `ci-cd-workflows.md` | Pipeline templates | ~2,300 | Pipeline setup |
| `security-compliance.md` | Security hardening | ~2,500 | Security scanning |

**Sources:** [.claude-plugin/marketplace.json:1-29](), [SKILL.md:1-517](), [README.md:1-212]()

---

## Progressive Disclosure Architecture

The system implements a **three-tier progressive disclosure pattern** to optimize token usage:

```mermaid
graph LR
    subgraph "Tier 1: Discovery"
        QUERY["User Query:<br/>Create Terraform module"]
        SCAN["Scan marketplace.json<br/>~100 tokens"]
    end
    
    subgraph "Tier 2: Core Guidance"
        CORE_LOAD["Load SKILL.md<br/>~4,400 tokens"]
        
        subgraph "Core Content Sections"
            SEC_WHEN["When to Use (14-28)"]
            SEC_PRINCIPLES["Core Principles (30-66)"]
            SEC_TESTING["Testing Strategy (116-172)"]
            SEC_MODULES["Module Development (315-350)"]
        end
    end
    
    subgraph "Tier 3: Deep Dive"
        DETAIL_LOAD["Load references/*.md<br/>0-7K tokens per file"]
        
        subgraph "Reference Files"
            REF_MOD["module-patterns.md"]
            REF_QUICK["quick-reference.md"]
            REF_CODE["code-patterns.md"]
        end
    end
    
    QUERY --> SCAN
    SCAN -->|"Keywords match"| CORE_LOAD
    
    CORE_LOAD --> SEC_WHEN
    CORE_LOAD --> SEC_PRINCIPLES
    CORE_LOAD --> SEC_TESTING
    CORE_LOAD --> SEC_MODULES
    
    SEC_MODULES -.->|"Need detailed patterns"| REF_MOD
    SEC_TESTING -.->|"Need command reference"| REF_QUICK
    SEC_PRINCIPLES -.->|"Need version-specific features"| REF_CODE
    
    REF_MOD --> DETAIL_LOAD
    REF_QUICK --> DETAIL_LOAD
    REF_CODE --> DETAIL_LOAD
```

**Token Efficiency:**

- **Total available content:** ~30,400 tokens (all files)
- **Typical query usage:** 4,500-12,000 tokens (15-40% of total)
- **Token savings:** 56-70% vs loading all content upfront

**Reference Mechanism:**

[SKILL.md:499-510]() provides explicit links to reference files:
- Line 505: "Testing Frameworks" → `references/testing-frameworks.md`
- Line 506: "Module Patterns" → `references/module-patterns.md`
- Line 507: "CI/CD Workflows" → `references/ci-cd-workflows.md`
- Line 508: "Security & Compliance" → `references/security-compliance.md`
- Line 509: "Quick Reference" → `references/quick-reference.md`

**Sources:** [SKILL.md:499-510](), [.claude-plugin/marketplace.json:1-29]()

---

## Content Distribution

The following table shows how the ~30.4K tokens of content are distributed across files:

| File | Primary Topic | Token Count | Importance Score | Load Trigger |
|------|---------------|-------------|------------------|--------------|
| `SKILL.md` | Core patterns & frameworks | ~4,400 | 10.14 | Skill activation |
| `module-patterns.md` | Module architecture | ~7,000 | 2.70 | Module questions |
| `code-patterns.md` | Modern features & refactoring | ~5,100 | 2.00 | Version-specific queries |
| `quick-reference.md` | Commands & troubleshooting | ~3,800 | 2.70 | Command lookup |
| `ci-cd-workflows.md` | Pipeline templates | ~2,300 | 0.70 | CI/CD setup |
| `security-compliance.md` | Security scanning | ~2,500 | 0.70 | Security questions |

**Content Structure in SKILL.md:**

[SKILL.md:1-517]() organizes core content into:
1. **Lines 14-28:** Activation criteria and use cases
2. **Lines 30-313:** Core principles (module hierarchy, naming, locals)
3. **Lines 116-172:** Testing strategy framework
4. **Lines 173-227:** Code structure standards
5. **Lines 229-313:** Count vs for_each patterns
6. **Lines 315-350:** Module development practices
7. **Lines 352-370:** CI/CD integration overview
8. **Lines 372-397:** Security & compliance essentials
9. **Lines 399-431:** Version management
10. **Lines 433-476:** Modern Terraform features by version

**Sources:** [SKILL.md:1-517](), High-level system diagrams

---

## Key Capabilities Summary

terraform-skill provides comprehensive guidance across five major areas. For detailed coverage, see [Key Capabilities](#1.2).

### Testing Frameworks

- **Decision matrices:** When to use native tests vs Terratest
- **Testing pyramid:** Static → Integration → E2E
- **Version-specific guidance:** Terraform 1.6+ native testing, 1.7+ mock providers

[SKILL.md:116-172]() provides the testing strategy framework with cost optimization patterns.

### Module Development

- **Hierarchy patterns:** Resource → Resource Module → Infrastructure Module → Composition
- **Naming conventions:** Use of "this" for singletons, descriptive names for multiples
- **Best practices:** Variable design, output patterns, documentation standards

[SKILL.md:315-350]() covers core module practices with links to [references/module-patterns.md]().

### CI/CD Integration

- **Workflow stages:** Validate → Test → Plan → Apply
- **Cost optimization:** Mocking for PRs, integration tests on main branch
- **Tool integration:** GitHub Actions, GitLab CI, Atlantis

[SKILL.md:352-370]() provides overview with detailed templates in [references/ci-cd-workflows.md]().

### Security & Compliance

- **Static scanning:** Trivy, Checkov integration
- **Secrets management:** AWS Secrets Manager patterns
- **State security:** Encryption at rest, access control

[SKILL.md:372-397]() covers essentials with comprehensive guidance in [references/security-compliance.md]().

### Code Patterns & Modern Features

- **Block ordering:** Strict standards for consistency
- **Count vs for_each:** Decision guide with migration patterns
- **Modern features:** Version-specific features from Terraform 1.0-1.11

[SKILL.md:173-476]() provides core patterns with detailed examples in [references/code-patterns.md]().

**Sources:** [SKILL.md:10-517](), [README.md:10-37]()

---

## Version Information

**Current Version:** 1.5.0

Version synchronization across three locations:
- [.claude-plugin/marketplace.json:6](): `"version": "1.5.0"` (root level)
- [.claude-plugin/marketplace.json:26](): `"version": "1.5.0"` (plugin level)
- [SKILL.md:7](): `version: 1.5.0` (metadata)

Version management is automated through GitHub Actions workflows. See [Automation Systems](#6) for details on release automation.

**Sources:** [.claude-plugin/marketplace.json:6,26](), [SKILL.md:7]()

---

## Next Steps

- **Installation:** See [Getting Started](#2) for installation methods
- **Architecture details:** See [Core Architecture](#3) for technical implementation
- **Content exploration:** See [Knowledge Base](#4) for detailed topic coverage
- **Contributing:** See [Development Guide](#5) for contribution guidelines

**Sources:** Document structure from table of contents

---

# Page: What is terraform-skill

# What is terraform-skill

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [CLAUDE.md](CLAUDE.md)
- [README.md](README.md)

</details>



## Purpose and Scope

This document explains what terraform-skill is, how it integrates with Claude Code, and the architectural philosophy behind treating prompt engineering as infrastructure. For installation instructions, see [Installation](#2.1). For details on the plugin definition system, see [Plugin Definition System](#3.1).

---

## Overview

terraform-skill is a **Claude Code skill** - a version-controlled knowledge artifact that provides Claude with domain expertise in Terraform and OpenTofu infrastructure-as-code best practices. It represents a novel approach to AI assistance: packaging expert knowledge as structured markdown files that Claude loads on-demand to enhance its responses.

Unlike traditional software that executes logic, terraform-skill is **executable documentation** that shapes Claude's understanding and decision-making when working with infrastructure code.

**Sources:** [CLAUDE.md:8-13](), [README.md:1-8]()

---

## Skill Discovery and Activation Flow

```mermaid
graph TD
    User["User: 'Create Terraform module with tests'"]
    Claude["Claude AI Agent"]
    Scan["Scan marketplace.json<br/>~100 tokens"]
    Match["Match keywords:<br/>terraform, testing, modules"]
    Activate["Activate terraform-skill"]
    LoadCore["Load SKILL.md<br/>~4,400 tokens"]
    LoadRef["Load references/*.md<br/>0-7K tokens on-demand"]
    Response["Generate response with<br/>best practices applied"]
    
    User --> Claude
    Claude --> Scan
    Scan --> Match
    Match -->|"description matches query"| Activate
    Activate --> LoadCore
    LoadCore -->|"Complex module question"| LoadRef
    LoadCore -->|"Simple query"| Response
    LoadRef --> Response
    
    style Activate fill:#f9f9f9
    style LoadCore fill:#f9f9f9
```

**Diagram: Skill Discovery to Response Generation**

The activation process follows a three-stage pattern defined in [.claude-plugin/marketplace.json:14-16]():

1. **Discovery**: Claude scans the `description` field for keyword matches
2. **Activation**: When keywords like "terraform", "opentofu", "modules", or "testing" appear in user queries
3. **Loading**: Progressive content loading from `SKILL.md` and optional `references/` files

**Sources:** [.claude-plugin/marketplace.json:1-29](), [CLAUDE.md:46-64]()

---

## File Structure and Purpose

```mermaid
graph TB
    subgraph "Plugin Definition"
        MJ["marketplace.json<br/>(28.17 importance)"]
        MJ_Name["name: 'antonbabenko'"]
        MJ_Plugin["plugins[0].name: 'terraform-skill'"]
        MJ_Desc["plugins[0].description: 'Use when...'"]
        MJ_Source["plugins[0].source: './'"]
    end
    
    subgraph "Core Skill"
        SKILL["SKILL.md<br/>(10.14 importance)<br/>~524 lines, ~4.4K tokens"]
        SKILL_Test["Testing Strategy Framework"]
        SKILL_Module["Module Development Patterns"]
        SKILL_CICD["CI/CD Integration"]
        SKILL_Quick["Quick Reference Tables"]
    end
    
    subgraph "Reference Library"
        REF_Mod["references/module-patterns.md<br/>(2.70 importance)<br/>~1,126 lines, ~7K tokens"]
        REF_Quick["references/quick-reference.md<br/>(2.70 importance)<br/>~600 lines, ~3.8K tokens"]
        REF_Code["references/code-patterns.md<br/>(2.00 importance)<br/>~859 lines, ~5.1K tokens"]
        REF_CI["references/ci-cd-workflows.md<br/>(0.70 importance)<br/>~473 lines, ~2.3K tokens"]
        REF_Sec["references/security-compliance.md<br/>(0.70 importance)<br/>~470 lines, ~2.5K tokens"]
    end
    
    MJ --> MJ_Name
    MJ --> MJ_Plugin
    MJ --> MJ_Desc
    MJ --> MJ_Source
    MJ_Source -.->|"points to"| SKILL
    
    SKILL --> SKILL_Test
    SKILL --> SKILL_Module
    SKILL --> SKILL_CICD
    SKILL --> SKILL_Quick
    
    SKILL -.->|"references"| REF_Mod
    SKILL -.->|"references"| REF_Quick
    SKILL -.->|"references"| REF_Code
    SKILL -.->|"references"| REF_CI
    SKILL -.->|"references"| REF_Sec
    
    style MJ fill:#f9f9f9
    style SKILL fill:#f9f9f9
```

**Diagram: Code Entity Structure**

The repository structure maps to a three-tier content hierarchy:

| Tier | File | Token Budget | Purpose | Activation |
|------|------|--------------|---------|------------|
| **Entry** | `.claude-plugin/marketplace.json` | ~100 | Plugin metadata, discovery triggers | Always scanned |
| **Core** | `SKILL.md` | ~4,400 | Essential patterns, decision frameworks, quick reference | On skill activation |
| **Reference** | `references/module-patterns.md` | ~7,000 | Deep module architecture guidance | On-demand |
| **Reference** | `references/quick-reference.md` | ~3,800 | Command cheat sheets, troubleshooting | On-demand |
| **Reference** | `references/code-patterns.md` | ~5,100 | Modern Terraform features, version-specific patterns | On-demand |
| **Reference** | `references/ci-cd-workflows.md` | ~2,300 | Pipeline templates, workflow automation | On-demand |
| **Reference** | `references/security-compliance.md` | ~2,500 | Security scanning, compliance frameworks | On-demand |

**Total available content:** ~30,400 tokens  
**Typical query usage:** 4,500-12,000 tokens (56-70% token savings)

**Sources:** [CLAUDE.md:66-82](), [.claude-plugin/marketplace.json:16]()

---

## Progressive Disclosure Architecture

The skill employs a **progressive disclosure pattern** to optimize token usage:

```mermaid
graph LR
    Query["User Query:<br/>Create S3 module"]
    
    subgraph "Stage 1: Metadata - 100 tokens"
        Meta["marketplace.json<br/>keywords: terraform, modules<br/>description: 'Use when...'"]
    end
    
    subgraph "Stage 2: Core - 4,400 tokens"
        Core["SKILL.md<br/>Module naming conventions<br/>Testing frameworks<br/>Variable patterns<br/>Quick reference"]
    end
    
    subgraph "Stage 3: Deep Dive - 0-7K tokens"
        Deep["references/module-patterns.md<br/>Detailed module hierarchy<br/>Advanced composition<br/>Version strategies"]
    end
    
    Result["Response:<br/>terraform-aws-s3-bucket<br/>with native tests"]
    
    Query --> Meta
    Meta -->|"Match: modules"| Core
    Core -->|"Simple module"| Result
    Core -.->|"Complex module"| Deep
    Deep -.-> Result
    
    style Meta fill:#f9f9f9
    style Core fill:#f9f9f9
    style Deep fill:#f9f9f9
```

**Diagram: Progressive Content Loading Pattern**

This architecture achieves **56-70% token reduction** compared to loading all content simultaneously. For a simple query, Claude only loads ~4,500 tokens instead of the full ~30,400 tokens available.

The activation logic is defined in [.claude-plugin/marketplace.json:15]():
```
"Use when working with Terraform or OpenTofu - creating modules, writing tests, 
setting up CI/CD pipelines, reviewing configurations, choosing between testing 
approaches, debugging state issues, implementing security scanning, or making 
infrastructure-as-code architecture decisions"
```

**Sources:** [CLAUDE.md:46-82](), [README.md:40-54]()

---

## Prompt Engineering as Infrastructure

terraform-skill embodies the philosophy of **prompt engineering as infrastructure** - treating AI instructions with the same rigor as infrastructure code:

| Traditional IaC | Prompt Engineering as IaC |
|----------------|---------------------------|
| Code defines infrastructure | Markdown defines AI behavior |
| Version controlled (Git) | Version controlled (Git) |
| Automated testing (Terratest) | Behavioral testing (Claude responses) |
| CI/CD pipelines | Validation + release workflows |
| Semantic versioning | Semantic versioning |
| Pull request reviews | Content quality reviews |
| Documentation as code | Instructions as documentation |

The repository applies infrastructure principles to prompt content:

- **Version Control**: All content in Git with semantic versioning [.claude-plugin/marketplace.json:6,26]()
- **Automated Releases**: Conventional commits drive version bumps (see [Release Automation](#6.2))
- **Quality Gates**: Automated validation of frontmatter, file size, and links (see [Validation Workflow](#6.1))
- **Progressive Disclosure**: Token budget optimization like infrastructure cost optimization
- **Modular Architecture**: Core skill + reference files like module composition

**Sources:** [CLAUDE.md:8-13](), [README.md:168-177]()

---

## Differences from Traditional Software

terraform-skill differs fundamentally from traditional software projects:

```mermaid
graph TB
    subgraph "Traditional Software"
        Code["Source Code"]
        Compile["Build/Compile"]
        Test["Unit Tests"]
        Deploy["Binary/Artifact"]
        Execute["Runtime Execution"]
    end
    
    subgraph "terraform-skill"
        Docs["Markdown Documentation"]
        Validate["Content Validation"]
        NoTest["No Test Suite"]
        Publish["Git Tag + Release"]
        Load["Claude Loads Content"]
    end
    
    Code --> Compile
    Compile --> Test
    Test --> Deploy
    Deploy --> Execute
    
    Docs --> Validate
    Validate --> NoTest
    NoTest --> Publish
    Publish --> Load
    
    style NoTest fill:#f9f9f9
```

**Diagram: Software vs. Skill Development Flow**

| Aspect | Traditional Software | terraform-skill |
|--------|---------------------|-----------------|
| **Nature** | Executable code | Executable documentation |
| **Build Process** | Compilation required | No build step |
| **Testing** | Automated test suites | Manual behavioral testing |
| **Validation** | Type checking, linting | Frontmatter validation, markdown linting |
| **Deployment** | Binary distribution | Marketplace publication |
| **Execution** | Runtime interpretation | Claude context loading |
| **Artifacts** | Compiled binaries | Raw markdown files |
| **Updates** | Patch releases | Content improvements |
| **Dependencies** | Libraries, packages | Reference knowledge |

As stated in [CLAUDE.md:163-174]():

> **This Is Not Traditional Software**
> 
> **No build/test/compile:**
> - It's documentation, not code
> - No automated test suite
> - No build artifacts

The validation approach requires:

1. Update `SKILL.md` or reference files
2. Load in Claude Code (skills auto-reload)
3. Test with real Terraform queries
4. Observe if Claude applies patterns correctly
5. Iterate based on behavioral results

**Sources:** [CLAUDE.md:160-199]()

---

## Installation and Discovery

Users install the skill through Claude Code's marketplace system:

```bash
/plugin marketplace add antonbabenko/terraform-skill
/plugin install terraform-skill@antonbabenko
```

The installation process:

1. Claude Code reads [.claude-plugin/marketplace.json:2-11]() for repository metadata
2. Downloads the repository to `~/.claude/skills/terraform-skill/`
3. Indexes the `plugins[0]` definition [.claude-plugin/marketplace.json:13-27]()
4. Makes skill available for query matching

For private testing during development:

```bash
git clone git@github.com:antonbabenko/terraform-skill.git ~/.claude/skills/terraform-skill
# Claude Code auto-loads from local filesystem
```

**Sources:** [README.md:38-63](), [CLAUDE.md:180-187]()

---

## Key Capabilities Provided

The skill provides domain expertise across five core areas:

| Capability | Location | Token Budget | Activation Trigger |
|------------|----------|--------------|-------------------|
| **Testing Strategy Framework** | `SKILL.md` | ~4,400 | "testing", "test framework", "terratest" |
| **Module Development** | `SKILL.md` + `references/module-patterns.md` | ~11,400 | "module", "structure", "naming" |
| **Code Patterns** | `references/code-patterns.md` | ~5,100 | "count vs for_each", "modern features" |
| **CI/CD Workflows** | `references/ci-cd-workflows.md` | ~2,300 | "pipeline", "github actions", "gitlab" |
| **Security & Compliance** | `references/security-compliance.md` | ~2,500 | "security", "trivy", "checkov", "compliance" |

The activation trigger description in [.claude-plugin/marketplace.json:15]() lists specific use cases:
- Creating modules
- Writing tests (native test framework, Terratest)
- Setting up CI/CD pipelines
- Reviewing configurations
- Choosing between testing approaches
- Debugging state issues
- Implementing security scanning (trivy, checkov)
- Making infrastructure-as-code architecture decisions

**Sources:** [.claude-plugin/marketplace.json:14-26](), [README.md:10-36]()

---

## Summary

terraform-skill is:

- **A Claude Code skill** that loads on-demand when Terraform/OpenTofu queries are detected
- **Version-controlled expertise** treating prompt engineering with infrastructure-level rigor
- **Progressively disclosed content** optimizing for 56-70% token savings
- **Executable documentation** that shapes Claude's behavior rather than executing code
- **Marketplace-distributed** through `.claude-plugin/marketplace.json` metadata

The skill represents a paradigm shift: instead of writing code that runs, contributors write documentation that teaches Claude how to generate and review code following production-grade Terraform best practices.

**Sources:** [CLAUDE.md:1-46](), [.claude-plugin/marketplace.json:1-29](), [README.md:1-212]()

---

# Page: Key Capabilities

# Key Capabilities

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [SKILL.md](SKILL.md)

</details>



This page documents the technical capabilities provided by terraform-skill, organized by functional area. The skill delivers Terraform and OpenTofu guidance through a structured knowledge base covering testing methodologies, module architecture, CI/CD automation, security scanning, and version-specific feature support.

For installation and usage instructions, see [Getting Started](#2). For architectural details of how these capabilities are delivered, see [Core Architecture](#3).

## Capability Overview

The skill provides guidance in six primary domains:

| Capability Area | Content Source | Token Size | Primary Use Cases |
|----------------|----------------|------------|-------------------|
| Testing Strategy Framework | [SKILL.md:116-171]() | ~1,200 tokens | Choosing test approaches, cost optimization |
| Module Development Patterns | [SKILL.md:315-350]() + `references/module-patterns.md` | ~4,400 + 7,000 tokens | Module structure, variable/output design |
| Code Structure Standards | [SKILL.md:173-227]() + `references/code-patterns.md` | ~1,100 + 5,100 tokens | Block ordering, count vs for_each, refactoring |
| CI/CD Integration | [SKILL.md:352-370]() + `references/ci-cd-workflows.md` | ~400 + 2,300 tokens | Pipeline setup, cost control, automation |
| Security & Compliance | [SKILL.md:372-397]() + `references/security-compliance.md` | ~500 + 2,500 tokens | Scanning tools, secrets management, compliance |
| Version Management | [SKILL.md:399-476]() + `references/code-patterns.md` | ~1,500 + (included above) | Feature availability, migration paths |

**Sources:** [SKILL.md:1-517](), [README.md:10-122]()

## Content Delivery Architecture

```mermaid
graph TB
    subgraph "User Queries"
        Q1["How do I test this module?"]
        Q2["Should I use count or for_each?"]
        Q3["Set up GitHub Actions pipeline"]
        Q4["Security scan configuration"]
    end
    
    subgraph "SKILL.md Core Content"
        TESTING["Testing Strategy Framework<br/>SKILL.md:116-171"]
        CODE["Code Structure Standards<br/>SKILL.md:173-227"]
        MODULE["Module Development<br/>SKILL.md:315-350"]
        CICD["CI/CD Integration<br/>SKILL.md:352-370"]
        SECURITY["Security & Compliance<br/>SKILL.md:372-397"]
        VERSION["Version Management<br/>SKILL.md:399-476"]
    end
    
    subgraph "references/ Directory - On Demand"
        REF_TEST["testing-frameworks.md<br/>~6K tokens"]
        REF_MOD["module-patterns.md<br/>~7K tokens"]
        REF_CODE["code-patterns.md<br/>~5.1K tokens"]
        REF_CICD["ci-cd-workflows.md<br/>~2.3K tokens"]
        REF_SEC["security-compliance.md<br/>~2.5K tokens"]
        REF_QUICK["quick-reference.md<br/>~3.8K tokens"]
    end
    
    Q1 --> TESTING
    Q2 --> CODE
    Q3 --> CICD
    Q4 --> SECURITY
    
    TESTING -.->|"complex scenarios"| REF_TEST
    CODE -.->|"detailed patterns"| REF_CODE
    MODULE -.->|"detailed patterns"| REF_MOD
    CICD -.->|"templates"| REF_CICD
    SECURITY -.->|"scanning setup"| REF_SEC
    
    TESTING -.->|"quick lookup"| REF_QUICK
    CODE -.->|"quick lookup"| REF_QUICK
    
    style TESTING fill:#f9f9f9
    style CODE fill:#f9f9f9
    style MODULE fill:#f9f9f9
    style CICD fill:#f9f9f9
    style SECURITY fill:#f9f9f9
    style VERSION fill:#f9f9f9
```

**Diagram: Content routing from user queries to knowledge base files**

**Sources:** [SKILL.md:499-510](), High-level architecture diagrams

## Testing Strategy Framework

### Decision Matrix

The skill provides a structured decision framework for selecting testing approaches based on project requirements and constraints.

```mermaid
graph TD
    START["Need to test Terraform code"]
    
    CHECK_VERSION{"Terraform version?"}
    CHECK_COST{"Cost sensitivity?"}
    CHECK_COMPLEXITY{"Code complexity?"}
    CHECK_SECURITY{"Security focus?"}
    
    STATIC["Static Analysis<br/>terraform validate, fmt<br/>tflint, trivy, checkov"]
    NATIVE["Native Test Framework<br/>terraform test<br/>SKILL.md:146-171"]
    NATIVE_MOCK["Native with Mock Providers<br/>terraform test + mocking<br/>1.7+ only"]
    TERRATEST["Terratest<br/>Go-based integration<br/>Real infrastructure"]
    POLICY["Policy as Code<br/>OPA, Sentinel"]
    
    START --> CHECK_VERSION
    
    CHECK_VERSION -->|"< 1.6"| TERRATEST
    CHECK_VERSION -->|">= 1.6"| CHECK_COST
    
    CHECK_COST -->|"High cost sensitivity"| CHECK_VERSION_MOCK
    CHECK_COST -->|"Budget available"| CHECK_COMPLEXITY
    
    CHECK_VERSION_MOCK{"Version >= 1.7?"}
    CHECK_VERSION_MOCK -->|"Yes"| NATIVE_MOCK
    CHECK_VERSION_MOCK -->|"No"| STATIC
    
    CHECK_COMPLEXITY -->|"Simple logic"| NATIVE
    CHECK_COMPLEXITY -->|"Complex, multi-cloud"| TERRATEST
    
    START --> CHECK_SECURITY
    CHECK_SECURITY -->|"Yes"| POLICY
```

**Diagram: Testing approach selection flowchart mapping to SKILL.md sections**

**Sources:** [SKILL.md:116-129](), [SKILL.md:146-171]()

### Testing Pyramid Implementation

The skill defines a three-tier testing strategy documented in [SKILL.md:130-144]():

| Tier | Cost | Tools | Implementation |
|------|------|-------|----------------|
| **Static Analysis** | Free | `terraform validate`, `terraform fmt`, `tflint`, `trivy`, `checkov` | Pre-commit hooks, CI validation stage |
| **Integration Tests** | Low-Medium | Native `terraform test` (1.6+) or Terratest | PR validation, main branch only |
| **End-to-End Tests** | High | Full environment deployment | Release validation, production-like |

**Sources:** [SKILL.md:130-144](), [README.md:92-96]()

### Native Test Framework Guidance

For Terraform 1.6+ and OpenTofu 1.6+, the skill provides specific patterns for using the built-in test framework:

**Key decision points documented in [SKILL.md:148-168]():**

1. **Schema validation** - Use Terraform MCP server to identify block types before generating tests
2. **Command mode selection:**
   - `command = plan` - Fast validation for input checking
   - `command = apply` - Required for computed values and set-type blocks
3. **Set-type block handling** - Use `for` expressions instead of indexing with `[0]`

**Common set-type blocks requiring special handling:**
- S3 encryption rules
- Lifecycle transitions  
- IAM policy statements

**Sources:** [SKILL.md:146-171]()

## Module Development Patterns

### Module Hierarchy

The skill defines a three-tier module architecture documented in [SKILL.md:32-66]():

```mermaid
graph LR
    subgraph "Resource Module"
        RM["Single logical resource group<br/>Example: VPC + subnets<br/>SKILL.md:38"]
    end
    
    subgraph "Infrastructure Module"
        IM["Collection of resource modules<br/>Example: Networking stack<br/>SKILL.md:39"]
    end
    
    subgraph "Composition"
        COMP["Complete infrastructure<br/>Multi-region/account<br/>SKILL.md:40"]
    end
    
    RM -->|"used by"| IM
    IM -->|"used by"| COMP
```

**Diagram: Module hierarchy from SKILL.md:34-42**

**Sources:** [SKILL.md:32-66]()

### Standard Module Structure

The skill enforces a consistent directory structure defined in [SKILL.md:319-331]():

```
my-module/
├── README.md           # Usage documentation
├── main.tf             # Primary resources (SKILL.md:110)
├── variables.tf        # Input variables (SKILL.md:111)
├── outputs.tf          # Output values (SKILL.md:112)
├── versions.tf         # Provider version constraints (SKILL.md:113)
├── data.tf             # Data sources (SKILL.md:114, optional)
├── examples/
│   ├── minimal/        # Minimal working example
│   └── complete/       # Full-featured example
└── tests/
    └── module_test.tftest.hcl
```

**Sources:** [SKILL.md:44-59](), [SKILL.md:109-114](), [SKILL.md:319-331]()

### Variable and Output Specifications

**Variable block ordering enforced in [SKILL.md:204-224]():**

1. `description` (required)
2. `type`
3. `default`
4. `validation`
5. `nullable`

**Output requirements from [SKILL.md:342-346]():**

- Always include `description`
- Mark sensitive outputs with `sensitive = true`
- Consider returning objects for related values
- Document consumer usage

**Sources:** [SKILL.md:204-224](), [SKILL.md:335-350]()

## Code Structure Standards

### Resource Block Ordering

The skill enforces strict block ordering defined in [SKILL.md:175-202]():

1. `count` or `for_each` FIRST (with blank line after)
2. Other arguments
3. `tags` as last real argument
4. `depends_on` after tags
5. `lifecycle` at the very end

**Sources:** [SKILL.md:173-202]()

### Count vs For_Each Decision Logic

```mermaid
graph TD
    SCENARIO["Resource creation scenario"]
    
    BOOLEAN{"Boolean condition?<br/>create or don't create"}
    NUMERIC{"Fixed numeric count?"}
    REORDER{"Items may be reordered<br/>or removed?"}
    KEYED{"Need named access?"}
    
    COUNT_BOOL["count = condition ? 1 : 0<br/>SKILL.md:243-249"]
    COUNT_NUM["count = N<br/>Simple replication"]
    FOREACH_SET["for_each = toset list<br/>Stable addresses<br/>SKILL.md:252-269"]
    FOREACH_MAP["for_each = map<br/>Named access<br/>SKILL.md:234-240"]
    
    SCENARIO --> BOOLEAN
    BOOLEAN -->|"Yes"| COUNT_BOOL
    BOOLEAN -->|"No"| NUMERIC
    
    NUMERIC -->|"Yes"| REORDER
    NUMERIC -->|"No"| KEYED
    
    REORDER -->|"Yes"| FOREACH_SET
    REORDER -->|"No"| COUNT_NUM
    
    KEYED -->|"Yes"| FOREACH_MAP
    KEYED -->|"No"| FOREACH_SET
```

**Diagram: Count vs for_each decision tree mapping to SKILL.md patterns**

**Sources:** [SKILL.md:229-271]()

### Naming Conventions

The skill defines specific naming rules in [SKILL.md:68-108]():

**Resource naming:**
- Use descriptive, contextual names for multiple resources
- Use `"this"` only for singleton resources (one per module)
- Avoid generic names like `"main"` or repeating the resource type

**Variable naming:**
- Prefix with context when needed (e.g., `vpc_cidr_block` not `cidr`)
- Use explicit types and descriptions

**Sources:** [SKILL.md:68-108]()

## CI/CD Integration Capabilities

### Workflow Stages

The skill recommends a four-stage pipeline defined in [SKILL.md:354-360]():

1. **Validate** - Format check + syntax validation + linting
2. **Test** - Automated tests (native or Terratest)
3. **Plan** - Generate and review execution plan
4. **Apply** - Execute changes with approvals

**Sources:** [SKILL.md:352-360]()

### Cost Optimization Strategy

The skill provides a cost optimization framework in [SKILL.md:362-367]():

```mermaid
graph LR
    PR["Pull Request"] --> MOCK["Mock Providers<br/>Free validation<br/>SKILL.md:363"]
    MOCK --> MERGE["Merge to main"]
    MERGE --> INTEGRATION["Integration Tests<br/>Real resources<br/>Controlled cost<br/>SKILL.md:364"]
    INTEGRATION --> CLEANUP["Auto-cleanup<br/>Prevent orphans<br/>SKILL.md:365"]
    CLEANUP --> TAG["Resource tagging<br/>Track spending<br/>SKILL.md:366"]
```

**Diagram: Cost-optimized CI/CD flow from SKILL.md:362-367**

**Sources:** [SKILL.md:362-367](), [README.md:107-113]()

### Supported Platforms

The skill provides templates and patterns for:

- GitHub Actions workflows
- GitLab CI pipelines
- Atlantis integration
- Infracost integration (cost estimation)

**Sources:** [SKILL.md:368-370](), [README.md:23-27]()

## Security and Compliance Capabilities

### Static Security Scanning

The skill integrates with multiple security scanning tools documented in [SKILL.md:375-380]():

```bash
# Static security scanning
trivy config .
checkov -d .
```

**Supported tools:**
- **Trivy** - Vulnerability and misconfiguration scanning
- **Checkov** - Policy-as-code compliance
- **TFLint** - Terraform-specific linting
- **OPA** (Open Policy Agent) - Custom policy enforcement
- **Sentinel** - HashiCorp policy framework

**Sources:** [SKILL.md:372-380](), [README.md:28-31]()

### Security Best Practices Checklist

The skill enforces security patterns in [SKILL.md:382-394]():

| Category | ❌ Don't | ✅ Do |
|----------|---------|-------|
| **Secrets** | Store in variables | Use AWS Secrets Manager / Parameter Store |
| **Networking** | Use default VPC | Create dedicated VPCs |
| **Encryption** | Skip encryption | Enable encryption at rest |
| **Access Control** | Open to 0.0.0.0/0 | Use least-privilege security groups |

**Sources:** [SKILL.md:382-394]()

### Compliance Framework Integration

The skill provides guidance for:

- State file security
- Secrets management
- Compliance scanning workflows
- Regulatory checklists

Detailed in `references/security-compliance.md` (~2,500 tokens)

**Sources:** [SKILL.md:396-397](), [README.md:115-121]()

## Version Management

### Version Constraint Strategies

The skill defines version pinning strategies in [SKILL.md:399-417]():

```mermaid
graph TB
    subgraph "Version Strategy by Component"
        TF["Terraform Core<br/>~> 1.9<br/>Pin minor version"]
        PROV["Providers<br/>~> 5.0<br/>Pin major version"]
        MOD_PROD["Modules Production<br/>5.1.2<br/>Exact version"]
        MOD_DEV["Modules Development<br/>~> 5.1<br/>Allow patch updates"]
    end
    
    SYNTAX["Version Constraint Syntax<br/>SKILL.md:402-407"]
    
    SYNTAX --> TF
    SYNTAX --> PROV
    SYNTAX --> MOD_PROD
    SYNTAX --> MOD_DEV
```

**Diagram: Version constraint strategy from SKILL.md:409-417**

**Version constraint operators documented in [SKILL.md:402-407]():**
- `version = "5.0.0"` - Exact (avoid - inflexible)
- `version = "~> 5.0"` - Recommended: 5.0.x only
- `version = ">= 5.0"` - Minimum (risky - breaking changes)

**Sources:** [SKILL.md:399-431]()

### Modern Terraform Features (1.0+)

The skill tracks feature availability by version in [SKILL.md:433-448]():

| Feature | Version | File Reference | Use Case |
|---------|---------|----------------|----------|
| `try()` function | 0.13+ | [SKILL.md:439]() | Safe fallbacks |
| `nullable = false` | 1.1+ | [SKILL.md:440]() | Prevent null values |
| `moved` blocks | 1.1+ | [SKILL.md:441]() | Refactor without destroy |
| `optional()` with defaults | 1.3+ | [SKILL.md:442]() | Optional object attributes |
| Native testing | 1.6+ | [SKILL.md:443]() | Built-in test framework |
| Mock providers | 1.7+ | [SKILL.md:444]() | Cost-free unit testing |
| Provider functions | 1.8+ | [SKILL.md:445]() | Provider-specific transformation |
| Cross-variable validation | 1.9+ | [SKILL.md:446]() | Variable relationship validation |
| Write-only arguments | 1.11+ | [SKILL.md:447]() | Secrets never in state |

**Sources:** [SKILL.md:433-476]()

### Version-Specific Guidance Pathways

```mermaid
graph TD
    VERSION{"Terraform/OpenTofu<br/>version?"}
    
    V10_15["Terraform 1.0-1.5<br/>SKILL.md:480-483"]
    V16_PLUS["Terraform 1.6+<br/>OpenTofu 1.6+<br/>SKILL.md:485-489"]
    V17_PLUS["Terraform 1.7+<br/>OpenTofu 1.7+<br/>SKILL.md:491-494"]
    
    TEST_TERRATEST["Use Terratest<br/>No native testing"]
    TEST_NATIVE["Native terraform test<br/>Migrate from Terratest"]
    TEST_MOCK["Mock providers<br/>Cost reduction"]
    
    VERSION -->|"< 1.6"| V10_15
    VERSION -->|">= 1.6"| V16_PLUS
    VERSION -->|">= 1.7"| V17_PLUS
    
    V10_15 --> TEST_TERRATEST
    V16_PLUS --> TEST_NATIVE
    V17_PLUS --> TEST_MOCK
```

**Diagram: Version-specific testing guidance from SKILL.md:479-494**

**Sources:** [SKILL.md:479-497]()

## Progressive Disclosure System

The skill uses a progressive disclosure architecture to optimize token usage:

| Layer | Content | Token Count | When Loaded |
|-------|---------|-------------|-------------|
| **Discovery** | `marketplace.json` metadata | ~100 | Always (skill activation) |
| **Core** | `SKILL.md` | ~4,400 | On Terraform/OpenTofu queries |
| **Deep Dive** | `references/*.md` (5 files) | ~24,000 total | On-demand per topic |

**Token efficiency:** Achieves 56-70% token reduction vs. loading all content upfront.

**Reference file organization:**
- `testing-frameworks.md` - In-depth testing guide
- `module-patterns.md` - Module structure deep dive
- `code-patterns.md` - Modern features and refactoring
- `ci-cd-workflows.md` - Pipeline templates
- `security-compliance.md` - Security scanning setup
- `quick-reference.md` - Command cheat sheets

**Sources:** [SKILL.md:499-510](), High-level architecture Diagram 2

## Capability Integration Matrix

```mermaid
graph TB
    subgraph "Query Types"
        Q_MODULE["Module creation<br/>structure questions"]
        Q_TEST["Testing approach<br/>test writing"]
        Q_CICD["Pipeline setup<br/>automation"]
        Q_SECURITY["Security scanning<br/>compliance"]
        Q_REFACTOR["Refactoring<br/>modernization"]
    end
    
    subgraph "Capabilities"
        CAP_MODULE["Module Patterns<br/>SKILL.md:315-350"]
        CAP_TEST["Testing Framework<br/>SKILL.md:116-171"]
        CAP_CICD["CI/CD Integration<br/>SKILL.md:352-370"]
        CAP_SECURITY["Security & Compliance<br/>SKILL.md:372-397"]
        CAP_VERSION["Version Management<br/>SKILL.md:399-476"]
        CAP_CODE["Code Standards<br/>SKILL.md:173-227"]
    end
    
    Q_MODULE --> CAP_MODULE
    Q_MODULE --> CAP_CODE
    
    Q_TEST --> CAP_TEST
    Q_TEST --> CAP_VERSION
    
    Q_CICD --> CAP_CICD
    Q_CICD --> CAP_SECURITY
    
    Q_SECURITY --> CAP_SECURITY
    
    Q_REFACTOR --> CAP_VERSION
    Q_REFACTOR --> CAP_CODE
```

**Diagram: Query routing to capability areas**

**Sources:** [SKILL.md:14-29](), [README.md:74-87]()

---

# Page: Getting Started

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

# Page: Installation

# Installation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [README.md](README.md)

</details>



## Purpose and Scope

This document provides detailed installation instructions for the terraform-skill plugin. It covers three installation methods: marketplace installation via Claude Code (recommended), manual filesystem installation, and private testing setup for development. For information about using the skill after installation, see [Using the Skill](#2.2). For contribution and development workflows, see [Development Guide](#5).

---

## Prerequisites

The terraform-skill plugin requires:

| Requirement | Version | Purpose |
|------------|---------|---------|
| Claude Code | Any version supporting skills | Runtime environment for skill execution |
| Terraform | 1.0+ | Target IaC tool (optional for installation) |
| OpenTofu | 1.6+ | Alternative IaC tool (optional for installation) |
| Git | Any recent version | Required for manual/private installation methods |

**Note:** Terraform/OpenTofu are not required for installation itself, only for using the skill's guidance.

Sources: [README.md:149-153]()

---

## Installation Methods

### Overview: Claude Skill Discovery Flow

**Diagram: Skill Discovery and Loading Architecture**

```mermaid
graph TB
    subgraph "Installation Methods"
        MARKETPLACE["/plugin marketplace add<br/>antonbabenko/terraform-skill"]
        MANUAL["git clone to<br/>~/.claude/skills/terraform-skill"]
        PRIVATE["git clone (private repo)<br/>to ~/.claude/skills/terraform-skill"]
    end
    
    subgraph "Claude Code Environment"
        SKILLS_DIR["~/.claude/skills/"]
        SCAN["Skill Directory Scanner"]
    end
    
    subgraph "Plugin Definition"
        MP_FILE[".claude-plugin/marketplace.json"]
        ROOT_META["Root metadata:<br/>name, owner, version"]
        PLUGIN_ARRAY["plugins[] array"]
        PLUGIN_DEF["Plugin definition:<br/>name: terraform-skill<br/>description<br/>source: ./"]
    end
    
    subgraph "Skill Content"
        SKILL_MD["SKILL.md"]
        REFERENCES["references/*.md"]
    end
    
    MARKETPLACE --> SKILLS_DIR
    MANUAL --> SKILLS_DIR
    PRIVATE --> SKILLS_DIR
    
    SKILLS_DIR --> SCAN
    SCAN --> MP_FILE
    
    MP_FILE --> ROOT_META
    MP_FILE --> PLUGIN_ARRAY
    PLUGIN_ARRAY --> PLUGIN_DEF
    
    PLUGIN_DEF --> SKILL_MD
    SKILL_MD --> REFERENCES
    
    ROOT_META -.->|"version: 1.5.0"| VERSION_SYNC[Version Synchronization]
    PLUGIN_DEF -.->|"version: 1.5.0"| VERSION_SYNC
```

Sources: [.claude-plugin/marketplace.json:1-29](), [README.md:38-72]()

---

## Method 1: Marketplace Installation (Recommended)

The marketplace installation method uses Claude Code's plugin marketplace to fetch and install the skill automatically.

**Diagram: Marketplace Installation Flow**

```mermaid
sequenceDiagram
    participant User
    participant ClaudeCode as "Claude Code CLI"
    participant Marketplace as "Marketplace Registry"
    participant SkillsDir as "~/.claude/skills/"
    participant MarketplaceJSON as "marketplace.json"
    
    User->>ClaudeCode: /plugin marketplace add antonbabenko/terraform-skill
    ClaudeCode->>Marketplace: Fetch plugin metadata
    Marketplace-->>ClaudeCode: Return repository info
    ClaudeCode->>SkillsDir: Clone repository
    Note over SkillsDir: Creates terraform-skill@antonbabenko/
    
    User->>ClaudeCode: /plugin install terraform-skill@antonbabenko
    ClaudeCode->>SkillsDir: Locate plugin directory
    ClaudeCode->>MarketplaceJSON: Read .claude-plugin/marketplace.json
    MarketplaceJSON-->>ClaudeCode: name: antonbabenko<br/>version: 1.5.0<br/>plugins[0].name: terraform-skill
    ClaudeCode->>ClaudeCode: Register skill in session
    ClaudeCode-->>User: Skill installed successfully
```

### Installation Commands

Execute these commands in Claude Code:

```bash
/plugin marketplace add antonbabenko/terraform-skill
/plugin install terraform-skill@antonbabenko
```

**Command Breakdown:**

| Command | Purpose | Result |
|---------|---------|--------|
| `/plugin marketplace add` | Registers repository with marketplace | Downloads repository to `~/.claude/skills/terraform-skill@antonbabenko/` |
| `/plugin install` | Activates specific plugin from repository | Loads `terraform-skill` plugin defined in [.claude-plugin/marketplace.json:14]() |

### Key Files Involved

| File Path | Purpose | Key Fields |
|-----------|---------|------------|
| `.claude-plugin/marketplace.json` | Plugin definition and metadata | `name: "antonbabenko"`<br/>`version: "1.5.0"`<br/>`plugins[0].name: "terraform-skill"` |
| `SKILL.md` | Core skill content | Referenced by `plugins[0].source: "./"` |
| `references/*.md` | Extended documentation | Loaded on-demand |

Sources: [README.md:42-47](), [.claude-plugin/marketplace.json:1-29]()

---

## Method 2: Manual Installation

Manual installation clones the repository directly to Claude's skills directory, bypassing the marketplace.

**Diagram: Manual Installation File Mapping**

```mermaid
graph LR
    subgraph "Source Repository"
        REPO["github.com/antonbabenko/<br/>terraform-skill"]
        REPO_MP[".claude-plugin/<br/>marketplace.json"]
        REPO_SKILL["SKILL.md"]
        REPO_REF["references/"]
    end
    
    subgraph "Target Location"
        TARGET["~/.claude/skills/<br/>terraform-skill/"]
        TARGET_MP[".claude-plugin/<br/>marketplace.json"]
        TARGET_SKILL["SKILL.md"]
        TARGET_REF["references/"]
    end
    
    subgraph "Claude Discovery"
        SCAN["Directory Scanner"]
        LOAD["Load marketplace.json"]
        REGISTER["Register Plugin:<br/>terraform-skill"]
    end
    
    REPO -->|git clone| TARGET
    REPO_MP -->|copied| TARGET_MP
    REPO_SKILL -->|copied| TARGET_SKILL
    REPO_REF -->|copied| TARGET_REF
    
    TARGET --> SCAN
    SCAN --> TARGET_MP
    TARGET_MP --> LOAD
    LOAD --> REGISTER
    REGISTER --> TARGET_SKILL
```

### Installation Command

```bash
git clone https://github.com/antonbabenko/terraform-skill ~/.claude/skills/terraform-skill
```

### Directory Structure After Installation

```
~/.claude/skills/terraform-skill/
├── .claude-plugin/
│   └── marketplace.json          # Plugin definition [lines 1-29]
├── SKILL.md                       # Core skill content
├── references/
│   ├── module-patterns.md         # ~7K tokens
│   ├── quick-reference.md         # ~3.8K tokens
│   ├── code-patterns.md           # ~5.1K tokens
│   ├── ci-cd-workflows.md         # ~2.3K tokens
│   └── security-compliance.md     # ~2.5K tokens
├── README.md
└── LICENSE
```

### How Claude Discovers Manually Installed Skills

Claude Code automatically scans `~/.claude/skills/` for subdirectories containing `.claude-plugin/marketplace.json`. The `source` field in [.claude-plugin/marketplace.json:16]() points to `"./"`, indicating the skill content is in the repository root.

Sources: [README.md:49-54](), [.claude-plugin/marketplace.json:16]()

---

## Method 3: Private Testing

This method is used for testing local changes before committing to the repository, or when the repository is private.

**Diagram: Private Testing Workflow**

```mermaid
graph TB
    subgraph "Development Environment"
        LOCAL_REPO["Local Git Repository<br/>(private or modified)"]
        EDIT["Edit SKILL.md or<br/>references/*.md"]
    end
    
    subgraph "Claude Skills Directory"
        CLONE["git clone to<br/>~/.claude/skills/terraform-skill"]
        SYMLINK["Alternative: symlink<br/>~/.claude/skills/terraform-skill<br/>-> /path/to/local/repo"]
    end
    
    subgraph "Claude Runtime"
        RELOAD["Claude Code automatically<br/>loads skills on startup"]
        TEST["Test with queries"]
        VERIFY["Verify behavior changes"]
    end
    
    LOCAL_REPO --> EDIT
    EDIT --> CLONE
    EDIT --> SYMLINK
    
    CLONE --> RELOAD
    SYMLINK --> RELOAD
    
    RELOAD --> TEST
    TEST --> VERIFY
    VERIFY -->|Changes needed| EDIT
    Verify -->|Ready| COMMIT["git commit & push"]
```

### Installation Command

```bash
git clone git@github.com:antonbabenko/terraform-skill.git ~/.claude/skills/terraform-skill
```

**Alternative: Symlink for Active Development**

```bash
ln -s /path/to/your/terraform-skill ~/.claude/skills/terraform-skill
```

This allows editing files in your development directory without copying them to `~/.claude/skills/`.

### Private Repository Authentication

For private repositories, ensure your Git credentials are configured:

```bash
# SSH key authentication (recommended)
ssh-add ~/.ssh/id_rsa

# Or use Git credential helper
git config --global credential.helper cache
```

Sources: [README.md:56-63]()

---

## Verification

After installation using any method, verify the skill is available and functioning correctly.

### Step 1: Check Skill Registration

In Claude Code, the skill should appear when querying about Terraform/OpenTofu topics. The activation trigger keywords are defined in [.claude-plugin/marketplace.json:15]():

```json
"description": "Use when working with Terraform or OpenTofu - creating modules, 
writing tests (native test framework, Terratest), setting up CI/CD pipelines, 
reviewing configurations, choosing between testing approaches, debugging state 
issues, implementing security scanning (trivy, checkov), or making 
infrastructure-as-code architecture decisions"
```

### Step 2: Test Activation

Execute a test query in Claude Code:

```
"Create a Terraform module with testing for an S3 bucket"
```

**Expected Behavior:**
- Claude recognizes the query as Terraform-related
- The `terraform-skill` plugin activates automatically
- Response includes best practices from `SKILL.md` and relevant reference files

### Step 3: Verify Version

Check that the installed version matches the latest release. The version is specified in three locations:

| File | Field | Line Reference |
|------|-------|----------------|
| `.claude-plugin/marketplace.json` | `version` (root level) | [.claude-plugin/marketplace.json:6]() |
| `.claude-plugin/marketplace.json` | `plugins[0].version` | [.claude-plugin/marketplace.json:26]() |
| `SKILL.md` | Frontmatter `version` field | Referenced by release automation |

All three should show the same version (e.g., `1.5.0`).

Sources: [README.md:65-72](), [.claude-plugin/marketplace.json:6](), [.claude-plugin/marketplace.json:26]()

---

## Troubleshooting

### Skill Not Activating

**Problem:** Claude doesn't use the skill when asked about Terraform topics.

**Diagnosis:**

1. **Check file structure:**
   ```bash
   ls -la ~/.claude/skills/terraform-skill/.claude-plugin/marketplace.json
   ```
   
2. **Verify JSON syntax:**
   ```bash
   cat ~/.claude/skills/terraform-skill/.claude-plugin/marketplace.json | jq .
   ```
   If `jq` fails, the JSON is malformed.

3. **Check plugin name match:**
   The `plugins[0].name` field in [.claude-plugin/marketplace.json:14]() must be `"terraform-skill"`.

**Solutions:**

- **Manual/Private installation:** Ensure the directory is named exactly `terraform-skill` (not `terraform-skill-main` or similar)
- **Marketplace installation:** Try reinstalling:
  ```bash
  /plugin uninstall terraform-skill@antonbabenko
  /plugin install terraform-skill@antonbabenko
  ```

### Version Mismatch Errors

**Problem:** Version numbers don't match across files.

**Cause:** Manual editing without updating all three version fields.

**Solution:** The release automation ([.github/workflows/automated-release.yml]()) handles version synchronization automatically. For local testing, manually verify:

```bash
# Check root version
jq '.version' ~/.claude/skills/terraform-skill/.claude-plugin/marketplace.json

# Check plugin version
jq '.plugins[0].version' ~/.claude/skills/terraform-skill/.claude-plugin/marketplace.json
```

Both should return the same version string.

### Permission Errors

**Problem:** Cannot write to `~/.claude/skills/`.

**Solution:**

```bash
# Ensure directory exists and is writable
mkdir -p ~/.claude/skills
chmod 755 ~/.claude/skills
```

### Private Repository Access Denied

**Problem:** `git clone` fails with authentication error.

**Solutions:**

1. **Verify SSH key:**
   ```bash
   ssh -T git@github.com
   ```
   Should return: `Hi <username>! You've successfully authenticated...`

2. **Use HTTPS with token:**
   ```bash
   git clone https://<token>@github.com/antonbabenko/terraform-skill.git ~/.claude/skills/terraform-skill
   ```

3. **Check repository permissions:** Ensure your GitHub account has read access to the repository.

Sources: [README.md:56-63]()

---

## Installation Summary

**Quick Reference Table:**

| Method | Command | Use Case | Pros | Cons |
|--------|---------|----------|------|------|
| **Marketplace** | `/plugin marketplace add` → `/plugin install` | General use | Automatic updates<br/>Official distribution | Requires marketplace access |
| **Manual** | `git clone https://...` | Stable version, offline use | Works without marketplace<br/>Full control | Manual updates needed |
| **Private Testing** | `git clone git@github.com:...` or symlink | Development, private repos | Test local changes<br/>Active development | Requires Git access<br/>No automatic updates |

All methods result in the same functional skill, with differences only in update mechanism and initial setup complexity.

Sources: [README.md:38-72](), [.claude-plugin/marketplace.json:1-29]()

---

# Page: Using the Skill

# Using the Skill

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [SKILL.md](SKILL.md)

</details>



This page describes how to interact with the terraform-skill in Claude Code, including activation triggers, query patterns, and response mechanisms. For installation instructions, see [Installation](#2.1). For details on the skill's content architecture, see [Progressive Disclosure Pattern](#3.2).

## Skill Activation Mechanism

The skill activates automatically when Claude detects Terraform or OpenTofu-related queries through keyword matching in `marketplace.json` and contextual analysis.

### Discovery and Activation Flow

```mermaid
flowchart TD
    User["User Query<br/>'Create a Terraform module for S3'"]
    
    subgraph "Discovery Phase"
        Scan["Claude scans marketplace.json"]
        Keywords["Match against keywords:<br/>terraform, opentofu, IaC, modules, terratest"]
        Description["Match against description field"]
        Triggers["Evaluate activation triggers"]
    end
    
    subgraph "Activation Decision"
        Score["Calculate relevance score"]
        Threshold{"Score ≥ threshold?"}
    end
    
    subgraph "Content Loading"
        LoadCore["Load SKILL.md<br/>(~4.4K tokens)"]
        Evaluate["Evaluate query complexity"]
        LoadRef["Load reference files<br/>(0-7K tokens per file)"]
    end
    
    subgraph "Response Generation"
        Synthesize["Synthesize guidance from<br/>loaded content"]
        Generate["Generate response with<br/>Terraform best practices"]
    end
    
    User --> Scan
    Scan --> Keywords
    Scan --> Description
    Keywords --> Triggers
    Description --> Triggers
    Triggers --> Score
    Score --> Threshold
    
    Threshold -->|"Yes"| LoadCore
    Threshold -->|"No"| NoSkill["Use base Claude knowledge"]
    
    LoadCore --> Evaluate
    Evaluate -->|"Needs detail"| LoadRef
    Evaluate -->|"Core sufficient"| Synthesize
    LoadRef --> Synthesize
    
    Synthesize --> Generate
    Generate --> Response["Response to user"]
```

**Sources:** [SKILL.md:1-8](), [SKILL.md:14-28](), [README.md:66-72]()

### Activation Triggers

The skill activates when queries involve the following scenarios, as defined in [SKILL.md:14-24]():

| Trigger Category | Example Keywords | Activates Skill |
|-----------------|------------------|-----------------|
| **Module creation** | "create module", "new terraform module" | ✅ Yes |
| **Testing infrastructure** | "test framework", "terratest", "native tests" | ✅ Yes |
| **Testing decisions** | "which testing approach", "validate vs plan" | ✅ Yes |
| **Multi-environment** | "staging", "production", "environment structure" | ✅ Yes |
| **CI/CD setup** | "github actions", "pipeline", "atlantis" | ✅ Yes |
| **Code review** | "review terraform", "refactor", "best practices" | ✅ Yes |
| **Pattern selection** | "module patterns", "state management" | ✅ Yes |
| **Basic syntax** | "how to write resource block" | ❌ No (Claude's base knowledge) |
| **Provider API** | "aws_instance parameters" | ❌ No (link to docs) |
| **Cloud platform** | "how S3 works" | ❌ No (not Terraform-specific) |

**Sources:** [SKILL.md:14-28]()

### Query-to-Content Mapping

```mermaid
flowchart LR
    subgraph "Query Types"
        Q1["Module creation query"]
        Q2["Testing approach query"]
        Q3["CI/CD setup query"]
        Q4["Security scan query"]
        Q5["Command reference query"]
    end
    
    subgraph "Content Loaded"
        Core["SKILL.md core content<br/>(always loaded)"]
        ModRef["references/module-patterns.md<br/>(7K tokens)"]
        QuickRef["references/quick-reference.md<br/>(3.8K tokens)"]
        CICDRef["references/ci-cd-workflows.md<br/>(2.3K tokens)"]
        SecRef["references/security-compliance.md<br/>(2.5K tokens)"]
    end
    
    Q1 --> Core
    Q1 --> ModRef
    
    Q2 --> Core
    Q2 --> QuickRef
    
    Q3 --> Core
    Q3 --> CICDRef
    
    Q4 --> Core
    Q4 --> SecRef
    
    Q5 --> Core
    Q5 --> QuickRef
```

**Sources:** [SKILL.md:499-510](), Diagram 2 from context

## Example Query Patterns

### High-Quality Queries

These queries trigger the skill and receive comprehensive responses:

| Query Pattern | Content Loaded | Example Response |
|--------------|----------------|------------------|
| **"Create a Terraform module for [resource] with testing"** | SKILL.md + module-patterns.md | Full module structure with variables, outputs, tests |
| **"Help me choose between native tests and Terratest"** | SKILL.md + quick-reference.md | Decision matrix with cost/complexity tradeoffs |
| **"Review this Terraform code for best practices"** | SKILL.md + code-patterns.md | Line-by-line review with ✅ DO / ❌ DON'T examples |
| **"Create GitHub Actions workflow for Terraform"** | SKILL.md + ci-cd-workflows.md | Complete workflow YAML with cost optimization |
| **"How do I secure Terraform state files?"** | SKILL.md + security-compliance.md | State backend configuration + encryption patterns |
| **"What's the difference between count and for_each?"** | SKILL.md (core only) | Decision guide + migration examples |

**Sources:** [README.md:74-87](), [SKILL.md:229-271]()

### Interactive Example: Module Creation

```mermaid
sequenceDiagram
    participant User
    participant Claude
    participant marketplace.json
    participant SKILL.md
    participant module-patterns.md
    
    User->>Claude: "Create a Terraform module for AWS VPC with native tests"
    Claude->>marketplace.json: Check activation triggers
    marketplace.json-->>Claude: Match: "terraform", "module", "tests"
    
    Claude->>SKILL.md: Load core content
    SKILL.md-->>Claude: Module structure (lines 315-331)
    SKILL.md-->>Claude: Testing framework (lines 116-172)
    SKILL.md-->>Claude: Variable ordering (lines 203-225)
    
    Claude->>module-patterns.md: Load detailed patterns
    module-patterns.md-->>Claude: Variable best practices
    module-patterns.md-->>Claude: Output design patterns
    
    Claude->>User: Generate:<br/>- main.tf with VPC resources<br/>- variables.tf with descriptions<br/>- outputs.tf with sensitive marking<br/>- tests/vpc.tftest.hcl<br/>- examples/complete/
```

**Sources:** [SKILL.md:315-350](), [SKILL.md:116-172](), [README.md:76-78]()

## Query Patterns by Use Case

### Module Development Queries

These queries focus on creating and structuring Terraform modules:

```
✅ Effective queries:
- "Create a module for [AWS resource] following best practices"
- "Structure a multi-resource module for [infrastructure pattern]"
- "Add input validation to this module"
- "Design outputs for this module"

📚 Content loaded:
- SKILL.md lines 315-350 (module structure)
- SKILL.md lines 203-225 (variable ordering)
- SKILL.md lines 333-347 (best practices summary)
- references/module-patterns.md (on-demand)
```

**Sources:** [SKILL.md:315-350](), [SKILL.md:333-350]()

### Testing Strategy Queries

These queries help choose and implement testing approaches:

```
✅ Effective queries:
- "Which testing approach for Terraform 1.9?"
- "Help me write native tests for this module"
- "Convert these Terratest tests to native format"
- "Set up testing workflow with cost optimization"

📚 Content loaded:
- SKILL.md lines 116-172 (testing strategy framework)
- SKILL.md lines 130-144 (testing pyramid)
- SKILL.md lines 146-172 (native test best practices)
- references/quick-reference.md (decision flowchart)
```

**Sources:** [SKILL.md:116-172](), [README.md:84-86]()

### CI/CD Integration Queries

These queries configure continuous integration workflows:

```
✅ Effective queries:
- "Create GitHub Actions workflow for Terraform with security scanning"
- "Set up GitLab CI for multi-environment Terraform"
- "Add cost estimation to my Terraform pipeline"
- "Configure Atlantis for pull request automation"

📚 Content loaded:
- SKILL.md lines 352-370 (CI/CD integration)
- SKILL.md lines 360-367 (cost optimization strategy)
- references/ci-cd-workflows.md (detailed templates)
```

**Sources:** [SKILL.md:352-370](), [README.md:82-84]()

### Code Review Queries

These queries analyze existing Terraform code:

```
✅ Effective queries:
- "Review this Terraform configuration for best practices"
- "Refactor this module to use for_each instead of count"
- "Update this code to use Terraform 1.9 features"
- "Identify security issues in this configuration"

📚 Content loaded:
- SKILL.md lines 173-228 (code structure standards)
- SKILL.md lines 229-271 (count vs for_each)
- SKILL.md lines 433-476 (modern features)
- references/code-patterns.md (detailed patterns)
```

**Sources:** [SKILL.md:173-271](), [README.md:79-80]()

## Response Patterns

### Token Budget Awareness

The skill uses progressive disclosure to optimize token usage:

| Query Complexity | Tokens Loaded | Content Sources |
|-----------------|---------------|-----------------|
| **Simple** (syntax check) | ~4,400 | SKILL.md only |
| **Moderate** (module creation) | ~11,400 | SKILL.md + 1 reference file |
| **Complex** (full architecture) | ~18,900 | SKILL.md + 2-3 reference files |
| **Maximum** | ~30,400 | SKILL.md + all references |

Typical queries use **4,500-12,000 tokens** (56-70% reduction vs loading all content).

**Sources:** Diagram 2 from context, [SKILL.md:500-510]()

### Code Entity References in Responses

When the skill generates responses, it references specific code patterns and file structures:

```mermaid
graph TB
    subgraph "User Query Space"
        Q["'Create module with tests'"]
    end
    
    subgraph "Code Entity Space"
        main_tf["main.tf<br/>(primary resources)"]
        variables_tf["variables.tf<br/>(input variables)"]
        outputs_tf["outputs.tf<br/>(output values)"]
        versions_tf["versions.tf<br/>(provider versions)"]
        tests_dir["tests/<br/>(test files)"]
        examples_dir["examples/<br/>(usage examples)"]
        
        tftest["*.tftest.hcl<br/>(native test files)"]
        minimal["examples/minimal/<br/>(minimal example)"]
        complete["examples/complete/<br/>(complete example)"]
    end
    
    subgraph "SKILL.md References"
        L315_331["SKILL.md:315-331<br/>(module structure)"]
        L109_115["SKILL.md:109-115<br/>(file naming)"]
        L203_225["SKILL.md:203-225<br/>(variable ordering)"]
        L146_172["SKILL.md:146-172<br/>(native tests)"]
    end
    
    Q --> L315_331
    L315_331 --> main_tf
    L315_331 --> variables_tf
    L315_331 --> outputs_tf
    L315_331 --> versions_tf
    L315_331 --> tests_dir
    L315_331 --> examples_dir
    
    L109_115 --> main_tf
    L109_115 --> variables_tf
    L109_115 --> outputs_tf
    
    L203_225 --> variables_tf
    
    L146_172 --> tftest
    L315_331 --> minimal
    L315_331 --> complete
```

**Sources:** [SKILL.md:315-331](), [SKILL.md:109-115](), [SKILL.md:203-225](), [SKILL.md:146-172]()

## Verification and Debugging

### Verifying Skill Activation

After installation (see [Installation](#2.1)), verify the skill is working:

```bash
# Method 1: Simple activation test
# Ask Claude: "Create a Terraform module with testing for an S3 bucket"
# Expected: Skill activates, references SKILL.md patterns

# Method 2: Check for specific guidance
# Ask Claude: "Should I use count or for_each for multiple subnets?"
# Expected: Decision guide from SKILL.md:229-271

# Method 3: Request citation
# Ask Claude: "Where does this recommendation come from?"
# Expected: References to SKILL.md line numbers or reference files
```

**Sources:** [README.md:66-72]()

### Signs the Skill is Active

When the skill is properly activated, Claude's responses will:

| Indicator | What to Look For |
|-----------|------------------|
| **Structure references** | Mentions "resource module", "infrastructure module", "composition" hierarchy |
| **File organization** | Suggests `main.tf`, `variables.tf`, `outputs.tf`, `versions.tf` layout |
| **Testing guidance** | Provides decision matrix for test framework selection |
| **Version-specific** | Mentions Terraform 1.6+, 1.7+, or 1.9+ features explicitly |
| **Code patterns** | Shows ✅ DO vs ❌ DON'T examples |
| **Token efficiency** | References progressive disclosure or reference files |

**Sources:** [SKILL.md:34-65](), [SKILL.md:315-331](), [SKILL.md:116-129]()

### Common Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| Skill not activating | Query too generic | Make query Terraform-specific: add "module", "testing", "CI/CD" |
| Missing detailed patterns | Only core loaded | Ask follow-up: "Show me detailed examples" |
| Outdated recommendations | Skill not updated | Check version in SKILL.md:7 |
| No reference file content | Progressive loading | Ask explicitly: "Show me the CI/CD workflow patterns" |

**Sources:** [SKILL.md:14-28](), [SKILL.md:499-510]()

## Advanced Usage Patterns

### Requesting Specific Reference Content

You can explicitly request content from reference files:

```
Query patterns that load specific references:

"Show me detailed module patterns" 
→ Loads references/module-patterns.md

"Give me command cheat sheets"
→ Loads references/quick-reference.md

"Show CI/CD workflow templates"
→ Loads references/ci-cd-workflows.md

"Explain security scanning integration"
→ Loads references/security-compliance.md

"Show me modern Terraform features"
→ Loads references/code-patterns.md
```

**Sources:** [SKILL.md:499-510]()

### Combining Multiple Query Types

Complex queries can combine multiple aspects:

```mermaid
flowchart TD
    ComplexQuery["'Create a secure VPC module with<br/>native tests and GitHub Actions CI/CD'"]
    
    subgraph "Content Assembly"
        Core["SKILL.md core"]
        ModPat["module-patterns.md<br/>(module structure)"]
        SecComp["security-compliance.md<br/>(security scanning)"]
        CICD["ci-cd-workflows.md<br/>(GitHub Actions)"]
        QuickRef["quick-reference.md<br/>(testing decisions)"]
    end
    
    subgraph "Response Components"
        ModuleFiles["Module files:<br/>main.tf, variables.tf, outputs.tf"]
        TestFiles["Test files:<br/>tests/vpc.tftest.hcl"]
        WorkflowFile["Workflow file:<br/>.github/workflows/terraform.yml"]
        SecurityScans["Security scans:<br/>trivy, checkov steps"]
    end
    
    ComplexQuery --> Core
    ComplexQuery --> ModPat
    ComplexQuery --> SecComp
    ComplexQuery --> CICD
    ComplexQuery --> QuickRef
    
    Core --> ModuleFiles
    ModPat --> ModuleFiles
    QuickRef --> TestFiles
    CICD --> WorkflowFile
    SecComp --> SecurityScans
    
    ModuleFiles --> FinalResponse["Comprehensive Response"]
    TestFiles --> FinalResponse
    WorkflowFile --> FinalResponse
    SecurityScans --> FinalResponse
```

**Sources:** [SKILL.md:499-510](), Diagram 2 from context

### Version-Specific Queries

The skill provides different guidance based on Terraform version:

```
"I'm using Terraform 1.5, how should I test?"
→ Response focuses on Terratest (native tests not available)

"I'm using Terraform 1.7, what testing options do I have?"
→ Response includes mock providers for cost-free unit testing

"Show me Terraform 1.9 cross-variable validation"
→ Response uses features from SKILL.md:465-474
```

**Sources:** [SKILL.md:478-497](), [SKILL.md:433-476]()

## Query Templates

### By Skill Level

**Beginner:**
```
- "What's the standard structure for a Terraform module?"
- "How do I organize variables in variables.tf?"
- "What files should a module have?"
```

**Intermediate:**
```
- "Should I use count or for_each for multiple security groups?"
- "Create a GitHub Actions workflow with terraform validate"
- "How do I test this module without deploying infrastructure?"
```

**Advanced:**
```
- "Refactor this module to use Terraform 1.9 features"
- "Design a multi-region module composition"
- "Implement policy-as-code for compliance scanning"
```

**Sources:** [SKILL.md:229-271](), [SKILL.md:352-370](), [SKILL.md:433-476]()

### By Deliverable Type

**Documentation:**
```
- "Generate README.md for this module"
- "Document the input variables with examples"
- "Create usage examples for this module"
```

**Testing:**
```
- "Write native tests for this S3 module"
- "Create integration tests using Terratest"
- "Add validation blocks to these variables"
```

**Automation:**
```
- "Create pre-commit hooks for Terraform"
- "Set up Atlantis for pull request automation"
- "Add automated cost estimation to CI/CD"
```

**Sources:** [SKILL.md:146-172](), [SKILL.md:352-370]()

---

# Page: Core Architecture

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [CLAUDE.md](CLAUDE.md)
- [SKILL.md](SKILL.md)

</details>



This document describes the technical architecture of the terraform-skill system, focusing on how Claude Code discovers, loads, and executes the skill. It covers the plugin definition system, the progressive disclosure pattern for token optimization, and the file organization strategy.

For information about the specific content and guidance provided by the skill, see [Knowledge Base](#4). For automation and quality systems, see [Automation Systems](#6).

---

## Architecture Overview

The terraform-skill system implements a **three-tier architecture** designed to optimize Claude Code's token budget while providing comprehensive Terraform/OpenTofu expertise:

1. **Discovery Layer** - Metadata that enables Claude to find and activate the skill
2. **Core Layer** - Essential guidance loaded on every activation (~4.4K tokens)
3. **Reference Layer** - Detailed content loaded on-demand (~26K tokens available)

This architecture achieves **56-70% token reduction** compared to loading all content upfront, while maintaining comprehensive coverage of Terraform best practices.

**Sources:** [CLAUDE.md:46-82](), [SKILL.md:1-517]()

---

## System Component Diagram

```mermaid
graph TB
    subgraph Discovery["Discovery Layer (~100 tokens)"]
        MPJ[".claude-plugin/marketplace.json"]
        OWNER["owner.name"]
        VERSION["version: 1.5.0"]
        PLUGINS["plugins[]"]
        KEYWORDS["keywords[]"]
    end
    
    subgraph Core["Core Layer (~4.4K tokens)"]
        SKILL["SKILL.md"]
        FRONTMATTER["YAML frontmatter<br/>name, description, version"]
        ACTIVATION["When to Use This Skill<br/>Activation triggers"]
        PRINCIPLES["Core Principles<br/>Code Structure Philosophy"]
        TESTING["Testing Strategy Framework<br/>Decision Matrix"]
        PATTERNS["Code Structure Standards<br/>Block Ordering"]
    end
    
    subgraph References["Reference Layer (~26K tokens, loaded on-demand)"]
        REF_MOD["references/module-patterns.md<br/>~7K tokens"]
        REF_QUICK["references/quick-reference.md<br/>~3.8K tokens"]
        REF_CODE["references/code-patterns.md<br/>~5.1K tokens"]
        REF_CI["references/ci-cd-workflows.md<br/>~2.3K tokens"]
        REF_SEC["references/security-compliance.md<br/>~2.5K tokens"]
        REF_TEST["references/testing-frameworks.md<br/>~3.4K tokens"]
    end
    
    MPJ --> SKILL
    SKILL --> FRONTMATTER
    SKILL --> ACTIVATION
    SKILL --> PRINCIPLES
    SKILL --> TESTING
    SKILL --> PATTERNS
    
    SKILL -.->|"On-demand reference"| REF_MOD
    SKILL -.->|"On-demand reference"| REF_QUICK
    SKILL -.->|"On-demand reference"| REF_CODE
    SKILL -.->|"On-demand reference"| REF_CI
    SKILL -.->|"On-demand reference"| REF_SEC
    SKILL -.->|"On-demand reference"| REF_TEST
    
    PLUGINS --> MPJ
    VERSION --> MPJ
    KEYWORDS --> MPJ
    OWNER --> MPJ
```

**Sources:** [.claude-plugin/marketplace.json:1-29](), [SKILL.md:1-517](), [CLAUDE.md:66-82]()

---

## Plugin Discovery and Activation Flow

```mermaid
sequenceDiagram
    participant User
    participant Claude["Claude Code Agent"]
    participant FS["File System"]
    participant MPJ[".claude-plugin/marketplace.json"]
    participant SKILL["SKILL.md"]
    participant REF["references/*.md"]
    
    User->>Claude: "Create Terraform module with tests"
    
    Claude->>FS: Scan ~/.claude/skills/
    FS-->>Claude: Available skills list
    
    Claude->>MPJ: Read metadata
    MPJ-->>Claude: plugins[0].description<br/>plugins[0].keywords
    
    Note over Claude: Match query against:<br/>keywords: ["terraform", "testing"]<br/>description: "working with Terraform"
    
    Claude->>SKILL: Load frontmatter (lines 1-8)
    SKILL-->>Claude: name, description, version
    
    Note over Claude: Skill activated
    
    Claude->>SKILL: Load full content
    SKILL-->>Claude: ~4.4K tokens<br/>Testing Strategy Framework<br/>Module Development<br/>Code Structure Standards
    
    alt Query needs detailed module guidance
        Claude->>REF: Load module-patterns.md
        REF-->>Claude: ~7K additional tokens
    else Query needs CI/CD templates
        Claude->>REF: Load ci-cd-workflows.md
        REF-->>Claude: ~2.3K additional tokens
    else Standard query
        Note over Claude: Use SKILL.md only<br/>~4.4K tokens total
    end
    
    Claude->>User: Response with Terraform best practices
```

**Sources:** [.claude-plugin/marketplace.json:13-27](), [SKILL.md:1-8](), [SKILL.md:14-28](), [CLAUDE.md:46-63]()

---

## File Organization and Responsibilities

The terraform-skill repository follows a strict file organization pattern where each file has a specific role and token budget:

| File Path | Role | Token Budget | Audience |
|-----------|------|--------------|----------|
| `.claude-plugin/marketplace.json` | Plugin metadata and discovery | ~100 tokens | Claude Code (machine) |
| `SKILL.md` | Core skill content | ~4,400 tokens | Claude Code (primary) |
| `references/module-patterns.md` | Module development patterns | ~7,000 tokens | Claude Code (on-demand) |
| `references/quick-reference.md` | Command cheat sheets | ~3,800 tokens | Claude Code (on-demand) |
| `references/code-patterns.md` | Modern Terraform features | ~5,100 tokens | Claude Code (on-demand) |
| `references/ci-cd-workflows.md` | Pipeline templates | ~2,300 tokens | Claude Code (on-demand) |
| `references/security-compliance.md` | Security guidance | ~2,500 tokens | Claude Code (on-demand) |
| `references/testing-frameworks.md` | Testing guides | ~3,400 tokens | Claude Code (on-demand) |
| `README.md` | Installation and usage | N/A | Human users |
| `CLAUDE.md` | Development guidelines | N/A | Contributors |
| `CONTRIBUTING.md` | Contribution process | N/A | Contributors |

**Total Available Content:** ~30,400 tokens
**Typical Query Cost:** 4,500-12,000 tokens (56-70% reduction)

**Sources:** [CLAUDE.md:17-43](), [CLAUDE.md:66-82]()

---

## marketplace.json Structure

The `.claude-plugin/marketplace.json` file serves as the **entry point** for Claude Code's skill discovery system. It defines both marketplace-level metadata and individual plugin configurations.

### File Structure Diagram

```mermaid
graph TB
    ROOT["marketplace.json root object"]
    
    MNAME["name: antonbabenko"]
    OWNER["owner.name: Anton Babenko"]
    MVERSION["version: 1.5.0"]
    META["metadata{}"]
    PLUGINS["plugins[]"]
    
    MDESC["metadata.description"]
    MREPO["metadata.repository"]
    MLIC["metadata.license: Apache-2.0"]
    
    PLUGIN0["plugins[0]"]
    PNAME["name: terraform-skill"]
    PDESC["description: Use when working with..."]
    PSOURCE["source: ./"]
    PCAT["category: development"]
    PKEYWORDS["keywords[]"]
    PVERSION["version: 1.5.0"]
    
    ROOT --> MNAME
    ROOT --> OWNER
    ROOT --> MVERSION
    ROOT --> META
    ROOT --> PLUGINS
    
    META --> MDESC
    META --> MREPO
    META --> MLIC
    
    PLUGINS --> PLUGIN0
    PLUGIN0 --> PNAME
    PLUGIN0 --> PDESC
    PLUGIN0 --> PSOURCE
    PLUGIN0 --> PCAT
    PLUGIN0 --> PKEYWORDS
    PLUGIN0 --> PVERSION
```

### Key Fields and Purposes

**Marketplace Metadata** (lines 2-11):
- `name` - Marketplace identifier (author namespace)
- `owner.name` - Human-readable author name
- `version` - Marketplace version (synchronized across system)
- `metadata.description` - High-level marketplace description
- `metadata.repository` - Source code location
- `metadata.license` - Legal terms (Apache-2.0)

**Plugin Definition** (lines 13-27):
- `plugins[0].name` - Plugin identifier (`terraform-skill`)
- `plugins[0].description` - **Critical:** Activation triggers for Claude
- `plugins[0].source` - File path to skill content (`./` points to repository root)
- `plugins[0].category` - Classification for marketplace (`development`)
- `plugins[0].keywords` - Searchable terms: `["terraform", "opentofu", "infrastructure-as-code", "testing", "ci-cd", "modules"]`
- `plugins[0].version` - Plugin version (synchronized with marketplace version)

### Activation Trigger Analysis

The `plugins[0].description` field at [.claude-plugin/marketplace.json:15]() is the **most important** field for skill activation:

```
"Use when working with Terraform or OpenTofu - creating modules, 
writing tests (native test framework, Terratest), setting up CI/CD 
pipelines, reviewing configurations, choosing between testing approaches, 
debugging state issues, implementing security scanning (trivy, checkov), 
or making infrastructure-as-code architecture decisions"
```

Claude matches user queries against these phrases to determine skill relevance. This description is **duplicated** in `SKILL.md` frontmatter for consistency.

**Sources:** [.claude-plugin/marketplace.json:1-29]()

---

## SKILL.md Frontmatter and Structure

The `SKILL.md` file begins with YAML frontmatter that mirrors the marketplace metadata:

### Frontmatter Structure

```yaml
---
name: terraform-skill
description: Use when working with Terraform or OpenTofu - creating modules, writing tests (native test framework, Terratest), setting up CI/CD pipelines, reviewing configurations, choosing between testing approaches, debugging state issues, implementing security scanning (trivy, checkov), or making infrastructure-as-code architecture decisions
license: Apache-2.0
metadata:
  author: Anton Babenko
  version: 1.5.0
---
```

This frontmatter serves multiple purposes:
1. **Discovery** - Claude reads this before loading full content
2. **Version Synchronization** - Must match marketplace.json versions
3. **Activation** - Description field matches marketplace plugin description
4. **Attribution** - Author and license information

### Content Organization Pattern

The skill content follows a **workflow-based organization**:

```mermaid
graph LR
    Q1["User Query"]
    
    A1["When to Use This Skill<br/>Lines 14-28"]
    A2["Core Principles<br/>Lines 30-67"]
    A3["Testing Strategy Framework<br/>Lines 116-172"]
    A4["Code Structure Standards<br/>Lines 173-227"]
    A5["Module Development<br/>Lines 315-350"]
    A6["CI/CD Integration<br/>Lines 352-371"]
    A7["Security & Compliance<br/>Lines 373-398"]
    A8["Version Management<br/>Lines 399-432"]
    
    REF["References section<br/>Lines 499-510"]
    
    Q1 --> A1
    A1 --> A2
    A2 --> A3
    A3 --> A4
    A4 --> A5
    A5 --> A6
    A6 --> A7
    A7 --> A8
    A8 --> REF
```

Each section is **self-contained** and can be referenced independently by Claude without requiring sequential reading.

**Sources:** [SKILL.md:1-8](), [SKILL.md:14-28](), [SKILL.md:30-517](), [CLAUDE.md:111-123]()

---

## Progressive Disclosure Implementation

The progressive disclosure pattern is the core architectural innovation that enables token efficiency. It works by structuring content into three loading stages:

### Three-Stage Loading Pattern

```mermaid
graph TB
    subgraph Stage1["Stage 1: Metadata Scan (~100 tokens)"]
        S1A["Read marketplace.json"]
        S1B["Read SKILL.md frontmatter"]
        S1C["Match against query"]
    end
    
    subgraph Stage2["Stage 2: Core Load (~4.4K tokens)"]
        S2A["Load full SKILL.md"]
        S2B["Testing Strategy Framework"]
        S2C["Code Structure Standards"]
        S2D["Module Development"]
        S2E["Quick Reference Tables"]
    end
    
    subgraph Stage3["Stage 3: On-Demand References (0-7K tokens per file)"]
        S3A["module-patterns.md<br/>For complex module questions"]
        S3B["quick-reference.md<br/>For command lookup"]
        S3C["code-patterns.md<br/>For version-specific features"]
        S3D["ci-cd-workflows.md<br/>For pipeline setup"]
        S3E["security-compliance.md<br/>For security scanning"]
        S3F["testing-frameworks.md<br/>For testing deep-dive"]
    end
    
    S1A --> S1B
    S1B --> S1C
    S1C -->|"Skill matches"| S2A
    S2A --> S2B
    S2B --> S2C
    S2C --> S2D
    S2D --> S2E
    
    S2E -.->|"If needed"| S3A
    S2E -.->|"If needed"| S3B
    S2E -.->|"If needed"| S3C
    S2E -.->|"If needed"| S3D
    S2E -.->|"If needed"| S3E
    S2E -.->|"If needed"| S3F
```

### Token Budget Allocation

| Stage | Content | Token Count | Loading Condition |
|-------|---------|-------------|-------------------|
| **Metadata** | marketplace.json + frontmatter | ~100 | Always (skill discovery) |
| **Core** | SKILL.md full content | ~4,400 | Skill activated |
| **Reference: Modules** | module-patterns.md | ~7,000 | Complex module architecture questions |
| **Reference: Commands** | quick-reference.md | ~3,800 | Command syntax lookup |
| **Reference: Features** | code-patterns.md | ~5,100 | Version-specific feature questions |
| **Reference: CI/CD** | ci-cd-workflows.md | ~2,300 | Pipeline setup questions |
| **Reference: Security** | security-compliance.md | ~2,500 | Security scanning questions |
| **Reference: Testing** | testing-frameworks.md | ~3,400 | Testing framework deep-dive |

**Total Available:** ~30,400 tokens
**Typical Usage:** 4,500-12,000 tokens (85-60% of total content unused)

### Reference Loading Mechanism

The SKILL.md file includes **explicit reference links** that Claude can follow:

```markdown
**For detailed module patterns, see:**
- **[Module Patterns Guide](references/module-patterns.md)** - Module structure, variable/output best practices, ✅ DO vs ❌ DON'T patterns
```

When Claude encounters a query requiring detailed module guidance, it:
1. Identifies the need from the query context
2. Loads the referenced file (`references/module-patterns.md`)
3. Incorporates that additional ~7K tokens into the response context
4. Generates a response using both core and reference content

**Sources:** [SKILL.md:348-350](), [SKILL.md:499-510](), [CLAUDE.md:46-63](), [CLAUDE.md:66-82]()

---

## Content Distribution Strategy

The distribution of content across files follows a **usage frequency** pattern:

### Core Content (SKILL.md ~4.4K tokens)

**High-frequency content** loaded on every activation:
- Testing decision matrix (lines 119-129)
- Count vs for_each comparison (lines 229-271)
- Variable/resource naming conventions (lines 68-115)
- Block ordering standards (lines 175-227)
- Version management quick reference (lines 399-432)

### Reference Files (~26K tokens distributed)

**Lower-frequency specialized content:**

1. **module-patterns.md** (~7K tokens) - Deepest coverage, lowest frequency
   - Detailed module hierarchy explanations
   - Variable/output best practices with extensive examples
   - DO/DON'T pattern catalogs

2. **quick-reference.md** (~3.8K tokens) - Medium coverage, high frequency
   - Command cheat sheets
   - Troubleshooting flowcharts
   - Migration path guides

3. **code-patterns.md** (~5.1K tokens) - Medium coverage, medium frequency
   - Modern Terraform features by version
   - Refactoring patterns
   - Advanced locals usage

4. **ci-cd-workflows.md** (~2.3K tokens) - Specific use case
   - GitHub Actions templates
   - GitLab CI templates
   - Atlantis integration

5. **security-compliance.md** (~2.5K tokens) - Specific use case
   - Trivy/Checkov integration
   - Secrets management patterns
   - Compliance frameworks

6. **testing-frameworks.md** (~3.4K tokens) - Deep-dive content
   - Static analysis detailed guide
   - Native test framework patterns
   - Terratest integration

### Content Selection Algorithm

```mermaid
flowchart TD
    Q["User Query"]
    
    CHECK1{"Contains 'module'<br/>architecture keywords?"}
    CHECK2{"Contains 'command'<br/>or 'how to' syntax?"}
    CHECK3{"Contains version number<br/>(1.6, 1.9, etc)?"}
    CHECK4{"Contains 'ci', 'pipeline',<br/>'github actions'?"}
    CHECK5{"Contains 'security',<br/>'trivy', 'checkov'?"}
    CHECK6{"Contains 'test'<br/>framework names?"}
    
    CORE["Load SKILL.md only<br/>~4.4K tokens"]
    MOD["+ module-patterns.md<br/>~7K tokens"]
    QUICK["+ quick-reference.md<br/>~3.8K tokens"]
    CODE["+ code-patterns.md<br/>~5.1K tokens"]
    CI["+ ci-cd-workflows.md<br/>~2.3K tokens"]
    SEC["+ security-compliance.md<br/>~2.5K tokens"]
    TEST["+ testing-frameworks.md<br/>~3.4K tokens"]
    
    Q --> CHECK1
    CHECK1 -->|Yes| MOD
    CHECK1 -->|No| CHECK2
    
    CHECK2 -->|Yes| QUICK
    CHECK2 -->|No| CHECK3
    
    CHECK3 -->|Yes| CODE
    CHECK3 -->|No| CHECK4
    
    CHECK4 -->|Yes| CI
    CHECK4 -->|No| CHECK5
    
    CHECK5 -->|Yes| SEC
    CHECK5 -->|No| CHECK6
    
    CHECK6 -->|Yes| TEST
    CHECK6 -->|No| CORE
```

**Sources:** [CLAUDE.md:66-82](), [SKILL.md:499-510]()

---

## Version Synchronization System

The terraform-skill system maintains version consistency across **three locations**:

### Version Locations

```mermaid
graph TB
    V1[".claude-plugin/marketplace.json<br/>root.version"]
    V2[".claude-plugin/marketplace.json<br/>plugins[0].version"]
    V3["SKILL.md<br/>metadata.version"]
    TAG["Git Tag<br/>v1.5.0"]
    
    RELEASE[".github/workflows/automated-release.yml<br/>Semantic versioning automation"]
    
    RELEASE -->|"Updates"| V1
    RELEASE -->|"Updates"| V2
    RELEASE -->|"Updates"| V3
    RELEASE -->|"Creates"| TAG
    
    V1 -.->|"Must match"| V2
    V2 -.->|"Must match"| V3
    V3 -.->|"Must match"| TAG
```

### Validation Rules

The system enforces these rules via automation:
1. `marketplace.json` root `version` MUST equal `plugins[0].version`
2. `SKILL.md` frontmatter `metadata.version` MUST equal marketplace versions
3. Git tag format MUST be `v{version}` (e.g., `v1.5.0`)
4. All three-way synchronization happens automatically on merge to master

**Current Version:** 1.5.0 (as of latest release)

**Sources:** [.claude-plugin/marketplace.json:6](), [.claude-plugin/marketplace.json:26](), [SKILL.md:7]()

---

## File Size and Token Constraints

The architecture enforces specific constraints to maintain performance:

### Size Limits

| File | Current Size | Target | Status |
|------|--------------|--------|--------|
| `SKILL.md` | 524 lines | ~500 lines | ✅ Acceptable (comprehensive core) |
| `SKILL.md` | ~17.7K chars | N/A | ~4,400 tokens |
| `module-patterns.md` | 1,126 lines | N/A | ~7,000 tokens |
| `code-patterns.md` | 859 lines | N/A | ~5,100 tokens |
| `quick-reference.md` | 600 lines | N/A | ~3,800 tokens |
| `testing-frameworks.md` | 563 lines | N/A | ~3,400 tokens |
| `ci-cd-workflows.md` | 473 lines | N/A | ~2,300 tokens |
| `security-compliance.md` | 470 lines | N/A | ~2,500 tokens |

### Token Calculation

Approximate conversion: **4 characters = 1 token**

This ratio varies by content type:
- Code blocks: ~3.5 chars/token (more efficient)
- Prose text: ~4.5 chars/token (less efficient)
- Markdown tables: ~4 chars/token (average)

The validation workflow at [.github/workflows/validate.yml]() includes file size checks with warnings at 500 lines for SKILL.md.

**Sources:** [CLAUDE.md:66-82](), [CLAUDE.md:76](), [CLAUDE.md:195-198]()

---

## Metadata-to-Runtime Mapping

The following diagram shows how static metadata becomes runtime behavior:

```mermaid
graph TB
    subgraph Static["Static Configuration"]
        MJ_DESC[".claude-plugin/marketplace.json:15<br/>plugins[0].description"]
        MJ_KEYWORDS[".claude-plugin/marketplace.json:18-25<br/>plugins[0].keywords[]"]
        SKILL_FRONT["SKILL.md:1-8<br/>YAML frontmatter"]
        SKILL_WHEN["SKILL.md:14-28<br/>'When to Use This Skill'"]
    end
    
    subgraph Runtime["Runtime Behavior"]
        DISCOVERY["Skill Discovery<br/>Match query to keywords"]
        ACTIVATION["Skill Activation<br/>Load if description matches"]
        CONTEXT["Context Loading<br/>Inject SKILL.md content"]
        RESPONSE["Response Generation<br/>Apply best practices"]
    end
    
    MJ_KEYWORDS -->|"terraform, opentofu, testing, ci-cd, modules"| DISCOVERY
    MJ_DESC -->|"working with Terraform or OpenTofu"| ACTIVATION
    SKILL_FRONT -->|"name, version, license"| CONTEXT
    SKILL_WHEN -->|"Activate when: creating modules, testing, CI/CD"| ACTIVATION
    
    DISCOVERY --> ACTIVATION
    ACTIVATION --> CONTEXT
    CONTEXT --> RESPONSE
```

### Activation Trigger Examples

Based on [.claude-plugin/marketplace.json:15]() and [SKILL.md:16-23](), these queries activate the skill:

✅ **Activates:**
- "Create a Terraform module"
- "Set up testing for OpenTofu"
- "Review this Terraform configuration"
- "Choose between terraform test and Terratest"
- "Implement Trivy scanning in CI/CD"

❌ **Does Not Activate:**
- "What is Terraform?" (basic syntax question)
- "AWS S3 bucket API reference" (provider-specific docs)
- "How do I use Kubernetes?" (unrelated to Terraform/OpenTofu)

**Sources:** [.claude-plugin/marketplace.json:15](), [SKILL.md:14-28]()

---

## Repository File Structure

Complete file system layout with architectural role annotations:

```
terraform-skill/
├── .claude-plugin/
│   └── marketplace.json           # Discovery Layer: Plugin metadata (28.17 importance)
├── .github/
│   └── workflows/
│       ├── automated-release.yml  # Automation: Version sync (8.94 importance)
│       └── validate.yml           # Automation: Content validation (5.50 importance)
├── references/                    # Reference Layer: On-demand content
│   ├── ci-cd-workflows.md         # ~2.3K tokens (0.70 importance)
│   ├── code-patterns.md           # ~5.1K tokens (2.00 importance)
│   ├── module-patterns.md         # ~7.0K tokens (2.70 importance)
│   ├── quick-reference.md         # ~3.8K tokens (2.70 importance)
│   ├── security-compliance.md     # ~2.5K tokens (0.70 importance)
│   └── testing-frameworks.md      # ~3.4K tokens (N/A - new file)
├── SKILL.md                       # Core Layer: Primary content (10.14 importance)
├── README.md                      # Documentation: User-facing (6.24 importance)
├── CLAUDE.md                      # Documentation: Contributor-facing (2.94 importance)
├── CONTRIBUTING.md                # Documentation: Process (1.50 importance)
├── CHANGELOG.md                   # Documentation: History (21.42 importance)
├── LICENSE                        # Legal: Apache 2.0 (2.00 importance)
└── .gitignore                     # Config: Exclusions (0.70 importance)
```

**Importance Values:** Based on edit frequency and system criticality (from high-level diagrams)

**Sources:** [CLAUDE.md:17-32]()

---

## Progressive Disclosure Performance Analysis

### Token Efficiency Calculation

**Scenario 1: Simple module creation query**
- Metadata scan: 100 tokens
- SKILL.md core: 4,400 tokens
- No references loaded
- **Total: 4,500 tokens (15% of available content)**

**Scenario 2: Complex module with testing**
- Metadata scan: 100 tokens
- SKILL.md core: 4,400 tokens
- module-patterns.md: 7,000 tokens
- testing-frameworks.md: 3,400 tokens
- **Total: 14,900 tokens (49% of available content)**

**Scenario 3: CI/CD pipeline setup**
- Metadata scan: 100 tokens
- SKILL.md core: 4,400 tokens
- ci-cd-workflows.md: 2,300 tokens
- security-compliance.md: 2,500 tokens
- **Total: 9,300 tokens (31% of available content)**

### Efficiency Gains

| Approach | Token Cost | Efficiency |
|----------|-----------|------------|
| **Load all content** | ~30,400 tokens | Baseline (0% savings) |
| **Progressive (simple)** | ~4,500 tokens | 85% savings |
| **Progressive (complex)** | ~14,900 tokens | 51% savings |
| **Progressive (CI/CD)** | ~9,300 tokens | 69% savings |
| **Average progressive** | ~9,567 tokens | **68% savings** |

This architecture enables **68% average token reduction** while maintaining full capability coverage.

**Sources:** [CLAUDE.md:66-82]()

---

## Summary

The terraform-skill architecture achieves efficient Claude Code integration through:

1. **Plugin Definition System** - marketplace.json provides machine-readable metadata for discovery
2. **Progressive Disclosure Pattern** - Three-tier loading (metadata → core → references) reduces token usage by 56-70%
3. **Content Organization** - Workflow-based structure with explicit reference links enables targeted loading
4. **Version Synchronization** - Automated three-way version sync across marketplace.json, SKILL.md, and git tags
5. **Token Budget Management** - ~30.4K tokens available, typical usage 4.5-12K tokens

This design prioritizes **token efficiency without sacrificing comprehensiveness**, making it a model for large-scale Claude Code skills.

**Sources:** [.claude-plugin/marketplace.json:1-29](), [SKILL.md:1-517](), [CLAUDE.md:1-346]()

---

# Page: Plugin Definition System

# Plugin Definition System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)

</details>



## Purpose and Scope

The Plugin Definition System is the foundational integration layer that enables Claude Code to discover, activate, and utilize the terraform-skill. This system is implemented through the `marketplace.json` file, which serves as the machine-readable contract between the skill and Claude's plugin ecosystem.

This document covers the structure, metadata fields, discovery mechanism, and integration points of the plugin definition. For information about the skill content itself, see [Core Skill Content](#4.1). For the progressive loading architecture, see [Progressive Disclosure Pattern](#3.2).

**Sources:** [.claude-plugin/marketplace.json:1-29]()

---

## File Location and Structure

The plugin definition resides at `.claude-plugin/marketplace.json` and follows a two-tier structure:

| Level | Purpose | Key Fields |
|-------|---------|------------|
| **Marketplace** | Root-level metadata about the skill publisher | `name`, `owner`, `version`, `metadata` |
| **Plugin** | Individual skill definitions within the marketplace | `name`, `description`, `source`, `category`, `keywords`, `version` |

This dual-level structure allows a single marketplace to contain multiple related skills, though the terraform-skill marketplace currently contains a single plugin.

**Sources:** [.claude-plugin/marketplace.json:1-29]()

---

## Marketplace Root Metadata

### marketplace.json Root Structure

```mermaid
graph TD
    ROOT["marketplace.json"]
    
    NAME["name: 'antonbabenko'<br/>Publisher identifier"]
    OWNER["owner.name: 'Anton Babenko'<br/>Human-readable owner"]
    VERSION["version: '1.5.0'<br/>Marketplace version"]
    META["metadata object"]
    PLUGINS["plugins array"]
    
    META_DESC["metadata.description<br/>Marketplace summary"]
    META_REPO["metadata.repository<br/>GitHub URL"]
    META_LIC["metadata.license<br/>'Apache-2.0'"]
    
    ROOT --> NAME
    ROOT --> OWNER
    ROOT --> VERSION
    ROOT --> META
    ROOT --> PLUGINS
    
    META --> META_DESC
    META --> META_REPO
    META --> META_LIC
```

**Sources:** [.claude-plugin/marketplace.json:2-11]()

### Field Specifications

| Field | Type | Purpose | Example Value |
|-------|------|---------|---------------|
| `name` | string | Marketplace identifier (kebab-case) | `"antonbabenko"` |
| `owner.name` | string | Publisher display name | `"Anton Babenko"` |
| `version` | string | Semantic version of marketplace | `"1.5.0"` |
| `metadata.description` | string | Human-readable marketplace summary | See line 8 |
| `metadata.repository` | string | Source code URL | `"https://github.com/antonbabenko/terraform-skill"` |
| `metadata.license` | string | SPDX license identifier | `"Apache-2.0"` |

**Sources:** [.claude-plugin/marketplace.json:2-11]()

---

## Plugin Definition Schema

### terraform-skill Plugin Object

The `plugins` array contains the actual skill definitions. Each plugin object defines how Claude discovers and activates the skill:

```mermaid
graph LR
    PLUGIN["Plugin Object"]
    
    P_NAME["name: 'terraform-skill'<br/>Unique plugin ID"]
    P_DESC["description<br/>Activation trigger phrase"]
    P_SOURCE["source: './'<br/>Content location"]
    P_CAT["category: 'development'"]
    P_KEYS["keywords array<br/>6 terms"]
    P_VER["version: '1.5.0'<br/>Plugin version"]
    
    PLUGIN --> P_NAME
    PLUGIN --> P_DESC
    PLUGIN --> P_SOURCE
    PLUGIN --> P_CAT
    PLUGIN --> P_KEYS
    PLUGIN --> P_VER
    
    P_KEYS --> K1["terraform"]
    P_KEYS --> K2["opentofu"]
    P_KEYS --> K3["infrastructure-as-code"]
    P_KEYS --> K4["testing"]
    P_KEYS --> K5["ci-cd"]
    P_KEYS --> K6["modules"]
```

**Sources:** [.claude-plugin/marketplace.json:13-27]()

### Critical Fields Breakdown

#### name
- **Location:** [.claude-plugin/marketplace.json:14]()
- **Value:** `"terraform-skill"`
- **Purpose:** Unique identifier for the plugin within the marketplace
- **Usage:** Referenced in CLI commands and skill activation logs

#### description
- **Location:** [.claude-plugin/marketplace.json:15]()
- **Value:** 207-character activation trigger specification
- **Purpose:** Defines when Claude should activate this skill
- **Key Phrases:**
  - "working with Terraform or OpenTofu"
  - "creating modules"
  - "writing tests (native test framework, Terratest)"
  - "setting up CI/CD pipelines"
  - "reviewing configurations"
  - "choosing between testing approaches"
  - "debugging state issues"
  - "implementing security scanning (trivy, checkov)"
  - "infrastructure-as-code architecture decisions"

This description acts as the primary matching logic for skill activation.

**Sources:** [.claude-plugin/marketplace.json:15]()

#### source
- **Location:** [.claude-plugin/marketplace.json:16]()
- **Value:** `"./"`
- **Purpose:** Relative path to skill content directory
- **Behavior:** Points to the directory containing `SKILL.md`
- **Resolution:** Claude resolves this relative to `.claude-plugin/` directory

**Sources:** [.claude-plugin/marketplace.json:16]()

#### category
- **Location:** [.claude-plugin/marketplace.json:17]()
- **Value:** `"development"`
- **Purpose:** Categorization for marketplace browsing and filtering
- **Standard Categories:** development, productivity, communication, etc.

**Sources:** [.claude-plugin/marketplace.json:17]()

#### keywords
- **Location:** [.claude-plugin/marketplace.json:18-25]()
- **Count:** 6 terms
- **Values:** `terraform`, `opentofu`, `infrastructure-as-code`, `testing`, `ci-cd`, `modules`
- **Purpose:** Search indexing and discovery
- **Matching:** Used in conjunction with description for activation decisions

**Sources:** [.claude-plugin/marketplace.json:18-25]()

#### version
- **Location:** [.claude-plugin/marketplace.json:26]()
- **Value:** `"1.5.0"`
- **Format:** Semantic versioning (MAJOR.MINOR.PATCH)
- **Synchronization:** Must match marketplace root version [.claude-plugin/marketplace.json:6]() and `SKILL.md` metadata
- **Management:** Automatically updated by automated-release workflow (see [Release Automation](#6.2))

**Sources:** [.claude-plugin/marketplace.json:6,26]()

---

## Claude Discovery and Activation Process

### Discovery Flow

```mermaid
sequenceDiagram
    participant User
    participant Claude as "Claude Code"
    participant Registry as "Plugin Registry"
    participant Local as "Local Plugin Cache"
    participant MJ as "marketplace.json"
    participant SKILL as "SKILL.md"
    
    User->>Claude: Query about Terraform/OpenTofu
    Claude->>Registry: Check for relevant skills
    Registry->>Local: Return matching marketplace
    Local->>MJ: Load marketplace.json
    MJ->>Claude: Return metadata + plugins[]
    
    Note over Claude: Match query against<br/>description + keywords
    
    alt Skill Activated
        Claude->>MJ: Read source field ("./")
        Claude->>SKILL: Load SKILL.md from source path
        SKILL->>Claude: Return skill content (~4.4K tokens)
        Claude->>User: Generate response with skill knowledge
    else No Match
        Claude->>User: Generate generic response
    end
```

**Sources:** [.claude-plugin/marketplace.json:14-16]()

### Activation Trigger Matching

Claude performs a multi-factor match to determine skill activation:

| Factor | Source | Weight | Example |
|--------|--------|--------|---------|
| **Keyword Match** | `keywords[]` | High | User mentions "terraform", "opentofu" |
| **Description Phrases** | `description` | Very High | User asks about "module testing" or "CI/CD pipelines" |
| **Context Analysis** | Query semantics | Medium | User working in `.tf` files or mentioning infrastructure |
| **Category Relevance** | `category` | Low | Development-related queries |

The `description` field at [.claude-plugin/marketplace.json:15]() is the primary activation trigger due to its specificity.

**Sources:** [.claude-plugin/marketplace.json:15,18-25]()

---

## Version Synchronization System

### Three-Way Version Sync

The plugin definition participates in a critical version synchronization system:

```mermaid
graph TD
    COMMIT["Git Commit with<br/>Conventional Commits"]
    
    RELEASE["automated-release.yml<br/>Analyzes commit messages"]
    
    VERSION["Calculated Version<br/>e.g., 1.5.0"]
    
    MP_ROOT["marketplace.json<br/>root version field<br/>Line 6"]
    
    MP_PLUGIN["marketplace.json<br/>plugins[0].version<br/>Line 26"]
    
    SKILL["SKILL.md<br/>frontmatter metadata"]
    
    TAG["Git Tag<br/>v1.5.0"]
    
    COMMIT --> RELEASE
    RELEASE --> VERSION
    VERSION --> MP_ROOT
    VERSION --> MP_PLUGIN
    VERSION --> SKILL
    VERSION --> TAG
    
    MP_ROOT -.->|"Must match"| MP_PLUGIN
    MP_PLUGIN -.->|"Must match"| SKILL
```

**Sources:** [.claude-plugin/marketplace.json:6,26]()

### Version Field Locations

| Location | Line | Field Path | Current Value |
|----------|------|------------|---------------|
| Marketplace root | 6 | `version` | `"1.5.0"` |
| Plugin definition | 26 | `plugins[0].version` | `"1.5.0"` |
| Skill metadata | N/A | See SKILL.md | `1.5.0` |
| Git tag | N/A | Repository tag | `v1.5.0` |

The automated-release workflow ensures all four locations remain synchronized. See [Version Synchronization](#6.3) for details.

**Sources:** [.claude-plugin/marketplace.json:6,26]()

---

## Source Resolution and Content Loading

### Path Resolution

```mermaid
graph LR
    INSTALL["Installation Directory<br/>~/.claude/skills/"]
    
    MARKETPLACE["antonbabenko/terraform-skill/"]
    
    PLUGIN_DIR[".claude-plugin/"]
    
    MJ["marketplace.json<br/>source: './'"]
    
    ROOT["Resolved Path:<br/>~/.claude/skills/antonbabenko/<br/>terraform-skill/"]
    
    SKILL["SKILL.md<br/>Main content file"]
    
    REF["references/<br/>*.md files"]
    
    INSTALL --> MARKETPLACE
    MARKETPLACE --> PLUGIN_DIR
    PLUGIN_DIR --> MJ
    MJ --> ROOT
    ROOT --> SKILL
    ROOT --> REF
```

**Sources:** [.claude-plugin/marketplace.json:16]()

### Source Field Behavior

The `source` field at [.claude-plugin/marketplace.json:16]() uses relative path resolution:

1. **Base Path:** `.claude-plugin/` directory containing `marketplace.json`
2. **Source Value:** `"./"`
3. **Resolution:** One directory up from `.claude-plugin/`, pointing to repository root
4. **Expected Content:** `SKILL.md` at resolved path
5. **Additional Content:** `references/` directory with extended documentation

This design allows the skill content to coexist with the plugin definition while maintaining clean separation.

**Sources:** [.claude-plugin/marketplace.json:16]()

---

## Relationship to Other System Components

### Component Dependencies

```mermaid
graph TD
    MJ["marketplace.json<br/>Plugin Definition"]
    
    SKILL["SKILL.md<br/>Core Content<br/>Importance: 10.14"]
    
    VALIDATE["validate.yml<br/>Validation Workflow<br/>Importance: 5.50"]
    
    RELEASE["automated-release.yml<br/>Release Automation<br/>Importance: 8.94"]
    
    CHANGELOG["CHANGELOG.md<br/>Release History<br/>Importance: 21.42"]
    
    README["README.md<br/>User Documentation<br/>Importance: 6.24"]
    
    MJ -->|"source field points to"| SKILL
    
    VALIDATE -->|"Validates frontmatter"| MJ
    VALIDATE -->|"Checks version sync"| MJ
    
    RELEASE -->|"Updates version fields"| MJ
    RELEASE -->|"Creates release from"| MJ
    RELEASE -->|"Updates"| CHANGELOG
    
    README -->|"Documents installation via"| MJ
```

**Sources:** [.claude-plugin/marketplace.json:1-29]()

### Integration Points

| Component | Interaction | Direction |
|-----------|-------------|-----------|
| **SKILL.md** | Content loading via `source` | marketplace.json → SKILL.md |
| **validate.yml** | Version validation | validate.yml → marketplace.json |
| **automated-release.yml** | Version updates | automated-release.yml → marketplace.json |
| **README.md** | Installation documentation | README.md → marketplace.json |
| **Claude Code** | Skill discovery and activation | Claude → marketplace.json |

**Sources:** [.claude-plugin/marketplace.json:6,16,26]()

---

## Metadata Best Practices

### Description Field Guidelines

The `description` field at [.claude-plugin/marketplace.json:15]() follows specific patterns for optimal activation:

1. **Action-Oriented Phrases:** "Use when working with..."
2. **Explicit Tools:** Name specific tools (Terratest, trivy, checkov)
3. **Activity Coverage:** List distinct activities (creating, writing, setting up, reviewing)
4. **Framework Variants:** Include both Terraform and OpenTofu
5. **Decision-Making Context:** "choosing between testing approaches", "architecture decisions"

**Anti-patterns to avoid:**
- Generic descriptions ("Helps with Terraform")
- Missing tool names (rely on brand names, not descriptions)
- Vague activities ("helps improve code")

**Sources:** [.claude-plugin/marketplace.json:15]()

### Keyword Selection

The `keywords` array at [.claude-plugin/marketplace.json:18-25]() balances breadth and specificity:

| Type | Examples | Purpose |
|------|----------|---------|
| **Brand Terms** | `terraform`, `opentofu` | Direct tool matching |
| **Category Terms** | `infrastructure-as-code` | Domain identification |
| **Activity Terms** | `testing`, `ci-cd`, `modules` | Task matching |

**Keyword count:** 6 (optimal for Claude's matching algorithm)

**Sources:** [.claude-plugin/marketplace.json:18-25]()

---

## Validation and Quality Assurance

### Automated Validation Checks

The validate workflow performs several checks on `marketplace.json`:

```mermaid
graph TD
    VALIDATE["validate.yml Workflow"]
    
    CHECK1["Frontmatter Validation<br/>Required fields present"]
    CHECK2["Version Synchronization<br/>Root vs plugin version"]
    CHECK3["JSON Schema Validation<br/>Valid JSON structure"]
    CHECK4["Description Length<br/>Meaningful content"]
    
    VALIDATE --> CHECK1
    VALIDATE --> CHECK2
    VALIDATE --> CHECK3
    VALIDATE --> CHECK4
    
    CHECK1 --> PASS{All Pass?}
    CHECK2 --> PASS
    CHECK3 --> PASS
    CHECK4 --> PASS
    
    PASS -->|Yes| MERGE["Allow Merge"]
    PASS -->|No| BLOCK["Block PR"]
```

**Sources:** [.claude-plugin/marketplace.json:1-29]()

### Version Validation Rules

| Rule | Check | Enforcement |
|------|-------|-------------|
| **Root-Plugin Match** | `version` == `plugins[0].version` | Automated (validate.yml) |
| **Semantic Versioning** | Format: `MAJOR.MINOR.PATCH` | Automated (automated-release.yml) |
| **No Manual Bumps** | Changed only by automation | PR review |
| **SKILL.md Sync** | Matches frontmatter version | Automated (validate.yml) |

**Sources:** [.claude-plugin/marketplace.json:6,26]()

---

## Usage in Installation Flow

### Marketplace Installation Command

```mermaid
sequenceDiagram
    participant User
    participant CLI as "Claude CLI"
    participant Registry as "Plugin Registry"
    participant Local as "~/.claude/skills/"
    participant MJ as "marketplace.json"
    
    User->>CLI: /plugin marketplace add<br/>antonbabenko/terraform-skill
    CLI->>Registry: Fetch marketplace metadata
    Registry->>CLI: Return marketplace.json
    CLI->>Local: Clone repository to<br/>~/.claude/skills/antonbabenko/terraform-skill/
    Local->>MJ: Read .claude-plugin/marketplace.json
    MJ->>CLI: Validate plugin definition
    CLI->>User: Installation successful
    
    Note over User,CLI: Skill now available in Claude Code
```

**Installation command referenced in README.md:**
```
/plugin marketplace add antonbabenko/terraform-skill
```

The `marketplace.json` is the first file Claude reads after cloning the repository to determine available plugins and their configuration.

**Sources:** [.claude-plugin/marketplace.json:1-29]()

---

## Schema Reference

### Complete JSON Schema

```json
{
  "type": "object",
  "required": ["name", "owner", "version", "plugins"],
  "properties": {
    "name": {
      "type": "string",
      "description": "Marketplace identifier"
    },
    "owner": {
      "type": "object",
      "properties": {
        "name": {"type": "string"}
      }
    },
    "version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "description": {"type": "string"},
        "repository": {"type": "string"},
        "license": {"type": "string"}
      }
    },
    "plugins": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "description", "source", "version"],
        "properties": {
          "name": {"type": "string"},
          "description": {"type": "string"},
          "source": {"type": "string"},
          "category": {"type": "string"},
          "keywords": {
            "type": "array",
            "items": {"type": "string"}
          },
          "version": {"type": "string"}
        }
      }
    }
  }
}
```

**Sources:** [.claude-plugin/marketplace.json:1-29]()

---

## Summary

The Plugin Definition System (`marketplace.json`) serves as the critical integration point between Claude Code and the terraform-skill. With an importance score of 28.17, it is the single most important file in the codebase, responsible for:

1. **Discovery:** Enabling Claude to find and identify the skill
2. **Activation:** Defining when the skill should be loaded based on user queries
3. **Routing:** Pointing to skill content via the `source` field
4. **Versioning:** Participating in three-way version synchronization
5. **Metadata:** Providing human-readable information for marketplace display

The dual-structure design (marketplace root + plugin array) allows for extensibility while maintaining a clean, focused definition for the terraform-skill plugin.

**Sources:** [.claude-plugin/marketplace.json:1-29]()

---

# Page: Progressive Disclosure Pattern

# Progressive Disclosure Pattern

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CLAUDE.md](CLAUDE.md)
- [SKILL.md](SKILL.md)

</details>



## Purpose and Scope

The progressive disclosure pattern is the core architectural strategy used by terraform-skill to minimize token consumption while maintaining comprehensive Terraform/OpenTofu guidance. This pattern organizes content into three tiers—metadata, core content, and reference files—that Claude Code loads incrementally based on query requirements. This document explains the three-stage loading architecture, token budget distribution, file organization strategy, and implementation mechanisms.

For information about the overall content architecture and file responsibilities, see [Content Organization](#3.3). For details on how the plugin discovery system works, see [Plugin Definition System](#3.1).

---

## Three-Stage Loading Architecture

The progressive disclosure pattern implements a three-tier loading system that optimizes token usage by deferring content loading until needed.

### Loading Sequence Diagram

```mermaid
flowchart TD
    QUERY["User Query: Terraform/OpenTofu task"]
    
    subgraph Stage1["Stage 1: Discovery (~100 tokens)"]
        METADATA["marketplace.json frontmatter<br/>name, description, keywords"]
        ACTIVATION["Activation trigger matching"]
    end
    
    subgraph Stage2["Stage 2: Core Content (~4,400 tokens)"]
        SKILL["SKILL.md loaded<br/>Testing frameworks<br/>Module patterns<br/>Quick reference tables"]
        DECISION["Apply decision matrices<br/>and core guidance"]
    end
    
    subgraph Stage3["Stage 3: On-Demand References (0-7K tokens each)"]
        REF_MODULE["references/module-patterns.md<br/>~7K tokens"]
        REF_QUICK["references/quick-reference.md<br/>~3.8K tokens"]
        REF_CODE["references/code-patterns.md<br/>~5.1K tokens"]
        REF_CI["references/ci-cd-workflows.md<br/>~2.3K tokens"]
        REF_SEC["references/security-compliance.md<br/>~2.5K tokens"]
    end
    
    QUERY --> METADATA
    METADATA --> ACTIVATION
    ACTIVATION -->|"Match found"| SKILL
    SKILL --> DECISION
    
    DECISION -.->|"Complex module query"| REF_MODULE
    DECISION -.->|"Command lookup"| REF_QUICK
    DECISION -.->|"Version-specific features"| REF_CODE
    DECISION -.->|"Pipeline setup"| REF_CI
    DECISION -.->|"Security scanning"| REF_SEC
    
    DECISION --> RESPONSE["Generate response with<br/>appropriate detail level"]
```

Sources: [SKILL.md:500-511](), [CLAUDE.md:46-64]()

### Stage Responsibilities

| Stage | Files | Token Cost | Always Loaded | Purpose |
|-------|-------|-----------|---------------|---------|
| **Discovery** | `.claude-plugin/marketplace.json` | ~100 tokens | Yes | Skill activation trigger matching |
| **Core** | `SKILL.md` | ~4,400 tokens | On activation | Essential patterns, decision matrices, quick reference |
| **References** | `references/*.md` (6 files) | 2.3K-7K per file | On demand only | Deep-dive guidance for specific topics |

**Total Available Content:** ~30.4K tokens  
**Typical Query Usage:** 4.5K-12K tokens (56-70% reduction vs. loading all content)

Sources: [CLAUDE.md:66-82](), [SKILL.md:1-8]()

---

## Token Budget Optimization

### Token Distribution

The skill's total content is strategically distributed across files to minimize default load while maintaining comprehensive coverage.

| File | Lines | Tokens | Load Trigger |
|------|-------|--------|--------------|
| `marketplace.json` | ~30 | ~100 | Always (skill discovery) |
| `SKILL.md` | 524 | ~4,400 | Skill activated |
| `references/module-patterns.md` | 1,126 | ~7,000 | Module development questions |
| `references/code-patterns.md` | 859 | ~5,100 | Modern features, version-specific guidance |
| `references/quick-reference.md` | 600 | ~3,800 | Command lookups, troubleshooting |
| `references/ci-cd-workflows.md` | 473 | ~2,300 | Pipeline setup, automation |
| `references/security-compliance.md` | 470 | ~2,500 | Security scanning, compliance |
| `references/testing-frameworks.md` | 563 | ~3,400 | Testing framework deep-dives |

**Total:** 4,645 lines, ~30,400 tokens across 8 files

Sources: [CLAUDE.md:69-82](), [CLAUDE.md:22-28]()

### Query Type Token Usage

```mermaid
graph LR
    subgraph Simple["Simple Query: 'Format my Terraform code'"]
        S_META["metadata.json<br/>100 tokens"]
        S_SKILL["SKILL.md<br/>4,400 tokens"]
        S_TOTAL["Total: ~4.5K tokens"]
    end
    
    subgraph Medium["Medium Query: 'Create module with tests'"]
        M_META["metadata.json<br/>100 tokens"]
        M_SKILL["SKILL.md<br/>4,400 tokens"]
        M_REF["module-patterns.md<br/>7,000 tokens"]
        M_TOTAL["Total: ~11.5K tokens"]
    end
    
    subgraph Complex["Complex Query: 'Set up CI/CD with security scanning'"]
        C_META["metadata.json<br/>100 tokens"]
        C_SKILL["SKILL.md<br/>4,400 tokens"]
        C_CI["ci-cd-workflows.md<br/>2,300 tokens"]
        C_SEC["security-compliance.md<br/>2,500 tokens"]
        C_TOTAL["Total: ~9.3K tokens"]
    end
    
    S_META --> S_SKILL
    S_SKILL --> S_TOTAL
    
    M_META --> M_SKILL
    M_SKILL --> M_REF
    M_REF --> M_TOTAL
    
    C_META --> C_SKILL
    C_SKILL --> C_CI
    C_SKILL --> C_SEC
    C_CI --> C_TOTAL
    C_SEC --> C_TOTAL
```

Sources: [CLAUDE.md:78-82]()

**Key Optimization:** Claude never loads all 30.4K tokens. The architecture ensures:
- Minimum load: 4.5K tokens (discovery + core)
- Typical load: 8-12K tokens (core + 1-2 references)
- Maximum theoretical load: 30.4K tokens (all references, rare)

---

## File Organization Strategy

### Core vs. Reference Content Split

The content split between `SKILL.md` and `references/*.md` follows specific architectural principles.

**SKILL.md Content (Core - Always Loaded on Activation):**
- Testing strategy decision matrices [SKILL.md:116-144]()
- Module development best practices summary [SKILL.md:315-350]()
- Count vs. for_each decision guide [SKILL.md:229-271]()
- Block ordering standards [SKILL.md:173-225]()
- Version constraint quick reference [SKILL.md:399-431]()
- CI/CD workflow stages overview [SKILL.md:352-371]()

**references/*.md Content (Deep-Dive - Loaded on Demand):**
- Detailed module architecture patterns
- Complete testing framework guides
- Full CI/CD pipeline templates
- Comprehensive security checklists
- Extended command reference tables

Sources: [CLAUDE.md:85-110](), [SKILL.md:500-511]()

### Directory Structure

```
terraform-skill/
├── .claude-plugin/
│   └── marketplace.json         # Stage 1: Discovery metadata
├── SKILL.md                      # Stage 2: Core content (~4.4K tokens)
└── references/                   # Stage 3: On-demand references
    ├── ci-cd-workflows.md        # 2.3K tokens
    ├── code-patterns.md          # 5.1K tokens
    ├── module-patterns.md        # 7K tokens
    ├── quick-reference.md        # 3.8K tokens
    ├── security-compliance.md    # 2.5K tokens
    └── testing-frameworks.md     # 3.4K tokens
```

Sources: [CLAUDE.md:16-32]()

### Content Categorization Principles

Content placement follows these rules:

| Content Type | Location | Example |
|--------------|----------|---------|
| **Decision frameworks** | `SKILL.md` | "Which testing approach?" table [SKILL.md:118-128]() |
| **Quick reference tables** | `SKILL.md` | Module type comparison [SKILL.md:36-42]() |
| **DO/DON'T examples** | `SKILL.md` | Singleton naming patterns [SKILL.md:85-100]() |
| **Detailed guides** | `references/` | Complete Terratest walkthrough |
| **Command templates** | `references/` | Full GitHub Actions workflow |
| **Extended checklists** | `references/` | Comprehensive security scanning setup |

Sources: [CLAUDE.md:85-110]()

---

## Content Loading Mechanism

### Metadata-Driven Discovery

The discovery phase uses YAML frontmatter in `.claude-plugin/marketplace.json` and `SKILL.md` to determine skill activation.

**marketplace.json Structure:**
```json
{
  "name": "terraform-skill",
  "description": "Use when working with Terraform or OpenTofu...",
  "source": "./"
}
```

**SKILL.md Frontmatter:**
```yaml
---
name: terraform-skill
description: Use when working with Terraform or OpenTofu - creating modules, 
  writing tests (native test framework, Terratest), setting up CI/CD pipelines...
license: Apache-2.0
metadata:
  author: Anton Babenko
  version: 1.5.0
---
```

Sources: [SKILL.md:1-8]()

### Activation Triggers

Claude Code evaluates activation based on explicit trigger conditions defined in `SKILL.md`.

```mermaid
flowchart TD
    QUERY["User Query Text"]
    
    PARSE["Parse query keywords"]
    
    CHECK_TERRAFORM["Contains: 'Terraform' OR 'OpenTofu'?"]
    CHECK_MODULE["Contains: 'module' OR 'configuration'?"]
    CHECK_TEST["Contains: 'test' OR 'testing'?"]
    CHECK_CICD["Contains: 'CI/CD' OR 'pipeline'?"]
    CHECK_SECURITY["Contains: 'security' OR 'scanning'?"]
    
    ACTIVATE["Load SKILL.md<br/>(4.4K tokens)"]
    SKIP["Skip skill<br/>(0 tokens)"]
    
    QUERY --> PARSE
    PARSE --> CHECK_TERRAFORM
    
    CHECK_TERRAFORM -->|Yes| CHECK_MODULE
    CHECK_TERRAFORM -->|No| SKIP
    
    CHECK_MODULE -->|Yes| ACTIVATE
    CHECK_TEST -->|Yes| ACTIVATE
    CHECK_CICD -->|Yes| ACTIVATE
    CHECK_SECURITY -->|Yes| ACTIVATE
    
    CHECK_MODULE -->|No| CHECK_TEST
    CHECK_TEST -->|No| CHECK_CICD
    CHECK_CICD -->|No| CHECK_SECURITY
    CHECK_SECURITY -->|No| SKIP
```

**Explicit Activation Conditions** [SKILL.md:14-28]():
- Creating new Terraform or OpenTofu configurations
- Setting up testing infrastructure
- Deciding between testing approaches
- Structuring multi-environment deployments
- Implementing CI/CD for IaC
- Reviewing or refactoring existing projects
- Choosing between module patterns

Sources: [SKILL.md:14-28](), [CLAUDE.md:46-64]()

### Reference File Loading

Reference files are loaded when `SKILL.md` explicitly mentions them or when Claude determines additional detail is needed.

**Explicit Reference Pattern in SKILL.md:**

```markdown
**For detailed module architecture, see:** 
[Code Patterns: Module Types & Hierarchy](references/code-patterns.md)
```
[SKILL.md:66]()

```markdown
**For complete CI/CD templates, see:**
- **[CI/CD Workflows Guide](references/ci-cd-workflows.md)** - GitHub Actions, 
  GitLab CI templates, cost optimization, automated cleanup
```
[SKILL.md:368-369]()

**Reference Link Format:**
- Markdown links to `references/*.md` files
- Descriptive anchor text indicating when to load
- Section-specific links when appropriate

Sources: [SKILL.md:66](), [SKILL.md:169-171](), [SKILL.md:227](), [SKILL.md:271](), [SKILL.md:313](), [SKILL.md:348-350](), [SKILL.md:368-370](), [SKILL.md:396-397](), [SKILL.md:431](), [SKILL.md:476](), [SKILL.md:503-509]()

---

## Implementation Details

### Frontmatter Metadata Requirements

Both `marketplace.json` and `SKILL.md` require specific metadata fields for proper discovery and loading.

**Required Fields:**

| Field | Location | Purpose | Example |
|-------|----------|---------|---------|
| `name` | Both | Skill identifier | `"terraform-skill"` |
| `description` | Both | Activation trigger keywords | `"Use when working with Terraform or OpenTofu..."` |
| `license` | `SKILL.md` | Legal terms | `"Apache-2.0"` |
| `metadata.version` | `SKILL.md` | Version tracking | `"1.5.0"` |
| `source` | `marketplace.json` | Content location | `"./"` |

Sources: [SKILL.md:1-8]()

### File Size Constraints

The architecture enforces soft limits to maintain token efficiency:

| File Type | Target Size | Current Size | Rationale |
|-----------|-------------|--------------|-----------|
| `SKILL.md` | < 500 lines | 524 lines | Core content should be scannable [CLAUDE.md:76-77]() |
| Reference files | No hard limit | 470-1,126 lines | Loaded on-demand, size less critical |

**Current Status:** `SKILL.md` slightly exceeds target by 24 lines, justified by comprehensive decision matrices and version-specific guidance. Future content growth should prioritize reference file expansion. [CLAUDE.md:319-328]()

Sources: [CLAUDE.md:76-82](), [CLAUDE.md:319-328]()

### Progressive Disclosure Section Pattern

`SKILL.md` implements a consistent pattern for deferring to reference files:

```markdown
## [Topic] Summary

[Essential information: decision tables, key patterns, quick reference]

**For detailed [topic] guidance, see:**
- **[Reference File Name](references/file.md)** - What the file contains
```

**Example Implementation:**

```markdown
## Testing Strategy Framework

[Decision Matrix: Which Testing Approach? - Table with 8 rows]

**For detailed testing guides, see:**
- **[Testing Frameworks Guide](references/testing-frameworks.md)** - In-depth 
  guide to static analysis, native tests, and Terratest
```
[SKILL.md:116-172]()

This pattern appears in sections:
- Testing Strategy [SKILL.md:169-172]()
- Module Development [SKILL.md:348-350]()
- Code Structure Standards [SKILL.md:227]()
- Count vs. For_Each [SKILL.md:271]()
- Locals for Dependencies [SKILL.md:313]()
- CI/CD Integration [SKILL.md:368-370]()
- Security & Compliance [SKILL.md:396-397]()
- Version Management [SKILL.md:431]()
- Modern Terraform Features [SKILL.md:476]()

Sources: [SKILL.md:169-172](), [SKILL.md:227](), [SKILL.md:271](), [SKILL.md:313](), [SKILL.md:348-350](), [SKILL.md:368-370](), [SKILL.md:396-397](), [SKILL.md:431](), [SKILL.md:476](), [SKILL.md:500-511]()

### Token Efficiency Validation

The development process includes explicit token budget tracking:

```bash
# Token estimation (CLAUDE.md:196-199)
wc -c SKILL.md  # Currently ~17,700 chars ≈ 4,400 tokens
```

**Validation Rules:**
- Aim for < 1,500 words in new content additions
- Use tables over prose paragraphs
- Prefer bullet lists to explanatory text
- Remove filler words and adjectives

Sources: [CLAUDE.md:196-199](), [CONTRIBUTING.md reference in CLAUDE.md]()

---

## Benefits and Trade-offs

### Achieved Optimization

**Token Savings:**
- **56-70% reduction** in typical query token usage vs. loading all content
- Baseline load: 4.5K tokens (metadata + core) instead of 30.4K tokens (all content)
- Most queries satisfied with 8-12K tokens (core + 1-2 references)

**User Experience:**
- Faster response times (less content to process)
- More context window available for user's code
- Scalable: can add reference files without impacting core performance

Sources: [CLAUDE.md:78-82]()

### Architectural Trade-offs

**Complexity:**
- Requires careful content categorization (core vs. reference)
- Must maintain explicit links between `SKILL.md` and reference files
- Contributors must understand where new content belongs

**Maintenance:**
- Content duplication risk (same concept in core + reference)
- Link maintenance burden (keeping references accurate)
- Version sync across files (ensure consistent guidance)

**User Impact:**
- Users must trust Claude to load appropriate references
- No guarantee all relevant content loads for every query
- Advanced users may not realize additional detail exists

Sources: [CLAUDE.md:312-328]()

### Design Rationale

The progressive disclosure pattern directly addresses Claude Code's context window constraints:

> "Skills only load when relevant, minimizing token usage."  
> [CLAUDE.md:63]()

> "Architecture optimizes for Claude's context window constraints"  
> [High-Level Diagram 2 Key Insights]

By splitting content into tiers, the skill provides comprehensive Terraform guidance (30.4K tokens) while maintaining practical usability (4.5K-12K token typical load). This enables the skill to cover enterprise-grade patterns, testing frameworks, CI/CD templates, and security compliance without overwhelming Claude's context or forcing users to manage multiple separate skills.

Sources: [CLAUDE.md:46-82](), [SKILL.md:500-511]()

---

# Page: Content Organization

# Content Organization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CLAUDE.md](CLAUDE.md)
- [SKILL.md](SKILL.md)

</details>



**Purpose and Scope**: This page documents the physical file structure of the terraform-skill repository, the responsibilities of each file type, and the ~30.4K token distribution strategy across files. It explains how content is organized to serve both Claude Code (machine-readable skill content) and human contributors (documentation and development guides).

For information about how Claude loads these files at runtime, see [Progressive Disclosure Pattern](#3.2). For the structure of marketplace.json specifically, see [Plugin Definition System](#3.1). For development workflows and contribution process, see [Development Guide](#5).

---

## Repository File Structure

The repository follows a clear separation between integration files, skill content, automation, and contributor documentation:

```
terraform-skill/
├── .claude-plugin/
│   └── marketplace.json              # Plugin metadata (28.17 importance)
├── SKILL.md                          # Core skill content (10.14 importance)
├── references/                       # Progressive disclosure content
│   ├── ci-cd-workflows.md            # ~473 lines, ~2.3K tokens
│   ├── code-patterns.md              # ~859 lines, ~5.1K tokens
│   ├── module-patterns.md            # ~1,126 lines, ~7.0K tokens
│   ├── quick-reference.md            # ~600 lines, ~3.8K tokens
│   ├── security-compliance.md        # ~470 lines, ~2.5K tokens
│   └── testing-frameworks.md         # ~563 lines, ~3.4K tokens
├── .github/
│   ├── workflows/
│   │   ├── automated-release.yml     # Release automation (8.94 importance)
│   │   └── validate.yml              # Content validation (5.50 importance)
│   └── PULL_REQUEST_TEMPLATE.md      # PR standards (0.70 importance)
├── README.md                         # End-user documentation (6.24 importance)
├── CLAUDE.md                         # Contributor guide (2.94 importance)
├── CONTRIBUTING.md                   # Contribution standards (1.50 importance)
├── CHANGELOG.md                      # Release history (21.42 importance)
├── LICENSE                           # Apache 2.0 (2.00 importance)
└── .gitignore                        # Git exclusions (0.70 importance)
```

Sources: [CLAUDE.md:15-32](), [SKILL.md:1-517]()

---

## File Hierarchy by Importance

### Diagram: File Organization by Importance Score

```mermaid
graph TB
    subgraph Critical["Critical Integration Layer (>10.0)"]
        MP[".claude-plugin/marketplace.json<br/>28.17<br/>Entry point for Claude"]
        CHANGELOG["CHANGELOG.md<br/>21.42<br/>Release history"]
        SKILL["SKILL.md<br/>10.14<br/>Core guidance ~524 lines"]
    end
    
    subgraph High["High Importance (5.0-10.0)"]
        RELEASE[".github/workflows/automated-release.yml<br/>8.94<br/>Version automation"]
        README["README.md<br/>6.24<br/>User documentation"]
        VALIDATE[".github/workflows/validate.yml<br/>5.50<br/>Quality gates"]
    end
    
    subgraph Moderate["Moderate Importance (1.0-5.0)"]
        CLAUDE_MD["CLAUDE.md<br/>2.94<br/>Contributor guide"]
        REF_MOD["references/module-patterns.md<br/>2.70<br/>~1,126 lines"]
        REF_QUICK["references/quick-reference.md<br/>2.70<br/>~600 lines"]
        REF_CODE["references/code-patterns.md<br/>2.00<br/>~859 lines"]
        LICENSE["LICENSE<br/>2.00<br/>Apache 2.0"]
        CONTRIB["CONTRIBUTING.md<br/>1.50<br/>Process standards"]
    end
    
    subgraph Supporting["Supporting Files (<1.0)"]
        REF_CI["references/ci-cd-workflows.md<br/>0.70<br/>~473 lines"]
        REF_SEC["references/security-compliance.md<br/>0.70<br/>~470 lines"]
        PR_TEMP[".github/PULL_REQUEST_TEMPLATE.md<br/>0.70<br/>PR checklist"]
        GITIGNORE[".gitignore<br/>0.70<br/>Exclusions"]
    end
    
    MP --> SKILL
    SKILL --> REF_MOD
    SKILL --> REF_QUICK
    SKILL --> REF_CODE
    SKILL --> REF_CI
    SKILL --> REF_SEC
    
    RELEASE --> MP
    RELEASE --> SKILL
    RELEASE --> CHANGELOG
    
    VALIDATE --> MP
    VALIDATE --> SKILL
```

The importance scores indicate how central each file is to the system's operation. Files above 10.0 are critical to the skill's functionality, while files below 1.0 provide supporting infrastructure.

Sources: High-level diagrams (Diagram 1, Diagram 6), [CLAUDE.md:34-43]()

---

## File Type Responsibilities

### Diagram: Responsibility Matrix

```mermaid
graph LR
    subgraph Integration["Claude Code Integration"]
        MP[".claude-plugin/marketplace.json"]
        SKILL["SKILL.md"]
    end
    
    subgraph Knowledge["Knowledge Base"]
        REF_DIR["references/"]
        REF_MOD["module-patterns.md"]
        REF_QUICK["quick-reference.md"]
        REF_CODE["code-patterns.md"]
        REF_CI["ci-cd-workflows.md"]
        REF_SEC["security-compliance.md"]
        REF_TEST["testing-frameworks.md"]
    end
    
    subgraph Automation["Automation & Quality"]
        RELEASE_YML[".github/workflows/automated-release.yml"]
        VALIDATE_YML[".github/workflows/validate.yml"]
        CHANGELOG["CHANGELOG.md"]
    end
    
    subgraph Documentation["Human Documentation"]
        README["README.md"]
        CLAUDE_MD["CLAUDE.md"]
        CONTRIB["CONTRIBUTING.md"]
        PR_TEMP[".github/PULL_REQUEST_TEMPLATE.md"]
    end
    
    subgraph Legal["Legal & Config"]
        LICENSE_FILE["LICENSE"]
        GITIGNORE[".gitignore"]
    end
    
    MP -->|"defines"| SKILL
    SKILL -->|"references"| REF_DIR
    REF_DIR -->|"contains"| REF_MOD
    REF_DIR -->|"contains"| REF_QUICK
    REF_DIR -->|"contains"| REF_CODE
    REF_DIR -->|"contains"| REF_CI
    REF_DIR -->|"contains"| REF_SEC
    REF_DIR -->|"contains"| REF_TEST
    
    RELEASE_YML -->|"updates"| MP
    RELEASE_YML -->|"updates"| SKILL
    RELEASE_YML -->|"generates"| CHANGELOG
    
    VALIDATE_YML -->|"validates"| MP
    VALIDATE_YML -->|"validates"| SKILL
    
    README -->|"documents"| MP
    CLAUDE_MD -->|"guides"| SKILL
    CONTRIB -->|"enforces standards"| SKILL
    PR_TEMP -->|"validates changes"| SKILL
```

Sources: [CLAUDE.md:34-43](), High-level diagrams (Diagram 1, Diagram 6)

### Machine-Readable Files (Claude Code)

| File | Audience | Lines | Tokens | Purpose |
|------|----------|-------|--------|---------|
| `.claude-plugin/marketplace.json` | Claude Code | ~50 | ~100 | Plugin discovery, activation triggers, metadata |
| `SKILL.md` | Claude Code | 524 | ~4,400 | Core Terraform/OpenTofu guidance, decision matrices |
| `references/module-patterns.md` | Claude Code | 1,126 | ~7,000 | Detailed module architecture, variable/output patterns |
| `references/quick-reference.md` | Claude Code | 600 | ~3,800 | Command cheat sheets, troubleshooting guide |
| `references/code-patterns.md` | Claude Code | 859 | ~5,100 | Modern Terraform features, block ordering, refactoring |
| `references/ci-cd-workflows.md` | Claude Code | 473 | ~2,300 | Pipeline templates, cost optimization |
| `references/security-compliance.md` | Claude Code | 470 | ~2,500 | Security scanning, secrets management |
| `references/testing-frameworks.md` | Claude Code | 563 | ~3,400 | Static analysis, native tests, Terratest |

Total machine-readable content: **~4,615 lines**, **~30,400 tokens**

Sources: [CLAUDE.md:66-82](), [SKILL.md:1-517]()

### Human-Readable Files (Contributors)

| File | Audience | Purpose |
|------|----------|---------|
| `README.md` | End users | Installation instructions, usage examples, feature overview |
| `CLAUDE.md` | Contributors | Development philosophy, content standards, architecture decisions |
| `CONTRIBUTING.md` | Contributors | Contribution process, PR requirements, testing methodology |
| `.github/PULL_REQUEST_TEMPLATE.md` | Contributors | PR checklist, evidence requirements |
| `CHANGELOG.md` | All | Version history, feature additions, breaking changes |
| `LICENSE` | All | Apache 2.0 legal terms |

Sources: [CLAUDE.md:34-43](), [README.md:1-50]()

### Automation Files (CI/CD)

| File | Trigger | Actions | Targets |
|------|---------|---------|---------|
| `.github/workflows/validate.yml` | Pull request | Frontmatter validation, file size checks, link detection, markdown linting | `SKILL.md`, `marketplace.json` |
| `.github/workflows/automated-release.yml` | Merge to master | Conventional commit analysis, version bumping, changelog generation, GitHub release | `marketplace.json`, `SKILL.md`, `CHANGELOG.md` |

Sources: [.github/workflows/validate.yml:1-50](), [.github/workflows/automated-release.yml:1-100]()

---

## Token Distribution Strategy

### Diagram: Token Budget Allocation

```mermaid
graph TB
    subgraph Discovery["Discovery Phase (100 tokens)"]
        META["marketplace.json metadata<br/>name, description, keywords"]
    end
    
    subgraph Core["Core Phase (4,400 tokens)"]
        SKILL_MAIN["SKILL.md<br/>Lines 1-517<br/>- Testing Strategy (lines 116-171)<br/>- Code Structure (lines 173-227)<br/>- Module Development (lines 315-350)<br/>- CI/CD Integration (lines 352-370)<br/>- Security (lines 372-397)<br/>- Version Management (lines 399-431)"]
    end
    
    subgraph References["Deep Dive Phase (0-7,000 tokens per file)"]
        REF1["module-patterns.md<br/>7,000 tokens<br/>Lines 1-1,126"]
        REF2["code-patterns.md<br/>5,100 tokens<br/>Lines 1-859"]
        REF3["quick-reference.md<br/>3,800 tokens<br/>Lines 1-600"]
        REF4["testing-frameworks.md<br/>3,400 tokens<br/>Lines 1-563"]
        REF5["security-compliance.md<br/>2,500 tokens<br/>Lines 1-470"]
        REF6["ci-cd-workflows.md<br/>2,300 tokens<br/>Lines 1-473"]
    end
    
    QUERY["User Query"] --> META
    META --> SKILL_MAIN
    SKILL_MAIN -.->|"Module questions"| REF1
    SKILL_MAIN -.->|"Modern features"| REF2
    SKILL_MAIN -.->|"Commands"| REF3
    SKILL_MAIN -.->|"Testing details"| REF4
    SKILL_MAIN -.->|"Security"| REF5
    SKILL_MAIN -.->|"CI/CD"| REF6
    
    TOTAL["Total: ~30,400 tokens available<br/>Typical query: 4,500-12,000 tokens<br/>Savings: 56-70%"]
    
    SKILL_MAIN -.-> TOTAL
```

**Token Efficiency Calculation:**
- **Worst case (load everything):** 100 + 4,400 + 24,000 = 28,500 tokens
- **Typical case (core + 1 reference):** 100 + 4,400 + 3,000 = 7,500 tokens
- **Best case (core only):** 100 + 4,400 = 4,500 tokens
- **Savings:** 4,500-7,500 vs 28,500 = **56-70% reduction**

Sources: [CLAUDE.md:66-82](), High-level diagrams (Diagram 2)

### Content Distribution by Topic

| Topic | Location | Lines | Tokens | Load Frequency |
|-------|----------|-------|--------|----------------|
| Testing Strategy Framework | `SKILL.md:116-171` | 56 | ~450 | Every query |
| Code Structure Standards | `SKILL.md:173-227` | 55 | ~550 | Every query |
| Count vs For_Each | `SKILL.md:229-271` | 43 | ~400 | High |
| Module Development | `SKILL.md:315-350` | 36 | ~350 | High |
| CI/CD Integration | `SKILL.md:352-370` | 19 | ~200 | Medium |
| Security & Compliance | `SKILL.md:372-397` | 26 | ~250 | Medium |
| Module Patterns (detailed) | `references/module-patterns.md` | 1,126 | ~7,000 | On-demand |
| Code Patterns (detailed) | `references/code-patterns.md` | 859 | ~5,100 | On-demand |
| Quick Reference | `references/quick-reference.md` | 600 | ~3,800 | On-demand |
| Testing Frameworks | `references/testing-frameworks.md` | 563 | ~3,400 | On-demand |
| Security Details | `references/security-compliance.md` | 470 | ~2,500 | On-demand |
| CI/CD Templates | `references/ci-cd-workflows.md` | 473 | ~2,300 | On-demand |

Sources: [SKILL.md:116-517](), [CLAUDE.md:66-82]()

---

## Content Flow Architecture

### Diagram: Reference Link Architecture

```mermaid
graph TB
    SKILL_TOP["SKILL.md Lines 1-114<br/>Frontmatter & Activation Triggers"]
    
    SKILL_TEST["SKILL.md Lines 116-171<br/>Testing Strategy Framework"]
    SKILL_STRUCT["SKILL.md Lines 173-313<br/>Code Structure Standards"]
    SKILL_MODULE["SKILL.md Lines 315-350<br/>Module Development"]
    SKILL_CICD["SKILL.md Lines 352-370<br/>CI/CD Integration"]
    SKILL_SEC["SKILL.md Lines 372-397<br/>Security & Compliance"]
    SKILL_VERSION["SKILL.md Lines 399-431<br/>Version Management"]
    SKILL_MODERN["SKILL.md Lines 433-476<br/>Modern Features"]
    SKILL_REFS["SKILL.md Lines 499-510<br/>Reference Links"]
    
    REF_TEST["references/testing-frameworks.md<br/>Deep dive: Static, Native, Terratest"]
    REF_MOD["references/module-patterns.md<br/>Variable/output patterns, ✅/❌ examples"]
    REF_CICD["references/ci-cd-workflows.md<br/>GitHub Actions, GitLab CI templates"]
    REF_SEC["references/security-compliance.md<br/>Trivy/Checkov, secrets management"]
    REF_QUICK["references/quick-reference.md<br/>Commands, troubleshooting, migration"]
    REF_CODE["references/code-patterns.md<br/>Block ordering, modern features detail"]
    
    SKILL_TOP --> SKILL_TEST
    SKILL_TOP --> SKILL_STRUCT
    SKILL_TOP --> SKILL_MODULE
    SKILL_TOP --> SKILL_CICD
    SKILL_TOP --> SKILL_SEC
    SKILL_TOP --> SKILL_VERSION
    SKILL_TOP --> SKILL_MODERN
    SKILL_TOP --> SKILL_REFS
    
    SKILL_TEST -.->|"Line 170: [Testing Frameworks Guide]"| REF_TEST
    SKILL_TEST -.->|"Line 171: [Quick Reference]"| REF_QUICK
    
    SKILL_STRUCT -.->|"Line 227: [Block Ordering & Structure]"| REF_CODE
    SKILL_STRUCT -.->|"Line 271: [Count vs For_Each]"| REF_CODE
    SKILL_STRUCT -.->|"Line 313: [Locals for Dependency]"| REF_CODE
    
    SKILL_MODULE -.->|"Line 349: [Module Patterns Guide]"| REF_MOD
    SKILL_MODULE -.->|"Line 350: [Quick Reference]"| REF_QUICK
    
    SKILL_CICD -.->|"Line 369: [CI/CD Workflows Guide]"| REF_CICD
    SKILL_CICD -.->|"Line 370: [Quick Reference]"| REF_QUICK
    
    SKILL_SEC -.->|"Line 397: [Security & Compliance]"| REF_SEC
    
    SKILL_VERSION -.->|"Line 431: [Version Management]"| REF_CODE
    
    SKILL_MODERN -.->|"Line 476: [Modern Terraform Features]"| REF_CODE
    
    SKILL_REFS --> REF_TEST
    SKILL_REFS --> REF_MOD
    SKILL_REFS --> REF_CICD
    SKILL_REFS --> REF_SEC
    SKILL_REFS --> REF_QUICK
```

Sources: [SKILL.md:1-517](), [SKILL.md:499-510]()

### Cross-Reference Pattern

The skill uses inline cross-references to guide Claude to deeper content:

| Pattern | Example Location | Target |
|---------|-----------------|--------|
| Testing details | [SKILL.md:170-171]() | `references/testing-frameworks.md` |
| Module patterns | [SKILL.md:349-350]() | `references/module-patterns.md` |
| Code patterns | [SKILL.md:227](), [SKILL.md:271](), [SKILL.md:313]() | `references/code-patterns.md` |
| CI/CD templates | [SKILL.md:369-370]() | `references/ci-cd-workflows.md` |
| Security scanning | [SKILL.md:397]() | `references/security-compliance.md` |
| Quick reference | [SKILL.md:171](), [SKILL.md:350](), [SKILL.md:370]() | `references/quick-reference.md` |

All reference links follow the pattern:
```markdown
**For [topic], see:** [Link Text](references/filename.md)
```

Sources: [SKILL.md:169-171](), [SKILL.md:227](), [SKILL.md:271](), [SKILL.md:313](), [SKILL.md:349-350](), [SKILL.md:369-370](), [SKILL.md:397]()

---

## File Organization Conventions

### Naming Standards

| File Type | Pattern | Examples |
|-----------|---------|----------|
| Core skill | `SKILL.md` | Single file, uppercase |
| Reference docs | `kebab-case.md` | `module-patterns.md`, `ci-cd-workflows.md` |
| Contributor docs | `UPPERCASE.md` | `README.md`, `CLAUDE.md`, `CONTRIBUTING.md` |
| Automation | `kebab-case.yml` | `automated-release.yml`, `validate.yml` |
| Generated | `UPPERCASE.md` | `CHANGELOG.md` |

Sources: [CLAUDE.md:15-32]()

### Directory Structure Rules

1. **`.claude-plugin/`** - Contains only `marketplace.json`
   - Single file directory for plugin metadata
   - Sources: [.claude-plugin/marketplace.json:1-50]()

2. **`references/`** - Contains all progressive disclosure content
   - All files must be `.md` format
   - No subdirectories (flat structure)
   - Filenames describe content domain (e.g., `module-patterns`, not `modules`)
   - Sources: [CLAUDE.md:22-28]()

3. **`.github/workflows/`** - Contains automation workflows
   - All files must be `.yml` format
   - Filenames describe action (e.g., `automated-release`, not `release`)
   - Sources: [.github/workflows/]()

4. **Root directory** - Contains integration and documentation
   - Core skill (`SKILL.md`)
   - Human documentation (`README.md`, `CLAUDE.md`, `CONTRIBUTING.md`)
   - Legal (`LICENSE`)
   - Configuration (`.gitignore`)
   - Generated (`CHANGELOG.md`)
   - Sources: [CLAUDE.md:15-32]()

### Line Length Standards

| File | Current Lines | Target | Status |
|------|--------------|--------|--------|
| `SKILL.md` | 524 | ~500 | Acceptable (comprehensive core) |
| `references/module-patterns.md` | 1,126 | No limit | As needed |
| `references/code-patterns.md` | 859 | No limit | As needed |
| `references/quick-reference.md` | 600 | No limit | As needed |
| `references/testing-frameworks.md` | 563 | No limit | As needed |
| `references/ci-cd-workflows.md` | 473 | No limit | As needed |
| `references/security-compliance.md` | 470 | No limit | As needed |

**Rationale for SKILL.md being 524 lines:**
- Comprehensive decision matrices require space
- Essential quick reference tables included
- Version-specific guidance covers multiple Terraform versions
- Progressive disclosure minimizes actual token cost
- Extra 24 lines provide significant value while maintaining scannability

Sources: [CLAUDE.md:76-82](), [CLAUDE.md:319-328]()

---

## Content Location Decision Matrix

| Content Type | Location | Reasoning |
|-------------|----------|-----------|
| Activation triggers | `SKILL.md:14-28` | Must be in core for Claude to load skill |
| Decision matrices | `SKILL.md` | High-value, frequently needed |
| Quick reference tables | `SKILL.md` | Efficient token use for common queries |
| ✅/❌ patterns (core) | `SKILL.md` | Essential for code generation |
| Module architecture | `references/module-patterns.md` | Deep dive, loaded on-demand |
| Pipeline templates | `references/ci-cd-workflows.md` | Detailed, large code blocks |
| Command cheat sheets | `references/quick-reference.md` | Comprehensive, rarely all needed |
| Security tool configs | `references/security-compliance.md` | Specialized, loaded when needed |
| Testing frameworks | `references/testing-frameworks.md` | Detailed comparisons, loaded on-demand |
| Modern features | `references/code-patterns.md` | Version-specific, loaded on-demand |

**Decision Rule**: If content is needed in >50% of queries, it belongs in `SKILL.md`. If it's specialized or detailed, it belongs in `references/`.

Sources: [CLAUDE.md:85-109](), [SKILL.md:499-510]()

---

## Frontmatter Structure

### SKILL.md Frontmatter

```yaml
---
name: terraform-skill
description: [Activation triggers and keywords]
license: Apache-2.0
metadata:
  author: Anton Babenko
  version: 1.5.0
---
```

Location: [SKILL.md:1-8]()

**Fields:**
- `name`: Must match directory name and marketplace.json
- `description`: Defines when Claude should activate the skill
- `license`: Legal terms
- `metadata.version`: Synced with marketplace.json by automated-release.yml

Sources: [SKILL.md:1-8]()

### Reference File Frontmatter

Reference files do not require frontmatter. They are loaded as plain markdown when referenced from `SKILL.md`.

Sources: [references/module-patterns.md:1-10](), [references/code-patterns.md:1-10]()

---

## Total Content Inventory

| Category | Files | Lines | Tokens | Purpose |
|----------|-------|-------|--------|---------|
| **Integration** | 2 | ~574 | ~4,500 | Claude skill loading |
| **Knowledge Base** | 6 | 4,091 | ~24,000 | Progressive disclosure content |
| **Automation** | 2 | ~300 | N/A | Quality and release automation |
| **Documentation** | 4 | ~1,000 | N/A | Human-readable guides |
| **Legal/Config** | 2 | ~50 | N/A | License and git config |
| **Generated** | 1 | Variable | N/A | Release history |
| **Total** | 17 | ~6,015 | ~30,400 | Complete system |

Sources: [CLAUDE.md:66-82](), High-level diagrams (Diagram 2, Diagram 6)

---

# Page: Knowledge Base

# Knowledge Base

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CLAUDE.md](CLAUDE.md)
- [SKILL.md](SKILL.md)

</details>



This document describes the Terraform/OpenTofu knowledge base structure, content organization, and progressive disclosure architecture that enables Claude to provide expert guidance on infrastructure-as-code development. The knowledge base contains approximately 30.4K tokens of technical content distributed across a core skill file and specialized reference documents.

For information about how Claude discovers and loads this skill, see [Plugin Definition System](#3.1). For guidelines on contributing new content, see [Development Guide](#5).

---

## Knowledge Base Architecture

The knowledge base implements a **three-tier progressive disclosure pattern** to optimize token usage while maintaining comprehensive coverage of Terraform/OpenTofu best practices.

### Content Distribution Model

```mermaid
graph TB
    subgraph Discovery["Discovery Layer - ~100 tokens"]
        META["marketplace.json metadata<br/>name, description, keywords<br/>activation triggers"]
    end
    
    subgraph Core["Core Layer - ~4,400 tokens"]
        SKILL["SKILL.md (524 lines)<br/>Testing Strategy Framework<br/>Module Development<br/>Code Structure Standards<br/>Common Patterns<br/>Version Management"]
    end
    
    subgraph References["Reference Layer - On-Demand Loading"]
        direction TB
        MOD["module-patterns.md<br/>~7,000 tokens (1,126 lines)"]
        QUICK["quick-reference.md<br/>~3,800 tokens (600 lines)"]
        CODE["code-patterns.md<br/>~5,100 tokens (859 lines)"]
        CI["ci-cd-workflows.md<br/>~2,300 tokens (473 lines)"]
        SEC["security-compliance.md<br/>~2,500 tokens (470 lines)"]
        TEST["testing-frameworks.md<br/>~3,400 tokens (563 lines)"]
    end
    
    META -->|"Skill activated"| SKILL
    SKILL -.->|"Complex module questions"| MOD
    SKILL -.->|"Command lookup"| QUICK
    SKILL -.->|"Version-specific features"| CODE
    SKILL -.->|"Pipeline setup"| CI
    SKILL -.->|"Security scanning"| SEC
    SKILL -.->|"Detailed testing guide"| TEST
    
    EFFICIENCY["Token Efficiency:<br/>56-70% reduction vs loading all content<br/>Typical query: 4.5K-12K tokens<br/>vs 30.4K total available"]
    
    SKILL -.-> EFFICIENCY
```

**Sources:** [SKILL.md:1-517](), [CLAUDE.md:49-82](), [.claude-plugin/marketplace.json:1-20]()

### Progressive Loading Sequence

The knowledge base loads in stages based on query complexity:

```mermaid
sequenceDiagram
    participant User
    participant Claude
    participant Metadata as "marketplace.json"
    participant Core as "SKILL.md"
    participant Refs as "references/*.md"
    
    User->>Claude: "Create Terraform module with tests"
    Claude->>Metadata: Scan activation triggers (~100 tokens)
    Metadata-->>Claude: Match found: module creation
    Claude->>Core: Load SKILL.md (~4,400 tokens)
    Core-->>Claude: Testing Strategy Framework loaded
    
    Note over Claude: Evaluates if additional detail needed
    
    alt Query requires detailed patterns
        Claude->>Refs: Load module-patterns.md (~7,000 tokens)
        Refs-->>Claude: Detailed module guidance
    else Query is straightforward
        Note over Claude: Use core content only
    end
    
    Claude->>User: Generate response with best practices
```

**Sources:** [SKILL.md:499-510](), [CLAUDE.md:49-64](), [CLAUDE.md:66-82]()

---

## Content Organization

The knowledge base is organized into two primary directories with distinct responsibilities:

### File Structure and Token Distribution

| File Path | Lines | Est. Tokens | Purpose | Loading Strategy |
|-----------|-------|-------------|---------|------------------|
| `SKILL.md` | 524 | ~4,400 | Core patterns, decision frameworks, quick reference | Always loaded on activation |
| `references/module-patterns.md` | 1,126 | ~7,000 | Module architecture, variable/output design | Loaded for module questions |
| `references/code-patterns.md` | 859 | ~5,100 | Block ordering, count vs for_each, modern features | Loaded for version-specific queries |
| `references/quick-reference.md` | 600 | ~3,800 | Command cheat sheets, troubleshooting | Loaded for command lookup |
| `references/testing-frameworks.md` | 563 | ~3,400 | Static analysis, native tests, Terratest | Loaded for testing questions |
| `references/ci-cd-workflows.md` | 473 | ~2,300 | GitHub Actions, GitLab CI, Atlantis | Loaded for pipeline setup |
| `references/security-compliance.md` | 470 | ~2,500 | Trivy, Checkov, secrets management | Loaded for security queries |
| **Total** | **4,615** | **~30,400** | Complete knowledge base | Progressive disclosure |

**Sources:** [CLAUDE.md:16-43](), [CLAUDE.md:66-82](), [SKILL.md:499-510]()

### Directory Structure

```
terraform-skill/
├── SKILL.md                           # Core skill file (always loaded)
└── references/                        # Reference library (on-demand)
    ├── module-patterns.md             # Module development guidance
    ├── code-patterns.md               # Modern Terraform patterns
    ├── quick-reference.md             # Command cheat sheets
    ├── testing-frameworks.md          # Testing methodology
    ├── ci-cd-workflows.md             # Pipeline integration
    └── security-compliance.md         # Security best practices
```

**Sources:** [CLAUDE.md:16-32](), [SKILL.md:503-509]()

---

## Core Content Categories

The knowledge base covers seven primary categories of Terraform/OpenTofu expertise:

### Topic to File Mapping

```mermaid
graph LR
    subgraph Topics["Knowledge Domains"]
        TESTING["Testing Strategy"]
        MODULES["Module Development"]
        STRUCTURE["Code Structure"]
        CICD["CI/CD Integration"]
        SECURITY["Security & Compliance"]
        COMMANDS["Commands & Reference"]
        VERSIONS["Version Management"]
    end
    
    subgraph Files["File Locations"]
        SKILL_FILE["SKILL.md<br/>(Core)"]
        MOD_FILE["module-patterns.md"]
        CODE_FILE["code-patterns.md"]
        QUICK_FILE["quick-reference.md"]
        TEST_FILE["testing-frameworks.md"]
        CI_FILE["ci-cd-workflows.md"]
        SEC_FILE["security-compliance.md"]
    end
    
    TESTING --> SKILL_FILE
    TESTING -.-> TEST_FILE
    
    MODULES --> SKILL_FILE
    MODULES -.-> MOD_FILE
    
    STRUCTURE --> SKILL_FILE
    STRUCTURE -.-> CODE_FILE
    
    CICD --> SKILL_FILE
    CICD -.-> CI_FILE
    
    SECURITY --> SKILL_FILE
    SECURITY -.-> SEC_FILE
    
    COMMANDS -.-> QUICK_FILE
    
    VERSIONS --> SKILL_FILE
    VERSIONS -.-> CODE_FILE
```

**Sources:** [SKILL.md:14-28](), [SKILL.md:116-476](), [SKILL.md:499-510]()

### Content Coverage Matrix

| Category | Core Guidance (SKILL.md) | Extended Reference | Key Topics |
|----------|--------------------------|-------------------|------------|
| **Testing Strategy** | Decision matrix, framework selection | testing-frameworks.md | Static analysis, native tests, Terratest, mock providers |
| **Module Development** | Structure, naming, best practices summary | module-patterns.md | Variable design, output patterns, DO/DON'T examples |
| **Code Structure** | Block ordering, resource naming, file organization | code-patterns.md | count vs for_each, locals, dependency management |
| **CI/CD Integration** | Workflow stages, cost optimization | ci-cd-workflows.md | GitHub Actions, GitLab CI, Atlantis, automated cleanup |
| **Security** | Essential checks, common issues | security-compliance.md | Trivy, Checkov, secrets management, compliance testing |
| **Commands** | Version constraints, update workflow | quick-reference.md | Command cheat sheets, troubleshooting, migration paths |
| **Modern Features** | Feature availability, quick examples | code-patterns.md | try(), optional(), moved blocks, cross-variable validation |

**Sources:** [SKILL.md:116-476](), [SKILL.md:499-510]()

---

## Content Categories in Detail

### Testing Strategy Framework

The knowledge base provides a comprehensive testing decision framework spanning multiple testing approaches:

**Core Content Location:** [SKILL.md:116-171]()

**Key Components:**
- Decision matrix for testing approach selection [SKILL.md:119-128]()
- Testing pyramid for infrastructure [SKILL.md:130-144]()
- Native test best practices for Terraform 1.6+ [SKILL.md:146-171]()
- Version-specific guidance (1.0-1.5, 1.6+, 1.7+) [SKILL.md:478-493]()

**Extended Reference:** `references/testing-frameworks.md` (~563 lines, ~3,400 tokens)

**Sources:** [SKILL.md:116-171](), [SKILL.md:478-493](), [CLAUDE.md:69-75]()

### Module Development Patterns

Module development guidance covers architecture principles, naming conventions, and best practices:

**Core Content Location:** [SKILL.md:315-350]()

**Key Components:**
- Standard module structure [SKILL.md:317-331]()
- Variable best practices (description, type, default, validation) [SKILL.md:335-341]()
- Output design principles [SKILL.md:342-347]()
- Reference to detailed patterns [SKILL.md:348-350]()

**Extended Reference:** `references/module-patterns.md` (~1,126 lines, ~7,000 tokens)

**Sources:** [SKILL.md:315-350](), [CLAUDE.md:71]()

### Code Structure Standards

Code structure guidance ensures consistency and maintainability:

**Core Content Location:** [SKILL.md:173-313]()

**Key Components:**
- Resource block ordering (count/for_each, arguments, tags, depends_on, lifecycle) [SKILL.md:175-202]()
- Variable block ordering (description, type, default, validation, nullable) [SKILL.md:204-225]()
- Count vs for_each decision guide [SKILL.md:229-271]()
- Locals for dependency management [SKILL.md:273-313]()

**Extended Reference:** `references/code-patterns.md` (~859 lines, ~5,100 tokens)

**Sources:** [SKILL.md:173-313](), [CLAUDE.md:70]()

### CI/CD Integration

CI/CD guidance covers pipeline integration, cost optimization, and workflow automation:

**Core Content Location:** [SKILL.md:352-370]()

**Key Components:**
- Recommended workflow stages (validate, test, plan, apply) [SKILL.md:354-359]()
- Cost optimization strategy (mocking, cleanup, resource tagging) [SKILL.md:361-367]()
- Reference to detailed templates [SKILL.md:368-370]()

**Extended Reference:** `references/ci-cd-workflows.md` (~473 lines, ~2,300 tokens)

**Sources:** [SKILL.md:352-370](), [CLAUDE.md:69]()

### Security and Compliance

Security guidance covers scanning tools, secrets management, and compliance frameworks:

**Core Content Location:** [SKILL.md:372-397]()

**Key Components:**
- Essential security checks (trivy, checkov) [SKILL.md:374-380]()
- Common security issues to avoid [SKILL.md:382-394]()
- Reference to detailed security guide [SKILL.md:396-397]()

**Extended Reference:** `references/security-compliance.md` (~470 lines, ~2,500 tokens)

**Sources:** [SKILL.md:372-397](), [CLAUDE.md:74]()

### Quick Reference and Commands

Command reference provides rapid consultation for common operations:

**Core Content Location:** [SKILL.md:399-476]()

**Key Components:**
- Version constraint syntax [SKILL.md:401-407]()
- Version strategy by component [SKILL.md:409-416]()
- Update workflow [SKILL.md:418-429]()
- Modern Terraform features by version [SKILL.md:433-476]()

**Extended Reference:** `references/quick-reference.md` (~600 lines, ~3,800 tokens)

**Sources:** [SKILL.md:399-476](), [CLAUDE.md:71]()

---

## Token Budget and Efficiency

The knowledge base achieves significant token efficiency through progressive disclosure:

### Token Usage Patterns

```mermaid
graph TD
    subgraph Scenarios["Query Scenarios"]
        SIMPLE["Simple Query<br/>'Format this Terraform code'"]
        MODERATE["Moderate Query<br/>'Create a module with tests'"]
        COMPLEX["Complex Query<br/>'Design multi-region architecture'"]
    end
    
    subgraph Loading["Content Loaded"]
        META_LOAD["Metadata: ~100 tokens"]
        CORE_LOAD["SKILL.md: ~4,400 tokens"]
        ONE_REF["1 Reference: ~2,500-7,000 tokens"]
        MULTI_REF["2-3 References: ~10,000-15,000 tokens"]
    end
    
    subgraph Total["Total Token Usage"]
        T_SIMPLE["~4,500 tokens<br/>(15% of total)"]
        T_MODERATE["~8,000-12,000 tokens<br/>(26-39% of total)"]
        T_COMPLEX["~15,000-20,000 tokens<br/>(49-66% of total)"]
    end
    
    SIMPLE --> META_LOAD
    SIMPLE --> CORE_LOAD
    META_LOAD --> T_SIMPLE
    CORE_LOAD --> T_SIMPLE
    
    MODERATE --> META_LOAD
    MODERATE --> CORE_LOAD
    MODERATE --> ONE_REF
    ONE_REF --> T_MODERATE
    
    COMPLEX --> META_LOAD
    COMPLEX --> CORE_LOAD
    COMPLEX --> MULTI_REF
    MULTI_REF --> T_COMPLEX
    
    BASELINE["Baseline (load all): 30,400 tokens"]
```

**Sources:** [CLAUDE.md:66-82](), [SKILL.md:499-510]()

### Efficiency Metrics

| Metric | Value | Calculation |
|--------|-------|-------------|
| **Total Available Content** | 30,400 tokens | Sum of all files |
| **Typical Simple Query** | 4,500 tokens | Metadata + SKILL.md |
| **Typical Moderate Query** | 8,000-12,000 tokens | + 1 reference file |
| **Typical Complex Query** | 15,000-20,000 tokens | + 2-3 reference files |
| **Token Reduction (Simple)** | 85% | vs loading all content |
| **Token Reduction (Moderate)** | 56-70% | vs loading all content |
| **Token Reduction (Complex)** | 34-51% | vs loading all content |

**Sources:** [CLAUDE.md:78-82](), [CLAUDE.md:320-328]()

### Content Distribution Strategy

The 524-line `SKILL.md` core file exceeds the suggested 500-line target but is justified by:

1. **Comprehensive decision matrices** - Testing approach selection, count vs for_each [SKILL.md:119-271]()
2. **Essential quick reference tables** - Version management, modern features [SKILL.md:399-476]()
3. **Version-specific guidance** - Multiple Terraform versions supported [SKILL.md:433-493]()
4. **Progressive disclosure architecture** - Minimizes actual token cost per query [CLAUDE.md:320-328]()

The extra 24 lines provide significant value while maintaining scannability. Future content additions prioritize reference file expansion over core skill growth.

**Sources:** [CLAUDE.md:314-328](), [SKILL.md:1-517]()

---

## Content Discovery and Loading

Claude Code discovers and loads knowledge base content through a multi-stage process:

### Discovery Mechanism

```mermaid
flowchart TD
    USER["User Query:<br/>'Create Terraform module'"]
    
    subgraph Discovery["Discovery Phase"]
        SCAN["Claude scans marketplace.json"]
        KEYWORDS["Match against keywords:<br/>terraform, opentofu, module,<br/>infrastructure-as-code"]
        DESCRIPTION["Match against description:<br/>'working with Terraform or OpenTofu'"]
        ACTIVATE["Activation trigger matched"]
    end
    
    subgraph Loading["Loading Phase"]
        LOAD_SKILL["Load SKILL.md frontmatter"]
        EVAL_TRIGGER["Evaluate 'When to Use This Skill'"]
        LOAD_CORE["Load full SKILL.md content"]
    end
    
    subgraph Reference["Reference Loading (Conditional)"]
        CHECK_NEED["Evaluate query complexity"]
        LOAD_MOD["Load module-patterns.md<br/>(if module design question)"]
        LOAD_TEST["Load testing-frameworks.md<br/>(if testing question)"]
        LOAD_OTHER["Load other references<br/>(if relevant)"]
    end
    
    subgraph Response["Response Generation"]
        APPLY["Apply loaded patterns"]
        GENERATE["Generate response"]
    end
    
    USER --> SCAN
    SCAN --> KEYWORDS
    SCAN --> DESCRIPTION
    KEYWORDS --> ACTIVATE
    DESCRIPTION --> ACTIVATE
    
    ACTIVATE --> LOAD_SKILL
    LOAD_SKILL --> EVAL_TRIGGER
    EVAL_TRIGGER --> LOAD_CORE
    
    LOAD_CORE --> CHECK_NEED
    CHECK_NEED -->|"Module question"| LOAD_MOD
    CHECK_NEED -->|"Testing question"| LOAD_TEST
    CHECK_NEED -->|"Other topics"| LOAD_OTHER
    CHECK_NEED -->|"Core sufficient"| APPLY
    
    LOAD_MOD --> APPLY
    LOAD_TEST --> APPLY
    LOAD_OTHER --> APPLY
    
    APPLY --> GENERATE
    GENERATE --> USER
```

**Sources:** [.claude-plugin/marketplace.json:1-20](), [SKILL.md:1-8](), [SKILL.md:14-28](), [SKILL.md:499-510]()

### Activation Triggers

The skill activates when queries match specific patterns defined in `SKILL.md`:

**Primary Triggers:** [SKILL.md:16-23]()
- Creating new Terraform or OpenTofu configurations or modules
- Setting up testing infrastructure for IaC code
- Deciding between testing approaches
- Structuring multi-environment deployments
- Implementing CI/CD for infrastructure-as-code
- Reviewing or refactoring existing Terraform/OpenTofu projects
- Choosing between module patterns or state management approaches

**Exclusion Triggers:** [SKILL.md:25-28]()
- Basic Terraform/OpenTofu syntax questions (Claude's base knowledge)
- Provider-specific API reference (delegated to documentation)
- Cloud platform questions unrelated to Terraform/OpenTofu

**Sources:** [SKILL.md:14-28](), [.claude-plugin/marketplace.json:3-4]()

### Reference File Loading Logic

Reference files load based on query analysis:

| Query Pattern | Reference File Loaded | Lines Loaded | Typical Use Case |
|---------------|----------------------|--------------|------------------|
| "module", "architecture", "structure" | module-patterns.md | 1,126 | Module design questions |
| "count", "for_each", "version", "modern" | code-patterns.md | 859 | Version-specific patterns |
| "command", "troubleshoot", "cheat sheet" | quick-reference.md | 600 | Command lookup |
| "test", "terratest", "native test", "mock" | testing-frameworks.md | 563 | Testing methodology |
| "ci", "cd", "pipeline", "github actions" | ci-cd-workflows.md | 473 | Pipeline setup |
| "security", "trivy", "checkov", "secrets" | security-compliance.md | 470 | Security scanning |

**Sources:** [SKILL.md:499-510](), [CLAUDE.md:69-76]()

---

## Content Maintenance Strategy

The knowledge base follows a structured approach to content maintenance:

### Content Quality Criteria

**Essential Characteristics:** [CLAUDE.md:85-109]()
- Terraform-specific patterns and idioms (not generic programming advice)
- Decision frameworks (when to use X vs Y)
- Version-specific features clearly marked
- ✅ DO vs ❌ DON'T examples
- Scannable format (tables, headers, visual hierarchy)
- Imperative voice ("Use X", not "You should consider X")

**What Doesn't Belong:** [CLAUDE.md:102-109]()
- Generic programming advice
- Terraform syntax basics (covered in official docs)
- Provider-specific resource details (use MCP tools)
- Obvious practices ("use version control")
- Long prose explanations (use tables instead)

**Sources:** [CLAUDE.md:85-109](), [CONTRIBUTING.md:1-50]()

### Update Triggers

Content updates occur when: [CLAUDE.md:200-211]()
- New Terraform major/minor versions introduce features
- Community consensus emerges on patterns
- Real-world usage reveals gaps or ambiguities
- Anti-patterns discovered that should be warned against

Content does not update for: [CLAUDE.md:208-211]()
- Provider-specific resource changes (use MCP tools)
- Minor version patches without feature changes
- Personal preferences without community consensus

**Sources:** [CLAUDE.md:200-211](), [CONTRIBUTING.md:1-50]()

### Version-Specific Content Organization

The knowledge base maintains guidance for multiple Terraform/OpenTofu versions:

| Version Range | Key Features Documented | Location |
|---------------|------------------------|----------|
| Terraform 1.0-1.5 | Terratest-based testing, core functionality | [SKILL.md:480-483]() |
| Terraform 1.6+ | Native test framework | [SKILL.md:485-488]() |
| Terraform 1.7+ | Mock providers for unit testing | [SKILL.md:490-493]() |
| Terraform 1.8+ | Provider functions | [SKILL.md:445]() |
| Terraform 1.9+ | Cross-variable validation | [SKILL.md:446]() |
| Terraform 1.11+ | Write-only arguments | [SKILL.md:447]() |

**Sources:** [SKILL.md:433-493](), [CLAUDE.md:91]()

---

For detailed information on specific knowledge domains, see:
- [Core Skill Content (SKILL.md)](#4.1) - Testing strategy, module development, patterns
- [Module Development Patterns](#4.2) - Module architecture and best practices
- [Code Patterns & Modern Features](#4.3) - Block ordering, version-specific features
- [Quick Reference & Commands](#4.4) - Command cheat sheets, troubleshooting
- [CI/CD Workflows](#4.5) - Pipeline integration templates
- [Security & Compliance](#4.6) - Security scanning, compliance testing

---

# Page: Core Skill Content (SKILL.md)

# Core Skill Content (SKILL.md)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SKILL.md](SKILL.md)

</details>



This page documents the structure, organization, and content of `SKILL.md`, the primary skill content file that Claude loads when the terraform-skill is activated. This ~4,400 token file serves as the entry point in the progressive disclosure architecture, providing essential Terraform/OpenTofu guidance while linking to detailed reference files when needed.

For information about the reference files that SKILL.md links to, see [Module Development Patterns](#4.2), [Code Patterns & Modern Features](#4.3), [Quick Reference & Commands](#4.4), [CI/CD Workflows](#4.5), and [Security & Compliance](#4.6). For the plugin definition that makes this content discoverable, see [Plugin Definition System](#3.1). For the overall architecture pattern, see [Progressive Disclosure Pattern](#3.2).

---

## File Metadata and Frontmatter

SKILL.md begins with YAML frontmatter that defines the skill's identity and activation conditions for Claude Code.

```mermaid
graph TB
    FM["Frontmatter Block<br/>[SKILL.md:1-8]()"]
    
    NAME["name: terraform-skill<br/>[SKILL.md:2]()"]
    DESC["description: Use when working with...<br/>[SKILL.md:3]()"]
    LICENSE["license: Apache-2.0<br/>[SKILL.md:4]()"]
    
    META["metadata block<br/>[SKILL.md:5-7]()"]
    AUTHOR["author: Anton Babenko"]
    VERSION["version: 1.5.0"]
    
    FM --> NAME
    FM --> DESC
    FM --> LICENSE
    FM --> META
    
    META --> AUTHOR
    META --> VERSION
    
    SYNC["Version Synchronization<br/>with marketplace.json"]
    VERSION -.->|"automated-release.yml syncs"| SYNC
```

**Frontmatter Structure:**

| Field | Purpose | Line Reference |
|-------|---------|---------------|
| `name` | Skill identifier matching marketplace.json | [SKILL.md:2]() |
| `description` | Activation trigger keywords for Claude | [SKILL.md:3]() |
| `license` | Apache-2.0 license identifier | [SKILL.md:4]() |
| `metadata.author` | Skill maintainer | [SKILL.md:6]() |
| `metadata.version` | Semantic version (synced with releases) | [SKILL.md:7]() |

The `description` field contains activation keywords that Claude uses to determine when to load this skill: "Terraform", "OpenTofu", "modules", "tests", "CI/CD", "security scanning", etc.

**Sources:** [SKILL.md:1-8]()

---

## Content Architecture Overview

The file is organized into distinct sections that provide progressively detailed guidance, with explicit links to reference files for deep dives.

```mermaid
graph TB
    subgraph "SKILL.md Structure"
        INTRO["Introduction & Scope<br/>[SKILL.md:10-28]()"]
        CORE["Core Principles<br/>[SKILL.md:30-67]()"]
        TEST["Testing Strategy Framework<br/>[SKILL.md:117-172]()"]
        CODE["Code Structure Standards<br/>[SKILL.md:173-227]()"]
        COUNTFOR["Count vs For_Each<br/>[SKILL.md:229-271]()"]
        LOCALS["Locals for Dependencies<br/>[SKILL.md:273-313]()"]
        MOD["Module Development<br/>[SKILL.md:315-350]()"]
        CI["CI/CD Integration<br/>[SKILL.md:352-370]()"]
        SEC["Security & Compliance<br/>[SKILL.md:372-397]()"]
        VER["Version Management<br/>[SKILL.md:399-431]()"]
        MODERN["Modern Features 1.0+<br/>[SKILL.md:433-476]()"]
        VERSGUIDE["Version-Specific Guidance<br/>[SKILL.md:478-497]()"]
        REFS["Detailed Guides Links<br/>[SKILL.md:499-510]()"]
    end
    
    subgraph "Progressive Disclosure Links"
        REF_TEST["references/testing-frameworks.md"]
        REF_MOD["references/module-patterns.md"]
        REF_CODE["references/code-patterns.md"]
        REF_CI["references/ci-cd-workflows.md"]
        REF_SEC["references/security-compliance.md"]
        REF_QUICK["references/quick-reference.md"]
    end
    
    TEST -.->|"[SKILL.md:170-171]()"| REF_TEST
    TEST -.->|"[SKILL.md:171]()"| REF_QUICK
    CODE -.->|"[SKILL.md:227]()"| REF_CODE
    COUNTFOR -.->|"[SKILL.md:271]()"| REF_CODE
    LOCALS -.->|"[SKILL.md:313]()"| REF_CODE
    MOD -.->|"[SKILL.md:349]()"| REF_MOD
    MOD -.->|"[SKILL.md:350]()"| REF_QUICK
    CI -.->|"[SKILL.md:369-370]()"| REF_CI
    CI -.->|"[SKILL.md:370]()"| REF_QUICK
    SEC -.->|"[SKILL.md:397]()"| REF_SEC
    VER -.->|"[SKILL.md:431]()"| REF_CODE
    MODERN -.->|"[SKILL.md:476]()"| REF_CODE
    VERSGUIDE -.->|"[SKILL.md:497]()"| REF_QUICK
    REFS --> REF_TEST
    REFS --> REF_MOD
    REFS --> REF_CI
    REFS --> REF_SEC
    REFS --> REF_QUICK
```

**Token Distribution Strategy:**

The file maintains ~4,400 tokens in the core content with explicit links to ~24,000 tokens in reference files. This allows Claude to load only the content needed for a specific query.

**Sources:** [SKILL.md:1-516]()

---

## Activation Conditions Section

The "When to Use This Skill" section [SKILL.md:14-28]() defines explicit triggers for skill activation and exclusions to avoid inappropriate activation.

**Activation Triggers** [SKILL.md:16-23]():

```
- Creating new Terraform or OpenTofu configurations or modules
- Setting up testing infrastructure for IaC code
- Deciding between testing approaches (validate, plan, frameworks)
- Structuring multi-environment deployments
- Implementing CI/CD for infrastructure-as-code
- Reviewing or refactoring existing Terraform/OpenTofu projects
- Choosing between module patterns or state management approaches
```

**Exclusion Conditions** [SKILL.md:25-28]():

```
- Basic Terraform/OpenTofu syntax questions (Claude knows this)
- Provider-specific API reference (link to docs instead)
- Cloud platform questions unrelated to Terraform/OpenTofu
```

This dual approach ensures the skill activates for architectural and testing decisions while avoiding activation for basic syntax queries that Claude's base knowledge can handle.

**Sources:** [SKILL.md:14-28]()

---

## Core Principles Section

The Core Principles section [SKILL.md:30-67]() establishes the foundational architecture patterns, primarily focusing on module hierarchy and directory structure.

### Module Hierarchy Table

```mermaid
graph LR
    RES["Resource<br/>Single logical group"]
    RESMOD["Resource Module<br/>Connected resources"]
    INFRA["Infrastructure Module<br/>Collection of modules"]
    COMP["Composition<br/>Complete infrastructure"]
    
    RES -->|"grouped into"| RESMOD
    RESMOD -->|"combined into"| INFRA
    INFRA -->|"orchestrated by"| COMP
    
    EX1["VPC + subnets"]
    EX2["Multiple modules<br/>in region/account"]
    EX3["Multi-region<br/>deployment"]
    
    RESMOD -.->|"example"| EX1
    INFRA -.->|"example"| EX2
    COMP -.->|"example"| EX3
```

The module hierarchy table [SKILL.md:36-42]() defines four levels:

| Type | When to Use | Scope |
|------|-------------|-------|
| Resource Module | Single logical group of connected resources | VPC + subnets, Security group + rules |
| Infrastructure Module | Collection of resource modules for a purpose | Multiple resource modules in one region/account |
| Composition | Complete infrastructure | Spans multiple regions/accounts |

### Standard Directory Structure

The recommended directory structure [SKILL.md:44-59]() follows the terraform-best-practices.com pattern:

```
environments/        # Environment-specific configurations
├── prod/
├── staging/
└── dev/

modules/            # Reusable modules
├── networking/
├── compute/
└── data/

examples/           # Module usage examples (also serve as tests)
├── complete/
└── minimal/
```

**Key principle** [SKILL.md:61-65](): Separation of environments from modules, with `examples/` serving dual purpose as documentation and test fixtures.

**Sources:** [SKILL.md:30-67]()

---

## Testing Strategy Framework

The Testing Strategy Framework [SKILL.md:117-172]() provides a decision matrix and testing pyramid for choosing appropriate testing approaches.

### Testing Decision Matrix

```mermaid
graph TD
    QUERY["User needs to test<br/>Terraform code"]
    
    SYNTAX["Quick syntax check?"]
    PRECOMMIT["Pre-commit validation?"]
    VERSION["Terraform 1.6+?"]
    SECURITY["Security focus?"]
    COST["Cost sensitive?"]
    COMPLEX["Multi-cloud/complex?"]
    
    QUERY --> SYNTAX
    SYNTAX -->|Yes| STATIC["Static analysis<br/>validate, fmt<br/>Cost: Free"]
    SYNTAX -->|No| PRECOMMIT
    
    PRECOMMIT -->|Yes| LINT["Static + lint<br/>tflint, trivy, checkov<br/>Cost: Free"]
    PRECOMMIT -->|No| VERSION
    
    VERSION -->|Yes| NATIVE["Native test framework<br/>terraform test<br/>Cost: Free-Low"]
    VERSION -->|No| TERRATEST["Terratest<br/>Go integration tests<br/>Cost: Low-Med"]
    
    SECURITY -->|Yes| POLICY["Policy as code<br/>OPA, Sentinel<br/>Cost: Free"]
    
    COST -->|Yes| MOCK["Mock providers 1.7+<br/>Native tests + mocking<br/>Cost: Free"]
    
    COMPLEX -->|Yes| INTEGRATION["Full integration<br/>Terratest + real infra<br/>Cost: Med-High"]
```

The decision matrix [SKILL.md:120-128]() maps user situations to recommended tools:

| Your Situation | Recommended Approach | Tools | Cost |
|----------------|---------------------|-------|------|
| Quick syntax check | Static analysis | `terraform validate`, `fmt` | Free |
| Pre-commit validation | Static + lint | `validate`, `tflint`, `trivy`, `checkov` | Free |
| Terraform 1.6+, simple logic | Native test framework | Built-in `terraform test` | Free-Low |
| Pre-1.6, or Go expertise | Integration testing | Terratest | Low-Med |
| Security/compliance focus | Policy as code | OPA, Sentinel | Free |
| Cost-sensitive workflow | Mock providers (1.7+) | Native tests + mocking | Free |
| Multi-cloud, complex | Full integration | Terratest + real infra | Med-High |

### Testing Pyramid

The testing pyramid [SKILL.md:130-144]() establishes cost/coverage tradeoffs:

```
        /\
       /  \          End-to-End Tests (Expensive)
      /____\         - Full environment deployment
     /      \        - Production-like setup
    /________\
   /          \      Integration Tests (Moderate)
  /____________\     - Module testing in isolation
 /              \    - Real resources in test account
/________________\   Static Analysis (Cheap)
                     - validate, fmt, lint
                     - Security scanning
```

### Native Test Best Practices

The Native Test Best Practices section [SKILL.md:146-168]() addresses schema validation and set-type block handling:

**Pre-test validation steps** [SKILL.md:150-162]():
1. Validate schemas with Terraform MCP
2. Choose correct command mode (`plan` vs `apply`)
3. Handle set-type blocks correctly (cannot index with `[0]`)

**Common set-type patterns** [SKILL.md:164-167]():
- S3 encryption rules: **set** (use for expressions)
- Lifecycle transitions: **set** (use for expressions)
- IAM policy statements: **set** (use for expressions)

**Progressive disclosure links** [SKILL.md:169-171]():
- `references/testing-frameworks.md` for deep dive
- `references/quick-reference.md` for decision flowchart

**Sources:** [SKILL.md:117-172]()

---

## Code Structure Standards

The Code Structure Standards section [SKILL.md:173-227]() defines strict ordering rules for resource and variable blocks.

### Resource Block Ordering

```mermaid
graph TB
    START["Resource Block Start"]
    
    ORDER1["1. count or for_each FIRST<br/>[SKILL.md:178]()"]
    BLANK1["blank line after"]
    ORDER2["2. Other arguments<br/>[SKILL.md:179]()"]
    ORDER3["3. tags as last real argument<br/>[SKILL.md:180]()"]
    ORDER4["4. depends_on after tags<br/>[SKILL.md:181]()"]
    ORDER5["5. lifecycle at very end<br/>[SKILL.md:182]()"]
    
    START --> ORDER1
    ORDER1 --> BLANK1
    BLANK1 --> ORDER2
    ORDER2 --> ORDER3
    ORDER3 --> ORDER4
    ORDER4 --> ORDER5
    
    EXAMPLE["Example: aws_nat_gateway<br/>[SKILL.md:185-201]()"]
    ORDER5 -.-> EXAMPLE
```

**Strict ordering** [SKILL.md:178-182]():
1. `count` or `for_each` FIRST (blank line after)
2. Other arguments
3. `tags` as last real argument
4. `depends_on` after tags (if needed)
5. `lifecycle` at the very end (if needed)

**Example implementation** [SKILL.md:185-201]():

```hcl
resource "aws_nat_gateway" "this" {
  count = var.create_nat_gateway ? 1 : 0

  allocation_id = aws_eip.this[0].id
  subnet_id     = aws_subnet.public[0].id

  tags = {
    Name = "${var.name}-nat"
  }

  depends_on = [aws_internet_gateway.this]

  lifecycle {
    create_before_destroy = true
  }
}
```

### Variable Block Ordering

**Ordering specification** [SKILL.md:206-210]():
1. `description` (ALWAYS required)
2. `type`
3. `default`
4. `validation`
5. `nullable` (when setting to false)

**Example implementation** [SKILL.md:213-224]():

```hcl
variable "environment" {
  description = "Environment name for resource tagging"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }

  nullable = false
}
```

**Sources:** [SKILL.md:173-227]()

---

## Naming Conventions

The Naming Conventions section [SKILL.md:68-115]() establishes patterns for resources, variables, and files.

### Resource Naming Pattern

```mermaid
graph LR
    DECISION{"Is this a<br/>singleton resource?"}
    
    YES["Use 'this'<br/>[SKILL.md:87-93]()"]
    NO["Use descriptive name<br/>[SKILL.md:72-82]()"]
    
    DECISION -->|"Only one of this type"| YES
    DECISION -->|"Multiple of this type"| NO
    
    GOOD_SINGLE["aws_vpc 'this'<br/>aws_security_group 'this'"]
    BAD_SINGLE["aws_subnet 'this'<br/>when creating multiple"]
    
    GOOD_MULTI["aws_instance 'web_server'<br/>aws_s3_bucket 'application_logs'"]
    
    YES -.->|"example"| GOOD_SINGLE
    YES -.->|"avoid"| BAD_SINGLE
    NO -.->|"example"| GOOD_MULTI
```

**Singleton rule** [SKILL.md:86-100](): Use `"this"` when module creates only one resource of that type:

✅ DO:
```hcl
resource "aws_vpc" "this" {}           # Module creates one VPC
resource "aws_security_group" "this" {}  # Module creates one SG
```

❌ DON'T:
```hcl
resource "aws_subnet" "this" {}  # If creating multiple subnets
```

**Descriptive naming** [SKILL.md:72-82]() for non-singletons:

✅ Good:
```hcl
resource "aws_instance" "web_server" { }
resource "aws_s3_bucket" "application_logs" { }
```

❌ Avoid:
```hcl
resource "aws_instance" "main" { }
resource "aws_s3_bucket" "bucket" { }
```

### Variable and File Naming

**Variable naming** [SKILL.md:103-107]():
```hcl
var.vpc_cidr_block          # Not just "cidr"
var.database_instance_class # Not just "instance_class"
```

**File organization** [SKILL.md:109-114]():
- `main.tf` - Primary resources
- `variables.tf` - Input variables
- `outputs.tf` - Output values
- `versions.tf` - Provider versions
- `data.tf` - Data sources (optional)

**Sources:** [SKILL.md:68-115]()

---

## Count vs For_Each Guidance

The Count vs For_Each section [SKILL.md:229-271]() provides a decision guide and migration patterns.

### Decision Guide

```mermaid
graph TD
    SCENARIO["What are you creating?"]
    
    BOOL["Boolean on/off?"]
    NUMERIC["Fixed number?"]
    REORDER["Items may reorder?"]
    KEY["Reference by key?"]
    MULTIPLE["Multiple named?"]
    
    SCENARIO --> BOOL
    SCENARIO --> NUMERIC
    SCENARIO --> REORDER
    SCENARIO --> KEY
    SCENARIO --> MULTIPLE
    
    BOOL -->|Yes| COUNT1["count = condition ? 1 : 0<br/>[SKILL.md:235]()"]
    NUMERIC -->|Yes| COUNT2["count = 3<br/>[SKILL.md:236]()"]
    REORDER -->|Yes| FOREACH1["for_each = toset list<br/>[SKILL.md:237]()"]
    KEY -->|Yes| FOREACH2["for_each = map<br/>[SKILL.md:238]()"]
    MULTIPLE -->|Yes| FOREACH3["for_each preferred<br/>[SKILL.md:239]()"]
    
    REASON1["Simple toggle"]
    REASON2["Fixed identical resources"]
    REASON3["Stable addresses"]
    REASON4["Named access"]
    REASON5["Better maintainability"]
    
    COUNT1 -.-> REASON1
    COUNT2 -.-> REASON2
    FOREACH1 -.-> REASON3
    FOREACH2 -.-> REASON4
    FOREACH3 -.-> REASON5
```

**Decision table** [SKILL.md:233-239]():

| Scenario | Use | Why |
|----------|-----|-----|
| Boolean condition (create or don't) | `count = condition ? 1 : 0` | Simple on/off toggle |
| Simple numeric replication | `count = 3` | Fixed number of identical resources |
| Items may be reordered/removed | `for_each = toset(list)` | Stable resource addresses |
| Reference by key | `for_each = map` | Named access to resources |
| Multiple named resources | `for_each` | Better maintainability |

### Stable Addressing Example

**Good: for_each with stable addresses** [SKILL.md:253-260]():
```hcl
resource "aws_subnet" "private" {
  for_each = toset(var.availability_zones)

  availability_zone = each.key
  # ...
}
# Removing "us-east-1b" only affects that subnet
```

**Bad: count with index-based addressing** [SKILL.md:262-268]():
```hcl
resource "aws_subnet" "private" {
  count = length(var.availability_zones)

  availability_zone = var.availability_zones[count.index]
  # ...
}
# Removing middle AZ recreates all subsequent subnets
```

**Sources:** [SKILL.md:229-271]()

---

## Locals for Dependency Management

The Locals for Dependency Management section [SKILL.md:273-313]() demonstrates using `try()` in locals to control resource deletion order.

```mermaid
graph TD
    PROBLEM["Problem: Deletion order errors<br/>Subnets deleted after CIDR blocks"]
    
    SOLUTION["Solution: try in locals<br/>[SKILL.md:277-289]()"]
    
    LOCAL["local.vpc_id = try<br/>CIDR.vpc_id,<br/>VPC.id,<br/>empty"]
    
    DELETE_ORDER["Deletion Order<br/>1. Subnets reference local<br/>2. Local references CIDR first<br/>3. CIDR deleted before VPC"]
    
    PROBLEM --> SOLUTION
    SOLUTION --> LOCAL
    LOCAL --> DELETE_ORDER
    
    VPC["aws_vpc.this<br/>[SKILL.md:291-293]()"]
    CIDR["aws_vpc_ipv4_cidr_block_association.this<br/>[SKILL.md:295-300]()"]
    SUBNET["aws_subnet.public<br/>[SKILL.md:302-305]()"]
    
    DELETE_ORDER -.-> SUBNET
    SUBNET -->|"uses"| LOCAL
    LOCAL -->|"references first"| CIDR
    LOCAL -->|"fallback to"| VPC
```

**Implementation pattern** [SKILL.md:281-305]():

```hcl
locals {
  # References secondary CIDR first, falling back to VPC
  # Forces Terraform to delete subnets before CIDR association
  vpc_id = try(
    aws_vpc_ipv4_cidr_block_association.this[0].vpc_id,
    aws_vpc.this.id,
    ""
  )
}

resource "aws_vpc" "this" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_vpc_ipv4_cidr_block_association" "this" {
  count = var.add_secondary_cidr ? 1 : 0

  vpc_id     = aws_vpc.this.id
  cidr_block = "10.1.0.0/16"
}

resource "aws_subnet" "public" {
  vpc_id     = local.vpc_id  # Uses local, not direct reference
  cidr_block = "10.1.0.0/24"
}
```

**Why this matters** [SKILL.md:308-311]():
- Prevents deletion errors when destroying infrastructure
- Ensures correct dependency order without explicit `depends_on`
- Particularly useful for VPC configurations with secondary CIDR blocks

**Sources:** [SKILL.md:273-313]()

---

## Module Development Section

The Module Development section [SKILL.md:315-350]() defines standard module structure and best practices.

### Standard Module Structure

**Directory layout** [SKILL.md:319-330]():

```
my-module/
├── README.md           # Usage documentation
├── main.tf             # Primary resources
├── variables.tf        # Input variables with descriptions
├── outputs.tf          # Output values
├── versions.tf         # Provider version constraints
├── examples/
│   ├── minimal/        # Minimal working example
│   └── complete/       # Full-featured example
└── tests/              # Test files
    └── module_test.tftest.hcl  # Or .go
```

### Best Practices Checklist

**Variables best practices** [SKILL.md:335-340]():
- ✅ Always include `description`
- ✅ Use explicit `type` constraints
- ✅ Provide sensible `default` values where appropriate
- ✅ Add `validation` blocks for complex constraints
- ✅ Use `sensitive = true` for secrets

**Outputs best practices** [SKILL.md:342-346]():
- ✅ Always include `description`
- ✅ Mark sensitive outputs with `sensitive = true`
- ✅ Consider returning objects for related values
- ✅ Document what consumers should do with each output

**Progressive disclosure links** [SKILL.md:348-350]():
- `references/module-patterns.md` for detailed patterns
- `references/quick-reference.md` for common patterns

**Sources:** [SKILL.md:315-350]()

---

## CI/CD Integration Section

The CI/CD Integration section [SKILL.md:352-370]() defines workflow stages and cost optimization strategies.

### Workflow Stages

```mermaid
graph LR
    VALIDATE["1. Validate<br/>fmt + validate + lint<br/>[SKILL.md:356]()"]
    TEST["2. Test<br/>native or Terratest<br/>[SKILL.md:357]()"]
    PLAN["3. Plan<br/>execution plan<br/>[SKILL.md:358]()"]
    APPLY["4. Apply<br/>with approvals<br/>[SKILL.md:359]()"]
    
    VALIDATE --> TEST
    TEST --> PLAN
    PLAN --> APPLY
    
    APPROVAL["Production<br/>approval gate"]
    PLAN -.->|"for prod"| APPROVAL
    APPROVAL -.-> APPLY
```

**Recommended stages** [SKILL.md:356-359]():
1. **Validate** - Format check + syntax validation + linting
2. **Test** - Run automated tests (native or Terratest)
3. **Plan** - Generate and review execution plan
4. **Apply** - Execute changes (with approvals for production)

### Cost Optimization Strategy

**Optimization steps** [SKILL.md:362-366]():

1. **Use mocking for PR validation** (free)
2. **Run integration tests only on main branch** (controlled cost)
3. **Implement auto-cleanup** (prevent orphaned resources)
4. **Tag all test resources** (track spending)

**Progressive disclosure links** [SKILL.md:368-370]():
- `references/ci-cd-workflows.md` for complete templates
- `references/quick-reference.md` for troubleshooting

**Sources:** [SKILL.md:352-370]()

---

## Security & Compliance Section

The Security & Compliance section [SKILL.md:372-397]() provides essential security checks and avoidance patterns.

### Essential Security Checks

**Static scanning commands** [SKILL.md:376-379]():

```bash
# Static security scanning
trivy config .
checkov -d .
```

### Security Patterns

```mermaid
graph TB
    subgraph "❌ DON'T"
        DONT1["Store secrets in variables"]
        DONT2["Use default VPC"]
        DONT3["Skip encryption"]
        DONT4["Open SG to 0.0.0.0/0"]
    end
    
    subgraph "✅ DO"
        DO1["Use Secrets Manager/<br/>Parameter Store"]
        DO2["Create dedicated VPCs"]
        DO3["Enable encryption at rest"]
        DO4["Least-privilege SGs"]
    end
    
    DONT1 -.->|"instead"| DO1
    DONT2 -.->|"instead"| DO2
    DONT3 -.->|"instead"| DO3
    DONT4 -.->|"instead"| DO4
```

**Anti-patterns** [SKILL.md:384-388]():
- ❌ Store secrets in variables
- ❌ Use default VPC
- ❌ Skip encryption
- ❌ Open security groups to 0.0.0.0/0

**Recommended practices** [SKILL.md:390-394]():
- ✅ Use AWS Secrets Manager / Parameter Store
- ✅ Create dedicated VPCs
- ✅ Enable encryption at rest
- ✅ Use least-privilege security groups

**Progressive disclosure link** [SKILL.md:396-397]():
- `references/security-compliance.md` for detailed guidance

**Sources:** [SKILL.md:372-397]()

---

## Version Management Section

The Version Management section [SKILL.md:399-431]() defines version constraint syntax and update workflows.

### Version Constraint Syntax

**Constraint patterns** [SKILL.md:403-407]():

```hcl
version = "5.0.0"      # Exact (avoid - inflexible)
version = "~> 5.0"     # Recommended: 5.0.x only
version = ">= 5.0"     # Minimum (risky - breaking changes)
```

### Strategy by Component

**Component-specific strategies** [SKILL.md:411-416]():

| Component | Strategy | Example |
|-----------|----------|---------|
| **Terraform** | Pin minor version | `required_version = "~> 1.9"` |
| **Providers** | Pin major version | `version = "~> 5.0"` |
| **Modules (prod)** | Pin exact version | `version = "5.1.2"` |
| **Modules (dev)** | Allow patch updates | `version = "~> 5.1"` |

### Update Workflow

**Update process** [SKILL.md:420-428]():

```bash
# Lock versions initially
terraform init              # Creates .terraform.lock.hcl

# Update to latest within constraints
terraform init -upgrade     # Updates providers

# Review and test
terraform plan
```

**Sources:** [SKILL.md:399-431]()

---

## Modern Terraform Features Section

The Modern Terraform Features section [SKILL.md:433-476]() documents version-specific capabilities and migration patterns.

### Feature Availability Timeline

```mermaid
graph TB
    V013["Terraform 0.13+"]
    V11["Terraform 1.1+"]
    V13["Terraform 1.3+"]
    V16["Terraform 1.6+"]
    V17["Terraform 1.7+"]
    V18["Terraform 1.8+"]
    V19["Terraform 1.9+"]
    V111["Terraform 1.11+"]
    
    V013 -->|"try function"| TRY["try<br/>Safe fallbacks<br/>[SKILL.md:439]()"]
    
    V11 -->|"nullable = false"| NULL["Prevent null values<br/>[SKILL.md:440]()"]
    V11 -->|"moved blocks"| MOVED["Refactor without<br/>destroy/recreate<br/>[SKILL.md:441]()"]
    
    V13 -->|"optional with defaults"| OPT["Optional object<br/>attributes<br/>[SKILL.md:442]()"]
    
    V16 -->|"terraform test"| TEST["Native testing<br/>[SKILL.md:443]()"]
    
    V17 -->|"mock providers"| MOCK["Cost-free unit<br/>testing<br/>[SKILL.md:444]()"]
    
    V18 -->|"provider functions"| PFUNC["Provider-specific<br/>transformation<br/>[SKILL.md:445]()"]
    
    V19 -->|"cross-variable validation"| CROSSVAL["Validate relationships<br/>[SKILL.md:446]()"]
    
    V111 -->|"write-only arguments"| WRITEONLY["Secrets never in<br/>state<br/>[SKILL.md:447]()"]
```

**Feature table** [SKILL.md:437-447]():

| Feature | Version | Use Case |
|---------|---------|----------|
| `try()` function | 0.13+ | Safe fallbacks, replaces `element(concat())` |
| `nullable = false` | 1.1+ | Prevent null values in variables |
| `moved` blocks | 1.1+ | Refactor without destroy/recreate |
| `optional()` with defaults | 1.3+ | Optional object attributes |
| Native testing | 1.6+ | Built-in test framework |
| Mock providers | 1.7+ | Cost-free unit testing |
| Provider functions | 1.8+ | Provider-specific data transformation |
| Cross-variable validation | 1.9+ | Validate relationships between variables |
| Write-only arguments | 1.11+ | Secrets never stored in state |

### Quick Examples

**try() example** [SKILL.md:452-455]():
```hcl
output "sg_id" {
  value = try(aws_security_group.this[0].id, "")
}
```

**optional() example** [SKILL.md:457-463]():
```hcl
variable "config" {
  type = object({
    name    = string
    timeout = optional(number, 300)  # Default: 300
  })
}
```

**Cross-variable validation** [SKILL.md:465-473]():
```hcl
variable "environment" { type = string }
variable "backup_days" {
  type = number
  validation {
    condition     = var.environment == "prod" ? var.backup_days >= 7 : true
    error_message = "Production requires backup_days >= 7"
  }
}
```

**Sources:** [SKILL.md:433-476]()

---

## Version-Specific Guidance Section

The Version-Specific Guidance section [SKILL.md:478-497]() provides recommendations by Terraform/OpenTofu version.

### Version-Based Recommendations

```mermaid
graph TD
    VERSION{"Terraform/<br/>OpenTofu Version?"}
    
    V10_15["1.0-1.5"]
    V16["1.6+"]
    V17["1.7+"]
    
    VERSION --> V10_15
    VERSION --> V16
    VERSION --> V17
    
    T1["Use Terratest<br/>[SKILL.md:481]()"]
    T2["No native testing<br/>[SKILL.md:482]()"]
    T3["Static analysis focus<br/>[SKILL.md:483]()"]
    
    V10_15 --> T1
    V10_15 --> T2
    V10_15 --> T3
    
    N1["Native terraform test<br/>[SKILL.md:487]()"]
    N2["Migrate from frameworks<br/>[SKILL.md:488]()"]
    N3["Keep Terratest for complex<br/>[SKILL.md:489]()"]
    
    V16 --> N1
    V16 --> N2
    V16 --> N3
    
    M1["Mock providers<br/>[SKILL.md:492]()"]
    M2["Reduce cost<br/>[SKILL.md:493]()"]
    M3["Real tests for validation<br/>[SKILL.md:494]()"]
    
    V17 --> M1
    V17 --> M2
    V17 --> M3
```

**Terraform 1.0-1.5** [SKILL.md:480-483]():
- Use Terratest for testing
- No native testing framework available
- Focus on static analysis and plan validation

**Terraform 1.6+ / OpenTofu 1.6+** [SKILL.md:485-489]():
- **New:** Native `terraform test` / `tofu test` command
- Consider migrating from external frameworks for simple tests
- Keep Terratest only for complex integration tests

**Terraform 1.7+ / OpenTofu 1.7+** [SKILL.md:491-494]():
- **New:** Mock providers for unit testing
- Reduce cost by mocking external dependencies
- Use real integration tests for final validation

### Terraform vs OpenTofu

**Comparison reference** [SKILL.md:496-497](): Both are fully supported. For licensing, governance, and feature comparison, see `references/quick-reference.md`.

**Sources:** [SKILL.md:478-497]()

---

## Progressive Disclosure Links Section

The Detailed Guides section [SKILL.md:499-510]() lists all reference files and their purposes.

```mermaid
graph TB
    SKILL["SKILL.md<br/>~4,400 tokens"]
    
    subgraph "Reference Files - ~24,000 tokens total"
        TEST_REF["references/testing-frameworks.md<br/>Static analysis, native tests, Terratest<br/>[SKILL.md:504]()"]
        MOD_REF["references/module-patterns.md<br/>Structure, variables, outputs, patterns<br/>[SKILL.md:505]()"]
        CI_REF["references/ci-cd-workflows.md<br/>GitHub Actions, GitLab CI, cost optimization<br/>[SKILL.md:506]()"]
        SEC_REF["references/security-compliance.md<br/>Trivy/Checkov, secrets, compliance<br/>[SKILL.md:507]()"]
        QUICK_REF["references/quick-reference.md<br/>Commands, flowcharts, troubleshooting<br/>[SKILL.md:508]()"]
    end
    
    LOAD["Claude loads on demand<br/>[SKILL.md:510]()"]
    
    SKILL -.->|"when needed"| TEST_REF
    SKILL -.->|"when needed"| MOD_REF
    SKILL -.->|"when needed"| CI_REF
    SKILL -.->|"when needed"| SEC_REF
    SKILL -.->|"when needed"| QUICK_REF
    
    TEST_REF --> LOAD
    MOD_REF --> LOAD
    CI_REF --> LOAD
    SEC_REF --> LOAD
    QUICK_REF --> LOAD
```

**Reference files inventory** [SKILL.md:503-508]():

| File | Purpose |
|------|---------|
| `references/testing-frameworks.md` | In-depth guide to static analysis, native tests, and Terratest |
| `references/module-patterns.md` | Module structure, variable/output best practices, ✅ DO vs ❌ DON'T patterns |
| `references/ci-cd-workflows.md` | GitHub Actions, GitLab CI templates, cost optimization, automated cleanup |
| `references/security-compliance.md` | Trivy/Checkov integration, secrets management, compliance testing |
| `references/quick-reference.md` | Command cheat sheets, decision flowcharts, troubleshooting guide |

**Loading strategy** [SKILL.md:510](): "When you need detailed information on a topic, reference the appropriate guide. Claude will load it on demand to provide comprehensive guidance."

**Sources:** [SKILL.md:499-510]()

---

## License Section

The License section [SKILL.md:512-516]() documents the Apache 2.0 license and copyright.

**License declaration** [SKILL.md:513]():
```
This skill is licensed under the **Apache License 2.0**. See the LICENSE file for full terms.
```

**Copyright notice** [SKILL.md:515]():
```
**Copyright © 2026 Anton Babenko**
```

**Sources:** [SKILL.md:512-516]()

---

## File Size and Token Management

SKILL.md maintains strict size constraints to optimize Claude's context window usage.

**Current metrics**:
- File size: ~4,400 tokens
- Line count: 516 lines
- Validation warning threshold: 500 lines [validate.yml references this file]

**Progressive disclosure benefits**:
- Total available content: ~30,400 tokens (SKILL.md + all references)
- Typical query usage: 4,500-12,000 tokens (56-70% token reduction)
- Loading strategy: Metadata (100 tokens) → Core (4,400 tokens) → References (0-7,000 tokens per file)

This architecture allows the skill to provide comprehensive guidance while respecting Claude's context limitations.

**Sources:** [SKILL.md:1-516](), See [Progressive Disclosure Pattern](#3.2) for architectural details.

---

# Page: Module Development Patterns

# Module Development Patterns

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [references/module-patterns.md](references/module-patterns.md)

</details>



This page documents best practices for creating reusable, maintainable Terraform/OpenTofu modules. It covers the three-tier module hierarchy (resource modules, infrastructure modules, and compositions), architecture principles for scalability and isolation, and comprehensive guidance on variable design, output patterns, and testing philosophy.

For high-level Terraform/OpenTofu guidance principles, see [Core Skill Content](#4.1). For modern Terraform 1.0+ features and refactoring patterns, see [Code Patterns & Modern Features](#4.3). For testing framework selection and implementation details, see [Quick Reference & Commands](#4.4).

---

## Module Type Classification

Terraform modules are organized into three distinct hierarchical types, each serving a specific architectural purpose and scope.

### Module Hierarchy Overview

```mermaid
graph TD
    Resource["Resource Module<br/>aws_vpc + subnets + routes"]
    Infrastructure["Infrastructure Module<br/>VPC + ALB + ECS"]
    Composition["Composition<br/>Complete Environment"]
    
    Resource -->|"Combined into"| Infrastructure
    Infrastructure -->|"Orchestrated in"| Composition
    
    Resource_Char["Characteristics:<br/>- Single logical group<br/>- Highly reusable<br/>- Minimal dependencies<br/>- Clear focused purpose"]
    Infrastructure_Char["Characteristics:<br/>- Multiple resource modules<br/>- Purpose-specific<br/>- Region/account scope<br/>- Moderate reusability"]
    Composition_Char["Characteristics:<br/>- Complete environment<br/>- Environment-specific values<br/>- Not reusable<br/>- Combines infrastructure modules"]
    
    Resource -.-> Resource_Char
    Infrastructure -.-> Infrastructure_Char
    Composition -.-> Composition_Char
```

**Sources:** [references/module-patterns.md:23-35]()

### Decision Tree for Module Classification

The following decision logic determines the appropriate module type for any Terraform configuration:

```mermaid
flowchart TD
    Start["New Terraform Configuration"]
    Q1{"Environment-specific<br/>configuration?"}
    Q2{"Combines multiple<br/>infrastructure concerns?"}
    Q3{"Focused group of<br/>related resources?"}
    
    CompType["Composition<br/>environments/prod/<br/>environments/staging/"]
    InfraType["Infrastructure Module<br/>modules/web-application/"]
    ResourceType["Resource Module<br/>modules/vpc/<br/>modules/rds/"]
    
    Start --> Q1
    Q1 -->|"YES"| CompType
    Q1 -->|"NO"| Q2
    Q2 -->|"YES"| InfraType
    Q2 -->|"NO"| Q3
    Q3 -->|"YES"| ResourceType
```

**Sources:** [references/module-patterns.md:127-140]()

### Module Type Comparison

| Type | When to Use | Scope | Example | Reusability |
|------|-------------|-------|---------|-------------|
| **Resource Module** | Single logical group of connected resources | Tightly coupled resources that always work together | VPC + subnets + route tables | High - used across projects |
| **Infrastructure Module** | Collection of resource modules for a purpose | Multiple resource modules in one region/account | Complete networking stack for web app | Medium - purpose-specific |
| **Composition** | Complete infrastructure | Spans multiple regions/accounts | Production environment | None - environment-specific |

**Sources:** [references/module-patterns.md:29-33]()

---

## Module Structure and File Organization

### Standard File Layout

All modules follow a consistent file organization pattern to ensure discoverability and maintainability:

```mermaid
graph TB
    subgraph "Required Files"
        main["main.tf<br/>Resource definitions,<br/>module calls,<br/>data sources"]
        variables["variables.tf<br/>Input variable<br/>declarations"]
        outputs["outputs.tf<br/>Output value<br/>declarations"]
        versions["versions.tf<br/>Provider and<br/>Terraform version<br/>constraints"]
        readme["README.md<br/>Usage<br/>documentation"]
    end
    
    subgraph "Conditional Files"
        tfvars["terraform.tfvars<br/>ONLY at composition level<br/>NEVER in modules"]
        locals["locals.tf<br/>Complex local value<br/>calculations"]
        data["data.tf<br/>Data sources if<br/>main.tf gets large"]
        backend["backend.tf<br/>ONLY at composition level<br/>remote state config"]
    end
    
    subgraph "Supporting Files"
        precommit[".pre-commit-config.yaml<br/>Automated validation"]
        gitignore[".gitignore<br/>Excluded files"]
        license["LICENSE<br/>MIT or Apache 2.0<br/>for public modules"]
    end
```

**Sources:** [references/module-patterns.md:142-165](), [references/module-patterns.md:361-390]()

### Repository Structure for Module Development

```mermaid
graph LR
    subgraph "Module Repository"
        Root["module-root/"]
        
        Core["main.tf<br/>variables.tf<br/>outputs.tf<br/>versions.tf<br/>README.md"]
        
        Examples["examples/"]
        Simple["examples/simple/<br/>Minimal working example"]
        Complete["examples/complete/<br/>Full-featured example"]
        
        Tests["tests/"]
        TestFile["tests/module_test.tftest.hcl"]
        
        Config[".pre-commit-config.yaml<br/>.gitignore<br/>LICENSE"]
    end
    
    Root --> Core
    Root --> Examples
    Root --> Tests
    Root --> Config
    Examples --> Simple
    Examples --> Complete
    Tests --> TestFile
```

**Sources:** [references/module-patterns.md:361-390]()

### File Organization Rationale

The standardized file structure provides several benefits:

- **Consistency:** Same structure across all modules enables muscle memory
- **Discoverability:** Know exactly where to find specific configuration types
- **Maintainability:** Easier navigation and modification
- **Terraform Registry:** Required structure for publishing public modules
- **Separation of Concerns:** Each file has a single, clear responsibility

**Sources:** [references/module-patterns.md:161-165]()

---

## Architecture Principles

### Principle 1: Smaller Scopes Reduce Blast Radius

Dividing infrastructure into focused, isolated scopes provides performance and safety benefits:

```mermaid
graph TB
    subgraph "Anti-pattern: Monolithic Composition"
        Mono["environments/prod/main.tf<br/>2000 lines<br/>VPC + EC2 + RDS + S3 + IAM"]
        MonoIssues["Issues:<br/>- 10+ minute plan time<br/>- Single mistake affects everything<br/>- No parallel development<br/>- Difficult to reason about"]
    end
    
    subgraph "Best Practice: Separated Compositions"
        Net["environments/prod/networking/<br/>VPC, subnets, route tables"]
        Compute["environments/prod/compute/<br/>EC2, ASG, ALB"]
        Data["environments/prod/data/<br/>RDS, ElastiCache"]
        Storage["environments/prod/storage/<br/>S3, EFS"]
        IAM["environments/prod/iam/<br/>IAM roles, policies"]
        
        Benefits["Benefits:<br/>- Faster plan/apply<br/>- Isolated failures<br/>- Parallel development<br/>- Clear ownership"]
    end
    
    Mono -.->|"Refactor to"| Net
    Mono -.->|"Refactor to"| Compute
    Mono -.->|"Refactor to"| Data
    Mono -.->|"Refactor to"| Storage
    Mono -.->|"Refactor to"| IAM
```

**Sources:** [references/module-patterns.md:171-195]()

### Principle 2: Remote State for Team Collaboration

Remote state backend configuration is mandatory for production infrastructure:

```mermaid
graph LR
    subgraph "Local State - Never Use"
        Local["terraform.tfstate<br/>local file"]
        LocalIssues["Problems:<br/>- Lost on computer crash<br/>- No team sharing<br/>- No state locking<br/>- No version history"]
    end
    
    subgraph "Remote State - Always Use"
        Remote["backend 's3'"]
        S3["S3 bucket<br/>my-terraform-state"]
        DynamoDB["DynamoDB table<br/>terraform-locks"]
        
        RemoteBenefits["Benefits:<br/>- Disaster recovery<br/>- Team collaboration<br/>- State locking<br/>- Encryption at rest"]
    end
    
    Remote --> S3
    Remote --> DynamoDB
    S3 --> RemoteBenefits
    DynamoDB --> RemoteBenefits
```

The required backend configuration pattern:

**Sources:** [references/module-patterns.md:197-225](), [references/module-patterns.md:215-224]()

### Principle 3: terraform_remote_state as Cross-Stack Glue

Remote state data sources enable loose coupling between independently managed infrastructure stacks:

```mermaid
graph TB
    subgraph "Production Networking Stack"
        NetMain["environments/prod/networking/main.tf"]
        NetState["S3: prod/networking/terraform.tfstate"]
        NetOutputs["outputs.tf:<br/>vpc_id<br/>private_subnet_ids"]
        
        NetMain --> NetState
        NetMain --> NetOutputs
    end
    
    subgraph "Production Compute Stack"
        CompMain["environments/prod/compute/main.tf"]
        RemoteStateData["data 'terraform_remote_state' 'networking'"]
        CompResources["module 'ec2':<br/>vpc_id = remote_state.outputs.vpc_id<br/>subnet_ids = remote_state.outputs.private_subnet_ids"]
        
        CompMain --> RemoteStateData
        RemoteStateData --> CompResources
    end
    
    NetState -.->|"Read outputs"| RemoteStateData
```

**Sources:** [references/module-patterns.md:227-274]()

### Principle 4: Parameterized Resource Modules

Resource modules must avoid hardcoded values to maintain reusability:

| Anti-pattern | Best Practice |
|-------------|---------------|
| Hardcoded AMI ID: `"ami-0c55b159cbfafe1f0"` | Data source or variable: `data.aws_ami.ubuntu.id` |
| Hardcoded instance type: `"t3.large"` | Variable: `var.instance_type` |
| Hardcoded subnet ID: `"subnet-12345678"` | Variable: `var.subnet_id` |
| Hardcoded environment tag: `"production"` | Variable: `var.tags` |

**Sources:** [references/module-patterns.md:275-315]()

### Principle 5: Compositions Contain Environment-Specific Values

The composition layer provides concrete values while modules provide abstractions:

```mermaid
graph LR
    subgraph "Module Layer - Abstract"
        ModVars["variables.tf:<br/>var.instance_type<br/>var.multi_az<br/>var.backup_retention"]
        ModResources["main.tf:<br/>Uses var.* references<br/>No hardcoded values"]
    end
    
    subgraph "Composition Layer - Concrete"
        ProdValues["environments/prod/main.tf:<br/>instance_type = 'db.r5.xlarge'<br/>multi_az = true<br/>backup_retention = 30"]
        DevValues["environments/dev/main.tf:<br/>instance_type = 'db.t3.micro'<br/>multi_az = false<br/>backup_retention = 7"]
    end
    
    ProdValues -->|"Provides values to"| ModVars
    DevValues -->|"Provides values to"| ModVars
    ModVars --> ModResources
```

**Sources:** [references/module-patterns.md:317-355]()

---

## Variable Design Patterns

### Complete Variable Declaration Pattern

Variables must include comprehensive metadata for proper validation and documentation:

```mermaid
graph TB
    VarDecl["variable 'instance_type'"]
    
    Desc["description:<br/>'EC2 instance type for<br/>the application server'"]
    Type["type: string"]
    Default["default: 't3.micro'"]
    Validation["validation block:<br/>condition + error_message"]
    
    VarDecl --> Desc
    VarDecl --> Type
    VarDecl --> Default
    VarDecl --> Validation
    
    Benefits["Benefits:<br/>- Self-documenting<br/>- Early error detection<br/>- Clear user guidance<br/>- Type safety"]
    
    Desc --> Benefits
    Type --> Benefits
    Default --> Benefits
    Validation --> Benefits
```

**Sources:** [references/module-patterns.md:450-477]()

### Variable Best Practices

| Practice | Implementation | Example |
|----------|---------------|---------|
| **Always include description** | Helps users understand variable purpose | `description = "EC2 instance type for the application server"` |
| **Use explicit type constraints** | Catches errors early | `type = string`, `type = map(string)` |
| **Provide sensible defaults** | Where appropriate for optional settings | `default = "t3.micro"` |
| **Add validation blocks** | For complex constraints | `validation { condition = contains([...], var.x) }` |
| **Mark sensitive variables** | For secrets (Terraform 0.14+) | `sensitive = true` |

**Sources:** [references/module-patterns.md:479-485]()

### Variable Naming Conventions

Context-specific naming prevents ambiguity:

```mermaid
graph LR
    subgraph "Anti-pattern: Generic Names"
        Bad1["var.name"]
        Bad2["var.type"]
        Bad3["var.value"]
        Issue["Problem: Ambiguous,<br/>hard to understand"]
    end
    
    subgraph "Best Practice: Context-Specific Names"
        Good1["var.vpc_cidr_block"]
        Good2["var.database_instance_class"]
        Good3["var.application_port"]
        Benefit["Benefit: Clear,<br/>self-documenting"]
    end
    
    Bad1 -.->|"Rename to"| Good1
    Bad2 -.->|"Rename to"| Good2
    Bad3 -.->|"Rename to"| Good3
```

**Sources:** [references/module-patterns.md:487-499]()

---

## Output Design Patterns

### Complete Output Declaration Pattern

Outputs should include descriptions and sensitivity markings:

```mermaid
graph TB
    Output["output 'instance_id'"]
    
    Desc["description:<br/>'ID of the created<br/>EC2 instance'"]
    Value["value:<br/>aws_instance.this.id"]
    Sensitive["sensitive: false<br/>(explicitly documented)"]
    
    Output --> Desc
    Output --> Value
    Output --> Sensitive
    
    Uses["Used by:<br/>- Module consumers<br/>- Remote state references<br/>- Documentation generation"]
    
    Desc --> Uses
    Value --> Uses
    Sensitive --> Uses
```

**Sources:** [references/module-patterns.md:503-532]()

### Output Best Practices

| Practice | Purpose | Example |
|----------|---------|---------|
| **Always include description** | Explain output purpose and intended use | `description = "ID of the created EC2 instance"` |
| **Mark sensitive outputs** | Prevent exposure in logs | `sensitive = true` |
| **Return objects for related values** | Group logically related data | `value = { id = ..., private_ip = ..., public_dns = ... }` |
| **Document intended use** | What should consumers do with this output? | `description = "Connection information for the instance"` |

**Sources:** [references/module-patterns.md:534-539]()

---

## Common Patterns and Anti-Patterns

### for_each vs count for Resource Creation

```mermaid
graph TB
    subgraph "Best Practice: for_each"
        ForEach["resource 'aws_instance' 'server'<br/>for_each = toset(['web', 'api', 'worker'])"]
        ForEachBehavior["Behavior:<br/>Removing 'api' only destroys<br/>aws_instance.server['api']"]
        ForEachBenefit["Benefit:<br/>Stable resource addresses<br/>No cascading changes"]
    end
    
    subgraph "Anti-pattern: count"
        Count["resource 'aws_instance' 'server'<br/>count = length(var.server_names)"]
        CountBehavior["Behavior:<br/>Removing server_names[1] destroys<br/>and recreates all instances after it"]
        CountIssue["Problem:<br/>Destroys server_names[2],<br/>server_names[3], etc.<br/>then recreates them"]
    end
    
    ForEach --> ForEachBehavior --> ForEachBenefit
    Count --> CountBehavior --> CountIssue
```

**Sources:** [references/module-patterns.md:543-574]()

### Module Versioning Pattern

Version pinning prevents unexpected breaking changes:

```mermaid
graph LR
    Consumer["Consuming Code"]
    ModuleCall["module 'vpc'"]
    Source["source = 'terraform-aws-modules/vpc/aws'"]
    Version["version = '~> 5.0'"]
    
    Constraint["Constraint Meaning:<br/>~> 5.0 allows:<br/>5.0, 5.1, 5.2<br/>but NOT 6.0"]
    
    Consumer --> ModuleCall
    ModuleCall --> Source
    ModuleCall --> Version
    Version --> Constraint
```

**Sources:** [references/module-patterns.md:614-625]()

### Locals for Computed Values

Use `locals` blocks to compute values once and reference them multiple times:

**Pattern:**
- Merge common tags with resource-specific tags
- Construct resource names from multiple variables
- Calculate derived values used by multiple resources

**Sources:** [references/module-patterns.md:593-611]()

### Critical Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| **Hard-coded environment values in modules** | Module locked to single environment | Make everything configurable via variables |
| **God modules** | Creates VPC, EC2, RDS, S3, IAM all in one | Break into focused, single-purpose modules |
| **count/for_each for environments in root** | Can't separate state files, huge blast radius | Use separate root modules per environment |
| **Overuse of terraform_remote_state** | Creates tight coupling between stacks | Use module outputs when possible, reserve remote state for cross-team boundaries |

**Sources:** [references/module-patterns.md:629-728]()

---

## Testing Philosophy and Patterns

### Testing Layers

Terraform module testing follows a progressive validation approach:

```mermaid
graph TB
    L1["Layer 1: Syntax Validation<br/>terraform fmt -check -recursive"]
    L2["Layer 2: Configuration Validity<br/>terraform validate"]
    L3["Layer 3: Plan Preview<br/>terraform plan"]
    L4["Layer 4: Integration Testing<br/>terraform apply + verify + destroy"]
    
    L1 --> L2
    L2 --> L3
    L3 --> L4
    
    L1Result["Fast, cheap<br/>No cloud resources"]
    L2Result["Fast, cheap<br/>No cloud resources"]
    L3Result["Fast, minimal cost<br/>No cloud resources"]
    L4Result["Slow, expensive<br/>Creates real resources"]
    
    L1 -.-> L1Result
    L2 -.-> L2Result
    L3 -.-> L3Result
    L4 -.-> L4Result
```

**Sources:** [references/module-patterns.md:940-973]()

### Core Testing Areas

What to verify in Terraform module tests:

| Testing Area | What to Verify | Method |
|-------------|----------------|--------|
| **Input validation** | Variables accept valid values and reject invalid ones | Test validation blocks with invalid values |
| **Resource creation** | Resources created with correct attributes | Apply and inspect with provider CLI |
| **Output correctness** | Outputs return expected values and types | Verify output types and non-empty values |
| **Idempotency** | Applying twice doesn't recreate resources | Run plan after apply, expect no changes |
| **Destroy completeness** | All resources cleaned up properly | Verify state is empty after destroy |

**Sources:** [references/module-patterns.md:925-933]()

### Idempotency Testing Pattern

The most critical test for Terraform modules:

```mermaid
graph LR
    Apply1["terraform apply<br/>-auto-approve"]
    Plan2["terraform plan<br/>-detailed-exitcode"]
    ExitCode{"Exit code?"}
    Success["Exit 0:<br/>Idempotent ✓"]
    Failure["Exit 2:<br/>Changes detected<br/>NOT idempotent ✗"]
    
    Apply1 --> Plan2
    Plan2 --> ExitCode
    ExitCode -->|"0"| Success
    ExitCode -->|"2"| Failure
```

**Why idempotency matters:**
- Proves configuration is stable
- No resource churn on repeated applies
- Safe to run in CI/CD pipelines
- Indicates proper use of computed values

**Sources:** [references/module-patterns.md:1010-1029]()

### Testing Strategy by Module Type

| Module Type | Testing Focus | Approach |
|-------------|---------------|----------|
| **Resource modules** | Input validation, resource creation, outputs, idempotency | Minimal config tests, mock providers for unit tests |
| **Infrastructure modules** | Module composition, cross-module dependencies | Different configuration combinations, integration tests in test account |
| **Compositions** | Can it plan? Production-like values? Remote state connectivity? | Smoke tests, manual QA in lower environments first |

**Sources:** [references/module-patterns.md:1063-1082]()

### Cost Control for Testing

Strategies to minimize testing costs while maintaining quality:

```mermaid
graph TB
    Strategy1["Use mocking for unit tests<br/>Terraform 1.7+ mock_provider"]
    Strategy2["Tag test resources<br/>Environment=test, TTL=2h"]
    Strategy3["Run integration tests<br/>only on main branch"]
    Strategy4["Use smaller instance types<br/>t3.micro for testing"]
    Strategy5["Implement auto-cleanup<br/>Lambda + TTL tag enforcement"]
    
    Benefits["Benefits:<br/>- Reduced cloud costs<br/>- Faster test execution<br/>- Easier cleanup<br/>- Cost attribution"]
    
    Strategy1 --> Benefits
    Strategy2 --> Benefits
    Strategy3 --> Benefits
    Strategy4 --> Benefits
    Strategy5 --> Benefits
```

**Sources:** [references/module-patterns.md:1084-1122]()

---

## Module Naming Conventions

### Public vs Private Module Naming

```mermaid
graph TB
    subgraph "Public Modules - Terraform Registry"
        PubPattern["Pattern:<br/>terraform-PROVIDER-NAME"]
        PubEx1["terraform-aws-vpc"]
        PubEx2["terraform-aws-eks"]
        PubEx3["terraform-google-network"]
    end
    
    subgraph "Private Modules - Organization-Specific"
        PrivPattern["Pattern:<br/>ORG-terraform-PROVIDER-NAME"]
        PrivEx1["acme-terraform-aws-vpc"]
        PrivEx2["acme-terraform-aws-rds"]
    end
    
    PubPattern --> PubEx1
    PubPattern --> PubEx2
    PubPattern --> PubEx3
    
    PrivPattern --> PrivEx1
    PrivPattern --> PrivEx2
```

**Sources:** [references/module-patterns.md:731-757]()

---

## Pre-commit Hooks and Automation

### Standard Pre-commit Configuration

All modules should include automated validation through pre-commit hooks:

```mermaid
graph LR
    PreCommit[".pre-commit-config.yaml"]
    
    Hook1["terraform_fmt:<br/>Format code"]
    Hook2["terraform_validate:<br/>Check syntax"]
    Hook3["terraform_tflint:<br/>Lint analysis"]
    Hook4["terraform_docs:<br/>Generate README"]
    
    PreCommit --> Hook1
    PreCommit --> Hook2
    PreCommit --> Hook3
    PreCommit --> Hook4
    
    Benefits["Benefits:<br/>- Consistent formatting<br/>- Early error detection<br/>- Automated documentation<br/>- Code quality enforcement"]
    
    Hook1 --> Benefits
    Hook2 --> Benefits
    Hook3 --> Benefits
    Hook4 --> Benefits
```

**Required files for module generation:**
- `.pre-commit-config.yaml` (standard template)
- `LICENSE` file (MIT or Apache 2.0 for public modules)
- `.gitignore` (from standard template)
- `README.md` with attribution footer

**Sources:** [references/module-patterns.md:777-819]()

### README Attribution Template

Modules created with terraform-skill guidance should include attribution:

**When to include:**
- ✅ All new modules created with terraform-skill guidance
- ✅ Public modules (GitHub, Terraform Registry)
- ✅ Private modules shared within organizations
- ⚠️ Optional for one-off environment configurations

**Rationale:** This is a derivative work as defined in Apache 2.0 License Section 1. Attribution supports the open-source ecosystem.

**Sources:** [references/module-patterns.md:820-864]()

---

## Terraform vs OpenTofu Preference

Before generating any module or configuration, the system must determine user preference:

```mermaid
graph TD
    Start["Module Generation Request"]
    Ask["Ask user:<br/>'Will this be for<br/>Terraform or OpenTofu?'"]
    
    UserChoice{"User specifies?"}
    ProjectDetect["Detect from existing:<br/>.terraform/ or .tofu/"]
    
    TerraformPath["Use 'terraform' commands<br/>in documentation"]
    TofuPath["Use 'tofu' commands<br/>in documentation"]
    BothPath["Show both options<br/>in documentation"]
    
    Start --> Ask
    Ask --> UserChoice
    UserChoice -->|"Yes"| TerraformPath
    UserChoice -->|"Yes"| TofuPath
    UserChoice -->|"No"| ProjectDetect
    ProjectDetect -->|".terraform/ found"| TerraformPath
    ProjectDetect -->|".tofu/ found"| TofuPath
    ProjectDetect -->|"Neither"| BothPath
```

**Note:** The HCL code itself is identical between Terraform and OpenTofu. The choice primarily affects:
- Command examples in documentation
- Binary references in CI/CD workflows
- README.md requirements table

**Sources:** [references/module-patterns.md:405-447]()

---

## Module Development Checklist

When creating or reviewing modules, verify:

- [ ] Ask: Terraform or OpenTofu?
- [ ] Ask: Public or private module?
- [ ] Include `examples/` directory with simple and complete examples
- [ ] Write tests (native Terraform tests or Terratest)
- [ ] Document inputs and outputs in README.md
- [ ] Version your module (semantic versioning)
- [ ] Create `.gitignore` from standard template
- [ ] Create `.pre-commit-config.yaml` from standard template
- [ ] Create `LICENSE` file (MIT or Apache 2.0 for public modules)
- [ ] Add attribution footer to README.md

**Sources:** [references/module-patterns.md:764-775]()

---

# Page: Code Patterns & Modern Features

# Code Patterns & Modern Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [references/code-patterns.md](references/code-patterns.md)

</details>



This document provides comprehensive guidance on Terraform/OpenTofu code structure, modern language features, and refactoring patterns. It covers block ordering conventions, the `count` vs `for_each` decision framework, version-specific features from Terraform 0.13+ through 1.11+, version constraint strategies, and safe refactoring techniques.

For high-level module architecture principles, see [Module Development Patterns](#4.2). For command-line usage and troubleshooting, see [Quick Reference & Commands](#4.4).

---

## Block Ordering & Structure

Terraform enforces strict argument ordering conventions within resource blocks to maintain consistency and readability across codebases. The canonical ordering follows a specific hierarchy designed to surface meta-arguments first.

### Resource Block Argument Order

```mermaid
graph TD
    START["resource block"]
    COUNT["1. count or for_each<br/>(FIRST, with blank line after)"]
    ARGS["2. Other arguments<br/>(alphabetical or logical grouping)"]
    TAGS["3. tags<br/>(last real argument)"]
    DEPENDS["4. depends_on<br/>(after tags, if needed)"]
    LIFECYCLE["5. lifecycle<br/>(very end, if needed)"]
    
    START --> COUNT
    COUNT --> ARGS
    ARGS --> TAGS
    TAGS --> DEPENDS
    DEPENDS --> LIFECYCLE
```

**Sources:** [references/code-patterns.md:21-69]()

The pattern enforces `count` or `for_each` as the first argument because these meta-arguments determine whether the resource will be created at all. A blank line follows to visually separate the conditional logic from the resource configuration. The `tags` argument appears last among real arguments to keep resource-specific configuration grouped together. Meta-arguments `depends_on` and `lifecycle` follow at the very end since they control Terraform's execution behavior rather than the resource's actual configuration.

| Position | Argument | Purpose | Required Blank Line |
|----------|----------|---------|---------------------|
| 1 | `count` or `for_each` | Conditional creation | Yes (after) |
| 2 | Other arguments | Resource configuration | No |
| 3 | `tags` | Metadata/labels | No |
| 4 | `depends_on` | Explicit dependencies | No |
| 5 | `lifecycle` | Terraform behavior | No |

**Sources:** [references/code-patterns.md:21-69]()

### Variable Block Structure

```mermaid
graph LR
    VAR["variable block"]
    DESC["1. description<br/>(ALWAYS required)"]
    TYPE["2. type"]
    DEFAULT["3. default"]
    SENSITIVE["4. sensitive<br/>(when true)"]
    NULLABLE["5. nullable<br/>(when false)"]
    VALIDATION["6. validation"]
    
    VAR --> DESC
    DESC --> TYPE
    TYPE --> DEFAULT
    DEFAULT --> SENSITIVE
    SENSITIVE --> NULLABLE
    NULLABLE --> VALIDATION
```

**Sources:** [references/code-patterns.md:71-95]()

Every variable must include a `description` as the first argument. This is not just convention but a requirement for self-documenting code. The `type` follows to define the data structure, then `default` for optional variables. The `sensitive` and `nullable` attributes modify behavior when set to non-default values (`true` and `false` respectively).

### Output Naming Convention

Output identifiers follow the pattern `{name}_{type}_{attribute}`, omitting the `this_` prefix that is common in resource declarations. Plural forms indicate list returns.

| Pattern | Example | Return Type |
|---------|---------|-------------|
| `{name}_{type}_{attribute}` | `security_group_id` | Single value |
| `{name}_{type}_{attribute}s` | `private_subnet_ids` | List |

**Sources:** [references/code-patterns.md:144-168]()

---

## Count vs For_Each Decision Framework

The choice between `count` and `for_each` affects resource addressability, state management, and behavior during list modifications.

### Decision Tree

```mermaid
graph TD
    START["Resource needs iteration?"]
    BOOLEAN["Boolean condition<br/>(create or don't)?"]
    SIMPLE["Simple numeric<br/>replication?"]
    ORDER["Order doesn't matter<br/>AND items won't change?"]
    
    USE_COUNT_BOOL["Use count = condition ? 1 : 0"]
    USE_COUNT_NUM["Use count = N"]
    USE_FOREACH["Use for_each"]
    
    START -->|Yes| BOOLEAN
    START -->|No| NONE["No iteration needed"]
    
    BOOLEAN -->|Yes| USE_COUNT_BOOL
    BOOLEAN -->|No| SIMPLE
    
    SIMPLE -->|Yes| ORDER
    SIMPLE -->|No| USE_FOREACH
    
    ORDER -->|Yes| USE_COUNT_NUM
    ORDER -->|No| USE_FOREACH
```

**Sources:** [references/code-patterns.md:172-259]()

### Count Use Cases

The `count` meta-argument works best for:

1. **Boolean conditions** where resources are either created or not created
2. **Simple numeric replication** with stable item order
3. **Fixed lists** that will never have items added or removed from the middle

The boolean pattern `count = var.create_nat_gateway ? 1 : 0` appears extensively in conditional resource creation. Resources created with `count` are addressed by numeric index: `aws_nat_gateway.this[0]`.

**Sources:** [references/code-patterns.md:174-196]()

### For_Each Use Cases

The `for_each` meta-argument provides:

1. **Key-based addressing** for stable resource references
2. **Safe list modification** where items can be added/removed without recreating other resources
3. **Named resource sets** with semantic keys

Resources created with `for_each` use the `each.key` and `each.value` references and are addressed by their key: `aws_subnet.private["us-east-1a"]`.

**Sources:** [references/code-patterns.md:200-259]()

### Impact of List Modification

```mermaid
graph TB
    subgraph count_behavior["count Behavior"]
        COUNT_LIST["var.availability_zones = <br/>['us-east-1a', 'us-east-1b', 'us-east-1c']"]
        COUNT_REMOVE["Remove 'us-east-1b'"]
        COUNT_RESULT["Result: Recreates resources at<br/>index [1] and [2]"]
        
        COUNT_LIST --> COUNT_REMOVE
        COUNT_REMOVE --> COUNT_RESULT
    end
    
    subgraph foreach_behavior["for_each Behavior"]
        FOREACH_LIST["var.availability_zones = <br/>['us-east-1a', 'us-east-1b', 'us-east-1c']"]
        FOREACH_REMOVE["Remove 'us-east-1b'"]
        FOREACH_RESULT["Result: Only destroys<br/>resource['us-east-1b']"]
        
        FOREACH_LIST --> FOREACH_REMOVE
        FOREACH_REMOVE --> FOREACH_RESULT
    end
```

**Sources:** [references/code-patterns.md:215-232]()

When using `count`, removing an item from the middle of a list causes Terraform to shift all subsequent resources down by one index, triggering destroy/recreate cycles. With `for_each`, resources are addressed by stable keys, so removal only affects that specific resource.

---

## Modern Terraform Features by Version

Terraform has introduced significant language enhancements across versions 0.13 through 1.11+. Adoption of these features reduces code complexity and improves state management.

### Feature Timeline

| Version | Feature | Replacement For | Key Benefit |
|---------|---------|-----------------|-------------|
| 0.13+ | `try()` | `element(concat())` | Simplified null handling |
| 1.1+ | `nullable = false` | Manual null checks | Explicit null rejection |
| 1.1+ | `moved` blocks | State surgery | Refactoring without recreation |
| 1.3+ | `optional()` | Multiple object types | Default values in objects |
| 1.8+ | Provider functions | Custom logic | Provider-native operations |
| 1.9+ | Cross-variable validation | External validation | Inter-variable constraints |
| 1.11+ | Write-only arguments | Secrets in state | Secrets never stored |

**Sources:** [references/code-patterns.md:335-525]()

### try() Function Pattern

```mermaid
graph LR
    LEGACY["element(concat(aws_security_group.this.*.id, ['']), 0)"]
    MODERN["try(aws_security_group.this[0].id, '')"]
    
    LEGACY -.->|"Replaced by"| MODERN
    
    LEGACY_STEPS["1. Create list with splat<br/>2. Concat with default<br/>3. Extract first element"]
    MODERN_STEPS["1. Try first element<br/>2. Return default if fails"]
    
    LEGACY --> LEGACY_STEPS
    MODERN --> MODERN_STEPS
```

**Sources:** [references/code-patterns.md:337-361]()

The `try()` function replaces the legacy `element(concat())` pattern for accessing potentially non-existent resources. It accepts multiple fallback arguments and returns the first successful evaluation. The pattern `try(aws_security_group.this[0].id, "")` attempts to access the resource at index 0, returning an empty string if it doesn't exist.

### optional() with Defaults

The `optional()` type constructor enables object attributes with default values, reducing the need for complex `merge()` operations.

```mermaid
graph TB
    OBJECT["variable 'database_config' type = object()"]
    REQ_NAME["name: string<br/>(required)"]
    REQ_ENGINE["engine: string<br/>(required)"]
    REQ_CLASS["instance_class: string<br/>(required)"]
    OPT_BACKUP["backup_retention:<br/>optional(number, 7)"]
    OPT_MONITOR["monitoring_enabled:<br/>optional(bool, true)"]
    OPT_TAGS["tags:<br/>optional(map(string), {})"]
    
    OBJECT --> REQ_NAME
    OBJECT --> REQ_ENGINE
    OBJECT --> REQ_CLASS
    OBJECT --> OPT_BACKUP
    OBJECT --> OPT_MONITOR
    OBJECT --> OPT_TAGS
```

**Sources:** [references/code-patterns.md:377-402]()

Users can omit optional attributes when calling modules, and the defaults specified in the `optional()` constructor are automatically applied. This pattern appears in [references/code-patterns.md:106-126]() and [references/code-patterns.md:381-402]().

### moved Blocks for Refactoring

The `moved` block enables resource renaming and restructuring without destroy/recreate cycles.

```mermaid
graph LR
    COUNT_ADDR["aws_subnet.private[0]<br/>aws_subnet.private[1]<br/>aws_subnet.private[2]"]
    
    MOVED["moved blocks:<br/>from = [0] to = ['us-east-1a']<br/>from = [1] to = ['us-east-1b']<br/>from = [2] to = ['us-east-1c']"]
    
    FOREACH_ADDR["aws_subnet.private['us-east-1a']<br/>aws_subnet.private['us-east-1b']<br/>aws_subnet.private['us-east-1c']"]
    
    COUNT_ADDR --> MOVED
    MOVED --> FOREACH_ADDR
```

**Sources:** [references/code-patterns.md:262-327](), [references/code-patterns.md:404-426]()

The migration from `count` to `for_each` requires `moved` blocks to preserve existing resources. Each `moved` block maps an old address to a new address. Running `terraform plan` after adding `moved` blocks should show only move operations, not destroy/create.

### Write-Only Arguments

Terraform 1.11+ introduces write-only arguments that prevent sensitive values from being stored in state files. These arguments use a `_wo` suffix.

```mermaid
graph TD
    SECRET["AWS Secrets Manager<br/>'prod-database-password'"]
    DATA_SECRET["data.aws_secretsmanager_secret"]
    DATA_VERSION["data.aws_secretsmanager_secret_version"]
    RESOURCE["aws_db_instance.this"]
    
    WO_ARG["password_wo =<br/>secret_string"]
    STATE["Terraform state<br/>(password NOT stored)"]
    AWS["AWS RDS<br/>(password stored)"]
    
    SECRET --> DATA_SECRET
    DATA_SECRET --> DATA_VERSION
    DATA_VERSION --> WO_ARG
    WO_ARG --> RESOURCE
    RESOURCE -.->|"Never written to"| STATE
    RESOURCE --> AWS
```

**Sources:** [references/code-patterns.md:488-524]()

The write-only pattern fetches secrets from external secret managers using data sources, passes them to resources via `*_wo` arguments, and ensures they never appear in the Terraform state file. This is critical for compliance with secret management policies.

---

## Version Management Strategy

Version constraints control Terraform core, provider, and module updates. The strategy balances stability with security patch adoption.

### Constraint Syntax

```mermaid
graph TB
    EXACT["version = '5.0.0'<br/>(exact - inflexible)"]
    PESSIMISTIC["version = '~> 5.0'<br/>(pessimistic - recommended)"]
    RANGE["version = '>= 5.0, < 6.0'<br/>(range)"]
    MINIMUM["version = '>= 5.0'<br/>(minimum - risky)"]
    LATEST["(no constraint)<br/>(latest - unpredictable)"]
    
    STABILITY["Stability"]
    FLEXIBILITY["Flexibility"]
    
    EXACT --> STABILITY
    PESSIMISTIC --> STABILITY
    PESSIMISTIC --> FLEXIBILITY
    RANGE --> FLEXIBILITY
    MINIMUM --> FLEXIBILITY
    LATEST --> FLEXIBILITY
```

**Sources:** [references/code-patterns.md:528-550]()

The pessimistic constraint operator `~>` allows patch-level updates but prevents minor or major version changes. For example, `~> 5.0` permits `5.0.x` but blocks `5.1.0`. This balances receiving security patches while preventing breaking changes.

### Component Versioning Strategy

| Component | Constraint Type | Example | Rationale |
|-----------|----------------|---------|-----------|
| Terraform Core | Pessimistic minor | `~> 1.9` | Allow patch updates only |
| Providers (production) | Pessimistic major | `~> 5.0` | Allow minor/patch updates |
| Providers (dev) | Pessimistic major | `~> 5.0` | Same as production |
| Modules (production) | Exact | `5.1.2` | Maximum stability |
| Modules (dev) | Pessimistic minor | `~> 5.1` | Allow patch updates |

**Sources:** [references/code-patterns.md:552-594]()

Production modules use exact versions to prevent unexpected changes during `terraform init`. Development environments can use pessimistic constraints to test newer versions before promoting to production.

### Version Lock File Workflow

```mermaid
sequenceDiagram
    participant DEV as "Developer"
    participant VERSIONS as "versions.tf"
    participant LOCK as ".terraform.lock.hcl"
    participant PROVIDERS as "Provider Registry"
    
    DEV->>VERSIONS: "Define version constraints<br/>(~> 5.0)"
    DEV->>PROVIDERS: "terraform init"
    PROVIDERS->>LOCK: "Lock exact versions<br/>(5.0.14)"
    DEV->>LOCK: "Commit to repository"
    
    Note over DEV,PROVIDERS: Later: Security update needed
    
    DEV->>PROVIDERS: "terraform init -upgrade"
    PROVIDERS->>LOCK: "Update to 5.0.15"
    DEV->>DEV: "terraform plan<br/>(verify changes)"
    DEV->>LOCK: "Commit updated lock"
```

**Sources:** [references/code-patterns.md:613-638]()

The `.terraform.lock.hcl` file records the exact provider versions selected during `terraform init`. This file must be committed to version control to ensure all team members use identical provider versions. The `terraform init -upgrade` command updates providers within the constraints defined in `versions.tf`.

---

## Refactoring Patterns

Safe refactoring of Terraform code requires migration strategies that preserve existing infrastructure while updating code patterns.

### Legacy to Modern Migration Checklist

The migration from Terraform 0.12/0.13 to 1.x involves replacing deprecated patterns with modern equivalents:

- [ ] Replace `element(concat(...))` with `try()`
- [ ] Add `nullable = false` to variables that shouldn't accept null
- [ ] Use `optional()` in object types for optional attributes
- [ ] Add `validation` blocks to variables with constraints
- [ ] Migrate secrets to write-only arguments (Terraform 1.11+)
- [ ] Use `moved` blocks for resource refactoring (Terraform 1.1+)
- [ ] Consider cross-variable validation (Terraform 1.9+)

**Sources:** [references/code-patterns.md:676-719]()

### Secrets Remediation Pattern

```mermaid
graph TB
    subgraph before["Before: Secrets in State"]
        VAR_PASS["variable 'db_password'<br/>(sensitive = true)"]
        OR["OR"]
        RANDOM["random_password.db"]
        RDS_BAD["aws_db_instance.this<br/>password = var.db_password"]
        STATE_BAD["Terraform state<br/>(contains password)"]
        
        VAR_PASS -.-> RDS_BAD
        RANDOM -.-> RDS_BAD
        RDS_BAD --> STATE_BAD
    end
    
    subgraph after["After: External Secrets (TF 1.11+)"]
        SM["AWS Secrets Manager<br/>'prod-database-password'"]
        DATA_SM["data.aws_secretsmanager_secret"]
        DATA_VER["data.aws_secretsmanager_secret_version"]
        RDS_GOOD["aws_db_instance.this<br/>password_wo = secret_string"]
        STATE_GOOD["Terraform state<br/>(no password)"]
        
        SM --> DATA_SM
        DATA_SM --> DATA_VER
        DATA_VER --> RDS_GOOD
        RDS_GOOD -.->|"Not written"| STATE_GOOD
    end
```

**Sources:** [references/code-patterns.md:721-804]()

The remediation process involves:

1. Creating the secret in AWS Secrets Manager outside Terraform
2. Adding data sources to fetch the secret
3. Updating resources to use the `*_wo` argument variant
4. Removing `random_password` resources or `sensitive` variables
5. Verifying the secret does not appear in `terraform show` output

For Terraform versions before 1.11, secrets must be managed entirely outside Terraform to avoid state file storage.

---

## Locals for Dependency Management

Local values can encode implicit dependencies to control resource deletion order without explicit `depends_on` declarations.

### VPC Deletion Order Pattern

```mermaid
graph TB
    subgraph creation["Resource Creation Order"]
        CREATE_VPC["aws_vpc.this"]
        CREATE_CIDR["aws_vpc_ipv4_cidr_block_association.this[0]"]
        CREATE_SUBNET["aws_subnet.public<br/>(vpc_id = local.vpc_id)"]
        
        CREATE_VPC --> CREATE_CIDR
        CREATE_CIDR --> CREATE_SUBNET
    end
    
    subgraph local_logic["local.vpc_id Logic"]
        TRY["try()"]
        CIDR_REF["aws_vpc_ipv4_cidr_block_association.this[0].vpc_id"]
        VPC_REF["aws_vpc.this.id"]
        EMPTY["''"]
        
        TRY --> CIDR_REF
        CIDR_REF -.->|"fallback"| VPC_REF
        VPC_REF -.->|"fallback"| EMPTY
    end
    
    subgraph deletion["Deletion Order (Implicit)"]
        DELETE_SUBNET["1. aws_subnet.public<br/>(depends on local.vpc_id)"]
        DELETE_CIDR["2. aws_vpc_ipv4_cidr_block_association.this[0]<br/>(referenced by local)"]
        DELETE_VPC["3. aws_vpc.this"]
        
        DELETE_SUBNET --> DELETE_CIDR
        DELETE_CIDR --> DELETE_VPC
    end
```

**Sources:** [references/code-patterns.md:807-856]()

The pattern uses `local.vpc_id` with a `try()` chain that references the secondary CIDR association before falling back to the VPC ID. This creates an implicit dependency graph:

```
aws_subnet.public → local.vpc_id → aws_vpc_ipv4_cidr_block_association.this[0] → aws_vpc.this
```

During destruction, Terraform must delete the subnet first (which depends on the local), then the CIDR association (which the local references), and finally the VPC. This prevents errors where Terraform attempts to delete the CIDR association while subnets still reference it.

### Common Use Cases

- VPC configurations with secondary CIDR blocks
- Resources depending on optional configurations
- Complex multi-resource dependency chains requiring specific deletion order

**Sources:** [references/code-patterns.md:852-856]()

---

**Related Documentation:**
- For module structure and hierarchy, see [Module Development Patterns](#4.2)
- For command-line workflows and troubleshooting, see [Quick Reference & Commands](#4.4)
- For testing methodology that validates these patterns, see [Testing Methodology](#5.3)

---

# Page: Quick Reference & Commands

# Quick Reference & Commands

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [references/quick-reference.md](references/quick-reference.md)

</details>



## Purpose and Scope

This page provides rapid-access command references, decision flowcharts, and troubleshooting guides for Terraform/OpenTofu development. It serves as a quick lookup resource during active development work, containing command cheat sheets, version-specific guidance, migration strategies, and pre-commit checklists.

For detailed module architecture patterns, see [Module Development Patterns](#4.2). For modern Terraform language features and code organization, see [Code Patterns & Modern Features](#4.3). For CI/CD pipeline integration, see [CI/CD Workflows](#4.5).

Sources: [references/quick-reference.md:1-6]()

---

## Command Cheat Sheet

The skill provides command references for both `terraform` and `tofu` (OpenTofu) commands, which are functionally equivalent for most operations.

### Static Analysis Commands

| Command | Purpose | Notes |
|---------|---------|-------|
| `terraform fmt -recursive -check` | Format validation | Works with `tofu` equivalent |
| `terraform validate` | Syntax validation | Validates configuration files |
| `tflint --init && tflint` | Linting | Third-party static analyzer |
| `checkov -d .` | Security scanning | Static security analysis |

### Native Testing (Terraform/OpenTofu 1.6+)

| Command | Purpose | Notes |
|---------|---------|-------|
| `terraform test` | Run all tests | Requires 1.6+ |
| `terraform test -test-directory=tests/unit/` | Specific directory | Target subset of tests |
| `terraform test -verbose` | Verbose output | Detailed test execution info |

### Plan Validation Workflow

| Command | Purpose | Output |
|---------|---------|--------|
| `terraform plan -out tfplan` | Generate plan | Binary plan file |
| `terraform show -json tfplan \| jq -r '.'` | Convert to JSON | Human-readable plan |
| `terraform show tfplan \| grep "will be created"` | Filter changes | Quick change summary |

Sources: [references/quick-reference.md:20-63]()

---

## Testing Approach Decision Tree

The skill provides a structured decision framework for selecting the appropriate testing strategy based on project requirements and Terraform/OpenTofu version.

### Testing Strategy Selection

```mermaid
graph TB
    START["Need to test Terraform/OpenTofu code?"]
    
    SYNTAX{"Just syntax/format?"}
    SECURITY{"Static security scan?"}
    VERSION{"Terraform/OpenTofu 1.6+?"}
    SIMPLE{"Simple logic test?"}
    COMPLEX{"Complex integration?"}
    TEAM{"Go team?"}
    
    VALIDATE["terraform/tofu validate + fmt"]
    TRIVY["trivy + checkov"]
    NATIVE["Native terraform/tofu test"]
    TERRATEST["Terratest"]
    UPGRADE["Plan to upgrade Terraform/OpenTofu"]
    
    START --> SYNTAX
    SYNTAX -->|Yes| VALIDATE
    SYNTAX -->|No| SECURITY
    
    SECURITY -->|Yes| TRIVY
    SECURITY -->|No| VERSION
    
    VERSION -->|Yes| SIMPLE
    VERSION -->|No| TEAM
    
    SIMPLE -->|Yes| NATIVE
    SIMPLE -->|No| COMPLEX
    
    COMPLEX -->|Yes| TERRATEST
    
    TEAM -->|Yes| TERRATEST
    TEAM -->|No| UPGRADE
```

Sources: [references/quick-reference.md:66-92]()

---

## Module Development Workflow

The skill defines a five-phase module development process that ensures quality and maintainability.

### Development Phases

```mermaid
graph LR
    subgraph "1. Plan"
        VARS["variables.tf<br/>Define inputs"]
        OUTPUTS["outputs.tf<br/>Define outputs"]
        README_PLAN["README.md<br/>Document purpose"]
    end
    
    subgraph "2. Implement"
        MAIN["main.tf<br/>Create resources"]
        VERSIONS["versions.tf<br/>Pin versions"]
        EXAMPLES["examples/<br/>simple/, complete/"]
    end
    
    subgraph "3. Test"
        STATIC["validate, fmt, lint"]
        UNIT["Native tests or Terratest"]
        INTEGRATION["examples/ testing"]
    end
    
    subgraph "4. Document"
        README_UPDATE["Update README usage"]
        INPUTS_OUTPUTS["Document inputs/outputs"]
        CHANGELOG["Add CHANGELOG"]
    end
    
    subgraph "5. Publish"
        TAG["git tag v1.0.0"]
        REGISTRY["Push to registry"]
        ANNOUNCE["Announce changes"]
    end
    
    VARS --> OUTPUTS --> README_PLAN
    README_PLAN --> MAIN
    MAIN --> VERSIONS --> EXAMPLES
    EXAMPLES --> STATIC
    STATIC --> UNIT --> INTEGRATION
    INTEGRATION --> README_UPDATE
    README_UPDATE --> INPUTS_OUTPUTS --> CHANGELOG
    CHANGELOG --> TAG
    TAG --> REGISTRY --> ANNOUNCE
```

Sources: [references/quick-reference.md:94-121]()

---

## Version-Specific Guidance

### Terraform/OpenTofu Version Capabilities

| Feature | 1.0-1.5 | 1.6+ | 1.7+ |
|---------|---------|------|------|
| Native testing framework | ❌ | ✅ `terraform test` | ✅ |
| Mock providers | ❌ | ❌ | ✅ Mock providers for unit testing |
| Terratest recommended | ✅ | ✅ (complex only) | ✅ (complex only) |
| Static analysis | ✅ | ✅ | ✅ |

### Terraform vs OpenTofu Decision Matrix

| Factor | Terraform | OpenTofu |
|--------|-----------|----------|
| Licensing | Business Source License (BSL) 1.1 | Mozilla Public License 2.0 (MPL 2.0) |
| Governance | HashiCorp (single vendor) | Linux Foundation (community-driven) |
| Latest Version | 1.14+ | 1.11+ |
| Native Testing | 1.6+ | 1.6+ |
| Mock Providers | 1.7+ | 1.7+ |
| Feature Parity | Reference implementation | Compatible fork with additions |
| Enterprise Support | HCP Terraform, Terraform Cloud | Multiple vendors |
| Migration Path | N/A | Drop-in replacement for Terraform ≤1.5 |

**When to choose Terraform:**
- Using HashiCorp Terraform Cloud or HCP Terraform
- Enterprise support contract with HashiCorp
- Need absolute latest features first

**When to choose OpenTofu:**
- Prefer open-source governance model
- Want to avoid vendor lock-in concerns
- Building on community-driven development
- BSL 1.1 license doesn't fit your use case

Sources: [references/quick-reference.md:125-182]()

---

## Troubleshooting Guide

### Common Issue Patterns

#### Issue 1: Tests Fail in CI But Pass Locally

```mermaid
graph LR
    SYMPTOM["Symptoms:<br/>Local pass, CI fail"]
    
    subgraph "Common Causes"
        VERSIONS["Different Terraform/<br/>provider versions"]
        ENV["Different environment<br/>variables"]
        CREDS["Different AWS<br/>credentials/permissions"]
    end
    
    SOLUTION["Solution:<br/>versions.tf<br/>Pin versions explicitly"]
    
    SYMPTOM --> VERSIONS
    SYMPTOM --> ENV
    SYMPTOM --> CREDS
    
    VERSIONS --> SOLUTION
    ENV --> SOLUTION
    CREDS --> SOLUTION
```

**Resolution:** Pin versions in `versions.tf`:

```hcl
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"  # Pin to major version
    }
  }
}
```

Sources: [references/quick-reference.md:186-213]()

#### Issue 2: Parallel Test Conflicts

**Symptoms:**
- Tests fail when run in parallel
- Error: "ResourceAlreadyExistsException"

**Cause:** Resource naming collisions

**Terratest Solution:**

```go
import "github.com/gruntwork-io/terratest/modules/random"

uniqueId := random.UniqueId()
bucketName := fmt.Sprintf("test-bucket-%s", uniqueId)
```

Sources: [references/quick-reference.md:215-231]()

#### Issue 3: High Test Costs

The skill provides five strategies for reducing test infrastructure costs:

| Strategy | Implementation | Use Case |
|----------|----------------|----------|
| Mock providers | `mock_provider "aws" { ... }` | Terraform 1.7+ unit tests |
| Resource TTL tags | `tags = { "TTL" = "2h" }` | Automated cleanup systems |
| Conditional integration tests | `if: github.ref == 'refs/heads/main'` | Run full tests only on main |
| Smaller instance types | `instance_type = "t3.micro"` | Test environments |
| Shared resources | Reuse VPCs, security groups | Stable infrastructure |

Sources: [references/quick-reference.md:233-269]()

---

## Migration Paths

### Migration Strategy Map

```mermaid
graph TB
    subgraph "Manual Testing"
        MANUAL_START["Manual testing"]
    end
    
    subgraph "Static Analysis"
        VALIDATE["terraform validate"]
        FMT["terraform fmt -check"]
    end
    
    subgraph "Plan Review"
        PLAN["terraform plan -out=tfplan"]
        MANUAL_REVIEW["Manual plan review"]
    end
    
    subgraph "Automated Testing"
        NATIVE["Native tests (1.6+)"]
        TERRATEST["Terratest"]
    end
    
    subgraph "CI/CD Integration"
        GITHUB["GitHub Actions"]
        GITLAB["GitLab CI"]
        AUTO_APPLY["Automated apply on main"]
    end
    
    MANUAL_START --> VALIDATE
    VALIDATE --> FMT
    FMT --> PLAN
    PLAN --> MANUAL_REVIEW
    MANUAL_REVIEW --> NATIVE
    MANUAL_REVIEW --> TERRATEST
    NATIVE --> GITHUB
    TERRATEST --> GITHUB
    GITHUB --> GITLAB
    GITLAB --> AUTO_APPLY
```

Sources: [references/quick-reference.md:272-294]()

### Terratest to Native Tests Migration

**Gradual migration strategy:**

| Test Type | Keep in Terratest | Migrate to Native |
|-----------|-------------------|-------------------|
| Complex integration tests | ✅ | ❌ |
| Multi-step workflows | ✅ | ❌ |
| Cross-provider tests | ✅ | ❌ |
| Simple unit tests | ❌ | ✅ |
| Logic validation | ❌ | ✅ |
| Mock-friendly tests | ❌ | ✅ |

**Directory structure during transition:**

```
tests/
├── unit/                    # Native tests
│   └── validation.tftest.hcl
└── integration/             # Terratest
    └── complete_test.go
```

Sources: [references/quick-reference.md:296-323]()

### Terraform to OpenTofu Migration

**Migration requirements:**

1. **No code changes needed** - OpenTofu is a drop-in replacement
2. **Update CI/CD commands:**

| Before (Terraform) | After (OpenTofu) |
|-------------------|------------------|
| `terraform init` | `tofu init` |
| `terraform plan` | `tofu plan` |
| `terraform apply` | `tofu apply` |

3. **Update documentation** to mention OpenTofu compatibility

Sources: [references/quick-reference.md:325-350]()

---

## Pre-Commit Checklist

### Formatting and Validation

```bash
# Format all Terraform files
terraform fmt -recursive

# Validate configuration
terraform validate
```

### Naming Convention Checklist

- [ ] All identifiers use `_` not `-`
- [ ] No resource names repeat resource type (no `aws_vpc.main_vpc`)
- [ ] Single-instance resources named `this` or descriptive name
- [ ] Variables have plural names for lists/maps (`subnet_ids` not `subnet_id`)
- [ ] All variables have descriptions
- [ ] All outputs have descriptions
- [ ] Output names follow `{name}_{type}_{attribute}` pattern
- [ ] No double negatives in variable names

### Code Structure Checklist

- [ ] `count`/`for_each` at top of resource blocks (blank line after)
- [ ] `tags` as last real argument in resources
- [ ] `depends_on` after tags (if used)
- [ ] `lifecycle` at end of resource (if used)
- [ ] Variables ordered: description → type → default → sensitive → nullable → validation
- [ ] Only `#` comments used (no `//` or `/* */`)

### Modern Features Checklist

- [ ] Using `try()` not `element(concat())`
- [ ] Secrets use write-only arguments or external data sources (not in state)
- [ ] `nullable = false` set on non-null variables
- [ ] `optional()` used in object types where applicable (Terraform 1.3+)
- [ ] Variable validation blocks added where constraints needed
- [ ] Consider cross-variable validation for related variables (Terraform 1.9+)

### Architecture Checklist

- [ ] `terraform.tfvars` only at composition level (not in modules)
- [ ] Remote state configured (never local state)
- [ ] Resource modules don't hardcode values (use variables/data sources)
- [ ] `terraform_remote_state` used for cross-composition dependencies
- [ ] File structure follows standard: `main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`

### Documentation Checklist

- [ ] **README.md exists** with absolute links (Terraform Registry compatibility)
- [ ] **All variables documented** in README with descriptions and types
- [ ] **All outputs documented** in README with descriptions
- [ ] **Usage examples provided** showing how to use the module
- [ ] **Version requirements specified** (Terraform version, provider versions)

Sources: [references/quick-reference.md:353-413]()

---

## Version Management

### Version Constraint Syntax

| Syntax | Meaning | Use Case |
|--------|---------|----------|
| `"5.0.0"` | Exact version | Avoid (inflexible) |
| `"~> 5.0"` | Pessimistic (5.0.x) | Recommended for stability |
| `"~> 5.0.1"` | Pessimistic (5.0.x where x >= 1) | Specific patch minimum |
| `">= 5.0, < 6.0"` | Range | Any 5.x version |
| `">= 5.0"` | Minimum | Risky (breaking changes) |

### Version Strategy by Component

| Component | Recommendation | Example |
|-----------|----------------|---------|
| **Terraform** | Pin minor, allow patch | `required_version = "~> 1.9"` |
| **Providers** | Pin major, allow minor/patch | `version = "~> 5.0"` |
| **Modules (prod)** | Pin exact version | `version = "5.1.2"` |
| **Modules (dev)** | Allow patch updates | `version = "~> 5.1"` |

### Update Workflow

```mermaid
graph LR
    LOCK["terraform init<br/>Creates .terraform.lock.hcl"]
    UPGRADE["terraform init -upgrade<br/>Updates providers"]
    PLAN["terraform plan<br/>Review changes"]
    COMMIT["git add .terraform.lock.hcl<br/>git commit"]
    
    LOCK --> UPGRADE
    UPGRADE --> PLAN
    PLAN --> COMMIT
```

### Update Strategy by Severity

| Update Type | Timing | Testing Path |
|-------------|--------|--------------|
| Security patches | Immediate | dev → stage → prod |
| Minor versions | Monthly/quarterly | Review changelog, test thoroughly |
| Major versions | Planned cycles | Dedicated testing, phased rollout |

Sources: [references/quick-reference.md:416-471]()

---

## Refactoring Quick Reference

### Common Refactoring Patterns

#### Pattern 1: Count to For_Each Migration

```mermaid
graph LR
    STEP1["Step 1:<br/>Add for_each,<br/>keep count commented"]
    STEP2["Step 2:<br/>Add moved blocks<br/>for each resource"]
    STEP3["Step 3:<br/>terraform plan<br/>(verify 'moved')"]
    STEP4["Step 4:<br/>Apply changes"]
    STEP5["Step 5:<br/>Remove commented count"]
    
    STEP1 --> STEP2
    STEP2 --> STEP3
    STEP3 --> STEP4
    STEP4 --> STEP5
```

**Key principle:** Use `moved` blocks to preserve existing resources, avoiding destroy/create cycles.

Sources: [references/quick-reference.md:476-490]()

#### Pattern 2: Legacy to Modern Terraform

**0.12/0.13 → 1.x migration checklist:**

- [ ] Replace `element(concat(...))` → `try()`
- [ ] Add `nullable = false` where appropriate
- [ ] Use `optional()` in object types (1.3+)
- [ ] Add `validation` blocks
- [ ] Migrate secrets to write-only arguments (1.11+)
- [ ] Use `moved` blocks for refactoring (1.1+)
- [ ] Add cross-variable validation (1.9+)

Sources: [references/quick-reference.md:492-502]()

#### Pattern 3: Secrets Remediation

**Goal:** Move secrets out of Terraform state

```bash
# Step 1: Create secret in AWS Secrets Manager (outside Terraform)
aws secretsmanager create-secret --name prod-db-password --secret-string "..."

# Step 2: Update Terraform to use data sources
# Step 3: Use write-only argument (Terraform 1.11+)
# Step 4: Remove random_password resource or variable
# Step 5: Apply and verify secret not in state
terraform show | grep -i password  # Should not appear
```

Sources: [references/quick-reference.md:504-517]()

### Refactoring Decision Tree

```mermaid
graph TB
    START["What are you refactoring?"]
    
    ADDRESSING["Resource addressing<br/>(count[0] → for_each['key'])"]
    SECRETS["Secrets in state"]
    LEGACY["Legacy Terraform syntax<br/>(0.12/0.13)"]
    STRUCTURE["Module structure<br/>(rename, reorganize)"]
    
    MOVED_FOREACH["Use: moved blocks +<br/>for_each conversion"]
    SECRETS_MGR["Use: AWS Secrets Manager +<br/>write-only arguments (1.11+)"]
    MODERN["Use: Modern feature<br/>checklist"]
    MOVED_PRESERVE["Use: moved blocks to<br/>preserve resources"]
    
    START --> ADDRESSING
    START --> SECRETS
    START --> LEGACY
    START --> STRUCTURE
    
    ADDRESSING --> MOVED_FOREACH
    SECRETS --> SECRETS_MGR
    LEGACY --> MODERN
    STRUCTURE --> MOVED_PRESERVE
```

Sources: [references/quick-reference.md:519-535]()

### Migration Best Practices

#### Before Refactoring

1. Backup state file
2. Test in development first
3. Review `terraform plan` carefully
4. Document what changed and why

#### During Refactoring

1. One change at a time
2. Verify each step with `terraform plan`
3. Use `moved` blocks, not destroy/recreate
4. Keep git history clean with logical commits

#### After Refactoring

1. Verify idempotency (plan shows no changes)
2. Test in staging before production
3. Update documentation
4. Communicate changes to team

For detailed refactoring patterns, see [Code Patterns & Modern Features](#4.3).

Sources: [references/quick-reference.md:537-557]()

---

## Common Patterns

### Resource Naming Conventions

| Pattern | Example | Status |
|---------|---------|--------|
| Descriptive, contextual | `resource "aws_instance" "web_server" { }` | ✅ Good |
| Generic | `resource "aws_instance" "main" { }` | ❌ Bad |
| Context-specific variables | `var.vpc_cidr_block` | ✅ Good |
| Generic variables | `var.cidr` | ❌ Bad |

### Standard Module File Structure

```
Standard module structure:
├── main.tf          # Primary resources
├── variables.tf     # Input variables
├── outputs.tf       # Output values
├── versions.tf      # Provider versions
└── README.md        # Documentation
```

Sources: [references/quick-reference.md:561-597]()

---

# Page: CI/CD Workflows

# CI/CD Workflows

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [references/ci-cd-workflows.md](references/ci-cd-workflows.md)

</details>



This page documents CI/CD pipeline integration patterns for Terraform and OpenTofu infrastructure-as-code projects. It covers workflow templates for GitHub Actions and GitLab CI, cost optimization strategies, automated resource cleanup, and production deployment patterns.

For module development guidance, see [Module Development Patterns](#4.2). For testing strategies that integrate with these workflows, see [Quick Reference & Commands](#4.4). For security scanning integration, see [Security & Compliance](#4.6).

**Sources:** [references/ci-cd-workflows.md:1-6]()

---

## Overview

The CI/CD workflow system provides four primary capabilities:

| Capability | Purpose | Implementation Files |
|------------|---------|---------------------|
| **Validation** | Format checking, linting, validation | `.github/workflows/terraform.yml` (validate job) |
| **Testing** | Unit and integration test execution | `.github/workflows/terraform.yml` (test job) |
| **Planning** | Change preview and cost estimation | `.github/workflows/terraform.yml` (plan, cost-estimate jobs) |
| **Deployment** | Automated infrastructure application | `.github/workflows/terraform.yml` (apply job) |

The reference file provides complete, production-ready templates that implement these capabilities across multiple CI/CD platforms.

**Sources:** [references/ci-cd-workflows.md:10-17]()

---

## GitHub Actions Pipeline Architecture

### Pipeline Structure

```mermaid
graph TB
    subgraph "Push/PR Trigger"
        TRIGGER["on: push, pull_request"]
    end
    
    subgraph "Validation Stage"
        VALIDATE["validate job"]
        FMT["terraform fmt -check"]
        INIT["terraform init"]
        VAL["terraform validate"]
        TFLINT["tflint"]
    end
    
    subgraph "Test Stage"
        TEST["test job<br/>needs: validate"]
        TFTEST["terraform test"]
        TERRATEST["Terratest (Go)"]
    end
    
    subgraph "Planning Stage"
        PLAN["plan job<br/>needs: test"]
        PLANINIT["terraform init"]
        PLANRUN["terraform plan -out=tfplan"]
        UPLOAD["upload-artifact@v3"]
        
        COST["cost-estimate job<br/>needs: plan"]
        INFRA["infracost breakdown"]
        COMMENT["infracost/actions/comment@v1"]
    end
    
    subgraph "Deployment Stage"
        APPLY["apply job<br/>needs: plan<br/>if: main branch<br/>environment: production"]
        DOWNLOAD["download-artifact@v3"]
        APPLYRUN["terraform apply tfplan"]
    end
    
    TRIGGER --> VALIDATE
    VALIDATE --> FMT
    VALIDATE --> INIT
    VALIDATE --> VAL
    VALIDATE --> TFLINT
    
    VALIDATE --> TEST
    TEST --> TFTEST
    TEST --> TERRATEST
    
    TEST --> PLAN
    PLAN --> PLANINIT
    PLAN --> PLANRUN
    PLAN --> UPLOAD
    
    PLAN --> COST
    COST --> INFRA
    COST --> COMMENT
    
    PLAN --> APPLY
    APPLY --> DOWNLOAD
    APPLY --> APPLYRUN
```

**Diagram: Complete GitHub Actions Terraform Workflow Pipeline**

The workflow is defined in [references/ci-cd-workflows.md:24-107]() and uses job dependencies (`needs:`) to enforce sequential execution. Key implementation details:

- **Conditional Apply**: The `apply` job uses `if: github.ref == 'refs/heads/main' && github.event_name == 'push'` to restrict deployments to the main branch
- **Environment Protection**: The `environment: production` setting enables manual approval gates
- **Artifact Passing**: Plan files are transferred between jobs using `actions/upload-artifact@v3` and `actions/download-artifact@v3`

**Sources:** [references/ci-cd-workflows.md:20-107]()

### Job Definitions

#### validate Job

```mermaid
graph LR
    CHECKOUT["actions/checkout@v3"]
    SETUP["hashicorp/setup-terraform@v2"]
    FMT["terraform fmt -check -recursive"]
    INIT["terraform init"]
    VAL["terraform validate"]
    TFLINT["tflint install & run"]
    
    CHECKOUT --> SETUP
    SETUP --> FMT
    FMT --> INIT
    INIT --> VAL
    VAL --> TFLINT
```

**Diagram: validate Job Execution Flow**

This job performs static analysis without requiring cloud credentials. Implementation at [references/ci-cd-workflows.md:31-50]() includes:
- Format verification with `terraform fmt -check -recursive`
- Syntax validation with `terraform validate`
- Policy checking with `tflint`

**Sources:** [references/ci-cd-workflows.md:31-50]()

#### test Job

The `test` job has two execution paths depending on the testing framework:

| Framework | Setup Action | Test Command | Configuration |
|-----------|-------------|--------------|---------------|
| Native Terraform Tests | N/A | `terraform test` | Test files in `tests/` directory |
| Terratest | `actions/setup-go@v4` with Go 1.21 | `go test -v -timeout 30m -parallel 4` | Test files in `tests/` directory |

Implementation at [references/ci-cd-workflows.md:52-70]() shows both patterns. The Terratest path requires additional setup of the Go environment before test execution.

**Sources:** [references/ci-cd-workflows.md:52-70]()

#### plan Job

The `plan` job generates an execution plan and uploads it as an artifact:

1. Checkout code and setup Terraform
2. Run `terraform init`
3. Execute `terraform plan -out=tfplan`
4. Upload `tfplan` artifact with name `tfplan`

The artifact is stored for 90 days by default and consumed by the `apply` and `cost-estimate` jobs. Implementation at [references/ci-cd-workflows.md:72-89]().

**Sources:** [references/ci-cd-workflows.md:72-106]()

#### cost-estimate Job

The cost estimation integration uses Infracost to analyze plan files:

```mermaid
graph TB
    PLANARTIFACT["Plan artifact<br/>from plan job"]
    SETUP["infracost/actions/setup@v2<br/>api-key: INFRACOST_API_KEY"]
    BREAKDOWN["infracost breakdown<br/>--path .<br/>--format json<br/>--out-file /tmp/infracost.json"]
    COMMENT["infracost/actions/comment@v1<br/>behavior: update"]
    
    PLANARTIFACT --> SETUP
    SETUP --> BREAKDOWN
    BREAKDOWN --> COMMENT
```

**Diagram: Infracost Integration Flow**

This job requires the `INFRACOST_API_KEY` secret to be configured in GitHub repository settings. The `behavior: update` parameter ensures cost comments are updated rather than creating new comments on each run.

**Sources:** [references/ci-cd-workflows.md:109-134]()

#### apply Job

The `apply` job implementation at [references/ci-cd-workflows.md:91-106]() includes critical safety controls:

- **Branch Restriction**: `if: github.ref == 'refs/heads/main' && github.event_name == 'push'`
- **Environment Gate**: `environment: production` enables manual approval requirements
- **Plan Verification**: Downloads the exact plan file from the `plan` job to prevent drift

**Sources:** [references/ci-cd-workflows.md:91-106]()

---

## GitLab CI Pipeline Architecture

### Pipeline Structure

The GitLab CI implementation uses a template pattern with inheritance:

```mermaid
graph TB
    subgraph "Base Template"
        TEMPLATE[".terraform_template<br/>image: hashicorp/terraform:latest<br/>before_script:<br/>- cd TF_ROOT<br/>- terraform init"]
    end
    
    subgraph "Stage: validate"
        VAL["validate job<br/>extends: .terraform_template<br/>terraform fmt -check<br/>terraform validate"]
    end
    
    subgraph "Stage: test"
        TEST["test job<br/>extends: .terraform_template<br/>terraform test<br/>only: merge_requests, main"]
    end
    
    subgraph "Stage: plan"
        PLAN["plan job<br/>extends: .terraform_template<br/>terraform plan -out=tfplan<br/>artifacts: tfplan (1 week)<br/>only: merge_requests, main"]
    end
    
    subgraph "Stage: apply"
        APPLY["apply job<br/>extends: .terraform_template<br/>terraform apply tfplan<br/>dependencies: plan<br/>when: manual<br/>environment: production<br/>only: main"]
    end
    
    TEMPLATE --> VAL
    TEMPLATE --> TEST
    TEMPLATE --> PLAN
    TEMPLATE --> APPLY
    
    VAL --> TEST
    TEST --> PLAN
    PLAN --> APPLY
```

**Diagram: GitLab CI Template Inheritance and Stage Flow**

The `.terraform_template` base template at [references/ci-cd-workflows.md:151-155]() provides:
- Terraform Docker image configuration
- Working directory navigation (`cd ${TF_ROOT}`)
- Automatic `terraform init` execution in `before_script`

Each job extends this template and adds stage-specific commands. The `only` keyword controls execution context (merge requests vs. main branch).

**Sources:** [references/ci-cd-workflows.md:138-198]()

### Key Differences from GitHub Actions

| Feature | GitHub Actions | GitLab CI |
|---------|---------------|-----------|
| Template Pattern | Reusable workflows (separate files) | `.terraform_template` (inline) |
| Artifact Storage | `actions/upload-artifact@v3` | `artifacts.paths` with `expire_in` |
| Manual Approval | `environment:` with GitHub settings | `when: manual` |
| Branch Filtering | `if: github.ref == ...` | `only: main` |
| Dependency Declaration | `needs: job-name` | `dependencies: [job-name]` |

The GitLab implementation at [references/ci-cd-workflows.md:140-198]() demonstrates these patterns.

**Sources:** [references/ci-cd-workflows.md:138-198]()

---

## Cost Optimization Strategy

### Execution Cost Model

```mermaid
graph TB
    subgraph "Cost-Free Validation"
        PR["Pull Request"]
        FMT["terraform fmt"]
        VAL["terraform validate"]
        MOCK["terraform test<br/>(mocked providers)"]
    end
    
    subgraph "Controlled Cost Testing"
        MAIN["Main Branch Merge"]
        INTEG["Integration Tests<br/>if: github.ref == refs/heads/main<br/>Real AWS/GCP resources"]
        TAG["Resource tagging:<br/>Environment=test<br/>TTL=2h<br/>CreatedBy=CI<br/>JobID=GITHUB_RUN_ID"]
    end
    
    subgraph "Auto-Cleanup System"
        CRON["Schedule: 0 */2 * * *<br/>(every 2 hours)"]
        CLEANUP["cleanup-test-resources.sh<br/>Terminate resources where TTL expired"]
    end
    
    PR --> FMT
    PR --> VAL
    PR --> MOCK
    
    MAIN --> INTEG
    INTEG --> TAG
    
    TAG --> CRON
    CRON --> CLEANUP
    
    COSTFREE["FREE<br/>No cloud resources"]
    CONTROLLED["METERED<br/>Tagged and tracked"]
    PREVENTED["PREVENTED<br/>Auto-deleted"]
    
    FMT -.-> COSTFREE
    VAL -.-> COSTFREE
    MOCK -.-> COSTFREE
    
    INTEG -.-> CONTROLLED
    TAG -.-> CONTROLLED
    
    CLEANUP -.-> PREVENTED
```

**Diagram: Three-Tier Cost Optimization Strategy**

### Implementation Pattern

The conditional test execution pattern at [references/ci-cd-workflows.md:212-229]() implements cost controls:

```yaml
test:
  runs-on: ubuntu-latest
  steps:
    - name: Run Unit Tests (Mocked)
      run: terraform test

    - name: Run Integration Tests
      if: github.ref == 'refs/heads/main'
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      run: |
        cd tests
        go test -v -timeout 30m
```

This pattern ensures:
1. **PR validation** uses mocked tests (no cloud cost)
2. **Main branch** runs integration tests with real resources (metered cost)
3. Cloud credentials are only exposed to the main branch job

**Sources:** [references/ci-cd-workflows.md:200-229]()

### Resource Tagging

The Terratest example at [references/ci-cd-workflows.md:232-246]() shows cost-aware tagging:

```go
terraformOptions := &terraform.Options{
    TerraformDir: "../examples/complete",
    Vars: map[string]interface{}{
        "tags": map[string]string{
            "Environment": "test",
            "TTL":         "2h",
            "CreatedBy":   "CI",
            "JobID":       os.Getenv("GITHUB_RUN_ID"),
        },
    },
}
```

Tags enable:
- **Environment identification**: Filter test resources
- **TTL enforcement**: Automatic cleanup based on creation time
- **Audit trail**: Link resources to specific CI runs via `GITHUB_RUN_ID`

**Sources:** [references/ci-cd-workflows.md:231-246]()

---

## Automated Cleanup System

### Cleanup Architecture

```mermaid
graph TB
    subgraph "Trigger Mechanisms"
        CRON["Scheduled: every 2 hours<br/>cron: 0 */2 * * *"]
        MANUAL["Manual dispatch<br/>workflow_dispatch"]
    end
    
    subgraph "Cleanup Job"
        CHECKOUT["actions/checkout@v3"]
        AWSCONFIG["aws-actions/configure-aws-credentials@v2<br/>AWS_ACCESS_KEY_ID<br/>AWS_SECRET_ACCESS_KEY<br/>aws-region: us-east-1"]
        SCRIPT["cleanup-test-resources.sh"]
    end
    
    subgraph "Cleanup Logic"
        QUERY["aws resourcegroupstaggingapi get-resources<br/>--tag-filters Key=Environment,Values=test<br/>Query for TTL < 2 hours ago"]
        PARSE["Extract instance IDs from ARNs"]
        TERMINATE["aws ec2 terminate-instances<br/>--instance-ids"]
    end
    
    CRON --> CHECKOUT
    MANUAL --> CHECKOUT
    
    CHECKOUT --> AWSCONFIG
    AWSCONFIG --> SCRIPT
    
    SCRIPT --> QUERY
    QUERY --> PARSE
    PARSE --> TERMINATE
```

**Diagram: Automated Cleanup Workflow and Execution Flow**

### Cleanup Script Implementation

The cleanup script at [references/ci-cd-workflows.md:252-270]() uses AWS Resource Groups Tagging API to find and terminate expired test resources:

```bash
#!/bin/bash
# cleanup-test-resources.sh

# Find and terminate instances older than 2 hours with test tag
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Environment,Values=test \
  --query 'ResourceTagMappingList[?Tags[?Key==`TTL` && Value<`'$(date -u -d '2 hours ago' +%Y-%m-%dT%H:%M:%S)'`]].ResourceARN' \
  --output text | \
  while read arn; do
    instance_id=$(echo $arn | grep -oP 'instance/\K[^/]+')
    if [ ! -z "$instance_id" ]; then
      echo "Terminating instance: $instance_id"
      aws ec2 terminate-instances --instance-ids $instance_id
    fi
  done
```

This script:
1. Queries resources with `Environment=test` tag
2. Filters for resources with `TTL` older than 2 hours
3. Extracts EC2 instance IDs from resource ARNs
4. Terminates matching instances

**Sources:** [references/ci-cd-workflows.md:250-270]()

### Scheduled Workflow

The GitHub Actions workflow at [references/ci-cd-workflows.md:272-298]() implements scheduled cleanup:

- **Trigger**: Runs every 2 hours via cron schedule
- **Manual Override**: `workflow_dispatch` enables on-demand cleanup
- **AWS Credentials**: Uses GitHub secrets for authentication
- **Region**: Configured for `us-east-1` but can be parameterized

**Sources:** [references/ci-cd-workflows.md:272-298]()

---

## Production Deployment Best Practices

### Environment Separation

The reference documents two organizational patterns for environment management:

**Pattern 1: Separate Workflow Files**

```
.github/workflows/
  terraform-dev.yml
  terraform-staging.yml
  terraform-prod.yml
```

Each file contains a complete workflow for one environment.

**Pattern 2: Reusable Workflow with Parameters**

The reusable workflow pattern at [references/ci-cd-workflows.md:314-329]() defines a parameterized workflow:

```yaml
# .github/workflows/terraform-deploy.yml (reusable)
on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string

jobs:
  deploy:
    environment: ${{ inputs.environment }}
    # ... deployment steps
```

This is called from environment-specific workflows that pass the environment name as input.

**Sources:** [references/ci-cd-workflows.md:300-329]()

### Approval Gates

GitHub environment protection rules are enforced via the `environment` setting at [references/ci-cd-workflows.md:331-339]():

```yaml
apply:
  environment:
    name: production
    # Requires manual approval in GitHub
  when: manual
```

GitLab uses `when: manual` for equivalent functionality.

**Sources:** [references/ci-cd-workflows.md:331-339]()

### State Management

#### Remote State Configuration

The backend configuration example at [references/ci-cd-workflows.md:341-354]() shows S3 backend setup:

```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

Critical elements:
- **bucket**: S3 bucket for state storage
- **key**: Unique path per environment/workspace
- **dynamodb_table**: DynamoDB table for state locking
- **encrypt**: Server-side encryption enabled

**Sources:** [references/ci-cd-workflows.md:341-354]()

#### State Locking in CI

The `terraform apply` command at [references/ci-cd-workflows.md:356-362]() includes lock timeout handling:

```yaml
- name: Terraform Apply
  run: terraform apply -lock-timeout=10m tfplan
```

The `-lock-timeout=10m` parameter ensures the apply operation waits up to 10 minutes if another operation holds the state lock, preventing concurrent modification failures.

**Sources:** [references/ci-cd-workflows.md:356-362]()

### Plugin Caching

GitHub Actions cache configuration at [references/ci-cd-workflows.md:364-374]():

```yaml
- name: Cache Terraform Plugins
  uses: actions/cache@v3
  with:
    path: |
      ~/.terraform.d/plugin-cache
    key: ${{ runner.os }}-terraform-${{ hashFiles('**/.terraform.lock.hcl') }}
```

Cache key components:
- **OS identifier**: `runner.os` ensures platform-specific caching
- **Lock file hash**: `hashFiles('**/.terraform.lock.hcl')` invalidates cache when provider versions change

This reduces provider download time by caching providers between workflow runs.

**Sources:** [references/ci-cd-workflows.md:364-374]()

### Security Scanning Integration

The security scanning job at [references/ci-cd-workflows.md:376-395]() integrates static analysis tools:

```yaml
security-scan:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3

    - name: Run Trivy
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'config'
        scan-ref: '.'

    - name: Run Checkov
      uses: bridgecrewio/bridgecrewio/checkov-action@master
      with:
        directory: .
        framework: terraform
```

This job runs in parallel with validation and fails the build if security issues are detected. For detailed security scanning configuration, see [Security & Compliance](#4.6).

**Sources:** [references/ci-cd-workflows.md:376-395]()

---

## Atlantis Integration

### Architecture

```mermaid
graph TB
    subgraph "Version Control System"
        PR["Pull Request Created"]
        COMMENT["PR Comment:<br/>atlantis plan<br/>atlantis apply"]
    end
    
    subgraph "Atlantis Server"
        WEBHOOK["Webhook Handler"]
        ATLANTISYAML["atlantis.yaml<br/>projects:<br/>- name: production<br/>  dir: environments/prod<br/>  workflow: custom"]
        WORKFLOW["workflows.custom:<br/>plan.steps<br/>apply.steps"]
    end
    
    subgraph "Execution"
        PLANSTEPS["Plan Steps:<br/>- init<br/>- plan (extra_args: -lock false)"]
        APPLYSTEPS["Apply Steps:<br/>- apply"]
    end
    
    subgraph "Feedback"
        PRCOMMENT["Plan Output<br/>Posted as PR Comment"]
        LOCK["State Lock<br/>Prevents Concurrent Changes"]
    end
    
    PR --> WEBHOOK
    COMMENT --> WEBHOOK
    
    WEBHOOK --> ATLANTISYAML
    ATLANTISYAML --> WORKFLOW
    
    WORKFLOW --> PLANSTEPS
    WORKFLOW --> APPLYSTEPS
    
    PLANSTEPS --> PRCOMMENT
    APPLYSTEPS --> PRCOMMENT
    
    WEBHOOK --> LOCK
```

**Diagram: Atlantis Pull Request Automation Flow**

### Configuration

The `atlantis.yaml` configuration at [references/ci-cd-workflows.md:403-424]() defines:

```yaml
version: 3
projects:
  - name: production
    dir: environments/prod
    workspace: default
    terraform_version: v1.6.0
    workflow: custom

workflows:
  custom:
    plan:
      steps:
        - init
        - plan:
            extra_args: ["-lock", "false"]
    apply:
      steps:
        - apply
```

Configuration elements:
- **projects**: Defines Terraform root modules and their configurations
- **terraform_version**: Pins Terraform version per project
- **workflow**: References custom workflow definition
- **extra_args**: Passes additional arguments to Terraform commands

**Sources:** [references/ci-cd-workflows.md:399-424]()

### Benefits

Atlantis provides at [references/ci-cd-workflows.md:426-431]():

| Benefit | Description |
|---------|-------------|
| Plan results as PR comments | Terraform plan output appears directly in pull request comments |
| Apply via PR comments | Trigger deployments with `atlantis apply` comment |
| Locking prevents concurrent changes | Automatic state locking across pull requests |
| VCS integration | Works with GitHub, GitLab, Bitbucket, Azure DevOps |

**Sources:** [references/ci-cd-workflows.md:426-432]()

---

## Troubleshooting

### Version Mismatch Issues

**Problem**: Tests fail in CI but pass locally

**Root Cause**: Different Terraform or provider versions between local and CI environments

**Solution**: Version pinning in `versions.tf` at [references/ci-cd-workflows.md:438-455]():

```hcl
# versions.tf - Pin versions
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
```

This ensures consistent versions across all execution environments.

**Sources:** [references/ci-cd-workflows.md:436-455]()

### Parallel Test Conflicts

**Problem**: Parallel tests conflict due to resource naming collisions

**Root Cause**: Multiple test runs creating resources with identical names

**Solution**: Unique identifier generation at [references/ci-cd-workflows.md:457-469]():

```go
// Use unique identifiers
uniqueId := random.UniqueId()
bucketName := fmt.Sprintf("test-bucket-%s-%s",
    os.Getenv("GITHUB_RUN_ID"),
    uniqueId)
```

This pattern combines:
- **CI run identifier**: `GITHUB_RUN_ID` ensures uniqueness across workflow runs
- **Random identifier**: `uniqueId` ensures uniqueness within a single run when tests execute in parallel

**Sources:** [references/ci-cd-workflows.md:457-470]()

---

## Integration with Core Skill

The CI/CD workflows reference file is part of the progressive disclosure architecture documented in [Core Architecture](#3). When Claude processes Terraform pipeline questions, it:

1. Loads core guidance from `SKILL.md`
2. References `references/ci-cd-workflows.md` for detailed pipeline templates
3. Cross-references `references/security-compliance.md` for security scanning integration
4. Cross-references `references/module-patterns.md` for module testing in pipelines

This architecture is maintained by the validation workflow at [.github/workflows/validate.yml]() which ensures all reference links remain valid.

**Sources:** [references/ci-cd-workflows.md:1-6](), [references/ci-cd-workflows.md:473]()

---

# Page: Security & Compliance

# Security & Compliance

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [references/security-compliance.md](references/security-compliance.md)

</details>



**Purpose:** This page documents the security hardening guidance and compliance automation strategies provided by the terraform-skill knowledge base. It covers the `references/security-compliance.md` file, which is one of five on-demand reference documents loaded when Claude needs detailed security guidance.

**Scope:** This document focuses on security scanning tools, common security patterns, compliance testing frameworks, secrets management, state file security, and regulatory checklists. For general Terraform best practices, see [Core Skill Content](#4.1). For CI/CD integration with security scanning, see [CI/CD Workflows](#4.5).

---

## Overview

The security-compliance.md reference file provides ~2.5K tokens of security guidance (importance score: 0.70) that is loaded on-demand when users ask security-related questions. It is part of the [progressive disclosure architecture](#3.2) that keeps the core SKILL.md lightweight while maintaining comprehensive coverage of security topics.

**File Location:** [references/security-compliance.md:1-471]()

**Key Topics Covered:**
- Security scanning tool integration (Trivy, Checkov)
- Common security anti-patterns with corrections
- Compliance testing frameworks (terraform-compliance, OPA)
- Secrets management patterns
- State file encryption and access control
- IAM least-privilege principles
- Regulatory compliance checklists (SOC 2, HIPAA, PCI-DSS)

Sources: [references/security-compliance.md:1-17]()

---

## Security Scanning Tools

The document provides integration guidance for two primary security scanning tools: **Trivy** (successor to tfsec) and **Checkov**.

### Trivy Integration

Trivy is maintained by Aqua Security and performs static configuration scanning for infrastructure-as-code.

**Installation Methods:**
- macOS: `brew install trivy` [references/security-compliance.md:38-39]()
- Linux: curl install script [references/security-compliance.md:41-42]()
- GitHub Actions: `aquasecurity/trivy-action@master` [references/security-compliance.md:45-48]()

**Basic Usage:**
```bash
trivy config .
```
[references/security-compliance.md:25-26]()

**Example Output Format:** The tool provides HIGH/MEDIUM/LOW severity findings with file location and problematic code snippets [references/security-compliance.md:54-68]().

### Checkov Integration

Checkov provides framework-specific scanning with skip capabilities and JSON reporting.

**Command Examples:**
- Basic scan: `checkov -d . --framework terraform` [references/security-compliance.md:74]()
- Skip specific check: `checkov -d . --skip-check CKV_AWS_23` [references/security-compliance.md:77]()
- JSON output: `checkov -d . -o json > checkov-report.json` [references/security-compliance.md:80]()

### Security Scanning Workflow

```mermaid
flowchart TD
    Code["Terraform Code<br/>(*.tf files)"]
    
    subgraph "Static Analysis Tools"
        Trivy["trivy config .<br/>[references/security-compliance.md:26]"]
        Checkov["checkov -d .<br/>[references/security-compliance.md:74]"]
    end
    
    subgraph "Scan Results"
        TrivyOut["Trivy findings<br/>HIGH/MEDIUM/LOW<br/>[references/security-compliance.md:56]"]
        CheckovOut["Checkov report<br/>JSON format<br/>[references/security-compliance.md:80]"]
    end
    
    subgraph "CI Integration"
        GHAction["aquasecurity/trivy-action@master<br/>[references/security-compliance.md:45]"]
    end
    
    Code --> Trivy
    Code --> Checkov
    Trivy --> TrivyOut
    Checkov --> CheckovOut
    Code --> GHAction
    GHAction --> TrivyOut
    
    TrivyOut --> Review["Security Review"]
    CheckovOut --> Review
```

**Diagram: Security Scanning Tool Integration**

Sources: [references/security-compliance.md:20-82]()

---

## Security Anti-Patterns and Corrections

The document uses a consistent **"❌ DON'T / ✅ DO"** pattern to teach security best practices through contrasting examples.

### Pattern Categories

| Category | Anti-Pattern | Correction | Line Reference |
|----------|-------------|------------|----------------|
| **Secrets Management** | Plaintext variable defaults | AWS Secrets Manager data source | [85-108]() |
| **Network Security** | Default VPC usage | Custom VPC with private subnets | [110-134]() |
| **Encryption** | Unencrypted S3 bucket | `aws_s3_bucket_server_side_encryption_configuration` | [136-163]() |
| **Security Groups** | `0.0.0.0/0` ingress on all ports | Least-privilege with specific CIDR blocks | [165-191]() |
| **IAM Permissions** | Wildcard `Action = "*"` | Specific action list | [387-427]() |

### Secrets Management Pattern

**Anti-Pattern (DON'T):**
```hcl
variable "database_password" {
  type    = string
  default = "SuperSecret123!"  # ❌ Never do this
}
```
[references/security-compliance.md:91-94]()

**Correct Pattern (DO):**
```hcl
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "prod/database/password"
}

resource "aws_db_instance" "this" {
  password = data.aws_secretsmanager_secret_version.db_password.secret_string
}
```
[references/security-compliance.md:101-107]()

### Security Group Pattern

**Anti-Pattern (DON'T):**
```hcl
cidr_blocks = ["0.0.0.0/0"]  # ❌ Never do this
```
[references/security-compliance.md:174]()

**Correct Pattern (DO):**
```hcl
cidr_blocks = ["10.0.0.0/16"]  # ✅ Internal only
```
[references/security-compliance.md:188]()

Sources: [references/security-compliance.md:85-191](), [references/security-compliance.md:387-427]()

---

## Compliance Testing Frameworks

The document covers two compliance testing approaches: **terraform-compliance** (BDD-style) and **Open Policy Agent** (policy-as-code).

### terraform-compliance Framework

Uses Gherkin syntax for behavior-driven compliance testing.

**Installation:**
```bash
pip install terraform-compliance
```
[references/security-compliance.md:202]()

**Test Structure Example:**
```gherkin
Feature: AWS Resources must be encrypted

  Scenario: S3 buckets must have encryption
    Given I have aws_s3_bucket defined
    When it has aws_s3_bucket_server_side_encryption_configuration
    Then it must contain rule
    And it must contain apply_server_side_encryption_by_default
```
[references/security-compliance.md:208-215]()

**Execution Workflow:**
1. Generate plan: `terraform plan -out=tfplan` [references/security-compliance.md:227]()
2. Convert to JSON: `terraform show -json tfplan > tfplan.json` [references/security-compliance.md:228]()
3. Run tests: `terraform-compliance -f compliance/ -p tfplan.json` [references/security-compliance.md:231]()

### Open Policy Agent (OPA)

Uses Rego policy language for custom compliance rules.

**Policy Example:**
```rego
package terraform.s3

deny[msg] {
  resource := input.resource_changes[_]
  resource.type == "aws_s3_bucket"
  not resource.change.after.server_side_encryption_configuration

  msg := sprintf("S3 bucket '%s' must have encryption enabled", [resource.address])
}
```
[references/security-compliance.md:237-246]()

### Compliance Testing Workflow

```mermaid
flowchart LR
    TFCode["Terraform Code"]
    
    subgraph "Plan Generation"
        Plan["terraform plan -out=tfplan<br/>[references/security-compliance.md:227]"]
        JSON["terraform show -json<br/>[references/security-compliance.md:228]"]
    end
    
    subgraph "Compliance Testing"
        TFC["terraform-compliance<br/>BDD tests (.feature files)<br/>[references/security-compliance.md:208]"]
        OPA["Open Policy Agent<br/>Rego policies (.rego files)<br/>[references/security-compliance.md:237]"]
    end
    
    subgraph "Test Results"
        Pass["Compliance Pass"]
        Fail["Compliance Fail<br/>Block deployment"]
    end
    
    TFCode --> Plan
    Plan --> JSON
    JSON --> TFC
    JSON --> OPA
    TFC --> Pass
    TFC --> Fail
    OPA --> Pass
    OPA --> Fail
```

**Diagram: Compliance Testing Workflow**

Sources: [references/security-compliance.md:195-248]()

---

## Secrets Management Patterns

The document provides comprehensive secrets management patterns using AWS Secrets Manager and environment variables.

### AWS Secrets Manager Pattern

**Complete Implementation:**

1. **Create secret resource:** `aws_secretsmanager_secret` [references/security-compliance.md:257-262]()
2. **Set secret value:** `aws_secretsmanager_secret_version` [references/security-compliance.md:264-267]()
3. **Generate password:** `random_password` with 32 characters and special chars [references/security-compliance.md:270-273]()
4. **Retrieve secret:** `data "aws_secretsmanager_secret_version"` [references/security-compliance.md:276-278]()
5. **Use in resource:** Reference `secret_string` attribute [references/security-compliance.md:281]()

**Key Configuration:**
- Recovery window: 30 days [references/security-compliance.md:261]()
- Password length: 32 characters [references/security-compliance.md:271]()
- Special characters: enabled [references/security-compliance.md:272]()

### Environment Variables

**Usage Pattern:**
```bash
export TF_VAR_database_password="secret123"
export AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"
export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
```
[references/security-compliance.md:289-292]()

**Gitignore Protection:**
```
*.tfvars
.env
secrets/
```
[references/security-compliance.md:298-300]()

Sources: [references/security-compliance.md:251-302]()

---

## State File Security

State file security involves three layers: encryption at rest, bucket hardening, and access control.

### State File Security Architecture

```mermaid
flowchart TB
    subgraph "Terraform Backend Configuration"
        Backend["terraform backend s3<br/>[references/security-compliance.md:312]"]
        Encrypt["encrypt = true<br/>[references/security-compliance.md:317]"]
        DDB["dynamodb_table for locking<br/>[references/security-compliance.md:316]"]
    end
    
    subgraph "S3 Bucket Security"
        Bucket["aws_s3_bucket terraform_state<br/>[references/security-compliance.md:325]"]
        Versioning["aws_s3_bucket_versioning<br/>status = Enabled<br/>[references/security-compliance.md:330-336]"]
        SSE["aws_s3_bucket_server_side_encryption_configuration<br/>sse_algorithm = AES256<br/>[references/security-compliance.md:339-347]"]
        PublicBlock["aws_s3_bucket_public_access_block<br/>block_public_acls = true<br/>[references/security-compliance.md:350-357]"]
    end
    
    subgraph "Access Control"
        IAMPolicy["IAM Policy<br/>Specific role ARN<br/>[references/security-compliance.md:369]"]
        Actions["s3:ListBucket<br/>s3:GetObject<br/>s3:PutObject<br/>[references/security-compliance.md:371-374]"]
    end
    
    Backend --> Encrypt
    Backend --> DDB
    Backend --> Bucket
    
    Bucket --> Versioning
    Bucket --> SSE
    Bucket --> PublicBlock
    Bucket --> IAMPolicy
    IAMPolicy --> Actions
```

**Diagram: State File Security Layers**

### Encryption Configuration

**Backend Configuration:**
```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true  # ✅ Always enable encryption
  }
}
```
[references/security-compliance.md:311-319]()

### Bucket Hardening Resources

| Resource Type | Purpose | Key Configuration |
|--------------|---------|-------------------|
| `aws_s3_bucket_versioning` | Protect against deletion | `status = "Enabled"` [334]() |
| `aws_s3_bucket_server_side_encryption_configuration` | Encrypt at rest | `sse_algorithm = "AES256"` [344]() |
| `aws_s3_bucket_public_access_block` | Block public access | All four flags set to `true` [353-356]() |

### Access Control Policy

**IAM Policy Structure:**
- Principal: Specific role ARN `arn:aws:iam::123456789012:role/TerraformRole` [references/security-compliance.md:369]()
- Actions: Limited to `ListBucket`, `GetObject`, `PutObject` [references/security-compliance.md:371-374]()
- Resources: Both bucket and object levels [references/security-compliance.md:376-379]()

Sources: [references/security-compliance.md:305-383]()

---

## IAM Best Practices

The document emphasizes least-privilege IAM policies through contrasting examples.

### Least Privilege Pattern

**Correct Implementation:**
```hcl
resource "aws_iam_policy" "app_policy" {
  name = "app-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "arn:aws:s3:::my-app-bucket/*"
      }
    ]
  })
}
```
[references/security-compliance.md:393-409]()

**Key Characteristics:**
- Specific actions listed (no wildcards)
- Resource ARN includes specific bucket name
- Statement limited to necessary permissions

### Wildcard Anti-Pattern

**Incorrect Implementation:**
```hcl
Statement = [
  {
    Effect   = "Allow"
    Action   = "*"  # ❌ Never use wildcard
    Resource = "*"
  }
]
```
[references/security-compliance.md:418-423]()

**Problems:**
- Grants all AWS actions
- Applies to all resources
- Violates least-privilege principle

Sources: [references/security-compliance.md:387-427]()

---

## Compliance Checklists

The document provides three regulatory compliance checklists: SOC 2, HIPAA, and PCI-DSS.

### Compliance Requirements Table

| Framework | Key Requirements | Line Reference |
|-----------|-----------------|----------------|
| **SOC 2** | Encryption at rest/transit, least-privilege IAM, logging, MFA, security scanning | [434-440]() |
| **HIPAA** | PHI encryption, access logs, dedicated VPC, backup/retention, audit trail | [442-448]() |
| **PCI-DSS** | Network segmentation, no defaults, strong encryption, scanning, access control | [450-456]() |

### SOC 2 Compliance Checklist

[references/security-compliance.md:433-440]()

- ☐ Encryption at rest for all data stores
- ☐ Encryption in transit (TLS/SSL)
- ☐ IAM policies follow least privilege
- ☐ Logging enabled for all resources
- ☐ MFA required for privileged access
- ☐ Regular security scanning in CI/CD

### HIPAA Compliance Checklist

[references/security-compliance.md:442-448]()

- ☐ PHI encrypted at rest and in transit
- ☐ Access logs enabled
- ☐ Dedicated VPC with private subnets
- ☐ Regular backup and retention policies
- ☐ Audit trail for all infrastructure changes

### PCI-DSS Compliance Checklist

[references/security-compliance.md:450-456]()

- ☐ Network segmentation (separate VPCs)
- ☐ No default passwords
- ☐ Strong encryption algorithms
- ☐ Regular security scanning
- ☐ Access control and monitoring

Sources: [references/security-compliance.md:431-457]()

---

## External Resources

The document links to authoritative external documentation:

- **Trivy Documentation:** https://aquasecurity.github.io/trivy/ [references/security-compliance.md:462]()
- **Checkov Documentation:** https://www.checkov.io/ [references/security-compliance.md:463]()
- **terraform-compliance:** https://terraform-compliance.com/ [references/security-compliance.md:464]()
- **Open Policy Agent:** https://www.openpolicyagent.org/ [references/security-compliance.md:465]()
- **AWS Security Best Practices:** https://aws.amazon.com/security/best-practices/ [references/security-compliance.md:466]()

Sources: [references/security-compliance.md:460-467]()

---

## Integration with Skill System

The security-compliance.md file is one of five on-demand reference documents in the progressive disclosure architecture. It has an importance score of 0.70, indicating it is loaded less frequently than core patterns but provides essential security guidance when needed.

**Loading Triggers:**
- User queries about security scanning
- Questions about compliance frameworks
- Secrets management questions
- State file security concerns
- IAM policy guidance requests

**Related Pages:**
- [Progressive Disclosure Pattern](#3.2) - Architecture that loads this file on-demand
- [Core Skill Content](#4.1) - SKILL.md that references this document
- [CI/CD Workflows](#4.5) - Pipeline integration of security scanning tools

Sources: [references/security-compliance.md:1-6](), Architecture diagrams (Diagram 1, Diagram 2)

---

# Page: Development Guide

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CLAUDE.md](CLAUDE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)

</details>



This document provides comprehensive guidance for contributors developing and maintaining the terraform-skill codebase. It covers the unique development philosophy of "prompt engineering as infrastructure", content quality standards, the mandatory testing methodology, and the complete contribution workflow from initial changes through automated release.

For installation and usage information, see [Getting Started](#2). For details on the automation systems that validate and release changes, see [Automation Systems](#6).

---

## Overview

The terraform-skill repository is fundamentally different from traditional software projects. It contains **executable documentation** that Claude loads to provide Terraform/OpenTofu expertise. This creates unique development requirements where content changes must be validated through agent behavior testing rather than traditional unit tests.

**Development Context Diagram**

```mermaid
graph TB
    subgraph "Development_Artifacts"
        SKILL["SKILL.md<br/>Core skill content<br/>~524 lines, ~4.4K tokens"]
        REF["references/*.md<br/>6 reference files<br/>~4K lines, ~26K tokens"]
        CLAUDE_DOC["CLAUDE.md<br/>Contributor guide"]
        CONTRIB["CONTRIBUTING.md<br/>Contribution standards"]
    end
    
    subgraph "Quality_Gates"
        VALIDATE_YML[".github/workflows/validate.yml<br/>Automated validation"]
        PR_TEMPLATE[".github/PULL_REQUEST_TEMPLATE.md<br/>Testing checklist"]
    end
    
    subgraph "Release_Automation"
        RELEASE_YML[".github/workflows/automated-release.yml<br/>Version & release"]
        CHANGELOG["CHANGELOG.md<br/>Generated from commits"]
        MARKETPLACE[".claude-plugin/marketplace.json<br/>Version synchronization"]
    end
    
    subgraph "Testing_Framework"
        BASELINE["tests/baseline-scenarios.md<br/>Test scenarios"]
        RESULTS["tests/baseline-results/<br/>tests/compliance-results/<br/>Documented behavior"]
        RATIONAL["tests/rationalization-table.md<br/>Tracked issues"]
    end
    
    CLAUDE_DOC -->|"Guides development of"| SKILL
    CLAUDE_DOC -->|"Guides development of"| REF
    CONTRIB -->|"Enforces standards for"| SKILL
    
    SKILL -->|"Validated by"| VALIDATE_YML
    SKILL -->|"Tested using"| BASELINE
    BASELINE -->|"Documents behavior in"| RESULTS
    
    PR_TEMPLATE -->|"Requires evidence from"| RESULTS
    PR_TEMPLATE -->|"Checks for"| RATIONAL
    
    SKILL -->|"Released by"| RELEASE_YML
    RELEASE_YML -->|"Updates"| MARKETPLACE
    RELEASE_YML -->|"Generates"| CHANGELOG
```

**Sources:** [CLAUDE.md:1-346](), [CONTRIBUTING.md:1-384]()

---

## Development Philosophy

### Prompt Engineering as Infrastructure

The repository implements "prompt engineering as infrastructure" - version-controlled AI instructions that encode domain knowledge into Claude's context. This approach treats documentation as:

- **Executable artifacts**: Content directly affects Claude's behavior
- **Domain knowledge encoding**: Distills terraform-best-practices.com into reusable guidance
- **Meta-project**: Building instructions for an AI assistant rather than traditional software

**Sources:** [CLAUDE.md:7-14]()

### Content Philosophy

Content decisions follow a strict framework defining what belongs in the skill versus what should be excluded:

| Category | Include | Exclude |
|----------|---------|---------|
| **Patterns** | Terraform-specific idioms, version features | Generic programming advice |
| **Guidance** | Decision frameworks (when X vs Y) | Terraform syntax basics |
| **Examples** | ✅ DO vs ❌ DON'T side-by-side | Provider resource details (use MCP) |
| **Reference** | Quick reference tables, decision matrices | Obvious practices ("use version control") |
| **Format** | Scannable tables, headers, bullets | Long prose explanations |

**Key Principles:**

- **Imperative voice**: "Use underscores" not "You should consider underscores"
- **Scannable format**: Tables over paragraphs, visual hierarchy with ✅/❌
- **Version markers**: Always indicate version requirements (e.g., "Terraform 1.6+")
- **Concrete examples**: Real scenarios with inline comments explaining WHY

**Sources:** [CLAUDE.md:83-109](), [CLAUDE.md:125-159](), [CONTRIBUTING.md:193-242]()

### Progressive Disclosure Architecture

The skill uses a three-tier loading strategy to optimize token usage:

```mermaid
flowchart LR
    subgraph "Tier_1_Metadata"
        META["marketplace.json<br/>frontmatter<br/>~100 tokens"]
    end
    
    subgraph "Tier_2_Core"
        SKILL_MD["SKILL.md<br/>~4,400 tokens<br/>524 lines"]
    end
    
    subgraph "Tier_3_References"
        MOD_PAT["references/module-patterns.md<br/>~7,000 tokens"]
        QUICK["references/quick-reference.md<br/>~3,800 tokens"]
        CODE_PAT["references/code-patterns.md<br/>~5,100 tokens"]
        CICD["references/ci-cd-workflows.md<br/>~2,300 tokens"]
        SEC["references/security-compliance.md<br/>~2,500 tokens"]
        TEST["references/testing-frameworks.md<br/>~3,400 tokens"]
    end
    
    META -->|"Activates"| SKILL_MD
    SKILL_MD -.->|"On-demand"| MOD_PAT
    SKILL_MD -.->|"On-demand"| QUICK
    SKILL_MD -.->|"On-demand"| CODE_PAT
    SKILL_MD -.->|"On-demand"| CICD
    SKILL_MD -.->|"On-demand"| SEC
    SKILL_MD -.->|"On-demand"| TEST
    
    TOKEN_SAVE["Token Reduction:<br/>56-70% savings<br/>vs loading all content"]
    SKILL_MD -.-> TOKEN_SAVE
```

This architecture keeps `SKILL.md` under 500 lines (currently 524) while providing ~30.4K tokens of total content through progressive disclosure.

**Sources:** [CLAUDE.md:45-82](), [CLAUDE.md:313-327]()

---

## Content Standards

### File Organization Structure

```mermaid
graph TB
    subgraph "Root_Level"
        SKILL["SKILL.md<br/>Core skill<br/><500 lines target"]
        README["README.md<br/>End user docs"]
        CLAUDE["CLAUDE.md<br/>Contributor guide"]
        CONTRIB["CONTRIBUTING.md<br/>Standards & process"]
        LICENSE["LICENSE<br/>Apache 2.0"]
    end
    
    subgraph "references_Directory"
        TEST_FW["testing-frameworks.md<br/>~563 lines"]
        MOD_PAT["module-patterns.md<br/>~1,126 lines"]
        CICD_WF["ci-cd-workflows.md<br/>~473 lines"]
        SEC_COMP["security-compliance.md<br/>~470 lines"]
        QUICK_REF["quick-reference.md<br/>~600 lines"]
        CODE_PAT["code-patterns.md<br/>~859 lines"]
    end
    
    subgraph "tests_Directory"
        BASE_SCEN["baseline-scenarios.md<br/>Test scenarios"]
        BASE_RES["baseline-results/<br/>Behavior without changes"]
        COMP_RES["compliance-results/<br/>Behavior with changes"]
        RAT_TABLE["rationalization-table.md<br/>Tracked issues"]
    end
    
    subgraph "claude_plugin_Directory"
        MARKET["marketplace.json<br/>Plugin metadata"]
    end
    
    subgraph "github_workflows_Directory"
        AUTO_REL["automated-release.yml<br/>Release workflow"]
        VAL["validate.yml<br/>Validation workflow"]
    end
    
    subgraph "github_Root"
        PR_TEMP["PULL_REQUEST_TEMPLATE.md<br/>PR checklist"]
    end
    
    SKILL -->|"References"| TEST_FW
    SKILL -->|"References"| MOD_PAT
    SKILL -->|"References"| CICD_WF
    SKILL -->|"References"| SEC_COMP
    SKILL -->|"References"| QUICK_REF
    SKILL -->|"References"| CODE_PAT
    
    SKILL -->|"Tested with"| BASE_SCEN
    BASE_SCEN -->|"Documents"| BASE_RES
    BASE_SCEN -->|"Documents"| COMP_RES
    
    MARKET -->|"Defines"| SKILL
    AUTO_REL -->|"Updates"| MARKET
    VAL -->|"Validates"| SKILL
```

**Sources:** [CLAUDE.md:16-32](), [CONTRIBUTING.md:92-110]()

### Frontmatter Requirements

The `SKILL.md` frontmatter is strictly limited to two fields per official Claude skill standards:

```yaml
---
name: terraform-skill
description: Use when working with Terraform or OpenTofu - creating modules,
  writing tests...
---
```

**Critical Rules:**

| Field | Required | Format |
|-------|----------|--------|
| `name` | ✅ Yes | Letters, numbers, hyphens only |
| `description` | ✅ Yes | Start with "Use when..." and list triggers |
| `author` | ❌ No | Put in README.md instead |
| `version` | ❌ No | Managed by [.github/workflows/automated-release.yml]() |
| `license` | ❌ No | Put in README.md and LICENSE |

**Description Best Practices:**

The description must focus on **WHEN to use** (activation triggers), not **WHAT it does** (feature summary):

✅ **Good:** "Use when working with Terraform or OpenTofu - creating modules, writing tests (native test framework, Terratest), setting up CI/CD pipelines, reviewing configurations..."

❌ **Bad:** "Comprehensive skill for Terraform development covering testing, modules, CI/CD, and production patterns"

**Sources:** [CONTRIBUTING.md:34-78]()

### Token Efficiency Guidelines

**Target Metrics:**

| File | Line Limit | Token Budget | Current Status |
|------|------------|--------------|----------------|
| `SKILL.md` | <500 lines | ~4,400 tokens | 524 lines (justified) |
| Total core | <1,500 words | - | ~1,400 words |
| Reference files | No limit | ~26K tokens | 4,091 lines across 6 files |

**Optimization Techniques:**

1. **Progressive disclosure**: Move detailed content to [references/*.md]()
2. **Table compression**: Use tables instead of prose for comparisons
3. **Link sections**: Pipe-separated lists instead of verbose formatting
4. **Reference over repeat**: Link to other files instead of duplicating content

The current 524 lines in `SKILL.md` (24 lines over guideline) is justified by:
- Comprehensive decision matrices for testing strategy and `count` vs `for_each`
- Essential quick reference tables used in every session
- Version-specific guidance across multiple Terraform versions
- Progressive disclosure architecture minimizes actual token cost

**Sources:** [CONTRIBUTING.md:80-91](), [CLAUDE.md:65-82](), [CLAUDE.md:313-327]()

### Writing Style Requirements

**Code Example Standards:**

One excellent example beats many mediocre ones. Every code example must be:

- **Complete and runnable**: Not pseudo-code or fill-in-the-blank templates
- **Well-commented**: Explain WHY, not just what
- **Real scenario**: From actual use cases, not contrived
- **Pattern clarity**: Shows the pattern clearly for adaptation

**Formatting Standards:**

```mermaid
graph LR
    subgraph "Required_Elements"
        IMP["Imperative Voice<br/>'Use X' not<br/>'You should use X'"]
        SCAN["Scannable Format<br/>Tables, bullets<br/>✅/❌ markers"]
        VER["Version Markers<br/>'Terraform 1.6+'<br/>'OpenTofu 1.7+'"]
        CODE["Code Blocks<br/>Inline comments<br/>explaining WHY"]
    end
    
    subgraph "Pattern_Templates"
        DO_DONT["✅ DO vs ❌ DON'T<br/>Side-by-side examples"]
        TABLES["Decision Tables<br/>'Your Situation'<br/>'Recommended Approach'"]
        FRAMES["Decision Frameworks<br/>'When to use X vs Y'<br/>Tradeoffs clearly stated"]
    end
    
    IMP --> DO_DONT
    SCAN --> TABLES
    VER --> CODE
    CODE --> FRAMES
```

**Sources:** [CLAUDE.md:125-159](), [CONTRIBUTING.md:195-242]()

---

## Testing Methodology

### The Iron Law: No Changes Without Testing First

**Absolute Rule:** NO CHANGES WITHOUT TESTING FIRST

This applies to:
- ✅ New content additions
- ✅ Edits to existing content  
- ✅ Reorganization or refactoring
- ✅ "Simple" documentation updates

**No exceptions.**

**Sources:** [CONTRIBUTING.md:112-125]()

### TDD for Documentation

This project implements Test-Driven Development for documentation content. Per official Claude skill standards (writing-skills reference), the workflow follows red-green-refactor:

**Testing Workflow Diagram**

```mermaid
flowchart TD
    START["Identify Change Need"]
    
    subgraph "RED_Phase"
        SCEN["Identify Affected Scenarios<br/>from tests/baseline-scenarios.md"]
        DISABLE["Disable Skill<br/>mv ~/.claude/references/terraform-skill<br/>~/.claude/references/terraform-skill.disabled"]
        RUN_BASE["Run Scenario WITHOUT Changes"]
        DOC_BASE["Document Baseline Behavior<br/>in tests/baseline-results/"]
    end
    
    subgraph "GREEN_Phase"
        MAKE_CHANGE["Apply Changes<br/>to SKILL.md or references/"]
        ENABLE["Re-enable Skill<br/>mv terraform-skill.disabled terraform-skill"]
        RUN_COMP["Run Same Scenario WITH Changes"]
        DOC_COMP["Document Compliance Behavior<br/>in tests/compliance-results/"]
    end
    
    subgraph "REFACTOR_Phase"
        VERIFY["Compare Baseline vs Compliance<br/>Does agent follow guidance?<br/>Patterns applied proactively?"]
        RAT_CHECK["Check for Rationalizations<br/>Agent inventing excuses?"]
        RAT_DOC["Document in<br/>tests/rationalization-table.md"]
        RETEST["Close Loopholes<br/>Re-test Until Clean"]
    end
    
    START --> SCEN
    SCEN --> DISABLE
    DISABLE --> RUN_BASE
    RUN_BASE --> DOC_BASE
    
    DOC_BASE --> MAKE_CHANGE
    MAKE_CHANGE --> ENABLE
    ENABLE --> RUN_COMP
    RUN_COMP --> DOC_COMP
    
    DOC_COMP --> VERIFY
    VERIFY --> RAT_CHECK
    RAT_CHECK -->|"Issues Found"| RAT_DOC
    RAT_DOC --> RETEST
    RETEST --> VERIFY
    RAT_CHECK -->|"Clean"| DONE["Document in PR<br/>Submit for Review"]
```

**Sources:** [CONTRIBUTING.md:126-192]()

### Baseline vs Compliance Testing

**Testing Process:**

1. **Identify Scenarios**: Review [tests/baseline-scenarios.md]() for affected scenarios
2. **Run Baseline**: Execute scenarios WITHOUT changes, document agent behavior
3. **Apply Changes**: Make edits to `SKILL.md` or [references/*.md]()
4. **Run Compliance**: Execute same scenarios WITH changes
5. **Verify Improvement**: Compare baseline vs compliance behavior
6. **Document**: Include evidence in PR description

**Verification Criteria:**

| Check | Question | Required Evidence |
|-------|----------|-------------------|
| **Follows Guidance** | Does agent apply new patterns? | Compliance output shows pattern usage |
| **Proactive Application** | Agent suggests patterns unprompted? | Compliance shows unprompted recommendations |
| **No Rationalizations** | Agent inventing excuses for non-compliance? | None found or documented in [tests/rationalization-table.md]() |
| **Behavior Improvement** | Clear improvement over baseline? | Side-by-side comparison in PR |

**Testing Checklist for PRs:**

Every pull request must include:

- [ ] Identified affected scenarios from [tests/baseline-scenarios.md]()
- [ ] Ran baseline WITHOUT changes (documented in [tests/baseline-results/]())
- [ ] Applied changes to [SKILL.md]() or [references/*.md]()
- [ ] Ran compliance WITH changes (documented in [tests/compliance-results/]())
- [ ] Verified behavior improvement (evidence in PR description)
- [ ] No new rationalizations discovered (or documented in [tests/rationalization-table.md]())
- [ ] Re-tested if rationalizations found (closed loopholes)

**Sources:** [CONTRIBUTING.md:136-192]()

### Why Testing Matters

Without testing, content changes are unvalidated assumptions. Testing proves that:

1. Changes actually improve agent behavior (not just theory)
2. Patterns are applied correctly by Claude
3. No unintended behavior regressions introduced
4. Agent doesn't rationalize non-compliance

This is fundamentally different from traditional documentation because **the content directly controls an AI agent's behavior**. Changes that seem clear to humans may not translate to agent understanding.

**Sources:** [CONTRIBUTING.md:126-135]()

---

## Contribution Workflow

### Fork and Branch Strategy

**Initial Setup:**

```bash
# Fork repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/terraform-skill
cd terraform-skill

# Create feature branch
git checkout -b feature/improve-testing-guidance
```

**Branch Naming:**
- `feature/*` - New features or content
- `fix/*` - Bug fixes or corrections
- `docs/*` - Documentation improvements
- `refactor/*` - Reorganization without content changes

**Sources:** [CLAUDE.md:268-274](), [CONTRIBUTING.md:310-315]()

### Local Development and Testing

**Development Loop:**

```mermaid
flowchart LR
    subgraph "Edit_Phase"
        EDIT["Edit SKILL.md or<br/>references/*.md"]
        CHECK_SIZE["Check file size<br/>wc -c SKILL.md"]
    end
    
    subgraph "Local_Test_Phase"
        COPY["Copy to Claude Directory<br/>cp -r . ~/.claude/references/terraform-skill/"]
        RELOAD["Claude auto-reloads<br/>on file changes"]
        TEST_QUERY["Test with Real Queries<br/>'Create module with tests'<br/>'Review this config'"]
    end
    
    subgraph "Verify_Phase"
        VERIFY_SKILL["Verify Skill Referenced<br/>Check response patterns"]
        VERIFY_TOKEN["Check Token Count<br/>~17,700 chars ≈ 4,400 tokens"]
        VERIFY_NO_CONFLICT["No conflicts with<br/>existing guidance"]
    end
    
    EDIT --> CHECK_SIZE
    CHECK_SIZE --> COPY
    COPY --> RELOAD
    RELOAD --> TEST_QUERY
    
    TEST_QUERY --> VERIFY_SKILL
    VERIFY_SKILL --> VERIFY_TOKEN
    VERIFY_TOKEN --> VERIFY_NO_CONFLICT
    
    VERIFY_NO_CONFLICT -->|"Issues"| EDIT
    VERIFY_NO_CONFLICT -->|"Good"| DONE["Ready for PR"]
```

**Local Testing Commands:**

```bash
# Copy to Claude skills directory
cp -r . ~/.claude/references/terraform-skill/

# Claude Code auto-reloads on file changes
# Test with real queries in Claude Code interface

# Check token count
wc -c SKILL.md  # Currently ~17,700 chars ≈ 4,400 tokens
```

**Sources:** [CLAUDE.md:176-198](), [CLAUDE.md:282-287]()

### Conventional Commits for Automated Versioning

This project uses [Conventional Commits](https://www.conventionalcommits.org/) to drive automated versioning and changelog generation.

**Commit Format:**

```
<type>: <description>

[optional body]

[optional footer]
```

**Type Definitions:**

| Type | Version Bump | Use For | Example |
|------|--------------|---------|---------|
| `feat!:` or `BREAKING CHANGE:` | Major (1.x → 2.0) | Breaking changes | `feat!: remove deprecated test framework guidance` |
| `feat:` | Minor (1.2.x → 1.3.0) | New features | `feat: add OpenTofu 1.8 support` |
| `fix:` | Patch (1.2.3 → 1.2.4) | Bug fixes | `fix: correct module output syntax` |
| `docs:` | Patch | Documentation only | `docs: improve testing strategy docs` |
| `chore:` | Patch | Maintenance, tooling | `chore: update workflow dependencies` |
| `test:` | Patch | Test improvements | `test: add security scanning scenarios` |
| `refactor:` | Patch | Code refactoring | `refactor: reorganize reference files` |

**Conventional Commit Examples:**

```bash
# Feature (minor version bump)
git commit -m "feat: add OpenTofu 1.8 support"

# Bug fix (patch version bump)
git commit -m "fix: correct module output syntax in examples"

# Breaking change (major version bump)
git commit -m "feat!: remove deprecated test framework guidance"

# With detailed description
git commit -m "feat: add native testing examples

- Add examples for Terraform 1.6+ native tests
- Include decision matrix for test framework selection
- Document best practices for test organization"

# Documentation only
git commit -m "docs: improve testing strategy documentation"
```

**Sources:** [CONTRIBUTING.md:243-308]()

### Automated Version Synchronization

**Conventional commits enable:**

```mermaid
flowchart TD
    subgraph "Commit_Analysis"
        COMMITS["Conventional Commits<br/>feat:/fix:/docs:<br/>Since Last Release"]
        ANALYZE["automated-release.yml<br/>Analyzes Commit Types"]
        CALC_VER["Calculate Version Bump<br/>Major/Minor/Patch"]
    end
    
    subgraph "Version_Sync"
        UPDATE_MARKET["Update marketplace.json<br/>marketplace.version<br/>marketplace.plugins[0].version<br/>marketplace.plugins[0].git.ref"]
        UPDATE_SKILL["Update SKILL.md<br/>Frontmatter metadata"]
        GEN_CHANGE["Generate CHANGELOG.md<br/>Grouped by type"]
    end
    
    subgraph "Release_Creation"
        CREATE_TAG["Create Git Tag<br/>v{version}"]
        CREATE_REL["Create GitHub Release<br/>With changelog body"]
        PUBLISH["Publish to<br/>Claude Marketplace"]
    end
    
    COMMITS --> ANALYZE
    ANALYZE --> CALC_VER
    
    CALC_VER --> UPDATE_MARKET
    CALC_VER --> UPDATE_SKILL
    CALC_VER --> GEN_CHANGE
    
    UPDATE_MARKET --> CREATE_TAG
    UPDATE_SKILL --> CREATE_TAG
    GEN_CHANGE --> CREATE_TAG
    
    CREATE_TAG --> CREATE_REL
    CREATE_REL --> PUBLISH
```

Contributors don't manage versions manually. The [.github/workflows/automated-release.yml]() workflow:

1. Analyzes commits since last release
2. Determines version bump from commit types
3. Updates version in three locations:
   - [.claude-plugin/marketplace.json]() (marketplace, plugin, git ref)
   - [SKILL.md]() (frontmatter metadata if present)
   - Git tag
4. Generates [CHANGELOG.md]() from commit messages
5. Creates GitHub Release with changelog

**Sources:** [CONTRIBUTING.md:293-362]()

### Pull Request Process

**PR Submission Flow:**

```mermaid
flowchart TD
    START["Create PR from<br/>feature branch"]
    
    subgraph "PR_Template_Requirements"
        TEMPLATE[".github/PULL_REQUEST_TEMPLATE.md"]
        DESC["Change Description<br/>What changed and why"]
        TEST_EVID["Testing Evidence<br/>Baseline vs Compliance"]
        CHECKLIST["Standards Checklist<br/>Frontmatter, token efficiency"]
    end
    
    subgraph "Automated_Validation"
        VALIDATE["validate.yml Workflow"]
        FRONT_CHECK["Frontmatter Validation<br/>name, description fields"]
        SIZE_CHECK["File Size Check<br/>SKILL.md < 500 lines warning"]
        LINK_CHECK["Broken Link Detection"]
        LINT_CHECK["Markdown Linting"]
    end
    
    subgraph "Maintainer_Review"
        REV_STANDARD["Standards Compliance<br/>Frontmatter, description format"]
        REV_TEST["Testing Evidence<br/>Baseline/compliance documented"]
        REV_TOKEN["Token Efficiency<br/>Not adding unnecessary content"]
        REV_ACCURACY["Accuracy<br/>Technically correct and current"]
        REV_QUALITY["Quality<br/>Clear, scannable, organized"]
    end
    
    START --> TEMPLATE
    TEMPLATE --> DESC
    TEMPLATE --> TEST_EVID
    TEMPLATE --> CHECKLIST
    
    DESC --> VALIDATE
    VALIDATE --> FRONT_CHECK
    VALIDATE --> SIZE_CHECK
    VALIDATE --> LINK_CHECK
    VALIDATE --> LINT_CHECK
    
    FRONT_CHECK --> REV_STANDARD
    SIZE_CHECK --> REV_TOKEN
    LINK_CHECK --> REV_ACCURACY
    LINT_CHECK --> REV_QUALITY
    TEST_EVID --> REV_TEST
    
    REV_STANDARD --> APPROVE{Approve?}
    REV_TEST --> APPROVE
    REV_TOKEN --> APPROVE
    REV_ACCURACY --> APPROVE
    REV_QUALITY --> APPROVE
    
    APPROVE -->|"Yes"| MERGE["Merge to master<br/>Triggers automated-release.yml"]
    APPROVE -->|"No"| CHANGES["Request Changes<br/>Return to editing"]
```

**Review Criteria:**

| Criterion | Validation | Required Evidence |
|-----------|------------|-------------------|
| **Standards Compliance** | [.github/workflows/validate.yml]() | Frontmatter correct, description format proper |
| **Testing Evidence** | Manual review | Baseline vs compliance documented in PR |
| **Token Efficiency** | Manual review | Changes don't add unnecessary content |
| **Technical Accuracy** | Manual review | Content is correct and current |
| **Content Quality** | Manual review | Clear, scannable, well-organized |

**Sources:** [CONTRIBUTING.md:309-362](), [.github/PULL_REQUEST_TEMPLATE.md]()

### Complete Contribution Lifecycle

**End-to-End Workflow:**

```mermaid
flowchart TD
    subgraph "Development"
        IDENTIFY["Identify Improvement Need<br/>New feature, bug fix, clarification"]
        FORK["Fork & Branch<br/>git checkout -b feature/xyz"]
        BASELINE["Test Baseline Behavior<br/>Disable skill, run scenarios"]
        EDIT["Make Changes<br/>SKILL.md or references/"]
        LOCAL_TEST["Test Locally<br/>Copy to ~/.claude/references/"]
        COMPLIANCE["Test Compliance<br/>Enable skill, verify improvement"]
    end
    
    subgraph "Submission"
        COMMIT["Commit with Conventional Format<br/>feat:/fix:/docs:"]
        PUSH["Push to Fork<br/>git push origin feature/xyz"]
        CREATE_PR["Create PR with Evidence<br/>Use PR template"]
    end
    
    subgraph "Validation"
        AUTO_VAL["Automated Validation<br/>validate.yml runs"]
        MANUAL_REV["Maintainer Review<br/>Standards + testing evidence"]
    end
    
    subgraph "Release"
        MERGE["Merge to master"]
        AUTO_REL["Automated Release<br/>automated-release.yml runs"]
        VER_SYNC["Version Synchronization<br/>marketplace.json, SKILL.md, tag"]
        GEN_LOG["Generate CHANGELOG.md<br/>From commit messages"]
        PUB["Publish Release<br/>GitHub + Marketplace"]
    end
    
    IDENTIFY --> FORK
    FORK --> BASELINE
    BASELINE --> EDIT
    EDIT --> LOCAL_TEST
    LOCAL_TEST --> COMPLIANCE
    
    COMPLIANCE --> COMMIT
    COMMIT --> PUSH
    PUSH --> CREATE_PR
    
    CREATE_PR --> AUTO_VAL
    AUTO_VAL --> MANUAL_REV
    
    MANUAL_REV -->|"Approved"| MERGE
    MANUAL_REV -->|"Changes Requested"| EDIT
    
    MERGE --> AUTO_REL
    AUTO_REL --> VER_SYNC
    VER_SYNC --> GEN_LOG
    GEN_LOG --> PUB
```

**Timeline:**

1. **Development**: Local testing and iteration (1-2 hours to days depending on scope)
2. **Submission**: Create PR with complete testing evidence (15-30 minutes)
3. **Validation**: Automated checks run immediately, manual review within 1-3 days
4. **Release**: Fully automated on merge, completes in ~2 minutes

**Sources:** [CLAUDE.md:160-310](), [CONTRIBUTING.md:1-384]()

---

## Quality Standards Checklist

Before submitting a pull request, verify all standards are met:

### Content Quality

- [ ] Decision frameworks are clear and actionable
- [ ] Examples are accurate and tested in real scenarios
- [ ] No outdated information (verify current Terraform/OpenTofu versions)
- [ ] Version-specific guidance clearly marked (e.g., "Terraform 1.6+")
- [ ] Common pitfalls documented with explanations
- [ ] ✅ DO vs ❌ DON'T examples for non-obvious patterns

### Technical Quality

- [ ] Code examples are syntactically correct
- [ ] Commands follow current best practices
- [ ] Links to official documentation work
- [ ] Tools referenced are current (not deprecated)
- [ ] No breaking changes without justification

### Testing Quality

- [ ] Baseline behavior documented in [tests/baseline-results/]()
- [ ] Compliance behavior documented in [tests/compliance-results/]()
- [ ] Evidence of improvement included in PR description
- [ ] No rationalizations discovered (or tracked in [tests/rationalization-table.md]())
- [ ] Re-tested if loopholes closed

### Usability

- [ ] Clear activation triggers in description
- [ ] Quick reference sections are scannable
- [ ] Logical organization maintained
- [ ] Consistent markdown formatting
- [ ] Headers provide clear navigation

### Legal

- [ ] License clearly stated (Apache 2.0)
- [ ] Sources attributed where applicable
- [ ] Copyright notice current
- [ ] No copyrighted content without permission

**Sources:** [CLAUDE.md:233-264](), [CONTRIBUTING.md:181-192](), [CONTRIBUTING.md:338-346]()

---

## When to Update vs When Not to Update

**Update the skill when:**

| Condition | Example | Action |
|-----------|---------|--------|
| **Major/minor version features** | Terraform 1.10 adds new testing syntax | Add version-specific guidance |
| **Community consensus emerges** | New module pattern becomes standard | Document pattern with decision framework |
| **Real-world gaps discovered** | Users consistently hit undocumented issue | Add troubleshooting guidance |
| **Anti-patterns identified** | Common mistake causing problems | Add ❌ DON'T example with explanation |

**Don't update for:**

| Condition | Reason | Alternative |
|-----------|--------|-------------|
| **Provider resource changes** | Use Terraform MCP tools for registry docs | Reference MCP tool in skill |
| **Patch versions without features** | No behavioral changes to document | Wait for feature releases |
| **Personal preferences** | Not community consensus | Discuss in GitHub Discussions first |
| **Duplicate Claude knowledge** | Claude already knows generic concepts | Focus on Terraform-specific content |

**Sources:** [CLAUDE.md:200-212]()

---

## Development Environment Setup

**Prerequisites:**

- Git installed and configured
- GitHub account with fork of [antonbabenko/terraform-skill]()
- Claude Code installed with skills support
- Text editor (VS Code, vim, etc.)
- Basic familiarity with Terraform/OpenTofu

**Setup Steps:**

```bash
# 1. Fork repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/terraform-skill
cd terraform-skill

# 3. Link to upstream for updates
git remote add upstream https://github.com/antonbabenko/terraform-skill

# 4. Create development directory in Claude
mkdir -p ~/.claude/references/terraform-skill

# 5. Link or copy for testing
ln -s $(pwd) ~/.claude/references/terraform-skill-dev
# OR
cp -r . ~/.claude/references/terraform-skill/

# 6. Create feature branch
git checkout -b feature/your-improvement
```

**Testing Setup:**

- Claude Code will auto-reload skills on file changes
- Test queries: "Create Terraform module with tests", "Review this config"
- Observe if Claude references the skill in responses
- Verify patterns are applied correctly

**Sources:** [CLAUDE.md:176-198](), [CLAUDE.md:282-287]()

---

## Additional Resources

**For Contributors:**
- [CLAUDE.md]() - Detailed development guidelines and architecture decisions
- [CONTRIBUTING.md]() - Contribution standards and process
- [tests/baseline-scenarios.md]() - Testing scenarios for validation
- [.github/PULL_REQUEST_TEMPLATE.md]() - PR checklist and requirements

**External Standards:**
- [Claude Code Skills Documentation](https://docs.claude.ai/docs/agent-skills)
- writing-skills (reference skill for skill development)
- [Conventional Commits Specification](https://www.conventionalcommits.org/)

**Community:**
- [GitHub Issues](https://github.com/antonbabenko/terraform-skill/issues) - Bug reports and feature requests
- [GitHub Discussions](https://github.com/antonbabenko/terraform-skill/discussions) - Questions and discussions
- Maintainer: [@antonbabenko](https://github.com/antonbabenko)

**Sources:** [CLAUDE.md:337-341](), [CONTRIBUTING.md:363-378]()

---

# Page: Development Philosophy

# Development Philosophy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CLAUDE.md](CLAUDE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)

</details>



## Purpose and Scope

This page explains the foundational philosophy behind developing terraform-skill, focusing on how prompt engineering principles guide architecture decisions, content organization, and development practices. For specific content requirements and standards, see [Content Standards](#5.2). For testing procedures, see [Testing Methodology](#5.3). For the contribution process, see [Contribution Workflow](#5.4).

## Core Concept: Prompt Engineering as Infrastructure

The terraform-skill repository embodies a paradigm shift from traditional software development to **executable documentation**. This is not a software library or framework—it is version-controlled AI instructions that shape how Claude understands and applies Terraform/OpenTofu best practices.

### The Meta-Project Nature

```mermaid
graph TB
    subgraph "Traditional Software Development"
        CODE["Source Code"]
        BUILD["Build Artifacts"]
        TESTS["Automated Tests"]
        USERS["End Users"]
        CODE --> BUILD
        BUILD --> TESTS
        TESTS --> USERS
    end
    
    subgraph "Skill Development"
        CONTENT["SKILL.md<br/>Content"]
        CLAUDE["Claude AI Agent"]
        BEHAVIOR["Agent Behavior"]
        DEVS["Terraform Developers"]
        CONTENT --> CLAUDE
        CLAUDE --> BEHAVIOR
        BEHAVIOR --> DEVS
    end
    
    FEEDBACK["Manual Testing<br/>& Observation"]
    BEHAVIOR --> FEEDBACK
    FEEDBACK --> CONTENT
    
    style CONTENT fill:#fff
    style BEHAVIOR fill:#fff
```

**Sources:** [CLAUDE.md:7-14](), [CLAUDE.md:162-174]()

As stated in [CLAUDE.md:9-13](), this represents three key concepts:

- **Prompt engineering as infrastructure**: Version-controlled AI instructions that persist across sessions
- **Domain knowledge artifact**: Encoding terraform-best-practices.com expertise into Claude's context window
- **Meta-project**: Building instructions for an AI assistant, not building software itself

This fundamental distinction drives every architectural and content decision.

### What This Means in Practice

| Traditional Software | Terraform Skill |
|---------------------|-----------------|
| Write code → Compile → Test | Write content → Load in Claude → Observe behavior |
| Unit tests verify behavior | Manual scenarios verify Claude's responses |
| Build artifacts are deployed | Content is loaded into context window |
| Users call functions | Claude reads and applies patterns |
| Versioning based on API compatibility | Versioning based on Terraform feature support |

The development workflow reflects this [CLAUDE.md:162-174]():

1. Update `SKILL.md` or reference files
2. Load in Claude Code (reload skills)
3. Test on real Terraform projects
4. Observe if Claude applies patterns correctly
5. Iterate based on results

**Sources:** [CLAUDE.md:162-174](), [CONTRIBUTING.md:115-125]()

## Token Efficiency as First Principle

Token efficiency is not a performance optimization—it is the **fundamental constraint** that drives the entire architecture. Every design decision flows from the need to maximize expertise delivery within Claude's context window limits.

### Token Budget Architecture

```mermaid
graph LR
    subgraph "Always Loaded"
        FRONT["Frontmatter<br/>~100 tokens"]
    end
    
    subgraph "Core Content"
        SKILL["SKILL.md<br/>~4,400 tokens"]
    end
    
    subgraph "On-Demand References"
        MOD["module-patterns.md<br/>~7,000 tokens"]
        QUICK["quick-reference.md<br/>~3,800 tokens"]
        CODE["code-patterns.md<br/>~5,100 tokens"]
        CI["ci-cd-workflows.md<br/>~2,300 tokens"]
        SEC["security-compliance.md<br/>~2,500 tokens"]
        TEST["testing-frameworks.md<br/>~3,400 tokens"]
    end
    
    FRONT --> SKILL
    SKILL -.->|"Complex module<br/>questions"| MOD
    SKILL -.->|"Command<br/>lookup"| QUICK
    SKILL -.->|"Version-specific<br/>features"| CODE
    SKILL -.->|"Pipeline<br/>setup"| CI
    SKILL -.->|"Security<br/>scanning"| SEC
    SKILL -.->|"Testing<br/>approach"| TEST
    
    SAVINGS["56-70% Token Reduction<br/>vs loading all content"]
    SKILL -.-> SAVINGS
```

**Token Budget Breakdown** from [CLAUDE.md:65-81]():

| Content Layer | Token Count | Loading Strategy |
|--------------|-------------|------------------|
| Frontmatter (YAML) | ~100 tokens | Always loaded (activation trigger) |
| SKILL.md core | ~4,400 tokens | Loaded when skill activates |
| module-patterns.md | ~7,000 tokens | On-demand only |
| quick-reference.md | ~3,800 tokens | On-demand only |
| code-patterns.md | ~5,100 tokens | On-demand only |
| ci-cd-workflows.md | ~2,300 tokens | On-demand only |
| security-compliance.md | ~2,500 tokens | On-demand only |
| testing-frameworks.md | ~3,400 tokens | On-demand only |
| **Total Available** | ~30,400 tokens | Progressive disclosure |
| **Typical Query** | 4,500-12,000 tokens | 56-70% savings |

**Sources:** [CLAUDE.md:65-81]()

### The 500-Line Guideline

The target of keeping `SKILL.md` under 500 lines [CLAUDE.md:76]() is not arbitrary—it represents a balance point where:

- Core decision frameworks remain comprehensive
- Quick reference tables stay accessible
- Version-specific guidance is included
- Progressive disclosure remains effective

The current implementation at 524 lines [CLAUDE.md:319-325]() is justified because the extra 24 lines provide:
- Comprehensive testing decision matrices
- Essential quick reference tables
- Multi-version Terraform support

As noted in [CLAUDE.md:324-325](): "Future updates should prioritize reference file expansion over core skill growth."

**Sources:** [CLAUDE.md:76](), [CLAUDE.md:319-328]()

## Progressive Disclosure Architecture

Progressive disclosure is the architectural pattern that makes token efficiency practical. Content is organized in layers of increasing detail, loaded only when Claude needs it.

### Three-Tier Content Architecture

```mermaid
graph TB
    subgraph "Tier 1: Discovery Layer"
        META["marketplace.json<br/>Activation triggers<br/>keywords, description"]
    end
    
    subgraph "Tier 2: Core Guidance Layer"
        PRINCIPLES["Core Principles<br/>Naming, structure"]
        TESTING["Testing Strategy<br/>Decision matrix"]
        MODULES["Module Development<br/>Best practices"]
        PATTERNS["Common Patterns<br/>DO/DON'T examples"]
        CICD["CI/CD Integration<br/>Workflow automation"]
        QUICK["Quick Reference<br/>Tables and matrices"]
    end
    
    subgraph "Tier 3: Deep Reference Layer"
        REF_TEST["testing-frameworks.md<br/>Detailed testing guides"]
        REF_MOD["module-patterns.md<br/>Module architecture"]
        REF_CODE["code-patterns.md<br/>Modern Terraform features"]
        REF_QUICK["quick-reference.md<br/>Command cheat sheets"]
        REF_CI["ci-cd-workflows.md<br/>Pipeline templates"]
        REF_SEC["security-compliance.md<br/>Security hardening"]
    end
    
    QUERY["User Query"]
    QUERY --> META
    META -->|"Skill<br/>activates"| PRINCIPLES
    META -->|"Skill<br/>activates"| TESTING
    META -->|"Skill<br/>activates"| MODULES
    META -->|"Skill<br/>activates"| PATTERNS
    META -->|"Skill<br/>activates"| CICD
    META -->|"Skill<br/>activates"| QUICK
    
    TESTING -.->|"Deep dive<br/>needed"| REF_TEST
    MODULES -.->|"Complex<br/>patterns"| REF_MOD
    PATTERNS -.->|"Version<br/>features"| REF_CODE
    QUICK -.->|"Command<br/>details"| REF_QUICK
    CICD -.->|"Pipeline<br/>templates"| REF_CI
    PATTERNS -.->|"Security<br/>scanning"| REF_SEC
```

**Sources:** [CLAUDE.md:45-63](), [CLAUDE.md:111-123]()

### Content Distribution Strategy

The organization in [CLAUDE.md:111-123]() defines clear boundaries for each tier:

**Tier 1 - Always Loaded:**
- Activation triggers define when Claude should use this skill
- Keywords enable skill discovery
- ~100 tokens, negligible cost

**Tier 2 - Core SKILL.md (Loaded on Activation):**
- Testing Strategy Framework - decision matrices for choosing approaches
- Module Development - essential patterns and structure
- Common Patterns - ✅ DO vs ❌ DON'T side-by-side examples
- CI/CD Integration - workflow automation overview
- Quick Reference - rapid consultation tables

**Tier 3 - References Directory (Loaded on Demand):**
- Deep-dive content for specific topics
- Detailed examples and templates
- Version-specific feature documentation
- Tool-specific integration guides

**Sources:** [CLAUDE.md:111-123]()

## Content Philosophy: What Belongs Where

The content philosophy directly implements token efficiency through strict inclusion criteria. Not all Terraform knowledge belongs in this skill.

### Inclusion Criteria

```mermaid
graph TD
    KNOWLEDGE["Terraform/OpenTofu<br/>Knowledge"]
    
    INCLUDE_CHECK{"Is it<br/>Terraform-specific?"}
    DECISION_CHECK{"Does it require<br/>a decision?"}
    VERSION_CHECK{"Is it version-specific<br/>guidance?"}
    PATTERN_CHECK{"Is it a<br/>common pattern?"}
    
    GENERIC["Generic programming<br/>advice"]
    SYNTAX["Basic Terraform<br/>syntax"]
    PROVIDER["Provider-specific<br/>resource details"]
    OBVIOUS["Obvious practices"]
    
    INCLUDE["✅ Include in<br/>SKILL.md or references/"]
    EXCLUDE["❌ Exclude<br/>covered elsewhere"]
    
    KNOWLEDGE --> INCLUDE_CHECK
    
    INCLUDE_CHECK -->|"No"| GENERIC
    INCLUDE_CHECK -->|"Yes"| DECISION_CHECK
    
    DECISION_CHECK -->|"Yes"| INCLUDE
    DECISION_CHECK -->|"No"| VERSION_CHECK
    
    VERSION_CHECK -->|"Yes"| INCLUDE
    VERSION_CHECK -->|"No"| PATTERN_CHECK
    
    PATTERN_CHECK -->|"Yes"| INCLUDE
    PATTERN_CHECK -->|"No"| SYNTAX
    
    GENERIC --> EXCLUDE
    SYNTAX --> EXCLUDE
    PROVIDER --> EXCLUDE
    OBVIOUS --> EXCLUDE
```

**Sources:** [CLAUDE.md:86-109]()

### What Belongs in SKILL.md

From [CLAUDE.md:86-100](), content must meet these criteria:

**✅ Include:**
- Terraform-specific patterns and idioms (not generic programming advice)
- Decision frameworks (when to use X vs Y, with clear criteria)
- Version-specific features (Terraform 1.6+, 1.9+, etc. with markers)
- Testing strategy workflows (framework selection matrices)
- ✅ DO vs ❌ DON'T examples (for non-obvious patterns)
- Quick reference tables and decision matrices (scannable format)

**Format Requirements:**
- Scannable format (tables, headers, visual hierarchy)
- Imperative voice ("Use X", not "You should consider X")
- Concrete examples with inline comments explaining WHY
- Version requirements clearly marked (e.g., "Terraform 1.6+")

### What Doesn't Belong

From [CLAUDE.md:101-109](), these are explicitly excluded:

**❌ Exclude:**
- Generic programming advice (covered by Claude's base knowledge)
- Terraform syntax basics (covered in official documentation)
- Provider-specific resource details (use MCP tools for registry docs)
- Obvious practices (e.g., "use version control")
- Long prose explanations (use tables instead for scannability)

**Sources:** [CLAUDE.md:86-109]()

### File Organization Mapping

```mermaid
graph TB
    subgraph "Core Decision Frameworks → SKILL.md"
        CORE_TEST["Testing Strategy<br/>Framework selection matrix"]
        CORE_MODULE["Module Development<br/>Structure & naming"]
        CORE_PATTERN["Common Patterns<br/>DO/DON'T examples"]
    end
    
    subgraph "Detailed Guidance → references/"
        REF_TEST["testing-frameworks.md<br/>Tool setup & examples"]
        REF_MOD["module-patterns.md<br/>Architecture patterns"]
        REF_CODE["code-patterns.md<br/>Terraform 1.0+ features"]
    end
    
    subgraph "Quick Lookup → references/"
        REF_QUICK["quick-reference.md<br/>Command cheat sheets"]
        REF_CI["ci-cd-workflows.md<br/>Pipeline templates"]
        REF_SEC["security-compliance.md<br/>Security checklists"]
    end
    
    CORE_TEST -.->|"Deep dive"| REF_TEST
    CORE_MODULE -.->|"Architecture"| REF_MOD
    CORE_PATTERN -.->|"Modern features"| REF_CODE
    
    CORE_PATTERN -.->|"Commands"| REF_QUICK
    CORE_PATTERN -.->|"Automation"| REF_CI
    CORE_PATTERN -.->|"Security"| REF_SEC
```

**Sources:** [CLAUDE.md:16-43](), [CONTRIBUTING.md:92-110]()

## Development Mindset Shift

Developing a Claude skill requires abandoning traditional software development mental models and adopting a documentation-centric, observation-based approach.

### Traditional Software vs Skill Development

| Aspect | Traditional Software | Skill Development |
|--------|---------------------|-------------------|
| **Artifact Type** | Executable code | Instructional content |
| **Quality Assurance** | Automated unit tests | Manual behavioral observation |
| **Validation** | Test suite passes | Claude applies patterns correctly |
| **Deployment** | Build → Deploy pipeline | Load into context window |
| **Versioning** | Semantic versioning based on API | Semantic versioning based on content |
| **Dependencies** | Code libraries | Terraform/OpenTofu version features |
| **Failure Mode** | Runtime errors, exceptions | Claude misunderstands or ignores guidance |
| **Debugging** | Stack traces, logs | Re-test scenarios, observe responses |
| **Performance** | Execution speed, memory | Token efficiency, context window usage |

**Sources:** [CLAUDE.md:162-174]()

### The Testing-First Philosophy

From [CONTRIBUTING.md:115-125](), the development philosophy enforces an "Iron Law":

**NO CHANGES WITHOUT TESTING FIRST**

This applies to all changes:
- ✅ New content additions
- ✅ Edits to existing content
- ✅ Reorganization or refactoring
- ✅ "Simple" documentation updates

This is **TDD for documentation** [CONTRIBUTING.md:128-133]():

1. **RED:** Run scenarios WITHOUT your changes (document baseline behavior)
2. **GREEN:** Add changes, verify behavior improves (document compliance behavior)
3. **REFACTOR:** Close loopholes, re-test if rationalizations found

For detailed testing procedures, see [Testing Methodology](#5.3).

**Sources:** [CONTRIBUTING.md:115-133]()

### Observation-Based Validation

```mermaid
graph LR
    subgraph "Traditional Software Validation"
        TRAD_CODE["Write Code"]
        TRAD_TEST["Write Tests"]
        TRAD_RUN["Run Tests"]
        TRAD_PASS{"All Pass?"}
        TRAD_DEPLOY["Deploy"]
        
        TRAD_CODE --> TRAD_TEST
        TRAD_TEST --> TRAD_RUN
        TRAD_RUN --> TRAD_PASS
        TRAD_PASS -->|"Yes"| TRAD_DEPLOY
        TRAD_PASS -->|"No"| TRAD_CODE
    end
    
    subgraph "Skill Development Validation"
        SKILL_EDIT["Edit SKILL.md"]
        SKILL_LOAD["Load in Claude"]
        SKILL_QUERY["Test with Queries"]
        SKILL_OBS["Observe Behavior"]
        SKILL_EVAL{"Improved?"}
        SKILL_MERGE["Merge to Master"]
        
        SKILL_EDIT --> SKILL_LOAD
        SKILL_LOAD --> SKILL_QUERY
        SKILL_QUERY --> SKILL_OBS
        SKILL_OBS --> SKILL_EVAL
        SKILL_EVAL -->|"Yes"| SKILL_MERGE
        SKILL_EVAL -->|"No"| SKILL_EDIT
    end
```

From [CLAUDE.md:178-194](), the validation workflow is:

1. **Load the updated skill** (Claude Code auto-reloads on file changes)
2. **Test with real queries** (e.g., "Create a Terraform module with tests")
3. **Verify Claude references the skill** (check if new patterns appear in responses)
4. **Check token count** (`wc -c SKILL.md` should be ~17,700 chars ≈ 4,400 tokens)

**Sources:** [CLAUDE.md:178-198](), [CONTRIBUTING.md:162-175]()

## Update Triggers and Evolution

The philosophy for when to update the skill reflects its nature as a knowledge artifact that must stay current with ecosystem changes.

### When to Update

From [CLAUDE.md:200-211](), update triggers are strictly defined:

**✅ Update the skill when:**
- New Terraform/OpenTofu major or minor versions introduce features
- Community consensus emerges on patterns (documented in terraform-best-practices.com)
- Real-world usage reveals gaps or ambiguities in guidance
- Anti-patterns discovered that should be warned against

**❌ Don't update for:**
- Provider-specific resource changes (use Terraform MCP tools instead)
- Minor version patches without feature changes
- Personal preferences without community consensus

This ensures the skill remains authoritative while avoiding opinion-based content.

**Sources:** [CLAUDE.md:200-211](), [CONTRIBUTING.md:14-30]()

### Maintaining Balance

From [CLAUDE.md:313-328](), the evolution strategy balances competing concerns:

**Tension Areas:**
- **Completeness** vs **Token efficiency** (more content vs context window limits)
- **Detail** vs **Scannability** (comprehensive vs quickly readable)
- **Examples** vs **Reference** (concrete vs concise)

**Current Sweet Spot:**
- `SKILL.md`: 524 lines, ~4.4K tokens (comprehensive core guidance)
- Reference files: 6 files, ~26K tokens (deep-dive content)
- Progressive disclosure: 56-70% token reduction vs loading all content
- Total coverage: ~30.4K tokens structured for progressive loading

**Long-term Vision** [CLAUDE.md:329-335]():
- Stay current with Terraform/OpenTofu releases
- Remain the definitive Claude resource for Terraform
- Evolve with community consensus
- Maintain production-grade quality standards

**Sources:** [CLAUDE.md:313-335]()

## Integration with MCP Tools

The skill philosophy explicitly defines complementary boundaries with Terraform MCP (Model Context Protocol) tools, avoiding duplication while enabling synergy.

### Division of Responsibilities

From [CLAUDE.md:213-225]():

| Capability | Skill | MCP Tools |
|------------|-------|-----------|
| Best practices | ✅ | ❌ |
| Code patterns | ✅ | ❌ |
| Testing workflows | ✅ | ❌ |
| Latest versions | ❌ | ✅ |
| Registry documentation | ❌ | ✅ |
| Module search | ❌ | ✅ |

**Together they enable** [CLAUDE.md:226-230]():
- Code generation following best practices (skill provides patterns)
- Up-to-date version constraints (MCP provides current data)
- Framework selection guidance (skill provides decision matrices)
- Proactive anti-pattern detection (skill provides warnings)

This philosophical separation keeps the skill focused on **timeless principles and patterns** while MCP tools handle **current data and registry lookups**.

**Sources:** [CLAUDE.md:213-230]()

## Summary

The development philosophy for terraform-skill fundamentally rests on these principles:

1. **Prompt Engineering as Infrastructure** - Version-controlled AI instructions, not traditional software
2. **Token Efficiency First** - Every architectural decision flows from context window constraints
3. **Progressive Disclosure** - Three-tier content architecture (metadata → core → references)
4. **Strict Inclusion Criteria** - Only Terraform-specific patterns and decision frameworks
5. **Testing-First Mindset** - No changes without baseline vs compliance evidence
6. **Observation-Based Validation** - Manual testing with real queries replaces automated tests
7. **Ecosystem Awareness** - Clear boundaries with MCP tools to avoid duplication

These principles guide all specific standards, testing methodologies, and contribution workflows detailed in subsequent sections.

**Sources:** [CLAUDE.md:1-346](), [CONTRIBUTING.md:1-384]()

---

# Page: Content Standards

# Content Standards

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/validate.yml](.github/workflows/validate.yml)
- [CONTRIBUTING.md](CONTRIBUTING.md)

</details>



## Purpose and Scope

This document defines the technical standards for all content in the terraform-skill repository. These standards ensure that skill content is Claude-compatible, token-efficient, and maintains consistent quality. This page covers frontmatter requirements, description format, writing style, code examples, and automated validation rules.

For broader principles behind these standards, see [Development Philosophy](#5.1). For testing requirements before submitting changes, see [Testing Methodology](#5.3). For the step-by-step PR process, see [Contribution Workflow](#5.4).

---

## Frontmatter Requirements

### Required Fields

The `SKILL.md` frontmatter MUST contain exactly two fields. Additional fields are prohibited and will cause validation failures.

**Required Structure:**

```yaml
---
name: terraform-skill
description: Use when working with Terraform or OpenTofu - creating modules,
  writing tests...
---
```

| Field | Format | Validation | Max Length |
|-------|--------|------------|------------|
| `name` | `[a-zA-Z0-9-]+` | Regex pattern match | N/A |
| `description` | Plain text | Must start with "Use when..." | 1024 characters |

**Sources:** [CONTRIBUTING.md:34-56](), [.github/workflows/validate.yml:34-92]()

### Prohibited Fields

The following fields are explicitly prohibited in `SKILL.md` frontmatter:

| Prohibited Field | Reason | Correct Location |
|------------------|--------|------------------|
| `author` | Not Claude standard | `README.md` |
| `version` | Auto-managed by workflow | `.claude-plugin/marketplace.json` |
| `license` | Not Claude standard | `LICENSE` file |
| `metadata.*` | Wastes tokens | N/A |

**Rationale:** Per Claude Code skill standards, only `name` and `description` are supported fields. Extra fields consume tokens without providing value to Claude's skill activation logic.

**Sources:** [CONTRIBUTING.md:49-56]()

### Frontmatter Validation Flow

```mermaid
flowchart TD
    Start["Pull Request Created"] --> CheckExists["Check frontmatter exists"]
    CheckExists -->|"Missing ---"| Error1["❌ ERROR: No frontmatter found"]
    CheckExists -->|"Present"| ParseYAML["Parse YAML between --- delimiters"]
    
    ParseYAML -->|"Parse fails"| Error2["❌ ERROR: Invalid frontmatter format"]
    ParseYAML -->|"Success"| CheckRequired["Check required fields: name, description"]
    
    CheckRequired -->|"Missing"| Error3["❌ ERROR: Missing required fields"]
    CheckRequired -->|"Present"| ValidateName["Validate name matches ^[a-zA-Z0-9-]+$"]
    
    ValidateName -->|"Invalid"| Error4["❌ ERROR: Invalid name format"]
    ValidateName -->|"Valid"| ValidateDesc["Validate description length <= 1024"]
    
    ValidateDesc -->|"Too long"| Error5["❌ ERROR: Description too long"]
    ValidateDesc -->|"Valid"| CheckOptional["Log optional fields if present"]
    
    CheckOptional --> Success["✅ Frontmatter valid"]
    
    Error1 --> ExitFail["exit 1"]
    Error2 --> ExitFail
    Error3 --> ExitFail
    Error4 --> ExitFail
    Error5 --> ExitFail
    
    Success --> Continue["Continue validation"]
```

**Sources:** [.github/workflows/validate.yml:34-92]()

---

## Description Standards

### Format Requirements

The `description` field serves as the skill activation trigger for Claude. It must follow a specific pattern to maximize effectiveness.

**Required Pattern:**

```
Use when [specific triggers/scenarios]
```

**Good Example:**

```yaml
description: >-
  Use when working with Terraform or OpenTofu - creating modules, writing
  tests (native test framework, Terratest), setting up CI/CD pipelines,
  reviewing configurations, choosing between testing approaches, debugging
  state issues, implementing security scanning (trivy, checkov), or making
  infrastructure-as-code architecture decisions
```

**Bad Example:**

```yaml
description: Comprehensive skill for Terraform development covering testing, modules, CI/CD, and production patterns
```

**Sources:** [CONTRIBUTING.md:58-78]()

### Trigger-Based Approach

The description must focus on **WHEN** to use the skill (triggers/symptoms), not **WHAT** it does (workflow summary).

| Approach | Focus | Example |
|----------|-------|---------|
| ✅ Correct | User symptoms and triggers | "Use when debugging state issues" |
| ❌ Incorrect | Capability summary | "Provides state management guidance" |

**Rationale:** Claude's skill activation system looks for pattern matches between user queries and description content. Symptom-based triggers have higher activation accuracy than abstract capability descriptions.

**Sources:** [CONTRIBUTING.md:78]()

---

## Token Efficiency Guidelines

### Target Metrics

| File | Current | Target | Warning Threshold |
|------|---------|--------|-------------------|
| `SKILL.md` | ~1,400 words | <1,500 words | 500 lines |
| `SKILL.md` | ~280 lines | N/A | 500 lines |

**Sources:** [CONTRIBUTING.md:80-90](), [.github/workflows/validate.yml:94-103]()

### File Size Validation

```mermaid
flowchart LR
    Count["Count lines in SKILL.md"] --> Check{"Lines > 500?"}
    Check -->|"Yes"| Warn["⚠️ WARNING: Lines exceeds guideline"]
    Check -->|"No"| Pass["✅ Size OK"]
    
    Warn --> Log["Log to CI output"]
    Pass --> Log
    
    Log --> Continue["Continue validation"]
```

**Note:** Line count exceeding 500 triggers a warning but does not fail validation. This serves as a guideline for contributors.

**Sources:** [.github/workflows/validate.yml:94-103]()

### Token Reduction Techniques

| Technique | Description | Example Location |
|-----------|-------------|------------------|
| Progressive disclosure | Move detailed content to `references/*.md` | `references/module-patterns.md` |
| Table formatting | Use tables instead of prose | Module comparison tables |
| Link compression | Pipe-separated reference links | Quick reference sections |
| Cross-referencing | Reference existing files instead of duplicating | Internal file links |

**Current Token Distribution:**

```mermaid
graph LR
    subgraph "Core Content"
        SKILL["SKILL.md<br/>~4,400 tokens"]
    end
    
    subgraph "Reference Files - Progressive Disclosure"
        MOD["module-patterns.md<br/>~7,000 tokens"]
        QUICK["quick-reference.md<br/>~3,800 tokens"]
        CODE["code-patterns.md<br/>~5,100 tokens"]
        CI["ci-cd-workflows.md<br/>~2,300 tokens"]
        SEC["security-compliance.md<br/>~2,500 tokens"]
    end
    
    SKILL -.->|"On-demand loading"| MOD
    SKILL -.->|"On-demand loading"| QUICK
    SKILL -.->|"On-demand loading"| CODE
    SKILL -.->|"On-demand loading"| CI
    SKILL -.->|"On-demand loading"| SEC
    
    Total["Total: ~30,400 tokens<br/>Typical query: 4.5K-12K tokens<br/>56-70% reduction"]
```

**Sources:** [CONTRIBUTING.md:80-90]()

---

## File Organization Standards

### Directory Structure

```
terraform-skill/
├── SKILL.md                       # Core skill (<500 lines guideline)
├── references/                    # Reference files (progressive disclosure)
│   ├── testing-frameworks.md
│   ├── module-patterns.md
│   ├── ci-cd-workflows.md
│   ├── security-compliance.md
│   └── quick-reference.md
├── tests/                         # TDD testing framework
│   ├── baseline-scenarios.md
│   ├── compliance-verification.md
│   └── rationalization-table.md
└── .github/workflows/             # Automation
    ├── release.yml
    └── validate.yml
```

**Sources:** [CONTRIBUTING.md:92-110]()

### File Responsibility Matrix

| File Type | Purpose | Token Budget | Validation |
|-----------|---------|--------------|------------|
| `SKILL.md` | Core skill content loaded by Claude | ~4,400 tokens | Frontmatter, size checks |
| `references/*.md` | Detailed guidance loaded on-demand | ~7,000 tokens max | Link validation |
| `tests/*.md` | Testing scenarios and evidence | N/A | Not validated |
| `.claude-plugin/marketplace.json` | Plugin definition and versioning | ~100 tokens | JSON schema, version format |

**Sources:** [CONTRIBUTING.md:92-110]()

---

## Writing Style Standards

### Voice and Tone

**Imperative voice is required:**

| Style | Example | Usage |
|-------|---------|-------|
| ✅ Correct | "Use underscores in variable names" | All guidance |
| ❌ Incorrect | "You should consider using underscores" | Never use |
| ❌ Incorrect | "It's recommended to use underscores" | Never use |

**Rationale:** Imperative voice is more concise (fewer tokens) and provides clearer direction to Claude.

**Sources:** [CONTRIBUTING.md:197-199]()

### Scannable Formatting

All content must be structured for rapid scanning by Claude's attention mechanism:

| Format | Use For | Example |
|--------|---------|---------|
| Tables | Comparisons, decision matrices | Testing framework selection |
| ✅ DO vs ❌ DON'T | Side-by-side correct/incorrect patterns | Module structure examples |
| Code blocks with comments | Implementation examples | Terraform configurations |
| Clear section headers | Hierarchical organization | `## Testing Strategy` |

**Sources:** [CONTRIBUTING.md:201-206]()

### Version-Specific Markers

All version-dependent content must include explicit version markers:

**Pattern:**

```markdown
**Native Tests** (Terraform 1.6+, OpenTofu 1.6+)
```

**Required Format:**

- Feature name in bold
- Parenthetical version requirement
- Both Terraform and OpenTofu versions when applicable

**Sources:** [CONTRIBUTING.md:207-210]()

---

## Code Example Standards

### Quality Requirements

**"One excellent example beats many mediocre ones"**

| Requirement | Description | Validation |
|-------------|-------------|------------|
| Complete | Runnable without modifications | Manual review |
| Commented | Explains WHY, not just WHAT | Manual review |
| Real-world | From actual scenarios, not contrived | Manual review |
| Pattern clarity | Demonstrates pattern unambiguously | Manual review |
| Adaptable | Easy to modify for user's context | Manual review |

**Sources:** [CONTRIBUTING.md:213-227]()

### Good vs Bad Examples

```mermaid
graph TB
    subgraph "✅ Good Example"
        Good1["Complete and runnable"]
        Good2["Well-commented explaining WHY"]
        Good3["From real scenario"]
        Good4["Shows pattern clearly"]
        Good5["Ready to adapt"]
    end
    
    subgraph "❌ Avoid"
        Bad1["Multiple language implementations"]
        Bad2["Fill-in-the-blank templates"]
        Bad3["Contrived examples"]
        Bad4["Uncommented code snippets"]
    end
    
    Example["Code Example"] --> Good1
    Example --> Good2
    Example --> Good3
    Example --> Good4
    Example --> Good5
    
    Example -.->|"Don't include"| Bad1
    Example -.->|"Don't include"| Bad2
    Example -.->|"Don't include"| Bad3
    Example -.->|"Don't include"| Bad4
```

**Sources:** [CONTRIBUTING.md:213-227]()

---

## Decision Framework Standards

### WHEN Information Requirement

All decision guidance must include WHEN information, not just HOW information:

| Component | Required | Example |
|-----------|----------|---------|
| When to use approach A vs B | ✅ Yes | "Use native tests when Terraform 1.6+" |
| Factors influencing decision | ✅ Yes | "Team Go expertise, existing test suite" |
| Tradeoffs and considerations | ✅ Yes | "Native tests: simpler but less flexible" |
| Implementation steps | ❌ No | Belongs in reference files |

**Sources:** [CONTRIBUTING.md:229-242]()

### Table-Based Decision Guidance

**Required Format:**

```markdown
| Your Situation | Recommended Approach |
|----------------|---------------------|
| Terraform 1.6+, simple logic | Native tests |
| Pre-1.6, Go expertise | Terratest |
```

**Pattern:**

1. Left column: User's context/situation
2. Right column: Specific recommendation
3. Rows: Exhaustive coverage of common scenarios

**Sources:** [CONTRIBUTING.md:236-242]()

---

## Validation System

### Automated Validation Checks

```mermaid
flowchart TD
    PR["Pull Request Triggered"] --> V1["Check SKILL.md Frontmatter"]
    V1 --> V2["Check File Size"]
    V2 --> V3["Validate marketplace.json"]
    V3 --> V4["Check for Broken Links"]
    V4 --> V5["Lint Markdown"]
    
    V1 -.->|"Failure"| Fail1["❌ Invalid frontmatter"]
    V2 -.->|"Warning"| Warn1["⚠️ Size exceeds guideline"]
    V3 -.->|"Failure"| Fail2["❌ Invalid marketplace.json"]
    V4 -.->|"Failure"| Fail3["❌ Broken internal links"]
    V5 -.->|"Warning"| Warn2["⚠️ Markdown style issues"]
    
    V5 --> Summary["Generate validation summary"]
    
    Fail1 --> Exit["exit 1"]
    Fail2 --> Exit
    Fail3 --> Exit
    
    Warn1 --> Summary
    Warn2 --> Summary
    Summary --> Success["✅ Validation Passed"]
```

**Sources:** [.github/workflows/validate.yml:1-183]()

### Validation Components

| Check | File | Failure Behavior | Lines |
|-------|------|------------------|-------|
| Frontmatter validation | `validate.yml` | Fails CI | [.github/workflows/validate.yml:34-92]() |
| File size check | `validate.yml` | Warning only | [.github/workflows/validate.yml:94-103]() |
| marketplace.json validation | `validate.yml` | Fails CI | [.github/workflows/validate.yml:105-151]() |
| Broken link detection | `validate.yml` | Fails CI | [.github/workflows/validate.yml:153-166]() |
| Markdown linting | `validate.yml` | Warning only | [.github/workflows/validate.yml:168-176]() |

**Sources:** [.github/workflows/validate.yml:1-183]()

### marketplace.json Validation

```mermaid
flowchart TD
    Start["Parse marketplace.json"] --> CheckMarket["Check marketplace-level fields"]
    CheckMarket --> CheckOwner["Validate owner.name exists"]
    CheckOwner --> CheckVersion["Validate version format: ^\d+\.\d+\.\d+$"]
    CheckVersion --> CheckPlugins["Validate plugins array non-empty"]
    CheckPlugins --> LoopPlugins["For each plugin in array"]
    
    LoopPlugins --> CheckPluginFields["Check required plugin fields:<br/>name, description, source"]
    
    CheckMarket -.->|"Missing fields"| Fail1["❌ Missing marketplace fields"]
    CheckOwner -.->|"No owner.name"| Fail2["❌ owner must have name"]
    CheckVersion -.->|"Invalid format"| Fail3["❌ Invalid version format"]
    CheckPlugins -.->|"Empty or not array"| Fail4["❌ plugins must be non-empty array"]
    CheckPluginFields -.->|"Missing fields"| Fail5["❌ Plugin missing required fields"]
    
    CheckPluginFields --> Success["✅ marketplace.json valid"]
    
    Fail1 --> Exit["exit 1"]
    Fail2 --> Exit
    Fail3 --> Exit
    Fail4 --> Exit
    Fail5 --> Exit
```

**Sources:** [.github/workflows/validate.yml:105-151]()

### Validation Trigger Configuration

| Trigger | Paths Monitored | Behavior |
|---------|----------------|----------|
| Pull Request | `SKILL.md`, `references/**/*.md`, `.claude-plugin/**` | Full validation |
| Push to master/main | `SKILL.md`, `references/**/*.md`, `.claude-plugin/**` | Full validation |
| Manual dispatch | All files | Full validation |

**Sources:** [.github/workflows/validate.yml:3-15]()

---

## Content Standards Compliance Matrix

```mermaid
graph TB
    subgraph "Content Standards"
        FRONT["Frontmatter Requirements"]
        DESC["Description Standards"]
        TOKEN["Token Efficiency"]
        STYLE["Writing Style"]
        CODE["Code Examples"]
        DECISION["Decision Frameworks"]
    end
    
    subgraph "Enforcement Mechanisms"
        AUTO["Automated Validation<br/>validate.yml"]
        MANUAL["Manual Review<br/>CONTRIBUTING.md"]
        TEMPLATE["PR Template<br/>PULL_REQUEST_TEMPLATE.md"]
    end
    
    subgraph "Validation Results"
        PASS["✅ Standards Met"]
        FAIL["❌ Changes Required"]
    end
    
    FRONT --> AUTO
    DESC --> MANUAL
    TOKEN --> MANUAL
    STYLE --> MANUAL
    CODE --> MANUAL
    DECISION --> MANUAL
    
    AUTO --> PASS
    AUTO --> FAIL
    MANUAL --> PASS
    MANUAL --> FAIL
    TEMPLATE --> MANUAL
```

**Sources:** [.github/workflows/validate.yml:1-183](), [CONTRIBUTING.md:32-242]()

---

# Page: Testing Methodology

# Testing Methodology

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CLAUDE.md](CLAUDE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)

</details>



## Purpose and Scope

This document describes the testing methodology for validating changes to terraform-skill content. The testing approach treats skill development as Test-Driven Development (TDD) for documentation, requiring empirical evidence that changes improve Claude's behavior before merging.

For information about content structure and organization, see [Content Standards](#5.2). For the complete contribution process including pull requests, see [Contribution Workflow](#5.4). For automation that validates file structure and metadata, see [Validation Workflow](#6.1).

---

## The Iron Law

**NO CHANGES WITHOUT TESTING FIRST**

This absolute requirement applies to all content modifications:

| Change Type | Testing Required |
|-------------|------------------|
| New content additions | ✅ Yes |
| Edits to existing content | ✅ Yes |
| Reorganization or refactoring | ✅ Yes |
| Documentation updates | ✅ Yes |
| Grammar/typo fixes | ✅ Yes |

**No exceptions.**

The rationale: Without testing, there is no empirical evidence that changes actually improve Claude's behavior. Changes that seem logical may introduce rationalizations, conflicts with existing guidance, or fail to activate in relevant scenarios.

Sources: [CONTRIBUTING.md:112-124]()

---

## TDD for Documentation

### Conceptual Framework

Traditional software follows the RED/GREEN/REFACTOR cycle for code. Skill development applies the same principle to documentation:

```mermaid
graph LR
    RED["RED<br/>Run scenarios WITHOUT changes<br/>Document baseline behavior"]
    GREEN["GREEN<br/>Apply changes<br/>Verify improved behavior"]
    REFACTOR["REFACTOR<br/>Close loopholes<br/>Re-test"]
    
    RED --> GREEN
    GREEN --> REFACTOR
    REFACTOR --> RED
    
    PASS["Merge to master"]
    FAIL["Iterate on changes"]
    
    GREEN -->|"Behavior improved"| PASS
    GREEN -->|"No improvement"| FAIL
    REFACTOR -->|"Rationalizations found"| FAIL
```

**Diagram: TDD Cycle for Skill Development**

Sources: [CONTRIBUTING.md:127-133]()

### Why This Approach Matters

Skills are executable documentation that shape AI agent behavior. Unlike traditional documentation where "working" means "readable," skills must demonstrably improve agent outputs. The TDD approach ensures:

1. **Baseline measurement** - Understanding current behavior before changes
2. **Empirical validation** - Verifying improvements actually occur
3. **Regression detection** - Catching unintended behavior changes
4. **Rationalization prevention** - Identifying when agents circumvent guidance

Sources: [CONTRIBUTING.md:127-133]()

---

## Testing Workflow

### Overview

```mermaid
flowchart TD
    START["Identify Change Needed"]
    
    subgraph "Phase 1: Baseline"
        IDENTIFY["Identify Affected Scenarios<br/>(tests/baseline-scenarios.md)"]
        DISABLE["Disable Skill<br/>(mv ~/.claude/references/terraform-skill)"]
        RUN_BASE["Run Scenarios<br/>WITHOUT Changes"]
        DOC_BASE["Document Baseline Behavior<br/>(tests/baseline-results/)"]
    end
    
    subgraph "Phase 2: Implementation"
        APPLY["Apply Changes<br/>(SKILL.md or references/*.md)"]
        ENABLE["Re-enable Skill<br/>(mv back to ~/.claude/references/)"]
    end
    
    subgraph "Phase 3: Compliance"
        RUN_COMP["Run Same Scenarios<br/>WITH Changes"]
        DOC_COMP["Document Compliance Behavior<br/>(tests/compliance-results/)"]
        COMPARE["Compare Baseline vs Compliance"]
    end
    
    subgraph "Phase 4: Verification"
        CHECK_IMP["Verify Improvement"]
        CHECK_RAT["Check for Rationalizations"]
        RECORD_RAT["Record in rationalization-table.md<br/>if found"]
        RETEST["Close Loopholes & Re-test"]
    end
    
    START --> IDENTIFY
    IDENTIFY --> DISABLE
    DISABLE --> RUN_BASE
    RUN_BASE --> DOC_BASE
    DOC_BASE --> APPLY
    APPLY --> ENABLE
    ENABLE --> RUN_COMP
    RUN_COMP --> DOC_COMP
    DOC_COMP --> COMPARE
    COMPARE --> CHECK_IMP
    CHECK_IMP --> CHECK_RAT
    CHECK_RAT -->|"Rationalizations found"| RECORD_RAT
    RECORD_RAT --> RETEST
    RETEST --> RUN_COMP
    CHECK_RAT -->|"No rationalizations"| SUBMIT["Submit PR with Evidence"]
```

**Diagram: Complete Testing Workflow**

Sources: [CONTRIBUTING.md:134-191]()

### Step-by-Step Process

#### 1. Identify Affected Scenarios

Review `tests/baseline-scenarios.md` to determine which test scenarios your change affects.

**Example mapping:**

| Change Type | Affected Scenarios |
|-------------|-------------------|
| Adding security scanning guidance | Scenario 3: Security implementation |
| Updating testing framework recommendations | Scenario 1: Test framework selection |
| Modifying module structure patterns | Scenario 2: Module creation |

Sources: [CONTRIBUTING.md:136-140]()

#### 2. Run Baseline (WITHOUT Changes)

Temporarily disable the skill to measure current behavior:

```bash
# Disable skill
mv ~/.claude/references/terraform-skill \
   ~/.claude/references/terraform-skill.disabled
```

Execute affected scenarios and document agent responses in `tests/baseline-results/`.

Sources: [CONTRIBUTING.md:142-150](), [CLAUDE.md:176-189]()

#### 3. Apply Changes

Make edits to `SKILL.md` or files in `references/`:

- `references/module-patterns.md` - Module development patterns
- `references/code-patterns.md` - Code structure and modern features
- `references/quick-reference.md` - Command cheat sheets
- `references/ci-cd-workflows.md` - Pipeline integration
- `references/security-compliance.md` - Security scanning

Sources: [CONTRIBUTING.md:152-154](), [CLAUDE.md:17-32]()

#### 4. Run Compliance Test (WITH Changes)

Re-enable the skill with your modifications:

```bash
# Re-enable skill
mv ~/.claude/references/terraform-skill.disabled \
   ~/.claude/references/terraform-skill
```

Execute the same scenarios and document improved behavior in `tests/compliance-results/`.

Sources: [CONTRIBUTING.md:156-165]()

#### 5. Verify Improvement

Compare baseline vs compliance behaviors:

| Verification Criteria | What to Check |
|----------------------|---------------|
| **Pattern Application** | Does agent now follow your guidance? |
| **Proactive Usage** | Are patterns applied without prompting? |
| **Consistency** | Is guidance applied consistently across scenarios? |
| **No Regressions** | Existing patterns still work correctly? |
| **No Rationalizations** | Agent doesn't circumvent new guidance? |

Sources: [CONTRIBUTING.md:167-172]()

---

## Baseline vs Compliance Testing

### Test Scenarios Location

Test scenarios are defined in `tests/baseline-scenarios.md`. Each scenario represents a common Terraform/OpenTofu task where skill guidance should activate.

**File structure:**

```
tests/
├── baseline-scenarios.md           # Standard test scenarios
├── baseline-results/               # Agent behavior WITHOUT changes
├── compliance-results/             # Agent behavior WITH changes
└── rationalization-table.md        # Known workarounds/evasions
```

Sources: [CONTRIBUTING.md:93-109]()

### Comparison Framework

```mermaid
graph TB
    subgraph "Baseline Behavior"
        BASE_QUERY["User Query:<br/>'Create Terraform module with tests'"]
        BASE_RESP["Agent Response<br/>(WITHOUT skill changes)"]
        BASE_PATTERNS["Patterns Applied:<br/>- Generic testing advice<br/>- No framework selection<br/>- No version-specific guidance"]
    end
    
    subgraph "Compliance Behavior"
        COMP_QUERY["Same User Query:<br/>'Create Terraform module with tests'"]
        COMP_RESP["Agent Response<br/>(WITH skill changes)"]
        COMP_PATTERNS["Patterns Applied:<br/>- Decision matrix consulted<br/>- Terraform 1.6+ native tests recommended<br/>- Specific examples provided"]
    end
    
    subgraph "Evidence"
        EVIDENCE["Documented Improvement:<br/>- Framework selection guidance applied<br/>- Version-appropriate patterns used<br/>- No rationalizations observed"]
    end
    
    BASE_QUERY --> BASE_RESP
    BASE_RESP --> BASE_PATTERNS
    
    COMP_QUERY --> COMP_RESP
    COMP_RESP --> COMP_PATTERNS
    
    BASE_PATTERNS --> EVIDENCE
    COMP_PATTERNS --> EVIDENCE
```

**Diagram: Baseline vs Compliance Comparison**

Sources: [CONTRIBUTING.md:167-172]()

### Documentation Requirements

For each tested scenario, document:

**Baseline (without changes):**
- Query text used
- Agent's complete response
- Patterns agent applied (or failed to apply)
- Issues or gaps identified

**Compliance (with changes):**
- Same query text
- Agent's improved response
- New patterns agent applied
- Evidence of guidance activation

**Comparison:**
- Specific improvements observed
- Behavior changes (positive and negative)
- Rationalizations discovered (if any)

Sources: [CONTRIBUTING.md:174-180]()

---

## Rationalization Tracking

### What Are Rationalizations?

Rationalizations occur when Claude circumvents or creatively reinterprets skill guidance. Common patterns:

| Rationalization Type | Example |
|---------------------|---------|
| **Rule avoidance** | "While the skill suggests X, in this specific case Y is better because..." |
| **Selective application** | Applying guidance to some scenarios but not others without justification |
| **Creative interpretation** | Redefining terms to justify different behavior |
| **Prioritization conflict** | "The skill says X but best practices dictate Y" (when skill IS best practices) |

### Recording Rationalizations

When rationalizations are discovered during testing, record them in `tests/rationalization-table.md`:

```markdown
| Scenario | Rationalization Observed | Root Cause | Mitigation |
|----------|-------------------------|------------|------------|
| Module testing | "Terratest is better for this complex module despite skill recommending native tests" | Ambiguous decision matrix criteria | Add complexity threshold to decision matrix |
```

### Closing Loopholes

When a rationalization is discovered:

1. **Record it** in `tests/rationalization-table.md`
2. **Identify root cause** - Why did agent rationalize?
3. **Refine guidance** - Make criteria more explicit
4. **Re-test** - Verify rationalization eliminated
5. **Repeat** until compliance behavior is consistent

This is the "REFACTOR" phase of the TDD cycle.

Sources: [CONTRIBUTING.md:187-191]()

---

## Evidence Documentation

### PR Requirements

Every pull request must include testing evidence in the description:

```markdown
## Testing Evidence

### Scenarios Tested
- Scenario 1: Test framework selection
- Scenario 3: Security scanning implementation

### Baseline Behavior (WITHOUT changes)
Query: "Create a Terraform module with tests"
Response: Agent suggested generic testing approach without 
framework selection guidance or version considerations.

### Compliance Behavior (WITH changes)
Query: "Create a Terraform module with tests"
Response: Agent consulted decision matrix, recommended 
native tests for Terraform 1.6+, provided specific examples 
with mock providers.

### Improvement Verified
✅ Decision matrix activated
✅ Version-specific patterns applied
✅ No rationalizations observed
✅ Existing patterns still work
```

Sources: [CONTRIBUTING.md:174-180]()

### Testing Checklist

Use this checklist in every PR:

```markdown
- [ ] Identified affected scenarios from tests/baseline-scenarios.md
- [ ] Ran baseline WITHOUT changes (documented)
- [ ] Applied changes
- [ ] Ran compliance WITH changes (documented)
- [ ] Verified behavior improvement
- [ ] No new rationalizations discovered
- [ ] If rationalizations found, documented in rationalization-table.md
- [ ] Re-tested after closing loopholes
```

Sources: [CONTRIBUTING.md:181-191]()

---

## Testing Checklist Reference

### Pre-Submission Verification

| Criterion | Verification Method |
|-----------|-------------------|
| **Scenarios identified** | Listed specific scenarios from `tests/baseline-scenarios.md` |
| **Baseline documented** | Responses saved in `tests/baseline-results/` |
| **Changes applied** | Edited `SKILL.md` or `references/*.md` |
| **Compliance documented** | Improved responses saved in `tests/compliance-results/` |
| **Improvement verified** | Side-by-side comparison shows better behavior |
| **No rationalizations** | Agent follows guidance without creative reinterpretation |
| **Loopholes closed** | If rationalizations found, guidance refined and re-tested |
| **Evidence included** | PR description contains baseline/compliance comparison |

### Local Testing Environment

Testing requires Claude Code with skill loading capability:

```bash
# Skill location
~/.claude/references/terraform-skill/

# Testing workflow
~/.claude/references/terraform-skill/       # Active skill
~/.claude/references/terraform-skill.disabled/  # Disabled for baseline

# Test artifacts
tests/baseline-scenarios.md                 # Standard scenarios
tests/baseline-results/                     # Baseline behavior logs
tests/compliance-results/                   # Compliance behavior logs
tests/rationalization-table.md              # Known issues tracker
```

Sources: [CLAUDE.md:176-198](), [CONTRIBUTING.md:142-165]()

---

## Integration with Quality Systems

### Relationship to Automated Validation

Testing methodology complements but does not replace automated validation:

| System | Purpose | Scope |
|--------|---------|-------|
| **Testing Methodology** (this document) | Validate behavior improvements | Agent response quality |
| **Validation Workflow** ([6.1](#6.1)) | Validate file structure | Frontmatter, links, size |
| **Content Standards** ([5.2](#5.2)) | Define writing requirements | Token efficiency, formatting |

Testing methodology provides empirical evidence that automated systems cannot: whether changes actually improve Claude's Terraform guidance.

Sources: [CONTRIBUTING.md:112-191](), High-Level System Architecture Diagram 4

### Maintainer Review Process

Testing evidence informs maintainer review criteria:

```mermaid
graph TD
    PR["Pull Request Submitted"]
    
    subgraph "Automated Checks"
        AUTO_VALID[".github/workflows/validate.yml<br/>Frontmatter, size, links"]
    end
    
    subgraph "Testing Evidence Review"
        TEST_EVIDENCE["Testing Evidence in PR Description"]
        BASELINE["Baseline behavior documented?"]
        COMPLIANCE["Compliance behavior documented?"]
        IMPROVEMENT["Clear improvement shown?"]
        NO_RAT["No rationalizations introduced?"]
    end
    
    subgraph "Manual Review"
        ACCURACY["Technical Accuracy"]
        QUALITY["Content Quality"]
        STANDARDS["Standards Compliance"]
    end
    
    PR --> AUTO_VALID
    AUTO_VALID -->|"Pass"| TEST_EVIDENCE
    AUTO_VALID -->|"Fail"| REJECT["Request Changes"]
    
    TEST_EVIDENCE --> BASELINE
    BASELINE --> COMPLIANCE
    COMPLIANCE --> IMPROVEMENT
    IMPROVEMENT --> NO_RAT
    
    NO_RAT -->|"Evidence complete"| ACCURACY
    NO_RAT -->|"Missing evidence"| REJECT
    
    ACCURACY --> QUALITY
    QUALITY --> STANDARDS
    STANDARDS --> APPROVE["Approve & Merge"]
```

**Diagram: Testing Evidence in Review Process**

Sources: [CONTRIBUTING.md:338-346](), High-Level System Architecture Diagram 4

---

## Practical Testing Examples

### Example 1: Adding Security Scanning Guidance

**Change:** Add trivy and checkov recommendations to `references/security-compliance.md`

**Affected scenarios:** Scenario 3 (Security implementation)

**Baseline behavior:**
- Query: "Add security scanning to my Terraform pipeline"
- Response: Generic recommendation to "use security tools" without specifics

**Compliance behavior:**
- Query: "Add security scanning to my Terraform pipeline"  
- Response: Recommends trivy for IaC scanning, checkov for compliance, provides integration examples

**Evidence:** Agent now provides actionable, specific tool recommendations with configuration examples

### Example 2: Updating Testing Framework Decision Matrix

**Change:** Refine criteria in `SKILL.md` decision matrix for test framework selection

**Affected scenarios:** Scenario 1 (Test framework selection)

**Baseline behavior:**
- Query: "What testing framework should I use for Terraform?"
- Response: Suggests "it depends" without clear decision criteria

**Compliance behavior:**
- Query: "What testing framework should I use for Terraform?"
- Response: Asks about Terraform version, then recommends native tests for 1.6+, provides decision matrix rationale

**Rationalization discovered:** Agent said "native tests work but Terratest is more mature" (undermining guidance)

**Refinement:** Added explicit "RECOMMENDED" label to decision matrix cells, re-tested, rationalization eliminated

**Evidence:** Agent now confidently recommends appropriate framework based on clear criteria

Sources: [CONTRIBUTING.md:134-191]()

---

## Summary

Testing methodology for terraform-skill enforces TDD principles for documentation:

1. **Iron Law:** All changes require testing before merge
2. **RED phase:** Document baseline behavior without changes
3. **GREEN phase:** Verify improved behavior with changes  
4. **REFACTOR phase:** Close rationalization loopholes and re-test
5. **Evidence:** PR must include baseline/compliance comparison
6. **Quality:** Testing evidence reviewed by maintainers

This methodology ensures every change demonstrably improves Claude's Terraform expertise rather than relying on assumptions about what "should" work.

Sources: [CONTRIBUTING.md:112-191](), [CLAUDE.md:160-198]()

---

# Page: Contribution Workflow

# Contribution Workflow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)

</details>



This document describes the step-by-step process for contributing changes to terraform-skill, from initial development through PR submission to automated release. It covers the practical mechanics of creating, testing, and submitting contributions.

For the testing methodology details, see [Testing Methodology](#5.3). For content quality standards, see [Content Standards](#5.2). For the underlying development philosophy, see [Development Philosophy](#5.1).

---

## Overview of Contribution Process

The contribution workflow follows a standard fork-and-PR model with mandatory testing requirements and automated release management. All version management, changelog generation, and releases are fully automated based on conventional commit messages.

**Complete Contribution Workflow**

```mermaid
flowchart TD
    Fork["Fork Repository"]
    Clone["Clone to Local"]
    Branch["Create Feature Branch<br/>git checkout -b feature/name"]
    
    subgraph "Local Development"
        Edit["Edit Files<br/>SKILL.md or references/*.md"]
        Test["Test Changes<br/>(TDD Required)"]
        Commit["Commit with Conventional Format<br/>feat:, fix:, docs:"]
    end
    
    subgraph "Pre-Submission"
        LocalValidate["Local Validation<br/>Check frontmatter, links, size"]
        Evidence["Prepare Testing Evidence<br/>Baseline vs Compliance"]
    end
    
    subgraph "Pull Request"
        CreatePR["Create PR<br/>Use PULL_REQUEST_TEMPLATE.md"]
        AutoValidate["Automated Validation<br/>.github/workflows/validate.yml"]
        ManualReview["Maintainer Review<br/>Standards & Testing"]
    end
    
    subgraph "Post-Merge Automation"
        Merge["Merge to master"]
        AutoRelease["Automated Release Workflow<br/>.github/workflows/automated-release.yml"]
        VersionBump["Calculate Version Bump<br/>from Conventional Commits"]
        UpdateFiles["Update marketplace.json<br/>SKILL.md, CHANGELOG.md"]
        CreateRelease["Create Git Tag & GitHub Release"]
    end
    
    Fork --> Clone
    Clone --> Branch
    Branch --> Edit
    Edit --> Test
    Test -->|Pass| Commit
    Test -->|Fail| Edit
    Commit --> LocalValidate
    LocalValidate --> Evidence
    Evidence --> CreatePR
    
    CreatePR --> AutoValidate
    AutoValidate -->|Pass| ManualReview
    AutoValidate -->|Fail| Edit
    ManualReview -->|Approved| Merge
    ManualReview -->|Changes Requested| Edit
    
    Merge --> AutoRelease
    AutoRelease --> VersionBump
    VersionBump --> UpdateFiles
    UpdateFiles --> CreateRelease
```

**Sources:** [CONTRIBUTING.md:1-381](), [.github/PULL_REQUEST_TEMPLATE.md:1-148]()

---

## Step 1: Repository Setup

### Forking and Cloning

Fork the repository at `https://github.com/antonbabenko/terraform-skill` and clone your fork locally [CONTRIBUTING.md:8-9]().

```bash
git clone https://github.com/YOUR_USERNAME/terraform-skill.git
cd terraform-skill
```

### Branch Creation

Create a feature branch from `master` following the naming convention `feature/descriptive-name` [CONTRIBUTING.md:312-315]():

```bash
git checkout -b feature/improve-testing-guidance
```

**Sources:** [CONTRIBUTING.md:312-315]()

---

## Step 2: Making Changes

### File Location Guidelines

Changes must follow the file organization structure [CONTRIBUTING.md:92-110]():

| File Type | Location | Purpose | Size Guideline |
|-----------|----------|---------|----------------|
| Core skill content | `SKILL.md` | Primary skill content loaded by Claude | <1,500 words, <500 lines |
| Reference documentation | `references/*.md` | Progressive disclosure content | No strict limit |
| Testing scenarios | `tests/baseline-scenarios.md` | Test scenario definitions | N/A |
| Rationalization tracking | `tests/rationalization-table.md` | Agent rationalization database | N/A |
| Documentation | `README.md`, `CONTRIBUTING.md` | User/contributor documentation | N/A |

### Frontmatter Requirements (Critical)

If modifying `SKILL.md`, the frontmatter must contain **exactly two fields** [CONTRIBUTING.md:34-56]():

```yaml
---
name: terraform-skill
description: Use when working with Terraform or OpenTofu - creating modules,
  writing tests...
---
```

**Prohibited fields:**
- `author` (belongs in README.md)
- `version` (managed by automated-release workflow)
- `license` (belongs in LICENSE)
- Any custom fields

**Sources:** [CONTRIBUTING.md:34-78](), [CONTRIBUTING.md:92-110]()

---

## Step 3: Testing Changes (Mandatory)

### The Iron Law

**NO CHANGES WITHOUT TESTING FIRST** [CONTRIBUTING.md:112-124](). This requirement has no exceptions and applies to all content changes, including documentation updates.

**Testing Process Flow**

```mermaid
flowchart TD
    Identify["Identify Affected Scenarios<br/>from tests/baseline-scenarios.md"]
    
    subgraph "Baseline Testing (RED Phase)"
        Disable["Disable Skill<br/>mv ~/.claude/references/terraform-skill<br/>.../terraform-skill.disabled"]
        RunBaseline["Run Test Scenarios<br/>WITHOUT Changes"]
        DocBaseline["Document Baseline Behavior<br/>in tests/baseline-results/"]
    end
    
    Apply["Apply Changes to SKILL.md<br/>or references/*.md"]
    
    subgraph "Compliance Testing (GREEN Phase)"
        Enable["Enable Skill<br/>mv ~/.claude/references/terraform-skill.disabled<br/>.../terraform-skill"]
        RunCompliance["Run Same Scenarios<br/>WITH Changes"]
        DocCompliance["Document Compliance Behavior<br/>in tests/compliance-results/"]
    end
    
    subgraph "Verification"
        Compare["Compare Baseline vs Compliance"]
        CheckImprovement["Verify Improvement:<br/>- Agent follows guidance<br/>- Patterns applied proactively<br/>- No new rationalizations"]
    end
    
    Refactor["Refactor if Needed<br/>Close loopholes"]
    Evidence["Prepare PR Evidence<br/>Baseline/Compliance documentation"]
    
    Identify --> Disable
    Disable --> RunBaseline
    RunBaseline --> DocBaseline
    DocBaseline --> Apply
    
    Apply --> Enable
    Enable --> RunCompliance
    RunCompliance --> DocCompliance
    DocCompliance --> Compare
    
    Compare --> CheckImprovement
    CheckImprovement -->|Pass| Evidence
    CheckImprovement -->|Fail| Refactor
    Refactor --> RunCompliance
```

### Testing Checklist

The PR must include evidence that all testing steps were completed [CONTRIBUTING.md:181-192]():

- [ ] Identified affected scenarios from `tests/baseline-scenarios.md`
- [ ] Ran baseline WITHOUT changes (documented)
- [ ] Applied changes
- [ ] Ran compliance WITH changes (documented)
- [ ] Verified behavior improvement
- [ ] No new rationalizations discovered (or documented in `tests/rationalization-table.md`)
- [ ] Re-tested if rationalizations found

**Sources:** [CONTRIBUTING.md:112-192]()

---

## Step 4: Committing Changes

### Conventional Commit Format

All commits must follow the Conventional Commits specification [CONTRIBUTING.md:244-307](). The commit type determines the automated version bump:

| Commit Type | Version Bump | Use Case | Example |
|-------------|--------------|----------|---------|
| `feat!:` or `BREAKING CHANGE:` | Major (1.x.x → 2.0.0) | Breaking changes | `feat!: remove deprecated test framework guidance` |
| `feat:` | Minor (1.2.x → 1.3.0) | New features | `feat: add OpenTofu 1.8 support` |
| `fix:` | Patch (1.2.3 → 1.2.4) | Bug fixes | `fix: correct module output syntax in examples` |
| `docs:` | Patch | Documentation only | `docs: improve testing strategy documentation` |
| `chore:` | Patch | Maintenance, tooling | `chore: update workflow dependencies` |
| `test:` | Patch | Test improvements | `test: add new baseline scenarios` |
| `refactor:` | Patch | Code refactoring | `refactor: reorganize module patterns` |

### Commit Message Structure

[CONTRIBUTING.md:248-255]()

```
<type>: <description>

[optional body]

[optional footer]
```

**Examples:**

```bash
# Simple feature
git commit -m "feat: add native testing examples"

# With detailed body
git commit -m "feat: add native testing examples

- Add examples for Terraform 1.6+ native tests
- Include decision matrix for test framework selection
- Document best practices for test organization"

# Bug fix
git commit -m "fix: correct security scanning tool recommendations"
```

**Sources:** [CONTRIBUTING.md:244-307]()

---

## Step 5: Pull Request Submission

### Using the PR Template

Create a PR using the template at `.github/PULL_REQUEST_TEMPLATE.md` [CONTRIBUTING.md:330-337](). The template enforces structured documentation of changes and testing evidence.

**PR Template Structure Mapping**

```mermaid
flowchart LR
    subgraph "PR Template Sections"
        Description["Description Section<br/>lines 3-16"]
        TestingEvidence["Testing Evidence Section<br/>lines 17-61<br/>(REQUIRED)"]
        StandardsCompliance["Standards Compliance Checklist<br/>lines 62-88"]
        Validation["Validation Section<br/>lines 95-104"]
        Rationalizations["Rationalizations Section<br/>lines 106-114"]
    end
    
    subgraph "Required Content"
        TypeChange["Type of Change<br/>New/Fix/Refactor/Docs/Test"]
        Scenarios["Scenarios Tested<br/>from tests/baseline-scenarios.md"]
        Baseline["Baseline Behavior<br/>WITHOUT changes"]
        Compliance["Compliance Behavior<br/>WITH changes"]
        Improvement["Evidence of Improvement<br/>4 verification points"]
    end
    
    subgraph "Automated Checks"
        Frontmatter["Frontmatter Validation<br/>lines 64-72"]
        TokenEfficiency["Token Efficiency<br/>lines 74-79"]
        ContentQuality["Content Quality<br/>lines 81-87"]
        FileOrg["File Organization<br/>lines 89-94"]
    end
    
    Description --> TypeChange
    TestingEvidence --> Scenarios
    TestingEvidence --> Baseline
    TestingEvidence --> Compliance
    TestingEvidence --> Improvement
    
    StandardsCompliance --> Frontmatter
    StandardsCompliance --> TokenEfficiency
    StandardsCompliance --> ContentQuality
    StandardsCompliance --> FileOrg
```

### Testing Evidence Requirements

The PR **must** include [.github/PULL_REQUEST_TEMPLATE.md:17-61]():

1. **Scenarios Tested**: List which scenarios from `tests/baseline-scenarios.md` were affected
2. **Baseline Behavior**: Verbatim agent response WITHOUT changes
3. **Compliance Behavior**: Verbatim agent response WITH changes
4. **Evidence of Improvement**: Checkboxes verifying:
   - Agent references new content
   - Agent applies new patterns proactively
   - Agent doesn't rationalize skipping guidance
   - No new rationalizations introduced

### Standards Compliance Checklist

**Frontmatter (if SKILL.md changed)** [.github/PULL_REQUEST_TEMPLATE.md:64-72]():
- [ ] Only `name` and `description` fields present
- [ ] Description starts with "Use when..."
- [ ] Description focuses on triggers/symptoms (not workflow summary)
- [ ] Description < 1024 characters
- [ ] Total frontmatter < 1024 characters
- [ ] Name uses only letters, numbers, hyphens

**Token Efficiency** [.github/PULL_REQUEST_TEMPLATE.md:74-79]():
- [ ] SKILL.md remains <1,500 words (current: ~1,400)
- [ ] Detailed content moved to `references/*.md` where appropriate
- [ ] Used tables instead of prose
- [ ] No content duplication

**Content Quality** [.github/PULL_REQUEST_TEMPLATE.md:81-87]():
- [ ] Imperative voice ("Use X", not "You should use X")
- [ ] Scannable format (tables, bullets, clear headers)
- [ ] Code examples are complete and runnable
- [ ] Version-specific features clearly marked
- [ ] ✅ DO vs ❌ DON'T patterns where appropriate

**Sources:** [.github/PULL_REQUEST_TEMPLATE.md:1-148](), [CONTRIBUTING.md:330-337]()

---

## Step 6: Automated Validation

Upon PR creation, the `validate.yml` workflow runs automated checks. See [Validation Workflow](#6.1) for complete details.

**Validation Workflow Components**

```mermaid
flowchart TD
    PRCreated["PR Created or Updated"]
    
    subgraph "validate.yml Workflow"
        CheckoutCode["Checkout Code"]
        
        subgraph "Validation Checks"
            FrontmatterCheck["Frontmatter Validation<br/>- Only name & description<br/>- Description format<br/>- Character limits"]
            FileSizeCheck["File Size Check<br/>SKILL.md < 500 lines (warning)"]
            LinkCheck["Link Validation<br/>No broken internal links"]
            MarkdownLint["Markdown Linting<br/>Format compliance"]
        end
        
        Results["Aggregate Results"]
    end
    
    PassFail{"All Checks<br/>Pass?"}
    GreenCheck["✅ Green Check<br/>Ready for Review"]
    FailedCheck["❌ Failed Check<br/>Fix Required"]
    
    PRCreated --> CheckoutCode
    CheckoutCode --> FrontmatterCheck
    CheckoutCode --> FileSizeCheck
    CheckoutCode --> LinkCheck
    CheckoutCode --> MarkdownLint
    
    FrontmatterCheck --> Results
    FileSizeCheck --> Results
    LinkCheck --> Results
    MarkdownLint --> Results
    
    Results --> PassFail
    PassFail -->|Yes| GreenCheck
    PassFail -->|No| FailedCheck
```

**Sources:** [CONTRIBUTING.md:338-346](), [.github/PULL_REQUEST_TEMPLATE.md:95-104]()

---

## Step 7: Maintainer Review

### Review Criteria

Maintainers evaluate PRs against five criteria [CONTRIBUTING.md:338-346]():

| Criterion | Evaluation | Reference |
|-----------|------------|-----------|
| **Standards compliance** | Frontmatter format, description structure | [CONTRIBUTING.md:34-78]() |
| **Testing evidence** | Baseline vs compliance documented, improvement shown | [CONTRIBUTING.md:112-192]() |
| **Token efficiency** | Not adding unnecessary content, SKILL.md <1,500 words | [CONTRIBUTING.md:80-91]() |
| **Accuracy** | Technically correct, reflects current best practices | [CONTRIBUTING.md:194-242]() |
| **Quality** | Clear, scannable, well-organized | [CONTRIBUTING.md:194-242]() |

### Maintainer Checklist

Maintainers complete the review checklist in the PR template [.github/PULL_REQUEST_TEMPLATE.md:130-148]():

**Review Checklist:**
- [ ] Testing evidence is convincing (baseline → compliance improvement shown)
- [ ] Standards compliance verified
- [ ] Content is accurate and current
- [ ] Token efficiency maintained
- [ ] Quality standards met
- [ ] No conflicts with existing content
- [ ] CHANGELOG.md updated (if needed)

**Merge Checklist:**
- [ ] Squash commits with clear commit message
- [ ] Update CHANGELOG.md if not done in PR
- [ ] Consider if version bump needed
- [ ] Tag if this completes a planned milestone

**Sources:** [CONTRIBUTING.md:338-346](), [.github/PULL_REQUEST_TEMPLATE.md:128-148]()

---

## Step 8: Post-Merge Automation

### Automated Release Process

When a PR is merged to `master`, the `automated-release.yml` workflow executes [CONTRIBUTING.md:347-361](). The entire release process is fully automated - contributors do not manage versions manually.

**Automated Release Workflow**

```mermaid
flowchart TD
    Merge["PR Merged to master"]
    
    subgraph "automated-release.yml Execution"
        Trigger["Workflow Triggered<br/>on push to master"]
        
        subgraph "Version Calculation"
            FetchCommits["Fetch Commits<br/>Since Last Release"]
            ParseCommits["Parse Conventional Commits<br/>feat:, fix:, feat!:, etc."]
            DetermineVersion["Determine Version Bump<br/>Major/Minor/Patch"]
        end
        
        subgraph "File Updates"
            UpdateMarketplace["Update marketplace.json<br/>3 version locations:<br/>- marketplace.version<br/>- marketplace.plugins[].version<br/>- marketplace.plugins[].source.git.ref"]
            UpdateSkill["Update SKILL.md<br/>Frontmatter version (if present)"]
            GenerateChangelog["Generate CHANGELOG.md<br/>Group by type: feat, fix, docs"]
        end
        
        subgraph "Release Creation"
            CreateTag["Create Git Tag<br/>vX.Y.Z"]
            CreateGHRelease["Create GitHub Release<br/>With changelog excerpt"]
            PublishMarketplace["Publish to Marketplace<br/>(via git ref)"]
        end
    end
    
    Merge --> Trigger
    Trigger --> FetchCommits
    FetchCommits --> ParseCommits
    ParseCommits --> DetermineVersion
    
    DetermineVersion --> UpdateMarketplace
    DetermineVersion --> UpdateSkill
    DetermineVersion --> GenerateChangelog
    
    UpdateMarketplace --> CreateTag
    UpdateSkill --> CreateTag
    GenerateChangelog --> CreateTag
    
    CreateTag --> CreateGHRelease
    CreateGHRelease --> PublishMarketplace
```

### Version Synchronization Points

The automated release workflow updates versions in three locations [CONTRIBUTING.md:352-358]():

1. `.claude-plugin/marketplace.json` - `marketplace.version` field
2. `.claude-plugin/marketplace.json` - `marketplace.plugins[0].version` field
3. `.claude-plugin/marketplace.json` - `marketplace.plugins[0].source.git.ref` field
4. `CHANGELOG.md` - Generated from conventional commits

For complete details on version synchronization, see [Version Synchronization](#6.3).

**Sources:** [CONTRIBUTING.md:347-361]()

---

## Common Workflow Patterns

### Pattern: Adding New Content

```bash
# 1. Create branch
git checkout -b feat/add-security-scanning

# 2. Edit file (e.g., add security content to SKILL.md)
# 3. Test WITHOUT changes (baseline)
mv ~/.claude/references/terraform-skill ~/.claude/references/terraform-skill.disabled
# Run test scenarios, document results

# 4. Test WITH changes (compliance)
mv ~/.claude/references/terraform-skill.disabled ~/.claude/references/terraform-skill
# Run same scenarios, document improvements

# 5. Commit with conventional format
git commit -m "feat: add trivy and checkov security scanning guidance"

# 6. Push and create PR
git push origin feat/add-security-scanning
# Create PR using template
```

### Pattern: Fixing Incorrect Information

```bash
# 1. Create branch
git checkout -b fix/correct-module-syntax

# 2. Edit file
# 3. Test baseline vs compliance
# 4. Commit
git commit -m "fix: correct module output syntax in examples"

# 5. Submit PR
```

### Pattern: Documentation-Only Changes

```bash
# 1. Create branch
git checkout -b docs/improve-readme

# 2. Edit README.md or CONTRIBUTING.md
# 3. If changes affect agent behavior, TEST
# 4. Commit
git commit -m "docs: clarify installation instructions"

# 5. Submit PR
```

**Sources:** [CONTRIBUTING.md:312-327]()

---

## Workflow Decision Matrix

| Your Situation | Recommended Action | Commit Type | Testing Required |
|----------------|-------------------|-------------|------------------|
| Adding new Terraform guidance | Edit `SKILL.md` or `references/*.md` | `feat:` | Yes (baseline vs compliance) |
| Fixing technical error | Edit affected file | `fix:` | Yes (verify fix works) |
| Reorganizing content | Edit affected files | `refactor:` | Yes (verify no behavior change) |
| Updating README only | Edit `README.md` | `docs:` | No (unless affects agent behavior) |
| Improving CI workflows | Edit `.github/workflows/*` | `chore:` | No (but test locally) |
| Adding test scenarios | Edit `tests/*.md` | `test:` | N/A (defines tests) |
| Breaking change (rare) | Edit affected files | `feat!:` or add `BREAKING CHANGE:` | Yes (extensive testing) |

**Sources:** [CONTRIBUTING.md:14-30](), [CONTRIBUTING.md:259-268]()

---

## Troubleshooting

### PR Validation Fails

**Problem:** Automated validation workflow fails

**Solution:**
1. Check workflow output in PR checks
2. Common issues:
   - Frontmatter contains prohibited fields (e.g., `version`, `author`)
   - Description doesn't start with "Use when..."
   - Broken internal links
   - Markdown linting errors

**Fix and re-push:**
```bash
# Fix issues
git add .
git commit -m "fix: resolve validation errors"
git push
```

### Testing Evidence Unclear

**Problem:** Maintainer requests clearer testing evidence

**Solution:**
1. Re-run baseline test (disable skill)
2. Capture verbatim agent response
3. Re-run compliance test (enable skill)
4. Document specific improvements
5. Update PR description with evidence

### Version Bump Incorrect

**Problem:** Merged PR created wrong version bump

**Issue:** Conventional commit type doesn't match change magnitude

**Prevention:**
- Use `feat:` for new features (minor bump)
- Use `fix:` for bug fixes (patch bump)
- Use `feat!:` for breaking changes (major bump)
- Review commit message before merge

**Sources:** [CONTRIBUTING.md:338-346](), [.github/PULL_REQUEST_TEMPLATE.md:95-104]()

---

## Summary

The contribution workflow enforces quality through mandatory testing and automated processes:

1. **Fork and branch** from `master`
2. **Make changes** following file organization guidelines
3. **Test changes** using baseline vs compliance methodology (no exceptions)
4. **Commit** with conventional commit format
5. **Submit PR** with complete testing evidence
6. **Pass validation** (automated checks)
7. **Pass review** (maintainer evaluation)
8. **Automated release** upon merge (version bump, changelog, GitHub release)

Contributors focus on **quality content and testing** - the automation handles versioning, releases, and distribution.

**Sources:** [CONTRIBUTING.md:1-381](), [.github/PULL_REQUEST_TEMPLATE.md:1-148]()

---

# Page: Automation Systems

# Automation Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/automated-release.yml](.github/workflows/automated-release.yml)
- [.github/workflows/validate.yml](.github/workflows/validate.yml)

</details>



## Purpose and Scope

This document provides an overview of the automated quality assurance and release management systems that ensure consistency and reliability of the terraform-skill codebase. The automation systems consist of two GitHub Actions workflows that handle validation and release processes.

For detailed information about specific automation workflows, see:
- Validation checks and quality gates: [Validation Workflow](#6.1)
- Release process and version management: [Release Automation](#6.2)
- Version synchronization mechanism: [Version Synchronization](#6.3)

For manual contribution processes that precede automation, see [Contribution Workflow](#5.4).

---

## System Overview

The terraform-skill repository implements a dual automation strategy:

1. **Validation System** (`.github/workflows/validate.yml`) - Quality gates for pull requests and commits
2. **Release System** (`.github/workflows/automated-release.yml`) - Automated semantic versioning and publishing

Both systems operate autonomously, requiring no manual version management or release preparation. The validation workflow ensures content quality before merge, while the release workflow automates version bumping, changelog generation, and GitHub release creation based on conventional commit messages.

**Sources:** [.github/workflows/validate.yml:1-183](), [.github/workflows/automated-release.yml:1-171]()

---

## Workflow Architecture

The following diagram illustrates the structure and responsibilities of both automation workflows:

### Automation Workflow Components

```mermaid
graph TB
    subgraph validate_yml["validate.yml Workflow"]
        validate_trigger["Trigger: PR + push to master<br/>Paths: SKILL.md, references/**, .claude-plugin/**"]
        validate_job["Job: validate"]
        
        validate_checkout["Step: Checkout"]
        validate_python["Step: Set up Python"]
        validate_deps["Step: Install Dependencies<br/>pip install pyyaml"]
        
        validate_frontmatter["Step: Check SKILL.md Frontmatter<br/>Python validation script"]
        validate_size["Step: Check File Size<br/>500 line warning threshold"]
        validate_marketplace["Step: Validate marketplace.json<br/>Python validation script"]
        validate_links["Step: Check for Broken Links<br/>Bash link checker"]
        validate_lint["Step: Lint Markdown<br/>markdownlint-cli2-action"]
        validate_summary["Step: Summary<br/>GitHub Step Summary output"]
    end
    
    subgraph release_yml["automated-release.yml Workflow"]
        release_trigger["Trigger: push to master<br/>+ workflow_dispatch"]
        release_job["Job: release"]
        
        release_checkout["Step: Checkout<br/>fetch-depth: 0 for commit history"]
        release_changelog["Step: Conventional Changelog Action<br/>TriPSs/conventional-changelog-action@v5"]
        release_sync["Step: Sync Plugin Version and SKILL.md<br/>Python sync script"]
        release_gh["Step: Create GitHub Release<br/>softprops/action-gh-release@v2"]
        release_summary["Step: Release Summary<br/>GitHub Step Summary output"]
    end
    
    validate_trigger --> validate_job
    validate_job --> validate_checkout
    validate_checkout --> validate_python
    validate_python --> validate_deps
    validate_deps --> validate_frontmatter
    validate_frontmatter --> validate_size
    validate_size --> validate_marketplace
    validate_marketplace --> validate_links
    validate_links --> validate_lint
    validate_lint --> validate_summary
    
    release_trigger --> release_job
    release_job --> release_checkout
    release_checkout --> release_changelog
    release_changelog --> release_sync
    release_sync --> release_gh
    release_gh --> release_summary
```

**Sources:** [.github/workflows/validate.yml:1-24](), [.github/workflows/validate.yml:34-183](), [.github/workflows/automated-release.yml:1-27](), [.github/workflows/automated-release.yml:34-171]()

---

## Automation Lifecycle and Triggers

This diagram shows when each automation system activates and how they interact with the development workflow:

### Automation Trigger Flow

```mermaid
graph LR
    subgraph developer["Developer Actions"]
        create_pr["Create Pull Request<br/>Modifying SKILL.md or references/"]
        push_master["Push to master branch<br/>(via merge)"]
        manual_trigger["Manual workflow_dispatch<br/>(optional)"]
    end
    
    subgraph validation["Validation Automation"]
        val_trigger["on.pull_request<br/>on.push (master)<br/>paths filter active"]
        val_execute["Execute validate job"]
        val_results["Results:<br/>✅ Pass → merge allowed<br/>❌ Fail → blocks merge"]
    end
    
    subgraph release["Release Automation"]
        rel_trigger["on.push (master)<br/>concurrency: release"]
        rel_analyze["Analyze conventional commits<br/>via fetch-depth: 0"]
        rel_decide{"New version<br/>needed?"}
        rel_execute["Execute release steps:<br/>1. Bump version<br/>2. Sync files<br/>3. Create release"]
        rel_skip["Skip release<br/>(no version bump)"]
    end
    
    create_pr --> val_trigger
    val_trigger --> val_execute
    val_execute --> val_results
    
    push_master --> val_trigger
    push_master --> rel_trigger
    manual_trigger --> rel_trigger
    
    rel_trigger --> rel_analyze
    rel_analyze --> rel_decide
    rel_decide -->|"feat/fix/BREAKING"| rel_execute
    rel_decide -->|"docs/chore/style"| rel_skip
```

**Sources:** [.github/workflows/validate.yml:3-15](), [.github/workflows/automated-release.yml:3-14](), [.github/workflows/automated-release.yml:22-49]()

---

## Key Automation Components

The following table catalogs the critical components within each workflow:

| Component | Type | File Location | Purpose |
|-----------|------|---------------|---------|
| `validate` | Job | [.github/workflows/validate.yml:18-183]() | Runs all validation checks |
| `Check SKILL.md Frontmatter` | Step | [.github/workflows/validate.yml:34-92]() | Validates YAML frontmatter structure, required fields (`name`, `description`), name pattern, and description length |
| `Check File Size` | Step | [.github/workflows/validate.yml:94-103]() | Warns if `SKILL.md` exceeds 500 lines |
| `Validate marketplace.json` | Step | [.github/workflows/validate.yml:105-151]() | Validates marketplace schema, version format, owner structure, and plugins array |
| `Check for Broken Links` | Step | [.github/workflows/validate.yml:153-166]() | Scans for broken internal references to `references/*.md` files |
| `Lint Markdown` | Step | [.github/workflows/validate.yml:168-176]() | Uses `markdownlint-cli2-action@v16` on `SKILL.md`, `references/**/*.md`, `README.md`, `CONTRIBUTING.md` |
| `release` | Job | [.github/workflows/automated-release.yml:17-171]() | Orchestrates entire release process |
| `Conventional Changelog Action` | Step | [.github/workflows/automated-release.yml:34-49]() | Uses `TriPSs/conventional-changelog-action@v5` with Angular preset to analyze commits and bump version |
| `Sync Plugin Version and SKILL.md` | Step | [.github/workflows/automated-release.yml:56-138]() | Python script that synchronizes three version fields: `marketplace.json` root, `plugins[0].version`, and `SKILL.md` metadata |
| `Create GitHub Release` | Step | [.github/workflows/automated-release.yml:142-152]() | Uses `softprops/action-gh-release@v2` to create tagged release with changelog |

**Sources:** [.github/workflows/validate.yml:18-183](), [.github/workflows/automated-release.yml:17-171]()

---

## Validation System Details

The validation workflow (`validate.yml`) implements five validation layers:

### 1. Frontmatter Validation

Python script validates YAML frontmatter in `SKILL.md`:
- Required fields: `name`, `description`
- Optional fields: `license`, `metadata.version`, `metadata.author`
- Name pattern: alphanumeric and hyphens only (`^[a-zA-Z0-9-]+$`)
- Description length limit: 1024 characters

**Sources:** [.github/workflows/validate.yml:34-92]()

### 2. File Size Monitoring

Bash script checks `SKILL.md` line and word count:
- Warning threshold: 500 lines
- Reports metrics to GitHub Actions output
- Non-blocking warning (does not fail build)

**Sources:** [.github/workflows/validate.yml:94-103]()

### 3. Marketplace Schema Validation

Python script validates `.claude-plugin/marketplace.json`:
- Marketplace-level required fields: `name`, `owner`, `version`, `plugins`
- Owner structure: must have `name` field
- Version format: semantic versioning pattern (`^\d+\.\d+\.\d+$`)
- Plugin validation: each plugin must have `name`, `description`, `source`

**Sources:** [.github/workflows/validate.yml:105-151]()

### 4. Link Integrity Checking

Bash script using `grep` and pattern matching:
- Extracts all internal links matching `[text](references/*.md)` pattern
- Verifies referenced files exist on filesystem
- Fails build if broken links detected

**Sources:** [.github/workflows/validate.yml:153-166]()

### 5. Markdown Linting

Uses `DavidAnson/markdownlint-cli2-action@v16`:
- Lints `SKILL.md`, `references/**/*.md`, `README.md`, `CONTRIBUTING.md`
- Configured with `continue-on-error: true` (warnings only)

**Sources:** [.github/workflows/validate.yml:168-176]()

---

## Release System Details

The release workflow (`automated-release.yml`) executes a four-phase release process:

### Phase 1: Conventional Commit Analysis

Uses `TriPSs/conventional-changelog-action@v5` with:
- Full git history (`fetch-depth: 0`)
- Angular commit convention preset
- Version file: `.claude-plugin/marketplace.json`
- Version path: `version` (root-level field)
- Changelog file: `CHANGELOG.md`
- Tag prefix: `v`

Commit types that trigger version bumps:
- `feat:` → minor version bump
- `fix:` → patch version bump
- `BREAKING CHANGE:` → major version bump

**Sources:** [.github/workflows/automated-release.yml:22-49]()

### Phase 2: Version Synchronization

Python script (`Sync Plugin Version and SKILL.md` step) performs three-way synchronization:

1. **Updates `marketplace.json` plugin version** at `plugins[0].version`
2. **Updates `SKILL.md` frontmatter** at `metadata.version` line
3. **Validates consistency** across all three version fields

The script amends the commit created by conventional-changelog-action to include these additional changes, maintaining a single commit for the entire release.

**Sources:** [.github/workflows/automated-release.yml:56-138]()

### Phase 3: GitHub Release Creation

Uses `softprops/action-gh-release@v2`:
- Creates release from git tag
- Populates release body with `clean_changelog` output
- Only executes if version bump occurred (`steps.changelog.outputs.skipped == 'false'`)

**Sources:** [.github/workflows/automated-release.yml:142-152]()

### Phase 4: Summary Generation

Outputs to GitHub Actions step summary:
- Version number
- Git tag
- Release URL
- Formatted changelog excerpt

**Sources:** [.github/workflows/automated-release.yml:154-170]()

---

## Workflow Permissions and Concurrency

Both workflows use strict permission and concurrency controls:

### Validation Workflow
- **Permissions:** Default (read-only for public repos)
- **Concurrency:** No restrictions (multiple PRs can validate simultaneously)
- **Triggers:** Pull requests, pushes to master/main, manual dispatch

**Sources:** [.github/workflows/validate.yml:3-15]()

### Release Workflow
- **Permissions:** `contents: write` (required for creating releases and pushing commits)
- **Concurrency:** Group `release`, `cancel-in-progress: false` (serializes releases)
- **Triggers:** Pushes to master, manual dispatch

The release workflow's concurrency control ensures only one release process runs at a time, preventing race conditions during version synchronization.

**Sources:** [.github/workflows/automated-release.yml:9-14]()

---

## File Modification Patterns

The following table shows which files each automation system reads and writes:

| File | Validation Reads | Validation Writes | Release Reads | Release Writes |
|------|-----------------|-------------------|---------------|----------------|
| `SKILL.md` | ✅ Frontmatter, size, links | ❌ | ✅ Version field | ✅ Version field |
| `references/**/*.md` | ✅ Link validation, linting | ❌ | ❌ | ❌ |
| `.claude-plugin/marketplace.json` | ✅ Schema validation | ❌ | ✅ Root version | ✅ Root + plugin version |
| `CHANGELOG.md` | ❌ | ❌ | ✅ Append mode | ✅ Generated entries |
| `README.md` | ✅ Linting only | ❌ | ❌ | ❌ |
| `CONTRIBUTING.md` | ✅ Linting only | ❌ | ❌ | ❌ |
| Git refs (tags) | ❌ | ❌ | ✅ Commit history | ✅ New tags |

**Sources:** [.github/workflows/validate.yml:5-14](), [.github/workflows/automated-release.yml:22-49](), [.github/workflows/automated-release.yml:56-138]()

---

## Integration with GitHub Features

Both workflows leverage GitHub Actions features for enhanced visibility:

### Step Summaries
- Validation: Displays pass/fail status with `$GITHUB_STEP_SUMMARY`
- Release: Shows version, tag, release URL, and changelog excerpt

### Status Checks
- Validation workflow creates required status check for PR merges
- Release workflow status visible in commit history

### Release Assets
- GitHub Releases automatically created with formatted changelogs
- Release notes populated from conventional commit messages
- Releases tagged with semantic version (`v1.2.3` format)

**Sources:** [.github/workflows/validate.yml:178-182](), [.github/workflows/automated-release.yml:154-170](), [.github/workflows/automated-release.yml:142-152]()

---

# Page: Validation Workflow

# Validation Workflow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/validate.yml](.github/workflows/validate.yml)

</details>



## Purpose and Scope

The Validation Workflow provides automated quality assurance for all skill content through GitHub Actions. It validates frontmatter structure, file sizes, configuration integrity, internal links, and markdown formatting whenever changes are proposed or merged.

This document covers the automated validation checks performed by the CI system. For manual testing methodology and the "Iron Law" of testing changes, see [Testing Methodology](#5.3). For the automated release process that runs after validation passes, see [Release Automation](#6.2). For content quality standards that inform these validations, see [Content Standards](#5.2).

**Sources:** [.github/workflows/validate.yml:1-183]()

---

## Workflow Trigger Conditions

The validation workflow runs automatically under three conditions:

| Trigger Type | Condition | Scope |
|--------------|-----------|-------|
| **Pull Request** | Any PR modifying skill content | `SKILL.md`, `references/**/*.md`, `.claude-plugin/**` |
| **Push to main/master** | Direct commits to protected branches | Same files as PR |
| **Manual Dispatch** | Developer-initiated via GitHub UI | All files |

### Trigger Diagram

```mermaid
flowchart TD
    PR["Pull Request Created/Updated"]
    PUSH["Push to master/main"]
    MANUAL["workflow_dispatch"]
    
    FILES_CHANGED{"Files Changed:<br/>SKILL.md<br/>references/**/*.md<br/>.claude-plugin/**"}
    
    WORKFLOW[".github/workflows/validate.yml<br/>Validation Job Starts"]
    
    PR --> FILES_CHANGED
    PUSH --> FILES_CHANGED
    MANUAL --> WORKFLOW
    
    FILES_CHANGED -->|"Match"| WORKFLOW
    FILES_CHANGED -->|"No Match"| SKIP["Skip Validation"]
```

**Sources:** [.github/workflows/validate.yml:3-15]()

---

## Validation Steps Overview

The workflow executes five sequential validation checks. All checks must pass for the workflow to succeed. The validation job runs on `ubuntu-latest` with Python 3.x.

```mermaid
flowchart LR
    CHECKOUT["Checkout Code<br/>actions/checkout@v4"]
    SETUP["Setup Python 3.x<br/>actions/setup-python@v5"]
    DEPS["Install Dependencies<br/>pip install pyyaml"]
    
    FM["Frontmatter Check<br/>SKILL.md frontmatter"]
    SIZE["File Size Check<br/>Line/word counts"]
    MARKET["marketplace.json Check<br/>Structure validation"]
    LINKS["Broken Links Check<br/>Internal references"]
    LINT["Markdown Linting<br/>markdownlint-cli2"]
    
    SUMMARY["Generate Summary<br/>GITHUB_STEP_SUMMARY"]
    
    CHECKOUT --> SETUP --> DEPS
    DEPS --> FM --> SIZE --> MARKET --> LINKS --> LINT --> SUMMARY
```

**Sources:** [.github/workflows/validate.yml:17-183]()

---

## Frontmatter Validation

### Purpose

Validates that `SKILL.md` contains valid YAML frontmatter with required metadata fields. This ensures Claude can properly discover and activate the skill.

### Validation Logic

The frontmatter check executes an inline Python script that performs four validations:

| Check | Requirement | Error Message |
|-------|-------------|---------------|
| **Presence** | File starts with `---` | "No frontmatter found" |
| **Format** | Properly delimited YAML block | "Invalid frontmatter format" |
| **Required Fields** | Must contain `name` and `description` | "Missing required fields: {missing}" |
| **Name Format** | Alphanumeric and hyphens only | "Invalid name: {name}" |
| **Description Length** | Maximum 1024 characters | "Description too long: {desc_len} chars" |

### Optional Fields

The validator recognizes but does not require these optional fields:

- `license` - Displayed in validation output if present
- `metadata.version` - Logged for informational purposes
- `metadata.author` - Logged for informational purposes

### Implementation Details

```mermaid
flowchart TD
    READ["Read SKILL.md Content"]
    
    CHECK_START{"Starts with<br/>'---'?"}
    CHECK_SPLIT{"Split produces<br/>3 parts?"}
    PARSE_YAML["Parse YAML<br/>yaml.safe_load()"]
    
    CHECK_REQ{"Required fields:<br/>name, description"}
    CHECK_NAME{"Name matches<br/>[a-zA-Z0-9-]+"}
    CHECK_DESC{"Description <= 1024 chars"}
    
    LOG_OPTIONAL["Log Optional Fields<br/>license, metadata.*"]
    SUCCESS["✅ Frontmatter valid"]
    
    ERROR1["❌ No frontmatter"]
    ERROR2["❌ Invalid format"]
    ERROR3["❌ Missing fields"]
    ERROR4["❌ Invalid name"]
    ERROR5["❌ Description too long"]
    
    READ --> CHECK_START
    CHECK_START -->|No| ERROR1
    CHECK_START -->|Yes| CHECK_SPLIT
    CHECK_SPLIT -->|No| ERROR2
    CHECK_SPLIT -->|Yes| PARSE_YAML
    
    PARSE_YAML --> CHECK_REQ
    CHECK_REQ -->|Missing| ERROR3
    CHECK_REQ -->|OK| CHECK_NAME
    CHECK_NAME -->|Invalid| ERROR4
    CHECK_NAME -->|Valid| CHECK_DESC
    CHECK_DESC -->|Too Long| ERROR5
    CHECK_DESC -->|OK| LOG_OPTIONAL
    LOG_OPTIONAL --> SUCCESS
```

**Sources:** [.github/workflows/validate.yml:34-92]()

---

## File Size Checks

### Purpose

Monitors `SKILL.md` size to maintain token efficiency. While not a hard limit, size warnings encourage keeping the core skill content concise per the progressive disclosure architecture (see [Progressive Disclosure Pattern](#3.2)).

### Validation Thresholds

| Metric | Command | Guideline | Action on Exceed |
|--------|---------|-----------|------------------|
| **Lines** | `wc -l < SKILL.md` | < 500 lines | ⚠️ Warning (non-blocking) |
| **Words** | `wc -w < SKILL.md` | ~1,500 words | Informational only |

### Output Format

```bash
📊 SKILL.md: 450 lines, 3200 words
✅ Size OK
```

Or when exceeding guideline:

```bash
📊 SKILL.md: 650 lines, 4800 words
⚠️ WARNING: 650 lines (guideline: <500)
```

**Note:** This check always succeeds; it never blocks merges. It serves as a developer reminder to consider moving content to `references/*.md` files.

**Sources:** [.github/workflows/validate.yml:94-103]()

---

## marketplace.json Validation

### Purpose

Ensures the plugin definition file has correct structure for Claude Code integration. This is critical since `marketplace.json` is the entry point for skill discovery (importance: 28.17).

### Validation Hierarchy

```mermaid
graph TB
    ROOT["marketplace.json Root"]
    
    REQ_MARKET["Required Marketplace Fields:<br/>name, owner, version, plugins"]
    
    OWNER["owner Object"]
    OWNER_NAME["owner.name Required"]
    
    VERSION["version Field"]
    VERSION_FORMAT["Format: X.Y.Z<br/>Regex: ^\d+\.\d+\.\d+$"]
    
    PLUGINS["plugins Array"]
    PLUGINS_NONEMPTY["Must be non-empty"]
    
    PLUGIN["Each Plugin Object"]
    PLUGIN_FIELDS["Required Fields:<br/>name, description, source"]
    
    ROOT --> REQ_MARKET
    ROOT --> OWNER
    ROOT --> VERSION
    ROOT --> PLUGINS
    
    OWNER --> OWNER_NAME
    VERSION --> VERSION_FORMAT
    PLUGINS --> PLUGINS_NONEMPTY
    PLUGINS --> PLUGIN
    PLUGIN --> PLUGIN_FIELDS
```

### Validation Rules

| Level | Check | Requirement | Error Code |
|-------|-------|-------------|------------|
| **Marketplace** | Required fields | `name`, `owner`, `version`, `plugins` present | "Missing marketplace fields" |
| **Owner** | Structure | `owner.name` must exist | "owner must have 'name'" |
| **Version** | Format | Semantic versioning: `\d+\.\d+\.\d+` | "Invalid marketplace version" |
| **Plugins** | Array validity | Non-empty array | "'plugins' must be a non-empty array" |
| **Plugin** | Required fields | Each plugin has `name`, `description`, `source` | "Plugin {idx} missing fields" |

### Success Output

```
✅ marketplace.json valid (v2.1.0, 1 plugin(s))
```

**Sources:** [.github/workflows/validate.yml:105-151]()

---

## Link Validation

### Purpose

Detects broken internal references to ensure all `references/*.md` links in skill content resolve to actual files. Prevents 404 errors when Claude attempts to load reference documentation.

### Link Detection Algorithm

```mermaid
flowchart TD
    GREP["grep -oP '\[.*?\]\(references/.*?\.md.*?\)'<br/>Extract markdown links"]
    
    PARSE_FILES["Parse files:<br/>SKILL.md<br/>references/*.md"]
    
    SED1["sed 's/.*(//'<br/>Remove text before ("]
    SED2["sed 's/).*//'<br/>Remove ) and after"]
    SED3["sed 's/#.*//'<br/>Remove anchor fragments"]
    
    LOOP["For each link path"]
    
    CHECK_FILE{"File exists?"}
    
    ERROR["❌ Broken link: {link}<br/>exit 1"]
    SUCCESS["✅ No broken links"]
    
    GREP --> PARSE_FILES
    PARSE_FILES --> SED1
    SED1 --> SED2
    SED2 --> SED3
    SED3 --> LOOP
    
    LOOP --> CHECK_FILE
    CHECK_FILE -->|No| ERROR
    CHECK_FILE -->|Yes| LOOP
    LOOP -->|Complete| SUCCESS
```

### Link Pattern Matching

The regex pattern `\[.*?\]\(references/.*?\.md.*?\)` matches:
- `[Module Patterns](references/module-patterns.md)` → validates `references/module-patterns.md`
- `[Quick Ref](references/quick-reference.md#testing)` → validates `references/quick-reference.md` (anchor ignored)

**Does not validate:**
- External URLs (`https://...`)
- Relative links not starting with `references/`
- Anchor-only links (`#section`)

**Sources:** [.github/workflows/validate.yml:153-166]()

---

## Markdown Linting

### Purpose

Enforces consistent markdown formatting across all documentation files using `markdownlint-cli2`. This check is informational and does not block merges (`continue-on-error: true`).

### Validated Files

| File Pattern | Purpose |
|--------------|---------|
| `SKILL.md` | Core skill content |
| `references/**/*.md` | Reference documentation |
| `README.md` | User documentation |
| `CONTRIBUTING.md` | Contributor guidelines |

### Linter Configuration

The workflow uses the GitHub Action `DavidAnson/markdownlint-cli2-action@v16` with default rules. Common issues flagged:

- Inconsistent heading styles
- Missing blank lines around code blocks
- Trailing whitespace
- Line length violations
- List formatting inconsistencies

### Non-Blocking Behavior

```yaml
continue-on-error: true
```

This setting means linting failures generate warnings but do not prevent the workflow from succeeding. This allows content changes to merge while encouraging formatting improvements.

**Sources:** [.github/workflows/validate.yml:168-176]()

---

## Validation Summary and Reporting

### GitHub Step Summary

Upon successful completion of all checks, the workflow generates a formatted summary visible in the GitHub Actions UI:

```markdown
## ✅ Validation Passed
All skill validation checks passed.
```

This summary is appended to `$GITHUB_STEP_SUMMARY`, making validation results immediately visible in the Actions tab without expanding individual steps.

### Failure Handling

If any validation check fails (except markdown linting):
1. The Python script calls `sys.exit(1)` or the shell command returns non-zero
2. Subsequent steps are skipped
3. The workflow status is marked as "Failed"
4. PR merge is blocked until issues are resolved

### Validation Status Flow

```mermaid
stateDiagram-v2
    [*] --> Running: Workflow Triggered
    
    Running --> CheckFrontmatter: Step 1
    CheckFrontmatter --> CheckSize: Pass
    CheckFrontmatter --> Failed: Fail
    
    CheckSize --> CheckMarketplace: Pass
    CheckSize --> Failed: Fail
    
    CheckMarketplace --> CheckLinks: Pass
    CheckMarketplace --> Failed: Fail
    
    CheckLinks --> LintMarkdown: Pass
    CheckLinks --> Failed: Fail
    
    LintMarkdown --> Success: Always Continue
    
    Success --> [*]: Generate Summary
    Failed --> [*]: Block Merge
```

**Sources:** [.github/workflows/validate.yml:178-183]()

---

## Technical Dependencies

### GitHub Actions

| Action | Version | Purpose |
|--------|---------|---------|
| `actions/checkout@v4` | v4 | Check out repository code |
| `actions/setup-python@v5` | v5 | Install Python 3.x runtime |
| `DavidAnson/markdownlint-cli2-action@v16` | v16 | Markdown linting |

### Python Dependencies

```bash
pip install pyyaml
```

The `pyyaml` library is used for safe YAML parsing in frontmatter validation. No other Python dependencies are required.

### Shell Utilities

Standard Unix utilities used:
- `wc` - Word and line counting
- `grep` - Pattern matching with Perl regex (`-oP`)
- `sed` - Stream editing for link extraction
- `[ -f ]` - File existence testing

**Sources:** [.github/workflows/validate.yml:22-32]()

---

## Integration with Development Workflow

### Pre-Merge Gates

The validation workflow integrates with GitHub's branch protection rules. When configured as a required check, it enforces that:

1. All PRs must pass validation before merge
2. Direct commits to `master/main` are validated post-merge
3. Failed validations prevent release automation from triggering

### Relationship to Other Workflows

```mermaid
flowchart LR
    PR["Pull Request"]
    VALIDATE[".github/workflows/validate.yml<br/>Validation Workflow"]
    MERGE["Merge to master"]
    RELEASE[".github/workflows/automated-release.yml<br/>Release Workflow"]
    
    PR --> VALIDATE
    VALIDATE -->|"✅ Pass"| MERGE
    VALIDATE -->|"❌ Fail"| BLOCK["Block Merge"]
    
    MERGE --> RELEASE
    
    RELEASE -.->|"Updates versions in"| FILES["SKILL.md<br/>marketplace.json"]
    FILES -.->|"Triggers"| VALIDATE
```

This creates a validation cycle:
1. **Pre-merge:** Developer changes trigger validation
2. **Post-merge:** Release automation updates trigger re-validation
3. **Continuous:** Manual dispatches allow on-demand validation

**Sources:** [.github/workflows/validate.yml:3-15](), Diagram 3 from system architecture

---

## Common Validation Failures

### Frontmatter Issues

**Missing Required Fields:**
```yaml
---
name: terraform-skill
# ERROR: Missing 'description'
---
```

**Invalid Name Format:**
```yaml
---
name: terraform skill  # ERROR: Contains space
description: "Terraform expertise"
---
```

### marketplace.json Issues

**Invalid Version:**
```json
{
  "version": "2.1",  // ERROR: Must be X.Y.Z
  "name": "terraform-skill"
}
```

**Missing Plugin Fields:**
```json
{
  "plugins": [
    {
      "name": "terraform-skill"
      // ERROR: Missing 'description' and 'source'
    }
  ]
}
```

### Broken Links

```markdown
See [Module Patterns](references/module-pattern.md)
                                          ^
                                          ERROR: File is module-patterns.md
```

**Sources:** [.github/workflows/validate.yml:34-166]()

---

## Validation Workflow File Structure

### Complete Step Mapping

| Step Name | Lines | Validation Type | Blocking? |
|-----------|-------|-----------------|-----------|
| Checkout | 23-24 | Setup | N/A |
| Set up Python | 26-29 | Setup | N/A |
| Install Dependencies | 31-32 | Setup | N/A |
| Check SKILL.md Frontmatter | 34-92 | Content | Yes |
| Check File Size | 94-103 | Content | No (warning only) |
| Validate marketplace.json | 105-151 | Configuration | Yes |
| Check for Broken Links | 153-166 | Content | Yes |
| Lint Markdown | 168-176 | Formatting | No (continue-on-error) |
| Summary | 178-183 | Reporting | N/A |

**Sources:** [.github/workflows/validate.yml:1-183]()

---

# Page: Release Automation

# Release Automation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/automated-release.yml](.github/workflows/automated-release.yml)
- [CHANGELOG.md](CHANGELOG.md)

</details>



## Purpose and Scope

This document describes the automated release process implemented in [.github/workflows/automated-release.yml](), which handles semantic versioning, changelog generation, and GitHub release creation. The workflow analyzes conventional commits to determine version bumps, updates version metadata across multiple files, generates release notes, and publishes releases—all without manual intervention.

For details on how versions are synchronized across `marketplace.json`, `SKILL.md`, and git tags, see [Version Synchronization](#6.3). For pre-release validation checks, see [Validation Workflow](#6.1).

---

## Workflow Architecture

The `automated-release.yml` workflow executes on every push to the `master` branch and can be manually triggered via `workflow_dispatch`. It uses concurrency control to prevent simultaneous releases and requires `contents: write` permissions to create tags and releases.

**Workflow Trigger Configuration**

```mermaid
graph LR
    subgraph "Trigger Events"
        PUSH["push to master branch"]
        MANUAL["workflow_dispatch"]
    end
    
    subgraph "Concurrency Control"
        LOCK["concurrency: release<br/>cancel-in-progress: false"]
    end
    
    subgraph "Permissions"
        PERMS["contents: write"]
    end
    
    PUSH --> LOCK
    MANUAL --> LOCK
    LOCK --> PERMS
    PERMS --> WORKFLOW["automated-release.yml job"]
```

Sources: [.github/workflows/automated-release.yml:3-14]()

---

## Release Process Overview

The release workflow consists of five sequential steps that transform conventional commits into a published GitHub release:

**End-to-End Release Flow**

```mermaid
flowchart TD
    START["Merge to master"]
    
    subgraph "Step 1: Checkout"
        CHECKOUT["actions/checkout@v6<br/>fetch-depth: 0"]
    end
    
    subgraph "Step 2: Conventional Changelog"
        ANALYZE["Analyze commit history<br/>conventional-changelog-action@v5"]
        CALC_VERSION["Calculate semantic version<br/>preset: angular"]
        UPDATE_FILES["Update CHANGELOG.md<br/>Update marketplace.json root version"]
        CREATE_TAG["Create git tag"]
        COMMIT_PUSH["Git commit and push"]
    end
    
    subgraph "Step 3: Sync Versions"
        PYTHON_SYNC["Python script execution"]
        SYNC_PLUGIN["Update plugins[0].version"]
        SYNC_SKILL["Update SKILL.md metadata.version"]
        VALIDATE_SYNC["Validate all 3 versions match"]
        AMEND_COMMIT["Git commit --amend<br/>force-with-lease push"]
    end
    
    subgraph "Step 4: GitHub Release"
        CREATE_RELEASE["softprops/action-gh-release@v2"]
        ATTACH_CHANGELOG["Attach clean changelog body"]
    end
    
    subgraph "Step 5: Summary"
        SUMMARY["Generate GITHUB_STEP_SUMMARY"]
    end
    
    START --> CHECKOUT
    CHECKOUT --> ANALYZE
    ANALYZE --> CALC_VERSION
    CALC_VERSION --> UPDATE_FILES
    UPDATE_FILES --> CREATE_TAG
    CREATE_TAG --> COMMIT_PUSH
    COMMIT_PUSH --> PYTHON_SYNC
    PYTHON_SYNC --> SYNC_PLUGIN
    SYNC_PLUGIN --> SYNC_SKILL
    SYNC_SKILL --> VALIDATE_SYNC
    VALIDATE_SYNC --> AMEND_COMMIT
    AMEND_COMMIT --> CREATE_RELEASE
    CREATE_RELEASE --> ATTACH_CHANGELOG
    ATTACH_CHANGELOG --> SUMMARY
```

Sources: [.github/workflows/automated-release.yml:21-171]()

---

## Conventional Commits as Version Drivers

The workflow uses the **Angular commit convention** preset to determine version bumps. Commit messages must follow the pattern `<type>(<scope>): <description>` to trigger version changes.

**Commit Type to Version Bump Mapping**

| Commit Type | Version Component | Example | Result |
|-------------|-------------------|---------|--------|
| `feat:` or `feat!:` | Minor (x.Y.z) | `feat: Add module patterns` | 1.4.0 → 1.5.0 |
| `fix:` | Patch (x.y.Z) | `fix: Correct validation` | 1.4.0 → 1.4.1 |
| `feat!:` or `BREAKING CHANGE:` | Major (X.y.z) | `feat!: Remove plugin.json` | 1.4.0 → 2.0.0 |
| `docs:`, `chore:`, `refactor:` | None | `docs: Update README` | No release |

**Version Calculation Flow**

```mermaid
graph TD
    COMMITS["Git commit history<br/>since last tag"]
    
    subgraph "Commit Analysis"
        PARSE["Parse conventional commits<br/>preset: angular"]
        BREAKING["Check for BREAKING CHANGE:<br/>or ! suffix"]
        FEAT["Count feat: commits"]
        FIX["Count fix: commits"]
    end
    
    subgraph "Version Bump Decision"
        MAJOR["Bump MAJOR<br/>X.y.z"]
        MINOR["Bump MINOR<br/>x.Y.z"]
        PATCH["Bump PATCH<br/>x.y.Z"]
        SKIP["Skip release<br/>skip-on-empty: false"]
    end
    
    COMMITS --> PARSE
    PARSE --> BREAKING
    PARSE --> FEAT
    PARSE --> FIX
    
    BREAKING -->|Found| MAJOR
    BREAKING -->|None| FEAT
    FEAT -->|Found| MINOR
    FEAT -->|None| FIX
    FIX -->|Found| PATCH
    FIX -->|None| SKIP
    
    MAJOR --> VERSION["New version number"]
    MINOR --> VERSION
    PATCH --> VERSION
```

Sources: [.github/workflows/automated-release.yml:42-49]()

---

## Step-by-Step Workflow Execution

### Step 1: Repository Checkout

The workflow checks out the repository with full commit history (`fetch-depth: 0`) to enable conventional commit analysis across all tags.

```yaml
- name: Checkout
  uses: actions/checkout@v6
  with:
    fetch-depth: 0
```

Sources: [.github/workflows/automated-release.yml:23-26]()

### Step 2: Conventional Changelog Action

The `TriPSs/conventional-changelog-action@v5` performs multiple operations:

**Configuration Parameters**

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `preset` | `angular` | Commit convention parser |
| `tag-prefix` | `v` | Prepends 'v' to semantic version |
| `output-file` | `CHANGELOG.md` | Changelog file location |
| `version-file` | `./.claude-plugin/marketplace.json` | Version source file |
| `version-path` | `version` | JSON path to version field |
| `skip-on-empty` | `false` | Create release even if no changelog changes |
| `skip-version-file` | `false` | Update version file |
| `skip-commit` | `false` | Create commit and tag |

**Outputs**

The action sets output variables used by subsequent steps:

- `steps.changelog.outputs.version` - Calculated semantic version (e.g., `1.5.0`)
- `steps.changelog.outputs.tag` - Git tag with prefix (e.g., `v1.5.0`)
- `steps.changelog.outputs.clean_changelog` - Markdown changelog content
- `steps.changelog.outputs.skipped` - Boolean indicating if release was skipped

Sources: [.github/workflows/automated-release.yml:34-49]()

### Step 3: Version Synchronization

After the conventional-changelog-action updates the root `version` field in `marketplace.json` and creates a tag, a Python script synchronizes two additional version locations. This step only executes if `steps.changelog.outputs.skipped == 'false'`.

**Version Synchronization Script Flow**

```mermaid
graph TD
    ENV["Environment variable<br/>VERSION from step 2"]
    
    subgraph "Python Script Execution"
        READ_MP["Read marketplace.json"]
        VALIDATE_STRUCT["Validate plugins array exists"]
        SYNC_PLUGIN["Set plugins[0].version = VERSION"]
        VALIDATE_ROOT["Verify root version == VERSION"]
        WRITE_MP["Write marketplace.json"]
        
        READ_SKILL["Read SKILL.md"]
        FIND_VERSION["Find 'version:' in frontmatter<br/>within first 10 lines"]
        UPDATE_VERSION["Update to VERSION"]
        WRITE_SKILL["Write SKILL.md"]
        
        REPORT["Print sync summary"]
    end
    
    subgraph "Git Operations"
        GIT_ADD["git add marketplace.json SKILL.md"]
        GIT_AMEND["git commit --amend --no-edit"]
        GIT_PUSH["git push --force-with-lease"]
    end
    
    ENV --> READ_MP
    READ_MP --> VALIDATE_STRUCT
    VALIDATE_STRUCT --> SYNC_PLUGIN
    SYNC_PLUGIN --> VALIDATE_ROOT
    VALIDATE_ROOT --> WRITE_MP
    WRITE_MP --> READ_SKILL
    READ_SKILL --> FIND_VERSION
    FIND_VERSION --> UPDATE_VERSION
    UPDATE_VERSION --> WRITE_SKILL
    WRITE_SKILL --> REPORT
    REPORT --> GIT_ADD
    GIT_ADD --> GIT_AMEND
    GIT_AMEND --> GIT_PUSH
```

**SKILL.md Version Update Logic**

The script locates the version field in the YAML frontmatter by searching for lines matching `version:` within the first 10 lines and updates the value with 2-space indentation:

```python
# Match "  version: X.Y.Z" pattern (2 spaces indent)
if line.strip().startswith('version:') and i < 10:
    lines[i] = f'  version: {version}\n'
    updated = True
    break
```

The script uses `git commit --amend` to incorporate version sync changes into the same commit created by the conventional-changelog-action, maintaining a clean git history with a single commit per release.

Sources: [.github/workflows/automated-release.yml:56-138]()

### Step 4: GitHub Release Creation

The `softprops/action-gh-release@v2` action creates a GitHub release using the tag and changelog generated by step 2. This step is conditional on `steps.changelog.outputs.skipped == 'false'`.

**Release Configuration**

```yaml
- name: Create GitHub Release
  uses: softprops/action-gh-release@v2
  with:
    tag_name: ${{ steps.changelog.outputs.tag }}
    name: ${{ steps.changelog.outputs.tag }}
    body: ${{ steps.changelog.outputs.clean_changelog }}
    draft: false
    prerelease: false
```

The release is published immediately (not draft) and marked as a stable release (not prerelease).

Sources: [.github/workflows/automated-release.yml:142-152]()

### Step 5: Workflow Summary

The final step generates a human-readable summary in `GITHUB_STEP_SUMMARY` that appears in the GitHub Actions UI:

```markdown
## Release Summary

✅ **Version:** 1.5.0
✅ **Tag:** v1.5.0
✅ **Release:** https://github.com/antonbabenko/terraform-skill/releases/tag/v1.5.0

### Changelog
<clean_changelog content>
```

Sources: [.github/workflows/automated-release.yml:155-170]()

---

## Changelog Generation

The `CHANGELOG.md` file is automatically generated and maintained by the conventional-changelog-action. It organizes commits by version and type:

**Changelog Structure**

```mermaid
graph TD
    subgraph "CHANGELOG.md"
        VERSION["# [X.Y.Z] (date)<br/>compare/vOLD...vNEW"]
        
        subgraph "Sections by Type"
            BREAKING["### BREAKING CHANGES"]
            FEATURES["### Features"]
            FIXES["### Bug Fixes"]
            DOCS["### Documentation"]
        end
        
        subgraph "Commit Entries"
            ENTRY1["* commit subject (hash)"]
            ENTRY2["* commit subject closes #issue"]
        end
    end
    
    VERSION --> BREAKING
    VERSION --> FEATURES
    VERSION --> FIXES
    VERSION --> DOCS
    
    FEATURES --> ENTRY1
    FIXES --> ENTRY2
```

**Example Changelog Entry**

The CHANGELOG.md file shows actual release entries:

```markdown
# [1.5.0](compare/v1.0.0...v1.5.0) (2026-01-19)

### Bug Fixes
* Allow optional frontmatter fields (e4393cb), closes #21146856119
* **changelog:** prevent regeneration from losing releases (b81b57d)

### Features
* Added plugin install command to docs (c400b18)
* Enhance skill with comprehensive best practices (f32fc3b)
```

Sources: [CHANGELOG.md:1-17](), [.github/workflows/automated-release.yml:44]()

---

## Workflow Outputs and Integration

The workflow produces several artifacts and state changes:

**Release Artifacts**

| Artifact | Location | Purpose |
|----------|----------|---------|
| Git Tag | `refs/tags/v{version}` | Version reference point |
| Git Commit | `master` branch | Version bump commit |
| Changelog | `CHANGELOG.md` | Human-readable history |
| GitHub Release | Releases page | Published release with notes |
| marketplace.json | Root & plugins[0] | Version metadata |
| SKILL.md | Frontmatter metadata | Skill version |

**Error Handling**

The Python synchronization script includes error handling for common failure modes:

- Missing `SKILL.md` file: `FileNotFoundError`
- Invalid marketplace.json structure: `ValueError("No plugins found")`
- Version mismatch: `ValueError("Marketplace version != VERSION")`
- Missing version field in SKILL.md: `ValueError("Could not find version field")`

All errors cause immediate workflow failure with descriptive messages.

Sources: [.github/workflows/automated-release.yml:128-130]()

---

## Historical Context

The workflow has evolved through several iterations:

1. **v1.0.0**: Initial marketplace migration, establishing version synchronization across three locations
2. **v1.5.0**: Fixed changelog regeneration bug that lost intermediate releases, reverted to `conventional-changelog-action@v5` due to tag detection issues in v6

The changelog shows the workflow's own evolution:

```markdown
### Bug Fixes
* **changelog:** prevent regeneration from losing intermediate releases (b81b57d)
* revert conventional-changelog-action to v5 due to tag detection bug (9ba8215)
```

Sources: [CHANGELOG.md:7-8]()

---

# Page: Version Synchronization

# Version Synchronization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/automated-release.yml](.github/workflows/automated-release.yml)
- [CHANGELOG.md](CHANGELOG.md)

</details>



## Purpose and Scope

This document describes the three-way version synchronization mechanism that keeps version identifiers consistent across `.claude-plugin/marketplace.json`, `SKILL.md` metadata, and Git tags. This synchronization is critical for ensuring Claude Code can properly resolve and load the skill at the correct version.

For information about the automated release workflow that triggers this synchronization, see [Release Automation](#6.2). For details on marketplace.json structure and validation, see [Plugin Definition System](#3.1).

---

## Version Synchronization Architecture

The terraform-skill repository maintains version consistency across three distinct locations, each serving a different purpose in the Claude Code plugin ecosystem.

### Version Location Diagram

```mermaid
graph TD
    subgraph "Version Sources"
        CC["Conventional Commits<br/>(feat:, fix:, etc.)"]
    end
    
    subgraph "marketplace.json"
        ROOT_V["root.version<br/>(line 2)"]
        PLUGIN_V["plugins[0].version<br/>(nested field)"]
    end
    
    subgraph "SKILL.md"
        META_V["metadata.version<br/>(frontmatter, ~line 7)"]
    end
    
    subgraph "Git"
        GIT_TAG["Git Tag<br/>(e.g., v1.5.0)"]
    end
    
    CC -->|"conventional-changelog-action"| ROOT_V
    ROOT_V -->|"Python sync script"| PLUGIN_V
    ROOT_V -->|"Python sync script"| META_V
    ROOT_V -->|"conventional-changelog-action"| GIT_TAG
    
    ROOT_V -.->|"Validation check"| PLUGIN_V
    ROOT_V -.->|"Validation check"| META_V
    ROOT_V -.->|"Validation check"| GIT_TAG
```

**Sources:** [.github/workflows/automated-release.yml:34-50](), [.github/workflows/automated-release.yml:56-131]()

---

## Version Fields Reference

| Location | Field Path | Purpose | Updated By | Example |
|----------|-----------|---------|------------|---------|
| `.claude-plugin/marketplace.json` | `version` (root) | Primary version identifier for marketplace | `conventional-changelog-action` | `1.5.0` |
| `.claude-plugin/marketplace.json` | `plugins[0].version` | Plugin-specific version | Python sync script | `1.5.0` |
| `SKILL.md` | `metadata.version` (YAML frontmatter) | Skill content version | Python sync script | `1.5.0` |
| Git repository | Tag (e.g., `v1.5.0`) | Version control reference | `conventional-changelog-action` | `v1.5.0` |

**Sources:** [.github/workflows/automated-release.yml:45-46](), [.github/workflows/automated-release.yml:105](), [.github/workflows/automated-release.yml:118]()

---

## Synchronization Process

The version synchronization occurs automatically during the release workflow when changes are pushed to the `master` branch.

### Synchronization Sequence

```mermaid
sequenceDiagram
    participant Commit as "Git Push to master"
    participant Workflow as "automated-release.yml"
    participant CCA as "conventional-changelog-action"
    participant Sync as "Sync Plugin Version Script"
    participant Files as "File System"
    participant Git as "Git Repository"
    
    Commit->>Workflow: Trigger on push
    Workflow->>CCA: Step 2: Conventional Changelog
    CCA->>Files: Analyze conventional commits
    CCA->>Files: Calculate new version
    CCA->>Files: Update marketplace.json root.version
    CCA->>Files: Generate CHANGELOG.md
    CCA->>Git: Create git tag (e.g., v1.5.0)
    CCA->>Git: Commit changes
    CCA->>Workflow: Output: version, tag, skipped
    
    Workflow->>Sync: Step 2b: Sync Plugin Version (if not skipped)
    Sync->>Files: Read marketplace.json
    Sync->>Files: Update plugins[0].version
    Sync->>Files: Read SKILL.md
    Sync->>Files: Update metadata.version in frontmatter
    Sync->>Files: Validate all versions match
    Sync->>Git: Amend commit with synced versions
    Sync->>Git: Force push with lease
    
    Workflow->>Git: Step 3: Create GitHub Release
```

**Sources:** [.github/workflows/automated-release.yml:22-50](), [.github/workflows/automated-release.yml:56-138]()

---

## Version Update Implementation

### Step 1: Primary Version Update

The `conventional-changelog-action` analyzes commit messages following the Angular preset and determines the version bump type:

- `feat:` commits → Minor version bump (1.4.0 → 1.5.0)
- `fix:` commits → Patch version bump (1.4.0 → 1.4.1)
- `BREAKING CHANGE:` footer or `!` → Major version bump (1.4.0 → 2.0.0)

The action updates the root `version` field in `.claude-plugin/marketplace.json`:

```yaml
version-file: './.claude-plugin/marketplace.json'
version-path: 'version'
```

**Sources:** [.github/workflows/automated-release.yml:45-46](), [.github/workflows/automated-release.yml:42]()

### Step 2: Plugin Version Synchronization

After the primary version is updated, a Python script synchronizes the remaining version fields:

```mermaid
flowchart TD
    Start["Step 2b: Sync Plugin Version and SKILL.md"]
    CheckSkip{{"steps.changelog.outputs.skipped == 'false'"}}
    ReadEnv["Read VERSION from environment"]
    ReadMarketplace["Read .claude-plugin/marketplace.json"]
    ValidatePlugins{"plugins array exists and non-empty?"}
    UpdatePlugin["data['plugins'][0]['version'] = version"]
    ValidateRoot{"data['version'] == version?"}
    WriteMarketplace["Write marketplace.json"]
    
    ReadSkill["Read SKILL.md lines"]
    FindVersion["Find version: line in frontmatter (line < 10)"]
    UpdateSkill["lines[i] = f'  version: {version}\n'"]
    WriteSkill["Write SKILL.md"]
    
    PrintSummary["Print version sync summary:<br/>- marketplace.json root<br/>- marketplace.json plugins[0]<br/>- SKILL.md metadata"]
    
    GitAdd["git add marketplace.json SKILL.md"]
    GitAmend["git commit --amend --no-edit"]
    GitPush["git push --force-with-lease"]
    
    End["Continue to GitHub Release"]
    Error["Exit with error code 1"]
    
    Start --> CheckSkip
    CheckSkip -->|false - version was bumped| ReadEnv
    CheckSkip -->|true - no changes| End
    ReadEnv --> ReadMarketplace
    ReadMarketplace --> ValidatePlugins
    ValidatePlugins -->|No| Error
    ValidatePlugins -->|Yes| UpdatePlugin
    UpdatePlugin --> ValidateRoot
    ValidateRoot -->|No| Error
    ValidateRoot -->|Yes| WriteMarketplace
    WriteMarketplace --> ReadSkill
    ReadSkill --> FindVersion
    FindVersion --> UpdateSkill
    UpdateSkill --> WriteSkill
    WriteSkill --> PrintSummary
    PrintSummary --> GitAdd
    GitAdd --> GitAmend
    GitAmend --> GitPush
    GitPush --> End
```

**Sources:** [.github/workflows/automated-release.yml:56-138]()

### Update Logic Details

The Python synchronization script performs the following operations:

#### Marketplace.json Plugin Version Update

```python
# Read current marketplace.json
with open('.claude-plugin/marketplace.json', 'r') as f:
    data = json.load(f)

# Update plugins[0].version
data['plugins'][0]['version'] = version

# Validate root version matches (already updated by conventional-changelog-action)
if data['version'] != version:
    raise ValueError(f"Marketplace version {data['version']} != {version}")
```

**Sources:** [.github/workflows/automated-release.yml:96-113]()

#### SKILL.md Metadata Version Update

The script updates the YAML frontmatter version field (typically on line 7):

```python
# Find and update version line in frontmatter
for i, line in enumerate(lines):
    # Match "  version: X.Y.Z" pattern (2 spaces indent)
    if line.strip().startswith('version:') and i < 10:  # Within frontmatter
        lines[i] = f'  version: {version}\n'
        updated = True
        break
```

**Sources:** [.github/workflows/automated-release.yml:66-91]()

---

## Validation and Error Handling

The synchronization process includes multiple validation checkpoints to ensure data integrity.

### Validation Checkpoints

| Checkpoint | Location | Condition | Failure Action |
|------------|----------|-----------|----------------|
| Plugins array exists | Python script | `'plugins' in data and len(data['plugins']) > 0` | Raise ValueError, exit 1 |
| Root version matches | Python script | `data['version'] == version` | Raise ValueError, exit 1 |
| SKILL.md version field found | Python script | Version line found within first 10 lines | Raise ValueError, exit 1 |
| Git amend successful | Bash | `git commit --amend` exit code 0 | Workflow fails |
| Git push successful | Bash | `git push --force-with-lease` exit code 0 | Workflow fails |

**Sources:** [.github/workflows/automated-release.yml:100-102](), [.github/workflows/automated-release.yml:108-109](), [.github/workflows/automated-release.yml:85-86]()

### Error Messages

The script outputs structured error messages with contextual information:

```python
except Exception as e:
    print(f"❌ ERROR: Failed to sync versions: {e}")
    sys.exit(1)
```

**Sources:** [.github/workflows/automated-release.yml:128-130]()

---

## Git Commit Strategy

The synchronization uses an amend-and-force-push strategy to maintain a clean commit history.

### Commit Amendment Process

```mermaid
graph LR
    Initial["Initial commit by<br/>conventional-changelog-action<br/>(marketplace.json root, CHANGELOG.md, tag)"]
    Stage["Stage additional changes<br/>git add marketplace.json SKILL.md"]
    Amend["Amend previous commit<br/>git commit --amend --no-edit"]
    Push["Force push with lease<br/>git push --force-with-lease"]
    
    Initial --> Stage
    Stage --> Amend
    Amend --> Push
```

This approach ensures:
- Single commit per release (not two separate commits)
- All version changes are atomic
- Commit message remains unchanged (`chore(release): {version}`)
- Tag points to final commit with all synchronized versions

**Sources:** [.github/workflows/automated-release.yml:134-138]()

---

## Version Sync Summary Output

After successful synchronization, the workflow outputs a summary:

```
📋 Version Sync Summary:
   - marketplace.json root: 1.5.0
   - marketplace.json plugins[0]: 1.5.0
   - SKILL.md metadata: 1.5.0
   ✅ All versions synchronized to 1.5.0
```

**Sources:** [.github/workflows/automated-release.yml:122-126]()

---

## Release History Examples

The CHANGELOG.md demonstrates successful version synchronization across multiple releases:

### Version 1.5.0 Release

```markdown
# [1.5.0](https://github.com/antonbabenko/terraform-skill/compare/v1.0.0...v1.5.0) (2026-01-19)

### Bug Fixes
* Allow optional frontmatter fields in SKILL.md validation
* **changelog:** prevent regeneration from losing intermediate releases
* revert conventional-changelog-action to v5 due to tag detection bug

### Features
* Added plugin install command to docs
* Enhance skill with comprehensive best practices from original guide
```

**Sources:** [CHANGELOG.md:1-15]()

### Version 1.0.0 Release (Marketplace Migration)

The 1.0.0 release included a breaking change that established the current three-way synchronization architecture:

```markdown
### BREAKING CHANGES

* Removed plugin.json in favor of marketplace.json.

Changes:
- Migrate source type from 'local' to 'github'
- Add version synchronization (marketplace, plugin, git ref)
- Update workflows for marketplace.json validation and releases
- Update documentation references
```

**Sources:** [CHANGELOG.md:35-43]()

---

## Troubleshooting

### Version Mismatch Detection

If versions become desynchronized (e.g., due to manual edits), the validation workflow will detect the issue. See [Validation Workflow](#6.1) for details on automated validation checks.

### Manual Version Verification

To manually verify version consistency:

```bash
# Check marketplace.json root version
jq -r '.version' .claude-plugin/marketplace.json

# Check marketplace.json plugin version
jq -r '.plugins[0].version' .claude-plugin/marketplace.json

# Check SKILL.md metadata version
grep "version:" SKILL.md | head -n 1

# Check latest git tag
git describe --tags --abbrev=0
```

All four values should match (git tag includes `v` prefix).

### Recovery from Failed Synchronization

If the synchronization step fails during a release:

1. The workflow will fail and halt before creating the GitHub release
2. No tag will be created (or the tag will point to incomplete sync)
3. Investigate the error in the workflow logs at step "Sync Plugin Version and SKILL.md"
4. Fix the underlying issue (e.g., corrupted JSON, missing SKILL.md frontmatter)
5. Re-trigger the workflow via workflow_dispatch

**Sources:** [.github/workflows/automated-release.yml:7](), [.github/workflows/automated-release.yml:56-57]()

---

## Concurrency Control

The automated release workflow uses concurrency control to prevent simultaneous releases:

```yaml
concurrency:
  group: release
  cancel-in-progress: false
```

This ensures:
- Only one release workflow runs at a time
- Subsequent pushes wait for the current release to complete
- No race conditions in version synchronization

**Sources:** [.github/workflows/automated-release.yml:12-14]()

---

## Related Configuration

### Workflow Permissions

The workflow requires `contents: write` permission to:
- Amend commits with synchronized versions
- Push commits to the repository
- Create Git tags
- Create GitHub releases

**Sources:** [.github/workflows/automated-release.yml:10]()

### Conventional Changelog Configuration

The version synchronization relies on the Angular preset for conventional commits:

```yaml
preset: 'angular'
tag-prefix: 'v'
skip-version-file: 'false'
skip-commit: 'false'
```

**Sources:** [.github/workflows/automated-release.yml:42-49]()

---

# Page: Release History

# Release History

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)

</details>



This document provides a complete version history of the terraform-skill project, documenting all releases, features, bug fixes, and breaking changes. The changelog is automatically generated by the [automated-release workflow](#6.2) using conventional commit analysis and semantic versioning principles.

For information about the automated release process itself, see [Release Automation](#6.2). For version synchronization mechanisms, see [Version Synchronization](#6.3).

---

## Version Timeline

The following diagram shows the progression of releases and their major characteristics:

**Version Release Timeline**

```mermaid
timeline
    title terraform-skill Release Timeline
    section 2026-01-18
        v1.0.0 : Initial Release
               : BREAKING marketplace migration
               : GitHub source type
               : Version synchronization
    section 2026-01-19
        v1.5.0 : Best practices enhancement
               : Plugin install docs
               : Validation fixes
               : Changelog preservation
```

**Sources:** [CHANGELOG.md:1-51]()

---

## Release Versions

### v1.5.0 (2026-01-19)

The latest release focused on content enhancement and automation reliability improvements.

| Category | Change | Commit | Issue |
|----------|--------|--------|-------|
| **Feature** | Added plugin install command to docs | `c400b18` | - |
| **Feature** | Enhance skill with comprehensive best practices from original guide | `f32fc3b` | - |
| **Bug Fix** | Allow optional frontmatter fields in SKILL.md validation | `e4393cb` | #21146856119 |
| **Bug Fix** | Prevent changelog regeneration from losing intermediate releases | `b81b57d` | - |
| **Bug Fix** | Revert conventional-changelog-action to v5 due to tag detection bug | `9ba8215` | - |

**Key Improvements:**
- Enhanced SKILL.md with comprehensive Terraform/OpenTofu best practices
- Improved validation workflow to support optional frontmatter fields
- Fixed changelog generation to preserve version history across regenerations
- Documented marketplace installation command for better user onboarding

**Sources:** [CHANGELOG.md:1-16]()

---

### v1.0.0 (2026-01-18)

Initial public release with marketplace-based distribution architecture.

| Category | Change | Commit | Issue |
|----------|--------|--------|-------|
| **Feature** | Initial release of terraform-skill v1.0.0 | `4f1a017` | - |
| **Feature** | Migrate to marketplace-only architecture | `f32de12` | - |
| **Bug Fix** | Update marketplace.json version and source structure | `2bca71c` | - |
| **Bug Fix** | Fixed marketplace.json | `2b12e4e` | - |

**Sources:** [CHANGELOG.md:18-48]()

---

## Breaking Changes

### v1.0.0: Marketplace Migration

The v1.0.0 release introduced a **breaking change** that fundamentally altered the distribution mechanism.

**Change Details:**

```mermaid
graph LR
    subgraph "Before v1.0.0"
        OLD_PLUGIN["plugin.json"]
        OLD_SOURCE["source: 'local'"]
    end
    
    subgraph "After v1.0.0"
        NEW_MP["marketplace.json"]
        NEW_SOURCE["source: 'github'"]
        VERSION_SYNC["Three-way version sync"]
    end
    
    OLD_PLUGIN -->|"Removed"| NEW_MP
    OLD_SOURCE -->|"Migrated"| NEW_SOURCE
    NEW_MP --> VERSION_SYNC
    
    subgraph "Impact"
        UNINSTALL["/plugin marketplace remove terraform-skill"]
        REINSTALL["/plugin marketplace add antonbabenko/terraform-skill"]
    end
    
    VERSION_SYNC --> UNINSTALL
    UNINSTALL --> REINSTALL
```

**Migration Requirements:**

Users upgrading from pre-1.0.0 versions must manually reinstall the skill:

```bash
/plugin marketplace remove terraform-skill
/plugin marketplace add antonbabenko/terraform-skill
```

**Technical Changes:**
- Removed `plugin.json` in favor of `.claude-plugin/marketplace.json`
- Changed source type from `local` to `github` for marketplace distribution
- Implemented version synchronization across marketplace root, plugin definition, and git refs
- Updated validation and release workflows to support `marketplace.json`
- Updated all documentation references from `plugin.json` to `marketplace.json`

**Sources:** [CHANGELOG.md:27-48]()

---

## Changelog Structure

The changelog file follows the [Conventional Changelog](https://github.com/conventional-changelog/conventional-changelog) format and is automatically generated.

**Changelog File Mapping**

```mermaid
graph TD
    subgraph "CHANGELOG.md Structure"
        HEADER["# [Version] (Date)"]
        COMPARE["compare/vPrev...vCurrent"]
        
        subgraph "Entry Types"
            FEATURES["### Features"]
            FIXES["### Bug Fixes"]
            BREAKING["### BREAKING CHANGES"]
        end
        
        subgraph "Entry Components"
            SCOPE["**scope:** description"]
            COMMIT["commit hash link"]
            ISSUE["closes #issue"]
        end
    end
    
    subgraph "Source: Git History"
        CONV_COMMITS["Conventional Commits<br/>feat: fix: docs: etc."]
        GIT_TAGS["Git Tags<br/>v1.0.0, v1.5.0"]
        COMMIT_MSG["Commit Messages<br/>with scope and breaking flags"]
    end
    
    CONV_COMMITS --> FEATURES
    CONV_COMMITS --> FIXES
    COMMIT_MSG --> BREAKING
    GIT_TAGS --> COMPARE
    CONV_COMMITS --> SCOPE
    CONV_COMMITS --> COMMIT
    COMMIT_MSG --> ISSUE
```

**Entry Format Examples:**

| Component | Example | Location in CHANGELOG.md |
|-----------|---------|--------------------------|
| Version header | `# [1.5.0](https://github.com/.../compare/v1.0.0...v1.5.0)` | [CHANGELOG.md:1]() |
| Feature entry | `* Added plugin install command to docs ([c400b18](...))` | [CHANGELOG.md:13]() |
| Bug fix entry | `* Allow optional frontmatter fields ([e4393cb](...)), closes [#21146856119](...)` | [CHANGELOG.md:6]() |
| Breaking change | `* Removed plugin.json in favor of marketplace.json.` | [CHANGELOG.md:37]() |

**Sources:** [CHANGELOG.md:1-51]()

---

## Semantic Versioning Strategy

The project follows [Semantic Versioning 2.0.0](https://semver.org/) with automated version determination based on conventional commit types.

**Version Bump Rules**

```mermaid
graph LR
    subgraph "Commit Types"
        FEAT["feat: commit"]
        FIX["fix: commit"]
        BREAKING["BREAKING CHANGE: footer"]
        OTHER["docs:, chore:, etc."]
    end
    
    subgraph "Version Increments"
        MAJOR["MAJOR<br/>X.0.0"]
        MINOR["MINOR<br/>0.X.0"]
        PATCH["PATCH<br/>0.0.X"]
        NO_RELEASE["No release"]
    end
    
    BREAKING --> MAJOR
    FEAT --> MINOR
    FIX --> PATCH
    OTHER --> NO_RELEASE
    
    subgraph "Example: v1.5.0"
        V1_0_0["v1.0.0"]
        FEAT_COMMITS["2x feat: commits"]
        FIX_COMMITS["3x fix: commits"]
        V1_5_0["v1.5.0"]
    end
    
    V1_0_0 --> FEAT_COMMITS
    V1_0_0 --> FIX_COMMITS
    FEAT_COMMITS --> V1_5_0
    FIX_COMMITS --> V1_5_0
```

**Version Component Mapping:**

| Version | MAJOR | MINOR | PATCH | Trigger |
|---------|-------|-------|-------|---------|
| v1.0.0 | 1 | 0 | 0 | `BREAKING CHANGE` footer in commit `f32de12` |
| v1.5.0 | 1 | 5 | 0 | `feat:` commits `c400b18`, `f32fc3b` |

**Sources:** [CHANGELOG.md:1-51](), High-level diagrams (Diagram 3: Development & Release Workflow)

---

## Version Synchronization Points

Each release ensures version consistency across multiple files through automated synchronization.

**Three-Way Version Sync**

```mermaid
graph TD
    subgraph "Version Sources"
        GIT_TAG["Git Tag<br/>v1.5.0"]
        
        MP_ROOT[".claude-plugin/marketplace.json<br/>root.version"]
        MP_PLUGIN[".claude-plugin/marketplace.json<br/>plugin.version"]
        
        SKILL_META["SKILL.md<br/>frontmatter.version"]
    end
    
    subgraph "Automated Release Workflow"
        RELEASE_YML[".github/workflows/automated-release.yml"]
        VERSION_BUMP["Determine version bump<br/>from conventional commits"]
        UPDATE_FILES["Update all version fields"]
        CREATE_TAG["Create git tag"]
        GEN_CHANGELOG["Generate CHANGELOG.md"]
    end
    
    RELEASE_YML --> VERSION_BUMP
    VERSION_BUMP --> UPDATE_FILES
    UPDATE_FILES --> MP_ROOT
    UPDATE_FILES --> MP_PLUGIN
    UPDATE_FILES --> SKILL_META
    UPDATE_FILES --> CREATE_TAG
    CREATE_TAG --> GIT_TAG
    VERSION_BUMP --> GEN_CHANGELOG
    
    MP_ROOT -.->|"Must match"| GIT_TAG
    MP_PLUGIN -.->|"Must match"| GIT_TAG
    SKILL_META -.->|"Must match"| GIT_TAG
```

**Synchronized Fields:**

| File | Field Path | v1.5.0 Value |
|------|-----------|--------------|
| Git repository | Tag | `v1.5.0` |
| `.claude-plugin/marketplace.json` | `version` (root) | `1.5.0` |
| `.claude-plugin/marketplace.json` | `plugin.version` | `1.5.0` |
| `SKILL.md` | `version` (frontmatter) | `1.5.0` |
| `CHANGELOG.md` | Latest header | `# [1.5.0]` |

**Sources:** [CHANGELOG.md:1-51](), High-level diagrams (Diagram 3: Development & Release Workflow)

---

## Changelog Generation Process

The changelog is automatically generated during the release workflow and follows a preservation strategy to prevent data loss.

**Generation Workflow**

```mermaid
graph TD
    MERGE["Merge to master"]
    ANALYZE["Analyze conventional commits<br/>since last tag"]
    
    subgraph "Version Determination"
        CHECK_BREAKING["Check for BREAKING CHANGE"]
        CHECK_FEAT["Check for feat: commits"]
        CHECK_FIX["Check for fix: commits"]
        DETERMINE["Determine bump:<br/>major / minor / patch"]
    end
    
    subgraph "File Updates"
        UPDATE_MP["Update marketplace.json versions"]
        UPDATE_SKILL["Update SKILL.md version"]
        GEN_CL["Generate CHANGELOG.md entry"]
        PRESERVE["Preserve existing entries"]
    end
    
    subgraph "Release Creation"
        COMMIT_CHANGES["Commit version updates"]
        CREATE_TAG["Create git tag vX.Y.Z"]
        CREATE_RELEASE["Create GitHub release"]
        PUBLISH["Publish to marketplace"]
    end
    
    MERGE --> ANALYZE
    ANALYZE --> CHECK_BREAKING
    ANALYZE --> CHECK_FEAT
    ANALYZE --> CHECK_FIX
    CHECK_BREAKING --> DETERMINE
    CHECK_FEAT --> DETERMINE
    CHECK_FIX --> DETERMINE
    
    DETERMINE --> UPDATE_MP
    DETERMINE --> UPDATE_SKILL
    DETERMINE --> GEN_CL
    GEN_CL --> PRESERVE
    
    UPDATE_MP --> COMMIT_CHANGES
    UPDATE_SKILL --> COMMIT_CHANGES
    PRESERVE --> COMMIT_CHANGES
    
    COMMIT_CHANGES --> CREATE_TAG
    CREATE_TAG --> CREATE_RELEASE
    CREATE_RELEASE --> PUBLISH
```

**Bug Fix: Changelog Preservation**

Commit `b81b57d` fixed an issue where regenerating the changelog would lose intermediate releases. The fix ensures that:
- Existing changelog entries are preserved during generation
- Only new version entries are appended
- Historical release data remains intact across workflow runs

**Sources:** [CHANGELOG.md:7](), High-level diagrams (Diagram 3: Development & Release Workflow)

---

## Commit Hash Reference

All changelog entries link to full commit details on GitHub. The following table provides quick access to significant commits:

| Commit | Type | Description | Version |
|--------|------|-------------|---------|
| `c400b18` | feat | Added plugin install command to docs | v1.5.0 |
| `f32fc3b` | feat | Enhance skill with comprehensive best practices | v1.5.0 |
| `e4393cb` | fix | Allow optional frontmatter fields in validation | v1.5.0 |
| `b81b57d` | fix | Prevent changelog regeneration data loss | v1.5.0 |
| `9ba8215` | fix | Revert conventional-changelog-action to v5 | v1.5.0 |
| `f32de12` | feat! | Migrate to marketplace-only architecture | v1.0.0 |
| `2bca71c` | fix | Update marketplace.json version and source | v1.0.0 |
| `2b12e4e` | fix | Fixed marketplace.json | v1.0.0 |
| `4f1a017` | feat | Initial release of terraform-skill | v1.0.0 |

**Sources:** [CHANGELOG.md:1-51]()

---

## Release Artifacts

Each release generates the following artifacts:

| Artifact | Location | Purpose |
|----------|----------|---------|
| Git Tag | `refs/tags/vX.Y.Z` | Version reference point |
| GitHub Release | `https://github.com/antonbabenko/terraform-skill/releases` | Release notes and downloads |
| Updated CHANGELOG.md | [CHANGELOG.md:1-51]() | Version history documentation |
| Updated marketplace.json | `.claude-plugin/marketplace.json` | Plugin metadata |
| Updated SKILL.md | `SKILL.md` frontmatter | Skill version metadata |

**Sources:** [CHANGELOG.md:1-51](), High-level diagrams (Diagram 3: Development & Release Workflow)

---

# Page: Legal & Licensing

# Legal & Licensing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)

</details>



## Purpose and Scope

This document describes the licensing terms, copyright information, and legal framework governing the terraform-skill repository. The project is released under the Apache License, Version 2.0, which defines how users may use, modify, redistribute, and contribute to the codebase.

For information about contribution requirements and workflow processes, see [Development Guide](#5).

**Sources:** [LICENSE:1-195]()

---

## License Overview

The terraform-skill repository is licensed under the **Apache License, Version 2.0** (January 2004). This is a permissive open-source license that allows broad use, modification, and redistribution while providing patent protection and clear attribution requirements.

### Copyright Holder

```
Copyright 2026 Anton Babenko
terraform-best-practices.com
Compliance.tf - Terraform Compliance for Cloud-Native Enterprise
```

The copyright notice appears at [LICENSE:1-4]() and establishes Anton Babenko as the copyright holder.

### License Location

The full license text is available at:
- Repository: [LICENSE:1-195]()
- Official text: http://www.apache.org/licenses/LICENSE-2.0 [LICENSE:10]()

**Sources:** [LICENSE:1-21]()

---

## License Architecture

### File Coverage Diagram

```mermaid
graph TB
    subgraph "Legal Framework"
        LICENSE["LICENSE<br/>Apache 2.0 Full Text<br/>(195 lines)"]
        COPYRIGHT["Copyright Notice<br/>Lines 1-4"]
    end
    
    subgraph "Protected Content"
        SKILL["SKILL.md<br/>Core skill content"]
        MP["marketplace.json<br/>Plugin definition"]
        REFS["references/*.md<br/>Knowledge base"]
        WORKFLOWS[".github/workflows/*.yml<br/>Automation"]
        DOCS["README.md<br/>CONTRIBUTING.md<br/>CLAUDE.md"]
    end
    
    subgraph "Derivative Works"
        FORKS["Forked repositories"]
        MODS["Modified versions"]
        DISTROS["Redistributions"]
    end
    
    LICENSE -->|"Governs use of"| SKILL
    LICENSE -->|"Governs use of"| MP
    LICENSE -->|"Governs use of"| REFS
    LICENSE -->|"Governs use of"| WORKFLOWS
    LICENSE -->|"Governs use of"| DOCS
    
    SKILL -->|"Can create"| FORKS
    SKILL -->|"Can create"| MODS
    SKILL -->|"Can create"| DISTROS
    
    LICENSE -->|"Must be included in"| FORKS
    LICENSE -->|"Must be included in"| MODS
    LICENSE -->|"Must be included in"| DISTROS
    
    COPYRIGHT -->|"Must be retained in"| FORKS
    COPYRIGHT -->|"Must be retained in"| MODS
    COPYRIGHT -->|"Must be retained in"| DISTROS
```

**Sources:** [LICENSE:1-195](), [LICENSE:107-146]()

---

## Key Permissions Granted

The Apache 2.0 license grants the following permissions to users:

| Permission | Scope | Conditions |
|------------|-------|------------|
| **Use** | Use the Work for any purpose | None |
| **Reproduction** | Make copies of the Work | Must include license copy |
| **Distribution** | Distribute copies | Must meet redistribution requirements (Section 4) |
| **Modification** | Create Derivative Works | Modified files must carry prominent notices |
| **Sublicensing** | Grant sublicenses | Must comply with license terms |
| **Patent Use** | Use patent claims in Contributions | Subject to patent license terms |
| **Commercial Use** | Use in commercial applications | Permitted without restriction |

### Copyright License Grant

As defined in [LICENSE:84-89]():

- **Perpetual**: No expiration date
- **Worldwide**: Valid in all jurisdictions
- **Non-exclusive**: Does not prevent other licenses
- **No-charge**: No royalty or fees required
- **Royalty-free**: No ongoing payments
- **Irrevocable**: Cannot be revoked (except for patent termination)

The license covers both **Source form** (markdown files, YAML, JSON) and **Object form** (generated documentation, compiled artifacts).

**Sources:** [LICENSE:84-89](), [LICENSE:43-65]()

---

## Redistribution Requirements

### Mandatory Requirements

When redistributing the Work or Derivative Works, users **must** comply with all conditions in [LICENSE:107-146](). The following table summarizes the requirements:

| Requirement | Location | Description |
|-------------|----------|-------------|
| **License Copy** | [LICENSE:112-113]() | Provide a copy of the Apache 2.0 license |
| **Change Notices** | [LICENSE:115-116]() | Mark modified files with prominent notices |
| **Copyright Retention** | [LICENSE:118-122]() | Retain all copyright, patent, trademark notices |
| **NOTICE File** | [LICENSE:124-139]() | Include NOTICE file if present (not applicable) |
| **Attribution** | [LICENSE:141-146]() | May add own attribution alongside original |

### Redistribution Flow Diagram

```mermaid
graph LR
    subgraph "Original Work"
        ORIG["terraform-skill<br/>repository"]
        LICENSE_ORIG["LICENSE file"]
        COPYRIGHT_ORIG["Copyright notices"]
    end
    
    subgraph "User Actions"
        FORK["Fork/Clone<br/>repository"]
        MODIFY["Modify<br/>SKILL.md or<br/>references/*.md"]
        DISTRIB["Distribute<br/>modified version"]
    end
    
    subgraph "Required Inclusions"
        LICENSE_COPY["Copy of LICENSE"]
        CHANGE_NOTICE["Prominent change<br/>notices in<br/>modified files"]
        COPYRIGHT_RETAIN["Original copyright<br/>notices retained"]
        ATTRIB_ADD["Optional: Add own<br/>attribution"]
    end
    
    subgraph "Derivative Work"
        DERIV["Redistributed<br/>terraform-skill"]
    end
    
    ORIG --> FORK
    LICENSE_ORIG --> FORK
    COPYRIGHT_ORIG --> FORK
    
    FORK --> MODIFY
    MODIFY --> DISTRIB
    
    DISTRIB --> LICENSE_COPY
    DISTRIB --> CHANGE_NOTICE
    DISTRIB --> COPYRIGHT_RETAIN
    DISTRIB --> ATTRIB_ADD
    
    LICENSE_COPY --> DERIV
    CHANGE_NOTICE --> DERIV
    COPYRIGHT_RETAIN --> DERIV
    ATTRIB_ADD --> DERIV
```

### Example Change Notice

When modifying files, add notices like:

```markdown
<!-- Modified by [Your Name/Organization] on [Date] -->
<!-- Changes: [Description of modifications] -->
```

This satisfies the requirement at [LICENSE:115-116]().

**Sources:** [LICENSE:107-146]()

---

## Contribution Licensing

### Automatic License Grant

All contributions to the terraform-skill repository are automatically licensed under the Apache 2.0 license through the submission process. This is defined in [LICENSE:148-154]().

```mermaid
graph TB
    subgraph "Contributor"
        DEV["Developer creates<br/>contribution"]
        SUBMIT["Submits PR via<br/>GitHub"]
    end
    
    subgraph "Contribution Definition (LICENSE:66-78)"
        CONTRIBUTION["Any work of authorship:<br/>- Original version<br/>- Modifications<br/>- Additions"]
        SUBMITTED["Intentionally submitted<br/>to Licensor via:<br/>- Electronic<br/>- Verbal<br/>- Written communication"]
    end
    
    subgraph "Automatic License Grant (LICENSE:148-154)"
        GRANT["Contribution licensed under<br/>Apache 2.0 terms"]
        NO_ADDITIONAL["No additional terms<br/>or conditions"]
    end
    
    subgraph "Project Integration"
        MERGE["Merged into<br/>master branch"]
        INCORPORATED["Becomes part of<br/>the Work"]
    end
    
    DEV --> SUBMIT
    SUBMIT --> CONTRIBUTION
    CONTRIBUTION --> SUBMITTED
    SUBMITTED --> GRANT
    GRANT --> NO_ADDITIONAL
    NO_ADDITIONAL --> MERGE
    MERGE --> INCORPORATED
    
    NOTE["Unless explicitly<br/>stated otherwise"]
    GRANT -.->|"Default"| NOTE
```

### Key Terms

- **Contribution**: Defined at [LICENSE:66-78]() as any work of authorship intentionally submitted for inclusion
- **Contributor**: Defined at [LICENSE:80-82]() as the Licensor and anyone whose Contribution has been incorporated
- **Submission**: Includes electronic, verbal, or written communication to maintainers

### Explicit Override Option

Contributors may explicitly state different terms before submission [LICENSE:148](), but this is uncommon and requires prior negotiation.

**Sources:** [LICENSE:66-82](), [LICENSE:148-154]()

---

## Patent License

### Patent Grant

The Apache 2.0 license includes a **patent license grant** at [LICENSE:91-105]() that provides protection for both contributors and users.

| Aspect | Terms |
|--------|-------|
| **Duration** | Perpetual |
| **Scope** | Worldwide, non-exclusive, no-charge, royalty-free |
| **Irrevocability** | Except for patent litigation |
| **Rights Granted** | Make, have made, use, offer to sell, sell, import, transfer |
| **Coverage** | Patent claims in Contributions that are necessarily infringed |

### Patent Termination Provision

If a user institutes patent litigation alleging that the Work or a Contribution infringes a patent, all patent licenses granted to that user terminate as of the litigation filing date [LICENSE:100-105]().

```mermaid
graph TB
    subgraph "Normal Operation"
        CONTRIB["Contributor submits<br/>code to terraform-skill"]
        PATENT_GRANT["Automatic patent license<br/>granted for claims in<br/>their Contribution"]
        USERS["All users receive<br/>patent license"]
    end
    
    subgraph "Patent Litigation Scenario"
        LITIGATION["User files patent lawsuit<br/>alleging Work infringes"]
        TERMINATION["Patent license for that<br/>user terminates immediately"]
        DATE["Termination effective<br/>as of filing date"]
    end
    
    CONTRIB --> PATENT_GRANT
    PATENT_GRANT --> USERS
    
    USERS -.->|"If user sues"| LITIGATION
    LITIGATION --> TERMINATION
    TERMINATION --> DATE
```

This defensive termination provision discourages patent trolling against the project.

**Sources:** [LICENSE:91-105]()

---

## Warranties and Liability

### Disclaimer of Warranty

The Apache 2.0 license provides the Work **"AS IS"** without any warranties. This is stated at [LICENSE:161-169]().

| Warranty Type | Status |
|--------------|--------|
| **Express warranties** | None |
| **Implied warranties** | None |
| **Title** | No warranty |
| **Non-infringement** | No warranty |
| **Merchantability** | No warranty |
| **Fitness for particular purpose** | No warranty |

Users are **solely responsible** for:
- Determining appropriateness of use
- Determining appropriateness of redistribution
- Assuming all risks of use

### Limitation of Liability

Contributors have **no liability** for damages arising from use of the Work [LICENSE:171-181](). This includes:

- Direct damages
- Indirect damages
- Special damages
- Incidental damages
- Consequential damages
- Loss of goodwill
- Work stoppage
- Computer failure or malfunction
- Any other commercial damages or losses

This limitation applies even if the contributor has been advised of the possibility of such damages.

### Optional Liability Assumption

When redistributing the Work, users may **choose** to offer support, warranty, or indemnity [LICENSE:183-192](). However:
- This is on the user's own behalf and sole responsibility
- Not on behalf of any other Contributor
- User must indemnify, defend, and hold Contributors harmless

**Sources:** [LICENSE:161-192]()

---

## Trademark Restrictions

The Apache 2.0 license **does not grant** permission to use trade names, trademarks, service marks, or product names of the Licensor [LICENSE:156-159]().

| Permitted Use | Prohibited Use |
|--------------|----------------|
| Describing origin of the Work | Using "terraform-skill" trademark without permission |
| Reproducing NOTICE file content (if present) | Implying endorsement by Anton Babenko |
| Reasonable and customary attribution | Marketing materials using licensor's trademarks |

The copyright notice references:
- `terraform-best-practices.com` [LICENSE:3]()
- `Compliance.tf` [LICENSE:4]()

These names should only be used for factual attribution, not to imply affiliation.

**Sources:** [LICENSE:156-159](), [LICENSE:1-4]()

---

## Practical Implications

### For End Users

| Scenario | Permitted | Requirements |
|----------|-----------|--------------|
| Using skill in Claude Code | ✅ Yes | None |
| Forking repository for private use | ✅ Yes | Retain LICENSE file |
| Modifying SKILL.md for internal use | ✅ Yes | Mark changes in modified files |
| Sharing modified version publicly | ✅ Yes | Include LICENSE, mark changes, retain copyright |
| Using in commercial product | ✅ Yes | Include LICENSE and attribution |
| Removing copyright notices | ❌ No | Violates [LICENSE:118-122]() |
| Suing project for patent infringement | ⚠️ Permitted but terminates patent license | See [LICENSE:100-105]() |

### For Contributors

When submitting a pull request to the repository:

1. Your contribution is automatically licensed under Apache 2.0 [LICENSE:148-154]()
2. You grant a perpetual patent license for any patent claims in your contribution [LICENSE:91-105]()
3. You retain copyright to your contribution, but grant broad usage rights
4. No additional agreements or CLAs required

This aligns with the contribution workflow described in [Development Guide](#5).

### For Redistributors

When creating a derivative version:

1. ✅ Include complete `LICENSE` file [LICENSE:112-113]()
2. ✅ Add change notices to modified files [LICENSE:115-116]()
3. ✅ Retain original copyright notices [LICENSE:118-122]()
4. ✅ Optionally add your own attribution [LICENSE:141-146]()
5. ❌ Do not claim the work is officially endorsed without permission

**Sources:** [LICENSE:84-192]()

---

## License Version and Applicability

### Apache License Version

The specific license version is **Apache License, Version 2.0, January 2004** [LICENSE:19-21](). This is the current version of the Apache License and is widely used in open-source projects.

### Work Definition

Under the license, "Work" means [LICENSE:53-56]():
- All files in the repository
- Source form (markdown, YAML, JSON files)
- Object form (generated documentation if any)
- Indicated by copyright notice [LICENSE:1-4]()

### License Applicability Diagram

```mermaid
graph TB
    subgraph "Files Governed by LICENSE"
        SKILL_MD["SKILL.md"]
        MARKETPLACE["marketplace.json<br/>(.claude-plugin/)"]
        REFS_MD["references/module-patterns.md<br/>references/quick-reference.md<br/>references/code-patterns.md<br/>references/ci-cd-workflows.md<br/>references/security-compliance.md"]
        WORKFLOWS_YML[".github/workflows/automated-release.yml<br/>.github/workflows/validate.yml"]
        DOCS_MD["README.md<br/>CONTRIBUTING.md<br/>CLAUDE.md<br/>CHANGELOG.md"]
        TEMPLATES[".github/PULL_REQUEST_TEMPLATE.md"]
        CONFIG[".gitignore"]
    end
    
    subgraph "License Terms Apply To All"
        LICENSE_FILE["LICENSE<br/>Apache 2.0"]
    end
    
    LICENSE_FILE -->|"Section 2:<br/>Copyright License"| SKILL_MD
    LICENSE_FILE -->|"Section 2:<br/>Copyright License"| MARKETPLACE
    LICENSE_FILE -->|"Section 2:<br/>Copyright License"| REFS_MD
    LICENSE_FILE -->|"Section 2:<br/>Copyright License"| WORKFLOWS_YML
    LICENSE_FILE -->|"Section 2:<br/>Copyright License"| DOCS_MD
    LICENSE_FILE -->|"Section 2:<br/>Copyright License"| TEMPLATES
    LICENSE_FILE -->|"Section 2:<br/>Copyright License"| CONFIG
```

The license covers all files in the repository tree, as indicated by the copyright notice being attached to the Work as a whole [LICENSE:53-56]().

**Sources:** [LICENSE:19-21](), [LICENSE:53-56](), [LICENSE:1-4]()

---

## Summary Table

### Quick Reference

| Topic | Key Points | License Section |
|-------|------------|-----------------|
| **License Type** | Apache 2.0, January 2004 | [LICENSE:19-21]() |
| **Copyright** | © 2026 Anton Babenko | [LICENSE:1]() |
| **Permissions** | Use, modify, distribute, sublicense, commercial use | [LICENSE:84-89]() |
| **Patent Grant** | Perpetual, irrevocable patent license for Contributions | [LICENSE:91-105]() |
| **Redistribution** | Must include LICENSE, mark changes, retain copyright | [LICENSE:107-146]() |
| **Contributions** | Automatic Apache 2.0 licensing upon submission | [LICENSE:148-154]() |
| **Warranties** | None - provided "AS IS" | [LICENSE:161-169]() |
| **Liability** | Contributors not liable for damages | [LICENSE:171-181]() |
| **Trademarks** | No permission to use licensor's trademarks | [LICENSE:156-159]() |

**Sources:** [LICENSE:1-195]()

---

# Page: Configuration Files

# Configuration Files

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)

</details>



## Purpose and Scope

This document describes the supporting configuration files used in the terraform-skill repository. These files control which artifacts are excluded from version control and manage local development settings. For information about the core plugin configuration, see [Plugin Definition System](#3.1). For information about workflow automation configuration, see [Automation Systems](#6).

The configuration layer in terraform-skill is intentionally minimal, consisting primarily of version control exclusions. Unlike typical software projects with extensive build configurations, this repository focuses on content delivery to Claude Code, requiring only basic repository hygiene.

---

## Overview

The repository contains a single configuration file that defines version control exclusion patterns:

| File | Purpose | Importance Score |
|------|---------|------------------|
| `.gitignore` | Excludes local Claude settings from version control | 0.70 |

This minimal configuration reflects the repository's architecture as a content-focused Claude skill rather than a traditional application codebase.

---

## Version Control Exclusions (.gitignore)

### File Structure

The [.gitignore:1-2]() file contains a single exclusion pattern:

```
.claude/settings.local.json
```

This pattern prevents local Claude Code configuration files from being committed to the repository.

### Excluded Artifacts

#### .claude/settings.local.json

The `.claude/settings.local.json` file is a local configuration file created by Claude Code for user-specific settings. This file:

- **Location**: `.claude/` directory in the repository root
- **Scope**: Local development environment only
- **Purpose**: Stores user-specific Claude Code preferences and settings
- **Why excluded**: Contains personal configuration that should not be shared across developers

**Characteristics**:
- Created automatically by Claude Code during local skill development
- May contain developer-specific preferences or API configurations
- Should never be committed to ensure consistent baseline behavior across all users
- Exclusion prevents accidental commits of personal settings

---

## Configuration File Integration

### Integration with Development Workflow

```mermaid
flowchart TD
    subgraph "Version Control Boundary"
        GITIGNORE[".gitignore<br/>Exclusion Rules"]
    end
    
    subgraph "Committed Files"
        MP["marketplace.json<br/>Public plugin definition"]
        SKILL["SKILL.md<br/>Public skill content"]
        REF["references/*.md<br/>Public documentation"]
    end
    
    subgraph "Local Development Files"
        LOCAL[".claude/settings.local.json<br/>Personal preferences"]
        INSTALL["~/.claude/skills/<br/>Installation directory"]
    end
    
    subgraph "Development Actions"
        DEV["Developer edits SKILL.md"]
        TEST["Test in Claude Code"]
        COMMIT["git commit"]
    end
    
    GITIGNORE -->|"Excludes"| LOCAL
    GITIGNORE -->|"Allows"| MP
    GITIGNORE -->|"Allows"| SKILL
    GITIGNORE -->|"Allows"| REF
    
    DEV --> TEST
    TEST -->|"Uses"| LOCAL
    TEST -->|"Loads from"| INSTALL
    
    DEV --> COMMIT
    COMMIT -->|"Blocks"| LOCAL
    COMMIT -->|"Includes"| MP
    COMMIT -->|"Includes"| SKILL
    COMMIT -->|"Includes"| REF
```

**Sources**: [.gitignore:1-2]()

### Relationship to Claude Plugin System

The `.gitignore` configuration supports the plugin development workflow by ensuring:

1. **Consistent Testing Environment**: All developers test against the same baseline without local configuration interference
2. **Clean Repository**: Only intentional, public-facing content gets committed
3. **Privacy Protection**: Personal Claude Code settings remain private
4. **Testing Methodology Compliance**: Aligns with the "Iron Law" of testing (see [Testing Methodology](#5.3)) by preventing configuration drift

---

## Configuration Patterns

### What Gets Committed vs. Excluded

```mermaid
graph TB
    subgraph "Repository Root"
        ROOT["/"]
    end
    
    subgraph "Committed - Public Content"
        MP_ROOT["marketplace.json"]
        SKILL_ROOT["SKILL.md"]
        README_ROOT["README.md"]
        PLUGIN_DIR[".claude-plugin/"]
        MP_PLUGIN[".claude-plugin/marketplace.json"]
        REF_DIR["references/"]
        REF_FILES["references/*.md"]
        WORKFLOWS[".github/workflows/"]
    end
    
    subgraph "Excluded - Local Settings"
        CLAUDE_DIR[".claude/"]
        SETTINGS_LOCAL[".claude/settings.local.json"]
    end
    
    subgraph "Ignore Rules"
        GITIGNORE_FILE[".gitignore"]
        PATTERN[".claude/settings.local.json"]
    end
    
    ROOT --> MP_ROOT
    ROOT --> SKILL_ROOT
    ROOT --> README_ROOT
    ROOT --> PLUGIN_DIR
    ROOT --> REF_DIR
    ROOT --> WORKFLOWS
    ROOT --> CLAUDE_DIR
    ROOT --> GITIGNORE_FILE
    
    PLUGIN_DIR --> MP_PLUGIN
    REF_DIR --> REF_FILES
    CLAUDE_DIR --> SETTINGS_LOCAL
    
    GITIGNORE_FILE --> PATTERN
    PATTERN -.->|"Blocks from commit"| SETTINGS_LOCAL
    
    style SETTINGS_LOCAL fill:#f9f9f9,stroke:#999,stroke-dasharray: 5 5
    style CLAUDE_DIR fill:#f9f9f9,stroke:#999,stroke-dasharray: 5 5
```

**Sources**: [.gitignore:1-2]()

---

## Implementation Details

### Pattern Specificity

The `.gitignore` pattern is intentionally specific:

| Pattern | Scope | Rationale |
|---------|-------|-----------|
| `.claude/settings.local.json` | Exact file match | Only excludes the specific local settings file |
| Does NOT use `.claude/*` | - | Avoids accidentally excluding future committed `.claude/` content |
| Does NOT use `*.local.json` | - | Prevents overly broad exclusions in other directories |

This precision ensures that:
- Only intentional files are excluded
- Future `.claude/` directory content can be committed if needed
- The exclusion pattern is self-documenting

### Integration with Automation

The `.gitignore` configuration interacts with automated workflows:

```mermaid
flowchart LR
    subgraph "Local Development"
        EDIT["Edit SKILL.md"]
        LOCAL_TEST["Test with local settings"]
        GIT_ADD["git add ."]
    end
    
    subgraph "Git Operations"
        GITIGNORE[".gitignore"]
        FILTER["Filter excluded files"]
        STAGING["Staging area"]
    end
    
    subgraph "Automation Triggers"
        PUSH["git push"]
        VALIDATE["validate.yml workflow"]
        RELEASE["automated-release.yml workflow"]
    end
    
    EDIT --> LOCAL_TEST
    LOCAL_TEST --> GIT_ADD
    GIT_ADD --> GITIGNORE
    GITIGNORE --> FILTER
    FILTER -->|"Excludes .claude/settings.local.json"| STAGING
    STAGING --> PUSH
    PUSH --> VALIDATE
    PUSH --> RELEASE
```

**Key Integration Points**:
- **Validation Workflow** (see [Validation Workflow](#6.1)): Only validates committed files, unaffected by local settings
- **Release Automation** (see [Release Automation](#6.2)): Only processes committed content for release
- **Local Testing**: Developers can maintain personal settings without risk of accidental commits

**Sources**: [.gitignore:1-2]()

---

## Usage Patterns

### For Contributors

When contributing to terraform-skill, the `.gitignore` configuration automatically handles local development artifacts:

**Workflow Example**:
```bash
# 1. Clone repository
git clone https://github.com/antonbabenko/terraform-skill
cd terraform-skill

# 2. Install for local testing (creates .claude/settings.local.json)
plugin marketplace add ./

# 3. Edit content
vim SKILL.md

# 4. Test in Claude Code
# (Uses .claude/settings.local.json automatically)

# 5. Commit changes
git add .
# .gitignore automatically excludes .claude/settings.local.json
git commit -m "feat: improve testing guidance"

# 6. Push - only public content is committed
git push
```

The `.gitignore` ensures step 5 never commits personal settings, maintaining clean PR history.

### For Maintainers

Maintainers benefit from `.gitignore` by:

1. **Consistent PR Review**: All PRs contain only intentional content changes
2. **No Configuration Drift**: Local settings don't pollute the repository
3. **Clean Git History**: CHANGELOG generation (see [Release Automation](#6.2)) only reflects content changes

---

## Design Rationale

### Why Exclude .claude/settings.local.json?

| Reason | Impact |
|--------|--------|
| **Personal Preferences** | Different developers may have different Claude Code settings |
| **Testing Isolation** | Ensures skill behavior is tested independently of local configuration |
| **Privacy** | May contain API keys or personal workspace settings |
| **Repository Hygiene** | Prevents configuration file churn in commit history |

### Why Not Exclude More?

The repository deliberately avoids excluding:

- **`.claude-plugin/` directory**: Contains the committed plugin definition [.claude-plugin/marketplace.json]()
- **Temporary files**: No build artifacts exist in this content-focused repository
- **IDE settings**: Contributors use diverse editors; no standardized IDE configuration

This minimalist approach aligns with the repository's "prompt engineering as infrastructure" philosophy (see [Development Philosophy](#5.1)), where content is code and configuration is minimal.

---

## Relationship to Other Systems

### Integration Points

| System | Relationship | Reference |
|--------|--------------|-----------|
| **Plugin Definition** | `.gitignore` ensures only committed plugin files are distributed | [Plugin Definition System](#3.1) |
| **Validation Workflow** | Validates only committed files, unaffected by excluded settings | [Validation Workflow](#6.1) |
| **Release Automation** | Releases only include committed content | [Release Automation](#6.2) |
| **Local Testing** | Excluded settings enable personalized development environments | [Testing Methodology](#5.3) |

```mermaid
graph LR
    subgraph "Configuration Layer"
        GITIGNORE[".gitignore"]
    end
    
    subgraph "Content Layer"
        MP["marketplace.json"]
        SKILL["SKILL.md"]
    end
    
    subgraph "Automation Layer"
        VALIDATE["validate.yml"]
        RELEASE["automated-release.yml"]
    end
    
    subgraph "Development Layer"
        LOCAL[".claude/settings.local.json"]
        TEST["Local Testing"]
    end
    
    GITIGNORE -->|"Protects"| MP
    GITIGNORE -->|"Protects"| SKILL
    GITIGNORE -->|"Excludes"| LOCAL
    
    MP --> VALIDATE
    SKILL --> VALIDATE
    MP --> RELEASE
    SKILL --> RELEASE
    
    LOCAL --> TEST
    TEST -.->|"Does not affect"| VALIDATE
    TEST -.->|"Does not affect"| RELEASE
```

**Sources**: [.gitignore:1-2]()

---

## Summary

The terraform-skill repository maintains minimal configuration:

- **Single Configuration File**: `.gitignore` with one exclusion pattern
- **Purpose**: Exclude local Claude Code settings from version control
- **Design Philosophy**: Minimalist approach focusing on content over configuration
- **Integration**: Supports clean development workflow and automated release processes

This simple configuration layer enables developers to maintain personal settings while ensuring the repository contains only intentional, public-facing content that gets validated and released through automated workflows.

**Sources**: [.gitignore:1-2]()