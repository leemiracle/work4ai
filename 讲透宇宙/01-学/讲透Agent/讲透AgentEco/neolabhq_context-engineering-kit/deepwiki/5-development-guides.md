<!-- source: DeepWiki mcp.deepwiki.com · repo neolabhq/context-engineering-kit · page 5 Development Guides · fetched 2026-10-27 -->

# Development Guides

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/guides/brainstorming-to-implementation.md](docs/guides/brainstorming-to-implementation.md)
- [docs/guides/bug-investigation.md](docs/guides/bug-investigation.md)
- [docs/guides/code-quality-improvement.md](docs/guides/code-quality-improvement.md)
- [docs/guides/decision-making.md](docs/guides/decision-making.md)
- [docs/guides/feature-development.md](docs/guides/feature-development.md)
- [docs/guides/project-setup.md](docs/guides/project-setup.md)
- [docs/plugins/reflexion/usage-examples.md](docs/plugins/reflexion/usage-examples.md)

</details>



This document provides an overview of practical workflows that combine multiple plugins from the Context Engineering Kit to accomplish complete development tasks. Each workflow is designed to leverage specific plugin combinations for maximum effectiveness by bridging natural language requirements with precise code entities.

These guides demonstrate end-to-end processes from initial task conception through completion and knowledge capture. For information about individual plugin capabilities, see [Plugin Reference](#3). For understanding the underlying architecture of how plugins work together, see [Core Concepts](#2).

## Overview

Development guides are organized into seven major workflow categories, each addressing a specific phase or type of development work:

| Workflow | Primary Focus | Key Plugins Used |
|----------|--------------|------------------|
| [Feature Development Workflow](#5.1) | Standard features with quality gates | `reflexion`, `code-review`, `git`, `tdd` |
| [Spec-Driven Development Workflow](#5.2) | Complex features requiring planning | `sdd`, `mcp`, `tdd`, `docs` |
| [Bug Investigation & Root Cause Analysis](#5.3) | Root cause analysis and systematic fixes | `kaizen`, `reflexion`, `git` |
| [PR Review Workflow](#5.4) | Comprehensive pull request analysis | `code-review`, `git` |
| [CI/CD Integration](#5.5) | Automated quality checks | `code-review` (GitHub Actions) |
| [Code Quality Improvement](#5.6) | Systematic refactoring and optimization | `kaizen`, `reflexion`, `code-review` |
| [Project Setup & Context Enhancement](#5.7) | Initial configuration and context | `tech-stack`, `mcp`, `ddd`, `docs` |

**Sources:** [docs/guides/feature-development.md:14-19](), [docs/guides/bug-investigation.md:14-19](), [docs/guides/project-setup.md:12-17]()

## Workflow Architecture

### Plugin Command Flow in Development Workflows

The following diagram maps specific development scenarios to the actual plugin commands executed during each workflow phase:

```mermaid
graph TB
    subgraph StandardFeature["Standard Feature Development"]
        SF_Start["User: Implement feature X"]
        SF_Impl["Claude: Implementation"]
        SF_Test["/tdd:write-tests"]
        SF_Review["/code-review:review-local-changes"]
        SF_Reflect["/reflexion:reflect"]
        SF_Memorize["/reflexion:memorize"]
        SF_Commit["/git:commit"]
    end
    
    subgraph ComplexFeature["Complex Feature with SDD"]
        CF_Start["User: /sdd:brainstorm"]
        CF_Setup["/sdd:add-task"]
        CF_Plan["/sdd:plan"]
        CF_Impl["/sdd:implement"]
        CF_PR["/git:create-pr"]
    end
    
    subgraph BugFix["Bug Investigation"]
        BF_Start["/git:analyze-issue"]
        BF_Trace["/kaizen:root-cause-tracing"]
        BF_Five["/kaizen:why"]
        BF_Fix["Claude: Implement fix"]
        BF_Review["/code-review:review-local-changes"]
        BF_Memorize["/reflexion:memorize"]
        BF_Commit["/git:commit"]
    end
    
    SF_Start --> SF_Impl --> SF_Test --> SF_Review --> SF_Reflect --> SF_Memorize --> SF_Commit
    CF_Start --> CF_Setup --> CF_Plan --> CF_Impl --> CF_PR
    BF_Start --> BF_Trace --> BF_Five --> BF_Fix --> BF_Review --> BF_Memorize --> BF_Commit
```

**Sources:** [docs/guides/feature-development.md:25-65](), [docs/guides/brainstorming-to-implementation.md:25-58](), [docs/guides/bug-investigation.md:25-72]()

### Mapping Natural Language to Code Entity Space

This diagram illustrates how high-level development intent is translated into specific code-level entities and plugin operations.

```mermaid
graph LR
    subgraph NL_Space["Natural Language Space (Intent)"]
        Requirement["'Add email validation'"]
        BugReport["'Rate limit is broken'"]
        Improvement["'Optimize checkout'"]
    end

    subgraph Plugin_Bridge["Plugin Orchestration"]
        SDD_B["/sdd:brainstorm"]
        K_Trace["/kaizen:root-cause-tracing"]
        K_Analyze["/kaizen:analyse"]
    end

    subgraph Code_Entity_Space["Code Entity Space (Implementation)"]
        SpecFile[".specs/tasks/todo/*.md"]
        LogicFile["src/validators/email.ts"]
        TestFile["tests/unit/email.test.ts"]
        MemoryFile["CLAUDE.md"]
        AuditFile[".fpf/knowledge/L2/"]
    end

    Requirement --> SDD_B
    BugReport --> K_Trace
    Improvement --> K_Analyze

    SDD_B --> SpecFile
    K_Trace --> LogicFile
    K_Analyze --> LogicFile

    LogicFile --> TestFile
    TestFile --> MemoryFile
    AuditFile -.-> MemoryFile
```

**Sources:** [docs/guides/brainstorming-to-implementation.md:141-157](), [docs/guides/bug-investigation.md:86-93](), [docs/guides/decision-making.md:183-193]()

## Workflow Categories

### 5.1 Feature Development Workflow
A lightweight workflow for standard features. It uses `claude "implement X, then reflect"` for immediate self-correction, followed by `/tdd:write-tests` and `/code-review:review-local-changes` to ensure quality before a conventional `/git:commit`.
For details, see [Feature Development Workflow](#5.1).
**Sources:** [docs/guides/feature-development.md:1-135]()

### 5.2 Spec-Driven Development (SDD) Workflow
Designed for complex features. It begins with `/sdd:brainstorm` to refine requirements through Q&A. It progresses through `/sdd:add-task` (creating draft specs in `.specs/tasks/draft/`) and `/sdd:plan` before `/sdd:implement` executes the changes using specialized subagents.
For details, see [Spec-Driven Development Workflow](#5.2).
**Sources:** [docs/guides/brainstorming-to-implementation.md:1-179]()

### 5.3 Bug Investigation & Root Cause Analysis
A systematic approach using the Kaizen plugin. It involves `/git:analyze-issue` to load context, `/kaizen:root-cause-tracing` to follow the call stack, and `/kaizen:why` (Five Whys) to identify systemic failures. The fix is verified with `/reflexion:reflect` and documented via `/reflexion:memorize`.
For details, see [Bug Investigation & Root Cause Analysis](#5.3).
**Sources:** [docs/guides/bug-investigation.md:1-151]()

### 5.4 PR Review Workflow
A comprehensive process for reviewing code. It utilizes `/code-review:review-pr` for remote pull requests and `/code-review:review-local-changes` for iterative local fixes. The review is performed by 6 specialized agents (Bug Hunter, Security Auditor, etc.) to ensure multi-perspective coverage.
For details, see [PR Review Workflow](#5.4).
**Sources:** [docs/guides/code-quality-improvement.md:121-130](), [docs/plugins/reflexion/usage-examples.md:207-211]()

### 5.5 CI/CD Integration
Automates the code review process by integrating `anthropics/claude-code-action` into GitHub Actions. This allows for automated "sticky" comments on PRs from the 6-agent review system, ensuring every change meets project standards before human review.
For details, see [CI/CD Integration](#5.5).

### 5.6 Code Quality Improvement
Focuses on technical debt and optimization. It employs `/kaizen:analyse` (Gemba Walk/Muda Analysis) to find waste and `/kaizen:plan-do-check-act` (PDCA) to run measurable improvement experiments. Results are captured in `CLAUDE.md` using `/reflexion:memorize`.
For details, see [Code Quality Improvement](#5.6).
**Sources:** [docs/guides/code-quality-improvement.md:1-150]()

### 5.7 Project Setup & Context Enhancement
The foundation for new projects. It uses `/tech-stack:add-typescript-best-practices` (or equivalent) to populate `CLAUDE.md`, `/ddd:setup-code-formating` for architecture standards, and `/mcp:setup-codemap-cli` to enable session hooks that keep the AI's view of the codebase synchronized.
For details, see [Project Setup & Context Enhancement](#5.7).
**Sources:** [docs/guides/project-setup.md:1-116]()

## Decision Making & Reasoning

For architectural decisions with long-term impact, the **First Principles Framework (FPF)** is integrated into these workflows.

```mermaid
graph TD
    subgraph FPF_Process["FPF Decision Logic"]
        H0["/fpf:propose-hypotheses<br/>(L0 Conjecture)"]
        H1["Verify Logic<br/>(L1 Substantiated)"]
        H2["Validate Evidence<br/>(L2 Corroborated)"]
        Trust["Audit Trust<br/>(WLNK Principle)"]
        DRR["Decision Readiness Report"]
    end

    subgraph Storage["Entity Storage"]
        L0_Dir[".fpf/knowledge/L0/"]
        L1_Dir[".fpf/knowledge/L1/"]
        L2_Dir[".fpf/knowledge/L2/"]
        Dec_Dir[".fpf/decisions/"]
    end

    H0 --> L0_Dir
    L0_Dir --> H1
    H1 --> L1_Dir
    L1_Dir --> H2
    H2 --> L2_Dir
    L2_Dir --> Trust
    Trust --> DRR
    DRR --> Dec_Dir
```

**Sources:** [docs/guides/decision-making.md:28-75](), [docs/guides/decision-making.md:183-193]()

## Summary of Configuration Artifacts

Workflows are supported by the following core configuration files:

| File Path | Purpose | Primary Plugin |
|-----------|---------|----------------|
| `CLAUDE.md` | Project-wide AI instructions and memorized patterns | `reflexion`, `tech-stack` |
| `.specs/tasks/` | Task definitions and implementation plans | `sdd` |
| `.fpf/` | Architectural hypotheses and audit trails | `fpf` |
| `.claude/settings.json` | Automation hooks (Pre/PostToolUse) | `mcp` (codemap) |

**Sources:** [docs/guides/project-setup.md:109-116](), [docs/guides/brainstorming-to-implementation.md:141-157](), [docs/guides/decision-making.md:85-91]()

---

