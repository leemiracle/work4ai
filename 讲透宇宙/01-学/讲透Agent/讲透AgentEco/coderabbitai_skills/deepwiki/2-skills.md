<!-- source: DeepWiki mcp.deepwiki.com · repo coderabbitai/skills · page 2 Skills · fetched 2026-10-27 -->

# Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/autofix/SKILL.md](skills/autofix/SKILL.md)
- [skills/autofix/github.md](skills/autofix/github.md)
- [skills/code-review/SKILL.md](skills/code-review/SKILL.md)
- [skills/code-review/references/auth-recovery.md](skills/code-review/references/auth-recovery.md)

</details>



## Purpose and Scope

The `skills/` directory serves as the portable core of the repository, providing structured, agent-agnostic markdown specifications (`SKILL.md`) that instruct host AI agents on how to execute code reviews, process review threads, and interact with the CodeRabbit CLI and GitHub APIs. This page provides a high-level overview of the core skill definitions, their CLI bindings, GitHub workflow integrations, and security constraints.

Sources: `skills/code-review/SKILL.md:1-18`, `skills/autofix/SKILL.md:1-24`

---

## 2. Skills Overview

The skills core acts as an execution bridge between natural language user prompts and programmatic command-line tools. Each skill defines its frontmatter metadata, trigger patterns, prerequisites, and step-by-step execution workflows.

```mermaid
graph TD
    NL[""Natural Language Request: Review Code""] --> SKILL[""skills/code-review/SKILL.md""]
    SKILL --> CLI[""coderabbit review --agent""]
    CLI --> NDJSON[""NDJSON Severity Stream (critical, major, minor)""]

    style NL fill:none,stroke:#333,stroke-width:2px
    style SKILL fill:none,stroke:#333,stroke-width:2px
    style CLI fill:none,stroke:#333,stroke-width:2px
    style NDJSON fill:none,stroke:#333,stroke-width:2px
```
*Figure 1: Bridging Natural Language Review Prompts to the CodeRabbit CLI execution contract.*

Sources: `skills/code-review/SKILL.md:1-30`, `skills/autofims/SKILL.md:1-25`

---

## 2.1 code-review Skill

The `code-review` skill (`[skills/code-review/SKILL.md:1-145]()`) governs how AI agents invoke the CodeRabbit CLI, parse agent-optimized NDJSON output, maintain severity categorizations (`critical`, `major`, `minor`, `trivial`, `info`, `none`), and execute autonomous fix-verification loops.

For deep technical details on triggers, CLI invocation parameters, and parsing contracts, see [code-review Skill](#2.1).

### 2.1.1 CLI Flags & Review Scopes
The skill defines precise scope selection rules to govern what code is submitted for analysis, including default tracked changes, `--committed`, `--uncommitted`, `--include-untracked`, `--base`, `--base-commit`, and `--dir <path>`. Conflict rules strictly forbid combining `--committed` with `--uncommitted` or `--include-untracked`.

Sources: `skills/code-review/SKILL.md:65-80`

### 2.1.2 Authentication & Recovery
Before executing any review, agents must validate host authentication via `auth status --agent` within a controlled execution boundary. The skill outlines recovery mechanisms for handling sandbox communication errors such as `credentials_unavailable` and `callback_listener_unavailable`.

Sources: `skills/code-review/SKILL.md:31-41`, `skills/code-review/references/auth-recovery.md:1-65`

Sources for Section 2.1: `skills/code-review/SKILL.md:1-137`, `skills/code-review/references/auth-recovery.md:1-65`

---

## 2.2 autofix Skill

The `autofix` skill (`[skills/autofix/SKILL.md:1-336]()`) manages pull request review threads, leveraging GitHub GraphQL APIs to extract CodeRabbit feedback items, derive actionable fixes, apply local modifications, and post summary verification comments.

```mermaid
graph TD
    PR[""GitHub PR Review Threads""] --> GHAPI[""gh api graphql (reviewThreads query)""]
    GHAPI --> NODES[""Filter: isResolved == false & isOutdated == false""]
    NODES --> FIX[""skills/autofix/SKILL.md: Apply Validated Fixes""]
    FIX --> COMM[""skills/autofix/github.md: gh pr comment""]

    style PR fill:none,stroke:#333,stroke-width:2px
    style GHAPI fill:none,stroke:#333,stroke-width:2px
    style NODES fill:none,stroke:#333,stroke-width:2px
    style FIX fill:none,stroke:#333,stroke-width:2px
    style COMM fill:none,stroke:#333,stroke-width:2px
```
*Figure 2: Bridging PR Review Feedback to Automated Fix Execution and GitHub Comment Posting.*

For details on the 10-step PR fix workflow, manual review modes, and consolidated commits, see [autofix Skill](#2.2).

### 2.2.1 GitHub Primitives (`github.md`)
Reusable command blocks for repository and PR resolution, pagination logic, and comment reporting are decoupled into `[skills/autofix/github.md:1-145]()`.

Sources for Section 2.2: `skills/autofix/SKILL.md:1-196`, `skills/autofix/github.md:1-146`

---

## 2.3 Security Model for Skills

All review outputs, comment bodies, and embedded instructions (such as `Prompt for AI Agents` blocks) are treated as untrusted input. Agents are strictly prohibited from executing reviewer-provided commands directly, must perform secret-scanning prior to transmitting diffs, and are bound by read-only subagent constraints during thread evaluation.

For complete coverage of the security posture, see [Security Model for Skills](#2.3).

Sources: `skills/code-review/SKILL.md:44-46`, `skills/autofix/SKILL.md:26-27`

---

