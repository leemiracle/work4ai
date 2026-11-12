<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/ClawTeam · page 16 Example Workflows · fetched 2026-11-09 -->

# Example Workflows

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [README.md](README.md)
- [clawteam/templates/code-review.toml](clawteam/templates/code-review.toml)
- [clawteam/templates/hedge-fund.toml](clawteam/templates/hedge-fund.toml)
- [clawteam/templates/research-paper.toml](clawteam/templates/research-paper.toml)
- [clawteam/templates/software-dev.toml](clawteam/templates/software-dev.toml)
- [clawteam/templates/strategy-room.toml](clawteam/templates/strategy-room.toml)
- [scripts/clawteam_local_install](scripts/clawteam_local_install)
- [scripts/install_clawteam.sh](scripts/install_clawteam.sh)
- [skills/clawteam/references/workflows.md](skills/clawteam/references/workflows.md)

</details>



This page demonstrates real-world ClawTeam workflows through complete, executable examples. Each workflow shows the full command sequence from team creation through agent coordination to cleanup, with expected outputs and state transitions.

For detailed breakdowns of specific team archetypes, see [Software Engineering Team](#16.1) and [AI Hedge Fund Team](#16.2). For CLI command syntax, see [CLI Command Reference](#10).

---

## Workflow Categories

ClawTeam workflows fall into three categories based on initialization approach:

| Category | Description | Example |
|----------|-------------|---------|
| **Manual Coordination** | Human directly executes commands as team leader | Basic task assignment |
| **Agent-Driven** | AI agent (e.g., Claude Code) calls `clawteam` commands | Multi-agent software development |
| **Template-Based** | Pre-configured team launched with `clawteam launch` | Hedge fund analysis team |

All workflows follow the same core pattern: team creation → task definition → agent spawning → coordination → cleanup.

**Sources:** [README.md:352-396](), [skills/clawteam/references/workflows.md:1-208]()

---

## Workflow 1: Basic Team Coordination

This workflow demonstrates fundamental ClawTeam operations: creating a team, assigning tasks with dependencies, spawning workers, and monitoring progress.

### Setup Phase

```mermaid
sequenceDiagram
    participant H as Human
    participant CLI as "clawteam CLI"
    participant TM as "TeamManager"
    participant TS as "TaskStore"
    participant FS as "FileSystem"

    H->>CLI: "team spawn-team project1 -d 'API development' -n leader"
    CLI->>TM: "create_team(name='project1', leader='leader')"
    TM->>FS: "Write ~/.clawteam/teams/project1.json"
    FS-->>CLI: "OK"
    CLI-->>H: "Team 'project1' created"

    H->>CLI: "task create project1 'Design schema' -o leader"
    CLI->>TS: "create_task(subject='Design schema', owner='leader')"
    TS->>FS: "Write ~/.clawteam/tasks/project1/task-aaa.json"
    FS-->>CLI: "Task ID: aaa"
    CLI-->>H: "Task created: aaa"

    H->>CLI: "task create project1 'Implement API' -o worker1 --blocked-by aaa"
    CLI->>TS: "create_task(blocked_by=['aaa'])"
    TS->>TS: "Set status=blocked"
    TS->>FS: "Write ~/.clawteam/tasks/project1/task-bbb.json"
    FS-->>CLI: "Task ID: bbb"
    CLI-->>H: "Task created: bbb (blocked)"
```

**Commands:**

```bash
# 1. Set leader identity
export CLAWTEAM_AGENT_ID="leader-001"
export CLAWTEAM_AGENT_NAME="leader"
export CLAWTEAM_AGENT_TYPE="leader"

# 2. Create team
clawteam team spawn-team project1 -d "API development" -n leader

# 3. Create tasks with dependency
clawteam task create project1 "Design API schema" -o leader
# Expected: Task created: aaa11111

clawteam task create project1 "Implement backend API" -o worker1 --blocked-by aaa11111
# Expected: Task created: bbb22222 (status: blocked)

# 4. Verify board state
clawteam board show project1
```

**Sources:** [skills/clawteam/references/workflows.md:3-35](), [clawteam/templates/software-dev.toml:7-33]()

### Execution Phase

```mermaid
sequenceDiagram
    participant L as "Leader"
    participant CLI as "clawteam CLI"
    participant Spawn as "AgentSpawner"
    participant Tmux as "TmuxBackend"
    participant WM as "WorkspaceManager"
    participant W as "Worker1"

    L->>CLI: "spawn --team project1 --agent-name worker1 --task 'Implement API'"
    CLI->>Spawn: "spawn(team='project1', agent_name='worker1')"
    Spawn->>WM: "create_worktree(team='project1', agent='worker1')"
    WM->>WM: "git worktree add ~/.clawteam/workspaces/project1/worker1"
    Spawn->>Tmux: "create_session(name='clawteam-project1')"
    Spawn->>Tmux: "new_window(name='worker1')"
    Tmux->>Tmux: "Set CLAWTEAM_AGENT_NAME=worker1, CLAWTEAM_TEAM_NAME=project1"
    Tmux->>W: "Launch: claude"
    
    W->>CLI: "task list project1 --owner worker1"
    CLI-->>W: "Task bbb22222: 'Implement backend API' (blocked)"
    
    Note over W: Wait for task to unblock
    
    L->>CLI: "task update project1 aaa11111 --status completed"
    CLI->>CLI: "Auto-unblock dependents (bbb22222: blocked -> pending)"
    
    W->>CLI: "task list project1 --owner worker1"
    CLI-->>W: "Task bbb22222: 'Implement backend API' (pending)"
    
    W->>CLI: "task update project1 bbb22222 --status in_progress"
    Note over W: Implement API code in isolated worktree
    W->>CLI: "task update project1 bbb22222 --status completed"
    W->>CLI: "inbox send project1 leader 'API implementation done'"
```

**Commands:**

```bash
# 5. Spawn worker agent
clawteam spawn --team project1 --agent-name worker1 \
  --task "Implement the backend API endpoints in your git worktree. Mark task as completed when done."

# 6. Leader completes design task
clawteam task update project1 aaa11111 --status completed

# 7. Verify auto-unblock
clawteam task list project1 --status pending

# 8. Monitor worker progress
clawteam board attach project1

# 9. Check for completion messages
clawteam inbox receive project1
```

**Sources:** [skills/clawteam/references/workflows.md:37-81](), [clawteam/templates/software-dev.toml:35-52]()

---

## Workflow 2: Multi-Agent Development (Parallel Work)

This workflow demonstrates parallel agent execution using a template for complex task dependencies and inter-agent messaging.

```mermaid
graph TB
    subgraph "Task Dependency Graph"
        T1["T1: Design API schema<br/>(tech-lead)<br/>pending"]
        T2["T2: Implement backend<br/>(backend-dev)<br/>blocked by T1"]
        T3["T3: Implement UI<br/>(frontend-dev)<br/>blocked by T1"]
        T4["T4: Write tests<br/>(qa-engineer)<br/>blocked by T2,T3"]
    end
    
    T1 -->|completes| T2
    T1 -->|completes| T3
    T2 -->|completes| T4
    T3 -->|completes| T4
    
    subgraph "Agent Worktrees"
        WT1["~/.clawteam/workspaces/webapp/backend-dev"]
        WT2["~/.clawteam/workspaces/webapp/frontend-dev"]
        WT3["~/.clawteam/workspaces/webapp/qa-engineer"]
    end
    
    T2 -.-> WT1
    T3 -.-> WT2
    T4 -.-> WT3
```

**Template-Based Launch:**

```bash
# Launch a full team from the software-dev template
clawteam launch software-dev --team webapp --goal "Build a RESTful todo app with React"

# Monitor in real-time
clawteam board live webapp --interval 5
```

**Sources:** [clawteam/templates/software-dev.toml:1-129](), [README.md:271-302]()

---

## Workflow 3: AI Hedge Fund (Consolidation Pattern)

This workflow demonstrates the "Specialist Synthesis" pattern, where multiple agents report to a manager who waits for all inputs before acting.

```mermaid
sequenceDiagram
    participant PM as "portfolio-manager"
    participant A1 as "buffett-analyst"
    participant A2 as "technical-analyst"
    participant RM as "risk-manager"
    participant Inbox as "MailboxManager"

    PM->>Inbox: "task create (to analysts)"
    PM->>Inbox: "inbox send 'Analyze AAPL'"
    
    A1->>Inbox: "inbox receive"
    A2->>Inbox: "inbox receive"
    
    Note over A1,A2: Parallel Analysis
    
    A1->>Inbox: "inbox send risk-manager 'SIGNAL: bullish'"
    A2->>Inbox: "inbox send risk-manager 'SIGNAL: bearish'"
    
    RM->>Inbox: "inbox receive (Wait for all 5 analysts)"
    RM->>Inbox: "inbox send portfolio-manager 'RISK REPORT'"
    
    PM->>PM: "Final Decision"
```

**Template Logic:**
The `portfolio-manager` and `risk-manager` use a polling loop to wait for specialist completion:
```bash
# Logic inside template
sleep 45 && clawteam board show {team_name}
# Repeat until ALL analyst tasks show "completed"
```

**Sources:** [clawteam/templates/hedge-fund.toml:1-164](), [clawteam/templates/strategy-room.toml:14-32]()

---

## Workflow 4: Strategy Room (Decision Pattern)

This workflow focuses on cross-functional tradeoff analysis using the `strategy-room` template.

| Agent | Role | Focus |
|-------|------|-------|
| `strategy-lead` | Coordinator | Frames problem, creates tasks, finalizes recommendation |
| `systems-analyst` | Architect | Evaluates boundaries, tradeoffs, and operational complexity |
| `delivery-planner`| Project Manager | Breaks down milestones and sequencing |
| `risk-mapper` | Security/Risk | Identifies failure modes and hidden assumptions |
| `decision-editor` | Synthesizer | Consolidates specialist outputs into a strategy memo |

**Sources:** [clawteam/templates/strategy-room.toml:1-128]()

---

## Summary of Patterns

ClawTeam workflows leverage these core patterns:

1.  **Chain Dependency:** Task A blocks Task B (e.g., Design blocks Code).
2.  **Fan-Out/Fan-In:** One leader spawns multiple specialists who report back to a single synthesizer.
3.  **Polling Wait:** Leaders use `sleep` and `board show` or `task wait` to coordinate without blocking the CLI process indefinitely.
4.  **Isolated Workspaces:** Each agent operates in a unique `git worktree` to prevent merge conflicts during development.

**Sources:** [skills/clawteam/references/workflows.md:164-208](), [clawteam/templates/code-review.toml:1-105]()

---

