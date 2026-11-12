<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/DeepCode · page 7 Goals, Automations, and Scheduling · fetched 2026-11-09 -->

# Goals, Automations, and Scheduling

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/agent_runtime/tools/__init__.py](core/agent_runtime/tools/__init__.py)
- [core/application/goal_extension.py](core/application/goal_extension.py)
- [core/schedule/__init__.py](core/schedule/__init__.py)
- [core/schedule/keepalive.py](core/schedule/keepalive.py)
- [core/schedule/scheduler.py](core/schedule/scheduler.py)
- [core/sessions/thread_goal_store.py](core/sessions/thread_goal_store.py)
- [tests/test_schedule.py](tests/test_schedule.py)

</details>



This page provides an overview of durable objectives and scheduled work in DeepCode, including Goals, the verify loop, Automations, the scheduler, and keepalive/monitor policies. 

This is a **PARENT** page. For deep technical details, refer to the child pages:
- [Goals and the Verify Loop](#7.1)
- [Automations and Scheduler](#7.2)

Sources: [core/schedule/__init__.py:1-18](), [core/application/goal_extension.py:1-105]()

## Goals and the Verify Loop

A **Goal** (`ThreadGoal`) represents a durable objective attached to a `Thread` that persists across turns and session restarts [core/domain/thread_goal.py:1-30](). Unlike a single prompt, a Goal tracks an objective status (`ACTIVE`, `COMPLETED`, `FAILED`) and uses runtime persistence via `ThreadGoalStore` [core/sessions/thread_goal_store.py:58-72]() and `GoalExtension` [core/application/goal_extension.py:84-108]().

The **Verify Loop** acts as a mechanical referee. When configured with a completion evidence command, the system executes validation checks after agent turns until the goal condition is satisfied or execution constraints are met.

### Goal Lifecycle and Code Entities
The following diagram bridges the natural language concept of a goal to its corresponding code entities.

```mermaid
graph TD
    subgraph "Natural Language Space"
        UserObjective[""Fix all lint errors in core/""]
        Verification[""Run ruff check""]
    end

    subgraph "Code Entity Space"
        TG[""ThreadGoal (core/domain/thread_goal.py)""]
        Store[""ThreadGoalStore (core/sessions/thread_goal_store.py)""]
        GE[""GoalExtension (core/application/goal_extension.py)""]
        
        UserObjective -->|objective| TG
        Verification -->|completion_evidence_command| TG
        TG -->|persisted by| Store
        TG -->|managed by| GE
    end
```
Sources: [core/domain/thread_goal.py:1-30](), [core/sessions/thread_goal_store.py:58-72](), [core/application/goal_extension.py:84-108]()

For details, see [Goals and the Verify Loop](#7.1).

## Automations and the Scheduler

Automations handle recurring or triggered agent tasks. The scheduling architecture relies on two core components defined in `core/schedule/`:
- **Continuation Gate**: Defined in `core/schedule/keepalive.py`, this pure function decides whether a long-horizon job should run again based on clean exits, goal achievement, and run caps (`max_runs`) [core/schedule/keepalive.py:23-37]().
- **Scheduler**: Defined in `core/schedule/scheduler.py`, `run_scheduled` executes tasks repeatedly at fixed intervals, consulting the keepalive gate between iterations [core/schedule/scheduler.py:33-66]().

### Scheduler and Keepalive Flow
The following diagram illustrates how the scheduler interacts with the continuation gate.

```mermaid
graph TD
    subgraph "Natural Language Space"
        TaskRequest[""Run scheduled background task""]
    end

    subgraph "Code Entity Space"
        Sched[""run_scheduled (core/schedule/scheduler.py)""]
        Gate[""Continuation (core/schedule/keepalive.py)""]
        Decision[""ContinuationDecision (core/schedule/keepalive.py)""]
        
        TaskRequest -->|invokes| Sched
        Sched -->|evaluates run state| Gate
        Gate -->|returns| Decision
        Decision -->|go=True| Sched
        Decision -->|go=False| Terminate[""Stop execution loop""]
    end
```
Sources: [core/schedule/keepalive.py:16-37](), [core/schedule/scheduler.py:33-66](), [tests/test_schedule.py:20-41]()

For details, see [Automations and Scheduler](#7.2).

## Autodream and Memory Consolidation

**Autodream** is a background automation pass designed to maintain and consolidate agent memory files stored under workspace directories. It aggregates notes, removes duplicates, and updates `MEMORY.md` without blocking interactive user sessions.

Sources: [core/sessions/thread_goal_store.py:65-73]()

## Related Systems

- **Thread Goal Store**: Manages append-only goal transitions and turn settlements [core/sessions/thread_goal_store.py:65-191]().
- **Goal Extension**: Bridges goal lifecycles with standard turn execution and policies [core/application/goal_extension.py:84-114]().

Sources: [core/sessions/thread_goal_store.py:65-191](), [core/application/goal_extension.py:84-114]()

---

