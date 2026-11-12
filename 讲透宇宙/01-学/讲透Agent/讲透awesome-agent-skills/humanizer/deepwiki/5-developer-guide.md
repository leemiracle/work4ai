<!-- source: DeepWiki mcp.deepwiki.com · repo blader/humanizer · page 5 Developer Guide · fetched 2026-10-26 -->

# Developer Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [SKILL.md](SKILL.md)
- [WARP.md](WARP.md)

</details>



## Purpose and Scope

This guide is for developers and maintainers who need to modify, update, or contribute to the Humanizer skill. It covers the maintenance workflow, file synchronization requirements, versioning protocols, and development best practices specific to this Markdown-based Claude Code skill.

For installation and usage instructions, see [Installation and Usage](#2). For detailed pattern documentation, see [AI Writing Patterns](#3). For technical architecture details, see [Architecture and Implementation](#4).

The Humanizer repository differs from traditional codebases in that it contains no executable code—only three Markdown files that define runtime behavior, user documentation, and maintenance guidance respectively.

Sources: [WARP.md:1-6](), [SKILL.md:1-20]()

---

## Repository Structure

The Humanizer skill consists of three Markdown files with distinct purposes and audiences. Understanding their relationships is critical for maintenance.

### File Relationships and Synchronization

```mermaid
graph TB
    subgraph "Source Files"
        SKILL["SKILL.md<br/>(Source of Truth)"]
        README["README.md<br/>(User Documentation)"]
        WARP["WARP.md<br/>(Developer Guidance)"]
    end
    
    subgraph "SKILL.md Components"
        YAML["YAML Frontmatter<br/>lines 1-20<br/>• name: humanizer<br/>• version: 2.5.1<br/>• description<br/>• allowed-tools"]
        EditorPrompt["Editor Prompt<br/>lines 22-end<br/>• 29 patterns with examples<br/>• Voice Calibration<br/>• Personality & Soul"]
    end
    
    subgraph "README.md Components"
        Install["Installation<br/>(Setup instructions)"]
        Usage["Usage<br/>(Command examples)"]
        PatternTable["Pattern Table<br/>(Must match SKILL.md)"]
        VersionHistory["Version History<br/>(v1.0.0 to v2.5.1)"]
    end
    
    subgraph "Synchronization Requirements"
        VersionSync["Version numbers<br/>must match"]
        PatternSync["Pattern numbers<br/>must match (29 total)"]
        ExampleSync["Examples should<br/>be consistent"]
    end
    
    SKILL --> YAML
    SKILL --> EditorPrompt
    README --> Install
    README --> Usage
    README --> PatternTable
    README --> VersionHistory
    
    YAML -.->|"version field"| VersionSync
    VersionHistory -.->|"version entries"| VersionSync
    
    EditorPrompt -.->|"pattern numbers 1-29"| PatternSync
    PatternTable -.->|"pattern numbers 1-29"| PatternSync
    
    EditorPrompt -.->|"detailed examples"| ExampleSync
    PatternTable -.->|"summarized examples"| ExampleSync
    
    WARP -->|"defines rules for"| VersionSync
    WARP -->|"defines rules for"| PatternSync
    
    style SKILL stroke-dasharray: 5 5
    style README stroke-dasharray: 5 5
    style WARP stroke-dasharray: 5 5
```

**Key File Locations:**

| File | Purpose | Primary Audience | Lines of Interest |
|------|---------|------------------|-------------------|
| `SKILL.md` | Runtime artifact loaded by Claude Code | Claude AI | [SKILL.md:1-20]() (YAML), [SKILL.md:92-350]() (patterns) |
| `README.md` | Installation and usage documentation | End users | (Usage & Version History) |
| `WARP.md` | Maintenance guidelines | Developers | [WARP.md:12-21]() (file relationships), [WARP.md:42-53]() (editing rules) |

Sources: [WARP.md:12-21](), [SKILL.md:1-20]()

---

## Developer Workflow

The following diagram illustrates the complete workflow for making changes to the Humanizer skill, from initial edit through deployment.

```mermaid
graph TB
    Start["Developer identifies<br/>needed change"]
    
    subgraph "Step 1: Consultation"
        ReadWARP["Read WARP.md<br/>for guidance<br/>[WARP.md:42-53]"]
    end
    
    subgraph "Step 2: Edit Source of Truth"
        EditYAML{"Changing<br/>metadata?"}
        EditPatterns{"Changing<br/>patterns?"}
        EditInstructions{"Changing<br/>instructions?"}
        
        ModifyYAML["Edit YAML frontmatter<br/>[SKILL.md:1-20]<br/>• Bump version<br/>• Update description"]
        
        ModifyPatterns["Edit pattern definitions<br/>[SKILL.md:92-350]<br/>• Update examples<br/>• Add patterns (e.g. 25-29)"]
        
        ModifyProcess["Edit processing logic<br/>[SKILL.md:26-36]<br/>• Update Task steps<br/>• Voice Calibration"]
    end
    
    subgraph "Step 3: Synchronize README"
        CheckSync{"What needs<br/>sync?"}
        
        SyncVersion["Update README version history<br/>Add entry for v2.5.1<br/>or current version"]
        
        SyncTable["Update pattern table<br/>Ensure all 29 patterns<br/>match SKILL.md"]
    end
    
    subgraph "Step 4: Validation"
        CheckYAML["Validate YAML syntax<br/>(indentation, colons)"]
        CheckNumbers["Verify pattern numbers<br/>1-29 consistent"]
        CheckVersions["Confirm version numbers<br/>match across files"]
    end
    
    subgraph "Step 5: Deployment"
        Commit["Git commit<br/>(both files together)"]
        Push["Git push to GitHub"]
        Install["Test installation:<br/>cp SKILL.md<br/>~/.claude/skills/humanizer/"]
    end
    
    Start --> ReadWARP
    ReadWARP --> EditYAML
    ReadWARP --> EditPatterns
    ReadWARP --> EditInstructions
    
    EditYAML -->|"Yes"| ModifyYAML
    EditPatterns -->|"Yes"| ModifyPatterns
    EditInstructions -->|"Yes"| ModifyProcess
    
    ModifyYAML --> CheckSync
    ModifyPatterns --> CheckSync
    ModifyProcess --> CheckSync
    
    CheckSync -->|"Version bumped"| SyncVersion
    CheckSync -->|"Pattern changed"| SyncTable
    
    SyncVersion --> CheckYAML
    SyncTable --> CheckYAML
    
    CheckYAML --> CheckNumbers
    CheckNumbers --> CheckVersions
    CheckVersions --> Commit
    
    Commit --> Push
    Push --> Install
    
    style ModifyYAML stroke-width:2px
    style ModifyPatterns stroke-width:2px
    style SyncVersion stroke-width:2px
    style SyncTable stroke-width:2px
```

Sources: [WARP.md:42-53](), [SKILL.md:1-350]()

---

## YAML Frontmatter Structure

The YAML frontmatter in `SKILL.md` defines the skill's metadata and capabilities. This structure is parsed by Claude Code at runtime.

```mermaid
graph LR
    subgraph "YAML Frontmatter [SKILL.md:1-20]"
        Name["name: humanizer<br/>(Skill identifier)"]
        Version["version: 2.5.1<br/>(Semantic versioning)"]
        Description["description: |<br/>(Multi-line text)"]
        Tools["allowed-tools:<br/>(List of capabilities)"]
    end
    
    subgraph "Allowed Tools [SKILL.md:13-19]"
        Read["- Read"]
        Write["- Write"]
        Edit["- Edit"]
        Grep["- Grep"]
        Glob["- Glob"]
        Ask["- AskUserQuestion"]
    end
    
    subgraph "Claude Code Runtime"
        Parser["YAML Parser"]
        Registry["Skill Registry"]
    end
    
    Name --> Parser
    Version --> Parser
    Description --> Parser
    Tools --> Parser
    
    Read --> Tools
    Write --> Tools
    Edit --> Tools
    Grep --> Tools
    Glob --> Tools
    Ask --> Tools
    
    Parser --> Registry
```

**Critical YAML Fields:**

| Field | Type | Purpose | Editing Rules |
|-------|------|---------|---------------|
| `name` | String | Skill identifier used in `/humanizer` command | Never change (breaks existing installations) [SKILL.md:2]() |
| `version` | String | Semantic version number | Must match README version history [SKILL.md:3](), [WARP.md:43-46]() |
| `description` | Multi-line | Displayed in skill list | Update when behavior changes significantly [SKILL.md:4-10]() |
| `allowed-tools` | List | Permissions for file operations | Current tools: Read, Write, Edit, Grep, Glob, AskUserQuestion [SKILL.md:13-19]() |

Sources: [SKILL.md:1-20](), [WARP.md:43-46]()

---

## Key Development Concepts

### Source of Truth Hierarchy

The repository maintains a strict hierarchy to prevent documentation drift:

1. **SKILL.md** is the canonical source of truth for all behavior and pattern definitions [WARP.md:21]().
2. **README.md** is derived documentation that must be updated to match SKILL.md changes [WARP.md:21]().
3. **WARP.md** is meta-documentation that defines the synchronization rules [WARP.md:1-3]().

**Rule:** Never edit README.md independently. Always edit SKILL.md first, then synchronize README.md according to the rules in WARP.md.

Sources: [WARP.md:12-21]()

### Pattern Numbering Stability

The patterns are numbered 1-29 across both SKILL.md and README.md. Pattern numbers are referenced in:

- [SKILL.md:92-350]() - Detailed pattern definitions with examples.
- User documentation and README pattern summaries.

**Rule:** Keep the pattern numbering stable unless intentionally re-numbering. The numbering in SKILL.md must remain consistent with the README table.

Sources: [WARP.md:49-50](), [SKILL.md:92-350]()

### Versioning Protocol

Version numbers use semantic versioning and must be synchronized:

- **SKILL.md YAML frontmatter:** [SKILL.md:3]() - `version: 2.5.1`
- **README.md version history:** Must contain a matching entry describing changes.

**Rule:** Every version bump requires a corresponding entry in README.md version history describing what changed.

Sources: [WARP.md:42-46](), [SKILL.md:3]()

### Non-Obvious Fixes

When fixing tricky failure modes (e.g., repeated mis-edits or unexpected tone shifts), document the fix in README.md's version history. This helps future maintainers understand why certain prompt instructions exist.

Sources: [WARP.md:51-53]()

---

## Validation Checklist

Before committing changes, verify:

- [ ] YAML frontmatter is syntactically valid [SKILL.md:1-20]().
- [ ] Version number in [SKILL.md:3]() matches the latest entry in README.md.
- [ ] Pattern numbers 1-29 are consistent between SKILL.md and README.md [WARP.md:49-50]().
- [ ] Non-obvious fixes are documented in the version history [WARP.md:51-53]().
- [ ] Both SKILL.md and README.md are committed together to maintain sync.

Sources: [WARP.md:42-53]()

---

## Next Steps

For detailed information on specific maintenance tasks:

- **[Maintenance Guidelines](#5.1)** — Explain WARP.md's role as meta-documentation and the workflow for making changes.
- **[Synchronization Protocol](#5.2)** — Document critical synchronization requirements for versioning and the 29-pattern set.
- **[Version History and Evolution](#5.3)** — Document the history through v2.5.1, including the major v2.0.0 rewrite and recent pattern additions.

Sources: [WARP.md:1-53]()

---

