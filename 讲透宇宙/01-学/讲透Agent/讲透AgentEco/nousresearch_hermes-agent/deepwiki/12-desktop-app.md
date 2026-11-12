<!-- source: DeepWiki mcp.deepwiki.com · repo nousresearch/hermes-agent · page 12 Desktop App · fetched 2026-10-27 -->

# Desktop App

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/desktop/electron/api-transport.test.ts](apps/desktop/electron/api-transport.test.ts)
- [apps/desktop/electron/api-transport.ts](apps/desktop/electron/api-transport.ts)
- [apps/desktop/electron/backend-health.test.ts](apps/desktop/electron/backend-health.test.ts)
- [apps/desktop/electron/backend-health.ts](apps/desktop/electron/backend-health.ts)
- [apps/desktop/electron/cloud-discovery.test.ts](apps/desktop/electron/cloud-discovery.test.ts)
- [apps/desktop/electron/cloud-discovery.ts](apps/desktop/electron/cloud-discovery.ts)
- [apps/desktop/electron/connection-config.test.ts](apps/desktop/electron/connection-config.test.ts)
- [apps/desktop/electron/connection-config.ts](apps/desktop/electron/connection-config.ts)
- [apps/desktop/electron/connection-registry.test.ts](apps/desktop/electron/connection-registry.test.ts)
- [apps/desktop/electron/connection-registry.ts](apps/desktop/electron/connection-registry.ts)
- [apps/desktop/electron/main.ts](apps/desktop/electron/main.ts)
- [apps/desktop/electron/native-auth-decisions.test.ts](apps/desktop/electron/native-auth-decisions.test.ts)
- [apps/desktop/electron/native-auth-decisions.ts](apps/desktop/electron/native-auth-decisions.ts)
- [apps/desktop/electron/preload.ts](apps/desktop/electron/preload.ts)
- [apps/desktop/src/app/chat/composer/types.ts](apps/desktop/src/app/chat/composer/types.ts)
- [apps/desktop/src/app/chat/sidebar/gateway-group-model.test.ts](apps/desktop/src/app/chat/sidebar/gateway-group-model.test.ts)
- [apps/desktop/src/app/chat/sidebar/gateway-group-model.ts](apps/desktop/src/app/chat/sidebar/gateway-group-model.ts)
- [apps/desktop/src/app/chat/sidebar/gateway-group-preferences.test.ts](apps/desktop/src/app/chat/sidebar/gateway-group-preferences.test.ts)
- [apps/desktop/src/app/chat/sidebar/gateway-group-preferences.ts](apps/desktop/src/app/chat/sidebar/gateway-group-preferences.ts)
- [apps/desktop/src/app/chat/sidebar/gateway-groups-drag.test.tsx](apps/desktop/src/app/chat/sidebar/gateway-groups-drag.test.tsx)
- [apps/desktop/src/app/chat/sidebar/gateway-groups.test.tsx](apps/desktop/src/app/chat/sidebar/gateway-groups.test.tsx)
- [apps/desktop/src/app/chat/sidebar/gateway-groups.tsx](apps/desktop/src/app/chat/sidebar/gateway-groups.tsx)
- [apps/desktop/src/app/chat/sidebar/reorderable-list.tsx](apps/desktop/src/app/chat/sidebar/reorderable-list.tsx)
- [apps/desktop/src/app/chat/sidebar/session-row-rename-drag.test.tsx](apps/desktop/src/app/chat/sidebar/session-row-rename-drag.test.tsx)
- [apps/desktop/src/app/contrib/latest-actions.test.ts](apps/desktop/src/app/contrib/latest-actions.test.ts)
- [apps/desktop/src/app/contrib/latest-actions.ts](apps/desktop/src/app/contrib/latest-actions.ts)
- [apps/desktop/src/app/contrib/surfaces.test.tsx](apps/desktop/src/app/contrib/surfaces.test.tsx)
- [apps/desktop/src/app/contrib/surfaces.tsx](apps/desktop/src/app/contrib/surfaces.tsx)
- [apps/desktop/src/app/contrib/types.ts](apps/desktop/src/app/contrib/types.ts)
- [apps/desktop/src/app/settings/cloud-team-change.ts](apps/desktop/src/app/settings/cloud-team-change.ts)
- [apps/desktop/src/app/settings/connections-registry.test.tsx](apps/desktop/src/app/settings/connections-registry.test.tsx)
- [apps/desktop/src/app/settings/connections-registry.tsx](apps/desktop/src/app/settings/connections-registry.tsx)
- [apps/desktop/src/app/settings/gateway-settings.test.tsx](apps/desktop/src/app/settings/gateway-settings.test.tsx)
- [apps/desktop/src/app/settings/gateway-settings.tsx](apps/desktop/src/app/settings/gateway-settings.tsx)
- [apps/desktop/src/components/boot-failure-cause.ts](apps/desktop/src/components/boot-failure-cause.ts)
- [apps/desktop/src/components/boot-failure-overlay.test.tsx](apps/desktop/src/components/boot-failure-overlay.test.tsx)
- [apps/desktop/src/components/boot-failure-overlay.tsx](apps/desktop/src/components/boot-failure-overlay.tsx)
- [apps/desktop/src/components/boot-failure-reauth.test.ts](apps/desktop/src/components/boot-failure-reauth.test.ts)
- [apps/desktop/src/components/boot-failure-reauth.ts](apps/desktop/src/components/boot-failure-reauth.ts)
- [apps/desktop/src/global.d.ts](apps/desktop/src/global.d.ts)
- [contributors/emails/RaviTharuma@users.noreply.github.com](contributors/emails/RaviTharuma@users.noreply.github.com)
- [website/docs/user-guide/desktop.md](website/docs/user-guide/desktop.md)
- [website/docs/user-guide/multi-connection-desktop.md](website/docs/user-guide/multi-connection-desktop.md)

</details>



The Hermes Desktop application is a native, cross-platform shell built on Electron that provides a high-performance graphical interface for the Hermes Agent core. It unifies the same agent that powers the CLI and gateway, sharing configuration, sessions, skills, and model interactions. The desktop app manages backend lifecycle, multi-profile connections, secure token storage, rich UI rendering, and system integration deep within the Electron environment [website/docs/user-guide/desktop.md:3-11]().

This page offers a high-level overview of the Desktop App’s architecture, gateway connection model, profile management, and bootstrapping via the Tauri installer. Detailed explanations of the Electron main process, React frontend, and windowing surfaces are provided in respective child pages:

- [Electron Shell and Gateway Connection](#12.1)
- [Desktop UI Components](#12.2)
- [HUD, Panes, and Window Management](#12.3)

---

## System Architecture

Hermes Desktop cleanly separates platform-native processes from the renderer UI to maintain security, performance, and modularity [apps/desktop/electron/preload.ts:1-13]().

### Process Model and Responsibilities

| Process / Component | Role | Key Code Entities and Locations |
|---|---|---|
| **Electron Main Process** | Native shell integration: manages gateway backend lifecycle (local/remote/ssh/cloud), connection registry, secure token storage, WebSocket health probes, OAuth network hooks, desktop updates, and plugin SDK support. | `apps/desktop/electron/main.ts` [1-192]() |
| **Renderer Process (React UI)**| Hosts React frontend: chat UI, session management, command palette, profile switching, and gateway wiring. Communicates with main process via IPC bridge exposed in preload. | `apps/desktop/electron/preload.ts` [27-69](), `apps/desktop/src/global.d.ts` [33-134]() |
| **Tauri Bootstrap Installer** | Lightweight native bootstrap app for first-time installs and dependency provisioning before launching Hermes Desktop native shell. | `apps/bootstrap-installer/package.json`() |

### Desktop App Architecture Diagram

```mermaid
graph TD
    subgraph "Electron_Main_Process_(Native_Space)"
        Main["apps/desktop/electron/main.ts"]
        ConnRegistry["apps/desktop/electron/connection-registry.ts"]
        SafeStorage["Electron safeStorage API"]
        IPCMain["ipcMain (IPC Bridge)"]
        GatewayProbe["local-gateway.ts (WebSocket Probe)"]
        BackendSpawner["backend-child.ts"]
        ConnectionConfig["apps/desktop/electron/connection-config.ts"]
    end

    subgraph "Renderer_Process_(React_UI)"
        PreloadBridge["apps/desktop/electron/preload.ts → window.hermesDesktop"]
        ReactComponents["React UI Components"]
        Nanostores["nanostores State Management"]
        GatewaySettingsUI["apps/desktop/src/app/settings/gateway-settings.tsx"]
        ConnectionsRegistryUI["apps/desktop/src/app/settings/connections-registry.tsx"]
    end

    Main -->|"spawns/manages"| BackendSpawner
    Main -->|"uses"| ConnRegistry
    Main -->|"probes & validates"| GatewayProbe
    Main -->|"configures"| ConnectionConfig
    IPCMain -->|"exposes APIs via"| PreloadBridge
    PreloadBridge -->|"invokes connection logic"| Main
    PreloadBridge -->|"invokes connection logic"| ConnRegistry
    PreloadBridge -->|"invokes connection logic"| ConnectionConfig
    ReactComponents --> Nanostores
    Nanostores --> PreloadBridge
    GatewaySettingsUI --> Nanostores
    ConnectionsRegistryUI --> Nanostores
    ConnectionsRegistryUI -->|"uses"| ConnectionConfig
```

This architecture ensures secure bridging of UI and native backend lifecycles and supports sophisticated multi-profile and multi-backend scenarios.

Sources: [apps/desktop/electron/main.ts:1-192](), [apps/desktop/electron/preload.ts:27-69](), [apps/desktop/src/global.d.ts:33-134](), [apps/desktop/electron/connection-registry.ts:1-178](), [apps/desktop/electron/connection-config.ts:1-161](), [apps/desktop/src/app/settings/gateway-settings.tsx:1-205](), [apps/desktop/src/app/settings/connections-registry.tsx:1-193]()

---

## Core Functional Areas

### 1. Electron Shell and Gateway Connection

The Electron main process is the desktop application's native core that manages:

- **Backend Child Processes:** Spawning and monitoring Hermes agent gateway backends locally or handling remote backend connections transparently.
- **Multi-Connection Registry:** Tracks multiple backend profiles—local, remote HTTP(S), SSH, or cloud-hosted—with distinct authentication and routing. This enables concurrent multi-profile workflows [apps/desktop/electron/connection-registry.ts:1-28](). The registry is versioned and handles migrations from older configurations [apps/desktop/electron/connection-registry.ts:40-41]().
- **Gateway WebSocket Probe:** Implements health checks on backend gateway availability and authentication status to maintain connectivity and react to failures early. This includes handling OAuth ticket minting and transport failures [apps/desktop/electron/connection-config.ts:91-146]().
- **Secure Token Storage:** Uses Electron’s `safeStorage` API to encrypt and store credentials locally.
- **IPC Bridge and API Exposure:** Exposes a set of IPC methods bridged through the Electron preload script to allow renderer processes to request backend connections, revalidate their state after wake/sleep, retrieve profile routes visible to plugins, and manage session windows [apps/desktop/electron/preload.ts:27-69]().
- **OAuth Network Request Handling:** Intercepts and handles OAuth flows within the desktop environment, including managing session cookies and refresh tokens [apps/desktop/electron/connection-config.ts:21-36]().
- **Updater and Plugin SDK:** Coordinates desktop auto-update processes and plugin integration for extensibility.

This subsystem is crucial for ensuring robust connection lifecycle management, multi-profile routing, and seamless backend integration.

For detailed implementation, refer to [Electron Shell and Gateway Connection](#12.1).

Sources: [apps/desktop/electron/connection-registry.ts:1-28](), [apps/desktop/electron/connection-registry.ts:40-41](), [apps/desktop/electron/connection-config.ts:21-36](), [apps/desktop/electron/connection-config.ts:91-146](), [apps/desktop/electron/preload.ts:27-69]()

---

### 2. Desktop UI Components and Profile Management

The renderer hosts the React-based user interface, providing a modern chat-centric experience:

- **Chat Composer and Rich Editor:** Featuring streaming AI responses, structured real-time tool outputs, Markdown-compatible editing, and drag/drop attachments [website/docs/user-guide/desktop.md:41-55]().
- **Session Sidebar and Action Hooks:** Allows managing concurrent conversations and interacting via prompts and commands. The sidebar organizes sessions by gateway and profile, allowing reordering and renaming of groups [website/docs/user-guide/multi-connection-desktop.md:85-101]().
- **Profile Switcher:** Logical abstraction encapsulating backend gateway connections. Profiles isolate backend URLs, authentication tokens, headers, and routing preferences per user context such as organization or deployment target [apps/desktop/src/global.d.ts:33-50](). The UI provides a dedicated "Gateways" settings page for managing these connections [website/docs/user-guide/multi-connection-desktop.md:19-26]().
- **State Management:** Uses nanostores to maintain UI and backend state, syncing with IPC bridge APIs for backend and profile resolution.
- **Auxiliary UI Features:** Command palette, model selection menu with metadata, settings panels for extensive configuration (appearance, security, gateway, advanced options) [website/docs/user-guide/desktop.md:35-79]().

Profiles unify the various connection modes (local, remote HTTP, SSH) into a single identity model, allowing users to effortlessly switch contexts while preserving secure and isolated states. The connection registry handles deduplication of remote and SSH connections based on normalized URLs and host configurations [apps/desktop/src/app/settings/connections-registry.tsx:126-165]().

For comprehensive coverage of React components, profile workflows, state usage, and UI hooks, see [Desktop UI Components](#12.2).

Sources: [website/docs/user-guide/desktop.md:35-79](), [website/docs/user-guide/desktop.md:41-55](), [website/docs/user-guide/multi-connection-desktop.md:19-26](), [website/docs/user-guide/multi-connection-desktop.md:85-101](), [apps/desktop/src/global.d.ts:33-50](), [apps/desktop/src/app/settings/connections-registry.tsx:126-165]()

---

### 3. HUD, Panes, and Window Management

Hermes Desktop supports advanced windowing on multiple operating systems with features including:

- **Chrome-less HUD Shell:** Floating translucent chat windows with platform-native glass effects for aesthetic and accessibility enhancements [apps/desktop/electron/preload.ts:29-30]().
- **Quick Entry Overlay:** Lightweight global hotkey invoked prompt input accessible above other applications.
- **Pet Overlay:** An animated desktop mascot capable of drag, focus management, and state updates [apps/desktop/electron/preload.ts:90-117]().
- **Pop-Out Browser Windows:** Enables detaching chat-preview tabs as independent native OS windows with bidirectional state syncing [apps/desktop/electron/preload.ts:54-69]().
- **Pane-Shell Tree Layout:** Supports hierarchical, split, and floating panes allowing complex multitasking and workspace organization.
- **Global Styles and Window State:** Central handling of window state, resizing modes, and style theming consistent across windowing surfaces [apps/desktop/src/global.d.ts:109-110]().

All window and overlay operations route through IPC communication between renderer and main process to maintain synchronized UI and backend states.

See [HUD, Panes, and Window Management](#12.3) for a full technical treatment.

Sources: [apps/desktop/electron/preload.ts:29-30](), [apps/desktop/electron/preload.ts:54-69](), [apps/desktop/electron/preload.ts:90-117](), [apps/desktop/src/global.d.ts:109-110]()

---

## UI Component to Code Entity Mapping

This diagram bridges natural language UI concepts to concrete code entities and Electron IPC layers, facilitating comprehension of the desktop app’s reactive and native coordination:

```mermaid
graph LR
  subgraph "Renderer_UI_Components"
    ChatUI["src/app/chat/index.tsx"]
    Composer["src/app/chat/composer/index.tsx"]
GatewaySettingsUI["src/app/settings/gateway-settings.tsx"]
ConnectionsRegistryUI["src/app/settings/connections-registry.tsx"]
  end

  subgraph "State_Stores_(Nanostores)"
    ActiveConnectionIdStore["store/connections.ts:$activeConnectionId"]
    ConnectionsRegistryStore["store/connections.ts:$connectionsRegistry"]
    GatewaySettingsState["apps/desktop/src/app/settings/gateway-settings.tsx:GatewaySettingsState"]
  end

  subgraph "Electron_Main_IPC"
    PreloadBridge["electron/preload.ts (window.hermesDesktop)"]
    MainProcess["electron/main.ts"]
    ConnectionConfigModule["electron/connection-config.ts"]
    ConnectionRegistryModule["electron/connection-registry.ts"]
  end

  ChatUI --> ActiveConnectionIdStore
  Composer --> ActiveConnectionIdStore
  GatewaySettingsUI --> GatewaySettingsState
  GatewaySettingsUI --> ConnectionsRegistryStore
  ConnectionsRegistryUI --> ConnectionsRegistryStore

  ActiveConnectionIdStore --> PreloadBridge
  ConnectionsRegistryStore --> PreloadBridge
  GatewaySettingsState --> PreloadBridge

  PreloadBridge -- "hermes:connection:for" --> MainProcess
  PreloadBridge -- "hermes:gateway:ws-url-for" --> MainProcess
  PreloadBridge -- "hermes:agents:roster" --> MainProcess
  PreloadBridge -- "hermes:connection:revalidate" --> MainProcess
  MainProcess -- "uses" --> ConnectionConfigModule
  MainProcess -- "uses" --> ConnectionRegistryModule
```

- React UI components rely on nanostores for managing their state.
- Nanostores coordinate backend and profile management through Electron's IPC bridge `window.hermesDesktop`.
- The Electron main process exposes native backend lifecycle and connection management APIs to the renderer, leveraging modules like `connection-config.ts` and `connection-registry.ts`.

Sources: [apps/desktop/electron/preload.ts:27-69](), [apps/desktop/src/global.d.ts:33-50](), [apps/desktop/src/app/settings/gateway-settings.tsx:59-81](), [apps/desktop/src/app/settings/connections-registry.tsx:1-193](), [apps/desktop/src/store/connections.ts:38-42](), [apps/desktop/electron/connection-config.ts:1-161](), [apps/desktop/electron/connection-registry.ts:1-178]()

---

## References and Further Reading

- Detailed Electron main process integration and gateway connection management: [Electron Shell and Gateway Connection](#12.1)
- React UI architecture and state management: [Desktop UI Components](#12.2)
- Windowing, overlays, HUD, and pane engine internals: [HUD, Panes, and Window Management](#12.3)
- Localization messages live under `apps/desktop/src/i18n/` covering multiple languages [apps/desktop/src/i18n/types.ts:1-10]()

---

Sources:
[apps/bootstrap-installer/package.json]()
[apps/desktop/electron/connection-config.ts:1-161]()
[apps/desktop/electron/connection-registry.ts:1-178]()
[apps/desktop/electron/main.ts:1-192]()
[apps/desktop/electron/preload.ts:1-117]()
[apps/desktop/src/app/settings/connections-registry.tsx:1-193]()
[apps/desktop/src/app/settings/gateway-settings.tsx:1-205]()
[apps/desktop/src/global.d.ts:33-134]()
[apps/desktop/src/i18n/types.ts:1-10]()
[apps/desktop/src/store/connections.ts:38-42]()
[website/docs/user-guide/desktop.md:3-79]()
[website/docs/user-guide/multi-connection-desktop.md:19-101]()

---

