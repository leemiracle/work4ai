<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/qa-use · page 4 User Interface · fetched 2026-10-30 -->

# User Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/layout.tsx](src/app/layout.tsx)
- [src/app/page.tsx](src/app/page.tsx)

</details>



## Purpose and Scope

This document covers the web application frontend of the QA Use platform, including the React components, page structure, navigation patterns, and user interaction flows. The UI is built using Next.js with React components and provides interfaces for managing test suites, creating tests, and monitoring execution.

For information about the underlying data structures and business logic, see [Core Concepts](#3). For details about form handling and data mutations, see [Server Actions](#8). For information about reusable UI components across the application, see [Shared Components](#4.4).

## UI Architecture Overview

The QA Use platform uses a Next.js application structure with React components organized around the core entities of suites, tests, and test runs.

### Frontend Technology Stack

```mermaid
graph TB
    subgraph "Frontend Stack"
        NEXTJS["Next.js Framework"]
        REACT["React Components"]
        TAILWIND["Tailwind CSS"]
        SHADCN["shadcn/ui Components"]
    end
    
    subgraph "Core UI Pages"
        DASHBOARD["page.tsx<br/>Main Dashboard"]
        SUITE_DETAIL["suite/[id]/page.tsx<br/>Suite Details"]
        TEST_DETAIL["test/[id]/page.tsx<br/>Test Management"]
        RUN_DETAIL["run/[id]/page.tsx<br/>Execution Views"]
    end
    
    subgraph "Shared Components"
        PAGE_HEADER["PageHeader"]
        SECTION_HEADER["SectionHeader"]
        FORM_COMPONENTS["Input, Button, Dialog"]
        TABLE_COMPONENTS["Table, TableRow, TableCell"]
    end
    
    NEXTJS --> DASHBOARD
    NEXTJS --> SUITE_DETAIL
    NEXTJS --> TEST_DETAIL
    NEXTJS --> RUN_DETAIL
    
    REACT --> PAGE_HEADER
    REACT --> SECTION_HEADER
    REACT --> FORM_COMPONENTS
    REACT --> TABLE_COMPONENTS
    
    TAILWIND --> REACT
    SHADCN --> FORM_COMPONENTS
    SHADCN --> TABLE_COMPONENTS
```

**Sources:** [src/app/layout.tsx:1-36](), [src/app/page.tsx:1-120]()

## Application Layout Structure

The application uses a centralized layout pattern with consistent styling and responsive design.

### Root Layout Configuration

```mermaid
graph TD
    subgraph "RootLayout Component"
        HTML["html element<br/>lang='en'"]
        BODY["body element<br/>Geist fonts + bg-gray-50"]
        CONTAINER["div.min-h-screen"]
        CONTENT["div.max-w-6xl.mx-auto.px-3.py-12.md:py-16"]
    end
    
    subgraph "Font Configuration"
        GEIST_SANS["Geist Sans Font<br/>--font-geist-sans"]
        GEIST_MONO["Geist Mono Font<br/>--font-geist-mono"]
    end
    
    subgraph "Global Styles"
        GLOBALS["globals.css<br/>Tailwind CSS imports"]
        ANTIALIASED["antialiased class<br/>Font smoothing"]
    end
    
    HTML --> BODY
    BODY --> CONTAINER
    CONTAINER --> CONTENT
    CONTENT --> "children pages"
    
    GEIST_SANS --> BODY
    GEIST_MONO --> BODY
    GLOBALS --> BODY
    ANTIALIASED --> BODY
```

**Sources:** [src/app/layout.tsx:22-36](), [src/app/layout.tsx:7-15]()

The layout establishes a consistent container with maximum width of `6xl` (1152px) and responsive padding that creates the main content area for all pages.

## Main Dashboard Interface

The primary interface is implemented in the root page component, displaying all test suites in a tabular format with creation and navigation capabilities.

### Dashboard Component Structure

```mermaid
graph TD
    subgraph "Page Component"
        LOADER["loader() function<br/>Data fetching"]
        PAGE_COMP["Page() component<br/>Main render function"]
    end
    
    subgraph "UI Components"
        PAGE_HEADER["PageHeader<br/>title='All Suites'<br/>subtitle='QA Use'"]
        SECTION_HEADER["SectionHeader<br/>title='Test Suites'"]
        CREATE_DIALOG["CreateSuiteDialog<br/>Suite creation form"]
        SUITES_TABLE["Table component<br/>Suite listing"]
    end
    
    subgraph "Table Structure"
        TABLE_HEADER["TableHeader<br/>Name, Tests, Created, Cron, Last Run"]
        TABLE_BODY["TableBody<br/>Dynamic suite rows"]
        TABLE_ROW["TableRow per suite<br/>Suite data + View link"]
    end
    
    subgraph "Actions"
        CREATE_SUITE_ACTION["createSuiteAction<br/>Server action"]
        VIEW_LINK["Link to /suite/[id]<br/>Navigation"]
    end
    
    LOADER --> PAGE_COMP
    PAGE_COMP --> PAGE_HEADER
    PAGE_COMP --> SECTION_HEADER
    SECTION_HEADER --> CREATE_DIALOG
    PAGE_COMP --> SUITES_TABLE
    
    SUITES_TABLE --> TABLE_HEADER
    SUITES_TABLE --> TABLE_BODY
    TABLE_BODY --> TABLE_ROW
    
    CREATE_DIALOG --> CREATE_SUITE_ACTION
    TABLE_ROW --> VIEW_LINK
```

**Sources:** [src/app/page.tsx:25-76](), [src/app/page.tsx:78-108]()

### Suite Table Data Display

The main table displays suite information with the following columns:

| Column | Data Source | Formatting |
|--------|-------------|------------|
| Name | `suite.name` | Plain text display |
| Tests | `suite.tests.length` | Count with "tests" suffix |
| Created | `suite.createdAt` | Formatted via `formatDate()` |
| Cron | `suite.cronCadence` | Mapped via `getCronLabel()` |
| Last Run | `suite.lastCronRunAt` | Formatted date or "Never" |
| Actions | Navigation | Link to `/suite/${suite.id}` |

**Sources:** [src/app/page.tsx:41-73](), [src/app/page.tsx:110-119]()

### Suite Creation Dialog

The creation interface uses a modal dialog pattern with form submission:

```mermaid
graph LR
    subgraph "CreateSuiteDialog"
        TRIGGER["Button<br/>'Create Suite'<br/>Plus icon"]
        DIALOG["Dialog component<br/>Modal overlay"]
        FORM["form element<br/>action=createSuiteAction"]
        INPUT["Input field<br/>name='name'<br/>required"]
        SUBMIT["Submit Button<br/>'Create'"]
    end
    
    TRIGGER --> DIALOG
    DIALOG --> FORM
    FORM --> INPUT
    FORM --> SUBMIT
    SUBMIT --> "Server Action"
```

**Sources:** [src/app/page.tsx:78-108]()

## Dynamic Loading and Server-Side Rendering

The dashboard implements dynamic server-side rendering with data loading:

- `export const dynamic = 'force-dynamic'` ensures fresh data on each request [src/app/page.tsx:23]()
- Async `loader()` function fetches suite data before rendering [src/app/page.tsx:26]()
- Server actions handle form submissions without client-side JavaScript requirements

## Navigation Patterns

The UI implements navigation through Next.js `Link` components:

- Main dashboard accessible at root path `/`
- Suite detail pages at `/suite/[id]` [src/app/page.tsx:68]()
- External link to GitHub repository in page header [src/app/page.tsx:33]()

## Responsive Design Considerations

The layout uses Tailwind CSS responsive utilities:

- Container padding: `px-3` base, responsive on larger screens
- Vertical spacing: `py-12 md:py-16` with breakpoint variation
- Maximum width constraint: `max-w-6xl` with center alignment

**Sources:** [src/app/layout.tsx:31]()

---

