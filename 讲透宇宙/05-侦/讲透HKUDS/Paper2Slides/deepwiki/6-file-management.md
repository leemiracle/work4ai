<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/Paper2Slides · page 6 File Management · fetched 2026-11-09 -->

# File Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [api/server.py](api/server.py)

</details>



## Purpose and Scope

This document explains how Paper2Slides organizes and manages files throughout the document processing lifecycle. It covers the storage of uploaded source files, the hierarchical organization of generated outputs, and the checkpoint system that enables resumable processing.

For details on the internal structure of checkpoint files, see [Checkpoint Files](#6.2). For information about the `state.json` file and pipeline progress tracking, see [State Management](#6.3). For the complete directory hierarchy reference, see [Directory Structure](#6.1).

---

## Storage Architecture Overview

Paper2Slides maintains two primary storage locations for file management:

| Directory | Purpose | Location | Managed By |
|-----------|---------|----------|------------|
| `UPLOAD_DIR` | Stores user-uploaded source files organized by session | `sources/uploads/` | [api/server.py:34]() |
| `OUTPUT_DIR` | Stores generated outputs, checkpoints, and state files | `outputs/` | [api/server.py:35]() |

The separation between uploads and outputs enables:
- **Session-based upload management**: Files grouped by unique session identifiers
- **Configuration-based output isolation**: Different parameter combinations produce separate outputs
- **Checkpoint reusability**: Intermediate results shared across regenerations with different styling

**Sources:** [api/server.py:34-37](), [README.md:234-254]()

---

## Upload Directory Structure

### Session-Based Organization

Uploaded files are stored in session-specific directories under `sources/uploads/`:

```mermaid
graph TB
    UploadDir["UPLOAD_DIR<br/>sources/uploads/"]
    Session1["session_id_1/<br/>(UUID)"]
    Session2["session_id_2/<br/>(UUID)"]
    Files1["paper.pdf<br/>report.docx<br/>data.xlsx"]
    Files2["research.pdf"]
    
    UploadDir --> Session1
    UploadDir --> Session2
    Session1 --> Files1
    Session2 --> Files2
```

### Session ID Generation

When files are uploaded through the web interface, a unique session identifier is generated:

```mermaid
sequenceDiagram
    participant Client as "Web Client"
    participant API as "/api/chat endpoint"
    participant FS as "File System"
    
    Client->>API: "POST /api/chat<br/>files=[paper.pdf]"
    API->>API: "session_id = uuid.uuid4()"
    API->>FS: "Create UPLOAD_DIR/session_id/"
    API->>FS: "Save files to session dir"
    API-->>Client: "Return session_id"
```

The session ID serves multiple purposes:

| Purpose | Implementation |
|---------|----------------|
| **File isolation** | Each upload batch stored separately | 
| **File reuse** | Regeneration with different parameters reuses existing files |
| **Tracking** | Links uploaded files to generated outputs via `state.json` |

**Code Reference:**
- Session ID generation: [api/server.py:204]()
- Session directory creation: [api/server.py:205-206]()
- File saving logic: [api/server.py:222-234]()

### File Reuse for Regeneration

When regenerating with different parameters, the API accepts an existing `session_id` to reuse uploaded files:

```mermaid
graph LR
    Upload["Initial Upload<br/>session_abc123"]
    Files["paper.pdf<br/>figures.pptx"]
    Gen1["Generation 1<br/>style=academic"]
    Gen2["Generation 2<br/>style=doraemon"]
    Gen3["Generation 3<br/>length=long"]
    
    Upload --> Files
    Files --> Gen1
    Files --> Gen2
    Files --> Gen3
    
    Gen1 -.->|"Reuse files"| Gen2
    Gen2 -.->|"Reuse files"| Gen3
```

**Sources:** [api/server.py:179-196](), [api/server.py:210-219]()

---

## Output Directory Hierarchy

### Hierarchical Path Encoding

Generated outputs use a hierarchical directory structure that encodes processing context:

```
outputs/
└── <content_type>/           # "paper" or "general"
    └── <project_name>/       # From PDF name or session_id
        └── <mode>/           # "fast" or "normal"
            ├── checkpoint_rag.json
            ├── checkpoint_summary.json
            ├── summary.md
            └── <config_hash>/    # e.g., "slides_doraemon_medium"
                ├── checkpoint_plan.json
                ├── state.json
                └── <timestamp>/  # YYYYMMDD_HHMMSS
                    ├── slide_01.png
                    ├── slide_02.png
                    └── slides.pdf
```

### Path Component Functions

```mermaid
graph TB
    subgraph "Path Components"
        Content["content_type<br/>'paper' or 'general'"]
        Project["project_name<br/>PDF name or session_id"]
        Mode["mode<br/>'fast' or 'normal'"]
        Config["config_hash<br/>'outputtype_style_length'"]
        Time["timestamp<br/>'YYYYMMDD_HHMMSS'"]
    end
    
    subgraph "Reuse Boundaries"
        ModeBoundary["Mode Level<br/>RAG & Summary checkpoints"]
        ConfigBoundary["Config Level<br/>Plan checkpoint"]
        TimeBoundary["Timestamp Level<br/>Final outputs"]
    end
    
    Content --> Project
    Project --> Mode
    Mode --> ModeBoundary
    Mode --> Config
    Config --> ConfigBoundary
    Config --> Time
    Time --> TimeBoundary
```

| Component | Determines | Example Values |
|-----------|------------|----------------|
| `content_type` | Processing strategy | `paper`, `general` |
| `project_name` | Source document grouping | `deepseek_v3_paper`, `session_a3f4b2c1` |
| `mode` | RAG indexing behavior | `normal`, `fast` |
| `config_hash` | Output configuration | `slides_doraemon_medium`, `poster_academic_dense` |
| `timestamp` | Generation time | `20250115_143022` |

**Sources:** [README.md:234-254](), [api/server.py:374-376]()

### Project Name Resolution

The `project_name` component is determined by file input:

```mermaid
graph TB
    Input{"Input Type"}
    Single["Single PDF"]
    Multiple["Multiple PDFs"]
    
    PDFName["get_project_name(pdf_path)<br/>Extract from filename"]
    SessionName["session_&lt;session_id[:8]&gt;<br/>Use short session ID"]
    
    ProjectSingle["project_name = PDF stem"]
    ProjectMulti["project_name = 'session_abc12345'"]
    
    Input -->|"len(pdf_paths) == 1"| Single
    Input -->|"len(pdf_paths) > 1"| Multiple
    
    Single --> PDFName
    Multiple --> SessionName
    
    PDFName --> ProjectSingle
    SessionName --> ProjectMulti
```

**Code Reference:**
- Single PDF: [api/server.py:357]()
- Multiple PDFs: [api/server.py:351]()
- Project name function: [api/server.py:30]()

---

## Checkpoint System Architecture

### Checkpoint Placement Strategy

Checkpoints are strategically placed at different directory levels to maximize reusability:

```mermaid
graph TB
    subgraph "Mode Level - Reusable Across Styles"
        RAG["checkpoint_rag.json<br/>Document parsing & indexing"]
        Summary["checkpoint_summary.json<br/>Content extraction"]
    end
    
    subgraph "Config Level - Style-Specific"
        Plan["checkpoint_plan.json<br/>Layout blueprint"]
        State["state.json<br/>Progress tracking"]
    end
    
    subgraph "Timestamp Level - Generation Outputs"
        Images["slide_*.png<br/>Generated images"]
        PDF["slides.pdf or poster.pdf<br/>Final PDF"]
    end
    
    RAG -.->|"Reuse if inputs unchanged"| Summary
    Summary -.->|"Reuse if inputs unchanged"| Plan
    Plan -.->|"Reuse if config unchanged"| State
    State -.->|"New timestamp per generation"| Images
    Images --> PDF
```

### Reusability Conditions

| Checkpoint File | Location | Reusable When | Skip Stages |
|-----------------|----------|---------------|-------------|
| `checkpoint_rag.json` | `mode/` | Input files unchanged | None (required) |
| `checkpoint_summary.json` | `mode/` | Input files + content type unchanged | RAG |
| `checkpoint_plan.json` | `config_hash/` | Style + length/density unchanged | RAG + Summary |
| Final outputs | `timestamp/` | Never reused (always regenerated) | RAG + Summary + Plan |

### Path Resolution Functions

The system uses helper functions to compute directory paths based on configuration:

```mermaid
graph LR
    GetBase["get_base_dir()<br/>OUTPUT_DIR/content_type/project_name/mode/"]
    GetConfig["get_config_dir()<br/>base_dir/config_hash/"]
    GetName["get_config_name()<br/>outputtype_style_length"]
    
    Config["Configuration<br/>Dict"]
    BasePath["Base Directory<br/>Path"]
    ConfigPath["Config Directory<br/>Path"]
    
    Config --> GetBase
    GetBase --> BasePath
    BasePath --> GetConfig
    Config --> GetConfig
    GetConfig --> ConfigPath
    
    Config --> GetName
    GetName --> GetConfig
```

**Code Reference:**
- `get_base_dir()`: [api/server.py:27]()
- `get_config_dir()`: [api/server.py:27]()
- `get_config_name()`: [api/server.py:28]()
- Usage: [api/server.py:374-376]()

**Sources:** [README.md:256-261](), [api/server.py:374-404]()

---

## File Access and Serving

### Static File Mounting

The FastAPI server mounts both storage directories as static file endpoints:

| Mount Point | Directory | Purpose |
|-------------|-----------|---------|
| `/outputs` | `OUTPUT_DIR` | Serve generated slides/posters |
| `/uploads` | `UPLOAD_DIR` | Serve uploaded source files |

**Code Reference:** [api/server.py:97-99]()

### URL Construction

Generated files are accessible via HTTP URLs constructed from their relative paths:

```mermaid
sequenceDiagram
    participant Client as "Frontend"
    participant API as "/api/result"
    participant FS as "File System"
    
    Client->>API: "GET /api/result/{session_id}"
    API->>FS: "Find files in config_dir"
    FS-->>API: "output_files list"
    API->>API: "Build URLs:<br/>/outputs/{relative_path}"
    API-->>Client: "slides: [<br/>  {image_url: '/outputs/...'}<br/>]"
    Client->>Client: "Render images"
```

**Example URL Construction:**

```
File Path:
  outputs/paper/deepseek_paper/normal/slides_doraemon_medium/20250115_143022/slide_01.png

Relative Path (from OUTPUT_DIR):
  paper/deepseek_paper/normal/slides_doraemon_medium/20250115_143022/slide_01.png

Served URL:
  http://localhost:8001/outputs/paper/deepseek_paper/normal/slides_doraemon_medium/20250115_143022/slide_01.png
```

**Code Reference:**
- File discovery: [api/server.py:411-424]()
- URL construction: [api/server.py:695-701]()

---

## File Discovery and State Tracking

### Finding State Files by Session

The API must locate state files to track progress. It searches for `state.json` files matching the session ID:

```mermaid
graph TB
    Request["GET /api/status/{session_id}"]
    FindPDF["Find PDFs in<br/>UPLOAD_DIR/session_id/"]
    GetProject["Determine project_name"]
    
    SearchPaper["Search base_dir<br/>content_type='paper'"]
    SearchGeneral["Search base_dir<br/>content_type='general'"]
    
    FindState["Locate state.json files<br/>base_dir.rglob('state.json')"]
    
    Match{"state.session_id<br/>== session_id?"}
    Fallback{"Most recent<br/>updated_at?"}
    
    ReturnState["Return state data"]
    
    Request --> FindPDF
    FindPDF --> GetProject
    GetProject --> SearchPaper
    GetProject --> SearchGeneral
    SearchPaper --> FindState
    SearchGeneral --> FindState
    FindState --> Match
    Match -->|"Yes (exact match)"| ReturnState
    Match -->|"No"| Fallback
    Fallback -->|"Yes"| ReturnState
```

**Matching Priority:**

1. **Exact match**: `state["session_id"] == session_id` (highest priority)
2. **Most recent**: Fallback to most recent `updated_at` timestamp

**Code Reference:** [api/server.py:550-643]()

**Sources:** [api/server.py:550-643](), [api/server.py:374-404]()

---

## Security and Path Validation

### Upload Path Safety

Session IDs are UUIDs, preventing directory traversal attacks in upload paths:

```python
session_id = str(uuid.uuid4())  # e.g., "a3f4b2c1-..."
session_dir = UPLOAD_DIR / session_id  # Safe: no ".." possible
```

### Download Path Validation

The download endpoint validates that requested files are within `OUTPUT_DIR`:

```mermaid
graph TB
    Request["GET /api/download/{filepath:path}"]
    Construct["file_path = OUTPUT_DIR / filepath"]
    Resolve["Resolve absolute paths"]
    
    Check{"file_path starts with<br/>OUTPUT_DIR?"}
    Exists{"File exists?"}
    
    Serve["Return FileResponse"]
    Deny403["HTTP 403 Forbidden"]
    Deny404["HTTP 404 Not Found"]
    
    Request --> Construct
    Construct --> Resolve
    Resolve --> Check
    Check -->|"No"| Deny403
    Check -->|"Yes"| Exists
    Exists -->|"No"| Deny404
    Exists -->|"Yes"| Serve
```

**Code Reference:** [api/server.py:729-750]()

**Sources:** [api/server.py:206](), [api/server.py:729-750]()

---

## Multi-File Processing

### Handling Multiple PDFs

When multiple PDFs are uploaded in a single session, they are processed as a unified project:

```mermaid
graph TB
    Upload["Upload Multiple PDFs<br/>paper1.pdf, paper2.pdf, paper3.pdf"]
    SessionDir["UPLOAD_DIR/session_abc123/"]
    
    Check{"len(pdf_paths) > 1?"}
    
    MultiProject["project_name =<br/>'session_abc12345'"]
    SingleProject["project_name =<br/>get_project_name(pdf_path)"]
    
    MultiInput["input_path =<br/>session directory"]
    SingleInput["input_path =<br/>PDF file path"]
    
    Config["Build config with:<br/>input_path<br/>pdf_paths (list)"]
    
    Pipeline["Run pipeline with<br/>all PDFs combined"]
    
    Upload --> SessionDir
    SessionDir --> Check
    
    Check -->|"Yes"| MultiProject
    Check -->|"No"| SingleProject
    
    MultiProject --> MultiInput
    SingleProject --> SingleInput
    
    MultiInput --> Config
    SingleInput --> Config
    
    Config --> Pipeline
```

**Configuration Differences:**

| Scenario | `input_path` | `pdf_paths` | `project_name` |
|----------|--------------|-------------|----------------|
| Single PDF | `/path/to/paper.pdf` | `['/path/to/paper.pdf']` | `paper` |
| Multiple PDFs | `/uploads/session_id/` | `['.../paper1.pdf', '.../paper2.pdf']` | `session_a3f4b2c1` |

**Code Reference:**
- Multi-file detection: [api/server.py:349-359]()
- Config construction: [api/server.py:362-372]()

**Sources:** [api/server.py:323-372]()

---

## Summary

Paper2Slides implements a sophisticated file management system with:

- **Session-based uploads**: Isolated file storage per upload batch
- **Hierarchical outputs**: Configuration-encoded directory structure
- **Strategic checkpoints**: Placed at mode/config levels for optimal reuse
- **Path safety**: UUID-based sessions and validated download paths
- **Multi-file support**: Unified processing of multiple documents

This architecture enables efficient regeneration scenarios where style changes reuse expensive parsing and analysis work, while maintaining isolation between different configurations.

**Sources:** [api/server.py:1-773](), [README.md:234-254]()

---

