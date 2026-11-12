<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/pdf-component-library · page 4 Demo Application · fetched 2026-10-26 -->

# Demo Application

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ui/demo/components/Header.tsx](ui/demo/components/Header.tsx)
- [ui/demo/components/Reader.tsx](ui/demo/components/Reader.tsx)
- [ui/library/index.ts](ui/library/index.ts)

</details>



The demo application serves as a comprehensive showcase and testing environment for the PDF Component Library. It demonstrates the library's capabilities through a fully functional PDF reader that includes interactive features like citations, highlights, outline navigation, and thumbnails. The demo is located in [ui/demo/]() and provides both a usage example for developers and a testing platform for library features.

For information about the core library components being demonstrated, see [Core PDF Components Library](#2). For build and deployment details, see [Development and Build System](#5).

## Demo Application Architecture

The demo application is structured as a React application that consumes the `@allenai/pdf-components` library. It showcases advanced features through specialized demo components while maintaining the same architectural patterns as the core library.

**Demo Application Structure**
```mermaid
graph TD
    subgraph "Demo Application (ui/demo)"
        Reader["Reader.tsx<br/>Main demo component"]
        Header["Header.tsx<br/>Control panel"]
        DemoContext["DemoHeaderContext<br/>Demo-specific state"]
    end
    
    subgraph "Demo Feature Components"
        CitationsDemo["CitationsDemo<br/>Citation popovers"]
        HighlightDemo["HighlightOverlayDemo<br/>Highlight regions"]
        TextHighlightDemo["TextHighlightDemo<br/>Text selection"]
        ScrollToDemo["ScrollToDemo<br/>Navigation demo"]
        NoteTakingDemo["NoteTakingDemo<br/>Annotation features"]
    end
    
    subgraph "Core Library (@allenai/pdf-components)"
        DocumentWrapper["DocumentWrapper<br/>PDF loader"]
        PageWrapper["PageWrapper<br/>Page renderer"]
        Overlay["Overlay<br/>Interactive layer"]
        Contexts["Context System<br/>State management"]
    end
    
    subgraph "External Services"
        ArxivPDF["ArXiv PDF<br/>Sample document"]
        S2API["Semantic Scholar API<br/>Citation data"]
    end
    
    Reader --> Header
    Reader --> DemoContext
    Reader --> DocumentWrapper
    Reader --> PageWrapper
    Reader --> Overlay
    
    Overlay --> CitationsDemo
    Overlay --> HighlightDemo
    Overlay --> TextHighlightDemo
    Overlay --> ScrollToDemo
    
    Reader --> NoteTakingDemo
    Header --> Contexts
    
    Reader --> ArxivPDF
    Reader --> S2API
    
    CitationsDemo --> S2API
```

Sources: [ui/demo/components/Reader.tsx:1-106](), [ui/demo/components/Header.tsx:1-84]()

## Main Reader Component

The `Reader` component serves as the root of the demo application, orchestrating PDF loading, data fetching, and component rendering. It demonstrates integration patterns for consuming the PDF Component Library.

**Reader Component Data Flow**
```mermaid
graph LR
    subgraph "External Data Sources"
        PDF["samplePdfUrl<br/>arxiv.org/pdf/2112.07873.pdf"]
        API["sampleS2airsUrl<br/>s2airs.prod.s2.allenai.org"]
    end
    
    subgraph "Reader State Management"
        State["Reader Component State"]
        Annotations["annotations<br/>PageToAnnotationsMap"]
        RawCitations["rawCitations<br/>RawCitation[]"]
        Refs["Component Refs<br/>pdfContentRef<br/>pdfScrollableRef"]
    end
    
    subgraph "Context Integration"
        DocumentContext["DocumentContext<br/>pageDimensions, numPages"]
        ScrollContext["ScrollContext<br/>setScrollRoot"]
    end
    
    subgraph "Rendered Components"
        DocumentWrapper["DocumentWrapper<br/>PDF container"]
        PageLoop["Page Array.map<br/>PageWrapper loop"]
        DemoComponents["Demo Feature Components<br/>CitationsDemo, HighlightDemo"]
    end
    
    PDF --> State
    API --> RawCitations
    RawCitations --> Annotations
    DocumentContext --> Annotations
    
    State --> DocumentWrapper
    State --> PageLoop
    Annotations --> DemoComponents
    Refs --> DemoComponents
    
    ScrollContext --> State
```

The Reader component implements several key patterns:

| Pattern | Implementation | Purpose |
|---------|----------------|---------|
| Data Fetching | [ui/demo/components/Reader.tsx:43-54]() | Loads citation data from Semantic Scholar API |
| State Management | [ui/demo/components/Reader.tsx:28-31]() | Manages annotations and citations state |
| Context Integration | [ui/demo/components/Reader.tsx:26-27]() | Consumes library contexts for PDF metadata |
| Component Composition | [ui/demo/components/Reader.tsx:84-97]() | Renders pages with overlay demos |

Sources: [ui/demo/components/Reader.tsx:25-106]()

## Demo Header and Controls

The `Header` component provides a control panel that demonstrates various library features through toggle buttons and navigation controls. It showcases integration with both library contexts and demo-specific state.

**Header Control Integration**
```mermaid
graph TD
    subgraph "Header Component"
        HeaderControls["Header.tsx<br/>Control panel"]
    end
    
    subgraph "Library Context Integration"
        UiContext["UiContext<br/>isShowingOutline<br/>isShowingThumbnail<br/>isShowing*Highlight"]
        PageNumberControl["PageNumberControl<br/>Page navigation"]
        DownloadButton["DownloadButton<br/>PDF download"]
    end
    
    subgraph "Demo-Specific Context"
        DemoHeaderContext["DemoHeaderContext<br/>isShowingNoteTaking"]
    end
    
    subgraph "Utility Functions"
        ScrollUtils["scrollToId<br/>Navigation utilities"]
        SimpleZoomControl["SimpleZoomControl<br/>Zoom controls"]
    end
    
    subgraph "Feature Toggles"
        OutlineToggle["handleShowOutline<br/>Toggle outline panel"]
        ThumbnailToggle["handleShowThumbnail<br/>Toggle thumbnail panel"]
        HighlightToggles["handleToggle*Highlight<br/>Toggle highlight modes"]
        ScrollToDemo["handleScrollToFigure<br/>Navigate to figure"]
    end
    
    HeaderControls --> UiContext
    HeaderControls --> DemoHeaderContext
    HeaderControls --> PageNumberControl
    HeaderControls --> DownloadButton
    HeaderControls --> SimpleZoomControl
    
    HeaderControls --> OutlineToggle
    HeaderControls --> ThumbnailToggle
    HeaderControls --> HighlightToggles
    HeaderControls --> ScrollToDemo
    
    ScrollToDemo --> ScrollUtils
```

The Header demonstrates key integration patterns:

- **Context Consumption**: [ui/demo/components/Header.tsx:13-23]() shows how to consume both library and demo contexts
- **Mutual Exclusion**: [ui/demo/components/Header.tsx:25-33]() implements logic to ensure only one panel is shown at a time
- **Feature Toggling**: [ui/demo/components/Header.tsx:35-41]() demonstrates toggle patterns for overlay features
- **Utility Integration**: [ui/demo/components/Header.tsx:43-49]() shows how to use library utilities like `scrollToId`

Sources: [ui/demo/components/Header.tsx:12-84](), [ui/library/index.ts:1-7]()

## Demo Feature Components

The demo application includes specialized components that showcase advanced library capabilities. Each component demonstrates specific integration patterns and use cases.

**Demo Component Architecture**
```mermaid
graph TD
    subgraph "Demo Components Layer"
        CitationsDemo["CitationsDemo<br/>Citation popup system"]
        HighlightOverlayDemo["HighlightOverlayDemo<br/>Highlight regions"]
        TextHighlightDemo["TextHighlightDemo<br/>Text selection demo"]
        ScrollToDemo["ScrollToDemo<br/>Navigation targets"]
        NoteTakingDemo["NoteTakingDemo<br/>Annotation interface"]
    end
    
    subgraph "Library Components (Consumed)"
        BoundingBox["BoundingBox<br/>Overlay regions"]
        HighlightOverlay["HighlightOverlay<br/>Highlight renderer"]
        Overlay["Overlay<br/>Interactive layer"]
    end
    
    subgraph "Demo Data Types"
        Annotations["PageToAnnotationsMap<br/>Annotation data"]
        RawCitation["RawCitation[]<br/>Citation metadata"]
        GeneratedCitations["generateCitations()<br/>Data transformation"]
    end
    
    subgraph "Integration Points"
        PageWrapper["PageWrapper<br/>Per-page container"]
        Refs["parentRef<br/>DOM references"]
        PageIndex["pageIndex<br/>Page targeting"]
    end
    
    CitationsDemo --> BoundingBox
    HighlightOverlayDemo --> HighlightOverlay
    TextHighlightDemo --> Overlay
    ScrollToDemo --> BoundingBox
    
    CitationsDemo --> Annotations
    Annotations --> RawCitation
    RawCitation --> GeneratedCitations
    
    PageWrapper --> CitationsDemo
    PageWrapper --> HighlightOverlayDemo
    PageWrapper --> TextHighlightDemo
    PageWrapper --> ScrollToDemo
    
    Refs --> CitationsDemo
    PageIndex --> CitationsDemo
    PageIndex --> HighlightOverlayDemo
    PageIndex --> TextHighlightDemo
    PageIndex --> ScrollToDemo
```

| Demo Component | Purpose | Key Integration |
|----------------|---------|-----------------|
| `CitationsDemo` | Shows citation popovers with external data | Uses `BoundingBox` with API data |
| `HighlightOverlayDemo` | Demonstrates highlight regions | Integrates with `HighlightOverlay` |
| `TextHighlightDemo` | Shows text selection features | Uses text selection APIs |
| `ScrollToDemo` | Navigation target demonstration | Creates scrollable targets |
| `NoteTakingDemo` | Annotation interface example | Separate annotation system |

Sources: [ui/demo/components/Reader.tsx:86-95](), [ui/demo/components/Reader.tsx:14-23]()

## Data Integration and External Services

The demo application demonstrates integration with external data sources, showing how to enhance PDF viewing with contextual information from APIs.

**External Data Integration Flow**
```mermaid
graph LR
    subgraph "Data Sources"
        ArxivPDF["samplePdfUrl<br/>https://arxiv.org/pdf/2112.07873.pdf"]
        S2API["sampleS2airsUrl<br/>s2airs.prod.s2.allenai.org/v1/pdf_data"]
    end
    
    subgraph "Data Processing"
        FetchEffect["useEffect<br/>API data fetching"]
        RawCitations["rawCitations<br/>RawCitation[]"]
        GenerateCitations["generateCitations()<br/>Data transformation"]
        Annotations["annotations<br/>PageToAnnotationsMap"]
    end
    
    subgraph "Context Dependencies"
        PageDimensions["pageDimensions<br/>From DocumentContext"]
        NumPages["numPages<br/>From DocumentContext"]
    end
    
    subgraph "Component Integration"
        DocumentWrapper["DocumentWrapper<br/>PDF rendering"]
        CitationsDemo["CitationsDemo<br/>Citation overlays"]
        PageLoop["Array.from({length: numPages})<br/>Page rendering loop"]
    end
    
    ArxivPDF --> DocumentWrapper
    S2API --> FetchEffect
    FetchEffect --> RawCitations
    RawCitations --> GenerateCitations
    PageDimensions --> GenerateCitations
    GenerateCitations --> Annotations
    
    Annotations --> CitationsDemo
    NumPages --> PageLoop
    PageLoop --> CitationsDemo
```

The data integration demonstrates several important patterns:

- **Conditional Fetching**: [ui/demo/components/Reader.tsx:44-47]() prevents duplicate API requests
- **Dependency Management**: [ui/demo/components/Reader.tsx:62-65]() waits for required context data
- **Data Transformation**: [ui/demo/components/Reader.tsx:67]() converts raw API data to component-ready format
- **Context Synchronization**: [ui/demo/components/Reader.tsx:54]() triggers updates based on PDF dimensions

Sources: [ui/demo/components/Reader.tsx:39-68]()

## Demo Application Usage Patterns

The demo application serves as a reference implementation for common integration patterns when using the PDF Component Library. It demonstrates best practices for component composition, state management, and feature integration.

**Component Composition Pattern**
```mermaid
graph TD
    subgraph "Application Shell"
        BrowserRouter["BrowserRouter<br/>Routing container"]
        Route["Route path='/'<br/>Main route"]
        ReaderContainer["div.reader__container<br/>Layout container"]
    end
    
    subgraph "Context Layers"
        DemoHeaderContextProvider["DemoHeaderContextProvider<br/>Demo-specific context"]
        LibraryContextProvider["ContextProvider (implicit)<br/>Library context system"]
    end
    
    subgraph "Core Structure"
        Header["Header<br/>Control panel"]
        DocumentWrapper["DocumentWrapper<br/>PDF container"]
        MainContent["div.reader__main<br/>Main content area"]
    end
    
    subgraph "Navigation Components"
        Outline["Outline<br/>Document structure"]
        Thumbnail["Thumbnail<br/>Page thumbnails"]
    end
    
    subgraph "Page Rendering"
        PageList["div.reader__page-list<br/>Scrollable container"]
        PageWrapperLoop["PageWrapper (mapped)<br/>Individual pages"]
        OverlaySystem["Overlay + Demo Components<br/>Interactive features"]
    end
    
    BrowserRouter --> Route
    Route --> ReaderContainer
    ReaderContainer --> DemoHeaderContextProvider
    DemoHeaderContextProvider --> Header
    DemoHeaderContextProvider --> DocumentWrapper
    
    DocumentWrapper --> Outline
    DocumentWrapper --> Thumbnail
    DocumentWrapper --> PageList
    PageList --> PageWrapperLoop
    PageWrapperLoop --> OverlaySystem
```

This pattern demonstrates:
- **Context Nesting**: Demo contexts wrap library contexts appropriately
- **Component Hierarchy**: Proper parent-child relationships for PDF components
- **Reference Management**: DOM refs passed to components that need them
- **Conditional Rendering**: Components shown/hidden based on state

Sources: [ui/demo/components/Reader.tsx:70-105]()

---

