<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/browser-harness · page 3 Interaction Skills · fetched 2026-10-30 -->

# Interaction Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [interaction-skills/connection.md](interaction-skills/connection.md)
- [interaction-skills/cookies.md](interaction-skills/cookies.md)
- [interaction-skills/drag-and-drop.md](interaction-skills/drag-and-drop.md)
- [interaction-skills/screenshots.md](interaction-skills/screenshots.md)
- [interaction-skills/scrolling.md](interaction-skills/scrolling.md)
- [interaction-skills/tabs.md](interaction-skills/tabs.md)
- [interaction-skills/viewport.md](interaction-skills/viewport.md)

</details>



The `interaction-skills/` library provides reusable patterns and high-level abstractions for handling complex browser mechanics that go beyond simple `click()` and `type_text()` commands. These skills address the "how" of browser automation—managing UI patterns, navigating DOM complexities like Shadow Roots, and handling browser-level events like dialogs, file transfers, scrolling, and connection stability.

## Interaction Architecture

Interaction skills bridge the gap between high-level intent and low-level Chrome DevTools Protocol (CDP) commands. They are designed to be "self-healing" by relying on coordinate-first interactions, robust detection mechanisms, and proper handling of focus emulation and viewport geometries.

### Bridging Intent to Code Entities

```mermaid
graph TD
    subgraph "Natural Language_Space"
        "Handle_the_alert"["'Handle the alert'"]
        "Upload_a_file"["'Upload a file'"]
        "Switch_to_the_popup"["'Switch to the popup'"]
        "Scroll_the_sidebar"["'Scroll the sidebar'"]
        "Capture_screenshot"["'Capture screenshot'"]
    end

    subgraph "Code_Entity_Space"
        "page_info"["page_info()"]
        "cdp_dialog"["cdp('Page.handleJavaScriptDialog')"]
        "setFileInputFiles"["DOM.setFileInputFiles"]
        "switch_tab"["switch_tab()"]
        "scroll"["scroll()"]
        "capture_shot"["capture_screenshot()"]
    end

    "Handle_the_alert" --> "page_info"
    "page_info" -- "Returns 'dialog' key" --> "cdp_dialog"
    "Upload_a_file" --> "setFileInputFiles"
    "Switch_to_the_popup" --> "switch_tab"
    "Scroll_the_sidebar" --> "scroll"
    "Capture_screenshot" --> "capture_shot"
```
Sources: [src/browser_harness/helpers.py:1-200](), [interaction-skills/drag-and-drop.md:1-3](), [interaction-skills/scrolling.md:1-22]()

---

## 3.1 Input & Navigation Patterns
This section covers the physical mechanics of interacting with web elements, addressing viewport geometry, scrolling, and input emulation.

*   **Scrolling:** Distinguishing between standard page scrolling and nested containers or virtualized lists. When background scroll commands time out on hidden tabs, harness patterns apply `Emulation.setFocusEmulationEnabled` rather than replacing wheel input with custom `Runtime.evaluate` scripts [interaction-skills/scrolling.md:1-22]().
*   **Dropdowns & Comboboxes:** Strategies for interacting with native HTML `<select>` elements versus custom React/Vue overlays, emphasizing re-measuring geometry after opening a menu.
*   **Drag-and-Drop:** Distinguishing between low-level mouse input events (`mousedown`/`mousemove`/`mouseup`) and DOM-specific drag sequences [interaction-skills/drag-and-drop.md:1-3]().
*   **Viewport Geometry & Screenshots:** Managing how viewport size changes affect layout and coordinate-based clicks. Click coordinates are in CSS pixels, while screenshots captured via `capture_screenshot()` are in device pixels (requiring conversion via `window.devicePixelRatio`). Downscaling via `max_dim=1800` prevents LLM token/size rejections on high-DPI displays [interaction-skills/screenshots.md:1-17]().
*   **Touch Emulation:** Configuring touch points safely via `Emulation.setTouchEmulationEnabled`, omitting invalid zero values as validated by Chrome [interaction-skills/viewport.md:1-16]().

For details, see [Input & Navigation Patterns](#3.1).

Sources: [interaction-skills/scrolling.md:1-22](), [interaction-skills/screenshots.md:1-17](), [interaction-skills/viewport.md:1-16](), [interaction-skills/drag-and-drop.md:1-3]()

---

## 3.2 Frames, Shadow DOM & Multi-Tab
Modern web applications isolate components using iframes, Shadow DOM trees, or multi-tab contexts that require specialized traversal strategies.

*   **Iframe Traversal:** Handling same-origin and cross-origin frames via target attachment and session management.
*   **Shadow DOM:** Recursive `shadowRoot` traversal to query elements encapsulated inside Web Components.
*   **Tab Management:** Using `switch_tab()` and `new_tab()` to manage multiple concurrent browser contexts. 
    *   Use **CDP for control** and **UI automation** (like AppleScript on macOS or `xdotool` on Linux) when user-visible order matters [interaction-skills/tabs.md:1-61]().
    *   Special handling is required for the `chrome://omnibox-popup.top-chrome/` target, an invisible viewport that can interfere with automation if attached by mistake [interaction-skills/connection.md:3-8]().
    *   `switch_tab()` attaches the harness without altering Chrome's visible tab; `activate_tab()` is reserved for explicit user-requested visible switches [interaction-skills/tabs.md:62-73]().

### Tab and Target Mapping

```mermaid
graph LR
    subgraph "CDP_Targets"
        "target_list"["list_tabs()"]
        "new_t"["new_tab(url)"]
        "activate"["Target.activateTarget"]
        "omnibox"["chrome://omnibox-popup"]
    end

    subgraph "Physical_Space"
        "visible_strip"["Tab Strip (Left-to-Right)"]
        "active_win"["Frontmost Window"]
    end

    "target_list" -- "Includes" --> "omnibox"
    "omnibox" -- "Filter Out" --> "visible_strip"
    "new_t" -- "Opens background" --> "visible_strip"
    "activate" -- "Brings to front" --> "active_win"
    "switch_tab"["switch_tab()"] -- "Calls" --> "activate"
```
Sources: [interaction-skills/connection.md:3-8](), [interaction-skills/tabs.md:1-73]()

For details, see [Frames, Shadow DOM & Multi-Tab](#3.2).

Sources: [interaction-skills/tabs.md:1-73](), [interaction-skills/connection.md:1-52]()

---

## 3.3 Dialogs, Downloads, Uploads & Network
These skills handle browser-level events and asynchronous resource transfers that impact automation flows.

*   **JavaScript Dialogs:** Managing `alert`, `confirm`, `prompt`, and `beforeunload` events via CDP and JavaScript stubs to avoid execution freezes.
*   **File Operations:** Handling file uploads via `DOM.setFileInputFiles` and managing browser-triggered downloads vs direct `http_get` fetches.
*   **Network & State:** Monitoring network requests for Single Page Application (SPA) flows and managing browser cookies explicitly via cookie storage APIs without confusing browser state with page state [interaction-skills/cookies.md:1-3]().
*   **PDF Generation:** Automating layout capture and document export via browser primitives.

For details, see [Dialogs, Downloads, Uploads & Network](#3.3).

Sources: [interaction-skills/cookies.md:1-3]()

---
**Sources:**
- [src/browser_harness/helpers.py:1-200]()
- [interaction-skills/scrolling.md:1-22]()
- [interaction-skills/tabs.md:1-73]()
- [interaction-skills/connection.md:1-52]()
- [interaction-skills/viewport.md:1-16]()
- [interaction-skills/screenshots.md:1-17]()
- [interaction-skills/drag-and-drop.md:1-3]()
- [interaction-skills/cookies.md:1-3]()

---

