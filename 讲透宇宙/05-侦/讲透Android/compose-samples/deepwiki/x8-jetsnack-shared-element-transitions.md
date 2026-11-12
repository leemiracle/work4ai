<!-- source: DeepWiki mcp.deepwiki.com · repo android/compose-samples · extra page Jetsnack Shared Element Transitions · fetched 2026-10-23 -->

# Jetsnack Shared Element Transitions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Jetsnack/app/src/main/java/com/example/jetsnack/model/Filter.kt](Jetsnack/app/src/main/java/com/example/jetsnack/model/Filter.kt)
- [Jetsnack/app/src/main/java/com/example/jetsnack/model/SnackbarManager.kt](Jetsnack/app/src/main/java/com/example/jetsnack/model/SnackbarManager.kt)
- [Jetsnack/app/src/main/java/com/example/jetsnack/ui/JetsnackApp.kt](Jetsnack/app/src/main/java/com/example/jetsnack/ui/JetsnackApp.kt)
- [Jetsnack/app/src/main/java/com/example/jetsnack/ui/SnackSharedElementKey.kt](Jetsnack/app/src/main/java/com/example/jetsnack/ui/SnackSharedElementKey.kt)
- [Jetsnack/app/src/main/java/com/example/jetsnack/ui/components/Filters.kt](Jetsnack/app/src/main/java/com/example/jetsnack/ui/components/Filters.kt)
- [Jetsnack/app/src/main/java/com/example/jetsnack/ui/components/GradientTintedIconButton.kt](Jetsnack/app/src/main/java/com/example/jetsnack/ui/components/GradientTintedIconButton.kt)
- [Jetsnack/app/src/main/java/com/example/jetsnack/ui/components/QuantitySelector.kt](Jetsnack/app/src/main/java/com/example/jetsnack/ui/components/QuantitySelector.kt)
- [Jetsnack/app/src/main/java/com/example/jetsnack/ui/components/Snackbar.kt](Jetsnack/app/src/main/java/com/example/jetsnack/ui/components/Snackbar.kt)
- [Jetsnack/app/src/main/java/com/example/jetsnack/ui/components/Snacks.kt](Jetsnack/app/src/main/java/com/example/jetsnack/ui/components/Snacks.kt)
- [Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/DestinationBar.kt](Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/DestinationBar.kt)
- [Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/Feed.kt](Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/Feed.kt)
- [Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/FilterScreen.kt](Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/FilterScreen.kt)
- [Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/Home.kt](Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/Home.kt)
- [Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/Profile.kt](Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/Profile.kt)
- [Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/cart/Cart.kt](Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/cart/Cart.kt)
- [Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/cart/SwipeDismissItem.kt](Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/cart/SwipeDismissItem.kt)
- [Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/search/Categories.kt](Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/search/Categories.kt)
- [Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/search/Results.kt](Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/search/Results.kt)
- [Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/search/Search.kt](Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/search/Search.kt)
- [Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/search/Suggestions.kt](Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/search/Suggestions.kt)
- [Jetsnack/app/src/main/java/com/example/jetsnack/ui/snackdetail/SnackDetail.kt](Jetsnack/app/src/main/java/com/example/jetsnack/ui/snackdetail/SnackDetail.kt)

</details>



## Purpose and Scope

This document explains the shared element transition system in the Jetsnack sample application. It covers how snack items animate smoothly when navigating from the feed/search/cart screens to the detail screen, including the key-based identification system, animation specifications, and coordinate space transformations.

For information about Jetsnack's custom design system (colors, theming), see [4.2.1](#4.2.1). For general navigation patterns across samples, see [5.3](#5.3).

---

## System Architecture Overview

Jetsnack implements shared element transitions using Compose's `SharedTransitionLayout` API (Experimental as of the implementation). The system enables five distinct UI elements to transition between screens: bounds container, snack image, title text, tagline text, and background gradient.

### High-Level Architecture

```mermaid
graph TB
    subgraph "App Root"
        JA["JetsnackApp"]
        STL["SharedTransitionLayout"]
        NH["NavHost"]
    end
    
    subgraph "CompositionLocal Providers"
        LSTS["LocalSharedTransitionScope"]
        LNAVS["LocalNavAnimatedVisibilityScope"]
    end
    
    subgraph "Source Screens"
        FEED["Feed Screen"]
        SEARCH["Search Screen"]
        CART["Cart Screen"]
        HSI["HighlightSnackItem"]
        SI["SnackItem"]
        CI["CartItem"]
    end
    
    subgraph "Destination Screen"
        SD["SnackDetail"]
        IMG["Image composable"]
        TTL["Title composable"]
        TGL["Tagline composable"]
        HDR["Header composable"]
        BDY["Body composable"]
    end
    
    subgraph "Key System"
        SSEK["SnackSharedElementKey(snackId, origin, type)"]
        SSET["SnackSharedElementType enum"]
    end
    
    JA --> STL
    STL --> NH
    STL -.provides.-> LSTS
    NH -.provides.-> LNAVS
    
    FEED --> HSI
    FEED --> SI
    SEARCH --> SI
    CART --> CI
    
    HSI -.uses.-> SSEK
    SI -.uses.-> SSEK
    CI --> SD
    
    SD --> IMG
    SD --> TTL
    SD --> TGL
    SD --> HDR
    SD --> BDY
    
    IMG -.uses.-> SSEK
    TTL -.uses.-> SSEK
    TGL -.uses.-> SSEK
    HDR -.uses.-> SSEK
    
    SSEK --> SSET
    
    LSTS -.accessed by.-> HSI
    LSTS -.accessed by.-> SI
    LSTS -.accessed by.-> SD
    LNAVS -.accessed by.-> SD
```

**Sources:** [Jetsnack/app/src/main/java/com/example/jetsnack/ui/JetsnackApp.kt:62-105](), [Jetsnack/app/src/main/java/com/example/jetsnack/ui/SnackSharedElementKey.kt:1-30]()

---

## Shared Element Key System

### SnackSharedElementKey Structure

The transition system uses a data class `SnackSharedElementKey` to uniquely identify each participating UI element across navigation boundaries.

```mermaid
classDiagram
    class SnackSharedElementKey {
        +Long snackId
        +String origin
        +SnackSharedElementType type
    }
    
    class SnackSharedElementType {
        <<enumeration>>
        Bounds
        Image
        Title
        Tagline
        Background
    }
    
    SnackSharedElementKey --> SnackSharedElementType
    
    class HighlightSnackItem {
        Uses: Bounds, Background, Image, Title, Tagline
    }
    
    class SnackItem {
        Uses: Image, Title
    }
    
    class SnackDetail {
        Uses: Bounds, Background, Image, Title, Tagline
    }
    
    HighlightSnackItem ..> SnackSharedElementKey
    SnackItem ..> SnackSharedElementKey
    SnackDetail ..> SnackSharedElementKey
```

| Field | Type | Purpose |
|-------|------|---------|
| `snackId` | `Long` | Unique identifier for the snack item |
| `origin` | `String` | Source screen identifier (collection ID or "cart", "search", "details") |
| `type` | `SnackSharedElementType` | Which UI element is being transitioned |

The `origin` parameter is critical for handling multiple instances of the same snack across different collections, ensuring the correct item animates even when the same snack appears in multiple lists.

**Sources:** [Jetsnack/app/src/main/java/com/example/jetsnack/ui/SnackSharedElementKey.kt:19-27]()

---

## CompositionLocal Setup

Jetsnack uses two `CompositionLocal` providers to propagate scope information down the composition tree:

```mermaid
graph TB
    subgraph "JetsnackApp Root"
        STL["SharedTransitionLayout { }"]
        PROVIDER1["CompositionLocalProvider"]
        NAVHOST["NavHost"]
    end
    
    subgraph "Custom Composable Extension"
        CWC["composableWithCompositionLocal"]
        PROVIDER2["CompositionLocalProvider"]
        CONTENT["content lambda"]
    end
    
    subgraph "Screen Composables"
        MC["MainContainer"]
        SD["SnackDetail"]
        FEED["Feed"]
    end
    
    STL -->|"provides this"| PROVIDER1
    PROVIDER1 -->|"LocalSharedTransitionScope"| NAVHOST
    NAVHOST -->|"calls"| CWC
    CWC -->|"provides this@composable"| PROVIDER2
    PROVIDER2 -->|"LocalNavAnimatedVisibilityScope"| CONTENT
    CONTENT --> MC
    CONTENT --> SD
    MC --> FEED
```

### CompositionLocal Definitions

Both scopes are nullable and must be validated at usage sites:

```kotlin
val LocalNavAnimatedVisibilityScope = compositionLocalOf<AnimatedVisibilityScope?> { null }
val LocalSharedTransitionScope = compositionLocalOf<SharedTransitionScope?> { null }
```

### Usage Pattern

Every composable participating in transitions must retrieve both scopes:

```kotlin
val sharedTransitionScope = LocalSharedTransitionScope.current
    ?: throw IllegalStateException("No Scope found")
val animatedVisibilityScope = LocalNavAnimatedVisibilityScope.current
    ?: throw IllegalStateException("No Scope found")
```

**Sources:** [Jetsnack/app/src/main/java/com/example/jetsnack/ui/JetsnackApp.kt:169-170](), [Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/Home.kt:86-125](), [Jetsnack/app/src/main/java/com/example/jetsnack/ui/snackdetail/SnackDetail.kt:148-151]()

---

## Shared Element Types

### Type Mapping Table

| Type | Visual Element | Transition Behavior | Used In |
|------|---------------|---------------------|---------|
| `Bounds` | Container card shape | Morphs shape with rounded corner animation | HighlightSnackItem → SnackDetail |
| `Image` | Snack product image | Scales and translates | All item types → SnackDetail |
| `Title` | Snack name text | Fades, scales, translates | HighlightSnackItem, SnackItem → SnackDetail |
| `Tagline` | Snack description text | Fades, scales, translates | HighlightSnackItem → SnackDetail |
| `Background` | Gradient background | Scales, fades, blurs | HighlightSnackItem → SnackDetail |

### Element Hierarchy in SnackDetail

```mermaid
graph TB
    subgraph "SnackDetail Layout"
        BOX["Box (Bounds sharedBounds)"]
        HEADER["Header (Background sharedBounds)"]
        BODY["Body (ScrollState)"]
        TITLE["Title (Title & Tagline sharedBounds)"]
        IMAGE["Image (Image sharedBounds)"]
        UP["Up Button (renderInOverlay)"]
        CART["CartBottomBar (renderInOverlay)"]
    end
    
    BOX -->|"contains"| HEADER
    BOX -->|"contains"| BODY
    BOX -->|"contains"| TITLE
    BOX -->|"contains"| IMAGE
    BOX -->|"overlays"| UP
    BOX -->|"overlays"| CART
    
    HEADER -.animates.-> BG["Background gradient"]
    TITLE -.animates.-> TTXT["Title text"]
    TITLE -.animates.-> TGTXT["Tagline text"]
    IMAGE -.animates.-> IMG["SnackImage"]
```

**Sources:** [Jetsnack/app/src/main/java/com/example/jetsnack/ui/snackdetail/SnackDetail.kt:161-191]()

---

## Feed-to-Detail Transition Flow

### Transition Sequence Diagram

```mermaid
sequenceDiagram
    participant Feed as Feed Screen
    participant HSI as HighlightSnackItem
    participant Nav as Navigation
    participant SD as SnackDetail
    participant STS as SharedTransitionScope
    
    Feed->>HSI: Display with sharedBounds modifiers
    HSI->>HSI: Create SnackSharedElementKey(id, collectionId, type)
    
    Note over HSI: User taps item
    HSI->>Nav: onSnackClick(snackId, origin)
    
    Nav->>Nav: Navigate to SnackDetail route
    Nav->>SD: Compose with same snackId, origin
    
    SD->>SD: Create matching SnackSharedElementKey
    SD->>STS: Match keys and compute bounds transform
    
    STS->>STS: Animate: EnterExitState.PreEnter → Visible
    
    par Animate Bounds
        STS->>HSI: Morph rounded corners (20dp → 0dp)
        STS->>SD: Morph rounded corners (20dp → 0dp)
    and Animate Image
        STS->>HSI: fadeOut + scale
        STS->>SD: fadeIn + scale
    and Animate Text
        STS->>HSI: fadeOut + scale
        STS->>SD: fadeIn + scale
    and Animate Background
        STS->>HSI: fadeOut
        STS->>SD: fadeIn + blur
    end
    
    STS->>SD: Transition complete, state = Visible
```

### Code Flow for HighlightSnackItem → SnackDetail

#### Source: HighlightSnackItem

The highlighted snack card on the feed screen defines all five shared elements:

```mermaid
graph LR
    subgraph "HighlightSnackItem Card"
        CARD["JetsnackCard with sharedBounds (Bounds)"]
        BG["Box with sharedBounds (Background)"]
        IMG["SnackImage with sharedBounds (Image)"]
        TTL["Text with sharedBounds (Title)"]
        TGL["Text with sharedBounds (Tagline)"]
    end
    
    CARD -->|"contains"| BG
    CARD -->|"contains"| IMG
    CARD -->|"contains"| TTL
    CARD -->|"contains"| TGL
    
    CARD -.key.-> KEY1["SnackSharedElementKey(id, origin, Bounds)"]
    BG -.key.-> KEY2["SnackSharedElementKey(id, origin, Background)"]
    IMG -.key.-> KEY3["SnackSharedElementKey(id, origin, Image)"]
    TTL -.key.-> KEY4["SnackSharedElementKey(id, origin, Title)"]
    TGL -.key.-> KEY5["SnackSharedElementKey(id, origin, Tagline)"]
```

**Sources:** [Jetsnack/app/src/main/java/com/example/jetsnack/ui/components/Snacks.kt:260-438]()

#### Destination: SnackDetail

The detail screen defines matching shared element keys for seamless transition:

**Sources:** [Jetsnack/app/src/main/java/com/example/jetsnack/ui/snackdetail/SnackDetail.kt:145-191](), [Jetsnack/app/src/main/java/com/example/jetsnack/ui/snackdetail/SnackDetail.kt:194-249](), [Jetsnack/app/src/main/java/com/example/jetsnack/ui/snackdetail/SnackDetail.kt:388-468](), [Jetsnack/app/src/main/java/com/example/jetsnack/ui/snackdetail/SnackDetail.kt:471-515]()

---

## Animation Specifications

### Spring Animation Functions

Jetsnack defines two custom spring animation functions for different motion types:

| Function | Damping Ratio | Stiffness | Usage |
|----------|--------------|-----------|--------|
| `spatialExpressiveSpring()` | 0.8f | 380f | Position, size changes (bounds, layout) |
| `nonSpatialExpressiveSpring()` | 1.0f | 1600f | Opacity, color changes (fade in/out) |

```mermaid
graph TB
    subgraph "Animation Configuration"
        SPATIAL["spatialExpressiveSpring<br/>dampingRatio=0.8f, stiffness=380f"]
        NONSPATIAL["nonSpatialExpressiveSpring<br/>dampingRatio=1.0f, stiffness=1600f"]
    end
    
    subgraph "Applied To"
        BOUNDS["BoundsTransform"]
        ENTER["Enter Transitions"]
        EXIT["Exit Transitions"]
        CORNER["Rounded Corner Animation"]
        NAVBAR["Bottom Navigation Bar"]
    end
    
    SPATIAL -->|"snackDetailBoundsTransform"| BOUNDS
    SPATIAL --> NAVBAR
    NONSPATIAL --> ENTER
    NONSPATIAL --> EXIT
    
    BOUNDS -.used in.-> S1["sharedBounds boundsTransform"]
    ENTER -.used in.-> S2["fadeIn, enter transitions"]
    EXIT -.used in.-> S3["fadeOut, exit transitions"]
    CORNER -.uses.-> S4["animateDp for corners"]
```

### BoundsTransform Definition

The global bounds transform ensures all spatial transitions use the same spring physics:

```kotlin
val snackDetailBoundsTransform = BoundsTransform { _, _ ->
    spatialExpressiveSpring()
}
```

**Sources:** [Jetsnack/app/src/main/java/com/example/jetsnack/ui/snackdetail/SnackDetail.kt:130-142]()

---

## Advanced Transition Techniques

### Rounded Corner Animation

The `Bounds` shared element animates corner radius during transitions using `EnterExitState`:

```mermaid
stateDiagram-v2
    [*] --> PreEnter: Navigation starts
    PreEnter --> Visible: Enter animation
    Visible --> PostExit: Back navigation
    PostExit --> [*]
    
    note right of PreEnter: cornerRadius = 20.dp
    note right of Visible: cornerRadius = 0.dp
    note right of PostExit: cornerRadius = 20.dp
```

The animation is defined in both the source and destination:

**Source (HighlightSnackItem):**
- PreEnter: 0.dp
- Visible: 20.dp
- PostExit: 20.dp

**Destination (SnackDetail):**
- PreEnter: 20.dp
- Visible: 0.dp
- PostExit: 20.dp

This creates a smooth morph from rounded card corners to full-screen (no corners) and back.

**Sources:** [Jetsnack/app/src/main/java/com/example/jetsnack/ui/snackdetail/SnackDetail.kt:152-159](), [Jetsnack/app/src/main/java/com/example/jetsnack/ui/components/Snacks.kt:274-281]()

### Overlay Rendering for UI Chrome

Non-content UI elements (back button, bottom bar) use `renderInSharedTransitionScopeOverlay` to render above the transition:

```kotlin
Modifier
    .renderInSharedTransitionScopeOverlay(zIndexInOverlay = 3f)
    .animateEnterExit(
        enter = scaleIn(tween(300, delayMillis = 300)),
        exit = scaleOut(tween(20))
    )
```

This ensures these elements don't participate in the shared element animation but still animate in/out appropriately.

**Sources:** [Jetsnack/app/src/main/java/com/example/jetsnack/ui/snackdetail/SnackDetail.kt:259-266](), [Jetsnack/app/src/main/java/com/example/jetsnack/ui/snackdetail/SnackDetail.kt:558-567]()

### skipToLookaheadSize for Layout Stability

The `Body` composable uses `skipToLookaheadSize()` to prevent layout thrashing during transitions:

```kotlin
Column(modifier = Modifier.skipToLookaheadSize()) {
    // Scrollable content
}
```

This modifier tells the layout system to immediately use the final target size during lookahead, preventing unnecessary intermediate layouts that would cause jank.

**Sources:** [Jetsnack/app/src/main/java/com/example/jetsnack/ui/snackdetail/SnackDetail.kt:286](), [Jetsnack/app/src/main/java/com/example/jetsnack/ui/snackdetail/SnackDetail.kt:321](), [Jetsnack/app/src/main/java/com/example/jetsnack/ui/snackdetail/SnackDetail.kt:343](), [Jetsnack/app/src/main/java/com/example/jetsnack/ui/snackdetail/SnackDetail.kt:461]()

### ResizeMode Configuration

Different shared elements use different resize modes:

| Element | ResizeMode | Reason |
|---------|-----------|--------|
| Title | `ScaleToBounds()` | Text should scale uniformly |
| Tagline | `ScaleToBounds()` | Text should scale uniformly |
| Background | `ScaleToBounds()` | Gradient should stretch/compress |
| Image | Default (RemeasureToBounds) | Image content should reflow |
| Bounds | Default (RemeasureToBounds) | Container should reflow content |

**Sources:** [Jetsnack/app/src/main/java/com/example/jetsnack/ui/components/Snacks.kt:250](), [Jetsnack/app/src/main/java/com/example/jetsnack/ui/components/Snacks.kt:346](), [Jetsnack/app/src/main/java/com/example/jetsnack/ui/components/Snacks.kt:408](), [Jetsnack/app/src/main/java/com/example/jetsnack/ui/components/Snacks.kt:432]()

---

## Transition Configuration Summary

### Complete Modifier Chain Example

Here's a complete example of a `sharedBounds` modifier from SnackDetail's outer Box:

```kotlin
.sharedBounds(
    rememberSharedContentState(
        key = SnackSharedElementKey(
            snackId = snack.id,
            origin = origin,
            type = SnackSharedElementType.Bounds
        )
    ),
    animatedVisibilityScope,
    clipInOverlayDuringTransition = OverlayClip(RoundedCornerShape(roundedCornerAnim)),
    boundsTransform = snackDetailBoundsTransform,
    exit = fadeOut(nonSpatialExpressiveSpring()),
    enter = fadeIn(nonSpatialExpressiveSpring())
)
```

### Transition Configuration Matrix

```mermaid
graph TB
    subgraph "Element Type Configurations"
        BOUNDS["Bounds<br/>boundsTransform: spatial<br/>enter/exit: nonSpatial fade<br/>clip: rounded corners"]
        
        IMAGE["Image<br/>boundsTransform: spatial<br/>enter/exit: fade (non/spatial)<br/>no clip"]
        
        TITLE["Title/Tagline<br/>boundsTransform: spatial<br/>enter/exit: nonSpatial fade<br/>resizeMode: ScaleToBounds"]
        
        BACKGROUND["Background<br/>boundsTransform: spatial<br/>enter/exit: nonSpatial fade<br/>resizeMode: ScaleToBounds"]
    end
    
    subgraph "Animation Functions"
        S["spatialExpressiveSpring()"]
        NS["nonSpatialExpressiveSpring()"]
    end
    
    BOUNDS -.uses.-> S
    BOUNDS -.uses.-> NS
    IMAGE -.uses.-> S
    IMAGE -.uses.-> NS
    TITLE -.uses.-> S
    TITLE -.uses.-> NS
    BACKGROUND -.uses.-> S
    BACKGROUND -.uses.-> NS
```

**Sources:** [Jetsnack/app/src/main/java/com/example/jetsnack/ui/snackdetail/SnackDetail.kt:164-178]()

---

## Navigation Integration

### Custom Navigation Composable Extension

Jetsnack extends `NavGraphBuilder` with `composableWithCompositionLocal` to inject `LocalNavAnimatedVisibilityScope`:

```kotlin
fun NavGraphBuilder.composableWithCompositionLocal(
    route: String,
    // ... other parameters
    content: @Composable AnimatedContentScope.(NavBackStackEntry) -> Unit
) {
    composable(...) {
        CompositionLocalProvider(
            LocalNavAnimatedVisibilityScope provides this@composable
        ) {
            content(it)
        }
    }
}
```

This pattern ensures every destination receives the `AnimatedVisibilityScope` from the `NavHost`'s `composable` lambda receiver.

**Sources:** [Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/Home.kt:86-125]()

---

## Filter Screen Shared Element

In addition to snack transitions, Jetsnack implements a separate shared element for the filter button/screen:

```mermaid
graph LR
    subgraph "Feed Screen"
        FB["FilterBar IconButton"]
        KEY1["FilterSharedElementKey"]
    end
    
    subgraph "Filter Screen"
        FS["FilterScreen Column"]
        KEY2["FilterSharedElementKey"]
    end
    
    FB -.sharedBounds.-> KEY1
    FS -.sharedBounds.-> KEY2
    KEY1 -.matches.-> KEY2
    
    FB -->|"AnimatedVisibility(false → true)"| FS
```

This uses a single object key `FilterSharedElementKey` since there's only one filter UI that transitions. The filter button morphs into the filter modal dialog.

**Sources:** [Jetsnack/app/src/main/java/com/example/jetsnack/ui/SnackSharedElementKey.kt:29](), [Jetsnack/app/src/main/java/com/example/jetsnack/ui/components/Filters.kt:77-81](), [Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/FilterScreen.kt:112-117]()

---

