<!-- source: DeepWiki mcp.deepwiki.com · repo android/wear-os-samples · page 7 Tiles · fetched 2026-10-23 -->

# Tiles

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [WearTilesKotlin/app/src/debug/AndroidManifest.xml](WearTilesKotlin/app/src/debug/AndroidManifest.xml)
- [WearTilesKotlin/app/src/main/AndroidManifest.xml](WearTilesKotlin/app/src/main/AndroidManifest.xml)
- [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/Contact.kt](WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/Contact.kt)
- [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingRepo.kt](WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingRepo.kt)
- [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileLayout.kt](WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileLayout.kt)
- [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileService.kt](WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileService.kt)
- [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileTheme.kt](WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileTheme.kt)
- [WearTilesKotlin/app/src/main/res/values-et/strings.xml](WearTilesKotlin/app/src/main/res/values-et/strings.xml)
- [WearTilesKotlin/app/src/main/res/values/strings.xml](WearTilesKotlin/app/src/main/res/values/strings.xml)

</details>



Tiles are glanceable, scannable UI elements that users can add to their Wear OS device to quickly access information or actions without opening a full app. This document covers the implementation of Tiles for Wear OS using the AndroidX Tiles library as demonstrated in the Wear OS Samples repository.

## Overview

Wear OS Tiles provide a way for users to quickly access information or perform actions with a simple swipe from the watch face. Tiles are designed to be lightweight, fast-loading, and focused on specific tasks or information.

```mermaid
graph TD
    subgraph "User Experience"
        U["User swipes from watch face"] --> T["Views Tile"]
        T --> A["Quick interaction/glance"]
    end
    
    subgraph "Implementation Components"
        TS["TileService"] --> TR["Tile Rendering"]
        TR --> TL["Tile Layout"]
        TR --> TR["Tile Resources"]
        TS --> TD["Tile Data Source"]
    end
    
    U -.-> TS
```

Sources: [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileService.kt:40-48]()

## Tile Architecture

The Tile architecture consists of several key components working together to create a responsive and efficient UI element:

```mermaid
graph TD
    subgraph "AndroidManifest Registration"
        M["Service Declaration"] --> MP["Permission: BIND_TILE_PROVIDER"]
        M --> MI["Intent Filter: androidx.wear.tiles.action.BIND_TILE_PROVIDER"]
        M --> MM["Metadata: PREVIEW"]
    end
    
    subgraph "Core Components"
        TS["SuspendingTileService"] --> TR["tileRequest()"]
        TS --> RR["resourcesRequest()"]
        
        TR --> TL["LayoutElement"]
        TR --> TT["Timeline"]
        
        RR --> RS["Resources"]
    end
    
    subgraph "Data Layer"
        DS["Data Source/Repository"] --> SF["StateFlow"]
        SF --> TR
    end
    
    M --> TS
```

Sources: 
- [WearTilesKotlin/app/src/main/AndroidManifest.xml:30-44]()
- [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileService.kt:49-68]()
- [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileService.kt:72-78]()

### Key Concepts

1. **TileService**: The foundation of a Tile implementation, responsible for providing layout and resources.
2. **Timeline**: Represents what content should be shown in the Tile at different points in time.
3. **LayoutElement**: The UI structure for the Tile.
4. **Resources**: Images and other resources used by the Tile.

## Creating a Tile Service

To implement a Tile, you need to create a service that extends `SuspendingTileService`. This class provides a coroutine-friendly wrapper around the standard `TileService`.

### Service Declaration

The Tile service must be declared in the AndroidManifest.xml with the appropriate permission and intent filter:

```xml
<service
    android:name="com.example.wear.tiles.messaging.MessagingTileService"
    android:exported="true"
    android:label="@string/tile_messaging_label"
    android:description="@string/tile_messaging_description"
    android:icon="@drawable/ic_message_24"
    android:permission="com.google.android.wearable.permission.BIND_TILE_PROVIDER">
    <intent-filter>
        <action android:name="androidx.wear.tiles.action.BIND_TILE_PROVIDER" />
    </intent-filter>

    <meta-data
        android:name="androidx.wear.tiles.PREVIEW"
        android:resource="@drawable/tile_messaging" />
</service>
```

Sources: [WearTilesKotlin/app/src/main/AndroidManifest.xml:30-44]()

### Implementing Core Methods

A Tile service needs to implement two main methods:

1. **tileRequest()**: Provides the layout for the Tile.
2. **resourcesRequest()**: Provides resources (like images) needed by the Tile.

```mermaid
sequenceDiagram
    participant System as "System"
    participant TileService as "SuspendingTileService"
    participant Repository as "Data Repository"
    participant Layout as "Layout Builder"
    
    System->>TileService: Request tile update
    activate TileService
    
    TileService->>Repository: Request latest data
    Repository-->>TileService: Return data
    
    TileService->>Layout: Create layout with data
    Layout-->>TileService: Return LayoutElement
    
    TileService->>TileService: Create Timeline with layout
    TileService-->>System: Return Tile with Timeline
    deactivate TileService
    
    System->>TileService: Request resources
    activate TileService
    TileService->>Repository: Fetch resources (e.g., images)
    Repository-->>TileService: Return resources
    TileService-->>System: Return Resources object
    deactivate TileService
```

Sources: 
- [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileService.kt:72-78]()
- [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileService.kt:111-138]()

## Implementation Example: Messaging Tile

The samples repository includes a Messaging Tile example that demonstrates how to create a functional Tile service.

### Architecture Overview

```mermaid
graph TD
    subgraph "MessagingTileService"
        MTS["MessagingTileService"] --> TR["tileRequest()"]
        MTS --> RR["resourcesRequest()"]
        MTS --> LTS["latestTileState()"]
        MTS --> RD["refreshData()"]
        MTS --> FAN["fetchAvatarsFromNetwork()"]
    end
    
    subgraph "Data Management"
        MR["MessagingRepo"] --> GFC["getFavoriteContacts()"]
        MR --> UC["updateContacts()"]
        MR --> DS["DataStore<Preferences>"]
        C["Contact"] --> PS["toPreferenceString()"]
    end
    
    subgraph "UI Components"
        MTL["messagingTileLayout()"] --> PL["PrimaryLayout"]
        MTL --> MBL["MultiButtonLayout"]
        MTL --> CL["contactLayout()"]
        MTL --> SL["searchLayout()"]
        MTL --> CC["CompactChip"]
    end
    
    subgraph "Styling"
        MTT["MessagingTileTheme"] --> TC["colors"]
    end
    
    MTS --> MR
    MTS --> MTL
    TR --> MTL
    RR --> FAN
```

Sources: 
- [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileService.kt:49-172]()
- [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileLayout.kt:43-73]()
- [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingRepo.kt:31-49]()

### Data Flow

1. The system requests an update from `MessagingTileService`.
2. The service retrieves contact data from `MessagingRepo`.
3. Contact data is used to build a layout with the `messagingTileLayout()` function.
4. The layout contains buttons for each contact, a search button, and a "New" action chip.
5. When resources are requested, the service fetches avatar images for contacts.

```mermaid
flowchart TD
    subgraph "Data Layer"
        DS["DataStore"] --> MR["MessagingRepo"]
        MR --> SF["StateFlow<MessagingTileState>"]
    end
    
    subgraph "Service Layer"
        SF --> MTS["MessagingTileService"]
        MTS --> TRQ["tileRequest()"]
        MTS --> RRQ["resourcesRequest()"]
    end
    
    subgraph "UI Layer"
        TRQ --> MTL["messagingTileLayout()"]
        MTL --> TL["Tile Layout"]
        
        RRQ --> R["Resources"]
        R --> I["Images (avatars, icons)"]
    end
    
    subgraph "System"
        S["System"] --> MTS
        TL --> U["User Interface"]
        I --> U
    end
```

Sources: 
- [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileService.kt:54-66]()
- [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileService.kt:72-78]()
- [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileService.kt:83-90]()

### Key Components

#### MessagingTileService

This is the main class that implements the Tile functionality:

- Extends `SuspendingTileService`
- Manages a `StateFlow` of `MessagingTileState` to track contacts data
- Implements `tileRequest()` to provide the Tile layout
- Implements `resourcesRequest()` to provide images (avatars and icons)

Sources: [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileService.kt:49-172]()

#### MessagingTileLayout

Defines the UI structure for the Messaging Tile:

- Uses `PrimaryLayout` as the root component
- Contains a `MultiButtonLayout` for contact buttons and search button
- Includes a `CompactChip` for the "New" action
- Adapts to different screen sizes using responsive design

Sources: [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileLayout.kt:43-73]()

#### MessagingRepo

Manages the data for the Tile:

- Uses DataStore to persist contact information
- Provides a `Flow` of contact data
- Includes methods to update contacts

Sources: [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingRepo.kt:31-49]()

### Tile UI Architecture

The Messaging Tile demonstrates a common pattern for Tile UIs:

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| PrimaryLayout | Root container | Provides content area and chip area |
| MultiButtonLayout | Contact grid | Displays contact buttons in a grid |
| Button | Contact entry | Shows contact avatar or initials |
| CompactChip | Primary action | Provides a "New" action |

Sources: 
- [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileLayout.kt:43-73]()
- [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileLayout.kt:74-90]()
- [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileLayout.kt:92-99]()

## Resource Management

Tiles need to manage resources efficiently, especially images that may be loaded from the network.

### Resource Handling

The `resourcesRequest()` method is responsible for providing resources to the Tile:

```mermaid
flowchart TD
    RR["resourcesRequest()"] --> FR["Fetch required resources"]
    FR --> RT["Return Resources object"]
    
    subgraph "Image Resource Types"
        L["Local drawable resources"] --> R["Resources object"]
        N["Network images (avatars)"] --> R
    end
    
    subgraph "Resource Loading"
        IL["imageLoader.loadAvatar()"] --> B["Bitmap"]
        B --> AM["addIdToImageMapping()"]
        AM --> R
    end
```

Sources: 
- [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileService.kt:111-138]()
- [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileService.kt:144-166]()

### Resource Versioning

The sample includes a debug flag `DEBUG_RESOURCES` that forces the Tile to reload resources on each update by changing the resources version. In a production environment, you would want to use a stable versioning strategy.

Sources: [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileService.kt:72-78]()

## Best Practices

Based on the sample implementation, here are some best practices for Tile development:

1. **Use Coroutines**: The `SuspendingTileService` makes it easier to work with asynchronous operations.

2. **Responsive Design**: Adapt to different screen sizes, as shown in the Messaging Tile layout:
   ```kotlin
   // A PrimaryLayout with a compact chip can fit 5 buttons (including search)
   // on "small" displays, 6 on "large" displays.
   val isLarge = deviceParameters.screenHeightDp >= 225
   state.contacts.take(if (isLarge) 5 else 4).forEach { contact ->
       addButtonContent(contactLayout(context, contact, emptyClickable))
   }
   ```

3. **Efficient Resource Management**: Load and cache resources efficiently to minimize memory usage.

4. **State Management**: Use Kotlin Flow for reactive state updates.

5. **Preview Support**: Provide preview images and implement preview functions to make your Tile visible in the Wear OS tile picker.

Sources: 
- [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileLayout.kt:52-57]()
- [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileService.kt:54-66]()
- [WearTilesKotlin/app/src/main/AndroidManifest.xml:41-43]()

## Conclusion

Tiles provide a powerful way to extend your Wear OS app's functionality with glanceable, accessible information. The Wear OS Samples repository demonstrates how to implement Tiles using modern Android development patterns, including coroutines, Flow, and responsive design.

To create your own Tile:

1. Create a service that extends `SuspendingTileService`
2. Implement `tileRequest()` and `resourcesRequest()`
3. Define a UI layout using the Proto Layout DSL
4. Register your service in the AndroidManifest.xml
5. Provide a preview image for the Tile picker

For more detailed information about implementing specific Tile types, see [Messaging Tile Implementation](#7.1).

Sources: 
- [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileService.kt:40-48]()
- [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileService.kt:72-78]()
- [WearTilesKotlin/app/src/main/java/com/example/wear/tiles/messaging/MessagingTileService.kt:111-138]()
- [WearTilesKotlin/app/src/main/AndroidManifest.xml:30-44]()

---

