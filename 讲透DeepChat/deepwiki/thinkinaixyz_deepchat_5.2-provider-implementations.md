> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/5.2-provider-implementations](https://deepwiki.com/thinkinaixyz/deepchat/5.2-provider-implementations)（Wayback 快照 2026-03-06）
> DeepWiki deepchat/5.2-provider-implementations

# Provider Implementations

  Relevant source files 
 - [src/main/presenter/llmProviderPresenter/baseProvider.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/baseProvider.ts)
 - [src/main/presenter/llmProviderPresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/index.ts)
 - [src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts)
 - [src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts)
 - [src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts)
 - [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts)
 - [src/main/presenter/llmProviderPresenter/providers/openAIResponsesProvider.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAIResponsesProvider.ts)
 - [test/main/presenter/llmProviderPresenter/openAIResponsesProvider.test.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/test/main/presenter/llmProviderPresenter/openAIResponsesProvider.test.ts)
 
  This document details the concrete provider implementations that extend `BaseLLMProvider` to integrate specific LLM services. DeepChat supports 30+ providers through a unified interface, with each provider implementing authentication, message formatting, and service-specific features. For the abstract base class and common patterns, see [Provider Architecture and Base Classes](https://deepwiki.com/thinkinaixyz/deepchat/5.1-provider-architecture-and-base-classes). For streaming and tool execution, see [Streaming and Agent Loop](https://deepwiki.com/thinkinaixyz/deepchat/5.3-streaming-and-agent-loop).

 
---

 
## Provider Hierarchy and Implementation Pattern

 All provider implementations follow a consistent inheritance pattern from `BaseLLMProvider`, implementing required abstract methods while adding provider-specific logic.

 
### Provider Class Hierarchy

 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/baseProvider.ts31-739](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/baseProvider.ts#L31-L739) [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts67-80](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L67-L80) [src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts81-179](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts#L81-L179) [src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts53-64](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts#L53-L64)

 
---

 
## Authentication Patterns

 Different providers implement various authentication mechanisms, from simple API keys to OAuth2 flows and cloud-specific credential systems.

 
### Authentication Method Matrix

 
| Provider | Auth Method | Implementation Details | Key Code |
|---|---|---|---|
| OpenAI | API Key | Bearer token in Authorization header | apiKey: this.provider.apiKey |
| Azure OpenAI | API Key + Version | Custom headers + API version | AzureOpenAI({ apiVersion }) |
| Anthropic | API Key or OAuth2 | Dual-mode with fallback | authMode === 'oauth' check |
| Gemini | API Key | Passed to GoogleGenAI constructor | GoogleGenAI({ apiKey }) |
| Ollama | Optional API Key | Bearer token if provided | headers: { Authorization } |
| AWS Bedrock | IAM Credentials | Via AWS SDK (not shown) | - |
| Vertex AI | Service Account | Via Google Cloud SDK | - |

 
### Anthropic Dual Authentication Mode

 Anthropic is unique in supporting both API key and OAuth2 authentication with automatic fallback:

 
```

```

 OAuth mode uses direct HTTP requests with custom headers:

 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts96-179](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts#L96-L179) [src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts251-289](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts#L251-L289)

 
---

 
## OpenAI-Compatible Provider

 `OpenAICompatibleProvider` is the most versatile provider, serving as the base for OpenAI, Azure OpenAI, and many third-party services that implement OpenAI's API specification.

 
### Provider Initialization and Client Creation

 
```

```

 **Third-Party Service Header Stripping:** To avoid 403 errors with third-party services, `createCleanFetch()` removes OpenAI SDK-specific headers (`X-Stainless-*`, `user-agent`, `openai-*`) while preserving essential headers (authorization, content-type, accept).

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts104-174](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L104-L174) [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts179-181](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L179-L181) [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts187-233](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L187-L233)

 
### Message Format Translation

 The provider handles complex message format translation, supporting both native function calling and mock function calling modes:

 
```

```

 **Merged Tool Response Splitting:** When multiple tool calls are made but responses are merged into a single message, `splitMergedToolContent()` attempts to recover individual payloads using strategies:

 
 - JSON array parsing
 - Delimiter detection (---, ===, ***)
 - Blank line separation
 - Header repeat detection
 
 **Sources:** [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts273-559](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L273-L559) [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts570-685](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L570-L685)

 
### Image Generation Models

 OpenAI-compatible providers support image generation models (DALL-E, GPT-Image-1):

 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts53-62](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L53-L62) [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts775-977](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L775-L977)

 
### Reasoning Model Handling

 OpenAI reasoning models (o1, o3, o4, gpt-5) have special parameter handling:

 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts35-50](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L35-L50) [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts1023-1034](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L1023-L1034) [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts1048-1061](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L1048-L1061)

 
---

 
## Anthropic Provider (Claude)

 The Anthropic provider implements Claude's unique message format and content block structure, with special handling for tool calls and multi-turn conversations.

 
### Message Grouping and Role Alternation

 Claude requires strict role alternation (user-assistant-user-...) and uses a sophisticated grouping algorithm:

 
```

```

 **Key Insight:** Tool use blocks (`functionCall`) and tool result blocks (`functionResponse`) must be in the same message group with alternating user roles. The two-pass algorithm first builds groups, then merges tool results into the corresponding tool use groups.

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts326-574](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts#L326-L574)

 
### OAuth-Specific Request Handling

 When in OAuth mode, Anthropic bypasses the SDK and uses direct HTTP requests:

 
```

```

 **Beta Features:** OAuth requests include extensive beta headers for accessing latest features: `oauth-2025-04-20`, `claude-code-20250219`, `interleaved-thinking-2025-05-14`, `fine-grained-tool-streaming-2025-05-14`.

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts251-289](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts#L251-L289) [src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts291-324](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts#L291-L324)

 
### Extended Thinking and Prompt Caching

 Claude supports extended thinking budgets and prompt caching for efficient context reuse:

 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts666-698](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts#L666-L698)

 
---

 
## Gemini Provider (Google)

 The Gemini provider integrates Google's Generative AI API with support for thinking budgets, safety settings, and native search.

 
### Safety Settings Configuration

 Gemini implements granular safety settings mapped from user configuration:

 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts34-51](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts#L34-L51) [src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts278-308](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts#L278-L308)

 
### Thinking Budget and Response Modalities

 Gemini 2.5 models support thinking budgets and can output both text and images:

 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts311-356](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts#L311-L356)

 
### Message Format and Tool Integration

 Gemini uses a unique format with `Content` objects and separate system instructions:

 
```

```

 **Tool Call Pairing:** Unlike OpenAI where tool responses reference call IDs, Gemini pairs tool calls and responses by name and order. The formatter matches `tool_call_id` from messages to insert corresponding `functionResponse` parts.

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts359-505](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts#L359-L505) [src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts376-425](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts#L376-L425)

 
### Native Search Integration

 Gemini supports built-in Google Search as a first-class tool:

 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts822-824](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts#L822-L824)

 
---

 
## Ollama Provider (Local Models)

 The Ollama provider manages locally-hosted models with unique features for model lifecycle management and info retrieval.

 
### Ollama-Specific Model Management

 
```

```

 **Model Info Enrichment:** Ollama's `list()` API doesn't return full model capabilities, so `attachModelInfo()` makes individual `show()` calls to retrieve context length, embedding dimensions, and capabilities (chat, embedding, etc.).

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts361-378](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts#L361-L378) [src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts325-358](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts#L325-L358) [src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts428-473](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts#L428-L473)

 
### Image Content Handling

 Ollama expects base64 image data without the data URI prefix:

 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts97-139](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts#L97-L139)

 
### Native Thinking Support

 Recent Ollama models expose thinking content natively:

 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts206-233](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts#L206-L233)

 
---

 
## Specialized Provider Features

 
### DashScope Provider (Alibaba Cloud)

 Extends `OpenAICompatibleProvider` with custom `enable_thinking` and `enable_search` parameters:

 
```

```

 **Parameter Injection:** DashScope doesn't use standard OpenAI reasoning parameters. The provider wraps the SDK's `create` method to inject `enable_thinking` and `enable_search` before making the actual API call.

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/dashscopeProvider.ts30-98](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/dashscopeProvider.ts#L30-L98)

 
### Zhipu Provider (GLM Models)

 Fetches models from Provider DB with modality-based capability detection:

 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/zhipuProvider.ts19-48](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/zhipuProvider.ts#L19-L48)

 
### OpenAI Responses Provider

 Implements OpenAI's new Responses API (preview) with different message format:

 
```

```

 **Key Differences:**

 
 - Tool calls are separate input objects, not nested in assistant messages
 - Text content type differs by role: `input_text` for user/system, `output_text` for assistant
 - Images use `input_image` with `image_url` property
 
 **Sources:** [src/main/presenter/llmProviderPresenter/providers/openAIResponsesProvider.ts152-213](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAIResponsesProvider.ts#L152-L213)

 
---

 
## Provider Feature Matrix

 
| Provider | Tool Calls | Streaming | Vision | Reasoning | Search | Image Gen | Embedding |
|---|---|---|---|---|---|---|---|
| OpenAI | Native | ✓ | ✓ | ✓ (o1/o3) | - | ✓ (DALL-E) | ✓ |
| Anthropic | Native | ✓ | ✓ | ✓ (Extended) | - | - | - |
| Gemini | Native | ✓ | ✓ | ✓ (Thinking) | ✓ (Native) | ✓ (Imagen) | - |
| Ollama | Native/Mock | ✓ | ✓ | ✓ (Some) | - | - | ✓ |
| DashScope | Native/Mock | ✓ | ✓ | ✓ (Custom) | ✓ (Custom) | - | ✓ |
| Zhipu | Native/Mock | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| Azure OpenAI | Native | ✓ | ✓ | ✓ | - | ✓ | ✓ |

 **Native vs Mock Tool Calls:**

 
 - **Native:** Provider API natively supports function calling (passes tools in API request, returns structured tool calls)
 - **Mock:** DeepChat wraps tools in prompt tags and parses function calls from text response (see [Function Call Tag Parsing](https://deepwiki.com/thinkinaixyz/deepchat/5.6-function-call-tag-parsing))
 
 **Sources:** [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts67-80](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L67-L80) [src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts81-95](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts#L81-L95) [src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts53-64](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts#L53-L64) [src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts40-55](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts#L40-L55)

 
---

 
## Provider Selection and Instantiation

 The `ProviderInstanceManager` (referenced in [src/main/presenter/llmProviderPresenter/index.ts25](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/index.ts#L25-L25)) creates provider instances based on provider ID:

 
```

```

 **Inheritance Selection:** Provider instantiation determines whether to use:

 
 - Base `OpenAICompatibleProvider` for standard OpenAI API compatibility
 - Specialized subclasses (`DashscopeProvider`, `ZhipuProvider`) for custom parameters
 - Completely independent implementations (`AnthropicProvider`, `GeminiProvider`, `OllamaProvider`) for non-OpenAI APIs
 
 **Sources:** [src/main/presenter/llmProviderPresenter/index.ts140-146](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/index.ts#L140-L146)
