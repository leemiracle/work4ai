<!-- source: DeepWiki mcp.deepwiki.com · repo kayba-ai/agentic-context-engine · page 3 Architecture · fetched 2026-10-27 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CLAUDE.md](CLAUDE.md)
- [README.md](README.md)
- [ace/__init__.py](ace/__init__.py)
- [ace/runners/litellm.py](ace/runners/litellm.py)
- [assets/kayba-banner.png](assets/kayba-banner.png)
- [docs/design/ACE_ARCHITECTURE.md](docs/design/ACE_ARCHITECTURE.md)
- [docs/design/ACE_DECISIONS.md](docs/design/ACE_DECISIONS.md)
- [docs/design/ACE_REFERENCE.md](docs/design/ACE_REFERENCE.md)
- [docs/design/RR_DESIGN.md](docs/design/RR_DESIGN.md)
- [examples/ace/ace_demo.py](examples/ace/ace_demo.py)
- [tests/test_pipeline_exports.py](tests/test_pipeline_exports.py)

</details>



## Purpose and Scope

This page provides a technical overview of the ACE Framework's architecture, covering the core implementation in `ace/`, the generic pipeline engine, and the key subsystems that enable self-improving AI agents.

For detailed information about specific subsystems:
- **Core Library (ace/)**: [Core Library (ace/)](#3.1) — Roles, adapters, and async learning orchestration.
- **Pipeline Engine (pipeline/)**: [Pipeline Engine (pipeline/)](#3.2) — The foundation of `StepProtocol`, `Pipeline`, and `Branch` primitives.
- **Recursive Reflector System**: [Recursive Reflector System](#3.3) — Iterative code-based trace analysis in sandboxed REPL environments.
- **RecursiveAgent Abstraction**: [RecursiveAgent Abstraction](#3.4) — The base class for budget management and depth-based recursion.
- **Prompt Engineering System**: [Prompt Engineering System](#3.5) — Versioning, atomicity, and domain-specific variants.
- **Deduplication System**: [Deduplication System](#3.6) — Hybrid retrieval and skill consolidation strategies.

## High-Level Component Map

The ACE architecture is built on a "Roles and Steps" pattern. Roles implement the business logic (LLM interactions), while Steps adapt that logic into the pipeline engine's context-based data flow.

```mermaid
graph TB
    subgraph "pipeline/ (Generic Engine)"
        StepProtocol["StepProtocol<br/>(pipeline/protocol.py)"]
        Pipeline["Pipeline<br/>(pipeline/pipeline.py)"]
        Branch["Branch<br/>(pipeline/branch.py)"]
        StepContext["StepContext<br/>(pipeline/context.py)"]
    end
    
    subgraph "ace/core"
        ACEStepContext["ACEStepContext<br/>(ace/core/context.py)"]
        SkillbookView["SkillbookView<br/>(ace/core/context.py)"]
        Skillbook["Skillbook<br/>(ace/core/skillbook.py)"]
    end
    
    subgraph "ace/steps"
        AgentStep["AgentStep"]
        EvaluateStep["EvaluateStep"]
        ReflectStep["ReflectStep"]
        UpdateStep["UpdateStep"]
        learning_tail["learning_tail()<br/>(ace/steps/__init__.py)"]
    end
    
    subgraph "ace/runners"
        ACERunner["ACERunner<br/>(ace/runners/base.py)"]
        ACE["ACE<br/>(ace/runners/ace.py)"]
        TraceAnalyser["TraceAnalyser<br/>(ace/runners/trace_analyser.py)"]
    end
    
    subgraph "ace/implementations"
        Agent_Impl["Agent<br/>(ace/implementations/agent.py)"]
        Reflector_Impl["Reflector<br/>(ace/implementations/reflector.py)"]
        SkillManager_Impl["SkillManager<br/>(ace/implementations/skill_manager.py)"]
    end
    
    subgraph "ace/rr"
        RRStep["RRStep<br/>(ace/steps/rr_step.py)"]
        TraceSandbox["TraceSandbox<br/>(ace/steps/rr_step.py)"]
    end
    
    StepContext --> ACEStepContext
    ACEStepContext --> SkillbookView
    StepProtocol --> AgentStep
    StepProtocol --> ReflectStep
    StepProtocol --> UpdateStep
    Pipeline --> ACERunner
    ACERunner --> ACE
    ACERunner --> TraceAnalyser
    AgentStep --> Agent_Impl
    ReflectStep --> Reflector_Impl
    ReflectStep --> RRStep
    UpdateStep --> SkillManager_Impl
    learning_tail --> ReflectStep
    learning_tail --> UpdateStep
    RRStep --> TraceSandbox
```

**Key characteristics:**
- **Composable steps:** Each step does one focused task, validated by `requires`/`provides` contracts [CLAUDE.md:11-13]().
- **Configurable boundaries:** `async_boundary` declared on steps enables background learning [docs/ACE_ARCHITECTURE.md:71-72]().
- **Protocol-based roles:** Steps depend on `AgentLike`, `ReflectorLike` protocols, not concrete classes [docs/ACE_ARCHITECTURE.md:54-56]().
- **Pluggable reflectors:** `Reflector` or `RRStep` (Recursive Reflector) are drop-in replacements [docs/RR_DESIGN.md:108-120]().

**Sources:** [docs/ACE_ARCHITECTURE.md:43-58](), [docs/PIPELINE_DESIGN.md:1-114](), [ace/__init__.py:62-121]().

## Pipeline Engine Foundation

The `pipeline/` module provides a generic execution engine that ACE is built on. It manages typed step contracts, concurrent execution, and structured error handling [docs/ACE_ARCHITECTURE.md:15-16]().

### Core Primitives

| Primitive | Description | Implementation |
|-----------|-------------|----------------|
| **Step** | Smallest unit of work; receives context, returns context | `StepProtocol` [ace/__init__.py:67]() |
| **Pipeline** | Sequential step list; runs one input through N steps | `Pipeline` [ace/__init__.py:64]() |
| **Branch** | Parallel fork-join; runs N sub-pipelines on same input | `Branch` [ace/__init__.py:65]() |

**Composability:** All primitives satisfy `StepProtocol`, so they nest arbitrarily. A `Pipeline` can contain `Branch` steps, and a `SubRunner` (like the one powering `RRStep`) can be placed in any pipeline as a black-box step [docs/RR_DESIGN.md:13-14]().

**Sources:** [docs/PIPELINE_DESIGN.md:6-263](), [ace/__init__.py:62-68]().

### Context and Immutability

ACE uses an immutable context pattern to ensure thread safety and explicit data flow [docs/ACE_ARCHITECTURE.md:93-95]().

```mermaid
graph LR
    StepContext_Base["StepContext<br/>(pipeline/context.py)<br/>frozen=True"]
    ACEStepContext_Sub["ACEStepContext<br/>(ace/core/context.py)<br/>frozen=True<br/>sample: ACESample<br/>skillbook: SkillbookView<br/>agent_output: AgentOutput | None<br/>reflections: tuple[ReflectorOutput, ...]"]
    
    StepContext_Base --> ACEStepContext_Sub
    ACEStepContext_Sub -.immutable updates via.-> replace["ctx.replace(field=value)"]
```

**SkillbookView:** To prevent accidental mutation of the `Skillbook` during concurrent execution, the context carries a `SkillbookView`—a read-only projection. Steps that need to write to the skillbook receive the real `Skillbook` via constructor injection [docs/ACE_ARCHITECTURE.md:80-91]().

**Sources:** [docs/ACE_ARCHITECTURE.md:93-128](), [docs/ACE_REFERENCE.md:112-134](), [ace/core/context.py:1-164]().

## Core Abstractions

### Protocols vs Implementations

The architecture separates interface contracts from business logic. Roles are backed by **PydanticAI** agents for structured LLM interactions [docs/ACE_ARCHITECTURE.md:16-17]().

```mermaid
graph TB
    subgraph "Protocols (ace/protocols/)"
        AgentLike["AgentLike<br/>generate(...)"]
        ReflectorLike["ReflectorLike<br/>reflect(...)"]
        SkillManagerLike["SkillManagerLike<br/>update_skills(...)"]
    end
    
    subgraph "Implementations (ace/implementations/)"
        Agent_Concrete["Agent<br/>(ace/implementations/agent.py)"]
        Reflector_Concrete["Reflector<br/>(ace/implementations/reflector.py)"]
        RRStep_Concrete["RRStep<br/>(ace/steps/rr_step.py)"]
        SkillManager_Concrete["SkillManager<br/>(ace/implementations/skill_manager.py)"]
    end
    
    AgentLike -.satisfied by.-> Agent_Concrete
    ReflectorLike -.satisfied by.-> Reflector_Concrete
    ReflectorLike -.satisfied by.-> RRStep_Concrete
    SkillManagerLike -.satisfied by.-> SkillManager_Concrete
```

**Sources:** [docs/ACE_ARCHITECTURE.md:43-58](), [docs/ACE_REFERENCE.md:143-159](), [ace/protocols/]()

## Data Flow Patterns

### ACE Pipeline (Full Execution)

The `ACE` runner orchestrates the full closed-loop pipeline: **Agent → Evaluate → Reflect → Update → Apply** [examples/ace/ace_demo.py:121-124]().

```mermaid
graph LR
    Sample["Sample"]
    AgentStep["AgentStep<br/>(ace/steps/agent_step.py)"]
    EvaluateStep["EvaluateStep<br/>(ace/steps/evaluate_step.py)"]
    ReflectStep["ReflectStep<br/>(ace/steps/reflect_step.py)"]
    UpdateStep["UpdateStep<br/>(ace/steps/update_step.py)"]
    
    Sample --> AgentStep
    AgentStep --> EvaluateStep
    EvaluateStep -.async_boundary.-> ReflectStep
    ReflectStep --> UpdateStep
```

**Async Boundary:** The `ReflectStep` typically marks an `async_boundary`, allowing the foreground execution to return results to the user while learning happens in the background [docs/ACE_REFERENCE.md:225-230]().

**Sources:** [docs/ACE_ARCHITECTURE.md:105-111](), [docs/ACE_REFERENCE.md:165-240](), [ace/runners/ace.py]().

## Runner Architecture

Runners are the primary entry points for the framework. They compose steps into pipelines and manage the iteration over input samples [docs/ACE_ARCHITECTURE.md:54-55]().

| Runner | Purpose | Key Method |
|--------|---------|------------|
| `ACE` | Live execution + feedback loop | `run(samples, epochs)` [ace/runners/ace.py]() |
| `TraceAnalyser` | Learn from pre-recorded traces | `run(traces, epochs)` [ace/runners/trace_analyser.py]() |
| `ACELiteLLM` | Simple conversational interface | `ask(question)`, `learn()` [ace/runners/litellm.py:50-54]() |

**Sources:** [docs/ACE_ARCHITECTURE.md:32-40](), [ace/runners/]()

## Summary

The ACE Framework architecture leverages a generic pipeline engine to compose PydanticAI-backed roles into adaptive learning loops. By enforcing immutability and protocol-based decoupling, the system achieves high concurrency and pluggable intelligence (e.g., swapping a standard `Reflector` for a `Recursive Reflector`).

For deeper technical details, proceed to the specific architecture child pages.

**Sources:** [README.md:78-100](), [docs/ACE_ARCHITECTURE.md:1-30](), [CLAUDE.md:45-57]().

---

