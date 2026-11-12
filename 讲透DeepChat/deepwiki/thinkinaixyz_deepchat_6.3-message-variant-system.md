> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/6.3-message-variant-system](https://deepwiki.com/thinkinaixyz/deepchat/6.3-message-variant-system)（Wayback 快照 2026-03-06）
> DeepWiki deepchat/6.3-message-variant-system

# Message Variant System

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

 The Message Variant System enables DeepChat to maintain multiple alternative AI responses (variants) for the same user message. This allows users to retry AI generations, receive different responses, and navigate between them without losing any previous responses. Each assistant message can have zero or more variants, and users can switch between them using navigation controls in the message toolbar.

 For information about the overall message generation flow, see page [6.2 Message Generation and Streaming Flow](https://deepwiki.com/thinkinaixyz/deepchat/6.2-message-generation-and-streaming-flow). For details on message rendering components, see page [6.4 Chat UI Components](https://deepwiki.com/thinkinaixyz/deepchat/6.4-chat-ui-components).

 
---

 
## Core Concepts

 
### Main Message and Variants

 Every assistant message has a **main message** (the original or primary response) and an optional array of **variants** (alternative responses). Structurally, variants are themselves `Message` objects with `is_variant` set to `1`, stored in the parent message's `variants` array.

 **Key characteristics:**

 
 - The main message always exists and is displayed by default
 - Variants share the same parent user message
 - Each variant has independent content, usage statistics, and model information
 - Users can navigate between the main message and variants using UI controls
 
 
### Variant Indexing Convention

 The system uses a **0-based indexing** where:

 
 - Index `0` represents the main message
 - Index `1, 2, 3...` represent variants in the `variants` array
 
 Sources: [src/shared/chat.d.ts1-32](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/shared/chat.d.ts#L1-L32) [src/renderer/src/components/message/MessageItemAssistant.vue206-212](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L206-L212)

 
---

 
## Data Model

 
### Message Structure with Variants

 **Diagram: AssistantMessage with variants[] array**

 
```

```

 Each `Message` object in the `variants` array is a complete message with its own metadata:

 
| Field | Type | Description |
|---|---|---|
| is_variant | number | 1 for variants, 0 for main messages |
| content | AssistantMessageBlock[] | Array of content blocks |
| usage | object | Token usage statistics for this specific variant |
| model_id | string | Model identifier that generated this variant |
| model_provider | string | Provider identifier (e.g., 'openai', 'anthropic') |
| model_name | string | Human-readable model name |
| timestamp | number | When this variant was created |
| parentId | string | Reference to parent user message |

 Sources: [src/shared/chat.d.ts3-43](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/shared/chat.d.ts#L3-L43) [src/renderer/src/components/message/MessageItemAssistant.vue225-249](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L225-L249)

 
---

 
## Variant Selection and Tracking

 
### selectedVariantsMap

 The `useChatStore` maintains a reactive `Ref<Record<string, string>>` called `selectedVariantsMap` that tracks which variant is currently selected for each message:

 
```

```

 **Selection semantics:**

 
 - If `messageId` is **not** in the object → display main message (index 0)
 - If `messageId` maps to `null` or empty string → display main message
 - If `messageId` maps to a variant ID → display that variant
 
 Sources: [src/renderer/src/stores/chat.ts127](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L127-L127) [src/renderer/src/stores/chat.ts259-281](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L259-L281)

 
### updateSelectedVariant

 The store provides `updateSelectedVariant(messageId: string, variantId: string | null)` to modify selection state:

 **Diagram: updateSelectedVariant flow**

 
```

```

 The selection is persisted to `CONVERSATION_SETTINGS.selectedVariantsMap` in the SQLite database via `conversationsTable`, ensuring selections survive app restarts.

 Sources: [src/renderer/src/stores/chat.ts1087-1099](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L1087-L1099) [src/renderer/src/components/message/MessageItemAssistant.vue326-370](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L326-L370) [src/renderer/src/components/message/MessageToolbar.vue58-87](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageToolbar.vue#L58-L87)

 
---

 
## Variant Navigation

 
### Toolbar Controls

 The `MessageToolbar` component displays navigation controls when `totalVariants > 1`:

 
| Control | Behavior | Enabled When |
|---|---|---|
| Previous (<) | Navigate to previous variant | currentVariantIndex > 0 |
| Counter | Display N / Total | Always visible with variants |
| Next (>) | Navigate to next variant | currentVariantIndex < totalVariants - 1 |

 **Diagram: Variant navigation state machine**

 
```

```

 Sources: [src/renderer/src/components/message/MessageToolbar.vue58-87](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageToolbar.vue#L58-L87) [src/renderer/src/components/message/MessageItemAssistant.vue326-370](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L326-L370)

 
### currentVariantIndex Computation

 The `MessageItemAssistant` component uses a **computed property** (not local state) to derive the current variant index from `selectedVariantsMap`:

 
```

```

 This design ensures the UI always reflects the authoritative state in the store, eliminating race conditions. The computed property reactively updates when `selectedVariantsMap` changes.

 Sources: [src/renderer/src/components/message/MessageItemAssistant.vue206-212](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L206-L212)

 
---

 
## Variant Resolution System

 
### resolveVariantMessage Function

 When rendering messages, the store's `resolveVariantMessage` function determines which message content to display:

 
```

```

 **Implementation details:**

 
 - Non-destructive: Creates a shallow copy with replaced fields
 - Replaces: `content`, `usage`, `model_id`, `model_provider`, `model_name`
 - Preserves: `id` (main message ID), `timestamp`, `role`, etc.
 
 Sources: [src/renderer/src/stores/chat.ts259-281](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L259-L281)

 
### messageItems and variantAwareMessages

 The store provides two computed properties that apply variant resolution:

 **messageItems:**

 
```

```

 **variantAwareMessages:**

 
```

```

 These computed properties are consumed by `MessageList.vue` for rendering.

 Sources: [src/renderer/src/stores/chat.ts283-305](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L283-L305)

 
---

 
## Variant Generation

 
### Creating New Variants

 New variants are generated through three main actions:

 
| Action | Store Method | Description |
|---|---|---|
| Retry | retryMessage(messageId) | Regenerate from the assistant message |
| Regenerate | regenerateFromUserMessage(userMsgId) | Regenerate from parent user message |
| Manual regeneration | User clicks retry in toolbar | Triggers one of the above |

 **Diagram: retryMessage variant generation flow**

 
```

```

 Sources: [src/renderer/src/stores/chat.ts705-751](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L705-L751) [src/renderer/src/stores/chat.ts872-1166](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L872-L1166)

 
### Auto-Switching to New Variants

 The `MessageItemAssistant` component watches `allVariants.value.length` to detect new variants:

 
```

```

 **Behavior:**

 
 - Only triggers when `newLength > oldLength` (new variant added, not removed)
 - Waits until generation is complete: `!generatingThreadIds.has(currentThreadId)`
 - Automatically switches to the newly created variant (last in array)
 - Persists the selection via `updateSelectedVariant`
 - No action if variant is deleted or list shrinks
 
 Sources: [src/renderer/src/components/message/MessageItemAssistant.vue265-279](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L265-L279)

 
---

 
## UI Integration

 
### MessageItemAssistant Component

 The `MessageItemAssistant.vue` component orchestrates variant display and navigation:

 **Key computed properties:**

 
| Property | Purpose |
|---|---|
| currentVariantIndex | Derives index from selectedVariantsMap |
| allVariants | Combines persisted variants with generating variants from cache |
| totalVariants | Count of all variants + 1 (main message) |
| currentMessage | The message to display (main or selected variant) |
| currentContent | Content blocks of the current message |

 **Diagram: MessageItemAssistant computed property dependency graph**

 
```

```

 Sources: [src/renderer/src/components/message/MessageItemAssistant.vue206-262](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L206-L262) [src/renderer/src/components/message/MessageToolbar.vue294-311](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageToolbar.vue#L294-L311)

 
### Handling Navigation Actions

 Navigation is handled through a centralized `handleAction` function in `MessageItemAssistant`:

 
```

```

 This ensures navigation follows the **unidirectional data flow** pattern: UI events → store updates → reactive re-renders.

 Sources: [src/renderer/src/components/message/MessageItemAssistant.vue326-387](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L326-L387)

 
---

 
## Variant-Aware Operations

 
### Message Operations with Variants

 When performing operations on messages with variants, the system respects the current selection:

 **sendMessage passes selectedVariantsMap:**

 
```

```

 **retryMessage passes selectedVariantsMap:**

 
```

```

 **forkConversation passes selectedVariantsMap:**

 
```

```

 This ensures that when creating new messages or branches, the conversation context includes the currently selected variants, not just the main messages. The backend uses this map to build the correct message history for LLM context.

 Sources: [src/renderer/src/stores/chat.ts664-703](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L664-L703) [src/renderer/src/stores/chat.ts705-751](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L705-L751) [src/renderer/src/stores/chat.ts799-828](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L799-L828)

 
---

 
## Lifecycle and State Management

 
### Clearing Variant State

 When switching threads or clearing the active thread, variant selection state is reset:

 
```

```

 This prevents variant selections from one conversation from affecting another. The empty object ensures no variants are selected in the new thread until explicitly chosen.

 Sources: [src/renderer/src/stores/chat.ts430-448](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L430-L448)

 
### Loading Variant State

 When activating a thread, variant selections are restored from `CONVERSATION_SETTINGS.selectedVariantsMap`:

 **Diagram: Loading variant selections from database**

 
```

```

 The `selectedVariantsMap` is stored as a JSON field in the `conversations` table's `context_chain` column (serialized as part of settings), ensuring selections persist across app restarts.

 Sources: [src/renderer/src/stores/chat.ts1312-1341](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L1312-L1341)

 
---

 
## Summary

 The Message Variant System provides a robust mechanism for managing multiple AI response alternatives:

 
 - **Data Model**: Variants stored as nested `Message` objects with `is_variant=1`
 - **Selection Tracking**: Global `selectedVariantsMap` maintained in `chatStore`
 - **Navigation**: UI controls in `MessageToolbar` for switching between variants
 - **Resolution**: `resolveVariantMessage` determines which content to display
 - **Auto-Switching**: New variants automatically become active after generation
 - **Persistence**: Selections saved to database and restored on thread activation
 - **Context Preservation**: Variant selections passed to backend for consistent conversation context
 
 This architecture enables users to explore different AI responses without losing previous attempts, supporting iterative refinement and comparison of model outputs.
