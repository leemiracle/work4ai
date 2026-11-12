> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/8-knowledge-base-and-rag-system](https://deepwiki.com/thinkinaixyz/deepchat/8-knowledge-base-and-rag-system)（Wayback 快照 2026-02-16）
> DeepWiki deepchat/8-knowledge-base-and-rag-system

# Advanced Features

  Relevant source files 
 - [src/main/presenter/deeplinkPresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/deeplinkPresenter/index.ts)
 - [src/main/presenter/sqlitePresenter/tables/conversations.ts](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/sqlitePresenter/tables/conversations.ts)
 - [src/main/presenter/tabPresenter.ts](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/tabPresenter.ts)
 - [src/main/presenter/windowPresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/windowPresenter/index.ts)
 - [src/renderer/shell/App.vue](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/shell/App.vue)
 - [src/renderer/shell/components/AppBar.vue](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/shell/components/AppBar.vue)
 - [src/renderer/shell/components/app-bar/AppBarTabItem.vue](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/shell/components/app-bar/AppBarTabItem.vue)
 - [src/renderer/shell/stores/tab.ts](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/shell/stores/tab.ts)
 - [src/renderer/src/components/ChatConfig.vue](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/ChatConfig.vue)
 - [src/renderer/src/components/ChatView.vue](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/ChatView.vue)
 - [src/renderer/src/components/MessageNavigationSidebar.vue](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/MessageNavigationSidebar.vue)
 - [src/renderer/src/components/ModelSelect.vue](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/ModelSelect.vue)
 - [src/renderer/src/components/NewThread.vue](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/NewThread.vue)
 - [src/renderer/src/components/ThreadsView.vue](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/ThreadsView.vue)
 - [src/renderer/src/components/TitleView.vue](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/TitleView.vue)
 - [src/renderer/src/components/message/MessageList.vue](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/message/MessageList.vue)
 - [src/renderer/src/composables/message/useMessageScroll.ts](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/composables/message/useMessageScroll.ts)
 - [src/renderer/src/views/ChatTabView.vue](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/views/ChatTabView.vue)
 - [src/renderer/src/views/SettingsTabView.vue](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/views/SettingsTabView.vue)
 
  
## Purpose and Scope

 This page documents specialized features and integrations that extend DeepChat's core functionality beyond basic chat operations. These advanced features include:

 
 - **DeepLink Protocol**: Custom URL scheme handling for application launching and MCP server installation
 - **Multi-Window Tab Operations**: Cross-window tab management with drag-and-drop support
 - **Floating Windows**: Quick access chat windows with system-wide hotkeys
 - **Shell Tooltip System**: Custom tooltip overlays for improved UX
 
 For information about MCP integration, see [MCP System Architecture](https://deepwiki.com/thinkinaixyz/deepchat/4.1-mcp-system-architecture). For window and tab architecture basics, see [Window and Tab Management](https://deepwiki.com/thinkinaixyz/deepchat/2.3-window-and-tab-management).

 
---

 
## DeepLink Protocol System

 DeepChat implements a custom `deepchat://` URL protocol for external application integration and automated workflows. The system supports cold-start scenarios, parameter sanitization, and coordinated initialization with subsystems like MCP.

 
### DeepLink Architecture

 
```

```

 **Sources:** [src/main/presenter/deeplinkPresenter/index.ts1-400](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/deeplinkPresenter/index.ts#L1-L400) [src/renderer/src/components/NewThread.vue435-497](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/NewThread.vue#L435-L497)

 
### Supported DeepLink Commands

 
| Command | Format | Parameters | Purpose |
|---|---|---|---|
| start | deepchat://start?params | msg, model, system, mentions | Launch app with pre-filled message |
| mcp/install | deepchat://mcp/install?json=base64 | json (base64-encoded MCP config) | Install MCP server configuration |

 **Parameter Sanitization**: All parameters undergo security validation via `sanitizeMessageContent()` and `sanitizeStringParameter()` methods [src/main/presenter/deeplinkPresenter/index.ts318-353](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/deeplinkPresenter/index.ts#L318-L353)

 **Security Note**: The `yolo` auto-send parameter has been disabled for security reasons [src/main/presenter/deeplinkPresenter/index.ts252-254](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/deeplinkPresenter/index.ts#L252-L254)

 
### Cold Start Handling

 
```

```

 **Sources:** [src/main/presenter/deeplinkPresenter/index.ts152-180](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/deeplinkPresenter/index.ts#L152-L180) [src/main/presenter/deeplinkPresenter/index.ts69-77](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/deeplinkPresenter/index.ts#L69-L77)

 
### MCP Installation Flow

 The MCP installation command requires coordination with the MCP subsystem initialization:

 
```

```

 **Sources:** [src/main/presenter/deeplinkPresenter/index.ts79-87](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/deeplinkPresenter/index.ts#L79-L87) [src/main/presenter/deeplinkPresenter/index.ts297-413](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/deeplinkPresenter/index.ts#L297-L413)

 
### Integration with NewThread Component

 The `NewThread.vue` component watches for deeplink cache updates and applies them automatically:

 
```

```

 **Sources:** [src/renderer/src/components/NewThread.vue436-497](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/src/components/NewThread.vue#L436-L497)

 
---

 
## Multi-Window Tab Operations

 DeepChat supports advanced tab management including drag-and-drop reordering, cross-window tab movement, and tab detachment to create new windows. The system enforces type safety between chat tabs (`local://chat`) and browser tabs (external URLs).

 
### Tab Management Architecture

 
```

```

 **Sources:** [src/main/presenter/tabPresenter.ts16-46](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/tabPresenter.ts#L16-L46) [src/main/presenter/tabPresenter.ts156-272](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/tabPresenter.ts#L156-L272) [src/main/presenter/tabPresenter.ts401-542](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/tabPresenter.ts#L401-L542)

 
### Tab Type Compatibility Matrix

 
| Source Tab Type | Target Window Type | Allowed | Notes |
|---|---|---|---|
| local://chat | chat | ✓ | Normal case |
| local://chat | browser | ✗ | Browser windows cannot host chat tabs |
| External URL | chat | ✗ | Chat windows cannot host browser tabs (requires allowNonLocal flag) |
| External URL | browser | ✓ | Normal case |

 **Validation Logic:** [src/main/presenter/tabPresenter.ts447-462](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/tabPresenter.ts#L447-L462) [src/main/presenter/tabPresenter.ts502-512](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/tabPresenter.ts#L502-L512)

 
### Drag-and-Drop Tab Reordering

 The AppBar component implements a complete drag-and-drop system for tab reordering and cross-window movement:

 
```

```

 **Sources:** [src/renderer/shell/components/AppBar.vue308-466](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/shell/components/AppBar.vue#L308-L466) [src/renderer/shell/stores/tab.ts57-81](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/shell/stores/tab.ts#L57-L81) [src/main/presenter/tabPresenter.ts495-542](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/tabPresenter.ts#L495-L542)

 
### Tab Detachment to New Window

 Users can detach tabs by dragging them outside the window bounds, creating a new window:

 
```

```

 **Sources:** [src/renderer/shell/components/AppBar.vue434-487](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/shell/components/AppBar.vue#L434-L487) [src/main/presenter/windowPresenter/index.ts682-693](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/windowPresenter/index.ts#L682-L693)

 
### WebContentsView Bounds Management

 The system maintains precise control over tab view positioning relative to the window chrome:

 
```

```

 **Bounds Calculation:** [src/main/presenter/tabPresenter.ts838-864](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/tabPresenter.ts#L838-L864)

 
```

```

 **Sources:** [src/main/presenter/tabPresenter.ts838-864](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/tabPresenter.ts#L838-L864) [src/renderer/shell/App.vue60-72](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/shell/App.vue#L60-L72)

 
---

 
## Floating Chat Window System

 DeepChat includes a floating chat window that provides quick access to AI assistance from anywhere on the system. The window can be toggled via system-wide hotkeys and maintains its own lifecycle separate from main windows.

 
### FloatingChatWindow Architecture

 
```

```

 **Sources:** [src/main/presenter/windowPresenter/FloatingChatWindow.ts](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/windowPresenter/FloatingChatWindow.ts) (referenced but not provided in files)

 
### Integration with WindowPresenter

 The floating window is managed as a singleton instance:

 
```

```

 **Sources:** [src/main/presenter/windowPresenter/index.ts41](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/windowPresenter/index.ts#L41-L41) [src/main/presenter/windowPresenter/index.ts70-79](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/windowPresenter/index.ts#L70-L79)

 
---

 
## Shell Tooltip Overlay System

 DeepChat implements a custom tooltip overlay system for the shell interface, providing hover tooltips without blocking the window's traffic light controls on macOS.

 
### Tooltip System Architecture

 
```

```

 **Sources:** [src/renderer/shell/components/AppBar.vue204-268](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/renderer/shell/components/AppBar.vue#L204-L268) [src/main/presenter/windowPresenter/index.ts81-130](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/windowPresenter/index.ts#L81-L130)

 
### Tooltip Overlay Window Properties

 The tooltip overlay is a separate frameless window positioned above the parent:

 
```

```

 **Fullscreen Handling**: Tooltips are automatically destroyed when entering fullscreen to prevent blocking macOS traffic lights [src/main/presenter/windowPresenter/index.ts869-877](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/windowPresenter/index.ts#L869-L877)

 **Sources:** [src/main/presenter/windowPresenter/index.ts1088-1156](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/windowPresenter/index.ts#L1088-L1156)

 
---

 
## Window Focus and Tab Activation Coordination

 The system implements sophisticated focus management to prevent race conditions and ensure proper tab activation timing:

 
```

```

 **Focus Debouncing**: The system prevents rapid focus calls within 100ms using `windowFocusStates.lastFocusTime` [src/main/presenter/windowPresenter/index.ts505-529](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/windowPresenter/index.ts#L505-L529)

 **Sources:** [src/main/presenter/windowPresenter/index.ts32-40](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/windowPresenter/index.ts#L32-L40) [src/main/presenter/windowPresenter/index.ts536-568](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/windowPresenter/index.ts#L536-L568) [src/main/presenter/windowPresenter/index.ts764-813](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/windowPresenter/index.ts#L764-L813)

 
---

 
## Window Lifecycle and Close Behavior

 DeepChat implements platform-specific close behavior with tray hiding support:

 
### Close Event Flow

 
```

```

 **Close-to-Quit vs Hide-to-Tray**: Controlled by `getCloseToQuit()` setting [src/main/presenter/windowPresenter/index.ts912-960](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/windowPresenter/index.ts#L912-L960)

 **Fullscreen Black Screen Fix**: The system exits fullscreen before hiding to prevent visual artifacts [src/main/presenter/windowPresenter/index.ts930-949](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/windowPresenter/index.ts#L930-L949)

 **Sources:** [src/main/presenter/windowPresenter/index.ts912-992](https://github.com/thinkinaixyz/deepchat/blob/89600d8b/src/main/presenter/windowPresenter/index.ts#L912-L992)
