<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/scholarphi · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [api/src/api.ts](api/src/api.ts)
- [api/src/db-connection.ts](api/src/db-connection.ts)
- [api/src/tests/api.test.ts](api/src/tests/api.test.ts)
- [api/src/types/api.ts](api/src/types/api.ts)
- [api/src/types/validation.ts](api/src/types/validation.ts)
- [ui/README.md](ui/README.md)
- [ui/src/ScholarReader.tsx](ui/src/ScholarReader.tsx)
- [ui/src/state.ts](ui/src/state.ts)

</details>



This document provides a comprehensive overview of the Scholar Reader system, an augmented PDF reader for academic papers that enhances the reading experience through automated entity extraction and interactive annotations. The system comprises a React/TypeScript frontend, Node.js/Hapi.js backend API, and Python-based data processing pipeline.

For detailed information about the frontend components and UI architecture, see [Frontend (UI System)](#2). For backend API implementation details, see [Backend (API System)](#3). For data processing and entity extraction specifics, see [Data Processing Pipeline](#4).

## System Architecture

Scholar Reader operates as a three-tier system where academic papers flow through a processing pipeline to generate an interactive PDF reading experience with entity annotations.

```mermaid
graph TB
    subgraph "Data Sources"
        ARXIV["arXiv Papers"]
        S2API["Semantic Scholar API"]
        LATEX["LaTeX Documents"]
    end
    
    subgraph "Processing Layer"
        PIPELINE["Python Processing Pipeline"]
        EXTRACTORS["Entity Extractors"]
        MODELS["ML/NLP Models"]
        LOCALIZATION["Entity Localization"]
    end
    
    subgraph "Storage Layer"
        POSTGRES["PostgreSQL Database"]
        ENTITIES["Entity Tables"]
        PAPERS["Paper Tables"]
        BBOX["BoundingBox Tables"]
    end
    
    subgraph "API Layer"
        HAPI["Hapi.js Server"]
        CONNECTION["db-connection.ts"]
        ROUTES["api.ts Routes"]
        VALIDATION["validation.ts"]
    end
    
    subgraph "Frontend Layer"
        SCHOLARREADER["ScholarReader.tsx"]
        PDFJS["PDF.js Integration"]
        ANNOTATIONS["Entity Annotations"]
        STATE["Application State"]
    end
    
    ARXIV --> PIPELINE
    S2API --> HAPI
    LATEX --> PIPELINE
    
    PIPELINE --> EXTRACTORS
    EXTRACTORS --> MODELS
    MODELS --> LOCALIZATION
    LOCALIZATION --> POSTGRES
    
    POSTGRES --> ENTITIES
    POSTGRES --> PAPERS
    POSTGRES --> BBOX
    
    ENTITIES --> CONNECTION
    PAPERS --> CONNECTION
    BBOX --> CONNECTION
    CONNECTION --> HAPI
    HAPI --> ROUTES
    ROUTES --> VALIDATION
    
    HAPI --> SCHOLARREADER
    SCHOLARREADER --> PDFJS
    SCHOLARREADER --> ANNOTATIONS
    SCHOLARREADER --> STATE
```

Sources: [ui/src/ScholarReader.tsx:1-1160](), [api/src/api.ts:1-352](), [api/src/db-connection.ts:1-767](), [README.md:1-79]()

## Data Flow Architecture

The system transforms raw academic papers into interactive, annotated PDF experiences through a multi-stage pipeline.

```mermaid
graph LR
    subgraph "Input Processing"
        INPUT["Academic Papers"]
        PARSE["LaTeX/PDF Parsing"]
        EXTRACT["Entity Extraction"]
    end
    
    subgraph "Entity Types"
        CITATIONS["Citation Entities"]
        SYMBOLS["Symbol Entities"] 
        EQUATIONS["Equation Entities"]
        SENTENCES["Sentence Entities"]
        TERMS["Term Entities"]
    end
    
    subgraph "Database Storage"
        ENTITYTABLE["entity table"]
        ENTITYDATA["entitydata table"]
        BOUNDINGBOX["boundingbox table"]
        PAPER["paper table"]
    end
    
    subgraph "API Endpoints"
        GETENTITIES["/papers/{id}/entities"]
        GETPAPERS["/papers"]
        POSTENTITY["/papers/{id}/entities"]
        PATCHENTITY["/papers/{id}/entities/{id}"]
    end
    
    subgraph "Frontend Rendering"
        STATEMANAGEMENT["State interface"]
        PAGEOVERLAY["PageOverlay components"]
        ENTITYLAYERS["EntityAnnotationLayer"]
        PDFJSVIEWER["PDF.js Viewer"]
    end
    
    INPUT --> PARSE
    PARSE --> EXTRACT
    
    EXTRACT --> CITATIONS
    EXTRACT --> SYMBOLS
    EXTRACT --> EQUATIONS
    EXTRACT --> SENTENCES
    EXTRACT --> TERMS
    
    CITATIONS --> ENTITYTABLE
    SYMBOLS --> ENTITYTABLE
    EQUATIONS --> ENTITYTABLE
    SENTENCES --> ENTITYTABLE
    TERMS --> ENTITYTABLE
    
    ENTITYTABLE --> ENTITYDATA
    ENTITYTABLE --> BOUNDINGBOX
    ENTITYTABLE --> PAPER
    
    ENTITYDATA --> GETENTITIES
    BOUNDINGBOX --> GETENTITIES
    PAPER --> GETPAPERS
    
    GETENTITIES --> POSTENTITY
    GETENTITIES --> PATCHENTITY
    
    GETENTITIES --> STATEMANAGEMENT
    STATEMANAGEMENT --> PAGEOVERLAY
    PAGEOVERLAY --> ENTITYLAYERS
    ENTITYLAYERS --> PDFJSVIEWER
```

Sources: [api/src/types/api.ts:92-441](), [ui/src/state.ts:15-202](), [api/src/api.ts:178-268]()

## Core Component Architecture

The `ScholarReader` component serves as the main orchestrator, managing PDF viewing, entity annotations, and user interactions.

```mermaid
graph TB
    subgraph "ScholarReader.tsx Main Component"
        SCHOLARREADER["ScholarReader class"]
        STATE_MGMT["State Management"]
        LIFECYCLE["React Lifecycle Methods"]
        EVENT_HANDLERS["Event Handlers"]
    end
    
    subgraph "PDF Integration"
        PDFVIEWER["PDFViewerApplication"]
        PDFDOCUMENT["PDFDocumentProxy"]
        PAGEVIEWS["PDFPageView objects"]
        PAGES_STATE["Pages state property"]
    end
    
    subgraph "Entity Management"
        ENTITIES_STATE["entities: Entities"]
        ENTITY_CRUD["Entity CRUD operations"]
        SELECTION["Entity Selection Logic"]
        SEARCH["Find/Search Functionality"]
    end
    
    subgraph "UI Components"
        PAGEOVERLAY["PageOverlay"]
        ENTITYLAYER["EntityAnnotationLayer"]
        FINDBAR["FindBar"]
        DRAWER["Drawer"]
        TOOLBAR["Control Toolbars"]
    end
    
    subgraph "API Integration"
        API_CALLS["api.ts functions"]
        GETENTITIES["getDedupedEntities()"]
        POSTENTITY["postEntity()"]
        PATCHENTITY["patchEntity()"]
    end
    
    SCHOLARREADER --> STATE_MGMT
    SCHOLARREADER --> LIFECYCLE
    SCHOLARREADER --> EVENT_HANDLERS
    
    STATE_MGMT --> PDFVIEWER
    STATE_MGMT --> ENTITIES_STATE
    STATE_MGMT --> PAGES_STATE
    
    LIFECYCLE --> API_CALLS
    API_CALLS --> GETENTITIES
    API_CALLS --> POSTENTITY
    API_CALLS --> PATCHENTITY
    
    EVENT_HANDLERS --> ENTITY_CRUD
    EVENT_HANDLERS --> SELECTION
    EVENT_HANDLERS --> SEARCH
    
    SCHOLARREADER --> PAGEOVERLAY
    PAGEOVERLAY --> ENTITYLAYER
    SCHOLARREADER --> FINDBAR
    SCHOLARREADER --> DRAWER
    SCHOLARREADER --> TOOLBAR
    
    PDFVIEWER --> PDFDOCUMENT
    PDFDOCUMENT --> PAGEVIEWS
    PAGEVIEWS --> PAGES_STATE
```

Sources: [ui/src/ScholarReader.tsx:69-124](), [ui/src/ScholarReader.tsx:665-678](), [ui/src/ScholarReader.tsx:711-730]()

## Entity Type System

Scholar Reader supports five primary entity types, each with specific attributes and relationships defined in the type system.

| Entity Type | TypeScript Interface | Key Attributes | Primary Use Case |
|-------------|---------------------|----------------|------------------|
| Citation | `Citation` | `paper_id` | Reference to other papers |
| Symbol | `Symbol` | `tex`, `mathml`, `definitions` | Mathematical notation |
| Equation | `Equation` | `tex` | Mathematical expressions |
| Sentence | `Sentence` | `text`, `tex_start`, `tex_end` | Text segmentation |
| Term | `Term` | `name`, `definitions`, `term_type` | Technical vocabulary |

```mermaid
graph TB
    subgraph "Base Entity Structure"
        BASEENTITY["BaseEntity interface"]
        BASEID["id: string"]
        BASETYPE["type: EntityType"]
        BASEATTR["attributes: BaseEntityAttributes"]
        BASEREL["relationships: Relationships"]
    end
    
    subgraph "Entity Specializations"
        SYMBOL["Symbol extends BaseEntity"]
        CITATION["Citation extends BaseEntity"]
        EQUATION["Equation extends BaseEntity"]
        SENTENCE["Sentence extends BaseEntity"]
        TERM["Term extends BaseEntity"]
    end
    
    subgraph "Attribute Types"
        SYMBOLATTR["SymbolAttributes"]
        CITATIONATTR["CitationAttributes"] 
        EQUATIONATTR["EquationAttributes"]
        SENTENCEATTR["SentenceAttributes"]
        TERMATTR["TermAttributes"]
    end
    
    subgraph "Common Properties"
        BBOX["bounding_boxes: BoundingBox[]"]
        VERSION["version: number"]
        SOURCE["source: string"]
        TAGS["tags: string[]"]
    end
    
    BASEENTITY --> BASEID
    BASEENTITY --> BASETYPE
    BASEENTITY --> BASEATTR
    BASEENTITY --> BASEREL
    
    BASEENTITY --> SYMBOL
    BASEENTITY --> CITATION
    BASEENTITY --> EQUATION
    BASEENTITY --> SENTENCE
    BASEENTITY --> TERM
    
    SYMBOL --> SYMBOLATTR
    CITATION --> CITATIONATTR
    EQUATION --> EQUATIONATTR
    SENTENCE --> SENTENCEATTR
    TERM --> TERMATTR
    
    BASEATTR --> BBOX
    BASEATTR --> VERSION
    BASEATTR --> SOURCE
    BASEATTR --> TAGS
```

Sources: [api/src/types/api.ts:108-398](), [api/src/types/api.ts:114-123](), [ui/src/state.ts:151-159]()

## Database Schema Integration

The system uses PostgreSQL with a normalized schema that separates entity metadata, attributes, and spatial information.

```mermaid
graph TB
    subgraph "Core Tables"
        PAPER_TBL["paper table"]
        VERSION_TBL["version table"] 
        ENTITY_TBL["entity table"]
        ENTITYDATA_TBL["entitydata table"]
        BOUNDINGBOX_TBL["boundingbox table"]
    end
    
    subgraph "Connection Class Methods"
        GETENTITIES["getEntitiesForPaper()"]
        CREATEENTITY["createEntity()"]
        UPDATEENTITY["updateEntity()"]
        DELETEENTITY["deleteEntity()"]
        GETDEDUPED["getDedupedEntitiesForPaper()"]
    end
    
    subgraph "Entity Object Construction"
        CREATEOBJECT["createEntityObjectFromRows()"]
        UNPACKDATA["unpackEntityDataRows()"]
        CREATEBBOX["createBoundingBoxes()"]
        VALIDATION["validation.loadedEntity"]
    end
    
    subgraph "Query Builder"
        KNEX["Knex query builder"]
        QUERYBUILDER["createQueryBuilder()"]
        CONFIG["DBConfig interface"]
    end
    
    PAPER_TBL --> VERSION_TBL
    VERSION_TBL --> ENTITY_TBL
    ENTITY_TBL --> ENTITYDATA_TBL
    ENTITY_TBL --> BOUNDINGBOX_TBL
    
    GETENTITIES --> ENTITY_TBL
    GETENTITIES --> ENTITYDATA_TBL
    GETENTITIES --> BOUNDINGBOX_TBL
    
    CREATEENTITY --> ENTITY_TBL
    UPDATEENTITY --> ENTITY_TBL
    DELETEENTITY --> ENTITY_TBL
    
    GETENTITIES --> CREATEOBJECT
    CREATEOBJECT --> UNPACKDATA
    CREATEOBJECT --> CREATEBBOX
    CREATEOBJECT --> VALIDATION
    
    KNEX --> QUERYBUILDER
    QUERYBUILDER --> CONFIG
    KNEX --> GETENTITIES
    KNEX --> CREATEENTITY
```

Sources: [api/src/db-connection.ts:24-35](), [api/src/db-connection.ts:276-406](), [api/src/db-connection.ts:242-274]()

## API Route Structure

The Hapi.js server exposes RESTful endpoints for paper and entity management with validation and authentication.

| HTTP Method | Route Pattern | Handler Function | Purpose |
|-------------|---------------|------------------|---------|
| GET | `/papers/list` | Paper listing | Paginated paper discovery |
| GET | `/papers/{paperSelector}` | Paper existence check | Verify paper availability |
| GET | `/papers/{paperSelector}/entities` | `getEntitiesForPaper()` | Retrieve all entities |
| GET | `/papers/{paperSelector}/entities-deduped` | `getDedupedEntitiesForPaper()` | Optimized entity retrieval |
| POST | `/papers/{arxivSelector}/entities` | `createEntity()` | Create new entities |
| PATCH | `/papers/{arxivSelector}/entities/{id}` | `updateEntity()` | Modify existing entities |
| DELETE | `/papers/{arxivSelector}/entities/{id}` | `deleteEntity()` | Remove entities |

```mermaid
graph LR
    subgraph "Request Flow"
        CLIENT["Frontend Client"]
        VALIDATION_LAYER["Joi Validation"]
        AUTH_LAYER["Bearer Token Auth"]
        HANDLER["Route Handler"]
        DB_LAYER["Database Connection"]
    end
    
    subgraph "Validation Schemas" 
        PAPERSEL["paperSelector schema"]
        ENTITYPOST["entityPost schema"]
        ENTITYPATCH["entityPatch schema"]
        APITYPES["apiEntityTypes schema"]
    end
    
    subgraph "Database Operations"
        CONNECTION_CLASS["Connection class"]
        KNEX_QUERIES["Knex.js queries"]
        POSTGRES["PostgreSQL"]
    end
    
    CLIENT --> VALIDATION_LAYER
    VALIDATION_LAYER --> AUTH_LAYER
    AUTH_LAYER --> HANDLER
    HANDLER --> DB_LAYER
    
    VALIDATION_LAYER --> PAPERSEL
    VALIDATION_LAYER --> ENTITYPOST
    VALIDATION_LAYER --> ENTITYPATCH
    VALIDATION_LAYER --> APITYPES
    
    DB_LAYER --> CONNECTION_CLASS
    CONNECTION_CLASS --> KNEX_QUERIES
    KNEX_QUERIES --> POSTGRES
```

Sources: [api/src/api.ts:73-351](), [api/src/types/validation.ts:31-282](), [api/src/api.ts:55-70]()

The Scholar Reader system demonstrates a sophisticated architecture for enhancing academic paper consumption through automated entity extraction, spatial annotation, and interactive user interfaces. The modular design enables independent development of data processing, API services, and frontend components while maintaining strong type safety and data consistency throughout the system.

---

