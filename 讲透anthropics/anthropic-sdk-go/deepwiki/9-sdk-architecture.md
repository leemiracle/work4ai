<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/anthropic-sdk-go · page 9 SDK Architecture · fetched 2026-10-26 -->

# SDK Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [aliases.go](aliases.go)
- [betamessageutil.go](betamessageutil.go)
- [client.go](client.go)
- [internal/apierror/apierror.go](internal/apierror/apierror.go)
- [internal/apijson/subfield.go](internal/apijson/subfield.go)
- [internal/requestconfig/requestconfig.go](internal/requestconfig/requestconfig.go)
- [message.go](message.go)
- [messageutil.go](messageutil.go)
- [option/requestoption.go](option/requestoption.go)
- [packages/pagination/pagination.go](packages/pagination/pagination.go)

</details>



This document explains the internal design and architecture of the Anthropic Go SDK for advanced users and contributors. It covers the core architectural patterns, code organization, request execution flow, and key design decisions that enable the SDK's functionality.

For detailed information on specific architectural subsystems, see:
- Type system implementation and discriminated unions: [Type System and Unions](#9.1)
- Request middleware and transformation pipeline: [Middleware and Request Pipeline](#9.2)
- Retry mechanism and timeout management: [Retry and Timeout Logic](#9.3)
- OpenAPI-driven code generation process: [Code Generation](#9.4)

## Core Architectural Components

The SDK is structured around several key architectural layers that work together to provide a type-safe, extensible interface to the Anthropic API.

### Client and Service Composition

```mermaid
graph TB
    Client["anthropic.Client<br/>(client.go:18-27)"]
    Options["[]option.RequestOption<br/>(client.go:22)"]
    
    CompletionService["CompletionService<br/>(client.go:23)"]
    MessageService["MessageService<br/>(client.go:24)"]
    ModelService["ModelService<br/>(client.go:25)"]
    BetaService["BetaService<br/>(client.go:26)"]
    
    MessageBatchService["MessageBatchService<br/>(message.go:32)"]
    BetaMessageService["BetaMessageService"]
    BetaFileService["BetaFileService"]
    
    NewClient["NewClient()<br/>(client.go:50-61)"]
    DefaultClientOptions["DefaultClientOptions()<br/>(client.go:32-44)"]
    
    EnvVars["Environment Variables:<br/>ANTHROPIC_API_KEY<br/>ANTHROPIC_AUTH_TOKEN<br/>ANTHROPIC_BASE_URL"]
    
    NewClient --> DefaultClientOptions
    DefaultClientOptions --> EnvVars
    NewClient --> Client
    Client --> Options
    Client --> CompletionService
    Client --> MessageService
    Client --> ModelService
    Client --> BetaService
    
    MessageService --> MessageBatchService
    BetaService --> BetaMessageService
    BetaService --> BetaFileService
    
    Options -.propagates to.-> CompletionService
    Options -.propagates to.-> MessageService
    Options -.propagates to.-> ModelService
    Options -.propagates to.-> BetaService
```

The SDK follows a compositional pattern where the top-level `Client` struct aggregates specialized service structs. Each service encapsulates operations for a specific API domain (Messages, Models, Completions, Beta features). Services are instantiated with a shared set of `RequestOption` values that propagate configuration throughout the request lifecycle.

**Sources:** [client.go:18-61](), [message.go:24-43]()

### Request Configuration Architecture

```mermaid
graph TB
    subgraph "Configuration Types"
        RequestOption["RequestOption<br/>(interface)"]
        RequestOptionFunc["RequestOptionFunc<br/>(requestconfig.go:84)"]
        PreRequestOptionFunc["PreRequestOptionFunc<br/>(requestconfig.go:85)"]
    end
    
    subgraph "RequestConfig Structure"
        RequestConfig["RequestConfig<br/>(requestconfig.go:203-225)"]
        MaxRetries["MaxRetries int<br/>(requestconfig.go:204)"]
        RequestTimeout["RequestTimeout time.Duration<br/>(requestconfig.go:205)"]
        Context["Context context.Context<br/>(requestconfig.go:206)"]
        Request["Request *http.Request<br/>(requestconfig.go:207)"]
        BaseURL["BaseURL *url.URL<br/>(requestconfig.go:208)"]
        HTTPClient["HTTPClient *http.Client<br/>(requestconfig.go:213)"]
        Middlewares["Middlewares []middleware<br/>(requestconfig.go:214)"]
        APIKey["APIKey string<br/>(requestconfig.go:215)"]
        AuthToken["AuthToken string<br/>(requestconfig.go:216)"]
        Body["Body io.Reader<br/>(requestconfig.go:224)"]
    end
    
    subgraph "Configuration Flow"
        NewRequestConfig["NewRequestConfig()<br/>(requestconfig.go:90-191)"]
        Apply["Apply(opts)<br/>(requestconfig.go:595-603)"]
        Execute["Execute()<br/>(requestconfig.go:377-558)"]
    end
    
    RequestOption --> RequestOptionFunc
    RequestOption --> PreRequestOptionFunc
    
    RequestConfig --> MaxRetries
    RequestConfig --> RequestTimeout
    RequestConfig --> Context
    RequestConfig --> Request
    RequestConfig --> BaseURL
    RequestConfig --> HTTPClient
    RequestConfig --> Middlewares
    RequestConfig --> APIKey
    RequestConfig --> AuthToken
    RequestConfig --> Body
    
    NewRequestConfig --> RequestConfig
    RequestConfig --> Apply
    Apply --> Execute
    
    RequestOptionFunc -.applies to.-> RequestConfig
    PreRequestOptionFunc -.applies to.-> RequestConfig
```

The `RequestConfig` struct ([requestconfig.go:203-225]()) is the central coordination point for all request execution. It accumulates configuration from multiple sources and provides the execution context for HTTP operations. The configuration system uses a functional options pattern where `RequestOption` interfaces ([option/requestoption.go:23]()) can be applied at client, service, or method levels.

**Sources:** [internal/requestconfig/requestconfig.go:90-225](), [option/requestoption.go:18-93]()

### Type System Organization

```mermaid
graph TB
    subgraph "Response Types"
        Message["Message<br/>(message.go)"]
        ContentBlockUnion["ContentBlockUnion<br/>(discriminated union)"]
        TextBlock["TextBlock"]
        ToolUseBlock["ToolUseBlock"]
        ThinkingBlock["ThinkingBlock"]
        ImageBlock["ImageBlock"]
    end
    
    subgraph "Request Parameter Types"
        MessageNewParams["MessageNewParams<br/>(message.go)"]
        MessageParam["MessageParam"]
        ContentBlockParamUnion["ContentBlockParamUnion<br/>(discriminated union)"]
        TextBlockParam["TextBlockParam"]
        ToolUseBlockParam["ToolUseBlockParam"]
    end
    
    subgraph "Conversion Methods"
        ToParam["ToParam()<br/>(messageutil.go:93-101)"]
        toParamUnion["toParamUnion()<br/>(messageutil.go:107-135)"]
    end
    
    subgraph "JSON Handling"
        UnmarshalJSON["UnmarshalJSON<br/>(apijson package)"]
        MarshalJSON["MarshalJSON<br/>(param package)"]
        RawJSON["RawJSON() string<br/>(respjson metadata)"]
    end
    
    Message --> ContentBlockUnion
    ContentBlockUnion --> TextBlock
    ContentBlockUnion --> ToolUseBlock
    ContentBlockUnion --> ThinkingBlock
    ContentBlockUnion --> ImageBlock
    
    MessageNewParams --> MessageParam
    MessageParam --> ContentBlockParamUnion
    ContentBlockParamUnion --> TextBlockParam
    ContentBlockParamUnion --> ToolUseBlockParam
    
    Message --> ToParam
    ToParam --> MessageParam
    ContentBlockUnion --> toParamUnion
    toParamUnion --> ContentBlockParamUnion
    
    Message --> UnmarshalJSON
    Message --> RawJSON
    MessageNewParams --> MarshalJSON
```

The SDK maintains a strict separation between **response types** (used for API responses) and **request parameter types** (used for API requests). Response types include metadata fields for JSON tracking and provide `ToParam()` conversion methods. Parameter types use the `param.Field` system for optional field handling and support zero-value elision.

**Sources:** [message.go:1-100](), [messageutil.go:91-226]()

## Request Execution Flow

The request execution pipeline transforms high-level API calls into HTTP requests and responses through a series of well-defined stages.

### End-to-End Request Pipeline

```mermaid
graph TB
    subgraph "1. Request Initiation"
        ServiceMethod["Service Method Call<br/>e.g., Messages.New()"]
        BodyParams["Body Parameters<br/>(e.g., MessageNewParams)"]
    end
    
    subgraph "2. Request Configuration"
        NewRequestConfig["NewRequestConfig()<br/>(requestconfig.go:90)"]
        SerializeBody["Serialize Body<br/>(JSON/Multipart/Query)<br/>(requestconfig.go:96-146)"]
        CreateHTTPRequest["http.NewRequestWithContext()<br/>(requestconfig.go:148)"]
        SetHeaders["Set Headers<br/>(User-Agent, Auth, Beta)<br/>(requestconfig.go:152-165)"]
        ApplyOptions["Apply RequestOptions<br/>(requestconfig.go:174)"]
    end
    
    subgraph "3. Execution Pipeline"
        Execute["Execute()<br/>(requestconfig.go:377)"]
        ResolveBaseURL["Resolve Base URL<br/>(requestconfig.go:378-389)"]
        SetupBody["Setup Request Body<br/>(requestconfig.go:391-412)"]
        BuildMiddlewareChain["Build Middleware Chain<br/>(requestconfig.go:414-420)"]
    end
    
    subgraph "4. HTTP Execution"
        RetryLoop["Retry Loop<br/>(requestconfig.go:427-471)"]
        SetTimeout["Set Request Timeout<br/>(requestconfig.go:429-437)"]
        CloneRequest["Clone Request<br/>(requestconfig.go:439)"]
        MiddlewareExecution["Execute Middleware Chain<br/>(requestconfig.go:444)"]
        HTTPDo["HTTP Client.Do()<br/>(requestconfig.go:414-417)"]
    end
    
    subgraph "5. Response Processing"
        CheckRetry["shouldRetry()<br/>(requestconfig.go:241-266)"]
        RetryDelay["retryDelay()<br/>(requestconfig.go:358-375)"]
        CheckStatusCode["Check Status Code<br/>(requestconfig.go:489)"]
        DeserializeError["Deserialize Error<br/>(requestconfig.go:490-506)"]
        DeserializeResponse["Deserialize Response<br/>(requestconfig.go:521-556)"]
    end
    
    ServiceMethod --> BodyParams
    BodyParams --> NewRequestConfig
    NewRequestConfig --> SerializeBody
    SerializeBody --> CreateHTTPRequest
    CreateHTTPRequest --> SetHeaders
    SetHeaders --> ApplyOptions
    
    ApplyOptions --> Execute
    Execute --> ResolveBaseURL
    ResolveBaseURL --> SetupBody
    SetupBody --> BuildMiddlewareChain
    
    BuildMiddlewareChain --> RetryLoop
    RetryLoop --> SetTimeout
    SetTimeout --> CloneRequest
    CloneRequest --> MiddlewareExecution
    MiddlewareExecution --> HTTPDo
    
    HTTPDo --> CheckRetry
    CheckRetry -->|Retry| RetryDelay
    RetryDelay --> RetryLoop
    CheckRetry -->|No Retry| CheckStatusCode
    CheckStatusCode -->|>= 400| DeserializeError
    CheckStatusCode -->|< 400| DeserializeResponse
```

Each request flows through this pipeline, with options applied at multiple stages. The retry loop ([requestconfig.go:427-471]()) handles transient failures, and the middleware chain ([requestconfig.go:418-420]()) enables request/response transformation.

**Sources:** [internal/requestconfig/requestconfig.go:90-558](), [message.go:55-69]()

### Middleware Chain Architecture

```mermaid
graph LR
    subgraph "Middleware Types"
        Middleware["Middleware<br/>func(*Request, Next) (*Response, error)<br/>(option/requestoption.go:83)"]
        MiddlewareNext["MiddlewareNext<br/>func(*Request) (*Response, error)<br/>(option/requestoption.go:78)"]
    end
    
    subgraph "Middleware Chain"
        MW1["Custom Middleware 1"]
        MW2["Custom Middleware 2"]
        BedrockMW["Bedrock Middleware<br/>(cloud/bedrock)"]
        VertexMW["Vertex Middleware<br/>(cloud/vertex)"]
        HTTPHandler["HTTP Client.Do<br/>(final handler)"]
    end
    
    subgraph "Chain Construction"
        ApplyMiddleware["applyMiddleware()<br/>(requestconfig.go:235-239)"]
        BuildChain["Build Chain in Reverse<br/>(requestconfig.go:418-420)"]
    end
    
    Middleware -.defines.-> MW1
    Middleware -.defines.-> MW2
    Middleware -.defines.-> BedrockMW
    Middleware -.defines.-> VertexMW
    
    BuildChain --> MW1
    MW1 --> MW2
    MW2 --> BedrockMW
    BedrockMW --> VertexMW
    VertexMW --> HTTPHandler
    
    ApplyMiddleware -.wraps.-> MW1
    ApplyMiddleware -.wraps.-> MW2
```

Middleware functions are applied in reverse order during chain construction ([requestconfig.go:418-420]()), so the first middleware registered executes first. This enables request transformation (e.g., for AWS Bedrock or Google Vertex AI) before the HTTP request is sent. Each middleware can inspect, modify, or short-circuit the request/response cycle.

**Sources:** [internal/requestconfig/requestconfig.go:229-239](), [option/requestoption.go:76-92]()

## Code Organization

### File Structure and Responsibilities

The SDK follows a layered architecture with clear separation of concerns:

| Directory/File | Purpose |
|----------------|---------|
| `client.go` | Top-level client initialization and service aggregation |
| `message.go`, `completion.go`, `model.go` | Service implementations for each API domain |
| `betamessage.go`, `betabatch.go`, etc. | Beta feature implementations |
| `messageutil.go`, `betamessageutil.go` | Type conversion utilities (response → request params) |
| `internal/requestconfig/` | Core request execution and configuration logic |
| `internal/apierror/` | Error type definitions and deserialization |
| `internal/apijson/` | JSON unmarshaling with metadata tracking |
| `option/` | Public API for request configuration options |
| `packages/param/` | Parameter encoding and optional field handling |
| `packages/pagination/` | Generic pagination support |
| `packages/ssestream/` | Server-sent events streaming |
| `shared/` | Shared types used across multiple services |
| `cloud/bedrock/`, `cloud/vertex/` | Cloud platform integration middleware |

**Sources:** [client.go:1-158](), [message.go:1-100]()

### Service Pattern Implementation

```mermaid
graph TB
    subgraph "Service Structure"
        MessageService["MessageService<br/>(message.go:30-33)"]
        Options["Options []option.RequestOption<br/>(message.go:31)"]
        Batches["Batches MessageBatchService<br/>(message.go:32)"]
    end
    
    subgraph "Service Methods"
        New["New(ctx, params, opts)<br/>(message.go:55-69)"]
        NewStreaming["NewStreaming(ctx, params, opts)<br/>(message.go:81-91)"]
        CountTokens["CountTokens(ctx, params, opts)<br/>(message.go:100-105)"]
    end
    
    subgraph "Method Implementation Pattern"
        MergeOpts["Merge Service & Method Options<br/>slices.Concat(r.Options, opts)<br/>(message.go:56)"]
        CalculateTimeout["CalculateNonStreamingTimeout<br/>(message.go:60-64)"]
        ExecuteRequest["ExecuteNewRequest()<br/>(message.go:67)"]
    end
    
    MessageService --> Options
    MessageService --> Batches
    MessageService --> New
    MessageService --> NewStreaming
    MessageService --> CountTokens
    
    New --> MergeOpts
    MergeOpts --> CalculateTimeout
    CalculateTimeout --> ExecuteRequest
```

Each service struct ([message.go:30-33]()) holds a slice of `RequestOption` values inherited from the parent client. Service methods merge these with method-specific options using `slices.Concat()` ([message.go:56]()), ensuring that options cascade properly: client → service → method. This pattern is consistent across all services.

**Sources:** [message.go:24-105](), [client.go:50-61]()

### Type Conversion Architecture

The SDK provides bidirectional conversion between response types and request parameter types through a consistent pattern:

```mermaid
graph TB
    subgraph "Response Type"
        Message["Message<br/>(API response)"]
        ContentBlockUnion["ContentBlockUnion<br/>(discriminated union)"]
        TextBlock["TextBlock<br/>- Text string<br/>- Citations []TextCitationUnion<br/>- Type constant<br/>+ JSON metadata"]
    end
    
    subgraph "Conversion Layer"
        ToParam["Message.ToParam()<br/>(messageutil.go:93-101)"]
        toParamUnion["ContentBlockUnion.ToParam()<br/>→ toParamUnion()<br/>(messageutil.go:103-135)"]
        TextBlockToParam["TextBlock.ToParam()<br/>(messageutil.go:201-217)"]
    end
    
    subgraph "Request Param Type"
        MessageParam["MessageParam<br/>(request parameter)"]
        ContentBlockParamUnion["ContentBlockParamUnion<br/>(discriminated union)"]
        TextBlockParam["TextBlockParam<br/>- Text string<br/>- Citations []TextCitationParamUnion<br/>- Type constant<br/>- CacheControl (optional)"]
    end
    
    Message --> ToParam
    ToParam --> MessageParam
    ContentBlockUnion --> toParamUnion
    toParamUnion --> ContentBlockParamUnion
    TextBlock --> TextBlockToParam
    TextBlockToParam --> TextBlockParam
```

The `ToParam()` methods ([messageutil.go:93-217]()) enable users to easily reuse API responses in subsequent requests, such as in multi-turn conversations. The conversion preserves semantic meaning while transforming from response-oriented types (with JSON metadata) to request-oriented types (with optional field handling).

**Sources:** [messageutil.go:91-226](), [betamessageutil.go:1-460]()

## Design Patterns

### Discriminated Union Pattern

The SDK extensively uses discriminated unions to represent polymorphic types in a type-safe manner:

```mermaid
graph TB
    subgraph "Union Type Structure"
        ContentBlockUnion["ContentBlockUnion<br/>(message.go)"]
        Type["Type string<br/>(discriminator field)"]
        TextFields["Text string<br/>Citations []TextCitationUnion<br/>(text variant fields)"]
        ToolUseFields["ID string<br/>Name string<br/>Input json.RawMessage<br/>(tool_use variant fields)"]
        JSON["JSON struct<br/>(metadata with raw JSON)"]
    end
    
    subgraph "Union Methods"
        AsAny["AsAny() anyContentBlock<br/>(type switch helper)"]
        AsTextBlock["AsTextBlock() TextBlock"]
        AsToolUseBlock["AsToolUseBlock() ToolUseBlock"]
        ToParam["ToParam() ContentBlockParamUnion"]
    end
    
    subgraph "Variant Types"
        TextBlock["TextBlock"]
        ToolUseBlock["ToolUseBlock"]
        ThinkingBlock["ThinkingBlock"]
        ImageBlock["ImageBlock"]
    end
    
    ContentBlockUnion --> Type
    ContentBlockUnion --> TextFields
    ContentBlockUnion --> ToolUseFields
    ContentBlockUnion --> JSON
    
    ContentBlockUnion --> AsAny
    ContentBlockUnion --> AsTextBlock
    ContentBlockUnion --> AsToolUseBlock
    ContentBlockUnion --> ToParam
    
    AsAny -->|"type == 'text'"| TextBlock
    AsAny -->|"type == 'tool_use'"| ToolUseBlock
    AsAny -->|"type == 'thinking'"| ThinkingBlock
```

Union types contain all fields from all variants in a flattened structure. The `Type` field acts as the discriminator. The `AsAny()` method uses type switching to safely cast to the correct variant type, returning `nil` for invalid types. This pattern is used throughout: `ContentBlockUnion`, `ToolChoiceUnion`, `MessageStreamEventUnion`, etc.

**Sources:** [message.go:1000-1500]() (ContentBlockUnion definition)

### Optional Field Handling

```mermaid
graph LR
    subgraph "Response Type"
        Field["Field string<br/>(always present in struct)"]
        JSONMeta["JSON.Field respjson.Field<br/>(tracks presence)"]
    end
    
    subgraph "Check Methods"
        Valid["JSON.Field.Valid()<br/>→ bool"]
        IsNull["JSON.Field.IsNull()<br/>→ bool"]
    end
    
    subgraph "Request Param Type"
        ParamField["Field param.Opt[string]<br/>(explicit optional)"]
        IsOmitted["param.IsOmitted()<br/>→ bool"]
    end
    
    Field --> JSONMeta
    JSONMeta --> Valid
    JSONMeta --> IsNull
    
    ParamField --> IsOmitted
```

Response types use the `respjson.Field` metadata pattern ([internal/apijson/subfield.go:1-68]()) to track whether a field was present in the API response, enabling distinction between absent, null, and zero-value fields. Request parameter types use `param.Opt[T]` and `param.Field[T]` types to control whether fields are included in the serialized JSON, supporting zero-value elision.

**Sources:** [internal/apijson/subfield.go:1-68](), [messageutil.go:155-199]()

### Streaming Accumulation Pattern

```mermaid
graph TB
    subgraph "Streaming Flow"
        NewStreaming["NewStreaming(ctx, params)<br/>→ *Stream[Event]"]
        StreamNext["stream.Next()<br/>→ bool"]
        StreamCurrent["stream.Current()<br/>→ Event"]
    end
    
    subgraph "Accumulation"
        Message["message := Message{}"]
        AccumulateLoop["for stream.Next()<br/>  message.Accumulate(stream.Current())"]
        AccumulateMethod["message.Accumulate(event)<br/>(messageutil.go:20-89)"]
    end
    
    subgraph "Event Types"
        MessageStartEvent["MessageStartEvent<br/>(initializes message)"]
        ContentBlockStartEvent["ContentBlockStartEvent<br/>(adds content block)"]
        ContentBlockDeltaEvent["ContentBlockDeltaEvent<br/>(appends to current block)"]
        MessageStopEvent["MessageStopEvent<br/>(finalizes message)"]
    end
    
    NewStreaming --> StreamNext
    StreamNext --> StreamCurrent
    StreamCurrent --> Message
    Message --> AccumulateLoop
    AccumulateLoop --> AccumulateMethod
    
    AccumulateMethod --> MessageStartEvent
    AccumulateMethod --> ContentBlockStartEvent
    AccumulateMethod --> ContentBlockDeltaEvent
    AccumulateMethod --> MessageStopEvent
```

The `Accumulate()` method ([messageutil.go:20-89]()) enables incremental construction of a complete `Message` from streaming events. It handles event-specific logic: `MessageStartEvent` initializes the message, `ContentBlockStartEvent` appends new blocks, `ContentBlockDeltaEvent` updates the current block, and `MessageStopEvent` finalizes JSON metadata. This pattern provides a simple API for consuming streams while maintaining full type safety.

**Sources:** [messageutil.go:20-89](), [betamessageutil.go:20-93](), [message.go:81-91]()

## Extensibility Points

The SDK provides several well-defined extension mechanisms for advanced use cases:

### Custom Middleware

Middleware can be injected using `option.WithMiddleware()` ([option/requestoption.go:87-92]()):

```mermaid
graph LR
    WithMiddleware["option.WithMiddleware(mw)<br/>(requestoption.go:87)"]
    CustomMiddleware["func(req *http.Request, next MiddlewareNext)<br/>  (*http.Response, error)"]
    RequestConfig["requestconfig.RequestConfig<br/>Middlewares []middleware"]
    MiddlewareChain["Middleware Chain Execution<br/>(requestconfig.go:418-420)"]
    
    WithMiddleware --> CustomMiddleware
    CustomMiddleware --> RequestConfig
    RequestConfig --> MiddlewareChain
```

Middleware functions receive the request and a `next` function. They can:
- Inspect or modify the request before calling `next(req)`
- Inspect or modify the response after calling `next(req)`
- Short-circuit execution by not calling `next` and returning directly
- Implement cross-cutting concerns like logging, metrics, or platform-specific transformations (AWS Bedrock, Google Vertex AI)

**Sources:** [option/requestoption.go:76-92](), [internal/requestconfig/requestconfig.go:229-239]()

### Custom HTTP Clients

The SDK accepts custom HTTP clients via `option.WithHTTPClient()` ([option/requestoption.go:58-74]()):

```mermaid
graph TB
    CustomClient["Custom HTTP Client<br/>(implements HTTPClient interface)"]
    HTTPClientInterface["HTTPClient interface<br/>Do(*Request) (*Response, error)<br/>(requestoption.go:49-51)"]
    WithHTTPClient["option.WithHTTPClient(client)"]
    RequestConfig["RequestConfig.HTTPClient<br/>RequestConfig.CustomHTTPDoer"]
    
    CustomClient -.implements.-> HTTPClientInterface
    CustomClient --> WithHTTPClient
    WithHTTPClient --> RequestConfig
```

This enables:
- Custom connection pooling or TLS configuration via `http.Transport`
- Request/response logging through custom `http.RoundTripper`
- Circuit breaker patterns
- Custom authentication flows

**Sources:** [option/requestoption.go:44-74](), [internal/requestconfig/requestconfig.go:195-197,413-417]()

### Request-Level Configuration

All service methods accept variadic `option.RequestOption` parameters, enabling per-request customization:

| Option Function | Purpose | Source |
|-----------------|---------|--------|
| `WithHeader(key, value)` | Set request headers | [option/requestoption.go:111-116]() |
| `WithQuery(key, value)` | Add query parameters | [option/requestoption.go:137-144]() |
| `WithJSONSet(key, value)` | Modify request body JSON | [option/requestoption.go:171-193]() |
| `WithRequestTimeout(duration)` | Set per-request timeout | [option/requestoption.go:255-262]() |
| `WithMaxRetries(count)` | Override retry count | [option/requestoption.go:99-107]() |
| `WithBaseURL(url)` | Override base URL | [option/requestoption.go:28-42]() |

**Sources:** [option/requestoption.go:1-286]()

### Pagination Interface

The pagination system ([packages/pagination/pagination.go:1-351]()) is generic and extensible:

```mermaid
graph TB
    subgraph "Pagination Types"
        Page["Page[T]<br/>(cursor-based)"]
        TokenPage["TokenPage[T]<br/>(token-based)"]
        PageCursor["PageCursor[T]<br/>(page number)"]
    end
    
    subgraph "Pager Pattern"
        AutoPager["PageAutoPager[T]<br/>(pagination.go:95)"]
        Next["Next() bool<br/>(pagination.go:111)"]
        Current["Current() T<br/>(pagination.go:128)"]
        Err["Err() error<br/>(pagination.go:132)"]
    end
    
    subgraph "Usage"
        GetNextPage["page.GetNextPage()<br/>(manual pagination)"]
        AutoPagerLoop["for pager.Next()<br/>  item := pager.Current()"]
    end
    
    Page --> AutoPager
    TokenPage --> AutoPager
    PageCursor --> AutoPager
    
    AutoPager --> Next
    AutoPager --> Current
    AutoPager --> Err
    
    Page --> GetNextPage
    AutoPager --> AutoPagerLoop
```

Each page type implements `GetNextPage()` to fetch the next page, and the auto-pager wraps this for iterator-style access. New pagination styles can be added by implementing the same interface pattern.

**Sources:** [packages/pagination/pagination.go:1-351]()

---

This architecture enables the SDK to be both simple for common use cases (through high-level service methods) and flexible for advanced scenarios (through middleware, custom clients, and per-request options). The strict separation between response and request types, combined with the discriminated union pattern, provides type safety while maintaining compatibility with the Anthropic API's polymorphic response structures.

---

