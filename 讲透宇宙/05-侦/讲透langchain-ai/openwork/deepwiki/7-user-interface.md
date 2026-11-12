<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/openwork · page 7 User Interface · fetched 2026-10-26 -->

# User Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/renderer/src/App.tsx](src/renderer/src/App.tsx)
- [src/renderer/src/components/chat/ChatContainer.tsx](src/renderer/src/components/chat/ChatContainer.tsx)

</details>



## Purpose and Scope

This page provides an overview of OpenWork's user interface architecture, including the React renderer process structure, component hierarchy, layout system, and state management patterns. The UI is built as an Electron renderer process using React, styled with Tailwind CSS, and manages state through Zustand.

For detailed information about specific UI subsystems, see:
- Application layout and resizable panels: [Application Layout and Structure](#7.1)
- Chat and message display: [Chat Interface](#7.2)
- Thread sidebar and right panel: [Side Panels and Navigation](#7.3)
- Model selection and settings dialogs: [Model Switcher and Settings](#7.4)
- TypeScript type definitions: [Type Definitions and Shared Interfaces](#7.5)

For information about how the UI communicates with the main process, see [IPC Communication System](#2.2). For state management details, see [Global State Management](#2.3).

## Renderer Process Architecture

OpenWork's UI runs in an Electron renderer process, isolated from Node.js APIs for security. The renderer communicates with the main process exclusively through IPC channels exposed via the preload script.

```mermaid
graph TB
    subgraph "Renderer Process (Browser Context)"
        App["App.tsx<br/>Root Component"]
        Store["useAppStore<br/>Zustand Store"]
        Components["UI Components<br/>ChatContainer<br/>ThreadSidebar<br/>RightPanel"]
        Transport["ElectronIPCTransport<br/>LangGraph SDK Bridge"]
    end
    
    subgraph "IPC Bridge"
        WindowAPI["window.api<br/>contextBridge API"]
        IPCChannels["IPC Channels<br/>threads:*<br/>agent:*<br/>models:*<br/>workspace:*"]
    end
    
    subgraph "Main Process"
        Handlers["IPC Handlers"]
        Runtime["Agent Runtime"]
        DB["SQLite Databases"]
    end
    
    App --> Store
    App --> Components
    Components --> Store
    Components --> Transport
    
    Store --> WindowAPI
    Transport --> IPCChannels
    WindowAPI --> IPCChannels
    
    IPCChannels --> Handlers
    Handlers --> Runtime
    Handlers --> DB
    
    style App fill:#e1f5ff
    style Store fill:#f0e1ff
    style WindowAPI fill:#fff4e1
```

**Key Architectural Properties:**

- **Process Isolation**: Renderer has no direct Node.js access; all privileged operations go through IPC
- **Single Source of Truth**: `useAppStore` manages all UI state using Zustand
- **Streaming Integration**: `ElectronIPCTransport` adapts LangGraph's streaming SDK to Electron IPC
- **Type Safety**: TypeScript types are shared between renderer and main processes via `src/types.ts`

**Sources:** [src/renderer/src/App.tsx:1-186](), [src/renderer/src/components/chat/ChatContainer.tsx:1-91]()

## Component Hierarchy

The UI is organized as a hierarchy of specialized components, each responsible for a specific domain.

### Component Tree Structure

```mermaid
graph TD
    App["App.tsx<br/>Root Layout"]
    
    App --> Badge["app-badge<br/>Fixed Position Badge"]
    App --> TitleBar["Titlebar Row<br/>Traffic Light + Tabs"]
    App --> MainArea["Main Content Area"]
    
    TitleBar --> TabBar["TabBar<br/>Thread Tabs"]
    
    MainArea --> LeftSide["Left Column"]
    MainArea --> Center["Center Column"]
    MainArea --> RightSide["Right Column"]
    
    LeftSide --> ThreadSidebar["ThreadSidebar<br/>Thread List + CRUD"]
    
    Center --> TabbedPanel["TabbedPanel<br/>Content Router"]
    TabbedPanel --> ChatTab["Chat Tab"]
    TabbedPanel --> FileTab["File Viewer Tab"]
    
    ChatTab --> ChatContainer["ChatContainer<br/>Messages + Input"]
    ChatContainer --> MessageBubble["MessageBubble[]<br/>Message Display"]
    ChatContainer --> ChatTodos["ChatTodos<br/>Inline Todo Display"]
    ChatContainer --> ModelSwitcher["ModelSwitcher<br/>Model Selection"]
    ChatContainer --> WorkspacePicker["WorkspacePicker<br/>Folder Selection"]
    
    RightSide --> RightPanel["RightPanel<br/>Status Panels"]
    RightPanel --> TodoPanel["TodoPanel<br/>Task List"]
    RightPanel --> FilesystemPanel["FilesystemPanel<br/>File Browser"]
    RightPanel --> SubagentsPanel["SubagentsPanel<br/>Subagent Status"]
    
    style App fill:#e1f5ff
    style ChatContainer fill:#e1f5ff
    style RightPanel fill:#ffe1e1
```

**Sources:** [src/renderer/src/App.tsx:17-186](), [src/renderer/src/components/chat/ChatContainer.tsx:61-590]()

### Component Responsibilities

| Component | File | Primary Responsibility |
|-----------|------|------------------------|
| `App.tsx` | [src/renderer/src/App.tsx]() | Root layout, zoom compensation, resizable column management |
| `ThreadSidebar` | [src/renderer/src/components/sidebar/ThreadSidebar.tsx]() | Thread list display, create/delete/select operations |
| `TabbedPanel` | [src/renderer/src/components/tabs/TabbedPanel.tsx]() | Content routing between chat and file viewer |
| `ChatContainer` | [src/renderer/src/components/chat/ChatContainer.tsx]() | Message display, input handling, agent streaming integration |
| `MessageBubble` | [src/renderer/src/components/chat/MessageBubble.tsx]() | Individual message rendering, tool call display, approval UI |
| `RightPanel` | [src/renderer/src/components/panels/RightPanel.tsx]() | Status panel container with tabs for tasks/files/agents |
| `WorkspacePicker` | [src/renderer/src/components/chat/WorkspacePicker.tsx]() | Workspace folder selection and display |
| `ModelSwitcher` | [src/renderer/src/components/chat/ModelSwitcher.tsx]() | Model/provider selection UI |

**Sources:** [src/renderer/src/App.tsx:1-186](), [src/renderer/src/components/chat/ChatContainer.tsx:1-590](), [src/renderer/src/components/chat/WorkspacePicker.tsx:1-136]()

## Three-Column Layout System

The application uses a fixed three-column layout with resizable panels:

```mermaid
graph LR
    subgraph "Screen Layout"
        Left["Left Column<br/>ThreadSidebar<br/>240-350px<br/>(resizable)"]
        Center["Center Column<br/>TabbedPanel<br/>(fluid)"]
        Right["Right Column<br/>RightPanel<br/>250-450px<br/>(resizable)"]
    end
    
    Left -->|ResizeHandle| Center
    Center -->|ResizeHandle| Right
    
    subgraph "Resize State"
        LeftWidth["leftWidth<br/>useState"]
        RightWidth["rightWidth<br/>useState"]
        DragStart["dragStartWidths<br/>useRef"]
    end
    
    Left -.->|width| LeftWidth
    Right -.->|width| RightWidth
    ResizeHandle -.->|tracks| DragStart
```

**Layout Constants:**

[src/renderer/src/App.tsx:8-15]() defines the panel size constraints:

```typescript
const BADGE_MIN_SCREEN_WIDTH = 235
const LEFT_MAX = 350
const LEFT_DEFAULT = 240
const RIGHT_MIN = 250
const RIGHT_MAX = 450
const RIGHT_DEFAULT = 320
```

**Zoom Compensation:**

The layout implements zoom-aware rendering for macOS traffic light buttons. As users zoom the UI, the titlebar height (36px CSS) shrinks in screen pixels, potentially overlapping the fixed-position traffic lights. The app calculates extra padding dynamically:

[src/renderer/src/App.tsx:28-46]() implements the compensation logic:

1. Detect zoom level by comparing `window.outerWidth / window.innerWidth`
2. Calculate titlebar height in screen pixels: `36px * zoomLevel`
3. Add extra padding if titlebar is shorter than 40 screen pixels (traffic light clearance)
4. Store padding in CSS custom property `--sidebar-safe-padding`

**Sources:** [src/renderer/src/App.tsx:8-92]()

## State Management and Data Flow

### Zustand Store Structure

The UI uses a single Zustand store (`useAppStore`) as the source of truth for all application state. The store is defined in [src/renderer/src/lib/store.ts]() and consumed by components via the `useAppStore` hook.

```mermaid
graph TB
    subgraph "useAppStore State Properties"
        Threads["threads: Thread[]<br/>All threads metadata"]
        CurrentThread["currentThreadId: string | null<br/>Active thread"]
        Messages["messages: Message[]<br/>Current conversation"]
        Todos["todos: Todo[]<br/>Agent task list"]
        Subagents["subagents: Subagent[]<br/>Subagent status"]
        WorkspacePath["workspacePath: string | null<br/>Active workspace"]
        WorkspaceFiles["workspaceFiles: FileItem[]<br/>File tree"]
        PendingApproval["pendingApproval: object | null<br/>HITL request"]
        ErrorByThread["errorByThread: Record<string, string><br/>Thread errors"]
        TabState["tabStateByThread: Record<string, TabState><br/>Per-thread UI state"]
    end
    
    subgraph "Store Actions"
        CreateThread["createThread()<br/>IPC: threads:create"]
        LoadThreads["loadThreads()<br/>IPC: threads:list"]
        AppendMessage["appendMessage(msg)<br/>Add to messages[]"]
        SetTodos["setTodos(todos)<br/>Update todos[]"]
        SetWorkspacePath["setWorkspacePath(path)<br/>Update workspace"]
        SetPendingApproval["setPendingApproval(req)<br/>Trigger HITL dialog"]
    end
    
    subgraph "IPC Communication"
        WindowAPI["window.api.*"]
    end
    
    CreateThread --> WindowAPI
    LoadThreads --> WindowAPI
    
    style Threads fill:#f0e1ff
    style Actions fill:#e1f5ff
```

**Store Update Sources:**

1. **Direct IPC Calls**: Actions like `createThread` call `window.api.threads.create()` and update state
2. **Stream Events**: `ChatContainer` receives events from `ElectronIPCTransport` and calls store actions
3. **User Interactions**: UI components call store actions in response to clicks, form submissions

**Sources:** [src/renderer/src/components/chat/ChatContainer.tsx:67-84]()

### IPC Communication Pattern

Components never directly invoke IPC; they go through the store for consistency:

```mermaid
sequenceDiagram
    participant Component as "UI Component"
    participant Store as "useAppStore"
    participant WindowAPI as "window.api"
    participant Main as "Main Process"
    
    Component->>Store: Call action (e.g., loadThreads)
    Store->>WindowAPI: window.api.threads.list()
    WindowAPI->>Main: IPC: threads:list
    Main-->>WindowAPI: Return threads data
    WindowAPI-->>Store: Resolve promise
    Store->>Store: Update threads state
    Store-->>Component: Re-render with new state
```

**Example: Thread Creation Flow**

[src/renderer/src/components/chat/ChatContainer.tsx:391-442]() shows the submit flow:

1. User submits message via form
2. `handleSubmit` checks workspace path (required)
3. Calls `appendMessage` to add user message to store
4. Calls `generateTitleForFirstMessage` if first message
5. Invokes `stream.submit()` to start agent execution
6. Stream events trigger store updates via `handleCustomEvent`

**Sources:** [src/renderer/src/components/chat/ChatContainer.tsx:391-442]()

## Agent Streaming Integration

The chat interface integrates with LangGraph's streaming agent execution through `ElectronIPCTransport`.

### ElectronIPCTransport Bridge

```mermaid
graph LR
    subgraph "Renderer Side"
        useStream["useStream hook<br/>@langchain/langgraph-sdk/react"]
        Transport["ElectronIPCTransport<br/>Custom Transport"]
        ChatContainer["ChatContainer<br/>Component"]
    end
    
    subgraph "IPC Channel"
        AgentInvoke["agent:invoke<br/>Start stream"]
        AgentResume["agent:resume<br/>Resume after HITL"]
        AgentStop["agent:stop<br/>Cancel stream"]
    end
    
    subgraph "Main Process"
        Handler["Agent IPC Handler"]
        Runtime["Agent Runtime"]
    end
    
    ChatContainer --> useStream
    useStream --> Transport
    Transport --> AgentInvoke
    Transport --> AgentResume
    Transport --> AgentStop
    
    AgentInvoke --> Handler
    AgentResume --> Handler
    AgentStop --> Handler
    
    Handler --> Runtime
    Runtime -.->|Stream chunks| Handler
    Handler -.->|IPC events| Transport
    Transport -.->|Custom events| useStream
    useStream -.->|State updates| ChatContainer
    
    style Transport fill:#fff4e1
    style useStream fill:#e1f5ff
```

**Stream Event Processing:**

[src/renderer/src/components/chat/ChatContainer.tsx:165-178]() configures the stream hook:

```typescript
const stream = useStream<DeepAgent>({
  transport,
  threadId,
  messagesKey: 'messages',
  onCustomEvent: (data) => { handleCustomEvent(data) },
  onError: (error) => { setThreadError(threadId, errorMessage) }
})
```

[src/renderer/src/components/chat/ChatContainer.tsx:95-163]() processes custom events:

- `type: 'message'`: Append message to store
- `type: 'workspace'`: Update workspace files list
- `type: 'subagents'`: Update subagent status
- `type: 'interrupt'`: Trigger HITL approval dialog

**Sources:** [src/renderer/src/components/chat/ChatContainer.tsx:92-196]()

### Real-Time UI Updates

As the agent streams responses, the UI updates incrementally:

| Stream Event | UI Update | Store Action |
|--------------|-----------|--------------|
| Message chunk | Append to `stream.messages` | None (streaming state) |
| Tool call | Display in `MessageBubble` | None until stream completes |
| Values update (todos) | Update `ChatTodos` inline | `setTodos()` |
| Interrupt | Show approval dialog | `setPendingApproval()` |
| Stream complete | Persist to store | `appendMessage()` for each message |

[src/renderer/src/components/chat/ChatContainer.tsx:199-211]() syncs todos from stream values:

```typescript
const agentValues = stream.values as AgentStreamValues | undefined
const streamTodos = agentValues?.todos
useEffect(() => {
  if (Array.isArray(streamTodos)) {
    setTodos(streamTodos.map(t => ({ ... })))
  }
}, [streamTodos, setTodos])
```

**Display Messages Merging:**

[src/renderer/src/components/chat/ChatContainer.tsx:286-322]() combines store messages with streaming messages to provide a unified display:

1. Get IDs of messages already in store
2. Filter streaming messages to exclude duplicates
3. Map streaming message types to store message format
4. Return concatenated array: `[...storeMessages, ...streamingMsgs]`

**Sources:** [src/renderer/src/components/chat/ChatContainer.tsx:199-322]()

## Workspace Integration

The workspace system provides both UI display and agent file access. The UI components for workspace management are in `WorkspacePicker` and `FilesystemPanel`.

### WorkspacePicker Component

```mermaid
graph TB
    Picker["WorkspacePicker<br/>Popover Button"]
    
    Picker --> CheckWS{"workspacePath<br/>exists?"}
    CheckWS -->|No| SelectBtn["'Select workspace'<br/>Button (amber)"]
    CheckWS -->|Yes| ShowFolder["Show folder name<br/>+ 'Change Folder' button"]
    
    SelectBtn --> OpenDialog["window.api.workspace.select()"]
    ShowFolder --> OpenDialog
    
    OpenDialog --> SetPath["setWorkspacePath(path)"]
    OpenDialog --> LoadFiles["window.api.workspace.loadFromDisk()"]
    LoadFiles --> SetFiles["setWorkspaceFiles(files)"]
    
    style Picker fill:#e1f5ff
    style OpenDialog fill:#fff4e1
```

**Key Functions:**

[src/renderer/src/components/chat/WorkspacePicker.tsx:12-36]() exports `selectWorkspaceFolder`, a shared utility for workspace selection:

1. Call `window.api.workspace.select(threadId)` to open native folder dialog
2. Update store with `setWorkspacePath(path)`
3. Call `window.api.workspace.loadFromDisk(threadId)` to scan directory
4. Update store with `setWorkspaceFiles(result.files)`

[src/renderer/src/components/chat/WorkspacePicker.tsx:44-60]() loads workspace on thread switch:

```typescript
useEffect(() => {
  async function loadWorkspace() {
    if (currentThreadId) {
      const path = await window.api.workspace.get(currentThreadId)
      setWorkspacePath(path)
      if (path) {
        const result = await window.api.workspace.loadFromDisk(currentThreadId)
        if (result.success && result.files) {
          setWorkspaceFiles(result.files)
        }
      }
    }
  }
  loadWorkspace()
}, [currentThreadId, setWorkspacePath, setWorkspaceFiles])
```

**Workspace Requirement:**

[src/renderer/src/components/chat/ChatContainer.tsx:395-399]() blocks message submission without a workspace:

```typescript
if (!workspacePath) {
  setThreadError(threadId, 'Please select a workspace folder before sending messages.')
  return
}
```

**Sources:** [src/renderer/src/components/chat/WorkspacePicker.tsx:1-136](), [src/renderer/src/components/chat/ChatContainer.tsx:395-399]()

## Task Display and Progress Tracking

The `TodoPanel` displays agent-generated tasks with status indicators and progress tracking.

### Todo Status Visualization

```mermaid
graph LR
    subgraph "Todo Sources"
        StreamValues["stream.values.todos<br/>Real-time from agent"]
        StoreState["useAppStore().todos<br/>Persisted state"]
    end
    
    subgraph "TodoPanel Display"
        Progress["Progress Bar<br/>done / total"]
        Collapsed["Completed Section<br/>(collapsible)"]
        InProgress["In Progress Items"]
        Pending["Pending Items"]
    end
    
    StreamValues --> StoreState
    StoreState --> Progress
    StoreState --> Collapsed
    StoreState --> InProgress
    StoreState --> Pending
    
    style StreamValues fill:#ffe1e1
    style TodoPanel fill:#e1f5ff
```

**Status Configuration:**

[src/renderer/src/components/panels/TodoPanel.tsx:9-34]() defines status metadata:

| Status | Icon | Badge Color | Label |
|--------|------|-------------|-------|
| `pending` | Circle | outline | PENDING |
| `in_progress` | Clock | info | IN PROGRESS |
| `completed` | CheckCircle2 | nominal | DONE |
| `cancelled` | XCircle | critical | CANCELLED |

**Grouping Logic:**

[src/renderer/src/components/panels/TodoPanel.tsx:40-47]() groups todos by status:

```typescript
const inProgress = todos.filter((t) => t.status === 'in_progress')
const pending = todos.filter((t) => t.status === 'pending')
const completed = todos.filter((t) => t.status === 'completed')
const cancelled = todos.filter((t) => t.status === 'cancelled')
const doneItems = [...completed, ...cancelled]
```

Display order: Completed (collapsible) → In Progress → Pending

**Progress Calculation:**

[src/renderer/src/components/panels/TodoPanel.tsx:49-52]() computes progress percentage:

```typescript
const total = todos.length
const done = completed.length
const progress = total > 0 ? Math.round((done / total) * 100) : 0
```

**Sources:** [src/renderer/src/components/panels/TodoPanel.tsx:1-161]()

## Auto-Scrolling and Viewport Management

The chat container implements intelligent auto-scrolling that preserves user scroll position while still scrolling for new messages when appropriate.

### Scroll Behavior Logic

```mermaid
graph TD
    NewMessage["New Message<br/>or Stream Update"]
    
    NewMessage --> CheckBottom{"isAtBottomRef<br/>= true?"}
    CheckBottom -->|Yes| AutoScroll["Scroll viewport<br/>to bottom"]
    CheckBottom -->|No| Preserve["Preserve current<br/>scroll position"]
    
    UserScroll["User Scrolls"] --> UpdateRef["Update isAtBottomRef<br/>based on position"]
    
    ThreadSwitch["Thread Switch"] --> ForceScroll["Force scroll to bottom<br/>Set isAtBottomRef = true"]
    
    style NewMessage fill:#e1f5ff
    style CheckBottom fill:#fff4e1
```

**Implementation Details:**

[src/renderer/src/components/chat/ChatContainer.tsx:339-354]() tracks scroll position:

```typescript
const handleScroll = useCallback(() => {
  const viewport = getViewport()
  if (!viewport) return
  
  const { scrollTop, scrollHeight, clientHeight } = viewport
  const threshold = 50  // Consider "at bottom" if within 50px
  isAtBottomRef.current = scrollHeight - scrollTop - clientHeight < threshold
}, [getViewport])
```

[src/renderer/src/components/chat/ChatContainer.tsx:366-371]() implements conditional auto-scroll:

```typescript
useEffect(() => {
  const viewport = getViewport()
  if (viewport && isAtBottomRef.current) {
    viewport.scrollTop = viewport.scrollHeight
  }
}, [displayMessages, stream.isLoading, getViewport])
```

[src/renderer/src/components/chat/ChatContainer.tsx:374-380]() forces scroll on thread switch:

```typescript
useEffect(() => {
  const viewport = getViewport()
  if (viewport) {
    viewport.scrollTop = viewport.scrollHeight
    isAtBottomRef.current = true
  }
}, [threadId, getViewport])
```

**Radix ScrollArea Integration:**

The component uses Radix UI's `ScrollArea` which wraps the content in a viewport. [src/renderer/src/components/chat/ChatContainer.tsx:339-343]() queries the actual viewport element:

```typescript
const getViewport = useCallback(() => {
  return scrollRef.current?.querySelector(
    '[data-radix-scroll-area-viewport]'
  ) as HTMLDivElement | null
}, [])
```

**Sources:** [src/renderer/src/components/chat/ChatContainer.tsx:339-380]()

## Error Handling and Display

The UI displays errors at two levels: thread-specific errors and global errors.

### Thread-Specific Error Display

```mermaid
graph TB
    Sources["Error Sources"]
    Sources --> StreamError["stream.error<br/>useStream hook"]
    Sources --> CustomError["Manual<br/>setThreadError() calls"]
    
    StreamError --> Store["errorByThread[threadId]<br/>In useAppStore"]
    CustomError --> Store
    
    Store --> Display["Error Banner<br/>in ChatContainer"]
    
    Display --> Content["AlertCircle icon<br/>Error message<br/>Dismiss button"]
    
    User["User Action"] --> Dismiss["clearThreadError(threadId)"]
    Dismiss --> Store
    
    style Store fill:#f0e1ff
    style Display fill:#ffe1e1
```

**Error Tracking:**

[src/renderer/src/components/chat/ChatContainer.tsx:222-243]() syncs stream errors to the store:

```typescript
const lastErrorRef = useRef<unknown>(null)

useEffect(() => {
  const isNewError = stream.error && stream.error !== lastErrorRef.current
  
  if (isNewError) {
    lastErrorRef.current = stream.error
    const errorMessage = stream.error instanceof Error 
      ? stream.error.message 
      : String(stream.error)
    setThreadError(threadId, errorMessage)
  } else if (!stream.error) {
    lastErrorRef.current = null
  }
}, [stream.error, threadId, setThreadError])
```

The `lastErrorRef` prevents stale errors from being synced when switching threads.

**Error Display:**

[src/renderer/src/components/chat/ChatContainer.tsx:526-546]() renders error banner:

- Only displays when `threadError` exists and `!stream.isLoading`
- Shows AlertCircle icon, error message, and dismiss button
- Positioned below messages, above input
- Red/destructive color scheme

**Sources:** [src/renderer/src/components/chat/ChatContainer.tsx:86-88](), [src/renderer/src/components/chat/ChatContainer.tsx:222-243](), [src/renderer/src/components/chat/ChatContainer.tsx:526-546]()

## Styling and Theming

OpenWork uses Tailwind CSS with a custom design system defined in theme configuration.

### Theme Architecture

The application uses CSS custom properties for theming, defined in `src/renderer/src/index.css`. Key color tokens include:

- **Backgrounds**: `--background`, `--background-secondary`, `--sidebar`
- **Borders**: `--border`, `--border-strong`
- **Text**: `--foreground`, `--muted-foreground`
- **Status**: `--status-nominal`, `--status-info`, `--status-critical`
- **Interactive**: `--accent`, `--ring`

### Spacing and Typography

The design system uses consistent spacing and typography conventions:

| Class | Usage | Example |
|-------|-------|---------|
| `.text-section-header` | Section labels | "PROGRESS", "TASKS" |
| `.text-data` | Data values | Counters, timestamps |
| `.app-drag-region` | Draggable titlebar | Enables window dragging |
| `.app-badge` | Fixed app badge | "OPENWORK v0.1.0" |

### Component-Specific Styling

**Message Bubbles**: Use role-based styling (user messages align right with blue background, assistant messages align left with gray background)

**Status Indicators**: Use semantic color coding (nominal/green for success, critical/red for errors, info/blue for in-progress)

**Panels**: Consistent border-t/border-b separators, ScrollArea for overflow, padding-4 for content

**Sources:** [src/renderer/src/App.tsx:122-136]()

---

