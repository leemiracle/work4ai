<!-- source: DeepWiki mcp.deepwiki.com · repo langbot-app/LangBot · page 8 Web Management Interface · fetched 2026-10-29 -->

# Web Management Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [web/src/app/home/components/home-sidebar/HomeSidebar.tsx](web/src/app/home/components/home-sidebar/HomeSidebar.tsx)
- [web/src/app/home/components/home-sidebar/SidebarDataContext.tsx](web/src/app/home/components/home-sidebar/SidebarDataContext.tsx)
- [web/src/app/home/plugins/page.tsx](web/src/app/home/plugins/page.tsx)
- [web/src/app/infra/entities/api/index.ts](web/src/app/infra/entities/api/index.ts)
- [web/src/app/infra/http/BackendClient.ts](web/src/app/infra/http/BackendClient.ts)
- [web/src/app/wizard/page.tsx](web/src/app/wizard/page.tsx)
- [web/src/i18n/locales/en-US.ts](web/src/i18n/locales/en-US.ts)
- [web/src/i18n/locales/es-ES.ts](web/src/i18n/locales/es-ES.ts)
- [web/src/i18n/locales/ja-JP.ts](web/src/i18n/locales/ja-JP.ts)
- [web/src/i18n/locales/ru-RU.ts](web/src/i18n/locales/ru-RU.ts)
- [web/src/i18n/locales/th-TH.ts](web/src/i18n/locales/th-TH.ts)
- [web/src/i18n/locales/vi-VN.ts](web/src/i18n/locales/vi-VN.ts)
- [web/src/i18n/locales/zh-Hans.ts](web/src/i18n/locales/zh-Hans.ts)
- [web/src/i18n/locales/zh-Hant.ts](web/src/i18n/locales/zh-Hant.ts)

</details>



The **Web Management Interface** is the primary administrative Single Page Application (SPA) for LangBot. It is developed using the **Vite** build tool in combination with **React Router 7**, providing a modern frontend framework with streamlined routing, fast development experience, and client-side page navigation. This SPA is served as static assets embedded within the Quart backend and enables a full-featured graphical interface for managing all of LangBot's administrative and operational domains:

- Bot and pipeline setup and control
- Model provider management
- Plugin installation and configuration
- Knowledge base and document ingestion
- Workspace and user management
- Monitoring, telemetry, and session feedback

The frontend uses schema-driven dynamic forms, internationalization powered by i18next, and real-time updates via WebSockets, encompassing a rich, extensible, and global SaaS-style control panel. The UI components primarily build on Radix UI primitives combined with the shadcn/ui library and are styled using Tailwind CSS.

This page provides a high-level overview of the frontend architecture, main system components, and natural language to code mappings. Detailed implementation information is covered in dedicated child wiki pages.

Sources: [web/src/app/home/components/home-sidebar/HomeSidebar.tsx:1-46]()

---

## Routing and Root Layout Architecture

Routing is implemented declaratively in React Router 7 via `createBrowserRouter` in `web/router.tsx`. The entire application is encapsulated within a top-level `RootLayout` component, which handles global page setup such as setting the document title through the custom hook `useDocumentTitle()`.

Routes bifurcate into two major groups:

- **Public Routes:** Handle unauthenticated pages like login, registration, password resets, initial workspace selection, and setup wizards. These are defined in `web/src/app/wizard/page.tsx` for the setup wizard.
- **Protected Routes:** All under the `/home` base path, accessible only after authentication and workspace selection. Managed by the `HomeLayout` component, this layout sets workspace context, enforces permissions, and manages sidebar navigation.

The router structure ensures clear separation of concerns for security and usability.

### Diagram: Router and Root Layout Architecture

```mermaid
graph TD
  subgraph "Code_Entity_Space"
    "router"["router.tsx"]
    "RootLayout"["RootLayout.tsx"]
    "useDocumentTitle"["useDocumentTitle.ts"]
    "HomeLayout"["home/layout.tsx"]
    "Outlet"["Outlet"]
    "WizardPage"["wizard/page.tsx"]
  end

  subgraph "Natural_Language_Space"
    "PublicRoutes"["Public Authentication and Setup Routes"]
    "HomeRoutes"["Protected Administrative /home Routes"]
  end

  "router" -- "defines" --> "RootLayout"
  "RootLayout" -- "invokes" --> "useDocumentTitle"
  "RootLayout" -- "renders" --> "Outlet"
  "Outlet" -- "renders" --> "PublicRoutes"
  "PublicRoutes" -- "includes" --> "WizardPage"
  "Outlet" -- "renders" --> "HomeLayout"
  "HomeLayout" -- "renders" --> "HomeRoutes"
```

Sources: [web/src/app/wizard/page.tsx:1](), [web/src/app/home/components/home-sidebar/HomeSidebar.tsx:1-46]()

---

## Frontend Module Organization and Sidebar Navigation

The administration UI is functionally divided into feature modules surfaced through a sidebar menu scoped within `/home`. The sidebar configuration relies on modules like `HomeSidebar` [web/src/app/home/components/home-sidebar/HomeSidebar.tsx:1-46]() and list definitions where each menu item specifies its ID, icon, route, description, and optional help links. The `sidebarConfigList` [web/src/app/home/components/home-sidebar/HomeSidebar.tsx:4]() defines the structure, and `SidebarDataContext` [web/src/app/home/components/home-sidebar/SidebarDataContext.tsx:1]() manages the state for sidebar entities.

Key sidebar sections and their route mappings include:

| Section | Sidebar ID Example | Representative Routes | Functionality |
|---|---|---|---|
| Home Section | `home.monitoring` | `/home/monitoring`, `/home/bots`, `/home/agents`, `/home/knowledge` | Monitoring dashboards, bot and processor management, knowledge base pages |
| Extensions Section | `home.extensions` | `/home/extensions`, `/home/add-extension`, `/home/mcp`, `/home/skills`, `/home/plugin-pages` | Plugin marketplace, MCP servers, skill management, plugin pages |

This modular structure maps closely to backend domain services and supports lazy loading of routes for performance.

### Diagram: Feature Modules to Code Mapping

```mermaid
graph TD
  subgraph "Code_Entity_Space"
    "HomeLayout"["home/layout.tsx"]
    "HomeSidebar"["HomeSidebar.tsx"]
    "sidbarConfigList"["sidbarConfigList.tsx"]
    "MonitoringPage"["monitoring/page.tsx"]
    "BotsPage"["bots/page.tsx"]
    "PluginsPage"["plugins/page.tsx"]
    "SidebarDataContext"["SidebarDataContext.tsx"]
  end

  subgraph "Natural_Language_Space"
    "HomeSection"["Home Section"]
    "ExtensionsSection"["Extensions Section"]
    "Monitoring"["Monitoring and Telemetry UI"]
    "Bots"["Bot Management UI"]
    "InstalledPlugins"["Installed Plugins UI"]
  end

  "HomeLayout" -- "uses" --> "HomeSidebar"
  "HomeSidebar" -- "configured by" --> "sidbarConfigList"
  "HomeSidebar" -- "manages state via" --> "SidebarDataContext"
  "sidbarConfigList" -- "routes to" --> "MonitoringPage"
  "sidbarConfigList" -- "routes to" --> "BotsPage"
  "sidbarConfigList" -- "routes to" --> "PluginsPage"

  "MonitoringPage" --> "Monitoring"
  "BotsPage" --> "Bots"
  "PluginsPage" --> "InstalledPlugins"
```

Sources: [web/src/app/home/components/home-sidebar/HomeSidebar.tsx:1-46](), [web/src/app/home/components/home-sidebar/SidebarDataContext.tsx:1]()

---

## Client Communication and State Management

The frontend API interaction uses strongly-typed client classes for HTTP and WebSocket:

- `BaseHttpClient`, `BackendClient`, `CloudServiceClient`: Wrap REST API calls, handle authentication, error states, and interceptors [web/src/app/infra/http/BackendClient.ts:113-127](). The `BackendClient` specifically handles interactions with the LangBot backend API [web/src/app/infra/http/BackendClient.ts:113-127]().
- `WebSocketClient`: Manages WebSocket connection lifecycles, streaming logs, telemetry data, and real-time session updates.

These clients provide typed method calls matching backend endpoints and support cross-cutting concerns like authorization and retries.

The UI extensively employs schema-driven dynamic form components (`DynamicFormComponent`, `DynamicFormItemComponent`) using React Hook Form for flexible rendering of configuration fields, support for conditional fields (`show_if`, `disable_if`), and integration with domain-specific value handlers (e.g., API keys, plugin configs, OAuth).

Internationalization (i18n) support is integrated via i18next and related utilities, enabling language detection, locale resource loading, and switching within the UI, scaling for global deployments. Examples of locale files include `en-US.ts` [web/src/i18n/locales/en-US.ts:1](), `zh-Hans.ts` [web/src/i18n/locales/zh-Hans.ts:1](), `zh-Hant.ts` [web/src/i18n/locales/zh-Hant.ts:1](), `ja-JP.ts` [web/src/i18n/locales/ja-JP.ts:1](), `es-ES.ts` [web/src/i18n/locales/es-ES.ts:1](), `ru-RU.ts` [web/src/i18n/locales/ru-RU.ts:1](), and `th-TH.ts` [web/src/i18n/locales/th-TH.ts:1](), `vi-VN.ts` [web/src/i18n/locales/vi-VN.ts:1]().

For more details, consult:
- [HTTP and WebSocket Client System](#8.3)
- [Dynamic Form System](#8.8)
- [Internationalization (i18n)](#8.9)

Sources: [web/src/app/infra/http/BackendClient.ts:113-127](), [web/src/i18n/locales/en-US.ts:1](), [web/src/i18n/locales/zh-Hans.ts:1](), [web/src/i18n/locales/zh-Hant.ts:1](), [web/src/i18n/locales/ja-JP.ts:1](), [web/src/i18n/locales/es-ES.ts:1](), [web/src/i18n/locales/ru-RU.ts:1](), [web/src/i18n/locales/th-TH.ts:1](), [web/src/i18n/locales/vi-VN.ts:1]()

---

## Summary of Subsystem Coverage in Child Pages

The Web Management Interface is broken down into comprehensive modular subsystems, each covered in separate child wiki pages:

| Child Page Title | Description |
|---|---|
| [Frontend Architecture and Technology Stack](#8.1) | Vite + React Router 7 integration, component libraries (shadcn/ui, Radix UI), Tailwind styling, routing structure, layouts, sidebar config, and build process. |
| [Authentication and User Management](#8.2) | User login, registration, password reset, TOTP MFA and recovery codes, WebAuthn passkeys, Space OAuth, JWT sessions, and API key management. |
| [HTTP and WebSocket Client System](#8.3) | Typed client wrappers for REST and WebSocket backend communication, interceptors, and error handling. |
| [Bot and Processor Management UI](#8.4) | Bot and processor CRUD pages, event bindings editor, processor detail workbench, diagram rendering, and dynamic form usage. |
| [Model Provider Management UI](#8.5) | Management of LLM and embedding models, provider cards, argument editors, model testing UIs, and Space credit display. |
| [Plugin Management UI](#8.6) | Plugin marketplace browsing, installed plugin overview, configuration dialogs, plugin page authorization, local preview panels, and README display. |
| [Knowledge Base Management UI](#8.7) | Knowledge base CRUD, document upload and ingestion, retrieval testing, and RAG migration dialogs. |
| [Dynamic Form System](#8.8) | Schema-driven form rendering, conditional elements, specialized auth fields, value saving, and custom field types. |
| [Internationalization (i18n)](#8.9) | i18next integration, supported languages, language selector, structured translation objects, extraction, and CI enforcement. |
| [Monitoring and Telemetry UI](#8.10) | Metrics overview, traffic charts, message and session logs, token usage monitoring, export features, and pipeline health monitoring. |
| [Bot Session Monitor and Feedback](#8.11) | Real-time session monitoring, backend integration, user feedback and survey collection. |
| [Workspace, Quota, and Invitation UI](#8.12) | Workspace switching and settings, member and email management, quota information, invitations, and privacy model distinctions. |
| [Workspace Assistant](#8.13) | Embedded AI assistant UI panels, result rendering, conversation history persistence, and backend assistant tooling support. |

Sources: [web/src/app/home/components/home-sidebar/HomeSidebar.tsx:1-46]()

---

## Natural Language to Code Entity Bridge Diagrams

### Diagram 1: Core Frontend System Mapping

This diagram illustrates how major natural-language UI concepts relate to key code entities and files.

```mermaid
graph TD
  subgraph "Natural_Language_Space"
    "RoutingLayer"["Routing Layer"]
    "PluginManagementUI"["Plugin Management UI"]
    "BackendClientLayer"["HTTP Client System"]
    "Internationalization"["Internationalization (i18n)"]
  end

  subgraph "Code_Entity_Space"
    "routerFile"["router.tsx"]
    "PluginsPage"["plugins/page.tsx"]
    "BackendClient"["BackendClient.ts"]
    "i18nLocales"["i18n/locales/*.ts"]
  end

  "RoutingLayer" --> "routerFile"
  "PluginManagementUI" --> "PluginsPage"
  "BackendClientLayer" --> "BackendClient"
  "Internationalization" --> "i18nLocales"
```

Sources: [web/src/app/home/plugins/page.tsx:35-44](), [web/src/app/infra/http/BackendClient.ts:113-127](), [web/src/i18n/locales/en-US.ts:1]()

---

### Diagram 2: Sidebar to Routes to Pages Mapping

This diagram clarifies the linkage between the sidebar configuration, routes, and the rendered pages.

```mermaid
graph TD
  subgraph "Natural_Language_Space"
    "SidebarNav"["Sidebar Navigation Items"]
    "PageViews"["Plugin & Home Views"]
  end

  subgraph "Code_Entity_Space"
    "HomeSidebar"["HomeSidebar.tsx"]
    "sidebarConfigList"["sidbarConfigList.tsx"]
    "PluginConfigPage"["plugins/page.tsx"]
    "SidebarDataContext"["SidebarDataContext.tsx"]
  end

  "SidebarNav" --> "HomeSidebar"
  "HomeSidebar" -- "uses" --> "sidebarConfigList"
  "HomeSidebar" -- "manages state via" --> "SidebarDataContext"
  "HomeSidebar" --> "PluginConfigPage"
  "PageViews" --> "PluginConfigPage"
```

Sources: [web/src/app/home/components/home-sidebar/HomeSidebar.tsx:1-46](), [web/src/app/home/plugins/page.tsx:35-44](), [web/src/app/home/components/home-sidebar/SidebarDataContext.tsx:1]()

---

## Links to Child Pages

- [Frontend Architecture and Technology Stack](#8.1)
- [Authentication and User Management](#8.2)
- [HTTP and WebSocket Client System](#8.3)
- [Bot and Processor Management UI](#8.4)
- [Model Provider Management UI](#8.5)
- [Plugin Management UI](#8.6)
- [Knowledge Base Management UI](#8.7)
- [Dynamic Form System](#8.8)
- [Internationalization (i18n)](#8.9)
- [Monitoring and Telemetry UI](#8.10)
- [Bot Session Monitor and Feedback](#8.11)
- [Workspace, Quota, and Invitation UI](#8.12)
- [Workspace Assistant](#8.13)

---

