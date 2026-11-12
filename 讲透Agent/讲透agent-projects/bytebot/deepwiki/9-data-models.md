<!-- source: DeepWiki mcp.deepwiki.com · repo bytebot-ai/bytebot · page 9 Data Models · fetched 2026-10-29 -->

# Data Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/bytebot-agent/prisma/schema.prisma](packages/bytebot-agent/prisma/schema.prisma)
- [packages/bytebot-agent/src/anthropic/anthropic.tools.ts](packages/bytebot-agent/src/anthropic/anthropic.tools.ts)
- [packages/bytebot-agent/src/tasks/dto/create-task.dto.ts](packages/bytebot-agent/src/tasks/dto/create-task.dto.ts)
- [packages/bytebot-ui/src/types/index.ts](packages/bytebot-ui/src/types/index.ts)

</details>



This document provides comprehensive documentation of the data structures, database schema, and type definitions used throughout the Bytebot system. It covers the PostgreSQL database schema, TypeScript interfaces, data transfer objects (DTOs), and shared type definitions that enable communication between services.

## Database Schema

The Bytebot system uses PostgreSQL as its primary database with Prisma as the ORM. The schema defines the core entities and their relationships for task management, message persistence, and file storage.

### Core Entity Models

**Database Entity Relationship Diagram**

The database schema centers around four primary entities: `Task`, `Message`, `Summary`, and `File`, with hierarchical relationships for conversation summarization.

```mermaid
erDiagram
    Task ||--o{ Message : "has many"
    Task ||--o{ File : "has many"  
    Task ||--o{ Summary : "has many"
    Message }o--o| Summary : "belongs to"
    Summary ||--o{ Message : "summarizes"
    Summary }o--o| Summary : "parent-child"
    
    Task {
        string id PK
        string description
        TaskType type
        TaskStatus status
        TaskPriority priority
        Role control
        Role createdBy
        DateTime createdAt
        DateTime updatedAt
        DateTime scheduledFor
        DateTime executedAt
        DateTime completedAt
        DateTime queuedAt
        string error
        Json result
        Json model
    }
    
    Message {
        string id PK
        Json content
        Role role
        DateTime createdAt
        DateTime updatedAt
        string taskId FK
        string summaryId FK
    }
    
    Summary {
        string id PK
        string content
        DateTime createdAt
        DateTime updatedAt
        string taskId FK
        string parentId FK
    }
    
    File {
        string id PK
        string name
        string type
        int size
        string data
        DateTime createdAt
        DateTime updatedAt
        string taskId FK
    }
```

**Sources:** [packages/bytebot-agent/prisma/schema.prisma:43-115]()

### Enumeration Types

The system defines several enums to constrain values and ensure data consistency:

| Enum | Values | Usage |
|------|--------|-------|
| `TaskStatus` | `PENDING`, `RUNNING`, `NEEDS_HELP`, `NEEDS_REVIEW`, `COMPLETED`, `CANCELLED`, `FAILED` | Tracks task lifecycle state |
| `TaskPriority` | `LOW`, `MEDIUM`, `HIGH`, `URGENT` | Prioritizes task execution |
| `TaskType` | `IMMEDIATE`, `SCHEDULED` | Distinguishes execution timing |
| `Role` | `USER`, `ASSISTANT` | Identifies message sender and task control |

**Sources:** [packages/bytebot-agent/prisma/schema.prisma:16-41]()

### Summary Model Hierarchy

The `Summary` model supports hierarchical summarization with self-referential relationships to enable progressive conversation compression:

```mermaid
graph TD
    Summary1["Summary (Parent)"] --> Summary2["Summary (Child 1)"]
    Summary1 --> Summary3["Summary (Child 2)"]
    Summary2 --> Summary4["Summary (Grandchild)"]
    
    Summary1 -.-> Message1["Message Group 1"]
    Summary2 -.-> Message2["Message Group 2"] 
    Summary3 -.-> Message3["Message Group 3"]
    Summary4 -.-> Message4["Message Group 4"]
```

This enables the system to maintain context while managing token limits by creating nested summaries of conversation history.

**Sources:** [packages/bytebot-agent/prisma/schema.prisma:67-81]()

## TypeScript Interfaces

The frontend and shared packages define TypeScript interfaces that correspond to database models with additional client-side properties and computed fields.

### Frontend Data Models

**Client-Side Type Structure**

```mermaid
classDiagram
    class Task {
        +string id
        +string description
        +TaskType type
        +TaskStatus status
        +TaskPriority priority
        +Role control
        +Role createdBy
        +string createdAt
        +string updatedAt
        +string scheduledFor
        +string executedAt
        +string completedAt
        +string queuedAt
        +string error
        +unknown result
        +Model model
        +User user
        +File[] files
    }
    
    class Message {
        +string id
        +MessageContentBlock[] content
        +Role role
        +string taskId
        +string createdAt
        +boolean take_over
    }
    
    class GroupedMessages {
        +Role role
        +Message[] messages
        +boolean take_over
    }
    
    class Model {
        +string provider
        +string name
        +string title
    }
    
    Task --> Model : uses
    Task --> File : contains
    Message --> MessageContentBlock : contains
    GroupedMessages --> Message : groups
```

**Sources:** [packages/bytebot-ui/src/types/index.ts:78-98](), [packages/bytebot-ui/src/types/index.ts:8-29]()

### File Handling Types

The system defines two file interfaces for different contexts:

| Interface | Purpose | Fields |
|-----------|---------|--------|
| `FileWithBase64` | Client-side file upload | `name`, `base64`, `type`, `size` |
| `File` | Persisted database file | `id`, `name`, `type`, `size`, `data`, `createdAt`, `updatedAt`, `taskId` |

**Sources:** [packages/bytebot-ui/src/types/index.ts:60-76]()

## Data Transfer Objects

The backend uses DTOs for request validation and type safety during API operations.

### Task Management DTOs

**Task Creation and Update DTOs**

```mermaid
classDiagram
    class CreateTaskDto {
        +string description
        +TaskType type
        +Date scheduledFor
        +TaskPriority priority
        +Role createdBy
        +any model
        +TaskFileDto[] files
    }
    
    class TaskFileDto {
        +string name
        +string base64
        +string type
        +number size
    }
    
    class UpdateTaskDto {
        +TaskStatus status
        +string error
        +unknown result
        +DateTime executedAt
        +DateTime completedAt
    }
    
    class AddTaskMessageDto {
        +string message
    }
    
    CreateTaskDto --> TaskFileDto : contains
```

The DTOs include validation decorators from `class-validator`:
- `@IsNotEmpty()` for required fields like `description`
- `@IsOptional()` for optional fields like `scheduledFor`  
- `@ValidateNested()` for nested object validation with `TaskFileDto[]`

**Sources:** [packages/bytebot-agent/src/tasks/dto/create-task.dto.ts:31-60](), [packages/bytebot-agent/src/tasks/dto/update-task.dto.ts]()

## Message Content Structure

Messages in Bytebot follow Anthropic's content blocks structure, stored as JSON in the database and typed via the shared package. The `@bytebot/shared` package provides comprehensive type definitions for all content block variants.

### Content Block Type Hierarchy

**MessageContentBlock Type Structure**

```mermaid
graph TD
    MessageContentBlock["MessageContentBlock<br/>(from @bytebot/shared)"] 
    
    TextContentBlock["TextContentBlock<br/>type: 'text'<br/>text: string"]
    ImageContentBlock["ImageContentBlock<br/>type: 'image'<br/>source: {media_type, data}"]
    DocumentContentBlock["DocumentContentBlock<br/>type: 'document'<br/>source: {media_type, data}"]
    ToolUseContentBlock["ToolUseContentBlock<br/>type: 'tool_use'<br/>name: string, input: object"]
    ToolResultContentBlock["ToolResultContentBlock<br/>type: 'tool_result'<br/>tool_use_id: string"]
    ThinkingContentBlock["ThinkingContentBlock<br/>type: 'thinking'<br/>thinking: string"]
    UserActionContentBlock["UserActionContentBlock<br/>type: 'user_action'<br/>content: ContentBlock[]"]
    
    MessageContentBlock --> TextContentBlock
    MessageContentBlock --> ImageContentBlock
    MessageContentBlock --> DocumentContentBlock
    MessageContentBlock --> ToolUseContentBlock
    MessageContentBlock --> ToolResultContentBlock
    MessageContentBlock --> ThinkingContentBlock
    MessageContentBlock --> UserActionContentBlock
```

### Computer Tool Use Types

The system defines specialized tool use blocks for computer automation:

**Computer Tool Use Content Blocks**

```mermaid
graph TD
    ComputerToolUseContentBlock["ComputerToolUseContentBlock<br/>(Union Type)"]
    
    MouseTools["Mouse Tools<br/>MoveMouseToolUseBlock<br/>ClickMouseToolUseBlock<br/>DragMouseToolUseBlock<br/>ScrollToolUseBlock"]
    
    KeyboardTools["Keyboard Tools<br/>TypeKeysToolUseBlock<br/>TypeTextToolUseBlock<br/>PasteTextToolUseBlock"]
    
    SystemTools["System Tools<br/>ScreenshotToolUseBlock<br/>ApplicationToolUseBlock<br/>WaitToolUseBlock"]
    
    FileTools["File Tools<br/>WriteFileToolUseBlock<br/>ReadFileToolUseBlock"]
    
    ComputerToolUseContentBlock --> MouseTools
    ComputerToolUseContentBlock --> KeyboardTools
    ComputerToolUseContentBlock --> SystemTools
    ComputerToolUseContentBlock --> FileTools
```

Content blocks are stored as JSON arrays in the database `Message.content` field and consumed by both the frontend chat interface and AI model processing.

**Sources:** [packages/shared/src/types/messageContent.types.ts:4-258](), [packages/bytebot-agent/prisma/schema.prisma:91]()

## Computer Action Types

The system defines comprehensive types for computer automation actions that correspond to desktop control operations.

### Computer Action Type Structure

**Computer Action Definitions**

```mermaid
graph TD
    ComputerAction["ComputerAction<br/>(Union Type)"]
    
    MouseActions["Mouse Actions<br/>MoveMouseAction<br/>ClickMouseAction<br/>DragMouseAction<br/>ScrollAction<br/>PressMouseAction<br/>TraceMouseAction"]
    
    KeyboardActions["Keyboard Actions<br/>TypeKeysAction<br/>TypeTextAction<br/>PasteTextAction<br/>PressKeysAction"]
    
    SystemActions["System Actions<br/>ScreenshotAction<br/>WaitAction<br/>CursorPositionAction<br/>ApplicationAction"]
    
    FileActions["File Actions<br/>WriteFileAction<br/>ReadFileAction"]
    
    ComputerAction --> MouseActions
    ComputerAction --> KeyboardActions
    ComputerAction --> SystemActions
    ComputerAction --> FileActions
```

These types are used by `ComputerUseService` in the desktop service to perform actual desktop automation, and are validated using DTOs and pipes.

**Sources:** [packages/shared/src/types/computerAction.types.ts:109-125](), [packages/bytebotd/src/computer-use/dto/computer-action.dto.ts:223-239]()

## Data Flow and Type Mapping

**System Data Flow Architecture**

```mermaid
flowchart TD
    subgraph "Frontend (bytebot-ui)"
        UITypes["UI Types<br/>Task, Message, Model<br/>GroupedMessages"]
        taskUtils["taskUtils.ts<br/>fetchTasks(), startTask()<br/>addMessage()"]
        useChatSession["useChatSession.ts<br/>WebSocket Management"]
    end
    
    subgraph "Backend (bytebot-agent)"
        TasksController["TasksController<br/>/api/tasks endpoints"]
        TasksService["TasksService<br/>create(), findAll()<br/>update()"]
        DTOs["DTOs<br/>CreateTaskDto<br/>AddTaskMessageDto"]
        PrismaModels["Prisma Models<br/>Task, Message, Summary, File"]
        AgentProcessor["AgentProcessor<br/>Task Execution Engine"]
    end
    
    subgraph "Desktop Service (bytebotd)"
        ComputerUseService["ComputerUseService<br/>action() method"]
        ComputerActionDtos["Computer Action DTOs<br/>Validation Pipeline"]
    end
    
    subgraph "Database"
        PostgreSQL["PostgreSQL<br/>Prisma Schema Tables"]
    end
    
    subgraph "Shared Package"
        SharedTypes["@bytebot/shared<br/>MessageContentBlock<br/>ComputerAction"]
    end
    
    taskUtils -->|"HTTP POST"| TasksController
    TasksController --> TasksService
    TasksService -->|"Validation"| DTOs
    DTOs --> PrismaModels
    PrismaModels -->|"Prisma ORM"| PostgreSQL
    
    AgentProcessor -->|"Computer Actions"| ComputerUseService
    ComputerUseService --> ComputerActionDtos
    
    SharedTypes -.->|"Import"| UITypes
    SharedTypes -.->|"Import"| AgentProcessor
    SharedTypes -.->|"Import"| ComputerUseService
    
    useChatSession -->|"WebSocket"| TasksService
```

**Sources:** [packages/bytebot-ui/src/utils/taskUtils.ts:1-260](), [packages/bytebot-agent/src/tasks/tasks.service.ts:1-393](), [packages/bytebotd/src/computer-use/computer-use.service.ts:25-507]()

## Tool Definitions and Computer Actions

The system defines tools that the AI agent can use to interact with the desktop environment:

```mermaid
graph LR
    subgraph "Agent Tools"
        AgentToolsDef["agentTools<br/>Tool Definitions"]
        AnthropicTools["anthropicTools<br/>Anthropic.Tool[]"]
    end
    
    subgraph "Computer Actions"
        MouseActions["Mouse Tools<br/>moveMouseTool, clickMouseTool,<br/>dragMouseTool, scrollTool"]
        KeyboardActions["Keyboard Tools<br/>typeKeysTool, pressKeysTool,<br/>typeTextTool, pasteTextTool"]
        SystemActions["System Tools<br/>screenshotTool, waitTool,<br/>applicationTool"]
        TaskActions["Task Tools<br/>setTaskStatusTool,<br/>createTaskTool"]
    end
    
    AgentToolsDef --> AnthropicTools
    AnthropicTools --> MouseActions
    AnthropicTools --> KeyboardActions  
    AnthropicTools --> SystemActions
    AnthropicTools --> TaskActions
```

Tool definitions are converted from generic agent tools to Anthropic-specific format and exposed as individual exports for type safety.

**Sources:** [packages/bytebot-agent/src/anthropic/anthropic.tools.ts:7-54]()

---

