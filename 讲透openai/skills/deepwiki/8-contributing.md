<!-- source: DeepWiki mcp.deepwiki.com · repo openai/skills · page 8 Contributing · fetched 2026-10-30 -->

# Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [README.md](README.md)
- [contributing.md](contributing.md)

</details>



This document provides an overview of the contribution process for the Agent Skills repository. It covers community values, security reporting procedures, and the general pathways for contributing skills, improvements, and documentation.

For detailed workflow steps and community standards, see [Contribution Workflow](#8.2). For legal requirements and the signing process, see [Contributor License Agreement](#8.1).

---

## Overview

The Agent Skills repository accepts several types of contributions to enhance the modular capabilities of Codex AI agents.

| Contribution Type | Target Location | Process |
|------------------|----------------|---------|
| **New skills** | `skills/.curated/` or `skills/.experimental/` | Use `skill-creator` system, validate with `quick_validate.py`, submit PR |
| **Skill improvements** | Existing skill directories | Modify `SKILL.md`, scripts, or references, validate, submit PR |
| **Bug fixes** | Any affected files | Standard PR with clear description of issue and fix |
| **Documentation** | `README.md`, wiki pages, skill docs | Direct edits via PR |
| **Tooling improvements** | `skills/.system/skill-creator/` | PR with tests demonstrating improvements |

New skills should start in `skills/.experimental/` for testing, then move to `skills/.curated/` once stable and reviewed. Skills in `skills/.system/` are maintained by the core team and auto-installed with Codex [README.md:14-14]().

**Sources:** [contributing.md:1-12](), [README.md:14-36]()

---

## Community Values

The repository follows these core principles for all interactions to ensure a productive and welcoming environment:

*   **Be Kind and Inclusive:** Treat others with respect. We follow the [Contributor Covenant](https://www.contributor-covenant.org/) code of conduct [contributing.md:5-5]().
*   **Assume Good Intent:** Written communication is hard—err on the side of generosity and assume positive intentions [contributing.md:6-6]().
*   **Teach & Learn:** If you spot something confusing, open an issue or PR with improvements [contributing.md:7-7]().

For more details on how these values are applied in our daily workflows, see [Contribution Workflow](#8.2).

**Sources:** [contributing.md:3-8]()

---

## Security and Responsible AI

If you discover a vulnerability or have concerns about model output, please do **not** open a public issue or PR.

### Reporting Process

Please email **security@openai.com** for:
*   Security vulnerabilities in skill code or scripts.
*   Authentication or credential exposure risks in MCP configurations.
*   Concerns regarding harmful or biased model outputs.

The security team will respond promptly to investigate and resolve the issue privately [contributing.md:11-11]().

**Security Triage Workflow**
```mermaid
graph LR
    "Discovery"["Discovery of<br/>vulnerability or<br/>AI concern"]
    "Email"["Email<br/>security@openai.com"]
    "Response"["Prompt response<br/>from security team"]
    "Resolution"["Private<br/>resolution"]
    
    "Discovery" --> "Email"
    "Email" --> "Response"
    "Response" --> "Resolution"
```

**Sources:** [contributing.md:9-12]()

---

## Contribution Paths

Different contribution types follow different validation and review paths. The following diagram bridges the natural language contribution types to the specific code entities involved in the process.

**Contribution to Code Entity Map**
```mermaid
graph TD
    "Contributor"["Contributor"]
    
    subgraph "Skill_Development_Space"
        "NewSkill"["New Skill Contribution"]
        "InitSkill"["skills/.system/skill-creator/init_skill.py"]
        "QuickValidate"["skills/.system/skill-creator/quick_validate.py"]
        "SkillDir"["SKILL.md & agents/openai.yaml"]
    end
    
    subgraph "Core_Tooling_Space"
        "ToolFix"["Tooling Improvement"]
        "CreatorDir"["skills/.system/skill-creator/"]
        "InstallerDir"["$skill-installer"]
    end
    
    "Contributor" --> "NewSkill"
    "NewSkill" --> "InitSkill"
    "InitSkill" --> "SkillDir"
    "SkillDir" --> "QuickValidate"
    
    "Contributor" --> "ToolFix"
    "ToolFix" --> "CreatorDir"
    "ToolFix" --> "InstallerDir"
```

**Sources:** [contributing.md:1-12](), [README.md:14-16]()

---

## Skill Contribution Lifecycle

When contributing a new skill, the code moves through validation gates before reaching end users. This process ensures that skills meet the required metadata standards for the Codex progressive disclosure model.

**Skill Validation and Installation Flow**
```mermaid
graph LR
    subgraph "Development"
        "InitScript"["skills/.system/skill-creator/init_skill.py"]
        "SkillDir"["my-skill/<br/>SKILL.md<br/>agents/openai.yaml"]
    end
    
    subgraph "Validation"
        "QuickValidate"["skills/.system/skill-creator/quick_validate.py"]
        "Checks"["Validates:<br/>- name format<br/>- frontmatter<br/>- description length"]
    end
    
    subgraph "Distribution_Tiers"
        "Experimental"["skills/.experimental/<br/>my-skill/"]
        "Curated"["skills/.curated/<br/>my-skill/"]
    end
    
    subgraph "User_Installation"
        "SkillInstaller"["$skill-installer utility"]
        "CodexAgent"["Codex Agent<br/>with skill loaded"]
    end
    
    "InitScript" -->|"Creates"| "SkillDir"
    "SkillDir" -->|"Run validation"| "QuickValidate"
    "QuickValidate" --> "Checks"
    "Checks" -->|"Pass"| "Experimental"
    "Experimental" -.->|"After stability"| "Curated"
    
    "Experimental" --> "SkillInstaller"
    "Curated" --> "SkillInstaller"
    "SkillInstaller" --> "CodexAgent"
```

### Validation Requirements

Before submitting a skill PR, you must run the validation tool. The validator checks:
*   `name` field uses `hyphen-case` format.
*   `name` field is ≤64 characters.
*   `description` field exists and is ≤256 characters.
*   Required frontmatter fields are present in `SKILL.md`.

For details on these requirements, see [SKILL.md Format Specification](#7.1).

**Sources:** [contributing.md:1-12](), [README.md:16-34]()

---

## Contributor License Agreement (CLA)

All contributors must sign a Contributor License Agreement (CLA) before their contributions can be merged. This ensures that OpenAI has the right to distribute the code under the Apache License 2.0 while contributors retain copyright to their work.

For details on the signing process, see [Contributor License Agreement](#8.1).

**Sources:** [contributing.md:1-12]()

---

## Next Steps

*   **New Contributors:** Start with the [Contribution Workflow](#8.2) for step-by-step guidance.
*   **Skill Developers:** See [Creating Skills](#4) for the complete development guide.
*   **Architecture Enthusiasts:** Review [Architecture](#2) to understand how skills are loaded and executed.

**Sources:** [contributing.md:1-12]()

---

