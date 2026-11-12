<!-- source: DeepWiki mcp.deepwiki.com · repo openai/gpt-5-coding-examples · extra page Build System & Asset Management · fetched 2026-10-26 -->

# Build System & Asset Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/asteroid-game/_next/static/CBX4_Ds-gHqKToLKyj8w-/_buildManifest.js](apps/asteroid-game/_next/static/CBX4_Ds-gHqKToLKyj8w-/_buildManifest.js)
- [apps/asteroid-game/_next/static/CBX4_Ds-gHqKToLKyj8w-/_ssgManifest.js](apps/asteroid-game/_next/static/CBX4_Ds-gHqKToLKyj8w-/_ssgManifest.js)
- [apps/asteroid-game/_next/static/chunks/main-661c9648457bfc1f.js](apps/asteroid-game/_next/static/chunks/main-661c9648457bfc1f.js)
- [apps/asteroid-game/_next/static/chunks/webpack-272b44dd0cfe77c4.js](apps/asteroid-game/_next/static/chunks/webpack-272b44dd0cfe77c4.js)

</details>



This document covers the webpack-based build system, code splitting strategy, and static asset management used in the asteroid game application. The build system handles JavaScript bundling, CSS optimization, font loading, and static asset delivery through Next.js's production build pipeline.

For information about the Next.js framework integration, see [Next.js Framework Integration](#3.1.2). For details about typography and styling implementation, see [Typography & Styling System](#3.1.5).

## Build Architecture Overview

The asteroid game uses Next.js's production build system with webpack as the underlying bundler. The build process generates optimized chunks, manifests, and static assets organized under the `_next/static/` directory structure.

```mermaid
graph TB
    subgraph "Build Process"
        BUILD_CONFIG["next.config.js<br/>Build Configuration"]
        WEBPACK["webpack-272b44dd0cfe77c4.js<br/>Webpack Runtime"]
        CODE_SPLITTING["Code Splitting Engine"]
        ASSET_OPTIMIZATION["Asset Optimization"]
    end
    
    subgraph "Generated Artifacts"
        BUILD_MANIFEST["_buildManifest.js<br/>Route & Page Manifest"]
        SSG_MANIFEST["_ssgManifest.js<br/>Static Generation Manifest"]
        MAIN_CHUNK["main-661c9648457bfc1f.js<br/>Core Framework Code"]
        APP_CHUNKS["Application Chunks<br/>Component Code"]
    end
    
    subgraph "Asset Organization"
        STATIC_DIR["/_next/static/"]
        BUILD_ID["CBX4_Ds-gHqKToLKyj8w-/<br/>Build ID Directory"]
        CHUNKS_DIR["chunks/<br/>JavaScript Modules"]
    end
    
    BUILD_CONFIG --> WEBPACK
    WEBPACK --> CODE_SPLITTING
    CODE_SPLITTING --> ASSET_OPTIMIZATION
    
    ASSET_OPTIMIZATION --> BUILD_MANIFEST
    ASSET_OPTIMIZATION --> SSG_MANIFEST
    ASSET_OPTIMIZATION --> MAIN_CHUNK
    ASSET_OPTIMIZATION --> APP_CHUNKS
    
    BUILD_MANIFEST --> STATIC_DIR
    SSG_MANIFEST --> BUILD_ID
    MAIN_CHUNK --> CHUNKS_DIR
    APP_CHUNKS --> CHUNKS_DIR
```

Sources: [apps/asteroid-game/_next/static/CBX4_Ds-gHqKToLKyj8w-/_buildManifest.js:1-1](), [apps/asteroid-game/_next/static/chunks/webpack-272b44dd0cfe77c4.js:1-1]()

## Webpack Runtime & Module System

The webpack runtime system manages module loading, chunk dependencies, and dynamic imports through a sophisticated promise-based loading mechanism.

### Core Runtime Components

| Component | Purpose | Location |
|-----------|---------|----------|
| `webpackChunk_N_E` | Global chunk registry | webpack runtime |
| `r.O` | Chunk ordering system | webpack runtime |
| `r.e` | Dynamic chunk loader | webpack runtime |
| `r.l` | Script tag injection | webpack runtime |
| `r.f.j` | Chunk load promises | webpack runtime |

The webpack runtime implements several key systems:

```mermaid
graph LR
    subgraph "Module Loading"
        MODULE_CACHE["t[moduleId]<br/>Module Cache"]
        MODULE_FACTORY["e[moduleId]<br/>Module Factory"]
        REQUIRE["r(moduleId)<br/>Require Function"]
    end
    
    subgraph "Chunk Management"
        CHUNK_CACHE["e[chunkId]<br/>Chunk Status Cache"]
        CHUNK_LOADER["r.e(chunkId)<br/>Chunk Loader"]
        SCRIPT_INJECTION["r.l()<br/>Script Tag Injection"]
    end
    
    subgraph "Asset Resolution"
        PUBLIC_PATH["r.p = '/asteroid-game/_next/'<br/>Public Path"]
        TRUSTED_TYPES["r.tt()<br/>Trusted Types Policy"]
        URL_CREATION["r.tu()<br/>Script URL Creation"]
    end
    
    REQUIRE --> MODULE_CACHE
    MODULE_FACTORY --> MODULE_CACHE
    CHUNK_LOADER --> CHUNK_CACHE
    CHUNK_LOADER --> SCRIPT_INJECTION
    SCRIPT_INJECTION --> PUBLIC_PATH
    PUBLIC_PATH --> TRUSTED_TYPES
    TRUSTED_TYPES --> URL_CREATION
```

Sources: [apps/asteroid-game/_next/static/chunks/webpack-272b44dd0cfe77c4.js:1-1]()

## Code Splitting & Chunk Strategy

The build system implements automatic code splitting with route-based and dynamic chunking to optimize bundle sizes and loading performance.

### Chunk Organization

The application is split into multiple chunks based on functionality and loading patterns:

```mermaid
graph TD
    subgraph "Entry Chunks"
        WEBPACK_RUNTIME["webpack-272b44dd0cfe77c4.js<br/>Webpack Runtime (68)"]
        MAIN_APP["main-661c9648457bfc1f.js<br/>Next.js Framework (792)"]
    end
    
    subgraph "Route-Based Chunks"
        ERROR_PAGE["_error-*.js<br/>Error Page Component"]
        APP_PAGE["_app-*.js<br/>App Component"]
    end
    
    subgraph "Dynamic Chunks"
        ASYNC_MODULES["Dynamic Import Chunks<br/>Lazy-loaded Components"]
        VENDOR_CHUNKS["Third-party Libraries<br/>node_modules"]
    end
    
    subgraph "Chunk Loading Strategy"
        PRIORITY_LOAD["High Priority<br/>Critical Path"]
        LAZY_LOAD["Lazy Loading<br/>On-demand"]
        PREFETCH["Prefetch<br/>Anticipated Routes"]
    end
    
    WEBPACK_RUNTIME --> MAIN_APP
    MAIN_APP --> ERROR_PAGE
    MAIN_APP --> APP_PAGE
    
    ASYNC_MODULES --> LAZY_LOAD
    VENDOR_CHUNKS --> PRIORITY_LOAD
    ERROR_PAGE --> PREFETCH
```

### Chunk Loading States

The webpack runtime tracks chunk loading with a state management system:

| State | Value | Description |
|-------|-------|-------------|
| Not loaded | `undefined` | Chunk not requested |
| Loading | `[resolve, reject, promise]` | Async loading in progress |
| Loaded | `0` | Successfully loaded |
| Failed | `undefined` | Load failed, cleared from cache |

Sources: [apps/asteroid-game/_next/static/chunks/webpack-272b44dd0cfe77c4.js:1-1](), [apps/asteroid-game/_next/static/chunks/main-661c9648457bfc1f.js:1-1]()

## Build Manifests & Asset Tracking

The build system generates multiple manifest files to track assets, routes, and build metadata for efficient client-side navigation and caching.

### Build Manifest Structure

The `_buildManifest.js` contains route filtering and page information:

```mermaid
graph LR
    subgraph "Build Manifest Components"
        REWRITES["__rewrites<br/>Route Rewrite Rules"]
        STATIC_FILTER["__routerFilterStatic<br/>Static Route Bloom Filter"]
        DYNAMIC_FILTER["__routerFilterDynamic<br/>Dynamic Route Bloom Filter"]
        SORTED_PAGES["sortedPages<br/>Page Route List"]
    end
    
    subgraph "Route Filtering"
        BLOOM_FILTER_STATIC["numItems: 3<br/>errorRate: 0.0001<br/>Static Routes"]
        BLOOM_FILTER_DYNAMIC["numItems: 0<br/>Dynamic Routes"]
    end
    
    subgraph "Page Registry"
        ERROR_ROUTE["/_error<br/>Error Page Handler"]
        APP_ROUTE["/_app<br/>App Wrapper Component"]
    end
    
    STATIC_FILTER --> BLOOM_FILTER_STATIC
    DYNAMIC_FILTER --> BLOOM_FILTER_DYNAMIC
    SORTED_PAGES --> ERROR_ROUTE
    SORTED_PAGES --> APP_ROUTE
```

### SSG Manifest

The Static Site Generation manifest tracks pre-rendered pages:

```javascript
self.__SSG_MANIFEST = new Set([]);
```

This indicates the application uses client-side rendering rather than static generation for this build.

Sources: [apps/asteroid-game/_next/static/CBX4_Ds-gHqKToLKyj8w-/_buildManifest.js:1-1](), [apps/asteroid-game/_next/static/CBX4_Ds-gHqKToLKyj8w-/_ssgManifest.js:1-1]()

## Static Asset Organization

The build system organizes static assets in a hierarchical directory structure under `_next/static/` with build ID-based versioning for cache busting.

### Asset Directory Structure

```mermaid
graph TD
    subgraph "Static Asset Hierarchy"
        ROOT["/_next/static/"]
        BUILD_ID["CBX4_Ds-gHqKToLKyj8w-/<br/>Build ID Directory"]
        CHUNKS["chunks/<br/>JavaScript Modules"]
        CSS["*.css<br/>Stylesheets"]
        FONTS["fonts/<br/>Font Files"]
    end
    
    subgraph "Asset Types"
        JS_CHUNKS["JavaScript Chunks<br/>.js files"]
        CSS_FILES["CSS Bundles<br/>.css files"]
        FONT_FILES["Font Assets<br/>.woff2 files"]
        SOURCE_MAPS["Source Maps<br/>.map files"]
    end
    
    subgraph "Cache Strategy"
        IMMUTABLE["Immutable Assets<br/>Build ID in path"]
        VERSIONED["Version Headers<br/>Long-term caching"]
        INVALIDATION["Cache Invalidation<br/>New build ID"]
    end
    
    ROOT --> BUILD_ID
    BUILD_ID --> CHUNKS
    BUILD_ID --> CSS
    BUILD_ID --> FONTS
    
    CHUNKS --> JS_CHUNKS
    CSS --> CSS_FILES
    FONTS --> FONT_FILES
    
    JS_CHUNKS --> IMMUTABLE
    CSS_FILES --> VERSIONED
    FONT_FILES --> INVALIDATION
```

### Public Path Configuration

The webpack runtime sets the public path for asset loading:

```javascript
r.p = "/asteroid-game/_next/"
```

This configures all dynamic imports and chunk loading to use the correct base path for the application deployment.

Sources: [apps/asteroid-game/_next/static/chunks/webpack-272b44dd0cfe77c4.js:1-1]()

## Asset Loading & Optimization

The build system implements sophisticated asset loading strategies including script injection, trusted types support, and error handling for robust production deployment.

### Script Loading Pipeline

```mermaid
graph TD
    subgraph "Asset Request Flow"
        CHUNK_REQUEST["r.e(chunkId)<br/>Chunk Load Request"]
        CACHE_CHECK["Cache Status Check"]
        PROMISE_CREATION["Promise Creation"]
        SCRIPT_INJECTION["Script Tag Injection"]
    end
    
    subgraph "Script Tag Management"
        ELEMENT_CREATION["document.createElement('script')"]
        TRUSTED_URL["r.tu() Trusted Types"]
        TIMEOUT_HANDLER["120s Timeout"]
        ERROR_HANDLING["Load Error Recovery"]
    end
    
    subgraph "Load States"
        PENDING["Loading Promise"]
        SUCCESS["Chunk Execution"]
        FAILURE["Error Cleanup"]
    end
    
    CHUNK_REQUEST --> CACHE_CHECK
    CACHE_CHECK --> PROMISE_CREATION
    PROMISE_CREATION --> SCRIPT_INJECTION
    SCRIPT_INJECTION --> ELEMENT_CREATION
    ELEMENT_CREATION --> TRUSTED_URL
    TRUSTED_URL --> TIMEOUT_HANDLER
    TIMEOUT_HANDLER --> ERROR_HANDLING
    
    ERROR_HANDLING --> PENDING
    PENDING --> SUCCESS
    PENDING --> FAILURE
```

### Security Features

The build system includes Content Security Policy support through Trusted Types:

| Feature | Implementation | Purpose |
|---------|---------------|---------|
| Trusted Types | `r.tt()` policy creation | XSS prevention |
| Nonce Support | `r.nc` attribute | CSP compliance |
| Webpack Data Attributes | `data-webpack` markers | Script identification |
| Timeout Protection | 120-second limits | Prevent hanging loads |

Sources: [apps/asteroid-game/_next/static/chunks/webpack-272b44dd0cfe77c4.js:1-1](), [apps/asteroid-game/_next/static/chunks/main-661c9648457bfc1f.js:1-1]()

---

