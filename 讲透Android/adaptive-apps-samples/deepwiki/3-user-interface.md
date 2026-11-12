<!-- source: DeepWiki mcp.deepwiki.com · repo android/adaptive-apps-samples · page 3 User Interface · fetched 2026-10-23 -->

# User Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [AdaptiveJetStream/README.md](AdaptiveJetStream/README.md)
- [AdaptiveJetStream/jetstream/src/main/ic_launcher-playstore.png](AdaptiveJetStream/jetstream/src/main/ic_launcher-playstore.png)
- [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/MainActivity.kt](AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/MainActivity.kt)

</details>



This document describes the adaptive user interface framework used in AdaptiveJetStream. The UI system is designed to provide consistent media streaming experiences across multiple form factors including mobile, tablet, foldable, TV, automotive, Chromebook, and XR devices using a single codebase.

For information about the application's overall architecture and component structure, see [Architecture](#2). For details about media playback integration with the UI, see [Media Playback System](#2.2).

## Adaptive UI Framework

AdaptiveJetStream implements a comprehensive adaptive UI system that automatically adjusts layouts, navigation patterns, and interaction models based on the target device's form factor and capabilities.

```mermaid
graph TD
    subgraph "Form Factor Detection"
        CONFIG["Configuration.resources"]
        UIMODE["UiMode.from()"]
        WINDOWSIZE["Window Size Classes"]
        FEATURES["System Features"]
    end
    
    subgraph "Adaptive UI Engine"
        MATERIAL3["Material3 Adaptive"]
        COMPOSE["Compose Adaptive"]
        XR_OVERRIDES["XR Component Overrides"]
    end
    
    subgraph "Platform Experiences"
        MOBILE["Mobile UI"]
        TABLET["Tablet UI"] 
        FOLDABLE["Foldable UI"]
        TV["TV/Leanback UI"]
        AUTO["Automotive UI"]
        CHROMEBOOK["Chromebook UI"]
        XR["XR/Spatial UI"]
    end
    
    CONFIG --> UIMODE
    UIMODE --> MATERIAL3
    WINDOWSIZE --> MATERIAL3
    FEATURES --> XR_OVERRIDES
    
    MATERIAL3 --> COMPOSE
    XR_OVERRIDES --> COMPOSE
    
    COMPOSE --> MOBILE
    COMPOSE --> TABLET
    COMPOSE --> FOLDABLE
    COMPOSE --> TV
    COMPOSE --> AUTO
    COMPOSE --> CHROMEBOOK
    COMPOSE --> XR
```

The adaptive framework operates through several key detection mechanisms that determine the appropriate UI layout and interaction patterns for each device type.

Sources: [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/MainActivity.kt:106-117](), [AdaptiveJetStream/README.md:3-11]()

## Main UI Entry Points

The application's UI hierarchy starts with `MainActivity` as the Android entry point, which sets up the Compose environment and delegates to the main `App` composable.

```mermaid
graph TD
    subgraph "Activity Layer"
        MAINACTIVITY["MainActivity"]
        SPLASHSCREEN["SplashScreen.installSplashScreen()"]
        EDGETOEDGE["enableEdgeToEdge()"]
        CUSTOMHEADER["tryEnableCustomHeader()"]
    end
    
    subgraph "Compose Layer"
        SETCONTENT["setContent{}"]
        JETSTREAMTHEME["JetStreamTheme"]
        COMPOSITIONLOCAL["CompositionLocalProvider"]
        SURFACE["Surface"]
    end
    
    subgraph "XR Integration"
        ENABLEXR["EnableXrComponentOverrides"]
        MATERIAL3XR["@OptIn(ExperimentalMaterial3XrApi)"]
    end
    
    subgraph "Main App"
        APP["App()"]
        SAFEDRAWING["safeDrawingPadding()"]
        BACKGROUND["background()"]
    end
    
    MAINACTIVITY --> SPLASHSCREEN
    MAINACTIVITY --> EDGETOEDGE
    MAINACTIVITY --> CUSTOMHEADER
    MAINACTIVITY --> SETCONTENT
    
    SETCONTENT --> JETSTREAMTHEME
    JETSTREAMTHEME --> COMPOSITIONLOCAL
    COMPOSITIONLOCAL --> ENABLEXR
    ENABLEXR --> SURFACE
    SURFACE --> APP
    
    MATERIAL3XR --> ENABLEXR
    
    APP --> SAFEDRAWING
    APP --> BACKGROUND
```

The `MainActivity` class handles platform-specific setup including splash screen installation, edge-to-edge display configuration, and custom header support for windowed environments.

Sources: [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/MainActivity.kt:49-82]()

## Form Factor Detection and Adaptation

The UI system uses multiple detection mechanisms to identify the current device context and adapt the interface accordingly.

| Detection Method | Purpose | Implementation |
|-----------------|---------|----------------|
| `UiMode.from(resources.configuration)` | Detect basic form factor category | [MainActivity.kt:107]() |
| Window Size Classes | Determine layout breakpoints | Material3 Adaptive |
| System Features | Detect capabilities like PiP, freeform windows | [MainActivity.kt:110-116]() |
| XR Environment | Enable spatial UI components | `EnableXrComponentOverrides` |

```mermaid
graph LR
    subgraph "Detection Layer"
        RESOURCES["resources.configuration"]
        PACKAGEMGR["PackageManager"]
        WINDOWMETRICS["WindowMetrics"]
    end
    
    subgraph "Adaptation Logic"
        UIMODE_DETECTION["UiMode.from()"]
        FEATURE_CHECK["hasSystemFeature()"]
        WINDOWCLASS["WindowSizeClass"]
    end
    
    subgraph "UI Variants"
        MOBILE_UI["Mobile Layout"]
        TABLET_UI["Tablet Layout"]
        TV_UI["TV Layout"]
        XR_UI["XR Layout"]
        FOLDABLE_UI["Foldable Layout"]
        AUTO_UI["Auto Layout"]
        CHROMEBOOK_UI["Chromebook Layout"]
    end
    
    RESOURCES --> UIMODE_DETECTION
    PACKAGEMGR --> FEATURE_CHECK
    WINDOWMETRICS --> WINDOWCLASS
    
    UIMODE_DETECTION --> MOBILE_UI
    UIMODE_DETECTION --> TABLET_UI
    UIMODE_DETECTION --> TV_UI
    FEATURE_CHECK --> XR_UI
    WINDOWCLASS --> FOLDABLE_UI
    FEATURE_CHECK --> AUTO_UI
    WINDOWCLASS --> CHROMEBOOK_UI
```

Sources: [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/MainActivity.kt:106-117](), [AdaptiveJetStream/README.md:5-11]()

## Material3 and Theming Integration

The application uses Material Design 3 components with adaptive capabilities to ensure consistent theming across all form factors while allowing for platform-specific customizations.

```mermaid
graph TD
    subgraph "Theme Layer"
        JETSTREAMTHEME["JetStreamTheme"]
        MATERIALTHEME["MaterialTheme"]
        COLORSCHEME["MaterialTheme.colorScheme"]
        TONALELEVATION["LocalAbsoluteTonalElevation"]
    end
    
    subgraph "Composition Locals"
        CONTENTCOLOR["LocalContentColor"]
        SURFACECOLOR["surfaceColorAtElevation()"]
        COMPOSITIONPROVIDER["CompositionLocalProvider"]
    end
    
    subgraph "Surface System"
        SURFACE["Surface{}"]
        BACKGROUND["background()"]
        SAFEDRAWING["safeDrawingPadding()"]
    end
    
    JETSTREAMTHEME --> MATERIALTHEME
    MATERIALTHEME --> COLORSCHEME
    MATERIALTHEME --> TONALELEVATION
    
    COLORSCHEME --> CONTENTCOLOR
    TONALELEVATION --> SURFACECOLOR
    CONTENTCOLOR --> COMPOSITIONPROVIDER
    
    COMPOSITIONPROVIDER --> SURFACE
    SURFACE --> BACKGROUND
    SURFACE --> SAFEDRAWING
```

The theming system provides consistent color schemes, typography, and spacing while adapting to different display densities and form factors.

Sources: [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/MainActivity.kt:60-80]()

## XR and Spatial UI Support

AdaptiveJetStream includes experimental support for XR devices through Material3's XR extensions, enabling spatial user interfaces for AR/VR experiences.

```mermaid
graph TD
    subgraph "XR Setup"
        EXPERIMENTAL["@OptIn(ExperimentalMaterial3XrApi)"]
        ENABLEXR["EnableXrComponentOverrides"]
        XR_MATERIAL3["androidx.xr.compose.material3"]
    end
    
    subgraph "XR Components"
        SPATIAL_UI["Spatial UI Components"]
        XR_NAVIGATION["XR Navigation"]
        DEPTH_LAYOUT["Depth-based Layouts"]
    end
    
    subgraph "Fallback System"
        STANDARD_UI["Standard UI Components"]
        CONDITIONAL["Conditional Rendering"]
        PLATFORM_CHECK["Platform Detection"]
    end
    
    EXPERIMENTAL --> ENABLEXR
    ENABLEXR --> XR_MATERIAL3
    XR_MATERIAL3 --> SPATIAL_UI
    SPATIAL_UI --> XR_NAVIGATION
    SPATIAL_UI --> DEPTH_LAYOUT
    
    PLATFORM_CHECK --> CONDITIONAL
    CONDITIONAL --> SPATIAL_UI
    CONDITIONAL --> STANDARD_UI
```

XR support is implemented through component overrides that replace standard Material3 components with spatial equivalents when running in XR environments.

Sources: [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/MainActivity.kt:42-43](), [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/MainActivity.kt:52](), [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/MainActivity.kt:64]()

## Input Handling and Keyboard Shortcuts

The application provides comprehensive input handling including keyboard shortcuts for efficient navigation and media control across different input modalities.

| Category | Function | Key Combination |
|----------|----------|----------------|
| General | Close Dialog | `Escape` |
| General | Scroll Down/Up | `Page Down`/`Page Up` |
| General | Show Profile | `Ctrl+,` or `Ctrl+Alt+P` |
| General | Show Home | `Ctrl+Alt+H` |
| General | Show Search | `/` or `Ctrl+Alt+S` |
| Video | Toggle Play/Pause | `K` |
| Video | Rewind 10 seconds | `J` |
| Video | Skip 10 seconds | `L` |
| Video | Toggle Fullscreen | `F` |
| Spatial | Pan Controls | `W`,`A`,`S`,`D` |
| Spatial | Zoom Controls | `+`/`-`, `[`/`]` |

```mermaid
graph TD
    subgraph "Input Categories"
        GENERAL["General Navigation"]
        VIDEO["Video Playback"]
        SPATIAL["Spatial/XR Controls"]
    end
    
    subgraph "Keyboard Handling"
        SHORTCUTS["KeyboardShortcutGroup"]
        SHORTCUTINFO["KeyboardShortcutInfo"]
        ONPROVIDE["onProvideKeyboardShortcuts()"]
    end
    
    subgraph "Action Routing"
        NAVIGATION_ACTIONS["Navigation Actions"]
        MEDIA_ACTIONS["Media Control Actions"]
        SPATIAL_ACTIONS["Spatial Control Actions"]
    end
    
    GENERAL --> SHORTCUTS
    VIDEO --> SHORTCUTS
    SPATIAL --> SHORTCUTS
    
    SHORTCUTS --> SHORTCUTINFO
    SHORTCUTINFO --> ONPROVIDE
    
    ONPROVIDE --> NAVIGATION_ACTIONS
    ONPROVIDE --> MEDIA_ACTIONS
    ONPROVIDE --> SPATIAL_ACTIONS
```

The keyboard shortcut system is organized into logical groups and provides discoverable shortcuts through the Android system's shortcut display mechanism.

Sources: [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/MainActivity.kt:84-90](), [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/MainActivity.kt:119-263]()

## Window Management and Display Features

The UI system includes advanced window management capabilities for modern Android form factors including foldables, large screens, and windowed environments.

```mermaid
graph TD
    subgraph "Window Features"
        EDGETOEDGE["enableEdgeToEdge()"]
        CUSTOMHEADER["Custom Header Support"]
        SAFEDRAWING["safeDrawingPadding()"]
        WINDOWINSETS["WindowInsetsController"]
    end
    
    subgraph "Feature Detection"
        FREEFORM["FEATURE_FREEFORM_WINDOW_MANAGEMENT"]
        PIP["FEATURE_PICTURE_IN_PICTURE"]
        PACKAGEMGR_CHECK["packageManager.hasSystemFeature()"]
    end
    
    subgraph "Display Adaptations"
        TRANSPARENT_CAPTION["APPEARANCE_TRANSPARENT_CAPTION_BAR_BACKGROUND"]
        SYSTEM_BARS["System Bars Appearance"]
        INSETS_HANDLING["Window Insets Handling"]
    end
    
    EDGETOEDGE --> SAFEDRAWING
    CUSTOMHEADER --> WINDOWINSETS
    WINDOWINSETS --> TRANSPARENT_CAPTION
    
    FREEFORM --> PACKAGEMGR_CHECK
    PIP --> PACKAGEMGR_CHECK
    PACKAGEMGR_CHECK --> CUSTOMHEADER
    
    TRANSPARENT_CAPTION --> SYSTEM_BARS
    SYSTEM_BARS --> INSETS_HANDLING
```

Advanced window management features are conditionally enabled based on system capabilities, ensuring optimal experiences on devices that support features like freeform windows and picture-in-picture mode.

Sources: [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/MainActivity.kt:57-58](), [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/MainActivity.kt:92-117]()

---

