<!-- source: DeepWiki mcp.deepwiki.com · repo browseros-ai/BrowserOS · page 8 DevTools Protocol Extensions · fetched 2026-10-29 -->

# DevTools Protocol Extensions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/browseros/chromium_patches/chrome/browser/devtools/BUILD.gn](packages/browseros/chromium_patches/chrome/browser/devtools/BUILD.gn)
- [packages/browseros/chromium_patches/chrome/browser/devtools/chrome_devtools_session.cc](packages/browseros/chromium_patches/chrome/browser/devtools/chrome_devtools_session.cc)
- [packages/browseros/chromium_patches/chrome/browser/devtools/chrome_devtools_session.h](packages/browseros/chromium_patches/chrome/browser/devtools/chrome_devtools_session.h)
- [packages/browseros/chromium_patches/chrome/browser/devtools/inspector_protocol_config.json](packages/browseros/chromium_patches/chrome/browser/devtools/inspector_protocol_config.json)
- [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/bookmarks_handler.cc](packages/browseros/chromium_patches/chrome/browser/devtools/protocol/bookmarks_handler.cc)
- [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/bookmarks_handler.h](packages/browseros/chromium_patches/chrome/browser/devtools/protocol/bookmarks_handler.h)
- [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/browser_handler.cc](packages/browseros/chromium_patches/chrome/browser/devtools/protocol/browser_handler.cc)
- [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/browser_handler.h](packages/browseros/chromium_patches/chrome/browser/devtools/protocol/browser_handler.h)
- [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/browser_handler_android.cc](packages/browseros/chromium_patches/chrome/browser/devtools/protocol/browser_handler_android.cc)
- [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/browser_handler_android.h](packages/browseros/chromium_patches/chrome/browser/devtools/protocol/browser_handler_android.h)
- [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/devtools_protocol_browsertest.cc](packages/browseros/chromium_patches/chrome/browser/devtools/protocol/devtools_protocol_browsertest.cc)
- [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/history_handler.cc](packages/browseros/chromium_patches/chrome/browser/devtools/protocol/history_handler.cc)
- [packages/browseros/chromium_patches/third_party/blink/public/devtools_protocol/domains/Browser.pdl](packages/browseros/chromium_patches/third_party/blink/public/devtools_protocol/domains/Browser.pdl)

</details>



## Purpose and Scope

BrowserOS extends the Chrome DevTools Protocol (CDP) with custom domains to enable programmatic browser automation, bookmark management, and history access. These extensions allow external MCP clients and internal agent components to control browser windows, tabs, tab groups, bookmarks, and browsing history through a standard CDP interface.

This page provides an overview of the custom CDP domains and their integration into Chromium. For detailed command references, see the domain-specific pages:
- Browser domain: [Browser Domain](#8.1) (windows), [Tab Management API](#8.2) (tabs), [Window Management API](#8.3) (window management)
- Bookmarks domain: [Bookmarks API](#8.4)
- History domain: [History API](#8.5)

For information about the BrowserOS MCP server that exposes these protocols to external clients, see [MCP Server](#5).

---

## Architecture Overview

BrowserOS extends CDP by adding custom protocol domains to Chromium's DevTools infrastructure. These extensions are implemented as protocol handlers that integrate with Chromium's existing CDP dispatch system.

### CDP Handler Architecture

```mermaid
graph TB
    subgraph "External Clients"
        [MCPClient] -- "CDP JSON-RPC" --> [AgentHost]
        [BunServer] -- "CDP JSON-RPC" --> [AgentHost]
    end
    
    subgraph "CDP Layer"
        [AgentHost] -- "content::DevToolsAgentHost" --> [Session]
        [Session] -- "ChromeDevToolsSession" --> [Dispatcher]
        [Dispatcher] -- "protocol::UberDispatcher" --> [Handlers]
    end
    
    subgraph "Handlers"
        [BrowserHandler]
        [BookmarksHandler]
        [HistoryHandler]
    end
    
    subgraph "Chromium Core"
        [BrowserHandler] --> [TabStripModel]
        [BrowserHandler] --> [BrowserWindowInterface]
        [BookmarksHandler] --> [BookmarkModel]
        [HistoryHandler] --> [HistoryService]
    end
```

**Sources:** [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/browser_handler.h:20-142](), [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/bookmarks_handler.cc:91-96](), [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/history_handler.cc:47-51](), [packages/browseros/chromium_patches/chrome/browser/devtools/chrome_devtools_session.cc:18-31]()

### Protocol Definition and Code Generation

CDP uses Protocol Definition Language (PDL) files to define domains, types, commands, and events. Chromium's build system generates C++ code from these definitions based on the `inspector_protocol_config.json` configuration [packages/browseros/chromium_patches/chrome/browser/devtools/inspector_protocol_config.json:1-27]().

```mermaid
graph LR
    subgraph "Protocol Definition"
        [BrowserPDL] -- "Browser.pdl" --> [InspectorConfig]
        [BookmarksPDL] -- "Bookmarks.pdl" --> [InspectorConfig]
        [HistoryPDL] -- "History.pdl" --> [InspectorConfig]
    end
    
    subgraph "Build Pipeline"
        [InspectorConfig] -- "Code Generator" --> [GeneratedCode]
    end
    
    subgraph "C++ Entities"
        [GeneratedCode] -. "Implements Backend" .-> [BrowserHandler]
        [GeneratedCode] -. "Implements Backend" .-> [BookmarksHandler]
        [GeneratedCode] -. "Implements Backend" .-> [HistoryHandler]
    end
```

**Sources:** [packages/browseros/chromium_patches/third_party/blink/public/devtools_protocol/domains/Browser.pdl:6-243](), [packages/browseros/chromium_patches/chrome/browser/devtools/inspector_protocol_config.json:8-23]()

---

## Custom CDP Domains

### Browser Domain (Extended)

The Browser domain is a standard CDP domain that BrowserOS significantly extends with window, tab, and tab group management capabilities [packages/browseros/chromium_patches/third_party/blink/public/devtools_protocol/domains/Browser.pdl:6-243]().

| Category | Commands Added | Purpose |
|----------|----------------|---------|
| **Window Management** | `getWindows`, `getActiveWindow`, `createWindow`, `closeWindow`, `activateWindow`, `setWindowVisibility` | Create, query, and control browser windows |
| **Tab Management** | `getTabs`, `getActiveTab`, `getTabInfo`, `createTab`, `closeTab`, `activateTab`, `moveTab`, `duplicateTab`, `pinTab`, `unpinTab`, `showTab` | Full tab lifecycle and state management |
| **Tab Group Management** | `getTabGroups`, `createTabGroup`, `updateTabGroup`, `closeTabGroup`, `addTabsToGroup`, `removeTabsFromGroup`, `moveTabGroup` | Organize tabs into collapsible groups |
| **ID Mapping** | `getTabForTarget`, `getTargetForTab` | Convert between CDP target IDs and tab IDs |

**Key Features:**
- **Retired Hidden State**: Recent updates have retired support for hidden windows and tabs to ensure better resource management and user visibility [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/browser_handler.cc:42-45]().
- **Tab Information**: The `TabInfo` object provides comprehensive metadata including `url`, `title`, `isLoading`, `isPinned`, and `groupId` [packages/browseros/chromium_patches/third_party/blink/public/devtools_protocol/domains/Browser.pdl:37-51]().
- **Dual Identification**: Tabs can be identified by CDP `targetId` (string) or persistent `tabId` (integer) [packages/browseros/chromium_patches/third_party/blink/public/devtools_protocol/domains/Browser.pdl:104-105]().

**Sources:** [packages/browseros/chromium_patches/third_party/blink/public/devtools_protocol/domains/Browser.pdl:6-243](), [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/browser_handler.h:43-142](), [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/browser_handler.cc:42-45]()

### Bookmarks Domain (New)

A new CDP domain providing complete bookmark management functionality [packages/browseros/chromium_patches/chrome/browser/devtools/inspector_protocol_config.json:13-17]().

| Command | Purpose |
|---------|---------|
| `getBookmarks` | Retrieve all bookmarks, optionally filtered by folder |
| `searchBookmarks` | Search bookmarks by query string |
| `createBookmark` | Create a new bookmark or folder |
| `updateBookmark` | Modify bookmark title or URL |
| `moveBookmark` | Change bookmark parent or position |
| `removeBookmark` | Delete a bookmark or folder |

**Data Model:**
- Each bookmark has a unique `id` (string) [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/bookmarks_handler.cc:38-38]().
- Bookmarks are organized in a tree structure with `parentId` and `index` [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/bookmarks_handler.cc:46-55]().
- Supports both URL bookmarks and folders [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/bookmarks_handler.cc:40-42]().

**Sources:** [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/bookmarks_handler.cc:115-199](), [packages/browseros/chromium_patches/chrome/browser/devtools/inspector_protocol_config.json:13-17]()

### History Domain (New)

A new CDP domain for querying and managing browsing history with asynchronous operations [packages/browseros/chromium_patches/chrome/browser/devtools/inspector_protocol_config.json:18-23]().

| Command | Purpose | Async |
|---------|---------|-------|
| `search` | Search history by query string with time range filters | Yes |
| `getRecent` | Get most recent history entries | Yes |
| `deleteUrl` | Remove all history entries for a specific URL | Yes |
| `deleteRange` | Delete history within a time range | Yes |

**Asynchronous Design:**
- History operations use callbacks due to database I/O [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/history_handler.cc:77-102]().
- Handlers use `base::CancelableTaskTracker` to manage async operations and prevent memory issues on destruction [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/history_handler.cc:102-102]().

**Sources:** [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/history_handler.cc:73-167](), [packages/browseros/chromium_patches/chrome/browser/devtools/inspector_protocol_config.json:19-23]()

---

## Handler Integration

### Profile Context Resolution

Handlers need a `Profile*` to access bookmark and history services. Resolution strategy:

1. **Target-attached sessions**: Extract `Profile` from the target's `BrowserContext` via `content::DevToolsAgentHost` [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/bookmarks_handler.cc:100-103]().
2. **Browser-level sessions**: Fall back to the last active window's profile using `GetLastActiveBrowserWindowInterfaceWithAnyProfile()` [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/bookmarks_handler.cc:105-107]().

**Sources:** [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/bookmarks_handler.cc:99-108](), [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/history_handler.cc:55-64]()

---

## Platform Differences

### Desktop vs. Android

The implementation varies significantly between Desktop and Android.

| Feature | Desktop (Mac/Win/Linux) | Android |
|---------|-------------------------|---------|
| Window Management | ✅ Full Support | ❌ Not Implemented |
| Tab Management | ✅ Full Support | ⚠️ Only ID Mapping |
| Bookmarks | ✅ Full Support | ❌ Not Implemented |
| History | ✅ Full Support | ❌ Not Implemented |

On Android, `BrowserHandlerAndroid` provides mapping between targets and Android Tab IDs [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/browser_handler_android.cc:17-68](), but returns `Response::MethodNotFound(kNotImplemented)` for most window and tab management commands [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/browser_handler_android.cc:80-202]().

**Sources:** [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/browser_handler_android.cc:80-202](), [packages/browseros/chromium_patches/chrome/browser/devtools/protocol/browser_handler.cc:43-142]()

---

## Build Configuration

### Dependencies and Sources

Custom CDP handlers are integrated into the `devtools` static library in Chromium's build system via `chrome/browser/devtools/BUILD.gn` [packages/browseros/chromium_patches/chrome/browser/devtools/BUILD.gn:9-40]().

**Sources:** [packages/browseros/chromium_patches/chrome/browser/devtools/BUILD.gn:9-40](), [packages/browseros/chromium_patches/chrome/browser/devtools/BUILD.gn:391-401]()

---

## Type System

### Custom Types

The extended Browser domain introduces several custom types defined in `Browser.pdl`:

| Type | Description |
|------|-------------|
| `TabID` | Integer identifier for tabs [packages/browseros/chromium_patches/third_party/blink/public/devtools_protocol/domains/Browser.pdl:9-9]() |
| `WindowType` | Enum: `normal`, `popup`, `app`, `devtools`, `app_popup`, `picture_in_picture` [packages/browseros/chromium_patches/third_party/blink/public/devtools_protocol/domains/Browser.pdl:11-18]() |
| `WindowInfo` | Object containing window state, bounds, and tab counts [packages/browseros/chromium_patches/third_party/blink/public/devtools_protocol/domains/Browser.pdl:26-35]() |
| `TabInfo` | Object containing tab URL, title, and loading status [packages/browseros/chromium_patches/third_party/blink/public/devtools_protocol/domains/Browser.pdl:37-51]() |

**Sources:** [packages/browseros/chromium_patches/third_party/blink/public/devtools_protocol/domains/Browser.pdl:9-63]()

---

