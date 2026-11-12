<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-assistants-quickstart · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [app/api/assistants/route.ts](app/api/assistants/route.ts)
- [app/components/chat.tsx](app/components/chat.tsx)
- [app/openai.ts](app/openai.ts)

</details>



This document provides a comprehensive overview of the system architecture for the OpenAI Assistants Quickstart. It explains how the frontend components interact with Next.js API routes and how these routes communicate with the OpenAI Assistants API. For information about specific frontend components, see [Frontend Components](#3), and for detailed API endpoint documentation, see [API Endpoints](#4).

## Overview

The OpenAI Assistants Quickstart is a Next.js application that implements a chat interface using the OpenAI Assistants API. The architecture follows a client-server model with:

1. **Frontend Layer**: React components that provide the user interface
2. **API Layer**: Next.js API routes that serve as middleware between the frontend and OpenAI
3. **External Services**: The OpenAI Assistants API that powers the AI functionality

### System Components Diagram

```mermaid
flowchart TD
    subgraph "Client Browser"
        UI["User Interface"]
    end

    subgraph "Next.js Frontend"
        Chat["Chat Component"]
        FileViewer["File Viewer Component"]
    end

    subgraph "Next.js API Routes"
        AssistantAPI["/api/assistants"]
        ThreadsAPI["/api/assistants/threads"]
        MessagesAPI["/api/assistants/threads/[threadId]/messages"]
        ActionsAPI["/api/assistants/threads/[threadId]/actions"]
        FilesAPI["/api/assistants/files"]
        FileDownloadAPI["/api/files/[fileId]"]
    end

    subgraph "OpenAI API"
        Assistants["openai.beta.assistants"]
        Threads["openai.beta.threads"]
        Runs["openai.beta.threads.runs"]
        Files["openai.files"]
        VectorStores["openai.beta.vectorStores"]
    end

    UI --> Chat
    UI --> FileViewer
    
    Chat --> ThreadsAPI
    Chat --> MessagesAPI
    Chat --> ActionsAPI
    Chat --> FileDownloadAPI
    
    FileViewer --> FilesAPI
    
    AssistantAPI --> Assistants
    ThreadsAPI --> Threads
    MessagesAPI --> Threads
    MessagesAPI --> Runs
    ActionsAPI --> Runs
    FilesAPI --> Files
    FilesAPI --> VectorStores
    FileDownloadAPI --> Files
```

Sources: [README.md:58-70](), [app/components/chat.tsx:77-87](), [app/components/chat.tsx:89-101](), [app/api/assistants/route.ts:5-38]()

## Core Components

### Frontend Components

The application has two main frontend components:

1. **Chat Component**: Manages the chat interface, including sending messages, receiving streaming responses, and handling function calls.
2. **File Viewer Component**: Handles file upload, listing, and deletion for the assistant.

### API Routes

The application uses several Next.js API routes to interface with OpenAI:

| API Route | Purpose |
|-----------|---------|
| `/api/assistants` | Creates the assistant with specified tools |
| `/api/assistants/threads` | Creates new conversation threads |
| `/api/assistants/threads/[threadId]/messages` | Sends messages and receives streaming responses |
| `/api/assistants/threads/[threadId]/actions` | Submits function call results back to the assistant |
| `/api/assistants/files` | Manages files for file search capability |
| `/api/files/[fileId]` | Downloads file content |

Sources: [README.md:63-70]()

### OpenAI Integration

The application initializes the OpenAI client simply:

```mermaid
flowchart LR
    App["Application"] --> OpenAIClient["openai.ts"]
    OpenAIClient --> OpenAISDK["OpenAI SDK"]
    OpenAISDK --> OpenAIAPI["OpenAI API"]
```

Sources: [app/openai.ts:1-3]()

## Data Flow

The following diagram shows how data flows through the system during a typical user interaction:

```mermaid
sequenceDiagram
    participant User
    participant Chat as "Chat Component"
    participant API as "Next.js API Routes"
    participant OpenAI as "OpenAI Assistants API"
    
    Note over User, OpenAI: Thread Creation
    User->>Chat: Open chat interface
    Chat->>API: Create new thread
    API->>OpenAI: Create thread
    OpenAI-->>API: Return thread ID
    API-->>Chat: Return thread ID
    
    Note over User, OpenAI: Message Exchange
    User->>Chat: Send message
    Chat->>API: Send message to thread
    API->>OpenAI: Add message to thread & run assistant
    OpenAI-->>API: Stream response events
    API-->>Chat: Stream response events
    Chat->>User: Display messages incrementally
    
    Note over User, OpenAI: Function Calling
    OpenAI->>API: Request function call
    API->>Chat: Forward function call request
    Chat->>Chat: Execute client-side function
    Chat->>API: Submit function result
    API->>OpenAI: Submit tool outputs
    OpenAI-->>API: Continue processing
    API-->>Chat: Stream continued response
    Chat->>User: Display complete response
```

Sources: [app/components/chat.tsx:77-87](), [app/components/chat.tsx:89-101](), [app/components/chat.tsx:103-119](), [app/components/chat.tsx:170-184]()

## Chat Component Architecture

The Chat component is the central piece of the frontend and handles all chat-related functionality:

```mermaid
classDiagram
    class Chat {
        -useState: userInput
        -useState: messages
        -useState: inputDisabled
        -useState: threadId
        +createThread()
        +sendMessage()
        +submitActionResult()
        +handleSubmit()
        +handleReadableStream()
    }
    
    class EventHandlers {
        +handleTextCreated()
        +handleTextDelta()
        +handleImageFileDone()
        +toolCallCreated()
        +toolCallDelta()
        +handleRequiresAction()
        +handleRunCompleted()
    }
    
    class MessageComponents {
        +UserMessage
        +AssistantMessage
        +CodeMessage
    }
    
    Chat --> EventHandlers : uses
    Chat --> MessageComponents : renders
    EventHandlers --> AssistantStream : processes
```

Sources: [app/components/chat.tsx:11-52](), [app/components/chat.tsx:60-132](), [app/components/chat.tsx:134-208]()

### Message Flow in Chat Component

The Chat component processes messages and streaming responses through a series of steps:

1. **Thread Creation**: When a user first opens the chat, a new conversation thread is created via the `/api/assistants/threads` endpoint.
2. **Message Sending**: When a user sends a message, it's added to the thread via the `/api/assistants/threads/[threadId]/messages` endpoint.
3. **Stream Processing**: The response is streamed back from the OpenAI API and processed through various event handlers:
   - `textCreated`: Creates a new assistant message
   - `textDelta`: Appends text to the last message incrementally
   - `imageFileDone`: Shows generated images in the chat
   - `toolCallCreated`/`toolCallDelta`: Handles code interpreter input/output
   - `thread.run.requires_action`: Processes function calls
   - `thread.run.completed`: Re-enables the input form

```mermaid
flowchart TD
    subgraph "Chat Component Stream Handling"
        Stream["AssistantStream"]
        textCreated["handleTextCreated()"]
        textDelta["handleTextDelta()"]
        imageFileDone["handleImageFileDone()"]
        toolCallCreated["toolCallCreated()"]
        toolCallDelta["toolCallDelta()"]
        requiresAction["handleRequiresAction()"]
        runCompleted["handleRunCompleted()"]
    end
    
    Stream -->|"textCreated event"| textCreated
    Stream -->|"textDelta event"| textDelta
    Stream -->|"imageFileDone event"| imageFileDone
    Stream -->|"toolCallCreated event"| toolCallCreated
    Stream -->|"toolCallDelta event"| toolCallDelta
    Stream -->|"thread.run.requires_action event"| requiresAction
    Stream -->|"thread.run.completed event"| runCompleted
    
    textCreated -->|"appendMessage()"| Messages["Chat Messages State"]
    textDelta -->|"appendToLastMessage()"| Messages
    imageFileDone -->|"appendToLastMessage()"| Messages
    toolCallCreated -->|"appendMessage()"| Messages
    toolCallDelta -->|"appendToLastMessage()"| Messages
    requiresAction -->|"functionCallHandler()"| FunctionCall["Execute Function"]
    FunctionCall -->|"submitActionResult()"| API["API Routes"]
    runCompleted -->|"setInputDisabled(false)"| InputForm["Enable Input Form"]
```

Sources: [app/components/chat.tsx:134-208](), [app/components/chat.tsx:217-249]()

## Assistant Creation and Configuration

The assistant is created with specific tools enabled through the `/api/assistants` endpoint:

```mermaid
flowchart LR
    AssistantRoute["/api/assistants"]
    OpenAIClient["openai"]
    AssistantsAPI["openai.beta.assistants"]
    
    AssistantRoute -->|"POST"| OpenAIClient
    OpenAIClient -->|"create()"| AssistantsAPI
    AssistantsAPI -->|"Return assistant ID"| AssistantRoute
    
    subgraph "Assistant Configuration"
        direction TB
        Model["model: gpt-4o"]
        Instructions["instructions"]
        Tools["tools"]
        
        subgraph "Enabled Tools"
            CodeInterpreter["code_interpreter"]
            FunctionCalling["function calling"]
            FileSearch["file_search"]
        end
        
        Tools --> CodeInterpreter
        Tools --> FunctionCalling
        Tools --> FileSearch
    end
```

Sources: [app/api/assistants/route.ts:6-38]()

## Summary

The OpenAI Assistants Quickstart application follows a clean, modular architecture that separates concerns between frontend components and API routes. The frontend components provide the user interface for interacting with the assistant, while the API routes handle the communication with the OpenAI API.

Key architectural features include:

1. **Real-time streaming**: The Chat component processes streaming responses from the OpenAI API in real-time, providing an interactive chat experience.

2. **Function calling**: The application implements the ability for the assistant to call client-side functions and receive the results.

3. **File management**: The application supports uploading and managing files for use with the assistant's file search capability.

4. **Code interpretation**: The Chat component can display and process code outputs from the assistant's code interpreter.

This architecture provides a solid foundation for building AI assistant applications with Next.js and the OpenAI Assistants API.

Sources: [README.md:45-71](), [app/components/chat.tsx:1-282](), [app/api/assistants/route.ts:1-38](), [app/openai.ts:1-3]()

---

