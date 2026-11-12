<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/langchain-extract · page 3 Frontend Components · fetched 2026-10-26 -->

# Frontend Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [frontend/app/components/Playground.tsx](frontend/app/components/Playground.tsx)
- [frontend/app/components/ResultsTable.tsx](frontend/app/components/ResultsTable.tsx)
- [frontend/app/utils/api.tsx](frontend/app/utils/api.tsx)

</details>



This page provides an overview of the key frontend components in the LangChain Extract application. The frontend is built using React and Next.js, providing an interactive user interface for creating extractors, running extractions, and viewing results.

For information about the backend API that these components interact with, see [Backend System](#4) and [API Endpoints](#4.2). For details on the creation and management of extractors, see [Creating and Managing Extractors](#3.2).

## Component Architecture

The frontend is organized into modular components that handle specific aspects of the extraction workflow. Below is a high-level architecture diagram showing the main components and their relationships:

```mermaid
flowchart TD
    subgraph "Frontend Application"
        App["App Component"]
        App --> Nav["Navigation"]
        App --> Routes["Routes"]
        
        Routes --> Playground["Playground Component"]
        Routes --> ExtractorCreation["Extractor Creation Component"]
        Routes --> ExtractorsList["Extractors List Component"]
        
        Playground --> ExtractorView["Extractor Component"]
        Playground --> InputForm["Input Form"]
        Playground --> ResultsView["Results View"]
        
        InputForm --> FileUpload["File Upload"]
        InputForm --> TextInput["Text Input"]
        InputForm --> ModelSelection["Model Selection"]
        
        ResultsView --> ResultsTable["ResultsTable Component"]
        ResultsView --> JSONView["JSON View"]
        
        ExtractorCreation --> SchemaEditor["Schema Editor"]
        ExtractorCreation --> InstructionsEditor["Instructions Editor"]
        
        subgraph "API Integration"
            APIHooks["API Hooks"]
        end
        
        Playground -.-> APIHooks
        ExtractorCreation -.-> APIHooks
        ExtractorsList -.-> APIHooks
    end
    
    APIHooks -.-> Backend["Backend API"]
```

Sources: [frontend/app/components/Playground.tsx:1-196](). [frontend/app/utils/api.tsx:1-184]()

## Key Components

### Playground Component

The Playground is the primary interface for testing extractors. It allows users to input text or upload files, select an extraction model, and view extraction results.

```mermaid
classDiagram
    class Playground {
        +string extractorId
        +boolean isShared
        -handleSubmit()
        -handleKeyDown()
        -handleChange()
    }
    
    class Extractor {
        +string extractorId
        +boolean isShared
    }
    
    class ResultsTable {
        +ExtractionResponse data
        +boolean isPending
    }
    
    class API {
        +runExtraction()
        +useConfiguration()
    }
    
    Playground --> Extractor : displays
    Playground --> ResultsTable : displays results in
    Playground --> API : calls
```

The Playground component:
- Displays extractor details using the Extractor component
- Provides a form for text input or file upload
- Allows selection of different LLM models for extraction
- Runs the extraction process
- Displays results in both table and JSON formats

Sources: [frontend/app/components/Playground.tsx:29-196]()

### ResultsTable Component

The ResultsTable component displays extraction results in a tabular format, dynamically determining columns based on the extracted data.

```mermaid
flowchart LR
    subgraph "ResultsTable Component"
        Input["Extraction Response Data"]
        Process["Column Analysis"]
        Display["Table Rendering"]
        
        Input --> Process
        Process --> Display
    end
    
    subgraph "Helper Functions"
        isRecord["isRecord(value)"]
        getColumns["getColumns(records)"]
        getDisplayValue["getDisplayValue(value)"]
    end
    
    Process --> getColumns
    Display --> getDisplayValue
    getColumns --> isRecord
    getDisplayValue --> isRecord
```

Key features:
- Dynamically determines table columns from extraction results
- Formats complex data types (arrays, objects) into readable strings
- Shows a loading spinner during extraction
- Displays extracted data in rows and columns

Sources: [frontend/app/components/ResultsTable.tsx:1-120]()

## API Integration

The frontend uses a set of React Query hooks to communicate with the backend API. These hooks manage API requests, caching, and state updates.

```mermaid
classDiagram
    class APIHooks {
        +useConfiguration()
        +useGetExtractor()
        +useGetExtractors()
        +useCreateExtractor()
        +useDeleteExtractor()
        +useRunExtraction()
    }
    
    class AxiosClient {
        +headers: x-key
        +get()
        +post()
        +delete()
        +postForm()
    }
    
    class ReactQuery {
        +useQuery()
        +useMutation()
        +useQueryClient()
    }
    
    APIHooks --> AxiosClient : uses
    APIHooks --> ReactQuery : built with
    
    class Functions {
        +getApiKey()
        +runExtraction()
        +suggestExtractor()
    }
    
    APIHooks --> Functions : exposes
```

The API hooks provide:
- Authentication through client-side API keys
- Functions for CRUD operations on extractors
- Methods for running extractions
- Configuration retrieval
- Suggestion functionality for extractors

Sources: [frontend/app/utils/api.tsx:1-184]()

## Data Flow

The following diagram illustrates how data flows through the frontend components when a user runs an extraction:

```mermaid
sequenceDiagram
    participant User
    participant Playground as "Playground Component"
    participant APIHooks as "API Hooks"
    participant Backend as "Backend API"
    participant ResultsTable as "ResultsTable Component"
    
    User->>Playground: Enters text or uploads file
    User->>Playground: Selects model
    User->>Playground: Clicks "Run"
    
    Playground->>APIHooks: Calls runExtraction()
    
    APIHooks->>Backend: POST /extract
    Backend-->>APIHooks: Returns extraction results
    
    APIHooks-->>Playground: Updates with results
    Playground->>ResultsTable: Passes extraction data
    ResultsTable->>ResultsTable: Analyzes columns
    ResultsTable->>ResultsTable: Formats data
    ResultsTable-->>User: Displays formatted results
```

When a user runs an extraction:
1. The user inputs text or uploads a file in the Playground component
2. The Playground component captures form data and calls the `runExtraction` function
3. The request is sent to the backend API with the extractor ID, input data, and model selection
4. The backend processes the extraction and returns results
5. The ResultsTable component receives the data, analyzes it to determine columns, and displays it

Sources: [frontend/app/components/Playground.tsx:50-65](), [frontend/app/utils/api.tsx:130-141]()

## User Interface Components

The frontend uses Chakra UI components for a consistent and responsive interface:

```mermaid
flowchart TD
    subgraph "Chakra UI Components"
        ChakraCore["Chakra UI Core"]
        
        ChakraCore --> Forms["Form Components"]
        ChakraCore --> Layout["Layout Components"]
        ChakraCore --> Feedback["Feedback Components"]
        ChakraCore --> Navigation["Navigation Components"]
        
        Forms --> Button["Button"]
        Forms --> Input["Input"]
        Forms --> Textarea["Textarea"]
        Forms --> Radio["Radio"]
        Forms --> RadioGroup["RadioGroup"]
        
        Layout --> Box["Box"]
        Layout --> Divider["Divider"]
        Layout --> HStack["HStack"]
        
        Feedback --> Spinner["Spinner"]
        
        Navigation --> Tabs["Tabs"]
        Navigation --> TabList["TabList"]
        Navigation --> Tab["Tab"]
        Navigation --> TabPanels["TabPanels"]
        Navigation --> TabPanel["TabPanel"]
    end
    
    subgraph "Custom Components"
        Playground["Playground"]
        ResultsTable["ResultsTable"]
    end
    
    Playground --> Forms
    Playground --> Layout
    Playground --> Navigation
    
    ResultsTable --> Feedback
    ResultsTable --> Table["Table Components"]
```

Key UI elements include:
- Form controls for text input and file upload
- Radio buttons for model selection
- Tabs for switching between table and JSON views
- Spinners for loading states
- Tables for displaying structured data

Sources: [frontend/app/components/Playground.tsx:2-20](), [frontend/app/components/ResultsTable.tsx:1-11]()

## Component State Management

The frontend components use React hooks for state management and API communication:

| Hook Type | Usage | Example |
|-----------|-------|---------|
| useState | Local component state | Managing form state, disabled buttons |
| useMutation | API mutations | Running extractions, creating extractors |
| useQuery | Data fetching | Getting extractors, configuration |
| useQueryClient | Cache invalidation | Refreshing lists after mutations |

The Playground component uses state to:
- Track whether the form is valid for submission
- Handle the extraction request and response
- Manage loading states during extraction

Sources: [frontend/app/components/Playground.tsx:43-48](), [frontend/app/utils/api.tsx:94-98](), [frontend/app/utils/api.tsx:147-152]()

---

