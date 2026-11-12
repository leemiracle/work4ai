<!-- source: DeepWiki mcp.deepwiki.com · repo openai/build-hours · page 8 Realtime Applications · fetched 2026-10-26 -->

# Realtime Applications

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [14-voice-agents/realtime-workspace-agents/README.md](14-voice-agents/realtime-workspace-agents/README.md)
- [9-realtime/openai-realtime-console-example/README.md](9-realtime/openai-realtime-console-example/README.md)

</details>



This section documents the real-time streaming applications in the Build Hours repository that utilize OpenAI's Realtime API for low-latency audio interactions. These systems demonstrate voice-enabled AI applications with streaming audio processing and interactive conversational interfaces.

The realtime applications consist of two distinct implementations: a React-based console for API inspection and development ([Realtime Console](#8.1)) and a Next.js voice agent system with workspace integration ([Voice Agents and Workspace Integration](#8.2)). For agent frameworks without real-time capabilities, see [Agent Systems](#6).

## System Architecture Overview

The realtime applications are built around OpenAI's Realtime API, which provides WebSocket-based streaming for audio input/output and low-latency conversational AI. Both systems share common patterns for audio management, event handling, and tool integration while serving different use cases.

**Realtime Applications Architecture**
```mermaid
graph TD
    subgraph "Realtime Applications"
        Console[Console-9-realtime] --> RealtimeAPI["OpenAI Realtime API<br/>WebSocket Streaming"]
        VoiceAgents[VoiceAgents-14-voice-agents] --> RealtimeAPI
        VoiceAgents --> AgentsSDK["OpenAI Agents SDK<br/>Advanced Patterns"]
    end
    
    subgraph "Core Components"
        RealtimeClient["RealtimeClient<br/>openai-realtime-api-beta"]
        WavTools["WavTools<br/>Audio Management"]
        RelayServer["Relay Server<br/>Node.js Proxy"]
    end
    
    subgraph "Integration Patterns"
        Tools["Tool Calling<br/>get_weather, set_memory"]
        Events["Event Handling<br/>conversation.updated"]
        Audio["Audio Streaming<br/>PCM16 24kHz"]
    end
    
    Console --> RealtimeClient
    Console --> WavTools
    Console --> RelayServer
    VoiceAgents --> RealtimeClient
    
    RealtimeClient --> Tools
    RealtimeClient --> Events
    WavTools --> Audio
    
    RealtimeAPI --> Audio
    RealtimeAPI --> Events
    RealtimeAPI --> Tools
```

Sources: [9-realtime/openai-realtime-console-example/README.md:1-42](), [14-voice-agents/realtime-workspace-agents/README.md:1-30]()

## Key Components and Technologies

Both realtime applications utilize shared core technologies with different implementation approaches and complexity levels.

| Component | Realtime Console | Voice Agents | Purpose |
|-----------|-----------------|--------------|---------|
| **Framework** | React (create-react-app) | Next.js TypeScript | UI Implementation |
| **API Client** | `RealtimeClient` | `RealtimeClient` + Agents SDK | OpenAI Integration |
| **Audio Management** | `WavRecorder`, `WavStreamPlayer` | Built-in SDK tools | Audio I/O |
| **Tool Integration** | Basic (`get_weather`, `set_memory`) | Advanced Agent Tools | Function Calling |
| **Deployment** | Development Console | Production-ready App | Target Use Case |
| **Complexity** | Reference Implementation | Advanced Patterns | Development Approach |

Sources: [9-realtime/openai-realtime-console-example/README.md:14-27](), [14-voice-agents/realtime-workspace-agents/README.md:22-26]()

## Audio Processing Pipeline

Both systems implement similar audio processing patterns using the same underlying libraries and audio formats.

**Audio Processing Flow**
```mermaid
graph LR
    subgraph "Input Processing"
        Microphone["Microphone Input"] --> WavRecorder["WavRecorder<br/>PCM16 24kHz"]
        WavRecorder --> AudioBuffer["Audio Buffer<br/>Int16Array"]
    end
    
    subgraph "Realtime API"
        AudioBuffer --> appendInputAudio["appendInputAudio()"]
        appendInputAudio --> RealtimeWS["Realtime WebSocket"]
        RealtimeWS --> ResponseAudio["Response Audio Stream"]
    end
    
    subgraph "Output Processing"
        ResponseAudio --> WavStreamPlayer["WavStreamPlayer<br/>add16BitPCM()"]
        WavStreamPlayer --> AudioOutput["Audio Output"]
    end
    
    subgraph "Control Flow"
        VAD["Voice Activity Detection"] --> TurnDetection["Turn Detection"]
        Manual["Push-to-Talk"] --> TurnDetection
        TurnDetection --> createResponse["createResponse()"]
        Interrupt["cancelResponse()"] --> WavStreamPlayer
    end
    
    TurnDetection --> RealtimeWS
    createResponse --> RealtimeWS
```

Sources: [9-realtime/openai-realtime-console-example/README.md:144-163](), [9-realtime/openai-realtime-console-example/README.md:285-324](), [9-realtime/openai-realtime-console-example/README.md:326-352]()

## Event Handling and Conversation Management

The realtime systems use an event-driven architecture for managing conversations and handling streaming updates.

**Event System Architecture**
```mermaid
graph TD
    subgraph "Client Events"
        Error["error<br/>Connection failures"]
        Interrupted["conversation.interrupted<br/>User starts speaking"]
        Updated["conversation.updated<br/>Content changes"]
        Appended["conversation.item.appended<br/>Item added"]
        Completed["conversation.item.completed<br/>Item finished"]
    end
    
    subgraph "Event Data"
        Item["item<br/>message|function_call|function_call_output"]
        Delta["delta<br/>audio|transcript|arguments"]
        Status["status<br/>in_progress|completed"]
    end
    
    subgraph "Application Response"
        ErrorHandler["Error Handling"]
        AudioStop["Stop Audio Playback"]
        UIUpdate["Update Chat Interface"]
        ToolExecution["Execute Function Calls"]
        ConversationState["Update Conversation State"]
    end
    
    Error --> ErrorHandler
    Interrupted --> AudioStop
    Updated --> UIUpdate
    Updated --> Delta
    Appended --> ConversationState
    Completed --> ToolExecution
    
    Item --> UIUpdate
    Delta --> UIUpdate
    Status --> ConversationState
```

Sources: [9-realtime/openai-realtime-console-example/README.md:230-276]()

## Tool Integration Patterns

Both systems demonstrate different approaches to tool integration with the Realtime API, from basic function calling to advanced agent patterns.

**Tool Integration Comparison**
```mermaid
graph TB
    subgraph "Realtime Console Tools"
        GetWeather["get_weather<br/>Weather API Integration"]
        SetMemory["set_memory<br/>JSON Blob Storage"]
        BasicCallback["Callback Execution<br/>async ({ lat, lng, location }) => {}"]
    end
    
    subgraph "Voice Agents Tools"
        AgentTools["Advanced Agent Tools<br/>OpenAI Agents SDK"]
        WorkspaceIntegration["Workspace Integration<br/>Responder-Thinker Pattern"]
        SDKPatterns["SDK Patterns<br/>Multi-agent collaboration"]
    end
    
    subgraph "Shared Infrastructure"
        RealtimeClient --> addTool["addTool()<br/>Tool Registration"]
        addTool --> ToolCallback["Tool Callback<br/>Automatic Response"]
        ToolCallback --> ModelResponse["Model Response<br/>Automatic continuation"]
    end
    
    GetWeather --> addTool
    SetMemory --> addTool
    AgentTools --> addTool
    
    RealtimeClient --> updateSession["updateSession()<br/>Configuration"]
    updateSession --> Instructions["instructions<br/>System Prompts"]
    updateSession --> Voice["voice<br/>alloy"]
    updateSession --> TurnDetection["turn_detection<br/>server_vad"]
```

Sources: [9-realtime/openai-realtime-console-example/README.md:53-61](), [9-realtime/openai-realtime-console-example/README.md:165-205](), [14-voice-agents/realtime-workspace-agents/README.md:5-14](), [14-voice-agents/realtime-workspace-agents/README.md:28-29]()

## Deployment and Development Patterns

The realtime applications demonstrate different deployment strategies and development approaches for realtime AI applications.

| Aspect | Realtime Console | Voice Agents |
|--------|-----------------|--------------|
| **Development Setup** | `npm start` on localhost:3000 | `npm run dev` on localhost:3000 |
| **API Key Management** | localStorage + UI prompt | Environment variables |
| **Relay Server** | Optional Node.js relay on :8081 | Integrated server handling |
| **Production Readiness** | Development/Reference tool | Production application framework |
| **Extensibility** | Manual client modification | SDK-based extension patterns |

**Deployment Architecture**
```mermaid
graph TD
    subgraph "Development Mode"
        DevClient["React/Next.js Client<br/>localhost:3000"]
        DevAPI["Direct OpenAI API<br/>Client-side key"]
    end
    
    subgraph "Production Mode"
        ProdClient["Production Client"]
        RelayServer["Relay Server<br/>localhost:8081"]
        ServerAPI["Server-side API<br/>Hidden credentials"]
    end
    
    subgraph "Configuration"
        EnvFile[".env<br/>OPENAI_API_KEY<br/>REACT_APP_LOCAL_RELAY_SERVER_URL"]
        LocalStorage["localStorage<br/>API Key Storage"]
    end
    
    DevClient --> DevAPI
    ProdClient --> RelayServer
    RelayServer --> ServerAPI
    
    EnvFile --> RelayServer
    LocalStorage --> DevClient
    
    DevClient -.-> ProdClient
    DevAPI -.-> RelayServer
```

Sources: [9-realtime/openai-realtime-console-example/README.md:64-109](), [14-voice-agents/realtime-workspace-agents/README.md:20-26]()

---

