<!-- source: DeepWiki mcp.deepwiki.com · repo aakashadesara/ctop · page 4 User Interaction · fetched 2026-10-26 -->

# User Interaction

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [src/_core.js](src/_core.js)
- [src/input.js](src/input.js)
- [test/animations.test.js](test/animations.test.js)
- [test/caching.test.js](test/caching.test.js)

</details>



This page provides a high-level overview of how users interact with the `ctop` terminal interface. It covers the primary input methods, including keyboard shortcuts, mouse support, and the searchable command palette. 

`ctop` is designed to be a keyboard-centric tool, allowing for rapid navigation and control of AI agent processes. However, it also provides full mouse support for selecting sessions and interacting with the UI.

### Interaction Subsystems

The interaction logic is distributed across three main areas:

*   **Keyboard & Mouse:** Standard navigation and control shortcuts. For details, see [Keyboard Commands and Mouse Support](#4.1).
*   **Command Palette:** A fuzzy-searchable interface for complex actions. For details, see [Command Palette and Filter/Sort](#4.2).
*   **External Integration:** Features that bridge the TUI to the local OS, such as session exports and opening project directories. For details, see [Quick Jump and Session Export](#4.3).

---

## Input Flow and State Management

User interactions trigger updates to the global `_state` object [src/_core.js:1450-1550](), which in turn schedules a re-render of the terminal buffer. To prevent performance degradation during rapid input (like scrolling), `ctop` utilizes a render coalescing mechanism via `setImmediate` [src/_core.js:1200-1215]().

### System Interaction Overview

The following diagram illustrates how user input flows from the terminal through the input handlers to modify the system state.

**Input Processing Pipeline**
```mermaid
graph TD
    "Terminal_Input" --> "process.stdin.on('data')"
    "process.stdin.on('data')" --> "Handle_Keys"
    "process.stdin.on('data')" --> "Handle_Mouse"
    
    subgraph "Input Handlers"
        "Handle_Keys" -- "j/k/h/l" --> "Update_selectedIndex"
        "Handle_Keys" -- "P/L/W/d" --> "Toggle_View_Modes"
        "Handle_Keys" -- "/" --> "Enter_filterMode"
        "Handle_Mouse" -- "parseMouseEvent" --> "Calculate_Index"
    end

    subgraph "State Updates"
        "Update_selectedIndex" --> "_state.selectedIndex"
        "Toggle_View_Modes" --> "_state.viewMode"
        "Calculate_Index" --> "_state.selectedIndex"
    end

    "_state.selectedIndex" --> "render()"
    "_state.viewMode" --> "render()"
```
**Sources:** [src/_core.js:1150-1300](), [src/input.js:1-11]()

---

## Core Interaction Modes

### 1. Navigation and View Toggles
Navigation follows standard `vi`-style keybindings (`j`, `k`, `h`, `l`) and arrow keys. The UI supports two primary layouts: **List View** (table format) and **Pane View** (card grid), which can be toggled using the `P` key [README.md:54-75]().

### 2. Process Control
Users can manage active agents directly from the TUI. Actions include sending `SIGTERM` (`x`) or `SIGKILL` (`X`) to the selected process, or killing all detected agents simultaneously (`K`) [src/_core.js:1400-1420]().

### 3. Search and Filtering
The interface supports both a simple filter mode (`/`) for narrowing down the visible list and a full-text search (`F`) that parses conversation logs for specific strings [README.md:63-64]().

### 4. Command Palette
The Command Palette provides a centralized location for actions that do not have dedicated keybindings or for users who prefer a fuzzy-search interface. It is invoked via the `showPalette` function [src/_core.js:1560-1580]().

**Interaction Logic Components**
```mermaid
graph LR
    subgraph "src/_core.js"
        "showPalette" -- "Fuzzy Search" --> "Palette_UI"
        "applySortAndFilter" -- "Pipeline" --> "Filtered_List"
        "openDirectory" -- "Spawn" --> "OS_Process"
    end

    subgraph "src/input.js"
        "parseMouseEvent" --> "listViewRowToIndex"
        "parseMouseEvent" --> "paneViewClickToIndex"
    end

    "Palette_UI" --> "Kill_Actions"
    "Palette_UI" --> "Theme_Actions"
    "Filtered_List" --> "Render_Engine"
    "OS_Process" --> "Finder/Editor/Terminal"
```
**Sources:** [src/_core.js:1500-1650](), [src/input.js:1-11]()

---

## Subsystem Details

| Subsystem | Key Functions / Entities | Purpose |
| :--- | :--- | :--- |
| **Keyboard & Mouse** | `parseMouseEvent`, `listViewRowToIndex` | Maps raw terminal input to list indices and state changes. |
| **Command Palette** | `showPalette`, `buildGroupedFlatList` | Provides fuzzy-searchable access to all ctop commands. |
| **Quick Jump** | `openDirectory`, `shortenCwd` | Transitions from monitoring to active development in local tools. |
| **Filtering** | `applySortAndFilter`, `SORT_MODES` | Manages the display logic for large numbers of sessions. |

For detailed implementation and reference:
- **[Keyboard Commands and Mouse Support](#4.1)**: Full keymap and mouse coordinate mapping logic.
- **[Command Palette and Filter/Sort](#4.2)**: Fuzzy search implementation and sorting algorithms.
- **[Quick Jump and Session Export](#4.3)**: Details on `openDirectory` and markdown/JSON/CSV export formats.

**Sources:** [src/_core.js:1-150](), [src/input.js:1-11](), [README.md:54-77]()

---

