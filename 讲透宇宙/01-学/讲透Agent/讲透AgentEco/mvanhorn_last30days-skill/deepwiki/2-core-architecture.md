<!-- source: DeepWiki mcp.deepwiki.com · repo mvanhorn/last30days-skill · page 2 Core Architecture · fetched 2026-10-27 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/last30days/scripts/last30days.py](skills/last30days/scripts/last30days.py)
- [skills/last30days/scripts/lib/pipeline.py](skills/last30days/scripts/lib/pipeline.py)
- [skills/last30days/scripts/lib/planner.py](skills/last30days/scripts/lib/planner.py)
- [tests/test_cli_v3.py](tests/test_cli_v3.py)
- [tests/test_external_plan_source_contract.py](tests/test_external_plan_source_contract.py)
- [tests/test_internals_v3.py](tests/test_internals_v3.py)
- [tests/test_pipeline_v3.py](tests/test_pipeline_v3.py)
- [tests/test_planner_v3.py](tests/test_planner_v3.py)

</details>



This page provides a high-level overview of the engine architecture for the `last30days` skill, covering planning, parallel retrieval, fusion, ranking, and rendering. The codebase is organized into modular components under `skills/last30days/scripts/lib` [skills/last30days/scripts/last30days.py:51-55]().

For detailed mechanics on each subsystem, refer to the child pages:
- [Two-Phase Search Strategy](#2.1) — Intent classification, query expansion, source priority tables, and auto-resolve pre-research.
- [Orchestration Pipeline](#2.2) — CLI integration, thread pool fan-out, fetch caps, rate-limit tracking, and Report assembly.
- [Configuration and Authentication](#2.3) — Configuration priority resolution, provider descriptors, chain failover, and cookie/credential extraction.
- [Discovery Protocol](#2.4) — Host-judged discovery workflow, river listing sweeps, and confidence floor gating.

---

## System Overview and Module Layout

The engine operates as a parallel multi-source research pipeline supporting over 20 source adapters (Reddit, X, YouTube, TikTok, Hacker News, Polymarket, GitHub, web search, etc.) [skills/last30days/scripts/lib/pipeline.py:199-225](). The implementation is partitioned into dedicated functional libraries under `skills/last30days/scripts/lib/` [skills/last30days/scripts/last30days.py:51-55]():

- **Orchestration & Control**: `pipeline.py`, `planner.py`, `query.py`, `resolve.py`, `fanout.py`
- **Data Acquisition & Sources**: `reddit.py`, `bird_x.py`, `youtube_yt.py`, `grounding.py`, `polymarket.py`, etc.
- **Processing & Fusion**: `normalize.py`, `signals.py`, `fusion.py`, `rerank.py`, `cluster.py`, `dedupe.py`
- **Output & Presentation**: `render.py`, `ui.py`, `html_render.py`
- **Persistence & Management**: `store.py`, `watchlist.py`, `briefing.py`, `health.py`, `doctor.py`

Title: Component Architecture Diagram
```mermaid
graph TB
    subgraph "CLI Entry"
        main["skills/last30days/scripts/last30days.py"]
    end
    
    subgraph "Orchestration Layer"
        pipeline["skills/last30days/scripts/lib/pipeline.py"]
        planner["skills/last30days/scripts/lib/planner.py"]
    end
    
    subgraph "Retrieval Layer"
        reddit["skills/last30days/scripts/lib/reddit.py"]
        x["skills/last30days/scripts/lib/bird_x.py"]
        web["skills/last30days/scripts/lib/grounding.py"]
    end
    
    subgraph "Processing Pipeline"
        normalize["skills/last30days/scripts/lib/normalize.py"]
        fusion["skills/last30days/scripts/lib/fusion.py"]
        cluster["skills/last30days/scripts/lib/cluster.py"]
    end
    
    subgraph "Output Layer"
        render["skills/last30days/scripts/lib/render.py"]
    end
    
    main --> pipeline
    pipeline --> planner
    pipeline --> reddit
    pipeline --> x
    pipeline --> web
    
    reddit --> normalize
    x --> normalize
    web --> normalize
    
    normalize --> fusion
    fusion --> cluster
    cluster --> render
```
Sources: [skills/last30days/scripts/last30days.py:51-55](), [skills/last30days/scripts/lib/pipeline.py:1-85]()

---

## Execution Flow

The engine executes research across four distinct phases: intent planning and query expansion, parallel retrieval via thread pools, multi-signal fusion and ranking, and final report rendering [skills/last30days/scripts/last30days.py:114-175](), [skills/last30days/scripts/lib/pipeline.py:1-102]().

Title: Engine Execution Flow
```mermaid
sequenceDiagram
    participant CLI as last30days.py
    participant Pipe as pipeline.py
    participant Plan as planner.py
    participant Pool as ThreadPoolExecutor
    participant Proc as Processing Pipeline
    
    CLI->>Pipe: run(topic, sources)
    Pipe->>Plan: plan_query(topic)
    Plan-->>Pipe: QueryPlan
    
    loop Parallel Retrieval
        Pipe->>Pool: submit(_retrieve_stream)
        Pool-->>Pipe: Raw Items
    end
    
    Pipe->>Proc: normalize -> signals -> fusion -> rerank -> cluster
    Proc-->>Pipe: Ranked Candidates & Clusters
    Pipe-->>CLI: Report Object
```
Sources: [skills/last30days/scripts/last30days.py:114-175](), [skills/last30days/scripts/lib/pipeline.py:1-102]()

---

## Summary of Subsystems and Child Pages

- **Two-Phase Search Strategy**: Details intent classification, query expansion, source priority tables, and auto-resolve pre-research. For details, see [Two-Phase Search Strategy](#2.1).
- **Orchestration Pipeline**: Covers `last30days.py` CLI integration, `pipeline.py` execution (`ThreadPoolExecutor` fan-out, fetch caps, rate-limit tracking, thin-source retries, and Report assembly). For details, see [Orchestration Pipeline](#2.2).
- **Configuration and Authentication**: Documents configuration resolution, provider/backend descriptors, chain failover, cookie extraction, and credential stores. For details, see [Configuration and Authentication](#2.3).
- **Discovery Protocol**: Details the host-judged discovery workflow, river listing sweeps, clustering, and confidence floor gating. For details, see [Discovery Protocol](#2.4).

Sources: [skills/last30days/scripts/last30days.py:1-115](), [skills/last30days/scripts/lib/pipeline.py:1-102](), [skills/last30days/scripts/lib/planner.py:19-90]()

---

