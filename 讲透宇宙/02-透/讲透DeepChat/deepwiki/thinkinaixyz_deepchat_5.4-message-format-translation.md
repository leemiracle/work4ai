> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/5.4-message-format-translation](https://deepwiki.com/thinkinaixyz/deepchat/5.4-message-format-translation)（Wayback 快照 2026-03-06）
> DeepWiki deepchat/5.4-message-format-translation

# Message Format Translation

  Relevant source files 
 - [src/main/presenter/llmProviderPresenter/baseProvider.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/baseProvider.ts)
 - [src/main/presenter/llmProviderPresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/index.ts)
 - [src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts)
 - [src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts)
 - [src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts)
 - [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts)
 - [src/main/presenter/llmProviderPresenter/providers/openAIResponsesProvider.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAIResponsesProvider.ts)
 - [test/main/presenter/llmProviderPresenter/openAIResponsesProvider.test.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/test/main/presenter/llmProviderPresenter/openAIResponsesProvider.test.ts)
 
  
## Purpose and Scope

 This page documents how DeepChat translates its internal unified message format (`ChatMessage`) into provider-specific API formats for OpenAI, Gemini, Anthropic, Ollama, and other LLM providers. This translation layer enables DeepChat to maintain a consistent internal representation while supporting the diverse message schemas required by different LLM APIs.

 For information about how these formatted messages are used during streaming responses, see [Streaming and Agent Loop](https://deepwiki.com/thinkinaixyz/deepchat/5.3-streaming-and-agent-loop). For details about specific provider implementations, see [Provider Implementations](https://deepwiki.com/thinkinaixyz/deepchat/5.2-provider-implementations).

 
## Message Translation Architecture

 DeepChat maintains a unified internal message format (`ChatMessage`) that abstracts away provider-specific details. Each provider implementation includes a `formatMessages` method that translates this internal format to the provider's API schema.

 
### Message Translation Flow

 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/baseProvider.ts31-739](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/baseProvider.ts#L31-L739) [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts67-1595](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L67-L1595)

 
## Internal ChatMessage Format

 DeepChat uses a unified `ChatMessage` type that includes the following roles and content types:

 
| Role | Description | Content Types |
|---|---|---|
| system | System-level instructions | String or multimodal array |
| user | User messages | String or multimodal array (text + images) |
| assistant | LLM responses | String, multimodal array, or with tool_calls |
| tool | Tool execution results | String or JSON with tool_call_id |

 
### Message Structure

 
```

```

 **Sources:** [src/shared/presenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/shared/presenter/index.ts) [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts273-559](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L273-L559)

 
## OpenAI Compatible Format Translation

 The `OpenAICompatibleProvider` serves as the base implementation for most providers, supporting both native function calling and mock (tag-based) function calling.

 
### Format Translation Method

 The `formatMessages` method at [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts273-559](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L273-L559) performs the following translations:

 
| Internal Format | OpenAI Format (Native FC) | OpenAI Format (Mock FC) |
|---|---|---|
| System messages | { role: 'system', content: string } | Same |
| User messages | { role: 'user', content: string \| ContentPart[] } | Same |
| Assistant with tool_calls | { role: 'assistant', tool_calls: [...] } | { role: 'assistant', content: string } + mock user messages |
| Tool responses | { role: 'tool', content: string, tool_call_id: string } | { role: 'user', content: '<function_call>...' } |

 
### Tool Call Format Translation

 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts273-559](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L273-L559)

 
### Multimodal Content Handling

 For user messages, OpenAI Compatible format preserves the array structure:

 
```

```

 For assistant and system messages, multimodal content is flattened to strings at [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts386-402](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L386-L402)

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts404-413](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L404-L413)

 
### Tool Response Splitting

 When multiple tool calls are merged into a single tool response, the provider attempts to split them back into individual responses using heuristics at [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts570-685](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L570-L685) Supported splitting strategies:

 
 - **JSON Array** - `["result1", "result2"]`
 - **Delimiter-based** - Content separated by `---`, `===`, `***`, or blank lines
 - **Header Repeats** - Repeated headers indicating separate sections
 
 **Sources:** [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts570-685](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L570-L685)

 
## Gemini Format Translation

 Gemini requires a distinct format with separate system instructions and role mapping from `assistant` to `model`.

 
### System Instruction Extraction

 The `formatGeminiMessages` method at [src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts358-504](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts#L358-L504) extracts all system messages into a single `systemInstruction` field:

 
```

```

 
### Role Mapping

 
| DeepChat Role | Gemini Role |
|---|---|
| system | Extracted to systemInstruction |
| user | user |
| assistant | model |
| tool | user (with special part types) |

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts358-368](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts#L358-L368)

 
### Tool Call Translation

 Gemini uses a different structure for function calls:

 
```

```

 The translation occurs at [src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts380-423](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts#L380-L423) where:

 
 - Assistant messages with `tool_calls` become `model` role messages with `functionCall` parts
 - Tool responses become `user` role messages with `functionResponse` parts
 - The tool response is matched to its corresponding tool call by `tool_call_id`
 
 **Sources:** [src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts374-501](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts#L374-L501)

 
### Image Format Translation

 Gemini requires base64 images in `inlineData` format:

 
```

```

 The conversion happens at [src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts468-481](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts#L468-L481)

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts468-481](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts#L468-L481)

 
## Anthropic Format Translation

 Anthropic's Claude API has strict message alternation requirements and uses content blocks rather than simple strings.

 
### Message Grouping Strategy

 The `formatMessages` method at [src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts326-598](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts#L326-L598) implements a two-phase approach:

 **Phase 1: Message Grouping**

 
 - System messages are extracted to a separate `system` field
 - Messages are grouped to ensure proper alternation between user and assistant
 - Tool calls are tracked and paired with their responses
 
 **Phase 2: Content Block Assembly**

 
 - Each group's contents are assembled into `ContentBlockParam[]` arrays
 - Tool responses are inserted immediately after their corresponding tool calls
 
 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts358-598](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts#L358-L598)

 
### Content Block Types

 Anthropic uses typed content blocks:

 
| Block Type | Usage |
|---|---|
| { type: 'text', text: string } | Text content |
| { type: 'image', source: {...} } | Images (base64 or URL) |
| { type: 'tool_use', id, name, input } | Function calls |
| { type: 'tool_result', tool_use_id, content } | Tool results |

 
### Tool Call Translation

 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts514-541](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts#L514-L541)

 
### OAuth Mode Message Translation

 For OAuth authenticated requests, system messages are converted to user messages at [src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts604-703](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts#L604-L703) because the fixed system prompt is required by the Claude Code OAuth API.

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts604-703](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts#L604-L703)

 
## Ollama Format Translation

 Ollama's local model format is simpler but requires special handling for images.

 
### Basic Translation

 The `formatMessages` method at [src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts97-139](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts#L97-L139) performs straightforward role preservation:

 
```

```

 
### Image Extraction

 Ollama expects base64 image data without the data URI prefix. Images are extracted at [src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts113-130](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts#L113-L130):

 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts97-139](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts#L97-L139)

 
## OpenAI Responses API Format Translation

 The Responses API uses a different format than the Chat Completions API.

 
### ResponseInput Format

 The `formatMessages` method at [src/main/presenter/llmProviderPresenter/providers/openAIResponsesProvider.ts152-211](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAIResponsesProvider.ts#L152-L211) translates to `ResponseInput`:

 
```

```

 
### Tool Call Mapping

 
| Internal | Responses API |
|---|---|
| assistant.tool_calls | { type: 'function_call', call_id, name, arguments } |
| tool messages | { type: 'function_call_output', call_id, output } |

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/openAIResponsesProvider.ts152-211](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAIResponsesProvider.ts#L152-L211)

 
## System Prompt Handling Patterns

 Different providers handle system prompts in distinct ways:

 
```

```

 
### Multiple System Messages

 When multiple system messages exist:

 
 - **OpenAI/Ollama**: Preserved as separate messages in array
 - **Gemini**: Concatenated with newlines into single `systemInstruction`
 - **Anthropic**: Concatenated with newlines into single `system` string
 - **Responses API**: Converted to separate `input_text` items
 
 **Sources:** [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts273-559](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L273-L559) [src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts362-368](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts#L362-L368) [src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts333-346](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts#L333-L346)

 
## Native vs Mock Function Calling

 DeepChat supports two modes for tool calling based on model capabilities:

 
### Native Function Calling

 Models with native tool calling support (determined by `modelConfig.functionCall`) receive structured tool definitions and return structured tool calls:

 
```

```

 
### Mock Function Calling

 Models without native support use XML-tagged prompts. The `prepareFunctionCallPrompt` method in `BaseLLMProvider` wraps tool definitions into the system prompt, and responses are parsed for `<function_call>` tags:

 
```

```

 The prompt template is defined at [src/main/presenter/llmProviderPresenter/baseProvider.ts306-437](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/baseProvider.ts#L306-L437) and parsing logic is at [src/main/presenter/llmProviderPresenter/baseProvider.ts446-547](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/baseProvider.ts#L446-L547)

 **Sources:** [src/main/presenter/llmProviderPresenter/baseProvider.ts306-547](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/baseProvider.ts#L306-L547) [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts1002-1009](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L1002-L1009)

 
## Reasoning Content Handling

 DeepChat supports reasoning models that produce thinking/reasoning content separate from the final response. Different providers use different mechanisms:

 
| Provider | Reasoning Mechanism | Translation |
|---|---|---|
| OpenAI | Native reasoning_content field | Preserved in response |
| OpenAI | `The answer is 42" |  |

 // Extracted result { reasoning_content: "Let me analyze this step by step...", content: "The answer is 42" }

 
```
**Sources:** <FileRef file-url="https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L740-L763" min=740 max=763 file-path="src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts">Hii</FileRef> <FileRef file-url="https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts#L507-L552" min=507 max=552 file-path="src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts">Hii</FileRef> <FileRef file-url="https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts#L206-L232" min=206 max=232 file-path="src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts">Hii</FileRef>

## Message Translation Error Handling

Each `formatMessages` implementation includes safeguards for malformed content:

1. **Empty Content Filtering** - Empty text parts are filtered out to prevent API errors
2. **Tool Call ID Generation** - Missing tool call IDs are auto-generated with timestamps
3. **JSON Parsing Fallbacks** - Invalid tool arguments are handled with `jsonrepair`
4. **Content Type Coercion** - Non-string content is stringified when necessary

These safeguards are implemented throughout the translation methods to ensure robust handling of edge cases.

**Sources:** <FileRef file-url="https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts#L453-L510" min=453 max=510 file-path="src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts">Hii</FileRef> <FileRef file-url="https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L420-L434" min=420 max=434 file-path="src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts">Hii</FileRef> <FileRef file-url="https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts#L453-L483" min=453 max=483 file-path="src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts">Hii</FileRef>
```
