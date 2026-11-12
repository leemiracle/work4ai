<!-- source: DeepWiki mcp.deepwiki.com · repo android/nav3-recipes · page 13 Utilities and Helper Components · fetched 2026-10-23 -->

# Utilities and Helper Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/src/main/java/com/example/nav3recipes/basicsaveable/BasicSaveableActivity.kt](app/src/main/java/com/example/nav3recipes/basicsaveable/BasicSaveableActivity.kt)
- [app/src/main/java/com/example/nav3recipes/content/Content.kt](app/src/main/java/com/example/nav3recipes/content/Content.kt)
- [app/src/main/java/com/example/nav3recipes/ui/EdgeToEdgeCompat.kt](app/src/main/java/com/example/nav3recipes/ui/EdgeToEdgeCompat.kt)

</details>



This page documents the reusable utility functions and helper composables provided in the nav3-recipes repository. These components handle common concerns like edge-to-edge display configuration and demonstration UI, allowing recipes to focus on Navigation 3 patterns without duplicating boilerplate code.

**Covered in this page:**
- Edge-to-edge display configuration: `setEdgeToEdgeConfig()` extension function
- Reusable content composables: `ContentBase` and color variants for demonstration screens
- Helper components: `Title`, `Count`, and layout utilities

**For navigation-specific components, see:**
- Core Navigation 3 primitives: [Core Navigation 3 Concepts](#2.2)
- Navigation component reference: [Core Navigation Components Reference](#12)
</thinking>

## Utilities Architecture

The repository provides two categories of utilities:

1. **Display Configuration Utilities** - Functions for configuring Android system UI behavior
2. **Content Composables** - Pre-styled UI components for demonstration purposes

These utilities are designed to be independent, optional, and focused on reducing boilerplate in recipe examples.

---

## Edge-to-Edge Display Configuration

The repository provides the `setEdgeToEdgeConfig()` extension function to configure edge-to-edge display for modern Android UI. This utility is called by recipe activities in their `onCreate()` method before `setContent()`.

### Implementation: setEdgeToEdgeConfig()

The function is defined in [app/src/main/java/com/example/nav3recipes/ui/EdgeToEdgeCompat.kt:7-14]():

```mermaid
graph TB
    Activity["ComponentActivity"]
    SetEdge["setEdgeToEdgeConfig()"]
    EnableEdge["enableEdgeToEdge()"]
    CheckAPI{"Build.VERSION.SDK_INT >= Q?"}
    SetContrast["window.isNavigationBarContrastEnforced = false"]
    
    Activity --> SetEdge
    SetEdge --> EnableEdge
    SetEdge --> CheckAPI
    CheckAPI -->|"Yes (API 29+)"| SetContrast
    CheckAPI -->|"No"| Done["Done"]
    SetContrast --> Done
    
    EnableEdge -->|"Calls Activity KTX"| Core["enableEdgeToEdge()<br/>from androidx.activity"]
```

The function performs two operations:

| Operation | API Level | Purpose |
|-----------|-----------|---------|
| `enableEdgeToEdge()` | All | Configures transparent system bars and allows content to draw behind them |
| `window.isNavigationBarContrastEnforced = false` | 29+ (Q) | Forces 3-button navigation bar transparency |

**Sources:** [app/src/main/java/com/example/nav3recipes/ui/EdgeToEdgeCompat.kt:1-15]()

### Usage Pattern in Recipes

Recipe activities call this function before rendering content:

```mermaid
sequenceDiagram
    participant Activity as "Recipe Activity"
    participant SetEdge as "setEdgeToEdgeConfig()"
    participant EdgeToEdge as "enableEdgeToEdge()"
    participant Window as "window"
    
    Activity->>Activity: "onCreate(savedInstanceState)"
    Activity->>SetEdge: "setEdgeToEdgeConfig()"
    SetEdge->>EdgeToEdge: "Call Activity KTX function"
    Note over EdgeToEdge: "Configures transparent bars<br/>and edge-to-edge layout"
    SetEdge->>Window: "isNavigationBarContrastEnforced = false"
    Note over Window: "API 29+ only:<br/>Removes automatic contrast"
    SetEdge-->>Activity: "Configuration complete"
    Activity->>Activity: "setContent { ... }"
    Note over Activity: "Content now renders<br/>behind system bars"
```

Example from [app/src/main/java/com/example/nav3recipes/basicsaveable/BasicSaveableActivity.kt:41-44]():

```
override fun onCreate(savedInstanceState: Bundle?) {
    setEdgeToEdgeConfig()
    super.onCreate(savedInstanceState)
    setContent { ... }
}
```

### Content Inset Handling

When edge-to-edge is enabled, composables must apply padding to avoid system bar overlap. The content composables in this repository use `Modifier.safeDrawingPadding()` from [app/src/main/java/com/example/nav3recipes/content/Content.kt:104]():

```mermaid
graph LR
    ContentBase["ContentBase composable"]
    Column["Column"]
    Modifiers["Modifier chain"]
    FillMax["fillMaxSize()"]
    SafePad["safeDrawingPadding()"]
    Clip["clip(RoundedCornerShape)"]
    
    ContentBase --> Column
    Column --> Modifiers
    Modifiers --> FillMax
    FillMax --> SafePad
    SafePad --> Clip
    
    SafePad -->|"Applies padding for"| SystemBars["System bars<br/>(status + navigation)"]
    SafePad -->|"Applies padding for"| Cutouts["Display cutouts"]
```

The `safeDrawingPadding()` modifier automatically applies padding for:
- Status bar (top)
- Navigation bar (bottom)
- Display cutouts (notches, camera holes)

**Sources:** [app/src/main/java/com/example/nav3recipes/ui/EdgeToEdgeCompat.kt:1-15](), [app/src/main/java/com/example/nav3recipes/basicsaveable/BasicSaveableActivity.kt:41-44](), [app/src/main/java/com/example/nav3recipes/content/Content.kt:100-118]()

---

## Reusable Content Components

The repository provides pre-styled composable components for demonstration purposes. These components allow recipes to focus on navigation logic without implementing custom UI for each destination.

### ContentBase Composable

The `ContentBase` composable is the foundation for all demonstration screens, defined in [app/src/main/java/com/example/nav3recipes/content/Content.kt:93-118]():

```mermaid
graph TB
    ContentBase["ContentBase"]
    
    Params["Parameters"]
    Params --> Title["title: String"]
    Params --> Modifier["modifier: Modifier = Modifier"]
    Params --> OnNext["onNext: (() -> Unit)? = null"]
    Params --> Content["content: (@Composable () -> Unit)? = null"]
    
    ContentBase --> Params
    
    Layout["Layout Structure"]
    Layout --> Column["Column<br/>(horizontalAlignment = CenterHorizontally)"]
    Column --> TitleComp["Title(title)"]
    Column --> ContentSlot["content() if provided"]
    Column --> NextButton["Button('Next') if onNext provided"]
    
    ContentBase --> Layout
    
    Modifiers["Applied Modifiers"]
    Modifiers --> Fill["fillMaxSize()"]
    Modifiers --> Safe["safeDrawingPadding()"]
    Modifiers --> Clip["clip(RoundedCornerShape(48.dp))"]
    
    Column --> Modifiers
```

**ContentBase Parameters:**

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `title` | `String` | Required | Heading text displayed at top via `Title()` helper |
| `modifier` | `Modifier` | `Modifier` | Applied to root `Column`, typically contains background color |
| `onNext` | `(() -> Unit)?` | `null` | Navigation callback; if non-null, displays "Next" button |
| `content` | `(@Composable () -> Unit)?` | `null` | Optional content slot for custom body content |

**Sources:** [app/src/main/java/com/example/nav3recipes/content/Content.kt:93-118]()

### Color Variant Composables

The repository provides eight color-coded wrapper composables that call `ContentBase` with specific background colors from the theme. These are defined in [app/src/main/java/com/example/nav3recipes/content/Content.kt:152-253]():

```mermaid
graph TB
    Variants["Color Variant Composables"]
    
    Variants --> Red["ContentRed<br/>(background: PastelRed)"]
    Variants --> Orange["ContentOrange<br/>(background: PastelOrange)"]
    Variants --> Yellow["ContentYellow<br/>(background: PastelYellow)"]
    Variants --> Green["ContentGreen<br/>(background: PastelGreen)"]
    Variants --> Blue["ContentBlue<br/>(background: PastelBlue)"]
    Variants --> Mauve["ContentMauve<br/>(background: PastelMauve)"]
    Variants --> Purple["ContentPurple<br/>(background: PastelPurple)"]
    Variants --> Pink["ContentPink<br/>(background: PastelPink)"]
    
    AllVariants["All variants accept same parameters as ContentBase"]
    Variants --> AllVariants
```

Each variant composable:
1. Accepts the same parameters as `ContentBase` (title, modifier, onNext, content)
2. Applies a background color from the theme's pastel color palette
3. Passes parameters through to `ContentBase`

| Composable | Background Color | Typical Usage |
|------------|------------------|---------------|
| `ContentRed` | `PastelRed` | First destination or primary screen |
| `ContentOrange` | `PastelOrange` | Second destination |
| `ContentYellow` | `PastelYellow` | Third destination |
| `ContentGreen` | `PastelGreen` | Fourth destination or success state |
| `ContentBlue` | `PastelBlue` | Fifth destination or detail screen |
| `ContentMauve` | `PastelMauve` | Sixth destination |
| `ContentPurple` | `PastelPurple` | Seventh destination |
| `ContentPink` | `PastelPink` | Eighth destination or special state |

**Sources:** [app/src/main/java/com/example/nav3recipes/content/Content.kt:152-253]()

### Pre-configured Content Composables

The repository also provides `ContentA` and `ContentB` with fixed titles and lorem ipsum text, defined in [app/src/main/java/com/example/nav3recipes/content/Content.kt:53-75]():

```mermaid
graph LR
    ContentA["ContentA"]
    ContentB["ContentB"]
    
    ContentA --> RedBG["ContentBase<br/>(background: PastelRed)"]
    ContentA --> TitleA["title = 'Content A Title'"]
    ContentA --> Lorem["Lorem ipsum body text"]
    ContentA --> OnNext["onNext parameter"]
    
    ContentB --> GreenBG["ContentBase<br/>(background: PastelGreen)"]
    ContentB --> TitleB["title = 'Content B Title'"]
    ContentB --> Lorem2["Lorem ipsum body text"]
```

**ContentA** ([app/src/main/java/com/example/nav3recipes/content/Content.kt:53-63]()):
- Background: `PastelRed`
- Title: "Content A Title"
- Body: Lorem ipsum placeholder text
- Button: Optional, controlled by `onNext` parameter

**ContentB** ([app/src/main/java/com/example/nav3recipes/content/Content.kt:66-75]()):
- Background: `PastelGreen`
- Title: "Content B Title"
- Body: Lorem ipsum placeholder text
- Button: No button (no `onNext` parameter)

**Sources:** [app/src/main/java/com/example/nav3recipes/content/Content.kt:53-75]()

### Usage in Recipe Activities

Recipe activities use these content composables in their `entryProvider` to map `NavKey` instances to UI:

```mermaid
graph TB
    NavDisplay["NavDisplay"]
    EntryProvider["entryProvider lambda"]
    NavDisplay --> EntryProvider
    
    EntryProvider --> RouteA["when (key) { is RouteA -> ... }"]
    EntryProvider --> RouteB["when (key) { is RouteB -> ... }"]
    
    RouteA --> NavEntryA["NavEntry(key)"]
    RouteB --> NavEntryB["NavEntry(key)"]
    
    NavEntryA --> ContentGreen["ContentGreen(<br/>  title = 'Welcome to Nav3',<br/>  onNext = { backStack.add(RouteB) }<br/>)"]
    
    NavEntryB --> ContentBlue["ContentBlue(<br/>  title = 'Route id: ${key.id}'<br/>)"]
```

Example from [app/src/main/java/com/example/nav3recipes/basicsaveable/BasicSaveableActivity.kt:52-64]():

```
when (key) {
    is RouteA -> NavEntry(key) {
        ContentGreen("Welcome to Nav3") {
            Button(onClick = { backStack.add(RouteB("123")) }) {
                Text("Click to navigate")
            }
        }
    }
    is RouteB -> NavEntry(key) {
        ContentBlue("Route id: ${key.id} ")
    }
}
```

The distinct background colors make navigation transitions visually obvious, helping developers understand back stack behavior.

**Sources:** [app/src/main/java/com/example/nav3recipes/basicsaveable/BasicSaveableActivity.kt:44-72](), [app/src/main/java/com/example/nav3recipes/content/Content.kt:53-75]()

### Helper Composables

**Title**: Displays bold, centered heading text, defined in [app/src/main/java/com/example/nav3recipes/content/Content.kt:121-129]():

```mermaid
graph LR
    Title["Title(title: String)"]
    Text["Text composable"]
    Modifiers["Modifiers"]
    
    Title --> Text
    Title --> Modifiers
    
    Modifiers --> Padding["padding(24.dp)"]
    Modifiers --> Align["align(CenterHorizontally)"]
    Modifiers --> Font["fontWeight = Bold"]
```

**Count**: Demonstrates state preservation with a counter, defined in [app/src/main/java/com/example/nav3recipes/content/Content.kt:140-148]():

```mermaid
graph TB
    Count["Count(name: String)"]
    State["var count by rememberSaveable"]
    Display["Text('Count $name is $count')"]
    Increment["Button(onClick = { count++ })"]
    
    Count --> State
    State --> Display
    State --> Increment
```

The `Count` composable uses `rememberSaveable` to preserve the count value across configuration changes and process death, demonstrating state survival in navigation scenarios.

**SampleContent**: Generic content creator defined in [app/src/main/java/com/example/nav3recipes/content/Content.kt:78-89](), accepts title, background color, and optional navigation callback.

**Sources:** [app/src/main/java/com/example/nav3recipes/content/Content.kt:78-148]()

---

## Recipe Picker Infrastructure

The `RecipePickerActivity` serves as the entry point to the application. It displays a scrollable, categorized list of all recipes and launches the selected recipe's activity.

### Recipe Picker Architecture

```mermaid
graph TB
    Launcher["Android Launcher"]
    Manifest["AndroidManifest.xml"]
    
    Launcher -->|"App icon tapped"| Manifest
    Manifest -->|"MAIN/LAUNCHER intent"| RecipePicker["RecipePickerActivity"]
    
    RecipePicker --> LoadRecipes["Load Recipe List<br/>from allRecipes()"]
    LoadRecipes --> GroupByCategory["Group Recipes<br/>by RecipeCategory"]
    
    GroupByCategory --> RenderUI["Render Scrollable UI"]
    
    RenderUI --> LazyColumn["LazyColumn"]
    LazyColumn --> CategoryHeader["Category Header"]
    LazyColumn --> RecipeCard["Recipe Card<br/>(name, description)"]
    
    RecipeCard -->|"onClick"| CreateIntent["recipe.start(context)"]
    CreateIntent --> LaunchActivity["startActivity(intent)"]
    LaunchActivity --> TargetRecipe["Target Recipe Activity<br/>(e.g., BasicActivity)"]
    
    TargetRecipe -->|"Back pressed"| RecipePicker
```

### Recipe List Structure

The recipe list is defined as a function that returns `List<Recipe>`:

```mermaid
graph LR
    allRecipes["allRecipes() Function"]
    
    allRecipes --> RecipeList["List<Recipe>"]
    
    RecipeList --> BasicGroup["Basic API Examples<br/>3 recipes"]
    RecipeList --> DeepLinkGroup["Deep Links<br/>1 recipe"]
    RecipeList --> SceneGroup["Layouts using Scenes<br/>4 recipes"]
    RecipeList --> MaterialGroup["Material Adaptive<br/>2 recipes"]
    RecipeList --> AnimGroup["Animations<br/>1 recipe"]
    RecipeList --> CommonGroup["Common Use Cases<br/>3 recipes"]
    RecipeList --> ArchGroup["Architecture<br/>2 recipes"]
    RecipeList --> VMGroup["ViewModels<br/>3 recipes"]
    RecipeList --> ResultGroup["Results<br/>2 recipes"]
    
    BasicGroup --> Recipe1["Recipe(<br/>name = 'Basic',<br/>description = '...',<br/>activity = BasicActivity::class,<br/>category = BASIC<br/>)"]
```

Each `Recipe` instance is constructed with:
- **name:** Short, descriptive title
- **description:** Brief explanation of demonstrated concept
- **activity:** KClass reference to the Activity to launch
- **category:** One of the `RecipeCategory` enum values for grouping

**Sources:** README.md:13-54, README.md:64

---

## Common Utilities Summary

The following table summarizes all common utilities available across recipes:

| Utility | Location | Purpose | Used By |
|---------|----------|---------|---------|
| `enableEdgeToEdge()` | Activity extension | Configure transparent system bars and edge-to-edge display | All recipe activities |
| `ContentBase()` | Composable | Base component for demonstration screens | All recipe UIs |
| `ContentA()` through `ContentE()` | Composables | Pre-configured colored content variants | Most recipe UIs |
| `Recipe` data class | Data model | Define recipe metadata and launch capability | `RecipePickerActivity` |
| `RecipeCategory` enum | Data model | Group recipes by functionality | `RecipePickerActivity` |
| `allRecipes()` | Function | Provide complete list of recipes | `RecipePickerActivity` |

### Design Principles

The common utilities follow these principles:

1. **Minimal dependencies:** Utilities depend only on Android/Compose APIs, not on each other
2. **Opt-in usage:** Recipes can choose not to use utilities if they demonstrate alternative approaches
3. **Focus enablement:** By handling boilerplate, utilities let recipes focus on demonstrating one concept
4. **Consistency:** Provide uniform look and feel across all recipes for easier learning
5. **Isolation:** Each recipe remains self-contained and can be copied as a starting point

**Sources:** README.md:64, README.md:1-8

---

