<!-- source: DeepWiki mcp.deepwiki.com · repo AgentDock/AgentDock · page 2 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agentdock-core/package.json](agentdock-core/package.json)
- [agentdock-core/pnpm-lock.yaml](agentdock-core/pnpm-lock.yaml)
- [agentdock-core/src/nodes/agent-node.ts](agentdock-core/src/nodes/agent-node.ts)
- [agentdock-core/tsconfig.json](agentdock-core/tsconfig.json)
- [docs/i18n/chinese/README.md](docs/i18n/chinese/README.md)
- [docs/i18n/dutch/README.md](docs/i18n/dutch/README.md)
- [docs/i18n/french/README.md](docs/i18n/french/README.md)
- [docs/i18n/greek/README.md](docs/i18n/greek/README.md)
- [scripts/clean-install.sh](scripts/clean-install.sh)

</details>



This document provides a comprehensive overview of the AgentDock system architecture, explaining the core components, their interactions, and the design principles that guide the system. For information about specific subsystems, refer to their dedicated pages: [Node System](#2.1), [LLM Integration](#2.2), [Orchestration System](#2.3), and [Session Management](#2.4).

## Core Design Philosophy

AgentDock's architecture is built around the concept of **configurable determinism**, allowing developers to balance AI creativity with predictable system behavior. The framework uses a modular, node-based design where all capabilities are implemented as nodes, with specialized nodes (tools) extending the system for agent capabilities.

Sources: [docs/i18n/chinese/README.md:28-37](), [docs/i18n/dutch/README.md:28-37]()

## High-Level System Overview

At a high level, AgentDock consists of two main components:

1. **AgentDock Core**: The backend framework that provides the foundation for building AI agents
2. **OSS Client**: A complete Next.js application that serves as a reference implementation

```mermaid
flowchart TD
    subgraph "OSS Client"
        WebClient["Web Interface"]
        APIRoutes["API Routes"]
        State["State Management"]
        Components["UI Components"]
    end
    
    subgraph "agentdock-core"
        CoreFramework["CoreFramework"]
        NodeSystem["NodeSystem"]
        LLMIntegration["LLMIntegration"]
        SessionManager["SessionManager"]
        ToolRegistry["ToolRegistry"]
        StorageAbstraction["StorageAbstraction"]
        Orchestration["Orchestration"]
    end
    
    subgraph "External Services"
        LLMProviders["LLM Providers"]
        StorageProviders["Storage Providers"]
        SearchProviders["Search Providers"]
    end
    
    WebClient <--> APIRoutes
    APIRoutes <--> CoreFramework
    
    CoreFramework --> NodeSystem
    CoreFramework --> LLMIntegration
    CoreFramework --> SessionManager
    CoreFramework --> ToolRegistry
    CoreFramework --> StorageAbstraction
    CoreFramework --> Orchestration
    
    LLMIntegration --> LLMProviders
    StorageAbstraction --> StorageProviders
    ToolRegistry --> SearchProviders
```

Sources: [agentdock-core/package.json:17-28](), [docs/i18n/chinese/README.md:118-126]()

## Core Framework Components

The AgentDock Core framework is built around a node-based architecture that provides the foundation for all agent functionality. The core components include:

### Node System

The Node System is the fundamental architecture of AgentDock, where all capabilities are implemented as nodes:

```mermaid
classDiagram
    class BaseNode {
        +id: string
        +execute(input): Promise~any~
        +getCategory(): NodeCategory
        +getInputs(): NodePort[]
        +getOutputs(): NodePort[]
    }
    
    class AgentNode {
        +type: "core.agent"
        -llm: CoreLLM
        -fallbackLlm: CoreLLM
        +handleMessage(options): Promise~AgentDockStreamResult~
        -getAvailableTools(): Tool[]
        -createLLMInstance(): CoreLLM
        #getCategory(): NodeCategory
    }
    
    class Tool {
        +name: string
        +description: string
        +parameters: ZodSchema
        +execute(params, options): Promise~any~
    }
    
    BaseNode <|-- AgentNode
    BaseNode <|-- Tool
```

Sources: [agentdock-core/src/nodes/agent-node.ts:6-22](), [agentdock-core/src/nodes/agent-node.ts:96-127]()

### LLM Integration

The LLM Integration system manages interactions with various Large Language Model providers:

```mermaid
flowchart TD
    AgentNode["AgentNode"] --> LLMOrchestrationService["LLMOrchestrationService"]
    LLMOrchestrationService --> CoreLLM["CoreLLM"]
    CoreLLM --> ProviderRegistry["ProviderRegistry"]
    
    ProviderRegistry --> AnthropicProvider["AnthropicProvider"]
    ProviderRegistry --> OpenAIProvider["OpenAIProvider"]
    ProviderRegistry --> GeminiProvider["GeminiProvider"]
    ProviderRegistry --> GroqProvider["GroqProvider"]
    ProviderRegistry --> DeepSeekProvider["DeepSeekProvider"]
    
    AgentNode --> MessageUtils["convertCoreToLLMMessages()"]
    AgentNode --> PromptUtils["createSystemPrompt()"]
```

The LLM Integration system supports multiple providers through a unified interface, with automatic fallbacks and configurable settings.

Sources: [agentdock-core/src/nodes/agent-node.ts:148-224](), [agentdock-core/package.json:17-28]()

### Orchestration System

The Orchestration System controls agent behavior and tool availability based on conversation context:

```mermaid
flowchart LR
    AgentNode["AgentNode"] --> OrchestrationManager["OrchestrationManager"]
    OrchestrationManager --> ToolRegistry["ToolRegistry"]
    
    subgraph "Orchestration Flow"
        OrchestrationManager --> GetState["getState()"]
        OrchestrationManager --> GetAllowedTools["getAllowedTools()"]
        GetAllowedTools --> OrchestrateTools["Orchestrate Tools Based on Context"]
    end
    
    ToolRegistry --> GetToolsForAgent["getToolsForAgent()"]
    GetToolsForAgent --> FilterTools["Filter Tools by Orchestration"]
    FilterTools --> AvailableTools["Available Tools for Turn"]
```

The Orchestration System ensures that agents have access to the right tools at the right time based on the conversation context and orchestration configuration.

Sources: [agentdock-core/src/nodes/agent-node.ts:230-258](), [docs/i18n/chinese/README.md:194-195]()

### Session Management

The Session Management system maintains isolated state for concurrent conversations:

```mermaid
flowchart TD
    APIRoute["api/chat/[agentId]"] --> AgentAdapter["AgentAdapter"]
    AgentAdapter --> ProcessAgentMessage["processAgentMessage()"]
    ProcessAgentMessage --> OrchestrationManager["OrchestrationManager"]
    
    subgraph "Session Management"
        OrchestrationManager --> GetState["getState(sessionId)"]
        GetState --> AIOrchestrationState["AIOrchestrationState"]
        OrchestrationManager --> UpdateState["updateState(sessionId, state)"]
    end
    
    AgentNode["AgentNode"] --> OrchestrationManager
```

The Session Management system allows multiple concurrent conversations to maintain their own isolated state, ensuring that interactions don't interfere with each other.

Sources: [agentdock-core/src/nodes/agent-node.ts:272-326](), [docs/i18n/chinese/README.md:194-195]()

### Tool Registry

The Tool Registry manages the registration and discovery of tools for agents:

```mermaid
classDiagram
    class ToolRegistry {
        +registerTool(name, tool): void
        +getToolsForAgent(nodeNames): Tool[]
        +getTools(): Record<string, Tool>
    }
    
    class Tool {
        +name: string
        +description: string
        +parameters: ZodSchema
        +execute(params, options): Promise~any~
    }
    
    ToolRegistry --> Tool : manages
```

The Tool Registry is responsible for registering tools, making them available to agents, and managing tool lifecycles.

Sources: [agentdock-core/src/nodes/agent-node.ts:7-8](), [agentdock-core/src/nodes/agent-node.ts:230-258]()

### Storage Abstraction

The Storage Abstraction layer provides a unified interface for different storage providers:

```mermaid
flowchart TD
    StorageAbstraction["StorageAbstraction"] --> StorageProvider["StorageProvider Interface"]
    
    StorageProvider --> MemoryStorage["MemoryStorage"]
    StorageProvider --> RedisStorage["RedisStorage (Upstash)"]
    StorageProvider --> VercelKVStorage["VercelKVStorage"]
    
    subgraph "Storage Types"
        KeyValueStorage["KeyValueStorage"]
        SecureStorage["SecureStorage"]
        VectorStorage["VectorStorage (Planned)"]
    end
    
    StorageAbstraction --> KeyValueStorage
    StorageAbstraction --> SecureStorage
    StorageAbstraction --> VectorStorage
```

The Storage Abstraction layer supports different storage providers for various storage needs, making it easy to switch between providers without changing application code.

Sources: [agentdock-core/package.json:17-28](), [docs/i18n/chinese/README.md:196-197]()

## OSS Client Architecture

The OSS Client is a Next.js application that provides a reference implementation of a client for the AgentDock Core framework:

```mermaid
flowchart TD
    subgraph "Client Pages"
        HomePage["HomePage"]
        ChatPage["ChatPage"]
        AgentsPage["AgentsPage"]
        SettingsPage["SettingsPage"]
    end
    
    subgraph "API Routes"
        ChatAPI["api/chat/[agentId]"]
        SettingsAPI["api/settings/*"]
        AgentsAPI["api/agents/*"]
    end
    
    subgraph "Core Components"
        ChatContainer["ChatContainer"]
        ChatMessages["ChatMessages"]
        MessageInput["MessageInput"]
        AgentAdapter["AgentAdapter"]
    end
    
    ChatPage --> ChatContainer
    ChatContainer --> ChatMessages
    ChatContainer --> MessageInput
    
    ChatContainer --> useChat["useChat Hook"]
    useChat --> ChatAPI
    ChatAPI --> AgentAdapter
    AgentAdapter --> AgentNode["AgentNode (Core)"]
```

The OSS Client demonstrates how to integrate with the AgentDock Core framework, providing a complete user interface for interacting with AI agents.

Sources: [docs/i18n/chinese/README.md:212-216]()

## Message Processing Flow

The following diagram illustrates how a user message flows through the system:

```mermaid
sequenceDiagram
    participant User
    participant ChatContainer
    participant APIRoute as api/chat/[agentId]
    participant AgentAdapter
    participant AgentNode
    participant LLMOrchestration
    participant ToolRegistry
    participant LLMProvider
    
    User->>ChatContainer: Send Message
    ChatContainer->>APIRoute: POST /api/chat/[agentId]
    APIRoute->>AgentAdapter: Process Message
    AgentAdapter->>AgentNode: handleMessage(options)
    
    AgentNode->>ToolRegistry: getToolsForAgent(nodeIds)
    ToolRegistry-->>AgentNode: Available Tools
    
    AgentNode->>LLMOrchestration: streamWithOrchestration()
    LLMOrchestration->>LLMProvider: streamText()
    
    loop For each response chunk
        LLMProvider-->>LLMOrchestration: Text/Tool Call Chunk
        
        alt Is Tool Call
            LLMOrchestration->>ToolRegistry: Execute Tool
            ToolRegistry-->>LLMOrchestration: Tool Result
            LLMOrchestration->>LLMProvider: Continue with Tool Result
        else Is Text
            LLMOrchestration-->>AgentNode: Text Chunk
            AgentNode-->>AgentAdapter: Stream Chunk
            AgentAdapter-->>APIRoute: Stream Response
            APIRoute-->>ChatContainer: Stream Response
            ChatContainer-->>User: Display Response
        end
    end
```

This diagram shows the complete flow of a user message through the system, from the user interface to the LLM provider and back, including tool execution.

Sources: [agentdock-core/src/nodes/agent-node.ts:272-403]()

## Agent Configuration and Execution Flow

AgentDock uses template-based configuration for agents, with the following execution flow:

```mermaid
flowchart LR
    UserQuery["User Query"] --> ApiRoute["api/chat/[agentId]"]
    ApiRoute --> ProcessAgentMessage["processAgentMessage()"]
    ProcessAgentMessage --> GetTemplate["Get Agent Template"]
    GetTemplate --> CreateAgent["Create AgentNode"]
    
    CreateAgent --> ResolveApiKey["Resolve API Key"]
    ResolveApiKey --> ApiKeys{"API Key Sources"}
    ApiKeys -->|"1st"| AgentSpecific["Agent-specific Key"]
    ApiKeys -->|"2nd"| GlobalSettings["Global Settings Key"]
    ApiKeys -->|"3rd"| EnvVars["Environment Variables"]
    
    CreateAgent --> HandleMessage["AgentNode.handleMessage()"]
    HandleMessage --> GetTools["Get Available Tools"]
    HandleMessage --> CreatePrompt["Create System Prompt"]
    HandleMessage --> LLMStream["Stream from LLM"]
    
    LLMStream --> ToolCalls{"Tool Calls?"}
    ToolCalls -->|"Yes"| ExecuteTool["Execute Tool"]
    ToolCalls -->|"No"| GenerateResponse["Generate Response"]
    ExecuteTool --> LLMStream
```

This diagram illustrates how an agent is configured and executed, from the initial user query to the final response, including API key resolution and tool execution.

Sources: [agentdock-core/src/nodes/agent-node.ts:272-403](), [docs/i18n/chinese/README.md:234-279]()

## Integration with External Services

AgentDock integrates with several external services:

| Service Type | Providers | Integration Point |
|--------------|-----------|-------------------|
| LLM Providers | Anthropic, OpenAI, Google Gemini, Groq, DeepSeek | LLM Integration System |
| Storage Providers | Upstash Redis, Vercel KV, Memory (in-process) | Storage Abstraction Layer |
| Search Providers | Serper, FireCrawl | Tool Registry (Search Tools) |
| Analytics | PostHog | OSS Client |

These integrations are managed through provider-specific adapters, allowing for easy switching between providers without changing application code.

Sources: [agentdock-core/package.json:17-28](), [docs/i18n/chinese/README.md:234-279]()

## Development Workflow

The development workflow for AgentDock uses pnpm as the package manager and follows a monorepo structure:

```mermaid
flowchart TD
    CloneRepo["Clone Repository"] --> InstallDeps["Install Dependencies (pnpm install)"]
    InstallDeps --> ConfigEnv["Configure Environment (.env)"]
    ConfigEnv --> StartDev["Start Development Server (pnpm dev)"]
    
    subgraph "Development Tasks"
        BuildCore["Build Core (pnpm build in agentdock-core)"]
        TestCore["Test Core (pnpm test in agentdock-core)"]
        TypeCheck["Type Check (pnpm typecheck)"]
    end
    
    StartDev --> BuildCore
    StartDev --> TestCore
    StartDev --> TypeCheck
```

This diagram illustrates the development workflow for AgentDock, from cloning the repository to running development tasks.

Sources: [agentdock-core/package.json:12-15](), [scripts/clean-install.sh:1-14](), [agentdock-core/tsconfig.json:1-21]()

## Conclusion

The AgentDock architecture combines a powerful, node-based core framework with a flexible client implementation, allowing developers to build sophisticated AI agents with configurable determinism. The modular design, with clear separation of concerns between components, makes it easy to extend and customize the system for different use cases.

For more detailed information on specific components, refer to their dedicated wiki pages:
- [Node System](#2.1)
- [LLM Integration](#2.2)
- [Orchestration System](#2.3)
- [Session Management](#2.4)
- [Storage Abstraction](#2.5)

---

