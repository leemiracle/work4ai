<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/OLMoE.swift · page 7 UI Components · fetched 2026-10-26 -->

# UI Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [OLMoE.swift/Assets.xcassets/DownloadIcon.imageset/Contents.json](OLMoE.swift/Assets.xcassets/DownloadIcon.imageset/Contents.json)
- [OLMoE.swift/Assets.xcassets/DownloadIcon.imageset/DownloadIcon.svg](OLMoE.swift/Assets.xcassets/DownloadIcon.imageset/DownloadIcon.svg)
- [OLMoE.swift/Assets.xcassets/MacIconColor.colorset/Contents.json](OLMoE.swift/Assets.xcassets/MacIconColor.colorset/Contents.json)
- [OLMoE.swift/Styles/ButtonStyles.swift](OLMoE.swift/Styles/ButtonStyles.swift)
- [OLMoE.swift/Styles/Typography.swift](OLMoE.swift/Styles/Typography.swift)
- [OLMoE.swift/Views/InfoPageView.swift](OLMoE.swift/Views/InfoPageView.swift)
- [OLMoE.swift/Views/ToolbarButton.swift](OLMoE.swift/Views/ToolbarButton.swift)

</details>



This page documents the reusable UI components used throughout the OLMoE.swift application. It covers the styling system, button variants, and specialized components that help maintain a consistent look and feel across the app. For information about the overall user interface flow and navigation, see [User Interface Flow](#3.2).

## Typography System

OLMoE.swift implements a consistent typography system through font extensions that provide standardized text styles throughout the application.

```mermaid
classDiagram
    class "Font" {
        +static title(weight: Font.Weight) Font
        +static body(weight: Font.Weight) Font
        +static subheader() Font
    }
    note for "Font" "Extension that provides\nstandardized type styles"
```

The typography system defines three main text styles:
- `title`: Used for headings, renders in Telegraf font at 24pt
- `body`: Main text style, renders in Manrope font at 17pt
- `subheader`: Bold variant of body text, uses Manrope Bold at 17pt

Sources: [OLMoE.swift/Styles/Typography.swift:11-23]()

## Button Components

OLMoE.swift includes several button variants that provide consistent interaction patterns throughout the application.

### Primary and Secondary Buttons

```mermaid
classDiagram
    class "ButtonStyle" {
        <<Protocol>>
    }
    class "PrimaryButton" {
        +minWidth: CGFloat?
        +makeBody(configuration) View
    }
    class "SecondaryButton" {
        +minWidth: CGFloat?
        +makeBody(configuration) View
    }
    "ButtonStyle" <|-- "PrimaryButton"
    "ButtonStyle" <|-- "SecondaryButton"
    note for "PrimaryButton" "Green filled button\nwith rounded corners"
    note for "SecondaryButton" "Outline button with\naccent color text"
```

The button system provides two main styles:
- `PrimaryButton`: Green background with rounded corners, used for primary actions
- `SecondaryButton`: Background-colored button with accent text, used for secondary actions

Both button types accept an optional `minWidth` parameter and are implemented as SwiftUI `ButtonStyle` conforming types, which can be applied using the `.buttonStyle()` modifier.

Sources: [OLMoE.swift/Styles/ButtonStyles.swift:11-56]()

### Toolbar Buttons

The `ToolbarButton` component provides a consistent way to create icon-based buttons used in toolbars and navigation areas.

```mermaid
classDiagram
    class "ToolbarButton" {
        +action: () -> Void
        +systemName: String?
        +assetName: String?
        +foregroundColor: Color?
        -isHovering: Bool
    }
    note for "ToolbarButton" "Icon button with hover\neffects on macCatalyst"
```

`ToolbarButton` supports:
- System icons (SF Symbols)
- Custom asset images
- Custom foreground colors
- Platform-specific styling for iOS/iPadOS and macCatalyst
- Hover effects on macCatalyst

The component adapts to macCatalyst by showing a hover effect and using a different foreground color.

Sources: [OLMoE.swift/Views/ToolbarButton.swift:10-60]()

## Specialized UI Components

### Info and Close Buttons

```mermaid
classDiagram
    class "InfoButton" {
        +action: () -> Void
    }
    class "CloseButton" {
        +action: () -> Void
    }
    class "ToolbarButton" {
        +action: () -> Void
        +systemName: String?
        +assetName: String?
    }
    "InfoButton" --> "ToolbarButton" : uses
    note for "InfoButton" "Information icon button\nthat uses ToolbarButton"
    note for "CloseButton" "X-shaped close button\nused in modal views"
```

The application includes specialized button variants:
- `InfoButton`: An information icon button built with `ToolbarButton`
- `CloseButton`: A close (X) button used for dismissing modals and sheets

Sources: [OLMoE.swift/Views/InfoPageView.swift:11-32]()

### Info View Components

The app includes an information view system composed of several nested components:

```mermaid
component
    subgraph "InfoView Components"
        direction TB
        "InfoView" --> "InfoContent"
        "InfoView" --> "CloseButton"
        "InfoView" --> "Ai2LogoView"
        "InfoContent" --> "HeaderTextPairView"
    end
```

The information view system consists of:
- `InfoView`: The main container view that displays information about the application
- `InfoContent`: A component that renders a collection of text sections
- `HeaderTextPairView`: A reusable component for displaying a header-text pair
- `CloseButton`: Button for dismissing the info view

The `InfoView` adapts its layout based on the platform, with slightly different structure for macCatalyst vs iOS/iPadOS.

Sources: [OLMoE.swift/Views/InfoPageView.swift:34-90]()

## UI Asset Integration

OLMoE.swift uses a combination of system icons (SF Symbols) and custom assets to provide a consistent visual language.

```mermaid
flowchart TD
    subgraph "UI Assets"
        direction LR
        "Custom Assets" --> "Icons"
        "Custom Assets" --> "Colors"
        "System Icons" --> "SF Symbols"
    end
    
    subgraph "Usage in Components"
        direction LR
        "ToolbarButton" --> "Icons"
        "ToolbarButton" --> "SF Symbols"
        "PrimaryButton" --> "Colors"
        "SecondaryButton" --> "Colors"
    end
```

Key assets include:
- Icons like `DownloadIcon` used in UI components
- Custom colors like `MacIconColor` for platform-specific styling
- SF Symbols for standard system iconography

Sources: 
- [OLMoE.swift/Assets.xcassets/DownloadIcon.imageset/DownloadIcon.svg:1-14]()
- [OLMoE.swift/Assets.xcassets/MacIconColor.colorset/Contents.json:1-21]()

## UI Component Relationships

The following diagram shows how the various UI components relate to each other within the application architecture:

```mermaid
graph TD
    subgraph "View Hierarchy"
        "ContentView" --> "ChatView"
        "ContentView" --> "ModelDownloadView"
        "ContentView" --> "DisclaimerPageView"
        "ContentView" --> "InfoView"
        "ContentView" --> "UnsupportedDeviceView"
    end
    
    subgraph "UI Components"
        "ToolbarButton" 
        "InfoButton"
        "CloseButton"
        "PrimaryButton"
        "SecondaryButton"
    end
    
    subgraph "Styling"
        "Typography" --> "Font Extensions"
        "ButtonStyles" --> "PrimaryButton"
        "ButtonStyles" --> "SecondaryButton"
    end
    
    "ChatView" --> "UI Components"
    "ModelDownloadView" --> "UI Components"
    "DisclaimerPageView" --> "UI Components"
    "InfoView" --> "UI Components"
    "UnsupportedDeviceView" --> "UI Components"
    
    "UI Components" --> "Styling"
```

This illustrates how the reusable UI components fit into the larger application structure, providing consistent interface elements across different views.

Sources:
- [OLMoE.swift/Views/InfoPageView.swift:11-90]()
- [OLMoE.swift/Views/ToolbarButton.swift:10-60]()
- [OLMoE.swift/Styles/ButtonStyles.swift:11-56]()
- [OLMoE.swift/Styles/Typography.swift:11-23]()

---

