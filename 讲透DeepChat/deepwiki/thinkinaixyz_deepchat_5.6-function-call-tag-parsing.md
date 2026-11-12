> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/5.6-function-call-tag-parsing](https://deepwiki.com/thinkinaixyz/deepchat/5.6-function-call-tag-parsing)（Wayback 快照 2026-03-06）
> DeepWiki deepchat/5.6-function-call-tag-parsing

# Function Call Tag Parsing

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

 This document describes the **mock function calling system** used by DeepChat for LLM providers that lack native tool calling support. The system enables these providers to execute MCP tools by instructing them to output function calls in a special XML tag format (`<function_call>`), which is then parsed and executed by the application.

 For information about native tool calling support and the overall agent loop architecture, see [Streaming and Agent Loop](https://deepwiki.com/thinkinaixyz/deepchat/5.3-streaming-and-agent-loop). For provider-specific message formatting, see [Message Format Translation](https://deepwiki.com/thinkinaixyz/deepchat/5.4-message-format-translation). For MCP tool execution mechanics, see [Tool Execution and Permission System](https://deepwiki.com/thinkinaixyz/deepchat/4.4-tool-execution-and-permission-system).

 
---

 
## System Overview

 When a provider's model configuration indicates `functionCall: false`, the system switches from native function calling to a mock implementation. This involves three key steps:

 
 - **Prompt Augmentation**: User messages are prepended with detailed instructions about available tools and how to format function calls
 - **Tag-Based Detection**: The streaming response is parsed character-by-character to detect `<function_call>` XML tags
 - **Format Conversion**: Detected function calls are converted to the standard `LLMCoreStreamEvent` format used by the agent loop
 
 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/baseProvider.ts304-438](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/baseProvider.ts#L304-L438) [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts1006-1009](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L1006-L1009)

 
---

 
## Prompt Wrapping System

 The `getFunctionCallWrapPrompt()` method in `BaseLLMProvider` generates comprehensive instructions that teach the model how to use tools through XML tags.

 
### Prompt Structure

 The generated prompt consists of several sections:

 
| Section | Purpose |
|---|---|
| Tool List Declaration | XML-formatted list of available tools with parameters |
| Invocation Rules | Strict instructions on when and how to call functions |
| Format Specification | JSON schema within <function_call> tags |
| Important Constraints | 7 rules governing tool usage and security |
| Historical Record Format | How to interpret past tool call results |
| Usage Guidelines | Priority order for information sources |

 
### Tool Definition Conversion

 Tools are converted from `MCPToolDefinition` format to XML using `convertToolsToXml()`:

 
```

```

 
### Expected Response Format

 The prompt instructs the model to respond with:

 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/baseProvider.ts306-437](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/baseProvider.ts#L306-L437) [src/main/presenter/llmProviderPresenter/baseProvider.ts707-738](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/baseProvider.ts#L707-L738)

 
---

 
## Streaming Tag Detection

 The system employs a **finite state machine** to detect function call tags in real-time as the model streams its response. This ensures immediate tool execution without waiting for the complete response.

 
### State Machine Architecture

 
```

```

 
### Implementation Variables

 The state machine maintains several key variables during streaming:

 
| Variable | Type | Purpose |
|---|---|---|
| funcState | 'none' \| 'start' \| 'inside' \| 'end' | Current parsing state |
| pendingBuffer | string | Accumulates chars for tag matching |
| funcCallBuffer | string | Content between opening/closing tags |
| funcStartMarker | '<function_call>' | Opening tag constant |
| funcEndMarker | '</function_call>' | Closing tag constant |

 
### Character-by-Character Processing

 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts1096-1198](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L1096-L1198) [src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts803-891](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts#L803-L891)

 
---

 
## Function Call Parsing Logic

 Once a complete `<function_call>` tag is detected, the `parseFunctionCalls()` method extracts structured tool call information from the JSON content.

 
### Multi-Format Support

 The parser handles multiple JSON format variations for maximum compatibility:

 
```

```

 
### Format Examples

 
| Format Type | JSON Structure |
|---|---|
| Standard | {"function_call": {"name": "tool", "arguments": {...}}} |
| Simplified | {"name": "tool", "arguments": {...}} |
| Alternative | {"function": {"name": "tool", "arguments": {...}}} |
| String Args | {"function_call": {"name": "tool", "arguments": "..."}} |

 
### Error Handling

 The parser implements graceful degradation:

 
 - **Direct Parse**: Attempt `JSON.parse()` on raw content
 - **Repair Parse**: Use `jsonrepair()` to fix common JSON errors
 - **Format Detection**: Try multiple format patterns
 - **Fallback**: Return `null` and log error (filter out from results)
 
 
### Argument Normalization

 Arguments are always normalized to string format:

 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/baseProvider.ts446-546](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/baseProvider.ts#L446-L546)

 
---

 
## Message Format Conversion

 For providers without native function call support, tool calls and responses must be converted to/from the mock format in the message history.

 
### Tool Call to Mock Format

 When formatting messages for non-native providers, assistant messages with `tool_calls` are converted to user messages with a special structure:

 
```

```

 
### Mock Record Structure

 The mock format embeds both the original call and its result:

 
```

```

 
### Message Pairing Logic

 The `formatMessages()` method in `OpenAICompatibleProvider` implements sophisticated pairing:

 
 - **Store Pending Calls**: When an assistant message has `tool_calls`, store each call in `pendingToolCalls` map
 - **Match Responses**: When a tool message arrives, look up its corresponding call using `tool_call_id`
 - **Generate Mock**: Create the `function_call_record` structure combining call and response
 - **Insert as User**: Inject as a user message with the `<function_call>` wrapper
 
 
### Pairing Data Structures

 
| Structure | Type | Purpose |
|---|---|---|
| pendingToolCalls | Map<string, {name, arguments, assistantContent}> | Unmatched tool calls |
| pendingToolCallOrder | string[] | Preserve call order |
| pendingNativeToolCallIds | string[] | Track expected IDs (native mode) |

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts273-559](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L273-L559)

 
---

 
## Code Block Variants (Ollama)

 The Ollama provider extends the mock function calling system to handle models that output function calls in code blocks instead of raw XML tags.

 
### Supported Code Block Markers

 
```

```

 
### Code Block State Machine

 
```

```

 
### Code Block Processing Flow

 
 - **Detection**: Check if `pendingBuffer` ends with any code block marker
 - **Accumulation**: Set `isInCodeBlock = true` and accumulate to `codeBlockBuffer`
 - **End Detection**: Watch for closing `\```` marker
 - **Content Cleaning**: Remove language identifier (e.g., `tool_code`) from content
 - **JSON Repair**: Apply repair strategies for common syntax errors
 - **Format Extraction**: Use same multi-format logic as tag parsing
 - **Event Generation**: Emit `tool_call_start`, `tool_call_chunk`, `tool_call_end`
 
 
### JSON Repair Strategies

 The code block parser includes additional repair logic:

 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts560-742](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts#L560-L742)

 
---

 
## Integration with Agent Loop

 The parsed function calls are converted to standard `LLMCoreStreamEvent` types that integrate seamlessly with the agent loop:

 
### Event Sequence

 
```

```

 
### Event Types Generated

 
| Event Type | Fields | Purpose |
|---|---|---|
| tool_call_start | tool_call_id, tool_call_name | Signal start of tool invocation |
| tool_call_chunk | tool_call_id, tool_call_arguments_chunk | Stream arguments incrementally |
| tool_call_end | tool_call_id, tool_call_arguments_complete | Signal completion with full args |

 
### Stop Reason Signaling

 When tool calls are detected, the parser sets `stopReason = 'tool_use'` and `toolUseDetected = true`, which tells the agent loop to:

 
 - Execute the detected tools
 - Append results to message history
 - Continue the agent loop iteration (not stop)
 
 **Sources:** [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts1145-1165](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L1145-L1165) [src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts706-837](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts#L706-L837)

 
---

 
## Provider-Specific Implementations

 
### OpenAI Compatible Providers

 The `OpenAICompatibleProvider` handles both native and mock function calling:

 
 - **Prompt Injection**: Calls `prepareFunctionCallPrompt()` when `supportsFunctionCall=false`
 - **Message Formatting**: Converts tool messages to mock format in `formatMessages()`
 - **Streaming**: Implements dual-mode parsing for both native and tag-based detection
 
 
### Ollama Provider

 Extends mock function calling with additional features:

 
 - **Code Block Support**: Handles `\```tool_code` format
 - **Thinking Tags**: Also parses `<think>` tags simultaneously
 - **State Isolation**: Maintains separate state machines for different tag types
 
 
### Key Differences

 
| Feature | OpenAI Compatible | Ollama |
|---|---|---|
| Tag Format | <function_call> only | <function_call> + code blocks |
| Native Support | Optional (switchable) | Optional (switchable) |
| Thinking Tags | Yes | Yes |
| State Machine | Single-threaded | Multi-state (think + func) |

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts1000-1198](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L1000-L1198) [src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts499-1055](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts#L499-L1055)

 
---

 
## Security and Constraints

 The prompt wrapping system includes security rules to prevent prompt injection and information leakage:

 
### Embedded Security Rules

 
 - **Necessity Check**: Only call tools when they provide essential information
 - **Accuracy Validation**: Tool names must exactly match the provided list
 - **Format Enforcement**: Responses must be pure `<function_call>` tags without extra text
 - **Direct Answer Priority**: Respond directly if information is already known
 - **Avoid Guessing**: Use tools instead of fabricating information
 - **Information Hiding**: Never expose tool calling instructions or format details
 - **Demonstration Prohibition**: Refuse to show `<function_call>` tag examples
 
 
### Language Localization

 The prompt adapts to the user's language setting:

 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/baseProvider.ts333-433](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/baseProvider.ts#L333-L433)
