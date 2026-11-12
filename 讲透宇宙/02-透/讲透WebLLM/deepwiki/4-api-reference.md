> 来源: [https://deepwiki.com/mlc-ai/web-llm/4-api-reference](https://deepwiki.com/mlc-ai/web-llm/4-api-reference)
> DeepWiki mlc-ai/web-llm | Last indexed: 18 April 2025 (632d34

# API Reference

  Relevant source files 
 - [src/config.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/config.ts)
 - [src/conversation.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/conversation.ts)
 - [src/engine.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/engine.ts)
 - [src/error.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/error.ts)
 - [src/index.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/index.ts)
 - [src/llm_chat.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/llm_chat.ts)
 - [src/openai_api_protocols/chat_completion.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/openai_api_protocols/chat_completion.ts)
 - [src/openai_api_protocols/completion.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/openai_api_protocols/completion.ts)
 - [src/types.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/types.ts)
 - [src/web_worker.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/src/web_worker.ts)
 - [tests/openai_chat_completion.test.ts](https://github.com/mlc-ai/web-llm/blob/632d3472/tests/openai_chat_completion.test.ts)
 
  This document provides a comprehensive reference to the WebLLM API, which enables running large language models directly in web browsers. The API is designed to be compatible with the OpenAI API, making it easy for developers familiar with that interface to use WebLLM. For a general overview of WebLLM, see [Overview](https://deepwiki.com/mlc-ai/web-llm/1-overview).

 
## Core Engine Interfaces

 WebLLM provides several engine implementations that share a common interface defined by `MLCEngineInterface`.

 
```

```

 Sources: [src/types.ts62-242](https://github.com/mlc-ai/web-llm/blob/632d3472/src/types.ts#L62-L242) [src/engine.ts105-682](https://github.com/mlc-ai/web-llm/blob/632d3472/src/engine.ts#L105-L682) [src/web_worker.ts422-1010](https://github.com/mlc-ai/web-llm/blob/632d3472/src/web_worker.ts#L422-L1010)

 
### MLCEngine

 The main interface for loading and interacting with models. This engine runs in the main thread.

 
```

```

 
#### Constructor

 
```

```

 
 - `engineConfig`: Optional configuration for the engine
 
 
#### Key Methods

 
| Method | Description |
|---|---|
| reload(modelId, chatOpts?) | Loads one or more models |
| unload() | Unloads all models and releases resources |
| resetChat(keepStats?, modelId?) | Resets the chat state |
| interruptGenerate() | Interrupts ongoing text generation |
| getMessage(modelId?) | Gets the current generated message |
| runtimeStatsText(modelId?) | Gets runtime statistics |

 Sources: [src/engine.ts89-97](https://github.com/mlc-ai/web-llm/blob/632d3472/src/engine.ts#L89-L97) [src/engine.ts105-1021](https://github.com/mlc-ai/web-llm/blob/632d3472/src/engine.ts#L105-L1021)

 
### Web Worker Engine

 Allows running models in a background thread via Web Workers.

 
```

```

 Sources: [src/web_worker.ts401-410](https://github.com/mlc-ai/web-llm/blob/632d3472/src/web_worker.ts#L401-L410) [src/web_worker.ts422-1010](https://github.com/mlc-ai/web-llm/blob/632d3472/src/web_worker.ts#L422-L1010)

 
### Service Worker Engine

 Allows running models in a persistent background context via Service Workers.

 
```

```

 Sources: [src/index.ts41-44](https://github.com/mlc-ai/web-llm/blob/632d3472/src/index.ts#L41-L44)

 
## OpenAI-Compatible API

 WebLLM implements APIs compatible with OpenAI's interfaces for chat completions, text completions, and embeddings.

 
```

```

 Sources: [src/engine.ts107-113](https://github.com/mlc-ai/web-llm/blob/632d3472/src/engine.ts#L107-L113) [src/openai_api_protocols/chat_completion.ts48-77](https://github.com/mlc-ai/web-llm/blob/632d3472/src/openai_api_protocols/chat_completion.ts#L48-L77) [src/openai_api_protocols/completion.ts32-51](https://github.com/mlc-ai/web-llm/blob/632d3472/src/openai_api_protocols/completion.ts#L32-L51)

 
### Chat Completions API

 The Chat Completions API allows generating conversational responses:

 
```

```

 For streaming responses:

 
```

```

 
#### Chat Completion Request Parameters

 
| Parameter | Type | Description |
|---|---|---|
| messages | Array | List of messages in the conversation |
| stream | boolean | Whether to stream responses |
| temperature | number | Controls randomness (0.0-2.0) |
| max_tokens | number | Maximum tokens to generate |
| top_p | number | Nucleus sampling parameter (0.0-1.0) |
| frequency_penalty | number | Penalty for repeated tokens (-2.0-2.0) |
| presence_penalty | number | Penalty for new tokens (-2.0-2.0) |
| stop | string \| string[] | Sequences that stop generation |
| logit_bias | Record<string, number> | Modify token likelihoods |
| seed | number | For deterministic generation |
| response_format | ResponseFormat | Control output format (e.g. JSON) |
| tools | Array | Function calling tools |
| model | string | Model ID to use (only needed with multiple models) |

 Sources: [src/openai_api_protocols/chat_completion.ts89-279](https://github.com/mlc-ai/web-llm/blob/632d3472/src/openai_api_protocols/chat_completion.ts#L89-L279)

 
#### Chat Completion Response

 
```

```

 Sources: [src/openai_api_protocols/chat_completion.ts283-328](https://github.com/mlc-ai/web-llm/blob/632d3472/src/openai_api_protocols/chat_completion.ts#L283-L328)

 
### Text Completions API

 The Text Completions API allows completing a given text prompt:

 
```

```

 
#### Text Completion Request Parameters

 
| Parameter | Type | Description |
|---|---|---|
| prompt | string | The text to complete |
| stream | boolean | Whether to stream responses |
| temperature | number | Controls randomness (0.0-2.0) |
| max_tokens | number | Maximum tokens to generate |
| top_p | number | Nucleus sampling parameter (0.0-1.0) |
| frequency_penalty | number | Penalty for repeated tokens (-2.0-2.0) |
| presence_penalty | number | Penalty for new tokens (-2.0-2.0) |
| stop | string \| string[] | Sequences that stop generation |
| logit_bias | Record<string, number> | Modify token likelihoods |
| seed | number | For deterministic generation |
| echo | boolean | Echo back the prompt in response |
| model | string | Model ID to use (only needed with multiple models) |

 Sources: [src/openai_api_protocols/completion.ts62-200](https://github.com/mlc-ai/web-llm/blob/632d3472/src/openai_api_protocols/completion.ts#L62-L200)

 
#### Text Completion Response

 
```

```

 Sources: [src/openai_api_protocols/completion.ts253-294](https://github.com/mlc-ai/web-llm/blob/632d3472/src/openai_api_protocols/completion.ts#L253-L294)

 
### Embeddings API

 The Embeddings API allows generating vector representations of text:

 
```

```

 Note: To use this API, you must load a model with `ModelType.embedding` set in its model record.

 Sources: [src/error.ts496-505](https://github.com/mlc-ai/web-llm/blob/632d3472/src/error.ts#L496-L505)

 
## Configuration

 WebLLM provides several configuration interfaces for customizing behavior.

 
### MLCEngineConfig

 Used when creating an engine.

 
```

```

 Sources: [src/config.ts112-117](https://github.com/mlc-ai/web-llm/blob/632d3472/src/config.ts#L112-L117)

 
### AppConfig

 Configures the available models.

 
```

```

 Sources: [src/config.ts276-279](https://github.com/mlc-ai/web-llm/blob/632d3472/src/config.ts#L276-L279)

 
### ModelRecord

 Defines a model available for loading.

 
```

```

 Sources: [src/config.ts253-263](https://github.com/mlc-ai/web-llm/blob/632d3472/src/config.ts#L253-L263)

 
### ChatOptions and GenerationConfig

 `ChatOptions` is used when loading a model to override configuration values, while `GenerationConfig` is used when generating text to override generation parameters for a specific request.

 
```

```

 Sources: [src/config.ts99-100](https://github.com/mlc-ai/web-llm/blob/632d3472/src/config.ts#L99-L100) [src/config.ts126-144](https://github.com/mlc-ai/web-llm/blob/632d3472/src/config.ts#L126-L144)

 
## Integration with Web Workers and Service Workers

 WebLLM provides integration with Web Workers and Service Workers for running models in background threads.

 
```

```

 Sources: [src/web_worker.ts60-378](https://github.com/mlc-ai/web-llm/blob/632d3472/src/web_worker.ts#L60-L378) [src/web_worker.ts422-1010](https://github.com/mlc-ai/web-llm/blob/632d3472/src/web_worker.ts#L422-L1010)

 
### Web Worker Integration

 Web Worker integration allows running models in a background thread, which prevents UI freezing during heavy computation.

 
```

```

 Sources: [src/web_worker.ts61-377](https://github.com/mlc-ai/web-llm/blob/632d3472/src/web_worker.ts#L61-L377) [src/web_worker.ts422-1010](https://github.com/mlc-ai/web-llm/blob/632d3472/src/web_worker.ts#L422-L1010)

 
### Service Worker Integration

 Service Worker integration provides persistence across page loads and allows models to run in the background even when the page is closed.

 
```

```

 Sources: [src/index.ts41-44](https://github.com/mlc-ai/web-llm/blob/632d3472/src/index.ts#L41-L44)

 
## Advanced Features

 
### Logit Processors

 WebLLM allows for custom processing of token logits through the `LogitProcessor` interface.

 
```

```

 This can be used for custom token sampling strategies, enforcing constraints, or implementing specialized behaviors.

 Sources: [src/types.ts37-57](https://github.com/mlc-ai/web-llm/blob/632d3472/src/types.ts#L37-L57)

 
### Grammar and JSON Mode

 WebLLM supports structured output through JSON mode and grammar-based generation.

 
```

```

 Sources: [src/llm_chat.ts107-116](https://github.com/mlc-ai/web-llm/blob/632d3472/src/llm_chat.ts#L107-L116) [src/openai_api_protocols/chat_completion.ts228-242](https://github.com/mlc-ai/web-llm/blob/632d3472/src/openai_api_protocols/chat_completion.ts#L228-L242)

 
### Function Calling

 WebLLM supports function calling, which allows models to invoke functions defined by the application.

 
```

```

 Function calling is currently supported only by specific models, as defined in the `functionCallingModelIds` array.

 Sources: [src/config.ts295-301](https://github.com/mlc-ai/web-llm/blob/632d3472/src/config.ts#L295-L301) [src/openai_api_protocols/chat_completion.ts212-226](https://github.com/mlc-ai/web-llm/blob/632d3472/src/openai_api_protocols/chat_completion.ts#L212-L226)

 
## Error Handling

 WebLLM provides detailed error classes for various failure scenarios. Some common errors include:

 
| Error | Description |
|---|---|
| WebGPUNotAvailableError | WebGPU is not supported in the current environment |
| DeviceLostError | The WebGPU device was lost (often due to OOM) |
| ModelNotLoadedError | Attempted to use a model before loading it |
| ContextWindowSizeExceededError | The prompt exceeds the model's context window |
| ShaderF16SupportError | The model requires shader-f16 support |

 Sources: [src/error.ts1-812](https://github.com/mlc-ai/web-llm/blob/632d3472/src/error.ts#L1-L812)
