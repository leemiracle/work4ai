<!-- source: DeepWiki mcp.deepwiki.com · repo android/nav3-recipes · page 6 Custom Scenes and Adaptive Layouts · fetched 2026-10-23 -->

# Custom Scenes and Adaptive Layouts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/src/main/java/com/example/nav3recipes/scenes/listdetail/Content.kt](app/src/main/java/com/example/nav3recipes/scenes/listdetail/Content.kt)
- [app/src/main/java/com/example/nav3recipes/scenes/listdetail/ListDetailActivity.kt](app/src/main/java/com/example/nav3recipes/scenes/listdetail/ListDetailActivity.kt)
- [app/src/main/java/com/example/nav3recipes/scenes/listdetail/ListDetailScene.kt](app/src/main/java/com/example/nav3recipes/scenes/listdetail/ListDetailScene.kt)
- [app/src/main/java/com/example/nav3recipes/scenes/twopane/TwoPaneActivity.kt](app/src/main/java/com/example/nav3recipes/scenes/twopane/TwoPaneActivity.kt)
- [app/src/main/java/com/example/nav3recipes/scenes/twopane/TwoPaneScene.kt](app/src/main/java/com/example/nav3recipes/scenes/twopane/TwoPaneScene.kt)

</details>



## Purpose and Scope

This document covers the Scene system in Navigation 3, which enables adaptive multi-pane layouts that respond to device characteristics. The Scene system allows multiple `NavEntry` objects to be rendered simultaneously in a single composition, creating list-detail layouts, two-pane views, and other responsive patterns.

This page provides an architectural overview of how scenes work. For implementation details of specific scene patterns, see:
- [Scene System Overview](#6.1) - Core concepts and the `SceneStrategy` interface
- [Two-Pane Scene Implementation](#6.2) - 50/50 split-pane pattern
- [List-Detail Scene Implementation](#6.3) - 40/60 list-detail pattern with animations
- [Dialog and BottomSheet Scenes](#6.4) - Overlay-based scene patterns
- [Material3 Adaptive Layouts](#6.5) - Production-ready Material3 adaptive components

## Scene System Architecture

The Scene system extends Navigation 3's single-entry model to support multi-pane layouts through a metadata-driven architecture. When a `SceneStrategy` is provided to `NavDisplay`, it can intercept the back stack rendering to compose multiple entries together.

### Core Components

```mermaid
graph TB
    subgraph "Navigation State"
        NBS["NavBackStack<T>"]
        NE1["NavEntry<T> 1"]
        NE2["NavEntry<T> 2"]
        NE3["NavEntry<T> 3"]
    end
    
    subgraph "Scene Decision Layer"
        ND["NavDisplay"]
        SS["SceneStrategy<T>"]
        SSS["SceneStrategyScope"]
        WS["WindowSizeClass"]
        MD["Entry Metadata"]
    end
    
    subgraph "Scene Rendering"
        SC["Scene<T>"]
        PE["previousEntries: List"]
        EN["entries: List"]
        CNT["content: @Composable"]
    end
    
    subgraph "Single Entry Fallback"
        SE["Single Entry Render"]
    end
    
    NBS -->|"provides entries"| ND
    ND -->|"consults"| SS
    WS -->|"input"| SS
    MD -->|"input"| SS
    SS -->|"evaluates in"| SSS
    SSS -->|"returns Scene? or null"| SC
    SSS -->|"returns null"| SE
    
    NE1 -->|"metadata.containsKey()"| MD
    NE2 -->|"metadata.containsKey()"| MD
    NE3 -->|"metadata.containsKey()"| MD
    
    SC -->|"has"| PE
    SC -->|"has"| EN
    SC -->|"has"| CNT
    
    EN -->|"renders"| NE1
    EN -->|"renders"| NE2
```

**Sources:** [app/src/main/java/com/example/nav3recipes/scenes/listdetail/ListDetailScene.kt:32-51](), [app/src/main/java/com/example/nav3recipes/scenes/twopane/TwoPaneScene.kt:10-48]()

### Scene Resolution Flow

The scene resolution process determines whether to render a multi-entry scene or fall back to single-entry rendering:

```mermaid
sequenceDiagram
    participant ND as NavDisplay
    participant SS as SceneStrategy
    participant WS as WindowSizeClass
    participant NBS as NavBackStack
    participant SC as Scene or null
    
    ND->>NBS: Get current entries
    ND->>WS: Query window characteristics
    ND->>SS: calculateScene(entries)
    SS->>NBS: Examine last N entries
    SS->>NBS: Check metadata keys
    SS->>WS: Check width breakpoint
    alt Scene conditions met
        SS->>SC: Create Scene instance
        SC->>ND: Return Scene
        ND->>SC: Render scene.content
    else Scene conditions not met
        SS->>ND: Return null
        ND->>ND: Render single entry
    end
```

**Sources:** [app/src/main/java/com/example/nav3recipes/scenes/listdetail/ListDetailScene.kt:113-147](), [app/src/main/java/com/example/nav3recipes/scenes/twopane/TwoPaneScene.kt:60-107]()

## Metadata-Based Pane Assignment

Entries declare their eligibility for pane display through metadata maps attached during entry provider configuration. The metadata keys serve as markers that `SceneStrategy` implementations query to determine scene composition.

### Metadata Pattern

| Scene Type | Metadata Function | Metadata Key | Usage |
|------------|------------------|--------------|-------|
| `TwoPaneScene` | `TwoPaneScene.twoPane()` | `"TwoPane"` | Both entries must have this key |
| `ListDetailScene` | `ListDetailScene.listPane()` | `"ListDetailScene-List"` | List entry requirement |
| `ListDetailScene` | `ListDetailScene.detailPane()` | `"ListDetailScene-Detail"` | Detail entry requirement |

**Sources:** [app/src/main/java/com/example/nav3recipes/scenes/twopane/TwoPaneScene.kt:40-47](), [app/src/main/java/com/example/nav3recipes/scenes/listdetail/ListDetailScene.kt:78-93]()

### Entry Provider Configuration

```mermaid
graph LR
    subgraph "Entry Provider DSL"
        EP["entryProvider { }"]
        E1["entry<Home>"]
        E2["entry<Product>"]
        E3["entry<Profile>"]
    end
    
    subgraph "Metadata Declaration"
        M1["metadata = twoPane()"]
        M2["metadata = listPane()"]
        M3["metadata = detailPane()"]
        M4["metadata = null"]
    end
    
    subgraph "Scene Strategy Matching"
        SS["SceneStrategy"]
        CHK1["entries.all { twoPane }"]
        CHK2["entries.findLast { listPane }"]
        CHK3["entries.lastOrNull { detailPane }"]
    end
    
    E1 -->|"declares"| M1
    E2 -->|"declares"| M2
    E2 -->|"or declares"| M3
    E3 -->|"declares"| M4
    
    M1 --> CHK1
    M2 --> CHK2
    M3 --> CHK3
    
    CHK1 --> SS
    CHK2 --> SS
    CHK3 --> SS
```

**Sources:** [app/src/main/java/com/example/nav3recipes/scenes/twopane/TwoPaneActivity.kt:63-97](), [app/src/main/java/com/example/nav3recipes/scenes/listdetail/ListDetailActivity.kt:75-97]()

## Window Size Evaluation

Scene strategies evaluate `WindowSizeClass` to determine device characteristics and apply responsive layout rules. The `isWidthAtLeastBreakpoint()` extension function checks width thresholds.

### Width Breakpoint Constants

| Constant | Value | Typical Device |
|----------|-------|---------------|
| `WIDTH_DP_MEDIUM_LOWER_BOUND` | 600dp | Tablets, large phones in landscape |
| Compact (implicit) | < 600dp | Phones in portrait |

**Sources:** [app/src/main/java/com/example/nav3recipes/scenes/twopane/TwoPaneScene.kt:50-57](), [app/src/main/java/com/example/nav3recipes/scenes/listdetail/ListDetailScene.kt:103-110]()

### Window Size Query Pattern

```mermaid
graph TB
    subgraph "Composition Context"
        CMP["@Composable"]
        AWI["currentWindowAdaptiveInfo()"]
        WSC["windowSizeClass"]
    end
    
    subgraph "SceneStrategy Creation"
        REM["remember(windowSizeClass)"]
        STRAT["SceneStrategy instance"]
    end
    
    subgraph "Strategy Logic"
        CHK["isWidthAtLeastBreakpoint()"]
        RET1["Return Scene"]
        RET2["Return null"]
    end
    
    CMP --> AWI
    AWI --> WSC
    WSC --> REM
    REM --> STRAT
    STRAT --> CHK
    CHK -->|"true"| RET1
    CHK -->|"false"| RET2
```

**Sources:** [app/src/main/java/com/example/nav3recipes/scenes/twopane/TwoPaneScene.kt:50-57](), [app/src/main/java/com/example/nav3recipes/scenes/listdetail/ListDetailScene.kt:103-110]()

## Scene Key Design

Each `Scene` instance has a unique `key` that identifies its state. The scene key determines when `NavDisplay` performs scene transitions. When the scene key changes, the entire scene animates out and the new scene animates in. When the scene key remains stable, the scene handles internal state changes without triggering `NavDisplay` transitions.

### Scene Key Strategies

| Scene Type | Key Composition | Purpose |
|------------|----------------|---------|
| `TwoPaneScene` | `Pair(firstEntry.contentKey, secondEntry.contentKey)` | New scene when either entry changes |
| `ListDetailScene` | `listEntry.contentKey` | Stable key allows scene to animate detail changes |

The `ListDetailScene` uses the list entry's content key as the scene key. This design allows the detail pane to change without triggering a scene transition, enabling the scene's internal `AnimatedContent` to handle detail animations smoothly.

**Sources:** [app/src/main/java/com/example/nav3recipes/scenes/twopane/TwoPaneScene.kt:85-88](), [app/src/main/java/com/example/nav3recipes/scenes/listdetail/ListDetailScene.kt:135-145]()

## Previous Entries and Back Navigation

The `previousEntries` property on a `Scene` defines what remains in the back stack when the user navigates back from a scene. This is a UX decision that the scene strategy controls.

### Back Stack Manipulation

```mermaid
graph TB
    subgraph "Current BackStack State"
        BS["[Home, Product1, Product2]"]
    end
    
    subgraph "TwoPaneScene Decision"
        TPS["TwoPaneScene displays<br/>Product1 and Product2"]
        PE1["previousEntries = entries.dropLast(1)"]
        PE1_VAL["[Home, Product1]"]
    end
    
    subgraph "Back Navigation Result"
        BACK["User presses back"]
        NEW_BS["[Home, Product1]"]
        RENDER["Renders Product1 only"]
    end
    
    BS --> TPS
    TPS --> PE1
    PE1 --> PE1_VAL
    PE1_VAL --> BACK
    BACK --> NEW_BS
    NEW_BS --> RENDER
```

The `TwoPaneScene` sets `previousEntries = entries.dropLast(1)`, removing only the second entry when navigating back. This matches the user's mental model: they navigated forward by adding one entry, so back should remove one entry, not two.

The `ListDetailScene` sets `previousEntries = entries.dropLast(1)`, which removes the detail entry but keeps the list entry when navigating back.

**Sources:** [app/src/main/java/com/example/nav3recipes/scenes/twopane/TwoPaneScene.kt:89-99](), [app/src/main/java/com/example/nav3recipes/scenes/listdetail/ListDetailScene.kt:140-145]()

## Custom Scene Implementation Pattern

Both `TwoPaneScene` and `ListDetailScene` follow a common implementation pattern:

```mermaid
graph TB
    subgraph "Scene Class"
        SC["Scene<T> implementation"]
        KEY["override val key: Any"]
        PREV["override val previousEntries"]
        ENTRIES["override val entries"]
        CONTENT["override val content: @Composable"]
    end
    
    subgraph "Strategy Class"
        SS["SceneStrategy<T> implementation"]
        WSC["windowSizeClass: WindowSizeClass"]
        CALC["calculateScene(entries): Scene?"]
    end
    
    subgraph "Factory Function"
        REM["remember{Scene}SceneStrategy()"]
        CWA["currentWindowAdaptiveInfo()"]
    end
    
    subgraph "Metadata Helpers"
        COMP["companion object"]
        META["metadata functions"]
    end
    
    SS --> CALC
    CALC -->|"produces"| SC
    
    REM --> CWA
    CWA --> WSC
    WSC --> SS
    
    COMP --> META
    META -->|"used by"| CALC
```

**Sources:** [app/src/main/java/com/example/nav3recipes/scenes/twopane/TwoPaneScene.kt:1-109](), [app/src/main/java/com/example/nav3recipes/scenes/listdetail/ListDetailScene.kt:1-149]()

## Scene Content Layout

Scene implementations define their layout composition in the `content` property. Both examples use `Row` with weighted `Column` children to create side-by-side panes.

### Layout Structure

| Scene Type | First Pane Weight | Second Pane Weight | Layout Modifier |
|------------|-------------------|-------------------|-----------------|
| `TwoPaneScene` | 0.5f | 0.5f | `Modifier.fillMaxSize()` |
| `ListDetailScene` | 0.4f | 0.6f | `Modifier.fillMaxSize()` |

The layout is rendered by calling `NavEntry.Content()` on each entry within the scene's `entries` list:

```mermaid
graph LR
    subgraph "Scene content Lambda"
        ROW["Row(fillMaxSize)"]
        COL1["Column(weight)"]
        COL2["Column(weight)"]
    end
    
    subgraph "Entry Rendering"
        E1["firstEntry.Content()"]
        E2["secondEntry.Content()"]
    end
    
    ROW --> COL1
    ROW --> COL2
    COL1 --> E1
    COL2 --> E2
```

**Sources:** [app/src/main/java/com/example/nav3recipes/scenes/twopane/TwoPaneScene.kt:28-38](), [app/src/main/java/com/example/nav3recipes/scenes/listdetail/ListDetailScene.kt:52-76]()

## Advanced Scene Features

### AnimatedContent for Detail Transitions

`ListDetailScene` wraps the detail pane in `AnimatedContent` to provide slide transitions when the detail entry changes while maintaining the scene's stable key:

```mermaid
graph TB
    subgraph "ListDetailScene content"
        ROW["Row"]
        LIST_COL["Column(weight=0.4f)"]
        DETAIL_COL["Column(weight=0.6f)"]
    end
    
    subgraph "Detail Pane Content"
        AC["AnimatedContent"]
        TS["targetState = detailEntry"]
        CK["contentKey = entry.contentKey"]
        SPEC["transitionSpec"]
    end
    
    subgraph "Transition Effects"
        SLIDE_IN["slideInHorizontally(it)"]
        SLIDE_OUT["slideOutHorizontally(-it)"]
        TW["togetherWith"]
    end
    
    ROW --> LIST_COL
    ROW --> DETAIL_COL
    DETAIL_COL --> AC
    AC --> TS
    AC --> CK
    AC --> SPEC
    SPEC --> SLIDE_IN
    SPEC --> TW
    SPEC --> SLIDE_OUT
```

The `AnimatedContent` animates detail entry changes with horizontal slide transitions: new content slides in from the right (`initialOffsetX = { it }`), while old content slides out to the left (`targetOffsetX = { -it }`).

**Sources:** [app/src/main/java/com/example/nav3recipes/scenes/listdetail/ListDetailScene.kt:61-73]()

### LocalBackButtonVisibility

`ListDetailScene` provides `LocalBackButtonVisibility` as a `CompositionLocal` to control back button rendering. Detail entries displayed in a list-detail scene should not show their own back button, since back navigation is already handled by the scene context.

```mermaid
graph TB
    subgraph "Scene Composition"
        CLP["CompositionLocalProvider"]
        LBBV["LocalBackButtonVisibility"]
        VAL["provides false"]
    end
    
    subgraph "Detail Entry"
        DETAIL["detailEntry.Content()"]
        CHECK["if (LocalBackButtonVisibility.current)"]
        BTN["IconButton back arrow"]
    end
    
    CLP --> LBBV
    LBBV --> VAL
    VAL --> DETAIL
    DETAIL --> CHECK
    CHECK -->|"false in scene"| BTN
    BTN -->|"not rendered"| X["No back button"]
```

Detail entries query `LocalBackButtonVisibility.current` to conditionally render their back button. In single-pane mode, the value is `true` (default). In list-detail scene mode, the scene sets it to `false`.

**Sources:** [app/src/main/java/com/example/nav3recipes/scenes/listdetail/ListDetailScene.kt:59-74, 101](), [app/src/main/java/com/example/nav3recipes/scenes/listdetail/Content.kt:90-100]()

## Entry Filtering in Strategies

Scene strategies examine the back stack to find entries that match their metadata requirements. The filtering patterns differ between scene types:

### TwoPaneSceneStrategy Filtering

```mermaid
graph TB
    ENT["entries: List<NavEntry>"]
    TAKE["entries.takeLast(2)"]
    CHK_SIZE["lastTwoEntries.size == 2"]
    CHK_META["all { metadata.containsKey(TWO_PANE_KEY) }"]
    SCENE["TwoPaneScene"]
    NULL["return null"]
    
    ENT --> TAKE
    TAKE --> CHK_SIZE
    CHK_SIZE -->|"false"| NULL
    CHK_SIZE -->|"true"| CHK_META
    CHK_META -->|"false"| NULL
    CHK_META -->|"true"| SCENE
```

**Sources:** [app/src/main/java/com/example/nav3recipes/scenes/twopane/TwoPaneScene.kt:67-104]()

### ListDetailSceneStrategy Filtering

```mermaid
graph TB
    ENT["entries: List<NavEntry>"]
    DETAIL["entries.lastOrNull()"]
    CHK_D["?.takeIf { DETAIL_KEY in metadata }"]
    LIST["entries.findLast { LIST_KEY in metadata }"]
    SCENE["ListDetailScene"]
    NULL["return null"]
    
    ENT --> DETAIL
    DETAIL --> CHK_D
    CHK_D -->|"null"| NULL
    CHK_D -->|"found"| LIST
    LIST -->|"null"| NULL
    LIST -->|"found"| SCENE
```

The `ListDetailSceneStrategy` requires:
1. A detail entry as the last entry in the back stack
2. A list entry anywhere in the back stack (found via `findLast`)

This allows the list to remain stable while details change, and supports navigation from detail to other destinations (like Profile) that don't participate in the list-detail layout.

**Sources:** [app/src/main/java/com/example/nav3recipes/scenes/listdetail/ListDetailScene.kt:125-146]()

## Integration with NavDisplay

Scene strategies are passed to `NavDisplay` via the `sceneStrategy` parameter. The strategy is consulted before rendering each composition:

```mermaid
graph LR
    subgraph "Activity Setup"
        BS["backStack = rememberNavBackStack(Home)"]
        STRAT["strategy = rememberListDetailSceneStrategy()"]
    end
    
    subgraph "NavDisplay Configuration"
        ND["NavDisplay"]
        BS_PARAM["backStack = backStack"]
        BACK_PARAM["onBack = { backStack.removeLastOrNull() }"]
        STRAT_PARAM["sceneStrategy = strategy"]
        EP_PARAM["entryProvider = entryProvider { }"]
    end
    
    BS --> BS_PARAM
    STRAT --> STRAT_PARAM
    BS_PARAM --> ND
    BACK_PARAM --> ND
    STRAT_PARAM --> ND
    EP_PARAM --> ND
```

**Sources:** [app/src/main/java/com/example/nav3recipes/scenes/twopane/TwoPaneActivity.kt:56-98](), [app/src/main/java/com/example/nav3recipes/scenes/listdetail/ListDetailActivity.kt:63-98]()

## Material3 Adaptive Comparison

While custom scenes provide complete layout control, Navigation 3 also supports Material3's adaptive components through similar metadata patterns. Material3 adaptive uses `PaneScaffoldDirective` to calculate optimal layouts for phones, tablets, and foldables based on Material Design guidelines.

Key differences:

| Aspect | Custom Scenes | Material3 Adaptive |
|--------|---------------|-------------------|
| Layout control | Manual Row/Column composition | `PaneScaffoldDirective` calculations |
| Breakpoints | Custom (e.g., 600dp) | Material Design standard breakpoints |
| Animation | Custom `AnimatedContent` | Built-in pane transitions |
| Back stack behavior | Custom `previousEntries` logic | Scaffold-managed navigation |
| Metadata functions | Custom (e.g., `twoPane()`) | Standard (e.g., `mainPane()`, `supportingPane()`) |

For Material3 adaptive implementation details, see [Material3 Adaptive Layouts](#6.5).

**Sources:** Referenced from high-level architecture diagrams

## Back Stack Management with Scenes

Scene-based navigation often requires custom back stack manipulation logic to maintain UX consistency. The examples demonstrate two patterns:

### Duplicate Prevention Pattern

```mermaid
graph TB
    ADD["addProductRoute(productId)"]
    ROUTE["Product(productId)"]
    CHECK["backStack.contains(productRoute)"]
    ADD_OP["backStack.add(productRoute)"]
    SKIP["Skip addition"]
    
    ADD --> ROUTE
    ROUTE --> CHECK
    CHECK -->|"false"| ADD_OP
    CHECK -->|"true"| SKIP
```

The `TwoPaneActivity` checks for duplicate routes before adding to prevent the same product appearing multiple times in the back stack, which would create confusing back navigation behavior in two-pane mode.

**Sources:** [app/src/main/java/com/example/nav3recipes/scenes/twopane/TwoPaneActivity.kt:103-110]()

### Detail Replacement Pattern

```mermaid
graph TB
    ADD["addDetail(detailRoute)"]
    REMOVE["backStack.removeIf { it is ConversationDetail }"]
    ADD_OP["backStack.add(detailRoute)"]
    
    ADD --> REMOVE
    REMOVE --> ADD_OP
```

The `ListDetailActivity` removes all existing detail routes before adding a new detail. This ensures only one detail is in the back stack at a time, preventing back navigation from cycling through multiple details instead of returning to the list.

**Sources:** [app/src/main/java/com/example/nav3recipes/scenes/listdetail/ListDetailActivity.kt:104-111]()

## Scene Strategy Scope

`SceneStrategy.calculateScene()` executes within a `SceneStrategyScope`, which provides context for scene calculation. The scope is marked but doesn't expose additional APIs in the current implementation—it serves as an extension point for future scene strategy capabilities.

**Sources:** [app/src/main/java/com/example/nav3recipes/scenes/listdetail/ListDetailScene.kt:125](), [app/src/main/java/com/example/nav3recipes/scenes/twopane/TwoPaneScene.kt:67]()

---

