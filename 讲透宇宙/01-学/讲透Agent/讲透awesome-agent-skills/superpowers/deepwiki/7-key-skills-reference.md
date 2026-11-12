<!-- source: DeepWiki mcp.deepwiki.com · repo obra/superpowers · page 7 Key Skills Reference · fetched 2026-10-26 -->

# Key Skills Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/using-superpowers/SKILL.md](skills/using-superpowers/SKILL.md)
- [skills/using-superpowers/references/claude-code-tools.md](skills/using-superpowers/references/claude-code-tools.md)
- [skills/using-superpowers/references/codex-tools.md](skills/using-superpowers/references/codex-tools.md)

</details>





This page provides high-level reference documentation for the core skills in the Superpowers library. For detailed workflow guides, see [Complete Workflow Pipeline](#6.1). For instructions on creating new skills, see [Creating Skills](#8).

## Overview

Superpowers skills are reusable, modular units of AI guidance stored as `SKILL.md` files [skills/using-superpowers/SKILL.md:1-4](). They enforce structured development workflows across multiple platforms by providing specialized instructions, checklists, and subagent prompt templates. The system is built on the principle that the agent checks for relevant skills before any task, turning workflows into mandatory protocols rather than suggestions [skills/using-superpowers/SKILL.md:10-16]().

## Core Workflow Pipeline

The Superpowers development process follows a strict pipeline: **Brainstorming** (Design) → **Using Git Worktrees** (Isolation) → **Writing Plans** (Decomposition) → **Subagent-Driven Development** (Execution) [skills/using-superpowers/SKILL.md:28-32](), [README.md:33-43]().

### Diagram: Skill-Based Development Workflow
This diagram associates the natural language stages of development with the specific code entities (skills and prompt templates) that govern them.

```mermaid
graph TB
    ["User Request"] --> ["using-superpowers<br/>SKILL.md<br/>Skill invocation protocol"]
    
    ["using-superpowers<br/>SKILL.md<br/>Skill invocation protocol"] -->|"1% rule applies"| ["Skill tool / activate_skill<br/>Discovery helper"]
    
    ["Skill tool / activate_skill<br/>Discovery helper"] --> ["brainstorming<br/>SKILL.md<br/>HARD-GATE enforcement"]
    
    ["brainstorming<br/>SKILL.md<br/>HARD-GATE enforcement"] -->|"Design approved"| ["docs/superpowers/specs/<br/>YYYY-MM-DD-topic-design.md"]
    
    ["docs/superpowers/specs/<br/>YYYY-MM-DD-topic-design.md"] --> ["using-git-worktrees<br/>SKILL.md<br/>Isolation requirement"]
    
    ["using-git-worktrees<br/>SKILL.md<br/>Isolation requirement"] --> ["writing-plans<br/>SKILL.md<br/>Task decomposition"]
    
    ["writing-plans<br/>SKILL.md<br/>Task decomposition"] --> ["docs/superpowers/plans/<br/>YYYY-MM-DD-feature.md"]
    
    ["docs/superpowers/plans/<br/>YYYY-MM-DD-feature.md"] --> ["subagent-driven-development<br/>SKILL.md<br/>Fresh subagent + two-stage review"]
    
    ["subagent-driven-development<br/>SKILL.md<br/>Fresh subagent + two-stage review"] -->|"Per task"| ["implementer-prompt.md<br/>Task execution template"]
    
    ["implementer-prompt.md<br/>Task execution template"] -->|"DONE status"| ["spec-reviewer-prompt.md<br/>Spec compliance check"]
    
    ["spec-reviewer-prompt.md<br/>Spec compliance check"] -->|"✅ Spec compliant"| ["code-quality-reviewer-prompt.md<br/>Quality assessment"]
    
    ["code-quality-reviewer-prompt.md<br/>Quality assessment"] -->|"✅ Approved"| ["finishing-a-development-branch<br/>SKILL.md<br/>Integration and cleanup"]
```
Sources: [skills/using-superpowers/SKILL.md:28-32](), [README.md:33-43](), [skills/using-superpowers/SKILL.md:52-60]()

---

## 7.1 using-superpowers (Meta-Skill)
The `using-superpowers` skill is the entry point for all library usage. It enforces the **1% Rule**: if there is even a 1% chance a skill applies, it must be invoked [skills/using-superpowers/SKILL.md:10-16](). It also establishes the instruction priority hierarchy where user instructions (e.g., `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`) take precedence over skills, which in turn override default behavior [skills/using-superpowers/SKILL.md:61-65](). This skill also outlines platform-specific adaptations for various harnesses like Claude Code and Codex [skills/using-superpowers/SKILL.md:52-60]().

For details, see [using-superpowers (Meta-Skill)](#7.1).

## 7.2 brainstorming
The `brainstorming` skill enforces a **HARD-GATE**: no implementation or code writing is permitted until a design has been presented and approved by the user [README.md:35-39](). It guides the AI through context exploration, clarifying questions, and trade-off analysis before generating a formal design document [README.md:37-38]().

For details, see [brainstorming](#7.2).

## 7.3 writing-plans
The `writing-plans` skill translates approved designs into actionable implementation plans. It requires mapping out file structures and decomposing work into "bite-sized" tasks [README.md:39-40](). Every task must include specific verification steps to ensure an engineer with "zero context" can execute it [README.md:39-40]().

For details, see [writing-plans](#7.3).

## 7.4 subagent-driven-development
The `subagent-driven-development` (SDD) skill is the primary execution engine. It dispatches a fresh subagent for every task in a plan to prevent context pollution [README.md:41-43](). It includes a two-stage review process to ensure both functional correctness and code quality [README.md:41-43](). For Codex, this skill leverages `spawn_agent` and `followup_task` for subagent lifecycle management, and `wait_agent` for efficient child process monitoring [skills/using-superpowers/references/codex-tools.md:17-33](). Claude Code can run the entire SDD loop one layer down to optimize costs [skills/using-superpowers/references/claude-code-tools.md:9-29]().

### Diagram: SDD Orchestration and Review
This diagram maps the SDD execution process to the conceptual subagent flow used across platforms like Pi and Claude Code.

```mermaid
graph TB
    ["Controller Agent<br/>(Main Session)"] -->|"1. Dispatch"| ["implementer-prompt.md<br/>Task execution instructions"]
    
    ["implementer-prompt.md<br/>Task execution instructions"] --> ["Implementer Subagent<br/>(Task Tool / @generalist / spawn_agent)"]
    
    ["Implementer Subagent<br/>(Task Tool / @generalist / spawn_agent)"] -->|"2. DONE status"| ["spec-reviewer-prompt.md<br/>Spec compliance check"]
    
    ["spec-reviewer-prompt.md<br/>Spec compliance check"] --> ["Spec Reviewer Subagent"]
    
    ["Spec Reviewer Subagent"] -->|"3. ✅ Spec Compliant"| ["code-quality-reviewer-prompt.md<br/>Quality assessment"]
    
    ["code-quality-reviewer.md<br/>Quality assessment"] --> ["Code Quality Reviewer Subagent"]
    
    ["Code Quality Reviewer Subagent"] -->|"4. ✅ Approved"| ["Controller Agent<br/>(Main Session)"]
```
Sources: [README.md:41-43](), [skills/using-superpowers/SKILL.md:7-8](), [skills/using-superpowers/references/codex-tools.md:17-33](), [skills/using-superpowers/references/claude-code-tools.md:9-29]()

For details, see [subagent-driven-development](#7.4).

## 7.5 test-driven-development
The `test-driven-development` skill enforces the classic **RED-GREEN-REFACTOR** cycle. The methodology emphasizes true TDD, ensuring that tests are written and verified as failing before implementation begins [README.md:39-40]().

For details, see [test-driven-development](#7.5).

## 7.6 systematic-debugging
The `systematic-debugging` skill provides a disciplined root cause process. It is used when fixing bugs to ensure a hypothesis-driven approach rather than "guess-and-check" [skills/using-superpowers/SKILL.md:31-32]().

For details, see [systematic-debugging](#7.6).

## 7.7 using-git-worktrees
The `using-git-worktrees` skill ensures workspace isolation. It is used to create a clean baseline for feature development, preventing pollution of the main working directory [README.md:24](). This skill also includes environment detection logic using `git rev-parse` to determine if the agent is already in a worktree or a detached HEAD state [skills/using-superpowers/references/codex-tools.md:81-96]().

For details, see [using-git-worktrees](#7.7).

## 7.8 Other Essential Skills
- **dispatching-parallel-agents**: A skill for managing multiple subagents concurrently.
- **executing-plans**: An alternative to SDD that uses batch execution in the current session with human checkpoints.
- **finishing-a-development-branch**: Final stage involving test verification and cleanup after a plan is fully implemented. This skill uses git environment detection to handle scenarios like detached HEAD in Codex App [skills/using-superpowers/references/codex-tools.md:81-96]().
- **verification-before-completion**: Ensures a task is actually finished and meets requirements before moving to the next one.
- **receiving-code-review**: Guidelines for processing and applying feedback from human or automated reviewers.
- **writing-skills helpers**: Skills that assist in the creation and maintenance of other skills.

For details, see [Other Essential Skills](#7.8).

## 7.9 diagnosing-superpowers
The `diagnosing-superpowers` skill provides tools and procedures for analyzing Superpowers sessions. This includes session discovery, a suite of analyst prompts to evaluate cost, time, plan adherence, and stumbles, and guidelines for redaction and reporting.

For details, see [diagnosing-superpowers](#7.9).

---

