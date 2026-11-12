<!-- source: DeepWiki mcp.deepwiki.com · repo alinaqi/claude-bootstrap · page 8 Team Collaboration · fetched 2026-10-27 -->

# Team Collaboration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This document explains how multiple developers coordinate work on the same repository when using Claude Code. The system provides file-based state management, todo claiming, active session tracking, and conflict detection to prevent duplicate work and merge conflicts.

For implementation details of the coordination commands, see [Multi-Developer Coordination](#8.1). For details about the shared state file structures, see [Shared State Management](#8.2).

## The Coordination Problem

When multiple developers use Claude Code (or Claude Desktop) on the same repository, several coordination challenges arise:

- **Duplicate work**: Two developers unknowingly implement the same todo
- **Merge conflicts**: Multiple developers modify the same files simultaneously
- **Context loss**: Developer B doesn't know what Developer A is currently working on
- **Decision drift**: Architectural decisions made by one developer are invisible to others

Claude Bootstrap solves this with a file-based state management system that tracks active sessions, claimed todos, and file ownership through standard git workflows.

**Sources:** [README.md:211-253]()

## System Architecture

```mermaid
graph TB
    subgraph "Developer Workflow"
        DEV_A["Developer A<br/>Claude Code Session"]
        DEV_B["Developer B<br/>Claude Code Session"]
    end
    
    subgraph "Coordination Commands"
        CHECK["/check-contributors"]
        STATUS["/check-contributors --status"]
        TEAM["/check-contributors --team"]
    end
    
    subgraph "State Files (_project_specs/team)"
        STATE["state.md<br/>Active sessions<br/>Claimed todos<br/>File ownership"]
        CONTRIB["contributors.md<br/>Team roster<br/>Focus areas<br/>Ownership"]
        HANDOFFS["handoffs/<br/>Context transfer<br/>Work notes"]
        DECISIONS["../decisions.md<br/>Shared decisions"]
    end
    
    subgraph "Conflict Detection"
        DETECT["Monitor file overlap"]
        WARN["⚠️ Conflict warnings"]
    end
    
    DEV_A --> CHECK
    DEV_B --> CHECK
    
    CHECK --> STATE
    CHECK --> CONTRIB
    STATUS --> STATE
    TEAM --> STATE
    TEAM --> CONTRIB
    
    STATE --> DETECT
    CONTRIB --> DETECT
    DETECT --> WARN
    
    DEV_A -.->|"Update on checkpoint"| STATE
    DEV_B -.->|"Update on checkpoint"| STATE
    
    DEV_A -.->|"Handoff notes"| HANDOFFS
    DEV_B -.->|"Read context"| HANDOFFS
    
    STATE -.->|"Log decisions"| DECISIONS
```

**Diagram: Team Collaboration System Components**

The system uses three primary state files in `_project_specs/team/` that are committed to git, enabling coordination through standard pull/push workflows without requiring external infrastructure.

**Sources:** [README.md:225-231](), [README.md:235-242]()

## Core Workflow Pattern

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Git as "git"
    participant Check as "/check-contributors"
    participant State as "state.md"
    participant Todos as "todos/active.md"
    participant Claude as "Claude Code"
    
    Dev->>Git: git pull
    Note over Git: Get latest state
    
    Dev->>Check: Run command
    Check->>State: Read current state
    Check->>Dev: Show active sessions<br/>Show claimed todos<br/>Show conflicts
    
    Dev->>State: Claim todo<br/>Update active session
    Dev->>Git: git add state.md<br/>git commit -m "Claim TODO-042"<br/>git push
    
    Dev->>Claude: Work on feature
    Note over Claude: Active development
    
    Dev->>State: Checkpoint update<br/>Log file changes
    Dev->>Git: git add state.md<br/>git commit & push
    
    Dev->>Claude: Continue work
    
    Dev->>State: Mark complete<br/>Clear active session
    Dev->>Todos: Move to completed.md
    Dev->>Git: git commit & push
```

**Diagram: Standard Team Collaboration Workflow**

The workflow enforces explicit state updates at key checkpoints: claiming work (start), progress updates (during), and completion (end). This creates visibility without requiring real-time communication.

**Sources:** [README.md:243-246]()

## The `/check-contributors` Command

The `/check-contributors` command is the primary entry point for team coordination. It detects whether a project is solo or team-based and offers appropriate actions.

**Command Variants:**

| Command | Purpose | Output |
|---------|---------|--------|
| `/check-contributors` | Full analysis and conversion | Detect mode, show state, offer conversion |
| `/check-contributors --status` | Quick status check | Show active sessions and claimed todos only |
| `/check-contributors --team` | Force team conversion | Create team structure immediately |

**Sources:** [README.md:249-253]()

### Detection Logic

```mermaid
flowchart TD
    START["Run /check-contributors"]
    
    CHECK_TEAM["Check _project_specs/team/<br/>directory exists?"]
    
    SOLO["Solo Project Mode"]
    TEAM["Team Project Mode"]
    
    OFFER["Offer conversion:<br/>'This looks like solo project.<br/>Convert to team?'"]
    
    CONVERT["Create team structure:<br/>- state.md<br/>- contributors.md<br/>- handoffs/"]
    
    SHOW_STATE["Show current state:<br/>- Active sessions<br/>- Claimed todos<br/>- File ownership<br/>- Conflict warnings"]
    
    START --> CHECK_TEAM
    CHECK_TEAM -->|"No"| SOLO
    CHECK_TEAM -->|"Yes"| TEAM
    
    SOLO --> OFFER
    OFFER -->|"Yes"| CONVERT
    OFFER -->|"No"| END["Continue solo"]
    
    CONVERT --> SHOW_STATE
    TEAM --> SHOW_STATE
    
    SHOW_STATE --> END
```

**Diagram: Project Mode Detection and Conversion**

**Sources:** [README.md:215-222]()

## State File Structure

### state.md Format

The `_project_specs/team/state.md` file tracks real-time project state:

```markdown
# Project State

Last updated: 2024-01-15 14:30 UTC

## Active Sessions

| Developer | Working On | Files | Started | Last Update |
|-----------|------------|-------|---------|-------------|
| alice | TODO-042: Email validation | src/auth/signup.ts, tests/signup.test.ts | 2024-01-15 13:00 | 2024-01-15 14:30 |
| bob | TODO-038: API rate limiting | src/middleware/ratelimit.ts | 2024-01-15 12:00 | 2024-01-15 14:15 |

## Claimed Todos

| ID | Title | Claimed By | Claimed At |
|----|-------|------------|------------|
| TODO-042 | Add email validation | alice | 2024-01-15 13:00 |
| TODO-038 | Implement rate limiting | bob | 2024-01-15 12:00 |

## File Ownership (Current Session)

| File Path | Owner | Purpose |
|-----------|-------|---------|
| src/auth/signup.ts | alice | Email validation |
| tests/signup.test.ts | alice | Validation tests |
| src/middleware/ratelimit.ts | bob | Rate limiter |

## Conflict Warnings

⚠️ No conflicts detected
```

**Key sections:**

- **Active Sessions**: Who's working on what right now (in-memory state)
- **Claimed Todos**: Reserved work items (prevents duplicate work)
- **File Ownership**: Current file modification ownership (for conflict detection)
- **Conflict Warnings**: Alerts when multiple developers touch overlapping files

**Sources:** [README.md:227-230]()

### contributors.md Format

The `_project_specs/team/contributors.md` file maintains team roster and ownership:

```markdown
# Team Contributors

## Active Contributors

| Developer | Role | Focus Areas | Since |
|-----------|------|-------------|-------|
| alice | Backend Lead | Auth, API, Database | 2024-01-01 |
| bob | Frontend Lead | UI, Components, State | 2024-01-05 |
| carol | Full Stack | Features, Integration | 2024-01-10 |

## Code Ownership

| Area | Primary | Backup |
|------|---------|--------|
| Authentication | alice | carol |
| UI Components | bob | carol |
| Database Schema | alice | - |
| API Routes | alice | carol |

## Communication

- Stand-ups: Daily 10am EST (async via state.md updates)
- Handoffs: Use _project_specs/team/handoffs/ directory
- Decisions: Log in _project_specs/decisions.md
```

**Sources:** [README.md:229]()

### handoffs/ Directory

The `_project_specs/team/handoffs/` directory contains context transfer notes when passing work between developers:

```
_project_specs/team/handoffs/
├── 2024-01-15-alice-to-bob-auth-module.md
├── 2024-01-14-bob-to-carol-ui-refactor.md
└── README.md
```

**Handoff note format:**

```markdown
# Handoff: Auth Module Refactor

**From:** alice  
**To:** bob  
**Date:** 2024-01-15  
**Context:** TODO-042 Email validation

## Current State
- Email validation logic in src/auth/signup.ts:45-67
- Tests passing but need edge case coverage
- Found bug with internationalized email addresses

## Remaining Work
- [ ] Add test cases for IDN emails (user@münchen.de)
- [ ] Update validation regex to support RFC 6531
- [ ] Check mobile app compatibility

## Important Context
- Don't modify validatePhone() - it's used by 3 other modules
- Database schema expects lowercase emails (normalize before save)
- See decision DOC-012 about email normalization strategy

## Files Modified
- src/auth/signup.ts
- tests/auth/signup.test.ts

## Branch
- alice/email-validation (pushed, not merged)
```

**Sources:** [README.md:230]()

## Todo Claiming Mechanism

```mermaid
stateDiagram-v2
    [*] --> Unclaimed: "Todo in<br/>active.md"
    
    Unclaimed --> Checking: "/check-contributors"
    
    Checking --> Unclaimed: "No claim"
    Checking --> Claimed: "Developer claims"
    
    Claimed --> InProgress: "Start work"
    
    InProgress --> InProgress: "Checkpoint updates<br/>to state.md"
    
    InProgress --> Complete: "Finish & test"
    
    Complete --> [*]: "Move to<br/>completed.md"
    
    Claimed --> Unclaimed: "Unclaim<br/>(abandon work)"
    
    note right of Claimed
        state.md updated:
        - Claimed Todos section
        - Developer name
        - Timestamp
    end note
    
    note right of InProgress
        state.md tracks:
        - Active session
        - Files being modified
        - Last update time
    end note
```

**Diagram: Todo Claim Lifecycle**

**Claiming prevents duplicate work:**

1. Developer runs `/check-contributors`
2. System shows unclaimed todos from `_project_specs/todos/active.md`
3. Developer claims by updating `state.md`
4. Commit and push claim (atomic reservation)
5. Other developers see claimed status after `git pull`

**Sources:** [README.md:237]()

## Conflict Detection Logic

```mermaid
graph TB
    subgraph "Input: state.md"
        ALICE_SESSION["Alice working on:<br/>src/auth/signup.ts<br/>tests/signup.test.ts"]
        BOB_SESSION["Bob working on:<br/>src/auth/signup.ts<br/>src/auth/login.ts"]
    end
    
    subgraph "Conflict Analysis"
        EXTRACT["Extract file lists<br/>per developer"]
        INTERSECT["Find file overlaps"]
        CLASSIFY["Classify conflict type"]
    end
    
    subgraph "Conflict Types"
        DIRECT["Direct Conflict<br/>Same exact file"]
        ADJACENT["Adjacent Conflict<br/>Same module area"]
        SAFE["No Conflict<br/>Separate areas"]
    end
    
    subgraph "Output: Warnings"
        WARN_HIGH["⚠️ HIGH: Alice & Bob<br/>both editing signup.ts<br/>Coordinate immediately"]
        WARN_MED["💡 MEDIUM: Alice & Bob<br/>both in auth module<br/>Watch for coupling"]
        NO_WARN["✅ No warnings"]
    end
    
    ALICE_SESSION --> EXTRACT
    BOB_SESSION --> EXTRACT
    
    EXTRACT --> INTERSECT
    INTERSECT --> CLASSIFY
    
    CLASSIFY --> DIRECT
    CLASSIFY --> ADJACENT
    CLASSIFY --> SAFE
    
    DIRECT --> WARN_HIGH
    ADJACENT --> WARN_MED
    SAFE --> NO_WARN
```

**Diagram: Conflict Detection Algorithm**

**Conflict severity levels:**

| Level | Condition | Action |
|-------|-----------|--------|
| **HIGH** | Same exact file | Immediate coordination required |
| **MEDIUM** | Same directory/module | Awareness, watch for coupling |
| **LOW** | Related files (imports) | Informational only |
| **NONE** | Separate areas | No action needed |

**Sources:** [README.md:239]()

## Converting Solo to Team Projects

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Cmd as "/check-contributors"
    participant FS as "File System"
    participant State as "state.md"
    participant Contrib as "contributors.md"
    
    Dev->>Cmd: Run in solo project
    Cmd->>FS: Check _project_specs/team/
    FS-->>Cmd: Directory not found
    
    Cmd->>Dev: "Solo project detected.<br/>Convert to team project?"
    Dev->>Cmd: Yes
    
    Cmd->>FS: Create _project_specs/team/
    Cmd->>State: Generate initial state.md
    Note over State: Empty active sessions<br/>Empty claimed todos
    
    Cmd->>Contrib: Generate contributors.md
    Note over Contrib: Current developer as first member<br/>Infer ownership from git history
    
    Cmd->>FS: Create handoffs/ directory
    Cmd->>FS: Create handoffs/README.md
    
    Cmd->>Dev: "Team structure created.<br/>Commit and push."
    
    Dev->>FS: git add _project_specs/team/
    Dev->>FS: git commit -m "Convert to team project"
    Dev->>FS: git push
```

**Diagram: Solo to Team Conversion Process**

**Conversion steps:**

1. Detect no `_project_specs/team/` directory exists
2. Offer conversion to team mode
3. Create directory structure
4. Generate initial `state.md` with empty sessions
5. Generate `contributors.md` from git history
6. Create `handoffs/` directory with README
7. Prompt commit and push

**Sources:** [README.md:218-222]()

## State Update Triggers

The system defines specific checkpoints when developers should update `state.md`:

| Trigger | When | What to Update |
|---------|------|----------------|
| **Claim** | Before starting work | Add to Claimed Todos |
| **Start** | Begin active development | Add to Active Sessions with files |
| **Checkpoint** | Every 1-2 hours during work | Update Last Update timestamp, add new files |
| **Break** | Before ending session | Update status to "Paused" |
| **Handoff** | Passing work to another dev | Create handoff note, update File Ownership |
| **Complete** | Todo finished and tested | Remove from Active Sessions, remove claim |

**Sources:** [README.md:243-246]()

## Integration with Session Management

Team collaboration integrates with the session management system (see [Session Management](#4.2)):

```mermaid
graph LR
    subgraph "Solo Project Files"
        SOLO_STATE["_project_specs/<br/>current-state.md"]
        SOLO_DECISIONS["_project_specs/<br/>decisions.md"]
    end
    
    subgraph "Team Project Files"
        TEAM_STATE["_project_specs/team/<br/>state.md"]
        TEAM_CONTRIB["_project_specs/team/<br/>contributors.md"]
        SHARED_DECISIONS["_project_specs/<br/>decisions.md<br/>(shared)"]
    end
    
    SOLO_STATE -.->|"Personal context"| SOLO_DECISIONS
    TEAM_STATE -.->|"Team context"| SHARED_DECISIONS
    TEAM_CONTRIB -.->|"Ownership context"| SHARED_DECISIONS
    
    TEAM_STATE -->|"Replaces for<br/>coordination"| SOLO_STATE
```

**Diagram: Solo vs. Team State Management**

In team projects, `_project_specs/team/state.md` supplements (not replaces) individual session state. Developers still maintain personal `current-state.md` for their own context, but coordination state lives in the shared `team/state.md`.

**Key difference:**

- **Solo**: `current-state.md` tracks "what am I working on"
- **Team**: `team/state.md` tracks "what is everyone working on"

**Sources:** [README.md:227-230]()

## Example: Two Developer Workflow

**Scenario:** Alice and Bob working on authentication module

### 1. Alice Claims Todo

```bash
# Alice's session
git pull
claude
> /check-contributors
```

**Claude shows:**
```
Project Status: Team Project (2 contributors)

Active Sessions: None
Claimed Todos: None

Available Todos:
- TODO-042: Add email validation (unclaimed)
- TODO-038: Add rate limiting (unclaimed)

Would you like to claim a todo?
```

Alice claims TODO-042, updates `state.md`:

```markdown
## Claimed Todos
| ID | Title | Claimed By | Claimed At |
|----|-------|------------|------------|
| TODO-042 | Add email validation | alice | 2024-01-15 13:00 |
```

Commits: `git commit -m "Claim TODO-042"`

### 2. Bob Checks State

```bash
# Bob's session (after Alice pushed)
git pull
claude
> /check-contributors --status
```

**Claude shows:**
```
Claimed Todos:
- TODO-042: Email validation (alice, claimed 1 hour ago)

Available Todos:
- TODO-038: Add rate limiting (unclaimed)
```

Bob claims TODO-038, different area → no conflict.

### 3. Alice Starts Work

Alice updates `state.md` when beginning active work:

```markdown
## Active Sessions
| Developer | Working On | Files | Started |
|-----------|------------|-------|---------|
| alice | TODO-042 | src/auth/signup.ts, tests/signup.test.ts | 13:00 |
```

### 4. Bob Accidentally Modifies Same File

Bob starts work on rate limiting but mistakenly edits `signup.ts`. When Bob runs `/check-contributors`:

**Claude detects:**
```
⚠️ CONFLICT WARNING

You are modifying: src/auth/signup.ts
Alice is also working on: src/auth/signup.ts (active since 13:00)

Recommendation: Coordinate with alice before continuing.
Consider:
1. Different files for rate limiting logic
2. Wait for alice to complete
3. Coordinate on Slack/handoff note
```

### 5. Alice Completes and Hands Off

Alice finishes email validation but found an edge case that needs attention:

Creates `_project_specs/team/handoffs/2024-01-15-alice-to-bob-email.md`:

```markdown
# Email Validation Edge Case

## Context
Completed basic email validation for TODO-042, but discovered that
internationalized domain names (IDN) need special handling.

## What's Done
- Basic RFC 5322 email validation
- Tests for common cases
- Integration with signup form

## What's Needed
- [ ] Support for IDN emails (münchen.de, etc.)
- [ ] Update regex or use library like `validator.js`
- [ ] Add test cases for IDN

## Files
- src/auth/signup.ts:45-67 (validation logic)
- tests/auth/signup.test.ts (add IDN tests here)
```

Updates `state.md`:
```markdown
## Active Sessions
(empty - alice completed)

## Claimed Todos
(TODO-042 moved to completed)
```

**Sources:** [README.md:243-246]()

## Command Reference Quick Guide

| Command | Use Case | When to Run |
|---------|----------|-------------|
| `/check-contributors` | Start of work session | Before claiming or starting new work |
| `/check-contributors --status` | Quick check during work | Periodically to see team status |
| `/check-contributors --team` | Convert solo project | When adding second developer |

**Sources:** [README.md:249-253]()

## Anti-Patterns to Avoid

| Anti-Pattern | Why It Fails | Correct Approach |
|--------------|--------------|------------------|
| Skip state updates | Team loses visibility, conflicts arise | Update state.md at every checkpoint |
| Claim without pushing | Other devs don't see claim, duplicate work | Always commit and push claims immediately |
| Modify files without claiming | No conflict detection | Claim todo first, then start work |
| Skip handoff notes | Context lost between developers | Always create handoff when passing work |
| Work offline for days | State becomes stale, conflicts increase | Pull frequently, push state updates |

**Sources:** [README.md:235-242]()

## State Management Best Practices

1. **Pull before you start**: Always `git pull` before running `/check-contributors`
2. **Claim atomically**: Commit and push claims immediately to reserve work
3. **Checkpoint frequently**: Update state.md every 1-2 hours during active work
4. **Handoff explicitly**: Create handoff notes even for "obvious" context
5. **Check before commit**: Run `/check-contributors` before pushing to detect conflicts early
6. **Clear on completion**: Remove yourself from active sessions when done

**Sources:** [README.md:243-246]()

---

