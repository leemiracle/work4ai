<!-- source: DeepWiki mcp.deepwiki.com · repo obra/superpowers · page 8 Creating Skills · fetched 2026-10-26 -->

# Creating Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/executing-plans/SKILL.md](skills/executing-plans/SKILL.md)
- [skills/using-superpowers/references/gemini-tools.md](skills/using-superpowers/references/gemini-tools.md)
- [skills/writing-skills/SKILL.md](skills/writing-skills/SKILL.md)
- [skills/writing-skills/anthropic-best-practices.md](skills/writing-skills/anthropic-best-practices.md)

</details>



This page documents the complete methodology for creating new skills in the Superpowers system. Skills are markdown-based process documentation that AI agents discover and follow when working on tasks. The creation process follows Test-Driven Development (TDD) principles adapted for documentation: you must observe agent failures before writing guidance, then iteratively bulletproof against rationalization.

For information about the skills system architecture and how skills are discovered, see [Skills Discovery and Resolution](#4.5). For details on specific existing skills, see [Key Skills Reference](#7).

**Sources:** [skills/writing-skills/SKILL.md:1-18](), [skills/writing-skills/SKILL.md:30-45]()

---

## What is a Skill?

A **skill** is a reference guide for proven techniques, patterns, or tools stored as a markdown file (`SKILL.md`) with YAML frontmatter. Skills help AI agents find and apply effective approaches consistently across projects and sessions.

**Skills are:**
- Reusable techniques, patterns, and tools [skills/writing-skills/SKILL.md:26-26]()
- Reference guides for future AI instances [skills/writing-skills/SKILL.md:24-24]()
- Concrete methods with steps (Techniques) [skills/writing-skills/SKILL.md:63-65]()
- Ways of thinking about problems (Patterns) [skills/writing-skills/SKILL.md:66-68]()

**Skills are NOT:**
- Narratives about solving one specific problem [skills/writing-skills/SKILL.md:28-28]()
- One-off solutions [skills/writing-skills/SKILL.md:50-50]()
- Standard practices well-documented elsewhere [skills/writing-skills/SKILL.md:51-51]()
- Project-specific conventions (those go in `CLAUDE.md` or `GEMINI.md`) [skills/writing-skills/SKILL.md:58-58](), [skills/using-superpowers/references/gemini-tools.md:24-24]()
- Mechanical constraints enforceable by automation [skills/writing-skills/SKILL.md:59-59]()

**Sources:** [skills/writing-skills/SKILL.md:22-71](), [skills/using-superpowers/references/gemini-tools.md:24-24]()

---

## Skill Structure and Organization

### Directory Structure

Skills follow a flat namespace structure to ensure they are easily searchable [skills/writing-skills/SKILL.md:82-82](). Personal skills are stored in agent-specific directories like `~/.claude/skills` for Claude Code or `~/.gemini/skills/` for Gemini CLI [skills/writing-skills/SKILL.md:12-12](), [skills/using-superpowers/references/gemini-tools.md:28-28](). All runtimes recognize `~/.agents/skills/` as a cross-runtime alias [skills/writing-skills/SKILL.md:12-12]().

```
skills/
  skill-name/
    SKILL.md              # Main reference (required)
    supporting-file.*     # Heavy reference or reusable tools (optional)
```

**Sources:** [skills/writing-skills/SKILL.md:12-12](), [skills/writing-skills/SKILL.md:72-82](), [skills/using-superpowers/references/gemini-tools.md:28-28]()

### SKILL.md Format

The `SKILL.md` file must follow a specific structure for discovery and readability. The frontmatter must include a `name` and a `description` field [skills/writing-skills/SKILL.md:95-96]().

**Diagram: Skill Entity Mapping**

```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        SKILLmd["SKILL.md"]
        YAMLFrontmatter["YAML Frontmatter"]
        OverviewSection["Overview Section"]
        WhenToUseSection["When to Use Section"]
        CorePatternSection["Core Pattern Section"]
        CommonMistakesSection["Common Mistakes Section"]
    end

    subgraph "CodeEntitySpace"
        SkillDiscoveryAlgorithm["Skill Discovery Algorithm"]
        CSO["Skill Discovery Optimization (CSO)"]
        ActivateSkill["activate_skill"]
    end

    YAMLFrontmatter -- "name, description" --> SkillDiscoveryAlgorithm
    YAMLFrontmatter -- "triggering conditions" --> CSO
    WhenToUseSection -- "symptoms, triggers" --> CSO
    CorePatternSection -- "implementation code" --> ActivateSkill
```

For a detailed breakdown of the `SKILL.md` structure, see [SKILL.md Format and Structure](#8.2).

**Sources:** [skills/writing-skills/SKILL.md:93-140](), [skills/writing-skills/anthropic-best-practices.md:147-153](), [skills/using-superpowers/references/gemini-tools.md:17-17]()

---

## The TDD Methodology for Skills

**Writing skills IS Test-Driven Development applied to process documentation.** The core principle is: "If you didn't watch an agent fail without the skill, you don't know if the skill teaches the right thing" [skills/writing-skills/SKILL.md:10-16]().

### The RED-GREEN-REFACTOR Cycle

| TDD Concept | Skill Creation Application |
|-------------|----------------------------|
| **Test case** | Pressure scenario with subagent [skills/writing-skills/SKILL.md:34-34]() |
| **Production code** | The `SKILL.md` document [skills/writing-skills/SKILL.md:35-35]() |
| **Test fails (RED)** | Agent violates rule without skill (baseline) [skills/writing-skills/SKILL.md:36-36]() |
| **Test passes (GREEN)** | Agent complies with skill present [skills/writing-skills/SKILL.md:37-37]() |
| **Refactor** | Close loopholes and rationalizations [skills/writing-skills/SKILL.md:38-38]() |

For more details on this process, see [Test-Driven Development for Skills](#8.1).

**Sources:** [skills/writing-skills/SKILL.md:30-45]()

---

## Skill Discovery Optimization (SDO)

SDO is critical for discovery. Future AI instances must be able to FIND the skill when they need it. At startup, only metadata (name and description) is pre-loaded; the full `SKILL.md` is only read when it becomes relevant [skills/writing-skills/anthropic-best-practices.md:20-20]().

### The Description Field

The YAML frontmatter `description` field is the primary signal for discovery.

- **Required Format:** Start with "Use when..." to focus on triggering conditions [skills/writing-skills/SKILL.md:148-148]().
- **Constraint:** The description should ONLY describe triggering conditions. **NEVER summarize the skill's process or workflow** in the description [skills/writing-skills/SKILL.md:150-152]().
- **Reasoning:** Summarizing workflow creates a "shortcut" that causes the AI to skip reading the full skill body [skills/writing-skills/SKILL.md:158-159]().
- **Perspective:** Always write in the third person [skills/writing-skills/anthropic-best-practices.md:189-191]().

**Diagram: Description Field Optimization**

```mermaid
graph TD
    subgraph "Skill.md Frontmatter"
        NameField["name: Skill-Name-With-Hyphens"]
        DescriptionField["description: Use when [specific triggering conditions and symptoms]"]
    end

    subgraph "Agent Discovery Process"
        AgentReadsDescription["Agent reads description to decide skill relevance"]
        SkillLoaded["Skill (SKILL.md) loaded into context"]
        SkillSkipped["Skill skipped"]
    end

    DescriptionField -- "Focus on triggering conditions" --> AgentReadsDescription
    AgentReadsDescription -- "Matches conditions" --> SkillLoaded
    AgentReadsDescription -- "No match" --> SkillSkipped

    style DescriptionField fill:#fff,stroke:#333,stroke-width:2px
    style AgentReadsDescription fill:#fff,stroke:#333,stroke-width:2px
```

For detailed optimization principles, see [Skill Discovery Optimization (CSO)](#8.4).

**Sources:** [skills/writing-skills/SKILL.md:140-182](), [skills/writing-skills/anthropic-best-practices.md:20-20](), [skills/writing-skills/anthropic-best-practices.md:185-195]()

---

## Testing Skills with Pressure Scenarios

To verify a skill works, you must design "Pressure Scenarios" that force the AI to choose between following the rule or taking a "pragmatic" shortcut.

**Diagram: Pressure Scenario Execution**

```mermaid
graph LR
    subgraph "Scenario Design"
        TimePressure["Time Pressure"]
        SunkCost["Sunk Cost"]
        AuthorityPressure["Authority Pressure"]
    end

    subgraph "Agent Behavior"
        ActionForcingChoice["Action-Forcing Choice"]
        RationalizedShortcutFAIL["Rationalized Shortcut (FAIL)"]
        SkillCompliancePASS["Skill Compliance (PASS)"]
    end

    TimePressure & SunkCost & AuthorityPressure --> ActionForcingChoice
    ActionForcingChoice -- "Violates Skill" --> RationalizedShortcutFAIL
    ActionForcingChoice -- "Follows Skill" --> SkillCompliancePASS
```

**Pressure Scenario Requirements:**
- Combine 3+ pressures (e.g., time, exhaustion, authority).
- Provide concrete, action-forcing options (A, B, or C).
- Allow no "easy outs" (e.g., "I would ask the user").

For details on designing these tests, see [Testing Skills with Pressure Scenarios](#8.3).

**Sources:** [skills/writing-skills/SKILL.md:34-43]()

---

## Contributor Guidelines

The Superpowers project maintains high standards for skill contributions.

- **Pre-submission:** Verify the problem exists in core and confirm it is not project-specific [skills/writing-skills/SKILL.md:58-58]().
- **Conciseness:** Agents are already smart; only add context they don't have [skills/writing-skills/anthropic-best-practices.md:22-28]().
- **Naming:** Use **gerund form** (verb + -ing) for skill names where possible [skills/writing-skills/anthropic-best-practices.md:157-166]().

For more details, see [Contributing Skills](#8.6).

**Sources:** [skills/writing-skills/SKILL.md:49-60](), [skills/writing-skills/anthropic-best-practices.md:9-28](), [skills/writing-skills/anthropic-best-practices.md:155-166]()

---

## Child Pages

- [Test-Driven Development for Skills](#8.1) — Detailed RED-GREEN-REFACTOR cycle for documentation.
- [SKILL.md Format and Structure](#8.2) — Technical specification for the markdown and frontmatter.
- [Testing Skills with Pressure Scenarios](#8.3) — How to design scenarios that break weak documentation.
- [Skill Discovery Optimization (CSO)](#8.4) — Principles for making skills discoverable.
- [Skill Creation Checklist](#8.5) — Step-by-step guide for authors.
- [Contributing Skills](#8.6) — Workflow for pull requests and community contributions.

**Sources:** [skills/writing-skills/SKILL.md:1-137](), [skills/writing-skills/anthropic-best-practices.md:1-200]()

---

