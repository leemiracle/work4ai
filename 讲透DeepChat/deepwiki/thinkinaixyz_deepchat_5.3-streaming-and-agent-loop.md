> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/5.3-streaming-and-agent-loop](https://deepwiki.com/thinkinaixyz/deepchat/5.3-streaming-and-agent-loop)（Wayback 快照 2026-03-06）
> DeepWiki deepchat/5.3-streaming-and-agent-loop

# Streaming and Agent Loop

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

 This document describes the streaming completion system and agent loop architecture that powers real-time message generation with iterative tool execution in DeepChat. It covers how LLM responses are streamed from providers, how tool calls trigger additional iterations, rate limiting, and the standardized event system that bridges provider-specific APIs to the application layer.

 For provider-specific implementations, see [Provider Implementations](https://deepwiki.com/thinkinaixyz/deepchat/5.2-provider-implementations). For tool execution details, see [Tool Execution and Permission System](https://deepwiki.com/thinkinaixyz/deepchat/4.4-tool-execution-and-permission-system). For message persistence and UI updates, see [Message Generation and Streaming Flow](https://deepwiki.com/thinkinaixyz/deepchat/6.2-message-generation-and-streaming-flow).

 
## Architecture Overview

 The streaming system consists of three main layers: the `LLMProviderPresenter` that manages provider instances and rate limiting, the `AgentLoopHandler` that orchestrates the iterative tool-calling loop, and provider-specific `coreStream` implementations that normalize API responses into `LLMCoreStreamEvent` objects.

 
### System Component Diagram

 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/index.ts1-252](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/index.ts#L1-L252) [src/main/presenter/llmProviderPresenter/baseProvider.ts19-643](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/baseProvider.ts#L19-L643)

 
## Stream Completion Entry Point

 The `startStreamCompletion` method in `LLMProviderPresenter` serves as the primary entry point for initiating a streaming conversation with tool support. This method is called from `SessionPresenter` when a user sends a message.

 
### Method Signature

 
```

```

 The method delegates to `AgentLoopHandler.startStreamCompletion()` which manages the complete lifecycle of a streaming response including tool execution loops.

 
### Stream State Tracking

 Each active stream is tracked in the `activeStreams` Map with the following structure:

 
```

```

 The `activeStreams` Map enables:

 
 - Stream cancellation via `stopStream(eventId)`
 - Concurrent stream management with `canStartNewStream()` checking against `maxConcurrentStreams`
 - Resource cleanup when streams complete
 
 **Sources:** [src/main/presenter/llmProviderPresenter/index.ts226-252](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/index.ts#L226-L252) [src/main/presenter/llmProviderPresenter/types.ts1-50](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/types.ts#L1-L50)

 
## LLMCoreStreamEvent Types

 All provider implementations normalize their API responses into a standardized event stream using the `LLMCoreStreamEvent` type. This abstraction allows the agent loop to handle responses uniformly regardless of the underlying provider.

 
### Event Type Reference

 
| Event Type | Purpose | Key Fields |
|---|---|---|
| text | Regular text content chunk | content: string |
| reasoning | Thinking/reasoning content (o1, Gemini 2.5) | reasoning: string |
| tool_call_start | Tool invocation begins | tool_call_id, tool_call_name |
| tool_call_chunk | Tool arguments streaming | tool_call_id, tool_call_arguments_chunk |
| tool_call_end | Tool arguments complete | tool_call_id, tool_call_arguments_complete |
| usage | Token usage statistics | prompt_tokens, completion_tokens, total_tokens |
| stop | Stream completion | stop_reason: 'complete' \| 'tool_use' \| 'length' \| 'error' |
| error | Error occurred | error: string |
| imageData | Generated image (DALL-E, Gemini Imagen) | data: string, mimeType: string |

 
### Event Creation Helper

 The `createStreamEvent` utility provides type-safe event construction:

 
```

```

 **Sources:** [src/shared/types/core/llm-events.ts1-100](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/shared/types/core/llm-events.ts#L1-L100) [src/main/presenter/llmProviderPresenter/baseProvider.ts635-643](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/baseProvider.ts#L635-L643)

 
## Provider coreStream Implementation

 Each provider implements the abstract `coreStream` method which performs a single API request and yields standardized events. The agent loop calls this method potentially multiple times when tool calls are involved.

 
### Base Method Contract

 
```

```

 
### Stream Processing Flow

 
```

```

 The parser extracts content between tags and yields it as separate reasoning events.

 
### Configuration Parameters

 Reasoning models support additional configuration:

 
 - `thinkingBudget` (Gemini 2.5): Controls reasoning computation time
 - `reasoningEffort` (OpenAI o1): `minimal` | `low` | `medium` | `high`
 - `verbosity` (OpenAI o3): Controls output detail level
 
 These parameters are checked via `ModelCapabilities` before being passed to the API:

 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts726-766](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L726-L766) [src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts310-355](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts#L310-L355) [src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts204-232](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts#L204-L232)

 
## Error Handling and Recovery

 The streaming system implements multiple layers of error handling to ensure robust operation even when provider APIs fail or return malformed data.

 
### Error Event Propagation

 When errors occur during streaming, they're yielded as error events rather than thrown:

 
```

```

 This allows the UI to display partial responses and error messages without losing accumulated content.

 
### JSON Repair for Tool Calls

 Malformed JSON in tool call arguments is automatically repaired using `jsonrepair`:

 
```

```

 This handles common issues like trailing commas, unquoted keys, and truncated JSON.

 
### Stream Abort Handling

 When a stream is aborted via `AbortController`, the provider cleans up resources and ensures the stream terminates gracefully:

 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/baseProvider.ts446-547](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/baseProvider.ts#L446-L547) [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts1050-1250](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L1050-L1250)
