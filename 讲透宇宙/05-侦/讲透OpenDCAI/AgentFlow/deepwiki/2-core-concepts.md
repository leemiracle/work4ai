<!-- source: DeepWiki mcp.deepwiki.com · repo OpenDCAI/AgentFlow · page 2 Core Concepts · fetched 2026-11-02 -->

# Core Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README_zh.md](README_zh.md)
- [assets/intro.png](assets/intro.png)
- [assets/method.png](assets/method.png)
- [assets/wechat.jpg](assets/wechat.jpg)
- [assets/wechatshow.png](assets/wechatshow.png)

</details>



This page introduces the fundamental architectural concepts and design patterns that underpin AgentFlow's unified agent data synthesis framework. It provides an overview of the core components, their interactions, and the key abstractions that enable cross-domain agent development.

For detailed information about specific topics:
- The three-stage data generation methodology: see [Three-Stage Data Synthesis Pipeline](#2.1)
- Specific agent implementations and use cases: see [Agent Types and Modalities](#2.2)
- Tool system internals: see [Tool Schemas and Abstraction Layer](#2.3)
- Model training strategies: see [Agentic Model Consolidation](#2.4)

## System Architecture Overview

AgentFlow is built on a modular architecture that separates infrastructure concerns (tool execution environment) from data generation logic (synthesis and rollout pipelines) and model development (training and evaluation).

```mermaid
graph TB
    subgraph "Infrastructure Layer"
        SandboxServer["Sandbox Server<br/>sandbox-server.sh<br/>FastAPI on :18890"]
        Backends["Backend Resources<br/>VMBackend, WebBackend<br/>SQLBackend, RAGBackend<br/>DocBackend, DSBackend"]
        ToolRegistry["Tool Registry<br/>sandbox/tool_schemas/__init__.py<br/>get_tool_schemas()"]
    end
    
    subgraph "Data Generation Layer"
        SynthPipeline["Synthesis Pipeline<br/>synthesis.synthesize()<br/>synthesis/core/"]
        RolloutPipeline["Rollout Pipeline<br/>rollout.pipeline()<br/>rollout/core/"]
        
        Sampler["TrajectorySampler<br/>synthesis/core/sampler.py"]
        Selector["TrajectorySelector<br/>synthesis/core/selector.py"]
        Synthesizer["QASynthesizer<br/>synthesis/core/synthesizer.py"]
        Runner["AgentRunner<br/>rollout/core/runner.py"]
    end
    
    subgraph "Configuration System"
        SandboxConfigs["configs/sandbox-server/<br/>*_config.json"]
        SynthConfigs["configs/synthesis/<br/>*_config.json"]
        TrajConfigs["configs/trajectory/<br/>*_trajectory.json"]
        InferConfigs["configs/infer/<br/>*_infer.json"]
    end
    
    subgraph "Data Artifacts"
        Seeds["seeds/*/<br/>seeds.jsonl"]
        SynthData["Synthesized Data<br/>synthesized_qa.jsonl<br/>trajectories.jsonl"]
        Benchmarks["Benchmark Data<br/>*.jsonl"]
    end
    
    SandboxConfigs --> SandboxServer
    SandboxServer --> Backends
    Backends --> ToolRegistry
    
    SynthConfigs --> SynthPipeline
    TrajConfigs --> RolloutPipeline
    InferConfigs --> RolloutPipeline
    
    SynthPipeline --> Sampler
    Sampler --> Selector
    Selector --> Synthesizer
    
    RolloutPipeline --> Runner
    
    Seeds --> Sampler
    Benchmarks --> Runner
    
    Sampler -.HTTP.-> SandboxServer
    Runner -.HTTP.-> SandboxServer
    
    Synthesizer --> SynthData
    Runner --> SynthData
```

**Sources:** [README.md:44-103](), [configs/](https://github.com/OpenDCAI/AgentFlow/tree/main/configs)

## Core Component Interactions

The following diagram shows how the key classes and modules interact during data generation:

```mermaid
graph LR
    subgraph "Client Side"
        synthesize["synthesis.synthesize()"]
        pipeline["rollout.pipeline()"]
        
        SandboxWorker["SandboxWorker<br/>synthesis/core/worker.py<br/>_execute_tool()"]
        SandboxClient["Sandbox Client<br/>rollout/core/runner.py<br/>execute_tool()"]
    end
    
    subgraph "Sandbox Server"
        FastAPI["FastAPI Server<br/>sandbox/server.py<br/>localhost:18890"]
        ToolExec["Tool Execution<br/>/execute_tool endpoint"]
        SessionMgmt["Session Management<br/>/create_session<br/>/reinitialize_session"]
    end
    
    subgraph "Backend Layer"
        VMBackend["VMBackend<br/>vm_tools.py schemas"]
        WebBackend["WebBackend<br/>web_tools.py schemas"]
        SQLBackend["DatabaseBackend<br/>sql_tools.py schemas"]
        RAGBackend["RAGBackend<br/>rag_tools.py schemas"]
        DocBackend["DocumentBackend<br/>doc_tools.py schemas"]
        DSBackend["DSBackend<br/>ds_tools.py schemas"]
    end
    
    synthesize --> SandboxWorker
    pipeline --> SandboxClient
    
    SandboxWorker -->|"HTTP POST"| FastAPI
    SandboxClient -->|"HTTP POST"| FastAPI
    
    FastAPI --> ToolExec
    FastAPI --> SessionMgmt
    
    ToolExec --> VMBackend
    ToolExec --> WebBackend
    ToolExec --> SQLBackend
    ToolExec --> RAGBackend
    ToolExec --> DocBackend
    ToolExec --> DSBackend
```

**Sources:** [synthesis/core/sampler.py](), [rollout/core/runner.py](), [sandbox/tool_schemas/]()

## The Three-Stage Pipeline

AgentFlow generates high-quality agent training data through a three-stage process:

```mermaid
graph TB
    subgraph "Stage 1: Trajectory Sampling"
        Input1["Seed Data<br/>seeds.jsonl"]
        Config1["Synthesis Config<br/>max_depth<br/>branching_factor<br/>sampling_tips"]
        
        Sampler1["TrajectorySampler<br/>_sample_trajectory_tree()"]
        LLM1["LLM API<br/>OpenRouter/OpenAI"]
        Tools1["Sandbox Tools<br/>rag-search, web-search<br/>doc-read, sql:execute, etc"]
        
        Output1["Trajectory Tree<br/>branching paths<br/>tool calls + observations"]
    end
    
    subgraph "Stage 2: Trajectory Selection"
        Scorer["Trajectory Scoring<br/>_score_trajectory()<br/>depth, richness, diversity"]
        Selector1["TrajectorySelector<br/>_select_trajectories()"]
        Dedup["Deduplication<br/>_deduplicate_trajectories()"]
        
        Output2["Selected Paths<br/>high-quality trajectories"]
    end
    
    subgraph "Stage 3: QA Synthesis"
        Synthesizer1["QASynthesizer<br/>_generate_qa_pair()"]
        LLM2["LLM API<br/>synthesis_tips<br/>quality checks"]
        
        Output3["QA Pairs<br/>question + answer<br/>+ trajectory"]
    end
    
    Input1 --> Sampler1
    Config1 --> Sampler1
    Sampler1 --> LLM1
    Sampler1 --> Tools1
    Sampler1 --> Output1
    
    Output1 --> Scorer
    Scorer --> Selector1
    Selector1 --> Dedup
    Dedup --> Output2
    
    Output2 --> Synthesizer1
    Synthesizer1 --> LLM2
    Synthesizer1 --> Output3
```

**Sources:** [README.md:77-84](), [synthesis/core/sampler.py](), [synthesis/core/selector.py](), [synthesis/core/synthesizer.py]()

The pipeline is modality-agnostic and operates consistently across all agent types. Stage 1 builds a branching trajectory tree through LLM-driven exploration with concurrent expansion and action deduplication. Stage 2 filters trajectories based on scoring criteria. Stage 3 generates multi-hop QA pairs grounded in the collected observations.

For implementation details, see [Three-Stage Data Synthesis Pipeline](#2.1).

## Agent Types and Tool Ecosystems

AgentFlow supports seven distinct agent modalities, each defined by its available tool set:

| Agent Type | Tools | Backend Implementation | Configuration |
|------------|-------|------------------------|---------------|
| RAG | `rag-search` | `RAGBackend` (E5 + Faiss) | `configs/sandbox-server/rag_config.json` |
| MM-Doc | `doc-search`, `doc-read` | `DocumentBackend` (VLM + PDF) | `configs/sandbox-server/doc_config.json` |
| Web Research | `web-search`, `web-visit` | `WebBackend` (Serper + Jina APIs) | `configs/sandbox-server/web_config.json` |
| GUI | `vm-screenshot`, `vm-click`, `vm-type`, etc (15 tools) | `VMBackend` (Docker VM) | `configs/sandbox-server/vm_config.json` |
| Text2SQL | `sql:list_databases`, `sql:get_schema`, `sql:execute` | `DatabaseBackend` (SQLite) | `configs/sandbox-server/text2sql_config.json` |
| Data Science | `ds_inspect_data`, `ds_read_csv`, `ds_run_python` | `DSBackend` (Python sandbox) | `configs/sandbox-server/ds_config.json` |
| Embodied | Custom robotic control tools | Custom backend | Custom configuration |

```mermaid
graph TB
    subgraph "Unified Abstraction"
        CorePipeline["Core Pipeline<br/>Sampling → Selection → Synthesis"]
        ToolSchemas["Tool Schema System<br/>sandbox/tool_schemas/"]
    end
    
    subgraph "RAG Agent"
        RAGTools["rag_tools.py<br/>rag-search"]
        RAGE5["E5 Embeddings<br/>RAG_EMBEDDING_MODEL_PATH"]
        RAGFaiss["Faiss Index<br/>RAG_INDEX_PATH"]
    end
    
    subgraph "Document Agent"
        DocTools["doc_tools.py<br/>doc-search<br/>doc-read"]
        DocVLM["VLM API<br/>gpt-4o-mini<br/>VLM_API_KEY"]
    end
    
    subgraph "Web Agent"
        WebTools["web_tools.py<br/>web-search<br/>web-visit"]
        Serper["Serper API<br/>SERPER_API_KEY"]
        Jina["Jina API<br/>JINA_API_KEY"]
    end
    
    subgraph "SQL Agent"
        SQLTools["sql_tools.py<br/>sql:list_databases<br/>sql:get_schema<br/>sql:execute"]
        SQLite["SQLite DBs<br/>TEXT2SQL_*_DB_PATH<br/>7 domains"]
    end
    
    CorePipeline --> ToolSchemas
    ToolSchemas --> RAGTools
    ToolSchemas --> DocTools
    ToolSchemas --> WebTools
    ToolSchemas --> SQLTools
    
    RAGTools --> RAGE5
    RAGTools --> RAGFaiss
    DocTools --> DocVLM
    WebTools --> Serper
    WebTools --> Jina
    SQLTools --> SQLite
```

**Sources:** [README.md:15-38](), [sandbox/tool_schemas/](), [configs/sandbox-server/]()

Each agent type uses the same core pipeline but with different `available_tools` and `resource_types` configurations. For detailed descriptions of each agent type and their use cases, see [Agent Types and Modalities](#2.2).

## Tool Schema System

The tool schema system provides a unified abstraction for defining and executing tools across heterogeneous environments:

```mermaid
graph TB
    subgraph "Schema Definition"
        VMSchema["vm_tools.py<br/>15 tool schemas"]
        WebSchema["web_tools.py<br/>2 tool schemas"]
        SQLSchema["sql_tools.py<br/>3 tool schemas"]
        DocSchema["doc_tools.py<br/>2 tool schemas"]
        RAGSchema["rag_tools.py<br/>1 tool schema"]
        DSSchema["ds_tools.py<br/>3 tool schemas"]
    end
    
    subgraph "Registry"
        GetSchemas["get_tool_schemas()<br/>filter by name pattern"]
        GetByResource["get_tools_by_resource()<br/>filter by resource type"]
    end
    
    subgraph "Server Integration"
        LoadTools["load_tools_from_config()<br/>available_tools list"]
        RegisterBackend["register backend handler<br/>for each resource type"]
    end
    
    VMSchema --> GetSchemas
    WebSchema --> GetSchemas
    SQLSchema --> GetSchemas
    DocSchema --> GetSchemas
    RAGSchema --> GetSchemas
    DSSchema --> GetSchemas
    
    GetSchemas --> GetByResource
    GetByResource --> LoadTools
    LoadTools --> RegisterBackend
```

**Sources:** [sandbox/tool_schemas/__init__.py](), [sandbox/tool_schemas/*.py]()

Tool schemas are defined as JSON dictionaries with `name`, `description`, and `parameters` fields. The registry supports filtering by name patterns (e.g., `"vm-*"`) and resource types (e.g., `"vm"`, `"web"`, `"sql"`). This enables the same pipeline to work across all agent types by simply changing configuration.

For complete tool schema reference, see [Tool Schemas Reference](#3.3).

## Configuration Hierarchy

AgentFlow uses a hierarchical configuration system organized by operational stage:

```mermaid
graph TB
    subgraph "Sandbox Server Configs"
        SSBase["configs/sandbox-server/<br/>*_config.json"]
        SSShared["Common Parameters:<br/>server.url<br/>server.port<br/>session_ttl"]
        SSModality["Modality-Specific:<br/>resource_types<br/>available_tools<br/>backend settings"]
    end
    
    subgraph "Synthesis Configs"
        SynthBase["configs/synthesis/<br/>*_config.json"]
        SynthShared["Common Parameters:<br/>max_depth<br/>branching_factor<br/>min_depth<br/>sampling_tips<br/>synthesis_tips"]
        SynthModality["Modality-Specific:<br/>available_tools<br/>resource_types<br/>seed_file"]
    end
    
    subgraph "Trajectory Configs"
        TrajBase["configs/trajectory/<br/>*_trajectory.json"]
        TrajShared["Common Parameters:<br/>trajectory_only: true<br/>evaluate_results: false"]
        TrajModality["Modality-Specific:<br/>available_tools<br/>benchmark_file"]
    end
    
    subgraph "Inference Configs"
        InferBase["configs/infer/<br/>*_infer.json"]
        InferShared["Common Parameters:<br/>evaluate_results: true<br/>evaluation_metric<br/>evaluator_model"]
        InferModality["Modality-Specific:<br/>available_tools<br/>benchmark_file"]
    end
    
    SSBase --> SSShared
    SSBase --> SSModality
    SynthBase --> SynthShared
    SynthBase --> SynthModality
    TrajBase --> TrajShared
    TrajBase --> TrajModality
    InferBase --> InferShared
    InferBase --> InferModality
```

**Sources:** [README.md:107-112](), [configs/sandbox-server/](), [configs/synthesis/](), [configs/trajectory/](), [configs/infer/]()

Configuration files use environment variable substitution with `${VAR_NAME}` syntax to centralize credentials and machine-specific paths. Within each category, configurations share common parameters while allowing modality-specific customization.

For complete configuration reference, see [Configuration Reference](#8).

## Agentic Model Consolidation

AgentFlow explores two strategies for training unified multi-domain models:

```mermaid
graph TB
    subgraph "Generated Data"
        RAGQA["RAG Data<br/>QA + trajectories"]
        DocQA["Doc Data<br/>QA + trajectories"]
        WebQA["Web Data<br/>QA + trajectories"]
        SQLQA["SQL Data<br/>QA + trajectories"]
    end
    
    subgraph "Data-Level Consolidation"
        DataMix["Agent-datamix<br/>Mix all trajectories<br/>Joint training"]
        UnifiedModel1["Unified Model<br/>64.08% GAIA accuracy"]
    end
    
    subgraph "Parameter-Level Consolidation"
        Specialist1["RAGShaper<br/>specialist model"]
        Specialist2["DocDancer<br/>specialist model"]
        Specialist3["WebAgent<br/>specialist model"]
        
        RegMean["Agent-RegMeanpp<br/>Parameter merging<br/>Regularized averaging"]
        UnifiedModel2["Unified Model<br/>60.19% GAIA accuracy"]
    end
    
    RAGQA --> DataMix
    DocQA --> DataMix
    WebQA --> DataMix
    SQLQA --> DataMix
    DataMix --> UnifiedModel1
    
    RAGQA --> Specialist1
    DocQA --> Specialist2
    WebQA --> Specialist3
    
    Specialist1 --> RegMean
    Specialist2 --> RegMean
    Specialist3 --> RegMean
    RegMean --> UnifiedModel2
```

**Sources:** [README.md:32-35](), [README.md:202-206]()

**Data-level consolidation** (Agent-datamix) mixes trajectories from all domains during training, forcing a single model to learn diverse behaviors. **Parameter-level consolidation** (Agent-RegMeanpp) first trains specialist models on individual domains, then merges their parameters using regularized averaging.

Benchmark results show data-level mixing outperforms parameter-level merging (64.08% vs 60.19% on GAIA), indicating joint training on mixed trajectories is more effective for multi-domain capability.

For training strategies and deployment, see [Agentic Model Consolidation](#2.4) and [Model Training and Deployment](#10).

## Data Flow Through the System

The complete end-to-end data flow:

```mermaid
graph LR
    subgraph "Input"
        Seeds["seeds.jsonl"]
        Benchmarks["benchmark.jsonl"]
    end
    
    subgraph "Synthesis Mode"
        SynthConfig["synthesis/*_config.json"]
        SynthFunc["synthesis.synthesize()"]
        SynthOutput["synthesized_qa.jsonl<br/>trajectories.jsonl"]
    end
    
    subgraph "Rollout Mode"
        TrajConfig["trajectory/*_trajectory.json"]
        RolloutFunc["rollout.pipeline()<br/>trajectory_only=true"]
        TrajOutput["trajectory results<br/>trajectories.jsonl"]
    end
    
    subgraph "Training"
        CombineData["Combine datasets"]
        Training["Model Training"]
        Model["Trained Model"]
    end
    
    subgraph "Inference Mode"
        InferConfig["infer/*_infer.json"]
        InferFunc["rollout.pipeline()<br/>evaluate_results=true"]
        vLLM["vLLM Server :8222<br/>--enable-auto-tool-choice"]
        Results["Evaluation Results<br/>Metrics"]
    end
    
    Seeds --> SynthConfig
    SynthConfig --> SynthFunc
    SynthFunc --> SynthOutput
    
    Benchmarks --> TrajConfig
    TrajConfig --> RolloutFunc
    RolloutFunc --> TrajOutput
    
    SynthOutput --> CombineData
    TrajOutput --> CombineData
    CombineData --> Training
    Training --> Model
    
    Model --> vLLM
    Benchmarks --> InferConfig
    InferConfig --> InferFunc
    vLLM --> InferFunc
    InferFunc --> Results
```

**Sources:** [README.md:69-103](), [synthesis/](), [rollout/]()

The same `rollout.pipeline()` function operates in two modes: trajectory generation (step 3, `trajectory_only=true`) and inference (step 6, `evaluate_results=true`), distinguished only by configuration. The sandbox server acts as a persistent service supporting all data generation and inference stages.

---

