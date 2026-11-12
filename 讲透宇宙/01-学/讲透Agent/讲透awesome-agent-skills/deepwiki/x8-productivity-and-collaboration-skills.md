<!-- source: DeepWiki mcp.deepwiki.com · repo VoltAgent/awesome-agent-skills · extra page Productivity and Collaboration Skills · fetched 2026-10-26 -->

# Productivity and Collaboration Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This page documents the 20+ community-contributed skills focused on productivity tools and team collaboration. These skills enable AI coding assistants to interact with popular productivity platforms (Notion, Linear, Slack, WhatsApp), generate presentation materials (PPT, HTML slides), coordinate multi-agent workflows, and analyze team communication patterns.

For development-focused skills including testing and CI/CD, see [Development and Testing Skills](#4.2.1). For marketing automation skills, see [Marketing Skills](#4.2.2). For advanced agent orchestration patterns, see [Context Engineering Skills](#4.2.4).

**Sources:** [README.md:271-291]()

## Skill Categories

The Productivity and Collaboration skill collection is organized into six functional categories, each addressing specific workflow needs:

```mermaid
graph TB
    subgraph "Productivity and Collaboration Skills"
        DocTools["Document & Presentation<br/>• Notion integration<br/>• PPT generation<br/>• HTML slides<br/>• NotebookLM<br/>• README generation"]
        CommTools["Communication Platforms<br/>• WhatsApp integration<br/>• WhatsApp automation<br/>• Delivery debugging"]
        ProjMgmt["Project Management<br/>• Linear issues<br/>• Linear projects<br/>• Linear teams"]
        TeamCollab["Team Analysis<br/>• Meeting insights<br/>• Communication patterns"]
        MetaProd["Meta-Productivity<br/>• Brainstorming<br/>• Plan writing<br/>• Plan execution<br/>• Agent coordination<br/>• Skill sharing"]
        MediaTools["Media Enhancement<br/>• Image quality improvement"]
    end
    
    DocTools --> Workflow["Productivity Workflows"]
    CommTools --> Workflow
    ProjMgmt --> Workflow
    TeamCollab --> Workflow
    MetaProd --> Workflow
    MediaTools --> Workflow
```

**Sources:** [README.md:271-291]()

## Repository Structure and Code Entities

The skills in this category are distributed across multiple external repositories, each with distinct organizational patterns:

```mermaid
graph TB
    subgraph "notiondevs Repository"
        NotionSkills["Notion Skills for Claude<br/>Collection page"]
    end
    
    subgraph "op7418/NanoBanana-PPT-Skills"
        PPTMain["PPT Skills<br/>Document analysis<br/>Styled image generation"]
    end
    
    subgraph "zarazhangrui/frontend-slides"
        HTMLSlides["frontend-slides<br/>Animation-rich HTML<br/>Visual style previews"]
    end
    
    subgraph "gokapso/agent-skills"
        WhatsAppIntegrate["skills/integrate-whatsapp<br/>Webhook setup<br/>Message sending"]
        WhatsAppAutomate["skills/automate-whatsapp<br/>Workflow builders<br/>Agent integration"]
        WhatsAppObserve["skills/observe-whatsapp<br/>Delivery debugging<br/>Health checks"]
    end
    
    subgraph "obra/superpowers"
        SuperpowersLab["superpowers-lab<br/>Lab environment"]
        Brainstorming["skills/brainstorming/SKILL.md"]
        WritingPlans["skills/writing-plans/SKILL.md"]
        ExecutingPlans["skills/executing-plans/SKILL.md"]
        DispatchAgents["skills/dispatching-parallel-agents/SKILL.md"]
        SharingSkills["skills/sharing-skills/SKILL.md"]
        UsingSuperpowers["skills/using-superpowers/SKILL.md"]
    end
    
    subgraph "wrsmith108/linear-claude-skill"
        LinearSkill["Linear integration<br/>Issue management<br/>Project coordination"]
    end
    
    subgraph "ComposioHQ/awesome-claude-skills"
        MeetingInsights["meeting-insights-analyzer<br/>Communication patterns"]
        ImageEnhancer["image-enhancer<br/>Quality improvement"]
    end
    
    subgraph "PleasePrompto/notebooklm-skill"
        NotebookLM["NotebookLM integration<br/>Document conversations"]
    end
    
    subgraph "Shpigford/skills"
        ReadmeGen["readme<br/>Project documentation"]
    end
```

**Sources:** [README.md:273-290]()

## Document and Presentation Skills

These skills enable AI agents to create, manipulate, and generate various document formats for presentations and documentation:

| Skill | Repository | Primary Functions |
|-------|-----------|-------------------|
| **Notion Skills** | `notiondevs/Notion Skills for Claude` | Notion workspace integration, database operations, page creation |
| **NanoBanana-PPT-Skills** | `op7418/NanoBanana-PPT-Skills` | AI-powered PPT generation, document analysis, styled image insertion |
| **frontend-slides** | `zarazhangrui/frontend-slides` | HTML presentation generation, animation integration, visual style previews |
| **notebooklm-skill** | `PleasePrompto/notebooklm-skill` | NotebookLM API interaction, document-based Q&A |
| **readme** | `Shpigford/skills/tree/main/readme` | Comprehensive project documentation generation |

### Integration Architecture

```mermaid
graph LR
    Agent["AI Agent"]
    
    Agent --> NotionAPI["Notion API<br/>Databases, Pages, Blocks"]
    Agent --> NotebookLMAPI["NotebookLM API<br/>Document ingestion, Q&A"]
    Agent --> LocalPPT["Local PPT Generation<br/>python-pptx library<br/>Image styling"]
    Agent --> HTMLGen["HTML Generator<br/>Animation frameworks<br/>CSS/JS libraries"]
    Agent --> MarkdownGen["Markdown Generator<br/>README templates<br/>Documentation structure"]
    
    NotionAPI --> NotionWorkspace["Notion Workspace"]
    NotebookLMAPI --> NotebookLMDocs["NotebookLM Documents"]
    LocalPPT --> PPTFile["PowerPoint File"]
    HTMLGen --> HTMLPresentation["HTML Presentation"]
    MarkdownGen --> ReadmeFile["README.md"]
```

**Sources:** [README.md:273-276](), [README.md:279](), [README.md:290]()

## Communication Platform Skills

Three related skills from the `gokapso/agent-skills` repository provide comprehensive WhatsApp integration capabilities:

```mermaid
graph TB
    subgraph "gokapso/agent-skills Repository"
        IntegrateSkill["skills/integrate-whatsapp<br/>Connection setup<br/>Webhook configuration<br/>Message sending API"]
        AutomateSkill["skills/automate-whatsapp<br/>Workflow builders<br/>Agent orchestration<br/>Event handling"]
        ObserveSkill["skills/observe-whatsapp<br/>Delivery tracking<br/>Health monitoring<br/>Debug tooling"]
    end
    
    IntegrateSkill --> WhatsAppAPI["WhatsApp Business API"]
    AutomateSkill --> WhatsAppAPI
    ObserveSkill --> WhatsAppAPI
    
    WhatsAppAPI --> Webhooks["Webhook Endpoints"]
    WhatsAppAPI --> Messages["Message Queue"]
    WhatsAppAPI --> Status["Delivery Status"]
```

### WhatsApp Skills Workflow

```mermaid
sequenceDiagram
    participant Agent
    participant IntegrateSkill as integrate-whatsapp
    participant AutomateSkill as automate-whatsapp
    participant ObserveSkill as observe-whatsapp
    participant WhatsAppAPI as WhatsApp API
    
    Agent->>IntegrateSkill: Setup connection
    IntegrateSkill->>WhatsAppAPI: Configure webhooks
    WhatsAppAPI-->>IntegrateSkill: Connection established
    
    Agent->>AutomateSkill: Build automation
    AutomateSkill->>WhatsAppAPI: Register workflows
    WhatsAppAPI-->>AutomateSkill: Workflow active
    
    Agent->>AutomateSkill: Trigger message send
    AutomateSkill->>WhatsAppAPI: Send message
    WhatsAppAPI-->>AutomateSkill: Message queued
    
    Agent->>ObserveSkill: Check delivery status
    ObserveSkill->>WhatsAppAPI: Query health
    WhatsAppAPI-->>ObserveSkill: Status report
    ObserveSkill-->>Agent: Delivery insights
```

**Sources:** [README.md:276-278]()

## Project Management Skills

The Linear integration skill provides comprehensive project management capabilities:

| Skill Component | Repository Path | Functionality |
|----------------|----------------|---------------|
| **Linear Integration** | `wrsmith108/linear-claude-skill` | Issue creation, status updates, assignment management |
| **Project Operations** | `wrsmith108/linear-claude-skill` | Project lifecycle, milestone tracking, roadmap planning |
| **Team Coordination** | `wrsmith108/linear-claude-skill` | Team member management, workload distribution, notifications |

```mermaid
graph TB
    Agent["AI Agent"]
    
    Agent --> LinearSkill["linear-claude-skill"]
    
    LinearSkill --> IssueOps["Issue Operations<br/>Create, update, close<br/>Labels, assignees<br/>Priorities"]
    LinearSkill --> ProjectOps["Project Operations<br/>Milestones<br/>Roadmaps<br/>Timelines"]
    LinearSkill --> TeamOps["Team Operations<br/>Member management<br/>Workload tracking<br/>Notifications"]
    
    IssueOps --> LinearAPI["Linear GraphQL API"]
    ProjectOps --> LinearAPI
    TeamOps --> LinearAPI
    
    LinearAPI --> LinearWorkspace["Linear Workspace<br/>Issues, Projects, Teams"]
```

**Sources:** [README.md:289]()

## Meta-Productivity Skills (obra/superpowers)

The `obra/superpowers` repository contains seven interconnected skills that form a meta-productivity framework for coordinating AI agent workflows:

```mermaid
graph TB
    subgraph "obra/superpowers Repository"
        SuperpowersLab["superpowers-lab<br/>Lab environment setup"]
        
        subgraph "Planning Skills"
            Brainstorming["skills/brainstorming/SKILL.md<br/>Idea generation and exploration"]
            WritingPlans["skills/writing-plans/SKILL.md<br/>Strategic documentation creation"]
            ExecutingPlans["skills/executing-plans/SKILL.md<br/>Plan implementation"]
        end
        
        subgraph "Coordination Skills"
            DispatchAgents["skills/dispatching-parallel-agents/SKILL.md<br/>Multi-agent coordination"]
            SharingSkills["skills/sharing-skills/SKILL.md<br/>Capability distribution"]
            UsingSuperpowers["skills/using-superpowers/SKILL.md<br/>Platform capabilities"]
        end
    end
    
    SuperpowersLab --> Brainstorming
    Brainstorming --> WritingPlans
    WritingPlans --> ExecutingPlans
    
    ExecutingPlans --> DispatchAgents
    DispatchAgents --> SharingSkills
    SharingSkills --> UsingSuperpowers
    
    UsingSuperpowers -.->|feedback loop| Brainstorming
```

### Meta-Productivity Workflow Pattern

```mermaid
sequenceDiagram
    participant User
    participant Brainstorm as brainstorming
    participant WritePlan as writing-plans
    participant ExecutePlan as executing-plans
    participant Dispatch as dispatching-parallel-agents
    
    User->>Brainstorm: Request idea exploration
    Brainstorm-->>User: Generated ideas
    
    User->>WritePlan: Request strategic plan
    WritePlan-->>User: Plan documentation
    
    User->>ExecutePlan: Implement plan
    ExecutePlan->>Dispatch: Requires parallel work
    
    Dispatch->>Dispatch: Spawn sub-agents
    Note over Dispatch: Agent 1: Task A<br/>Agent 2: Task B<br/>Agent 3: Task C
    
    Dispatch-->>ExecutePlan: Results aggregated
    ExecutePlan-->>User: Plan completed
```

**Sources:** [README.md:280-286]()

## Team Analysis and Enhancement Skills

Skills for analyzing team communication and enhancing media quality:

```mermaid
graph LR
    Agent["AI Agent"]
    
    Agent --> MeetingAnalyzer["meeting-insights-analyzer<br/>ComposioHQ/awesome-claude-skills"]
    Agent --> ImageEnhancer["image-enhancer<br/>ComposioHQ/awesome-claude-skills"]
    
    MeetingAnalyzer --> MeetingData["Meeting Transcripts<br/>Participant data<br/>Communication logs"]
    MeetingData --> Insights["Communication Patterns<br/>Engagement metrics<br/>Action items"]
    
    ImageEnhancer --> InputImages["Input Images<br/>Low quality<br/>Poor lighting"]
    InputImages --> EnhancedImages["Enhanced Images<br/>Improved quality<br/>Better composition"]
```

**Sources:** [README.md:287-288]()

## Skill Installation Paths

All productivity and collaboration skills follow the standard AI assistant installation conventions:

| AI Assistant | Project-Specific Path | Global Path |
|-------------|----------------------|-------------|
| **Claude Code** | `.claude/skills/` | `~/.claude/skills/` |
| **Cursor** | `.cursor/skills/` | `~/.cursor/skills/` |
| **GitHub Copilot** | `.github/skills/` | `~/.copilot/skills/` |
| **Gemini CLI** | `.gemini/skills/` | `~/.gemini/skills/` |
| **Windsurf** | `.windsurf/skills/` | `~/.codeium/windsurf/skills/` |
| **Antigravity** | `.agent/skills/` | `~/.gemini/antigravity/skills/` |
| **Codex** | `.codex/skills/` | `~/.codex/skills/` |
| **OpenCode** | `.opencode/skills/` | `~/.config/opencode/skills/` |

Users copy skill files from external repositories to these paths based on whether they need project-specific or user-wide availability.

**Sources:** [README.md:76-87]()

## Common Integration Patterns

### Pattern 1: API-Based Integration

Skills like `linear-claude-skill`, `integrate-whatsapp`, and Notion skills interact with external SaaS platforms via REST or GraphQL APIs:

```mermaid
graph LR
    SkillFile["Skill YAML+Markdown<br/>.claude/skills/linear.md"]
    Agent["AI Agent Runtime"]
    APIClient["API Client<br/>HTTP/GraphQL"]
    
    SkillFile --> Agent
    Agent --> APIClient
    APIClient --> ExternalAPI["External API<br/>Linear/WhatsApp/Notion"]
    ExternalAPI --> ExternalService["External Service<br/>Data persistence"]
    
    ExternalAPI -.->|responses| APIClient
    APIClient -.->|results| Agent
```

### Pattern 2: Local Generation

Skills like `NanoBanana-PPT-Skills`, `frontend-slides`, and `readme` generate artifacts locally without external API dependencies:

```mermaid
graph LR
    SkillFile["Skill Definition"]
    Agent["AI Agent"]
    Generator["Local Generator<br/>python-pptx, HTML, Markdown"]
    
    SkillFile --> Agent
    Agent --> Generator
    Generator --> OutputFile["Generated Artifact<br/>.pptx, .html, .md"]
```

### Pattern 3: Meta-Coordination

The `obra/superpowers` skills coordinate multiple agents or workflows through a hierarchical orchestration pattern:

```mermaid
graph TB
    MainAgent["Main Agent<br/>using-superpowers"]
    
    MainAgent --> SubAgent1["Sub-Agent 1<br/>brainstorming"]
    MainAgent --> SubAgent2["Sub-Agent 2<br/>writing-plans"]
    MainAgent --> SubAgent3["Sub-Agent 3<br/>executing-plans"]
    
    SubAgent3 --> ParallelDispatch["dispatching-parallel-agents"]
    ParallelDispatch --> Worker1["Worker Agent 1"]
    ParallelDispatch --> Worker2["Worker Agent 2"]
    ParallelDispatch --> WorkerN["Worker Agent N"]
```

**Sources:** [README.md:271-291]()

## Skill Definition Structure

All productivity and collaboration skills follow the standard YAML + Markdown format defined in the skill specification:

```yaml
---
name: skill-name
description: Brief description (≤10 words)
---

# Skill Title

Description of what the skill does.

## When to Use This Skill

Use cases and triggering conditions.

## Instructions

Step-by-step execution instructions for the AI agent.

## Validation

Expected outputs and success criteria.
```

For detailed skill structure specifications, see [Skill Definition Format](#3.1).

**Sources:** [README.md:44-72]()

## Usage Example: Linear Project Management Workflow

A typical workflow combining multiple productivity skills:

```mermaid
sequenceDiagram
    participant User
    participant BrainstormSkill as brainstorming
    participant PlanSkill as writing-plans
    participant LinearSkill as linear-claude-skill
    participant ReadmeSkill as readme
    
    User->>BrainstormSkill: "Generate feature ideas"
    BrainstormSkill-->>User: Idea list
    
    User->>PlanSkill: "Create implementation plan"
    PlanSkill-->>User: Strategic plan document
    
    User->>LinearSkill: "Create Linear issues from plan"
    LinearSkill-->>User: Issues created in Linear
    
    User->>ReadmeSkill: "Generate project README"
    ReadmeSkill-->>User: README.md with feature documentation
```

**Sources:** [README.md:280-290]()

## External Dependencies

Many productivity and collaboration skills require external service accounts or API keys:

| Skill Category | Required Services | Authentication |
|---------------|------------------|----------------|
| **Notion Skills** | Notion account, Notion API key | OAuth 2.0 or API token |
| **Linear Integration** | Linear workspace, API key | GraphQL API token |
| **WhatsApp Skills** | WhatsApp Business API account | Business API credentials |
| **NotebookLM** | Google account, NotebookLM access | Google OAuth |
| **Meeting Insights** | Meeting platform integration | Platform-specific API keys |

Skills that generate artifacts locally (PPT, HTML, README) do not require external authentication.

**Sources:** [README.md:273-290]()

## Skill Repository Maintenance

The productivity and collaboration skills are maintained by their respective authors:

- **notiondevs**: Notion Skills collection
- **op7418**: NanoBanana-PPT-Skills
- **zarazhangrui**: frontend-slides
- **gokapso**: WhatsApp integration suite
- **PleasePrompto**: NotebookLM skill
- **obra**: Superpowers meta-productivity framework
- **wrsmith108**: Linear integration
- **ComposioHQ**: Meeting insights and image enhancement
- **Shpigford**: README generator

For issues or feature requests, users should contact the repository maintainers directly via their GitHub repositories.

**Sources:** [README.md:271-291]()

---

