<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/aisheets · extra page Cell Rendering and Interaction · fetched 2026-10-26 -->

# Cell Rendering and Interaction

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/features/execution/useGenerateColumn.ts](src/features/execution/useGenerateColumn.ts)
- [src/features/table/components/body/cell-renderer.tsx](src/features/table/components/body/cell-renderer.tsx)
- [src/features/table/components/body/renderer/components/cell/table-renderer.tsx](src/features/table/components/body/renderer/components/cell/table-renderer.tsx)
- [src/features/table/components/body/renderer/components/preview/preview-raw-renderer.tsx](src/features/table/components/body/renderer/components/preview/preview-raw-renderer.tsx)
- [src/features/table/components/body/renderer/components/preview/preview-renderer.tsx](src/features/table/components/body/renderer/components/preview/preview-renderer.tsx)
- [src/features/utils/columns.ts](src/features/utils/columns.ts)
- [src/services/repository/cells.ts](src/services/repository/cells.ts)
- [src/usecases/validate-cell.usecase.ts](src/usecases/validate-cell.usecase.ts)

</details>



This document covers the cell rendering system and user interaction mechanisms within the AI Sheets table interface. It details how different data types are displayed, how users can edit cell content, and the validation pipeline for cell updates. For information about column management and generation, see [Column Management](#3.2.1). For broader AI integration concepts, see [AI Integration](#3.3).

## Cell Rendering System

The cell rendering system dynamically selects appropriate renderers based on column types and content detection. The main entry point is `CellRenderer` component which orchestrates both display and editing functionality.

### Renderer Selection Pipeline

```mermaid
flowchart TD
    Cell["Cell Data"] --> CellRenderer["CellRenderer"]
    CellRenderer --> TableRenderer["TableRenderer"]
    TableRenderer --> TypeCheck{"Type Detection"}
    
    TypeCheck --> BlobCheck{"hasBlobContent()"}
    BlobCheck -->|true| TableBlobRenderer["TableBlobRenderer"]
    
    BlobCheck -->|false| ObjectCheck{"isObjectType()"}
    ObjectCheck -->|true| TableObjectRenderer["TableObjectRenderer"]
    
    ObjectCheck -->|false| ArrayCheck{"isArrayType()"}
    ArrayCheck -->|true| TableArrayRenderer["TableArrayRenderer"]
    
    ArrayCheck -->|false| MarkdownCheck{"isMarkDown()"}
    MarkdownCheck -->|true| TableMarkDownRenderer["TableMarkDownRenderer"]
    
    MarkdownCheck -->|false| HTMLCheck{"isHTMLContent()"}
    HTMLCheck -->|true| TableHTMLRenderer["TableHTMLRenderer"]
    
    HTMLCheck -->|false| TableRawRenderer["TableRawRenderer"]
    
    TableBlobRenderer --> Display["Cell Display"]
    TableObjectRenderer --> Display
    TableArrayRenderer --> Display
    TableMarkDownRenderer --> Display
    TableHTMLRenderer --> Display
    TableRawRenderer --> Display
```

The system uses utility functions from `columns.ts` to determine content types:

| Function | Purpose | Detection Logic |
|----------|---------|----------------|
| `hasBlobContent()` | Detects binary/image data | Checks for `BLOB` type or image columns |
| `isObjectType()` | Identifies structured data | Matches `STRUCT` or `MAP` types |
| `isArrayType()` | Finds array data | Looks for `[]` in type name |
| `isMarkDown()` | Detects markdown content | Pattern matching against markdown syntax |
| `isHTMLContent()` | Identifies HTML content | Regex pattern for HTML tags |

Sources: [src/features/table/components/body/renderer/components/cell/table-renderer.tsx:18-49](), [src/features/utils/columns.ts:7-86]()

### Content Processing

Cells undergo content processing to handle AI-generated thinking tags and format content appropriately:

```mermaid
graph LR
    RawValue["Raw Cell Value"] --> removeThinking["removeThinking()"]
    RawValue --> getThinking["getThinking()"]
    
    removeThinking --> DisplayValue["Processed Display Value"]
    getThinking --> ThinkingSteps["Extracted Reasoning Steps"]
    
    DisplayValue --> Renderer["Type-specific Renderer"]
    ThinkingSteps --> PreviewRenderer["Preview with Reasoning"]
```

Sources: [src/features/utils/columns.ts:69-86](), [src/features/table/components/body/renderer/components/preview/preview-renderer.tsx:26-31]()

## Cell Interaction Workflow

Cell interaction follows a modal-based editing system with dual-mode display capabilities.

### Editing State Machine

```mermaid
stateDiagram-v2
    [*] --> Display
    Display --> Expanded : "Double-click"
    Display --> Display : "Single-click"
    
    Expanded --> EditMode : "Edit button"
    Expanded --> Display : "Close overlay"
    
    EditMode --> WriteMode : "Write tab"
    EditMode --> PreviewMode : "Preview tab"
    
    WriteMode --> PreviewMode : "Tab switch"
    PreviewMode --> WriteMode : "Tab switch"
    
    EditMode --> Validating : "Save button"
    EditMode --> Display : "Cancel button"
    
    Validating --> Display : "Success"
    Validating --> EditMode : "Validation error"
```

The interaction flow is managed by `CellRenderer` component with these key states:

- `isExpanded`: Controls modal overlay display
- `isEditing`: Toggles between view and edit modes  
- `mode`: Switches between 'write' and 'preview' in edit mode

Sources: [src/features/table/components/body/cell-renderer.tsx:16-46]()

### Cell Validation and Persistence

```mermaid
sequenceDiagram
    participant User
    participant CellRenderer
    participant validateCellUseCase as "validateCellUseCase"
    participant updateCell as "updateCell"
    participant createCell as "createCell"
    participant ColumnsStore as "useColumnsStore"

    User->>CellRenderer: "Edit cell content"
    CellRenderer->>CellRenderer: "Update newValue signal"
    User->>CellRenderer: "Click Save"
    CellRenderer->>validateCellUseCase: "validateCell(cell, newValue)"
    
    validateCellUseCase->>updateCell: "Try update existing cell"
    
    alt Cell exists
        updateCell-->>validateCellUseCase: "Updated cell"
    else Cell doesn't exist
        updateCell-->>validateCellUseCase: "Error"
        validateCellUseCase->>createCell: "Create new cell"
        createCell-->>validateCellUseCase: "Created cell"
    end
    
    validateCellUseCase->>ColumnsStore: "replaceCell(updatedCell)"
    ColumnsStore-->>CellRenderer: "State updated"
    CellRenderer->>User: "Close edit modal"
```

The validation system handles both cell updates and creation through `validateCellUseCase`. The use case attempts to update existing cells first, falling back to creation if the cell doesn't exist in the database.

Sources: [src/usecases/validate-cell.usecase.ts:18-66](), [src/features/table/components/body/cell-renderer.tsx:39-46]()

## Data Flow Architecture

### Client-Server Cell Operations

```mermaid
graph TB
    subgraph "Client State"
        CellState["Cell State Signals"]
        ColumnsStore["useColumnsStore"]
    end
    
    subgraph "Use Cases Layer"
        ValidateCell["validateCellUseCase"]
        GenerateColumn["useGenerateColumn"]
    end
    
    subgraph "Server Services"
        CellsRepository["cells.ts repository"]
        UpdateCell["updateCell()"]
        CreateCell["createCell()"]
        GetCell["getColumnCellById()"]
    end
    
    subgraph "Database Layer"
        ColumnCellModel["ColumnCellModel"]
        DatasetTable["Dataset Table (DuckDB)"]
    end
    
    CellState --> ValidateCell
    ValidateCell --> UpdateCell
    ValidateCell --> CreateCell
    UpdateCell --> CellsRepository
    CreateCell --> CellsRepository
    
    GenerateColumn --> GetCell
    GetCell --> CellsRepository
    
    CellsRepository --> ColumnCellModel
    CellsRepository --> DatasetTable
    
    UpdateCell --> ColumnsStore
    CreateCell --> ColumnsStore
    GetCell --> ColumnsStore
```

The system maintains cell data in two locations:
- `ColumnCellModel` (SQLite): Stores metadata, validation status, errors, and sources
- Dataset Table (DuckDB): Stores actual cell values for efficient querying

Sources: [src/services/repository/cells.ts:14-89](), [src/usecases/validate-cell.usecase.ts:21-32]()

### Cell Model Structure

The `Cell` type represents the complete cell state:

```typescript
interface Cell {
  id?: string;              // Database ID
  idx: number;              // Row index
  value?: string;           // Cell content
  error?: string;           // Validation error
  validated: boolean;       // Validation status
  column: {                 // Column reference
    id: string;
    type: string;
  };
  updatedAt: Date;          // Last modification
  generating: boolean;      // AI generation status
  sources?: CellSource[];   // Source references for AI-generated content
}
```

Sources: [src/state:Cell](), [src/services/repository/cells.ts:42-56]()

## Component Hierarchy

### Renderer Component Tree

```mermaid
graph TD
    CellRenderer --> TableRenderer
    CellRenderer --> PreviewRenderer
    
    TableRenderer --> TableBlobRenderer
    TableRenderer --> TableObjectRenderer  
    TableRenderer --> TableArrayRenderer
    TableRenderer --> TableMarkDownRenderer
    TableRenderer --> TableHTMLRenderer
    TableRenderer --> TableRawRenderer
    
    PreviewRenderer --> PreviewBlobRenderer
    PreviewRenderer --> PreviewObjectRenderer
    PreviewRenderer --> PreviewArrayRenderer  
    PreviewRenderer --> PreviewMarkDownRenderer
    PreviewRenderer --> PreviewHtmlRenderer
    PreviewRenderer --> PreviewRawRenderer
    
    CellRenderer --> CellRawEditor
    CellRenderer --> ToggleGroup
```

Each renderer type handles specific data formats:

- **Raw**: Plain text content
- **Markdown**: Formatted markdown with syntax highlighting
- **HTML**: Rendered HTML content
- **Blob**: Binary data and images  
- **Array**: List/array data structures
- **Object**: Structured object data

Sources: [src/features/table/components/body/cell-renderer.tsx:12](), [src/features/table/components/body/renderer/components/cell/table-renderer.tsx:18-49]()

### Cell Edit Modal Structure

The edit modal provides a comprehensive editing experience with preview capabilities:

```mermaid
graph TD
    Modal["Edit Modal Overlay"] --> Header["Header with Tab Controls"]
    Modal --> Content["Content Area"]  
    Modal --> Actions["Action Buttons"]
    
    Header --> WriteTab["Write Tab"]
    Header --> PreviewTab["Preview Tab"]
    
    Content --> CellRawEditor["Raw Text Editor"]
    Content --> PreviewRenderer["Live Preview"]
    
    Actions --> SaveButton["Save Button"]
    Actions --> CancelButton["Cancel Button"]
    
    CellRawEditor -.->|"mode === 'write'"| Content
    PreviewRenderer -.->|"mode === 'preview'"| Content
```

The modal supports real-time preview switching, allowing users to see formatted output while editing raw content.

Sources: [src/features/table/components/body/cell-renderer.tsx:80-168]()

---

