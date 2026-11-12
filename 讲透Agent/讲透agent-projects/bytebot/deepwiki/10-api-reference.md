<!-- source: DeepWiki mcp.deepwiki.com · repo bytebot-ai/bytebot · page 10 API Reference · fetched 2026-10-29 -->

# API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/src/agent/agent.processor.ts](packages/bytebot-agent/src/agent/agent.processor.ts)
- [packages/bytebot-agent/src/tasks/tasks.controller.ts](packages/bytebot-agent/src/tasks/tasks.controller.ts)
- [packages/bytebot-agent/src/tasks/tasks.service.ts](packages/bytebot-agent/src/tasks/tasks.service.ts)
- [packages/bytebot-ui/src/hooks/useChatSession.ts](packages/bytebot-ui/src/hooks/useChatSession.ts)
- [packages/bytebotd/src/computer-use/computer-use.service.ts](packages/bytebotd/src/computer-use/computer-use.service.ts)
- [packages/bytebotd/src/computer-use/dto/base.dto.ts](packages/bytebotd/src/computer-use/dto/base.dto.ts)
- [packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts](packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts)
- [packages/bytebotd/src/computer-use/dto/computer-action.dto.ts](packages/bytebotd/src/computer-use/dto/computer-action.dto.ts)
- [packages/bytebotd/src/mcp/computer-use.tools.ts](packages/bytebotd/src/mcp/computer-use.tools.ts)
- [packages/shared/src/types/computerAction.types.ts](packages/shared/src/types/computerAction.types.ts)
- [packages/shared/src/types/messageContent.types.ts](packages/shared/src/types/messageContent.types.ts)
- [packages/shared/src/utils/computerAction.utils.ts](packages/shared/src/utils/computerAction.utils.ts)
- [packages/shared/src/utils/messageContent.utils.ts](packages/shared/src/utils/messageContent.utils.ts)

</details>



This document provides a comprehensive reference for all HTTP and WebSocket APIs exposed by the Bytebot system. It covers the REST API endpoints for task management, the Computer Use API for desktop automation, and the WebSocket API for real-time event subscriptions.

For detailed endpoint specifications, see:
- Tasks REST API: [#10.1](#10.1)
- Computer Use API: [#10.2](#10.2)
- WebSocket API: [#10.3](#10.3)

For information about the data models used in these APIs, see [Data Models](#9).

---

## API Architecture Overview

The Bytebot system exposes three distinct API surfaces across two backend services:

**bytebot-agent (Port 9991):**
- **Tasks REST API**: CRUD operations for tasks, messages, and task control
- **WebSocket API**: Real-time task and message events via Socket.IO

**bytebotd (Port 9990):**
- **Computer Use API**: Desktop automation actions and screenshots

**bytebot-ui (Port 9992)** acts as a unified proxy layer, routing requests to the appropriate backend service.

```mermaid
graph TB
    subgraph "Client Layer"
        Browser["Web Browser / API Client"]
    end
    
    subgraph "bytebot-ui (Port 9992)"
        UIProxy["/api/proxy/tasks<br/>HTTP Proxy"]
        WSProxy["/api/proxy/tasks<br/>WebSocket Proxy"]
    end
    
    subgraph "bytebot-agent (Port 9991)"
        TasksController["TasksController<br/>/tasks/*"]
        TasksGateway["TasksGateway<br/>Socket.IO Server"]
        
        TasksService["TasksService"]
        MessagesService["MessagesService"]
    end
    
    subgraph "bytebotd (Port 9990)"
        ComputerUseController["ComputerUseController<br/>/computer-use"]
        ComputerUseService["ComputerUseService"]
    end
    
    subgraph "Data Layer"
        PostgreSQL[("PostgreSQL<br/>Tasks, Messages,<br/>Summaries, Files")]
    end
    
    Browser -->|"GET/POST/PATCH/DELETE"| UIProxy
    Browser -->|"Socket.IO Events"| WSProxy
    
    UIProxy -->|"HTTP"| TasksController
    WSProxy -->|"WebSocket"| TasksGateway
    
    TasksController --> TasksService
    TasksController --> MessagesService
    TasksGateway --> TasksService
    
    TasksService --> PostgreSQL
    MessagesService --> PostgreSQL
    
    TasksService -.->|"POST /computer-use"| ComputerUseController
    ComputerUseController --> ComputerUseService
    
    ComputerUseService -.->|"Desktop Automation"| Desktop["XFCE Desktop<br/>NutJS / uiohook"]
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts](), [packages/bytebotd/src/computer-use/computer-use.service.ts]()

---

## Base URLs and Service Endpoints

### Development Environment

| Service | Base URL | Purpose |
|---------|----------|---------|
| **bytebot-ui** | `http://localhost:9992` | Unified frontend and API proxy |
| **bytebot-agent** | `http://localhost:9991` | Task orchestration and AI agent |
| **bytebotd** | `http://localhost:9990` | Desktop automation execution |

### Production (via Proxy)

When accessing through **bytebot-ui**, all backend services are proxied:

| API Surface | Proxied Path | Target Service |
|-------------|--------------|----------------|
| Tasks REST API | `/api/proxy/tasks/*` | `bytebot-agent:9991/tasks/*` |
| WebSocket API | `/api/proxy/tasks` (Socket.IO) | `bytebot-agent:9991` |
| Computer Use API | Direct access not proxied | `bytebot-agent` calls internally |

**Sources:** [packages/bytebot-ui/src/server.ts]()

---

## API Surface Breakdown

### Tasks REST API Endpoints

The Tasks REST API provides full CRUD operations for task management:

```mermaid
graph LR
    subgraph "Task Lifecycle Endpoints"
        CreateTask["POST /tasks<br/>CreateTaskDto"]
        GetTasks["GET /tasks<br/>?page&limit&status"]
        GetTask["GET /tasks/:id"]
        DeleteTask["DELETE /tasks/:id"]
    end
    
    subgraph "Task Control Endpoints"
        TakeOver["POST /tasks/:id/takeover<br/>Transfer to USER control"]
        Resume["POST /tasks/:id/resume<br/>Transfer to ASSISTANT control"]
        Cancel["POST /tasks/:id/cancel<br/>Cancel execution"]
    end
    
    subgraph "Message Endpoints"
        GetMessages["GET /tasks/:id/messages<br/>Paginated messages"]
        AddMessage["POST /tasks/:id/messages<br/>Add user guidance"]
        GetRaw["GET /tasks/:id/messages/raw<br/>Unprocessed messages"]
        GetProcessed["GET /tasks/:id/messages/processed<br/>Grouped messages"]
    end
    
    subgraph "Model Metadata"
        GetModels["GET /tasks/models<br/>Available AI models"]
    end
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:1-194]()

### Computer Use API Actions

The Computer Use API accepts action objects via `POST /computer-use`:

```mermaid
graph TB
    subgraph "Mouse Actions"
        MoveMouse["move_mouse<br/>MoveMouseAction"]
        TraceMouse["trace_mouse<br/>TraceMouseAction"]
        ClickMouse["click_mouse<br/>ClickMouseAction"]
        PressMouse["press_mouse<br/>PressMouseAction"]
        DragMouse["drag_mouse<br/>DragMouseAction"]
        Scroll["scroll<br/>ScrollAction"]
    end
    
    subgraph "Keyboard Actions"
        TypeKeys["type_keys<br/>TypeKeysAction"]
        PressKeys["press_keys<br/>PressKeysAction"]
        TypeText["type_text<br/>TypeTextAction"]
        PasteText["paste_text<br/>PasteTextAction"]
    end
    
    subgraph "Observation Actions"
        Screenshot["screenshot<br/>ScreenshotAction"]
        CursorPos["cursor_position<br/>CursorPositionAction"]
    end
    
    subgraph "Application Actions"
        OpenApp["application<br/>ApplicationAction"]
        Wait["wait<br/>WaitAction"]
    end
    
    subgraph "File Operations"
        WriteFile["write_file<br/>WriteFileAction"]
        ReadFile["read_file<br/>ReadFileAction"]
    end
    
    ComputerAction["ComputerAction<br/>(Union Type)"] --> MoveMouse
    ComputerAction --> TraceMouse
    ComputerAction --> ClickMouse
    ComputerAction --> PressMouse
    ComputerAction --> DragMouse
    ComputerAction --> Scroll
    ComputerAction --> TypeKeys
    ComputerAction --> PressKeys
    ComputerAction --> TypeText
    ComputerAction --> PasteText
    ComputerAction --> Screenshot
    ComputerAction --> CursorPos
    ComputerAction --> OpenApp
    ComputerAction --> Wait
    ComputerAction --> WriteFile
    ComputerAction --> ReadFile
```

**Sources:** [packages/shared/src/types/computerAction.types.ts:1-126](), [packages/bytebotd/src/computer-use/dto/computer-action.dto.ts:1-240]()

### WebSocket Event Types

The WebSocket API uses Socket.IO for bidirectional communication:

| Event Direction | Event Name | Payload | Purpose |
|----------------|------------|---------|---------|
| **Client → Server** | `join_task` | `{ taskId: string }` | Subscribe to task updates |
| **Client → Server** | `leave_task` | `{ taskId: string }` | Unsubscribe from task updates |
| **Server → Client** | `task_created` | `Task` | New task created (global) |
| **Server → Client** | `task_updated` | `Task` | Task state changed (room-scoped) |
| **Server → Client** | `task_deleted` | `{ taskId: string }` | Task deleted (global) |
| **Server → Client** | `new_message` | `Message` | New message added (room-scoped) |

**Sources:** [packages/bytebot-agent/src/tasks/tasks.gateway.ts](), [packages/bytebot-ui/src/hooks/useWebSocket.ts]()

---

## Core Type System

The API uses a shared type system defined in the `@bytebot/shared` package:

### Request/Response Type Flow

```mermaid
graph TB
    subgraph "Client Request Types"
        CreateTaskDto["CreateTaskDto<br/>description, model,<br/>files[], priority"]
        AddTaskMessageDto["AddTaskMessageDto<br/>message: string"]
        ComputerActionDto["ComputerActionDto<br/>Discriminated union<br/>by action field"]
    end
    
    subgraph "Shared Domain Types"
        Task["Task<br/>id, description, status,<br/>control, model, priority"]
        Message["Message<br/>id, content, role,<br/>taskId, summaryId"]
        MessageContentBlock["MessageContentBlock<br/>Text | Image | Document<br/>ToolUse | ToolResult<br/>Thinking | UserAction"]
    end
    
    subgraph "Response Types"
        TaskResponse["Task<br/>(with files[])"]
        MessageArray["Message[]<br/>(paginated)"]
        GroupedMessages["GroupedMessages[]<br/>(UI-optimized)"]
        ComputerResult["{ image?: string }<br/>| { success, message }"]
    end
    
    CreateTaskDto -->|"TasksService.create()"| TaskResponse
    AddTaskMessageDto -->|"TasksService.addTaskMessage()"| TaskResponse
    ComputerActionDto -->|"ComputerUseService.action()"| ComputerResult
    
    Task -.->|"Persisted to"| PostgreSQL[("PostgreSQL<br/>Task table")]
    Message -.->|"Persisted to"| PostgreSQL
    
    TaskResponse --> Task
    MessageArray --> Message
    Message --> MessageContentBlock
```

**Sources:** [packages/shared/src/types/messageContent.types.ts:1-258](), [packages/bytebot-agent/src/tasks/dto/create-task.dto.ts]()

### MessageContentBlock Type Hierarchy

The `MessageContentBlock` type is a discriminated union used throughout the message system:

| Type | Discriminator | Key Fields | Purpose |
|------|---------------|------------|---------|
| `TextContentBlock` | `type: "text"` | `text: string` | Plain text content |
| `ImageContentBlock` | `type: "image"` | `source: { data, media_type }` | Base64-encoded images |
| `DocumentContentBlock` | `type: "document"` | `source: { data, media_type }`, `name`, `size` | File attachments |
| `ToolUseContentBlock` | `type: "tool_use"` | `name: string`, `input: object`, `id: string` | LLM tool invocations |
| `ToolResultContentBlock` | `type: "tool_result"` | `tool_use_id: string`, `content: []`, `is_error?` | Tool execution results |
| `ThinkingContentBlock` | `type: "thinking"` | `thinking: string`, `signature: string` | Extended thinking (Claude) |
| `UserActionContentBlock` | `type: "user_action"` | `content: []` | Captured user input |

**Sources:** [packages/shared/src/types/messageContent.types.ts:1-258]()

### ComputerAction Type Hierarchy

All desktop automation actions share the `ComputerAction` discriminated union:

```mermaid
graph TB
    subgraph "Action Categories"
        MouseActions["Mouse Actions<br/>move_mouse, trace_mouse,<br/>click_mouse, press_mouse,<br/>drag_mouse, scroll"]
        KeyboardActions["Keyboard Actions<br/>type_keys, press_keys,<br/>type_text, paste_text"]
        ObservationActions["Observation Actions<br/>screenshot,<br/>cursor_position"]
        UtilityActions["Utility Actions<br/>wait, application,<br/>write_file, read_file"]
    end
    
    ComputerAction["ComputerAction<br/>Discriminated by<br/>action: string"] --> MouseActions
    ComputerAction --> KeyboardActions
    ComputerAction --> ObservationActions
    ComputerAction --> UtilityActions
    
    MouseActions -.->|"Coordinates"| CoordinatesType["Coordinates<br/>{ x: number, y: number }"]
    MouseActions -.->|"Button"| ButtonType["Button<br/>'left' | 'right' | 'middle'"]
    KeyboardActions -.->|"Keys"| KeyArray["string[]<br/>Valid key names"]
```

**Sources:** [packages/shared/src/types/computerAction.types.ts:1-126](), [packages/bytebotd/src/computer-use/dto/base.dto.ts:1-38]()

---

## Authentication and Configuration

### Environment Variables

The APIs require the following environment variables:

**bytebot-agent:**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/bytebot
ANTHROPIC_API_KEY=sk-ant-...        # For Claude models
OPENAI_API_KEY=sk-...               # For GPT models
GEMINI_API_KEY=...                  # For Gemini models
BYTEBOT_DESKTOP_BASE_URL=http://localhost:9990  # bytebotd URL
```

**bytebotd:**
```bash
# No API keys required - receives actions from bytebot-agent
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:23-28]()

### Model Selection

Available models are dynamically determined by configured API keys:

```typescript
GET /tasks/models
```

**Response:**
```json
[
  {
    "provider": "anthropic",
    "name": "claude-3-7-sonnet-20250219",
    "title": "Claude 3.7 Sonnet",
    "contextWindow": 200000
  },
  {
    "provider": "openai", 
    "name": "gpt-4o",
    "title": "GPT-4o",
    "contextWindow": 128000
  }
]
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:69-111]()

---

## Request/Response Patterns

### Standard Task Creation Flow

```mermaid
sequenceDiagram
    participant Client
    participant TasksController
    participant TasksService
    participant MessagesService
    participant PostgreSQL
    participant TasksGateway
    
    Client->>TasksController: POST /tasks<br/>CreateTaskDto
    TasksController->>TasksService: create(dto)
    
    TasksService->>PostgreSQL: BEGIN TRANSACTION
    TasksService->>PostgreSQL: INSERT Task
    
    opt Files attached
        TasksService->>PostgreSQL: INSERT Files (base64)
    end
    
    TasksService->>PostgreSQL: INSERT initial Message<br/>(USER, description)
    TasksService->>PostgreSQL: COMMIT
    
    TasksService->>TasksGateway: emitTaskCreated(task)
    TasksGateway-->>Client: task_created event (broadcast)
    
    TasksService-->>TasksController: Task
    TasksController-->>Client: 201 Created<br/>Task
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.service.ts:40-117](), [packages/bytebot-agent/src/tasks/tasks.controller.ts:42-46]()

### Computer Action Execution Flow

```mermaid
sequenceDiagram
    participant AgentProcessor
    participant ComputerUseController
    participant ComputerUseService
    participant NutService
    participant Desktop
    
    AgentProcessor->>ComputerUseController: POST /computer-use<br/>ComputerActionDto
    ComputerUseController->>ComputerUseService: action(params)
    
    alt Screenshot
        ComputerUseService->>NutService: screendump()
        NutService->>Desktop: Capture screen
        Desktop-->>NutService: Raw buffer
        NutService-->>ComputerUseService: PNG buffer
        ComputerUseService-->>ComputerUseController: { image: base64 }
    else Mouse Action
        ComputerUseService->>NutService: mouseMoveEvent(coords)
        NutService->>Desktop: Move cursor
        Desktop-->>NutService: Success
        NutService-->>ComputerUseService: void
        ComputerUseService-->>ComputerUseController: void
    else File Operation
        ComputerUseService->>Desktop: Write to /home/user/Desktop
        Desktop-->>ComputerUseService: Success
        ComputerUseService-->>ComputerUseController: { success, message }
    end
    
    ComputerUseController-->>AgentProcessor: 200 OK<br/>Result
```

**Sources:** [packages/bytebotd/src/computer-use/computer-use.service.ts:31-507](), [packages/bytebot-agent/src/agent/agent.computer-use.ts]()

---

## Validation and Error Handling

### DTO Validation

All endpoints use class-validator decorators for input validation:

**Example: CreateTaskDto**
```typescript
class CreateTaskDto {
  @IsString()
  @IsNotEmpty()
  description: string;

  @IsOptional()
  @ValidateNested()
  @Type(() => BytebotAgentModel)
  model?: BytebotAgentModel;

  @IsOptional()
  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => FileWithBase64)
  files?: FileWithBase64[];
}
```

**Sources:** [packages/bytebot-agent/src/tasks/dto/create-task.dto.ts]()

### Computer Action Validation Pipeline

Computer actions use a discriminated union validation pipe:

```mermaid
graph TB
    Request["POST /computer-use<br/>{ action, ...params }"]
    
    Request --> Pipe["ComputerActionValidationPipe"]
    
    Pipe --> Switch{action field}
    
    Switch -->|"move_mouse"| DTO1["plainToClass<br/>MoveMouseActionDto"]
    Switch -->|"click_mouse"| DTO2["plainToClass<br/>ClickMouseActionDto"]
    Switch -->|"screenshot"| DTO3["plainToClass<br/>ScreenshotActionDto"]
    Switch -->|"unknown"| Error1["BadRequestException<br/>'Unknown action'"]
    
    DTO1 --> Validate1["validate(dto)"]
    DTO2 --> Validate2["validate(dto)"]
    DTO3 --> Validate3["validate(dto)"]
    
    Validate1 --> Check1{errors.length}
    Validate2 --> Check2{errors.length}
    Validate3 --> Check3{errors.length}
    
    Check1 -->|"> 0"| Error2["BadRequestException<br/>validation errors"]
    Check2 -->|"> 0"| Error2
    Check3 -->|"> 0"| Error2
    
    Check1 -->|"= 0"| Valid["Return validated DTO"]
    Check2 -->|"= 0"| Valid
    Check3 -->|"= 0"| Valid
```

**Sources:** [packages/bytebotd/src/computer-use/dto/computer-action-validation.pipe.ts:1-97]()

### Standard Error Responses

All endpoints return standard NestJS error responses:

| Status Code | Error Type | Example |
|-------------|------------|---------|
| 400 | `BadRequestException` | Invalid DTO, validation failure |
| 404 | `NotFoundException` | Task not found |
| 500 | `InternalServerException` | Unexpected errors |

**Response Format:**
```json
{
  "statusCode": 404,
  "message": "Task with ID abc-123 not found",
  "error": "Not Found"
}
```

---

## Pagination and Filtering

### Task List Pagination

```
GET /tasks?page=1&limit=10&status=RUNNING
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | `number` | `1` | Page number (1-indexed) |
| `limit` | `number` | `10` | Items per page |
| `status` | `string` | - | Single status filter |
| `statuses` | `string` | - | Comma-separated statuses |

**Response:**
```json
{
  "tasks": [Task],
  "total": 42,
  "totalPages": 5
}
```

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:48-67](), [packages/bytebot-agent/src/tasks/tasks.service.ts:158-190]()

### Message Pagination

```
GET /tasks/:id/messages?page=1&limit=10
```

Messages are returned in reverse chronological order (newest first).

**Sources:** [packages/bytebot-agent/src/tasks/tasks.controller.ts:118-131]()

---

## Type Guards and Utilities

The `@bytebot/shared` package provides type guard functions for runtime type checking:

**MessageContentBlock Type Guards:**
```typescript
isTextContentBlock(obj): obj is TextContentBlock
isImageContentBlock(obj): obj is ImageContentBlock  
isToolUseContentBlock(obj): obj is ToolUseContentBlock
isComputerToolUseContentBlock(obj): obj is ComputerToolUseContentBlock
isSetTaskStatusToolUseBlock(obj): obj is SetTaskStatusToolUseBlock
```

**ComputerAction Type Guards:**
```typescript
isMoveMouseAction(obj): obj is MoveMouseAction
isClickMouseAction(obj): obj is ClickMouseAction
isScreenshotAction(obj): obj is ScreenshotAction
```

**Converter Functions:**
```typescript
convertComputerActionToToolUseBlock(
  action: ComputerAction,
  toolUseId: string
): ComputerToolUseContentBlock
```

**Sources:** [packages/shared/src/utils/messageContent.utils.ts:1-516](), [packages/shared/src/utils/computerAction.utils.ts:1-343]()

---

## Complete API Reference Sections

For detailed documentation of individual endpoints and events, refer to:

- **[Tasks REST API](#10.1)**: Complete endpoint specifications, request/response schemas, and examples
- **[Computer Use API](#10.2)**: All 17 desktop automation actions with parameter details
- **[WebSocket API](#10.3)**: Event specifications, room management, and real-time patterns

**Sources:** All files listed above

---

