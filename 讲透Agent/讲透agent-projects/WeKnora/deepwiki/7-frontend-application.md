<!-- source: DeepWiki mcp.deepwiki.com · repo Tencent/WeKnora · page 7 Frontend Application · fetched 2026-10-29 -->

# Frontend Application

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/frontend.yml](.github/workflows/frontend.yml)
- [frontend/docker-entrypoint.sh](frontend/docker-entrypoint.sh)
- [frontend/mcpProxy.test.ts](frontend/mcpProxy.test.ts)
- [frontend/nginx-api-proxy.conf](frontend/nginx-api-proxy.conf)
- [frontend/nginx.conf](frontend/nginx.conf)
- [frontend/public/config.js](frontend/public/config.js)
- [frontend/src/components/ModelDebugDrawer.vue](frontend/src/components/ModelDebugDrawer.vue)
- [frontend/src/components/menu.vue](frontend/src/components/menu.vue)
- [frontend/src/i18n/index.ts](frontend/src/i18n/index.ts)
- [frontend/src/i18n/locales/en-US.ts](frontend/src/i18n/locales/en-US.ts)
- [frontend/src/i18n/locales/ja-JP.ts](frontend/src/i18n/locales/ja-JP.ts)
- [frontend/src/i18n/locales/ko-KR.ts](frontend/src/i18n/locales/ko-KR.ts)
- [frontend/src/i18n/locales/ru-RU.ts](frontend/src/i18n/locales/ru-RU.ts)
- [frontend/src/i18n/locales/workspaceTerminology.test.ts](frontend/src/i18n/locales/workspaceTerminology.test.ts)
- [frontend/src/i18n/locales/zh-CN.ts](frontend/src/i18n/locales/zh-CN.ts)
- [frontend/src/i18n/locales/zh-TW.ts](frontend/src/i18n/locales/zh-TW.ts)
- [frontend/src/i18n/resolveDefaultLocale.test.ts](frontend/src/i18n/resolveDefaultLocale.test.ts)
- [frontend/src/i18n/resolveDefaultLocale.ts](frontend/src/i18n/resolveDefaultLocale.ts)
- [frontend/src/utils/index.ts](frontend/src/utils/index.ts)
- [frontend/src/views/agent/AgentEditorModal.vue](frontend/src/views/agent/AgentEditorModal.vue)
- [frontend/src/views/agent/AgentList.vue](frontend/src/views/agent/AgentList.vue)
- [frontend/src/views/knowledge/KnowledgeBase.vue](frontend/src/views/knowledge/KnowledgeBase.vue)
- [frontend/src/views/knowledge/KnowledgeBaseList.vue](frontend/src/views/knowledge/KnowledgeBaseList.vue)
- [frontend/src/views/knowledge/components/FAQEntryManager.vue](frontend/src/views/knowledge/components/FAQEntryManager.vue)
- [frontend/src/views/knowledge/settings/DataSourceEditorDialog.test.ts](frontend/src/views/knowledge/settings/DataSourceEditorDialog.test.ts)
- [frontend/src/views/knowledge/settings/DataSourceEditorDialog.vue](frontend/src/views/knowledge/settings/DataSourceEditorDialog.vue)
- [frontend/src/views/organization/OrganizationList.vue](frontend/src/views/organization/OrganizationList.vue)
- [scripts/test_embed_nginx.py](scripts/test_embed_nginx.py)
- [website-docs/03-features/10-datasource.md](website-docs/03-features/10-datasource.md)

</details>



The WeKnora frontend is a Vue 3 single-page application (SPA) built with TypeScript and Vite, providing the user interface for knowledge base management, conversational chat sessions, agent visualizers, and system configuration [frontend/src/utils/index.ts:5-14](). This parent page provides a high-level overview of the architecture, build setup, request pipeline, and core modules.

**Child Pages:**
- [Navigation and Menu System](#7.1) — Document the sidebar navigation, menu components, session management UI, and routing structure.
- [Knowledge Base Interface](#7.2) — Explain the knowledge base editor, document list view, tag sidebar, upload UI, settings panels, and image gallery.
- [Chat Interface and Agent Display](#7.3) — Document the chat interface components, markdown/mermaid rendering, agent stream visualization, and real-time updates.
- [Settings and Configuration Interface](#7.4) — Document the settings UI for agent configuration, conversation settings, model selection, sandbox/skills panels, and system preferences.
- [State Management and API Integration](#7.5) — Explain Pinia stores, API client organization, request interceptors/auth refresh, and data flow patterns.
- [Internationalization System](#7.6) — Document the i18n setup, translation structure, supported languages, and adding new translations.
- [Frontend Security and Markdown Sanitization](#7.7) — Document DOMPurify-based sanitization, document preview rendering, protected file access, and XSS defenses in the frontend.

---

## Technology Stack and Build Pipeline

The frontend application uses a modern build system powered by Vite, producing optimized assets wrapped in an Nginx production container [frontend/nginx.conf:16-36](). Runtime configurations such as maximum file sizes and default locales are injected dynamically via entrypoint scripts into `config.js` [frontend/docker-entrypoint.sh:19-25]().

| Category | Library / Tool | Configuration Source |
|---|---|---|
| Build & Bundler | `vite` | `frontend/vite.config.ts` |
| UI Framework | `vue` | `frontend/package.json` |
| Component Library | `tdesign-vue-next` | `frontend/src/utils/index.ts:1-2` |
| HTTP Transport | `axios` | `frontend/src/utils/request.ts:56-64` |
| Localization | `vue-i18n` | `frontend/src/i18n/index.ts:25-35` |
| Reverse Proxy | `nginx` | `frontend/nginx.conf:16-100` |

Sources: [frontend/nginx.conf:16-100](), [frontend/docker-entrypoint.sh:19-25](), [frontend/src/utils/request.ts:56-64](), [frontend/src/i18n/index.ts:25-35]()

---

## Request Handling and API Integration

HTTP requests are managed through a centralized Axios instance configured with request interceptors that attach Bearer tokens, language preferences, and tenant context headers [frontend/src/utils/request.ts:56-111](). Response interceptors manage error normalization, timeout detection, and token refresh workflows [frontend/src/utils/request.ts:125-183](). For detailed documentation on state management and API integration patterns, see [State Management and API Integration](#7.5).

Sources: [frontend/src/utils/request.ts:56-183]()

---

## Core Interface Modules

The application is structured around feature-specific views and components. For deep-dive documentation on each major functional area, refer to the respective child pages:
- **Navigation and Menu:** Managed via layout components and dynamic routing structures, including the main sidebar menu [frontend/src/components/menu.vue:1-2100](). For details, see [Navigation and Menu System](#7.1).
- **Knowledge Base Management:** Document processing, parsers, and tag views, including the `KnowledgeBase.vue` editor [frontend/src/views/knowledge/KnowledgeBase.vue:1-3583]() and `FAQEntryManager.vue` [frontend/src/views/knowledge/components/FAQEntryManager.vue:1-5607](). For details, see [Knowledge Base Interface](#7.2).
- **Chat and Agent Workflows:** Streaming bot responses, markdown rendering, and model debugging drawers [frontend/src/components/ModelDebugDrawer.vue:2-16](). Agent creation and editing are handled by `AgentEditorModal.vue` [frontend/src/views/agent/AgentEditorModal.vue:1-6831](). For details, see [Chat Interface and Agent Display](#7.3).
- **Settings and Administration:** Model definitions, sandbox options, and tenant preferences. This includes the model catalog settings [frontend/src/i18n/locales/en-US.ts:2-126](), [frontend/src/i18n/locales/zh-CN.ts:2-126](), [frontend/src/i18n/locales/ru-RU.ts:2-126](), [frontend/src/i18n/locales/ko-KR.ts:2-126](), [frontend/src/i18n/locales/ja-JP.ts:2-126](), [frontend/src/i18n/locales/zh-TW.ts:2-126](). For details, see [Settings and Configuration Interface](#7.4).

Sources: [frontend/src/components/ModelDebugDrawer.vue:2-16](), [frontend/src/components/menu.vue:1-2100](), [frontend/src/views/knowledge/KnowledgeBase.vue:1-3583](), [frontend/src/views/knowledge/components/FAQEntryManager.vue:1-5607](), [frontend/src/views/agent/AgentEditorModal.vue:1-6831](), [frontend/src/i18n/locales/en-US.ts:2-126](), [frontend/src/i18n/locales/zh-CN.ts:2-126](), [frontend/src/i18n/locales/ru-RU.ts:2-126](), [frontend/src/i18n/locales/ko-KR.ts:2-126](), [frontend/src/i18n/locales/ja-JP.ts:2-126](), [frontend/src/i18n/locales/zh-TW.ts:2-126]()

---

## Bridging Natural Language Space to Code Entity Space

### Diagram: Natural Language Architecture to Code Modules

Title: "NaturalLanguageToCodeArchitecture"
```mermaid
graph LR
    NL_Navigation[""Navigation & Sidebar""]
    NL_Knowledge[""Knowledge Base UI""]
    NL_ChatAgent[""Chat & Agent Display""]
    NL_Settings[""Settings & Model Debug""]

    Code_Menu[""menu.vue""]
    Code_KB[""KnowledgeBase.vue""]
    Code_FAQManager[""FAQEntryManager.vue""]
    Code_AgentEditor[""AgentEditorModal.vue""]
    Code_Debug[""ModelDebugDrawer.vue""]
    Code_KBList[""KnowledgeBaseList.vue""]
    Code_AgentList[""AgentList.vue""]
    Code_ModelCatalog[""i18n/locales/*.ts (modelCatalog)""]

    NL_Navigation --> Code_Menu
    NL_Knowledge --> Code_KB
    NL_Knowledge --> Code_FAQManager
    NL_Knowledge --> Code_KBList
    NL_ChatAgent --> Code_AgentEditor
    NL_ChatAgent --> Code_AgentList
    NL_ChatAgent --> Code_Debug
    NL_Settings --> Code_ModelCatalog
```
Sources: [frontend/src/components/ModelDebugDrawer.vue:2-16](), [frontend/src/components/menu.vue:1-2100](), [frontend/src/views/knowledge/KnowledgeBase.vue:1-3583](), [frontend/src/views/knowledge/components/FAQEntryManager.vue:1-5607](), [frontend/src/views/agent/AgentEditorModal.vue:1-6831](), [frontend/src/views/knowledge/KnowledgeBaseList.vue:1-2112](), [frontend/src/views/agent/AgentList.vue:1-1877](), [frontend/src/i18n/locales/en-US.ts:2-126](), [frontend/src/i18n/locales/zh-CN.ts:2-126](), [frontend/src/i18n/locales/ru-RU.ts:2-126](), [frontend/src/i18n/locales/ko-KR.ts:2-126](), [frontend/src/i18n/locales/ja-JP.ts:2-126](), [frontend/src/i18n/locales/zh-TW.ts:2-126]()

### Diagram: Request Lifecycle and API Interceptors

Title: "RequestLifecycleAndInterceptors"
```mermaid
graph TB
    NL_Request[""User API Request""]
    Code_Axios[""axios.create()""]
    Code_Interceptor[""instance.interceptors.request.use()""]
    Code_Response[""nginx.conf location /""]

    NL_Request --> Code_Axios
    Code_Axios --> Code_Interceptor
    Code_Interceptor --> Code_Response
```
Sources: [frontend/src/utils/request.ts:56-111](), [frontend/nginx.conf:87-100]()

---

For detailed technical descriptions, implementation patterns, and code structure across specific modules, follow the child page links provided above.

---

