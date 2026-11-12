<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-voice-agent-sdk-sample · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This document provides an introduction to the OpenAI Voice Agent SDK Sample App, a reference implementation demonstrating how to build voice-enabled conversational agents using the OpenAI Agents SDK. For detailed setup instructions, see [Getting Started](#2), and for in-depth architectural details, see [System Architecture](#3).

## Purpose and Scope

The OpenAI Voice Agent SDK Sample App serves as a foundation for developers to create customizable voice-enabled conversational assistants. It demonstrates best practices for implementing real-time audio processing, multi-turn conversations, streaming responses, and function calling capabilities using OpenAI's APIs.

Sources: [README.md:1-17]()

## Key Features

The sample application showcases several key capabilities essential for modern voice agent applications:

- **Multi-turn conversation handling**: Support for contextual, ongoing dialogues
- **Push-to-talk audio mode**: Real-time voice input processing
- **Function calling**: Ability for the agent to execute actions or retrieve information
- **Streaming responses & tool calls**: Progressive display of agent responses

These features are implemented through a combination of frontend and backend components working together to provide a seamless user experience.

Sources: [README.md:10-15]()

## System Architecture

The application follows a client-server architecture with real-time communication capabilities:

```mermaid
flowchart TB
    subgraph "Client"
        frontend["Next.js Frontend"]
        websocketClient["WebSocket Client"]
        audioRecording["Audio Recording"]
    end
    
    subgraph "Server"
        backend["FastAPI Backend"]
        websocketServer["WebSocket Server"]
        agentsSDK["OpenAI Agents SDK"]
    end
    
    subgraph "External"
        openAI["OpenAI API"]
    end
    
    frontend --- websocketClient
    audioRecording --- frontend
    websocketClient <---> websocketServer
    websocketServer --- backend
    backend --- agentsSDK
    agentsSDK --- openAI
```

### Client Components

- **Next.js Frontend**: Provides the user interface for interaction with the voice agent
- **WebSocket Client**: Manages real-time communication with the server
- **Audio Recording**: Handles capture and transmission of user voice input

### Server Components

- **FastAPI Backend**: Processes requests and manages application logic
- **WebSocket Server**: Enables bidirectional, real-time communication
- **OpenAI Agents SDK**: Interfaces with OpenAI's APIs for voice processing and language model interaction

Sources: [README.md:8-9]()

## Communication Flow

The following diagram illustrates the interaction pattern between system components during a typical conversation:

```mermaid
sequenceDiagram
    participant User
    participant Frontend as "Next.js Frontend"
    participant Backend as "FastAPI Backend"
    participant OpenAI as "OpenAI API"
    
    User->>Frontend: Initiate push-to-talk
    Frontend->>Backend: Send audio data via WebSocket
    Backend->>OpenAI: Process audio with Agents SDK
    
    OpenAI-->>Backend: Stream response
    
    loop Streaming Response
        Backend-->>Frontend: Stream text/tool calls
        Frontend-->>User: Display streaming response
    end
    
    opt Function Calling
        OpenAI->>Backend: Tool/Function call request
        Backend->>Backend: Execute function
        Backend->>OpenAI: Return function result
        OpenAI-->>Backend: Continue streaming response
        Backend-->>Frontend: Stream updated response
        Frontend-->>User: Display updated response
    end
```

This real-time, bidirectional communication enables the responsive experience necessary for effective voice agents.

Sources: [README.md:8-15]()

## Frontend Architecture

The user interface is composed of several key components that work together to provide a cohesive experience:

```mermaid
graph TD
    App["App"] --> Layout["Layout"]
    Layout --> Header["Header Component"]
    Layout --> Conversation["Conversation Component"]
    Layout --> Composer["Composer Component"]
    
    Conversation --> TextMessage["TextMessage Component"]
    Conversation --> ToolCall["Tool Call Component"]
    
    Composer --> TextInput["Text Input"]
    Composer --> AudioChat["Audio Chat Integration"]
    
    Header --> AgentName["Agent Name Display"]
    Header --> AudioPlayback["Audio Playback"]
    Header --> ResetButton["Reset Conversation Button"]
```

For more detailed information about these components, see [Frontend Components](#5).

## Technology Stack

The application leverages the following technologies:

| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | Next.js | User interface and client-side logic |
| Backend | FastAPI | API server and WebSocket endpoint |
| Communication | WebSockets | Real-time bidirectional data exchange |
| AI Integration | OpenAI Agents SDK | Interface to OpenAI's API services |

Sources: [README.md:4-6]()

## Getting Started

To use this application, you'll need:

- An OpenAI API key
- Node.js and npm
- The `uv` package manager

For complete setup instructions, see the [Getting Started](#2) section.

Sources: [README.md:19-61]()

## Development Workflow

The application uses a streamlined development workflow:

```mermaid
flowchart LR
    clone["Clone Repository"] --> setupEnv["Set OpenAI API Key"]
    setupEnv --> installDeps["Install Dependencies (make sync)"]
    installDeps --> runApp["Run Application (make serve)"]
    runApp --> access["Access at localhost:3000"]
```

For detailed development guidelines, see the [Development Guide](#8).

Sources: [README.md:40-61]()

## Customization Opportunities

This sample application is designed as a starting point that developers can customize to their specific requirements. Common customization areas include:

- Adding domain-specific function calls
- Customizing the conversation UI
- Extending the agent's capabilities
- Integrating with additional services or APIs

For information on extending the application with function calling, see [Function Calling](#7).

Sources: [README.md:17]()

---

