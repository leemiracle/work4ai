<!-- source: DeepWiki mcp.deepwiki.com · repo NeoLabHQ/context-engineering-kit · extra page SADD Plugin · fetched 2026-10-26 -->

# SADD Plugin

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/plugins/sadd/README.md](docs/plugins/sadd/README.md)
- [docs/plugins/sadd/do-and-judge.md](docs/plugins/sadd/do-and-judge.md)
- [docs/plugins/sadd/do-competitively.md](docs/plugins/sadd/do-competitively.md)
- [docs/plugins/sadd/do-in-parallel.md](docs/plugins/sadd/do-in-parallel.md)
- [docs/plugins/sadd/judge-with-debate.md](docs/plugins/sadd/judge-with-debate.md)
- [docs/plugins/sadd/judge.md](docs/plugins/sadd/judge.md)
- [docs/plugins/sadd/multi-agent-patterns.md](docs/plugins/sadd/multi-agent-patterns.md)
- [docs/plugins/sadd/subagent-driven-development.md](docs/plugins/sadd/subagent-driven-development.md)
- [docs/plugins/sadd/tree-of-thoughts.md](docs/plugins/sadd/tree-of-thoughts.md)
- [docs/resources/papers.md](docs/resources/papers.md)
- [plugins/customaize-agent/skills/create-rule/SKILL.md](plugins/customaize-agent/skills/create-rule/SKILL.md)
- [plugins/sadd/README.md](plugins/sadd/README.md)
- [plugins/sadd/agents/judge.md](plugins/sadd/agents/judge.md)
- [plugins/sadd/agents/meta-judge.md](plugins/sadd/agents/meta-judge.md)
- [plugins/sadd/skills/do-and-judge/SKILL.md](plugins/sadd/skills/do-and-judge/SKILL.md)
- [plugins/sadd/skills/do-competitively/SKILL.md](plugins/sadd/skills/do-competitively/SKILL.md)
- [plugins/sadd/skills/do-in-parallel/SKILL.md](plugins/sadd/skills/do-in-parallel/SKILL.md)
- [plugins/sadd/skills/do-in-steps/SKILL.md](plugins/sadd/skills/do-in-steps/SKILL.md)
- [plugins/sadd/skills/judge-with-debate/SKILL.md](plugins/sadd/skills/judge-with-debate/SKILL.md)
- [plugins/sadd/skills/judge/SKILL.md](plugins/sadd/skills/judge/SKILL.md)
- [plugins/sadd/skills/launch-sub-agent/SKILL.md](plugins/sadd/skills/launch-sub-agent/SKILL.md)
- [plugins/sadd/skills/tree-of-thoughts/SKILL.md](plugins/sadd/skills/tree-of-thoughts/SKILL.md)

</details>



The Subagent-Driven Development (SADD) Plugin is an execution framework that dispatches fresh subagents for each task with quality-controlled gates between iterations. It is designed to prevent "context pollution"—the accumulation of confusion, outdated assumptions, or implementation drift over long sessions—by ensuring each subagent starts with a clean context window [plugins/sadd/README.md:1-29]().

For other development workflow methodologies, see [TDD Plugin (3.2.1)](), [SDD Plugin (3.2.2)](), and [DDD Plugin (3.2.4)]().

## Overview

SADD implements the **Supervisor/Orchestrator pattern** [plugins/sadd/skills/do-in-steps/SKILL.md:14-14](). Instead of one agent performing all work, a main orchestrator decomposes a complex requirement into discrete tasks and dispatches specialized subagents.

**Core Capabilities:**
*   **Fresh Context per Task:** Each subagent starts clean without context pollution from previous tasks [plugins/sadd/README.md:7-7]().
*   **Quality Gates:** Integrated **LLM-as-a-Judge** and **Meta-Judge** verification catches issues before they compound [plugins/sadd/README.md:8-8]().
*   **Parallel Execution:** Independent tasks run concurrently to reduce total execution time [plugins/sadd/README.md:9-9]().
*   **Sequential Execution:** Dependent tasks execute in order with review checkpoints [plugins/sadd/README.md:10-10]().
*   **Model Selection:** Intelligent selection of models (Opus, Sonnet, Haiku) based on task complexity [plugins/sadd/skills/do-and-judge/SKILL.md:77-84]().

**Sources:** [plugins/sadd/README.md:1-31](), [plugins/sadd/skills/do-in-steps/SKILL.md:14-24]()

## Architecture & Data Flow

### The Meta-Judge -> Judge Pattern
A critical innovation in SADD v2.2 is the separation of evaluation criteria generation from the evaluation itself [plugins/sadd/README.md:46-51]().
1.  **Meta-Judge (`sadd:meta-judge`)**: Generates a tailored evaluation specification (YAML) including rubrics and checklists for a specific task [plugins/sadd/skills/do-and-judge/SKILL.md:93-115]().
2.  **Implementation Agent**: Executes the task in parallel with the Meta-Judge [plugins/sadd/skills/do-and-judge/SKILL.md:87-91]().
3.  **Judge (`sadd:judge`)**: Applies the Meta-Judge's specification to the implementation artifact to provide a verdict and score [plugins/sadd/skills/do-and-judge/SKILL.md:13-22]().

### SADD System Entity Mapping

```mermaid
graph TD
    subgraph "Natural Language Space"
        UserTask["User Requirement Prompt"]
        Verdict["Judge Verdict (Score 1-5)"]
        Rubric["Evaluation Rubric"]
    end

    subgraph "Code Entity Space (SADD Plugin)"
        Orchestrator["Orchestrator (Main Agent)"]
        MetaJudge["plugins/sadd/agents/meta-judge.md"]
        Judge["plugins/sadd/agents/judge.md"]
        Implementor["Implementation Subagent"]
        SpecYAML[".specs/reports/task-spec.yaml"]
        Scratchpad[".specs/scratchpad/hex-id.md"]
    end

    UserTask --> Orchestrator
    Orchestrator -->|"dispatch"| MetaJudge
    Orchestrator -->|"dispatch"| Implementor
    MetaJudge -->|"outputs YAML"| SpecYAML
    MetaJudge -->|"records analysis"| Scratchpad
    Implementor -->|"outputs code/docs"| Judge
    SpecYAML -->|"configures"| Judge
    Judge -->|"reads"| Scratchpad
    Judge -->|"returns SCORE/ISSUES"| Orchestrator
    Orchestrator --> Verdict
```
**Sources:** [plugins/sadd/skills/do-and-judge/SKILL.md:13-30](), [plugins/sadd/agents/meta-judge.md:8-39](), [plugins/sadd/agents/judge.md:68-80]()

## Key Orchestration Skills

### `/do-and-judge`
Executes a single task with an automatic retry loop. It dispatches a meta-judge and implementor in parallel, then uses a judge to verify the result. It allows up to 2 retries if the score is below 4 [plugins/sadd/skills/do-and-judge/SKILL.md:1-30]().

### `/do-in-parallel`
Used for batch operations across multiple files or targets.
*   **Requirement Grouping**: Analyzes tasks to identify "repeatable" (same task, different files) or "shared" (interdependent) groups to reduce the number of meta-judges required [plugins/sadd/skills/do-in-parallel/SKILL.md:14-24]().
*   **Independence Validation**: Ensures targets do not share files or state before parallelizing [plugins/sadd/skills/do-in-parallel/SKILL.md:127-135]().

### `/do-in-steps`
Orchestrates complex, sequential tasks. It decomposes a feature into steps (e.g., Interface -> Implementation -> Consumer) and applies the Judge gate to each step before proceeding [plugins/sadd/skills/do-in-steps/SKILL.md:9-24]().

### `/do-competitively`
Implements the **Generate-Critique-Synthesize (GCS)** pattern. It launches 3 independent generator agents and 1 meta-judge in parallel, evaluates all solutions using 3 judges, and then performs an evidence-based synthesis of the best elements [plugins/sadd/skills/do-competitively/SKILL.md:27-52]().

### `/tree-of-thoughts`
Systematically explores the solution space by proposing multiple approaches, pruning unpromising branches via multi-agent voting, expanding viable approaches into full solutions, and synthesizing the final result [plugins/sadd/skills/tree-of-thoughts/SKILL.md:24-65]().

### `/judge-with-debate`
Evaluates solutions through an iterative multi-judge debate. Independent judges analyze the artifact, challenge each other's assessments, and refine their evaluations until reaching consensus or maximum rounds [plugins/sadd/README.md:60-60]().

### Orchestration Workflow (Competitive)

```mermaid
sequenceDiagram
    participant O as Orchestrator
    participant MJ as sadd:meta-judge
    participant G as Generators (A,B,C)
    participant J as Judges (1,2,3)
    participant S as Synthesizer

    O->>O: Phase 1: Setup Reports Dir
    O->>MJ: Task: Generate Eval Spec
    O->>G: Task: Generate 3 Solutions (Parallel)
    MJ-->>O: Spec YAML
    G-->>O: Solutions A, B, C
    O->>J: Task: Evaluate(A,B,C + Spec)
    J-->>O: Reports 1, 2, 3
    O->>O: Phase 2.5: Adaptive Strategy Selection
    alt Split Decision
        O->>S: Task: Evidence-Based Synthesis
        S-->>O: Final Solution
    else Clear Winner
        O->>O: Select and Polish
    else All Flawed
        O->>O: Phase 1 Redesign
    end
```
**Sources:** [plugins/sadd/skills/do-competitively/SKILL.md:27-52](), [plugins/sadd/skills/do-competitively/SKILL.md:54-110]()

## Implementation Details

### Model Selection Logic
The orchestrator selects models based on task characteristics to optimize for cost and speed:
| Model | Use Case |
| :--- | :--- |
| **Opus** | Default for complex implementation, architecture, and business logic [plugins/sadd/skills/do-and-judge/SKILL.md:81-81](). |
| **Sonnet** | High volume, repetitive tasks with large context (e.g., bulk refactoring) [plugins/sadd/skills/do-and-judge/SKILL.md:82-82](). |
| **Haiku** | Trivial, mechanical operations (e.g., file moving, simple config edits) [plugins/sadd/skills/do-and-judge/SKILL.md:83-83](). |

### Quality Gate Thresholds
*   **Pass (Score 4.5-5.0)**: Exceptional quality, ready as-is [plugins/sadd/skills/judge/SKILL.md:173-173]().
*   **Good (Score 4.0-4.49)**: Solid quality, minor improvements optional [plugins/sadd/skills/judge/SKILL.md:174-174]().
*   **Acceptable (Score 3.5-3.99)**: Adequate but improvements recommended [plugins/sadd/skills/judge/SKILL.md:175-175]().
*   **Insufficient (Score <3.0)**: Requires significant rework and automatic retry [plugins/sadd/skills/judge/SKILL.md:177-177]().

### Rule Generation (Quality Feedback Loop)
When the `sadd:judge` identifies repetitive issues or gaps, it generates **contrastive rules** (Incorrect vs Correct) using the `customaize-agent:create-rule` skill [plugins/sadd/agents/judge.md:137-154](). These rules are stored in `.claude/rules/` to prevent the same mistakes in future sessions [plugins/customaize-agent/skills/create-rule/SKILL.md:10-25]().

**Sources:** [plugins/sadd/skills/do-and-judge/SKILL.md:77-85](), [plugins/sadd/skills/judge/SKILL.md:169-178](), [plugins/sadd/agents/judge.md:137-154]()

## Theoretical Foundation
The SADD plugin is built on advanced agentic research, including:
*   **LLM-as-a-Judge**: Using models to evaluate outputs [plugins/sadd/README.md:92-92]().
*   **LLM-as-a-Meta-Judge**: Evaluating the quality of the evaluation rubrics themselves [plugins/sadd/README.md:95-95]().
*   **Tree of Thoughts**: Systematic exploration of solution spaces [plugins/sadd/README.md:87-87]().
*   **Multi-Agent Debate**: Improving reasoning through iterative challenging [plugins/sadd/README.md:85-85]().
*   **Checklist-Based Evaluation (TICK/CheckEval)**: Decomposing requirements into boolean conditions for reliability [plugins/sadd/README.md:104-105]().

**Sources:** [plugins/sadd/README.md:73-106](), [docs/resources/papers.md:57-92]()

---

