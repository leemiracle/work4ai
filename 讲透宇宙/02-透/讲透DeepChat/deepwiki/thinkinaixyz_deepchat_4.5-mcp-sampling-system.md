> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/6.6-mcp-sampling-system](https://deepwiki.com/thinkinaixyz/deepchat/6.6-mcp-sampling-system)（Wayback 快照 2026-02-18）
> DeepWiki deepchat/6.6-mcp-sampling-system

# Thread Creation and Model Selection

  Relevant source files 
 - [src/main/presenter/deeplinkPresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/deeplinkPresenter/index.ts)
 - [src/main/presenter/sqlitePresenter/tables/conversations.ts](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/sqlitePresenter/tables/conversations.ts)
 - [src/renderer/src/components/ChatConfig.vue](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/ChatConfig.vue)
 - [src/renderer/src/components/ChatView.vue](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/ChatView.vue)
 - [src/renderer/src/components/MessageNavigationSidebar.vue](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/MessageNavigationSidebar.vue)
 - [src/renderer/src/components/ModelSelect.vue](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/ModelSelect.vue)
 - [src/renderer/src/components/NewThread.vue](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/NewThread.vue)
 - [src/renderer/src/components/ThreadsView.vue](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/ThreadsView.vue)
 - [src/renderer/src/components/TitleView.vue](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/TitleView.vue)
 - [src/renderer/src/components/message/MessageList.vue](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/message/MessageList.vue)
 - [src/renderer/src/composables/message/useMessageScroll.ts](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/composables/message/useMessageScroll.ts)
 - [src/renderer/src/views/ChatTabView.vue](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/views/ChatTabView.vue)
 
  
## Purpose and Scope

 This document describes the thread creation and model selection system in the NewThread interface. It covers how users create new chat threads, select models from enabled providers, configure chat parameters based on model capabilities, and how the system intelligently defaults model selection based on user history and preferences.

 For information about thread management after creation, see [Thread and Message Management](https://deepwiki.com/thinkinaixyz/deepchat/6.1-thread-and-message-management). For details on message generation within a thread, see [Message Generation and Streaming Flow](https://deepwiki.com/thinkinaixyz/deepchat/6.2-message-generation-and-streaming-flow). For UI components used during active chat sessions, see [Chat UI Components](https://deepwiki.com/thinkinaixyz/deepchat/6.4-chat-ui-components).

 
---

 
## Architecture Overview

 The thread creation system consists of three primary components that work together to provide a model selection and configuration interface before users begin chatting.

 
```

```

 **Sources:** [src/renderer/src/components/NewThread.vue1-568](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/NewThread.vue#L1-L568) [src/renderer/src/components/ModelSelect.vue1-156](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/ModelSelect.vue#L1-L156) [src/renderer/src/components/ChatConfig.vue1-232](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/ChatConfig.vue#L1-L232)

 
---

 
## Component Structure and Responsibilities

 
### NewThread.vue

 The `NewThread` component serves as the primary orchestration point for thread creation. It manages three key responsibilities:

 
| Responsibility | Implementation | Lines |
|---|---|---|
| Model Selection | Maintains activeModel state, handles model updates via handleModelUpdate() | NewThread.vue140-433 |
| Configuration UI | Renders ChatConfig component with reactive parameter bindings | NewThread.vue76-91 |
| Thread Creation | Calls chatStore.createThread() with all settings on send | NewThread.vue521-567 |

 The component structure follows this hierarchy:

 
```

```

 **Sources:** [src/renderer/src/components/NewThread.vue1-97](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/NewThread.vue#L1-L97)

 
---

 
## Model Selection System

 
### Priority-Based Model Initialization

 The model selection system uses a three-tier priority mechanism implemented in `initActiveModel()` to determine the default model when NewThread is displayed:

 
```

```

 The implementation uses several helper functions:

 
| Function | Purpose | Returns |
|---|---|---|
| findEnabledModel(providerId, modelId) | Searches enabledModels for specific model | { model, providerId } or undefined |
| pickFirstEnabledModel() | Finds first Chat or ImageGeneration model | Model object or undefined |
| pickFirstAcpModel() | Finds first ACP provider model | Model object or undefined |
| pickFirstNonAcpModel() | Finds first non-ACP model | Model object or undefined |
| pickModelForMode(mode) | Routes to ACP or non-ACP picker based on mode | Model object or undefined |
| matchesModeProvider(providerId, mode) | Validates provider matches chat mode | boolean |

 **Sources:** [src/renderer/src/components/NewThread.vue221-366](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/NewThread.vue#L221-L366)

 
### Chat Mode Filtering

 The system supports two chat modes that affect which models are displayed and selectable:

 
```

```

 The filtering logic in `ModelSelect.vue`:

 
```

```

 When the user switches modes (via `ChatInput` component's mode selector), `NewThread` automatically switches models:

 
```

```

 **Sources:** [src/renderer/src/components/NewThread.vue266-407](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/NewThread.vue#L266-L407) [src/renderer/src/components/ModelSelect.vue82-121](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/ModelSelect.vue#L82-L121)

 
---

 
## Configuration Parameters

 
### ChatConfig Component Architecture

 The `ChatConfig` component dynamically displays configuration fields based on model capabilities and type detection. It uses three composables to determine field visibility:

 
```

```

 **Sources:** [src/renderer/src/components/ChatConfig.vue1-232](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/ChatConfig.vue#L1-L232)

 
### Parameter Configuration Fields

 The configuration system organizes parameters into three categories via `useChatConfigFields` composable:

 
#### Slider Fields (Always Visible)

 
| Field | Range | Step | Default | Description |
|---|---|---|---|---|
| Temperature | 0.0 - 2.0 | 0.1 | 0.7 | Creativity control |
| Context Length | Model-specific | Varies | 16384 | Input context window |
| Max Tokens | Model-specific | Varies | 4096 | Output length limit |

 
#### Input Fields (Conditional)

 
| Field | Visibility | Validation | Range |
|---|---|---|---|
| Thinking Budget | supportsReasoning | Token count | Model-specific budgetRange |

 The thinking budget field includes validation:

 
```

```

 
#### Select Fields (Conditional)

 
| Field | Visibility | Options | Provider |
|---|---|---|---|
| Reasoning Effort | isGPT5Model | minimal, low, medium, high | OpenAI o1 models |
| Verbosity | providerId === 'gemini' | low, medium, high | Gemini models |

 **Sources:** [src/renderer/src/components/ChatConfig.vue102-127](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/ChatConfig.vue#L102-L127) [src/renderer/src/composables/useChatConfigFields.ts](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/composables/useChatConfigFields.ts)

 
### Model Capability Detection

 The `useModelCapabilities` composable queries model features from the provider database:

 
```

```

 The detection happens reactively:

 
```

```

 When the user changes models in `NewThread`, the configuration automatically reloads defaults:

 
```

```

 **Sources:** [src/renderer/src/components/NewThread.vue189-220](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/NewThread.vue#L189-L220) [src/renderer/src/composables/useModelCapabilities.ts](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/composables/useModelCapabilities.ts)

 
---

 
## Thread Creation Flow

 
### Complete Creation Sequence

 
```

```

 **Sources:** [src/renderer/src/components/NewThread.vue521-567](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/NewThread.vue#L521-L567)

 
### Settings Object Structure

 The thread creation call passes a comprehensive settings object to `SessionPresenter.createThread()`:

 
```

```

 The settings are persisted to the `conversations` table with the following mapping:

 
| Property | Column | Type | Default |
|---|---|---|---|
| providerId | provider_id | TEXT | 'openai' |
| modelId | model_id | TEXT | 'gpt-4' |
| systemPrompt | system_prompt | TEXT | '' |
| temperature | temperature | REAL | 0.7 |
| contextLength | context_length | INTEGER | 4000 |
| maxTokens | max_tokens | INTEGER | 2000 |
| artifacts | artifacts | INTEGER | 0 |
| thinkingBudget | thinking_budget | INTEGER | NULL |
| reasoningEffort | reasoning_effort | TEXT | NULL |
| verbosity | verbosity | TEXT | NULL |
| enabledMcpTools | enabled_mcp_tools | TEXT (JSON) | NULL |
| agentWorkspacePath | agent_workspace_path | TEXT | NULL |
| acpWorkdirMap | acp_workdir_map | TEXT (JSON) | NULL |

 **Sources:** [src/main/presenter/sqlitePresenter/tables/conversations.ts158-225](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/sqlitePresenter/tables/conversations.ts#L158-L225)

 
---

 
## Deeplink Integration

 The thread creation system supports pre-population via the `deepchat://start` protocol, enabling external applications to launch DeepChat with predefined content and settings.

 
### Deeplink Parameters

 
| Parameter | Purpose | Sanitization | Example |
|---|---|---|---|
| msg | Pre-fill message text | sanitizeMessageContent() | ?msg=Hello%20world |
| model | Model ID or partial match | sanitizeStringParameter() | ?model=gpt-4 |
| system | System prompt override | sanitizeStringParameter() | ?system=Be%20helpful |
| mentions | Comma-separated mentions | Split & sanitize each | ?mentions=@file,@web |
| yolo | Auto-send | Disabled for security | N/A |

 
### Deeplink Processing Flow

 
```

```

 **Sources:** [src/main/presenter/deeplinkPresenter/index.ts215-277](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/deeplinkPresenter/index.ts#L215-L277) [src/renderer/src/components/NewThread.vue435-497](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/NewThread.vue#L435-L497)

 
### Deeplink Cache Watcher

 The `NewThread` component watches for deeplink data and applies it with retry logic for the ChatInput reference:

 
```

```

 **Sources:** [src/renderer/src/components/NewThread.vue435-497](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/NewThread.vue#L435-L497)

 
### Security Sanitization

 The deeplink handler implements multiple security layers in `sanitizeMessageContent()` and `sanitizeStringParameter()`:

 
| Protection | Method | Lines |
|---|---|---|
| Length limit | 50KB for messages, 1KB for parameters | deeplinkPresenter577-654 |
| Script tags | Regex pattern matching | deeplinkPresenter585-599 |
| Event handlers | on\w+\s*= pattern | deeplinkPresenter594 |
| Artifact content | Nested XSS in <antArtifact> | deeplinkPresenter609-636 |
| Protocol injection | Remove javascript:, vbscript:, data: | deeplinkPresenter659-661 |
| Auto-send disabled | Removed yolo parameter | deeplinkPresenter253-254 |

 **Sources:** [src/main/presenter/deeplinkPresenter/index.ts567-664](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/deeplinkPresenter/index.ts#L567-L664)

 
---

 
## System Prompt Management

 
### Default System Prompt Loading

 The system prompt field loads from a user-configurable default on component mount:

 
```

```

 The component also listens for changes to the default prompt:

 
```

```

 **Sources:** [src/renderer/src/components/NewThread.vue165-519](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/NewThread.vue#L165-L519)

 
---

 
## Model Store Integration

 
### Enabled Models Structure

 The `modelStore` provides the list of enabled models that appear in the `ModelSelect` component:

 
```

```

 The `ModelSelect` component filters this list based on:

 
 - **Provider enable status** - Only shows `providerStore.sortedProviders` where `enable === true`
 - **Chat mode** - Filters ACP vs non-ACP providers based on `chatMode.currentMode.value`
 - **Model type** - If `type` prop provided, filters models by `ModelType`
 - **Keyword search** - User-typed filter in search box
 
 
```

```

 **Sources:** [src/renderer/src/components/ModelSelect.vue82-133](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/ModelSelect.vue#L82-L133)

 
---

 
## Reactive Model Configuration Updates

 When the user changes the selected model via `handleModelUpdate()`, several reactive effects trigger:

 
```

```

 The watcher implementation at [NewThread.vue189-220](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/NewThread.vue#L189-L220) ensures configuration stays synchronized with the selected model, while also calculating safe defaults like `maxTokens` based on reasoning support.

 **Sources:** [src/renderer/src/components/NewThread.vue189-433](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/NewThread.vue#L189-L433)

 
---

 
## Summary

 The thread creation and model selection system provides:

 
 - **Intelligent Defaults** - Three-tier priority system (recent threads → preferred model → first enabled)
 - **Mode-Aware Filtering** - Automatic model filtering based on chat mode (ACP vs normal)
 - **Capability-Based UI** - Dynamic configuration fields based on model features
 - **Deeplink Support** - External integration with security-sanitized parameters
 - **Persistence** - User preferences and thread settings stored for future sessions
 
 Key components: `NewThread.vue`, `ModelSelect.vue`, `ChatConfig.vue`, `SessionPresenter`, `ConversationsTable`

 Key stores: `chatStore`, `modelStore`, `providerStore`

 Key composables: `useModelCapabilities`, `useModelTypeDetection`, `useThinkingBudget`, `useChatMode`
