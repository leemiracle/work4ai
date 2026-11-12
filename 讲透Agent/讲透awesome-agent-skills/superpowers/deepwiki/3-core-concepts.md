<!-- source: DeepWiki mcp.deepwiki.com · repo obra/superpowers · page 3 Core Concepts · fetched 2026-10-26 -->

# Core Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/using-superpowers/SKILL.md](skills/using-superpowers/SKILL.md)
- [skills/using-superpowers/references/claude-code-tools.md](skills/using-superpowers/references/claude-code-tools.md)
- [skills/using-superpowers/references/codex-tools.md](skills/using-superpowers/references/codex-tools.md)

</details>



This page explains the fundamental concepts that underpin the Superpowers system: what skills are, how they are structured, and the mandatory protocols that ensure AI agents follow them across various platforms.

## What Are Skills

Skills are reusable, modular units of AI guidance that provide structured workflows for coding agents. Unlike static prompts, skills are dynamic instructions that agents discover and invoke via specific tools based on the current task [README.md:3-5](). They represent the core logic of the Superpowers methodology, transforming an AI from a simple code generator into a disciplined engineering partner [README.md:33-43]().

### Skill File Structure

Every skill is defined in a `SKILL.md` file within a dedicated directory [README.md:218-249](). They follow a specific format that combines metadata for discovery and content for execution.

**Part 1: YAML Frontmatter**
The frontmatter contains the skill's identity and its "trigger" description, which the agent uses to match the current context [skills/using-superpowers/SKILL.md:1-4]().

```yaml
---
name: brainstorming
description: Use when starting any creative work—creating features, building components, adding functionality, or modifying behavior
---
```

**Part 2: Markdown Content**
The body of the skill contains the actual instructions, often including:
*   **Instruction Priority**: Defining how the skill interacts with user instructions [skills/using-superpowers/SKILL.md:61-63]().
*   **Process Flow**: Defined instructions that ensure unambiguous execution [skills/using-superpowers/SKILL.md:18-25]().
*   **Red Flags**: A table of common rationalizations agents use to skip the skill, with corresponding reality checks [skills/using-superpowers/SKILL.md:33-51]().

**Sources:** [skills/using-superpowers/SKILL.md:1-4](), [skills/using-superpowers/SKILL.md:18-25](), [skills/using-superpowers/SKILL.md:33-51](), [skills/using-superpowers/SKILL.md:61-63](), [README.md:218-249]()

### Platform Tool Mapping

While skills are written using Claude Code tool names (like `Skill`, `Task`, and `TodoWrite`), they are designed to be cross-platform. The system maps these to native equivalents on other platforms [skills/using-superpowers/SKILL.md:52-59](). For instance, Pi uses a specialized extension to map these to its native tools and injects the bootstrap after compaction [README.md:233-247]().

| Claude Code Tool | Pi Equivalent | Codex Equivalent |
| :--- | :--- | :--- |
| `Skill` | Native Skill system | `references/codex-tools.md` |
| `TodoWrite` | Task-list tool | Native plan tracking |
| `Task` | `subagent` | `spawn_agent` |
| `Read`/`Write`/`Edit` | `read`/`write`/`edit` | Native file tools |

**Sources:** [skills/using-superpowers/SKILL.md:52-59](), [README.md:233-247](), [README.md:100-116]()

For details, see [What Are Skills](#3.1).

## The Mandatory Skill Check Protocol

Superpowers is built on a "Mandatory, not Suggested" philosophy. This is enforced by the `using-superpowers` meta-skill, which establishes how to find and use skills [skills/using-superpowers/SKILL.md:2-3]().

### The 1% Rule
The system enforces a strict discipline: if there is even a **1% chance** a skill might apply to the current task, the agent **must** invoke the skill [skills/using-superpowers/SKILL.md:10-16](). This check must happen before any response, including clarifying questions or exploring the codebase [skills/using-superpowers/SKILL.md:18-20]().

### Rationalization Table
The `using-superpowers` skill includes a "Red Flags" table to explicitly counter common rationalizations an agent might use to avoid invoking a skill [skills/using-superpowers/SKILL.md:33-51](). This table serves as a direct instruction to prevent agents from deviating from the protocol.

### Instruction Priority Hierarchy
To ensure the user remains in control, Superpowers follows a strict priority:
1.  **User's explicit instructions** (e.g., `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, direct requests) — **Highest** [skills/using-superpowers/SKILL.md:61-63]()
2.  **Superpowers skills** — Overrides default behavior [skills/using-superpowers/SKILL.md:63]()
3.  **Default system behavior** — **Lowest** [skills/using-superpowers/SKILL.md:63]()

**Sources:** [skills/using-superpowers/SKILL.md:10-20](), [skills/using-superpowers/SKILL.md:33-51](), [skills/using-superpowers/SKILL.md:61-63]()

For details, see [The Mandatory Skill Check Protocol](#3.2).

## Finding and Invoking Skills

Agents do not "know" all skills at once. Instead, they use a discovery mechanism to find the right tool for the job.

### Discovery Flow
When an agent receives a message, it follows this logic:

**Skill Discovery and Invocation Logic**
```mermaid
graph TD
    "User Message Received" --> "Mandatory Skill Check Protocol"
    "Mandatory Skill Check Protocol" -- "1% Rule Applies?" --> "Invoke Skill Mechanism"
    "Mandatory Skill Check Protocol" -- "No Skill Applies" --> "Respond Normally"
    "Invoke Skill Mechanism" --> "Match 'description' in SKILL.md Frontmatter"
    "Match 'description' in SKILL.md Frontmatter" --> "Follow Skill Exactly"
    
    subgraph "Code Entity Mapping"
        "Mandatory Skill Check Protocol" -.-> "skills/using-superpowers/SKILL.md"
        "Invoke Skill Mechanism" -.-> "Skill Tool (e.g., Claude Code 'Skill')"
        "Match 'description' in SKILL.md Frontmatter" -.-> "YAML Frontmatter Parsing"
    end
```

**Sources:** [skills/using-superpowers/SKILL.md:10-25](), [README.md:3-4](), [README.md:233-247]()

For details, see [Finding and Invoking Skills](#3.3).

## Skill Priority and Overriding

When multiple skills apply, the system follows a specific resolution order to prevent conflicting instructions and ensure process discipline.

### Process vs. Implementation
If multiple core skills apply, agents are instructed to prioritize **Process skills** (like `brainstorming` or `systematic-debugging`) over **Implementation skills**. This ensures the "How" is decided before the "What" is executed [skills/using-superpowers/SKILL.md:26-32]().

**Workflow Tier Hierarchy**
```mermaid
graph LR
    "User Task" --> "Process Tier"
    "Process Tier" --> "Determine Strategy"
    "Determine Strategy" --> "Implementation Tier"
    "Implementation Tier" --> "Execute Code"

    subgraph "Process Tier"
        "brainstorming [skills/brainstorming/SKILL.md]"
        "systematic-debugging [skills/systematic-debugging/SKILL.md]"
    end

    subgraph "Implementation Tier"
        "test-driven-development [skills/test-driven-development/SKILL.md]"
        "writing-plans [skills/writing-plans/SKILL.md]"
    end
```

**Sources:** [skills/using-superpowers/SKILL.md:26-32](), [README.md:33-43]()

For details, see [Skill Priority and Overriding](#3.4).

---

