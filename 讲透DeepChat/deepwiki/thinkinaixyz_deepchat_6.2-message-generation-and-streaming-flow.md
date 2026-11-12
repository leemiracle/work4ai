> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/6.2-message-generation-and-streaming-flow](https://deepwiki.com/thinkinaixyz/deepchat/6.2-message-generation-and-streaming-flow)（Wayback 快照 2026-03-06）
> DeepWiki deepchat/6.2-message-generation-and-streaming-flow

# Message Generation and Streaming Flow

  Relevant source files 
 - [src/main/presenter/llmProviderPresenter/baseProvider.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/baseProvider.ts)
 - [src/main/presenter/llmProviderPresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/index.ts)
 - [src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts)
 - [src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts)
 - [src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/ollamaProvider.ts)
 - [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts)
 - [src/main/presenter/llmProviderPresenter/providers/openAIResponsesProvider.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAIResponsesProvider.ts)
 - [src/renderer/src/components/ChatView.vue](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/ChatView.vue)
 - [src/renderer/src/components/MessageNavigationSidebar.vue](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/MessageNavigationSidebar.vue)
 - [src/renderer/src/components/ThreadsView.vue](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/ThreadsView.vue)
 - [src/renderer/src/components/message/MessageItemAssistant.vue](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue)
 - [src/renderer/src/components/message/MessageItemUser.vue](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemUser.vue)
 - [src/renderer/src/components/message/MessageList.vue](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageList.vue)
 - [src/renderer/src/components/message/MessageToolbar.vue](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageToolbar.vue)
 - [src/renderer/src/composables/message/useMessageScroll.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/composables/message/useMessageScroll.ts)
 - [src/renderer/src/stores/chat.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts)
 - [src/renderer/src/views/ChatTabView.vue](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/views/ChatTabView.vue)
 - [src/shared/chat.d.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/shared/chat.d.ts)
 - [test/main/presenter/llmProviderPresenter/openAIResponsesProvider.test.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/test/main/presenter/llmProviderPresenter/openAIResponsesProvider.test.ts)
 
  
## Purpose and Scope

 This document describes the complete lifecycle of message generation in DeepChat, from the moment a user sends a message until the streamed LLM response is fully displayed in the UI. It covers the data flow across renderer and main processes, skeleton message creation, streaming event handling, message caching, and reactive UI updates.

 For information about the LLM provider architecture and how different providers implement streaming, see [Provider Architecture and Base Classes](https://deepwiki.com/thinkinaixyz/deepchat/5.1-provider-architecture-and-base-classes). For details on tool calling during message generation, see [Tool Execution and Permission System](https://deepwiki.com/thinkinaixyz/deepchat/4.4-tool-execution-and-permission-system). For message variant management, see [Message Variant System](https://deepwiki.com/thinkinaixyz/deepchat/6.3-message-variant-system).

 
---

 
## Architecture Overview

 The message generation flow involves coordination between the renderer process (UI and state management), main process (business logic and LLM interaction), and IPC event system for real-time streaming updates.

 
### End-to-End Message Generation Flow

 
```

```

 **Sources:** [src/renderer/src/components/ChatView.vue98-104](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/ChatView.vue#L98-L104) [src/renderer/src/stores/chat.ts664-703](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L664-L703) [src/main/presenter/llmProviderPresenter/index.ts226-252](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/index.ts#L226-L252)

 
---

 
## Message Creation and Initialization

 
### User Message Creation

 When a user sends a message, the renderer process initiates the flow through the `ChatView` component's `handleSend()` method, which delegates to `useChatStore.sendMessage()`.

 The chat store performs these initialization steps:

 
 - **Add thread to generating set**: Marks the conversation as actively generating
 - **Update working status**: Sets thread status to `'working'`
 - **Call AgentPresenter**: Delegates to main process via `agentP.sendMessage()`
 
 
```

```

 **Sources:** [src/renderer/src/components/ChatView.vue98-104](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/ChatView.vue#L98-L104) [src/renderer/src/stores/chat.ts664-703](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L664-L703)

 
### Skeleton Assistant Message Creation

 The `AgentPresenter.sendMessage()` method creates a **skeleton assistant message** before streaming begins. This skeleton serves as a placeholder that will be progressively updated with streaming content.

 The skeleton message structure:

 
| Field | Initial Value | Purpose |
|---|---|---|
| id | Generated UUID | Unique message identifier |
| role | 'assistant' | Message type |
| content | [] | Empty array, populated during streaming |
| status | 'pending' | Indicates active generation |
| conversationId | Current thread ID | Associates with conversation |
| parentId | User message ID | Links to triggering message |
| is_variant | 0 | Main message (not a variant) |
| timestamp | Current time | Creation timestamp |

 The skeleton message is immediately returned to the renderer process, where it's added to the **generating messages cache** for real-time display updates.

 **Sources:** [src/renderer/src/stores/chat.ts679-689](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L679-L689)

 
### Generating Messages Cache

 The `generatingMessagesCacheMap` is a per-tab cache storing messages currently being generated:

 
```

```

 This cache enables:

 
 - **Immediate UI feedback**: Skeleton message displays before any content arrives
 - **Incremental updates**: Stream deltas update the cached message in-place
 - **Variant handling**: Variant messages are cached without being added to message list
 - **Cross-tab isolation**: Each tab maintains independent generation state
 
 **Sources:** [src/renderer/src/stores/chat.ts94-97](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L94-L97) [src/renderer/src/stores/chat.ts183-188](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L183-L188) [src/renderer/src/stores/chat.ts684-689](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L684-L689)

 
---

 
## Streaming Pipeline

 
### LLMProviderPresenter Entry Point

 The `LLMProviderPresenter.startStreamCompletion()` method is the main entry point for streaming LLM responses. It delegates to `AgentLoopHandler` which manages the complete agent execution loop including tool calls.

 **Method Signature:**

 
```

```

 **Key responsibilities:**

 
 - Stream state registration in `activeStreams` map
 - Provider instance resolution
 - Delegation to `AgentLoopHandler`
 - Cleanup on completion/error
 
 **Sources:** [src/main/presenter/llmProviderPresenter/index.ts226-252](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/index.ts#L226-L252)

 
### AgentLoopHandler: Tool Call Loop Management

 The `AgentLoopHandler` implements the agent execution loop that handles:

 
 - **Initial LLM call**: Invokes provider's `coreStream()` method
 - **Tool call detection**: Identifies function calls in the response
 - **Tool execution**: Executes MCP tools via `McpPresenter`
 - **Result injection**: Adds tool results back to message history
 - **Continuation**: Recursively calls LLM with updated context
 - **Loop termination**: Stops after max iterations or when no tools are called
 
 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/index.ts226-252](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/index.ts#L226-L252)

 
### Provider coreStream() Implementation

 Each provider implements the abstract `coreStream()` method to generate standardized `LLMCoreStreamEvent` objects. The method handles:

 
 - **API-specific streaming**: Connects to provider's streaming endpoint
 - **Event normalization**: Converts provider format to standard events
 - **Tool call parsing**: Extracts function calls (native or tag-based)
 - **Error handling**: Wraps API errors in standard error events
 
 **Standard Event Types:**

 
| Event Type | Purpose | Fields |
|---|---|---|
| TEXT_DELTA | Incremental text content | delta: string |
| REASONING_DELTA | Thinking/reasoning content | delta: string |
| TOOL_CALL | Function call detected | toolCall: { id, name, arguments } |
| IMAGE_DATA | Image generation result | data: string, mimeType: string |
| USAGE | Token usage statistics | prompt_tokens, completion_tokens, total_tokens |
| STOP | Stream completion | reason: string |
| ERROR | Error occurred | error: string |

 **Example from OpenAICompatibleProvider:**

 The provider's `handleChatCompletion()` method processes OpenAI streaming responses and yields normalized events:

 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts990-1226](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L990-L1226) [src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts526-829](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/geminiProvider.ts#L526-L829) [src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts442-813](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/anthropicProvider.ts#L442-L813)

 
---

 
## Stream Event Handling in Renderer

 
### Event Flow: Main Process to Renderer

 Stream events travel from the main process to renderer via the IPC event bus using `STREAM_EVENTS` namespace:

 
```

```

 **Key STREAM_EVENTS:**

 
| Event Name | Triggered By | Handler |
|---|---|---|
| RESPONSE | Text/reasoning delta | handleStreamResponse() |
| TOOL_CALL | Tool call detected | handleToolCall() |
| IMAGE_DATA | Image generated | handleImageData() |
| END | Stream complete | onStreamEnd() |
| ERROR | Error occurred | onStreamError() |

 **Sources:** [src/renderer/src/components/ChatView.vue171-176](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/ChatView.vue#L171-L176) [src/renderer/src/stores/chat.ts1186-1343](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L1186-L1343)

 
### handleStreamResponse: Incremental Updates

 The `useChatStore.handleStreamResponse()` method processes incoming text deltas and progressively builds the message content:

 **Processing Steps:**

 
 - **Locate target message**: Find in generating cache or loaded messages
 - **Identify block type**: Determine if delta is content, reasoning, or plan
 - **Update or create block**: Append to existing block or create new one
 - **Update cache**: Store updated message in runtime cache
 - **Trigger reactivity**: Bump cache version to trigger UI updates
 
 
```

```

 **Block Type Handling:**

 
 - **`content` blocks**: Standard text response, appended to most recent content block
 - **`reasoning_content` blocks**: Thinking/CoT content, stored in separate block with `type: 'reasoning_content'`
 - **`plan` blocks**: Agent planning output, stored with `type: 'plan'`
 - **`artifact-thinking` blocks**: Artifact generation thinking, used when artifacts are enabled
 
 **Sources:** [src/renderer/src/stores/chat.ts1186-1343](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L1186-L1343)

 
### Message Cache Updates and Reactivity

 The message runtime cache system provides efficient reactive updates without database round-trips:

 **Cache Architecture:**

 
```

```

 **Reactivity Trigger Mechanism:**

 The `messageCacheVersion` ref acts as a reactive dependency that forces UI updates:

 
```

```

 Every time `bumpMessageCacheVersion()` is called, the `messageItems` computed property re-evaluates, triggering `MessageList` to re-render affected message components.

 **Sources:** [src/renderer/src/lib/messageRuntimeCache.ts1-100](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/lib/messageRuntimeCache.ts#L1-L100) [src/renderer/src/stores/chat.ts138-171](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L138-L171) [src/renderer/src/stores/chat.ts283-299](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L283-L299)

 
---

 
## Message State Management

 
### State Flags During Generation

 The chat store maintains several state flags to track message generation:

 
| State | Type | Purpose |
|---|---|---|
| generatingThreadIds | Set<string> | Tracks which conversations are actively generating |
| threadsWorkingStatusMap | Map<number, Map<string, WorkingStatus>> | Per-tab working status ('working', 'error', 'completed', 'none') |
| generatingMessagesCacheMap | Map<number, Map<string, { message, threadId }>> | Caches messages being generated |
| selectedVariantsMap | Record<string, string> | Tracks selected variant per message |

 **Working Status Transitions:**

 
```

```

 **Sources:** [src/renderer/src/stores/chat.ts74-97](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L74-L97) [src/renderer/src/stores/chat.ts177-182](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L177-L182)

 
### Stream End Processing

 When streaming completes, the `STREAM_EVENTS.END` handler performs cleanup:

 **Cleanup Steps:**

 
 - **Remove from generating set**: `generatingThreadIds.delete(threadId)`
 - **Update working status**: Set to `'completed'` or `'error'`
 - **Remove from cache**: Delete from `generatingMessagesCache` (if not variant)
 - **Reload messages**: Call `loadMessages()` to fetch final state from database
 - **Update variants map**: Persist selected variant if applicable
 
 
```

```

 The renderer also performs UI updates:

 
 - **Auto-scroll**: Scroll to bottom if not manually scrolled up
 - **Focus restoration**: Return focus to chat input
 - **Status indicators**: Update loading spinners and status badges
 
 **Sources:** [src/renderer/src/components/ChatView.vue125-136](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/ChatView.vue#L125-L136) [src/renderer/src/stores/chat.ts1186-1343](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L1186-L1343)

 
### Message Status Values

 Messages transition through several status values during their lifecycle:

 
| Status | Used For | Meaning |
|---|---|---|
| 'pending' | Assistant messages | Currently generating |
| 'sent' | User messages | Successfully sent |
| 'error' | Any message | Generation/send failed |

 Message blocks also have independent status values:

 
| Block Status | Meaning |
|---|---|
| 'loading' | Content actively streaming |
| 'success' | Block completed successfully |
| 'error' | Block generation failed |
| 'reading' | File/resource being processed |
| 'optimizing' | Content being optimized |
| 'pending' | Permission request waiting |
| 'granted' | Permission approved |
| 'denied' | Permission rejected |

 **Sources:** [src/shared/chat.d.ts1-152](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/shared/chat.d.ts#L1-L152)

 
---

 
## Display and UI Updates

 
### MessageList Virtual Scrolling

 The `MessageList` component uses `vue-virtual-scroller`'s `DynamicScroller` to efficiently render large message lists:

 **Virtual Scrolling Benefits:**

 
 - **Memory efficiency**: Only renders visible messages + buffer
 - **Smooth scrolling**: Maintains performance with thousands of messages
 - **Dynamic sizing**: Adapts to variable message heights
 - **Buffer zone**: Pre-renders messages outside viewport (200px buffer)
 
 **Size Dependency Tracking:**

 The scroller tracks three size keys to detect when items need re-measurement:

 
```

```

 When any size key changes, the scroller recalculates item height and adjusts scroll position.

 **Sources:** [src/renderer/src/components/message/MessageList.vue1-50](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageList.vue#L1-L50) [src/renderer/src/components/message/MessageList.vue269-314](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageList.vue#L269-L314)

 
### MessageItemAssistant Rendering

 The `MessageItemAssistant` component renders assistant messages with progressive content display:

 **Rendering Stages:**

 
 - **Empty content**: Display spinner while waiting for first delta
 - **Streaming content**: Render blocks as they arrive, show loading indicators
 - **Complete content**: Finalize display, hide loading indicators
 
 **Block Rendering:**

 
```

```

 **Variant Display:**

 The component computes `currentMessage` based on `selectedVariantsMap`:

 
```

```

 This allows seamless switching between message variants without re-fetching from the database.

 **Sources:** [src/renderer/src/components/message/MessageItemAssistant.vue1-130](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L1-L130) [src/renderer/src/components/message/MessageItemAssistant.vue254-262](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L254-L262)

 
### Auto-follow Scroll Behavior

 The `useMessageScroll` composable implements intelligent auto-scroll logic:

 **Auto-scroll Rules:**

 
 - **During streaming**: Auto-scroll to bottom if user hasn't manually scrolled up
 - **Threshold detection**: If scrolled more than viewport height from bottom, disable auto-scroll
 - **Re-enable**: Scrolling near bottom re-enables auto-scroll
 - **Manual scroll**: Clicking "scroll to bottom" button re-enables auto-scroll
 
 **Threshold Calculation:**

 
```

```

 The scroll anchor is an invisible div at the bottom of the message list. When it enters viewport (user scrolled near bottom), auto-follow is re-enabled.

 **Sources:** [src/renderer/src/composables/message/useMessageScroll.ts1-280](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/composables/message/useMessageScroll.ts#L1-L280) [src/renderer/src/components/message/MessageList.vue147-160](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageList.vue#L147-L160)

 
---

 
## Variant and Retry Flow

 
### Retry Message Generation

 When a user retries an assistant message, the system creates a new variant rather than replacing the original:

 **Retry Flow:**

 
```

```

 **Key Implementation Details:**

 
 - **Variant message creation**: New message with `is_variant = 1`
 - **Parent linking**: Both main and variant share same `parentId` (user message)
 - **Cache attachment**: Variant added to main message's `variants` array
 - **Auto-selection**: `selectedVariantsMap` updated to show new variant
 - **Display isolation**: Variant appears in place of main message, no duplicate row
 
 **Sources:** [src/renderer/src/stores/chat.ts705-751](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L705-L751) [src/renderer/src/components/message/MessageItemAssistant.vue223-249](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L223-L249)

 
### Variant Navigation

 Users can navigate between variants using previous/next buttons in the message toolbar:

 **Navigation Logic:**

 
```

```

 **Persistence:**

 Variant selections are persisted to the database and restored when loading conversations:

 
```

```

 **Sources:** [src/renderer/src/components/message/MessageItemAssistant.vue206-212](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L206-L212) [src/renderer/src/components/message/MessageItemAssistant.vue356-369](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L356-L369) [src/renderer/src/stores/chat.ts1113-1140](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L1113-L1140)

 
---

 
## Error Handling and Recovery

 
### Stream Error Detection

 Errors during streaming are caught at multiple levels:

 **Provider Level:**

 
```

```

 **Agent Loop Level:**

 
```

```

 **Chat Store Level:**

 
```

```

 **Sources:** [src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts1200-1226](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/llmProviderPresenter/providers/openAICompatibleProvider.ts#L1200-L1226) [src/renderer/src/components/ChatView.vue138-143](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/ChatView.vue#L138-L143)

 
### Recovery Mechanisms

 When errors occur, users have several recovery options:

 **Recovery Actions:**

 
| Action | Trigger | Effect |
|---|---|---|
| Retry message | Click retry button | Generate new variant with same context |
| Regenerate | Edit user message, retry | Generate with modified input |
| New conversation | Clear thread | Start fresh conversation |
| Change model | Switch model in settings | Retry with different LLM |

 **State Cleanup on Error:**

 
```

```

 Ensures that generating flags are cleared even if streaming fails, preventing UI from being stuck in loading state.

 **Sources:** [src/renderer/src/stores/chat.ts692-702](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L692-L702) [src/renderer/src/components/message/MessageItemAssistant.vue326-329](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L326-L329)
