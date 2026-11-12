> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/6.1-thread-and-message-management](https://deepwiki.com/thinkinaixyz/deepchat/6.1-thread-and-message-management)（Wayback 快照 2026-03-06）
> DeepWiki deepchat/6.1-thread-and-message-management

# Thread and Message Management

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
 
  This page documents the thread (conversation) and message state management system in DeepChat's renderer process. It covers the `useChatStore` Pinia store architecture, per-tab state isolation, message ID tracking, the message runtime cache, and lazy loading strategies. For information about message streaming and generation, see [Message Generation and Streaming Flow](https://deepwiki.com/thinkinaixyz/deepchat/6.2-message-generation-and-streaming-flow). For message variant display and navigation, see [Message Variant System](https://deepwiki.com/thinkinaixyz/deepchat/6.3-message-variant-system).

 
---

 
## Architecture Overview

 The thread and message management system centers around the `useChatStore` Pinia store, which maintains per-tab state for active threads, message lists, and runtime caches. The store communicates with the main process via presenters and implements a two-tier caching strategy: message IDs in reactive state and full message objects in a non-reactive runtime cache.

 
```

```

 **Per-Tab State Isolation**: The store uses `Map` structures keyed by tab ID (`window.api.getWebContentsId()`) to maintain independent state for each browser tab. This allows multiple conversations to be open simultaneously without interference.

 **Two-Tier Caching Strategy**: The store maintains lightweight message ID arrays in reactive state (`messageIdsMap`) while full `Message` objects are stored in a separate non-reactive cache (`messageRuntimeCache`). This approach minimizes reactivity overhead for large conversation histories.

 **Sources**: [src/renderer/src/stores/chat.ts1-250](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L1-L250)

 
---

 
## Per-Tab State Management

 The `useChatStore` implements per-tab state isolation using `Map` structures where each tab's state is stored under its WebContents ID. This architecture enables true multi-tab conversation management without state conflicts.

 
### Tab ID Resolution

 
```

```

 The `getTabId()` helper function wraps the Electron API call to retrieve the current tab's WebContents ID. All per-tab state operations use this identifier as the map key.

 **Sources**: [src/renderer/src/stores/chat.ts133-137](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L133-L137)

 
### Per-Tab State Structures

 
| State Map | Type | Purpose |
|---|---|---|
| activeThreadIdMap | Map<number, string \| null> | Tracks which thread is active in each tab |
| messageIdsMap | Map<number, string[]> | Stores message ID lists for each tab's active thread |
| threadsWorkingStatusMap | Map<number, Map<string, WorkingStatus>> | Tracks generation status per thread per tab |
| generatingMessagesCacheMap | Map<number, Map<string, {message, threadId}>> | Caches messages being generated per tab |

 **Active Thread Tracking**: Each tab maintains its own active thread ID. When a user switches threads in one tab, other tabs remain unaffected.

 
```

```

 **Message ID Array Management**: Each tab's message list is stored as an array of IDs, ordered chronologically. This array is the source of truth for what messages should be displayed.

 
```

```

 **Cache Version Bumping**: The `messageCacheVersion` ref triggers Vue reactivity when message IDs change, forcing dependent computed properties to recalculate without directly mutating the non-reactive message cache.

 **Sources**: [src/renderer/src/stores/chat.ts75-145](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L75-L145)

 
---

 
## Thread (Conversation) Management

 Thread management operations handle the lifecycle of conversations, including creation, activation, switching, and cleanup. The store delegates persistence operations to `SessionPresenter` in the main process while managing local UI state.

 
### Thread Creation Flow

 
```

```

 **Settings Normalization**: The `createThread` method automatically attaches ACP agent working directories from `chatConfig.acpWorkdirMap` if the thread uses an ACP provider, ensuring agent workspace context is preserved.

 **Automatic Activation**: After creation, the presenter automatically activates the new thread for the requesting tab, and the store updates its local `activeThreadIdMap` state immediately to prevent race conditions with subsequent operations.

 **Sources**: [src/renderer/src/stores/chat.ts367-402](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L367-L402)

 
### Thread Activation and Switching

 Thread activation is a coordinated operation between the renderer and main process. The renderer sends an intent to activate a thread, and the main process validates and executes it, broadcasting the result via events.

 
```

```

 **Deduplication Logic**: The main process prevents redundant activations by checking if the thread is already active for the requesting tab, avoiding unnecessary database queries and event broadcasts.

 **Event-Driven State Update**: The renderer listens for `CONVERSATION_EVENTS.ACTIVATED` to update its local state, ensuring consistency even when multiple tabs interact with the same thread.

 **Sources**: [src/renderer/src/stores/chat.ts404-410](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L404-L410)

 
### Thread Cleanup and Reset

 When clearing a thread or switching to a different one, the store performs comprehensive cleanup to prevent memory leaks and stale UI state.

 
```

```

 **Cleanup Operations**:

 
 - Clear active thread ID in main process and local state
 - Empty message ID array for the tab
 - Remove cached message objects for the thread
 - Clear DOM position information for virtual scrolling
 - Reset variant selections
 - Clear child thread mappings
 - Remove pending context mentions and scroll targets
 - Reset ACP agent workspace preferences
 
 **Sources**: [src/renderer/src/stores/chat.ts430-448](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L430-L448)

 
---

 
## Message ID Tracking System

 The message ID tracking system maintains ordered arrays of message IDs per tab, serving as the source of truth for what messages should be displayed. Full message objects are loaded on-demand from the runtime cache or fetched from the database.

 
### Message ID Array Structure

 
```

```

 **Ordered Array**: Message IDs are stored in chronological order, matching the conversation flow. This array is loaded from the database when a thread becomes active.

 **Computed Message Items**: The `messageItems` computed property maps each ID to a `MessageListItem` object containing the ID and the corresponding cached message (or `null` if not yet loaded).

 **Sources**: [src/renderer/src/stores/chat.ts283-299](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L283-L299)

 
### Message ID Operations

 
| Operation | Method | Purpose |
|---|---|---|
| Get IDs | getMessageIds() | Retrieves ID array for current tab |
| Set IDs | setMessageIds(ids) | Replaces entire ID array and bumps cache version |
| Ensure ID | ensureMessageId(messageId) | Adds ID if not present, maintaining order |
| Load IDs | loadMessages() | Fetches ID array from database for active thread |

 **ensureMessageId Pattern**: This method is used when streaming messages arrive to ensure the new message appears in the list if it's not a variant. It checks for existence before adding to avoid duplicates.

 
```

```

 **Cache Version Mechanism**: After modifying the ID array, `bumpMessageCacheVersion()` increments a reactive counter that forces the `messageItems` computed property to recalculate, triggering UI updates.

 **Sources**: [src/renderer/src/stores/chat.ts142-151](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L142-L151)

 
### Message Loading Flow

 
```

```

 The `loadMessages` method is called when a thread becomes active. It fetches only message IDs initially, then loads full message objects on-demand as the virtual scroller requests them.

 **Sources**: [src/renderer/src/stores/chat.ts638-662](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L638-L662)

 
---

 
## Message Runtime Cache

 The message runtime cache is a separate, non-reactive `Map<messageId, Message>` that stores full message objects to avoid Vue reactivity overhead. The cache is defined in `messageRuntimeCache.ts` and provides low-level operations for storing and retrieving messages.

 
### Cache Operations

 
```

```

 **Non-Reactive Storage**: The cache uses a plain JavaScript `Map` rather than Vue `ref` or `reactive` to avoid tracking overhead for potentially thousands of message objects. Vue reactivity is triggered indirectly via `messageCacheVersion`.

 **Store Integration**: The store wraps cache operations with cache version bumping to trigger reactive updates:

 
```

```

 **Sources**: [src/renderer/src/stores/chat.ts30-39](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L30-L39) [src/renderer/src/stores/chat.ts163-171](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L163-L171)

 
### Cache and Reactivity Integration

 The `messageItems` computed property bridges the reactive ID array with the non-reactive cache:

 
```

```

 **Lazy Loading Support**: When `getCachedMessage` returns `null`, the `MessageList` component displays a placeholder and triggers background fetching via `ensureMessagesLoadedByIds`.

 **Variant Resolution**: The computed property applies variant selection logic to replace message content with the selected variant if applicable, creating a new message object with swapped content.

 **Sources**: [src/renderer/src/stores/chat.ts283-299](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L283-L299)

 
---

 
## Message Loading Strategies

 The store implements multiple loading strategies to balance performance and user experience: initial batch loading, lazy loading for off-screen messages, and intelligent prefetching around the viewport.

 
### Batch Loading with Prefetching

 When a thread becomes active, the store loads message IDs synchronously, then fetches the first batch of messages and prefetches a range around the viewport.

 
```

```

 **Constants**:

 
 - `PREFETCH_BUFFER = 24`: Number of messages to fetch beyond visible viewport
 - `PREFETCH_BATCH_SIZE = 80`: Maximum messages per database query
 
 **Sources**: [src/renderer/src/stores/chat.ts594-662](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L594-L662)

 
### Lazy Loading with ensureMessagesLoadedByIds

 The `ensureMessagesLoadedByIds` method checks which messages are missing from the cache and fetches them in batches.

 
```

```

 **Batch Fetching**: The `fetchMessagesByIds` method processes IDs in chunks of 80 to avoid overwhelming the database with large queries while minimizing round trips.

 **Sources**: [src/renderer/src/stores/chat.ts597-613](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L597-L613)

 
### Intelligent Prefetching for Virtual Scrolling

 The `prefetchMessagesForRange` method is called by the `MessageList` virtual scroller when the viewport changes, loading messages in a buffer zone around visible items.

 
```

```

 **Buffer Zone**: By prefetching `PREFETCH_BUFFER` (24) messages before and after the visible range, the system ensures smooth scrolling without visible loading delays.

 **Virtual Scroller Integration**: The `MessageList` component calls `prefetchMessagesForRange` in its `handleVirtualUpdate` callback, which fires when the virtual scroller's visible range changes.

 **Sources**: [src/renderer/src/stores/chat.ts615-622](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L615-L622) [src/renderer/src/components/message/MessageList.vue682-696](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageList.vue#L682-L696)

 
---

 
## Message Variants

 The message variant system allows assistant messages to have multiple alternative responses. Users can navigate between variants, and the store tracks which variant is selected for each message.

 
### Variant Selection State

 
```

```

 **Selection Tracking**: The `selectedVariantsMap` stores the selected variant ID for each main message. If no entry exists, the main message content is used.

 **Variant Storage**: Variants are stored in the main message's `variants` array and also exist as separate message records in the database with `is_variant: 1`.

 **Sources**: [src/renderer/src/stores/chat.ts112-130](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L112-L130)

 
### Variant Resolution

 The `resolveVariantMessage` method swaps message content when a variant is selected:

 
```

```

 **Deep Copy**: The method creates a deep copy of the main message and replaces its content, usage, and model information with the selected variant's data.

 **Applied in messageItems**: This resolution happens in the `messageItems` computed property, so the UI always receives messages with the correct variant content applied.

 **Sources**: [src/renderer/src/stores/chat.ts259-281](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L259-L281)

 
### Automatic Variant Selection

 When a new variant is generated (via retry), the `MessageItemAssistant` component automatically selects it if the thread is not actively generating:

 
```

```

 **Defer During Generation**: The auto-selection is skipped while the thread is generating to avoid switching variants mid-stream as blocks are added.

 **Sources**: [src/renderer/src/components/message/MessageItemAssistant.vue265-279](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L265-L279)

 
---

 
## Child Threads and Parent Selection

 Child threads are conversations created from selected text in a parent message. The store tracks the relationship between messages and their child threads to enable highlighting and navigation.

 
### Child Thread Mapping

 
```

```

 **Parent Selection Object**: Each child thread stores a `ParentSelection` object containing the selected text, character offsets, and surrounding context for text re-location.

 **Mapping Structure**: The `childThreadsByMessageId` map groups all child threads by their parent message ID, enabling efficient lookup when rendering parent messages.

 **Sources**: [src/renderer/src/stores/chat.ts87](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L87-L87)

 
### Refreshing Child Thread Mappings

 The `refreshChildThreadsForActiveThread` method queries the database for child threads and builds the mapping:

 
```

```

 **Batch Query**: Instead of querying per message, the method sends all message IDs at once and filters the results by parent conversation ID.

 **Called After Load**: This method is invoked after `loadMessages()` completes, ensuring child threads are available for highlighting.

 **Sources**: [src/renderer/src/stores/chat.ts552-575](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L552-L575)

 
### Selection Highlighting and Navigation

 The `MessageList` component uses the `childThreadsByMessageId` mapping to apply highlights to selected text in parent messages, displaying clickable spans that open child threads in new tabs. The highlighting system uses DOM manipulation to wrap selected text ranges with styled `<span>` elements. For details on the highlighting implementation, see [src/renderer/src/components/message/MessageList.vue392-592](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageList.vue#L392-L592)

 **Sources**: [src/renderer/src/components/message/MessageList.vue501-592](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageList.vue#L501-L592)

 
---

 
## Generating Messages and Streaming State

 The `generatingMessagesCacheMap` tracks messages that are actively being generated via streaming responses. These messages may not yet exist in the database but need to appear in the UI immediately.

 
### Generating Messages Cache

 
```

```

 **Skeleton Message**: When sending a message, the store receives a skeleton assistant message from the main process with minimal content. This is cached and its ID is added to `messageIdsMap` (unless it's a variant).

 **Streaming Updates**: As `STREAM_EVENTS.RESPONSE` events arrive, the `handleStreamResponse` method updates the cached message's content blocks directly. The `messageCacheVersion` is bumped to trigger UI updates.

 **Cleanup After Stream End**: When `STREAM_EVENTS.END` arrives, the generating message is removed from the cache and `loadMessages()` is called to load the final, persisted version from the database.

 **Sources**: [src/renderer/src/stores/chat.ts664-703](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L664-L703) [src/renderer/src/stores/chat.ts872-1021](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L872-L1021)

 
### Working Status Tracking

 The `threadsWorkingStatusMap` tracks the generation status for each thread per tab:

 
```

```

 **Per-Tab, Per-Thread**: Each tab maintains a map of thread IDs to their working status, enabling UI indicators like loading spinners or error states in the thread list.

 **Status Transitions**: Status changes from `'none'` → `'working'` when sending a message, then to `'completed'` on success or `'error'` on failure.

 **Sources**: [src/renderer/src/stores/chat.ts42](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L42-L42) [src/renderer/src/stores/chat.ts177-182](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L177-L182)
