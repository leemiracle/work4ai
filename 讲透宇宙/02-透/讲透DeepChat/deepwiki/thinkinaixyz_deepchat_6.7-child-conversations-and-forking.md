> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/6.7-child-conversations-and-forking](https://deepwiki.com/thinkinaixyz/deepchat/6.7-child-conversations-and-forking)（Wayback 快照 2026-03-06）
> DeepWiki deepchat/6.7-child-conversations-and-forking

# Child Conversations and Forking

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
 
  
## Purpose and Scope

 This document covers the system for creating branching conversations in DeepChat. The system supports two distinct branching mechanisms:

 
 - **Child Conversations**: Create new threads with parent-child relationships, preserving context from selected text in the parent message
 - **Fork Threads**: Create independent conversation copies that diverge from a specific point in history
 
 For information about general thread and message management, see [Thread and Message Management](https://deepwiki.com/thinkinaixyz/deepchat/6.1-thread-and-message-management). For the message variant system (multiple responses to the same prompt), see [Message Variant System](https://deepwiki.com/thinkinaixyz/deepchat/6.3-message-variant-system).

 
---

 
## Child Conversations Architecture

 Child conversations enable users to explore tangential topics without disrupting the main conversation flow. They maintain a persistent link to their parent message and can include highlighted text selections.

 
### Core Data Structures

 The chat store maintains a map of child threads indexed by parent message ID:

 
```

```

 Each child conversation stores:

 
 - `parentConversationId`: ID of the parent thread
 - `parentMessageId`: ID of the specific message in the parent thread
 - `parentSelection`: Optional text selection data including `selectedText`, `startOffset`, and `endOffset`
 
 [src/renderer/src/stores/chat.ts87-89](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L87-L89)

 
### Child Thread Creation Flow

 
```

```

 **Child Thread Creation Process**

 Sources: [src/renderer/src/stores/chat.ts830-870](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L830-L870)

 The `createChildThreadFromSelection` function in the chat store orchestrates child thread creation:

 
 - **Payload Construction**: Builds a `ParentSelection` object containing the selected text and its position offsets
 - **Title Generation**: Creates a descriptive title combining the parent thread title with a snippet of the selected text (truncated to 48 characters)
 - **Settings Inheritance**: Copies the parent conversation's settings (model, temperature, etc.) to the child
 - **IPC Call**: Invokes `threadP.createChildConversationFromSelection` with `openInNewTab: true`
 - **Refresh**: Updates the child threads map for the current active thread
 
 
```

```

 [src/renderer/src/stores/chat.ts840-846](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L840-L846)

 
### Loading and Caching Child Threads

 Child threads are loaded on-demand and cached per parent message:

 
```

```

 [src/renderer/src/stores/chat.ts552-575](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L552-L575)

 This function:

 
 - Fetches all child conversations for visible message IDs in the current thread
 - Filters out children belonging to other parent conversations
 - Groups children by their parent message ID
 - Updates the reactive map triggering UI updates
 
 Sources: [src/renderer/src/stores/chat.ts552-575](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L552-L575)

 
---

 
## Context Mention System

 When a child thread is created from a text selection, the system automatically prepares a "context mention" that will be inserted into the first message of the child thread. This ensures the AI understands what text the user is referring to.

 
### Context Mention Flow

 
```

```

 **Context Mention Lifecycle**

 Sources: [src/renderer/src/stores/chat.ts577-592](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L577-L592) [src/renderer/src/stores/chat.ts321-341](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L321-L341)

 The `maybeQueueContextMention` function runs after loading messages:

 
```

```

 [src/renderer/src/stores/chat.ts577-592](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L577-L592)

 The context mention is stored in a map keyed by conversation ID:

 
```

```

 [src/renderer/src/stores/chat.ts44-49](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L44-L49) [src/renderer/src/stores/chat.ts88](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L88-L88)

 The label is formatted to be concise (max 48 characters) and normalized:

 
```

```

 [src/renderer/src/stores/chat.ts313-319](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L313-L319)

 Sources: [src/renderer/src/stores/chat.ts313-319](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L313-L319) [src/renderer/src/stores/chat.ts44-49](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L44-L49) [src/renderer/src/stores/chat.ts88](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L88-L88)

 
---

 
## Fork Thread System

 Fork threads create an independent copy of the conversation history up to a specific message. Unlike child conversations, forked threads have no parent relationship and function as completely separate conversations.

 
### Fork vs Child Comparison

 
| Feature | Child Conversation | Fork Thread |
|---|---|---|
| Parent Relationship | Maintains parentConversationId and parentMessageId | No parent relationship |
| History | Starts empty (except context mention) | Copies history up to fork point |
| Context Preservation | Text selection via parentSelection | Full message history |
| Independence | Linked to parent | Fully independent |
| Use Case | Explore tangent while preserving parent | Create alternative path from specific point |
| UI Navigation | Listed under parent message | Appears as separate thread in sidebar |

 
### Fork Thread Creation

 
```

```

 **Fork Thread Creation Flow**

 Sources: [src/renderer/src/stores/chat.ts800-828](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L800-L828) [src/renderer/src/components/message/MessageItemAssistant.vue287-309](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L287-L309)

 The fork operation is initiated from the message toolbar:

 
```

```

 [src/renderer/src/stores/chat.ts800-828](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L800-L828)

 The `forkConversation` IPC call copies:

 
 - All messages up to and including the specified `messageId`
 - Selected variants according to `selectedVariantsMap`
 - Conversation settings (model, temperature, etc.)
 
 The new forked thread is immediately activated, and the UI switches to display it.

 Sources: [src/renderer/src/stores/chat.ts800-828](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L800-L828)

 
### Fork UI Dialog

 The fork action is available in the assistant message toolbar and triggers a confirmation dialog:

 
```

```

 [src/renderer/src/components/message/MessageItemAssistant.vue112-129](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L112-L129)

 The fork action handler in `MessageItemAssistant`:

 
```

```

 [src/renderer/src/components/message/MessageItemAssistant.vue326-386](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L326-L386)

 Sources: [src/renderer/src/components/message/MessageItemAssistant.vue112-129](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L112-L129) [src/renderer/src/components/message/MessageItemAssistant.vue300-309](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L300-L309) [src/renderer/src/components/message/MessageItemAssistant.vue382-383](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L382-L383)

 
---

 
## Navigation Between Threads

 The system provides seamless navigation between parent and child threads with automatic scrolling to relevant content.

 
### Scroll Target Queueing

 When opening a child thread or navigating to a specific message, a scroll target is queued:

 
```

```

 [src/renderer/src/stores/chat.ts51-54](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L51-L54) [src/renderer/src/stores/chat.ts89](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L89-L89)

 Functions for managing scroll targets:

 
```

```

 [src/renderer/src/stores/chat.ts343-355](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L343-L355)

 Sources: [src/renderer/src/stores/chat.ts51-54](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L51-L54) [src/renderer/src/stores/chat.ts89](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L89-L89) [src/renderer/src/stores/chat.ts343-355](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L343-L355)

 
### Opening Threads with Navigation Context

 The `openThreadInNewTab` function accepts options for targeting specific messages or child conversations:

 
```

```

 [src/renderer/src/stores/chat.ts412-428](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L412-L428)

 This enables:

 
 - **Direct Message Navigation**: Opening a thread and scrolling to a specific message
 - **Child Thread Highlighting**: Opening a parent thread and highlighting the child conversation entry point
 
 Sources: [src/renderer/src/stores/chat.ts412-428](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L412-L428)

 
### Thread Activation and Cache Clearing

 When switching between threads, the system clears caches to prevent state leakage:

 
```

```

 [src/renderer/src/stores/chat.ts430-448](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L430-L448)

 This ensures:

 
 - Message caches are cleared per thread
 - Child thread maps are reset
 - Pending context mentions are removed
 - Scroll targets are cleared
 - Variant selection state is reset
 
 Sources: [src/renderer/src/stores/chat.ts430-448](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L430-L448) [src/renderer/src/stores/chat.ts450-473](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L450-L473)

 
---

 
## Text Selection and Highlighting

 When creating a child conversation from a text selection, the parent message can display the highlighted region to show what context was extracted.

 
### ParentSelection Structure

 The `ParentSelection` type captures the selected text and its position:

 
```

```

 This data is stored in the child conversation's `parentSelection` field and used by the UI to render highlights.

 Sources: [src/renderer/src/stores/chat.ts12](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L12-L12)

 
### Selection-Based Child Creation

 When the user selects text and creates a child thread, the selection data flows through:

 
 - **UI captures selection**: User highlights text in `MessageBlockContent`
 - **Store receives selection**: `createChildThreadFromSelection` is called with `ParentSelection`
 - **Database stores selection**: The `parentSelection` field is persisted in the conversations table
 - **UI renders highlight**: When viewing the parent thread, the selection is highlighted in the message
 
 The selection snippet is used to generate a descriptive title:

 
```

```

 [src/renderer/src/stores/chat.ts840-843](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L840-L843)

 And stored in the context mention for the child thread:

 
```

```

 [src/renderer/src/stores/chat.ts590-591](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L590-L591)

 Sources: [src/renderer/src/stores/chat.ts840-843](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L840-L843) [src/renderer/src/stores/chat.ts590-591](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L590-L591)

 
---

 
## State Management Summary

 
### Key State Variables

 
```

```

 **State Management for Child Conversations and Navigation**

 
| State Variable | Type | Purpose |
|---|---|---|
| childThreadsByMessageId | Map<string, CONVERSATION[]> | Caches child conversations grouped by parent message ID |
| pendingContextMentions | Map<string, PendingContextMention> | Stores pending context mentions for empty child threads |
| pendingScrollTargetByConversation | Map<string, PendingScrollTarget> | Queues scroll targets when navigating between threads |

 Sources: [src/renderer/src/stores/chat.ts87-89](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L87-L89)

 
### Lifecycle Integration

 
```

```

 **Thread Loading with Child Conversation Support**

 When a thread is loaded via `setActiveThread()`, the system:

 
 - Calls `loadMessages()` to fetch message IDs and content
 - Invokes `refreshChildThreadsForActiveThread()` to populate child thread map
 - Runs `maybeQueueContextMention()` to prepare context for empty child threads
 - Updates reactive state triggering UI re-renders with child thread links and context mentions
 
 Sources: [src/renderer/src/stores/chat.ts638-662](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L638-L662) [src/renderer/src/stores/chat.ts552-575](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L552-L575) [src/renderer/src/stores/chat.ts577-592](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L577-L592)

 
---

 
## Implementation Notes

 
### Performance Considerations

 
 - **Lazy Loading**: Child threads are only loaded when viewing their parent thread, not on application startup
 - **Batch Fetching**: `listChildConversationsByMessageIds()` fetches all child threads for visible messages in one IPC call
 - **Cache Invalidation**: Child thread maps are cleared when switching conversations to prevent stale data
 
 
### Error Handling

 Both child conversation and fork operations wrap database calls in try-catch blocks:

 
```

```

 [src/renderer/src/stores/chat.ts837-869](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L837-L869)

 The UI components can catch these errors and display appropriate notifications to the user.

 
### Variant Integration

 When forking a thread, the current variant selections are passed to preserve the user's chosen response path:

 
```

```

 [src/renderer/src/stores/chat.ts812-818](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L812-L818)

 This ensures forked threads maintain the same message variants that were selected in the original thread.

 Sources: [src/renderer/src/stores/chat.ts800-828](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L800-L828) [src/renderer/src/stores/chat.ts837-869](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L837-L869)
