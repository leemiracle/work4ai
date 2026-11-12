<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-python · page 4 API Resources and Endpoints · fetched 2026-10-26 -->

# API Resources and Endpoints

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.stats.yml](.stats.yml)
- [api.md](api.md)
- [src/openai/resources/chat/completions/completions.py](src/openai/resources/chat/completions/completions.py)
- [src/openai/resources/responses/responses.py](src/openai/resources/responses/responses.py)
- [src/openai/types/__init__.py](src/openai/types/__init__.py)
- [src/openai/types/chat/completion_create_params.py](src/openai/types/chat/completion_create_params.py)
- [src/openai/types/responses/response.py](src/openai/types/responses/response.py)
- [src/openai/types/responses/response_compact_params.py](src/openai/types/responses/response_compact_params.py)
- [src/openai/types/responses/response_create_params.py](src/openai/types/responses/response_create_params.py)
- [src/openai/types/responses/responses_client_event.py](src/openai/types/responses/responses_client_event.py)
- [src/openai/types/responses/responses_client_event_param.py](src/openai/types/responses/responses_client_event_param.py)
- [src/openai/types/shared/__init__.py](src/openai/types/shared/__init__.py)
- [src/openai/types/shared_params/__init__.py](src/openai/types/shared_params/__init__.py)
- [tests/api_resources/chat/test_completions.py](tests/api_resources/chat/test_completions.py)
- [tests/api_resources/test_responses.py](tests/api_resources/test_responses.py)

</details>



This document provides a comprehensive reference for the API resources organized into namespaces within the OpenAI Python SDK. Each resource is accessible as a property on the `OpenAI` or `AsyncOpenAI` client and provides methods for interacting with specific OpenAI API capabilities.

For details about the client instantiation and HTTP infrastructure, see [Core Client Classes](#3). For information about type definitions and validation, see [Data Types and Type System](#5).

**Sources:** [.stats.yml:1-4](), [src/openai/types/__init__.py:1-125]()

---

## Resource Organization

The SDK organizes API endpoints into a hierarchical resource structure accessed via the client object. All resources are defined in `src/openai/resources/` with both synchronous and asynchronous implementations. The `_module_client.py` file exposes these resources through a proxy pattern for convenience.

**Sources:** [src/openai/_module_client.py:36-189](), [src/openai/resources/__init__.py:1-256]()

### Natural Language Space to Code Entity Space

The following diagram bridges the conceptual API resources to their specific class implementations within the SDK.

```mermaid
graph TD
    [OpenAI_Client] --> [Responses_Resource]
    [OpenAI_Client] --> [Chat_Resource]
    [OpenAI_Client] --> [Images_Resource]
    [OpenAI_Client] --> [Audio_Resource]
    [OpenAI_Client] --> [Embeddings_Resource]
    [OpenAI_Client] --> [Files_Resource]
    [OpenAI_Client] --> [VectorStores_Resource]
    [OpenAI_Client] --> [FineTuning_Resource]
    [OpenAI_Client] --> [Batches_Resource]
    [OpenAI_Client] --> [Uploads_Resource]
    [OpenAI_Client] --> [Models_Resource]
    [OpenAI_Client] --> [Moderations_Resource]
    [OpenAI_Client] --> [Beta_Resource]
    [OpenAI_Client] --> [Realtime_Resource]
    [OpenAI_Client] --> [Conversations_Resource]
    [OpenAI_Client] --> [Completions_Resource]
    [OpenAI_Client] --> [Evals_Resource]
    [OpenAI_Client] --> [Containers_Resource]
    [OpenAI_Client] --> [Videos_Resource]
    [OpenAI_Client] --> [Skills_Resource]
    [OpenAI_Client] --> [Admin_Resource]
    
    [Chat_Resource] --> [ChatCompletions_Resource]
    
    [Beta_Resource] --> [Assistants_Resource]
    [Beta_Resource] --> [Threads_Resource]
    
    [Admin_Resource] --> [AdminOrg_Resource]
    
    [Realtime_Resource] --> [RealtimeCalls_Resource]

    subgraph "Code Entities"
    [Responses_Resource]:::code
    [ChatCompletions_Resource]:::code
    [Assistants_Resource]:::code
    end

    classDef code font-family:monospace
```

**Sources:** [src/openai/_module_client.py:168-189](), [src/openai/resources/admin/admin.py:19-22](), [api.md:1-1168]()

---

## Primary Interaction APIs

### Responses API
The Responses API is the modern interface for model interactions, supporting text, images, audio, and files. It provides built-in conversation state management and background processing. The resource supports sub-resources for `input_items` and `input_tokens`.

- **Methods:** `create`, `retrieve`, `delete`, `cancel`, `compact`.
- **Sub-resources:** `input_items`, `input_tokens`.
- **For details, see [Responses API](#4.2)**

**Sources:** [src/openai/resources/responses/responses.py:104-111](), [src/openai/types/responses/response_create_params.py:43-149](), [api.md:26-26]()

### Chat Completions API
The traditional message-based interface for conversational AI. It supports structured outputs through Pydantic model parsing and tool calling. The SDK provides a `parse` method for automatic deserialization into Pydantic models.

- **Methods:** `create`, `retrieve`, `update`, `list`, `delete`, `parse`.
- **Sub-resource:** `messages`.
- **For details, see [Chat Completions API](#4.1)**

**Sources:** [src/openai/resources/chat/completions/completions.py:60-136](), [src/openai/types/chat/completion_create_params.py:42-183](), [api.md:94-104]()

---

## Agentic and Stateful APIs

### Assistants API (Beta)
Designed for building persistent, stateful AI assistants. It manages `Threads` for conversation history and `Runs` for executing an assistant's instructions using tools like `code_interpreter` and `file_search`.

- **Components:** `Assistants`, `Threads`, `Messages`, `Runs`, `Run Steps`.
- **For details, see [Assistants API (Beta)](#4.3)**

**Sources:** [api.md:532-684](), [src/openai/resources/beta/beta.py:1-20]()

### Realtime API (Beta)
Enables low-latency, multi-modal (voice/text) interactions over WebSockets. It includes a `calls` resource for phone and voice integration.

- **Components:** `Session`, `Events`, `Input Audio Buffer`, `Calls`.
- **For details, see [Realtime API (Beta)](#4.9)**

**Sources:** [api.md:865-1001](), [src/openai/_module_client.py:114-117]()

---

## Data and Training APIs

### Fine-Tuning API
Allows training custom models on specific datasets. Supports job management, checkpointing, and integration with third-party tools.

- **Methods:** `create`, `retrieve`, `list`, `cancel`, `checkpoints`.
- **For details, see [Fine-Tuning API](#4.4)**

**Sources:** [api.md:246-333](), [src/openai/_module_client.py:150-154]()

### Embeddings and Vector Stores
Provides tools for semantic search and RAG (Retrieval-Augmented Generation). Embeddings convert text to vectors, while Vector Stores manage the storage and retrieval of these vectors.

- **Resources:** `embeddings`, `vector_stores`.
- **For details, see [Embeddings and Vector Stores](#4.5)**

**Sources:** [api.md:105-116](), [api.md:351-417](), [src/openai/types/embedding.py:1-10]()

### File Management and Uploads
Handles file storage for training, assistant knowledge bases, and batch processing. Supports multi-part uploads for large files via the `uploads` resource.

- **Resources:** `files`, `uploads`.
- **For details, see [File Management and Uploads](#4.6)**

**Sources:** [api.md:117-134](), [api.md:700-725](), [src/openai/resources/files.py:31-118]()

---

## Specialized Content APIs

### Audio, Images, and Video APIs
Dedicated endpoints for non-text modalities.
- **Audio:** Transcription, translation, and speech synthesis.
- **Images:** Generation (`dall-e`), editing, and variations.
- **Video:** Video generation, remixing, and extending.
- **For details, see [Audio, Images, and Video APIs](#4.7)**

**Sources:** [api.md:135-212](), [src/openai/types/__init__.py:6-9](), [src/openai/types/video_create_params.py:1-15]()

---

## Additional API Resources

The SDK also exposes resources for model management, content moderation, bulk processing, and administrative tasks.

| Resource | Purpose |
| :--- | :--- |
| `models` | List and retrieve metadata for available models. |
| `moderations` | Check if content complies with OpenAI usage policies. |
| `batches` | Execute bulk requests asynchronously at lower cost. |
| `evals` | Programmatic evaluation of model performance. |
| `containers` | Manage code execution environments. |
| `skills` | Manage specific model capabilities. |
| `admin` | Organization management (users, projects, usage, invites). |

- **For details, see [Additional API Resources](#4.8)**

**Sources:** [api.md:213-245](), [api.md:685-699](), [src/openai/resources/admin/organization/organization.py:99-144]()

---

## Resource Implementation Mapping

The following diagram shows how high-level method calls on the client map to the underlying resource classes and request parameters.

```mermaid
graph LR
    subgraph "Client Interface"
        [OpenAI_Client]
    end

    subgraph "Resource Classes"
        [Completions_Resource]
        [Responses_Resource]
        [Files_Resource]
        [Admin_Resource]
    end

    subgraph "Parameter Types"
        [CompletionCreateParams]
        [ResponseCreateParams]
        [FileCreateParams]
        [UserListParams]
    end

    [OpenAI_Client] -- ".chat.completions" --> [Completions_Resource]
    [OpenAI_Client] -- ".responses" --> [Responses_Resource]
    [OpenAI_Client] -- ".files" --> [Files_Resource]
    [OpenAI_Client] -- ".admin.organization" --> [Admin_Resource]

    [Completions_Resource] -- "create()" --> [CompletionCreateParams]
    [Responses_Resource] -- "create()" --> [ResponseCreateParams]
    [Files_Resource] -- "create()" --> [FileCreateParams]
    [Admin_Resource] -- "users.list()" --> [UserListParams]
```

**Sources:** [src/openai/resources/chat/completions/completions.py:60-91](), [src/openai/resources/responses/responses.py:133-166](), [src/openai/resources/admin/organization/organization.py:118-119](), [api.md:94-94]()

---

