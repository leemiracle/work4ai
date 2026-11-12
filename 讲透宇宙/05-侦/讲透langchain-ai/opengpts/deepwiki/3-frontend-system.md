<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/opengpts · page 3 Frontend System · fetched 2026-10-26 -->

# Frontend System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [frontend/src/App.tsx](frontend/src/App.tsx)

</details>



## Purpose and Scope

This document describes the React-based frontend application that provides the user interface for OpenGPTs. The frontend is responsible for assistant configuration, conversation management, message display, and real-time streaming of agent responses. It communicates with the backend through REST APIs and Server-Sent Events (SSE).

For information about the backend APIs that the frontend consumes, see [Backend System](#2). For details about the agent execution and streaming mechanisms, see [Streaming System](#2.6).

---

## Technology Stack

The frontend is built with the following technologies:

| Technology | Purpose | Key Features |
|-----------|---------|--------------|
| **React 18** | UI framework | Component-based architecture, hooks |
| **TypeScript** | Type safety | Static typing, interface definitions |
| **React Router** | URL-based routing | Path parameters for threads and assistants |
| **Vite** | Build tool | Fast development server, optimized production builds |
| **Tailwind CSS** | Styling | Utility-first CSS framework |
| **Heroicons** | Icons | React icon components |

The application follows a single-page application (SPA) architecture where all UI state is derived from the URL and backend API responses.

**Sources:** `frontend/package.json`, `frontend/vite.config.ts`

---

## Application Architecture

The frontend uses a centralized orchestration pattern where the `App` component serves as the main hub that:

1. Reads route parameters to determine current context
2. Fetches necessary data through custom hooks
3. Conditionally renders appropriate UI components
4. Manages global state like sidebar visibility

```mermaid
graph TB
    Router["React Router<br/>/thread/:id<br/>/assistant/:id<br/>/assistant/:id/edit<br/>/"]
    
    App["App Component<br/>(App.tsx)"]
    
    subgraph "Custom Hooks Layer"
        UTA["useThreadAndAssistant<br/>Derives state from URL"]
        UCL["useChatList<br/>Thread CRUD"]
        UCFG["useConfigList<br/>Assistant CRUD"]
        USS["useStreamState<br/>SSE streaming"]
        USM["useSchemas<br/>Config schemas"]
    end
    
    subgraph "UI Components"
        Chat["Chat<br/>Active conversation"]
        NewChat["NewChat<br/>Start new conversation"]
        Config["Config<br/>Assistant editor"]
        OrphanChat["OrphanChat<br/>Thread without assistant"]
        Layout["Layout<br/>Shell + sidebar"]
        ChatList["ChatList<br/>Thread/assistant navigation"]
    end
    
    subgraph "Backend APIs"
        ThreadsAPI["/threads"]
        AssistantsAPI["/assistants"]
        RunsAPI["/runs/stream"]
        IngestAPI["/ingest"]
    end
    
    Router --> App
    
    App --> UTA
    App --> UCL
    App --> UCFG
    App --> USS
    App --> USM
    
    App --> Layout
    Layout --> ChatList
    
    App --> Chat
    App --> NewChat
    App --> Config
    App --> OrphanChat
    
    UTA --> ThreadsAPI
    UTA --> AssistantsAPI
    UCL --> ThreadsAPI
    UCFG --> AssistantsAPI
    USS --> RunsAPI
    USS --> IngestAPI
    
    ChatList --> UCL
    ChatList --> UCFG
    Chat --> USS
    NewChat --> USS
```

**Diagram: Frontend Component and Hook Architecture**

The diagram shows how URL routing drives the entire application state. The `useThreadAndAssistant` hook [frontend/src/hooks/useThreadAndAssistant.ts]() extracts route parameters and fetches the corresponding thread and assistant data, which determines which component the `App` renders.

**Sources:** [frontend/src/App.tsx:1-189](), [frontend/src/main.tsx]()

---

## Routing Structure

The application defines four primary routes that determine the UI state:

```mermaid
graph LR
    Root["/"]
    Thread["/thread/:id"]
    Assistant["/assistant/:id"]
    AssistantEdit["/assistant/:id/edit"]
    
    Root -->|"No thread, no assistant"| ConfigCreate["Config Component<br/>(create mode)"]
    Thread -->|"Has thread + assistant"| ChatView["Chat Component"]
    Thread -->|"Has thread, missing assistant"| OrphanView["OrphanChat Component"]
    Assistant -->|"No thread, has assistant"| NewChatView["NewChat Component"]
    AssistantEdit -->|"No thread, has assistant"| ConfigEdit["Config Component<br/>(edit mode)"]
```

**Diagram: URL Routes and Component Rendering Logic**

The routing logic is implemented in [frontend/src/App.tsx:146-184]():

| Condition | Rendered Component | Purpose |
|-----------|-------------------|---------|
| `currentChat && assistantConfig` | `Chat` | Active conversation |
| `currentChat && !assistantConfig` | `OrphanChat` | Thread exists but assistant was deleted |
| `!currentChat && assistantConfig && !props.edit` | `NewChat` | Start new conversation with selected assistant |
| `!currentChat && assistantConfig && props.edit` | `Config` (edit mode) | Modify existing assistant |
| `!currentChat && !assistantConfig && !isLoading` | `Config` (create mode) | Create new assistant |

This conditional rendering ensures that the UI always displays an appropriate view based on the presence or absence of thread and assistant data.

**Sources:** [frontend/src/App.tsx:146-184](), [frontend/src/main.tsx]()

---

## State Management Philosophy

The frontend follows a **URL-as-source-of-truth** pattern where:

1. **URL parameters drive data fetching** - Route params (`:id`) are extracted by `useThreadAndAssistant`
2. **Backend is authoritative** - No local optimistic updates for conversation state
3. **Hooks encapsulate data access** - Each data domain (threads, assistants, schemas) has a dedicated hook
4. **Streaming is separate from persistence** - Real-time updates come via SSE, but final state is fetched from REST endpoints

```mermaid
sequenceDiagram
    participant URL as "URL Change"
    participant UTA as "useThreadAndAssistant"
    participant API as "Backend APIs"
    participant App as "App Component"
    participant UI as "UI Components"
    
    URL->>UTA: Route params change
    UTA->>API: GET /threads/:id
    UTA->>API: GET /assistants/:id
    API-->>UTA: Thread data
    API-->>UTA: Assistant config
    UTA-->>App: {currentChat, assistantConfig, isLoading}
    App->>App: Evaluate conditions
    App->>UI: Render appropriate component
```

**Diagram: State Derivation Flow from URL to UI**

The key insight is that navigation (changing the URL) automatically triggers data fetching through the `useThreadAndAssistant` hook, which then causes the `App` component to re-render with updated data.

**Sources:** [frontend/src/App.tsx:29](), [frontend/src/hooks/useThreadAndAssistant.ts]()

---

## Component Overview

### Core UI Components

| Component | File Path | Purpose |
|-----------|-----------|---------|
| `App` | `frontend/src/App.tsx` | Central orchestrator, routing logic, sidebar management |
| `Chat` | `frontend/src/components/Chat.tsx` | Active conversation interface with message display and input |
| `NewChat` | `frontend/src/components/NewChat.tsx` | Assistant selection and first message interface |
| `Config` | `frontend/src/components/Config.tsx` | Assistant configuration form (create/edit) |
| `OrphanChat` | `frontend/src/components/OrphanChat.tsx` | Display for threads with deleted assistants |
| `Layout` | `frontend/src/components/Layout.tsx` | Page shell with responsive sidebar |
| `ChatList` | `frontend/src/components/ChatList.tsx` | Sidebar navigation for threads and assistants |

### Specialized Display Components

| Component | Purpose |
|-----------|---------|
| `MessageViewer` | Renders individual messages with markdown support |
| `DocumentViewer` | Displays file attachments and document metadata |
| `ToolCallViewer` | Visualizes agent tool invocations and results |

For detailed information about the configuration interface, see [Configuration Interface](#3.2). For chat and messaging components, see [Chat and Messaging](#3.3).

**Sources:** [frontend/src/components/]()

---

## Data Flow: Message Submission

The frontend handles message submission through a multi-phase process:

```mermaid
sequenceDiagram
    participant User
    participant App as "App.startTurn()"
    participant IngestAPI as "/ingest"
    participant USS as "useStreamState"
    participant RunsAPI as "/runs/stream"
    participant Backend as "Backend Agent"
    
    Note over User,Backend: Phase 1: File Upload (if present)
    User->>App: Submit message with files
    App->>App: Extract files from MessageWithFiles
    alt files.length > 0
        App->>IngestAPI: POST multipart/form-data<br/>{files, config}
        IngestAPI->>Backend: Process and embed files
        IngestAPI-->>App: 200 OK
    end
    
    Note over User,Backend: Phase 2: Format Input
    App->>App: Create Message[] array<br/>type: "human"
    alt assistantType === "chat_retrieval"
        App->>App: Wrap in {messages: [...]}
    end
    
    Note over User,Backend: Phase 3: Start Streaming
    App->>USS: startStream(input, thread_id, config)
    USS->>RunsAPI: POST SSE connection
    RunsAPI->>Backend: Execute agent graph
    Backend-->>USS: Stream events
    USS-->>App: Update stream state
    USS-->>User: Display incremental updates
```

**Diagram: Message Submission Flow with File Handling**

The implementation in [frontend/src/App.tsx:31-81]() shows several key details:

1. **File upload is synchronous** - Files are uploaded via `/ingest` endpoint before streaming begins
2. **Input format varies by assistant type** - RAG assistants require `{messages: [...]}` while others accept `Message[]` directly
3. **Human messages have specific structure** - Each message includes `content`, `type`, `additional_kwargs`, and a unique `id`

**Sources:** [frontend/src/App.tsx:31-81]()

---

## Hook Architecture

The frontend uses specialized custom hooks to encapsulate different aspects of state management:

```mermaid
graph TB
    subgraph "Data Domain Hooks"
        UCL["useChatList<br/>Thread operations"]
        UCFG["useConfigList<br/>Assistant operations"]
        USM["useSchemas<br/>Config schemas"]
    end
    
    subgraph "Derived State Hooks"
        UTA["useThreadAndAssistant<br/>URL-based state"]
        UCM["useChatMessages<br/>Message merging"]
    end
    
    subgraph "Streaming Hooks"
        USS["useStreamState<br/>SSE management"]
    end
    
    subgraph "Backend APIs"
        ThreadsAPI["/threads<br/>/threads/:id<br/>/threads/:id/state"]
        AssistantsAPI["/assistants<br/>/assistants/:id"]
        RunsAPI["/runs/stream"]
    end
    
    UCL --> ThreadsAPI
    UCFG --> AssistantsAPI
    USM --> AssistantsAPI
    UTA --> ThreadsAPI
    UTA --> AssistantsAPI
    UCM --> ThreadsAPI
    USS --> RunsAPI
```

**Diagram: Custom Hooks and API Endpoints**

### Hook Responsibilities

| Hook | Responsibility | Key Methods |
|------|---------------|-------------|
| `useChatList` | Thread CRUD operations | `createChat`, `updateChat`, `deleteChat` |
| `useConfigList` | Assistant CRUD operations | `saveConfig`, `deleteConfig` |
| `useStreamState` | SSE connection management | `startStream`, `stopStream` |
| `useSchemas` | Fetch configuration schemas | Returns `configSchema`, `configDefaults` |
| `useThreadAndAssistant` | Derive state from URL | Returns `currentChat`, `assistantConfig`, `isLoading` |
| `useChatMessages` | Merge streaming and persisted messages | Returns deduplicated message list |

For detailed information about these hooks, see [State Management and API Integration](#3.4).

**Sources:** [frontend/src/hooks/]()

---

## Chat Initialization Flow

When starting a new conversation, the frontend performs several coordinated operations:

```mermaid
sequenceDiagram
    participant User
    participant App as "App.startChat()"
    participant UCL as "useChatList"
    participant Router as "React Router"
    participant App2 as "App.startTurn()"
    
    User->>App: Submit first message
    App->>UCL: createChat(message, assistant_id)
    UCL->>Backend: POST /threads<br/>{name, assistant_id}
    Backend-->>UCL: {thread_id, ...}
    UCL-->>App: Created chat object
    App->>Router: navigate(`/thread/${thread_id}`)
    Note over Router: URL changes, triggers re-render
    App->>App2: startTurn(message, thread_id, assistantType)
    App2->>USS: Start streaming execution
```

**Diagram: New Conversation Creation Flow**

The `startChat` callback in [frontend/src/App.tsx:83-91]() demonstrates the coordinated sequence:

1. **Create thread** - Call `createChat` which POSTs to `/threads`
2. **Navigate to thread** - Change URL to `/thread/:id`
3. **Start streaming** - Begin agent execution with the initial message

This separation ensures that the thread exists in the database before any streaming begins, preventing race conditions.

**Sources:** [frontend/src/App.tsx:83-91]()

---

## Sidebar and Navigation

The `ChatList` component provides navigation between threads and assistants:

```mermaid
graph TB
    ChatList["ChatList Component"]
    
    subgraph "Displayed Data"
        ThreadList["Thread List<br/>(from useChatList)"]
        AssistantList["Assistant List<br/>(from useConfigList)"]
    end
    
    subgraph "User Actions"
        SelectThread["Click thread<br/>→ navigate(`/thread/:id`)"]
        SelectAssistant["Click assistant<br/>→ navigate(`/assistant/:id`)"]
        DeleteThread["Delete thread<br/>→ deleteChat()"]
        DeleteAssistant["Delete assistant<br/>→ deleteConfig()"]
    end
    
    ChatList --> ThreadList
    ChatList --> AssistantList
    ChatList --> SelectThread
    ChatList --> SelectAssistant
    ChatList --> DeleteThread
    ChatList --> DeleteAssistant
    
    SelectThread --> Router
    SelectAssistant --> Router
    DeleteThread --> API
    DeleteAssistant --> API
```

**Diagram: ChatList Sidebar Navigation Structure**

The `Layout` component in [frontend/src/components/Layout.tsx]() provides a responsive shell that:
- Displays the `ChatList` in a sidebar
- Handles mobile/desktop sidebar visibility
- Shows the current assistant name in the header
- Contains the main content area where `Chat`, `NewChat`, or `Config` renders

The sidebar state is managed in [frontend/src/App.tsx:23]() with `useState` and can be toggled via the hamburger menu icon.

**Sources:** [frontend/src/App.tsx:120-145](), [frontend/src/components/Layout.tsx](), [frontend/src/components/ChatList.tsx]()

---

## Error Handling and Edge Cases

The frontend handles several edge cases through conditional rendering:

### Orphaned Threads

When a thread exists but its associated assistant has been deleted, the `OrphanChat` component is rendered [frontend/src/App.tsx:149-151](). This component:
- Displays the conversation history
- Allows reassigning the thread to a different assistant
- Updates the thread's `assistant_id` via `updateChat`

### Loading States

While `useThreadAndAssistant` is fetching data, `isLoading` is true and a loading indicator is displayed [frontend/src/App.tsx:184](). This prevents premature rendering of components that depend on loaded data.

### Stream Interruption

When navigating away from an active chat, the `selectChat` callback [frontend/src/App.tsx:93-110]() calls `stopStream?.(true)` to cleanly terminate the SSE connection before changing routes.

### Empty State

When no assistants exist and no thread is selected, the `Config` component is rendered in create mode [frontend/src/App.tsx:174-183](), allowing the user to create their first assistant.

**Sources:** [frontend/src/App.tsx:93-110](), [frontend/src/App.tsx:146-184](), [frontend/src/components/OrphanChat.tsx]()

---

## Build and Deployment

The frontend is built using Vite and can be deployed in two ways:

### Development Mode

```bash
cd frontend
npm run dev  # Starts dev server on port 5173
```

The development server proxies API requests to the backend running on port 8100.

### Production Build

```bash
cd frontend
npm run build  # Outputs to frontend/dist
```

The production build is copied into the backend's `ui/` directory and served as static files by the FastAPI application. This monolithic deployment approach is implemented in the multi-stage Dockerfile [Dockerfile]().

For detailed deployment information, see [Deployment and Configuration](#1.2).

**Sources:** `frontend/package.json`, `frontend/vite.config.ts`, `Dockerfile`

---

## Summary

The OpenGPTs frontend is a React application that:

1. **Uses URL-driven state** via React Router and `useThreadAndAssistant`
2. **Conditionally renders components** based on the presence of thread and assistant data
3. **Encapsulates data access** through specialized custom hooks
4. **Handles file uploads** before streaming begins via the `/ingest` endpoint
5. **Manages real-time updates** through SSE connections in `useStreamState`
6. **Provides navigation** via a responsive sidebar with `ChatList`

The application architecture emphasizes separation of concerns, with the `App` component serving as a thin orchestration layer that delegates to specialized hooks and components.

For component-specific details, refer to:
- [Application Structure](#3.1) - App component orchestration
- [Configuration Interface](#3.2) - Assistant setup and management
- [Chat and Messaging](#3.3) - Message display and interaction
- [State Management and API Integration](#3.4) - Hook implementations

**Sources:** [frontend/src/App.tsx:1-189](), [frontend/src/main.tsx]()

---

