<!-- source: DeepWiki mcp.deepwiki.com · repo shareAI-lab/learn-claude-code · page 7 Multi-Agent Coordination · fetched 2026-10-29 -->

# Multi-Agent Coordination

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agents/s08_background_tasks.py](agents/s08_background_tasks.py)
- [agents/s_full.py](agents/s_full.py)
- [s13_agent_teams/code.py](s13_agent_teams/code.py)
- [tests/test_s_full_background.py](tests/test_s_full_background.py)

</details>



## Purpose and Scope

This page covers the multi-agent coordination architecture in `learn-claude-code`, detailing how the execution harness scales from single-agent loops to coordinated teams of persistent agents working across isolated workspaces and shared task boards [s13_agent_teams/code.py:1-21]().

Multi-agent coordination is organized into five core pillars:
- **Evolution**: Transitioning from ephemeral subagents to persistent teammates and automated protocols [agents/s_full.py:30-34]()
- **Communication**: Append-only JSONL mailboxes, message broadcasting, and stateful protocol handshakes [agents/s_full.py:75-76]()
- **Task Claiming**: Autonomous board scanning, idle cycles, and atomic claims under file locks [s13_agent_teams/code.py:70-90]()
- **Worktree Isolation**: Git worktree binding and directory redirection for parallel execution lanes [s13_agent_teams/code.py:64-68]()
- **Shared Task Board**: Filesystem-mediated dependency graphs and status transitions [s13_agent_teams/code.py:57-61]()

For deep technical details, see the child pages linked below.

Sources: [s13_agent_teams/code.py:1-21](), [agents/s_full.py:30-34]()

---

## Architectural Overview

The coordination architecture links control planes (`.tasks/`), communication planes (`.team/inbox/`), and execution planes (`.worktrees/`) through filesystem-based primitives handled by classes like `BackgroundManager` and `Task` structures [agents/s08_background_tasks.py:56-61](), [s13_agent_teams/code.py:113-121]().

### Diagram: System Components to Code Entities

```mermaid
graph TB
    subgraph "Control Plane"
        TaskStore["Task Store<br/>"s13_agent_teams/code.py:70-90"<br/>task_store_lock()"]
        TaskStruct["Task Dataclass<br/>"s13_agent_teams/code.py:113-121"<br/>Task(id, subject, status, owner)"]
    end

    subgraph "Communication Plane"
        Mailbox["JSONL Mailboxes<br/>"s13_agent_teams/code.py:19"<br/>.mailboxes/ and .team/inbox/"]
        MsgTypes["Message Validation<br/>"agents/s_full.py:75-76"<br/>VALID_MSG_TYPES"]
    end

    subgraph "Execution Plane"
        BgMgr["Background Execution<br/>"agents/s08_background_tasks.py:56-115"<br/>BackgroundManager"]
        WorktreeReg["Worktree Registry<br/>"s13_agent_teams/code.py:64-68"<br/>teammate_assignments"]
    end

    TaskStore --> TaskStruct
    Mailbox --> MsgTypes
    BgMgr --> WorktreeReg
```

**Sources**: [agents/s08_background_tasks.py:56-115](), [agents/s_full.py:75-76](), [s13_agent_teams/code.py:64-121]()

---

## Evolution: Subagents to Teams (#7.1)

The harness evolves from single-use execution contexts to long-lived cooperative teams. Early lessons introduce ephemeral subagents via `run_subagent` [agents/s_full.py:166](), which spawn fresh message lists to handle isolated subtasks. Later stages introduce persistent teammates, atomic task assignment, and standardized communication protocols [s13_agent_teams/code.py:8-17]().

For detailed evolution traces and legacy lineages, see [Evolution: Subagents to Teams](#7.1).

Sources: [agents/s_full.py:166](), [s13_agent_teams/code.py:8-17]()

---

## Team Communication and Protocols (#7.2)

Communication between agents relies on file-based JSONL mailboxes stored in `.team/inbox/` [agents/s_full.py:66-67](). Messages are typed using `VALID_MSG_TYPES` (including `message`, `broadcast`, `shutdown_request`, `shutdown_response`, and `plan_approval_response`) to govern coordination flows like graceful shutdowns and plan gates [agents/s_full.py:75-76]().

For detailed message types, broadcast routines, inbox draining, and handshake state machines, see [Team Communication and Protocols](#7.2).

Sources: [agents/s_full.py:66-76]()

---

## Autonomous Task Claiming (#7.3)

Teammates avoid central scheduling bottlenecks by entering an idle cycle when unassigned. During idle phases, agents scan the shared task board (`.tasks/`), identify pending and unblocked items, and execute atomic claim operations protected by advisory file locks (`task_store_lock()`) [s13_agent_teams/code.py:70-90]().

For implementation details on task board scanning, idle timeouts, and self-organization, see [Autonomous Task Claiming](#7.3).

Sources: [s13_agent_teams/code.py:70-90]()

---

## Task Isolation with Worktrees (#7.4)

To prevent file overwrite collisions during concurrent development, tasks can be bound to dedicated git worktrees [s13_agent_teams/code.py:20](). The `teammate_assignments` registry maps each teammate to an execution directory (`assignment_cwd`), ensuring that all tool interactions operate safely within isolated lanes [s13_agent_teams/code.py:64-68]().

For worktree lifecycle management, collision prevention, and cleanup routines, see [Task Isolation with Worktrees](#7.4).

Sources: [s13_agent_teams/code.py:20](), [s13_agent_teams/code.py:64-68]()

---

## Shared Task Board Architecture (#7.5)

Task coordination is mediated by individual JSON files within the `.tasks/` directory [s13_agent_teams/code.py:57-58](). Each `Task` object tracks metadata such as `status`, `owner`, and `blockedBy` dependencies [s13_agent_teams/code.py:113-121](). Dependency validation prevents cycles using graph traversal helpers like `_task_depends_on` [s13_agent_teams/code.py:156-168]().

For graph schemas, status transitions, and filesystem locking mechanisms, see [Shared Task Board Architecture](#7.5).

Sources: [s13_agent_teams/code.py:57-58](), [s13_agent_teams/code.py:113-121](), [s13_agent_teams/code.py:156-168]()

---

