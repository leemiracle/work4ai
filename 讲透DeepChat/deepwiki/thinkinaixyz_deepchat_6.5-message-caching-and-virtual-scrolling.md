> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/6.5-message-caching-and-virtual-scrolling](https://deepwiki.com/thinkinaixyz/deepchat/6.5-message-caching-and-virtual-scrolling)（Wayback 快照 2026-03-06）
> DeepWiki deepchat/6.5-message-caching-and-virtual-scrolling

# Message Caching and Virtual Scrolling

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
 
  This document explains the message caching system and virtual scrolling implementation in DeepChat's chat interface. The system manages potentially thousands of messages efficiently by separating message storage from reactive rendering and using virtual scrolling to render only visible messages.

 For information about the overall chat state management and message flow, see [Chat State Management and Message Flow](https://deepwiki.com/thinkinaixyz/deepchat/6.1-thread-and-message-management). For streaming response handling, see [Message Generation and Streaming Flow](https://deepwiki.com/thinkinaixyz/deepchat/6.2-message-generation-and-streaming-flow).

 
---

 
## Overview

 DeepChat's message display system addresses three key challenges:

 
 - **Memory efficiency**: Storing thousands of messages in reactive Vue state causes performance degradation
 - **Rendering performance**: Rendering all messages in the DOM creates excessive nodes and slow scrolling
 - **Loading performance**: Fetching all messages from the database on thread switch causes delays
 
 The solution implements a three-tier architecture:

 
 - **SQLite persistence layer**: Permanent message storage managed by `ThreadPresenter`
 - **Runtime cache layer**: In-memory JavaScript Map storing message objects
 - **Reactive ID layer**: Pinia store maintaining only message IDs with a version counter
 
 Virtual scrolling renders only visible messages plus a buffer zone, with lazy loading fetching messages as the user scrolls.

 
---

 
## Message Caching Architecture

 
### Cache Structure

 The message caching system separates message data from reactive state to minimize Vue's reactivity overhead.

 **Message Runtime Cache Diagram**

 
```

```

 **Sources**: [src/renderer/src/stores/chat.ts1-311](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L1-L311)

 
### Cache Operations

 The chat store provides methods for managing the message cache:

 
| Method | Purpose | Triggers Reactivity |
|---|---|---|
| cacheMessage(message) | Store single message in cache | No |
| cacheMessages(messages) | Store multiple messages | No |
| cacheMessageForView(message) | Cache and bump version | Yes |
| cacheMessagesForView(messages) | Cache batch and bump version | Yes |
| getCachedMessage(messageId) | Retrieve from cache | No |
| hasCachedMessage(messageId) | Check cache presence | No |
| clearCachedMessagesForThread(threadId) | Clear thread messages | No |
| bumpMessageCacheVersion() | Increment version counter | Yes |

 The version counter pattern allows bulk cache updates without triggering reactivity for each individual message, then a single version bump triggers one recomputation of computed properties.

 **Sources**: [src/renderer/src/stores/chat.ts29-39](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L29-L39) [src/renderer/src/stores/chat.ts138-171](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L138-L171)

 
### Message IDs Management

 Each tab maintains its own message ID list:

 
```

```

 The `messageItems` computed property maps IDs to cached messages:

 
```

```

 **MessageListItem** objects contain either a message or null (placeholder), allowing the virtual scroller to reserve space for unloaded messages.

 **Sources**: [src/renderer/src/stores/chat.ts82-83](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L82-L83) [src/renderer/src/stores/chat.ts141-151](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L141-L151) [src/renderer/src/stores/chat.ts283-299](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L283-L299)

 
---

 
## Virtual Scrolling Implementation

 
### DynamicScroller Configuration

 The `MessageList.vue` component uses `vue-virtual-scroller`'s `DynamicScroller` to render only visible messages:

 
```

```

 **Configuration Parameters**:

 
| Parameter | Value | Purpose |
|---|---|---|
| items | chatStore.messageItems | Array of MessageListItem objects |
| min-item-size | 48 | Minimum pixel height for unrendered items |
| buffer | 200 | Pixels of buffer zone above/below viewport |
| key-field | "id" | Unique identifier for each item |
| emit-update | true | Emit update events on scroll |

 **Sources**: [src/renderer/src/components/message/MessageList.vue3-14](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageList.vue#L3-L14)

 
### Item Size Dependencies

 The virtual scroller needs to know when to recalculate item heights. The `DynamicScrollerItem` uses size dependencies:

 
```

```

 **Size Key Computation**:

 
```

```

 The variant size key tracks which variant is selected:

 
```

```

 The rendering state key captures loading/streaming states:

 
```

```

 **Sources**: [src/renderer/src/components/message/MessageList.vue18-26](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageList.vue#L18-L26) [src/renderer/src/components/message/MessageList.vue269-329](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageList.vue#L269-L329)

 
### Message Placeholders

 When a message ID exists but the message isn't in cache, the system renders a placeholder:

 
```

```

 The placeholder height comes from stored DOM info (see [DOM Information Tracking](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/DOM Information Tracking) below).

 **Sources**: [src/renderer/src/components/message/MessageList.vue42-46](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageList.vue#L42-L46) [src/renderer/src/components/message/MessageList.vue357](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageList.vue#L357-L357)

 
---

 
## Lazy Loading and Prefetching

 
### Loading Strategy

 Messages are loaded on-demand using a prefetch buffer strategy:

 **Lazy Loading Flow Diagram**

 
```

```

 **Sources**: [src/renderer/src/stores/chat.ts594-628](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L594-L628) [src/renderer/src/components/message/MessageList.vue682-696](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageList.vue#L682-L696)

 
### Prefetch Configuration

 
```

```

 **Batch Fetching**:

 
```

```

 **Sources**: [src/renderer/src/stores/chat.ts594-628](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L594-L628)

 
### Virtual Update Handler

 The `handleVirtualUpdate` callback is triggered by the DynamicScroller:

 
```

```

 **Sources**: [src/renderer/src/components/message/MessageList.vue682-696](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageList.vue#L682-L696)

 
---

 
## DOM Information Tracking

 
### DOM Info Cache

 The system stores the position and height of rendered messages to:

 
 - Calculate placeholder heights for unloaded messages
 - Restore scroll position accurately
 - Detect height changes for scroll correction
 
 **DOM Info Structure**:

 
```

```

 **Sources**: Inferred from [src/renderer/src/stores/chat.ts29-39](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L29-L39)

 
### Recording DOM Info

 The `recordVisibleDomInfo` function captures DOM positions of all visible messages:

 
```

```

 **Validation Constants**:

 
```

```

 **Sources**: [src/renderer/src/components/message/MessageList.vue628-656](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageList.vue#L628-L656)

 
### Height Change Detection

 A ResizeObserver tracks message height changes to update the virtual scroller:

 
```

```

 **Height Change Tracking**:

 
```

```

 **Sources**: [src/renderer/src/components/message/MessageList.vue194-267](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageList.vue#L194-L267)

 
---

 
## Message Variants and Cache Coordination

 
### Variant Architecture

 Assistant messages can have multiple variants (from retry operations). Only the main message appears in `messageIdsMap`, while variants are stored within the message object or in the generating cache.

 **Variant Storage Diagram**

 
```

```

 **Sources**: [src/renderer/src/stores/chat.ts259-281](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L259-L281) [src/renderer/src/components/message/MessageItemAssistant.vue224-249](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L224-L249)

 
### Variant Resolution

 The `resolveVariantMessage` function swaps the main message content with the selected variant:

 
```

```

 This resolution happens in the `messageItems` computed property, so changing the selected variant triggers a recomputation with the variant's content swapped in.

 **Sources**: [src/renderer/src/stores/chat.ts259-281](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L259-L281)

 
### Generating Messages Cache

 During message generation, skeleton messages are stored in a separate cache to prevent duplication:

 
```

```

 When a variant is being generated:

 
```

```

 **Sources**: [src/renderer/src/stores/chat.ts95-97](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L95-L97) [src/renderer/src/stores/chat.ts183-188](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L183-L188) [src/renderer/src/stores/chat.ts709-743](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L709-L743)

 
### Variant Display in MessageItemAssistant

 The `MessageItemAssistant` component computes all variants including those in the generating cache:

 
```

```

 **Sources**: [src/renderer/src/components/message/MessageItemAssistant.vue224-249](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L224-L249)

 
---

 
## Scroll Position Management

 
### Scroll Composable Architecture

 The `useMessageScroll` composable encapsulates scroll logic:

 **Scroll Management Diagram**

 
```

```

 **Sources**: [src/renderer/src/composables/message/useMessageScroll.ts1-333](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/composables/message/useMessageScroll.ts#L1-L333)

 
### Scroll to Bottom with Retry

 The scroll-to-bottom operation uses a retry mechanism because virtual scroller height calculations may not be complete:

 
```

```

 **Retry Constants**:

 
```

```

 **Sources**: [src/renderer/src/composables/message/useMessageScroll.ts68-143](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/composables/message/useMessageScroll.ts#L68-L143)

 
### Scroll to Message with Retry

 Scrolling to a specific message also uses retries because the virtual scroller may not have rendered the target yet:

 
```

```

 The retry mechanism handles cases where:

 
 - The virtual scroller hasn't rendered the item yet
 - The item is rendered but in a placeholder state
 - Height calculations are still in progress
 
 **Sources**: [src/renderer/src/composables/message/useMessageScroll.ts177-248](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/composables/message/useMessageScroll.ts#L177-L248)

 
### Auto-Follow Behavior

 The system tracks whether the user has manually scrolled up using an IntersectionObserver:

 
```

```

 The `scrollAnchor` is a small div at the bottom of the message list. When it's not intersecting the viewport, the user has scrolled up and auto-follow should be disabled.

 In `MessageList.vue`, this is connected to the `shouldAutoFollow` ref:

 
```

```

 **Sources**: [src/renderer/src/composables/message/useMessageScroll.ts268-291](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/composables/message/useMessageScroll.ts#L268-L291) [src/renderer/src/components/message/MessageList.vue722-731](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageList.vue#L722-L731)
