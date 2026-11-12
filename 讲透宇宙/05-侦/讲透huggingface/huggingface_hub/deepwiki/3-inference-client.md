<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/huggingface_hub · page 3 Inference Client · fetched 2026-10-26 -->

# Inference Client

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/en/guides/inference.md](docs/source/en/guides/inference.md)
- [docs/source/en/package_reference/inference_client.md](docs/source/en/package_reference/inference_client.md)
- [src/huggingface_hub/inference/_client.py](src/huggingface_hub/inference/_client.py)
- [src/huggingface_hub/inference/_common.py](src/huggingface_hub/inference/_common.py)
- [src/huggingface_hub/inference/_generated/_async_client.py](src/huggingface_hub/inference/_generated/_async_client.py)
- [src/huggingface_hub/inference/_providers/__init__.py](src/huggingface_hub/inference/_providers/__init__.py)
- [src/huggingface_hub/inference/_providers/_common.py](src/huggingface_hub/inference/_providers/_common.py)
- [src/huggingface_hub/inference/_providers/fal_ai.py](src/huggingface_hub/inference/_providers/fal_ai.py)
- [src/huggingface_hub/inference/_providers/hf_inference.py](src/huggingface_hub/inference/_providers/hf_inference.py)
- [src/huggingface_hub/inference/_providers/replicate.py](src/huggingface_hub/inference/_providers/replicate.py)
- [src/huggingface_hub/inference/_providers/sambanova.py](src/huggingface_hub/inference/_providers/sambanova.py)
- [src/huggingface_hub/inference/_providers/together.py](src/huggingface_hub/inference/_providers/together.py)
- [src/huggingface_hub/inference/_providers/zai_org.py](src/huggingface_hub/inference/_providers/zai_org.py)
- [tests/test_inference_async_client.py](tests/test_inference_async_client.py)
- [tests/test_inference_client.py](tests/test_inference_client.py)
- [tests/test_inference_providers.py](tests/test_inference_providers.py)
- [utils/generate_async_inference_client.py](utils/generate_async_inference_client.py)

</details>



The Inference Client provides a unified interface for running machine learning inference across multiple providers and deployment types. It supports the Hugging Face Inference API, third-party providers (OpenAI, Together, Replicate, etc.), Inference Endpoints, and local servers with a consistent API design.

For information about managing inference endpoints, see [Inference Endpoints](#3.3). For details about the underlying provider routing system, see [Inference Providers](#3.1).

## Architecture Overview

The Inference Client system is built around a provider-agnostic design that routes requests to different inference services while maintaining a consistent interface.

```mermaid
graph TB
    subgraph "Client Layer"
        IC["InferenceClient"]
        AIC["AsyncInferenceClient"]
        Proxy["OpenAI Compatibility Layer"]
    end
    
    subgraph "Provider System"
        PH["get_provider_helper()"]
        TPH["TaskProviderHelper"]
        subgraph "Provider Implementations"
            HFI["HFInferenceTask"]
            OpenAI["OpenAIConversationalTask"]
            Together["TogetherTextToImageTask"]
            Other["Other Provider Tasks..."]
        end
    end
    
    subgraph "Request Processing"
        RP["RequestParameters"]
        Common["_common utilities"]
        Streaming["Streaming utilities"]
    end
    
    subgraph "External Services"
        HFHub["Hugging Face Hub"]
        ThirdParty["Third-party APIs"]
        Endpoints["Inference Endpoints"]
        Local["Local Servers"]
    end
    
    IC --> PH
    AIC --> PH
    Proxy --> IC
    
    PH --> TPH
    TPH --> HFI
    TPH --> OpenAI
    TPH --> Together
    TPH --> Other
    
    HFI --> RP
    OpenAI --> RP
    RP --> Common
    RP --> Streaming
    
    HFI --> HFHub
    OpenAI --> ThirdParty
    Together --> ThirdParty
    HFI --> Endpoints
    HFI --> Local
```

Sources: [src/huggingface_hub/inference/_client.py:120](), [src/huggingface_hub/inference/_generated/_async_client.py:108](), [src/huggingface_hub/inference/_providers/__init__.py:163](), [src/huggingface_hub/inference/_providers/_common.py:66]()

## Core Client Classes

### InferenceClient

The `InferenceClient` class is the primary synchronous interface for inference operations.

```mermaid
graph LR
    subgraph "InferenceClient Methods"
        Init["__init__()"]
        Post["_inner_post()"]
        TaskMethods["Task Methods<br/>chat_completion()<br/>text_generation()<br/>text_to_image()<br/>etc."]
    end
    
    subgraph "Configuration"
        Model["model: Optional[str]"]
        Provider["provider: PROVIDER_OR_POLICY_T"]
        Token["token: Optional[str]"]
        Headers["headers: Dict"]
        Timeout["timeout: Optional[float]"]
    end
    
    subgraph "Internal Components"
        ProviderHelper["get_provider_helper()"]
        RequestParams["RequestParameters"]
        HTTPCall["HTTP Request via requests"]
    end
    
    Init --> Model
    Init --> Provider
    Init --> Token
    
    TaskMethods --> ProviderHelper
    ProviderHelper --> RequestParams
    Post --> HTTPCall
    RequestParams --> Post
```

The client supports both model-specific initialization and per-call model specification:

```python
# Model-specific client
client = InferenceClient(model="meta-llama/Llama-3.1-8B", provider="together")

# Generic client with per-call model
client = InferenceClient(provider="together") 
response = client.chat_completion(messages, model="meta-llama/Llama-3.1-8B")
```

Sources: [src/huggingface_hub/inference/_client.py:120-236](), [src/huggingface_hub/inference/_client.py:162-234]()

### AsyncInferenceClient

The `AsyncInferenceClient` provides asynchronous inference capabilities with the same interface as the synchronous client.

```mermaid
graph LR
    subgraph "AsyncInferenceClient Specifics"
        AsyncPost["_inner_post() async"]
        AsyncMethods["All task methods are async"]
        SessionMgmt["_sessions: Dict[ClientSession, Set[ClientResponse]]"]
        ContextMgr["__aenter__ / __aexit__"]
        Close["close() method"]
    end
    
    subgraph "Async HTTP Handling"
        AioHttp["aiohttp.ClientSession"]
        AsyncStream["_async_yield_from()"]
        AsyncTimeout["asyncio.TimeoutError handling"]
    end
    
    AsyncPost --> AioHttp
    AsyncMethods --> AsyncPost
    SessionMgmt --> AioHttp
    ContextMgr --> Close
    AsyncStream --> SessionMgmt
```

The async client automatically generates from the sync client via [utils/generate_async_inference_client.py]().

Sources: [src/huggingface_hub/inference/_generated/_async_client.py:108-317](), [utils/generate_async_inference_client.py:31-76]()

## Provider System

The provider system abstracts different inference services behind a common interface.

### Provider Registry

```mermaid
graph TB
    subgraph "Provider Types"
        HF["hf-inference"]
        OpenAI["openai"]
        Together["together"]
        Replicate["replicate"]
        Others["cerebras, cohere, fal-ai, etc."]
    end
    
    subgraph "Task Support Matrix"
        Conv["conversational"]
        TextGen["text-generation"]
        TextToImg["text-to-image"]
        Audio["audio tasks"]
        Vision["vision tasks"]
    end
    
    subgraph "Provider Resolution"
        GetHelper["get_provider_helper()"]
        AutoSelect["provider='auto'"]
        Mapping["_fetch_inference_provider_mapping()"]
    end
    
    HF --> Conv
    HF --> TextToImg
    HF --> Audio
    HF --> Vision
    
    OpenAI --> Conv
    Together --> Conv
    Together --> TextGen
    Together --> TextToImg
    
    GetHelper --> AutoSelect
    AutoSelect --> Mapping
    Mapping --> HF
```

Provider selection follows this priority:
1. Explicit provider parameter
2. Auto-selection based on model and user preferences
3. Fallback to `hf-inference` for URLs or when no model specified

Sources: [src/huggingface_hub/inference/_providers/__init__.py:67-160](), [src/huggingface_hub/inference/_providers/__init__.py:163-208]()

### TaskProviderHelper Base Class

All provider implementations inherit from `TaskProviderHelper`:

```mermaid
graph TB
    subgraph "TaskProviderHelper Lifecycle"
        PrepareRequest["prepare_request()"]
        PrepareAPIKey["_prepare_api_key()"]
        PrepareMapping["_prepare_mapping_info()"]
        PrepareHeaders["_prepare_headers()"]
        PrepareURL["_prepare_url()"]
        PreparePayload["_prepare_payload_as_dict()"]
        GetResponse["get_response()"]
    end
    
    PrepareRequest --> PrepareAPIKey
    PrepareRequest --> PrepareMapping
    PrepareRequest --> PrepareHeaders
    PrepareRequest --> PrepareURL
    PrepareRequest --> PreparePayload
    PrepareRequest --> GetResponse
    
    subgraph "Request Building"
        APIKey["API Key Resolution"]
        ModelMapping["Model ID Mapping"]
        URLRouting["URL Routing Logic"]
        PayloadFormat["Provider-specific Formatting"]
    end
    
    PrepareAPIKey --> APIKey
    PrepareMapping --> ModelMapping
    PrepareURL --> URLRouting
    PreparePayload --> PayloadFormat
```

Sources: [src/huggingface_hub/inference/_providers/_common.py:66-235](), [src/huggingface_hub/inference/_providers/_common.py:74-117]()

## Task Methods

The client provides task-specific methods that map to different ML capabilities.

### Chat Completion

The primary conversational interface supporting OpenAI-compatible parameters:

```mermaid
graph LR
    subgraph "chat_completion() Method"
        Messages["messages: List[ChatCompletionInputMessage]"]
        Parameters["max_tokens, temperature, stream, etc."]
        Overloads["@overload for stream=True/False"]
    end
    
    subgraph "Output Types"
        NonStream["ChatCompletionOutput"]
        Stream["Iterable[ChatCompletionStreamOutput]"]
        AsyncStream["AsyncIterable[ChatCompletionStreamOutput]"]
    end
    
    subgraph "Provider Routing"
        ConvTask["conversational task"]
        ProviderImpl["Provider-specific implementation"]
        OpenAICompat["OpenAI compatibility layer"]
    end
    
    Messages --> ConvTask
    Parameters --> ProviderImpl
    Overloads --> NonStream
    Overloads --> Stream
    ProviderImpl --> OpenAICompat
```

The method supports both streaming and non-streaming responses with proper type annotations.

Sources: [src/huggingface_hub/inference/_client.py:523-766](), [src/huggingface_hub/inference/_generated/_async_client.py:557-803]()

### Text Generation

Lower-level text completion interface:

```mermaid
graph LR
    subgraph "text_generation() Parameters"
        Prompt["prompt: str"]
        Details["details: bool"]
        Stream["stream: bool"]
        MaxTokens["max_new_tokens, temperature, etc."]
    end
    
    subgraph "Return Types"
        SimpleStr["str (details=False, stream=False)"]
        DetailedOutput["TextGenerationOutput (details=True)"]
        StreamStr["Iterable[str] (stream=True, details=False)"]
        StreamOutput["Iterable[TextGenerationStreamOutput]"]
    end
    
    subgraph "Error Handling"
        Validation["ValidationError for unsupported params"]
        Retry["Automatic retry for non-TGI servers"]
        ModelKwargs["MODEL_KWARGS_NOT_USED_REGEX"]
    end
    
    Details --> SimpleStr
    Details --> DetailedOutput
    Stream --> StreamStr
    Stream --> StreamOutput
    
    Retry --> ModelKwargs
    Validation --> Retry
```

Sources: [src/huggingface_hub/inference/_client.py:1068-1336]()

### Task Method Pattern

All task methods follow a consistent pattern:

```mermaid
graph TB
    subgraph "Task Method Implementation"
        InputValidation["Input validation"]
        ModelResolution["model = model or self.model"]
        ProviderHelper["get_provider_helper(provider, task, model)"]
        RequestPrep["provider_helper.prepare_request()"]
        HTTPCall["self._inner_post(request_parameters)"]
        ResponseParsing["OutputType.parse_obj_as_*()"]
    end
    
    InputValidation --> ModelResolution
    ModelResolution --> ProviderHelper
    ProviderHelper --> RequestPrep
    RequestPrep --> HTTPCall
    HTTPCall --> ResponseParsing
```

This pattern is implemented across all task methods like `text_to_image()`, `audio_classification()`, `image_segmentation()`, etc.

Sources: [src/huggingface_hub/inference/_client.py:288-343](), [src/huggingface_hub/inference/_client.py:1406-1449]()

## Authentication and Routing

### Authentication Modes

The client supports multiple authentication patterns:

```mermaid
graph LR
    subgraph "Authentication Types"
        HFToken["HF Token (hf_*)"]
        ProviderKey["Provider API Key"]
        NoAuth["No Authentication"]
    end
    
    subgraph "Request Routing"
        HFRouter["Hugging Face Router"]
        DirectAPI["Direct Provider API"]
        LocalServer["Local Server"]
    end
    
    subgraph "Billing"
        HFBilling["Billed to HF Account"]
        ProviderBilling["Billed to Provider Account"]
    end
    
    HFToken --> HFRouter
    HFToken --> HFBilling
    ProviderKey --> DirectAPI
    ProviderKey --> ProviderBilling
    NoAuth --> LocalServer
```

### API Key Resolution

API key resolution follows this hierarchy in `_prepare_api_key()`:

1. Explicit `api_key` parameter
2. Locally saved token via `get_token()`
3. Error if required but not found

Sources: [src/huggingface_hub/inference/_client.py:176-205](), [src/huggingface_hub/inference/_providers/_common.py:129-139]()

## Streaming Support

### Streaming Architecture

```mermaid
graph TB
    subgraph "Streaming Implementation"
        StreamParam["stream=True parameter"]
        InnerPost["_inner_post(stream=True)"]
        HTTPStream["HTTP streaming response"]
        Parsing["Server-Sent Events parsing"]
    end
    
    subgraph "Sync Streaming"
        RequestsIter["requests.Response.iter_lines()"]
        SyncGenerator["Generator[OutputType]"]
    end
    
    subgraph "Async Streaming"
        AioHttpStream["aiohttp streaming"]
        AsyncYield["_async_yield_from()"]
        AsyncGenerator["AsyncGenerator[OutputType]"]
    end
    
    StreamParam --> InnerPost
    InnerPost --> HTTPStream
    HTTPStream --> Parsing
    
    HTTPStream --> RequestsIter
    RequestsIter --> SyncGenerator
    
    HTTPStream --> AioHttpStream
    AioHttpStream --> AsyncYield
    AsyncYield --> AsyncGenerator
```

### Stream Response Parsing

Stream responses use Server-Sent Events format:

```
data: {"choices": [{"delta": {"content": "Hello"}}]}
data: {"choices": [{"delta": {"content": " world"}}]}
data: [DONE]
```

Parsing is handled by specialized functions like `_stream_chat_completion_response()` and `_format_text_generation_stream_output()`.

Sources: [src/huggingface_hub/inference/_common.py:330-391](), [src/huggingface_hub/inference/_common.py:393-448]()

## Error Handling

### Error Hierarchy

```mermaid
graph TB
    subgraph "Client-Level Errors"
        TimeoutError["InferenceTimeoutError"]
        HTTPError["HTTPError / ClientResponseError"]
        ValidationError["ValidationError"]
    end
    
    subgraph "Provider-Level Errors"
        AuthError["Authentication errors"]
        ModelError["Model not supported"]
        TaskError["Task not supported"]
    end
    
    subgraph "Generation-Specific Errors"
        GenerationError["GenerationError"]
        IncompleteError["IncompleteGenerationError"]
        OverloadedError["OverloadedError"]
    end
    
    subgraph "Error Handling Logic"
        RetryLogic["Automatic retry for unsupported params"]
        ErrorMapping["Provider-specific error mapping"]
        GracefulFallback["Graceful degradation"]
    end
    
    HTTPError --> ErrorMapping
    ValidationError --> RetryLogic
    RetryLogic --> GracefulFallback
```

Error handling includes automatic retry logic for text generation when unsupported parameters are detected via regex matching on error messages.

Sources: [src/huggingface_hub/inference/_client.py:274-286](), [src/huggingface_hub/inference/_common.py:44-51](), [src/huggingface_hub/inference/_client.py:1271-1295]()

## OpenAI Compatibility

### Compatible Interface

The client provides OpenAI-compatible access patterns:

```mermaid
graph LR
    subgraph "OpenAI Compatibility"
        BaseURL["base_url parameter"]
        APIKey["api_key parameter"] 
        ChatCompletions["client.chat.completions.create()"]
    end
    
    subgraph "Internal Mapping"
        ModelAlias["model <-> base_url alias"]
        TokenAlias["token <-> api_key alias"]
        ProxyClient["OpenAI-style proxy client"]
    end
    
    subgraph "Shared Implementation"
        ChatCompletion["chat_completion() method"]
        StreamSupport["Streaming support"]
        TypeAnnotations["OpenAI-compatible types"]
    end
    
    BaseURL --> ModelAlias
    APIKey --> TokenAlias
    ChatCompletions --> ProxyClient
    ProxyClient --> ChatCompletion
    ChatCompletion --> StreamSupport
```

This allows drop-in replacement of OpenAI client code with minimal changes.

Sources: [src/huggingface_hub/inference/_client.py:168-183](), [docs/source/en/guides/inference.md:247-276]()

---

