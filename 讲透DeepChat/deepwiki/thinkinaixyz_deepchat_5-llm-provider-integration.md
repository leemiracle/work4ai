> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/5-llm-provider-integration](https://deepwiki.com/thinkinaixyz/deepchat/5-llm-provider-integration)（Wayback 快照 2025-10-13）
> DeepWiki deepchat/5-llm-provider-integration

# Chat and Conversation System

  Relevant source files 
 - [src/main/presenter/deeplinkPresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/deeplinkPresenter/index.ts)
 - [src/main/presenter/proxyConfig.ts](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/proxyConfig.ts)
 - [src/main/presenter/sqlitePresenter/tables/conversations.ts](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/sqlitePresenter/tables/conversations.ts)
 - [src/main/presenter/threadPresenter/contentEnricher.ts](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/contentEnricher.ts)
 - [src/main/presenter/threadPresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/index.ts)
 - [src/main/presenter/threadPresenter/searchManager.ts](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/searchManager.ts)
 - [src/renderer/src/assets/llm-icons/tokenflux-color.svg](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/assets/llm-icons/tokenflux-color.svg)
 - [src/renderer/src/components/ChatView.vue](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/components/ChatView.vue)
 - [src/renderer/src/components/MessageNavigationSidebar.vue](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/components/MessageNavigationSidebar.vue)
 - [src/renderer/src/components/NewThread.vue](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/components/NewThread.vue)
 - [src/renderer/src/components/ThreadsView.vue](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/components/ThreadsView.vue)
 - [src/renderer/src/components/TitleView.vue](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/components/TitleView.vue)
 - [src/renderer/src/components/message/MessageItemAssistant.vue](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/components/message/MessageItemAssistant.vue)
 - [src/renderer/src/components/message/MessageList.vue](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/components/message/MessageList.vue)
 - [src/renderer/src/stores/chat.ts](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/stores/chat.ts)
 - [src/renderer/src/views/ChatTabView.vue](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/views/ChatTabView.vue)
 - [src/shared/chat.d.ts](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/shared/chat.d.ts)
 
  
## Purpose and Scope

 The Chat and Conversation System manages the core chat functionality of DeepChat, including conversation lifecycle management, message creation and streaming, conversation storage, and the UI components for displaying and interacting with chat threads. This system coordinates between the main process (via `ThreadPresenter`) and the renderer process (via `chatStore`) to provide a seamless chat experience.

 For LLM provider integration and streaming details, see [LLM Provider Integration](https://deepwiki.com/thinkinaixyz/deepchat/4-llm-provider-integration). For MCP tool integration within conversations, see [Model Context Protocol (MCP)](https://deepwiki.com/thinkinaixyz/deepchat/6-model-context-protocol-(mcp)). For file handling in messages, see [File Handling System](https://deepwiki.com/thinkinaixyz/deepchat/7-file-handling-system).

 **Sources:** [src/main/presenter/threadPresenter/index.ts1-114](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/index.ts#L1-L114) [src/renderer/src/stores/chat.ts1-50](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/stores/chat.ts#L1-L50)

 
---

 
## System Architecture

 The conversation system follows a presenter-store pattern with SQLite persistence:

 
```

```

 **Diagram: High-Level Chat System Architecture**

 The system is organized into three layers:

 
 - **Renderer Process**: UI components and local state management
 - **Main Process**: Business logic, orchestration, and external integrations
 - **Data Layer**: SQLite database for persistent storage
 
 **Sources:** [src/main/presenter/threadPresenter/index.ts77-114](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/index.ts#L77-L114) [src/renderer/src/stores/chat.ts22-50](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/stores/chat.ts#L22-L50) [src/renderer/src/views/ChatTabView.vue1-46](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/views/ChatTabView.vue#L1-L46)

 
---

 
## Conversation Management

 
### Conversation Lifecycle

 
```

```

 **Diagram: Conversation State Machine**

 Conversations in DeepChat follow this lifecycle:

 
| State | Description | Persisted Field |
|---|---|---|
| Empty | No active conversation, showing NewThread.vue | activeThreadId = null |
| Creating | First message sent, conversation being created | is_new = 1 |
| Active | Conversation exists with messages | is_new = 0 |
| Generating | AI response is being generated | Tracked in generatingThreadIds Set |
| Pinned | User has pinned the conversation | is_pinned = 1 |
| Forked | Conversation branched from another | New conv_id with copied messages |

 **Sources:** [src/main/presenter/threadPresenter/index.ts999-1079](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/index.ts#L999-L1079) [src/renderer/src/stores/chat.ts152-174](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/stores/chat.ts#L152-L174)

 
### Creating a Conversation

 
```

```

 **Diagram: Conversation Creation Flow**

 The creation process includes several optimizations:

 
 - **Empty conversation singleton**: If the latest conversation has no messages, it's reused instead of creating a new one
 - **Settings inheritance**: New conversations inherit settings from the previous conversation (except system prompt and model-specific parameters)
 - **Tab binding**: Each conversation is bound to a specific tab ID to support multi-tab workflows
 
 **Sources:** [src/main/presenter/threadPresenter/index.ts999-1079](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/index.ts#L999-L1079) [src/renderer/src/stores/chat.ts162-174](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/stores/chat.ts#L162-L174) [src/renderer/src/components/NewThread.vue457-476](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/components/NewThread.vue#L457-L476)

 
### Conversation Settings

 Conversation settings are stored in the `conversations` table and control the behavior of AI generation:

 
| Setting | Type | Description | Default |
|---|---|---|---|
| modelId | string | Selected model identifier | 'gpt-4' |
| providerId | string | LLM provider identifier | 'openai' |
| systemPrompt | string | System instruction for the model | '' |
| temperature | number | Randomness of responses (0-2) | 0.7 |
| contextLength | number | Maximum context window size | Model default |
| maxTokens | number | Maximum response length | Model default |
| artifacts | 0 \| 1 | Enable artifacts feature | 0 |
| thinkingBudget | number \| null | Thinking budget for Gemini/Qwen3 | null |
| reasoningEffort | string \| null | Reasoning effort for GPT/Grok | null |
| verbosity | string \| null | Response verbosity for GPT-5 | null |
| enableSearch | boolean \| null | Enable web search integration | null |
| forcedSearch | boolean \| null | Force search for every message | null |
| searchStrategy | 'turbo' \| 'max' \| null | Search result quantity strategy | null |
| enabledMcpTools | string[] | MCP tools enabled for this conversation | [] |
| selectedVariantsMap | Record<string, string> | Tracks selected message variants | {} |

 **Sources:** [src/main/presenter/sqlitePresenter/tables/conversations.ts6-28](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/sqlitePresenter/tables/conversations.ts#L6-L28) [src/main/presenter/threadPresenter/index.ts1020-1062](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/index.ts#L1020-L1062)

 
### SQLite Schema

 The `conversations` table schema:

 
```

```

 **Key Features:**

 
 - `conv_id` uses `nanoid()` for unique, URL-safe identifiers
 - `context_chain` stores the `selectedVariantsMap` for message variant tracking
 - Indexes optimize conversation list queries (sorted by `updated_at`)
 
 **Sources:** [src/main/presenter/sqlitePresenter/tables/conversations.ts44-123](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/sqlitePresenter/tables/conversations.ts#L44-L123)

 
---

 
## Message Management

 
### Message Types and Structure

 DeepChat uses TypeScript discriminated unions for type-safe message handling:

 
```

```

 Assistant messages use a **block-based content structure** for rich rendering:

 
| Block Type | Description | Example Use Case |
|---|---|---|
| content | Plain text or markdown content | Model response text |
| reasoning_content | Chain-of-thought reasoning (o1 models) | Thinking process display |
| tool_call | MCP tool execution details | Function call with params/response |
| action | System actions and permissions | Tool permission requests, rate limits |
| search | Web search results | Pages found and processed |
| image | Generated images | DALL-E, Imagen outputs |
| error | Error messages | API failures, validation errors |

 **Sources:** [src/shared/chat.d.ts3-138](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/shared/chat.d.ts#L3-L138) [src/main/presenter/threadPresenter/index.ts19-32](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/index.ts#L19-L32)

 
### Message Creation Flow

 
```

```

 **Diagram: Message Creation and Preparation Flow**

 The message creation process is split into two phases:

 
 - **User message creation**: Immediately persisted to SQLite
 - **Assistant message creation**: Empty shell created, then populated via streaming
 
 **Sources:** [src/main/presenter/threadPresenter/index.ts1238-1308](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/index.ts#L1238-L1308) [src/renderer/src/stores/chat.ts282-311](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/stores/chat.ts#L282-L311)

 
### Message Generation Lifecycle (Streaming)

 
```

```

 **Diagram: Streaming Message Generation Lifecycle**

 The streaming system uses a **dual-update strategy**:

 
 - **Database persistence**: Every content update is immediately written to SQLite
 - **Cache-based reactivity**: The renderer maintains a `generatingMessagesCache` that updates on stream events, triggering Vue reactivity without re-querying the database
 
 This approach ensures:

 
 - **Data durability**: Content is never lost, even if the app crashes mid-stream
 - **UI responsiveness**: Real-time updates without database polling
 - **Recovery**: Unfinished messages are detected on startup and marked as errors
 
 **Sources:** [src/main/presenter/threadPresenter/index.ts148-321](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/index.ts#L148-L321) [src/main/presenter/threadPresenter/index.ts578-932](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/index.ts#L578-L932) [src/renderer/src/stores/chat.ts391-651](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/stores/chat.ts#L391-L651)

 
### Adaptive Content Buffering

 For large responses (especially those containing base64-encoded images), `ThreadPresenter` implements adaptive buffering:

 
```

```

 When `shouldSplitContent(content)` returns true (content > 8KB or contains base64 images > 5KB):

 
 - Content is split into smaller chunks (512 bytes for images, 4KB otherwise)
 - Chunks are processed asynchronously in batches of 5
 - Each batch yields to the event loop via `setImmediate()` to prevent UI blocking
 
 **Sources:** [src/main/presenter/threadPresenter/index.ts42-75](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/index.ts#L42-L75) [src/main/presenter/threadPresenter/index.ts390-522](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/index.ts#L390-L522)

 
### Message Variants and Regeneration

 DeepChat supports **message variants** - alternative responses to the same user message:

 
```

```

 **Diagram: Message Variant Structure**

 Variants are created when:

 
 - User clicks "Retry" on an assistant message
 - User clicks "Regenerate" on a user message
 - Multiple responses are needed for comparison
 
 The `selectedVariantsMap` in conversation settings tracks which variant is currently displayed:

 
```

```

 **Sources:** [src/renderer/src/stores/chat.ts115-150](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/stores/chat.ts#L115-L150) [src/renderer/src/components/message/MessageItemAssistant.vue164-239](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/components/message/MessageItemAssistant.vue#L164-L239) [src/main/presenter/threadPresenter/index.ts1405-1485](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/index.ts#L1405-L1485)

 
---

 
## UI Components

 
### NewThread Component

 `NewThread.vue` is the landing page when no conversation is active:

 
| Feature | Implementation | Purpose |
|---|---|---|
| Model Selection | ModelSelect in popover | Choose LLM before starting |
| Configuration Panel | ChatConfig in scrollable popover | Set temperature, context, system prompt, etc. |
| Preferred Model Memory | configPresenter.getSetting('preferredModel') | Remembers last-used model |
| Deeplink Integration | Watches chatStore.deeplinkCache | Handles deepchat://start URLs |
| Auto-initialization | initActiveModel() on mount | Selects from recent conversations or default |

 The component implements smart model selection logic:

 
 - Check most recent conversation (pinned or normal) for model
 - Fall back to user's saved `preferredModel` setting
 - Fall back to first enabled model in settings
 
 **Sources:** [src/renderer/src/components/NewThread.vue140-432](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/components/NewThread.vue#L140-L432)

 
### ChatView Component

 `ChatView.vue` is the active conversation interface:

 
```
┌─────────────────────────────────────┐
│          TitleView                  │  ← Sidebar toggle, message navigation
├─────────────────────────────────────┤
│                                     │
│          MessageList                │  ← Scrollable message history
│                                     │
│                                     │
├─────────────────────────────────────┤
│         PromptInput                 │  ← Chat input with file upload
└─────────────────────────────────────┘
```

 The component:

 
 - Listens to `STREAM_EVENTS` (RESPONSE, END, ERROR) via IPC
 - Delegates to `chatStore.handleStreamResponse()` for cache updates
 - Auto-scrolls to bottom when new messages arrive (unless user scrolled up)
 - Disables input during generation (`isGenerating` computed property)
 
 **Sources:** [src/renderer/src/components/ChatView.vue1-123](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/components/ChatView.vue#L1-L123)

 
### MessageList Component

 `MessageList.vue` renders the conversation history with advanced features:

 **Key Features:**

 
| Feature | Description |
|---|---|
| Infinite Scroll Detection | IntersectionObserver on scroll anchor |
| Message Highlighting | CSS animation on scroll-to-message |
| Screenshot Capture | usePageCapture for message-to-image |
| Scroll Restoration | Maintains scroll position during content updates |
| Cancel Generation | Button visible when generatingThreadIds.has(threadId) |
| Message Minimap | MessageMinimap for navigation in long conversations |

 **Screenshot Feature:**

 
 - `calculateMessageGroupRect()`: Captures user + assistant message pair
 - `calculateFromTopToCurrentRect()`: Captures all messages from top to selected
 - Adds watermark with app version, model info, and branding
 
 **Sources:** [src/renderer/src/components/message/MessageList.vue1-523](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/components/message/MessageList.vue#L1-L523)

 
### ThreadsView Component

 `ThreadsView.vue` displays the conversation sidebar with virtual scrolling:

 
```

```

 The component uses `vue-virtual-scroller` for performance with 1000+ conversations:

 
 - `DynamicScroller` with `min-item-size: 30`
 - Lazy loading via `handleScrollEnd()` → `threadP.loadMoreThreads()`
 - Grouped by date with computed `flattenedThreads`
 
 **Conversation Item Actions:**

 
 - Click: Switch to conversation
 - Right-click context menu: Rename, Delete, Clean Messages, Pin/Unpin
 - Drag to reorder (pinned conversations only)
 
 **Sources:** [src/renderer/src/components/ThreadsView.vue1-373](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/components/ThreadsView.vue#L1-L373)

 
---

 
## Advanced Features

 
### Search Integration

 The search system enriches AI responses with real-time web content:

 
```

```

 **Diagram: Search Integration Flow**

 The search system operates in the main process using headless browser windows:

 
 - **Engine Configuration**: `SearchEngineTemplate` defines selectors for each engine ([src/main/presenter/threadPresenter/searchManager.ts63-210](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/searchManager.ts#L63-L210))
 - **Result Extraction**: JavaScript executed in browser context extracts titles, URLs, descriptions, and favicons
 - **Content Enrichment**: `ContentEnricher` fetches actual page content using axios + cheerio ([src/main/presenter/threadPresenter/contentEnricher.ts98-124](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/contentEnricher.ts#L98-L124))
 - **Context Injection**: Results formatted using `SEARCH_PROMPT_TEMPLATE` and added to messages
 
 **Search Engines Supported:**

 
 - Google (`#search .MjjYud`)
 - Bing (`#b_results h2`)
 - Baidu (`#content_left .result`)
 - DuckDuckGo (`article.yQDlj3B5DI5YO8c8Ulio`)
 - Google Scholar (`#gs_res_ccl .gs_r`)
 - Baidu Xueshu (`#bdxs_result_lists`)
 - Sogou Weixin (`weixin.sogou.com`)
 
 Search can be:

 
 - **Per-message**: Enabled via toggle in `ChatInput`
 - **Per-conversation**: Set `enableSearch: true` in conversation settings
 - **Forced**: Set `forcedSearch: true` to search every message
 - **Strategy-based**: `'turbo'` (3 results) or `'max'` (10 results)
 
 **Sources:** [src/main/presenter/threadPresenter/searchManager.ts249-600](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/searchManager.ts#L249-L600) [src/main/presenter/threadPresenter/contentEnricher.ts1-262](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/contentEnricher.ts#L1-L262) [src/main/presenter/threadPresenter/index.ts1282-1299](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/index.ts#L1282-L1299)

 
### Fork Functionality

 Forking creates a new conversation from a specific message in an existing conversation:

 
```

```

 **Diagram: Fork Conversation Flow**

 **Fork Behavior:**

 
 - **Respects Variant Selection**: Uses `selectedVariantsMap` to determine which variant of each message to copy
 - **Preserves Attachments**: Copies search results, file attachments, and metadata
 - **Inherits Settings**: New conversation gets same model, temperature, etc.
 - **Title Formatting**: Appends `(fork)` or custom tag to original title
 
 **Use Cases:**

 
 - Explore alternative responses without losing original conversation
 - Create specialized conversations from general discussions
 - Branch discussions at decision points
 
 **Sources:** [src/renderer/src/stores/chat.ts362-389](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/stores/chat.ts#L362-L389) [src/main/presenter/threadPresenter/index.ts1681-1779](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/index.ts#L1681-L1779) [src/renderer/src/components/message/MessageItemAssistant.vue247-269](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/components/message/MessageItemAssistant.vue#L247-L269)

 
### Deep Link Support

 The `DeeplinkPresenter` handles `deepchat://` protocol URLs for conversation automation:

 **Supported Commands:**

 
| Command | Parameters | Example |
|---|---|---|
| start | msg, model, system, mentions | deepchat://start?msg=Hello&model=gpt-4 |
| mcp/install | json (base64-encoded) | deepchat://mcp/install?json=eyJtY3BTZXZlcnMi... |

 **Start Command Flow:**

 
 - Parse URL parameters and sanitize for security
 - Ensure a chat tab is active (create if needed)
 - Wait for tab renderer to be ready (`TAB_EVENTS.RENDERER_TAB_READY`)
 - Broadcast `DEEPLINK_EVENTS.START` to target tab
 - `NewThread.vue` watches `chatStore.deeplinkCache` and populates input
 
 **Security Features:**

 
 - `sanitizeMessageContent()`: Strips HTML tags, normalizes whitespace
 - `sanitizeStringParameter()`: Validates string inputs
 - Auto-send disabled by default (was controlled by `yolo` param, now removed for security)
 
 **Sources:** [src/main/presenter/deeplinkPresenter/index.ts1-333](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/deeplinkPresenter/index.ts#L1-L333) [src/renderer/src/components/NewThread.vue357-419](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/components/NewThread.vue#L357-L419)

 
### Message Navigation Sidebar

 `MessageNavigationSidebar.vue` provides quick navigation for long conversations:

 **Features:**

 
| Feature | Implementation |
|---|---|
| Search | Full-text search across all message content |
| Context Preview | Shows 30 chars before/after match |
| Syntax Highlighting | Highlights search terms in results |
| Role Indicators | Icons for user vs. assistant messages |
| Timestamp Display | Relative time formatting |
| Scroll Sync | Highlights active message |

 **Search Implementation:**

 
```

```

 **Sources:** [src/renderer/src/components/MessageNavigationSidebar.vue1-262](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/components/MessageNavigationSidebar.vue#L1-L262)

 
---

 
## State Synchronization

 The chat system maintains consistency across tabs and windows through event-driven synchronization:

 **Key State Management Patterns:**

 
```

```

 **Synchronization Events:**

 
| Event | Source | Purpose |
|---|---|---|
| CONVERSATION_EVENTS.ACTIVATED | ThreadPresenter | Notify UI of conversation switch |
| CONVERSATION_EVENTS.MESSAGE_GENERATED | ThreadPresenter | Broadcast completed message |
| CONVERSATION_EVENTS.THREADS_UPDATED | ThreadPresenter | Refresh conversation list |
| TAB_EVENTS.TITLE_UPDATED | ThreadPresenter | Update tab title with conversation name |
| STREAM_EVENTS.RESPONSE | LLMProviderPresenter | Real-time token streaming |
| STREAM_EVENTS.END | ThreadPresenter | Generation complete |
| STREAM_EVENTS.ERROR | ThreadPresenter | Generation failed |

 **Conversation Deletion Orchestration:**

 When a conversation is deleted, `ThreadPresenter` orchestrates:

 
 - Check if conversation is active in any tab
 - If active, clear that tab's state and show empty `NewThread`
 - Broadcast `CONVERSATION_EVENTS.THREADS_UPDATED` to all windows
 - UI updates conversation list reactively
 
 This ensures no orphaned references exist after deletion.

 **Sources:** [src/main/presenter/threadPresenter/index.ts102-132](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/index.ts#L102-L132) [src/renderer/src/stores/chat.ts84-109](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/stores/chat.ts#L84-L109) [src/main/presenter/threadPresenter/index.ts1081-1092](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/index.ts#L1081-L1092)

 
---

 
## Error Handling and Recovery

 The system implements comprehensive error handling:

 **Unfinished Message Recovery:**

 On application startup, `MessageManager.initializeUnfinishedMessages()` finds any messages with `status = 'pending'` and marks them as errors:

 
```

```

 **Streaming Error Handling:**

 When `handleLLMAgentError()` is called:

 
 - Flush any remaining buffered content
 - Call `messageManager.handleMessageError(eventId, error)`
 - Add error block to message content
 - Update message status to `'error'`
 - Broadcast `STREAM_EVENTS.ERROR` to UI
 - Remove from `generatingMessages` Map
 - UI displays retry button
 
 **Database Constraint Violations:**

 The `conv_id` unique constraint prevents duplicate conversations. If a race condition occurs, the second attempt fails gracefully and reuses the existing conversation.

 **Sources:** [src/main/presenter/threadPresenter/index.ts148-164](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/index.ts#L148-L164) [src/main/presenter/threadPresenter/messageManager.ts83-111](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/messageManager.ts#L83-L111) [src/renderer/src/stores/chat.ts726-797](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/stores/chat.ts#L726-L797)

 
---

 
## Performance Optimizations

 
### Virtual Scrolling

 `ThreadsView` and `MessageList` use different strategies for performance:

 **ThreadsView:** Virtual scrolling via `vue-virtual-scroller`

 
 - Only renders visible conversation items + buffer
 - Dynamic item sizing based on content
 - Handles 10,000+ conversations without performance degradation
 
 **MessageList:** Standard scrolling with selective rendering

 
 - Messages are typically < 100 per conversation
 - Full render for search/scroll-to-message features
 - Intersection observer for scroll-to-bottom detection
 
 
### Caching Strategy

 The renderer maintains multiple caches:

 
```

```

 This multi-level caching avoids:

 
 - Repeated database queries during streaming
 - Full re-fetches when switching tabs
 - Status polling for generation progress
 
 **Sources:** [src/renderer/src/stores/chat.ts39-109](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/stores/chat.ts#L39-L109) [src/renderer/src/components/ThreadsView.vue28-69](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/components/ThreadsView.vue#L28-L69)

 
### Adaptive Content Processing

 Large content (images, long text) uses chunked processing to prevent UI blocking:

 
 - Detect large content: `shouldSplitContent(content)` checks size and base64 presence
 - Split into chunks: 512 bytes for images, 4KB for text
 - Process in batches: 5 chunks per batch
 - Yield to event loop: `setImmediate()` between batches
 - Stream to renderer: Progressive updates maintain responsiveness
 
 **Sources:** [src/main/presenter/threadPresenter/index.ts390-522](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/index.ts#L390-L522)

 
---

 **Full System Sources:**

 
 - [src/main/presenter/threadPresenter/index.ts1-2037](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/threadPresenter/index.ts#L1-L2037)
 - [src/renderer/src/stores/chat.ts1-1056](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/stores/chat.ts#L1-L1056)
 - [src/main/presenter/sqlitePresenter/tables/conversations.ts1-316](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/main/presenter/sqlitePresenter/tables/conversations.ts#L1-L316)
 - [src/shared/chat.d.ts1-163](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/shared/chat.d.ts#L1-L163)
 - [src/renderer/src/components/ChatView.vue1-124](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/components/ChatView.vue#L1-L124)
 - [src/renderer/src/components/message/MessageList.vue1-524](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/components/message/MessageList.vue#L1-L524)
 - [src/renderer/src/components/NewThread.vue1-489](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/components/NewThread.vue#L1-L489)
 - [src/renderer/src/components/ThreadsView.vue1-374](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/components/ThreadsView.vue#L1-L374)
 - [src/renderer/src/views/ChatTabView.vue1-212](https://github.com/thinkinaixyz/deepchat/blob/d1073a0e/src/renderer/src/views/ChatTabView.vue#L1-L212)
