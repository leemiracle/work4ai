<!-- source: DeepWiki mcp.deepwiki.com · repo mixpeek/amux · page 9 iOS App · fetched 2026-10-26 -->

# iOS App

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ios.yml](.github/workflows/ios.yml)
- [ios/.ruby-version](ios/.ruby-version)
- [ios/AmuxApp/AmuxApp.entitlements](ios/AmuxApp/AmuxApp.entitlements)
- [ios/AmuxApp/Assets.xcassets/AppIcon.appiconset/Contents.json](ios/AmuxApp/Assets.xcassets/AppIcon.appiconset/Contents.json)
- [ios/AmuxApp/Assets.xcassets/Contents.json](ios/AmuxApp/Assets.xcassets/Contents.json)
- [ios/AmuxApp/Info.plist](ios/AmuxApp/Info.plist)
- [ios/AmuxApp/Sources/AmuxApp.swift](ios/AmuxApp/Sources/AmuxApp.swift)
- [ios/AmuxApp/Sources/ContentView.swift](ios/AmuxApp/Sources/ContentView.swift)
- [ios/AmuxApp/Sources/ServerManager.swift](ios/AmuxApp/Sources/ServerManager.swift)
- [ios/AmuxApp/Sources/ServerPickerView.swift](ios/AmuxApp/Sources/ServerPickerView.swift)
- [ios/AmuxApp/Sources/WebView.swift](ios/AmuxApp/Sources/WebView.swift)
- [ios/Gemfile.lock](ios/Gemfile.lock)
- [ios/fastlane/Matchfile](ios/fastlane/Matchfile)

</details>



The iOS app provides a native mobile interface to amux by wrapping the web dashboard in a WKWebView. It handles server configuration (cloud vs self-hosted), TLS certificate validation for Tailscale deployments, and navigation controls. The app is a thin client that displays the same web interface described in [Web Dashboard](#6).

For server-side deployment and multi-tenancy, see [Cloud Deployment](#4). For app deployment via TestFlight, see [iOS Deployment](#9.3).

---

## Overview

The iOS app is built with SwiftUI and consists of five main components:

| Component | File | Purpose |
|-----------|------|---------|
| `AmuxApp` | [ios/AmuxApp/Sources/AmuxApp.swift]() | App entry point, manages ServerManager lifecycle |
| `ServerManager` | [ios/AmuxApp/Sources/ServerManager.swift]() | ObservableObject that persists server configurations |
| `ServerPickerView` | [ios/AmuxApp/Sources/ServerPickerView.swift]() | Initial setup screen for selecting cloud vs self-hosted |
| `ContentView` | [ios/AmuxApp/Sources/ContentView.swift]() | Main view with WebView wrapper and navigation toolbar |
| `WebView` | [ios/AmuxApp/Sources/WebView.swift]() | UIViewRepresentable wrapper for WKWebView |

The app supports three deployment modes:
1. **Cloud** (`cloud.amux.io`) — Managed multi-tenant deployment with Clerk authentication
2. **Tailscale** — Self-hosted on a Mac accessible via Tailscale network (e.g. `https://amux.tail-xxxx.ts.net:8822`)
3. **Local Network** — Self-hosted on LAN (e.g. `https://192.168.1.10:8822`)

**Sources**: [ios/AmuxApp/Sources/AmuxApp.swift:1-18](), [ios/AmuxApp/Sources/ServerPickerView.swift:1-135]()

---

## Application Flow Diagram

```mermaid
stateDiagram-v2
    [*] --> AppLaunch: "User opens app"
    
    AppLaunch --> ServerManagerInit: "AmuxApp.body"
    ServerManagerInit --> CheckServerURL: "Load UserDefaults"
    
    CheckServerURL --> ServerPickerView: "serverURL == nil"
    CheckServerURL --> ContentView: "serverURL != nil"
    
    ServerPickerView --> CloudSelected: "Tap cloud.amux.io"
    ServerPickerView --> SelfHostedSheet: "Tap Self-hosted"
    
    CloudSelected --> SetCloudURL: "serverManager.selectServer()"
    SelfHostedSheet --> ValidateURL: "Enter custom URL"
    ValidateURL --> AddServer: "URL valid"
    ValidateURL --> ShowError: "URL invalid"
    ShowError --> SelfHostedSheet: "Retry"
    AddServer --> SetCustomURL: "serverManager.addServer()"
    
    SetCloudURL --> PersistToUserDefaults: "Save to UserDefaults"
    SetCustomURL --> PersistToUserDefaults: "Save to UserDefaults"
    PersistToUserDefaults --> ContentView: "Reload view hierarchy"
    
    ContentView --> LoadWebView: "WebView(url: serverURL)"
    LoadWebView --> HandleTLS: "didReceive challenge"
    HandleTLS --> BypassCertCheck: "Tailscale/localhost"
    HandleTLS --> ValidateCert: "cloud.amux.io"
    
    BypassCertCheck --> RenderDashboard: "Load amux web UI"
    ValidateCert --> RenderDashboard: "Load amux web UI"
    
    RenderDashboard --> UserInteraction: "View sessions/board"
    UserInteraction --> SettingsSheet: "Tap gear icon"
    SettingsSheet --> ServerList: "Show saved servers"
    ServerList --> SwitchServer: "Select different server"
    ServerList --> ResetServer: "Back to Setup"
    SwitchServer --> ContentView: "Reload WebView"
    ResetServer --> ServerPickerView: "Clear serverURL"
```

**Sources**: [ios/AmuxApp/Sources/AmuxApp.swift:8-17](), [ios/AmuxApp/Sources/ServerPickerView.swift:12-100](), [ios/AmuxApp/Sources/ContentView.swift:12-64]()

---

## Server Configuration System

### ServerManager Class

`ServerManager` is an `ObservableObject` that manages server persistence using `UserDefaults`. It stores:

- **Active Server** (`serverURL: URL?`) — Currently selected server, persisted to key `"serverURL"`
- **Saved Servers** (`savedServers: [SavedServer]`) — List of configured servers, persisted to key `"savedServers"` as JSON

The class provides these operations:

| Method | Signature | Behavior |
|--------|-----------|----------|
| `init()` | `init()` | Loads `savedServers` from JSON; defaults to `[SavedServer(name: "cloud.amux.io", url: "https://cloud.amux.io")]` if none exist |
| `selectServer` | `func selectServer(_ urlString: String)` | Sets `serverURL` and persists to UserDefaults |
| `addServer` | `func addServer(name: String, urlString: String) -> Bool` | Validates URL starts with `"http"`, normalizes trailing slash, appends to `savedServers` |
| `removeServer` | `func removeServer(at offsets: IndexSet)` | Deletes servers from list |
| `resetServer` | `func resetServer()` | Clears `serverURL`, returns to setup screen |

**Sources**: [ios/AmuxApp/Sources/ServerManager.swift:1-67]()

### SavedServer Model

```swift
struct SavedServer: Codable, Identifiable {
    var id: String { url }
    let name: String
    let url: String
}
```

The `id` is derived from `url` to ensure uniqueness. When encoded to JSON, each server looks like:

```json
{
  "name": "Home Mac",
  "url": "https://amux.tail-abc123.ts.net:8822"
}
```

**Sources**: [ios/AmuxApp/Sources/ServerManager.swift:62-66]()

---

## Server Selection UI

### ServerPickerView

This view displays when `serverManager.serverURL == nil`. It presents two primary options:

1. **Cloud Option** — Immediately selects `https://cloud.amux.io` via `serverManager.selectServer()`
2. **Self-Hosted Option** — Opens a modal sheet with custom URL input

The sheet validates URLs using `serverManager.addServer()`, which rejects URLs that don't start with `"http"`. The default port `8822` is assumed but must be explicitly included in the URL.

**Sources**: [ios/AmuxApp/Sources/ServerPickerView.swift:12-101]()

### ServerPickerView Component Hierarchy

```mermaid
graph TB
    SPV["ServerPickerView"]
    Header["VStack: Header"]
    Icon["Image: square.stack.3d.up.fill"]
    Title["Text: amux"]
    Subtitle["Text: Where do you run amux?"]
    
    Options["VStack: Options"]
    CloudBtn["ServerOptionButton<br/>cloud.amux.io"]
    SelfHostedBtn["ServerOptionButton<br/>Self-hosted"]
    
    Sheet["Sheet: .custom mode"]
    Form["Form"]
    NameField["TextField: Name"]
    URLField["TextField: URL"]
    ErrorText["Text: Invalid URL"]
    
    SPV --> Header
    Header --> Icon
    Header --> Title
    Header --> Subtitle
    
    SPV --> Options
    Options --> CloudBtn
    Options --> SelfHostedBtn
    
    SPV -.->|"mode == .custom"| Sheet
    Sheet --> Form
    Form --> NameField
    Form --> URLField
    Form --> ErrorText
    
    CloudBtn -.->|"onTapGesture"| SelectCloud["selectServer(cloud.amux.io)"]
    SelfHostedBtn -.->|"onTapGesture"| SetMode["mode = .custom"]
    Form -.->|"Connect button"| AddServer["addServer(name, url)"]
```

**Sources**: [ios/AmuxApp/Sources/ServerPickerView.swift:12-135]()

---

## WebView Implementation

### WKWebView Configuration

The `WebView` struct wraps `WKWebView` in a `UIViewRepresentable`. Key configurations in `makeUIView()`:

| Configuration | Value | Purpose |
|---------------|-------|---------|
| `allowsInlineMediaPlayback` | `true` | Enable video playback without fullscreen |
| `dataDetectorTypes` | `[]` | Disable phone/email auto-detection |
| `allowsBackForwardNavigationGestures` | `true` | Enable swipe navigation |
| `contentInsetAdjustmentBehavior` | `.automatic` | Respect safe areas |

A `UIRefreshControl` is attached to the scroll view for pull-to-refresh functionality.

**Sources**: [ios/AmuxApp/Sources/WebView.swift:15-35]()

### TLS Certificate Handling

The `Coordinator` class implements `WKNavigationDelegate.webView(_:didReceive:completionHandler:)` to handle TLS certificate challenges. This is required for self-hosted servers using self-signed certificates (generated by amux-server.py via Tailscale→mkcert→fallback chain).

Certificate bypass logic:

```swift
let host = challenge.protectionSpace.host
let isTailscale = host.contains(".ts.net") || host.hasSuffix(".local") || host == "localhost"
if isTailscale {
    completionHandler(.useCredential, URLCredential(trust: serverTrust))
} else {
    completionHandler(.performDefaultHandling, nil)
}
```

This **only** bypasses certificate validation for Tailscale (`.ts.net`), local (`.local`), and `localhost` hosts. Production `cloud.amux.io` uses standard certificate validation.

**Sources**: [ios/AmuxApp/Sources/WebView.swift:54-71]()

### Navigation Policy

The `decidePolicyFor navigationAction` delegate intercepts link taps. If the user taps a link that navigates away from the amux host (e.g., external documentation), it opens in Safari via `UIApplication.shared.open()` and cancels the WebView navigation:

```swift
if action.navigationType == .linkActivated && url.host != serverHost {
    UIApplication.shared.open(url)
    return .cancel
}
```

This prevents users from accidentally navigating away from the dashboard in the app.

**Sources**: [ios/AmuxApp/Sources/ContentView.swift:66-77]()

---

## ContentView Navigation

### Toolbar Structure

```mermaid
graph LR
    subgraph "NavigationBar"
        Leading["ToolbarItemGroup: .navigationBarLeading"]
        Principal["ToolbarItem: .principal"]
        Trailing["ToolbarItem: .navigationBarTrailing"]
    end
    
    subgraph "Leading Buttons"
        BackBtn["Button: chevron.left<br/>webView.goBack()"]
        ForwardBtn["Button: chevron.right<br/>webView.goForward()"]
    end
    
    subgraph "Principal"
        HostLabel["Text: serverURL.host<br/>font: .caption"]
    end
    
    subgraph "Trailing Button"
        SettingsBtn["Button: gear<br/>showSettings = true"]
    end
    
    Leading --> BackBtn
    Leading --> ForwardBtn
    Principal --> HostLabel
    Trailing --> SettingsBtn
    
    SettingsBtn -.->|"sheet"| SettingsView["SettingsView<br/>Server list + Add/Remove"]
```

The back/forward buttons are disabled based on `canGoBack` and `canGoForward` bindings, which are updated by the `Coordinator` in `didFinish navigation`.

**Sources**: [ios/AmuxApp/Sources/ContentView.swift:34-58]()

### Settings Sheet

The settings sheet displays:

1. **Servers Section** — List of `savedServers` with checkmark on active server
2. **Add Server Button** — Opens `AddServerView` modal
3. **Back to Setup Button** — Calls `serverManager.resetServer()` (destructive style)

Tapping a server in the list calls `serverManager.selectServer()` and dismisses the sheet, which triggers a reload of the WebView in `ContentView` due to the `@Published` property change.

**Sources**: [ios/AmuxApp/Sources/ContentView.swift:82-143]()

---

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant AmuxApp as "AmuxApp.body"
    participant SM as "ServerManager"
    participant UD as "UserDefaults"
    participant SPV as "ServerPickerView"
    participant CV as "ContentView"
    participant WV as "WebView"
    participant WKWV as "WKWebView"
    participant Server as "amux-server.py"
    
    Note over User,Server: App Launch
    User->>AmuxApp: Open app
    AmuxApp->>SM: @StateObject init()
    SM->>UD: Load "savedServers"
    UD-->>SM: JSON array or nil
    SM->>UD: Load "serverURL"
    UD-->>SM: String or nil
    
    alt serverURL == nil
        AmuxApp->>SPV: Render ServerPickerView
        SPV->>User: Show cloud vs self-hosted options
        User->>SPV: Select "cloud.amux.io"
        SPV->>SM: selectServer("https://cloud.amux.io")
        SM->>UD: Set "serverURL"
        SM->>AmuxApp: @Published change triggers re-render
    end
    
    AmuxApp->>CV: Render ContentView
    CV->>WV: WebView(url: serverURL)
    WV->>WKWV: load(URLRequest)
    WKWV->>Server: HTTPS GET /
    
    alt Self-signed cert (Tailscale)
        WKWV->>WV: didReceive challenge
        WV->>WV: Check host contains ".ts.net"
        WV->>WKWV: useCredential(trust)
    end
    
    Server-->>WKWV: HTML dashboard
    WKWV->>WV: didFinish navigation
    WV->>CV: Update isLoading = false
    CV->>User: Display dashboard
    
    Note over User,Server: Server Switch
    User->>CV: Tap gear icon
    CV->>CV: showSettings = true
    CV->>User: Present SettingsView sheet
    User->>SM: Select different server
    SM->>UD: Update "serverURL"
    SM->>CV: @Published change
    CV->>WV: updateUIView(webView)
    WV->>WV: Check if host changed
    WV->>WKWV: load(URLRequest) with new URL
```

**Sources**: [ios/AmuxApp/Sources/AmuxApp.swift:8-17](), [ios/AmuxApp/Sources/ServerManager.swift:5-44](), [ios/AmuxApp/Sources/WebView.swift:37-42]()

---

## App Metadata & Permissions

The `Info.plist` configures app behavior and requested permissions:

| Key | Value | Purpose |
|-----|-------|---------|
| `CFBundleIdentifier` | `io.amux.app` | Unique app identifier for App Store |
| `ITSAppUsesNonExemptEncryption` | `false` | Exempt from export compliance (no custom crypto) |
| `NSFaceIDUsageDescription` | `"Used to protect access to your amux dashboard"` | Justification for biometric auth (unused in current version) |
| `UISupportedInterfaceOrientations` | `Portrait, PortraitUpsideDown` | iPhone locked to portrait |
| `UISupportedInterfaceOrientations~ipad` | `All orientations` | iPad supports landscape |

**Sources**: [ios/AmuxApp/Info.plist:1-43]()

---

## File Structure

```
ios/
├── AmuxApp/
│   ├── Sources/
│   │   ├── AmuxApp.swift              # @main entry point, ServerManager lifecycle
│   │   ├── ServerManager.swift        # ObservableObject for server config
│   │   ├── ServerPickerView.swift     # Initial setup UI
│   │   ├── ContentView.swift          # Main view with WebView + toolbar
│   │   └── WebView.swift              # WKWebView UIViewRepresentable wrapper
│   ├── Assets.xcassets/               # App icon and assets
│   ├── Info.plist                     # App metadata and permissions
│   └── AmuxApp.entitlements           # App capabilities (currently empty)
├── fastlane/
│   ├── Fastfile                       # Deployment automation (see §9.3)
│   └── Matchfile                      # Code signing configuration
├── Gemfile                            # Ruby dependencies (fastlane)
├── Gemfile.lock                       # Locked dependency versions
└── project.yml                        # XcodeGen project specification
```

**Sources**: [ios/AmuxApp/Sources/AmuxApp.swift:1](), [ios/AmuxApp/Sources/ServerManager.swift:1](), [ios/AmuxApp/Sources/ServerPickerView.swift:1](), [ios/AmuxApp/Sources/ContentView.swift:1](), [ios/AmuxApp/Sources/WebView.swift:1]()

---

