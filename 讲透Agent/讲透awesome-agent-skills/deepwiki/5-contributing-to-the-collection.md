<!-- source: DeepWiki mcp.deepwiki.com · repo VoltAgent/awesome-agent-skills · page 5 Contributing to the Collection · fetched 2026-10-26 -->

# Contributing to the Collection

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)

</details>



This document guides contributors through the process of submitting Agent Skills to the Awesome Agent Skills curated collection. It covers the overall contribution workflow, architectural boundaries, and quality requirements for skill submissions.

For detailed step-by-step submission instructions, see [Contribution Guidelines](#5.1). For quality standards and acceptance criteria, see [Quality Requirements](#5.2). For information about the review process, see [Review Process](#5.3).

## Scope and Purpose

This page addresses how external skill authors contribute links to their skills in the centralized collection. It does not cover:

- Creating skills themselves (see [Skill Definition Format](#3.1))
- Installing skills in AI assistants (see [Installing Skills](#2.1))
- Using the skills catalog (see [Skill Catalog](#4))

## Architectural Context: What Is Being Contributed

The Awesome Agent Skills repository follows a **decentralized content, centralized discovery** architecture. Contributors do not submit skill implementations to this repository—they submit links to external repositories where skills are maintained.

```mermaid
graph TB
    subgraph External["External Skill Repository<br/>(Owned by Contributor)"]
        SkillImpl["Skill Implementation<br/>SKILL.md or skill directory<br/>with YAML + Markdown"]
        SkillDoc["Documentation<br/>README.md or inline docs"]
        SkillCode["Optional Resources<br/>scripts, configs, examples"]
    end
    
    subgraph AwesomeRepo["Awesome Agent Skills Repository<br/>(This Repository)"]
        README["README.md"]
        CONTRIBUTING["CONTRIBUTING.md"]
        
        subgraph READMESections["README.md Sections"]
            OfficialTeams["Official Team Skills<br/>Lines 97-261"]
            CommunitySkills["Community Skills<br/>Lines 262-373"]
            
            subgraph CommunityCategories["Community Categories"]
                Marketing["Marketing<br/>Lines 264-270"]
                Productivity["Productivity and Collaboration<br/>Lines 272-291"]
                Development["Development and Testing<br/>Lines 293-331"]
                ContextEng["Context Engineering<br/>Lines 333-342"]
                Specialized["Specialized Domains<br/>Lines 344-354"]
                n8n["n8n Automation<br/>Lines 357-365"]
                Other["Other<br/>Lines 367-373"]
            end
        end
    end
    
    subgraph ContributionProcess["Contribution Process"]
        PR["Pull Request<br/>Title: 'Add skill: author/skill-name'<br/>CONTRIBUTING.md:29-31"]
        Entry["Entry Format<br/>**[author/skill-name](URL)** - Description<br/>CONTRIBUTING.md:11-13"]
        Placement["Placement Decision<br/>Based on category<br/>CONTRIBUTING.md:15-19"]
    end
    
    SkillImpl -.->|"contributor creates"| External
    SkillDoc -.->|"contributor documents"| External
    
    External -->|"contributor submits link via"| PR
    PR -->|"contains"| Entry
    PR -->|"specifies"| Placement
    
    Entry -->|"added to"| README
    Placement -->|"determines section in"| READMESections
    
    CONTRIBUTING -.->|"governs format of"| Entry
    CONTRIBUTING -.->|"governs placement in"| READMESections
    
    README -->|"links to"| External
```

**Sources:** [CONTRIBUTING.md:1-44](), [README.md:1-394]()

### Repository Boundaries

This table clarifies what is hosted where:

| Component | Location | Maintained By | Modified By Contributors |
|-----------|----------|---------------|--------------------------|
| Skill implementation (YAML + Markdown) | External repository | Skill author | No - stays external |
| Skill documentation | External repository | Skill author | No - stays external |
| Link to skill | `README.md` in this repo | Collection maintainers | Yes - via PR |
| Contribution rules | `CONTRIBUTING.md` | Collection maintainers | No - governance only |
| License | `LICENSE` | Collection maintainers | No - governance only |

**Sources:** [CONTRIBUTING.md:33-37](), Diagram 6 in high-level architecture

## Contribution Workflow

The complete contribution lifecycle follows this sequence:

```mermaid
graph TB
    A["Skill Author Creates Skill<br/>in External Repository"]
    B["Skill Gains Community Usage<br/>CONTRIBUTING.md:27"]
    C["Author Prepares PR<br/>Title: 'Add skill: author/skill-name'<br/>CONTRIBUTING.md:29-31"]
    
    subgraph PRContent["PR Content"]
        D["Format Entry<br/>**[author/skill-name](URL)** - Description<br/>CONTRIBUTING.md:11-13"]
        E["Choose Placement<br/>README.md section<br/>CONTRIBUTING.md:15-19"]
        F["Verify Requirements<br/>CONTRIBUTING.md:21-27"]
    end
    
    G["Submit PR to<br/>awesome-agent-skills"]
    
    subgraph Review["Maintainer Review"]
        H["Verify Link Works<br/>CONTRIBUTING.md:36"]
        I["Check Community Usage<br/>CONTRIBUTING.md:27"]
        J["Validate Description Length<br/>≤10 words, CONTRIBUTING.md:26"]
        K["Assess Quality Bar<br/>CONTRIBUTING.md:37"]
        L["Verify Documentation Exists<br/>CONTRIBUTING.md:24"]
    end
    
    M{"Review<br/>Decision"}
    N["PR Merged<br/>Link Added to README.md"]
    O["PR Declined<br/>with Feedback"]
    
    P["Skill Appears in Collection<br/>Discoverable by Users"]
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    
    G --> H
    H --> I
    I --> J
    J --> K
    K --> L
    L --> M
    
    M -->|"Approved"| N
    M -->|"Rejected"| O
    N --> P
    
    O -.->|"Author improves skill"| B
```

**Sources:** [CONTRIBUTING.md:1-44](), [README.md:374-382](), Diagram 2 in high-level architecture

### Entry Format Specification

Contributors must format entries according to this exact pattern:

```markdown
- **[author/skill-name](https://github.com/author/repo/path)** - Short description of what it does
```

**Format Components:**

| Component | Requirement | Example | Location |
|-----------|-------------|---------|----------|
| Prefix | `- **` | `- **` | Start of line |
| Author/Skill Name | `[author/skill-name]` | `[anthropics/docx]` | Link text |
| URL | `(full-github-path)` | `(https://github.com/anthropics/skills/tree/main/skills/docx)` | Link target |
| Suffix | `**` | `**` | After link |
| Separator | ` - ` | ` - ` | Before description |
| Description | ≤10 words | `Create, edit, and analyze Word documents` | End of line |

**Sources:** [CONTRIBUTING.md:8-13]()

### Placement Decision Tree

```mermaid
graph TB
    Start["New Skill Submission"]
    
    Q1{"Is submitter an<br/>official development team?"}
    Q2{"Does team have<br/>existing section?"}
    Q3{"Matches which<br/>community category?"}
    
    Official["Add to Official Team Section<br/>README.md:97-261"]
    NewTeam["Create New Official Team Section<br/>After existing teams"]
    
    Marketing["Add to Marketing<br/>README.md:264-270"]
    Productivity["Add to Productivity and Collaboration<br/>README.md:272-291"]
    Development["Add to Development and Testing<br/>README.md:293-331"]
    Context["Add to Context Engineering<br/>README.md:333-342"]
    Specialized["Add to Specialized Domains<br/>README.md:344-354"]
    n8n["Add to n8n Automation<br/>README.md:357-365"]
    Other["Add to Other<br/>README.md:367-373"]
    
    Start --> Q1
    Q1 -->|"Yes"| Q2
    Q1 -->|"No"| Q3
    
    Q2 -->|"Yes"| Official
    Q2 -->|"No"| NewTeam
    
    Q3 -->|"SEO, content, ads"| Marketing
    Q3 -->|"Notion, Linear, Slack"| Productivity
    Q3 -->|"Testing, CI/CD, dev tools"| Development
    Q3 -->|"Memory, RAG, multi-agent"| Context
    Q3 -->|"Healthcare, finance, research"| Specialized
    Q3 -->|"n8n workflows"| n8n
    Q3 -->|"No clear fit"| Other
```

**Sources:** [CONTRIBUTING.md:15-19](), [README.md:97-373]()

## Core Requirements

All submissions must meet these mandatory requirements before acceptance:

```mermaid
graph LR
    subgraph Checks["Pre-Submission Checks"]
        C1["Public Repository<br/>CONTRIBUTING.md:23"]
        C2["Documentation Exists<br/>README.md or SKILL.md<br/>CONTRIBUTING.md:24"]
        C3["Author/Org Prefix<br/>in skill name<br/>CONTRIBUTING.md:25"]
        C4["Description ≤10 Words<br/>CONTRIBUTING.md:26"]
        C5["Community Usage<br/>Proven, not brand new<br/>CONTRIBUTING.md:27"]
    end
    
    subgraph Verification["Maintainer Verification"]
        V1["Link Functionality<br/>CONTRIBUTING.md:36"]
        V2["Quality Bar<br/>CONTRIBUTING.md:37"]
    end
    
    C1 --> V1
    C2 --> V1
    C3 --> V1
    C4 --> V1
    C5 --> V2
    
    V1 --> Accept["Accepted"]
    V2 --> Accept
```

**Sources:** [CONTRIBUTING.md:21-27](), [CONTRIBUTING.md:33-37]()

### Community Usage Requirement

The most critical and frequently overlooked requirement:

> Skill must have real community usage. We focus on community-adopted, proven skills. Brand new skills that were just created are not accepted. Give your skill time to mature and gain users before submitting.

This requirement is emphasized in both `CONTRIBUTING.md` and `README.md`:

```markdown
# From CONTRIBUTING.md:27
- Skill must have real community usage. We focus on community-adopted, proven skills. 
  Brand new skills that were just created are not accepted. Give your skill time to 
  mature and gain users before submitting.

# From README.md:381-382  
**Note:** Please don't submit skills you created 3 hours ago. We're now focusing on 
community-adopted skills, especially those published by development teams and proven 
in real-world usage. Quality over quantity.
```

**Sources:** [CONTRIBUTING.md:27](), [README.md:381-382]()

## Getting Help

Contributors experiencing issues should follow this escalation path:

| Issue Type | Action | Reference |
|------------|--------|-----------|
| General contribution questions | Check existing issues and PRs | [CONTRIBUTING.md:41]() |
| New questions about process | Open new issue | [CONTRIBUTING.md:42]() |
| Skill-specific functionality | Visit skill's own repository | [CONTRIBUTING.md:43]() |
| Broken links or removal requests | Open issue in this repository | [README.md:392]() |

**Sources:** [CONTRIBUTING.md:39-44](), [README.md:390-393]()

## License and Legal Boundaries

```mermaid
graph TB
    subgraph ThisRepo["Awesome Agent Skills<br/>(MIT License)"]
        Links["Curated Links<br/>in README.md"]
        Guidelines["Contribution Guidelines<br/>in CONTRIBUTING.md"]
        License["MIT License Terms<br/>in LICENSE"]
    end
    
    subgraph ExternalSkills["External Skill Repositories<br/>(Various Licenses)"]
        Skill1["Skill Implementation"]
        Skill2["Skill Code"]
        Skill3["Skill Resources"]
    end
    
    Disclaimer["Disclaimer:<br/>Skills created and maintained<br/>by respective authors.<br/>Not security-audited.<br/>README.md:390-391"]
    
    Links -.->|"links to"| ExternalSkills
    
    ThisRepo -->|"covered by"| License
    ExternalSkills -->|"not covered by"| License
    
    ThisRepo -.->|"includes"| Disclaimer
```

The repository's license (MIT) applies only to the curated list content in this repository. Individual skills maintain their own licenses and security posture:

> This is a curated list. Skills listed here are created and maintained by their respective authors and teams, not by us. We select community-adopted, proven skills and do not audit, endorse, or guarantee the security or correctness of listed projects. They are not security-audited and should be reviewed before production use.

**Sources:** [README.md:386-393](), [LICENSE:1-21]()

## Next Steps

For detailed information about specific aspects of contributing:

- **Submission mechanics:** See [Contribution Guidelines](#5.1) for PR format, entry syntax, and placement rules
- **Quality standards:** See [Quality Requirements](#5.2) for acceptance criteria and quality bar
- **Review process:** See [Review Process](#5.3) for how submissions are evaluated and what to expect

**Sources:** [CONTRIBUTING.md:1-44](), Table of Contents for sections 5.1-5.3

---

