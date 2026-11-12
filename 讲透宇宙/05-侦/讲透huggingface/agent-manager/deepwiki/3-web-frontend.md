<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/agent-manager · page 3 Web Frontend · fetched 2026-10-26 -->

# Web Frontend

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [demo/src/main.tsx](demo/src/main.tsx)
- [docs/conversation-view.md](docs/conversation-view.md)

</details>



The `web/` directory contains a React and Vite single-page application that serves as the primary graphical interface for Agent Manager. It provides real-time terminal interaction, conversation tracing, file exploration, settings management, and onboarding flows. This section provides a high-level architectural overview of the frontend bootstrap, api client layout, styling, and component organization, while deferring deep technical specifics to its child pages.

## Frontend Architecture and Bootstrap

The frontend application initializes in `web/src/App.tsx`, mounting the root React tree, establishing WebSocket/HTTP client connections through `web/src/api.js`, and managing global application state such as active sessions, locks, and view routing.

```
Title: Frontend Bootstrapping and Component Layout

graph TD
    subgraph "Natural Language Space"
        A["Client Initialization"] --> B["API Connection"]
        B --> C["Workspace Rendering"]
    end
    subgraph "Code Entity Space"
        D["web/src/App.tsx"] --> E["web/src/api.js"]
        E --> F["web/src/components/Sidebar.tsx"]
        F --> G["web/src/components/TerminalPane.tsx"]
        F --> H["web/src/components/FilesPane.tsx"]
    end
    A -.-> D
    B -.-> E
    C -.-> F
```

Sources: `web/src/App.tsx:1-50`, `web/src/api.js:1-30`

---

## Child Pages

For detailed technical specifications, component layouts, and implementation details, refer to the following child pages:

- [Conversation Reader UI](#3.1) — Covers `ConversationView`, `readerModel`/`readerStore`, trace windows, trace panel specs, and reader validation approaches.
- [Workspace, Panes and Terminal UI](#3.2) — Covers the workspace overview, sidebar/rails layout, `TerminalPane` and retry logic, `FilesPane`, file link previews, attachments, screenshot inputs, and uploads.
- [Settings, Onboarding and Lock States](#3.3) — Covers first-run dialogs, `WelcomeSetup`/`BucketPrompt`, `SettingsView` and save queues, locked views, and lock status handling, as well as API log and usage panels.

---

## Core Layout and Navigation

The user interface relies on a responsive sidebar-and-rails layout that adapts between desktop multi-pane views and mobile stacked panes. State management coordinates between active CLI processes, file modifications, and live console streams.

```
Title: Core UI Data Flow and Module Dependencies

graph TD
    subgraph "Natural Language Space"
        U1["User Input / Terminal Command"] --> U2["API Request Client"]
        U2 --> U3["State Synchronization"]
    end
    subgraph "Code Entity Space"
        C1["web/src/components/TerminalPane.tsx"] --> C2["web/src/api.js"]
        C2 --> C3["web/src/App.tsx"]
        C3 --> C4["web/src/components/Sidebar.tsx"]
    end
    U1 -.-> C1
    U2 -.-> C2
    U3 -.-> C3
```

Sources: `web/src/App.tsx:10-80`, `web/src/api.js:15-60`, `web/src/components/TerminalPane.tsx:1-40`

---

