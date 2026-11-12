<!-- source: DeepWiki mcp.deepwiki.com · repo cline/cline · page 6 VS Code Webview UI · fetched 2026-10-27 -->

# VS Code Webview UI

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [.nvmrc](.nvmrc)
- [.tool-versions](.tool-versions)
- [.vscode/extensions.json](.vscode/extensions.json)
- [.vscode/launch.json](.vscode/launch.json)
- [.vscode/settings.json](.vscode/settings.json)
- [.vscode/tasks.json](.vscode/tasks.json)
- [apps/vscode/scripts/clean-webview-vite-cache.mjs](apps/vscode/scripts/clean-webview-vite-cache.mjs)
- [apps/vscode/src/core/webview/WebviewProvider.ts](apps/vscode/src/core/webview/WebviewProvider.ts)
- [apps/vscode/webview-ui/src/components/chat/BrowserSessionRow.tsx](apps/vscode/webview-ui/src/components/chat/BrowserSessionRow.tsx)
- [apps/vscode/webview-ui/src/components/chat/ChatView.tsx](apps/vscode/webview-ui/src/components/chat/ChatView.tsx)
- [apps/vscode/webview-ui/src/components/chat/OptionsButtons.test.tsx](apps/vscode/webview-ui/src/components/chat/OptionsButtons.test.tsx)
- [apps/vscode/webview-ui/src/components/chat/OptionsButtons.tsx](apps/vscode/webview-ui/src/components/chat/OptionsButtons.tsx)
- [apps/vscode/webview-ui/src/components/chat/chat-view/components/layout/ActionButtons.test.tsx](apps/vscode/webview-ui/src/components/chat/chat-view/components/layout/ActionButtons.test.tsx)
- [apps/vscode/webview-ui/src/components/chat/chat-view/components/layout/ActionButtons.tsx](apps/vscode/webview-ui/src/components/chat/chat-view/components/layout/ActionButtons.tsx)
- [apps/vscode/webview-ui/src/components/chat/chat-view/components/layout/InputSection.test.tsx](apps/vscode/webview-ui/src/components/chat/chat-view/components/layout/InputSection.test.tsx)
- [apps/vscode/webview-ui/src/components/chat/chat-view/components/layout/InputSection.tsx](apps/vscode/webview-ui/src/components/chat/chat-view/components/layout/InputSection.tsx)
- [apps/vscode/webview-ui/src/components/chat/chat-view/components/layout/MessagesArea.tsx](apps/vscode/webview-ui/src/components/chat/chat-view/components/layout/MessagesArea.tsx)
- [apps/vscode/webview-ui/src/components/chat/chat-view/components/messages/MessageRenderer.tsx](apps/vscode/webview-ui/src/components/chat/chat-view/components/messages/MessageRenderer.tsx)
- [apps/vscode/webview-ui/src/components/chat/chat-view/hooks/index.ts](apps/vscode/webview-ui/src/components/chat/chat-view/hooks/index.ts)
- [apps/vscode/webview-ui/src/components/chat/chat-view/hooks/useChatState.test.tsx](apps/vscode/webview-ui/src/components/chat/chat-view/hooks/useChatState.test.tsx)
- [apps/vscode/webview-ui/src/components/chat/chat-view/hooks/useChatState.ts](apps/vscode/webview-ui/src/components/chat/chat-view/hooks/useChatState.ts)
- [apps/vscode/webview-ui/src/components/chat/chat-view/hooks/useMessageHandlers.test.tsx](apps/vscode/webview-ui/src/components/chat/chat-view/hooks/useMessageHandlers.test.tsx)
- [apps/vscode/webview-ui/src/components/chat/chat-view/hooks/useMessageHandlers.ts](apps/vscode/webview-ui/src/components/chat/chat-view/hooks/useMessageHandlers.ts)
- [apps/vscode/webview-ui/src/components/chat/chat-view/hooks/useThinkingLoaderRow.test.tsx](apps/vscode/webview-ui/src/components/chat/chat-view/hooks/useThinkingLoaderRow.test.tsx)
- [apps/vscode/webview-ui/src/components/chat/chat-view/hooks/useThinkingLoaderRow.ts](apps/vscode/webview-ui/src/components/chat/chat-view/hooks/useThinkingLoaderRow.ts)
- [apps/vscode/webview-ui/src/components/chat/chat-view/shared/buttonConfig.ts](apps/vscode/webview-ui/src/components/chat/chat-view/shared/buttonConfig.ts)
- [apps/vscode/webview-ui/src/components/chat/chat-view/types/chatTypes.ts](apps/vscode/webview-ui/src/components/chat/chat-view/types/chatTypes.ts)
- [apps/vscode/webview-ui/src/components/chat/chat-view/utils/messageUtils.test.ts](apps/vscode/webview-ui/src/components/chat/chat-view/utils/messageUtils.test.ts)
- [apps/vscode/webview-ui/src/components/chat/chat-view/utils/messageUtils.ts](apps/vscode/webview-ui/src/components/chat/chat-view/utils/messageUtils.ts)
- [apps/vscode/webview-ui/src/utils/__tests__/hooks.spec.ts](apps/vscode/webview-ui/src/utils/__tests__/hooks.spec.ts)
- [apps/vscode/webview-ui/src/utils/__tests__/platformUtils.spec.ts](apps/vscode/webview-ui/src/utils/__tests__/platformUtils.spec.ts)
- [apps/vscode/webview-ui/src/utils/platformUtils.ts](apps/vscode/webview-ui/src/utils/platformUtils.ts)
- [apps/vscode/webview-ui/vite.config.ts](apps/vscode/webview-ui/vite.config.ts)

</details>



The User Interface system implements Cline's React-based webview that runs inside VS Code. This page provides a high-level overview of the UI architecture, chat conversation system, settings configuration, task history, and account/onboarding flows. 

For detailed information, refer to the respective child pages: [UI Architecture](#6.1), [Chat Interface](#6.2), [Settings and Configuration UI](#6.3), [Task History and Task Header](#6.4), and [Account and Onboarding UI](#6.5).

## Purpose and Scope

This document describes the webview UI implementation that provides Cline's visual interface inside VS Code. The UI is built as a single-page React application communicating with the extension backend via gRPC-over-postMessage, managing all user interactions, task execution flows, settings updates, and configurations.

```mermaid
graph TB
    subgraph "NaturalLanguageSpace: Webview Root and State"
        Root[""Webview Root App""]
        State[""Extension State Context""]
    end
    
    subgraph "CodeEntitySpace: Application Files"
        App[""App.tsx"<br/>apps/vscode/webview-ui/src/App.tsx""]
        StateContext[""ExtensionStateContext.tsx"<br/>apps/vscode/webview-ui/src/context/ExtensionStateContext.tsx""]
        ChatView[""ChatView.tsx"<br/>apps/vscode/webview-ui/src/components/chat/ChatView.tsx""]
        SettingsView[""SettingsView.tsx"<br/>apps/vscode/webview-ui/src/components/settings/SettingsView.tsx""]
    end
    
    Root --> App
    State --> StateContext
    App --> StateContext
    StateContext --> ChatView
    StateContext --> SettingsView
```
Sources: [apps/vscode/webview-ui/src/App.tsx:15-98](), [apps/vscode/webview-ui/src/context/ExtensionStateContext.tsx:46-140]()

---

## 6.1. UI Architecture

The root of the webview application is defined in `App.tsx`, which wraps the view hierarchy inside the `ExtensionStateContext` provider [apps/vscode/webview-ui/src/App.tsx:15-90](). The build pipeline relies on Vite to bundle the React application into static assets loaded by the VS Code extension host [apps/vscode/webview-ui/vite.config.ts:83-114](). 

Communication with the extension backend utilizes typed gRPC clients (`TaskServiceClient`, `UiServiceClient`, `SlashServiceClient`) over `postMessage` [apps/vscode/webview-ui/src/components/chat/chat-view/hooks/useMessageHandlers.ts:7-30]().

For details, see [UI Architecture](#6.1).

Sources: [apps/vscode/webview-ui/src/App.tsx:15-90](), [apps/vscode/webview-ui/vite.config.ts:83-114](), [apps/vscode/webview-ui/src/components/chat/chat-view/hooks/useMessageHandlers.ts:7-30]()

---

## 6.2. Chat Interface

The `ChatView` component serves as the core conversation surface [apps/vscode/webview-ui/src/components/chat/ChatView.tsx:49-65](). It manages message lists via `MessagesArea` and `ChatRow`, supporting streaming assistant responses, tool execution blocks, completion results, queued prompts, and the thinking loader (`useThinkingLoaderRow`) [apps/vscode/webview-ui/src/components/chat/chat-view/components/layout/MessagesArea.tsx:40-106](). Input handling is managed through `InputSection` and `ChatTextArea`.

```mermaid
graph LR
    subgraph "NaturalLanguageSpace: Action Flow"
        UserAction[""User Message or Action""]
        RPCClient[""Typed gRPC Dispatcher""]
    end
    
    subgraph "CodeEntitySpace: Chat Handlers and Clients"
        MsgHandlers[""useMessageHandlers.ts"<br/>apps/vscode/webview-ui/src/components/chat/chat-view/hooks/useMessageHandlers.ts""]
        GrpcClient[""grpc-client.ts"<br/>apps/vscode/webview-ui/src/services/grpc-client.ts""]
    end
    
    UserAction --> MsgHandlers
    MsgHandlers --> RPCClient
    RPCClient --> GrpcClient
```
Sources: [apps/vscode/webview-ui/src/components/chat/chat-view/hooks/useMessageHandlers.ts:32-95](), [apps/vscode/webview-ui/src/components/chat/ChatView.tsx:49-65]()

For details, see [Chat Interface](#6.2).

Sources: [apps/vscode/webview-ui/src/components/chat/ChatView.tsx:49-108](), [apps/vscode/webview-ui/src/components/chat/chat-view/components/layout/MessagesArea.tsx:40-47]()

---

## 6.3. Settings and Configuration UI

The settings interface manages user configurations, LLM provider options (`ApiOptions`), feature settings sections, terminal integration settings, and MCP settings. Settings changes persist through gRPC state updates and extension state handlers.

For details, see [Settings and Configuration UI](#6.3).

Sources: [apps/vscode/webview-ui/src/components/settings/ApiOptions.tsx]()

---

## 6.4. Task History and Task Header

Task history browsing and resumption are handled by history view components, backed by the session model and task history utilities. The task header component displays usage cost visibility, context tokens, and active session badges.

For details, see [Task History and Task Header](#6.4).

Sources: [apps/vscode/webview-ui/src/components/chat/ChatView.tsx:49-65]()

---

## 6.5. Account and Onboarding UI

The account view features user info cards, credit displays, and organization management. First-time setup and model provider selection are guided by onboarding wizards that integrate feature flags and authentication flows.

For details, see [Account and Onboarding UI](#6.5).

Sources: [apps/vscode/webview-ui/src/App.tsx:63-88]()

---

