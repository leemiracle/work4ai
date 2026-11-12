<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/scholarphi · page 2 Frontend (UI System) · fetched 2026-10-26 -->

# Frontend (UI System)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ui/jest.config.ts](ui/jest.config.ts)
- [ui/package-lock.json](ui/package-lock.json)
- [ui/package.json](ui/package.json)
- [ui/src/ScholarReader.tsx](ui/src/ScholarReader.tsx)
- [ui/src/selectors/index.ts](ui/src/selectors/index.ts)
- [ui/src/settings.ts](ui/src/settings.ts)
- [ui/src/state.ts](ui/src/state.ts)
- [ui/src/style/equation-diagram.less](ui/src/style/equation-diagram.less)
- [ui/src/types/pdfjs-viewer.ts](ui/src/types/pdfjs-viewer.ts)

</details>



The Frontend (UI System) provides the interactive web interface for Scholar Reader, implementing an augmented PDF viewer built on React and TypeScript. This system integrates PDF.js for document rendering with a sophisticated annotation overlay system that displays extracted entities (symbols, citations, equations, terms) as interactive elements overlaid on the PDF pages.

The frontend serves as the primary user interface for browsing academic papers with enhanced navigation and search capabilities. For backend API integration details, see [Backend (API System)](#3). For information about how entities are processed and extracted, see [Data Processing Pipeline](#4).

## Core Architecture

The frontend is built as a single-page React application centered around the `ScholarReader` component, which orchestrates PDF viewing, entity annotation, search functionality, and user interface controls.

### Component Hierarchy

```mermaid
graph TD
    SR["ScholarReader"] --> AO["AppOverlay"]
    SR --> PT["PdfjsToolbar"] 
    SR --> PB["PdfjsBrandbar"]
    SR --> VO["ViewerOverlay"]
    
    VO --> MCP["MainControlPanel"]
    VO --> FB["FindBar"] 
    VO --> ECT["EntityCreationToolbar"]
    VO --> TSM["TextSelectionMenu"]
    VO --> DW["Drawer"]
    VO --> DP["DefinitionPreview"]
    
    SR --> PP["PrimerPage"]
    SR --> PO["PageOverlay"]
    
    PO --> EAL["EntityAnnotationLayer"]
    PO --> SPM["SearchPageMask"]
    PO --> EPM["EntityPageMask"]
    PO --> ED["EquationDiagram"]
```

Sources: [ui/src/ScholarReader.tsx:1-1200]()

### State Management Architecture

```mermaid
graph LR
    subgraph "State Interface"
        S["State"] --> PD["Paper Data"]
        S --> PDF["PDF.js Objects"] 
        S --> UI["UI State"]
        S --> SET["Settings"]
    end
    
    subgraph "Paper Data"
        PD --> E["entities: Entities"]
        PD --> LP["lazyPapers: Map"]
    end
    
    subgraph "PDF.js Objects"
        PDF --> PDFA["pdfViewerApplication"]
        PDF --> PDFD["pdfDocument"] 
        PDF --> PDFV["pdfViewer"]
        PDF --> PAGES["pages: Pages"]
    end
    
    subgraph "UI State"
        UI --> SEL["Selection State"]
        UI --> FIND["Find State"]
        UI --> DRAWER["Drawer State"]
        UI --> SNACK["Snackbar State"]
    end
```

Sources: [ui/src/state.ts:43-149]()

## PDF.js Integration

The frontend integrates Mozilla's PDF.js library to provide core PDF viewing capabilities while extending it with custom annotation overlays.

### PDF Viewer Integration Flow

```mermaid
sequenceDiagram
    participant SR as "ScholarReader"
    participant PDFA as "PDFViewerApplication"  
    participant EB as "EventBus"
    participant PV as "PDFViewer"
    
    SR->>PDFA: "waitForPDFViewerInitialization()"
    PDFA->>SR: "application loaded"
    SR->>PDFA: "set externalServices.supportsIntegratedFind = true"
    SR->>EB: "subscribe to 'documentloaded'"
    SR->>EB: "subscribe to 'pagerendered'"
    EB->>SR: "DocumentLoadedEvent"
    EB->>SR: "PageRenderedEvent"
    SR->>SR: "update state with pages"
```

Sources: [ui/src/ScholarReader.tsx:665-709](), [ui/src/types/pdfjs-viewer.ts:37-154]()

### Page Rendering and Overlay System

Each PDF page gets corresponding overlay components that render annotations on top of the PDF content:

```mermaid
graph TB
    subgraph "Page Rendering"
        PDFJS["PDF.js PageView"] --> PO["PageOverlay"]
        PO --> EAL["EntityAnnotationLayer"]
        PO --> MASKS["Page Masks"]
        
        EAL --> SA["Symbol Annotations"]
        EAL --> CA["Citation Annotations"] 
        EAL --> EA["Equation Annotations"]
        EAL --> TA["Term Annotations"]
        
        MASKS --> SPM["SearchPageMask"]
        MASKS --> EPM["EntityPageMask"]
    end
```

Sources: [ui/src/ScholarReader.tsx:1000-1200]()

## State Management

The `ScholarReader` component manages all application state through React's built-in state management, implementing a flat state structure for performance optimization.

### State Categories

| Category | Properties | Purpose |
|----------|------------|---------|
| **Paper Data** | `entities`, `lazyPapers` | Entity data from API, cached paper metadata |
| **PDF.js Objects** | `pdfViewerApplication`, `pdfDocument`, `pdfViewer`, `pages` | References to PDF.js viewer components |
| **Selection State** | `selectedEntityIds`, `selectedAnnotationIds`, `multiselectEnabled` | User selection tracking |
| **Find State** | `isFindActive`, `findMode`, `findQuery`, `findMatchedEntities` | Search functionality |
| **UI State** | `drawerMode`, `snackbarMode`, `controlPanelShowing` | Interface visibility |

Sources: [ui/src/state.ts:43-149]()

### Entity Data Structure

```mermaid
graph LR
    subgraph "Entity Store"
        E["Entities"] --> ALL["all: string[]"]
        E --> BYID["byId: Record<string, Entity>"]
    end
    
    subgraph "Entity Types"
        BYID --> SYM["Symbol"]
        BYID --> CIT["Citation"]  
        BYID --> EQ["Equation"]
        BYID --> SENT["Sentence"]
        BYID --> TERM["Term"]
    end
```

Sources: [ui/src/state.ts:151-161](), [ui/src/api/types.ts]()

## Settings and Configuration

The frontend uses a flexible settings system that supports presets and runtime configuration.

### Settings Architecture

```mermaid
graph TD
    subgraph "Settings System"
        CS["ConfigurableSetting[]"] --> SC["Setting Controls"]
        PRESETS["Preset[]"] --> GS["getSettings()"]
        GS --> DS["Default Settings"]
        GS --> MERGED["Merged Settings"]
    end
    
    subgraph "Setting Types"
        SC --> FLAG["Flag Settings"]
        SC --> CHOICE["Choice Settings"]
    end
    
    subgraph "Feature Categories"
        MERGED --> PRIMER["Primer Page Features"]
        MERGED --> ANNOT["Annotation Features"]
        MERGED --> SEARCH["Search Features"]
        MERGED --> GLOSS["Gloss Features"]
    end
```

Sources: [ui/src/settings.ts:10-301]()

## Component Integration Patterns

### Event Handling Flow

```mermaid
graph LR
    subgraph "User Interactions"
        CLICK["Entity Click"] --> SEA["selectEntityAnnotation()"]
        SEARCH["Search Trigger"] --> SSS["startTextSearch()"]
        CREATE["Entity Creation"] --> CE["createEntity()"]
    end
    
    subgraph "State Updates"
        SEA --> USS["Update Selection State"]
        SSS --> UFS["Update Find State"] 
        CE --> UES["Update Entity State"]
    end
    
    subgraph "Component Re-renders"
        USS --> RERENDER["Re-render Annotations"]
        UFS --> RERENDER2["Re-render FindBar"]
        UES --> RERENDER3["Re-render Entity Lists"]
    end
```

Sources: [ui/src/ScholarReader.tsx:167-284](), [ui/src/ScholarReader.tsx:583-663]()

### API Integration

The frontend integrates with the backend API for entity data and paper metadata:

```mermaid
graph LR
    subgraph "API Calls"
        LDA["loadDataFromApi()"] --> GDE["getDedupedEntities()"]
        CE["createEntity()"] --> PE["postEntity()"]
        UE["updateEntity()"] --> PATCH["patchEntity()"]
        DE["deleteEntity()"] --> DEL["deleteEntity()"]
    end
    
    subgraph "State Updates"
        GDE --> USS["Update entities state"]
        PE --> ASE["Add entity to state"]
        PATCH --> USE["Update entity in state"]
        DEL --> RSE["Remove entity from state"]
    end
```

Sources: [ui/src/ScholarReader.tsx:711-730](), [ui/src/ScholarReader.tsx:317-542]()

This frontend architecture provides a scalable foundation for the Scholar Reader interface, with clear separation between PDF viewing, entity annotation, search functionality, and user interface controls. The component-based design allows for modular development and testing while maintaining performant rendering through careful state management.

---

