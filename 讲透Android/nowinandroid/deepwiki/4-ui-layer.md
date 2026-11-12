<!-- source: DeepWiki mcp.deepwiki.com · repo android/nowinandroid · page 4 UI Layer · fetched 2026-10-23 -->

# UI Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/src/main/kotlin/com/google/samples/apps/nowinandroid/ui/NiaApp.kt](app/src/main/kotlin/com/google/samples/apps/nowinandroid/ui/NiaApp.kt)
- [app/src/main/kotlin/com/google/samples/apps/nowinandroid/ui/NiaAppState.kt](app/src/main/kotlin/com/google/samples/apps/nowinandroid/ui/NiaAppState.kt)
- [app/src/testDemo/kotlin/com/google/samples/apps/nowinandroid/ui/NiaAppStateTest.kt](app/src/testDemo/kotlin/com/google/samples/apps/nowinandroid/ui/NiaAppStateTest.kt)
- [docs/ArchitectureLearningJourney.md](docs/ArchitectureLearningJourney.md)
- [docs/images/architecture-1-overall.png](docs/images/architecture-1-overall.png)
- [docs/images/architecture-2-example.png](docs/images/architecture-2-example.png)
- [docs/images/architecture-3-data-layer.png](docs/images/architecture-3-data-layer.png)
- [docs/images/architecture-4-ui-layer.png](docs/images/architecture-4-ui-layer.png)

</details>



## Purpose and Scope

The UI Layer encompasses the presentation components, navigation infrastructure, and state management patterns that render the Now in Android application. This includes the main application scaffolding, design system, reusable UI components, and feature screen compositions built with Jetpack Compose.

For information about individual feature module implementations and their ViewModels, see [Feature Modules](#6). For build-time UI configurations and Compose compiler settings, see [Convention Plugins](#3.2).

## Application Entry Point and Composition Root

The application UI initializes through a hierarchy: `MainActivity` → `NiaApp` composable → Feature screens.

### MainActivity

`MainActivity` serves as the Android `ComponentActivity` entry point and handles system-level UI concerns:

- **Edge-to-edge display**: Configures system bar styles based on theme using `enableEdgeToEdge()` [app/src/main/kotlin/com/google/samples/apps/nowinandroid/MainActivity.kt:115-124]().
- **Splash screen**: Keeps splash visible until `MainActivityViewModel` signals data is ready [app/src/main/kotlin/com/google/samples/apps/nowinandroid/MainActivity.kt:108-113]().
- **Theme initialization**: Observes user preferences and system dark mode to configure `NiaTheme` [app/src/main/kotlin/com/google/samples/apps/nowinandroid/MainActivity.kt:84-104]().
- **Dependency injection**: Provides `NetworkMonitor`, `TimeZoneMonitor`, `AnalyticsHelper`, and `UserNewsResourceRepository` via Hilt [app/src/main/kotlin/com/google/samples/apps/nowinandroid/MainActivity.kt:56-75]().
- **Performance monitoring**: Initializes `JankStats` for performance tracking [app/src/main/kotlin/com/google/samples/apps/nowinandroid/MainActivity.kt:159-167]().

```mermaid
graph TB
    MainActivity["MainActivity<br/>(ComponentActivity)"]
    MainActivityViewModel["MainActivityViewModel"]
    NiaTheme["NiaTheme<br/>(Composable)"]
    NiaApp["NiaApp<br/>(Composable)"]
    CompositionLocals["CompositionLocalProvider<br/>- LocalAnalyticsHelper<br/>- LocalTimeZone"]
    
    MainActivity -->|"viewModels()"| MainActivityViewModel
    MainActivity -->|"setContent"| CompositionLocals
    CompositionLocals --> NiaTheme
    NiaTheme --> NiaApp
    MainActivityViewModel -->|"uiState: StateFlow"| MainActivity
    
    MainActivity -.->|"@Inject"| NetworkMonitor
    MainActivity -.->|"@Inject"| TimeZoneMonitor
    MainActivity -.->|"@Inject"| AnalyticsHelper
    MainActivity -.->|"@Inject"| UserNewsResourceRepository
    
    NetworkMonitor[NetworkMonitor]
    TimeZoneMonitor[TimeZoneMonitor]
    AnalyticsHelper[AnalyticsHelper]
    UserNewsResourceRepository[UserNewsResourceRepository]
```

**Sources:** [app/src/main/kotlin/com/google/samples/apps/nowinandroid/MainActivity.kt:56-167]()

### NiaApp Composable

The `NiaApp` composable defines the application's visual structure and handles top-level UI orchestration:

- **Outer Layer**: Applies `NiaBackground` and conditional `NiaGradientBackground` based on the current navigation key [app/src/main/kotlin/com/google/samples/apps/nowinandroid/ui/NiaApp.kt:89-133]().
- **Inner Layer**: Uses `NiaNavigationSuiteScaffold` for adaptive navigation (bottom bar/rail/drawer) and `NavDisplay` to render the navigation stack [app/src/main/kotlin/com/google/samples/apps/nowinandroid/ui/NiaApp.kt:141-279]().

```mermaid
graph TB
    NiaApp_Outer["NiaApp (Outer)<br/>appState: NiaAppState"]
    NiaBackground["NiaBackground"]
    GradientBg["NiaGradientBackground"]
    SnackbarHost["SnackbarHostState"]
    LocalProvider["CompositionLocalProvider<br/>LocalSnackbarHostState"]
    
    NiaApp_Inner["NiaApp (Inner)"]
    NavSuite["NiaNavigationSuiteScaffold"]
    Scaffold["Scaffold"]
    TopAppBar["NiaTopAppBar"]
    NavDisplay["NavDisplay"]
    
    NiaApp_Outer --> NiaBackground
    NiaBackground --> GradientBg
    GradientBg --> SnackbarHost
    SnackbarHost --> LocalProvider
    LocalProvider --> NiaApp_Inner
    
    NiaApp_Inner --> NavSuite
    NavSuite --> Scaffold
    Scaffold --> TopAppBar
    Scaffold --> NavDisplay
    
    NavDisplay -->|"entries"| EntryProvider["entryProvider { }"]
    EntryProvider --> ForYouEntry["forYouEntry()"]
    EntryProvider --> BookmarksEntry["bookmarksEntry()"]
    EntryProvider --> InterestsEntry["interestsEntry()"]
    EntryProvider --> TopicEntry["topicEntry()"]
    EntryProvider --> SearchEntry["searchEntry()"]
```

**Sources:** [app/src/main/kotlin/com/google/samples/apps/nowinandroid/ui/NiaApp.kt:89-279]()

## State Management

### NiaAppState

`NiaAppState` is a `@Stable` class that manages app-level reactive state and navigation. It is created by `rememberNiaAppState()` [app/src/main/kotlin/com/google/samples/apps/nowinandroid/ui/NiaAppState.kt:42-67]().

| Property | Type | Purpose |
|----------|------|---------|
| `navigationState` | `NavigationState` | Current navigation stack and top-level destinations [app/src/main/kotlin/com/google/samples/apps/nowinandroid/ui/NiaAppState.kt:71]() |
| `isOffline` | `StateFlow<Boolean>` | Connectivity status derived from `NetworkMonitor` [app/src/main/kotlin/com/google/samples/apps/nowinandroid/ui/NiaAppState.kt:77-83]() |
| `topLevelNavKeysWithUnreadResources` | `StateFlow<Set<NavKey>>` | Tracks navigation items with unread content [app/src/main/kotlin/com/google/samples/apps/nowinandroid/ui/NiaAppState.kt:88-100]() |
| `currentTimeZone` | `StateFlow<TimeZone>` | Current device timezone from `TimeZoneMonitor` [app/src/main/kotlin/com/google/samples/apps/nowinandroid/ui/NiaAppState.kt:102-107]() |

```mermaid
graph LR
    subgraph "Data Sources"
        NetworkMonitor["NetworkMonitor<br/>.isOnline"]
        UserNewsRepo["UserNewsResourceRepository"]
        TimeZoneMonitor["TimeZoneMonitor<br/>.currentTimeZone"]
    end
    
    subgraph "NiaAppState"
        IsOffline["isOffline<br/>StateFlow&lt;Boolean&gt;"]
        UnreadKeys["topLevelNavKeysWithUnreadResources<br/>StateFlow&lt;Set&lt;NavKey&gt;&gt;"]
        CurrentTZ["currentTimeZone<br/>StateFlow&lt;TimeZone&gt;"]
        NavState["navigationState<br/>NavigationState"]
    end
    
    subgraph "UI Observation"
        NiaApp["NiaApp composable"]
        NavigationItems["Navigation items<br/>with badges"]
    end
    
    NetworkMonitor -->|"map(!it)"| IsOffline
    UserNewsRepo -->|"combine flows"| UnreadKeys
    TimeZoneMonitor --> CurrentTZ
    
    IsOffline -->|"collectAsStateWithLifecycle()"| NiaApp
    UnreadKeys -->|"collectAsStateWithLifecycle()"| NavigationItems
    CurrentTZ -->|"collectAsStateWithLifecycle()"| NiaApp
    NavState --> NiaApp
```

**Sources:** [app/src/main/kotlin/com/google/samples/apps/nowinandroid/ui/NiaAppState.kt:41-108]()

## Navigation System

Navigation uses the experimental Navigation3 library with a declarative `EntryProvider` pattern.

### Core Navigation Components

- **NavigationState**: Manages the navigation stack [app/src/main/kotlin/com/google/samples/apps/nowinandroid/ui/NiaAppState.kt:71]().
- **Navigator**: Provides navigation actions like `navigate` and `goBack` [app/src/testDemo/kotlin/com/google/samples/apps/nowinandroid/ui/NiaAppStateTest.kt:80]().
- **EntryProvider**: DSL for declaring navigation entries aggregated in `NiaApp` [app/src/main/kotlin/com/google/samples/apps/nowinandroid/ui/NiaApp.kt:259-265]().

### Navigation Architecture

```mermaid
graph TB
    subgraph "Navigation State"
        NavState["NavigationState"]
        TopLevelStack["topLevelStack: NavBackStack"]
        SubStacks["subStacks: Map&lt;NavKey, NavBackStack&gt;"]
        CurrentKey["currentKey: NavKey"]
    end
    
    subgraph "Navigation Actions"
        Navigator["Navigator"]
        Navigate["navigate(NavKey)"]
        GoBack["goBack()"]
    end
    
    subgraph "Feature API Modules"
        ForYouNavKey["ForYouNavKey"]
        BookmarksNavKey["BookmarksNavKey"]
        InterestsNavKey["InterestsNavKey"]
        TopicNavKey["TopicNavKey(id: String)"]
        SearchNavKey["SearchNavKey"]
    end
    
    subgraph "Feature Impl Modules"
        ForYouEntry["forYouEntry(navigator)"]
        BookmarksEntry["bookmarksEntry(navigator)"]
        InterestsEntry["interestsEntry(navigator)"]
        TopicEntry["topicEntry(navigator)"]
        SearchEntry["searchEntry(navigator)"]
    end
    
    NavState --> TopLevelStack
    NavState --> SubStacks
    NavState --> CurrentKey
    
    Navigator -->|"modifies"| NavState
    Navigator --> Navigate
    Navigator --> GoBack
    
    Navigate -->|"accepts"| ForYouNavKey
    Navigate -->|"accepts"| BookmarksNavKey
    Navigate -->|"accepts"| TopicNavKey
    
    ForYouNavKey -.->|"entry&lt;ForYouNavKey&gt;"| ForYouEntry
    BookmarksNavKey -.->|"entry&lt;BookmarksNavKey&gt;"| BookmarksEntry
    TopicNavKey -.->|"entry&lt;TopicNavKey&gt;"| TopicEntry
```

**Sources:** [app/src/main/kotlin/com/google/samples/apps/nowinandroid/ui/NiaApp.kt:257-271](), [app/src/main/kotlin/com/google/samples/apps/nowinandroid/ui/NiaAppState.kt:27-28]()

For details on adaptive navigation and list-detail patterns, see [Navigation and Adaptive UI](#4.2).

## Design System

The design system provides the Material 3 theme and primitive components.

### NiaTheme

`NiaTheme` determines the color scheme, typography, and shapes. It supports dark mode, dynamic color (Material You), and custom gradient backgrounds [app/src/main/kotlin/com/google/samples/apps/nowinandroid/ui/NiaApp.kt:99-105]().

```mermaid
graph TB
    UserDataRepository["UserDataRepository<br/>(UserPreferences)"]
    MainActivityViewModel["MainActivityViewModel"]
    MainActivity["MainActivity"]
    NiaTheme["NiaTheme"]
    
    subgraph "Theme Parameters"
        DarkTheme["darkTheme: Boolean"]
        AndroidTheme["androidTheme: Boolean"]
        DisableDynamic["disableDynamicTheming: Boolean"]
    end
    
    subgraph "Material 3 Theme"
        ColorScheme["ColorScheme<br/>(light/dark/dynamic)"]
        Typography["Typography"]
        Shapes["Shapes"]
    end
    
    subgraph "Custom Theme Elements"
        GradientColors["GradientColors<br/>LocalGradientColors"]
        TintTheme["TintTheme"]
    end
    
    UserDataRepository -->|"themeBrand, darkThemeConfig"| MainActivityViewModel
    MainActivityViewModel -->|"uiState.shouldUseDarkTheme()"| MainActivity
    MainActivity --> DarkTheme
    MainActivity --> AndroidTheme
    MainActivity --> DisableDynamic
    
    DarkTheme --> NiaTheme
    AndroidTheme --> NiaTheme
    DisableDynamic --> NiaTheme
    
    NiaTheme --> ColorScheme
    NiaTheme --> Typography
    NiaTheme --> Shapes
    NiaTheme --> GradientColors
    NiaTheme --> TintTheme
```

For details, see [Design System](#4.3).

## Core UI Components

The `core:ui` module provides reusable components like `NewsResourceCard` used across multiple features [docs/ArchitectureLearningJourney.md:157]().

| Component | Purpose |
|-----------|---------|
| `NiaTopAppBar` | Top app bar with actions [app/src/main/kotlin/com/google/samples/apps/nowinandroid/ui/NiaApp.kt:230](). |
| `NiaNavigationSuiteScaffold` | Adaptive navigation container [app/src/main/kotlin/com/google/samples/apps/nowinandroid/ui/NiaApp.kt:162](). |
| `NiaBackground` | Primary app background [app/src/main/kotlin/com/google/samples/apps/nowinandroid/ui/NiaApp.kt:98](). |

For a full catalog, see [Core UI Components](#4.4).

## Child Pages

- [Application Structure](#4.1) — MainActivity, NiaApp, and app-level state management.
- [Navigation and Adaptive UI](#4.2) — Navigation3 system and responsive layouts.
- [Design System](#4.3) — NiaTheme, Material 3, and dynamic color.
- [Core UI Components](#4.4) — Reusable composables and the component catalog.

---

