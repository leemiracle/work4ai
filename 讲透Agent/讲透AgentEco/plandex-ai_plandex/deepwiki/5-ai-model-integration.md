<!-- source: DeepWiki mcp.deepwiki.com · repo plandex-ai/plandex · page 5 AI Model Integration · fetched 2026-10-27 -->

# AI Model Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/cli/lib/model_credentials.go](app/cli/lib/model_credentials.go)
- [app/server/model/client.go](app/server/model/client.go)
- [app/server/model/client_stream.go](app/server/model/client_stream.go)
- [app/server/model/model_error.go](app/server/model/model_error.go)
- [app/server/model/plan/tell_stream_error.go](app/server/model/plan/tell_stream_error.go)
- [app/server/types/message.go](app/server/types/message.go)
- [app/shared/ai_models_available.go](app/shared/ai_models_available.go)
- [app/shared/ai_models_data_models.go](app/shared/ai_models_data_models.go)
- [app/shared/ai_models_errors.go](app/shared/ai_models_errors.go)
- [app/shared/ai_models_packs.go](app/shared/ai_models_packs.go)
- [app/shared/ai_models_providers.go](app/shared/ai_models_providers.go)
- [test/smoke_test.sh](test/smoke_test.sh)
- [test/test_utils.sh](test/test_utils.sh)

</details>



This document provides a technical overview of how Plandex integrates with AI models to enable its core code generation, planning, and task execution capabilities. It covers the client initialization process, request handling, response streaming, error management, context formation, and model role configuration. This system forms the bridge between the Plandex application and the external AI providers that power its intelligent coding features.

For information about specific model configurations and model packs, see [Model Configuration](#5.1). For details on context and token management strategies, see [Context and Token Management](#5.2).

## Architecture Overview

The AI model integration in Plandex consists of several interrelated components that work together to enable communication with various AI model providers and optimize the interaction for different scenarios.

```mermaid
flowchart TD
    subgraph "Plandex Server"
        ModelClient["ModelClient"]
        ModelConfig["shared.ModelRoleConfig"]
        StreamManager["ExtendedChatCompletionStream"]
        ContextFormatter["formatModelContext()"]
        ErrorHandler["withRetries()"]
        TokenManager["GetMessagesTokenEstimate()"]
    end
    
    subgraph "External AI Providers"
        OpenAI["OpenAI API"]
        Anthropic["Anthropic API"]
        Google["Google API"]
        OpenRouter["OpenRouter.ai API"]
        Together["Together.ai API"]
    end
    
    ModelClient --> |"API Requests"|OpenAI
    ModelClient --> |"API Requests"|Anthropic
    ModelClient --> |"API Requests"|Google
    ModelClient --> |"API Requests"|OpenRouter
    ModelClient --> |"API Requests"|Together
    
    ModelConfig --> ModelClient
    ModelClient --> StreamManager
    ContextFormatter --> ModelClient
    TokenManager --> ContextFormatter
    ErrorHandler --> ModelClient
```

Sources: `app/server/model/client.go`, `app/server/model/plan/tell_context.go`, `README.md`

## Supported AI Model Providers

Plandex supports multiple AI model providers, allowing users to leverage different models based on their capabilities, cost, and availability:

| Provider | Description | Environment Variable |
|----------|-------------|---------------------|
| OpenAI | Providers of GPT models | `OPENAI_API_KEY` |
| Anthropic | Providers of Claude models | `ANTHROPIC_API_KEY` |
| Google | Providers of Gemini models | `GOOGLE_API_KEY` |
| OpenRouter.ai | Gateway to multiple models | `OPENROUTER_API_KEY` |
| Together.ai | Providers of open-source models | `TOGETHER_API_KEY` |

### Client Initialization Process

The client initialization process establishes connections to the various AI providers using API keys and configuring appropriate endpoints:

```mermaid
sequenceDiagram
    participant Server as "Plandex Server"
    participant InitClients as "InitClients()"
    participant ClientInfo as "ClientInfo struct"
    participant Provider as "AI Provider APIs"
    
    Server->>InitClients: Call with apiKeys, endpoints, openAIEndpoint, orgId
    loop For Each API Key
        InitClients->>ClientInfo: newClient(apiKey, endpoint, orgId)
        Note over ClientInfo: Configure client with proper<br>authentication and endpoint
        ClientInfo->>Provider: Initialize connection
    end
    InitClients->>Server: Return map of configured clients
```

Sources: `app/server/model/client.go:42-56`, `app/server/model/client.go:58-73`

## Client Configuration

Each AI provider requires specific configuration, which is handled through the `ClientInfo` struct and the initialization process:

```go
type ClientInfo struct {
    Client   *openai.Client
    ApiKey   string
    OrgId    string
    Endpoint string
}
```

Configuration options include:
- **Custom Endpoints**: Set via the `OPENAI_ENDPOINT` environment variable
- **Organization ID**: For OpenAI multi-org accounts via `OPENAI_ORG_ID`
- **Provider-specific Headers**: Such as OpenRouter's region and preference settings

Sources: `app/server/model/client.go:35-40`, `releases/server/versions/0.8.3.md:2-4`

## Request Processing Flow

The system uses a robust request processing flow to communicate with AI models:

```mermaid
flowchart TD
    Start["ModelRequest()"]
    Filter["FilterEmptyMessages()"]
    Estimate["GetMessagesTokenEstimate()"]
    SelectModel["modelConfig.GetRoleForInputTokens()"]
    CreateReq["Create ExtendedChatCompletionRequest"]
    ExecHook["Execute WillSendModelRequest hook"]
    SendReq["CreateChatCompletionWithInternalStream()"]
    Process["Process model response"]
    TrackUsage["Track token usage with DidSendModelRequest hook"]
    End["Return ModelResponse"]
    
    Start --> Filter
    Filter --> Estimate
    Estimate --> SelectModel
    SelectModel --> CreateReq
    CreateReq --> ExecHook
    ExecHook --> SendReq
    SendReq --> Process
    Process --> TrackUsage
    TrackUsage --> End
```

Sources: `app/server/model/model_request.go:45-187`, `app/server/model/model_request.go:189-206`

## Message Formatting

Plandex extends the standard OpenAI message format to accommodate additional features:

```mermaid
classDiagram
    class ExtendedChatMessage {
        +Role string
        +Content []ExtendedChatMessagePart
        +ToOpenAI() *openai.ChatCompletionMessage
    }
    
    class ExtendedChatMessagePart {
        +Type string
        +Text string
        +ImageURL *openai.ChatMessageImageURL
        +CacheControl *CacheControlSpec
    }
    
    class ExtendedChatCompletionRequest {
        +Model shared.ModelName
        +Messages []ExtendedChatMessage
        +Temperature float32
        +TopP float32
        +Stop []string
        +Tools []openai.Tool
        +ToolChoice any
        +Prediction *OpenAIPrediction
        +Provider *OpenRouterProviderConfig
        +IncludeReasoning bool
        +ToOpenAI() *ExtendedOpenAIChatCompletionRequest
    }
    
    ExtendedChatMessage --> ExtendedChatMessagePart: Contains
    ExtendedChatCompletionRequest --> ExtendedChatMessage: Contains
```

Sources: `app/server/types/message.go:22-32`, `app/server/types/message.go:34-57`, `app/server/types/message.go:69-124`

## Streaming Response Handling

Streaming is a critical feature for providing real-time feedback during code generation. The system implements a sophisticated streaming mechanism:

```mermaid
sequenceDiagram
    participant Client as "Plandex Client"
    participant Server as "Plandex Server"
    participant streamState as "activeTellStreamState"
    participant streamManager as "ExtendedChatCompletionStream"
    participant Provider as "AI Provider API"
    
    Client->>Server: Request generation
    Server->>streamState: execTellPlan()
    streamState->>Provider: CreateChatCompletionStream()
    Provider-->>streamState: Return stream object
    streamState->>streamState: listenStream(stream)
    
    loop For Each Chunk
        streamState->>streamManager: Recv()
        streamManager->>Provider: Get next chunk
        Provider-->>streamManager: Return chunk
        streamManager-->>streamState: Return processed chunk
        streamState->>streamState: processChunk()
        streamState-->>Client: Stream update
    end
    
    Provider-->>streamManager: Stream end signal
    streamManager-->>streamState: Signal completion
    streamState->>streamState: handleStreamFinished()
    streamState->>streamState: storeOnFinished()
    streamState-->>Client: Completed response
```

The streaming system includes:
- **Timeout Management**: Handles inactivity with configurable timeouts
- **Retry Logic**: Automatically retries failed requests with backoff
- **Chunk Processing**: Parses and processes stream chunks
- **State Management**: Tracks and updates the state of the streaming process

Sources: `app/server/model/client.go:75-108`, `app/server/model/plan/tell_stream_main.go:17-251`, `app/server/model/plan/tell_stream_finish.go:17-248`

## Error Handling and Retries

The system implements robust error handling with sophisticated retry logic:

```mermaid
flowchart TD
    Start["withRetries()"]
    Attempt["Execute operation()"]
    CheckError{"Error occurred?"}
    CheckRetryable{"isNonRetriableErr()"}
    CheckMaxRetries{"numRetry >= OPENAI_MAX_RETRIES"}
    ParseRetryTime["parseRetryAfter()"]
    HasDuration{"duration != nil"}
    CalcWait["Calculate wait with OPENAI_BACKOFF_MULTIPLIER"]
    CheckAbort{"waitDuration > OPENAI_ABORT_WAIT_DURATION"}
    CheckMax{"waitDuration > OPENAI_MAX_WAIT_DURATION"}
    SetMax["waitDuration = OPENAI_MAX_WAIT_DURATION"]
    UseBackoff["waitBackoff(numRetry)"]
    Wait["time.Sleep(waitDuration)"]
    Increment["numRetry++"]
    Return["Return result"]
    ReturnError["Return error"]
    
    Start --> Attempt
    Attempt --> CheckError
    CheckError -- "No" --> Return
    CheckError -- "Yes" --> CheckRetryable
    CheckRetryable -- "Yes" --> ReturnError
    CheckRetryable -- "No" --> CheckMaxRetries
    CheckMaxRetries -- "Yes" --> ReturnError
    CheckMaxRetries -- "No" --> ParseRetryTime
    ParseRetryTime --> HasDuration
    HasDuration -- "Yes" --> CalcWait
    HasDuration -- "No" --> UseBackoff
    CalcWait --> CheckAbort
    CheckAbort -- "Yes" --> ReturnError
    CheckAbort -- "No" --> CheckMax
    CheckMax -- "Yes" --> SetMax
    CheckMax -- "No" --> Wait
    SetMax --> Wait
    UseBackoff --> Wait
    Wait --> Increment
    Increment --> Attempt
```

Key error handling features:
1. **Error Classification**: Categorizes errors as retryable or non-retryable
2. **Exponential Backoff**: Increases wait time between retries
3. **Rate Limit Handling**: Respects provider rate limit headers
4. **Maximum Retries**: Caps retry attempts to prevent endless loops

Sources: `app/server/model/client.go:408-434`, `app/server/model/client.go:436-440`, `app/server/model/client.go:544-589`

## Context Management

The context management system ensures AI models have the necessary information while optimizing token usage:

```mermaid
flowchart TD
    Start["formatModelContext()"]
    InitContext["Initialize context bodies"]
    FilterContext["Apply context filters"]
    CollectFiles["Collect files to include"]
    SortByRelevance["Sort by relevance if ordered"]
    ProcessFiles["Process each file up to token limit"]
    FormatMessages["Format as ExtendedChatMessagePart"]
    AddImages["Add image context if present"]
    AddApplyScript["Add _apply.sh script if needed"]
    AddEnd["Add END OF CONTEXT marker"]
    Return["Return formatted context"]
    
    Start --> InitContext
    InitContext --> FilterContext
    FilterContext --> CollectFiles
    CollectFiles --> SortByRelevance
    SortByRelevance --> ProcessFiles
    ProcessFiles --> FormatMessages
    FormatMessages --> AddImages
    AddImages --> AddApplyScript
    AddApplyScript --> AddEnd
    AddEnd --> Return
```

Context management features:
1. **Smart Context Selection**: Prioritizes relevant files based on current task
2. **Auto-Loading**: Automatically identifies and loads files referenced in the plan
3. **Token Management**: Ensures context stays within model token limits
4. **Context Caching**: Optimizes performance and costs through caching

Sources: `app/server/model/plan/tell_context.go:16-366`, `app/server/model/plan/tell_context.go:368-443`

## Model Roles System

Plandex uses a sophisticated role-based system for AI models, where different models are configured for specific tasks:

```mermaid
flowchart TD
    subgraph "ModelPack System"
        ModelPack["ModelPack Configuration"]
        ModelRoleConfigs["ModelRoleConfig instances"]
    end
    
    subgraph "Model Roles"
        Architect["Architect\n(System Design)"]
        Planner["Planner\n(Task Planning)"]
        Coder["Coder\n(Code Generation)"]
        Builder["Builder\n(Integration)"]
        Verifier["Verifier\n(Validation)"]
        AutoFix["AutoFix\n(Bug Fixing)"]
    end
    
    subgraph "Model Selection Process"
        EstimateTokens["GetMessagesTokenEstimate()"]
        SelectRole["GetRoleForInputTokens()"]
        CreateRequest["ModelRequest() in model_request.go"]
        SendRequest["CreateChatCompletionStream() in client.go"]
    end
    
    ModelPack --> ModelRoleConfigs
    ModelRoleConfigs --> Architect
    ModelRoleConfigs --> Planner
    ModelRoleConfigs --> Coder
    ModelRoleConfigs --> Builder
    ModelRoleConfigs --> Verifier
    ModelRoleConfigs --> AutoFix
    
    EstimateTokens --> SelectRole
    SelectRole --> CreateRequest
    CreateRequest --> SendRequest
```

The role system allows for:
1. **Specialized Models**: Different models optimized for different tasks
2. **Parameter Tuning**: Role-specific temperature, top_p, and other settings
3. **Token Management**: Role-specific token limits and prioritization
4. **Cost Optimization**: Using lower-cost models for appropriate tasks

Sources: `app/server/model/model_request.go:16-44`, `app/server/model/model_request.go:73-74`

## Provider-Specific Optimizations

The system includes various optimizations for specific providers:

1. **OpenRouter optimizations**:
   - Adding the `:nitro` suffix to choose the fastest provider
   - Setting headers for region preferences and throughput
   - Configuring referer information

2. **OpenAI optimizations**:
   - Support for organization ID
   - Custom endpoints
   - Handling system prompt disabling for models that don't support it

3. **Streaming optimizations**:
   - Timeouts tuned by provider (30s for chunks, 5s for usage)
   - Provider-specific response parsing
   - Fallback handling for differently structured responses

Sources: `app/server/model/client.go:110-125`, `app/server/model/client.go:459-528`, `app/server/model/client.go:592-599`

## Usage Tracking

The system tracks AI model usage through hooks that record token usage, models used, and other metrics:

```mermaid
sequenceDiagram
    participant Server as "Plandex Server"
    participant ModelRequest as "ModelRequest()"
    participant AI as "AI Provider"
    participant Hooks as "hooks.ExecHook()"
    
    Server->>ModelRequest: Make request with parameters
    ModelRequest->>Hooks: WillSendModelRequest hook
    Hooks-->>ModelRequest: Continue if allowed
    ModelRequest->>AI: Send request to provider
    AI-->>ModelRequest: Return response
    ModelRequest->>Hooks: DidSendModelRequest hook
    Note over Hooks: Record usage metrics:<br>- Input tokens<br>- Output tokens<br>- Cached tokens<br>- Model name & provider<br>- Purpose & generation ID
    Hooks-->>ModelRequest: Processing complete
    ModelRequest-->>Server: Return final response
```

Usage tracking includes:
- Input, output, and cached token counts
- Model identification (name, provider, role)
- Purpose categorization
- Request timing metrics
- Content generation IDs

Sources: `app/server/model/model_request.go:151-184`

## Conclusion

Plandex's AI Model Integration system provides a robust, flexible interface to various AI providers while handling the complexities of token management, streaming, error handling, and provider-specific optimizations. This system forms the foundation for Plandex's AI-powered capabilities, allowing it to leverage multiple models for different aspects of the development process while maintaining a consistent interface for the rest of the application.

---

