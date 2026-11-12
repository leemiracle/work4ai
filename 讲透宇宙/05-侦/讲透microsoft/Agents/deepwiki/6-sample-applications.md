<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/Agents · page 6 Sample Applications · fetched 2026-10-26 -->

# Sample Applications

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [samples/README.md](samples/README.md)

</details>



This section provides a comprehensive guide to the sample applications included in the Microsoft 365 Agents SDK repository. The samples demonstrate various SDK capabilities, patterns, and integration scenarios across .NET, JavaScript, and Python implementations.

For detailed information about building agents using the core SDK classes, see [Building Agents](#2). For specific authentication implementation patterns, see [Authentication](#3). For deployment and hosting configurations, see [Deployment and Hosting](#4).

## Sample Categories and Structure

The sample applications are organized into multiple categories based on complexity and use case, distributed across three language implementations:

```mermaid
graph TB
    subgraph "Sample Organization"
        SamplesRoot["samples/"]
        DotNetSamples["samples/dotnet/"]
        NodeSamples["samples/nodejs/"]
        PythonSamples["samples/python/"]
    end
    
    subgraph "Basic Patterns"
        QuickStart["quickstart/"]
        Empty["Empty Agent"]
        Echo["Echo Bot"]
    end
    
    subgraph "Authentication Patterns"
        AutoSignIn["auto-signin/"]
        OBO["obo-authorization/"]
        MultiProvider["Multi-Provider OAuth"]
    end
    
    subgraph "AI Integration Patterns"
        SemanticKernel["semantic-kernel-multiturn/"]
        LangChain["langchain-multiturn/"]
        Streaming["azure-ai-streaming/"]
    end
    
    subgraph "Platform Integration"
        CopilotStudioSkill["copilotstudio-skill/"]
        CopilotStudioClient["copilotstudio-client/"]
        Cards["cards/"]
        WebChat["copilotstudio-webchat-react/"]
    end
    
    subgraph "Advanced Features"
        Retrieval["RetrievalBot/"]
        MultiTurn["multi-turn-prompt/"]
        ReactWebChat["copilotstudio-webchat-react/"]
    end
    
    SamplesRoot --> DotNetSamples
    SamplesRoot --> NodeSamples
    SamplesRoot --> PythonSamples
    
    DotNetSamples --> QuickStart
    DotNetSamples --> AutoSignIn
    DotNetSamples --> SemanticKernel
    DotNetSamples --> Streaming
    DotNetSamples --> CopilotStudioSkill
    DotNetSamples --> Retrieval
    
    NodeSamples --> Empty
    NodeSamples --> AutoSignIn
    NodeSamples --> LangChain
    NodeSamples --> Streaming
    NodeSamples --> Cards
    NodeSamples --> MultiTurn
    NodeSamples --> WebChat
```

Sources: [samples/README.md:1-9](), [samples/dotnet/README.md:1-12](), [samples/nodejs/README.md:1-15]()

## Sample Inventory by Language

The following table provides a comprehensive view of available samples across all supported languages:

| Category | .NET | JavaScript | Python | Description |
|----------|------|------------|--------|-------------|
| **Basic** | `quickstart` | Empty Agent | TBD | Simple echo functionality |
| **Authentication** | `auto-signin` | `auto-signin` | TBD | OAuth integration patterns |
| **Authentication** | `obo-authorization` | `obo-authorization` | TBD | On-Behalf-Of token exchange |
| **AI Integration** | `semantic-kernel-multiturn` | `langchain-multiturn` | TBD | Multi-turn AI conversations |
| **AI Integration** | `azure-ai-streaming` | `azure-ai-streaming` | TBD | Streaming AI responses |
| **Platform Integration** | `copilotstudio-skill` | `copilotstudio-skill` | TBD | Copilot Studio skills |
| **Platform Integration** | `copilotstudio-client` | `copilotstudio-client` | TBD | Copilot Studio clients |
| **Rich UI** | N/A | `cards` | TBD | Rich card interactions |
| **Dialog Management** | N/A | `multi-turn-prompt` | TBD | Multi-turn prompts |
| **Web Integration** | N/A | `copilotstudio-webchat-react` | TBD | React WebChat integration |
| **Data Retrieval** | `RetrievalBot` | N/A | TBD | Semantic Kernel retrieval |

Sources: [samples/dotnet/README.md:3-12](), [samples/nodejs/README.md:3-15]()

## Development and Testing Workflow

All samples follow a consistent development and testing workflow that supports both local development and cloud deployment:

```mermaid
graph TB
    subgraph "Local Development"
        IDE["Visual Studio Code<br/>Visual Studio"]
        DevTunnel["dev tunnel --allow-anonymous<br/>Port 3978"]
        LocalAgent["npm start<br/>dotnet run<br/>python -m src.main"]
    end
    
    subgraph "Testing Methods"
        Playground["agentsplayground<br/>Microsoft 365 Agents Playground"]
        WebChat["Azure Bot Service<br/>Test in WebChat"]
        Teams["Microsoft Teams<br/>App Manifest Upload"]
    end
    
    subgraph "Azure Configuration"
        BotService["Azure Bot Service<br/>Bot Registration"]
        AppReg["Entra ID App Registration<br/>Client Credentials"]
        OAuth["OAuth Connections<br/>Identity Providers"]
    end
    
    subgraph "Cloud Deployment"
        AppService["Azure App Service<br/>ASP.NET Core / Node.js"]
        ContainerApps["Azure Container Apps<br/>Docker Deployment"]
        CICD["GitHub Actions<br/>cd-samples Workflow"]
    end
    
    IDE --> LocalAgent
    LocalAgent --> DevTunnel
    DevTunnel --> Playground
    DevTunnel --> WebChat
    DevTunnel --> Teams
    
    BotService --> AppReg
    BotService --> OAuth
    AppReg --> OAuth
    
    LocalAgent --> AppService
    LocalAgent --> ContainerApps
    CICD --> AppService
    CICD --> ContainerApps
    
    AppService --> WebChat
    ContainerApps --> WebChat
    AppService --> Teams
    ContainerApps --> Teams
```

Sources: [samples/dotnet/quickstart/README.md:13-27](), [samples/nodejs/langchain-multiturn/README.md:32-38](), [samples/dotnet/auto-signin/README.md:69-83]()

## Authentication Sample Patterns

The authentication samples demonstrate different OAuth and authorization patterns used across the Microsoft 365 ecosystem:

```mermaid
graph TB
    subgraph "Authentication Types"
        ClientSecret["ClientSecret Authentication<br/>appsettings.json<br/>.env files"]
        FederatedCreds["Federated Credentials<br/>Certificate-based"]
        ManagedIdentity["User Assigned Managed Identity<br/>Azure-native auth"]
    end
    
    subgraph "Auto Sign-In Pattern"
        AutoSignInConfig["AgentApplication:UserAuthorization:AutoSignIn: true<br/>Default handler configuration"]
        PerRoute["Per-Route Authorization<br/>onMessage('/me', handler, ['graph'])"]
        TokenAvailability["Multiple tokens available<br/>Auto + Per-Route"]
    end
    
    subgraph "OBO Pattern"
        InitialToken["Initial User Token<br/>Graph API access"]
        TokenExchange["OBO Token Exchange<br/>Custom scope acquisition"]
        ServiceAccess["Service API Access<br/>CopilotStudio.Copilots.Invoke"]
    end
    
    subgraph "Multi-Provider Pattern"
        GraphProvider["Microsoft Graph Provider<br/>Azure AD v2"]
        GitHubProvider["GitHub Provider<br/>OAuth App Configuration"]
        MultiAuth["Combined Authentication<br/>graph_connectionName<br/>github_connectionName"]
    end
    
    ClientSecret --> AutoSignInConfig
    ClientSecret --> PerRoute
    ClientSecret --> InitialToken
    
    AutoSignInConfig --> TokenAvailability
    PerRoute --> TokenAvailability
    
    InitialToken --> TokenExchange
    TokenExchange --> ServiceAccess
    
    GraphProvider --> MultiAuth
    GitHubProvider --> MultiAuth
```

Sources: [samples/dotnet/auto-signin/README.md:6-9](), [samples/nodejs/auto-signin/README.md:5-12](), [samples/nodejs/obo-authorization/README.md:5-7]()

## AI Integration Architecture

The AI-powered samples showcase integration with various AI services and frameworks:

```mermaid
graph TB
    subgraph "AI Service Providers"
        AzureOpenAI["Azure OpenAI<br/>AZURE_OPENAI_DEPLOYMENT_NAME<br/>AZURE_OPENAI_API_KEY"]
        OpenAI["OpenAI API<br/>OPENAI_MODEL<br/>OPENAI_API_KEY"]
    end
    
    subgraph "AI Framework Integration"
        SemanticKernelImpl["Semantic Kernel<br/>semantic-kernel-multiturn<br/>Chat Completion Agents"]
        LangChainImpl["LangChain<br/>langchain-multiturn<br/>streamText from ai package"]
        AzureAISDK["@ai-sdk/azure<br/>azure-ai-streaming<br/>Stream Integration"]
    end
    
    subgraph "Streaming Implementation"
        StreamingResponse["context.streamingResponse<br/>setFeedbackLoop(true)<br/>setGeneratedByAILabel(true)"]
        TextChunking["queueTextChunk(part.textDelta)<br/>queueInformativeUpdate()"]
        StreamManagement["endStream()<br/>Error handling"]
    end
    
    subgraph "Multi-turn Conversation"
        StateManagement["TurnState management<br/>Conversation context"]
        WeatherAgent["Weather forecast requests<br/>JSON output from model"]
        AdaptiveCards["Adaptive Card responses<br/>Rich formatting"]
    end
    
    AzureOpenAI --> SemanticKernelImpl
    AzureOpenAI --> LangChainImpl
    AzureOpenAI --> AzureAISDK
    OpenAI --> LangChainImpl
    OpenAI --> AzureAISDK
    
    AzureAISDK --> StreamingResponse
    StreamingResponse --> TextChunking
    TextChunking --> StreamManagement
    
    SemanticKernelImpl --> StateManagement
    LangChainImpl --> StateManagement
    StateManagement --> WeatherAgent
    WeatherAgent --> AdaptiveCards
```

Sources: [samples/nodejs/azure-ai-streaming/src/agent.ts:1-70](), [samples/nodejs/langchain-multiturn/README.md:1-8](), [samples/dotnet/semantic-kernel-multiturn/README.md:1-8]()

## Copilot Studio Integration Patterns

The Copilot Studio samples demonstrate different integration approaches for skills and clients:

```mermaid
graph TB
    subgraph "Skill Development"
        SkillManifest["wwwroot/manifest/echoskill-manifest-1.0.json<br/>Skill capability description"]
        SkillEndpoint["/api/messages<br/>Activity processing"]
        SkillConversation["Multi-turn conversation<br/>Success/Error indication"]
    end
    
    subgraph "Client Development"
        CopilotStudioClient["CopilotStudioClient<br/>Agent invocation"]
        OBOTokenExchange["OBO Token Exchange<br/>CopilotStudio.Copilots.Invoke"]
        EnvironmentConfig["EnvironmentId<br/>SchemaName configuration"]
    end
    
    subgraph "WebChat Integration"
        ReactWebChat["copilotstudio-webchat-react<br/>React component integration"]
        WebChatClient["Web-based chat interface<br/>Browser deployment"]
        UIComponents["Interactive UI elements<br/>Rich conversation"]
    end
    
    subgraph "Copilot Studio Configuration"
        AgentSettings["Agent Settings > Skills<br/>Skill registration"]
        TopicTriggers["Topic configuration<br/>Call an Action nodes"]
        ManifestValidation["Manifest URL validation<br/>Capability verification"]
    end
    
    SkillManifest --> SkillEndpoint
    SkillEndpoint --> SkillConversation
    SkillConversation --> AgentSettings
    AgentSettings --> TopicTriggers
    AgentSettings --> ManifestValidation
    
    EnvironmentConfig --> CopilotStudioClient
    CopilotStudioClient --> OBOTokenExchange
    OBOTokenExchange --> SkillEndpoint
    
    ReactWebChat --> WebChatClient
    WebChatClient --> UIComponents
    UIComponents --> CopilotStudioClient
```

Sources: [samples/dotnet/copilotstudio-skill/README.md:10-18](), [samples/nodejs/copilotstudio-skill/README.md:1-4](), [samples/dotnet/obo-authorization/README.md:5-7]()

## Sample Configuration Patterns

Each sample follows consistent configuration patterns for different deployment scenarios:

| Configuration Type | .NET Implementation | JavaScript Implementation | Purpose |
|-------------------|-------------------|--------------------------|---------|
| **Bot Authentication** | `appsettings.json` | `.env` file | Client credentials and tenant configuration |
| **AI Service Configuration** | `AIServices` section | Environment variables | Azure OpenAI/OpenAI endpoint configuration |
| **OAuth Configuration** | `UserAuthorization` section | Connection name prefixes | Identity provider connections |
| **JWT Validation** | `TokenValidation` section | Not implemented | Production security validation |
| **Development Settings** | Debug mode defaults | Anonymous mode support | Local development configuration |

Sources: [samples/dotnet/auto-signin/README.md:39-67](), [samples/nodejs/auto-signin/README.md:34-61](), [samples/dotnet/semantic-kernel-multiturn/README.md:17-32]()

## Development Tools and Testing

The samples utilize several development tools and testing approaches:

```mermaid
graph LR
    subgraph "Development Tools"
        VSCode["Visual Studio Code<br/>Cross-platform development"]
        VS["Visual Studio<br/>.NET development"]
        DevTunnels["dev tunnel<br/>Local to cloud bridging"]
    end
    
    subgraph "Testing Tools"
        AgentsPlayground["agentsplayground<br/>winget install agentsplayground<br/>Local testing UI"]
        TestTool["npm run test-tool<br/>@microsoft/m365agentsplayground"]
        WebChatTest["Test in WebChat<br/>Azure Portal integration"]
    end
    
    subgraph "Package Management"
        NPM["npm start<br/>Node.js package management"]
        NuGet["dotnet run<br/>.NET package management"]
        Python["python -m src.main<br/>pip package management"]
    end
    
    subgraph "CI/CD Pipeline"
        GitHubActions["GitHub Actions<br/>cd-samples workflow"]
        Linting["ESLint (neostandard)<br/>TypeScript checking"]
        BuildTest["Build & Test<br/>Automated validation"]
    end
    
    VSCode --> DevTunnels
    VS --> DevTunnels
    DevTunnels --> AgentsPlayground
    DevTunnels --> WebChatTest
    
    NPM --> TestTool
    NPM --> AgentsPlayground
    NuGet --> AgentsPlayground
    Python --> AgentsPlayground
    
    GitHubActions --> Linting
    GitHubActions --> BuildTest
    Linting --> BuildTest
```

Sources: [samples/dotnet/quickstart/README.md:13-27](), [samples/nodejs/azure-ai-streaming/package.json:10-15](), [samples/nodejs/cards/README.md:45-63]()

---

