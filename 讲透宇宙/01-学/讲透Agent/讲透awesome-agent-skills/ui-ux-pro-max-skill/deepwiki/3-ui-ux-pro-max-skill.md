<!-- source: DeepWiki mcp.deepwiki.com · repo nextlevelbuilder/ui-ux-pro-max-skill · page 3 UI/UX Pro Max Skill · fetched 2026-10-26 -->

# UI/UX Pro Max Skill

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude/skills/ui-ux-pro-max/SKILL.md](.claude/skills/ui-ux-pro-max/SKILL.md)
- [.claude/skills/ui-ux-pro-max/scripts/core.py](.claude/skills/ui-ux-pro-max/scripts/core.py)
- [.claude/skills/ui-ux-pro-max/scripts/search.py](.claude/skills/ui-ux-pro-max/scripts/search.py)
- [CLAUDE.md](CLAUDE.md)
- [cli/assets/templates/base/skill-content.md](cli/assets/templates/base/skill-content.md)
- [src/ui-ux-pro-max/templates/base/skill-content.md](src/ui-ux-pro-max/templates/base/skill-content.md)

</details>



## Purpose and Overview

The UI/UX Pro Max Skill provides AI coding assistants with design intelligence through a searchable database of 344+ design resources spanning UI styles, color palettes, typography, UX guidelines, and technology-specific best practices. The skill activates automatically or via commands when users request UI/UX work, guiding the AI through a systematic 4-step workflow to generate consistent, professional designs.

**Core Capabilities:**

| Resource Type | Count | Examples |
|---------------|-------|----------|
| UI Styles | 79 | Glassmorphism, Minimalism, Brutalism, AI-Native UI [SKILL.md:3]() |
| Color Palettes | 192 | Industry-specific palettes for SaaS, E-commerce, Fintech [SKILL.md:3]() |
| Font Pairings | 74 | Google Fonts combinations with mood/style keywords [SKILL.md:3]() |
| Chart Types | 25 | Trend, comparison, heatmap with library recommendations [SKILL.md:3]() |
| Tech Stacks | 22 | React, Next.js, Vue, Svelte, SwiftUI, Flutter, Tailwind, shadcn [SKILL.md:3]() |
| UX Guidelines | 119 | Accessibility, performance, responsive design best practices [SKILL.md:3]() |
| GSAP Presets | 17 | Animation skeletons by intensity tier (hover, scroll, stagger) [SKILL.md:3]() |

The skill operates across 18+ AI platforms including Claude Code, Cursor, Windsurf, Trae, and others. For detailed workflow steps, see [Skill Workflow](#3.1). For search domains and technology stacks, see [Search Domains and Stacks](#3.2). For quality validation, see [Pre-Delivery Checklist](#3.3).

**Sources:** [CLAUDE.md:5-28](), [.claude/skills/ui-ux-pro-max/SKILL.md:1-8](), [src/ui-ux-pro-max/scripts/core.py:17-79](), [src/ui-ux-pro-max/scripts/core.py:89-112]()

## Skill Architecture

The skill system bridges natural language requests to structured code entities through a search and reasoning engine.

### System Flow Diagram

```mermaid
graph TB
    subgraph "Natural Language Space"
        UserRequest["User: 'Build SaaS landing page'"]
        AIAssistant["AI Coding Assistant"]
    end

    subgraph "Logic & Search Layer (Code Entity Space)"
        SKILL["SKILL.md<br/>Activation patterns"]
        SearchPy["search.py<br/>CLI interface"]
        CorePy["core.py<br/>BM25 Class<br/>detect_domain()"]
        DesignSys["design_system.py<br/>DesignSystemGenerator"]
    end
    
    subgraph "Data Layer (Code Entity Space)"
        CSV["CSV Databases<br/>styles.csv, colors.csv<br/>typography.csv, charts.csv"]
        Stacks["Stack Guidelines<br/>html-tailwind.csv<br/>react.csv, nextjs.csv"]
        Reasoning["ui-reasoning.csv<br/>Decision Rules"]
    end
    
    UserRequest --> AIAssistant
    AIAssistant --> SKILL
    SKILL --> SearchPy
    SearchPy --> CorePy
    SearchPy --> DesignSys
    
    CorePy --> CSV
    CorePy --> Stacks
    DesignSys --> Reasoning
    DesignSys --> CorePy
    
    CSV --> CorePy
    Stacks --> CorePy
    Reasoning --> DesignSys
    
    DesignSys --> SearchPy
    CorePy --> SearchPy
    SearchPy --> SKILL
    SKILL --> AIAssistant
    AIAssistant --> UserRequest
```

**Component Responsibilities:**

| Component | File | Key Functions/Classes | Purpose |
|-----------|------|----------------------|---------|
| **Skill Definition** | `SKILL.md` | Frontmatter metadata | Defines activation and guides AI through the design process [SKILL.md:1-4]() |
| **CLI Interface** | `scripts/search.py` | `main()` | Entry point for domain/stack searches and design system generation [scripts/search.py:96-120]() |
| **Search Engine** | `scripts/core.py` | `BM25` class, `search()` | Implements probabilistic ranking (k1=1.5, b=0.75) [scripts/core.py:96-156]() |
| **Design Gen** | `scripts/design_system.py` | `generate_design_system()` | Synthesizes multi-domain data into a cohesive spec [scripts/search.py:33]() |
| **Data Repos** | `data/*.csv` | `CSV_CONFIG`, `STACK_CONFIG` | Mapped data for 12 domains and 22 stacks [scripts/core.py:18-112]() |

**Sources:** [CLAUDE.md:41-69](), [.claude/skills/ui-ux-pro-max/SKILL.md:37-64](), [src/ui-ux-pro-max/scripts/core.py:17-156]()

## How the Skill Activates

The skill supports two activation paradigms across 18 supported AI platforms:

**Skill Mode** - Auto-activates when AI detects UI/UX keywords:
- Platforms: Claude Code, Cursor, Windsurf, Augment, Trae, OpenCode, Continue, etc.
- Full content installation with complete knowledge base.
- Detection triggers: "Build landing page", "Design dashboard", "Create UI component".

**Workflow Mode** - Requires explicit slash command or manual invocation:
- Platforms: Kiro, GitHub Copilot, Roo Code.
- Reference content installation with lighter context window usage.

The activation mechanism is defined in `SKILL.md` frontmatter metadata:

```markdown
---
name: ui-ux-pro-max
description: "UI/UX design intelligence for web, mobile, and desktop. This skill should be used when designing, building, reviewing, or fixing interfaces..."
---
```

**Activation Triggers:**

| Trigger Type | Examples | Result |
|--------------|----------|--------|
| **Action Verbs** | designing, building, reviewing, fixing, creating, refactoring [SKILL.md:12]() | Skill activates and begins workflow |
| **Project Types** | web, mobile, desktop, SaaS, e-commerce, portfolio, dashboard [SKILL.md:68]() | Informs product type detection |
| **UI Concerns** | accessibility, interaction, layout, typography, color, charts [SKILL.md:3]() | Guides component-level searches |

For detailed platform-specific integration mechanisms, see page 7.

**Sources:** [.claude/skills/ui-ux-pro-max/SKILL.md:1-15](), [src/ui-ux-pro-max/templates/base/skill-content.md:25-35]()

## Skill Workflow Overview

When activated, the skill guides AI assistants through a systematic 4-step process.

### Workflow Execution Flow

```mermaid
sequenceDiagram
    participant AI["AI Assistant"]
    participant SKILL["SKILL.md"]
    participant SearchPy["search.py"]
    participant DesignSys["design_system.py"]
    participant CorePy["core.py"]
    
    Note over SKILL: Step 1: Analyze Requirements
    SKILL->>SKILL: Extract product, style, audience, stack
    
    Note over SKILL: Step 2: Generate Design System
    SKILL->>SearchPy: python3 search.py "<query>" --design-system
    SearchPy->>DesignSys: generate_design_system()
    DesignSys->>CorePy: Multi-domain search()
    CorePy-->>DesignSys: Ranked results
    DesignSys-->>SearchPy: Synthesized System
    SearchPy-->>SKILL: Markdown Design System
    
    Note over SKILL: Step 3: Supplement Searches
    SKILL->>SearchPy: python3 search.py "<query>" --domain <domain>
    SearchPy->>CorePy: search()
    CorePy-->>SearchPy: Domain-specific guidelines
    SearchPy-->>SKILL: Results
    
    Note over SKILL: Step 4: Stack Guidelines
    SKILL->>SearchPy: python3 search.py "<query>" --stack <stack>
    SearchPy->>CorePy: search_stack()
    CorePy-->>SearchPy: Code-specific patterns
    SearchPy-->>SKILL: Implementation rules
```

| Step | Purpose | Search Command |
|------|---------|----------------|
| **1. Analyze** | Extract product type, audience, style keywords, and stack | N/A [SKILL.md:65-72]() |
| **2. Generate** | Create a comprehensive design system spec (Master + Overrides) | `--design-system --persist -p "Project"` [SKILL.md:73-101]() |
| **3. Supplement** | Get additional domain-specific details (e.g., icons, gsap, ux) | `--domain <domain>` [SKILL.md:102-108]() |
| **4. Stack** | Get implementation best practices for the tech stack | `--stack <stack>` [SKILL.md:109-121]() |

For detailed workflow instructions, see [Skill Workflow](#3.1). For search domain and stack options, see [Search Domains and Stacks](#3.2).

**Sources:** [.claude/skills/ui-ux-pro-max/SKILL.md:65-121](), [src/ui-ux-pro-max/templates/base/skill-content.md:37-128]()

## Search Engine and BM25 Implementation

The skill uses a BM25 probabilistic ranking algorithm implemented in `core.py` to score document relevance.

**BM25 Parameters:**

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `k1` | 1.5 | Term frequency saturation parameter [src/ui-ux-pro-max/scripts/core.py:102]() |
| `b` | 0.75 | Document length normalization factor [src/ui-ux-pro-max/scripts/core.py:103]() |

**Key Search Logic:**

1.  **Tokenization**: `BM25.tokenize()` filters words with length > 2 and removes punctuation [src/ui-ux-pro-max/scripts/core.py:109-112]().
2.  **Domain Detection**: `detect_domain()` uses keyword scoring to route queries to the correct CSV file [src/ui-ux-pro-max/scripts/core.py:202-221]().
3.  **Scoring**: `BM25.score()` calculates TF-IDF scores across the corpus [src/ui-ux-pro-max/scripts/core.py:133-155]().

**Sources:** [src/ui-ux-pro-max/scripts/core.py:96-254](), [CLAUDE.md:71]()

## Pre-Delivery Checklist

After implementation, the skill applies a quality assurance checklist to ensure the UI meets professional standards. This includes:

- **Accessibility**: Contrast ratios (4.5:1), keyboard navigation, and Aria-labels [SKILL.md:22]().
- **Performance**: WebP/AVIF usage, lazy loading, and CLS optimization [SKILL.md:24]().
- **Interaction**: Touch target sizes (44x44px), loading feedback, and haptics [SKILL.md:23]().
- **Visuals**: Semantic color tokens, SVG icons (no emoji), and responsive breakpoints [SKILL.md:25-27]().

For the complete quality validation process, see [Pre-Delivery Checklist](#3.3).

**Sources:** [.claude/skills/ui-ux-pro-max/SKILL.md:20-31](), [.claude/skills/ui-ux-pro-max/SKILL.md:136-172]()

---

