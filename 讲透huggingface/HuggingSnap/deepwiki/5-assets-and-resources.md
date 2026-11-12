<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/HuggingSnap · page 5 Assets and Resources · fetched 2026-10-26 -->

# Assets and Resources

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [HuggingSnap/Assets.xcassets/AppIcon.appiconset/Contents.json](HuggingSnap/Assets.xcassets/AppIcon.appiconset/Contents.json)
- [HuggingSnap/Assets.xcassets/GYellow.colorset/Contents.json](HuggingSnap/Assets.xcassets/GYellow.colorset/Contents.json)
- [HuggingSnap/Assets.xcassets/Gold.colorset/Contents.json](HuggingSnap/Assets.xcassets/Gold.colorset/Contents.json)
- [HuggingSnap/Assets.xcassets/huggy.fill.symbolset/huggy.fill.svg](HuggingSnap/Assets.xcassets/huggy.fill.symbolset/huggy.fill.svg)

</details>



This document details the visual assets and design resources used in the HuggingSnap application. It covers the app icon, color palette, and custom symbols that maintain visual consistency and branding throughout the application. For information about project configuration and build settings, see [Project Configuration](#3.1).

## App Icon

HuggingSnap uses a custom app icon named "SmolVLM logo.png" configured for iOS platform display with support for different appearance modes.

```mermaid
graph TD
    AppIcon["AppIcon.appiconset"]
    Icon["SmolVLM logo.png (1024x1024)"]
    LightMode["Light Mode Display"]
    DarkMode["Dark Mode Display"]
    TintedMode["Tinted Mode Display"]
    
    AppIcon --> Icon
    AppIcon --> LightMode
    AppIcon --> DarkMode
    AppIcon --> TintedMode
```

Sources: [HuggingSnap/Assets.xcassets/AppIcon.appiconset/Contents.json:1-36]()

## Color System

The application employs a custom color palette defined in the asset catalog for consistent UI styling. All colors support both light and dark appearance modes.

### GYellow

A light yellow color primarily used for highlighting and accents:

| Property | Light Mode Value |
|----------|------------------|
| Color Space | Display P3 |
| Alpha | 1.000 |
| Red | 1.000 |
| Green | 0.902 |
| Blue | 0.761 |

Sources: [HuggingSnap/Assets.xcassets/GYellow.colorset/Contents.json:1-29]()

### Gold

A muted gold color used for UI accents and details:

| Property | Light Mode Value |
|----------|------------------|
| Color Space | Display P3 |
| Alpha | 1.000 |
| Red | 0.643 |
| Green | 0.486 |
| Blue | 0.318 |

Sources: [HuggingSnap/Assets.xcassets/Gold.colorset/Contents.json:1-29]()

## Custom SF Symbols

### huggy.fill

A custom SF Symbol that represents a chat bubble with a face, used throughout the UI. It supports multiple weights, scales, and appearance modes for versatile display options.

```mermaid
graph TD
    HuggyFill["huggy.fill Symbol"]
    RenderModes["Rendering Modes"]
    WeightsScales["Weights and Scales"]
    
    HuggyFill --> RenderModes
    HuggyFill --> WeightsScales
    
    RenderModes --> Monochrome["Monochrome Mode"]
    RenderModes --> Multicolor["Multicolor Mode (SystemRed/Yellow)"]
    RenderModes --> Hierarchical["Hierarchical Mode (Primary/Secondary)"]
    
    WeightsScales --> Weights["9 Weights (Ultralight to Black)"]
    WeightsScales --> Scales["3 Scales (Small, Medium, Large)"]
```

Sources: [HuggingSnap/Assets.xcassets/huggy.fill.symbolset/huggy.fill.svg:1-199]()

## Asset Access in Code

The following diagram illustrates how these assets are accessed within the codebase:

```mermaid
graph LR
    AssetCatalog["Assets.xcassets"]
    CodeAccess["Code Access Patterns"]
    Views["UI Components"]
    
    AssetCatalog --> AppIcon["AppIcon.appiconset"]
    AssetCatalog --> GYellow["GYellow.colorset"]
    AssetCatalog --> Gold["Gold.colorset"]
    AssetCatalog --> HuggyFill["huggy.fill.symbolset"]
    
    GYellow --> CodeAccess
    Gold --> CodeAccess
    HuggyFill --> CodeAccess
    
    CodeAccess --> UIKitColor["UIColor(named: &quot;GYellow&quot;)"]
    CodeAccess --> SwiftUIColor["Color(&quot;Gold&quot;)"]
    CodeAccess --> Symbol["Image(systemName: &quot;huggy.fill&quot;)"]
    
    UIKitColor --> Views
    SwiftUIColor --> Views
    Symbol --> Views
    
    Views --> ContentView["ContentView"]
    Views --> ControlView["ControlView"]
    Views --> MessageView["MessageView"]
    Views --> InputView["InputView"]
    Views --> SettingsView["SettingsView"]
```

Sources:
- [HuggingSnap/Assets.xcassets/GYellow.colorset/Contents.json:1-29]()
- [HuggingSnap/Assets.xcassets/Gold.colorset/Contents.json:1-29]()
- [HuggingSnap/Assets.xcassets/huggy.fill.symbolset/huggy.fill.svg:1-199]()

## Asset Integration with App Architecture

This diagram shows how assets integrate with the broader system architecture of HuggingSnap:

```mermaid
graph TD
    Assets["Assets & Resources"]
    UILayer["User Interface Layer"]
    MLLayer["Machine Learning Layer"]
    MediaLayer["Media Capture Layer"]
    
    Assets --> UILayer
    
    Assets --> AppIcon["App Icon"]
    Assets --> Colors["Color Assets (GYellow, Gold)"]
    Assets --> Symbols["Symbol Assets (huggy.fill)"]
    
    Colors --> ContentView["ContentView"]
    Colors --> ControlView["ControlView"]
    Symbols --> ControlView
    Symbols --> InputView["InputView"]
    
    UILayer --> ContentView
    UILayer --> ControlView
    UILayer --> MessageView["MessageView"]
    UILayer --> InputView
    UILayer --> SettingsView["SettingsView"]
    
    ContentView --> MLLayer
    ContentView --> MediaLayer
    
    MLLayer --> VLMEvaluator["VLMEvaluator"]
    MediaLayer --> CameraManager["CameraManager"]
```

This diagram illustrates how the assets primarily support the User Interface Layer, which in turn interacts with the Machine Learning and Media Capture components. Assets provide visual styling while the functional components handle the core application logic.

For more information about the UI components themselves, refer to [User Interface Components](#2.2). For details on the Machine Learning system, see [Machine Learning System](#2.1).

Sources:
- [HuggingSnap/Assets.xcassets/AppIcon.appiconset/Contents.json:1-36]()
- [HuggingSnap/Assets.xcassets/GYellow.colorset/Contents.json:1-29]()
- [HuggingSnap/Assets.xcassets/Gold.colorset/Contents.json:1-29]()
- [HuggingSnap/Assets.xcassets/huggy.fill.symbolset/huggy.fill.svg:1-199]()

---

