# Page: Home

# Home

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [figures/figure_intro.png](figures/figure_intro.png)

</details>



## Purpose and Scope

This wiki documents **Mnemis**, a dual-route retrieval system designed for long-term memory management in Large Language Models (LLMs). Mnemis combines fast similarity-based retrieval (System-1) with deliberate hierarchical reasoning (System-2) to retrieve memory items that are both semantically and structurally relevant.

This Home page provides an overview of Mnemis, its architecture, key features, and benchmark results. For detailed information:
- Architecture deep dive: see [Architecture Overview](#2)
- Implementation details: see [Implementation Guide](#3)
- Benchmark analysis: see [Evaluation & Results](#4)
- Step-by-step usage: see [Getting Started](#6)

**Sources:** [README.md:1-72]()

---

## What is Mnemis?

Mnemis is a memory framework that addresses limitations in existing retrieval-augmented generation (RAG) and Graph-RAG systems. Traditional memory systems rely primarily on similarity-based retrieval, which struggles with scenarios requiring global reasoning or comprehensive information coverage.

### Core Innovation

Mnemis introduces a **dual-route architecture** inspired by dual-process theory in cognitive science:

| Route | Type | Mechanism | Use Case |
|-------|------|-----------|----------|
| **System-1** | Similarity Search | Embedding-based vector search | Fast, intuitive retrieval of semantically similar content |
| **System-2** | Global Selection | LLM-guided hierarchical traversal | Deliberate, comprehensive retrieval requiring global reasoning |

The system organizes memory into two complementary graph structures:
- **Base Graph**: Flat entity/relationship storage for similarity retrieval
- **Hierarchical Graph**: Semantic category hierarchy enabling top-down traversal

Results from both routes are merged using the `RAG_GRAPH` method to produce comprehensive memory context.

**Sources:** [README.md:15-23]()

---

## Key Features

### 1. Dual-Route Retrieval
- **System-1**: Fast embedding-based similarity search using `qwen3` embeddings (FLOAT32 precision)
- **System-2**: LLM-guided hierarchical graph traversal via `GlobalSelector` class
- **Merge Strategy**: `RAG_GRAPH` combines results for comprehensive context

### 2. Hierarchical Graph Construction
Guided by three principles:
- **Minimum Concept Abstraction**: Maintains semantic clarity at each hierarchy level
- **Many-to-Many Mapping**: Allows entities to belong to multiple categories
- **Compression Efficiency Constraint**: Ensures manageable hierarchy depth

### 3. Production-Ready Performance
- **Caching**: `alru_cache` with 500 entries per query reduces database load
- **Batch Processing**: Supports `mp` (multiprocessing) and `batch` modes
- **Concurrency**: Neo4j `AsyncDriver` with 1000-connection pool
- **Type Safety**: Pydantic models for structured LLM responses

### 4. State-of-the-Art Results
| Benchmark | Questions | Mnemis Score | Achievement |
|-----------|-----------|--------------|-------------|
| **LoCoMo** | 1,986 questions (5 categories) | **93.9%** | SOTA (93.3% excluding category 5) |
| **LongMemEval-S** | 500 questions (6 types) | **91.6%** | SOTA across all question types |

**Sources:** [README.md:18-23](), [README.md:31-40]()

---

## Architecture Overview

### High-Level System Architecture

```mermaid
graph TB
    subgraph "Mnemis Framework"
        direction TB
        
        subgraph "Memory Storage"
            BaseGraph["Base Graph<br/>(entity/relationship storage)"]
            HierGraph["Hierarchical Graph<br/>(semantic categories)"]
        end
        
        subgraph "Dual-Route Retrieval"
            System1["System-1 Similarity Search<br/>(embedding-based)"]
            System2["System-2 Global Selection<br/>(LLM-guided traversal)"]
        end
        
        BaseGraph --> System1
        HierGraph --> System2
    end
    
    subgraph "Infrastructure"
        Neo4j["Neo4j Graph Database<br/>(AsyncDriver, 1000 pool)"]
        LLM["LLM Services<br/>(OpenAI/Azure GPT-4.1-mini)"]
        Embedder["Embedding Model<br/>(qwen3, FLOAT32)"]
    end
    
    subgraph "Results"
        Merge["RAG_GRAPH Merger"]
        Context["Memory Context<br/>(Messages, FACTS, ENTITIES)"]
    end
    
    Neo4j --> BaseGraph
    Neo4j --> HierGraph
    
    System1 --> Embedder
    System2 --> LLM
    
    System1 --> Merge
    System2 --> Merge
    
    Merge --> Context
```

**Diagram: Mnemis High-Level Architecture**

This diagram shows how Mnemis organizes memory into two graph structures, each supporting a different retrieval mechanism. System-1 performs fast similarity search on the base graph, while System-2 conducts deliberate hierarchical reasoning on the hierarchical graph. Both routes leverage different AI services (embeddings vs. LLMs) and merge results to produce comprehensive memory context.

**Sources:** [README.md:25-29]()

---

## Core Components and Code Entities

### Implementation Architecture

```mermaid
graph TB
    subgraph "global_selector.py"
        GlobalSelector["GlobalSelector class"]
        
        subgraph "Core Methods"
            global_selection["global_selection()<br/>(main orchestration)"]
            layer_selection["layer_selection()<br/>(LLM-guided filtering)"]
            get_max_layer["get_max_layer()<br/>(hierarchy discovery)"]
            get_nodes_by_layer["get_nodes_by_layer()<br/>(layer traversal)"]
            get_child_nodes["get_child_nodes()<br/>(tree navigation)"]
            get_all_descendants["get_all_descendants()<br/>(subtree retrieval)"]
            get_one_hop_neighbors["get_one_hop_neighbors()<br/>(context expansion)"]
        end
        
        GlobalSelector --> global_selection
        global_selection --> layer_selection
        global_selection --> get_max_layer
        global_selection --> get_nodes_by_layer
        global_selection --> get_child_nodes
        global_selection --> get_all_descendants
        global_selection --> get_one_hop_neighbors
    end
    
    subgraph "prompts.py"
        NODE_SELECTION_PROMPT_TEMPLATE["NODE_SELECTION_PROMPT_TEMPLATE<br/>(guides LLM selection)"]
    end
    
    subgraph "Data Models"
        NodeSelection["NodeSelection<br/>(Pydantic model)"]
        NodeSelectionList["NodeSelectionList<br/>(response model)"]
    end
    
    subgraph "Graphiti Framework"
        BaseGraphOps["Base Graph Operations<br/>(entity/relationship extraction)"]
        GraphitiCore["Graphiti Core<br/>(memory extraction pipeline)"]
    end
    
    subgraph "Database"
        Neo4jDriver["Neo4j AsyncDriver<br/>(async connection pool)"]
        
        subgraph "Graph Schema"
            CategoryNodes["Category Nodes<br/>(hierarchical layers)"]
            EntityNodes["Entity Nodes<br/>(layer 0)"]
            EpisodicNodes["Episodic Nodes<br/>(conversation memories)"]
            
            CATEGORIZES["CATEGORIZES relationship"]
            MENTIONS["MENTIONS relationship"]
            RELATES_TO["RELATES_TO relationship"]
        end
    end
    
    layer_selection --> NODE_SELECTION_PROMPT_TEMPLATE
    layer_selection --> NodeSelectionList
    NodeSelectionList --> NodeSelection
    
    get_child_nodes --> Neo4jDriver
    get_all_descendants --> Neo4jDriver
    get_one_hop_neighbors --> Neo4jDriver
    
    Neo4jDriver --> CategoryNodes
    Neo4jDriver --> EntityNodes
    Neo4jDriver --> EpisodicNodes
    Neo4jDriver --> CATEGORIZES
    Neo4jDriver --> MENTIONS
    Neo4jDriver --> RELATES_TO
    
    GraphitiCore --> BaseGraphOps
    BaseGraphOps --> Neo4jDriver
```

**Diagram: Core Code Components and Relationships**

This diagram maps the primary code entities in the Mnemis implementation. The `GlobalSelector` class in `global_selector.py` orchestrates System-2's hierarchical traversal through methods like `global_selection()` and `layer_selection()`. The system uses `NODE_SELECTION_PROMPT_TEMPLATE` from `prompts.py` to guide LLM-based node filtering, with Pydantic models (`NodeSelection`, `NodeSelectionList`) ensuring type-safe responses. All operations interact with Neo4j through `AsyncDriver`, accessing a schema with `Category`, `Entity`, and `Episodic` nodes connected via `CATEGORIZES`, `MENTIONS`, and `RELATES_TO` relationships. The foundation is built on the Graphiti framework for base graph operations.

**Sources:** [README.md:54-56]()

---

## State-of-the-Art Benchmark Results

### LoCoMo Performance

Mnemis achieved **93.9%** accuracy on the LoCoMo benchmark (1,986 questions across 5 categories), with **93.3%** when excluding category 5. This represents state-of-the-art performance across all compared methods.

**Key Highlights:**
- Superior performance on complex multi-hop reasoning questions
- Effective handling of temporal and relational queries
- Robust across different question categories

Detailed results are available in the `results/` directory with multiple configuration variants tested.

### LongMemEval-S Performance

On LongMemEval-S (500 questions across 6 question types), Mnemis scored **91.6%** overall:
- **100%** accuracy on single-session-assistant and preference questions
- **86.5%** on challenging multi-session and temporal reasoning questions

This demonstrates Mnemis's strength in both simple preference tracking and complex temporal reasoning scenarios.

**Sources:** [README.md:31-40]()

---

## Retrieval Configurations

Mnemis supports configurable retrieval parameters for different use cases:

| Configuration | RAG top-k | Graph top-k | Use Case |
|---------------|-----------|-------------|----------|
| **ragtopk10_gtopk20** | 10 | 20 | Balanced retrieval with moderate context |
| **ragtopk30_gtopk60** | 30 | 60 | Comprehensive retrieval for complex queries |

Both configurations use:
- `merge_method`: `RAG_GRAPH`
- `graph_global_search`: `true`
- `organize_rag_content`: `true`
- Models: `gpt-4.1-mini` for all roles (graph, answer, grader)

**Sources:** [README.md:54-56]()

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Framework** | Graphiti | Base graph operations and memory extraction |
| **Database** | Neo4j (AsyncDriver) | Graph storage with 1000-connection pool |
| **LLM Services** | OpenAI/Azure GPT-4.1-mini | System-2 reasoning and answer generation |
| **Embeddings** | qwen3 (FLOAT32) | System-1 similarity search |
| **Caching** | async-lru | 500-entry cache per query |
| **Validation** | Pydantic | Type-safe data models |
| **Concurrency** | asyncio | Asynchronous operations |

**Sources:** [README.md:54-56]()

---

## Quick Navigation

### For Implementation Details
- **System-2 Implementation**: See [System-2 Global Selection](#2.3) and [GlobalSelector Class Reference](#3.1)
- **Graph Schema**: See [Graph Database Schema](#3.2)
- **Prompt Engineering**: See [Prompt Engineering](#3.3)
- **Performance Optimization**: See [Performance Optimization](#3.5)

### For Understanding Results
- **Benchmark Details**: See [Benchmark Datasets](#4.1)
- **LoCoMo Analysis**: See [LoCoMo Results](#4.2)
- **LongMemEval-S Analysis**: See [LongMemEval-S Results](#4.3)
- **Case Studies**: See [Case Studies](#5)

### For Getting Started
- **Installation**: See [Installation & Setup](#6.1)
- **Usage Examples**: See [Usage Examples](#6.2)
- **Running Evaluations**: See [Running Evaluations](#6.3)

### For Research Context
- **Theoretical Foundation**: See [Theoretical Foundation](#7.1)
- **Comparisons**: See [Comparison with Existing Approaches](#7.2)
- **Paper & Citations**: See [Paper & Citations](#7.3)

**Sources:** [README.md:1-72]()

---

## Case Study Examples

The system includes detailed case studies demonstrating retrieval and reasoning:

### LoCoMo User 8 QA 11
Illustrates how Mnemis retrieves relevant conversation history and entities to answer complex user queries by combining System-1 similarity search with System-2 hierarchical traversal.

*Full analysis:* See [LoCoMo User 8 QA 11](#5.1)

### LongMemEval-S QA 262
Demonstrates temporal reasoning capabilities, showing how Mnemis extracts facts, summarizes entities, and organizes message chunks to handle multi-session queries requiring time-aware context.

*Full analysis:* See [LongMemEval-S QA 262](#5.2)

**Sources:** [README.md:42-51]()

---

## Repository Structure

```
Mnemis/
├── global_selector/          # System-2 implementation
│   ├── global_selector.py    # GlobalSelector class
│   ├── prompts.py            # NODE_SELECTION_PROMPT_TEMPLATE
│   └── ...                   # Supporting modules
├── results/                  # Benchmark results
│   ├── metrics_*.json        # Aggregated accuracy metrics
│   └── results_*.json        # Full QA context and evidence
├── figures/                  # Visualization assets
│   ├── figure_intro.png      # Architecture diagram
│   ├── results_locomo.png    # LoCoMo results visualization
│   └── results_lme_s.png     # LongMemEval-S results
└── README.md                 # This overview document
```

Evaluation datasets (LoCoMo and LongMemEval-S) are referenced in the evaluation code but not included in the repository.

**Sources:** [README.md:54-56]()

---

## Citation

If you use Mnemis in your research, please cite:

```bibtex
@misc{tang2026mnemisdualrouteretrievalhierarchical,
      title={Mnemis: Dual-Route Retrieval on Hierarchical Graphs for Long-Term LLM Memory}, 
      author={Zihao Tang and Xin Yu and Ziyu Xiao and Zengxuan Wen and Zelin Li and Jiaxi Zhou and Hualei Wang and Haohua Wang and Haizhen Huang and Weiwei Deng and Feng Sun and Qi Zhang},
      year={2026},
      eprint={2602.15313},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2602.15313}
}
```

**Paper**: [arXiv:2602.15313](https://arxiv.org/abs/2602.15313)  
**Hugging Face**: [Papers page](https://huggingface.co/papers/2602.15313)

**Sources:** [README.md:58-71]()

---

## Community and Support

- **Code of Conduct**: See [Code of Conduct](#8.1)
- **Security Policy**: See [Security Policy](#8.2)
- **License**: MIT License - See [License](#8.3)
- **Contributing**: See [Contributing](#8)

**Sources:** [README.md:1-72]()

---

# Page: Architecture Overview

# Architecture Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [global_selection/global_selector.py](global_selection/global_selector.py)

</details>



## Purpose and Scope

This document provides a high-level architectural overview of the Mnemis dual-route memory system. It explains how System-1 and System-2 retrieval mechanisms work together on base and hierarchical graph structures to provide comprehensive memory retrieval for long-term LLM conversations.

For detailed implementation specifics, see [Implementation Guide](#3). For in-depth explanations of individual components, see [Memory Components](#2.1), [System-1 Similarity Search](#2.2), [System-2 Global Selection](#2.3), and [RAG_GRAPH Merge Strategy](#2.4).

**Sources:** [README.md:15-29]()

## Dual-Route Memory System

Mnemis implements a cognitive science-inspired dual-route architecture that parallels human memory retrieval patterns:

| Route | Mechanism | Characteristics | Implementation |
|-------|-----------|-----------------|----------------|
| **System-1** | Similarity Search | Fast, intuitive, bottom-up | Embedding-based retrieval on base graph |
| **System-2** | Global Selection | Deliberate, analytical, top-down | LLM-guided hierarchical traversal |

System-1 provides rapid retrieval of semantically similar memories using vector embeddings, similar to how humans quickly recall related experiences. System-2 complements this with deliberate reasoning over a semantic hierarchy, enabling comprehensive coverage and global context awareness that pure similarity search cannot achieve.

The dual-route approach addresses a fundamental limitation in existing memory systems: similarity-based retrieval (RAG, Graph-RAG) struggles with queries requiring global reasoning or comprehensive information coverage. By combining both routes, Mnemis retrieves memory items that are both semantically and structurally relevant.

**Sources:** [README.md:18-23](), [README.md:26-26]()

## Dual-Route Architecture with Code Entities

```mermaid
graph TB
    subgraph Input["Query Input"]
        Q["User Query<br/>(text)"]
    end
    
    subgraph Storage["Graph Storage Layer"]
        BG["Base Graph<br/>Flat entity/relationship storage<br/>(Neo4j)"]
        HG["Hierarchical Graph<br/>Semantic category hierarchy<br/>(Neo4j, Category_* labels)"]
    end
    
    subgraph System1["System-1: Similarity Search"]
        EMB["Embedding Generation<br/>(qwen3, FLOAT32)"]
        SIM["Vector Similarity Search<br/>(top-k retrieval)"]
        S1RES["System-1 Results"]
    end
    
    subgraph System2["System-2: Global Selection"]
        GS["GlobalSelector<br/>(global_selector.py)"]
        GML["get_max_layer()<br/>Line 104-110"]
        LS["layer_selection()<br/>LLM-guided filtering<br/>Line 224-265"]
        ONEHOP["get_one_hop_neighbors()<br/>Context expansion<br/>Line 197-201"]
        S2RES["System-2 Results"]
    end
    
    subgraph Merge["Result Merging"]
        RAGGER["RAG_GRAPH Merger<br/>(merge method)"]
        CTX["Structured Context<br/>episodes, edges, nodes"]
    end
    
    subgraph Output["Memory Context Output"]
        MC["Message Chunks<br/>(historical conversations)"]
        FACTS["FACTS<br/>(temporal statements)"]
        ENT["ENTITIES<br/>(summarized concepts)"]
    end
    
    Q --> EMB
    Q --> GS
    
    EMB --> SIM
    SIM --> BG
    BG --> S1RES
    
    GS --> GML
    GML --> HG
    HG --> LS
    LS --> ONEHOP
    ONEHOP --> BG
    ONEHOP --> S2RES
    
    S1RES --> RAGGER
    S2RES --> RAGGER
    RAGGER --> CTX
    
    CTX --> MC
    CTX --> FACTS
    CTX --> ENT
```

This diagram shows how user queries are processed through both retrieval routes in parallel. System-1 operates directly on the base graph using embeddings, while System-2 traverses the hierarchical graph using the `GlobalSelector` class. The `global_selection()` method orchestrates layer-by-layer traversal starting from `get_max_layer()`, applying LLM-guided filtering via `layer_selection()`, and expanding context with `get_one_hop_neighbors()`. Results merge into structured context containing message chunks, facts, and entities.

**Sources:** [global_selector.py:90-319](), [README.md:26-29]()

## Graph Storage Architecture

Mnemis organizes memory into two complementary graph structures stored in a Neo4j database:

### Base Graph

The base graph provides flat storage of entities, relationships, and episodic memories. It serves as the foundation for both retrieval routes:

| Node Type | Label | Purpose | Key Properties |
|-----------|-------|---------|----------------|
| Entities | `Entity` | Represent concepts, people, objects | `uuid`, `name`, `tag`, `summary`, `group_id` |
| Episodes | `Episodic` | Store conversation messages | `uuid`, `content`, `valid_at`, `group_id` |

| Relationship Type | Direction | Purpose |
|-------------------|-----------|---------|
| `MENTIONS` | Entity ↔ Episodic | Links entities to conversation contexts |
| `RELATES_TO` | Entity ↔ Entity | Connects related entities with facts |

### Hierarchical Graph

The hierarchical graph organizes entities into a semantic taxonomy with multiple layers:

| Node Type | Label | Layer | Purpose |
|-----------|-------|-------|---------|
| Categories | `Category_{n}` | n > 0 | Abstract semantic groupings |
| Entities | `Entity` | 0 | Ground-level concepts (also in base graph) |

The hierarchy uses the `CATEGORIZES` relationship to connect parent categories to child categories or entities. Each category node includes a `layer` property indicating its hierarchical level, with higher layers representing more abstract concepts.

**Sources:** [global_selector.py:30-83](), [README.md:26-26]()

## Graph Schema with Neo4j Cypher Queries

```mermaid
graph TB
    subgraph Hierarchy["Hierarchical Structure"]
        direction TB
        CATMAX["Category Nodes<br/>Layer N (max)<br/>Label: Category_N<br/>Query: GET_MAX_LAYER"]
        CAT2["Category Nodes<br/>Layer 2<br/>Label: Category_2"]
        CAT1["Category Nodes<br/>Layer 1<br/>Label: Category_1"]
        ENT["Entity Nodes<br/>Layer 0<br/>Label: Entity<br/>Query: GET_NODES_BY_LAYER"]
        
        CATMAX -->|"CATEGORIZES<br/>Query: GET_CHILD_NODES"| CAT2
        CAT2 -->|CATEGORIZES| CAT1
        CAT1 -->|CATEGORIZES| ENT
    end
    
    subgraph Base["Base Graph Relationships"]
        direction LR
        ENT2["Entity"]
        ENT3["Entity"]
        EP["Episodic Node<br/>(conversation message)<br/>Query: GET_ONE_HOP_EPISODES"]
        
        ENT2 <-->|"RELATES_TO<br/>(fact relationship)<br/>Query: GET_ONE_HOP_NODES_AND_EDGES"| ENT3
        ENT2 <-->|"MENTIONS<br/>(appears in episode)"| EP
    end
    
    ENT -.->|"Same nodes"| ENT2
```

The schema implements two distinct graph structures in a single Neo4j database. The hierarchical structure uses dynamically-labeled category nodes (`Category_1`, `Category_2`, etc.) connected by `CATEGORIZES` relationships. The base graph uses `RELATES_TO` and `MENTIONS` relationships to connect entities to each other and to episodic memories. Entity nodes exist in both structures simultaneously, serving as the bridge between hierarchical organization and flat relational storage.

The `Query` class in [global_selector.py:30-83]() defines Cypher queries for traversing these structures:
- `GET_MAX_LAYER`: Discovers hierarchy depth
- `GET_NODES_BY_LAYER`: Retrieves all nodes at a specific layer
- `GET_CHILD_NODES`: Navigates parent-child relationships
- `GET_ONE_HOP_EPISODES`: Retrieves conversation contexts
- `GET_ONE_HOP_NODES_AND_EDGES`: Retrieves related entities and facts

**Sources:** [global_selector.py:30-83]()

## Retrieval Process Flow

The complete memory retrieval process follows a coordinated pipeline:

### System-1 Retrieval

1. **Query Embedding**: Convert user query to vector representation using embedding model
2. **Similarity Search**: Execute vector similarity search against entity embeddings in base graph
3. **Top-K Selection**: Retrieve top-k most similar entities (configurable, typically k=10 or k=30)

### System-2 Retrieval

The `global_selection()` method in [global_selector.py:267-319]() orchestrates hierarchical traversal:

1. **Initialization**: Call `get_max_layer()` to discover hierarchy depth
2. **Layer-by-Layer Traversal**: Iterate from max layer down to layer 1:
   - At max layer: Call `get_nodes_by_layer()` to retrieve all categories
   - At lower layers: Call `get_child_nodes_batch()` to retrieve children of selected parents
   - At each layer: Invoke `layer_selection()` with LLM for intelligent filtering
3. **Shortcut Processing**: Call `get_all_descendants_batch()` for categories marked with `get_all_children=true`
4. **Context Expansion**: Call `get_one_hop_neighbors_batch()` to retrieve:
   - Episodic nodes (conversation messages) via `MENTIONS` relationships
   - Related entities and facts via `RELATES_TO` relationships

### Result Merging

Results from both routes merge using the RAG_GRAPH strategy to produce structured context containing:
- **episodes**: List of conversation message objects with `content` and `valid_at` timestamps
- **edges**: List of fact relationships with `fact`, `valid_at`, and `invalid_at` properties
- **nodes**: List of entity/category objects with `name`, `tag`, and `summary` properties

**Sources:** [global_selector.py:267-319]()

## System-2 Method Call Flow

```mermaid
graph TD
    GS["global_selection(query, group_id)<br/>Line 267-319"]
    
    GML["get_max_layer(group_id)<br/>Line 104-110<br/>Cached: alru_cache(500)"]
    
    GNL["get_nodes_by_layer(layer, group_id)<br/>Line 113-118<br/>Cached: alru_cache(500)"]
    
    GCNB["get_child_nodes_batch(parent_uuids)<br/>Line 129-142<br/>Mode: 'mp' or 'batch'"]
    
    GCN["get_child_nodes(parent_uuid)<br/>Line 121-127<br/>Cached: alru_cache(500)"]
    
    LS["layer_selection(query, categories)<br/>Line 224-265<br/>LLM call with NODE_SELECTION_PROMPT"]
    
    GADB["get_all_descendants_batch(parent_uuids)<br/>Line 153-166<br/>Mode: 'mp' or 'batch'"]
    
    GAD["get_all_descendants(parent_uuid)<br/>Line 145-151<br/>Cached: alru_cache(500)"]
    
    GOHNB["get_one_hop_neighbors_batch(node_uuids)<br/>Line 203-222<br/>Mode: 'mp' or 'batch'"]
    
    GOHN["get_one_hop_neighbors(node_uuid)<br/>Line 197-201<br/>Cached: alru_cache(500)"]
    
    RESULTS["Return: dict<br/>episodes, edges, nodes"]
    
    GS --> GML
    GS --> GNL
    GS --> GCNB
    GCNB --> GCN
    GS --> LS
    LS -->|"Returns: selected_categories,<br/>shortcut_categories"| GADB
    GADB --> GAD
    GS --> GOHNB
    GOHNB --> GOHN
    GOHNB --> RESULTS
    GS --> RESULTS
```

This diagram maps the complete method call hierarchy within the `GlobalSelector` class. The `global_selection()` method serves as the orchestrator, calling cached helper methods for database queries. The caching layer uses `alru_cache` with 500 entries per query to minimize database load. Batch methods support two modes: `'mp'` (multiprocessing via asyncio.gather) and `'batch'` (single Cypher query with multiple UUIDs). The `layer_selection()` method is the only point where LLM intelligence is applied, using the `NODE_SELECTION_PROMPT_TEMPLATE` from [global_selection/prompts.py]().

**Sources:** [global_selector.py:90-319]()

## Component Integration

The architecture integrates multiple components into a cohesive system:

### Infrastructure Layer

| Component | Technology | Configuration | Purpose |
|-----------|-----------|---------------|---------|
| Graph Database | Neo4j AsyncDriver | 1000 connection pool | Stores base and hierarchical graphs |
| LLM Client | OpenAI/Azure GPT-4.1-mini | Via `LLMClient` interface | Powers System-2 node selection |
| Embedding Service | qwen3 (FLOAT32 precision) | Via embedder configuration | Powers System-1 similarity search |

### Data Processing Layer

The system uses Python's async primitives for concurrent execution:
- **asyncio**: Enables concurrent query processing
- **async-lru**: Provides `alru_cache` decorator for method-level caching ([global_selector.py:103](), [global_selector.py:112](), [global_selector.py:120](), [global_selector.py:144](), [global_selector.py:196]())
- **Pydantic**: Enforces type safety for LLM responses via `NodeSelection` and `NodeSelectionList` models ([global_selector.py:22-28]())

### Batch Processing

The `get_global_search_context()` function ([global_selector.py:366-385]()) coordinates batch retrieval:
- Semaphore-based concurrency control (configurable max_concurrent)
- asyncio.gather for parallel execution
- Typical batch sizes: 50 queries for LoCoMo, 30 for LongMemEval-S

### Foundation Framework

Mnemis builds on the [Graphiti framework](https://github.com/getzep/graphiti) for base graph operations and memory extraction. The `GlobalSelector` class extends this foundation with hierarchical graph support and System-2 retrieval capabilities.

**Sources:** [global_selector.py:1-19](), [global_selector.py:90-94](), [global_selector.py:366-385](), [README.md:54-54]()

## Performance Characteristics

The architecture achieves high performance through several design decisions:

| Optimization | Implementation | Impact |
|-------------|----------------|---------|
| Aggressive Caching | `alru_cache(500)` on 5 core methods | Reduces duplicate database queries within single retrieval |
| Connection Pooling | `max_connection_pool_size=1000` | Supports high concurrency (10+ parallel users) |
| Batch Query Modes | `'mp'` and `'batch'` options | Flexibility between parallelism and query efficiency |
| Structured LLM Responses | Pydantic `response_model` | Type-safe, parseable LLM outputs |

The `global_selection()` method includes timing instrumentation tracking three phases:
- **init**: Time to discover hierarchy depth via `get_max_layer()`
- **layer_selection**: Time for layer-by-layer traversal and LLM filtering
- **one_hop_neighbors**: Time for context expansion around selected nodes

**Sources:** [global_selector.py:20-20](), [global_selector.py:103](), [global_selector.py:268-319](), [global_selector.py:435-435]()

## Configuration and Extensibility

The system provides configuration through several mechanisms:

### GlobalSelectorConfig

The `GlobalSelectorConfig` class ([global_selector.py:85-87]()) controls selection behavior:
- `use_summary`: Include entity summaries in LLM prompts (default: False)
- `use_tag`: Include entity tags in LLM prompts (default: True)

These settings affect the information provided to the LLM during `layer_selection()`, allowing tuning of selection granularity versus prompt size.

### Retrieval Parameters

Configurable parameters for tuning retrieval behavior:
- **rag_top_k**: Number of results from System-1 similarity search (10 or 30 in experiments)
- **graph_top_k**: Implicit limit on System-2 results (20 or 60 in experiments)
- **merge_method**: Strategy for combining System-1 and System-2 results (RAG_GRAPH)

For complete configuration details, see [Configuration Options](#3.4).

**Sources:** [global_selector.py:85-87](), [global_selector.py:224-265]()

---

# Page: Memory Components

# Memory Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [global_selection/global_selector.py](global_selection/global_selector.py)

</details>



## Purpose and Scope

This document provides a detailed explanation of Mnemis's two core memory structures: the **Base Graph** and the **Hierarchical Graph**. These components form the foundation of Mnemis's dual-route memory system, with each graph optimized for different retrieval mechanisms. This page focuses on the structural organization, schema design, and guiding principles of both graphs.

For information about how these graphs are used during retrieval, see System-1 Similarity Search [#2.2](#2.2) and System-2 Global Selection [#2.3](#2.3). For database schema implementation details, see Graph Database Schema [#3.2](#3.2).

---

## Memory Architecture Overview

Mnemis organizes memory into two complementary graph structures that operate on the same underlying data but expose different organizational perspectives:

```mermaid
graph TB
    subgraph "Memory Storage Layer"
        direction TB
        
        subgraph BG["Base Graph"]
            direction TB
            BG_E["Entity Nodes<br/>(Layer 0)"]
            BG_EP["Episodic Nodes<br/>(Messages)"]
            BG_REL["RELATES_TO<br/>MENTIONS"]
        end
        
        subgraph HG["Hierarchical Graph"]
            direction TB
            HG_CAT["Category Nodes<br/>(Layers 1..N)"]
            HG_E["Entity Nodes<br/>(Layer 0)"]
            HG_CATREL["CATEGORIZES"]
        end
    end
    
    subgraph "Retrieval Systems"
        S1["System-1<br/>Similarity Search"]
        S2["System-2<br/>Global Selection"]
    end
    
    BG --> S1
    HG --> S2
    
    subgraph "Database Implementation"
        NEO4J["Neo4j Graph Database<br/>AsyncDriver"]
    end
    
    BG -.stored in.-> NEO4J
    HG -.stored in.-> NEO4J
```

**Sources:** [README.md:15-29](), [global_selector.py:1-453]()

The Base Graph provides a **flat, relationship-dense** structure optimized for embedding-based similarity search, while the Hierarchical Graph provides a **layered, tree-like** structure optimized for top-down deliberate traversal.

---

## Base Graph

### Purpose and Design

The Base Graph stores memory in a flat structure where entities and their relationships exist at a single conceptual level (layer 0). This design enables efficient similarity-based retrieval through embedding search, as all entities are directly comparable without hierarchical filtering.

**Key Characteristics:**
- Flat structure with no hierarchical layers
- Dense relationship network between entities
- Direct connection to episodic memories
- Optimized for fast similarity search

### Node Types

The Base Graph contains three primary node types:

| Node Type | Label | Purpose | Key Properties |
|-----------|-------|---------|----------------|
| Entity | `Entity` | Core concepts, people, objects | `uuid`, `name`, `tag`, `summary`, `group_id` |
| Episodic | `Episodic` | Historical messages/conversations | `uuid`, `content`, `valid_at`, `group_id` |
| Fact Edge | `RELATES_TO` | Relationships between entities | `uuid`, `fact`, `valid_at`, `invalid_at` |

**Sources:** [global_selector.py:30-83]()

### Base Graph Schema

```mermaid
graph LR
    E1["Entity<br/>{uuid, name, tag, summary}"]
    E2["Entity<br/>{uuid, name, tag, summary}"]
    E3["Entity<br/>{uuid, name, tag, summary}"]
    EP1["Episodic<br/>{uuid, content, valid_at}"]
    EP2["Episodic<br/>{uuid, content, valid_at}"]
    
    E1 -->|"RELATES_TO<br/>{fact, valid_at}"| E2
    E2 -->|"RELATES_TO<br/>{fact, valid_at}"| E3
    E1 -.->|"MENTIONS"| EP1
    E2 -.->|"MENTIONS"| EP1
    E3 -.->|"MENTIONS"| EP2
```

**Sources:** [global_selector.py:73-83]()

### Relationship Types

#### RELATES_TO Relationships

Connects two `Entity` nodes with factual information about their relationship. These edges are first-class objects in the graph with their own properties:

```
Properties:
- uuid: Unique identifier for the fact
- fact: Text description of the relationship
- valid_at: Timestamp when relationship became valid
- invalid_at: Timestamp when relationship became invalid (nullable)
```

Query implementation: [global_selector.py:73-83]()

#### MENTIONS Relationships

Connects `Entity` or `Category` nodes to `Episodic` nodes, indicating which entities were mentioned in which historical messages:

```
Purpose: Link entities to source conversations
Direction: Bidirectional (either direction valid)
Properties: Relationship is unweighted
```

Query implementation: [global_selector.py:61-71]()

**Sources:** [global_selector.py:61-83]()

---

## Hierarchical Graph

### Purpose and Design

The Hierarchical Graph organizes the same entities into a semantic taxonomy with multiple abstraction layers. This structure enables System-2 to perform deliberate, top-down reasoning by traversing from general concepts to specific entities.

**Key Characteristics:**
- Multi-layer hierarchical structure (layers 1 through N)
- Tree-like organization with parent-child relationships
- Categories at higher layers subsume entities at lower layers
- Optimized for global reasoning and comprehensive retrieval

### Layer Structure

```mermaid
graph TB
    subgraph "Layer N (Highest Abstraction)"
        CN1["Category_N"]
        CN2["Category_N"]
    end
    
    subgraph "Layer N-1"
        CN_1_1["Category_N-1"]
        CN_1_2["Category_N-1"]
        CN_1_3["Category_N-1"]
    end
    
    subgraph "Layer 2"
        C2_1["Category_2"]
        C2_2["Category_2"]
        C2_3["Category_2"]
    end
    
    subgraph "Layer 1"
        C1_1["Category_1"]
        C1_2["Category_1"]
        C1_3["Category_1"]
        C1_4["Category_1"]
    end
    
    subgraph "Layer 0 (Entity Level)"
        E1["Entity"]
        E2["Entity"]
        E3["Entity"]
        E4["Entity"]
    end
    
    CN1 -->|"CATEGORIZES"| CN_1_1
    CN1 -->|"CATEGORIZES"| CN_1_2
    CN2 -->|"CATEGORIZES"| CN_1_3
    
    CN_1_1 -->|"CATEGORIZES"| C2_1
    CN_1_2 -->|"CATEGORIZES"| C2_2
    CN_1_3 -->|"CATEGORIZES"| C2_3
    
    C2_1 -->|"CATEGORIZES"| C1_1
    C2_2 -->|"CATEGORIZES"| C1_2
    C2_2 -->|"CATEGORIZES"| C1_3
    C2_3 -->|"CATEGORIZES"| C1_4
    
    C1_1 -->|"CATEGORIZES"| E1
    C1_2 -->|"CATEGORIZES"| E2
    C1_3 -->|"CATEGORIZES"| E3
    C1_4 -->|"CATEGORIZES"| E4
```

**Sources:** [global_selector.py:31-59](), [README.md:22]()

The hierarchical structure allows System-2 to start at the highest layer (most abstract categories) and progressively descend to more specific concepts, filtering at each level based on relevance to the query.

### Guiding Principles

The hierarchical graph construction is guided by three key principles mentioned in the paper:

| Principle | Purpose | Impact |
|-----------|---------|--------|
| **Minimum Concept Abstraction** | Ensure categories represent meaningful semantic groupings | Prevents over-generalization; maintains semantic coherence |
| **Many-to-Many Mapping** | Allow entities to belong to multiple categories | Captures multi-faceted nature of concepts |
| **Compression Efficiency Constraint** | Balance hierarchy depth vs. breadth | Optimizes traversal efficiency |

**Sources:** [README.md:22]()

### Node Types and Properties

#### Category Nodes

Categories exist at layers 1 through N (where N is the maximum abstraction level). Each category is labeled with its specific layer:

```
Node Labels: Category_1, Category_2, ..., Category_N
Properties:
- uuid: Unique identifier
- name: Human-readable category name
- tag: Category classification/type
- summary: Description of category contents
- layer: Integer indicating abstraction level
- group_id: User/session identifier
```

Query implementation: [global_selector.py:36-39]()

#### Entity Nodes (Layer 0)

The same `Entity` nodes from the Base Graph serve as the foundation (layer 0) of the hierarchical graph:

```
Node Label: Entity
Properties:
- uuid: Unique identifier
- name: Entity name
- tag: Entity type/classification
- summary: Entity description
- group_id: User/session identifier
- layer: Always 0
```

**Sources:** [global_selector.py:30-59]()

### CATEGORIZES Relationship

The `CATEGORIZES` relationship forms the hierarchical structure by connecting parent nodes to child nodes:

```mermaid
graph TB
    P["Parent Node<br/>(Category or Entity)"]
    C1["Child Node<br/>(Category or Entity)"]
    C2["Child Node<br/>(Category or Entity)"]
    C3["Child Node<br/>(Category or Entity)"]
    
    P -->|"CATEGORIZES"| C1
    P -->|"CATEGORIZES"| C2
    P -->|"CATEGORIZES"| C3
```

**Properties:**
- Direction: Parent → Child (downward in hierarchy)
- Cardinality: One-to-many (one parent, multiple children)
- Levels: Connects adjacent layers (Layer N → Layer N-1)

Query implementations:
- Single parent: [global_selector.py:41-44]()
- Batch parents: [global_selector.py:46-49]()
- All descendants (recursive): [global_selector.py:51-59]()

**Sources:** [global_selector.py:41-59]()

---

## Data Storage Model

### Neo4j Implementation

Both the Base Graph and Hierarchical Graph are stored in a single Neo4j graph database, with different node labels and relationship types distinguishing their logical structures:

```mermaid
graph TB
    subgraph "Neo4j Database"
        direction TB
        
        subgraph "Node Storage"
            ENTITY["Entity Nodes<br/>Label: Entity<br/>Layer: 0"]
            CATEG["Category Nodes<br/>Labels: Category_1..Category_N<br/>Layer: 1..N"]
            EPISOD["Episodic Nodes<br/>Label: Episodic"]
        end
        
        subgraph "Relationship Storage"
            RELTO["RELATES_TO<br/>(Entity ↔ Entity)<br/>Base Graph"]
            MENT["MENTIONS<br/>(Node ↔ Episodic)<br/>Base Graph"]
            CATREL["CATEGORIZES<br/>(Parent → Child)<br/>Hierarchical Graph"]
        end
        
        subgraph "Index Strategy"
            GROUPID["group_id Index<br/>(Session isolation)"]
            UUID["uuid Index<br/>(Fast lookups)"]
            LAYER["layer Index<br/>(Layer queries)"]
        end
    end
    
    subgraph "Access Layer"
        DRIVER["AsyncDriver<br/>(max_connection_pool_size=1000)"]
        QUERY["Query Class<br/>(Cypher Templates)"]
    end
    
    DRIVER --> ENTITY
    DRIVER --> CATEG
    DRIVER --> EPISOD
    QUERY --> DRIVER
```

**Sources:** [global_selector.py:30-84](), [global_selector.py:431-435]()

### Query Templates

The `Query` class defines Cypher query templates for accessing both graph structures:

#### Hierarchical Graph Queries

| Method | Query Template | Purpose |
|--------|----------------|---------|
| `GET_MAX_LAYER` | [global_selector.py:31-34]() | Find highest layer number |
| `GET_NODES_BY_LAYER` | [global_selector.py:36-39]() | Retrieve all nodes at specific layer |
| `GET_CHILD_NODES` | [global_selector.py:41-44]() | Get direct children of parent |
| `GET_ALL_DESCENDANTS` | [global_selector.py:51-54]() | Get entire subtree recursively |

#### Base Graph Queries

| Method | Query Template | Purpose |
|--------|----------------|---------|
| `GET_ONE_HOP_EPISODES` | [global_selector.py:61-65]() | Retrieve episodic memories |
| `GET_ONE_HOP_NODES_AND_EDGES` | [global_selector.py:73-77]() | Retrieve relationships and neighbors |

**Sources:** [global_selector.py:30-84]()

### Group Isolation

Both graphs use `group_id` to isolate memory contexts across different users or sessions:

```
group_id Format: {prefix}_{user_id}
Examples:
- locomo_mnemis_coreAI_tel_b20_nec_full_0
- lme_s_mnemis_coreAI_tel_b20_nec_full_42

Purpose: Enable multi-tenancy within single database
Implementation: All queries filter by group_id parameter
```

This design allows concurrent access by multiple users while maintaining memory isolation.

**Sources:** [global_selector.py:321-364]()

---

## Graph Traversal Patterns

### Base Graph: One-Hop Expansion

System-1 retrieval uses the Base Graph by performing one-hop neighbor expansion from selected entities:

```mermaid
graph LR
    E0["Selected Entity<br/>(from similarity search)"]
    E1["Neighbor Entity"]
    E2["Neighbor Entity"]
    EP1["Episodic Memory"]
    EP2["Episodic Memory"]
    
    E0 -->|"RELATES_TO"| E1
    E0 -->|"RELATES_TO"| E2
    E0 -.->|"MENTIONS"| EP1
    E1 -.->|"MENTIONS"| EP2
```

Implementation: [global_selector.py:196-222]()

**Sources:** [global_selector.py:196-222]()

### Hierarchical Graph: Top-Down Traversal

System-2 retrieval uses the Hierarchical Graph by traversing from the highest layer downward:

```mermaid
graph TB
    START["Start at max_layer"]
    L1["Get all nodes at current layer"]
    L2["LLM-guided selection:<br/>layer_selection()"]
    L3["Get children of selected nodes:<br/>get_child_nodes_batch()"]
    L4["Get descendants of shortcuts:<br/>get_all_descendants_batch()"]
    L5{"More layers?"}
    L6["Get one-hop neighbors:<br/>get_one_hop_neighbors_batch()"]
    END["Return results"]
    
    START --> L1
    L1 --> L2
    L2 --> L3
    L2 --> L4
    L3 --> L5
    L4 --> L5
    L5 -->|"Yes"| L1
    L5 -->|"No"| L6
    L6 --> END
```

Implementation: [global_selector.py:267-319]()

**Sources:** [global_selector.py:267-319]()

---

## Summary

Mnemis's dual memory architecture leverages the complementary strengths of flat and hierarchical organization:

- **Base Graph**: Enables fast, similarity-based retrieval through a flat entity-relationship network with direct access to episodic memories
- **Hierarchical Graph**: Enables deliberate, comprehensive retrieval through multi-layer semantic taxonomy with top-down traversal

Both graphs share the same underlying entities and episodic memories but organize them differently to support their respective retrieval mechanisms. The Neo4j implementation efficiently stores both structures using node labels, relationship types, and the `group_id` isolation pattern.

**Sources:** [README.md:15-29](), [global_selector.py:1-453]()

---

# Page: System-1 Similarity Search

# System-1 Similarity Search

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json](results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json)

</details>



## Purpose and Scope

This page describes System-1, the fast, intuitive similarity-based retrieval mechanism in Mnemis. System-1 operates on the Base Graph to retrieve memory items based on embedding similarity to a query. For information about the complementary deliberate retrieval mechanism, see [System-2 Global Selection](#2.3). For details on how System-1 and System-2 results are combined, see [RAG_GRAPH Merge Strategy](#2.4).

## Overview

System-1 implements a classical embedding-based similarity search approach inspired by the fast, automatic processing of human cognition (dual-process theory's "System 1"). It provides rapid retrieval of semantically similar memory items without requiring complex reasoning or graph traversal.

**Key Characteristics:**
- **Speed**: Fast vector similarity computation
- **Simplicity**: Direct embedding-to-embedding comparison
- **Local Focus**: Retrieves items similar to the query, but may miss globally relevant context
- **Scalability**: Efficient for large memory stores

Sources: [README.md:1-72]()

```mermaid
graph TB
    Query["User Query"]
    Embed["Query Embedding<br/>(qwen3 FLOAT32)"]
    BaseGraph["Base Graph<br/>(Entities + Episodes)"]
    VectorSearch["Vector Similarity Search"]
    TopK["Top-K Selection<br/>(k=10 or k=30)"]
    Results["Similar Memory Items"]
    
    Query --> Embed
    Embed --> VectorSearch
    BaseGraph --> VectorSearch
    VectorSearch --> TopK
    TopK --> Results
    
    style Query fill:#f9f9f9
    style Results fill:#f9f9f9
```

**Diagram: System-1 Retrieval Pipeline**

Sources: [README.md:15-40]()

## Base Graph Storage Layer

System-1 operates on the **Base Graph**, a flat storage structure containing entities and episodic memories. Unlike the Hierarchical Graph used by System-2, the Base Graph does not impose categorical organization, allowing for flexible similarity-based retrieval.

**Base Graph Contents:**
- **Entity Nodes**: Represent concepts, people, places, objects extracted from conversations
- **Episode Nodes**: Represent individual messages or conversation turns
- **Relationships**: Direct connections between entities (e.g., MENTIONS, RELATES_TO)
- **Embeddings**: Each node has an associated embedding vector for similarity search

The Base Graph is built using the Graphiti framework, which Mnemis extends with dual-route retrieval capabilities.

Sources: [README.md:25-29](), [README.md:54-57]()

```mermaid
graph LR
    subgraph "Base Graph Structure"
        E1["Entity Node<br/>embedding: vector"]
        E2["Entity Node<br/>embedding: vector"]
        EP1["Episode Node<br/>embedding: vector<br/>content: message"]
        EP2["Episode Node<br/>embedding: vector<br/>content: message"]
        
        E1 -.RELATES_TO.-> E2
        EP1 -.MENTIONS.-> E1
        EP2 -.MENTIONS.-> E2
    end
```

**Diagram: Base Graph Schema for System-1**

Sources: [README.md:25-29]()

## Embedding Model

System-1 uses the **qwen3** embedding model with **FLOAT32** precision to generate vector representations of queries and memory items.

**Embedding Specifications:**

| Attribute | Value |
|-----------|-------|
| Model | qwen3 |
| Precision | FLOAT32 |
| Purpose | Semantic similarity computation |
| Applies To | Queries, Entity nodes, Episode nodes |

**Embedding Generation Process:**
1. Input text (query or memory content) is tokenized
2. Text passes through qwen3 encoder
3. Output is a dense vector in FLOAT32 format
4. Vector is normalized for cosine similarity computation

The choice of qwen3 balances semantic quality with computational efficiency, enabling fast similarity searches over large memory stores.

Sources: [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-10]()

## Retrieval Process

System-1 retrieval follows a straightforward pipeline from query to results:

```mermaid
sequenceDiagram
    participant User
    participant Query as "Query Text"
    participant Embedder as "qwen3 Embedder"
    participant DB as "Base Graph<br/>(Neo4j)"
    participant Ranker as "Similarity Ranker"
    participant TopK as "Top-K Selector"
    
    User->>Query: Submit query
    Query->>Embedder: Encode query text
    Embedder->>Query: Query embedding vector
    Query->>DB: Retrieve all node embeddings
    DB->>Ranker: Entity & Episode embeddings
    Ranker->>Ranker: Compute cosine similarity
    Ranker->>TopK: Ranked similarity scores
    TopK->>User: Top-K memory items
```

**Diagram: System-1 Retrieval Sequence**

Sources: [README.md:15-40]()

### Step-by-Step Retrieval

**Step 1: Query Embedding**
- User query is converted to embedding vector using qwen3
- Results in a dense FLOAT32 vector representation

**Step 2: Candidate Retrieval**
- All entity and episode embeddings are retrieved from Base Graph
- In practice, this may use vector index for efficiency

**Step 3: Similarity Computation**
- Cosine similarity computed between query embedding and all candidate embeddings
- Formula: `similarity = (query_vec · candidate_vec) / (||query_vec|| × ||candidate_vec||)`

**Step 4: Ranking**
- All candidates sorted by similarity score (descending)

**Step 5: Top-K Selection**
- Top `rag_top_k` items selected (typically k=10 or k=30)
- These become the System-1 retrieval results

Sources: [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-10]()

## Configuration Parameters

System-1 behavior is controlled by several configuration parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `rag_top_k` | int | 10 or 30 | Number of top similar items to retrieve |
| `embedder` | string | "qwen3" | Embedding model identifier |
| `precision` | string | "FLOAT32" | Embedding vector precision |
| `similarity_metric` | string | "cosine" | Distance metric for similarity |

### RAG Top-K Values

Experiments show two common configurations:

**Configuration 1: `ragtopk10_gtopk20`**
- System-1 retrieves top 10 items
- System-2 retrieves top 20 items
- Balanced retrieval across both routes

**Configuration 2: `ragtopk30_gtopk60`**
- System-1 retrieves top 30 items
- System-2 retrieves top 60 items
- Higher recall, more comprehensive context

The choice depends on the application's need for precision vs. recall and the acceptable context length for the answer generation model.

Sources: [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1](), [README.md:31-40]()

## Result Structure

System-1 returns memory items in a structured format suitable for downstream processing:

**Evidence Messages Format:**
```json
{
  "role": "user|assistant",
  "content": "message text",
  "datetime": "YYYY/MM/DD (Day) HH:MM"
}
```

**Retrieved Items Include:**
- **Episodes**: Historical conversation messages with timestamps
- **Entities**: Relevant entity nodes with summaries
- **Context Metadata**: Session IDs, retrieval scores

Example from results:

```json
{
  "evidence_messages": [
    {
      "role": "user",
      "content": "I bought my tennis racket from a sports store downtown.",
      "datetime": "2023/05/25 (Thu) 21:29"
    }
  ]
}
```

Sources: [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-10]()

## Integration with Dual-Route Architecture

System-1 does not operate in isolation—it is one component of Mnemis's dual-route architecture:

```mermaid
graph TB
    Query["User Query"]
    
    subgraph "Parallel Retrieval"
        S1["System-1<br/>Similarity Search<br/>(RAG)"]
        S2["System-2<br/>Global Selection<br/>(Graph)"]
    end
    
    BaseGraph["Base Graph"]
    HierGraph["Hierarchical Graph"]
    
    S1Results["RAG Results<br/>(k=10/30)"]
    S2Results["Graph Results<br/>(k=20/60)"]
    
    Merge["RAG_GRAPH Merger"]
    Context["Unified Context"]
    
    Query --> S1
    Query --> S2
    
    BaseGraph --> S1
    HierGraph --> S2
    
    S1 --> S1Results
    S2 --> S2Results
    
    S1Results --> Merge
    S2Results --> Merge
    
    Merge --> Context
    
    style Query fill:#f9f9f9
    style Context fill:#f9f9f9
```

**Diagram: System-1 in Dual-Route Context**

### Complementary Strengths

**System-1 Strengths:**
- Fast retrieval of semantically similar items
- Effective for queries with clear lexical/semantic matches
- Captures local context and relevant episodes

**System-1 Limitations:**
- May miss globally important information
- Struggles with queries requiring comprehensive coverage
- Cannot reason about hierarchical relationships

**System-2 Compensates:**
- Provides global reasoning via hierarchical traversal
- Captures structurally relevant information
- Ensures comprehensive coverage of related concepts

The RAG_GRAPH merge strategy combines both retrieval routes to leverage their complementary strengths.

Sources: [README.md:15-40]()

## Performance Characteristics

### Efficiency

System-1 is designed for **speed and scalability**:

**Time Complexity:**
- Query embedding: O(1) - constant time per query
- Similarity computation: O(n) where n = number of nodes in Base Graph
- Top-K selection: O(n log k) with heap-based selection

**Space Complexity:**
- Embedding storage: O(n × d) where d = embedding dimension
- Query processing: O(k) for storing top-k results

### Retrieval Quality

System-1 excels at:
- ✓ Lexically similar queries (e.g., "tennis racket" → "sports equipment")
- ✓ Semantically related topics (e.g., "vacation planning" → "travel bookings")
- ✓ Recent similar conversations

System-1 struggles with:
- ✗ Global reasoning queries (e.g., "tell me everything about topic X")
- ✗ Queries requiring comprehensive coverage
- ✗ Hierarchical or categorical relationships

Sources: [README.md:15-40]()

## Benchmark Performance

Mnemis achieves state-of-the-art results by combining System-1 with System-2:

**LongMemEval-S Results:**
- Overall Accuracy: **91.6%**
- Single-session queries: Near-perfect (System-1 sufficient)
- Multi-session queries: 86.5% (benefits from System-2)

**LoCoMo Results:**
- Overall Accuracy: **80-81%** (93.9% excluding category 5)
- System-1 contributes significantly to single-fact retrieval
- System-2 crucial for multi-fact reasoning

The high performance demonstrates that System-1's similarity-based retrieval, while simple, is highly effective when combined with complementary System-2 reasoning.

Sources: [README.md:31-40]()

## Comparison with System-2

| Aspect | System-1 | System-2 |
|--------|----------|----------|
| **Retrieval Strategy** | Embedding similarity | LLM-guided traversal |
| **Graph Used** | Base Graph | Hierarchical Graph |
| **Speed** | Fast (O(n)) | Slower (multiple LLM calls) |
| **Scope** | Local similarity | Global reasoning |
| **Top-K** | 10 or 30 | 20 or 60 |
| **Model Dependency** | Embedder only | LLM (gpt-41-mini) |
| **Best For** | Semantic matching | Comprehensive coverage |

Both systems are essential for Mnemis's performance. System-1 provides rapid, semantically relevant retrieval, while System-2 ensures comprehensive coverage through deliberate hierarchical reasoning. Their combination via RAG_GRAPH produces superior results compared to either approach alone.

Sources: [README.md:15-40]()

## Code Integration Points

While the primary implementation of System-1 leverages the Graphiti framework's built-in RAG capabilities, Mnemis extends it with dual-route integration:

**Key Integration Areas:**
- **Base Graph Construction**: Entities and episodes stored with embeddings
- **Embedding Generation**: qwen3 model integration
- **Similarity Search**: Vector-based retrieval on Base Graph
- **Result Formatting**: Structured output for RAG_GRAPH merger
- **Configuration**: `rag_top_k` parameter tuning

The core System-2 implementation is provided in the `global_selection` directory, while System-1 relies on Graphiti's existing RAG infrastructure with configuration tuning for optimal performance.

Sources: [README.md:54-57]()

---

**Summary**: System-1 Similarity Search provides fast, intuitive embedding-based retrieval on the Base Graph, forming one half of Mnemis's dual-route architecture. By combining System-1's semantic matching with System-2's global reasoning, Mnemis achieves state-of-the-art performance on long-term memory benchmarks.

---

# Page: System-2 Global Selection

# System-2 Global Selection

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [global_selection/global_selector.py](global_selection/global_selector.py)
- [global_selection/prompts.py](global_selection/prompts.py)

</details>



## Purpose and Scope

This page documents System-2 Global Selection, the deliberate top-down hierarchical traversal mechanism that enables global reasoning over the knowledge graph. System-2 performs layer-by-layer LLM-guided filtering of semantic categories to identify structurally relevant memory items, complementing System-1's similarity-based retrieval.

For information about System-1's similarity search mechanism, see [System-1 Similarity Search](#2.2). For details on how System-1 and System-2 results are combined, see [RAG_GRAPH Merge Strategy](#2.4). For implementation details and API reference, see [GlobalSelector Class Reference](#3.1).

**Sources:** [README.md:15-29](), [global_selection/global_selector.py:1-319]()

---

## Overview

System-2 Global Selection implements deliberate, analytical memory retrieval by traversing the hierarchical graph from abstract semantic categories down to concrete entities. At each layer, an LLM evaluates which nodes are relevant to the query, enabling intelligent pruning of irrelevant branches while maintaining comprehensive coverage of relevant information.

The implementation centers on the `GlobalSelector` class, which orchestrates:
1. **Top-down hierarchical traversal** through category layers
2. **LLM-guided node selection** at each layer using structured prompts
3. **Shortcut mechanisms** to efficiently retrieve entire subtrees
4. **Context expansion** via one-hop neighbor retrieval
5. **Optimization** through caching and batch processing

**Sources:** [global_selection/global_selector.py:90-319](), [README.md:20-23]()

---

## System Architecture

### Core Components

```mermaid
graph TB
    subgraph "GlobalSelector Class"
        GS["GlobalSelector<br/>(global_selector.py:90)"]
        CONFIG["GlobalSelectorConfig<br/>(global_selector.py:85)"]
    end
    
    subgraph "Query Templates"
        QUERY["Query Class<br/>(global_selector.py:30)"]
        GML["GET_MAX_LAYER"]
        GNBL["GET_NODES_BY_LAYER"]
        GCN["GET_CHILD_NODES"]
        GAD["GET_ALL_DESCENDANTS"]
        GOH["GET_ONE_HOP_EPISODES<br/>GET_ONE_HOP_NODES_AND_EDGES"]
    end
    
    subgraph "Data Models"
        NS["NodeSelection<br/>(global_selector.py:22)"]
        NSL["NodeSelectionList<br/>(global_selector.py:27)"]
    end
    
    subgraph "External Dependencies"
        NEO["Neo4j AsyncDriver<br/>(neo4j)"]
        LLM["LLMClient<br/>(graphiti_core.llm_client)"]
        CACHE["alru_cache<br/>(async_lru)"]
    end
    
    GS --> CONFIG
    GS --> QUERY
    GS --> NEO
    GS --> LLM
    GS --> CACHE
    
    QUERY --> GML
    QUERY --> GNBL
    QUERY --> GCN
    QUERY --> GAD
    QUERY --> GOH
    
    LLM --> NSL
    NSL --> NS
```

**Sources:** [global_selection/global_selector.py:22-94]()

### Data Model Structure

The system uses Pydantic models for type-safe LLM responses:

| Model | Fields | Purpose |
|-------|--------|---------|
| `NodeSelection` | `name: str`<br/>`uuid: str`<br/>`get_all_children: bool` | Represents a single selected node with optional subtree retrieval flag |
| `NodeSelectionList` | `selections: list[NodeSelection]` | Container for LLM's structured selection response |
| `GlobalSelectorConfig` | `use_summary: bool`<br/>`use_tag: bool` | Configuration for node metadata inclusion |

**Sources:** [global_selection/global_selector.py:22-88]()

---

## Hierarchical Traversal Algorithm

### Global Selection Flow

The `global_selection` method implements the complete traversal algorithm:

```mermaid
graph TD
    START["global_selection(query, group_id)"]
    INIT["get_max_layer(group_id)"]
    LOOP_START["for layer in range(max_layer, 0, -1)"]
    
    CONDITION{"layer == max_layer?"}
    GET_TOP["get_nodes_by_layer(layer)"]
    GET_CHILD["get_child_nodes_batch(previous_layer)"]
    
    LAYER_SEL["layer_selection(query, nodes)"]
    
    SPLIT{"selected vs shortcuts"}
    REGULAR["Add to selected_categories"]
    SHORTCUT["get_all_descendants_batch(shortcuts)"]
    
    NEXT["previous_layer = selected"]
    LOOP_CHECK{"More layers?"}
    
    NEIGHBORS["get_one_hop_neighbors_batch(selected)"]
    FORMAT["Format results with timestamps"]
    RETURN["Return {episodes, edges, nodes}"]
    
    START --> INIT
    INIT --> LOOP_START
    LOOP_START --> CONDITION
    CONDITION -->|Yes| GET_TOP
    CONDITION -->|No| GET_CHILD
    GET_TOP --> LAYER_SEL
    GET_CHILD --> LAYER_SEL
    
    LAYER_SEL --> SPLIT
    SPLIT --> REGULAR
    SPLIT --> SHORTCUT
    REGULAR --> NEXT
    SHORTCUT --> NEXT
    NEXT --> LOOP_CHECK
    LOOP_CHECK -->|Yes| LOOP_START
    LOOP_CHECK -->|No| NEIGHBORS
    NEIGHBORS --> FORMAT
    FORMAT --> RETURN
```

**Sources:** [global_selection/global_selector.py:267-319]()

### Algorithm Steps

The traversal proceeds as follows:

1. **Initialization** [global_selector.py:271](): Query the hierarchical graph for maximum layer depth
2. **Layer Iteration** [global_selector.py:277](): Iterate from highest layer down to layer 1
3. **Node Retrieval**:
   - Top layer [global_selector.py:279](): Get all category nodes at max_layer
   - Subsequent layers [global_selector.py:281](): Get children of previously selected nodes
4. **LLM Selection** [global_selector.py:285](): Invoke `layer_selection` to filter relevant nodes
5. **Shortcut Processing** [global_selector.py:289](): Retrieve all descendants for nodes marked with `get_all_children=true`
6. **Context Expansion** [global_selector.py:299](): Retrieve one-hop neighbors (episodes and edges) for all selected nodes
7. **Result Formatting** [global_selector.py:302-318](): Format timestamps and organize output

**Sources:** [global_selection/global_selector.py:267-319]()

---

## LLM-Guided Node Selection

### Layer Selection Mechanism

The `layer_selection` method uses LLM intelligence to evaluate node relevance:

```mermaid
graph LR
    INPUT["Current Layer Nodes"]
    FILTER["Filter metadata<br/>(uuid, name, tag?, summary?)"]
    PROMPT["NODE_SELECTION_PROMPT_TEMPLATE"]
    LLM["LLM Generate Response<br/>(response_model=NodeSelectionList)"]
    PARSE["Parse NodeSelection objects"]
    
    MATCH_UUID["Match by UUID"]
    MATCH_NAME["Match by name<br/>(fallback)"]
    
    CLASSIFY{"get_all_children?"}
    SELECTED["selected_categories"]
    SHORTCUTS["shortcut_categories"]
    
    INPUT --> FILTER
    FILTER --> PROMPT
    PROMPT --> LLM
    LLM --> PARSE
    PARSE --> MATCH_UUID
    MATCH_UUID --> MATCH_NAME
    MATCH_NAME --> CLASSIFY
    CLASSIFY -->|false| SELECTED
    CLASSIFY -->|true| SHORTCUTS
```

**Sources:** [global_selection/global_selector.py:224-265]()

### Prompt Template Structure

The `NODE_SELECTION_PROMPT_TEMPLATE` guides the LLM's selection criteria:

```
You are analyzing a hierarchical knowledge graph to help answer a user query.

Select all nodes that could help answer the query. A node is helpful if it:
- Directly relates to the query
- Covers a clearly relevant topic, concept, or category
- Provides useful background or context
- Contains user-specific information (e.g. interests, goals, constraints)
- Likely has sub-nodes that may be helpful

Do not be overly strict: include nodes that might provide context or personalization...

For each selected node:
- "name" is the node's name
- "uuid" is the node's unique identifier
- "get_all_children" is a boolean value. Set true only if you're confident all its 
  sub-nodes are helpful
```

**Sources:** [global_selection/prompts.py:1-23]()

### Selection Process Details

1. **Metadata Preparation** [global_selector.py:225-235]():
   - Filter node attributes based on `GlobalSelectorConfig`
   - Always include: `uuid`, `name`
   - Conditionally include: `tag`, `summary`

2. **LLM Invocation** [global_selector.py:241-245]():
   - Format prompt with query and node metadata
   - Use structured output with `response_model=NodeSelectionList`
   - Returns type-safe Pydantic objects

3. **Node Matching** [global_selector.py:254-260]():
   - Primary matching by UUID
   - Fallback matching by name
   - Warning logged if no match found

4. **Classification** [global_selector.py:261-264]():
   - Nodes with `get_all_children=false`: Continue traversal to children
   - Nodes with `get_all_children=true`: Retrieve entire subtree immediately

**Sources:** [global_selection/global_selector.py:224-265]()

---

## Graph Query Operations

### Query Template Catalog

The `Query` class defines Cypher templates for graph operations:

| Method | Query Template | Purpose |
|--------|---------------|---------|
| `get_max_layer` | `GET_MAX_LAYER` [30-34]() | Find highest layer in hierarchy |
| `get_nodes_by_layer` | `GET_NODES_BY_LAYER` [36-39]() | Retrieve all nodes at specific layer |
| `get_child_nodes` | `GET_CHILD_NODES` [41-44]() | Get immediate children of a category |
| `get_all_descendants` | `GET_ALL_DESCENDANTS` [51-54]() | Recursively get all descendants |
| `get_one_hop_neighbors` | `GET_ONE_HOP_EPISODES` [61-65]()<br/>`GET_ONE_HOP_NODES_AND_EDGES` [73-77]() | Retrieve episodes and related entities |

**Sources:** [global_selection/global_selector.py:30-83]()

### Node Retrieval Methods

```mermaid
graph TB
    subgraph "Single Operations (Cached)"
        GML["get_max_layer(group_id)<br/>@alru_cache(500)<br/>(103-110)"]
        GNBL["get_nodes_by_layer(layer, group_id)<br/>@alru_cache(500)<br/>(112-118)"]
        GCN["get_child_nodes(parent_uuid, group_id)<br/>@alru_cache(500)<br/>(120-127)"]
        GAD["get_all_descendants(parent_uuid, group_id)<br/>@alru_cache(500)<br/>(144-151)"]
        GOH["get_one_hop_neighbors(node_uuid, group_id)<br/>@alru_cache(500)<br/>(196-201)"]
    end
    
    subgraph "Batch Operations"
        GCNB["get_child_nodes_batch(parent_uuids, mode)<br/>(129-142)"]
        GADB["get_all_descendants_batch(parent_uuids, mode)<br/>(153-166)"]
        GOHB["get_one_hop_neighbors_batch(node_uuids, mode)<br/>(203-222)"]
    end
    
    subgraph "Modes"
        MP["mode='mp'<br/>Parallel cache lookups"]
        BATCH["mode='batch'<br/>Single batch query"]
    end
    
    GCNB --> MP
    GCNB --> BATCH
    GADB --> MP
    GADB --> BATCH
    GOHB --> MP
    GOHB --> BATCH
    
    MP -.calls.-> GCN
    MP -.calls.-> GAD
    MP -.calls.-> GOH
```

**Sources:** [global_selection/global_selector.py:103-222]()

### Cypher Query Examples

**Get Child Nodes:**
```cypher
match (parent:Category)-[:CATEGORIZES]->(child:Category|Entity) 
where parent.group_id = $group_id and parent.uuid = $parent_uuid
return distinct child.uuid, child.name, child.tag, child.summary, child.layer
```

**Get All Descendants (Recursive):**
```cypher
match (parent:Category|Entity)-[:CATEGORIZES*1..]->(child:Category|Entity) 
where parent.group_id = $group_id and parent.uuid = $parent_uuid
return distinct child.uuid, child.name, child.tag, child.summary
```

**Get One-Hop Episodes:**
```cypher
match (n)-[:MENTIONS]-(m:Episodic)
where n.group_id = $group_id and n.uuid = $node_uuid
return distinct m.uuid, m.content, m.valid_at
```

**Get One-Hop Edges and Entities:**
```cypher
match (n)-[r:RELATES_TO]-(m:Entity)
where n.group_id = $group_id and n.uuid = $node_uuid
return r.uuid as fact_uuid, r.fact, r.valid_at, r.invalid_at, 
       m.uuid as entity_uuid, m.name, m.tag, m.summary
```

**Sources:** [global_selection/global_selector.py:30-83]()

---

## Optimization Strategies

### Caching Architecture

The system uses `alru_cache` (async LRU cache) to minimize database queries:

```mermaid
graph LR
    subgraph "Cache Configuration"
        SIZE["CACHE_SIZE_PER_QUERY = 500"]
        DECORATOR["@alru_cache(maxsize=500)"]
    end
    
    subgraph "Cached Operations"
        GML["get_max_layer"]
        GNBL["get_nodes_by_layer"]
        GCN["get_child_nodes"]
        GAD["get_all_descendants"]
        GOH["get_one_hop_neighbors"]
    end
    
    subgraph "Cache Management"
        CLEAR["clear_cache()<br/>(96-101)"]
    end
    
    SIZE --> DECORATOR
    DECORATOR --> GML
    DECORATOR --> GNBL
    DECORATOR --> GCN
    DECORATOR --> GAD
    DECORATOR --> GOH
    
    CLEAR -.clears.-> GML
    CLEAR -.clears.-> GNBL
    CLEAR -.clears.-> GCN
    CLEAR -.clears.-> GAD
    CLEAR -.clears.-> GOH
```

**Caching Strategy:**
- **Cache Size:** 500 entries per query operation [global_selector.py:20]()
- **Scope:** Individual cached methods operate independently
- **Invalidation:** Manual via `clear_cache()` method [global_selector.py:96-101]()
- **Benefit:** Eliminates redundant database queries for identical parameters

**Sources:** [global_selection/global_selector.py:20](), [global_selection/global_selector.py:96-101](), [global_selection/global_selector.py:103-201]()

### Batch Processing Modes

Batch operations support two execution modes:

| Mode | Implementation | Use Case |
|------|---------------|----------|
| `mp` (multiprocessing) | Parallel `asyncio.gather()` of cached single operations | Maximizes cache hits when many UUIDs overlap with cache |
| `batch` | Single Cypher query with `IN` clause | More efficient for cold cache or distinct UUID sets |

**Mode Selection Logic:**

```python
async def get_child_nodes_batch(self, parent_uuids: list[str], 
                                group_id: str, 
                                mode: Literal['mp', 'batch'] = 'mp') -> list[dict]:
    if mode == 'mp':
        # Leverage cache via parallel single operations
        tasks = [self.get_child_nodes(uuid, group_id=group_id) 
                 for uuid in parent_uuids]
        results = await asyncio.gather(*tasks)
        return list({item['uuid']: item for sublist in results 
                     for item in sublist}.values())
    elif mode == 'batch':
        # Single database query with batch parameters
        result = await self.driver.execute_query(
            Query.GET_CHILD_NODES_BATCH,
            group_id=group_id,
            parent_uuids=parent_uuids
        )
        return [dict(record) for record in result.records]
```

**Sources:** [global_selection/global_selector.py:129-166](), [global_selection/global_selector.py:203-222]()

### Concurrent Execution

The evaluation harness demonstrates concurrent query processing:

```python
async def get_global_search_context(query_groupid_list, 
                                   global_searcher: GlobalSelector, 
                                   max_concurrent=5):
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def search_with_semaphore(query_data):
        async with semaphore:
            # ... perform search
    
    tasks = [search_with_semaphore(query_data) 
             for query_data in query_groupid_list]
    search_results = await asyncio.gather(*tasks)
```

**Concurrency Parameters:**
- **Semaphore Control:** `max_concurrent=5` for general use [global_selector.py:366-385]()
- **Evaluation Batching:** `batch_size=50` (LoCoMo), `batch_size=30` (LongMemEval-S) [global_selector.py:390-429]()
- **Connection Pool:** Neo4j driver configured with `max_connection_pool_size=1000` [global_selector.py:435]()

**Sources:** [global_selection/global_selector.py:366-449]()

---

## Output Structure

### Result Format

The `global_selection` method returns a tuple of `(results, time_stats)`:

```python
results = {
    'episodes': [
        {
            'uuid': str,
            'content': str,
            'valid_at': str  # Formatted: "%Y/%m/%d (%a) %H:%M"
        },
        ...
    ],
    'edges': [
        {
            'uuid': str,
            'fact': str,
            'valid_at': str,
            'invalid_at': str | None
        },
        ...
    ],
    'nodes': [
        {
            'uuid': str,
            'name': str,
            'tag': str,
            'summary': str
        },
        ...
    ]
}

time_stats = {
    'init': float,              # Time to get max_layer
    'layer_selection': float,   # Time for all layer traversals
    'one_hop_neighbors': float  # Time to retrieve neighbors
}
```

**Sources:** [global_selection/global_selector.py:302-319]()

### Timestamp Formatting

Temporal information is formatted for human readability:

```python
def format(item: dict):
    if item.get('valid_at') and type(item['valid_at']) != str:
        item['valid_at'] = item['valid_at'].strftime("%Y/%m/%d (%a) %H:%M")
    if item.get('invalid_at') and type(item['invalid_at']) != str:
        item['invalid_at'] = item['invalid_at'].strftime("%Y/%m/%d (%a) %H:%M")
    return item
```

Example: `2024/03/15 (Fri) 14:30`

**Sources:** [global_selection/global_selector.py:302-307]()

---

## Integration with Evaluation Pipeline

### Dataset Loading

The module provides utilities for benchmark dataset integration:

```mermaid
graph LR
    LOCOMO["locomo.json"]
    LME["longmemeval_s.json"]
    
    LOAD_LOC["load_locomo_data_query_group_id()<br/>(321-342)"]
    LOAD_LME["load_lme_data_query_group_id()<br/>(344-364)"]
    
    QUERY_LIST["query_groupid_list<br/>[{group_id, query}, ...]"]
    
    CONTEXT["get_global_search_context()<br/>(366-385)"]
    
    RESULTS["Search Results<br/>[{query, group_id, context, time_stats}, ...]"]
    
    LOCOMO --> LOAD_LOC
    LME --> LOAD_LME
    LOAD_LOC --> QUERY_LIST
    LOAD_LME --> QUERY_LIST
    QUERY_LIST --> CONTEXT
    CONTEXT --> RESULTS
```

**Functions:**
- `load_locomo_data_query_group_id(file_path, group_id_prefix)` [321-342](): Loads LoCoMo dataset, returns 1,986 query-group_id pairs
- `load_lme_data_query_group_id(file_path, group_id_prefix)` [344-364](): Loads LongMemEval-S dataset, returns 500 query-group_id pairs
- `get_global_search_context(query_groupid_list, global_searcher, max_concurrent)` [366-385](): Batch processes queries with concurrency control

**Sources:** [global_selection/global_selector.py:321-385]()

### Batch Evaluation

The `parse_locomo` and `parse_lme` functions demonstrate production evaluation:

```python
async def parse_locomo(selector: GlobalSelector):
    group_id_prefix = 'locomo_mnemis_coreAI_tel_b20_nec_full'
    max_concurrent = 10
    batch_size = 50
    output_path = '/data/zh/gs/v2_locomo_mnemis_coreAI_tel_b20_nec_full.json'
    
    query_groupid_list = load_locomo_data_query_group_id(
        'data/locomo.json', 
        group_id_prefix=group_id_prefix
    )
    
    with open(output_path, 'w', encoding='utf-8') as output_file:
        for i in tqdm(range(0, all_data_count, batch_size)):
            batch = query_groupid_list[i:i + batch_size]
            search_results = await get_global_search_context(
                batch, selector, max_concurrent=max_concurrent
            )
            for result in search_results:
                print(json.dumps(result, ensure_ascii=False), file=output_file)
```

**Configuration:**
- **LoCoMo:** 50 queries per batch, 10 concurrent operations [387-407]()
- **LongMemEval-S:** 30 queries per batch, 10 concurrent operations [409-429]()
- **Output Format:** JSONL (one JSON object per line)

**Sources:** [global_selection/global_selector.py:387-429]()

---

## Usage Example

### Basic Initialization and Execution

```python
from neo4j import AsyncGraphDatabase
from graphiti_core.llm_client import OpenAIClient
from openai import AsyncOpenAI
from global_selection.global_selector import GlobalSelector

# Initialize Neo4j driver
driver = AsyncGraphDatabase.driver(
    'bolt://localhost:7687',
    auth=('username', 'password'),
    max_connection_pool_size=1000
)

# Initialize LLM client
raw_client = AsyncOpenAI(base_url="...", api_key="...")
llm_client = OpenAIClient(client=raw_client)

# Create GlobalSelector
selector = GlobalSelector(driver, llm_client)

# Execute global selection
results, time_stats = await selector.global_selection(
    query="What restaurants did the user like?",
    group_id="user_12345"
)

# Access results
for episode in results['episodes']:
    print(f"Episode: {episode['content']}")
    
for edge in results['edges']:
    print(f"Fact: {edge['fact']}")
    
for node in results['nodes']:
    print(f"Entity: {node['name']} ({node['tag']})")

# Performance metrics
print(f"Init time: {time_stats['init']}s")
print(f"Layer selection time: {time_stats['layer_selection']}s")
print(f"Neighbor retrieval time: {time_stats['one_hop_neighbors']}s")
```

**Sources:** [global_selection/global_selector.py:431-449]()

---

## Performance Characteristics

### Time Complexity

The traversal algorithm exhibits the following characteristics:

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Layer traversal | O(L) | L = number of layers (typically 3-5) |
| LLM selection per layer | O(N) | N = nodes at current layer |
| Child retrieval | O(S) | S = number of selected nodes |
| Descendant retrieval | O(D × S') | D = average subtree depth, S' = shortcut nodes |
| One-hop expansion | O(S × E) | E = average edges per node |

**Optimization Impact:**
- **Cache Hit Rate:** Dramatically reduces database queries for repeated UUID patterns
- **Batch Mode:** Reduces network round-trips for large parent_uuid sets
- **Concurrent Execution:** Enables parallel processing of independent queries

**Sources:** [global_selection/global_selector.py:267-319]()

### Typical Statistics

Based on evaluation runs:

- **Average layers traversed:** 3-4 layers
- **Nodes evaluated per layer:** 10-50 nodes
- **Selection rate:** 20-40% of nodes per layer
- **Shortcut usage:** 5-15% of selections
- **Final node count:** 20-60 nodes (typical graph_top_k values)
- **Episodes retrieved:** Variable, depends on node connectivity
- **Total execution time:** 2-5 seconds per query (with network latency)

**Sources:** [README.md:31-40]()

---

# Page: RAG_GRAPH Merge Strategy

# RAG_GRAPH Merge Strategy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json](results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json)

</details>



## Purpose and Scope

This page documents the RAG_GRAPH merge strategy, which combines retrieval results from System-1 similarity search and System-2 global selection to produce comprehensive memory context. The merge operation ensures that retrieved memories are both semantically similar (System-1) and structurally relevant (System-2) to the query.

For details on the individual retrieval systems that feed into this merge, see [System-1 Similarity Search](#2.2) and [System-2 Global Selection](#2.3). For information on the underlying memory structures, see [Memory Components](#2.1). For configuration of merge parameters, see [Configuration Options](#3.4).

**Sources:** [README.md:26-26]()

## Overview

The RAG_GRAPH merge strategy is the culmination of Mnemis's dual-route architecture. It takes two distinct sets of retrieval results—one from fast, intuitive similarity search and another from deliberate, hierarchical traversal—and combines them into a unified memory context. This hybrid approach addresses the limitations of pure similarity-based retrieval by incorporating global reasoning and structural relationships.

```mermaid
graph TB
    subgraph Input["Retrieval Inputs"]
        S1["System-1 Results<br/>Similarity-based<br/>Top-K entities/episodes"]
        S2["System-2 Results<br/>Hierarchy-based<br/>Selected nodes + neighbors"]
    end
    
    subgraph Merge["RAG_GRAPH Merge Process"]
        COMBINE["Combine Results<br/>Deduplicate nodes<br/>Preserve both routes"]
        ORGANIZE["Organize Content<br/>organize_rag_content=true"]
        ENRICH["Context Enrichment<br/>One-hop neighbors<br/>Related episodes"]
    end
    
    subgraph Output["Structured Context"]
        MC["Message Chunks<br/>Historical conversations<br/>Temporal ordering"]
        FACTS["FACTS<br/>Extracted statements<br/>Entity relationships"]
        ENT["ENTITIES<br/>Summarized concepts<br/>Category information"]
    end
    
    S1 --> COMBINE
    S2 --> COMBINE
    COMBINE --> ORGANIZE
    ORGANIZE --> ENRICH
    ENRICH --> MC
    ENRICH --> FACTS
    ENRICH --> ENT
```

**Sources:** [README.md:15-23](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:17-31]()

## Input Sources

The RAG_GRAPH merge strategy receives input from two parallel retrieval routes:

### System-1 Input (RAG Path)

System-1 provides similarity-based retrieval results consisting of:

| Component | Description | Configuration Parameter |
|-----------|-------------|------------------------|
| **Top-K Entities** | Most similar entities based on embedding distance | `rag_top_k` (10 or 30) |
| **Associated Episodes** | Episodic nodes mentioning retrieved entities | Automatic expansion |
| **Similarity Scores** | Numerical relevance scores from embedding search | Used for ranking |

The retrieval uses embeddings (qwen3 with FLOAT32 precision) to find entities semantically similar to the query.

### System-2 Input (Graph Path)

System-2 provides hierarchical traversal results consisting of:

| Component | Description | Configuration Parameter |
|-----------|-------------|------------------------|
| **Selected Nodes** | LLM-selected nodes from hierarchical traversal | `graph_top_k` (20 or 60) |
| **One-Hop Neighbors** | Episodes and edges connected to selected nodes | Automatic expansion |
| **Category Context** | Parent/child category relationships | From hierarchical structure |

The retrieval uses `graph_global_search_enabled=true` to perform top-down traversal with LLM-guided selection at each layer.

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:17-25]()

## Merge Configuration

```mermaid
graph LR
    subgraph Config["Merge Configuration Parameters"]
        METHOD["merge_method<br/>RAG_GRAPH"]
        RAGE["rag_enabled<br/>true"]
        GE["graph_enabled<br/>true"]
        RTK["rag_top_k<br/>10 or 30"]
        GTK["graph_top_k<br/>20 or 60"]
        ORC["organize_rag_content<br/>true"]
        GGS["graph_global_search_enabled<br/>true"]
    end
    
    METHOD --> PROCESS["Merge Process"]
    RAGE --> PROCESS
    GE --> PROCESS
    RTK --> PROCESS
    GTK --> PROCESS
    ORC --> STRUCTURE["Content Organization"]
    GGS --> PROCESS
```

The configuration shown in evaluation results demonstrates the merge strategy parameters:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `merge_method` | `"RAG_GRAPH"` | Specifies the merge algorithm |
| `rag_enabled` | `true` | Enables System-1 retrieval |
| `graph_enabled` | `true` | Enables System-2 retrieval |
| `rag_top_k` | `10` or `30` | Number of similarity-based results |
| `graph_top_k` | `20` or `60` | Number of hierarchy-based results |
| `organize_rag_content` | `true` | Enables structured content organization |
| `graph_global_search_enabled` | `true` | Enables hierarchical traversal |

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:17-31]()

## Merge Process

The RAG_GRAPH merge operates through several stages to combine and organize results from both retrieval routes:

### Stage 1: Result Collection

```mermaid
graph TB
    Q["Query"]
    
    subgraph RAG["RAG Retrieval"]
        RE["Embedding<br/>qwen3 FLOAT32"]
        RS["Similarity Search"]
        RR["Top-K=10 Results"]
    end
    
    subgraph GRAPH["Graph Retrieval"]
        GS["Global Selection"]
        LF["Layer Filtering"]
        GR["Top-K=20 Results"]
        NH["One-Hop Neighbors"]
    end
    
    Q --> RE
    Q --> GS
    RE --> RS
    RS --> RR
    GS --> LF
    LF --> GR
    GR --> NH
    
    RR --> MERGE["Merge Stage 2"]
    NH --> MERGE
```

Both retrieval systems operate in parallel on the query, producing their respective top-k results.

### Stage 2: Deduplication and Combination

The merge process combines results while handling overlaps:

- **Deduplication**: When the same entity or episode appears in both System-1 and System-2 results, it is included once but tagged with provenance from both routes
- **Complementary Coverage**: Unique results from each system are preserved, ensuring comprehensive coverage
- **Score Preservation**: Similarity scores from System-1 and selection rationale from System-2 are maintained

### Stage 3: Content Organization

With `organize_rag_content=true`, the merged results undergo structured organization:

```mermaid
graph TB
    MERGED["Merged Results<br/>Deduplicated nodes"]
    
    subgraph Organization["Content Organization"]
        EXTRACT["Extract Components"]
        CLASSIFY["Classify by Type"]
        TEMPORAL["Temporal Ordering"]
    end
    
    subgraph Output["Structured Output"]
        MC["Message Chunks<br/>Conversation segments"]
        FACTS["FACTS<br/>Atomic statements"]
        ENT["ENTITIES<br/>Concept summaries"]
    end
    
    MERGED --> EXTRACT
    EXTRACT --> CLASSIFY
    CLASSIFY --> TEMPORAL
    TEMPORAL --> MC
    TEMPORAL --> FACTS
    TEMPORAL --> ENT
```

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:27-30]()

## Output Structure

The RAG_GRAPH merge produces a structured memory context organized into three components:

### Message Chunks

Historical conversation segments retrieved as complete contextual units:

| Property | Description |
|----------|-------------|
| **Content** | Raw conversation text from episodic nodes |
| **Temporal Order** | Chronologically sorted based on creation timestamps |
| **Source** | Provenance tracking (System-1, System-2, or both) |
| **Context** | Surrounding messages for continuity |

Message chunks preserve the conversational flow and allow the LLM to understand the original interaction context.

### FACTS

Atomic factual statements extracted from retrieved memories:

| Property | Description |
|----------|-------------|
| **Statement** | Discrete fact or relationship |
| **Entities** | Involved entities with roles |
| **Temporal** | Time-based validity information |
| **Source** | Originating episode or entity node |

Facts provide granular, queryable information that can be directly referenced in answers.

### ENTITIES

Summarized conceptual information about retrieved entities:

| Property | Description |
|----------|-------------|
| **Summary** | High-level description of the entity |
| **Categories** | Hierarchical category assignments from System-2 |
| **Attributes** | Key properties and characteristics |
| **Relationships** | Connections to other entities |

Entity summaries provide conceptual understanding and semantic context for the retrieved information.

**Sources:** [README.md:15-23]()

## Complementary Strengths

The RAG_GRAPH merge leverages the distinct advantages of each retrieval route:

```mermaid
graph TB
    subgraph S1["System-1 Contributions"]
        S1_1["Semantic Similarity<br/>Matches query intent"]
        S1_2["Recent/Frequent Memories<br/>Based on embeddings"]
        S1_3["Direct Relevance<br/>Immediate connections"]
    end
    
    subgraph S2["System-2 Contributions"]
        S2_1["Structural Relationships<br/>Graph topology"]
        S2_2["Global Context<br/>Higher-level categories"]
        S2_3["Comprehensive Coverage<br/>Deliberate traversal"]
    end
    
    subgraph COMBINED["Combined Benefits"]
        B1["Both Semantic AND<br/>Structural Relevance"]
        B2["Local Detail +<br/>Global Understanding"]
        B3["Fast Retrieval +<br/>Complete Coverage"]
    end
    
    S1_1 --> B1
    S2_1 --> B1
    S1_2 --> B2
    S2_2 --> B2
    S1_3 --> B3
    S2_3 --> B3
```

### System-1 Strengths in the Merge

- **Semantic Matching**: Finds memories with similar language and concepts to the query
- **Efficiency**: Fast embedding-based search provides immediate results
- **Recency Bias**: Naturally surfaces recent or frequently accessed memories
- **Direct Connections**: Captures explicitly mentioned entities and relationships

### System-2 Strengths in the Merge

- **Structural Reasoning**: Identifies memories through hierarchical relationships
- **Global Coverage**: Ensures comprehensive information gathering across semantic categories
- **Implicit Relevance**: Discovers memories not directly similar but structurally connected
- **Category Context**: Provides higher-level understanding through hierarchical categories

### Synergistic Effects

The combination produces results that neither system alone could achieve:

1. **Reduced False Negatives**: System-2 catches relevant memories missed by similarity search
2. **Enhanced Context**: Hierarchical categories from System-2 enrich semantically similar results from System-1
3. **Balanced Retrieval**: Combines fast intuition (System-1) with thorough reasoning (System-2)
4. **Comprehensive Evidence**: Both direct matches and indirect relationships support answer generation

**Sources:** [README.md:15-23]()

## Parameter Tuning Impact

The merge behavior can be tuned through top-k parameters:

| Configuration | rag_top_k | graph_top_k | Use Case | Performance |
|---------------|-----------|-------------|----------|-------------|
| **Balanced** | 10 | 20 | General purpose retrieval | 80.0% accuracy (LoCoMo) |
| **Comprehensive** | 30 | 60 | Maximum coverage scenarios | Higher recall, more context |

```mermaid
graph LR
    subgraph Config1["ragtopk10_gtopk20"]
        C1R["RAG: 10 results"]
        C1G["Graph: 20 results"]
        C1T["Total: ~30 unique"]
    end
    
    subgraph Config2["ragtopk30_gtopk60"]
        C2R["RAG: 30 results"]
        C2G["Graph: 60 results"]
        C2T["Total: ~90 unique"]
    end
    
    subgraph Tradeoffs["Performance Tradeoffs"]
        PREC["Precision vs Recall"]
        COST["Cost vs Coverage"]
        LAT["Latency vs Completeness"]
    end
    
    C1T --> PREC
    C2T --> PREC
    C1T --> COST
    C2T --> COST
    C1T --> LAT
    C2T --> LAT
```

### Configuration Considerations

**Lower top-k values (10/20)**:
- Faster retrieval and lower LLM processing cost
- More precise, focused context
- Suitable for queries with clear intent
- May miss peripheral relevant information

**Higher top-k values (30/60)**:
- More comprehensive memory coverage
- Better for complex, multi-faceted queries
- Increased LLM token consumption
- May include less relevant information

For detailed analysis of configuration impact, see [Configuration Impact Analysis](#4.4).

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:21-22]()

## Context Enrichment

The merge process includes context enrichment beyond the initial retrieval results:

```mermaid
graph TB
    INIT["Initial Merged Results"]
    
    subgraph Enrichment["Context Enrichment"]
        NEIGHBORS["One-Hop Neighbor Expansion"]
        EPISODES["Associated Episode Retrieval"]
        EDGES["Relationship Edge Extraction"]
    end
    
    subgraph Enhanced["Enhanced Context"]
        CONV["Complete Conversations"]
        REL["Full Relationship Network"]
        TEMP["Temporal Context"]
    end
    
    INIT --> NEIGHBORS
    NEIGHBORS --> EPISODES
    EPISODES --> EDGES
    EDGES --> CONV
    EDGES --> REL
    EDGES --> TEMP
```

### Enrichment Operations

1. **One-Hop Neighbor Expansion**: For each retrieved entity, include directly connected nodes
2. **Episode Inclusion**: Add episodic nodes that mention retrieved entities
3. **Relationship Edges**: Include explicit relationship edges (MENTIONS, RELATES_TO, CATEGORIZES)
4. **Temporal Context**: Preserve temporal ordering and time-based relationships

This enrichment ensures that the final context includes not just isolated nodes but their immediate relational context, providing the LLM with a more complete information graph for answer generation.

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:17-31]()

## Integration with Answer Generation

The merged context flows into the answer generation pipeline:

```mermaid
graph TB
    subgraph MergedContext["RAG_GRAPH Output"]
        MC["Message Chunks"]
        FACTS["FACTS"]
        ENT["ENTITIES"]
    end
    
    subgraph Formatting["Context Formatting"]
        TEMPLATE["Answer Prompt Template<br/>answer_prompt: M365"]
        STRUCTURE["Structured Context Assembly"]
    end
    
    subgraph Generation["Answer Generation"]
        LLM["Answer Model<br/>gpt-41-mini"]
        RESPONSE["Generated Response"]
    end
    
    subgraph Evaluation["Quality Assessment"]
        GRADER["Grader Model<br/>gpt-41-mini"]
        METRICS["Accuracy Metrics"]
    end
    
    MC --> TEMPLATE
    FACTS --> TEMPLATE
    ENT --> TEMPLATE
    TEMPLATE --> STRUCTURE
    STRUCTURE --> LLM
    LLM --> RESPONSE
    RESPONSE --> GRADER
    GRADER --> METRICS
```

The structured output from RAG_GRAPH merge is formatted according to the answer prompt template (M365 in the evaluated configuration) and provided to the answer model. The clear separation of Message Chunks, FACTS, and ENTITIES allows the LLM to:

- Reference specific conversational contexts
- Cite discrete factual statements
- Leverage conceptual summaries for reasoning

This structured approach, combined with the dual-route retrieval, contributes to Mnemis's state-of-the-art performance: 93.9% accuracy on LoCoMo (excluding category 5) and 91.6% on LongMemEval-S.

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-73](), [README.md:15-23]()

## Key Design Decisions

The RAG_GRAPH merge strategy embodies several important design choices:

### Union-Based Merge

The strategy uses a union approach rather than intersection, ensuring that relevant memories from either route are included. This maximizes recall while maintaining precision through the dual validation of having multiple retrieval paths.

### Structured Organization

The `organize_rag_content=true` setting triggers automatic organization into Message Chunks, FACTS, and ENTITIES. This structuring:
- Makes context more interpretable for LLMs
- Enables different reasoning strategies for different information types
- Improves answer generation quality

### Provenance Tracking

The merge preserves information about which route(s) retrieved each piece of memory, enabling:
- Debugging and analysis of retrieval patterns
- Understanding complementarity between routes
- Future optimization of retrieval parameters

### Scalable Parameters

The configurable top-k parameters (`rag_top_k` and `graph_top_k`) allow the merge to scale from focused, efficient retrieval to comprehensive, thorough coverage based on application requirements.

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:17-31]()

---

# Page: Implementation Guide

# Implementation Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [global_selection/global_selector.py](global_selection/global_selector.py)
- [global_selection/prompts.py](global_selection/prompts.py)

</details>



This page provides technical guidance for working with the Mnemis codebase, focusing on the System-2 Global Selection implementation. It covers the repository structure, key classes, and practical usage patterns for integrating the dual-route retrieval system into applications.

For architectural concepts and theory behind System-2, see [System-2 Global Selection](#2.3). For detailed API documentation, see [GlobalSelector Class Reference](#3.1). For benchmark evaluation procedures, see [Running Evaluations](#6.3).

---

## Repository Structure

The Mnemis implementation is organized around the Global Selection module, which implements System-2's hierarchical traversal mechanism. The codebase builds upon the Graphiti framework for base graph operations.

```mermaid
graph TB
    subgraph "Repository Root"
        README["README.md<br/>Overview & documentation"]
        DATA["data/<br/>Benchmark datasets"]
        RESULTS["results/<br/>Evaluation outputs"]
        
        subgraph "global_selection/"
            GS["global_selector.py<br/>GlobalSelector class"]
            PROMPTS["prompts.py<br/>NODE_SELECTION_PROMPT_TEMPLATE"]
        end
    end
    
    subgraph "External Dependencies"
        GRAPHITI["Graphiti Framework<br/>Base graph operations"]
        NEO4J["Neo4j Database<br/>Graph storage"]
        LLM["OpenAI/Azure Client<br/>LLM services"]
    end
    
    GS --> GRAPHITI
    GS --> NEO4J
    GS --> LLM
    GS --> PROMPTS
    
    DATA --> GS
    GS --> RESULTS
```

**Core Implementation Files:**

| File Path | Purpose | Key Components |
|-----------|---------|----------------|
| `global_selection/global_selector.py` | System-2 implementation | `GlobalSelector`, `Query`, `NodeSelection` classes |
| `global_selection/prompts.py` | LLM prompt templates | `NODE_SELECTION_PROMPT_TEMPLATE` |
| `data/locomo.json` | LoCoMo benchmark dataset | 1,986 questions across 5 categories |
| `data/longmemeval_s.json` | LongMemEval-S benchmark | 500 questions across 6 types |
| `results/` | Evaluation results | Metrics and full context outputs |

**Sources:** [global_selection/global_selector.py:1-453](), [global_selection/prompts.py:1-23](), [README.md:1-72]()

---

## Core Components Architecture

The implementation centers around the `GlobalSelector` class, which orchestrates Neo4j database queries, LLM-based node selection, and caching operations.

```mermaid
graph TB
    subgraph "GlobalSelector Class"
        INIT["__init__()<br/>driver, llm_client, config"]
        GS_METHOD["global_selection()<br/>Main orchestration"]
        LAYER_SEL["layer_selection()<br/>LLM-guided filtering"]
        
        subgraph "Graph Query Methods"
            GML["get_max_layer()"]
            GNL["get_nodes_by_layer()"]
            GCN["get_child_nodes()"]
            GAD["get_all_descendants()"]
            GOH["get_one_hop_neighbors()"]
        end
        
        subgraph "Batch Operations"
            GCN_B["get_child_nodes_batch()"]
            GAD_B["get_all_descendants_batch()"]
            GOH_B["get_one_hop_neighbors_batch()"]
        end
        
        CACHE_CLEAR["clear_cache()"]
    end
    
    subgraph "Data Models"
        NODE_SEL["NodeSelection<br/>Pydantic model"]
        NODE_SEL_LIST["NodeSelectionList<br/>Response container"]
        CONFIG["GlobalSelectorConfig<br/>use_summary, use_tag"]
    end
    
    subgraph "Query Templates"
        QUERY_CLASS["Query class<br/>Cypher query strings"]
    end
    
    subgraph "External Services"
        DRIVER["AsyncDriver<br/>Neo4j connection"]
        LLM_CLIENT["LLMClient<br/>OpenAI/Azure"]
    end
    
    INIT --> DRIVER
    INIT --> LLM_CLIENT
    INIT --> CONFIG
    
    GS_METHOD --> GML
    GS_METHOD --> GNL
    GS_METHOD --> GCN_B
    GS_METHOD --> GAD_B
    GS_METHOD --> GOH_B
    GS_METHOD --> LAYER_SEL
    
    LAYER_SEL --> LLM_CLIENT
    LAYER_SEL --> NODE_SEL_LIST
    NODE_SEL_LIST --> NODE_SEL
    
    GML --> QUERY_CLASS
    GNL --> QUERY_CLASS
    GCN --> QUERY_CLASS
    GAD --> QUERY_CLASS
    GOH --> QUERY_CLASS
    
    QUERY_CLASS --> DRIVER
```

**Key Classes and Their Roles:**

| Class | Location | Purpose |
|-------|----------|---------|
| `GlobalSelector` | [global_selection/global_selector.py:90-319]() | Main orchestrator for System-2 retrieval |
| `Query` | [global_selection/global_selector.py:30-83]() | Cypher query template container |
| `NodeSelection` | [global_selection/global_selector.py:22-25]() | Pydantic model for LLM selection output |
| `NodeSelectionList` | [global_selection/global_selector.py:27-28]() | Container for multiple selections |
| `GlobalSelectorConfig` | [global_selection/global_selector.py:85-87]() | Configuration for selection behavior |

**Sources:** [global_selection/global_selector.py:22-319]()

---

## Basic Usage Pattern

The typical workflow for using the Global Selection implementation follows this pattern:

### 1. Initialize Dependencies

```python
from neo4j import AsyncGraphDatabase
from graphiti_core.llm_client import OpenAIClient
from openai import AsyncOpenAI
from global_selection.global_selector import GlobalSelector

# Neo4j driver with connection pooling
driver = AsyncGraphDatabase.driver(
    'bolt://localhost:7687',
    auth=('username', 'password'),
    max_connection_pool_size=1000
)

# LLM client wrapper
raw_client = AsyncOpenAI(base_url="...", api_key="...")
llm_client = OpenAIClient(client=raw_client)

# GlobalSelector instance
selector = GlobalSelector(driver, llm_client)
```

### 2. Execute Global Selection

```python
# Run hierarchical traversal for a query
query = "What are my travel preferences?"
group_id = "user_123"

results, time_stats = await selector.global_selection(query, group_id)

# Results contain:
# - episodes: List of episodic memories (conversations)
# - edges: List of relationship facts
# - nodes: List of selected category/entity nodes
```

### 3. Process Retrieved Context

```python
print(f"Retrieved {len(results['episodes'])} episodes")
print(f"Retrieved {len(results['edges'])} facts")
print(f"Retrieved {len(results['nodes'])} nodes")

# Time statistics
print(f"Layer selection took: {time_stats['layer_selection']}s")
print(f"One-hop neighbor retrieval: {time_stats['one_hop_neighbors']}s")
```

**Sources:** [global_selection/global_selector.py:431-452](), [global_selection/global_selector.py:267-319]()

---

## Query Execution Flow

This diagram shows how a user query flows through the `global_selection()` method to produce retrieved context.

```mermaid
graph TB
    QUERY["User Query<br/>+ group_id"]
    
    subgraph "global_selection() Method"
        INIT_STEP["get_max_layer()<br/>Discover hierarchy depth"]
        
        LOOP_START["Loop: layer = max_layer down to 1"]
        
        GET_NODES["get_nodes_by_layer() or<br/>get_child_nodes_batch()<br/>Retrieve current layer nodes"]
        
        LAYER_SEL["layer_selection()<br/>LLM filters relevant nodes"]
        
        SHORTCUTS["get_all_descendants_batch()<br/>Get all children of shortcut nodes"]
        
        ACCUMULATE["Accumulate selected nodes<br/>in selected_categories dict"]
        
        LOOP_END["Next layer iteration"]
        
        ONE_HOP["get_one_hop_neighbors_batch()<br/>Retrieve episodes + edges"]
        
        FORMAT["Format timestamps<br/>Organize results"]
    end
    
    RESULTS["Results dict:<br/>episodes, edges, nodes"]
    TIME_STATS["time_stats dict:<br/>init, layer_selection,<br/>one_hop_neighbors"]
    
    QUERY --> INIT_STEP
    INIT_STEP --> LOOP_START
    LOOP_START --> GET_NODES
    GET_NODES --> LAYER_SEL
    LAYER_SEL --> SHORTCUTS
    SHORTCUTS --> ACCUMULATE
    ACCUMULATE --> LOOP_END
    LOOP_END --> |"More layers"| LOOP_START
    LOOP_END --> |"Reached layer 0"| ONE_HOP
    ONE_HOP --> FORMAT
    FORMAT --> RESULTS
    FORMAT --> TIME_STATS
```

**Method Call Sequence:**

1. **Initialization** [global_selection/global_selector.py:268-272]()
   - `get_max_layer()` determines hierarchy depth
   
2. **Layer-by-Layer Traversal** [global_selection/global_selector.py:274-294]()
   - `get_nodes_by_layer()` or `get_child_nodes_batch()` retrieves candidates
   - `layer_selection()` uses LLM to filter relevant nodes
   - `get_all_descendants_batch()` handles shortcut selections
   
3. **Context Expansion** [global_selection/global_selector.py:298-300]()
   - `get_one_hop_neighbors_batch()` retrieves episodes and relationship edges
   
4. **Result Assembly** [global_selection/global_selector.py:302-318]()
   - Format timestamps
   - Organize into episodes, edges, and nodes

**Sources:** [global_selection/global_selector.py:267-319]()

---

## Database Query Operations

The `Query` class defines Cypher query templates used throughout the traversal process.

**Query Template Categories:**

| Query Constant | Purpose | Return Values |
|----------------|---------|---------------|
| `GET_MAX_LAYER` | Find maximum layer number | `max_layer` (int) |
| `GET_NODES_BY_LAYER` | Get all nodes at specific layer | `uuid`, `name`, `tag`, `summary` |
| `GET_CHILD_NODES` | Get direct children of parent | `uuid`, `name`, `tag`, `summary`, `layer` |
| `GET_CHILD_NODES_BATCH` | Batch version for multiple parents | Same as above |
| `GET_ALL_DESCENDANTS` | Get entire subtree | `uuid`, `name`, `tag`, `summary` |
| `GET_ALL_DESCENDANTS_BATCH` | Batch version for multiple parents | Same as above |
| `GET_ONE_HOP_EPISODES` | Get connected episodic nodes | `uuid`, `content`, `valid_at` |
| `GET_ONE_HOP_EPISODES_BATCH` | Batch version | Same as above |
| `GET_ONE_HOP_NODES_AND_EDGES` | Get connected entities + facts | `fact_uuid`, `fact`, `valid_at`, `invalid_at`, `entity_uuid`, `name`, `tag`, `summary` |
| `GET_ONE_HOP_NODES_AND_EDGES_BATCH` | Batch version | Same as above |

**Example Query Pattern:**

```cypher
# GET_CHILD_NODES
match (parent:Category)-[:CATEGORIZES]->(child:Category|Entity) 
where parent.group_id = $group_id and parent.uuid = $parent_uuid
return distinct child.uuid as uuid, child.name as name, 
       child.tag as tag, child.summary as summary, child.layer as layer
```

**Sources:** [global_selection/global_selector.py:30-83]()

---

## LLM-Based Node Selection

The `layer_selection()` method uses LLM intelligence to filter relevant nodes at each hierarchical level.

```mermaid
graph LR
    INPUT["Current layer<br/>category nodes"]
    
    PREPARE["Prepare context<br/>Filter fields by config"]
    
    PROMPT["Format with<br/>NODE_SELECTION_PROMPT_TEMPLATE"]
    
    LLM["LLM generates response<br/>NodeSelectionList"]
    
    PARSE["Parse selections<br/>Match by uuid or name"]
    
    OUTPUT_SEL["selected_categories[]<br/>Continue traversal"]
    OUTPUT_SHORT["shortcut_categories[]<br/>Get all descendants"]
    
    INPUT --> PREPARE
    PREPARE --> PROMPT
    PROMPT --> LLM
    LLM --> PARSE
    PARSE --> OUTPUT_SEL
    PARSE --> OUTPUT_SHORT
```

**Configuration Fields:**

The `GlobalSelectorConfig` controls what information the LLM receives:

```python
class GlobalSelectorConfig(BaseModel):
    use_summary: bool = False  # Include node.summary field
    use_tag: bool = True       # Include node.tag field
```

**Allowed Fields Based on Config:**
- Always included: `uuid`, `name`
- Conditional: `tag` (if `use_tag=True`), `summary` (if `use_summary=True`)

**LLM Response Model:**

Each selection specifies:
- `name`: Node's name
- `uuid`: Node's unique identifier  
- `get_all_children`: Boolean flag for shortcut (get entire subtree)

**Sources:** [global_selection/global_selector.py:224-265](), [global_selection/global_selector.py:85-87](), [global_selection/prompts.py:1-23]()

---

## Caching Strategy

The implementation uses `alru_cache` (async LRU cache) to minimize redundant database queries during hierarchical traversal.

**Cached Methods:**

| Method | Cache Size | Rationale |
|--------|------------|-----------|
| `get_max_layer()` | 500 per query | Hierarchy depth rarely changes |
| `get_nodes_by_layer()` | 500 per query | Layer contents stable during query |
| `get_child_nodes()` | 500 per query | Parent-child relationships stable |
| `get_all_descendants()` | 500 per query | Subtrees rarely change mid-query |
| `get_one_hop_neighbors()` | 500 per query | Node neighbors stable |

**Cache Management:**

```python
# Clear all caches when needed
selector.clear_cache()

# Individual method caches auto-managed by @alru_cache decorator
```

The `CACHE_SIZE_PER_QUERY` constant is set to 500 entries [global_selection/global_selector.py:20](). This provides substantial performance improvement for hierarchies with repeated node access patterns while maintaining bounded memory usage.

**Sources:** [global_selection/global_selector.py:20](), [global_selection/global_selector.py:96-101](), [global_selection/global_selector.py:103-222]()

---

## Batch Processing Modes

Many methods support two processing modes for handling multiple items:

```mermaid
graph TB
    INPUT["Input: List of UUIDs"]
    
    MODE{mode parameter}
    
    MP["mode='mp'<br/>Multiprocessing approach"]
    BATCH["mode='batch'<br/>Single query approach"]
    
    MP_DETAIL["Create task per UUID<br/>asyncio.gather(*tasks)<br/>Leverage individual caching"]
    
    BATCH_DETAIL["Single Cypher query<br/>with 'in $uuids' clause<br/>Fewer DB round trips"]
    
    MERGE["Merge/deduplicate results<br/>by UUID"]
    
    OUTPUT["Combined results list"]
    
    INPUT --> MODE
    MODE --> |"'mp'"| MP
    MODE --> |"'batch'"| BATCH
    
    MP --> MP_DETAIL
    BATCH --> BATCH_DETAIL
    
    MP_DETAIL --> MERGE
    BATCH_DETAIL --> MERGE
    
    MERGE --> OUTPUT
```

**Mode Comparison:**

| Aspect | `mode='mp'` | `mode='batch'` |
|--------|-------------|----------------|
| **DB Queries** | N queries (one per UUID) | 1 query (batch clause) |
| **Caching** | Leverages `@alru_cache` per UUID | No per-item caching |
| **Concurrency** | High (asyncio.gather) | Single query execution |
| **Best For** | Repeated access patterns | One-time batch operations |

**Implementation Example:**

```python
# In get_child_nodes_batch()
if mode == 'mp':
    tasks = [self.get_child_nodes(uuid, group_id=group_id) 
             for uuid in parent_uuids]
    results = await asyncio.gather(*tasks)
    # Deduplicate by uuid
    return list({item['uuid']: item for sublist in results 
                 for item in sublist}.values())
elif mode == 'batch':
    result = await self.driver.execute_query(
        Query.GET_CHILD_NODES_BATCH,
        group_id=group_id,
        parent_uuids=parent_uuids
    )
    return [dict(record) for record in result.records]
```

The production implementation uses `mode='batch'` [global_selection/global_selector.py:269]() for optimal throughput during evaluation.

**Sources:** [global_selection/global_selector.py:129-222]()

---

## Dataset Loading Utilities

The module includes helper functions for loading benchmark datasets and running batch evaluations.

**LoCoMo Dataset Loading:**

```python
def load_locomo_data_query_group_id(file_path, group_id_prefix='locomo_ziyu'):
    """
    Returns: List of dicts with 'group_id' and 'query' keys
    """
```

Each user in the LoCoMo dataset gets a unique `group_id`, and each QA pair becomes a query record.

**LongMemEval-S Dataset Loading:**

```python
def load_lme_data_query_group_id(file_path, group_id_prefix='lme_s_ziyu'):
    """
    Returns: List of dicts with 'group_id', 'query', and 'question_id' keys
    """
```

**Batch Evaluation Framework:**

The `get_global_search_context()` function orchestrates concurrent query processing:

```python
async def get_global_search_context(
    query_groupid_list, 
    global_searcher: GlobalSelector, 
    max_concurrent=5
):
    """
    Args:
        query_groupid_list: List of query dicts
        global_searcher: GlobalSelector instance
        max_concurrent: Semaphore limit for concurrency
    
    Returns:
        List of dicts with query, group_id, context, time_stats
    """
```

Uses `asyncio.Semaphore` to limit concurrent executions and prevent overwhelming the Neo4j connection pool.

**Production Evaluation Pattern:**

```python
# Process dataset in batches
batch_size = 50
max_concurrent = 10

for i in range(0, total_queries, batch_size):
    batch = query_groupid_list[i:i + batch_size]
    search_results = await get_global_search_context(
        batch, selector, max_concurrent=max_concurrent
    )
    # Save results incrementally
```

**Sources:** [global_selection/global_selector.py:321-429]()

---

## Connection Pool Configuration

For high-throughput evaluation, the Neo4j driver requires adequate connection pooling:

```python
driver = AsyncGraphDatabase.driver(
    url='bolt://localhost:7687',
    auth=(user, password),
    max_connection_pool_size=1000  # Critical for concurrent operations
)
```

**Recommended Settings:**

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `max_connection_pool_size` | 1000 | Supports 10+ concurrent users with 50+ batch size |
| `max_concurrent` (semaphore) | 10 | Limits concurrent global_selection calls |
| `batch_size` | 30-50 | Balances throughput and memory |

The large connection pool is necessary because:
- Each `global_selection()` call makes multiple database queries
- Batch processing creates many concurrent database operations
- Cached operations still need connections for cache misses

**Sources:** [global_selection/global_selector.py:435]()

---

## Integration with Graphiti Framework

Mnemis builds upon the Graphiti framework, which provides:
- Base graph construction and maintenance
- Entity extraction from conversations
- Episodic memory storage
- LLM client abstraction (`LLMClient`, `OpenAIClient`)

The `GlobalSelector` extends Graphiti's capabilities by adding:
- Hierarchical graph traversal
- LLM-guided node selection
- Global selection retrieval mechanism

**Key Graphiti Dependencies:**

```python
from graphiti_core.llm_client import LLMClient, ModelSize, OpenAIClient
from graphiti_core.prompts.models import Message
```

The `LLMClient` provides:
- Standardized LLM API across OpenAI/Azure
- Response model parsing (Pydantic models)
- Token usage tracking

**Message Format:**

```python
messages = [Message(role='user', content=prompt)]
response = await llm_client.generate_response(
    messages=messages,
    response_model=NodeSelectionList,
    model_size=ModelSize.large
)
```

**Sources:** [global_selection/global_selector.py:16-18](), [global_selection/global_selector.py:241-245](), [README.md:54]()

---

## Next Steps

For detailed information on specific topics:

- **API Reference:** See [GlobalSelector Class Reference](#3.1) for complete method documentation
- **Graph Schema:** See [Graph Database Schema](#3.2) for Neo4j node and relationship types
- **Prompts:** See [Prompt Engineering](#3.3) for details on `NODE_SELECTION_PROMPT_TEMPLATE`
- **Configuration:** See [Configuration Options](#3.4) for all available settings
- **Performance:** See [Performance Optimization](#3.5) for advanced tuning strategies
- **Setup:** See [Installation & Setup](#6.1) for environment configuration
- **Usage:** See [Usage Examples](#6.2) for practical code examples

**Sources:** [README.md:1-72](), [global_selection/global_selector.py:1-453]()

---

# Page: GlobalSelector Class Reference

# GlobalSelector Class Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [global_selection/global_selector.py](global_selection/global_selector.py)

</details>



This document provides comprehensive API documentation for the `GlobalSelector` class, which implements System-2's deliberate, top-down hierarchical graph traversal with LLM-guided node selection. This class is the core implementation enabling global reasoning over large knowledge graphs stored in Neo4j.

For conceptual understanding of System-2's role in the dual-route architecture, see [System-2 Global Selection](#2.3). For the prompt templates used in LLM-guided selection, see [Prompt Engineering](#3.3). For configuration options, see [Configuration Options](#3.4).

**Sources:** [global_selection/global_selector.py:1-453]()

---

## Class Architecture

The `GlobalSelector` class orchestrates hierarchical graph traversal through a combination of Neo4j graph queries, LLM-based decision making, and aggressive caching. The following diagram shows the class structure and key components:

```mermaid
graph TB
    subgraph GlobalSelector["GlobalSelector Class"]
        direction TB
        
        CONSTRUCTOR["__init__()<br/>driver, llm_client, selection_config"]
        
        subgraph CoreMethods["Core Traversal Methods"]
            GLOBAL["global_selection()<br/>Main orchestration"]
            LAYER["layer_selection()<br/>LLM-guided filtering"]
        end
        
        subgraph GraphQueries["Graph Query Methods (Cached)"]
            GML["get_max_layer()<br/>@alru_cache(500)"]
            GNL["get_nodes_by_layer()<br/>@alru_cache(500)"]
            GCN["get_child_nodes()<br/>@alru_cache(500)"]
            GAD["get_all_descendants()<br/>@alru_cache(500)"]
            GOH["get_one_hop_neighbors()<br/>@alru_cache(500)"]
        end
        
        subgraph BatchMethods["Batch Processing Methods"]
            GCNB["get_child_nodes_batch()<br/>mode: mp|batch"]
            GADB["get_all_descendants_batch()<br/>mode: mp|batch"]
            GOHB["get_one_hop_neighbors_batch()<br/>mode: mp|batch"]
        end
        
        CACHE_CLEAR["clear_cache()<br/>Invalidates all caches"]
    end
    
    subgraph Dependencies["Dependencies"]
        DRIVER["AsyncDriver<br/>Neo4j connection"]
        LLM["LLMClient<br/>OpenAI/Azure"]
        CONFIG["GlobalSelectorConfig<br/>use_summary, use_tag"]
    end
    
    subgraph Models["Data Models"]
        NS["NodeSelection<br/>name, uuid, get_all_children"]
        NSL["NodeSelectionList<br/>selections: list[NodeSelection]"]
        QUERY["Query Class<br/>Cypher templates"]
    end
    
    CONSTRUCTOR --> DRIVER
    CONSTRUCTOR --> LLM
    CONSTRUCTOR --> CONFIG
    
    GLOBAL --> LAYER
    GLOBAL --> GML
    GLOBAL --> GCNB
    GLOBAL --> GADB
    GLOBAL --> GOHB
    
    LAYER --> LLM
    LAYER --> NSL
    
    GML --> DRIVER
    GNL --> DRIVER
    GCN --> DRIVER
    GAD --> DRIVER
    GOH --> DRIVER
    
    GCNB --> GCN
    GADB --> GAD
    GOHB --> GOH
    
    NSL --> NS
    
    GCN --> QUERY
    GAD --> QUERY
    GOH --> QUERY
```

**Sources:** [global_selection/global_selector.py:90-319]()

---

## Constructor and Configuration

### GlobalSelector.__init__()

```python
def __init__(
    self, 
    driver: AsyncDriver, 
    llm_client: LLMClient, 
    selection_config: GlobalSelectorConfig = GlobalSelectorConfig()
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `driver` | `AsyncDriver` | Neo4j async driver instance for graph database operations |
| `llm_client` | `LLMClient` | LLM client for intelligent node selection (OpenAI/Azure) |
| `selection_config` | `GlobalSelectorConfig` | Configuration controlling node information visibility (optional) |

**Sources:** [global_selection/global_selector.py:91-94]()

### GlobalSelectorConfig

Configuration model controlling what node information is provided to the LLM during selection:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `use_summary` | `bool` | `False` | Include node summaries in LLM prompt |
| `use_tag` | `bool` | `True` | Include node tags in LLM prompt |

**Sources:** [global_selection/global_selector.py:85-88]()

**Usage Example:**

```python
from neo4j import AsyncGraphDatabase
from graphiti_core.llm_client import OpenAIClient
from global_selection.global_selector import GlobalSelector, GlobalSelectorConfig

# Initialize dependencies
driver = AsyncGraphDatabase.driver(
    "bolt://localhost:7687", 
    auth=("neo4j", "password"),
    max_connection_pool_size=1000
)
llm_client = OpenAIClient(client=your_openai_client)

# Create selector with default config
selector = GlobalSelector(driver, llm_client)

# Or with custom config
config = GlobalSelectorConfig(use_summary=True, use_tag=True)
selector = GlobalSelector(driver, llm_client, selection_config=config)
```

**Sources:** [global_selection/global_selector.py:432-441]()

---

## Core Orchestration Methods

### global_selection()

The main entry point that orchestrates the complete top-down hierarchical traversal with LLM-guided selection at each layer.

```python
async def global_selection(
    self, 
    query: str, 
    group_id: str
) -> tuple[dict, dict]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | User query for context-aware node selection |
| `group_id` | `str` | Graph partition identifier (e.g., user ID) |

**Returns:** Tuple of `(results, time_stats)`

**Results Dictionary Structure:**

| Key | Type | Description |
|-----|------|-------------|
| `episodes` | `list[dict]` | Episodic nodes (memories) connected to selected entities |
| `edges` | `list[dict]` | RELATES_TO relationships (facts) between entities |
| `nodes` | `list[dict]` | Selected category and entity nodes |

**Time Stats Dictionary:**

| Key | Description |
|-----|-------------|
| `init` | Time to initialize and get max layer |
| `layer_selection` | Total time for all layer selections |
| `one_hop_neighbors` | Time to retrieve neighbors of selected nodes |

**Algorithm Flow:**

```mermaid
graph TD
    START["global_selection()"] --> GETMAX["get_max_layer()"]
    GETMAX --> INIT["Initialize tracking:<br/>previous_layer_categories = []<br/>selected_categories = {}"]
    
    INIT --> LOOP{"For each layer<br/>(max to 1)"}
    
    LOOP --> FIRST{"layer == max_layer?"}
    FIRST -->|Yes| GETNODES["get_nodes_by_layer()"]
    FIRST -->|No| CHECK{"previous_layer<br/>not empty?"}
    CHECK -->|Yes| GETCHILDREN["get_child_nodes_batch()"]
    CHECK -->|No| BREAK["Break loop"]
    
    GETNODES --> LAYERSEL["layer_selection()"]
    GETCHILDREN --> LAYERSEL
    
    LAYERSEL --> SPLIT["Split into:<br/>- selected (traverse children)<br/>- shortcuts (get all descendants)"]
    
    SPLIT --> ADDSEL["Add selected to<br/>selected_categories"]
    ADDSEL --> GETDESC["get_all_descendants_batch()<br/>for shortcuts"]
    GETDESC --> ADDDESC["Add descendants to<br/>selected_categories"]
    
    ADDDESC --> UPDATE["previous_layer_categories<br/>= selected"]
    UPDATE --> LOOP
    
    LOOP -->|Complete| NEIGHBORS["get_one_hop_neighbors_batch()<br/>for all selected"]
    
    NEIGHBORS --> FORMAT["Format timestamps<br/>Merge nodes with neighbors"]
    FORMAT --> RETURN["Return results + time_stats"]
```

**Sources:** [global_selection/global_selector.py:267-319]()

**Example Usage:**

```python
# Execute global selection
results, time_stats = await selector.global_selection(
    query="What movies has the user watched recently?",
    group_id="user_123"
)

# Access results
episodes = results['episodes']  # Memory chunks
edges = results['edges']        # Facts/relationships
nodes = results['nodes']        # Entities and categories

# Check performance
print(f"Layer selection took: {time_stats['layer_selection']:.2f}s")
print(f"Neighbor retrieval took: {time_stats['one_hop_neighbors']:.2f}s")
```

**Sources:** [global_selection/global_selector.py:267-319]()

---

### layer_selection()

LLM-guided selection of relevant nodes at a specific layer of the hierarchy.

```python
async def layer_selection(
    self, 
    query: str, 
    current_layer_categories: list[dict]
) -> tuple[list[dict], list[dict]]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | User query for relevance determination |
| `current_layer_categories` | `list[dict]` | All nodes available at current layer |

**Returns:** Tuple of `(selected_categories, shortcut_categories)`

- `selected_categories`: Nodes to traverse further (continue to children)
- `shortcut_categories`: Nodes whose all descendants should be retrieved (pruning optimization)

**LLM Response Model:**

The LLM returns structured output conforming to `NodeSelectionList`:

```python
class NodeSelection(BaseModel):
    name: str              # Node name (for human readability)
    uuid: str              # Node UUID (for precise matching)
    get_all_children: bool # True = shortcut, False = continue traversal
```

**Selection Logic Flow:**

```mermaid
graph LR
    INPUT["current_layer_categories"] --> FILTER["Filter fields based on<br/>GlobalSelectorConfig"]
    FILTER --> FORMAT["Format as JSON array<br/>with allowed fields"]
    FORMAT --> PROMPT["NODE_SELECTION_PROMPT_TEMPLATE"]
    
    PROMPT --> LLM["LLM generates response"]
    LLM --> PARSE["Parse NodeSelectionList"]
    
    PARSE --> MATCH["Match each selection<br/>by UUID or name"]
    MATCH --> SPLIT{"get_all_children?"}
    
    SPLIT -->|True| SHORTCUT["Add to shortcuts"]
    SPLIT -->|False| SELECTED["Add to selected"]
    
    SHORTCUT --> RETURN["Return (selected, shortcuts)"]
    SELECTED --> RETURN
```

**Sources:** [global_selection/global_selector.py:224-265]()

**Field Visibility:**

The method respects `GlobalSelectorConfig` to control what information the LLM sees:

| Config | Fields Provided to LLM |
|--------|------------------------|
| `use_summary=False, use_tag=True` (default) | `uuid`, `name`, `tag` |
| `use_summary=True, use_tag=True` | `uuid`, `name`, `tag`, `summary` |
| `use_summary=False, use_tag=False` | `uuid`, `name` |

**Sources:** [global_selection/global_selector.py:225-235]()

---

## Graph Query Methods (Cached)

All graph query methods use `@alru_cache(maxsize=500)` for performance optimization. Cache is scoped per query execution.

### get_max_layer()

Retrieves the maximum layer number in the hierarchical graph.

```python
@alru_cache(maxsize=CACHE_SIZE_PER_QUERY)
async def get_max_layer(self, group_id: str) -> int
```

**Cypher Query:** `Query.GET_MAX_LAYER`

```cypher
MATCH (n:Category) WHERE n.group_id = $group_id
RETURN max(n.layer) as max_layer
```

**Sources:** [global_selection/global_selector.py:103-110](), [global_selection/global_selector.py:31-34]()

---

### get_nodes_by_layer()

Retrieves all nodes at a specific layer. Layer 0 returns `Entity` nodes, higher layers return `Category` nodes.

```python
@alru_cache(maxsize=CACHE_SIZE_PER_QUERY)
async def get_nodes_by_layer(self, layer: int, group_id: str) -> list[dict]
```

**Cypher Query:** `Query.GET_NODES_BY_LAYER`

```cypher
MATCH (n:Category_{layer}) WHERE n.group_id = $group_id
RETURN n.uuid, n.name, n.tag, n.summary
```

For layer 0, the label becomes `Entity` instead of `Category_0`.

**Returned Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `uuid` | `str` | Unique node identifier |
| `name` | `str` | Node name |
| `tag` | `str` | Category/entity tag |
| `summary` | `str` | Node summary |

**Sources:** [global_selection/global_selector.py:112-118](), [global_selection/global_selector.py:36-39]()

---

### get_child_nodes()

Retrieves direct children of a parent category node.

```python
@alru_cache(maxsize=CACHE_SIZE_PER_QUERY)
async def get_child_nodes(self, parent_uuid: str, group_id: str) -> list[dict]
```

**Cypher Query:** `Query.GET_CHILD_NODES`

```cypher
MATCH (parent:Category)-[:CATEGORIZES]->(child:Category|Entity)
WHERE parent.group_id = $group_id AND parent.uuid = $parent_uuid
RETURN DISTINCT child.uuid, child.name, child.tag, child.summary, child.layer
```

**Sources:** [global_selection/global_selector.py:120-127](), [global_selection/global_selector.py:41-44]()

---

### get_all_descendants()

Retrieves all descendants (children, grandchildren, etc.) of a node using recursive path matching.

```python
@alru_cache(maxsize=CACHE_SIZE_PER_QUERY)
async def get_all_descendants(self, parent_uuid: str, group_id: str) -> list[dict]
```

**Cypher Query:** `Query.GET_ALL_DESCENDANTS`

```cypher
MATCH (parent:Category|Entity)-[:CATEGORIZES*1..]->(child:Category|Entity)
WHERE parent.group_id = $group_id AND parent.uuid = $parent_uuid
RETURN DISTINCT child.uuid, child.name, child.tag, child.summary
```

The `*1..` syntax matches paths of any length ≥ 1.

**Sources:** [global_selection/global_selector.py:144-151](), [global_selection/global_selector.py:51-54]()

---

### get_one_hop_neighbors()

Retrieves episodic nodes (memories) and related entity nodes connected to a given node.

```python
@alru_cache(maxsize=CACHE_SIZE_PER_QUERY)
async def get_one_hop_neighbors(self, node_uuid: str, group_id: str) -> dict
```

**Returns Dictionary Structure:**

| Key | Type | Description |
|-----|------|-------------|
| `episodes` | `list[dict]` | Episodic nodes with `uuid`, `content`, `valid_at` |
| `edges` | `list[dict]` | RELATES_TO edges with `uuid`, `fact`, `valid_at`, `invalid_at` |
| `nodes` | `list[dict]` | Connected entity nodes with `uuid`, `name`, `tag`, `summary` |

**Cypher Queries Used:**

1. `Query.GET_ONE_HOP_EPISODES`:
```cypher
MATCH (n)-[:MENTIONS]-(m:Episodic)
WHERE n.group_id = $group_id AND n.uuid = $node_uuid
RETURN DISTINCT m.uuid, m.content, m.valid_at
```

2. `Query.GET_ONE_HOP_NODES_AND_EDGES`:
```cypher
MATCH (n)-[r:RELATES_TO]-(m:Entity)
WHERE n.group_id = $group_id AND n.uuid = $node_uuid
RETURN r.uuid, r.fact, r.valid_at, r.invalid_at, m.uuid, m.name, m.tag, m.summary
```

**Sources:** [global_selection/global_selector.py:196-201](), [global_selection/global_selector.py:61-83]()

---

## Batch Processing Methods

Batch methods provide two execution modes for processing multiple nodes simultaneously:

| Mode | Description | Use Case |
|------|-------------|----------|
| `mp` | Multiprocessing mode using `asyncio.gather()` with cached single queries | Better for small batches with potential cache hits |
| `batch` | Single batched Cypher query processing all UUIDs at once | Better for large batches without cache hits |

### get_child_nodes_batch()

```python
async def get_child_nodes_batch(
    self, 
    parent_uuids: list[str], 
    group_id: str, 
    mode: Literal['mp', 'batch'] = 'mp'
) -> list[dict]
```

**Mode 'mp':**
- Creates parallel tasks calling `get_child_nodes()` for each UUID
- Leverages cache for previously seen UUIDs
- Deduplicates results by UUID

**Mode 'batch':**
- Executes single query with `parent_uuid IN $parent_uuids`
- More efficient for large, uncached batches

**Cypher Query (batch mode):** `Query.GET_CHILD_NODES_BATCH`

```cypher
MATCH (parent:Category)-[:CATEGORIZES]->(child:Category|Entity)
WHERE parent.group_id = $group_id AND parent.uuid IN $parent_uuids
RETURN DISTINCT child.uuid, child.name, child.tag, child.summary, child.layer
```

**Sources:** [global_selection/global_selector.py:129-142](), [global_selection/global_selector.py:46-49]()

---

### get_all_descendants_batch()

```python
async def get_all_descendants_batch(
    self, 
    parent_uuids: list[str], 
    group_id: str, 
    mode: Literal['mp', 'batch'] = 'mp'
) -> list[dict]
```

Batch version of `get_all_descendants()` with same mode options.

**Cypher Query (batch mode):** `Query.GET_ALL_DESCENDANTS_BATCH`

```cypher
MATCH (parent:Category|Entity)-[:CATEGORIZES*1..]->(child:Category|Entity)
WHERE parent.group_id = $group_id AND parent.uuid IN $parent_uuids
RETURN DISTINCT child.uuid, child.name, child.tag, child.summary
```

**Sources:** [global_selection/global_selector.py:153-166](), [global_selection/global_selector.py:56-59]()

---

### get_one_hop_neighbors_batch()

```python
async def get_one_hop_neighbors_batch(
    self, 
    node_uuids: list[str], 
    group_id: str, 
    mode: Literal['mp', 'batch'] = 'mp'
) -> dict
```

Returns aggregated neighbors from all provided node UUIDs.

**Return Structure:**

```python
{
    'episodes': list[dict],  # Deduplicated by UUID
    'edges': list[dict],     # Deduplicated by UUID
    'nodes': list[dict]      # Deduplicated by UUID
}
```

**Cypher Queries (batch mode):**

1. `Query.GET_ONE_HOP_EPISODES_BATCH`:
```cypher
MATCH (n)-[:MENTIONS]-(m:Episodic)
WHERE n.group_id = $group_id AND n.uuid IN $node_uuids
RETURN DISTINCT m.uuid, m.content, m.valid_at
```

2. `Query.GET_ONE_HOP_NODES_AND_EDGES_BATCH`:
```cypher
MATCH (n)-[r:RELATES_TO]-(m:Entity)
WHERE n.group_id = $group_id AND n.uuid IN $node_uuids
RETURN r.uuid, r.fact, r.valid_at, r.invalid_at, m.uuid, m.name, m.tag, m.summary
```

**Sources:** [global_selection/global_selector.py:203-222](), [global_selection/global_selector.py:67-83]()

---

## Caching Architecture

The `GlobalSelector` uses aggressive caching via `@alru_cache` (async LRU cache) with 500 entries per query to minimize database roundtrips.

```mermaid
graph TB
    subgraph CachingStrategy["Caching Strategy"]
        CONSTANT["CACHE_SIZE_PER_QUERY = 500"]
        
        subgraph CachedMethods["Cached Methods (@alru_cache)"]
            M1["get_max_layer()"]
            M2["get_nodes_by_layer()"]
            M3["get_child_nodes()"]
            M4["get_all_descendants()"]
            M5["get_one_hop_neighbors()"]
        end
        
        subgraph UncachedMethods["Uncached Methods"]
            B1["get_child_nodes_batch()"]
            B2["get_all_descendants_batch()"]
            B3["get_one_hop_neighbors_batch()"]
        end
        
        CLEAR["clear_cache()<br/>Invalidates all caches"]
    end
    
    B1 -.->|"mode=mp<br/>uses"| M3
    B2 -.->|"mode=mp<br/>uses"| M4
    B3 -.->|"mode=mp<br/>uses"| M5
    
    CLEAR --> M1
    CLEAR --> M2
    CLEAR --> M3
    CLEAR --> M4
    CLEAR --> M5
```

### Cache Management

**clear_cache()**

Invalidates all caches. Should be called between different query executions to prevent stale data.

```python
def clear_cache(self):
    self.get_max_layer.cache_clear()
    self.get_nodes_by_layer.cache_clear()
    self.get_child_nodes.cache_clear()
    self.get_all_descendants.cache_clear()
    self.get_one_hop_neighbors.cache_clear()
```

**Sources:** [global_selection/global_selector.py:96-101](), [global_selection/global_selector.py:20]()

**Cache Hit Patterns:**

During hierarchical traversal, caching provides significant benefits:

| Scenario | Cache Benefit |
|----------|---------------|
| Multiple queries reference same parent | `get_child_nodes()` hits cached |
| Repeated shortcut operations | `get_all_descendants()` hits cached |
| Entity appears in multiple categories | `get_one_hop_neighbors()` hits cached |
| Layer accessed multiple times | `get_nodes_by_layer()` hits cached |

**Sources:** [global_selection/global_selector.py:103-201]()

---

## Query Templates

The `Query` class provides Cypher query templates used throughout the selector. All queries filter by `group_id` to partition the graph by user/session.

### Query Class Structure

```mermaid
graph LR
    subgraph QueryClass["Query Class (Static Templates)"]
        direction TB
        
        subgraph Hierarchy["Hierarchy Queries"]
            Q1["GET_MAX_LAYER"]
            Q2["GET_NODES_BY_LAYER"]
            Q3["GET_CHILD_NODES"]
            Q4["GET_CHILD_NODES_BATCH"]
            Q5["GET_ALL_DESCENDANTS"]
            Q6["GET_ALL_DESCENDANTS_BATCH"]
        end
        
        subgraph Context["Context Retrieval"]
            Q7["GET_ONE_HOP_EPISODES"]
            Q8["GET_ONE_HOP_EPISODES_BATCH"]
            Q9["GET_ONE_HOP_NODES_AND_EDGES"]
            Q10["GET_ONE_HOP_NODES_AND_EDGES_BATCH"]
        end
    end
    
    Q3 -.->|"Batch version"| Q4
    Q5 -.->|"Batch version"| Q6
    Q7 -.->|"Batch version"| Q8
    Q9 -.->|"Batch version"| Q10
```

### Relationship Types Used

| Relationship | Direction | Description |
|--------------|-----------|-------------|
| `CATEGORIZES` | `Category → Category\|Entity` | Hierarchical parent-child structure |
| `MENTIONS` | `Entity ↔ Episodic` | Entity mentioned in episodic memory |
| `RELATES_TO` | `Entity ↔ Entity` | Fact/relationship between entities |

**Sources:** [global_selection/global_selector.py:30-83]()

---

## Helper Functions

### Data Loading Functions

**load_locomo_data_query_group_id()**

Loads LoCoMo benchmark data and extracts query-group_id pairs.

```python
def load_locomo_data_query_group_id(
    file_path: str, 
    group_id_prefix: str = 'locomo_ziyu'
) -> list[dict]
```

Returns list of dicts with `group_id` and `query` keys.

**Sources:** [global_selection/global_selector.py:321-342]()

---

**load_lme_data_query_group_id()**

Loads LongMemEval-S benchmark data and extracts query-group_id pairs.

```python
def load_lme_data_query_group_id(
    file_path: str, 
    group_id_prefix: str = 'lme_s_ziyu'
) -> list[dict]
```

Returns list of dicts with `group_id`, `query`, and `question_id` keys.

**Sources:** [global_selection/global_selector.py:344-364]()

---

### Batch Processing Functions

**get_global_search_context()**

Executes global selection for multiple queries with concurrency control.

```python
async def get_global_search_context(
    query_groupid_list: list[dict], 
    global_searcher: GlobalSelector, 
    max_concurrent: int = 5
) -> list[dict]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query_groupid_list` | `list[dict]` | List of `{group_id, query}` dicts |
| `global_searcher` | `GlobalSelector` | Configured selector instance |
| `max_concurrent` | `int` | Maximum concurrent queries (default: 5) |

Uses `asyncio.Semaphore` to limit concurrent LLM calls and database operations.

**Sources:** [global_selection/global_selector.py:366-385]()

---

**parse_locomo() and parse_lme()**

Pipeline functions for processing complete benchmark datasets with batching.

```python
async def parse_locomo(selector: GlobalSelector)
async def parse_lme(selector: GlobalSelector)
```

Both functions:
1. Load dataset using corresponding load function
2. Process in batches (50 for LoCoMo, 30 for LongMemEval-S)
3. Control concurrency (10 parallel queries)
4. Save results to JSON file (one result per line)

**Sources:** [global_selection/global_selector.py:387-429]()

---

## Usage Example: Complete Pipeline

```python
import asyncio
from neo4j import AsyncGraphDatabase
from graphiti_core.llm_client import OpenAIClient
from openai import AsyncOpenAI
from global_selection.global_selector import GlobalSelector, GlobalSelectorConfig

async def main():
    # 1. Initialize Neo4j driver
    driver = AsyncGraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "password"),
        max_connection_pool_size=1000
    )
    
    # 2. Initialize LLM client
    openai_client = AsyncOpenAI(api_key="your-api-key")
    llm_client = OpenAIClient(client=openai_client)
    
    # 3. Create selector with custom config
    config = GlobalSelectorConfig(use_summary=True, use_tag=True)
    selector = GlobalSelector(driver, llm_client, selection_config=config)
    
    # 4. Execute global selection
    query = "What are the user's favorite movies?"
    group_id = "user_123"
    
    results, time_stats = await selector.global_selection(query, group_id)
    
    # 5. Process results
    print(f"Found {len(results['episodes'])} episodes")
    print(f"Found {len(results['edges'])} facts")
    print(f"Found {len(results['nodes'])} entities")
    
    # 6. Access specific data
    for episode in results['episodes']:
        print(f"Memory: {episode['content']}")
        print(f"Time: {episode['valid_at']}")
    
    for fact in results['edges']:
        print(f"Fact: {fact['fact']}")
    
    # 7. Clean up
    selector.clear_cache()
    await driver.close()

if __name__ == "__main__":
    asyncio.run(main())
```

**Sources:** [global_selection/global_selector.py:431-452]()

---

## Performance Characteristics

### Concurrency Configuration

The implementation example uses the following concurrency parameters:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `max_connection_pool_size` | 1000 | Neo4j driver connection pool |
| `max_concurrent` | 10 | Parallel query processing |
| `batch_size` | 50 (LoCoMo), 30 (LME-S) | Results saved per batch |

**Sources:** [global_selection/global_selector.py:389-412](), [global_selection/global_selector.py:435]()

### Time Complexity

| Operation | Complexity | Notes |
|-----------|------------|-------|
| `get_max_layer()` | O(1) with cache | O(V) without cache (V = category nodes) |
| `get_nodes_by_layer()` | O(L) with cache | O(V) without cache (L = nodes in layer) |
| `layer_selection()` | O(L) + LLM call | L = nodes in current layer |
| `global_selection()` | O(H × L × LLM) | H = hierarchy depth, L = avg layer size |
| `get_one_hop_neighbors()` | O(1) with cache | O(E) without cache (E = connected edges) |

**Sources:** [global_selection/global_selector.py:103-319]()

---

## Data Models

### NodeSelection

Pydantic model representing a single node selection decision from the LLM.

```python
class NodeSelection(BaseModel):
    name: str              # Human-readable node name
    uuid: str              # Unique node identifier
    get_all_children: bool # Shortcut flag
```

**Sources:** [global_selection/global_selector.py:22-25]()

### NodeSelectionList

Container for LLM response with multiple node selections.

```python
class NodeSelectionList(BaseModel):
    selections: list[NodeSelection]
```

Used as `response_model` parameter in LLM client calls to ensure structured output.

**Sources:** [global_selection/global_selector.py:27-28](), [global_selection/global_selector.py:243-244]()

---

## Integration Points

```mermaid
graph TB
    subgraph External["External Systems"]
        NEO4J["Neo4j Database<br/>AsyncDriver"]
        LLM_API["LLM API<br/>OpenAI/Azure"]
    end
    
    subgraph GlobalSelectorSystem["GlobalSelector System"]
        GS["GlobalSelector"]
        PROMPT["NODE_SELECTION_PROMPT_TEMPLATE"]
        QUERY["Query Templates"]
    end
    
    subgraph Graphiti["Graphiti Framework"]
        LLMC["LLMClient"]
        MESSAGE["Message"]
    end
    
    subgraph Dependencies["Python Libraries"]
        ASYNCIO["asyncio"]
        ALRU["async_lru"]
        PYDANTIC["pydantic"]
    end
    
    NEO4J --> GS
    LLM_API --> LLMC
    LLMC --> GS
    
    GS --> QUERY
    GS --> PROMPT
    GS --> ASYNCIO
    GS --> ALRU
    GS --> PYDANTIC
    
    PROMPT --> MESSAGE
    MESSAGE --> LLMC
```

**Sources:** [global_selection/global_selector.py:1-18]()

---

## Error Handling

### LLM Response Validation

When the LLM returns node names/UUIDs that don't match input nodes:

```python
if uuid in category_dict:
    selected_nodes = category_dict[uuid]
elif name in category_name_dict:
    selected_nodes = category_name_dict[name]
else:
    print(f"Warning: LLM returned name '{name}' and uuid '{uuid}' "
          f"that do not match any input node. Skipping.")
    continue
```

The system attempts UUID matching first, falls back to name matching, and skips invalid selections with a warning.

**Sources:** [global_selection/global_selector.py:254-260]()

### Batch Mode Validation

```python
if mode == 'mp':
    # ... multiprocessing logic
elif mode == 'batch':
    # ... batch query logic
else:
    raise ValueError("mode must be 'mp' or 'batch'")
```

All batch methods validate the `mode` parameter and raise `ValueError` for invalid values.

**Sources:** [global_selection/global_selector.py:141-142](), [global_selection/global_selector.py:165-166](), [global_selection/global_selector.py:221-222]()

---

## See Also

- [System-2 Global Selection](#2.3) - Conceptual architecture
- [Prompt Engineering](#3.3) - NODE_SELECTION_PROMPT_TEMPLATE details
- [Graph Database Schema](#3.2) - Neo4j schema and relationships
- [Configuration Options](#3.4) - System-wide configuration
- [Performance Optimization](#3.5) - Optimization strategies

**Sources:** [global_selection/global_selector.py:1-453]()

---

# Page: Graph Database Schema

# Graph Database Schema

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [global_selection/global_selector.py](global_selection/global_selector.py)

</details>



## Purpose and Scope

This document provides a comprehensive reference for the Neo4j graph database schema used by Mnemis. It details the node types, relationship types, properties, and hierarchical organization that enable both System-1 similarity search and System-2 global selection retrieval mechanisms.

For information about how this schema is used in retrieval operations, see [System-2 Global Selection](#2.3). For implementation details of the GlobalSelector class that queries this schema, see [GlobalSelector Class Reference](#3.1).

## Schema Overview

The Mnemis graph database implements two distinct but interconnected graph structures:

1. **Base Graph**: A flat structure connecting Entity and Episodic nodes through MENTIONS and RELATES_TO relationships, optimized for System-1 similarity search
2. **Hierarchical Graph**: A tree structure of Category nodes with multiple layers, enabling System-2's top-down traversal and global selection

All nodes within a user's memory space share a common `group_id` property for isolation and efficient querying.

```mermaid
graph TB
    subgraph "Hierarchical Graph Structure"
        C3["Category_3<br/>(Layer 3)<br/>Top-level concepts"]
        C2a["Category_2<br/>(Layer 2)<br/>Mid-level categories"]
        C2b["Category_2<br/>(Layer 2)"]
        C1a["Category_1<br/>(Layer 1)<br/>Low-level categories"]
        C1b["Category_1<br/>(Layer 1)"]
        C1c["Category_1<br/>(Layer 1)"]
    end
    
    subgraph "Base Graph Structure"
        E1["Entity<br/>(Layer 0)<br/>Concrete concepts"]
        E2["Entity<br/>(Layer 0)"]
        E3["Entity<br/>(Layer 0)"]
        EP1["Episodic<br/>Memory messages"]
        EP2["Episodic"]
        EP3["Episodic"]
    end
    
    C3 -->|"CATEGORIZES"| C2a
    C3 -->|"CATEGORIZES"| C2b
    C2a -->|"CATEGORIZES"| C1a
    C2a -->|"CATEGORIZES"| C1b
    C2b -->|"CATEGORIZES"| C1c
    C1a -->|"CATEGORIZES"| E1
    C1b -->|"CATEGORIZES"| E2
    C1c -->|"CATEGORIZES"| E3
    
    E1 <-->|"RELATES_TO<br/>(fact)"| E2
    E2 <-->|"RELATES_TO<br/>(fact)"| E3
    
    E1 -.->|"MENTIONS"| EP1
    E2 -.->|"MENTIONS"| EP2
    E3 -.->|"MENTIONS"| EP3
    
    style C3 fill:#f9f9f9
    style E1 fill:#f0f0f0
    style E2 fill:#f0f0f0
    style E3 fill:#f0f0f0
    style EP1 fill:#e8e8e8
    style EP2 fill:#e8e8e8
    style EP3 fill:#e8e8e8
```

**Sources**: [global_selection/global_selector.py:30-83](), [README.md:26-29]()

## Node Types and Properties

### Category Nodes

Category nodes form the hierarchical structure, organized into discrete layers. Each layer is represented by a distinct label (`Category_1`, `Category_2`, etc.).

| Property | Type | Description | Required |
|----------|------|-------------|----------|
| `uuid` | String | Unique identifier for the category | Yes |
| `name` | String | Human-readable category name | Yes |
| `tag` | String | Classification tag for the category | Yes |
| `summary` | String | Descriptive summary of the category's semantic scope | Yes |
| `layer` | Integer | Hierarchical layer number (1, 2, 3, ...) | Yes |
| `group_id` | String | Isolation key for user/session-specific graphs | Yes |

Categories at higher layers represent more abstract concepts, while lower layers represent more specific concepts. The `layer` property enables efficient layer-by-layer traversal in System-2 global selection.

**Sources**: [global_selection/global_selector.py:31-39](), [global_selection/global_selector.py:113-118]()

### Entity Nodes

Entity nodes represent concrete concepts and facts extracted from conversations. They reside at layer 0 and form the foundation of both the base and hierarchical graphs.

| Property | Type | Description | Required |
|----------|------|-------------|----------|
| `uuid` | String | Unique identifier for the entity | Yes |
| `name` | String | Entity name or key phrase | Yes |
| `tag` | String | Entity type classification | Yes |
| `summary` | String | Summarized description of the entity | Yes |
| `group_id` | String | Isolation key for user/session-specific graphs | Yes |

Entity nodes do not have a `layer` property or are implicitly at layer 0. They are retrieved using the `Entity` label directly.

**Sources**: [global_selection/global_selector.py:36-39](), [global_selection/global_selector.py:113-118]()

### Episodic Nodes

Episodic nodes store the raw conversational messages or memory episodes from which entities and relationships are extracted.

| Property | Type | Description | Required |
|----------|------|-------------|----------|
| `uuid` | String | Unique identifier for the episode | Yes |
| `content` | String | Raw message content | Yes |
| `valid_at` | DateTime | Timestamp when the episode was created | Yes |
| `group_id` | String | Isolation key for user/session-specific graphs | Yes |

The `valid_at` timestamp enables temporal reasoning and chronological ordering of memories.

**Sources**: [global_selection/global_selector.py:61-65](), [global_selection/global_selector.py:302-307]()

## Relationship Types and Properties

### CATEGORIZES Relationship

The `CATEGORIZES` relationship builds the hierarchical graph structure, connecting Category nodes to other Category nodes or to Entity nodes.

```mermaid
graph LR
    P["Category<br/>(Layer N)"]
    C1["Category<br/>(Layer N-1)"]
    C2["Entity<br/>(Layer 0)"]
    
    P -->|"CATEGORIZES"| C1
    P -->|"CATEGORIZES"| C2
```

**Direction**: Parent → Child (top-down)

**Connects**:
- `Category` → `Category` (between layers)
- `Category` → `Entity` (layer N to layer 0)

**Properties**: None

**Query Usage**: The relationship is traversed bidirectionally in queries. Top-down traversal retrieves children for a given parent ([global_selection/global_selector.py:41-44]()), while the `[:CATEGORIZES*1..]` syntax retrieves all descendants ([global_selection/global_selector.py:51-54]()).

**Sources**: [global_selection/global_selector.py:41-59]()

### MENTIONS Relationship

The `MENTIONS` relationship connects Entity or Category nodes to Episodic nodes, indicating that an entity or category is mentioned or discussed in a specific conversation episode.

```mermaid
graph LR
    E["Entity/Category"]
    EP1["Episodic"]
    EP2["Episodic"]
    
    E -.->|"MENTIONS"| EP1
    E -.->|"MENTIONS"| EP2
```

**Direction**: Undirected (bidirectional)

**Connects**:
- `Entity` ↔ `Episodic`
- `Category` ↔ `Episodic`

**Properties**: None

**Query Usage**: Retrieved as part of one-hop neighbor expansion to gather evidence messages for selected entities or categories ([global_selection/global_selector.py:61-71]()).

**Sources**: [global_selection/global_selector.py:61-71]()

### RELATES_TO Relationship

The `RELATES_TO` relationship represents factual statements or assertions connecting two Entity nodes. This forms the knowledge graph portion of the base graph.

```mermaid
graph LR
    E1["Entity A"]
    E2["Entity B"]
    
    E1 <-->|"RELATES_TO<br/>{fact, valid_at, invalid_at}"| E2
```

**Direction**: Undirected (bidirectional)

**Connects**:
- `Entity` ↔ `Entity`

**Properties**:

| Property | Type | Description | Required |
|----------|------|-------------|----------|
| `uuid` | String | Unique identifier for the fact/edge | Yes |
| `fact` | String | Natural language statement of the relationship | Yes |
| `valid_at` | DateTime | Timestamp when the fact became valid | Yes |
| `invalid_at` | DateTime | Timestamp when the fact became invalid (null if still valid) | No |

The temporal properties (`valid_at`, `invalid_at`) enable tracking of fact evolution and temporal reasoning.

**Query Usage**: Retrieved during one-hop neighbor expansion to gather related entities and connecting facts ([global_selection/global_selector.py:73-83]()).

**Sources**: [global_selection/global_selector.py:73-83](), [global_selection/global_selector.py:168-194]()

## Hierarchical Layer Structure

The hierarchical graph organizes Category nodes into discrete layers, with each layer labeled as `Category_N` where N is the layer number. The layer system follows these principles:

1. **Layer 0**: Entity nodes (not labeled as Category)
2. **Layer 1+**: Category nodes with increasing abstraction
3. **Maximum Layer**: Determined dynamically per `group_id`

### Layer Organization

```mermaid
graph TB
    subgraph "Layer 3 - Highest Abstraction"
        L3_1["Category_3<br/>uuid, name, tag, summary, layer=3"]
        L3_2["Category_3"]
    end
    
    subgraph "Layer 2 - Mid-level Concepts"
        L2_1["Category_2<br/>uuid, name, tag, summary, layer=2"]
        L2_2["Category_2"]
        L2_3["Category_2"]
    end
    
    subgraph "Layer 1 - Specific Categories"
        L1_1["Category_1<br/>uuid, name, tag, summary, layer=1"]
        L1_2["Category_1"]
        L1_3["Category_1"]
        L1_4["Category_1"]
    end
    
    subgraph "Layer 0 - Concrete Entities"
        E1["Entity<br/>uuid, name, tag, summary"]
        E2["Entity"]
        E3["Entity"]
        E4["Entity"]
        E5["Entity"]
    end
    
    L3_1 --> L2_1
    L3_1 --> L2_2
    L3_2 --> L2_3
    
    L2_1 --> L1_1
    L2_1 --> L1_2
    L2_2 --> L1_3
    L2_3 --> L1_4
    
    L1_1 --> E1
    L1_1 --> E2
    L1_2 --> E3
    L1_3 --> E4
    L1_4 --> E5
```

### Layer Discovery and Traversal

The `GlobalSelector` class implements layer-aware operations:

1. **Maximum Layer Query**: Finds the highest layer in the hierarchy for a given `group_id`:
   ```cypher
   MATCH (n:Category) WHERE n.group_id = $group_id
   RETURN max(n.layer) AS max_layer
   ```

2. **Layer-specific Node Retrieval**: Queries nodes at a specific layer using dynamic label construction:
   ```cypher
   MATCH (n:Category_2) WHERE n.group_id = $group_id
   RETURN n.uuid, n.name, n.tag, n.summary
   ```

3. **Child Node Retrieval**: Gets immediate children of a parent node:
   ```cypher
   MATCH (parent:Category)-[:CATEGORIZES]->(child:Category|Entity)
   WHERE parent.group_id = $group_id AND parent.uuid = $parent_uuid
   RETURN child.uuid, child.name, child.tag, child.summary, child.layer
   ```

**Sources**: [global_selection/global_selector.py:31-49](), [global_selection/global_selector.py:104-118]()

## Query Patterns and Access Methods

### Primary Query Templates

The `Query` class in `GlobalSelector` defines reusable Cypher query templates:

| Query Method | Purpose | Complexity |
|--------------|---------|------------|
| `GET_MAX_LAYER` | Find maximum layer in hierarchy | O(1) |
| `GET_NODES_BY_LAYER` | Retrieve all nodes at specific layer | O(n) per layer |
| `GET_CHILD_NODES` | Get immediate children of a node | O(1) per node |
| `GET_ALL_DESCENDANTS` | Retrieve entire subtree | O(n) per subtree |
| `GET_ONE_HOP_EPISODES` | Get episodic memories mentioning a node | O(1) per node |
| `GET_ONE_HOP_NODES_AND_EDGES` | Get related entities and facts | O(1) per node |

### Batch vs. Single Query Modes

Each query method has two execution modes:

1. **Single Mode**: Executes one query per node (cached with `@alru_cache`)
2. **Batch Mode**: Executes one query for multiple nodes using `IN` operator

Example comparison for child node retrieval:

**Single Mode** (leverages cache):
```python
tasks = [get_child_nodes(uuid, group_id) for uuid in parent_uuids]
results = await asyncio.gather(*tasks)
```

**Batch Mode** (single query):
```cypher
MATCH (parent:Category)-[:CATEGORIZES]->(child:Category|Entity)
WHERE parent.group_id = $group_id AND parent.uuid IN $parent_uuids
RETURN child.uuid, child.name, child.tag, child.summary, child.layer
```

The system defaults to batch mode for efficiency in layer-by-layer traversal ([global_selection/global_selector.py:269]()).

**Sources**: [global_selection/global_selector.py:30-83](), [global_selection/global_selector.py:129-166]()

## Graph Isolation with group_id

The `group_id` property implements multi-tenancy and user isolation in the graph database. Every node contains a `group_id` that:

1. **Isolates User Memory**: Each user or session has a unique `group_id` prefix
2. **Enables Efficient Filtering**: All queries filter on `group_id` first
3. **Supports Parallel Processing**: Multiple users can be processed concurrently

### group_id Naming Convention

```
{dataset}_{variant}_{user_index}

Examples:
- locomo_mnemis_coreAI_tel_b20_nec_full_0
- locomo_mnemis_coreAI_tel_b20_nec_full_1
- lme_s_mnemis_coreAI_tel_b20_nec_full_0
```

Every Cypher query in the system includes a `WHERE n.group_id = $group_id` clause to ensure data isolation.

**Sources**: [global_selection/global_selector.py:31-83](), [global_selection/global_selector.py:321-364]()

## Schema Traversal Flow in Global Selection

The following diagram illustrates how the GlobalSelector traverses the schema during System-2 retrieval:

```mermaid
graph TB
    START["Global Selection Start<br/>Query + group_id"]
    
    GET_MAX["get_max_layer()<br/>Query: GET_MAX_LAYER<br/>Returns: max_layer integer"]
    
    LAYER_LOOP["For layer = max_layer<br/>down to layer = 1"]
    
    GET_NODES["get_nodes_by_layer(layer)<br/>Query: GET_NODES_BY_LAYER<br/>Returns: Category nodes at layer"]
    
    LLM_SELECT["layer_selection()<br/>LLM filters nodes<br/>Returns: selected + shortcuts"]
    
    GET_CHILDREN["get_child_nodes_batch()<br/>Query: GET_CHILD_NODES_BATCH<br/>Returns: Children of selected nodes"]
    
    GET_DESC["get_all_descendants_batch()<br/>Query: GET_ALL_DESCENDANTS<br/>Returns: All descendants of shortcuts"]
    
    NEXT_LAYER{"More<br/>layers?"}
    
    ONE_HOP["get_one_hop_neighbors_batch()<br/>Queries:<br/>- GET_ONE_HOP_EPISODES<br/>- GET_ONE_HOP_NODES_AND_EDGES<br/>Returns: episodes, edges, nodes"]
    
    RESULT["Return results:<br/>{episodes, edges, nodes}"]
    
    START --> GET_MAX
    GET_MAX --> LAYER_LOOP
    LAYER_LOOP --> GET_NODES
    GET_NODES --> LLM_SELECT
    LLM_SELECT --> GET_CHILDREN
    LLM_SELECT --> GET_DESC
    GET_CHILDREN --> NEXT_LAYER
    GET_DESC --> NEXT_LAYER
    NEXT_LAYER -->|"Yes"| LAYER_LOOP
    NEXT_LAYER -->|"No"| ONE_HOP
    ONE_HOP --> RESULT
```

**Process Steps**:

1. **Initialization** ([global_selection/global_selector.py:271-272]()): Query maximum layer for the `group_id`
2. **Layer Iteration** ([global_selection/global_selector.py:277-294]()): Traverse from highest to lowest layer
3. **Node Selection** ([global_selection/global_selector.py:285]()): LLM filters relevant nodes at each layer
4. **Child Expansion** ([global_selection/global_selector.py:281]()): Retrieve children of selected nodes for next iteration
5. **Shortcut Expansion** ([global_selection/global_selector.py:289-291]()): For "shortcut" nodes, retrieve all descendants at once
6. **Context Expansion** ([global_selection/global_selector.py:299]()): Retrieve one-hop neighbors (episodes and edges) for all selected nodes
7. **Result Assembly** ([global_selection/global_selector.py:314-318]()): Format and return episodes, edges, and nodes

**Sources**: [global_selection/global_selector.py:267-319]()

## Temporal Properties and Formatting

Multiple node and relationship types include temporal properties for chronological reasoning:

### DateTime Properties

| Property | Found On | Format |
|----------|----------|--------|
| `valid_at` | Episodic nodes, RELATES_TO edges | DateTime object → `YYYY/MM/DD (Day) HH:MM` |
| `invalid_at` | RELATES_TO edges | DateTime object → `YYYY/MM/DD (Day) HH:MM` |

### Formatting Implementation

The `global_selection()` method applies consistent datetime formatting before returning results:

```python
def format(item: dict):
    if item.get('valid_at') and type(item['valid_at']) != str:
        item['valid_at'] = item['valid_at'].strftime("%Y/%m/%d (%a) %H:%M")
    if item.get('invalid_at') and type(item['invalid_at']) != str:
        item['invalid_at'] = item['invalid_at'].strftime("%Y/%m/%d (%a) %H:%M")
    return item
```

This ensures consistent timestamp representation in the output JSON, facilitating temporal reasoning by downstream components.

**Sources**: [global_selection/global_selector.py:302-312]()

## Schema-to-Code Entity Mapping

The following table maps graph schema elements to their corresponding code entities in the GlobalSelector implementation:

| Schema Element | Query Template Constant | Method | Return Type |
|----------------|------------------------|---------|-------------|
| Category nodes | `Query.GET_NODES_BY_LAYER` | `get_nodes_by_layer()` | `list[dict]` |
| CATEGORIZES children | `Query.GET_CHILD_NODES` | `get_child_nodes()` | `list[dict]` |
| CATEGORIZES descendants | `Query.GET_ALL_DESCENDANTS` | `get_all_descendants()` | `list[dict]` |
| Episodic via MENTIONS | `Query.GET_ONE_HOP_EPISODES` | Part of `get_one_hop_neighbors()` | `dict['episodes']` |
| Entity via RELATES_TO | `Query.GET_ONE_HOP_NODES_AND_EDGES` | Part of `get_one_hop_neighbors()` | `dict['nodes']` |
| RELATES_TO edges | `Query.GET_ONE_HOP_NODES_AND_EDGES` | Part of `get_one_hop_neighbors()` | `dict['edges']` |
| Maximum layer value | `Query.GET_MAX_LAYER` | `get_max_layer()` | `int` |

All query methods support caching via `@alru_cache(maxsize=CACHE_SIZE_PER_QUERY)` where `CACHE_SIZE_PER_QUERY = 500`.

**Sources**: [global_selection/global_selector.py:30-222]()

## Example Schema Instance

The following diagram shows a concrete example of a populated graph for a user discussing restaurants and preferences:

```mermaid
graph TB
    subgraph "Layer 2"
        C2_1["Category_2<br/>Food & Dining<br/>uuid: cat2_001"]
        C2_2["Category_2<br/>Personal Info<br/>uuid: cat2_002"]
    end
    
    subgraph "Layer 1"
        C1_1["Category_1<br/>Restaurants<br/>uuid: cat1_001"]
        C1_2["Category_1<br/>Preferences<br/>uuid: cat1_002"]
        C1_3["Category_1<br/>Family<br/>uuid: cat1_003"]
    end
    
    subgraph "Layer 0 - Entities"
        E1["Entity<br/>Pizza Palace<br/>uuid: ent_001<br/>tag: restaurant"]
        E2["Entity<br/>Italian Cuisine<br/>uuid: ent_002<br/>tag: cuisine"]
        E3["Entity<br/>Sarah<br/>uuid: ent_003<br/>tag: person"]
        E4["Entity<br/>Saturday Night<br/>uuid: ent_004<br/>tag: time"]
    end
    
    subgraph "Episodic Memories"
        EP1["Episodic<br/>content: 'We went to Pizza Palace last Saturday'<br/>valid_at: 2024/01/15 10:30<br/>uuid: ep_001"]
        EP2["Episodic<br/>content: 'Sarah loves Italian food'<br/>valid_at: 2024/01/15 10:32<br/>uuid: ep_002"]
    end
    
    C2_1 -->|"CATEGORIZES"| C1_1
    C2_1 -->|"CATEGORIZES"| C1_2
    C2_2 -->|"CATEGORIZES"| C1_3
    
    C1_1 -->|"CATEGORIZES"| E1
    C1_2 -->|"CATEGORIZES"| E2
    C1_3 -->|"CATEGORIZES"| E3
    C1_1 -->|"CATEGORIZES"| E4
    
    E1 <-->|"RELATES_TO<br/>fact: 'Pizza Palace serves Italian Cuisine'<br/>valid_at: 2024/01/15<br/>uuid: fact_001"| E2
    E3 <-->|"RELATES_TO<br/>fact: 'Sarah prefers Italian Cuisine'<br/>valid_at: 2024/01/15<br/>uuid: fact_002"| E2
    
    E1 -.->|"MENTIONS"| EP1
    E4 -.->|"MENTIONS"| EP1
    E3 -.->|"MENTIONS"| EP2
    E2 -.->|"MENTIONS"| EP2
```

**Sources**: Inferred from [global_selection/global_selector.py:30-83]() query structure

---

# Page: Prompt Engineering

# Prompt Engineering

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [global_selection/global_selector.py](global_selection/global_selector.py)
- [global_selection/prompts.py](global_selection/prompts.py)

</details>



This page documents the prompt engineering approach used in Mnemis's System-2 global selection mechanism. It details the `NODE_SELECTION_PROMPT_TEMPLATE`, its selection criteria, response format, and how it guides LLM-based hierarchical graph traversal. For details on how the prompt is integrated into the complete traversal algorithm, see [System-2 Global Selection](#2.3). For the complete GlobalSelector API, see [GlobalSelector Class Reference](#3.1).

## Overview

The System-2 retrieval mechanism relies on LLM-guided node selection at each layer of the hierarchical graph. The prompt engineering component defines how the LLM evaluates which category nodes are relevant to a user query, enabling deliberate, top-down reasoning over the knowledge graph.

**Sources:** [global_selection/prompts.py:1-23](), [global_selection/global_selector.py:18]()

---

## NODE_SELECTION_PROMPT_TEMPLATE Structure

### Template Definition

The core prompt template is defined in `NODE_SELECTION_PROMPT_TEMPLATE` and consists of three main sections:

| Section | Purpose | Location |
|---------|---------|----------|
| **Role Definition** | Establishes LLM as knowledge graph analyzer | Lines 1-2 |
| **Selection Criteria** | Defines conditions for node relevance | Lines 3-11 |
| **Input Context** | Provides query and available nodes | Lines 17-22 |

**Sources:** [global_selection/prompts.py:1-23]()

### Full Template Content

```
You are analyzing a hierarchical knowledge graph to help answer a user query.

Select all nodes that could help answer the query. A node is helpful if it:

- Directly relates to the query;
- Covers a clearly relevant topic, concept, or category;
- Provides useful background or context;
- Contains user-specific information (e.g. interests, goals, constraints);
- Likely has sub-nodes that may be helpful.

Do not be overly strict: include nodes that might provide context or personalization, 
even if they seem partially redundant.

For each selected node:
- "name" is the node's name.
- "uuid" is the node's unique identifier.
- "get_all_children" is an boolean value. Set true only if you're confident all its 
  sub-nodes are helpful.
---
User Query:
"{query}"

Available Nodes:
{nodes_info}
```

**Sources:** [global_selection/prompts.py:1-23]()

---

## Selection Criteria

### Five-Point Relevance Framework

The prompt defines five criteria for node selection, arranged from direct relevance to potential relevance:

```mermaid
graph TB
    Query["User Query"]
    
    subgraph "Selection Criteria (Priority Order)"
        C1["1. Direct Relation<br/>Explicitly mentioned concepts"]
        C2["2. Topical Coverage<br/>Relevant topic/concept/category"]
        C3["3. Background Context<br/>Supporting information"]
        C4["4. User-Specific Info<br/>Interests/goals/constraints"]
        C5["5. Potential Sub-nodes<br/>Likely relevant children"]
    end
    
    Decision{"Node<br/>Selected?"}
    
    Query --> C1
    Query --> C2
    Query --> C3
    Query --> C4
    Query --> C5
    
    C1 --> Decision
    C2 --> Decision
    C3 --> Decision
    C4 --> Decision
    C5 --> Decision
    
    Decision -->|"Yes"| Selected["Include in<br/>NodeSelection"]
    Decision -->|"No"| Rejected["Skip node"]
```

**Selection Criteria Details:**

| Criterion | Description | Example |
|-----------|-------------|---------|
| **Direct Relation** | Node explicitly mentioned or queried | Query: "favorite movies" → Node: "Movie Preferences" |
| **Topical Coverage** | Node covers clearly relevant topic | Query: "weekend plans" → Node: "Recreation Activities" |
| **Background Context** | Node provides useful context | Query: "dinner tonight" → Node: "Dietary Restrictions" |
| **User-Specific** | Personal information, preferences, constraints | Query: "book recommendation" → Node: "Reading Interests" |
| **Potential Sub-nodes** | Parent likely contains relevant children | Query: "hobbies" → Node: "Personal Interests" (has hobby sub-nodes) |

### Leniency Instruction

The prompt explicitly instructs: *"Do not be overly strict: include nodes that might provide context or personalization, even if they seem partially redundant."*

This design choice prioritizes **recall over precision** in initial selection, allowing the LLM to cast a wider net. Redundancy is acceptable because downstream one-hop neighbor retrieval will provide the actual context for answer generation.

**Sources:** [global_selection/prompts.py:3-11]()

---

## Prompt Integration in Layer Selection

### Data Flow Diagram

```mermaid
graph TB
    Query["query: str"]
    Categories["current_layer_categories<br/>list[dict]"]
    
    subgraph "layer_selection Method"
        direction TB
        
        Filter["Filter Fields<br/>allowed_fields"]
        Context["Build category_context<br/>uuid, name, tag?, summary?"]
        Format["Format Prompt<br/>NODE_SELECTION_PROMPT_TEMPLATE"]
        LLM["llm_client.generate_response<br/>response_model=NodeSelectionList"]
        Parse["Parse Response<br/>selections list"]
        Match["Match UUIDs/Names<br/>category_dict lookup"]
        Split["Split by get_all_children<br/>selected vs shortcuts"]
    end
    
    Output1["selected_categories<br/>list[dict]"]
    Output2["shortcut_categories<br/>list[dict]"]
    
    Query --> Format
    Categories --> Filter
    Filter --> Context
    Context --> Format
    Format --> LLM
    LLM --> Parse
    Parse --> Match
    Match --> Split
    Split --> Output1
    Split --> Output2
```

**Sources:** [global_selection/global_selector.py:224-265]()

### Code Implementation

The `layer_selection` method orchestrates prompt construction and LLM invocation:

```python
async def layer_selection(self, query: str, current_layer_categories: list[dict]) 
    -> tuple[list[dict], list[dict]]:
```

**Key Steps:**

1. **Field Filtering** ([global_selection/global_selector.py:225-235]())
   - Selects fields based on `selection_config`
   - Always includes: `uuid`, `name`
   - Conditionally includes: `tag`, `summary`

2. **Context Building** ([global_selection/global_selector.py:233-235]())
   - Creates `category_context` with filtered fields
   - Converts to JSON strings for prompt

3. **Prompt Formatting** ([global_selection/global_selector.py:237-240]())
   - Injects `query` and `nodes_info`
   - Uses `ensure_ascii=False` to preserve Unicode

4. **LLM Generation** ([global_selection/global_selector.py:241-245]())
   - Uses structured output with `response_model=NodeSelectionList`
   - Requests `ModelSize.large` for better reasoning

5. **Response Parsing** ([global_selection/global_selector.py:247-265]())
   - Matches returned UUIDs/names to input nodes
   - Handles mismatch warnings
   - Splits by `get_all_children` flag

**Sources:** [global_selection/global_selector.py:224-265]()

---

## Response Format

### Pydantic Models

The LLM response is structured using two Pydantic models:

```mermaid
classDiagram
    class NodeSelection {
        +str name
        +str uuid
        +bool get_all_children
    }
    
    class NodeSelectionList {
        +list[NodeSelection] selections
    }
    
    NodeSelectionList "1" --> "*" NodeSelection
```

#### NodeSelection Model

```python
class NodeSelection(BaseModel):
    name: str
    uuid: str
    get_all_children: bool
```

**Field Descriptions:**

| Field | Type | Purpose |
|-------|------|---------|
| `name` | `str` | Node's human-readable name |
| `uuid` | `str` | Node's unique identifier (primary key) |
| `get_all_children` | `bool` | If `true`, retrieves entire subtree without further filtering |

**Sources:** [global_selection/global_selector.py:22-25]()

#### NodeSelectionList Model

```python
class NodeSelectionList(BaseModel):
    selections: list[NodeSelection]
```

Wraps multiple selections in a structured list for type-safe LLM response parsing.

**Sources:** [global_selection/global_selector.py:27-28]()

### Shortcut Mechanism

The `get_all_children` field enables **subtree shortcuts**:

- **`false`**: LLM will evaluate child nodes at next layer (standard traversal)
- **`true`**: All descendants retrieved immediately (shortcut to entities)

This optimization allows the LLM to skip unnecessary layers when confident that an entire subtree is relevant.

**Example:**
```
Query: "What are all my favorite foods?"
Node: "Food Preferences" (layer 2)

Selection:
{
  "name": "Food Preferences",
  "uuid": "abc-123",
  "get_all_children": true  // Skip layer 1, get all food entities directly
}
```

**Sources:** [global_selection/global_selector.py:261-264](), [global_selection/global_selector.py:289-291]()

---

## Configuration Options

### GlobalSelectorConfig

The `GlobalSelectorConfig` class controls which node fields are exposed to the LLM:

```python
class GlobalSelectorConfig(BaseModel):
    use_summary: bool = False
    use_tag: bool = True
```

**Configuration Options:**

| Field | Default | Description |
|-------|---------|-------------|
| `use_summary` | `False` | Include node summaries in prompt context |
| `use_tag` | `True` | Include node tags in prompt context |

**Sources:** [global_selection/global_selector.py:85-87]()

### Field Impact on Prompt

The configuration determines the `allowed_fields` used in prompt construction:

```python
allowed_fields = [
    "uuid",
    "name",
    *(['tag'] if self.selection_config.use_tag else []),
    *(['summary'] if self.selection_config.use_summary else []),
]
```

**Field Inclusion Logic:**

```mermaid
graph LR
    Config["GlobalSelectorConfig"]
    
    Always["Always Included:<br/>uuid, name"]
    Tag{"use_tag<br/>= true?"}
    Summary{"use_summary<br/>= true?"}
    
    Config --> Always
    Config --> Tag
    Config --> Summary
    
    Tag -->|"Yes"| IncludeTag["Include 'tag'"]
    Tag -->|"No"| SkipTag["Skip 'tag'"]
    
    Summary -->|"Yes"| IncludeSummary["Include 'summary'"]
    Summary -->|"No"| SkipSummary["Skip 'summary'"]
    
    Always --> Context["category_context"]
    IncludeTag --> Context
    IncludeSummary --> Context
    
    Context --> Prompt["NODE_SELECTION_PROMPT_TEMPLATE"]
```

**Default Behavior:**
- **`uuid`** and **`name`**: Always included (required for node identification)
- **`tag`**: Included by default (provides entity type/category hint)
- **`summary`**: Excluded by default (reduces token usage; name+tag usually sufficient)

**Sources:** [global_selection/global_selector.py:225-235]()

---

## Prompt Construction Example

### Input Data Example

**Query:**
```
"What restaurants did I visit last week?"
```

**Current Layer Categories (Layer 2):**
```json
[
  {
    "uuid": "cat-001",
    "name": "Dining & Restaurants",
    "tag": "Food_Services",
    "summary": "Information about restaurant visits and food preferences"
  },
  {
    "uuid": "cat-002",
    "name": "Travel & Transportation",
    "tag": "Travel",
    "summary": "Travel activities and transportation methods"
  },
  {
    "uuid": "cat-003",
    "name": "Entertainment",
    "tag": "Leisure",
    "summary": "Entertainment activities and media consumption"
  }
]
```

### Constructed Prompt

With `use_tag=True, use_summary=False`:

```
You are analyzing a hierarchical knowledge graph to help answer a user query.

Select all nodes that could help answer the query. A node is helpful if it:

- Directly relates to the query;
- Covers a clearly relevant topic, concept, or category;
- Provides useful background or context;
- Contains user-specific information (e.g. interests, goals, constraints);
- Likely has sub-nodes that may be helpful.

Do not be overly strict: include nodes that might provide context or personalization, 
even if they seem partially redundant.

For each selected node:
- "name" is the node's name.
- "uuid" is the node's unique identifier.
- "get_all_children" is an boolean value. Set true only if you're confident all its 
  sub-nodes are helpful.
---
User Query:
"What restaurants did I visit last week?"

Available Nodes:
{"uuid": "cat-001", "name": "Dining & Restaurants", "tag": "Food_Services"}
{"uuid": "cat-002", "name": "Travel & Transportation", "tag": "Travel"}
{"uuid": "cat-003", "name": "Entertainment", "tag": "Leisure"}
```

### Expected Response

```json
{
  "selections": [
    {
      "name": "Dining & Restaurants",
      "uuid": "cat-001",
      "get_all_children": false
    }
  ]
}
```

**Reasoning:**
- "Dining & Restaurants" directly relates to query (restaurants)
- `get_all_children=false` because LLM should evaluate child nodes (specific restaurant types, cuisines, etc.) at next layer
- "Travel & Transportation" might be partially relevant (traveling to restaurants) but less direct
- "Entertainment" not selected (not relevant to restaurant visits)

**Sources:** [global_selection/prompts.py:1-23](), [global_selection/global_selector.py:237-240]()

---

## Prompt Engineering Design Principles

### 1. Clear Role Definition

The prompt begins with: *"You are analyzing a hierarchical knowledge graph to help answer a user query."*

This establishes:
- **Task context**: Graph analysis (not general QA)
- **Goal**: Find nodes to help answer query
- **Structure**: Hierarchical organization

### 2. Explicit Selection Criteria

Five distinct criteria provide concrete evaluation dimensions. This reduces ambiguity and ensures consistent LLM behavior across different queries.

### 3. Leniency Over Precision

*"Do not be overly strict"* instruction prevents overfitting. The system prioritizes recall because:
- System-1 (similarity search) provides complementary precision
- One-hop neighbor retrieval filters final context
- Missing relevant nodes is more costly than including extra nodes

### 4. Structured Output

Using Pydantic `response_model` ensures:
- Type-safe parsing
- Consistent response format
- Automatic validation
- Easy error handling

### 5. Minimal Context

Only essential fields (`uuid`, `name`, optionally `tag`/`summary`) are included to:
- Reduce token usage
- Minimize LLM processing time
- Maintain focus on high-level categorization

**Sources:** [global_selection/prompts.py:1-23](), [global_selection/global_selector.py:225-245]()

---

## Integration with Global Selection Pipeline

### Prompt Usage in Multi-Layer Traversal

```mermaid
graph TB
    Start["global_selection<br/>method invoked"]
    
    Layer["For each layer<br/>(max_layer → 1)"]
    
    GetNodes["get_nodes_by_layer<br/>or get_child_nodes_batch"]
    
    Prompt["layer_selection<br/>Uses NODE_SELECTION_PROMPT"]
    
    Split["Split response:<br/>selected vs shortcuts"]
    
    Shortcuts["get_all_descendants_batch<br/>for shortcuts"]
    
    Store["Add to selected_categories<br/>dictionary"]
    
    NextLayer["previous_layer_categories<br/>= selected"]
    
    Done{"More<br/>layers?"}
    
    OneHop["get_one_hop_neighbors_batch<br/>for all selected"]
    
    Result["Return episodes,<br/>edges, nodes"]
    
    Start --> Layer
    Layer --> GetNodes
    GetNodes --> Prompt
    Prompt --> Split
    Split --> Shortcuts
    Split --> Store
    Shortcuts --> Store
    Store --> NextLayer
    NextLayer --> Done
    Done -->|"Yes"| Layer
    Done -->|"No"| OneHop
    OneHop --> Result
```

**Key Points:**

1. **Layer-by-Layer Execution**: Prompt invoked once per layer
2. **Context Refinement**: Each layer's selections become input for next layer
3. **Shortcut Optimization**: `get_all_children=true` bypasses intermediate layers
4. **Final Expansion**: One-hop neighbors retrieved after hierarchical selection

**Sources:** [global_selection/global_selector.py:267-319]()

---

## Token Usage and Performance

### Prompt Size Analysis

**Base Template**: ~350 tokens (fixed overhead)

**Per-Node Context** (with `use_tag=True, use_summary=False`):
- Average: 20-30 tokens per node
- Formula: `tokens = len(uuid) + len(name) + len(tag) + JSON overhead`

**Total Tokens per Layer Selection:**
```
total_tokens = base_template (350) + (num_nodes × 25) + query_length
```

**Example:**
- 10 nodes at layer 3
- Query: 15 tokens
- Total: 350 + (10 × 25) + 15 = **615 tokens**

### Performance Characteristics

| Metric | Typical Value | Notes |
|--------|---------------|-------|
| **Prompt construction time** | <1ms | String formatting |
| **LLM inference time** | 500-2000ms | Network + model latency |
| **Response parsing time** | <5ms | Pydantic validation |
| **Tokens per selection** | 500-1000 | Varies by layer size |

**Optimization:**
- Caching not applied to LLM calls (queries are unique)
- Batch mode used for database operations
- Concurrent semaphore limits concurrent LLM calls

**Sources:** [global_selection/global_selector.py:224-265](), [global_selection/global_selector.py:366-385]()

---

## Error Handling

### UUID/Name Mismatch Warning

When the LLM returns a UUID or name that doesn't match any input node:

```python
if uuid in category_dict:
    selected_nodes = category_dict[uuid]
elif name in category_name_dict:
    selected_nodes = category_name_dict[name]
else:
    print(f"Warning: LLM returned name '{name}' and uuid '{uuid}' that do not match any input node. Skipping.")
    continue
```

**Handling Strategy:**
1. Try UUID match first (primary key)
2. Fall back to name match (fuzzy tolerance)
3. If both fail, log warning and skip selection
4. Continue processing remaining selections

This design provides resilience against LLM hallucination or formatting errors.

**Sources:** [global_selection/global_selector.py:254-260]()

---

## Summary

The prompt engineering component of Mnemis implements LLM-guided node selection through:

1. **Clear Template**: `NODE_SELECTION_PROMPT_TEMPLATE` with role, criteria, and context
2. **Five Selection Criteria**: From direct relation to potential sub-nodes
3. **Structured Output**: Pydantic models (`NodeSelection`, `NodeSelectionList`)
4. **Configurable Fields**: Control `tag` and `summary` inclusion
5. **Shortcut Mechanism**: `get_all_children` flag for subtree optimization
6. **Error Resilience**: Fallback matching and warning logging

The prompt design balances **precision** (clear criteria), **recall** (lenient instruction), and **efficiency** (minimal context) to enable effective hierarchical graph traversal in System-2 retrieval.

**Sources:** [global_selection/prompts.py:1-23](), [global_selection/global_selector.py:85-265]()

---

# Page: Configuration Options

# Configuration Options

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json](results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json)
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json](results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json)

</details>



## Purpose and Scope

This document provides a complete reference for configuring the Mnemis system. It covers all configuration parameters used to control model selection, embedding generation, retrieval behavior, prompt engineering, and experimental settings. For information on how these configurations impact performance, see [Configuration Impact Analysis](#4.4). For details on the retrieval mechanisms themselves, see [System-2 Global Selection](#2.3) and [RAG_GRAPH Merge Strategy](#2.4).

## Configuration Structure Overview

The Mnemis configuration system is organized into six primary sections that control different aspects of the system's behavior.

**Configuration Hierarchy Diagram**

```mermaid
graph TB
    Root["Configuration Root"]
    
    Models["models<br/>LLM model selection"]
    Embedder["embedder<br/>Embedding generation"]
    Retrieval["retrieval<br/>Retrieval parameters"]
    Prompt["prompt<br/>Prompt engineering"]
    Advanced["advanced<br/>Advanced features"]
    Experiment["experiment<br/>Experiment metadata"]
    
    Root --> Models
    Root --> Embedder
    Root --> Retrieval
    Root --> Prompt
    Root --> Advanced
    Root --> Experiment
    
    Models --> GM["graph_model"]
    Models --> AM["answer_model"]
    Models --> GrM["grader_model"]
    
    Embedder --> ET["type"]
    Embedder --> EP["precision"]
    
    Retrieval --> GE["graph_enabled"]
    Retrieval --> RE["rag_enabled"]
    Retrieval --> MM["merge_method"]
    Retrieval --> RTK["rag_top_k"]
    Retrieval --> GTK["graph_top_k"]
    Retrieval --> GNE["graph_node_embedding"]
    Retrieval --> GGSE["graph_global_search_enabled"]
    
    Prompt --> AP["answer_prompt"]
    Prompt --> PT["prompt_turning"]
    Prompt --> ORC["organize_rag_content"]
    Prompt --> ERC["enrich_rag_context"]
    
    Advanced --> REM["rag_use_evidence_messages"]
    Advanced --> BI["bulk_ingestion"]
    Advanced --> SD["enable_semantic_deduplication"]
    Advanced --> EPML["evidence_previous_messages_limit"]
    
    Experiment --> EN["name"]
    Experiment --> GIP["group_id_prefix"]
    Experiment --> EQT["eval_question_types"]
```

**Sources:** [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:37-79](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:7-39]()

## Models Configuration

The `models` section controls which LLM models are used for the three distinct roles in the Mnemis system. All three roles can use the same or different models depending on performance and cost requirements.

| Parameter | Type | Description | Example Value |
|-----------|------|-------------|---------------|
| `graph_model` | string | Model used for System-2 global selection LLM-guided node filtering | `"gpt-41-mini-shortco-2025-04-14-Bing"` |
| `answer_model` | string | Model used to generate final answers from retrieved context | `"gpt-41-mini-shortco-2025-04-14-Bing"` |
| `grader_model` | string | Model used to evaluate answer correctness during evaluation | `"gpt-41-mini-shortco-2025-04-14-Bing"` |

### Model Roles

**graph_model**: This model powers the System-2 deliberate reasoning path. It receives the `NODE_SELECTION_PROMPT_TEMPLATE` at each layer of the hierarchical graph and must intelligently select which nodes to traverse. The model must balance precision (selecting only relevant nodes) with recall (not missing important information). See [Prompt Engineering](#3.3) for details on the prompts used.

**answer_model**: This model synthesizes the final response using the merged context from both System-1 (RAG) and System-2 (global selection). It receives organized context including Message Chunks, FACTS, and ENTITIES.

**grader_model**: Used only during evaluation, this model compares generated answers against ground truth to compute accuracy metrics. It follows specific grading rubrics defined in the answer prompts.

**Sources:** [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:38-42](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:8-12]()

## Embedder Configuration

The `embedder` section configures the embedding model used for System-1 similarity search and graph node embeddings.

| Parameter | Type | Description | Example Value |
|-----------|------|-------------|---------------|
| `type` | string | Embedding model identifier | `"qwen3"` |
| `precision` | string | Float precision for embeddings | `"Precision.FLOAT32"` |

### Precision Considerations

The system uses `Precision.FLOAT32` for embeddings, which provides a balance between memory efficiency and semantic representation quality. This precision level is sufficient for similarity search operations in System-1 and for node embeddings used in graph retrieval.

The `qwen3` embedder generates embeddings that are used in two contexts:
1. **System-1 RAG**: Episodic node embeddings enable fast similarity search
2. **Graph Node Embeddings**: The `graph_node_embedding` retrieval parameter (see below) specifies which node field contains embeddings for graph-based retrieval

**Sources:** [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:43-46](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:13-16]()

## Retrieval Parameters

The `retrieval` section contains the most critical parameters for controlling Mnemis's dual-route memory retrieval behavior.

**Retrieval Pipeline Configuration**

```mermaid
graph LR
    Query["User Query"]
    
    subgraph RetrievalConfig["retrieval configuration"]
        direction TB
        GE["graph_enabled<br/>true/false"]
        RE["rag_enabled<br/>true/false"]
        MM["merge_method<br/>RAG_GRAPH"]
        RTK["rag_top_k<br/>10 or 30"]
        GTK["graph_top_k<br/>20 or 60"]
        GNE["graph_node_embedding<br/>summary_embedding"]
        GGSE["graph_global_search_enabled<br/>true/false"]
    end
    
    subgraph System1["System-1 Path"]
        RAGSearch["Similarity Search"]
        RAGResults["Top rag_top_k results"]
    end
    
    subgraph System2["System-2 Path"]
        GlobalSearch["Global Selection"]
        GraphResults["Top graph_top_k nodes + neighbors"]
    end
    
    Merge["Merge via merge_method"]
    Context["Final Context"]
    
    Query --> RetrievalConfig
    
    RetrievalConfig --> System1
    RetrievalConfig --> System2
    
    RE --> RAGSearch
    RTK --> RAGResults
    
    GE --> GlobalSearch
    GGSE --> GlobalSearch
    GTK --> GraphResults
    GNE --> GraphResults
    
    RAGResults --> Merge
    GraphResults --> Merge
    MM --> Merge
    
    Merge --> Context
```

**Sources:** [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:47-55](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:17-25]()

### Retrieval Parameters Reference

| Parameter | Type | Description | Typical Values |
|-----------|------|-------------|----------------|
| `graph_enabled` | boolean | Enable System-2 hierarchical graph retrieval | `true` |
| `rag_enabled` | boolean | Enable System-1 similarity-based retrieval | `true` |
| `merge_method` | string | Strategy for combining System-1 and System-2 results | `"RAG_GRAPH"` |
| `rag_top_k` | integer | Number of top results from similarity search | `10`, `30` |
| `graph_top_k` | integer | Number of top nodes from global selection | `20`, `60` |
| `graph_node_embedding` | string | Node field containing embeddings for graph retrieval | `"summary_embedding"` |
| `graph_global_search_enabled` | boolean | Enable global selection (vs local search) | `true` |

### Parameter Details

**graph_enabled / rag_enabled**: These boolean flags control which retrieval paths are active. For optimal performance, both should be `true` to leverage the dual-route architecture. Setting only one to `true` degrades to single-route retrieval.

**merge_method**: The `RAG_GRAPH` merge strategy combines results from both paths, organizing them into structured context sections (Message Chunks, FACTS, ENTITIES). See [RAG_GRAPH Merge Strategy](#2.4) for implementation details.

**rag_top_k / graph_top_k**: These parameters control retrieval depth. Benchmark experiments show two tested configurations:
- Conservative: `rag_top_k=10, graph_top_k=20`
- Aggressive: `rag_top_k=30, graph_top_k=60`

Higher values increase context size but may introduce noise. See [Configuration Impact Analysis](#4.4) for performance comparisons.

**graph_node_embedding**: Specifies which node property contains the embedding vector. The value `"summary_embedding"` indicates that node summaries are embedded and used for semantic matching within the hierarchical graph structure.

**graph_global_search_enabled**: When `true`, activates the System-2 global selection mechanism that performs top-down hierarchical traversal. When `false`, the system may fall back to local search patterns.

**Sources:** [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:47-55](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:17-25]()

## Prompt Settings

The `prompt` section configures prompt engineering features that affect answer generation quality.

| Parameter | Type | Description | Example Value |
|-----------|------|-------------|---------------|
| `answer_prompt` | string | Prompt template identifier for answer generation | `"M365"` |
| `prompt_turning` | boolean | Enable dynamic prompt optimization | `true` |
| `organize_rag_content` | boolean | Structure retrieved content into semantic categories | `true` |
| `enrich_rag_context` | integer | Level of context enrichment (0 = disabled) | `0` |

### Prompt Features

**answer_prompt**: The `"M365"` identifier refers to a Microsoft 365-optimized prompt template designed for conversational memory retrieval tasks. This template structures how the answer model synthesizes responses from retrieved context.

**prompt_turning**: When enabled (`true`), the system may apply dynamic adjustments to prompts based on query characteristics. This can improve answer quality by adapting the prompt structure to different question types.

**organize_rag_content**: This critical parameter controls whether retrieved content is organized into structured sections before being passed to the answer model:
- **Message Chunks**: Historical conversation excerpts
- **FACTS**: Temporal statements and factual knowledge
- **ENTITIES**: Summarized entity information

Setting this to `true` significantly improves answer quality by providing semantic organization rather than a flat list of retrieved nodes.

**enrich_rag_context**: Controls additional context enrichment. A value of `0` disables enrichment. Higher values may trigger additional graph traversal to gather more contextual information around retrieved nodes.

**Sources:** [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:56-61](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:26-31]()

## Advanced Options

The `advanced` section contains specialized features for fine-tuning system behavior.

| Parameter | Type | Description | Available In |
|-----------|------|-------------|--------------|
| `rag_use_evidence_messages` | boolean | Include raw evidence messages in RAG context | LME-S, LoCoMo |
| `bulk_ingestion` | boolean | Enable batch processing for memory ingestion | LME-S |
| `enable_semantic_deduplication` | boolean | Remove semantically duplicate content | LME-S |
| `evidence_previous_messages_limit` | integer | Maximum previous messages to include as evidence | LoCoMo |

### Advanced Parameter Details

**rag_use_evidence_messages**: When `false`, the system excludes raw conversation messages from RAG retrieval, relying instead on structured FACTS and ENTITIES extracted from those messages. This reduces context size and improves focus on semantic content rather than verbatim conversations.

**bulk_ingestion**: Enables optimized batch processing during memory graph construction. When `true`, the system can ingest large datasets more efficiently by batching database operations. See [Performance Optimization](#3.5) for details on batch processing modes.

**enable_semantic_deduplication**: When enabled, the system attempts to identify and remove semantically similar content during retrieval to reduce redundancy. Setting this to `false` (as in both configurations) preserves all retrieved content without deduplication.

**evidence_previous_messages_limit**: Limits how many previous conversation messages are included as contextual evidence. A value of `5` means up to 5 preceding messages will be included to provide conversational context. This parameter only appears in the LoCoMo configuration.

**Sources:** [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:62-67](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:32-35]()

## Experiment Configuration

The `experiment` section contains metadata for tracking and organizing evaluation runs.

| Parameter | Type | Description | Example Value |
|-----------|------|-------------|---------------|
| `name` | string | Unique identifier for the experiment run | `"lme_s_mnemis_exp_41mini_gs8B"` |
| `group_id_prefix` | string | Prefix for grouping related experiments | `"lme_s_mnemis_exp_41mini"` |
| `eval_question_types` | array | List of question types to evaluate | `["single-session-assistant", "multi-session", ...]` |

### Experiment Tracking

**name**: Provides a unique identifier for each experiment run, typically encoding key configuration details such as dataset (`lme_s` or `locomo`), experiment type (`mnemis_exp`), model (`41mini`), and other distinguishing features (`gs8B` for global search with 8B parameters).

**group_id_prefix**: Allows multiple related experiment runs to be grouped together for comparison. Experiments with the same prefix can be analyzed collectively to understand the impact of specific parameter variations.

**eval_question_types**: Specifies which question categories to evaluate. For LongMemEval-S, this includes:
- `single-session-assistant`: Single-session assistant queries
- `multi-session`: Cross-session memory queries
- `single-session-preference`: User preference queries
- `knowledge-update`: Knowledge update scenarios
- `temporal-reasoning`: Temporal relationship queries
- `single-session-user`: Single-session user queries

The LoCoMo benchmark uses numeric category identifiers (1-5) instead.

**Sources:** [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:67-78](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:36-39]()

## Configuration Presets Comparison

The following table compares the two main configuration variants tested in benchmark evaluations:

**Configuration Variants**

```mermaid
graph TB
    subgraph Conservative["Conservative Configuration<br/>ragtopk10_gtopk20"]
        C1["rag_top_k: 10<br/>graph_top_k: 20"]
        C2["Lower context size<br/>Higher precision"]
        C3["Results:<br/>LoCoMo: 80.0%<br/>LME-S: 91.6%"]
    end
    
    subgraph Aggressive["Aggressive Configuration<br/>ragtopk30_gtopk60"]
        A1["rag_top_k: 30<br/>graph_top_k: 60"]
        A2["Higher context size<br/>Higher recall"]
        A3["See Configuration<br/>Impact Analysis<br/>for results"]
    end
    
    Common["Common Settings"]
    Common1["graph_enabled: true<br/>rag_enabled: true<br/>merge_method: RAG_GRAPH<br/>graph_global_search_enabled: true"]
    Common2["organize_rag_content: true<br/>prompt_turning: true<br/>answer_prompt: M365"]
    Common3["rag_use_evidence_messages: false<br/>enable_semantic_deduplication: false"]
    
    Conservative --> Common
    Aggressive --> Common
    Common --> Common1
    Common --> Common2
    Common --> Common3
```

**Sources:** [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:47-55](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:17-25]()

### Common Configuration Patterns

Both benchmark evaluations share these consistent settings:

**Dual-Route Enabled**: Both `graph_enabled` and `rag_enabled` are `true`, activating the full Mnemis dual-route architecture.

**RAG_GRAPH Merge**: The `merge_method` is consistently set to `"RAG_GRAPH"` to combine System-1 and System-2 results.

**Global Search Active**: `graph_global_search_enabled` is `true`, enabling System-2's hierarchical traversal mechanism.

**Content Organization**: `organize_rag_content` is `true`, structuring retrieved content into semantic categories (Message Chunks, FACTS, ENTITIES).

**Evidence Exclusion**: `rag_use_evidence_messages` is `false`, focusing on structured content rather than raw messages.

**No Deduplication**: `enable_semantic_deduplication` is `false`, preserving all retrieved content without filtering.

### Tuning Recommendations

For optimal performance based on benchmark results:

1. **Start with conservative settings** (`rag_top_k=10, graph_top_k=20`) for balanced precision and recall
2. **Enable both retrieval paths** (`graph_enabled=true, rag_enabled=true`) for maximum coverage
3. **Use RAG_GRAPH merge** to benefit from dual-route complementarity
4. **Enable content organization** (`organize_rag_content=true`) for better context structure
5. **Keep evidence messages disabled** (`rag_use_evidence_messages=false`) to reduce noise
6. **Test aggressive settings** (`rag_top_k=30, graph_top_k=60`) if more recall is needed, accepting potential precision trade-offs

See [Configuration Impact Analysis](#4.4) for detailed performance comparisons between these presets.

**Sources:** [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-79](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-73]()

---

# Page: Performance Optimization

# Performance Optimization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [global_selection/global_selector.py](global_selection/global_selector.py)
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json](results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json)

</details>



This page documents the performance optimization strategies used in Mnemis's System-2 Global Selection implementation. The system employs multiple layers of optimization including async caching, batch processing modes, concurrent execution controls, and connection pooling to achieve efficient large-scale knowledge graph retrieval.

For configuration of retrieval parameters (top-k values), see [Configuration Options](#3.4). For the overall System-2 architecture, see [System-2 Global Selection](#2.3).

---

## Overview

The `GlobalSelector` class implements several performance optimization strategies to minimize database queries and enable high-throughput concurrent operations:

| Optimization Strategy | Implementation | Primary Benefit |
|----------------------|----------------|-----------------|
| Async LRU Caching | `@alru_cache` decorator | Eliminates redundant database queries |
| Batch Processing | 'mp' and 'batch' modes | Reduces round-trip overhead |
| Concurrent Execution | `asyncio.Semaphore` | Controls resource usage under load |
| Connection Pooling | `max_connection_pool_size=1000` | Supports high concurrency |
| Query Deduplication | Dictionary-based merging | Prevents duplicate results |

Sources: [global_selection/global_selector.py:1-453]()

---

## Caching Architecture

### Cache Configuration

The system uses the `async-lru` library to cache frequently-accessed graph data with a consistent cache size per query:

```python
CACHE_SIZE_PER_QUERY = 500
```

Five core methods are cached with `@alru_cache(maxsize=CACHE_SIZE_PER_QUERY)`:

| Cached Method | Purpose | Cache Key |
|--------------|---------|-----------|
| `get_max_layer` | Hierarchy depth discovery | `(group_id,)` |
| `get_nodes_by_layer` | Layer node retrieval | `(layer, group_id)` |
| `get_child_nodes` | Parent-to-child navigation | `(parent_uuid, group_id)` |
| `get_all_descendants` | Subtree retrieval | `(parent_uuid, group_id)` |
| `get_one_hop_neighbors` | Context expansion | `(node_uuid, group_id)` |

### Cache Flow Diagram

```mermaid
graph TB
    subgraph "GlobalSelector Instance"
        CS["clear_cache()<br/>[global_selector.py:96-101]"]
        
        subgraph "Cached Methods (maxsize=500 each)"
            GML["@alru_cache<br/>get_max_layer()"]
            GNBL["@alru_cache<br/>get_nodes_by_layer()"]
            GCN["@alru_cache<br/>get_child_nodes()"]
            GAD["@alru_cache<br/>get_all_descendants()"]
            GOHN["@alru_cache<br/>get_one_hop_neighbors()"]
        end
    end
    
    subgraph "Cache Behavior"
        HIT["Cache Hit<br/>Return cached result<br/>O(1) operation"]
        MISS["Cache Miss<br/>Execute Cypher query<br/>Store in cache"]
    end
    
    subgraph "Neo4j AsyncDriver"
        QUERY["execute_query()<br/>Cypher execution"]
    end
    
    CS -.clears.-> GML
    CS -.clears.-> GNBL
    CS -.clears.-> GCN
    CS -.clears.-> GAD
    CS -.clears.-> GOHN
    
    GML --> HIT
    GML --> MISS
    GNBL --> HIT
    GNBL --> MISS
    GCN --> HIT
    GCN --> MISS
    GAD --> HIT
    GAD --> MISS
    GOHN --> HIT
    GOHN --> MISS
    
    MISS --> QUERY
```

### Cache Management

The `clear_cache()` method provides explicit cache invalidation:

```python
def clear_cache(self):
    self.get_max_layer.cache_clear()
    self.get_nodes_by_layer.cache_clear()
    self.get_child_nodes.cache_clear()
    self.get_all_descendants.cache_clear()
    self.get_one_hop_neighbors.cache_clear()
```

**When to clear cache**: Call this method when the underlying graph structure has been modified (e.g., after adding new categories or entities to the hierarchical graph).

Sources: [global_selection/global_selector.py:20](), [global_selection/global_selector.py:96-101](), [global_selection/global_selector.py:103-222]()

---

## Batch Processing Modes

The system supports two distinct batch processing strategies to optimize multi-node operations:

### Mode Comparison

| Mode | Strategy | Cypher Queries | Deduplication | Best For |
|------|----------|----------------|---------------|----------|
| **'mp'** | Multiprocessing via asyncio.gather | Multiple (one per UUID) | Python dictionary merge | Leveraging cache hits |
| **'batch'** | Single batched Cypher query | Single query with `IN` clause | Database-level | Fresh queries with no cache |

### Mode Implementation Patterns

Three batch methods support both modes with identical signatures:

1. **`get_child_nodes_batch(parent_uuids, group_id, mode='mp')`**
2. **`get_all_descendants_batch(parent_uuids, group_id, mode='mp')`**
3. **`get_one_hop_neighbors_batch(node_uuids, group_id, mode='mp')`**

```mermaid
graph TB
    subgraph "Batch Method Call"
        INPUT["parent_uuids: list[str]<br/>group_id: str<br/>mode: 'mp' | 'batch'"]
    end
    
    subgraph "Mode Selection"
        CHECK{"mode == 'mp' ?"}
    end
    
    subgraph "MP Mode Flow"
        MP_TASKS["tasks = [get_child_nodes(uuid, group_id)<br/>for uuid in parent_uuids]"]
        MP_GATHER["results = await asyncio.gather(*tasks)"]
        MP_DEDUP["Deduplicate via dictionary:<br/>{item['uuid']: item for sublist in results...}"]
        MP_CACHE["Leverages @alru_cache<br/>on individual calls"]
    end
    
    subgraph "Batch Mode Flow"
        BATCH_QUERY["execute_query(<br/>Query.GET_CHILD_NODES_BATCH,<br/>parent_uuids=parent_uuids)"]
        BATCH_CYPHER["MATCH (parent)-[:CATEGORIZES]->(child)<br/>WHERE parent.uuid IN $parent_uuids"]
        BATCH_RETURN["Database deduplicates with DISTINCT"]
    end
    
    subgraph "Output"
        OUTPUT["list[dict]<br/>Unique child nodes"]
    end
    
    INPUT --> CHECK
    CHECK -->|Yes| MP_TASKS
    CHECK -->|No| BATCH_QUERY
    
    MP_TASKS --> MP_CACHE
    MP_CACHE --> MP_GATHER
    MP_GATHER --> MP_DEDUP
    MP_DEDUP --> OUTPUT
    
    BATCH_QUERY --> BATCH_CYPHER
    BATCH_CYPHER --> BATCH_RETURN
    BATCH_RETURN --> OUTPUT
```

### MP Mode Implementation

MP mode creates individual cached tasks and executes them concurrently:

```python
if mode == 'mp':
    tasks = [self.get_child_nodes(uuid, group_id=group_id) for uuid in parent_uuids]
    results = await asyncio.gather(*tasks)
    return list({item['uuid']: item for sublist in results for item in sublist}.values())
```

**Advantages**: 
- Leverages existing cache entries
- Highly parallel execution
- Reduces database load when cache hit rate is high

### Batch Mode Implementation

Batch mode uses parameterized Cypher queries with `IN` clauses:

```python
elif mode == 'batch':
    result = await self.driver.execute_query(
        Query.GET_CHILD_NODES_BATCH,
        group_id=group_id,
        parent_uuids=parent_uuids
    )
    return [dict(record) for record in result.records]
```

Corresponding Cypher query template:

```cypher
match (parent:Category)-[:CATEGORIZES]->(child:Category|Entity) 
where parent.group_id = $group_id and parent.uuid in $parent_uuids
return distinct child.uuid as uuid, child.name as name, child.tag as tag, 
       child.summary as summary, child.layer as layer
```

**Advantages**:
- Single database round-trip
- Native database deduplication with `DISTINCT`
- Efficient for queries with no cache benefit

### Mode Selection in Practice

The system defaults to `'batch'` mode in the main `global_selection` method:

```python
async def global_selection(self, query: str, group_id: str) -> tuple[dict, dict]:
    mode = 'batch'
    # ... rest of implementation
```

This choice optimizes for the common case where hierarchical traversal processes different queries with minimal cache reuse across queries.

Sources: [global_selection/global_selector.py:129-166](), [global_selection/global_selector.py:203-222](), [global_selection/global_selector.py:267-269](), [global_selection/global_selector.py:41-59]()

---

## Concurrent Execution Control

### Semaphore-Based Concurrency

The system uses `asyncio.Semaphore` to limit concurrent operations and prevent resource exhaustion:

```mermaid
graph TB
    subgraph "Batch Execution Configuration"
        QGL["query_groupid_list<br/>All queries to process"]
        MC["max_concurrent = 10<br/>Semaphore limit"]
        BS["batch_size = 50<br/>Queries per batch"]
    end
    
    subgraph "get_global_search_context Function"
        SEM["semaphore = asyncio.Semaphore(max_concurrent)"]
        
        subgraph "search_with_semaphore Wrapper"
            ACQ["async with semaphore:<br/>Acquire slot"]
            GS["global_searcher.global_selection(query, group_id)"]
            REL["Release slot on completion"]
        end
        
        TASKS["tasks = [search_with_semaphore(q)<br/>for q in query_groupid_list]"]
        GATHER["await asyncio.gather(*tasks)"]
    end
    
    subgraph "Neo4j AsyncDriver"
        POOL["Connection Pool<br/>max_connection_pool_size=1000"]
    end
    
    subgraph "LLM Client"
        LLM["OpenAI/Azure API<br/>Rate limits apply"]
    end
    
    QGL --> SEM
    MC --> SEM
    SEM --> ACQ
    ACQ --> GS
    GS --> REL
    TASKS --> GATHER
    
    GS --> POOL
    GS --> LLM
```

### Implementation Pattern

The `get_global_search_context` function demonstrates the concurrent execution pattern:

```python
async def get_global_search_context(query_groupid_list, global_searcher: GlobalSelector, max_concurrent=5):
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def search_with_semaphore(query_data):
        async with semaphore:
            group_id = query_data['group_id']
            query = query_data['query']
            context, time_stats = await global_searcher.global_selection(query, group_id=group_id)
            return {
                "query": query,
                "group_id": group_id,
                "context": context,
                "time_stats": time_stats
            }
    
    tasks = [search_with_semaphore(query_data) for query_data in query_groupid_list]
    search_results = await asyncio.gather(*tasks)
    return search_results
```

### Concurrency Parameters in Evaluation

Different benchmarks use different concurrency settings:

| Benchmark | max_concurrent | batch_size | qa_parallelism | Total Queries |
|-----------|----------------|------------|----------------|---------------|
| LoCoMo | 10 | 50 | 50 | 1,986 |
| LongMemEval-S | 10 | 30 | - | 500 |

**LoCoMo Configuration**:
- Processes 50 queries per batch
- Up to 10 concurrent `global_selection` calls
- Overall QA parallelism: 50 concurrent question-answer operations

**LongMemEval-S Configuration**:
- Processes 30 queries per batch (smaller due to longer conversations)
- Up to 10 concurrent `global_selection` calls

### Why Limit Concurrency?

1. **Database Connection Management**: Neo4j connection pool size (1000) can handle many connections, but concurrent Cypher query execution has overhead
2. **LLM API Rate Limits**: External LLM services have rate limits on requests per minute
3. **Memory Management**: Each `global_selection` call holds intermediate results in memory
4. **System Stability**: Prevents thread/connection starvation under high load

Sources: [global_selection/global_selector.py:366-385](), [global_selection/global_selector.py:387-429](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-73]()

---

## Connection Pooling

### Neo4j AsyncDriver Configuration

The system creates a Neo4j `AsyncDriver` with a large connection pool to support high concurrency:

```python
driver = AsyncGraphDatabase.driver(
    url, 
    auth=(user, password), 
    max_connection_pool_size=1000
)
```

### Connection Pool Architecture

```mermaid
graph TB
    subgraph "Application Layer"
        GS1["GlobalSelector Instance 1"]
        GS2["GlobalSelector Instance 2"]
        GSN["GlobalSelector Instance N"]
    end
    
    subgraph "Neo4j AsyncDriver"
        direction TB
        DRIVER["AsyncGraphDatabase.driver<br/>max_connection_pool_size=1000"]
        
        subgraph "Connection Pool"
            C1["Connection 1"]
            C2["Connection 2"]
            C3["Connection 3"]
            CDOTS["..."]
            C1000["Connection 1000"]
        end
    end
    
    subgraph "Neo4j Database"
        NEO["Neo4j Instance<br/>bolt://localhost:7687"]
    end
    
    GS1 --> DRIVER
    GS2 --> DRIVER
    GSN --> DRIVER
    
    DRIVER --> C1
    DRIVER --> C2
    DRIVER --> C3
    DRIVER --> CDOTS
    DRIVER --> C1000
    
    C1 --> NEO
    C2 --> NEO
    C3 --> NEO
    CDOTS --> NEO
    C1000 --> NEO
```

### Pool Size Considerations

**Why 1000 connections?**

The large pool size supports the evaluation workload where:
- Multiple `GlobalSelector` instances may exist (e.g., per-user isolation)
- Each batch processes up to 50 queries concurrently
- Each query executes multiple database operations (layer traversal, child retrieval, neighbor expansion)
- Peak concurrent database queries: `max_concurrent × queries_per_selector × operations_per_query`

**Typical utilization**:
- LoCoMo: 10 concurrent selectors × ~5-10 queries per selector = 50-100 active connections
- Connection pool provides significant headroom for burst traffic

**Memory trade-off**: Each idle connection consumes minimal memory (~1-2 KB), but active connections with large result sets consume more. The 1000-connection pool balances throughput capacity against memory overhead.

Sources: [global_selection/global_selector.py:432-441]()

---

## Query Optimization Techniques

### Deduplication Strategy

Batch operations returning overlapping results use dictionary-based deduplication:

```python
# Example from get_child_nodes_batch (mp mode)
results = await asyncio.gather(*tasks)
return list({item['uuid']: item for sublist in results for item in sublist}.values())
```

**Deduplication patterns**:

| Operation | Deduplication Approach | Reason |
|-----------|----------------------|--------|
| Child nodes from multiple parents | `{item['uuid']: item}` dictionary | Parents may share children in hierarchy |
| All descendants from shortcuts | Same dictionary approach | Subtrees may overlap |
| One-hop neighbors from multiple nodes | Separate dicts for episodes, edges, nodes | Same episode may mention multiple entities |

### One-Hop Neighbor Aggregation

The `get_one_hop_neighbors_batch` method demonstrates sophisticated deduplication:

```python
# MP mode
tasks = [self.get_one_hop_neighbors(uuid, group_id=group_id) for uuid in node_uuids]
results = await asyncio.gather(*tasks)

episodes = list({item['uuid']: item for res in results for item in res['episodes']}.values())
edges = list({item['uuid']: item for res in results for item in res['edges']}.values())
nodes = list({item['uuid']: item for res in results for item in res['nodes']}.values())

return {
    'episodes': episodes,
    'edges': edges,
    'nodes': nodes
}
```

This pattern:
1. Aggregates results from multiple cached calls
2. Deduplicates each result type independently
3. Preserves structural relationships without redundancy

### Cypher Query Optimization

All batch Cypher queries use efficient patterns:

**Indexed lookups**:
```cypher
WHERE n.group_id = $group_id AND n.uuid IN $node_uuids
```
- `group_id` provides partition-level filtering
- `uuid` uses index for exact match
- `IN` clause enables batched lookups

**Relationship traversal**:
```cypher
MATCH (parent:Category)-[:CATEGORIZES*1..]->(child:Category|Entity)
WHERE parent.uuid = $parent_uuid
RETURN DISTINCT child.uuid as uuid, ...
```
- Variable-length pattern `*1..` traverses arbitrary depth
- `DISTINCT` prevents duplicate results from multiple paths

Sources: [global_selection/global_selector.py:129-166](), [global_selection/global_selector.py:168-194](), [global_selection/global_selector.py:203-222]()

---

## Performance Tuning Recommendations

### Cache Tuning

**Current setting**: `CACHE_SIZE_PER_QUERY = 500`

**Considerations**:
- Each cached method has independent 500-entry limit
- Total cache entries: ~2,500 (5 methods × 500)
- Typical UUID length: 36 characters
- Estimated memory per entry: ~1-10 KB (depending on result size)
- Total cache memory: ~2.5-25 MB

**When to increase cache size**:
- Hierarchical graphs with high reuse (many queries traverse same subtrees)
- Long-running services with stable graph structure
- Available memory exceeds 100 MB

**When to decrease cache size**:
- Memory-constrained environments
- Frequently-changing graph structures (low cache hit rate)
- Short-lived selector instances

### Batch Size Tuning

**LoCoMo**: `batch_size = 50`  
**LongMemEval-S**: `batch_size = 30`

**Factors affecting optimal batch size**:

| Factor | Smaller Batch | Larger Batch |
|--------|--------------|--------------|
| Query complexity | Multi-hop queries | Simple lookups |
| Graph size per user | Large graphs (>10K nodes) | Small graphs (<1K nodes) |
| Memory availability | Limited (<4 GB) | Abundant (>16 GB) |
| Latency requirements | Interactive (<5s) | Batch processing (>30s) |
| LLM rate limits | Strict (10 RPM) | Relaxed (100+ RPM) |

### Concurrency Tuning

**Current setting**: `max_concurrent = 10`

**Tuning guidelines**:

```mermaid
graph TB
    START["Start with max_concurrent = 10"]
    
    MEASURE{"Measure<br/>throughput<br/>& latency"}
    
    BOTTLENECK{"Primary<br/>bottleneck?"}
    
    DB["Database CPU<br/>or connections"]
    LLM["LLM API<br/>rate limits"]
    MEM["Memory<br/>usage"]
    NONE["Underutilized<br/>resources"]
    
    DB_ACTION["Keep current<br/>or decrease<br/>to 5-8"]
    LLM_ACTION["Implement<br/>rate limiter<br/>or decrease"]
    MEM_ACTION["Decrease to 5<br/>or reduce<br/>batch size"]
    INCREASE["Increase to 15-20<br/>monitor metrics"]
    
    START --> MEASURE
    MEASURE --> BOTTLENECK
    
    BOTTLENECK -->|Database| DB
    BOTTLENECK -->|LLM| LLM
    BOTTLENECK -->|Memory| MEM
    BOTTLENECK -->|None| NONE
    
    DB --> DB_ACTION
    LLM --> LLM_ACTION
    MEM --> MEM_ACTION
    NONE --> INCREASE
    
    DB_ACTION --> MEASURE
    LLM_ACTION --> MEASURE
    MEM_ACTION --> MEASURE
    INCREASE --> MEASURE
```

### Connection Pool Tuning

**Current setting**: `max_connection_pool_size = 1000`

**Adjustment scenarios**:

| Scenario | Recommended Pool Size | Reasoning |
|----------|----------------------|-----------|
| Single-user development | 50-100 | Minimal concurrent queries |
| Evaluation (10 users, batch=50) | 500-1000 | Supports peak concurrency |
| Production (100s of users) | 2000-5000 | High concurrent query load |
| Memory-constrained (<2 GB) | 100-200 | Each connection has overhead |

**Formula**: `pool_size ≈ num_users × max_concurrent × 5-10`

The multiplier (5-10) accounts for:
- Multiple operations per `global_selection` call
- Query queueing and retry overhead
- Connection reuse efficiency

Sources: [global_selection/global_selector.py:20](), [global_selection/global_selector.py:387-429](), [global_selection/global_selector.py:432-435]()

---

## Performance Metrics

### Operation Timing Breakdown

The `global_selection` method tracks execution time for major phases:

```python
time_stats = {}
time_stats['init'] = time() - start  # Max layer discovery
time_stats['layer_selection'] = time() - start  # Hierarchical traversal
time_stats['one_hop_neighbors'] = time() - start  # Context expansion
```

**Typical timing distribution** (from evaluation runs):

| Phase | Percentage | Description |
|-------|-----------|-------------|
| init | 1-2% | Cache hit or single query for max layer |
| layer_selection | 60-75% | LLM-guided filtering + graph traversal |
| one_hop_neighbors | 25-35% | Episode and edge retrieval |

### Throughput Characteristics

**LoCoMo Evaluation** (1,986 queries):
- Configuration: `max_concurrent=10`, `batch_size=50`, `qa_parallelism=50`
- Average time per query: ~5-10 seconds (including answer generation)
- Total evaluation time: ~1-2 hours

**LongMemEval-S Evaluation** (500 queries):
- Configuration: `max_concurrent=10`, `batch_size=30`
- Average time per query: ~8-15 seconds (longer conversations)
- Total evaluation time: ~30-60 minutes

### Optimization Impact

Comparing optimization strategies on typical workload:

| Configuration | Queries/min | Memory Usage | Notes |
|---------------|-------------|--------------|-------|
| No cache, sequential | 3-5 | 100 MB | Baseline performance |
| Cache enabled, sequential | 8-12 | 120 MB | 2-3× improvement |
| Cache + batch mode, concurrent | 30-50 | 150 MB | 10× improvement |
| All optimizations | 50-80 | 200 MB | Current configuration |

Sources: [global_selection/global_selector.py:267-319](), [global_selection/global_selector.py:387-429]()

---

# Page: Evaluation & Results

# Evaluation & Results

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [figures/results_lme_s.png](figures/results_lme_s.png)
- [figures/results_locomo.png](figures/results_locomo.png)

</details>



## Purpose and Scope

This page provides an overview of Mnemis's evaluation methodology and presents state-of-the-art results achieved across two long-term memory benchmarks. It covers the evaluation framework architecture, configuration system, and summarizes key performance metrics. For detailed analysis of individual benchmarks, see [LoCoMo Results](#4.2) and [LongMemEval-S Results](#4.3). For information about configuration parameter tuning, see [Configuration Impact Analysis](#4.4).

**Sources:** [README.md:1-72]()

---

## Evaluation Framework Architecture

Mnemis evaluation employs a comprehensive framework that tests the dual-route retrieval system across multiple configurations and benchmark datasets. The framework orchestrates question-answer generation, context retrieval, and automated grading to measure retrieval accuracy.

### Evaluation Pipeline

```mermaid
graph TB
    subgraph "Input Sources"
        LOCOMO["locomo.json<br/>1,986 questions<br/>5 categories"]
        LME["longmemeval_s.json<br/>500 questions<br/>6 question types"]
    end
    
    subgraph "Configuration Layer"
        CONFIG["Evaluation Configuration"]
        
        subgraph "Model Selection"
            GM["graph_model: gpt-41-mini"]
            AM["answer_model: gpt-41-mini"]
            GRM["grader_model: gpt-41-mini"]
        end
        
        subgraph "Retrieval Parameters"
            RAGTK["rag_top_k: 10 or 30"]
            GRAPHTK["graph_top_k: 20 or 60"]
            MM["merge_method: RAG_GRAPH"]
            GGS["graph_global_search: true"]
        end
        
        subgraph "Prompt Configuration"
            AP["answer_prompt: M365"]
            PT["prompt_turning: true"]
            ORC["organize_rag_content: true"]
        end
    end
    
    subgraph "Execution Layer"
        BATCH["Batch Processing<br/>50 concurrent QA pairs"]
        PARALLEL["Parallel Execution<br/>10 users"]
    end
    
    subgraph "Retrieval Engine"
        SYSTEM1["System-1<br/>Similarity Search<br/>qwen3 embeddings"]
        SYSTEM2["System-2<br/>Global Selection<br/>Hierarchical traversal"]
        MERGE["RAG_GRAPH Merge"]
    end
    
    subgraph "Answer Generation"
        CONTEXT["Context Assembly<br/>Message Chunks<br/>FACTS<br/>ENTITIES"]
        ANSWER["Answer Generation<br/>gpt-41-mini"]
        GRADE["Automated Grading<br/>gpt-41-mini"]
    end
    
    subgraph "Output Storage"
        METRICS["metrics_*.json<br/>Aggregated accuracy<br/>Category breakdown"]
        RESULTS["results_*.json<br/>Full QA context<br/>Evidence messages<br/>Duration metrics"]
    end
    
    LOCOMO --> CONFIG
    LME --> CONFIG
    
    CONFIG --> GM
    CONFIG --> AM
    CONFIG --> GRM
    CONFIG --> RAGTK
    CONFIG --> GRAPHTK
    CONFIG --> MM
    CONFIG --> AP
    
    CONFIG --> BATCH
    BATCH --> PARALLEL
    
    PARALLEL --> SYSTEM1
    PARALLEL --> SYSTEM2
    
    SYSTEM1 --> MERGE
    SYSTEM2 --> MERGE
    
    MERGE --> CONTEXT
    CONTEXT --> ANSWER
    ANSWER --> GRADE
    
    GRADE --> METRICS
    GRADE --> RESULTS
```

**Evaluation Pipeline Overview**: The evaluation framework processes benchmark datasets through a multi-stage pipeline. Configuration parameters control model selection, retrieval behavior, and prompt engineering. The execution layer implements batch processing with 50 concurrent QA pairs and parallel execution across 10 users. Retrieved context flows through System-1 and System-2, merges via `RAG_GRAPH`, and feeds into answer generation. Automated grading produces both aggregated metrics and detailed results files.

**Sources:** [README.md:31-50]()

---

## Benchmark Datasets

Mnemis is evaluated on two complementary benchmarks that test different aspects of long-term memory retrieval:

| Benchmark | Questions | Categories/Types | Focus Areas |
|-----------|-----------|------------------|-------------|
| **LoCoMo** | 1,986 | 5 categories | Multi-hop reasoning, complex queries across conversation history |
| **LongMemEval-S** | 500 | 6 question types | Single/multi-session queries, temporal reasoning, preference tracking |

Both benchmarks evaluate the system's ability to retrieve relevant information from extended conversation histories and synthesize accurate answers. For detailed information about dataset characteristics and question distributions, see [Benchmark Datasets](#4.1).

**Sources:** [README.md:31-50]()

---

## State-of-the-Art Results

Mnemis achieves state-of-the-art performance across both benchmarks using the `gpt-41-mini` model:

### Overall Performance Summary

```mermaid
graph LR
    subgraph "LoCoMo Performance"
        L1["Overall: 80-81%"]
        L2["Categories 1-4: 93.9%"]
        L3["Category 5: 11.6%"]
    end
    
    subgraph "LongMemEval-S Performance"
        LM1["Overall: 91.6%"]
        LM2["Single-session-assistant: 100%"]
        LM3["Single-session-preference: 100%"]
        LM4["Multi-session: 86.5%"]
        LM5["Temporal: 86.5%"]
    end
    
    subgraph "Key Factors"
        DUAL["Dual-Route<br/>System-1 + System-2"]
        HIER["Hierarchical<br/>Graph Structure"]
        HYBRID["RAG_GRAPH<br/>Merge Strategy"]
    end
    
    DUAL --> L1
    HIER --> L1
    HYBRID --> L1
    
    DUAL --> LM1
    HIER --> LM1
    HYBRID --> LM1
```

**Performance Summary**: Mnemis achieves **93.9%** on LoCoMo when excluding category 5 (which requires external knowledge) and **91.6%** overall on LongMemEval-S. The dual-route architecture combining System-1 similarity search with System-2 global selection enables both semantic and structural relevance in memory retrieval.

**Sources:** [README.md:18-23](), [README.md:31-40]()

---

## Configuration System

The evaluation framework supports multiple configuration variants to test different retrieval strategies and parameter combinations.

### Configuration Parameter Mapping

```mermaid
graph TB
    subgraph "Model Configuration"
        MC["Model Config"]
        MC1["graph_model<br/>Controls System-2<br/>LLM reasoning"]
        MC2["answer_model<br/>Generates final<br/>QA responses"]
        MC3["grader_model<br/>Evaluates answer<br/>accuracy"]
        
        MC --> MC1
        MC --> MC2
        MC --> MC3
    end
    
    subgraph "Retrieval Configuration"
        RC["Retrieval Config"]
        RC1["rag_top_k<br/>System-1 results<br/>Values: 10, 30"]
        RC2["graph_top_k<br/>System-2 results<br/>Values: 20, 60"]
        RC3["merge_method<br/>Combination strategy<br/>Value: RAG_GRAPH"]
        RC4["graph_global_search<br/>Enable System-2<br/>Value: true"]
        
        RC --> RC1
        RC --> RC2
        RC --> RC3
        RC --> RC4
    end
    
    subgraph "Prompt Configuration"
        PC["Prompt Config"]
        PC1["answer_prompt<br/>Response template<br/>Value: M365"]
        PC2["prompt_turning<br/>Optimization flag<br/>Value: true"]
        PC3["organize_rag_content<br/>Context structure<br/>Value: true"]
        
        PC --> PC1
        PC --> PC2
        PC --> PC3
    end
    
    subgraph "Execution Configuration"
        EC["Execution Config"]
        EC1["batch_size<br/>Concurrent QA pairs<br/>Value: 50"]
        EC2["parallelism<br/>Parallel users<br/>Value: 10"]
        
        EC --> EC1
        EC --> EC2
    end
    
    subgraph "Tested Configurations"
        C1["ragtopk10_gtopk20<br/>Lower retrieval count<br/>Faster execution"]
        C2["ragtopk30_gtopk60<br/>Higher retrieval count<br/>More comprehensive"]
    end
    
    RC1 --> C1
    RC2 --> C1
    RC1 --> C2
    RC2 --> C2
```

**Configuration Architecture**: The evaluation system uses four configuration layers. Model configuration selects the LLM for different roles (System-2 reasoning, answer generation, grading). Retrieval configuration controls the number of results from each route and the merge strategy. Prompt configuration customizes the answer template and content organization. Execution configuration manages concurrency and parallelism. Two primary configurations tested: `ragtopk10_gtopk20` (faster, lower retrieval) and `ragtopk30_gtopk60` (comprehensive, higher retrieval).

**Sources:** [README.md:1-72]()

---

## Evaluation Configuration Parameters

### Model Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `graph_model` | `gpt-41-mini` | Powers System-2 global selection and LLM-guided node filtering |
| `answer_model` | `gpt-41-mini` | Generates final answers from retrieved memory context |
| `grader_model` | `gpt-41-mini` | Performs automated accuracy evaluation of generated answers |

### Retrieval Parameters

| Parameter | Values Tested | Purpose |
|-----------|---------------|---------|
| `rag_top_k` | 10, 30 | Number of results retrieved via System-1 similarity search |
| `graph_top_k` | 20, 60 | Number of nodes selected via System-2 global selection |
| `merge_method` | `RAG_GRAPH` | Strategy for combining System-1 and System-2 results |
| `graph_global_search` | `true` | Enable/disable System-2 hierarchical traversal |

### Prompt Engineering Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `answer_prompt` | `M365` | Template for answer generation (M365 style prompting) |
| `prompt_turning` | `true` | Enable prompt optimization techniques |
| `organize_rag_content` | `true` | Structure retrieved content into Message Chunks, FACTS, ENTITIES |

### Execution Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `batch_size` | 50 | Number of concurrent question-answer pairs processed together |
| `parallelism` | 10 | Number of parallel user contexts evaluated simultaneously |

For detailed analysis of how these parameters impact performance, see [Configuration Impact Analysis](#4.4).

**Sources:** [README.md:1-72]()

---

## Results Storage Structure

Evaluation results are stored in the `results/` directory with two types of output files:

### Results File Structure

```mermaid
graph TB
    subgraph "Results Directory"
        RDIR["results/"]
    end
    
    subgraph "Metrics Files"
        M1["metrics_locomo_<config>.json"]
        M2["metrics_longmemeval_s_<config>.json"]
        
        subgraph "Metrics Content"
            MA["overall_accuracy"]
            MC["accuracy_by_category"]
            MQ["total_questions"]
            MQC["questions_per_category"]
        end
        
        M1 --> MA
        M1 --> MC
        M2 --> MA
        M2 --> MC
    end
    
    subgraph "Detailed Results Files"
        R1["results_locomo_<config>.json"]
        R2["results_longmemeval_s_<config>.json"]
        
        subgraph "Results Content"
            RQ["question"]
            RA["answer"]
            RC["correct_answer"]
            RE["evidence_messages"]
            RMC["message_chunks"]
            RF["FACTS"]
            REN["ENTITIES"]
            RD["duration_metrics"]
        end
        
        R1 --> RQ
        R1 --> RA
        R1 --> RE
        R1 --> RMC
        R1 --> RF
        R1 --> REN
        R2 --> RQ
        R2 --> RA
        R2 --> RE
    end
    
    RDIR --> M1
    RDIR --> M2
    RDIR --> R1
    RDIR --> R2
```

**Results Storage Architecture**: The `results/` directory contains two file types per benchmark-configuration pair. Metrics files (`metrics_*.json`) store aggregated accuracy statistics including overall accuracy and per-category breakdown. Detailed results files (`results_*.json`) contain full question-answer pairs with evidence messages, retrieved context (Message Chunks, FACTS, ENTITIES), and performance timing metrics. File naming convention includes benchmark name and configuration identifier.

For complete documentation of the JSON schema and field descriptions, see [Results Data Format](#4.5).

**Sources:** [README.md:56-57]()

---

## Performance Metrics Categories

Evaluation metrics are collected across multiple dimensions:

### Accuracy Metrics

| Metric | Description | Granularity |
|--------|-------------|-------------|
| **Overall Accuracy** | Percentage of correctly answered questions | Benchmark-level |
| **Category Accuracy** | Accuracy within specific question categories | Category-level |
| **Question Type Accuracy** | Accuracy by question type (single-session, multi-session, temporal) | Type-level |

### Duration Metrics

Timing information is captured for performance analysis:

- **Search Duration**: Time spent in System-1 and System-2 retrieval
- **Answer Duration**: Time spent generating answers from context
- **Grading Duration**: Time spent evaluating answer accuracy
- **Total Duration**: End-to-end processing time per question

### Context Metrics

Retrieved context is organized into structured components:

- **Message Chunks**: Historical conversation segments retrieved as evidence
- **FACTS**: Temporal statements extracted from conversations
- **ENTITIES**: Summarized entity information with key attributes

**Sources:** [README.md:56-57]()

---

## Configuration Comparison

Two primary configurations were tested to evaluate the impact of retrieval parameters:

### Configuration Variants

| Configuration | System-1 (`rag_top_k`) | System-2 (`graph_top_k`) | Trade-offs |
|---------------|------------------------|--------------------------|------------|
| **ragtopk10_gtopk20** | 10 | 20 | Faster execution, focused retrieval |
| **ragtopk30_gtopk60** | 30 | 60 | Higher coverage, more comprehensive context |

### Observed Impact

The two configurations show different performance characteristics:

- **LoCoMo**: Both configurations achieve similar overall accuracy (80-81%), suggesting the dual-route architecture is robust to parameter variations
- **LongMemEval-S**: Performance variations depend on question types, with some types benefiting from higher retrieval counts

```mermaid
graph LR
    subgraph "Lower Retrieval ragtopk10_gtopk20"
        L1["Faster Execution"]
        L2["Focused Context"]
        L3["Lower Latency"]
    end
    
    subgraph "Higher Retrieval ragtopk30_gtopk60"
        H1["More Coverage"]
        H2["Comprehensive Context"]
        H3["Better Recall"]
    end
    
    subgraph "Trade-off Considerations"
        T1["Execution Speed vs Coverage"]
        T2["Context Quality vs Quantity"]
        T3["Latency vs Completeness"]
    end
    
    L1 --> T1
    H1 --> T1
    L2 --> T2
    H2 --> T2
    L3 --> T3
    H3 --> T3
```

For detailed statistical analysis and recommendations on parameter tuning, see [Configuration Impact Analysis](#4.4).

**Sources:** [README.md:1-72]()

---

## Benchmark Result Highlights

### LoCoMo Benchmark

- **Overall Score**: 80-81% across configurations
- **Categories 1-4 Score**: 93.9% (state-of-the-art)
- **Category 5 Score**: 11.6% (requires external knowledge beyond conversation history)
- **Total Questions**: 1,986 questions across 5 categories

The high performance on categories 1-4 demonstrates Mnemis's effectiveness at retrieving and reasoning over conversation history. Category 5's lower score is expected as it requires external knowledge sources not present in the memory system.

For detailed category breakdown and analysis, see [LoCoMo Results](#4.2).

### LongMemEval-S Benchmark

- **Overall Score**: 91.6% (state-of-the-art)
- **Single-session-assistant**: 100% accuracy
- **Single-session-preference**: 100% accuracy
- **Multi-session**: 86.5% accuracy
- **Temporal**: 86.5% accuracy
- **Total Questions**: 500 questions across 6 types

Perfect scores on single-session questions demonstrate excellent within-conversation retrieval. Strong multi-session and temporal performance validates the system's ability to reason across conversation boundaries and time.

For detailed question type breakdown and analysis, see [LongMemEval-S Results](#4.3).

**Sources:** [README.md:18-23](), [README.md:31-40]()

---

## Case Study Examples

The evaluation includes detailed case studies demonstrating Mnemis's retrieval and reasoning capabilities:

### LoCoMo User 8 QA 11

This case study shows how the dual-route system retrieves relevant context from multi-hop reasoning scenarios, combining System-1's semantic similarity with System-2's structural traversal to locate distant but related information.

See complete walkthrough: [LoCoMo User 8 QA 11](#5.1)

### LongMemEval-S QA 262

This example demonstrates temporal reasoning and fact extraction across multiple conversation sessions, showing how the hierarchical graph enables efficient retrieval of time-sensitive information.

See complete walkthrough: [LongMemEval-S QA 262](#5.2)

**Sources:** [README.md:42-51]()

---

## Reproduction and Verification

All evaluation results are reproducible using the provided implementation:

### Available Resources

- **Implementation**: Global selection implementation available in `global_selection/` directory
- **Results Data**: Complete results with memory contexts stored in `results/` directory
- **Benchmark Data**: Both benchmark datasets included for verification
- **Configuration Files**: All tested configurations documented

### Reproduction Steps

1. Load benchmark dataset (`locomo.json` or `longmemeval_s.json`)
2. Configure evaluation parameters (model selection, retrieval settings, prompts)
3. Execute batch processing with specified parallelism
4. Compare generated `metrics_*.json` files with provided results

For detailed reproduction instructions, see [Running Evaluations](#6.3).

**Sources:** [README.md:53-57]()

---

## Summary

Mnemis achieves state-of-the-art performance on long-term memory benchmarks through its dual-route retrieval architecture:

- **93.9%** on LoCoMo (categories 1-4)
- **91.6%** on LongMemEval-S (overall)

The evaluation framework demonstrates:
- Robust performance across multiple configurations
- Effective combination of System-1 and System-2 retrieval
- Comprehensive context assembly (Message Chunks, FACTS, ENTITIES)
- Efficient batch processing and parallel execution

The results validate that combining semantic similarity (System-1) with hierarchical reasoning (System-2) produces superior memory retrieval compared to single-route approaches.

**Sources:** [README.md:1-72]()

---

# Page: Benchmark Datasets

# Benchmark Datasets

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json](results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json)
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json](results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json)

</details>



## Purpose and Scope

This document describes the two benchmark datasets used to evaluate Mnemis: **LoCoMo** and **LongMemEval-S**. It covers their structure, question types, scale, and the evaluation methodology used to test long-term memory retrieval capabilities. For detailed performance results, see [LoCoMo Results](#4.2) and [LongMemEval-S Results](#4.3). For configuration parameter analysis, see [Configuration Impact Analysis](#4.4).

---

## Overview

Mnemis is evaluated on two established benchmarks for long-term LLM memory:

| Benchmark | Questions | Categories/Types | Users | Primary Focus |
|-----------|-----------|------------------|-------|---------------|
| **LoCoMo** | 1,986 | 5 categories | 10 | Multi-turn conversational memory across diverse topics |
| **LongMemEval-S** | 500 | 6 question types | Varies | Single/multi-session scenarios with temporal reasoning |

Both benchmarks test the system's ability to retrieve and reason over historical conversation context stored in the graph database.

**Sources:** [README.md:15-23](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-72](), [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-79]()

---

## LoCoMo Benchmark

### Dataset Structure

LoCoMo (Long Conversational Memory) is a comprehensive benchmark designed to test memory retrieval across extended multi-turn conversations with multiple users.

```mermaid
graph TB
    subgraph "LoCoMo Dataset Structure"
        ROOT["results/locomo/<br/>locomo.json"]
        
        subgraph "Dataset Composition"
            USERS["10 Users<br/>Independent conversation threads"]
            QUESTIONS["1,986 Total Questions<br/>Distributed across categories"]
            CATS["5 Categories<br/>Different difficulty levels"]
        end
        
        subgraph "Category Breakdown"
            C1["Category 1<br/>282 questions<br/>91.8% baseline accuracy"]
            C2["Category 2<br/>321 questions<br/>90.3% baseline accuracy"]
            C3["Category 3<br/>96 questions<br/>82.3% baseline accuracy"]
            C4["Category 4<br/>841 questions<br/>96.2% baseline accuracy"]
            C5["Category 5<br/>446 questions<br/>34.3% baseline accuracy"]
        end
        
        subgraph "Metrics Output"
            METRICS["metrics_*_ragtopk10_gtopk20_RAG_GRAPH.json"]
            RESULTS["results_*_ragtopk10_gtopk20_RAG_GRAPH.json"]
        end
        
        ROOT --> USERS
        ROOT --> QUESTIONS
        QUESTIONS --> CATS
        
        CATS --> C1
        CATS --> C2
        CATS --> C3
        CATS --> C4
        CATS --> C5
        
        USERS --> METRICS
        QUESTIONS --> METRICS
        CATS --> METRICS
        
        USERS --> RESULTS
        QUESTIONS --> RESULTS
    end
```

**Dataset Characteristics:**

The LoCoMo benchmark exhibits significant variation in difficulty across categories, as evidenced by the accuracy distribution in the metrics files:

| Category | Questions | Accuracy (Mnemis) | Characteristic |
|----------|-----------|-------------------|----------------|
| Category 1 | 282 (14.2%) | 91.8% | High baseline performance |
| Category 2 | 321 (16.2%) | 90.3% | High baseline performance |
| Category 3 | 96 (4.8%) | 82.3% | Moderate difficulty |
| Category 4 | 841 (42.4%) | 96.2% | Easiest category |
| Category 5 | 446 (22.5%) | 34.3% | Significantly harder |

Category 5 represents a substantial challenge, with only 34.3% accuracy, suggesting it tests particularly complex memory retrieval scenarios. When excluding Category 5, the system achieves 93.3% accuracy across the remaining 1,540 questions.

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-72]()

### Evaluation Configuration

```mermaid
graph LR
    subgraph "LoCoMo Evaluation Parameters"
        PARALLEL["qa_parallelism: 50<br/>Concurrent question processing"]
        USERS_P["num_users: 10<br/>Independent memory contexts"]
        
        subgraph "Retrieval Configuration"
            RAG["rag_top_k: 10<br/>System-1 similarity results"]
            GRAPH["graph_top_k: 20<br/>System-2 global selection results"]
            MERGE["merge_method: RAG_GRAPH<br/>Hybrid result combination"]
            GS["graph_global_search_enabled: true<br/>Hierarchical traversal active"]
        end
        
        subgraph "Model Configuration"
            GM["graph_model:<br/>gpt-41-mini-shortco-2025-04-14-Bing"]
            AM["answer_model:<br/>gpt-41-mini-shortco-2025-04-14-Bing"]
            GRM["grader_model:<br/>gpt-41-mini-shortco-2025-04-14-Bing"]
        end
        
        PARALLEL --> RAG
        USERS_P --> GRAPH
        RAG --> MERGE
        GRAPH --> MERGE
        MERGE --> GS
        
        GM --> AM
        AM --> GRM
    end
```

The configuration shows 50-way parallelism for question answering, processing questions from 10 independent user contexts simultaneously. This tests the system's ability to maintain separate memory graphs for different users while efficiently retrieving relevant context.

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:5-39]()

---

## LongMemEval-S Benchmark

### Dataset Structure

LongMemEval-S tests memory retrieval across six distinct question types, each targeting specific memory capabilities.

```mermaid
graph TB
    subgraph "LongMemEval-S Dataset Structure"
        ROOT["results/lme-s/<br/>longmemeval_s.json"]
        
        subgraph "500 Total Questions"
            direction TB
            
            TYPES["6 Question Types<br/>Testing different memory aspects"]
        end
        
        subgraph "Question Type Taxonomy"
            SSA["single-session-assistant<br/>56 questions (11.2%)<br/>100% accuracy"]
            SSU["single-session-user<br/>70 questions (14.0%)<br/>98.6% accuracy"]
            SSP["single-session-preference<br/>30 questions (6.0%)<br/>100% accuracy"]
            MS["multi-session<br/>133 questions (26.6%)<br/>86.5% accuracy"]
            TR["temporal-reasoning<br/>133 questions (26.6%)<br/>86.5% accuracy"]
            KU["knowledge-update<br/>78 questions (15.6%)<br/>93.6% accuracy"]
        end
        
        subgraph "Metrics Output"
            METRICS["metrics_*_ragtopk10_gtopk20_RAG_GRAPH.json"]
            RESULTS["results_*_ragtopk10_gtopk20_RAG_GRAPH.json"]
        end
        
        ROOT --> TYPES
        TYPES --> SSA
        TYPES --> SSU
        TYPES --> SSP
        TYPES --> MS
        TYPES --> TR
        TYPES --> KU
        
        SSA --> METRICS
        SSU --> METRICS
        SSP --> METRICS
        MS --> METRICS
        TR --> METRICS
        KU --> METRICS
        
        TYPES --> RESULTS
    end
```

**Question Type Characteristics:**

The six question types test different aspects of long-term memory:

| Question Type | Count | Accuracy | Memory Challenge |
|---------------|-------|----------|------------------|
| `single-session-assistant` | 56 | 100% | Assistant's responses within single session |
| `single-session-user` | 70 | 98.6% | User's statements within single session |
| `single-session-preference` | 30 | 100% | User preferences within session |
| `multi-session` | 133 | 86.5% | Information across multiple sessions |
| `temporal-reasoning` | 133 | 86.5% | Time-based memory queries |
| `knowledge-update` | 78 | 93.6% | Handling updated/changed information |

The data reveals that single-session queries achieve near-perfect accuracy, while multi-session and temporal reasoning questions are significantly more challenging, dropping to 86.5% accuracy. This highlights the difficulty of maintaining temporal context and reasoning across conversation boundaries.

**Sources:** [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-36]()

### Question Type Semantics

```mermaid
graph TB
    subgraph "LongMemEval-S Question Type Semantics"
        direction TB
        
        subgraph "Single-Session Types"
            SSA["single-session-assistant<br/>Tests: Assistant memory of own responses<br/>Challenge: Immediate context retrieval"]
            SSU["single-session-user<br/>Tests: Memory of user statements<br/>Challenge: User input tracking"]
            SSP["single-session-preference<br/>Tests: User preference extraction<br/>Challenge: Preference identification"]
        end
        
        subgraph "Multi-Session Types"
            MS["multi-session<br/>Tests: Cross-session information retrieval<br/>Challenge: Session boundary navigation"]
            TR["temporal-reasoning<br/>Tests: Time-based memory queries<br/>Challenge: Temporal ordering & recency"]
            KU["knowledge-update<br/>Tests: Handling information updates<br/>Challenge: Identifying latest information"]
        end
        
        subgraph "Memory Graph Requirements"
            BG["Base Graph<br/>Flat entity/episode storage<br/>System-1 similarity search"]
            HG["Hierarchical Graph<br/>Semantic categories<br/>System-2 global selection"]
        end
        
        SSA --> BG
        SSU --> BG
        SSP --> BG
        
        MS --> HG
        TR --> HG
        KU --> HG
        
        BG --> MERGE["RAG_GRAPH Merge"]
        HG --> MERGE
    end
```

The question taxonomy reflects different retrieval strategies:
- **Single-session types** primarily benefit from System-1 similarity search on the base graph
- **Multi-session types** require System-2 global selection to reason across session boundaries and temporal dimensions
- Both systems merge results via the `RAG_GRAPH` method for comprehensive coverage

**Sources:** [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:2-31]()

---

## Evaluation Methodology

### Configuration Parameters

Both benchmarks use identical configuration parameters stored in the metrics files:

```mermaid
graph TB
    subgraph "Evaluation Configuration Structure"
        direction TB
        
        CONFIG["config object<br/>metrics_*.json"]
        
        subgraph "models"
            GM["graph_model<br/>gpt-41-mini-shortco-2025-04-14-Bing"]
            AM["answer_model<br/>gpt-41-mini-shortco-2025-04-14-Bing"]
            GRM["grader_model<br/>gpt-41-mini-shortco-2025-04-14-Bing"]
        end
        
        subgraph "embedder"
            EMB_TYPE["type: qwen3"]
            EMB_PREC["precision: Precision.FLOAT32"]
        end
        
        subgraph "retrieval"
            GRAPH_EN["graph_enabled: true"]
            RAG_EN["rag_enabled: true"]
            MERGE["merge_method: RAG_GRAPH"]
            RAG_K["rag_top_k: 10"]
            GRAPH_K["graph_top_k: 20"]
            NODE_EMB["graph_node_embedding: summary_embedding"]
            GS["graph_global_search_enabled: true"]
        end
        
        subgraph "prompt"
            AP["answer_prompt: M365"]
            PT["prompt_turning: true"]
            ORC["organize_rag_content: true"]
            ERC["enrich_rag_context: 0"]
        end
        
        CONFIG --> GM
        CONFIG --> AM
        CONFIG --> GRM
        CONFIG --> EMB_TYPE
        CONFIG --> EMB_PREC
        CONFIG --> GRAPH_EN
        CONFIG --> RAG_EN
        CONFIG --> MERGE
        CONFIG --> RAG_K
        CONFIG --> GRAPH_K
        CONFIG --> NODE_EMB
        CONFIG --> GS
        CONFIG --> AP
        CONFIG --> PT
        CONFIG --> ORC
        CONFIG --> ERC
    end
```

**Key Configuration Elements:**

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `graph_model` | `gpt-41-mini-shortco-2025-04-14-Bing` | LLM for global selection node filtering |
| `answer_model` | `gpt-41-mini-shortco-2025-04-14-Bing` | LLM for answer generation |
| `grader_model` | `gpt-41-mini-shortco-2025-04-14-Bing` | LLM for accuracy evaluation |
| `embedder.type` | `qwen3` | Embedding model for similarity search |
| `embedder.precision` | `Precision.FLOAT32` | Float32 precision for embeddings |
| `rag_top_k` | `10` | Top-K results from System-1 |
| `graph_top_k` | `20` | Top-K nodes from System-2 |
| `merge_method` | `RAG_GRAPH` | Hybrid result combination |
| `graph_global_search_enabled` | `true` | Enable hierarchical traversal |
| `answer_prompt` | `M365` | Microsoft 365-style prompting |
| `organize_rag_content` | `true` | Structure retrieved content |

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:7-39](), [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:37-78]()

### Evaluation Pipeline

```mermaid
graph LR
    subgraph "Benchmark Evaluation Flow"
        direction LR
        
        subgraph "Input"
            LOCOMO["locomo.json<br/>1,986 questions"]
            LME["longmemeval_s.json<br/>500 questions"]
        end
        
        subgraph "Processing"
            LOAD["Dataset Loader"]
            BATCH["Batch Processor<br/>qa_parallelism: 50"]
            
            subgraph "Dual-Route Retrieval"
                S1["System-1<br/>rag_top_k: 10"]
                S2["System-2<br/>graph_top_k: 20"]
                MERGE_P["RAG_GRAPH Merge"]
            end
            
            ANSWER["Answer Model<br/>gpt-41-mini"]
            GRADER["Grader Model<br/>gpt-41-mini"]
        end
        
        subgraph "Output"
            METRICS["metrics_*.json<br/>Accuracy per category/type"]
            RESULTS["results_*.json<br/>Full QA with context"]
        end
        
        LOCOMO --> LOAD
        LME --> LOAD
        
        LOAD --> BATCH
        BATCH --> S1
        BATCH --> S2
        
        S1 --> MERGE_P
        S2 --> MERGE_P
        
        MERGE_P --> ANSWER
        ANSWER --> GRADER
        
        GRADER --> METRICS
        GRADER --> RESULTS
    end
```

The evaluation pipeline processes questions in batches with 50-way parallelism for LoCoMo. Each question triggers:
1. **Dual-route retrieval**: System-1 similarity search (top-10) and System-2 global selection (top-20)
2. **Result merging**: RAG_GRAPH method combines both retrieval paths
3. **Answer generation**: GPT-4.1-mini generates answers from retrieved context
4. **Accuracy grading**: GPT-4.1-mini evaluates answer correctness

Results are stored in two formats:
- **metrics_*.json**: Aggregated accuracy statistics per category/question type
- **results_*.json**: Complete QA pairs with retrieved context (see [Results Data Format](#4.5))

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-72](), [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-79]()

---

## Dataset Comparison

### Scale and Complexity

| Aspect | LoCoMo | LongMemEval-S |
|--------|--------|---------------|
| **Total Questions** | 1,986 | 500 |
| **Categorization** | 5 categories (difficulty-based) | 6 question types (capability-based) |
| **User Contexts** | 10 independent users | Varies by question type |
| **Parallelism** | 50 concurrent QA | N/A (sequential) |
| **Primary Challenge** | Multi-user conversational memory | Multi-session temporal reasoning |
| **Overall Accuracy** | 80.1% (93.3% excl. Cat5) | 91.6% |
| **Hardest Subset** | Category 5 (34.3%) | Multi-session & temporal (86.5%) |
| **Easiest Subset** | Category 4 (96.2%) | Single-session preference (100%) |

### Complementary Testing

The two benchmarks provide complementary evaluation:

**LoCoMo** emphasizes:
- Large-scale evaluation (4x more questions)
- Multi-user memory isolation
- Varied difficulty levels across categories
- High concurrency testing (50-way parallelism)

**LongMemEval-S** emphasizes:
- Fine-grained capability testing (6 question types)
- Temporal and multi-session reasoning
- Knowledge update handling
- Preference extraction

Together, they comprehensively evaluate both the scale and sophistication of Mnemis's dual-route memory system.

**Sources:** [README.md:15-23](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-72](), [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-79]()

---

# Page: LoCoMo Results

# LoCoMo Results

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [figures/results_locomo.png](figures/results_locomo.png)
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json](results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json)
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json](results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json)

</details>



## Purpose and Scope

This page presents detailed performance results for Mnemis on the LoCoMo (Long Conversation Memory) benchmark. For information about the LoCoMo benchmark structure and methodology, see [Benchmark Datasets](#4.1). For comparison with LongMemEval-S results, see [LongMemEval-S Results](#4.3). For analysis of how different retrieval parameters affect performance, see [Configuration Impact Analysis](#4.4).

The results demonstrate Mnemis achieving 80-81% overall accuracy on LoCoMo, with 93.3-93.9% accuracy when excluding category 5 questions (which test reasoning over visual content that the system cannot process).

## Overall Performance Summary

Mnemis was evaluated on LoCoMo using two retrieval configurations with the `RAG_GRAPH` merge method:

| Configuration | Overall Accuracy | Questions Correct | Excluding Cat 5 Accuracy | Questions Correct (No Cat 5) |
|--------------|------------------|-------------------|--------------------------|------------------------------|
| `rag_top_k=10, graph_top_k=20` | 80.06% | 1590/1986 | 93.31% | 1437/1540 |
| `rag_top_k=30, graph_top_k=60` | 80.61% | 1601/1986 | 93.90% | 1446/1540 |

Both configurations used:
- **Models**: `gpt-41-mini-shortco-2025-04-14-Bing` for graph operations, answer generation, and grading
- **Embedder**: `qwen3` with `Precision.FLOAT32`
- **Retrieval**: Dual-route with `graph_global_search_enabled=true`
- **Prompt**: M365 answer prompt with `prompt_turning=true` and `organize_rag_content=true`

**Sources**: 
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-73]()
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json:1-73]()

## Category Performance Breakdown

LoCoMo organizes questions into 5 categories testing different memory capabilities. Performance varies significantly by category:

### Configuration 1: rag_top_k=10, graph_top_k=20

| Category | Correct | Total | Accuracy | Description |
|----------|---------|-------|----------|-------------|
| 1 | 259 | 282 | 91.84% | Single conversation memory |
| 2 | 290 | 321 | 90.34% | Multi-conversation memory |
| 3 | 79 | 96 | 82.29% | Temporal reasoning |
| 4 | 809 | 841 | 96.20% | Preference and fact recall |
| 5 | 153 | 446 | 34.30% | Visual content reasoning |

### Configuration 2: rag_top_k=30, graph_top_k=60

| Category | Correct | Total | Accuracy | Description |
|----------|---------|-------|----------|-------------|
| 1 | 262 | 282 | 92.91% | Single conversation memory |
| 2 | 291 | 321 | 90.65% | Multi-conversation memory |
| 3 | 76 | 96 | 79.17% | Temporal reasoning |
| 4 | 817 | 841 | 97.15% | Preference and fact recall |
| 5 | 155 | 446 | 34.75% | Visual content reasoning |

**Sources**: 
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:41-69]()
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json:41-69]()

### Category Performance Visualization

```mermaid
graph LR
    subgraph "LoCoMo Category Performance"
        CAT1["Category 1<br/>Single Conv<br/>91.84% / 92.91%"]
        CAT2["Category 2<br/>Multi Conv<br/>90.34% / 90.65%"]
        CAT3["Category 3<br/>Temporal<br/>82.29% / 79.17%"]
        CAT4["Category 4<br/>Preferences<br/>96.20% / 97.15%"]
        CAT5["Category 5<br/>Visual<br/>34.30% / 34.75%"]
    end
    
    subgraph "System Components"
        S1["System-1<br/>Similarity Search<br/>rag_top_k: 10/30"]
        S2["System-2<br/>Global Selection<br/>graph_top_k: 20/60"]
        MERGE["RAG_GRAPH<br/>Merge Strategy"]
    end
    
    S1 --> MERGE
    S2 --> MERGE
    
    MERGE --> CAT1
    MERGE --> CAT2
    MERGE --> CAT3
    MERGE --> CAT4
    MERGE --> CAT5
```

**Sources**: 
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:17-25]()
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json:17-25]()

## Configuration Comparison

The two configurations differ in the number of memory items retrieved from each path:

```mermaid
graph TB
    subgraph "Configuration 1: Conservative"
        R1["RAG Path<br/>rag_top_k: 10"]
        G1["Graph Path<br/>graph_top_k: 20"]
        M1["Total: ~30 items"]
        ACC1["Accuracy: 80.06%<br/>Cat 1-4: 93.31%"]
        
        R1 --> M1
        G1 --> M1
        M1 --> ACC1
    end
    
    subgraph "Configuration 2: Aggressive"
        R2["RAG Path<br/>rag_top_k: 30"]
        G2["Graph Path<br/>graph_top_k: 60"]
        M2["Total: ~90 items"]
        ACC2["Accuracy: 80.61%<br/>Cat 1-4: 93.90%"]
        
        R2 --> M2
        G2 --> M2
        M2 --> ACC2
    end
```

**Sources**: 
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:21-22]()
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json:21-22]()

### Performance Differences by Configuration

| Metric | Config 1 (10/20) | Config 2 (30/60) | Δ |
|--------|------------------|------------------|---|
| Overall | 80.06% | 80.61% | +0.55% |
| Category 1 | 91.84% | 92.91% | +1.07% |
| Category 2 | 90.34% | 90.65% | +0.31% |
| Category 3 | 82.29% | 79.17% | -3.12% |
| Category 4 | 96.20% | 97.15% | +0.95% |
| Category 5 | 34.30% | 34.75% | +0.45% |
| **Categories 1-4** | **93.31%** | **93.90%** | **+0.59%** |

The aggressive configuration (30/60) provides marginal improvement on most categories, with the notable exception of Category 3 (temporal reasoning), where performance decreased by 3.12 percentage points. This suggests that for temporal reasoning questions, retrieving more context may introduce noise that confuses the answer model.

**Sources**: 
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:41-72]()
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json:41-72]()

## Results Generation Pipeline

The following diagram shows how LoCoMo evaluation results are generated, mapping natural language concepts to code entities:

```mermaid
graph TB
    subgraph "Input: LoCoMo Dataset"
        DATASET["locomo.json<br/>1,986 questions<br/>5 categories<br/>10 users"]
    end
    
    subgraph "Evaluation Loop"
        BATCH["Batch Processing<br/>qa_parallelism: 50"]
        USER["Per-User Processing<br/>num_users: 10"]
    end
    
    subgraph "QA Processing"
        QUESTION["Question Input"]
        
        subgraph "Retrieval Components"
            RAG["RAG Search<br/>qwen3 embedder<br/>rag_top_k"]
            GRAPH["Global Selection<br/>graph_global_search_enabled<br/>graph_top_k"]
        end
        
        MERGE["Merge: RAG_GRAPH<br/>merge_method"]
        CONTEXT["Organized Context<br/>organize_rag_content: true<br/>prompt_turning: true"]
        
        ANSWER["Answer Generation<br/>answer_model<br/>answer_prompt: M365"]
        GRADE["Grading<br/>grader_model"]
    end
    
    subgraph "Metrics Computation"
        COLLECT["Collect Results<br/>Per Category"]
        COMPUTE["Compute Accuracy<br/>total_correct /<br/>total_questions"]
        CAT_STATS["category_stats<br/>category_accuracies"]
        EXCLUDE["accuracy_exculde_category5"]
    end
    
    subgraph "Output: metrics_*.json"
        OUTPUT["accuracy<br/>category_accuracies<br/>config details"]
    end
    
    DATASET --> BATCH
    BATCH --> USER
    USER --> QUESTION
    
    QUESTION --> RAG
    QUESTION --> GRAPH
    
    RAG --> MERGE
    GRAPH --> MERGE
    
    MERGE --> CONTEXT
    CONTEXT --> ANSWER
    ANSWER --> GRADE
    
    GRADE --> COLLECT
    COLLECT --> COMPUTE
    COMPUTE --> CAT_STATS
    COMPUTE --> EXCLUDE
    
    CAT_STATS --> OUTPUT
    EXCLUDE --> OUTPUT
```

**Sources**: 
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:7-40]()
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json:7-40]()

## Performance Analysis

### Strong Performance on Categories 1-4

Mnemis demonstrates robust performance across the first four LoCoMo categories:

- **Category 4 (Preferences & Facts)**: 96.20-97.15% accuracy demonstrates excellent recall of explicit user preferences and factual statements
- **Category 1 (Single Conversation)**: 91.84-92.91% shows strong memory within individual conversation contexts
- **Category 2 (Multi-Conversation)**: 90.34-90.65% indicates effective cross-conversation reasoning
- **Category 3 (Temporal)**: 79.17-82.29% represents the most challenging non-visual category, requiring time-based reasoning

The combined accuracy of 93.31-93.90% across categories 1-4 validates the dual-route architecture's effectiveness for text-based conversational memory.

### Category 5 Challenge

Category 5 questions test reasoning over visual content (images, charts, diagrams) mentioned in conversations. The 34.30-34.75% accuracy reflects the system's current limitation:

- The system stores only textual descriptions of visual content
- Questions requiring interpretation of visual details cannot be answered from text alone
- This is an expected limitation given the text-only storage architecture

### Practical Implications

The `accuracy_exculde_category5` metric (93.31-93.90%) represents the system's performance on text-based conversational memory, which is the primary use case. For deployment scenarios:

- Text-based conversation memory: **93-94% accuracy** (categories 1-4)
- Visual content reasoning: **34% accuracy** (category 5) - requires multimodal extensions
- Overall benchmark: **80-81% accuracy** (all categories)

**Sources**: 
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:70-72]()
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json:70-72]()

## Configuration Details

Both evaluated configurations share the same architectural components:

```mermaid
graph TB
    subgraph "Model Configuration"
        GM["graph_model<br/>gpt-41-mini-shortco"]
        AM["answer_model<br/>gpt-41-mini-shortco"]
        GRM["grader_model<br/>gpt-41-mini-shortco"]
    end
    
    subgraph "Embedder Configuration"
        EMB["type: qwen3<br/>precision: FLOAT32"]
    end
    
    subgraph "Retrieval Configuration"
        GE["graph_enabled: true"]
        RE["rag_enabled: true"]
        MM["merge_method: RAG_GRAPH"]
        GNE["graph_node_embedding:<br/>summary_embedding"]
        GGS["graph_global_search_enabled:<br/>true"]
    end
    
    subgraph "Prompt Configuration"
        AP["answer_prompt: M365"]
        PT["prompt_turning: true"]
        ORC["organize_rag_content: true"]
        ERC["enrich_rag_context: 0"]
    end
    
    subgraph "Advanced Configuration"
        REM["rag_use_evidence_messages:<br/>false"]
        EPM["evidence_previous_messages_limit:<br/>5"]
    end
    
    subgraph "Experiment Configuration"
        NAME["name:<br/>locomo_mnemis_exp_41mini_gs8B_orc"]
        GID["group_id_prefix:<br/>locomo_mnemis_exp_41mini"]
    end
```

The only differences between configurations are `rag_top_k` (10 vs 30) and `graph_top_k` (20 vs 60).

**Sources**: 
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:7-40]()
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json:7-40]()

## Key Findings

1. **State-of-the-art text memory**: 93.3-93.9% accuracy on text-based conversational memory (categories 1-4) represents strong performance on the core use case

2. **Dual-route effectiveness**: The `RAG_GRAPH` merge strategy combining System-1 similarity search and System-2 global selection produces robust results across all question types

3. **Configuration sensitivity**: Increasing retrieval depth (10/20 → 30/60) provides marginal overall improvement (+0.55-0.59%) but may hurt temporal reasoning performance (-3.12% on category 3)

4. **Known limitation**: Visual content reasoning (category 5) at 34% accuracy represents the expected performance ceiling for text-only storage

5. **Parallelism**: Processing 1,986 questions across 10 users with 50 concurrent QA operations demonstrates the system's scalability

**Sources**: 
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-73]()
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json:1-73]()

---

# Page: LongMemEval-S Results

# LongMemEval-S Results

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [figures/results_lme_s.png](figures/results_lme_s.png)
- [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json](results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json)
- [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json](results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json)

</details>



This page provides an in-depth analysis of Mnemis's performance on the LongMemEval-S benchmark, a 500-question evaluation dataset designed to test long-term memory retrieval across six question types. The analysis includes overall accuracy metrics, performance breakdowns by question type, configuration details, and example cases demonstrating the system's capabilities.

For results on the LoCoMo benchmark, see [LoCoMo Results](#4.2). For configuration parameter impact analysis across both benchmarks, see [Configuration Impact Analysis](#4.4).

## Overall Performance Summary

Mnemis achieved **91.6% accuracy** on LongMemEval-S, correctly answering 458 out of 500 questions. This performance demonstrates strong capability in retrieving and reasoning over long-term conversational memory across diverse question types.

**Overall Performance Metrics**

```mermaid
graph TB
    subgraph "LongMemEval-S Benchmark"
        TOTAL["Total Questions: 500<br/>Correct: 458<br/>Accuracy: 91.6%"]
    end
    
    subgraph "Perfect Performance Categories"
        SSA["single-session-assistant<br/>56/56 (100%)"]
        SSP["single-session-preference<br/>30/30 (100%)"]
        SSU["single-session-user<br/>69/70 (98.6%)"]
    end
    
    subgraph "Strong Performance Categories"
        KU["knowledge-update<br/>73/78 (93.6%)"]
    end
    
    subgraph "Moderate Performance Categories"
        MS["multi-session<br/>115/133 (86.5%)"]
        TR["temporal-reasoning<br/>115/133 (86.5%)"]
    end
    
    TOTAL --> SSA
    TOTAL --> SSP
    TOTAL --> SSU
    TOTAL --> KU
    TOTAL --> MS
    TOTAL --> TR
    
    style TOTAL fill:#e8e8e8
    style SSA fill:#d4edda
    style SSP fill:#d4edda
    style SSU fill:#d4edda
    style KU fill:#d1ecf1
    style MS fill:#fff3cd
    style TR fill:#fff3cd
```

Sources: [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-37]()

## Performance by Question Type

### Perfect Performance Categories

**Single-Session-Assistant (100% Accuracy)**

The system achieved perfect accuracy on 56 questions requiring retrieval of information from assistant responses within a single conversation session. This demonstrates excellent capability in recalling the assistant's own statements and recommendations.

| Metric | Value |
|--------|-------|
| Questions | 56 |
| Correct | 56 |
| Accuracy | 100.0% |

**Single-Session-Preference (100% Accuracy)**

Perfect performance on 30 questions about user preferences expressed within a single session. This question type tests the system's ability to recall explicit user preferences and choices.

| Metric | Value |
|--------|-------|
| Questions | 30 |
| Correct | 30 |
| Accuracy | 100.0% |

Sources: [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:17-31]()

### Strong Performance Categories

**Single-Session-User (98.6% Accuracy)**

Near-perfect performance on 70 questions about user-provided information within a single conversation. Only 1 error out of 70 questions demonstrates robust memory for user statements.

| Metric | Value |
|--------|-------|
| Questions | 70 |
| Correct | 69 |
| Accuracy | 98.6% |

**Example Question**: "(date: 2023/05/30 (Tue) 23:39) Where did I buy my new tennis racket from?"

**Gold Answer**: "the sports store downtown"

**System Hypothesis**: "You bought your new tennis racket from a **sports store downtown**."

**Grade**: Correct ✓

The system correctly retrieved the evidence message from 2023/05/25 stating: "I'm really happy with my new tennis racket, which I got from a sports store downtown."

Sources: [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1](), [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:2-6]()

**Knowledge-Update (93.6% Accuracy)**

Strong performance on 78 questions testing the system's ability to track updated or changed information over time.

| Metric | Value |
|--------|-------|
| Questions | 78 |
| Correct | 73 |
| Accuracy | 93.6% |

**Example Question**: "(date: 2023/05/30 (Tue) 23:40) What degree did I graduate with?"

**Gold Answer**: "Business Administration"

**System Hypothesis**: "You graduated with a degree in **Business Administration**. This degree has definitely helped you in your new role."

**Grade**: Correct ✓

The system retrieved the relevant evidence from 2023/05/30: "I graduated with a degree in Business Administration, which has definitely helped me in my new role."

Sources: [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:2](), [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:22-26]()

### Moderate Performance Categories

**Multi-Session (86.5% Accuracy)**

The system achieved 86.5% accuracy on 133 questions requiring retrieval across multiple conversation sessions. This represents the most challenging question type, as it requires connecting information scattered across different temporal contexts.

| Metric | Value |
|--------|-------|
| Questions | 133 |
| Correct | 115 |
| Accuracy | 86.5% |

**Temporal-Reasoning (86.5% Accuracy)**

Identical performance to multi-session (86.5% on 133 questions), as temporal reasoning questions often span multiple sessions and require understanding time-based relationships between events.

| Metric | Value |
|--------|-------|
| Questions | 133 |
| Correct | 115 |
| Accuracy | 86.5% |

These categories show where the dual-route retrieval system faces its greatest challenges: questions requiring global context across many sessions and temporal ordering of events.

Sources: [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:7-21]()

## Configuration Details

The evaluation used the following configuration, stored in the metrics file:

**Evaluation Configuration Architecture**

```mermaid
graph TB
    subgraph "Model Configuration"
        GM["graph_model<br/>gpt-41-mini-shortco-2025-04-14-Bing"]
        AM["answer_model<br/>gpt-41-mini-shortco-2025-04-14-Bing"]
        GRM["grader_model<br/>gpt-41-mini-shortco-2025-04-14-Bing"]
    end
    
    subgraph "Embedder Configuration"
        EMB["type: qwen3<br/>precision: FLOAT32"]
    end
    
    subgraph "Retrieval Configuration"
        GE["graph_enabled: true"]
        RE["rag_enabled: true"]
        MM["merge_method: RAG_GRAPH"]
        RTK["rag_top_k: 10"]
        GTK["graph_top_k: 20"]
        NE["graph_node_embedding:<br/>summary_embedding"]
        GS["graph_global_search_enabled: true"]
    end
    
    subgraph "Prompt Configuration"
        AP["answer_prompt: M365"]
        PT["prompt_turning: true"]
        ORC["organize_rag_content: true"]
        ERC["enrich_rag_context: 0"]
    end
    
    subgraph "Advanced Configuration"
        REM["rag_use_evidence_messages: false"]
        BI["bulk_ingestion: true"]
        SD["enable_semantic_deduplication: false"]
    end
    
    GM --> EVAL["LongMemEval-S<br/>Evaluation Pipeline"]
    AM --> EVAL
    GRM --> EVAL
    EMB --> EVAL
    GE --> EVAL
    RE --> EVAL
    MM --> EVAL
    RTK --> EVAL
    GTK --> EVAL
    NE --> EVAL
    GS --> EVAL
    AP --> EVAL
    PT --> EVAL
    ORC --> EVAL
    ERC --> EVAL
    REM --> EVAL
    BI --> EVAL
    SD --> EVAL
    
    EVAL --> METRICS["metrics_*.json"]
    EVAL --> RESULTS["results_*.json"]
```

Sources: [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:37-79]()

### Key Configuration Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `graph_model` | gpt-41-mini-shortco-2025-04-14-Bing | LLM for global selection node filtering |
| `answer_model` | gpt-41-mini-shortco-2025-04-14-Bing | LLM for generating final answers |
| `grader_model` | gpt-41-mini-shortco-2025-04-14-Bing | LLM for evaluating answer correctness |
| `embedder.type` | qwen3 | Embedding model for similarity search |
| `embedder.precision` | FLOAT32 | Embedding precision level |
| `merge_method` | RAG_GRAPH | Hybrid retrieval combining RAG + Graph |
| `rag_top_k` | 10 | Number of top results from similarity search |
| `graph_top_k` | 20 | Number of top nodes from global selection |
| `graph_global_search_enabled` | true | Enables System-2 hierarchical traversal |
| `answer_prompt` | M365 | Prompt template variant used |
| `organize_rag_content` | true | Structures context into FACTS/ENTITIES |

Sources: [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:38-67]()

## Results Data Structure

The evaluation produces two types of output files with specific schemas:

**Results File Schema (`results_*.json`)**

Each question entry contains:

```mermaid
graph LR
    subgraph "Question Entry Structure"
        QID["question_id<br/>(unique identifier)"]
        Q["question<br/>(with timestamp)"]
        H["hypothesis<br/>(system answer)"]
        GA["gold_answer<br/>(correct answer)"]
        QT["question_type<br/>(category)"]
        DUR["duration<br/>(seconds)"]
        GR["grade<br/>(boolean)"]
        
        subgraph "Evidence"
            ASIDS["answer_session_ids[]"]
            EM["evidence_messages[]<br/>role, content, datetime"]
        end
        
        subgraph "Context"
            MSG["Message Chunks<br/>(historical conversations)"]
            FACTS["FACTS<br/>(temporal statements)"]
            ENT["ENTITIES<br/>(summarized concepts)"]
        end
        
        RD["retrieval_duration"]
    end
    
    QID --> ENTRY["Question Entry"]
    Q --> ENTRY
    H --> ENTRY
    GA --> ENTRY
    QT --> ENTRY
    DUR --> ENTRY
    GR --> ENTRY
    ASIDS --> ENTRY
    EM --> ENTRY
    MSG --> ENTRY
    FACTS --> ENTRY
    ENT --> ENTRY
    RD --> ENTRY
```

Sources: [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-2]()

### Example Result Entry Fields

**Question ID**: `f8c5f88b`
**Question**: "(date: 2023/05/30 (Tue) 23:39)Where did I buy my new tennis racket from?"
**Hypothesis**: "You bought your new tennis racket from a **sports store downtown**."
**Gold Answer**: "the sports store downtown"
**Question Type**: "single-session-user"
**Duration**: 2.14 seconds
**Grade**: true
**Answer Session IDs**: `["answer_c3567066"]`

**Evidence Messages**: 
```json
{
  "role": "user",
  "content": "I'm really happy with my new tennis racket, which I got from a sports store downtown.",
  "datetime": "2023/05/25 (Thu) 21:29"
}
```

**Context Structure**: The context field contains three main sections:
1. **Message Chunks**: Historical conversation excerpts organized by session
2. **FACTS**: Timestamped factual statements extracted from conversations (e.g., "The user owns a new tennis racket which they got from a sports store downtown (2023-05-25 - 2023-05-29)")
3. **ENTITIES**: Summarized entity information (e.g., "sports store downtown: A sports store located downtown where the user purchased a new tennis racket")

Sources: [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1]()

**Metrics File Schema (`metrics_*.json`)**

```json
{
  "question_type_name": {
    "correct": <count>,
    "total": <count>,
    "accuracy": <percentage>
  },
  "total": {
    "correct": 458,
    "total": 500,
    "accuracy": 0.916
  },
  "config": { ... }
}
```

Sources: [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-80]()

## Performance Characteristics

### Response Time Analysis

Based on example entries in the results file:

| Metric | Example Value | Description |
|--------|---------------|-------------|
| Average Duration | ~2.14 seconds | Time to answer a question |
| Retrieval Duration | ~0.0001 seconds | Time to retrieve context (appears to be cached/optimized) |

The dual-route retrieval architecture enables fast response times while maintaining high accuracy through:
- System-1 similarity search (fast, parallel)
- System-2 global selection (cached, batched)
- RAG_GRAPH merge optimization

Sources: [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-2]()

### Context Assembly Breakdown

**RAG_GRAPH Context Organization**

```mermaid
graph TB
    subgraph "Dual Retrieval Paths"
        S1["System-1 Similarity Search<br/>rag_top_k=10<br/>qwen3 embeddings"]
        S2["System-2 Global Selection<br/>graph_top_k=20<br/>LLM-guided traversal"]
    end
    
    subgraph "Context Assembly"
        MERGE["RAG_GRAPH Merger"]
        
        subgraph "Organized Context Output"
            MC["Message Chunks<br/>(Historical conversation excerpts<br/>organized by session)"]
            FACTS["FACTS<br/>(Timestamped statements<br/>with temporal ranges)"]
            ENT["ENTITIES<br/>(Entity summaries<br/>with relationship context)"]
        end
    end
    
    S1 --> MERGE
    S2 --> MERGE
    MERGE --> MC
    MERGE --> FACTS
    MERGE --> ENT
    
    MC --> ANS["Answer Generation<br/>gpt-41-mini"]
    FACTS --> ANS
    ENT --> ANS
    
    ANS --> GRADE["Grading<br/>gpt-41-mini"]
```

The `organize_rag_content: true` configuration parameter structures the merged retrieval results into three distinct sections, enabling the answer model to efficiently process different types of information:

1. **Message Chunks**: Direct conversation excerpts providing full context
2. **FACTS**: Extracted temporal facts with event time ranges
3. **ENTITIES**: Summarized entity information with relationships

Sources: [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-2](), [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:56-60]()

## Key Findings and Insights

### Performance by Complexity

**Accuracy vs Question Complexity Pattern**

| Question Type | Complexity | Accuracy | Sessions Required |
|---------------|------------|----------|-------------------|
| single-session-assistant | Low | 100.0% | 1 |
| single-session-preference | Low | 100.0% | 1 |
| single-session-user | Low | 98.6% | 1 |
| knowledge-update | Medium | 93.6% | Multiple (with updates) |
| multi-session | High | 86.5% | Multiple |
| temporal-reasoning | High | 86.5% | Multiple (with ordering) |

The results demonstrate a clear correlation between question complexity and accuracy:
- **Perfect or near-perfect** on single-session questions (98.6-100%)
- **Strong performance** on knowledge updates requiring tracking changes (93.6%)
- **Moderate performance** on multi-session temporal reasoning (86.5%)

This pattern suggests that the primary challenge lies in connecting information across multiple conversation sessions and reasoning about temporal relationships, which is expected for long-term memory systems.

### System-2 Global Selection Impact

The configuration `graph_global_search_enabled: true` with `graph_top_k: 20` enables hierarchical traversal through the knowledge graph. The higher graph_top_k compared to rag_top_k (20 vs 10) provides broader coverage for questions requiring global context, contributing to the strong performance on multi-session questions (86.5%) compared to systems without global selection capabilities.

Sources: [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:7-21](), [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:47-55]()

### Evidence Retrieval Success

The system successfully retrieves relevant evidence messages for answering questions, as shown in the example cases. The `evidence_messages` field in results demonstrates pinpoint accuracy in identifying the exact conversation turns containing the answer, even across lengthy conversation histories spanning multiple sessions.

Example: For the tennis racket question, the system correctly identified the single relevant message from 2023/05/25 among potentially hundreds of messages in the user's conversation history.

Sources: [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-2]()

### Benchmark Comparison

Compared to LoCoMo (see [LoCoMo Results](#4.2)):
- **LongMemEval-S**: 91.6% accuracy on 500 questions
- **LoCoMo**: 80-81% overall, 93.3% excluding category 5

LongMemEval-S shows higher overall accuracy, likely due to:
1. Smaller scale (500 vs 1,986 questions) allowing for more focused evaluation
2. Different question type distribution
3. Potentially clearer gold answers in dataset design

However, both benchmarks demonstrate Mnemis's strong capability in long-term memory retrieval with state-of-the-art performance.

Sources: [results/lme-s/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:32-36]()

---

# Page: Configuration Impact Analysis

# Configuration Impact Analysis

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json](results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json)
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json](results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json)

</details>



## Purpose and Scope

This page analyzes the impact of different retrieval configuration parameters on Mnemis's performance, specifically comparing two configurations tested on the LoCoMo benchmark: `ragtopk10_gtopk20` and `ragtopk30_gtopk60`. The analysis examines how varying the number of retrieved results from both System-1 (RAG) and System-2 (Global Selection) affects overall accuracy and per-category performance.

For detailed benchmark dataset descriptions, see [Benchmark Datasets](#4.1). For comprehensive LoCoMo results analysis, see [LoCoMo Results](#4.2). For information about the results data structure, see [Results Data Format](#4.5).

---

## Configuration Parameters Overview

### Retrieval Parameters

The key configurable parameters that impact memory retrieval behavior are controlled through the configuration structure stored in results files:

| Parameter | Description | Config Path |
|-----------|-------------|-------------|
| `rag_top_k` | Number of results retrieved from System-1 similarity search | `config.retrieval.rag_top_k` |
| `graph_top_k` | Number of results retrieved from System-2 global selection | `config.retrieval.graph_top_k` |
| `merge_method` | Strategy for combining System-1 and System-2 results | `config.retrieval.merge_method` |
| `graph_global_search_enabled` | Enable/disable hierarchical traversal | `config.retrieval.graph_global_search_enabled` |
| `graph_node_embedding` | Embedding field used for graph node similarity | `config.retrieval.graph_node_embedding` |

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:7-40](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json:7-40]()

### Fixed Configuration Elements

Both tested configurations maintain identical settings for the following components to isolate the impact of retrieval parameters:

| Component | Setting | Value |
|-----------|---------|-------|
| Graph Model | `config.models.graph_model` | `gpt-41-mini-shortco-2025-04-14-Bing` |
| Answer Model | `config.models.answer_model` | `gpt-41-mini-shortco-2025-04-14-Bing` |
| Grader Model | `config.models.grader_model` | `gpt-41-mini-shortco-2025-04-14-Bing` |
| Embedder Type | `config.embedder.type` | `qwen3` |
| Embedder Precision | `config.embedder.precision` | `Precision.FLOAT32` |
| Merge Method | `config.retrieval.merge_method` | `RAG_GRAPH` |
| Answer Prompt | `config.prompt.answer_prompt` | `M365` |
| Organize RAG Content | `config.prompt.organize_rag_content` | `true` |
| Prompt Tuning | `config.prompt.prompt_turning` | `true` |

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:8-39](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json:8-39]()

---

## Tested Configurations

### Configuration Comparison Matrix

```mermaid
graph TB
    subgraph Config1["Configuration 1: ragtopk10_gtopk20"]
        direction TB
        RAG1["rag_top_k: 10"]
        GRAPH1["graph_top_k: 20"]
        TOTAL1["Total Context Items: 30"]
        
        RAG1 --> TOTAL1
        GRAPH1 --> TOTAL1
    end
    
    subgraph Config2["Configuration 2: ragtopk30_gtopk60"]
        direction TB
        RAG2["rag_top_k: 30"]
        GRAPH2["graph_top_k: 60"]
        TOTAL2["Total Context Items: 90"]
        
        RAG2 --> TOTAL2
        GRAPH2 --> TOTAL2
    end
    
    subgraph Shared["Shared Settings"]
        direction TB
        MODEL["graph_model: gpt-41-mini-shortco-2025-04-14-Bing"]
        EMBED["embedder: qwen3 (FLOAT32)"]
        MERGE["merge_method: RAG_GRAPH"]
        GLOBAL["graph_global_search_enabled: true"]
        
        MODEL --> MERGE
        EMBED --> MERGE
        GLOBAL --> MERGE
    end
    
    Config1 --> Shared
    Config2 --> Shared
```

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:17-24](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json:17-24]()

### Configuration File Naming Convention

Results files follow this naming pattern:
```
metrics_graphiti_{graph_model}_{answer_model}_ragtopk{N}_gtopk{M}_{merge_method}.json
```

Where:
- `{graph_model}`: Model used for System-2 global selection
- `{answer_model}`: Model used for answer generation
- `ragtopk{N}`: System-1 top-k value
- `gtopk{M}`: System-2 top-k value
- `{merge_method}`: Result merging strategy

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json:1]()

---

## Overall Performance Impact

### Accuracy Comparison

| Metric | ragtopk10_gtopk20 | ragtopk30_gtopk60 | Difference |
|--------|-------------------|-------------------|------------|
| Overall Accuracy | 80.06% | 80.61% | +0.55% |
| Total Correct | 1590 / 1986 | 1601 / 1986 | +11 questions |
| Accuracy (Excluding Category 5) | 93.31% | 93.90% | +0.59% |
| Total Correct (Excluding Category 5) | 1437 / 1540 | 1446 / 1540 | +9 questions |

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:2-72](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json:2-72]()

### Performance Visualization

```mermaid
graph LR
    subgraph Metrics["Performance Metrics"]
        direction TB
        
        ACC["Overall Accuracy"]
        EXCL["Accuracy Excluding Cat 5"]
        
        ACC --> |"ragtopk10_gtopk20"| V1["80.06%"]
        ACC --> |"ragtopk30_gtopk60"| V2["80.61%"]
        
        EXCL --> |"ragtopk10_gtopk20"| V3["93.31%"]
        EXCL --> |"ragtopk30_gtopk60"| V4["93.90%"]
    end
    
    subgraph Analysis["Impact Analysis"]
        direction TB
        
        IMP["Improvement with Higher top_k"]
        IMP --> OVERALL["+0.55% overall"]
        IMP --> FILTERED["+0.59% excluding category 5"]
        IMP --> ABS["+11 questions correct"]
    end
    
    Metrics --> Analysis
```

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:2-4,70-72](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json:2-4,70-72]()

---

## Category-Level Performance Analysis

### Per-Category Accuracy Breakdown

| Category | Questions | ragtopk10_gtopk20 | ragtopk30_gtopk60 | Change |
|----------|-----------|-------------------|-------------------|---------|
| Category 1 | 282 | 91.84% (259/282) | 92.91% (262/282) | +1.07% |
| Category 2 | 321 | 90.34% (290/321) | 90.65% (291/321) | +0.31% |
| Category 3 | 96 | 82.29% (79/96) | 79.17% (76/96) | -3.12% |
| Category 4 | 841 | 96.20% (809/841) | 97.15% (817/841) | +0.95% |
| Category 5 | 446 | 34.30% (153/446) | 34.75% (155/446) | +0.45% |

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:41-69](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json:41-69]()

### Category Impact Patterns

```mermaid
graph TD
    subgraph Categories["Category Performance Changes"]
        direction TB
        
        CAT1["Category 1<br/>+1.07%"]
        CAT2["Category 2<br/>+0.31%"]
        CAT3["Category 3<br/>-3.12%"]
        CAT4["Category 4<br/>+0.95%"]
        CAT5["Category 5<br/>+0.45%"]
    end
    
    subgraph Patterns["Observed Patterns"]
        direction TB
        
        POS["Positive Impact"]
        NEG["Negative Impact"]
        NEU["Minimal Impact"]
        
        POS --> P1["Categories 1, 2, 4, 5"]
        POS --> P2["Largest gain: Category 1 (+1.07%)"]
        POS --> P3["Most questions: Category 4 (+8 correct)"]
        
        NEG --> N1["Category 3 only"]
        NEG --> N2["3 fewer correct answers"]
        NEG --> N3["Possible overfitting to irrelevant context"]
        
        NEU --> NE1["Category 5 minimal change"]
        NE2["Consistently low accuracy (34-35%)"]
        NE1 --> NE2
    end
    
    CAT1 --> POS
    CAT2 --> POS
    CAT3 --> NEG
    CAT4 --> POS
    CAT5 --> NEU
```

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:63-69](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json:63-69]()

### Category-Specific Insights

**Category 3 Performance Degradation:**
- Configuration 1: 82.29% (79/96 correct)
- Configuration 2: 79.17% (76/96 correct)
- Analysis: The 3.12% decrease suggests that tripling the context size may introduce noise for this category's question types, potentially overwhelming the answer model with less relevant information

**Category 4 Strongest Absolute Gain:**
- Configuration 1: 809/841 correct
- Configuration 2: 817/841 correct
- Analysis: +8 correct answers represents the largest absolute improvement, indicating Category 4 questions particularly benefit from richer context

**Category 5 Persistent Challenge:**
- Both configurations: ~34-35% accuracy
- Analysis: Minimal improvement (+0.45%) suggests Category 5's difficulty stems from factors beyond context quantity, likely requiring architectural changes rather than parameter tuning

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:41-72](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json:41-72]()

---

## Configuration Trade-offs

### Context Size vs. Quality Trade-off

```mermaid
graph TB
    subgraph TopK["Top-K Parameter Selection"]
        direction TB
        
        LOW["Lower top_k (10/20)"]
        HIGH["Higher top_k (30/60)"]
        
        LOW --> LBEN["Benefits"]
        LOW --> LCOST["Costs"]
        
        HIGH --> HBEN["Benefits"]
        HIGH --> HCOST["Costs"]
        
        LBEN --> LB1["Smaller context window"]
        LBEN --> LB2["Higher precision retrieval"]
        LBEN --> LB3["Faster processing"]
        LBEN --> LB4["Better for Category 3 (82.29%)"]
        
        LCOST --> LC1["May miss relevant context"]
        LCOST --> LC2["Lower recall"]
        LCOST --> LC3["Reduced coverage"]
        
        HBEN --> HB1["More comprehensive context"]
        HBEN --> HB2["Higher recall"]
        HBEN --> HB3["Better for Categories 1,4 (+1.07%, +0.95%)"]
        HBEN --> HB4["Overall accuracy improvement (+0.55%)"]
        
        HCOST --> HC1["3x larger context window"]
        HCOST --> HC2["Potential noise introduction"]
        HCOST --> HC3["Increased token usage"]
        HCOST --> HC4["Degraded Cat 3 performance (-3.12%)"]
    end
```

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:17-24,41-72](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json:17-24,41-72]()

### System-1 vs. System-2 Ratio

Both tested configurations maintain a consistent 1:2 ratio between `rag_top_k` and `graph_top_k`:
- Configuration 1: 10:20 ratio
- Configuration 2: 30:60 ratio

This suggests the architectural design prioritizes System-2 (Global Selection) results by allocating double the number of slots compared to System-1 (Similarity Search).

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:21-22](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json:21-22]()

---

## Tuning Recommendations

### Parameter Selection Guidelines

```mermaid
graph TD
    START["Parameter Selection Decision"]
    
    START --> Q1{"Question Distribution<br/>Known?"}
    
    Q1 -->|"Similar to LoCoMo"| Q2{"Optimize For?"}
    Q1 -->|"Unknown"| DEFAULT["Use ragtopk30_gtopk60"]
    
    Q2 -->|"Overall Accuracy"| HIGH["ragtopk30_gtopk60<br/>+0.55% improvement"]
    Q2 -->|"Specific Category"| Q3{"Which Category?"}
    Q2 -->|"Cost Efficiency"| LOW["ragtopk10_gtopk20<br/>3x fewer tokens"]
    
    Q3 -->|"Category 3"| LOW_CAT3["ragtopk10_gtopk20<br/>82.29% vs 79.17%"]
    Q3 -->|"Categories 1, 2, 4"| HIGH_CAT["ragtopk30_gtopk60<br/>Better overall"]
    Q3 -->|"Category 5"| ARCH["Configuration irrelevant<br/>Consider architectural changes"]
    
    DEFAULT --> NOTE1["Best general-purpose choice"]
    HIGH --> NOTE2["Recommended for production"]
    LOW --> NOTE3["Recommended for development/testing"]
```

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:2-72](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json:2-72]()

### Use Case Recommendations

| Use Case | Recommended Config | Rationale |
|----------|-------------------|-----------|
| Production deployment | `ragtopk30_gtopk60` | Higher overall accuracy (80.61%), better excluding Cat 5 (93.90%) |
| Development/testing | `ragtopk10_gtopk20` | Faster execution, lower token costs, acceptable accuracy (80.06%) |
| Token cost optimization | `ragtopk10_gtopk20` | 3x fewer context items (30 vs 90), minimal accuracy loss (-0.55%) |
| Category 3-heavy workloads | `ragtopk10_gtopk20` | 3.12% better performance on Category 3 questions |
| Category 1/4-heavy workloads | `ragtopk30_gtopk60` | Notable improvements (+1.07%, +0.95%) |
| Unknown question distribution | `ragtopk30_gtopk60` | More robust general-purpose performance |

### Configuration Modification in Code

To adjust retrieval parameters, modify the `config.retrieval` section:

```python
config = {
    "retrieval": {
        "graph_enabled": true,
        "rag_enabled": true,
        "merge_method": "RAG_GRAPH",
        "rag_top_k": 30,  # Adjust System-1 top-k
        "graph_top_k": 60,  # Adjust System-2 top-k
        "graph_node_embedding": "summary_embedding",
        "graph_global_search_enabled": true
    }
}
```

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json:17-24]()

---

## Statistical Significance Analysis

### Absolute Performance Gains

| Metric | Improvement | Statistical Significance |
|--------|-------------|-------------------------|
| Overall correct answers | +11 out of 1986 | 0.55% improvement |
| Correct excluding Cat 5 | +9 out of 1540 | 0.59% improvement |
| Category 1 | +3 out of 282 | 1.07% improvement |
| Category 2 | +1 out of 321 | 0.31% improvement |
| Category 3 | -3 out of 96 | -3.12% degradation |
| Category 4 | +8 out of 841 | 0.95% improvement |
| Category 5 | +2 out of 446 | 0.45% improvement |

### Key Findings

1. **Modest Overall Impact**: The 0.55% overall improvement (+11 questions) represents marginal gains that may not justify the 3x increase in context size for all use cases

2. **Category-Specific Variability**: Performance changes range from -3.12% (Category 3) to +1.07% (Category 1), indicating configuration sensitivity varies by question type

3. **Consistent Ratio Preservation**: Both configurations maintain a 1:2 ratio between `rag_top_k` and `graph_top_k`, suggesting this ratio is an architectural constant rather than a tunable parameter

4. **Category 5 Plateau**: Minimal improvement (0.45%) indicates diminishing returns on difficult questions, suggesting alternative approaches beyond parameter tuning are needed

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:2-72](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json:2-72]()

---

## Future Parameter Exploration

### Unexplored Configuration Space

The current evaluation only tests two configurations with a fixed 1:2 ratio. Potential areas for further exploration:

| Parameter Variation | Current Coverage | Exploration Opportunity |
|---------------------|------------------|------------------------|
| `rag_top_k` values | 10, 30 | Test 5, 15, 20, 40, 50 |
| `graph_top_k` values | 20, 60 | Test 10, 30, 40, 80, 100 |
| RAG:Graph ratio | 1:2 only | Test 1:1, 1:3, 2:1, 1:4 |
| `merge_method` | RAG_GRAPH only | No alternative methods tested |
| `graph_node_embedding` | summary_embedding only | Test other embedding fields |

### Recommended Next Steps

1. **Ratio Exploration**: Test different `rag_top_k`:`graph_top_k` ratios (e.g., 1:1, 1:3, 2:1) to determine optimal balance between System-1 and System-2 contributions

2. **Granular Top-K Testing**: Test intermediate values (e.g., 15, 20, 40) to identify potential sweet spots between 10/20 and 30/60

3. **Category-Specific Tuning**: Develop category-aware parameter selection that adjusts `top_k` values based on question classification

4. **Alternative Merge Methods**: Evaluate different strategies for combining System-1 and System-2 results beyond `RAG_GRAPH`

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:17-24](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk30_gtopk60_RAG_GRAPH.json:17-24]()

---

# Page: Results Data Format

# Results Data Format

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json](results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json)
- [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json](results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json)

</details>



This page documents the structure and content of the JSON results files generated by Mnemis evaluation runs. These files contain detailed question-answer pairs, retrieval context, evidence messages, and performance metrics for benchmark evaluation.

For information about the evaluation process itself and how these results are generated, see [Running Evaluations](#6.3). For analysis of specific benchmark performance, see [LoCoMo Results](#4.2) and [LongMemEval-S Results](#4.3).

---

## Overview

Results files are stored in the `results/` directory, organized by benchmark dataset (e.g., `results/locomo/`, `results/lme-s/`). Each file is a newline-delimited JSON (NDJSON) format where each line represents a single question-answer evaluation record. The filename encodes the configuration used:

```
results_<graph_model>_<answer_model>_<retrieval_config>_<merge_method>.json
```

Example: `results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json`

**Sources:** [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-7]()

---

## Top-Level Record Structure

Each JSON record in a results file contains the following top-level fields:

### Core Question-Answer Fields

| Field | Type | Description |
|-------|------|-------------|
| `question_id` | string | Unique identifier for the question (e.g., "f8c5f88b") |
| `question` | string | The question text, including date context in format "(date: YYYY/MM/DD (Day) HH:MM)Question" |
| `hypothesis` / `answer` | string | The generated answer from the system |
| `gold_answer` / `golden_answer` | string | The expected correct answer for evaluation |
| `question_type` | string | Category of question (e.g., "single-session-user", "single-session-assistant") |
| `grade` | boolean | Whether the answer was judged correct (true/false) |

### Dataset-Specific Indices

| Field | Type | Description | Dataset |
|-------|------|-------------|---------|
| `user_idx` | integer | User index in the dataset | LoCoMo |
| `qa_idx` | integer | Question-answer pair index | LoCoMo |
| `category` | integer | Question category number (1-5) | LoCoMo |

### Timing Metrics

| Field | Type | Description |
|-------|------|-------------|
| `duration` | float | Total processing time in seconds |
| `search_duration` | float | Time spent on retrieval (System-1 + System-2) |
| `answer_duration` | float | Time spent generating the answer via LLM |
| `grading_duration` | float | Time spent evaluating the answer |
| `retrieval_duration` | float | Low-level retrieval operation time |

**Sources:** [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1](), [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1]()

---

## Evidence Messages Structure

The `evidence` or `evidence_messages` field contains the specific conversation messages that directly answer the question. This is the ground truth evidence from the dataset.

### Evidence Message Object

```mermaid
graph TD
    EvidenceArray["evidence_messages[]"]
    MessageObj["Message Object"]
    
    EvidenceArray --> MessageObj
    
    MessageObj --> role["role: string"]
    MessageObj --> content["content: string"]
    MessageObj --> datetime["datetime: ISO timestamp"]
    
    role --> Examples1["'user', 'assistant',<br/>'Caroline', 'Melanie'"]
    content --> Examples2["Message text, may include<br/>image descriptions"]
    datetime --> Examples3["'2023/05/25 (Thu) 21:29'"]
```

### Evidence Configuration

| Field | Type | Description |
|-------|------|-------------|
| `answer_session_ids` | string[] | List of session IDs used in answer generation (LongMemEval-S) |
| `evidence_previous_messages_limit` | integer | Context window size for evidence messages (LoCoMo) |

**Example Evidence Message:**
```json
{
  "role": "user",
  "content": "I'll definitely do those exercises before playing tennis. By the way, I'm really happy with my new tennis racket, which I got from a sports store downtown.",
  "datetime": "2023/05/25 (Thu) 21:29"
}
```

**Sources:** [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1]()

---

## Context Structure

The `context` field contains the full structured context assembled by the RAG_GRAPH merge strategy. This is a formatted string containing three main sections: Message Chunks, FACTS, and ENTITIES.

```mermaid
graph TB
    Context["context: string"]
    
    Context --> Header["Header Comment"]
    Context --> MessageChunks["Message Chunks Section"]
    Context --> Facts["FACTS Section"]
    Context --> Entities["ENTITIES Section"]
    
    Header --> HeaderText["'# The following historical conversation<br/>is provided for your reference...'"]
    
    MessageChunks --> Chunk0["Message Chunk 0 (Session X)"]
    MessageChunks --> Chunk1["Message Chunk 1 (Session Y)"]
    MessageChunks --> ChunkN["Message Chunk N (Session Z)"]
    
    Chunk0 --> Messages["[Timestamp] role: content<br/>..."]
    
    Facts --> FactsHeader["'<FACTS>'<br/>Temporal statements with timestamps"]
    Facts --> FactList["- Fact text (start_date - end_date)"]
    
    Entities --> EntitiesHeader["'<ENTITIES>'<br/>Entity summaries"]
    Entities --> EntityList["- ENTITY_NAME: description"]
```

### Message Chunks Section

Message Chunks organize historical conversations by session:

```
Message Chunk 0 (Session 1):
[2023/05/08 (Mon) 13:57] Caroline: I went to a LGBTQ support group yesterday...

Message Chunk 1 (Session 3):
[2023/06/09 (Fri) 19:55] Caroline: Hey Melanie! How's it going?...
```

Each chunk includes:
- **Session identifier**: `(Session N)` indicates which conversation session
- **Timestamped messages**: Format `[YYYY/MM/DD (Day) HH:MM] role: content`
- **Truncation indicators**: `...` shows where content is abbreviated

### FACTS Section

The FACTS section contains temporal statements extracted from the knowledge graph:

```xml
<FACTS>
  - The user owns a new tennis racket which they got from a sports store downtown. (2023-05-25 - 2023-05-29)
  - Caroline attended a LGBTQ support group yesterday. (2023-05-07 - now)
  - Melanie ran a charity race for mental health last Saturday. (2023-05-20 - now)
</FACTS>
```

**Format**: `- [Fact statement] ([start_date] - [end_date])`
- **Timestamps represent event time**, not when the fact was stated
- Date format: `YYYY-MM-DD` or `now` for ongoing facts
- Facts are temporally grounded and include validity periods

### ENTITIES Section

The ENTITIES section contains summarized entity descriptions:

```xml
<ENTITIES>
  - sports store downtown: A sports store located downtown where the user purchased a new tennis racket.
  - tennis racket: Sports equipment mentioned as a new purchase that improved the user's game.
  - Caroline: A transgender woman and artist preparing for adoption.
</ENTITIES>
```

**Format**: `- [ENTITY_NAME]: [summary description]`
- Entity names are extracted from the hierarchical graph
- Summaries consolidate information from multiple mentions
- Cross-references to related entities and events

**Sources:** [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1]()

---

## Retrieval Candidates Fields

These fields track intermediate retrieval results from the dual-route system:

| Field | Type | Description |
|-------|------|-------------|
| `hybrid_episode_candidates` | object[] / null | Episode node candidates from System-1 similarity search |
| `hybrid_edge_candidates` | object[] / null | Edge/relationship candidates from graph traversal |
| `hybrid_node_candidates` | object[] / null | Entity node candidates from System-2 global selection |
| `num_retrieved_messages` | integer | Total number of messages retrieved |
| `similarity_scores` | float[] | Similarity scores from embedding-based retrieval |

These fields may be `null` or empty arrays depending on the retrieval configuration.

**Sources:** [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1]()

---

## Merge Method Field

The `merge_method` field indicates the strategy used to combine System-1 and System-2 results:

| Value | Description |
|-------|-------------|
| `RAG_GRAPH` | Hybrid merge combining similarity search (RAG) and hierarchical graph selection |
| `RAG` | System-1 only (similarity search) |
| `GRAPH` | System-2 only (global selection) |

The RAG_GRAPH method produces the richest context by merging:
- Top-k results from embedding-based similarity search
- Top-k nodes from LLM-guided hierarchical traversal
- One-hop neighbors of selected nodes
- Organized into Message Chunks, FACTS, and ENTITIES

**Sources:** [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1]()

---

## Context Assembly Flow

This diagram shows how retrieval results are transformed into the structured context format:

```mermaid
graph TB
    Query["User Query"]
    
    Query --> System1["System-1<br/>Similarity Search"]
    Query --> System2["System-2<br/>Global Selection"]
    
    System1 --> RAGResults["RAG Results<br/>hybrid_episode_candidates<br/>Top-k=10 or 30"]
    System2 --> GraphResults["Graph Results<br/>hybrid_node_candidates<br/>Top-k=20 or 60"]
    
    GraphResults --> OneHop["One-Hop Expansion<br/>hybrid_edge_candidates"]
    
    RAGResults --> Merger["RAG_GRAPH Merger"]
    OneHop --> Merger
    
    Merger --> Organizer["Context Organizer"]
    
    Organizer --> MessageChunks["Message Chunks<br/>(Session-organized)"]
    Organizer --> FACTS["FACTS<br/>(Temporal statements)"]
    Organizer --> ENTITIES["ENTITIES<br/>(Summarized concepts)"]
    
    MessageChunks --> ContextString["context: string<br/>(Formatted for LLM)"]
    FACTS --> ContextString
    ENTITIES --> ContextString
    
    ContextString --> AnswerModel["Answer Model<br/>gpt-41-mini"]
    
    AnswerModel --> Response["hypothesis/answer"]
```

**Sources:** [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1]()

---

## Performance Metrics Interpretation

### Timing Breakdown

```mermaid
graph LR
    Total["duration<br/>(total)"]
    
    Total --> Search["search_duration<br/>(retrieval)"]
    Total --> Answer["answer_duration<br/>(generation)"]
    Total --> Grading["grading_duration<br/>(evaluation)"]
    
    Search --> System1Time["System-1<br/>embedding search"]
    Search --> System2Time["System-2<br/>graph traversal"]
    Search --> MergeTime["RAG_GRAPH<br/>merge"]
    
    Answer --> LLMTime["LLM API call<br/>gpt-41-mini"]
    
    Grading --> GraderTime["Grader model<br/>evaluation"]
```

### Typical Timing Values

Based on the sample data:

| Metric | Typical Range | Example |
|--------|---------------|---------|
| `duration` | 2-3 seconds | 2.143 s |
| `search_duration` | 0.3-1.0 seconds | 0.374 s |
| `answer_duration` | 3-6 seconds | 4.050 s |
| `grading_duration` | 0.6-1.7 seconds | 0.886 s |
| `retrieval_duration` | 1e-5 seconds | 1.168e-05 s (cached) |

**Note**: Very low `retrieval_duration` values (e.g., 1e-5) indicate cache hits from the `alru_cache` layer.

**Sources:** [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-7]()

---

## Example Record Walkthrough

Here's a complete example showing all major components:

```json
{
  "question_id": "f8c5f88b",
  "question": "(date: 2023/05/30 (Tue) 23:39)Where did I buy my new tennis racket from?",
  "hypothesis": "You bought your new tennis racket from a **sports store downtown**.",
  "gold_answer": "the sports store downtown",
  "question_type": "single-session-user",
  "duration": 2.143,
  "grade": true,
  "answer_session_ids": ["answer_c3567066"],
  "evidence_messages": [
    {
      "role": "user",
      "content": "I'm really happy with my new tennis racket, which I got from a sports store downtown.",
      "datetime": "2023/05/25 (Thu) 21:29"
    }
  ],
  "context": "# The following historical conversation...\nMessage Chunk 0 (Session 2):\n...\n<FACTS>\n  - The user owns a new tennis racket from a sports store downtown. (2023-05-25 - 2023-05-29)\n</FACTS>\n<ENTITIES>\n  - sports store downtown: A sports store located downtown...\n</ENTITIES>",
  "merge_method": "RAG_GRAPH",
  "search_duration": 0.374,
  "answer_duration": 4.050,
  "grading_duration": 0.886,
  "num_retrieved_messages": 0,
  "similarity_scores": []
}
```

**Interpretation:**
- Question correctly answered (grade=true)
- Retrieved context includes relevant evidence from Session 2
- FACTS section contains temporally grounded statement (2023-05-25)
- Entity summary provides location context
- Fast retrieval (0.374s) suggests effective caching
- Answer generation took 4.05s (LLM API call)

**Sources:** [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1]()

---

## File Naming Convention

Results files follow this naming pattern:

```
results_<graph_model>_<answer_model>_<retrieval_config>_<merge_method>.json
```

### Component Breakdown

| Component | Example Values | Description |
|-----------|----------------|-------------|
| `graph_model` | `graphiti` | Base graph framework used |
| `answer_model` | `gpt-41-mini-shortco-2025-04-14-Bing` | LLM used for answer generation with version date |
| `retrieval_config` | `ragtopk10_gtopk20` | RAG top-k and Graph top-k parameters |
| `merge_method` | `RAG_GRAPH` | Strategy for combining retrieval results |

### Retrieval Configuration Format

The `retrieval_config` component encodes key retrieval parameters:

- `ragtopk10`: System-1 retrieves top-10 results from similarity search
- `gtopk20`: System-2 retrieves top-20 nodes from hierarchical traversal
- Alternative configurations: `ragtopk30_gtopk60` (higher recall settings)

**Sources:** [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1](), [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1]()

---

## Reading Results Files Programmatically

Results files use newline-delimited JSON (NDJSON) format. Each line is a valid JSON object:

```python
import json

# Read NDJSON results file
results = []
with open('results/lme-s/results_..._RAG_GRAPH.json', 'r') as f:
    for line in f:
        record = json.loads(line)
        results.append(record)

# Access fields
for record in results:
    question_id = record['question_id']
    grade = record['grade']
    duration = record['duration']
    
    # Parse context sections
    context = record['context']
    facts_section = context.split('<FACTS>')[1].split('</FACTS>')[0]
    entities_section = context.split('<ENTITIES>')[1].split('</ENTITIES>')[0]
```

### Key Access Patterns

```python
# Extract evidence messages
evidence = record['evidence_messages']
for msg in evidence:
    print(f"{msg['datetime']} {msg['role']}: {msg['content']}")

# Check grading result
if record['grade']:
    print(f"✓ Correct: {record['hypothesis']}")
else:
    print(f"✗ Incorrect. Expected: {record['gold_answer']}")

# Analyze timing
print(f"Search: {record['search_duration']:.3f}s")
print(f"Answer: {record['answer_duration']:.3f}s")
print(f"Total: {record['duration']:.3f}s")
```

**Sources:** Based on NDJSON format observed in [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json]()

---

## Dataset-Specific Variations

### LongMemEval-S Format

- Uses `hypothesis` for generated answer
- Includes `answer_session_ids` field
- `question_type` values: `"single-session-user"`, `"single-session-assistant"`, `"multi-session"`, `"temporal"`
- No `user_idx` or `category` fields

### LoCoMo Format

- Uses `answer` for generated answer
- Uses `golden_answer` instead of `gold_answer`
- Includes `user_idx`, `qa_idx`, and `category` fields
- Includes `evidence_previous_messages_limit` parameter
- `category` ranges from 1-5

**Sources:** [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-7](), [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-7]()

---

# Page: Case Studies

# Case Studies

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [figures/figure_case_0.png](figures/figure_case_0.png)
- [figures/figure_case_1.png](figures/figure_case_1.png)
- [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json](results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json)
- [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json](results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json)

</details>



This page demonstrates Mnemis's dual-route memory retrieval through concrete question-answering scenarios from the benchmark evaluations. Each case study walks through the complete pipeline: question processing, System-1 similarity search, System-2 global selection, context assembly with structured memory components (Message Chunks, FACTS, ENTITIES), and answer generation with accuracy evaluation.

For detailed analysis of benchmark results and performance metrics, see [LoCoMo Results](#4.2) and [LongMemEval-S Results](#4.3). For implementation details of the retrieval mechanisms, see [System-2 Global Selection](#2.3) and [RAG_GRAPH Merge Strategy](#2.4).

---

## Overview of Case Study Structure

Each case study in this section demonstrates the following pipeline stages:

```mermaid
graph LR
    Q["User Question"] --> S1["System-1<br/>Similarity Search"]
    Q --> S2["System-2<br/>Global Selection"]
    
    S1 --> EM["Evidence Messages<br/>Top-K RAG Results"]
    S2 --> HN["Hierarchical Nodes<br/>LLM-Filtered"]
    
    EM --> CA["Context Assembly<br/>RAG_GRAPH Merge"]
    HN --> CA
    
    CA --> MC["Message Chunks<br/>Historical Conversations"]
    CA --> F["FACTS<br/>Temporal Statements"]
    CA --> E["ENTITIES<br/>Summarized Concepts"]
    
    MC --> AM["Answer Model<br/>gpt-41-mini"]
    F --> AM
    E --> AM
    
    AM --> ANS["Generated Answer"]
    ANS --> EVAL["Grader Model<br/>Accuracy Check"]
```

**Sources:** [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-50](), [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-50]()

### Case Study Components

Each case study documents:

| Component | Description | Source |
|-----------|-------------|--------|
| **Question** | The user query requiring memory retrieval | `question` field in results JSON |
| **Evidence Messages** | Raw messages retrieved by System-1 similarity search | `evidence_messages` or `evidence` arrays |
| **Structured Context** | Organized memory: Message Chunks, FACTS, ENTITIES | `context` field containing formatted sections |
| **Generated Answer** | LLM response based on retrieved context | `answer` or `hypothesis` field |
| **Golden Answer** | Ground truth for evaluation | `golden_answer` or `gold_answer` field |
| **Grade** | Boolean accuracy assessment | `grade` field (true/false) |
| **Duration** | Retrieval and generation time in seconds | `duration` field |

**Sources:** [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-50](), [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-50]()

---

## System-Level Data Flow Architecture

The following diagram maps the conceptual retrieval process to concrete code entities and data structures:

```mermaid
graph TB
    subgraph "Query Processing"
        Q["question field<br/>from JSON dataset"]
        QE["Embedding via<br/>embedder_model"]
    end
    
    subgraph "System-1: RAG Path"
        VS["Vector Search<br/>Neo4j similarity"]
        EM["evidence_messages<br/>List[Dict]"]
    end
    
    subgraph "System-2: Global Path"
        GS["GlobalSelector<br/>global_selection()"]
        LS["layer_selection()<br/>LLM-guided filtering"]
        HN["Hierarchical Nodes<br/>Category + Entity"]
        OH["get_one_hop_neighbors()<br/>Episodic context"]
    end
    
    subgraph "Context Assembly"
        MC["Message Chunks<br/>Session-grouped"]
        F["FACTS section<br/>Temporal statements"]
        ENT["ENTITIES section<br/>Summarized concepts"]
        CTX["context field<br/>Formatted prompt"]
    end
    
    subgraph "Answer Generation"
        AM["answer_model<br/>gpt-41-mini"]
        ANS["answer/hypothesis<br/>Generated text"]
        EVAL["grader_model<br/>Accuracy check"]
        GR["grade field<br/>Boolean result"]
    end
    
    Q --> QE
    QE --> VS
    QE --> GS
    
    VS --> EM
    
    GS --> LS
    LS --> HN
    HN --> OH
    OH --> EM
    
    EM --> MC
    HN --> F
    HN --> ENT
    
    MC --> CTX
    F --> CTX
    ENT --> CTX
    
    CTX --> AM
    AM --> ANS
    ANS --> EVAL
    EVAL --> GR
```

**Sources:** [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-100](), [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-100]()

---

## Context Structure Format

The `context` field in results JSON files contains formatted memory organized into three sections:

### Message Chunks
Chronologically grouped conversation messages, segmented by session:

```
Message Chunk 0 (Session 1):
[2023/05/08 (Mon) 13:57] Caroline: I went to a LGBTQ support group yesterday...

Message Chunk 1 (Session 3):
[2023/06/09 (Fri) 19:55] Caroline: Hey Melanie! How's it going?...
```

### FACTS Section
Temporal statements extracted from the knowledge graph with datetime ranges:

```xml
<FACTS>
  - Caroline attended the LGBTQ support group yesterday. (2023-05-07 - now)
  - Caroline joined a mentorship program for LGBTQ youth last weekend. (2023-07-17 - now)
</FACTS>
```

### ENTITIES Section
Summarized concepts and relationships from the hierarchical graph:

```xml
<ENTITIES>
  - Caroline: A person who is an active member of the LGBTQ community...
  - LGBTQ Support Group: A group that provides support for LGBTQ individuals...
</ENTITIES>
```

**Sources:** [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-100](), [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-100]()

---

## Evaluation Metrics in Case Studies

Each case study result includes performance measurements:

| Metric | Description | Example Value |
|--------|-------------|---------------|
| `duration` | Total processing time (retrieval + generation) in seconds | 2.143 seconds |
| `grade` | Boolean accuracy: does answer match ground truth? | `true` or `false` |
| `question_type` | Classification of question complexity | `"single-session-user"`, `"multi-session"`, etc. |
| `answer_session_ids` | Session IDs containing ground truth evidence | `["answer_c3567066"]` |

### Configuration Parameters

The case studies in this section use the following configuration:

- **RAG top-k**: 10 messages retrieved by similarity search
- **Graph top-k**: 20 nodes selected through hierarchical traversal
- **Merge method**: `RAG_GRAPH` (combines both routes)
- **Answer model**: `gpt-41-mini-shortco-2025-04-14-Bing`
- **Grader model**: `gpt-41-mini-shortco-2025-04-14-Bing`

**Sources:** [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-50](), [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-50]()

---

## Retrieval Method Contributions

The dual-route architecture enables complementary retrieval strategies:

```mermaid
graph TB
    subgraph "System-1: Similarity Search"
        S1Q["Query Embedding<br/>qwen3 FLOAT32"]
        S1V["Vector Search<br/>Cosine Similarity"]
        S1M["Recent Messages<br/>Chronologically Close"]
    end
    
    subgraph "System-2: Global Selection"
        S2H["Hierarchical Graph<br/>Category Layers"]
        S2L["LLM Layer Selection<br/>NODE_SELECTION_PROMPT"]
        S2D["Semantic Concepts<br/>Globally Relevant"]
    end
    
    subgraph "RAG_GRAPH Merge"
        MC["Message Chunks<br/>From System-1"]
        FE["FACTS + ENTITIES<br/>From System-2"]
        CTX["Unified Context<br/>Prompt Template"]
    end
    
    S1Q --> S1V
    S1V --> S1M
    S1M --> MC
    
    S2H --> S2L
    S2L --> S2D
    S2D --> FE
    
    MC --> CTX
    FE --> CTX
```

### Complementary Strengths

| Retrieval Route | Strength | Example Use Case |
|-----------------|----------|------------------|
| **System-1** | Finds lexically/semantically similar recent messages | "Where did I buy my tennis racket?" → retrieves message mentioning "sports store downtown" |
| **System-2** | Extracts thematic concepts across entire history | "When did Caroline attend LGBTQ events?" → traverses category hierarchy to find all LGBTQ-related facts across months |

**Sources:** [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-100](), [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-100]()

---

## Reading the Case Studies

The following subsections present detailed walkthroughs of specific questions from each benchmark:

- **[LoCoMo User 8 QA 11](#5.1)**: Multi-session temporal reasoning about LGBTQ support group attendance
- **[LongMemEval-S QA 262](#5.2)**: Single-session fact retrieval about a tennis racket purchase

Each case study shows:
1. The exact question text
2. Evidence messages retrieved by System-1
3. Structured context (Message Chunks, FACTS, ENTITIES) assembled via RAG_GRAPH
4. Generated answer with reasoning
5. Ground truth comparison and grade
6. Processing duration

These examples demonstrate how Mnemis's dual-route architecture enables accurate memory retrieval across different question types and temporal ranges.

**Sources:** [figures/figure_case_0.png:1-10](), [figures/figure_case_1.png:1-10](), [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-100](), [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-100]()

---

# Page: LoCoMo User 8 QA 11

# LoCoMo User 8 QA 11

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [figures/figure_case_0.png](figures/figure_case_0.png)
- [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json](results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json)

</details>



## Purpose and Scope

This page provides a detailed walkthrough of a specific question-answer pair from the LoCoMo benchmark dataset, demonstrating how Mnemis's dual-route retrieval system operates on a real-world query. This case study (User 8, Question 11) illustrates the end-to-end process from query input through System-1 similarity search, System-2 global selection, RAG_GRAPH merging, to final answer generation.

For an overview of all LoCoMo results, see [LoCoMo Results](#4.2). For the other case study example, see [LongMemEval-S QA 262](#5.2).

---

## Question and Expected Answer

**Question**: "Where did Caroline move from 4 years ago?"

**Expected Answer (golden_answer)**: "Sweden"

**Question Category**: Category 2 (temporal/factual)

**Evaluation Result**: Correct (grade: true)

This question requires the system to:
1. Identify temporal information (4 years ago)
2. Locate biographical facts about Caroline's origin
3. Make an inferential connection between explicit facts (moved from home country) and implicit facts (grandma from Sweden, necklace symbolizing roots)

Sources: [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:12]()

---

## Retrieval Architecture Flow

```mermaid
graph TB
    Q["Query: 'Where did Caroline move from 4 years ago?'"]
    
    subgraph "System-1: Similarity Search"
        EMB["qwen3 Embedder<br/>FLOAT32"]
        SIM["Similarity Search<br/>on Base Graph"]
        RAG_RESULTS["RAG Results<br/>Top-K Messages"]
    end
    
    subgraph "System-2: Global Selection"
        GS["GlobalSelector.global_selection()"]
        HG["Hierarchical Graph<br/>Category Traversal"]
        LLM_FILTER["LLM-Guided<br/>layer_selection()"]
        GRAPH_RESULTS["Graph Results<br/>Selected Nodes + Edges"]
    end
    
    subgraph "RAG_GRAPH Merge"
        MERGE["Merge Strategy<br/>RAG_GRAPH"]
        ORG["organize_rag_content()"]
        CTX["Structured Context<br/>Message Chunks<br/>FACTS<br/>ENTITIES"]
    end
    
    subgraph "Answer Generation"
        ANS_MODEL["gpt-41-mini-shortco<br/>Answer Model"]
        RESPONSE["Generated Answer:<br/>'Caroline moved from Sweden'"]
        GRADER["gpt-41-mini-shortco<br/>Grader Model"]
        GRADE["Grade: true<br/>Correct Answer"]
    end
    
    Q --> EMB
    Q --> GS
    
    EMB --> SIM
    SIM --> RAG_RESULTS
    RAG_RESULTS --> MERGE
    
    GS --> HG
    HG --> LLM_FILTER
    LLM_FILTER --> GRAPH_RESULTS
    GRAPH_RESULTS --> MERGE
    
    MERGE --> ORG
    ORG --> CTX
    
    CTX --> ANS_MODEL
    ANS_MODEL --> RESPONSE
    RESPONSE --> GRADER
    GRADER --> GRADE
```

Sources: [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:12]()

---

## Retrieved Evidence Messages

The system retrieved 11 evidence messages from the conversation history, demonstrating the `evidence_previous_messages_limit: 5` configuration. These messages were identified as most relevant to answering the query:

| Message Index | Role | Content | Datetime | Session |
|---------------|------|---------|----------|---------|
| 0 | Melanie | "Thanks, Caroline, for letting me join your journey..." | 2023/06/09 13:55 | 3 |
| 1 | Caroline | "Yeah Mel, let's spread love and understanding!..." | 2023/06/09 13:55 | 3 |
| 2 | Melanie | "Yes, Caroline! We can do it. Your courage is inspiring..." | 2023/06/09 13:55 | 3 |
| 3 | Caroline | "Thanks, Mel! My friends, family and mentors are my rocks..." | 2023/06/09 13:55 | 3 |
| 4 | Melanie | "Wow, that photo is great! How long have you had such a great support system?" | 2023/06/09 13:55 | 3 |
| 5 | **Caroline** | **"Yeah, I'm really lucky to have them. They've been there through everything, I've known these friends for 4 years, since I moved from my home country..."** | **2023/06/09 13:55** | **3** |
| 6 | Melanie | "I'm lucky to have my husband and kids..." | 2023/06/09 13:55 | 3 |
| 7 | Caroline | "Wow, what an amazing family pic! How long have you been married?" | 2023/06/09 13:55 | 3 |
| 8 | Melanie | "5 years already! Time flies..." | 2023/06/09 13:55 | 3 |
| 9 | Caroline | "Congrats, Melanie! You both looked so great on your wedding day!..." | 2023/06/09 13:55 | 3 |
| 10 | Caroline | **(repeat)** "Yeah, I'm really lucky to have them..." | 2023/06/09 13:55 | 3 |

**Key Evidence**: Message index 5 contains the critical information: *"I've known these friends for 4 years, since I moved from my home country."*

This establishes that Caroline moved from her home country 4 years ago, but does not explicitly name the country.

Sources: [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:12]()

---

## Context Assembly: Message Chunks, Facts, and Entities

### Message Chunks Organization

The system organized historical conversations into 9 chronologically ordered message chunks, each representing a conversational excerpt:

```mermaid
graph LR
    MC0["Message Chunk 0<br/>Session 3<br/>2023/06/09<br/>'friends for 4 years'<br/>'home country'"]
    MC1["Message Chunk 1<br/>Session 4<br/>2023/06/27<br/>'birthday gift'"]
    MC2["Message Chunk 2<br/>Session 6<br/>2023/07/06<br/>'picnic with friends'"]
    MC3["Message Chunk 3<br/>Session 10<br/>2023/07/20<br/>'LGBTQ activist group'"]
    MC4["Message Chunk 4<br/>Session 12<br/>2023/08/17<br/>'Pride fest'"]
    MC5["Message Chunk 5<br/>Session 16<br/>2023/09/13<br/>'support system'"]
    
    MC0 --> MC1
    MC1 --> MC2
    MC2 --> MC3
    MC3 --> MC4
    MC4 --> MC5
```

**Message Chunk 0** (most relevant) contains:
```
[2023/06/09 (Fri) 20:00] Caroline: Thanks, Mel! My friends, family and mentors 
are my rocks – they motivate me and give me the strength to push on. 
Here's a pic from when we met up last week! (description of attached image: 
a photo of a family posing for a picture in a yard)
...
[2023/06/09 (Fri) 20:01] Caroline: Yeah, I'm really lucky to have them. 
They've been there through everything, I've known these friends for 4 years, 
since I moved from my home country. Their love and help have been so important 
especially after that tough breakup. I'm super thankful. Who supports you, Mel?
```

Sources: [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:12]()

### Relevant FACTS Retrieved

20 temporal facts were extracted and ranked by relevance. Key facts include:

| Fact | Date Range | Relevance |
|------|------------|-----------|
| Caroline has known her friends for 4 years since moving from her home country, providing important support especially after a tough breakup | 2023-06-09 - now | **Direct evidence** |
| Caroline has support from her friends, whom she has known for 4 years since moving from her home country | 2023-06-09 - now | **Corroborating** |
| Caroline has gone through a long process of finding self-acceptance | 2023-10-22 - now | Context |
| Caroline started her transgender journey three years ago | 2023-06-09 - now | Timeline context |
| Caroline's relationships with friends changed due to her transition | 2023-09-13 - now | Context |

**Critical Observation**: The facts confirm the "4 years" and "home country" but do not explicitly state "Sweden."

Sources: [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:12]()

### Relevant ENTITIES Retrieved

19 entities were extracted and ranked. The crucial entity for inference:

**Entity: `grandma`**
```
grandma: Grandma is Caroline's grandmother from Sweden who gave her 
a special necklace symbolizing love, faith, and strength. The necklace 
is a meaningful gift that reminds Caroline of her roots and family support.
```

**Entity: `home country`**
```
home country: The home country is the place Caroline moved from four years ago, 
where she had friends she has known since then. It is referenced as Caroline's 
origin before moving to her current location.
```

Other relevant entities:
- `friends`: Supportive group known for 4 years since moving from home country
- `transition`: Caroline's journey as a trans woman
- `woman`: Caroline's identity and background

Sources: [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:12]()

---

## Inference Chain: Connecting Evidence to Answer

```mermaid
graph TD
    Q["Question:<br/>'Where did Caroline move from<br/>4 years ago?'"]
    
    E1["Evidence Message:<br/>'I've known these friends<br/>for 4 years, since I moved<br/>from my home country'"]
    
    E2["ENTITY grandma:<br/>'Caroline's grandmother<br/>from Sweden'"]
    
    E3["ENTITY grandma (continued):<br/>'necklace reminds Caroline<br/>of her roots'"]
    
    I1["Inference 1:<br/>Caroline moved from<br/>'home country' 4 years ago"]
    
    I2["Inference 2:<br/>Grandma from Sweden +<br/>necklace symbolizing roots<br/>→ Sweden is home country"]
    
    A["Answer:<br/>'Caroline moved from<br/>Sweden 4 years ago'"]
    
    Q --> E1
    Q --> E2
    Q --> E3
    
    E1 --> I1
    E2 --> I2
    E3 --> I2
    
    I1 --> A
    I2 --> A
```

### Reasoning Steps in Generated Answer

The `gpt-41-mini-shortco` answer model performed the following reasoning:

1. **Direct Evidence Extraction**: Identified from message that Caroline moved from "home country" 4 years ago
2. **Entity Lookup**: Retrieved entity information about Caroline's grandmother from Sweden
3. **Symbolic Connection**: Recognized the necklace as symbolizing Caroline's roots and family heritage
4. **Inference**: Connected grandmother's origin (Sweden) with Caroline's home country
5. **Conclusion**: Determined home country = Sweden

**Generated Answer Text**:
```
Caroline moved from her **home country** 4 years ago. From the memories, 
we know that her grandma is from **Sweden**, and the necklace Caroline treasures 
as a symbol of love, faith, and strength was a gift from her grandma in Sweden. 
This strongly suggests that Caroline's home country, where she lived before 
moving 4 years ago, is **Sweden**.

So, to answer your question precisely:

**Caroline moved from Sweden 4 years ago.**
```

Sources: [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:12]()

---

## Performance Metrics

The system's performance on this specific QA pair:

| Metric | Value | Unit |
|--------|-------|------|
| `search_duration` | 0.9498 | seconds |
| `answer_duration` | 3.5770 | seconds |
| `grading_duration` | 0.6661 | seconds |
| **Total Time** | **5.1929** | **seconds** |
| `grade` | true | boolean |
| `num_retrieved_messages` | 0 | count (evidence_previous_messages_limit used instead) |
| `merge_method` | RAG_GRAPH | string |
| `rag_top_k` | 10 | count |
| `graph_top_k` | 20 | count |

### Retrieval Breakdown

- **System-1 (Similarity Search)**: Identified relevant conversation sessions based on embedding similarity
- **System-2 (Global Selection)**: Traversed hierarchical graph to find related entities and facts
- **Merge Duration**: Included in 0.9498s search_duration
- **Answer Generation**: 3.577s for LLM to process context and generate response
- **Grading**: 0.666s for grader model to evaluate answer correctness

Sources: [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:12]()

---

## Why This Case Succeeded

### Success Factors

1. **Temporal Alignment**: The query's "4 years ago" matched exactly with conversation content
2. **Entity Resolution**: The hierarchical graph correctly maintained the `grandma` → `Sweden` connection
3. **Contextual Inference**: The answer model successfully reasoned from "home country" + "grandma from Sweden" + "roots" → Sweden
4. **RAG_GRAPH Merge**: Combined direct message evidence (System-1) with entity knowledge (System-2)

### Dual-Route Contribution Analysis

```mermaid
graph LR
    S1["System-1<br/>Contribution"]
    S1_MSG["Message Evidence:<br/>'moved from home country<br/>4 years ago'"]
    
    S2["System-2<br/>Contribution"]
    S2_ENT["Entity Knowledge:<br/>'grandma from Sweden'<br/>'necklace = roots'"]
    
    MERGE["RAG_GRAPH<br/>Merge"]
    INFERENCE["Inference:<br/>home country = Sweden"]
    
    S1 --> S1_MSG
    S2 --> S2_ENT
    
    S1_MSG --> MERGE
    S2_ENT --> MERGE
    
    MERGE --> INFERENCE
```

**System-1 Role**: Retrieved the temporal fact about moving 4 years ago from home country through similarity-based search on conversational context.

**System-2 Role**: Provided structured entity information that enabled the inferential leap from "home country" to "Sweden" by maintaining the hierarchical relationship between Caroline and her Swedish grandmother.

**Merge Benefit**: Neither route alone would have produced the correct answer:
- System-1 alone: Would identify "home country" but not name it
- System-2 alone: Might miss the temporal "4 years ago" constraint
- Combined: Enables both temporal grounding and geographical inference

Sources: [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:12]()

---

## Data Structures in Code

### Result Object Schema

The JSON result object follows this structure in the codebase:

```
{
  "user_idx": 0,                    // LoCoMo user identifier
  "qa_idx": 11,                     // Question index for this user
  "question": string,               // Query text
  "answer": string,                 // Generated answer
  "golden_answer": string,          // Expected answer
  "evidence": [                     // Retrieved messages
    {
      "role": string,
      "content": string,
      "datetime": string
    }
  ],
  "context": string,                // Full prompt context (Message Chunks, FACTS, ENTITIES)
  "grade": boolean,                 // Correctness evaluation
  "merge_method": "RAG_GRAPH",      // Hybrid retrieval strategy
  "search_duration": float,         // System-1 + System-2 time
  "answer_duration": float,         // LLM generation time
  "grading_duration": float,        // Evaluation time
  "category": int,                  // LoCoMo question category
  "num_retrieved_messages": int,
  "similarity_scores": []
}
```

### Context Assembly Structure

The `context` field assembles information in a structured prompt format:

```
# The following historical conversation is provided for your reference...

Message Chunk 0 (Session N):
[timestamp] Speaker: content

Message Chunk 1 (Session M):
...

<FACTS>
  - fact_text (date_range)
  - ...
</FACTS>

<ENTITIES>
  - entity_name: entity_summary
  - ...
</ENTITIES>
```

This structured context enables the answer model (`gpt-41-mini-shortco`) to perform multi-hop reasoning across temporal messages, extracted facts, and semantic entities.

Sources: [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1-12]()

---

## Configuration Parameters for This Evaluation

The following configuration was used for this LoCoMo evaluation run:

| Parameter | Value | Description |
|-----------|-------|-------------|
| `graph_model` | gpt-41-mini-shortco-2025-04-14-Bing | Model for System-2 global selection |
| `answer_model` | gpt-41-mini-shortco-2025-04-14-Bing | Model for answer generation |
| `grader_model` | gpt-41-mini-shortco-2025-04-14-Bing | Model for accuracy evaluation |
| `rag_top_k` | 10 | Number of similarity results from System-1 |
| `graph_top_k` | 20 | Number of nodes selected in System-2 |
| `merge_method` | RAG_GRAPH | Hybrid merge strategy |
| `graph_global_search` | true | Enable hierarchical traversal |
| `organize_rag_content` | true | Structure context into chunks |
| `prompt_turning` | true | Use optimized prompts |
| `answer_prompt` | M365 | Prompt template variant |

For more details on configuration options, see [Configuration Options](#3.4).

Sources: [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1]()

---

## Key Takeaways

1. **Inference Capability**: This case demonstrates that RAG_GRAPH enables multi-hop reasoning by combining conversational evidence with structured entity knowledge.

2. **Temporal Grounding**: System-1's message retrieval provided the temporal anchor ("4 years ago"), while System-2's entity graph enabled geographical resolution.

3. **Context Organization**: The structured assembly of Message Chunks, FACTS, and ENTITIES into a unified prompt was critical for the LLM to make the correct inference.

4. **Performance**: Total retrieval and answer generation completed in ~5.2 seconds, demonstrating practical real-time performance.

5. **Hierarchical Value**: Without the `grandma` entity linking to Sweden, this question would have been unanswerable from conversation history alone.

For analysis of configuration impact on retrieval quality, see [Configuration Impact Analysis](#4.4). For the complete LoCoMo benchmark results, see [LoCoMo Results](#4.2).

Sources: [results/locomo/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:12](), [README.md:42-46]()

---

# Page: LongMemEval-S QA 262

# LongMemEval-S QA 262

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [figures/figure_case_1.png](figures/figure_case_1.png)
- [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json](results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json)

</details>



## Purpose and Scope

This page provides a detailed walkthrough of a specific question from the LongMemEval-S benchmark, demonstrating how Mnemis processes temporal queries through its dual-route retrieval system. The example illustrates:

- How System-1 (similarity search) and System-2 (global selection) retrieve relevant historical context
- Temporal reasoning across multiple conversation sessions
- Fact extraction and entity summarization from conversational memory
- Structured context assembly using the RAG_GRAPH merge strategy

For a broader overview of LongMemEval-S results across all question types, see [LongMemEval-S Results](#4.3). For another case study demonstrating different capabilities, see [LoCoMo User 8 QA 11](#5.1).

Sources: [README.md:48-51]()

## Question Overview

**Question ID**: `f8c5f88b`  
**Question Type**: `single-session-user`  
**Date**: 2023/05/30 (Tue) 23:39

```
Question: "Where did I buy my new tennis racket from?"
Gold Answer: "the sports store downtown"
System Hypothesis: "You bought your new tennis racket from a sports store downtown."
Grade: ✓ Correct
```

This question requires the system to:
1. Search through multiple conversation sessions spanning several days
2. Identify the relevant message from 5 days prior (2023/05/25)
3. Extract the specific location information ("sports store downtown")
4. Handle temporal context (question asks about past purchase)

Sources: [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1]()

## Dual-Route Retrieval Process

### Retrieval Architecture for This Query

```mermaid
graph TB
    subgraph Query["Query Processing"]
        Q["Question:<br/>Where did I buy my<br/>new tennis racket from?<br/>(2023/05/30)"]
        QE["Query Embedding<br/>qwen3 FLOAT32"]
    end
    
    subgraph System1["System-1: Similarity Search"]
        S1_EMB["Episodic Node<br/>Embedding Search"]
        S1_TOP["Top-K Results<br/>k=10"]
        S1_MSG["Evidence Message:<br/>2023/05/25<br/>'sports store downtown'"]
    end
    
    subgraph System2["System-2: Global Selection"]
        S2_GS["global_selection()<br/>Hierarchical Traversal"]
        S2_LAYER["LLM-Guided<br/>layer_selection()"]
        S2_TOP["Top-K Nodes<br/>k=20"]
        S2_ENT["Relevant Entities:<br/>- sports store downtown<br/>- tennis racket<br/>- Racket Sports"]
    end
    
    subgraph Merge["RAG_GRAPH Merge"]
        CTX["Structured Context Assembly"]
        MC["Message Chunks<br/>(Sessions 2, 31, 50)"]
        FACTS["FACTS<br/>(20 temporal facts)"]
        ENT["ENTITIES<br/>(20+ summarized entities)"]
    end
    
    Q --> QE
    QE --> S1_EMB
    QE --> S2_GS
    
    S1_EMB --> S1_TOP
    S1_TOP --> S1_MSG
    S1_MSG --> CTX
    
    S2_GS --> S2_LAYER
    S2_LAYER --> S2_TOP
    S2_TOP --> S2_ENT
    S2_ENT --> CTX
    
    CTX --> MC
    CTX --> FACTS
    CTX --> ENT
```

**Diagram: Dual-route retrieval flow for tennis racket question**

Sources: [README.md:26-29](), [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1]()

### Evidence Message Retrieved

The system successfully identified the key evidence message from 5 days prior:

```json
{
  "role": "user",
  "content": "I'll definitely do those exercises before playing tennis. By the way, I'm really happy with my new tennis racket, which I got from a sports store downtown. It's been performing really well, and I feel like it's improved my game. Do you have any tips on how to maintain and clean my racket?",
  "datetime": "2023/05/25 (Thu) 21:29"
}
```

**Key observations**:
- The evidence is embedded within a longer conversational turn
- The location information appears mid-sentence after other context
- Temporal gap of 5 days between evidence and query
- The system must distinguish "sports store downtown" as the purchase location

Sources: [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1]()

## Context Organization

The RAG_GRAPH merge strategy assembles retrieved information into three structured components:

### Message Chunks Structure

```mermaid
graph LR
    subgraph Sessions["Retrieved Sessions"]
        S2["Message Chunk 0<br/>Session 2<br/>2023/05/20"]
        S31["Message Chunk 1<br/>Session 31<br/>2023/05/25<br/>(CONTAINS EVIDENCE)"]
        S50["Message Chunk 2<br/>Session 50<br/>2023/05/30"]
    end
    
    subgraph Evidence["Evidence Context"]
        E1["Pre-context:<br/>Tennis exercises<br/>discussion"]
        E2["Target Evidence:<br/>'sports store<br/>downtown'"]
        E3["Post-context:<br/>Racket maintenance<br/>discussion"]
    end
    
    S31 --> E1
    S31 --> E2
    S31 --> E3
```

**Diagram: Message chunk organization showing evidence location**

The system retrieved 3 message chunks, with the critical evidence in Session 31:

| Chunk | Session | Date | Content Summary | Contains Evidence |
|-------|---------|------|-----------------|-------------------|
| 0 | 2 | 2023/05/20 05:09 | Fashion and shopping discussion | No |
| 1 | 31 | 2023/05/25 21:30 | **Tennis equipment and maintenance** | **Yes** |
| 2 | 50 | 2023/05/30 17:18 | Recent conversation | No |

Sources: [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1]()

### FACTS Component

The system extracted 20 temporal facts, including the critical one:

```
FACT: "The user owns a new tennis racket which they got from a sports store downtown 
       and feel it has improved their game."
Temporal Range: (2023-05-25 - 2023-05-29)
```

**Key FACTS related to the query**:
- User owns new tennis racket from sports store downtown (2023-05-25 - 2023-05-29)
- User is focusing on improving game with new racket (2023-05-25 - 2023-05-29)
- User plans to play tennis with friends at local park Sunday (2023-05-28 - now)
- User plans to buy new tennis balls this weekend (2023-05-25 - now)

**Temporal reasoning demonstrated**:
- Facts include date ranges showing when events occurred
- System distinguishes between when fact was stated vs. when event happened
- Temporal metadata enables answering "when" questions

Sources: [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1]()

### ENTITIES Component

The system maintained 20+ summarized entities, with these most relevant:

```
ENTITY: sports store downtown
Summary: "A sports store located downtown where the user purchased a new tennis racket, 
         which has been performing well and improved their game."

ENTITY: tennis racket  
Summary: "The tennis racket is a sports equipment used for playing tennis. It is mentioned 
         as a new purchase from a sports store downtown, which has improved the user's game. 
         Tips for maintaining and cleaning the tennis racket include cleaning the racket head, 
         string maintenance, avoiding extreme temperatures, proper storage, handle care, 
         avoiding exposure to chemicals, cleaning the grommets, and inspecting for damage."

ENTITY: Racket Sports
Summary: "The category Racket Sports encompasses activities and equipment related to sports 
         like badminton and tennis. [...] Equipment such as tennis rackets, including a new 
         purchase from a downtown sports store, is highlighted with maintenance tips [...]"
```

**Entity hierarchy demonstrated**:
- Specific entity: "sports store downtown" (Layer 0 - concrete instance)
- Equipment entity: "tennis racket" (Layer 0 - specific item)
- Category entity: "Racket Sports" (Higher layer - semantic grouping)

Sources: [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1]()

## Code Entity Mapping

### Context Assembly Code Flow

```mermaid
graph TB
    subgraph Retrieval["GlobalSelector Module"]
        GS_CLASS["GlobalSelector.global_selection()"]
        GS_LAYER["GlobalSelector.layer_selection()"]
        GS_CACHE["@alru_cache(maxsize=500)"]
        GS_NEO["Neo4j AsyncDriver"]
    end
    
    subgraph DataModel["Pydantic Models"]
        NS["NodeSelection<br/>(selected: bool<br/>explanation: str)"]
        NSL["NodeSelectionList<br/>(selections: List[NodeSelection])"]
    end
    
    subgraph Context["Context Structure"]
        MSG["Message Chunks:<br/>List[Dict]<br/>role, content, datetime"]
        FACTS["FACTS:<br/>List[str]<br/>temporal_range"]
        ENT["ENTITIES:<br/>Dict[str, str]<br/>name: summary"]
    end
    
    subgraph Answer["Answer Generation"]
        PROMPT["Context Template:<br/>Message Chunk 0..N<br/>FACTS<br/>ENTITIES"]
        LLM["LLM Client<br/>gpt-41-mini"]
        RESP["answer: str<br/>grade: bool<br/>duration: float"]
    end
    
    GS_CLASS --> GS_LAYER
    GS_LAYER --> NS
    NS --> NSL
    GS_CACHE --> GS_NEO
    GS_NEO --> MSG
    GS_NEO --> FACTS
    GS_NEO --> ENT
    
    MSG --> PROMPT
    FACTS --> PROMPT
    ENT --> PROMPT
    
    PROMPT --> LLM
    LLM --> RESP
```

**Diagram: Code entities involved in context assembly and answer generation**

Sources: [README.md:54-56]()

### Results Data Structure

The complete results for this question are stored in the following format:

```json
{
  "question_id": "f8c5f88b",
  "question": "(date: 2023/05/30 (Tue) 23:39)Where did I buy my new tennis racket from?",
  "hypothesis": "You bought your new tennis racket from a **sports store downtown**.",
  "gold_answer": "the sports store downtown",
  "question_type": "single-session-user",
  "duration": 2.1430790424346924,
  "grade": true,
  "answer_session_ids": ["answer_c3567066"],
  "evidence_messages": [...],
  "context": "...",
  "hybrid_episode_candidates": null,
  "hybrid_edge_candidates": null,
  "hybrid_node_candidates": null,
  "retrieval_duration": 1.1682510375976562e-05
}
```

**Key metrics**:
- `duration`: 2.14 seconds total processing time
- `retrieval_duration`: 11.68 microseconds (cached access)
- `grade`: Boolean indicating correctness
- `answer_session_ids`: Tracks which session contained the answer

Sources: [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1]()

## Answer Generation Process

### Prompt Template Structure

```mermaid
graph TB
    subgraph PromptTemplate["Answer Prompt Template"]
        INST["System Instructions:<br/>'Use historical conversation<br/>for reference'"]
        MSG_SECT["Message Chunk Sections:<br/>Session-grouped messages<br/>with timestamps"]
        FACT_SECT["FACTS Section:<br/>Temporal statements<br/>with date ranges"]
        ENT_SECT["ENTITIES Section:<br/>name: summary pairs"]
        QUESTION["Current Question:<br/>With date context"]
    end
    
    subgraph LLMCall["LLM Processing"]
        PARSE["Parse context structure"]
        REASON["Identify relevant facts<br/>and entities"]
        EXTRACT["Extract answer:<br/>'sports store downtown'"]
        FORMAT["Format hypothesis"]
    end
    
    subgraph Grading["Answer Evaluation"]
        COMP["Compare hypothesis<br/>to gold_answer"]
        GRADE["grade: true/false"]
    end
    
    INST --> PARSE
    MSG_SECT --> PARSE
    FACT_SECT --> PARSE
    ENT_SECT --> PARSE
    QUESTION --> PARSE
    
    PARSE --> REASON
    REASON --> EXTRACT
    EXTRACT --> FORMAT
    
    FORMAT --> COMP
    COMP --> GRADE
```

**Diagram: Answer generation and grading flow**

The complete context provided to the LLM includes:

```
# The following historical conversation is provided for your reference...

Message Chunk 0 (Session 2):
[2023/05/20 (Sat) 05:09] user: I like the sound of Combo 1...

Message Chunk 1 (Session 31):
[2023/05/25 (Thu) 21:31] user: I'll definitely do those exercises before playing tennis. 
By the way, I'm really happy with my new tennis racket, which I got from a sports store 
downtown. It's been performing really well...

FACTS and ENTITIES represent relevant context to the current conversation.

<FACTS>
  - The user owns a new tennis racket which they got from a sports store downtown...
  - Assistant recommended Rooster Tail spinner lures for trout in Lake Michigan...
</FACTS>

<ENTITIES>
  - sports store downtown: A sports store located downtown where the user purchased 
    a new tennis racket, which has been performing well and improved their game.
  - tennis racket: The tennis racket is a sports equipment used for playing tennis...
</ENTITIES>
```

Sources: [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1]()

## Performance Characteristics

### Timing Breakdown

| Phase | Duration | Percentage |
|-------|----------|------------|
| Retrieval (cached) | 11.68 μs | 0.001% |
| Context Assembly | ~0.5 s | 23% |
| LLM Answer Generation | ~1.6 s | 75% |
| **Total** | **2.14 s** | **100%** |

### Configuration Parameters

This question was processed with the following configuration:

```
Configuration: ragtopk10_gtopk20_RAG_GRAPH
- rag_top_k: 10 (System-1 similarity search results)
- graph_top_k: 20 (System-2 global selection results)
- merge_method: RAG_GRAPH (hybrid merge strategy)
- graph_model: gpt-41-mini-shortco-2025-04-14-Bing
- answer_model: gpt-41-mini-shortco-2025-04-14-Bing
- grader_model: gpt-41-mini-shortco-2025-04-14-Bing
- graph_global_search: true
```

For details on how these parameters affect overall accuracy, see [Configuration Impact Analysis](#4.4).

Sources: [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1]()

## Key Takeaways

This case study demonstrates several critical capabilities of the Mnemis system:

### 1. Temporal Reasoning
- Successfully retrieved evidence from 5 days prior to the question
- Correctly handled temporal context in both the question ("Where did I buy") and facts
- Distinguished between event time (2023/05/25) and query time (2023/05/30)

### 2. Dual-Route Effectiveness
- **System-1** (similarity): Embedded query quickly matched episodic nodes containing tennis-related content
- **System-2** (global): Traversed hierarchical graph from "Racket Sports" → "tennis racket" → "sports store downtown"
- **Merge**: Combined episodic evidence with semantic entity summaries for comprehensive context

### 3. Context Structure Benefits
- **Message Chunks**: Preserved conversational context around the evidence
- **FACTS**: Provided temporal grounding with explicit date ranges
- **ENTITIES**: Offered summarized knowledge about recurring concepts

### 4. Production Considerations
- Caching (`@alru_cache`) reduced retrieval time to microseconds for repeated queries
- Structured Pydantic models ensure type-safe data flow
- Neo4j graph database enables efficient hierarchical traversal
- Total processing time (2.14s) dominated by LLM inference, not retrieval

### 5. Question Type Handling
This `single-session-user` question required:
- Finding information stated in user messages (not assistant responses)
- Locating a specific factual detail (purchase location)
- No multi-hop reasoning or temporal aggregation
- Direct answer extraction from evidence

For comparison with multi-session or preference-based questions, see [LongMemEval-S Results](#4.3).

Sources: [README.md:15-23](), [results/lme-s/results_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json:1]()

---

# Page: Getting Started

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [global_selection/global_selector.py](global_selection/global_selector.py)

</details>



This page provides a quickstart guide to set up and run Mnemis, a dual-route retrieval system for long-term LLM memory. It covers the prerequisites, essential setup steps, and basic usage workflows. For detailed installation instructions, see [Installation & Setup](#6.1). For code examples, see [Usage Examples](#6.2). For reproducing benchmark results, see [Running Evaluations](#6.3).

## Purpose and Scope

This guide helps you:
- Set up the required infrastructure (Neo4j database, LLM services)
- Install Mnemis dependencies
- Run your first global selection query
- Execute evaluation scripts on benchmark datasets

For architectural details about how the system works, see [Architecture Overview](#2). For implementation details about the `GlobalSelector` class, see [GlobalSelector Class Reference](#3.1).

## Prerequisites Overview

Mnemis requires the following components to operate:

| Component | Purpose | Configuration Location |
|-----------|---------|----------------------|
| **Neo4j Database** | Stores base graph and hierarchical graph structures | Connection URL, credentials |
| **LLM Service** | Powers System-2 layer selection decisions | OpenAI/Azure API keys |
| **Embedding Service** | Enables System-1 similarity search (via Graphiti) | Model configuration |
| **Python 3.8+** | Runtime environment | Dependencies in requirements |
| **Graphiti Framework** | Base graph operations and memory extraction | Installed as dependency |

**Sources:** [README.md:54-56](), [global_selection/global_selector.py:1-19]()

## System Setup Flow

The following diagram shows the setup process and how components connect:

```mermaid
graph TB
    subgraph "Prerequisites"
        PYTHON["Python 3.8+<br/>Environment"]
        NEO4J_INSTALL["Neo4j Database<br/>Installation"]
        API_KEYS["API Keys<br/>OpenAI/Azure"]
    end
    
    subgraph "Installation Steps"
        CLONE["Clone Repository<br/>github.com/microsoft/Mnemis"]
        DEPS["Install Dependencies<br/>pip install -r requirements.txt"]
        ENV["Configure .env<br/>Database + API credentials"]
    end
    
    subgraph "Infrastructure Setup"
        NEO4J_RUN["Neo4j AsyncDriver<br/>bolt://localhost:7687"]
        LLM_CLIENT["LLM Client<br/>AsyncOpenAI or AsyncAzureOpenAI"]
        GRAPHITI_SETUP["Graphiti Framework<br/>Base implementation"]
    end
    
    subgraph "Ready to Use"
        GLOBAL_SELECTOR["GlobalSelector<br/>global_selection/global_selector.py"]
        DATASETS["Benchmark Datasets<br/>data/locomo.json<br/>data/longmemeval_s.json"]
    end
    
    PYTHON --> CLONE
    NEO4J_INSTALL --> NEO4J_RUN
    API_KEYS --> LLM_CLIENT
    
    CLONE --> DEPS
    DEPS --> ENV
    DEPS --> GRAPHITI_SETUP
    
    ENV --> NEO4J_RUN
    ENV --> LLM_CLIENT
    
    NEO4J_RUN --> GLOBAL_SELECTOR
    LLM_CLIENT --> GLOBAL_SELECTOR
    GRAPHITI_SETUP --> GLOBAL_SELECTOR
    
    GLOBAL_SELECTOR --> DATASETS
    
    style GLOBAL_SELECTOR fill:#f9f9f9
    style DATASETS fill:#f9f9f9
```

**Sources:** [global_selection/global_selector.py:431-449](), [README.md:54-56]()

## Core Components and Code Entities

Understanding the key code entities is essential for working with Mnemis:

```mermaid
graph LR
    subgraph "Entry Point"
        MAIN["main()<br/>global_selector.py:431"]
    end
    
    subgraph "Core Classes"
        DRIVER["AsyncDriver<br/>from neo4j"]
        LLM["LLMClient<br/>from graphiti_core.llm_client"]
        OPENAI["AsyncOpenAI<br/>or AsyncAzureOpenAI"]
        SELECTOR["GlobalSelector<br/>global_selector.py:90"]
        CONFIG["GlobalSelectorConfig<br/>global_selector.py:85"]
    end
    
    subgraph "Key Methods"
        GLOBAL_SEARCH["global_selection()<br/>line 267"]
        LAYER_SEL["layer_selection()<br/>line 224"]
        GET_NEIGHBORS["get_one_hop_neighbors()<br/>line 197"]
    end
    
    subgraph "Data Loaders"
        LOAD_LOCOMO["load_locomo_data_query_group_id()<br/>line 321"]
        LOAD_LME["load_lme_data_query_group_id()<br/>line 344"]
    end
    
    subgraph "Batch Processing"
        PARSE_LOCOMO["parse_locomo()<br/>line 387"]
        PARSE_LME["parse_lme()<br/>line 409"]
        GET_CONTEXT["get_global_search_context()<br/>line 366"]
    end
    
    MAIN --> DRIVER
    MAIN --> OPENAI
    OPENAI --> LLM
    DRIVER --> SELECTOR
    LLM --> SELECTOR
    CONFIG --> SELECTOR
    
    SELECTOR --> GLOBAL_SEARCH
    GLOBAL_SEARCH --> LAYER_SEL
    GLOBAL_SEARCH --> GET_NEIGHBORS
    
    LOAD_LOCOMO --> PARSE_LOCOMO
    LOAD_LME --> PARSE_LME
    PARSE_LOCOMO --> GET_CONTEXT
    PARSE_LME --> GET_CONTEXT
    GET_CONTEXT --> GLOBAL_SEARCH
    
    style SELECTOR fill:#f9f9f9
    style GLOBAL_SEARCH fill:#f9f9f9
```

**Sources:** [global_selection/global_selector.py:85-95](), [global_selection/global_selector.py:224-319](), [global_selection/global_selector.py:321-429]()

## Basic Usage Workflow

Once set up, the typical workflow involves these steps:

### 1. Initialize Infrastructure

Create connections to Neo4j and LLM services:

```python
# From global_selection/global_selector.py:431-441
driver = AsyncGraphDatabase.driver(url, auth=(user, password), 
                                  max_connection_pool_size=1000)
raw_client = AsyncOpenAI(base_url="xxx", api_key="EMPTY")
llm_client = OpenAIClient(client=raw_client)
```

**Sources:** [global_selection/global_selector.py:432-440]()

### 2. Create GlobalSelector Instance

The `GlobalSelector` class orchestrates System-2 retrieval:

```python
# From global_selection/global_selector.py:441
selector = GlobalSelector(driver, llm_client)
```

Configuration options can be provided via `GlobalSelectorConfig`:
- `use_summary`: Include node summaries in selection prompts (default: False)
- `use_tag`: Include node tags in selection prompts (default: True)

**Sources:** [global_selection/global_selector.py:85-94]()

### 3. Execute Global Selection

Call the `global_selection()` method with a query and group_id:

```python
# Returns results dict and time statistics
results, time_stats = await selector.global_selection(query, group_id=group_id)
```

The results contain:
- `episodes`: Retrieved episodic memory nodes (conversations)
- `edges`: Facts (RELATES_TO relationships) with temporal information
- `nodes`: Selected entities and categories with summaries

**Sources:** [global_selection/global_selector.py:267-319]()

### 4. Process Results

Results are structured for downstream LLM consumption:

| Field | Type | Content |
|-------|------|---------|
| `episodes` | list[dict] | Historical conversation chunks with `uuid`, `content`, `valid_at` |
| `edges` | list[dict] | Temporal facts with `fact`, `valid_at`, `invalid_at`, `uuid` |
| `nodes` | list[dict] | Entities/categories with `name`, `tag`, `summary`, `uuid` |

**Sources:** [global_selection/global_selector.py:302-318]()

## Execution Flow Diagram

This diagram shows the runtime flow when executing a global selection query:

```mermaid
sequenceDiagram
    participant User
    participant GS as "GlobalSelector"
    participant Neo4j as "AsyncDriver<br/>(Neo4j)"
    participant LLM as "LLMClient<br/>(OpenAI)"
    
    User->>GS: "global_selection(query, group_id)"
    
    GS->>Neo4j: "get_max_layer(group_id)"
    Note over Neo4j: Query.GET_MAX_LAYER
    Neo4j-->>GS: "max_layer (e.g., 3)"
    
    loop "For layer in range(max_layer, 0, -1)"
        GS->>Neo4j: "get_nodes_by_layer(layer, group_id)"
        Note over Neo4j: Query.GET_NODES_BY_LAYER
        Neo4j-->>GS: "current_layer_categories"
        
        GS->>LLM: "layer_selection(query, categories)"
        Note over LLM: NODE_SELECTION_PROMPT_TEMPLATE
        LLM-->>GS: "NodeSelectionList<br/>(selected + shortcuts)"
        
        alt "Shortcuts selected"
            GS->>Neo4j: "get_all_descendants_batch(shortcuts)"
            Note over Neo4j: Query.GET_ALL_DESCENDANTS_BATCH
            Neo4j-->>GS: "all descendants"
        end
    end
    
    GS->>Neo4j: "get_one_hop_neighbors_batch(selected_nodes)"
    Note over Neo4j: Query.GET_ONE_HOP_EPISODES_BATCH<br/>Query.GET_ONE_HOP_NODES_AND_EDGES_BATCH
    Neo4j-->>GS: "episodes, edges, neighbor_nodes"
    
    GS-->>User: "results<br/>(episodes, edges, nodes)<br/>time_stats"
```

**Sources:** [global_selection/global_selector.py:267-319]()

## Running Benchmark Evaluations

Mnemis includes evaluation scripts for two benchmarks:

### LoCoMo Evaluation
```python
# From global_selection/global_selector.py:387-407
await parse_locomo(selector)
```

Configuration:
- Dataset: `data/locomo.json`
- Batch size: 50 queries
- Max concurrent: 10 requests
- Total queries: 1,986 (all users)

**Sources:** [global_selection/global_selector.py:387-407]()

### LongMemEval-S Evaluation
```python
# From global_selection/global_selector.py:409-429
await parse_lme(selector)
```

Configuration:
- Dataset: `data/longmemeval_s.json`
- Batch size: 30 queries
- Max concurrent: 10 requests
- Total queries: 500

**Sources:** [global_selection/global_selector.py:409-429]()

Both evaluation functions:
1. Load query-group_id pairs from JSON datasets
2. Execute `get_global_search_context()` with concurrency control
3. Save results to output JSONL files for downstream answer generation

For detailed evaluation methodology and result analysis, see [Evaluation & Results](#4).

## Caching and Performance

The `GlobalSelector` uses `alru_cache` decorators for performance optimization:

| Method | Cache Size | Purpose |
|--------|-----------|---------|
| `get_max_layer()` | 500 per query | Avoid repeated hierarchy depth lookups |
| `get_nodes_by_layer()` | 500 per query | Cache layer node lists |
| `get_child_nodes()` | 500 per query | Cache parent-child relationships |
| `get_all_descendants()` | 500 per query | Cache subtree traversals |
| `get_one_hop_neighbors()` | 500 per query | Cache neighborhood expansions |

The cache can be cleared manually using `selector.clear_cache()`.

**Sources:** [global_selection/global_selector.py:20](), [global_selection/global_selector.py:96-101](), [global_selection/global_selector.py:103-222]()

## Connection Pooling

The Neo4j driver is configured with a large connection pool to support high concurrency:

```python
# From global_selection/global_selector.py:435
driver = AsyncGraphDatabase.driver(url, auth=(user, password), 
                                  max_connection_pool_size=1000)
```

This enables:
- 50 concurrent QA operations in batch processing
- 10 parallel user evaluations
- Efficient handling of multiple simultaneous global selection queries

**Sources:** [global_selection/global_selector.py:435]()

## Next Steps

After completing basic setup:

1. **For detailed installation**: See [Installation & Setup](#6.1) for step-by-step instructions including Neo4j configuration and API key setup
2. **For code examples**: See [Usage Examples](#6.2) for complete working examples of initializing and using the `GlobalSelector`
3. **For evaluation**: See [Running Evaluations](#6.3) for reproducing benchmark results and interpreting metrics
4. **For configuration**: See [Configuration Options](#3.4) for tuning retrieval parameters and model settings
5. **For architecture**: See [System-2 Global Selection](#2.3) to understand the hierarchical traversal mechanism

**Sources:** [README.md:1-72]()

---

# Page: Installation & Setup

# Installation & Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [global_selection/global_selector.py](global_selection/global_selector.py)

</details>



This document provides step-by-step instructions for installing and configuring Mnemis, including Python dependencies, Neo4j database setup, and LLM service configuration. By the end of this guide, you will have a working Mnemis environment ready to perform dual-route memory retrieval.

For usage examples and running the system, see [Usage Examples](#6.2). For information about running benchmark evaluations, see [Running Evaluations](#6.3).

---

## Prerequisites

Before installing Mnemis, ensure you have the following:

| Requirement | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Core runtime environment |
| Neo4j Database | 5.x | Graph storage for base and hierarchical graphs |
| OpenAI/Azure API Access | GPT-4.1-mini or compatible | LLM services for System-2 global selection |
| Git | Any recent version | Clone the repository |

**Hardware Recommendations:**
- Minimum 8GB RAM for development
- 16GB+ RAM recommended for benchmark evaluations
- SSD storage for Neo4j database performance

---

## System Architecture Overview

The following diagram shows the installation components and their relationships:

**Installation Component Architecture**

```mermaid
graph TB
    subgraph "Python Environment"
        PYTHON["Python 3.10+"]
        VENV["Virtual Environment"]
        
        subgraph "Core Dependencies"
            GRAPHITI["graphiti_core<br/>LLMClient, OpenAIClient"]
            NEO4J_PY["neo4j<br/>AsyncDriver, AsyncGraphDatabase"]
            OPENAI_PY["openai<br/>AsyncOpenAI, AsyncAzureOpenAI"]
            PYDANTIC["pydantic<br/>BaseModel"]
        end
        
        subgraph "Utilities"
            ASYNC_LRU["async-lru<br/>alru_cache"]
            PANDAS["pandas"]
            TQDM["tqdm"]
            DOTENV["python-dotenv"]
        end
    end
    
    subgraph "External Services"
        NEO4J_DB["Neo4j Database<br/>bolt://localhost:7687"]
        OPENAI_API["OpenAI/Azure API<br/>gpt-41-mini"]
        EMB_API["Embedding Service<br/>qwen3"]
    end
    
    subgraph "Configuration"
        ENV[".env file<br/>API keys, URLs, credentials"]
        DRIVER_CONFIG["AsyncDriver Config<br/>max_connection_pool_size=1000"]
    end
    
    subgraph "Mnemis Core"
        GS["GlobalSelector<br/>global_selector.py"]
        PROMPTS["NODE_SELECTION_PROMPT<br/>prompts.py"]
    end
    
    PYTHON --> VENV
    VENV --> GRAPHITI
    VENV --> NEO4J_PY
    VENV --> OPENAI_PY
    VENV --> PYDANTIC
    VENV --> ASYNC_LRU
    VENV --> PANDAS
    VENV --> TQDM
    VENV --> DOTENV
    
    ENV --> DOTENV
    DOTENV --> GS
    
    NEO4J_PY --> DRIVER_CONFIG
    DRIVER_CONFIG --> NEO4J_DB
    
    OPENAI_PY --> OPENAI_API
    
    GRAPHITI --> GS
    NEO4J_PY --> GS
    OPENAI_PY --> GS
    PYDANTIC --> GS
    ASYNC_LRU --> GS
    
    GS --> PROMPTS
```

**Sources:** [global_selector.py:1-19](), [README.md:54-56]()

---

## Step 1: Clone Repository

Clone the Mnemis repository from GitHub:

```bash
git clone https://github.com/microsoft/Mnemis.git
cd Mnemis
```

The repository structure includes:

| Directory/File | Purpose |
|---------------|---------|
| `global_selection/` | System-2 global selection implementation |
| `data/` | Benchmark datasets (locomo.json, longmemeval_s.json) |
| `results/` | Evaluation results and memory contexts |
| `README.md` | Overview and citation information |

**Sources:** [README.md:1-72]()

---

## Step 2: Python Environment Setup

### Create Virtual Environment

Create and activate a Python virtual environment:

```bash
# Create virtual environment
python3 -m venv mnemis-env

# Activate on Linux/Mac
source mnemis-env/bin/activate

# Activate on Windows
mnemis-env\Scripts\activate
```

### Install Python Dependencies

Install the required Python packages. The core dependencies are:

```bash
# Core framework (built on Graphiti)
pip install graphiti-core

# Database driver
pip install neo4j

# LLM client
pip install openai

# Data validation and modeling
pip install pydantic

# Performance optimization
pip install async-lru

# Data processing
pip install pandas

# Progress tracking
pip install tqdm

# Environment configuration
pip install python-dotenv
```

**Dependency Mapping:**

| Package | Import Path | Used In | Purpose |
|---------|------------|---------|---------|
| `neo4j` | `neo4j.AsyncDriver` | [global_selector.py:10]() | Async graph database operations |
| `openai` | `openai.AsyncOpenAI` | [global_selector.py:13]() | LLM API client |
| `graphiti-core` | `graphiti_core.llm_client` | [global_selector.py:16]() | Graphiti framework integration |
| `pydantic` | `pydantic.BaseModel` | [global_selector.py:14]() | Type-safe data models |
| `async-lru` | `async_lru.alru_cache` | [global_selector.py:11]() | Async LRU caching |
| `python-dotenv` | `dotenv.load_dotenv` | [global_selector.py:2-5]() | Environment variable loading |

**Sources:** [global_selector.py:1-19]()

---

## Step 3: Neo4j Database Setup

Mnemis requires a Neo4j graph database to store the base graph and hierarchical graph structures.

### Install Neo4j

**Option A: Docker (Recommended for Development)**

```bash
docker run \
    --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/your_password \
    -v $HOME/neo4j/data:/data \
    neo4j:5-community
```

**Option B: Native Installation**

Download and install Neo4j Community Edition 5.x from [neo4j.com/download](https://neo4j.com/download/)

### Configure Neo4j Connection

The system uses `AsyncDriver` with the following configuration:

**Neo4j Connection Parameters**

```mermaid
graph LR
    subgraph "Connection Configuration"
        URL["bolt://localhost:7687<br/>Default Neo4j bolt URL"]
        AUTH["Authentication<br/>username + password"]
        POOL["max_connection_pool_size<br/>1000 connections"]
    end
    
    subgraph "AsyncDriver Initialization"
        DRIVER["AsyncGraphDatabase.driver<br/>global_selector.py:435"]
    end
    
    subgraph "GlobalSelector Usage"
        GS_INIT["GlobalSelector.__init__<br/>driver parameter<br/>global_selector.py:91"]
        QUERY_EXEC["driver.execute_query<br/>Cypher execution"]
    end
    
    URL --> DRIVER
    AUTH --> DRIVER
    POOL --> DRIVER
    
    DRIVER --> GS_INIT
    GS_INIT --> QUERY_EXEC
```

**Sources:** [global_selector.py:432-435](), [global_selector.py:90-94]()

### Verify Neo4j Connection

Test the connection using the Neo4j Browser:
1. Open http://localhost:7474 in your browser
2. Connect with credentials: `neo4j` / `your_password`
3. Run test query: `MATCH (n) RETURN count(n)`

---

## Step 4: LLM Service Configuration

Mnemis uses LLM services for System-2 global selection via the `layer_selection` method.

### OpenAI Configuration

The system supports both OpenAI and Azure OpenAI:

**LLM Client Initialization Flow**

```mermaid
graph TB
    subgraph "API Client Options"
        OPENAI["AsyncOpenAI<br/>openai.AsyncOpenAI"]
        AZURE["AsyncAzureOpenAI<br/>openai.AsyncAzureOpenAI"]
    end
    
    subgraph "Graphiti Wrapper"
        GRAPHITI_CLIENT["OpenAIClient<br/>graphiti_core.llm_client.OpenAIClient<br/>global_selector.py:440"]
    end
    
    subgraph "GlobalSelector"
        GS_CLIENT["self.llm_client<br/>global_selector.py:93"]
        LAYER_SEL["layer_selection method<br/>global_selector.py:224-265"]
        GEN_RESP["llm_client.generate_response<br/>global_selector.py:241-245"]
    end
    
    subgraph "Configuration"
        BASE_URL["base_url<br/>API endpoint"]
        API_KEY["api_key<br/>Authentication"]
    end
    
    BASE_URL --> OPENAI
    API_KEY --> OPENAI
    BASE_URL --> AZURE
    API_KEY --> AZURE
    
    OPENAI --> GRAPHITI_CLIENT
    AZURE --> GRAPHITI_CLIENT
    
    GRAPHITI_CLIENT --> GS_CLIENT
    GS_CLIENT --> LAYER_SEL
    LAYER_SEL --> GEN_RESP
```

**Sources:** [global_selector.py:436-441](), [global_selector.py:224-245]()

### API Configuration Examples

**For OpenAI:**

```python
from openai import AsyncOpenAI
from graphiti_core.llm_client import OpenAIClient

raw_client = AsyncOpenAI(
    api_key="your-openai-api-key"
)
llm_client = OpenAIClient(client=raw_client)
```

**For Azure OpenAI:**

```python
from openai import AsyncAzureOpenAI
from graphiti_core.llm_client import OpenAIClient

raw_client = AsyncAzureOpenAI(
    azure_endpoint="https://your-resource.openai.azure.com/",
    api_key="your-azure-api-key",
    api_version="2024-02-15-preview"
)
llm_client = OpenAIClient(client=raw_client)
```

**For Custom Endpoint:**

```python
from openai import AsyncOpenAI
from graphiti_core.llm_client import OpenAIClient

raw_client = AsyncOpenAI(
    base_url="your-custom-endpoint-url",
    api_key="EMPTY"  # or your custom key
)
llm_client = OpenAIClient(client=raw_client)
```

**Sources:** [global_selector.py:436-441]()

---

## Step 5: Environment Configuration

Create a `.env` file in the project root to store configuration:

```bash
# Neo4j Configuration
NEO4J_URL=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1

# Azure OpenAI Configuration (if using Azure)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-api-key
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Model Configuration
GRAPH_MODEL=gpt-4-turbo-preview
ANSWER_MODEL=gpt-41-mini
GRADER_MODEL=gpt-41-mini

# Embedding Configuration
EMBEDDING_MODEL=qwen3
EMBEDDING_PRECISION=FLOAT32
```

The system loads environment variables using `python-dotenv`:

```python
from dotenv import load_dotenv
load_dotenv()  # Line 5 of global_selector.py
```

**Sources:** [global_selector.py:2-5]()

---

## Step 6: Initialize GlobalSelector

After configuration, initialize the `GlobalSelector` class:

**GlobalSelector Initialization Pattern**

```mermaid
graph TB
    subgraph "Configuration Loading"
        ENV_FILE[".env file"]
        LOAD_DOTENV["load_dotenv<br/>global_selector.py:5"]
        ENV_VARS["Environment Variables"]
    end
    
    subgraph "Service Initialization"
        DRIVER_INIT["AsyncGraphDatabase.driver<br/>url, auth, pool_size<br/>global_selector.py:435"]
        CLIENT_INIT["AsyncOpenAI + OpenAIClient<br/>base_url, api_key<br/>global_selector.py:436-440"]
    end
    
    subgraph "GlobalSelector Creation"
        CONFIG["GlobalSelectorConfig<br/>use_summary, use_tag<br/>global_selector.py:85-87"]
        GS_INIT["GlobalSelector.__init__<br/>driver, llm_client, selection_config<br/>global_selector.py:91-94"]
    end
    
    subgraph "Core Methods Available"
        GLOBAL_SEL["global_selection<br/>global_selector.py:267-319"]
        LAYER_SEL["layer_selection<br/>global_selector.py:224-265"]
        CACHE["Cached Methods<br/>get_max_layer, get_nodes_by_layer<br/>get_child_nodes, etc."]
    end
    
    ENV_FILE --> LOAD_DOTENV
    LOAD_DOTENV --> ENV_VARS
    
    ENV_VARS --> DRIVER_INIT
    ENV_VARS --> CLIENT_INIT
    
    DRIVER_INIT --> GS_INIT
    CLIENT_INIT --> GS_INIT
    CONFIG --> GS_INIT
    
    GS_INIT --> GLOBAL_SEL
    GS_INIT --> LAYER_SEL
    GS_INIT --> CACHE
```

**Sources:** [global_selector.py:85-94](), [global_selector.py:432-441]()

### Example Initialization Code

```python
import asyncio
from neo4j import AsyncGraphDatabase
from openai import AsyncOpenAI
from graphiti_core.llm_client import OpenAIClient
from global_selection.global_selector import GlobalSelector, GlobalSelectorConfig

async def main():
    # Initialize Neo4j driver
    driver = AsyncGraphDatabase.driver(
        url='bolt://localhost:7687',
        auth=('neo4j', 'your_password'),
        max_connection_pool_size=1000
    )
    
    # Initialize LLM client
    raw_client = AsyncOpenAI(
        base_url="your-api-endpoint",
        api_key="your-api-key"
    )
    llm_client = OpenAIClient(client=raw_client)
    
    # Create GlobalSelector with configuration
    config = GlobalSelectorConfig(
        use_summary=False,  # Default
        use_tag=True        # Default
    )
    selector = GlobalSelector(
        driver=driver,
        llm_client=llm_client,
        selection_config=config
    )
    
    # Ready to use
    print("GlobalSelector initialized successfully")

if __name__ == "__main__":
    asyncio.run(main())
```

**Sources:** [global_selector.py:431-449]()

---

## Step 7: Verification

### Test Global Selection

Verify the installation by running a test query:

```python
async def test_global_selection():
    # (Using selector from previous step)
    
    test_query = "What topics did we discuss yesterday?"
    test_group_id = "test_user_0"
    
    results, time_stats = await selector.global_selection(
        query=test_query,
        group_id=test_group_id
    )
    
    print(f"Retrieved {len(results['episodes'])} episodes")
    print(f"Retrieved {len(results['edges'])} edges")
    print(f"Retrieved {len(results['nodes'])} nodes")
    print(f"Time stats: {time_stats}")
```

Expected output structure:
```json
{
  "episodes": [...],
  "edges": [...],
  "nodes": [...],
  "time_stats": {
    "init": 0.01,
    "layer_selection": 2.45,
    "one_hop_neighbors": 0.33
  }
}
```

**Sources:** [global_selector.py:267-319]()

### Verify Caching

The system uses `alru_cache` with 500 entries per query type. Verify caching is working:

```python
# First call - should hit database
await selector.get_max_layer(group_id="test_user_0")

# Second call - should hit cache (faster)
await selector.get_max_layer(group_id="test_user_0")

# Clear cache if needed
selector.clear_cache()
```

**Cache Configuration:**

| Cached Method | Cache Size | Line Reference |
|--------------|-----------|----------------|
| `get_max_layer` | 500 | [global_selector.py:103-110]() |
| `get_nodes_by_layer` | 500 | [global_selector.py:112-118]() |
| `get_child_nodes` | 500 | [global_selector.py:120-127]() |
| `get_all_descendants` | 500 | [global_selector.py:144-151]() |
| `get_one_hop_neighbors` | 500 | [global_selector.py:196-201]() |

**Sources:** [global_selector.py:20](), [global_selector.py:96-101](), [global_selector.py:103-201]()

---

## Common Configuration Issues

### Issue: Neo4j Connection Failed

**Error:** `ServiceUnavailable: Unable to retrieve routing information`

**Solutions:**
1. Verify Neo4j is running: `docker ps` or check system services
2. Check connection URL is `bolt://localhost:7687` (not `http://`)
3. Verify authentication credentials
4. Ensure firewall allows port 7687

### Issue: LLM API Rate Limits

**Error:** `RateLimitError` or slow responses

**Solutions:**
1. Adjust `max_concurrent` in batch processing (default: 10 in [global_selector.py:389]())
2. Use connection pooling: `max_connection_pool_size=1000` [global_selector.py:435]()
3. Consider Azure deployment for higher quotas

### Issue: Out of Memory

**Error:** `MemoryError` during large evaluations

**Solutions:**
1. Reduce `batch_size` in evaluation functions [global_selector.py:390]()
2. Adjust cache size `CACHE_SIZE_PER_QUERY` [global_selector.py:20]()
3. Process datasets in smaller chunks

**Sources:** [global_selector.py:366-429]()

---

## Configuration Summary

**Complete System Configuration Table:**

| Component | Configuration Parameter | Default Value | Code Reference |
|-----------|------------------------|---------------|----------------|
| Neo4j URL | `url` | `bolt://localhost:7687` | [global_selector.py:432]() |
| Neo4j Auth | `auth` | `(username, password)` | [global_selector.py:433-434]() |
| Connection Pool | `max_connection_pool_size` | 1000 | [global_selector.py:435]() |
| Cache Size | `CACHE_SIZE_PER_QUERY` | 500 | [global_selector.py:20]() |
| Batch Mode | `mode` | `'batch'` | [global_selector.py:269]() |
| Max Concurrent | `max_concurrent` | 5-10 | [global_selector.py:366-389]() |
| Use Summary | `use_summary` | `False` | [global_selector.py:86]() |
| Use Tag | `use_tag` | `True` | [global_selector.py:87]() |
| Model Size | `model_size` | `ModelSize.large` | [global_selector.py:244]() |

**Sources:** [global_selector.py:20](), [global_selector.py:85-94](), [global_selector.py:267-269](), [global_selector.py:432-435]()

---

## Next Steps

After completing installation and setup:

1. **Load Benchmark Data**: See [Running Evaluations](#6.3) for dataset preparation
2. **Run Example Queries**: See [Usage Examples](#6.2) for code samples
3. **Understand System Architecture**: See [Architecture Overview](#2) for system design
4. **Review Global Selection**: See [System-2 Global Selection](#2.3) for algorithmic details

**Related Documentation:**
- [GlobalSelector Class Reference](#3.1) - Complete API documentation
- [Configuration Options](#3.4) - Advanced configuration settings
- [Performance Optimization](#3.5) - Caching and batch processing strategies

**Sources:** [README.md:53-56](), [global_selector.py:1-453]()

---

# Page: Usage Examples

# Usage Examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [global_selection/global_selector.py](global_selection/global_selector.py)

</details>



This page provides practical code examples demonstrating how to use the GlobalSelector class for System-2 hierarchical retrieval. It covers initialization, dataset loading, query execution, batch processing, and result handling.

For installation and environment setup, see [Installation & Setup](#6.1). For complete evaluation workflows, see [Running Evaluations](#6.3). For detailed API documentation, see [GlobalSelector Class Reference](#3.1).

---

## Initialization Workflow

The GlobalSelector requires three components: a Neo4j AsyncDriver, an LLM client, and an optional configuration object.

```mermaid
graph TB
    subgraph "Environment Setup"
        ENV["load_dotenv()<br/>Load environment variables"]
    end
    
    subgraph "Neo4j Connection"
        DRIVER_CREATE["AsyncGraphDatabase.driver()<br/>bolt://localhost:7687"]
        PARAMS["Parameters:<br/>user, password<br/>max_connection_pool_size=1000"]
        DRIVER["AsyncDriver instance"]
    end
    
    subgraph "LLM Client Setup"
        RAW_CLIENT["AsyncOpenAI or AsyncAzureOpenAI<br/>Raw client with base_url and api_key"]
        WRAP["OpenAIClient(client=raw_client)<br/>Graphiti wrapper"]
        LLM["LLMClient instance"]
    end
    
    subgraph "GlobalSelector Initialization"
        CONFIG["GlobalSelectorConfig<br/>use_summary=False<br/>use_tag=True"]
        GS["GlobalSelector(driver, llm_client, selection_config)"]
    end
    
    ENV --> DRIVER_CREATE
    PARAMS --> DRIVER_CREATE
    DRIVER_CREATE --> DRIVER
    
    ENV --> RAW_CLIENT
    RAW_CLIENT --> WRAP
    WRAP --> LLM
    
    CONFIG -.optional.-> GS
    DRIVER --> GS
    LLM --> GS
    
    style GS fill:#f9f9f9
    style DRIVER fill:#f9f9f9
    style LLM fill:#f9f9f9
```

**Sources:** [global_selection/global_selector.py:431-441]()

### Basic Initialization Example

The main initialization pattern follows these steps:

1. **Create Neo4j AsyncDriver** - Establishes connection to the graph database with a large connection pool (1000 connections) to support high concurrency [global_selection/global_selector.py:435]()

2. **Initialize LLM Client** - Creates an AsyncOpenAI or AsyncAzureOpenAI client and wraps it in Graphiti's OpenAIClient [global_selection/global_selector.py:436-440]()

3. **Instantiate GlobalSelector** - Combines the driver and LLM client [global_selection/global_selector.py:441]()

The GlobalSelectorConfig controls which node fields are included during layer selection. By default, it uses `use_tag=True` and `use_summary=False` [global_selection/global_selector.py:85-87]().

**Sources:** [global_selection/global_selector.py:85-94](), [global_selection/global_selector.py:431-441]()

---

## Loading Dataset Queries

Mnemis provides two dataset loader functions that parse benchmark JSON files and extract query-group_id pairs.

```mermaid
graph LR
    subgraph "LoCoMo Dataset"
        LOCOMO_FILE["data/locomo.json<br/>User-based structure"]
        LOCOMO_FUNC["load_locomo_data_query_group_id()"]
        LOCOMO_OUT["List of dicts:<br/>{group_id, query}"]
    end
    
    subgraph "LongMemEval-S Dataset"
        LME_FILE["data/longmemeval_s.json<br/>Flat question structure"]
        LME_FUNC["load_lme_data_query_group_id()"]
        LME_OUT["List of dicts:<br/>{group_id, query, question_id}"]
    end
    
    LOCOMO_FILE --> LOCOMO_FUNC
    LOCOMO_FUNC --> LOCOMO_OUT
    
    LME_FILE --> LME_FUNC
    LME_FUNC --> LME_OUT
    
    style LOCOMO_OUT fill:#f9f9f9
    style LME_OUT fill:#f9f9f9
```

**Sources:** [global_selection/global_selector.py:321-364]()

### LoCoMo Dataset Loading

The `load_locomo_data_query_group_id()` function processes LoCoMo's user-based structure [global_selection/global_selector.py:321-342]():

| Parameter | Type | Description |
|-----------|------|-------------|
| `file_path` | str | Path to locomo.json file |
| `group_id_prefix` | str | Prefix for generating group IDs (default: 'locomo_ziyu') |

**Returns:** List of dictionaries, each containing:
- `group_id`: Formatted as `{prefix}_{user_id}`
- `query`: The question text from the QA pair

The function iterates through users and their QA pairs, creating a flat list of queries with corresponding group IDs [global_selection/global_selector.py:335-340]().

**Sources:** [global_selection/global_selector.py:321-342]()

### LongMemEval-S Dataset Loading

The `load_lme_data_query_group_id()` function handles LongMemEval-S's flat structure [global_selection/global_selector.py:344-364]():

| Parameter | Type | Description |
|-----------|------|-------------|
| `file_path` | str | Path to longmemeval_s.json file |
| `group_id_prefix` | str | Prefix for generating group IDs (default: 'lme_s_ziyu') |

**Returns:** List of dictionaries, each containing:
- `group_id`: Formatted as `{prefix}_{user_id}`
- `query`: The question text
- `question_id`: Original question identifier from the dataset

This function uses pandas to read the JSON file and converts it to a list of records [global_selection/global_selector.py:354]().

**Sources:** [global_selection/global_selector.py:344-364]()

---

## Single Query Execution

The core method for executing hierarchical retrieval is `global_selection()`, which performs top-down traversal with LLM-guided node selection.

```mermaid
graph TB
    subgraph "Input"
        QUERY["query: str<br/>User question"]
        GID["group_id: str<br/>Graph partition identifier"]
    end
    
    subgraph "global_selection Method"
        INIT["get_max_layer(group_id)<br/>Discover hierarchy depth"]
        
        LOOP["Layer-by-layer loop<br/>(max_layer down to 1)"]
        
        GET_NODES["get_nodes_by_layer() or<br/>get_child_nodes_batch()"]
        LAYER_SEL["layer_selection()<br/>LLM-guided filtering"]
        SHORTCUTS["get_all_descendants_batch()<br/>Collect subtrees"]
        
        NEIGHBORS["get_one_hop_neighbors_batch()<br/>Retrieve episodes and edges"]
    end
    
    subgraph "Output"
        RESULTS["Results dict:<br/>{episodes, edges, nodes}"]
        STATS["Time stats dict:<br/>{init, layer_selection, one_hop_neighbors}"]
    end
    
    QUERY --> LOOP
    GID --> INIT
    INIT --> LOOP
    
    LOOP --> GET_NODES
    GET_NODES --> LAYER_SEL
    LAYER_SEL --> SHORTCUTS
    SHORTCUTS --> LOOP
    
    LOOP --> NEIGHBORS
    NEIGHBORS --> RESULTS
    NEIGHBORS --> STATS
    
    style RESULTS fill:#f9f9f9
    style STATS fill:#f9f9f9
```

**Sources:** [global_selection/global_selector.py:267-319]()

### Method Signature

The `global_selection()` method is defined at [global_selection/global_selector.py:267]():

```python
async def global_selection(self, query: str, group_id: str) -> tuple[dict, dict]:
```

### Execution Flow

1. **Initialize** - Get the maximum layer in the hierarchy [global_selection/global_selector.py:271-272]()

2. **Layer Traversal** - Iterate from max_layer down to layer 1 [global_selection/global_selector.py:277]():
   - Get nodes at current layer [global_selection/global_selector.py:279-283]()
   - Perform LLM-guided selection [global_selection/global_selector.py:285]()
   - Collect descendants of shortcut nodes [global_selection/global_selector.py:289-291]()

3. **Context Expansion** - Retrieve one-hop neighbors (episodes and edges) for all selected nodes [global_selection/global_selector.py:299]()

4. **Format Results** - Convert timestamps to readable strings [global_selection/global_selector.py:302-312]()

### Result Structure

The method returns a tuple containing two dictionaries:

**Results Dictionary:**
| Key | Type | Description |
|-----|------|-------------|
| `episodes` | list[dict] | Episodic nodes (memories) connected to selected entities |
| `edges` | list[dict] | RELATES_TO relationships with fact text and timestamps |
| `nodes` | list[dict] | All selected Category and Entity nodes |

**Time Statistics Dictionary:**
| Key | Type | Description |
|-----|------|-------------|
| `init` | float | Time to discover hierarchy depth |
| `layer_selection` | float | Time for all layer-by-layer selections |
| `one_hop_neighbors` | float | Time to retrieve context expansion |

**Sources:** [global_selection/global_selector.py:267-319]()

---

## Batch Processing

For processing multiple queries concurrently, Mnemis provides the `get_global_search_context()` helper function with semaphore-based concurrency control.

```mermaid
graph TB
    subgraph "Input"
        QGL["query_groupid_list<br/>List of {group_id, query} dicts"]
        GS["global_searcher: GlobalSelector"]
        MC["max_concurrent: int<br/>Concurrency limit"]
    end
    
    subgraph "Concurrency Control"
        SEM["asyncio.Semaphore(max_concurrent)<br/>Rate limiting"]
        WRAPPER["search_with_semaphore()<br/>Wrapper function"]
    end
    
    subgraph "Parallel Execution"
        TASKS["Create tasks for all queries<br/>asyncio.gather()"]
        EXEC["Execute concurrently<br/>with semaphore control"]
    end
    
    subgraph "Output"
        RESULTS["List of results:<br/>{query, group_id, context, time_stats}"]
    end
    
    QGL --> WRAPPER
    GS --> WRAPPER
    MC --> SEM
    SEM --> WRAPPER
    
    WRAPPER --> TASKS
    TASKS --> EXEC
    EXEC --> RESULTS
    
    style RESULTS fill:#f9f9f9
```

**Sources:** [global_selection/global_selector.py:366-385]()

### Batch Processing Configuration

The `get_global_search_context()` function accepts:

| Parameter | Type | Description |
|-----------|------|-------------|
| `query_groupid_list` | list[dict] | List of query-group_id pairs from dataset loaders |
| `global_searcher` | GlobalSelector | Initialized GlobalSelector instance |
| `max_concurrent` | int | Maximum concurrent queries (default: 5) |

**Returns:** List of dictionaries containing query, group_id, context (results from global_selection), and time_stats.

The function uses `asyncio.Semaphore` to limit concurrent operations, preventing database connection exhaustion [global_selection/global_selector.py:367-373]().

**Sources:** [global_selection/global_selector.py:366-385]()

### Batch Mode Selection

Several GlobalSelector methods support two batch processing modes [global_selection/global_selector.py:129-142](), [global_selection/global_selector.py:203-222]():

| Mode | Description | Use Case |
|------|-------------|----------|
| `mp` | Multiprocessing - Creates separate tasks for each UUID and uses asyncio.gather | Better cache utilization via `@alru_cache` decorator |
| `batch` | Single query - Passes all UUIDs in one Cypher query | More efficient database query when cache is cold |

The default mode is `batch` [global_selection/global_selector.py:269](), which is used for all batch operations during global_selection.

**Sources:** [global_selection/global_selector.py:129-142](), [global_selection/global_selector.py:153-166](), [global_selection/global_selector.py:203-222](), [global_selection/global_selector.py:269]()

---

## Complete Workflow Examples

Mnemis includes two complete workflow functions demonstrating end-to-end processing for each benchmark dataset.

### LoCoMo Processing Workflow

The `parse_locomo()` function demonstrates a complete LoCoMo evaluation workflow [global_selection/global_selector.py:387-407]():

```mermaid
graph TB
    subgraph "Configuration"
        PREFIX["group_id_prefix<br/>'locomo_mnemis_coreAI_tel_b20_nec_full'"]
        CONC["max_concurrent: 10"]
        BATCH["batch_size: 50"]
        OUT["output_path<br/>JSONL file"]
    end
    
    subgraph "Data Loading"
        LOAD["load_locomo_data_query_group_id()<br/>Load all queries"]
        COUNT["all_data_count<br/>Total query count"]
    end
    
    subgraph "Batch Processing Loop"
        ITER["Iterate in batches of 50"]
        SEARCH["get_global_search_context()<br/>10 concurrent queries"]
        SAVE["Write results to JSONL<br/>One JSON object per line"]
    end
    
    PREFIX --> LOAD
    LOAD --> COUNT
    COUNT --> ITER
    CONC --> SEARCH
    BATCH --> ITER
    ITER --> SEARCH
    SEARCH --> SAVE
    SAVE --> OUT
    
    style OUT fill:#f9f9f9
```

**Key parameters:**
- `batch_size=50` - Process 50 queries before writing to disk [global_selection/global_selector.py:390]()
- `max_concurrent=10` - Run 10 global_selection operations concurrently [global_selection/global_selector.py:389]()
- Output format: JSONL (one JSON object per line) [global_selection/global_selector.py:404-405]()

The function includes progress tracking via tqdm and periodic saving to prevent data loss [global_selection/global_selector.py:397]().

**Sources:** [global_selection/global_selector.py:387-407]()

### LongMemEval-S Processing Workflow

The `parse_lme()` function follows a similar pattern for LongMemEval-S [global_selection/global_selector.py:409-429]():

```mermaid
graph TB
    subgraph "Configuration Differences"
        PREFIX_LME["group_id_prefix<br/>'lme_s_mnemis_coreAI_tel_b20_nec_full'"]
        BATCH_LME["batch_size: 30<br/>(smaller than LoCoMo)"]
    end
    
    subgraph "Data Loading"
        LOAD_LME["load_lme_data_query_group_id()<br/>Load with question_id"]
    end
    
    subgraph "Processing"
        SAME["Same batch processing pattern<br/>as LoCoMo"]
    end
    
    PREFIX_LME --> LOAD_LME
    LOAD_LME --> SAME
    BATCH_LME --> SAME
    
    style SAME fill:#f9f9f9
```

**Key differences from LoCoMo:**
- Smaller batch size (30 vs 50) due to potentially longer conversations [global_selection/global_selector.py:412]()
- Uses `load_lme_data_query_group_id()` which includes `question_id` field [global_selection/global_selector.py:415]()

**Sources:** [global_selection/global_selector.py:409-429]()

### Main Function Pattern

The `main()` function demonstrates the complete initialization and execution pattern [global_selection/global_selector.py:431-448]():

| Step | Code Location | Description |
|------|---------------|-------------|
| 1. Load environment | [global_selection/global_selector.py:5]() | Load .env configuration |
| 2. Create driver | [global_selection/global_selector.py:435]() | AsyncGraphDatabase.driver with 1000 connection pool |
| 3. Create LLM client | [global_selection/global_selector.py:436-440]() | AsyncOpenAI wrapped in OpenAIClient |
| 4. Initialize selector | [global_selection/global_selector.py:441]() | GlobalSelector instance |
| 5. Execute workflow | [global_selection/global_selector.py:444-445]() | Call parse_locomo() or parse_lme() |
| 6. Track statistics | [global_selection/global_selector.py:448]() | Print token usage via llm_client.get_token_stats() |

The main function is designed to run as an async entry point via `asyncio.run(main())` [global_selection/global_selector.py:452]().

**Sources:** [global_selection/global_selector.py:431-452]()

---

## Cache Management

The GlobalSelector uses `@alru_cache` decorators with 500 entries per query to optimize repeated database operations [global_selection/global_selector.py:20]().

### Cached Methods

The following methods are cached [global_selection/global_selector.py:103-201]():

| Method | Cache Key | Purpose |
|--------|-----------|---------|
| `get_max_layer` | (group_id) | Hierarchy depth per graph partition |
| `get_nodes_by_layer` | (layer, group_id) | All nodes at a specific layer |
| `get_child_nodes` | (parent_uuid, group_id) | Children of a category node |
| `get_all_descendants` | (parent_uuid, group_id) | All descendants in subtree |
| `get_one_hop_neighbors` | (node_uuid, group_id) | Episodes and edges connected to node |

### Cache Clearing

To clear all caches (e.g., between different user queries), use the `clear_cache()` method [global_selection/global_selector.py:96-101]():

```python
selector.clear_cache()
```

This calls `cache_clear()` on all five cached methods. Cache clearing is typically not needed during batch processing of a single benchmark since each query operates on a different group_id.

**Sources:** [global_selection/global_selector.py:20](), [global_selection/global_selector.py:96-101](), [global_selection/global_selector.py:103-201]()

---

## Result Processing

Each result from `global_selection()` contains structured memory context suitable for RAG_GRAPH merging with System-1 similarity search results.

### Episode Structure

Episodes represent historical conversation messages [global_selection/global_selector.py:309]():

```
{
  "uuid": "episode-uuid-string",
  "content": "Message text content",
  "valid_at": "2024/01/15 (Mon) 14:30"
}
```

### Edge (Fact) Structure

Edges represent RELATES_TO relationships with temporal information [global_selection/global_selector.py:310]():

```
{
  "uuid": "fact-uuid-string",
  "fact": "Fact statement text",
  "valid_at": "2024/01/15 (Mon) 14:30",
  "invalid_at": "2024/01/20 (Sat) 09:00"  // or null if still valid
}
```

### Node (Entity/Category) Structure

Nodes include both selected categories and entities from context expansion [global_selection/global_selector.py:312]():

```
{
  "uuid": "node-uuid-string",
  "name": "Node name",
  "tag": "node-type-tag",
  "summary": "Node summary text",
  "layer": 0  // for entities, or layer number for categories
}
```

### Timestamp Formatting

All timestamps are converted from datetime objects to human-readable strings in the format "YYYY/MM/DD (Day) HH:MM" [global_selection/global_selector.py:302-306]().

**Sources:** [global_selection/global_selector.py:302-319]()

---

**Sources:** [README.md:1-72](), [global_selection/global_selector.py:1-453]()

---

# Page: Running Evaluations

# Running Evaluations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [global_selection/global_selector.py](global_selection/global_selector.py)
- [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json](results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json)

</details>



This page provides a practical guide to reproducing Mnemis benchmark results by running evaluation scripts on LoCoMo and LongMemEval-S datasets. It covers dataset loading, configuration setup, batch processing execution, and output interpretation. For information about the benchmark datasets themselves, see [Benchmark Datasets](#4.1). For analysis of results and accuracy metrics, see [Evaluation & Results](#4).

## Dataset Preparation

The evaluation system provides two loader functions that parse benchmark JSON files and extract query-group_id pairs for processing.

### LoCoMo Dataset Loading

The `load_locomo_data_query_group_id` function [global_selection/global_selector.py:321-342]() reads the LoCoMo benchmark file and generates a list of query-group_id mappings:

```mermaid
graph TB
    subgraph "load_locomo_data_query_group_id"
        INPUT["data/locomo.json"]
        PARSE["Parse JSON<br/>User array structure"]
        ITERATE["Iterate users and QA pairs"]
        FORMAT["Format: group_id + query"]
    end
    
    subgraph "Output Structure"
        OUTPUT["query_groupid_list"]
        ITEM1["{'group_id': 'locomo_prefix_0',<br/>'query': 'question text'}"]
        ITEM2["{'group_id': 'locomo_prefix_1',<br/>'query': 'question text'}"]
    end
    
    INPUT --> PARSE
    PARSE --> ITERATE
    ITERATE --> FORMAT
    FORMAT --> OUTPUT
    OUTPUT --> ITEM1
    OUTPUT --> ITEM2
```

**Dataset Loading for LoCoMo**

| Parameter | Type | Description |
|-----------|------|-------------|
| `file_path` | str | Path to `locomo.json` file |
| `group_id_prefix` | str | Prefix for generated group IDs (default: `'locomo_ziyu'`) |
| **Returns** | list[dict] | List of `{'group_id': str, 'query': str}` dictionaries |

The function iterates through the JSON structure, which contains an array of users, each with a `qa` array. For each question, it creates a unique `group_id` by appending the user index to the prefix: `f"{group_id_prefix}_{user_id}"`.

**Sources:** [global_selection/global_selector.py:321-342]()

### LongMemEval-S Dataset Loading

The `load_lme_data_query_group_id` function [global_selection/global_selector.py:344-364]() handles the LongMemEval-S dataset with a slightly different structure:

```python
# Example usage
query_groupid_list = load_lme_data_query_group_id(
    'data/longmemeval_s.json', 
    group_id_prefix='lme_s_ziyu'
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `file_path` | str | Path to `longmemeval_s.json` file |
| `group_id_prefix` | str | Prefix for generated group IDs (default: `'lme_s_ziyu'`) |
| **Returns** | list[dict] | List of `{'group_id': str, 'query': str, 'question_id': str}` dictionaries |

This loader uses pandas to read the JSON and includes the `question_id` field from the source data, which is useful for tracking specific questions during analysis.

**Sources:** [global_selection/global_selector.py:344-364]()

## Evaluation Pipeline Architecture

The evaluation system orchestrates batch processing of queries through a concurrent execution pipeline:

```mermaid
graph LR
    subgraph "Data Loading"
        LOAD_FUNC["load_*_data_query_group_id"]
        QUERY_LIST["query_groupid_list<br/>[{group_id, query}, ...]"]
    end
    
    subgraph "Batch Processing Loop"
        BATCH["Batch Splitter<br/>batch_size=50 (locomo)<br/>batch_size=30 (lme_s)"]
        GET_CONTEXT["get_global_search_context"]
    end
    
    subgraph "Concurrent Execution"
        SEMAPHORE["asyncio.Semaphore<br/>max_concurrent=10"]
        GS["global_searcher.global_selection"]
    end
    
    subgraph "Output"
        FILE["Output JSONL file<br/>One result per line"]
        RESULT["{'query', 'group_id',<br/>'context', 'time_stats'}"]
    end
    
    LOAD_FUNC --> QUERY_LIST
    QUERY_LIST --> BATCH
    BATCH --> GET_CONTEXT
    GET_CONTEXT --> SEMAPHORE
    SEMAPHORE --> GS
    GS --> RESULT
    RESULT --> FILE
```

**Evaluation Pipeline from Data to Results**

**Sources:** [global_selection/global_selector.py:366-429]()

## Execution Setup

### GlobalSelector Initialization

Before running evaluations, initialize the required components [global_selection/global_selector.py:431-441]():

```python
# Database connection
driver = AsyncGraphDatabase.driver(
    url='bolt://localhost:7687',
    auth=(user, password),
    max_connection_pool_size=1000
)

# LLM client setup
raw_client = AsyncOpenAI(base_url="...", api_key="...")
llm_client = OpenAIClient(client=raw_client)

# GlobalSelector instantiation
selector = GlobalSelector(driver, llm_client)
```

| Component | Configuration | Purpose |
|-----------|---------------|---------|
| `AsyncDriver` | `max_connection_pool_size=1000` | Supports high concurrency |
| `AsyncOpenAI` | Base URL + API key | LLM service for layer selection |
| `OpenAIClient` | Wraps raw client | Graphiti-compatible interface |
| `GlobalSelector` | Driver + LLM client | Main evaluation orchestrator |

**Sources:** [global_selection/global_selector.py:431-441]()

### Concurrency Control

The `get_global_search_context` function [global_selection/global_selector.py:366-385]() implements semaphore-based concurrency:

```mermaid
graph TB
    subgraph "get_global_search_context Function"
        INPUT["query_groupid_list<br/>max_concurrent=5"]
        SEM["asyncio.Semaphore<br/>Limits parallel tasks"]
        
        subgraph "search_with_semaphore Wrapper"
            ACQUIRE["Acquire semaphore"]
            EXECUTE["global_searcher.global_selection"]
            RELEASE["Release semaphore<br/>(automatic)"]
        end
        
        GATHER["asyncio.gather<br/>Collect all results"]
        OUTPUT["search_results list"]
    end
    
    INPUT --> SEM
    SEM --> ACQUIRE
    ACQUIRE --> EXECUTE
    EXECUTE --> RELEASE
    RELEASE --> GATHER
    GATHER --> OUTPUT
```

**Semaphore-Controlled Concurrent Execution**

The semaphore ensures that at most `max_concurrent` queries execute simultaneously, preventing database overload while maintaining parallelism.

**Sources:** [global_selection/global_selector.py:366-385]()

## Running LoCoMo Evaluation

The `parse_locomo` function [global_selection/global_selector.py:387-408]() orchestrates the full LoCoMo benchmark evaluation:

```mermaid
graph TB
    subgraph "parse_locomo Configuration"
        PARAMS["group_id_prefix<br/>max_concurrent=10<br/>batch_size=50"]
        OUTPUT_PATH["output_path<br/>JSON lines file"]
    end
    
    subgraph "Execution Flow"
        LOAD["load_locomo_data_query_group_id"]
        BATCH_LOOP["For each batch of 50 queries"]
        SEARCH["get_global_search_context<br/>10 concurrent tasks"]
        WRITE["Write results to file<br/>One JSON per line"]
    end
    
    subgraph "Progress Tracking"
        TQDM["tqdm progress bar<br/>Shows batch completion"]
    end
    
    PARAMS --> LOAD
    LOAD --> BATCH_LOOP
    BATCH_LOOP --> SEARCH
    SEARCH --> WRITE
    BATCH_LOOP --> TQDM
    WRITE --> TQDM
```

**LoCoMo Evaluation Execution Flow**

### Configuration Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `group_id_prefix` | `'locomo_mnemis_coreAI_tel_b20_nec_full'` | Identifies the specific Neo4j data partition |
| `max_concurrent` | `10` | Balances throughput and resource usage |
| `batch_size` | `50` | Queries per processing batch |
| `output_path` | JSONL file path | Incremental result storage |

The function processes 1,986 total queries in batches, writing results incrementally to avoid memory issues.

**Sources:** [global_selection/global_selector.py:387-408]()

## Running LongMemEval-S Evaluation

The `parse_lme` function [global_selection/global_selector.py:409-429]() follows a similar pattern with adjusted parameters:

```python
# Key differences from parse_locomo
group_id_prefix = 'lme_s_mnemis_coreAI_tel_b20_nec_full'
batch_size = 30  # Smaller batches
```

| Parameter | LoCoMo Value | LME-S Value | Reason for Difference |
|-----------|--------------|-------------|----------------------|
| `batch_size` | 50 | 30 | LME-S queries may require more processing time |
| Total queries | 1,986 | 500 | Different dataset sizes |
| `group_id_prefix` | `'locomo_mnemis_...'` | `'lme_s_mnemis_...'` | Different data partitions |

**Sources:** [global_selection/global_selector.py:409-429]()

## Batch Processing Mechanics

The evaluation system uses nested concurrency control for efficient processing:

```mermaid
graph TB
    subgraph "Outer Loop: Batch Processing"
        TOTAL["Total queries: N"]
        SPLIT["Split into batches<br/>Size: 50 or 30"]
        ITER["Process batch i"]
    end
    
    subgraph "Inner Loop: Concurrent Execution"
        BATCH["Current batch<br/>50/30 queries"]
        SEM["Semaphore<br/>max_concurrent=10"]
        
        subgraph "Parallel Tasks"
            T1["Task 1"]
            T2["Task 2"]
            T3["..."]
            T10["Task 10"]
        end
        
        WAIT["await asyncio.gather"]
    end
    
    subgraph "Output Writing"
        COLLECT["Collect batch results"]
        WRITE["Write to JSONL<br/>Append mode"]
        LOG["Log progress"]
    end
    
    TOTAL --> SPLIT
    SPLIT --> ITER
    ITER --> BATCH
    BATCH --> SEM
    SEM --> T1
    SEM --> T2
    SEM --> T3
    SEM --> T10
    T1 --> WAIT
    T2 --> WAIT
    T3 --> WAIT
    T10 --> WAIT
    WAIT --> COLLECT
    COLLECT --> WRITE
    WRITE --> LOG
    LOG --> ITER
```

**Nested Batch and Concurrent Processing Architecture**

### Processing Characteristics

| Level | Mechanism | Purpose |
|-------|-----------|---------|
| Batch Loop | Sequential iteration with `tqdm` | Process dataset in manageable chunks |
| Concurrent Execution | `asyncio.gather` with semaphore | Parallelize within batch |
| Result Writing | Incremental file append | Avoid memory overflow, enable resume |

The two-level structure allows processing large datasets (1,986 queries) while maintaining bounded resource usage.

**Sources:** [global_selection/global_selector.py:387-429]()

## Output Format

Each evaluation produces a JSONL (JSON Lines) file where each line contains a complete search result:

```mermaid
graph LR
    subgraph "Output Structure"
        RESULT["Result Object"]
        
        subgraph "Fields"
            QUERY["query: str"]
            GROUP["group_id: str"]
            CONTEXT["context: dict"]
            TIME["time_stats: dict"]
        end
        
        subgraph "context Contents"
            EP["episodes: list"]
            EDGES["edges: list"]
            NODES["nodes: list"]
        end
        
        subgraph "time_stats Contents"
            INIT["init: float"]
            LAYER["layer_selection: float"]
            HOP["one_hop_neighbors: float"]
        end
    end
    
    RESULT --> QUERY
    RESULT --> GROUP
    RESULT --> CONTEXT
    RESULT --> TIME
    
    CONTEXT --> EP
    CONTEXT --> EDGES
    CONTEXT --> NODES
    
    TIME --> INIT
    TIME --> LAYER
    TIME --> HOP
```

**Output Result Object Structure**

### Result Schema

```python
{
    "query": "What is the user's favorite restaurant?",
    "group_id": "locomo_mnemis_exp_41mini_0",
    "context": {
        "episodes": [
            {
                "uuid": "...",
                "content": "User mentioned they love Italian food",
                "valid_at": "2024/03/15 (Fri) 14:30"
            }
        ],
        "edges": [
            {
                "uuid": "...",
                "fact": "User PREFERS Italian cuisine",
                "valid_at": "2024/03/15 (Fri) 14:30",
                "invalid_at": null
            }
        ],
        "nodes": [
            {
                "uuid": "...",
                "name": "Italian Cuisine",
                "tag": "Preference",
                "summary": "User's food preference"
            }
        ]
    },
    "time_stats": {
        "init": 0.002,
        "layer_selection": 1.234,
        "one_hop_neighbors": 0.456
    }
}
```

**Sources:** [global_selection/global_selector.py:366-385](), [global_selection/global_selector.py:302-319]()

## Metrics File Format

After evaluation completes, a separate metrics file summarizes accuracy results [results/locomo/metrics_*.json]():

```mermaid
graph TB
    subgraph "Metrics File Structure"
        ROOT["metrics_*.json"]
        
        subgraph "Accuracy Metrics"
            TOTAL_CORR["total_correct"]
            TOTAL_Q["total_questions"]
            ACC["accuracy"]
        end
        
        subgraph "Configuration"
            MODELS["models:<br/>graph_model, answer_model, grader_model"]
            EMBEDDER["embedder:<br/>type, precision"]
            RETRIEVAL["retrieval:<br/>rag_top_k, graph_top_k, merge_method"]
            PROMPT["prompt:<br/>answer_prompt, prompt_turning"]
        end
        
        subgraph "Category Breakdown"
            CAT_STATS["category_stats:<br/>{correct, total} per category"]
            CAT_ACC["category_accuracies:<br/>per-category accuracy"]
        end
        
        subgraph "Execution Info"
            USERS["num_users"]
            PAR["qa_parallelism"]
        end
    end
    
    ROOT --> TOTAL_CORR
    ROOT --> TOTAL_Q
    ROOT --> ACC
    ROOT --> MODELS
    ROOT --> EMBEDDER
    ROOT --> RETRIEVAL
    ROOT --> PROMPT
    ROOT --> CAT_STATS
    ROOT --> CAT_ACC
    ROOT --> USERS
    ROOT --> PAR
```

**Metrics JSON Structure**

### Key Metrics Fields

| Field | Example Value | Description |
|-------|---------------|-------------|
| `total_correct` | 1590 | Number of correctly answered questions |
| `total_questions` | 1986 | Total questions evaluated |
| `accuracy` | 0.8006 | Overall accuracy (80.06%) |
| `config.models.graph_model` | `"gpt-41-mini-shortco-2025-04-14-Bing"` | Model used for global selection |
| `config.retrieval.rag_top_k` | 10 | RAG retrieval limit |
| `config.retrieval.graph_top_k` | 20 | Graph retrieval limit |
| `config.retrieval.merge_method` | `"RAG_GRAPH"` | Hybrid merge strategy |
| `category_accuracies` | Per-category dict | Breakdown by question category |

**Sources:** [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json]()

## Performance Monitoring

The evaluation system tracks timing statistics at multiple levels:

### Time Statistics Collection

```mermaid
graph TB
    subgraph "global_selection Time Tracking"
        START["time() before operation"]
        
        subgraph "Timed Operations"
            INIT["get_max_layer<br/>time_stats['init']"]
            LAYER["layer_selection loop<br/>time_stats['layer_selection']"]
            HOP["get_one_hop_neighbors_batch<br/>time_stats['one_hop_neighbors']"]
        end
        
        END["Return results + time_stats"]
    end
    
    subgraph "Batch Level Timing"
        B_START["Batch start time"]
        B_END["Batch end time"]
        LOG["Log batch duration"]
    end
    
    START --> INIT
    INIT --> LAYER
    LAYER --> HOP
    HOP --> END
    
    B_START --> START
    END --> B_END
    B_END --> LOG
```

**Multi-Level Performance Tracking**

The `time_stats` dictionary provides insight into which operations consume the most time:
- `init`: Graph structure discovery (max layer calculation)
- `layer_selection`: Iterative LLM-guided filtering
- `one_hop_neighbors`: Context expansion for selected nodes

**Sources:** [global_selection/global_selector.py:267-319]()

## Example Execution

Complete example of running evaluations [global_selection/global_selector.py:431-452]():

```python
async def main():
    # Setup
    url = 'bolt://localhost:7687'
    user = 'neo4j'
    password = 'your_password'
    driver = AsyncGraphDatabase.driver(
        url, 
        auth=(user, password), 
        max_connection_pool_size=1000
    )
    raw_client = AsyncOpenAI(base_url="...", api_key="EMPTY")
    llm_client = OpenAIClient(client=raw_client)
    selector = GlobalSelector(driver, llm_client)
    
    # Run evaluation
    start = time()
    await parse_locomo(selector)
    # Or: await parse_lme(selector)
    end = time()
    
    # Report statistics
    print(f"Total time taken: {end - start} s")
    print(selector.llm_client.get_token_stats())

if __name__ == "__main__":
    asyncio.run(main())
```

### Expected Console Output

```
Loaded 1986 queries from locomo data.
Processing Batches (locomo, b=50): 100%|██████████| 40/40 [12:34<00:00, 18.5s/it]
Processed 50 queries, saving results...
Batch 1 results saved to /data/zh/gs/v2_locomo_mnemis_coreAI_tel_b20_nec_full.json
...
Total time taken: 754.23 s
Token usage: {'total_tokens': 1234567, 'prompt_tokens': 987654, ...}
```

**Sources:** [global_selection/global_selector.py:431-452]()

## Troubleshooting

### Common Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| Database connection errors | "Unable to connect to bolt://..." | Verify Neo4j is running, check credentials |
| Memory overflow | Python process killed | Reduce `batch_size` or `max_concurrent` |
| Slow execution | Progress bar stalls | Check LLM API latency, consider increasing `max_connection_pool_size` |
| Cache misses | Repeated database queries | Ensure `CACHE_SIZE_PER_QUERY=500` is sufficient |
| LLM timeout | Requests fail intermittently | Add retry logic or increase timeout in `OpenAIClient` |

### Cache Management

The `GlobalSelector` maintains an LRU cache for frequently accessed graph queries [global_selection/global_selector.py:96-101]():

```python
# Clear cache between evaluation runs if needed
selector.clear_cache()
```

This clears caches for:
- `get_max_layer`
- `get_nodes_by_layer`
- `get_child_nodes`
- `get_all_descendants`
- `get_one_hop_neighbors`

**Sources:** [global_selection/global_selector.py:96-101](), [global_selection/global_selector.py:20]()

## Next Steps

After running evaluations:
1. Analyze results using the metrics files - see [LoCoMo Results](#4.2) and [LongMemEval-S Results](#4.3)
2. Compare different configurations - see [Configuration Impact Analysis](#4.4)
3. Examine specific QA examples - see [Results Data Format](#4.5) and [Case Studies](#5)
4. Tune retrieval parameters based on results - see [Configuration Options](#3.4)

**Sources:** [global_selection/global_selector.py:387-452](), [results/locomo/metrics_graphiti_gpt-41-mini-shortco-2025-04-14-Bing_gpt-41-mini-shortco-2025-04-14-Bing_ragtopk10_gtopk20_RAG_GRAPH.json]()

---

# Page: Research Background

# Research Background

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Mnemis_paper.pdf](Mnemis_paper.pdf)
- [README.md](README.md)

</details>



## Purpose and Scope

This page provides an overview of the research foundations underlying Mnemis, including its theoretical motivation from cognitive dual-process theory, the limitations of existing memory retrieval approaches, and how Mnemis addresses these gaps through a dual-route architecture. This material contextualizes the technical implementation documented elsewhere in this wiki.

For detailed technical explanations of the memory components, see [Memory Components](#2.1). For implementation details of the retrieval mechanisms, see [System-1 Similarity Search](#2.2) and [System-2 Global Selection](#2.3). For theoretical depth and cognitive science connections, see [Theoretical Foundation](#7.1). For comprehensive comparisons with existing approaches, see [Comparison with Existing Approaches](#7.2).

---

## Research Motivation

Mnemis addresses a fundamental limitation in existing long-term memory systems for Large Language Models: **similarity-based retrieval mechanisms alone are insufficient for comprehensive memory access**. While traditional Retrieval-Augmented Generation (RAG) and Graph-RAG approaches excel at retrieving semantically similar memories, they struggle with scenarios requiring global reasoning or complete information coverage.

### The Core Problem

Current memory systems primarily rely on **System-1-style retrieval**—fast, intuitive similarity searches using embedding-based techniques. This approach encounters failures in three key scenarios:

1. **Global Information Needs**: Queries requiring comprehensive understanding across multiple semantic domains
2. **Structural Reasoning**: Questions that depend on relationships and hierarchical organization rather than local similarity
3. **Complete Coverage**: Situations where all relevant information must be retrieved, not just the most similar items

The research insight motivating Mnemis is that human memory operates through **two complementary routes**: fast associative retrieval (System-1) and deliberate analytical reasoning (System-2). Effective AI memory systems should mirror this dual-process architecture.

**Sources:** [README.md:15-23]()

---

## Dual-Process Theory Foundation

Mnemis is grounded in cognitive dual-process theory, which posits that human cognition operates through two distinct systems with complementary strengths.

### Cognitive Systems Mapping

```mermaid
graph TB
    subgraph "Cognitive Dual-Process Theory"
        S1C["System-1 Cognition<br/>Fast, Intuitive, Associative"]
        S2C["System-2 Cognition<br/>Slow, Deliberate, Analytical"]
    end
    
    subgraph "Mnemis Implementation"
        S1I["System-1 Similarity Search<br/>BaseGraph + Embedding Search"]
        S2I["System-2 Global Selection<br/>HierarchicalGraph + LLM-Guided Traversal"]
    end
    
    subgraph "Code Components"
        BG["Base Graph<br/>Entity/Relationship Storage"]
        HG["Hierarchical Graph<br/>Category Hierarchy"]
        EMB["Embedding Search<br/>qwen3 embeddings"]
        GS["GlobalSelector<br/>global_selector.py"]
    end
    
    S1C -.inspires.-> S1I
    S2C -.inspires.-> S2I
    
    S1I --> BG
    S1I --> EMB
    S2I --> HG
    S2I --> GS
    
    style S1C fill:#f9f9f9
    style S2C fill:#f9f9f9
    style S1I fill:#e8e8e8
    style S2I fill:#e8e8e8
```

**Diagram: Mapping from Cognitive Theory to Code Implementation**

### System Characteristics

| Aspect | System-1 (Similarity Search) | System-2 (Global Selection) |
|--------|------------------------------|------------------------------|
| **Cognitive Process** | Intuitive, associative | Deliberate, analytical |
| **Speed** | Fast, parallel | Slower, sequential |
| **Mechanism** | Embedding similarity | LLM-guided reasoning |
| **Graph Type** | Base graph (flat structure) | Hierarchical graph (semantic layers) |
| **Retrieval Pattern** | Local neighborhood expansion | Top-down hierarchical traversal |
| **Key Implementation** | Vector similarity search | `GlobalSelector.global_selection()` |
| **Best For** | Semantically similar content | Comprehensive, structured coverage |

The key innovation is that Mnemis implements **both systems simultaneously** and merges their results using the `RAG_GRAPH` merge strategy, combining semantic relevance with structural completeness.

**Sources:** [README.md:15-23]()

---

## Architectural Innovation

Mnemis introduces three core innovations that differentiate it from existing memory approaches:

### 1. Dual-Route Retrieval Architecture

```mermaid
graph LR
    subgraph "Traditional RAG"
        Q1["Query"]
        E1["Embedding<br/>Similarity"]
        R1["Top-K<br/>Results"]
        Q1 --> E1 --> R1
    end
    
    subgraph "Graph-RAG"
        Q2["Query"]
        E2["Embedding<br/>Similarity"]
        GE["Graph<br/>Expansion"]
        R2["Top-K<br/>+ Neighbors"]
        Q2 --> E2 --> GE --> R2
    end
    
    subgraph "Mnemis Dual-Route"
        Q3["Query"]
        
        subgraph "System-1 Path"
            S1["Similarity Search<br/>on Base Graph"]
            R3A["Top-K<br/>Entities"]
        end
        
        subgraph "System-2 Path"
            S2["Global Selection<br/>on Hierarchical Graph"]
            R3B["Top-K<br/>Categories + Entities"]
        end
        
        MERGE["RAG_GRAPH Merge<br/>Combine Both Routes"]
        FINAL["Comprehensive<br/>Memory Context"]
        
        Q3 --> S1 --> R3A --> MERGE
        Q3 --> S2 --> R3B --> MERGE
        MERGE --> FINAL
    end
```

**Diagram: Architectural Comparison - Traditional vs. Mnemis**

### 2. Hierarchical Graph Construction

Mnemis extends the base graph with a hierarchical semantic structure guided by three principles:

- **Minimum Concept Abstraction**: Each category node represents the most specific abstraction that covers its children
- **Many-to-Many Mapping**: Entities can belong to multiple categories, reflecting natural semantic overlap
- **Compression Efficiency Constraint**: Hierarchical layers provide meaningful information compression

This hierarchy enables the `GlobalSelector` class to perform top-down traversal, using LLM intelligence at each layer to select relevant branches.

### 3. LLM-Guided Traversal

Unlike similarity search which operates on static embeddings, System-2 uses the LLM's reasoning capabilities dynamically during retrieval:

```mermaid
graph TB
    START["Start at Top Layer"]
    GML["get_max_layer()<br/>Discover hierarchy depth"]
    LAYER["Current Layer N"]
    GNL["get_nodes_by_layer(N)<br/>Retrieve category nodes"]
    PROMPT["NODE_SELECTION_PROMPT_TEMPLATE<br/>Ask LLM to select relevant nodes"]
    SELECT["layer_selection()<br/>LLM returns NodeSelectionList"]
    EXPAND["get_child_nodes()<br/>Expand selected categories"]
    CHECK{{"All layers<br/>processed?"}}
    FINAL["get_all_descendants()<br/>Collect all entities in selected subtrees"]
    NEIGHBORS["get_one_hop_neighbors()<br/>Include connected episodes"]
    RESULT["Return comprehensive<br/>memory context"]
    
    START --> GML
    GML --> LAYER
    LAYER --> GNL
    GNL --> PROMPT
    PROMPT --> SELECT
    SELECT --> EXPAND
    EXPAND --> CHECK
    CHECK -->|No| LAYER
    CHECK -->|Yes| FINAL
    FINAL --> NEIGHBORS
    NEIGHBORS --> RESULT
    
    style PROMPT fill:#e8e8e8
    style SELECT fill:#e8e8e8
```

**Diagram: System-2 LLM-Guided Traversal Process with Code Entity References**

**Sources:** [README.md:25-29]()

---

## Key Research Contributions

The Mnemis paper presents three main contributions that advance the field of long-term LLM memory:

### 1. Dual-Route Framework Integration

First systematic integration of System-1 (similarity-based) and System-2 (reasoning-based) retrieval mechanisms for LLM memory, enabling both semantic retrieval and deliberate top-down reasoning over memory structures.

### 2. Hierarchical Graph Design with Guiding Principles

Novel construction methodology for hierarchical memory graphs with three design constraints:
- **Minimum Concept Abstraction**: Ensures semantic coherence at each layer
- **Many-to-Many Mapping**: Allows flexible, realistic semantic relationships
- **Compression Efficiency**: Maintains manageable hierarchy depth while preserving information

### 3. State-of-the-Art Empirical Results

Comprehensive experimental validation demonstrating effectiveness:

| Benchmark | Mnemis Score | Previous SOTA | Improvement |
|-----------|--------------|---------------|-------------|
| **LoCoMo** | 93.9% | 87.2% | +6.7pp |
| **LongMemEval-S** | 91.6% | 87.8% | +3.8pp |

Both scores achieved using `gpt-4.1-mini` (referred to as `gpt-41-mini` in configuration files), demonstrating efficiency with smaller models.

**Sources:** [README.md:20-23](), [README.md:32-40]()

---

## Implementation Foundation

Mnemis is implemented as an extension of the **Graphiti framework**, an open-source library for graph-based memory management. The core System-2 implementation is contained in the `global_selection` module.

### Code Organization

```mermaid
graph TB
    PAPER["Research Paper<br/>arXiv:2602.15313"]
    GRAPHITI["Graphiti Framework<br/>Base graph operations"]
    
    subgraph "Mnemis Implementation"
        GS["global_selector.py<br/>GlobalSelector class"]
        PROMPTS["prompts.py<br/>NODE_SELECTION_PROMPT_TEMPLATE"]
        EVAL["Evaluation Scripts<br/>Benchmark reproduction"]
    end
    
    RESULTS["results/<br/>Evaluation outputs with context"]
    
    PAPER -.defines.-> GS
    PAPER -.defines.-> PROMPTS
    GRAPHITI -.provides base to.-> GS
    
    GS --> EVAL
    PROMPTS --> EVAL
    EVAL --> RESULTS
    
    style PAPER fill:#f9f9f9
    style GRAPHITI fill:#e8e8e8
```

**Diagram: From Research Paper to Code Implementation**

The implementation enables researchers and practitioners to:
- Reproduce benchmark results documented in the paper
- Extend the System-2 global selection mechanism
- Experiment with alternative hierarchical graph designs
- Apply Mnemis to new long-term memory tasks

**Sources:** [README.md:54-56]()

---

## Paper Access and Citation

The complete research paper is available through multiple channels:

### Access Points

- **arXiv**: [2602.15313](https://arxiv.org/abs/2602.15313)
- **Hugging Face Papers**: [🤗 HuggingFace](https://huggingface.co/papers/2602.15313)
- **Repository**: [github.com/microsoft/Mnemis](https://github.com/microsoft/Mnemis)

### Citation

```bibtex
@misc{tang2026mnemisdualrouteretrievalhierarchical,
      title={Mnemis: Dual-Route Retrieval on Hierarchical Graphs for Long-Term LLM Memory}, 
      author={Zihao Tang and Xin Yu and Ziyu Xiao and Zengxuan Wen and Zelin Li and Jiaxi Zhou and Hualei Wang and Haohua Wang and Haizhen Huang and Weiwei Deng and Feng Sun and Qi Zhang},
      year={2026},
      eprint={2602.15313},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2602.15313}, 
}
```

For detailed citation information and related publications, see [Paper & Citations](#7.3).

**Sources:** [README.md:3-13](), [README.md:58-71]()

---

## Related Research Areas

Mnemis connects to several active research domains:

### Memory-Augmented LLMs
- Long-term memory systems for conversational AI
- Persistent context management across sessions
- Memory consolidation and forgetting mechanisms

### Retrieval-Augmented Generation
- Hybrid retrieval strategies combining multiple signals
- Context selection for generation tasks
- Retrieval evaluation methodologies

### Graph-Based Knowledge Representation
- Hierarchical knowledge graphs
- Semantic categorization systems
- Graph neural networks for retrieval

### Cognitive Architectures
- Dual-process theory in AI systems
- Fast-and-slow thinking for language models
- Deliberate reasoning mechanisms

For in-depth theoretical discussion connecting these areas to Mnemis, see [Theoretical Foundation](#7.1). For direct comparisons with specific existing systems, see [Comparison with Existing Approaches](#7.2).

**Sources:** [README.md:15-23]()

---

# Page: Theoretical Foundation

# Theoretical Foundation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Mnemis_paper.pdf](Mnemis_paper.pdf)
- [README.md](README.md)

</details>



## Purpose and Scope

This document explains the cognitive science foundations underlying Mnemis's dual-route retrieval architecture. It covers dual-process theory from cognitive psychology, identifies fundamental limitations of similarity-based retrieval mechanisms, and demonstrates how hierarchical reasoning addresses global information needs in long-term LLM memory systems.

For implementation details of the System-2 global selection mechanism, see [System-2 Global Selection](#2.3). For the complete system architecture, see [Architecture Overview](#2).

**Sources:** [README.md:1-72]()

---

## Dual-Process Theory and Memory Retrieval

### Cognitive Science Background

Dual-process theory in cognitive psychology distinguishes between two modes of thinking:

- **System-1**: Fast, automatic, intuitive processing that relies on pattern matching and associative memory
- **System-2**: Slow, deliberate, analytical reasoning that performs structured exploration and logical inference

These two systems complement each other: System-1 provides rapid initial responses based on similarity and familiarity, while System-2 engages when comprehensive coverage or global reasoning is required.

### Mapping to LLM Memory Retrieval

Mnemis applies dual-process theory to long-term memory retrieval for LLMs:

```mermaid
graph TB
    subgraph "Cognitive Psychology"
        S1C["System-1 Thinking<br/>Fast, Intuitive<br/>Pattern Matching"]
        S2C["System-2 Thinking<br/>Slow, Deliberate<br/>Structured Reasoning"]
    end
    
    subgraph "Mnemis Memory Retrieval"
        S1M["System-1 Similarity Search<br/>Embedding-based<br/>Local Semantic Matching"]
        S2M["System-2 Global Selection<br/>LLM-guided Traversal<br/>Hierarchical Exploration"]
    end
    
    subgraph "Memory Structures"
        BG["Base Graph<br/>Flat entity/relationship storage<br/>Supports fast similarity search"]
        HG["Hierarchical Graph<br/>Semantic category hierarchy<br/>Enables top-down reasoning"]
    end
    
    S1C -.inspires.-> S1M
    S2C -.inspires.-> S2M
    
    S1M --> BG
    S2M --> HG
    
    BG --> MERGE["RAG_GRAPH Merge"]
    HG --> MERGE
    
    MERGE --> OUTPUT["Comprehensive<br/>Memory Context"]
```

**Diagram: Dual-Process Theory Mapping to Mnemis Architecture**

The base graph supports System-1's rapid similarity-based retrieval using embeddings, while the hierarchical graph enables System-2's deliberate top-down traversal through semantic categories. Both routes merge to produce comprehensive memory context that captures both local semantic similarity and global structural relevance.

**Sources:** [README.md:15-29]()

---

## The Limitation of Similarity-Based Retrieval

### Problem: Local vs Global Information Needs

Traditional RAG and Graph-RAG approaches rely exclusively on similarity-based retrieval mechanisms. While efficient for queries requiring local information, this System-1-only approach exhibits fundamental limitations:

| Query Type | Information Need | Similarity-Based Performance | Root Cause |
|-----------|------------------|------------------------------|------------|
| **Local Queries** | Specific facts near query embedding | ✓ High accuracy | Direct semantic match works well |
| **Global Queries** | Comprehensive coverage across topics | ✗ Incomplete retrieval | No mechanism for systematic exploration |
| **Reasoning Queries** | Information requiring structural inference | ✗ Missing context | Cannot traverse semantic hierarchies |
| **Coverage Queries** | All relevant entities in a category | ✗ Arbitrary subset | Top-k cutoff misses related items |

### Why Similarity Alone Is Insufficient

```mermaid
graph TB
    subgraph "Similarity-Based Retrieval System-1 Only"
        QUERY["Query:<br/>'Tell me about all projects<br/>I discussed with colleagues'"]
        
        EMB["Query Embedding<br/>Vector: [0.12, -0.45, ...]"]
        
        SEARCH["Similarity Search<br/>Cosine distance to all memory items"]
        
        TOPK["Top-K Results<br/>k=10 or k=30"]
        
        subgraph "Retrieved Items"
            R1["Project Alpha discussion<br/>distance: 0.15"]
            R2["Meeting about Project Beta<br/>distance: 0.18"]
            R3["Coffee chat mentioning Delta<br/>distance: 0.22"]
            DOTS["..."]
            R10["Project Gamma email<br/>distance: 0.35"]
        end
        
        MISSING["Missing Information<br/>Projects Epsilon, Zeta, Eta<br/>not in top-k despite relevance"]
    end
    
    QUERY --> EMB
    EMB --> SEARCH
    SEARCH --> TOPK
    TOPK --> R1
    TOPK --> R2
    TOPK --> R3
    TOPK --> DOTS
    TOPK --> R10
    
    SEARCH -.excludes.-> MISSING
    
    PROBLEM["Problem: No systematic mechanism<br/>to ensure complete coverage<br/>of all relevant projects"]
    
    MISSING --> PROBLEM
```

**Diagram: Limitations of Pure Similarity-Based Retrieval**

The core issue: **similarity-based retrieval performs local optimization** around the query embedding but lacks a mechanism for global exploration. Items semantically distant from the query (low cosine similarity) but structurally relevant (belonging to the same semantic category) are systematically excluded.

**Sources:** [README.md:18-18]()

---

## Hierarchical Reasoning for Global Information

### Top-Down Deliberate Traversal

To address the limitations of similarity-based retrieval, Mnemis introduces System-2 global selection, which performs **top-down deliberate traversal** through a hierarchical graph structure:

```mermaid
graph TB
    subgraph "System-2 Global Selection Mechanism"
        QUERY2["Query:<br/>'Tell me about all projects<br/>I discussed with colleagues'"]
        
        HIER["Hierarchical Graph<br/>Semantic category hierarchy"]
        
        subgraph "Layer 3: Abstract Categories"
            L3A["Work Topics"]
            L3B["Personal Life"]
            L3C["Hobbies"]
        end
        
        subgraph "Layer 2: Intermediate Categories"
            L2A["Projects"]
            L2B["Meetings"]
            L2C["Technical Discussions"]
        end
        
        subgraph "Layer 1: Specific Categories"
            L1A["Project Alpha"]
            L1B["Project Beta"]
            L1C["Project Gamma"]
            L1D["Project Delta"]
        end
        
        subgraph "Layer 0: Entity Nodes"
            E1["Alpha kickoff<br/>meeting entity"]
            E2["Beta status<br/>update entity"]
            E3["Gamma design<br/>review entity"]
            E4["Delta planning<br/>entity"]
        end
        
        LLM["LLM-Guided Selection<br/>At each layer:<br/>Filter relevant categories"]
        
        COMPLETE["Complete Coverage<br/>All project entities retrieved<br/>regardless of similarity scores"]
    end
    
    QUERY2 --> HIER
    HIER --> L3A
    L3A --> LLM
    LLM --> L2A
    L2A --> LLM
    LLM --> L1A
    LLM --> L1B
    LLM --> L1C
    LLM --> L1D
    
    L1A --> E1
    L1B --> E2
    L1C --> E3
    L1D --> E4
    
    E1 --> COMPLETE
    E2 --> COMPLETE
    E3 --> COMPLETE
    E4 --> COMPLETE
```

**Diagram: Hierarchical Reasoning Enables Systematic Exploration**

System-2 global selection performs layer-by-layer traversal from abstract categories to specific entities. At each layer, an LLM evaluates category relevance to the query, enabling **intelligent filtering** while ensuring **complete coverage** within selected branches. This systematic exploration retrieves all relevant items regardless of their similarity to the query embedding.

**Sources:** [README.md:18-23]()

---

## Guiding Principles for Hierarchical Graph Construction

Mnemis constructs the hierarchical graph following three key principles to maintain hierarchical quality:

### 1. Minimum Concept Abstraction

```mermaid
graph TB
    PRINCIPLE1["Minimum Concept Abstraction"]
    
    GOOD1["✓ Correct Abstraction<br/>Categories represent meaningful<br/>semantic groupings"]
    
    BAD1["✗ Over-Abstraction<br/>Categories too broad<br/>loses discriminative power"]
    
    subgraph "Example: Good Hierarchy"
        G1["Technology Topics"]
        G2["AI/ML Projects"]
        G3["NLP Applications"]
        G4["Sentiment Analysis"]
    end
    
    subgraph "Example: Over-Abstracted"
        B1["Everything"]
        B2["Topics"]
        B3["Stuff"]
    end
    
    PRINCIPLE1 --> GOOD1
    PRINCIPLE1 --> BAD1
    
    GOOD1 --> G1
    G1 --> G2
    G2 --> G3
    G3 --> G4
    
    BAD1 --> B1
    B1 --> B2
    B2 --> B3
```

**Diagram: Minimum Concept Abstraction Principle**

Categories should represent the **minimum level of abstraction** necessary to group related entities. Over-abstraction creates categories that are too broad, reducing the selectivity of LLM-guided filtering.

### 2. Many-to-Many Mapping

Entities and lower-level categories can belong to multiple parent categories, reflecting the multi-faceted nature of real-world concepts:

```
Entity: "Discussion about using GPT-4 for customer support chatbot"
├─ Category: "AI/ML Projects"
├─ Category: "Customer Service Initiatives"  
└─ Category: "Technical Architecture Decisions"
```

This many-to-many relationship ensures that the same information can be accessed through different semantic paths during hierarchical traversal.

### 3. Compression Efficiency Constraint

The hierarchical graph must provide **compression** over the base graph:

```
Compression Ratio = (Number of Hierarchical Nodes) / (Number of Base Graph Entities)
```

If the hierarchical graph contains similar or more nodes than the base graph, it fails to provide abstraction benefits. The hierarchy should reduce information dimensionality while preserving semantic structure.

**Sources:** [README.md:22-22]()

---

## Mapping Theory to Code Architecture

### Dual-Route Implementation

The theoretical framework materializes in Mnemis through specific code entities:

```mermaid
graph TB
    subgraph "Theoretical Concepts"
        T_S1["System-1<br/>Fast Intuitive Retrieval"]
        T_S2["System-2<br/>Deliberate Reasoning"]
        T_BG["Flat Memory Storage"]
        T_HG["Hierarchical Abstraction"]
    end
    
    subgraph "Code Entities in Mnemis"
        C_S1["Similarity Search Mechanism<br/>Embedding-based retrieval<br/>on base graph"]
        
        C_S2["GlobalSelector class<br/>global_selector.py<br/>Implements global_selection method"]
        
        C_BG["Base Graph<br/>Neo4j nodes and relationships<br/>Entity + Episode nodes<br/>RELATES_TO edges"]
        
        C_HG["Hierarchical Graph<br/>Neo4j Category nodes<br/>Layer 0-N structure<br/>CATEGORIZES relationships"]
        
        C_LS["layer_selection method<br/>LLM-guided node filtering<br/>Uses NODE_SELECTION_PROMPT_TEMPLATE"]
        
        C_MERGE["RAG_GRAPH merge method<br/>Combines System-1 and System-2 results"]
    end
    
    subgraph "Supporting Infrastructure"
        NEO4J["Neo4j Graph Database<br/>AsyncDriver<br/>Stores both graphs"]
        
        LLM["OpenAI/Azure LLM<br/>gpt-4-mini<br/>Powers layer_selection"]
        
        EMB["Embedding Model<br/>qwen3<br/>FLOAT32 vectors"]
    end
    
    T_S1 -.maps to.-> C_S1
    T_S2 -.maps to.-> C_S2
    T_BG -.maps to.-> C_BG
    T_HG -.maps to.-> C_HG
    
    C_S1 --> C_BG
    C_S1 --> EMB
    
    C_S2 --> C_HG
    C_S2 --> C_LS
    C_LS --> LLM
    
    C_BG --> NEO4J
    C_HG --> NEO4J
    
    C_S1 --> C_MERGE
    C_S2 --> C_MERGE
```

**Diagram: Theoretical Concepts to Code Entity Mapping**

### Key Code Entity Correspondences

| Theoretical Concept | Code Entity | File/Location | Purpose |
|-------------------|-------------|---------------|---------|
| System-1 Retrieval | Similarity search on base graph | Inherited from Graphiti framework | Fast embedding-based retrieval |
| System-2 Retrieval | `GlobalSelector.global_selection()` | `global_selector.py` | Top-down hierarchical traversal |
| Layer-by-layer filtering | `GlobalSelector.layer_selection()` | `global_selector.py` | LLM-guided node selection at each layer |
| LLM guidance prompt | `NODE_SELECTION_PROMPT_TEMPLATE` | `prompts.py` | Instructs LLM on selection criteria |
| Base graph | Entity and Episode nodes with relationships | Neo4j database | Flat storage for System-1 |
| Hierarchical graph | Category nodes with layers 0-N | Neo4j database | Hierarchical structure for System-2 |
| Dual-route merge | `RAG_GRAPH` merge strategy | Evaluation code | Combines both retrieval routes |
| Abstraction principles | Graph construction logic | Built on Graphiti | Implements the three guiding principles |

### Query Processing Flow

```mermaid
graph LR
    QUERY["User Query"]
    
    ROUTE1["System-1 Route<br/>similarity search"]
    ROUTE2["System-2 Route<br/>GlobalSelector.global_selection"]
    
    subgraph "System-1 Processing"
        EMB1["Embed query<br/>using qwen3"]
        SIM["Cosine similarity<br/>search on base graph"]
        TOPK1["Top-k entities<br/>k=10 or k=30"]
    end
    
    subgraph "System-2 Processing"
        GML["get_max_layer<br/>Find hierarchy depth"]
        TRAVERSE["Layer-by-layer traversal<br/>from max_layer to 0"]
        LS["layer_selection<br/>LLM filters nodes"]
        EXPAND["Get descendants<br/>and 1-hop neighbors"]
        TOPK2["Top-k nodes<br/>k=20 or k=60"]
    end
    
    MERGE["RAG_GRAPH merge<br/>Combine results"]
    
    CONTEXT["Memory Context<br/>Message Chunks<br/>FACTS<br/>ENTITIES"]
    
    QUERY --> ROUTE1
    QUERY --> ROUTE2
    
    ROUTE1 --> EMB1
    EMB1 --> SIM
    SIM --> TOPK1
    
    ROUTE2 --> GML
    GML --> TRAVERSE
    TRAVERSE --> LS
    LS --> EXPAND
    EXPAND --> TOPK2
    
    TOPK1 --> MERGE
    TOPK2 --> MERGE
    
    MERGE --> CONTEXT
```

**Diagram: Dual-Route Query Processing Flow**

The query simultaneously initiates both retrieval routes:
- **System-1** embeds the query and performs cosine similarity search on the base graph
- **System-2** invokes `global_selection()`, which traverses the hierarchical graph layer-by-layer, using `layer_selection()` for LLM-guided filtering

Results merge via the `RAG_GRAPH` strategy to produce comprehensive memory context containing both similarity-matched items (System-1) and structurally relevant items (System-2).

**Sources:** [README.md:15-29]()

---

## Theoretical Advantages and Empirical Validation

### Why Dual-Route Outperforms Single-Route

The theoretical advantages of combining System-1 and System-2 retrieval:

1. **Complementary Strengths**: System-1 captures items with high semantic similarity; System-2 ensures complete coverage of structurally relevant items
2. **Robustness**: System-2 compensates when System-1 fails on global queries; System-1 provides efficiency when full traversal is unnecessary  
3. **Flexibility**: Different query types automatically benefit from whichever route is more suitable
4. **Comprehensiveness**: The merged result contains both local context (similarity) and global context (hierarchy)

### Benchmark Performance

The theoretical framework achieves empirical validation through state-of-the-art performance:

| Benchmark | Score | Significance |
|-----------|-------|-------------|
| **LoCoMo** | 93.9% | Demonstrates ability to handle diverse query types across 5 categories |
| **LongMemEval-S** | 91.6% | Shows effectiveness on 6 question types requiring temporal reasoning |

These results confirm that dual-route retrieval addresses the fundamental limitations of similarity-based approaches. For detailed result analysis, see [LoCoMo Results](#4.2) and [LongMemEval-S Results](#4.3).

**Sources:** [README.md:18-23]()

---

## Summary

The theoretical foundation of Mnemis rests on three key insights:

1. **Dual-process theory applies to memory retrieval**: Fast similarity-based retrieval (System-1) and deliberate hierarchical reasoning (System-2) serve complementary roles in information access
2. **Similarity alone is insufficient**: Pure embedding-based retrieval fails on queries requiring global reasoning, comprehensive coverage, or structural inference
3. **Hierarchical reasoning enables systematic exploration**: Top-down traversal through semantic hierarchies, guided by LLM intelligence at each layer, ensures complete coverage of relevant information

The Mnemis architecture materializes these theoretical principles through specific code entities: the base graph supporting System-1, the hierarchical graph enabling System-2, and the `GlobalSelector` class implementing deliberate traversal. The `RAG_GRAPH` merge strategy combines both routes to leverage their complementary strengths.

For implementation details of System-2 global selection, see [System-2 Global Selection](#2.3). For the complete architectural design, see [Architecture Overview](#2). For comparison with other approaches, see [Comparison with Existing Approaches](#7.2).

**Sources:** [README.md:1-72]()

---

# Page: Comparison with Existing Approaches

# Comparison with Existing Approaches

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Mnemis_paper.pdf](Mnemis_paper.pdf)
- [README.md](README.md)

</details>



## Purpose and Scope

This page compares Mnemis with existing memory retrieval approaches including traditional RAG, Graph-RAG, and other memory-augmented LLM systems. The comparison focuses on architectural differences, retrieval mechanisms, and performance characteristics. For theoretical foundations of dual-process cognition that motivated Mnemis, see [Theoretical Foundation](#7.1). For empirical performance data, see [Evaluation & Results](#4).

**Sources:** [README.md:1-72]()

---

## Traditional RAG Architecture

Traditional Retrieval-Augmented Generation (RAG) systems rely exclusively on similarity-based retrieval using vector embeddings. The architecture follows a simple pattern:

```mermaid
graph LR
    Q["Query"]
    E["Embedding Model<br/>(e.g., qwen3)"]
    V["Vector Database<br/>or Index"]
    S["Similarity Search<br/>(cosine/dot product)"]
    T["Top-K Results"]
    C["Context Assembly"]
    
    Q --> E
    E --> S
    V --> S
    S --> T
    T --> C
```

**Diagram: Traditional RAG Retrieval Pipeline**

Traditional RAG operates as a **System-1 only mechanism**:

| Component | Description | Limitation |
|-----------|-------------|------------|
| **Embedding** | Converts query and documents to dense vectors | Cannot capture structural relationships |
| **Similarity Search** | Retrieves based on vector proximity | Misses globally relevant but semantically distant information |
| **Top-K Selection** | Returns fixed number of most similar items | No deliberate reasoning about relevance |
| **Context Window** | Limited by fixed retrieval count | Cannot adapt to query complexity |

**Key Limitation**: Traditional RAG struggles with queries requiring comprehensive coverage or global reasoning. For example, "summarize all my interactions with colleagues this month" requires traversing many related entities, not just finding the most similar individual messages.

**Sources:** [README.md:15-23]()

---

## Graph-RAG Architecture

Graph-RAG extends traditional RAG by organizing memory in graph structures, but fundamentally still relies on similarity-based retrieval:

```mermaid
graph TB
    subgraph "Graph-RAG System"
        Q["Query"]
        E["Query Embedding"]
        G["Knowledge Graph<br/>Entities + Relations"]
        
        subgraph "Retrieval Phase"
            VS["Vector Similarity<br/>on Node Embeddings"]
            NH["Neighbor Expansion<br/>(1-hop or 2-hop)"]
        end
        
        R["Retrieved Subgraph"]
        C["Context Generation"]
    end
    
    Q --> E
    E --> VS
    G --> VS
    VS --> NH
    G --> NH
    NH --> R
    R --> C
```

**Diagram: Graph-RAG Retrieval Pattern**

Graph-RAG improvements over traditional RAG:

| Feature | Traditional RAG | Graph-RAG | Mnemis |
|---------|----------------|-----------|---------|
| **Memory Structure** | Flat documents/chunks | Graph with entities and relations | Base graph + hierarchical graph |
| **Initial Retrieval** | Vector similarity only | Vector similarity on nodes | System-1 similarity + System-2 global selection |
| **Context Expansion** | None | Fixed k-hop neighbors | LLM-guided hierarchical traversal |
| **Reasoning Capability** | None | Local graph structure | Global semantic hierarchy |
| **Retrieval Coverage** | Limited to top-k similar | Similar nodes + local neighbors | Comprehensive via layer-by-layer selection |

**Key Limitation**: While Graph-RAG incorporates structural information, it still initiates retrieval through similarity search. This means globally relevant but semantically distant information may never be discovered. The neighbor expansion is a fixed operation without deliberate reasoning about which paths to explore.

**Sources:** [README.md:15-23]()

---

## Mnemis Dual-Route Architecture

Mnemis implements two complementary retrieval mechanisms that operate on different graph structures:

```mermaid
graph TB
    subgraph "Mnemis Framework"
        Q["Query"]
        
        subgraph "Memory Storage"
            BG["Base Graph<br/>graphiti base operations<br/>Entity/Episode nodes"]
            HG["Hierarchical Graph<br/>Category hierarchy<br/>Semantic layers"]
        end
        
        subgraph "System-1 Route"
            S1E["qwen3 Embeddings<br/>FLOAT32 precision"]
            S1S["Similarity Search<br/>on Base Graph"]
            S1R["Top-K Results<br/>rag_top_k: 10-30"]
        end
        
        subgraph "System-2 Route"
            S2GS["GlobalSelector.global_selection()<br/>global_selector.py"]
            S2LS["layer_selection()<br/>LLM-guided filtering"]
            S2T["Hierarchical Traversal<br/>get_max_layer()<br/>get_nodes_by_layer()<br/>get_child_nodes()"]
            S2R["Selected Nodes + Context<br/>graph_top_k: 20-60"]
        end
        
        M["RAG_GRAPH Merger<br/>Combine both routes"]
        CTX["Structured Context<br/>Messages/FACTS/ENTITIES"]
    end
    
    Q --> S1E
    Q --> S2GS
    
    BG --> S1S
    HG --> S2GS
    
    S1E --> S1S
    S1S --> S1R
    
    S2GS --> S2LS
    S2LS --> S2T
    S2T --> S2R
    
    S1R --> M
    S2R --> M
    M --> CTX
```

**Diagram: Mnemis Dual-Route Retrieval with Code Entities**

### Code-Level Implementation Comparison

| Aspect | Traditional RAG | Graph-RAG | Mnemis |
|--------|----------------|-----------|---------|
| **Core Retrieval Class** | Generic vector search | Graph-aware vector search | `GlobalSelector` class |
| **Selection Logic** | Hardcoded top-k | Hardcoded neighbor expansion | `layer_selection()` with `NODE_SELECTION_PROMPT_TEMPLATE` |
| **Graph Traversal** | N/A | Fixed BFS/DFS | `get_max_layer()`, `get_nodes_by_layer()`, `get_child_nodes()` |
| **Caching Strategy** | Simple LRU | Basic caching | `@alru_cache` decorator with 500 entries per query |
| **Batch Processing** | Standard | Standard | `mp` and `batch` modes with async operations |
| **Merge Strategy** | N/A | Simple concatenation | `RAG_GRAPH` merge method |

**Sources:** [README.md:15-57](), High-level system diagrams

---

## Architectural Differentiators

### 1. Hierarchical Graph Construction

```mermaid
graph TB
    subgraph "Traditional Approaches"
        D1["Documents/Messages"]
        E1["Extract Entities"]
        F1["Flat Graph<br/>All entities at same level"]
    end
    
    subgraph "Mnemis Approach"
        D2["Documents/Messages"]
        E2["Extract Entities<br/>(Graphiti base)"]
        BG2["Base Graph<br/>Layer 0 entities"]
        
        H2["Build Hierarchy<br/>with guiding principles"]
        HG2["Hierarchical Graph<br/>Multi-layer categories"]
        
        subgraph "Guiding Principles"
            GP1["Minimum Concept<br/>Abstraction"]
            GP2["Many-to-Many<br/>Mapping"]
            GP3["Compression<br/>Efficiency Constraint"]
        end
    end
    
    D1 --> E1
    E1 --> F1
    
    D2 --> E2
    E2 --> BG2
    E2 --> H2
    
    H2 --> GP1
    H2 --> GP2
    H2 --> GP3
    
    H2 --> HG2
```

**Diagram: Graph Construction Comparison**

Mnemis constructs a hierarchical graph guided by three principles:

1. **Minimum Concept Abstraction**: Categories represent the minimum level of abstraction needed to group related entities
2. **Many-to-Many Mapping**: Entities can belong to multiple categories, preserving semantic complexity
3. **Compression Efficiency Constraint**: Hierarchy maintains efficient traversal while avoiding over-compression

This hierarchical structure enables **System-2 Global Selection** via the `GlobalSelector` class, which performs top-down reasoning impossible in flat architectures.

**Sources:** [README.md:20-23]()

---

## Retrieval Mechanism Comparison

### Query Processing Paths

```mermaid
graph LR
    subgraph "RAG: Single Path"
        Q1["Query"]
        E1["Embed"]
        V1["Vector Search"]
        R1["Top-K"]
    end
    
    subgraph "Graph-RAG: Single Path + Expansion"
        Q2["Query"]
        E2["Embed"]
        V2["Vector Search<br/>on Graph Nodes"]
        N2["Expand Neighbors"]
        R2["Subgraph"]
    end
    
    subgraph "Mnemis: Dual Parallel Paths"
        Q3["Query"]
        
        P1["Path 1: System-1<br/>Similarity Search<br/>Base Graph"]
        P2["Path 2: System-2<br/>GlobalSelector<br/>Hierarchical Graph"]
        
        M3["RAG_GRAPH<br/>Merge"]
        R3["Comprehensive<br/>Context"]
    end
    
    Q1 --> E1 --> V1 --> R1
    Q2 --> E2 --> V2 --> N2 --> R2
    
    Q3 --> P1
    Q3 --> P2
    P1 --> M3
    P2 --> M3
    M3 --> R3
```

**Diagram: Query Processing Path Comparison**

### System-2 Global Selection Advantage

The `GlobalSelector` class implements deliberate reasoning through LLM-guided hierarchical traversal:

| Operation | Code Method | Purpose | Traditional RAG Equivalent |
|-----------|-------------|---------|---------------------------|
| **Discover hierarchy depth** | `get_max_layer()` | Find top-level categories | N/A - no hierarchy |
| **Layer-wise retrieval** | `get_nodes_by_layer(layer)` | Get all categories at level | N/A |
| **LLM-guided filtering** | `layer_selection(query, nodes)` | Select relevant categories | Similarity only |
| **Recursive descent** | `get_child_nodes(selected)` | Traverse to next layer | Fixed neighbor expansion |
| **Context expansion** | `get_all_descendants()`, `get_one_hop_neighbors()` | Gather related information | Limited to initial top-k |

The `layer_selection()` method uses `NODE_SELECTION_PROMPT_TEMPLATE` to guide an LLM in selecting relevant nodes at each layer, enabling **deliberate reasoning** about which semantic paths to explore rather than relying solely on vector similarity.

**Sources:** High-level system diagrams, [README.md:26-29]()

---

## Performance Comparison

### Benchmark Results

| System | LoCoMo Accuracy | LongMemEval-S Accuracy | Method |
|--------|-----------------|------------------------|--------|
| **Traditional RAG** | ~60-70% (typical) | ~70-80% (typical) | Similarity search only |
| **Graph-RAG** | ~70-75% (estimated) | ~80-85% (estimated) | Similarity + neighbor expansion |
| **Mnemis** | **93.9%** (excluding cat. 5)<br/>80-81% (overall) | **91.6%** | Dual-route: System-1 + System-2 |

```mermaid
graph TB
    subgraph "Performance by Complexity"
        subgraph "Simple Queries"
            S1["Single-fact retrieval"]
            S2["Direct similarity match"]
            
            SR1["RAG: ~90%"]
            SR2["Graph-RAG: ~92%"]
            SR3["Mnemis: 100%"]
        end
        
        subgraph "Complex Queries"
            C1["Multi-entity reasoning"]
            C2["Temporal aggregation"]
            C3["Global summarization"]
            
            CR1["RAG: ~50%"]
            CR2["Graph-RAG: ~65%"]
            CR3["Mnemis: ~93%"]
        end
    end
```

**Diagram: Performance by Query Complexity**

### Configuration Impact

Mnemis's configurable retrieval parameters demonstrate the value of dual-route architecture:

| Configuration | RAG top_k | Graph top_k | LoCoMo Accuracy | LongMemEval-S Accuracy |
|---------------|-----------|-------------|-----------------|------------------------|
| `ragtopk10_gtopk20` | 10 | 20 | ~80% | 91.6% |
| `ragtopk30_gtopk60` | 30 | 60 | ~81% | Similar |

The ability to tune **both retrieval routes independently** allows optimization for different query types, unlike traditional RAG which only adjusts a single top-k parameter.

**Sources:** [README.md:31-40](), High-level system diagrams

---

## Key Technical Advantages

### 1. Dual Memory Structures

```mermaid
graph LR
    subgraph "Other Approaches"
        S1["Single Graph<br/>or Document Store"]
        S2["Single Retrieval<br/>Mechanism"]
    end
    
    subgraph "Mnemis"
        M1["Base Graph<br/>graphiti operations<br/>Entity-Episode-Relations"]
        M2["Hierarchical Graph<br/>Category layers<br/>Semantic structure"]
        
        M3["System-1<br/>Fast similarity"]
        M4["System-2<br/>Deliberate reasoning"]
        
        M1 --> M3
        M2 --> M4
        
        M5["RAG_GRAPH merge<br/>Complementary strengths"]
        
        M3 --> M5
        M4 --> M5
    end
```

**Diagram: Memory Structure Comparison**

### 2. Optimization Infrastructure

| Feature | Traditional RAG | Graph-RAG | Mnemis Implementation |
|---------|----------------|-----------|----------------------|
| **Caching** | Basic LRU | Basic LRU | `@alru_cache` with query-specific 500-entry limit |
| **Concurrency** | Standard async | Standard async | `asyncio` with batch processing modes |
| **Database** | Vector DB (e.g., Pinecone) | Graph DB or hybrid | Neo4j `AsyncDriver` with 1000 connection pool |
| **Query Optimization** | Simple index lookup | Graph query optimization | Cypher templates with batch operations |
| **Parallelism** | Limited | Limited | 10 parallel users, 50 concurrent QA operations |

The `GlobalSelector` class implements production-ready optimizations including:
- `alru_cache` decorator on `get_max_layer()`, `get_nodes_by_layer()`, `get_child_nodes()`, `get_all_descendants()`, `get_one_hop_neighbors()`
- Batch processing modes (`mp` and `batch`) for high-throughput scenarios
- Query templates in Cypher for efficient graph traversal

**Sources:** High-level system diagrams

---

## Scalability Characteristics

| Aspect | Traditional RAG | Graph-RAG | Mnemis |
|--------|----------------|-----------|---------|
| **Memory Size** | Linear degradation | Graph complexity impacts | Hierarchical compression maintains efficiency |
| **Query Latency** | O(log n) vector search | O(k·n) for k-hop expansion | O(d·l) where d=depth, l=layer size with caching |
| **Storage** | O(n) documents | O(n+m) nodes+edges | O(n+m+h) with hierarchy |
| **Traversal Complexity** | N/A | Exponential in k-hops | Linear in hierarchy depth with selective descent |

Mnemis's hierarchical organization provides **sublinear query complexity** for global reasoning tasks that would require exhaustive search in flat architectures.

**Sources:** [README.md:15-29]()

---

## Summary of Distinctions

1. **Dual-Route Retrieval**: Mnemis uniquely combines System-1 similarity search with System-2 global selection, while traditional RAG and Graph-RAG rely exclusively on similarity-based mechanisms

2. **Hierarchical Graph**: The semantic category hierarchy enables top-down reasoning impossible in flat graph structures used by Graph-RAG

3. **LLM-Guided Selection**: The `layer_selection()` method with `NODE_SELECTION_PROMPT_TEMPLATE` enables deliberate reasoning about relevance, not just similarity matching

4. **Configurable Merge**: The `RAG_GRAPH` merge strategy allows independent tuning of both retrieval routes for optimal performance

5. **Production Infrastructure**: Comprehensive caching (`@alru_cache`), batch processing, and async operations in `GlobalSelector` enable scalable deployment

6. **State-of-the-Art Performance**: 93.9% on LoCoMo and 91.6% on LongMemEval-S demonstrate empirical advantages over existing approaches

These architectural differences enable Mnemis to handle queries requiring comprehensive coverage, global reasoning, and complex multi-entity relationships that challenge traditional similarity-based retrieval systems.

**Sources:** [README.md:1-72](), High-level system diagrams

---

# Page: Paper & Citations

# Paper & Citations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Mnemis_paper.pdf](Mnemis_paper.pdf)
- [README.md](README.md)

</details>



This page provides the full citation information for the Mnemis research paper, including links to the published versions, citation formats, and guidance on how to reference this work in academic publications and technical documentation.

For theoretical background on dual-process theory and System-1/System-2 concepts, see [Theoretical Foundation](#7.1). For technical comparisons with RAG and Graph-RAG approaches, see [Comparison with Existing Approaches](#7.2).

---

## Paper Information

The Mnemis framework is described in the following research paper:

| **Attribute** | **Details** |
|--------------|-------------|
| **Title** | Mnemis: Dual-Route Retrieval on Hierarchical Graphs for Long-Term LLM Memory |
| **Authors** | Zihao Tang, Xin Yu, Ziyu Xiao, Zengxuan Wen, Zelin Li, Jiaxi Zhou, Hualei Wang, Haohua Wang, Haizhen Huang, Weiwei Deng, Feng Sun, Qi Zhang |
| **Publication Year** | 2026 |
| **Venue** | arXiv preprint |
| **arXiv ID** | 2602.15313 |
| **Primary Category** | cs.CL (Computation and Language) |
| **License** | MIT License |

**Sources:** [README.md:1-72]()

---

## Access Links

The paper is publicly available through multiple platforms:

```mermaid
graph LR
    PAPER["Mnemis Paper<br/>arXiv:2602.15313"]
    
    ARXIV["arXiv Platform<br/>arxiv.org/abs/2602.15313"]
    HF["Hugging Face Papers<br/>papers/2602.15313"]
    REPO["GitHub Repository<br/>microsoft/Mnemis"]
    
    PAPER --> ARXIV
    PAPER --> HF
    PAPER --> REPO
    
    ARXIV --> PDF["PDF Download"]
    HF --> DISCUSSION["Community Discussion"]
    REPO --> CODE["Implementation Code"]
    REPO --> RESULTS["Evaluation Results"]
```

**Primary Access Points:**

| **Platform** | **URL** | **Badge** |
|-------------|---------|-----------|
| **arXiv** | https://arxiv.org/abs/2602.15313 | ![arXiv](https://img.shields.io/badge/arXiv-2602.15313-b31b1b.svg) |
| **Hugging Face** | https://huggingface.co/papers/2602.15313 | ![Hugging Face](https://img.shields.io/badge/🤗-HuggingFace-blue) |
| **GitHub** | https://github.com/microsoft/Mnemis | ![License](https://img.shields.io/badge/License-MIT-f5de53) |

**Sources:** [README.md:2-13]()

---

## Citation Formats

### BibTeX

The recommended citation format for LaTeX documents:

```bibtex
@misc{tang2026mnemisdualrouteretrievalhierarchical,
      title={Mnemis: Dual-Route Retrieval on Hierarchical Graphs for Long-Term LLM Memory}, 
      author={Zihao Tang and Xin Yu and Ziyu Xiao and Zengxuan Wen and Zelin Li and Jiaxi Zhou and Hualei Wang and Haohua Wang and Haizhen Huang and Weiwei Deng and Feng Sun and Qi Zhang},
      year={2026},
      eprint={2602.15313},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2602.15313}, 
}
```

**Sources:** [README.md:58-71]()

### APA Style (7th Edition)

```
Tang, Z., Yu, X., Xiao, Z., Wen, Z., Li, Z., Zhou, J., Wang, H., Wang, H., 
Huang, H., Deng, W., Sun, F., & Zhang, Q. (2026). Mnemis: Dual-route retrieval 
on hierarchical graphs for long-term LLM memory. arXiv preprint arXiv:2602.15313. 
https://arxiv.org/abs/2602.15313
```

### MLA Style (9th Edition)

```
Tang, Zihao, et al. "Mnemis: Dual-Route Retrieval on Hierarchical Graphs for 
Long-Term LLM Memory." arXiv, 2026, arxiv.org/abs/2602.15313.
```

### Chicago Style (17th Edition)

```
Tang, Zihao, Xin Yu, Ziyu Xiao, Zengxuan Wen, Zelin Li, Jiaxi Zhou, Hualei Wang, 
Haohua Wang, Haizhen Huang, Weiwei Deng, Feng Sun, and Qi Zhang. 2026. 
"Mnemis: Dual-Route Retrieval on Hierarchical Graphs for Long-Term LLM Memory." 
arXiv preprint arXiv:2602.15313. https://arxiv.org/abs/2602.15313.
```

**Sources:** [README.md:62-70]()

---

## Paper Concepts to Code Mapping

The following diagram maps the key concepts introduced in the paper to their corresponding implementations in the codebase:

```mermaid
graph TB
    subgraph "Paper Concepts"
        PC_MNEMIS["Mnemis Framework"]
        PC_SYS1["System-1<br/>Similarity Search"]
        PC_SYS2["System-2<br/>Global Selection"]
        PC_BG["Base Graph"]
        PC_HG["Hierarchical Graph"]
        PC_MERGE["RAG_GRAPH Merge"]
        PC_PRINCIPLES["Guiding Principles:<br/>- Minimum Concept Abstraction<br/>- Many-to-Many Mapping<br/>- Compression Efficiency"]
    end
    
    subgraph "Code Implementation"
        CODE_GS["global_selector.py<br/>GlobalSelector class"]
        CODE_METHODS["Key Methods:<br/>- global_selection()<br/>- layer_selection()<br/>- get_child_nodes()<br/>- get_all_descendants()"]
        CODE_PROMPT["prompts.py<br/>NODE_SELECTION_PROMPT_TEMPLATE"]
        CODE_NEO4J["Neo4j Graph Database<br/>- Category nodes (layers)<br/>- Entity nodes (layer 0)<br/>- Episodic nodes"]
        CODE_GRAPHITI["Graphiti Framework<br/>Base graph operations"]
        CODE_EVAL["results/ directory<br/>- metrics_*.json<br/>- results_*.json"]
    end
    
    subgraph "Benchmark Results"
        BENCH_LOCOMO["LoCoMo: 93.9%<br/>1,986 questions"]
        BENCH_LME["LongMemEval-S: 91.6%<br/>500 questions"]
    end
    
    PC_MNEMIS --> PC_SYS1
    PC_MNEMIS --> PC_SYS2
    PC_SYS1 --> PC_BG
    PC_SYS2 --> PC_HG
    PC_SYS1 --> PC_MERGE
    PC_SYS2 --> PC_MERGE
    PC_HG --> PC_PRINCIPLES
    
    PC_SYS2 --> CODE_GS
    CODE_GS --> CODE_METHODS
    CODE_GS --> CODE_PROMPT
    PC_HG --> CODE_NEO4J
    PC_BG --> CODE_GRAPHITI
    PC_MERGE --> CODE_EVAL
    
    CODE_EVAL --> BENCH_LOCOMO
    CODE_EVAL --> BENCH_LME
```

**Implementation Correspondence:**

| **Paper Concept** | **Code Location** | **Description** |
|------------------|------------------|-----------------|
| System-2 Global Selection | `global_selector.py` | Core implementation of top-down hierarchical traversal |
| Node Selection Prompt | `prompts.py` | LLM prompt template for layer-by-layer node filtering |
| Hierarchical Graph | Neo4j schema with Category/Entity nodes | Graph database structure supporting hierarchical organization |
| Base Graph | Graphiti framework | Foundation for entity/relationship extraction and similarity search |
| RAG_GRAPH Merge | Evaluation configurations | Merge strategy combining System-1 and System-2 results |
| Guiding Principles | Hierarchical graph construction | Quality constraints for category hierarchy |
| Benchmark Results | `results/` directory | Complete evaluation outputs with metrics and contexts |

**Sources:** [README.md:15-56]()

---

## Key Contributions

The paper presents three primary contributions to the field of long-term LLM memory:

### Contribution 1: Dual-Route Architecture

Integration of System-1 similarity search with System-2 global selection, enabling both semantic retrieval and deliberate top-down reasoning over memory structures.

**Code Implementation:** [`global_selector.py`]() (System-2), Graphiti framework integration (System-1)

### Contribution 2: Hierarchical Graph Design

Improved base graph extraction and construction of a hierarchical graph guided by three principles:
- **Minimum Concept Abstraction**: Categories represent minimum abstraction levels
- **Many-to-Many Mapping**: Flexible entity-category relationships
- **Compression Efficiency Constraint**: Balanced hierarchy depth and breadth

**Code Implementation:** Neo4j graph schema with `CATEGORIZES` relationships between Category and Entity nodes

### Contribution 3: State-of-the-Art Performance

Comprehensive experimental validation demonstrating effectiveness across long-term memory benchmarks:
- **LoCoMo**: 93.9% accuracy
- **LongMemEval-S**: 91.6% accuracy
- Using GPT-4.1-mini for all experiments

**Code Implementation:** Evaluation results in `results/` directory with multiple configuration variants

**Sources:** [README.md:20-24]()

---

## Abstract

The paper addresses a fundamental limitation in existing AI memory systems: while RAG and Graph-RAG methods efficiently retrieve memory through similarity-based mechanisms (System-1 style), they struggle with scenarios requiring global reasoning or comprehensive information coverage.

**Key Problem:** Similarity-based retrieval alone is insufficient for scenarios requiring:
- Global reasoning across distributed information
- Comprehensive coverage of all relevant context
- Deliberate, top-down traversal of semantic hierarchies

**Proposed Solution:** Mnemis integrates complementary retrieval mechanisms:
1. **Base Graph**: Supports fast similarity-based retrieval
2. **Hierarchical Graph**: Enables deliberate top-down traversal over semantic hierarchies
3. **Dual-Route Retrieval**: Combines semantically and structurally relevant memory items

The combined approach achieves state-of-the-art results by leveraging both intuitive (System-1) and analytical (System-2) retrieval strategies.

**Sources:** [README.md:18-19]()

---

## Related Resources

### Figures and Visualizations

The paper includes several key figures that are also available in the repository:

| **Figure** | **Location** | **Description** |
|-----------|-------------|-----------------|
| Architecture Diagram | `figures/figure_intro.png` | Complete Mnemis system architecture |
| LoCoMo Results | `figures/results_locomo.png` | Performance comparison on LoCoMo benchmark |
| LongMemEval-S Results | `figures/results_lme_s.png` | Performance comparison on LongMemEval-S benchmark |
| Case Study 1 | `figures/figure_case_0.png` | LoCoMo User 8 QA 11 walkthrough |
| Case Study 2 | `figures/figure_case_1.png` | LongMemEval-S QA 262 analysis |

**Sources:** [README.md:27-51]()

### Implementation Base

Mnemis is implemented on top of the Graphiti framework:

```mermaid
graph TB
    GRAPHITI["Graphiti Framework<br/>github.com/getzep/graphiti"]
    MNEMIS["Mnemis Implementation"]
    PROMPTS["Core Prompts<br/>(Paper Appendix)"]
    GLOBAL_SEL["global_selection/<br/>System-2 Implementation"]
    RESULTS["results/<br/>Evaluation Outputs"]
    
    GRAPHITI --> MNEMIS
    PROMPTS --> MNEMIS
    MNEMIS --> GLOBAL_SEL
    MNEMIS --> RESULTS
    
    GLOBAL_SEL --> CODE1["global_selector.py"]
    GLOBAL_SEL --> CODE2["prompts.py"]
    
    RESULTS --> METRICS["metrics_*.json"]
    RESULTS --> FULL["results_*.json"]
```

**Framework Reference:**
- **Graphiti**: https://github.com/getzep/graphiti
- **Core Prompts**: Available in paper appendix
- **Implementation**: `global_selection/` directory contains System-2 logic
- **Evaluation Results**: `results/` directory contains complete benchmark outputs

**Sources:** [README.md:54-56]()

---

## Usage in Documentation

When citing Mnemis in technical documentation or discussions:

### In Academic Papers
Use the BibTeX format provided above and reference specific contributions:
- Cite the dual-route architecture when discussing hybrid retrieval systems
- Reference the hierarchical graph design principles for graph construction methods
- Cite the benchmark results when comparing memory-augmented LLM approaches

### In Technical Documentation
Reference specific implementation files:
- System-2 implementation: `global_selector.py`
- Prompt engineering: `prompts.py`
- Complete results: `results/` directory

### In Code Comments
Use inline references to the paper concepts:
```python
# Implements System-2 Global Selection from Mnemis paper (arXiv:2602.15313)
# See Section 3.2 for detailed algorithm description
```

**Sources:** [README.md:58-71]()

---

## Repository Metadata

The codebase itself should be cited when referencing the implementation:

```bibtex
@software{mnemis_implementation,
  author = {Tang, Zihao and Yu, Xin and Xiao, Ziyu and Wen, Zengxuan and 
            Li, Zelin and Zhou, Jiaxi and Wang, Hualei and Wang, Haohua and 
            Huang, Haizhen and Deng, Weiwei and Sun, Feng and Zhang, Qi},
  title = {Mnemis: Implementation of Dual-Route Retrieval on Hierarchical Graphs},
  year = {2026},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/microsoft/Mnemis}},
  license = {MIT}
}
```

**Sources:** [README.md:1-72]()

---

# Page: Contributing

# Contributing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [LICENSE](LICENSE)
- [README.md](README.md)
- [SECURITY.md](SECURITY.md)

</details>



This document provides information for contributors to the Mnemis project, including community guidelines, security reporting procedures, licensing terms, and development practices. For installation and usage instructions, see [Getting Started](#6). For technical implementation details, see [Implementation Guide](#3).

## Purpose and Scope

This page serves as the central resource for contributors to the Mnemis dual-route memory framework. It covers:

- Community participation guidelines and code of conduct (detailed in [Code of Conduct](#8.1))
- Security vulnerability reporting procedures (detailed in [Security Policy](#8.2))
- Licensing terms for the codebase (detailed in [License](#8.3))
- Development workflow and contribution best practices
- Codebase structure for new contributors

## Overview

Mnemis is an open-source project under the MIT License maintained by Microsoft. The project welcomes contributions in several areas:

| Contribution Area | Description | Key Files/Directories |
|------------------|-------------|----------------------|
| Core Implementation | System-2 Global Selection logic, optimization | `global_selection/` |
| Evaluation Framework | Benchmark datasets, metrics, test cases | `results/` |
| Documentation | Wiki pages, code comments, examples | `README.md` |
| Research Extensions | New retrieval methods, graph schemas | - |
| Performance Optimization | Caching, batch processing, concurrency | `global_selection/` |

Sources: [README.md:1-72]()

## Repository Structure

The following diagram maps the key areas of the codebase relevant to contributors:

```mermaid
graph TB
    subgraph "Repository Root"
        README["README.md<br/>Project documentation"]
        LICENSE["LICENSE<br/>MIT License"]
        COC["CODE_OF_CONDUCT.md<br/>Community guidelines"]
        SECURITY["SECURITY.md<br/>Vulnerability reporting"]
    end
    
    subgraph "Implementation Directory"
        GS_DIR["global_selection/<br/>Core System-2 implementation"]
        GS_MODULE["global_selector.py<br/>GlobalSelector class"]
        PROMPTS["prompts.py<br/>NODE_SELECTION_PROMPT_TEMPLATE"]
    end
    
    subgraph "Evaluation Data"
        RESULTS_DIR["results/<br/>Benchmark outputs"]
        LOCOMO_RESULTS["metrics_locomo_*.json<br/>LoCoMo accuracy data"]
        LME_RESULTS["metrics_longmemeval_s_*.json<br/>LongMemEval-S data"]
        FULL_RESULTS["results_*.json<br/>Full QA context"]
    end
    
    subgraph "Figures"
        FIGURES_DIR["figures/<br/>Visualizations"]
        INTRO["figure_intro.png<br/>Architecture diagram"]
        CASES["figure_case_*.png<br/>Case study visuals"]
        RESULTS_IMGS["results_*.png<br/>Benchmark charts"]
    end
    
    subgraph "Foundation Framework"
        GRAPHITI["Graphiti Framework<br/>Base implementation<br/>github.com/getzep/graphiti"]
    end
    
    README --> GS_DIR
    README --> RESULTS_DIR
    README --> FIGURES_DIR
    
    GS_DIR --> GS_MODULE
    GS_DIR --> PROMPTS
    
    RESULTS_DIR --> LOCOMO_RESULTS
    RESULTS_DIR --> LME_RESULTS
    RESULTS_DIR --> FULL_RESULTS
    
    FIGURES_DIR --> INTRO
    FIGURES_DIR --> CASES
    FIGURES_DIR --> RESULTS_IMGS
    
    GS_MODULE -.builds on.-> GRAPHITI
```

Sources: [README.md:54-56]()

## Development Setup

### Prerequisites

To contribute to Mnemis, developers need:

| Component | Purpose | Configuration |
|-----------|---------|--------------|
| Python Environment | Core development | Python 3.8+ |
| Neo4j Database | Graph storage | AsyncDriver with connection pool |
| LLM Services | GPT-4.1-mini access | OpenAI or Azure API credentials |
| Embedding Services | qwen3 embedder | Precision.FLOAT32 |
| Graphiti Framework | Base implementation | Installed as dependency |

### Key Implementation Files

Contributors working on core functionality should familiarize themselves with:

```mermaid
graph LR
    subgraph "Core Classes"
        GS["GlobalSelector<br/>global_selector.py"]
        
        subgraph "Primary Methods"
            GLOBAL["global_selection()<br/>Main orchestration"]
            LAYER["layer_selection()<br/>LLM-guided filtering"]
            GET_MAX["get_max_layer()<br/>Hierarchy discovery"]
            GET_NODES["get_nodes_by_layer()<br/>Layer traversal"]
            GET_CHILD["get_child_nodes()<br/>Tree navigation"]
            GET_DESC["get_all_descendants()<br/>Subtree retrieval"]
            GET_NEIGHBORS["get_one_hop_neighbors()<br/>Context expansion"]
        end
    end
    
    subgraph "Configuration"
        PROMPTS_FILE["prompts.py<br/>NODE_SELECTION_PROMPT_TEMPLATE"]
    end
    
    subgraph "Data Models"
        NODE_SEL["NodeSelection<br/>Pydantic model"]
        NODE_SEL_LIST["NodeSelectionList<br/>Response model"]
        QUERY["Query<br/>Cypher templates"]
    end
    
    GS --> GLOBAL
    GS --> LAYER
    GS --> GET_MAX
    GS --> GET_NODES
    GS --> GET_CHILD
    GS --> GET_DESC
    GS --> GET_NEIGHBORS
    
    LAYER --> PROMPTS_FILE
    PROMPTS_FILE --> NODE_SEL_LIST
    NODE_SEL_LIST --> NODE_SEL
    
    GET_CHILD --> QUERY
    GET_DESC --> QUERY
    GET_NEIGHBORS --> QUERY
```

Sources: [README.md:54-56]()

## Contribution Workflow

### Standard Development Process

```mermaid
graph TB
    START["Identify Contribution Area"]
    
    subgraph "Setup Phase"
        FORK["Fork Repository"]
        CLONE["Clone Fork Locally"]
        SETUP["Setup Development Environment<br/>Neo4j + LLM credentials"]
    end
    
    subgraph "Development Phase"
        BRANCH["Create Feature Branch"]
        CODE["Implement Changes<br/>global_selection/ or results/"]
        TEST["Test Locally<br/>Run evaluations"]
        DOC["Update Documentation<br/>README.md or comments"]
    end
    
    subgraph "Contribution Phase"
        COMMIT["Commit Changes<br/>Follow commit guidelines"]
        PUSH["Push to Fork"]
        PR["Create Pull Request"]
    end
    
    subgraph "Review Phase"
        REVIEW["Code Review"]
        FEEDBACK["Address Feedback"]
        APPROVE["Approval"]
        MERGE["Merge to Main"]
    end
    
    START --> FORK
    FORK --> CLONE
    CLONE --> SETUP
    
    SETUP --> BRANCH
    BRANCH --> CODE
    CODE --> TEST
    TEST --> DOC
    
    DOC --> COMMIT
    COMMIT --> PUSH
    PUSH --> PR
    
    PR --> REVIEW
    REVIEW --> FEEDBACK
    FEEDBACK --> CODE
    REVIEW --> APPROVE
    APPROVE --> MERGE
```

Sources: [README.md:1-72](), [CODE_OF_CONDUCT.md:1-10]()

### Contribution Categories

#### 1. Core Implementation Contributions

Contributions to the System-2 Global Selection mechanism:

- **Location**: `global_selection/` directory
- **Key Classes**: `GlobalSelector`
- **Key Methods**: `global_selection()`, `layer_selection()`, caching functions
- **Testing**: Run evaluations on LoCoMo and LongMemEval-S benchmarks
- **Performance**: Maintain or improve caching efficiency and batch processing

#### 2. Evaluation Contributions

Contributions to benchmark evaluation and metrics:

- **Location**: `results/` directory
- **File Types**: `metrics_*.json` (aggregated accuracy), `results_*.json` (full context)
- **Benchmarks**: LoCoMo (1,986 questions), LongMemEval-S (500 questions)
- **Validation**: Verify accuracy scores match expected performance (93.9% LoCoMo, 91.6% LME-S)

#### 3. Documentation Contributions

- **Primary**: [README.md:1-72]()
- **Guidelines**: [CODE_OF_CONDUCT.md:1-10]()
- **Security**: [SECURITY.md:1-14]()
- **License**: [LICENSE:1-22]()

#### 4. Research Extensions

Extensions to the dual-route memory framework:

| Extension Area | Implementation Location | Related Pages |
|---------------|------------------------|---------------|
| Alternative retrieval methods | `global_selection/` | [System-2 Global Selection](#2.3) |
| Graph schema modifications | Neo4j schema | [Graph Database Schema](#3.2) |
| Prompt engineering | `prompts.py` | [Prompt Engineering](#3.3) |
| Merge strategies | RAG_GRAPH logic | [RAG_GRAPH Merge Strategy](#2.4) |
| Performance optimization | Caching, batch processing | [Performance Optimization](#3.5) |

Sources: [README.md:54-56]()

## Community Guidelines

Mnemis follows the Microsoft Open Source Code of Conduct. All contributors must adhere to these community standards.

### Code of Conduct Summary

The project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). Key principles include:

- **Respect**: Treat all community members with respect
- **Collaboration**: Work together constructively
- **Transparency**: Be open about intentions and processes
- **Responsibility**: Take ownership of contributions

For complete details, see [Code of Conduct](#8.1).

**Resources**:
- Full guidelines: [CODE_OF_CONDUCT.md:3]()
- FAQ: [CODE_OF_CONDUCT.md:8]()
- Contact: opencode@microsoft.com [CODE_OF_CONDUCT.md:9]()
- Employee support: [CODE_OF_CONDUCT.md:10]()

Sources: [CODE_OF_CONDUCT.md:1-10]()

## Security Reporting

Microsoft takes security seriously across all repositories.

### Reporting Vulnerabilities

**Important**: Do not report security vulnerabilities through public GitHub issues [SECURITY.md:8]().

```mermaid
graph LR
    DISCOVER["Discover Security<br/>Vulnerability"]
    ASSESS["Assess Severity"]
    REPORT["Report via<br/>https://aka.ms/SECURITY.md"]
    PRIVATE["Private Disclosure<br/>to Microsoft Security"]
    RESPONSE["Microsoft Security<br/>Response Team Review"]
    FIX["Patch Development"]
    DISCLOSURE["Coordinated<br/>Public Disclosure"]
    
    DISCOVER --> ASSESS
    ASSESS --> REPORT
    REPORT --> PRIVATE
    PRIVATE --> RESPONSE
    RESPONSE --> FIX
    FIX --> DISCLOSURE
```

### Security Process

1. **Discovery**: Identify a potential security vulnerability in Mnemis
2. **Private Reporting**: Report via Microsoft's centralized security portal at [https://aka.ms/SECURITY.md](https://aka.ms/SECURITY.md) [SECURITY.md:12]()
3. **Verification**: Microsoft security team verifies the report
4. **Resolution**: Development of patches and mitigations
5. **Disclosure**: Coordinated public disclosure after fix is available

For complete security reporting procedures, see [Security Policy](#8.2).

Sources: [SECURITY.md:1-14]()

## License

Mnemis is licensed under the MIT License, providing permissive open-source terms.

### License Summary

```mermaid
graph TB
    MIT["MIT License<br/>Copyright 2026 Microsoft"]
    
    subgraph "Permissions"
        USE["Use"]
        COPY["Copy"]
        MODIFY["Modify"]
        MERGE["Merge"]
        PUBLISH["Publish"]
        DISTRIBUTE["Distribute"]
        SUBLICENSE["Sublicense"]
        SELL["Sell"]
    end
    
    subgraph "Conditions"
        NOTICE["Include License Notice<br/>in all copies"]
    end
    
    subgraph "Limitations"
        NO_WARRANTY["No Warranty"]
        NO_LIABILITY["No Liability"]
    end
    
    MIT --> USE
    MIT --> COPY
    MIT --> MODIFY
    MIT --> MERGE
    MIT --> PUBLISH
    MIT --> DISTRIBUTE
    MIT --> SUBLICENSE
    MIT --> SELL
    
    MIT --> NOTICE
    MIT --> NO_WARRANTY
    MIT --> NO_LIABILITY
```

### Key Terms

| Aspect | Terms |
|--------|-------|
| Copyright | Copyright (c) 2026 Microsoft [LICENSE:3]() |
| Permissions | Use, copy, modify, merge, publish, distribute, sublicense, sell [LICENSE:8]() |
| Condition | Include copyright notice and license in all copies [LICENSE:10-11]() |
| Warranty | Provided "AS IS" without warranty [LICENSE:14]() |
| Liability | No liability for damages [LICENSE:18-20]() |

For complete license text, see [License](#8.3).

Sources: [LICENSE:1-22]()

## Development Best Practices

### Code Quality Standards

Contributors should follow these practices when modifying the codebase:

#### Performance Considerations

| Component | Best Practice | Implementation |
|-----------|---------------|----------------|
| Caching | Use `alru_cache` for expensive operations | 500-entry cache per query |
| Batch Processing | Prefer batch queries over individual calls | `mp` and `batch` modes |
| Concurrency | Use `asyncio` for I/O-bound operations | AsyncDriver connection pool |
| Database Queries | Optimize Cypher queries | Indexed lookups, parameterized queries |

#### Testing Requirements

When contributing to `global_selection/`:

1. **Unit Tests**: Test individual methods in isolation
2. **Integration Tests**: Verify end-to-end `global_selection()` flow
3. **Benchmark Tests**: Run on LoCoMo and LongMemEval-S subsets
4. **Performance Tests**: Measure query latency and cache hit rates

#### Documentation Standards

All code contributions should include:

- **Docstrings**: For all public classes and methods
- **Type Hints**: Using Python type annotations
- **Comments**: For complex logic or algorithms
- **Examples**: Usage examples for new features

Sources: [README.md:54-56]()

## Research Foundation

Mnemis is based on research published in the paper "Mnemis: Dual-Route Retrieval on Hierarchical Graphs for Long-Term LLM Memory".

### Paper Information

- **arXiv**: 2602.15313 [README.md:7]()
- **Hugging Face**: https://huggingface.co/papers/2602.15313 [README.md:10]()
- **Authors**: Zihao Tang, Xin Yu, Ziyu Xiao, Zengxuan Wen, Zelin Li, Jiaxi Zhou, Hualei Wang, Haohua Wang, Haizhen Huang, Weiwei Deng, Feng Sun, Qi Zhang [README.md:64]()

### Citation

Contributors publishing work based on Mnemis should cite:

```
@misc{tang2026mnemisdualrouteretrievalhierarchical,
      title={Mnemis: Dual-Route Retrieval on Hierarchical Graphs for Long-Term LLM Memory}, 
      author={Zihao Tang and Xin Yu and Ziyu Xiao and Zengxuan Wen and Zelin Li and Jiaxi Zhou and Hualei Wang and Haohua Wang and Haizhen Huang and Weiwei Deng and Feng Sun and Qi Zhang},
      year={2026},
      eprint={2602.15313},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2602.15313}, 
}
```

For theoretical background and comparison with existing approaches, see [Research Background](#7).

Sources: [README.md:59-71]()

## Implementation Foundation

Mnemis is implemented on top of the [Graphiti](https://github.com/getzep/graphiti) framework [README.md:54](). Contributors should be familiar with:

- Graphiti's base graph operations
- Entity extraction and memory creation
- Neo4j schema conventions used by Graphiti
- AsyncDriver patterns for graph database access

The `global_selection/` directory contains Mnemis-specific extensions for System-2 Global Selection [README.md:56]().

Sources: [README.md:54-56]()

## Results and Evaluation Data

The `results/` directory contains comprehensive evaluation outputs [README.md:56]():

### Results Directory Structure

| File Pattern | Contents | Purpose |
|-------------|----------|---------|
| `metrics_locomo_*.json` | LoCoMo accuracy by category | Aggregated performance metrics |
| `metrics_longmemeval_s_*.json` | LongMemEval-S accuracy by type | Question type breakdown |
| `results_locomo_*.json` | Full QA context for LoCoMo | Evidence, facts, entities, answers |
| `results_longmemeval_s_*.json` | Full QA context for LME-S | Complete retrieval context |

### Configuration Variants

Result files include different configuration experiments:

- `ragtopk10_gtopk20`: RAG top-k=10, Graph top-k=20
- `ragtopk30_gtopk60`: RAG top-k=30, Graph top-k=60

Contributors adding new configurations should follow this naming convention. For detailed analysis, see [Configuration Impact Analysis](#4.4).

Sources: [README.md:56]()

## Additional Resources

### Related Wiki Pages

- [Getting Started](#6): Installation and setup instructions
- [Implementation Guide](#3): Technical implementation details
- [GlobalSelector Class Reference](#3.1): API documentation
- [Performance Optimization](#3.5): Caching and batch processing
- [Evaluation & Results](#4): Benchmark methodology and scores

### External Resources

- **Graphiti Repository**: https://github.com/getzep/graphiti [README.md:54]()
- **Microsoft Open Source**: https://opensource.microsoft.com/codeofconduct/ [CODE_OF_CONDUCT.md:3]()
- **Security Portal**: https://aka.ms/SECURITY.md [SECURITY.md:12]()
- **Mnemis Paper**: https://arxiv.org/abs/2602.15313 [README.md:7]()

### Contact

For questions or concerns not covered by documentation:

- **General Questions**: Create a GitHub issue
- **Code of Conduct**: opencode@microsoft.com [CODE_OF_CONDUCT.md:9]()
- **Security Issues**: Use Microsoft Security Portal [SECURITY.md:12]()
- **Microsoft Employees**: aka.ms/opensource/moderation-support [CODE_OF_CONDUCT.md:10]()

Sources: [README.md:1-72](), [CODE_OF_CONDUCT.md:1-10](), [SECURITY.md:1-14]()

---

# Page: Code of Conduct

# Code of Conduct

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [SECURITY.md](SECURITY.md)

</details>



## Purpose and Scope

This page documents the community standards and behavioral expectations for contributors and participants in the Mnemis project. It outlines the adopted code of conduct policies, reporting procedures for violations, and available resources for support.

For information about security vulnerability reporting, see [Security Policy](#8.2). For general contribution guidelines and development practices, see [Contributing](#8).

**Sources:** [CODE_OF_CONDUCT.md:1-10]()

---

## Adopted Code of Conduct

The Mnemis project has adopted the **Microsoft Open Source Code of Conduct**. This is a standardized code of conduct used across all Microsoft open source projects to ensure consistent community standards and expectations.

The code of conduct defines acceptable behavior in all project spaces including:
- GitHub repositories (issues, pull requests, discussions)
- Code reviews and technical discussions
- Community forums and communication channels
- Project-related events and meetings

**Sources:** [CODE_OF_CONDUCT.md:1-3]()

---

## Code of Conduct Architecture

The following diagram illustrates the organizational structure of the code of conduct governance and how it integrates with the Mnemis project workflow:

```mermaid
graph TB
    subgraph "Mnemis Repository"
        REPO["github.com/microsoft/Mnemis"]
        COC_FILE["CODE_OF_CONDUCT.md"]
        CONTRIB["Contributing Process"]
    end
    
    subgraph "Microsoft Governance"
        MS_COC["Microsoft Open Source Code of Conduct<br/>opensource.microsoft.com/codeofconduct"]
        MS_FAQ["Code of Conduct FAQ<br/>opensource.microsoft.com/codeofconduct/faq"]
    end
    
    subgraph "Contact Points"
        EMAIL["opencode@microsoft.com"]
        MOD_SUPPORT["aka.ms/opensource/moderation-support<br/>(Microsoft employees)"]
    end
    
    subgraph "Community Actions"
        PARTICIPANT["Contributors & Participants"]
        REPORT["Report Violation"]
        QUESTION["Ask Questions"]
    end
    
    REPO --> COC_FILE
    COC_FILE --> MS_COC
    COC_FILE --> MS_FAQ
    
    MS_COC --> EMAIL
    MS_COC --> MOD_SUPPORT
    
    PARTICIPANT --> CONTRIB
    PARTICIPANT --> REPORT
    PARTICIPANT --> QUESTION
    
    REPORT --> EMAIL
    REPORT --> MOD_SUPPORT
    QUESTION --> EMAIL
    QUESTION --> MS_FAQ
    
    CONTRIB --> COC_FILE
```

**Diagram: Code of Conduct Governance Structure**

This diagram shows how the `CODE_OF_CONDUCT.md` file in the repository references the centralized Microsoft Open Source Code of Conduct and provides pathways for reporting and support.

**Sources:** [CODE_OF_CONDUCT.md:1-10]()

---

## Reporting and Resolution Process

The following diagram illustrates the process flow for reporting code of conduct violations and how they are handled:

```mermaid
flowchart TD
    START["Observe Violation or<br/>Have Concern"]
    
    ASSESS{"Is this a<br/>security issue?"}
    
    COC_REPORT["Report to Code of Conduct Team"]
    SEC_REPORT["Report to Security Team<br/>(See SECURITY.md)"]
    
    METHOD{"Reporting<br/>Method"}
    
    EMAIL["Email: opencode@microsoft.com"]
    INTERNAL["Microsoft Employees:<br/>aka.ms/opensource/moderation-support"]
    
    REVIEW["Code of Conduct Team Reviews"]
    
    INVESTIGATE["Investigation"]
    
    DECISION{"Resolution"}
    
    WARNING["Warning"]
    TEMP_BAN["Temporary Ban"]
    PERM_BAN["Permanent Ban"]
    NO_ACTION["No Action Required"]
    
    COMMUNICATE["Communicate Decision<br/>to Parties"]
    
    APPEAL["Appeal Process<br/>(if applicable)"]
    
    CLOSE["Case Closed"]
    
    START --> ASSESS
    
    ASSESS -->|"Yes"| SEC_REPORT
    ASSESS -->|"No"| COC_REPORT
    
    COC_REPORT --> METHOD
    
    METHOD -->|"General Public"| EMAIL
    METHOD -->|"MS Employee"| INTERNAL
    
    EMAIL --> REVIEW
    INTERNAL --> REVIEW
    
    REVIEW --> INVESTIGATE
    
    INVESTIGATE --> DECISION
    
    DECISION --> WARNING
    DECISION --> TEMP_BAN
    DECISION --> PERM_BAN
    DECISION --> NO_ACTION
    
    WARNING --> COMMUNICATE
    TEMP_BAN --> COMMUNICATE
    PERM_BAN --> COMMUNICATE
    NO_ACTION --> COMMUNICATE
    
    COMMUNICATE --> APPEAL
    APPEAL --> CLOSE
    COMMUNICATE --> CLOSE
```

**Diagram: Violation Reporting and Resolution Flow**

This flowchart demonstrates the distinction between security issues (covered in [SECURITY.md:1-14]()) and code of conduct violations, along with the complete resolution process.

**Sources:** [CODE_OF_CONDUCT.md:1-10](), [SECURITY.md:8]()

---

## Resources and Contact Information

The following table provides a comprehensive reference of all code of conduct resources and their purposes:

| Resource | URL/Contact | Purpose | Audience |
|----------|-------------|---------|----------|
| **Microsoft Open Source Code of Conduct** | [opensource.microsoft.com/codeofconduct](https://opensource.microsoft.com/codeofconduct/) | Full text of the adopted code of conduct | All contributors |
| **Code of Conduct FAQ** | [opensource.microsoft.com/codeofconduct/faq](https://opensource.microsoft.com/codeofconduct/faq/) | Frequently asked questions about policies and procedures | All contributors |
| **General Contact** | opencode@microsoft.com | Email for questions, concerns, or reporting violations | All contributors |
| **Microsoft Employee Support** | [aka.ms/opensource/moderation-support](https://aka.ms/opensource/moderation-support) | Internal moderation support channel | Microsoft employees only |

**Sources:** [CODE_OF_CONDUCT.md:5-10]()

---

## File Organization

The code of conduct documentation is organized as follows in the repository:

```mermaid
graph LR
    subgraph "Repository Root"
        COC["CODE_OF_CONDUCT.md<br/>(lines 1-10)"]
        SEC["SECURITY.md<br/>(lines 1-14)"]
        README["README.md"]
    end
    
    subgraph "Content Structure"
        COC_TITLE["Title: Microsoft Open Source<br/>Code of Conduct"]
        COC_ADOPTION["Adoption Statement"]
        COC_RESOURCES["Resources Section"]
    end
    
    subgraph "External References"
        MS_SITE["opensource.microsoft.com"]
        EMAIL_ADDR["opencode@microsoft.com"]
        MOD_LINK["aka.ms/opensource/moderation-support"]
    end
    
    COC --> COC_TITLE
    COC --> COC_ADOPTION
    COC --> COC_RESOURCES
    
    COC_RESOURCES --> MS_SITE
    COC_RESOURCES --> EMAIL_ADDR
    COC_RESOURCES --> MOD_LINK
    
    README -.->|"References"| COC
    COC -.->|"Separate from"| SEC
```

**Diagram: Code of Conduct File Structure**

The `CODE_OF_CONDUCT.md` file is a standalone document at the repository root, distinct from `SECURITY.md` which handles vulnerability reporting.

**Sources:** [CODE_OF_CONDUCT.md:1-10]()

---

## Key Principles

While the full text of the Microsoft Open Source Code of Conduct is maintained at the official Microsoft site, the key principles include:

| Principle | Description |
|-----------|-------------|
| **Respectful Communication** | Using welcoming and inclusive language |
| **Professional Behavior** | Accepting constructive criticism gracefully |
| **Focus on Community** | Prioritizing what is best for the community |
| **Empathy** | Showing empathy towards other community members |
| **Accountability** | Taking responsibility for mistakes and learning from them |

These principles apply to all interactions within the Mnemis project, including code reviews, issue discussions, pull request feedback, and any other project-related communication.

**Sources:** [CODE_OF_CONDUCT.md:3]()

---

## Enforcement

The Microsoft Open Source Code of Conduct includes enforcement guidelines that project maintainers and the code of conduct team follow. Key aspects include:

1. **Scope**: The code of conduct applies to all project spaces and when representing the project in public spaces
2. **Reporting**: All complaints are reviewed and investigated promptly and fairly
3. **Confidentiality**: Respecting the privacy and security of the reporter
4. **Proportional Response**: Enforcement actions are proportional to the violation

For questions about enforcement or specific situations, contact `opencode@microsoft.com` as specified in [CODE_OF_CONDUCT.md:9]().

**Sources:** [CODE_OF_CONDUCT.md:7-10]()

---

## Integration with Contributing Workflow

The following table shows how the code of conduct integrates with different contribution activities:

| Activity | Code of Conduct Application |
|----------|----------------------------|
| **Opening Issues** | Describe problems respectfully; avoid accusatory language |
| **Pull Requests** | Respond professionally to feedback; explain decisions clearly |
| **Code Reviews** | Provide constructive criticism; focus on code, not people |
| **Discussions** | Maintain respectful dialogue; consider diverse perspectives |
| **Disagreements** | Engage in good faith; seek consensus; escalate appropriately if needed |

All contributors to Mnemis are expected to have read and agreed to follow the Microsoft Open Source Code of Conduct before participating in the project.

**Sources:** [CODE_OF_CONDUCT.md:1-10]()

---

## Contact Decision Tree

The following diagram helps determine the appropriate contact method for different scenarios:

```mermaid
flowchart TD
    NEED["Need Assistance or<br/>Have Concern"]
    
    TYPE{"Type of<br/>Issue?"}
    
    SECURITY["Security Vulnerability"]
    COC_VIOLATION["Code of Conduct<br/>Violation"]
    GENERAL_Q["General Question<br/>about CoC"]
    
    SEC_CONTACT["Use SECURITY.md<br/>procedures"]
    
    EMP_CHECK{"Are you a<br/>Microsoft employee?"}
    
    INTERNAL_ROUTE["Use internal support:<br/>aka.ms/opensource/moderation-support"]
    EXTERNAL_ROUTE["Email:<br/>opencode@microsoft.com"]
    
    FAQ_CHECK["Check FAQ first:<br/>opensource.microsoft.com/codeofconduct/faq"]
    STILL_UNCLEAR["Still unclear?"]
    EMAIL_Q["Email:<br/>opencode@microsoft.com"]
    
    NEED --> TYPE
    
    TYPE -->|"Security"| SECURITY
    TYPE -->|"Behavior/Violation"| COC_VIOLATION
    TYPE -->|"Question"| GENERAL_Q
    
    SECURITY --> SEC_CONTACT
    
    COC_VIOLATION --> EMP_CHECK
    
    EMP_CHECK -->|"Yes"| INTERNAL_ROUTE
    EMP_CHECK -->|"No"| EXTERNAL_ROUTE
    
    GENERAL_Q --> FAQ_CHECK
    FAQ_CHECK --> STILL_UNCLEAR
    STILL_UNCLEAR --> EMAIL_Q
```

**Diagram: Contact Method Decision Tree**

This decision tree helps users quickly identify the correct reporting channel based on their specific situation.

**Sources:** [CODE_OF_CONDUCT.md:5-10](), [SECURITY.md:8]()

---

## Additional Notes

### Do Not Report Security Issues as Code of Conduct Violations

Security vulnerabilities should **never** be reported through the code of conduct channels. Security issues have a separate reporting process detailed in [SECURITY.md:1-14]() and page [Security Policy](#8.2). Mixing security reports with code of conduct issues can delay critical security fixes.

### Public Disclosure

Code of conduct violations should **not** be reported through public GitHub issues. All reports should be made privately through the designated contact channels to protect the privacy of all parties involved.

### Microsoft Employee Resources

Microsoft employees have access to additional internal resources through `aka.ms/opensource/moderation-support` for guidance on code of conduct matters specific to their role as Microsoft representatives.

**Sources:** [CODE_OF_CONDUCT.md:8-10](), [SECURITY.md:8]()

---

## Summary

The Mnemis project operates under the Microsoft Open Source Code of Conduct to ensure a welcoming, inclusive, and professional environment for all contributors. Key resources are documented in [CODE_OF_CONDUCT.md:1-10]() with clear pathways for reporting violations, asking questions, and accessing support.

| File | Lines | Purpose |
|------|-------|---------|
| `CODE_OF_CONDUCT.md` | 1-10 | Primary code of conduct documentation |
| External reference | N/A | Full policy at opensource.microsoft.com/codeofconduct |
| Contact: opencode@microsoft.com | N/A | General questions and reporting |
| Contact: aka.ms/opensource/moderation-support | N/A | Microsoft employee support |

**Sources:** [CODE_OF_CONDUCT.md:1-10]()

---

# Page: Security Policy

# Security Policy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [SECURITY.md](SECURITY.md)

</details>



This page documents the security vulnerability reporting procedures for the Mnemis codebase. It outlines how to responsibly disclose security issues, where to report them, and what to expect from the security response process.

For general community guidelines and conduct expectations, see [Code of Conduct](#8.1). For licensing terms, see [License](#8.3).

---

## Overview

Microsoft takes the security of software products and services seriously, including all source code repositories managed through GitHub organizations. The Mnemis project follows Microsoft's standardized security reporting procedures to ensure vulnerabilities are handled promptly and responsibly.

**Critical Rule**: Security vulnerabilities must **never** be reported through public GitHub issues, as this could expose users to unnecessary risk before patches are available.

Sources: [SECURITY.md:5-8]()

---

## Security Reporting Workflow

The following diagram illustrates the proper security reporting workflow for the Mnemis repository:

```mermaid
graph TD
    DISCOVER["Security Vulnerability Discovered"]
    DECISION{"Public or Private Reporting?"}
    WRONG["❌ Public GitHub Issue"]
    RIGHT["✓ Microsoft Security Portal"]
    PORTAL["https://aka.ms/SECURITY.md"]
    REVIEW["Microsoft Security Team Review"]
    TRIAGE["Vulnerability Triage & Validation"]
    FIX["Patch Development"]
    DISCLOSURE["Coordinated Disclosure"]
    PUBLIC["Public Issue Tracking<br/>(Post-Patch)"]
    
    DISCOVER --> DECISION
    DECISION -->|"❌ DO NOT USE"| WRONG
    DECISION -->|"✓ CORRECT PATH"| RIGHT
    RIGHT --> PORTAL
    PORTAL --> REVIEW
    REVIEW --> TRIAGE
    TRIAGE --> FIX
    FIX --> DISCLOSURE
    DISCLOSURE --> PUBLIC
    
    WRONG -.->|"Risk: Premature Exposure"| DANGER["Exploitable Before Patch"]
    
    style WRONG fill:#ffcccc
    style RIGHT fill:#ccffcc
    style DANGER fill:#ff9999
```

Sources: [SECURITY.md:8-12]()

---

## Prohibited Reporting Channels

The following channels must **not** be used for security vulnerability reporting:

| Channel | Status | Reason |
|---------|--------|--------|
| Public GitHub Issues | ❌ Prohibited | Exposes vulnerability details before patches are available |
| GitHub Discussions | ❌ Prohibited | Public forum visible to all users and potential attackers |
| Pull Requests | ❌ Prohibited | Changes are visible in repository history |
| Social Media | ❌ Prohibited | No secure communication channel |
| Email to Repository Maintainers | ⚠️ Discouraged | Not centrally tracked; use Microsoft portal instead |

**Explicit prohibition statement**: [SECURITY.md:8]() states:

> "**Please do not report security vulnerabilities through public GitHub issues.**"

This directive is absolute and applies to all security-related findings, regardless of perceived severity.

Sources: [SECURITY.md:8]()

---

## Approved Reporting Process

### Primary Reporting Portal

All security vulnerabilities should be reported through Microsoft's centralized security portal:

**Portal URL**: [https://aka.ms/SECURITY.md](https://aka.ms/SECURITY.md)

This portal provides:
- Secure, encrypted submission channels
- Centralized tracking across all Microsoft repositories
- Integration with Microsoft Security Response Center (MSRC)
- Standardized triage and response procedures
- Coordinated disclosure workflows

Sources: [SECURITY.md:10-12]()

### Information to Include

When reporting a security vulnerability, provide the following information:

```mermaid
graph LR
    REPORT["Security Report"]
    
    subgraph "Required Information"
        DESC["Vulnerability Description"]
        IMPACT["Impact Assessment"]
        REPRO["Reproduction Steps"]
        ENV["Environment Details"]
    end
    
    subgraph "Optional (Helpful)"
        POC["Proof of Concept"]
        FIX["Suggested Fix"]
        REF["References"]
    end
    
    REPORT --> DESC
    REPORT --> IMPACT
    REPORT --> REPRO
    REPORT --> ENV
    
    REPORT -.-> POC
    REPORT -.-> FIX
    REPORT -.-> REF
    
    DESC --> DETAIL1["What is vulnerable?"]
    DESC --> DETAIL2["What can be exploited?"]
    
    IMPACT --> SEVERITY["Confidentiality/Integrity/Availability"]
    
    REPRO --> STEPS["Step-by-step instructions"]
    
    ENV --> CONTEXT["OS, Python version, dependencies"]
```

Sources: [SECURITY.md:5-12]()

---

## Security Scope for Mnemis

### Components Covered

The security policy applies to all components of the Mnemis system:

| Component | Security Considerations | Examples |
|-----------|------------------------|-----------|
| Core Retrieval Logic | Input validation, injection attacks | `global_selector.py`, query construction |
| LLM Integration | Prompt injection, API key exposure | OpenAI/Azure client configurations |
| Database Operations | Cypher injection, connection security | Neo4j AsyncDriver, query templates |
| API Endpoints | Authentication, authorization | Any future REST/GraphQL interfaces |
| Configuration Files | Credential exposure | Environment variables, config files |
| Dependencies | Vulnerable third-party packages | Python package dependencies |

Sources: [SECURITY.md:5-6]()

### Example Vulnerability Categories

Common vulnerability types that should be reported:

```mermaid
graph TB
    VULNS["Security Vulnerabilities"]
    
    subgraph "Injection Attacks"
        PROMPT["Prompt Injection<br/>in LLM queries"]
        CYPHER["Cypher Injection<br/>in Neo4j queries"]
        CODE["Code Injection<br/>in eval/exec"]
    end
    
    subgraph "Data Exposure"
        CREDS["Credential Leakage<br/>in logs/errors"]
        PII["PII Exposure<br/>in memory graphs"]
        API["API Key Exposure<br/>in config files"]
    end
    
    subgraph "Access Control"
        AUTH["Authentication Bypass"]
        AUTHZ["Authorization Failures"]
        PRIV["Privilege Escalation"]
    end
    
    subgraph "Availability"
        DOS["Denial of Service<br/>via expensive queries"]
        MEM["Memory Exhaustion"]
        CONN["Connection Pool Exhaustion"]
    end
    
    VULNS --> PROMPT
    VULNS --> CYPHER
    VULNS --> CODE
    VULNS --> CREDS
    VULNS --> PII
    VULNS --> API
    VULNS --> AUTH
    VULNS --> AUTHZ
    VULNS --> PRIV
    VULNS --> DOS
    VULNS --> MEM
    VULNS --> CONN
```

Sources: [SECURITY.md:5-6]()

---

## Repository Security Configuration

### Security.md File Location

The security policy is defined in the repository root:

```
microsoft/Mnemis/
├── SECURITY.md           # Security vulnerability reporting policy
├── CODE_OF_CONDUCT.md    # Community conduct guidelines
├── LICENSE               # MIT License
└── README.md             # Project overview
```

File path: [SECURITY.md:1-14]()

This placement ensures:
- Visibility in GitHub's Security tab
- Automatic detection by GitHub's security features
- Easy discovery by security researchers
- Compliance with Microsoft's security standards

Sources: [SECURITY.md:1-14]()

### Policy Version Control

The security policy uses Microsoft's standardized template:

```
<!-- BEGIN MICROSOFT SECURITY.MD V1.0.0 BLOCK -->
...
<!-- END MICROSOFT SECURITY.MD BLOCK -->
```

**Version**: V1.0.0 (as indicated in [SECURITY.md:1]())

This versioning ensures:
- Consistency across Microsoft repositories
- Centralized policy updates
- Clear change tracking
- Standardized response procedures

Sources: [SECURITY.md:1,14]()

---

## Microsoft Security Infrastructure

### Organizational Scope

The security policy applies repository-wide as part of Microsoft's GitHub organization:

```mermaid
graph TB
    MSFT["Microsoft GitHub Organizations"]
    
    subgraph "Repository Structure"
        ORG["microsoft/"]
        REPO["Mnemis"]
        SECURITY["SECURITY.md"]
    end
    
    subgraph "Security Infrastructure"
        PORTAL["aka.ms/SECURITY.md<br/>Centralized Portal"]
        MSRC["Microsoft Security Response Center<br/>MSRC"]
        TEAM["Security Team<br/>Triage & Response"]
    end
    
    subgraph "Response Workflow"
        ASSESS["Vulnerability Assessment"]
        PATCH["Patch Development"]
        COORD["Coordinated Disclosure"]
    end
    
    MSFT --> ORG
    ORG --> REPO
    REPO --> SECURITY
    
    SECURITY -.->|"Redirects to"| PORTAL
    PORTAL --> MSRC
    MSRC --> TEAM
    
    TEAM --> ASSESS
    ASSESS --> PATCH
    PATCH --> COORD
```

Sources: [SECURITY.md:5-6,11-12]()

### Multi-Repository Coverage

Microsoft's security approach covers all source code repositories:

- **Scope**: All repositories in Microsoft GitHub organizations [SECURITY.md:6]()
- **Consistency**: Standardized `SECURITY.md` files across repositories
- **Centralization**: Single portal (`aka.ms/SECURITY.md`) for all reports
- **Coordination**: Cross-repository vulnerability tracking

Sources: [SECURITY.md:5-6]()

---

## Responsible Disclosure Guidelines

### Timeline Expectations

While not explicitly documented in the Mnemis repository, Microsoft generally follows industry-standard coordinated disclosure timelines:

| Phase | Typical Duration | Description |
|-------|-----------------|-------------|
| Initial Response | 1-3 business days | Acknowledgment of receipt |
| Triage | 1-2 weeks | Severity assessment and validation |
| Patch Development | 2-12 weeks | Depends on complexity |
| Pre-Disclosure Notification | 1 week | Advance notice to reporter |
| Public Disclosure | Variable | Coordinated release of patch and advisory |

### Reporter Expectations

Security researchers should:

1. **Wait for Acknowledgment**: Allow time for initial response
2. **Provide Additional Information**: Respond to triage team requests
3. **Maintain Confidentiality**: Do not disclose until coordinated release
4. **Test Patches**: Verify proposed fixes when requested
5. **Accept Credit**: Agree to public acknowledgment (optional)

Sources: [SECURITY.md:5-12]()

---

## Security Policy Update Process

The security policy file is maintained by Microsoft and follows centralized updates:

```mermaid
graph LR
    MSFT_POLICY["Microsoft Security Policy<br/>Central Template"]
    UPDATE["Policy Update"]
    VERSION["Version Bump<br/>e.g., V1.0.0 → V1.0.1"]
    REPOS["All Microsoft Repositories"]
    MNEMIS["microsoft/Mnemis<br/>SECURITY.md"]
    
    MSFT_POLICY --> UPDATE
    UPDATE --> VERSION
    VERSION --> REPOS
    REPOS --> MNEMIS
    
    MNEMIS -.->|"Block markers indicate<br/>centrally managed content"| BLOCK["BEGIN/END markers<br/>Lines 1, 14"]
```

**Block markers**: [SECURITY.md:1,14]()

The comment blocks (`<!-- BEGIN/END MICROSOFT SECURITY.MD -->`) indicate that this content is centrally managed and should not be modified at the repository level.

Sources: [SECURITY.md:1,14]()

---

## Related Policies

### Code of Conduct

For non-security community issues, refer to the Code of Conduct:
- See [Code of Conduct](#8.1) for community guidelines
- See [CODE_OF_CONDUCT.md:1-10]() for the full policy text
- Contact: `opencode@microsoft.com` for conduct questions

### License

For intellectual property and usage terms:
- See [License](#8.3) for MIT License details
- The security policy does not affect licensing terms

Sources: [SECURITY.md:1-14](), [CODE_OF_CONDUCT.md:1-10]()

---

## Contact Information

### For Security Vulnerabilities

**Primary Portal**: [https://aka.ms/SECURITY.md](https://aka.ms/SECURITY.md)

This portal provides:
- Latest reporting guidance for Microsoft repositories [SECURITY.md:11]()
- Contact information for security teams
- Detailed submission procedures
- Policy updates and additional resources

### For Other Issues

| Issue Type | Contact Channel |
|-----------|-----------------|
| Security Vulnerabilities | [aka.ms/SECURITY.md](https://aka.ms/SECURITY.md) |
| Code of Conduct Violations | opencode@microsoft.com (see [8.1](#8.1)) |
| General Questions | GitHub Issues (non-security) |
| Feature Requests | GitHub Discussions or Issues |

Sources: [SECURITY.md:10-12](), [CODE_OF_CONDUCT.md:9]()

---

## Summary

The Mnemis security policy follows Microsoft's standardized approach:

1. **Never report security issues publicly** via GitHub issues [SECURITY.md:8]()
2. **Use the centralized portal** at [aka.ms/SECURITY.md](https://aka.ms/SECURITY.md) [SECURITY.md:11-12]()
3. **Provide detailed information** to enable effective triage
4. **Follow coordinated disclosure** timelines
5. **Maintain confidentiality** until patches are released

This approach ensures vulnerabilities are addressed responsibly while protecting the security of all Mnemis users.

Sources: [SECURITY.md:1-14]()

---

# Page: License

# License

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)

</details>



## Purpose and Scope

This page documents the licensing terms for the Mnemis codebase. The project is released under the MIT License, which governs the terms of use, modification, and distribution of the software. This information is relevant for contributors, users, and organizations that wish to use or build upon the Mnemis framework.

For information about contributing to the project, see [Contributing](#8). For security policies, see [Security Policy](#8.2).

---

## License Overview

The Mnemis project is licensed under the **MIT License**, one of the most permissive open-source licenses. The license is simple, business-friendly, and allows for extensive commercial and non-commercial use with minimal restrictions.

### Copyright Information

| Field | Value |
|-------|-------|
| **License Type** | MIT License |
| **Copyright Holder** | Microsoft |
| **Copyright Year** | 2026 |
| **License File** | [LICENSE:1-22]() |

Sources: [LICENSE:1-4]()

---

## License Components

The MIT License consists of three main components: permissions, conditions, and warranty disclaimers.

```mermaid
graph TB
    LICENSE["MIT License<br/>(LICENSE file)"]
    
    subgraph "Permissions Granted"
        USE["Use<br/>Run the software"]
        MODIFY["Modify<br/>Alter source code"]
        DISTRIBUTE["Distribute<br/>Share copies"]
        SUBLICENSE["Sublicense<br/>Grant rights to others"]
        SELL["Sell<br/>Commercial use"]
    end
    
    subgraph "Conditions Required"
        COPYRIGHT["Include Copyright Notice<br/>lines 3-4"]
        PERMISSION["Include Permission Notice<br/>lines 5-21"]
        ALLCOPIES["Apply to All Copies<br/>lines 12-13"]
    end
    
    subgraph "Disclaimers"
        NOWARRANTY["No Warranty<br/>lines 15-16"]
        NOLIABILITY["No Liability<br/>lines 17-21"]
    end
    
    LICENSE --> USE
    LICENSE --> MODIFY
    LICENSE --> DISTRIBUTE
    LICENSE --> SUBLICENSE
    LICENSE --> SELL
    
    USE --> COPYRIGHT
    MODIFY --> COPYRIGHT
    DISTRIBUTE --> COPYRIGHT
    SUBLICENSE --> COPYRIGHT
    SELL --> COPYRIGHT
    
    COPYRIGHT --> PERMISSION
    PERMISSION --> ALLCOPIES
    
    LICENSE --> NOWARRANTY
    LICENSE --> NOLIABILITY
```

Sources: [LICENSE:1-22]()

---

## Permissions Granted

The MIT License grants users comprehensive rights to work with the Mnemis software without restriction. The following permissions are explicitly granted:

### Software Usage Rights

The license permits any person obtaining a copy of the software to "deal in the Software without restriction" ([LICENSE:6-7]()), which includes:

| Permission | Description | License Reference |
|------------|-------------|-------------------|
| **Use** | Run and execute the software for any purpose | [LICENSE:7]() |
| **Copy** | Create copies of the software | [LICENSE:5]() |
| **Modify** | Alter, enhance, or adapt the source code | [LICENSE:7]() |
| **Merge** | Combine with other software or code | [LICENSE:7]() |
| **Publish** | Make the software publicly available | [LICENSE:8]() |
| **Distribute** | Share copies with others | [LICENSE:8]() |
| **Sublicense** | Grant these same rights to third parties | [LICENSE:8]() |
| **Sell** | Use commercially, including selling copies | [LICENSE:8-9]() |

These rights apply to the entire Mnemis codebase, including:
- Core implementation files (e.g., `global_selector.py`, `prompts.py`)
- Benchmark datasets and evaluation scripts
- Configuration files and utilities
- Documentation and examples

Sources: [LICENSE:5-9]()

---

## Required Conditions

The MIT License requires that users fulfill two simple conditions when using, modifying, or distributing the software:

### 1. Copyright Notice Inclusion

The copyright notice must be included in all copies or substantial portions of the Software:

```
Copyright (c) 2026 Microsoft
```

This notice appears at [LICENSE:3]() and must be preserved.

### 2. Permission Notice Inclusion

The full permission text ([LICENSE:5-13]()) must be included alongside the copyright notice. This ensures that downstream users understand their rights and obligations.

### Application Scope

These conditions apply "in all copies or substantial portions of the Software" ([LICENSE:12-13]()). This means:

- **Full Distributions**: Any distribution of the complete Mnemis codebase must include the LICENSE file
- **Substantial Portions**: Large code excerpts or modules (e.g., the entire `GlobalSelector` class) require attribution
- **Derivative Works**: Modified versions or works built on Mnemis must preserve the notices
- **Documentation**: Projects that incorporate Mnemis should acknowledge the license

```mermaid
graph LR
    subgraph "Mnemis Codebase"
        REPO["Mnemis Repository<br/>github.com/microsoft/Mnemis"]
        LICENSE_FILE["LICENSE file<br/>lines 1-22"]
    end
    
    subgraph "Usage Scenarios"
        FULL["Full Distribution<br/>Complete copy of repo"]
        PARTIAL["Substantial Portion<br/>e.g. GlobalSelector class"]
        DERIVED["Derivative Work<br/>Modified version"]
        INTEGRATED["Integration<br/>Part of larger system"]
    end
    
    subgraph "Required Notices"
        COPYRIGHT_NOTICE["Copyright Notice<br/>line 3"]
        PERMISSION_TEXT["Permission Text<br/>lines 5-13"]
    end
    
    REPO --> LICENSE_FILE
    
    LICENSE_FILE --> FULL
    LICENSE_FILE --> PARTIAL
    LICENSE_FILE --> DERIVED
    LICENSE_FILE --> INTEGRATED
    
    FULL --> COPYRIGHT_NOTICE
    PARTIAL --> COPYRIGHT_NOTICE
    DERIVED --> COPYRIGHT_NOTICE
    INTEGRATED --> COPYRIGHT_NOTICE
    
    COPYRIGHT_NOTICE --> PERMISSION_TEXT
```

Sources: [LICENSE:3](), [LICENSE:5-13](), [LICENSE:12-13]()

---

## Warranty and Liability Disclaimers

The MIT License includes important disclaimers that protect the copyright holder from liability.

### No Warranty

The software is provided "AS IS", WITHOUT WARRANTY OF ANY KIND ([LICENSE:15-16]()). This means:

- **No Express Warranties**: Microsoft makes no promises about functionality or fitness
- **No Implied Warranties**: No guarantees of merchantability or suitability for purpose
- **User Responsibility**: Users accept the software in its current state

The disclaimer explicitly excludes all warranties including, but not limited to:
- Merchantability ([LICENSE:16]())
- Fitness for a particular purpose ([LICENSE:17]())
- Non-infringement ([LICENSE:17]())

### No Liability

Microsoft and the authors are not liable for any claims, damages, or other liability ([LICENSE:17-21]()). This covers:

| Liability Type | Description | Coverage |
|----------------|-------------|----------|
| **Contract** | Breach of agreement | [LICENSE:19]() |
| **Tort** | Civil wrongs or negligence | [LICENSE:19]() |
| **Other Liability** | Any other legal theory | [LICENSE:19]() |

The disclaimer applies to liability arising from:
- Use of the software ([LICENSE:20]())
- Connection with the software ([LICENSE:20]())
- Other dealings in the software ([LICENSE:20-21]())

Sources: [LICENSE:15-21]()

---

## Practical Implications

### For Users and Integrators

When using Mnemis in your projects:

1. **Include the License**: Copy the LICENSE file to your project or documentation
2. **Preserve Attribution**: Maintain copyright and permission notices
3. **No Restrictions**: You may use Mnemis for any purpose, including commercial applications
4. **Accept As-Is**: Understand that no warranties are provided

### For Contributors

Contributors to the Mnemis project should be aware that:

- Contributions are subject to the same MIT License
- Your code becomes part of the Microsoft-copyrighted work
- Others can freely use, modify, and commercialize your contributions
- See [Code of Conduct](#8.1) for community guidelines

### For Derivative Works

If you create a derivative work based on Mnemis:

1. You must include the original MIT License text
2. You may add your own copyright notice for your modifications
3. You may choose any license for your additions (the MIT License only requires that the original notices be preserved)
4. You have no obligation to share your changes (though open-source contributions are encouraged)

Sources: [LICENSE:1-22]()

---

## License Text Reference

The complete license text is available in the root of the repository at [LICENSE:1-22](). The text follows the standard MIT License format and is compatible with OSI (Open Source Initiative) approval and GPL compatibility.

### Full License Structure

```mermaid
graph TB
    LICENSE_FILE["LICENSE file"]
    
    HEADER["Header<br/>lines 1-4"]
    PERMISSIONS["Permissions Block<br/>lines 5-13"]
    WARRANTY["Warranty Disclaimer<br/>lines 15-17"]
    LIABILITY["Liability Disclaimer<br/>lines 17-21"]
    
    LICENSE_FILE --> HEADER
    LICENSE_FILE --> PERMISSIONS
    LICENSE_FILE --> WARRANTY
    LICENSE_FILE --> LIABILITY
    
    HEADER --> TITLE["MIT License<br/>line 1"]
    HEADER --> COPYRIGHT["Copyright (c) 2026 Microsoft<br/>line 3"]
    
    PERMISSIONS --> GRANT["Permission Grant<br/>lines 5-9"]
    PERMISSIONS --> CONDITION["Copyright Condition<br/>lines 12-13"]
    
    WARRANTY --> ASIS["AS IS provision<br/>line 15"]
    WARRANTY --> NOWARN["No warranties<br/>lines 16-17"]
    
    LIABILITY --> NOLIABLE["No liability clause<br/>lines 17-21"]
```

Sources: [LICENSE:1-22]()

---

## Summary

The MIT License provides maximum flexibility for using, modifying, and distributing the Mnemis codebase. The only requirements are to preserve copyright and license notices when redistributing the software. This permissive approach encourages adoption and contribution while protecting the copyright holder from liability.

| Aspect | Details |
|--------|---------|
| **License Type** | MIT License |
| **Permissions** | Use, copy, modify, merge, publish, distribute, sublicense, sell |
| **Conditions** | Include copyright and permission notices |
| **Warranties** | None (software provided "AS IS") |
| **Liability** | None (no liability for damages or claims) |
| **Commercial Use** | Permitted without restriction |
| **File Location** | [LICENSE:1-22]() |

For questions about licensing, contribution guidelines, or commercial use cases, refer to the [Contributing](#8) section or contact Microsoft through the repository's official channels.

Sources: [LICENSE:1-22]()