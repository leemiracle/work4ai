<!-- source: DeepWiki mcp.deepwiki.com · repo makenotion/claude-code-notion-plugin · page 7 Advanced Topics · fetched 2026-10-26 -->

# Advanced Topics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [commands/tasks/build.md](commands/tasks/build.md)
- [skills/notion/knowledge-capture/SKILL.md](skills/notion/knowledge-capture/SKILL.md)

</details>



This page covers advanced usage patterns, implementation details, and power-user workflows for the Notion plugin. These topics assume familiarity with basic plugin operations. For introductory command usage, see [Slash Commands Reference](#5). For task management basics, see [Task Management Workflow](#4).

The material here focuses on:
- How the agent-user communication protocol works under the hood
- Polling mechanisms and sub-agent architecture (detailed in [Agent Polling and Sub-Agents](#7.1))
- Knowledge capture implementation patterns (detailed in [Knowledge Capture Workflows](#7.2))
- Context management strategies
- Advanced MCP tool usage patterns

## Communication Protocol Implementation

The task management commands (`/Notion:tasks:plan` and `/Notion:tasks:build`) implement an asynchronous communication pattern where Notion itself serves as the message bus between agent and user. This allows users to monitor progress without watching the Claude Code session.

### Protocol Flow

```mermaid
sequenceDiagram
    participant Agent as "Agent<br/>(Claude Code)"
    participant MCP as "Notion MCP<br/>Tools"
    participant Board as "Notion Board<br/>(Properties + Comments)"
    participant User as "User<br/>(Notion UI)"
    
    Agent->>MCP: "update_page_property"<br/>property="Agent status"<br/>value="🤖 Starting..."
    MCP->>Board: Update property
    
    User->>Board: Views status in real-time
    
    Agent->>MCP: "update_page_property"<br/>property="Agent status"<br/>value="📂 Searching files..."
    MCP->>Board: Update property
    
    rect rgb(240, 240, 240)
    note right of Agent: Agent needs input
    Agent->>MCP: "add_comment"<br/>text="Message from Claude:<br/>[question]"
    MCP->>Board: Add comment
    
    Agent->>MCP: "update_page_property"<br/>property="Agent blocked"<br/>value=true
    MCP->>Board: Update property
    
    Agent->>MCP: "update_page_property"<br/>property="Agent status"<br/>value="❓ Choose color scheme"
    MCP->>Board: Update property
    end
    
    User->>Board: Sees blocked status
    User->>Board: Adds comment with response
    
    loop "Every 10 seconds"
        Agent->>MCP: "get_comments"<br/>page_id=task_url
        MCP->>Board: Fetch comments
        Board->>MCP: Return comment list
        MCP->>Agent: New comments
        
        alt "Response found"
            Agent->>MCP: "update_page_property"<br/>property="Agent blocked"<br/>value=false
            Agent->>Agent: Resume execution
        end
    end
```

**Sources:** [commands/tasks/build.md:36-48]()

### Required Notion Properties

The communication protocol requires specific properties on the task board:

| Property Name | Type | Purpose | Values |
|--------------|------|---------|--------|
| `Status` | Select/Status | Overall task state | "Planning", "In progress", "Done" |
| `Agent status` | Text | Real-time agent activity | Emoji + brief description |
| `Agent blocked` | Checkbox | Indicates agent awaiting input | `true` when blocked, `false` otherwise |

The [/Notion:tasks:setup](#4.1) command creates these properties automatically.

**Sources:** [commands/tasks/build.md:22-23](), [commands/tasks/build.md:41]()

### Status Update Patterns

The `Agent status` field follows a consistent convention of emoji prefix followed by brief description:

```
Working states:
- "🤖 Starting..."
- "📂 Searching relevant files..."
- "✍️ Writing plan..."
- "🎨 Updating color scheme..."
- "🧪 Running tests..."

Blocked states:
- "❓ Choose a color scheme"
- "❓ Give architecture feedback"
- "❓ Clarify requirement"
```

These updates occur throughout task execution via repeated `update_page_property` MCP calls to the same property.

**Sources:** [commands/tasks/build.md:23](), [commands/tasks/build.md:27](), [commands/tasks/build.md:41]()

## Sub-Agent Architecture for Polling

To prevent context pollution during long-running tasks, the polling mechanism uses a sub-agent pattern. This architectural decision isolates the repetitive polling operations from the main agent's context.

### Polling Implementation Strategy

```mermaid
flowchart TB
    MainAgent["Main Agent<br/>(Primary Task Execution)"]
    
    MainAgent -->|"Needs user input"| AddComment["MCP: add_comment<br/>'Message from Claude: [question]'"]
    AddComment --> SetBlocked["MCP: update_page_property<br/>Agent blocked = true"]
    SetBlocked --> SetStatus["MCP: update_page_property<br/>Agent status = '❓ ...'"]
    
    SetStatus --> SpawnSub["Spawn Sub-Agent<br/>max_turns=100"]
    
    SpawnSub --> SubAgent["Sub-Agent<br/>(Isolated Context)"]
    
    SubAgent --> PollLoop{"Polling Loop"}
    
    PollLoop --> Sleep["bash: sleep 10"]
    Sleep --> GetComments["MCP: get_comments<br/>page_id=task_url"]
    GetComments --> Check{"New user<br/>comment?"}
    
    Check -->|"No"| PollLoop
    Check -->|"Yes"| Unblock["MCP: update_page_property<br/>Agent blocked = false"]
    Unblock --> Return["Return to Main Agent<br/>with user response"]
    
    Return --> MainAgent
```

**Sources:** [commands/tasks/build.md:44-47]()

### Sub-Agent Configuration

The polling sub-agent uses specific parameters:

- **max_turns=100**: Allows up to 100 polling cycles (1000 seconds / ~16.7 minutes)
- **Interleaved operations**: Bash `sleep` commands between MCP `get_comments` calls
- **Context isolation**: Polling history doesn't pollute parent agent's token window

**Implementation pattern:**
```
1. Main agent triggers sub-agent for polling
2. Sub-agent executes: sleep 10 → get_comments → check for response
3. Loop continues until user responds or max_turns reached
4. Sub-agent returns control with user response
5. Main agent continues with response data
```

**Sources:** [commands/tasks/build.md:46-47]()

## Knowledge Capture Architecture

The Knowledge Capture skill ([skills/notion/knowledge-capture/SKILL.md:1-201]()) implements a six-stage pipeline that transforms conversational content into structured Notion documentation.

### Knowledge Capture Pipeline

```mermaid
flowchart LR
    subgraph "Input"
        Conv["Conversation<br/>Context"]
    end
    
    subgraph "Processing Stages"
        Extract["1. Extract<br/>Key content<br/>from context"]
        Classify["2. Classify<br/>Content type<br/>(6 types)"]
        Structure["3. Structure<br/>Apply template<br/>per type"]
        Destination["4. Determine<br/>Destination<br/>(wiki/database)"]
        Create["5. Create<br/>MCP: create_pages"]
        Link["6. Link<br/>Update indexes<br/>Make discoverable"]
    end
    
    subgraph "Output"
        NotionPage["Notion Page<br/>(Discoverable)"]
    end
    
    Conv --> Extract
    Extract --> Classify
    Classify --> Structure
    Structure --> Destination
    Destination --> Create
    Create --> Link
    Link --> NotionPage
```

**Sources:** [skills/notion/knowledge-capture/SKILL.md:20-108]()

### Content Type Classification

The system recognizes six content types, each with specific structure:

| Content Type | Template Structure | Typical Use Case |
|--------------|-------------------|------------------|
| Concept/Definition | Overview → Definition → Characteristics → Examples → Use Cases → Related | Explaining technical terms |
| How-To Guide | Overview → Prerequisites → Steps → Verification → Troubleshooting → Related | Process documentation |
| Decision Record | Context → Decision → Rationale → Options Considered → Consequences → Implementation | Architecture decisions |
| FAQ Entry | Short Answer → Detailed Explanation → Examples → When to Use → Related Questions | Common questions |
| Meeting Summary | Context → Discussion → Decisions → Action Items | Meeting notes |
| Learning/Post-mortem | What Happened → What Went Well → What Didn't → Root Causes → Learnings → Actions | Retrospectives |

**Sources:** [skills/notion/knowledge-capture/SKILL.md:34-45](), [skills/notion/knowledge-capture/SKILL.md:112-119]()

### Destination Routing Patterns

Content is routed to different Notion structures based on type and organizational needs:

```mermaid
graph TB
    Content["Classified Content"]
    
    Content --> General["General Wiki<br/>(Standalone pages)"]
    Content --> Project["Project Wiki<br/>(Child of project)"]
    Content --> DocDB["Documentation Database<br/>(Properties: Title, Type,<br/>Category, Tags)"]
    Content --> DecisionDB["Decision Log Database<br/>(Properties: Decision,<br/>Date, Status, Domain)"]
    Content --> FAQDB["FAQ Database<br/>(Properties: Question,<br/>Category, Tags)"]
    
    General --> Index1["Update wiki index<br/>MCP: update_page"]
    Project --> Index2["Link from project page<br/>MCP: update_page"]
    DocDB --> Index3["Set database properties<br/>MCP: create_page"]
    DecisionDB --> Index3
    FAQDB --> Index3
```

**Sources:** [skills/notion/knowledge-capture/SKILL.md:59-68](), [skills/notion/knowledge-capture/SKILL.md:120-131]()

## Context Management Strategies

Long-running agent sessions accumulate context tokens. The plugin employs several strategies to manage context efficiently.

### Context Pollution Prevention

| Strategy | Implementation | Benefit |
|----------|---------------|---------|
| Sub-agent polling | Isolate polling loops in sub-agents with `max_turns=100` | Main agent context stays clean |
| Status field updates | Use same property repeatedly instead of creating new content | Constant memory footprint |
| Comment-based communication | User responses via Notion comments, not chat messages | Context growth controlled |
| Periodic status snapshots | Agent status field shows current state only | No history accumulation |

**Sources:** [commands/tasks/build.md:46]()

### MCP Tool Call Patterns

Efficient MCP usage reduces context bloat:

**Pattern 1: Batch property updates**
```
Instead of:
  update_page_property(status)
  update_page_property(blocked)
  update_page_property(agent_status)

Use single call when possible:
  update_page_properties(status, blocked, agent_status)
```

**Pattern 2: Targeted content fetching**
```
Instead of:
  get_page(full_content=true)

Use:
  get_page_properties(specific_props=['Status', 'Agent blocked'])
```

**Pattern 3: Comment pagination**
```
Use:
  get_comments(page_id, limit=10, since_last_poll=true)

Avoid:
  get_comments(page_id, full_history=true)
```

**Sources:** [commands/tasks/build.md:16-19]()

## Advanced MCP Tool Combinations

Certain workflows benefit from chaining MCP tools in specific sequences.

### Search → Create → Link Pattern

Common pattern for knowledge capture:

```mermaid
flowchart LR
    Start["Need to<br/>save content"]
    
    Start --> Search["MCP: search_pages<br/>Find existing wiki"]
    Search --> Check{"Exists?"}
    
    Check -->|"Yes"| Update["MCP: append_blocks<br/>Add to existing"]
    Check -->|"No"| Create["MCP: create_page<br/>Create new page"]
    
    Create --> GetParent["MCP: get_page<br/>Get parent wiki page"]
    GetParent --> AddLink["MCP: append_blocks<br/>Add link in index"]
    
    Update --> Done["Content saved<br/>and discoverable"]
    AddLink --> Done
```

**Sources:** [skills/notion/knowledge-capture/SKILL.md:82-108]()

### Query → Filter → Bulk Update Pattern

For database operations:

```
1. database_query(database_id, filters={...})
   → Returns matching pages
   
2. For each page:
   update_page_property(page_id, property, value)
   
3. Optional: add_comment to notify users of bulk change
```

This pattern is useful for task board management, status migrations, and bulk property updates.

**Sources:** [commands/tasks/build.md:16-23]()

### Task Execution Lifecycle

The complete task execution lifecycle combines multiple patterns:

```mermaid
stateDiagram-v2
    [*] --> Fetch: "MCP: get_page<br/>(task details)"
    
    Fetch --> UpdateStatus: "MCP: update_page_property<br/>Status = 'In progress'"
    
    UpdateStatus --> Work: "Agent executes task"
    
    Work --> StatusUpdate: "MCP: update_page_property<br/>Agent status = '🤖 ...'"
    StatusUpdate --> Work: "Continue working"
    
    Work --> Blocked: "Need user input"
    
    Blocked --> AddComment: "MCP: add_comment<br/>'Message from Claude:...'"
    AddComment --> SetBlock: "MCP: update_page_property<br/>Agent blocked = true"
    SetBlock --> Poll: "Sub-agent polls"
    
    Poll --> Poll: "Every 10s:<br/>MCP: get_comments"
    Poll --> Unblock: "User responded"
    
    Unblock --> ClearBlock: "MCP: update_page_property<br/>Agent blocked = false"
    ClearBlock --> Work: "Resume with response"
    
    Work --> Complete: "Task finished"
    
    Complete --> MarkDone: "MCP: update_page_property<br/>Status = 'Done'"
    
    MarkDone --> CheckCode: "Code changes?"
    
    CheckCode --> ExplainDiff: "Yes: /Notion:tasks:explain-diff"
    CheckCode --> Notify: "No: Skip diff"
    
    ExplainDiff --> Notify: "MCP: add_comment<br/>'Task complete, see diff'"
    
    Notify --> [*]
```

**Sources:** [commands/tasks/build.md:15-34]()

## Best Practices Summary

| Practice | Rationale | Implementation |
|----------|-----------|----------------|
| Use sub-agents for polling | Prevents context pollution | Set `max_turns=100`, isolate polling logic |
| Update same status field | Constant memory usage | Repeatedly call `update_page_property` on `Agent status` |
| Comment-based communication | Out-of-band messaging | Use `add_comment` + poll pattern |
| Emoji conventions | Visual clarity for users | Consistent emoji prefixes in status updates |
| Targeted property fetches | Reduce payload size | Fetch only needed properties |
| Link after creation | Ensure discoverability | Update parent/index pages after creating content |

**Sources:** [commands/tasks/build.md:1-52](), [skills/notion/knowledge-capture/SKILL.md:172-182]()

---

