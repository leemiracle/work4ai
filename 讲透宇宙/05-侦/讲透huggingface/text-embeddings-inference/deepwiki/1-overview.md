<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/text-embeddings-inference · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Cargo.lock](Cargo.lock)
- [Cargo.toml](Cargo.toml)
- [README.md](README.md)
- [docs/openapi.json](docs/openapi.json)
- [docs/source/en/cli_arguments.md](docs/source/en/cli_arguments.md)
- [docs/source/en/custom_container.md](docs/source/en/custom_container.md)
- [docs/source/en/private_models.md](docs/source/en/private_models.md)
- [docs/source/en/quick_tour.md](docs/source/en/quick_tour.md)
- [docs/source/en/supported_models.md](docs/source/en/supported_models.md)
- [router/src/lib.rs](router/src/lib.rs)
- [router/src/main.rs](router/src/main.rs)

</details>



Text Embeddings Inference (TEI) is a Rust-based toolkit for deploying and serving open-source text embedding, sequence classification, and re-ranking models. TEI provides production-ready inference with optimizations for NVIDIA GPUs (via CUDA), Apple Silicon (via Metal), and CPUs (via Intel MKL or ONNX Runtime).

The system supports popular embedding models including FlagEmbedding, Ember, GTE, E5, Qwen3, Mistral, and ModernBERT architectures. TEI is designed for high throughput and low latency, featuring token-based dynamic batching, Flash Attention optimizations, and comprehensive observability.

**Key Capabilities:**
- Multiple API interfaces: HTTP REST (via `axum`), gRPC (via `tonic`), OpenAI-compatible endpoints. [router/src/lib.rs:5-15]()
- Three backend implementations: Candle (Rust ML), ORT (ONNX Runtime), Python (PyTorch via gRPC). [Cargo.toml:3-11]()
- Hardware-optimized builds for CUDA compute capabilities 75-120, Intel CPUs, and Apple Metal. [docs/source/en/supported_models.md:70-80]()
- Production features: Prometheus metrics, OpenTelemetry tracing, distributed deployment support. [README.md:51-62]()

For deployment instructions, see [Getting Started](#2). For detailed API documentation, see [API Reference](#6).

Sources: [README.md:1-61](), [router/src/lib.rs:1-40](), [Cargo.toml:1-28]()

## System Architecture

TEI is organized into four main layers: client interfaces, router layer, core processing, and backend implementations. The architecture is designed for high performance with async I/O, multi-threaded tokenization, and hardware-accelerated inference.

**Overall System Architecture**

```mermaid
graph TB
    subgraph "Client Layer"
        HTTPClient["HTTP/REST Clients<br/>curl, Python SDK, OpenAI SDK"]
        GRPCClient["gRPC Clients"]
        PrometheusClient["Prometheus Scraper"]
    end
    
    subgraph "Router Layer - router crate"
        HTTPServer["axum HTTP Server<br/>router/src/http/server.rs"]
        GRPCServer["tonic gRPC Server<br/>router/src/grpc/server.rs"]
        
        Endpoints["API Routes:<br/>/embed, /embed_all, /embed_sparse<br/>/predict, /rerank<br/>/tokenize, /decode<br/>/health, /info, /metrics<br/>/v1/embeddings"]
    end
    
    subgraph "Core Processing - core crate"
        Infer["Infer orchestrator<br/>core/src/infer.rs"]
        Tokenization["Tokenization workers<br/>core/src/tokenization.rs"]
        Queue["Dynamic batching Queue<br/>core/src/queue.rs"]
    end
    
    subgraph "Backend Layer - backends crate"
        BackendTrait["Backend trait<br/>backends/core/src/lib.rs"]
        
        Candle["CandleBackend<br/>backends/candle"]
        ORT["OrtBackend<br/>backends/ort"]
        Python["PythonBackend<br/>backends/python"]
    end
    
    subgraph "Model Loading"
        HFHub["Hugging Face Hub<br/>hf-hub API"]
        LocalCache["Local cache<br/>~/.cache/huggingface"]
    end
    
    HTTPClient -->|"POST /embed"| HTTPServer
    GRPCClient -->|"tei.v1.Embed/Embed"| GRPCServer
    PrometheusClient -->|"GET /metrics"| HTTPServer
    
    HTTPServer --> Endpoints
    GRPCServer --> Endpoints
    
    Endpoints --> Infer
    Infer --> Tokenization
    Infer --> Queue
    Queue --> BackendTrait
    
    BackendTrait --> Candle
    BackendTrait --> ORT
    BackendTrait --> Python
    
    Candle -.downloads.-> HFHub
    ORT -.downloads.-> HFHub
    Python -.downloads.-> HFHub
    HFHub --> LocalCache
```

**Key Architecture Characteristics:**
- **Async Router**: Built on `tokio` async runtime for non-blocking I/O. [Cargo.toml:38-38]()
- **Multi-threaded Tokenization**: CPU-bound tokenization runs in OS thread pool. [router/src/lib.rs:47-47]()
- **Dynamic Batching**: Token budget tracking in `Queue` maximizes GPU utilization. [router/src/main.rs:73-74]()
- **Backend Abstraction**: `Backend` trait enables swapping between Candle/ORT/Python implementations. [Cargo.toml:3-11]()
- **Safetensors Loading**: All backends use `.safetensors` format for fast weight loading. [README.md:60-60]()

Sources: [router/src/lib.rs:44-378](), [Cargo.toml:1-23](), [README.md:47-61]()

## Core Components and Data Flow

The TEI core components implement the request processing pipeline, from tokenization through batching to inference.

**Core Component Structure**

```mermaid
classDiagram
    class Infer {
        +tokenization: Tokenization
        +queue: Queue
        +backend: Backend
        +max_concurrent_requests: usize
        +embed(request) Result~EmbedResponse~
        +predict(request) Result~PredictResponse~
        +rerank(request) Result~RerankResponse~
    }
    
    class Tokenization {
        +workers: usize
        +tokenizer: Tokenizer
        +max_input_length: usize
        +position_offset: usize
        +default_prompt: Option~String~
        +prompts: HashMap~String, String~
        +encode(inputs) ValidEncoding
        +decode(ids) String
    }
    
    class Queue {
        +padded_model: bool
        +max_batch_tokens: usize
        +max_batch_requests: Option~usize~
        +next_batch() NextBatch
    }
    
    class Backend {
        <<trait>>
        +max_batch_size: Option~usize~
        +padded_model: bool
        +health() Result
        +embed(batch) Embeddings
        +predict(batch) Predictions
        +warmup() Result
    }
    
    class ModelType {
        <<enum>>
        Classifier
        Embedding(Pool)
    }
    
    class Pool {
        <<enum>>
        Cls
        Mean
        LastToken
        Splade
    }
    
    Infer --> Tokenization: uses
    Infer --> Queue: manages
    Infer --> Backend: delegates
    Backend --> ModelType: configured with
    ModelType --> Pool: contains for embedding
```

**Component Responsibilities:**

| Component | Key Functions | Purpose |
|-----------|---------------|---------|
| `Infer` | `embed()`, `predict()`, `rerank()` | Request orchestration, admission control via semaphore. [router/src/lib.rs:31-31]() |
| `Tokenization` | `encode()`, `decode()` | Multi-threaded tokenization with prompt injection. [router/src/lib.rs:33-33]() |
| `Queue` | `next_batch()` | Dynamic batching with token budget tracking. [router/src/lib.rs:32-32]() |
| `Backend` | `embed()`, `predict()`, `warmup()` | Abstract inference interface. [router/src/lib.rs:29-29]() |

**Request Admission Control:**
- Semaphore-based limiting via `max_concurrent_requests` in `Infer`. [router/src/main.rs:59-60]()
- Returns HTTP 429 when limit exceeded to prevent queue buildup. [docs/openapi.json:173-186]()
- Per-request tracking with `tokio::sync::Semaphore`. [Cargo.toml:38-38]()

Sources: [router/src/lib.rs:244-306](), [README.md:47-61]()

## Request Processing Pipeline

Requests flow through multiple stages with detailed timing instrumentation at each step. The pipeline is designed to maximize throughput while maintaining low latency.

**Request Processing Sequence**

```mermaid
sequenceDiagram
    participant Client
    participant Router as "HTTP/gRPC Server"
    participant Infer as "Infer::embed()"
    participant Tokenization as "Tokenization::encode()"
    participant Queue as "Queue::next_batch()"
    participant Backend as "Backend::embed()"
    
    Client->>Router: POST /embed {inputs, normalize, truncate}
    
    Router->>Router: Validate max_client_batch_size
    Router->>Infer: Acquire semaphore permit
    
    alt Overloaded
        Infer-->>Router: 429 Overloaded
        Router-->>Client: HTTP 429
    end
    
    Infer->>Tokenization: encode(inputs, truncate)
    Note over Tokenization: Multi-threaded workers<br/>Prompt injection<br/>Character validation<br/>Truncation
    
    Tokenization-->>Infer: ValidEncoding {tokens, positions}
    
    Infer->>Queue: Append to batch queue
    Note over Queue: Token budget tracking<br/>max_batch_tokens check<br/>max_batch_requests check<br/>Client disconnect detection
    
    Queue->>Queue: Wait for batch full or timeout
    Queue->>Backend: embed(NextBatch)
    
    Note over Backend: Model forward pass<br/>Pooling strategy (CLS/Mean/LastToken)<br/>Optional normalization
    
    Backend-->>Queue: Embeddings
    Queue-->>Infer: Results
    
    Infer->>Infer: Record metrics & traces
    Infer-->>Router: EmbedResponse + metadata
    
    Router->>Router: Add headers:<br/>x-compute-time<br/>x-tokenization-time<br/>x-queue-time<br/>x-inference-time
    
    Router-->>Client: HTTP 200 + embeddings
```

**Pipeline Stages and Timing:**

1. **Validation**: Request size, batch size checks in router handlers. [router/src/main.rs:81-82]()
2. **Tokenization**: Parallel tokenization in OS thread pool. [router/src/main.rs:35-36]()
3. **Queue Wait**: Dynamic batching until `max_batch_tokens` reached. [router/src/main.rs:73-74]()
4. **Backend Inference**: GPU/CPU forward pass with hardware acceleration. [README.md:57-59]()
5. **Response Assembly**: Metadata headers, Prometheus recording, OpenTelemetry spans. [router/src/lib.rs:66-67]()

Sources: [router/src/lib.rs:44-70](), [README.md:123-128]()

## Deployment Architecture

TEI provides multiple deployment options with pre-built Docker images optimized for different hardware platforms. The build matrix generates specialized images for maximum performance.

**Multi-Platform Deployment Options**

```mermaid
graph TB
    subgraph "Source Repository"
        RustSource["Rust codebase<br/>router + backends/candle"]
        PythonSource["Python backend<br/>backends/python"]
        Dockerfiles["Platform-specific<br/>Dockerfiles"]
    end
    
    subgraph "Docker Image Registry"
        CPUImage["ghcr.io/.../text-embeddings-inference:cpu-1.9"]
        TuringImage["ghcr.io/.../text-embeddings-inference:turing-1.9<br/>CUDA CC 75 - T4, RTX 2000"]
        AmpereImage["ghcr.io/.../text-embeddings-inference:1.9<br/>CUDA CC 80 - A100, A30"]
        A10Image["ghcr.io/.../text-embeddings-inference:86-1.9<br/>CUDA CC 86 - A10, A40"]
        AdaImage["ghcr.io/.../text-embeddings-inference:89-1.9<br/>CUDA CC 89 - RTX 4000"]
        HopperImage["ghcr.io/.../text-embeddings-inference:hopper-1.9<br/>CUDA CC 90 - H100"]
        BlackwellImage["ghcr.io/.../text-embeddings-inference:1.9<br/>CUDA CC 100/120 - B200/RTX 5090"]
    end
    
    subgraph "Deployment Targets"
        Local["Local GPU<br/>Docker / cargo install"]
        Cloud["Cloud Providers<br/>AWS, GCP, Azure"]
        SageMaker["Amazon SageMaker<br/>Custom entrypoints"]
        K8s["Kubernetes<br/>Deployment manifests"]
    end
    
    RustSource --> CPUImage
    RustSource --> TuringImage
    RustSource --> AmpereImage
    RustSource --> A10Image
    RustSource --> AdaImage
    RustSource --> HopperImage
    RustSource --> BlackwellImage
    
    CPUImage --> Local
    AmpereImage --> Cloud
    AmpereImage --> SageMaker
    A10Image --> K8s
```

**Docker Image Selection Guide:**

| Hardware | CUDA Compute Capability | Docker Image Tag | Flash Attention |
|----------|------------------------|------------------|-----------------|
| Intel/AMD CPU | N/A | `cpu-1.9` | No |
| NVIDIA T4, RTX 2000 | 75 (Turing) | `turing-1.9` | v1 |
| NVIDIA A100, A30 | 80 (Ampere) | `1.9` (default) | v2 |
| NVIDIA RTX 4000 | 89 (Ada) | `89-1.9` | v2 |
| NVIDIA H100 | 90 (Hopper) | `hopper-1.9` | v2 |
| NVIDIA B200, RTX 5090 | 100/120 (Blackwell) | `1.9` | v2 |

Sources: [docs/source/en/supported_models.md:70-95](), [docs/source/en/custom_container.md:30-36](), [Cargo.toml:1-23]()

## Supported Model Types

TEI categorizes models into three types based on their architecture and determines available API endpoints accordingly.

**Model Type Detection and API Routing**

```mermaid
graph TB
    ConfigJSON["config.json parsing<br/>ModelConfig struct"]
    
    ConfigJSON --> ArchCheck["Check 'architectures' array"]
    ConfigJSON --> LabelCheck["Check id2label/label2id"]
    
    LabelCheck --> MultiClass["Multiple classes<br/>(len > 1)"]
    LabelCheck --> SingleClass["Single class<br/>(len == 1)"]
    
    MultiClass --> ClassifierModel["ModelType::Classifier"]
    SingleClass --> RerankerModel["ModelType::Reranker"]
    
    ArchCheck --> EmbeddingModel["Embedding architectures"]
    
    ClassifierModel --> PredictEndpoint["/predict endpoint"]
    RerankerModel --> RerankEndpoint["/rerank endpoint"]
    
    EmbeddingModel --> EmbedEndpoints["/embed, /embed_all<br/>/v1/embeddings"]
```

**Supported Embedding Models:**

| Model Family | Position Encoding | Examples |
|--------------|------------------|----------|
| Qwen3 | RoPE | `Qwen/Qwen3-Embedding-8B` |
| Qwen2 | RoPE | `Alibaba-NLP/gte-Qwen2-7B-instruct` |
| XLM-RoBERTa | Absolute | `multilingual-e5-large-instruct` |
| JinaBERT | ALiBi | `jina-embeddings-v2-base-en` |
| ModernBERT | Absolute | `ModernBERT-large` |

**Pooling Strategy Selection:**

For embedding models, TEI supports four pooling strategies (configured via `--pooling` or auto-detected): [docs/source/en/cli_arguments.md:65-69]()

- **CLS**: Select the CLS token.
- **Mean**: Average all token embeddings.
- **LastToken**: Select the last token.
- **Splade**: Sparse Lexical and Expansion.

Sources: [router/src/lib.rs:118-141](), [docs/source/en/supported_models.md:21-67]()

## Performance Optimizations

TEI implements multiple optimization techniques to maximize throughput and minimize latency.

**Token-Based Dynamic Batching:**
The `Queue` component groups requests based on token counts:
- **Token Budget Tracking**: Tracks total tokens via `max_batch_tokens` (default: 16384). [router/src/main.rs:73-74]()
- **Client Disconnect Detection**: Prevents wasted computation on abandoned requests. [router/src/main.rs:59-60]()

**Hardware-Specific Optimizations:**
- **Flash Attention**: Optimized kernels for CUDA devices. [README.md:57-58]()
- **cuBLASLt**: Fused matrix operations for NVIDIA GPUs. [README.md:59-59]()
- **Candle**: Rust-native ML framework for low-overhead execution. [README.md:58-58]()

Sources: [README.md:51-62](), [router/src/main.rs:62-82]()

## Observability and Monitoring

TEI provides comprehensive observability through Prometheus metrics and OpenTelemetry tracing. [README.md:62-62]()

**Monitoring Features:**
- **Prometheus Metrics**: Exported on a configurable port (default: 9000). [router/src/lib.rs:68-68]()
- **OpenTelemetry**: Distributed tracing via `--otlp-endpoint`. [router/src/lib.rs:66-66]()
- **Timing Headers**: All HTTP responses include `x-compute-time`, `x-tokenization-time`, etc. [docs/source/en/quick_tour.md:103-103]()

Sources: [router/src/lib.rs:64-68](), [docs/openapi.json:1-15]()

## Configuration and Deployment

TEI is configured via command-line arguments or environment variables. [router/src/main.rs:13-15]()

**Essential Parameters:**
- `--model-id`: HF Hub ID or local path. [router/src/main.rs:25-25]()
- `--dtype`: Force model precision (`float16`, `float32`). [router/src/main.rs:40-40]()
- `--max-batch-tokens`: Critical control for hardware usage. [router/src/main.rs:74-74]()
- `--hf-token`: For private or gated models. [router/src/main.rs:144-144]()

For details, see [System Architecture](#1.1), [Features and Capabilities](#1.2), and [Model Types and Endpoint Routing](#1.3).

Sources: [router/src/main.rs:13-158](), [docs/source/en/cli_arguments.md:1-150]()

---

