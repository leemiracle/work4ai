<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/hub-docs · page 4 Inference and Model Execution · fetched 2026-10-26 -->

# Inference and Model Execution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/inference-providers/_redirects.yml](docs/inference-providers/_redirects.yml)
- [docs/inference-providers/_toctree.yml](docs/inference-providers/_toctree.yml)
- [docs/inference-providers/guides/evaluation-inspect-ai.md](docs/inference-providers/guides/evaluation-inspect-ai.md)
- [docs/inference-providers/guides/first-api-call.md](docs/inference-providers/guides/first-api-call.md)
- [docs/inference-providers/guides/function-calling.md](docs/inference-providers/guides/function-calling.md)
- [docs/inference-providers/hub-api.md](docs/inference-providers/hub-api.md)
- [docs/inference-providers/index.md](docs/inference-providers/index.md)
- [docs/inference-providers/integrations/vscode.md](docs/inference-providers/integrations/vscode.md)
- [docs/inference-providers/providers/hf-inference.md](docs/inference-providers/providers/hf-inference.md)
- [docs/inference-providers/providers/zai-org.md](docs/inference-providers/providers/zai-org.md)
- [docs/inference-providers/tasks/chat-completion.md](docs/inference-providers/tasks/chat-completion.md)
- [docs/inference-providers/tasks/image-text-to-text.md](docs/inference-providers/tasks/image-text-to-text.md)
- [scripts/inference-providers/package.json](scripts/inference-providers/package.json)
- [scripts/inference-providers/pnpm-lock.yaml](scripts/inference-providers/pnpm-lock.yaml)
- [scripts/inference-providers/scripts/generate.ts](scripts/inference-providers/scripts/generate.ts)

</details>



This document covers the Hugging Face Hub's inference and model execution ecosystem, including the Inference API, third-party inference providers, interactive widgets, and task-based pipeline architecture. It explains how models hosted on the Hub can be executed through various interfaces and services.

For information about uploading and managing models themselves, see [Models](#2.1). For details about programmatic Hub access, see [Hub API and Programmatic Access](#3). For enterprise inference features, see [Security and Enterprise Features](#6).

## Overview

The Hub provides multiple pathways for executing machine learning models:

- **Interactive Widgets**: Browser-based interfaces for immediate model testing directly on model pages.
- **Inference API**: Serverless REST API endpoints for programmatic model execution.
- **Inference Providers**: A network of third-party providers (e.g., Fal AI, Groq, Together) integrated into the Hub UI and SDKs.
- **Task-based Pipeline System**: Standardized interfaces organized by ML task types (e.g., `text-generation`, `text-to-image`).

All inference capabilities are organized around **tasks** (also called pipeline types), which define the input/output schema and API behavior.

## Inference Architecture

The Hub's inference system is built around a task-centric architecture where models are categorized by their ML task type, and each task has standardized APIs across different execution environments.

### System Architecture Diagram

Title: Inference and Execution Flow
```mermaid
graph TB
    subgraph "Model Repository"
        [ModelRepo] --> [TaskMetadata]
        [TaskMetadata] --> [PipelineTag]
    end
    
    subgraph "Task System (@huggingface/tasks)"
        [PipelineTag] --> [TaskSpec]
        [TaskSpec] --> [InputSchema]
        [TaskSpec] --> [OutputSchema]
    end
    
    subgraph "Execution Interfaces"
        [InputSchema] --> [InferenceWidget]
        [InputSchema] --> [InferenceAPI]
        [InputSchema] --> [ProviderRouter]
    end
    
    subgraph "Client Libraries"
        [InferenceAPI] --> [hf_hub_python]
        [ProviderRouter] --> [hf_js_inference]
        [InferenceAPI] --> [OpenAI_SDK]
    end
    
    [hf_hub_python] --> [InferenceClient_class]
    [hf_js_inference] --> [InferenceClient_js]
```
Sources: [docs/inference-providers/tasks/chat-completion.md:1-13](), [scripts/inference-providers/package.json:16-27](), [docs/inference-providers/index.md:8-12]()

## Task and Pipeline System

Tasks define the "shape" of model APIs and determine which inference interfaces are available. Each task corresponds to a specific ML capability with standardized input/output formats defined in `@huggingface/tasks`.

### Task-to-Code Entity Mapping

Title: Task to Specification Mapping
```mermaid
graph LR
    subgraph "Task Types"
        [chat-completion]
        [text-to-image]
        [feature-extraction]
        [image-text-to-text]
    end
    
    subgraph "Code Specifications (huggingface.js)"
        [chat-completion] --> [chat_spec_json]
        [text-to-image] --> [t2i_spec_json]
        [feature-extraction] --> [fe_spec_json]
        [image-text-to-text] --> [vlm_spec_json]
    end
    
    subgraph "Router Endpoints"
        [chat_spec_json] --> [router_v1_chat]
        [t2i_spec_json] --> [router_v1_models]
        [fe_spec_json] --> [api_models_task]
    end
    
    [router_v1_chat] -- "https://router.huggingface.co/v1/chat/completions" --> [Execution]
```
Sources: [docs/inference-providers/tasks/chat-completion.md:5-7](), [docs/inference-providers/tasks/image-text-to-text.md:5-7](), [docs/inference-providers/hub-api.md:141-146]()

### Task Categories
The Hub supports over 20 pipeline types, ranging from NLP to Computer Vision. For a full list of supported tasks, see [Tasks and Pipeline Types](#4.3).

Sources: [scripts/inference-providers/scripts/generate.ts:8-29](), [docs/inference-providers/_toctree.yml:60-105]()

## Inference Providers

Inference Providers allow developers to run models on specialized third-party infrastructure through a unified Hugging Face interface.

- **Unified API**: Access providers like Cerebras, Groq, and Novita using a single Hugging Face token.
- **Automatic Routing**: The `provider="auto"` parameter in SDKs automatically selects available providers based on user preferences.
- **OpenAI Compatibility**: The Hub Router provides an OpenAI-compatible `/v1/chat/completions` endpoint for many models.

For a complete list of partners and setup instructions, see [Inference Providers](#4.2).

Sources: [docs/inference-providers/index.md:8-12](), [docs/inference-providers/guides/first-api-call.md:138-156](), [docs/inference-providers/hub-api.md:141-146]()

## Interactive Widgets and Playground

Interactive widgets provide browser-based interfaces for immediate model testing.

- **Model Page Widgets**: Automatically generated based on the model's `pipeline_tag`.
- **Inference Playground**: A dedicated UI for Chat Completion models that allows side-by-side model comparison, system prompt testing, and real-time parameter adjustment.
- **Code Snippet Generator**: The widget provides ready-to-use `curl`, `Python`, and `JavaScript` snippets for the selected model and provider.

For details on configuring these tools, see [Model Inference and Widgets](#4.1).

Sources: [docs/inference-providers/tasks/chat-completion.md:43-56](), [docs/inference-providers/guides/first-api-call.md:34-46](), [docs/inference-providers/guides/first-api-call.md:51-55]()

## API Specifications and Protocols

Each task defines precise API contracts for request/response formats.

- **Authentication**: All endpoints require a Bearer token with `inference.serverless.write` permissions.
- **Streaming**: Supported for tasks like `text-generation` and `chat-completion` using Server-Sent Events (SSE).
- **Function Calling**: Enabled for supported LLMs to interact with external tools via structured JSON schemas.

### Request Headers Example
| Header | Description |
| :--- | :--- |
| **Authorization** | `Bearer hf_****` (Personal access token) |

Sources: [docs/inference-providers/tasks/chat-completion.md:88-93](), [docs/inference-providers/guides/function-calling.md:1-10](), [docs/inference-providers/hub-api.md:73-80]()

## Child Pages

- [Model Inference and Widgets](#4.1) — Interactive widgets, Inference API, and Playground configuration.
- [Inference Providers](#4.2) — Third-party provider details (Groq, Fal, Together, etc.) and registration.
- [Tasks and Pipeline Types](#4.3) — Technical specifications for chat, vision, and audio tasks.
- [Inference Provider Integrations](#4.4) — Using providers with VS Code, Claude Code, and other frameworks.

---

