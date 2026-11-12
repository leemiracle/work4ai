<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/Paper2Slides · page 2 Core Pipeline Architecture · fetched 2026-11-09 -->

# Core Pipeline Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [api/server.py](api/server.py)

</details>



## Purpose and Scope

This document describes the core 4-stage processing pipeline that transforms input documents into presentation materials. It covers the pipeline orchestration, stage sequencing, checkpoint mechanisms, and configuration flow. For detailed information about individual stages, see:
- Stage 1 (RAG): [Stage 1: RAG](#2.1)
- Stage 2 (Analysis): [Stage 2: Analysis and Content Extraction](#2.2)
- Stage 3 (Planning): [Stage 3: Planning and Layout](#2.3)
- Stage 4 (Creation): [Stage 4: Creation and Rendering](#2.4)
- Smart Recovery System: [Smart Recovery System](#2.5)

For user-facing configuration options, see [Configuration Guide](#5).

## Pipeline Overview

The Paper2Slides system processes documents through a linear 4-stage pipeline. Each stage produces checkpoint files that enable resumption and selective regeneration. The pipeline is orchestrated by the `run_pipeline` function in [paper2slides/core/pipeline.py]().

### Four Processing Stages

```mermaid
graph LR
    Input["Input Documents<br/>(PDF, MD, DOC, PPT)"]
    
    S1["Stage 1: rag<br/>RAG Indexing"]
    CP1[("checkpoint_rag.json")]
    
    S2["Stage 2: summary<br/>Content Extraction"]
    CP2[("checkpoint_summary.json")]
    
    S3["Stage 3: plan<br/>Layout Planning"]
    CP3[("checkpoint_plan.json")]
    
    S4["Stage 4: generate<br/>Image Generation"]
    Output["Output Files<br/>(PNG slides + PDF)"]
    
    Input --> S1
    S1 --> CP1
    CP1 --> S2
    S2 --> CP2
    CP2 --> S3
    S3 --> CP3
    CP3 --> S4
    S4 --> Output
```

**Stage Sequence**:
| Stage Number | Stage Name | Module | Primary Function | Checkpoint File |
|--------------|-----------|---------|------------------|-----------------|
| 1 | `rag` | `paper2slides.core.stages.rag_stage` | Document parsing and RAG indexing | `checkpoint_rag.json` |
| 2 | `summary` | `paper2slides.core.stages.summary_stage` | Extract structure, figures, tables | `checkpoint_summary.json` |
| 3 | `plan` | `paper2slides.core.stages.plan_stage` | Generate content layout blueprint | `checkpoint_plan.json` |
| 4 | `generate` | `paper2slides.core.stages.generate_stage` | Render final images and PDF | Output directory |

**Sources**: [README.md:202-207](), [paper2slides/core/pipeline.py]()

## Pipeline Orchestration

### Core Entry Points

The pipeline can be invoked through two interfaces that both converge on the same core execution logic:

```mermaid
graph TB
    CLI["CLI Interface<br/>python -m paper2slides"]
    Web["Web API Request<br/>POST /api/chat"]
    
    Main["paper2slides.main.main()"]
    Server["api.server.generate_slides_with_pipeline()"]
    
    RunPipeline["paper2slides.core.run_pipeline()"]
    
    DetectStage["detect_start_stage()"]
    ConfigDir["get_config_dir()"]
    BaseDir["get_base_dir()"]
    
    Stage1["run_rag_stage()"]
    Stage2["run_summary_stage()"]
    Stage3["run_plan_stage()"]
    Stage4["run_generate_stage()"]
    
    CLI --> Main
    Web --> Server
    Main --> RunPipeline
    Server --> RunPipeline
    
    RunPipeline --> DetectStage
    RunPipeline --> ConfigDir
    RunPipeline --> BaseDir
    
    DetectStage --> Stage1
    DetectStage --> Stage2
    DetectStage --> Stage3
    DetectStage --> Stage4
    
    Stage1 --> Stage2
    Stage2 --> Stage3
    Stage3 --> Stage4
```

**Sources**: [api/server.py:294-430](), [paper2slides/main.py](), [paper2slides/core/pipeline.py]()

### Configuration Resolution

Before pipeline execution, the system resolves directory paths and determines which stage to start from:

```mermaid
graph TB
    Config["Configuration Object<br/>{content_type, output_type,<br/>style, length/density, fast_mode}"]
    
    ProjName["get_project_name()<br/>Extract from PDF filename<br/>or use session_id"]
    
    BaseDir["get_base_dir()<br/>outputs/&lt;project&gt;/&lt;content_type&gt;"]
    
    ModeDir["Mode Directory<br/>fast/ or normal/"]
    
    ConfigDir["get_config_dir()<br/>hash of output_type_style_size"]
    
    DetectStage["detect_start_stage()<br/>Check existing checkpoints"]
    
    FromStage["from_stage<br/>rag | summary | plan | generate"]
    
    Config --> ProjName
    ProjName --> BaseDir
    Config --> BaseDir
    BaseDir --> ModeDir
    Config --> ModeDir
    ModeDir --> ConfigDir
    Config --> ConfigDir
    
    ConfigDir --> DetectStage
    BaseDir --> DetectStage
    Config --> DetectStage
    
    DetectStage --> FromStage
```

The `detect_start_stage` function implements the smart recovery logic by checking for existing checkpoint files and determining the earliest stage that needs execution:

**Logic Flow**:
1. Check if `checkpoint_plan.json` exists and is valid → start from `generate`
2. Check if `checkpoint_summary.json` exists and is valid → start from `plan`
3. Check if `checkpoint_rag.json` exists and is valid → start from `summary`
4. Otherwise → start from `rag`

**Sources**: [paper2slides/core/pipeline.py](), [api/server.py:388-404]()

## Stage Execution Flow

### Sequential Processing

Each stage follows a common execution pattern:

```mermaid
sequenceDiagram
    participant Pipeline as run_pipeline()
    participant State as state.json
    participant Stage as Stage Function
    participant Checkpoint as Checkpoint File
    
    Pipeline->>State: Load or create state
    Pipeline->>State: Mark stage as "running"
    Pipeline->>State: save_state()
    
    Pipeline->>Stage: Execute stage logic
    Stage->>Stage: Process data
    Stage->>Checkpoint: Save results
    
    Stage-->>Pipeline: Return success
    
    Pipeline->>State: Mark stage as "completed"
    Pipeline->>State: save_state()
    
    Pipeline->>Pipeline: Continue to next stage
```

**State Tracking**: The `state.json` file maintains the current execution state. Each stage updates this file at the start and end of its execution:

```json
{
  "session_id": "uuid-string",
  "config": { /* configuration parameters */ },
  "stages": {
    "rag": "completed",
    "summary": "completed",
    "plan": "running",
    "generate": "pending"
  },
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:35:00"
}
```

**Sources**: [paper2slides/core/state.py](), [api/server.py:392-404]()

### Stage Interdependencies

```mermaid
graph TB
    subgraph "Stage Dependencies"
        direction TB
        
        InputFiles["Input Files<br/>(PDF, MD, etc.)"]
        Config["Configuration<br/>{content_type, output_type,<br/>style, length/density}"]
        
        RAG["Stage 1: rag<br/>Uses: input_path, content_type, fast_mode"]
        RAGCP[("checkpoint_rag.json<br/>{parsed_content, file_paths}")]
        
        Summary["Stage 2: summary<br/>Uses: checkpoint_rag.json, content_type"]
        SumCP[("checkpoint_summary.json<br/>{structure, figures, tables}")]
        
        Plan["Stage 3: plan<br/>Uses: checkpoint_summary.json,<br/>output_type, style, length/density"]
        PlanCP[("checkpoint_plan.json<br/>{slides/poster layout}")]
        
        Generate["Stage 4: generate<br/>Uses: checkpoint_plan.json,<br/>style, output_type"]
        Output["Output Directory<br/>{timestamp}/slide_*.png, slides.pdf"]
        
        InputFiles --> RAG
        Config --> RAG
        RAG --> RAGCP
        RAGCP --> Summary
        Config --> Summary
        Summary --> SumCP
        SumCP --> Plan
        Config --> Plan
        Plan --> PlanCP
        PlanCP --> Generate
        Config --> Generate
        Generate --> Output
    end
```

**Key Observations**:
- Stage 1 and 2 depend on `input_path` and `content_type` but not on `style` or `length`/`density`
- Stage 3 is the first stage influenced by `output_type`, `style`, and size parameters
- Stage 4 only depends on the plan checkpoint and style configuration

This dependency structure enables efficient regeneration: changing style only requires re-running stages 3-4, while the RAG and analysis results can be reused.

**Sources**: [README.md:202-228](), [paper2slides/core/pipeline.py]()

## Directory Structure and Checkpoints

### Hierarchical Output Organization

The output directory structure encodes processing context to enable checkpoint reuse:

```
outputs/
└── <project_name>/              # From PDF filename or session_id
    └── <content_type>/          # "paper" or "general"
        └── <mode>/              # "fast" or "normal"
            ├── checkpoint_rag.json        # Stage 1 output
            ├── checkpoint_summary.json    # Stage 2 output
            ├── summary.md                 # Human-readable summary
            ├── rag_output/                # RAG index files
            └── <config_hash>/             # e.g., "slides_doraemon_medium"
                ├── state.json             # Pipeline state tracker
                ├── checkpoint_plan.json   # Stage 3 output
                └── <timestamp>/           # e.g., "20240115_103045"
                    ├── slide_01.png
                    ├── slide_02.png
                    └── slides.pdf
```

### Checkpoint Reusability

```mermaid
graph TB
    subgraph "Checkpoint Placement Strategy"
        direction TB
        
        Input["Same Input Files?"]
        Mode["Same Mode<br/>(fast/normal)?"]
        Config["Same Config<br/>(style, length/density)?"]
        
        CPRAG["checkpoint_rag.json<br/>@ mode level"]
        CPSum["checkpoint_summary.json<br/>@ mode level"]
        CPPlan["checkpoint_plan.json<br/>@ config level"]
        
        Stage1["Reuse Stage 1"]
        Stage2["Reuse Stage 2"]
        Stage3["Reuse Stage 3"]
        
        Input -->|Yes| Mode
        Input -->|No| RunRAG["Run from rag"]
        Mode -->|Yes| CPRAG
        Mode -->|No| RunRAG
        CPRAG --> Stage1
        
        Stage1 --> Config
        Config -->|Yes| CPSum
        Config -->|No| RunSummary["Run from summary"]
        CPSum --> Stage2
        
        Stage2 --> ConfigCheck["Same output config?"]
        ConfigCheck -->|Yes| CPPlan
        ConfigCheck -->|No| RunPlan["Run from plan"]
        CPPlan --> Stage3
    end
```

**Checkpoint Scope**:

| Checkpoint File | Location | Reusable When | Contains |
|-----------------|----------|---------------|----------|
| `checkpoint_rag.json` | `<mode>/` | Same input files + same mode | Parsed document content, file paths |
| `checkpoint_summary.json` | `<mode>/` | Same input files + same mode | Extracted figures, tables, structure |
| `checkpoint_plan.json` | `<config_hash>/` | Same config (style + length/density) | Content layout and slide/poster plan |
| `state.json` | `<config_hash>/` | Current generation | Stage statuses, timestamps |

**Sources**: [README.md:234-254](), [api/server.py:374-376]()

## Configuration Flow Through Pipeline

### Parameter Influence by Stage

Different configuration parameters affect different stages of the pipeline:

```mermaid
graph LR
    subgraph "Configuration Parameters"
        InputPath["input_path"]
        ContentType["content_type<br/>(paper/general)"]
        FastMode["fast_mode<br/>(true/false)"]
        OutputType["output_type<br/>(slides/poster)"]
        Style["style<br/>(academic/doraemon/custom)"]
        Length["length<br/>(short/medium/long)"]
        Density["density<br/>(sparse/medium/dense)"]
    end
    
    subgraph "Stage 1: rag"
        RAGStage["Document Parsing<br/>RAG Indexing"]
    end
    
    subgraph "Stage 2: summary"
        SumStage["Content Extraction<br/>Figure/Table Processing"]
    end
    
    subgraph "Stage 3: plan"
        PlanStage["Layout Planning<br/>Content Organization"]
    end
    
    subgraph "Stage 4: generate"
        GenStage["Image Generation<br/>PDF Creation"]
    end
    
    InputPath --> RAGStage
    ContentType --> RAGStage
    FastMode --> RAGStage
    
    ContentType --> SumStage
    
    OutputType --> PlanStage
    Style --> PlanStage
    Length --> PlanStage
    Density --> PlanStage
    
    Style --> GenStage
    OutputType --> GenStage
```

### Fast Mode vs Normal Mode

The `fast_mode` parameter creates a processing bifurcation at Stage 1:

```mermaid
graph TB
    Start["Pipeline Start"]
    CheckMode{"fast_mode<br/>enabled?"}
    
    subgraph "Normal Mode Path"
        FullRAG["Full RAG Indexing<br/>raganything.RAGAnything"]
        BuildIndex["Build vector index<br/>Chunk documents"]
        RAGOutput["checkpoint_rag.json<br/>with index references"]
    end
    
    subgraph "Fast Mode Path"
        SkipRAG["Skip RAG indexing<br/>Direct LLM query"]
        SimpleCP["checkpoint_rag.json<br/>with full text"]
    end
    
    Continue["Continue to summary stage"]
    
    Start --> CheckMode
    CheckMode -->|false| FullRAG
    CheckMode -->|true| SkipRAG
    
    FullRAG --> BuildIndex
    BuildIndex --> RAGOutput
    RAGOutput --> Continue
    
    SkipRAG --> SimpleCP
    SimpleCP --> Continue
```

**Use Cases**:
- **Normal Mode** (`fast_mode=false`): Default. Performs full RAG indexing. Suitable for long documents, multiple files, or when precise retrieval is needed.
- **Fast Mode** (`fast_mode=true`): Skips RAG indexing and uses direct LLM queries. Suitable for short documents that fit in context window, quick previews, or rapid iteration.

**Sources**: [README.md:212-228](), [api/server.py:236-237]()

## Pipeline Invocation Patterns

### CLI Invocation

The command-line interface directly calls the pipeline:

```mermaid
graph TB
    CLI["CLI Command<br/>python -m paper2slides"]
    
    Main["paper2slides.main.main()"]
    ArgParse["Parse CLI arguments<br/>--input, --output, --style, etc."]
    
    BuildConfig["Build config dict"]
    
    GetPaths["get_base_dir()<br/>get_config_dir()"]
    
    Detect["detect_start_stage()"]
    
    RunPipe["run_pipeline(base_dir, config_dir,<br/>config, from_stage)"]
    
    CLI --> Main
    Main --> ArgParse
    ArgParse --> BuildConfig
    BuildConfig --> GetPaths
    GetPaths --> Detect
    Detect --> RunPipe
```

**Sources**: [paper2slides/main.py](), [README.md:123-166]()

### Web API Invocation

The web interface adds asynchronous processing and session management:

```mermaid
graph TB
    Request["POST /api/chat"]
    
    SessionCheck["SessionManager.start_session()"]
    CheckLock{"Session<br/>available?"}
    
    SaveFiles["Save uploaded files<br/>to UPLOAD_DIR/session_id/"]
    
    CreateState["create_state()<br/>save_state()"]
    
    Background["background_tasks.add_task(<br/>run_pipeline_background)"]
    
    Response["Return 200 OK<br/>{session_id}"]
    
    AsyncRun["run_pipeline()<br/>in background"]
    
    EndSession["SessionManager.end_session()"]
    
    Request --> SessionCheck
    SessionCheck --> CheckLock
    CheckLock -->|Available| SaveFiles
    CheckLock -->|Locked| Return409["Return 409 Conflict"]
    
    SaveFiles --> CreateState
    CreateState --> Background
    Background --> Response
    
    Background -.async.-> AsyncRun
    AsyncRun -.when done.-> EndSession
```

**Concurrency Control**: The `SessionManager` class enforces single-threaded execution. Only one session can run at a time. Concurrent requests receive HTTP 409 status.

**Sources**: [api/server.py:45-86](), [api/server.py:145-292](), [api/server.py:489-548]()

## Error Handling and State Persistence

### Error Propagation

When a stage fails, the pipeline updates the state file and stops execution:

```mermaid
sequenceDiagram
    participant Pipeline as run_pipeline()
    participant Stage as Stage Function
    participant State as state.json
    participant Session as SessionManager
    
    Pipeline->>State: Mark stage as "running"
    Pipeline->>Stage: Execute stage
    
    alt Stage Success
        Stage-->>Pipeline: Return result
        Pipeline->>State: Mark stage as "completed"
        Pipeline->>Pipeline: Continue to next stage
    else Stage Failure
        Stage-->>Pipeline: Raise exception
        Pipeline->>State: Mark stage as "failed"
        Pipeline->>State: Store error message
        Pipeline->>Session: end_session()
        Pipeline-->>API: Propagate error
    end
```

**State File on Error**:
```json
{
  "stages": {
    "rag": "completed",
    "summary": "completed",
    "plan": "failed",
    "generate": "pending"
  },
  "error": "Error message from stage",
  "updated_at": "2024-01-15T10:40:00"
}
```

**Sources**: [api/server.py:433-487](), [api/server.py:532-543]()

### Cancellation Support

The web interface supports session cancellation through the `SessionManager`:

```mermaid
graph TB
    Running["Session Running"]
    
    Cancel["POST /api/cancel/session_id"]
    
    MarkCancel["SessionManager.cancel_session()<br/>Add to cancelled_sessions set"]
    
    StageCheck["Stage execution loop"]
    
    CheckFlag{"is_cancelled()?"}
    
    Abort["Abort execution<br/>Clean up resources"]
    
    Complete["Normal completion"]
    
    Running --> StageCheck
    
    Cancel --> MarkCancel
    MarkCancel -.sets flag.-> CheckFlag
    
    StageCheck --> CheckFlag
    CheckFlag -->|true| Abort
    CheckFlag -->|false| Complete
```

**Sources**: [api/server.py:68-79](), [api/server.py:131-143]()

## Summary

The Paper2Slides pipeline architecture provides:

1. **Linear 4-stage processing**: RAG → Analysis → Planning → Creation
2. **Checkpoint-based state**: Each stage saves recoverable checkpoints
3. **Smart resumption**: Auto-detection of completed stages enables selective regeneration
4. **Configuration-driven execution**: Parameters influence different stages appropriately
5. **Dual interfaces**: CLI for direct execution, Web API for asynchronous processing
6. **Session management**: Enforced single-threaded execution with cancellation support

The hierarchical directory structure and strategic checkpoint placement enable efficient regeneration when only style or output parameters change, while preserving computationally expensive RAG and analysis results.

**Sources**: [README.md:198-228](), [api/server.py:1-773](), [paper2slides/core/pipeline.py](), [paper2slides/core/state.py]()

---

