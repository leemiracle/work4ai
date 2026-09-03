# Serving APIs

> 来源: https://deepwiki.com/vllm-project/vllm/6-serving-apis 抓取日期: 2026-09-02
> 章节: 第 6 章 服务 API

---

Relevant source files

  * [docs/features/per_request_metrics.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/features/per_request_metrics.md?plain=1)
  * [docs/usage/security.md](https://github.com/vllm-project/vllm/blob/185cada3/docs/usage/security.md?plain=1)
  * [tests/engine/test_short_mm_context.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/engine/test_short_mm_context.py)
  * [tests/entrypoints/openai/chat_completion/test_batched_chat_completions.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/entrypoints/openai/chat_completion/test_batched_chat_completions.py)
  * [tests/entrypoints/openai/chat_completion/test_chat_error.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/entrypoints/openai/chat_completion/test_chat_error.py)
  * [tests/entrypoints/openai/chat_completion/test_logprob_token_ids.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/entrypoints/openai/chat_completion/test_logprob_token_ids.py)
  * [tests/entrypoints/openai/chat_completion/test_serving_chat.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/entrypoints/openai/chat_completion/test_serving_chat.py)
  * [tests/entrypoints/openai/chat_completion/test_thinking_token_budget_validation.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/entrypoints/openai/chat_completion/test_thinking_token_budget_validation.py)
  * [tests/entrypoints/openai/completion/test_completion_error.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/entrypoints/openai/completion/test_completion_error.py)
  * [tests/entrypoints/openai/completion/test_lora_resolvers.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/entrypoints/openai/completion/test_lora_resolvers.py)
  * [tests/entrypoints/openai/responses/test_sampling_params.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/entrypoints/openai/responses/test_sampling_params.py)
  * [tests/entrypoints/openai/test_cli_args.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/entrypoints/openai/test_cli_args.py)
  * [tests/entrypoints/openai/test_run_batch.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/entrypoints/openai/test_run_batch.py)
  * [tests/entrypoints/serve/utils/test_request_logger.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/entrypoints/serve/utils/test_request_logger.py)
  * [tests/tool_use/test_responses_request_validations.py](https://github.com/vllm-project/vllm/blob/185cada3/tests/tool_use/test_responses_request_validations.py)
  * [vllm/entrypoints/generate/api_router.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/generate/api_router.py)
  * [vllm/entrypoints/generate/base/serving.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/generate/base/serving.py)
  * [vllm/entrypoints/openai/api_server.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/api_server.py)
  * [vllm/entrypoints/openai/chat_completion/batch_serving.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/chat_completion/batch_serving.py)
  * [vllm/entrypoints/openai/chat_completion/protocol.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/chat_completion/protocol.py)
  * [vllm/entrypoints/openai/chat_completion/serving.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/chat_completion/serving.py)
  * [vllm/entrypoints/openai/cli_args.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/cli_args.py)
  * [vllm/entrypoints/openai/completion/protocol.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/completion/protocol.py)
  * [vllm/entrypoints/openai/completion/serving.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/completion/serving.py)
  * [vllm/entrypoints/openai/engine/protocol.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/engine/protocol.py)
  * [vllm/entrypoints/openai/responses/context.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/responses/context.py)
  * [vllm/entrypoints/openai/responses/protocol.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/responses/protocol.py)
  * [vllm/entrypoints/openai/responses/serving.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/responses/serving.py)
  * [vllm/entrypoints/openai/run_batch.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/run_batch.py)
  * [vllm/entrypoints/serve/utils/request_logger.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/serve/utils/request_logger.py)
  * [vllm/renderers/online_renderer.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/renderers/online_renderer.py)
  * [vllm/sampling_params.py](https://github.com/vllm-project/vllm/blob/185cada3/vllm/sampling_params.py)

## Purpose and Scope

This document describes vLLM's serving layer, which exposes OpenAI-compatible HTTP APIs for inference. It covers the FastAPI application setup, engine client integration, route registration, middleware, and application state initialization. The serving layer acts as the interface between external HTTP clients and vLLM's internal engine components, supporting text generation, multimodal inputs, and specialized tasks. [vllm/entrypoints/openai/api_server.py13-22](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/api_server.py#L13-L22)

For details on the FastAPI application structure and route registration, see [OpenAI-Compatible API Server](/vllm-project/vllm/6.1-openai-compatible-api-server). For chat template processing and message parsing, see [Chat Utilities and Message Processing](/vllm-project/vllm/6.2-chat-utilities-and-message-processing). For function calling and structured output, see [Tool Calling and Structured Output](/vllm-project/vllm/6.3-tool-calling-and-structured-output). For dynamic adapter management, see [LoRA Adapter Management](/vllm-project/vllm/6.4-lora-adapter-management). For the experimental Rust-based high-performance frontend, see [Rust Frontend (vllm-frontend-rs)](/vllm-project/vllm/6.5-rust-frontend-\(vllm-frontend-rs\)).

## System Architecture

The serving layer consists of a FastAPI application that manages the HTTP interface, coordinates with the engine client for inference, and provides OpenAI-compatible endpoints. The system supports multiple deployment modes including in-process engines and multi-process API servers. [vllm/entrypoints/openai/api_server.py5-22](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/api_server.py#L5-L22)

### High-Level Component Relationships

**Sources:** [vllm/entrypoints/openai/api_server.py5-22](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/api_server.py#L5-L22) [vllm/entrypoints/openai/chat_completion/serving.py116-139](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/chat_completion/serving.py#L116-L139) [vllm/entrypoints/openai/responses/serving.py150-169](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/responses/serving.py#L150-L169) [vllm/entrypoints/openai/chat_completion/protocol.py127-150](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/chat_completion/protocol.py#L127-L150)

### Serving Entity Mapping

This diagram bridges serving concepts to the specific code entities that implement them, including the protocol definitions used for request/call parsing.

**Sources:** [vllm/entrypoints/openai/api_server.py5-22](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/api_server.py#L5-L22) [vllm/entrypoints/openai/chat_completion/serving.py116-139](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/chat_completion/serving.py#L116-L139) [vllm/entrypoints/openai/responses/serving.py150-169](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/responses/serving.py#L150-L169) [vllm/entrypoints/openai/run_batch.py148-188](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/run_batch.py#L148-L188)

## Supported API Suites

vLLM provides several API interfaces registered conditionally based on the model's supported tasks. [vllm/entrypoints/openai/api_server.py13-14](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/api_server.py#L13-L14)

### Generative and Multimodal APIs

The primary interface for Large Language Models (LLMs) and Vision-Language Models (VLMs).

  * **Completions:** `/v1/completions` handled by `OpenAIServingCompletion`. [vllm/entrypoints/openai/completion/protocol.py46-110](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/completion/protocol.py#L46-L110)
  * **Chat Completions:** `/v1/chat/completions` handled by `OpenAIServingChat`. [vllm/entrypoints/openai/chat_completion/serving.py116-139](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/chat_completion/serving.py#L116-L139)
  * **Responses API:** `/v1/responses` handled by `OpenAIServingResponses` for multi-turn or tool-enabled interactions, including support for MCP (Model Context Protocol) tools and unified parsing via `ParserManager`. [vllm/entrypoints/openai/responses/serving.py150-195](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/responses/serving.py#L150-L195)

### Specialized APIs

  * **Batch API:** Supports offline processing of multiple requests from JSONL files, handling Chat, Embedding, and Audio tasks. [vllm/entrypoints/openai/run_batch.py148-188](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/run_batch.py#L148-L188)
  * **Audio APIs:** Transcription and translation endpoints for speech-to-text models like Whisper. [vllm/entrypoints/openai/run_batch.py56-65](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/run_batch.py#L56-L65)
  * **LoRA API:** Dynamic loading and unloading of adapters via `/v1/load_lora_adapter` and `/v1/unload_lora_adapter`. [vllm/entrypoints/openai/cli_args.py32-63](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/cli_args.py#L32-L63)

Feature| Code Implementation| Request Protocol  
---|---|---  
Chat| `OpenAIServingChat`| `ChatCompletionRequest`  
Completions| `OpenAIServingCompletion`| `CompletionRequest`  
Responses| `OpenAIServingResponses`| `ResponsesRequest`  
Batch| `run_batch` logic| `BatchRequestInput`  
  
**Sources:** [vllm/entrypoints/openai/chat_completion/serving.py116-139](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/chat_completion/serving.py#L116-L139) [vllm/entrypoints/openai/responses/serving.py150-195](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/responses/serving.py#L150-L195) [vllm/entrypoints/openai/run_batch.py148-188](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/run_batch.py#L148-L188) [vllm/entrypoints/openai/completion/protocol.py46-110](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/completion/protocol.py#L46-L110)

## Serving Utilities

### Chat Templates and Rendering

vLLM uses templates to convert structured chat messages into raw text prompts. This behavior is customized via `chat_template` or `chat_template_content_format` (supporting `string` or `openai` formats). [vllm/entrypoints/openai/chat_completion/serving.py146-153](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/chat_completion/serving.py#L146-L153) For details, see [Chat Utilities and Message Processing](/vllm-project/vllm/6.2-chat-utilities-and-message-processing).

### Tool Calling and Structured Output

vLLM supports automated tool choice and parsing of model-generated tool calls through the `ParserManager` which coordinates `ToolParser` and `ReasoningParser` instances. [vllm/entrypoints/openai/chat_completion/serving.py157-163](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/chat_completion/serving.py#L157-L163) This includes support for reasoning-specific token budgets defined in `ThinkingTokenBudget`. [vllm/sampling_params.py51-77](https://github.com/vllm-project/vllm/blob/185cada3/vllm/sampling_params.py#L51-L77) For details, see [Tool Calling and Structured Output](/vllm-project/vllm/6.3-tool-calling-and-structured-output).

### LoRA Management

The API server allows dynamic loading of LoRA adapters. Adapters can be specified at startup via `--lora-modules` or loaded at runtime. [vllm/entrypoints/openai/cli_args.py32-63](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/cli_args.py#L32-L63) For details, see [LoRA Adapter Management](/vllm-project/vllm/6.4-lora-adapter-management).

## Configuration and CLI

The server is configured via `AsyncEngineArgs` and `BaseFrontendArgs` arguments from the CLI. These handle network settings, performance tuning, and model-specific parameters. [vllm/entrypoints/openai/cli_args.py67-151](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/cli_args.py#L67-L151)

Argument Category| Class| Key Fields  
---|---|---  
Engine Config| `AsyncEngineArgs`| `model`, `tensor_parallel_size`, `dtype`  
Frontend Config| `BaseFrontendArgs`| `chat_template`, `tool_call_parser`, `api_key`  
Request Handling| `SamplingParams`| `n`, `temperature`, `top_p`, `max_tokens`  
  
**Sources:** [vllm/entrypoints/openai/cli_args.py67-151](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/cli_args.py#L67-L151) [vllm/sampling_params.py198-205](https://github.com/vllm-project/vllm/blob/185cada3/vllm/sampling_params.py#L198-L205) [vllm/entrypoints/openai/engine/protocol.py124-130](https://github.com/vllm-project/vllm/blob/185cada3/vllm/entrypoints/openai/engine/protocol.py#L124-L130)
