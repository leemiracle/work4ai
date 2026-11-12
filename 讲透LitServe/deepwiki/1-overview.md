<!-- source: DeepWiki mcp.deepwiki.com · repo Lightning-AI/LitServe · page 1 Overview · fetched 2026-10-21 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [src/litserve/__about__.py](src/litserve/__about__.py)
- [src/litserve/python_client.py](src/litserve/python_client.py)
- [tests/conftest.py](tests/conftest.py)
- [tests/e2e/test_e2e.py](tests/e2e/test_e2e.py)
- [tests/simple_server.py](tests/simple_server.py)
- [tests/simple_server_diff_port.py](tests/simple_server_diff_port.py)

</details>



## Purpose and Scope

This document provides a high-level introduction to the LitServe framework, its core architectural components, and primary use cases. LitServe is a lightweight AI inference server designed to deploy machine learning models and build complete AI systems with minimal configuration. 

For detailed implementation guides on specific components, see [Core Concepts](#2). For installation and setup instructions, see [Installation & Quick Start](#1.1). For detailed architectural patterns, see [Architecture Overview](#1.2).

## What is LitServe

LitServe is a Python framework for building custom inference engines with expert control. Unlike rigid serving engines like vLLM (designed for specific model types), LitServe provides low-level control to serve any model type—vision, audio, text, multi-modal—and define exactly how inference works. This includes custom batching, caching, streaming, routing, multi-model orchestration, and custom logic.

Built on FastAPI, LitServe is optimized for AI workloads and delivers 2× faster throughput through specialized multi-worker handling. The framework is designed for building inference APIs, agents, chatbots, MCP servers, RAG systems, and complex pipelines without MLOps overhead.

### Core Value Proposition

- **Full control**: Define custom inference logic rather than conforming to rigid abstractions
- **Any model type**: Support PyTorch, TensorFlow, JAX, and any Python-based model
- **No MLOps overhead**: Pure Python implementation without YAML configuration or infrastructure glue
- **Performance optimized**: 2× faster than plain FastAPI with specialized AI workload handling
- **Flexible deployment**: Self-host or deploy to Lightning AI cloud with GPU autoscaling

**Sources:** [README.md:1-75](), [src/litserve/__about__.py:20]()

## Core Architecture

LitServe follows a modular architecture where user-defined models integrate with the framework through the `LitAPI` abstraction, while `LitServer` orchestrates request processing and HTTP handling.

### System Components

**Figure 1: Core Architecture and Code Entity Mapping**

```mermaid
graph TB
    subgraph User["User Code"]
        UserLitAPI["User's LitAPI subclass<br/>Example: SimpleLitAPI"]
        UserModel["User's model<br/>self.model in setup()"]
    end
    
    subgraph Core["LitServe Core (src/litserve/)"]
        LitAPI["LitAPI base class<br/>src/litserve/api.py"]
        LitServer["LitServer orchestrator<br/>src/litserve/server.py"]
        FastAPIApp["FastAPI() app instance<br/>self.app in LitServer"]
    end
    
    subgraph Loops["Processing Loops (src/litserve/loops/)"]
        SingleLoop["SingleLoop<br/>loops/single.py"]
        BatchedLoop["BatchedLoop<br/>loops/batched.py"]
        StreamingLoop["StreamingLoop<br/>loops/streaming.py"]
        BatchedStreamLoop["BatchedStreamingLoop<br/>loops/batched_streaming.py"]
        ContBatchLoop["ContinuousBatchingLoop<br/>loops/continuous_batching.py"]
    end
    
    subgraph Specs["API Specs (src/litserve/specs/)"]
        LitSpec["LitSpec base<br/>specs/base.py"]
        OpenAISpec["OpenAISpec<br/>specs/openai.py"]
        EmbedSpec["OpenAIEmbeddingSpec<br/>specs/openai.py"]
    end
    
    subgraph Transport["Communication (src/litserve/)"]
        ReqQueue["request_queue<br/>multiprocessing.Queue"]
        Transport["message_transport<br/>MessageTransport"]
        RespBuffer["response_buffer<br/>asyncio.Queue"]
    end
    
    UserLitAPI -->|"extends"| LitAPI
    UserLitAPI -->|"loads"| UserModel
    LitServer -->|"instantiates"| UserLitAPI
    LitServer -->|"creates"| FastAPIApp
    LitServer -->|"spawns workers with"| SingleLoop
    LitServer -->|"spawns workers with"| BatchedLoop
    LitServer -->|"spawns workers with"| StreamingLoop
    LitServer -->|"spawns workers with"| BatchedStreamLoop
    LitServer -->|"spawns workers with"| ContBatchLoop
    
    LitServer -->|"creates"| ReqQueue
    LitServer -->|"creates"| Transport
    LitServer -->|"creates"| RespBuffer
    
    UserLitAPI -->|"optional"| LitSpec
    LitSpec -->|"subclassed by"| OpenAISpec
    LitSpec -->|"subclassed by"| EmbedSpec
    
    FastAPIApp -->|"POST /predict"| ReqQueue
    FastAPIApp -->|"GET /health"| UserLitAPI
```

**Sources:** [tests/simple_server.py:20-31](), [tests/conftest.py:43-54](), [src/litserve/api.py](), [src/litserve/server.py](), [src/litserve/loops/](), [src/litserve/specs/]()

### Request Processing Pipeline

**Figure 2: Method Call Flow with Code Entities**

```mermaid
sequenceDiagram
    participant Client
    participant App as "FastAPI app<br/>(LitServer.app)"
    participant Queue as "request_queue<br/>(mp.Queue)"
    participant Worker as "Worker Process"
    participant Loop as "LitLoop.run()"
    participant API as "LitAPI Instance"
    
    Client->>App: "POST /predict"
    App->>Queue: "queue.put(request, uid)"
    
    Note over Worker: "Spawned via mp.Process"
    
    Worker->>Queue: "queue.get()"
    Queue->>Worker: "request, uid"
    
    Worker->>Loop: "run(lit_api, request_queue, ...)"
    
    Loop->>API: "decode_request(request)"
    API-->>Loop: "decoded input"
    
    alt "max_batch_size > 1"
        Loop->>API: "batch([inputs])"
        API-->>Loop: "batched tensor"
    end
    
    Loop->>API: "predict(input)"
    API-->>Loop: "output"
    
    alt "max_batch_size > 1"
        Loop->>API: "unbatch(output)"
        API-->>Loop: "[individual outputs]"
    end
    
    Loop->>API: "encode_response(output)"
    API-->>Loop: "response dict"
    
    Worker->>App: "transport.send(uid, response)"
    App->>Client: "HTTP 200 + JSON"
```

**Sources:** [tests/simple_server.py:20-36](), [tests/conftest.py:43-54](), [README.md:87-107](), [src/litserve/server.py](), [src/litserve/loops/]()

## Key Components Overview

| Component | File Location | Core Responsibilities | Key Methods/Attributes |
|-----------|---------------|----------------------|----------------------|
| **`LitAPI`** | `src/litserve/api.py` | Abstract base class for model logic | `setup(device)`, `predict(x)`, `decode_request(request)`, `encode_response(output)`, `batch(inputs)`, `unbatch(outputs)` |
| **`LitServer`** | `src/litserve/server.py` | Orchestration and HTTP server | `__init__(lit_api, accelerator, devices)`, `run(port)`, `app` (FastAPI instance) |
| **`SingleLoop`** | `src/litserve/loops/single.py` | Sequential request processing | `run(lit_api, request_queue, message_transport)` |
| **`BatchedLoop`** | `src/litserve/loops/batched.py` | Batched request processing | `run()`, batch collection with `max_batch_size` and `batch_timeout` |
| **`StreamingLoop`** | `src/litserve/loops/streaming.py` | Generator-based streaming | `run()`, handles generator yields from `predict()` |
| **`LitSpec`** | `src/litserve/specs/base.py` | Protocol specification base | `decode_request()`, `encode_response()`, `add_endpoint()` |
| **`OpenAISpec`** | `src/litserve/specs/openai.py` | OpenAI Chat Completions API | `/v1/chat/completions`, `/v1/models` endpoints |
| **`MessageTransport`** | `src/litserve/transport.py` | IPC for worker responses | `send(uid, response)`, `recv()` |

### Core Workflow

1. **Initialization**: User instantiates `LitServer(lit_api_instance)` with their `LitAPI` subclass
2. **Server Start**: `LitServer.run(port)` spawns worker processes via `multiprocessing.Process`
3. **Worker Setup**: Each worker calls `lit_api.setup(device)` to load models onto assigned GPU/CPU
4. **Request Routing**: FastAPI `POST /predict` endpoint puts requests into `multiprocessing.Queue`
5. **Loop Processing**: Workers run selected loop (`SingleLoop`, `BatchedLoop`, etc.) that calls `decode_request()` → `predict()` → `encode_response()`
6. **Response Delivery**: Responses sent via `MessageTransport` back to FastAPI for HTTP response

**Sources:** [tests/simple_server.py:20-36](), [tests/conftest.py:43-101](), [README.md:87-108](), [src/litserve/api.py](), [src/litserve/server.py]()

## Deployment Options

### Self-Hosted Deployment

```bash
# Direct Python execution (development)
python server.py  # Starts uvicorn server on port 8000

# Lightning CLI deployment (self-hosted with tooling)
lightning deploy server.py

# Client code generation
# Auto-generates client.py for testing when server starts
```

When `LitServer.run(port=8000)` is called, it:
1. Spawns worker processes via `multiprocessing.Process`
2. Starts FastAPI with uvicorn on specified port
3. Optionally generates `client.py` with sample HTTP requests

**Sources:** [tests/simple_server.py:34-36](), [tests/simple_server_diff_port.py:32-34](), [src/litserve/python_client.py:1-8]()

### Lightning AI Cloud Deployment

```bash
# Deploy with managed infrastructure
lightning deploy server.py --cloud
```

### Feature Comparison

| Feature | Self-Hosted (`python server.py`) | Lightning AI Cloud |
|---------|----------------------------------|-------------------|
| **Core Features** | | |
| Batching (`max_batch_size`) | ✅ | ✅ |
| Streaming (`stream=True`) | ✅ | ✅ |
| GPU acceleration (`accelerator="cuda"`) | ✅ (requires GPU hardware) | ✅ (H100s from $1.75/hr) |
| OpenAI compatibility (`OpenAISpec`) | ✅ | ✅ |
| MCP integration (`MCP` class) | ✅ | ✅ |
| Multi-worker (`workers_per_device`) | ✅ | ✅ |
| **Infrastructure** | | |
| Load balancing | ❌ Manual setup | ✅ Built-in |
| GPU autoscaling | ❌ Manual | ✅ Auto scale up/down |
| Scale-to-zero | ❌ | ✅ Serverless |
| Authentication | ❌ DIY | ✅ Token/password |
| Monitoring & logs | ❌ DIY | ✅ Built-in observability |
| SLA uptime guarantee | ❌ | ✅ 99.995% |

**Sources:** [README.md:196-249](), [README.md:110-119]()

### Testing Your Server

```bash
# Auto-generated client (created by LitServer.run())
python client.py

# Manual curl test
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"input": 4.0}'

# Expected response: {"output": 16.0}
```

**Sources:** [tests/e2e/test_e2e.py:64-69](), [tests/e2e/test_e2e.py:122-124](), [src/litserve/python_client.py:1-8]()

## Framework Capabilities

LitServe provides specialized support for common AI deployment patterns:

- **Multi-model systems**: Single API can orchestrate multiple models, databases, and external services
- **Streaming responses**: Real-time generation for LLM chat and text completion use cases  
- **Batching strategies**: Dynamic batching with configurable timeouts for throughput optimization
- **OpenAI compatibility**: Drop-in replacement for OpenAI API endpoints
- **MCP integration**: Model Context Protocol support for AI agent frameworks
- **Hardware acceleration**: Automatic GPU detection and device allocation

For implementation details on these features, see [Advanced Features](#4). For protocol-specific guides, see [API Specifications](#3).

**Sources:** [README.md:147-161](), [README.md:198-237]()

---

