<!-- source: DeepWiki mcp.deepwiki.com · repo tambo-ai/tambo · page 7 Backend API · fetched 2026-10-29 -->

# Backend API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/api/src/threads/guards/thread-in-project-guard.ts](apps/api/src/threads/guards/thread-in-project-guard.ts)
- [apps/api/src/threads/threads.service.test.ts](apps/api/src/threads/threads.service.test.ts)
- [apps/api/src/threads/threads.service.ts](apps/api/src/threads/threads.service.ts)
- [apps/api/src/threads/util/content.test.ts](apps/api/src/threads/util/content.test.ts)
- [apps/api/src/threads/util/content.ts](apps/api/src/threads/util/content.ts)
- [apps/api/src/threads/util/thread-state.test.ts](apps/api/src/threads/util/thread-state.test.ts)
- [apps/api/src/threads/util/thread-state.ts](apps/api/src/threads/util/thread-state.ts)
- [apps/api/src/v1/__tests__/v1-conversions.test.ts](apps/api/src/v1/__tests__/v1-conversions.test.ts)
- [apps/api/src/v1/__tests__/v1-thread-in-project-guard.test.ts](apps/api/src/v1/__tests__/v1-thread-in-project-guard.test.ts)
- [apps/api/src/v1/__tests__/v1.controller.test.ts](apps/api/src/v1/__tests__/v1.controller.test.ts)
- [apps/api/src/v1/__tests__/v1.service.test.ts](apps/api/src/v1/__tests__/v1.service.test.ts)
- [apps/api/src/v1/dto/component-state.dto.ts](apps/api/src/v1/dto/component-state.dto.ts)
- [apps/api/src/v1/dto/message.dto.ts](apps/api/src/v1/dto/message.dto.ts)
- [apps/api/src/v1/dto/thread.dto.ts](apps/api/src/v1/dto/thread.dto.ts)
- [apps/api/src/v1/guards/v1-thread-in-project-guard.ts](apps/api/src/v1/guards/v1-thread-in-project-guard.ts)
- [apps/api/src/v1/utils/get-v1-context-info.ts](apps/api/src/v1/utils/get-v1-context-info.ts)
- [apps/api/src/v1/v1-conversions.ts](apps/api/src/v1/v1-conversions.ts)
- [apps/api/src/v1/v1.controller.ts](apps/api/src/v1/v1.controller.ts)
- [apps/api/src/v1/v1.service.ts](apps/api/src/v1/v1.service.ts)
- [packages/backend/src/index.ts](packages/backend/src/index.ts)
- [packages/backend/src/services/decision-loop/decision-loop-service.ts](packages/backend/src/services/decision-loop/decision-loop-service.ts)
- [packages/backend/src/services/llm/ai-sdk-client-abort.test.ts](packages/backend/src/services/llm/ai-sdk-client-abort.test.ts)
- [packages/backend/src/services/llm/ai-sdk-client.test.ts](packages/backend/src/services/llm/ai-sdk-client.test.ts)
- [packages/backend/src/services/llm/ai-sdk-client.ts](packages/backend/src/services/llm/ai-sdk-client.ts)
- [packages/backend/src/services/llm/llm-client.ts](packages/backend/src/services/llm/llm-client.ts)
- [packages/backend/src/services/tool/tool-service.ts](packages/backend/src/services/tool/tool-service.ts)
- [packages/backend/src/tambo-backend.ts](packages/backend/src/tambo-backend.ts)
- [packages/backend/src/util/component-streaming.test.ts](packages/backend/src/util/component-streaming.test.ts)
- [packages/backend/src/util/component-streaming.ts](packages/backend/src/util/component-streaming.ts)
- [packages/core/src/ComponentDecision.ts](packages/core/src/ComponentDecision.ts)
- [packages/db/src/index.ts](packages/db/src/index.ts)
- [packages/db/src/operations/thread.ts](packages/db/src/operations/thread.ts)
- [packages/react-ui-base/src/toolcall-info/result/toolcall-info-result.tsx](packages/react-ui-base/src/toolcall-info/result/toolcall-info-result.tsx)
- [packages/ui-registry/src/components/thread-content/thread-content.tsx](packages/ui-registry/src/components/thread-content/thread-content.tsx)
- [react-sdk/src/v1/types/message.ts](react-sdk/src/v1/types/message.ts)

</details>



## Purpose and Scope

This document covers the V1 REST API located in `apps/api/src/v1`, which provides HTTP endpoints for thread management, streaming AI responses, and component state synchronization. The API implements a run-based concurrency model with atomic locks, streams AG-UI events via Server-Sent Events (SSE), and orchestrates LLM interactions through `ThreadsService`. For the React SDK that consumes this API, see [React SDK](#3). For database schema details, see [Database Schema and Operations](#7.6).

**Sources:** [apps/api/src/v1/v1.controller.ts:1-570](), [apps/api/src/v1/v1.service.ts:1-1545]()

---

## V1 API Architecture

**V1 API Request Flow**

```mermaid
graph TB
    Client["React SDK<br/>@tambo-ai/react"]
    
    subgraph "apps/api/src/v1"
        V1Controller["V1Controller<br/>v1.controller.ts"]
        V1Service["V1Service<br/>v1.service.ts"]
        
        subgraph "Request Flow"
            Guards["Guards<br/>ApiKeyGuard<br/>BearerTokenGuard<br/>V1ThreadInProjectGuard"]
            Validation["DTO Validation<br/>class-validator"]
            StartRun["startRun()<br/>Atomic Lock Acquisition"]
            ExecuteRun["executeRun()<br/>SSE Streaming"]
        end
    end
    
    subgraph "apps/api/src/threads"
        ThreadsService["ThreadsService<br/>threads.service.ts"]
        AdvanceThread["advanceThread()<br/>LLM Orchestration"]
    end
    
    subgraph "@tambo-ai-cloud/backend"
        DecisionLoop["runDecisionLoop<br/>AI Decision Engine"]
        AISdkClient["AISdkClient<br/>Multi-Provider Client"]
    end
    
    subgraph "@tambo-ai-cloud/db"
        Operations["operations<br/>CRUD + Locking"]
        DB[("PostgreSQL")]
    end
    
    Client -->|"POST /v1/threads/:id/runs"| V1Controller
    V1Controller --> Guards
    Guards --> Validation
    Validation --> StartRun
    StartRun --> V1Service
    V1Service -->|"acquireRunLock()"| Operations
    Operations --> DB
    V1Service --> ExecuteRun
    ExecuteRun --> ThreadsService
    ThreadsService --> AdvanceThread
    AdvanceThread --> DecisionLoop
    DecisionLoop --> AISdkClient
    AISdkClient -.->|"SSE Events"| Client
```

**Layered Architecture:** The V1 API separates HTTP concerns (`V1Controller`) from business logic (`V1Service`) and thread orchestration (`ThreadsService`). Guards enforce authentication and authorization, while the decision loop handles AI generation.

**Sources:** [apps/api/src/v1/v1.controller.ts:421-527](), [apps/api/src/v1/v1.service.ts:669-944](), [apps/api/src/threads/threads.service.ts:737-1218]()

---

## V1 API Endpoints

**V1Controller REST Endpoints**

The `V1Controller` exposes RESTful endpoints for thread and message operations:

| Method | Endpoint | Description | Response Type |
|--------|----------|-------------|---------------|
| `POST` | `/v1/threads` | Create empty thread | JSON |
| `GET` | `/v1/threads` | List threads with pagination | JSON |
| `GET` | `/v1/threads/:threadId` | Get thread with messages | JSON |
| `PATCH` | `/v1/threads/:threadId` | Update thread metadata | JSON |
| `DELETE` | `/v1/threads/:threadId` | Delete thread and messages | 204 No Content |
| `GET` | `/v1/threads/:threadId/messages` | List messages in thread | JSON |
| `GET` | `/v1/threads/:threadId/messages/:messageId` | Get single message | JSON |
| `POST` | `/v1/threads/runs` | Create thread with run (streaming) | SSE |
| `POST` | `/v1/threads/:threadId/runs` | Start run on thread (streaming) | SSE |
| `DELETE` | `/v1/threads/:threadId/runs/:runId` | Cancel active run | JSON |
| `PATCH` | `/v1/threads/:threadId/components/:componentId` | Update component state | JSON |
| `POST` | `/v1/threads/:threadId/messages/:messageId/suggestions` | Generate suggestions | JSON |
| `GET` | `/v1/threads/:threadId/messages/:messageId/suggestions` | List suggestions | JSON |

**Thread Lifecycle:** Threads are created empty (`POST /v1/threads`), then populated through runs (`POST /v1/threads/:id/runs`). Each run appends a user message and streams the AI response via SSE.

**Run Endpoints:** Both run endpoints (`POST /v1/threads/runs` and `POST /v1/threads/:threadId/runs`) return Server-Sent Events streams with `Content-Type: text/event-stream`. They emit AG-UI events as the AI generates content.

**Component State Endpoint:** `PATCH /v1/threads/:threadId/components/:componentId` supports both full state replacement and JSON Patch operations (RFC 6902) for atomic component updates.

**Sources:** [apps/api/src/v1/v1.controller.ts:78-570](), [apps/api/src/v1/dto/thread.dto.ts:1-326](), [apps/api/src/v1/dto/component-state.dto.ts:1-97]()

---

## Run Lifecycle and Concurrency

**Run State Machine**

```mermaid
stateDiagram-v2
    [*] --> IDLE: Thread Created
    IDLE --> WAITING: startRun()<br/>acquireRunLock()
    WAITING --> STREAMING: executeRun()<br/>Start LLM Stream
    STREAMING --> WAITING: Tool Call Detected<br/>awaiting_input
    STREAMING --> IDLE: RUN_FINISHED<br/>releaseRunLock()
    STREAMING --> IDLE: RUN_ERROR<br/>releaseRunLock()
    STREAMING --> IDLE: cancelRun()<br/>releaseRunLock()
    WAITING --> IDLE: cancelRun()<br/>releaseRunLock()
    
    note right of IDLE
        runStatus: "idle"
        currentRunId: null
    end note
    
    note right of WAITING
        runStatus: "waiting"
        currentRunId: set
        Atomic lock acquired
    end note
    
    note right of STREAMING
        runStatus: "streaming"
        SSE events flowing
        Tool calls executing
    end note
```

**Concurrency Model:** The V1 API implements atomic run locks to prevent concurrent runs on the same thread. `operations.acquireRunLock()` atomically sets `runStatus` from `IDLE` to `WAITING`, failing if the thread is already processing.

**Run Creation:** `V1Service.startRun()` performs atomic lock acquisition in a database transaction:
1. Validates `previousRunId` matches `lastCompletedRunId` (for continuing threads)
2. Processes any tool results from the request
3. Atomically acquires run lock via `operations.acquireRunLock()`
4. Creates run record in `runs` table
5. Returns run ID or conflict error

**Lock Release:** `operations.releaseRunLockIfCurrent()` releases the lock only if the current run ID matches, preventing race conditions. Locks are released on completion, error, or cancellation.

**Tool Call Flow:** When the LLM generates client-side tool calls, the run enters `WAITING` state and emits an `awaiting_input` event with `pendingToolCallIds`. The client executes tools and submits results via `POST /v1/threads/:id/runs` with `previousRunId` set.

**Sources:** [apps/api/src/v1/v1.service.ts:394-581](), [apps/api/src/v1/v1.service.ts:591-651](), [packages/db/src/operations/thread.ts:450-544]()

---

## Streaming Responses

**SSE Event Flow**

```mermaid
sequenceDiagram
    participant Client as React SDK
    participant V1Controller as V1Controller<br/>executeRun()
    participant ThreadsService as ThreadsService<br/>advanceThread()
    participant AsyncQueue as AsyncQueue<br/>StreamQueueItem
    participant DecisionLoop as runDecisionLoop<br/>AI Engine
    participant LLM as AISdkClient<br/>LLM Provider
    
    Client->>V1Controller: POST /v1/threads/:id/runs
    V1Controller->>V1Controller: Set SSE headers<br/>Content-Type: text/event-stream
    V1Controller->>Client: RUN_STARTED event
    
    V1Controller->>ThreadsService: advanceThread(queue, abortSignal)
    ThreadsService->>DecisionLoop: Process messages + tools
    DecisionLoop->>LLM: streamText()
    
    loop Streaming Chunks
        LLM-->>DecisionLoop: Delta (text/tool_call/component)
        DecisionLoop->>DecisionLoop: Parse to DecisionStreamItem
        DecisionLoop->>AsyncQueue: Push StreamQueueItem
        AsyncQueue->>V1Controller: Yield item
        V1Controller->>Client: SSE event (TEXT_DELTA, etc.)
    end
    
    alt Tool Call Required
        DecisionLoop->>AsyncQueue: awaiting_input event
        AsyncQueue->>V1Controller: Tool call info
        V1Controller->>Client: AWAITING_INPUT event
        Note over Client: Client executes tool
    end
    
    LLM-->>DecisionLoop: Stream complete
    DecisionLoop->>AsyncQueue: Close queue
    V1Controller->>Client: RUN_FINISHED event
    V1Controller->>Client: Close SSE connection
```

**SSE Configuration:** Both run endpoints set response headers `Content-Type: text/event-stream`, `Cache-Control: no-cache`, and `Connection: keep-alive`. They also set custom headers `X-Thread-Id` and `X-Run-Id` for client-side tracking.

**Event Format:** Each SSE event is formatted as `data: <json>\n\n` where `<json>` is a serialized `BaseEvent` from AG-UI core. Events include `TEXT_DELTA`, `TOOL_CALL_START`, `COMPONENT_START`, `RUN_FINISHED`, etc.

**Queue Architecture:** `ThreadsService.advanceThread()` accepts an `AsyncQueue<StreamQueueItem>` that acts as a bridge between the LLM streaming loop and the SSE writer. The decision loop pushes items to the queue, and `V1Controller.executeRun()` consumes them in a for-await loop.

**Cancellation:** The client can cancel a run by closing the SSE connection or calling `DELETE /v1/threads/:id/runs/:runId`. Both trigger `V1Service.cancelRun()` which sets the run status to cancelled and aborts the LLM stream via `AbortController`.

**Throttled Cancellation Checks:** During streaming, the controller periodically checks `operations.getRun()` to detect if the run was cancelled (e.g., by another request). Checks are throttled to `CANCEL_CHECK_INTERVAL_MS` (500ms) to avoid excessive database load.

**Sources:** [apps/api/src/v1/v1.service.ts:669-944](), [apps/api/src/v1/v1.controller.ts:341-527](), [packages/core/src/shared/asyncQueue.ts:1-61]()

---

## LLM Integration

**LLM Provider Architecture**

```mermaid
graph TB
    subgraph "ThreadsService"
        AdvanceThread["advanceThread()"]
        CreateBackend["createTamboBackendForThread()"]
    end
    
    subgraph "@tambo-ai-cloud/backend"
        TamboBackend["ITamboBackend"]
        DecisionLoop["runDecisionLoop()"]
        AISdkClient["AISdkClient"]
        
        subgraph "Provider Support"
            OpenAI["OpenAI<br/>@ai-sdk/openai"]
            Anthropic["Anthropic<br/>@ai-sdk/anthropic"]
            Google["Google<br/>@ai-sdk/google"]
            Groq["Groq<br/>@ai-sdk/groq"]
            Mistral["Mistral<br/>@ai-sdk/mistral"]
            Compatible["OpenAI-Compatible<br/>@ai-sdk/openai-compatible"]
        end
    end
    
    subgraph "Streaming Infrastructure"
        ComponentTracker["ComponentStreamTracker<br/>Incremental JSON Parsing"]
        EventAccumulator["fixStreamedToolCalls<br/>Event Processing"]
    end
    
    AdvanceThread --> CreateBackend
    CreateBackend --> TamboBackend
    TamboBackend --> DecisionLoop
    DecisionLoop --> AISdkClient
    
    AISdkClient --> OpenAI
    AISdkClient --> Anthropic
    AISdkClient --> Google
    AISdkClient --> Groq
    AISdkClient --> Mistral
    AISdkClient --> Compatible
    
    AISdkClient --> ComponentTracker
    ComponentTracker --> EventAccumulator
```

**Multi-Provider Client:** `AISdkClient` abstracts over multiple LLM providers using Vercel's AI SDK. It normalizes streaming responses, tool calls, and error handling across OpenAI, Anthropic, Google, Groq, Mistral, and OpenAI-compatible endpoints.

**Backend Instantiation:** `ThreadsService.createTamboBackendForThread()` creates a provider-specific backend instance based on project configuration. It fetches the project's `defaultLlmProviderName`, `defaultLlmModelName`, API keys, and custom parameters from the database.

**Decision Loop:** `runDecisionLoop()` is the core AI orchestration function. It:
1. Pre-fetches and caches MCP resources
2. Builds system prompt with component/tool definitions
3. Streams LLM responses through `AISdkClient.complete()`
4. Parses streaming deltas into `DecisionStreamItem` objects
5. Emits AG-UI events for text, tool calls, and components

**Incremental Component Parsing:** `ComponentStreamTracker` parses incomplete JSON as component props stream in. It uses `partial-json` to handle malformed JSON during streaming and emits `COMPONENT_PROPS_DELTA` events for progressive rendering.

**Tool Choice:** The decision loop supports tool choice overrides via `forceToolChoice` parameter. It converts keyword values (`"auto"`, `"required"`, `"none"`) and tool names to OpenAI's tool choice format.

**Sources:** [apps/api/src/threads/threads.service.ts:119-193](), [packages/backend/src/services/llm/ai-sdk-client.ts:128-545](), [packages/backend/src/services/decision-loop/decision-loop-service.ts:109-272]()

---

## Tool Execution Pipeline

**Tool Aggregation and Execution**

```mermaid
graph TB
    subgraph "Tool Sources"
        SystemTools["System Tools<br/>Project Config<br/>getSystemTools()"]
        ClientTools["Client Tools<br/>SDK Registry<br/>dto.tools"]
        MCPTools["MCP Tools<br/>Server Connections<br/>getThreadMCPClients()"]
        UITools["UI Component Tools<br/>Registered Components<br/>show_component_*"]
    end
    
    subgraph "ThreadsService.advanceThread()"
        Aggregate["Aggregate All Tools<br/>convertMetadataToTools()"]
        FormatPrompt["Add to System Prompt<br/>Available tools list"]
    end
    
    subgraph "runDecisionLoop()"
        StreamLLM["Stream LLM Response"]
        DetectToolCall["Detect Tool Call<br/>toolCallRequest"]
    end
    
    subgraph "Tool Execution"
        IsSystem{"System Tool?<br/>isSystemToolCall()"}
        ExecuteSystem["callSystemTool()<br/>Server-side execution"]
        ClientWait["Emit awaiting_input<br/>Client-side execution"]
    end
    
    SystemTools --> Aggregate
    ClientTools --> Aggregate
    MCPTools --> Aggregate
    UITools --> Aggregate
    
    Aggregate --> FormatPrompt
    FormatPrompt --> StreamLLM
    StreamLLM --> DetectToolCall
    
    DetectToolCall --> IsSystem
    IsSystem -->|"Yes"| ExecuteSystem
    IsSystem -->|"No"| ClientWait
    
    ExecuteSystem -->|"Result"| StreamLLM
    ClientWait -->|"User submits result"| StreamLLM
```

**Tool Aggregation:** `ThreadsService.advanceThread()` aggregates tools from four sources:
1. **System Tools:** Configured in project settings (e.g., MCP server tools)
2. **Client Tools:** Registered in the SDK and sent with the run request
3. **MCP Tools:** Dynamically registered from connected MCP servers
4. **UI Tools:** Auto-generated from registered components (`show_component_<name>`)

**Standard Parameters:** The backend adds `_tambo_statusMessage` and `_tambo_completionStatusMessage` to all tools via `addParametersToTools()`. These parameters enable custom status messages during tool execution.

**Server-Side Execution:** System tools (MCP and project tools) execute server-side. `callSystemTool()` invokes the tool, validates the response, and recursively continues the LLM conversation with the result.

**Client-Side Execution:** Client tools execute in the browser. When detected, the run enters `WAITING` state and emits an `awaiting_input` event with tool details. The client submits results via `POST /v1/threads/:id/runs` with `tool_result` content.

**Tool Call Tracking:** `ClientToolCallTracker` tracks pending client-side tool calls during streaming. It detects `TOOL_CALL_START` and `TOOL_RESULT` events to determine which tools are awaiting results.

**Sources:** [apps/api/src/threads/threads.service.ts:737-1086](), [apps/api/src/v1/v1-client-tools.ts:1-136](), [packages/backend/src/services/tool/tool-service.ts:1-267]()

---

## Database Schema and Operations

**Database Schema (Drizzle ORM)**

```mermaid
erDiagram
    threads ||--o{ messages : contains
    threads ||--o{ runs : has
    threads }o--|| projects : "belongs to"
    messages }o--|| messages : "parent/child"
    runs }o--|| runs : "previous run"
    
    threads {
        string id PK
        string projectId FK
        string contextKey
        string name
        V1RunStatus runStatus
        string currentRunId
        string lastCompletedRunId
        jsonb pendingToolCallIds
        boolean lastRunCancelled
        jsonb lastRunError
        jsonb metadata
        timestamp createdAt
        timestamp updatedAt
    }
    
    messages {
        string id PK
        string threadId FK
        string parentMessageId FK
        MessageRole role
        jsonb content
        jsonb componentDecision
        jsonb componentState
        jsonb toolCallRequest
        string toolCallId
        boolean isCancelled
        jsonb metadata
        timestamp createdAt
    }
    
    runs {
        string id PK
        string threadId FK
        string previousRunId FK
        string model
        jsonb requestParams
        V1RunStatus status
        boolean isCancelled
        jsonb error
        jsonb metadata
        timestamp createdAt
        timestamp completedAt
    }
```

**Core Tables:**
- **threads:** Conversation threads with run status tracking (`runStatus`, `currentRunId`, `pendingToolCallIds`)
- **messages:** Individual messages with content, component decisions, and tool calls
- **runs:** Run records for tracking execution history and concurrency

**Operations Module:** The `@tambo-ai-cloud/db` package exports an `operations` namespace with typed CRUD functions:

| Function | Purpose |
|----------|---------|
| `operations.createThread()` | Create new thread with metadata |
| `operations.getThreadForProjectId()` | Fetch thread with messages and access control |
| `operations.acquireRunLock()` | Atomically acquire run lock (IDLE → WAITING) |
| `operations.releaseRunLockIfCurrent()` | Release lock only if current run matches |
| `operations.addMessage()` | Insert message with content validation |
| `operations.updateThread()` | Update thread metadata and status |
| `operations.listThreadsPaginated()` | Cursor-based pagination for threads |
| `operations.listMessagesPaginated()` | Cursor-based pagination for messages |
| `operations.clearPendingToolCalls()` | Atomic clear with state verification |

**Optimistic Locking:** Run operations use optimistic locking to prevent race conditions. `acquireRunLock()` uses `UPDATE ... WHERE runStatus = 'idle'` to atomically acquire locks. If the update affects 0 rows, the lock acquisition fails.

**Pagination:** Pagination uses compound cursors `{createdAt, id}` for stable ordering. The API fetches `limit + 1` records and sets `hasMore` based on whether extra records exist.

**Sources:** [packages/db/src/schema.ts:1-500](), [packages/db/src/operations/thread.ts:1-820](), [apps/api/src/v1/v1.service.ts:394-581]()

---

## Component State Management

**Component State Update Flow**

```mermaid
sequenceDiagram
    participant Client as React SDK
    participant V1Controller as V1Controller
    participant V1Service as V1Service<br/>updateComponentState()
    participant DB as Database<br/>operations
    
    Client->>V1Controller: PATCH /v1/threads/:id/components/:cid
    V1Controller->>V1Service: updateComponentState(dto)
    
    V1Service->>DB: Begin Transaction
    V1Service->>DB: SELECT ... FOR UPDATE<br/>Lock thread row
    
    alt Thread is IDLE
        V1Service->>DB: SELECT message with component
        V1Service->>V1Service: Get current componentState
        
        alt JSON Patch Mode
            V1Service->>V1Service: validateJsonPatch(operations)
            V1Service->>V1Service: applyPatch(current, operations)
        else Full Replacement Mode
            V1Service->>V1Service: newState = dto.state
        end
        
        V1Service->>DB: UPDATE message<br/>SET componentState = newState
        V1Service->>DB: COMMIT
        V1Service-->>Client: 200 OK {state: newState}
    else Thread is WAITING or STREAMING
        V1Service->>DB: ROLLBACK
        V1Service-->>Client: 409 Conflict<br/>RUN_ACTIVE
    end
```

**Component State Endpoint:** `PATCH /v1/threads/:threadId/components/:componentId` updates component state with atomic validation. It requires the thread to be `IDLE` to prevent conflicts with active runs.

**Update Modes:**
1. **Full Replacement:** `{state: {...}}` replaces the entire state object
2. **JSON Patch:** `{patch: [{op: "replace", path: "/foo", value: "bar"}]}` applies RFC 6902 JSON Patch operations

**Atomicity:** The update executes in a database transaction with `SELECT ... FOR UPDATE` on the thread row to lock it during the state change. This prevents concurrent runs from starting mid-update.

**Validation:** JSON Patch operations are validated using `fast-json-patch.validate()` before application. Invalid patches return `400 Bad Request` with error details.

**State Persistence:** Component state is stored in `messages.componentState` as a JSONB column. The state is merged with component blocks in message content during API responses.

**Sources:** [apps/api/src/v1/v1.service.ts:973-1127](), [apps/api/src/v1/dto/component-state.dto.ts:1-97]()

---

## Authentication and Authorization

**V1 API Auth Flow**

```mermaid
graph TB
    Client["Client Request"]
    
    subgraph "Guard Chain"
        ApiKeyGuard["ApiKeyGuard<br/>Extract Project ID"]
        BearerTokenGuard["BearerTokenGuard<br/>Optional User Auth"]
        V1ThreadInProjectGuard["V1ThreadInProjectGuard<br/>Verify Thread Access"]
    end
    
    subgraph "Context Resolution"
        GetV1ContextInfo["getV1ContextInfo()<br/>Resolve contextKey"]
        ExtractContextInfo["extractContextInfo()<br/>From JWT or userKey"]
    end
    
    subgraph "Request Execution"
        V1Service["V1Service<br/>Business Logic"]
        Operations["operations<br/>Database Queries"]
    end
    
    Client -->|"x-api-key: sk_..."| ApiKeyGuard
    Client -->|"Authorization: Bearer ..."| BearerTokenGuard
    
    ApiKeyGuard -->|"Set request[ProjectId]"| V1ThreadInProjectGuard
    BearerTokenGuard -->|"Set request[UserToken]"| V1ThreadInProjectGuard
    
    V1ThreadInProjectGuard -->|"Verify thread in project"| GetV1ContextInfo
    GetV1ContextInfo --> ExtractContextInfo
    ExtractContextInfo -->|"contextKey, projectId"| V1Service
    V1Service --> Operations
```

**ApiKeyGuard:** Extracts project API key from `x-api-key` header, validates it against the database, and sets `request[ProjectId]` for downstream guards and services.

**BearerTokenGuard:** Optionally extracts user JWT from `Authorization: Bearer` header. If present, validates the token and sets `request[UserToken]` for user-scoped operations.

**Context Key Resolution:** `getV1ContextInfo()` resolves the effective `contextKey` for database queries:
- If bearer token present: uses token's user ID
- Else if `userKey` query param present: uses `userKey`
- Else: throws `BadRequestException`

**Thread Access Guard:** `V1ThreadInProjectGuard` verifies that the thread ID in the URL belongs to the authenticated project using `operations.ensureThreadByProjectId()`. Returns 404 if not found.

**Input Validation:** All DTOs use `class-validator` decorators (`@IsString()`, `@IsOptional()`, `@IsIn()`, etc.). The global validation pipe automatically validates requests and returns detailed error messages for invalid inputs.

**Sources:** [apps/api/src/v1/guards/v1-thread-in-project-guard.ts:1-82](), [apps/api/src/v1/utils/get-v1-context-info.ts:1-42](), [apps/api/src/projects/guards/apikey.guard.ts:1-100]()

---

## AI Model Configuration

**Model Selection and Provider Configuration**

The API supports multiple LLM providers with project-level configuration stored in the `projects` table:

| Field | Type | Purpose |
|-------|------|---------|
| `defaultLlmProviderName` | `string` | Provider name (openai, anthropic, google, groq, mistral, openai-compatible) |
| `defaultLlmModelName` | `string` | Model identifier (e.g., gpt-4o, claude-3-5-sonnet) |
| `customLlmModelName` | `string` | Override model name for custom deployments |
| `customLlmBaseURL` | `string` | Custom base URL for openai-compatible providers |
| `maxInputTokens` | `number` | Token limit for context window |
| `customLlmParameters` | `jsonb` | Provider-specific parameters (temperature, top_p, etc.) |

**Backend Creation:** `ThreadsService.createTamboBackendForThread()` loads project configuration and instantiates the appropriate provider client:

```typescript
// 1. Fetch project settings
const project = await this.projectsService.findOne(projectId);
const providerName = project.defaultLlmProviderName ?? "openai";
const modelName = project.defaultLlmModelName ?? DEFAULT_OPENAI_MODEL;

// 2. Get provider API key
const apiKey = await this.validateProjectAndProviderKeys(projectId, providerName, modelName);

// 3. Create backend with custom parameters
return await createTamboBackend(apiKey, chainId, userId, {
  provider: providerName,
  model: modelName,
  baseURL: project.customLlmBaseURL,
  maxInputTokens: project.maxInputTokens,
  customLlmParameters: project.customLlmParameters,
});
```

**Custom Parameters:** Projects can specify provider-specific parameters like `temperature`, `top_p`, `reasoningEffort` (for reasoning models), and model-specific settings. These are passed to `AISdkClient` and merged with provider defaults.

**Token Limiting:** `limitTokens()` truncates message history to fit within the model's input token limit. It preserves the system prompt and most recent messages while removing older messages if necessary.

**Sources:** [apps/api/src/threads/threads.service.ts:119-193](), [packages/backend/src/services/llm/ai-sdk-client.ts:158-280]()

---

## V1 API Error Handling

**Error Response Format (RFC 9457 Problem Details)**

The V1 API returns structured error responses following RFC 9457:

```json
{
  "type": "https://tambo.ai/errors/concurrent-run",
  "title": "Concurrent Run Conflict",
  "status": 409,
  "detail": "A run is already active on thread thr_abc123",
  "instance": "/v1/threads/thr_abc123/runs",
  "code": "CONCURRENT_RUN",
  "threadId": "thr_abc123",
  "currentRunId": "run_xyz789"
}
```

**Error Codes:** The V1 API defines error codes in `V1ErrorCodes`:

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `THREAD_NOT_FOUND` | 404 | Thread does not exist or not in project |
| `CONCURRENT_RUN` | 409 | Another run is already active on thread |
| `INVALID_PREVIOUS_RUN` | 400 | previousRunId doesn't match lastCompletedRunId |
| `INVALID_TOOL_RESULT` | 400 | Tool result doesn't match pending tool calls |
| `RUN_ACTIVE` | 409 | Cannot update component state during run |
| `INVALID_JSON_PATCH` | 400 | JSON Patch operations are invalid |
| `VALIDATION_ERROR` | 400 | Request validation failed |

**Concurrent Run Detection:** `V1Service.startRun()` returns `{success: false, error: HttpException}` if lock acquisition fails. The controller throws the error to return 409 Conflict.

**Tool Result Validation:** `validateToolResults()` checks that submitted tool results match `pendingToolCallIds` exactly. Missing or extra tool call IDs return `INVALID_TOOL_RESULT` with details about which IDs are missing/extra.

**Streaming Errors:** During SSE streaming, errors are emitted as `RUN_ERROR` events before closing the stream:

```typescript
const errorEvent: RunErrorEvent = {
  type: EventType.RUN_ERROR,
  message: "An internal error occurred",
  code: "INTERNAL_ERROR",
  timestamp: Date.now(),
};
response.write(`data: ${JSON.stringify(errorEvent)}\n\n`);
```

**Sentry Integration:** Unhandled exceptions during run execution are captured by Sentry with full context (threadId, runId, projectId, model). The client receives a generic error message to avoid leaking internal details.

**Sources:** [apps/api/src/v1/v1.errors.ts:1-100](), [apps/api/src/v1/v1.service.ts:394-557](), [apps/api/src/v1/v1-tool-results.ts:1-185]()

---

## Deployment Configuration

The API requires the following environment variables for deployment:

| Variable | Purpose | Example |
|----------|---------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `JWT_SECRET` | Secret key for JWT signing | `your-secret-key-here` |
| `OPENAI_API_KEY` | OpenAI API authentication | `sk-...` |
| `ANTHROPIC_API_KEY` | Anthropic API authentication | `sk-ant-...` |
| `AWS_S3_BUCKET` | S3 bucket for file storage | `tambo-uploads` |
| `LANGFUSE_PUBLIC_KEY` | Langfuse monitoring key | `pk-...` |
| `SENTRY_DSN` | Sentry error tracking endpoint | `https://...@sentry.io/...` |

**Build Process:** The application uses `nest build` which compiles TypeScript to JavaScript in the `dist/` directory. The build requires Node.js >=22 as specified in the `engines` field.

**Startup Script:** The production start script uses `node dist/apps/api/src/main` with the `--experimental-require-module` flag to enable ESM support in Node.js. This is required for the modern module system used throughout the codebase.

**Health Checks:** The API exposes health check endpoints for monitoring deployment status and database connectivity. These endpoints are used by container orchestration platforms for readiness and liveness probes.

**Sources:** [apps/api/package.json:1-94]()

---

