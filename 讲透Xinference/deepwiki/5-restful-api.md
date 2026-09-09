> 来源: [https://deepwiki.com/xorbitsai/inference/5-restful-api](https://deepwiki.com/xorbitsai/inference/5-restful-api)
> DeepWiki xorbitsai/inference | Last indexed: 30 July 2026 (d97e09

# RESTful API

  Relevant source files 
 - [xinference/_compat.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/_compat.py)
 - [xinference/api/restful_api.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py)
 - [xinference/api/routers/models.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/routers/models.py)
 - [xinference/api/schemas/__init__.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/schemas/__init__.py)
 - [xinference/api/schemas/requests.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/schemas/requests.py)
 - [xinference/api/tests/test_embedding_truncate.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/tests/test_embedding_truncate.py)
 - [xinference/client/restful/restful_client.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/client/restful/restful_client.py)
 - [xinference/client/tests/test_client.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/client/tests/test_client.py)
 - [xinference/constants.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/constants.py)
 - [xinference/core/model.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/model.py)
 - [xinference/core/supervisor.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/supervisor.py)
 - [xinference/core/tests/test_restful_api.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/tests/test_restful_api.py)
 - [xinference/core/tests/test_types.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/tests/test_types.py)
 - [xinference/core/worker.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/worker.py)
 - [xinference/deploy/cmdline.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/cmdline.py)
 - [xinference/deploy/test/test_cmdline.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/deploy/test/test_cmdline.py)
 - [xinference/model/embedding/sentence_transformers/tests/test_truncate_prompt_tokens.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/model/embedding/sentence_transformers/tests/test_truncate_prompt_tokens.py)
 - [xinference/types.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/types.py)
 - [xinference/ui/__init__.py](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/ui/__init__.py)
 
  The RESTful API is the primary HTTP-based interface for interacting with Xinference. Built with **FastAPI**, it provides endpoints for model management, inference operations, and cluster administration. All client interactions—whether through the Python SDK, CLI, Web UI, or external clients—communicate with Xinference through this layer.

 For information about client libraries that consume this API, see [Client Interfaces](https://deepwiki.com/xorbitsai/inference/6-client-interfaces). For authentication configuration details, see [Authentication and Authorization](https://deepwiki.com/xorbitsai/inference/5.5-authentication-and-authorization). For model management operations, see [Model Management Endpoints](https://deepwiki.com/xorbitsai/inference/5.1-model-management-endpoints).

 
## API Server Architecture

 The RESTful API is implemented in the `RESTfulAPI` class [xinference/api/restful_api.py160](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L160-L160) It acts as a gateway, translating HTTP requests into RPC calls for the `SupervisorActor` [xinference/core/supervisor.py127](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/supervisor.py#L127-L127)

 
### Request Processing Flow

 The following diagram bridges the "Natural Language Space" (HTTP Requests) to the "Code Entity Space" (FastAPI routes and Actor references).

 **API Request to Actor RPC Mapping**

 
```

```

 The `RESTfulAPI` class handles:

 
 - **Middleware**: CORS [xinference/api/restful_api.py331](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L331-L331) IP restriction [xinference/api/restful_api.py340](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L340-L340) and Prometheus metrics [xinference/api/restful_api.py335](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L335-L335)
 - **Authentication**: Advanced JWT-based auth or no-auth modes [xinference/api/restful_api.py190-207](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L190-L207)
 - **Event Collection**: Reporting errors and lifecycle events to the `EventCollectorActor` [xinference/api/restful_api.py305-319](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L305-L319)
 
 Sources: [xinference/api/restful_api.py160-349](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L160-L349) [xinference/constants.py105-110](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/constants.py#L105-L110)

 
## Endpoint Categories

 The API provides endpoints organized into functional categories. Detailed documentation for each category can be found in the child pages.

 
### Model Lifecycle and Management

 Managed via the `SupervisorActor`, these endpoints control the state of models in the cluster.

 
 - **Launch**: `POST /v1/models` triggers `launch_builtin_model` on the supervisor [xinference/api/restful_api.py494-510](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L494-L510)
 - **Terminate**: `DELETE /v1/models/{model_uid}` calls `terminate_model` [xinference/api/restful_api.py535-544](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L535-L544)
 - **Status**: `GET /v1/models/{model_uid}/progress` tracks asynchronous launches [xinference/api/restful_api.py557-564](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L557-L564)
 
 For details, see [Model Management Endpoints](https://deepwiki.com/xorbitsai/inference/5.1-model-management-endpoints).

 
### Inference Endpoints

 These endpoints provide OpenAI-compatible interfaces for various model types.

 
 - **LLM**: `/v1/chat/completions` and `/v1/completions` [xinference/api/restful_api.py584-630](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L584-L630)
 - **Embedding**: `/v1/embeddings` [xinference/api/restful_api.py644-656](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L644-L656)
 - **Rerank**: `/v1/rerank` [xinference/api/restful_api.py837-850](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L837-L850)
 - **Multimodal**: Image (`/v1/images/*`), Audio (`/v1/audio/*`), and Video (`/v1/video/*`) generation [xinference/api/restful_api.py669-835](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L669-L835)
 
 For details, see [Inference Endpoints](https://deepwiki.com/xorbitsai/inference/5.2-inference-endpoints).

 
### Custom Model Registration

 Allows users to register models not included in the builtin library.

 
 - **Register**: `POST /v1/model_registrations/{model_type}` [xinference/api/restful_api.py863-874](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L863-L874)
 - **Unregister**: `DELETE /v1/model_registrations/{model_type}/{model_name}` [xinference/api/restful_api.py876-887](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L876-L887)
 
 For details, see [Model Registration Endpoints](https://deepwiki.com/xorbitsai/inference/5.3-model-registration-endpoints).

 
## System Compatibility

 Xinference provides compatibility layers for several popular API standards to ensure a "drop-in" replacement experience.

 **Compatibility Layer Architecture**

 
```

```

 
 - **OpenAI**: Native support for the `/v1` namespace [xinference/api/restful_api.py584](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L584-L584)
 - **Anthropic**: Conditional support for `/anthropic/v1/messages` [xinference/api/restful_api.py596-628](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L596-L628)
 - **SD WebUI**: Compatibility with AUTOMATIC1111's `/sdapi/v1` endpoints [xinference/api/restful_api.py755-806](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L755-L806)
 
 For details, see [OpenAI and Anthropic Compatibility](https://deepwiki.com/xorbitsai/inference/5.4-openai-and-anthropic-compatibility).

 
## Security and Authentication

 Xinference supports two authentication modes:

 
 - **Advanced Auth**: Database-backed JWT authentication with user management and permissions [xinference/api/restful_api.py190-211](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L190-L211)
 - **No Auth**: Open access for local development [xinference/api/restful_api.py105-110](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L105-L110)
 
 Access is controlled via **Scopes** (e.g., `models:start`, `models:stop`) which are checked during request handling [xinference/api/restful_api.py496-501](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L496-L501)

 For details, see [Authentication and Authorization](https://deepwiki.com/xorbitsai/inference/5.5-authentication-and-authorization).

 
## Request Management

 
### Streaming

 Inference endpoints support streaming via Server-Sent Events (SSE) [xinference/api/restful_api.py1822-1900](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L1822-L1900) The server sends a periodic `ping` event to prevent connection timeouts during long generations [xinference/constants.py44](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/constants.py#L44-L44)

 
### Cancellation

 Requests can be aborted using a `request_id`. The `RESTfulAPI` uses the `CancelMixin` to propagate the abort signal to the underlying `ModelActor` [xinference/api/restful_api.py160](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L160-L160) [xinference/core/utils.py57](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/utils.py#L57-L57)

 Sources: [xinference/api/restful_api.py160-180](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L160-L180) [xinference/api/restful_api.py1822-1900](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/api/restful_api.py#L1822-L1900) [xinference/core/model.py204-215](https://github.com/xorbitsai/inference/blob/d97e0970/xinference/core/model.py#L204-L215)
