<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/text-embeddings-inference · page 3 Router Component · fetched 2026-10-26 -->

# Router Component

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [core/src/infer.rs](core/src/infer.rs)
- [core/src/queue.rs](core/src/queue.rs)
- [core/src/tokenization.rs](core/src/tokenization.rs)
- [docs/source/en/cli_arguments.md](docs/source/en/cli_arguments.md)
- [proto/tei.proto](proto/tei.proto)
- [router/src/grpc/server.rs](router/src/grpc/server.rs)
- [router/src/http/server.rs](router/src/http/server.rs)
- [router/src/http/types.rs](router/src/http/types.rs)
- [router/src/lib.rs](router/src/lib.rs)
- [router/src/main.rs](router/src/main.rs)
- [router/tests/test_http_embed.rs](router/tests/test_http_embed.rs)

</details>



## Purpose and Scope

The Router Component is the entry point and orchestration layer for Text Embeddings Inference (TEI). It handles incoming HTTP and gRPC requests, coordinates tokenization, manages dynamic batching, and dispatches work to backend model implementations. The router is responsible for concurrency control, request validation, observability instrumentation, and response assembly.

This page covers the router's architecture, initialization, and orchestration responsibilities. For detailed information about specific subsystems, see:
- API endpoint specifications: [HTTP and gRPC Endpoints](#3.1)
- Request processing details: [Request Processing Pipeline](#3.2)
- Tokenization implementation: [Tokenization System](#3.3)
- Batching logic: [Dynamic Batching Queue](#3.4)
- Metrics and tracing: [Observability and Monitoring](#3.5)

For backend model inference, see [Backend System](#4).

## Architecture Overview

The router component sits between external clients and the backend inference system. It is implemented primarily in Rust and consists of two main server implementations (HTTP and gRPC), an orchestration layer (`Infer`), and supporting systems for tokenization and batching.

```mermaid
graph TB
    subgraph "External Layer"
        HTTPClients["HTTP Clients<br/>(REST, OpenAI SDK)"]
        GRPCClients["gRPC Clients"]
    end
    
    subgraph "Router Layer - router/src/"
        subgraph "Server Implementations"
            HTTPServer["HTTP Server<br/>http/server.rs<br/>axum framework"]
            GRPCServer["gRPC Server<br/>grpc/server.rs<br/>tonic framework"]
        end
        
        subgraph "Orchestration - core/src/infer.rs"
            InferStruct["Infer struct<br/>Coordinates all operations"]
            Semaphore["Request Semaphore<br/>limit_concurrent_requests<br/>Arc&lt;Semaphore&gt;"]
        end
        
        subgraph "Processing Subsystems"
            TokenizationWorkers["Tokenization Workers<br/>core/src/tokenization.rs<br/>OS thread pool"]
            BatchingQueue["Dynamic Batching Queue<br/>core/src/queue.rs<br/>Token budget tracking"]
        end
        
        Init["Initialization Entry Point<br/>router/src/lib.rs::run()"]
    end
    
    subgraph "Backend Layer"
        BackendTrait["Backend Trait<br/>text_embeddings_backend"]
    end
    
    HTTPClients --> HTTPServer
    GRPCClients --> GRPCServer
    
    HTTPServer --> InferStruct
    GRPCServer --> InferStruct
    
    InferStruct --> Semaphore
    InferStruct --> TokenizationWorkers
    InferStruct --> BatchingQueue
    
    BatchingQueue --> BackendTrait
    
    Init -.creates.-> HTTPServer
    Init -.creates.-> GRPCServer
    Init -.creates.-> InferStruct
```

**Sources**: [router/src/lib.rs:1-412](), [router/src/http/server.rs:1-100](), [router/src/grpc/server.rs:1-50](), [core/src/infer.rs:1-100]()

## Core Components

### Entry Point and Initialization

The router's entry point is the `run` function in [router/src/lib.rs:44-412](). This function handles:

1. **Model discovery and download** - resolves model path (local or Hub), downloads artifacts if needed via `download_artifacts` [router/src/lib.rs:101-101]().
2. **Configuration parsing** - loads `config.json`, determines model type (embedding/classifier/reranker) [router/src/lib.rs:109-141]().
3. **Tokenizer initialization** - loads `tokenizer.json`, applies model-specific post-processing for architectures like Qwen2 [router/src/lib.rs:144-177]().
4. **Backend creation** - initializes the appropriate backend (Candle/ORT/Python) [router/src/lib.rs:260-264]().
5. **Subsystem setup** - creates `Tokenization` workers [router/src/lib.rs:271-278](), the `Queue` [router/src/lib.rs:280-285](), and the `Infer` orchestrator [router/src/lib.rs:292-297]().
6. **Server launch** - starts HTTP or gRPC server based on feature flags [router/src/lib.rs:348-412]().

```mermaid
graph TB
    MainArgs["main.rs<br/>Args::parse()"]
    
    RunFunc["lib.rs::run()"]
    
    subgraph "Initialization Steps"
        Step1["Download Model<br/>download_artifacts()"]
        Step2["Parse config.json<br/>ModelConfig"]
        Step3["Determine Model Type<br/>get_backend_model_type()"]
        Step4["Load Tokenizer<br/>Tokenizer::from_file()"]
        Step5["Create Backend<br/>Backend::new()"]
        Step6["Setup Tokenization<br/>Tokenization::new()"]
        Step7["Create Queue<br/>Queue::new()"]
        Step8["Create Infer<br/>Infer::new()"]
        Step9["Start Server<br/>http::server::run()<br/>or grpc::server::run()"]
    end
    
    MainArgs --> RunFunc
    RunFunc --> Step1
    Step1 --> Step2
    Step2 --> Step3
    Step3 --> Step4
    Step4 --> Step5
    Step5 --> Step6
    Step6 --> Step7
    Step7 --> Step8
    Step8 --> Step9
```

**Key Configuration Parameters** (from [router/src/main.rs:15-188]()):

| Parameter | Environment Variable | Default | Description |
|-----------|---------------------|---------|-------------|
| `model_id` | `MODEL_ID` | N/A | Model identifier or local path |
| `max_concurrent_requests` | `MAX_CONCURRENT_REQUESTS` | `512` | Semaphore limit for request admission |
| `max_batch_tokens` | `MAX_BATCH_TOKENS` | `16384` | Token budget for dynamic batching |
| `max_batch_requests` | `MAX_BATCH_REQUESTS` | None | Optional limit on requests per batch |
| `tokenization_workers` | `TOKENIZATION_WORKERS` | CPU count | Number of OS threads for tokenization |
| `auto_truncate` | `AUTO_TRUNCATE` | `true` | Automatically truncate oversized inputs |
| `port` | `PORT` | `3000` | Server listening port |

**Sources**: [router/src/lib.rs:44-412](), [router/src/main.rs:15-188]()

### Infer Orchestrator

The `Infer` struct in [core/src/infer.rs:13-56]() is the central orchestration component. It coordinates tokenization, batching, and backend inference while managing concurrency.

```mermaid
graph TB
    InferStruct["Infer Struct"]
    
    subgraph "Fields in Infer"
        Tokenization["tokenization: Tokenization<br/>Multi-threaded tokenizer pool"]
        Queue["queue: Queue<br/>Dynamic batching queue"]
        NotifyBatching["notify_batching_task<br/>Arc&lt;Notify&gt;<br/>Wake batching task"]
        Semaphore["limit_concurrent_requests<br/>Arc&lt;Semaphore&gt;<br/>Request admission control"]
        Backend["backend: Backend<br/>Model inference backend"]
    end
    
    InferStruct --> Tokenization
    InferStruct --> Queue
    InferStruct --> NotifyBatching
    InferStruct --> Semaphore
    InferStruct --> Backend
    
    subgraph "Background Tasks"
        BatchingTask["batching_task()<br/>Polls queue, sends batches"]
        BackendTask["backend_task()<br/>Receives batches, calls backend"]
    end
    
    InferStruct -.spawns.-> BatchingTask
    InferStruct -.spawns.-> BackendTask
    
    Queue --> BatchingTask
    BatchingTask --> BackendTask
    BackendTask --> Backend
```

**Core Methods** in `Infer`:

| Method | Purpose | Key Code Location |
|--------|---------|-------------------|
| `try_acquire_permit()` | Attempt to get request semaphore permit (non-blocking) | [core/src/infer.rs:94-105]() |
| `acquire_permit()` | Get request semaphore permit (blocking) | [core/src/infer.rs:107-115]() |
| `tokenize()` | Tokenize input without inference | [core/src/infer.rs:59-74]() |
| `decode()` | Decode token IDs to text | [core/src/infer.rs:76-91]() |
| `embed_pooled()` | Get pooled embeddings | [core/src/infer.rs:224-321]() |
| `embed_all()` | Get all token embeddings | [core/src/infer.rs:118-166]() |
| `embed_sparse()` | Get sparse embeddings (SPLADE) | [core/src/infer.rs:169-221]() |
| `predict()` | Classification/scoring | [core/src/infer.rs:391-498]() |

**Sources**: [core/src/infer.rs:11-523]()

### HTTP Server

The HTTP server is implemented using the `axum` framework in [router/src/http/server.rs](). It provides REST endpoints with JSON request/response formats and OpenAPI documentation.

**Endpoint Groups**:

| Endpoint Pattern | Handler Function | Model Type Support |
|------------------|------------------|-------------------|
| `POST /embed` | `embed()` | Embedding models only |
| `POST /embed_sparse` | `embed_sparse()` | SPLADE pooling only |
| `POST /embed_all` | `embed_all()` | Embedding models only |
| `POST /predict` | `predict()` | Classifier/Reranker |
| `POST /rerank` | `rerank()` | Reranker only |
| `POST /v1/embeddings` | `openai_embed()` | Embedding models (OpenAI compat) |
| `POST /tokenize` | `tokenize()` | All model types |
| `POST /decode` | `decode()` | All model types |
| `GET /health` | `health()` | All model types |
| `GET /info` | `get_model_info()` | All model types |

**Sources**: [router/src/http/server.rs:46-109]()

### gRPC Server

The gRPC server uses the `tonic` framework and is defined in [router/src/grpc/server.rs](). It offers the same functionality as HTTP with protobuf messages and streaming support.

**Service Structure** (from [proto/tei.proto:1-37]()):

```mermaid
graph TB
    subgraph "gRPC Services - proto/tei.proto"
        InfoService["Info Service<br/>Info()"]
        EmbedService["Embed Service<br/>Embed(), EmbedStream()<br/>EmbedSparse(), EmbedAll()"]
        PredictService["Predict Service<br/>Predict(), PredictPair()<br/>PredictStream()"]
        RerankService["Rerank Service<br/>Rerank(), RerankStream()"]
        TokenizeService["Tokenize Service<br/>Tokenize(), Decode()"]
    end
    
    subgraph "Implementation - grpc/server.rs"
        TextEmbeddingsService["TextEmbeddingsService<br/>implements all traits"]
    end
    
    InfoService -.implemented by.-> TextEmbeddingsService
    EmbedService -.implemented by.-> TextEmbeddingsService
    PredictService -.implemented by.-> TextEmbeddingsService
    RerankService -.implemented by.-> TextEmbeddingsService
    TokenizeService -.implemented by.-> TextEmbeddingsService
```

**Streaming Support**:

The gRPC server provides optimized streaming endpoints that process multiple requests concurrently while maintaining response ordering. The `TextEmbeddingsService` ([router/src/grpc/server.rs:46-50]()) manages these requests, using a configurable `max_parallel_stream_requests` limit [router/src/grpc/server.rs:54-57]().

**Sources**: [proto/tei.proto:1-37](), [router/src/grpc/server.rs:45-63]()

## Request Flow Through Router

The following diagram shows how a request flows through the router components from initial receipt to final response:

```mermaid
graph TB
    Request["Incoming Request<br/>HTTP or gRPC"]
    
    subgraph "Admission Control"
        TryAcquire["Infer.try_acquire_permit()<br/>or acquire_permit()"]
        SemaphoreCheck{{"Semaphore available?"}}
        Reject["Return 429 Overloaded"]
    end
    
    subgraph "Tokenization Phase"
        SendToTokenizer["tokenization.encode()"]
        TokenizerWorker["Tokenization Worker<br/>OS thread pool<br/>tokenizer_worker()"]
        PromptInjection["Apply prompt if configured"]
        Truncation["Truncate if enabled<br/>TruncationParams"]
    end
    
    subgraph "Queueing Phase"
        CreateEntry["Create Entry<br/>ValidEncoding + Metadata"]
        AppendQueue["queue.append(entry)"]
        NotifyBatching["notify_batching_task.notify_one()"]
        WaitResponse["Await on oneshot::Receiver"]
    end
    
    subgraph "Batching Task - batching_task()"
        AwaitNotify["Await notify"]
        NextBatch["queue.next_batch()"]
        SendToBackend["Send to embed_sender"]
    end
    
    subgraph "Backend Task - backend_task()"
        ReceiveBatch["Receive NextBatch"]
        BackendEmbed["backend.embed(batch)"]
        DistributeResults["Send results to<br/>response_tx channels"]
    end
    
    subgraph "Response Assembly"
        ReceiveResult["Receive from response_rx"]
        RecordMetadata["Record metrics & spans"]
        BuildResponse["Build HTTP/gRPC response"]
    end
    
    Request --> TryAcquire
    TryAcquire --> SemaphoreCheck
    SemaphoreCheck -->|No permit| Reject
    SemaphoreCheck -->|Got permit| SendToTokenizer
    
    SendToTokenizer --> TokenizerWorker
    TokenizerWorker --> PromptInjection
    PromptInjection --> Truncation
    
    Truncation --> CreateEntry
    CreateEntry --> AppendQueue
    AppendQueue --> NotifyBatching
    NotifyBatching --> WaitResponse
    
    NotifyBatching -.wakes.-> AwaitNotify
    AwaitNotify --> NextBatch
    NextBatch --> SendToBackend
    
    SendToBackend --> ReceiveBatch
    ReceiveBatch --> BackendEmbed
    BackendEmbed --> DistributeResults
    
    DistributeResults -.sends.-> WaitResponse
    WaitResponse --> ReceiveResult
    ReceiveResult --> RecordMetadata
    RecordMetadata --> BuildResponse
```

**Timing Breakdown** in `ResponseMetadata`:

| Timing Field | Description | Recorded Where |
|--------------|-------------|----------------|
| `tokenization_time` | Duration in tokenization workers | [core/src/tokenization.rs:68-101]() |
| `queue_time` | Time waiting in queue + batching | [core/src/queue.rs:27](), [core/src/infer.rs:207-210]() |
| `inference_time` | Actual backend inference duration | Returned by backend |

**Sources**: [core/src/infer.rs:125-166](), [core/src/queue.rs:69-95](), [core/src/tokenization.rs:171-200]()

## Code Entity Mapping

### Key Structs and Their Roles

| Concept | Code Entity | Location | Primary Responsibility |
|---------|-------------|----------|----------------------|
| Router entry point | `run()` function | [router/src/lib.rs:44]() | Initialize all components and start server |
| Request orchestration | `Infer` struct | [core/src/infer.rs:13]() | Coordinates tokenization → batching → backend |
| Tokenization system | `Tokenization` struct | [core/src/tokenization.rs:14]() | Manages OS thread pool of tokenizers |
| Dynamic batching | `Queue` struct | [core/src/queue.rs:36]() | Token-budget-aware batch assembly |
| Concurrency control | `limit_concurrent_requests` | [core/src/infer.rs:19]() | `Arc<Semaphore>` for request admission |

### Configuration Flow

```mermaid
graph LR
    subgraph "CLI Arguments"
        ArgsStruct["Args struct<br/>main.rs:15-188"]
    end
    
    subgraph "Runtime Config"
        ModelConfig["ModelConfig<br/>lib.rs:111"]
    end
    
    subgraph "Component Config"
        TokenizationConfig["Tokenization::new()<br/>workers, max_input_length"]
        QueueConfig["Queue::new()<br/>max_batch_tokens, max_batch_requests"]
        InferConfig["Infer::new()<br/>max_concurrent_requests"]
    end
    
    ArgsStruct --> TokenizationConfig
    ArgsStruct --> QueueConfig
    ArgsStruct --> InferConfig
    
    ModelConfig -.parsed from config.json.-> ArgsStruct
```

**Sources**: [router/src/main.rs:15-188](), [router/src/lib.rs:109-113](), [core/src/tokenization.rs:30-65]()

### Feature Flags and Server Selection

The router is compiled with exactly one of two mutually exclusive feature flags:

```mermaid
graph TB
    CargoFeatures["Cargo Feature Flags"]
    
    HTTPFeature["--features http"]
    GRPCFeature["--features grpc"]
    
    CompileCheck["Compile-time check<br/>lib.rs:348-356"]
    
    HTTPImpl["HTTP Server<br/>http::server::run()"]
    GRPCImpl["gRPC Server<br/>grpc::server::run()"]
    
    CargoFeatures --> HTTPFeature
    CargoFeatures --> GRPCFeature
    
    HTTPFeature --> CompileCheck
    GRPCFeature --> CompileCheck
    
    CompileCheck -->|"#[cfg(feature = 'http')]"| HTTPImpl
    CompileCheck -->|"#[cfg(feature = 'grpc')]"| GRPCImpl
```

The compile-time enforcement is at [router/src/lib.rs:348-356]().

**Sources**: [router/src/lib.rs:348-356]()

## Observability Integration

### Metrics (Prometheus)

Metrics are collected via the `metrics` crate:

| Metric Name | Type | Labels | Location |
|-------------|------|--------|----------|
| `te_request_count` | Counter | `method` | [router/src/http/server.rs:177]() |
| `te_request_failure` | Counter | `err` | [core/src/infer.rs:69, 100, 129]() |
| `te_queue_size` | Gauge | - | [core/src/queue.rs:115]() |
| `te_embed_duration` | Histogram | - | [core/src/infer.rs:157]() |

**Sources**: [core/src/infer.rs:156-163](), [core/src/queue.rs:115-116]()

---

