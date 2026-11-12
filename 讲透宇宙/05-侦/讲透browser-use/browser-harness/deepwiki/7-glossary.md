<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/browser-harness · page 7 Glossary · fetched 2026-10-30 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/VOUCHED.td](.github/VOUCHED.td)
- [SKILL.md](SKILL.md)
- [install.md](install.md)
- [src/browser_harness/_ipc.py](src/browser_harness/_ipc.py)
- [src/browser_harness/daemon.py](src/browser_harness/daemon.py)
- [src/browser_harness/helpers.py](src/browser_harness/helpers.py)
- [tests/unit/test_daemon.py](tests/unit/test_daemon.py)
- [tests/unit/test_helpers.py](tests/unit/test_helpers.py)
- [tests/unit/test_ipc.py](tests/unit/test_ipc.py)

</details>



This glossary defines the technical terms, environment variables, abbreviations, and domain concepts specific to the `browser-harness` codebase. It serves as a reference for onboarding engineers to understand the implementation details, configuration options, and data flow of the system.

## Core System Terms

| Term | Definition | Implementation Pointer |
| :--- | :--- | :--- |
| **Daemon** | A background process (one per `BU_NAME`) that maintains a persistent WebSocket connection to Chrome via CDP and exposes an IPC relay (Unix socket on POSIX, TCP loopback on Windows). | `daemon.py` [src/browser_harness/daemon.py:1-5]() |
| **CDP (Chrome DevTools Protocol)** | The low-level protocol used to communicate directly with the browser engine. `browser-harness` uses a `CDPClient` to send raw JSON-RPC commands. | `daemon.py` [src/browser_harness/daemon.py:10-11](), `helpers.py` [src/browser_harness/helpers.py:53-78]() |
| **Harness** | The minimal Python wrapper that translates high-level agent commands into CDP calls via a thin IPC layer. | `helpers.py` [src/browser_harness/helpers.py:1-5]() |
| **Self-Healing** | The philosophy where the LLM agent is empowered to edit helper files or create new domain skills mid-task if a primitive is missing or a selector fails. | `SKILL.md` [SKILL.md:8-12]() |
| **Interaction Skill** | Reusable logic for complex browser mechanics (e.g., handling iframes, shadow DOM, or file uploads) documented in internal patterns. | `SKILL.md` [SKILL.md:125-147]() |
| **Domain Skill** | Site-specific knowledge (selectors, URL patterns, private APIs) stored in workspace directories to prevent agents from rediscovering site structures. | `SKILL.md` [SKILL.md:14-17]() |
| **Remote Daemon** | A daemon instance managing a Browser Use cloud browser, typically identified by `BU_BROWSER_ID`. | `daemon.py` [src/browser_harness/daemon.py:114-117]() |
| **Recording** | A directory containing metadata, event streams, and sequential image captures of browser actions. | `recorder.py` [src/browser_harness/recorder.py:1-10]() |

### Data Flow: Script to Browser
The following diagram illustrates how a Python command travels from the agent's script to the browser instance.

**Command Execution Flow**
```mermaid
graph TD
    subgraph "Natural Language Space"
        "AgentPrompt["Agent Prompt"]" -- "Generates" --> "PythonScript["Python Script"]"
    end

    subgraph "Code Entity Space"
        "PythonScript" -- "stdin" --> "run_main["run.py:main()"]"
        "run_main" -- "Calls" --> "ensure_daemon["admin.py:ensure_daemon()"]"
        "ensure_daemon" -- "Spawns" --> "daemon_main["daemon.py:main()"]"
        "run_main" -- "Executes" --> "helpers_click["helpers.py:click_at_xy()"]"
        "helpers_click" -- "Calls" --> "helpers_send["helpers.py:_send()"]"
        "helpers_send" -- "IPC Socket" --> "daemon_handle["daemon.py:handle()"]"
        "daemon_handle" -- "CDPClient.send_raw" --> "BrowserCDP["Browser (CDP Endpoint)"]"
    end
```
Sources: [src/browser_harness/run.py:207-213](), [src/browser_harness/admin.py:178-181](), [src/browser_harness/helpers.py:52-69](), [src/browser_harness/daemon.py:1-10]()

---

## Environment Variables & Configuration

These variables configure the behavior of both the local daemon and remote cloud integrations.

| Variable | Purpose | File Reference |
| :--- | :--- | :--- |
| `BU_NAME` | Namespaces the daemon. Determines the socket, PID, and log filenames. Defaults to `default`. | `daemon.py` [src/browser_harness/daemon.py:33-36]() |
| `BROWSER_USE_API_KEY` | Required for provisioning and managing remote browsers via the Browser Use cloud API. | `admin.py` [src/browser_harness/admin.py:128](), `auth.py` [src/browser_harness/auth.py:1-10]() |
| `BU_BROWSER_ID` | The UUID of a remote cloud browser. Used by the daemon to identify the remote session. | `daemon.py` [src/browser_harness/daemon.py:115-115]() |
| `BU_CDP_WS` | Overrides local Chrome discovery with a direct WebSocket URL. | `daemon.py` [src/browser_harness/daemon.py:117-117]() |
| `BU_CDP_URL` | Overrides discovery with a specific DevTools HTTP endpoint. | `daemon.py` [src/browser_harness/daemon.py:117-117]() |
| `BH_DOMAIN_SKILLS` | Set to `1` to enable auto-loading of site-specific playbooks from domain-skills directories. | `helpers.py` [src/browser_harness/helpers.py:154-157]() |
| `BH_TMP_DIR` | Path to store screenshots, debug overlays, and daemon logs. | `_ipc.py` [src/browser_harness/_ipc.py:18-18]() |
| `BH_RUNTIME_DIR` | Directory holding runtime files like sockets, ports, and PID records. | `_ipc.py` [src/browser_harness/_ipc.py:19-19]() |
| `BH_RECORD` | Set to force enable or disable session recording for a specific process. | `recorder.py` [src/browser_harness/recorder.py:86-90]() |
| `BH_TAB_MARKER` | Controls whether controlled-tab cosmetic title markers are injected. | `daemon.py` [src/browser_harness/daemon.py:133-136]() |

Sources: [src/browser_harness/daemon.py:33-136](), [src/browser_harness/helpers.py:154-157](), [src/browser_harness/_ipc.py:18-21]()

---

## Technical Concepts & Implementation

### The "Stale Session" Recovery
The system handles browser crashes or closed tabs through session tracking and re-attachment. When a target session changes, `set_session` updates the active binding in the daemon.

**Session Management Logic**
```mermaid
graph TD
    subgraph "Code Entity Space"
        "switch_tab"["helpers.py:switch_tab()"] -- "meta: set_session" --> "daemon_handle"["daemon.py:handle()"]
        "daemon_handle" -- "Updates" --> "Daemon_session"["Daemon.session"]
        "page_info"["helpers.py:page_info()"] -- "Evaluates" --> "Runtime_evaluate"["helpers.py:_runtime_evaluate()"]
    end

    subgraph "Browser State"
        "Target1"["Target 1 (Active)"]
        "Target2"["Target 2 (Background)"]
    end

    "Daemon_session" -.-> "Target1"
```
Sources: [src/browser_harness/helpers.py:135-170](), [src/browser_harness/daemon.py:1-50]()

### Coordinate-First Interaction
`browser-harness` prioritizes coordinate-based clicks over DOM selectors. This allows interaction with elements inside iframes, Shadow DOMs, and cross-origin boundaries without complex tree traversal logic.

*   **Implementation**: `click_at_xy(x, y)` triggers low-level input events via CDP [src/browser_harness/helpers.py:174-185]().
*   **Debug Mode**: If `BH_DEBUG_CLICKS` is set, the harness uses `Pillow` to draw a visual indicator on a captured screenshot of the click location [src/browser_harness/helpers.py:175-185]().

### DevToolsActivePort Discovery
The daemon locates a running Chrome instance by scanning platform-specific profile directories for the `DevToolsActivePort` file.

*   **Logic**: The file contains the ephemeral port on the first line and a browser path or token on subsequent lines [src/browser_harness/daemon.py:138-152]().
*   **Source**: [src/browser_harness/daemon.py:138-172]()

### Remote Browser Lifecycle
Remote browsers are provisioned via `start_remote_daemon` and should be explicitly terminated to manage billing and resources.

*   **Management**: Remote daemons remain active until stopped via `stop_remote` [tests/unit/test_daemon.py:43-61]().
*   **Authentication**: Managed via auth helpers that load and verify API credentials [src/browser_harness/auth.py:1-10]().

---

## File Convention Summary

| Path | Role |
| :--- | :--- |
| `_RUNTIME/{stem}.sock` | Unix domain socket for IPC on POSIX systems [src/browser_harness/_ipc.py:54](). |
| `_RUNTIME/{stem}.port` | JSON file on Windows holding the TCP port and security token [src/browser_harness/_ipc.py:53](). |
| `_RUNTIME/{stem}.pid` | Process ID file used to verify daemon identity and prevent PID reuse [src/browser_harness/_ipc.py:52](). |
| `_TMP/{stem}.log` | Daemon log file containing CDP traffic and error traces [src/browser_harness/_ipc.py:51](). |

Sources: [src/browser_harness/_ipc.py:51-54](), [src/browser_harness/daemon.py:33-36]()