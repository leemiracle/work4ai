<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/iCode · page 8 Application Layer: TUI, CLI and ACP · fetched 2026-11-02 -->

# Application Layer: TUI, CLI and ACP

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/chrys/app/acp/doc/frontend-api.md](src/chrys/app/acp/doc/frontend-api.md)
- [src/chrys/app/acp/transport.py](src/chrys/app/acp/transport.py)
- [src/chrys/app/cli/acp.py](src/chrys/app/cli/acp.py)
- [src/chrys/app/tui/app.py](src/chrys/app/tui/app.py)
- [src/chrys/app/tui/screens/dialogs/approval/bodies/file_edit.py](src/chrys/app/tui/screens/dialogs/approval/bodies/file_edit.py)
- [src/chrys/app/tui/screens/dialogs/approval/dialog.py](src/chrys/app/tui/screens/dialogs/approval/dialog.py)
- [tests/app/tui/behaviors/test_app_startup.py](tests/app/tui/behaviors/test_app_startup.py)

</details>



The Application Layer serves as the user-facing and external integration tier of iCode (`chrys`). Its primary architectural principle is a **shared backend runtime** (`AgentEngine` and `ChrysSessionHost`) driven entirely by an internal `EventBus` [src/chrys/app/acp/doc/frontend-api.md:14-15](), allowing multiple distinct frontends to provide feature parity without duplicating agent logic or engine rules. 

Three frontends consume this single backend:
1. **Textual TUI (`ChrysApp`)** — Subscribes directly to `EventBus` events in-process and drives the orchestration runtime [src/chrys/app/tui/app.py:6-7]().
2. **CLI (`icode`)** — Executes one-shot commands, interactive headless loops, workflows, and serves protocols [src/chrys/app/cli/acp.py:37-41]().
3. **ACP Server (`ChrysAcpServer`)** — Exposes standard Agent Client Protocol methods and custom extensions over stdio for external editors like VS Code [src/chrys/app/acp/doc/frontend-api.md:3-8]().

```mermaid
title "Frontend-to-Backend Architecture and EventBus Flow"
graph TD
    sub0["Natural Language Space"] --> CodeSpace["Code Entity Space"]
    
    subgraph CodeSpace ["Code Entity Space"]
        TUI["ChrysApp\n(src/chrys/app/tui/app.py)"]
        CLI["CLI Commands\n(src/chrys/app/cli)"]
        ACP["ChrysAcpServer\n(src/chrys/app/acp/server.py)"]
        
        Bus["EventBus\n(chrys.foundation.events.bus)"]
        
        Engine["AgentEngine & ChrysSessionHost\n(chrys.orchestration.engine)"]
    end

    TUI -->|"Subscribes & Calls"| Bus
    ACP -->|"Bridges RPC / Events"| Bus
    CLI -->|"Invokes Runner"| Engine
    Bus --> Engine
```
Sources: `src/chrys/app/acp/doc/frontend-api.md:14-22`, `src/chrys/app/tui/app.py:6-7`, `src/chrys/app/cli/acp.py:18-20`

---

## 8.1 TUI Main Screen and Controllers

The main screen wiring establishes the central workspace UI in Textual, handling view adapters, dialog gateways, event handlers, and workflow run controls. It manages active session states, model profile indicators, and real-time turn execution updates.

For deep technical details, see [TUI Main Screen and Controllers](#8.1) (Child Page).

Sources: `src/chrys/app/tui/app.py:40-44`

---

## 8.2 TUI Widgets: Chat, Input and Renderers

The chat subsystem features scrollable replay histories, enhanced text input areas supporting multi-line commands, and specialized tool-call cards. It includes rendering components for diff views, code blocks, structured payloads, and embedded image attachments.

For deep technical details, see [TUI Widgets: Chat, Input and Renderers](#8.2) (Child Page).

Sources: `src/chrys/app/tui/screens/dialogs/approval/bodies/file_edit.py:47-92`

---

## 8.3 TUI Dialogs and Screens

Modal interfaces and auxiliary screens handle sensitive operations such as tool call approvals [src/chrys/app/tui/screens/dialogs/approval/dialog.py:3-4](), profile configurations, file picking, session browser management, built-in user guides, and visual theme selectors.

For deep technical details, see [TUI Dialogs and Screens](#8.3) (Child Page).

Sources: `src/chrys/app/tui/screens/dialogs/approval/dialog.py:3-23`

---

## 8.4 Trajectory Dashboard and Analytics

The trajectory sub-system provides timeline visualization, chart-kit widgets, and turn-graph analytics. It computes insights and findings from historical agent executions to help users diagnose model reasoning paths.

For deep technical details, see [Trajectory Dashboard and Analytics](#8.4) (Child Page).

Sources: `src/chrys/app/tui/app.py:36-39`

---

## 8.5 Terminal, Themes and App Shell

Bootstrap sequences initialize Textual application runtimes, custom stylesheets (`.tcss`), ANSI variable maps, terminal title synchronization, notification services, and spinner states. It ensures correct terminal cleanup and restoration upon exit.

For deep technical details, see [Terminal, Themes and App Shell](#8.5) (Child Page).

Sources: `src/chrys/app/tui/app.py:139-154`, `tests/app/tui/behaviors/test_app_startup.py:87-122`

---

## 8.6 CLI Commands

The `icode` entry point exposes subcommands for running interactive sessions, headless automation, ACP server processes [src/chrys/app/cli/acp.py:39-41](), approval policy adjustments, profile listings, workflow coordination, trajectory exports, and update checks.

For deep technical details, see [CLI Commands](#8.6) (Child Page).

Sources: `src/chrys/app/cli/acp.py:37-69`

---

## 8.7 ACP Server and Frontend API

The Agent Client Protocol server (`ChrysAcpServer`) and session manager (`AcpSessionManager`) bridge external JSON-RPC clients to the iCode engine [src/chrys/app/acp/doc/frontend-api.md:14-19](). They implement standard lifecycle methods alongside custom `ext_method` and `ext_notification` namespaces, supported by `AbortableMessageSender` for robust teardown semantics [src/chrys/app/acp/transport.py:13-35]().

```mermaid
title "ACP Server Integration & RPC Flow"
graph TD
    Client["External ACP Client\n(e.g., VS Code Extension)"] -->|"JSON-RPC (stdio)"| Connection["AgentSideConnection\n(acp.agent.connection)"]
    
    subgraph CodeSpace ["Code Entity Space"]
        Connection --> Server["ChrysAcpServer\n(src/chrys/app/acp/server.py)"]
        Server --> Manager["AcpSessionManager\n(src/chrys/app/acp/session_manager.py)"]
        Manager --> Host["ChrysSessionHost\n(chrys.orchestration)"]
        Server --> Sender["AbortableMessageSender\n(src/chrys/app/acp/transport.py)"]
    end

    Server -->|"ext_method / std methods"| Manager
    Sender -->|"Discard unsent on close"| Connection
```
Sources: `src/chrys/app/acp/doc/frontend-api.md:7-8`, `src/chrys/app/cli/acp.py:133-171`, `src/chrys/app/acp/transport.py:13-20`

For deep technical details, see [ACP Server and Frontend API](#8.7) (Child Page).

Sources: `src/chrys/app/acp/doc/frontend-api.md:1-129`, `src/chrys/app/acp/transport.py:13-36`

---

