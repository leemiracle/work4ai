<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/ClawTeam · page 9 Agent Lifecycle · fetched 2026-11-09 -->

# Agent Lifecycle

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [clawteam/spawn/__init__.py](clawteam/spawn/__init__.py)
- [clawteam/spawn/keepalive.py](clawteam/spawn/keepalive.py)
- [clawteam/spawn/prompt.py](clawteam/spawn/prompt.py)
- [clawteam/spawn/registry.py](clawteam/spawn/registry.py)
- [clawteam/spawn/wsh_rpc.py](clawteam/spawn/wsh_rpc.py)
- [clawteam/team/lifecycle.py](clawteam/team/lifecycle.py)
- [tests/test_costs.py](tests/test_costs.py)
- [tests/test_lifecycle.py](tests/test_lifecycle.py)
- [tests/test_prompt.py](tests/test_prompt.py)
- [tests/test_registry.py](tests/test_registry.py)
- [tests/test_wsh_backend.py](tests/test_wsh_backend.py)

</details>



This page documents the lifecycle management system for ClawTeam agents, covering the states an agent transitions through from spawning to shutdown, the coordinated shutdown protocol, idle notifications, and automatic cleanup on unexpected exit.

For information about spawning new agents and backend options, see [Spawning Agents](3.2). For task state transitions and coordination, see [Task Management](4).

---

## Lifecycle Overview

Agents in ClawTeam follow a managed lifecycle with explicit coordination points. The lifecycle system ensures graceful shutdown, prevents abandoned work, and maintains system consistency when agents exit.

### Agent Lifecycle States

```mermaid
stateDiagram-v2
    [*] --> Spawning: "clawteam spawn"
    Spawning --> Running: "Process started<br/>Identity env vars set"
    
    Running --> Idle: "lifecycle idle<br/>(no more tasks)"
    Idle --> Running: "New task assigned"
    
    Running --> ShutdownRequested: "lifecycle request-shutdown<br/>(from leader)"
    ShutdownRequested --> Running: "lifecycle reject-shutdown"
    ShutdownRequested --> ShuttingDown: "lifecycle approve-shutdown"
    
    ShuttingDown --> Exited: "Agent process exits"
    Running --> Exited: "Unexpected exit"
    Idle --> Exited: "Unexpected exit"
    
    Exited --> Cleanup: "lifecycle on-exit<br/>(automatic)"
    Cleanup --> [*]
    
    note right of Running
        Agent executes tasks
        Polls inbox for messages
        Reports cost/progress
    end note
    
    note right of ShutdownRequested
        Agent has pending
        shutdown_request message
        in inbox
    end note
    
    note right of Cleanup
        - Reset in_progress tasks to pending
        - Notify leader of abandonment
        - Clean up resources
    end note
```

**Sources:**
- [clawteam/spawn/prompt.py:84-107]()
- [clawteam/team/lifecycle.py:12-89]()

---

## Coordinated Shutdown Protocol

The shutdown protocol follows a request-approve pattern to ensure agents complete their current work gracefully before exiting.

### Shutdown Message Flow

```mermaid
sequenceDiagram
    participant Leader as "Leader Agent"
    participant MailboxMgr as "MailboxManager"
    participant LifecycleMgr as "LifecycleManager"
    participant WorkerInbox as "Worker Inbox<br/>(filesystem)"
    participant Worker as "Worker Agent"
    
    Note over Leader,Worker: Request Phase
    
    Leader->>LifecycleMgr: request_shutdown(from_agent, to_agent, reason)
    LifecycleMgr->>MailboxMgr: send(msg_type=shutdown_request)
    MailboxMgr->>WorkerInbox: Write msg-{timestamp}-{uuid}.json
    MailboxMgr-->>LifecycleMgr: request_id
    LifecycleMgr-->>Leader: request_id
    
    Note over Worker: Worker polls inbox periodically
    
    Worker->>MailboxMgr: receive(worker_name)
    MailboxMgr->>WorkerInbox: Read messages
    WorkerInbox-->>MailboxMgr: shutdown_request message
    MailboxMgr-->>Worker: [{type: shutdown_request, requestId: ...}]
    
    Note over Worker: Worker decides: approve or reject
    
    alt Worker Approves
        Worker->>LifecycleMgr: approve_shutdown(agent_name, request_id)
        LifecycleMgr->>MailboxMgr: send(msg_type=shutdown_approved)
        MailboxMgr->>WorkerInbox: Write response message
        Note over Worker: Worker exits (exit code 0)
    else Worker Rejects
        Worker->>LifecycleMgr: reject_shutdown(agent_name, request_id, reason)
        LifecycleMgr->>MailboxMgr: send(msg_type=shutdown_rejected)
        Note over Worker: Worker continues working
    end
    
    Leader->>MailboxMgr: receive(leader_name)
    MailboxMgr-->>Leader: shutdown_approved or shutdown_rejected
```

**Sources:**
- [clawteam/team/lifecycle.py:19-63]()
- [clawteam/team/models.py:9-10]() (MessageType enum)

### Shutdown Commands

| Command | Description | Parameters | Effect |
|---------|-------------|------------|--------|
| `lifecycle request-shutdown` | Leader requests agent shutdown | `<team> <from-agent> <to-agent> [--reason]` | Sends `shutdown_request` message to target agent's inbox |
| `lifecycle approve-shutdown` | Agent approves shutdown | `<team> <request-id> <agent>` | Sends `shutdown_approved` to requester, agent should exit |
| `lifecycle reject-shutdown` | Agent rejects shutdown | `<team> <request-id> <agent> [--reason]` | Sends `shutdown_rejected` to requester, agent continues |

**Sources:**
- [clawteam/team/lifecycle.py:19-63]()

---

## Idle Notifications

Workers send `idle` messages to the leader when they have no more tasks to execute, enabling the leader to assign new work or initiate shutdown.

### Idle Notification Flow

```mermaid
graph TB
    Worker["Worker Agent<br/>(running state)"]
    TaskList["clawteam task list --owner worker"]
    CheckTasks{"Has pending<br/>tasks?"}
    SendIdle["clawteam lifecycle idle"]
    LifecycleMgr["LifecycleManager"]
    MailboxMgr["MailboxManager"]
    LeaderInbox["Leader Inbox"]
    
    Worker --> TaskList
    TaskList --> CheckTasks
    CheckTasks -->|No| SendIdle
    CheckTasks -->|Yes| Worker
    SendIdle --> LifecycleMgr
    LifecycleMgr --> MailboxMgr
    MailboxMgr --> LeaderInbox
    
    Note1["Idle message includes:<br/>- agent_name<br/>- agent_id<br/>- last_task (optional)<br/>- status (optional)"]
    SendIdle -.-> Note1
```

**Sources:**
- [clawteam/team/lifecycle.py:64-89]()
- [clawteam/spawn/prompt.py:104-105]()

---

## Automatic Exit and Keepalive

When an agent process exits, ClawTeam provides mechanisms to either clean up abandoned work or automatically resume the agent if keepalive is enabled.

### Resumable Agent Keepalive

For interactive CLI agents (like `claude-code` or `codex`), ClawTeam can wrap the execution in a shell loop that automatically resumes the agent after a clean exit if there is more work to do.

```mermaid
flowchart TD
    Start["Initial Command"] --> Loop["while true"]
    Loop --> Run["eval '$__ct_cmd'"]
    Run --> ExitHook["lifecycle on-exit"]
    ExitHook --> CheckKeep["lifecycle should-keepalive"]
    CheckKeep -->|True| Resume["__ct_cmd='$__ct_resume'"]
    Resume --> Loop
    CheckKeep -->|False| End["exit $__ct_status"]
```

**Sources:**
- [clawteam/spawn/keepalive.py:53-91]()
- [clawteam/spawn/keepalive.py:11-35]() (build_resume_command)

### Process Liveness and Registry

ClawTeam tracks spawned processes in a `spawn_registry.json` to monitor health and identify "zombie" processes (agents running longer than a threshold).

| Backend | Liveness Check Mechanism | Code Entity |
|---------|-------------------------|-------------|
| `tmux` | Check `pane_dead` flag and current command | `_tmux_pane_alive` [clawteam/spawn/registry.py:171-193]() |
| `subprocess` | Check OS PID status | `_pid_alive` [clawteam/spawn/registry.py:195-216]() |
| `wsh` | Query TideTerm JSON-RPC | `_wsh_block_alive` [clawteam/spawn/registry.py:78]() |

**Sources:**
- [clawteam/spawn/registry.py:55-80]()
- [clawteam/spawn/registry.py:93-118]() (list_zombie_agents)

---

## Lifecycle Manager Architecture

The `LifecycleManager` class encapsulates all lifecycle operations and coordinates with the mailbox system.

```mermaid
classDiagram
    class LifecycleManager {
        +team_name: str
        +mailbox: MailboxManager
        +request_shutdown(from_agent, to_agent, reason) str
        +approve_shutdown(agent_name, request_id, requester_name)
        +reject_shutdown(agent_name, request_id, requester_name, reason)
        +send_idle(agent_name, agent_id, leader_name, last_task, task_status)
        +cleanup_team(team_name) bool$
    }
    
    class MailboxManager {
        +send(from_agent, to, content, msg_type, ...)
    }
    
    class MessageType {
        <<enumeration>>
        shutdown_request
        shutdown_approved
        shutdown_rejected
        idle
    }
    
    LifecycleManager --> MailboxManager : uses
    LifecycleManager --> MessageType : uses
```

**Sources:**
- [clawteam/team/lifecycle.py:12-119]()
- [clawteam/team/models.py:15-32]() (MessageType)

---

## Integration with Cost Tracking

As part of the lifecycle, agents are instructed to report their token usage and costs before they go idle or exit.

```bash
# Agent reports cost at the end of a task batch
clawteam cost report my-team --input-tokens 1500 --output-tokens 800 --cost-cents 4.5
```

**Sources:**
- [clawteam/spawn/prompt.py:95]()
- [tests/test_costs.py:27-44]()

---

