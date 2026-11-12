> 来源: [https://deepwiki.com/Tencent/WeKnora/7-frontend-application](https://deepwiki.com/Tencent/WeKnora/7-frontend-application)
> DeepWiki Tencent/WeKnora

# Frontend Application

  Relevant source files 
 - [frontend/src/api/system/index.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/api/system/index.ts)
 - [frontend/src/components/menu.vue](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/components/menu.vue)
 - [frontend/src/i18n/locales/en-US.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/i18n/locales/en-US.ts)
 - [frontend/src/i18n/locales/ja-JP.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/i18n/locales/ja-JP.ts)
 - [frontend/src/i18n/locales/ko-KR.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/i18n/locales/ko-KR.ts)
 - [frontend/src/i18n/locales/ru-RU.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/i18n/locales/ru-RU.ts)
 - [frontend/src/i18n/locales/zh-CN.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/i18n/locales/zh-CN.ts)
 - [frontend/src/views/agent/AgentEditorModal.vue](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/agent/AgentEditorModal.vue)
 - [frontend/src/views/knowledge/KnowledgeBase.vue](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/KnowledgeBase.vue)
 - [internal/handler/tenant.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/tenant.go)
 - [internal/router/router.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/router/router.go)
 - [internal/types/tenant.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/tenant.go)
 
  The WeKnora frontend is a Vue 3 single-page application (SPA) built with TypeScript and Vite. It provides the web interface for managing knowledge bases, conducting conversational AI chat sessions, visualizing agent executions, and configuring system-wide settings. This page documents the overall frontend architecture, key components, state management strategies, and integration patterns with backend services.

 **Child Pages:**

 
 - [Navigation and Menu System](https://deepwiki.com/Tencent/WeKnora/7.1-navigation-and-menu-system) — Sidebar navigation, menu components, session management UI, and routing structure.
 - [Knowledge Base Interface](https://deepwiki.com/Tencent/WeKnora/7.2-knowledge-base-interface) — Knowledge base editor, document list views, tag sidebar, upload UI, and settings panels.
 - [Chat Interface and Agent Display](https://deepwiki.com/Tencent/WeKnora/7.3-chat-interface-and-agent-display) — Chat UI components, markdown/mermaid rendering, agent stream visualization, and real-time update mechanisms.
 - [Settings and Configuration Interface](https://deepwiki.com/Tencent/WeKnora/7.4-settings-and-configuration-interface) — UI for agent configuration, conversation settings, model selection, sandbox/skills panels, and system preferences.
 - [State Management and API Integration](https://deepwiki.com/Tencent/WeKnora/7.5-state-management-and-api-integration) — Pinia stores, API client structure, request interceptors for authentication, and data flow patterns.
 - [Internationalization System](https://deepwiki.com/Tencent/WeKnora/7.6-internationalization-system) — i18n setup, translation structure, supported languages, and how to add new translations.
 - [Frontend Security and Markdown Sanitization](https://deepwiki.com/Tencent/WeKnora/7.7-frontend-security-and-markdown-sanitization) — DOMPurify based sanitization for safe markdown rendering, document preview security, protected file access, and XSS defenses.
 
 
---

 
## Technology Stack

 The frontend adopts a modern Vue 3 ecosystem SPA architecture and leverages core libraries bootstrapped centrally in `frontend/src/main.ts` [frontend/src/main.ts1-6](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/main.ts#L1-L6)

 
| Category | Library | Version |
|---|---|---|
| UI Framework | vue | ^3.5.13 |
| Build Tool | vite | ^7.2.2 |
| Language | typescript | ~5.8.0 |
| State Management | pinia | ^3.0.1 |
| Routing | vue-router | ^4.5.0 |
| UI Component Lib | tdesign-vue-next | ^1.17.2 |
| Internationalization | vue-i18n | ^11.1.12 |
| HTTP Client | axios | ^1.8.4 |

 Sources: [frontend/src/main.ts1-6](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/main.ts#L1-L6)

 
---

 
## Application Architecture

 The frontend implements a modular design where the main layout container manages both the sidebar navigation and a dynamic viewport rendering feature views such as Knowledge Base, Chat, Agents, and Settings. Initial application bootstrap includes user identity and capabilities resolution to gate access before the first render [frontend/src/main.ts41-59](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/main.ts#L41-L59)

 
### Frontend Component Hierarchy and State Flow

 Title: Frontend Component and Store Relationships

 
```

```

 Sources: [frontend/src/components/menu.vue2-101](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/components/menu.vue#L2-L101) [frontend/src/stores/auth.ts31-60](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/stores/auth.ts#L31-L60) [frontend/src/router/index.ts46-182](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/router/index.ts#L46-L182) [frontend/src/stores/menu.ts22-37](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/stores/menu.ts#L22-L37)

 
---

 
## Core Interface Modules

 
### Knowledge Base and Agent Management

 The frontend offers unified user experiences for managing WeKnora’s core resources:

 
 - **Knowledge Base Interface:** Supports features like document list views, FAQ management, Wiki browsing, and tag navigation [frontend/src/views/knowledge/KnowledgeBase.vue1-166](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/KnowledgeBase.vue#L1-L166) For details, see [Knowledge Base Interface](https://deepwiki.com/Tencent/WeKnora/7.2-knowledge-base-interface).
 - **Agent Configuration:** Provides modal dialog editors for creating and updating agents with mode selection, prompt configuration, and integration status displays [frontend/src/views/agent/AgentEditorModal.vue1-123](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/agent/AgentEditorModal.vue#L1-L123) For details, see [Chat Interface and Agent Display](https://deepwiki.com/Tencent/WeKnora/7.3-chat-interface-and-agent-display).
 
 
### Global Interaction UI

 Cross-cutting UI tools enhance productivity across the application:

 
 - **Global Command Palette:** Accessible via `⌘K` / `Ctrl+K`, enabling rapid search across knowledge bases, agents, and conversations [frontend/src/components/menu.vue10-21](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/components/menu.vue#L10-L21)
 - **Dynamic Sidebar Navigation:** Managed by `menu.vue` for navigating spaces, settings, and chat history [frontend/src/components/menu.vue79-101](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/components/menu.vue#L79-L101)
 
 Sources: [frontend/src/components/menu.vue10-21](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/components/menu.vue#L10-L21) [frontend/src/router/index.ts114-141](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/router/index.ts#L114-L141) [frontend/src/stores/menu.ts23-37](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/stores/menu.ts#L23-L37)

 
---

 
## Authentication and State Management

 WeKnora applies Pinia as the centralized state library to manage reactive user state, tenant context, and session data coherently across UI components. The `useAuthStore` tracks user identity, active workspaces, and permissions [frontend/src/stores/auth.ts33-46](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/stores/auth.ts#L33-L46) Vue Router enforces authentication guards and tenant namespace requirements [frontend/src/router/index.ts46-101](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/router/index.ts#L46-L101)

 Title: Authentication and Routing Flow

 
```

```

 Sources: [frontend/src/views/auth/Login.vue1-101](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/auth/Login.vue#L1-L101) [frontend/src/api/auth/index.ts210-220](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/api/auth/index.ts#L210-L220) [frontend/src/stores/auth.ts31-67](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/stores/auth.ts#L31-L67) [frontend/src/App.vue22-94](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/App.vue#L22-L94)

 
---

 
## Internationalization (i18n)

 The frontend supports multi-language translation including English (`en-US`), Simplified Chinese (`zh-CN`), Korean (`ko-KR`), and Russian (`ru-RU`) via `vue-i18n` [frontend/src/App.vue17-33](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/App.vue#L17-L33) [frontend/src/stores/menu.ts47-62](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/stores/menu.ts#L47-L62) For details, see [Internationalization System](https://deepwiki.com/Tencent/WeKnora/7.6-internationalization-system).

 Sources: [frontend/src/App.vue17-33](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/App.vue#L17-L33) [frontend/src/stores/menu.ts47-62](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/stores/menu.ts#L47-L62) [frontend/src/main.ts53](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/main.ts#L53-L53)

 
---

 
## Bridging Natural Language UI Concepts to Code Entities

 
### Diagram: Mapping System Features to Code Components

 Title: Natural Language to Code Entity Mapping

 
```

```

 Sources: [frontend/src/components/menu.vue1-101](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/components/menu.vue#L1-L101) [frontend/src/views/knowledge/KnowledgeBase.vue1-166](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/KnowledgeBase.vue#L1-L166) [frontend/src/views/agent/AgentEditorModal.vue1-123](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/agent/AgentEditorModal.vue#L1-L123)

 
### Diagram: Linking User Actions to Frontend Modules and APIs

 Title: User Actions and Data Flow

 
```

```

 Sources: [frontend/src/main.ts1-59](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/main.ts#L1-L59) [frontend/src/components/menu.vue2-101](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/components/menu.vue#L2-L101) [frontend/src/views/knowledge/KnowledgeBase.vue1-166](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/knowledge/KnowledgeBase.vue#L1-L166) [frontend/src/views/agent/AgentEditorModal.vue1-123](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/agent/AgentEditorModal.vue#L1-L123)

 
---

 For detailed technical descriptions and code structure across specific modules, follow the links to the child pages above.
