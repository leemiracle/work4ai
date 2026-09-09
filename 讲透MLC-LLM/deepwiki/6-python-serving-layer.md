> 来源: [https://deepwiki.com/mlc-ai/mlc-llm/6-python-serving-layer](https://deepwiki.com/mlc-ai/mlc-llm/6-python-serving-layer)
> DeepWiki mlc-ai/mlc-llm | Last indexed: 30 March 2026 (fcce2c

# Python Serving Layer

  Relevant source files 
 - [python/mlc_llm/cli/calibrate.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/cli/calibrate.py)
 - [python/mlc_llm/cli/chat.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/cli/chat.py)
 - [python/mlc_llm/cli/serve.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/cli/serve.py)
 - [python/mlc_llm/interface/chat.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/interface/chat.py)
 - [python/mlc_llm/interface/help.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/interface/help.py)
 - [python/mlc_llm/interface/serve.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/interface/serve.py)
 - [python/mlc_llm/json_ffi/__init__.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/json_ffi/__init__.py)
 - [python/mlc_llm/json_ffi/engine.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/json_ffi/engine.py)
 - [python/mlc_llm/protocol/mlc_chat_config.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/protocol/mlc_chat_config.py)
 - [python/mlc_llm/protocol/openai_api_protocol.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/protocol/openai_api_protocol.py)
 - [python/mlc_llm/serve/__init__.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/__init__.py)
 - [python/mlc_llm/serve/config.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/config.py)
 - [python/mlc_llm/serve/embedding_engine.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/embedding_engine.py)
 - [python/mlc_llm/serve/engine.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/engine.py)
 - [python/mlc_llm/serve/engine_base.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/engine_base.py)
 - [python/mlc_llm/serve/engine_utils.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/engine_utils.py)
 - [python/mlc_llm/serve/entrypoints/openai_entrypoints.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/entrypoints/openai_entrypoints.py)
 - [python/mlc_llm/serve/server/server_context.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/server/server_context.py)
 - [python/mlc_llm/serve/sync_engine.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/sync_engine.py)
 - [tests/python/serve/server/test_embedding_server.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/tests/python/serve/server/test_embedding_server.py)
 - [tests/python/serve/test_embedding_engine.py](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/tests/python/serve/test_embedding_engine.py)
 
  
## Purpose and Scope

 This page documents the Python-based serving interfaces that sit on top of the C++ runtime engine. The Python serving layer provides production-ready APIs for model inference, including OpenAI-compatible interfaces, asynchronous request handling, and streaming support.

 For details about the underlying C++ engine that executes model inference, see [C++ Runtime Engine](https://deepwiki.com/mlc-ai/mlc-llm/5-c++-runtime-engine). For information about the FastAPI REST endpoints, see [REST API Server](https://deepwiki.com/mlc-ai/mlc-llm/6.2-rest-api-server). For configuration options and runtime tuning, see [OpenAI API Protocol and Configuration](https://deepwiki.com/mlc-ai/mlc-llm/6.3-openai-api-protocol-and-configuration). For specialized orchestration, see [Microserving and Disaggregated Serving](https://deepwiki.com/mlc-ai/mlc-llm/6.4-microserving-and-disaggregated-serving).

 **Sources:** [python/mlc_llm/serve/engine_base.py1-32](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/engine_base.py#L1-L32)

 
## Architecture Overview

 The Python serving layer wraps the C++ threaded engine with Python interfaces that manage request lifecycle, streaming callbacks, and API protocol handling. The layer consists of four main components:

 
 - **Engine Classes** - Python wrappers around the C++ engine with different concurrency models.
 - **State Management** - Thread-safe callback system for streaming results.
 - **Protocol Handlers** - OpenAI API-compatible request/response processing.
 - **Server Context** - Multi-model registration and routing for the REST server.
 
 **Component map — Python Serving Layer**

 
```

```

 **Sources:** [python/mlc_llm/serve/engine_base.py551-680](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/engine_base.py#L551-L680) [python/mlc_llm/serve/engine.py835-900](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/engine.py#L835-L900) [python/mlc_llm/serve/server/server_context.py11-72](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/server/server_context.py#L11-L72) [python/mlc_llm/serve/embedding_engine.py11-105](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/embedding_engine.py#L11-L105)

 
## Engine Class Hierarchy

 The serving layer provides multiple engine variants built on a common base class. Each variant serves different use cases with different concurrency and API models. For details, see [Engine Classes](https://deepwiki.com/mlc-ai/mlc-llm/6.1-engine-classes).

 
| Engine Class | Use Case | API Style | Threading | Location |
|---|---|---|---|---|
| MLCEngineBase | Base implementation | N/A | Background threads | python/mlc_llm/serve/engine_base.py551 |
| AsyncMLCEngine | Production serving | Async/await | Event loop + threads | python/mlc_llm/serve/engine.py835 |
| MLCEngine | Testing/debugging | Synchronous | Blocking + threads | python/mlc_llm/serve/engine.py1353 |
| JSONFFIEngine | CLI/simple usage | Iterator-based | Background threads | python/mlc_llm/json_ffi/engine.py210 |
| SyncMLCEngine | Low-level debugging | Step-by-step | Manual stepping | python/mlc_llm/serve/sync_engine.py45 |

 
```

```

 **Sources:** [python/mlc_llm/serve/engine_base.py551-680](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/engine_base.py#L551-L680) [python/mlc_llm/serve/engine.py835-900](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/engine.py#L835-L900) [python/mlc_llm/serve/engine.py1353-1400](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/engine.py#L1353-L1400) [python/mlc_llm/json_ffi/engine.py210-272](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/json_ffi/engine.py#L210-L272) [python/mlc_llm/serve/sync_engine.py45-155](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/sync_engine.py#L45-L155)

 
## REST API Server

 The Python serving layer includes a `FastAPI`-based REST server that exposes OpenAI-compatible endpoints. The server is launched via the `mlc_llm serve` CLI command. For details, see [REST API Server](https://deepwiki.com/mlc-ai/mlc-llm/6.2-rest-api-server).

 The server uses `ServerContext` to manage multiple hosted models and their corresponding `AsyncMLCEngine` or `AsyncEmbeddingEngine` instances.

 **REST Entrypoint Diagram**

 
```

```

 **Sources:** [python/mlc_llm/interface/serve.py24-132](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/interface/serve.py#L24-L132) [python/mlc_llm/serve/entrypoints/openai_entrypoints.py1-132](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/entrypoints/openai_entrypoints.py#L1-L132) [python/mlc_llm/serve/server/server_context.py11-73](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/server/server_context.py#L11-L73)

 
## OpenAI API Protocol and Configuration

 The serving layer implements the OpenAI API protocol using `pydantic` models defined in `openai_api_protocol.py`. This ensures strict validation of incoming requests and standardized responses. Configuration is handled through `EngineConfig` (for runtime engine parameters) and `GenerationConfig` (for sampling parameters). For details, see [OpenAI API Protocol and Configuration](https://deepwiki.com/mlc-ai/mlc-llm/6.3-openai-api-protocol-and-configuration).

 **Key Protocol Entities:**

 
 - `ChatCompletionRequest`: Schema for `/v1/chat/completions`.
 - `EmbeddingRequest`: Schema for `/v1/embeddings`.
 - `EngineConfig`: Controls `max_num_sequence`, `gpu_memory_utilization`, and speculative decoding modes.
 - `GenerationConfig`: Controls `temperature`, `top_p`, and `stop` sequences.
 
 **Sources:** [python/mlc_llm/protocol/openai_api_protocol.py1-226](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/protocol/openai_api_protocol.py#L1-L226) [python/mlc_llm/serve/config.py9-170](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/config.py#L9-L170) [python/mlc_llm/protocol/generation_config.py1-120](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/protocol/generation_config.py#L1-L120)

 
## Microserving and Disaggregated Serving

 For advanced orchestration and distributed deployment, MLC LLM provides a "Microserving" API. This allows for sub-request-level LLM orchestration, such as disaggregating prefill and decode steps across different nodes. For details, see [Microserving and Disaggregated Serving](https://deepwiki.com/mlc-ai/mlc-llm/6.4-microserving-and-disaggregated-serving).

 **Sources:** [python/mlc_llm/serve/entrypoints/microserving_entrypoints.py1-50](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/entrypoints/microserving_entrypoints.py#L1-L50) [python/mlc_llm/serve/server/server_context.py1-73](https://github.com/mlc-ai/mlc-llm/blob/fcce2cc3/python/mlc_llm/serve/server/server_context.py#L1-L73)
