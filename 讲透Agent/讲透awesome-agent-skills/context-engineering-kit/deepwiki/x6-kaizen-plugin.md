<!-- source: DeepWiki mcp.deepwiki.com · repo NeoLabHQ/context-engineering-kit · extra page Kaizen Plugin · fetched 2026-10-26 -->

# Kaizen Plugin

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [plugins/kaizen/skills/analyse-problem/SKILL.md](plugins/kaizen/skills/analyse-problem/SKILL.md)
- [plugins/kaizen/skills/analyse/SKILL.md](plugins/kaizen/skills/analyse/SKILL.md)
- [plugins/kaizen/skills/cause-and-effect/SKILL.md](plugins/kaizen/skills/cause-and-effect/SKILL.md)
- [plugins/kaizen/skills/kaizen/SKILL.md](plugins/kaizen/skills/kaizen/SKILL.md)
- [plugins/kaizen/skills/plan-do-check-act/SKILL.md](plugins/kaizen/skills/plan-do-check-act/SKILL.md)
- [plugins/kaizen/skills/root-cause-tracing/SKILL.md](plugins/kaizen/skills/root-cause-tracing/SKILL.md)
- [plugins/kaizen/skills/why/SKILL.md](plugins/kaizen/skills/why/SKILL.md)

</details>



The Kaizen Plugin is a continuous improvement toolkit inspired by the Toyota Production System (TPS) and Lean manufacturing principles, adapted specifically for software development. It provides a structured framework for systematic problem analysis, root cause investigation, and iterative improvement cycles, moving beyond surface-level fixes to address fundamental systemic issues [plugins/kaizen/skills/kaizen/SKILL.md:6-14]().

## Architecture & Data Flow

The Kaizen plugin is implemented as a set of specialized commands and a persistent skill. It provides structured prompts and methodologies that guide the primary AI agent through rigorous analytical frameworks.

### Code Entity Space to System Mapping

The following diagram maps the logical Kaizen concepts to the specific code entities within the plugin structure.

**Diagram: Kaizen System to Code Entity Mapping**
```mermaid
graph TD
    subgraph "Natural Language Space (Methodologies)"
        "Five Whys"["Five Whys"]
        "Fishbone Analysis"["Fishbone Analysis"]
        "A3 Problem Solving"["A3 Problem Solving"]
        "PDCA Cycle"["PDCA Cycle"]
        "Waste Analysis"["Muda (Waste) Analysis"]
        "Root Cause Tracing"["Root Cause Tracing"]
        "Gemba Walk"["Gemba Walk"]
    end

    subgraph "Code Entity Space (plugins/kaizen/skills/)"
        "C_WHY"["why/SKILL.md"]
        "C_CE"["cause-and-effect/SKILL.md"]
        "C_A3"["analyse-problem/SKILL.md"]
        "C_PDCA"["plan-do-check-act/SKILL.md"]
        "C_AN"["analyse/SKILL.md"]
        "C_RT"["root-cause-tracing/SKILL.md"]
        "S_KAI"["kaizen/SKILL.md"]
    end

    "Five Whys" --> "C_WHY"
    "Fishbone Analysis" --> "C_CE"
    "A3 Problem Solving" --> "C_A3"
    "PDCA Cycle" --> "C_PDCA"
    "Waste Analysis" --> "C_AN"
    "Root Cause Tracing" --> "C_RT"
    "Gemba Walk" --> "C_AN"
    
    "C_AN" -- "Selects based on target" --> "C_WHY"
    "C_AN" -- "Selects based on target" --> "C_CE"
    
    "S_KAI" -- "Enforces mindset for" --> "C_RT"
    "S_KAI" -- "Enforces mindset for" --> "C_PDCA"
```
Sources: [plugins/kaizen/skills/kaizen/SKILL.md:1-10](), [plugins/kaizen/skills/analyse/SKILL.md:1-12](), [plugins/kaizen/skills/root-cause-tracing/SKILL.md:1-4]()

## Core Implementation Components

### 1. The Kaizen Skill (`kaizen:kaizen`)
The `kaizen` skill is a persistent context provider that guides the AI's mindset during code implementation, refactoring, and architectural design. It enforces four pillars of improvement [plugins/kaizen/skills/kaizen/SKILL.md:1-10]().

**The Four Pillars of Kaizen Skill**:
*   **Continuous Improvement**: Prioritizes small, frequent improvements that compound over time [plugins/kaizen/skills/kaizen/SKILL.md:29-31]().
*   **Poka-Yoke (Error Proofing)**: Focuses on designing systems that prevent errors at compile-time (e.g., using exhaustive type unions or branded types to make invalid states unrepresentable) [plugins/kaizen/skills/kaizen/SKILL.md:133-144](), [plugins/kaizen/skills/kaizen/SKILL.md:170-185]().
*   **Standardized Work**: Encourages following established patterns and documenting what works [plugins/kaizen/skills/kaizen/SKILL.md:8-12]().
*   **Just-In-Time (JIT)**: Building only what is needed now to avoid over-engineering and premature optimization [plugins/kaizen/skills/kaizen/SKILL.md:12-14]().

Sources: [plugins/kaizen/skills/kaizen/SKILL.md:1-10](), [plugins/kaizen/skills/kaizen/SKILL.md:29-31](), [plugins/kaizen/skills/kaizen/SKILL.md:133-144]()

### 2. Analysis Commands

The plugin provides specialized commands for different depths of problem-solving.

| Command | Methodology | Primary Function |
| :--- | :--- | :--- |
| `/kaizen:why` | Five Whys | Drills from surface symptoms to fundamental root causes by repeatedly asking "why" [plugins/kaizen/skills/why/SKILL.md:11-13](). |
| `/kaizen:cause-and-effect` | Fishbone (Ishikawa) | Explores problem causes across six categories: People, Process, Technology, Environment, Methods, and Materials [plugins/kaizen/skills/cause-and-effect/SKILL.md:11-13](). |
| `/kaizen:analyse-problem` | A3 Analysis | Creates a comprehensive one-page document covering Background, Current Condition, Goals, Root Cause, Countermeasures, and Implementation Plan [plugins/kaizen/skills/analyse-problem/SKILL.md:12-28](). |
| `/kaizen:root-cause-tracing` | Stack Tracing | Systematically traces bugs backward through the call stack to find the original trigger, adding instrumentation when needed [plugins/kaizen/skills/root-cause-tracing/SKILL.md:3-4](), [plugins/kaizen/skills/root-cause-tracing/SKILL.md:38-40](). |
| `/kaizen:plan-do-check-act` | PDCA Cycle | A four-phase iterative cycle for systematic experimentation and improvement: Plan, Do, Check, Act [plugins/kaizen/skills/plan-do-check-act/SKILL.md:11-14](). |

Sources: [plugins/kaizen/skills/why/SKILL.md:1-13](), [plugins/kaizen/skills/cause-and-effect/SKILL.md:1-13](), [plugins/kaizen/skills/analyse-problem/SKILL.md:12-28](), [plugins/kaizen/skills/root-cause-tracing/SKILL.md:1-4](), [plugins/kaizen/skills/plan-do-check-act/SKILL.md:11-14]()

## Smart Analysis Selection (`/kaizen:analyse`)

The `/kaizen:analyse` command acts as a router. It intelligently selects the most appropriate Kaizen technique based on the target provided by the user [plugins/kaizen/skills/analyse/SKILL.md:9-12]().

**Diagram: /kaizen:analyse Logic Flow**
```mermaid
flowchart TD
    "START"["/kaizen:analyse [target_description]"] --> "LOGIC"{"Method Selection Logic"}
    
    "LOGIC" -- "Code exploration / Gaps in docs" --> "GEMBA"["Gemba Walk<br/>(Go and see reality)"]
    "LOGIC" -- "Workflows / Pipelines / Handoffs" --> "VSM"["Value Stream Mapping<br/>(Map workflow stages)"]
    "LOGIC" -- "Inefficiencies / Tech Debt" --> "MUDA"["Muda Analysis<br/>(Waste identification)"]
    
    "GEMBA" --> "FINDINGS"["Actionable Insights & Findings"]
    "VSM" --> "FINDINGS"
    "MUDA" --> "FINDINGS"
```

**Muda (Waste) Analysis Categories**:
The plugin identifies specific waste in software development to eliminate non-value-adding activities [plugins/kaizen/skills/analyse/SKILL.md:243-245]():
1.  **Overproduction**: Extra features or code not required by current specs [plugins/kaizen/skills/analyse/SKILL.md:255-255]().
2.  **Waiting**: Delays in reviews, builds, or feedback [plugins/kaizen/skills/analyse/SKILL.md:259-259]().
3.  **Transportation**: Unnecessary data handoffs or context switching [plugins/kaizen/skills/analyse/SKILL.md:263-263]().
4.  **Over-processing**: Redundant logic, excessive refactoring, or over-engineering [plugins/kaizen/skills/analyse/SKILL.md:267-267]().
5.  **Inventory**: Partially completed work, unmerged PRs, or large backlogs [plugins/kaizen/skills/analyse/SKILL.md:271-271]().
6.  **Motion**: Unnecessary movement between tools or files [plugins/kaizen/skills/analyse/SKILL.md:275-275]().
7.  **Defects**: Bugs, rework, and technical debt [plugins/kaizen/skills/analyse/SKILL.md:279-279]().

Sources: [plugins/kaizen/skills/analyse/SKILL.md:26-45](), [plugins/kaizen/skills/analyse/SKILL.md:243-280]()

## Implementation Example: Continuous Improvement

The `kaizen` skill enforces an iterative approach to code quality. It discourages "doing everything at once" and instead promotes a three-pass iteration strategy [plugins/kaizen/skills/kaizen/SKILL.md:49-54]().

**Code Evolution Pattern (Kaizen Skill)**:
1.  **Iteration 1: Make it work** - Simplest viable version that works [plugins/kaizen/skills/kaizen/SKILL.md:58-65]().
2.  **Iteration 2: Make it clear** - Refactor for clarity and readability [plugins/kaizen/skills/kaizen/SKILL.md:67-72]().
3.  **Iteration 3: Make it robust** - Add validation, error handling, and efficiency [plugins/kaizen/skills/kaizen/SKILL.md:74-84]().

Sources: [plugins/kaizen/skills/kaizen/SKILL.md:49-88]()

## Root Cause Tracing Logic

The `/kaizen:root-cause-tracing` methodology moves beyond symptom fixing by requiring developers to trace one level up until the original trigger is identified [plugins/kaizen/skills/root-cause-tracing/SKILL.md:12-14]().

**Diagram: Root Cause Tracing Flow**
```mermaid
flowchart TD
    "SYM"["Observe Symptom"] --> "CAUSE"["Find Immediate Cause"]
    "CAUSE" --> "TRACE"["Ask: What Called This?"]
    "TRACE" --> "UP"["Keep Tracing Up Call Chain"]
    "UP" --> "TRIGGER"{"Is this the original trigger?"}
    "TRIGGER" -- "No" --> "TRACE"
    "TRIGGER" -- "Yes" --> "FIX"["Fix at Source"]
    "FIX" --> "DEFENSE"["Add Defense-in-Depth Validation"]
```

Sources: [plugins/kaizen/skills/root-cause-tracing/SKILL.md:38-80](), [plugins/kaizen/skills/root-cause-tracing/SKILL.md:150-169]()

---

