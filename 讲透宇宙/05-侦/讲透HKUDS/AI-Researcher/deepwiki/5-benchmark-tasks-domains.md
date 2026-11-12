<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/AI-Researcher · page 5 Benchmark Tasks & Domains · fetched 2026-11-09 -->

# Benchmark Tasks & Domains

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [benchmark/README.md](benchmark/README.md)

</details>



## Overview

The AI-Researcher benchmark system, Inno-Bench, provides systematic evaluation across 16+ research tasks organized into 5 distinct research domains. Each domain represents a different area of machine learning research and contains multiple benchmark instances with expert-written ground truth papers.

The benchmark system is configured through the `CATEGORY` parameter in [.env.template:37-46](), which determines which research domain to evaluate. This page documents the task organization, domain structure, and configuration mechanisms.

For detailed information about specific research domains, see: [Diffusion & Flow Matching](#5.1), [Graph Neural Networks](#5.2), [Reasoning](#5.3), [Recommendation Systems](#5.4), and [Vector Quantization](#5.5). For information about the evaluation framework, see page 3.3.

## Benchmark Configuration System

The benchmark system is configured through environment variables that specify the domain, task instance, and execution level. The primary configuration parameters are defined in [.env.template:36-52]().

**Category Configuration**

The `CATEGORY` environment variable determines which research domain to execute:
- `diffu_flow` - Diffusion and flow matching models (4 tasks)
- `gnn` - Graph neural networks (10 tasks)
- `reasoning` - Analogical reasoning tasks (1 task)
- `recommendation` - Recommendation systems (1 task)
- `vq` - Vector quantization methods (2+ tasks)

**Task Instance Selection Diagram**

```mermaid
graph TB
    ENV[".env.template"]
    
    subgraph "Configuration Parameters"
        CATEGORY["CATEGORY<br/>diffu_flow|gnn|reasoning|recommendation|vq"]
        INSTANCE["INSTANCE_ID<br/>specific task identifier"]
        LEVEL["TASK_LEVEL<br/>task1|task2"]
    end
    
    subgraph "Domain Categories"
        DF["diffu_flow<br/>./benchmark/final/diffu_flow/"]
        GNN["gnn<br/>./benchmark/final/gnn/"]
        REASON["reasoning<br/>./benchmark/final/reasoning/"]
        REC["recommendation<br/>./benchmark/final/recommendation/"]
        VQ["vq<br/>./benchmark/final/vq/"]
    end
    
    subgraph "Task Instances"
        DF_TASKS["con_flowmatching.json<br/>i_rect_flow.json<br/>immiscible_diffusion.json<br/>mmdit.json"]
        GNN_TASKS["allinone.json<br/>exphormer.json<br/>gnn_difformer.json<br/>gnn_fractional.json<br/>..."]
        REASON_TASKS["analog_reasoner.json"]
        REC_TASKS["categorical_rec.json"]
        VQ_TASKS["one_layer_vq.json<br/>rotation_vq.json"]
    end
    
    ENV --> CATEGORY
    ENV --> INSTANCE
    ENV --> LEVEL
    
    CATEGORY --> DF
    CATEGORY --> GNN
    CATEGORY --> REASON
    CATEGORY --> REC
    CATEGORY --> VQ
    
    DF --> DF_TASKS
    GNN --> GNN_TASKS
    REASON --> REASON_TASKS
    REC --> REC_TASKS
    VQ --> VQ_TASKS
```

Sources: [.env.template:36-52](), [README.md:190-207]()

## Domain Distribution and Task Counts

The benchmark contains 16+ tasks distributed across 5 research domains. Each domain tests different aspects of autonomous research capabilities.

| Domain | Task Count | Directory Path | Example Instance IDs |
|--------|-----------|----------------|---------------------|
| **Diffusion & Flow** | 4 | `./benchmark/final/diffu_flow/` | `con_flowmatching`, `i_rect_flow`, `immiscible_diffusion`, `mmdit` |
| **Graph Neural Networks** | 10 | `./benchmark/final/gnn/` | `allinone`, `exphormer`, `gnn_difformer`, `gnn_fractional`, `gnn_generalization`, `gnn_nodeformer`, `gnn_poly_gcl`, `gnn_universal`, `graphgpt` |
| **Reasoning** | 1 | `./benchmark/final/reasoning/` | `analog_reasoner` |
| **Recommendation** | 1 | `./benchmark/final/recommendation/` | `categorical_rec` |
| **Vector Quantization** | 2+ | `./benchmark/final/vq/` | `one_layer_vq`, `rotation_vq` |

**Benchmark Task Distribution Diagram**

```mermaid
graph TB
    subgraph "benchmark/final/"
        subgraph "diffu_flow/ [4 tasks]"
            DF1["con_flowmatching.json"]
            DF2["i_rect_flow.json"]
            DF3["immiscible_diffusion.json"]
            DF4["mmdit.json"]
        end
        
        subgraph "gnn/ [10 tasks]"
            G1["allinone.json"]
            G2["exphormer.json"]
            G3["gnn_difformer.json"]
            G4["gnn_fractional.json"]
            G5["gnn_generalization.json"]
            G6["gnn_nodeformer.json"]
            G7["gnn_poly_gcl.json"]
            G8["gnn_universal.json"]
            G9["graphgpt.json"]
            G10["[additional tasks]"]
        end
        
        subgraph "reasoning/ [1 task]"
            R1["analog_reasoner.json"]
        end
        
        subgraph "recommendation/ [1 task]"
            REC1["categorical_rec.json"]
        end
        
        subgraph "vq/ [2+ tasks]"
            VQ1["one_layer_vq.json"]
            VQ2["rotation_vq.json"]
        end
    end
    
    ENV_CATEGORY["CATEGORY env variable"]
    ENV_INSTANCE["INSTANCE_ID env variable"]
    
    ENV_CATEGORY -.selects domain.-> diffu_flow
    ENV_INSTANCE -.selects task file.-> DF1
```

Sources: [.env.template:37-46](), [README.md:1000-1024]()

## Task Execution Levels

Each benchmark task supports two execution levels configured via the `TASK_LEVEL` environment variable in [.env.template:47-50]():

**Level 1 (task1): Direct Implementation**
- User provides detailed research idea and implementation specifications
- System bypasses literature review and idea generation phases
- Executes design, implementation, validation, and refinement phases
- Entry point: `research_agent/run_infer_level_1.sh` or `research_agent/run_infer_plan.py`

**Level 2 (task2): Full Autonomous Pipeline**
- User provides only reference papers without specific ideas
- System performs complete research cycle: literature review → idea generation → implementation → validation
- Tests full autonomous research capabilities
- Entry point: `research_agent/run_infer_level_2.sh` or `research_agent/run_infer_idea.py`

**Task Level Execution Flow**

```mermaid
graph TB
    CONFIG[".env: TASK_LEVEL"]
    
    subgraph "task1 Pipeline"
        T1_INPUT["User Idea + References"]
        T1_DESIGN["Design Phase"]
        T1_IMPL["Implementation Phase"]
        T1_VAL["Validation Phase"]
        T1_OUTPUT["Research Output"]
        
        T1_INPUT --> T1_DESIGN
        T1_DESIGN --> T1_IMPL
        T1_IMPL --> T1_VAL
        T1_VAL --> T1_OUTPUT
    end
    
    subgraph "task2 Pipeline"
        T2_INPUT["Reference Papers Only"]
        T2_LIT["Literature Review"]
        T2_IDEA["Idea Generation"]
        T2_DESIGN["Design Phase"]
        T2_IMPL["Implementation Phase"]
        T2_VAL["Validation Phase"]
        T2_OUTPUT["Research Output"]
        
        T2_INPUT --> T2_LIT
        T2_LIT --> T2_IDEA
        T2_IDEA --> T2_DESIGN
        T2_DESIGN --> T2_IMPL
        T2_IMPL --> T2_VAL
        T2_VAL --> T2_OUTPUT
    end
    
    CONFIG -.task1.-> T1_INPUT
    CONFIG -.task2.-> T2_INPUT
```

Sources: [.env.template:47-50](), [README.md:988-1024]()

## Benchmark Task Execution Workflow

The benchmark system integrates with the AI-Researcher's core components to provide systematic evaluation of research outputs across all supported domains.

```mermaid
sequenceDiagram
    participant RA as "ResearchAgent"
    participant BC as "BenchmarkController"
    participant EA as "EvaluatorAgent"
    participant GT as "GroundTruthDB"
    participant RS as "ResultsSystem"
    
    RA->>BC: "Submit research output for evaluation"
    BC->>BC: "Identify domain and task category"
    BC->>EA: "Initialize domain-specific evaluators"
    
    loop "Multi-Dimensional Assessment"
        EA->>GT: "Retrieve expert ground truth"
        GT->>EA: "Domain-specific reference standards"
        EA->>EA: "Perform comparative analysis"
    end
    
    EA->>BC: "Return evaluation scores"
    BC->>RS: "Aggregate and weight scores"
    RS->>RA: "Comprehensive evaluation report"
```

**Benchmark Execution Sequence**

Sources: [benchmark/README.md:1]()

The benchmark tasks serve as the foundation for validating AI-Researcher's autonomous research capabilities, ensuring that generated research meets rigorous academic standards across diverse scientific domains. Each domain contains carefully curated tasks that represent current research frontiers and methodological challenges in their respective fields.

---

