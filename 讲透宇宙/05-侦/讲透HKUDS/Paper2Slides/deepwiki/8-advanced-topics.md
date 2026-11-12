<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/Paper2Slides · page 8 Advanced Topics · fetched 2026-11-09 -->

# Advanced Topics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [api/server.py](api/server.py)

</details>



This section covers advanced use cases, optimization strategies, and best practices for the Paper2Slides system. It is intended for users who want to understand deeper system behavior, optimize performance for specific scenarios, or troubleshoot complex issues.

**Scope**: This page provides an overview of advanced topics including concurrency control, checkpoint reuse strategies, resource optimization, and error recovery patterns. For specific guidance, see:
- Error handling details: [Error Handling and Recovery](#8.1)
- Performance tuning: [Performance Optimization](#8.2)  
- Issue resolution: [Troubleshooting Guide](#8.3)

Configuration basics are covered in [Configuration Guide](#5). This page assumes familiarity with the 4-stage pipeline architecture described in [Core Pipeline Architecture](#2).

---

## Session Management and Concurrency

The web interface enforces single-threaded execution to prevent resource conflicts and ensure predictable behavior. The `SessionManager` class coordinates request handling and prevents concurrent pipeline execution.

### Session Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Idle: "System ready"
    
    Idle --> SessionAcquired: "POST /api/chat\nSessionManager.start_session()"
    SessionAcquired --> Running: "Background task starts"
    
    Running --> Completed: "Pipeline succeeds"
    Running --> Failed: "Pipeline throws exception"
    Running --> Cancelled: "POST /api/cancel/{session_id}"
    
    Completed --> Idle: "SessionManager.end_session()"
    Failed --> Idle: "SessionManager.end_session()"
    Cancelled --> Idle: "SessionManager.end_session()"
    
    SessionAcquired --> Rejected: "Another session already running"
    Rejected --> [*]: "HTTP 409 Conflict"
    
    note right of Running
        SessionManager tracks:
        - running_session ID
        - cancelled_sessions set
    end note
    
    note right of Rejected
        Only one session can
        run at a time
    end note
```

**Sources**: [api/server.py:45-84](), [api/server.py:176-202]()

### Concurrency Control Implementation

The `SessionManager` uses an asyncio lock to provide thread-safe session coordination:

| Method | Purpose | Return Value |
|--------|---------|--------------|
| `start_session(session_id)` | Attempt to acquire execution lock | `True` if acquired, `False` if busy |
| `end_session(session_id)` | Release execution lock | None |
| `cancel_session(session_id)` | Mark session for cancellation | `True` if was running |
| `is_cancelled(session_id)` | Check cancellation status | Boolean |
| `get_running_session()` | Get current session ID | Session ID or `None` |

When a request arrives while another session is running, the API returns HTTP 409 (Conflict) with the running session ID. The frontend detects this and displays a "generation in progress" message.

**Sources**: [api/server.py:45-84](), [api/server.py:121-128]()

### Session Cancellation

```mermaid
sequenceDiagram
    participant User
    participant Frontend as "React Frontend"
    participant API as "FastAPI /api/cancel"
    participant SM as "SessionManager"
    participant BG as "Background Task"
    
    User->>Frontend: "Click Cancel"
    Frontend->>API: "POST /api/cancel/{session_id}"
    API->>SM: "cancel_session(session_id)"
    SM->>SM: "Add to cancelled_sessions set"
    SM-->>API: "True (was running)"
    API-->>Frontend: "{cancelled: true}"
    
    Note over BG: "Pipeline continues running"
    
    BG->>BG: "Between stages..."
    BG->>SM: "is_cancelled(session_id)?"
    SM-->>BG: "True"
    BG->>BG: "Raise cancellation exception"
    BG->>SM: "end_session(session_id)"
    
    Note over BG: "Session cleaned up"
```

The cancellation mechanism is cooperative - the pipeline checks `session_manager.is_cancelled()` between stages rather than forcefully terminating threads. This allows graceful cleanup and prevents partial state corruption.

**Sources**: [api/server.py:131-142](), [api/server.py:520-523]()

---

## Checkpoint Reuse Strategy

The checkpoint system enables selective regeneration by caching intermediate results. Understanding checkpoint placement and reusability is key to efficient iteration.

### Checkpoint Hierarchy

```mermaid
graph TB
    subgraph "Inputs"
        InputFiles["Input Files<br/>(PDFs, docs)"]
        Config["Configuration<br/>(style, length, etc)"]
    end
    
    subgraph "Mode Level - Reusable Across Configs"
        RAGChk["checkpoint_rag.json<br/>• Document parsing<br/>• Text extraction<br/>• RAG index"]
        SummChk["checkpoint_summary.json<br/>• Content hierarchy<br/>• Figures/tables<br/>• Key sections"]
        SummMD["summary.md<br/>• Human-readable<br/>• Not used by pipeline"]
    end
    
    subgraph "Config Level - Specific to Style/Size"
        PlanChk["checkpoint_plan.json<br/>• Slide layout<br/>• Content selection<br/>• Style interpretation"]
        StateFile["state.json<br/>• Pipeline progress<br/>• Session tracking<br/>• Error status"]
    end
    
    subgraph "Timestamp Level - Final Outputs"
        Images["slide_01.png<br/>slide_02.png<br/>..."]
        PDF["slides.pdf or<br/>poster.pdf"]
    end
    
    InputFiles --> RAGChk
    InputFiles --> SummChk
    Config --> PlanChk
    
    RAGChk -.reuse if.-> InputFiles
    SummChk -.reuse if.-> InputFiles
    PlanChk -.reuse if.-> Config
    
    RAGChk --> SummChk
    SummChk --> PlanChk
    PlanChk --> Images
    Images --> PDF
    
    StateFile -.tracks.-> PlanChk
    StateFile -.tracks.-> Images
```

**Sources**: [README.md:233-262](), [api/server.py:373-404]()

### Reuse Decision Logic

The system automatically determines the starting stage based on existing checkpoints:

| Scenario | Starting Stage | Checkpoints Reused | Typical Use Case |
|----------|---------------|-------------------|------------------|
| First run on document | `rag` | None | Initial generation |
| Same inputs, different style | `plan` | RAG + Summary | Style experimentation |
| Same inputs+style, regenerate | `generate` | RAG + Summary + Plan | Image regeneration |
| User forces `--from-stage` | User-specified | All stages before | Manual control |
| Fast mode enabled | `summary` | None (RAG skipped) | Quick preview |

The `detect_start_stage()` function implements this logic by checking for checkpoint file existence:

```mermaid
graph TD
    Start["detect_start_stage()"] --> CheckForce{"--from-stage<br/>specified?"}
    
    CheckForce -->|"Yes"| ReturnForced["Return forced stage"]
    CheckForce -->|"No"| CheckGen{"checkpoint_plan.json<br/>exists?"}
    
    CheckGen -->|"Yes"| CheckImages{"Timestamped<br/>output exists?"}
    CheckImages -->|"Yes"| ReturnGen["Return 'generate'<br/>(regenerate images)"]
    CheckImages -->|"No"| ReturnGen
    
    CheckGen -->|"No"| CheckSumm{"checkpoint_summary.json<br/>exists?"}
    CheckSumm -->|"Yes"| ReturnPlan["Return 'plan'<br/>(create new plan)"]
    CheckSumm -->|"No"| CheckRAG{"checkpoint_rag.json<br/>exists?"}
    
    CheckRAG -->|"Yes"| ReturnSumm["Return 'summary'<br/>(extract content)"]
    CheckRAG -->|"No"| ReturnRAG["Return 'rag'<br/>(full pipeline)"]
```

**Sources**: [api/server.py:388-404](), [README.md:153-165]()

---

## Fast Mode Optimization

Fast mode trades indexing overhead for speed by skipping RAG stage when documents are small enough to fit in LLM context windows.

### Processing Path Comparison

```mermaid
graph TB
    subgraph "Normal Mode - Deep Analysis"
        N1["parse_documents()<br/>Extract all text"]
        N2["build_rag_index()<br/>Chunk + embed + index"]
        N3["query_rag(question)<br/>Retrieve relevant chunks"]
        N4["analyze_with_llm()<br/>Process retrieved context"]
        
        N1 --> N2
        N2 --> N3
        N3 --> N4
    end
    
    subgraph "Fast Mode - Direct Query"
        F1["parse_documents()<br/>Extract all text"]
        F2["analyze_with_llm()<br/>Process full document"]
        
        F1 --> F2
    end
    
    Decision{"fast_mode=true<br/>AND<br/>content_type='paper'"}
    
    Decision -->|"Yes"| F1
    Decision -->|"No"| N1
    
    style N2 fill:#ffe6e6
    style N3 fill:#ffe6e6
    
    Note1["RAG indexing overhead:<br/>• Chunking strategy<br/>• Embedding generation<br/>• Vector index build"]
    Note2["Direct LLM benefits:<br/>• No chunking artifacts<br/>• Full context preserved<br/>• Faster for short docs"]
    
    N2 -.-> Note1
    F2 -.-> Note2
```

**Sources**: [README.md:212-228](), [api/server.py:371-372]()

### When to Use Fast Mode

| Document Characteristics | Recommended Mode | Reason |
|--------------------------|------------------|--------|
| Single PDF < 10 pages | Fast | Fits in LLM context |
| Multiple files | Normal | Need retrieval for relevant content |
| Complex figures/tables | Normal | Better figure extraction with RAG |
| Quick preview needed | Fast | Skip indexing overhead |
| Conference paper (8-10 pages) | Either | Depends on complexity |
| Technical report (50+ pages) | Normal | Requires retrieval |

Fast mode only applies when `content_type='paper'`. General content always uses normal mode since it may lack academic structure that RAG helps parse.

**Sources**: [README.md:219-228](), [api/server.py:371-372]()

---

## State Tracking and Progress Monitoring

The `state.json` file tracks pipeline execution and enables progress polling in the web interface.

### State File Structure

```mermaid
graph LR
    subgraph "state.json Fields"
        Config["config:<br/>• output_type<br/>• style<br/>• length/density<br/>• fast_mode"]
        
        Stages["stages:<br/>• rag: status<br/>• summary: status<br/>• plan: status<br/>• generate: status"]
        
        Meta["metadata:<br/>• session_id<br/>• created_at<br/>• updated_at<br/>• error (if failed)"]
    end
    
    Status1["Status values:<br/>• 'pending'<br/>• 'running'<br/>• 'completed'<br/>• 'failed'"]
    
    Stages --> Status1
```

**Sources**: [api/server.py:392-404](), [api/server.py:623-638]()

### Progress Polling Flow

The frontend polls `/api/status/{session_id}` to track progress:

```mermaid
sequenceDiagram
    participant FE as "Frontend"
    participant API as "/api/status"
    participant FS as "File System"
    
    loop "Every 2-3 seconds"
        FE->>API: "GET /api/status/{session_id}"
        API->>FS: "Find state.json for session"
        
        alt "State file found"
            FS-->>API: "state.json contents"
            API->>API: "Determine overall status"
            
            alt "All stages completed"
                API-->>FE: "{status: 'completed'}"
                FE->>FE: "Stop polling"
                FE->>API: "GET /api/result/{session_id}"
            end
            
            alt "Any stage running"
                API-->>FE: "{status: 'running', stages: {...}}"
                FE->>FE: "Update progress UI"
            end
            
            alt "Any stage failed"
                API-->>FE: "{status: 'failed', error: '...'}"
                FE->>FE: "Stop polling, show error"
            end
        end
        
        alt "State file not found"
            API-->>FE: "{status: 'pending'}"
            FE->>FE: "Continue polling"
        end
    end
```

**Sources**: [api/server.py:550-643]()

### Error State Management

When a background task fails, the system updates `state.json` to mark the failed stage:

```mermaid
graph TD
    Exception["Exception in<br/>background task"] --> Catch["Exception caught<br/>in try/except"]
    
    Catch --> Store["Store error in<br/>app.state.results"]
    Catch --> Update["Call _update_state_on_error()"]
    
    Update --> Load["Load existing state.json"]
    Load --> Find["Find stage with<br/>status='running'"]
    Find --> Mark["Set stage status='failed'"]
    Mark --> AddError["Add error message<br/>to state"]
    AddError --> Save["save_state(config_dir, state)"]
    
    Store --> Finally["Finally block:<br/>end_session()"]
    Save --> Finally
    
    Finally --> Release["Release session lock"]
```

This ensures the frontend can detect failures through status polling and display appropriate error messages.

**Sources**: [api/server.py:433-486](), [api/server.py:532-546]()

---

## Resource Management Strategies

### Memory Optimization

The system handles large files through streaming and chunked processing:

| Component | Strategy | Implementation |
|-----------|----------|----------------|
| File uploads | 1MB chunk streaming | [api/server.py:225-228]() |
| PDF parsing | Page-by-page processing | RAG parser |
| Image generation | Single-image iteration | [README.md:273-279]() |
| Output delivery | Static file serving | [api/server.py:96-99]() |

### Directory Organization for Cache Efficiency

The hierarchical output structure enables efficient checkpoint reuse:

```
outputs/
└── {project_name}/
    └── {content_type}/              # paper or general
        └── {mode}/                  # fast or normal
            ├── checkpoint_rag.json       # ← Shared across all configs
            ├── checkpoint_summary.json   # ← Shared across all configs  
            └── {config_hash}/            # ← Unique per style/length/density
                ├── checkpoint_plan.json
                └── {timestamp}/
                    ├── slide_01.png
                    └── slides.pdf
```

This organization means:
- Changing only style regenerates from `plan` stage
- Multiple style experiments reuse the same RAG/summary work
- Each configuration maintains independent outputs
- Old outputs remain accessible by timestamp

**Sources**: [README.md:233-262](), [api/server.py:374-385]()

### API Server Configuration

The FastAPI server includes resource limits to prevent exhaustion:

| Parameter | Default Value | Purpose |
|-----------|---------------|---------|
| `timeout_keep_alive` | 300 seconds | Long-running generation support |
| `limit_concurrency` | 10 | Prevent connection exhaustion |
| `limit_max_requests` | 1000 | Request lifecycle limit |

These values balance responsiveness with stability for long-running document processing.

**Sources**: [api/server.py:765-772]()

---

## Configuration Hash System

The system generates configuration hashes to create unique directories for different parameter combinations:

```mermaid
graph LR
    Inputs["Configuration Inputs:<br/>• output_type<br/>• style<br/>• slides_length OR<br/>• poster_density"] --> Hash["get_config_name()"]
    
    Hash --> Format["Format:<br/>{output_type}_{style}_{size}"]
    
    Format --> Example1["slides_doraemon_medium"]
    Format --> Example2["poster_academic_dense"]
    Format --> Example3["slides_custom_short"]
    
    Example1 --> Dir1["outputs/.../slides_doraemon_medium/"]
    Example2 --> Dir2["outputs/.../poster_academic_dense/"]
    Example3 --> Dir3["outputs/.../slides_custom_short/"]
```

This ensures that:
- Different configurations never overwrite each other
- Each parameter set has its own checkpoint
- Users can regenerate with different styles without losing work

**Sources**: [api/server.py:362-372](), [README.md:243-250]()

---

## Best Practices Summary

### For Optimal Performance

1. **Use fast mode** for papers under 10 pages that fit in LLM context
2. **Reuse sessions** when experimenting with styles - pass `session_id` without new files
3. **Leverage checkpoints** - use `--from-stage` CLI flag to skip completed stages
4. **Organize inputs** - group related documents in a single session for coherent output

### For Reliable Operation

1. **Monitor state.json** - check pipeline progress and detect failures early
2. **Handle 409 conflicts** - only one generation can run at a time in web interface  
3. **Check cancellation** - system supports graceful cancellation between stages
4. **Validate uploads** - ensure at least one PDF is present before submission

### For Development

1. **Study SessionManager** - understand concurrency model before modifying API
2. **Test checkpoint reuse** - verify that stage skipping works correctly
3. **Handle long operations** - use background tasks and polling, not blocking requests
4. **Preserve state.json** - critical for progress tracking and error recovery

**Sources**: [README.md:212-228](), [api/server.py:45-84](), [api/server.py:489-547]()

---

