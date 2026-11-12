<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/NeMo-Agent-Toolkit-UI · page 2 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [components/Chat/Chat.tsx](components/Chat/Chat.tsx)
- [pages/api/chat.ts](pages/api/chat.ts)
- [utils/app/helper.ts](utils/app/helper.ts)

</details>



This document details the main chat system architecture of the AIQ Toolkit-UI, focusing on the dual HTTP/WebSocket communication system, message processing pipeline, and content rendering architecture. This covers the foundational components that enable real-time communication with AI agents and workflows.

For specific chat interface components and user interactions, see [Chat System](#2.1). For authentication and user management, see [Authentication](#4). For development setup and deployment, see [Development](#5).

## Architecture Overview

The AIQ Toolkit-UI employs a dual-mode communication architecture that supports both traditional HTTP requests and real-time WebSocket connections for interacting with the AIQ Toolkit Backend. The system is built around a central `Chat` component that orchestrates message handling, state management, and content rendering.

### Core Communication Architecture

```mermaid
graph TB
    subgraph "Frontend Components"
        ChatComponent["Chat.tsx"]
        ChatInput["ChatInput"]
        ChatMessage["MemoizedChatMessage"]
        ChatHeader["ChatHeader"]
    end
    
    subgraph "Communication Layer"
        HTTPHandler["handleSend (HTTP Mode)"]
        WSHandler["handleWebSocketMessage"]
        WSConnection["webSocketRef.current"]
        AbortController["controllerRef.current"]
    end
    
    subgraph "API Layer"
        ChatAPI["pages/api/chat.ts"]
        StreamProcessor["ResponseStream"]
        PayloadBuilder["ChatBody"]
    end
    
    subgraph "Backend Services"
        AIQBackend["AIQ Toolkit Backend"]
        GenerateEndpoint["/generate"]
        ChatEndpoint["/chat"]
        StreamEndpoint["/stream"]
        WSEndpoint["/websocket"]
    end
    
    subgraph "State Management"
        HomeContext["HomeContext"]
        SessionStorage["sessionStorage"]
        ConversationState["selectedConversation"]
    end
    
    ChatComponent --> HTTPHandler
    ChatComponent --> WSHandler
    ChatComponent --> WSConnection
    
    HTTPHandler --> ChatAPI
    WSHandler --> WSConnection
    
    ChatAPI --> GenerateEndpoint
    ChatAPI --> ChatEndpoint
    ChatAPI --> StreamEndpoint
    
    WSConnection --> WSEndpoint
    
    ChatComponent --> HomeContext
    ChatComponent --> SessionStorage
    HomeContext --> ConversationState
    
    StreamProcessor --> ChatComponent
    WSEndpoint --> WSHandler
```

**Sources:** [components/Chat/Chat.tsx:35-936](), [pages/api/chat.ts:13-227]()

### Dual Communication Modes

The system operates in two distinct communication modes, determined by the `webSocketMode` configuration:

| Mode | Implementation | Use Case | Message Flow |
|------|---------------|----------|--------------|
| HTTP | `handleSend` function | Traditional request-response | Client → `/api/chat` → AIQ Backend |
| WebSocket | `connectWebSocket` + `handleWebSocketMessage` | Real-time streaming | Client ↔ WebSocket Server ↔ AIQ Backend |

The mode selection is controlled by `webSocketModeRef.current` and can be toggled through the settings interface.

**Sources:** [components/Chat/Chat.tsx:73-74](), [components/Chat/Chat.tsx:404-489]()

## Message Processing Pipeline

The message processing pipeline handles user input, processes responses, and manages intermediate steps and human-in-the-loop interactions.

### Message Flow Architecture

```mermaid
sequenceDiagram
    participant User
    participant ChatInput
    participant Chat
    participant ProcessingUtils
    participant Backend
    participant StateManager
    
    User->>ChatInput: "Send Message"
    ChatInput->>Chat: "handleSend(message)"
    
    alt HTTP Mode
        Chat->>Backend: "POST /api/chat"
        Backend-->>Chat: "Stream Response"
        Chat->>ProcessingUtils: "processIntermediateMessage"
        ProcessingUtils-->>Chat: "Processed Steps"
    else WebSocket Mode
        Chat->>Backend: "WebSocket Message"
        Backend-->>Chat: "handleWebSocketMessage"
        Chat->>ProcessingUtils: "processIntermediateMessage"
        ProcessingUtils-->>Chat: "Processed Steps"
    end
    
    Chat->>StateManager: "Update Conversation"
    StateManager->>Chat: "State Updated"
    Chat->>User: "Display Response"
```

**Sources:** [components/Chat/Chat.tsx:365-751](), [utils/app/helper.ts:134-217]()

### Content Processing Functions

The system uses several key utility functions for processing different types of content:

- `compressImage`: Reduces image file sizes to under 200KB while maintaining quality
- `processIntermediateMessage`: Handles hierarchical intermediate step data structures
- `generateContentIntermediate`: Converts intermediate steps to HTML details/summary elements
- `fixMalformedHtml`: Sanitizes and repairs malformed HTML content

**Sources:** [utils/app/helper.ts:10-68](), [utils/app/helper.ts:134-217](), [utils/app/helper.ts:261-306](), [utils/app/helper.ts:330-364]()

## WebSocket Communication System

The WebSocket implementation provides real-time bidirectional communication with automatic reconnection and message type handling.

### WebSocket Message Types

```mermaid
graph LR
    subgraph "Outbound Messages"
        UserMessage["webSocketMessageTypes.userMessage"]
        InteractionResponse["webSocketMessageTypes.userInteractionMessage"]
    end
    
    subgraph "Inbound Messages"
        SystemResponse["webSocketMessageTypes.systemResponseMessage"]
        IntermediateStep["webSocketMessageTypes.systemIntermediateMessage"]
        InteractionPrompt["webSocketMessageTypes.systemInteractionMessage"]
        ErrorMessage["type: 'error'"]
    end
    
    subgraph "Processing Functions"
        WSMessageHandler["handleWebSocketMessage"]
        InteractionHandler["handleUserInteraction"]
        IntermediateProcessor["processIntermediateMessage"]
    end
    
    UserMessage --> WSMessageHandler
    InteractionResponse --> WSMessageHandler
    
    WSMessageHandler --> SystemResponse
    WSMessageHandler --> IntermediateStep
    WSMessageHandler --> InteractionPrompt
    WSMessageHandler --> ErrorMessage
    
    IntermediateStep --> IntermediateProcessor
    InteractionPrompt --> InteractionHandler
```

**Sources:** [components/Chat/Chat.tsx:225-362](), [components/Chat/Chat.tsx:87-112](), [utils/app/const.ts]()

### Connection Management

The WebSocket connection lifecycle is managed through several key functions:

- `connectWebSocket`: Establishes connection with retry logic (max 3 attempts)
- `webSocketRef.current`: Maintains the active WebSocket connection reference
- `webSocketConnectedRef.current`: Tracks connection state for reliable message sending

**Sources:** [components/Chat/Chat.tsx:136-211](), [components/Chat/Chat.tsx:71-72]()

## HTTP Communication System

The HTTP mode uses a traditional request-response pattern with streaming support for real-time response delivery.

### HTTP Request Processing

The `/api/chat` endpoint handles different backend schemas:

```mermaid
graph TD
    subgraph "Request Processing"
        ChatAPI["pages/api/chat.ts handler"]
        SchemaDetection["URL.includes('generate') ?"]
        GeneratePayload["{ input_message: string }"]
        ChatPayload["OpenAI Compatible Schema"]
    end
    
    subgraph "Response Handling"
        StreamingCheck["URL.includes('stream') ?"]
        StreamProcessor["ReadableStream Processing"]
        NonStreamProcessor["Direct JSON Response"]
    end
    
    subgraph "Content Processing"
        IntermediateExtraction["<intermediatestep> parsing"]
        ContentDecoding["TextDecoder processing"]
        ErrorHandling["Error response formatting"]
    end
    
    ChatAPI --> SchemaDetection
    SchemaDetection -->|Yes| GeneratePayload
    SchemaDetection -->|No| ChatPayload
    
    ChatAPI --> StreamingCheck
    StreamingCheck -->|Yes| StreamProcessor
    StreamingCheck -->|No| NonStreamProcessor
    
    StreamProcessor --> IntermediateExtraction
    StreamProcessor --> ContentDecoding
    StreamProcessor --> ErrorHandling
```

**Sources:** [pages/api/chat.ts:24-51](), [pages/api/chat.ts:88-188](), [pages/api/chat.ts:190-218]()

## State Management Architecture

The application uses a combination of React Context API and sessionStorage for state persistence across page reloads.

### State Flow

| State Container | Purpose | Key Fields |
|----------------|---------|------------|
| `HomeContext` | Global application state | `selectedConversation`, `conversations`, `messageIsStreaming`, `webSocketConnected` |
| `sessionStorage` | Persistence layer | `selectedConversation`, `conversationsHistory`, `webSocketURL`, `chatCompletionURL` |
| Component State | Local UI state | `currentMessage`, `autoScrollEnabled`, `showSettings` |

The state synchronization ensures that conversation data persists across browser sessions while maintaining real-time updates during active conversations.

**Sources:** [components/Chat/Chat.tsx:37-55](), [components/Chat/Chat.tsx:260-361](), [utils/app/conversation.ts]()

## Content Rendering Pipeline

The system processes various content types including markdown, code blocks, mathematical equations, and interactive charts through a structured rendering pipeline.

### Intermediate Steps Processing

Intermediate steps are processed hierarchically using the `processIntermediateMessage` function, which supports:

- Parent-child relationship tracking via `parent_id` fields
- Step overriding when `intermediateStepOverride` is enabled
- Recursive tree structure for nested intermediate steps
- HTML details/summary element generation for collapsible display

**Sources:** [utils/app/helper.ts:134-217](), [utils/app/helper.ts:261-306]()

This architecture provides a robust foundation for real-time AI agent interactions while maintaining flexibility for different communication patterns and content types.

---

