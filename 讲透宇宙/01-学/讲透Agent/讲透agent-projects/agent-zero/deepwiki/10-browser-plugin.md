<!-- source: DeepWiki mcp.deepwiki.com · repo agent0ai/agent-zero · page 10 Browser Plugin · fetched 2026-10-29 -->

# Browser Plugin

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [plugins/_browser/AGENTS.md](plugins/_browser/AGENTS.md)
- [plugins/_browser/api/extensions.py](plugins/_browser/api/extensions.py)
- [plugins/_browser/api/ws_browser.py](plugins/_browser/api/ws_browser.py)
- [plugins/_browser/default_config.yaml](plugins/_browser/default_config.yaml)
- [plugins/_browser/helpers/config.py](plugins/_browser/helpers/config.py)
- [plugins/_browser/helpers/connector_runtime.py](plugins/_browser/helpers/connector_runtime.py)
- [plugins/_browser/helpers/extension_manager.py](plugins/_browser/helpers/extension_manager.py)
- [plugins/_browser/helpers/runtime.py](plugins/_browser/helpers/runtime.py)
- [plugins/_browser/prompts/agent.system.tool.browser.md](plugins/_browser/prompts/agent.system.tool.browser.md)
- [plugins/_browser/skills/browser-automation/SKILL.md](plugins/_browser/skills/browser-automation/SKILL.md)
- [plugins/_browser/skills/browser-form-workflows/SKILL.md](plugins/_browser/skills/browser-form-workflows/SKILL.md)
- [plugins/_browser/tools/browser.py](plugins/_browser/tools/browser.py)
- [plugins/_browser/webui/browser-config-store.js](plugins/_browser/webui/browser-config-store.js)
- [plugins/_browser/webui/browser-panel.html](plugins/_browser/webui/browser-panel.html)
- [plugins/_browser/webui/browser-store.js](plugins/_browser/webui/browser-store.js)
- [plugins/_browser/webui/config.html](plugins/_browser/webui/config.html)
- [plugins/_browser/webui/main.html](plugins/_browser/webui/main.html)
- [tests/test_browser_agent_regressions.py](tests/test_browser_agent_regressions.py)
- [tests/test_browser_tool_output.py](tests/test_browser_tool_output.py)
- [tests/test_host_browser_connector.py](tests/test_host_browser_connector.py)

</details>



The Browser Plugin (`_browser`) provides Agent Zero with full web automation capabilities using Playwright/Patchright-based Chromium management [plugins/_browser/AGENTS.md:5-12](). It bridges raw headless browser execution and a rich, interactive visual experience for users via real-time Chrome DevTools Protocol (CDP) screencasting, a persistent multi-tab management system, and an Alpine.js-based frontend for manual intervention [plugins/_browser/webui/browser-panel.html:11-47]().

For deeper technical details, see the child pages:
- [Browser Runtime & WebSocket API](#10.1) — Covers `BrowserRuntime`, persistent context management, CDP screencast, `WsBrowser` handlers, viewport sync, Playwright binary provisioning, interactive Xpra view, profile cleanup, and extension management.
- [Browser UI & Tool Integration](#10.2) — Covers `browser-store.js`, Right Canvas surface registration, `drawBrowserTool()` handler, Annotate Mode, Dock Handoff, Browser LLM Preset, browser tool prompts, `ConnectorBrowserRuntime` (Bring Your Own Browser mode), and browser skills.

---

### System Overview

The browser architecture divides responsibilities between a Python-based runtime managing the browser process and a WebSocket-driven UI handling real-time interaction. It supports both an internal Docker-isolated Chromium instance and a "Bring Your Own Browser" mode via `ConnectorBrowserRuntime` [plugins/_browser/helpers/connector_runtime.py:120-136]().

**Diagram: Natural Language to Browser Execution Pipeline**
```mermaid
graph TD
    subgraph "Natural Language Space"
        [NL_REQ]["User/Agent Prompt: 'Open example.com'"]
    end

    subgraph "Code Entity Space"
        [BrowserTool]["plugins/_browser/tools/browser.py::Browser"]
        [BrowserRuntime]["plugins/_browser/helpers/runtime.py::BrowserRuntime"]
        [RuntimeCore]["plugins/_browser/helpers/runtime.py::_BrowserRuntimeCore"]
        [ConnectorRuntime]["plugins/_browser/helpers/connector_runtime.py::ConnectorBrowserRuntime"]
        [WsBrowser]["plugins/_browser/api/ws_browser.py::WsBrowser"]
    end

    [NL_REQ] --> [BrowserTool]
    [BrowserTool] -- "get_tool_runtime()" --> [BrowserRuntime]
    [BrowserRuntime] -- "internal container" --> [RuntimeCore]
    [BrowserRuntime] -- "host_required mode" --> [ConnectorRuntime]
    [RuntimeCore] -- "Playwright/CDP" --> [Chromium_Instance]
    [Chromium_Instance] -- "Screencast Frames" --> [WsBrowser]
```
Sources: [plugins/_browser/tools/browser.py:28-80](), [plugins/_browser/helpers/runtime.py:101-104](), [plugins/_browser/helpers/connector_runtime.py:120-136](), [plugins/_browser/api/ws_browser.py:40-67]()

---

### Key Components

#### 1. Browser Tool
The `Browser` tool is the primary interface for agents to execute web tasks [plugins/_browser/tools/browser.py:28-80](). It supports navigation, form interaction, element inspection via text refs, and visual screenshots [plugins/_browser/prompts/agent.system.tool.browser.md:8-12]().
*   **Actions:** `open`, `navigate`, `content`, `click`, `type`, `screenshot`, `multi`, `keyboard`, `mouse`, `wheel`. [plugins/_browser/prompts/agent.system.tool.browser.md:8-9]()
*   **Multi-Tab Management:** Handles concurrent tabs (up to 32 by default) tracked by `browser_id` [plugins/_browser/helpers/config.py:32-34]().
*   **Vision Integration:** Explicit screenshot triggers return paths consumable by the `vision_load` multimodal tool [plugins/_browser/prompts/agent.system.tool.browser.md:13-14]().

Sources: [plugins/_browser/tools/browser.py:28-80](), [plugins/_browser/prompts/agent.system.tool.browser.md:1-15](), [plugins/_browser/helpers/config.py:32-34]()

#### 2. Runtime Backends & Connector
The plugin supports running Chromium inside Agent Zero's container environment or connecting to an external host browser via the A0 CLI connector bridge [plugins/_browser/webui/config.html:24-42]().

**Diagram: Runtime Selection & Dispatch Flow**
```mermaid
graph TD
    subgraph "Natural Language Space"
        [Intent]["Configure runtime backend"]
    end

    subgraph "Code Entity Space"
        [ConfigHelper]["plugins/_browser/helpers/config.py::normalize_browser_config"]
        [RuntimeRouter]["plugins/_browser/helpers/runtime.py::get_runtime"]
        [ContainerRuntime]["plugins/_browser/helpers/runtime.py::_BrowserRuntimeCore"]
        [HostRuntime]["plugins/_browser/helpers/connector_runtime.py::ConnectorBrowserRuntime"]
    end

    [Intent] --> [ConfigHelper]
    [ConfigHelper] --> [RuntimeRouter]
    [RuntimeRouter] -- "runtime_backend == container" --> [ContainerRuntime]
    [RuntimeRouter] -- "runtime_backend == host_required" --> [HostRuntime]
```
Sources: [plugins/_browser/helpers/config.py:133-162](), [plugins/_browser/helpers/runtime.py:101-115](), [plugins/_browser/helpers/connector_runtime.py:120-136]()

#### 3. WebSocket API (`WsBrowser`)
The `WsBrowser` handler manages live duplex communication between the web frontend and the Python browser runtime [plugins/_browser/api/ws_browser.py:40-77]().
*   **Frame Streaming:** Manages subscriptions for real-time screencast transmission (`_stream_frames`) [plugins/_browser/api/ws_browser.py:133-142]().
*   **Input Bridging:** Forwards pointer and key events from the canvas directly to the active Playwright page [plugins/_browser/api/ws_browser.py:67-68]().

Sources: [plugins/_browser/api/ws_browser.py:40-77](), [plugins/_browser/api/ws_browser.py:133-142]()

#### 4. UI Canvas and Panel
The frontend is implemented via Alpine.js components inside the Right Canvas surface area [plugins/_browser/webui/browser-panel.html:11-15]().
*   **`browser-store.js`:** The central reactive state manager [plugins/_browser/webui/browser-store.js:177-195]().
*   **`browser-panel.html`:** The layout containing the address bar, navigation controls, and viewport canvas [plugins/_browser/webui/browser-panel.html:11-66]().
*   **Annotation Mode:** Allows users to draw annotations directly onto the browser view to guide agent interactions [plugins/_browser/webui/browser-panel.html:69-77]().

Sources: [plugins/_browser/webui/browser-panel.html:11-115](), [plugins/_browser/webui/browser-store.js:177-195]()

---

### Integration Summary

| Subsystem | Core File / Class | Role |
| :--- | :--- | :--- |
| **Tool Execution** | `plugins/_browser/tools/browser.py` | Agent tool bindings and action parser. |
| **Runtime Core** | `plugins/_browser/helpers/runtime.py` | Playwright session and CDP management. |
| **Connector Runtime** | `plugins/_browser/helpers/connector_runtime.py` | Bring Your Own Browser integration. |
| **WebSocket API** | `plugins/_browser/api/ws_browser.py` | Real-time frames, input events, and sessions. |
| **Frontend Store** | `plugins/_browser/webui/browser-store.js` | UI state, tab management, and viewport sync. |

Sources: [plugins/_browser/tools/browser.py:28-50](), [plugins/_browser/helpers/runtime.py:37-50](), [plugins/_browser/helpers/connector_runtime.py:120-130](), [plugins/_browser/api/ws_browser.py:40-50](), [plugins/_browser/webui/browser-store.js:177-195]()

---

### Child Pages

For detailed specifications, refer to the child pages:
- **[Browser Runtime & WebSocket API](#10.1)**
- **[Browser UI & Tool Integration](#10.2)**

Sources: [plugins/_browser/helpers/runtime.py:125-132](), [plugins/_browser/webui/browser-store.js:1-10]()

---

