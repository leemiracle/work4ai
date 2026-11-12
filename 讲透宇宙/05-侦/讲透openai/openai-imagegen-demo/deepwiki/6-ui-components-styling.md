<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-imagegen-demo · page 6 UI Components & Styling · fetched 2026-10-26 -->

# UI Components & Styling

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/globals.css](app/globals.css)
- [app/layout.tsx](app/layout.tsx)
- [components/ui/button.tsx](components/ui/button.tsx)

</details>



This section provides an overview of the application's visual layer, including the React component architecture, the design system tokens, and global CSS configurations. The UI is built using **Tailwind CSS v4**, **Radix UI** primitives, and **Shadcn UI** patterns, ensuring a responsive and accessible experience across mobile and desktop devices.

## High-Level Architecture

The UI is divided into two distinct layers: a base design system providing primitive components and tokens, and a feature-specific layer containing complex components for image capture and result streaming.

### Component Hierarchy & Styling Flow

The following diagram illustrates how global styles and design tokens flow into the functional components used in the application.

**UI Layer Association**
```mermaid
graph TD
    subgraph "Natural Language Space"
        "Visual Theme"
        "Layout Structure"
        "Interactive Elements"
    end

    subgraph "Code Entity Space"
        direction TB
        G[app/globals.css]
        L[app/layout.tsx]
        B[components/ui/button.tsx]
        PC[components/photobooth/*]
        
        G -->|Provides Tokens| B
        G -->|Provides Tokens| PC
        L -->|Wraps| PC
        B -->|Used by| PC
    end

    "Visual Theme" -.-> G
    "Layout Structure" -.-> L
    "Interactive Elements" -.-> B
```
**Sources:** [app/globals.css:1-124](), [app/layout.tsx:25-39](), [components/ui/button.tsx:7-35]()

## Photobooth Components

The `components/photobooth/` directory contains the core domain-specific logic for the application. These components manage the complex states of the camera interface, style selection, and the asynchronous streaming of AI-generated images.

Key components include:
*   **CaptureStage**: Handles the webcam stream, file uploads, and drag-and-drop interactions.
*   **Style Selection**: Responsive components (`DesktopStylePanel` and `MobileStyleStrip`) that allow users to choose generation styles.
*   **Result Displays**: `ResultImageCard` manages the lifecycle of a single generation (from spinner to final image), while `ResultPreviewModal` provides a fullscreen view with download capabilities.

For a detailed breakdown of these components, see **[Photobooth Components](#6.1)**.

**Sources:** [app/layout.tsx:16-23](), [components/ui/button.tsx:1-58]()

## Design System & Global Styles

The application utilizes a modern styling stack centered around **Tailwind CSS v4** and **OKLCH** color spaces. This allows for high-precision color definitions that remain consistent across light and dark modes.

### Styling Logic Overview
The following diagram maps the styling configuration to the resulting UI behavior.

**Styling System Mapping**
```mermaid
graph LR
    subgraph "Code Entity Space"
        V4["Tailwind v4 @theme"]
        OKLCH["OKLCH Tokens"]
        CN["cn() Utility"]
        CVA["buttonVariants (CVA)"]
    end

    subgraph "Natural Language Space"
        "Design Tokens"
        "Color Consistency"
        "Dynamic Classes"
        "Component Variants"
    end

    V4 --- "Design Tokens"
    OKLCH --- "Color Consistency"
    CN --- "Dynamic Classes"
    CVA --- "Component Variants"
```
**Sources:** [app/globals.css:8-44](), [components/ui/button.tsx:7-35]()

### Core Styling Features
*   **OKLCH Color Tokens**: Defined in `app/globals.css`, these tokens (e.g., `--primary`, `--destructive`) provide perceptually uniform colors for both light and dark themes [app/globals.css:46-115]().
*   **Tailwind v4 Integration**: The `@theme inline` block maps CSS variables to Tailwind utility classes, such as `bg-background` and `text-foreground` [app/globals.css:8-44]().
*   **Primitive Components**: Base UI elements like the `Button` component use `class-variance-authority` (CVA) to manage visual states (e.g., `outline`, `ghost`, `destructive`) while maintaining accessibility through Radix UI's `Slot` [components/ui/button.tsx:7-55]().

For details on the CSS variable map and utility functions, see **[Design System & Global Styles](#6.2)**.

**Sources:** [app/globals.css:1-124](), [components/ui/button.tsx:7-58]()

---

