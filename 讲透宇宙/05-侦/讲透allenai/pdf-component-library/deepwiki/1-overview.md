<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/pdf-component-library · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.skiff/cloudbuild-deploy.yaml](.skiff/cloudbuild-deploy.yaml)
- [.skiff/util.libsonnet](.skiff/util.libsonnet)
- [README.md](README.md)
- [docker-compose.yaml](docker-compose.yaml)
- [ui/library/dist/index.d.ts](ui/library/dist/index.d.ts)
- [ui/library/dist/package.json](ui/library/dist/package.json)
- [ui/library/dist/pdf-components.css](ui/library/dist/pdf-components.css)
- [ui/library/dist/pdf-components.js](ui/library/dist/pdf-components.js)

</details>



This document provides a comprehensive overview of the PDF Component Library repository, a React-based system for displaying PDF documents with interactive features. The library is built on top of react-pdf and provides enhanced functionality for creating research-focused PDF reading experiences.

For information about the specific component APIs and usage patterns, see [Library API and Public Interface](#2.1). For details about the styling system, see [Styling System](#3). For build and deployment processes, see [Development and Build System](#5).

## System Purpose and Architecture

The PDF Component Library serves as a foundational system for building interactive PDF readers in React applications. It provides a layered rendering approach where PDF pages are displayed with multiple interactive layers: a background image layer, a transparent text selection layer, and an overlay layer for interactive elements like citations and highlights.

### High-Level System Architecture

```mermaid
graph TB
    subgraph "Published Library (@allenai/pdf-components)"
        DIST["dist/pdf-components.js<br/>dist/pdf-components.css<br/>dist/index.d.ts"]
        LIB_SRC["ui/library/src/"]
    end
    
    subgraph "Core Components"
        DOCWRAP["DocumentWrapper"]
        PAGEWRAP["PageWrapper"] 
        BBOX["BoundingBox"]
        OVERLAY["Overlay"]
        OUTLINE["Outline"]
        THUMB["Thumbnail"]
    end
    
    subgraph "Context System"
        CTXPROV["ContextProvider"]
        DOCCTX["DocumentContext"]
        SCROLLCTX["ScrollContext"]
        TRANSFORM["TransformContext"]
        UICTX["UiContext"]
        RENDER["PageRenderContext"]
    end
    
    subgraph "Demo Application"
        DEMO["ui/demo/"]
        READER["Reader Component"]
        CITATION["CitationPopover"]
    end
    
    subgraph "External Dependencies"
        REACTPDF["react-pdf"]
        PDFJS["PDF.js"]
        REACT["React"]
    end
    
    subgraph "Build & Deploy"
        WEBPACK["webpack.config.js"]
        DOCKER["docker-compose.yaml"]
        CLOUDBUILD[".skiff/cloudbuild-deploy.yaml"]
    end
    
    LIB_SRC --> DIST
    DIST --> DEMO
    
    CTXPROV --> DOCCTX
    CTXPROV --> SCROLLCTX
    CTXPROV --> TRANSFORM
    CTXPROV --> UICTX
    CTXPROV --> RENDER
    
    DOCWRAP --> PAGEWRAP
    PAGEWRAP --> OVERLAY
    OVERLAY --> BBOX
    
    DEMO --> READER
    READER --> CITATION
    
    DOCWRAP --> REACTPDF
    REACTPDF --> PDFJS
    CTXPROV --> REACT
    
    WEBPACK --> DIST
    DOCKER --> DEMO
    CLOUDBUILD --> DOCKER
```

**Sources**: [ui/library/dist/package.json:1-8](), [ui/library/dist/index.d.ts:7-43](), [docker-compose.yaml:1-25](), [.skiff/cloudbuild-deploy.yaml:1-93]()

## Core Library Components

The library exports a comprehensive set of React components organized into functional categories. The main entry point provides both individual components and a default export containing all functionality.

### Component Hierarchy and Relationships

```mermaid
graph TD
    CP["ContextProvider<br/>(src/context/ContextProvider)"] --> DW["DocumentWrapper<br/>(src/components/DocumentWrapper)"]
    DW --> PW["PageWrapper<br/>(src/components/PageWrapper)"]
    PW --> OV["Overlay<br/>(src/components/Overlay)"]
    PW --> HO["HighlightOverlay<br/>(src/components/HighlightOverlay)"]
    OV --> BB["BoundingBox<br/>(src/components/BoundingBox)"]
    HO --> BB
    
    CP --> OUT["Outline<br/>(src/components/outline/Outline)"]
    OUT --> OI["OutlineItem<br/>(src/components/outline/OutlineItem)"]
    
    CP --> TL["ThumbnailList<br/>(src/components/thumbnails/ThumbnailList)"]
    TL --> TH["Thumbnail<br/>(src/components/thumbnails/Thumbnail)"]
    
    CP --> SP["SidePanel<br/>(src/components/SidePanel)"]
    CP --> PNC["PageNumberControl<br/>(src/components/PageNumberControl)"]
    CP --> ZIB["ZoomInButton<br/>(src/components/ZoomInButton)"]
    CP --> ZOB["ZoomOutButton<br/>(src/components/ZoomOutButton)"]
    
    BB --> AF["ArrowFlag<br/>(src/components/marker/ArrowFlag)"]
    BB --> AFB["ArrowFlagBase<br/>(src/components/marker/ArrowFlagBase)"]
    BB --> IF["IconFlag<br/>(src/components/icon/IconFlag)"]
```

**Sources**: [ui/library/dist/index.d.ts:44-113](), [ui/library/dist/index.d.ts:116-414]()

The `DocumentWrapper` serves as the primary container component that initializes PDF loading and sets up the rendering infrastructure. The `PageWrapper` handles individual page rendering with support for multiple render types defined in `RENDER_TYPE` constants (`MULTI_CANVAS` and `SINGLE_CANVAS`).

## Context System Architecture

The library implements a sophisticated React Context system for state management across the component hierarchy. The `ContextProvider` orchestrates five specialized contexts that manage different aspects of the PDF reading experience.

### Context Data Flow and Dependencies

```mermaid
graph LR
    subgraph "External Data Sources"
        PDF["PDF Document"]
        USER["User Interactions"]
        API["Browser APIs"]
    end
    
    subgraph "Context Providers"
        DOC["DocumentContext<br/>• numPages: number<br/>• outline: OutlineNode[]<br/>• pageDimensions: Dimensions<br/>• pdfDocProxy: PDFDocumentProxy"]
        
        SCROLL["ScrollContext<br/>• visiblePageRatios: Map<br/>• scrollDirection: ScrollDirection<br/>• isPageVisible()<br/>• scrollToPage()"]
        
        TRANS["TransformContext<br/>• scale: number<br/>• rotation: PageRotation<br/>• pixelRatio: number<br/>• DEFAULT_ZOOM_SCALE"]
        
        UI["UiContext<br/>• isLoading: boolean<br/>• isShowingOutline: boolean<br/>• isShowingThumbnail: boolean<br/>• errorMessage: string"]
        
        RENDER["PageRenderContext<br/>• pageRenderStates: Map<br/>• getObjectURLForPage()<br/>• buildObjectURLForPage()"]
    end
    
    subgraph "Component Consumers"
        COMP["React Components<br/>DocumentWrapper<br/>PageWrapper<br/>BoundingBox<br/>Thumbnail"]
    end
    
    PDF --> DOC
    USER --> SCROLL
    USER --> TRANS
    USER --> UI
    API --> SCROLL
    
    DOC --> RENDER
    TRANS --> RENDER
    SCROLL --> RENDER
    
    DOC -.-> COMP
    SCROLL -.-> COMP  
    TRANS -.-> COMP
    UI -.-> COMP
    RENDER -.-> COMP
```

**Sources**: [ui/library/dist/index.d.ts:424-447](), [ui/library/dist/index.d.ts:479-508](), [ui/library/dist/index.d.ts:510-526](), [ui/library/dist/index.d.ts:528-547](), [ui/library/dist/index.d.ts:450-477]()

The `ScrollContext` implements sophisticated visibility detection using `IntersectionObserver` APIs through the `VisibleEntriesDetector` class. The `PageRenderContext` manages canvas-based page image generation with priority queuing for visible pages, while the `DocumentContext` handles PDF.js integration for document loading and outline processing.

## Utility Systems and Helper Functions

The library includes several utility modules that provide core functionality for coordinate transformations, scroll management, and style calculations.

| Utility Module | Key Functions | Purpose |
|---|---|---|
| `src/utils/scroll` | `generatePageIdFromIndex()`, `scrollToId()`, `scrollToPdfPageIndex()` | Page navigation and scroll management |
| `src/utils/style` | `computeBoundingBoxStyle()`, `computePageStyle()`, `getPageHeight()` | CSS style calculations with rotation support |
| `src/utils/rotate` | `rotateClockwise()`, `rotateCounterClockwise()`, `isSideways()` | Page rotation transformations |
| `src/utils/format` | `PercentFormatter` | Number formatting utilities |

**Sources**: [ui/library/dist/index.d.ts:580-620](), [ui/library/dist/index.d.ts:622-629](), [ui/library/dist/index.d.ts:564-578](), [ui/library/dist/index.d.ts:549-551]()

## Demo Application Structure

The demo application located in `ui/demo/` serves as both a reference implementation and testing environment for the library components. It demonstrates integration patterns and advanced features like citation popovers.

### Demo Application Architecture

```mermaid
graph TB
    subgraph "Demo Components (ui/demo)"
        READER["Reader Component"]
        HEADER["Header Component"] 
        CITATION["CitationPopover"]
        THUMB_DEMO["Thumbnail Demo"]
    end
    
    subgraph "Core Library Integration"
        CP_DEMO["ContextProvider"] --> READER
        DW_DEMO["DocumentWrapper"] --> READER
        PW_DEMO["PageWrapper"] --> READER
    end
    
    subgraph "Demo-Specific Features"
        CITATION --> SEMANTIC["Semantic Scholar API"]
        READER --> HYPO["Hypothesis.io Integration"]
    end
    
    subgraph "Build Assets"
        WEBPACK_DEMO["webpack.config.js"] --> BUILD["demo/build/"]
        CSS_DEMO["reader.less"] --> BUILD
        COLORS["colors.less"] --> BUILD
    end
    
    READER --> CP_DEMO
    BUILD --> DOCKER_UI["Docker UI Service"]
```

**Sources**: [docker-compose.yaml:8-13](), [README.md:27-35]()

## Build and Deployment Pipeline

The system uses a multi-stage build process with Docker containerization and Google Cloud Build for CI/CD automation.

### Build Process Flow

```mermaid
graph TD
    subgraph "Development"
        SRC["Source Code<br/>ui/library/src/"] --> BUILD_LIB["yarn build<br/>(ui/library)"]
        BUILD_LIB --> DIST_LIB["dist/ artifacts<br/>pdf-components.js<br/>pdf-components.css"]
    end
    
    subgraph "Demo Build"
        DEMO_SRC["ui/demo/src/"] --> BUILD_DEMO["yarn build<br/>(ui/demo)"]
        BUILD_DEMO --> DEMO_DIST["demo/build/"]
    end
    
    subgraph "Docker Services" 
        DOCKERFILE_UI["ui/Dockerfile"] --> UI_IMAGE["UI Docker Image"]
        DOCKERFILE_PROXY["proxy/Dockerfile"] --> PROXY_IMAGE["Proxy Docker Image"]
        COMPOSE["docker-compose.yaml"] --> LOCAL["localhost:8080"]
    end
    
    subgraph "CI/CD Pipeline"
        CLOUDBUILD[".skiff/cloudbuild-deploy.yaml"] --> GCR["Google Container Registry"]
        GCR --> K8S["Kubernetes Deployment"]
    end
    
    DIST_LIB --> DEMO_SRC
    DEMO_DIST --> DOCKERFILE_PROXY
    UI_IMAGE --> COMPOSE
    PROXY_IMAGE --> COMPOSE
    
    UI_IMAGE --> CLOUDBUILD
    PROXY_IMAGE --> CLOUDBUILD
```

**Sources**: [docker-compose.yaml:1-25](), [.skiff/cloudbuild-deploy.yaml:4-85](), [README.md:40-51]()

The build system produces distributable npm packages through `npm pack` and supports local development through Docker Compose with volume mounting for hot reloading. The CI/CD pipeline automatically deploys to production environments using Google Cloud Build and Kubernetes orchestration.

---

