<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/ai-deadlines · page 6 Styling System · fetched 2026-10-26 -->

# Styling System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [postcss.config.js](postcss.config.js)
- [src/index.css](src/index.css)
- [src/styles/globals.css](src/styles/globals.css)
- [tailwind.config.ts](tailwind.config.ts)

</details>



This document provides an overview of the styling architecture and implementation in the ai-deadlines application. The styling system is built on Tailwind CSS with custom configurations, component-specific styles, and animation definitions.

## Overview

The ai-deadlines application uses a utility-first CSS approach through Tailwind CSS, supplemented with custom component styles and animations. The styling system consists of:

- Tailwind CSS as the core styling framework
- Custom theme configuration with brand colors
- Component-specific CSS classes
- Animation and transition effects
- PostCSS for processing

## Styling Architecture

```mermaid
graph TD
    subgraph "Configuration Files"
        tw["tailwind.config.ts<br>Theme Configuration"] --> postcss["postcss.config.js<br>Processing Configuration"]
    end
    
    subgraph "Style Definitions"
        index["src/index.css<br>Tailwind Imports & Base Styles"]
        globals["src/styles/globals.css<br>Component-specific Styles"]
    end
    
    tw --> build["CSS Build Process"]
    postcss --> build
    index --> build
    globals --> build
    
    build --> output["Final CSS Output"]
    
    subgraph "Component Usage"
        comp["React Components (.tsx)"] --> utility["Tailwind Utility Classes<br>(inline in components)"]
        comp --> custom["Custom CSS Classes<br>(.conference-card, .tag, etc.)"]
    end
    
    utility --> output
    custom --> output
```

Sources: [tailwind.config.ts](), [postcss.config.js](), [src/index.css](), [src/styles/globals.css]()

## Tailwind Configuration

The application extends Tailwind's default configuration with custom colors, animations, and container settings in `tailwind.config.ts`.

### Color System

```mermaid
graph TD
    subgraph "Theme Configuration"
        colors["Custom Color Palette<br>tailwind.config.ts"] --> primary["Primary Colors<br>#0284C7 (Default)<br>#7DD3FC (Light)<br>#075985 (Dark)"]
        colors --> neutral["Neutral Colors<br>#6B7280 (Default)<br>#F9FAFB (Light)<br>#111827 (Dark)"]
    end
    
    subgraph "CSS Variables"
        root["CSS Variables<br>:root in index.css"] --> base["Base Element Styles"]
        root --> components["Component Styles"]
    end
    
    primary --> usage["Component Usage<br>(text-primary, bg-primary-light, etc.)"]
    neutral --> usage
```

Sources: [tailwind.config.ts:22-37](), [src/index.css:5-27]()

The color system includes:

| Variable | Value | Usage |
|----------|-------|-------|
| primary | #0284C7 | Main brand color, buttons, links |
| primary-light | #7DD3FC | Highlights, backgrounds |
| primary-dark | #075985 | Hover states, emphasis |
| neutral | #6B7280 | Regular text, icons |
| neutral-light | #F9FAFB | Page backgrounds |
| neutral-dark | #111827 | Headings, important text |

## Component Styling Approach

The application uses a mix of Tailwind utility classes and custom component classes to achieve consistent styling.

### Base Styles

Base HTML and body styles are defined in `index.css`:

```mermaid
graph TD
    subgraph "Base Element Styles"
        html["html, body<br>src/index.css:29-34"] --> props["Properties:<br>h-full w-full<br>position: relative<br>overscroll-behavior-y: none"]
        body["body<br>src/index.css:36-38"] --> bodyProps["Properties:<br>bg-neutral-light<br>text-neutral-dark<br>antialiased"]
    end
```

Sources: [src/index.css:29-38]()

### Component-Specific Classes

The application defines several reusable component classes:

```mermaid
graph TD
    subgraph "Custom Component Classes"
        confCard["conference-card<br>src/index.css:41-43"] --> cardProps["Properties:<br>bg-white rounded-lg shadow-sm<br>hover:shadow-md transition-shadow<br>duration-300 p-4 flex flex-col"]
        
        tag["tag<br>src/index.css:45-47"] --> tagProps["Properties:<br>inline-flex items-center px-2 py-1<br>rounded-full text-sm font-medium<br>bg-primary/10 text-primary"]
        
        countdown["countdown<br>src/index.css:49-51"] --> countProps["Properties:<br>text-2xl font-semibold text-primary"]
        
        filterTag["filter-tag<br>src/styles/globals.css:2-4"] --> filterProps["Properties:<br>transition-all duration-200"]
        
        tagButton["tag-button<br>src/styles/globals.css:21-33"] --> buttonProps["Properties:<br>background-color: #f5f5f5<br>color: #666<br>border-radius: 0.375rem<br>etc."]
    end
```

Sources: [src/index.css:41-51](), [src/styles/globals.css:1-37]()

## Animation System

The application includes a rich set of animations for UI transitions and interactions.

### Dialog Animations

Dialog animations provide smooth transitions when opening and closing conference detail dialogs:

```mermaid
graph TD
    subgraph "Dialog Animation System"
        keyframes["Animation Keyframes"] --> scaleUp["scale-up<br>src/index.css:53-64"]
        keyframes --> scaleDown["scale-down<br>src/index.css:66-77"]
        keyframes --> fadeIn["fade-in<br>src/index.css:96-105"]
        keyframes --> fadeOut["fade-out<br>src/index.css:107-116"]
        
        dialogContent["dialog-content<br>src/index.css:79-82"] --> contentAnim["Animation:<br>scale-up 0.4s cubic-bezier"]
        dialogOverlay["dialog-overlay<br>src/index.css:84-86"] --> overlayAnim["Animation:<br>fade-in 0.4s cubic-bezier"]
        
        closedState["[data-state='closed']<br>src/index.css:88-94"] --> closedAnim["Applies close animations<br>when dialog is closing"]
    end
```

Sources: [src/index.css:53-116]()

### Filter Tag Animations

Interactive animations for filter tags improve user experience:

```mermaid
graph TD
    subgraph "Filter Tag Animations"
        pulseDef["subtle-pulse Keyframes<br>src/styles/globals.css:11-15"] --> pulseSteps["Steps:<br>scale(1) → scale(1.02) → scale(1)"]
        
        filterTagHover["filter-tag:hover<br>src/styles/globals.css:6-8"] --> hoverEffect["Effect:<br>transform scale-105"]
        
        filterTagActive["filter-tag-active<br>src/styles/globals.css:17-19"] --> activeEffect["Effect:<br>subtle-pulse animation<br>2s infinite"]
    end
```

Sources: [src/styles/globals.css:1-19]()

## Tailwind Extensions

The application extends Tailwind's default configuration with custom animations and keyframes:

```mermaid
graph TD
    subgraph "Tailwind Animation Extensions"
        keyframesDef["Keyframes Definitions<br>tailwind.config.ts:39-47"] --> fadeIn["fade-in:<br>opacity 0→1<br>translateY 10px→0"]
        keyframesDef --> slideIn["slide-in:<br>translateX -100%→0"]
        
        animDef["Animation Definitions<br>tailwind.config.ts:48-52"] --> fadeInAnim["fade-in:<br>0.5s ease-out"]
        animDef --> slideInAnim["slide-in:<br>0.3s ease-out"]
    end
```

Sources: [tailwind.config.ts:39-52]()

## Usage Examples

### Inline Tailwind Classes

Most styling in the application is applied using Tailwind utility classes directly in component TSX files:

```tsx
<div className="bg-white rounded-lg shadow-sm p-4 my-2">
  <h2 className="text-xl font-semibold text-primary">Conference Title</h2>
  <p className="text-sm text-neutral">Conference description</p>
</div>
```

### Custom Component Classes

For common UI patterns, the application uses predefined component classes:

```tsx
<div className="conference-card">
  <h2 className="text-xl font-semibold">Conference Title</h2>
  <div className="flex gap-2 mt-2">
    <span className="tag">AI</span>
    <span className="tag">Machine Learning</span>
  </div>
  <div className="countdown">2 days</div>
</div>
```

### Animation Classes

Animations are applied to components using the defined animation classes:

```tsx
<Dialog>
  <DialogOverlay className="dialog-overlay" />
  <DialogContent className="dialog-content">
    {/* Dialog content */}
  </DialogContent>
</Dialog>
```

## Integration with UI Components

The styling system integrates directly with the UI components described in [UI Components](#4), particularly with the [Conference Card](#4.1), [Conference Dialog](#4.2), and [Filter System](#4.3).

Sources: [src/index.css](), [src/styles/globals.css](), [tailwind.config.ts]()

---

