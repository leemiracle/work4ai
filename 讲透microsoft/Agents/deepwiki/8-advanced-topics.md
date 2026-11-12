<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/Agents · page 8 Advanced Topics · fetched 2026-10-26 -->

# Advanced Topics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [MCSandAgentsEcosystemLinks.md](MCSandAgentsEcosystemLinks.md)
- [README.md](README.md)

</details>



This section covers advanced development concepts for the Microsoft 365 Agents SDK. These topics assume familiarity with [Building Agents](#2), [Authentication and Authorization](#3), and [Deployment and Hosting](#4).

The advanced topics are organized into four main areas:

- **AI Integration Patterns** ([Section 8.1](#8.1)) - Integrating with Semantic Kernel, Azure AI Foundry, LangChain, and custom AI services
- **Activity Protocol Specification** ([Section 8.2](#8.2)) - Complete protocol specification for activities, cards, manifests, and APIs
- **Error Handling and Troubleshooting** ([Section 8.3](#8.3)) - Error codes, debugging strategies, and issue reporting
- **Development Tools and Debugging** ([Section 8.4](#8.4)) - Tools including agents playground, dev tunnel, and VS Code extensions

For sample implementations demonstrating these concepts, see [Sample Applications](#6).

## SDK Architecture and Extension Points

The Microsoft 365 Agents SDK provides a layered architecture that separates the core agent container from AI services and external integrations. This design enables developers to select AI frameworks and services based on specific requirements.

### SDK Core and Extension Architecture

The following diagram shows the relationship between core SDK packages and external service integrations:

```mermaid
graph TB
    subgraph "Core SDK Packages"
        AgentsActivity["@microsoft/agents-activity<br/>Microsoft.Agents.Activity<br/>agents-activity"]
        AgentsHosting["@microsoft/agents-hosting<br/>Microsoft.Agents.Hosting<br/>agents-hosting"]
        HostingExpress["@microsoft/agents-hosting-express<br/>Microsoft.Agents.Hosting.AspNetCore<br/>agents-hosting-aiohttp"]
    end
    
    subgraph "AI Framework Integration Points"
        SemanticKernel["Semantic Kernel SDK<br/>Multi-language support"]
        AzureAI["@ai-sdk/azure<br/>Azure.AI.Inference"]
        LangChain["langchain / langgraph<br/>Python LangChain"]
        CustomAI["Custom AI Services<br/>Direct API integration"]
    end
    
    subgraph "Microsoft Services"
        CopilotStudio["@microsoft/agents-copilotstudio-client<br/>Copilot Studio API"]
        Graph["Microsoft Graph<br/>@microsoft/microsoft-graph-client"]
        AzureOpenAI["Azure OpenAI Service"]
    end
    
    AgentsActivity --> AgentsHosting
    AgentsHosting --> HostingExpress
    
    HostingExpress -.integrates.-> SemanticKernel
    HostingExpress -.integrates.-> AzureAI
    HostingExpress -.integrates.-> LangChain
    HostingExpress -.integrates.-> CustomAI
    
    HostingExpress -.connects.-> CopilotStudio
    HostingExpress -.connects.-> Graph
    
    SemanticKernel --> AzureOpenAI
    AzureAI --> AzureOpenAI
    LangChain --> AzureOpenAI
```

**Key Integration Points:**

| Language | Core Package | Hosting Package | AI Framework Examples |
|----------|--------------|-----------------|----------------------|
| Node.js | `@microsoft/agents-hosting` | `@microsoft/agents-hosting-express` | `@ai-sdk/azure`, `langchain`, `@langchain/langgraph` |
| .NET | `Microsoft.Agents.Hosting` | `Microsoft.Agents.Hosting.AspNetCore` | Semantic Kernel, Azure.AI.Inference |
| Python | `agents-hosting` | `agents-hosting-aiohttp` | LangChain, Azure AI SDK |

**Sources:** [README.md:1-106](), [MCSandAgentsEcosystemLinks.md:1-119]()

### AI Service Integration Overview

The SDK supports multiple AI integration patterns. See [AI Integration Patterns](#8.1) for detailed documentation on:

- Integrating with Semantic Kernel for LLM orchestration
- Using Azure AI Foundry for reasoning and RAG patterns
- Implementing LangChain for complex multi-agent workflows
- Direct API integration with Azure OpenAI and other providers
- Streaming response patterns with `StreamingResponse` API

**Sources:** [README.md:34-50]()

## Protocol and API Architecture

The SDK implements the Activity Protocol specification, which defines the message format, authentication patterns, and service discovery mechanisms used across all channels.

### Protocol Layers and SDK Implementation

The following diagram maps protocol specifications to SDK implementation components:

```mermaid
graph TB
    subgraph "Protocol Specification Layer"
        ActivityProtocol["Activity Protocol<br/>specs/activity/protocol-activity.md<br/>17+ Activity Types"]
        CardsProtocol["Cards Protocol<br/>Hero, Adaptive, Thumbnail<br/>Interactive Elements"]
        ManifestSpec["Bot Manifest<br/>specs/manifest/manifest.json<br/>Capability Declaration"]
    end
    
    subgraph "API Specifications"
        ChannelAPI["Channel API<br/>specs/channel-api/ChannelAPI-OpenAPI.yaml<br/>Conversations, Activities, Members"]
        TokenAPI["Token API<br/>specs/channel-api/TokenAPI-OpenAPI.yaml<br/>OAuth, Sign-in, Token Exchange"]
    end
    
    subgraph "SDK Implementation Components"
        ActivityTypes["Activity classes<br/>IActivity, IMessageActivity<br/>IConversationUpdateActivity"]
        CardClasses["Card attachment classes<br/>HeroCard, AdaptiveCard<br/>ThumbnailCard"]
        ChannelClient["Channel connector clients<br/>IConnectorClient<br/>Conversations.SendToConversationAsync"]
        AuthHandlers["Authorization handlers<br/>IUserAuthorization<br/>IAccessTokenProvider"]
    end
    
    ActivityProtocol -.implements.-> ActivityTypes
    CardsProtocol -.implements.-> CardClasses
    ChannelAPI -.implements.-> ChannelClient
    TokenAPI -.implements.-> AuthHandlers
    
    ManifestSpec -.configures.-> ChannelClient
    ManifestSpec -.configures.-> AuthHandlers
```

**Protocol Components:**

| Protocol Area | Specification Location | SDK Implementation |
|--------------|----------------------|-------------------|
| Activity Types | `specs/activity/protocol-activity.md` | `IActivity`, `IMessageActivity`, `IConversationUpdateActivity` |
| Cards | `specs/activity/cards.md` | `HeroCard`, `AdaptiveCard`, `ThumbnailCard` classes |
| Channel API | `specs/channel-api/ChannelAPI-OpenAPI.yaml` | `IConnectorClient`, `Conversations` resource |
| Token API | `specs/channel-api/TokenAPI-OpenAPI.yaml` | `IUserAuthorization`, `IAccessTokenProvider` |
| Bot Manifest | `specs/manifest/manifest.json` | Service configuration and registration |

See [Activity Protocol Specification](#8.2) for complete protocol documentation including:

- Activity schema and validation rules
- Card format specifications
- Channel API endpoints and request/response formats
- Token API authentication flows
- Bot manifest structure and service discovery

**Sources:** [README.md:1-106](), [MCSandAgentsEcosystemLinks.md:46-58]()

## Error Handling and Troubleshooting

The SDK provides structured error handling patterns and diagnostic tools for identifying and resolving issues during development and production operation.

### Error Handling Architecture

Error handling spans multiple layers from protocol validation through application logic:

| Error Type | Layer | Handling Mechanism |
|-----------|-------|-------------------|
| Protocol Errors | Activity validation | Schema validation, error activities |
| Authentication Errors | Token management | Token refresh, user authorization handlers |
| Application Errors | Message handlers | Try-catch blocks, error logging |
| Service Errors | External API calls | Retry policies, fallback responses |

Common error scenarios and resolution strategies are documented in [Error Handling and Troubleshooting](#8.3), including:

- Error code reference and diagnostic messages
- Common authentication and authorization issues
- State management errors and recovery patterns
- Network connectivity and timeout handling
- Channel-specific error scenarios

**Sources:** [README.md:74-86]()

## Development Tools and Workflow

The SDK ecosystem includes tools for local development, testing, and debugging agents before production deployment.

### Development Tools Ecosystem

The following diagram shows the relationship between development tools and the agent runtime:

```mermaid
graph TB
    subgraph "VS Code Extensions"
        ESLint["ESLint<br/>dbaeumer.vscode-eslint"]
        CSharpDevKit["C# Dev Kit<br/>ms-dotnettools.csdevkit"]
        AdaptiveCards["Adaptive Card Previewer<br/>TeamsDevApp.vscode-adaptive-cards"]
        Copilot["GitHub Copilot Chat<br/>GitHub.copilot-chat"]
    end
    
    subgraph "Local Development Tools"
        DevTunnel["dev tunnel<br/>devtunnels.ms"]
        LocalServer["Local HTTP Server<br/>:3978 (default)"]
        Playground["@microsoft/m365agentsplayground<br/>npm run test-tool"]
    end
    
    subgraph "Testing Channels"
        PlaygroundUI["Agents Playground UI"]
        AzureWebChat["Azure Bot Service WebChat"]
        TeamsChannel["Microsoft Teams Test Channel"]
    end
    
    subgraph "Azure Configuration"
        BotRegistration["Azure Bot Service Registration"]
        AppReg["Azure App Registration<br/>Client ID + Secret"]
        MessagingEndpoint["Messaging Endpoint URL"]
    end
    
    ESLint -.validates.-> LocalServer
    CSharpDevKit -.builds.-> LocalServer
    AdaptiveCards -.previews.-> LocalServer
    
    LocalServer --> DevTunnel
    LocalServer --> Playground
    
    DevTunnel --> MessagingEndpoint
    Playground --> PlaygroundUI
    
    MessagingEndpoint --> BotRegistration
    BotRegistration --> AzureWebChat
    BotRegistration --> TeamsChannel
    
    AppReg -.authenticates.-> BotRegistration
```

**Recommended VS Code Extensions:**

| Extension | Package ID | Purpose |
|----------|------------|---------|
| ESLint | `dbaeumer.vscode-eslint` | JavaScript/TypeScript linting |
| C# Dev Kit | `ms-dotnettools.csdevkit` | .NET development and testing |
| Adaptive Card Previewer | `TeamsDevApp.vscode-adaptive-cards` | Card design and validation |
| GitHub Copilot Chat | `GitHub.copilot-chat` | AI-assisted development |

**Testing Tools:**

| Tool | Command | Purpose |
|------|---------|---------|
| Agents Playground | `npm run test-tool` | Local testing with UI |
| dev tunnel | `devtunnel host -p 3978` | Expose local endpoint to Azure |
| Azure WebChat | Azure Portal | Browser-based testing |

See [Development Tools and Debugging](#8.4) for detailed documentation on:

- Setting up local development environment
- Using dev tunnel for local testing
- Agents Playground features and configuration
- Debugging techniques and logging patterns
- VS Code integration and recommended workflows

**Sources:** [README.md:74-86]()

## Advanced Integration Patterns

### Copilot Studio Integration Architecture

The SDK supports both skill development for Copilot Studio and client applications that consume Copilot Studio agents.

```mermaid
graph TB
    subgraph "Copilot Studio Skills"
        SkillManifest["Skill Manifest"]
        SkillEndpoint["Skill Endpoint"]
        SkillRegistration["Copilot Studio Registration"]
    end
    
    subgraph "Agent Implementation"
        AgentApplication["AgentApplication"]
        MessageHandlers["Message Handlers"]
        StateManagement["State Management"]
    end
    
    subgraph "Copilot Studio Client"
        ClientApp["Client Application"]
        CopilotInvoke["CopilotStudio.Copilots.Invoke"]
        OBOAuth["OBO Authorization"]
    end
    
    SkillManifest --> SkillRegistration
    SkillEndpoint --> AgentApplication
    AgentApplication --> MessageHandlers
    MessageHandlers --> StateManagement
    
    ClientApp --> CopilotInvoke
    CopilotInvoke --> OBOAuth
    OBOAuth --> SkillEndpoint
```

Sources: [samples/nodejs/copilotstudio-skill/README.md:1-58](), [samples/nodejs/obo-authorization/README.md:1-86]()

### Multi-turn Dialog Management

Advanced dialog patterns support complex conversational flows with persistent state management and context preservation.

```mermaid
graph TB
    subgraph "Dialog Flow Management"
        TurnContext["TurnContext"]
        TurnState["TurnState<ConversationState>"]
        DialogManager["Dialog Manager"]
        StateStorage["State Storage"]
    end
    
    subgraph "State Types"
        ConversationState["Conversation State"]
        UserState["User State"]
        DialogState["Dialog State"]
        TemporaryState["Temporary State"]
    end
    
    subgraph "Storage Backends"
        MemoryStorage["Memory Storage"]
        CosmosStorage["Cosmos DB Storage"]
        BlobStorage["Blob Storage"]
    end
    
    TurnContext --> TurnState
    TurnState --> DialogManager
    DialogManager --> StateStorage
    
    TurnState --> ConversationState
    TurnState --> UserState
    TurnState --> DialogState
    TurnState --> TemporaryState
    
    StateStorage --> MemoryStorage
    StateStorage --> CosmosStorage
    StateStorage --> BlobStorage
```

Sources: [samples/nodejs/multi-turn-prompt/README.md:14]()

This advanced topics coverage demonstrates the enterprise-ready capabilities of the Microsoft 365 Agents SDK, from low-level protocol specifications to high-level AI integration patterns, providing the foundation for building sophisticated conversational agents that integrate seamlessly with the Microsoft 365 ecosystem.

---

