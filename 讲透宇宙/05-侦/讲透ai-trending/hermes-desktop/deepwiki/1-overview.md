<!-- source: DeepWiki mcp.deepwiki.com · repo fathah/hermes-desktop · page 1 Overview · fetched 2026-10-30 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitattributes](.gitattributes)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [Development.md](Development.md)
- [README.md](README.md)
- [assets/header.webp](assets/header.webp)
- [assets/partners/atlascloud.webp](assets/partners/atlascloud.webp)
- [assets/partners/greptile.webp](assets/partners/greptile.webp)
- [build/linux-after-install.sh](build/linux-after-install.sh)
- [electron-builder.yml](electron-builder.yml)
- [eslint.config.mjs](eslint.config.mjs)
- [lat.md/lat.md](lat.md/lat.md)
- [lat.md/sidebar-navigation.md](lat.md/sidebar-navigation.md)
- [package-lock.json](package-lock.json)
- [package.json](package.json)
- [previews/discover.png](previews/discover.png)
- [previews/memory.png](previews/memory.png)
- [previews/sessions.png](previews/sessions.png)
- [src/main/config.ts](src/main/config.ts)
- [src/main/default-models.ts](src/main/default-models.ts)
- [src/main/hermes.ts](src/main/hermes.ts)
- [src/main/index.ts](src/main/index.ts)
- [src/main/ipc/register.ts](src/main/ipc/register.ts)
- [src/preload/index.d.ts](src/preload/index.d.ts)
- [src/preload/index.ts](src/preload/index.ts)
- [src/renderer/src/assets/main.css](src/renderer/src/assets/main.css)
- [src/renderer/src/screens/Chat/Chat.tsx](src/renderer/src/screens/Chat/Chat.tsx)
- [src/renderer/src/screens/Chat/FileViewer.tsx](src/renderer/src/screens/Chat/FileViewer.tsx)
- [src/renderer/src/screens/Chat/HistoryRow.tsx](src/renderer/src/screens/Chat/HistoryRow.tsx)
- [src/renderer/src/screens/Chat/MessageList.tsx](src/renderer/src/screens/Chat/MessageList.tsx)
- [src/renderer/src/screens/Chat/WorktreePanel.tsx](src/renderer/src/screens/Chat/WorktreePanel.tsx)
- [src/renderer/src/screens/Layout/Layout.tsx](src/renderer/src/screens/Layout/Layout.tsx)

</details>



Hermes Desktop is a native cross-platform application designed to manage, configure, and interact with the [Hermes Agent](https://github.com/NousResearch/hermes-agent) ecosystem [README.md:44-47](). It provides a graphical interface for a complex backend that handles multi-provider LLM orchestration, tool use, memory persistence, and multi-platform messaging gateways [README.md:136-139]().

The application is built on Electron and follows a multi-process architecture to ensure security and performance when handling streaming AI responses and local system operations [src/main/index.ts:1-21]().

### High-Level Architecture

Hermes Desktop bridges the gap between a high-level React UI and a Python-based agent backend. It utilizes a local API gateway to facilitate communication between the desktop interface and the underlying Hermes engine, supporting local execution, remote server connections via HTTP, or secure SSH tunnels [src/main/hermes.ts:131-148](), [src/main/hermes.ts:150-155]().

**System Context Diagram**

```mermaid
graph TD
  subgraph "User Interface (Renderer Process)"
    "UI[React UI / src/renderer]"
  end

  subgraph "Application Core (Main Process)"
    "IPC[IPC Handlers / src/main/ipc/register.ts]"
    "GW[Gateway Manager / src/main/hermes.ts]"
    "INST[Installer Service / src/main/installer.ts]"
    "SSH[SSH Tunnel / src/main/ssh-tunnel.ts]"
    "DASH[Dashboard / src/main/dashboard.ts]"
  end

  subgraph "Hermes Engine (Local or Remote)"
    "AG[Hermes Agent]"
    "API[Hermes API :8642]"
    "FS[~/.hermes File System]"
  end

  "UI" <-- "Exposed API via ContextBridge / src/preload" --> "IPC"
  "IPC" --> "GW"
  "IPC" --> "INST"
  "IPC" --> "SSH"
  "IPC" --> "DASH"
  "GW" <-- "SSE / HTTP" --> "API"
  "API" <-- "Orchestration" --> "AG"
  "AG" <-- "State/Config" --> "FS"
```
Sources: [README.md:44-47](), [src/main/hermes.ts:131-148](), [src/main/ipc/register.ts:116-140](), [src/preload/index.ts:127-221]()

### Key Capabilities

The system is organized into several major functional areas:

*   **Installation & Environment**: Automated setup of the Hermes environment in `~/.hermes`, including dependency resolution, "Hermes Doctor" diagnostics, and environment validation [src/main/ipc/register.ts:61-79](), [README.md:138-138]().
*   **Chat & Orchestration**: A streaming interface supporting SSE (Server-Sent Events), reasoning extraction, and real-time tool progress tracking [src/renderer/src/screens/Chat/Chat.tsx:146-164](), [src/preload/index.d.ts:261-300]().
*   **Data Management**: Persistence layers for conversation sessions, profile-scoped memory entries, and persona management via `SOUL.md` [src/main/ipc/register.ts:210-215](), [src/main/ipc/register.ts:265-270]().
*   **Connectivity & Wallets**: Management of messaging gateways and LLM providers [src/main/ipc/register.ts:116-126](), alongside a profile-scoped Ethereum wallet system on Base mainnet [src/preload/index.d.ts:7-14]().
*   **Automation & Visualization**: A built-in cron job scheduler [src/main/ipc/register.ts:285-290]() and the Hermes Office (Claw3D) visual interface featuring a 3D R3F scene and Kanban task management [src/renderer/src/screens/Layout/Layout.tsx:21-33](), [src/preload/index.d.ts:177-207]().

### Subsystem Relationships

The application transitions through distinct states, from initial installation to active agent management. Communication is strictly mediated via IPC (Inter-Process Communication) handlers registered in the main process.

**Code Entity Mapping: Process Communication**

```mermaid
graph LR
  subgraph "Renderer Space (src/renderer/src)"
    "App.tsx[App Entry]"
    "Chat.tsx[Chat UI]"
    "Layout.tsx[Main Shell]"
  end

  subgraph "Preload Bridge (src/preload)"
    "hermesAPI[hermesAPI / index.ts]"
  end

  subgraph "Main Space (src/main)"
    "register.ts[IPC Handler Registration]"
    "hermes.ts[sendMessage / startGateway]"
    "installer.ts[runInstall / checkInstallStatus]"
    "config.ts[readEnv / getModelConfig]"
    "ssh-tunnel.ts[startSshTunnel]"
  end

  "App.tsx" --> "hermesAPI"
  "hermesAPI" -- "ipcRenderer.invoke" --> "register.ts"
  "register.ts" -- "calls" --> "hermes.ts"
  "register.ts" -- "calls" --> "installer.ts"
  "register.ts" -- "calls" --> "config.ts"
  "register.ts" -- "calls" --> "ssh-tunnel.ts"
```
Sources: [src/main/ipc/register.ts:1-261](), [src/preload/index.ts:127-221](), [src/renderer/src/screens/Layout/Layout.tsx:1-33]()

### Navigation and Documentation

This wiki is structured to provide both high-level conceptual overviews and deep technical dives into specific subsystems.

#### [Getting Started](#1.1)
Covers the prerequisites and the initial onboarding flow, including the transition from the `Welcome` screen to the `Install` and `Setup` phases. It explains how the app handles local vs. remote backend modes. For details, see [Getting Started](#1.1).

#### [Project Structure and Build System](#1.2)
Detailed breakdown of the repository layout (main, preload, renderer, shared), the `electron-vite` build pipeline, and how the application is packaged for macOS, Linux, and Windows using `electron-builder`. For details, see [Project Structure and Build System](#1.2).

#### Further Sections
*   **Electron Architecture**: Deep dive into IPC patterns, the `hermesAPI` bridge, and process lifecycles.
*   **Hermes Engine Integration**: Details on the Gateway lifecycle, Installer environment setup, and profile-scoped configuration.
*   **Agent Features and Data Layer**: Exploration of the memory system, soul management, skills registry, and SQLite-backed session cache.
*   **User Interface**: Documentation of the React component library, i18n localization system, and specialized screens like the Kanban board and 3D Office.
*   **Testing and CI/CD**: Overview of the Vitest suites and the multi-platform GitHub Actions release pipeline.

Sources: [package.json:8-31](), [src/main/ipc/register.ts:1-261](), [lat.md/sidebar-navigation.md:1-46]()

---

