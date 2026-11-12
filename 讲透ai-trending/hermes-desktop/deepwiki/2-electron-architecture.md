<!-- source: DeepWiki mcp.deepwiki.com · repo fathah/hermes-desktop · page 2 Electron Architecture · fetched 2026-10-30 -->

# Electron Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [lat.md/lat.md](lat.md/lat.md)
- [lat.md/sidebar-navigation.md](lat.md/sidebar-navigation.md)
- [src/main/config.ts](src/main/config.ts)
- [src/main/hermes.ts](src/main/hermes.ts)
- [src/main/index.ts](src/main/index.ts)
- [src/main/ipc/register.ts](src/main/ipc/register.ts)
- [src/main/security.ts](src/main/security.ts)
- [src/preload/index.d.ts](src/preload/index.d.ts)
- [src/preload/index.ts](src/preload/index.ts)
- [src/renderer/src/assets/main.css](src/renderer/src/assets/main.css)
- [src/renderer/src/screens/Chat/Chat.tsx](src/renderer/src/screens/Chat/Chat.tsx)
- [src/renderer/src/screens/Layout/Layout.tsx](src/renderer/src/screens/Layout/Layout.tsx)
- [tests/electron-security.test.ts](tests/electron-security.test.ts)
- [tests/ipc-handlers.test.ts](tests/ipc-handlers.test.ts)

</details>



Hermes Desktop follows the standard Electron multi-process architecture, strictly separating system-level operations from the user interface. This separation ensures that the heavy lifting of managing the Hermes Python engine, local file system, and network requests does not block the UI thread and remains secure.

### Process Split Overview

The application is divided into three distinct layers:

1.  **Main Process**: The privileged Node.js environment responsible for window lifecycle, native API access, and orchestrating the Hermes engine.
2.  **Preload Bridge**: A secure gateway that exposes a limited, type-safe API to the renderer process while maintaining process isolation.
3.  **Renderer Process**: The React-based frontend that handles user interactions and displays data.

#### Process Interaction Diagram

This diagram illustrates how code entities across the three layers interact via IPC (Inter-Process Communication), specifically mapping frontend UI components to the backend handlers defined in the main process.

```mermaid
graph TD
    subgraph "Renderer Process (React)"
        [App.tsx] -- "calls" --> [HermesAPI]
        [Chat.tsx] -- "listens to" --> [onInstallProgress]
        [Layout.tsx] -- "calls" --> [getPublicConnectionRegistry]
    end

    subgraph "Preload Bridge (contextBridge)"
        [HermesAPI] -- "ipcRenderer.invoke" --> [ipcMain.handle]
        [ipcRenderer.on] -- "emits" --> [onInstallProgress]
        [ipcRenderer.invoke] -- "channel: get-public-connection-registry" --> [ipcMain.handle]
    end

    subgraph "Main Process (Node.js)"
        [ipcMain.handle] -- "routes to" --> [src/main/ipc/register.ts]
        [src/main/ipc/register.ts] -- "calls" --> [installer.ts]
        [src/main/ipc/register.ts] -- "calls" --> [hermes.ts]
        [src/main/ipc/register.ts] -- "calls" --> [config.ts]
        [installer.ts] -- "event.sender.send" --> [ipcRenderer.on]
    end
```
**Sources:** [src/main/ipc/register.ts:61-134](), [src/preload/index.ts:127-221](), [src/preload/index.d.ts:261-280](), [src/renderer/src/screens/Layout/Layout.tsx:110-112]()

---

### Main Process

The **Main Process** serves as the application's entry point, bootstrapped in `src/main/index.ts` [src/main/index.ts:1-21](). It manages the `BrowserWindow` instance and registers handlers for all IPC calls originating from the UI via `src/main/ipc/register.ts` [src/main/ipc/register.ts:1-261](). It has full access to Node.js built-ins, allowing it to manage the Hermes Python environment, local SQLite databases, and the file system.

Key responsibilities include:
*   **Window Management**: Creating the main window with security configurations like `sandbox: true`, `contextIsolation: true`, and `nodeIntegration: false` [tests/electron-security.test.ts:22-28]().
*   **IPC Handling**: Mapping frontend requests (e.g., `check-install`, `send-message`, `get-public-connection-registry`) to backend logic in modules like `installer.ts`, `hermes.ts`, or `config.ts` [src/main/ipc/register.ts:61-190]().
*   **Engine Control**: Managing the lifecycle of the Hermes gateway, SSH tunnels, and dashboard WebSocket transports [src/main/hermes.ts:131-155](), [src/main/dashboard.ts:134-154]().

For details, see [Main Process](#2.1).

**Sources:** [src/main/index.ts:1-21](), [src/main/ipc/register.ts:1-261](), [src/main/hermes.ts:1-155]()

---

### Preload Bridge (IPC API)

The **Preload Bridge** is the security boundary of the application. Using Electron's `contextBridge`, it exposes the `hermesAPI` object to the `window` global in the renderer process [src/preload/index.ts:1-127](). This ensures the renderer cannot access Node.js primitives directly, preventing Remote Code Execution (RCE) vulnerabilities.

The bridge defines a strict interface, `HermesAPI`, which includes:
*   **Invokers**: Asynchronous functions that return Promises (e.g., `checkInstall`, `startGateway`, `sendMessage`) [src/preload/index.ts:129-221]().
*   **Listeners**: Subscription-based patterns for streaming data, such as installation logs (`onInstallProgress`) or gateway events [src/preload/index.ts:164-188]().
*   **Type Safety**: Shared type definitions ensure that complex objects like `PublicConnectionConfig` or `KanbanTask` are handled consistently across the process boundary [src/preload/index.d.ts:89-207]().

For details, see [Preload Bridge (IPC API)](#2.2).

**Sources:** [src/preload/index.ts:1-221](), [src/preload/index.d.ts:1-261]()

---

### Renderer Entry and Routing

The **Renderer Process** is a React application bundled by Vite. It treats the `hermesAPI` provided by the preload script as its primary data source. The architecture uses a screen-state machine to manage the transition from initial setup to the main chat interface.

*   **Entry Point**: The application mounts and initializes the UI, utilizing the `ElectronAPI` for environment metadata [src/preload/index.ts:116-125]().
*   **Routing Logic**: The UI transitions through states such as `welcome`, `installing`, and `setup` based on the status returned by `hermesAPI.checkInstall()` [src/preload/index.ts:129-133]().
*   **Multi-Session Management**: `Layout.tsx` manages multiple `ChatRun` instances, allowing users to switch between active conversations and background sessions [src/renderer/src/screens/Layout/Layout.tsx:109-113]().

For details, see [Renderer Entry and Routing](#2.3).

**Sources:** [src/renderer/src/screens/Layout/Layout.tsx:1-197](), [src/renderer/src/screens/Chat/Chat.tsx:86-164]()

---

### Security Model

Hermes Desktop implements a defense-in-depth strategy to protect user data and the local system. Security policies are centralized in `src/main/security.ts` and verified by automated tests in `tests/electron-security.test.ts`.

#### Security Hardening Diagram

This diagram maps the security functions in `security.ts` to their application within the `BrowserWindow` creation and lifecycle.

```mermaid
graph LR
    subgraph "Main Process Security"
        [startMainProcess] -- "sets" --> [WebPreferences]
        [WebPreferences] -- "configures" --> [Sandbox: true]
        [WebPreferences] -- "configures" --> [ContextIsolation: true]
        
        [app.on: web-contents-created] -- "calls" --> [hardenAttachedWebContents]
        [hardenAttachedWebContents] -- "calls" --> [isAllowedWebviewUrl]
        [openExternalUrl] -- "calls" --> [isAllowedExternalUrl]
    end
```
**Sources:** [tests/electron-security.test.ts:22-59](), [src/main/security.ts:1-77]()

#### Security Features Table

| Feature | Implementation | Purpose |
| :--- | :--- | :--- |
| **Context Isolation** | `contextIsolation: true` | Prevents renderer access to preload internals or Node.js APIs [tests/electron-security.test.ts:24-24](). |
| **Sandbox** | `sandbox: true` | Restricts the renderer and preload process to a limited set of APIs [tests/electron-security.test.ts:25-25](). |
| **URL Allowlist** | `isAllowedExternalUrl` | Validates protocols (`https:`, `http:`, `mailto:`) before opening external links [tests/electron-security.test.ts:99-103](). |
| **Webview Hardening** | `hardenWebviewPreferences` | Strips preloads and forces isolation for embedded webviews [tests/electron-security.test.ts:50-50](). |
| **Navigation Control** | `isAllowedAppNavigationUrl` | Blocks the renderer from navigating away from the local `index.html` [tests/electron-security.test.ts:120-125](). |

**Sources:** [src/main/security.ts:1-77](), [tests/electron-security.test.ts:21-169]()

---

