<!-- source: DeepWiki mcp.deepwiki.com · repo VoltAgent/awesome-agent-skills · page 3 Skill Architecture · fetched 2026-10-26 -->

# Skill Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This document explains the technical architecture of the Agent Skills system, focusing on how skills are defined, discovered, and executed by AI coding assistants. It covers the standardized skill format, file system conventions, and the execution model that enables write-once, run-anywhere portability across multiple AI assistants.

For details about the specific YAML and Markdown structure of skill definitions, see [Skill Definition Format](#3.1). For information about how individual AI assistants integrate with and execute skills, see [AI Assistant Integration](#3.2). For MCP server capabilities within skills, see [MCP Server Integration](#3.3).

**Sources:** [README.md:1-43]()

## Architectural Overview

The Agent Skills system implements a decentralized architecture where skill implementations live in external repositories while discovery and curation happen through this repository. This separation enables independent skill development while maintaining a curated quality bar.

### System Components

```mermaid
graph TB
    subgraph "Curation Layer"
        README["README.md<br/>180+ skill links<br/>organized by team/category"]
        CONTRIB["CONTRIBUTING.md<br/>quality requirements<br/>submission process"]
    end
    
    subgraph "External Repositories"
        SkillImpl["Skill Implementation<br/>YAML front matter<br/>Markdown content<br/>Optional resources"]
        SkillDocs["Documentation<br/>Usage examples<br/>Integration guides"]
    end
    
    subgraph "File System Layer"
        ProjectPaths["Project-Specific Paths<br/>.claude/skills/<br/>.cursor/skills/<br/>.github/skills/<br/>.gemini/skills/<br/>.windsurf/skills/<br/>.agent/skills/<br/>.codex/skills/<br/>.opencode/skills/"]
        GlobalPaths["Global User Paths<br/>~/.claude/skills/<br/>~/.cursor/skills/<br/>~/.copilot/skills/<br/>~/.gemini/skills/<br/>~/.codeium/windsurf/skills/<br/>~/.gemini/antigravity/skills/<br/>~/.codex/skills/<br/>~/.config/opencode/skills/"]
    end
    
    subgraph "Execution Layer"
        Parser["Skill Parser<br/>YAML metadata extraction<br/>Markdown parsing"]
        Context["Context Builder<br/>Skill matching<br/>Instruction loading"]
        Executor["Task Executor<br/>Instruction interpretation<br/>Validation application"]
    end
    
    README -->|"links to"| SkillImpl
    CONTRIB -->|"governs quality of"| SkillImpl
    
    SkillImpl -->|"user copies to"| ProjectPaths
    SkillImpl -->|"user copies to"| GlobalPaths
    
    ProjectPaths --> Parser
    GlobalPaths --> Parser
    
    Parser --> Context
    Context --> Executor
    
    style README fill:#f9f9f9,stroke:#333,stroke-width:3px
    style SkillImpl fill:#f9f9f9,stroke:#333,stroke-width:2px
    style Parser fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Diagram: End-to-End Skill Architecture**

This architecture implements three key design principles:

1. **Decentralized Content, Centralized Discovery**: Skills are maintained in 180+ external repositories but discovered through `README.md`
2. **Standardized Format**: All skills use identical YAML + Markdown structure regardless of AI assistant
3. **Dual-Scope Deployment**: Skills can be installed project-wide or globally per-user

**Sources:** [README.md:1-43](), [README.md:76-88]()

## Skill File Structure

Each skill consists of two required components and one optional component:

### Required Components

| Component | Format | Purpose |
|-----------|--------|---------|
| YAML Front Matter | YAML block between `---` delimiters | Machine-readable metadata for parsing |
| Markdown Content | Standard Markdown | Human-readable instructions for AI agent |

### Optional Component

| Component | Format | Purpose |
|-----------|--------|---------|
| Resources | Additional files | Scripts, configs, examples that support the skill |

**Sources:** [README.md:42-73]()

### YAML Front Matter Fields

```mermaid
graph LR
    YAML["YAML Front Matter"]
    
    YAML --> name["name field<br/>kebab-case identifier"]
    YAML --> description["description field<br/>concise capability summary"]
    
    name -->|"parsed by"| Parser["AI Assistant Parser"]
    description -->|"parsed by"| Parser
    
    Parser --> Indexer["Skill Indexer<br/>enables discovery"]
    Parser --> Matcher["Request Matcher<br/>enables selection"]
```

**Diagram: YAML Metadata Processing**

The `name` field uses kebab-case (e.g., `api-tester`, `web-artifacts-builder`) and serves as the skill's unique identifier. The `description` field provides a brief summary of capabilities, typically 10 words or fewer.

**Sources:** [README.md:44-48]()

### Markdown Content Structure

Skills follow a consistent Markdown structure:

```mermaid
graph TB
    Title["# Skill Title<br/>Human-readable name"]
    Summary["Brief summary paragraph<br/>One-line capability statement"]
    WhenToUse["## When to Use This Skill<br/>Triggering conditions"]
    Instructions["## Instructions<br/>Step-by-step procedures"]
    Validation["## Validation/Response<br/>Success criteria"]
    
    Title --> Summary
    Summary --> WhenToUse
    WhenToUse --> Instructions
    Instructions --> Validation
    
    Instructions -->|"numbered steps"| Step1["1. Action verb + target"]
    Instructions -->|"numbered steps"| Step2["2. Action verb + target"]
    Instructions -->|"numbered steps"| Step3["3. Action verb + target"]
    
    Validation -->|"bullet points"| Check1["- Verify condition"]
    Validation -->|"bullet points"| Check2["- Check requirement"]
```

**Diagram: Skill Markdown Structure**

**Sources:** [README.md:50-72]()

## File System Conventions

The skill system uses standardized directory paths that enable multi-assistant compatibility. Each AI coding assistant recognizes specific directory patterns for skill discovery.

### Directory Path Patterns

```mermaid
graph TB
    subgraph "Project-Scoped Skills"
        ProjectRoot["Project Root Directory"]
        
        ProjectRoot --> claude[".claude/skills/"]
        ProjectRoot --> cursor[".cursor/skills/"]
        ProjectRoot --> github[".github/skills/"]
        ProjectRoot --> gemini[".gemini/skills/"]
        ProjectRoot --> windsurf[".windsurf/skills/"]
        ProjectRoot --> agent[".agent/skills/"]
        ProjectRoot --> codex[".codex/skills/"]
        ProjectRoot --> opencode[".opencode/skills/"]
    end
    
    subgraph "User-Scoped Skills"
        UserHome["User Home Directory ~"]
        
        UserHome --> claudeGlobal["~/.claude/skills/"]
        UserHome --> cursorGlobal["~/.cursor/skills/"]
        UserHome --> copilotGlobal["~/.copilot/skills/"]
        UserHome --> geminiGlobal["~/.gemini/skills/"]
        UserHome --> windsurfGlobal["~/.codeium/windsurf/skills/"]
        UserHome --> antigravityGlobal["~/.gemini/antigravity/skills/"]
        UserHome --> codexGlobal["~/.codex/skills/"]
        UserHome --> opencodeGlobal["~/.config/opencode/skills/"]
    end
    
    claude --> ClaudeCode["Claude Code"]
    cursor --> Cursor["Cursor"]
    github --> Copilot["GitHub Copilot"]
    gemini --> GeminiCLI["Gemini CLI"]
    windsurf --> Windsurf["Windsurf"]
    agent --> Antigravity["Antigravity"]
    codex --> Codex["Codex"]
    opencode --> OpenCode["OpenCode"]
    
    claudeGlobal --> ClaudeCode
    cursorGlobal --> Cursor
    copilotGlobal --> Copilot
    geminiGlobal --> GeminiCLI
    windsurfGlobal --> Windsurf
    antigravityGlobal --> Antigravity
    codexGlobal --> Codex
    opencodeGlobal --> OpenCode
```

**Diagram: File System Path Mapping to AI Assistants**

### Path Resolution Priority

AI assistants typically check paths in this order:

1. Project-specific path (`.assistant/skills/`)
2. Global user path (`~/.assistant/skills/`)

Skills in project-specific paths override identically-named skills in global paths, enabling project-specific customization.

**Sources:** [README.md:76-88]()

## Skill Discovery and Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant README as README.md
    participant ExtRepo as External Repository
    participant FileSystem as File System
    participant Parser as AI Assistant Parser
    participant Executor as AI Executor
    
    User->>README: Browse skills by category
    README->>User: Display skill links
    User->>ExtRepo: Navigate to skill repository
    ExtRepo->>User: View YAML + Markdown
    User->>FileSystem: Copy skill to .assistant/skills/
    
    Note over FileSystem: Skill file stored locally
    
    User->>Parser: Issue task request
    Parser->>FileSystem: Scan .assistant/skills/
    FileSystem->>Parser: Return skill files
    
    Parser->>Parser: Parse YAML front matter
    Parser->>Parser: Extract name, description
    Parser->>Parser: Parse Markdown sections
    
    Parser->>Executor: Load matched skill
    Executor->>Executor: Build execution context
    Executor->>Executor: Interpret instructions
    Executor->>Executor: Execute task steps
    Executor->>Executor: Apply validation rules
    
    Executor->>User: Return task results
```

**Diagram: Skill Discovery and Execution Sequence**

### Processing Stages

| Stage | Component | Input | Output |
|-------|-----------|-------|--------|
| Discovery | `README.md` | User browsing | Skill repository URLs |
| Installation | User action | Skill files | Local `.assistant/skills/` directory |
| Parsing | AI Assistant Parser | YAML + Markdown files | Structured skill metadata |
| Matching | Request Matcher | User task + skill descriptions | Selected skill(s) |
| Execution | Task Executor | Skill instructions + user request | Task results |

**Sources:** [README.md:1-88]()

## Repository Architecture and Boundaries

This repository serves as a curation hub rather than an implementation host. Understanding these boundaries is critical to the architecture.

```mermaid
graph TB
    subgraph "awesome-agent-skills Repository"
        READMEFile["README.md<br/>Lines: 1-394<br/>Importance: 123.19"]
        CONTRIBFile["CONTRIBUTING.md<br/>Lines: 1-40<br/>Importance: 3.02"]
        LICENSEFile["LICENSE<br/>Lines: 1-21<br/>Importance: 1.00"]
    end
    
    subgraph "External Ecosystem"
        AnthropicRepo["github.com/anthropics/skills<br/>15 skills"]
        VercelRepo["github.com/vercel-labs/agent-skills<br/>8 skills"]
        CloudflareRepo["github.com/cloudflare/skills<br/>7 skills"]
        TrailOfBitsRepo["github.com/trailofbits/skills<br/>22 skills"]
        CommunityRepos["100+ community repositories<br/>130+ skills"]
    end
    
    READMEFile -->|"links to"| AnthropicRepo
    READMEFile -->|"links to"| VercelRepo
    READMEFile -->|"links to"| CloudflareRepo
    READMEFile -->|"links to"| TrailOfBitsRepo
    READMEFile -->|"links to"| CommunityRepos
    
    CONTRIBFile -->|"governs PRs to"| READMEFile
    
    AnthropicRepo -.->|"maintained by"| AnthropicTeam["Anthropic Team"]
    VercelRepo -.->|"maintained by"| VercelTeam["Vercel Labs"]
    CloudflareRepo -.->|"maintained by"| CloudflareTeam["Cloudflare Team"]
    TrailOfBitsRepo -.->|"maintained by"| TrailOfBitsTeam["Trail of Bits"]
    CommunityRepos -.->|"maintained by"| CommunityDevs["Community Developers"]
    
    style READMEFile fill:#f9f9f9,stroke:#333,stroke-width:4px
    style CONTRIBFile fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Diagram: Repository Architecture and External Dependencies**

### Responsibility Separation

| Repository | Responsibilities | Does NOT Include |
|------------|------------------|------------------|
| `awesome-agent-skills` | Curate links, maintain quality standards, organize by category | Skill implementations, support, maintenance |
| External skill repositories | Implement skills, provide documentation, support users | Curation, quality gatekeeping |

This architecture enables:
- **Independent skill evolution**: Authors update implementations without touching this repository
- **Quality-controlled discovery**: Only community-proven skills appear in `README.md`
- **Distributed maintenance**: Each team maintains their own skills
- **Single source of truth**: `README.md` remains the canonical skill catalog

**Sources:** [README.md:1-394](), [README.md:374-393]()

## Standardization Benefits

The standardized architecture provides several key benefits:

### Write-Once, Run-Anywhere

```mermaid
graph LR
    SingleSkill["Single Skill Definition<br/>YAML + Markdown"]
    
    SingleSkill -->|"copy to"| Claude[".claude/skills/<br/>Claude Code"]
    SingleSkill -->|"copy to"| Cursor[".cursor/skills/<br/>Cursor"]
    SingleSkill -->|"copy to"| Copilot[".github/skills/<br/>GitHub Copilot"]
    SingleSkill -->|"copy to"| Gemini[".gemini/skills/<br/>Gemini CLI"]
    SingleSkill -->|"copy to"| Windsurf[".windsurf/skills/<br/>Windsurf"]
    SingleSkill -->|"copy to"| Antigravity[".agent/skills/<br/>Antigravity"]
    SingleSkill -->|"copy to"| Codex[".codex/skills/<br/>Codex"]
    SingleSkill -->|"copy to"| OpenCode[".opencode/skills/<br/>OpenCode"]
    
    Claude -->|"identical parsing"| Result["Task Execution"]
    Cursor -->|"identical parsing"| Result
    Copilot -->|"identical parsing"| Result
    Gemini -->|"identical parsing"| Result
    Windsurf -->|"identical parsing"| Result
    Antigravity -->|"identical parsing"| Result
    Codex -->|"identical parsing"| Result
    OpenCode -->|"identical parsing"| Result
```

**Diagram: Cross-Assistant Portability**

### Zero Vendor Lock-In

Because skills use a standardized format independent of any specific AI assistant, users can:
- Switch between assistants without recreating skills
- Use different assistants for different projects
- Share skills across teams using different tools
- Adopt new assistants as they emerge

**Sources:** [README.md:37-88]()

## Integration Points

Skills can integrate with external systems through several mechanisms:

### MCP Server Integration

Skills may reference MCP (Model Context Protocol) servers to access external APIs and services. For detailed information about MCP integration patterns, see [MCP Server Integration](#3.3).

Example skills using MCP servers:
- [README.md:118]() - `anthropics/mcp-builder` for creating MCP servers
- [README.md:146]() - `cloudflare/building-mcp-server-on-cloudflare` for remote MCP servers
- [README.md:361]() - `czlonkowski/n8n-mcp-tools-expert` for n8n MCP tools

### External Tool Integration

Skills can invoke external development tools and CLIs:
- [README.md:119]() - `anthropics/webapp-testing` uses Playwright
- [README.md:302]() - `jthack/ffuf-claude-skill` uses ffuf for web fuzzing
- [README.md:303]() - `lackeyjb/playwright-skill` for browser automation

### API Integration

Skills may call external APIs directly:
- [README.md:244-249]() - `fal-ai-community/*` skills integrate with fal.ai APIs
- [README.md:298]() - `Rootly-AI-Labs/rootly-incident-responder` requires Rootly MCP Server

**Sources:** [README.md:118-119](), [README.md:146](), [README.md:244-249](), [README.md:298](), [README.md:302-303](), [README.md:361]()

## Quality Architecture

The contribution process enforces quality through architectural constraints defined in `CONTRIBUTING.md`:

```mermaid
graph TB
    Submission["Skill Submission PR"]
    
    Submission --> Check1{"Public repository?"}
    Check1 -->|"No"| Reject["Rejection"]
    Check1 -->|"Yes"| Check2{"Documentation exists?"}
    
    Check2 -->|"No"| Reject
    Check2 -->|"Yes"| Check3{"Community usage proven?"}
    
    Check3 -->|"No"| Reject
    Check3 -->|"Yes"| Check4{"Description ≤10 words?"}
    
    Check4 -->|"No"| Reject
    Check4 -->|"Yes"| Review["Maintainer Review"]
    
    Review --> QualityBar{"Meets quality bar?"}
    QualityBar -->|"No"| Reject
    QualityBar -->|"Yes"| Accept["Add to README.md"]
```

**Diagram: Quality Enforcement Flow**

This architectural approach ensures `README.md` contains only battle-tested, community-validated skills rather than experimental projects.

**Sources:** [README.md:374-382]()

---

This skill architecture enables a scalable, decentralized ecosystem where skill creators maintain independence while users benefit from centralized discovery and quality curation. The standardized format ensures skills work across all major AI coding assistants, maximizing utility and minimizing vendor lock-in.

---

