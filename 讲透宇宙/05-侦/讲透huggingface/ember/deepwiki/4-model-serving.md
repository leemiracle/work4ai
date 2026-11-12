<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/ember · page 4 Model Serving · fetched 2026-10-26 -->

# Model Serving

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [ember/serve.py](ember/serve.py)

</details>



This page documents the Ember embedding server, which provides HTTP API endpoints for generating embeddings using CoreML models. The server uses a multi-process architecture to handle concurrent requests and manage model lifecycles efficiently.

For information about converting models for serving, see [Model Creation](#3). For usage examples and client integration, see [Usage Examples](#5).

## Architecture Overview

The model serving system is built around a FastAPI application that manages multiple worker processes, each responsible for handling inference requests for specific models. The architecture separates HTTP request handling from model inference to provide isolation and concurrent processing capabilities.

### Core Components

```mermaid
graph TB
    subgraph "HTTP Layer"
        FastAPI["FastAPI app"]
        CORSMiddleware["CORSMiddleware"]
        APIEndpoints["/api/embed<br/>/api/models"]
    end
    
    subgraph "Process Management"
        ProcessManager["ProcessManager"]
        CleanupThread["cleanup_thread"]
    end
    
    subgraph "Worker Processes"
        ModelWorker1["model_worker<br/>(Process 1)"]
        ModelWorker2["model_worker<br/>(Process 2)"]
        ModelWorkerN["model_worker<br/>(Process N)"]
    end
    
    subgraph "Model Resources"
        CoreMLModel["CompiledMLModel"]
        AutoTokenizer["AutoTokenizer"]
        EmberConfig["ember_config.json"]
    end
    
    subgraph "Communication"
        InputQueue["input_queue<br/>(mp.Queue)"]
        OutputQueue["output_queue<br/>(mp.Queue)"]
        ShutdownEvent["shutdown_event<br/>(mp.Event)"]
    end
    
    FastAPI --> CORSMiddleware
    FastAPI --> APIEndpoints
    APIEndpoints --> ProcessManager
    ProcessManager --> CleanupThread
    ProcessManager --> ModelWorker1
    ProcessManager --> ModelWorker2
    ProcessManager --> ModelWorkerN
    
    ModelWorker1 --> InputQueue
    ModelWorker1 --> OutputQueue
    ModelWorker1 --> ShutdownEvent
    ModelWorker1 --> CoreMLModel
    ModelWorker1 --> AutoTokenizer
    ModelWorker1 --> EmberConfig
    
    ProcessManager --> InputQueue
    ProcessManager --> OutputQueue
```

**Sources:** [ember/serve.py:1-382]()

## API Endpoints

The server exposes two primary HTTP endpoints for interaction with the embedding service.

### POST /api/embed

The main endpoint for generating document embeddings. Accepts an `EmbeddingRequest` and returns an `EmbeddingResponse`.

| Field | Type | Description |
|-------|------|-------------|
| `model` | string | Model identifier (e.g., "intfloat/multilingual-e5-small") |
| `documents` | List[Document] | List of documents with content field |
| `options` | dict (optional) | Request options including keep_alive duration |

The endpoint validates batch sizes against model configuration and manages process lifecycle based on the `keep_alive` option.

### GET /api/models

Returns a list of currently active models in the process manager. This endpoint provides visibility into which models have running worker processes.

**Sources:** [ember/serve.py:326-367]()

## Process Management System

The `ProcessManager` class orchestrates worker processes and handles their lifecycle management through a sophisticated queuing and cleanup system.

### Process Lifecycle

```mermaid
sequenceDiagram
    participant Client as "HTTP Client"
    participant PM as "ProcessManager"
    participant Worker as "model_worker"
    participant Model as "CompiledMLModel"
    
    Client->>PM: "POST /api/embed request"
    PM->>PM: "get_or_create_process()"
    
    alt Process doesn't exist or died
        PM->>Worker: "mp.Process.start()"
        Worker->>Model: "ct.models.CompiledMLModel()"
        Worker->>PM: "Worker ready"
    end
    
    PM->>Worker: "input_queue.put(documents)"
    Worker->>Model: "model.predict(input_data)"
    Model-->>Worker: "embeddings"
    Worker->>PM: "output_queue.put(results)"
    PM-->>Client: "EmbeddingResponse"
    
    Note over Worker: "Process stays alive for keep_alive duration"
    
    PM->>PM: "_cleanup_expired_processes()"
    PM->>Worker: "shutdown_event.set()"
    Worker->>Worker: "Process terminates"
```

### Process Configuration

Each worker process is configured with:

- `PROCESS_LIFETIME_MINUTES = 5`: Default process lifetime
- `QUEUE_TIMEOUT = 20`: Timeout for queue operations
- `keep_alive`: User-configurable process lifetime from request options

The `ProcessManager` maintains a background cleanup thread that periodically terminates expired processes to prevent resource leaks.

**Sources:** [ember/serve.py:233-301]()

## Request Processing Flow

The serving system processes embedding requests through a multi-stage pipeline involving tokenization, batch padding, and CoreML inference.

### Worker Process Flow

```mermaid
flowchart TD
    Start["Worker Process Start"]
    LoadTokenizer["AutoTokenizer.from_pretrained()"]
    LoadConfig["ModelConfig.from_json()"]
    LoadModel["ct.models.CompiledMLModel()"]
    
    WaitRequest["input_queue.get()"]
    ValidateBatch["Validate batch_size <= config.batch_size"]
    Tokenize["tokenizer.batch_encode_plus()"]
    Pad["Pad to config.batch_size"]
    Predict["model.predict()"]
    Extract["Extract embeddings[:current_batch_sz]"]
    Respond["output_queue.put()"]
    
    CheckLifetime{"Process lifetime<br/>exceeded?"}
    CheckShutdown{"shutdown_event<br/>set?"}
    
    Start --> LoadTokenizer
    LoadTokenizer --> LoadConfig
    LoadConfig --> LoadModel
    LoadModel --> WaitRequest
    
    WaitRequest --> ValidateBatch
    ValidateBatch --> Tokenize
    Tokenize --> Pad
    Pad --> Predict
    Predict --> Extract
    Extract --> Respond
    
    Respond --> CheckLifetime
    CheckLifetime -->|No| CheckShutdown
    CheckShutdown -->|No| WaitRequest
    CheckLifetime -->|Yes| End["Process Shutdown"]
    CheckShutdown -->|Yes| End
    
    ValidateBatch -->|Failed| ErrorResponse["Error Response"]
    Tokenize -->|Failed| ErrorResponse
    Predict -->|Failed| ErrorResponse
    ErrorResponse --> CheckLifetime
```

The worker process handles batch validation, tokenization with padding/truncation, batch size padding for CoreML requirements, and extraction of results for the actual batch size.

**Sources:** [ember/serve.py:98-232]()

## Error Handling

The server implements structured error handling through the `EmbeddingError` system with specific error codes and HTTP status mapping.

### Error Types

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `BATCH_SIZE_EXCEEDED` | 422 | Request batch size exceeds model configuration |
| `MODEL_LOAD_FAILED` | 500 | CoreML model or tokenizer loading failed |
| `TOKENIZATION_FAILED` | 400 | Text tokenization processing error |
| `INFERENCE_FAILED` | 500 | CoreML model prediction error |
| `TIMEOUT` | 408 | Queue operation timeout |

Each error includes structured details for debugging and client error handling. The `EmbeddingErrorResponse` model provides consistent error formatting across all endpoints.

**Sources:** [ember/serve.py:27-76]()

## Model Configuration

Worker processes load configuration from `ember_config.json` files created during the model conversion process. The `ModelConfig` class defines essential parameters:

- `max_length`: Maximum sequence length for tokenization
- `batch_size`: Maximum batch size for inference

These parameters are enforced at runtime to ensure compatibility with the converted CoreML model's input requirements.

**Sources:** [ember/serve.py:89-96](), [ember/serve.py:115]()

## Server Configuration

The server is configured with production-ready defaults:

- **Host**: `0.0.0.0` (all interfaces)
- **Port**: `11434` (default)
- **Workers**: `1` (single worker process)
- **CORS**: Enabled for all origins
- **Logging**: Uvicorn format with color support

The `serve()` function provides the entry point for starting the server with configurable host and port parameters.

**Sources:** [ember/serve.py:368-378]()

---

