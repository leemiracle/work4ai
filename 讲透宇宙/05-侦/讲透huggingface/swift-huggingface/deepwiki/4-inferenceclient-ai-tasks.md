<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/swift-huggingface · page 4 InferenceClient - AI Tasks · fetched 2026-10-26 -->

# InferenceClient - AI Tasks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [Sources/HuggingFace/InferenceProviders/InferenceClient.swift](Sources/HuggingFace/InferenceProviders/InferenceClient.swift)

</details>



## Purpose and Scope

This page provides an overview of the `InferenceClient` component and its role in executing AI inference tasks. The `InferenceClient` provides a unified Swift interface for running various AI operations including chat completion, embeddings generation, image/video synthesis, and speech transcription across multiple inference providers.

For detailed information about specific capabilities:
- Chat completion and streaming: see [Chat Completion](#4.1)
- Text embeddings: see [Feature Extraction (Embeddings)](#4.2)
- Image and video synthesis: see [Image and Video Generation](#4.3)
- Audio transcription: see [Speech-to-Text](#4.4)
- Provider configuration: see [Inference Providers](#4.5)

For repository management and file operations, see [HubClient - Repository Management](#3).
For authentication setup, see [Authentication System](#5).

## InferenceClient Architecture

The `InferenceClient` is one of two primary client interfaces in the swift-huggingface SDK, specializing in AI task execution. It orchestrates communication with various inference provider APIs while handling authentication, request serialization, and response parsing.

Title: InferenceClient Architecture
```mermaid
graph TB
    App["Application Code"]
    
    IC["InferenceClient"]
    
    subgraph "Task Methods"
        ChatMethod["chatCompletion()"]
        ChatStreamMethod["chatCompletionStream()"]
        EmbedMethod["featureExtraction()"]
        T2IMethod["textToImage()"]
        T2VMethod["textToVideo()"]
        S2TMethod["speechToText()"]
    end
    
    subgraph "Infrastructure"
        HTTPClient["HTTPClient"]
        TokenProvider["TokenProvider"]
    end
    
    subgraph "Provider Routing"
        HFInf["HF Inference API"]
        Groq["Groq API"]
        Hyperbolic["Hyperbolic API"]
        Replicate["Replicate API"]
    end
    
    App --> IC
    
    IC --> ChatMethod
    IC --> ChatStreamMethod
    IC --> EmbedMethod
    IC --> T2IMethod
    IC --> T2VMethod
    IC --> S2TMethod
    
    ChatMethod --> HTTPClient
    ChatStreamMethod --> HTTPClient
    EmbedMethod --> HTTPClient
    T2IMethod --> HTTPClient
    T2VMethod --> HTTPClient
    S2TMethod --> HTTPClient
    
    HTTPClient --> TokenProvider
    
    HTTPClient --> HFInf
    HTTPClient --> Groq
    HTTPClient --> Hyperbolic
    HTTPClient --> Replicate
```

**InferenceClient Architecture**: The client provides task-specific methods that route through `HTTPClient` for network communication and `TokenProvider` for authentication.

Sources: [Sources/HuggingFace/InferenceProviders/InferenceClient.swift:7-24](), [Sources/HuggingFace/InferenceProviders/InferenceClient.swift:114-120]()

## Creating an InferenceClient

### Default Client

The simplest way to create an `InferenceClient` is using the `default` static property, which automatically detects authentication credentials from environment variables or token files and uses the default router host [Sources/HuggingFace/InferenceProviders/InferenceClient.swift:25-33]().

```swift
let client = InferenceClient.default
```

The default client looks for credentials in standard locations such as `HF_TOKEN` or `~/.cache/huggingface/token` [Sources/HuggingFace/InferenceProviders/InferenceClient.swift:13-19]().

### Custom Configuration

For advanced scenarios requiring custom session configuration, base URLs, or authentication strategies:

```swift
// Custom session configuration
let configuration = URLSessionConfiguration.default
configuration.timeoutIntervalForRequest = 30
let session = URLSession(configuration: configuration)

let client = InferenceClient(
    session: session,
    host: URL(string: "https://router.huggingface.co")!,
    userAgent: "MyApp/1.0"
)
```

Sources: [Sources/HuggingFace/InferenceProviders/InferenceClient.swift:80-99]()

### Authentication Strategies

The `InferenceClient` supports multiple authentication approaches through the `TokenProvider` abstraction [Sources/HuggingFace/InferenceProviders/InferenceClient.swift:108-112]():

| Strategy | Usage | Typical Scenario |
|----------|-------|------------------|
| `.environment` | Auto-detected from env vars/files | Development, CI/CD |
| `.fixed(token:)` | Static token string | Server applications |
| `.oauth(manager:)` | Dynamic OAuth tokens | User-facing apps |
| `.none` | No authentication | Public models/endpoints |

```swift
// Fixed token
let client = InferenceClient(host: myHost, bearerToken: "hf_...")

// OAuth-based
let authManager = try HuggingFaceAuthenticationManager(...)
let client = InferenceClient(host: myHost, tokenProvider: .oauth(manager: authManager))
```

Sources: [Sources/HuggingFace/InferenceProviders/InferenceClient.swift:87-112](), [README.md:81-94]()

## Task Type Taxonomy

The `InferenceClient` organizes AI capabilities into distinct task categories, each with dedicated methods and data structures:

Title: Task Method Mapping
```mermaid
graph TB
    IC["InferenceClient"]
    
    subgraph "Language Tasks"
        Chat["Chat Completion<br/>chatCompletion()<br/>chatCompletionStream()"]
        Embed["Feature Extraction<br/>featureExtraction()"]
    end
    
    subgraph "Generation Tasks"
        T2I["Text-to-Image<br/>textToImage()"]
        T2V["Text-to-Video<br/>textToVideo()"]
    end
    
    subgraph "Audio Tasks"
        S2T["Speech-to-Text<br/>speechToText()"]
    end
    
    subgraph "Request Types"
        ChatReq["ChatCompletion.Message[]"]
        EmbedReq["String[]"]
        ImageReq["prompt: String"]
        VideoReq["prompt: String"]
        AudioReq["audio: String (base64)"]
    end
    
    subgraph "Response Types"
        ChatResp["ChatCompletion.Response"]
        EmbedResp["FeatureExtraction.Response"]
        ImageResp["TextToImage.Response"]
        VideoResp["TextToVideo.Response"]
        AudioResp["SpeechToText.Response"]
    end
    
    IC --> Chat
    IC --> Embed
    IC --> T2I
    IC --> T2V
    IC --> S2T
    
    Chat --> ChatReq
    Embed --> EmbedReq
    T2I --> ImageReq
    T2V --> VideoReq
    S2T --> AudioReq
    
    Chat --> ChatResp
    Embed --> EmbedResp
    T2I --> ImageResp
    T2V --> VideoResp
    S2T --> AudioResp
```

### Language Tasks

**Chat Completion** provides conversational AI capabilities with support for multi-turn dialogues, system prompts, tool calling, and vision-language models. For details, see [Chat Completion](#4.1).

**Feature Extraction** generates text embeddings (vector representations) for semantic search and similarity comparison. For details, see [Feature Extraction (Embeddings)](#4.2).

### Generation Tasks

**Text-to-Image** synthesizes images from text prompts with control over dimensions and guidance. For details, see [Image and Video Generation](#4.3).

**Text-to-Video** generates video sequences from textual descriptions. For details, see [Image and Video Generation](#4.3).

### Audio Tasks

**Speech-to-Text** transcribes audio files to text with optional language specification. For details, see [Speech-to-Text](#4.4).

## Provider Selection Architecture

The `InferenceClient` uses dynamic provider routing, allowing the same task to execute on different inference backends.

Title: Provider Routing Flow
```mermaid
graph LR
    subgraph "Application Layer"
        ChatCall["client.chatCompletion()"]
    end
    
    subgraph "Provider Parameter"
        ProviderEnum["InferenceProvider enum"]
        HFOption[".hfInference"]
        GroqOption[".groq"]
        HyperbolicOption[".hyperbolic"]
        ReplicateOption[".replicate"]
    end
    
    subgraph "Routing Logic"
        URLBuilder["URL Construction"]
        HeaderBuilder["Header Construction"]
    end
    
    subgraph "Provider Endpoints"
        HFURL["api-inference.huggingface.co"]
        GroqURL["api.groq.com"]
        HyperbolicURL["api.hyperbolic.xyz"]
        ReplicateURL["api.replicate.com"]
    end
    
    ChatCall --> ProviderEnum
    ProviderEnum --> HFOption
    ProviderEnum --> GroqOption
    ProviderEnum --> HyperbolicOption
    ProviderEnum --> ReplicateOption
    
    HFOption --> URLBuilder
    GroqOption --> URLBuilder
    HyperbolicOption --> URLBuilder
    ReplicateOption --> URLBuilder
    
    URLBuilder --> HeaderBuilder
    
    HeaderBuilder --> HFURL
    HeaderBuilder --> GroqURL
    HeaderBuilder --> HyperbolicURL
    HeaderBuilder --> ReplicateURL
```

### Provider Compatibility

Different tasks support different provider combinations. For a detailed compatibility matrix and configuration guide, see [Inference Providers](#4.5).

## Request/Response Flow

The typical lifecycle of an inference request follows this sequence:

Title: Standard Request Flow
```mermaid
sequenceDiagram
    participant App as "Application"
    participant IC as "InferenceClient"
    participant HTTP as "HTTPClient"
    participant TP as "TokenProvider"
    participant API as "Provider API"
    
    App->>IC: chatCompletion(model, messages, provider)
    IC->>IC: Build request URL for provider
    
    IC->>HTTP: fetch(url, method, body, headers)
    HTTP->>TP: getToken()
    TP-->>HTTP: "hf_..."
    HTTP->>HTTP: Add Authorization header
    
    HTTP->>API: POST /v1/chat/completions
    API-->>HTTP: HTTP 200 + JSON response
    
    HTTP->>HTTP: Decode JSON to Response Type
    HTTP-->>IC: Response object
    IC-->>App: Response
```

Sources: [Sources/HuggingFace/InferenceProviders/InferenceClient.swift:114-120]()

## Next Steps

- **[Chat Completion](#4.1)**: Multi-turn conversations, streaming, vision models, tool calling.
- **[Feature Extraction (Embeddings)](#4.2)**: Text embeddings for semantic search.
- **[Image and Video Generation](#4.3)**: Text-to-image/video synthesis parameters.
- **[Speech-to-Text](#4.4)**: Audio transcription and translation.
- **[Inference Providers](#4.5)**: Provider selection, configuration, and compatibility.

---

