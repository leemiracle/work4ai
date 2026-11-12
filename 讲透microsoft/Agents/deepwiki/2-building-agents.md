<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/Agents · page 2 Building Agents · fetched 2026-10-26 -->

# Building Agents

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [samples/nodejs/quickstart/README.md](samples/nodejs/quickstart/README.md)
- [samples/nodejs/quickstart/env.TEMPLATE](samples/nodejs/quickstart/env.TEMPLATE)
- [samples/nodejs/quickstart/package.json](samples/nodejs/quickstart/package.json)
- [samples/nodejs/quickstart/src/index.ts](samples/nodejs/quickstart/src/index.ts)
- [samples/nodejs/quickstart/tsconfig.json](samples/nodejs/quickstart/tsconfig.json)

</details>



This document provides a comprehensive guide to building agents using the Microsoft 365 Agents SDK across .NET, Node.js, and Python. It covers the core `AgentApplication` class, activity processing patterns, message handling, and multi-language implementation approaches. For deployment information, see [Deployment and Hosting](#4). For authentication patterns, see [Authentication](#3).

## Multi-Language Agent Architecture

The Microsoft 365 Agents SDK provides consistent architecture across .NET, Node.js, and Python implementations, centered around the `AgentApplication` class as the main container for agent logic and event handling.

### Cross-Platform Architecture Overview

```mermaid
graph TB
    subgraph "Language Implementations"
        DotNet[".NET Implementation<br/>AgentApplication<br/>ASP.NET Core"]
        NodeJS["Node.js Implementation<br/>AgentApplication<br/>Express.js"]
        Python["Python Implementation<br/>AgentApplication<br/>aiohttp"]
    end
    
    subgraph "HTTP Endpoints"
        ApiMessages["/api/messages<br/>POST endpoint"]
        ProcessAsync["ProcessAsync()<br/>Request handling"]
    end
    
    subgraph "Agent Core"
        AgentApplication["AgentApplication<br/>Main container"]
        TurnContext["TurnContext<br/>Request context"]
        TurnState["TurnState<br/>Conversation state"]
    end
    
    subgraph "Activity Processing"
        OnMessage["@AGENT_APP.message<br/>onMessage()<br/>message handlers"]
        OnConversationUpdate["@AGENT_APP.conversation_update<br/>onConversationUpdate()<br/>member events"]
        OnActivity["@AGENT_APP.activity<br/>onActivity()<br/>activity handlers"]
    end
    
    subgraph "Storage & State"
        MemoryStorage["MemoryStorage<br/>In-memory state"]
        Authorization["Authorization<br/>Auth handlers"]
        CloudAdapter["CloudAdapter<br/>Bot Framework"]
    end
    
    DotNet --> ApiMessages
    NodeJS --> ApiMessages
    Python --> ApiMessages
    
    ApiMessages --> ProcessAsync
    ProcessAsync --> AgentApplication
    AgentApplication --> TurnContext
    TurnContext --> TurnState
    
    AgentApplication --> OnMessage
    AgentApplication --> OnConversationUpdate
    AgentApplication --> OnActivity
    
    AgentApplication --> MemoryStorage
    AgentApplication --> Authorization
    AgentApplication --> CloudAdapter
```

Sources: [samples/dotnet/auto-signin/README.md:1-134](), [samples/nodejs/langchain-multiturn/README.md:1-80](), [samples/python/auto-signin/src/agent.py:1-139](), [samples/python/cards/src/agent.py:1-78]()

### Language-Specific Hosting Patterns

| Language | Hosting Framework | Entry Point | Agent Registration |
|----------|------------------|-------------|-------------------|
| .NET | ASP.NET Core | `Program.cs` | `AddAgent<T>()` |
| Node.js | Express.js | `agent.ts` | `startServer(agent)` |
| Python | aiohttp | `main.py` | `start_server()` |

Sources: [samples/dotnet/quickstart/README.md:1-98](), [samples/nodejs/azure-ai-streaming/src/agent.ts:1-70](), [samples/python/auto-signin/src/start_server.py:1-32]()

## Core Components

### AgentApplication Class Across Languages

The `AgentApplication` class serves as the primary container for agent functionality across all language implementations, with language-specific patterns for configuration and handler registration.

#### .NET Implementation

```mermaid
graph TB
    subgraph ".NET Agent Setup"
        WebApplicationBuilder["WebApplicationBuilder.CreateBuilder()"]
        AddAgentApplicationOptions["builder.Services.AddAgentApplicationOptions()"]
        AddAgent["builder.Services.AddAgent<T>()"]
        BuildApp["builder.Build()"]
    end
    
    subgraph "Agent Configuration"
        AppSettings["appsettings.json<br/>AgentApplication section"]
        ServiceCollection["ServiceCollection<br/>DI container"]
        AgentApplicationOptions["AgentApplicationOptions<br/>Configuration binding"]
    end
    
    subgraph "Handler Registration"
        OnActivityMethod["agent.OnActivity()<br/>Activity type routing"]
        MessageHandler["ActivityTypes.Message<br/>Text processing"]
        ConversationUpdateHandler["ActivityTypes.ConversationUpdate<br/>Member events"]
    end
    
    WebApplicationBuilder --> AddAgentApplicationOptions
    AddAgentApplicationOptions --> AddAgent
    AddAgent --> BuildApp
    
    AppSettings --> ServiceCollection
    ServiceCollection --> AgentApplicationOptions
    AgentApplicationOptions --> OnActivityMethod
    OnActivityMethod --> MessageHandler
    OnActivityMethod --> ConversationUpdateHandler
```

#### Node.js Implementation

```mermaid
graph TB
    subgraph "Node.js Agent Setup"
        AgentConstructor["new AgentApplication<TurnState>()"]
        StartServer["startServer(agent)<br/>Express.js hosting"]
        ExpressApp["Express app<br/>Port 3978"]
    end
    
    subgraph "Handler Registration"
        OnMessage["agent.onMessage()<br/>Text message routing"]
        OnConversationUpdate["agent.onConversationUpdate()<br/>Member events"]
        OnActivity["agent.onActivity()<br/>Activity routing"]
    end
    
    subgraph "Configuration"
        EnvFile[".env file<br/>Environment variables"]
        PackageJson["package.json<br/>Dependencies"]
        StartScript["npm start<br/>Launch script"]
    end
    
    AgentConstructor --> StartServer
    StartServer --> ExpressApp
    
    OnMessage --> AgentConstructor
    OnConversationUpdate --> AgentConstructor
    OnActivity --> AgentConstructor
    
    EnvFile --> StartScript
    PackageJson --> StartScript
    StartScript --> ExpressApp
```

#### Python Implementation

```mermaid
graph TB
    subgraph "Python Agent Setup"
        AgentApplicationClass["AgentApplication[TurnState]<br/>Type-annotated container"]
        StartServer["start_server()<br/>aiohttp hosting"]
        AiohttpApp["aiohttp.Application<br/>Port 3978"]
    end
    
    subgraph "Handler Registration"
        MessageDecorator["@AGENT_APP.message<br/>Regex pattern matching"]
        ConversationUpdateDecorator["@AGENT_APP.conversation_update<br/>Member events"]
        ActivityDecorator["@AGENT_APP.activity<br/>Activity type routing"]
    end
    
    subgraph "Configuration"
        LoadDotenv["load_dotenv()<br/>Environment loading"]
        LoadConfiguration["load_configuration_from_env()<br/>SDK configuration"]
        MemoryStorageInit["MemoryStorage()<br/>State management"]
    end
    
    AgentApplicationClass --> StartServer
    StartServer --> AiohttpApp
    
    MessageDecorator --> AgentApplicationClass
    ConversationUpdateDecorator --> AgentApplicationClass
    ActivityDecorator --> AgentApplicationClass
    
    LoadDotenv --> LoadConfiguration
    LoadConfiguration --> MemoryStorageInit
    MemoryStorageInit --> AgentApplicationClass
```

Sources: [samples/dotnet/auto-signin/README.md:18-97](), [samples/nodejs/azure-ai-streaming/src/agent.ts:7-69](), [samples/python/auto-signin/src/agent.py:28-52](), [samples/python/cards/src/agent.py:23-37]()

### HTTP Endpoint Configuration

All agent implementations expose an HTTP POST endpoint at `/api/messages` to receive Bot Framework activities. The endpoint configuration varies by language but follows the same processing pattern.

#### Language-Specific Endpoint Setup

| Language | Framework | Endpoint Registration | Adapter Class |
|----------|-----------|----------------------|---------------|
| .NET | ASP.NET Core | `app.MapPost("/api/messages")` | `IAgentHttpAdapter` |
| Node.js | Express.js | `startServer(agent)` | Built into hosting |
| Python | aiohttp | `APP.router.add_post("/api/messages")` | `CloudAdapter` |

#### Request Processing Flow

```mermaid
graph TB
    subgraph "HTTP Layer"
        IncomingRequest["HTTP POST<br/>/api/messages<br/>Bot Framework Activity"]
    end
    
    subgraph ".NET Processing"
        DotNetAdapter["IAgentHttpAdapter<br/>ProcessAsync()"]
        DotNetAgent["IAgent implementation<br/>OnActivity handlers"]
    end
    
    subgraph "Node.js Processing"
        NodeAdapter["Built-in adapter<br/>Express middleware"]
        NodeAgent["AgentApplication<br/>onMessage/onActivity"]
    end
    
    subgraph "Python Processing"
        PythonAdapter["CloudAdapter<br/>start_agent_process()"]
        PythonAgent["AgentApplication<br/>@decorators"]
    end
    
    subgraph "Common Processing"
        TurnContext["TurnContext<br/>Request context"]
        ActivityProcessing["Activity processing<br/>Handler execution"]
        ResponseGeneration["Response generation<br/>HTTP 200/activity"]
    end
    
    IncomingRequest --> DotNetAdapter
    IncomingRequest --> NodeAdapter
    IncomingRequest --> PythonAdapter
    
    DotNetAdapter --> DotNetAgent
    NodeAdapter --> NodeAgent
    PythonAdapter --> PythonAgent
    
    DotNetAgent --> TurnContext
    NodeAgent --> TurnContext
    PythonAgent --> TurnContext
    
    TurnContext --> ActivityProcessing
    ActivityProcessing --> ResponseGeneration
```

Sources: [samples/nodejs/azure-ai-streaming/src/agent.ts:69-70](), [samples/python/auto-signin/src/start_server.py:13-31](), [samples/python/cards/src/start_server.py:13-32]()

## Agent Lifecycle and Processing

The agent processing lifecycle follows a structured pattern from HTTP request to response, with turn-based processing and activity handling.

```mermaid
graph TD
    subgraph "Request Processing"
        IncomingRequest["Incoming HTTP Request"]
        ProcessAsync["adapter.ProcessAsync()"]
        ActivityExtraction["Extract Activity from request"]
    end
    
    subgraph "Turn Processing"
        TurnContext["Create TurnContext"]
        TurnState["Initialize TurnState"]
        ActivityType["Determine ActivityType"]
        HandlerLookup["Find OnActivity handler"]
    end
    
    subgraph "Handler Execution"
        MessageHandler["Execute Message handler"]
        ConversationUpdateHandler["Execute ConversationUpdate handler"]
        CustomHandler["Execute Custom handler"]
        BusinessLogic["Execute business logic"]
    end
    
    subgraph "Response Generation"
        MessageFactory["MessageFactory.Text()"]
        SendActivityAsync["turnContext.SendActivityAsync()"]
        ResponseGeneration["Generate HTTP response"]
    end
    
    IncomingRequest --> ProcessAsync
    ProcessAsync --> ActivityExtraction
    ActivityExtraction --> TurnContext
    TurnContext --> TurnState
    TurnState --> ActivityType
    ActivityType --> HandlerLookup
    HandlerLookup --> MessageHandler
    HandlerLookup --> ConversationUpdateHandler
    HandlerLookup --> CustomHandler
    MessageHandler --> BusinessLogic
    ConversationUpdateHandler --> BusinessLogic
    CustomHandler --> BusinessLogic
    BusinessLogic --> MessageFactory
    MessageFactory --> SendActivityAsync
    SendActivityAsync --> ResponseGeneration
```

Sources: [docs/managingturns.md:1-30](), [docs/usingactivities.md:1-94](), [samples/basic/weather-agent/dotnet/Program.cs:69-72]()

## Activity Handling Patterns

Activities are the core communication units in the SDK. Each language implementation provides different patterns for registering handlers for various activity types.

### Activity Types and Constants

| Activity Type | .NET | Node.js | Python | Purpose |
|---------------|------|---------|---------|---------|
| Message | `ActivityTypes.Message` | `'message'` | `ActivityTypes.message` | Text, media, rich content |
| ConversationUpdate | `ActivityTypes.ConversationUpdate` | `'conversationUpdate'` | `ActivityTypes.conversation_update` | Member events |
| Typing | `ActivityTypes.Typing` | `'typing'` | `ActivityTypes.typing` | Typing indicators |
| Invoke | `ActivityTypes.Invoke` | `'invoke'` | `ActivityTypes.invoke` | Action invocations |

### Language-Specific Handler Registration

#### .NET Handler Pattern

```mermaid
graph TB
    subgraph ".NET Activity Handlers"
        OnActivity["agent.OnActivity(ActivityTypes.Message, handler)"]
        HandlerMethod["async Task Handler(ITurnContext, TurnState, CancellationToken)"]
        ExtractActivity["turnContext.Activity.Text"]
        SendResponse["turnContext.SendActivityAsync(MessageFactory.Text())"]
    end
    
    OnActivity --> HandlerMethod
    HandlerMethod --> ExtractActivity
    ExtractActivity --> SendResponse
```

#### Node.js Handler Pattern

```mermaid
graph TB
    subgraph "Node.js Activity Handlers"
        OnMessage["agent.onMessage('text', handler)"]
        OnConversationUpdate["agent.onConversationUpdate('membersAdded', handler)"]
        OnActivity["agent.onActivity('invoke', handler)"]
        HandlerFunction["async (context: TurnContext, state: TurnState) => {}"]
        ContextSendActivity["context.sendActivity('response')"]
    end
    
    OnMessage --> HandlerFunction
    OnConversationUpdate --> HandlerFunction
    OnActivity --> HandlerFunction
    HandlerFunction --> ContextSendActivity
```

#### Python Decorator Pattern

```mermaid
graph TB
    subgraph "Python Activity Handlers"
        MessageDecorator["@AGENT_APP.message(regex_pattern)"]
        ConversationDecorator["@AGENT_APP.conversation_update('membersAdded')"]
        ActivityDecorator["@AGENT_APP.activity(ActivityTypes.invoke)"]
        HandlerFunction["async def handler(context: TurnContext, state: TurnState)"]
        SendActivity["await context.send_activity(MessageFactory.text())"]
    end
    
    MessageDecorator --> HandlerFunction
    ConversationDecorator --> HandlerFunction
    ActivityDecorator --> HandlerFunction
    HandlerFunction --> SendActivity
```

### Practical Handler Examples

#### Message Handler with Pattern Matching

```mermaid
graph LR
    subgraph "Pattern Matching Examples"
        RegexPattern["re.compile(r'^/(me|profile)$')"]
        StringMatch["'/logout'"]
        ConversationEvent["'membersAdded'"]
    end
    
    subgraph "Handler Logic"
        AuthCheck["auth_handlers=['GRAPH']"]
        TokenRetrieval["await AGENT_APP.auth.get_token()"]
        BusinessLogic["Process user request"]
        ResponseCard["MessageFactory.attachment(card)"]
    end
    
    RegexPattern --> AuthCheck
    StringMatch --> TokenRetrieval
    ConversationEvent --> BusinessLogic
    AuthCheck --> BusinessLogic
    TokenRetrieval --> BusinessLogic
    BusinessLogic --> ResponseCard
```

Sources: [samples/python/auto-signin/src/agent.py:55-93](), [samples/nodejs/azure-ai-streaming/src/agent.ts:9-23](), [samples/python/cards/src/agent.py:40-77]()

## Message Creation and Response Patterns

The SDK provides `MessageFactory` and `CardFactory` classes across all languages for creating different types of messages and responses. Each language implementation follows consistent patterns with language-specific syntax.

### MessageFactory Methods Across Languages

| Message Type | .NET | Node.js | Python | Purpose |
|--------------|------|---------|---------|---------|
| Text | `MessageFactory.Text()` | `context.sendActivity()` | `MessageFactory.text()` | Simple text messages |
| Attachment | `MessageFactory.Attachment()` | `MessageFactory.attachment()` | `MessageFactory.attachment()` | Cards and media |
| Adaptive Card | `CardFactory.AdaptiveCard()` | `CardFactory.adaptiveCard()` | `CardFactory.adaptive_card()` | Rich interactive cards |

### Language-Specific Message Creation

#### .NET Message Creation

```mermaid
graph TB
    subgraph ".NET Response Pattern"
        MessageFactoryText["MessageFactory.Text(string)"]
        MessageFactoryAttachment["MessageFactory.Attachment(attachment)"]
        SendActivityAsync["turnContext.SendActivityAsync(activity, cancellationToken)"]
        IMessageActivity["IMessageActivity result"]
    end
    
    MessageFactoryText --> SendActivityAsync
    MessageFactoryAttachment --> SendActivityAsync
    SendActivityAsync --> IMessageActivity
```

#### Node.js Message Creation

```mermaid
graph TB
    subgraph "Node.js Response Pattern"
        ContextSendActivity["context.sendActivity('text message')"]
        MessageFactoryAttachment["MessageFactory.attachment(cardAttachment)"]
        StreamingResponse["context.streamingResponse.queueTextChunk()"]
        DirectResponse["Direct context method"]
    end
    
    ContextSendActivity --> DirectResponse
    MessageFactoryAttachment --> ContextSendActivity
    StreamingResponse --> DirectResponse
```

#### Python Message Creation

```mermaid
graph TB
    subgraph "Python Response Pattern"
        MessageFactoryText["MessageFactory.text(text_content)"]
        MessageFactoryAttachment["MessageFactory.attachment(attachment)"]
        ContextSendActivity["await context.send_activity(activity)"]
        ActivityResult["Activity delivery"]
    end
    
    MessageFactoryText --> ContextSendActivity
    MessageFactoryAttachment --> ContextSendActivity
    ContextSendActivity --> ActivityResult
```

### Card Creation Examples

#### Adaptive Card Creation

```mermaid
graph TB
    subgraph "Adaptive Card Creation"
        CardDefinition["JSON card definition<br/>adaptive_card.json"]
        CardFactoryCall["CardFactory.adaptive_card(card_json)"]
        AttachmentCreation["Attachment object"]
        MessageWithCard["MessageFactory.attachment(card)"]
        SendToUser["context.send_activity(message)"]
    end
    
    CardDefinition --> CardFactoryCall
    CardFactoryCall --> AttachmentCreation
    AttachmentCreation --> MessageWithCard
    MessageWithCard --> SendToUser
```

#### Hero Card Creation

```mermaid
graph TB
    subgraph "Hero Card Creation"
        HeroCardClass["HeroCard(title, images, buttons)"]
        CardFactoryHero["CardFactory.hero_card(hero_card)"]
        AttachmentGeneration["Attachment with hero card"]
        ActivityCreation["Activity with attachment"]
        ResponseDelivery["Deliver to client"]
    end
    
    HeroCardClass --> CardFactoryHero
    CardFactoryHero --> AttachmentGeneration
    AttachmentGeneration --> ActivityCreation
    ActivityCreation --> ResponseDelivery
```

### Practical Message Examples

#### Text Response Pattern

```mermaid
graph LR
    subgraph "Simple Text Response"
        UserInput["User: 'hello'"]
        ContextActivity["context.activity.text"]
        ResponseText["f'You said: {context.activity.text}'"]
        SendActivity["context.send_activity(MessageFactory.text(response))"]
    end
    
    UserInput --> ContextActivity
    ContextActivity --> ResponseText
    ResponseText --> SendActivity
```

#### Profile Card Response Pattern

```mermaid
graph LR
    subgraph "Profile Card Response"
        AuthToken["user_token_response.token"]
        ApiCall["get_user_info(token)"]
        ProfileCard["create_profile_card(user_info)"]
        AttachmentActivity["MessageFactory.attachment(card)"]
        SendCard["context.send_activity(activity)"]
    end
    
    AuthToken --> ApiCall
    ApiCall --> ProfileCard
    ProfileCard --> AttachmentActivity
    AttachmentActivity --> SendCard
```

Sources: [samples/python/auto-signin/src/agent.py:83-93](), [samples/python/cards/src/card_messages.py:22-200](), [samples/nodejs/azure-ai-streaming/src/agent.ts:9-11](), [samples/python/auto-signin/src/cards.py:1-98]()

## Configuration Patterns Across Languages

Agent configuration varies by language but follows consistent patterns for authentication, AI services, and application settings. Each implementation uses language-appropriate configuration management.

### Configuration File Patterns

| Language | Config File | Loading Method | Example Variables |
|----------|-------------|----------------|-------------------|
| .NET | `appsettings.json` | `IConfiguration` binding | `AgentApplication:*` |
| Node.js | `.env` | `process.env.*` | `clientId`, `tenantId` |
| Python | `.env` | `load_dotenv()` | Environment variables |

### Language-Specific Configuration

#### .NET Configuration Structure

```mermaid
graph TB
    subgraph ".NET Configuration"
        AppSettingsJson["appsettings.json<br/>Structured configuration"]
        AgentApplicationSection["AgentApplication<br/>Core settings"]
        UserAuthorizationSection["UserAuthorization<br/>OAuth settings"]
        AIServicesSection["AIServices<br/>OpenAI/Azure configuration"]
        TokenValidationSection["TokenValidation<br/>JWT validation"]
    end
    
    subgraph "Configuration Binding"
        IConfiguration["IConfiguration interface"]
        AgentApplicationOptions["AgentApplicationOptions binding"]
        DependencyInjection["ServiceCollection registration"]
    end
    
    AppSettingsJson --> AgentApplicationSection
    AppSettingsJson --> UserAuthorizationSection
    AppSettingsJson --> AIServicesSection
    AppSettingsJson --> TokenValidationSection
    
    AgentApplicationSection --> IConfiguration
    IConfiguration --> AgentApplicationOptions
    AgentApplicationOptions --> DependencyInjection
```

#### Node.js Configuration Structure

```mermaid
graph TB
    subgraph "Node.js Configuration"
        EnvFile[".env file<br/>Key-value pairs"]
        ProcessEnv["process.env.*<br/>Environment access"]
        PackageJson["package.json<br/>Dependencies & scripts"]
    end
    
    subgraph "Configuration Usage"
        ClientId["process.env.clientId"]
        TenantId["process.env.tenantId"]
        AzureOpenAI["process.env.AZURE_OPENAI_API_KEY"]
        AgentConstruction["new AgentApplication(config)"]
    end
    
    EnvFile --> ProcessEnv
    ProcessEnv --> ClientId
    ProcessEnv --> TenantId
    ProcessEnv --> AzureOpenAI
    ClientId --> AgentConstruction
    TenantId --> AgentConstruction
    AzureOpenAI --> AgentConstruction
```

#### Python Configuration Structure

```mermaid
graph TB
    subgraph "Python Configuration"
        EnvFile[".env file<br/>Environment variables"]
        LoadDotenv["load_dotenv()<br/>Environment loading"]
        LoadConfigurationFromEnv["load_configuration_from_env(environ)"]
    end
    
    subgraph "Agent Setup"
        AgentsSdkConfig["agents_sdk_config dictionary"]
        MemoryStorageInit["MemoryStorage()"]
        ConnectionManagerInit["MsalConnectionManager(**config)"]
        CloudAdapterInit["CloudAdapter(connection_manager)"]
        AuthorizationInit["Authorization(storage, connection_manager, **config)"]
        AgentApplicationInit["AgentApplication[TurnState](storage, adapter, authorization, **config)"]
    end
    
    EnvFile --> LoadDotenv
    LoadDotenv --> LoadConfigurationFromEnv
    LoadConfigurationFromEnv --> AgentsSdkConfig
    
    AgentsSdkConfig --> MemoryStorageInit
    AgentsSdkConfig --> ConnectionManagerInit
    AgentsSdkConfig --> CloudAdapterInit
    AgentsSdkConfig --> AuthorizationInit
    AgentsSdkConfig --> AgentApplicationInit
```

### Authentication Configuration Examples

#### OAuth Connection Configuration

```mermaid
graph TB
    subgraph "OAuth Configuration Pattern"
        AzureBotService["Azure Bot Service<br/>OAuth connections"]
        ConnectionNames["Connection names<br/>graph_connectionName<br/>github_connectionName"]
        AuthHandlers["Authorization handlers<br/>GRAPH, GITHUB"]
    end
    
    subgraph "Language-Specific Setup"
        DotNetHandlers["appsettings.json<br/>UserAuthorization.Handlers"]
        NodeJSHandlers[".env variables<br/>graph_connectionName="]
        PythonHandlers["Environment variables<br/>Auth handler names"]
    end
    
    AzureBotService --> ConnectionNames
    ConnectionNames --> AuthHandlers
    
    AuthHandlers --> DotNetHandlers
    AuthHandlers --> NodeJSHandlers
    AuthHandlers --> PythonHandlers
```

### AI Service Configuration

#### Azure OpenAI Configuration

```mermaid
graph LR
    subgraph "AI Configuration Variables"
        AzureEndpoint["AZURE_OPENAI_API_INSTANCE_NAME"]
        ApiKey["AZURE_OPENAI_API_KEY"]
        DeploymentName["AZURE_OPENAI_API_DEPLOYMENT_NAME"]
        ModelId["Model ID (gpt-4o-mini)"]
    end
    
    subgraph "Service Initialization"
        AzureClient["Azure OpenAI client"]
        SemanticKernel["Semantic Kernel integration"]
        LangChain["LangChain integration"]
        StreamingResponse["Streaming response setup"]
    end
    
    AzureEndpoint --> AzureClient
    ApiKey --> AzureClient
    DeploymentName --> AzureClient
    ModelId --> AzureClient
    
    AzureClient --> SemanticKernel
    AzureClient --> LangChain
    AzureClient --> StreamingResponse
```

Sources: [samples/dotnet/auto-signin/README.md:39-67](), [samples/nodejs/langchain-multiturn/README.md:16-28](), [samples/python/auto-signin/src/agent.py:28-52](), [samples/nodejs/azure-ai-streaming/README.md:14-21]()

## Storage and State Management

The SDK supports stateless and stateful agent patterns through the `IStorage` interface. State management includes conversation state, user state, and private state.

### Storage Implementations

| Storage Type | Class | Use Case |
|--------------|-------|----------|
| Memory | `MemoryStorage` | Development and testing |
| Blob | `BlobStorage` | Production persistence |
| Cosmos | `CosmosStorage` | Distributed scenarios |
| Custom | `IStorage` implementation | Specialized requirements |

### State Management Pattern

```mermaid
graph LR
    subgraph "State Types"
        ConversationState["Conversation State"]
        UserState["User State"]
        PrivateState["Private State"]
    end
    
    subgraph "Storage Layer"
        IStorage["IStorage interface"]
        MemoryStorage["MemoryStorage"]
        BlobStorage["BlobStorage"]
        CosmosStorage["CosmosStorage"]
    end
    
    subgraph "State Access"
        TurnState["TurnState"]
        StateAccessor["State accessors"]
        StateModification["State modification"]
    end
    
    ConversationState --> IStorage
    UserState --> IStorage
    PrivateState --> IStorage
    IStorage --> MemoryStorage
    IStorage --> BlobStorage
    IStorage --> CosmosStorage
    TurnState --> StateAccessor
    StateAccessor --> StateModification
    StateModification --> IStorage
```

Sources: [docs/managingturns.md:22-30](), [samples/basic/weather-agent/dotnet/Program.cs:57-60](), [samples/basic/azureai-streaming-poem-agent/dotnet/Program.cs:37-41]()

---

