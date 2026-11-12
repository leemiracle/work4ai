<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/aisheets · page 5 UI Components · fetched 2026-10-26 -->

# UI Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/components/ui/button/button.tsx](src/components/ui/button/button.tsx)
- [src/components/ui/index.ts](src/components/ui/index.ts)
- [src/components/ui/modal/modal.tsx](src/components/ui/modal/modal.tsx)
- [src/features/table/components/header/delete-column.tsx](src/features/table/components/header/delete-column.tsx)
- [src/features/table/components/header/hide-column.tsx](src/features/table/components/header/hide-column.tsx)
- [tailwind.config.js](tailwind.config.js)

</details>



This page documents the reusable UI component library that provides the visual building blocks for AI Sheets. It covers the design system, component architecture, styling approach, and individual component APIs. For information about how these components are integrated into the table interface, see [Table Interface](#3.2). For broader frontend architecture patterns, see [Frontend Architecture](#4.1).

## Component Architecture

AI Sheets uses Qwik's component system to build a modular, reusable UI library. All UI components are centralized in the `src/components/ui/` directory and follow consistent patterns for styling, variants, and behavior.

```mermaid
graph TB
    UIIndex["index.ts<br/>Component Exports"]
    
    subgraph "Form Components"
        Button["button/button.tsx"]
        Input["input/input.tsx"] 
        Textarea["textarea/textarea.tsx"]
        Select["select/select.tsx"]
        Checkbox["checkbox/checkbox.tsx"]
        ToggleGroup["toggle-group/toggle-group.tsx"]
    end
    
    subgraph "Layout Components"
        Modal["modal/modal.tsx"]
        Popover["popover/popover.tsx"]
        Accordion["accordion/accordion.tsx"]
    end
    
    subgraph "Feedback Components"
        Label["label/label.tsx"]
        Skeleton["skeleton/skeleton.tsx"]
    end
    
    subgraph "Styling System"
        CVA["class-variance-authority<br/>Variant System"]
        Tailwind["tailwind.config.js<br/>Design Tokens"]
        Utils["@qwik-ui/utils<br/>Utility Functions"]
    end
    
    UIIndex --> Button
    UIIndex --> Input
    UIIndex --> Textarea
    UIIndex --> Select
    UIIndex --> Checkbox
    UIIndex --> ToggleGroup
    UIIndex --> Modal
    UIIndex --> Popover
    UIIndex --> Accordion
    UIIndex --> Label
    UIIndex --> Skeleton
    
    Button --> CVA
    Button --> Tailwind
    Button --> Utils
    Modal --> Tailwind
    Modal --> Utils
```

**Sources:** [src/components/ui/index.ts:1-13](), [src/components/ui/button/button.tsx:1-89](), [src/components/ui/modal/modal.tsx:1-72]()

## Design System

The design system is built on Tailwind CSS with a comprehensive set of design tokens that ensure visual consistency across the application.

### Color Palette

The color system uses HSL values with semantic naming and multiple shade variations:

| Color Group | Purpose | Shades Available |
|-------------|---------|------------------|
| **Primary** | Main brand color, primary actions | 50, 100, 200, 300, 400, 500, 600, DEFAULT |
| **Secondary** | Secondary actions, success states | 50, 100, 200, 300, 400, 500, 600, DEFAULT |
| **Neutral** | Text, borders, backgrounds | 50, 100, 200, 300, 400, 500, 600, 700, DEFAULT |
| **Alert** | Error states, destructive actions | DEFAULT, foreground |
| **Green** | Success indicators | 50, 100, 200, 300, 400, 500, 600 |

### Design Tokens

```mermaid
graph LR
    subgraph "Spacing & Layout"
        BorderRadius["Border Radius<br/>--border-radius base"]
        BorderWidth["Border Width<br/>--border-width base"]
        Shadows["Box Shadows<br/>--shadow variants"]
    end
    
    subgraph "Color Variables"
        Semantic["Semantic Colors<br/>--background, --foreground"]
        Component["Component Colors<br/>--muted, --card, --popover"]
        State["State Colors<br/>--alert, --ring"]
    end
    
    subgraph "Animation"
        Press["Press Transform<br/>--transform-press"]
        Accordion["Accordion Animation<br/>collapsible-up/down"]
    end
    
    TailwindConfig["tailwind.config.js"] --> BorderRadius
    TailwindConfig --> BorderWidth
    TailwindConfig --> Shadows
    TailwindConfig --> Semantic
    TailwindConfig --> Component
    TailwindConfig --> State
    TailwindConfig --> Press
    TailwindConfig --> Accordion
```

**Sources:** [tailwind.config.js:6-124]()

## Core UI Components

### Button Component

The `Button` component is the most feature-rich UI component, supporting multiple visual variants, sizes, and states including AI generation feedback.

```mermaid
graph TB
    ButtonComponent["Button Component"]
    
    subgraph "Variant System"
        Look["Look Variants<br/>primary, secondary, alert, outline, ghost, link"]
        Size["Size Variants<br/>sm, md, lg, icon"]
        State["State Variants<br/>default, generating, stopGenerating"]
    end
    
    subgraph "Props Interface"
        ButtonProps["ButtonProps"]
        VariantProps["VariantProps<buttonVariants>"]
        QwikProps["PropsOf<'button'>"]
        GeneratingProps["isGenerating, onStopGenerating"]
    end
    
    subgraph "Implementation"
        CVAFunction["buttonVariants (cva)"]
        QwikComponent["component$"]
        SlotSystem["<Slot /> children"]
    end
    
    ButtonComponent --> Look
    ButtonComponent --> Size  
    ButtonComponent --> State
    ButtonComponent --> ButtonProps
    ButtonProps --> VariantProps
    ButtonProps --> QwikProps
    ButtonProps --> GeneratingProps
    ButtonComponent --> CVAFunction
    ButtonComponent --> QwikComponent
    ButtonComponent --> SlotSystem
```

The button variants are defined using `class-variance-authority` for type-safe styling:

- **Look variants**: Control visual appearance from primary brand styling to subtle ghost buttons
- **Size variants**: Standard sizing from small (`sm`) to large (`lg`) plus square icon variant
- **State variants**: Special `generating` state provides visual feedback during AI operations

**Sources:** [src/components/ui/button/button.tsx:5-89]()

### Modal Component

The `Modal` component integrates with the application's modal management system and provides overlay functionality with proper accessibility and DOM manipulation.

```mermaid
graph TB
    ModalComponent["Modal Component"]
    
    subgraph "Modal Props"
        ModalName["name: ID"]
        ModalTitle["title?: string"]
        ModalRest["...PropsOf<'div'>"]
    end
    
    subgraph "Hooks Integration"
        UseModals["useModals(name)"]
        IsOpen["isOpen signal"]
        Close["close function"]
    end
    
    subgraph "DOM Management"
        StickyHandling["Sticky Element Handling"]
        PointerEvents["Pointer Events Control"]
        ZIndexManagement["Z-Index Layering"]
    end
    
    subgraph "UI Elements"
        Header["Modal Header"]
        CloseButton["Close Button (LuX)"]
        Content["<Slot /> Content"]
    end
    
    ModalComponent --> ModalName
    ModalComponent --> ModalTitle
    ModalComponent --> ModalRest
    ModalComponent --> UseModals
    UseModals --> IsOpen
    UseModals --> Close
    ModalComponent --> StickyHandling
    ModalComponent --> PointerEvents
    ModalComponent --> ZIndexManagement
    ModalComponent --> Header
    ModalComponent --> CloseButton
    ModalComponent --> Content
```

The modal system handles complex DOM interactions including temporarily removing sticky positioning from elements and managing pointer events on the main content area.

**Sources:** [src/components/ui/modal/modal.tsx:1-72](), [src/components/hooks/modals/config.ts]()

## Usage Patterns

### Button Integration in Table Features

UI components are extensively used throughout the table interface, particularly in column management operations:

```mermaid
graph LR
    subgraph "Column Actions"
        HideColumn["HideColumn Component"]
        DeleteColumn["DeleteColumn Component"]
    end
    
    subgraph "Button Usage"
        GhostButton["Button look='ghost'"]
        SizeSmall["Button size='sm'"]
        IconButton["Icon + Text Pattern"]
    end
    
    subgraph "State Management"
        Disabled["disabled prop"]
        Loading["isGenerating prop"]
        Hover["hover styling"]
    end
    
    HideColumn --> GhostButton
    DeleteColumn --> GhostButton
    GhostButton --> SizeSmall
    GhostButton --> IconButton
    
    HideColumn --> Disabled
    DeleteColumn --> Disabled
    GhostButton --> Loading
    GhostButton --> Hover
```

**Sources:** [src/features/table/components/header/hide-column.tsx:36-50](), [src/features/table/components/header/delete-column.tsx:40-66]()

### Styling Conventions

Components follow consistent patterns for styling and behavior:

| Pattern | Implementation | Usage |
|---------|----------------|-------|
| **Ghost Buttons** | `look="ghost"` with hover backgrounds | Action buttons in dropdowns, toolbars |
| **Icon + Text** | Lucide icons with text labels | Column actions, toolbar buttons |
| **Disabled States** | Conditional `disabled` prop with opacity styling | Context-dependent action availability |
| **Responsive Sizing** | `size="sm"` for compact interfaces | Table headers, modal controls |

The component system emphasizes consistency through shared styling utilities and standardized prop interfaces across all UI components.

**Sources:** [src/components/ui/button/button.tsx:5-39](), [tailwind.config.js:127-133]()

---

