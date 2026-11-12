<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/agent-chat-ui · page 8 State Management · fetched 2026-10-26 -->

# State Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/page.tsx](src/app/page.tsx)
- [src/components/thread/artifact.tsx](src/components/thread/artifact.tsx)
- [src/components/thread/index.tsx](src/components/thread/index.tsx)
- [src/providers/Stream.tsx](src/providers/Stream.tsx)

</details>



This document explains the state management architecture of the agent-chat-ui application. The system employs a layered approach with distinct state management mechanisms for different concerns: URL query parameters for navigation and persistence, React Context providers for global application state, and local component state for ephemeral UI interactions.

For detailed information about individual provider implementations, see [Stream Provider](#2.2), [Thread Provider](#2.3), and [Artifact System](#2.4). For overall architectural context, see [Core Architecture](#2).

## State Management Layers

The application uses four distinct layers of state management, each with specific responsibilities and scopes:

```mermaid
graph TB
    subgraph URLLayer["URL State Layer (nuqs)"]
        ThreadID["threadId<br/>Current thread"]
        ChatHistory["chatHistoryOpen<br/>Sidebar visibility"]
        ToolVis["hideToolCalls<br/>Display preference"]
        APIURL["apiUrl<br/>Server endpoint"]
        AssistID["assistantId<br/>Graph ID"]
    end
    
    subgraph ProviderLayer["Provider Context Layer"]
        StreamProv["StreamProvider<br/>Streaming & messages"]
        ThreadProv["ThreadProvider<br/>Thread list"]
        ArtifactProv["ArtifactProvider<br/>Side panel"]
    end
    
    subgraph LocalLayer["Local Component State"]
        InputState["input<br/>Text input value"]
        FileState["contentBlocks<br/>Uploaded files"]
        EditState["isEditing<br/>Message edit mode"]
        UIState["dragOver<br/>Drag feedback"]
    end
    
    subgraph ComponentLayer["Component Tree"]
        Thread["Thread Component"]
        Messages["Message Components"]
        History["ThreadHistory"]
    end
    
    URLLayer --> Thread
    ProviderLayer --> Thread
    Thread --> LocalLayer
    Thread --> Messages
    Thread --> History
    
    StreamProv -.-> Messages
    ThreadProv -.-> History
    ArtifactProv -.-> Messages
```

**Sources**: [src/components/thread/index.tsx:1-565](), [src/providers/Stream.tsx:1-287](), [src/components/thread/artifact.tsx:1-190](), [src/app/page.tsx:1-24]()

## URL State Management

The application uses the `nuqs` library to manage state in URL query parameters, providing persistent, shareable state that survives page refreshes and enables deep linking.

### Managed Parameters

| Parameter | Type | Default | Purpose | Component |
|-----------|------|---------|---------|-----------|
| `threadId` | string \| null | null | Current conversation thread | Thread |
| `chatHistoryOpen` | boolean | false | Sidebar visibility state | Thread |
| `hideToolCalls` | boolean | false | Tool call display toggle | Thread |
| `apiUrl` | string | env var | LangGraph server URL | StreamProvider |
| `assistantId` | string | env var | Graph/assistant identifier | StreamProvider |

### Implementation Pattern

URL state is managed using `useQueryState` hook from nuqs:

```mermaid
graph LR
    Component["Component"]
    Hook["useQueryState()"]
    URLBar["Browser URL"]
    Parser["parseAsBoolean"]
    
    Component -->|"Read"| Hook
    Hook -->|"Parse"| Parser
    Parser -->|"Value"| Component
    Component -->|"Update"| Hook
    Hook -->|"Sync"| URLBar
```

**Example usage from Thread component** [src/components/thread/index.tsx:118-126]():
```typescript
const [threadId, _setThreadId] = useQueryState("threadId");
const [chatHistoryOpen, setChatHistoryOpen] = useQueryState(
  "chatHistoryOpen",
  parseAsBoolean.withDefault(false),
);
const [hideToolCalls, setHideToolCalls] = useQueryState(
  "hideToolCalls",
  parseAsBoolean.withDefault(false),
);
```

### Thread ID Management

The Thread component wraps the `setThreadId` function to perform cleanup operations when switching threads [src/components/thread/index.tsx:147-153]():

```mermaid
graph TD
    SetThread["setThreadId(id)"]
    UpdateURL["_setThreadId(id)"]
    CloseArtifact["closeArtifact()"]
    ResetContext["setArtifactContext({})"]
    
    SetThread --> UpdateURL
    SetThread --> CloseArtifact
    SetThread --> ResetContext
```

This ensures the artifact panel is closed and artifact context is cleared when navigating between threads.

**Sources**: [src/components/thread/index.tsx:118-153]()

## Provider Context Architecture

The application uses three React Context providers, nested in a specific order to establish dependency relationships:

```mermaid
graph TD
    App["Application Root"]
    ThreadProv["ThreadProvider<br/>Thread list management"]
    StreamProv["StreamProvider<br/>Streaming & messages"]
    ArtifactProv["ArtifactProvider<br/>Side panel content"]
    ThreadComp["Thread Component"]
    
    App --> ThreadProv
    ThreadProv --> StreamProv
    StreamProv --> ArtifactProv
    ArtifactProv --> ThreadComp
    
    ThreadProv -.->|"threads[]<br/>getThreads()<br/>threadsLoading"| ThreadComp
    StreamProv -.->|"messages[]<br/>submit()<br/>stop()<br/>isLoading"| ThreadComp
    ArtifactProv -.->|"artifactOpen<br/>artifactContext<br/>refs"| ThreadComp
```

**Provider nesting order** [src/app/page.tsx:10-23]():
```typescript
<ThreadProvider>
  <StreamProvider>
    <ArtifactProvider>
      <Thread />
    </ArtifactProvider>
  </StreamProvider>
</ThreadProvider>
```

**Sources**: [src/app/page.tsx:10-23]()

### StreamProvider State

The StreamProvider manages the most critical application state related to LangGraph streaming connections. It uses the `useStream` hook from `@langchain/langgraph-sdk/react` with custom type parameters.

**Type definition** [src/providers/Stream.tsx:28-40]():

```mermaid
graph TB
    StateType["StateType<br/>{messages, ui}"]
    UpdateType["UpdateType<br/>{messages, ui, context}"]
    CustomEventType["CustomEventType<br/>UIMessage | RemoveUIMessage"]
    
    UseTypedStream["useTypedStream<br/>useStream&lt;StateType, ...&gt;"]
    
    StateType -.-> UseTypedStream
    UpdateType -.-> UseTypedStream
    CustomEventType -.-> UseTypedStream
    
    ReturnValue["StreamContextType<br/>messages[], ui[], isLoading<br/>submit(), stop(), error"]
    
    UseTypedStream --> ReturnValue
```

Key state elements exposed by StreamProvider:
- `messages: Message[]` - LangGraph message history
- `ui: UIMessage[]` - UI-specific messages processed by `uiMessageReducer`
- `isLoading: boolean` - Stream activity indicator
- `error: unknown` - Stream error state
- `submit(input, options)` - Initiate stream with input
- `stop()` - Cancel active stream
- `interrupt` - Current agent interrupt state

**Sources**: [src/providers/Stream.tsx:28-43](), [src/providers/Stream.tsx:69-127]()

### ThreadProvider State

The ThreadProvider manages the list of conversation threads, enabling the thread history sidebar functionality. While not included in the provided files, it exposes:
- `threads: Thread[]` - List of available threads
- `getThreads()` - Fetch thread list from server
- `setThreads(threads)` - Update thread list state
- `threadsLoading: boolean` - Loading indicator

The StreamProvider integrates with ThreadProvider to refresh the thread list when new threads are created [src/providers/Stream.tsx:96-101]().

**Sources**: [src/providers/Stream.tsx:81](), [src/providers/Stream.tsx:96-101]()

### ArtifactProvider State

The ArtifactProvider uses React Portals to render artifact content in a side panel. Its state structure uses tuples of `[value, setter]`:

```mermaid
graph TB
    ArtifactCtx["ArtifactSlotContext"]
    
    OpenState["open: [string | null, Setter]<br/>Active artifact ID"]
    MountedState["mounted: [string | null, Setter]<br/>Mounted artifact ID"]
    TitleRef["title: [HTMLElement | null, Setter]<br/>Title container ref"]
    ContentRef["content: [HTMLElement | null, Setter]<br/>Content container ref"]
    ContextState["context: [Record&lt;string, unknown&gt;, Setter]<br/>Artifact context data"]
    
    ArtifactCtx --> OpenState
    ArtifactCtx --> MountedState
    ArtifactCtx --> TitleRef
    ArtifactCtx --> ContentRef
    ArtifactCtx --> ContextState
```

**Context definition** [src/components/thread/artifact.tsx:17-25]():

The provider maintains refs to DOM elements where artifact title and content should be rendered, enabling flexible portal-based rendering from any component in the tree.

**Sources**: [src/components/thread/artifact.tsx:17-25](), [src/components/thread/artifact.tsx:98-113]()

## Local Component State

Local component state is used for ephemeral UI concerns that don't need to be shared across the application or persisted. The Thread component manages several pieces of local state:

### Input and File Upload State

```mermaid
graph TB
    InputState["input<br/>useState('')<br/>Text input value"]
    FileState["useFileUpload()<br/>Custom hook"]
    
    FileState --> ContentBlocks["contentBlocks: Base64ContentBlock[]"]
    FileState --> DragOver["dragOver: boolean"]
    FileState --> Handlers["handleFileUpload()<br/>handlePaste()<br/>removeBlock()"]
    
    InputState -.->|"User types"| TextArea["textarea element"]
    TextArea -.->|"onChange"| InputState
    
    ContentBlocks -.->|"Merge with text"| Submit["handleSubmit()"]
    InputState -.->|"Merge with files"| Submit
```

**State declarations** [src/components/thread/index.tsx:127-137]():
- `input` - Controlled text input state
- `contentBlocks` - Array of uploaded file blocks
- `dragOver` - Drag-and-drop UI feedback
- File upload handlers (from `useFileUpload` hook)

**Sources**: [src/components/thread/index.tsx:127-137]()

### Loading and Error State

```mermaid
graph LR
    FirstToken["firstTokenReceived<br/>useState(false)"]
    LastError["lastError<br/>useRef&lt;string | undefined&gt;"]
    PrevMsgLen["prevMessageLength<br/>useRef(0)"]
    
    FirstToken -.->|"Controls"| LoadingIndicator["AssistantMessageLoading"]
    LastError -.->|"Prevents duplicate"| ErrorToast["toast.error()"]
    PrevMsgLen -.->|"Detects new messages"| FirstToken
```

**Loading state tracking** [src/components/thread/index.tsx:138]():
- `firstTokenReceived` - Tracks whether the first token of a streaming response has arrived
- Controls display of loading indicator while waiting for initial response

**Error state tracking** [src/components/thread/index.tsx:145]():
- `lastError` - Ref storing last error message to prevent duplicate toasts
- Used in effect that monitors `stream.error` [src/components/thread/index.tsx:155-181]()

**Message length tracking** [src/components/thread/index.tsx:184-195]():
- `prevMessageLength` - Ref tracking previous message count
- Effect detects new AI messages to set `firstTokenReceived` flag

**Sources**: [src/components/thread/index.tsx:138](), [src/components/thread/index.tsx:145](), [src/components/thread/index.tsx:184-195]()

### Media Query State

The Thread component uses a media query hook to detect screen size [src/components/thread/index.tsx:139]():
```typescript
const isLargeScreen = useMediaQuery("(min-width: 1024px)");
```

This controls responsive behavior, particularly animation timing for the chat history sidebar [src/components/thread/index.tsx:270-274]().

**Sources**: [src/components/thread/index.tsx:139](), [src/components/thread/index.tsx:270-274]()

## Configuration Priority System

The StreamProvider implements a three-tier priority system for configuration values:

```mermaid
graph TD
    URLParams["1. URL Query Parameters<br/>Highest Priority"]
    EnvVars["2. Environment Variables<br/>Middle Priority"]
    LocalStorage["3. Local Storage<br/>Lowest Priority<br/>(API Key only)"]
    
    URLParams -->|"Override"| EnvVars
    EnvVars -->|"Override"| LocalStorage
    
    FinalConfig["Final Configuration<br/>apiUrl, assistantId, apiKey"]
    
    URLParams -.-> FinalConfig
    EnvVars -.-> FinalConfig
    LocalStorage -.-> FinalConfig
    
    SetupForm["Interactive Setup Form<br/>Shown if missing values"]
    FinalConfig -.->|"If incomplete"| SetupForm
```

### Priority Implementation

**URL parameters with environment variable fallbacks** [src/providers/Stream.tsx:136-147]():
```typescript
const envApiUrl = process.env.NEXT_PUBLIC_API_URL;
const envAssistantId = process.env.NEXT_PUBLIC_ASSISTANT_ID;

const [apiUrl, setApiUrl] = useQueryState("apiUrl", {
  defaultValue: envApiUrl || "",
});
const [assistantId, setAssistantId] = useQueryState("assistantId", {
  defaultValue: envAssistantId || "",
});
```

**API key from local storage** [src/providers/Stream.tsx:150-158]():
```typescript
const [apiKey, _setApiKey] = useState(() => {
  const storedKey = getApiKey();
  return storedKey || "";
});

const setApiKey = (key: string) => {
  window.localStorage.setItem("lg:chat:apiKey", key);
  _setApiKey(key);
};
```

**Final value resolution** [src/providers/Stream.tsx:160-162]():
```typescript
const finalApiUrl = apiUrl || envApiUrl;
const finalAssistantId = assistantId || envAssistantId;
```

### Setup Form

When required configuration is missing, the StreamProvider renders an interactive setup form [src/providers/Stream.tsx:165-264](). The form allows users to input:
- **Deployment URL** - Required, defaults to `http://localhost:2024`
- **Assistant/Graph ID** - Required, defaults to `agent`
- **LangSmith API Key** - Optional for local development

Form submission updates all three state layers simultaneously [src/providers/Stream.tsx:182-196]().

**Sources**: [src/providers/Stream.tsx:136-162](), [src/providers/Stream.tsx:165-264]()

## State Flow Patterns

### Message Submission Flow

The message submission process coordinates multiple state layers:

```mermaid
graph TD
    UserInput["User submits message"]
    GatherState["Gather state<br/>input, contentBlocks, artifactContext"]
    
    CreateMsg["Create newHumanMessage<br/>type: 'human'<br/>content: [text, ...files]"]
    
    EnsureTools["ensureToolCallsHaveResponses()<br/>Validate tool message pairs"]
    
    CheckContext["Check artifactContext<br/>Include if non-empty"]
    
    Submit["stream.submit()<br/>optimisticValues<br/>streamMode: ['values']"]
    
    ClearLocal["Clear local state<br/>setInput('')<br/>setContentBlocks([])"]
    
    UserInput --> GatherState
    GatherState --> CreateMsg
    GatherState --> EnsureTools
    GatherState --> CheckContext
    CreateMsg --> Submit
    EnsureTools --> Submit
    CheckContext --> Submit
    Submit --> ClearLocal
```

**Implementation** [src/components/thread/index.tsx:197-237]():
1. Prevent submission if input is empty and no files are attached
2. Create a new `Message` object with UUID
3. Merge text and content blocks into message content array
4. Validate tool messages using `ensureToolCallsHaveResponses`
5. Include artifact context if present
6. Submit to stream with optimistic UI updates
7. Clear local input and file state

**Sources**: [src/components/thread/index.tsx:197-237]()

### Thread Navigation Flow

When switching threads, multiple cleanup operations occur:

```mermaid
graph TD
    Trigger["setThreadId(id)"]
    UpdateURL["_setThreadId(id)<br/>Update URL parameter"]
    ClosePanel["closeArtifact()<br/>Close side panel"]
    ClearContext["setArtifactContext({})<br/>Clear artifact data"]
    
    Trigger --> UpdateURL
    Trigger --> ClosePanel
    Trigger --> ClearContext
    
    URLChange["URL change detected"]
    StreamSession["StreamSession re-mounts<br/>New stream connection"]
    
    UpdateURL --> URLChange
    URLChange --> StreamSession
```

**Cleanup wrapper** [src/components/thread/index.tsx:147-153]():
The Thread component wraps the URL state setter to perform necessary cleanup operations when the thread ID changes.

**Sources**: [src/components/thread/index.tsx:147-153]()

### Thread List Refresh Flow

The StreamProvider coordinates with ThreadProvider to refresh the thread list when new threads are created:

```mermaid
graph LR
    StreamHook["useTypedStream<br/>onThreadId callback"]
    SetURL["setThreadId(id)"]
    Sleep["sleep(4000ms)"]
    GetThreads["getThreads()"]
    SetThreads["setThreads(threads)"]
    
    StreamHook -->|"Thread created"| SetURL
    SetURL --> Sleep
    Sleep -->|"Delay for backend"| GetThreads
    GetThreads -->|"Fetch from API"| SetThreads
```

**Implementation** [src/providers/Stream.tsx:96-101]():
The `onThreadId` callback includes a 4-second delay before fetching threads to ensure the backend has processed the new thread creation.

**Sources**: [src/providers/Stream.tsx:96-101]()

### Artifact Context Flow

Artifact context is passed through the message submission pipeline:

```mermaid
graph TD
    UseContext["useArtifactContext()<br/>Get context getter/setter"]
    CheckEmpty["Check if context non-empty<br/>Object.keys().length > 0"]
    
    IncludeInSubmit["Include in stream.submit()<br/>{messages, context}"]
    OptimisticUpdate["optimisticValues<br/>Merge context into state"]
    
    BackendReceive["LangGraph receives context<br/>Available to agent"]
    
    UseContext --> CheckEmpty
    CheckEmpty -->|"Has data"| IncludeInSubmit
    IncludeInSubmit --> OptimisticUpdate
    OptimisticUpdate --> BackendReceive
```

**Context usage in submission** [src/components/thread/index.tsx:214-216]():
```typescript
const context =
  Object.keys(artifactContext).length > 0 ? artifactContext : undefined;
```

The context is only included if it contains data, preventing empty object submission.

**Sources**: [src/components/thread/index.tsx:115](), [src/components/thread/index.tsx:214-233]()

## State Persistence

The application uses different persistence strategies for different state types:

| State Type | Persistence Mechanism | Lifetime | Use Case |
|------------|----------------------|----------|----------|
| URL Parameters | Browser history & bookmarks | Session + shareable | Navigation, preferences |
| API Key | localStorage | Persistent across sessions | Authentication |
| Environment Variables | Build-time configuration | Application lifetime | Deployment defaults |
| Provider Contexts | React component tree | Current session | Runtime application state |
| Local Component State | Component lifecycle | Component mount lifetime | Ephemeral UI state |

**LocalStorage usage** [src/providers/Stream.tsx:150-158]():
Only the API key is stored in localStorage, retrieved via `getApiKey()` utility and set via `window.localStorage.setItem()`.

**URL persistence** [src/components/thread/index.tsx:118-126]():
All URL parameters automatically persist to browser history and can be bookmarked for deep linking.

**Sources**: [src/providers/Stream.tsx:150-158](), [src/components/thread/index.tsx:118-126]()

---

