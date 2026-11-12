<!-- source: DeepWiki mcp.deepwiki.com · repo agentsmd/agents.md · extra page LogoItem Rendering · fetched 2026-10-21 -->

# LogoItem Rendering

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [components/CompatibilitySection.tsx](components/CompatibilitySection.tsx)
- [public/logos/junie.svg](public/logos/junie.svg)
- [public/logos/vscode-dark.svg](public/logos/vscode-dark.svg)
- [public/logos/vscode-light.svg](public/logos/vscode-light.svg)
- [styles/globals.css](styles/globals.css)

</details>



The `LogoItem` component is the primary unit for displaying agent information and branding within the `CompatibilitySection`. It implements a theme-aware rendering system that handles two distinct logo patterns: separate light/dark image variants and single SVG files using CSS masking. This ensures high-contrast visibility across both system color schemes while maintaining consistent typography and layout.

**Sources:** [components/CompatibilitySection.tsx:157-226]()

## Component Interface

The `LogoItem` component is a functional React component that consumes the `LogoItemProps` type. This type extends the core `AgentEntry` definition with an optional display variant.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | `string` | Yes | Agent display name (e.g., "VS Code") |
| `url` | `string` | Yes | Target link for the agent's documentation or site |
| `from` | `string` | No | Parent organization (e.g., "GitHub Copilot") |
| `imageSrc` | `string` | No | Path to a single SVG used for CSS masking |
| `imageSrcLight` | `string` | No | Path to the light-theme specific image |
| `imageSrcDark` | `string` | No | Path to the dark-theme specific image |
| `variant` | `"marquee" \| "grid"` | No | Layout style (default: `"marquee"`) |

**Sources:** [components/CompatibilitySection.tsx:5-12](), [components/CompatibilitySection.tsx:153-165]()

## Rendering Decision Flow

The component uses conditional rendering to determine how to display the logo asset. It prioritizes explicit light/dark pairs over the single-source masking technique.

```mermaid
graph TD
    "LogoItem(props)"["LogoItem Component"]
    "CheckPairs"{"imageSrcLight && imageSrcDark?"}
    "RenderDual"["Render Two Image Components"]
    "CheckSingle"{"imageSrc?"}
    "RenderMask"["Render CSS Masked Span"]
    "RenderNull"["Render null"]
    
    "TailwindToggle"["Toggle visibility via 'dark:hidden' and 'dark:block'"]
    "MaskLogic"["Apply bg-gray-700 (light) or bg-gray-400 (dark)"]

    "LogoItem(props)" --> "CheckPairs"
    "CheckPairs" -- "Yes" --> "RenderDual"
    "CheckPairs" -- "No" --> "CheckSingle"
    "CheckSingle" -- "Yes" --> "RenderMask"
    "CheckSingle" -- "No" --> "RenderNull"
    
    "RenderDual" --> "TailwindToggle"
    "RenderMask" --> "MaskLogic"
```

**Sources:** [components/CompatibilitySection.tsx:179-211]()

## Theme-Aware Logo Patterns

### 1. Dual-Image Variants
For logos that require specific color adjustments beyond simple fills (like VS Code or Windsurf), the system uses two separate files. Both are rendered, but one is hidden based on the CSS `dark` class.

*   **Light Mode:** The `imageSrcLight` asset is displayed using `block`, while `imageSrcDark` is `hidden`.
*   **Dark Mode:** The `imageSrcLight` asset is hidden using `dark:hidden`, while `imageSrcDark` is shown using `dark:block`.

**Example Entry:**
[components/CompatibilitySection.tsx:100-104]()
```typescript
{
  name: "VS Code",
  url: "...",
  imageSrcLight: "/logos/vscode-light.svg",
  imageSrcDark: "/logos/vscode-dark.svg",
}
```

**Sources:** [components/CompatibilitySection.tsx:181-194](), [public/logos/vscode-light.svg:1-13](), [public/logos/vscode-dark.svg:1-20]()

### 2. CSS Masked SVGs
For single-color logos (like Cursor or Zed), the component uses the SVG as a mask. This allows the website to control the logo's color via standard Tailwind background utilities.

*   **Light Mode:** The background is `bg-gray-700`.
*   **Dark Mode:** The background is `dark:bg-gray-400`.
*   **Masking:** The SVG path defines where the background color shows through using `maskImage` and `WebkitMaskImage`.

**Sources:** [components/CompatibilitySection.tsx:196-210]()

## Layout and Styling

The `LogoItem` adapts its container styles based on whether it is rendered within the scrolling marquee or the static grid view.

```mermaid
graph TD
    "LogoItemProps.variant"["LogoItemProps.variant"]
    "MarqueeStyle"["'flex h-20 min-w-[280px] items-center gap-4 pr-10'"]
    "GridStyle"["'flex h-full w-full min-w-0 items-center gap-4'"]
    "BaseLayout"["Anchor Tag (a)"]
    
    "LogoItemProps.variant" -- "marquee" --> "MarqueeStyle"
    "LogoItemProps.variant" -- "grid" --> "GridStyle"
    "MarqueeStyle" --> "BaseLayout"
    "GridStyle" --> "BaseLayout"

    subgraph "Internal Structure"
        "BaseLayout" --> "LogoContainer"["div (h-16 w-16)"]
        "BaseLayout" --> "TextContainer"["div (flex-col)"]
        "TextContainer" --> "Name"["span (text-xl font-semibold)"]
        "TextContainer" --> "From"["span (text-sm font-light)"]
    end
```

### Visual Hierarchy
1.  **Logo Container:** A fixed `64x64px` (`h-16 w-16`) area that centers the image or mask. [components/CompatibilitySection.tsx:178]()
2.  **Name:** Rendered in `text-xl` with `font-semibold`. The color shifts from `text-gray-700` (light) to `text-gray-300` (dark). [components/CompatibilitySection.tsx:214-216]()
3.  **Origin ("from"):** If provided, displayed in `text-sm` below the name. [components/CompatibilitySection.tsx:217-222]()

**Sources:** [components/CompatibilitySection.tsx:166-169](), [components/CompatibilitySection.tsx:213-223]()

## Integration and Performance

The component is optimized for both visual fidelity and performance:
*   **Next.js Image:** Uses the `next/image` component for dual-variant logos, benefiting from automatic optimization and lazy loading. [components/CompatibilitySection.tsx:2]()
*   **CSS Masking:** Single-variant logos are rendered as simple `span` elements, reducing the number of network requests and DOM nodes compared to full inline SVGs. [components/CompatibilitySection.tsx:197]()
*   **Typography:** Utilizes the custom `OpenAI Sans` font family defined in the global styles. [styles/globals.css:78]()

**Sources:** [components/CompatibilitySection.tsx:181-194](), [styles/globals.css:3-79]()

---

