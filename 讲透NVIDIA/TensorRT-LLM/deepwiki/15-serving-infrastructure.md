<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/TensorRT-LLM · page 15 Serving Infrastructure · fetched 2026-10-26 -->

# Serving Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tensorrt_llm/disaggregated_params.py](tensorrt_llm/disaggregated_params.py)
- [tensorrt_llm/llmapi/disagg_utils.py](tensorrt_llm/llmapi/disagg_utils.py)
- [tensorrt_llm/llmapi/reasoning_parser.py](tensorrt_llm/llmapi/reasoning_parser.py)
- [tensorrt_llm/llmapi/thinking_budget.py](tensorrt_llm/llmapi/thinking_budget.py)
- [tensorrt_llm/sampling_params.py](tensorrt_llm/sampling_params.py)
- [tensorrt_llm/serve/chat_tokenization.py](tensorrt_llm/serve/chat_tokenization.py)
- [tensorrt_llm/serve/conversation_id.py](tensorrt_llm/serve/conversation_id.py)
- [tensorrt_llm/serve/harmony_adapter.py](tensorrt_llm/serve/harmony_adapter.py)
- [tensorrt_llm/serve/openai_client.py](tensorrt_llm/serve/openai_client.py)
- [tensorrt_llm/serve/openai_disagg_server.py](tensorrt_llm/serve/openai_disagg_server.py)
- [tensorrt_llm/serve/openai_disagg_service.py](tensorrt_llm/serve/openai_disagg_service.py)
- [tensorrt_llm/serve/openai_protocol.py](tensorrt_llm/serve/openai_protocol.py)
- [tensorrt_llm/serve/openai_server.py](tensorrt_llm/serve/openai_server.py)
- [tensorrt_llm/serve/perf_metrics.py](tensorrt_llm/serve/perf_metrics.py)
- [tensorrt_llm/serve/postprocess_handlers.py](tensorrt_llm/serve/postprocess_handlers.py)
- [tensorrt_llm/serve/responses_utils.py](tensorrt_llm/serve/responses_utils.py)
- [tensorrt_llm/serve/router.py](tensorrt_llm/serve/router.py)
- [tensorrt_llm/serve/router_utils.py](tensorrt_llm/serve/router_utils.py)
- [tests/integration/defs/disaggregated/test_ad_disagg.py](tests/integration/defs/disaggregated/test_ad_disagg.py)
- [tests/integration/defs/disaggregated/test_ad_disagg_trtllm_serve.py](tests/integration/defs/disaggregated/test_ad_disagg_trtllm_serve.py)
- [tests/integration/defs/disaggregated/test_disaggregated_etcd.py](tests/integration/defs/disaggregated/test_disaggregated_etcd.py)
- [tests/integration/defs/disaggregated/test_disaggregated_single_gpu.py](tests/integration/defs/disaggregated/test_disaggregated_single_gpu.py)
- [tests/integration/defs/disaggregated/test_workers.py](tests/integration/defs/disaggregated/test_workers.py)
- [tests/unittest/disaggregated/test_coordinator_worker.py](tests/unittest/disaggregated/test_coordinator_worker.py)
- [tests/unittest/disaggregated/test_disagg_internal_auth.py](tests/unittest/disaggregated/test_disagg_internal_auth.py)
- [tests/unittest/disaggregated/test_disagg_openai_client.py](tests/unittest/disaggregated/test_disagg_openai_client.py)
- [tests/unittest/disaggregated/test_disagg_utils.py](tests/unittest/disaggregated/test_disagg_utils.py)
- [tests/unittest/disaggregated/test_disaggregated_params.py](tests/unittest/disaggregated/test_disaggregated_params.py)
- [tests/unittest/disaggregated/test_openai_disagg_server.py](tests/unittest/disaggregated/test_openai_disagg_server.py)
- [tests/unittest/disaggregated/test_openai_disagg_service.py](tests/unittest/disaggregated/test_openai_disagg_service.py)
- [tests/unittest/disaggregated/test_router.py](tests/unittest/disaggregated/test_router.py)
- [tests/unittest/llmapi/apps/_test_openai_chat.py](tests/unittest/llmapi/apps/_test_openai_chat.py)
- [tests/unittest/llmapi/apps/_test_openai_chat_harmony.py](tests/unittest/llmapi/apps/_test_openai_chat_harmony.py)
- [tests/unittest/llmapi/apps/_test_openai_chat_harmony_perf_metrics.py](tests/unittest/llmapi/apps/_test_openai_chat_harmony_perf_metrics.py)
- [tests/unittest/llmapi/apps/_test_openai_completions.py](tests/unittest/llmapi/apps/_test_openai_completions.py)
- [tests/unittest/llmapi/apps/_test_openai_reasoning.py](tests/unittest/llmapi/apps/_test_openai_reasoning.py)
- [tests/unittest/llmapi/apps/_test_openai_responses.py](tests/unittest/llmapi/apps/_test_openai_responses.py)
- [tests/unittest/llmapi/apps/test_harmony_channel_validation.py](tests/unittest/llmapi/apps/test_harmony_channel_validation.py)
- [tests/unittest/llmapi/apps/test_harmony_parsing.py](tests/unittest/llmapi/apps/test_harmony_parsing.py)
- [tests/unittest/llmapi/test_reasoning_parser.py](tests/unittest/llmapi/test_reasoning_parser.py)
- [tests/unittest/llmapi/test_sampling_params.py](tests/unittest/llmapi/test_sampling_params.py)

</details>



This page documents the HTTP serving layer of TensorRT-LLM: the server classes, FastAPI endpoint registration, protocol schemas, routing, and response post-processing. It covers both the standard single-server deployment and the disaggregated (prefill/decode-separated) deployment mode.

- For the CLI command that starts these servers, see [trtllm-serve: Inference Server](#4.1).
- For KV cache transfer mechanics between context and generation nodes, see [KV Cache Transfer and Disaggregated Cache](#20.3).
- For the post-processing workers that run detokenization in a separate process pool, see [Post-Processing Workers](#7.6).

---

## Architecture Overview

The serving layer provides two primary server implementations based on FastAPI and Uvicorn:

| Class | File | Role |
|---|---|---|
| `OpenAIServer` | [tensorrt_llm/serve/openai_server.py:204-206]() | Standard OpenAI-compatible HTTP server wrapping a single LLM instance. |
| `OpenAIDisaggServer` | [tensorrt_llm/serve/openai_disagg_server.py:139-141]() | Disaggregated orchestrating server that proxies requests to separate context and generation workers. |

**Server Architecture and Component Relationships**

```mermaid
graph TD
    subgraph "Natural_Language_Space"
        [HTTP_Client] -->|"/v1/chat/completions"| [FastAPI_App]
    end

    subgraph "Code_Entity_Space"
        [FastAPI_App] --> [OpenAIServer_py]
        [OpenAIServer_py] --> [AsyncLLM]
        [OpenAIServer_py] --> [OpenAIDisaggServer]
        
        [OpenAIDisaggServer] --> [OpenAIDisaggregatedService]
        [OpenAIDisaggregatedService] --> [Router]
        
        [Router] -->|HTTP_Proxy| [Context_Worker_Role]
        [Router] -->|HTTP_Proxy| [Generation_Worker_Role]
        
        [Context_Worker_Role] -.->|KV_Cache_Transfer| [Generation_Worker_Role]
    end
```
Sources: [tensorrt_llm/serve/openai_server.py:204-206](), [tensorrt_llm/serve/openai_disagg_server.py:139-165](), [tensorrt_llm/serve/openai_disagg_server.py:43-44]()

---

## OpenAI-Compatible Server (`OpenAIServer`)

The `OpenAIServer` class wraps a generator object (an `LLM` or `AsyncLLM` instance, a `MultimodalEncoder`, or a `VisualGen`) and exposes it over HTTP. For details, see [OpenAI Compatible Server](#15.1).

### Server Roles
The `ServerRole` enum determines which endpoint set is registered and how the underlying engine is utilized:

| Role | Value | Generator Type | Purpose |
|---|---|---|---|
| `CONTEXT` | 0 | `LLM` | Prefill-only worker in disaggregated serving. |
| `GENERATION` | 1 | `LLM` | Decode-only worker in disaggregated serving. |
| `MM_ENCODER` | 2 | `MultimodalEncoder` | Multimodal feature extraction. |
| `VISUAL_GEN` | 3 | `VisualGen` | Image/video generation models (Flux, WAN, etc.). |
| `EMBEDDING` | 4 | `LLM` | Embedding generation. |

Sources: [tensorrt_llm/llmapi/disagg_utils.py:77-82](), [tensorrt_llm/serve/openai_server.py:204-220]()

### Registered HTTP Endpoints
The server registers standard OpenAI endpoints and internal management routes:
- `/v1/chat/completions`: Chat completion with tool/reasoning support. [tensorrt_llm/serve/openai_server.py:74-75]()
- `/v1/completions`: Legacy text completion. [tensorrt_llm/serve/openai_server.py:76]()
- `/v1/responses`: Asynchronous Responses API for conversation history. [tensorrt_llm/serve/openai_server.py:81]()
- `/health` / `/metrics`: Liveness checks and Prometheus metrics collection. [tensorrt_llm/serve/router.py:91-97]()

---

## Protocol Schemas

All request and response types are Pydantic models derived from `OpenAIBaseModel` in `tensorrt_llm/serve/openai_protocol.py`.

**Core Request and Response Types**

```mermaid
classDiagram
    class "OpenAIBaseModel" {
        +populate_by_name: bool
    }
    class "CompletionRequest" {
        +model: str
        +prompt: Union[str, List[int]]
        +stream: bool
        +disaggregated_params: DisaggregatedParams
    }
    class "ChatCompletionRequest" {
        +messages: List[ChatMessage]
        +tools: List[ChatCompletionToolsParam]
        +stream: bool
    }
    class "DisaggregatedParams" {
        +request_type: str
        +ctx_request_id: int
        +encoded_opaque_state: str
    }
    "OpenAIBaseModel" <|-- "CompletionRequest"
    "OpenAIBaseModel" <|-- "ChatCompletionRequest"
    "CompletionRequest" *-- "DisaggregatedParams"
```
Sources: [tensorrt_llm/serve/openai_protocol.py:147-149](), [tensorrt_llm/serve/openai_protocol.py:177-224](), [tensorrt_llm/serve/openai_protocol.py:227-302](), [tensorrt_llm/serve/openai_protocol.py:56-59]()

---

## Disaggregated Serving Architecture

In disaggregated mode, prefill (context) and decode (generation) tasks run on separate server instances to optimize GPU utilization and reduce interference. `OpenAIDisaggServer` acts as the orchestrating front-end via `OpenAIDisaggregatedService`. For details, see [Disaggregated Serving Architecture](#15.2).

### Request Flow
1. **Context Phase**: The disagg service proxies the request to a context worker using `request_type: "context_only"`. [tensorrt_llm/serve/openai_disagg_server.py:79-83]()
2. **State Transfer**: The context worker returns `DisaggregatedParams` containing a `disagg_request_id` and `encoded_opaque_state`. [tensorrt_llm/serve/openai_disagg_server.py:88-90]()
3. **Generation Phase**: The disagg service proxies the request to a generation worker, passing the state metadata. The actual KV cache data is transferred out-of-band via specialized transceivers (NIXL/UCX). [tensorrt_llm/serve/openai_disagg_server.py:106-110]()

Sources: [tensorrt_llm/serve/openai_disagg_server.py:139-165](), [tensorrt_llm/serve/openai_disagg_server.py:43-44]()

---

## Service Discovery and Routing

The system supports both static and dynamic worker discovery to manage clusters of context and generation nodes. For details, see [Service Discovery and Routing](#15.3).

### Routers
`OpenAIDisaggServer` utilizes routers to distribute load across worker pools. [tensorrt_llm/serve/router.py:54]()
- `RoundRobinRouter`: Cyclic selection across available instances.
- `LoadBalancingRouter`: Selects based on active request counts or tokens reported by workers. [tensorrt_llm/serve/router.py:69-71]()
- `KvCacheAwareRouter`: Selects generation nodes based on prefix cache hits using `block_key_hasher` and worker `kv_cache_events`. [tensorrt_llm/serve/router.py:100-115]()

### Metadata Server
Workers register their availability, health, and metadata with a metadata server (e.g., `etcd`) if configured via `MetadataServerConfig`. [tensorrt_llm/serve/metadata_server.py:73]()

Sources: [tensorrt_llm/serve/router.py:15-38](), [tensorrt_llm/serve/openai_disagg_server.py:141-158](), [tensorrt_llm/llmapi/disagg_utils.py:172-178](), [tensorrt_llm/serve/metadata_server.py:29-30]()

---

## Tool Calling and Post-Processing

The serving layer includes sophisticated logic for parsing model outputs and formatting them for API consumers.

### Tool and Reasoning Parsers
- **Tool Calling**: `ToolParserFactory` creates model-specific parsers to extract function calls from generated text. It supports "strict" mode via structural tags in guided decoding. [tensorrt_llm/serve/openai_server.py:104]() For details, see [Tool Calling and Function Calling](#15.4).
- **Reasoning**: `ReasoningParserFactory` handles `<think>` tags and reasoning content extraction for models like DeepSeek-R1. [tensorrt_llm/serve/openai_server.py:52]() For details, see [Response Post-Processing and Reasoning Parsers](#15.5).

### Harmony Adapter
A specialized `HarmonyAdapter` is used for GPT-OSS models to handle channel-based message formatting and specialized reasoning/effort parameters. [tensorrt_llm/serve/openai_server.py:112]() For details, see [Harmony Adapter for GPT-OSS Models](#15.6).

Sources: [tensorrt_llm/serve/openai_server.py:104](), [tensorrt_llm/serve/openai_server.py:52](), [tensorrt_llm/serve/postprocess_handlers.py:89-95]()

---

