> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/6-chat-and-conversation-system](https://deepwiki.com/thinkinaixyz/deepchat/6-chat-and-conversation-system)（Wayback 快照 2026-03-06）
> DeepWiki deepchat/6-chat-and-conversation-system

# Chat and Conversation System

  Relevant source files 
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
 
  The Chat and Conversation System is the core user-facing component of DeepChat, managing the entire lifecycle of conversations (threads), messages, and their real-time streaming display. This system handles thread creation and activation, message generation with LLM providers, variant management for multiple response versions, child conversation forking, and efficient message caching with virtual scrolling.

 This document covers the overall architecture and data flow of the chat system. For details on specific aspects:

 
 - Provider integration and LLM streaming: see [LLM Provider Integration](https://deepwiki.com/thinkinaixyz/deepchat/5-llm-provider-integration)
 - MCP tool execution within messages: see [Model Context Protocol (MCP) System](https://deepwiki.com/thinkinaixyz/deepchat/4-model-context-protocol-(mcp)-system)
 - File attachment handling: see [File Processing and Artifact System](https://deepwiki.com/thinkinaixyz/deepchat/7-file-processing-system)
 - UI component details: see subsection [Chat UI Components](https://deepwiki.com/thinkinaixyz/deepchat/6.4-chat-ui-components)
 
 
## Architecture Overview

 The chat system follows a presenter-store pattern with clear separation between the Electron main process (business logic) and renderer process (UI state).

 
### Core Components

 
```

```

 **Sources:** [src/renderer/src/stores/chat.ts1-200](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L1-L200) [src/shared/chat.d.ts1-50](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/shared/chat.d.ts#L1-L50)

 
### Data Flow Architecture

 
```

```

 **Sources:** [src/renderer/src/stores/chat.ts664-703](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L664-L703) [src/renderer/src/stores/chat.ts872-1400](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L872-L1400)

 
## Thread (Conversation) Structure

 A thread (also called conversation) is the primary container for a chat session. Each thread maintains its own configuration, message history, and optional parent-child relationships.

 
### Thread Entity Schema

 
| Field | Type | Description |
|---|---|---|
| id | string | Unique thread identifier (UUID) |
| title | string | Thread display name |
| settings | CONVERSATION_SETTINGS | Model, prompts, temperature, etc. |
| timestamp | number | Creation timestamp |
| parentConversationId | string? | Parent thread (for child threads) |
| parentMessageId | string? | Specific parent message |
| parentSelection | ParentSelection? | Selected text that spawned child |

 
### Thread Settings Structure

 
```

```

 **Sources:** [src/renderer/src/stores/chat.ts100-115](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L100-L115) [src/shared/presenter.d.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/shared/presenter.d.ts#LNaN-LNaN)

 
### Thread State Management

 The `chatStore` maintains per-tab thread state using Maps keyed by tab ID:

 
```

```

 **Key Methods:**

 
 - `getTabId()`: Returns current webContents ID [chat.ts133](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L133-L133)
 - `getActiveThreadId()`: Returns active thread for current tab [chat.ts134](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L134-L134)
 - `setActiveThreadId(threadId)`: Sets active thread [chat.ts135-137](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L135-L137)
 - `createThread(title, settings)`: Creates new thread [chat.ts367-402](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L367-L402)
 - `setActiveThread(threadId)`: Activates existing thread [chat.ts404-410](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L404-L410)
 
 **Sources:** [src/renderer/src/stores/chat.ts74-98](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L74-L98) [src/renderer/src/stores/chat.ts133-137](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L133-L137)

 
## Message Structure and Types

 Messages are the atomic units of conversation content. DeepChat supports two primary message roles: `user` and `assistant`.

 
### Message Base Type

 
```

```

 **Sources:** [src/shared/chat.d.ts3-32](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/shared/chat.d.ts#L3-L32)

 
### User Message Content

 User messages contain rich content including text, files, mentions, and metadata flags:

 
```

```

 **Sources:** [src/shared/chat.d.ts62-72](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/shared/chat.d.ts#L62-L72)

 
### Assistant Message Blocks

 Assistant messages consist of typed blocks representing different content types:

 
```

```

 Each block has the structure:

 
```

```

 **Sources:** [src/shared/chat.d.ts84-152](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/shared/chat.d.ts#L84-L152)

 
### Block Type Rendering

 Each block type has a dedicated Vue component:

 
| Block Type | Component | Purpose |
|---|---|---|
| content | MessageBlockContent.vue | Markdown text rendering |
| reasoning_content | MessageBlockThink.vue | Collapsible reasoning display |
| tool_call | MessageBlockToolCall.vue | Tool execution with parameters |
| action (permission) | MessageBlockPermissionRequest.vue | Permission approval UI |
| action (question) | MessageBlockQuestionRequest.vue | Question prompts |
| error | MessageBlockError.vue | Error display |
| image | MessageBlockImage.vue | Image rendering |
| audio | MessageBlockAudio.vue | Audio player |
| mcp_ui_resource | MessageBlockMcpUi.vue | MCP UI components |
| plan | MessageBlockPlan.vue | Agent plan display |

 **Sources:** [src/renderer/src/components/message/MessageItemAssistant.vue26-88](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L26-L88)

 
## State Management (chatStore)

 The `chatStore` is the central Pinia store managing all chat-related state in the renderer process.

 
### Key State Properties

 
```

```

 **Sources:** [src/renderer/src/stores/chat.ts74-98](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L74-L98)

 
### Critical Computed Properties

 **`messageItems`**: Transforms message IDs into resolved message objects with variant support:

 
```

```

 **`variantAwareMessages`**: Filters out null messages and applies variant selection:

 
```

```

 **Sources:** [src/renderer/src/stores/chat.ts283-305](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L283-L305)

 
### Core Actions

 
#### Thread Operations

 
```

```

 **Sources:** [src/renderer/src/stores/chat.ts367-448](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L367-L448)

 
#### Message Operations

 **`sendMessage(content)`**: Initiates message generation:

 
 - Adds thread to `generatingThreadIds` [chat.ts669](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L669-L669)
 - Calls `agentPresenter.sendMessage()` via IPC [chat.ts672-677](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L672-L677)
 - Caches skeleton message [chat.ts684-689](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L684-L689)
 - Reloads message list [chat.ts691](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L691-L691)
 
 **`retryMessage(messageId)`**: Creates a variant response:

 
 - Calls `agentPresenter.retryMessage()` [chat.ts708](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L708-L708)
 - Caches variant as part of main message [chat.ts716-729](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L716-L729)
 - Updates `selectedVariantsMap` to show new variant [chat.ts730](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L730-L730)
 
 **`regenerateFromUserMessage(userMessageId)`**: Regenerates from a specific user message:

 
 - Calls `agentPresenter.regenerateFromUserMessage()` [chat.ts760-764](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L760-L764)
 - Creates new assistant message (not a variant) [chat.ts766-771](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L766-L771)
 
 **Sources:** [src/renderer/src/stores/chat.ts664-778](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L664-L778)

 
## Message Lifecycle

 The complete lifecycle of a message from user input to persisted storage involves multiple stages and stream events.

 
### Message Generation Flow

 
```

```

 **Sources:** [src/renderer/src/stores/chat.ts664-703](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L664-L703) [src/renderer/src/stores/chat.ts872-1400](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L872-L1400)

 
### Stream Event Handling

 The `handleStreamResponse` function processes all stream events from the main process [chat.ts872-1400](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L872-L1400):

 **Event Types:**

 
| Event | stream_kind / tool_call | Action |
|---|---|---|
| Init | stream_kind: 'init' | Create skeleton message chat.ts956-1021 |
| Content | content field present | Append to last content block chat.ts1328-1342 |
| Reasoning | reasoning_content present | Update reasoning block chat.ts1345-1364 |
| Tool Start | tool_call: 'start' | Add tool_call block chat.ts1197-1213 |
| Tool Update | tool_call: 'update' | Update parameters chat.ts1214-1233 |
| Tool End | tool_call: 'end' | Mark success with response chat.ts1274-1296 |
| Permission | tool_call: 'permission-required' | Add permission request block chat.ts1106-1158 |
| Question | tool_call: 'question-required' | Add question request block chat.ts1075-1103 |
| Image | image_data present | Add image/audio block chat.ts1297-1311 |
| Rate Limit | rate_limit present | Show rate limit warning chat.ts1312-1327 |
| Final | stream_kind: 'final' | Finalize and persist chat.ts1365-1400 |

 **Sources:** [src/renderer/src/stores/chat.ts872-1400](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L872-L1400)

 
### Message Finalization

 The `finalizeAssistantMessageBlocks` function ensures blocks are properly closed before adding new ones:

 
```

```

 This is called before:

 
 - Adding tool call blocks [chat.ts1198-1258](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L1198-L1258)
 - Adding permission blocks [chat.ts1107](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L1107-L1107)
 - Adding error blocks [chat.ts1067](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L1067-L1067)
 - Adding rate limit blocks [chat.ts1313](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L1313-L1313)
 - Adding new content blocks after reasoning [chat.ts1334](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L1334-L1334)
 
 **Sources:** [src/shared/chat/messageBlocks.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/shared/chat/messageBlocks.ts#LNaN-LNaN) [src/renderer/src/stores/chat.ts1041-1334](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L1041-L1334)

 
## Message Variants System

 The variant system allows multiple response versions for a single assistant message, enabling users to retry generation and compare different outputs.

 
### Variant Data Model

 
```

```

 **Key Properties:**

 
 - **Main message**: `is_variant: 0` (default/first response)
 - **Variant messages**: `is_variant: 1` (retry responses)
 - All variants share the same `parentId` (the user message)
 - Main message contains `variants` array with all variant objects
 
 **Sources:** [src/shared/chat.d.ts30-31](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/shared/chat.d.ts#L30-L31) [src/renderer/src/stores/chat.ts189-204](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L189-L204)

 
### Variant Selection State

 The `selectedVariantsMap` tracks which variant is currently displayed for each main message:

 
```

```

 
### Variant Resolution

 The `resolveVariantMessage` function swaps the main message content with the selected variant:

 
```

```

 This ensures the UI always displays the correct variant without duplicating messages in the list.

 **Sources:** [src/renderer/src/stores/chat.ts259-281](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L259-L281)

 
### Variant Generation Workflow

 
```

```

 **Sources:** [src/renderer/src/stores/chat.ts705-751](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L705-L751)

 
### Variant Navigation UI

 The `MessageToolbar` component provides prev/next buttons when variants exist:

 
```

```

 **Navigation Actions:**

 
 - **Prev**: Decrement index [MessageItemAssistant.vue359](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/MessageItemAssistant.vue#L359-L359)
 - **Next**: Increment index [MessageItemAssistant.vue361](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/MessageItemAssistant.vue#L361-L361)
 - Updates `selectedVariantsMap` with new variant ID [MessageItemAssistant.vue368](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/MessageItemAssistant.vue#L368-L368)
 
 **Sources:** [src/renderer/src/components/message/MessageItemAssistant.vue206-212](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L206-L212) [src/renderer/src/components/message/MessageItemAssistant.vue356-369](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L356-L369)

 
### Auto-Switch on New Variant

 When a new variant finishes generating, the system automatically switches to display it:

 
```

```

 **Sources:** [src/renderer/src/components/message/MessageItemAssistant.vue265-279](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L265-L279)

 
## Child Conversations and Forking

 DeepChat supports two types of conversation branching: **child conversations** (with context highlighting) and **fork conversations** (independent copies).

 
### Child Conversation Architecture

 
```

```

 **Key Properties:**

 
 - `parentConversationId`: Links to parent thread
 - `parentMessageId`: Specific message where child was created
 - `parentSelection`: Stores selected text and range information
 
 **Sources:** [src/shared/presenter.d.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/shared/presenter.d.ts#LNaN-LNaN)

 
### Child Thread Creation Flow

 
```

```

 **Sources:** [src/renderer/src/stores/chat.ts830-870](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L830-L870)

 
### Child Thread Tracking

 The store maintains a map of child threads per message:

 
```

```

 **Sources:** [src/renderer/src/stores/chat.ts552-575](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L552-L575)

 
### Context Mention System

 When opening a child thread, the selected text is queued as a pending context mention:

 
```

```

 The mention appears in the input as a `@` mention chip [chat.ts313-334](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L313-L334) and can be consumed on send [chat.ts336-341](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L336-L341)

 **Sources:** [src/renderer/src/stores/chat.ts321-341](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L321-L341) [src/renderer/src/stores/chat.ts577-592](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L577-L592)

 
### Fork Thread (Independent Copy)

 Unlike child threads, fork threads create a completely independent conversation up to a specific message:

 
```

```

 **Fork Dialog UI:**

 
```

```

 **Sources:** [src/renderer/src/stores/chat.ts800-828](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L800-L828) [src/renderer/src/components/message/MessageItemAssistant.vue112-129](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L112-L129)

 
## Message Caching and Performance

 The chat system uses a multi-layer caching strategy to minimize database queries and ensure smooth scrolling with large conversation histories.

 
### Cache Architecture

 
```

```

 **Sources:** [src/renderer/src/lib/messageRuntimeCache.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/lib/messageRuntimeCache.ts) [src/renderer/src/stores/chat.ts82-98](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L82-L98)

 
### Message Runtime Cache API

 Located in [src/renderer/src/lib/messageRuntimeCache.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/lib/messageRuntimeCache.ts):

 
```

```

 **Cache Invalidation:**

 
 - On thread switch: `clearCachedMessagesForThread()` [chat.ts437-452](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L437-L452)
 - On message update: Individual cache entries updated [chat.ts164-169](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L164-L169)
 - Reactive trigger: `messageCacheVersion` bumped [chat.ts138-170](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L138-L170)
 
 **Sources:** [src/renderer/src/lib/messageRuntimeCache.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/lib/messageRuntimeCache.ts) [src/renderer/src/stores/chat.ts138-171](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L138-L171)

 
### Prefetching Strategy

 The store implements aggressive prefetching to keep nearby messages cached:

 
```

```

 **Prefetch Triggers:**

 
 - Initial load: First 50 messages [chat.ts655](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L655-L655)
 - Virtual scroll viewport change (via component)
 - Manual prefetch all: `prefetchAllMessages()` [chat.ts624-628](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L624-L628)
 
 **Sources:** [src/renderer/src/stores/chat.ts594-628](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L594-L628)

 
### Generating Messages Cache

 In-flight messages are cached separately to avoid premature persistence:

 
```

```

 **Usage:**

 
 - Added on stream init [chat.ts684-766](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L684-L766)
 - Merged into main message variants [chat.ts716-729](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L716-L729)
 - Included in message list until persisted [chat.ts646-654](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L646-L654)
 - Cleaned up on thread clear [chat.ts453-461](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/chat.ts#L453-L461)
 
 **Sources:** [src/renderer/src/stores/chat.ts95-188](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L95-L188) [src/renderer/src/stores/chat.ts646-654](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L646-L654)

 
### Virtual Scrolling Integration

 The message list uses `vue-virtual-scroller` for efficient rendering of large conversations. The DOM info cache stores each message's position:

 
```

```

 This allows the virtual scroller to:

 
 - Calculate total scroll height
 - Determine visible range
 - Scroll to specific messages
 - Restore scroll position on navigation
 
 **Sources:** [src/renderer/src/stores/chat.ts630-636](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L630-L636) [src/renderer/src/lib/messageRuntimeCache.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/lib/messageRuntimeCache.ts)

 
### Search Result Enrichment

 Search results in assistant messages contain extra metadata that requires additional fetching:

 
```

```

 **Sources:** [src/renderer/src/stores/chat.ts493-530](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L493-L530)

 
---

 This document provides a comprehensive overview of the Chat and Conversation System. For implementation details on specific aspects, refer to the subsections: [Thread and Message Management](https://deepwiki.com/thinkinaixyz/deepchat/6.1-thread-and-message-management), [Message Generation and Streaming Flow](https://deepwiki.com/thinkinaixyz/deepchat/6.2-message-generation-and-streaming-flow), [Message Variant System](https://deepwiki.com/thinkinaixyz/deepchat/6.3-message-variant-system), [Chat UI Components](https://deepwiki.com/thinkinaixyz/deepchat/6.4-chat-ui-components), [Message Caching and Virtual Scrolling](https://deepwiki.com/thinkinaixyz/deepchat/6.5-message-caching-and-virtual-scrolling), [Thread Creation and Model Selection](https://deepwiki.com/thinkinaixyz/deepchat/6.6-thread-creation-and-model-selection), and [Child Conversations and Forking](https://deepwiki.com/thinkinaixyz/deepchat/6.7-child-conversations-and-forking).
