<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/deep-agents-ui · page 4 Chat System · fetched 2026-10-26 -->

# Chat System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/components/ChatInterface.tsx](src/app/components/ChatInterface.tsx)
- [src/app/components/ChatMessage.tsx](src/app/components/ChatMessage.tsx)
- [src/app/hooks/useChat.ts](src/app/hooks/useChat.ts)
- [src/app/hooks/useThreads.ts](src/app/hooks/useThreads.ts)
- [src/app/utils/utils.ts](src/app/utils/utils.ts)

</details>



## Purpose and Scope

The Chat System is the core functionality layer of Deep Agents UI responsible for managing real-time communication between users and LangGraph agents. It handles message submission, streaming responses, tool execution visualization, and state synchronization including tasks and files.

This document covers the overall chat architecture, message flow, and state management. For details on specific components, see:
- **ChatInterface UI component and input handling**: [ChatInterface Component](#4.1)
- **useChat hook internals and streaming**: [useChat Hook](#4.2)
- **Message rendering and tool call display**: [Message Processing and Display](#4.3)

For information about the context providers that wrap the chat system, see [Configuration and Connection](#2) and [System Architecture](#1.2). For tool approval mechanisms, see [Tool Approval and Interrupts](#5.2).

---

## System Architecture

The Chat System is organized into three primary layers: the `useChat` hook for state management and API communication, the `ChatProvider` context for sharing chat state across components, and the `ChatInterface` component for user interaction and display.

### Component and Hook Structure

```mermaid
graph TB
    ChatProvider["ChatProvider<br/>(providers/ChatProvider)"]
    useChat["useChat hook<br/>(app/hooks/useChat.ts)"]
    useStream["useStream<br/>(@langchain/langgraph-sdk/react)"]
    ChatInterface["ChatInterface<br/>(app/components/ChatInterface.tsx)"]
    ChatMessage["ChatMessage<br/>(app/components/ChatMessage.tsx)"]
    
    subgraph "Context Layer"
        ChatProvider
    end
    
    subgraph "Hook Layer"
        useChat
        useStream
    end
    
    subgraph "UI Layer"
        ChatInterface
        ChatMessage
    end
    
    ChatProvider -->|"provides context"| ChatInterface
    ChatProvider -->|"uses"| useChat
    useChat -->|"wraps"| useStream
    ChatInterface -->|"renders list of"| ChatMessage
    useStream -->|"manages WebSocket<br/>to LangGraph API"| LangGraphAPI["LangGraph<br/>Stream API"]
    
    useChat -->|"exposes"| ChatState["Chat State:<br/>messages, todos,<br/>files, interrupt"]
    useChat -->|"exposes"| ChatActions["Chat Actions:<br/>sendMessage,<br/>continueStream,<br/>resumeInterrupt"]
    
    ChatInterface -->|"calls"| ChatActions
    ChatInterface -->|"renders"| ChatState
```

**Sources:** [src/app/hooks/useChat.ts:1-168](), [src/app/components/ChatInterface.tsx:1-546]()

---

## Data Flow Architecture

The following diagram shows how user actions flow through the chat system, including the key functions and state transformations at each stage.

```mermaid
sequenceDiagram
    participant User
    participant ChatInterface
    participant sendMessage
    participant useStream
    participant LangGraphAPI
    participant StreamProcessor
    participant UIUpdate
    
    User->>ChatInterface: "Types message + submits"
    ChatInterface->>sendMessage: "handleSubmit() → sendMessage(content)"
    
    Note over sendMessage: "useChat.ts:56-72<br/>Creates Message object<br/>with uuid"
    
    sendMessage->>sendMessage: "Create newMessage<br/>{id: uuidv4(), type: 'human', content}"
    sendMessage->>useStream: "stream.submit({messages: [newMessage]},<br/>{optimisticValues, config})"
    
    Note over useStream: "Optimistic update:<br/>adds message to UI<br/>immediately"
    
    useStream->>UIUpdate: "Update messages array"
    UIUpdate->>ChatInterface: "Re-render with new message"
    
    useStream->>LangGraphAPI: "POST /threads/{threadId}/input"
    
    loop "Streaming Response"
        LangGraphAPI-->>StreamProcessor: "Stream chunks<br/>(messages, todos, files)"
        StreamProcessor-->>useStream: "Update stream.values"
        useStream-->>ChatInterface: "Re-render with updates"
    end
    
    alt "Agent completes normally"
        LangGraphAPI-->>useStream: "Stream end"
        useStream->>useStream: "onFinish() → onHistoryRevalidate()"
    else "Tool requires approval"
        LangGraphAPI-->>useStream: "Interrupt signal"
        useStream->>ChatInterface: "stream.interrupt populated"
        ChatInterface->>User: "Show ToolApprovalInterrupt UI"
        User->>ChatInterface: "Approve/Reject/Edit"
        ChatInterface->>useStream: "resumeInterrupt(decision)"
    end
```

**Sources:** [src/app/hooks/useChat.ts:56-72](), [src/app/components/ChatInterface.tsx:89-100]()

---

## State Management

The Chat System manages multiple types of state through the `useChat` hook, which wraps the LangGraph SDK's `useStream` hook.

### State Type Definition

The primary state interface is `StateType`, defined in [src/app/hooks/useChat.ts:16-26]():

| Field | Type | Description |
|-------|------|-------------|
| `messages` | `Message[]` | Array of chat messages (human, ai, tool) |
| `todos` | `TodoItem[]` | Task list tracked by agent |
| `files` | `Record<string, string>` | File content keyed by path |
| `email` | `object` (optional) | Email context with id, subject, page_content |
| `ui` | `any` (optional) | Custom UI components from agent |

### State Initialization

```mermaid
graph LR
    URLParams["URL Query Parameter<br/>threadId"]
    useStream["useStream hook<br/>initialization"]
    ThreadHistory["Fetch Thread History<br/>fetchStateHistory: true"]
    InitialState["Initial State<br/>messages, todos, files"]
    
    URLParams -->|"threadId ?? null"| useStream
    useStream -->|"if threadId exists"| ThreadHistory
    ThreadHistory --> InitialState
    
    useStream -->|"onThreadId callback"| setThreadId["setThreadId<br/>(updates URL)"]
    
    Note1["useChat.ts:37-54<br/>Configuration"]
    Note2["reconnectOnMount: true<br/>enables reconnection<br/>to existing threads"]
```

The `useChat` hook initializes with configuration from [src/app/hooks/useChat.ts:40-54]():

- **assistantId**: From `activeAssistant.assistant_id` [src/app/hooks/useChat.ts:41]()
- **client**: LangGraph SDK client instance [src/app/hooks/useChat.ts:42]()
- **reconnectOnMount**: `true` - reconnects to WebSocket on component mount [src/app/hooks/useChat.ts:43]()
- **threadId**: From URL query parameter via `nuqs` [src/app/hooks/useChat.ts:37, 44]()
- **onThreadId**: Callback to update URL when thread changes [src/app/hooks/useChat.ts:45]()
- **fetchStateHistory**: `true` - fetches existing messages when switching threads [src/app/hooks/useChat.ts:48]()
- **defaultHeaders**: `{ "x-auth-scheme": "langsmith" }` [src/app/hooks/useChat.ts:46]()

**Sources:** [src/app/hooks/useChat.ts:16-54]()

---

## Message Submission Flow

### sendMessage Function

The `sendMessage` function handles user message submission with optimistic updates:

```mermaid
graph TB
    Input["User Input<br/>(string content)"]
    CreateMsg["Create Message Object<br/>{id: uuidv4(),<br/>type: 'human',<br/>content}"]
    Optimistic["Optimistic Update<br/>optimisticValues: (prev) => ({<br/>messages: [...prev.messages, newMessage]})"]
    Submit["stream.submit()<br/>with messages + config"]
    Revalidate["onHistoryRevalidate()<br/>(update thread list)"]
    
    Input --> CreateMsg
    CreateMsg --> Optimistic
    CreateMsg --> Submit
    Submit --> Revalidate
    
    Config["Assistant Config<br/>+ recursion_limit: 100"]
    Config --> Submit
    
    Note["useChat.ts:56-72"]
```

**Implementation details:**

1. **Message Creation** [src/app/hooks/useChat.ts:58](): Creates a new `Message` object with UUID, type "human", and user content
2. **Optimistic Update** [src/app/hooks/useChat.ts:62-64](): Immediately adds message to UI before server response
3. **Submit to Stream** [src/app/hooks/useChat.ts:59-67](): Sends message with assistant config and recursion limit of 100
4. **Thread List Update** [src/app/hooks/useChat.ts:69](): Triggers revalidation to update thread list sidebar

**Sources:** [src/app/hooks/useChat.ts:56-72]()

---

## Stream Control Functions

The `useChat` hook exposes several functions for controlling the agent execution stream:

### Function Reference

| Function | Parameters | Purpose | Location |
|----------|-----------|---------|----------|
| `sendMessage` | `content: string` | Submit user message | [src/app/hooks/useChat.ts:56-72]() |
| `runSingleStep` | `messages, checkpoint?, isRerunningSubagent?, optimisticMessages?` | Execute single step with interrupt | [src/app/hooks/useChat.ts:74-100]() |
| `continueStream` | `hasTaskToolCall?: boolean` | Resume agent execution | [src/app/hooks/useChat.ts:112-127]() |
| `stopStream` | none | Stop streaming execution | [src/app/hooks/useChat.ts:144-146]() |
| `resumeInterrupt` | `value: any` | Resume from human approval interrupt | [src/app/hooks/useChat.ts:135-142]() |
| `markCurrentThreadAsResolved` | none | Mark thread complete and goto `__end__` | [src/app/hooks/useChat.ts:129-133]() |
| `setFiles` | `files: Record<string, string>` | Update file state | [src/app/hooks/useChat.ts:102-110]() |

### runSingleStep Configuration

The `runSingleStep` function [src/app/hooks/useChat.ts:74-100]() supports stepping through agent execution with interrupts:

```mermaid
graph TB
    runSingleStep["runSingleStep()"]
    
    HasCheckpoint{{"checkpoint<br/>provided?"}}
    IsRerunning{{"isRerunningSubagent<br/>flag?"}}
    
    runSingleStep --> HasCheckpoint
    
    HasCheckpoint -->|"Yes"| WithCheckpoint["stream.submit(undefined,<br/>{config, checkpoint})"]
    HasCheckpoint -->|"No"| WithoutCheckpoint["stream.submit({messages},<br/>{config})"]
    
    WithCheckpoint --> IsRerunning
    IsRerunning -->|"Yes"| InterruptAfter["interruptAfter: ['tools']"]
    IsRerunning -->|"No"| InterruptBefore["interruptBefore: ['tools']"]
    
    WithoutCheckpoint --> InterruptBefore2["interruptBefore: ['tools']"]
    
    Note1["Used for:<br/>- Step-by-step debugging<br/>- Sub-agent re-execution<br/>- Tool approval flow"]
```

**Sources:** [src/app/hooks/useChat.ts:74-100]()

---

## Message Processing

The `ChatInterface` component processes messages from the stream into a renderable format with tool calls attached.

### Message-to-ToolCall Association

```mermaid
graph TB
    Messages["messages array<br/>(from useStream)"]
    ProcessLoop["useMemo() loop<br/>ChatInterface.tsx:114-216"]
    MessageMap["Map<string, {message, toolCalls}>"]
    
    Messages --> ProcessLoop
    
    subgraph "Processing Steps"
        AIMsg["AI Message:<br/>Extract tool_calls from<br/>additional_kwargs or<br/>message.tool_calls"]
        ToolMsg["Tool Message:<br/>Find matching tool_call<br/>by tool_call_id"]
        HumanMsg["Human Message:<br/>Add with empty toolCalls"]
        
        ProcessLoop --> AIMsg
        ProcessLoop --> ToolMsg
        ProcessLoop --> HumanMsg
    end
    
    AIMsg --> AddToMap["Add to Map with<br/>status: 'pending'"]
    ToolMsg --> UpdateMap["Update existing tool<br/>status: 'completed'<br/>add result"]
    HumanMsg --> AddToMap
    
    AddToMap --> MessageMap
    UpdateMap --> MessageMap
    
    MessageMap --> ProcessedArray["Array of<br/>{message, toolCalls, showAvatar}"]
    ProcessedArray --> Render["Render ChatMessage<br/>components"]
```

**Implementation details** [src/app/components/ChatInterface.tsx:114-216]():

1. **Create Message Map**: Initialize `Map<string, {message, toolCalls}>` to associate tool calls with AI messages.
2. **Process AI Messages**: Extract tool calls from `additional_kwargs.tool_calls` [src/app/components/ChatInterface.tsx:135](), `message.tool_calls` [src/app/components/ChatInterface.tsx:139](), or content blocks with type `"tool_use"` [src/app/components/ChatInterface.tsx:146]().
3. **Handle Tool Messages**: Find matching tool call by `tool_call_id` [src/app/components/ChatInterface.tsx:183]() and update status to "completed" with result extracted via `extractStringFromMessageContent` [src/app/components/ChatInterface.tsx:197]().
4. **Determine Avatar Display**: Compare current message type with previous to decide whether to show avatar [src/app/components/ChatInterface.tsx:213]().
5. **Return Processed Array**: Convert map to array with tool call associations preserved.

**Sources:** [src/app/components/ChatInterface.tsx:114-216](), [src/app/utils/utils.ts:9-31]()

---

## Interrupt Handling

The Chat System supports human-in-the-loop interrupts for tool approval. When an agent requests approval, the `interrupt` state is populated with `action_requests` and optional `review_configs`.

### Interrupt State Structure

```mermaid
graph LR
    Interrupt["stream.interrupt"]
    
    ActionRequests["action_requests array<br/>List of tools awaiting approval"]
    ReviewConfigs["review_configs array<br/>(optional)<br/>Approval UI configuration"]
    
    Interrupt --> ActionRequests
    Interrupt --> ReviewConfigs
    
    ActionRequestsMap["Map<string, ActionRequest><br/>Keyed by tool name"]
    ReviewConfigsMap["Map<string, ReviewConfig><br/>Keyed by actionName"]
    
    ActionRequests --> ActionRequestsMap
    ReviewConfigs --> ReviewConfigsMap
    
    PassToMessage["Pass to ChatMessage<br/>for last message only"]
    
    ActionRequestsMap --> PassToMessage
    ReviewConfigsMap --> PassToMessage
```

The interrupt parsing logic [src/app/components/ChatInterface.tsx:228-242]():

1. Extract `action_requests` from `interrupt.value` [src/app/components/ChatInterface.tsx:229-230]().
2. Extract `review_configs` (if present) from `interrupt.value` [src/app/components/ChatInterface.tsx:234-235]().
3. Create maps keyed by tool name / action name for efficient lookup.
4. Pass maps only to the last message for rendering approval UI.

**Sources:** [src/app/components/ChatInterface.tsx:228-242]()

---

## Tasks and Files UI

The `ChatInterface` includes an embedded UI section above the input box for displaying tasks and files.

### UI State Management

```mermaid
graph TB
    MetaState["metaOpen state<br/>'tasks' | 'files' | null"]
    
    Collapsed["Collapsed View<br/>(metaOpen === null)"]
    Expanded["Expanded View<br/>(metaOpen !== null)"]
    
    MetaState --> Collapsed
    MetaState --> Expanded
    
    subgraph "Collapsed Display"
        ActiveTask["Show active task<br/>(status: 'in_progress')"]
        TaskProgress["Task X of Y"]
        FilesCount["Files count badge"]
    end
    
    subgraph "Expanded Display"
        TabButtons["Tab buttons:<br/>Tasks | Files"]
        TaskGroups["Grouped todos by status:<br/>pending, in_progress, completed"]
        FilesPopover["FilesPopover component<br/>with edit capability"]
    end
    
    Collapsed --> ActiveTask
    Collapsed --> TaskProgress
    Collapsed --> FilesCount
    
    Expanded --> TabButtons
    Expanded --> TaskGroups
    Expanded --> FilesPopover
```

**Key features** [src/app/components/ChatInterface.tsx:296-501]():

- **Conditional Rendering**: Only shows when `hasTasks || hasFiles` is true.
- **Collapsed State**: Displays single-line summary of active task and file count.
- **Expanded State**: Shows full task list grouped by status or file list with editing via `FilesPopover` [src/app/components/ChatInterface.tsx:456]().
- **Max Height**: `max-h-72` with scroll for long lists [src/app/components/ChatInterface.tsx:327]().
- **Edit Locking**: File editing disabled when `isLoading === true || interrupt !== undefined` [src/app/components/ChatInterface.tsx:459]().

**Sources:** [src/app/components/ChatInterface.tsx:296-501]()

---

## Input Handling

The message input uses a `<textarea>` with auto-resizing via CSS `field-sizing-content` property.

### Input Component Structure

```mermaid
graph TB
    Textarea["textarea element<br/>field-sizing-content<br/>resize-none"]
    InputState["input state<br/>(local component state)"]
    
    subgraph "Event Handlers"
        OnChange["onChange:<br/>setInput(e.target.value)"]
        OnKeyDown["onKeyDown:<br/>Enter submits (if !Shift)"]
        OnSubmit["form onSubmit:<br/>handleSubmit()"]
    end
    
    Textarea --> OnChange
    Textarea --> OnKeyDown
    
    OnChange --> InputState
    OnKeyDown --> HandleSubmit["handleSubmit()<br/>useCallback"]
    OnSubmit --> HandleSubmit
    
    HandleSubmit --> Validation{{"Validation:<br/>!messageText.trim() ||<br/>isLoading ||<br/>submitDisabled"}}
    
    Validation -->|"Valid"| SendMsg["sendMessage(messageText)<br/>setInput('')"]
    Validation -->|"Invalid"| Return["return (no-op)"]
    
    SendMsg --> StreamAPI["Submit to stream"]
```

**Implementation details** [src/app/components/ChatInterface.tsx:503-539]():

- **Auto-resize**: CSS property `field-sizing-content` enables automatic height adjustment based on content [src/app/components/ChatInterface.tsx:511]().
- **Enter Key**: Submits message; Shift+Enter adds newline [src/app/components/ChatInterface.tsx:105-108]().
- **Submit Button**: Toggles between "Send" (with `ArrowUp` icon) and "Stop" (with `Square` icon) based on `isLoading` state [src/app/components/ChatInterface.tsx:526-533]().
- **Disabled State**: Submit disabled when `!isLoading && (submitDisabled || !input.trim())` [src/app/components/ChatInterface.tsx:524]().
- **Placeholder**: Changes to "Running..." when `isLoading === true` [src/app/components/ChatInterface.tsx:516]().

**Sources:** [src/app/components/ChatInterface.tsx:89-111, 503-539]()

---

## Exposed API

The `useChat` hook returns an object with the following properties and methods:

### Return Value Structure

```typescript
{
  // Stream management
  stream: UseStreamThread<StateType>
  
  // State values (from stream.values)
  todos: TodoItem[]
  files: Record<string, string>
  email?: { id?: string; subject?: string; page_content?: string }
  ui?: any
  
  // Message management
  messages: Message[]
  isLoading: boolean
  isThreadLoading: boolean
  interrupt: Interrupt | undefined
  getMessagesMetadata: () => MessagesMetadata
  
  // Actions
  sendMessage: (content: string) => void
  runSingleStep: (messages, checkpoint?, isRerunningSubagent?, optimisticMessages?) => void
  continueStream: (hasTaskToolCall?: boolean) => void
  stopStream: () => void
  markCurrentThreadAsResolved: () => void
  resumeInterrupt: (value: any) => void
  setFiles: (files: Record<string, string>) => Promise<void>
}
```

**Sources:** [src/app/hooks/useChat.ts:148-167]()

---

## Integration with ChatProvider

The `useChat` hook is consumed by `ChatProvider` context, which makes the chat state and actions available to all descendant components via the `useChatContext()` hook.

```mermaid
graph TB
    CP["ChatProvider<br/>(context provider)"]
    useChat["useChat hook"]
    Context["Chat Context Value"]
    
    CI["ChatInterface"]
    CM["ChatMessage"]
    TFS["TasksFilesSidebar"]
    OtherComponents["Other Components"]
    
    CP -->|"calls"| useChat
    useChat -->|"returns"| Context
    CP -->|"provides via context"| Context
    
    Context -->|"useChatContext()"| CI
    Context -->|"useChatContext()"| CM
    Context -->|"useChatContext()"| TFS
    Context -->|"useChatContext()"| OtherComponents
    
    Note["ChatInterface.tsx:72-85<br/>Destructures from useChatContext():<br/>stream, messages, todos, files,<br/>ui, setFiles, isLoading,<br/>isThreadLoading, interrupt,<br/>sendMessage, stopStream,<br/>resumeInterrupt"]
```

**Sources:** [src/app/components/ChatInterface.tsx:72-85]()

---

