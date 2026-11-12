<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/open-agent-platform · page 7 Agent Inbox · fetched 2026-10-26 -->

# Agent Inbox

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/web/src/components/agent-inbox/contexts/ThreadContext.tsx](apps/web/src/components/agent-inbox/contexts/ThreadContext.tsx)
- [apps/web/src/components/agent-inbox/index.tsx](apps/web/src/components/agent-inbox/index.tsx)
- [apps/web/src/components/inbox-sidebar/index.tsx](apps/web/src/components/inbox-sidebar/index.tsx)

</details>



The Agent Inbox is a system for managing agent threads that require human intervention. It provides a centralized interface for viewing, filtering, and responding to agent conversations that have been interrupted and are waiting for human input. This system handles the complete lifecycle of interrupted agent threads, from discovery through human response submission.

For information about the general chat interface with agents, see [Chat Interface](#4). For details about agent configuration and management, see [Agent Management](#3).

## System Architecture

The Agent Inbox consists of three main components that work together to provide thread management capabilities:

```mermaid
graph TB
    subgraph "Agent Inbox Core"
        AgentInboxComponent["AgentInbox Component<br/>apps/web/src/components/agent-inbox/index.tsx"]
        InboxView["AgentInboxView<br/>List View"]
        ThreadView_["ThreadView<br/>Thread Detail View"]
    end
    
    subgraph "State Management"
        ThreadsContext["ThreadsContext<br/>apps/web/src/components/agent-inbox/contexts/ThreadContext.tsx"]
        QueryState["Query State<br/>nuqs - URL Parameters"]
        ScrollPosition["useScrollPosition<br/>Scroll State Management"]
    end
    
    subgraph "UI Components"
        InboxSidebar["InboxSidebar<br/>apps/web/src/components/inbox-sidebar/index.tsx"]
        AgentSelection["Agent Selection"]
        ThreadList["Thread List Display"]
    end
    
    subgraph "External Services"
        LangGraphSDK["LangGraph SDK<br/>client.threads.search()"]
        AuthContext["AuthContext<br/>session.accessToken"]
        AgentsContext["AgentsContext<br/>Available Agents"]
    end
    
    AgentInboxComponent --> InboxView
    AgentInboxComponent --> ThreadView_
    AgentInboxComponent --> QueryState
    AgentInboxComponent --> ScrollPosition
    
    InboxView --> ThreadsContext
    ThreadView_ --> ThreadsContext
    InboxSidebar --> ThreadsContext
    InboxSidebar --> AgentsContext
    
    ThreadsContext --> LangGraphSDK
    ThreadsContext --> AuthContext
    
    QueryState --> ThreadsContext
    
    style ThreadsContext fill:#f9f,stroke:#333,stroke-width:2px
    style AgentInboxComponent fill:#bbf,stroke:#333,stroke-width:2px
```

Sources: [apps/web/src/components/agent-inbox/index.tsx:1-210](), [apps/web/src/components/agent-inbox/contexts/ThreadContext.tsx:1-469](), [apps/web/src/components/inbox-sidebar/index.tsx:1-274]()

## Thread Management System

The thread management system handles the complete lifecycle of agent threads requiring human intervention. The system processes different thread statuses and manages their state transitions:

```mermaid
graph TB
    subgraph "Thread Processing Pipeline"
        SearchThreads["client.threads.search()<br/>ThreadsContext.fetchThreads()"]
        ProcessBatch["Promise.all()<br/>Batch Processing"]
        ClassifyThread["Thread Classification"]
        InterruptedHandler["processInterruptedThread()<br/>getInterruptFromThread()"]
        NonInterruptedHandler["processThreadWithoutInterrupts()"]
        StateHandler["client.threads.getState()<br/>Fallback Processing"]
    end
    
    subgraph "Thread States"
        Interrupted["interrupted<br/>Thread.status === 'interrupted'"]
        HumanNeeded["human_response_needed<br/>Custom Status"]
        Other["success | error | cancelled<br/>Standard Statuses"]
    end
    
    subgraph "Thread Data Structure"
        ThreadData["ThreadData<T><br/>status: EnhancedThreadStatus<br/>thread: Thread<T><br/>interrupts?: Interrupt[]<br/>invalidSchema?: boolean"]
    end
    
    SearchThreads --> ProcessBatch
    ProcessBatch --> ClassifyThread
    
    ClassifyThread --> Interrupted
    ClassifyThread --> HumanNeeded  
    ClassifyThread --> Other
    
    Interrupted --> InterruptedHandler
    Interrupted --> StateHandler
    HumanNeeded --> NonInterruptedHandler
    Other --> NonInterruptedHandler
    
    InterruptedHandler --> ThreadData
    NonInterruptedHandler --> ThreadData
    StateHandler --> ThreadData
    
    style ThreadData fill:#f9f,stroke:#333,stroke-width:2px
    style SearchThreads fill:#bbf,stroke:#333,stroke-width:2px
```

Sources: [apps/web/src/components/agent-inbox/contexts/ThreadContext.tsx:77-235](), [apps/web/src/components/agent-inbox/contexts/ThreadContext.tsx:138-215]()

### Thread Filtering and Pagination

The system supports multiple filtering modes for different thread states:

| Filter Type | Description | API Parameters |
|-------------|-------------|----------------|
| `interrupted` | Threads with status "interrupted" | `{ status: "interrupted" }` |
| `human_response_needed` | Custom filter for threads needing human input | No status filter, handled in processing |
| `all` | All threads regardless of status | No status filter |
| Other statuses | Standard LangGraph thread statuses | `{ status: <ThreadStatus> }` |

Query parameters control the filtering and pagination behavior through the `nuqs` library:

- `inbox`: Filter type (default: "interrupted")
- `offset`: Pagination offset (default: 0)  
- `limit`: Results per page (default: 10, max: 100)
- `agentInbox`: Selected agent ID in format "assistantId:deploymentId"

Sources: [apps/web/src/components/agent-inbox/contexts/ThreadContext.tsx:64-131](), [apps/web/src/components/agent-inbox/index.tsx:33-42]()

## Human Response System

The human response system enables users to provide input to interrupted agent threads and resume their execution:

```mermaid
graph LR
    subgraph "Response Submission"
        SendResponse["sendHumanResponse()<br/>ThreadsContext"]
        StreamOption["stream?: boolean<br/>Options Parameter"]
        ResponseData["HumanResponse[]<br/>Array of Responses"]
    end
    
    subgraph "LangGraph Integration"
        RunsCreate["client.runs.create()<br/>Non-streaming"]
        RunsStream["client.runs.stream()<br/>Streaming Mode"]
        ResumeCommand["command: { resume: response }<br/>Resume Configuration"]
    end
    
    subgraph "Thread State Management"
        IgnoreThread["ignoreThread()<br/>Mark as Complete"]
        UpdateState["client.threads.updateState()<br/>asNode: '__end__'"]
        RemoveFromList["Filter from threadData<br/>Update UI State"]
    end
    
    SendResponse --> StreamOption
    StreamOption --> RunsCreate
    StreamOption --> RunsStream
    ResponseData --> ResumeCommand
    
    ResumeCommand --> RunsCreate
    ResumeCommand --> RunsStream
    
    IgnoreThread --> UpdateState
    UpdateState --> RemoveFromList
    
    style SendResponse fill:#f9f,stroke:#333,stroke-width:2px
    style IgnoreThread fill:#bbf,stroke:#333,stroke-width:2px
```

The `sendHumanResponse` function supports both streaming and non-streaming modes:

```typescript
// Type signature from ThreadContext
sendHumanResponse: <TStream extends boolean = false>(
  _threadId: string,
  _response: HumanResponse[],
  _options?: { stream?: TStream; }
) => TStream extends true ? AsyncGenerator<...> : Promise<Run>
```

Sources: [apps/web/src/components/agent-inbox/contexts/ThreadContext.tsx:382-430](), [apps/web/src/components/agent-inbox/contexts/ThreadContext.tsx:341-380]()

## Agent Selection and Sidebar

The inbox sidebar provides agent selection functionality, organizing agents by deployment and allowing users to switch between different agent contexts:

```mermaid
graph TB
    subgraph "Agent Organization"
        Deployments["getDeployments()<br/>Deployment[]"]
        AgentsByDeployment["agents.filter()<br/>deploymentId match"]
        GroupByGraph["groupAgentsByGraphs()<br/>Group by graph_id"]
    end
    
    subgraph "Agent Display"
        DeploymentHeaders["Deployment Name Headers"]
        AgentMenuItems["SidebarMenuItem<br/>Agent Selection Buttons"]
        StatusIcons["UploadCloud | House<br/>Deployment Status Icons"]
        Tooltips["TooltipProvider<br/>Agent Information"]
    end
    
    subgraph "Selection Logic"
        HandleAgentSelect["handleAgentSelect()<br/>Agent Selection Handler"]
        UpdateQueryParams["setAgentInboxId()<br/>Update URL Parameters"]
        ResetPagination["setOffset(0), setLimit(10)<br/>Reset Pagination"]
        FetchThreads["fetchThreads()<br/>Load Agent Threads"]
    end
    
    Deployments --> AgentsByDeployment
    AgentsByDeployment --> GroupByGraph
    GroupByGraph --> DeploymentHeaders
    GroupByGraph --> AgentMenuItems
    
    AgentMenuItems --> StatusIcons
    AgentMenuItems --> Tooltips
    AgentMenuItems --> HandleAgentSelect
    
    HandleAgentSelect --> UpdateQueryParams
    UpdateQueryParams --> ResetPagination
    ResetPagination --> FetchThreads
    
    style HandleAgentSelect fill:#f9f,stroke:#333,stroke-width:2px
    style GroupByGraph fill:#bbf,stroke:#333,stroke-width:2px
```

The sidebar integrates with both the `AgentsContext` for available agents and the `ThreadsContext` for thread management operations.

Sources: [apps/web/src/components/inbox-sidebar/index.tsx:36-76](), [apps/web/src/components/inbox-sidebar/index.tsx:100-196]()

## State Management and Navigation

The Agent Inbox uses a sophisticated state management system that coordinates URL parameters, React context, and scroll position:

### Query Parameter Management

The system uses `nuqs` for URL-based state management with the following parameters:

| Parameter | Parser | Default | Purpose |
|-----------|--------|---------|---------|
| `agentInbox` | `parseAsString` | - | Selected agent (format: "assistantId:deploymentId") |
| `inbox` | `parseAsString` | "interrupted" | Thread filter type |
| `offset` | `parseAsInteger` | 0 | Pagination offset |
| `limit` | `parseAsInteger` | 10 | Results per page |
| `viewStateThread` | `parseAsString` | - | Selected thread ID for detail view |

### View State Transitions

The system manages transitions between list view and thread detail view with scroll position preservation:

```mermaid
stateDiagram-v2
    [*] --> ListView: "Initial Load"
    ListView --> ThreadView: "selectedThreadIdParam set"
    ThreadView --> ListView: "selectedThreadIdParam cleared"
    
    state ListView {
        [*] --> LoadingAgents
        LoadingAgents --> ShowingThreadList: "Agents loaded"
        ShowingThreadList --> SaveScrollPosition: "Thread selected"
    }
    
    state ThreadView {
        [*] --> LoadingThread
        LoadingThread --> ShowingThreadDetail: "Thread loaded"
        ShowingThreadDetail --> RestoreScrollPosition: "Back to list"
    }
    
    SaveScrollPosition --> ThreadView
    RestoreScrollPosition --> ListView
```

Sources: [apps/web/src/components/agent-inbox/index.tsx:95-156](), [apps/web/src/components/agent-inbox/index.tsx:28-51]()

## Integration Points

The Agent Inbox integrates with several external systems and contexts:

### Authentication Integration

- Uses `useAuthContext()` to access `session.accessToken`
- All LangGraph API calls require valid authentication tokens
- Displays error messages when authentication is unavailable

### LangGraph SDK Integration

Key API endpoints used:

- `client.threads.search()`: Search for threads with filters
- `client.threads.get()`: Fetch individual thread details  
- `client.threads.getState()`: Get thread state for interrupt processing
- `client.threads.updateState()`: Update thread state (for ignoring threads)
- `client.runs.create()`: Create new runs to resume threads
- `client.runs.stream()`: Create streaming runs for real-time responses

### Agent Management Integration

- Integrates with `AgentsContext` for available agent list
- Uses `groupAgentsByGraphs()` utility for agent organization
- Supports both local and deployed agent types through deployment detection

Sources: [apps/web/src/components/agent-inbox/contexts/ThreadContext.tsx:59-95](), [apps/web/src/components/inbox-sidebar/index.tsx:28-40](), [apps/web/src/components/agent-inbox/contexts/ThreadContext.tsx:409-425]()

---

