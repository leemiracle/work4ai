<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/intelligent-terminal · page 1 Intelligent Terminal: Overview · fetched 2026-10-26 -->

# Intelligent Terminal: Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/spelling/allow/allow.txt](.github/actions/spelling/allow/allow.txt)
- [.github/actions/spelling/allow/apis.txt](.github/actions/spelling/allow/apis.txt)
- [.github/actions/spelling/allow/microsoft.txt](.github/actions/spelling/allow/microsoft.txt)
- [.github/actions/spelling/allow/names.txt](.github/actions/spelling/allow/names.txt)
- [.github/actions/spelling/expect/expect.txt](.github/actions/spelling/expect/expect.txt)
- [AGENTS.md](AGENTS.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [SUPPORT.md](SUPPORT.md)
- [TelemetryEvents.md](TelemetryEvents.md)
- [doc/building.md](doc/building.md)
- [doc/faq.md](doc/faq.md)
- [doc/roadmap-2022.md](doc/roadmap-2022.md)
- [doc/roadmap-2023.md](doc/roadmap-2023.md)
- [doc/specs/#1571 - New Tab Menu Customization/#1571 - New Tab Menu Customization.md](doc/specs/#1571 - New Tab Menu Customization/#1571 - New Tab Menu Customization.md)
- [doc/specs/#1571 - New Tab Menu Customization/Menu-Customization-000.png](doc/specs/#1571 - New Tab Menu Customization/Menu-Customization-000.png)
- [doc/specs/#1595 - Suggestions UI/Suggestions-UI.md](doc/specs/#1595 - Suggestions UI/Suggestions-UI.md)
- [doc/specs/#2046 - Command Palette.md](doc/specs/#2046 - Command Palette.md)
- [doc/specs/#2046 - Unified keybindings and commands, and synthesized action names.md](doc/specs/#2046 - Unified keybindings and commands, and synthesized action names.md)
- [doc/specs/#4066 - Theme-controlled color scheme switch.md](doc/specs/#4066 - Theme-controlled color scheme switch.md)
- [doc/specs/#653 - Quake Mode/#653 - Quake Mode.md](doc/specs/#653 - Quake Mode/#653 - Quake Mode.md)
- [doc/specs/#6899 - Action IDs/#6899 - Action IDs.md](doc/specs/#6899 - Action IDs/#6899 - Action IDs.md)
- [doc/specs/#6899 - Action IDs/data-mockup-actions-ids-keys-maps.png](doc/specs/#6899 - Action IDs/data-mockup-actions-ids-keys-maps.png)
- [doc/specs/connection-resilience.md](doc/specs/connection-resilience.md)
- [doc/terminal-a11y-2023.md](doc/terminal-a11y-2023.md)
- [doc/terminal-v2-roadmap.md](doc/terminal-v2-roadmap.md)
- [images/intelligent-terminal-agent-focus.png](images/intelligent-terminal-agent-focus.png)
- [res/README.md](res/README.md)
- [res/fonts/CascadiaCode.ttf](res/fonts/CascadiaCode.ttf)
- [res/fonts/CascadiaCodeItalic.ttf](res/fonts/CascadiaCodeItalic.ttf)
- [res/fonts/CascadiaMono.ttf](res/fonts/CascadiaMono.ttf)
- [res/fonts/CascadiaMonoItalic.ttf](res/fonts/CascadiaMonoItalic.ttf)
- [res/fonts/README.md](res/fonts/README.md)
- [src/cascadia/CascadiaResources.build.items](src/cascadia/CascadiaResources.build.items)
- [tools/bcz.cmd](tools/bcz.cmd)
- [tools/bx.ps1](tools/bx.ps1)

</details>



Intelligent Terminal is an experimental fork of [Windows Terminal](https://github.com/microsoft/terminal) that introduces native AI agent integration directly into the terminal experience [README.md:39-41](). It is designed to work with any agent CLI compatible with the **Agent Client Protocol (ACP)** [README.md:43-43]().

While inheriting the high-performance rendering engine, settings model, and terminal emulation from Windows Terminal, Intelligent Terminal adds a specialized "Natural Language Space" that interacts with the traditional "Code Entity Space" (the shell and terminal buffer).

## Key Features and Differences

Unlike the standard Windows Terminal, Intelligent Terminal provides:
*   **Agent Pane:** A context-aware, docked XAML pane (`AgentPaneContent`) that hosts an AI agent CLI with full access to the terminal's scrollback buffer [README.md:135-141]().
*   **WTA (Windows Terminal Agent):** A specialized Rust-based binary (`wta.exe`) that acts as a bridge between the terminal UI and various AI agents [README.md:43-43]().
*   **Automatic Error Detection:** Integration with shell execution (via OSC 133 marks) to detect non-zero exit codes and suggest fixes via the status bar [README.md:127-133]().
*   **Agent Management:** A dedicated UI for tracking active sessions, history, and background agent tasks [README.md:149-155]().

## Architectural Layers

The system is organized into three primary conceptual layers that bridge the gap between user intent and terminal execution.

### High-Level Architecture Diagram
This diagram illustrates the relationship between the UI components and the background agent processes.

```mermaid
graph TD
    subgraph "UI Layer (XAML/C++)"
        [TerminalPage] --> [AgentPaneContent]
        [TerminalPage] --> [TermControl]
        [AgentPaneContent] --> [SharedWta]
    end

    subgraph "Agent Space (Rust/JSON-RPC)"
        [SharedWta] -- "ACP Protocol" --> [WTA_Binary]
        [WTA_Binary] -- "stdio JSON-RPC" --> [Agent_CLI]
    end

    subgraph "Data Bridge (COM)"
        [Agent_CLI] -- "IProtocolServer" --> [TerminalProtocolComServer]
        [TerminalProtocolComServer] --> [TextBuffer]
    end

    style [WTA_Binary] stroke-dasharray: 5 5
    style [Agent_CLI] stroke-dasharray: 5 5
```
Sources: [README.md:135-155](), [CONTRIBUTING.md:7-7]()

### Bridging Natural Language to Code Entities
The following diagram maps how user interactions in the "Natural Language" Agent Pane translate into operations on core terminal code entities.

```mermaid
graph LR
    subgraph "Natural Language Space"
        [AIAgentsViewModel] -- "manages" --> [Agent_Session]
        [AgentPaneContent] -- "renders" --> [WTA_TUI]
    end

    subgraph "Code Entity Space"
        [WTA_TUI] -- "calls" --> [IProtocolServer::GetText]
        [IProtocolServer::GetText] -- "accesses" --> [TextBuffer]
        [Agent_Session] -- "triggers" --> [ShortcutActionDispatch]
        [ShortcutActionDispatch] -- "executes" --> [TerminalPage::_HandleOpenNewTab]
    end
```
Sources: [README.md:113-122](), [README.md:141-141]()

## Project Structure

The repository maintains the original Windows Terminal structure while adding specific directories for AI integration:

| Directory | Purpose |
| :--- | :--- |
| `src/cascadia` | The main Terminal UI (XAML/WinRT). Contains the new `AgentPane` and AI settings. |
| `tools/wta` | The **Windows Terminal Agent** Rust source code. |
| `src/host` | The Windows Console Host (`conhost.exe`) and ConPTY logic. |
| `src/terminal` | The core VT state machine and text buffer logic. |
| `src/renderer` | Hardware-accelerated (AtlasEngine) and legacy (GDI) renderers. |

For a detailed walkthrough of the repository, see **[Project Structure and Key Directories](#1.2)**.

## Navigation and Wiki Guide

This wiki is structured to guide you from high-level concepts down to specific implementation details.

### 1. Setup and Basics
*   **[Getting Started: Installation and Building](#1.1)**: System requirements (Windows 11 22H2+), building via `OpenConsole.psm1` or `razzle.cmd`, and deploying the `CascadiaPackage` [doc/building.md:20-41]().
*   **[Project Structure and Key Directories](#1.2)**: Understanding the layout of the fork and where AI-specific code resides.

### 2. AI Integration (The "Intelligent" Layer)
Detailed documentation on the `WTA` binary, the **Agent Client Protocol (ACP)**, and the `TerminalProtocolComServer` which allows agents to read and write to the terminal.

### 3. Core Terminal Engine
Deep dives into the inherited Windows Terminal stack:
*   **Terminal Emulation**: The VT parser (`AdaptDispatch`) and `TextBuffer` management.
*   **Rendering Pipeline**: How `AtlasEngine` uses DirectX for high-performance text rendering.
*   **Settings Model**: The JSON-based layering system and the XAML Settings Editor.

### 4. Console Infrastructure
Information on `ConPTY`, the `conhost` screen buffer, and how terminal applications communicate with the shell.

---

**Next Steps:** To begin contributing or building the project, visit **[Getting Started: Installation and Building](#1.1)**.

---

