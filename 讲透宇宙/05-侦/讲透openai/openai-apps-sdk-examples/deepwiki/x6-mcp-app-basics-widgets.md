<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-apps-sdk-examples · extra page MCP App Basics Widgets · fetched 2026-10-26 -->

# MCP App Basics Widgets

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [mcp_app_basics_node/README.md](mcp_app_basics_node/README.md)
- [mcp_app_basics_node/package.json](mcp_app_basics_node/package.json)
- [mcp_app_basics_node/src/server.ts](mcp_app_basics_node/src/server.ts)
- [mcp_app_basics_node/tsconfig.json](mcp_app_basics_node/tsconfig.json)
- [src/call-server-tool/App.tsx](src/call-server-tool/App.tsx)
- [src/call-server-tool/index.css](src/call-server-tool/index.css)
- [src/call-server-tool/index.tsx](src/call-server-tool/index.tsx)
- [src/get-host-capabilities/App.tsx](src/get-host-capabilities/App.tsx)
- [src/get-host-context/App.tsx](src/get-host-context/App.tsx)
- [src/get-host-version/App.tsx](src/get-host-version/App.tsx)
- [src/host-theming/App.tsx](src/host-theming/App.tsx)
- [src/open-link/App.tsx](src/open-link/App.tsx)
- [src/request-display-mode/App.tsx](src/request-display-mode/App.tsx)
- [src/send-message/App.tsx](src/send-message/App.tsx)
- [src/show-tool-result/App.tsx](src/show-tool-result/App.tsx)
- [src/streaming-tool-input/App.tsx](src/streaming-tool-input/App.tsx)
- [src/update-model-context/App.tsx](src/update-model-context/App.tsx)

</details>



The **MCP App Basics** collection is an educational suite of eleven interactive widgets designed to demonstrate the core capabilities of the MCP Apps SDK. Each widget focuses on a specific API or data flow pattern, providing a live demonstration alongside an expandable code walkthrough.

## Overview

The `mcp-app-basics-node` server implements eleven tools, each paired with a dedicated React widget. These examples cover the spectrum of App-to-Host, App-to-Model, and App-to-Server communication.

| Category | Widgets | Key APIs |
| :--- | :--- | :--- |
| **Data Flow** | `show_tool_result`, `send_message`, `update_model_context` | `ontoolresult`, `app.sendMessage`, `app.updateModelContext` |
| **Widget ↔ Server** | `call_server_tool` | `app.callServerTool` |
| **Host Interaction** | `open_link`, `request_display_mode`, `host_theming`, `get_host_capabilities`, `get_host_context`, `get_host_version` | `app.openLink`, `app.requestDisplayMode`, `useHostStyles`, `app.getHostCapabilities` |
| **Lifecycle** | `streaming_tool_input` | `ontoolinputpartial` |

Sources: [mcp_app_basics_node/src/server.ts:4-15](), [mcp_app_basics_node/README.md:22-52]()

## Implementation Architecture

The server uses the `registerAppTool` and `registerAppResource` helpers from `@modelcontextprotocol/ext-apps/server` to simplify the association between MCP tools and their corresponding UI assets.

### Server-Side Registration
Each tool is registered with a `resourceUri` in its metadata. This URI points to a virtual resource that serves the widget's HTML.

```mermaid
title "MCP App Basics Registration Flow"
graph TD
    subgraph "Server (Node.js)"
        S["McpServer"]
        RAT["registerAppTool()"]
        RAR["registerAppResource()"]
    end

    subgraph "Assets"
        HTML["Widget HTML Files"]
    end

    S --> RAT
    RAT -- "metadata._meta.ui.resourceUri" --> URI["ui://widget-name/index.html"]
    RAR -- "serves" --> HTML
    URI -.-> RAR
```

Sources: [mcp_app_basics_node/src/server.ts:22-28](), [mcp_app_basics_node/src/server.ts:102-131]()

### Widget Initialization
All widgets in this collection use the `useApp` hook from `@modelcontextprotocol/ext-apps/react` to establish the connection with the host (e.g., ChatGPT).

Sources: [src/call-server-tool/App.tsx:34-43](), [src/get-host-capabilities/App.tsx:32-46]()

---

## Data Flow Widgets

### Show Tool Result (`show_tool_result`)
Demonstrates how structured data flows from a server tool handler into a widget. The server returns a `structuredContent` object, which the widget consumes via the `ontoolresult` callback.

*   **Key Function**: The server handler returns an object containing both `content` (for the model) and `structuredContent` (for the widget) [mcp_app_basics_node/src/server.ts:147-152]().
*   **Widget Consumption**: The React component listens for `app.ontoolresult` and updates its local state with the provided data [src/call-server-tool/App.tsx:38-41]().

### Send Message (`send_message`)
Shows how a widget can programmatically insert a message into the conversation on behalf of the user using `app.sendMessage()`.

### Update Model Context (`update_model_context`)
Demonstrates "silent" context injection. The widget uses `app.updateModelContext()` to provide the model with background information that doesn't appear as a visible message in the chat history.

---

## Widget ↔ Server Interaction

### Call Server Tool (`call_server_tool`)
This widget demonstrates direct communication between the UI and the MCP server, bypassing the LLM. It allows the widget to trigger server-side logic (like rolling a dice) without the model needing to "decide" to call the tool.

```mermaid
title "Direct Tool Call Flow (call_server_tool)"
sequenceDiagram
    participant W as "Widget (App.tsx)"
    participant H as "Host (ChatGPT)"
    participant S as "Server (server.ts)"

    W->>H: app.callServerTool("roll_dice", {sides: 20})
    H->>S: call_server_tool__roll_dice({sides: 20})
    S-->>H: {rolled: 18}
    H-->>W: ToolResult
    Note over W: Update React state with result.rolled
```

*   **Server Implementation**: The server registers a specific "app-only" tool, often prefixed to distinguish it from model-accessible tools [mcp_app_basics_node/src/server.ts:291-300]().
*   **Widget Implementation**: The widget calls `app.callServerTool` and awaits the result [src/call-server-tool/App.tsx:74-77]().

Sources: [src/call-server-tool/App.tsx:69-99](), [mcp_app_basics_node/src/server.ts:291-310]()

---

## Host Interaction Widgets

### Host Theming (`host_theming`)
Demonstrates how to synchronize widget styles with the host application's appearance (Light/Dark mode and accent colors).

*   **`useHostStyles`**: Injects host-provided CSS variables into the widget's document [src/host-theming/App.tsx:44]().
*   **`useDocumentTheme`**: A hook that returns the current active theme string ("light" or "dark") [src/host-theming/App.tsx:45]().

### Host Information APIs
Three widgets demonstrate how to query the environment:
1.  **`get_host_capabilities`**: Uses `app.getHostCapabilities()` to check for features like `openLinks` or `serverTools` support [src/get-host-capabilities/App.tsx:39-40]().
2.  **`get_host_context`**: Uses `app.getHostContext()` for live info (dimensions, locale) and `app.onhostcontextchanged` to react to window resizing or theme flips [src/get-host-context/App.tsx:26-45]().
3.  **`get_host_version`**: Uses `app.getHostVersion()` to identify the host (e.g., "ChatGPT") and its current version [src/get-host-version/App.tsx:34-35]().

### UI Control
*   **Open Link**: Uses `app.openLink({ url })`. The host intercepts this and may apply security policies before opening [src/open-link/App.tsx:74]().
*   **Request Display Mode**: Allows the widget to request a transition between `normal`, `compact`, or `fullscreen` modes using `app.requestDisplayMode()`.

---

## Tool Lifecycle

### Streaming Tool Input (`streaming_tool_input`)
This advanced example shows how a widget can display real-time feedback as the model generates tool arguments.

*   **`ontoolinputpartial`**: This callback triggers as the model is still "typing" the JSON arguments for a tool call.
*   **`ontoolinput`**: Triggers once the model has finished generating arguments but before the tool is actually executed.
*   **`ontoolresult`**: Triggers after the server has processed the call.

Sources: [mcp_app_basics_node/src/server.ts:518-525](), [mcp_app_basics_node/README.md:51]()

---

