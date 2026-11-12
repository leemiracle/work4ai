<!-- source: DeepWiki mcp.deepwiki.com · repo voxel51/fiftyone · page 4 Frontend Architecture · fetched 2026-10-21 -->

# Frontend Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/package.json](app/package.json)
- [app/packages/aggregations/package.json](app/packages/aggregations/package.json)
- [app/packages/app/index.html](app/packages/app/index.html)
- [app/packages/app/package.json](app/packages/app/package.json)
- [app/packages/app/vite.config.ts](app/packages/app/vite.config.ts)
- [app/packages/components/package.json](app/packages/components/package.json)
- [app/packages/core/package.json](app/packages/core/package.json)
- [app/packages/embeddings/package.json](app/packages/embeddings/package.json)
- [app/packages/flashlight/package.json](app/packages/flashlight/package.json)
- [app/packages/looker-3d/package.json](app/packages/looker-3d/package.json)
- [app/packages/looker/package.json](app/packages/looker/package.json)
- [app/packages/map/package.json](app/packages/map/package.json)
- [app/packages/operators/package.json](app/packages/operators/package.json)
- [app/packages/plugins/package.json](app/packages/plugins/package.json)
- [app/packages/relay/package.json](app/packages/relay/package.json)
- [app/packages/state/package.json](app/packages/state/package.json)
- [app/packages/utilities/package.json](app/packages/utilities/package.json)
- [app/yarn.lock](app/yarn.lock)
- [package/db/setup.py](package/db/setup.py)
- [package/desktop/setup.py](package/desktop/setup.py)
- [setup.py](setup.py)

</details>



## Purpose and Scope

This document covers the frontend architecture of the FiftyOne web application, including the React-based user interface, state management systems, media viewing components, and client-side data processing. The frontend is responsible for rendering datasets, managing user interactions, and providing visualization tools for computer vision data.

For backend server architecture and GraphQL APIs, see [Server Architecture](#3). For data model and persistence layers, see [Core Data Model](#2).

## Frontend System Overview

The FiftyOne frontend is built as a modern React application with TypeScript, featuring a component-based architecture with centralized state management and specialized media viewing capabilities.

```mermaid
graph TB
    subgraph "Frontend Application"
        React["React Application<br/>TypeScript + Vite"]
        Recoil["Recoil State Management<br/>Atoms & Selectors"]
        Components["UI Components<br/>Material-UI + Styled"]
    end

    subgraph "Core Systems"
        Looker["Looker System<br/>Media Viewers"]
        Schema["Schema Settings<br/>Field Visibility"]
        Sidebar["Sidebar<br/>Filters & Navigation"]
        Grid["Grid View<br/>Sample Display"]
    end

    subgraph "Data Layer"
        GraphQL["GraphQL Client<br/>Relay Integration"]
        State["Application State<br/>Datasets & Views"]
        Cache["Local Cache<br/>Media & Metadata"]
    end

    subgraph "Media Processing"
        ImageViewer["Image Looker<br/>2D Visualization"]
        VideoPlayer["Video Looker<br/>Timeline & Controls"]
        ThreeDViewer["3D Looker<br/>Point Cloud Viewer"]
        Overlays["Overlay System<br/>Labels & Annotations"]
    end

    React --> Components
    React --> Recoil
    Components --> Looker
    Components --> Schema
    Components --> Sidebar
    Components --> Grid

    Looker --> ImageViewer
    Looker --> VideoPlayer
    Looker --> ThreeDViewer
    Looker --> Overlays

    Recoil --> State
    GraphQL --> State
    State --> Cache

    Components --> GraphQL
```

Sources: [app/packages/looker/src/index.ts:1-29](), [app/packages/state/src/hooks/useSchemaSettings.ts:1-376](), [app/packages/core/src/components/Sidebar/Sidebar.tsx:1-50]()

## State Management Architecture

The frontend uses Recoil for state management, providing a reactive state system with atoms, selectors, and hooks. The state is organized around core entities like datasets, samples, and UI preferences.

```mermaid
graph TB
    subgraph "Recoil State Management"
        Atoms["State Atoms<br/>dataset, filters, modal"]
        Selectors["Derived State<br/>viewSchemaSelector"]
        Hooks["Custom Hooks<br/>useSchemaSettings"]
    end

    subgraph "State Categories"
        DatasetState["Dataset State<br/>datasetName, fieldSchema"]
        UIState["UI State<br/>settingsModal, sidebar"]
        FilterState["Filter State<br/>excludedPaths, visibility"]
        ViewState["View State<br/>selectedSamples, groupBy"]
    end

    subgraph "State Persistence"
        LocalStorage["Browser Storage<br/>Preferences & Settings"]
        Session["Session State<br/>Temporary UI State"]
        URL["URL State<br/>View Parameters"]
    end

    Atoms --> DatasetState
    Atoms --> UIState
    Atoms --> FilterState
    Atoms --> ViewState

    Selectors --> Atoms
    Hooks --> Selectors
    Hooks --> Atoms

    UIState --> LocalStorage
    FilterState --> Session
    ViewState --> URL
```

### Core State Hooks

The `useSchemaSettings` hook manages field visibility and schema-related state:

- **Field Management**: Controls which fields are visible in the UI
- **Search Integration**: Handles field search and filtering
- **Exclusion Logic**: Manages excluded field paths for different view types
- **Tab State**: Controls between selection and filter rule modes

Sources: [app/packages/state/src/hooks/useSchemaSettings.ts:28-375](), [app/packages/state/src/recoil/schemaSettings.atoms.ts:1-50]()

## Looker System Architecture

The Looker system provides media viewing capabilities for different media types with overlay support for annotations and labels.

```mermaid
graph TB
    subgraph "Looker Core"
        LookerIndex["looker/src/index.ts<br/>Main Exports"]
        BaseState["BaseState Interface<br/>Common State Props"]
        StateUpdate["StateUpdate Type<br/>State Management"]
    end

    subgraph "Media Viewers"
        ImageLooker["Image Looker<br/>Static Image Viewing"]
        VideoLooker["Video Looker<br/>Timeline & Controls"]
        FrameLooker["Frame Looker<br/>Video Frame Viewing"]
        ThreeDLooker["3D Looker<br/>Point Cloud Rendering"]
    end

    subgraph "Overlay System"
        Detection["Detection Overlays<br/>Bounding Boxes"]
        Segmentation["Segmentation Overlays<br/>Pixel Masks"]
        Classification["Classification Overlays<br/>Labels & Tags"]
        Keypoint["Keypoint Overlays<br/>Skeletal Data"]
    end

    subgraph "UI Elements"
        Controls["Control Elements<br/>Play/Pause/Seek"]
        Timeline["Timeline Elements<br/>Video Navigation"]
        Options["Options Panel<br/>View Settings"]
        Canvas["Canvas Element<br/>Rendering Surface"]
    end

    LookerIndex --> BaseState
    LookerIndex --> StateUpdate
    BaseState --> ImageLooker
    BaseState --> VideoLooker
    BaseState --> FrameLooker
    BaseState --> ThreeDLooker

    ImageLooker --> Detection
    ImageLooker --> Segmentation
    ImageLooker --> Classification
    VideoLooker --> Detection
    VideoLooker --> Keypoint

    VideoLooker --> Controls
    VideoLooker --> Timeline
    ImageLooker --> Options
    ThreeDLooker --> Canvas
```

### Media State Management

Each media type extends the base state with specific properties:

- **ImageState**: Basic zoom and pan controls
- **VideoState**: Frame navigation, playback controls, buffering
- **FrameState**: Individual frame viewing with frame-specific options
- **ThreeDState**: 3D rendering controls and camera positioning

Sources: [app/packages/looker/src/state.ts:1-525](), [app/packages/looker/src/overlays/detection.ts:1-372](), [app/packages/looker/src/overlays/segmentation.ts:1-287]()

## Schema Settings System

The schema settings system manages field visibility and provides advanced filtering capabilities for dataset fields.

```mermaid
graph TB
    subgraph "Schema Settings UI"
        SettingsModal["SchemaSettings.tsx<br/>Modal Component"]
        SearchComponent["SchemaSearch.tsx<br/>Field Search UI"]
        SelectionComponent["SchemaSelection.tsx<br/>Field Selection UI"]
    end

    subgraph "State Management"
        SettingsHook["useSchemaSettings Hook<br/>Core Logic"]
        SearchHook["useSearchSchemaFields<br/>Search Functionality"]
        VisibilityAtoms["Recoil Atoms<br/>excludedPaths, modal"]
    end

    subgraph "Field Processing"
        FieldSchema["Field Schema<br/>Dataset Structure"]
        PathUtils["Path Utilities<br/>getSubPaths, skipField"]
        DisabledFields["Disabled Field Logic<br/>Metadata & Reserved"]
    end

    subgraph "View Integration"
        FieldVisibilityStage["Field Visibility Stage<br/>ExcludeFields Stage"]
        ViewPipeline["View Pipeline<br/>Applied Exclusions"]
        BackendSync["Backend Synchronization<br/>GraphQL Mutations"]
    end

    SettingsModal --> SearchComponent
    SettingsModal --> SelectionComponent
    SettingsModal --> SettingsHook

    SettingsHook --> SearchHook
    SettingsHook --> VisibilityAtoms
    SearchHook --> FieldSchema

    FieldSchema --> PathUtils
    PathUtils --> DisabledFields
    DisabledFields --> FieldVisibilityStage

    FieldVisibilityStage --> ViewPipeline
    ViewPipeline --> BackendSync
```

### Field Visibility Logic

The system implements sophisticated field visibility rules:

- **Reserved Fields**: System fields like `id`, `filepath`, `metadata` are always disabled
- **Nested Fields**: Supports showing/hiding nested object properties
- **View-Specific Rules**: Different rules for patches, clips, and frame views
- **Search Integration**: Real-time field search with nested field support

Sources: [app/packages/core/src/components/Schema/SchemaSettings.tsx:1-263](), [app/packages/state/src/hooks/useSchemaSettings.utils.ts:1-310]()

## Component Architecture

The frontend follows a hierarchical component structure with clear separation of concerns between presentation and logic.

```mermaid
graph TB
    subgraph "Core Components"
        App["App Component<br/>Root Application"]
        Router["Router<br/>Navigation Logic"]
        Layout["Layout Components<br/>Header, Sidebar, Main"]
    end

    subgraph "View Components"
        Grid["Grid Component<br/>Sample Grid View"]
        Modal["Modal Component<br/>Sample Detail View"]
        Dataset["Dataset Component<br/>Dataset Overview"]
    end

    subgraph "Sidebar System"
        SidebarMain["Sidebar.tsx<br/>Main Container"]
        FilterEntry["FilterEntry.tsx<br/>Filter Controls"]
        Draggable["Draggable.tsx<br/>Drag & Drop"]
    end

    subgraph "Schema Components"
        SchemaSettings["SchemaSettings.tsx<br/>Field Visibility Modal"]
        SchemaSearch["SchemaSearch.tsx<br/>Field Search"]
        SchemaSelection["SchemaSelection.tsx<br/>Field Selection"]
    end

    subgraph "Looker Integration"
        LookerComponent["Looker Components<br/>Media Viewers"]
        OverlayComponents["Overlay Components<br/>Label Rendering"]
        ControlComponents["Control Components<br/>Media Controls"]
    end

    App --> Router
    Router --> Layout
    Layout --> Grid
    Layout --> Modal
    Layout --> Dataset

    Layout --> SidebarMain
    SidebarMain --> FilterEntry
    SidebarMain --> Draggable

    Modal --> SchemaSettings
    SchemaSettings --> SchemaSearch
    SchemaSettings --> SchemaSelection

    Grid --> LookerComponent
    Modal --> LookerComponent
    LookerComponent --> OverlayComponents
    LookerComponent --> ControlComponents
```

### Sidebar Architecture

The sidebar implements a sophisticated drag-and-drop interface for field management:

- **Entry Types**: Different entry types for groups, paths, empty states, and inputs
- **Interactive Items**: Draggable items with spring animations
- **Measurement System**: Dynamic height calculation and positioning
- **Event Handling**: Keyboard navigation and mouse interactions

Sources: [app/packages/core/src/components/Sidebar/Sidebar.tsx:24-153](), [app/packages/core/src/components/Sidebar/Entries/FilterEntry.tsx:1-160]()

## Media Overlay System

The overlay system renders labels and annotations over media content with interactive capabilities.

```mermaid
graph TB
    subgraph "Overlay Base System"
        BaseOverlay["base.ts<br/>Overlay Interface"]
        CoordinateOverlay["CoordinateOverlay<br/>Abstract Base Class"]
        OverlayTypes["Overlay Types<br/>CONTAINS, PointInfo"]
    end

    subgraph "Label Overlays"
        DetectionOverlay["detection.ts<br/>Bounding Box Rendering"]
        SegmentationOverlay["segmentation.ts<br/>Pixel Mask Rendering"]
        ClassificationOverlay["classifications.ts<br/>Text Label Rendering"]
        HeatmapOverlay["heatmap.ts<br/>Heat Map Rendering"]
    end

    subgraph "Interactive Features"
        Selection["Label Selection<br/>Click Handling"]
        Hover["Hover Effects<br/>Highlight & Tooltip"]
        Filtering["Label Filtering<br/>Visibility Rules"]
        Coloring["Color Management<br/>Field-based Coloring"]
    end

    subgraph "Rendering Pipeline"
        Canvas["Canvas Rendering<br/>2D Context Drawing"]
        Transform["Coordinate Transform<br/>Screen to Image Space"]
        Optimization["Rendering Optimization<br/>Selective Updates"]
    end

    BaseOverlay --> CoordinateOverlay
    CoordinateOverlay --> DetectionOverlay
    CoordinateOverlay --> SegmentationOverlay
    CoordinateOverlay --> ClassificationOverlay
    BaseOverlay --> HeatmapOverlay

    DetectionOverlay --> Selection
    DetectionOverlay --> Hover
    SegmentationOverlay --> Filtering
    ClassificationOverlay --> Coloring

    Selection --> Canvas
    Hover --> Transform
    Filtering --> Canvas
    Coloring --> Optimization
```

### Overlay Rendering Process

Each overlay type implements specific rendering logic:

- **Detection**: Renders bounding boxes with labels and confidence scores
- **Segmentation**: Displays pixel-level masks with color coding
- **Classification**: Shows text labels with background styling
- **Heatmap**: Renders intensity maps with customizable coloring

Sources: [app/packages/looker/src/overlays/base.ts:1-172](), [app/packages/looker/src/overlays/detection.ts:80-356](), [app/packages/looker/src/overlays/segmentation.ts:29-287]()

## Frontend-Backend Integration

The frontend integrates with the backend through GraphQL queries and real-time subscriptions.

```mermaid
graph LR
    subgraph "Frontend State"
        RecoilAtoms["Recoil Atoms<br/>Client State"]
        Selectors["GraphQL Selectors<br/>Data Derivation"]
        Components["React Components<br/>UI Rendering"]
    end

    subgraph "GraphQL Layer"
        Fragments["GraphQL Fragments<br/>viewSchemaFragment"]
        Queries["GraphQL Queries<br/>Dataset & Sample Data"]
        Mutations["GraphQL Mutations<br/>Field Visibility Updates"]
        Subscriptions["Subscriptions<br/>Real-time Updates"]
    end

    subgraph "Backend APIs"
        GraphQLServer["GraphQL Server<br/>Schema & Resolvers"]
        SessionManagement["Session Management<br/>State Synchronization"]
        DataServices["Data Services<br/>Dataset Operations"]
    end

    Components --> Selectors
    Selectors --> RecoilAtoms
    Selectors --> Fragments
    
    Fragments --> Queries
    Queries --> GraphQLServer
    Mutations --> SessionManagement
    Subscriptions --> DataServices

    GraphQLServer --> DataServices
    SessionManagement --> DataServices
```

The frontend maintains synchronized state with the backend through:

- **Fragment-based Queries**: Reusable GraphQL fragments for consistent data fetching
- **Optimistic Updates**: Immediate UI updates with backend synchronization
- **Session Persistence**: Maintains view state across browser sessions
- **Real-time Sync**: Live updates when data changes on the server

Sources: [app/packages/state/src/hooks/useSchemaSettings.ts:17-26](), [app/packages/core/src/components/Schema/SchemaSettings.tsx:225-231]()

---

