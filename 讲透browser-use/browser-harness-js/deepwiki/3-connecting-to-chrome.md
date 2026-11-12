<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/browser-harness-js · page 3 Connecting to Chrome · fetched 2026-10-30 -->

# Connecting to Chrome

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [interaction-skills/connection.md](interaction-skills/connection.md)
- [sdk/session.ts](sdk/session.ts)

</details>



Connecting to Chrome is the first step in the `browser-harness-js` lifecycle. This process involves resolving a WebSocket (WS) URL for the browser-level DevTools endpoint and subsequently attaching to a specific page target.

## Connection Strategies

The SDK provides three primary ways to establish a connection via the `session.connect()` method [sdk/session.ts:46-60](). The choice of strategy depends on how Chrome was launched and the version of Chrome being used.

| Strategy | `ConnectOptions` Key | Use Case |
| :--- | :--- | :--- |
| **Profile Directory** | `profileDir` | **Recommended.** Works with Chrome 144+ and `chrome://inspect` flows. Reads `DevToolsActivePort` directly. |
| **HTTP Probe** | `port` | Legacy. Probes `http://host:port/json/version`. Fails on Chrome 144+ without explicit flags. |
| **Direct WS URL** | `wsUrl` | Escape hatch. Use if you already have the full `ws://...` browser endpoint URL. |

### The Chrome 144+ Compatibility Shift
Starting with Chrome 144, the traditional HTTP endpoint `/json/version` is often not served when attaching via `chrome://inspect`. The `profileDir` strategy bypasses this by reading the `DevToolsActivePort` file directly from the filesystem [sdk/session.ts:159-170]().

For a detailed breakdown of these strategies and why the HTTP probe fails, see [Connection Strategies and Chrome 144+ Compatibility](#3.1).

Sources: [sdk/session.ts:16-24](), [sdk/session.ts:159-170](), [interaction-skills/connection.md:7-12]()

---

## Startup Lifecycle and Target Management

Connecting to the browser is only the beginning. Once the `Session` [sdk/session.ts:26]() is connected to the browser-level WebSocket, you must discover and "use" a specific target (tab or page) to begin interaction.

### Typical Startup Sequence
1.  **Resolve & Connect**: Call `session.connect({profileDir})` [sdk/session.ts:46]().
2.  **Discover Targets**: Use `listPageTargets()` to find available tabs, filtering out internal Chrome pages [interaction-skills/connection.md:21-34]().
3.  **Attach Session**: Call `session.use(targetId)` to route subsequent commands (like `Page` or `DOM`) to that tab [sdk/session.ts:74-78]().
4.  **Visual Focus**: Use `Target.activateTarget` to bring the tab to the front within Chrome [interaction-skills/connection.md:52]().
5.  **Initialize Domains**: Enable required CDP domains (e.g., `session.Page.enable()`) [interaction-skills/connection.md:53]().

### Connection Logic Flow

The following diagram illustrates how the `Session` class interacts with the filesystem and Chrome to establish a functional connection.

**Connection and Target Discovery Flow**
```mermaid
graph TD
    subgraph "Natural Language Space"
        User["User / Script"]
        Chrome["Chrome Browser"]
        FS["File System"]
    end

    subgraph "Code Entity Space"
        S["class Session"]
        RWU["function resolveWsUrl"]
        RDAP["function readDevToolsActivePort"]
        LPT["function listPageTargets"]
    end

    User -->| "session.connect({profileDir})" | S
    S --> RWU
    RWU -->| "Read DevToolsActivePort" | RDAP
    RDAP -.->| "fs.readFile" | FS
    FS -.->| "Port + UUID Path" | RDAP
    RDAP --> RWU
    RWU -->| "ws://127.0.0.1:PORT/PATH" | S
    S -->| "new WebSocket()" | Chrome
    
    User -->| "listPageTargets()" | LPT
    LPT -->| "Target.getTargets" | S
    S -->| "CDP Request" | Chrome
    Chrome -->| "TargetInfo[]" | S
    S -->| "Filter Type: page" | LPT
    LPT --> User
```
Sources: [sdk/session.ts:46-60](), [sdk/session.ts:171-185](), [sdk/session.ts:193-200](), [interaction-skills/connection.md:47-53]()

---

## Target Discovery and Routing

Chrome may report several targets that are not useful for automation, such as the `chrome://omnibox-popup.top-chrome/` or DevTools windows. The SDK provides helpers to filter these and ensure commands are routed to the correct execution context.

### Session Routing with `session.use()`
The `session.use(targetId)` method is a critical primitive. It calls `Target.attachToTarget` with `flatten: true` [sdk/session.ts:74-78](). This allows the `Session` class to automatically append the correct `sessionId` to every subsequent CDP message, effectively "routing" your commands to that specific tab without needing to manage multiple WebSockets.

### Window Focus and Platform UI
While `Target.activateTarget` focuses a tab within the Chrome window, it may not bring the Chrome application itself to the foreground of the OS. The SDK documentation recommends using platform-specific CLI tools (like `osascript` on macOS or `wmctrl` on Linux) to manage window-level focus [interaction-skills/connection.md:69-81]().

For details on filtering targets, handling the "Omnibox Popup" problem, and platform-specific focus commands, see [Target Discovery and Session Routing](#3.2).

Sources: [sdk/session.ts:74-78](), [sdk/session.ts:121-123](), [interaction-skills/connection.md:21-45](), [interaction-skills/connection.md:69-81]()

---

