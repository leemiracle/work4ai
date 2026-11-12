<!-- source: DeepWiki mcp.deepwiki.com · repo affaan-m/ECC · page 11 Orchestration & Multi-Agent Workflows · fetched 2026-10-30 -->

# Orchestration & Multi-Agent Workflows

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/crosspost/SKILL.md](.agents/skills/crosspost/SKILL.md)
- [.agents/skills/exa-search/SKILL.md](.agents/skills/exa-search/SKILL.md)
- [.agents/skills/plan-canvas/SKILL.md](.agents/skills/plan-canvas/SKILL.md)
- [.agents/skills/x-api/SKILL.md](.agents/skills/x-api/SKILL.md)
- [scripts/control-pane.js](scripts/control-pane.js)
- [scripts/lib/control-pane/server.js](scripts/lib/control-pane/server.js)
- [scripts/lib/control-pane/state.js](scripts/lib/control-pane/state.js)
- [scripts/lib/control-pane/ui.js](scripts/lib/control-pane/ui.js)
- [scripts/lib/control-pane/work-item-mutations.js](scripts/lib/control-pane/work-item-mutations.js)
- [scripts/lib/orchestration-session.js](scripts/lib/orchestration-session.js)
- [scripts/lib/plan-canvas/server.js](scripts/lib/plan-canvas/server.js)
- [scripts/lib/plan-canvas/ui.js](scripts/lib/plan-canvas/ui.js)
- [scripts/lib/platform-launch.js](scripts/lib/platform-launch.js)
- [scripts/lib/tmux-worktree-orchestrator.js](scripts/lib/tmux-worktree-orchestrator.js)
- [scripts/orchestrate-worktrees.js](scripts/orchestrate-worktrees.js)
- [scripts/orchestration-status.js](scripts/orchestration-status.js)
- [scripts/plan-canvas.js](scripts/plan-canvas.js)
- [scripts/work-items.js](scripts/work-items.js)
- [skills/crosspost/SKILL.md](skills/crosspost/SKILL.md)
- [skills/dmux-workflows/SKILL.md](skills/dmux-workflows/SKILL.md)
- [skills/exa-search/SKILL.md](skills/exa-search/SKILL.md)
- [skills/fal-ai-media/SKILL.md](skills/fal-ai-media/SKILL.md)
- [skills/plan-canvas/SKILL.md](skills/plan-canvas/SKILL.md)
- [skills/x-api/SKILL.md](skills/x-api/SKILL.md)
- [tests/lib/control-pane-state.test.js](tests/lib/control-pane-state.test.js)
- [tests/lib/control-pane-ui.test.js](tests/lib/control-pane-ui.test.js)
- [tests/lib/orchestration-session.test.js](tests/lib/orchestration-session.test.js)
- [tests/lib/platform-launch.test.js](tests/lib/platform-launch.test.js)
- [tests/lib/tmux-worktree-orchestrator.test.js](tests/lib/tmux-worktree-orchestrator.test.js)
- [tests/scripts/control-pane.test.js](tests/scripts/control-pane.test.js)
- [tests/scripts/plan-canvas.test.js](tests/scripts/plan-canvas.test.js)
- [tests/scripts/work-items.test.js](tests/scripts/work-items.test.js)

</details>



Everything Claude Code (ECC) provides a sophisticated orchestration layer designed to coordinate multiple autonomous agents working across different branches and tasks simultaneously. This system manages the lifecycle of agent sessions, ensures isolation through git worktrees, and provides visual tools for operators to monitor and intervene in complex multi-agent plans.

The orchestration logic is split between a high-performance Rust control plane (`ecc2`) for daemonized management and a suite of JavaScript/Shell scripts for environment setup, work item tracking, and tool-level integration.

For full technical details, see the child pages:
- [Tmux & Worktree Orchestration](#11.1)
- [Hermes Operator Shell](#11.2)
- [GitHub Coordination & Autonomous Loops](#11.3)

---

## Multi-Agent Architecture

ECC adopts a lead-delegate model in which a primary session (lead) can spawn multiple child sessions (delegates) for workload distribution and specialized task execution. This model ensures parallelism while preserving isolation and consistency.

Key orchestration components are primarily implemented in the `ecc2` Rust subsystem, leveraging a SQLite-backed persistent state store to maintain session metadata, worktree associations, and inter-agent communications.

### Core Orchestration Entities

| Entity              | Code Reference                       | Responsibility                                                            |
|---------------------|------------------------------------|---------------------------------------------------------------------------|
| **State Store**     | `StateStore`                       | SQLite-backed persistence for sessions, worktrees, and handoffs.         |
| **Session Manager** | `ecc2/src/session/manager.rs`     | Handles session creation, delegation, and status tracking.                |
| **Daemon**          | `ecc2/src/session/daemon.rs`      | Background monitoring, auto-dispatching, and resource cleanup.            |
| **Worktree Controller** | `ecc2/src/worktree/mod.rs`      | Git worktree lifecycle management: creation, synchronization, pruning.   |

### Code Entity Mapping for Multi-Agent Orchestration

```mermaid
graph TD
    A["Spawn a delegate session"] --> A1["manager::create_session_from_source_with_profile_and_grouping"]
    B["Auto-dispatch tasks"] --> B1["daemon::maybe_auto_dispatch"]
    B1 --> B2["manager::auto_dispatch_backlog"]
    C["Check worktree health & merge readiness"] --> C1["worktree::WorktreeHealth"]
    C1 --> C2["worktree::MergeReadiness"]

    click A1 "ecc2/src/session/manager.rs:90-114" ""
    click B1 "ecc2/src/session/daemon.rs:127-143" ""
    click B2 "ecc2/src/session/manager.rs:210-250" ""
    click C1 "ecc2/src/worktree/mod.rs:12-31" ""
    click C2 "ecc2/src/worktree/mod.rs:32-78" ""
```

Sources: [ecc2/src/session/manager.rs:90-114](), [ecc2/src/session/manager.rs:210-250](), [ecc2/src/session/daemon.rs:127-143](), [ecc2/src/worktree/mod.rs:12-78]()

---

## Tmux & Worktree Orchestration

To prevent conflicts between concurrent agents, ECC orchestrates isolated work environments using **Git Worktrees**. Each agent session runs in a dedicated worktree on a unique git branch, ensuring that changes do not collide or overwrite each other.

The orchestration logic includes:
- **Worktree Lifecycle:** `worktree::create_for_session` creates and manages isolated worktrees for agent sessions [ecc2/src/worktree/mod.rs:96-149]().
- **Seed Paths Overlay:** Specific files or directories can be overlayed into worktrees ("seed paths") to provide necessary dependencies or configuration [scripts/lib/tmux-worktree-orchestrator.js:86-105]().
- **Tmux Session Integration:** The `tmux-worktree-orchestrator.js` script generates orchestrated `tmux` commands to launch and monitor multiple agent shells in parallel [scripts/lib/tmux-worktree-orchestrator.js:175-187]().

For a detailed technical deep dive into tmux session orchestration, worktree lifecycle, Plan Canvas, and collision avoidance strategies, see [Tmux & Worktree Orchestration](#11.1).

Sources: [ecc2/src/worktree/mod.rs:96-149](), [scripts/lib/tmux-worktree-orchestrator.js:86-105]()

---

## ecc2 Control Plane and Control Pane UI

The `ecc2` binary is the core control plane providing daemonized session and resource management. The web-based Control Pane server is implemented via the `scripts/control-pane.js` CLI and `scripts/lib/control-pane/server.js` modules, with UI markup rendered by `scripts/lib/control-pane/ui.js` [scripts/control-pane.js:21-51](), [scripts/lib/control-pane/server.js:162-194](), [scripts/lib/control-pane/ui.js:3-126]().

- **Auto-Dispatch Policy:** Background daemon monitors lead session inboxes for unread task handoffs [ecc2/src/main.rs:195-217]().
- **Operator Web UI & Actions:** Exposes endpoints to inspect states and trigger authorized management commands [scripts/lib/control-pane/server.js:166-194]().

Sources: [ecc2/src/main.rs:195-217](), [scripts/control-pane.js:21-51](), [scripts/lib/control-pane/server.js:162-194](), [scripts/lib/control-pane/ui.js:3-126]()

---

## Visual Review, Work Items & Collision Avoidance

Managing multi-agent workflows requires robust safety, review, and tracking tooling:

- **Plan Canvas:** Interactive browser-based review canvas for multi-step agent plans, managed via `scripts/plan-canvas.js` [scripts/plan-canvas.js:1-74]() and `scripts/lib/plan-canvas/server.js:1-38]().
- **Work Items & State Store:** Tracks Linear, GitHub, and handoff items in SQLite via `scripts/work-items.js` and `scripts/lib/state-store.js` [scripts/work-items.js:31-60]().
- **Agent-Proximity Collision Avoidance:** Measures spatial overlaps of agents editing the same code regions to prevent destructive merge conflicts [scripts/lib/agent-proximity/index.js]().

Sources: [scripts/plan-canvas.js:1-74](), [scripts/lib/plan-canvas/server.js:1-38](), [scripts/work-items.js:31-60]()

---

## GitHub Coordination & Autonomous Loops

ECC supports autonomous background execution loops (`/loop-start`, `/loop-status`) and GitHub integration libraries (`github-coordination`) to synchronize work items, issue states, and pull requests directly into the local SQLite state store.

For full technical documentation on autonomous loops, branch management, and GitHub coordination actions, see [GitHub Coordination & Autonomous Loops](#11.3).

Sources: [scripts/work-items.js:145-204]()

---

## Hermes Operator Shell

The **Hermes Operator Shell** sits above ECC as the primary natural language interface shell for operators, adhering to the Hermes boundary sanitization standard and supporting imported ECC skills.

For full technical exposition on Hermes architecture, boundary protocols, and skill integrations, see [Hermes Operator Shell](#11.2).

Sources: [skills/dmux-workflows/SKILL.md](), [ecc2/src/main.rs:60-64]()

---

## See Also

- [Tmux & Worktree Orchestration](#11.1) — Detailed lifecycle, tmux integration, codex worker, agent-proximity, Control Pane internals.
- [Hermes Operator Shell](#11.2) — High-level shell interface, boundary sanitization, skill importing, Hermes setup and migration.
- [GitHub Coordination & Autonomous Loops](#11.3) — Autonomous loops, GitHub API integration, work items synchronization.

---

