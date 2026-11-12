<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/browsercode · page 4 User Interfaces · fetched 2026-10-30 -->

# User Interfaces

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/app/src/components/dialog-edit-project.tsx](packages/app/src/components/dialog-edit-project.tsx)
- [packages/app/src/components/dialog-select-file.tsx](packages/app/src/components/dialog-select-file.tsx)
- [packages/app/src/components/prompt-input.tsx](packages/app/src/components/prompt-input.tsx)
- [packages/app/src/components/session-context-usage.tsx](packages/app/src/components/session-context-usage.tsx)
- [packages/app/src/components/session/session-context-tab.tsx](packages/app/src/components/session/session-context-tab.tsx)
- [packages/app/src/components/session/session-header.tsx](packages/app/src/components/session/session-header.tsx)
- [packages/app/src/components/session/session-new-view.tsx](packages/app/src/components/session/session-new-view.tsx)
- [packages/app/src/components/titlebar.tsx](packages/app/src/components/titlebar.tsx)
- [packages/app/src/context/global-sync.tsx](packages/app/src/context/global-sync.tsx)
- [packages/app/src/context/layout.tsx](packages/app/src/context/layout.tsx)
- [packages/app/src/context/sync.tsx](packages/app/src/context/sync.tsx)
- [packages/app/src/pages/layout.tsx](packages/app/src/pages/layout.tsx)
- [packages/app/src/pages/session.tsx](packages/app/src/pages/session.tsx)
- [packages/core/src/process.ts](packages/core/src/process.ts)
- [packages/core/test/process/process.test.ts](packages/core/test/process/process.test.ts)
- [packages/desktop/electron-builder.config.ts](packages/desktop/electron-builder.config.ts)
- [packages/desktop/electron.vite.config.ts](packages/desktop/electron.vite.config.ts)
- [packages/desktop/src/main/apps.ts](packages/desktop/src/main/apps.ts)
- [packages/desktop/src/main/index.ts](packages/desktop/src/main/index.ts)
- [packages/desktop/src/main/ipc.ts](packages/desktop/src/main/ipc.ts)
- [packages/desktop/src/main/logging.ts](packages/desktop/src/main/logging.ts)
- [packages/desktop/src/main/server.ts](packages/desktop/src/main/server.ts)
- [packages/desktop/src/main/shell-env.test.ts](packages/desktop/src/main/shell-env.test.ts)
- [packages/desktop/src/main/shell-env.ts](packages/desktop/src/main/shell-env.ts)
- [packages/desktop/src/main/sidecar.ts](packages/desktop/src/main/sidecar.ts)
- [packages/desktop/src/main/store.ts](packages/desktop/src/main/store.ts)
- [packages/desktop/src/main/updater.ts](packages/desktop/src/main/updater.ts)
- [packages/opencode/src/cli/cmd/tui/app.tsx](packages/opencode/src/cli/cmd/tui/app.tsx)
- [packages/opencode/src/cli/cmd/tui/component/prompt/autocomplete.tsx](packages/opencode/src/cli/cmd/tui/component/prompt/autocomplete.tsx)
- [packages/opencode/src/cli/cmd/tui/component/prompt/index.tsx](packages/opencode/src/cli/cmd/tui/component/prompt/index.tsx)
- [packages/opencode/src/cli/cmd/tui/routes/session/index.tsx](packages/opencode/src/cli/cmd/tui/routes/session/index.tsx)
- [packages/opencode/src/cli/cmd/tui/util/clipboard.ts](packages/opencode/src/cli/cmd/tui/util/clipboard.ts)

</details>



BrowserCode provides three primary user interface surfaces designed for different workflows: a high-performance Terminal User Interface (TUI) for CLI-centric development, a cross-platform Desktop Application for a native experience, and a Web Application for browser-based access. All interfaces leverage a shared UI component library and synchronize state via the Core Engine's SDK.

## Interface Overview

The following diagram illustrates how the different UI surfaces interact with the core `opencode` services and the shared component architecture.

### UI to Code Entity Mapping
```mermaid
graph TD
    subgraph "Natural Language Space"
        "Terminal Interface"
        "Web Interface"
        "Desktop App"
    end

    subgraph "Code Entity Space (packages/)"
        direction LR
        subgraph "opencode/src/cli/cmd/tui"
            TUI_App["App.tsx"]
            TUI_Session["routes/session/index.tsx"]
        end

        subgraph "app/src"
            Web_Layout["pages/layout.tsx"]
            Web_Session["pages/session.tsx"]
            Web_Sync["context/global-sync.tsx"]
        end

        subgraph "desktop/src/main"
            Electron_Main["index.ts"]
            Sidecar["sidecar.ts"]
        end

        subgraph "ui/src"
            Shared_Comp["@opencode-ai/ui"]
        end
    end

    "Terminal Interface" --> TUI_App
    "Web Interface" --> Web_Layout
    "Desktop App" --> Electron_Main
    
    TUI_Session -.-> Shared_Comp
    Web_Session -.-> Shared_Comp
    Electron_Main --> Sidecar
    Sidecar --> TUI_App
```
**Sources:** [packages/opencode/src/cli/cmd/tui/app.tsx:161-170](), [packages/app/src/pages/layout.tsx:91-104](), [packages/desktop/src/main/index.ts:1-20](), [packages/desktop/src/main/sidecar.ts:1-10]()

---

## Terminal User Interface (TUI)

The TUI is built using `@opentui/solid`, a custom rendering stack that brings SolidJS-style reactive components to the terminal [packages/opencode/src/cli/cmd/tui/app.tsx:1-6](). It is designed for low-latency interactions and features a sophisticated `Prompt` component with support for extmarks, stash management, and frecency-based autocomplete [packages/opencode/src/cli/cmd/tui/component/prompt/index.tsx:26-34]().

**Key Components:**
*   **App Shell**: Manages the main TUI loop, keybinding registration, and terminal resizing [packages/opencode/src/cli/cmd/tui/app.tsx:121-142]().
*   **Session Route**: Handles the rendering of message timelines, tool outputs, and agent reasoning steps within the terminal [packages/opencode/src/cli/cmd/tui/routes/session/index.tsx:177-195]().
*   **Command Palette**: Provides a centralized interface for executing global commands and switching sessions [packages/opencode/src/cli/cmd/tui/app.tsx:75-119]().

For details, see [Terminal User Interface (TUI)](#4.1).

**Sources:** [packages/opencode/src/cli/cmd/tui/app.tsx:1-6](), [packages/opencode/src/cli/cmd/tui/component/prompt/index.tsx:136-150](), [packages/opencode/src/cli/cmd/tui/routes/session/index.tsx:121-155]()

---

## Web Application

The Web App is a SolidJS Single Page Application (SPA) located in `packages/app`. It serves as the foundation for both the standalone web interface and the UI rendered within the Desktop App [packages/app/src/pages/layout.tsx:91-104](). It utilizes a complex `GlobalSync` context to mirror state from the `opencode` server across multiple workspaces and sessions [packages/app/src/context/global-sync.tsx:81-110]().

**Core Features:**
*   **Session Management**: A detailed timeline view with auto-scrolling, history windowing, and message composition [packages/app/src/pages/session.tsx:88-101]().
*   **Prompt Input**: A rich `contenteditable` input supporting file "pills", image attachments, and slash commands [packages/app/src/components/prompt-input.tsx:104-125]().
*   **Layout Shell**: A persistent sidebar for project navigation, workspace switching, and global settings [packages/app/src/pages/layout.tsx:153-163]().

For details, see [Web App (packages/app)](#4.2).

**Sources:** [packages/app/src/pages/layout.tsx:91-104](), [packages/app/src/context/global-sync.tsx:10-28](), [packages/app/src/pages/session.tsx:45-60](), [packages/app/src/components/prompt-input.tsx:38-55]()

---

## Desktop Application

The Desktop App uses Electron to wrap the Web App, providing deeper OS integration [packages/desktop/src/main/index.ts:1-20](). It orchestrates the `opencode` server as a sidecar process and handles native features like deep-linking (`opencode://`), shell environment probing, and auto-updates [packages/desktop/src/main/sidecar.ts:1-10](), [packages/desktop/src/main/shell-env.ts:1-15]().

**System Integration:**
*   **Sidecar Orchestration**: Automatically starts and manages the lifecycle of the `opencode` binary [packages/desktop/src/main/server.ts:1-20]().
*   **IPC Handlers**: Facilitates communication between the Electron main process and the web frontend for operations like file system access and window management [packages/desktop/src/main/ipc.ts:1-15]().
*   **Titlebar**: A custom native-style titlebar that integrates with Tauri/Electron APIs for window controls and navigation history [packages/app/src/components/titlebar.tsx:42-64]().

For details, see [Desktop Application (Electron)](#4.3).

**Sources:** [packages/desktop/src/main/index.ts:1-20](), [packages/desktop/src/main/server.ts:1-20](), [packages/app/src/components/titlebar.tsx:17-37]()

---

## Shared UI Component Library

All interfaces share a common set of components defined in `@opencode-ai/ui`. This library ensures visual consistency and encapsulates complex logic for rendering AI-specific data structures [packages/app/src/pages/layout.tsx:22-30]().

| Component Category | Key Entities |
| :--- | :--- |
| **Session Rendering** | `SessionTurn`, `MessagePart`, `SessionReview` |
| **Diffing Engine** | `Pierre` (Worker-based WASM diffing), `Shiki` highlighting |
| **Input & Control** | `PromptInput`, `ResizeHandle`, `CommandPalette` |
| **Layout** | `DockShell`, `Sidebar`, `Titlebar` |

For details, see [Shared UI Component Library (packages/ui)](#4.4).

**Sources:** [packages/app/src/pages/layout.tsx:22-30](), [packages/app/src/pages/session.tsx:24-30](), [packages/app/src/components/prompt-input.tsx:21-28]()

---

