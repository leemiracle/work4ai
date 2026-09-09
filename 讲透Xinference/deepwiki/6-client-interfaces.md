> 来源: [https://deepwiki.com/xorbitsai/inference/6-client-interfaces](https://deepwiki.com/xorbitsai/inference/6-client-interfaces)
> DeepWiki xorbitsai/inference | Last indexed: 30 July 2026 (d97e09

# Client Interfaces

  Relevant source files 
 - [doc/source/getting_started/index.rst](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/getting_started/index.rst)
 - [doc/source/getting_started/using_docker_image.rst](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/getting_started/using_docker_image.rst)
 - [doc/source/getting_started/using_xinference.rst](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/getting_started/using_xinference.rst)
 - [doc/source/locale/zh_CN/LC_MESSAGES/getting_started/using_docker_image.po](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/locale/zh_CN/LC_MESSAGES/getting_started/using_docker_image.po)
 - [doc/source/locale/zh_CN/LC_MESSAGES/getting_started/using_xinference.po](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/locale/zh_CN/LC_MESSAGES/getting_started/using_xinference.po)
 - [doc/source/locale/zh_CN/LC_MESSAGES/user_guide/client_api.po](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/locale/zh_CN/LC_MESSAGES/user_guide/client_api.po)
 - [doc/source/reference/index.rst](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/reference/index.rst)
 - [doc/source/user_guide/client_api.rst](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/user_guide/client_api.rst)
 - [doc/source/user_guide/index.rst](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/user_guide/index.rst)
 - [xinference/client/__init__.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/client/__init__.py)
 - [xinference/client/common.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/client/common.py)
 - [xinference/client/handlers.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/client/handlers.py)
 
  This document provides an overview of the different interfaces available for interacting with Xinference. It covers the four primary client types (Python client library, command-line interface, web UI, and external integrations), their common patterns, and guidance on selecting the appropriate interface for different use cases.

 For detailed information about specific client implementations, see:

 
 - **Python Client Library**: [Python Client Library](https://deepwiki.com/xorbitsai/inference/6.1-python-client-library) — Documenting `RESTfulClient`, `AsyncRESTfulClient`, and model handles.
 - **Command Line Interface**: [Command Line Interface](https://deepwiki.com/xorbitsai/inference/6.2-command-line-interface) — Documenting CLI commands for cluster management and model interaction.
 - **Web UI**: [Web UI](https://deepwiki.com/xorbitsai/inference/6.3-web-ui) — Documenting the React-based interface for model management.
 - **External Client Integration**: [External Client Integration](https://deepwiki.com/xorbitsai/inference/6.4-external-client-integration) — Explaining integration with LangChain, LlamaIndex, and OpenAI/Anthropic SDKs.
 
 For information about the RESTful API that all clients communicate with, see [RESTful API](https://deepwiki.com/xorbitsai/inference/5-restful-api).

 
---

 
## Client Architecture Overview

 Xinference provides multiple client interfaces that all communicate with the same underlying RESTful API layer. This unified architecture ensures consistency across all client types while allowing users to choose the interface that best fits their workflow.

 
### System-to-Code Mapping: Client Flow

 The following diagram maps high-level client interactions to specific code entities within the `xinference.client` module and the deployment layer.

 
```

```

 **Sources:** [xinference/client/__init__.py15-21](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/client/__init__.py#L15-L21) [doc/source/getting_started/using_xinference.rst49-61](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/getting_started/using_xinference.rst#L49-L61) [doc/source/user_guide/client_api.rst18-19](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/user_guide/client_api.rst#L18-L19)

 
---

 
## Client Type Comparison

 The following table summarizes the key characteristics of each client interface:

 
| Client Type | Use Case | Communication | Key Features | Implementation |
|---|---|---|---|---|
| Python Sync Client | Scripts, sequential workflows | HTTP/REST | Synchronous blocking calls | RESTfulClient |
| Python Async Client | High concurrency, web apps | HTTP/REST | async/await non-blocking | AsyncRESTfulClient |
| CLI | Sysadmin, local deployment | HTTP/REST | Cluster startup, model list | xinference command |
| Web UI | Visual exploration | HTTP/REST | Interactive chat, GPU monitor | React/Next.js |
| External SDKs | Drop-in replacement | HTTP/REST | OpenAI/Anthropic compatibility | openai.Client |

 **Sources:** [doc/source/getting_started/using_xinference.rst49-53](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/getting_started/using_xinference.rst#L49-L53) [doc/source/user_guide/client_api.rst40-87](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/user_guide/client_api.rst#L40-L87) [xinference/client/__init__.py19-20](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/client/__init__.py#L19-L20)

 
---

 
## Common Client Operations

 All Xinference clients share a common set of operations for interacting with models. These operations follow a consistent pattern regardless of the client interface used.

 
### Model Lifecycle Operations

 
```

```

 **Key Operations:**

 
 - **Model Launch**: Start a model instance via `launch_model`. Users must specify `model_name`, and for LLMs, the `model_engine` (e.g., `vllm`, `llama.cpp`). [doc/source/getting_started/using_xinference.rst119-130](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/getting_started/using_xinference.rst#L119-L130)
 - **Model Retrieval**: Obtain a handle to a running model using `get_model(model_uid)`. [doc/source/user_guide/client_api.rst54](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/user_guide/client_api.rst#L54-L54)
 - **Inference**: Call methods like `chat()`, `generate()`, or `create_embedding()` on the handle. [doc/source/user_guide/client_api.rst59-62](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/user_guide/client_api.rst#L59-L62)
 - **Termination**: Stop the model and free resources using `terminate_model(model_uid)`. [doc/source/reference/index.rst29](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/reference/index.rst#L29-L29)
 
 **Sources:** [doc/source/getting_started/using_xinference.rst201-203](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/getting_started/using_xinference.rst#L201-L203) [doc/source/user_guide/client_api.rst45-62](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/user_guide/client_api.rst#L45-L62) [doc/source/reference/index.rst13-38](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/reference/index.rst#L13-L38)

 
---

 
## Model Handle Types

 Once a model is retrieved via `get_model`, the client returns a specific "Handle" class that provides the appropriate API for that model type.

 
### System-to-Code Mapping: Model Handles

 The following diagram maps the logical model types to the specific Python classes used in the client library.

 
```

```

 
| Handle Class | Primary Methods | Code Reference |
|---|---|---|
| ChatModelHandle | chat(), generate() | xinference/client/handlers.py23-24 |
| EmbeddingModelHandle | create_embedding() | xinference/client/handlers.py26-27 |
| ImageModelHandle | text_to_image() | xinference/client/handlers.py32-33 |
| AudioModelHandle | transcriptions(), speech() | xinference/client/handlers.py20-21 |
| RerankModelHandle | rerank() | xinference/client/reference/index.rst70-72 |

 
---

 
## Synchronous vs. Asynchronous Clients

 Xinference provides two main Python entry points. The choice depends on the application's concurrency model.

 
 - **`RESTfulClient` (Sync)**:

 
 - Built on `requests`.
 - Best for simple scripts or data science notebooks.
 - [xinference/client/__init__.py19](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/client/__init__.py#L19-L19)
 - **`AsyncRESTfulClient` (Async)**:

 
 - Built on `aiohttp`.
 - Best for web backends (FastAPI/Django) and high-throughput streaming.
 - [xinference/client/__init__.py20](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/client/__init__.py#L20-L20)
 
 
### Streaming Response Handling

 Both clients support streaming for LLMs via the `stream=True` parameter in `chat()` or `generate()`. The client provides iterators to process tokens as they are generated. [xinference/client/common.py30-100](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/client/common.py#L30-L100)

 **Sources:** [xinference/client/common.py30-64](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/client/common.py#L30-L64) [xinference/client/common.py66-99](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/client/common.py#L66-L99)

 
---

 
## Web UI

 The Web UI is a React/Next.js application served directly by the Xinference backend. It is bundled as a static export, so no Node.js runtime is required on the server. [doc/source/getting_started/using_xinference.rst55-58](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/getting_started/using_xinference.rst#L55-L58)

 
 - **Access**: Typically at `http://<host>:<port>/ui` (default port 9997). [doc/source/getting_started/using_xinference.rst52](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/getting_started/using_xinference.rst#L52-L52)
 - **Features**: Launching models from a gallery, interactive chat interface, and monitoring cluster status.
 
 
---

 
## Command Line Interface (CLI)

 The `xinference` CLI is the primary tool for managing the lifecycle of the Xinference cluster and performing quick model operations without writing code.

 **Common Commands:**

 
 - `xinference-local`: Starts a supervisor and worker in a single process. [doc/source/getting_started/using_xinference.rst27](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/getting_started/using_xinference.rst#L27-L27)
 - `xinference launch`: Launches a model on the cluster. [doc/source/getting_started/using_xinference.rst98](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/getting_started/using_xinference.rst#L98-L98)
 - `xinference list`: Lists all running model instances. [doc/source/getting_started/using_xinference.rst99](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/getting_started/using_xinference.rst#L99-L99)
 - `xinference engine`: Queries which engines (vLLM, llama.cpp, etc.) support a specific model. [doc/source/getting_started/using_xinference.rst135](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/getting_started/using_xinference.rst#L135-L135)
 
 **Sources:** [doc/source/getting_started/using_xinference.rst83-107](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/getting_started/using_xinference.rst#L83-L107) [doc/source/getting_started/using_xinference.rst144-157](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/getting_started/using_xinference.rst#L144-L157)

 
---

 
## External Client Integration

 Xinference is designed to be a drop-in replacement for proprietary AI services.

 
 - **OpenAI Compatibility**: Supports the OpenAI Python SDK by setting `base_url="http://<host>:<port>/v1"`. [doc/source/user_guide/client_api.rst76](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/user_guide/client_api.rst#L76-L76)
 - **Anthropic Compatibility**: Supports the Anthropic SDK via the `/anthropic` endpoint. [doc/source/user_guide/client_api.rst145-154](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/user_guide/client_api.rst#L145-L154)
 - **Frameworks**: Integrated with LangChain, LlamaIndex, and Dify for building RAG applications. [doc/source/user_guide/index.rst11](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/user_guide/index.rst#L11-L11)
 
 **Sources:** [doc/source/user_guide/client_api.rst64-87](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/user_guide/client_api.rst#L64-L87) [doc/source/user_guide/client_api.rst140-163](https://github.com/xorbitsai/inference/blob/d97e0970/doc/source/user_guide/client_api.rst#L140-L163)
