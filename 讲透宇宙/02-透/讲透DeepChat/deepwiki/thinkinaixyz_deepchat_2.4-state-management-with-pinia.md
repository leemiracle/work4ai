> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/2.4-state-management-with-pinia](https://deepwiki.com/thinkinaixyz/deepchat/2.4-state-management-with-pinia)（Wayback 快照 2026-03-06）
> DeepWiki deepchat/2.4-state-management-with-pinia

# State Management and Pinia Stores

  Relevant source files 
 - [src/main/lib/scrollCapture.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/lib/scrollCapture.ts)
 - [src/main/lib/system.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/lib/system.ts)
 - [src/main/presenter/configPresenter/aes.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/configPresenter/aes.ts)
 - [src/renderer/src/App.vue](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/App.vue)
 - [src/renderer/src/components/ChatView.vue](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/ChatView.vue)
 - [src/renderer/src/components/MessageNavigationSidebar.vue](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/MessageNavigationSidebar.vue)
 - [src/renderer/src/components/ThreadsView.vue](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/ThreadsView.vue)
 - [src/renderer/src/components/message/MessageItemAssistant.vue](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue)
 - [src/renderer/src/components/message/MessageItemUser.vue](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemUser.vue)
 - [src/renderer/src/components/message/MessageList.vue](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageList.vue)
 - [src/renderer/src/components/message/MessageToolbar.vue](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageToolbar.vue)
 - [src/renderer/src/composables/message/useMessageScroll.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/composables/message/useMessageScroll.ts)
 - [src/renderer/src/stores/chat.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts)
 - [src/renderer/src/stores/language.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/language.ts)
 - [src/renderer/src/views/ChatTabView.vue](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/views/ChatTabView.vue)
 - [src/shared/chat.d.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/shared/chat.d.ts)
 
  
## Purpose and Scope

 This document covers the renderer process state management architecture in DeepChat, which is implemented using Pinia stores. The stores manage UI state, cache data, coordinate with main process presenters via IPC, and handle reactive updates for Vue components. This document focuses on the store layer in the renderer process.

 For IPC communication patterns with the main process, see [Presenter Pattern and IPC Communication](https://deepwiki.com/thinkinaixyz/deepchat/2.1-presenter-pattern-and-ipc-communication). For event handling architecture, see [Event System Architecture](https://deepwiki.com/thinkinaixyz/deepchat/2.2-event-system-architecture). For UI component integration, see [Chat User Interface Components](https://deepwiki.com/thinkinaixyz/deepchat/5.4-message-format-translation).

 
## Store Architecture Overview

 DeepChat uses Pinia as its state management solution, with multiple specialized stores handling different domains of application state. The stores operate exclusively in the renderer process and communicate with main process presenters through IPC.

 **Pinia Store Architecture - Code Entity Map**

 
```

```

 **Sources:** [src/renderer/src/stores/chat.ts61-68](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L61-L68) [src/renderer/src/stores/chat.ts30-39](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L30-L39) [src/renderer/src/components/ChatView.vue98-104](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/ChatView.vue#L98-L104) [src/renderer/src/components/message/MessageList.vue3-14](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageList.vue#L3-L14) [src/renderer/src/components/message/MessageItemAssistant.vue332-393](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L332-L393)

 
## ChatStore Architecture

 The `ChatStore` is the central state management hub for conversation and messaging functionality. It manages thread state, message caching, generation tracking, and coordinates with main process presenters.

 
### State Structure

 **ChatStore State Structure - Code Symbols**

 
```

```

 The store uses a per-tab state pattern, where most state is keyed by `tabId` (obtained via `window.api.getWebContentsId()`) to support multiple tabs with independent conversation contexts. This allows each browser tab to maintain its own active thread, message list, and UI state.

 **Sources:** [src/renderer/src/stores/chat.ts75-148](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L75-L148) [src/renderer/src/stores/chat.ts209-314](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L209-L314)

 
| State Property | Type | Purpose |
|---|---|---|
| activeThreadIdMap | Map<number, string \| null> | Maps tab IDs to active thread IDs |
| threads | Array<{dt: string, dtThreads: CONVERSATION[]}> | Grouped thread list for sidebar display |
| messageIdsMap | Map<number, string[]> | Message ID lists per tab for virtual scrolling |
| generatingThreadIds | Set<string> | Tracks threads currently generating responses |
| threadsWorkingStatusMap | Map<number, Map<string, WorkingStatus>> | Per-thread working status ('working', 'error', 'completed', 'none') |
| generatingMessagesCacheMap | Map<number, Map<string, {message, threadId}>> | Caches messages being generated for real-time updates |
| selectedVariantsMap | Map<string, string> | Maps message IDs to selected variant IDs |

 **Sources:** [src/renderer/src/stores/chat.ts74-96](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L74-L96)

 
### Key Actions and IPC Flow

 **Message Send Flow - IPC and Event Sequence**

 
```

```

 **Sources:** [src/renderer/src/stores/chat.ts644-683](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L644-L683) [src/renderer/src/stores/chat.ts809-1071](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L809-L1071) [src/renderer/src/stores/chat.ts1073-1113](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L1073-L1113)

 
### Core Actions

 
| Action | IPC Call | Purpose |
|---|---|---|
| createThread | threadP.createConversation | Creates new conversation thread with settings |
| setActiveThread | threadP.setActiveConversation | Switches active thread for current tab |
| sendMessage | agentP.sendMessage | Initiates message generation with streaming |
| retryMessage | agentP.retryMessage | Regenerates response for existing message |
| loadMessages | threadP.getMessageIds, threadP.getMessagesByIds | Loads message history for active thread |
| deleteMessage | sessionP.deleteMessage | Deletes message and triggers UI update |
| forkThread | threadP.forkConversation | Creates branch conversation from message |
| renameThread | sessionP.renameConversation | Updates thread title |

 **Sources:** [src/renderer/src/stores/chat.ts341-807](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L341-L807)

 
### Stream Event Handling

 The store handles real-time streaming events from LLM responses:

 
```

```

 The `handleStreamResponse` method [src/renderer/src/stores/chat.ts809-1071](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L809-L1071) processes these events and updates the cached message in real-time, triggering reactive UI updates through `bumpMessageCacheVersion()`.

 **Sources:** [src/renderer/src/stores/chat.ts809-1071](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L809-L1071)

 
## Message Caching System

 DeepChat implements a three-tier caching strategy for optimal performance with large conversation histories:

 **Three-Tier Message Caching Architecture**

 
```

```

 **Sources:** [src/renderer/src/stores/chat.ts30-38](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L30-L38) [src/renderer/src/stores/chat.ts82-83](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L82-L83) [src/renderer/src/stores/chat.ts141-148](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L141-L148) [src/renderer/src/stores/chat.ts286-302](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L286-L302) [src/renderer/src/stores/chat.ts597-625](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L597-L625) [src/renderer/src/components/message/MessageList.vue3-14](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageList.vue#L3-L14) [src/renderer/src/components/message/MessageList.vue628-696](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageList.vue#L628-L696)

 
### Cache Operations Flow

 
```

```

 **Sources:** [src/renderer/src/stores/chat.ts577-611](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L577-L611) [src/renderer/src/stores/chat.ts266-282](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L266-L282)

 
### Cache Invalidation Strategy

 
| Trigger | Action | Scope |
|---|---|---|
| Thread switch | clearCachedMessagesForThread(oldThreadId) | Thread-specific |
| Message delete | deleteCachedMessage(messageId) | Single message |
| Message update | cacheMessageForView(updatedMessage) | Single message |
| Generation complete | Remove from generatingMessagesCache | Single message |
| Tab close | clearThreadCachesForTab(threadId) | Tab-specific |

 **Sources:** [src/renderer/src/stores/chat.ts433-456](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L433-L456)

 
## Message Variant System

 DeepChat supports multiple AI response variants for the same user message, with state management handled through `selectedVariantsMap`:

 **Message Variant Selection System**

 
```

```

 **Sources:** [src/renderer/src/stores/chat.ts130](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L130-L130) [src/renderer/src/stores/chat.ts262-284](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L262-L284) [src/renderer/src/stores/chat.ts286-302](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L286-L302) [src/renderer/src/stores/chat.ts1115-1132](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L1115-L1132) [src/renderer/src/components/message/MessageItemAssistant.vue212-255](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L212-L255) [src/renderer/src/components/message/MessageItemAssistant.vue271-285](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L271-L285) [src/renderer/src/components/message/MessageItemAssistant.vue362-375](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L362-L375)

 
### Variant Selection Flow

 
```

```

 **Sources:** [src/renderer/src/components/message/MessageItemAssistant.vue237-253](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L237-L253) [src/renderer/src/components/message/MessageItemAssistant.vue326-351](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L326-L351)

 
## Store-Component Integration Patterns

 
### Reactive State Access

 Components access store state through computed properties for automatic reactivity:

 
```

```

 **Sources:** [src/renderer/src/components/ChatView.vue81-86](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/ChatView.vue#L81-L86) [src/renderer/src/components/ChatView.vue94-97](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/ChatView.vue#L94-L97)

 
### Store Dependencies

 Stores can depend on each other through direct imports:

 
```

```

 **Sources:** [src/renderer/src/stores/mcp.ts8](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L8-L8)

 
### Component-Store Communication

 
```

```

 **Sources:** [src/renderer/src/components/ChatView.vue98-104](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/ChatView.vue#L98-L104)

 
### Store Getters Pattern

 The ChatStore uses a getter pattern for per-tab state access:

 
```

```

 **Sources:** [src/renderer/src/stores/chat.ts132-187](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L132-L187)

 
## Store-Presenter Communication

 
### IPC Call Pattern

 Stores communicate with main process presenters through the `usePresenter` composable:

 
```

```

 **Sources:** [src/renderer/src/stores/chat.ts61-67](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L61-L67)

 
### Query-Based IPC Pattern (Pinia Colada)

 The `useMcpStore` demonstrates a declarative approach using `useIpcQuery` and `useQuery` from `@pinia/colada`:

 
```

```

 **Sources:** [src/renderer/src/stores/mcp.ts71-96](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L71-L96) [src/renderer/src/stores/mcp.ts371-404](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L371-L404)

 
### Event Subscription Pattern

 Stores subscribe to events from the main process for real-time updates:

 
```

```

 **Sources:** [src/renderer/src/components/ChatView.vue171-174](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/ChatView.vue#L171-L174)

 
### MCP Event Handling

 The `useMcpStore` listens to MCP-specific events for server lifecycle management:

 
```

```

 **Sources:** [src/renderer/src/stores/mcp.ts441-490](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L441-L490)

 
## State Synchronization Patterns

 
### Multi-Tab Synchronization

 DeepChat supports multiple tabs with independent conversation contexts, synchronized through the main process:

 
```

```

 **Sources:** [src/renderer/src/stores/chat.ts74-143](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L74-L143)

 
### Event-Driven State Updates

 The store listens to conversation events and updates local state accordingly:

 
```

```

 **Sources:** [src/renderer/src/stores/chat.ts387-393](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L387-L393)

 
## McpStore Architecture

 The `McpStore` (`useMcpStore`) manages MCP (Model Context Protocol) server state, tool definitions, prompts, and resources. It integrates with `@pinia/colada` for query management and cache invalidation.

 
### State Structure

 **McpStore State and Query Architecture**

 
```

```

 The McpStore uses Pinia Colada's `useQuery` and `useIpcQuery` patterns for declarative IPC-based data fetching with automatic cache management, stale-time control, and query invalidation.

 **Sources:** [src/renderer/src/stores/mcp.ts35-165](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L35-L165)

 
| State Property | Type | Purpose |
|---|---|---|
| config | MCPConfig | Server configurations, default servers, MCP enabled status |
| serverStatuses | Record<string, boolean> | Running status per server |
| serverLoadingStates | Record<string, boolean> | Loading status per server during start/stop |
| toolInputs | Record<string, Record<string, string>> | User inputs for tool parameters |
| toolResults | Record<string, string \| object[]> | Results from tool executions |
| mcpEnabled | computed boolean | Global MCP feature toggle |

 **Sources:** [src/renderer/src/stores/mcp.ts35-56](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L35-L56)

 
### Query Management Pattern

 The McpStore demonstrates advanced query patterns with Pinia Colada:

 
```

```

 **Sources:** [src/renderer/src/stores/mcp.ts71-96](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L71-L96)

 
### State Synchronization with Main Process

 **MCP Server Lifecycle Flow - Event and State Sync**

 
```

```

 The store listens to MCP events for real-time status updates:

 
```

```

 **Sources:** [src/renderer/src/stores/mcp.ts441-490](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L441-L490)

 
### Mutation Pattern with Auto-Invalidation

 The McpStore uses `useIpcMutation` for write operations with automatic cache invalidation:

 
```

```

 **Sources:** [src/renderer/src/stores/mcp.ts171-189](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L171-L189) [src/renderer/src/stores/mcp.ts362-404](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L362-L404)

 
### Conditional Query Enabling

 Queries are conditionally enabled based on MCP status to avoid unnecessary IPC calls:

 
```

```

 **Sources:** [src/renderer/src/stores/mcp.ts90-151](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/mcp.ts#L90-L151)

 
## Other Key Stores

 
### ModelStore

 Manages available LLM models and provider configurations:

 
 - State: `enabledModels`, `modelCapabilities`
 - IPC: Communicates with `configPresenter` for model metadata
 - Used by: `NewThread.vue`, model selection components
 
 
### WorkspaceStore

 Manages workspace/file tree state for agent mode:

 
 - State: `isOpen`, `isAgentMode`, `currentWorkspacePath`, `fileTree`
 - Used by: `ChatView.vue`, `WorkspaceView.vue`
 
 **Sources:** [src/renderer/src/components/ChatView.vue82-86](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/ChatView.vue#L82-L86)

 
### ArtifactStore

 Manages artifact preview state for rich content display:

 
 - State: `isOpen`, `currentArtifact`, `artifacts`
 - Used by: `ArtifactDialog.vue`, `MessageBlockContent.vue`
 
 **Sources:** [src/renderer/src/views/ChatTabView.vue30-31](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/views/ChatTabView.vue#L30-L31)

 
### UISettingsStore

 Manages user interface preferences:

 
 - State: `artifactsEffectEnabled`, `copyWithCotEnabled`, `traceDebugEnabled`
 - Used by: Components for feature toggles
 
 **Sources:** [src/renderer/src/components/message/MessageItemAssistant.vue163](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L163-L163)

 
### ThemeStore

 Manages dark/light theme state:

 
 - State: `isDark`, `theme`
 - Used by: All components for conditional styling
 
 **Sources:** [src/renderer/src/components/message/MessageItemAssistant.vue161](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageItemAssistant.vue#L161-L161)

 
## Performance Optimization Strategies

 
### Cache Version Tracking

 The store uses a `messageCacheVersion` counter to trigger reactive updates efficiently:

 
```

```

 This pattern avoids deep reactivity overhead on large message objects while maintaining fine-grained updates. When the cache changes, only the version number updates, triggering a single computed recalculation.

 **Sources:** [src/renderer/src/stores/chat.ts82](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L82-L82) [src/renderer/src/stores/chat.ts140-173](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L140-L173) [src/renderer/src/stores/chat.ts285-301](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L285-L301)

 
### Batch Prefetching

 Message loading uses batch prefetching to reduce IPC calls:

 
```

```

 **Sources:** [src/renderer/src/stores/chat.ts577-624](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/stores/chat.ts#L577-L624)

 
### Lazy Loading Pattern

 Messages are loaded on-demand as the user scrolls:

 
```

```

 **Sources:** [src/renderer/src/components/message/MessageList.vue578-591](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/renderer/src/components/message/MessageList.vue#L578-L591)

 
```

```
