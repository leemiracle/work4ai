<!-- source: DeepWiki mcp.deepwiki.com · repo openai/harmony · page 5 Assets and Resources · fetched 2026-10-26 -->

# Assets and Resources

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [demo/harmony-demo/public/openai_logo.svg](demo/harmony-demo/public/openai_logo.svg)
- [demo/harmony-demo/src/app/favicon.ico](demo/harmony-demo/src/app/favicon.ico)
- [docs/header.png](docs/header.png)

</details>



This section documents the visual assets, logos, and supplementary files used throughout the `openai-harmony` project, particularly in the demo application and documentation. These resources support the branding and visual presentation of the harmony response format library.

## Asset Organization

The project contains a focused set of visual assets primarily located in the demo application's public directory structure and the root documentation folder. These assets serve the Next.js demo application and provide visual context for project documentation.

```mermaid
graph TB
    subgraph "Repository Assets"
        ROOT_DOCS["docs/"]
        HEADER["header.png"]
        PUB["demo/harmony-demo/public/"]
        LOGO["openai_logo.svg"]
        APP["demo/harmony-demo/src/app/"]
        FAVICON["favicon.ico"]
    end
    
    ROOT_DOCS --> HEADER
    PUB --> LOGO
    APP --> FAVICON
    
    subgraph "Asset Types"
        SVG["SVG Vector Graphics"]
        ICO["ICO Icon Format"]
        PNG["PNG Raster Image"]
    end
    
    LOGO --> SVG
    FAVICON --> ICO
    HEADER --> PNG
    
    subgraph "Usage Context"
        BRAND["Brand Identity"]
        NAV["Browser Tab Icon"]
        DOC_UI["Documentation Header"]
    end
    
    SVG --> BRAND
    ICO --> NAV
    PNG --> DOC_UI
```

**Sources:** [demo/harmony-demo/public/openai_logo.svg:1-21](), [demo/harmony-demo/src/app/favicon.ico:1-80](), [docs/header.png:1-43]()

## OpenAI Logo Specification

The primary brand asset is the OpenAI logo implemented as an SVG vector graphic. This logo maintains the official OpenAI visual identity within the harmony demo application.

### Logo Technical Details

| Property | Value |
|----------|-------|
| Format | SVG (Scalable Vector Graphics) |
| Dimensions | 127×127 viewBox |
| Background | White circle fill |
| Logo | Black OpenAI symbol |
| File Size | ~2KB optimized vector |

The logo implementation uses SVG masking and clipping paths to achieve precise rendering at any scale while maintaining small file size.

```mermaid
graph LR
    subgraph "SVG Structure"
        ROOT["svg"]
        CLIP["clipPath id='clip0_2048_18'"]
        MASK["mask id='mask0_2048_18'"]
        CIRCLE["circle cx='63.5' cy='63.5' r='63.5'"]
        PATH["path d='M54.0593...'"]
    end
    
    ROOT --> CLIP
    ROOT --> MASK
    ROOT --> CIRCLE
    ROOT --> PATH
    
    subgraph "Visual Properties"
        WHITE["White Background Circle"]
        BLACK["Black Logo Symbol"]
        SCALE["Scalable Vector"]
    end
    
    CIRCLE --> WHITE
    PATH --> BLACK
    ROOT --> SCALE
```

**Sources:** [demo/harmony-demo/public/openai_logo.svg:1-21]()

## Documentation Header

The project includes a high-resolution PNG header image located in the `docs/` directory. This asset is used to provide visual branding for the repository's documentation and GitHub presence.

### Header Specifications

| Property | Value |
|----------|-------|
| Format | PNG (Portable Network Graphics) |
| Color Space | ICC Profile (Adobe RGB/sRGB) |
| Dimensions | 1025×310 pixels |
| Metadata | XML:com.adobe.xmp (Screenshot) |

The image contains embedded XMP metadata and an ICC profile to ensure consistent color rendering across different display devices.

**Sources:** [docs/header.png:1-26](), [docs/header.png:17-23]()

## Favicon Implementation

The demo application includes a multi-resolution favicon in ICO format to ensure proper display across different browsers and contexts.

### Favicon Specifications

| Property | Value |
|----------|-------|
| Format | ICO (Icon) |
| Location | `/src/app/favicon.ico` |
| Resolutions | Multiple embedded sizes (16x16, 32x32, 48x48) |
| Color Depth | 32-bit with alpha transparency |

The favicon appears to contain the OpenAI logo symbol optimized for small icon display contexts such as browser tabs and taskbar representations.

**Sources:** [demo/harmony-demo/src/app/favicon.ico:1-80]()

## Asset Usage in Demo Application

The assets integrate with the Next.js demo application through standard web conventions and framework-specific patterns.

### Integration Patterns

The SVG logo is accessible via the public directory serving mechanism, making it available at `/openai_logo.svg` for use in React components. The favicon follows Next.js App Router conventions by being placed in the `app` directory where it is automatically detected.

```mermaid
graph LR
    subgraph "Asset Serving"
        PUBLIC["public/ Directory"]
        STATIC["Static File Serving"]
        APPDIR["app/ Directory"]
        AUTO["Automatic Favicon Detection"]
    end
    
    PUBLIC --> STATIC
    APPDIR --> AUTO
    
    subgraph "Client Access"
        LOGO_URL["/openai_logo.svg"]
        FAVICON_URL["/favicon.ico"]
        COMPONENTS["React Components"]
        BROWSER["Browser Automatic"]
    end
    
    STATIC --> LOGO_URL
    AUTO --> FAVICON_URL
    LOGO_URL --> COMPONENTS
    FAVICON_URL --> BROWSER
```

**Sources:** [demo/harmony-demo/public/openai_logo.svg:1-21](), [demo/harmony-demo/src/app/favicon.ico:1-80]()

## Asset Management Strategy

The project maintains a minimal but effective asset management approach focused on essential branding elements. This strategy prioritizes performance and maintainability while ensuring consistent visual identity across the library's demo and documentation.

### Key Principles

- **Minimal Asset Footprint**: Only essential visual assets are included to keep the repository lightweight.
- **Vector-First Approach**: SVG format is prioritized for the logo to ensure perfect scaling without quality loss.
- **Framework Conventions**: Assets are placed in directories that leverage Next.js built-in handling (e.g., `public/` and `src/app/`).
- **Standardized Formats**: Uses universal formats (SVG, ICO, PNG) for maximum compatibility.

**Sources:** [demo/harmony-demo/public/openai_logo.svg:1-21](), [demo/harmony-demo/src/app/favicon.ico:1-80](), [docs/header.png:1-43]()

---

