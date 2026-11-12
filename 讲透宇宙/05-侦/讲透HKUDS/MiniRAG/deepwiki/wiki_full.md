# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [MANIFEST.in](MANIFEST.in)
- [README.md](README.md)
- [README_CN.md](README_CN.md)
- [README_JA.md](README_JA.md)
- [pyproject.toml](pyproject.toml)

</details>



This document provides a high-level introduction to MiniRAG, its design philosophy, and system architecture. It explains the core workflow, key components, and how they interact to enable efficient Retrieval-Augmented Generation (RAG) on Small Language Models (SLMs).

For detailed information about specific subsystems, see [System Architecture](#3) and [Core Concepts](#4). For practical usage examples, refer to [Usage Examples](#8).

## What is MiniRAG?

MiniRAG is a lightweight Retrieval-Augmented Generation framework designed to enable Small Language Models (1.5B-4B parameters) to achieve strong RAG performance. Unlike traditional RAG systems that rely on large language models with advanced semantic understanding capabilities, MiniRAG employs a simplified approach through heterogeneous graph indexing and topology-enhanced retrieval.

The framework addresses a critical challenge: existing RAG systems experience severe performance degradation when using SLMs due to their limited semantic understanding and text processing capabilities. MiniRAG achieves comparable performance to LLM-based methods while requiring only 25% of the storage space.

**Key Performance Metrics:**
- 53.29% accuracy with Phi-3.5-mini-instruct on LiHua-World dataset
- 13.48 percentage point improvement over baseline LightRAG (39.81%)
- 25% storage footprint compared to traditional approaches

**Sources:** [README.md:1-35](), [README_CN.md:1-29](), [README_JA.md:1-31]()

## System Purpose and Scope

MiniRAG serves as a complete RAG solution with the following capabilities:

| Capability | Description |
|------------|-------------|
| **Document Indexing** | Ingests raw text documents, extracts entities and relationships, builds knowledge graph |
| **Multi-mode Querying** | Supports five query strategies (naive, light, mini, hybrid, global) for different use cases |
| **Storage Abstraction** | Pluggable backend support for 10+ databases (Neo4j, PostgreSQL, TiDB, etc.) |
| **SLM Optimization** | Specifically designed for resource-constrained environments with small models |
| **Benchmark Evaluation** | Includes LiHua-World dataset for comprehensive performance assessment |

**Sources:** [README.md:30-88](), [pyproject.toml:1-22]()

## Core Components and Code Architecture

The following diagram maps MiniRAG's logical components to their concrete implementations in the codebase:

```mermaid
graph TB
    subgraph "Entry Points"
        Main["main.py<br/>Basic usage example"]
        Step0["reproduce/Step_0_index.py<br/>Document indexing"]
        Step1["reproduce/Step_1_QA.py<br/>Query processing"]
    end
    
    subgraph "Core Orchestration Layer"
        MiniRAGClass["minirag/minirag.py<br/>MiniRAG class<br/>Primary orchestrator"]
    end
    
    subgraph "Storage Abstraction"
        BaseInterfaces["minirag/base.py<br/>BaseGraphStorage<br/>BaseVectorStorage<br/>BaseKVStorage"]
        DocStatus["minirag/base.py<br/>DocStatusStorage<br/>Document tracking"]
    end
    
    subgraph "Storage Implementations"
        GraphImpl["minirag/kg/<br/>networkx_impl.py<br/>neo4j_impl.py<br/>postgres_impl.py<br/>oracle_impl.py"]
        VectorImpl["minirag/storage.py<br/>NanoVectorDB<br/>Weaviate"]
        KVImpl["minirag/storage.py<br/>JSON/Redis storage"]
    end
    
    subgraph "Processing & Operations"
        Operate["minirag/operate.py<br/>extract_entities()<br/>minirag_query()<br/>naive_query()"]
        Utils["minirag/utils.py<br/>Text processing<br/>Similarity calculations"]
    end
    
    subgraph "LLM Integration"
        LLM["minirag/llm.py<br/>openai_complete()<br/>hf_model_complete()"]
        Prompts["minirag/prompt.py<br/>Entity extraction<br/>Query generation"]
    end
    
    subgraph "Data Resources"
        Dataset["dataset/LiHua-World/<br/>query_set.json<br/>LiHuaWorld.zip"]
    end
    
    Main --> MiniRAGClass
    Step0 --> MiniRAGClass
    Step1 --> MiniRAGClass
    
    MiniRAGClass --> BaseInterfaces
    MiniRAGClass --> Operate
    MiniRAGClass --> LLM
    
    BaseInterfaces --> GraphImpl
    BaseInterfaces --> VectorImpl
    BaseInterfaces --> KVImpl
    BaseInterfaces --> DocStatus
    
    Operate --> LLM
    Operate --> Prompts
    Operate --> Utils
    
    Step0 --> Dataset
    Step1 --> Dataset
```

**Sources:** [README.md:96-131](), [README_CN.md:89-123](), [README_JA.md:93-127]()

## Two-Phase Workflow

MiniRAG operates in two distinct phases, implemented through a clear separation of concerns in the codebase:

### Phase 1: Document Indexing

```mermaid
graph LR
    Input["Raw Documents<br/>Text files"]
    Insert["MiniRAG.insert()<br/>minirag/minirag.py"]
    Chunk["Text chunking<br/>minirag/utils.py"]
    Extract["extract_entities()<br/>minirag/operate.py"]
    
    subgraph "Storage Population"
        GraphDB["Graph Storage<br/>BaseGraphStorage<br/>entities + relationships"]
        VectorDB["Vector Databases<br/>entity_vdb<br/>chunks_vdb"]
        KVDB["Key-Value Store<br/>text chunks<br/>BaseKVStorage"]
        DocStatusDB["DocStatusStorage<br/>processing status"]
    end
    
    Input --> Insert
    Insert --> Chunk
    Chunk --> Extract
    Extract --> GraphDB
    Extract --> VectorDB
    Extract --> KVDB
    Extract --> DocStatusDB
```

During indexing, the system:
1. Accepts documents through `MiniRAG.insert()` method in [minirag/minirag.py]()
2. Chunks documents using utilities in [minirag/utils.py]()
3. Extracts entities and relationships via `extract_entities()` in [minirag/operate.py]()
4. Populates three storage types: graph (entities/relationships), vector (embeddings), and key-value (text chunks)
5. Tracks processing status using `DocStatusStorage` in [minirag/base.py]()

**Sources:** [README.md:36-41](), [minirag/minirag.py]()

### Phase 2: Query and Retrieval

```mermaid
graph LR
    Query["User Query"]
    QueryMethod["MiniRAG.query()<br/>minirag/minirag.py"]
    
    subgraph "Query Mode Selection"
        Naive["naive_query()<br/>minirag/operate.py"]
        Light["lightrag_query()<br/>minirag/operate.py"]
        Mini["minirag_query()<br/>minirag/operate.py"]
        Hybrid["hybrid_query()<br/>minirag/operate.py"]
    end
    
    Retrieval["Graph Traversal<br/>Context Assembly"]
    
    subgraph "Storage Retrieval"
        GraphRead["BaseGraphStorage<br/>get_node()<br/>get_node_edges()"]
        VectorRead["BaseVectorStorage<br/>query()<br/>similarity search"]
        KVRead["BaseKVStorage<br/>get()<br/>text retrieval"]
    end
    
    LLMGen["LLM Generation<br/>openai_complete()<br/>hf_model_complete()"]
    Answer["Final Answer"]
    
    Query --> QueryMethod
    QueryMethod --> Naive
    QueryMethod --> Light
    QueryMethod --> Mini
    QueryMethod --> Hybrid
    
    Mini --> Retrieval
    Retrieval --> GraphRead
    Retrieval --> VectorRead
    Retrieval --> KVRead
    
    GraphRead --> LLMGen
    VectorRead --> LLMGen
    KVRead --> LLMGen
    
    LLMGen --> Answer
```

During querying, the system:
1. Accepts queries through `MiniRAG.query()` method in [minirag/minirag.py]()
2. Selects query mode (naive, light, mini, hybrid, global) based on `QueryParam` configuration
3. Performs topology-enhanced retrieval using graph traversal operations in [minirag/operate.py]()
4. Retrieves relevant context from graph, vector, and key-value storage backends
5. Generates answers using LLM integration functions in [minirag/llm.py]()

**Sources:** [README.md:36-41]()

## Repository Structure

The codebase is organized into clear functional modules:

| Directory/File | Purpose |
|----------------|---------|
| `minirag/minirag.py` | Core `MiniRAG` class - main orchestrator for insert and query operations |
| `minirag/base.py` | Abstract storage interfaces: `BaseGraphStorage`, `BaseVectorStorage`, `BaseKVStorage` |
| `minirag/operate.py` | RAG operations: entity extraction, query processing for all modes |
| `minirag/llm.py` | LLM integration: OpenAI, HuggingFace, NVIDIA, OpenRouter APIs |
| `minirag/storage.py` | Concrete storage implementations: NanoVectorDB, JSON storage |
| `minirag/kg/` | Graph database implementations: Neo4j, PostgreSQL, TiDB, Oracle |
| `minirag/utils.py` | Utility functions: text processing, similarity calculations, graph operations |
| `minirag/prompt.py` | Prompt templates for entity extraction and query generation |
| `reproduce/Step_0_index.py` | Script for indexing datasets into knowledge graph |
| `reproduce/Step_1_QA.py` | Script for running query experiments and evaluation |
| `dataset/LiHua-World/` | Benchmark dataset with query sets and evaluation data |

**Sources:** [README.md:96-131](), [README_CN.md:89-123]()

## Quick Start Example

The simplest way to use MiniRAG involves three steps:

```python
# 1. Initialize MiniRAG with working directory
rag = MiniRAG(working_dir="./workspace")

# 2. Index documents (one-time setup)
rag.insert("Your document content here")

# 3. Query the knowledge graph
result = rag.query("Your question", param=QueryParam(mode="mini"))
```

For complete reproduction of benchmark results:
- Use [reproduce/Step_0_index.py]() to index the LiHua-World dataset
- Use [reproduce/Step_1_QA.py]() to run evaluation experiments

**Sources:** [README.md:57-68](), [README_CN.md:51-62](), [README_JA.md:54-65]()

## Supported Models and Backends

MiniRAG supports multiple LLM providers and storage backends through its abstraction layers:

**Language Models:**
- Small Language Models: Phi-3.5-mini-instruct, GLM-Edge-1.5B-Chat, Qwen2.5-3B-Instruct, MiniCPM3-4B
- Large Language Models: gpt-4o-mini (for comparison)
- Integration: OpenAI API, HuggingFace models, NVIDIA API, OpenRouter

**Storage Backends:**
- Graph: NetworkX (in-memory), Neo4j, PostgreSQL, TiDB, Oracle, and 5+ additional databases
- Vector: NanoVectorDB, Weaviate, Chroma
- Key-Value: JSON files, Redis, MongoDB

See [LLM and Embedding Integration](#6) for detailed model configuration and [Storage Implementations](#5) for backend setup instructions.

**Sources:** [README.md:25-29](), [README_CN.md:20-23]()

## Performance Characteristics

MiniRAG achieves strong performance across different model sizes and question types:

| Model | Size | LiHua-World Accuracy | Storage Reduction |
|-------|------|----------------------|-------------------|
| Phi-3.5-mini-instruct | 3.8B | 53.29% | 75% |
| GLM-Edge-1.5B-Chat | 1.5B | 52.51% | 75% |
| Qwen2.5-3B-Instruct | 3B | 48.75% | 75% |
| MiniCPM3-4B | 4B | 51.25% | 75% |

Compared to baselines (NaiveRAG: ~42%, LightRAG: ~39%), MiniRAG shows 10-14 percentage point improvements when using small models. The framework achieves this through two key technical innovations detailed in [Key Innovations](#1.2).

**Sources:** [README.md:73-88](), [README_CN.md:67-82]()

## Related Projects and Acknowledgments

MiniRAG builds upon and extends the following projects:
- **LightRAG**: Foundation codebase providing base storage abstractions and query modes
- **nano-graphrag**: Graph processing utilities and algorithms
- **VideoRAG**: Related project by the same team for video understanding

The framework is available on PyPI as `minirag-hku` or `lightrag-hku` for easy installation and deployment.

**Sources:** [README.md:158-161](), [README_CN.md:151-152](), [pyproject.toml:5-7]()

---

# Page: Goals and Motivation

# Goals and Motivation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README_CN.md](README_CN.md)

</details>



This document explains the fundamental problems that MiniRAG addresses, the scenarios and use cases it targets, and how it differs from existing RAG approaches. It covers the challenges faced by Small Language Models (SLMs) in retrieval-augmented generation, the limitations of resource-intensive LLM-based systems, and MiniRAG's design philosophy of extreme simplicity and efficiency.

For implementation details of the two core technical innovations (heterogeneous graph indexing and topology-enhanced retrieval), see [Key Innovations](#1.2).

## The Problem: SLM Performance Degradation in RAG Systems

Traditional RAG systems face severe performance degradation when deployed with Small Language Models (1.5B-4B parameters) instead of large language models. This degradation stems from three fundamental limitations:

### Limited Semantic Understanding

SLMs struggle with the complex semantic reasoning required by existing RAG frameworks. Traditional vector-based retrieval relies heavily on the model's ability to understand nuanced semantic relationships between query and document embeddings. When SLMs perform entity extraction, relationship identification, and contextual reasoning, their accuracy drops significantly compared to LLMs.

### Text Processing Constraints

SLMs have reduced capacity for processing and synthesizing information from multiple retrieved documents. Methods like GraphRAG [README.md:74-88]() require sophisticated text generation capabilities to build knowledge graphs and perform multi-hop reasoning. As shown in the performance tables, GraphRAG completely fails (marked as "/") when used with SLMs like Phi-3.5-mini-instruct or GLM-Edge-1.5B-Chat.

### Resource Requirements vs. Model Capabilities

The mismatch between computational resources and model capabilities creates a critical gap. While on-device deployment demands lightweight solutions, existing RAG approaches assume the availability of powerful LLMs with strong reasoning capabilities.

```mermaid
graph TB
    subgraph "Traditional RAG Approaches"
        VectorRAG["NaiveRAG<br/>Vector Similarity Search"]
        GraphRAGMethod["GraphRAG<br/>LLM-Generated Knowledge Graphs"]
        LightRAGMethod["LightRAG<br/>Entity-Based Retrieval"]
    end
    
    subgraph "Small Language Models"
        SLM1["Phi-3.5-mini-instruct<br/>3.8B parameters"]
        SLM2["GLM-Edge-1.5B-Chat<br/>1.5B parameters"]
        SLM3["Qwen2.5-3B-Instruct<br/>3B parameters"]
        SLM4["MiniCPM3-4B<br/>4B parameters"]
    end
    
    subgraph "Performance Barriers"
        Semantic["Weak Semantic<br/>Understanding<br/>39-43% accuracy"]
        Generation["Limited Text<br/>Generation<br/>Complete failure ()"]
        Memory["Constrained<br/>Context Window<br/>High error rates"]
    end
    
    VectorRAG --> SLM1
    VectorRAG --> SLM2
    GraphRAGMethod --> SLM3
    LightRAGMethod --> SLM4
    
    SLM1 --> Semantic
    SLM2 --> Semantic
    SLM3 --> Generation
    SLM4 --> Memory
    
    style Semantic fill:#ffcccc
    style Generation fill:#ffcccc
    style Memory fill:#ffcccc
```

**Diagram 1: Performance Barriers When Deploying SLMs in Traditional RAG Systems**

Sources: [README.md:74-91](), [README.md:33-34]()

## Target Scenarios and Use Cases

MiniRAG specifically targets deployment scenarios where computational resources, storage capacity, and network connectivity are constrained. These scenarios demand RAG systems that can operate efficiently without relying on large language models or cloud-based infrastructure.

### On-Device RAG Deployment

The primary use case is on-device RAG systems that run entirely on local hardware such as smartphones, tablets, IoT devices, and edge computing nodes. The LiHua-World benchmark dataset [README.md:133-137]() was specifically designed to evaluate RAG systems in these realistic on-device scenarios with complex queries based on one year of chat history from a virtual user.

```mermaid
graph LR
    subgraph "Deployment Constraints"
        Storage["Storage<br/>Limited disk space<br/>< 1GB for index"]
        Compute["Compute<br/>Consumer hardware<br/>No GPU required"]
        Network["Network<br/>Offline operation<br/>No API calls"]
        Privacy["Privacy<br/>Local data only<br/>No cloud upload"]
    end
    
    subgraph "MiniRAG Architecture"
        Core["MiniRAG Core<br/>minirag/minirag.py"]
        HetGraph["Heterogeneous Graph Index<br/>25% storage vs traditional"]
        TopoRetrieval["Topology-Enhanced Retrieval<br/>Lightweight discovery"]
    end
    
    subgraph "Target Devices"
        Mobile["Smartphones<br/>Personal assistants"]
        IoT["IoT Devices<br/>Smart home hubs"]
        Edge["Edge Nodes<br/>Local servers"]
    end
    
    Storage --> Core
    Compute --> Core
    Network --> Core
    Privacy --> Core
    
    Core --> HetGraph
    Core --> TopoRetrieval
    
    HetGraph --> Mobile
    TopoRetrieval --> IoT
    Core --> Edge
    
    style Core fill:#e6f3ff
    style HetGraph fill:#fff0e6
    style TopoRetrieval fill:#ffe6f0
```

**Diagram 2: MiniRAG Target Deployment Scenarios and Architecture Mapping**

Sources: [README.md:30-34](), [README.md:133-137](), [minirag/minirag.py:1-1000]()

### Resource-Constrained Enterprise Applications

Organizations deploying RAG systems in resource-limited environments benefit from MiniRAG's efficiency:

| Constraint Type | Traditional RAG Impact | MiniRAG Solution |
|-----------------|------------------------|------------------|
| Storage Space | Full-text indices + embeddings require 4x original data | Heterogeneous graph requires only 25% space [README.md:34]() |
| Model Size | Requires 7B+ parameter LLMs (14GB+ memory) | Works with 1.5B-4B parameter SLMs (3-8GB memory) |
| API Costs | Continuous API calls to cloud LLMs ($$$) | Local inference with open-source models (free) |
| Latency | Network round-trips + LLM generation (seconds) | Local graph traversal + SLM inference (milliseconds) |
| Privacy | Data sent to third-party APIs | All processing remains on-device |

Sources: [README.md:33-34](), [README.md:74-88]()

## Design Goals and Principles

MiniRAG's design centers on three core principles that guide all architectural decisions:

### Extreme Simplicity

The framework achieves "extreme simplicity" [README.md:1]() by:

1. **Unified Data Structure**: Combining text chunks and named entities in a single heterogeneous graph index, eliminating the need for separate complex data structures
2. **Lightweight Operations**: Using graph topology for knowledge discovery instead of complex semantic reasoning
3. **Minimal Dependencies**: Relying on basic graph operations rather than sophisticated NLP pipelines

This simplicity is implemented in the core `MiniRAG` class [minirag/minirag.py:1-1000]() which orchestrates the entire pipeline through straightforward graph-based operations.

### Efficiency-First Architecture

Every component prioritizes resource efficiency:

- **Storage Efficiency**: 25% storage requirement compared to traditional methods [README.md:34]()
- **Computational Efficiency**: Graph traversal operations in the topology-enhanced retrieval [minirag/operate.py:1-1000]() require minimal computation
- **Memory Efficiency**: SLMs with 1.5B-4B parameters fit in consumer-grade memory

### Performance Parity with LLM-Based Systems

Despite using much smaller models, MiniRAG achieves comparable or superior performance to LLM-based baselines. On the LiHua-World benchmark:

- MiniRAG with Phi-3.5-mini (3.8B): **53.29% accuracy**
- LightRAG with Phi-3.5-mini (3.8B): 39.81% accuracy
- GraphRAG with gpt-4o-mini: 35.27% accuracy (fails with SLMs)

Sources: [README.md:30-34](), [README.md:74-88]()

```mermaid
graph TB
    subgraph "Design Goal: Extreme Simplicity"
        Goal1["Unified heterogeneous<br/>graph structure"]
        Goal2["Basic graph operations<br/>instead of complex NLP"]
        Goal3["Minimal architectural<br/>complexity"]
    end
    
    subgraph "Implementation: minirag/"
        Core["minirag.py<br/>Main orchestrator<br/>Importance: 15.12"]
        Operate["operate.py<br/>Entity extraction<br/>Query processing<br/>Importance: 4.78"]
        Base["base.py<br/>Storage abstractions<br/>Importance: 6.61"]
    end
    
    subgraph "Result: Efficiency"
        Storage["25% storage space"]
        Performance["53.29% accuracy<br/>vs 39.81% baseline"]
        Models["Works with 1.5B-4B<br/>parameter SLMs"]
    end
    
    Goal1 --> Core
    Goal2 --> Operate
    Goal3 --> Base
    
    Core --> Storage
    Operate --> Performance
    Base --> Models
    
    style Core fill:#e6f3ff
    style Storage fill:#e6ffe6
    style Performance fill:#e6ffe6
```

**Diagram 3: Design Goals Flow from Principles to Implementation to Results**

Sources: [README.md:1](), [README.md:30-34](), [minirag/minirag.py:1-1000](), [minirag/operate.py:1-1000](), [minirag/base.py:1-1000]()

## Comparison with Existing RAG Approaches

MiniRAG's motivation becomes clearer when compared against the three primary baseline methods documented in the evaluation scripts [reproduce/Step_1_QA.py:1-1000]():

### NaiveRAG: Simple Vector Similarity

NaiveRAG represents the baseline approach using pure vector similarity search without graph structures or entity extraction. While simple, it achieves only 41-44% accuracy with SLMs [README.md:78-81]() because:

- No structural knowledge representation
- Relies entirely on semantic embedding quality
- Cannot perform multi-hop reasoning
- High error rates (17-24%) due to insufficient context

### GraphRAG: LLM-Dependent Graph Construction

GraphRAG attempts to build knowledge graphs using LLMs but completely fails when deployed with SLMs (marked "/" in results table [README.md:78-81]()). The fundamental issues:

- Requires strong LLM capabilities for graph construction
- Heavy computational and storage overhead
- Error rates spike to 37% even with gpt-4o-mini [README.md:82]()
- Cannot operate in resource-constrained environments

### LightRAG: Entity-Centric Foundation

LightRAG [README.md:160]() serves as the codebase foundation for MiniRAG. While it improves over NaiveRAG by incorporating entity extraction, it still faces limitations:

- Performance with SLMs: 35-40% accuracy [README.md:78-81]()
- Requires relatively strong semantic understanding
- Less efficient storage and retrieval
- Error rates: 21-28%

### MiniRAG: Topology-Enhanced Lightweight Solution

MiniRAG builds on LightRAG's foundation while introducing critical innovations:

| Metric | NaiveRAG | GraphRAG | LightRAG | **MiniRAG** |
|--------|----------|----------|----------|-------------|
| **Phi-3.5-mini Accuracy** | 41.22% | / (fails) | 39.81% | **53.29%** ✓ |
| **GLM-Edge-1.5B Accuracy** | 42.79% | / (fails) | 35.74% | **52.51%** ✓ |
| **Storage Requirement** | 100% | 150%+ | 100% | **25%** ✓ |
| **SLM Compatibility** | Partial | None | Partial | **Full** ✓ |
| **Error Rate (Phi-3.5)** | 23.20% | N/A | 25.39% | **23.35%** ≈ |
| **Multi-hop Performance** | 42.72% | 60.92% (LLM) | 27.03% | **49.96%** ✓ |

Sources: [README.md:74-88]()

```mermaid
graph TB
    subgraph "Baseline: NaiveRAG"
        NV["Vector Search Only<br/>reproduce/Step_1_QA.py<br/>mode='naive'"]
        NP["41-44% accuracy<br/>No structure"]
    end
    
    subgraph "Baseline: GraphRAG"
        GV["LLM-Built Graphs<br/>reproduce/Step_1_QA.py<br/>Comparison method"]
        GP["Fails with SLMs ()<br/>Requires strong LLM"]
    end
    
    subgraph "Foundation: LightRAG"
        LV["Entity Extraction<br/>reproduce/Step_1_QA.py<br/>mode='light'"]
        LP["35-40% accuracy<br/>Base implementation"]
    end
    
    subgraph "Innovation: MiniRAG"
        MV["Heterogeneous Graph +<br/>Topology Retrieval<br/>reproduce/Step_1_QA.py<br/>mode='mini'"]
        MP["48-53% accuracy<br/>25% storage<br/>SLM-optimized"]
    end
    
    NV --> NP
    GV --> GP
    LV --> LP
    MV --> MP
    
    LP --> MV
    
    style MP fill:#e6ffe6
    style GP fill:#ffcccc
```

**Diagram 4: Evolution from Baseline Methods to MiniRAG**

Sources: [README.md:74-91](), [README.md:159-160](), [reproduce/Step_1_QA.py:1-1000]()

## Key Metrics and Success Criteria

The motivation for MiniRAG is validated through concrete performance metrics across multiple dimensions:

### Accuracy Improvement

On the LiHua-World benchmark [dataset/LiHua-World/qa/query_set.json:1-1000](), MiniRAG achieves:

- **+13.48%** absolute improvement over LightRAG with Phi-3.5-mini (53.29% vs 39.81%)
- **+16.77%** improvement with GLM-Edge-1.5B (52.51% vs 35.74%)
- **+9.57%** improvement with Qwen2.5-3B (48.75% vs 39.18%)
- **+15.83%** improvement with MiniCPM3-4B (51.25% vs 35.42%)

### Storage Efficiency

MiniRAG's heterogeneous graph indexing requires only **25% of the storage space** [README.md:34]() compared to traditional full-text indices and vector databases, making it practical for on-device deployment.

### Multi-Hop Reasoning

On the MultiHop-RAG benchmark, MiniRAG demonstrates strong multi-hop reasoning capabilities even with SLMs:

- Phi-3.5-mini: **49.96%** (vs 42.72% NaiveRAG, 27.03% LightRAG)
- Approaches LLM-level performance: 68.43% with gpt-4o-mini (vs 64.91% LightRAG)

### Error Rate Stability

MiniRAG maintains stable error rates comparable to baselines (23-26% range [README.md:78-82]()), indicating that performance improvements come from better retrieval and reasoning rather than increased hallucination.

Sources: [README.md:74-88](), [README.md:33-34](), [dataset/LiHua-World/README.md:1-100]()

---

**Summary**: MiniRAG addresses the critical gap between the growing demand for on-device RAG systems and the limitations of Small Language Models in existing frameworks. By introducing heterogeneous graph indexing and topology-enhanced retrieval, it enables SLMs to achieve performance comparable to LLM-based methods while requiring only 25% of the storage space. This makes practical on-device RAG deployment feasible for resource-constrained scenarios, as validated by comprehensive evaluation on the LiHua-World benchmark.

Sources: [README.md:1-174](), [README_CN.md:1-166]()

---

# Page: Key Innovations

# Key Innovations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [minirag/api/requirements.txt](minirag/api/requirements.txt)
- [minirag/operate.py](minirag/operate.py)

</details>



MiniRAG introduces two core technical innovations that enable Small Language Models (SLMs) to achieve strong RAG performance while using only 25% of the storage space compared to traditional methods. These innovations address the fundamental limitations of SLMs in semantic understanding and complex reasoning tasks.

The two key innovations are:

1. **Heterogeneous Graph Indexing**: A unified graph structure combining text chunks and named entities that reduces semantic understanding requirements
2. **Topology-Enhanced Retrieval**: A lightweight graph traversal approach that enables efficient knowledge discovery without advanced language capabilities

On the LiHua-World benchmark, MiniRAG achieves 53.29% accuracy with Phi-3.5-mini (vs 39.81% baseline), demonstrating significant performance improvements over NaiveRAG and LightRAG when using SLMs.

Sources: [README.md:30-35](), [README.md:74-82]()

## Innovation 1: Heterogeneous Graph Indexing

### Overview

MiniRAG's heterogeneous graph indexing mechanism creates a unified structure that combines text chunks and named entities into a single graph. This approach reduces the semantic understanding burden on SLMs by providing explicit, pre-computed connections between information pieces.

### Graph Structure

The heterogeneous graph index consists of three types of elements:

| Element Type | Stored In | Key Attributes | Purpose |
|--------------|-----------|----------------|---------|
| **Text Chunk Nodes** | `chunks_vdb` (vector DB)<br>`text_chunks_db` (KV store) | `content`, `tokens`, `chunk_order_index` | Original document fragments with embeddings |
| **Entity Nodes** | `entity_vdb` (vector DB)<br>`entity_name_vdb` (vector DB)<br>`knowledge_graph_inst` (graph DB) | `entity_name`, `entity_type`, `description`, `source_id` | Named entities extracted from text |
| **Relationship Edges** | `relationships_vdb` (vector DB)<br>`knowledge_graph_inst` (graph DB) | `src_id`, `tgt_id`, `keywords`, `weight`, `description` | Connections between entities |

#### Heterogeneous Graph Index Structure

```mermaid
graph TB
    subgraph TextChunks["Text Chunk Layer"]
        TC1["TextChunk_001<br/>content: 'Alice works...'<br/>tokens: 1024"]
        TC2["TextChunk_002<br/>content: 'Bob manages...'<br/>tokens: 856"]
        TC3["TextChunk_003<br/>content: 'Alice and Bob...'<br/>tokens: 942"]
    end
    
    subgraph Entities["Entity Layer"]
        E1["Entity: ALICE<br/>type: PERSON<br/>source_id: chunk_001,chunk_003"]
        E2["Entity: BOB<br/>type: PERSON<br/>source_id: chunk_002,chunk_003"]
        E3["Entity: COMPANY_X<br/>type: ORGANIZATION<br/>source_id: chunk_001"]
    end
    
    subgraph Relationships["Relationship Layer"]
        R1["ALICE --works_at--> COMPANY_X<br/>weight: 1.0<br/>source_id: chunk_001"]
        R2["ALICE --collaborates_with--> BOB<br/>weight: 2.0<br/>source_id: chunk_003"]
    end
    
    TC1 -.contains.-> E1
    TC1 -.contains.-> E3
    TC2 -.contains.-> E2
    TC3 -.contains.-> E1
    TC3 -.contains.-> E2
    
    E1 --> R1
    E3 --> R1
    E1 --> R2
    E2 --> R2
```

Sources: [minirag/operate.py:233-408](), [minirag/base.py:1-50]()

### Entity Extraction Process

The entity extraction process is implemented in `extract_entities()` and follows these steps:

#### Entity Extraction Pipeline

```mermaid
flowchart TD
    Chunks["Text Chunks<br/>TextChunkSchema"] --> ExtractPrompt["entity_extraction prompt<br/>PROMPTS['entity_extraction']"]
    
    ExtractPrompt --> LLM["llm_model_func<br/>use_llm_func()"]
    
    LLM --> ParseRecords["_handle_single_entity_extraction()<br/>_handle_single_relationship_extraction()"]
    
    ParseRecords --> MaybeNodes["maybe_nodes: dict<br/>entity_name -> list[entity_data]"]
    ParseRecords --> MaybeEdges["maybe_edges: dict<br/>(src, tgt) -> list[edge_data]"]
    
    MaybeNodes --> MergeNodes["_merge_nodes_then_upsert()<br/>Aggregates descriptions"]
    MaybeEdges --> MergeEdges["_merge_edges_then_upsert()<br/>Sums weights"]
    
    MergeNodes --> GraphDB["knowledge_graph_inst<br/>BaseGraphStorage.upsert_node()"]
    MergeEdges --> GraphDB["knowledge_graph_inst<br/>BaseGraphStorage.upsert_edge()"]
    
    MergeNodes --> EntityVDB["entity_vdb.upsert()<br/>entity_name_vdb.upsert()"]
    MergeEdges --> RelVDB["relationships_vdb.upsert()"]
```

Sources: [minirag/operate.py:233-408]()

### Implementation Details

The extraction process uses LLM-based entity recognition with configurable gleaning:

```
extract_entities() parameters:
- chunks: dict[str, TextChunkSchema]
- knowledge_graph_inst: BaseGraphStorage
- entity_vdb, entity_name_vdb, relationships_vdb: BaseVectorStorage
- global_config['entity_extract_max_gleaning']: int (default: 1)
```

Key implementation functions:
- `_handle_single_entity_extraction()` [minirag/operate.py:70-88](): Parses entity records
- `_handle_single_relationship_extraction()` [minirag/operate.py:91-114](): Parses relationship records
- `_merge_nodes_then_upsert()` [minirag/operate.py:117-163](): Aggregates duplicate entities
- `_merge_edges_then_upsert()` [minirag/operate.py:166-230](): Merges relationship data

The heterogeneous graph structure enables multiple retrieval pathways:
- **Vector-based**: Search entities or relationships by semantic similarity
- **Graph-based**: Traverse connections between entities
- **Hybrid**: Combine vector search with graph traversal

Sources: [minirag/operate.py:233-408](), [README.md:31-35]()

## Innovation 2: Topology-Enhanced Retrieval

### Overview

MiniRAG's topology-enhanced retrieval approach leverages the graph structure to discover relevant information through lightweight graph traversal operations, eliminating the need for advanced language understanding capabilities. This is particularly effective for multi-hop reasoning queries.

### MiniRAG Query Architecture

The topology-enhanced retrieval is implemented in `minirag_query()` and consists of three main phases:

#### Phase 1: Query Analysis and Entity Extraction

```mermaid
flowchart TD
    Query["User Query<br/>'What did Alice do at Company X?'"] --> ExtractPrompt["minirag_query2kwd<br/>PROMPTS['minirag_query2kwd']"]
    
    ExtractPrompt --> TypePool["get_types()<br/>TYPE_POOL from knowledge_graph_inst"]
    TypePool --> LLM["llm_model_func()"]
    
    LLM --> ParseJSON["json_repair.loads()"]
    
    ParseJSON --> EntitiesFromQuery["entities_from_query: list<br/>['ALICE', 'COMPANY_X']"]
    ParseJSON --> AnswerTypes["answer_type_keywords: list<br/>['ACTION', 'EVENT']"]
```

Sources: [minirag/operate.py:1409-1449]()

#### Phase 2: Graph Traversal and Path Discovery

```mermaid
flowchart TD
    EntitiesFromQuery["entities_from_query"] --> EntityNameVDB["entity_name_vdb.query()<br/>top_k matching entities"]
    
    EntityNameVDB --> CandidatePaths["candidate_reasoning_path: dict<br/>entity_name -> {Score, Path}"]
    
    CandidatePaths --> GetNeighbors["get_neighbors_within_k_hops()<br/>k=2 hops"]
    
    GetNeighbors --> PathData["Path data:<br/>[(entity1, entity2), ...]"]
    
    AnswerTypes["answer_type_keywords"] --> TypeQuery["get_node_from_types()<br/>Retrieve entities by type"]
    
    TypeQuery --> MaybeAnswers["maybe_answer_list: list<br/>Candidate answer entities"]
    
    PathData --> ScorePaths["cal_path_score_list()<br/>Score reasoning paths"]
    MaybeAnswers --> ScorePaths
    
    ScorePaths --> ScoredPaths["scored_reasoning_path: dict<br/>Scored entity paths"]
```

Sources: [minirag/operate.py:1252-1319]()

#### Phase 3: Edge Voting and Chunk Retrieval

```mermaid
flowchart TD
    ScoredPaths["scored_reasoning_path"] --> RelVDB["relationships_vdb.query()<br/>Find relevant edges"]
    
    RelVDB --> FilterEdges["Filter edges by<br/>important entities"]
    
    FilterEdges --> EdgeVote["edge_vote_path()<br/>Vote on path quality"]
    
    EdgeVote --> ScoredEdgePaths["scored_edged_reasoning_path<br/>pairs_append"]
    
    ScoredEdgePaths --> Path2Chunk["path2chunk()<br/>Convert paths to chunk IDs"]
    
    Path2Chunk --> ChunkVDB["chunks_vdb.query()<br/>Get additional chunks"]
    
    ChunkVDB --> KWD2Chunk["kwd2chunk()<br/>Combine chunk scores"]
    
    KWD2Chunk --> FinalChunks["final_chunk_id: list<br/>Top-ranked chunks"]
    
    FinalChunks --> TextChunksDB["text_chunks_db.get_by_id()<br/>Retrieve chunk content"]
    
    TextChunksDB --> Context["Context Assembly<br/>Entities + Sources"]
```

Sources: [minirag/operate.py:1320-1406]()

### Complete MiniRAG Retrieval Flow

#### minirag_query() End-to-End Process

```mermaid
sequenceDiagram
    participant User
    participant minirag_query
    participant LLM as llm_model_func
    participant EntityNameVDB as entity_name_vdb
    participant KG as knowledge_graph_inst
    participant RelVDB as relationships_vdb
    participant ChunksVDB as chunks_vdb
    participant TextChunksDB as text_chunks_db
    
    User->>minirag_query: query string
    minirag_query->>KG: get_types()
    KG-->>minirag_query: TYPE_POOL
    
    minirag_query->>LLM: Extract entities + answer types
    LLM-->>minirag_query: entities_from_query, answer_type_keywords
    
    minirag_query->>EntityNameVDB: query(entity, top_k)
    EntityNameVDB-->>minirag_query: Matched entities
    
    minirag_query->>KG: get_neighbors_within_k_hops(entity, k=2)
    KG-->>minirag_query: Reasoning paths
    
    minirag_query->>KG: get_node_from_types(answer_types)
    KG-->>minirag_query: Candidate answer entities
    
    minirag_query->>minirag_query: cal_path_score_list()
    
    minirag_query->>RelVDB: query(query, top_k)
    RelVDB-->>minirag_query: Relevant edges
    
    minirag_query->>minirag_query: edge_vote_path()
    minirag_query->>minirag_query: path2chunk()
    
    minirag_query->>ChunksVDB: query(query, top_k)
    ChunksVDB-->>minirag_query: Relevant chunk IDs
    
    minirag_query->>minirag_query: kwd2chunk()
    
    minirag_query->>TextChunksDB: get_by_id(chunk_ids)
    TextChunksDB-->>minirag_query: Text chunks
    
    minirag_query->>minirag_query: Build context (CSV format)
    minirag_query->>LLM: Generate response with context
    LLM-->>minirag_query: Final answer
    minirag_query-->>User: Response
```

Sources: [minirag/operate.py:1409-1479]()

### Key Algorithms

The topology-enhanced retrieval uses several specialized algorithms:

| Algorithm | Function | Purpose |
|-----------|----------|---------|
| **Path Scoring** | `cal_path_score_list()` [minirag/utils.py]() | Scores reasoning paths based on entity connections to answer candidates |
| **Edge Voting** | `edge_vote_path()` [minirag/utils.py]() | Votes on edge quality based on entity importance |
| **Path to Chunk** | `path2chunk()` [minirag/operate.py:1124-1209]() | Converts reasoning paths to relevant chunk IDs with scoring |
| **Keyword to Chunk** | `kwd2chunk()` [minirag/operate.py:1220-1249]() | Aggregates chunk scores from multiple entity paths |

### Advantages Over Traditional RAG

The topology-enhanced approach provides several advantages:

1. **Reduced Semantic Load**: Graph structure provides explicit connections without requiring the SLM to infer relationships
2. **Multi-Hop Reasoning**: Natural support for multi-hop queries through k-hop neighbor traversal
3. **Answer Type Guidance**: Uses entity types to guide retrieval toward likely answer entities
4. **Hybrid Scoring**: Combines vector similarity, graph topology, and path voting for robust retrieval

Sources: [minirag/operate.py:1409-1479](), [README.md:31-35]()

## Performance Achievements

MiniRAG's two core innovations enable significant performance improvements while reducing storage requirements.

### Storage Efficiency

MiniRAG achieves **25% storage usage** compared to traditional RAG methods through:

1. **Unified Graph Structure**: Single heterogeneous graph eliminates redundant entity representations
2. **Modular Storage Architecture**: Separate storage backends for different data types avoid duplication
3. **Efficient Entity Indexing**: Named entities stored once with references to source chunks

The storage architecture uses three abstraction layers:

```mermaid
graph TB
    subgraph Application["Application Layer"]
        MiniRAG["MiniRAG Core<br/>minirag.py"]
    end
    
    subgraph Abstractions["Storage Abstractions"]
        BaseGraph["BaseGraphStorage<br/>base.py"]
        BaseVector["BaseVectorStorage<br/>base.py"]
        BaseKV["BaseKVStorage<br/>base.py"]
    end
    
    subgraph Implementations["Concrete Implementations"]
        NetworkX["NetworkXStorage<br/>networkx_impl.py"]
        NanoVector["NanoVectorDBStorage<br/>storage.py"]
        JsonKV["JsonKVStorage<br/>storage.py"]
    end
    
    MiniRAG --> BaseGraph
    MiniRAG --> BaseVector
    MiniRAG --> BaseKV
    
    BaseGraph --> NetworkX
    BaseVector --> NanoVector
    BaseKV --> JsonKV
```

Sources: [README.md:31-35](), [minirag/base.py:1-100]()

### Accuracy Results on LiHua-World Benchmark

MiniRAG demonstrates substantial accuracy improvements across multiple small language models:

#### LiHua-World Dataset Results

| Model | Parameters | NaiveRAG | LightRAG | **MiniRAG** | Improvement |
|-------|------------|----------|----------|-------------|-------------|
| Phi-3.5-mini-instruct | ~3.8B | 41.22% | 39.81% | **53.29%** | +13.48% |
| GLM-Edge-1.5B-Chat | 1.5B | 42.79% | 35.74% | **52.51%** | +16.77% |
| Qwen2.5-3B-Instruct | 3B | 43.73% | 39.18% | **48.75%** | +9.57% |
| MiniCPM3-4B | 4B | 43.42% | 35.42% | **51.25%** | +15.83% |
| gpt-4o-mini | 8B | 46.55% | **56.90%** | 54.08% | -2.82% |

Sources: [README.md:74-82]()

#### MultiHop-RAG Dataset Results

| Model | Parameters | NaiveRAG | LightRAG | **MiniRAG** | Improvement |
|-------|------------|----------|----------|-------------|-------------|
| Phi-3.5-mini-instruct | ~3.8B | 42.72% | 27.03% | **49.96%** | +22.93% |
| GLM-Edge-1.5B-Chat | 1.5B | 44.44% | / | **51.41%** | +6.97% |
| Qwen2.5-3B-Instruct | 3B | 39.48% | 21.91% | **48.55%** | +26.64% |
| MiniCPM3-4B | 4B | 39.24% | 19.48% | **47.77%** | +28.29% |
| gpt-4o-mini | 8B | 53.60% | 64.91% | **68.43%** | +3.52% |

Sources: [README.md:83-88]()

### Key Performance Insights

The performance results demonstrate several important findings:

1. **SLM Performance**: MiniRAG enables SLMs (1.5B-4B parameters) to achieve 48-53% accuracy, comparable to baseline LLM performance
2. **Multi-Hop Superiority**: The topology-enhanced retrieval shows particularly strong improvements on multi-hop reasoning tasks (+23-28%)
3. **GraphRAG Failure**: Traditional GraphRAG fails completely with SLMs (marked as "/" in tables), highlighting the need for MiniRAG's lightweight approach
4. **LLM Competitiveness**: Even with larger models like gpt-4o-mini, MiniRAG remains competitive or superior

### Why MiniRAG Succeeds with Small Models

The success with SLMs stems from the two core innovations:

```mermaid
graph TD
    subgraph SLM_Limitations["SLM Limitations"]
        L1["Limited Semantic<br/>Understanding"]
        L2["Weak Multi-Hop<br/>Reasoning"]
        L3["Small Context<br/>Window"]
    end
    
    subgraph MiniRAG_Solutions["MiniRAG Solutions"]
        S1["Heterogeneous Graph<br/>Explicit Connections"]
        S2["Topology-Enhanced<br/>Graph Traversal"]
        S3["Efficient Context<br/>Selection"]
    end
    
    L1 --> S1
    L2 --> S2
    L3 --> S3
    
    S1 --> R1["Reduces Need for<br/>Semantic Inference"]
    S2 --> R2["Enables Lightweight<br/>Multi-Hop Discovery"]
    S3 --> R3["Provides Relevant<br/>Context Only"]
    
    R1 --> Performance["Strong RAG Performance<br/>with SLMs"]
    R2 --> Performance
    R3 --> Performance
```

Sources: [README.md:30-35](), [README.md:74-88]()

## Storage Efficiency

MiniRAG achieves significant storage efficiency compared to traditional RAG approaches:

- Requires only 25% of the storage space of traditional methods
- Uses modular storage architecture with separate components for different data types
- Minimizes redundancy through the graph structure

```mermaid
classDiagram
    class StorageNameSpace {
        +namespace: str
        +global_config: dict
    }
    
    class BaseVectorStorage {
        +embedding_func
        +query(query, top_k)
        +upsert(data)
    }
    
    class BaseKVStorage {
        +get_by_id(id)
        +upsert(data)
    }
    
    class BaseGraphStorage {
        +get_node(node_id)
        +get_edge(source_id, target_id)
        +upsert_node(node_id, data)
        +upsert_edge(source_id, target_id, data)
    }
    
    StorageNameSpace <|-- BaseVectorStorage
    StorageNameSpace <|-- BaseKVStorage
    StorageNameSpace <|-- BaseGraphStorage
```

The storage architecture includes:

| Storage Type | Purpose | Implementations |
|--------------|---------|----------------|
| Vector Storage | Stores embeddings for chunks and entities | NanoVectorDBStorage |
| Key-Value Storage | Stores original text and metadata | JsonKVStorage |
| Graph Storage | Stores relationships between entities and chunks | NetworkXStorage, Neo4jStorage |
| Document Status Storage | Tracks document processing status | JsonDocStatusStorage |

Sources: [README.md:31]()

## Multi-Database Support

MiniRAG supports integration with multiple heterogeneous graph databases for flexibility in different deployment scenarios:

| Database | Advantages | Implementation |
|----------|------------|----------------|
| Neo4j | Native graph operations, scalable | `neo4j_impl.py` |
| PostgreSQL | Widely available, SQL-based | Extension of graph storage |
| TiDB | Distributed SQL database | Extension of graph storage |
| Oracle | Enterprise-grade reliability | `oracle_impl.py` |
| NetworkX | Simple, in-memory, great for development | Default implementation |

This multi-database support allows users to choose the most appropriate backend based on their existing infrastructure, performance requirements, and deployment constraints.

Sources: [README.md:23](), [README.md:98-104]()

## Performance with Small Language Models

MiniRAG enables small language models to achieve performance comparable to or better than traditional RAG approaches with larger models. The framework has been tested with various SLMs:

| Model | Size | Performance with MiniRAG |
|-------|------|----------------------------|
| Phi-3.5-mini-instruct | ~1.4B parameters | 53.29% accuracy on LiHua-World |
| GLM-Edge-1.5B-Chat | 1.5B parameters | 52.51% accuracy on LiHua-World |
| Qwen2.5-3B-Instruct | 3B parameters | 48.75% accuracy on LiHua-World |
| MiniCPM3-4B | 4B parameters | 51.25% accuracy on LiHua-World |

MiniRAG consistently outperforms NaiveRAG, GraphRAG, and LightRAG across all tested models, especially on multi-hop reasoning tasks.

Sources: [README.md:66-85]()

## Deployment Options

MiniRAG supports multiple deployment options to fit different use cases:

```mermaid
graph TD
    subgraph "Installation Methods"
        SI["Source Installation<br>pip install -e ."]
        PI["PyPI Installation<br>pip install lightrag-hku"]
    end
    
    subgraph "Interface Options"
        CLI["Command Line Interface<br>Step_0_index.py<br>Step_1_QA.py"]
        API["REST API<br>/documents<br>/query"]
        PythonAPI["Python API<br>MiniRAG.insert()<br>MiniRAG.query()"]
    end
    
    subgraph "Deployment Options"
        LD["Local Deployment"]
        DD["Docker Deployment"]
    end
    
    SI --> LD
    PI --> LD
    PI --> DD
    
    LD --> CLI
    LD --> PythonAPI
    DD --> API
```

The flexibility in deployment options makes MiniRAG suitable for a wide range of applications, from development and testing to production systems.

Sources: [README.md:40-47](), [README.md:56-62](), [README.md:25]()

---

# Page: Installation and Setup

# Installation and Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [MANIFEST.in](MANIFEST.in)
- [README.md](README.md)
- [README_JA.md](README_JA.md)
- [pyproject.toml](pyproject.toml)

</details>



This page provides comprehensive instructions for installing and setting up MiniRAG, a lightweight retrieval-augmented generation system. It covers different installation methods, configuration options, and deployment strategies. For details about how to use MiniRAG after installation, see [Usage Examples](#8).

## Prerequisites

Before installing MiniRAG, ensure your system meets the following requirements:

- Python 3.9 or higher
- Sufficient disk space for storage backends
- Pip package manager

```mermaid
flowchart LR
    subgraph "Prerequisites"
        Python["Python 3.9+"]
        PIP["pip"]
        Storage["Storage Space"]
    end
    
    Python --> Ready["Ready for Installation"]
    PIP --> Ready
    Storage --> Ready
```

Sources: [setup.py:59]()

## Installation Options

MiniRAG can be installed in multiple ways, depending on your needs and preferences.

### Installation from Source (Recommended)

Installing from source provides the most up-to-date version of MiniRAG and is recommended for development and experimentation.

```bash
# Clone the repository
git clone https://github.com/HKUDS/MiniRAG
cd MiniRAG

# Install in development mode
pip install -e .
```

### Installation from PyPI

MiniRAG is available on PyPI under the package name `lightrag-hku` (since MiniRAG is based on LightRAG).

```bash
# Install basic version
pip install lightrag-hku

# Install with API support
pip install "lightrag-hku[api]"
```

```mermaid
flowchart TD
    subgraph "Installation Methods"
        Source["Source Installation"]
        PyPI["PyPI Installation"]
    end
    
    Source -->|"pip install -e ."| Dev["Development Environment"]
    PyPI -->|"pip install lightrag-hku"| Basic["Basic Installation"]
    PyPI -->|"pip install 'lightrag-hku[api]'"| API["API-Enabled Installation"]
    
    Dev --> MiniRAG["MiniRAG System"]
    Basic --> MiniRAG
    API --> MiniRAG
    
    MiniRAG --> CLI["Command Line Interface"]
    MiniRAG --> PythonAPI["Python API"]
    API --> RestAPI["REST API Server"]
```

Sources: [README.md:40-52](), [setup.py:40-70]()

## Dependencies

MiniRAG relies on various libraries for different functionality areas. Core dependencies are installed automatically when you install the package.

### Core Dependencies

| Category | Libraries |
|----------|-----------|
| Network & Communication | accelerate, aiofiles, aiohttp, httpx |
| Database | networkx, nltk |
| Core Processing | numpy, pydantic |
| Document Processing | PyPDF2, python-docx, python-pptx |
| LLM Integration | tiktoken |
| Utilities | json_repair, tenacity, tqdm, xxhash |

Additional dependencies for API functionality are installed when using the `[api]` extra.

Sources: [requirements.txt:1-34](), [setup.py:62-64]()

## Configuration

MiniRAG uses a combination of environment variables and configuration files to customize its behavior.

### Environment Variables

Create a `.env` file in your project root with the following variables:

```
# LLM Configuration
LLM_MODEL=gpt-4o-mini  # or any other supported model
LLM_API_KEY=your_api_key_here

# Storage Configuration
VECTOR_DB_PATH=./storage/vector_db
KV_STORAGE_PATH=./storage/kv_storage
GRAPH_STORAGE_PATH=./storage/graph_storage
```

### Configuration File

You can also create a `config.ini` file for more detailed configuration:

```
[Storage]
vector_db_type=nano
kv_storage_type=json
graph_storage_type=networkx

[Indexing]
chunk_size=1000
chunk_overlap=200
```

```mermaid
flowchart LR
    subgraph "Configuration Sources"
        ENV[".env File"]
        CONFIG["config.ini"]
        CLI["Command Line Args"]
    end
    
    ENV --> MiniRAG["MiniRAG Configuration"]
    CONFIG --> MiniRAG
    CLI --> MiniRAG
    
    MiniRAG --> StorageConfig["Storage Configuration"]
    MiniRAG --> ModelConfig["Model Configuration"] 
    MiniRAG --> IndexingConfig["Indexing Configuration"]
    
    StorageConfig --> VDB["Vector DB Settings"]
    StorageConfig --> KV["KV Storage Settings"]
    StorageConfig --> Graph["Graph Storage Settings"]
    
    ModelConfig --> LLM["LLM Selection"]
    ModelConfig --> Embedding["Embedding Models"]
    
    IndexingConfig --> ChunkSettings["Chunking Settings"]
    IndexingConfig --> EntitySettings["Entity Extraction Settings"]
```

Sources: [requirements.txt:4](), [setup.py:24-34]()

## Storage Backend Options

MiniRAG supports multiple storage backends for different components of the system.

### Vector Storage

For storing embeddings and performing vector searches:
- NanoVectorDB (default, lightweight in-memory)
- Other compatible vector databases

### Key-Value Storage

For storing document chunks and metadata:
- JSON files (default, simple file-based storage)
- Other key-value stores

### Graph Storage

For storing the heterogeneous knowledge graph:
- NetworkX (default, in-memory graph)
- Neo4j (for production deployments)
- Oracle
- PostgreSQL
- TiDB

```mermaid
classDiagram
    class StorageNameSpace {
        +namespace: str
        +global_config: dict
    }
    
    class BaseVectorStorage {
        +embedding_func
        +query(query, top_k)
        +upsert(data)
    }
    
    class BaseKVStorage {
        +get_by_id(id)
        +upsert(data)
    }
    
    class BaseGraphStorage {
        +get_node(node_id)
        +get_edge(source_id, target_id)
        +upsert_node(node_id, data)
        +upsert_edge(source_id, target_id, data)
    }
    
    StorageNameSpace <|-- BaseVectorStorage
    StorageNameSpace <|-- BaseKVStorage
    StorageNameSpace <|-- BaseGraphStorage
    
    BaseVectorStorage <|-- NanoVectorDBStorage
    BaseKVStorage <|-- JsonKVStorage
    BaseGraphStorage <|-- NetworkXStorage
    BaseGraphStorage <|-- Neo4jStorage
    BaseGraphStorage <|-- OracleStorage
```

Sources: [README.md:22-23](), [minirag/kg/neo4j_impl.py](), [minirag/kg/oracle_impl.py]()

## Docker Deployment

MiniRAG provides Docker support for containerized deployment, making it easier to set up in production environments.

### Prerequisites for Docker Deployment

- Docker and Docker Compose installed
- Sufficient system resources for containers

### Setting Up with Docker

1. Clone the repository if you haven't already:
   ```bash
   git clone https://github.com/HKUDS/MiniRAG
   cd MiniRAG
   ```

2. Build and run the Docker containers:
   ```bash
   docker-compose up -d
   ```

This will start the MiniRAG API server and any required database containers.

```mermaid
flowchart TD
    subgraph "Docker Deployment"
        Docker["Docker Container"] 
        API["MiniRAG API Server"]
        Storage["Storage Containers"]
    end
    
    Docker --> API
    Docker --> Storage
    
    Storage --> Neo4j["Neo4j Container"]
    Storage --> VectorDB["Vector DB Container"]
    
    API --> |"/documents endpoints"| Indexing["Document Indexing"]
    API --> |"/query endpoints"| Querying["Query Processing"]
    
    User["Client Application"] --> |"HTTP Requests"| API
```

Sources: [README.md:24-25]()

## Verification and Testing

After installation, verify that MiniRAG is working correctly by running a simple test:

```bash
# Navigate to the MiniRAG directory
cd MiniRAG

# Run the indexing example
python reproduce/Step_0_index.py

# Run the Q&A example
python reproduce/Step_1_QA.py
```

If everything is set up correctly, you should see output indicating successful document indexing and query processing.

Sources: [README.md:60-65]()

## Next Steps

After completing the installation and setup, you can:

1. Index your documents following the [Document Indexing](#8.1) guide
2. Start asking questions with [Question Answering](#8.2)
3. Explore advanced configurations and customizations in [Extending MiniRAG](#9)

## Troubleshooting

### Common Installation Issues

- **Dependency conflicts**: Use a virtual environment to avoid conflicts with existing packages
- **Permission errors**: Use `sudo` or administrator privileges when needed, or consider using a user-level installation with `pip install --user`
- **Missing dependencies**: Ensure all required dependencies are installed with `pip install -r requirements.txt`

### Docker Issues

- **Container fails to start**: Check Docker logs with `docker-compose logs`
- **API not responding**: Verify port mappings and network configurations in your Docker Compose file

Sources: [README.md:53-55]()

---

# Page: Installation Options

# Installation Options

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [MANIFEST.in](MANIFEST.in)
- [README.md](README.md)
- [README_JA.md](README_JA.md)
- [pyproject.toml](pyproject.toml)

</details>



This document details the various ways to install and set up MiniRAG in your environment. For configuration options after installation, see [Configuration](#3.2), and for Docker-specific deployment instructions, see [Docker Deployment](#3.3).

MiniRAG provides multiple installation methods to accommodate different use cases, from local development to production deployments. This page covers the prerequisites and steps for each installation option.

## Prerequisites

Before installing MiniRAG, ensure your system meets the following requirements:

- Python 3.9 or higher
- Pip package manager

## Installation Methods Overview

```mermaid
flowchart TD
    Start["Choose Installation Method"]
    Source["Install from Source"]
    PyPI["Install from PyPI"]
    PyPIBasic["Basic Installation"]
    PyPIAPI["Installation with API Support"]
    
    Start --> Source
    Start --> PyPI
    PyPI --> PyPIBasic
    PyPI --> PyPIAPI
    
    Source --> GitClone["Clone Repository:<br>git clone https://github.com/HKUDS/MiniRAG"]
    GitClone --> Navigate["Navigate to Directory:<br>cd MiniRAG"]
    Navigate --> InstallSource["Install Package:<br>pip install -e ."]
    
    PyPIBasic --> InstallBasic["pip install minirag-hku"]
    PyPIAPI --> InstallAPI["pip install \"minirag-hku[api]\""]
    
    InstallSource --> Verify["Verify Installation"]
    InstallBasic --> Verify
    InstallAPI --> Verify
```

Sources: [README.md:40-52](), [setup.py:40-69]()

## Installation from Source (Recommended)

Installing from source is the recommended method as it provides the most up-to-date version of the code and allows for customization.

### Steps:

1. Clone the MiniRAG repository:
   ```bash
   git clone https://github.com/HKUDS/MiniRAG
   ```

2. Navigate to the MiniRAG directory:
   ```bash
   cd MiniRAG
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

This method installs MiniRAG in development mode, which means any changes you make to the source code will be reflected immediately without needing to reinstall the package.

Sources: [README.md:40-47]()

## Installation from PyPI

MiniRAG is available on PyPI under the package name `minirag-hku`, making it easy to install with pip.

### Basic Installation

For basic usage without the API server:

```bash
pip install minirag-hku
```

### Installation with API Support

To include API server functionality:

```bash
pip install "minirag-hku[api]"
```

This installs additional dependencies required for running the RESTful API server.

Sources: [README.md:48-52](), [setup.py:62-64]()

## Package Structure and Components

The installation process makes the following components available:

```mermaid
classDiagram
    class "MiniRAG Package" {
        +Core Components
        +Storage Layer
        +API Components (Optional)
    }
    
    class "Core Components" {
        +base.py
        +minirag.py
        +operate.py
        +prompt.py
        +llm.py
    }
    
    class "Storage Layer" {
        +storage.py
        +kg/*
    }
    
    class "API Components" {
        +api/*
        +minirag-server (CLI Tool)
    }
    
    "MiniRAG Package" --> "Core Components"
    "MiniRAG Package" --> "Storage Layer"
    "MiniRAG Package" --> "API Components"
```

Sources: [README.md:93-128](), [setup.py:48-50]()

## Python Version Compatibility

MiniRAG requires Python 3.9 or higher. This requirement is enforced by the package metadata.

| Python Version | Compatibility |
|----------------|--------------|
| Python 3.9+    | ✓ Supported  |
| Python 3.8     | ✗ Not supported |
| Python 3.7 or lower | ✗ Not supported |

Sources: [setup.py:59](), [pyproject.toml:13]()

## Verifying Installation

After installation, you can verify that MiniRAG was installed correctly by running the example code from the documentation:

```python
from minirag import MiniRAG

# Initialize MiniRAG
minirag = MiniRAG()

# Now you can use MiniRAG for indexing and querying
```

If installed with API support, you can also run the API server using the provided entry point:

```bash
minirag-server
```

Sources: [setup.py:65-69]()

## Installation Options Comparison

| Feature | Source Installation | PyPI Basic | PyPI with API |
|---------|---------------------|------------|---------------|
| Installation Command | `pip install -e .` | `pip install minirag-hku` | `pip install "minirag-hku[api]"` |
| Up-to-date with latest changes | ✓ | Depends on release cycle | Depends on release cycle |
| Source code modifications | ✓ | ✗ | ✗ |
| API server support | Requires manual setup | ✗ | ✓ |
| Suitable for | Development | Basic usage | API deployment |

Sources: [README.md:40-52](), [setup.py:62-69]()

## Package Information

The PyPI package includes the following metadata:

- **Package Name**: minirag-hku
- **Version**: 0.0.2 (as of documentation writing)
- **Author**: Tianyu Fan
- **Python Requirement**: >=3.9
- **License**: MIT License

Sources: [setup.py:40-65](), [pyproject.toml:5-21]()

## Additional Resources

- For package inclusion details, see [MANIFEST.in:1-3]()
- For build system requirements, see [pyproject.toml:1-3]()

---

# Page: Quick Start Guide

# Quick Start Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [reproduce/Step_0_index.py](reproduce/Step_0_index.py)
- [reproduce/Step_1_QA.py](reproduce/Step_1_QA.py)

</details>



This guide walks you through the fastest path to running MiniRAG using the reproduction scripts provided in the repository. You will learn how to index documents into the knowledge graph and perform question-answering queries using either Small Language Models or LLMs.

For installation instructions, see [Installation Options](#2.1). For detailed configuration options beyond the defaults used here, see [Configuration](#2.3). For programmatic usage beyond these scripts, see [Usage Examples](#8).

---

## Overview of the Two-Phase Quick Start

MiniRAG's quick start follows a two-phase pipeline implemented in the reproduction scripts:

```mermaid
graph LR
    subgraph "Phase 1: Indexing"
        Dataset["LiHua-World Dataset<br/>(./dataset/LiHua-World/data)"]
        Step0["Step_0_index.py<br/>(./reproduce)"]
        Index["Knowledge Graph Index<br/>(./LiHua-World)"]
        
        Dataset --> Step0
        Step0 --> Index
    end
    
    subgraph "Phase 2: Query & Evaluation"
        QuerySet["Query Set<br/>(query_set.csv)"]
        Step1["Step_1_QA.py<br/>(./reproduce)"]
        Results["Results CSV<br/>(./logs)"]
        
        Index --> Step1
        QuerySet --> Step1
        Step1 --> Results
    end
    
    style Step0 fill:#f9f9f9
    style Step1 fill:#f9f9f9
```

**Sources:** [README.md:57-68](), [reproduce/Step_0_index.py:1-97](), [reproduce/Step_1_QA.py:1-135]()

---

## Prerequisites and Dataset Preparation

Before running the quick start scripts, ensure you have:

1. **Installed MiniRAG** following [Installation Options](#2.1)
2. **LiHua-World dataset** located at `./dataset/LiHua-World/data/`
3. **Query set** available at `./dataset/LiHua-World/qa/query_set.csv`

The dataset comes pre-packaged in the repository as `LiHuaWorld.zip` and should be extracted before use.

### Directory Structure

```
MiniRAG/
├── dataset/
│   └── LiHua-World/
│       ├── data/              # Text documents (.txt files)
│       └── qa/
│           ├── query_set.csv  # Questions and gold answers
│           └── query_set.json
├── reproduce/
│   ├── Step_0_index.py        # Indexing script
│   └── Step_1_QA.py           # QA script
└── logs/                      # Output directory (created automatically)
```

**Sources:** [README.md:59-61](), [README.md:99-131]()

---

## Phase 1: Document Indexing with Step_0_index.py

### Purpose

`Step_0_index.py` indexes all text documents in the dataset into MiniRAG's heterogeneous graph structure, creating the knowledge base required for subsequent queries.

### Command-Line Arguments

| Argument | Default Value | Description |
|----------|---------------|-------------|
| `--model` | `"PHI"` | LLM model identifier: `"PHI"`, `"GLM"`, `"MiniCPM"`, or `"qwen"` |
| `--workingdir` | `"./LiHua-World"` | Directory where the knowledge graph index will be stored |
| `--datapath` | `"./dataset/LiHua-World/data/"` | Path to the input text documents |
| `--outputpath` | `"./logs/Default_output.csv"` | (Not used in indexing, but accepted for consistency) |
| `--querypath` | `"./dataset/LiHua-World/qa/query_set.csv"` | (Not used in indexing, but accepted for consistency) |

**Sources:** [reproduce/Step_0_index.py:24-34]()

### Running the Indexing Script

```bash
python ./reproduce/Step_0_index.py --model PHI --workingdir ./LiHua-World
```

This command will:
1. Initialize a `MiniRAG` instance with the specified model
2. Recursively find all `.txt` files in the data path
3. Process each file through the insertion pipeline
4. Store the resulting knowledge graph in the working directory

### Step_0_index.py Internal Workflow

```mermaid
graph TB
    Start["Script Start"]
    Args["Parse Arguments<br/>[Step_0_index.py:24-34]()"]
    ModelMap["Map Model Name<br/>[Step_0_index.py:40-50]()"]
    
    subgraph "MiniRAG Initialization"
        CreateRAG["Initialize MiniRAG<br/>[Step_0_index.py:63-78]()"]
        SetLLM["llm_model_func=gpt_4o_mini_complete<br/>[Step_0_index.py:66]()"]
        SetEmbed["embedding_func=EmbeddingFunc<br/>[Step_0_index.py:69-77]()"]
    end
    
    subgraph "Document Discovery"
        FindFiles["find_txt_files(DATA_PATH)<br/>[Step_0_index.py:82-88]()"]
        FileList["List of .txt files<br/>WEEK_LIST"]
    end
    
    subgraph "Indexing Loop"
        Iterate["For each .txt file<br/>[Step_0_index.py:92-96]()"]
        ReadFile["Read file contents<br/>[Step_0_index.py:95]()"]
        Insert["rag.insert(content)<br/>[Step_0_index.py:96]()"]
    end
    
    Storage["Knowledge Graph<br/>Stored in WORKING_DIR"]
    
    Start --> Args
    Args --> ModelMap
    ModelMap --> CreateRAG
    CreateRAG --> SetLLM
    CreateRAG --> SetEmbed
    SetLLM --> FindFiles
    SetEmbed --> FindFiles
    FindFiles --> FileList
    FileList --> Iterate
    Iterate --> ReadFile
    ReadFile --> Insert
    Insert --> Storage
    Insert -.next file.-> Iterate
    
    style Insert fill:#f9f9f9
    style CreateRAG fill:#f9f9f9
```

**Sources:** [reproduce/Step_0_index.py:1-97]()

### Model Selection

The script maps command-line model identifiers to HuggingFace model names:

| `--model` Value | Actual Model Name |
|-----------------|-------------------|
| `"PHI"` | `"microsoft/Phi-3.5-mini-instruct"` |
| `"GLM"` | `"THUDM/glm-edge-1.5b-chat"` |
| `"MiniCPM"` | `"openbmb/MiniCPM3-4B"` |
| `"qwen"` | `"Qwen/Qwen2.5-3B-Instruct"` |

**Note:** For indexing, `Step_0_index.py` uses `gpt_4o_mini_complete` by default at [Step_0_index.py:66](), regardless of the `--model` argument. This is because entity extraction requires more capable language understanding. The specified model will be used during the query phase.

**Sources:** [reproduce/Step_0_index.py:40-50](), [reproduce/Step_0_index.py:66]()

### Expected Output

After successful indexing, you will find the following structure in your working directory:

```
./LiHua-World/
├── graph_chunk_entity_relation.graphml  # Graph structure
├── chunks_vdb/                          # Text chunk embeddings
├── entity_vdb/                          # Entity embeddings
├── entity_name_vdb/                     # Entity name embeddings
├── relationships_vdb/                   # Relationship embeddings
└── doc_status.json                      # Document processing status
```

**Sources:** [reproduce/Step_0_index.py:63-78]()

---

## Phase 2: Question Answering with Step_1_QA.py

### Purpose

`Step_1_QA.py` loads the indexed knowledge graph and evaluates MiniRAG's question-answering performance on the LiHua-World query set, recording results to a CSV file.

### Command-Line Arguments

| Argument | Default Value | Description |
|----------|---------------|-------------|
| `--model` | `"PHI"` | LLM model for query processing: `"PHI"`, `"GLM"`, `"MiniCPM"`, or `"qwen"` |
| `--workingdir` | `"./LiHua-World"` | Directory containing the indexed knowledge graph |
| `--querypath` | `"./dataset/LiHua-World/qa/query_set.csv"` | Path to the query set CSV |
| `--outputpath` | `"./logs/Default_output.csv"` | Output file for recording answers |
| `--datapath` | `"./dataset/LiHua-World/data/"` | (Not used in QA, but accepted for consistency) |

**Sources:** [reproduce/Step_1_QA.py:26-36]()

### Running the QA Script

```bash
python ./reproduce/Step_1_QA.py --model PHI --workingdir ./LiHua-World --outputpath ./logs/PHI_results.csv
```

This command will:
1. Initialize a `MiniRAG` instance with the specified Small Language Model
2. Load the query set from `query_set.csv`
3. Process each question using `mode="mini"` query strategy
4. Record results (Question, Gold Answer, MiniRAG Answer) to the output CSV

### Step_1_QA.py Internal Workflow

```mermaid
graph TB
    Start["Script Start"]
    Args["Parse Arguments<br/>[Step_1_QA.py:26-36]()"]
    ModelMap["Map Model Name<br/>[Step_1_QA.py:42-52]()"]
    
    subgraph "MiniRAG Initialization"
        CreateRAG["Initialize MiniRAG<br/>[Step_1_QA.py:65-80]()"]
        SetLLM["llm_model_func=hf_model_complete<br/>[Step_1_QA.py:67]()"]
        SetEmbed["embedding_func=EmbeddingFunc<br/>[Step_1_QA.py:71-79]()"]
        LoadIndex["Load existing index<br/>from WORKING_DIR"]
    end
    
    subgraph "Query Loading"
        ReadCSV["Read query_set.csv<br/>[Step_1_QA.py:85-89]()"]
        ParseRows["Parse Question + Gold Answer<br/>[Step_1_QA.py:87-89]()"]
        Lists["QUESTION_LIST<br/>GA_LIST"]
    end
    
    subgraph "Experiment Loop"
        CheckResume["Check existing output<br/>[Step_1_QA.py:96-100]()"]
        Resume["Resume from last position<br/>[Step_1_QA.py:102]()"]
        Iterate["For each question<br/>[Step_1_QA.py:110]()"]
        Query["rag.query(QUESTION,<br/>param=QueryParam(mode='mini'))<br/>[Step_1_QA.py:118-122]()"]
        HandleError["Error handling<br/>[Step_1_QA.py:123-125]()"]
        WriteRow["Write to CSV<br/>[Step_1_QA.py:127]()"]
    end
    
    Output["Results CSV File"]
    
    Start --> Args
    Args --> ModelMap
    ModelMap --> CreateRAG
    CreateRAG --> SetLLM
    CreateRAG --> SetEmbed
    CreateRAG --> LoadIndex
    LoadIndex --> ReadCSV
    ReadCSV --> ParseRows
    ParseRows --> Lists
    Lists --> CheckResume
    CheckResume --> Resume
    Resume --> Iterate
    Iterate --> Query
    Query --> WriteRow
    Query --> HandleError
    HandleError --> WriteRow
    WriteRow --> Output
    WriteRow -.next question.-> Iterate
    
    style Query fill:#f9f9f9
    style CreateRAG fill:#f9f9f9
```

**Sources:** [reproduce/Step_1_QA.py:1-135]()

### Resume Capability

The script supports resuming interrupted experiments. If the output file already exists, it:
1. Reads previously processed questions at [Step_1_QA.py:96-100]()
2. Counts completed rows at [Step_1_QA.py:102]()
3. Continues from the next unprocessed question at [Step_1_QA.py:110]()

This allows you to safely interrupt and restart long-running evaluations.

**Sources:** [reproduce/Step_1_QA.py:96-103]()

### Query Processing

Each question is processed using the **"mini" query mode**, which leverages MiniRAG's topology-enhanced retrieval:

```python
minirag_answer = rag.query(QUESTION, param=QueryParam(mode="mini"))
```

The `mode="mini"` parameter activates:
- Entity extraction from the query
- Graph traversal for reasoning paths
- Lightweight knowledge discovery
- Context-aware answer generation

For details on other query modes, see [Query Modes](#4.3).

**Sources:** [reproduce/Step_1_QA.py:118-122]()

### Output Format

The script generates a CSV file with the following columns:

| Column | Description |
|--------|-------------|
| `Question` | Original query from query_set.csv |
| `Gold Answer` | Human-annotated correct answer |
| `minirag` | Answer generated by MiniRAG |

Example output:

```csv
Question,Gold Answer,minirag
"Who is LiHua's best friend?","Zhang Wei","According to the context, LiHua's best friend is Zhang Wei..."
"What did LiHua do last weekend?","Visited the museum","LiHua visited the museum with friends last weekend..."
```

**Sources:** [reproduce/Step_1_QA.py:93](), [reproduce/Step_1_QA.py:127]()

---

## Complete End-to-End Workflow

The following diagram illustrates how the two scripts interact with MiniRAG's core components:

```mermaid
sequenceDiagram
    participant User
    participant Step0 as Step_0_index.py
    participant Step1 as Step_1_QA.py
    participant MiniRAG as MiniRAG Instance
    participant Storage as Storage Layer
    participant LLM as Language Models
    
    rect rgb(245, 245, 245)
        Note over User,LLM: Phase 1: Indexing
        User->>Step0: python Step_0_index.py
        Step0->>Step0: Parse arguments [24-34]()
        Step0->>Step0: find_txt_files() [82-88]()
        Step0->>MiniRAG: Initialize with gpt_4o_mini [63-78]()
        MiniRAG->>Storage: Create graph/vector/KV stores
        
        loop For each .txt file
            Step0->>Step0: Read file content [95]()
            Step0->>MiniRAG: rag.insert(content) [96]()
            MiniRAG->>LLM: Extract entities & relationships
            LLM-->>MiniRAG: Extracted entities
            MiniRAG->>Storage: Store in heterogeneous graph
        end
        
        Storage-->>User: Index stored in WORKING_DIR
    end
    
    rect rgb(250, 250, 250)
        Note over User,LLM: Phase 2: Question Answering
        User->>Step1: python Step_1_QA.py
        Step1->>Step1: Parse arguments [26-36]()
        Step1->>Step1: Load query_set.csv [85-89]()
        Step1->>MiniRAG: Initialize with SLM [65-80]()
        MiniRAG->>Storage: Load existing index
        
        loop For each question
            Step1->>MiniRAG: rag.query(Q, mode="mini") [118-122]()
            MiniRAG->>Storage: Retrieve reasoning paths
            Storage-->>MiniRAG: Graph context + chunks
            MiniRAG->>LLM: Generate answer with SLM
            LLM-->>MiniRAG: Final answer
            MiniRAG-->>Step1: Answer string
            Step1->>Step1: Write to output CSV [127]()
        end
        
        Step1-->>User: Results CSV generated
    end
```

**Sources:** [reproduce/Step_0_index.py:1-97](), [reproduce/Step_1_QA.py:1-135]()

---

## Common Quick Start Scenarios

### Scenario 1: Basic Evaluation with Phi-3.5

```bash
# Step 1: Index the dataset
python ./reproduce/Step_0_index.py --model PHI --workingdir ./workdir_phi

# Step 2: Run QA evaluation
python ./reproduce/Step_1_QA.py --model PHI --workingdir ./workdir_phi --outputpath ./logs/phi_results.csv
```

### Scenario 2: Testing Multiple Models

```bash
# Index once (uses gpt-4o-mini for entity extraction)
python ./reproduce/Step_0_index.py --workingdir ./shared_index

# Evaluate with different SLMs
python ./reproduce/Step_1_QA.py --model PHI --workingdir ./shared_index --outputpath ./logs/phi.csv
python ./reproduce/Step_1_QA.py --model GLM --workingdir ./shared_index --outputpath ./logs/glm.csv
python ./reproduce/Step_1_QA.py --model qwen --workingdir ./shared_index --outputpath ./logs/qwen.csv
python ./reproduce/Step_1_QA.py --model MiniCPM --workingdir ./shared_index --outputpath ./logs/minicpm.csv
```

### Scenario 3: Custom Dataset

```bash
# Place your .txt files in a custom directory
mkdir -p ./dataset/MyData/

# Index your data
python ./reproduce/Step_0_index.py --datapath ./dataset/MyData/ --workingdir ./MyData_index

# Query with your own questions (modify Step_1_QA.py or use main.py)
```

**Sources:** [README.md:64-68]()

---

## Key Configuration Points

Both scripts share critical configuration that connects to MiniRAG's core functionality:

### Embedding Configuration

```python
embedding_func=EmbeddingFunc(
    embedding_dim=384,
    max_token_size=1000,
    func=lambda texts: hf_embed(
        texts,
        tokenizer=AutoTokenizer.from_pretrained(EMBEDDING_MODEL),
        embed_model=AutoModel.from_pretrained(EMBEDDING_MODEL)
    )
)
```

- Uses `sentence-transformers/all-MiniLM-L6-v2` for embeddings
- 384-dimensional vectors for efficient storage
- Maximum 1000 tokens per text chunk

**Sources:** [reproduce/Step_0_index.py:19](), [reproduce/Step_0_index.py:69-77](), [reproduce/Step_1_QA.py:21](), [reproduce/Step_1_QA.py:71-79]()

### LLM Model Functions

| Script | LLM Function | Purpose |
|--------|--------------|---------|
| `Step_0_index.py` | `gpt_4o_mini_complete` | Entity extraction (requires strong understanding) |
| `Step_1_QA.py` | `hf_model_complete` | Answer generation with Small Language Models |

**Sources:** [reproduce/Step_0_index.py:66](), [reproduce/Step_1_QA.py:67]()

### Token Limits

```python
llm_model_max_token_size=200
```

Both scripts use a 200-token limit for generated responses, balancing answer quality with generation speed.

**Sources:** [reproduce/Step_0_index.py:69](), [reproduce/Step_1_QA.py:69]()

---

## Troubleshooting

### Issue: ModuleNotFoundError

**Symptom:** `ModuleNotFoundError: No module named 'minirag'`

**Solution:** Ensure you've installed MiniRAG following [Installation Options](#2.1). The scripts add the parent directory to `sys.path` at [Step_0_index.py:8]() and [Step_1_QA.py:8]().

### Issue: HuggingFace Authentication

**Symptom:** Cannot download gated models

**Solution:** Uncomment and configure the login token at the top of both scripts:

```python
from huggingface_hub import login
your_token = "INPUT YOUR TOKEN HERE"
login(your_token)
```

**Sources:** [reproduce/Step_0_index.py:1-3](), [reproduce/Step_1_QA.py:1-3]()

### Issue: Out of Memory

**Symptom:** CUDA out of memory errors during processing

**Solution:** 
- Reduce batch size in embedding generation
- Use CPU instead of GPU
- Process documents in smaller batches

### Issue: Dataset Not Found

**Symptom:** `FileNotFoundError` when accessing dataset

**Solution:** Ensure the LiHua-World dataset is extracted:
```bash
cd ./dataset/LiHua-World/data/
unzip LiHuaWorld.zip
```

**Sources:** [README.md:59-61]()

---

## Next Steps

After completing this quick start:

1. **Understand Configuration:** Read [Configuration](#2.3) to customize query parameters, chunk sizes, and model settings
2. **Explore Query Modes:** Learn about different retrieval strategies in [Query Modes](#4.3)
3. **Evaluate Performance:** Analyze your results against the benchmark in [Evaluation Methodology](#7.3)
4. **Custom Integration:** See [Usage Examples](#8) for programmatic usage beyond the reproduction scripts

For the underlying technical concepts, see [Heterogeneous Graph Indexing](#4.1) and [Topology-Enhanced Retrieval](#4.2).

**Sources:** [README.md:1-174]()

---

# Page: Configuration

# Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [main.py](main.py)
- [minirag/__init__.py](minirag/__init__.py)
- [minirag/base.py](minirag/base.py)
- [minirag/prompt.py](minirag/prompt.py)

</details>



This page documents the configuration system in MiniRAG, covering query-time parameters, initialization settings, and environment variables. Configuration in MiniRAG is divided into two main categories: **QueryParam** settings that control query behavior at runtime, and **MiniRAG initialization** parameters that set up storage, models, and working directories.

For information about storage backend implementations and their specific configuration, see [Storage Implementations](#5). For details on LLM and embedding model integration, see [LLM and Embedding Integration](#6).

---

## Overview of Configuration Architecture

MiniRAG uses a two-tier configuration approach: initialization-time configuration establishes the system's infrastructure, while query-time configuration customizes retrieval and generation behavior.

**Configuration Flow: Environment to Runtime**

```mermaid
graph TB
    subgraph "Configuration Sources"
        ENV["Environment Variables<br/>TOP_K, etc."]
        CODE["Code Initialization<br/>main.py"]
        RUNTIME["Runtime Parameters<br/>query() calls"]
    end
    
    subgraph "Configuration Objects"
        QueryParam["QueryParam dataclass<br/>minirag/base.py:18-45"]
        MiniRAGInit["MiniRAG.__init__()<br/>working_dir, models, etc."]
    end
    
    subgraph "System Components"
        Storage["Storage Layer<br/>Graph, Vector, KV"]
        LLM["LLM Interface<br/>Model completion"]
        Embedding["Embedding Function<br/>Vector generation"]
        QueryEngine["Query Engine<br/>minirag_query()"]
    end
    
    ENV --> QueryParam
    CODE --> MiniRAGInit
    RUNTIME --> QueryParam
    
    MiniRAGInit --> Storage
    MiniRAGInit --> LLM
    MiniRAGInit --> Embedding
    
    QueryParam --> QueryEngine
    LLM --> QueryEngine
    Embedding --> Storage
    Storage --> QueryEngine
```

**Sources:** [minirag/base.py:18-45](), [main.py:58-72]()

---

## QueryParam Configuration

The `QueryParam` dataclass defines all query-time configuration parameters. These settings control retrieval strategy, context size, response format, and other runtime behaviors.

### Core Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | `Literal["light", "naive", "mini"]` | `"mini"` | Query mode selection (see [Query Modes](#4.3)) |
| `only_need_context` | `bool` | `False` | Return only retrieved context without LLM generation |
| `only_need_prompt` | `bool` | `False` | Return only the formatted prompt without execution |
| `response_type` | `str` | `"Multiple Paragraphs"` | Desired format of generated response |
| `stream` | `bool` | `False` | Enable streaming response generation |

**Sources:** [minirag/base.py:18-24]()

### Retrieval Configuration

The following parameters control the scope and size of retrieved context:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `top_k` | `int` | `60` (from `TOP_K` env var) | Number of top entities/relationships to retrieve |
| `max_token_for_text_unit` | `int` | `4000` | Maximum tokens for original text chunks |
| `max_token_for_global_context` | `int` | `4000` | Maximum tokens for relationship descriptions |
| `max_token_for_local_context` | `int` | `4000` | Maximum tokens for entity descriptions |
| `max_token_for_node_context` | `int` | `500` | Maximum tokens per node (critical for SLMs) |

**Sources:** [minirag/base.py:25-35]()

The `max_token_for_node_context` parameter is particularly important for Small Language Models, as noted in the comment at line 35: "For Mini, if too long, SLM may fail to generate any response."

### Keyword and History Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `hl_keywords` | `list[str]` | `[]` | High-level keywords for query expansion |
| `ll_keywords` | `list[str]` | `[]` | Low-level keywords for entity matching |
| `conversation_history` | `list[dict]` | `[]` | Previous conversation turns for context |
| `history_turns` | `int` | `3` | Number of conversation pairs to consider |

**Sources:** [minirag/base.py:37-45]()

The `conversation_history` list should contain dictionaries with `"role"` (either `"user"` or `"assistant"`) and `"content"` keys.

**QueryParam Field Mapping to Query Modes**

```mermaid
graph LR
    subgraph "QueryParam Fields"
        mode["mode<br/>mini/light/naive"]
        top_k["top_k<br/>Entity count"]
        max_text["max_token_for_text_unit"]
        max_global["max_token_for_global_context"]
        max_local["max_token_for_local_context"]
        max_node["max_token_for_node_context"]
    end
    
    subgraph "Query Mode: naive"
        naive_vec["Vector Search Only"]
        naive_chunks["Text Chunks"]
    end
    
    subgraph "Query Mode: light"
        light_entity["Entity-Centric Retrieval"]
        light_desc["Entity Descriptions"]
    end
    
    subgraph "Query Mode: mini"
        mini_topo["Topology-Enhanced Retrieval"]
        mini_paths["Reasoning Paths"]
        mini_nodes["Node Context"]
    end
    
    mode -->|"naive"| naive_vec
    top_k --> naive_vec
    max_text --> naive_chunks
    
    mode -->|"light"| light_entity
    top_k --> light_entity
    max_local --> light_desc
    
    mode -->|"mini"| mini_topo
    top_k --> mini_topo
    max_node --> mini_nodes
    max_local --> mini_paths
```

**Sources:** [minirag/base.py:18-45]()

---

## MiniRAG Initialization Configuration

The `MiniRAG` class constructor accepts parameters that establish the system's core infrastructure. These settings cannot be changed after initialization without creating a new instance.

### Initialization Parameters

**MiniRAG Initialization Parameter Structure**

```mermaid
graph TB
    subgraph "Core Parameters"
        working_dir["working_dir: str<br/>Storage location"]
        llm_model_func["llm_model_func: callable<br/>LLM completion function"]
        llm_model_name["llm_model_name: str<br/>Model identifier"]
        llm_max_tokens["llm_model_max_token_size: int<br/>Output token limit"]
    end
    
    subgraph "Embedding Configuration"
        embed_func["embedding_func: EmbeddingFunc"]
        embed_dim["embedding_dim: int"]
        embed_max["max_token_size: int"]
        embed_callable["func: callable"]
    end
    
    subgraph "Storage Backends"
        graph_db["Graph Storage<br/>BaseGraphStorage"]
        vector_db["Vector Storage<br/>BaseVectorStorage"]
        kv_db["KV Storage<br/>BaseKVStorage"]
    end
    
    working_dir --> graph_db
    working_dir --> vector_db
    working_dir --> kv_db
    
    llm_model_func --> llm_model_name
    llm_model_name --> llm_max_tokens
    
    embed_func --> embed_dim
    embed_func --> embed_max
    embed_func --> embed_callable
    
    embed_func --> vector_db
```

**Sources:** [main.py:58-72]()

### Working Directory Configuration

The `working_dir` parameter specifies the base directory for all persistent storage:

```python
working_dir = "./LiHua-World"  # Example from main.py:47
```

MiniRAG creates subdirectories within this path for different storage backends (graph database, vector databases, key-value stores). The directory structure is managed automatically.

**Sources:** [main.py:47,58-72]()

### LLM Configuration

Three parameters control the language model integration:

1. **`llm_model_func`**: A callable that performs model completion. Common options:
   - `hf_model_complete` for HuggingFace models
   - `openai_complete` for OpenAI API models
   - Custom functions matching the expected signature

2. **`llm_model_name`**: String identifier for the model, examples:
   - `"microsoft/Phi-3.5-mini-instruct"`
   - `"THUDM/glm-edge-1.5b-chat"`
   - `"openbmb/MiniCPM3-4B"`
   - `"Qwen/Qwen2.5-3B-Instruct"`

3. **`llm_model_max_token_size`**: Maximum tokens for model output (e.g., `200`)

**Sources:** [main.py:35-72]()

### Embedding Function Configuration

The `embedding_func` parameter accepts an `EmbeddingFunc` dataclass instance with three fields:

```python
EmbeddingFunc(
    embedding_dim=384,           # Dimensionality of embedding vectors
    max_token_size=1000,        # Maximum tokens to embed at once
    func=lambda texts: ...      # Actual embedding function
)
```

**Sources:** [main.py:63-71](), [minirag/utils.py (EmbeddingFunc)]()

---

## Environment Variables

MiniRAG supports configuration via environment variables, which provide system-wide defaults.

| Variable | Type | Default | Usage | Code Reference |
|----------|------|---------|-------|----------------|
| `TOP_K` | `int` | `60` | Default number of entities to retrieve | [minirag/base.py:25]() |

Additional environment variables may be used by specific storage backends or LLM providers.

**Sources:** [minirag/base.py:25]()

---

## Configuration Examples

### Example 1: Basic HuggingFace Configuration

This example demonstrates configuring MiniRAG with a Small Language Model from HuggingFace:

```python
from minirag import MiniRAG, QueryParam
from minirag.llm.hf import hf_model_complete, hf_embed
from minirag.utils import EmbeddingFunc
from transformers import AutoModel, AutoTokenizer

# Initialize MiniRAG with Phi-3.5 model
rag = MiniRAG(
    working_dir="./my_knowledge_base",
    llm_model_func=hf_model_complete,
    llm_model_max_token_size=200,
    llm_model_name="microsoft/Phi-3.5-mini-instruct",
    embedding_func=EmbeddingFunc(
        embedding_dim=384,
        max_token_size=1000,
        func=lambda texts: hf_embed(
            texts,
            tokenizer=AutoTokenizer.from_pretrained(
                "sentence-transformers/all-MiniLM-L6-v2"
            ),
            embed_model=AutoModel.from_pretrained(
                "sentence-transformers/all-MiniLM-L6-v2"
            ),
        ),
    ),
)

# Query with custom parameters
response = rag.query(
    "What is the capital of France?",
    param=QueryParam(
        mode="mini",
        top_k=50,
        max_token_for_node_context=400,
    )
)
```

**Sources:** [main.py:35-72,93-96]()

### Example 2: Model Selection via Command-Line

The main.py script demonstrates a pattern for selecting models dynamically:

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str, default="PHI")
args = parser.parse_args()

# Map model names to HuggingFace identifiers
model_map = {
    "PHI": "microsoft/Phi-3.5-mini-instruct",
    "GLM": "THUDM/glm-edge-1.5b-chat",
    "MiniCPM": "openbmb/MiniCPM3-4B",
    "qwen": "Qwen/Qwen2.5-3B-Instruct",
}

llm_model_name = model_map.get(args.model)
```

**Sources:** [main.py:19-46]()

### Example 3: Query Mode Comparison

Different query modes require different QueryParam configurations:

```python
# Naive mode: Simple vector search
naive_result = rag.query(
    query,
    param=QueryParam(
        mode="naive",
        top_k=10,  # Fewer chunks needed
        max_token_for_text_unit=2000,
    )
)

# Light mode: Entity-centric retrieval
light_result = rag.query(
    query,
    param=QueryParam(
        mode="light",
        top_k=60,
        max_token_for_local_context=4000,  # Entity descriptions
    )
)

# Mini mode: Topology-enhanced retrieval (recommended for SLMs)
mini_result = rag.query(
    query,
    param=QueryParam(
        mode="mini",
        top_k=60,
        max_token_for_node_context=500,  # Critical for SLMs
        max_token_for_local_context=4000,
    )
)
```

**Sources:** [minirag/base.py:19]()

### Example 4: Context-Only Retrieval

For debugging or custom generation pipelines, retrieve context without LLM generation:

```python
context = rag.query(
    "What technologies does the company use?",
    param=QueryParam(
        mode="mini",
        only_need_context=True,  # Skip LLM generation
        top_k=40,
    )
)

# `context` contains the retrieved graph paths and text chunks
# Process it with custom logic or a different LLM
```

**Sources:** [minirag/base.py:20]()

### Example 5: Conversation History Configuration

Enable multi-turn conversations by providing history:

```python
# Build conversation history
history = [
    {"role": "user", "content": "What is MiniRAG?"},
    {"role": "assistant", "content": "MiniRAG is a RAG system for SLMs..."},
    {"role": "user", "content": "How does it compare to GraphRAG?"},
    {"role": "assistant", "content": "MiniRAG uses less storage..."},
]

# Query with conversation context
response = rag.query(
    "Can you elaborate on the storage efficiency?",
    param=QueryParam(
        mode="mini",
        conversation_history=history,
        history_turns=2,  # Use last 2 complete turns
    )
)
```

**Sources:** [minirag/base.py:40-45]()

---

## Configuration Best Practices

### Token Limits for Small Language Models

When using Small Language Models (1.5B-4B parameters), carefully tune token limits:

- **`max_token_for_node_context=500`**: Default is appropriate for most SLMs
- Reduce `max_token_for_local_context` and `max_token_for_global_context` if the model produces empty responses
- Increase `llm_model_max_token_size` cautiously; SLMs may fail with very long outputs

**Sources:** [minirag/base.py:35]()

### Top-K Selection

The `top_k` parameter significantly impacts retrieval quality and performance:

| Query Complexity | Recommended `top_k` | Rationale |
|------------------|---------------------|-----------|
| Simple, single-hop | 20-40 | Fewer entities needed |
| Multi-hop reasoning | 60-80 | More paths to explore |
| Summarization | 40-60 | Broader context coverage |

**Sources:** [minirag/base.py:25]()

### Working Directory Structure

Ensure the working directory has sufficient space and appropriate permissions. MiniRAG creates the directory automatically if it doesn't exist:

```python
import os
working_dir = "./data/minirag"
if not os.path.exists(working_dir):
    os.makedirs(working_dir)  # Or use os.mkdir for single level
```

**Sources:** [main.py:55-56]()

---

## Configuration Validation

MiniRAG performs minimal validation at initialization and query time. Consider implementing validation for:

1. **Valid mode strings**: Ensure `mode` is one of `"naive"`, `"light"`, `"mini"`
2. **Token limits**: Verify token parameters are positive integers
3. **Working directory**: Check for write permissions before initialization
4. **Model compatibility**: Ensure embedding dimensions match vector storage expectations

**Sources:** [minirag/base.py:18-45]()

---

# Page: System Architecture

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [minirag/kg/weaviate_impl.py](minirag/kg/weaviate_impl.py)
- [minirag/minirag.py](minirag/minirag.py)
- [tests/test_weaviate.py](tests/test_weaviate.py)

</details>



This document provides an overview of the MiniRAG system architecture. It explains the high-level design, key components, and how they interact to provide retrieval-augmented generation capabilities optimized for small language models (SLMs). For details about specific components, see [Core Components](#2.1), [Data Flow](#2.2), and [Storage Layer](#2.3).

## High-Level Architecture Overview

The MiniRAG system is built with a modular architecture that separates concerns across several logical layers while providing flexibility through pluggable components.

### System Architecture Diagram

```mermaid
graph TD
    subgraph "Core Components"
        MiniRAGClass["MiniRAG Class"]
        IndexingPipeline["Indexing Pipeline"]
        QueryPipeline["Query Pipeline"]
    end
    
    subgraph "Storage Layer"
        KVStorage["BaseKVStorage"]
        VectorStorage["BaseVectorStorage"]
        GraphStorage["BaseGraphStorage"]
        DocStatusStorage["DocStatusStorage"]
    end
    
    subgraph "External Components"
        LLM["Language Models"]
        EmbeddingModels["Embedding Models"]
    end
    
    InputDocs["Input Documents"] --> IndexingPipeline
    UserQuery["User Query"] --> QueryPipeline
    
    IndexingPipeline --> KVStorage
    IndexingPipeline --> VectorStorage
    IndexingPipeline --> GraphStorage
    IndexingPipeline --> DocStatusStorage
    
    QueryPipeline --> KVStorage
    QueryPipeline --> VectorStorage
    QueryPipeline --> GraphStorage
    
    IndexingPipeline --> EmbeddingModels
    QueryPipeline --> EmbeddingModels
    QueryPipeline --> LLM
    
    MiniRAGClass --> IndexingPipeline
    MiniRAGClass --> QueryPipeline
```

Sources: [minirag/minirag.py:119-607](), [minirag/base.py:49-149]()

## Architecture Design Principles

MiniRAG is built on several key architectural principles:

1. **Modular Design**: The system is composed of interchangeable components that can be swapped without affecting the overall functionality.

2. **Storage Abstraction**: All storage operations are performed through abstract interfaces that allow multiple backend implementations.

3. **Workflow Separation**: Document processing and query processing follow separate, well-defined workflows.

4. **Extensibility**: The system can be extended with new storage backends, embedding models, and language models.

5. **Heterogeneous Graph Indexing**: Documents are processed into a graph structure that connects text chunks with entities and their relationships.

6. **Multi-Mode Querying**: Support for different retrieval strategies (light, naive, mini) to optimize for different use cases.

### Storage System Design

```mermaid
classDiagram
    class StorageNameSpace {
        +namespace: str
        +global_config: dict
        +index_done_callback()
        +query_done_callback()
    }
    
    class BaseVectorStorage {
        +embedding_func: EmbeddingFunc
        +query(query, top_k)
        +upsert(data)
    }
    
    class BaseKVStorage {
        +get_by_id(id)
        +get_by_ids(ids)
        +filter_keys(data)
        +upsert(data)
    }
    
    class BaseGraphStorage {
        +get_node(node_id)
        +get_edge(source_id, target_id)
        +upsert_node(node_id, data)
        +upsert_edge(source_id, target_id, data)
    }
    
    class DocStatusStorage {
        +get_status_counts()
        +get_failed_docs()
        +get_pending_docs()
    }
    
    StorageNameSpace <|-- BaseVectorStorage
    StorageNameSpace <|-- BaseKVStorage
    StorageNameSpace <|-- BaseGraphStorage
    BaseKVStorage <|-- DocStatusStorage
```

Sources: [minirag/base.py:49-197]()

## Component Interaction in Key Workflows

### Document Indexing Workflow

The document indexing workflow processes input documents into a queryable knowledge base:

```mermaid
sequenceDiagram
    participant Client
    participant MiniRAG
    participant Chunking
    participant EntityExtraction
    participant Storage
    
    Client->>MiniRAG: insert(documents)
    MiniRAG->>MiniRAG: apipeline_enqueue_documents()
    MiniRAG->>Storage: Store document status as PENDING
    MiniRAG->>MiniRAG: apipeline_process_enqueue_documents()
    
    loop For each document
        MiniRAG->>Chunking: chunking_func(document)
        Chunking-->>MiniRAG: document chunks
        MiniRAG->>Storage: Store chunks in chunks_vdb and text_chunks
        MiniRAG->>Storage: Update document status to PROCESSED
    end
    
    MiniRAG->>EntityExtraction: extract_entities(chunks)
    EntityExtraction->>Storage: Store entities in entities_vdb
    EntityExtraction->>Storage: Store relationships in relationships_vdb
    EntityExtraction->>Storage: Build graph in chunk_entity_relation_graph
    
    MiniRAG->>MiniRAG: _insert_done()
    MiniRAG->>Storage: Finalize storage operations
    MiniRAG-->>Client: Done
```

Sources: [minirag/minirag.py:336-385](), [minirag/minirag.py:387-446](), [minirag/minirag.py:447-511]()

### Query Processing Workflow

The query processing workflow retrieves relevant information and generates responses:

```mermaid
sequenceDiagram
    participant Client
    participant MiniRAG
    participant QueryProcessor
    participant Storage
    participant LLM
    
    Client->>MiniRAG: query(query, param)
    
    alt param.mode == "light"
        MiniRAG->>QueryProcessor: hybrid_query()
    else param.mode == "mini"
        MiniRAG->>QueryProcessor: minirag_query()
    else param.mode == "naive"
        MiniRAG->>QueryProcessor: naive_query()
    end
    
    QueryProcessor->>Storage: Retrieve relevant information
    Storage-->>QueryProcessor: Retrieved context
    
    QueryProcessor->>LLM: Generate response with context
    LLM-->>QueryProcessor: Generated response
    
    QueryProcessor-->>MiniRAG: Response
    MiniRAG->>MiniRAG: _query_done()
    MiniRAG-->>Client: Response
```

Sources: [minirag/minirag.py:529-576]()

## Key Classes and Their Roles

### MiniRAG Class

The `MiniRAG` class serves as the main entry point and orchestrator for the entire system:

```mermaid
classDiagram
    class MiniRAG {
        +working_dir: str
        +kv_storage: str
        +vector_storage: str
        +graph_storage: str
        +doc_status_storage: str
        +embedding_func: EmbeddingFunc
        +llm_model_func: callable
        +insert(string_or_strings): None
        +query(query, param): str
        +ainsert(input, split_by_character, split_by_character_only, ids): None
        +aquery(query, param): str
        -_get_storage_class(storage_name): dict
        -apipeline_enqueue_documents(input, ids): None
        -apipeline_process_enqueue_documents(split_by_character, split_by_character_only): None
    }
```

The `MiniRAG` class is responsible for:

1. **System Initialization**: Setting up storage instances and processing pipelines
2. **Document Processing**: Managing the document indexing workflow
3. **Query Processing**: Handling user queries and generating responses
4. **Storage Management**: Coordinating operations across multiple storage backends

Sources: [minirag/minirag.py:119-607]()

### Storage Component Initialization

During initialization, `MiniRAG` creates multiple storage instances:

```mermaid
flowchart TD
    MiniRAG["MiniRAG.__post_init__()"] --> KV["Create KV Storage"]
    MiniRAG --> Vector["Create Vector Storage"]
    MiniRAG --> Graph["Create Graph Storage"]
    MiniRAG --> DocStatus["Create DocStatus Storage"]
    
    KV --> full_docs["full_docs: key_string_value_json_storage_cls"]
    KV --> text_chunks["text_chunks: key_string_value_json_storage_cls"]
    KV --> llm_response_cache["llm_response_cache: key_string_value_json_storage_cls"]
    
    Vector --> entities_vdb["entities_vdb: vector_db_storage_cls"]
    Vector --> entity_name_vdb["entity_name_vdb: vector_db_storage_cls"]
    Vector --> relationships_vdb["relationships_vdb: vector_db_storage_cls"]
    Vector --> chunks_vdb["chunks_vdb: vector_db_storage_cls"]
    
    Graph --> chunk_entity_relation_graph["chunk_entity_relation_graph: graph_storage_cls"]
    
    DocStatus --> doc_status["doc_status: doc_status_storage_cls"]
```

Sources: [minirag/minirag.py:186-308]()

### Query Parameter Configuration

The `QueryParam` class configures how queries are processed:

```mermaid
classDiagram
    class QueryParam {
        +mode: Literal["light", "naive", "mini"]
        +only_need_context: bool
        +only_need_prompt: bool
        +response_type: str
        +stream: bool
        +top_k: int
        +max_token_for_text_unit: int
        +max_token_for_global_context: int
        +max_token_for_local_context: int
        +max_token_for_node_context: int
        +hl_keywords: list[str]
        +ll_keywords: list[str]
        +conversation_history: list[dict]
        +history_turns: int
    }
```

The `QueryParam` class controls:

1. **Query Mode**: Determines which retrieval strategy to use
2. **Response Format**: Configures the response format and token limits
3. **Retrieval Parameters**: Sets parameters for retrieval, such as number of items to retrieve
4. **Context Control**: Controls how much context to include in the prompt

Sources: [minirag/base.py:18-46]()

### Storage System Implementation

The storage system is based on abstract base classes with multiple concrete implementations:

| Storage Type | Base Class | Available Implementations |
|--------------|------------|---------------------------|
| Vector Storage | `BaseVectorStorage` | NanoVectorDBStorage, ChromaVectorDBStorage, OracleVectorDBStorage, TiDBVectorDBStorage, MilvusVectorDBStorage, PGVectorStorage |
| Key-Value Storage | `BaseKVStorage` | JsonKVStorage, OracleKVStorage, MongoKVStorage, RedisKVStorage, TiDBKVStorage, PGKVStorage |
| Graph Storage | `BaseGraphStorage` | NetworkXStorage, Neo4JStorage, OracleGraphStorage, MongoGraphStorage, TiDBGraphStorage, PGGraphStorage, AGEStorage, GremlinStorage |
| Document Status Storage | `DocStatusStorage` | JsonDocStatusStorage, PGDocStatusStorage |

The storage implementations are dynamically loaded using a lazy import mechanism:

```python
def _get_storage_class(self, storage_name: str) -> dict:
    import_path = STORAGES[storage_name]
    storage_class = lazy_external_import(import_path, storage_name)
    return storage_class
```

Sources: [minirag/minirag.py:39-62](), [minirag/minirag.py:311-314]()

## Summary

The MiniRAG system architecture is built on a modular design with clear separation of concerns. The system is centered around the `MiniRAG` class, which orchestrates the interaction between various components. The storage layer provides a flexible foundation with pluggable backends, while the document processing and query processing pipelines implement the core functionality.

Key architectural features include:

1. **Modular Storage System**: Abstract base classes with multiple implementations
2. **Heterogeneous Graph Indexing**: Building a graph that connects document chunks with entities
3. **Multiple Query Modes**: Different retrieval strategies for different use cases
4. **Extensible Design**: Support for custom storage backends, embedding models, and language models

For more details about specific aspects of the architecture, refer to:
- [Core Components](#2.1) for information about each component's responsibilities
- [Data Flow](#2.2) for a detailed explanation of data flow during indexing and querying
- [Storage Layer](#2.3) for information about storage implementations

Sources: [minirag/minirag.py](), [minirag/base.py](), [main.py]()

---

# Page: Core MiniRAG Class

# Core MiniRAG Class

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [minirag/__init__.py](minirag/__init__.py)
- [minirag/base.py](minirag/base.py)
- [minirag/kg/weaviate_impl.py](minirag/kg/weaviate_impl.py)
- [minirag/minirag.py](minirag/minirag.py)
- [tests/test_weaviate.py](tests/test_weaviate.py)

</details>



This document describes the `MiniRAG` class, the central orchestrator that manages the entire MiniRAG system lifecycle. It handles initialization of storage backends, coordinates document ingestion, executes queries across multiple retrieval modes, and maintains the connection between all system components.

For details on the storage interfaces that MiniRAG manages, see [Storage Abstraction Layer](#3.2). For the data processing workflows that MiniRAG orchestrates, see [Data Processing Pipeline](#3.3). For query execution strategies, see [Query Modes](#4.3).

---

## Class Overview and Role

The `MiniRAG` class serves as the primary entry point for all RAG operations. It is implemented as a Python dataclass at [minirag/minirag.py:122-611]() and acts as a facade pattern, coordinating between:

- **Storage Layer**: Graph, vector, and key-value storage instances
- **Processing Layer**: Entity extraction and query execution logic
- **LLM Layer**: Language model and embedding function integrations
- **Document Tracking**: Status management for ingested documents

Users interact with MiniRAG through three main operations:
1. `insert()` - Ingest and index documents into the knowledge graph
2. `query()` - Retrieve information using various query modes
3. `delete_by_entity()` - Remove specific entities and their relationships

**Sources:** [minirag/minirag.py:122-611]()

---

## MiniRAG Class Structure

The following diagram shows the key components and relationships within the MiniRAG class:

```mermaid
graph TB
    subgraph MiniRAG["MiniRAG Class (minirag.py:122-611)"]
        Config["Configuration Fields<br/>working_dir, chunk_token_size<br/>llm_model_name, etc."]
        
        subgraph StorageInstances["Storage Instances"]
            FullDocs["full_docs<br/>BaseKVStorage"]
            TextChunks["text_chunks<br/>BaseKVStorage"]
            ChunkGraph["chunk_entity_relation_graph<br/>BaseGraphStorage"]
            EntitiesVDB["entities_vdb<br/>BaseVectorStorage"]
            EntityNameVDB["entity_name_vdb<br/>BaseVectorStorage"]
            RelVDB["relationships_vdb<br/>BaseVectorStorage"]
            ChunksVDB["chunks_vdb<br/>BaseVectorStorage"]
            DocStatus["doc_status<br/>DocStatusStorage"]
            LLMCache["llm_response_cache<br/>BaseKVStorage"]
        end
        
        subgraph Methods["Core Methods"]
            Insert["insert() / ainsert()<br/>Document Ingestion"]
            Query["query() / aquery()<br/>Information Retrieval"]
            Delete["delete_by_entity()<br/>Entity Deletion"]
        end
        
        subgraph Functions["Functions & Callbacks"]
            EmbedFunc["embedding_func<br/>EmbeddingFunc"]
            LLMFunc["llm_model_func<br/>callable"]
            Chunking["chunking_func<br/>callable"]
            Callbacks["_insert_done()<br/>_query_done()"]
        end
    end
    
    Config --> StorageInstances
    Methods --> StorageInstances
    Functions --> Methods
    Callbacks --> StorageInstances
```

**Sources:** [minirag/minirag.py:122-188](), [minirag/minirag.py:254-313]()

---

## Configuration Fields

The `MiniRAG` dataclass contains extensive configuration options organized into several categories:

| Category | Fields | Purpose |
|----------|--------|---------|
| **Working Directory** | `working_dir` | Base path for all storage and logs, defaults to timestamped cache directory |
| **Storage Selection** | `kv_storage`, `vector_storage`, `graph_storage`, `doc_status_storage` | String names of storage backend classes to instantiate |
| **Text Chunking** | `chunk_token_size`, `chunk_overlap_token_size`, `tiktoken_model_name` | Controls document splitting parameters |
| **Entity Extraction** | `entity_extract_max_gleaning`, `entity_summary_to_max_tokens` | Entity extraction iteration and summarization limits |
| **Node Embedding** | `node_embedding_algorithm`, `node2vec_params` | Graph node embedding configuration (not used in MiniRAG) |
| **Embedding Function** | `embedding_func`, `embedding_batch_num`, `embedding_func_max_async` | Text-to-vector conversion and parallelization |
| **LLM Configuration** | `llm_model_func`, `llm_model_name`, `llm_model_max_token_size`, `llm_model_kwargs` | Language model settings and parameters |
| **Performance** | `llm_model_max_async`, `max_parallel_insert`, `enable_llm_cache` | Concurrency and caching controls |
| **Extension Points** | `addon_params`, `convert_response_to_json_func`, `chunking_func` | Customization hooks |

**Default Storage Backends:**
- Graph: `NetworkXStorage` (in-memory graph)
- Vector: `NanoVectorDBStorage` (lightweight vector DB)
- Key-Value: `JsonKVStorage` (JSON file-based)
- Document Status: `JsonDocStatusStorage` (JSON file-based)

**Sources:** [minirag/minirag.py:124-188]()

---

## Initialization Process

The initialization workflow in `__post_init__()` follows a specific sequence to set up all system components:

```mermaid
flowchart TD
    Start["__post_init__() called"] --> SetupLogging["Setup logging<br/>set_logger(log_file)"]
    SetupLogging --> CreateDir["Create working_dir<br/>if not exists"]
    CreateDir --> LoadClasses["Load storage classes<br/>_get_storage_class()"]
    
    LoadClasses --> WrapClasses["Wrap classes with<br/>global_config using partial()"]
    
    WrapClasses --> InitKV["Initialize KV storages:<br/>full_docs, text_chunks<br/>llm_response_cache"]
    InitKV --> InitGraph["Initialize graph storage:<br/>chunk_entity_relation_graph"]
    InitGraph --> InitVector["Initialize vector storages:<br/>entities_vdb, entity_name_vdb<br/>relationships_vdb, chunks_vdb"]
    InitVector --> InitDocStatus["Initialize doc status:<br/>doc_status"]
    
    InitDocStatus --> WrapFuncs["Wrap async functions:<br/>limit_async_func_call()<br/>for embedding & LLM"]
    
    WrapFuncs --> Ready["MiniRAG instance ready"]
```

**Key Initialization Steps:**

1. **Logging Setup** [minirag/minirag.py:191-193](): Creates log file in working directory
2. **Storage Class Loading** [minirag/minirag.py:207-215](): Uses lazy import pattern via `_get_storage_class()` to load backend implementations from `STORAGES` dictionary [minirag/minirag.py:39-66]()
3. **Partial Application** [minirag/minirag.py:217-227](): Wraps storage classes with `global_config` parameter using `functools.partial`
4. **Storage Instantiation** [minirag/minirag.py:228-313](): Creates all storage instances with appropriate namespaces
5. **Function Wrapping** [minirag/minirag.py:247-306](): Applies async concurrency limits to embedding and LLM functions

**Sources:** [minirag/minirag.py:190-313]()

---

## Storage Instance Management

MiniRAG creates and manages nine distinct storage instances, each with a specific namespace and purpose:

```mermaid
graph LR
    subgraph GraphStorage["Graph Storage"]
        ChunkEntityGraph["chunk_entity_relation_graph<br/>namespace: 'chunk_entity_relation'<br/>Stores entity-entity and<br/>entity-chunk relationships"]
    end
    
    subgraph VectorStorages["Vector Storages (4 instances)"]
        EntitiesVDB["entities_vdb<br/>namespace: 'entities'<br/>Entity description embeddings"]
        EntityNameVDB["entity_name_vdb<br/>namespace: 'entities_name'<br/>Entity name embeddings"]
        RelVDB["relationships_vdb<br/>namespace: 'relationships'<br/>Relationship embeddings"]
        ChunksVDB["chunks_vdb<br/>namespace: 'chunks'<br/>Text chunk embeddings"]
    end
    
    subgraph KVStorages["Key-Value Storages (3 instances)"]
        FullDocs["full_docs<br/>namespace: 'full_docs'<br/>Original documents"]
        TextChunks["text_chunks<br/>namespace: 'text_chunks'<br/>Chunked text with metadata"]
        LLMCache["llm_response_cache<br/>namespace: 'llm_response_cache'<br/>Cached LLM responses"]
    end
    
    subgraph DocTracking["Document Tracking"]
        DocStatus["doc_status<br/>namespace: 'doc_status'<br/>Document processing status"]
    end
```

**Storage Instance Details:**

| Instance | Type | Namespace | Purpose |
|----------|------|-----------|---------|
| `full_docs` | BaseKVStorage | `full_docs` | Stores complete original documents by doc_id |
| `text_chunks` | BaseKVStorage | `text_chunks` | Stores chunked text with metadata (tokens, order, full_doc_id) |
| `chunk_entity_relation_graph` | BaseGraphStorage | `chunk_entity_relation` | Graph connecting entities, relationships, and chunks |
| `entities_vdb` | BaseVectorStorage | `entities` | Vector embeddings of entity descriptions for semantic search |
| `entity_name_vdb` | BaseVectorStorage | `entities_name` | Vector embeddings of entity names for name-based retrieval |
| `relationships_vdb` | BaseVectorStorage | `relationships` | Vector embeddings of entity relationships |
| `chunks_vdb` | BaseVectorStorage | `chunks` | Vector embeddings of text chunks for naive retrieval |
| `doc_status` | DocStatusStorage | `doc_status` | Tracks document processing status (PENDING/PROCESSING/PROCESSED/FAILED) |
| `llm_response_cache` | BaseKVStorage | `llm_response_cache` | Caches LLM responses to avoid redundant API calls (optional) |

**Sources:** [minirag/minirag.py:228-313]()

---

## Document Ingestion Workflow

The `insert()` and `ainsert()` methods handle document ingestion through a multi-stage pipeline:

```mermaid
sequenceDiagram
    participant User
    participant MiniRAG
    participant Pipeline as "apipeline_enqueue_documents()"
    participant Process as "apipeline_process_enqueue_documents()"
    participant Extract as "extract_entities()"
    participant DocStatus as "doc_status storage"
    participant Storages as "Vector/Graph/KV storages"
    
    User->>MiniRAG: insert(string_or_strings)
    MiniRAG->>MiniRAG: always_get_an_event_loop()
    MiniRAG->>MiniRAG: ainsert()
    
    rect rgb(240, 240, 240)
        Note over MiniRAG,DocStatus: Stage 1: Document Enqueuing
        MiniRAG->>Pipeline: apipeline_enqueue_documents()
        Pipeline->>Pipeline: Generate or validate doc IDs
        Pipeline->>Pipeline: Remove duplicates
        Pipeline->>Pipeline: Filter existing docs
        Pipeline->>DocStatus: upsert(new_docs with PENDING status)
    end
    
    rect rgb(240, 240, 240)
        Note over MiniRAG,Storages: Stage 2: Document Processing
        MiniRAG->>Process: apipeline_process_enqueue_documents()
        Process->>DocStatus: get PENDING/PROCESSING/FAILED docs
        loop For each document batch
            Process->>Process: chunking_func() to split text
            Process->>Storages: upsert chunks to chunks_vdb, text_chunks
            Process->>Storages: upsert full doc to full_docs
            Process->>DocStatus: Update status to PROCESSED
        end
    end
    
    rect rgb(240, 240, 240)
        Note over MiniRAG,Storages: Stage 3: Entity Extraction
        MiniRAG->>DocStatus: get_docs_by_status(PROCESSED)
        MiniRAG->>MiniRAG: Re-chunk PROCESSED docs
        MiniRAG->>Extract: extract_entities()
        Extract->>Storages: Populate entities_vdb, relationships_vdb
        Extract->>Storages: Update chunk_entity_relation_graph
    end
    
    MiniRAG->>MiniRAG: _insert_done()
    MiniRAG->>Storages: index_done_callback() on all storages
    MiniRAG-->>User: Complete
```

### Stage 1: Document Enqueuing

The `apipeline_enqueue_documents()` method [minirag/minirag.py:391-449]() performs:

1. **ID Generation/Validation**: Uses MD5 hash with `compute_mdhash_id()` if IDs not provided
2. **Deduplication**: Ensures unique content by creating reverse mapping
3. **Status Initialization**: Creates `DocProcessingStatus` with `DocStatus.PENDING`
4. **Filtering**: Calls `doc_status.filter_keys()` to exclude already-processed documents
5. **Storage**: Upserts new documents to `doc_status` storage

### Stage 2: Document Processing

The `apipeline_process_enqueue_documents()` method [minirag/minirag.py:451-514]() processes documents in batches:

1. **Batch Retrieval**: Fetches documents with status PENDING, PROCESSING, or FAILED
2. **Batch Creation**: Splits into batches of size `max_parallel_insert` (default: 2)
3. **Chunking**: Applies `chunking_func` (default: `chunking_by_token_size`) to each document
4. **Parallel Upsert**: Uses `asyncio.gather()` to store chunks in multiple storages simultaneously
5. **Status Update**: Marks documents as `DocStatus.PROCESSED`

### Stage 3: Entity Extraction

After processing, the main `ainsert()` method [minirag/minirag.py:362-387]() performs entity extraction:

1. **Retrieve Processed Docs**: Gets all documents with `DocStatus.PROCESSED`
2. **Re-chunking**: Chunks content again (to get full metadata)
3. **Entity Extraction**: Calls `extract_entities()` from [minirag/operate.py]()
4. **Graph Population**: Updates `chunk_entity_relation_graph`, `entities_vdb`, `entity_name_vdb`, `relationships_vdb`

**Sources:** [minirag/minirag.py:340-389](), [minirag/minirag.py:391-449](), [minirag/minirag.py:451-514]()

---

## Query Execution Workflow

The `query()` and `aquery()` methods route queries to different retrieval strategies based on `QueryParam.mode`:

```mermaid
flowchart TD
    Start["query(query_str, param)"] --> GetLoop["always_get_an_event_loop()"]
    GetLoop --> AsyncQuery["aquery(query_str, param)"]
    
    AsyncQuery --> CheckMode{"param.mode"}
    
    CheckMode -->|"'light'"| LightMode["hybrid_query()<br/>Entity-centric retrieval<br/>Uses: graph, entities_vdb,<br/>relationships_vdb, text_chunks"]
    
    CheckMode -->|"'mini'"| MiniMode["minirag_query()<br/>Topology-enhanced retrieval<br/>Uses: graph, entities_vdb,<br/>entity_name_vdb, relationships_vdb,<br/>chunks_vdb, text_chunks, embedding_func"]
    
    CheckMode -->|"'naive'"| NaiveMode["naive_query()<br/>Vector search only<br/>Uses: chunks_vdb, text_chunks"]
    
    CheckMode -->|"other"| Error["Raise ValueError:<br/>'Unknown mode'"]
    
    LightMode --> Done["_query_done()"]
    MiniMode --> Done
    NaiveMode --> Done
    
    Done --> Callback["index_done_callback()<br/>on llm_response_cache"]
    Callback --> Return["Return response"]
```

### Query Mode Routing

The routing logic at [minirag/minirag.py:537-572]() determines the execution path:

| Mode | Function | Storage Requirements | Use Case |
|------|----------|---------------------|----------|
| `"light"` | `hybrid_query()` | graph, entities_vdb, relationships_vdb, text_chunks | Entity-centric retrieval with relationship context |
| `"mini"` | `minirag_query()` | graph, entities_vdb, entity_name_vdb, relationships_vdb, chunks_vdb, text_chunks, embedding_func | Topology-enhanced retrieval with graph traversal |
| `"naive"` | `naive_query()` | chunks_vdb, text_chunks | Simple vector similarity search on chunks |

Each query function receives:
- The query string
- Relevant storage instances
- `QueryParam` object with configuration
- Global configuration dictionary via `asdict(self)`

**Query Parameter Passthrough:**

The `QueryParam` object (see [Query Modes](#4.3)) contains settings like:
- `top_k`: Number of entities/chunks to retrieve
- `max_token_for_*`: Token limits for context assembly
- `only_need_context`: Return context without LLM generation
- `only_need_prompt`: Return prompt without LLM generation
- `stream`: Enable streaming response

**Sources:** [minirag/minirag.py:533-580]()

---

## Entity Deletion

The `delete_by_entity()` method removes specific entities and their associated data:

```mermaid
sequenceDiagram
    participant User
    participant MiniRAG
    participant EntitiesVDB as "entities_vdb"
    participant RelVDB as "relationships_vdb"
    participant Graph as "chunk_entity_relation_graph"
    
    User->>MiniRAG: delete_by_entity("Entity Name")
    MiniRAG->>MiniRAG: Convert to uppercase with quotes
    MiniRAG->>EntitiesVDB: delete_entity(entity_name)
    MiniRAG->>RelVDB: delete_relation(entity_name)
    MiniRAG->>Graph: delete_node(entity_name)
    MiniRAG->>MiniRAG: _delete_by_entity_done()
    MiniRAG->>EntitiesVDB: index_done_callback()
    MiniRAG->>RelVDB: index_done_callback()
    MiniRAG->>Graph: index_done_callback()
    MiniRAG-->>User: Deletion complete
```

**Implementation Details:**

The `adelete_by_entity()` method [minirag/minirag.py:586-599]() performs:

1. **Name Normalization**: Converts entity name to uppercase and wraps in quotes (format: `"ENTITY"`)
2. **Entity Deletion**: Calls `entities_vdb.delete_entity()` to remove entity vectors
3. **Relationship Deletion**: Calls `relationships_vdb.delete_relation()` to remove associated relationships
4. **Graph Node Deletion**: Calls `chunk_entity_relation_graph.delete_node()` to remove graph node
5. **Callback Execution**: Runs `_delete_by_entity_done()` to commit changes via `index_done_callback()`

**Note:** This operation does not remove the underlying text chunks that mentioned the entity, only the entity metadata and graph connections.

**Sources:** [minirag/minirag.py:582-611]()

---

## Lifecycle Management

MiniRAG implements callback patterns to handle post-operation cleanup and persistence:

### Insert Completion Callback

The `_insert_done()` method [minirag/minirag.py:516-531]() is called after document insertion completes:

```python
async def _insert_done(self):
    tasks = []
    for storage_inst in [
        self.full_docs,
        self.text_chunks,
        self.llm_response_cache,
        self.entities_vdb,
        self.entity_name_vdb,
        self.relationships_vdb,
        self.chunks_vdb,
        self.chunk_entity_relation_graph,
    ]:
        if storage_inst is None:
            continue
        tasks.append(cast(StorageNameSpace, storage_inst).index_done_callback())
    await asyncio.gather(*tasks)
```

This ensures all storage backends commit their in-memory changes to persistent storage.

### Query Completion Callback

The `_query_done()` method [minirag/minirag.py:574-580]() commits LLM cache updates:

```python
async def _query_done(self):
    tasks = []
    for storage_inst in [self.llm_response_cache]:
        if storage_inst is None:
            continue
        tasks.append(cast(StorageNameSpace, storage_inst).index_done_callback())
    await asyncio.gather(*tasks)
```

### Deletion Completion Callback

The `_delete_by_entity_done()` method [minirag/minirag.py:601-611]() commits entity deletions:

```python
async def _delete_by_entity_done(self):
    tasks = []
    for storage_inst in [
        self.entities_vdb,
        self.relationships_vdb,
        self.chunk_entity_relation_graph,
    ]:
        if storage_inst is None:
            continue
        tasks.append(cast(StorageNameSpace, storage_inst).index_done_callback())
    await asyncio.gather(*tasks)
```

**Purpose of Callbacks:**

The `index_done_callback()` method defined in `BaseStorageNameSpace` [minirag/base.py:53-55]() allows each storage implementation to:
- Flush in-memory buffers to disk
- Commit database transactions
- Update indices
- Perform cleanup operations

**Sources:** [minirag/minirag.py:516-531](), [minirag/minirag.py:574-580](), [minirag/minirag.py:601-611]()

---

## Event Loop Management

MiniRAG handles asyncio event loop complexities through the `always_get_an_event_loop()` function:

```mermaid
flowchart TD
    Start["always_get_an_event_loop()"] --> TryGet["Try to get current<br/>event loop"]
    TryGet --> CheckClosed{"Is loop closed?"}
    
    CheckClosed -->|"No"| Return["Return current loop"]
    CheckClosed -->|"Yes"| CreateNew
    TryGet -->|"RuntimeError"| CreateNew["Create new event loop"]
    
    CreateNew --> SetLoop["asyncio.set_event_loop(new_loop)"]
    SetLoop --> Return
```

**Implementation:**

The function at [minirag/minirag.py:97-119]() ensures an event loop always exists:

```python
def always_get_an_event_loop() -> asyncio.AbstractEventLoop:
    try:
        # Try to get the current event loop
        current_loop = asyncio.get_event_loop()
        if current_loop.is_closed():
            raise RuntimeError("Event loop is closed.")
        return current_loop

    except RuntimeError:
        # If no event loop exists or it is closed, create a new one
        logger.info("Creating a new event loop in main thread.")
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        return new_loop
```

**Usage in Synchronous Methods:**

All public synchronous methods (`insert()`, `query()`, `delete_by_entity()`) use this pattern:

```python
def insert(self, string_or_strings):
    loop = always_get_an_event_loop()
    return loop.run_until_complete(self.ainsert(string_or_strings))
```

This allows MiniRAG to provide a simple synchronous API while internally using async operations for performance.

**Sources:** [minirag/minirag.py:97-119](), [minirag/minirag.py:340-342](), [minirag/minirag.py:533-535](), [minirag/minirag.py:582-584]()

---

## Lazy Storage Loading

MiniRAG uses a lazy import pattern to avoid loading all storage backend dependencies at startup:

### Storage Registry

The `STORAGES` dictionary [minirag/minirag.py:39-66]() maps storage class names to their module paths:

```python
STORAGES = {
    "NetworkXStorage": ".kg.networkx_impl",
    "JsonKVStorage": ".kg.json_kv_impl",
    "NanoVectorDBStorage": ".kg.nano_vector_db_impl",
    "JsonDocStatusStorage": ".kg.jsondocstatus_impl",
    "Neo4JStorage": ".kg.neo4j_impl",
    # ... 10+ more storage backends
}
```

### Lazy Import Function

The `lazy_external_import()` function [minirag/minirag.py:77-94]() defers module loading:

```python
def lazy_external_import(module_name: str, class_name: str):
    """Lazily import a class from an external module based on the package of the caller."""
    
    # Get the caller's module and package
    import inspect
    caller_frame = inspect.currentframe().f_back
    module = inspect.getmodule(caller_frame)
    package = module.__package__ if module else None

    def import_class(*args, **kwargs):
        import importlib
        module = importlib.import_module(module_name, package=package)
        cls = getattr(module, class_name)
        return cls(*args, **kwargs)

    return import_class
```

### Storage Class Resolution

The `_get_storage_class()` method [minirag/minirag.py:315-318]() resolves storage classes:

```python
def _get_storage_class(self, storage_name: str) -> dict:
    import_path = STORAGES[storage_name]
    storage_class = lazy_external_import(import_path, storage_name)
    return storage_class
```

**Benefits:**
- Only loads required storage backend dependencies
- Reduces startup time
- Allows optional dependencies (e.g., Neo4j, Weaviate)
- Supports pluggable storage architecture

**Sources:** [minirag/minirag.py:39-66](), [minirag/minirag.py:77-94](), [minirag/minirag.py:315-318]()

---

## Configuration Summary Table

Key configuration fields and their impact on system behavior:

| Configuration | Default Value | Impact | Location |
|---------------|---------------|--------|----------|
| `working_dir` | `./minirag_cache_{timestamp}` | Base directory for all storage and logs | [minirag/minirag.py:124-126]() |
| `chunk_token_size` | `1200` | Size of text chunks for processing | [minirag/minirag.py:138]() |
| `chunk_overlap_token_size` | `100` | Overlap between consecutive chunks | [minirag/minirag.py:139]() |
| `entity_extract_max_gleaning` | `1` | Number of entity extraction iterations | [minirag/minirag.py:143]() |
| `embedding_func_max_async` | `16` | Max concurrent embedding operations | [minirag/minirag.py:161]() |
| `llm_model_max_async` | `16` | Max concurrent LLM calls | [minirag/minirag.py:169]() |
| `max_parallel_insert` | `2` (from env var) | Parallel document processing limit | [minirag/minirag.py:188]() |
| `enable_llm_cache` | `True` | Whether to cache LLM responses | [minirag/minirag.py:175]() |
| `kv_storage` | `"JsonKVStorage"` | KV storage backend class name | [minirag/minirag.py:130]() |
| `vector_storage` | `"NanoVectorDBStorage"` | Vector storage backend class name | [minirag/minirag.py:131]() |
| `graph_storage` | `"NetworkXStorage"` | Graph storage backend class name | [minirag/minirag.py:132]() |

**Sources:** [minirag/minirag.py:124-188]()

---

## Usage Example

Basic usage pattern for the MiniRAG class:

```python
from minirag import MiniRAG, QueryParam

# Initialize with configuration
rag = MiniRAG(
    working_dir="./my_rag_storage",
    chunk_token_size=800,
    llm_model_name="gpt-4o-mini",
    embedding_func=my_embedding_function,
    llm_model_func=my_llm_function
)

# Insert documents
documents = [
    "First document content...",
    "Second document content..."
]
rag.insert(documents)

# Query with different modes
response_mini = rag.query(
    "What is the relationship between X and Y?",
    param=QueryParam(mode="mini", top_k=60)
)

response_naive = rag.query(
    "What is X?",
    param=QueryParam(mode="naive", top_k=10)
)

# Delete entity
rag.delete_by_entity("EntityName")
```

For complete examples, see [Document Indexing](#8.1) and [Question Answering](#8.2).

**Sources:** [minirag/minirag.py:122-611](), [minirag/__init__.py:1-6]()

---

# Page: Storage Abstraction Layer

# Storage Abstraction Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [minirag/__init__.py](minirag/__init__.py)
- [minirag/base.py](minirag/base.py)
- [minirag/kg/weaviate_impl.py](minirag/kg/weaviate_impl.py)
- [minirag/minirag.py](minirag/minirag.py)
- [tests/test_weaviate.py](tests/test_weaviate.py)

</details>



## Introduction

The Storage Abstraction Layer defines the core interfaces that enable MiniRAG's pluggable storage architecture. This layer consists of three primary abstract base classes—`BaseGraphStorage`, `BaseVectorStorage`, and `BaseKVStorage`—each defining a contract for a specific storage concern. The abstraction layer allows MiniRAG to support over 10 different database backends (NetworkX, Neo4j, PostgreSQL, TiDB, Oracle, Weaviate, Chroma, etc.) without changing core system logic.

All storage abstractions inherit from `StorageNameSpace`, which provides namespace isolation and lifecycle callbacks. The abstractions are defined in [minirag/base.py:48-198]() and instantiated through a lazy-loading mechanism in [minirag/minirag.py:39-66]().

For concrete implementations of these abstractions, see [Storage Implementations](#5).

Sources: [minirag/base.py:48-198](), [minirag/minirag.py:39-66](), [minirag/minirag.py:207-227]()

## Architecture Overview

The Storage Abstraction Layer uses an interface-based design where abstract base classes define contracts that concrete implementations must fulfill. This design enables the pluggable storage architecture, allowing MiniRAG to switch between different database backends by changing configuration strings.

### Storage Abstraction Hierarchy

```mermaid
classDiagram
    class StorageNameSpace {
        +namespace: str
        +global_config: dict
        +index_done_callback() async
        +query_done_callback() async
    }
    
    class BaseVectorStorage {
        +embedding_func: EmbeddingFunc
        +meta_fields: set
        +query(query, top_k) async
        +upsert(data) async
    }
    
    class BaseKVStorage~T~ {
        +embedding_func: EmbeddingFunc
        +all_keys() async
        +get_by_id(id) async
        +get_by_ids(ids, fields) async
        +filter_keys(data) async
        +upsert(data) async
        +drop() async
    }
    
    class BaseGraphStorage {
        +embedding_func: EmbeddingFunc
        +get_types() async
        +has_node(node_id) async
        +has_edge(source_id, target_id) async
        +node_degree(node_id) async
        +edge_degree(src_id, tgt_id) async
        +get_node(node_id) async
        +get_edge(source_id, target_id) async
        +get_node_edges(source_id) async
        +upsert_node(node_id, data) async
        +upsert_edge(source_id, target_id, data) async
        +delete_node(node_id) async
        +embed_nodes(algorithm) async
    }
    
    class DocStatusStorage {
        +get_status_counts() async
        +get_docs_by_status(status) async
        +get_failed_docs() async
        +get_pending_docs() async
    }
    
    StorageNameSpace <|-- BaseVectorStorage
    StorageNameSpace <|-- BaseKVStorage
    StorageNameSpace <|-- BaseGraphStorage
    BaseKVStorage <|-- DocStatusStorage
```

Sources: [minirag/base.py:48-198]()

## Core Storage Abstractions

### StorageNameSpace Base Class

`StorageNameSpace` is the root base class for all storage abstractions, defined in [minirag/base.py:48-59](). It provides:

| Field | Type | Purpose |
|-------|------|---------|
| `namespace` | `str` | Isolates storage instances by data type (e.g., "entities", "chunks", "relationships") |
| `global_config` | `dict` | Provides access to system-wide configuration settings |

**Lifecycle Callbacks:**
- `async def index_done_callback()`: Called after indexing operations to commit/persist changes
- `async def query_done_callback()`: Called after query operations to perform cleanup

These callbacks are invoked by the `MiniRAG` class in [minirag/minirag.py:516-531]() after indexing and [minirag/minirag.py:574-580]() after querying.

Sources: [minirag/base.py:48-59](), [minirag/minirag.py:516-531](), [minirag/minirag.py:574-580]()

### BaseVectorStorage Interface

`BaseVectorStorage` defines the contract for vector similarity search operations, defined in [minirag/base.py:62-74]().

**Core Methods:**

| Method | Signature | Purpose |
|--------|-----------|---------|
| `query` | `async query(query: str, top_k: int) -> list[dict]` | Perform semantic similarity search |
| `upsert` | `async upsert(data: dict[str, dict])` | Insert or update vector embeddings |

**Fields:**
- `embedding_func: EmbeddingFunc` - Function to generate embeddings from text
- `meta_fields: set` - Set of metadata fields to store alongside vectors

The MiniRAG system creates four instances of `BaseVectorStorage`:
- `entities_vdb` - Stores entity descriptions ([minirag/minirag.py:273-278]())
- `entity_name_vdb` - Stores entity names ([minirag/minirag.py:281-286]())
- `relationships_vdb` - Stores relationship descriptions ([minirag/minirag.py:288-293]())
- `chunks_vdb` - Stores text chunk embeddings ([minirag/minirag.py:294-298]())

Sources: [minirag/base.py:62-74](), [minirag/minirag.py:273-298]()

### BaseKVStorage Interface

`BaseKVStorage[T]` is a generic interface for key-value storage, defined in [minirag/base.py:77-101]().

**Core Methods:**

| Method | Signature | Purpose |
|--------|-----------|---------|
| `all_keys` | `async all_keys() -> list[str]` | Retrieve all keys in storage |
| `get_by_id` | `async get_by_id(id: str) -> Union[T, None]` | Retrieve single value by key |
| `get_by_ids` | `async get_by_ids(ids: list[str], fields: Union[set[str], None]) -> list[Union[T, None]]` | Retrieve multiple values, optionally filtering fields |
| `filter_keys` | `async filter_keys(data: list[str]) -> set[str]` | Return keys that don't exist in storage |
| `upsert` | `async upsert(data: dict[str, T])` | Insert or update key-value pairs |
| `drop` | `async drop()` | Delete all data in the storage |

The MiniRAG system creates three instances of `BaseKVStorage`:
- `full_docs` - Stores complete document content ([minirag/minirag.py:254-258]())
- `text_chunks` - Stores chunked document segments ([minirag/minirag.py:259-263]())
- `llm_response_cache` - Caches LLM responses ([minirag/minirag.py:237-245]())

Sources: [minirag/base.py:77-101](), [minirag/minirag.py:237-263]()

### BaseGraphStorage Interface

`BaseGraphStorage` defines the contract for graph database operations, defined in [minirag/base.py:103-149]().

**Node Operations:**

| Method | Signature | Purpose |
|--------|-----------|---------|
| `has_node` | `async has_node(node_id: str) -> bool` | Check if node exists |
| `get_node` | `async get_node(node_id: str) -> Union[dict, None]` | Retrieve node data |
| `upsert_node` | `async upsert_node(node_id: str, node_data: dict[str, str])` | Insert or update node |
| `delete_node` | `async delete_node(node_id: str)` | Remove node from graph |
| `node_degree` | `async node_degree(node_id: str) -> int` | Get number of edges connected to node |

**Edge Operations:**

| Method | Signature | Purpose |
|--------|-----------|---------|
| `has_edge` | `async has_edge(source_node_id: str, target_node_id: str) -> bool` | Check if edge exists |
| `get_edge` | `async get_edge(source_node_id: str, target_node_id: str) -> Union[dict, None]` | Retrieve edge data |
| `upsert_edge` | `async upsert_edge(source_node_id: str, target_node_id: str, edge_data: dict[str, str])` | Insert or update edge |
| `get_node_edges` | `async get_node_edges(source_node_id: str) -> Union[list[tuple[str, str]], None]` | Get all edges from a node |
| `edge_degree` | `async edge_degree(src_id: str, tgt_id: str) -> int` | Get weight/degree of edge |

**Graph Metadata:**

| Method | Signature | Purpose |
|--------|-----------|---------|
| `get_types` | `async get_types() -> tuple[list[str], list[str]]` | Return (node_types, edge_types) |
| `embed_nodes` | `async embed_nodes(algorithm: str) -> tuple[np.ndarray, list[str]]` | Generate node embeddings (not used in MiniRAG) |

The MiniRAG system creates one instance of `BaseGraphStorage`:
- `chunk_entity_relation_graph` - Stores the heterogeneous graph of chunks, entities, and relationships ([minirag/minirag.py:264-268]())

Sources: [minirag/base.py:103-149](), [minirag/minirag.py:264-268]()

### DocStatusStorage Interface

`DocStatusStorage` extends `BaseKVStorage` with specialized methods for tracking document processing status, defined in [minirag/base.py:184-198]().

**Specialized Methods:**

| Method | Signature | Purpose |
|--------|-----------|---------|
| `get_status_counts` | `async get_status_counts() -> dict[str, int]` | Count documents in each status |
| `get_docs_by_status` | `async get_docs_by_status(status: DocStatus) -> dict[str, DocProcessingStatus]` | Retrieve documents by status |
| `get_failed_docs` | `async get_failed_docs() -> dict[str, DocProcessingStatus]` | Get all failed documents |
| `get_pending_docs` | `async get_pending_docs() -> dict[str, DocProcessingStatus]` | Get all pending documents |

**Document Status Types** (`DocStatus` enum, [minirag/base.py:151-157]()):
- `PENDING` - Document queued for processing
- `PROCESSING` - Document currently being processed
- `PROCESSED` - Document successfully processed
- `FAILED` - Document processing failed

The MiniRAG system creates one instance of `DocStatusStorage`:
- `doc_status` - Tracks processing status of all documents ([minirag/minirag.py:308-313]())

Sources: [minirag/base.py:151-198](), [minirag/minirag.py:308-313]()

## Pluggable Storage Architecture

MiniRAG's storage abstraction layer enables a pluggable architecture where storage backends can be swapped by changing configuration strings. This is implemented through the `STORAGES` registry in [minirag/minirag.py:39-66]().

### Storage Registry and Lazy Loading

The `STORAGES` dictionary maps storage class names to their module paths:

| Storage Class | Module | Supported Backends |
|---------------|--------|-------------------|
| `NetworkXStorage` | `.kg.networkx_impl` | In-memory graph |
| `Neo4JStorage` | `.kg.neo4j_impl` | Neo4j native graph database |
| `PGGraphStorage`, `AGEStorage` | `.kg.postgres_impl`, `.kg.age_impl` | PostgreSQL with graph extensions |
| `TiDBGraphStorage` | `.kg.tidb_impl` | TiDB distributed graph |
| `MongoGraphStorage` | `.kg.mongo_impl` | MongoDB graph storage |
| `GremlinStorage` | `.kg.gremlin_impl` | Gremlin-compatible graph databases |
| `WeaviateGraphStorage` | `.kg.weaviate_impl` | Weaviate graph storage |
| `OracleGraphStorage` | `.kg.oracle_impl` | Oracle graph database |
| `NanoVectorDBStorage` | `.kg.nano_vector_db_impl` | Lightweight vector DB |
| `ChromaVectorDBStorage` | `.kg.chroma_impl` | Chroma vector database |
| `MilvusVectorDBStorge` | `.kg.milvus_impl` | Milvus vector database |
| `WeaviateVectorStorage` | `.kg.weaviate_impl` | Weaviate vector storage |
| `TiDBVectorDBStorage` | `.kg.tidb_impl` | TiDB vector storage |
| `PGVectorStorage` | `.kg.postgres_impl` | PostgreSQL pgvector |
| `OracleVectorDBStorage` | `.kg.oracle_impl` | Oracle vector storage |
| `JsonKVStorage` | `.kg.json_kv_impl` | JSON file-based storage |
| `RedisKVStorage` | `.kg.redis_impl` | Redis in-memory KV store |
| `MongoKVStorage` | `.kg.mongo_impl` | MongoDB document store |
| `WeaviateKVStorage` | `.kg.weaviate_impl` | Weaviate KV storage |
| `TiDBKVStorage` | `.kg.tidb_impl` | TiDB KV storage |
| `PGKVStorage` | `.kg.postgres_impl` | PostgreSQL KV storage |
| `OracleKVStorage` | `.kg.oracle_impl` | Oracle KV storage |
| `JsonDocStatusStorage` | `.kg.jsondocstatus_impl` | JSON-based doc status tracking |
| `PGDocStatusStorage` | `.kg.postgres_impl` | PostgreSQL doc status tracking |

**Lazy Loading Mechanism** ([minirag/minirag.py:77-94]()):

The `lazy_external_import` function dynamically imports storage classes only when needed:

```python
def lazy_external_import(module_name: str, class_name: str):
    """Lazily import a class from an external module based on the package of the caller."""
    
    def import_class(*args, **kwargs):
        import importlib
        module = importlib.import_module(module_name, package=package)
        cls = getattr(module, class_name)
        return cls(*args, **kwargs)
    
    return import_class
```

This approach reduces startup time and memory usage by loading only the storage backends actually configured.

Sources: [minirag/minirag.py:39-94]()

### MiniRAG Storage Initialization

The `MiniRAG` class initializes storage instances in its `__post_init__` method ([minirag/minirag.py:190-313]()):

**Configuration Phase** ([minirag/minirag.py:207-227]()):
```python
# Load storage classes
self.key_string_value_json_storage_cls: Type[BaseKVStorage] = (
    self._get_storage_class(self.kv_storage)
)
self.vector_db_storage_cls: Type[BaseVectorStorage] = self._get_storage_class(
    self.vector_storage
)
self.graph_storage_cls: Type[BaseGraphStorage] = self._get_storage_class(
    self.graph_storage
)

# Bind global config via partial
self.key_string_value_json_storage_cls = partial(
    self.key_string_value_json_storage_cls, global_config=global_config
)
```

**Storage Instance Creation** ([minirag/minirag.py:254-313]()):

The MiniRAG system creates nine storage instances:

```mermaid
graph TB
    subgraph "MiniRAG Storage Instances"
        full_docs["full_docs<br/>BaseKVStorage<br/>namespace='full_docs'"]
        text_chunks["text_chunks<br/>BaseKVStorage<br/>namespace='text_chunks'"]
        llm_cache["llm_response_cache<br/>BaseKVStorage<br/>namespace='llm_response_cache'"]
        
        entities_vdb["entities_vdb<br/>BaseVectorStorage<br/>namespace='entities'"]
        entity_name_vdb["entity_name_vdb<br/>BaseVectorStorage<br/>namespace='entities_name'"]
        relationships_vdb["relationships_vdb<br/>BaseVectorStorage<br/>namespace='relationships'"]
        chunks_vdb["chunks_vdb<br/>BaseVectorStorage<br/>namespace='chunks'"]
        
        graph["chunk_entity_relation_graph<br/>BaseGraphStorage<br/>namespace='chunk_entity_relation'"]
        
        doc_status["doc_status<br/>DocStatusStorage<br/>namespace='doc_status'"]
    end
    
    subgraph "Storage Types"
        kv_type["Key-Value<br/>Storage"]
        vec_type["Vector<br/>Storage"]
        graph_type["Graph<br/>Storage"]
        status_type["Status<br/>Storage"]
    end
    
    full_docs --> kv_type
    text_chunks --> kv_type
    llm_cache --> kv_type
    
    entities_vdb --> vec_type
    entity_name_vdb --> vec_type
    relationships_vdb --> vec_type
    chunks_vdb --> vec_type
    
    graph --> graph_type
    
    doc_status --> status_type
```

Each instance is created with:
- A unique `namespace` for data isolation
- The `global_config` dictionary
- An `embedding_func` for generating embeddings
- Optional `meta_fields` for vector storage instances

Sources: [minirag/minirag.py:207-313]()

## Storage Abstraction Usage

The storage abstractions are used throughout MiniRAG's indexing and query pipelines.

### Storage Instances in MiniRAG Workflow

```mermaid
flowchart TB
    subgraph "Indexing Phase"
        docs["Documents"] --> insert["MiniRAG.ainsert()"]
        insert --> chunking["chunking_func"]
        chunking --> text_chunks["text_chunks<br/>(BaseKVStorage)"]
        chunking --> chunks_vdb["chunks_vdb<br/>(BaseVectorStorage)"]
        chunking --> extract["extract_entities()"]
        extract --> entities_vdb["entities_vdb<br/>(BaseVectorStorage)"]
        extract --> entity_name_vdb["entity_name_vdb<br/>(BaseVectorStorage)"]
        extract --> relationships_vdb["relationships_vdb<br/>(BaseVectorStorage)"]
        extract --> chunk_entity_relation_graph["chunk_entity_relation_graph<br/>(BaseGraphStorage)"]
        insert --> doc_status["doc_status<br/>(DocStatusStorage)"]
        text_chunks --> callback["index_done_callback()"]
        chunks_vdb --> callback
        entities_vdb --> callback
        entity_name_vdb --> callback
        relationships_vdb --> callback
        chunk_entity_relation_graph --> callback
    end
    
    subgraph "Query Phase"
        query["Query String"] --> aquery["MiniRAG.aquery()"]
        aquery --> mode{param.mode}
        mode -->|"mini"| minirag_query["minirag_query()"]
        mode -->|"light"| hybrid_query["hybrid_query()"]
        mode -->|"naive"| naive_query["naive_query()"]
        
        minirag_query --> entities_vdb2["entities_vdb.query()"]
        minirag_query --> entity_name_vdb2["entity_name_vdb.query()"]
        minirag_query --> chunk_entity_relation_graph2["chunk_entity_relation_graph<br/>.get_node()/.get_edge()"]
        
        hybrid_query --> entities_vdb3["entities_vdb.query()"]
        hybrid_query --> relationships_vdb2["relationships_vdb.query()"]
        hybrid_query --> chunk_entity_relation_graph3["chunk_entity_relation_graph<br/>.get_node()"]
        
        naive_query --> chunks_vdb2["chunks_vdb.query()"]
        
        entities_vdb2 --> text_chunks2["text_chunks.get_by_ids()"]
        entities_vdb3 --> text_chunks2
        relationships_vdb2 --> text_chunks2
        chunks_vdb2 --> text_chunks2
        chunk_entity_relation_graph2 --> text_chunks2
        chunk_entity_relation_graph3 --> text_chunks2
        
        text_chunks2 --> response["Response"]
    end
```

Sources: [minirag/minirag.py:340-389](), [minirag/minirag.py:537-572]()

### Storage Method Call Patterns

The following table shows which abstract methods are called during different operations:

| Operation | Storage Instance | Abstract Methods Called |
|-----------|------------------|------------------------|
| **Document Insertion** | `doc_status` | `filter_keys()`, `upsert()`, `get_docs_by_status()` |
| | `text_chunks` | `upsert()` |
| | `chunks_vdb` | `upsert()` |
| | `full_docs` | `upsert()` |
| **Entity Extraction** | `entities_vdb` | `upsert()` |
| | `entity_name_vdb` | `upsert()` |
| | `relationships_vdb` | `upsert()` |
| | `chunk_entity_relation_graph` | `upsert_node()`, `upsert_edge()` |
| **Mini Query** | `entity_name_vdb` | `query()` |
| | `chunk_entity_relation_graph` | `get_node()`, `get_edge()`, `has_node()`, `get_node_edges()` |
| | `text_chunks` | `get_by_ids()` |
| **Light Query** | `entities_vdb` | `query()` |
| | `relationships_vdb` | `query()` |
| | `chunk_entity_relation_graph` | `get_node()` |
| | `text_chunks` | `get_by_ids()` |
| **Naive Query** | `chunks_vdb` | `query()` |
| | `text_chunks` | `get_by_ids()` |
| **Entity Deletion** | `entities_vdb` | `delete_entity()` (if implemented) |
| | `relationships_vdb` | `delete_relation()` (if implemented) |
| | `chunk_entity_relation_graph` | `delete_node()` |

Sources: [minirag/minirag.py:340-611](), [minirag/operate.py]()

## Integration with MiniRAG Core

The storage abstractions integrate with the `MiniRAG` class through several key methods.

### Indexing Integration

During document insertion, the `MiniRAG.ainsert()` method ([minirag/minirag.py:344-389]()) orchestrates storage operations:

**Sequence Diagram: Document Insertion**

```mermaid
sequenceDiagram
    participant Client
    participant MiniRAG
    participant doc_status as "doc_status<br/>(DocStatusStorage)"
    participant text_chunks as "text_chunks<br/>(BaseKVStorage)"
    participant chunks_vdb as "chunks_vdb<br/>(BaseVectorStorage)"
    participant extract_entities as "extract_entities()"
    participant entities_vdb as "entities_vdb<br/>(BaseVectorStorage)"
    participant graph as "chunk_entity_relation_graph<br/>(BaseGraphStorage)"
    
    Client->>MiniRAG: ainsert(documents)
    MiniRAG->>MiniRAG: compute_mdhash_id(doc)
    MiniRAG->>doc_status: filter_keys(doc_ids)
    doc_status-->>MiniRAG: new_doc_ids
    MiniRAG->>doc_status: upsert({id: {..., status: PENDING}})
    
    loop For each pending document
        MiniRAG->>doc_status: get_docs_by_status(PENDING)
        doc_status-->>MiniRAG: pending_docs
        MiniRAG->>MiniRAG: chunking_func(doc.content)
        MiniRAG->>text_chunks: upsert(chunks)
        MiniRAG->>chunks_vdb: upsert(chunk_embeddings)
        MiniRAG->>doc_status: upsert({id: {..., status: PROCESSED}})
    end
    
    MiniRAG->>extract_entities: extract_entities(chunks)
    extract_entities->>entities_vdb: upsert(entity_embeddings)
    extract_entities->>graph: upsert_node(entity_id, entity_data)
    extract_entities->>graph: upsert_edge(src_id, tgt_id, edge_data)
    
    MiniRAG->>text_chunks: index_done_callback()
    MiniRAG->>chunks_vdb: index_done_callback()
    MiniRAG->>entities_vdb: index_done_callback()
    MiniRAG->>graph: index_done_callback()
    
    MiniRAG-->>Client: Indexing complete
```

Sources: [minirag/minirag.py:344-389](), [minirag/minirag.py:516-531]()

### Query Integration

During query processing, the `MiniRAG.aquery()` method ([minirag/minirag.py:537-572]()) dispatches to different query modes:

**Sequence Diagram: Mini Query Mode**

```mermaid
sequenceDiagram
    participant Client
    participant MiniRAG
    participant minirag_query as "minirag_query()"
    participant entity_name_vdb as "entity_name_vdb<br/>(BaseVectorStorage)"
    participant graph as "chunk_entity_relation_graph<br/>(BaseGraphStorage)"
    participant text_chunks as "text_chunks<br/>(BaseKVStorage)"
    
    Client->>MiniRAG: aquery(query, mode='mini')
    MiniRAG->>minirag_query: minirag_query(query, ...)
    
    minirag_query->>entity_name_vdb: query(query_entities, top_k)
    entity_name_vdb-->>minirag_query: matching_entities
    
    loop For each entity
        minirag_query->>graph: get_node(entity_id)
        graph-->>minirag_query: entity_data
        minirag_query->>graph: get_node_edges(entity_id)
        graph-->>minirag_query: edges
        
        loop For each edge
            minirag_query->>graph: get_edge(src_id, tgt_id)
            graph-->>minirag_query: edge_data
        end
    end
    
    minirag_query->>minirag_query: extract chunk_ids from graph paths
    minirag_query->>text_chunks: get_by_ids(chunk_ids)
    text_chunks-->>minirag_query: chunk_contents
    
    minirag_query->>minirag_query: build context from chunks
    minirag_query-->>MiniRAG: response
    
    MiniRAG->>text_chunks: query_done_callback()
    MiniRAG->>entity_name_vdb: query_done_callback()
    MiniRAG->>graph: query_done_callback()
    
    MiniRAG-->>Client: response
```

Sources: [minirag/minirag.py:537-580](), [minirag/operate.py]()

## Configuring Storage Backends

Storage backends are configured in the `MiniRAG` dataclass through three string fields ([minirag/minirag.py:130-132]()):

```python
@dataclass
class MiniRAG:
    kv_storage: str = field(default="JsonKVStorage")
    vector_storage: str = field(default="NanoVectorDBStorage")
    graph_storage: str = field(default="NetworkXStorage")
```

These strings must match keys in the `STORAGES` registry. To use a different backend:

**Example 1: Using PostgreSQL Storage**
```python
rag = MiniRAG(
    working_dir="./data",
    kv_storage="PGKVStorage",
    vector_storage="PGVectorStorage",
    graph_storage="PGGraphStorage",
    # PostgreSQL connection config would be in global_config or environment
)
```

**Example 2: Using Weaviate Storage**
```python
rag = MiniRAG(
    working_dir="./data",
    kv_storage="WeaviateKVStorage",
    vector_storage="WeaviateVectorStorage",
    graph_storage="WeaviateGraphStorage",
)
```

**Example 3: Mixed Storage Backends**
```python
rag = MiniRAG(
    working_dir="./data",
    kv_storage="RedisKVStorage",        # Redis for key-value
    vector_storage="ChromaVectorDBStorage",  # Chroma for vectors
    graph_storage="Neo4JStorage",       # Neo4j for graph
)
```

The storage backend resolution happens in `_get_storage_class()` ([minirag/minirag.py:315-318]()), which uses `lazy_external_import()` to dynamically load the implementation.

Sources: [minirag/minirag.py:130-132](), [minirag/minirag.py:207-227](), [minirag/minirag.py:315-318]()

## Storage Backend Requirements

Each storage backend implementation must:

1. **Inherit from the appropriate base class**: `BaseVectorStorage`, `BaseKVStorage`, `BaseGraphStorage`, or `DocStatusStorage`
2. **Implement all abstract methods**: All methods marked as abstract in the base class must be implemented
3. **Accept initialization parameters**: Constructor must accept `namespace`, `global_config`, and `embedding_func`
4. **Provide lifecycle callbacks**: Implement `index_done_callback()` and `query_done_callback()` if needed

**Example Storage Implementation Structure**:

```python
from minirag.base import BaseVectorStorage
from dataclasses import dataclass

@dataclass
class MyCustomVectorStorage(BaseVectorStorage):
    def __post_init__(self):
        # Initialize backend client
        working_dir = self.global_config["working_dir"]
        self.client = MyVectorDBClient(working_dir, self.namespace)
    
    async def query(self, query: str, top_k: int) -> list[dict]:
        # Generate embedding
        embedding = await self.embedding_func([query])
        # Query backend
        return self.client.similarity_search(embedding[0], top_k)
    
    async def upsert(self, data: dict[str, dict]):
        # Generate embeddings for all items
        contents = [v["content"] for v in data.values()]
        embeddings = await self.embedding_func(contents)
        # Insert into backend
        for (key, value), embedding in zip(data.items(), embeddings):
            self.client.insert(key, embedding, value)
    
    async def index_done_callback(self):
        # Persist changes if needed
        self.client.flush()
```

For detailed examples of concrete implementations, see [Storage Implementations](#5).

Sources: [minirag/base.py:62-149]()

## Summary

The Storage Layer in MiniRAG provides a flexible, extensible foundation for persistent data storage. Key features include:

- **Abstraction**: Common interfaces for different storage types
- **Isolation**: Namespace-based separation of storage concerns
- **Persistence**: File-based storage for vectors, key-values, graphs, and document status
- **Integration**: Seamless connection with indexing and query pipelines

For specific implementation details on vector storage, key-value storage, and graph storage, see the corresponding sections in [Storage Implementations](#5).

Sources: [minirag/base.py:48-198]()

---

# Page: Data Processing Pipeline

# Data Processing Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [minirag/api/requirements.txt](minirag/api/requirements.txt)
- [minirag/kg/weaviate_impl.py](minirag/kg/weaviate_impl.py)
- [minirag/minirag.py](minirag/minirag.py)
- [minirag/operate.py](minirag/operate.py)
- [tests/test_weaviate.py](tests/test_weaviate.py)

</details>



This page documents the two-phase workflow in MiniRAG: **Phase 1 (Document Ingestion)** transforms raw documents into a heterogeneous knowledge graph, and **Phase 2 (Query Processing)** retrieves relevant information and generates responses. See page 3.1 for the `MiniRAG` class and page 3.2 for storage abstractions.

## 1. Two-Phase Pipeline Overview

MiniRAG processes data through two distinct phases executed by the `MiniRAG` class in [minirag/minirag.py](minirag/minirag.py):

**Phase 1: Document Ingestion Pipeline**
- Entry point: `insert()` / `ainsert()` methods [minirag/minirag.py:340-389]()
- Transforms documents → text chunks → entities/relations → knowledge graph
- Populates: `full_docs`, `text_chunks`, `chunks_vdb`, `entities_vdb`, `entity_name_vdb`, `relationships_vdb`, `chunk_entity_relation_graph`

**Phase 2: Query Processing Pipeline**
- Entry point: `query()` / `aquery()` methods [minirag/minirag.py:533-572]()
- Dispatches to: `naive_query()`, `hybrid_query()`, or `minirag_query()` based on `QueryParam.mode`
- Reads from: All storage instances populated in Phase 1
- Generates: Context-enhanced LLM responses

### High-Level Two-Phase Architecture

```mermaid
flowchart TB
    subgraph Phase1["Phase 1: Document Ingestion"]
        direction TB
        Doc["insert(string_or_strings)"]
        Doc --> Enqueue["apipeline_enqueue_documents()"]
        Enqueue --> Process["apipeline_process_enqueue_documents()"]
        Process --> Extract["extract_entities()"]
        
        Process --> Storages1["Storage Population"]
        Extract --> Storages1
        
        Storages1 --> FullDocs["full_docs\n(JsonKVStorage)"]
        Storages1 --> TextChunks["text_chunks\n(JsonKVStorage)"]
        Storages1 --> ChunksVDB["chunks_vdb\n(NanoVectorDBStorage)"]
        Storages1 --> EntitiesVDB["entities_vdb\n(NanoVectorDBStorage)"]
        Storages1 --> EntityNameVDB["entity_name_vdb\n(NanoVectorDBStorage)"]
        Storages1 --> RelationshipsVDB["relationships_vdb\n(NanoVectorDBStorage)"]
        Storages1 --> Graph["chunk_entity_relation_graph\n(NetworkXStorage)"]
    end
    
    subgraph Phase2["Phase 2: Query Processing"]
        direction TB
        Query["query(query, param)"]
        Query --> Dispatch{"param.mode?"}
        
        Dispatch -->|"naive"| NaiveQ["naive_query()"]
        Dispatch -->|"light"| HybridQ["hybrid_query()"]
        Dispatch -->|"mini"| MiniQ["minirag_query()"]
        
        NaiveQ --> Response["LLM Response"]
        HybridQ --> Response
        MiniQ --> Response
    end
    
    FullDocs -.reads.-> Phase2
    TextChunks -.reads.-> Phase2
    ChunksVDB -.reads.-> Phase2
    EntitiesVDB -.reads.-> Phase2
    EntityNameVDB -.reads.-> Phase2
    RelationshipsVDB -.reads.-> Phase2
    Graph -.reads.-> Phase2
```

Sources: [minirag/minirag.py:340-389](), [minirag/minirag.py:533-572](), [minirag/minirag.py:254-298]()

## 2. Phase 1: Document Ingestion

Phase 1 transforms raw documents into the heterogeneous knowledge graph through three sub-stages executed by `ainsert()` [minirag/minirag.py:344-389]().

### 2.1 Document Enqueue: `apipeline_enqueue_documents()`

The first sub-stage [minirag/minirag.py:391-449]() validates, deduplicates, and enqueues documents for processing.

**Document Enqueue Pipeline (`apipeline_enqueue_documents`)**

```mermaid
flowchart TB
    Input["input: str | list[str]\nids: str | list[str] | None"]
    Input --> IDCheck{"ids provided?"}
    
    IDCheck -->|"Yes"| ValidateIDs["Validate:\nlen(ids) == len(input)\nids are unique"]
    IDCheck -->|"No"| GenIDs["Generate IDs:\ncompute_mdhash_id(doc, prefix='doc-')"]
    
    ValidateIDs --> CreateContents["contents = {id: doc}"]
    GenIDs --> CreateContents
    
    CreateContents --> Deduplicate["unique_contents =\nReverse dict to deduplicate"]
    
    Deduplicate --> CreateNewDocs["new_docs[id] = {\ncontent, content_summary,\ncontent_length, status: PENDING,\ncreated_at, updated_at\n}"]
    
    CreateNewDocs --> FilterKeys["unique_new_doc_ids =\ndoc_status.filter_keys(all_new_doc_ids)"]
    
    FilterKeys --> Upsert["doc_status.upsert(new_docs)"]
```

**Key Operations:**

| Step | Code Location | Description |
|------|---------------|-------------|
| ID generation | [minirag/minirag.py:416]() | Uses `compute_mdhash_id()` with prefix `"doc-"` |
| Deduplication | [minirag/minirag.py:418-423]() | Reverses content→id mapping to remove duplicate content |
| Metadata enrichment | [minirag/minirag.py:424-433]() | Adds `content_summary`, `content_length`, `status`, timestamps |
| Filtering existing | [minirag/minirag.py:437]() | `doc_status.filter_keys()` returns only new doc IDs |
| Status storage | [minirag/minirag.py:448]() | Stores in `doc_status` with `DocStatus.PENDING` |

Sources: [minirag/minirag.py:391-449](), [minirag/utils.py:compute_mdhash_id]()

### 2.2 Chunk Processing: `apipeline_process_enqueue_documents()`

The second sub-stage [minirag/minirag.py:451-514]() chunks documents and stores them across multiple storage instances.

**Chunk Processing Pipeline (`apipeline_process_enqueue_documents`)**

```mermaid
flowchart TB
    Start["apipeline_process_enqueue_documents()"]
    Start --> GetDocs["Get docs by status:\nPROCESSING, FAILED, PENDING"]
    
    GetDocs --> Batch["Split into batches:\nmax_parallel_insert per batch"]
    
    Batch --> ForEachDoc["For each doc_id, status_doc:"]
    ForEachDoc --> Chunk["chunks = chunking_func(\nstatus_doc.content,\nchunk_overlap_token_size,\nchunk_token_size,\ntiktoken_model_name\n)"]
    
    Chunk --> GenChunkIDs["chunk_id =\ncompute_mdhash_id(content, prefix='chunk-')"]
    
    GenChunkIDs --> ParallelUpsert["asyncio.gather(\nchunks_vdb.upsert(chunks),\nfull_docs.upsert({doc_id: content}),\ntext_chunks.upsert(chunks)\n)"]
    
    ParallelUpsert --> UpdateStatus["doc_status.upsert({\ndoc_id: {\nstatus: PROCESSED,\nchunks_count: len(chunks),\n...\n}\n})"]
```

**Key Operations:**

| Operation | Code Location | Storage Target |
|-----------|---------------|----------------|
| Get pending docs | [minirag/minirag.py:461-465]() | `doc_status.get_docs_by_status()` |
| Batch processing | [minirag/minirag.py:476-479]() | Controlled by `max_parallel_insert` config |
| Chunking | [minirag/minirag.py:484-495]() | Calls `chunking_func` (default: `chunking_by_token_size`) |
| Generate chunk IDs | [minirag/minirag.py:485]() | `compute_mdhash_id(content, prefix="chunk-")` |
| Parallel storage | [minirag/minirag.py:496-500]() | `chunks_vdb`, `full_docs`, `text_chunks` |
| Update status | [minirag/minirag.py:501-513]() | Sets `DocStatus.PROCESSED` |

**`chunking_by_token_size()` Function** [minirag/operate.py:36-54]()

Default chunking implementation:
- Tokenizes with `encode_string_by_tiktoken()`
- Creates overlapping windows: `range(0, len(tokens), max_token_size - overlap_token_size)`
- Returns list of dicts: `{"tokens": int, "content": str, "chunk_order_index": int}`

Sources: [minirag/minirag.py:451-514](), [minirag/operate.py:36-54](), [minirag/utils.py:compute_mdhash_id]()

### 2.3 Entity Extraction: `extract_entities()`

The third sub-stage [minirag/minirag.py:377-387]() calls `extract_entities()` [minirag/operate.py:233-408]() to extract entities and relationships using LLM.

**Entity Extraction Pipeline (`extract_entities`)**

```mermaid
flowchart TB
    Start["extract_entities(\nchunks,\nknowledge_graph_inst,\nentity_vdb,\nentity_name_vdb,\nrelationships_vdb,\nglobal_config\n)"]
    
    Start --> AsyncProcess["For each chunk_key, chunk_dp:\nasyncio.gather(_process_single_content())"]
    
    AsyncProcess --> LLMExtract["llm_model_func(\nPROMPTS['entity_extraction']\n)"]
    
    LLMExtract --> Gleaning["For i in range(entity_extract_max_gleaning):\nllm_model_func(continue_prompt)"]
    
    Gleaning --> Parse["Parse LLM output:\nsplit_string_by_multi_markers()"]
    
    Parse --> ClassifyRecords["Classify records:"]
    ClassifyRecords --> Entities["('entity', name, type, desc)\n→ maybe_nodes[name]"]
    ClassifyRecords --> Relations["('relationship', src, tgt, desc, kw)\n→ maybe_edges[(src,tgt)]"]
    
    Entities --> MergeNodes["_merge_nodes_then_upsert():\nAggregate entity_type, description, source_id"]
    Relations --> MergeEdges["_merge_edges_then_upsert():\nAggregate weight, keywords, description"]
    
    MergeNodes --> GraphUpsert["knowledge_graph_inst.upsert_node()"]
    MergeEdges --> GraphUpsert["knowledge_graph_inst.upsert_edge()"]
    
    GraphUpsert --> VectorUpsert["entity_vdb.upsert()\nentity_name_vdb.upsert()\nrelationships_vdb.upsert()"]
```

**Key Operations:**

| Operation | Code Location | Description |
|-----------|---------------|-------------|
| Prompt formatting | [minirag/operate.py:249-256]() | Uses `PROMPTS["entity_extraction"]` with delimiters |
| LLM extraction | [minirag/operate.py:271]() | `llm_model_func(hint_prompt)` |
| Gleaning loop | [minirag/operate.py:274-287]() | Iterative refinement up to `entity_extract_max_gleaning` times |
| Record parsing | [minirag/operate.py:289-292]() | Splits by `record_delimiter` and `completion_delimiter` |
| Entity handling | [minirag/operate.py:304-309]() | `_handle_single_entity_extraction()` |
| Relation handling | [minirag/operate.py:311-317]() | `_handle_single_relationship_extraction()` |
| Node merging | [minirag/operate.py:117-163]() | `_merge_nodes_then_upsert()` aggregates duplicate entities |
| Edge merging | [minirag/operate.py:166-230]() | `_merge_edges_then_upsert()` aggregates duplicate relationships |
| Vector storage | [minirag/operate.py:364-406]() | Stores in `entities_vdb`, `entity_name_vdb`, `relationships_vdb` |

**Entity Extraction Format:**

Entities: `("entity", "<NAME>", "<TYPE>", "<DESCRIPTION>")`  
Relationships: `("relationship", "<SRC>", "<TGT>", "<DESCRIPTION>", "<KEYWORDS>", <WEIGHT>)`

Sources: [minirag/minirag.py:377-387](), [minirag/operate.py:233-408](), [minirag/operate.py:70-114](), [minirag/operate.py:117-230]()

## 3. Phase 2: Query Processing

Phase 2 retrieves relevant information and generates responses. Entry point is `aquery()` [minirag/minirag.py:537-572]() which dispatches to mode-specific functions based on `QueryParam.mode`.

### 3.1 Query Dispatch: `aquery()`

The `aquery()` method [minirag/minirag.py:537-572]() routes queries to one of three implementations in [minirag/operate.py](minirag/operate.py).

**Query Dispatch Logic**

```mermaid
flowchart TB
    Entry["query(query, param: QueryParam)\n↓\naquery(query, param)"]
    
    Entry --> Mode{"param.mode?"}
    
    Mode -->|"'naive'"| Naive["response = await naive_query(\nquery,\nchunks_vdb,\ntext_chunks,\nparam,\nglobal_config\n)"]
    
    Mode -->|"'light'"| Light["response = await hybrid_query(\nquery,\nchunk_entity_relation_graph,\nentities_vdb,\nrelationships_vdb,\ntext_chunks,\nparam,\nglobal_config\n)"]
    
    Mode -->|"'mini'"| Mini["response = await minirag_query(\nquery,\nchunk_entity_relation_graph,\nentities_vdb,\nentity_name_vdb,\nrelationships_vdb,\nchunks_vdb,\ntext_chunks,\nembedding_func,\nparam,\nglobal_config\n)"]
    
    Mode -->|"other"| Error["raise ValueError(f'Unknown mode {param.mode}')"]
    
    Naive --> Done["_query_done()"]
    Light --> Done
    Mini --> Done
    
    Done --> Return["return response"]
```

**Mode Comparison:**

| Mode | Function | Storage Used | Key Characteristic |
|------|----------|--------------|-------------------|
| `"naive"` | `naive_query()` | `chunks_vdb`, `text_chunks` | Direct vector similarity search |
| `"light"` | `hybrid_query()` | All except `entity_name_vdb`, `chunks_vdb` | Local + global context combining |
| `"mini"` | `minirag_query()` | All storage instances | Topology-enhanced graph traversal |

Sources: [minirag/minirag.py:537-572](), [minirag/minirag.py:533-535]()

### 3.2 Naive Mode: `naive_query()`

Simplest mode using direct vector similarity search without knowledge graph [minirag/operate.py:1076-1121]().

**Naive Query Pipeline**

```mermaid
flowchart TB
    Start["naive_query(\nquery,\nchunks_vdb,\ntext_chunks_db,\nquery_param,\nglobal_config\n)"]
    
    Start --> VectorQuery["results = await chunks_vdb.query(\nquery,\ntop_k=query_param.top_k\n)"]
    
    VectorQuery --> ExtractIDs["chunks_ids = [r['id'] for r in results]"]
    
    ExtractIDs --> GetChunks["chunks = await text_chunks_db.get_by_ids(\nchunks_ids\n)"]
    
    GetChunks --> Truncate["maybe_trun_chunks = truncate_list_by_token_size(\nchunks,\nkey=lambda x: x['content'],\nmax_token_size=query_param.max_token_for_text_unit\n)"]
    
    Truncate --> CheckContext{"query_param.only_need_context?"}
    
    CheckContext -->|"True"| ReturnSection["return '--New Chunk--\\n'.join(\n[c['content'] for c in chunks]\n)"]
    
    CheckContext -->|"False"| BuildPrompt["sys_prompt = PROMPTS['naive_rag_response'].format(\ncontent_data=section,\nresponse_type=query_param.response_type\n)"]
    
    BuildPrompt --> LLMCall["response = await llm_model_func(\nquery,\nsystem_prompt=sys_prompt\n)"]
    
    LLMCall --> CleanResponse["Strip sys_prompt, 'user', 'model', etc."]
    
    CleanResponse --> Return["return response"]
```

**Key Characteristics:**
- **No graph traversal**: Only uses vector similarity
- **Simple retrieval**: Direct `chunks_vdb.query()` → `text_chunks_db.get_by_ids()`
- **Token truncation**: Uses `truncate_list_by_token_size()` to fit context window
- **Prompt template**: Uses `PROMPTS["naive_rag_response"]` [minirag/operate.py:1100]()

Sources: [minirag/operate.py:1076-1121](), [minirag/minirag.py:561-568]()

### 3.3 Light Mode: `hybrid_query()`

Combines local (entity-centric) and global (relationship-centric) contexts [minirag/operate.py:918-1004]().

**Hybrid Query Pipeline**

```mermaid
flowchart TB
    Start["hybrid_query(\nquery,\nknowledge_graph_inst,\nentities_vdb,\nrelationships_vdb,\ntext_chunks_db,\nquery_param,\nglobal_config\n)"]
    
    Start --> ExtractKW["kw_prompt = PROMPTS['keywords_extraction'].format(query=query)\nresult = await llm_model_func(kw_prompt)\nkeywords_data = json.loads(result)"]
    
    ExtractKW --> ParseKW["hl_keywords = keywords_data['high_level_keywords']\nll_keywords = keywords_data['low_level_keywords']"]
    
    ParseKW --> ParallelRetrieval["Parallel Context Building:"]
    
    ParallelRetrieval --> LocalContext["IF ll_keywords:\nlow_level_context = await _build_local_query_context(\nll_keywords,\nknowledge_graph_inst,\nentities_vdb,\ntext_chunks_db,\nquery_param\n)"]
    
    ParallelRetrieval --> GlobalContext["IF hl_keywords:\nhigh_level_context = await _build_global_query_context(\nhl_keywords,\nknowledge_graph_inst,\nentities_vdb,\nrelationships_vdb,\ntext_chunks_db,\nquery_param\n)"]
    
    LocalContext --> Combine["context = combine_contexts(\nhigh_level_context,\nlow_level_context\n)"]
    GlobalContext --> Combine
    
    Combine --> CheckOnly{"query_param.only_need_context?"}
    
    CheckOnly -->|"True"| ReturnContext["return context"]
    
    CheckOnly -->|"False"| BuildPrompt["sys_prompt = PROMPTS['rag_response'].format(\ncontext_data=context,\nresponse_type=query_param.response_type\n)"]
    
    BuildPrompt --> LLMCall["response = await llm_model_func(\nquery,\nsystem_prompt=sys_prompt\n)"]
    
    LLMCall --> Return["return response"]
```

**Context Building Functions:**

| Function | Storage Query | Graph Operation | Output |
|----------|---------------|-----------------|--------|
| `_build_local_query_context()` [minirag/operate.py:483-563]() | `entities_vdb.query()` | `get_node()`, `get_node_edges()` | CSV tables: entities, relationships, sources |
| `_build_global_query_context()` [minirag/operate.py:754-847]() | `relationships_vdb.query()` | `get_edge()`, `edge_degree()` | CSV tables: relationships, entities, sources |
| `combine_contexts()` [minirag/operate.py:1007-1073]() | N/A | N/A | Merged CSV tables with deduplication |

Sources: [minirag/operate.py:918-1004](), [minirag/operate.py:483-563](), [minirag/operate.py:754-847](), [minirag/minirag.py:538-546]()

### 3.4 Mini Mode: `minirag_query()`

Most advanced mode using topology-enhanced retrieval with knowledge graph traversal. Implementation in [minirag/operate.py](minirag/operate.py) (function not shown in provided files, but called at [minirag/minirag.py:548-559]()).

**Mini Mode Characteristics:**

The `minirag_query()` function is called with all storage instances:
```python
response = await minirag_query(
    query,
    self.chunk_entity_relation_graph,    # Graph for traversal
    self.entities_vdb,                   # Entity descriptions
    self.entity_name_vdb,                # Entity names only
    self.relationships_vdb,              # Relationship data
    self.chunks_vdb,                     # Chunk embeddings
    self.text_chunks,                    # Chunk content
    self.embedding_func,                 # Embedding function
    param,
    asdict(self),
)
```

**Key Differences from Light Mode:**
- Uses `entity_name_vdb` for precise entity matching
- Uses `chunks_vdb` for chunk-level similarity
- Implements graph topology-based reasoning paths
- Optimized for small language models with reduced semantic understanding burden

Sources: [minirag/minirag.py:548-559]()

## 4. Storage Layer Interaction

MiniRAG instantiates 8 storage instances in `__post_init__()` [minirag/minirag.py:190-313]().

### 4.1 Storage Instance Initialization

**Storage Instances Created in `MiniRAG.__post_init__()`**

```mermaid
flowchart TB
    PostInit["__post_init__()"]
    
    PostInit --> GetClasses["_get_storage_class():\nkv_storage → JsonKVStorage\nvector_storage → NanoVectorDBStorage\ngraph_storage → NetworkXStorage\ndoc_status_storage → JsonDocStatusStorage"]
    
    GetClasses --> CreateInstances["Create storage instances with namespace and embedding_func:"]
    
    CreateInstances --> DocStatusInst["doc_status =\nJsonDocStatusStorage(\nnamespace='doc_status',\nembedding_func=None\n)"]
    
    CreateInstances --> LLMCacheInst["llm_response_cache =\nJsonKVStorage(\nnamespace='llm_response_cache',\nembedding_func=None\n)"]
    
    CreateInstances --> FullDocsInst["full_docs =\nJsonKVStorage(\nnamespace='full_docs',\nembedding_func=embedding_func\n)"]
    
    CreateInstances --> TextChunksInst["text_chunks =\nJsonKVStorage(\nnamespace='text_chunks',\nembedding_func=embedding_func\n)"]
    
    CreateInstances --> GraphInst["chunk_entity_relation_graph =\nNetworkXStorage(\nnamespace='chunk_entity_relation',\nembedding_func=embedding_func\n)"]
    
    CreateInstances --> ChunksVDBInst["chunks_vdb =\nNanoVectorDBStorage(\nnamespace='chunks',\nembedding_func=embedding_func\n)"]
    
    CreateInstances --> EntitiesVDBInst["entities_vdb =\nNanoVectorDBStorage(\nnamespace='entities',\nembedding_func=embedding_func,\nmeta_fields={'entity_name'}\n)"]
    
    CreateInstances --> EntityNameVDBInst["entity_name_vdb =\nNanoVectorDBStorage(\nnamespace='entities_name',\nembedding_func=embedding_func,\nmeta_fields={'entity_name'}\n)"]
    
    CreateInstances --> RelationshipsVDBInst["relationships_vdb =\nNanoVectorDBStorage(\nnamespace='relationships',\nembedding_func=embedding_func,\nmeta_fields={'src_id', 'tgt_id'}\n)"]
```

**Storage Instance Reference Table:**

| Attribute | Type | Namespace | Purpose | Embedding |
|-----------|------|-----------|---------|-----------|
| `doc_status` | `JsonDocStatusStorage` | `"doc_status"` | Document processing status tracking | None |
| `llm_response_cache` | `JsonKVStorage` | `"llm_response_cache"` | Cache LLM responses | None |
| `full_docs` | `JsonKVStorage` | `"full_docs"` | Original document content | Yes |
| `text_chunks` | `JsonKVStorage` | `"text_chunks"` | Chunked text content | Yes |
| `chunk_entity_relation_graph` | `NetworkXStorage` | `"chunk_entity_relation"` | Knowledge graph (nodes + edges) | Yes |
| `chunks_vdb` | `NanoVectorDBStorage` | `"chunks"` | Chunk embeddings for similarity search | Yes |
| `entities_vdb` | `NanoVectorDBStorage` | `"entities"` | Entity embeddings (name + description) | Yes |
| `entity_name_vdb` | `NanoVectorDBStorage` | `"entities_name"` | Entity name-only embeddings | Yes |
| `relationships_vdb` | `NanoVectorDBStorage` | `"relationships"` | Relationship embeddings | Yes |

Sources: [minirag/minirag.py:228-313](), [minirag/minirag.py:207-227]()

### 4.2 Storage Usage by Phase

**Phase 1 (Indexing) Storage Writes:**

```mermaid
flowchart LR
    subgraph Phase1Writes["Phase 1: Storage Writes"]
        direction TB
        
        Enqueue["apipeline_enqueue_documents()"] --> DocStatusW["doc_status.upsert():\nPENDING status"]
        
        Process["apipeline_process_enqueue_documents()"] --> FullDocsW["full_docs.upsert():\nOriginal document"]
        Process --> TextChunksW1["text_chunks.upsert():\nChunk content + metadata"]
        Process --> ChunksVDBW["chunks_vdb.upsert():\nChunk embeddings"]
        Process --> DocStatusW2["doc_status.upsert():\nPROCESSED status"]
        
        Extract["extract_entities()"] --> GraphW["chunk_entity_relation_graph:\nupsert_node(), upsert_edge()"]
        Extract --> EntitiesVDBW["entities_vdb.upsert():\nEntity name + description"]
        Extract --> EntityNameVDBW["entity_name_vdb.upsert():\nEntity name only"]
        Extract --> RelationshipsVDBW["relationships_vdb.upsert():\nRelationship data"]
    end
```

**Phase 2 (Query) Storage Reads:**

```mermaid
flowchart LR
    subgraph Phase2Reads["Phase 2: Storage Reads"]
        direction TB
        
        NaiveMode["naive_query()"] --> ChunksVDBR1["chunks_vdb.query():\nVector similarity search"]
        ChunksVDBR1 --> TextChunksR1["text_chunks.get_by_ids():\nRetrieve content"]
        
        HybridMode["hybrid_query()"] --> EntitiesVDBR["entities_vdb.query():\nEntity search"]
        HybridMode --> RelationshipsVDBR["relationships_vdb.query():\nRelationship search"]
        EntitiesVDBR --> GraphR1["chunk_entity_relation_graph:\nget_node(), get_node_edges()"]
        RelationshipsVDBR --> GraphR2["chunk_entity_relation_graph:\nget_edge(), edge_degree()"]
        GraphR1 --> TextChunksR2["text_chunks.get_by_ids():\nRetrieve content"]
        GraphR2 --> TextChunksR2
        
        MiniMode["minirag_query()"] --> EntityNameVDBR["entity_name_vdb.query():\nEntity name search"]
        MiniMode --> ChunksVDBR2["chunks_vdb.query():\nChunk search"]
        EntityNameVDBR --> GraphR3["chunk_entity_relation_graph:\nGraph traversal"]
        GraphR3 --> TextChunksR3["text_chunks.get_by_ids():\nRetrieve content"]
        
        AllModes["All query modes"] --> LLMCacheRW["llm_response_cache:\nget() / upsert()"]
    end
```

Sources: [minirag/minirag.py:391-514](), [minirag/operate.py:233-408](), [minirag/minirag.py:537-572]()

## 5. Configuration Parameters

Key configuration parameters affecting the data processing pipeline:

### 5.1 Document Processing Configuration

| Parameter | Type | Default | Impact |
|-----------|------|---------|--------|
| `chunk_token_size` | `int` | `1200` | Maximum tokens per chunk in `chunking_by_token_size()` |
| `chunk_overlap_token_size` | `int` | `100` | Overlap between adjacent chunks |
| `tiktoken_model_name` | `str` | `"gpt-4o-mini"` | Tokenizer model for chunking |
| `chunking_func` | `callable` | `chunking_by_token_size` | Custom chunking function |
| `max_parallel_insert` | `int` | `int(os.getenv("MAX_PARALLEL_INSERT", 2))` | Parallel document batch size |

### 5.2 Entity Extraction Configuration

| Parameter | Type | Default | Impact |
|-----------|------|---------|--------|
| `entity_extract_max_gleaning` | `int` | `1` | Iterative LLM extraction rounds |
| `entity_summary_to_max_tokens` | `int` | `500` | Max tokens for entity/relation summaries |
| `llm_model_func` | `callable` | Required | LLM function for entity extraction |
| `llm_model_max_async` | `int` | `16` | Parallel LLM calls limit |

### 5.3 Storage Configuration

| Parameter | Type | Default | Impact |
|-----------|------|---------|--------|
| `kv_storage` | `str` | `"JsonKVStorage"` | Key-value storage implementation |
| `vector_storage` | `str` | `"NanoVectorDBStorage"` | Vector storage implementation |
| `graph_storage` | `str` | `"NetworkXStorage"` | Graph storage implementation |
| `doc_status_storage` | `str` | `"JsonDocStatusStorage"` | Document status tracking implementation |
| `working_dir` | `str` | `"./minirag_cache_{timestamp}"` | Storage directory |

### 5.4 Query Configuration (via `QueryParam`)

| Parameter | Type | Default | Impact |
|-----------|------|---------|--------|
| `mode` | `str` | Required | Query mode: `"naive"`, `"light"`, `"mini"` |
| `top_k` | `int` | Varies | Number of results from vector search |
| `max_token_for_text_unit` | `int` | Varies | Token limit for retrieved chunks |
| `max_token_for_local_context` | `int` | Varies | Token limit for local context (light mode) |
| `max_token_for_global_context` | `int` | Varies | Token limit for global context (light mode) |
| `only_need_context` | `bool` | `False` | Return context without LLM generation |

Sources: [minirag/minirag.py:122-189](), [minirag/base.py:QueryParam]()

## 6. Configuration Impact on Data Flow

Configuration parameters significantly affect how data flows through MiniRAG:

| Configuration Parameter | Impact on Data Flow |
|-------------------------|---------------------|
| `chunk_token_size` | Controls size of text chunks during document processing |
| `chunk_overlap_token_size` | Determines overlap between adjacent chunks |
| `entity_extract_max_gleaning` | Controls how many rounds of entity extraction are performed |
| `embedding_func` | Function used to convert text to vector embeddings |
| `embedding_func_max_async` | Limits parallel embedding operations |
| `llm_model_func` | Function used for generating LLM responses |
| `kv_storage`, `vector_storage`, `graph_storage` | Determine storage implementations used |
| `max_parallel_insert` | Controls parallelism during document insertion |

Sources: [minirag/minirag.py:118-185](), [minirag/operate.py:242-247]()

---

# Page: Core Concepts

# Core Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [minirag/api/requirements.txt](minirag/api/requirements.txt)
- [minirag/operate.py](minirag/operate.py)

</details>



This page provides a comprehensive technical explanation of the core algorithms and concepts that power MiniRAG. It covers the two fundamental innovations—heterogeneous graph indexing and topology-enhanced retrieval—as well as the five query modes that balance performance and complexity. 

For implementation details of these concepts in the codebase, see [System Architecture](#3). For specific storage backend implementations, see [Storage Implementations](#5). For practical usage examples, see [Usage Examples](#8).

## Overview

MiniRAG achieves efficient RAG performance on Small Language Models (SLMs) through two key technical innovations that work together to reduce the semantic understanding burden placed on the language model:

1. **Heterogeneous Graph Indexing**: Unifies text chunks and named entities into a single graph structure, providing explicit semantic relationships rather than relying solely on embedding similarity
2. **Topology-Enhanced Retrieval**: Leverages graph structure for efficient knowledge discovery through traversal, enabling reasoning without requiring advanced language capabilities

These innovations are implemented across the indexing and query phases, creating a two-stage pipeline that separates knowledge organization from retrieval.

**Sources:** [README.md:30-34](), [README.md:36-40]()

---

## Heterogeneous Graph Indexing

### Concept and Structure

Heterogeneous graph indexing combines two types of nodes in a unified graph structure:

1. **Entity Nodes**: Named entities extracted from documents (people, places, concepts)
2. **Text Chunk Nodes**: Implicitly represented through source IDs stored in entity and relationship metadata

This dual representation allows the system to navigate between semantic concepts (entities) and raw text evidence (chunks) efficiently. Unlike traditional knowledge graphs that only store entities and relationships, or vector databases that only store embeddings, MiniRAG's heterogeneous structure maintains explicit links between both levels of abstraction.

```mermaid
graph TB
    subgraph "Heterogeneous Graph Structure"
        subgraph "Entity Layer"
            E1["Entity: LIHUA<br/>Type: PERSON<br/>Description: Virtual user..."]
            E2["Entity: WORK_PROJECT<br/>Type: EVENT<br/>Description: Project deadline..."]
            E3["Entity: COLLEAGUE_ZHANG<br/>Type: PERSON<br/>Description: Team member..."]
        end
        
        subgraph "Relationship Layer"
            R1["works_on<br/>weight: 2.0<br/>keywords: project, deadline"]
            R2["collaborates_with<br/>weight: 1.5<br/>keywords: team, meeting"]
        end
        
        subgraph "Text Chunk Layer"
            C1["Chunk_001<br/>Content: LiHua discussed the project..."]
            C2["Chunk_015<br/>Content: Meeting with Zhang..."]
            C3["Chunk_042<br/>Content: Project deadline extended..."]
        end
    end
    
    E1 -->|"source_id"| C1
    E2 -->|"source_id"| C3
    E3 -->|"source_id"| C2
    
    E1 -->|R1| E2
    E1 -->|R2| E3
    E2 -->|"source_id"| C1
    
    R1 -.->|"source_id"| C1
    R2 -.->|"source_id"| C2
```

**Sources:** [README.md:30-34](), [minirag/operate.py:117-163]()

### Entity Extraction Process

The entity extraction process transforms raw text into structured graph elements through LLM-based extraction. The workflow follows a multi-step gleaning approach to ensure comprehensive extraction:

```mermaid
sequenceDiagram
    participant Chunk as "Text Chunk"
    participant Extract as "extract_entities()<br/>operate.py:233"
    participant LLM as "LLM Model"
    participant Parse as "Parsing Logic"
    participant Graph as "BaseGraphStorage"
    participant VDB as "VectorStorage"
    
    Chunk->>Extract: "content"
    Extract->>LLM: "entity_extraction prompt"
    LLM-->>Extract: "CSV formatted entities/relationships"
    
    loop "Gleaning (max iterations)"
        Extract->>LLM: "continue extraction prompt"
        LLM-->>Extract: "Additional entities"
        Extract->>LLM: "if_loop prompt"
        LLM-->>Extract: "yes/no"
        alt "no more entities"
            Note over Extract: Break loop
        end
    end
    
    Extract->>Parse: "Raw extraction result"
    Parse->>Parse: "_handle_single_entity_extraction()<br/>operate.py:70"
    Parse->>Parse: "_handle_single_relationship_extraction()<br/>operate.py:91"
    
    Parse->>Extract: "Entity list, Relationship list"
    Extract->>Extract: "_merge_nodes_then_upsert()<br/>operate.py:117"
    Extract->>Extract: "_merge_edges_then_upsert()<br/>operate.py:166"
    
    Extract->>Graph: "upsert_node(entity_name, node_data)"
    Extract->>Graph: "upsert_edge(src_id, tgt_id, edge_data)"
    Extract->>VDB: "upsert(entity_embeddings)"
```

**Sources:** [minirag/operate.py:233-408](), [minirag/operate.py:70-114]()

### Entity and Relationship Schema

The extraction process follows a structured CSV format with specific delimiters defined in the prompt system:

| Element Type | Format | Attributes | Example |
|--------------|--------|------------|---------|
| **Entity** | `("entity", NAME, TYPE, DESCRIPTION)` | entity_name, entity_type, description, source_id | `("entity", "LIHUA", "PERSON", "Virtual user in chat logs")` |
| **Relationship** | `("relationship", SRC, TGT, DESC, KEYWORDS, WEIGHT)` | src_id, tgt_id, description, keywords, weight, source_id | `("relationship", "LIHUA", "PROJECT", "works on", "deadline, task", 1.0)` |

The schema uses several key separators defined in [minirag/prompt.py]():
- **Tuple Delimiter**: Separates attributes within a record
- **Record Delimiter**: Separates multiple extraction records
- **Completion Delimiter**: Marks end of extraction
- **GRAPH_FIELD_SEP**: Used to concatenate multiple values (e.g., multiple source_ids)

**Sources:** [minirag/operate.py:74-88](), [minirag/operate.py:95-114]()

### Node and Edge Merging Strategy

When processing multiple chunks that reference the same entities, MiniRAG merges information to create consolidated nodes and edges:

**Node Merging** [minirag/operate.py:117-163]():
1. Check if entity already exists in graph
2. Aggregate entity types (most common wins)
3. Concatenate descriptions using `GRAPH_FIELD_SEP`
4. Combine source_ids from all chunks mentioning this entity

**Edge Merging** [minirag/operate.py:166-230]():
1. Check if edge already exists between nodes
2. Sum weights from all occurrences
3. Concatenate descriptions and keywords
4. Combine source_ids
5. Create placeholder nodes for missing entities (`"UNKNOWN"` type)

This merging strategy ensures that entities mentioned across multiple documents are unified into single nodes with comprehensive metadata, enabling more accurate retrieval.

**Sources:** [minirag/operate.py:117-230]()

---

## Topology-Enhanced Retrieval

### Graph Traversal Fundamentals

Topology-enhanced retrieval exploits the explicit graph structure to discover relevant information through traversal rather than purely semantic similarity. This approach is particularly effective for SLMs because it reduces the model's burden—instead of understanding complex relationships through language alone, the model can follow pre-computed graph connections.

The core concept involves finding **reasoning paths** between query entities and potential answer entities by traversing the graph structure.

```mermaid
graph LR
    subgraph "Query Processing Flow"
        Q["User Query:<br/>What project is LiHua<br/>working on?"]
        
        Q -->|"Extract entities"| QE["Query Entities:<br/>[LIHUA]"]
        Q -->|"Extract types"| QT["Expected Answer Types:<br/>[PROJECT, EVENT]"]
        
        QE -->|"Vector search<br/>entity_name_vdb"| CE["Candidate Entities:<br/>LIHUA (0.95)<br/>LI_HUA (0.82)"]
        
        CE -->|"get_neighbors_within_k_hops()<br/>k=2"| RP["Reasoning Paths:<br/>LIHUA -> works_on -> PROJECT_A<br/>LIHUA -> collaborates -> ZHANG -> assigned_to -> PROJECT_A"]
        
        QT -->|"get_node_from_types()"| AE["Answer Candidates:<br/>PROJECT_A (type: PROJECT)<br/>PROJECT_B (type: PROJECT)"]
        
        RP -->|"Path Scoring"| SP["Scored Paths:<br/>Path 1: Score 0.85<br/>Path 2: Score 0.63"]
        
        SP -->|"path2chunk()"| TC["Relevant Text Chunks:<br/>chunk_001, chunk_015, chunk_042"]
        
        TC --> Ctx["Context for LLM"]
        SP --> Ctx
    end
```

**Sources:** [minirag/operate.py:1252-1407](), [minirag/operate.py:1409-1479]()

### K-Hop Neighbor Discovery

The `get_neighbors_within_k_hops()` method (implemented in [BaseGraphStorage interface](minirag/base.py)) performs breadth-first traversal to find all nodes reachable within k steps from a starting entity. For MiniRAG's mini query mode, k=2 is typically used:

**K-Hop Example:**
- **1-hop neighbors**: Direct connections (e.g., LIHUA → PROJECT_A)
- **2-hop neighbors**: Connections through intermediary (e.g., LIHUA → ZHANG → PROJECT_B)

The reasoning path structure returned is a dictionary mapping path tuples to metadata:

```python
# Conceptual structure returned by get_neighbors_within_k_hops
{
    ("LIHUA", "PROJECT_A"): {"score": 0.85, "path_length": 1},
    ("LIHUA", "ZHANG", "PROJECT_B"): {"score": 0.63, "path_length": 2}
}
```

**Sources:** [minirag/operate.py:1289-1292]()

### Path Scoring Algorithm

The `cal_path_score_list()` function [minirag/utils.py]() assigns scores to reasoning paths based on:

1. **Vector similarity score**: Distance of starting entity from query embedding
2. **Path length**: Shorter paths generally more relevant
3. **Answer type match**: Bonus for paths ending at expected answer types
4. **Edge voting**: Relationships that appear in relationship vector search results boost connected paths

The scoring formula combines these factors to rank paths:

```
path_score = entity_similarity * length_penalty * type_bonus * edge_vote_weight
```

The `edge_vote_path()` function [minirag/utils.py]() cross-references paths with retrieved relationships, identifying which edges in the path appear in top relationship search results. This provides an additional signal for path quality.

**Sources:** [minirag/operate.py:1317-1333](), [minirag/utils.py]()

### From Paths to Chunks

The `path2chunk()` function [minirag/operate.py:1124-1209]() converts scored reasoning paths into ranked text chunks:

1. **Extract source_ids**: For each node and edge in path, retrieve associated chunk IDs
2. **Count occurrences**: Build a Counter of chunk IDs weighted by path scores
3. **Similarity filtering**: For nodes with many chunks, use `calculate_similarity()` to select most relevant
4. **Ranking**: Return top-k chunks by weighted frequency

This ensures that the final context includes text chunks that provide evidence for the reasoning paths, giving the LLM both structured (entities/relationships) and unstructured (original text) information.

**Sources:** [minirag/operate.py:1124-1209](), [minirag/operate.py:1373-1379]()

---

## Query Modes

MiniRAG implements five distinct query modes, each offering different trade-offs between retrieval quality, computational cost, and suitability for SLMs versus LLMs.

### Query Mode Architecture

```mermaid
graph TB
    Query["User Query"]
    
    Query --> Mode{Select Query Mode}
    
    Mode -->|"mode='naive'"| Naive["naive_query()<br/>operate.py:1076"]
    Mode -->|"mode='local'"| Local["local_query()<br/>operate.py:411"]
    Mode -->|"mode='mini'"| Mini["minirag_query()<br/>operate.py:1409"]
    Mode -->|"mode='global'"| Global["global_query()<br/>operate.py:678"]
    Mode -->|"mode='hybrid'"| Hybrid["hybrid_query()<br/>operate.py:918"]
    
    subgraph "Naive Mode - Vector Only"
        Naive --> NV["chunks_vdb.query()"]
        NV --> NChunks["Top-K Text Chunks"]
        NChunks --> NPrompt["naive_rag_response prompt"]
    end
    
    subgraph "Local Mode - Entity-Centric"
        Local --> LKW["Extract low_level_keywords"]
        LKW --> LEnt["entities_vdb.query()"]
        LEnt --> L1Hop["Get 1-hop neighbors"]
        L1Hop --> LChunks["Find related chunks"]
        LChunks --> LPrompt["rag_response prompt"]
    end
    
    subgraph "Mini Mode - Reasoning Paths"
        Mini --> MKW["Extract entities_from_query<br/>+ answer_type_keywords"]
        MKW --> MEnt["entity_name_vdb.query()"]
        MEnt --> M2Hop["Get 2-hop reasoning paths"]
        M2Hop --> MScore["Score paths + edge voting"]
        MScore --> MPath["path2chunk()"]
        MPath --> MPrompt["rag_response prompt"]
    end
    
    subgraph "Global Mode - Relationship-Centric"
        Global --> GKW["Extract high_level_keywords"]
        GKW --> GRel["relationships_vdb.query()"]
        GRel --> GEnt["Find entities from relationships"]
        GEnt --> GChunks["Find related chunks"]
        GChunks --> GPrompt["rag_response prompt"]
    end
    
    subgraph "Hybrid Mode - Combined"
        Hybrid --> HKW["Extract high + low keywords"]
        HKW --> HLocal["Build local context"]
        HKW --> HGlobal["Build global context"]
        HLocal --> Combine["combine_contexts()"]
        HGlobal --> Combine
        Combine --> HPrompt["rag_response prompt"]
    end
```

**Sources:** [minirag/operate.py:411-1479]()

### Naive Mode

**Function:** `naive_query()` [minirag/operate.py:1076-1121]()

The simplest mode that bypasses the knowledge graph entirely. It performs standard vector similarity search on text chunks and directly generates answers.

**Workflow:**
1. Query `chunks_vdb` for top-k most similar chunks
2. Retrieve full chunk content from `text_chunks_db`
3. Truncate chunks to fit within token budget
4. Generate response using `naive_rag_response` prompt

**When to use:** Baseline comparison, simple factual queries, when graph construction overhead isn't justified

**Limitations:** No reasoning across documents, no entity-relationship awareness, relies entirely on embedding similarity

**Sources:** [minirag/operate.py:1076-1121]()

### Local Mode (Light)

**Function:** `local_query()` [minirag/operate.py:411-480]()

Focuses on entity-centric retrieval using immediate graph neighborhoods. Suitable for queries about specific entities where direct relationships provide sufficient context.

**Workflow:**
1. Extract `low_level_keywords` from query
2. Query `entities_vdb` to find relevant entity nodes
3. Retrieve 1-hop neighbors for each entity
4. Find text chunks associated with entities and their neighbors via `_find_most_related_text_unit_from_entities()` [minirag/operate.py:566-641]()
5. Find relationships between entities via `_find_most_related_edges_from_entities()` [minirag/operate.py:644-675]()
6. Format as CSV context with entities, relationships, and sources

**Context Structure:**
```
-----Entities-----
```csv
id,entity,type,description,rank
0,LIHUA,PERSON,"Virtual user",5
1,PROJECT_A,EVENT,"Work deadline",3
```

-----Relationships-----
```csv
id,source,target,description,keywords,weight,rank
0,LIHUA,PROJECT_A,"works on","deadline",2.0,4
```

-----Sources-----
```csv
id,content
0,"LiHua discussed the project deadline..."
```
```

**When to use:** Single-hop questions, entity-focused queries, SLMs with moderate capability

**Sources:** [minirag/operate.py:411-563]()

### Mini Mode (MiniRAG)

**Function:** `minirag_query()` [minirag/operate.py:1409-1479]()

The signature MiniRAG mode that uses topology-enhanced retrieval with reasoning paths. Optimized for SLMs by providing explicit reasoning structure.

**Workflow:**
1. Extract `entities_from_query` and `answer_type_keywords` using `minirag_query2kwd` prompt [minirag/operate.py:1422-1424]()
2. Query `entity_name_vdb` to find candidate entities
3. Call `get_neighbors_within_k_hops(k=2)` to find 2-hop reasoning paths
4. Get nodes matching expected answer types via `get_node_from_types()`
5. Score paths using `cal_path_score_list()` to rank by relevance
6. Query `relationships_vdb` and boost paths with matching edges via `edge_vote_path()`
7. Convert paths to chunks using `path2chunk()` with similarity filtering
8. Build context via `_build_mini_query_context()` [minirag/operate.py:1252-1406]()

**Key Innovation:** The combination of type-based filtering and path scoring reduces the reasoning burden on SLMs by providing pre-computed connection structures.

**When to use:** Multi-hop reasoning, complex queries requiring entity chains, deployment on SLMs (1.5B-4B parameters)

**Sources:** [minirag/operate.py:1409-1479](), [minirag/operate.py:1252-1406]()

### Global Mode

**Function:** `global_query()` [minirag/operate.py:678-751]()

Relationship-centric retrieval that starts from high-level relationships rather than entities. Useful for understanding connections and patterns.

**Workflow:**
1. Extract `high_level_keywords` from query
2. Query `relationships_vdb` to find relevant relationships
3. Retrieve edge metadata and compute edge degrees
4. Find entities involved in relationships via `_find_most_related_entities_from_relationships()` [minirag/operate.py:850-878]()
5. Find associated text chunks via `_find_related_text_unit_from_relationships()` [minirag/operate.py:881-915]()
6. Build context via `_build_global_query_context()` [minirag/operate.py:754-847]()

**When to use:** Queries about relationships/patterns, summarization tasks, understanding system-level connections

**Sources:** [minirag/operate.py:678-847]()

### Hybrid Mode

**Function:** `hybrid_query()` [minirag/operate.py:918-1004]()

Combines local (entity-centric) and global (relationship-centric) contexts for comprehensive coverage. Balances breadth and depth.

**Workflow:**
1. Extract both `high_level_keywords` and `low_level_keywords`
2. Build local context via `_build_local_query_context()` [minirag/operate.py:483-563]()
3. Build global context via `_build_global_query_context()` [minirag/operate.py:754-847]()
4. Merge contexts using `combine_contexts()` [minirag/operate.py:1007-1073]() which:
   - Extracts entity/relationship/source sections from both contexts
   - Deduplicates using `process_combine_contexts()` [minirag/utils.py]()
   - Truncates combined sections to token limits

**When to use:** Complex queries requiring both specific entity information and broader relationship patterns, queries where mode selection is unclear

**Sources:** [minirag/operate.py:918-1073]()

### Mode Comparison Table

| Mode | Storage Used | Graph Traversal | Best For | SLM Performance |
|------|-------------|-----------------|----------|-----------------|
| **Naive** | chunks_vdb only | None | Simple factual queries | Baseline |
| **Local** | entities_vdb, chunks_vdb, graph | 1-hop neighbors | Entity-focused queries | Good |
| **Mini** | entity_name_vdb, relationships_vdb, chunks_vdb, graph | 2-hop reasoning paths | Multi-hop reasoning | Excellent (53.29%) |
| **Global** | relationships_vdb, chunks_vdb, graph | Relationship-centric | Pattern/summarization | Good |
| **Hybrid** | All databases | Both local & global | Complex queries | Very Good |

**Performance Data:** On LiHua-World dataset with Phi-3.5-mini-instruct, MiniRAG's mini mode achieves 53.29% accuracy versus 39.81% for local mode and 41.22% for naive mode [README.md:74-82]().

**Sources:** [README.md:74-89](), [minirag/operate.py:411-1479]()

---

## Code Entity Reference Map

The following diagram maps core concepts to their concrete implementations in the codebase:

```mermaid
graph TB
    subgraph "Core Concepts"
        HGI["Heterogeneous Graph<br/>Indexing"]
        TER["Topology-Enhanced<br/>Retrieval"]
        QM["Query Modes"]
    end
    
    subgraph "Primary Implementation Files"
        OP["minirag/operate.py<br/>(1480 lines)"]
        BASE["minirag/base.py<br/>Storage Interfaces"]
        UTILS["minirag/utils.py<br/>Helper Functions"]
    end
    
    subgraph "Key Functions in operate.py"
        EE["extract_entities()<br/>Line 233-408"]
        HSE["_handle_single_entity_extraction()<br/>Line 70-88"]
        HSR["_handle_single_relationship_extraction()<br/>Line 91-114"]
        MN["_merge_nodes_then_upsert()<br/>Line 117-163"]
        ME["_merge_edges_then_upsert()<br/>Line 166-230"]
        
        NQ["naive_query()<br/>Line 1076-1121"]
        LQ["local_query()<br/>Line 411-480"]
        MQ["minirag_query()<br/>Line 1409-1479"]
        GQ["global_query()<br/>Line 678-751"]
        HQ["hybrid_query()<br/>Line 918-1004"]
        
        P2C["path2chunk()<br/>Line 1124-1209"]
        BMC["_build_mini_query_context()<br/>Line 1252-1406"]
    end
    
    subgraph "Key Functions in utils.py"
        CPS["cal_path_score_list()"]
        EVP["edge_vote_path()"]
        CS["calculate_similarity()"]
    end
    
    subgraph "Storage Interfaces in base.py"
        BGS["BaseGraphStorage<br/>get_neighbors_within_k_hops()<br/>get_node_from_types()"]
        BVS["BaseVectorStorage<br/>query(), upsert()"]
        BKV["BaseKVStorage<br/>get_by_id(), get_by_ids()"]
    end
    
    HGI --> EE
    EE --> HSE
    EE --> HSR
    EE --> MN
    EE --> ME
    
    TER --> BMC
    BMC --> P2C
    BMC --> CPS
    BMC --> EVP
    
    QM --> NQ
    QM --> LQ
    QM --> MQ
    QM --> GQ
    QM --> HQ
    
    MQ --> BMC
    P2C --> CS
    
    EE --> BGS
    EE --> BVS
    BMC --> BGS
    BMC --> BVS
    BMC --> BKV
```

**Sources:** [minirag/operate.py:1-1480](), [minirag/base.py](), [minirag/utils.py]()

---

# Page: Heterogeneous Graph Indexing

# Heterogeneous Graph Indexing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [minirag/api/requirements.txt](minirag/api/requirements.txt)
- [minirag/operate.py](minirag/operate.py)

</details>



Heterogeneous graph indexing is one of MiniRAG's two core innovations (the other being topology-enhanced retrieval). The system extracts named entities and relationships from text chunks using LLM-based extraction, then stores them in a graph structure alongside the original text chunks. This creates a unified index where both entities (nodes) and text chunks (metadata) can be accessed through graph traversal.

The indexing process is implemented in the `extract_entities()` function [minirag/operate.py:233-408]() and integrates three storage components:
- `chunk_entity_relation_graph`: A `BaseGraphStorage` instance storing entity nodes and relationship edges
- Multiple vector databases: `entities_vdb`, `entity_name_vdb`, `relationships_vdb` for semantic search
- `text_chunks`: A `BaseKVStorage` instance mapping chunk IDs to content

For information about how this graph is used during query time, see [Topology-Enhanced Retrieval](#4.2).

## Graph Structure and Data Schema

The heterogeneous graph consists of entity nodes and relationship edges, with each component having specific attributes defined by the extraction prompts in [minirag/prompt.py]().

**Entity Node Schema:**
- `entity_name`: Uppercase normalized entity name (primary key)
- `entity_type`: One of `DEFAULT_ENTITY_TYPES` from prompts
- `description`: Concatenated descriptions from all source chunks (separated by `GRAPH_FIELD_SEP`)
- `source_id`: Concatenated chunk IDs where entity appears (separated by `GRAPH_FIELD_SEP`)

**Relationship Edge Schema:**
- `src_id`, `tgt_id`: Entity names (both normalized to uppercase)
- `weight`: Cumulative weight summed across all mentions (default 1.0 per mention)
- `description`: Concatenated relationship descriptions (separated by `GRAPH_FIELD_SEP`)
- `keywords`: Concatenated keywords (separated by `GRAPH_FIELD_SEP`)
- `source_id`: Concatenated chunk IDs where relationship appears

The `GRAPH_FIELD_SEP` constant (default `"<SEP>"`) is used to join multiple values within a single field, allowing the system to track all source chunks for each entity/relationship.

Sources: [minirag/operate.py:73-88](), [minirag/operate.py:91-114](), [minirag/prompt.py:1-50]()

### Data Flow: Text Chunks to Graph Storage

```mermaid
graph LR
    subgraph "Text Chunks"
        Chunk1["chunk_key_1<br/>TextChunkSchema"]
        Chunk2["chunk_key_2<br/>TextChunkSchema"]
    end
    
    subgraph "BaseGraphStorage: chunk_entity_relation_graph"
        Node1["JOHN_SMITH<br/>entity_type: PERSON<br/>description: CEO...<br/>source_id: chunk_key_1"]
        Node2["ACME_CORP<br/>entity_type: ORGANIZATION<br/>description: Tech...<br/>source_id: chunk_key_1<SEP>chunk_key_2"]
        
        Node1 -->|"weight: 2.0<br/>keywords: employment, CEO<br/>source_id: chunk_key_1"| Node2
    end
    
    Chunk1 -.-> Node1
    Chunk1 -.-> Node2
    Chunk2 -.-> Node2
```

This diagram shows how text chunks are transformed into entity nodes with relationships. The `source_id` fields track which chunks contain each entity/relationship, enabling retrieval of original text during query processing.

Sources: [minirag/operate.py:117-163](), [minirag/operate.py:166-230](), [minirag/base.py:20-30]()

## Entity and Relationship Extraction Process

The `extract_entities()` function [minirag/operate.py:233-408]() orchestrates LLM-based extraction with the following workflow:

1. **Prompt Construction**: Uses `PROMPTS["entity_extraction"]` [minirag/prompt.py]() with context including:
   - `tuple_delimiter`, `record_delimiter`, `completion_delimiter`
   - `entity_types`: Comma-separated list of allowed entity types
   - `input_text`: The chunk content

2. **Initial Extraction**: Calls `use_llm_func()` with the prompt to extract entities and relationships

3. **Iterative Gleaning**: For `entity_extract_max_gleaning` iterations:
   - Sends `PROMPTS["entiti_continue_extraction"]` to extract additional entities
   - Checks `PROMPTS["entiti_if_loop_extraction"]` to determine if more gleaning is needed
   - Accumulates all extraction results

4. **Parsing**: Splits response by `record_delimiter` and `completion_delimiter`, then parses each record:
   - Entity format: `("entity", "ENTITY_NAME", "ENTITY_TYPE", "DESCRIPTION")`
   - Relationship format: `("relationship", "SOURCE", "TARGET", "DESCRIPTION", "KEYWORDS", WEIGHT)`

5. **Deduplication and Merging**: Groups extracted data by entity name and edge tuple, then merges using:
   - `_merge_nodes_then_upsert()` [minirag/operate.py:117-163]()
   - `_merge_edges_then_upsert()` [minirag/operate.py:166-230]()

Sources: [minirag/operate.py:233-408](), [minirag/operate.py:265-329]()

### Extraction Pipeline: Functions and Data Flow

```mermaid
flowchart TD
    Input["chunks: dict[str, TextChunkSchema]"] --> ProcessSingle["_process_single_content()"]
    
    ProcessSingle --> LLMCall["use_llm_func(hint_prompt)"]
    LLMCall --> Gleaning["Iterative gleaning loop<br/>entity_extract_max_gleaning times"]
    Gleaning --> Parse["split_string_by_multi_markers()<br/>by record_delimiter"]
    
    Parse --> EntityHandler["_handle_single_entity_extraction()"]
    Parse --> RelHandler["_handle_single_relationship_extraction()"]
    
    EntityHandler --> MaybeNodes["maybe_nodes: defaultdict[str, list[dict]]"]
    RelHandler --> MaybeEdges["maybe_edges: defaultdict[tuple, list[dict]]"]
    
    MaybeNodes --> MergeNodes["_merge_nodes_then_upsert()"]
    MaybeEdges --> MergeEdges["_merge_edges_then_upsert()"]
    
    MergeNodes --> GraphUpsert["knowledge_graph_inst.upsert_node()"]
    MergeEdges --> GraphUpsert2["knowledge_graph_inst.upsert_edge()"]
    
    MergeNodes --> VDBUpsert["entity_vdb.upsert()<br/>entity_name_vdb.upsert()"]
    MergeEdges --> VDBUpsert2["relationships_vdb.upsert()"]
```

Each `_process_single_content()` call is executed concurrently using `asyncio.gather()` [minirag/operate.py:332-334](). The function tracks progress with `already_processed`, `already_entities`, and `already_relations` counters displayed using `PROMPTS["process_tickers"]`.

Sources: [minirag/operate.py:265-329](), [minirag/operate.py:332-408]()

## Node and Edge Merging Logic

The `_merge_nodes_then_upsert()` [minirag/operate.py:117-163]() and `_merge_edges_then_upsert()` [minirag/operate.py:166-230]() functions implement merging logic when the same entity or relationship is extracted from multiple chunks.

### Node Merging (`_merge_nodes_then_upsert`)

For each `entity_name`, the function:

1. **Retrieves existing node**: Calls `knowledge_graph_inst.get_node(entity_name)` to check for existing data
2. **Aggregates entity types**: Uses `Counter` to find most common type across all mentions
3. **Concatenates descriptions**: Joins unique descriptions with `GRAPH_FIELD_SEP`
4. **Concatenates source IDs**: Joins all chunk IDs with `GRAPH_FIELD_SEP`
5. **Upserts to graph**: Calls `knowledge_graph_inst.upsert_node(entity_name, node_data)`
6. **Updates vector DBs**: 
   - `entity_vdb`: Stores `entity_name + description` with hash ID prefix `"ent-"`
   - `entity_name_vdb`: Stores just `entity_name` with hash ID prefix `"Ename-"`

### Edge Merging (`_merge_edges_then_upsert`)

For each `(src_id, tgt_id)` tuple, the function:

1. **Retrieves existing edge**: Calls `knowledge_graph_inst.get_edge(src_id, tgt_id)`
2. **Sums weights**: Aggregates all weight values
3. **Concatenates descriptions**: Joins unique descriptions with `GRAPH_FIELD_SEP`
4. **Concatenates keywords**: Joins unique keywords with `GRAPH_FIELD_SEP`
5. **Concatenates source IDs**: Joins all chunk IDs
6. **Creates missing nodes**: If `src_id` or `tgt_id` don't exist, creates nodes with type `"UNKNOWN"`
7. **Upserts to graph**: Calls `knowledge_graph_inst.upsert_edge(src_id, tgt_id, edge_data)`
8. **Updates vector DB**: Stores in `relationships_vdb` with concatenated `keywords + src_id + tgt_id + description` and hash ID prefix `"rel-"`

Both functions use `compute_mdhash_id()` [minirag/utils.py]() to generate consistent hash-based IDs for vector database entries.

Sources: [minirag/operate.py:117-163](), [minirag/operate.py:166-230](), [minirag/operate.py:364-406]()

## Storage Architecture and Interfaces

```mermaid
graph TB
    subgraph "MiniRAG Instance"
        GraphStore["chunk_entity_relation_graph<br/>BaseGraphStorage"]
        EntVDB["entities_vdb<br/>BaseVectorStorage"]
        EntNameVDB["entity_name_vdb<br/>BaseVectorStorage"]
        RelVDB["relationships_vdb<br/>BaseVectorStorage"]
        ChunkKV["text_chunks<br/>BaseKVStorage[TextChunkSchema]"]
    end
    
    subgraph "BaseGraphStorage Methods"
        GetNode["get_node(entity_name)"]
        GetEdge["get_edge(src_id, tgt_id)"]
        UpsertNode["upsert_node(entity_name, node_data)"]
        UpsertEdge["upsert_edge(src_id, tgt_id, edge_data)"]
        NodeDegree["node_degree(entity_name)"]
        GetNeighbors["get_neighbors_within_k_hops(node_id, k)"]
    end
    
    GraphStore --> GetNode
    GraphStore --> GetEdge
    GraphStore --> UpsertNode
    GraphStore --> UpsertEdge
    GraphStore --> NodeDegree
    GraphStore --> GetNeighbors
```

The `BaseGraphStorage` abstract interface [minirag/base.py]() defines the core graph operations. During extraction, MiniRAG only uses `get_node()`, `get_edge()`, `upsert_node()`, and `upsert_edge()`. The topology methods (`node_degree()`, `get_neighbors_within_k_hops()`) are used during query processing.

Sources: [minirag/base.py:120-180](), [minirag/operate.py:117-230]()

## Graph Storage Backend Implementations

MiniRAG's storage layer uses a factory pattern defined in the `STORAGES` dictionary [minirag/minirag.py:39-62](). Each entry maps a string key to a tuple `(module_path, class_name)`:

| Key | Module Path | Class Name | Backend Technology |
|-----|-------------|------------|-------------------|
| `"NetworkXStorage"` | `minirag.kg.networkx_impl` | `NetworkXStorage` | NetworkX in-memory graph |
| `"Neo4JStorage"` | `minirag.kg.neo4j_impl` | `Neo4JStorage` | Neo4j native graph database |
| `"OracleGraphStorage"` | `minirag.kg.oracle_impl` | `OracleGraphStorage` | Oracle Graph |
| `"TiDBGraphStorage"` | `minirag.kg.tidb_impl` | `TiDBGraphStorage` | TiDB distributed SQL |
| `"PGGraphStorage"` | `minirag.kg.postgres_impl` | `PostgreSQLImpl` | PostgreSQL with custom schema |
| `"AGEStorage"` | `minirag.kg.age_impl` | `AGEStorage` | Apache AGE (Postgres extension) |
| `"GremlinStorage"` | `minirag.kg.gremlin_impl` | `GremlinStorage` | Apache TinkerPop Gremlin |
| `"CozoDB"` | `minirag.kg.cozo_impl` | `CozoStorage` | CozoDB graph database |
| `"FalkorDB"` | `minirag.kg.falkordb_impl` | `FalkorDBStorage` | FalkorDB graph database |
| `"MongoDBAtlas"` | `minirag.kg.mongodb_impl` | `MongoDBStorage` | MongoDB Atlas |

The MiniRAG constructor uses `dynamic_import()` [minirag/storage.py]() to load the specified implementation:

```python
# From minirag/minirag.py initialization
graph_storage_cls = lazy_external_import(*STORAGES[graph_storage])
self.chunk_entity_relation_graph = graph_storage_cls(
    namespace=self.namespace,
    global_config=asdict(self),
    embedding_func=self.embedding_func,
)
```

All implementations must conform to the `BaseGraphStorage` interface, providing methods like `upsert_node()`, `get_node()`, `upsert_edge()`, `get_edge()`, and graph traversal methods.

Sources: [minirag/minirag.py:39-62](), [minirag/minirag.py:259-265](), [minirag/storage.py:1-50]()

## Integration with MiniRAG Insert Pipeline

The graph indexing is triggered during document insertion via `insert()` [minirag/minirag.py:336-385]() or `ainsert()` [minirag/minirag.py:387-424]():

```mermaid
flowchart TD
    Insert["insert(content, metadata)"] --> CheckStatus["Check DocStatusStorage"]
    CheckStatus --> Enqueue["apipeline_process_enqueue_documents()"]
    
    Enqueue --> Chunk["chunking_by_token_size()<br/>max_token_size=1024<br/>overlap_token_size=128"]
    Chunk --> StoreChunks["text_chunks.upsert(chunks)"]
    StoreChunks --> VectorizeChunks["chunks_vdb.upsert(chunks)"]
    
    VectorizeChunks --> Extract["extract_entities(<br/>chunks,<br/>knowledge_graph_inst,<br/>entity_vdb,<br/>entity_name_vdb,<br/>relationships_vdb,<br/>global_config)"]
    
    Extract --> MergeLoop["For each entity:<br/>_merge_nodes_then_upsert()"]
    Extract --> MergeLoop2["For each relationship:<br/>_merge_edges_then_upsert()"]
    
    MergeLoop --> UpdateGraph["chunk_entity_relation_graph<br/>.upsert_node()"]
    MergeLoop2 --> UpdateGraph2["chunk_entity_relation_graph<br/>.upsert_edge()"]
    
    MergeLoop --> UpdateVDB["entity_vdb.upsert()<br/>entity_name_vdb.upsert()"]
    MergeLoop2 --> UpdateVDB2["relationships_vdb.upsert()"]
    
    UpdateVDB --> Done["_insert_done()"]
    UpdateVDB2 --> Done
```

The `extract_entities()` function [minirag/operate.py:233-408]() takes the following parameters:
- `chunks`: dict mapping chunk keys to `TextChunkSchema` objects
- `knowledge_graph_inst`: The `BaseGraphStorage` instance (`chunk_entity_relation_graph`)
- `entity_vdb`, `entity_name_vdb`, `relationships_vdb`: Vector storage instances
- `global_config`: Dictionary containing `llm_model_func`, `entity_extract_max_gleaning`, and other settings

The function returns the updated `knowledge_graph_inst` or `None` if extraction failed.

Sources: [minirag/minirag.py:336-385](), [minirag/minirag.py:370-383](), [minirag/operate.py:233-408]()

## Optimizations and Graph Traversal

MiniRAG's heterogeneous graph indexing implements several optimizations for efficient graph traversal and retrieval:

1. **Edge weighting**: Relationships between entities have weights that represent their importance
2. **Node and edge ranking**: Based on degree (number of connections)
3. **K-hop neighborhood retrieval**: Finding entities within K steps of a given entity
4. **Path scoring**: Scoring potential reasoning paths through the graph

The system uses these optimization techniques during query time to identify the most relevant entities, relationships, and chunks for a given query.

## Advantages of Heterogeneous Graph Indexing

Compared to traditional vector-only indexing, heterogeneous graph indexing offers several advantages:

1. **Captures semantic relationships**: Beyond simple similarity, it represents how entities relate to each other
2. **Enables multi-hop reasoning**: Can connect information across multiple chunks through graph traversal
3. **Supports complex queries**: Better handles queries requiring understanding of relationships
4. **Optimal for SLMs**: Provides structured, relationship-aware context that helps small language models reason effectively

For more details on how the graph is used during query processing, see [Topology-Enhanced Retrieval](#4.2) and [Query Modes](#4.3).

Sources: [minirag/operate.py:918-1004](), [minirag/operate.py:1409-1479]()

---

# Page: Topology-Enhanced Retrieval

# Topology-Enhanced Retrieval

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [minirag/api/requirements.txt](minirag/api/requirements.txt)
- [minirag/kg/networkx_impl.py](minirag/kg/networkx_impl.py)
- [minirag/operate.py](minirag/operate.py)

</details>



## Purpose and Scope

This document describes MiniRAG's topology-enhanced retrieval mechanism, which leverages the structure of the knowledge graph to discover reasoning paths and relevant context for answering queries. This is one of MiniRAG's two core technical innovations (the other being heterogeneous graph indexing, covered in [section 4.1](#4.1)).

Topology-enhanced retrieval enables Small Language Models (SLMs) to perform effective RAG by using graph traversal algorithms to find relevant information, rather than relying on advanced semantic understanding. This page focuses on the algorithms, data structures, and implementation details of the topology-based retrieval process.

For information about the different query modes that utilize this retrieval mechanism, see [Query Modes](#4.3). For details on the underlying graph storage implementations, see [Graph Storage Backends](#5.1).

---

## Overview

Topology-enhanced retrieval exploits the structural properties of the knowledge graph to find reasoning paths between query entities and potential answer entities. Unlike traditional vector search that relies purely on semantic similarity, this approach uses graph connectivity, k-hop neighborhood exploration, and path scoring to identify relevant context.

### Key Characteristics

| Characteristic | Description |
|---------------|-------------|
| **Graph Traversal** | Uses k-hop neighborhood exploration to discover connected entities |
| **Path-Based Reasoning** | Constructs and scores reasoning paths from query entities to answer entities |
| **Entity Type Awareness** | Leverages entity types to identify potential answer nodes |
| **Edge Voting** | Uses edge relevance to reinforce important reasoning paths |
| **Lightweight** | Does not require advanced semantic reasoning from the LLM |

**Sources:** [minirag/operate.py:1252-1406](), Diagram 5 from high-level architecture

---

## K-Hop Neighborhood Exploration

The foundation of topology-enhanced retrieval is the ability to traverse the graph and discover entities within k hops of a starting node.

### Algorithm Overview

```mermaid
graph TB
    subgraph "K-Hop Traversal Process"
        Start["Start Node<br/>(Query Entity)"]
        Hop1["1-Hop Neighbors<br/>get_node_edges()"]
        Hop2["2-Hop Neighbors<br/>Recursive Expansion"]
        HopK["K-Hop Neighbors<br/>merge_tuples()"]
        
        Start --> Hop1
        Hop1 --> Hop2
        Hop2 --> HopK
    end
    
    subgraph "NetworkXStorage Implementation"
        HasNode["has_node()<br/>Check existence"]
        GetEdges["_graph.edges()<br/>Get adjacency"]
        MergeTuples["merge_tuples()<br/>Combine paths"]
        
        HasNode --> GetEdges
        GetEdges --> MergeTuples
    end
    
    HopK --> HasNode
```

### Implementation: `get_neighbors_within_k_hops`

The core k-hop traversal is implemented in `NetworkXStorage`:

[minirag/kg/networkx_impl.py:177-193]()

```python
async def get_neighbors_within_k_hops(self, source_node_id: str, k):
    count = 0
    if await self.has_node(source_node_id):
        source_edge = list(self._graph.edges(source_node_id))
    else:
        print("NO THIS ID:", source_node_id)
        return []
    count = count + 1
    while count < k:
        count = count + 1
        sc_edge = copy.deepcopy(source_edge)
        source_edge = []
        for pair in sc_edge:
            append_edge = list(self._graph.edges(pair[-1]))
            for tuples in merge_tuples([pair], append_edge):
                source_edge.append(tuples)
    return source_edge
```

**Key Components:**

| Component | Purpose |
|-----------|---------|
| `source_node_id` | Starting entity for traversal |
| `k` | Number of hops to explore |
| `source_edge` | List of edge tuples representing paths |
| `merge_tuples()` | Combines path segments into longer paths |

**Sources:** [minirag/kg/networkx_impl.py:177-193](), [minirag/utils.py]() (merge_tuples)

---

## Reasoning Path Discovery

### MiniRAG Query Context Building

The topology-enhanced retrieval is primarily used in the `minirag` query mode through the `_build_mini_query_context` function:

```mermaid
sequenceDiagram
    participant Query as "User Query"
    participant Extract as "Entity Extraction<br/>minirag_query()"
    participant VDB as "entity_name_vdb<br/>Vector Search"
    participant Graph as "knowledge_graph_inst<br/>BaseGraphStorage"
    participant Score as "Path Scoring<br/>cal_path_score_list()"
    participant Vote as "Edge Voting<br/>edge_vote_path()"
    participant Convert as "Path to Chunks<br/>path2chunk()"
    
    Query->>Extract: Extract entities & types
    Extract->>VDB: Query top-k similar entities
    VDB-->>Extract: Candidate entities
    Extract->>Graph: get_neighbors_within_k_hops(entity, 2)
    Graph-->>Extract: Reasoning paths (edge tuples)
    Extract->>Graph: get_node_from_types(answer_types)
    Graph-->>Extract: Potential answer entities
    Extract->>Score: Score paths to answer entities
    Score-->>Extract: Scored reasoning paths
    Extract->>Vote: Vote on edges using relationship_vdb
    Vote-->>Extract: Enhanced paths with edge scores
    Extract->>Convert: Convert paths to chunk IDs
    Convert-->>Extract: Ranked text chunks
```

**Sources:** [minirag/operate.py:1252-1406](), [minirag/operate.py:1409-1479]()

### Step-by-Step Process

#### 1. Entity Extraction from Query

[minirag/operate.py:1422-1449]()

The query is first processed to extract:
- **Entities from query**: Entities mentioned or implied in the query
- **Answer type keywords**: Expected entity types for the answer

```python
kw_prompt_temp = PROMPTS["minirag_query2kwd"]
TYPE_POOL, TYPE_POOL_w_CASE = await knowledge_graph_inst.get_types()
kw_prompt = kw_prompt_temp.format(query=query, TYPE_POOL=TYPE_POOL)
result = await use_model_func(kw_prompt)
keywords_data = json_repair.loads(result)
type_keywords = keywords_data.get("answer_type_keywords", [])
entities_from_query = keywords_data.get("entities_from_query", [])[:5]
```

#### 2. Candidate Entity Discovery

[minirag/operate.py:1269-1292]()

For each extracted entity, find similar entities in the graph:

```python
for ent in ent_from_query:
    results_node = await entity_name_vdb.query(ent, top_k=query_param.top_k)
    nodes_from_query_list.append(results_node)
    ent_from_query_dict[ent] = [e["entity_name"] for e in results_node]
```

Then construct reasoning paths from these candidates:

```python
for key in candidate_reasoning_path.keys():
    candidate_reasoning_path[key]["Path"] = \
        await knowledge_graph_inst.get_neighbors_within_k_hops(key, 2)
```

#### 3. Answer Type Filtering

[minirag/operate.py:1311-1319]()

Retrieve entities that match the expected answer types:

```python
node_datas_from_type = await knowledge_graph_inst.get_node_from_types(
    type_keywords
)
maybe_answer_list = [n["entity_name"] for n in node_datas_from_type]
scored_reasoning_path = cal_path_score_list(
    candidate_reasoning_path, maybe_answer_list
)
```

**Sources:** [minirag/operate.py:1269-1319]()

---

## Path Scoring and Edge Voting

### Path Scoring Algorithm

The `cal_path_score_list` function (referenced from utils) scores reasoning paths based on:
1. **Connectivity**: How many hops to reach answer entities
2. **Type matching**: Whether path endpoints match expected answer types
3. **Distance scores**: Semantic similarity from vector search

### Edge Voting Mechanism

```mermaid
graph LR
    subgraph "Edge Voting Process"
        Paths["Scored Reasoning Paths"]
        EdgeVDB["relationships_vdb<br/>Query relevant edges"]
        GoodEdge["Good Edges<br/>(Connected to important entities)"]
        BadEdge["Bad Edges<br/>(Not connected)"]
        Vote["edge_vote_path()<br/>Vote on path edges"]
        Enhanced["Enhanced Paths<br/>with edge scores"]
        
        Paths --> EdgeVDB
        EdgeVDB --> GoodEdge
        EdgeVDB --> BadEdge
        GoodEdge --> Vote
        Paths --> Vote
        Vote --> Enhanced
    end
```

[minirag/operate.py:1321-1333]()

```python
results_edge = await relationships_vdb.query(
    originalquery, top_k=len(ent_from_query) * query_param.top_k
)
goodedge = []
badedge = []
for item in results_edge:
    if item["src_id"] in imp_ents or item["tgt_id"] in imp_ents:
        goodedge.append(item)
    else:
        badedge.append(item)
scored_edged_reasoning_path, pairs_append = edge_vote_path(
    scored_reasoning_path, goodedge
)
```

**Sources:** [minirag/operate.py:1321-1333](), [minirag/utils.py]() (edge_vote_path, cal_path_score_list)

---

## Path to Chunk Conversion

Once reasoning paths are scored and enhanced, they need to be converted to actual text chunks for context generation.

### Conversion Process Diagram

```mermaid
graph TB
    subgraph "path2chunk Conversion"
        ScoredPaths["Scored Edge Reasoning Paths"]
        ExtractSource["Extract source_id from edges<br/>get_edge()"]
        ExtractNode["Extract source_id from nodes<br/>get_node()"]
        SimilarityFilter["Similarity Filter<br/>calculate_similarity()"]
        Counter["Count Chunk Occurrences<br/>Counter()"]
        Weight["Weight by path scores"]
        TopChunks["Select Top Chunks<br/>most_common()"]
        
        ScoredPaths --> ExtractSource
        ScoredPaths --> ExtractNode
        ExtractSource --> Counter
        ExtractNode --> SimilarityFilter
        SimilarityFilter --> Counter
        Counter --> Weight
        Weight --> TopChunks
    end
```

### Implementation Details

[minirag/operate.py:1124-1209]()

The `path2chunk` function performs the following:

1. **Extract chunk IDs from edges**:
```python
edge_datas = await asyncio.gather(
    *[knowledge_graph_inst.get_edge(r[0], r[1]) for r in use_edge]
)
text_units = [
    split_string_by_multi_markers(dp["source_id"], [GRAPH_FIELD_SEP])
    for dp in edge_datas
][0]
```

2. **Extract chunk IDs from nodes**:
```python
node_datas = await asyncio.gather(
    *[knowledge_graph_inst.get_node(pathtuple[0])]
)
for dp in node_datas:
    text_units_node = split_string_by_multi_markers(
        dp["source_id"], [GRAPH_FIELD_SEP]
    )
    text_units = text_units + text_units_node
```

3. **Filter nodes by description similarity**:
```python
if len(text_units_node) > 5:
    max_ids = int(max(5, len(text_units_node) / 2))
    should_consider_idx = calculate_similarity(
        descriptionlist_node, query, k=max_ids
    )
    text_units_node = [text_units_node[i] for i in should_consider_idx]
```

4. **Weight chunks by path scores**:
```python
count_dict = Counter(text_units)
total_score = scorelist[0] + scorelist[1] + 1
for key, value in count_dict.items():
    count_dict[key] = value * total_score
```

5. **Select top chunks**:
```python
for id in count_dict.most_common(max_chunks):
    v["Path"].append(id[0])
```

**Sources:** [minirag/operate.py:1124-1209]()

---

## Final Context Assembly

### Keyword to Chunk Mapping

The `kwd2chunk` function aggregates chunk scores across all query entities:

[minirag/operate.py:1220-1249]()

```python
def kwd2chunk(ent_from_query_dict, chunks_ids, chunk_nums):
    final_chunk = Counter()
    for key, list_of_dicts in ent_from_query_dict.items():
        total_id_scores = Counter()
        for d in list_of_dicts:
            score = d["Score"] * 2 if d == list_of_dicts[0] else d["Score"]
            path = d["Path"]
            for id in path:
                if id == path[0] and id in chunks_ids:
                    score = score * 10  # Boost first chunk if in vector search results
                if id in id_scores:
                    id_scores[id] += score
                else:
                    id_scores[id] = score
        final_chunk = final_chunk + total_id_scores
    return [i[0] for i in final_chunk.most_common(chunk_nums)]
```

### Context Structure

[minirag/operate.py:1397-1406]()

The final context returned includes:

| Section | Content | Source |
|---------|---------|--------|
| **Entities** | Scored entities from reasoning paths | `scored_edged_reasoning_path` |
| **Sources** | Relevant text chunks | `final_chunk_id` via `kwd2chunk()` |

```python
return f"""
-----Entities-----
```csv
{entities_context}
```
-----Sources-----
```csv
{text_units_context}
```
"""
```

**Sources:** [minirag/operate.py:1220-1249](), [minirag/operate.py:1397-1406]()

---

## Integration with Query Pipeline

### Complete MiniRAG Query Flow

```mermaid
graph TB
    subgraph "minirag_query Entry Point"
        QueryInput["User Query"]
        ExtractKW["Extract Keywords<br/>PROMPTS['minirag_query2kwd']"]
        BuildContext["_build_mini_query_context()"]
        GenResponse["LLM Response Generation<br/>PROMPTS['rag_response']"]
        QueryOutput["Final Answer"]
    end
    
    subgraph "_build_mini_query_context Details"
        E1["entity_name_vdb.query()"]
        E2["get_neighbors_within_k_hops()"]
        E3["get_node_from_types()"]
        E4["cal_path_score_list()"]
        E5["edge_vote_path()"]
        E6["path2chunk()"]
        E7["kwd2chunk()"]
    end
    
    subgraph "Storage Layers"
        GraphDB["knowledge_graph_inst<br/>BaseGraphStorage"]
        VectorDB["entity_name_vdb<br/>relationships_vdb<br/>chunks_vdb"]
        KVDB["text_chunks_db<br/>BaseKVStorage"]
    end
    
    QueryInput --> ExtractKW
    ExtractKW --> BuildContext
    BuildContext --> E1
    E1 --> E2
    E2 --> E3
    E3 --> E4
    E4 --> E5
    E5 --> E6
    E6 --> E7
    E7 --> GenResponse
    GenResponse --> QueryOutput
    
    E1 --> VectorDB
    E2 --> GraphDB
    E3 --> GraphDB
    E5 --> VectorDB
    E7 --> VectorDB
    E6 --> KVDB
```

**Sources:** [minirag/operate.py:1409-1479](), [minirag/operate.py:1252-1406]()

---

## Configuration Parameters

The topology-enhanced retrieval process is controlled by several `QueryParam` settings:

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `top_k` | 60 | Number of candidate entities/edges to retrieve |
| `max_token_for_node_context` | 6000 | Maximum tokens for entity context |
| `max_token_for_text_unit` | 4000 | Maximum tokens for text chunks |

These are configured when creating a query:

```python
query_param = QueryParam(
    mode="mini",
    top_k=60,
    max_token_for_node_context=6000,
    max_token_for_text_unit=4000
)
```

**Sources:** [minirag/base.py]() (QueryParam), [minirag/operate.py:1252-1406]()

---

## Comparison with Other Query Modes

### Topology-Enhanced vs Vector-Only Retrieval

| Aspect | Topology-Enhanced (MiniRAG) | Naive (Vector-Only) |
|--------|---------------------------|---------------------|
| **Primary mechanism** | K-hop graph traversal | Vector similarity search |
| **Context discovery** | Follows graph connections | Independent chunk retrieval |
| **Multi-hop reasoning** | Native support via paths | Limited |
| **Entity relationships** | Explicitly modeled | Implicit in embeddings |
| **Computational cost** | Graph traversal + vector search | Vector search only |

### Topology-Enhanced vs LightRAG

| Aspect | MiniRAG | LightRAG |
|--------|---------|----------|
| **Entity types** | Used for answer filtering | Not emphasized |
| **Path scoring** | Type-aware + edge voting | Degree-based |
| **Chunk selection** | Path-weighted + similarity filter | Source-based aggregation |
| **SLM optimization** | Designed for 1.5B-4B models | Requires stronger models |

**Sources:** High-level architecture Diagram 5, [minirag/operate.py:1409-1479]() vs [minirag/operate.py:411-481]()

---

## Performance Characteristics

### Advantages

1. **Efficient for Small Models**: Reduces semantic understanding burden on the LLM
2. **Multi-hop Reasoning**: Naturally handles questions requiring multiple inference steps
3. **Type-Guided Search**: Uses entity types to focus on relevant answer candidates
4. **Path Interpretability**: Reasoning paths provide explainability

### Trade-offs

1. **Graph Quality Dependency**: Requires well-constructed knowledge graph
2. **Computational Overhead**: K-hop traversal can be expensive for large graphs
3. **Configuration Sensitivity**: Requires tuning of k-hop depth and scoring weights

### Storage Access Patterns

```mermaid
graph LR
    subgraph "Storage Access Frequency"
        VDBHigh["entity_name_vdb<br/>relationships_vdb<br/>(High frequency)"]
        GraphMed["knowledge_graph_inst<br/>get_neighbors_within_k_hops<br/>get_node, get_edge<br/>(Medium-high frequency)"]
        KVLow["text_chunks_db<br/>get_by_id<br/>(Lower frequency, final step)"]
    end
```

**Sources:** [minirag/operate.py:1252-1406](), Performance analysis from high-level architecture

---

## Key Utility Functions

The topology-enhanced retrieval relies on several utility functions:

| Function | Location | Purpose |
|----------|----------|---------|
| `merge_tuples()` | [minirag/utils.py:68]() | Combines path segments in k-hop traversal |
| `cal_path_score_list()` | [minirag/utils.py:24]() | Scores reasoning paths |
| `edge_vote_path()` | [minirag/utils.py:17]() | Votes on edges to enhance paths |
| `calculate_similarity()` | [minirag/utils.py:23]() | Filters nodes by description similarity |
| `split_string_by_multi_markers()` | [minirag/utils.py:12]() | Extracts source IDs from concatenated strings |
| `truncate_list_by_token_size()` | [minirag/utils.py:11]() | Limits context by token count |

**Sources:** [minirag/utils.py](), [minirag/operate.py:9-25]()

---

## Summary

Topology-enhanced retrieval is the mechanism that enables MiniRAG to achieve strong performance with Small Language Models. By leveraging graph structure through k-hop traversal, path scoring, and edge voting, the system can discover relevant context without requiring advanced semantic reasoning from the LLM.

The key insight is that graph topology encodes structural relationships that can guide retrieval, reducing the burden on the language model to understand complex semantic relationships. This makes MiniRAG particularly effective for on-device deployment scenarios where model size and computational resources are constrained.

**Sources:** [minirag/operate.py:1252-1479](), [minirag/kg/networkx_impl.py:177-193](), High-level architecture diagrams

---

# Page: Query Modes

# Query Modes

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [minirag/__init__.py](minirag/__init__.py)
- [minirag/api/requirements.txt](minirag/api/requirements.txt)
- [minirag/base.py](minirag/base.py)
- [minirag/operate.py](minirag/operate.py)

</details>



This document details the query modes available in MiniRAG, how they work, and when to use each mode. Query modes determine the retrieval strategy that MiniRAG uses to find relevant information for answering user queries. For information about how these modes are implemented in the topology-enhanced retrieval framework, see [Topology-Enhanced Retrieval](#4.2).

## Overview of Query Modes

MiniRAG offers three query modes, each with different characteristics, advantages, and use cases:

| Mode | Description | Best For | Implementation |
|------|-------------|----------|----------------|
| `naive` | Direct vector retrieval | Simple queries, baseline performance | `naive_query()` function |
| `light` | Hybrid approach combining entity and relationship retrieval | Balance of performance and accuracy | `hybrid_query()` function |
| `mini` | Full topology-enhanced retrieval with reasoning paths | Complex queries requiring reasoning | `minirag_query()` function |

The query mode is specified in the `QueryParam` class:

```python
@dataclass
class QueryParam:
    mode: Literal["light", "naive", "mini"] = "mini"
    # Other parameters...
```

Sources: [minirag/base.py:18-45]()

## Query Mode Architecture

The following diagram illustrates how the three query modes interact with the various components of MiniRAG:

```mermaid
flowchart TD
    UserQuery["User Query"] --> QueryParam{"Query Mode Parameter"}
    
    QueryParam -->|mode="naive"| NaiveQuery["naive_query()"]
    QueryParam -->|mode="light"| HybridQuery["hybrid_query()"]
    QueryParam -->|mode="mini"| MiniRAGQuery["minirag_query()"]
    
    subgraph "Vector Storage Layer"
        ChunksVDB[(Chunks Vector DB)]
        EntitiesVDB[(Entities Vector DB)]
        EntityNameVDB[(Entity Name Vector DB)]
        RelationshipsVDB[(Relationships Vector DB)]
    end
    
    subgraph "Graph Storage Layer"
        KnowledgeGraph[(Knowledge Graph)]
    end
    
    subgraph "KV Storage Layer"
        TextChunksDB[(Text Chunks DB)]
    end
    
    NaiveQuery --> ChunksVDB
    NaiveQuery --> TextChunksDB
    
    HybridQuery --> EntitiesVDB
    HybridQuery --> RelationshipsVDB
    HybridQuery --> KnowledgeGraph
    HybridQuery --> TextChunksDB
    
    MiniRAGQuery --> EntityNameVDB
    MiniRAGQuery --> EntitiesVDB
    MiniRAGQuery --> RelationshipsVDB
    MiniRAGQuery --> ChunksVDB
    MiniRAGQuery --> KnowledgeGraph
    MiniRAGQuery --> TextChunksDB
    
    subgraph "Context Generation"
        NaiveQuery --> NaiveContext["Direct Text Context"]
        HybridQuery --> HybridContext["Combined Entity-Relation Context"]
        MiniRAGQuery --> MiniContext["Topology-Enhanced Context"]
    end
    
    NaiveContext --> LLM["LLM Response Generation"]
    HybridContext --> LLM
    MiniContext --> LLM
```

Sources: [minirag/operate.py:411-1479](), [minirag/base.py:18-45]()

## Naive Mode

Naive mode is the most straightforward approach, using direct vector similarity search without leveraging the graph structure. It provides a baseline for comparison with the more advanced modes.

### How Naive Mode Works

```mermaid
sequenceDiagram
    participant "User" as U
    participant "naive_query()" as NQ
    participant "ChunksVDB" as CVDB
    participant "TextChunksDB" as TCDB
    participant "LLM" as LLM

    U->>NQ: Query with mode="naive"
    NQ->>CVDB: Vector similarity search
    CVDB-->>NQ: Return top_k chunk IDs
    NQ->>TCDB: Get chunks by IDs
    TCDB-->>NQ: Return chunk contents
    NQ->>NQ: Truncate chunks to fit max token limit
    NQ->>LLM: Generate response with chunks as context
    LLM-->>U: Final response
```

In naive mode, MiniRAG:
1. Performs vector similarity search on the chunks vector database
2. Retrieves the top k chunks based on similarity
3. Truncates the chunks to fit the token limit if necessary
4. Passes the chunks as context to the LLM for response generation

### Implementation Details

The naive query logic is implemented in the `naive_query()` function:

```python
async def naive_query(
    query,
    chunks_vdb: BaseVectorStorage,
    text_chunks_db: BaseKVStorage[TextChunkSchema],
    query_param: QueryParam,
    global_config: dict,
):
    # Retrieve chunks from vector database by similarity
    results = await chunks_vdb.query(query, top_k=query_param.top_k)
    
    # Get the full content of those chunks
    chunks_ids = [r["id"] for r in results]
    chunks = await text_chunks_db.get_by_ids(chunks_ids)
    
    # Truncate chunks to fit token limit
    maybe_trun_chunks = truncate_list_by_token_size(
        chunks,
        key=lambda x: x["content"],
        max_token_size=query_param.max_token_for_text_unit,
    )
    
    # Format chunks for LLM context
    section = "--New Chunk--\n".join([c["content"] for c in maybe_trun_chunks])
    
    # Return context if only context is requested
    if query_param.only_need_context:
        return section
        
    # Generate LLM response
    sys_prompt = PROMPTS["naive_rag_response"].format(
        content_data=section, response_type=query_param.response_type
    )
    response = await use_model_func(query, system_prompt=sys_prompt)
    
    # Clean and return response
    # ...
    return response
```

Sources: [minirag/operate.py:1076-1121]()

### When to Use Naive Mode

Naive mode is recommended when:
- You need a baseline for performance comparison
- Your queries are simple and don't require complex reasoning
- Your dataset doesn't have many interconnected entities and relationships
- You want faster query processing with less computational overhead

## Light Mode (Hybrid)

Light mode combines entity-based and relationship-based retrieval strategies. It extracts both high-level and low-level keywords from the query, then retrieves relevant entities and relationships based on these keywords.

### How Light Mode Works

```mermaid
flowchart TD
    Query["User Query"]
    KeywordExtraction["Extract High/Low Level Keywords"]
    LocalQuery["Local Query (Entities)"]
    GlobalQuery["Global Query (Relationships)"]
    CombineContexts["Combine Contexts"]
    
    Query --> KeywordExtraction
    KeywordExtraction -->|"Low-level keywords"| LocalQuery
    KeywordExtraction -->|"High-level keywords"| GlobalQuery
    
    subgraph "Entity-Based Retrieval"
        LocalQuery --> EntitiesVDB[(Entities Vector DB)]
        EntitiesVDB --> RetrieveEntities["Retrieve relevant entities"]
        RetrieveEntities --> EntityContext["Build entity context"]
    end
    
    subgraph "Relationship-Based Retrieval"
        GlobalQuery --> RelationshipsVDB[(Relationships Vector DB)]
        RelationshipsVDB --> RetrieveRelationships["Retrieve relevant relationships"]
        RetrieveRelationships --> RelationshipContext["Build relationship context"]
    end
    
    EntityContext --> CombineContexts
    RelationshipContext --> CombineContexts
    CombineContexts --> LLMResponse["Generate LLM Response"]
```

In light mode, MiniRAG:
1. Extracts high-level and low-level keywords from the query
2. Uses low-level keywords to retrieve relevant entities (local query)
3. Uses high-level keywords to retrieve relevant relationships (global query)
4. Combines the entity and relationship contexts
5. Passes the combined context to the LLM for response generation

### Implementation Details

The light mode query logic is implemented in the `hybrid_query()` function:

```python
async def hybrid_query(
    query,
    knowledge_graph_inst: BaseGraphStorage,
    entities_vdb: BaseVectorStorage,
    relationships_vdb: BaseVectorStorage,
    text_chunks_db: BaseKVStorage[TextChunkSchema],
    query_param: QueryParam,
    global_config: dict,
) -> str:
    # Extract keywords from query
    kw_prompt = PROMPTS["keywords_extraction"].format(query=query)
    result = await use_model_func(kw_prompt)
    
    # Parse keywords
    keywords_data = json.loads(json_text)
    hl_keywords = keywords_data.get("high_level_keywords", [])
    ll_keywords = keywords_data.get("low_level_keywords", [])
    
    # Build local context from entities
    low_level_context = await _build_local_query_context(
        ll_keywords, knowledge_graph_inst, entities_vdb, text_chunks_db, query_param,
    )
    
    # Build global context from relationships
    high_level_context = await _build_global_query_context(
        hl_keywords, knowledge_graph_inst, entities_vdb, relationships_vdb, 
        text_chunks_db, query_param,
    )
    
    # Combine contexts
    context = combine_contexts(high_level_context, low_level_context)
    
    # Generate LLM response
    sys_prompt = PROMPTS["rag_response"].format(
        context_data=context, response_type=query_param.response_type
    )
    response = await use_model_func(query, system_prompt=sys_prompt)
    
    # Clean and return response
    # ...
    return response
```

Sources: [minirag/operate.py:918-1004]()

### When to Use Light Mode

Light mode is recommended when:
- You need a balance between performance and accuracy
- Your queries involve both specific entities and their relationships
- You want to leverage the graph structure without the full computational cost of mini mode
- You're dealing with a medium-sized knowledge base

## Mini Mode

Mini mode is the most sophisticated retrieval strategy, implementing the full MiniRAG approach with topology-enhanced retrieval. It extracts entities from the query, builds reasoning paths through the knowledge graph, and uses these paths to retrieve highly relevant context.

### How Mini Mode Works

```mermaid
flowchart TD
    Query["User Query"] --> ExtractEntities["Extract Entities & Type Keywords"]
    
    subgraph "Entity Retrieval"
        ExtractEntities --> EntityNameVDB[(Entity Name Vector DB)]
        EntityNameVDB --> EntityCandidates["Entity Candidates"]
    end
    
    subgraph "Graph-Based Reasoning"
        EntityCandidates --> BuildReasoningPaths["Build Reasoning Paths (2-hop)"]
        TypeKeywords["Type Keywords"] --> NodesByType["Get Nodes by Type"]
        NodesByType --> PotentialAnswers["Potential Answer Entities"]
        BuildReasoningPaths --> ScoredPaths["Score Reasoning Paths"]
        PotentialAnswers --> ScoredPaths
    end
    
    subgraph "Edge-Based Enhancement"
        Query --> RelationshipSearch["Search Relationships"]
        RelationshipSearch --> RelationshipsVDB[(Relationships Vector DB)]
        RelationshipsVDB --> RelevantEdges["Relevant Edges"]
        RelevantEdges --> VotePaths["Vote/Enhance Paths"]
        ScoredPaths --> VotePaths
    end
    
    subgraph "Chunk Retrieval"
        VotePaths --> ChunkMapping["Map Paths to Chunks"]
        Query --> DirectChunkSearch["Direct Chunk Search"]
        DirectChunkSearch --> ChunksVDB[(Chunks Vector DB)]
        ChunksVDB --> RelevantChunks["Relevant Chunks"]
        ChunkMapping --> FinalChunks["Final Chunk Selection"]
        RelevantChunks --> FinalChunks
    end
    
    FinalChunks --> ContextGeneration["Generate Context"]
    ContextGeneration --> LLMResponse["Generate LLM Response"]
```

In mini mode, MiniRAG:
1. Extracts entities and type keywords from the query
2. Retrieves candidate entities from the entity name vector database
3. Builds reasoning paths through the knowledge graph (up to 2 hops)
4. Scores the reasoning paths based on relevance to potential answer entities
5. Enhances paths with relevant relationships from the vector database
6. Maps paths to document chunks and combines with direct chunk retrieval
7. Generates a rich context with entities and chunks
8. Passes the context to the LLM for response generation

### Implementation Details

The mini mode query logic is implemented in the `minirag_query()` function:

```python
async def minirag_query(
    query,
    knowledge_graph_inst: BaseGraphStorage,
    entities_vdb: BaseVectorStorage,
    entity_name_vdb: BaseVectorStorage,
    relationships_vdb: BaseVectorStorage,
    chunks_vdb: BaseVectorStorage,
    text_chunks_db: BaseKVStorage[TextChunkSchema],
    embedder,
    query_param: QueryParam,
    global_config: dict,
) -> str:
    # Extract entities and type keywords from query
    kw_prompt = PROMPTS["minirag_query2kwd"].format(query=query, TYPE_POOL=TYPE_POOL)
    result = await use_model_func(kw_prompt)
    
    # Parse entities and types
    keywords_data = json_repair.loads(result)
    type_keywords = keywords_data.get("answer_type_keywords", [])
    entities_from_query = keywords_data.get("entities_from_query", [])[:5]
    
    # Build context with topology-enhanced retrieval
    context = await _build_mini_query_context(
        entities_from_query, type_keywords, query, knowledge_graph_inst,
        entities_vdb, entity_name_vdb, relationships_vdb, chunks_vdb,
        text_chunks_db, embedder, query_param,
    )
    
    # Generate LLM response
    sys_prompt = PROMPTS["rag_response"].format(
        context_data=context, response_type=query_param.response_type
    )
    response = await use_model_func(query, system_prompt=sys_prompt)
    
    return response
```

The complex `_build_mini_query_context` function implements the topology-enhanced retrieval, finding reasoning paths through the graph and mapping them to relevant chunks.

Sources: [minirag/operate.py:1409-1479](), [minirag/operate.py:1252-1406]()

### When to Use Mini Mode

Mini mode is recommended when:
- You need the most accurate and comprehensive answers
- Your queries require complex reasoning over heterogeneous knowledge
- You have a rich knowledge graph with many entities and relationships
- You're dealing with multi-hop questions that require connecting multiple facts
- You're using small language models (SLMs) that benefit from enhanced retrieval

## Comparison of Query Modes

The following table summarizes the key differences between the three query modes:

| Feature | Naive Mode | Light Mode | Mini Mode |
|---------|------------|------------|-----------|
| Graph Structure Usage | None | Partial | Full |
| Retrieval Approach | Direct vector search | Entity + relationship retrieval | Topology-enhanced paths |
| Multi-hop Reasoning | No | Limited | Yes (up to 2 hops) |
| Computational Cost | Low | Medium | High |
| Response Quality | Baseline | Good | Best |
| Best For | Simple questions | General queries | Complex reasoning |
| Default | No | No | Yes |

## Setting the Query Mode

To specify the query mode when using MiniRAG:

### Python API

```python
from minirag import MiniRAG, QueryParam

# Create MiniRAG instance
rag = MiniRAG()

# Query with specific mode
response = await rag.query(
    "Who is the founder of Apple?",
    QueryParam(mode="light")  # "light", "naive", or "mini"
)
```

### REST API

```
POST /query
{
    "query": "Who is the founder of Apple?",
    "mode": "mini"  # "light", "naive", or "mini"
}
```

Sources: [minirag/__init__.py:1-6](), [minirag/base.py:18-45]()

## Best Practices

- **Start with Mini Mode**: It's the default and provides the best results in most cases
- **Use Light Mode** for faster responses when dealing with simpler queries
- **Use Naive Mode** for baseline comparison or when your knowledge base is primarily text-based with few entity relationships
- **Adjust `top_k` Parameter**: Increase for more comprehensive results, decrease for faster responses
- **Consider Storage Backends**: Different modes may perform better with different storage backends (e.g., Neo4j for graph-heavy mini mode)

Sources: [minirag/base.py:18-45]()

---

# Page: Storage Implementations

# Storage Implementations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [minirag/__init__.py](minirag/__init__.py)
- [minirag/base.py](minirag/base.py)
- [minirag/kg/weaviate_impl.py](minirag/kg/weaviate_impl.py)
- [minirag/minirag.py](minirag/minirag.py)
- [tests/test_weaviate.py](tests/test_weaviate.py)

</details>



This page provides a comprehensive overview of the storage systems used in MiniRAG. We will explore the storage abstractions, concrete implementations, and how they're integrated into the overall system architecture.

MiniRAG's storage layer is designed with flexibility in mind, supporting various backend technologies while providing consistent interfaces for the core functionality. This modular approach allows users to choose the most appropriate storage solution for their specific deployment needs.

## Storage Architecture Overview

MiniRAG adopts a layered storage approach with four primary storage types:

1. **Vector Storage**: For embedding-based similarity search
2. **Key-Value Storage**: For document and text chunk storage
3. **Graph Storage**: For storing relationships between entities and chunks
4. **Document Status Storage**: For tracking document processing status

```mermaid
classDiagram
    class StorageNameSpace {
        +namespace: str
        +global_config: dict
        +index_done_callback()
        +query_done_callback()
    }
    
    class BaseVectorStorage {
        +embedding_func
        +query(query, top_k)
        +upsert(data)
    }
    
    class BaseKVStorage {
        +get_by_id(id)
        +get_by_ids(ids)
        +filter_keys(data)
        +upsert(data)
    }
    
    class BaseGraphStorage {
        +get_node(node_id)
        +get_edge(source_id, target_id)
        +upsert_node(node_id, data)
        +upsert_edge(source_id, target_id, data)
    }
    
    class DocStatusStorage {
        +get_status_counts()
        +get_failed_docs()
        +get_pending_docs()
    }
    
    StorageNameSpace <|-- BaseVectorStorage
    StorageNameSpace <|-- BaseKVStorage
    StorageNameSpace <|-- BaseGraphStorage
    BaseKVStorage <|-- DocStatusStorage
```

Sources: [minirag/base.py:48-198]()

## Base Storage Abstractions

All storage implementations in MiniRAG inherit from a common set of abstract base classes that define standard interfaces for each storage type.

### StorageNameSpace

The foundational class for all storage types, providing namespace isolation and common functionality.

```python
@dataclass
class StorageNameSpace:
    namespace: str
    global_config: dict

    async def index_done_callback(self):
        """commit the storage operations after indexing"""
        pass

    async def query_done_callback(self):
        """commit the storage operations after querying"""
        pass
```

Sources: [minirag/base.py:48-60]()

### BaseVectorStorage

Abstract class for vector storage implementations, handling embeddings and similarity search.

```python
@dataclass
class BaseVectorStorage(StorageNameSpace):
    embedding_func: EmbeddingFunc
    meta_fields: set = field(default_factory=set)

    async def query(self, query: str, top_k: int) -> list[dict]:
        raise NotImplementedError

    async def upsert(self, data: dict[str, dict]):
        """Use 'content' field from value for embedding, use key as id.
        If embedding_func is None, use 'embedding' field from value
        """
        raise NotImplementedError
```

Sources: [minirag/base.py:62-74]()

### BaseKVStorage

Abstract class for key-value storage implementations, providing data retrieval by keys.

```python
@dataclass
class BaseKVStorage(Generic[T], StorageNameSpace):
    embedding_func: EmbeddingFunc

    async def all_keys(self) -> list[str]:
        raise NotImplementedError

    async def get_by_id(self, id: str) -> Union[T, None]:
        raise NotImplementedError

    async def get_by_ids(
        self, ids: list[str], fields: Union[set[str], None] = None
    ) -> list[Union[T, None]]:
        raise NotImplementedError

    async def filter_keys(self, data: list[str]) -> set[str]:
        """return un-exist keys"""
        raise NotImplementedError

    async def upsert(self, data: dict[str, T]):
        raise NotImplementedError

    async def drop(self):
        raise NotImplementedError
```

Sources: [minirag/base.py:77-101]()

### BaseGraphStorage

Abstract class for graph storage implementations, handling nodes and edges.

```python
@dataclass
class BaseGraphStorage(StorageNameSpace):
    embedding_func: EmbeddingFunc = None

    @abstractmethod
    async def get_types(self) -> tuple[list[str], list[str]]:
        raise NotImplementedError

    async def has_node(self, node_id: str) -> bool:
        raise NotImplementedError

    async def has_edge(self, source_node_id: str, target_node_id: str) -> bool:
        raise NotImplementedError

    async def get_node(self, node_id: str) -> Union[dict, None]:
        raise NotImplementedError

    async def get_edge(
        self, source_node_id: str, target_node_id: str
    ) -> Union[dict, None]:
        raise NotImplementedError

    async def upsert_node(self, node_id: str, node_data: dict[str, str]):
        raise NotImplementedError

    async def upsert_edge(
        self, source_node_id: str, target_node_id: str, edge_data: dict[str, str]
    ):
        raise NotImplementedError

    async def delete_node(self, node_id: str):
        raise NotImplementedError
```

Sources: [minirag/base.py:103-149]()

### DocStatusStorage

Abstract class for document status storage implementations, tracking document processing progress.

```python
class DocStatusStorage(BaseKVStorage):
    """Base class for document status storage"""

    async def get_status_counts(self) -> dict[str, int]:
        """Get counts of documents in each status"""
        raise NotImplementedError

    async def get_failed_docs(self) -> dict[str, DocProcessingStatus]:
        """Get all failed documents"""
        raise NotImplementedError

    async def get_pending_docs(self) -> dict[str, DocProcessingStatus]:
        """Get all pending documents"""
        raise NotImplementedError
```

Sources: [minirag/base.py:184-198]()

## Storage Implementations

MiniRAG supports a wide range of storage backends, allowing users to choose based on their specific requirements. The system uses a dynamic loading mechanism to instantiate the appropriate storage classes based on configuration.

```mermaid
graph TD
    subgraph "Storage Base Classes"
        StorageNameSpace["StorageNameSpace"]
        BaseVectorStorage["BaseVectorStorage"]
        BaseKVStorage["BaseKVStorage"]
        BaseGraphStorage["BaseGraphStorage"]
        DocStatusStorage["DocStatusStorage"]
    end
    
    subgraph "Vector Storage Implementations"
        NanoVectorDBStorage["NanoVectorDBStorage"]
        OracleVectorDBStorage["OracleVectorDBStorage"]
        MilvusVectorDBStorage["MilvusVectorDBStorage"]
        ChromaVectorDBStorage["ChromaVectorDBStorage"]
        TiDBVectorDBStorage["TiDBVectorDBStorage"]
        PGVectorStorage["PGVectorStorage"]
    end
    
    subgraph "KV Storage Implementations"
        JsonKVStorage["JsonKVStorage"]
        OracleKVStorage["OracleKVStorage"]
        MongoKVStorage["MongoKVStorage"]
        RedisKVStorage["RedisKVStorage"]
        TiDBKVStorage["TiDBKVStorage"]
        PGKVStorage["PGKVStorage"]
    end
    
    subgraph "Graph Storage Implementations"
        NetworkXStorage["NetworkXStorage"]
        Neo4JStorage["Neo4JStorage"]
        OracleGraphStorage["OracleGraphStorage"]
        MongoGraphStorage["MongoGraphStorage"]
        TiDBGraphStorage["TiDBGraphStorage"]
        AGEStorage["AGEStorage"]
        PGGraphStorage["PGGraphStorage"]
        GremlinStorage["GremlinStorage"]
    end
    
    subgraph "Doc Status Storage Implementations"
        JsonDocStatusStorage["JsonDocStatusStorage"]
        PGDocStatusStorage["PGDocStatusStorage"]
    end
    
    StorageNameSpace --> BaseVectorStorage
    StorageNameSpace --> BaseKVStorage
    StorageNameSpace --> BaseGraphStorage
    BaseKVStorage --> DocStatusStorage
    
    BaseVectorStorage --> NanoVectorDBStorage
    BaseVectorStorage --> OracleVectorDBStorage
    BaseVectorStorage --> MilvusVectorDBStorage
    BaseVectorStorage --> ChromaVectorDBStorage
    BaseVectorStorage --> TiDBVectorDBStorage
    BaseVectorStorage --> PGVectorStorage
    
    BaseKVStorage --> JsonKVStorage
    BaseKVStorage --> OracleKVStorage
    BaseKVStorage --> MongoKVStorage
    BaseKVStorage --> RedisKVStorage
    BaseKVStorage --> TiDBKVStorage
    BaseKVStorage --> PGKVStorage
    
    BaseGraphStorage --> NetworkXStorage
    BaseGraphStorage --> Neo4JStorage
    BaseGraphStorage --> OracleGraphStorage
    BaseGraphStorage --> MongoGraphStorage
    BaseGraphStorage --> TiDBGraphStorage
    BaseGraphStorage --> AGEStorage
    BaseGraphStorage --> PGGraphStorage
    BaseGraphStorage --> GremlinStorage
    
    DocStatusStorage --> JsonDocStatusStorage
    DocStatusStorage --> PGDocStatusStorage
```

Sources: [minirag/minirag.py:39-62]()

The available storage implementations are defined in the `STORAGES` dictionary in the MiniRAG codebase:

```python
STORAGES = {
    "NetworkXStorage": ".kg.networkx_impl",
    "JsonKVStorage": ".kg.json_kv_impl",
    "NanoVectorDBStorage": ".kg.nano_vector_db_impl",
    "JsonDocStatusStorage": ".kg.jsondocstatus_impl",
    "Neo4JStorage": ".kg.neo4j_impl",
    "OracleKVStorage": ".kg.oracle_impl",
    "OracleGraphStorage": ".kg.oracle_impl",
    "OracleVectorDBStorage": ".kg.oracle_impl",
    "MilvusVectorDBStorge": ".kg.milvus_impl",
    "MongoKVStorage": ".kg.mongo_impl",
    "MongoGraphStorage": ".kg.mongo_impl",
    "RedisKVStorage": ".kg.redis_impl",
    "ChromaVectorDBStorage": ".kg.chroma_impl",
    "TiDBKVStorage": ".kg.tidb_impl",
    "TiDBVectorDBStorage": ".kg.tidb_impl",
    "TiDBGraphStorage": ".kg.tidb_impl",
    "PGKVStorage": ".kg.postgres_impl",
    "PGVectorStorage": ".kg.postgres_impl",
    "AGEStorage": ".kg.age_impl",
    "PGGraphStorage": ".kg.postgres_impl",
    "GremlinStorage": ".kg.gremlin_impl",
    "PGDocStatusStorage": ".kg.postgres_impl",
}
```

Sources: [minirag/minirag.py:39-62]()

The storage classes are dynamically loaded using the `lazy_external_import` function:

```python
def lazy_external_import(module_name: str, class_name: str):
    """Lazily import a class from an external module based on the package of the caller."""

    # Get the caller's module and package
    import inspect

    caller_frame = inspect.currentframe().f_back
    module = inspect.getmodule(caller_frame)
    package = module.__package__ if module else None

    def import_class(*args, **kwargs):
        import importlib

        module = importlib.import_module(module_name, package=package)
        cls = getattr(module, class_name)
        return cls(*args, **kwargs)

    return import_class
```

Sources: [minirag/minirag.py:73-90]()

### Vector Storage Implementations

Vector storage implementations manage embeddings and provide similarity search functionality.

| Implementation | Backend Technology | Description |
|----------------|-------------------|-------------|
| NanoVectorDBStorage | In-memory vector database | Simple, lightweight vector database for development and testing |
| OracleVectorDBStorage | Oracle Database | Uses Oracle's vector capabilities for production workloads |
| MilvusVectorDBStorage | Milvus | Open-source vector database specialized for similarity search |
| ChromaVectorDBStorage | Chroma | Open-source embedding database |
| TiDBVectorDBStorage | TiDB | Distributed SQL database with vector capabilities |
| PGVectorStorage | PostgreSQL | Uses PostgreSQL with vector extensions |

Sources: [minirag/minirag.py:39-62]()

### Key-Value Storage Implementations

Key-Value storage implementations provide simple data persistence with key-based access.

| Implementation | Backend Technology | Description |
|----------------|-------------------|-------------|
| JsonKVStorage | Local JSON files | Simple file-based storage for development |
| OracleKVStorage | Oracle Database | Enterprise-grade key-value storage |
| MongoKVStorage | MongoDB | Document-oriented NoSQL database |
| RedisKVStorage | Redis | In-memory data structure store |
| TiDBKVStorage | TiDB | Distributed SQL database |
| PGKVStorage | PostgreSQL | Relational database with JSONB support |

Sources: [minirag/minirag.py:39-62]()

### Graph Storage Implementations

Graph storage implementations manage the relationships between entities and chunks.

| Implementation | Backend Technology | Description |
|----------------|-------------------|-------------|
| NetworkXStorage | NetworkX | In-memory graph library for Python |
| Neo4JStorage | Neo4j | Dedicated graph database |
| OracleGraphStorage | Oracle Graph | Enterprise graph database capabilities |
| MongoGraphStorage | MongoDB | Document database with graph features |
| TiDBGraphStorage | TiDB | SQL database with graph capabilities |
| AGEStorage | Apache AGE | PostgreSQL extension for graph data |
| PGGraphStorage | PostgreSQL | Relational database with graph functionality |
| GremlinStorage | Any Gremlin-compatible DB | Apache TinkerPop interface |

Sources: [minirag/minirag.py:39-62]()

### Document Status Storage Implementations

Document Status storage implementations track the processing status of documents.

| Implementation | Backend Technology | Description |
|----------------|-------------------|-------------|
| JsonDocStatusStorage | Local JSON files | Simple file-based status tracking |
| PGDocStatusStorage | PostgreSQL | Database-backed status tracking |

Sources: [minirag/minirag.py:39-62]()

## Storage Initialization and Usage

The MiniRAG class initializes storage implementations based on configuration parameters. By default, it uses lightweight file-based implementations suitable for development:

- `kv_storage = "JsonKVStorage"`
- `vector_storage = "NanoVectorDBStorage"`
- `graph_storage = "NetworkXStorage"`
- `doc_status_storage = "JsonDocStatusStorage"`

```mermaid
graph TD
    subgraph "MiniRAG"
        minirag["MiniRAG"]
    end
    
    subgraph "Vector Storage Instances"
        entities_vdb["entities_vdb\n(Entity Embeddings)"]
        entity_name_vdb["entity_name_vdb\n(Entity Name Embeddings)"]
        relationships_vdb["relationships_vdb\n(Relationship Embeddings)"]
        chunks_vdb["chunks_vdb\n(Chunk Embeddings)"]
    end
    
    subgraph "KV Storage Instances"
        full_docs["full_docs\n(Original Documents)"]
        text_chunks["text_chunks\n(Document Chunks)"]
        llm_response_cache["llm_response_cache\n(LLM Response Cache)"]
    end
    
    subgraph "Graph Storage Instances"
        chunk_entity_relation_graph["chunk_entity_relation_graph\n(Entity-Relation Graph)"]
    end
    
    subgraph "Doc Status Storage Instances"
        doc_status["doc_status\n(Document Processing Status)"]
    end
    
    minirag --> entities_vdb
    minirag --> entity_name_vdb
    minirag --> relationships_vdb
    minirag --> chunks_vdb
    
    minirag --> full_docs
    minirag --> text_chunks
    minirag --> llm_response_cache
    
    minirag --> chunk_entity_relation_graph
    
    minirag --> doc_status
    
    entities_vdb -- "used in" --> hybrid_query
    entities_vdb -- "used in" --> minirag_query
    entity_name_vdb -- "used in" --> minirag_query
    relationships_vdb -- "used in" --> hybrid_query
    relationships_vdb -- "used in" --> minirag_query
    chunks_vdb -- "used in" --> naive_query
    chunks_vdb -- "used in" --> minirag_query
    
    text_chunks -- "provides context" --> LLM
    chunk_entity_relation_graph -- "enhances retrieval" --> hybrid_query
    chunk_entity_relation_graph -- "enhances retrieval" --> minirag_query
```

Sources: [minirag/minirag.py:250-309]()

The MiniRAG class initializes a variety of storage instances for different purposes:

1. **Vector Storage Instances**:
   - `entities_vdb`: Stores entity embeddings for similarity search
   - `entity_name_vdb`: Stores entity name embeddings
   - `relationships_vdb`: Stores relationship embeddings
   - `chunks_vdb`: Stores document chunk embeddings

2. **Key-Value Storage Instances**:
   - `full_docs`: Stores original documents
   - `text_chunks`: Stores document chunks with metadata
   - `llm_response_cache`: Caches LLM responses for efficiency

3. **Graph Storage Instance**:
   - `chunk_entity_relation_graph`: Stores the heterogeneous graph connecting chunks, entities, and relationships

4. **Document Status Storage Instance**:
   - `doc_status`: Tracks document processing status

Sources: [minirag/minirag.py:250-309]()

## Configuring Storage Backends

The storage backends in MiniRAG can be configured by specifying the implementation types when creating a MiniRAG instance:

```python
from minirag import MiniRAG

# Use PostgreSQL for all storage types
rag = MiniRAG(
    kv_storage="PGKVStorage",
    vector_storage="PGVectorStorage",
    graph_storage="PGGraphStorage",
    doc_status_storage="PGDocStatusStorage",
    # Database connection parameters
    vector_db_storage_cls_kwargs={
        "connection_string": "postgresql://user:password@localhost:5432/database"
    }
)

# Use Neo4j for graph storage and MongoDB for document storage
rag = MiniRAG(
    kv_storage="MongoKVStorage",
    vector_storage="ChromaVectorDBStorage",
    graph_storage="Neo4JStorage",
    doc_status_storage="JsonDocStatusStorage",
    vector_db_storage_cls_kwargs={
        "mongo_uri": "mongodb://localhost:27017/",
        "neo4j_uri": "bolt://localhost:7687",
        "neo4j_user": "neo4j",
        "neo4j_password": "password"
    }
)
```

For database backends that require a client connection, the `set_storage_client` method can be used to set a shared database client for all storage instances:

```python
# Example: Setting an Oracle client for all storage instances
import oracledb

connection = oracledb.connect(user="user", password="password", dsn="localhost:1521/service")
rag.set_storage_client(connection)
```

Sources: [minirag/minirag.py:316-334]()

## Storage-Related Operations

The storage layer supports several key operations in MiniRAG:

1. **Document Insertion**: Stores document chunks, extracts entities, and builds relationships
   ```python
   rag.insert("Document content")
   ```

2. **Querying**: Retrieves relevant information based on the query mode
   ```python
   result = rag.query("Query text", param=QueryParam(mode="mini"))
   ```

3. **Entity Deletion**: Removes entities and their relationships from the system
   ```python
   rag.delete_by_entity("Entity name")
   ```

Sources: [minirag/minirag.py:336-607]()

## Conclusion

MiniRAG's storage system is designed to be flexible, allowing users to choose the most appropriate storage backend for their needs. The modular architecture provides a consistent interface across different storage technologies, from simple file-based implementations for development to enterprise-grade databases for production deployments.

For more information on specific aspects of the system:
- For details on vector-specific storage, see [Vector Storage](#5.1)
- For key-value storage details, see [Key-Value Storage](#5.2) 
- For graph storage details, see [Graph Storage](#5.3)
- For document status tracking details, see [Document Status Storage](#5.4)

---

# Page: Graph Storage Backends

# Graph Storage Backends

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [minirag/kg/networkx_impl.py](minirag/kg/networkx_impl.py)
- [minirag/kg/weaviate_impl.py](minirag/kg/weaviate_impl.py)
- [minirag/minirag.py](minirag/minirag.py)
- [tests/test_weaviate.py](tests/test_weaviate.py)

</details>



Graph Storage Backends in MiniRAG provide pluggable implementations for storing, retrieving, and manipulating knowledge graphs built from document entities and their relationships. MiniRAG supports multiple graph database backends through a unified interface, allowing users to choose the most appropriate storage solution for their deployment requirements.

The framework currently supports eight graph storage backends: NetworkX (in-memory), Neo4j (native graph database), PostgreSQL with AGE extension, TiDB, Oracle, MongoDB, Weaviate, and Gremlin-compatible databases.

Sources: [minirag/base.py:104-148](), [minirag/minirag.py:39-66]()

## Base Graph Storage Interface

The graph storage system in MiniRAG is built on a well-defined abstraction layer that allows for different backend implementations while maintaining a consistent API.

```mermaid
classDiagram
    class StorageNameSpace {
        +namespace: str
        +global_config: dict
        +index_done_callback()
        +query_done_callback()
    }
    
    class BaseGraphStorage {
        +embedding_func
        +get_types()
        +has_node(node_id)
        +has_edge(source_id, target_id)
        +node_degree(node_id)
        +edge_degree(src_id, tgt_id)
        +get_node(node_id)
        +get_edge(source_id, target_id)
        +get_node_edges(source_id)
        +upsert_node(node_id, data)
        +upsert_edge(source_id, target_id, data)
        +delete_node(node_id)
        +embed_nodes(algorithm)
    }
    
    class NetworkXStorage {
        +_graph: nx.Graph
        +_graphml_xml_file: str
    }
    
    class Neo4JStorage {
        +_driver: AsyncDriver
        +_DATABASE: str
    }
    
    class PGGraphStorage {
        +_pool: asyncpg.Pool
        +_table_name: str
    }
    
    class AGEStorage {
        +_pool: asyncpg.Pool
        +_graph_name: str
    }
    
    class TiDBGraphStorage {
        +_pool: aiomysql.Pool
        +_database: str
    }
    
    class OracleGraphStorage {
        +_pool: oracledb.Pool
        +_schema: str
    }
    
    class MongoGraphStorage {
        +_client: AsyncIOMotorClient
        +_collection: str
    }
    
    class WeaviateGraphStorage {
        +client: weaviate.Client
    }
    
    class GremlinStorage {
        +_client: DriverRemoteConnection
    }
    
    StorageNameSpace <|-- BaseGraphStorage
    BaseGraphStorage <|-- NetworkXStorage
    BaseGraphStorage <|-- Neo4JStorage
    BaseGraphStorage <|-- PGGraphStorage
    BaseGraphStorage <|-- AGEStorage
    BaseGraphStorage <|-- TiDBGraphStorage
    BaseGraphStorage <|-- OracleGraphStorage
    BaseGraphStorage <|-- MongoGraphStorage
    BaseGraphStorage <|-- WeaviateGraphStorage
    BaseGraphStorage <|-- GremlinStorage
```

*Class Hierarchy Diagram for MiniRAG Graph Storage Backends*

Sources: [minirag/base.py:48-148](), [minirag/minirag.py:39-66](), [minirag/kg/networkx_impl.py:69-70](), [minirag/kg/weaviate_impl.py:166-167]()

The `BaseGraphStorage` abstract class defines the interface that all graph storage implementations must adhere to:

| Method | Purpose |
|--------|---------|
| `get_types()` | Returns all node types in the graph |
| `has_node(node_id)` | Checks if a node exists in the graph |
| `has_edge(source_id, target_id)` | Checks if an edge exists between two nodes |
| `node_degree(node_id)` | Gets the degree (number of connections) of a node |
| `edge_degree(src_id, tgt_id)` | Gets the combined degree of an edge's nodes |
| `get_node(node_id)` | Retrieves a node's data |
| `get_edge(source_id, target_id)` | Retrieves an edge's data |
| `get_node_edges(source_id)` | Gets all edges connected to a node |
| `upsert_node(node_id, data)` | Inserts or updates a node |
| `upsert_edge(source_id, target_id, data)` | Inserts or updates an edge |
| `delete_node(node_id)` | Removes a node from the graph |
| `embed_nodes(algorithm)` | Embeds nodes using a specified algorithm |

Sources: [minirag/base.py:104-148]()

## NetworkX Storage Implementation

The `NetworkXStorage` implementation provides an in-memory graph storage solution using the NetworkX library. This implementation is ideal for smaller knowledge graphs and development scenarios.

```mermaid
flowchart TB
    subgraph "NetworkXStorage Components"
        direction TB
        
        Graph["nx.Graph Object"]
        GraphMLFile["GraphML File (.graphml)"]
        
        Graph -- "save" --> GraphMLFile
        GraphMLFile -- "load" --> Graph
    end
    
    subgraph "Graph Operations"
        direction TB
        UpsertNode["upsert_node()"]
        UpsertEdge["upsert_edge()"]
        GetNode["get_node()"]
        GetEdge["get_edge()"]
        GetNodeEdges["get_node_edges()"]
        DeleteNode["delete_node()"]
    end
    
    UpsertNode --> Graph
    UpsertEdge --> Graph
    Graph --> GetNode
    Graph --> GetEdge
    Graph --> GetNodeEdges
    DeleteNode --> Graph
    
    subgraph "Callbacks"
        IndexDone["index_done_callback()"]
    end
    
    IndexDone --> GraphMLFile
```

*NetworkX Storage Data Flow Diagram*

Sources: [minirag/kg/networkx_impl.py:69-276]()

Key features of the NetworkX implementation:

1. **Persistent Storage**: Graphs are stored as GraphML files, loaded on initialization, and saved after indexing.
   ```python
   # File path is defined in __post_init__
   self._graphml_xml_file = os.path.join(
       self.global_config["working_dir"], f"graph_{self.namespace}.graphml"
   )
   ```

2. **Graph Stabilization**: Provides methods to ensure graph consistency with `stable_largest_connected_component` and `_stabilize_graph` functions.

3. **Node and Edge Operations**: Implements all required operations for manipulating graph elements:
   ```python
   # Example implementation of node retrieval
   async def get_node(self, node_id: str) -> Union[dict, None]:
       return self._graph.nodes.get(node_id)
   ```

4. **Extended Functionality**: Offers additional functionality like multi-hop neighbors retrieval:
   ```python
   async def get_neighbors_within_k_hops(self, source_node_id: str, k):
       # Implementation to get all neighbors up to k hops away
   ```

Sources: [minirag/kg/networkx_impl.py:132-267]()

## Neo4j Storage Implementation

`Neo4JStorage` provides a native graph database backend using Neo4j. This implementation is suitable for production deployments requiring advanced graph query capabilities and ACID transactions.

**Configuration**: Requires `NEO4J_URI`, `NEO4J_USERNAME`, and `NEO4J_PASSWORD` environment variables.

**Key Features**:
- Native graph database with Cypher query language
- Asynchronous operations using `AsyncDriver` and `AsyncSession`
- Retry mechanisms with exponential backoff for transient errors
- Advanced graph traversal with `get_knowledge_graph()` method
- Node label-based indexing for efficient lookups

**Import Path**: `.kg.neo4j_impl`

Sources: [minirag/minirag.py:44](), [minirag/kg/neo4j_impl.py:30-531]()

## PostgreSQL Storage Implementations

MiniRAG provides two PostgreSQL-based graph storage implementations:

### PGGraphStorage

`PGGraphStorage` implements graph storage using native PostgreSQL tables with foreign key relationships to represent edges.

**Configuration**: Uses PostgreSQL connection pool (`asyncpg.Pool`)

**Key Features**:
- Relational representation of graph data
- Standard PostgreSQL tables for nodes and edges
- Efficient for simple graph queries
- Compatible with existing PostgreSQL infrastructure

**Import Path**: `.kg.postgres_impl`

Sources: [minirag/minirag.py:59]()

### AGEStorage

`AGEStorage` leverages Apache AGE (A Graph Extension) for PostgreSQL, providing native graph capabilities within PostgreSQL.

**Configuration**: Requires PostgreSQL with AGE extension installed

**Key Features**:
- Native graph data type support in PostgreSQL
- Cypher-like query language support
- Graph-optimized storage and indexing
- Combines relational and graph query capabilities

**Import Path**: `.kg.age_impl`

Sources: [minirag/minirag.py:58]()

## TiDB Storage Implementation

`TiDBGraphStorage` provides distributed graph storage using TiDB, a MySQL-compatible distributed database.

**Configuration**: Uses TiDB connection pool (`aiomysql.Pool`)

**Key Features**:
- Horizontally scalable graph storage
- MySQL-compatible interface
- Distributed transaction support
- High availability and fault tolerance
- Suitable for large-scale deployments

**Import Path**: `.kg.tidb_impl`

Sources: [minirag/minirag.py:53-55]()

## Oracle Storage Implementation

`OracleGraphStorage` implements graph storage using Oracle Database's native graph capabilities.

**Configuration**: Requires Oracle Database connection credentials

**Key Features**:
- Enterprise-grade database features
- Native graph data types and queries
- Advanced indexing and optimization
- ACID transaction support
- Integration with Oracle ecosystem

**Import Path**: `.kg.oracle_impl`

Sources: [minirag/minirag.py:45-47]()

## MongoDB Storage Implementation

`MongoGraphStorage` provides document-based graph storage using MongoDB.

**Configuration**: Uses MongoDB connection string and `AsyncIOMotorClient`

**Key Features**:
- Document-oriented graph representation
- Flexible schema for node and edge attributes
- Aggregation pipeline for graph traversal
- Horizontal scalability
- JSON-native data model

**Import Path**: `.kg.mongo_impl`

Sources: [minirag/minirag.py:49-50]()

## Weaviate Storage Implementation

`WeaviateGraphStorage` implements graph storage using Weaviate, a cloud-native vector database.

**Configuration**: Connects to Weaviate instance at `http://localhost:8080` by default

**Key Features**:
- Graph storage with integrated vector search
- Cloud-native architecture
- Schema-based data model with `GraphNode` class
- Reference-based edge representation using `linkedTo` property
- Batch operations for efficient data loading

**Implementation Details**:

```mermaid
flowchart TB
    subgraph WeaviateGraph["WeaviateGraphStorage"]
        Client["weaviate.Client"]
        Schema["GraphNode Schema"]
        NodeOps["Node Operations"]
        EdgeOps["Edge Reference Operations"]
    end
    
    subgraph SchemaStructure["Schema Structure"]
        GraphNode["GraphNode Class"]
        NameProp["name property"]
        LinkedToProp["linkedTo property"]
        
        GraphNode --> NameProp
        GraphNode --> LinkedToProp
    end
    
    Client --> Schema
    Schema --> NodeOps
    Schema --> EdgeOps
    NodeOps --> GraphNode
    EdgeOps --> LinkedToProp
```

*Weaviate Graph Storage Architecture*

The Weaviate implementation uses a schema-based approach where graph nodes are stored as `GraphNode` objects with a `linkedTo` cross-reference property for edges. Node operations use `data_object.create()` and `data_object.delete()`, while edge operations use `data_object.add_reference()`.

**Import Path**: `.kg.weaviate_impl`

Sources: [minirag/minirag.py:62-64](), [minirag/kg/weaviate_impl.py:166-261]()

## Gremlin Storage Implementation

`GremlinStorage` provides compatibility with Gremlin-compatible graph databases (e.g., Amazon Neptune, JanusGraph, Azure Cosmos DB).

**Configuration**: Uses Gremlin `DriverRemoteConnection`

**Key Features**:
- Standard Gremlin query language
- Compatible with multiple graph database backends
- Graph traversal-based operations
- Cloud provider integrations

**Import Path**: `.kg.gremlin_impl`

Sources: [minirag/minirag.py:60]()

## Data Model and Graph Representation

Both implementations represent knowledge graphs using a consistent data model:

```mermaid
erDiagram
    NODE {
        string node_id
        string entity_type
        string content
        dict attributes
    }
    
    EDGE {
        string relation_type
        string description
        dict attributes
    }
    
    NODE ||--o{ EDGE : "source"
    NODE ||--o{ EDGE : "target"
```

*Graph Data Model Diagram*

Sources: [minirag/kg/networkx_impl.py:221-227](), [minirag/kg/neo4j_impl.py:306-379]()

Key aspects of the graph representation:

1. **Nodes**: Represent entities with unique identifiers and attributes:
   - In NetworkX: Nodes are identified by their ID and store properties directly
   - In Neo4j: Nodes use labels as identifiers and store properties internally

2. **Edges**: Represent relationships between entities:
   - In NetworkX: Edges are identified by source and target node IDs
   - In Neo4j: Edges use the `DIRECTED` relationship type with properties

3. **Properties**: Both nodes and edges can have arbitrary properties stored as key-value pairs.

This consistent representation ensures that the underlying storage implementation is transparent to the rest of the system, allowing seamless switching between implementations.

Sources: [minirag/base.py:136-142]()

## Backend Comparison and Selection

| Backend | Storage Type | Scalability | Query Language | Use Case | Setup Complexity |
|---------|-------------|-------------|----------------|----------|------------------|
| **NetworkX** | In-memory + file | Memory-limited | Python API | Development, small graphs | Low |
| **Neo4j** | Native graph DB | Highly scalable | Cypher | Production, complex queries | Medium |
| **PostgreSQL (PGGraphStorage)** | Relational tables | Medium | SQL | Existing PostgreSQL infrastructure | Low-Medium |
| **PostgreSQL (AGEStorage)** | Graph extension | Medium-High | Cypher-like | PostgreSQL with graph needs | Medium |
| **TiDB** | Distributed SQL | Highly scalable | SQL | Large-scale, distributed deployments | Medium-High |
| **Oracle** | Enterprise DB | Highly scalable | SQL + Graph queries | Enterprise environments | High |
| **MongoDB** | Document store | Highly scalable | Aggregation pipeline | Flexible schema, JSON data | Medium |
| **Weaviate** | Vector + Graph | High | GraphQL + Custom | Vector search + graph | Medium |
| **Gremlin** | Varies by backend | Varies | Gremlin | Cloud deployments, portability | Medium-High |

**Selection Criteria**:

1. **Development vs Production**: Use `NetworkXStorage` for development and testing. Use Neo4j, TiDB, or Oracle for production.

2. **Existing Infrastructure**: Choose backends that align with your existing database infrastructure:
   - PostgreSQL → `PGGraphStorage` or `AGEStorage`
   - Oracle ecosystem → `OracleGraphStorage`
   - MongoDB experience → `MongoGraphStorage`

3. **Scale Requirements**:
   - Small graphs (<100K nodes) → `NetworkXStorage`
   - Medium graphs (100K-10M nodes) → Neo4j, PostgreSQL (AGE)
   - Large graphs (>10M nodes) → TiDB, Oracle, distributed solutions

4. **Query Complexity**:
   - Simple lookups → Any backend
   - Complex graph traversal → Neo4j, AGE, Gremlin
   - Hybrid vector + graph queries → Weaviate

5. **Deployment Environment**:
   - Local/single machine → NetworkX, PostgreSQL
   - Cloud environments → Weaviate, Gremlin (Neptune/Cosmos DB), TiDB
   - On-premise clusters → TiDB, Oracle

Sources: [minirag/minirag.py:39-66](), [minirag/kg/networkx_impl.py:69-276](), [minirag/kg/weaviate_impl.py:166-261]()

## Configuration and Initialization

Graph storage backends are configured in the `MiniRAG` class through the `graph_storage` parameter. The storage class is dynamically loaded using the `lazy_external_import` mechanism.

**Configuration Example**:

```python
# In MiniRAG initialization
@dataclass
class MiniRAG:
    graph_storage: str = field(default="NetworkXStorage")
    # ... other fields
```

**Storage Class Resolution**:

The storage class name is resolved through the `STORAGES` dictionary which maps class names to their import paths:

```python
STORAGES = {
    "NetworkXStorage": ".kg.networkx_impl",
    "Neo4JStorage": ".kg.neo4j_impl",
    "PGGraphStorage": ".kg.postgres_impl",
    "AGEStorage": ".kg.age_impl",
    "TiDBGraphStorage": ".kg.tidb_impl",
    "OracleGraphStorage": ".kg.oracle_impl",
    "MongoGraphStorage": ".kg.mongo_impl",
    "WeaviateGraphStorage": ".kg.weaviate_impl",
    "GremlinStorage": ".kg.gremlin_impl",
}
```

**Initialization Process**:

```mermaid
flowchart LR
    MiniRAGInit["MiniRAG.__post_init__()"]
    GetClass["_get_storage_class()"]
    LazyImport["lazy_external_import()"]
    StorageDict["STORAGES dict"]
    ImportModule["importlib.import_module()"]
    CreateInstance["graph_storage_cls()"]
    GraphInstance["chunk_entity_relation_graph"]
    
    MiniRAGInit --> GetClass
    GetClass --> StorageDict
    GetClass --> LazyImport
    LazyImport --> ImportModule
    ImportModule --> CreateInstance
    CreateInstance --> GraphInstance
```

*Graph Storage Initialization Flow*

The initialized graph storage instance is assigned to `chunk_entity_relation_graph` and used throughout the document processing and query pipelines.

Sources: [minirag/minirag.py:213-227](), [minirag/minirag.py:264-268](), [minirag/minirag.py:315-318]()

## Integration with MiniRAG

Graph storage backends integrate with MiniRAG's core pipelines through the `chunk_entity_relation_graph` instance.

```mermaid
flowchart TB
    subgraph Indexing["Document Indexing Pipeline"]
        ExtractEntities["extract_entities()"]
        UpsertNode["graph.upsert_node()"]
        UpsertEdge["graph.upsert_edge()"]
        IndexDone["graph.index_done_callback()"]
    end
    
    subgraph Storage["chunk_entity_relation_graph"]
        GraphStorage["Selected Graph Backend"]
    end
    
    subgraph Query["Query Pipeline"]
        MiniRAGQuery["minirag_query()"]
        GetNeighbors["graph.get_neighbors_within_k_hops()"]
        GetNode["graph.get_node()"]
        HasNode["graph.has_node()"]
    end
    
    ExtractEntities --> UpsertNode
    ExtractEntities --> UpsertEdge
    UpsertNode --> GraphStorage
    UpsertEdge --> GraphStorage
    IndexDone --> GraphStorage
    
    MiniRAGQuery --> GetNeighbors
    MiniRAGQuery --> GetNode
    MiniRAGQuery --> HasNode
    GetNeighbors --> GraphStorage
    GetNode --> GraphStorage
    HasNode --> GraphStorage
```

*Graph Storage Integration in MiniRAG Pipelines*

**Indexing Phase**: During document insertion, the `extract_entities` function creates nodes and edges in the graph storage using `upsert_node()` and `upsert_edge()`. After indexing completes, `index_done_callback()` is called to persist data (e.g., writing GraphML files for NetworkX, committing transactions for databases).

**Query Phase**: During query processing, graph storage is used for topology-enhanced retrieval through methods like `get_neighbors_within_k_hops()`, `get_node()`, and `has_node()` to traverse the knowledge graph and find related entities.

Sources: [minirag/minirag.py:264-268](), [minirag/minirag.py:379-387](), [minirag/minirag.py:516-531](), [minirag/minirag.py:549-560]()

## Extending Graph Storage

The `BaseGraphStorage` abstract interface enables adding new graph storage backends. 

**Required Methods**:

All graph storage implementations must implement the following methods defined in `BaseGraphStorage`:

| Method | Return Type | Purpose |
|--------|-------------|---------|
| `get_types()` | `tuple[List[str], List[str]]` | Returns node types and edge types |
| `has_node(node_id)` | `bool` | Checks node existence |
| `has_edge(source_id, target_id)` | `bool` | Checks edge existence |
| `node_degree(node_id)` | `int` | Returns node connection count |
| `edge_degree(src_id, tgt_id)` | `int` | Returns combined degree of edge endpoints |
| `get_node(node_id)` | `Union[dict, None]` | Retrieves node data |
| `get_edge(source_id, target_id)` | `Union[dict, None]` | Retrieves edge data |
| `get_node_edges(source_id)` | `Union[List[tuple], None]` | Gets all edges for a node |
| `upsert_node(node_id, node_data)` | `None` | Inserts or updates a node |
| `upsert_edge(source_id, target_id, edge_data)` | `None` | Inserts or updates an edge |
| `delete_node(node_id)` | `None` | Deletes a node |
| `embed_nodes(algorithm)` | `tuple[np.ndarray, list[str]]` | Generates node embeddings |

**Adding a New Backend**:

1. **Create Implementation Class**: Inherit from `BaseGraphStorage` and implement all required methods
2. **Add to STORAGES Dictionary**: Add the class name and import path to the `STORAGES` dictionary in `minirag.py`
3. **Implement Connection Management**: Handle database connections in `__post_init__()` method
4. **Implement Callbacks**: Provide `index_done_callback()` for persistence operations

**Example Structure**:

```python
from minirag.base import BaseGraphStorage

@dataclass
class MyGraphStorage(BaseGraphStorage):
    def __post_init__(self):
        # Initialize database connection
        self._client = MyDatabaseClient(...)
    
    async def has_node(self, node_id: str) -> bool:
        # Implementation
        pass
    
    # ... implement other required methods
```

For detailed guidance on extending storage backends, see page 10.1.

Sources: [minirag/base.py:104-148](), [minirag/minirag.py:315-318]()

## Summary

Graph Storage in MiniRAG provides a flexible and consistent interface for storing and manipulating knowledge graphs. The system offers two concrete implementations:

1. **NetworkXStorage**: An in-memory implementation using the NetworkX library, suitable for development and smaller applications.
2. **Neo4JStorage**: A robust implementation using the Neo4j graph database, suitable for production and larger-scale deployments.

Both implementations adhere to the common interface defined by `BaseGraphStorage`, allowing for transparent switching between backends while maintaining consistent behavior throughout the system. This architecture supports MiniRAG's core capabilities of heterogeneous graph indexing and topology-enhanced retrieval.

Sources: [minirag/base.py:104-148](), [minirag/kg/networkx_impl.py:69-276](), [minirag/kg/neo4j_impl.py:30-531]()

---

# Page: Vector Storage Backends

# Vector Storage Backends

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [minirag/__init__.py](minirag/__init__.py)
- [minirag/base.py](minirag/base.py)
- [minirag/kg/weaviate_impl.py](minirag/kg/weaviate_impl.py)
- [minirag/minirag.py](minirag/minirag.py)
- [tests/test_weaviate.py](tests/test_weaviate.py)

</details>



This page documents the vector storage layer in MiniRAG, which enables efficient similarity search for entities, entity names, relationships, and text chunks. Vector storage backends implement semantic search capabilities that are essential for retrieval operations.

For graph-based storage of entity relationships, see [Graph Storage Backends](#5.1). For text chunk key-value storage, see [Key-Value Storage Backends](#5.3).

## Purpose and Scope

Vector storage backends provide embedding-based similarity search for four distinct data types in MiniRAG's heterogeneous graph index. Each vector database instance stores embeddings and supports top-k nearest neighbor queries to retrieve contextually relevant information during query processing.

## Vector Storage Architecture

MiniRAG maintains four separate vector database instances, each serving a specific role in the retrieval pipeline:

```mermaid
graph TB
    subgraph "MiniRAG Core"
        MiniRAG["MiniRAG<br/>(minirag.py)"]
    end
    
    subgraph "Vector Storage Instances"
        entities_vdb["entities_vdb<br/>namespace='entities'<br/>meta_fields={'entity_name'}"]
        entity_name_vdb["entity_name_vdb<br/>namespace='entities_name'<br/>meta_fields={'entity_name'}"]
        relationships_vdb["relationships_vdb<br/>namespace='relationships'<br/>meta_fields={'src_id', 'tgt_id'}"]
        chunks_vdb["chunks_vdb<br/>namespace='chunks'<br/>meta_fields={}"]
    end
    
    subgraph "Backend Implementations"
        NanoVectorDB["NanoVectorDBStorage<br/>(.kg.nano_vector_db_impl)"]
        Weaviate["WeaviateVectorStorage<br/>(.kg.weaviate_impl)"]
        Chroma["ChromaVectorDBStorage<br/>(.kg.chroma_impl)"]
        Milvus["MilvusVectorDBStorge<br/>(.kg.milvus_impl)"]
        TiDB["TiDBVectorDBStorage<br/>(.kg.tidb_impl)"]
        PGVector["PGVectorStorage<br/>(.kg.postgres_impl)"]
        Oracle["OracleVectorDBStorage<br/>(.kg.oracle_impl)"]
    end
    
    MiniRAG --> entities_vdb
    MiniRAG --> entity_name_vdb
    MiniRAG --> relationships_vdb
    MiniRAG --> chunks_vdb
    
    entities_vdb -.implements.-> NanoVectorDB
    entity_name_vdb -.implements.-> Weaviate
    relationships_vdb -.implements.-> Chroma
    chunks_vdb -.implements.-> Milvus
```

**Sources:** [minirag/minirag.py:273-298](), [minirag/minirag.py:39-66]()

### The Four Vector Storage Instances

| Instance | Namespace | Meta Fields | Purpose | Usage |
|----------|-----------|-------------|---------|-------|
| `entities_vdb` | `"entities"` | `{"entity_name"}` | Stores entity descriptions with embeddings | Entity-based retrieval in light/mini modes |
| `entity_name_vdb` | `"entities_name"` | `{"entity_name"}` | Stores entity names with embeddings | Efficient entity name matching in queries |
| `relationships_vdb` | `"relationships"` | `{"src_id", "tgt_id"}` | Stores relationship descriptions between entities | Relationship-based context retrieval |
| `chunks_vdb` | `"chunks"` | `{}` | Stores text chunk embeddings | Naive mode vector search and fallback retrieval |

**Sources:** [minirag/minirag.py:273-298]()

## BaseVectorStorage Interface

All vector storage backends implement the `BaseVectorStorage` abstract class, which defines the contract for similarity search and data insertion operations.

```mermaid
classDiagram
    class StorageNameSpace {
        +namespace: str
        +global_config: dict
        +index_done_callback() async
        +query_done_callback() async
    }
    
    class BaseVectorStorage {
        +embedding_func: EmbeddingFunc
        +meta_fields: set
        +query(query: str, top_k: int) async list~dict~
        +upsert(data: dict) async
    }
    
    class WeaviateVectorStorage {
        +client: weaviate.Client
        +init_schema()
        +query(query: str, top_k: int) async
        +upsert(data: dict) async
        +delete(ids: list) async
        +clear() async
        +count() async int
    }
    
    class NanoVectorDBStorage {
        <<implementation>>
    }
    
    class ChromaVectorDBStorage {
        <<implementation>>
    }
    
    StorageNameSpace <|-- BaseVectorStorage
    BaseVectorStorage <|-- WeaviateVectorStorage
    BaseVectorStorage <|-- NanoVectorDBStorage
    BaseVectorStorage <|-- ChromaVectorDBStorage
```

**Sources:** [minirag/base.py:62-75](), [minirag/base.py:48-59]()

### Core Methods

#### `query(query: str, top_k: int) -> list[dict]`

Performs similarity search to retrieve the top-k most relevant items based on the query string.

- **Parameters:**
  - `query`: The search query text
  - `top_k`: Number of results to return
- **Returns:** List of dictionaries containing matched items with their metadata
- **Implementation:** Query text is embedded using `embedding_func`, then nearest neighbor search is performed

**Sources:** [minirag/base.py:67-68]()

#### `upsert(data: dict[str, dict])`

Inserts or updates vector data in the storage backend.

- **Parameters:**
  - `data`: Dictionary mapping IDs to data dictionaries. Each value must contain a `"content"` field for embedding generation, or an `"embedding"` field if embeddings are pre-computed
- **Behavior:** Uses the `embedding_func` to generate embeddings from `"content"` field, then stores the embedding with the provided ID and metadata

**Sources:** [minirag/base.py:70-74]()

## Vector Storage Initialization

Vector storage instances are initialized during `MiniRAG.__post_init__()` with shared configuration and embedding functions:

```mermaid
sequenceDiagram
    participant Client
    participant MiniRAG
    participant VectorStorageCls
    participant EmbeddingFunc
    
    Client->>MiniRAG: __init__(vector_storage="NanoVectorDBStorage")
    MiniRAG->>MiniRAG: __post_init__()
    MiniRAG->>MiniRAG: _get_storage_class("NanoVectorDBStorage")
    Note over MiniRAG: Lazy import from .kg.nano_vector_db_impl
    
    MiniRAG->>MiniRAG: Apply partial(vector_db_storage_cls, global_config)
    
    loop For each vector instance
        MiniRAG->>VectorStorageCls: vector_db_storage_cls(namespace, embedding_func, meta_fields)
        VectorStorageCls->>VectorStorageCls: Initialize storage backend
        VectorStorageCls-->>MiniRAG: Vector storage instance
    end
    
    MiniRAG->>EmbeddingFunc: limit_async_func_call(embedding_func)
    Note over MiniRAG: Rate limit embedding function
```

**Sources:** [minirag/minirag.py:190-314](), [minirag/minirag.py:210-227]()

### Configuration Parameters

Vector storage is configured through the `MiniRAG` dataclass fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `vector_storage` | `str` | `"NanoVectorDBStorage"` | Class name of vector storage backend |
| `embedding_func` | `EmbeddingFunc` | `None` | Function to generate embeddings from text |
| `embedding_batch_num` | `int` | `32` | Batch size for embedding generation |
| `embedding_func_max_async` | `int` | `16` | Maximum concurrent embedding calls |
| `vector_db_storage_cls_kwargs` | `dict` | `{}` | Additional kwargs for storage initialization |

**Sources:** [minirag/minirag.py:130-173]()

## Concrete Backend Implementations

### NanoVectorDBStorage

Default lightweight vector database implementation, suitable for development and small-scale deployments.

- **Module:** `.kg.nano_vector_db_impl`
- **Features:** In-memory vector storage with simple similarity search
- **Use Case:** Development, testing, small datasets (<100K vectors)

**Sources:** [minirag/minirag.py:42](), [minirag/minirag.py:131]()

### WeaviateVectorStorage

Cloud-native vector database with advanced features and scalability.

```mermaid
graph TB
    subgraph "WeaviateVectorStorage Implementation"
        WeaviateClass["WeaviateVectorStorage<br/>BaseVectorStorage"]
        
        client["client: weaviate.Client<br/>(http://localhost:8080)"]
        
        init_schema["init_schema()<br/>Creates 'Document' class<br/>properties: ['content']"]
        
        query_method["query(query, top_k)<br/>Uses with_near_text()<br/>Returns top_k documents"]
        
        upsert_method["upsert(data)<br/>Calls data_object.create()<br/>For each id-value pair"]
        
        delete_method["delete(ids)<br/>Calls data_object.delete()"]
        
        clear_method["clear()<br/>batch.delete_objects()"]
        
        count_method["count()<br/>aggregate().with_meta_count()"]
    end
    
    WeaviateClass --> client
    WeaviateClass --> init_schema
    WeaviateClass --> query_method
    WeaviateClass --> upsert_method
    WeaviateClass --> delete_method
    WeaviateClass --> clear_method
    WeaviateClass --> count_method
```

**Features:**
- Schema management with class creation
- Near-text semantic search using Weaviate's vectorizer
- Batch operations for bulk delete
- Metadata counting and aggregation

**Configuration:**
```python
rag = MiniRAG(
    vector_storage="WeaviateVectorStorage",
    # Weaviate connects to http://localhost:8080 by default
)
```

**Sources:** [minirag/kg/weaviate_impl.py:16-86](), [minirag/minirag.py:62]()

### ChromaVectorDBStorage

Open-source embedding database optimized for AI applications.

- **Module:** `.kg.chroma_impl`
- **Features:** Persistent storage, multiple distance metrics, filtering
- **Use Case:** Medium-scale deployments, local development

**Sources:** [minirag/minirag.py:52]()

### MilvusVectorDBStorage

High-performance distributed vector database.

- **Module:** `.kg.milvus_impl`
- **Features:** Horizontal scaling, GPU acceleration, hybrid search
- **Use Case:** Large-scale production deployments (>1M vectors)

**Sources:** [minirag/minirag.py:48]()

### PostgreSQL with PGVector

Vector search extension for PostgreSQL.

- **Module:** `.kg.postgres_impl`
- **Implementation:** `PGVectorStorage`
- **Features:** SQL integration, ACID transactions, existing PostgreSQL infrastructure
- **Use Case:** Organizations already using PostgreSQL

**Sources:** [minirag/minirag.py:57]()

### TiDB Vector Storage

Distributed vector storage in TiDB database.

- **Module:** `.kg.tidb_impl`
- **Implementation:** `TiDBVectorDBStorage`
- **Features:** Distributed architecture, horizontal scaling
- **Use Case:** TiDB users needing vector search

**Sources:** [minirag/minirag.py:54]()

### Oracle Vector Storage

Enterprise-grade vector storage in Oracle Database.

- **Module:** `.kg.oracle_impl`
- **Implementation:** `OracleVectorDBStorage`
- **Features:** Enterprise security, high availability, Oracle ecosystem integration
- **Use Case:** Enterprise deployments with Oracle infrastructure

**Sources:** [minirag/minirag.py:47]()

## Vector Storage in Query Modes

Different query modes utilize vector storage instances differently:

```mermaid
graph LR
    subgraph "Query Modes"
        naive["Naive Mode<br/>(naive_query)"]
        light["Light Mode<br/>(hybrid_query)"]
        mini["Mini Mode<br/>(minirag_query)"]
    end
    
    subgraph "Vector Storage Usage"
        chunks_naive["chunks_vdb<br/>Simple vector search"]
        
        entities_light["entities_vdb<br/>Entity descriptions"]
        relationships_light["relationships_vdb<br/>Relationship context"]
        
        entities_mini["entities_vdb<br/>Entity retrieval"]
        entity_name_mini["entity_name_vdb<br/>Entity name matching"]
        relationships_mini["relationships_vdb<br/>Relationship paths"]
        chunks_mini["chunks_vdb<br/>Chunk-level retrieval"]
    end
    
    naive --> chunks_naive
    
    light --> entities_light
    light --> relationships_light
    
    mini --> entities_mini
    mini --> entity_name_mini
    mini --> relationships_mini
    mini --> chunks_mini
```

**Sources:** [minirag/minirag.py:537-572]()

### Naive Mode

Uses only `chunks_vdb` for simple vector similarity search across all text chunks.

```python
response = await naive_query(
    query,
    self.chunks_vdb,  # Only vector storage used
    self.text_chunks,
    param,
    asdict(self),
)
```

**Sources:** [minirag/minirag.py:561-568]()

### Light Mode

Uses `entities_vdb` and `relationships_vdb` for entity-centric retrieval.

```python
response = await hybrid_query(
    query,
    self.chunk_entity_relation_graph,
    self.entities_vdb,      # Entity description search
    self.relationships_vdb, # Relationship search
    self.text_chunks,
    param,
    asdict(self),
)
```

**Sources:** [minirag/minirag.py:538-547]()

### Mini Mode

Utilizes all four vector storage instances for comprehensive topology-enhanced retrieval.

```python
response = await minirag_query(
    query,
    self.chunk_entity_relation_graph,
    self.entities_vdb,      # Entity descriptions
    self.entity_name_vdb,   # Entity name matching
    self.relationships_vdb, # Relationship context
    self.chunks_vdb,        # Text chunks
    self.text_chunks,
    self.embedding_func,
    param,
    asdict(self),
)
```

**Sources:** [minirag/minirag.py:548-560]()

## Vector Storage Lifecycle

### Insertion Phase

During document insertion, embeddings are generated and stored in vector databases:

```mermaid
sequenceDiagram
    participant MiniRAG
    participant extract_entities
    participant entities_vdb
    participant entity_name_vdb
    participant relationships_vdb
    participant chunks_vdb
    
    MiniRAG->>MiniRAG: ainsert(documents)
    MiniRAG->>MiniRAG: chunk documents
    MiniRAG->>chunks_vdb: upsert(chunks)
    Note over chunks_vdb: Store chunk embeddings
    
    MiniRAG->>extract_entities: extract_entities(chunks)
    
    extract_entities->>entities_vdb: upsert(entity_descriptions)
    Note over entities_vdb: Entity description embeddings
    
    extract_entities->>entity_name_vdb: upsert(entity_names)
    Note over entity_name_vdb: Entity name embeddings
    
    extract_entities->>relationships_vdb: upsert(relationships)
    Note over relationships_vdb: Relationship embeddings
    
    MiniRAG->>MiniRAG: _insert_done()
    MiniRAG->>entities_vdb: index_done_callback()
    MiniRAG->>entity_name_vdb: index_done_callback()
    MiniRAG->>relationships_vdb: index_done_callback()
    MiniRAG->>chunks_vdb: index_done_callback()
```

**Sources:** [minirag/minirag.py:344-389](), [minirag/minirag.py:516-531]()

### Query Phase

Vector storage is queried to retrieve relevant context:

```mermaid
sequenceDiagram
    participant Client
    participant MiniRAG
    participant minirag_query
    participant entity_name_vdb
    participant entities_vdb
    participant relationships_vdb
    participant chunks_vdb
    
    Client->>MiniRAG: aquery("What is X?", mode="mini")
    MiniRAG->>minirag_query: Forward query
    
    minirag_query->>entity_name_vdb: query(entities_from_query, top_k)
    entity_name_vdb-->>minirag_query: Matched entity names
    
    minirag_query->>entities_vdb: query(entity_context, top_k)
    entities_vdb-->>minirag_query: Entity descriptions
    
    minirag_query->>relationships_vdb: query(relationship_context, top_k)
    relationships_vdb-->>minirag_query: Relationships
    
    minirag_query->>chunks_vdb: query(fallback_query, top_k)
    chunks_vdb-->>minirag_query: Text chunks
    
    minirag_query-->>MiniRAG: Retrieved context
    MiniRAG->>MiniRAG: _query_done()
    MiniRAG-->>Client: Final response
```

**Sources:** [minirag/minirag.py:537-580]()

### Index Completion

After insertion or query operations, the `index_done_callback()` method is called to commit changes:

```python
async def _insert_done(self):
    tasks = []
    for storage_inst in [
        self.entities_vdb,
        self.entity_name_vdb,
        self.relationships_vdb,
        self.chunks_vdb,
        # ... other storage instances
    ]:
        if storage_inst is None:
            continue
        tasks.append(cast(StorageNameSpace, storage_inst).index_done_callback())
    await asyncio.gather(*tasks)
```

**Sources:** [minirag/minirag.py:516-531](), [minirag/minirag.py:574-580]()

## Embedding Function Integration

Vector storage instances share a common `embedding_func` that is rate-limited and configured during initialization:

```mermaid
graph TB
    subgraph "Embedding Configuration"
        embedding_func["embedding_func: EmbeddingFunc<br/>User-provided or default"]
        
        limit_async["limit_async_func_call<br/>(embedding_func_max_async=16)"]
        
        limited_func["Rate-limited embedding_func"]
    end
    
    subgraph "Vector Storage Instances"
        entities["entities_vdb<br/>embedding_func=limited_func"]
        entity_name["entity_name_vdb<br/>embedding_func=limited_func"]
        relationships["relationships_vdb<br/>embedding_func=limited_func"]
        chunks["chunks_vdb<br/>embedding_func=limited_func"]
    end
    
    embedding_func --> limit_async
    limit_async --> limited_func
    
    limited_func --> entities
    limited_func --> entity_name
    limited_func --> relationships
    limited_func --> chunks
```

The embedding function is wrapped with `limit_async_func_call()` to prevent overwhelming the embedding service:

```python
self.embedding_func = limit_async_func_call(self.embedding_func_max_async)(
    self.embedding_func
)
```

**Sources:** [minirag/minirag.py:247-249](), [minirag/minirag.py:159-161]()

## Custom Vector Storage Backend

To add a new vector storage backend, implement the `BaseVectorStorage` interface:

```python
from minirag.base import BaseVectorStorage
from dataclasses import dataclass

@dataclass
class CustomVectorStorage(BaseVectorStorage):
    # Add custom fields here
    
    async def query(self, query: str, top_k: int) -> list[dict]:
        # 1. Generate embedding from query using self.embedding_func
        # 2. Perform nearest neighbor search
        # 3. Return top_k results with metadata
        pass
    
    async def upsert(self, data: dict[str, dict]):
        # 1. For each item in data:
        #    - Generate embedding from data[id]["content"] using self.embedding_func
        #    - Store embedding with id and meta_fields
        pass
```

Then register it in the `STORAGES` dictionary in [minirag/minirag.py:39-66]():

```python
STORAGES = {
    # ... existing entries
    "CustomVectorStorage": ".kg.custom_impl",
}
```

**Sources:** [minirag/base.py:62-75](), [minirag/minirag.py:39-66](), [minirag/minirag.py:315-318]()

## Best Practices

### Choosing a Backend

| Scenario | Recommended Backend | Rationale |
|----------|-------------------|-----------|
| Development/Testing | `NanoVectorDBStorage` | Lightweight, no setup required |
| Small datasets (<100K) | `NanoVectorDBStorage` or `ChromaVectorDBStorage` | Simple, efficient for small scale |
| Medium datasets (100K-1M) | `ChromaVectorDBStorage` or `Weaviate` | Good balance of features and performance |
| Large datasets (>1M) | `MilvusVectorDBStorge` or `TiDBVectorDBStorage` | Horizontal scaling, production-ready |
| Enterprise with PostgreSQL | `PGVectorStorage` | Leverage existing infrastructure |
| Enterprise with Oracle | `OracleVectorDBStorage` | Enterprise features, high availability |

### Meta Fields Configuration

Vector storage instances use `meta_fields` to store additional metadata alongside embeddings:

- `entities_vdb`: `meta_fields={"entity_name"}` - Stores entity name for filtering
- `entity_name_vdb`: `meta_fields={"entity_name"}` - Enables entity name lookup
- `relationships_vdb`: `meta_fields={"src_id", "tgt_id"}` - Tracks relationship endpoints
- `chunks_vdb`: `meta_fields={}` - No additional metadata needed

**Sources:** [minirag/minirag.py:273-298]()

### Performance Tuning

Adjust embedding batch size and concurrency limits based on your infrastructure:

```python
rag = MiniRAG(
    embedding_batch_num=64,        # Increase for better throughput
    embedding_func_max_async=32,   # Increase if embedding service can handle it
    vector_db_storage_cls_kwargs={
        # Backend-specific tuning parameters
    }
)
```

**Sources:** [minirag/minirag.py:160-173]()

---

# Page: Key-Value Storage Backends

# Key-Value Storage Backends

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [minirag/__init__.py](minirag/__init__.py)
- [minirag/base.py](minirag/base.py)
- [minirag/kg/weaviate_impl.py](minirag/kg/weaviate_impl.py)
- [minirag/minirag.py](minirag/minirag.py)
- [tests/test_weaviate.py](tests/test_weaviate.py)

</details>



This document describes the Key-Value (KV) Storage backends in MiniRAG, which provide mechanisms for storing and retrieving data by unique identifiers. MiniRAG uses KV storage for three primary purposes: storing full document content (`full_docs`), storing text chunks (`text_chunks`), and caching LLM responses (`llm_response_cache`). Multiple backend implementations are available, including JSON files, Redis, MongoDB, and others.

For information about Vector Storage which handles embeddings, see page 5.2. For Graph Storage which manages the heterogeneous graph relationships, see page 5.1.

## 1. Role in the System Architecture

Key-Value Storage is one of the core storage components in MiniRAG. The system uses three separate KV storage instances for different purposes:

- **`full_docs`**: Stores complete document content indexed by document ID
- **`text_chunks`**: Stores chunked text segments with metadata (chunk order, token count, parent document reference)
- **`llm_response_cache`**: Caches LLM API responses to reduce redundant calls (when `enable_llm_cache=True`)

KV Storage Instances in MiniRAG Core

```mermaid
graph TB
    subgraph "MiniRAG Core Initialization"
        MiniRAG["MiniRAG.__post_init__()"]
    end
    
    subgraph "Three KV Storage Instances"
        FullDocs["self.full_docs\nnamespace='full_docs'\nStores complete documents"]
        TextChunks["self.text_chunks\nnamespace='text_chunks'\nStores text chunks"]
        LLMCache["self.llm_response_cache\nnamespace='llm_response_cache'\nCaches LLM responses"]
    end
    
    subgraph "Configurable Backend"
        KVStorageCls["self.key_string_value_json_storage_cls\nConfigured via kv_storage parameter"]
    end
    
    MiniRAG -->|"Creates instances"| FullDocs
    MiniRAG -->|"Creates instances"| TextChunks
    MiniRAG -->|"Creates instances"| LLMCache
    
    KVStorageCls -->|"Instantiates"| FullDocs
    KVStorageCls -->|"Instantiates"| TextChunks
    KVStorageCls -->|"Instantiates"| LLMCache
```

Sources: [minirag/minirag.py:254-263](), [minirag/minirag.py:237-245]()

## 2. Available KV Storage Backends

MiniRAG supports multiple KV storage backends, configured via the `kv_storage` parameter:

| Backend | Class Name | Use Case | Storage Location |
|---------|-----------|----------|------------------|
| **JSON Files** | `JsonKVStorage` | Default, local development | Local filesystem |
| **Redis** | `RedisKVStorage` | High-performance caching | Redis server |
| **MongoDB** | `MongoKVStorage` | Document-oriented storage | MongoDB database |
| **Oracle** | `OracleKVStorage` | Enterprise deployments | Oracle Database |
| **PostgreSQL** | `PGKVStorage` | Relational database storage | PostgreSQL |
| **TiDB** | `TiDBKVStorage` | Distributed MySQL-compatible | TiDB cluster |
| **Weaviate** | `WeaviateKVStorage` | Vector database with KV | Weaviate instance |

Sources: [minirag/minirag.py:39-66](), [minirag/minirag.py:130]()

## 3. BaseKVStorage Interface

The `BaseKVStorage` class defined in [minirag/base.py:77-101]() is a generic abstract class that provides the core interface all KV storage backends must implement.

Class Hierarchy

```mermaid
classDiagram
    class StorageNameSpace {
        +namespace: str
        +global_config: dict
        +index_done_callback()
        +query_done_callback()
    }
    
    class BaseKVStorage~T~ {
        +embedding_func: EmbeddingFunc
        +all_keys() list[str]
        +get_by_id(id) T|None
        +get_by_ids(ids, fields) list[T|None]
        +filter_keys(data) set[str]
        +upsert(data) dict[str, T]
        +drop()
    }
    
    class JsonKVStorage {
        +_file_name: str
        +_data: dict
        +_lock: asyncio.Lock
    }
    
    class RedisKVStorage {
        +redis_client
    }
    
    class MongoKVStorage {
        +mongo_client
        +collection
    }
    
    class WeaviateKVStorage {
        +client: weaviate.Client
    }
    
    StorageNameSpace <|-- BaseKVStorage
    BaseKVStorage <|-- JsonKVStorage
    BaseKVStorage <|-- RedisKVStorage
    BaseKVStorage <|-- MongoKVStorage
    BaseKVStorage <|-- WeaviateKVStorage
```

Sources: [minirag/base.py:48-60](), [minirag/base.py:77-101]()

### 3.1 Required Methods

All KV storage backend implementations must provide these methods:

| Method | Signature | Purpose |
|--------|-----------|---------|
| `all_keys()` | `async all_keys() -> list[str]` | Returns all keys in the storage |
| `get_by_id(id)` | `async get_by_id(id: str) -> Union[T, None]` | Retrieves a single value by its ID |
| `get_by_ids(ids, fields)` | `async get_by_ids(ids: list[str], fields: Union[set[str], None]) -> list[Union[T, None]]` | Retrieves multiple values with optional field filtering |
| `filter_keys(data)` | `async filter_keys(data: list[str]) -> set[str]` | Returns keys from input list that don't exist in storage (for deduplication) |
| `upsert(data)` | `async upsert(data: dict[str, T])` | Updates or inserts key-value pairs |
| `drop()` | `async drop()` | Clears the storage |

Sources: [minirag/base.py:77-101]()

### 3.2 Generic Type Parameter

`BaseKVStorage` is generic over type `T`, allowing type-safe storage of different data structures:

- For `full_docs` and `text_chunks`: Stores dictionaries with content and metadata
- For `llm_response_cache`: Stores LLM response strings or objects

Sources: [minirag/base.py:14](), [minirag/base.py:78]()

## 4. Text Chunk Storage

Text chunks are a central concept in MiniRAG's retrieval system. After documents are split into chunks, they are stored in the `text_chunks` KV storage instance.

Text Chunk Data Flow

```mermaid
graph LR
    subgraph "Document Processing"
        RawDoc["Raw Document"] --> ChunkingFunc["chunking_by_token_size()"]
        ChunkingFunc --> Chunks["Text Chunks"]
    end
    
    subgraph "Storage"
        Chunks -->|"upsert()"| TextChunksKV["self.text_chunks\nJsonKVStorage\nnamespace='text_chunks'"]
        Chunks -->|"upsert()"| ChunksVDB["self.chunks_vdb\nNanoVectorDBStorage\nnamespace='chunks'"]
    end
    
    subgraph "Retrieval"
        Query["User Query"] --> VectorSearch["Vector Search"]
        VectorSearch --> ChunksVDB
        ChunksVDB -->|"Returns chunk IDs"| ChunkIDs["Chunk IDs"]
        ChunkIDs -->|"get_by_ids()"| TextChunksKV
        TextChunksKV -->|"Returns full content"| Context["Context for LLM"]
    end
```

Sources: [minirag/minirag.py:259-263](), [minirag/minirag.py:484-500]()

### 4.1 TextChunkSchema

Each text chunk stored in KV storage follows the `TextChunkSchema` structure:

| Field | Type | Description |
|-------|------|-------------|
| `content` | `str` | The actual text content of the chunk |
| `tokens` | `int` | Number of tokens in the chunk |
| `full_doc_id` | `str` | Reference to the parent document ID |
| `chunk_order_index` | `int` | Position of this chunk in the original document |

Sources: [minirag/base.py:9-12]()

### 4.2 Chunk ID Generation

Chunk IDs are generated using MD5 hashing of the content with a `"chunk-"` prefix:

```python
compute_mdhash_id(chunk_content, prefix="chunk-")
```

This ensures deterministic IDs and automatic deduplication of identical chunks.

Sources: [minirag/minirag.py:485]()

## 5. JsonKVStorage Implementation

`JsonKVStorage` is the default KV storage backend, storing data in JSON files on the local filesystem.

JsonKVStorage Architecture

```mermaid
graph TB
    subgraph "Initialization"
        Init["__post_init__()"] --> SetFilename["_file_name = working_dir/kv_store_{namespace}.json"]
        SetFilename --> LoadData["_data = load_json(_file_name)"]
        LoadData --> CreateLock["_lock = asyncio.Lock()"]
    end
    
    subgraph "In-Memory Operations"
        Upsert["upsert(data)"] -->|"async with _lock"| UpdateDict["Update _data dict"]
        GetByID["get_by_id(id)"] --> ReadDict["Read from _data"]
        AllKeys["all_keys()"] --> ReadDict
    end
    
    subgraph "Persistence"
        IndexDone["index_done_callback()"] -->|"async with _lock"| WriteFile["Write _data to JSON file"]
    end
    
    UpdateDict -.->|"Not persisted until callback"| WriteFile
```

Sources: [minirag/kg/json_kv_impl.py:66-135]()

### 5.1 Key Characteristics

- **File-based persistence**: Each namespace gets its own JSON file
- **In-memory operations**: All operations work on an in-memory dictionary
- **Async lock protection**: Uses `asyncio.Lock` for concurrent access safety
- **Explicit persistence**: Data is written to disk only on `index_done_callback()`
- **Lazy loading**: Loads existing data from file during initialization

### 5.2 File Naming Convention

Files are named using the pattern:
```
{working_dir}/kv_store_{namespace}.json
```

For example:
- `kv_store_full_docs.json`
- `kv_store_text_chunks.json`
- `kv_store_llm_response_cache.json`

Sources: [minirag/kg/json_kv_impl.py:66-135]()

## 6. Document Status Storage

The `DocStatusStorage` class extends `BaseKVStorage` to provide specialized functionality for tracking document processing status.

### 6.1 Document Status Tracking

`DocStatusStorage` defines the following additional methods to manage document status:

| Method | Description | Definition |
|--------|-------------|------------|
| `get_status_counts()` | Get counts of documents in each status | [base.py:187-189]() |
| `get_failed_docs()` | Retrieve all failed documents | [base.py:191-193]() |
| `get_pending_docs()` | Retrieve all pending documents | [base.py:195-197]() |

Sources: [minirag/base.py:151-197]()

### 6.2 Document Status Enum

Documents can be in one of the following states:

```mermaid
graph LR
    PENDING["PENDING"] --> PROCESSING["PROCESSING"]
    PROCESSING --> PROCESSED["PROCESSED"]
    PROCESSING --> FAILED["FAILED"]
```

Sources: [minirag/base.py:151-158]()

## 7. Extending with Custom KV Storage

MiniRAG's modular architecture allows for custom Key-Value Storage implementations. To create a custom implementation:

1. Extend the `BaseKVStorage` class
2. Implement all required methods 
3. Configure MiniRAG to use your implementation

By implementing this interface, you can create KV storage solutions that use different backends, such as Redis, MongoDB, or other databases.

Sources: [minirag/base.py:77-100](), [minirag/kg/json_kv_impl.py:66-135]()

---

# Page: Document Status Tracking

# Document Status Tracking

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [minirag/__init__.py](minirag/__init__.py)
- [minirag/base.py](minirag/base.py)
- [minirag/kg/jsondocstatus_impl.py](minirag/kg/jsondocstatus_impl.py)

</details>



## Purpose and Scope

Document Status Tracking is a system within MiniRAG that manages the lifecycle of documents as they are ingested, processed, and indexed into the knowledge graph. This system tracks which documents have been successfully processed, which are pending, which are currently being processed, and which have failed, enabling incremental updates, error recovery, and processing resumption.

This page documents the `DocStatus` enum, `DocProcessingStatus` dataclass, and the `DocStatusStorage` interface and implementations. For information about how documents are actually processed and indexed, see [Data Processing Pipeline](#3.3). For other storage backends, see [Key-Value Storage Backends](#5.3).

**Sources:** [minirag/base.py:151-197](), [minirag/kg/jsondocstatus_impl.py:1-148]()

---

## Document Lifecycle Overview

MiniRAG tracks documents through four distinct states during their processing lifecycle. Understanding these states is essential for managing document ingestion and handling processing failures.

### Document Status State Machine

```mermaid
stateDiagram-v2
    [*] --> PENDING: "Document added"
    PENDING --> PROCESSING: "Processing starts"
    PROCESSING --> PROCESSED: "Successfully indexed"
    PROCESSING --> FAILED: "Error occurred"
    FAILED --> PROCESSING: "Retry processing"
    PROCESSED --> [*]: "Complete"
```

### Status Definitions

| Status | Value | Description | Next States |
|--------|-------|-------------|-------------|
| `PENDING` | `"pending"` | Document is queued for processing but not yet started | `PROCESSING` |
| `PROCESSING` | `"processing"` | Document is currently being chunked and entities are being extracted | `PROCESSED`, `FAILED` |
| `PROCESSED` | `"processed"` | Document has been successfully indexed into all storage backends | Terminal state |
| `FAILED` | `"failed"` | Document processing encountered an error | `PROCESSING` (on retry) |

**Sources:** [minirag/base.py:151-157]()

---

## Core Data Structures

### DocStatus Enum

The `DocStatus` enum defines the four possible states a document can be in during processing.

```python
class DocStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
```

This enum extends both `str` and `Enum`, allowing status values to be used as strings while maintaining type safety.

**Sources:** [minirag/base.py:151-157]()

### DocProcessingStatus Dataclass

The `DocProcessingStatus` dataclass captures comprehensive metadata about a document's processing state.

```mermaid
classDiagram
    class DocProcessingStatus {
        +str content
        +str content_summary
        +int content_length
        +DocStatus status
        +str created_at
        +str updated_at
        +Optional~int~ chunks_count
        +Optional~str~ error
        +dict metadata
    }
    
    DocStatus ..> DocProcessingStatus : "used by"
```

#### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content` | `str` | Yes | Full original content of the document |
| `content_summary` | `str` | Yes | First 100 characters for preview purposes |
| `content_length` | `int` | Yes | Total character count of the document |
| `status` | `DocStatus` | Yes | Current processing status |
| `created_at` | `str` | Yes | ISO 8601 timestamp when document was first added |
| `updated_at` | `str` | Yes | ISO 8601 timestamp of last status change |
| `chunks_count` | `Optional[int]` | No | Number of chunks created during splitting |
| `error` | `Optional[str]` | No | Error message if `status` is `FAILED` |
| `metadata` | `dict[str, Any]` | No | Additional custom metadata |

**Sources:** [minirag/base.py:160-181]()

---

## Storage Interface

### DocStatusStorage Base Class

The `DocStatusStorage` abstract class extends `BaseKVStorage` and defines the interface for storing and querying document status information.

```mermaid
classDiagram
    class BaseKVStorage~T~ {
        <<abstract>>
        +str namespace
        +dict global_config
        +EmbeddingFunc embedding_func
        +all_keys() list~str~
        +get_by_id(id) T
        +filter_keys(data) set~str~
        +upsert(data) 
        +drop()
    }
    
    class DocStatusStorage {
        <<abstract>>
        +get_status_counts() dict~str,int~
        +get_failed_docs() dict~str,DocProcessingStatus~
        +get_pending_docs() dict~str,DocProcessingStatus~
    }
    
    class JsonDocStatusStorage {
        -str _file_name
        -dict _data
        +filter_keys(data) set~str~
        +get_status_counts() dict~str,int~
        +get_docs_by_status(status) dict
        +get_failed_docs() dict
        +get_pending_docs() dict
        +upsert(data)
        +get_by_id(id)
        +get(doc_id)
        +delete(doc_ids)
        +index_done_callback()
    }
    
    BaseKVStorage <|-- DocStatusStorage
    DocStatusStorage <|-- JsonDocStatusStorage
```

### Core Methods

#### Status Querying Methods

| Method | Return Type | Description |
|--------|-------------|-------------|
| `get_status_counts()` | `dict[str, int]` | Returns count of documents in each status state |
| `get_failed_docs()` | `dict[str, DocProcessingStatus]` | Retrieves all documents with `FAILED` status |
| `get_pending_docs()` | `dict[str, DocProcessingStatus]` | Retrieves all documents with `PENDING` status |

These methods are defined in the base class but must be implemented by concrete storage backends.

**Sources:** [minirag/base.py:184-197]()

---

## JSON Implementation: JsonDocStatusStorage

The `JsonDocStatusStorage` class provides a file-based implementation of document status tracking using JSON serialization.

### Initialization and File Structure

```mermaid
sequenceDiagram
    participant Client
    participant JsonDocStatusStorage
    participant FileSystem
    
    Client->>JsonDocStatusStorage: "__post_init__()"
    JsonDocStatusStorage->>JsonDocStatusStorage: "Construct file path"
    Note over JsonDocStatusStorage: "working_dir/kv_store_{namespace}.json"
    JsonDocStatusStorage->>FileSystem: "load_json(file_path)"
    FileSystem-->>JsonDocStatusStorage: "Existing data or {}"
    JsonDocStatusStorage->>JsonDocStatusStorage: "Store in self._data"
    JsonDocStatusStorage-->>Client: "Ready"
```

The storage file is located at `{working_dir}/kv_store_{namespace}.json` where:
- `working_dir` is from `global_config["working_dir"]`
- `namespace` is the storage namespace identifier

**Sources:** [minirag/kg/jsondocstatus_impl.py:72-76]()

### Key Methods

#### filter_keys(data: list[str]) -> set[str]

Returns the set of document IDs that need processing. A document needs processing if:
1. It doesn't exist in storage, OR
2. Its status is not `PROCESSED`

```python
async def filter_keys(self, data: list[str]) -> set[str]:
    return set([
        k for k in data
        if k not in self._data or self._data[k]["status"] != DocStatus.PROCESSED
    ])
```

This method is critical for incremental indexing, allowing MiniRAG to skip already-processed documents.

**Sources:** [minirag/kg/jsondocstatus_impl.py:78-86]()

#### get_status_counts() -> Dict[str, int]

Aggregates counts of documents in each status state.

**Sources:** [minirag/kg/jsondocstatus_impl.py:88-93]()

#### get_docs_by_status(status: DocStatus) -> dict[str, DocProcessingStatus]

Retrieves all documents matching a specific status. Handles a special case where `content` field might be missing but `content_summary` is present:

```python
if "content" not in data and "content_summary" in data:
    data["content"] = data["content_summary"]
```

This fallback ensures backward compatibility if the storage schema evolves.

**Sources:** [minirag/kg/jsondocstatus_impl.py:95-112]()

#### upsert(data: dict[str, dict])

Updates or inserts document status records. After updating the in-memory `_data` dictionary, it immediately persists to disk by calling `index_done_callback()`.

**Sources:** [minirag/kg/jsondocstatus_impl.py:126-134]()

#### index_done_callback()

Persists the in-memory `_data` dictionary to the JSON file. This method is called after indexing operations complete to ensure durability.

**Sources:** [minirag/kg/jsondocstatus_impl.py:122-124]()

#### delete(doc_ids: list[str])

Removes document status records by their IDs and persists changes to disk.

**Sources:** [minirag/kg/jsondocstatus_impl.py:143-147]()

### Data Structure Example

The JSON file stores a dictionary mapping document IDs to status objects:

```json
{
  "doc_123": {
    "content": "Full document text...",
    "content_summary": "Full document text...",
    "content_length": 1500,
    "status": "processed",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:35:00Z",
    "chunks_count": 3,
    "metadata": {}
  },
  "doc_456": {
    "content": "Another document...",
    "content_summary": "Another document...",
    "content_length": 800,
    "status": "failed",
    "created_at": "2024-01-15T11:00:00Z",
    "updated_at": "2024-01-15T11:02:00Z",
    "error": "Entity extraction timeout",
    "metadata": {}
  }
}
```

**Sources:** [minirag/kg/jsondocstatus_impl.py:68-148]()

---

## Integration with MiniRAG Core

### Document Status Tracking in the Indexing Pipeline

```mermaid
sequenceDiagram
    participant MiniRAG
    participant DocStatusStorage
    participant Processing
    participant Storage
    
    MiniRAG->>DocStatusStorage: "filter_keys(doc_ids)"
    DocStatusStorage-->>MiniRAG: "Unprocessed doc IDs"
    
    loop "For each unprocessed document"
        MiniRAG->>DocStatusStorage: "upsert({doc_id: status=PROCESSING})"
        MiniRAG->>Processing: "Chunk and extract entities"
        
        alt "Success"
            Processing->>Storage: "Store in graph/vector/KV"
            MiniRAG->>DocStatusStorage: "upsert({doc_id: status=PROCESSED})"
        else "Failure"
            MiniRAG->>DocStatusStorage: "upsert({doc_id: status=FAILED, error=...})"
        end
    end
    
    MiniRAG->>DocStatusStorage: "index_done_callback()"
```

### Usage Pattern: Incremental Updates

When documents are added to MiniRAG, the system:

1. **Checks existing status** via `filter_keys()` to determine which documents need processing
2. **Marks as processing** by setting status to `PROCESSING`
3. **Processes the document** through chunking and entity extraction
4. **Updates final status** to either `PROCESSED` or `FAILED`
5. **Persists state** via `index_done_callback()`

This design enables:
- **Crash recovery**: Resume processing after interruption
- **Incremental indexing**: Skip already-processed documents
- **Error tracking**: Identify and retry failed documents
- **Progress monitoring**: Query status counts to track processing progress

**Sources:** [minirag/kg/jsondocstatus_impl.py:78-86](), [minirag/base.py:184-197]()

---

## Extensibility

### Implementing Custom Status Storage

To implement a custom document status storage backend (e.g., using Redis, MongoDB, or a SQL database), create a class that extends `DocStatusStorage`:

```python
from minirag.base import DocStatusStorage, DocStatus, DocProcessingStatus
from dataclasses import dataclass

@dataclass
class CustomDocStatusStorage(DocStatusStorage):
    def __post_init__(self):
        # Initialize connection to your storage backend
        pass
    
    async def filter_keys(self, data: list[str]) -> set[str]:
        # Query backend for unprocessed documents
        pass
    
    async def get_status_counts(self) -> dict[str, int]:
        # Aggregate counts from backend
        pass
    
    async def get_docs_by_status(self, status: DocStatus) -> dict:
        # Query documents by status
        pass
    
    async def upsert(self, data: dict[str, dict]):
        # Update/insert records in backend
        pass
```

The key requirement is implementing `filter_keys()` correctly to enable incremental processing.

**Sources:** [minirag/base.py:184-197]()

---

## Summary

The Document Status Tracking system provides robust lifecycle management for documents in MiniRAG through:

| Component | Purpose |
|-----------|---------|
| `DocStatus` enum | Defines four processing states (pending, processing, processed, failed) |
| `DocProcessingStatus` dataclass | Captures comprehensive document metadata including content, timestamps, and errors |
| `DocStatusStorage` interface | Abstract base class defining status querying and management operations |
| `JsonDocStatusStorage` implementation | File-based JSON storage for document status, suitable for local deployments |

This system enables incremental indexing, crash recovery, error tracking, and processing resumption, making MiniRAG robust for production deployments where document ingestion may be interrupted or fail.

**Sources:** [minirag/base.py:151-197](), [minirag/kg/jsondocstatus_impl.py:1-148]()

---

# Page: LLM and Embedding Integration

# LLM and Embedding Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [minirag/llm/openai.py](minirag/llm/openai.py)

</details>



This document describes how MiniRAG integrates with Large Language Models (LLMs) and embedding models to power both the indexing and query phases of the RAG pipeline. It covers the abstraction interfaces, provider implementations, and integration points within the system architecture.

For detailed information about specific aspects of LLM integration:
- LLM interface implementations and provider-specific functions: see [LLM Interface](#6.1)
- Embedding function wrappers and generation: see [Embedding Functions](#6.2)  
- Supported model list and performance characteristics: see [Supported Models](#6.3)

## Purpose and Scope

MiniRAG's LLM and embedding integration layer provides:

1. **Unified async interfaces** for multiple LLM providers (OpenAI, HuggingFace, NVIDIA, OpenRouter)
2. **Embedding function abstraction** with dimension and token size metadata
3. **Retry and error handling** logic for robust API interactions
4. **Streaming and batch support** for different usage patterns

This layer decouples the core RAG logic from specific LLM implementations, enabling flexible model selection based on deployment constraints (cloud APIs, on-device models, or hybrid approaches).

---

## System Integration Architecture

The following diagram shows how LLM and embedding components integrate with the broader MiniRAG system:

**Diagram 1: LLM and Embedding Integration in MiniRAG Architecture**

```mermaid
graph TB
    subgraph "MiniRAG Core"
        MiniRAG["MiniRAG Class<br/>(minirag.py)"]
        Operate["RAG Operations<br/>(operate.py)"]
    end
    
    subgraph "LLM Integration Layer"
        LLMFunc["async LLM Functions"]
        
        subgraph "Provider Implementations"
            OpenAIComplete["openai_complete()"]
            GPT4o["gpt_4o_mini_complete()"]
            NvidiaComplete["nvidia_openai_complete()"]
            OpenRouterComplete["openrouter_openai_complete()"]
            HFComplete["hf_model_complete()"]
        end
        
        LLMFunc --> OpenAIComplete
        LLMFunc --> GPT4o
        LLMFunc --> NvidiaComplete
        LLMFunc --> OpenRouterComplete
        LLMFunc --> HFComplete
    end
    
    subgraph "Embedding Integration Layer"
        EmbedFunc["Embedding Functions"]
        
        subgraph "Embedding Implementations"
            OpenAIEmbed["openai_embed()<br/>text-embedding-3-small"]
            HFEmbed["HuggingFace Embeddings<br/>sentence-transformers"]
        end
        
        EmbedFunc --> OpenAIEmbed
        EmbedFunc --> HFEmbed
        
        Wrapper["@wrap_embedding_func_with_attrs<br/>embedding_dim, max_token_size"]
        Wrapper -.decorates.-> OpenAIEmbed
        Wrapper -.decorates.-> HFEmbed
    end
    
    subgraph "Storage Layer"
        VectorDB["Vector Storage<br/>entity_vdb, chunks_vdb"]
        GraphDB["Graph Storage<br/>entities, relationships"]
        KVDB["KV Storage<br/>text chunks"]
    end
    
    MiniRAG --> Operate
    Operate --> LLMFunc
    Operate --> EmbedFunc
    
    EmbedFunc --> VectorDB
    LLMFunc -.extracts entities.-> GraphDB
    LLMFunc -.generates text.-> KVDB
    
    style MiniRAG fill:#f9f9f9
    style LLMFunc fill:#f9f9f9
    style EmbedFunc fill:#f9f9f9
    style Wrapper fill:#e8e8e8
```

Sources: [minirag/llm/openai.py:1-267](), [README.md:36-42]()

---

## Two-Phase LLM Usage Pattern

MiniRAG uses LLMs and embeddings in distinct ways during the indexing and query phases:

**Diagram 2: LLM Calls in Indexing and Query Phases**

```mermaid
sequenceDiagram
    participant Docs as "Input Documents"
    participant MiniRAG as "MiniRAG.insert()"
    participant Operate as "operate.py"
    participant LLM as "LLM Functions"
    participant Embed as "Embedding Functions"
    participant Storage as "Storage Layer"
    
    rect rgb(245, 245, 245)
        Note over Docs,Storage: Phase 1: Indexing
        Docs->>MiniRAG: Raw text documents
        MiniRAG->>MiniRAG: Chunk into segments
        MiniRAG->>Operate: extract_entities(chunks)
        Operate->>LLM: Call with entity extraction prompt
        Note over LLM: openai_complete()<br/>gpt_4o_mini_complete()<br/>hf_model_complete()
        LLM-->>Operate: JSON with entities & relationships
        Operate->>Embed: Generate embeddings for entities
        Note over Embed: openai_embed()<br/>with text-embedding-3-small
        Embed-->>Operate: Embedding vectors
        Operate->>Embed: Generate embeddings for chunks
        Embed-->>Operate: Chunk embedding vectors
        Operate->>Storage: Store entities in graph_storage
        Operate->>Storage: Store embeddings in vector_storage
        Operate->>Storage: Store text in kv_storage
    end
    
    rect rgb(250, 250, 250)
        Note over Docs,Storage: Phase 2: Query
        Docs->>MiniRAG: User query string
        MiniRAG->>Operate: minirag_query(query)
        Operate->>LLM: Extract entities from query
        LLM-->>Operate: Query entities
        Operate->>Embed: Generate query embedding
        Embed-->>Operate: Query vector
        Operate->>Storage: Retrieve via graph + vector search
        Storage-->>Operate: Relevant chunks & entities
        Operate->>LLM: Generate answer with context
        Note over LLM: Stream or batch response
        LLM-->>Operate: Final answer text
        Operate-->>MiniRAG: Formatted response
    end
```

Sources: [minirag/llm/openai.py:93-169](), [README.md:36-42]()

---

## LLM Interface Design Pattern

All LLM integrations follow a consistent async interface pattern that provides:

| Feature | Implementation | Purpose |
|---------|---------------|---------|
| **Async Execution** | `async def` functions | Non-blocking I/O for API calls |
| **Retry Logic** | `@retry` decorator with exponential backoff | Handle rate limits and transient failures |
| **Streaming Support** | `AsyncIterator[str]` return type | Enable real-time response generation |
| **Message History** | `history_messages` parameter | Support conversational context |
| **System Prompts** | `system_prompt` parameter | Configure model behavior |
| **Provider Abstraction** | Unified function signature | Swap providers without code changes |

**Function Signature Pattern:**

```python
async def {provider}_complete(
    prompt: str,
    system_prompt: str = None,
    history_messages: List[Dict] = [],
    keyword_extraction: bool = False,
    **kwargs
) -> Union[str, AsyncIterator[str]]
```

Sources: [minirag/llm/openai.py:156-169](), [minirag/llm/openai.py:93-154]()

---

## LLM Provider Implementations

**Diagram 3: LLM Provider Architecture**

```mermaid
graph TB
    subgraph "Core Interface Pattern"
        BaseSignature["async complete()<br/>prompt, system_prompt, history_messages"]
    end
    
    subgraph "OpenAI-Compatible Providers"
        OpenAIImpl["openai_complete_if_cache()<br/>minirag/llm/openai.py:93-154"]
        
        OpenAIAPI["OpenAI API<br/>AsyncOpenAI client<br/>base_url: api.openai.com"]
        GPT4oMini["gpt_4o_mini_complete()<br/>model: gpt-4o-mini<br/>lines 187-199"]
        GPT4o["gpt_4o_complete()<br/>model: gpt-4o<br/>lines 172-184"]
        
        NvidiaAPI["NVIDIA API<br/>base_url: integrate.api.nvidia.com<br/>lines 202-216"]
        OpenRouterAPI["OpenRouter API<br/>base_url: openrouter.ai<br/>lines 218-241"]
        
        OpenAIImpl --> OpenAIAPI
        OpenAIImpl --> GPT4oMini
        OpenAIImpl --> GPT4o
        OpenAIImpl --> NvidiaAPI
        OpenAIImpl --> OpenRouterAPI
    end
    
    subgraph "HuggingFace Provider"
        HFImpl["hf_model_complete()<br/>Local or API models"]
        
        HFModels["Phi-3.5-mini-instruct<br/>GLM-Edge-1.5B-Chat<br/>Qwen2.5-3B-Instruct<br/>MiniCPM3-4B"]
        
        HFImpl --> HFModels
    end
    
    subgraph "Retry & Error Handling"
        RetryDec["@retry decorator<br/>tenacity library"]
        Exceptions["RateLimitError<br/>APIConnectionError<br/>APITimeoutError"]
        Backoff["Exponential backoff<br/>min=4s, max=60s<br/>max 3 attempts"]
        
        RetryDec --> Exceptions
        RetryDec --> Backoff
    end
    
    BaseSignature -.implements.-> OpenAIImpl
    BaseSignature -.implements.-> HFImpl
    
    RetryDec -.protects.-> OpenAIImpl
    RetryDec -.protects.-> HFImpl
    
    style BaseSignature fill:#f9f9f9
    style RetryDec fill:#f9f9f9
```

Sources: [minirag/llm/openai.py:81-241](), [README.md:74-89]()

---

## Embedding Function Architecture

The embedding integration uses a decorator pattern to attach metadata to embedding functions:

**Diagram 4: Embedding Function Wrapper Pattern**

```mermaid
graph LR
    subgraph "Decorator Pattern"
        WrapperFunc["@wrap_embedding_func_with_attrs<br/>minirag/utils.py"]
        
        Attrs["Function Attributes:<br/>embedding_dim=1536<br/>max_token_size=8192"]
        
        WrapperFunc --> Attrs
    end
    
    subgraph "Embedding Implementation"
        OpenAIEmbedFunc["openai_embed()<br/>minirag/llm/openai.py:243-267"]
        
        RetryLogic["@retry<br/>3 attempts<br/>4-60s backoff"]
        
        AsyncClient["AsyncOpenAI.embeddings.create()<br/>model: text-embedding-3-small"]
        
        NumpyArray["Returns: np.ndarray<br/>shape: (n_texts, 1536)"]
        
        RetryLogic --> OpenAIEmbedFunc
        OpenAIEmbedFunc --> AsyncClient
        AsyncClient --> NumpyArray
    end
    
    subgraph "Usage in MiniRAG"
        VectorStores["Vector Storage:<br/>entity_vdb<br/>entity_name_vdb<br/>relationships_vdb<br/>chunks_vdb"]
        
        Quantization["Optional Quantization:<br/>Reduce storage size"]
        
        NumpyArray --> VectorStores
        NumpyArray --> Quantization
    end
    
    WrapperFunc -.decorates.-> OpenAIEmbedFunc
    Attrs -.metadata for.-> VectorStores
    
    style WrapperFunc fill:#f9f9f9
    style OpenAIEmbedFunc fill:#f9f9f9
```

Sources: [minirag/llm/openai.py:243-267](), [minirag/llm/openai.py:69-74]()

---

## Configuration and API Keys

LLM and embedding functions access credentials through environment variables:

| Environment Variable | Purpose | Used By |
|---------------------|---------|---------|
| `OPENAI_API_KEY` | OpenAI authentication | `openai_complete()`, `openai_embed()` |
| `OPENAI_API_BASE` | Custom OpenAI endpoint | `openai_complete_if_cache()` |
| `OPENROUTER_API_KEY` | OpenRouter authentication | `openrouter_openai_complete()` |

**Configuration Flow:**

```mermaid
graph LR
    subgraph "Configuration Sources"
        EnvVars["Environment Variables"]
        FuncArgs["Function Arguments<br/>api_key, base_url"]
    end
    
    subgraph "Priority Logic"
        ArgCheck["Check function args"]
        EnvCheck["Check os.environ"]
        SetEnv["os.environ[KEY] = value"]
    end
    
    subgraph "Client Initialization"
        AsyncClient["AsyncOpenAI()<br/>or<br/>AsyncOpenAI(base_url=...)"]
    end
    
    FuncArgs --> ArgCheck
    ArgCheck -->|if provided| SetEnv
    ArgCheck -->|if not provided| EnvCheck
    EnvVars --> EnvCheck
    
    SetEnv --> AsyncClient
    EnvCheck --> AsyncClient
    
    style ArgCheck fill:#f9f9f9
```

Sources: [minirag/llm/openai.py:102-108](), [minirag/llm/openai.py:226-227](), [minirag/llm/openai.py:257-258]()

---

## Streaming Response Support

LLM functions can return either complete strings or async iterators for streaming:

**Return Type Handling:**

```python
# From minirag/llm/openai.py:131-153
if hasattr(response, "__aiter__"):
    # Streaming response
    async def inner():
        async for chunk in response:
            content = chunk.choices[0].delta.content
            if content is None:
                continue
            if r"\u" in content:
                content = safe_unicode_decode(content.encode("utf-8"))
            yield content
    return inner()  # Returns AsyncIterator[str]
else:
    # Complete response
    content = response.choices[0].message.content
    if r"\u" in content:
        content = safe_unicode_decode(content.encode("utf-8"))
    return content  # Returns str
```

This dual-mode support enables:
- **Batch processing** during indexing for efficiency
- **Real-time streaming** during query for user experience
- **Flexible integration** with different downstream consumers

Sources: [minirag/llm/openai.py:131-153]()

---

## Error Handling and Resilience

The LLM integration layer implements comprehensive error handling:

**Error Handling Strategy:**

| Error Type | Handling | Configuration |
|------------|----------|---------------|
| `RateLimitError` | Exponential backoff retry | Wait 4-60s, max 3 attempts |
| `APIConnectionError` | Automatic retry | Same backoff strategy |
| `APITimeoutError` | Automatic retry | Same backoff strategy |
| Empty response | Logged warning + empty string | No retry (data issue) |
| Unicode errors | `safe_unicode_decode()` | Automatic correction |

The retry decorator is applied at two levels:

1. **Function level**: [minirag/llm/openai.py:81-87]() for `openai_complete_if_cache()`
2. **Embedding level**: [minirag/llm/openai.py:244-250]() for `openai_embed()`

Sources: [minirag/llm/openai.py:81-87](), [minirag/llm/openai.py:144-150](), [minirag/llm/openai.py:244-250]()

---

## Keyword Extraction Mode

LLM functions support a special `keyword_extraction` mode for structured entity extraction:

**Extraction Flow:**

```mermaid
graph TB
    Query["User Query or Document Chunk"]
    
    ExtractFlag["keyword_extraction=True"]
    
    FormatSet["Set response_format"]
    
    subgraph "OpenAI API"
        JSONFormat["response_format='json'<br/>or<br/>GPTKeywordExtractionFormat"]
        
        StructuredOutput["beta.chat.completions.parse()"]
    end
    
    subgraph "Other Providers"
        FreeForm["Standard completion"]
        JSONParse["locate_json_string_body_from_string()"]
    end
    
    Result["Structured Entity Data"]
    
    Query --> ExtractFlag
    ExtractFlag -->|if True| FormatSet
    FormatSet --> JSONFormat
    FormatSet --> FreeForm
    
    JSONFormat --> StructuredOutput
    FreeForm --> JSONParse
    
    StructuredOutput --> Result
    JSONParse --> Result
    
    style ExtractFlag fill:#f9f9f9
    style Result fill:#f9f9f9
```

The `GPTKeywordExtractionFormat` schema:

```python
class GPTKeywordExtractionFormat(BaseModel):
    high_level_keywords: List[str]
    low_level_keywords: List[str]
```

Sources: [minirag/llm/openai.py:89-92](), [minirag/llm/openai.py:157-161](), [minirag/llm/openai.py:214-216]()

---

## Integration with MiniRAG Core

The LLM and embedding functions are accessed through the `QueryParam` configuration:

**Configuration Structure:**

| Parameter | Purpose | Example Values |
|-----------|---------|----------------|
| `llm_model_func` | LLM function reference | `openai_complete`, `gpt_4o_mini_complete` |
| `llm_model_name` | Model identifier | `"gpt-4o-mini"`, `"Phi-3.5-mini-instruct"` |
| `embedding_func` | Embedding function | `openai_embed` with decorator attributes |
| `embedding_dim` | Inferred from function | `1536` (from decorator) |
| `max_token_size` | Inferred from function | `8192` (from decorator) |

The core MiniRAG class passes these through the `hashing_kv` global config:

```python
# Pattern used in minirag/llm/openai.py:162-163
model_name = kwargs["hashing_kv"].global_config["llm_model_name"]
return await openai_complete_if_cache(model_name, prompt, ...)
```

Sources: [minirag/llm/openai.py:162-169](), [minirag/llm/openai.py:243]()

---

## Performance Characteristics

Different LLM and embedding combinations affect MiniRAG performance:

**Model Performance on LiHua-World Dataset:**

| Model | Type | Parameters | Accuracy | Error Rate | Use Case |
|-------|------|-----------|----------|------------|----------|
| Phi-3.5-mini-instruct | SLM | ~3.8B | 53.29% | 23.35% | On-device |
| GLM-Edge-1.5B-Chat | SLM | 1.5B | 52.51% | 25.71% | Resource-constrained |
| Qwen2.5-3B-Instruct | SLM | 3B | 48.75% | 26.02% | Edge deployment |
| MiniCPM3-4B | SLM | 4B | 51.25% | 21.79% | Balanced |
| gpt-4o-mini | LLM | Unknown | 54.08% | 19.44% | Cloud API |

**Embedding Model:**
- Default: `text-embedding-3-small` with 1536 dimensions
- Storage optimization: 25% reduction vs. traditional RAG through quantization

Sources: [README.md:74-89](), [minirag/llm/openai.py:243]()

---

## Summary

The LLM and embedding integration layer in MiniRAG provides:

1. **Unified async interface** across multiple providers (OpenAI, HuggingFace, NVIDIA, OpenRouter)
2. **Robust error handling** with automatic retry and exponential backoff
3. **Flexible response modes** supporting both streaming and batch operations
4. **Metadata-enriched embeddings** via decorator pattern for storage optimization
5. **Structured extraction support** for entity and keyword identification
6. **Provider-agnostic design** enabling easy model swapping and A/B testing

This architecture enables MiniRAG to support both Small Language Models for on-device deployment and Large Language Models for cloud-based scenarios, with consistent interfaces throughout the codebase.

For implementation details:
- LLM function implementations: [LLM Interface](#6.1)
- Embedding generation and quantization: [Embedding Functions](#6.2)
- Complete model list and benchmarks: [Supported Models](#6.3)

Sources: [minirag/llm/openai.py:1-267](), [README.md:1-174]()

---

# Page: LLM Interface

# Python API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [main.py](main.py)
- [minirag/llm/openai.py](minirag/llm/openai.py)
- [minirag/prompt.py](minirag/prompt.py)

</details>



This page documents the Python API for MiniRAG, which provides programmatic access to MiniRAG's core functionality. The API allows users to index documents, query the indexed knowledge base, and manage entities within the system. For information about the REST API, see [REST API](#6.2).

## Core API Overview

MiniRAG's Python API is centered around the `MiniRAG` class, which serves as the primary entry point for interacting with the system. This class encapsulates all the functionality needed to initialize the system, configure storage backends, index documents, and perform queries.

### MiniRAG Class Overview

```mermaid
classDiagram
    class MiniRAG {
        +working_dir: str
        +kv_storage: str
        +vector_storage: str
        +graph_storage: str
        +doc_status_storage: str
        +embedding_func: EmbeddingFunc
        +llm_model_func: callable
        +insert(string_or_strings)
        +ainsert(input, ids)
        +query(query, param)
        +aquery(query, param)
        +delete_by_entity(entity_name)
        +adelete_by_entity(entity_name)
    }
    
    class QueryParam {
        +mode: str
        +response_type: str
        +top_k: int
    }
    
    MiniRAG -- QueryParam: "Uses for query()"
```

Sources: [minirag/minirag.py:118-600]()

## Installation and Initialization

To use the MiniRAG Python API, you first need to import the MiniRAG class and create an instance:

```python
from minirag import MiniRAG, QueryParam
from minirag.utils import EmbeddingFunc

# Create a MiniRAG instance
rag = MiniRAG(
    working_dir="./my_minirag_cache",
    embedding_func=your_embedding_function,
    llm_model_func=your_llm_function
)
```

The `MiniRAG` class constructor accepts numerous parameters to configure various aspects of the system:

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `working_dir` | str | Directory for storing cache files | `"./minirag_cache_{timestamp}"` |
| `kv_storage` | str | Key-value storage backend | `"JsonKVStorage"` |
| `vector_storage` | str | Vector storage backend | `"NanoVectorDBStorage"` |
| `graph_storage` | str | Graph storage backend | `"NetworkXStorage"` |
| `doc_status_storage` | str | Document status storage backend | `"JsonDocStatusStorage"` |
| `embedding_func` | EmbeddingFunc | Function for creating embeddings | None |
| `llm_model_func` | callable | Function for LLM inference | None |
| `chunk_token_size` | int | Token size for text chunks | 1200 |
| `chunk_overlap_token_size` | int | Overlap size between chunks | 100 |

Sources: [minirag/minirag.py:118-183]()

### Storage Components

During initialization, MiniRAG creates various storage components based on the configured backends:

```mermaid
flowchart TB
    MiniRAGClass["MiniRAG Class"] --> KVStore["key_string_value_json_storage_cls"]
    MiniRAGClass --> VectorDB["vector_db_storage_cls"]
    MiniRAGClass --> GraphStore["graph_storage_cls"]
    MiniRAGClass --> DocStore["doc_status_storage_cls"]
    
    KVStore --> full_docs["full_docs"]
    KVStore --> text_chunks["text_chunks"]
    KVStore --> llm_cache["llm_response_cache"]
    
    VectorDB --> chunks_vdb["chunks_vdb"]
    VectorDB --> entities_vdb["entities_vdb"]
    VectorDB --> entity_name_vdb["entity_name_vdb"]
    VectorDB --> relationships_vdb["relationships_vdb"]
    
    GraphStore --> cerg["chunk_entity_relation_graph"]
    
    DocStore --> doc_status["doc_status"]
```

Sources: [minirag/minirag.py:185-309]()

## Core Methods

The MiniRAG class provides several core methods for document indexing, querying, and entity management:

### Document Indexing

```python
# Synchronous indexing
rag.insert("My document text")
rag.insert(["Document 1", "Document 2", "Document 3"])

# Asynchronous indexing
await rag.ainsert("My document text")
await rag.ainsert(["Document 1", "Document 2", "Document 3"])

# With custom IDs
rag.insert("My document text", ids="doc-1")
rag.insert(["Document 1", "Document 2"], ids=["doc-1", "doc-2"])
```

Sources: [minirag/minirag.py:336-385]()

The document indexing pipeline consists of several steps:

```mermaid
flowchart TB
    subgraph "DocumentProcessing"
        doc_insert["insert(doc)"] --> doc_ainsert["ainsert(input, ids)"]
        doc_ainsert --> doc_pipeline1["apipeline_enqueue_documents()"]
        doc_pipeline1 --> doc_pipeline2["apipeline_process_enqueue_documents()"]
        doc_pipeline2 --> doc_chunking["chunking_func()"]
        doc_chunking --> doc_store["Store chunks in storage"]
        doc_store --> doc_entity["extract_entities()"]
        doc_entity --> doc_insert_done["_insert_done()"]
    end
```

Sources: [minirag/minirag.py:386-511]()

### Querying

```python
# Synchronous querying with different modes
result = rag.query("What is MiniRAG?", param=QueryParam(mode="light"))
result = rag.query("What is MiniRAG?", param=QueryParam(mode="mini"))
result = rag.query("What is MiniRAG?", param=QueryParam(mode="naive"))

# Asynchronous querying
result = await rag.aquery("What is MiniRAG?", param=QueryParam(mode="mini"))

# With custom parameters
result = rag.query("What is MiniRAG?", param=QueryParam(
    mode="mini",
    top_k=5,
    response_type="brief"
))
```

Sources: [minirag/minirag.py:529-568]()

The query processing workflow:

```mermaid
flowchart TB
    subgraph "QueryProcessing"
        query_start["query(q, param)"] --> query_async["aquery(query, param)"]
        query_async --> query_mode{"param.mode"}
        query_mode -->|"light"| query_hybrid["hybrid_query()"]
        query_mode -->|"mini"| query_minirag["minirag_query()"]
        query_mode -->|"naive"| query_naive["naive_query()"]
        query_hybrid & query_minirag & query_naive --> query_response["Return response"]
        query_response --> query_done["_query_done()"]
    end
```

Sources: [minirag/minirag.py:529-576]()

### Entity Management

```python
# Delete an entity and its relationships
rag.delete_by_entity("Entity Name")

# Asynchronous deletion
await rag.adelete_by_entity("Entity Name")
```

Sources: [minirag/minirag.py:578-607]()

## Query Parameters

The `QueryParam` class provides configuration options for queries:

```python
from minirag import QueryParam

param = QueryParam(
    mode="mini",       # Query mode: "light", "mini", or "naive"
    top_k=5,           # Number of results to retrieve
    response_type="brief"  # Response format
)
```

## Complete Usage Example

Here's a complete example of using the MiniRAG Python API:

```python
from minirag import MiniRAG, QueryParam
from minirag.llm.hf import hf_model_complete, hf_embed
from minirag.utils import EmbeddingFunc
from transformers import AutoModel, AutoTokenizer

# Initialize embedding function
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
embedding_func = EmbeddingFunc(
    embedding_dim=384,
    max_token_size=1000,
    func=lambda texts: hf_embed(
        texts,
        tokenizer=AutoTokenizer.from_pretrained(EMBEDDING_MODEL),
        embed_model=AutoModel.from_pretrained(EMBEDDING_MODEL),
    ),
)

# Initialize MiniRAG
rag = MiniRAG(
    working_dir="./minirag_cache",
    llm_model_func=hf_model_complete,
    llm_model_name="meta-llama/Llama-3.2-1B-Instruct",
    embedding_func=embedding_func,
)

# Index documents
with open("document.txt") as f:
    rag.insert(f.read())

# Query the indexed documents
query = "What is MiniRAG?"
answer = rag.query(query, param=QueryParam(mode="mini"))
print(answer)
```

Sources: [main.py:1-97]()

## Storage Backends

MiniRAG supports multiple storage backends for different components:

| Component | Available Backends |
|-----------|-------------------|
| Vector Storage | NanoVectorDBStorage, OracleVectorDBStorage, MilvusVectorDBStorge, ChromaVectorDBStorage, TiDBVectorDBStorage, PGVectorStorage |
| Key-Value Storage | JsonKVStorage, OracleKVStorage, MongoKVStorage, RedisKVStorage, TiDBKVStorage, PGKVStorage |
| Graph Storage | NetworkXStorage, Neo4JStorage, OracleGraphStorage, MongoGraphStorage, TiDBGraphStorage, PGGraphStorage, AGEStorage, GremlinStorage |
| Document Status Storage | JsonDocStatusStorage, PGDocStatusStorage |

Sources: [minirag/minirag.py:39-62]()

## Asynchronous API

MiniRAG provides both synchronous and asynchronous versions of its core methods:

| Synchronous | Asynchronous | Description |
|-------------|--------------|-------------|
| `insert()` | `ainsert()` | Insert documents into the system |
| `query()` | `aquery()` | Query the indexed knowledge base |
| `delete_by_entity()` | `adelete_by_entity()` | Delete an entity and its relationships |

The synchronous methods are implemented as wrappers around the asynchronous ones, running them in the current event loop until completion:

```python
def insert(self, string_or_strings):
    loop = always_get_an_event_loop()
    return loop.run_until_complete(self.ainsert(string_or_strings))
```

Sources: [minirag/minirag.py:336-339](), [minirag/minirag.py:529-532](), [minirag/minirag.py:578-580]()

## Event Loop Management

MiniRAG includes a utility function `always_get_an_event_loop()` to ensure there is always an event loop available for asynchronous operations. This function tries to get the current event loop, and if not available or closed, creates a new one:

```python
def always_get_an_event_loop() -> asyncio.AbstractEventLoop:
    try:
        current_loop = asyncio.get_event_loop()
        if current_loop.is_closed():
            raise RuntimeError("Event loop is closed.")
        return current_loop
    except RuntimeError:
        logger.info("Creating a new event loop in main thread.")
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        return new_loop
```

Sources: [minirag/minirag.py:93-115]()

## Advanced Usage: Custom Storage Backends

MiniRAG allows lazy loading of storage classes through the `_get_storage_class` method:

```python
def _get_storage_class(self, storage_name: str) -> dict:
    import_path = STORAGES[storage_name]
    storage_class = lazy_external_import(import_path, storage_name)
    return storage_class
```

Sources: [minirag/minirag.py:311-314]()

This enables you to use any of the supported storage backends or implement your own by extending the base storage classes.

---

# Page: Embedding Functions

# Embedding Functions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [minirag/__init__.py](minirag/__init__.py)
- [minirag/base.py](minirag/base.py)
- [minirag/utils.py](minirag/utils.py)

</details>



## Purpose and Scope

Embedding functions in MiniRAG convert text into dense vector representations that enable semantic similarity search across entities, relationships, and document chunks. This page documents the `EmbeddingFunc` dataclass, quantization mechanisms, and integration patterns with storage backends.

For information about LLM models and API interfaces, see [LLM Interface](#6.1). For supported embedding model implementations, see [Supported Models](#6.3). For vector storage backends that consume embeddings, see [Vector Storage Backends](#5.2).

---

## EmbeddingFunc Dataclass

The `EmbeddingFunc` dataclass wraps embedding generation functions with metadata about dimensionality and token limits. It provides a standardized interface for all embedding operations across the MiniRAG system.

**Structure:**

```
EmbeddingFunc
├── embedding_dim: int          # Dimensionality of output vectors
├── max_token_size: int         # Maximum input tokens the model handles
└── func: callable              # Async function that generates embeddings
```

### Core Implementation

The dataclass is defined in [minirag/utils.py:45-52]() and implements the async callable protocol:

```python
@dataclass
class EmbeddingFunc:
    embedding_dim: int
    max_token_size: int
    func: callable

    async def __call__(self, *args, **kwargs) -> np.ndarray:
        return await self.func(*args, **kwargs)
```

| Field | Type | Purpose |
|-------|------|---------|
| `embedding_dim` | `int` | Dimension of embedding vectors (e.g., 384, 768, 1536) |
| `max_token_size` | `int` | Maximum tokens the embedding model can process |
| `func` | `callable` | Async function that performs the actual embedding generation |

The async callable pattern allows `EmbeddingFunc` instances to be invoked directly: `embeddings = await embedding_func(texts)`.

**Sources:** [minirag/utils.py:45-52]()

---

## Creating Embedding Functions

Embedding functions are created using the `wrap_embedding_func_with_attrs` decorator, which converts a standard async function into an `EmbeddingFunc` instance with the required metadata.

### Decorator Pattern

The decorator is implemented in [minirag/utils.py:119-126]():

```python
def wrap_embedding_func_with_attrs(**kwargs):
    """Wrap a function with attributes"""
    def final_decro(func) -> EmbeddingFunc:
        new_func = EmbeddingFunc(**kwargs, func=func)
        return new_func
    return final_decro
```

### Usage Example

```python
@wrap_embedding_func_with_attrs(
    embedding_dim=384,
    max_token_size=512
)
async def my_embedding_function(texts: list[str]) -> np.ndarray:
    # Implementation that returns shape (len(texts), 384)
    ...
```

This pattern ensures all embedding functions provide consistent metadata to storage backends that need to configure vector dimensions and handle token limits.

```mermaid
graph TB
    AsyncFunc["async embedding_function(texts)"]
    Decorator["@wrap_embedding_func_with_attrs<br/>embedding_dim=384<br/>max_token_size=512"]
    EmbedFunc["EmbeddingFunc instance<br/>.embedding_dim<br/>.max_token_size<br/>.func"]
    Storage["Storage Backends<br/>BaseVectorStorage<br/>BaseKVStorage<br/>BaseGraphStorage"]
    
    AsyncFunc --> Decorator
    Decorator --> EmbedFunc
    EmbedFunc --> Storage
    
    Storage -.uses metadata.-> EmbedFunc
    Storage -.calls.-> AsyncFunc
```

**Sources:** [minirag/utils.py:119-126]()

---

## Embedding Quantization

MiniRAG supports 8-bit quantization of embedding vectors to reduce storage requirements by approximately 75% (from 32-bit float to 8-bit uint). This is particularly important for on-device deployment scenarios.

### Quantization Functions

```mermaid
graph LR
    Original["np.ndarray<br/>float32 embeddings<br/>(e.g., 384 dims × 4 bytes)"]
    Quant["quantize_embedding()"]
    QuantData["quantized: np.uint8<br/>min_val: float<br/>max_val: float<br/>(384 dims × 1 byte)"]
    Dequant["dequantize_embedding()"]
    Restored["np.ndarray<br/>float32 approximation"]
    
    Original --> Quant
    Quant --> QuantData
    QuantData --> Dequant
    Dequant --> Restored
```

### Quantization Implementation

Defined in [minirag/utils.py:450-463]():

| Function | Input | Output | Purpose |
|----------|-------|--------|---------|
| `quantize_embedding()` | `embedding: np.ndarray`, `bits: int = 8` | `(quantized, min_val, max_val)` | Convert float embeddings to 8-bit integers with metadata |
| `dequantize_embedding()` | `quantized: np.ndarray`, `min_val`, `max_val`, `bits=8` | `np.ndarray` (float32) | Restore quantized embeddings to approximate float values |

### Quantization Algorithm

The quantization process uses min-max normalization:

1. **Find range:** `min_val = embedding.min()`, `max_val = embedding.max()`
2. **Calculate scale:** `scale = (2^bits - 1) / (max_val - min_val)`
3. **Quantize:** `quantized = round((embedding - min_val) * scale)` as uint8

Dequantization reverses the process:

1. **Calculate scale:** `scale = (max_val - min_val) / (2^bits - 1)`
2. **Dequantize:** `restored = quantized * scale + min_val` as float32

The metadata (`min_val`, `max_val`) must be stored alongside quantized vectors to enable reconstruction.

**Sources:** [minirag/utils.py:450-463]()

---

## Integration with Storage Backends

All three storage abstraction layers accept an `embedding_func` parameter, though they use it differently based on their role in the system.

### Storage Layer Embedding Requirements

```mermaid
graph TB
    EmbedFunc["EmbeddingFunc"]
    
    subgraph BaseStorage ["Storage Abstraction Layer"]
        BaseVector["BaseVectorStorage<br/>embedding_func: EmbeddingFunc<br/>(required)"]
        BaseKV["BaseKVStorage<br/>embedding_func: EmbeddingFunc<br/>(required)"]
        BaseGraph["BaseGraphStorage<br/>embedding_func: EmbeddingFunc<br/>(optional, default None)"]
    end
    
    subgraph VectorOps ["Vector Operations"]
        VectorQuery["query(query: str, top_k: int)<br/>→ Embeds query text<br/>→ Similarity search"]
        VectorUpsert["upsert(data: dict)<br/>→ Embeds 'content' field<br/>→ Stores vectors"]
    end
    
    subgraph GraphOps ["Graph Operations"]
        GraphEmbed["embed_nodes(algorithm: str)<br/>→ NotImplementedError<br/>(not used in MiniRAG)"]
    end
    
    EmbedFunc --> BaseVector
    EmbedFunc --> BaseKV
    EmbedFunc --> BaseGraph
    
    BaseVector --> VectorQuery
    BaseVector --> VectorUpsert
    BaseGraph --> GraphEmbed
```

### BaseVectorStorage

Declared in [minirag/base.py:63-74]():

```python
@dataclass
class BaseVectorStorage(StorageNameSpace):
    embedding_func: EmbeddingFunc
    meta_fields: set = field(default_factory=set)

    async def query(self, query: str, top_k: int) -> list[dict]:
        # Uses embedding_func to convert query to vector
        
    async def upsert(self, data: dict[str, dict]):
        # Uses embedding_func to convert 'content' field to vectors
```

**Usage:** The `embedding_func` is invoked during both `query()` (to embed the query string) and `upsert()` (to embed the `'content'` field from each document). If the data already contains an `'embedding'` field, it may be used directly instead.

### BaseKVStorage

Declared in [minirag/base.py:78-100]():

```python
@dataclass
class BaseKVStorage(Generic[T], StorageNameSpace):
    embedding_func: EmbeddingFunc
    # ... methods for key-value operations
```

**Usage:** While `BaseKVStorage` receives an `embedding_func`, it's primarily provided for consistency across storage types. Key-value stores typically don't perform similarity searches themselves but may use embeddings for related operations.

### BaseGraphStorage

Declared in [minirag/base.py:104-148]():

```python
@dataclass
class BaseGraphStorage(StorageNameSpace):
    embedding_func: EmbeddingFunc = None
    
    async def embed_nodes(self, algorithm: str) -> tuple[np.ndarray, list[str]]:
        raise NotImplementedError("Node embedding is not used in minirag.")
```

**Usage:** The `embedding_func` is optional for graph storage. The `embed_nodes()` method explicitly raises `NotImplementedError` at [minirag/base.py:148](), confirming that MiniRAG does not use graph node embeddings for its topology-enhanced retrieval approach.

**Sources:** [minirag/base.py:63-148]()

---

## Similarity Computation

Once embeddings are generated, they are used for similarity search operations. MiniRAG provides cosine similarity calculation as the primary similarity metric.

### Cosine Similarity

Implemented in [minirag/utils.py:443-447]():

```python
def cosine_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    return dot_product / (norm1 * norm2)
```

This function computes the cosine of the angle between two vectors, producing values in [-1, 1] where 1 indicates identical direction (maximum similarity) and -1 indicates opposite direction.

### Usage in Vector Databases

Vector storage implementations use this similarity function (or hardware-accelerated equivalents) to rank results during `query()` operations:

1. **Query embedding:** Convert query string to vector using `embedding_func`
2. **Similarity search:** Compute cosine similarity with stored vectors
3. **Ranking:** Return top-k results sorted by similarity score

**Sources:** [minirag/utils.py:443-447]()

---

## Embedding Flow in MiniRAG Pipeline

The following diagram shows how embedding functions are used throughout the indexing and query phases:

```mermaid
sequenceDiagram
    participant Doc as "Documents"
    participant MiniRAG as "MiniRAG Core"
    participant Extract as "Entity Extraction"
    participant EmbedFunc as "EmbeddingFunc"
    participant VectorDB as "Vector Storage<br/>(entity_vdb,<br/>chunks_vdb, etc.)"
    participant Query as "User Query"
    
    rect rgb(245, 245, 245)
        Note over Doc,VectorDB: Indexing Phase
        Doc->>MiniRAG: insert(documents)
        MiniRAG->>Extract: Extract entities/chunks
        Extract->>EmbedFunc: Generate embeddings
        EmbedFunc-->>Extract: np.ndarray vectors
        Extract->>VectorDB: upsert(data with embeddings)
        Note over VectorDB: Stores vectors for<br/>entities, relationships,<br/>chunks
    end
    
    rect rgb(250, 250, 250)
        Note over Query,VectorDB: Query Phase
        Query->>MiniRAG: query(question, mode)
        MiniRAG->>EmbedFunc: Embed query text
        EmbedFunc-->>MiniRAG: query_vector
        MiniRAG->>VectorDB: query(query_vector, top_k)
        VectorDB->>VectorDB: Compute cosine_similarity
        VectorDB-->>MiniRAG: Top-k similar items
        Note over MiniRAG: Use retrieved context<br/>for LLM generation
    end
```

### Indexing Phase Embedding Points

During document indexing, embeddings are generated for:

1. **Named entities:** Entity names and descriptions are embedded and stored in `entity_vdb` and `entity_name_vdb`
2. **Relationships:** Relationship descriptions are embedded and stored in `relationships_vdb`
3. **Text chunks:** Document chunks are embedded and stored in `chunks_vdb`

### Query Phase Embedding Points

During query processing, embeddings are generated for:

1. **Query text:** The user's question is embedded to find semantically similar entities
2. **Entity extraction:** Extracted query entities may be embedded for matching
3. **Context ranking:** Retrieved contexts are compared using embedding similarity

**Sources:** [minirag/base.py:63-74](), [minirag/utils.py:45-52]()

---

## Summary

The `EmbeddingFunc` abstraction provides a clean separation between embedding generation logic and storage operations. Key design principles:

| Aspect | Design Choice | Benefit |
|--------|---------------|---------|
| **Dataclass structure** | Wraps callable with metadata | Storage backends can configure dimensions and token limits |
| **Async protocol** | `__call__` returns coroutine | Integrates with async storage operations |
| **Decorator pattern** | `wrap_embedding_func_with_attrs` | Clean syntax for creating instances |
| **Quantization support** | 8-bit compression functions | 75% storage reduction for on-device scenarios |
| **Storage integration** | Required for vector/KV, optional for graph | Flexible usage based on storage type needs |

The embedding system enables MiniRAG's semantic search capabilities while maintaining flexibility for different embedding models and storage backends. The quantization support is particularly important for the system's goal of efficient on-device deployment with Small Language Models.

**Sources:** [minirag/base.py:7](), [minirag/base.py:63-148](), [minirag/utils.py:45-52](), [minirag/utils.py:119-126](), [minirag/utils.py:443-463]()

---

# Page: Supported Models

# Supported Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [main.py](main.py)
- [minirag/prompt.py](minirag/prompt.py)

</details>



This page documents the language models and embedding models supported by MiniRAG, including Small Language Models (SLMs) optimized for on-device RAG scenarios and larger LLMs for comparison purposes. For information about the LLM interface and API integration, see [LLM Interface](#6.1). For details on embedding generation, see [Embedding Functions](#6.2).

## Overview

MiniRAG is designed to enable effective RAG performance with Small Language Models (1.5B-4B parameters) through its heterogeneous graph indexing and topology-enhanced retrieval innovations. The framework supports both open-source models via HuggingFace and commercial models via OpenAI-compatible APIs.

**Sources:** [README.md:30-34](), [README.md:74-88]()

---

## Small Language Models (SLMs)

MiniRAG's core innovation targets Small Language Models, which are suitable for resource-constrained and on-device deployment scenarios. The following SLMs have been validated with MiniRAG:

### Phi-3.5-mini-instruct

| Property | Value |
|----------|-------|
| **Model ID** | `microsoft/Phi-3.5-mini-instruct` |
| **Parameters** | ~3.8B |
| **Provider** | Microsoft |
| **LiHua-World Accuracy** | 53.29% |
| **Error Rate** | 23.35% |

Microsoft's Phi-3.5-mini-instruct is a compact instruction-tuned model that demonstrates strong performance with MiniRAG's topology-enhanced retrieval, achieving 53.29% accuracy compared to 41.22% with NaiveRAG.

### GLM-Edge-1.5B-Chat

| Property | Value |
|----------|-------|
| **Model ID** | `THUDM/glm-edge-1.5b-chat` |
| **Parameters** | 1.5B |
| **Provider** | Tsinghua University (THUDM) |
| **LiHua-World Accuracy** | 52.51% |
| **Error Rate** | 25.71% |

GLM-Edge is the smallest model tested, demonstrating that MiniRAG can achieve strong RAG performance even with ultra-compact models. It shows a 52.51% accuracy with MiniRAG versus 42.79% with NaiveRAG.

### Qwen2.5-3B-Instruct

| Property | Value |
|----------|-------|
| **Model ID** | `Qwen/Qwen2.5-3B-Instruct` |
| **Parameters** | 3B |
| **Provider** | Alibaba Cloud |
| **LiHua-World Accuracy** | 48.75% |
| **Error Rate** | 26.02% |

Qwen2.5-3B-Instruct is part of Alibaba's Qwen model family, showing consistent improvement with MiniRAG's graph-based retrieval (48.75%) over the baseline NaiveRAG approach (43.73%).

### MiniCPM3-4B

| Property | Value |
|----------|-------|
| **Model ID** | `openbmb/MiniCPM3-4B` |
| **Parameters** | 4B |
| **Provider** | OpenBMB |
| **LiHua-World Accuracy** | 51.25% |
| **Error Rate** | 21.79% |

MiniCPM3-4B is the largest SLM in the test set, achieving 51.25% accuracy with MiniRAG and demonstrating the lowest error rate (21.79%) among small models.

**Sources:** [README.md:78-82](), [main.py:35-45]()

---

## Large Language Models (LLMs)

### gpt-4o-mini

| Property | Value |
|----------|-------|
| **Model ID** | `gpt-4o-mini` |
| **Provider** | OpenAI |
| **API** | OpenAI API |
| **LiHua-World Accuracy** | 54.08% (MiniRAG), 56.90% (LightRAG) |
| **Error Rate** | 19.44% (MiniRAG) |

OpenAI's gpt-4o-mini serves as the LLM baseline, demonstrating that MiniRAG's SLM performance approaches LLM-level results. The model achieves 54.08% accuracy with MiniRAG on the LiHua-World dataset.

**Sources:** [README.md:82]()

---

## Embedding Models

MiniRAG uses embedding models for vector-based similarity search in its heterogeneous graph structure. The default configuration uses:

### sentence-transformers/all-MiniLM-L6-v2

| Property | Value |
|----------|-------|
| **Model ID** | `sentence-transformers/all-MiniLM-L6-v2` |
| **Embedding Dimension** | 384 |
| **Max Token Size** | 1000 |
| **Provider** | Sentence Transformers |

This lightweight embedding model provides efficient semantic embeddings for text chunks and entity representations in MiniRAG's vector storage backends.

**Sources:** [main.py:14](), [main.py:63-71]()

---

## Model Integration Architecture

The following diagram shows how different model types integrate into MiniRAG's architecture:

```mermaid
graph TB
    subgraph "MiniRAG Core"
        MiniRAG["MiniRAG<br/>(minirag.py)"]
    end
    
    subgraph "Model Configuration"
        ModelFunc["llm_model_func"]
        ModelName["llm_model_name"]
        EmbedFunc["embedding_func"]
        MaxToken["llm_model_max_token_size"]
    end
    
    subgraph "HuggingFace Models"
        HFComplete["hf_model_complete()<br/>(minirag.llm.hf)"]
        HFEmbed["hf_embed()<br/>(minirag.llm.hf)"]
        
        subgraph "SLM Options"
            Phi["microsoft/Phi-3.5-mini-instruct"]
            GLM["THUDM/glm-edge-1.5b-chat"]
            Qwen["Qwen/Qwen2.5-3B-Instruct"]
            MiniCPM["openbmb/MiniCPM3-4B"]
        end
        
        Embedding["sentence-transformers/all-MiniLM-L6-v2"]
    end
    
    subgraph "OpenAI Models"
        OpenAIComplete["openai_complete()<br/>(minirag.llm.openai)"]
        GPT4o["gpt-4o-mini"]
    end
    
    MiniRAG --> ModelFunc
    MiniRAG --> ModelName
    MiniRAG --> EmbedFunc
    MiniRAG --> MaxToken
    
    ModelFunc --> HFComplete
    ModelFunc --> OpenAIComplete
    
    HFComplete --> Phi
    HFComplete --> GLM
    HFComplete --> Qwen
    HFComplete --> MiniCPM
    
    OpenAIComplete --> GPT4o
    
    EmbedFunc --> HFEmbed
    HFEmbed --> Embedding
```

**Diagram: Model Integration in MiniRAG Architecture**

**Sources:** [main.py:58-72]()

---

## Model Configuration

### HuggingFace Model Configuration

The following example shows how to configure a HuggingFace model in MiniRAG:

```python
from minirag import MiniRAG, QueryParam
from minirag.llm.hf import hf_model_complete, hf_embed
from minirag.utils import EmbeddingFunc
from transformers import AutoModel, AutoTokenizer

# Configure LLM
LLM_MODEL = "microsoft/Phi-3.5-mini-instruct"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Initialize MiniRAG
rag = MiniRAG(
    working_dir="./working_dir",
    llm_model_func=hf_model_complete,
    llm_model_max_token_size=200,
    llm_model_name=LLM_MODEL,
    embedding_func=EmbeddingFunc(
        embedding_dim=384,
        max_token_size=1000,
        func=lambda texts: hf_embed(
            texts,
            tokenizer=AutoTokenizer.from_pretrained(EMBEDDING_MODEL),
            embed_model=AutoModel.from_pretrained(EMBEDDING_MODEL),
        ),
    ),
)
```

This code can be found at [main.py:58-72]().

### Model Selection via Command Line

The main.py script provides a convenient command-line interface for model selection:

```bash
# Use Phi-3.5-mini-instruct
python main.py --model PHI

# Use GLM-Edge-1.5B-Chat
python main.py --model GLM

# Use MiniCPM3-4B
python main.py --model MiniCPM

# Use Qwen2.5-3B-Instruct
python main.py --model qwen
```

The model mapping logic is implemented at [main.py:35-45]().

**Sources:** [main.py:35-72]()

---

## Performance Comparison

### LiHua-World Dataset Results

The following table compares model performance across different RAG approaches on the LiHua-World benchmark:

| Model | NaiveRAG | GraphRAG | LightRAG | **MiniRAG** |
|-------|----------|----------|----------|-------------|
|       | acc↑ / err↓ | acc↑ / err↓ | acc↑ / err↓ | acc↑ / err↓ |
| **Phi-3.5-mini-instruct** | 41.22% / 23.20% | / | 39.81% / 25.39% | **53.29% / 23.35%** |
| **GLM-Edge-1.5B-Chat** | 42.79% / 24.76% | / | 35.74% / 25.86% | **52.51% / 25.71%** |
| **Qwen2.5-3B-Instruct** | 43.73% / 24.14% | / | 39.18% / 28.68% | **48.75% / 26.02%** |
| **MiniCPM3-4B** | 43.42% / 17.08% | / | 35.42% / 21.94% | **51.25% / 21.79%** |
| **gpt-4o-mini** | 46.55% / 19.12% | 35.27% / 37.77% | 56.90% / 20.85% | **54.08% / 19.44%** |

**Key Observations:**
- All SLMs show 8-13% absolute accuracy improvement with MiniRAG over NaiveRAG
- MiniRAG enables SLMs to achieve performance comparable to LLM-based methods
- Error rates remain competitive across all models with MiniRAG

### MultiHop-RAG Dataset Results

| Model | NaiveRAG | GraphRAG | LightRAG | **MiniRAG** |
|-------|----------|----------|----------|-------------|
|       | acc↑ / err↓ | acc↑ / err↓ | acc↑ / err↓ | acc↑ / err↓ |
| **Phi-3.5-mini-instruct** | 42.72% / 31.34% | / | 27.03% / 11.78% | **49.96% / 28.44%** |
| **GLM-Edge-1.5B-Chat** | 44.44% / 24.26% | / | / | **51.41% / 23.44%** |
| **Qwen2.5-3B-Instruct** | 39.48% / 31.69% | / | 21.91% / 13.73% | **48.55% / 33.10%** |
| **MiniCPM3-4B** | 39.24% / 31.42% | / | 19.48% / 10.41% | **47.77% / 26.88%** |
| **gpt-4o-mini** | 53.60% / 27.19% | 60.92% / 16.86% | 64.91% / 19.37% | **68.43% / 19.41%** |

**Note:** "/" indicates the method struggles to generate effective responses.

**Sources:** [README.md:73-91]()

---

## Model Selection Guidelines

```mermaid
graph TB
    Start["Model Selection Decision"]
    
    Constraint["Resource Constraints?"]
    UseCase["Use Case Requirements"]
    
    Start --> Constraint
    
    Constraint -->|"Strict<br/>(On-Device)"| UltraCompact
    Constraint -->|"Moderate<br/>(Edge Devices)"| Compact
    Constraint -->|"Flexible<br/>(Cloud/Server)"| Standard
    
    UltraCompact["GLM-Edge-1.5B-Chat<br/>1.5B params<br/>Lowest resource usage"]
    
    Compact["Phi-3.5-mini-instruct<br/>or Qwen2.5-3B-Instruct<br/>~3B params<br/>Balanced performance"]
    
    Standard["MiniCPM3-4B<br/>4B params<br/>Best SLM accuracy<br/>or<br/>gpt-4o-mini<br/>Highest accuracy"]
    
    UltraCompact --> Metrics
    Compact --> Metrics
    Standard --> Metrics
    
    Metrics["Evaluation Metrics:<br/>✓ Accuracy on test queries<br/>✓ Error rate tolerance<br/>✓ Response latency<br/>✓ Memory footprint"]
```

**Diagram: Model Selection Decision Tree**

### Selection Criteria

**For Ultra-Compact Deployment (< 2GB Memory):**
- **Model:** GLM-Edge-1.5B-Chat
- **Use Case:** Mobile devices, IoT, severely constrained environments
- **Trade-off:** Lowest resource usage, 52.51% accuracy

**For Balanced Performance (2-4GB Memory):**
- **Model:** Phi-3.5-mini-instruct or Qwen2.5-3B-Instruct
- **Use Case:** Edge devices, embedded systems, standard on-device scenarios
- **Trade-off:** Good balance of accuracy (48-53%) and resource usage

**For Maximum SLM Performance (4-8GB Memory):**
- **Model:** MiniCPM3-4B
- **Use Case:** High-performance edge computing, workstations
- **Trade-off:** Best SLM accuracy (51.25%), lowest error rate among SLMs

**For Cloud/API Deployment:**
- **Model:** gpt-4o-mini
- **Use Case:** Cloud services, unlimited resources
- **Trade-off:** Highest accuracy (54-68%), requires API access

**Sources:** [README.md:74-91]()

---

## Model-Specific Integration Details

### HuggingFace Model Loading

```mermaid
sequenceDiagram
    participant Main as "main.py"
    participant MiniRAG as "MiniRAG"
    participant HFFunc as "hf_model_complete"
    participant HF as "HuggingFace<br/>Transformers"
    
    Main->>Main: "Load AutoModel and AutoTokenizer"
    Main->>MiniRAG: "Initialize with llm_model_func=hf_model_complete"
    
    rect rgb(245, 245, 245)
        Note over Main,HF: Entity Extraction Phase
        MiniRAG->>HFFunc: "extract_entities(text_chunk)"
        HFFunc->>HF: "tokenizer.encode(prompt)"
        HF-->>HFFunc: "input_ids"
        HFFunc->>HF: "model.generate(input_ids)"
        HF-->>HFFunc: "output_ids"
        HFFunc->>HF: "tokenizer.decode(output_ids)"
        HF-->>HFFunc: "entities and relationships"
        HFFunc-->>MiniRAG: "parsed entities"
    end
    
    rect rgb(245, 245, 245)
        Note over Main,HF: Query Phase
        MiniRAG->>HFFunc: "generate_response(context)"
        HFFunc->>HF: "model.generate(prompt + context)"
        HF-->>HFFunc: "response"
        HFFunc-->>MiniRAG: "final answer"
    end
```

**Diagram: HuggingFace Model Integration Sequence**

**Sources:** [main.py:7-10](), [main.py:58-72]()

---

## Embedding Model Configuration

The `EmbeddingFunc` dataclass wraps the embedding generation process:

```python
EmbeddingFunc(
    embedding_dim=384,        # Output dimension for all-MiniLM-L6-v2
    max_token_size=1000,      # Maximum tokens per text chunk
    func=lambda texts: hf_embed(
        texts,
        tokenizer=AutoTokenizer.from_pretrained(EMBEDDING_MODEL),
        embed_model=AutoModel.from_pretrained(EMBEDDING_MODEL),
    ),
)
```

This configuration at [main.py:63-71]() provides:
- **embedding_dim:** 384-dimensional vectors for efficient similarity search
- **max_token_size:** 1000 tokens to handle substantial text chunks
- **func:** Custom embedding function using HuggingFace's sentence transformers

**Sources:** [main.py:63-71]()

---

## Performance vs. Resource Trade-offs

```mermaid
graph LR
    subgraph "Resource Efficiency"
        GLM["GLM-Edge-1.5B<br/>1.5B params<br/>~3GB RAM<br/>52.51% acc"]
    end
    
    subgraph "Balanced Models"
        Phi["Phi-3.5-mini<br/>3.8B params<br/>~5GB RAM<br/>53.29% acc"]
        Qwen["Qwen2.5-3B<br/>3B params<br/>~4GB RAM<br/>48.75% acc"]
    end
    
    subgraph "High Performance"
        MiniCPM["MiniCPM3-4B<br/>4B params<br/>~6GB RAM<br/>51.25% acc"]
        GPT["gpt-4o-mini<br/>API-based<br/>Cloud RAM<br/>54.08% acc"]
    end
    
    GLM -->|"Better Accuracy"| Phi
    GLM -->|"Better Accuracy"| Qwen
    Phi -->|"More Resources"| MiniCPM
    Qwen -->|"More Resources"| MiniCPM
    MiniCPM -->|"Cloud Deployment"| GPT
```

**Diagram: Model Performance vs. Resource Requirements**

The diagram illustrates the progression from ultra-compact models suitable for mobile devices to high-performance models for cloud deployment, showing the trade-off between resource requirements and accuracy.

**Sources:** [README.md:74-91]()

---

This page provides comprehensive documentation of all models supported by MiniRAG, their performance characteristics, and guidelines for selecting the appropriate model for specific deployment scenarios.

---

# Page: LiHua-World Benchmark

# LiHua-World Benchmark

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [dataset/LiHua-World/qa/query_set.csv](dataset/LiHua-World/qa/query_set.csv)
- [dataset/LiHua-World/qa/query_set.json](dataset/LiHua-World/qa/query_set.json)

</details>



## Purpose and Scope

This document describes the **LiHua-World Benchmark**, a comprehensive evaluation dataset specifically designed for assessing on-device Retrieval-Augmented Generation (RAG) systems in realistic scenarios. LiHua-World provides a year-long chat record from a virtual user named LiHua, annotated with questions requiring single-hop and multi-hop reasoning, along with gold standard answers and supporting evidence.

For information about using this dataset in MiniRAG experiments, see [Usage Examples](#8). For details on the reproduction scripts that use this benchmark, see [Quick Start Guide](#2.2).

**Sources:** [README.md:133-137](), [dataset/LiHua-World/qa/query_set.json:1-100]()

---

## Dataset Structure

### File Organization

LiHua-World is organized within the repository as follows:

```
dataset/LiHua-World/
├── README.md                    # Dataset documentation
├── README_CN.md                 # Chinese documentation
├── data/
│   └── LiHuaWorld.zip          # One year of chat records
└── qa/
    ├── query_set.json          # Questions in JSON format
    └── query_set.csv           # Questions in CSV format
```

**Dataset Location:** [dataset/LiHua-World/data/LiHuaWorld.zip]()

**Query Sets:** [dataset/LiHua-World/qa/query_set.json](), [dataset/LiHua-World/qa/query_set.csv]()

### Evidence Timestamp Format

The dataset uses a specific timestamp format to reference supporting documents within LiHua's chat history:

**Format:** `YYYYMMDD_HH:MM`

**Example:** `20260121_10:00` refers to a conversation on January 21, 2026 at 10:00 AM

Multiple evidence timestamps are concatenated using `<and>` separators:

```
20260121_10:00<and>20260701_10:00<and>20260812_11:00
```

This format allows evaluators to precisely identify which conversations contain the information needed to answer each question.

### Data Format Schema

Both JSON and CSV formats contain identical information. The JSON structure for each question is:

```json
{
  "0": {
    "question": "Question text here",
    "answer": "Answer text or Yes/No",
    "evidence": "timestamp1<and>timestamp2<and>...",
    "type": "Single|Multi"
  }
}
```

#### Dataset File Organization Diagram

```mermaid
graph TB
    DatasetRoot["dataset/LiHua-World/"]
    
    subgraph "Documentation"
        README["README.md<br/>Dataset Description"]
        READMECN["README_CN.md<br/>Chinese Docs"]
    end
    
    subgraph "Raw Data"
        DataDir["data/"]
        ZipFile["LiHuaWorld.zip<br/>One Year Chat Records<br/>YYYYMMDD_HH:MM format"]
    end
    
    subgraph "Query Sets"
        QADir["qa/"]
        JSONFile["query_set.json<br/>640+ Questions<br/>JSON Format"]
        CSVFile["query_set.csv<br/>640+ Questions<br/>CSV Format"]
    end
    
    DatasetRoot --> README
    DatasetRoot --> READMECN
    DatasetRoot --> DataDir
    DatasetRoot --> QADir
    DataDir --> ZipFile
    QADir --> JSONFile
    QADir --> CSVFile
    
    JSONFile -.identical content.-> CSVFile
```

**Sources:** [README.md:96-131](), [dataset/LiHua-World/qa/query_set.json:1-50](), [dataset/LiHua-World/qa/query_set.csv:1-50]()

---

## Question Types and Schema

### Question Type Taxonomy

LiHua-World contains two primary question types, each designed to test different aspects of RAG system capabilities:

| Question Type | Description | Example Count | Complexity |
|--------------|-------------|---------------|------------|
| **Single-hop** | Questions answerable from a single conversation or direct fact | ~320 questions | Low |
| **Multi-hop** | Questions requiring reasoning across multiple conversations or entities | ~320 questions | High |

### Single-Hop Questions

Single-hop questions test basic retrieval and extraction capabilities. They can be answered from information found in one conversation or document.

**Example from Dataset:**

```json
{
  "62": {
    "question": "What time does Li Hua check in with Adam about moving in?",
    "answer": "5:30 PM",
    "evidence": "20260105_14:00",
    "type": "Single"
  }
}
```

**Characteristics:**
- Single evidence timestamp
- Direct factual answers
- Tests basic retrieval accuracy
- Minimal reasoning required

**Additional Examples:**
- [dataset/LiHua-World/qa/query_set.json:377-450]() (Questions 62-72)

### Multi-Hop Questions

Multi-hop questions require the RAG system to:
1. Retrieve information from multiple conversations
2. Connect entities and relationships across documents
3. Perform temporal or logical reasoning
4. Synthesize information from diverse sources

**Example from Dataset:**

```json
{
  "0": {
    "question": "Did Adam Smith send a message to Li Hua about the upcoming building maintenance schedule before the administrators announced a temporary change in the construction schedule due to weather conditions?",
    "answer": "Yes",
    "evidence": "20260121_10:00<and>20260701_10:00",
    "type": "Multi"
  }
}
```

**Characteristics:**
- Multiple evidence timestamps (typically 2-8)
- Temporal reasoning (before/after relationships)
- Entity tracking across conversations
- Complex boolean or comparative answers

**Additional Examples:**
- [dataset/LiHua-World/qa/query_set.json:1-300]() (Questions 0-50)

### Schema Field Definitions

#### Question Schema Structure

```mermaid
graph LR
    Question["Question Entry"]
    
    subgraph "Required Fields"
        QField["question<br/>String<br/>The question text"]
        AField["answer<br/>String<br/>Gold standard answer"]
        EField["evidence<br/>String<br/>Timestamp(s) of<br/>supporting documents"]
        TField["type<br/>Enum<br/>Single | Multi"]
    end
    
    Question --> QField
    Question --> AField
    Question --> EField
    Question --> TField
    
    EField --> EFormat["Format:<br/>YYYYMMDD_HH:MM<br/>Multiple joined by<br/>&lt;and&gt;"]
```

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `question` | String | The evaluation question | "What is the Wi-Fi password at Li Hua's house?" |
| `answer` | String | Human-annotated gold answer | "Family123" |
| `evidence` | String | Timestamp(s) of supporting conversations | "20260106_09:00" or "20260121_10:00<and>20260701_10:00" |
| `type` | String | Question category: "Single" or "Multi" | "Single" |

### Question Distribution Examples

Examining the first 100 questions from the dataset:

| Type | Count (first 100) | Percentage |
|------|-------------------|------------|
| Multi-hop | 62 | 62% |
| Single-hop | 38 | 38% |

**Note:** The dataset also includes a special "Null" type for questions marked as having insufficient information, which are used to test the system's ability to recognize unanswerable queries [dataset/LiHua-World/qa/query_set.csv:574-639]().

#### Question Type Distribution Diagram

```mermaid
graph TB
    Dataset["LiHua-World Dataset<br/>640+ Questions"]
    
    subgraph "Answerable Questions"
        Single["Single-Hop<br/>~320 questions<br/>Direct retrieval<br/>Single evidence"]
        Multi["Multi-Hop<br/>~320 questions<br/>Complex reasoning<br/>Multiple evidence"]
    end
    
    subgraph "Unanswerable Questions"
        Null["Null Type<br/>Insufficient Information<br/>Tests refusal capability"]
    end
    
    Dataset --> Single
    Dataset --> Multi
    Dataset --> Null
    
    Single --> SingleEx["Example:<br/>What is the Wi-Fi password?<br/>Evidence: 20260106_09:00"]
    Multi --> MultiEx["Example:<br/>Did event A occur before B?<br/>Evidence: timestamp1&lt;and&gt;timestamp2"]
    Null --> NullEx["Example:<br/>What did Li Hua eat for dinner<br/>on January 20, 2026?<br/>Evidence: N/A"]
```

**Sources:** [dataset/LiHua-World/qa/query_set.json:1-100](), [dataset/LiHua-World/qa/query_set.csv:1-100](), [dataset/LiHua-World/qa/query_set.csv:574-639]()

---

## Evaluation Methodology

### Evaluation Metrics

LiHua-World uses two primary metrics to assess RAG system performance:

| Metric | Symbol | Description | Calculation |
|--------|--------|-------------|-------------|
| **Accuracy** | acc↑ | Percentage of correct answers | (Correct Answers / Total Questions) × 100% |
| **Error Rate** | err↓ | Percentage of failed responses | (Failed/Error Responses / Total Questions) × 100% |

**Note:** Higher accuracy (↑) is better, while lower error rate (↓) is better.

### Evaluation Pipeline

The evaluation process uses two reproduction scripts located in [reproduce/]():

#### Step 0: Indexing

**Script:** [reproduce/Step_0_index.py]()

1. Loads chat records from `LiHuaWorld.zip`
2. Extracts entities and relationships using MiniRAG
3. Builds the knowledge graph index
4. Stores in specified working directory

```bash
python ./reproduce/Step_0_index.py
```

#### Step 1: Question Answering

**Script:** [reproduce/Step_1_QA.py]()

1. Loads questions from `query_set.json` or `query_set.csv`
2. For each question:
   - Queries the indexed knowledge graph
   - Retrieves relevant contexts
   - Generates answer using LLM
3. Compares generated answers against gold answers
4. Calculates accuracy and error rate metrics

```bash
python ./reproduce/Step_1_QA.py
```

#### Evaluation Workflow Diagram

```mermaid
sequenceDiagram
    participant Script as Step_1_QA.py
    participant Dataset as query_set.json
    participant MiniRAG as MiniRAG System
    participant KG as Knowledge Graph<br/>(from Step_0)
    participant LLM as Language Model
    participant Metrics as Evaluation Metrics
    
    Script->>Dataset: Load questions
    Dataset-->>Script: Return 640+ questions
    
    loop For each question
        Script->>MiniRAG: query(question, mode)
        MiniRAG->>KG: Retrieve contexts<br/>(topology-enhanced)
        KG-->>MiniRAG: Return relevant chunks<br/>+ reasoning paths
        MiniRAG->>LLM: Generate answer<br/>with context
        LLM-->>MiniRAG: Generated answer
        MiniRAG-->>Script: Return answer
        
        Script->>Script: Compare with<br/>gold answer
    end
    
    Script->>Metrics: Calculate accuracy<br/>and error rate
    Metrics-->>Script: Final scores
```

**Sources:** [README.md:64-68](), [README.md:93-94]()

### Baseline Comparison Systems

LiHua-World evaluation compares MiniRAG against three baseline RAG systems:

| System | Approach | Key Features |
|--------|----------|--------------|
| **NaiveRAG** | Simple vector search | Retrieves chunks based on embedding similarity only |
| **GraphRAG** | Graph-based RAG | Requires strong LLMs; often fails with small models |
| **LightRAG** | Lightweight graph RAG | Foundation for MiniRAG; entity-centric retrieval |
| **MiniRAG** | Heterogeneous graph + topology | Optimized for small language models (SLMs) |

**Note:** GraphRAG is marked with "/" (slash) in results tables when it struggles to generate effective responses with small language models [README.md:74-88]().

### Tested Models

Evaluation spans both Small Language Models (SLMs) and Large Language Models (LLMs):

#### Small Language Models (1.5B-4B parameters)
- `Phi-3.5-mini-instruct` (Microsoft)
- `GLM-Edge-1.5B-Chat` (Zhipu AI)
- `Qwen2.5-3B-Instruct` (Alibaba)
- `MiniCPM3-4B` (OpenBMB)

#### Large Language Model (comparison)
- `gpt-4o-mini` (OpenAI)

### Performance Results

#### LiHua-World Benchmark Results

| Model | NaiveRAG | | GraphRAG | | LightRAG | | **MiniRAG** | |
|-------|----------|---|----------|---|----------|---|-------------|---|
| | acc↑ | err↓ | acc↑ | err↓ | acc↑ | err↓ | acc↑ | err↓ |
| Phi-3.5-mini-instruct | 41.22% | 23.20% | / | / | 39.81% | 25.39% | **53.29%** | 23.35% |
| GLM-Edge-1.5B-Chat | 42.79% | 24.76% | / | / | 35.74% | 25.86% | **52.51%** | 25.71% |
| Qwen2.5-3B-Instruct | 43.73% | 24.14% | / | / | 39.18% | 28.68% | **48.75%** | 26.02% |
| MiniCPM3-4B | 43.42% | 17.08% | / | / | 35.42% | 21.94% | **51.25%** | 21.79% |
| gpt-4o-mini | 46.55% | 19.12% | 35.27% | 37.77% | **56.90%** | 20.85% | 54.08% | 19.44% |

**Key Findings:**
- MiniRAG achieves **~13% absolute improvement** over LightRAG baseline with SLMs
- MiniRAG enables SLMs to reach **comparable performance** to LLM-based methods
- GraphRAG fails to generate effective responses with SLMs (marked with "/")
- Error rates remain relatively stable across systems (~20-25%)

#### MultiHop-RAG Benchmark Results

| Model | NaiveRAG | | GraphRAG | | LightRAG | | **MiniRAG** | |
|-------|----------|---|----------|---|----------|---|-------------|---|
| | acc↑ | err↓ | acc↑ | err↓ | acc↑ | err↓ | acc↑ | err↓ |
| Phi-3.5-mini-instruct | 42.72% | 31.34% | / | / | 27.03% | 11.78% | **49.96%** | 28.44% |
| GLM-Edge-1.5B-Chat | 44.44% | 24.26% | / | / | / | / | **51.41%** | 23.44% |
| Qwen2.5-3B-Instruct | 39.48% | 31.69% | / | / | 21.91% | 13.73% | **48.55%** | 33.10% |
| MiniCPM3-4B | 39.24% | 31.42% | / | / | 19.48% | 10.41% | **47.77%** | 26.88% |
| gpt-4o-mini | 53.60% | 27.19% | 60.92% | 16.86% | 64.91% | 19.37% | **68.43%** | 19.41% |

**Key Findings:**
- MiniRAG shows even stronger improvements on multi-hop reasoning tasks
- Some baseline systems completely fail (marked with "/") on certain SLMs
- MiniRAG maintains consistent performance across all tested models

#### Performance Comparison Diagram

```mermaid
graph TB
    subgraph "LiHua-World Benchmark"
        LH_Dataset["LiHua-World<br/>On-Device RAG Scenario<br/>Single + Multi-hop Questions"]
        
        subgraph "Small Language Models"
            SLM_Results["Phi-3.5: 53.29% acc<br/>GLM-Edge: 52.51% acc<br/>Qwen2.5: 48.75% acc<br/>MiniCPM3: 51.25% acc"]
        end
        
        subgraph "Baseline Performance"
            NaiveRAG_LH["NaiveRAG<br/>~41-43% acc<br/>Vector search only"]
            LightRAG_LH["LightRAG<br/>~35-40% acc<br/>Entity-centric"]
            GraphRAG_LH["GraphRAG<br/>Failed ()<br/>Requires strong LLM"]
        end
        
        LH_Dataset --> SLM_Results
        LH_Dataset --> NaiveRAG_LH
        LH_Dataset --> LightRAG_LH
        LH_Dataset --> GraphRAG_LH
    end
    
    subgraph "Key Achievement"
        Improvement["+13% Accuracy<br/>MiniRAG vs LightRAG<br/>on Small Models"]
        Storage["25% Storage Space<br/>vs Traditional Methods"]
    end
    
    SLM_Results --> Improvement
    Improvement --> Storage
    
    subgraph "Evaluation Metrics"
        Accuracy["Accuracy ↑<br/>Correct Answers"]
        ErrorRate["Error Rate ↓<br/>Failed Responses"]
    end
```

### Why MiniRAG Outperforms on LiHua-World

The performance gains on LiHua-World specifically validate MiniRAG's two core innovations:

1. **Heterogeneous Graph Indexing**: Reduces semantic understanding requirements by unifying text chunks and named entities [README.md:31-34]()

2. **Topology-Enhanced Retrieval**: Leverages graph structure for lightweight knowledge discovery without requiring advanced language capabilities [README.md:31-34]()

These innovations are particularly effective on LiHua-World's multi-hop questions, which require reasoning across multiple conversations and entities—precisely the scenario where small language models traditionally struggle.

**Sources:** [README.md:73-88](), [README.md:30-34]()

---

## Summary

LiHua-World provides a rigorous benchmark for evaluating on-device RAG systems with realistic, multi-hop reasoning requirements. The dataset's design—one year of chat records with precisely timestamped evidence—enables fine-grained assessment of how well systems can handle the complex information retrieval and reasoning tasks that occur in real-world on-device scenarios.

**Key Specifications:**
- **Size:** 640+ questions across one year of chat data
- **Question Types:** Single-hop (direct retrieval) and Multi-hop (reasoning)
- **Evaluation:** Accuracy and error rate metrics
- **Benchmark Results:** MiniRAG achieves 53.29% accuracy with small models vs 39.81% baseline

For practical usage of this benchmark in your own experiments, see [Document Indexing](#8.1) and [Question Answering](#8.2).

**Sources:** [README.md:133-137](), [README.md:73-88](), [dataset/LiHua-World/qa/query_set.json:1-3000]()

---

# Page: Dataset Structure

# Dataset Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README_CN.md](README_CN.md)
- [dataset/LiHua-World/qa/query_set.csv](dataset/LiHua-World/qa/query_set.csv)
- [dataset/LiHua-World/qa/query_set.json](dataset/LiHua-World/qa/query_set.json)

</details>



This page explains the structure and organization of the LiHua-World dataset used for evaluating MiniRAG's retrieval and question-answering capabilities. The dataset provides a standardized way to measure performance across different retrieval modes. For information about using the dataset for evaluation, see [Evaluation Methodology](#7.3).

## Overview of LiHua-World Dataset

The LiHua-World dataset is a specialized collection of text-based data designed to test retrieval-augmented generation systems. It consists of two primary components:

1. **Chat Records**: A collection of time-stamped conversations between Li Hua and various characters
2. **Question-Answer Pairs**: A structured set of queries with gold-standard answers and evidence references

```mermaid
flowchart TD
    subgraph "LiHua-World Dataset"
        direction TB
        CR["Chat Records"] --> D["Document Collection"]
        QA["QA Data"] --> QS["query_set.json/csv"]
        
        QS --> |"Contains"| QT["Question Types"]
        QT --> S["Single-hop Questions"]
        QT --> M["Multi-hop Questions"]
        QT --> SU["Summary Questions"]
        
        D --> |"Indexed by"| MR["MiniRAG System"]
        QS --> |"Used to evaluate"| MR
    end
```

Sources: [dataset/LiHua-World/qa/query_set.json](dataset/LiHua-World/qa/query_set.json), [dataset/LiHua-World/qa/query_set.csv](dataset/LiHua-World/qa/query_set.csv)

## Data Components

### Chat Records

The chat records represent a series of conversations formatted as text files with timestamps. Each record follows a naming convention that uses a date and time format: `YYYYMMDD_HH:MM`. These documents form the corpus that MiniRAG indexes and later retrieves from during evaluation.

### Query Set Format

The query set is provided in two formats (JSON and CSV) with identical content. Each query entry contains:

| Field | Description |
|-------|-------------|
| ID | Numeric identifier for the query |
| Question | Natural language question about the chat records |
| Answer | Gold-standard reference answer |
| Evidence | References to specific chat records (in timestamp format) |
| Type | Question type: "Single" or "Multi" |

```mermaid
classDiagram
    class QueryEntry {
        +String questionID
        +String question
        +String answer
        +String evidence
        +String type
    }
    
    class Evidence {
        +String timestamp
        +format: "YYYYMMDD_HH:MM"
    }
    
    class QuestionType {
        +Single: Requires single document
        +Multi: Requires multiple documents
    }
    
    QueryEntry --> Evidence: references
    QueryEntry --> QuestionType: categorized as
```

Sources: [dataset/LiHua-World/qa/query_set.json](dataset/LiHua-World/qa/query_set.json), [dataset/LiHua-World/qa/query_set.csv](dataset/LiHua-World/qa/query_set.csv)

## Question Types

The dataset contains different types of questions, each designed to test different aspects of retrieval and reasoning:

### Single-hop Questions

These questions can be answered by retrieving information from a single document/chat record. They test basic retrieval capabilities.

Example:
```
"What time does Li Hua check in with Adam about moving in?"
Answer: "5:30 PM"
Evidence: "20260105_14:00"
```

### Multi-hop Questions

These questions require the system to retrieve and connect information across multiple documents. They test the system's ability to integrate information from different sources.

Example:
```
"Did Li Hua ask Jennifer for advice on how to prevent muscle soreness after an intense workout session before he told her that he feels soreness in his arm muscles after the workout this week?"
Answer: "Yes"
Evidence: "20260206_16:00<and>20260811_11:00<and>20261008_14:00<and>20261211_11:00"
```

The `<and>` delimiter in the evidence field indicates that multiple documents need to be referenced to answer the question correctly.

Sources: [dataset/LiHua-World/qa/query_set.json](dataset/LiHua-World/qa/query_set.json), [dataset/LiHua-World/qa/query_set.csv](dataset/LiHua-World/qa/query_set.csv)

## Evidence Format

The evidence field uses a specific format to indicate which documents contain information relevant to answering a question:

1. Single document reference: `YYYYMMDD_HH:MM`
2. Multiple document references: `YYYYMMDD_HH:MM<and>YYYYMMDD_HH:MM<and>...`

This structured approach allows for precise evaluation of the system's retrieval capabilities by comparing the documents it retrieves with the gold-standard evidence list.

## Dataset Usage in Evaluation

The dataset integrates with MiniRAG's evaluation pipeline as follows:

```mermaid
flowchart LR
    subgraph "Evaluation Process"
        direction TB
        QSet["Query Set (JSON/CSV)"] --> |"Input"| QA["Step_1_QA.py"]
        ChatRecords["Chat Records"] --> |"Indexed by"| MR["MiniRAG"]
        MR --> |"Used by"| QA
        
        QA --> Light["Light Mode"]
        QA --> Naive["Naive Mode"]
        QA --> Mini["Mini Mode"]
        
        Light --> |"Generates"| Results["Evaluation Results"]
        Naive --> |"Generates"| Results
        Mini --> |"Generates"| Results
    end
```

The query set is processed by the evaluation script, which tests how well MiniRAG can retrieve relevant documents and answer questions across different retrieval modes.

Sources: [dataset/LiHua-World/qa/query_set.json](dataset/LiHua-World/qa/query_set.json), [dataset/LiHua-World/qa/query_set.csv](dataset/LiHua-World/qa/query_set.csv)

## Data Statistics

The LiHua-World dataset contains:

- 639 total questions in the query set
- Multiple question types:
  - Single-hop questions
  - Multi-hop questions
- "Sufficient Information" and "Insufficient Information" questions (the latter marked as "Null" type)
- Temporal questions that test reasoning about event sequences
- Factual questions that test retrieval of specific details

This variety ensures comprehensive evaluation of different aspects of MiniRAG's retrieval and reasoning capabilities.

## Relationship to MiniRAG Architecture

The dataset is designed to work with MiniRAG's storage and retrieval components:

```mermaid
flowchart TD
    subgraph "MiniRAG Components using LiHua-World"
        direction TB
        LHW["LiHua-World Dataset"] --> |"During Indexing"| IP["IndexingPipeline"]
        LHW --> |"During Evaluation"| QP["QueryPipeline"]
        
        IP --> VDB[(Vector Storage)]
        IP --> KV[(KV Storage)]
        IP --> GS[(Graph Storage)]
        
        QP --> |"Retrieves from"| VDB
        QP --> |"Retrieves from"| KV
        QP --> |"Retrieves from"| GS
        
        QP --> |"Generates"| Resp["Response"]
        Resp --> |"Compared with"| Gold["Gold Answer"]
    end
```

The timestamped document IDs in the dataset correspond to keys in the storage systems. During evaluation, the query pipeline retrieves documents based on these IDs to generate answers.

Sources: [dataset/LiHua-World/qa/query_set.json](dataset/LiHua-World/qa/query_set.json), [dataset/LiHua-World/qa/query_set.csv](dataset/LiHua-World/qa/query_set.csv)

## Extending the Dataset

The LiHua-World dataset structure allows for straightforward extension through:

1. Adding new chat records with the same timestamp format
2. Extending the query set with new question-answer pairs
3. Creating new question types to test additional reasoning capabilities

This flexibility makes it a valuable resource for ongoing development and evaluation of retrieval-augmented generation systems like MiniRAG.

---

# Page: Question Types and Schema

# Question Types and Schema

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [dataset/LiHua-World/qa/query_set.csv](dataset/LiHua-World/qa/query_set.csv)
- [dataset/LiHua-World/qa/query_set.json](dataset/LiHua-World/qa/query_set.json)

</details>



This document details the structure and taxonomy of questions in the LiHua-World benchmark dataset. It covers the JSON schema format, the three primary question types (Single-hop, Multi-hop, and Null), and the evidence referencing system used to link questions to supporting documents.

For information about the overall dataset structure and organization, see [Dataset Structure](#7.1). For evaluation methodology and metrics, see [Evaluation Methodology](#7.3).

## Purpose and Scope

The LiHua-World benchmark includes 638 questions designed to test RAG systems across different reasoning complexity levels. Each question follows a standardized schema with explicit type annotations and evidence pointers to support reproducible evaluation. This page documents the question schema, type taxonomy, and the evidence format used to reference source documents.

## Schema Structure

### Core Fields

Each question in the dataset follows a consistent JSON schema with four primary fields:

```mermaid
graph TB
    Question["Question Entry<br/>(Numeric ID)"]
    
    subgraph "Required Fields"
        Q["question<br/>(string)"]
        A["answer<br/>(string)"]
        E["evidence<br/>(string)"]
        T["type<br/>(enum)"]
    end
    
    Question --> Q
    Question --> A
    Question --> E
    Question --> T
    
    T --> Single["Single"]
    T --> Multi["Multi"]
    T --> Null["Null"]
    
    E --> TS["Timestamp References<br/>YYYYMMDD_HH:MM"]
    E --> Sep["Separator: &lt;and&gt;"]
```

**Schema Field Definitions:**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `question` | string | Natural language question text | "Did Adam Smith send a message to Li Hua..." |
| `answer` | string | Gold standard answer | "Yes" / "No" / Specific value |
| `evidence` | string | Timestamp references to supporting documents | "20260121_10:00&lt;and&gt;20260701_10:00" |
| `type` | enum | Question type classification | "Multi" / "Single" / "Null" |

**Sources:** [dataset/LiHua-World/qa/query_set.json:1-10]()

### JSON Structure Example

```json
{
    "0": {
        "question": "Did Adam Smith send a message to Li Hua about the upcoming building maintenance schedule before the administrators announced a temporary change in the construction schedule due to weather conditions?",
        "answer": "Yes",
        "evidence": "20260121_10:00<and>20260701_10:00",
        "type": "Multi"
    },
    "62": {
        "question": "What time does Li Hua check in with Adam about moving in?",
        "answer": "5:30 PM",
        "evidence": "20260105_14:00",
        "type": "Single"
    },
    "574": {
        "question": "What time will Li Hua and Wolfgang meet for breakfast on the morning of the 9th?",
        "answer": "Insufficient information",
        "evidence": "N/A",
        "type": "Null"
    }
}
```

**Sources:** [dataset/LiHua-World/qa/query_set.json:1-7](), [dataset/LiHua-World/qa/query_set.json:375-379](), [dataset/LiHua-World/qa/query_set.json:2296-2301]()

## Question Type Taxonomy

### Type Distribution

```mermaid
graph LR
    Root["LiHua-World<br/>Questions<br/>(638 total)"]
    
    subgraph "Answerable Questions"
        Multi["Multi-hop<br/>Complex Reasoning<br/>~300 questions"]
        Single["Single-hop<br/>Direct Retrieval<br/>~270 questions"]
    end
    
    subgraph "Unanswerable Questions"
        Null["Null Type<br/>Insufficient Info<br/>~68 questions"]
    end
    
    Root --> Multi
    Root --> Single
    Root --> Null
    
    Multi --> Temporal["Temporal Ordering<br/>Before/After Queries"]
    Multi --> Aggregation["Aggregation<br/>Count/List Queries"]
    Multi --> CrossRef["Cross-Reference<br/>Multi-Entity"]
    
    Single --> Factual["Factual<br/>What/Who/When"]
    Single --> Verification["Verification<br/>Yes/No"]
    
    Null --> OutOfScope["Out of Scope"]
    Null --> Ambiguous["Ambiguous"]
```

**Sources:** [dataset/LiHua-World/qa/query_set.json:1-2700]()

### Multi-Hop Questions

Multi-hop questions require reasoning across multiple pieces of evidence. They test the system's ability to traverse the knowledge graph and synthesize information from different temporal contexts.

**Characteristics:**
- Require 2+ evidence timestamps
- Involve temporal reasoning ("before", "after")
- Test relationship tracking across events
- May involve counting or aggregation

**Example Patterns:**

| Pattern | Question Example | Evidence Count |
|---------|-----------------|----------------|
| **Temporal Ordering** | "Did Adam Smith send a message... before the administrators announced..." | 2 |
| **Event Sequence** | "Did Wolfgang arrive in Hong Kong after he informed Li Hua..." | 2 |
| **Aggregation** | "Who wished Li Hua a happy Lunar New Year?" | 3 |
| **Complex Timeline** | "What special offerings did Hailey have... in May?" | 4 |

**Code Mapping:**

```mermaid
graph TB
    MultiQ["Multi-hop Question<br/>type='Multi'"]
    
    MultiQ --> Parse["Question Parsing<br/>extract_entities()"]
    Parse --> Entities["Named Entities<br/>People, Events, Times"]
    
    Entities --> GraphQuery["Graph Traversal<br/>minirag_query()"]
    GraphQuery --> Paths["Reasoning Paths<br/>k-hop neighbors"]
    
    Paths --> Evidence["Evidence Assembly<br/>Multiple Timestamps"]
    Evidence --> Answer["Answer Generation<br/>LLM synthesis"]
    
    style MultiQ fill:#f9f9f9
    style GraphQuery fill:#f9f9f9
```

**Sources:** [dataset/LiHua-World/qa/query_set.json:1-7](), [dataset/LiHua-World/qa/query_set.json:26-31](), [dataset/LiHua-World/qa/query_set.json:188-193]()

### Single-Hop Questions

Single-hop questions can be answered from a single piece of evidence. They test direct retrieval capabilities without complex reasoning.

**Characteristics:**
- Require exactly 1 evidence timestamp
- Direct factual queries
- No temporal reasoning required
- Test precision of retrieval

**Example Patterns:**

| Pattern | Question Example | Answer Type |
|---------|-----------------|-------------|
| **Time Query** | "What time does Li Hua check in with Adam about moving in?" | Time value |
| **Location Query** | "What is the name of the café..." | Place name |
| **Person Query** | "Who suggested Li Hua keep a clear log..." | Person name |
| **Object Query** | "What is the Wi-Fi password at Li Hua's house?" | String value |
| **Yes/No** | "Can Li Hua hang his artworks on the wall?" | Boolean |

**Code Mapping:**

```mermaid
graph TB
    SingleQ["Single-hop Question<br/>type='Single'"]
    
    SingleQ --> VectorSearch["Vector Search<br/>naive/light mode"]
    VectorSearch --> Chunk["Text Chunk<br/>Single document"]
    
    Chunk --> Extract["Information Extract<br/>Direct answer"]
    Extract --> Answer["Answer Generation<br/>Straightforward"]
    
    style SingleQ fill:#f9f9f9
    style VectorSearch fill:#f9f9f9
```

**Sources:** [dataset/LiHua-World/qa/query_set.json:375-379](), [dataset/LiHua-World/qa/query_set.json:391-395](), [dataset/LiHua-World/qa/query_set.json:519-523]()

### Null Type Questions

Null type questions are designed to be unanswerable based on the available dataset. They test the system's ability to recognize information gaps.

**Characteristics:**
- Answer: "Insufficient information"
- Evidence: "N/A"
- No supporting documents exist
- Test system's ability to avoid hallucination

**Example Patterns:**

| Pattern | Question Example | Why Unanswerable |
|---------|-----------------|------------------|
| **Missing Detail** | "What time will Li Hua and Wolfgang meet for breakfast on the morning of the 9th?" | Specific detail not recorded |
| **Undefined Context** | "What type of equipment does Wolfgang use at the gym?" | Information never mentioned |
| **Out of Scope** | "What payment method did Li Hua use to purchase groceries..." | Transaction details not tracked |
| **Ambiguous Reference** | "What specific suggestions did Li Hua have regarding the construction schedule..." | Vague reference |

**Sources:** [dataset/LiHua-World/qa/query_set.json:2296-2301](), [dataset/LiHua-World/qa/query_set.json:2302-2307](), [dataset/LiHua-World/qa/query_set.csv:575-640]()

## Evidence Format and Referencing

### Timestamp Format

Evidence references use a standardized timestamp format that maps directly to chat record files in the LiHua-World dataset.

**Format:** `YYYYMMDD_HH:MM`

```mermaid
graph LR
    TS["Timestamp<br/>20260121_10:00"]
    
    TS --> Date["Date Component<br/>20260121"]
    TS --> Time["Time Component<br/>10:00"]
    
    Date --> Y["Year: 2026"]
    Date --> M["Month: 01"]
    Date --> D["Day: 21"]
    
    Time --> H["Hour: 10"]
    Time --> Min["Minute: 00"]
    
    TS --> File["Maps to Chat Record<br/>January 21, 2026 10:00 AM"]
```

**Components:**

| Component | Format | Example | Description |
|-----------|--------|---------|-------------|
| Year | YYYY | 2026 | Four-digit year |
| Month | MM | 01 | Two-digit month (01-12) |
| Day | DD | 21 | Two-digit day (01-31) |
| Hour | HH | 10 | Two-digit hour (00-23) |
| Minute | MM | 00 | Two-digit minute (00-59) |

**Sources:** [dataset/LiHua-World/qa/query_set.json:5]()

### Multiple Evidence References

Multi-hop questions link multiple evidence timestamps using the `<and>` separator.

**Syntax:** `timestamp1<and>timestamp2<and>timestamp3`

```mermaid
graph LR
    Q["Question:<br/>Multi-hop"]
    
    Q --> E["evidence field"]
    
    E --> E1["20260121_10:00"]
    E --> Sep1["&lt;and&gt;"]
    E --> E2["20260204_15:00"]
    E --> Sep2["&lt;and&gt;"]
    E --> E3["20260701_10:00"]
    
    E1 --> Doc1["Chat Record 1<br/>Jan 21 10:00"]
    E2 --> Doc2["Chat Record 2<br/>Feb 4 15:00"]
    E3 --> Doc3["Chat Record 3<br/>Jul 1 10:00"]
    
    Doc1 --> Answer["Combined Context<br/>for Reasoning"]
    Doc2 --> Answer
    Doc3 --> Answer
```

**Examples:**

| Evidence String | Document Count | Question Type |
|----------------|----------------|---------------|
| `20260105_14:00` | 1 | Single-hop |
| `20260121_10:00<and>20260701_10:00` | 2 | Multi-hop |
| `20260119_11:30<and>20260119_14:30<and>20260119_09:30` | 3 | Multi-hop aggregation |
| `20260206_16:00<and>20260811_11:00<and>20261008_14:00<and>20261211_11:00` | 4 | Complex multi-hop |

**Sources:** [dataset/LiHua-World/qa/query_set.json:5](), [dataset/LiHua-World/qa/query_set.json:22-24](), [dataset/LiHua-World/qa/query_set.json:191]()

### Evidence-to-Code Mapping

```mermaid
graph TB
    Evidence["evidence field<br/>20260121_10:00"]
    
    Evidence --> Parse["Timestamp Parser<br/>extract date/time"]
    
    Parse --> Lookup["Document Lookup<br/>BaseKVStorage.get()"]
    
    Lookup --> Chunk["Text Chunk<br/>full_doc storage"]
    
    Chunk --> Context["Context for LLM<br/>openai_complete()"]
    
    subgraph "Storage Layer"
        KV["BaseKVStorage<br/>chunks_vdb"]
        Graph["BaseGraphStorage<br/>entity relationships"]
    end
    
    Lookup --> KV
    Lookup --> Graph
    
    style Evidence fill:#f9f9f9
    style Lookup fill:#f9f9f9
```

**Sources:** [dataset/LiHua-World/qa/query_set.json:5]()

## Question Characteristics

### Temporal Reasoning Patterns

Multi-hop questions often involve explicit temporal reasoning keywords:

| Keyword | Count | Example |
|---------|-------|---------|
| "before" | ~40 | "Did X happen before Y?" |
| "after" | ~30 | "Did X occur after Y?" |
| "between" | ~15 | "Time interval between X and Y" |
| "during" | ~10 | "Who did X during period Y?" |

**Sources:** [dataset/LiHua-World/qa/query_set.json:1-200]()

### Entity-Centric Questions

Questions focus on core entities in the LiHua-World narrative:

```mermaid
graph TB
    Questions["Question Types"]
    
    subgraph "Primary Entities"
        LH["Li Hua<br/>Protagonist"]
        WS["Wolfgang Schulz<br/>Friend"]
        AS["Adam Smith<br/>Landlord"]
        JM["Jennifer Moore<br/>Trainer"]
    end
    
    subgraph "Secondary Entities"
        YY["Yuriko Yamamoto"]
        CS["Chae Song-hwa"]
        HJ["Hailey Johnson"]
        JW["Jake Watson"]
    end
    
    Questions --> LH
    Questions --> WS
    Questions --> AS
    Questions --> JM
    Questions --> YY
    Questions --> CS
    Questions --> HJ
    Questions --> JW
    
    LH --> Events["Events:<br/>Work, Fitness, Social"]
    WS --> Events
    JM --> Training["Training Sessions"]
    AS --> Rent["Rent & Maintenance"]
```

**Entity Frequency in Questions:**

| Entity | Mention Count | Primary Role |
|--------|--------------|--------------|
| Li Hua | ~500 | Main protagonist |
| Wolfgang Schulz | ~120 | Friend, coworker |
| Jennifer Moore | ~80 | Fitness trainer |
| Adam Smith | ~60 | Landlord |
| Yuriko Yamamoto | ~40 | Client, musician |

**Sources:** [dataset/LiHua-World/qa/query_set.json:1-2700]()

### Answer Type Distribution

```mermaid
graph TB
    Answers["Answer Types"]
    
    Answers --> Bool["Boolean<br/>Yes/No<br/>~150 questions"]
    Answers --> Person["Person Names<br/>~100 questions"]
    Answers --> Time["Dates/Times<br/>~80 questions"]
    Answers --> Place["Places/Locations<br/>~40 questions"]
    Answers --> Event["Events/Actions<br/>~120 questions"]
    Answers --> Number["Numeric Values<br/>~30 questions"]
    Answers --> Text["Text/Strings<br/>~50 questions"]
    Answers --> Null["Insufficient Info<br/>~68 questions"]
```

**Sources:** [dataset/LiHua-World/qa/query_set.json:1-2700]()

## CSV Format

The dataset is also available in CSV format with identical information:

**Column Schema:**

| Column | Description | JSON Equivalent |
|--------|-------------|-----------------|
| Question | Natural language question | `question` field |
| Gold Answer | Correct answer | `answer` field |
| Evidence | Timestamp references | `evidence` field |
| Type | Question type | `type` field |

**Sources:** [dataset/LiHua-World/qa/query_set.csv:1-2]()

## Usage in Evaluation

### Question Processing Pipeline

```mermaid
graph TB
    QSet["query_set.json<br/>Load Questions"]
    
    QSet --> Parse["Parse Question<br/>Extract type & evidence"]
    
    Parse --> Route{Question Type?}
    
    Route -->|Single| Naive["naive_query()<br/>Simple retrieval"]
    Route -->|Multi| Mini["minirag_query()<br/>Graph traversal"]
    Route -->|Null| Test["Test hallucination<br/>detection"]
    
    Naive --> Eval["Evaluate Answer<br/>calculate_similarity()"]
    Mini --> Eval
    Test --> Eval
    
    Eval --> Metrics["Accuracy & Error Rate<br/>See Section 7.3"]
    
    style QSet fill:#f9f9f9
    style Route fill:#f9f9f9
    style Eval fill:#f9f9f9
```

**Sources:** [dataset/LiHua-World/qa/query_set.json:1-10]()

### Type-Specific Evaluation

Different question types are evaluated separately to measure performance across reasoning complexity levels:

| Type | Evaluation Focus | Key Metric |
|------|-----------------|------------|
| Single | Retrieval precision | Exact match accuracy |
| Multi | Reasoning capability | Multi-hop accuracy |
| Null | Hallucination detection | False positive rate |

**Sources:** [dataset/LiHua-World/qa/query_set.json:1-2700]()

---

# Page: Evaluation Methodology

# Evaluation Methodology

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [reproduce/Step_0_index.py](reproduce/Step_0_index.py)
- [reproduce/Step_1_QA.py](reproduce/Step_1_QA.py)

</details>



This page describes the methodology used to evaluate MiniRAG's performance, covering the benchmarking process, evaluation metrics, and comparison protocols. For information about the dataset structure used in evaluation, see [Dataset Structure](#7.1), and for details about the different question types used in testing, see [Question Types](#7.2).

## Overview of Evaluation Approach

MiniRAG's evaluation methodology is designed to assess how effectively small language models (SLMs) can perform retrieval-augmented generation tasks when equipped with MiniRAG's heterogeneous graph indexing and topology-enhanced retrieval capabilities. The evaluation process consists of two main phases: document indexing and question answering, followed by performance measurement against gold standard answers.

```mermaid
flowchart TB
    subgraph "Evaluation Process"
        direction LR
        DatasetPrep["Dataset Preparation<br>LiHua-World"]
        Indexing["Document Indexing<br>(Step_0_index.py)"]
        QA["Question Answering<br>(Step_1_QA.py)"]
        Metrics["Performance Metrics<br>Accuracy & Error Rate"]
        
        DatasetPrep --> Indexing
        Indexing --> QA
        QA --> Metrics
    end
    
    subgraph "Query Modes"
        direction TB
        NaiveMode["naive mode<br>Vector-only retrieval"]
        LightMode["light mode<br>Hybrid retrieval"]
        MiniMode["mini mode<br>Full MiniRAG retrieval"]
    end
    
    QA --> NaiveMode
    QA --> LightMode
    QA --> MiniMode
    
    NaiveMode --> Metrics
    LightMode --> Metrics
    MiniMode --> Metrics
```

Sources: [README.md:34-36](), [reproduce/Step_0_index.py](), [reproduce/Step_1_QA.py]()

## Evaluation Dataset

MiniRAG is evaluated using the LiHua-World dataset, which contains one year of chat records from a virtual user named LiHua. This dataset is specifically designed for on-device RAG scenarios and includes three question types:

1. **Single-hop questions**: Require retrieving information from a single document
2. **Multi-hop questions**: Require synthesizing information from multiple documents
3. **Summary questions**: Require summarizing information across multiple documents

The dataset provides manually annotated gold standard answers for each question to enable objective evaluation.

Sources: [README.md:130-134]()

## Evaluation Process

### Document Indexing Phase

The first step in the evaluation process is document indexing, which is handled by the `Step_0_index.py` script. This script:

1. Initializes a MiniRAG instance with the specified language model and embedding model
2. Recursively finds all text files in the dataset directory
3. Inserts each document into the MiniRAG system, which builds the heterogeneous graph index

```mermaid
flowchart LR
    subgraph "Indexing Process"
        direction TB
        DataDir["Dataset Directory<br>LiHua-World"]
        TXTFiles["Text Files<br>(.txt)"]
        MiniRAGIndex["MiniRAG Insert<br>rag.insert()"]
        HetGraph["Heterogeneous Graph<br>Construction"]
        
        DataDir --> TXTFiles
        TXTFiles --> MiniRAGIndex
        MiniRAGIndex --> HetGraph
    end
    
    subgraph "Components"
        EmbeddingModel["Embedding Model<br>all-MiniLM-L6-v2"]
        LLMModel["LLM Model<br>(PHI/GLM/MiniCPM/Qwen)"]
    end
    
    EmbeddingModel --> MiniRAGIndex
    LLMModel --> MiniRAGIndex
```

Sources: [reproduce/Step_0_index.py:80-97]()

### Question Answering Phase

After indexing, the `Step_1_QA.py` script performs the question answering evaluation:

1. Reads questions and gold answers from the query CSV file
2. For each question, queries the MiniRAG system using the "mini" mode
3. Records the MiniRAG answer alongside the question and gold answer in an output CSV file

The script processes questions sequentially and handles any errors that may occur during the querying process.

Sources: [reproduce/Step_1_QA.py:92-134]()

## Evaluation Metrics

MiniRAG's performance is evaluated using two primary metrics:

1. **Accuracy (acc↑)**: The percentage of questions for which the system provides a correct answer. Higher is better.
2. **Error Rate (err↓)**: The percentage of answers containing factual errors or hallucinations. Lower is better.

These metrics allow for comprehensive assessment of both the system's ability to retrieve relevant information and its accuracy in generating answers.

```mermaid
flowchart LR
    subgraph "Evaluation Metrics"
        AccuracyMetric["Accuracy (acc↑)<br>Percentage of correct answers"]
        ErrorMetric["Error Rate (err↓)<br>Percentage of factual errors"]
    end
    
    subgraph "Comparison Framework"
        MiniRAG["MiniRAG"]
        NaiveRAG["NaiveRAG"]
        GraphRAG["GraphRAG"]
        LightRAG["LightRAG"]
    end
    
    MiniRAG --> AccuracyMetric
    MiniRAG --> ErrorMetric
    
    NaiveRAG --> AccuracyMetric
    NaiveRAG --> ErrorMetric
    
    GraphRAG --> AccuracyMetric
    GraphRAG --> ErrorMetric
    
    LightRAG --> AccuracyMetric
    LightRAG --> ErrorMetric
```

Sources: [README.md:70-85]()

## Query Modes and Comparison

MiniRAG supports three query modes, each corresponding to a different retrieval approach:

1. **Naive mode**: Uses only vector-based retrieval
2. **Light mode**: Uses hybrid retrieval combining vector search with entity-based retrieval
3. **Mini mode**: Uses full MiniRAG topology-enhanced retrieval

The evaluation framework compares these modes against other RAG systems:

| System | Retrieval Method | Description |
|--------|------------------|-------------|
| NaiveRAG | Vector-only | Traditional RAG using only vector embeddings |
| GraphRAG | Graph-based | Uses knowledge graphs but with more complex query mechanisms |
| LightRAG | Hybrid | Lightweight RAG with simplified hybrid retrieval |
| MiniRAG | Topology-enhanced | Uses heterogeneous graph indexing with topology-enhanced retrieval |

Sources: [README.md:70-85](), [reproduce/Step_1_QA.py:119]()

## Language Models Evaluation

The evaluation methodology tests MiniRAG with various small language models to demonstrate its effectiveness across different model sizes and architectures:

1. **Phi-3.5-mini-instruct**: Microsoft's small instruction-tuned model
2. **GLM-Edge-1.5B-Chat**: THUDM's edge-optimized chat model
3. **Qwen2.5-3B-Instruct**: Qwen's instruction-tuned model
4. **MiniCPM3-4B**: OpenBMB's compact model
5. **gpt-4o-mini**: OpenAI's smaller version of GPT-4o

This diverse set of models allows for comprehensive evaluation across different model capabilities and sizes.

```mermaid
flowchart TB
    subgraph "Model Selection Process"
        direction LR
        ModelArg["Command Line Arg<br>--model"]
        ModelSelection{{"Model Selection"}}
        Phi["microsoft/Phi-3.5-mini-instruct"]
        GLM["THUDM/glm-edge-1.5b-chat"]
        MiniCPM["openbmb/MiniCPM3-4B"]
        Qwen["Qwen/Qwen2.5-3B-Instruct"]
    end
    
    ModelArg --> ModelSelection
    ModelSelection -->|"--model=PHI"| Phi
    ModelSelection -->|"--model=GLM"| GLM
    ModelSelection -->|"--model=MiniCPM"| MiniCPM
    ModelSelection -->|"--model=qwen"| Qwen
    
    subgraph "Evaluation"
        MiniRAG["MiniRAG System"]
        QAProcess["Question Answering<br>Process"]
        PerformanceMetrics["Performance<br>Metrics"]
    end
    
    Phi --> MiniRAG
    GLM --> MiniRAG
    MiniCPM --> MiniRAG
    Qwen --> MiniRAG
    
    MiniRAG --> QAProcess
    QAProcess --> PerformanceMetrics
```

Sources: [reproduce/Step_0_index.py:40-50](), [reproduce/Step_1_QA.py:42-52]()

## Running Evaluations

The evaluation can be reproduced using the following steps:

1. **Setup**: Ensure the LiHua-World dataset is placed in the `./dataset/LiHua-World/data/` directory
2. **Indexing**: Run `python ./reproduce/Step_0_index.py` with appropriate arguments
3. **Question Answering**: Run `python ./reproduce/Step_1_QA.py` with matching arguments

### Command Line Arguments

Both scripts accept the following arguments:

| Argument | Description | Default Value |
|----------|-------------|---------------|
| `--model` | LLM model to use (PHI, GLM, MiniCPM, qwen) | PHI |
| `--outputpath` | Path for the output CSV file | ./logs/Default_output.csv |
| `--workingdir` | Working directory for MiniRAG | ./LiHua-World |
| `--datapath` | Path to the dataset files | ./dataset/LiHua-World/data/ |
| `--querypath` | Path to the query set file | ./dataset/LiHua-World/qa/query_set.csv |

This standardized approach ensures consistent and reproducible evaluation across different models and configurations.

Sources: [reproduce/Step_0_index.py:23-35](), [reproduce/Step_1_QA.py:26-37]()

## Performance Comparison

The evaluation methodology enables fair comparison between MiniRAG and other RAG systems across different language models. The results demonstrate MiniRAG's effectiveness, particularly when used with small language models.

For the LiHua-World dataset, MiniRAG achieves significantly higher accuracy compared to other RAG approaches when using small models like Phi-3.5-mini-instruct (53.29% vs. 41.22% for NaiveRAG), while maintaining comparable error rates.

For the MultiHop-RAG dataset, which contains more complex multi-hop questions, MiniRAG shows even more pronounced improvements, with accuracy gains of up to 28.29 percentage points over competing approaches when using small language models.

Sources: [README.md:70-85]()

---

# Page: Usage Examples

# Usage Examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [main.py](main.py)
- [minirag/prompt.py](minirag/prompt.py)
- [reproduce/Step_0_index.py](reproduce/Step_0_index.py)
- [reproduce/Step_1_QA.py](reproduce/Step_1_QA.py)

</details>



This page provides practical examples of common MiniRAG operations. MiniRAG follows a two-phase workflow: document indexing (Phase 1) and question answering (Phase 2). The examples demonstrate how to use both the reproduction scripts and the programmatic API.

## Overview

MiniRAG provides two usage patterns:

| Usage Pattern | Description | Best For |
|--------------|-------------|----------|
| **Reproduction Scripts** | `Step_0_index.py` and `Step_1_QA.py` in the `reproduce/` directory | Benchmarking on LiHua-World dataset |
| **Programmatic API** | Direct use of `MiniRAG` class with `insert()` and `query()` methods | Custom applications and integration |

This page is organized into three sections:
- **Document Indexing (Page 8.1)**: Using `insert()` to build the knowledge graph
- **Question Answering (Page 8.2)**: Using `query()` with different `QueryParam` modes
- **Custom Workflows (Page 8.3)**: Advanced usage patterns and error handling

For system architecture details, see Page 3. For installation, see Page 2.

## MiniRAG Initialization Pattern

### Code Entity Mapping: Initialization Components

The following diagram maps the initialization process to specific code constructs:

```mermaid
flowchart TB
    subgraph "Initialization in Code"
        MiniRAGClass["MiniRAG class<br/>minirag/minirag.py"]
        
        subgraph "Required Parameters"
            WorkingDir["working_dir: str<br/>Storage location"]
            LLMFunc["llm_model_func: Callable<br/>hf_model_complete or gpt_4o_mini_complete"]
            LLMName["llm_model_name: str<br/>Model identifier"]
            LLMMaxToken["llm_model_max_token_size: int<br/>Token limit"]
            EmbedFunc["embedding_func: EmbeddingFunc<br/>minirag/utils.py"]
        end
        
        subgraph "EmbeddingFunc Dataclass"
            EmbedDim["embedding_dim: int<br/>Vector dimension"]
            MaxToken["max_token_size: int<br/>Chunk size"]
            Func["func: Callable<br/>hf_embed function"]
        end
        
        MiniRAGClass --> WorkingDir
        MiniRAGClass --> LLMFunc
        MiniRAGClass --> LLMName
        MiniRAGClass --> LLMMaxToken
        MiniRAGClass --> EmbedFunc
        
        EmbedFunc --> EmbedDim
        EmbedFunc --> MaxToken
        EmbedFunc --> Func
    end
```

Sources: [main.py:58-72](), [reproduce/Step_0_index.py:63-78](), [reproduce/Step_1_QA.py:65-80]()

### Standard Initialization Example

All examples follow this initialization pattern defined in [main.py:58-72](), [reproduce/Step_0_index.py:63-78](), and [reproduce/Step_1_QA.py:65-80](). Key components:

- **`MiniRAG` constructor**: Orchestrates the entire system
- **`working_dir`**: Persistent directory for graph, vector, and KV storage
- **`llm_model_func`**: Function pointer to `hf_model_complete` or `gpt_4o_mini_complete`
- **`llm_model_name`**: Model identifier (e.g., `"microsoft/Phi-3.5-mini-instruct"`)
- **`embedding_func`**: `EmbeddingFunc` dataclass wrapping `hf_embed` with tokenizer and model

### Supported LLM Models

MiniRAG supports multiple Small Language Models defined in [main.py:35-45](), [reproduce/Step_0_index.py:40-50](), [reproduce/Step_1_QA.py:42-52]():

| Model Argument | Model Path | Parameters |
|----------------|-----------|-----------|
| `PHI` | `microsoft/Phi-3.5-mini-instruct` | ~3.8B |
| `GLM` | `THUDM/glm-edge-1.5b-chat` | 1.5B |
| `MiniCPM` | `openbmb/MiniCPM3-4B` | 4B |
| `qwen` | `Qwen/Qwen2.5-3B-Instruct` | 3B |

Sources: [main.py:35-51](), [reproduce/Step_0_index.py:40-51](), [reproduce/Step_1_QA.py:42-52]()

## Document Indexing Workflow

### Code Entity Mapping: Indexing Pipeline

The document indexing process uses the following code constructs:

```mermaid
flowchart TB
    subgraph "File Discovery"
        FindFiles["find_txt_files()<br/>main.py:76-82"]
        OSWalk["os.walk()<br/>Python stdlib"]
        FileList["txt_files: List[str]<br/>File paths"]
        
        FindFiles --> OSWalk
        OSWalk --> FileList
    end
    
    subgraph "Document Processing Loop"
        Loop["for WEEK in WEEK_LIST<br/>main.py:86-90"]
        ReadFile["open(WEEK).read()<br/>Python I/O"]
        InsertMethod["rag.insert(text)<br/>MiniRAG.insert()"]
        
        Loop --> ReadFile
        ReadFile --> InsertMethod
    end
    
    subgraph "Internal Processing"
        ChunkText["Text chunking<br/>minirag/utils.py"]
        ExtractEntities["Entity extraction<br/>minirag/operate.py"]
        StoreGraph["Store to graph_storage<br/>BaseGraphStorage"]
        StoreVector["Store to vector_db<br/>BaseVectorStorage"]
        StoreKV["Store to kv_storage<br/>BaseKVStorage"]
        
        InsertMethod --> ChunkText
        ChunkText --> ExtractEntities
        ExtractEntities --> StoreGraph
        ExtractEntities --> StoreVector
        ExtractEntities --> StoreKV
    end
    
    FileList --> Loop
```

Sources: [main.py:76-90](), [reproduce/Step_0_index.py:82-96]()

### Implementation Details

The indexing implementation follows this pattern:

1. **File Discovery**: `find_txt_files()` utility at [main.py:76-82]() and [reproduce/Step_0_index.py:82-88]() uses `os.walk()` to locate all `.txt` files recursively

2. **Iteration**: Loop at [main.py:86-90]() and [reproduce/Step_0_index.py:91-96]() processes each file sequentially

3. **Insertion**: `rag.insert(text)` method accepts raw text strings and handles:
   - Text chunking into manageable segments
   - Entity extraction using prompts from [minirag/prompt.py:13-118]()
   - Storage in graph, vector, and key-value backends

### LiHua-World Dataset Structure

The reproduction scripts use the LiHua-World benchmark dataset organized as:

```
dataset/LiHua-World/
├── data/              # Text files (chat records)
│   ├── week_01.txt
│   ├── week_02.txt
│   └── ...
└── qa/                # Question sets
    ├── query_set.csv
    └── query_set.json
```

The `DATA_PATH` variable at [main.py:48](), [reproduce/Step_0_index.py:53](), and [reproduce/Step_1_QA.py:55]() points to `./dataset/LiHua-World/data/`.

For detailed indexing examples, see Page 8.1.

Sources: [main.py:24-90](), [reproduce/Step_0_index.py:29-96]()

## Question Answering Workflow

### Code Entity Mapping: Query Pipeline

The query process maps to these code constructs:

```mermaid
flowchart TB
    subgraph "Query Entry Point"
        QueryMethod["rag.query(question, param)<br/>MiniRAG.query()"]
        QueryParamClass["QueryParam dataclass<br/>mode: str"]
        
        QueryMethod --> QueryParamClass
    end
    
    subgraph "Query Modes"
        ModeSwitch["Mode selection<br/>minirag/operate.py"]
        
        MiniMode["mode='mini'<br/>minirag_query()<br/>Topology-enhanced retrieval"]
        NaiveMode["mode='naive'<br/>naive_query()<br/>Vector similarity only"]
        LightMode["mode='light'<br/>lightrag_query()<br/>Hybrid approach"]
        HybridMode["mode='hybrid'<br/>hybrid_query()<br/>Combined strategies"]
        GlobalMode["mode='global'<br/>global_query()<br/>Full graph search"]
        
        QueryParamClass --> ModeSwitch
        ModeSwitch --> MiniMode
        ModeSwitch --> NaiveMode
        ModeSwitch --> LightMode
        ModeSwitch --> HybridMode
        ModeSwitch --> GlobalMode
    end
    
    subgraph "Response Generation"
        ExtractKeywords["Extract keywords<br/>minirag/prompt.py:159-305"]
        RetrieveContext["Retrieve from storage<br/>graph_storage/vector_db"]
        ConstructPrompt["Build prompt<br/>minirag/prompt.py:315-335"]
        LLMCall["llm_model_func()<br/>hf_model_complete"]
        
        MiniMode --> ExtractKeywords
        ExtractKeywords --> RetrieveContext
        RetrieveContext --> ConstructPrompt
        ConstructPrompt --> LLMCall
    end
```

Sources: [main.py:93-96](), [reproduce/Step_1_QA.py:118-122](), [minirag/prompt.py:159-335]()

### Single Query Example

Basic query invocation at [main.py:93-96]():

- **Query string**: User question as `str`
- **`QueryParam`**: Configuration object with `mode` field
- **Return value**: Generated answer as `str`

Example query: `'What does LiHua predict will happen in "The Rings of Power"?'`

The query is processed with `QueryParam(mode="mini")` to use topology-enhanced retrieval.

### Batch Processing Pattern

The batch processing implementation at [reproduce/Step_1_QA.py:85-128]() demonstrates:

| Component | Implementation | Location |
|-----------|---------------|----------|
| **CSV Loading** | `csv.DictReader` | [reproduce/Step_1_QA.py:85-89]() |
| **Progress Tracking** | `tqdm.trange` | [reproduce/Step_1_QA.py:110]() |
| **Error Handling** | `try-except` block | [reproduce/Step_1_QA.py:117-125]() |
| **Result Logging** | `csv.writer.writerow` | [reproduce/Step_1_QA.py:127]() |

The script loads questions from `QUERY_PATH` variable defined at [reproduce/Step_1_QA.py:56](), which defaults to `./dataset/LiHua-World/qa/query_set.csv`.

### QueryParam Modes

The five query modes are defined in the `operate.py` module:

1. **`mode="mini"`**: MiniRAG's core topology-enhanced retrieval using graph structure
2. **`mode="naive"`**: Simple vector similarity search without graph
3. **`mode="light"`**: LightRAG-style entity-centric retrieval
4. **`mode="hybrid"`**: Combines multiple retrieval strategies
5. **`mode="global"`**: Full knowledge graph search

For detailed query examples and mode comparisons, see Page 8.2.

Sources: [reproduce/Step_1_QA.py:82-128](), [main.py:93-97]()

## Experiment Execution Pattern

### Reproduction Scripts Workflow

The reproduction scripts implement a complete benchmarking pipeline:

```mermaid
flowchart LR
    subgraph "Step 0: Indexing"
        S0Script["Step_0_index.py"]
        S0Index["rag.insert()"]
        S0Storage["Build storage in<br/>working_dir"]
        
        S0Script --> S0Index
        S0Index --> S0Storage
    end
    
    subgraph "Step 1: Question Answering"
        S1Script["Step_1_QA.py"]
        S1Load["Load query_set.csv"]
        S1Query["rag.query()"]
        S1Log["Write to output.csv"]
        
        S1Script --> S1Load
        S1Load --> S1Query
        S1Query --> S1Log
    end
    
    S0Storage --> S1Query
```

Sources: [reproduce/Step_0_index.py:1-97](), [reproduce/Step_1_QA.py:1-135]()

### Command-Line Arguments

Both scripts accept the same argument structure defined using `argparse.ArgumentParser`:

| Argument | Default | Description |
|----------|---------|-------------|
| `--model` | `"PHI"` | LLM model selection (PHI/GLM/MiniCPM/qwen) |
| `--workingdir` | `"./LiHua-World"` | Persistent storage directory |
| `--datapath` | `"./dataset/LiHua-World/data/"` | Input documents (Step_0 only) |
| `--querypath` | `"./dataset/LiHua-World/qa/query_set.csv"` | Question set (Step_1 only) |
| `--outputpath` | `"./logs/Default_output.csv"` | Results log (Step_1 only) |

Argument parsing is implemented at [reproduce/Step_0_index.py:24-36]() and [reproduce/Step_1_QA.py:26-36]().

### Experiment Function Structure

The `run_experiment()` function at [reproduce/Step_1_QA.py:92-129]() implements:

1. **Resume Capability**: Checks existing output file at [reproduce/Step_1_QA.py:96-100]() to skip already-processed questions
2. **Incremental Logging**: Appends results using `mode="a"` at [reproduce/Step_1_QA.py:105]()
3. **Error Handling**: Catches exceptions at [reproduce/Step_1_QA.py:117-125]() and logs `"Error"` string
4. **Progress Display**: Uses `trange()` at [reproduce/Step_1_QA.py:110]() for visual progress bar

The output CSV contains three columns defined in the `headers` list at [reproduce/Step_1_QA.py:93]():
- `"Question"`: Input query
- `"Gold Answer"`: Reference answer from dataset
- `"minirag"`: Generated answer from MiniRAG

Sources: [reproduce/Step_1_QA.py:92-134]()

## Script Execution Examples

### Running Step_0_index.py

Index the LiHua-World dataset with Phi-3.5 model:

```bash
python reproduce/Step_0_index.py \
    --model PHI \
    --workingdir ./LiHua-World \
    --datapath ./dataset/LiHua-World/data/
```

This script:
1. Discovers all `.txt` files in `--datapath` using [reproduce/Step_0_index.py:82-88]()
2. Initializes MiniRAG with specified model at [reproduce/Step_0_index.py:63-78]()
3. Calls `rag.insert()` for each file at [reproduce/Step_0_index.py:91-96]()
4. Stores graph/vector/KV data in `--workingdir`

### Running Step_1_QA.py

Execute question answering on indexed data:

```bash
python reproduce/Step_1_QA.py \
    --model PHI \
    --workingdir ./LiHua-World \
    --querypath ./dataset/LiHua-World/qa/query_set.csv \
    --outputpath ./logs/phi_results.csv
```

This script:
1. Loads MiniRAG from existing `--workingdir` at [reproduce/Step_1_QA.py:65-80]()
2. Reads questions from `--querypath` at [reproduce/Step_1_QA.py:85-89]()
3. Queries with `mode="mini"` at [reproduce/Step_1_QA.py:118-122]()
4. Logs results to `--outputpath` at [reproduce/Step_1_QA.py:127]()

Sources: [reproduce/Step_0_index.py:1-97](), [reproduce/Step_1_QA.py:1-135]()

## Best Practices

When using MiniRAG, consider the following best practices:

1. **Working directory setup**: Choose a persistent directory for the `working_dir` parameter to maintain your index between sessions.
2. **Model selection**: Choose LLM and embedding models appropriate for your task. Smaller models may be faster but less accurate.
3. **Query mode selection**:
   - Use `mode="mini"` for complex questions requiring comprehension of relationships
   - Use `mode="naive"` for simple factual questions
   - Use `mode="light"` for a balance between speed and accuracy
4. **Error handling**: Always wrap query calls in try-except blocks to handle potential errors.

## Summary

This page has demonstrated the basic usage patterns of MiniRAG:

1. **Setup and configuration**: Initializing MiniRAG with appropriate models
2. **Document indexing**: Adding documents to build the knowledge graph
3. **Question answering**: Querying the system with different modes
4. **Running experiments**: Processing multiple questions and logging results

For more advanced usage, including custom storage backends, embedding models, and LLM integration, see [Extending MiniRAG](#9).

---

# Page: Document Indexing

# Document Indexing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [minirag/kg/weaviate_impl.py](minirag/kg/weaviate_impl.py)
- [minirag/minirag.py](minirag/minirag.py)
- [reproduce/Step_0_index.py](reproduce/Step_0_index.py)
- [reproduce/Step_1_QA.py](reproduce/Step_1_QA.py)
- [tests/test_weaviate.py](tests/test_weaviate.py)

</details>



Document Indexing in MiniRAG is the process of ingesting raw documents, extracting valuable information from them, and storing this information in various storage systems for efficient retrieval. This page explains how to index documents using MiniRAG and details the underlying indexing architecture.

For information on how to query the indexed documents, see [Question Answering](#8.2).

## Indexing Process Overview

The document indexing pipeline in MiniRAG transforms raw text documents into a structured knowledge base that supports advanced retrieval capabilities.

```mermaid
flowchart TD
    A["Raw Documents"] --> B["MiniRAG.insert()"]
    B --> C["Text Chunking"]
    C --> D["Entity Extraction"]
    D --> E["Graph Construction"]
    
    C --> |"Chunk Text"| F1["KVStorage.upsert()"]
    C --> |"Chunk Embeddings"| F2["VectorStorage.upsert()"]
    D --> |"Entity Data"| F1
    D --> |"Entity Embeddings"| F2
    E --> |"Graph Structure"| F3["GraphStorage.upsert_node()/upsert_edge()"]
    
    B --> |"Document Status"| F4["DocStatusStorage.upsert()"]
```

Sources: [main.py:76-90](), [minirag/prompt.py:13-118]()

## Using the API to Index Documents

The primary way to index documents is using the `insert` method of the `MiniRAG` class:

```python
# Initialize MiniRAG
rag = MiniRAG(
    working_dir="./working_dir",
    llm_model_func=hf_model_complete,
    llm_model_max_token_size=200,
    llm_model_name="microsoft/Phi-3.5-mini-instruct",
    embedding_func=EmbeddingFunc(...),
)

# Index a document
with open("document.txt") as f:
    rag.insert(f.read())
```

Sources: [main.py:58-71](), [main.py:85-90]()

## Indexing Process Details

### Document Reading

The first step in the indexing process is reading documents from their source. MiniRAG supports reading plain text files (`.txt`). In the provided example, a utility function `find_txt_files()` is used to locate text files in a directory structure.

```python
def find_txt_files(root_path):
    txt_files = []
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.endswith(".txt"):
                txt_files.append(os.path.join(root, file))
    return txt_files
```

Sources: [main.py:76-82]()

### Text Chunking

During indexing, MiniRAG splits documents into smaller chunks to:
1. Fit within token limits of LLMs
2. Create more granular units for retrieval
3. Enable more precise context generation

Each chunk is assigned a unique identifier, and the text is stored in KV storage while its embedding is stored in Vector storage.

### Entity Extraction

MiniRAG uses a Language Model with a specialized prompt to extract structured information from text chunks:

1. **Entities**: Named objects with types (person, organization, location, event)
2. **Relationships**: Connections between entities
3. **Content Keywords**: High-level themes and concepts

```mermaid
graph TD
    subgraph "Entity Extraction Process"
        Chunk["Text Chunk"] --> |"LLM with\nextraction prompt"| Processor["Entity Processor"]
        Processor --> Entities["Entities"]
        Processor --> Relationships["Relationships"]
        Processor --> Keywords["Content Keywords"]
        
        Entities --> |"store"| KV["KVStorage"]
        Entities --> |"embed"| VS["VectorStorage"]
        Relationships --> |"store"| KV
        Keywords --> |"store"| KV
    end
```

The entity extraction prompt template is defined in `prompt.py` and includes detailed instructions for identifying entities with their names, types, and descriptions.

Sources: [minirag/prompt.py:13-118]()

### Graph Construction

After extracting entities and relationships, MiniRAG constructs a heterogeneous graph that represents the knowledge in the documents. This graph includes:

- Nodes for text chunks
- Nodes for entities
- Edges between chunks and entities they mention
- Edges between related entities

This graph structure is stored in Graph storage and is essential for MiniRAG's topology-enhanced retrieval capabilities. For more information on the theoretical basis of this approach, see [Heterogeneous Graph Indexing](#4.1).

## Storage Systems

MiniRAG uses four types of storage systems during indexing:

| Storage Type | Purpose | Implementation Options | Key Methods |
|--------------|---------|------------------------|-------------|
| Vector Storage | Stores embeddings for similarity search | NanoVectorDBStorage | `upsert()`, `query()` |
| KV Storage | Stores text and metadata | JsonKVStorage | `upsert()`, `get_by_id()` |
| Graph Storage | Stores entity-relation graph | NetworkXStorage, Neo4JStorage | `upsert_node()`, `upsert_edge()` |
| Document Status Storage | Tracks document processing status | JsonDocStatusStorage | `upsert()`, `get_status_counts()` |

Each storage system inherits from the `StorageNameSpace` base class, providing a consistent interface and namespace management.

```mermaid
classDiagram
    class StorageNameSpace {
        +namespace: str
        +global_config: dict
        +index_done_callback()
        +query_done_callback()
    }
    
    StorageNameSpace <|-- BaseVectorStorage
    StorageNameSpace <|-- BaseKVStorage
    StorageNameSpace <|-- BaseGraphStorage
    BaseKVStorage <|-- DocStatusStorage
    
    BaseVectorStorage <|-- NanoVectorDBStorage
    BaseKVStorage <|-- JsonKVStorage
    BaseGraphStorage <|-- NetworkXStorage
    BaseGraphStorage <|-- Neo4JStorage
    DocStatusStorage <|-- JsonDocStatusStorage
```

For more details on storage implementations, see [Storage Implementations](#5).

Sources: [main.py:58-71]()

## Example: Indexing a Document Collection

The following example shows how to index all text files in a directory, which is useful for processing collections like the LiHua-World dataset:

```python
# Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "microsoft/Phi-3.5-mini-instruct"
WORKING_DIR = "./working_dir"
DATA_PATH = "./dataset/LiHua-World/data/"

# Initialize MiniRAG
rag = MiniRAG(
    working_dir=WORKING_DIR,
    llm_model_func=hf_model_complete,
    llm_model_max_token_size=200,
    llm_model_name=LLM_MODEL,
    embedding_func=EmbeddingFunc(...),
)

# Find and index all text files
WEEK_LIST = find_txt_files(DATA_PATH)
for WEEK in WEEK_LIST:
    id = WEEK_LIST.index(WEEK)
    print(f"{id}/{len(WEEK_LIST)}")
    with open(WEEK) as f:
        rag.insert(f.read())
```

This example shows:
1. How to configure MiniRAG with appropriate model settings
2. How to locate text files in a directory structure
3. How to index each file and track progress

Sources: [main.py:84-90]()

## Best Practices for Document Indexing

When indexing documents with MiniRAG, consider the following best practices:

1. **Model Selection**: Choose appropriate embedding models and LLMs that balance quality and speed
2. **Working Directory**: Use a dedicated working directory for each project to isolate storage
3. **Document Preprocessing**: Clean and normalize text before indexing if needed
4. **Batch Processing**: For large collections, index in batches to manage memory usage
5. **Status Monitoring**: Check document status storage to identify and fix failed indexing operations

By following these practices, you can build a robust knowledge base that supports effective question answering and information retrieval.

---

# Page: Question Answering

# Question Answering

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [minirag/api/requirements.txt](minirag/api/requirements.txt)
- [minirag/operate.py](minirag/operate.py)
- [reproduce/Step_0_index.py](reproduce/Step_0_index.py)
- [reproduce/Step_1_QA.py](reproduce/Step_1_QA.py)

</details>



This page documents how to use MiniRAG's question answering capabilities to retrieve and generate accurate responses based on indexed documents. It explains the query processing flow, different query modes, and how to execute queries against your knowledge base. For information about indexing documents before querying, see [Document Indexing](#8.1).

## Query Processing Flow

MiniRAG supports three different query modes that determine how your query is processed and how information is retrieved from the knowledge base.

```mermaid
flowchart TD
    subgraph "Query Processing Flow"
        UserQuery[/"User Query"/] --> QueryPreprocessing["Query Preprocessing"]
        QueryPreprocessing --> QueryMode{"Query Mode?"}
        
        QueryMode -->|"light"| HybridRetrieval["Hybrid Query Retrieval"]
        QueryMode -->|"naive"| DirectRetrieval["Direct Vector Retrieval"]
        QueryMode -->|"mini"| MiniRetrieval["MiniRAG Query Retrieval"]
        
        HybridRetrieval --> TopologyEnhanced["Topology-Enhanced Retrieval"]
        MiniRetrieval --> TopologyEnhanced
        
        DirectRetrieval --> ContextGeneration["Context Generation"]
        TopologyEnhanced --> ContextGeneration
        
        ContextGeneration --> PromptCreation["Prompt Creation"]
        PromptCreation --> LLMGeneration["LLM Response Generation"]
        LLMGeneration --> FinalResponse[/"Final Response"/]
    end
```

Sources: [reproduce/Step_1_QA.py:117-123](), [minirag/prompt.py:313-413]()

### Query Modes

MiniRAG provides three distinct query modes, each with different retrieval strategies:

| Mode | Description | Retrieval Strategy | Best Use Cases |
|------|-------------|-------------------|----------------|
| `naive` | Basic vector similarity search | Direct vector retrieval without topology | Simple factual queries where direct matching is sufficient |
| `light` | Hybrid vector and graph search | Topology-enhanced retrieval with lightweight graph traversal | Most general-purpose queries requiring some connections |
| `mini` | Full heterogeneous graph-based retrieval | Advanced topology-enhanced retrieval with full graph features | Complex questions requiring multi-hop reasoning and entity relationships |

Sources: [reproduce/Step_1_QA.py:119]()

## Using Question Answering

### Basic Usage

The simplest way to query your indexed data is to use the `query()` method of your MiniRAG instance:

```mermaid
sequenceDiagram
    participant "User Code" as UC
    participant "MiniRAG Instance" as MR
    participant "QueryParam" as QP
    participant "Storage Components" as SC
    participant "LLM" as LLM
    
    UC->>MR: Initialize MiniRAG
    UC->>QP: Create QueryParam(mode="mini")
    UC->>MR: rag.query(question, param=QueryParam)
    MR->>SC: Retrieve relevant chunks and entities
    SC-->>MR: Return retrieved data
    MR->>LLM: Generate response with context
    LLM-->>MR: Return generated answer
    MR-->>UC: Return final answer
```

Sources: [reproduce/Step_1_QA.py:117-123](), [main.py:94-96]()

### Code Example

Here's a minimal example of how to perform question answering with MiniRAG:

```python
from minirag import MiniRAG, QueryParam

# Initialize MiniRAG (configuration omitted for brevity)
rag = MiniRAG(...)

# Ask a question
question = 'What does LiHua predict will happen in "The Rings of Power"?'
answer = rag.query(question, param=QueryParam(mode="mini"))
print(answer)
```

Sources: [main.py:94-96](), [reproduce/Step_1_QA.py:117-123]()

## Query Processing Components

### Query Parameter Configuration

The `QueryParam` class allows you to customize how your query is processed:

```mermaid
classDiagram
    class QueryParam {
        +mode: str
        +top_k: int
        +response_type: str
    }
    
    note for QueryParam "mode: 'naive', 'light', or 'mini'\ntop_k: number of results to retrieve\nresponse_type: format of response"
```

Sources: [reproduce/Step_1_QA.py:119](), [main.py:95]()

### Retrieval Strategies

The retrieval strategy differs based on the query mode:

```mermaid
flowchart TD
    subgraph "Retrieval Strategies"
        Query[/"User Query"/]
        
        subgraph "Vector Storage"
            ChunksVDB[("Chunks Vector DB")]
            EntitiesVDB[("Entities Vector DB")]
            EntityNameVDB[("Entity Name Vector DB")]
            RelationshipsVDB[("Relationships Vector DB")]
        end
        
        subgraph "KV Storage"
            TextChunksDB[("Text Chunks DB")]
        end
        
        subgraph "Graph Storage"
            GraphDB[("Chunk-Entity-Relation Graph")]
        end
        
        Query --> NaiveMode["Naive Mode"]
        Query --> LightMode["Light Mode"]
        Query --> MiniMode["Mini Mode"]
        
        NaiveMode --> ChunksVDB
        LightMode --> ChunksVDB
        LightMode --> EntitiesVDB
        LightMode --> RelationshipsVDB
        LightMode --> GraphDB
        
        MiniMode --> ChunksVDB
        MiniMode --> EntityNameVDB
        MiniMode --> GraphDB
        
        ChunksVDB --> DirectRetrieval["Direct Vector Retrieval"]
        EntitiesVDB --> HybridRetrieval["Hybrid Vector & Graph Retrieval"]
        EntityNameVDB --> MiniRetrieval["MiniRAG Entity-Aware Retrieval"]
        RelationshipsVDB --> HybridRetrieval
        GraphDB --> TopologyEnhanced["Topology-Enhanced Retrieval"]
        
        DirectRetrieval --> RetrievedChunks["Retrieved Chunks"]
        HybridRetrieval --> RetrievedChunks
        MiniRetrieval --> RetrievedChunks
        TopologyEnhanced --> RetrievedChunks
        
        RetrievedChunks --> TextChunksDB
        TextChunksDB --> FullContent["Full Content Context"]
    end
```

Sources: [reproduce/Step_1_QA.py:117-123](), [main.py:94-96]()

## Response Generation

After retrieving relevant information, MiniRAG uses an LLM to generate a response based on the retrieved context:

```mermaid
flowchart TD
    subgraph "Response Generation"
        RetrievedContext["Retrieved Context"] --> PromptCreation["Prompt Creation"]
        UserQuery["User Query"] --> PromptCreation
        
        PromptCreation --> RagResponsePrompt["RAG Response Prompt"]
        RagResponsePrompt --> LLMGeneration["LLM Generation"]
        
        LLMGeneration --> |"Using:\nhf_model_complete\nor other LLM function"| LLMResponse["LLM Response"]
        
        LLMResponse --> Answer[/"Final Answer"/]
    end
```

Sources: [minirag/prompt.py:313-337](), [minirag/prompt.py:393-413](), [reproduce/Step_1_QA.py:67-70]()

### Prompt Templates

MiniRAG uses specific prompt templates for generating responses:

1. For standard RAG responses: `rag_response` template
2. For naive mode: `naive_rag_response` template

These templates include placeholders for:
- Response type
- Context data from retrieved documents
- The user's query

Sources: [minirag/prompt.py:313-337](), [minirag/prompt.py:393-413]()

## Practical Example: Running a Query

Here's a complete example of how to run a question answering task with MiniRAG using the LiHua-World dataset:

```mermaid
flowchart TD
    subgraph "Complete QA Process"
        InitializeRAG["Initialize MiniRAG\nwith LLM and Embedding Model"]
        ReadQuestions["Read Questions from CSV/JSON"]
        ProcessQuestion["Process Each Question"]
        
        InitializeRAG --> ReadQuestions
        ReadQuestions --> ProcessQuestion
        
        ProcessQuestion --> QueryMiniRAG["Query MiniRAG\nrag.query(question, param=QueryParam(mode='mini'))"]
        QueryMiniRAG --> FormatResponse["Format Response"]
        FormatResponse --> SaveResult["Save Result to Output File"]
    end
```

Sources: [reproduce/Step_1_QA.py:65-127]()

## Integration with Language Models

MiniRAG supports integration with various language models:

| Model | Identifier | Description |
|-------|------------|-------------|
| Phi-3.5-mini | `microsoft/Phi-3.5-mini-instruct` | Small but capable model from Microsoft |
| GLM Edge | `THUDM/glm-edge-1.5b-chat` | Efficient edge model from THUDM |
| MiniCPM | `openbmb/MiniCPM3-4B` | Small Chinese-English bilingual model |
| Qwen | `Qwen/Qwen2.5-3B-Instruct` | Small model from Alibaba |

To use these models, specify the model name when initializing MiniRAG or set it via the command line in provided scripts.

Sources: [reproduce/Step_1_QA.py:42-52](), [main.py:35-45]()

## Performance Considerations

When using question answering with MiniRAG, consider:

1. **Query Mode Selection**: Choose the appropriate mode based on your query complexity
   - `naive`: Fastest but least sophisticated
   - `light`: Good balance of speed and accuracy
   - `mini`: Most accurate but potentially slower

2. **Model Selection**: Smaller models are faster but may have lower accuracy

3. **Embedding Model**: The default embedding model `sentence-transformers/all-MiniLM-L6-v2` provides a good balance of performance and accuracy

4. **Top-k Parameter**: Adjust this to control how many documents are retrieved and sent to the LLM

Sources: [reproduce/Step_1_QA.py:21-79](), [main.py:14-72]()

---

# Page: Custom Workflows

# Custom Workflows

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [main.py](main.py)
- [minirag/kg/weaviate_impl.py](minirag/kg/weaviate_impl.py)
- [minirag/minirag.py](minirag/minirag.py)
- [minirag/prompt.py](minirag/prompt.py)
- [tests/test_weaviate.py](tests/test_weaviate.py)

</details>



## Purpose and Scope

This document covers advanced usage patterns for MiniRAG beyond basic document indexing and querying. Topics include custom text chunking strategies, incremental document updates, batch processing configurations, error handling mechanisms, custom storage backend selection, and custom LLM/embedding integration.

For basic document insertion, see [Document Indexing](#8.1). For standard query operations, see [Question Answering](#8.2). For implementing new storage backends from scratch, see [Adding Storage Backends](#10.1).

---

## Custom Chunking Functions

MiniRAG allows you to replace the default token-based chunking algorithm with custom implementations. The `chunking_func` parameter in the `MiniRAG` class accepts any callable that follows the chunking interface.

### Default Chunking Behavior

By default, MiniRAG uses token-based chunking from `operate.py`:

```python
chunking_func: callable = chunking_by_token_size
```

The default function takes the following parameters and returns a list of chunk dictionaries with `content` and `tokens` fields. Configuration is controlled via:

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `chunk_token_size` | 1200 | Maximum tokens per chunk |
| `chunk_overlap_token_size` | 100 | Overlap between chunks |
| `tiktoken_model_name` | "gpt-4o-mini" | Tokenizer model |

Sources: [minirag/minirag.py:138-140](), [minirag/minirag.py:185-186]()

### Implementing Custom Chunking

Custom chunking functions must accept `(content, overlap_size, chunk_size, tokenizer_model)` parameters and return a list of dictionaries with at minimum a `content` field:

```python
def custom_semantic_chunker(content, overlap_size, chunk_size, tokenizer_model):
    """Custom chunker that splits by semantic boundaries"""
    chunks = []
    # Your custom logic here
    # Split by paragraphs, sentences, or semantic similarity
    for i, chunk_text in enumerate(split_semantic(content)):
        chunks.append({
            "content": chunk_text,
            "tokens": len(chunk_text.split()),
            "chunk_index": i
        })
    return chunks

# Initialize with custom chunker
rag = MiniRAG(
    working_dir="./my_rag",
    chunking_func=custom_semantic_chunker,
    chunking_func_kwargs={}  # Additional kwargs passed to your function
)
```

The custom chunking function is invoked during document processing in the pipeline:

Sources: [minirag/minirag.py:484-495]()

### Chunking Function Call Pattern

```mermaid
graph TB
    Insert["rag.insert(documents)"] --> Pipeline["apipeline_process_enqueue_documents()"]
    Pipeline --> Loop["For each document in batch"]
    Loop --> ChunkCall["self.chunking_func(<br/>content,<br/>overlap_size,<br/>chunk_size,<br/>tokenizer)"]
    ChunkCall --> Hash["compute_mdhash_id(chunk, prefix='chunk-')"]
    Hash --> Store["Store in chunks_vdb<br/>and text_chunks"]
    Store --> Status["Update doc_status to PROCESSED"]
    
    ChunkCall -.default.-> TokenChunk["chunking_by_token_size"]
    ChunkCall -.custom.-> CustomChunk["Your custom_chunker"]
```

Sources: [minirag/minirag.py:484-495](), [minirag/minirag.py:370-376]()

---

## Document Lifecycle Management

MiniRAG tracks document processing status through a state machine, enabling incremental updates and robust error handling.

### Document Status States

The `DocStatus` enum defines the document lifecycle:

| Status | Description | Transition |
|--------|-------------|------------|
| `PENDING` | Newly enqueued, not yet processed | Initial state |
| `PROCESSING` | Currently being chunked/indexed | From PENDING or FAILED |
| `PROCESSED` | Successfully completed | Terminal success state |
| `FAILED` | Processing encountered error | Can retry to PROCESSING |

Sources: [minirag/base.py]()

### Document Status Tracking Diagram

```mermaid
stateDiagram-v2
    [*] --> PENDING: insert() called
    PENDING --> PROCESSING: apipeline_process_enqueue_documents()
    PROCESSING --> PROCESSED: Chunking succeeds
    PROCESSING --> FAILED: Exception during processing
    FAILED --> PROCESSING: Retry on next insert()
    PROCESSED --> [*]: Entity extraction complete
    
    note right of PENDING
        Stored in doc_status storage
        with metadata: created_at,
        content_summary, content_length
    end note
    
    note right of PROCESSED
        Includes chunks_count
        and updated_at timestamp
    end note
```

Sources: [minirag/minirag.py:424-449](), [minirag/minirag.py:501-513]()

### Incremental Update Pattern

Documents are deduplicated by content hash. If a document with the same content already exists, it is not reprocessed:

```python
# Enqueue multiple documents - duplicates filtered automatically
documents = [
    "Document content 1",
    "Document content 2",
    "Document content 1",  # Duplicate - will be filtered
]

rag.insert(documents)  # Only 2 documents processed

# Check document status
all_docs = await rag.doc_status.get_docs_by_status(DocStatus.PROCESSED)
print(f"Processed {len(all_docs)} unique documents")
```

The deduplication logic uses MD5 hashing:

```mermaid
graph LR
    Input["Input documents"] --> Clean["clean_text(doc)"]
    Clean --> Hash["compute_mdhash_id(doc, prefix='doc-')"]
    Hash --> Unique["Remove duplicates<br/>by content hash"]
    Unique --> Filter["filter_keys()<br/>Check existing in doc_status"]
    Filter --> New["Only new unique docs<br/>get PENDING status"]
    New --> Upsert["doc_status.upsert()"]
```

Sources: [minirag/minirag.py:391-449](), [minirag/minirag.py:415-423]()

### Querying Document Status

Access document status programmatically:

```python
# Get all documents by status
pending = await rag.doc_status.get_docs_by_status(DocStatus.PENDING)
processing = await rag.doc_status.get_docs_by_status(DocStatus.PROCESSING)
failed = await rag.doc_status.get_docs_by_status(DocStatus.FAILED)
processed = await rag.doc_status.get_docs_by_status(DocStatus.PROCESSED)

# Manually retry failed documents
if failed:
    # Failed docs are automatically retried on next insert()
    await rag.apipeline_process_enqueue_documents()
```

Failed and processing documents are automatically included in the next processing batch:

Sources: [minirag/minirag.py:461-474]()

---

## Batch Processing and Parallelization

### Batch Size Configuration

Control parallel document processing with the `max_parallel_insert` parameter:

```python
import os

# Set via environment variable
os.environ["MAX_PARALLEL_INSERT"] = "5"

# Or via constructor
rag = MiniRAG(
    working_dir="./rag_data",
    max_parallel_insert=5  # Process 5 documents in parallel
)
```

Default value is 2 if not specified. This controls how many documents are processed concurrently in each batch during the pipeline execution.

Sources: [minirag/minirag.py:188]()

### Batch Processing Flow

```mermaid
graph TB
    Docs["to_process_docs<br/>(PENDING + PROCESSING + FAILED)"] --> Split["Split into batches<br/>size = max_parallel_insert"]
    Split --> B1["Batch 1<br/>[doc1, doc2, ..., docN]"]
    Split --> B2["Batch 2<br/>[docN+1, ..., doc2N]"]
    Split --> B3["Batch K<br/>[remaining docs]"]
    
    B1 --> P1["Process batch 1<br/>sequentially"]
    B2 --> P2["Process batch 2<br/>sequentially"]
    B3 --> P3["Process batch K<br/>sequentially"]
    
    P1 --> Chunk1["Chunk each doc<br/>+ Store in chunks_vdb<br/>+ Update doc_status"]
    P2 --> Chunk2["Chunk each doc<br/>+ Store in chunks_vdb<br/>+ Update doc_status"]
    P3 --> Chunk3["Chunk each doc<br/>+ Store in chunks_vdb<br/>+ Update doc_status"]
    
    Chunk1 --> Complete["All batches complete"]
    Chunk2 --> Complete
    Chunk3 --> Complete
```

Sources: [minirag/minirag.py:476-514]()

### Async Concurrency Limits

LLM and embedding calls have separate async concurrency controls:

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `llm_model_max_async` | 16 | Max concurrent LLM calls |
| `embedding_func_max_async` | 16 | Max concurrent embedding calls |

These are applied using the `limit_async_func_call` decorator:

```python
rag = MiniRAG(
    llm_model_max_async=8,      # Limit to 8 concurrent LLM calls
    embedding_func_max_async=32  # Allow 32 concurrent embeddings
)
```

The limits are enforced via semaphore-based throttling:

Sources: [minirag/minirag.py:161](), [minirag/minirag.py:169](), [minirag/minirag.py:247-249](), [minirag/minirag.py:300-306]()

---

## Error Handling and Recovery

### Automatic Retry for Failed Documents

Documents that fail during processing are marked as `FAILED` and automatically retried on the next `insert()` call. The system aggregates all documents needing processing:

```python
# First attempt - some docs may fail
rag.insert(["doc1", "doc2", "doc3"])

# Later insert - failed docs from previous run are retried
rag.insert(["doc4"])  # Also retries any FAILED docs from before
```

The retry logic combines `PROCESSING`, `FAILED`, and `PENDING` documents:

Sources: [minirag/minirag.py:461-474]()

### Storage-Level Error Handling

Storage operations should handle exceptions gracefully. Example from Weaviate implementation:

```python
async def upsert(self, data: Dict[str, Dict]):
    for _id, value in data.items():
        try:
            obj = {"content": value.get("content")}
            await run_sync(
                self.client.data_object.create, obj, "Document", _id
            )
        except WeaviateQueryException as e:
            print(f"Error upserting id {_id} to weaviate: {e}")
            # Continue processing other documents
```

Custom storage implementations should follow this pattern of catching exceptions and allowing partial success.

Sources: [minirag/kg/weaviate_impl.py:50-62]()

### Error Handling Pattern

```mermaid
graph TB
    Start["Document processing starts"] --> Try["Try: Chunk and index"]
    Try -->|Success| Update["Update status to PROCESSED"]
    Try -->|Exception| Catch["Catch exception"]
    Catch --> Log["Log error"]
    Log --> Failed["Set status to FAILED"]
    Failed --> NextRun["Next insert() call"]
    NextRun --> Retry["Retry FAILED docs"]
    Retry --> Try
    
    Update --> Extract["Entity extraction"]
    Extract --> Done["Complete"]
```

Sources: [minirag/minirag.py:496-513]()

---

## Custom Storage Backend Selection

MiniRAG supports pluggable storage backends for graph, vector, and key-value stores. Select storage implementations via constructor parameters.

### Storage Backend Configuration

```python
rag = MiniRAG(
    working_dir="./data",
    graph_storage="NetworkXStorage",      # In-memory graph
    vector_storage="NanoVectorDBStorage", # Lightweight vector DB
    kv_storage="JsonKVStorage",           # JSON file storage
    doc_status_storage="JsonDocStatusStorage"
)
```

### Available Storage Backends

| Storage Type | Implementations | Use Case |
|-------------|-----------------|----------|
| Graph Storage | `NetworkXStorage`, `Neo4JStorage`, `AGEStorage`, `PGGraphStorage`, `TiDBGraphStorage`, `MongoGraphStorage`, `OracleGraphStorage`, `WeaviateGraphStorage`, `GremlinStorage` | Entity relationships |
| Vector Storage | `NanoVectorDBStorage`, `MilvusVectorDBStorge`, `ChromaVectorDBStorage`, `TiDBVectorDBStorage`, `PGVectorStorage`, `OracleVectorDBStorage`, `WeaviateVectorStorage` | Semantic search |
| KV Storage | `JsonKVStorage`, `MongoKVStorage`, `RedisKVStorage`, `TiDBKVStorage`, `PGKVStorage`, `OracleKVStorage`, `WeaviateKVStorage` | Text chunk storage |

Sources: [minirag/minirag.py:39-66](), [minirag/minirag.py:130-133](), [minirag/minirag.py:182]()

### Storage Initialization Flow

```mermaid
graph TB
    Init["MiniRAG.__post_init__()"] --> GetCls["_get_storage_class(storage_name)"]
    GetCls --> Import["lazy_external_import(module, class)"]
    Import --> Partial["partial(cls, global_config)"]
    
    Partial --> CreateGraph["graph_storage_cls(namespace, embedding_func)"]
    Partial --> CreateVector["vector_db_storage_cls(namespace, embedding_func)"]
    Partial --> CreateKV["key_string_value_json_storage_cls(namespace, embedding_func)"]
    
    CreateGraph --> Instances["Storage instances:<br/>- chunk_entity_relation_graph<br/>- entities_vdb<br/>- entity_name_vdb<br/>- relationships_vdb<br/>- chunks_vdb<br/>- text_chunks<br/>- full_docs<br/>- doc_status"]
    CreateVector --> Instances
    CreateKV --> Instances
```

Sources: [minirag/minirag.py:207-227](), [minirag/minirag.py:264-314](), [minirag/minirag.py:315-318]()

### Using Cloud/Distributed Backends

Example with TiDB for distributed storage:

```python
rag = MiniRAG(
    working_dir="./tidb_rag",
    graph_storage="TiDBGraphStorage",
    vector_storage="TiDBVectorDBStorage",
    kv_storage="TiDBKVStorage",
    vector_db_storage_cls_kwargs={
        "host": "gateway01.us-west-2.prod.aws.tidbcloud.com",
        "port": 4000,
        "user": "your_user",
        "password": "your_password",
        "database": "minirag_db"
    }
)
```

Storage-specific configuration is passed via `vector_db_storage_cls_kwargs`:

Sources: [minirag/minirag.py:173]()

---

## Custom LLM and Embedding Integration

### Custom LLM Functions

Replace the default LLM with custom implementations by providing a callable to `llm_model_func`:

```python
from minirag.llm.hf import hf_model_complete
from transformers import AutoModelForCausalLM, AutoTokenizer

# Custom LLM wrapper
def my_custom_llm(prompt, **kwargs):
    # Your custom logic here
    model = AutoModelForCausalLM.from_pretrained("my-model")
    tokenizer = AutoTokenizer.from_pretrained("my-model")
    # ... generation logic
    return response_text

rag = MiniRAG(
    llm_model_func=my_custom_llm,
    llm_model_name="custom-model-name",
    llm_model_max_token_size=4096,
    llm_model_kwargs={
        "temperature": 0.7,
        "top_p": 0.9
    }
)
```

The LLM function is wrapped with async limiting and caching:

Sources: [minirag/minirag.py:164-170](), [minirag/minirag.py:300-306]()

### Custom Embedding Functions

Provide custom embedding functions via `EmbeddingFunc`:

```python
from minirag.utils import EmbeddingFunc
from transformers import AutoModel, AutoTokenizer

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def custom_embed(texts):
    tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL)
    model = AutoModel.from_pretrained(EMBEDDING_MODEL)
    # Your embedding logic
    return embeddings

rag = MiniRAG(
    embedding_func=EmbeddingFunc(
        embedding_dim=384,
        max_token_size=512,
        func=lambda texts: custom_embed(texts)
    )
)
```

The `EmbeddingFunc` dataclass wraps your function and provides metadata:

- `embedding_dim`: Dimension of output vectors
- `max_token_size`: Maximum tokens to process
- `func`: Callable that takes list of texts and returns embeddings

Sources: [main.py:63-71](), [minirag/minirag.py:159](), [minirag/minirag.py:247-249]()

### LLM/Embedding Integration Architecture

```mermaid
graph TB
    Config["MiniRAG initialization"] --> WrapLLM["limit_async_func_call<br/>(llm_model_func, max=llm_model_max_async)"]
    Config --> WrapEmbed["limit_async_func_call<br/>(embedding_func, max=embedding_func_max_async)"]
    
    WrapLLM --> CacheLLM["partial(func, hashing_kv=llm_response_cache)"]
    CacheLLM --> LLMReady["self.llm_model_func<br/>(with cache + rate limit)"]
    
    WrapEmbed --> EmbedReady["self.embedding_func<br/>(with rate limit)"]
    
    LLMReady --> Operations["Used in:<br/>- extract_entities()<br/>- minirag_query()<br/>- hybrid_query()<br/>- naive_query()"]
    
    EmbedReady --> VDBs["Passed to all storage:<br/>- entities_vdb<br/>- entity_name_vdb<br/>- relationships_vdb<br/>- chunks_vdb<br/>- text_chunks<br/>- full_docs"]
```

Sources: [minirag/minirag.py:247-249](), [minirag/minirag.py:300-306](), [minirag/minirag.py:254-298]()

---

## Advanced Workflow Patterns

### Pattern 1: Progressive Document Loading

Load and process documents incrementally with status monitoring:

```python
import os
from minirag import MiniRAG, QueryParam
from minirag.base import DocStatus

rag = MiniRAG(working_dir="./progressive_rag")

# Load documents in batches from a directory
def load_documents_progressively(data_path):
    txt_files = []
    for root, dirs, files in os.walk(data_path):
        for file in files:
            if file.endswith(".txt"):
                txt_files.append(os.path.join(root, file))
    
    # Process in batches of 10
    batch_size = 10
    for i in range(0, len(txt_files), batch_size):
        batch = txt_files[i:i+batch_size]
        batch_content = []
        
        for file_path in batch:
            with open(file_path) as f:
                content = f.read()
                batch_content.append(content)
        
        # Insert batch
        rag.insert(batch_content)
        
        # Check status
        processed = await rag.doc_status.get_docs_by_status(DocStatus.PROCESSED)
        print(f"Processed {len(processed)} documents total")
```

Sources: [main.py:76-90]()

### Pattern 2: Custom Document IDs

Provide explicit document IDs to maintain stable references:

```python
# Using custom IDs
document_ids = ["doc-001", "doc-002", "doc-003"]
documents = ["Content 1", "Content 2", "Content 3"]

rag.insert(documents, ids=document_ids)

# Later updates with same IDs are deduplicated
rag.insert(["Content 1"], ids=["doc-001"])  # Skipped - already exists
```

Custom IDs bypass the MD5 hash generation and allow explicit control over document identity:

Sources: [minirag/minirag.py:344-359](), [minirag/minirag.py:408-416]()

### Pattern 3: Multi-Stage Processing with Custom Handlers

Combine custom chunking, preprocessing, and post-processing:

```python
from minirag import MiniRAG

# Preprocessing function
def preprocess_document(text):
    # Clean, normalize, extract metadata
    cleaned = text.strip().lower()
    return cleaned

# Custom chunker with metadata
def chunk_with_metadata(content, overlap, size, tokenizer):
    chunks = []
    # Your chunking logic
    for i, chunk in enumerate(split_content(content, size)):
        chunks.append({
            "content": chunk,
            "chunk_index": i,
            "metadata": extract_metadata(chunk)
        })
    return chunks

# Initialize
rag = MiniRAG(
    chunking_func=chunk_with_metadata,
    max_parallel_insert=4
)

# Process with preprocessing
documents = load_raw_documents()
preprocessed = [preprocess_document(doc) for doc in documents]
rag.insert(preprocessed)
```

### Pattern 4: Monitoring and Observability

Track processing metrics during bulk operations:

```python
import asyncio
from minirag import MiniRAG
from minirag.base import DocStatus

async def monitor_processing(rag, check_interval=5):
    """Monitor document processing status"""
    while True:
        pending = await rag.doc_status.get_docs_by_status(DocStatus.PENDING)
        processing = await rag.doc_status.get_docs_by_status(DocStatus.PROCESSING)
        processed = await rag.doc_status.get_docs_by_status(DocStatus.PROCESSED)
        failed = await rag.doc_status.get_docs_by_status(DocStatus.FAILED)
        
        print(f"""
        Status:
        - Pending: {len(pending)}
        - Processing: {len(processing)}
        - Processed: {len(processed)}
        - Failed: {len(failed)}
        """)
        
        if not pending and not processing:
            break
            
        await asyncio.sleep(check_interval)

# Usage
rag = MiniRAG(working_dir="./monitored_rag")
rag.insert(large_document_list)
await monitor_processing(rag)
```

Sources: [minirag/minirag.py:461-474]()

### Pattern 5: Batch Query with Different Modes

Execute multiple queries with varying retrieval strategies:

```python
from minirag import MiniRAG, QueryParam

rag = MiniRAG(working_dir="./multi_mode_rag")
rag.insert(documents)

queries = [
    "What is the main topic?",
    "List all persons mentioned",
    "Summarize the key events"
]

# Run same queries with different modes
results = {}
for mode in ["naive", "light", "mini"]:
    results[mode] = []
    for query in queries:
        answer = rag.query(query, param=QueryParam(mode=mode))
        results[mode].append(answer)

# Compare results
for query, naive_ans, light_ans, mini_ans in zip(
    queries, results["naive"], results["light"], results["mini"]
):
    print(f"Query: {query}")
    print(f"Naive: {naive_ans[:100]}...")
    print(f"Light: {light_ans[:100]}...")
    print(f"Mini: {mini_ans[:100]}...")
    print()
```

Sources: [minirag/minirag.py:537-572](), [main.py:93-97]()

---

## Summary

Custom workflows in MiniRAG enable:

1. **Flexible chunking** via `chunking_func` parameter with custom implementations
2. **Incremental updates** through automatic document deduplication and status tracking  
3. **Scalable batch processing** controlled by `max_parallel_insert` and async concurrency limits
4. **Robust error handling** with automatic retry for failed documents
5. **Storage flexibility** through pluggable backend selection for graph, vector, and KV stores
6. **Custom model integration** via `llm_model_func` and `embedding_func` parameters

These capabilities allow MiniRAG to adapt to diverse deployment scenarios, from single-machine prototypes to distributed production systems with custom data processing requirements.

Sources: [minirag/minirag.py:122-314](), [minirag/minirag.py:340-581](), [main.py:1-98]()

---

# Page: Utilities and Helpers

# Utilities and Helpers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [minirag/utils.py](minirag/utils.py)

</details>



The `minirag/utils.py` module provides a comprehensive set of utility functions that support MiniRAG's core operations. These utilities handle text processing, similarity calculations, graph algorithms, data serialization, and async control mechanisms used throughout the codebase. This page documents the helper functions that enable MiniRAG's data processing pipeline, storage operations, and query execution.

For information about the main RAG operations that use these utilities, see [RAG Operations and Query Processing](#3.3). For embedding model integration details, see [Embedding Functions](#6.2).

**Sources:** [minirag/utils.py:1-517]()

---

## Utility Function Categories

The utilities module is organized into several functional categories that support different aspects of the MiniRAG system:

```mermaid
graph TB
    subgraph "minirag/utils.py"
        TextProc["Text Processing<br/>clean_text, clean_str<br/>get_content_summary<br/>safe_unicode_decode"]
        Tokenization["Tokenization & Encoding<br/>encode_string_by_tiktoken<br/>decode_tokens_by_tiktoken<br/>truncate_list_by_token_size"]
        Similarity["Similarity Calculations<br/>calculate_similarity<br/>cosine_similarity<br/>6 methods supported"]
        GraphUtils["Graph Processing<br/>merge_tuples<br/>cal_path_score_list<br/>edge_vote_path"]
        DataConv["Data Conversion<br/>convert_response_to_json<br/>load_json, write_json<br/>csv_string_to_list<br/>xml_to_json"]
        AsyncCtrl["Async Control<br/>limit_async_func_call<br/>wrap_embedding_func_with_attrs"]
        Hashing["Hashing & IDs<br/>compute_mdhash_id<br/>compute_args_hash"]
        Embedding["Embedding Utilities<br/>EmbeddingFunc dataclass<br/>quantize_embedding<br/>dequantize_embedding"]
    end
    
    subgraph "Used By"
        MiniRAGCore["MiniRAG Core<br/>minirag.py"]
        Operate["RAG Operations<br/>operate.py"]
        LLM["LLM Interface<br/>llm/openai.py"]
        Storage["Storage Implementations<br/>storage/"]
    end
    
    TextProc --> MiniRAGCore
    Tokenization --> MiniRAGCore
    Tokenization --> Operate
    Similarity --> Operate
    GraphUtils --> Operate
    DataConv --> MiniRAGCore
    DataConv --> Operate
    AsyncCtrl --> LLM
    Hashing --> Storage
    Embedding --> LLM
    
    style TextProc fill:#f9f9f9
    style Similarity fill:#f9f9f9
    style GraphUtils fill:#f9f9f9
```

**Diagram: Utility Function Categories and Their Consumers**

**Sources:** [minirag/utils.py:1-517]()

---

## Logger Configuration

The module provides a global logger instance for MiniRAG operations:

```python
logger = logging.getLogger("minirag")
```

The `set_logger` function configures file-based logging with DEBUG level output:

| Function | Purpose | Parameters |
|----------|---------|------------|
| `set_logger` | Configure file logging for MiniRAG | `log_file: str` - Path to log file |

The logger uses a standard format including timestamp, logger name, level, and message. It ensures only one file handler is attached to prevent duplicate log entries.

**Sources:** [minirag/utils.py:27-42]()

---

## 9.1 Text Processing

Text processing utilities handle cleaning, normalization, tokenization, and encoding operations required for document ingestion and query processing.

### Text Cleaning and Normalization

```mermaid
graph LR
    RawText["Raw Text Input"]
    
    subgraph "Cleaning Functions"
        clean_text["clean_text()<br/>Remove null bytes<br/>Strip whitespace"]
        clean_str["clean_str()<br/>HTML unescape<br/>Remove control chars"]
        safe_unicode_decode["safe_unicode_decode()<br/>Handle \\uXXXX sequences"]
    end
    
    CleanText["Cleaned Text"]
    
    RawText --> clean_text
    RawText --> clean_str
    RawText --> safe_unicode_decode
    
    clean_text --> CleanText
    clean_str --> CleanText
    safe_unicode_decode --> CleanText
```

**Diagram: Text Cleaning Pipeline**

| Function | Purpose | Implementation Details |
|----------|---------|----------------------|
| `clean_text` | Remove null bytes and whitespace | Strips text and replaces `\x00` characters |
| `clean_str` | Comprehensive cleaning for entity extraction | HTML unescape, removes control characters `[\x00-\x1f\x7f-\x9f]` |
| `safe_unicode_decode` | Decode Unicode escape sequences | Converts `\uXXXX` patterns to actual characters |
| `get_content_summary` | Truncate content for logging/display | Returns first `max_length` characters with ellipsis |

**Sources:** [minirag/utils.py:66-74](), [minirag/utils.py:174-182](), [minirag/utils.py:293-307]()

### Tokenization and Token Management

MiniRAG uses `tiktoken` for token-based text operations, essential for managing LLM context windows:

```mermaid
graph TB
    subgraph "Tokenization Functions"
        ENCODER["Global ENCODER<br/>tiktoken encoder instance"]
        
        encode["encode_string_by_tiktoken()<br/>text → tokens"]
        decode["decode_tokens_by_tiktoken()<br/>tokens → text"]
        truncate["truncate_list_by_token_size()<br/>Limit by token count"]
    end
    
    TextInput["Text Input"]
    TokenList["Token List"]
    DataList["List of Data Items"]
    TruncatedList["Truncated List"]
    
    TextInput --> encode
    encode --> TokenList
    TokenList --> decode
    decode --> TextInput
    
    DataList --> truncate
    truncate --> TruncatedList
    
    encode -.uses.-> ENCODER
    decode -.uses.-> ENCODER
    truncate -.uses.-> encode
```

**Diagram: Tokenization Functions and Token Management**

| Function | Signature | Purpose |
|----------|-----------|---------|
| `encode_string_by_tiktoken` | `(content: str, model_name: str = "gpt-4o") -> list[int]` | Encode text to tokens |
| `decode_tokens_by_tiktoken` | `(tokens: list[int], model_name: str = "gpt-4o") -> str` | Decode tokens to text |
| `truncate_list_by_token_size` | `(list_data: list, key: callable, max_token_size: int) -> list` | Truncate list to fit token budget |

The `ENCODER` global variable [line 25] caches the tiktoken encoder to avoid repeated initialization overhead.

**Sources:** [minirag/utils.py:25](), [minirag/utils.py:141-154](), [minirag/utils.py:189-198]()

### String Manipulation Utilities

Additional string processing functions support specialized operations:

| Function | Purpose | Example Use Case |
|----------|---------|------------------|
| `split_string_by_multi_markers` | Split text by multiple delimiters | Parse structured LLM outputs |
| `pack_user_ass_to_openai_messages` | Format conversation as OpenAI messages | Prepare chat history for API calls |

**Sources:** [minirag/utils.py:157-169]()

---

## 9.2 Similarity Calculations

The similarity calculation system provides multiple algorithms for comparing text and embeddings, critical for retrieval and ranking operations.

### Multi-Method Similarity Framework

The `calculate_similarity` function [lines 466-516] supports six different similarity methods:

```mermaid
graph TB
    InputSentences["sentences: list[str]"]
    TargetText["target: str"]
    
    subgraph "calculate_similarity()"
        method_param["method parameter"]
        
        jaccard["jaccard<br/>Set intersection/union"]
        levenshtein["levenshtein<br/>Edit distance"]
        rouge["rouge<br/>ROUGE-N score"]
        bert["bert<br/>Sentence embeddings"]
        overlap["overlap<br/>Token overlap"]
        bleu["bleu<br/>BLEU score"]
        
        method_param --> jaccard
        method_param --> levenshtein
        method_param --> rouge
        method_param --> bert
        method_param --> overlap
        method_param --> bleu
    end
    
    TopK["Top-k most similar<br/>indices: list[int]"]
    
    InputSentences --> method_param
    TargetText --> method_param
    
    jaccard --> TopK
    levenshtein --> TopK
    rouge --> TopK
    bert --> TopK
    overlap --> TopK
    bleu --> TopK
```

**Diagram: Similarity Calculation Methods in calculate_similarity()**

#### Similarity Method Details

| Method | Algorithm | Use Case | Dependencies |
|--------|-----------|----------|--------------|
| `jaccard` | Jaccard index of token sets | Fast lexical similarity | None (built-in) |
| `levenshtein` | Edit distance between token sequences | Spelling/structural similarity | `nltk.metrics.edit_distance` |
| `rouge` | ROUGE-N recall/precision/F1 | Summary evaluation | `rouge` library |
| `bert` | Cosine similarity of sentence embeddings | Semantic similarity | `sentence-transformers` |
| `overlap` | Token set overlap ratio | Entity matching | None (built-in) |
| `bleu` | BLEU score with smoothing | Translation/generation quality | `nltk.translate.bleu_score` |

**Function Signature:**
```python
calculate_similarity(
    sentences: list[str], 
    target: str, 
    method: str = "levenshtein", 
    n: int = 1,  # ROUGE-n parameter
    k: int = 1   # Number of top results to return
) -> list[int]  # Indices of top-k similar sentences
```

**Sources:** [minirag/utils.py:466-516]()

### Vector Similarity and Quantization

For embedding-based operations:

```mermaid
graph LR
    subgraph "Embedding Operations"
        FullEmbed["Full Precision<br/>Embedding<br/>np.ndarray"]
        
        quantize["quantize_embedding()<br/>8-bit compression"]
        dequantize["dequantize_embedding()<br/>Reconstruction"]
        cosine["cosine_similarity()<br/>Dot product / norms"]
        
        QuantEmbed["Quantized<br/>uint8 array<br/>+ min/max values"]
        SimilarityScore["Similarity Score<br/>float"]
    end
    
    FullEmbed --> quantize
    quantize --> QuantEmbed
    QuantEmbed --> dequantize
    dequantize --> FullEmbed
    
    FullEmbed --> cosine
    cosine --> SimilarityScore
```

**Diagram: Embedding Quantization and Similarity**

| Function | Purpose | Parameters | Returns |
|----------|---------|------------|---------|
| `cosine_similarity` | Calculate cosine similarity | `v1, v2: np.ndarray` | `float` similarity score |
| `quantize_embedding` | Compress to 8-bit integers | `embedding, bits=8` | `(quantized, min_val, max_val)` |
| `dequantize_embedding` | Restore full precision | `quantized, min_val, max_val, bits=8` | `np.ndarray` |

Quantization reduces storage by ~75% (32-bit → 8-bit) while maintaining similarity ranking quality.

**Sources:** [minirag/utils.py:443-463]()

---

## 9.3 Graph Processing Utilities

Graph processing utilities implement algorithms for path merging, scoring, and edge voting used in topology-enhanced retrieval (see [Topology-Enhanced Retrieval](#4.2)).

### Path Merging and Tuple Operations

```mermaid
graph TB
    subgraph "Tuple/Path Merging Pipeline"
        List1["list1: list of tuples<br/>Source paths"]
        List2["list2: list of tuples<br/>Extension paths"]
        
        merge["merge_tuples()<br/>Connect paths via<br/>shared endpoints"]
        
        is_continuous["is_continuous_subsequence()<br/>Check if subseq in seq"]
        
        MergedPaths["Merged Paths<br/>Extended tuples"]
    end
    
    List1 --> merge
    List2 --> merge
    merge --> MergedPaths
    
    merge -.uses.-> is_continuous
```

**Diagram: Path Merging Process**

| Function | Purpose | Algorithm |
|----------|---------|-----------|
| `is_continuous_subsequence` | Check if 2-element tuple appears consecutively in sequence | Finds all occurrences of first element, checks if next matches second |
| `merge_tuples` | Extend paths by connecting via shared endpoints | For each tuple, find matching tuples starting with last element, concatenate if not redundant |
| `count_elements_in_tuple` | Count matching elements between tuple and list | Sorted intersection counting |

**Example:**
- `list1 = [("A", "B", "C")]`
- `list2 = [("C", "D"), ("C", "E")]`
- Result: `[("A", "B", "C", "D"), ("A", "B", "C", "E")]`

**Sources:** [minirag/utils.py:341-401]()

### Path Scoring and Edge Voting

The scoring system ranks reasoning paths based on entity matches and edge support:

```mermaid
graph TB
    subgraph "Path Scoring System"
        CandidatePaths["candidate_reasoning_path<br/>dict[str, dict]"]
        MaybeAnswers["maybe_answer_list<br/>Query entities"]
        
        cal_path_score["cal_path_score_list()<br/>Score paths by<br/>entity matches"]
        
        ScoredPaths["Scored Paths<br/>With entity counts"]
        
        EdgeList["edge_list<br/>Graph edges"]
        
        edge_vote["edge_vote_path()<br/>Vote by edge<br/>support"]
        
        VotedPaths["Final Paths<br/>With edge votes"]
    end
    
    CandidatePaths --> cal_path_score
    MaybeAnswers --> cal_path_score
    cal_path_score --> ScoredPaths
    
    ScoredPaths --> edge_vote
    EdgeList --> edge_vote
    edge_vote --> VotedPaths
```

**Diagram: Path Scoring and Edge Voting Pipeline**

| Function | Purpose | Implementation |
|----------|---------|----------------|
| `cal_path_score_list` | Score paths by entity overlap | Counts how many query entities appear in each path |
| `edge_vote_path` | Vote for paths based on edge support | Counts how many graph edges support path connections |

**Data Structures:**
- Input: `candidate_reasoning_path: dict[str, {"Score": float, "Path": list[tuple]}]`
- Output: `dict[str, {"Score": float, "Path": dict[tuple, list[int]]}]` where list contains `[entity_count, edge_vote]`

These functions implement the topology-enhanced retrieval scoring mechanism that ranks reasoning paths without requiring advanced language understanding.

**Sources:** [minirag/utils.py:404-437]()

---

## Data Conversion and Serialization

### JSON Operations

```mermaid
graph LR
    subgraph "JSON Processing"
        RawResponse["LLM Response<br/>Mixed text + JSON"]
        locate["locate_json_string_body_from_string()<br/>Regex extraction"]
        JsonStr["JSON String"]
        convert["convert_response_to_json()<br/>Parse & validate"]
        JsonDict["dict"]
    end
    
    subgraph "File I/O"
        FilePath["File Path"]
        load_json["load_json()<br/>Read from disk"]
        write_json["write_json()<br/>Write to disk"]
        save_data["save_data_to_file()<br/>Write with formatting"]
        JsonObj["JSON Object"]
    end
    
    RawResponse --> locate
    locate --> JsonStr
    JsonStr --> convert
    convert --> JsonDict
    
    FilePath --> load_json
    load_json --> JsonObj
    JsonObj --> write_json
    JsonObj --> save_data
    write_json --> FilePath
    save_data --> FilePath
```

**Diagram: JSON Conversion and File I/O Functions**

| Function | Purpose | Notes |
|----------|---------|-------|
| `locate_json_string_body_from_string` | Extract JSON from mixed text | Uses regex `r"{.*}"` with DOTALL flag |
| `convert_response_to_json` | Parse LLM response to dict | Combines locate + parse, raises on error |
| `load_json` | Load JSON from file | Returns `None` if file doesn't exist |
| `write_json` | Save dict to JSON file | Uses `indent=2, ensure_ascii=False` |
| `save_data_to_file` | Alias with consistent formatting | Uses `indent=4` |

**Sources:** [minirag/utils.py:77-94](), [minirag/utils.py:129-138](), [minirag/utils.py:214-216]()

### CSV Operations

| Function | Purpose | Signature |
|----------|---------|-----------|
| `list_of_list_to_csv` | Convert 2D list to CSV string | `(data: List[List[str]]) -> str` |
| `csv_string_to_list` | Parse CSV string to 2D list | `(csv_string: str) -> List[List[str]]` |
| `process_combine_contexts` | Merge high/low level contexts | Used in context combination for queries |

The `process_combine_contexts` function [lines 310-338] is specifically designed for MiniRAG's multi-level context retrieval, merging entity-level and chunk-level contexts into a unified CSV format.

**Sources:** [minirag/utils.py:201-211](), [minirag/utils.py:310-338]()

### XML to JSON Conversion

The `xml_to_json` function [lines 219-290] supports importing graph data from GraphML format:

**Supported Schema:**
- **Nodes:** `id`, `entity_type` (d0), `description` (d1), `source_id` (d2)
- **Edges:** `source`, `target`, `weight` (d3), `description` (d4), `keywords` (d5), `source_id` (d6)

Returns: `{"nodes": [...], "edges": [...]}`

**Sources:** [minirag/utils.py:219-290]()

---

## Async Control and Decorators

### Concurrency Limiting

The `limit_async_func_call` decorator [lines 97-116] throttles async function execution:

```mermaid
graph TB
    subgraph "limit_async_func_call Decorator"
        AsyncFunc["Async Function"]
        decorator["@limit_async_func_call<br/>max_size=N"]
        
        subgraph "Execution Control"
            current_size["__current_size counter"]
            check["while __current_size >= max_size:<br/>await asyncio.sleep()"]
            increment["__current_size += 1"]
            execute["Execute function"]
            decrement["__current_size -= 1"]
        end
        
        LimitedFunc["Limited Async Function"]
    end
    
    AsyncFunc --> decorator
    decorator --> LimitedFunc
    
    LimitedFunc --> check
    check --> increment
    increment --> execute
    execute --> decrement
```

**Diagram: Async Function Concurrency Limiting**

**Parameters:**
- `max_size: int` - Maximum concurrent executions
- `waitting_time: float = 0.0001` - Sleep interval when waiting

**Usage Pattern:**
```python
@limit_async_func_call(max_size=10)
async def call_llm(prompt):
    return await llm_api(prompt)
```

This prevents overwhelming LLM APIs with too many simultaneous requests.

**Sources:** [minirag/utils.py:97-116]()

### Embedding Function Wrapper

```mermaid
graph LR
    subgraph "wrap_embedding_func_with_attrs"
        RawFunc["Async embedding function"]
        decorator["@wrap_embedding_func_with_attrs<br/>embedding_dim=<br/>max_token_size="]
        EmbeddingFunc["EmbeddingFunc instance<br/>embedding_dim<br/>max_token_size<br/>func"]
    end
    
    RawFunc --> decorator
    decorator --> EmbeddingFunc
    
    EmbeddingFunc -.used by.-> LLMInterface["LLM Interface<br/>llm/openai.py"]
```

**Diagram: EmbeddingFunc Wrapper Creation**

The `EmbeddingFunc` dataclass [lines 45-52] wraps embedding functions with metadata:

| Attribute | Type | Purpose |
|-----------|------|---------|
| `embedding_dim` | `int` | Dimensionality of embeddings |
| `max_token_size` | `int` | Maximum input token length |
| `func` | `callable` | Async embedding function |

The `wrap_embedding_func_with_attrs` decorator [lines 119-126] creates these instances, enabling uniform handling of different embedding models throughout MiniRAG.

**Sources:** [minirag/utils.py:45-52](), [minirag/utils.py:119-126]()

---

## Hashing and ID Generation

### MD5-Based Identifiers

```mermaid
graph LR
    subgraph "ID Generation"
        Content["Content string"]
        compute_mdhash["compute_mdhash_id()<br/>MD5 hash + prefix"]
        ChunkID["Chunk ID<br/>'prefix' + hash"]
        
        Args["Multiple args"]
        compute_args["compute_args_hash()<br/>Concatenate + hash"]
        CacheKey["Cache key<br/>hash string"]
    end
    
    Content --> compute_mdhash
    compute_mdhash --> ChunkID
    
    Args --> compute_args
    compute_args --> CacheKey
```

**Diagram: Hash-Based ID Generation**

| Function | Signature | Purpose |
|----------|-----------|---------|
| `compute_mdhash_id` | `(content: str, prefix: str = "") -> str` | Generate unique chunk/entity IDs |
| `compute_args_hash` | `(*args, cache_type: str \| None = None) -> str` | Generate cache keys from arguments |

Both use MD5 hashing to create deterministic, collision-resistant identifiers for content-based deduplication and caching.

**Sources:** [minirag/utils.py:55-63]()

---

## Validation Utilities

| Function | Purpose | Implementation |
|----------|---------|----------------|
| `is_float_regex` | Check if string represents a float | Regex: `^[-+]?[0-9]*\.?[0-9]+$` |

**Sources:** [minirag/utils.py:185-186]()

---

## Summary Table: Key Utility Functions by Use Case

| Use Case | Functions | Purpose |
|----------|-----------|---------|
| **Document Chunking** | `encode_string_by_tiktoken`, `truncate_list_by_token_size` | Manage token budgets |
| **Entity Extraction** | `clean_str`, `convert_response_to_json` | Clean and parse LLM outputs |
| **Similarity Search** | `calculate_similarity`, `cosine_similarity` | Rank retrieved chunks/entities |
| **Path Retrieval** | `merge_tuples`, `cal_path_score_list`, `edge_vote_path` | Score reasoning paths |
| **Context Assembly** | `process_combine_contexts`, `csv_string_to_list` | Merge multi-level contexts |
| **Deduplication** | `compute_mdhash_id` | Generate content-based IDs |
| **API Rate Limiting** | `limit_async_func_call` | Prevent API throttling |
| **Embedding Management** | `EmbeddingFunc`, `quantize_embedding` | Wrap and compress embeddings |

**Sources:** [minirag/utils.py:1-517]()

---

# Page: Text Processing

# Text Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [minirag/utils.py](minirag/utils.py)

</details>



## Purpose and Scope

This document covers the text processing utilities provided by MiniRAG in [minirag/utils.py](). These utilities handle fundamental text operations required throughout the RAG pipeline, including text cleaning, tokenization, truncation, Unicode handling, and string manipulation. These functions are used extensively during document indexing and query processing phases.

For text similarity calculations, see [Similarity Calculations](#9.2). For graph-specific data processing, see [Graph Processing Utilities](#9.3).

## Overview

The text processing utilities in MiniRAG are organized into six functional categories that support the document ingestion and query pipeline:

```mermaid
graph TB
    subgraph "Text Processing Categories"
        Cleaning["Text Cleaning<br/>clean_text, clean_str, get_content_summary"]
        Tokenization["Tokenization & Token Counting<br/>encode_string_by_tiktoken, decode_tokens_by_tiktoken"]
        Truncation["Token-Based Truncation<br/>truncate_list_by_token_size"]
        Unicode["Unicode & Encoding<br/>safe_unicode_decode"]
        Strings["String Manipulation<br/>split_string_by_multi_markers"]
        Parsing["Format Parsing<br/>locate_json_string_body_from_string, convert_response_to_json"]
    end
    
    subgraph "Usage in MiniRAG Pipeline"
        DocIngestion["Document Ingestion"]
        EntityExtraction["Entity Extraction"]
        QueryProcessing["Query Processing"]
        LLMInteraction["LLM Response Handling"]
    end
    
    Cleaning --> DocIngestion
    Tokenization --> Truncation
    Truncation --> EntityExtraction
    Truncation --> QueryProcessing
    Unicode --> DocIngestion
    Strings --> EntityExtraction
    Parsing --> LLMInteraction
    
    style Cleaning fill:#f9f9f9
    style Tokenization fill:#f9f9f9
    style Truncation fill:#f9f9f9
```

**Sources:** [minirag/utils.py:1-517]()

## Text Cleaning Functions

MiniRAG provides two levels of text cleaning to handle various input quality issues:

### Basic Cleaning: `clean_text()`

The `clean_text()` function provides lightweight cleaning for standard text inputs.

| Function | Purpose | Operations | Location |
|----------|---------|------------|----------|
| `clean_text()` | Basic text sanitization | Removes null bytes (`\x00`), strips whitespace | [minirag/utils.py:66-68]() |

```mermaid
graph LR
    Input["Raw Text Input<br/>'Hello World\x00\n'"]
    clean_text["clean_text()"]
    Output["Cleaned Text<br/>'Hello World'"]
    
    Input --> clean_text
    clean_text --> |"Strip whitespace"| Step1["Remove leading/trailing spaces"]
    Step1 --> |"Replace '\x00'"| Step2["Remove null bytes"]
    Step2 --> Output
```

**Sources:** [minirag/utils.py:66-68]()

### Advanced Cleaning: `clean_str()`

The `clean_str()` function, adapted from Microsoft's GraphRAG implementation, provides comprehensive text sanitization:

| Feature | Implementation | Purpose |
|---------|---------------|---------|
| HTML Unescaping | `html.unescape()` | Converts HTML entities like `&amp;` to `&` |
| Control Character Removal | Regex `[\x00-\x1f\x7f-\x9f]` | Removes ASCII control characters |
| Type Safety | Returns non-strings unchanged | Handles mixed input types |

```mermaid
graph TB
    Input["Input: Any Type"]
    TypeCheck{"isinstance(input, str)?"}
    Unescape["html.unescape(input.strip())"]
    RemoveControl["re.sub(r'[\x00-\x1f\x7f-\x9f]', '', result)"]
    Output["Clean String Output"]
    PassThrough["Return input unchanged"]
    
    Input --> TypeCheck
    TypeCheck -->|"Yes"| Unescape
    TypeCheck -->|"No"| PassThrough
    Unescape --> RemoveControl
    RemoveControl --> Output
```

**Sources:** [minirag/utils.py:174-182]()

### Content Summarization: `get_content_summary()`

The `get_content_summary()` function truncates long text for logging and display purposes:

```mermaid
graph LR
    Content["Document Content"]
    get_content_summary["get_content_summary()<br/>max_length=100"]
    Check{"len(content) > max_length?"}
    Truncate["content[:max_length] + '...'"]
    Full["Return full content"]
    
    Content --> get_content_summary
    get_content_summary --> Check
    Check -->|"Yes"| Truncate
    Check -->|"No"| Full
```

**Sources:** [minirag/utils.py:71-74]()

## Tokenization and Token Counting

MiniRAG uses the `tiktoken` library for tokenization, which is essential for managing context windows and truncating content to fit LLM token limits.

### Global Encoder Instance

The tokenization system maintains a global encoder to avoid repeated initialization overhead:

| Variable | Type | Purpose | Location |
|----------|------|---------|----------|
| `ENCODER` | `tiktoken.Encoding` | Global tokenizer instance | [minirag/utils.py:25]() |

### Tokenization Functions

```mermaid
graph TB
    subgraph "Tokenization Flow"
        Input["Text String"]
        encode_string_by_tiktoken["encode_string_by_tiktoken()<br/>default: 'gpt-4o'"]
        GlobalEncoder{"ENCODER is None?"}
        InitEncoder["ENCODER = tiktoken.encoding_for_model()"]
        Encode["tokens = ENCODER.encode(content)"]
        TokensOutput["List[int] tokens"]
        
        Input --> encode_string_by_tiktoken
        encode_string_by_tiktoken --> GlobalEncoder
        GlobalEncoder -->|"Yes"| InitEncoder
        GlobalEncoder -->|"No"| Encode
        InitEncoder --> Encode
        Encode --> TokensOutput
    end
    
    subgraph "Detokenization Flow"
        TokensInput["List[int] tokens"]
        decode_tokens_by_tiktoken["decode_tokens_by_tiktoken()<br/>default: 'gpt-4o'"]
        Decode["content = ENCODER.decode(tokens)"]
        StringOutput["Text String"]
        
        TokensInput --> decode_tokens_by_tiktoken
        decode_tokens_by_tiktoken --> Decode
        Decode --> StringOutput
    end
```

**Sources:** [minirag/utils.py:25](), [minirag/utils.py:141-154]()

### Token-Based Truncation

The `truncate_list_by_token_size()` function is critical for managing context window limits:

```python
# Function signature
def truncate_list_by_token_size(
    list_data: list, 
    key: callable, 
    max_token_size: int
) -> list
```

**Algorithm:**

```mermaid
graph TB
    Start["Input: list_data, key, max_token_size"]
    CheckSize{"max_token_size <= 0?"}
    ReturnEmpty["Return []"]
    InitTokens["tokens = 0"]
    IterateLoop["For i, data in enumerate(list_data)"]
    CountTokens["tokens += len(encode_string_by_tiktoken(key(data)))"]
    CheckExceed{"tokens > max_token_size?"}
    ReturnSlice["Return list_data[:i]"]
    Continue["Continue iteration"]
    ReturnFull["Return full list_data"]
    
    Start --> CheckSize
    CheckSize -->|"Yes"| ReturnEmpty
    CheckSize -->|"No"| InitTokens
    InitTokens --> IterateLoop
    IterateLoop --> CountTokens
    CountTokens --> CheckExceed
    CheckExceed -->|"Yes"| ReturnSlice
    CheckExceed -->|"No"| Continue
    Continue --> IterateLoop
    IterateLoop -->|"End"| ReturnFull
```

**Usage Example:** This function is commonly used to truncate retrieved context before sending to LLMs:

| Parameter | Type | Purpose |
|-----------|------|---------|
| `list_data` | `list` | List of items to truncate (e.g., text chunks) |
| `key` | `callable` | Function to extract text from each item |
| `max_token_size` | `int` | Maximum total tokens allowed |

**Sources:** [minirag/utils.py:189-198]()

## Unicode and Encoding Handling

### Unicode Escape Sequence Decoding

The `safe_unicode_decode()` function handles Unicode escape sequences commonly found in JSON or encoded text:

```mermaid
graph TB
    Input["Byte Content<br/>b'Hello \\u4E2D\\u6587'"]
    Pattern["Regex Pattern<br/>r'\\u([0-9a-fA-F]{4})'"]
    DecodeUTF8["content.decode('utf-8')"]
    FindMatches["Find all \\uXXXX sequences"]
    ReplaceMatch["For each match:<br/>chr(int(match, 16))"]
    Output["Decoded String<br/>'Hello 中文'"]
    
    Input --> DecodeUTF8
    DecodeUTF8 --> Pattern
    Pattern --> FindMatches
    FindMatches --> ReplaceMatch
    ReplaceMatch --> Output
```

**Implementation Details:**

| Component | Implementation | Purpose |
|-----------|---------------|---------|
| Pattern | `r'\\u([0-9a-fA-F]{4})'` | Matches Unicode escape sequences |
| Replacement | `chr(int(match.group(1), 16))` | Converts hex to Unicode character |
| Input | `bytes` | Handles byte content directly |

**Sources:** [minirag/utils.py:293-307]()

## String Manipulation

### Multi-Marker String Splitting

The `split_string_by_multi_markers()` function splits text using multiple delimiters simultaneously:

```python
# Function signature
def split_string_by_multi_markers(
    content: str, 
    markers: list[str]
) -> list[str]
```

```mermaid
graph TB
    Input["content: 'A|B;C|D'<br/>markers: ['|', ';']"]
    CheckMarkers{"markers empty?"}
    ReturnList["Return [content]"]
    EscapeMarkers["Escape each marker:<br/>re.escape()"]
    JoinPattern["Join with '|':<br/>'\\||;'"]
    Split["re.split(pattern, content)"]
    StripFilter["Strip whitespace,<br/>filter empty strings"]
    Output["['A', 'B', 'C', 'D']"]
    
    Input --> CheckMarkers
    CheckMarkers -->|"Yes"| ReturnList
    CheckMarkers -->|"No"| EscapeMarkers
    EscapeMarkers --> JoinPattern
    JoinPattern --> Split
    Split --> StripFilter
    StripFilter --> Output
```

**Key Features:**
- **Regex Escaping:** Properly escapes special regex characters in markers
- **Whitespace Handling:** Strips leading/trailing whitespace from results
- **Empty Filtering:** Removes empty strings from output

**Sources:** [minirag/utils.py:164-169]()

## Format Parsing and Conversion

### JSON Extraction from Text

MiniRAG provides utilities to extract and parse JSON from LLM responses:

```mermaid
graph TB
    subgraph "JSON Extraction Pipeline"
        Response["LLM Response Text<br/>'Here is the data: {...}'"]
        locate_json_string_body_from_string["locate_json_string_body_from_string()"]
        RegexSearch["re.search(r'{.*}', content, re.DOTALL)"]
        CheckMatch{"Match found?"}
        ExtractGroup["maybe_json_str.group(0)"]
        ReturnNone["Return None"]
        JSONStr["JSON String: '{...}'"]
        
        Response --> locate_json_string_body_from_string
        locate_json_string_body_from_string --> RegexSearch
        RegexSearch --> CheckMatch
        CheckMatch -->|"Yes"| ExtractGroup
        CheckMatch -->|"No"| ReturnNone
        ExtractGroup --> JSONStr
    end
    
    subgraph "JSON Parsing"
        JSONInput["JSON String or Text"]
        convert_response_to_json["convert_response_to_json()"]
        Extract["locate_json_string_body_from_string()"]
        Assert{"JSON found?"}
        Parse["json.loads(json_str)"]
        ErrorHandle["Log error, raise JSONDecodeError"]
        DictOutput["dict"]
        
        JSONInput --> convert_response_to_json
        convert_response_to_json --> Extract
        Extract --> Assert
        Assert -->|"Yes"| Parse
        Assert -->|"No"| ErrorHandle
        Parse -->|"Success"| DictOutput
        Parse -->|"Failure"| ErrorHandle
    end
```

| Function | Returns | Error Handling | Location |
|----------|---------|----------------|----------|
| `locate_json_string_body_from_string()` | `str \| None` | Returns `None` if no JSON found | [minirag/utils.py:77-83]() |
| `convert_response_to_json()` | `dict` | Raises assertion/JSONDecodeError with logging | [minirag/utils.py:86-94]() |

**Sources:** [minirag/utils.py:77-94]()

### CSV Format Conversion

MiniRAG uses CSV format for serializing structured context data:

```mermaid
graph LR
    subgraph "List to CSV"
        ListData["List[List[str]]<br/>[['A', 'B'], ['C', 'D']]"]
        list_of_list_to_csv["list_of_list_to_csv()"]
        StringIO1["io.StringIO()"]
        CSVWriter["csv.writer()"]
        WriteRows["writer.writerows()"]
        CSVString["CSV String<br/>'A,B\nC,D\n'"]
        
        ListData --> list_of_list_to_csv
        list_of_list_to_csv --> StringIO1
        StringIO1 --> CSVWriter
        CSVWriter --> WriteRows
        WriteRows --> CSVString
    end
    
    subgraph "CSV to List"
        CSVInput["CSV String<br/>'A,B\nC,D\n'"]
        csv_string_to_list["csv_string_to_list()"]
        StringIO2["io.StringIO()"]
        CSVReader["csv.reader()"]
        IterateRows["Iterate rows"]
        ListOutput["List[List[str]]<br/>[['A', 'B'], ['C', 'D']]"]
        
        CSVInput --> csv_string_to_list
        csv_string_to_list --> StringIO2
        StringIO2 --> CSVReader
        CSVReader --> IterateRows
        IterateRows --> ListOutput
    end
```

**Usage in MiniRAG:** These functions are used to serialize context data for LLM prompts and deserialize structured responses.

**Sources:** [minirag/utils.py:201-211]()

## Hash Functions for Content Identification

### MD5 Hash Generation

MiniRAG uses MD5 hashing for generating unique identifiers:

```mermaid
graph TB
    subgraph "Content Hashing: compute_mdhash_id()"
        Content["content: str"]
        Prefix["prefix: str = ''"]
        Encode["content.encode()"]
        MD5["md5(encoded)"]
        Hexdigest["hexdigest()"]
        Concat["prefix + hash"]
        Output["Hash ID: 'prefix_abc123...'"]
        
        Content --> Encode
        Prefix --> Concat
        Encode --> MD5
        MD5 --> Hexdigest
        Hexdigest --> Concat
        Concat --> Output
    end
    
    subgraph "Argument Hashing: compute_args_hash()"
        Args["*args"]
        CacheType["cache_type: str | None"]
        JoinArgs["''.join([str(arg) for arg in args])"]
        CheckType{"cache_type provided?"}
        AddType["f'{cache_type}:{args_str}'"]
        NoType["args_str"]
        EncodeMD5["md5(args_str.encode())"]
        HashOutput["Hash: 'def456...'"]
        
        Args --> JoinArgs
        CacheType --> CheckType
        JoinArgs --> CheckType
        CheckType -->|"Yes"| AddType
        CheckType -->|"No"| NoType
        AddType --> EncodeMD5
        NoType --> EncodeMD5
        EncodeMD5 --> HashOutput
    end
```

| Function | Parameters | Purpose | Usage |
|----------|-----------|---------|-------|
| `compute_mdhash_id()` | `content: str, prefix: str` | Generate prefixed content hash | Document IDs, chunk IDs |
| `compute_args_hash()` | `*args, cache_type: str \| None` | Generate hash from multiple arguments | Cache keys, deduplication |

**Sources:** [minirag/utils.py:55-63]()

## Integration with MiniRAG Pipeline

The text processing utilities integrate throughout the MiniRAG system:

```mermaid
graph TB
    subgraph "Document Ingestion Phase"
        RawDocs["Raw Documents"]
        clean_str["clean_str()"]
        clean_text["clean_text()"]
        safe_unicode_decode["safe_unicode_decode()"]
        CleanedDocs["Cleaned Documents"]
        
        RawDocs --> clean_str
        clean_str --> clean_text
        clean_text --> safe_unicode_decode
        safe_unicode_decode --> CleanedDocs
    end
    
    subgraph "Chunking and Truncation"
        CleanedDocs --> ChunkingLogic["Chunking Logic"]
        ChunkingLogic --> truncate_list_by_token_size["truncate_list_by_token_size()"]
        ChunkingLogic --> compute_mdhash_id["compute_mdhash_id()"]
        truncate_list_by_token_size --> Chunks["Token-Limited Chunks"]
        compute_mdhash_id --> ChunkIDs["Chunk IDs"]
    end
    
    subgraph "Entity Extraction"
        Chunks --> LLMPrompt["LLM Prompt"]
        LLMPrompt --> LLMResponse["LLM Response"]
        LLMResponse --> locate_json_string_body_from_string["locate_json_string_body_from_string()"]
        locate_json_string_body_from_string --> convert_response_to_json["convert_response_to_json()"]
        convert_response_to_json --> Entities["Extracted Entities"]
    end
    
    subgraph "Query Processing"
        UserQuery["User Query"]
        UserQuery --> clean_str
        encode_string_by_tiktoken["encode_string_by_tiktoken()"]
        UserQuery --> encode_string_by_tiktoken
        encode_string_by_tiktoken --> TokenCount["Token Count Check"]
    end
    
    subgraph "Context Preparation"
        RetrievedContext["Retrieved Context"]
        list_of_list_to_csv["list_of_list_to_csv()"]
        RetrievedContext --> list_of_list_to_csv
        list_of_list_to_csv --> truncate_list_by_token_size
        truncate_list_by_token_size --> FinalContext["Token-Limited Context"]
    end
```

**Sources:** [minirag/utils.py:1-517]()

## Summary Table of Text Processing Functions

| Category | Function | Input | Output | Primary Use Case |
|----------|----------|-------|--------|------------------|
| **Cleaning** | `clean_text()` | `str` | `str` | Remove null bytes and whitespace |
| | `clean_str()` | `Any` | `str` | Remove HTML entities and control chars |
| | `get_content_summary()` | `str, int` | `str` | Truncate for display |
| **Tokenization** | `encode_string_by_tiktoken()` | `str, str` | `list[int]` | Count tokens, encode text |
| | `decode_tokens_by_tiktoken()` | `list[int], str` | `str` | Decode tokens to text |
| **Truncation** | `truncate_list_by_token_size()` | `list, callable, int` | `list` | Limit context by token count |
| **Unicode** | `safe_unicode_decode()` | `bytes` | `str` | Decode Unicode escapes |
| **String Ops** | `split_string_by_multi_markers()` | `str, list[str]` | `list[str]` | Split by multiple delimiters |
| **Parsing** | `locate_json_string_body_from_string()` | `str` | `str \| None` | Extract JSON from text |
| | `convert_response_to_json()` | `str` | `dict` | Parse JSON from LLM response |
| **CSV** | `list_of_list_to_csv()` | `List[List[str]]` | `str` | Serialize to CSV format |
| | `csv_string_to_list()` | `str` | `List[List[str]]` | Parse CSV to list |
| **Hashing** | `compute_mdhash_id()` | `str, str` | `str` | Generate content hash ID |
| | `compute_args_hash()` | `*args, str \| None` | `str` | Generate argument hash |

**Sources:** [minirag/utils.py:1-517]()

---

# Page: Similarity Calculations

# Similarity Calculations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [minirag/utils.py](minirag/utils.py)

</details>



This page documents the text similarity calculation utilities provided in [minirag/utils.py:466-517](). These functions enable MiniRAG to compare and rank text passages based on various similarity metrics. The primary use case is selecting the most relevant sentences or chunks when processing queries or performing entity matching.

For information about graph-specific path scoring and ranking utilities, see [Graph Processing Utilities](#9.3). For text preprocessing operations before similarity calculation, see [Text Processing](#9.1).

## Overview

The similarity calculation module provides six distinct similarity measurement methods, each with different characteristics and computational requirements. The main entry point is the `calculate_similarity` function, which returns the indices of the top-k most similar sentences to a target text.

**Sources:** [minirag/utils.py:466-517]()

## Function Signature and Parameters

```python
calculate_similarity(sentences, target, method="levenshtein", n=1, k=1)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sentences` | List[str] | Required | List of candidate sentences to compare against target |
| `target` | str | Required | Reference text to measure similarity against |
| `method` | str | `"levenshtein"` | Similarity algorithm: `"jaccard"`, `"levenshtein"`, `"rouge"`, `"bert"`, `"overlap"`, or `"bleu"` |
| `n` | int | 1 | ROUGE-n gram size (only used when method=`"rouge"`) |
| `k` | int | 1 | Number of top-k most similar sentence indices to return |

**Returns:** `List[int]` - Indices of the k most similar sentences, sorted by similarity score (highest first)

**Sources:** [minirag/utils.py:466-467]()

## Similarity Methods

### Method Comparison Flow

```mermaid
graph TB
    Input["calculate_similarity()<br/>sentences + target"]
    
    subgraph "Token-Based Methods"
        Jaccard["Jaccard<br/>Set Intersection/Union"]
        Overlap["Overlap<br/>Min-normalized Intersection"]
        Levenshtein["Levenshtein<br/>Edit Distance"]
        BLEU["BLEU<br/>N-gram Precision"]
    end
    
    subgraph "Sequence Methods"
        ROUGE["ROUGE<br/>N-gram F-score"]
    end
    
    subgraph "Embedding Methods"
        BERT["BERT<br/>Semantic Embeddings"]
    end
    
    Input --> Jaccard
    Input --> Overlap
    Input --> Levenshtein
    Input --> BLEU
    Input --> ROUGE
    Input --> BERT
    
    Jaccard --> Scoring["Score & Rank"]
    Overlap --> Scoring
    Levenshtein --> Scoring
    BLEU --> Scoring
    ROUGE --> Scoring
    BERT --> Scoring
    
    Scoring --> Output["Top-k Indices"]
    
    style Input fill:#f9f9f9
    style Output fill:#f9f9f9
```

**Sources:** [minirag/utils.py:469-514]()

### Jaccard Similarity

Measures overlap between token sets using the Jaccard coefficient: |A ∩ B| / |A ∪ B|

**Implementation:** [minirag/utils.py:469-475]()

```python
# Tokenizes to lowercase words
sentence_tokens = sentence.lower().split()
target_tokens = target.lower().split()
# Computes set intersection and union
intersection = set(sentence_tokens).intersection(set(target_tokens))
union = set(sentence_tokens).union(set(target_tokens))
jaccard_score = len(intersection) / len(union) if union else 0
```

**Characteristics:**
- Fast computation (O(n) where n is number of tokens)
- Order-independent
- Good for keyword matching
- Range: [0, 1]

**Sources:** [minirag/utils.py:469-475]()

### Levenshtein Distance

Computes normalized edit distance between token sequences. Measures the minimum number of single-token edits (insertions, deletions, substitutions) required to transform one sequence into another.

**Implementation:** [minirag/utils.py:476-481]()

```python
# Uses nltk.metrics.edit_distance
distance = edit_distance(target_tokens, sentence.lower().split())
# Normalizes by maximum sequence length
similarity = 1 - (distance / max(len(target_tokens), len(sentence.split())))
```

**Characteristics:**
- Order-sensitive
- Accounts for token position differences
- Normalized to [0, 1] range
- Moderate computational cost (O(mn) dynamic programming)

**Dependencies:** `nltk.metrics.edit_distance` [minirag/utils.py:17]()

**Sources:** [minirag/utils.py:476-481]()

### ROUGE Score

Uses ROUGE (Recall-Oriented Understudy for Gisting Evaluation) to measure n-gram overlap with F-score weighting.

**Implementation:** [minirag/utils.py:482-487]()

```python
from rouge import Rouge
rouge = Rouge()
scores = rouge.get_scores(sentence, target)
rouge_score = scores[0].get(f"rouge-{n}", {}).get("f", 0)
```

**Characteristics:**
- Designed for summarization evaluation
- Balances precision and recall via F-score
- Configurable n-gram size (typically n=1 or n=2)
- Range: [0, 1]

**Dependencies:** `rouge.Rouge` [minirag/utils.py:18]()

**Sources:** [minirag/utils.py:482-487]()

### BERT Embeddings

Computes semantic similarity using pre-trained sentence embeddings from the `sentence-transformers` library.

**Implementation:** [minirag/utils.py:489-495]()

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
# Encode all sentences plus target
embeddings = model.encode(sentences + [target])
target_vec = embeddings[-1]
# Compute cosine similarity
similarity = np.dot(embeddings[i], target_vec) / 
             (np.linalg.norm(embeddings[i]) * np.linalg.norm(target_vec))
```

**Characteristics:**
- Captures semantic meaning beyond lexical overlap
- Best for paraphrase detection
- Highest computational cost (neural network inference)
- Model: `all-MiniLM-L6-v2` (produces 384-dimensional embeddings)
- Range: [-1, 1], typically [0, 1] for similar sentences

**Dependencies:** `sentence_transformers.SentenceTransformer` [minirag/utils.py:20]()

**Sources:** [minirag/utils.py:489-495]()

### Overlap Coefficient

Measures the ratio of common tokens to the size of the smaller set. This is particularly useful when comparing texts of significantly different lengths.

**Implementation:** [minirag/utils.py:497-502]()

```python
sentence_tokens = set(sentence.lower().split())
overlap = sentence_tokens.intersection(set(target_tokens))
score = len(overlap) / min(len(sentence_tokens), len(target_tokens))
```

**Characteristics:**
- Normalizes by smaller set (more lenient than Jaccard)
- Good for subset matching
- Fast computation (O(n))
- Range: [0, 1]

**Sources:** [minirag/utils.py:497-502]()

### BLEU Score

Uses BLEU (Bilingual Evaluation Understudy) to measure n-gram precision with length penalty. Originally designed for machine translation evaluation.

**Implementation:** [minirag/utils.py:504-510]()

```python
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
smooth_fn = SmoothingFunction().method1
target_tokens_bleu = word_tokenize(target.lower())
sentence_tokens_bleu = word_tokenize(sentence.lower())
score = sentence_bleu([target_tokens_bleu], sentence_tokens_bleu, 
                      smoothing_function=smooth_fn)
```

**Characteristics:**
- Precision-oriented (rewards matching n-grams)
- Uses smoothing to handle zero counts
- Considers multiple n-gram sizes (1-4 grams by default)
- Range: [0, 1]

**Dependencies:** `nltk.translate.bleu_score`, `nltk.tokenize.word_tokenize` [minirag/utils.py:19,22]()

**Sources:** [minirag/utils.py:504-510]()

## Vector Similarity Utilities

The module also provides lower-level vector operations used by embedding-based methods and throughout MiniRAG's vector storage operations.

### cosine_similarity Function

Computes the cosine similarity between two numpy arrays, representing the cosine of the angle between vectors in n-dimensional space.

**Implementation:** [minirag/utils.py:443-447]()

```python
def cosine_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    return dot_product / (norm1 * norm2)
```

**Formula:** `cos(θ) = (v1 · v2) / (||v1|| × ||v2||)`

**Range:** [-1, 1] where:
- 1 = identical direction
- 0 = orthogonal (no similarity)
- -1 = opposite direction

**Sources:** [minirag/utils.py:443-447]()

### Embedding Quantization

Reduces memory footprint of embeddings by converting float32 values to lower-bit representations.

```mermaid
graph LR
    Float32["float32 Embedding<br/>32 bits per value"]
    Quantize["quantize_embedding()<br/>Scale to [0, 2^bits-1]"]
    Uint8["uint8 Quantized<br/>8 bits per value<br/>+ min/max metadata"]
    Dequantize["dequantize_embedding()<br/>Rescale to original range"]
    Recovered["float32 Approximation"]
    
    Float32 --> Quantize
    Quantize --> Uint8
    Uint8 --> Dequantize
    Dequantize --> Recovered
    
    style Float32 fill:#f9f9f9
    style Uint8 fill:#f9f9f9
    style Recovered fill:#f9f9f9
```

**Sources:** [minirag/utils.py:450-463]()

#### quantize_embedding

**Implementation:** [minirag/utils.py:450-456]()

```python
def quantize_embedding(embedding: np.ndarray | list[float], bits: int = 8):
    embedding = np.array(embedding)
    min_val = embedding.min()
    max_val = embedding.max()
    scale = (2**bits - 1) / (max_val - min_val)
    quantized = np.round((embedding - min_val) * scale).astype(np.uint8)
    return quantized, min_val, max_val
```

**Parameters:**
- `embedding`: Original float embedding vector
- `bits`: Quantization bit depth (default: 8)

**Returns:** `(quantized, min_val, max_val)` tuple

**Storage Reduction:** 75% reduction (32 bits → 8 bits per dimension)

**Sources:** [minirag/utils.py:450-456]()

#### dequantize_embedding

**Implementation:** [minirag/utils.py:459-463]()

```python
def dequantize_embedding(quantized: np.ndarray, min_val: float, 
                        max_val: float, bits=8) -> np.ndarray:
    scale = (max_val - min_val) / (2**bits - 1)
    return (quantized * scale + min_val).astype(np.float32)
```

**Parameters:**
- `quantized`: Quantized uint8 array
- `min_val`: Original minimum value
- `max_val`: Original maximum value
- `bits`: Quantization bit depth

**Returns:** `np.ndarray` - Reconstructed float32 embedding

**Sources:** [minirag/utils.py:459-463]()

## Integration with MiniRAG System

```mermaid
graph TB
    subgraph "MiniRAG Query Pipeline"
        Query["User Query"]
        EntityExtract["Entity Extraction<br/>operate.py"]
        VectorSearch["Vector Search<br/>BaseVectorStorage"]
    end
    
    subgraph "Similarity Calculations"
        CalcSim["calculate_similarity()"]
        
        subgraph "Method Selection"
            FastMethods["Fast Methods<br/>Jaccard, Overlap<br/>Levenshtein"]
            SlowMethods["Semantic Methods<br/>BERT, ROUGE, BLEU"]
        end
        
        CalcSim --> FastMethods
        CalcSim --> SlowMethods
    end
    
    subgraph "Storage Layer"
        Chunks["Text Chunks<br/>BaseKVStorage"]
        Embeddings["Embeddings<br/>quantize/dequantize"]
        VectorDB["Vector Databases<br/>cosine_similarity"]
    end
    
    Query --> EntityExtract
    EntityExtract --> VectorSearch
    VectorSearch --> VectorDB
    
    VectorDB --> CalcSim
    Chunks --> CalcSim
    
    VectorDB --> Embeddings
    Embeddings --> CalcSim
    
    CalcSim --> Ranking["Ranked Results"]
    
    style CalcSim fill:#f9f9f9
    style Ranking fill:#f9f9f9
```

**Sources:** [minirag/utils.py:443-517](), [minirag/operate.py](), [minirag/storage/base.py]()

### Usage Contexts

| Context | Typical Method | Rationale |
|---------|---------------|-----------|
| Entity name matching | `overlap` or `jaccard` | Fast, handles partial matches |
| Chunk retrieval ranking | `levenshtein` | Balances speed and accuracy |
| Semantic query expansion | `bert` | Captures meaning beyond keywords |
| Answer evaluation | `rouge` or `bleu` | Standard metrics for generation quality |
| Duplicate detection | `jaccard` | Fast, order-independent |

**Sources:** [minirag/utils.py:466-517]()

## Method Selection Guidelines

```mermaid
graph TD
    Start["Choose Similarity Method"]
    
    Semantic{"Semantic<br/>Understanding<br/>Needed?"}
    Speed{"Speed<br/>Critical?"}
    Order{"Order<br/>Matters?"}
    Length{"Comparing<br/>Different<br/>Lengths?"}
    
    Start --> Semantic
    
    Semantic -->|Yes| BERT["Use BERT<br/>Best semantic quality<br/>Slowest"]
    Semantic -->|No| Speed
    
    Speed -->|Yes| Order
    Speed -->|No| ROUGE["Use ROUGE/BLEU<br/>Good for summaries<br/>Medium speed"]
    
    Order -->|Yes| Levenshtein["Use Levenshtein<br/>Position-sensitive<br/>Fast"]
    Order -->|No| Length
    
    Length -->|Yes| Overlap["Use Overlap<br/>Length-normalized<br/>Fastest"]
    Length -->|No| Jaccard["Use Jaccard<br/>Standard baseline<br/>Fastest"]
    
    style Start fill:#f9f9f9
    style BERT fill:#f9f9f9
    style Levenshtein fill:#f9f9f9
    style Overlap fill:#f9f9f9
    style Jaccard fill:#f9f9f9
    style ROUGE fill:#f9f9f9
```

**Sources:** [minirag/utils.py:466-517]()

## Example Usage

### Basic Similarity Calculation

```python
from minirag.utils import calculate_similarity

sentences = [
    "The cat sat on the mat",
    "A feline rested on the rug",
    "Dogs are great pets",
    "The mat had a cat on it"
]

target = "cat sitting on mat"

# Get top 2 most similar using Levenshtein
indices = calculate_similarity(sentences, target, method="levenshtein", k=2)
# Returns: [0, 3] - indices of most similar sentences

# Use BERT for semantic similarity
semantic_indices = calculate_similarity(sentences, target, method="bert", k=2)
# Returns: [1, 0] - "feline" and "rug" semantically similar

# Fast keyword matching
keyword_indices = calculate_similarity(sentences, target, method="jaccard", k=2)
# Returns: [0, 3] - exact word overlap
```

**Sources:** [minirag/utils.py:466-517]()

### Vector Operations

```python
from minirag.utils import cosine_similarity, quantize_embedding, dequantize_embedding
import numpy as np

# Compute cosine similarity
v1 = np.array([1.0, 2.0, 3.0])
v2 = np.array([2.0, 4.0, 6.0])
similarity = cosine_similarity(v1, v2)  # Returns: 1.0 (parallel vectors)

# Quantize embeddings for storage
embedding = np.random.randn(384)  # Typical BERT embedding
quantized, min_val, max_val = quantize_embedding(embedding, bits=8)
# quantized is uint8, 75% smaller

# Restore for computation
restored = dequantize_embedding(quantized, min_val, max_val, bits=8)
# Small approximation error, significant space savings
```

**Sources:** [minirag/utils.py:443-463]()

## Performance Characteristics

| Method | Time Complexity | Space | Semantic Quality | Best Use Case |
|--------|----------------|-------|------------------|---------------|
| Jaccard | O(n) | O(n) | Low | Keyword matching |
| Overlap | O(n) | O(n) | Low | Subset detection |
| Levenshtein | O(mn) | O(mn) | Medium | Sequence comparison |
| ROUGE | O(n) | O(n) | Medium | Summary evaluation |
| BLEU | O(n) | O(n) | Medium | Translation quality |
| BERT | O(batch×d²) | O(d) | High | Semantic similarity |

**Legend:**
- n, m = sequence lengths
- d = embedding dimension (typically 384)
- batch = number of sentences

**Sources:** [minirag/utils.py:466-517]()

## Error Handling

The `calculate_similarity` function raises a `ValueError` if an unsupported method is specified:

```python
try:
    indices = calculate_similarity(sentences, target, method="unknown")
except ValueError as e:
    # "Unsupported method. Choose from 'jaccard', 'levenshtein', 
    # 'rouge', 'bert', 'overlap', or 'bleu'."
    print(e)
```

**Sources:** [minirag/utils.py:514]()

## Dependencies

The following external libraries are required for full functionality:

| Library | Purpose | Required For |
|---------|---------|--------------|
| `nltk` | Edit distance, BLEU, tokenization | Levenshtein, BLEU methods |
| `rouge` | ROUGE score computation | ROUGE method |
| `sentence-transformers` | Pre-trained BERT models | BERT method |
| `scikit-learn` | TF-IDF vectorization (imported but unused) | - |
| `numpy` | Vector operations | All embedding operations |

**Sources:** [minirag/utils.py:16-23]()

---

# Page: Graph Processing Utilities

# Graph Processing Utilities

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [minirag/kg/networkx_impl.py](minirag/kg/networkx_impl.py)
- [minirag/utils.py](minirag/utils.py)

</details>



This page documents the graph-specific utility functions in MiniRAG that support topology-enhanced retrieval operations. These utilities handle path construction, merging, scoring, and validation within the knowledge graph structure.

For general text processing utilities, see [Text Processing](#9.1). For similarity calculation methods, see [Similarity Calculations](#9.2). For the storage implementations that use these utilities, see [Graph Storage Backends](#5.1).

## Purpose and Scope

The graph processing utilities in [minirag/utils.py]() provide specialized functions for working with graph paths and reasoning chains. These utilities are essential for MiniRAG's topology-enhanced retrieval mechanism, which constructs and evaluates reasoning paths through the heterogeneous knowledge graph to answer queries.

The primary responsibilities of these utilities include:
- **Path Construction**: Merging edge tuples to build multi-hop reasoning paths
- **Path Validation**: Checking path continuity and subsequence relationships
- **Path Scoring**: Ranking paths based on entity overlap and edge voting
- **Path Extension**: Supporting k-hop neighbor traversal operations

Sources: [minirag/utils.py:341-437]()

## Core Graph Utility Functions

### Function Overview

```mermaid
graph TB
    subgraph "Path Construction"
        merge_tuples["merge_tuples()<br/>lines 362-386"]
        is_continuous["is_continuous_subsequence()<br/>lines 341-359"]
        merge_tuples --> is_continuous
    end
    
    subgraph "Path Scoring"
        count_elements["count_elements_in_tuple()<br/>lines 389-401"]
        cal_path_score["cal_path_score_list()<br/>lines 404-413"]
        edge_vote["edge_vote_path()<br/>lines 416-437"]
        
        count_elements --> cal_path_score
        is_continuous --> edge_vote
    end
    
    subgraph "Graph Storage Integration"
        get_neighbors["get_neighbors_within_k_hops()<br/>networkx_impl.py:177-193"]
        merge_tuples --> get_neighbors
    end
    
    subgraph "Query Processing"
        query_engine["Query Modes<br/>operate.py"]
        cal_path_score --> query_engine
        edge_vote --> query_engine
    end
    
    style merge_tuples fill:#f9f9f9
    style is_continuous fill:#f9f9f9
    style count_elements fill:#f9f9f9
    style cal_path_score fill:#f9f9f9
    style edge_vote fill:#f9f9f9
```

Sources: [minirag/utils.py:341-437](), [minirag/kg/networkx_impl.py:177-193]()

## Path Construction and Merging

### Tuple Merging for Path Extension

The `merge_tuples()` function [minirag/utils.py:362-386]() is the core path construction utility. It takes two lists of tuples representing graph edges or paths and merges them by connecting paths where the last element of one tuple matches the first element of another.

**Function Signature:**
```python
def merge_tuples(list1, list2):
    """
    Merges tuples from list1 and list2 by connecting paths.
    
    Args:
        list1: List of tuples representing initial paths
        list2: List of tuples representing potential extensions
    
    Returns:
        List of merged tuples with extended paths
    """
```

**Algorithm:**
1. For each tuple in `list1`, extract the last element
2. Find tuples in `list2` where the first element matches this last element
3. Check if the potential merge would create a cycle (using `is_continuous_subsequence()`)
4. If valid, append the remaining elements from the `list2` tuple to create an extended path
5. If no merge is possible, keep the original tuple

**Example Operation:**

```mermaid
graph LR
    subgraph "Input: list1"
        L1A["('A', 'B')"]
        L1B["('C', 'D')"]
    end
    
    subgraph "Input: list2"
        L2A["('B', 'E')"]
        L2B["('D', 'F')"]
        L2C["('E', 'G')"]
    end
    
    subgraph "Output: result"
        R1["('A', 'B', 'E')"]
        R2["('C', 'D', 'F')"]
    end
    
    L1A --> R1
    L2A --> R1
    L1B --> R2
    L2B --> R2
    
    style R1 fill:#f9f9f9
    style R2 fill:#f9f9f9
```

Sources: [minirag/utils.py:362-386]()

### Continuity and Cycle Detection

The `is_continuous_subsequence()` function [minirag/utils.py:341-359]() validates whether a 2-element subsequence appears consecutively in a larger sequence. This prevents cycles and ensures path validity during merging.

**Function Signature:**
```python
def is_continuous_subsequence(subseq, seq):
    """
    Check if a 2-element subsequence appears consecutively in seq.
    
    Args:
        subseq: Tuple with 2 elements (edge)
        seq: Longer tuple (path)
    
    Returns:
        bool: True if subseq appears consecutively in seq
    """
```

**Implementation Details:**
- Uses a helper function `find_all_indexes()` to locate all occurrences of the first element
- For each occurrence, checks if the next element matches the second element of the subsequence
- Returns `True` if any consecutive match is found

**Usage in merge_tuples:**
```python
# Check if edge already exists in path (lines 374-376)
if is_continuous_subsequence(match, tup) or is_continuous_subsequence(matchh, tup):
    continue  # Skip to avoid cycles
```

Sources: [minirag/utils.py:341-359](), [minirag/utils.py:374-376]()

### Integration with k-Hop Traversal

The `get_neighbors_within_k_hops()` method in NetworkXStorage [minirag/kg/networkx_impl.py:177-193]() uses `merge_tuples()` to iteratively expand paths:

```mermaid
sequenceDiagram
    participant Caller as "Query Processing"
    participant GNK as "get_neighbors_within_k_hops()"
    participant Graph as "NetworkX Graph"
    participant MT as "merge_tuples()"
    
    Caller->>GNK: get_neighbors_within_k_hops(node_id, k=3)
    GNK->>Graph: Get initial edges from node
    
    loop For each hop (count < k)
        GNK->>GNK: Copy current edge list
        loop For each edge pair
            GNK->>Graph: Get edges from last node
            GNK->>MT: merge_tuples(current_edges, new_edges)
            MT-->>GNK: Extended paths
        end
    end
    
    GNK-->>Caller: All k-hop paths from node
```

**Code Reference:**
```python
# Lines 184-192 in networkx_impl.py
while count<k:
    count = count+1
    sc_edge = copy.deepcopy(source_edge)
    source_edge =[]
    for pair in sc_edge:
        append_edge = list(self._graph.edges(pair[-1]))
        for tuples in merge_tuples([pair],append_edge):
            source_edge.append(tuples)
```

Sources: [minirag/kg/networkx_impl.py:177-193](), [minirag/kg/networkx_impl.py:67]()

## Path Scoring and Ranking

### Element Counting in Paths

The `count_elements_in_tuple()` function [minirag/utils.py:389-401]() counts how many elements from a target list appear in a given path tuple. This is used to score paths based on their overlap with query entities or answer candidates.

**Function Signature:**
```python
def count_elements_in_tuple(tuple_elements, list_elements):
    """
    Count matching elements between tuple and list.
    
    Args:
        tuple_elements: Tuple of node IDs in a path
        list_elements: List of target entities
    
    Returns:
        int: Count of matching elements
    """
```

**Algorithm:**
- Sorts both inputs for efficient comparison
- Uses a two-pointer technique to count matches
- Time complexity: O(n log n + m log m) for sorting, O(n + m) for counting

Sources: [minirag/utils.py:389-401]()

### Reasoning Path Score Calculation

The `cal_path_score_list()` function [minirag/utils.py:404-413]() scores candidate reasoning paths based on entity overlap with answer candidates.

**Function Signature:**
```python
def cal_path_score_list(candidate_reasoning_path, maybe_answer_list):
    """
    Calculate scores for reasoning paths based on entity overlap.
    
    Args:
        candidate_reasoning_path: Dict with path candidates and initial scores
        maybe_answer_list: List of potential answer entities
    
    Returns:
        Dict with updated path scores based on entity overlap
    """
```

**Input/Output Structure:**

| Input Structure | Output Structure |
|----------------|------------------|
| `{key: {"Score": float, "Path": [paths]}}` | `{key: {"Score": float, "Path": {path: [score]}}}` |
| Paths are lists of tuples | Each path mapped to list with overlap count |

**Scoring Logic:**
```python
# For each candidate path (lines 406-412)
for p in paths:
    scores[p] = [count_elements_in_tuple(p, maybe_answer_list)]
```

Sources: [minirag/utils.py:404-413]()

### Edge Voting Mechanism

The `edge_vote_path()` function [minirag/utils.py:416-437]() validates and scores paths by counting how many edges from the retrieved edge list appear consecutively in each path.

**Function Signature:**
```python
def edge_vote_path(path_dict, edge_list):
    """
    Vote on paths based on edge presence.
    
    Args:
        path_dict: Dict with paths and initial scores
        edge_list: List of dicts with 'src_id' and 'tgt_id'
    
    Returns:
        Tuple of (updated_path_dict, pairs_append_dict)
    """
```

**Voting Process:**

```mermaid
graph TB
    subgraph "Input"
        PD["path_dict<br/>{path_id: {Score, Path: {tuple: [overlap_score]}}}"]
        EL["edge_list<br/>[{src_id, tgt_id}, ...]"]
    end
    
    subgraph "Processing"
        Convert["Convert edge_list<br/>to tuple list"]
        Iterate["Iterate paths<br/>in path_dict"]
        Check["Check each edge<br/>for continuous<br/>subsequence"]
        Count["Increment vote<br/>count"]
    end
    
    subgraph "Output"
        Updated["path_dict with<br/>vote counts appended"]
        Pairs["pairs_append dict<br/>mapping paths to<br/>matching edges"]
    end
    
    PD --> Iterate
    EL --> Convert
    Convert --> Check
    Iterate --> Check
    Check --> Count
    Count --> Updated
    Count --> Pairs
    
    style Updated fill:#f9f9f9
    style Pairs fill:#f9f9f9
```

**Implementation Details:**
```python
# Convert edge list to tuples (lines 420-421)
for i in edge_list:
    EDGELIST.append((i["src_id"], i["tgt_id"]))

# Vote on each path (lines 427-433)
for pairs in EDGELIST:
    if is_continuous_subsequence(pairs, j[0]):
        count = count + 1
        # Track which edges voted for this path
        if j[0] not in pairs_append:
            pairs_append[j[0]] = [pairs]
        else:
            pairs_append[j[0]].append(pairs)
```

**Return Values:**
1. **return_dict**: Deep copy of path_dict with vote counts appended to each path's score list
2. **pairs_append**: Dict mapping each path tuple to the list of edges that voted for it

Sources: [minirag/utils.py:416-437]()

## Utility Function Relationships

### Data Flow in Query Processing

The graph utilities work together to support the topology-enhanced retrieval pipeline:

```mermaid
graph TB
    subgraph "1. Path Discovery"
        Q["Query Entities<br/>Extracted from<br/>user question"]
        GN["get_neighbors_within_k_hops()<br/>Build k-hop paths"]
        MT["merge_tuples()<br/>Extend paths"]
        Q --> GN
        GN --> MT
        MT --> GN
    end
    
    subgraph "2. Path Collection"
        CP["Candidate<br/>Reasoning Paths<br/>{id: {Score, Path}}"]
        GN --> CP
    end
    
    subgraph "3. Entity-Based Scoring"
        MAL["Maybe Answer List<br/>Potential entities"]
        CPS["cal_path_score_list()<br/>Score by overlap"]
        CET["count_elements_in_tuple()<br/>Count matches"]
        CP --> CPS
        MAL --> CPS
        CPS --> CET
    end
    
    subgraph "4. Edge-Based Validation"
        EL["Edge List<br/>Retrieved edges"]
        EVP["edge_vote_path()<br/>Vote on paths"]
        ICS["is_continuous_subsequence()<br/>Validate edges"]
        CPS --> EVP
        EL --> EVP
        EVP --> ICS
    end
    
    subgraph "5. Final Ranking"
        RP["Ranked Paths<br/>with scores"]
        EVP --> RP
    end
    
    style CP fill:#f9f9f9
    style RP fill:#f9f9f9
```

Sources: [minirag/utils.py:341-437](), [minirag/kg/networkx_impl.py:177-193]()

## Common Usage Patterns

### Pattern 1: Building k-Hop Paths

This pattern is used in NetworkXStorage to explore the graph neighborhood:

```python
# From networkx_impl.py:177-193
async def get_neighbors_within_k_hops(self, source_node_id: str, k):
    # 1. Get initial edges
    if await self.has_node(source_node_id):
        source_edge = list(self._graph.edges(source_node_id))
    else:
        return []
    
    # 2. Iteratively expand to k hops
    count = 0
    while count < k:
        count += 1
        sc_edge = copy.deepcopy(source_edge)
        source_edge = []
        for pair in sc_edge:
            append_edge = list(self._graph.edges(pair[-1]))
            # merge_tuples connects paths
            for tuples in merge_tuples([pair], append_edge):
                source_edge.append(tuples)
    
    return source_edge
```

Sources: [minirag/kg/networkx_impl.py:177-193]()

### Pattern 2: Scoring and Ranking Paths

This pattern combines entity overlap scoring with edge validation:

```python
# Step 1: Score by entity overlap
scored_paths = cal_path_score_list(
    candidate_reasoning_path=candidate_paths,
    maybe_answer_list=extracted_entities
)
# Result: {id: {"Score": score, "Path": {path_tuple: [overlap_count]}}}

# Step 2: Add edge voting
final_paths, edge_mapping = edge_vote_path(
    path_dict=scored_paths,
    edge_list=retrieved_edges
)
# Result: Path scores now have [overlap_count, edge_vote_count]
```

Sources: [minirag/utils.py:404-413](), [minirag/utils.py:416-437]()

### Pattern 3: Path Validation

This pattern ensures path quality during construction:

```python
# Check if merging would create a cycle
for match in matching_tuples:
    matchh = (match[1], match[0])  # Reverse edge
    if is_continuous_subsequence(match, tup) or \
       is_continuous_subsequence(matchh, tup):
        continue  # Skip, would create cycle
    
    # Safe to merge
    merged_tuple = tup + match[1:]
    result.append(merged_tuple)
```

Sources: [minirag/utils.py:374-376]()

## Summary Table

| Function | Purpose | Input | Output | Line Reference |
|----------|---------|-------|--------|----------------|
| `is_continuous_subsequence()` | Check if edge exists in path | (subseq, seq) | bool | [341-359]() |
| `merge_tuples()` | Extend paths by joining edges | (list1, list2) | list of tuples | [362-386]() |
| `count_elements_in_tuple()` | Count entity overlap | (tuple, list) | int | [389-401]() |
| `cal_path_score_list()` | Score paths by entity overlap | (path_dict, entities) | scored dict | [404-413]() |
| `edge_vote_path()` | Validate paths with edge voting | (path_dict, edges) | (dict, mapping) | [416-437]() |

Sources: [minirag/utils.py:341-437]()

---

# Page: Extending MiniRAG

# Extending MiniRAG

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [minirag/__init__.py](minirag/__init__.py)
- [minirag/base.py](minirag/base.py)
- [minirag/kg/weaviate_impl.py](minirag/kg/weaviate_impl.py)
- [minirag/minirag.py](minirag/minirag.py)
- [tests/test_weaviate.py](tests/test_weaviate.py)

</details>



This document describes how to extend and customize MiniRAG to add new capabilities or integrate with different systems. MiniRAG's architecture is designed to be modular and extensible, allowing developers to add custom storage backends, embedding models, language models, and other components.

For information about the overall architecture, see [System Architecture](#2).

## Extension Points Overview

MiniRAG provides several extension points that allow developers to customize its behavior:

1. **Storage Backends** - Add support for new databases or storage systems
2. **Embedding Models** - Integrate custom text embedding models
3. **Language Models** - Use different LLMs for response generation
4. **Chunking Functions** - Customize document splitting logic
5. **Add-on Parameters** - Extend functionality through additional parameters

```mermaid
flowchart TD
    subgraph "MiniRAG Extension Points"
        direction LR
        MiniRAG["MiniRAG Core"]
        
        subgraph "Storage Extensions"
            direction TB
            KVStorageExt["Key-Value Storage\nImplementations"]
            VectorStorageExt["Vector Storage\nImplementations"]
            GraphStorageExt["Graph Storage\nImplementations"]
            DocStatusExt["Document Status\nImplementations"]
        end
        
        subgraph "Model Extensions"
            direction TB
            EmbeddingExt["Custom Embedding\nModels"]
            LLMExt["Custom Language\nModels"]
        end
        
        subgraph "Processing Extensions"
            direction TB
            ChunkingExt["Custom Chunking\nFunctions"]
            ResponseParsingExt["Custom Response\nParsing"]
        end
        
        MiniRAG --- StorageBaseClasses["Base Storage Classes"]
        StorageBaseClasses --- KVStorageExt
        StorageBaseClasses --- VectorStorageExt
        StorageBaseClasses --- GraphStorageExt
        StorageBaseClasses --- DocStatusExt
        
        MiniRAG --- EmbeddingExt
        MiniRAG --- LLMExt
        MiniRAG --- ChunkingExt
        MiniRAG --- ResponseParsingExt
    end
```

Sources: [minirag/minirag.py:169-176](), [minirag/minirag.py:39-62]()

## Adding Custom Storage Backends

MiniRAG uses a storage abstraction layer defined by base classes in `base.py`. To add a new storage backend, you need to implement one or more of these base classes.

### Storage Class Hierarchy

```mermaid
classDiagram
    class StorageNameSpace {
        +namespace: str
        +global_config: dict
        +index_done_callback()
        +query_done_callback()
    }
    
    class BaseVectorStorage {
        +embedding_func
        +query(query, top_k)
        +upsert(data)
    }
    
    class BaseKVStorage {
        +get_by_id(id)
        +get_by_ids(ids)
        +filter_keys(data)
        +upsert(data)
    }
    
    class BaseGraphStorage {
        +get_node(node_id)
        +get_edge(source_id, target_id)
        +upsert_node(node_id, data)
        +upsert_edge(source_id, target_id, data)
    }
    
    class DocStatusStorage {
        +get_status_counts()
        +get_failed_docs()
        +get_pending_docs()
    }
    
    StorageNameSpace <|-- BaseVectorStorage
    StorageNameSpace <|-- BaseKVStorage
    StorageNameSpace <|-- BaseGraphStorage
    BaseKVStorage <|-- DocStatusStorage
```

Sources: [minirag/base.py:48-196]()

### Implementation Steps

To add a new storage backend:

1. Create a new file in the `minirag/kg/` directory (e.g., `minirag/kg/my_storage_impl.py`)
2. Implement the relevant storage class(es) by inheriting from the base classes
3. Register your storage class in the `STORAGES` dictionary in `minirag/minirag.py`

### Example: Adding a New Vector Storage Backend

Here's how you would implement a new vector storage backend:

1. Create a file `minirag/kg/my_vector_db_impl.py` 
2. Implement the `MyVectorDBStorage` class that inherits from `BaseVectorStorage`
3. Implement the required methods: `query()` and `upsert()`
4. Add your class to the `STORAGES` dictionary in `minirag/minirag.py`

```python
# Required methods to implement for BaseVectorStorage
async def query(self, query: str, top_k: int) -> list[dict]:
    # Implement vector similarity search
    pass

async def upsert(self, data: dict[str, dict]):
    # Implement vector storage insertion/update
    pass
```

### Registering a New Storage Backend

Add your storage class to the `STORAGES` dictionary in `minirag/minirag.py`:

```python
STORAGES = {
    # Existing storages...
    "MyVectorDBStorage": ".kg.my_vector_db_impl",
}
```

Then you can use it when initializing MiniRAG:

```python
rag = MiniRAG(
    vector_storage="MyVectorDBStorage",
    # Other parameters...
)
```

Sources: [minirag/minirag.py:39-62](), [minirag/minirag.py:311-314]()

## Customizing Embedding Models

MiniRAG uses embedding models to convert text to vector representations. You can provide your own embedding function when initializing MiniRAG.

### Embedding Function Interface

Your embedding function should:
- Accept a string or list of strings
- Return a list of vectors (numpy arrays)
- Be compatible with async operations

```mermaid
flowchart TD
    subgraph "Embedding Model Integration"
        User["User Code"] -- "Create custom\nembedding function" --> EmbeddingFunc["embedding_func(text: str | list[str]) -> list[np.ndarray]"]
        EmbeddingFunc -- "Provide to MiniRAG\nconstructor" --> MiniRAG["MiniRAG Instance"]
        MiniRAG -- "Uses for document\nand query embedding" --> VectorStorages["Vector Storages:\n- chunks_vdb\n- entities_vdb\n- entity_name_vdb\n- relationships_vdb"]
    end
```

Sources: [minirag/minirag.py:155-157](), [minirag/base.py:7-7]()

### Example Implementation

```python
import numpy as np
from sentence_transformers import SentenceTransformer

# Create an embedding function using SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

async def my_embedding_func(text):
    if isinstance(text, str):
        text = [text]
    # Get embeddings from the model
    embeddings = model.encode(text)
    return embeddings

# Initialize MiniRAG with custom embedding function
rag = MiniRAG(
    embedding_func=my_embedding_func,
    # Other parameters...
)
```

MiniRAG will apply a wrapper to your embedding function using `limit_async_func_call` to manage concurrency:

```python
self.embedding_func = limit_async_func_call(self.embedding_func_max_async)(
    self.embedding_func
)
```

Sources: [minirag/minirag.py:243-245]()

## Integrating Custom Language Models

MiniRAG uses language models for generating responses to queries. You can integrate your own LLM by providing a custom model function.

### LLM Function Interface

Your LLM function should:
- Accept a prompt string and optional parameters
- Return a string response or streamed response
- Be compatible with async operations

```mermaid
flowchart TD
    subgraph "Language Model Integration"
        User["User Code"] -- "Create custom\nLLM function" --> LLMFunc["llm_model_func(prompt: str, **kwargs) -> str"]
        LLMFunc -- "Provide to MiniRAG\nconstructor" --> MiniRAG["MiniRAG Instance"]
        MiniRAG -- "Wraps with\nlimit_async_func_call" --> WrappedLLM["Wrapped LLM Function"]
        WrappedLLM -- "Used for generating\nresponses to queries" --> QueryPipeline["Query Pipeline"]
    end
```

Sources: [minirag/minirag.py:160-166](), [minirag/minirag.py:296-302]()

### Example Implementation

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load model and tokenizer
model_name = "meta-llama/Llama-3.2-1B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

async def my_llm_func(prompt, hashing_kv=None, **kwargs):
    # If caching is enabled and we have a cached response, return it
    if hashing_kv:
        cache_key = hash(prompt)
        cached_response = await hashing_kv.get_by_id(cache_key)
        if cached_response:
            return cached_response
    
    # Generate response with the model
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=kwargs.get("max_length", 512))
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Cache the response if caching is enabled
    if hashing_kv:
        await hashing_kv.upsert({cache_key: response})
    
    return response

# Initialize MiniRAG with custom LLM function
rag = MiniRAG(
    llm_model_func=my_llm_func,
    llm_model_name="my-custom-llm",
    llm_model_max_token_size=4096,
    llm_model_max_async=8,
    llm_model_kwargs={"temperature": 0.7},
    # Other parameters...
)
```

The LLM function is wrapped with `limit_async_func_call` to manage concurrency, similar to the embedding function:

```python
self.llm_model_func = limit_async_func_call(self.llm_model_max_async)(
    partial(
        self.llm_model_func,
        hashing_kv=self.llm_response_cache,
        **self.llm_model_kwargs,
    )
)
```

Sources: [minirag/minirag.py:296-302]()

## Custom Chunking Functions

MiniRAG uses chunking functions to split input documents into manageable pieces. You can provide your own chunking function to customize how documents are split.

### Chunking Function Interface

Your chunking function should:
- Accept a document string and chunking parameters
- Return a list of chunk dictionaries with content and metadata
- Each chunk should have at least a "content" field

```mermaid
flowchart TD
    subgraph "Chunking Function Extension"
        User["User Code"] -- "Create custom\nchunking function" --> ChunkingFunc["chunking_func(text, overlap, size, model, **kwargs)"]
        ChunkingFunc -- "Provide to MiniRAG\nconstructor" --> MiniRAG["MiniRAG Instance"]
        MiniRAG -- "Uses during\ndocument insertion" --> DocumentProcessing["Document Processing Pipeline"]
        DocumentProcessing -- "Creates chunks\nand processes them" --> StorageLayer["Storage Layer"]
    end
```

Sources: [minirag/minirag.py:181-182](), [minirag/minirag.py:356-371](), [minirag/minirag.py:480-490]()

### Example Implementation

```python
def my_custom_chunking(
    text, chunk_overlap_token_size, chunk_token_size, tiktoken_model_name, **kwargs
):
    # Custom logic to split text into chunks
    # For example, split by paragraphs instead of token count
    paragraphs = text.split("\n\n")
    chunks = []
    
    for i, para in enumerate(paragraphs):
        if para.strip():  # Skip empty paragraphs
            chunk = {
                "content": para,
                "chunk_order_index": i,
                "tokens": len(para.split())  # Approximate token count
            }
            chunks.append(chunk)
    
    return chunks

# Initialize MiniRAG with custom chunking function
rag = MiniRAG(
    chunking_func=my_custom_chunking,
    chunking_func_kwargs={"min_paragraph_length": 50},
    # Other parameters...
)
```

The custom chunking function is used during document insertion:

```python
chunks = {
    compute_mdhash_id(dp["content"], prefix="chunk-"): {
        **dp,
        "full_doc_id": doc_id,
    }
    for dp in self.chunking_func(
        status_doc.content,
        self.chunk_overlap_token_size,
        self.chunk_token_size,
        self.tiktoken_model_name,
    )
}
```

Sources: [minirag/minirag.py:480-490]()

## Add-on Parameters

MiniRAG allows you to pass additional parameters for custom extensions using the `addon_params` field.

### Using Add-on Parameters

```python
# Initialize MiniRAG with add-on parameters
rag = MiniRAG(
    addon_params={
        "custom_extension": {
            "parameter1": "value1",
            "parameter2": "value2",
        },
        "another_extension": {
            "setting": True,
        }
    },
    # Other parameters...
)
```

These parameters are accessible through the `global_config` dictionary passed to storage classes and other components:

```python
class MyCustomStorage(BaseVectorStorage):
    def __init__(self, namespace, global_config, embedding_func, **kwargs):
        super().__init__(namespace, global_config, embedding_func, **kwargs)
        # Access custom parameters
        extension_params = global_config.get("addon_params", {}).get("custom_extension", {})
        self.parameter1 = extension_params.get("parameter1")
```

Sources: [minirag/minirag.py:174-174](), [minirag/minirag.py:198-199]()

## Custom Response Parsing

MiniRAG allows you to customize how LLM responses are parsed by providing a custom response parsing function.

```mermaid
flowchart TD
    subgraph "Response Parsing Extension"
        User["User Code"] -- "Create custom\nresponse parsing function" --> ParseFunc["convert_response_to_json_func(response: str) -> dict"]
        ParseFunc -- "Provide to MiniRAG\nconstructor" --> MiniRAG["MiniRAG Instance"]
        MiniRAG -- "Uses during\nquery processing" --> QueryPipeline["Query Pipeline"]
        QueryPipeline -- "Parses LLM\nresponses" --> FormattedResponse["Formatted Response"]
    end
```

Sources: [minirag/minirag.py:175-175](), [minirag/minirag.py:22-22]()

### Example Implementation

```python
def my_custom_response_parser(response: str) -> dict:
    # Custom logic to parse the LLM response
    # For example, extract structured data in a specific format
    
    # Simple example: extract key-value pairs
    result = {}
    for line in response.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            result[key.strip()] = value.strip()
    
    return result

# Initialize MiniRAG with custom response parser
rag = MiniRAG(
    convert_response_to_json_func=my_custom_response_parser,
    # Other parameters...
)
```

## Putting It All Together

The following diagram shows how all the extension points integrate into the MiniRAG architecture:

```mermaid
flowchart TD
    subgraph "Extended MiniRAG Architecture"
        MiniRAG["MiniRAG Class\nminirag.py"]
        
        subgraph "Storage Layer"
            BaseStorage["StorageNameSpace\nbase.py"]
            BaseKV["BaseKVStorage\nbase.py"]
            BaseVector["BaseVectorStorage\nbase.py"]
            BaseGraph["BaseGraphStorage\nbase.py"]
            DocStatus["DocStatusStorage\nbase.py"]
            
            CustomKV["Custom KV Storage\nImplementation"]
            CustomVector["Custom Vector Storage\nImplementation"]
            CustomGraph["Custom Graph Storage\nImplementation"]
            
            BaseStorage --> BaseKV
            BaseStorage --> BaseVector
            BaseStorage --> BaseGraph
            BaseKV --> DocStatus
            
            BaseKV -.-> CustomKV
            BaseVector -.-> CustomVector
            BaseGraph -.-> CustomGraph
        end
        
        subgraph "Model Extensions"
            EmbeddingFunc["Custom Embedding Function"]
            LLMFunc["Custom LLM Function"]
        end
        
        subgraph "Processing Extensions"
            ChunkingFunc["Custom Chunking Function"]
            ResponseParser["Custom Response Parser"]
        end
        
        MiniRAG --> BaseStorage
        MiniRAG --> EmbeddingFunc
        MiniRAG --> LLMFunc
        MiniRAG --> ChunkingFunc
        MiniRAG --> ResponseParser
        
        STORAGES["STORAGES Dictionary\nminirag.py:39-62"] --> MiniRAG
        StorageRegistry["_get_storage_class\nminirag.py:311-314"] --> STORAGES
    end
```

Sources: [minirag/minirag.py:39-62](), [minirag/minirag.py:311-314](), [minirag/base.py:48-196]()

## Example: Complete Custom Configuration

Here's an example that combines multiple extension points:

```python
from minirag import MiniRAG

# Custom embedding function
async def my_embedding_func(text):
    # Implementation details...
    return embeddings

# Custom LLM function
async def my_llm_func(prompt, **kwargs):
    # Implementation details...
    return response

# Custom chunking function
def my_chunking_func(text, overlap, size, model, **kwargs):
    # Implementation details...
    return chunks

# Custom response parser
def my_response_parser(response):
    # Implementation details...
    return parsed_response

# Initialize MiniRAG with all custom components
rag = MiniRAG(
    # Storage backends
    kv_storage="MyCustomKVStorage",
    vector_storage="MyCustomVectorStorage",
    graph_storage="MyCustomGraphStorage",
    doc_status_storage="MyCustomDocStatusStorage",
    
    # Custom functions
    embedding_func=my_embedding_func,
    llm_model_func=my_llm_func,
    chunking_func=my_chunking_func,
    convert_response_to_json_func=my_response_parser,
    
    # Function parameters
    embedding_func_max_async=32,
    llm_model_max_async=16,
    chunking_func_kwargs={"custom_param": True},
    
    # Add-on parameters
    addon_params={
        "my_extension": {
            "feature_flag": True,
            "custom_threshold": 0.75,
        }
    },
    
    # Other configuration...
    working_dir="./my_custom_minirag"
)
```

Sources: [minirag/minirag.py:119-184]()

---

# Page: Adding Storage Backends

# Adding Storage Backends

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [minirag/__init__.py](minirag/__init__.py)
- [minirag/base.py](minirag/base.py)
- [minirag/kg/networkx_impl.py](minirag/kg/networkx_impl.py)

</details>



This document outlines how to implement custom storage backends for MiniRAG. The MiniRAG system is designed with a flexible storage layer that allows for different storage implementations to be added. This guide explains the storage architecture, steps to create new storage backends, and best practices for implementation.

For information about using existing storage backends, see [Storage Implementations](#5).

## 1. Storage Architecture Overview

MiniRAG's storage layer is built on a set of abstract base classes that define the interfaces for different types of storage. All storage components inherit from a common `StorageNameSpace` class, which provides basic namespace functionality and lifecycle hooks.

```mermaid
classDiagram
    class StorageNameSpace {
        +namespace: str
        +global_config: dict
        +index_done_callback()
        +query_done_callback()
    }
    
    class BaseVectorStorage {
        +embedding_func
        +query(query, top_k)
        +upsert(data)
    }
    
    class BaseKVStorage {
        +get_by_id(id)
        +get_by_ids(ids)
        +filter_keys(data)
        +upsert(data)
    }
    
    class BaseGraphStorage {
        +get_node(node_id)
        +get_edge(source_id, target_id)
        +upsert_node(node_id, data)
        +upsert_edge(source_id, target_id, data)
    }
    
    class DocStatusStorage {
        +get_status_counts()
        +get_failed_docs()
        +get_pending_docs()
    }
    
    BaseVectorStorage --|> StorageNameSpace
    BaseKVStorage --|> StorageNameSpace
    BaseGraphStorage --|> StorageNameSpace
    DocStatusStorage --|> BaseKVStorage
```

Sources: [minirag/base.py:48-197]()

### 1.1 Storage Types

MiniRAG uses four main types of storage:

1. **Vector Storage**: Stores embeddings for efficient similarity search
2. **Key-Value Storage**: Stores general data with key-based access
3. **Graph Storage**: Stores entity relationships in a graph structure
4. **Document Status Storage**: Tracks the processing status of documents

## 2. Implementing a New Storage Backend

### 2.1 Choose the Appropriate Base Class

To add a new storage backend, first determine which base class to extend based on the type of storage:

```mermaid
flowchart TD
    Start["Choose Storage Type"]
    VectorStorage["Extend BaseVectorStorage"]
    KVStorage["Extend BaseKVStorage"]
    GraphStorage["Extend BaseGraphStorage"]
    DocStatusStorage["Extend DocStatusStorage"]
    
    Start --> Decision{"What type of storage?"}
    Decision -->|"For similarity search"| VectorStorage
    Decision -->|"For key-value data"| KVStorage
    Decision -->|"For entity relationships"| GraphStorage
    Decision -->|"For document status"| DocStatusStorage
    
    VectorStorage --> Implement["Implement Required Methods"]
    KVStorage --> Implement
    GraphStorage --> Implement
    DocStatusStorage --> Implement
```

Sources: [minirag/base.py:62-197]()

### 2.2 Implementing Required Methods

Each base class requires you to implement specific methods. The following sections detail the required methods for each storage type.

#### 2.2.1 Vector Storage

To implement a custom vector storage backend, extend `BaseVectorStorage` and implement these methods:

```python
# Required methods for BaseVectorStorage
async def query(self, query: str, top_k: int) -> list[dict]:
    # Perform similarity search and return top_k items
    
async def upsert(self, data: dict[str, dict]):
    # Add or update vectors in the storage
```

Sources: [minirag/base.py:62-75]()

#### 2.2.2 Key-Value Storage

To implement a custom key-value storage backend, extend `BaseKVStorage` and implement these methods:

```python
# Required methods for BaseKVStorage
async def all_keys(self) -> list[str]:
    # Return all keys in the storage
    
async def get_by_id(self, id: str) -> Union[T, None]:
    # Retrieve item by id
    
async def get_by_ids(self, ids: list[str], fields: Union[set[str], None] = None) -> list[Union[T, None]]:
    # Retrieve multiple items by ids
    
async def filter_keys(self, data: list[str]) -> set[str]:
    # Return keys that don't exist in storage
    
async def upsert(self, data: dict[str, T]):
    # Add or update items in storage
    
async def drop(self):
    # Clear all data from storage
```

Sources: [minirag/base.py:77-100]()

#### 2.2.3 Graph Storage

To implement a custom graph storage backend, extend `BaseGraphStorage` and implement these methods:

```python
# Required methods for BaseGraphStorage
async def get_types(self) -> tuple[list[str], list[str]]:
    # Return node types in the graph
    
async def has_node(self, node_id: str) -> bool:
    # Check if node exists
    
async def has_edge(self, source_node_id: str, target_node_id: str) -> bool:
    # Check if edge exists
    
async def node_degree(self, node_id: str) -> int:
    # Get number of edges for node
    
async def edge_degree(self, src_id: str, tgt_id: str) -> int:
    # Get combined degree of source and target nodes
    
async def get_node(self, node_id: str) -> Union[dict, None]:
    # Retrieve node data
    
async def get_edge(self, source_node_id: str, target_node_id: str) -> Union[dict, None]:
    # Retrieve edge data
    
async def get_node_edges(self, source_node_id: str) -> Union[list[tuple[str, str]], None]:
    # Get all edges for a node
    
async def upsert_node(self, node_id: str, node_data: dict[str, str]):
    # Add or update node
    
async def upsert_edge(self, source_node_id: str, target_node_id: str, edge_data: dict[str, str]):
    # Add or update edge
    
async def delete_node(self, node_id: str):
    # Remove node from graph
```

Sources: [minirag/base.py:103-148]()

#### 2.2.4 Document Status Storage

To implement a custom document status storage backend, extend `DocStatusStorage` and implement these methods in addition to the `BaseKVStorage` methods:

```python
# Required methods for DocStatusStorage (in addition to BaseKVStorage methods)
async def get_status_counts(self) -> dict[str, int]:
    # Return counts of documents in each status
    
async def get_failed_docs(self) -> dict[str, DocProcessingStatus]:
    # Return all failed documents
    
async def get_pending_docs(self) -> dict[str, DocProcessingStatus]:
    # Return all pending documents
```

Sources: [minirag/base.py:184-197]()

### 2.3 Implementing Storage Lifecycle Methods

Each storage class inherits the following methods from `StorageNameSpace`:

```python
# Storage lifecycle methods
async def index_done_callback(self):
    """Called after indexing is complete"""
    pass

async def query_done_callback(self):
    """Called after a query is complete"""
    pass
```

These methods can be overridden to perform actions like committing transactions or persisting data after operations.

Sources: [minirag/base.py:53-59]()

## 3. Example Implementation: NetworkX Graph Storage

Let's examine how `NetworkXStorage` implements `BaseGraphStorage` as a reference:

```mermaid
classDiagram
    class BaseGraphStorage {
        +get_node(node_id)
        +get_edge(source_id, target_id)
        +upsert_node(node_id, data)
        +upsert_edge(source_id, target_id, data)
    }
    
    class NetworkXStorage {
        -_graph: nx.Graph
        -_graphml_xml_file: str
        +__post_init__()
        +index_done_callback()
        +has_node(node_id)
        +has_edge(source_node_id, target_node_id)
        +get_node(node_id)
        +get_edge(source_node_id, target_node_id)
        +upsert_node(node_id, node_data)
        +upsert_edge(source_node_id, target_node_id, edge_data)
    }
    
    BaseGraphStorage <|-- NetworkXStorage
```

Sources: [minirag/kg/networkx_impl.py:69-276]()

Key implementation details:

1. **Initialization**: The `__post_init__` method initializes the NetworkX graph and loads existing data if available.

```python
def __post_init__(self):
    self._graphml_xml_file = os.path.join(
        self.global_config["working_dir"], f"graph_{self.namespace}.graphml"
    )
    preloaded_graph = NetworkXStorage.load_nx_graph(self._graphml_xml_file)
    if preloaded_graph is not None:
        logger.info(f"Loaded graph from {self._graphml_xml_file}...")
    self._graph = preloaded_graph or nx.Graph()
    # ...
```

Sources: [minirag/kg/networkx_impl.py:132-144]()

2. **Lifecycle Methods**: The `index_done_callback` method persists the graph after indexing.

```python
async def index_done_callback(self):
    NetworkXStorage.write_nx_graph(self._graph, self._graphml_xml_file)
```

Sources: [minirag/kg/networkx_impl.py:146-147]()

3. **Node Operations**: Methods to add, query, and manage nodes.

```python
async def has_node(self, node_id: str) -> bool:
    return self._graph.has_node(node_id)

async def get_node(self, node_id: str) -> Union[dict, None]:
    return self._graph.nodes.get(node_id)

async def upsert_node(self, node_id: str, node_data: dict[str, str]):
    self._graph.add_node(node_id, **node_data)
```

Sources: [minirag/kg/networkx_impl.py:196-222]()

4. **Edge Operations**: Methods to add, query, and manage edges.

```python
async def has_edge(self, source_node_id: str, target_node_id: str) -> bool:
    return self._graph.has_edge(source_node_id, target_node_id)

async def get_edge(self, source_node_id: str, target_node_id: str) -> Union[dict, None]:
    return self._graph.edges.get((source_node_id, target_node_id))

async def upsert_edge(self, source_node_id: str, target_node_id: str, edge_data: dict[str, str]):
    self._graph.add_edge(source_node_id, target_node_id, **edge_data)
```

Sources: [minirag/kg/networkx_impl.py:199-227]()

## 4. Example Implementation: Neo4j Graph Storage

For comparison, let's look at the Neo4j implementation which provides a different backend for graph storage:

```mermaid
classDiagram
    class BaseGraphStorage {
        +get_node(node_id)
        +get_edge(source_id, target_id)
        +upsert_node(node_id, data)
        +upsert_edge(source_id, target_id, data)
    }
    
    class Neo4JStorage {
        -_driver: AsyncDriver
        -_DATABASE: str
        +__init__(namespace, global_config, embedding_func)
        +has_node(node_id)
        +has_edge(source_node_id, target_node_id)
        +get_node(node_id)
        +get_edge(source_node_id, target_node_id)
        +upsert_node(node_id, node_data)
        +upsert_edge(source_node_id, target_node_id, edge_data)
    }
    
    BaseGraphStorage <|-- Neo4JStorage
```

Sources: [minirag/kg/neo4j_impl.py:30-557]()

Key implementation differences:

1. **Connection Management**: The Neo4j implementation manages a database connection.

```python
def __init__(self, namespace, global_config, embedding_func):
    super().__init__(
        namespace=namespace,
        global_config=global_config,
        embedding_func=embedding_func,
    )
    self._driver = None
    self._driver_lock = asyncio.Lock()
    URI = os.environ["NEO4J_URI"]
    USERNAME = os.environ["NEO4J_USERNAME"]
    PASSWORD = os.environ["NEO4J_PASSWORD"]
    # ...
```

Sources: [minirag/kg/neo4j_impl.py:36-54]()

2. **Database Operations**: Uses Cypher queries to perform graph operations.

```python
async def get_node(self, node_id: str) -> Union[dict, None]:
    async with self._driver.session(database=self._DATABASE) as session:
        entity_name_label = node_id.strip('"')
        query = f"MATCH (n:`{entity_name_label}`) RETURN n"
        result = await session.run(query)
        record = await result.single()
        if record:
            node = record["n"]
            node_dict = dict(node)
            # ...
            return node_dict
        return None
```

Sources: [minirag/kg/neo4j_impl.py:141-154]()

3. **Error Handling**: Includes retry mechanisms for database operations.

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(
        (
            neo4jExceptions.ServiceUnavailable,
            neo4jExceptions.TransientError,
            neo4jExceptions.WriteServiceUnavailable,
            neo4jExceptions.ClientError,
        )
    ),
)
async def upsert_node(self, node_id: str, node_data: Dict[str, Any]):
    # Implementation...
```

Sources: [minirag/kg/neo4j_impl.py:294-332]()

## 5. Implementation Guidelines

When implementing a new storage backend, follow these guidelines:

### 5.1 Implementation Checklist

1. **Select the appropriate base class** based on storage type
2. **Implement all required methods** defined in the base class
3. **Handle errors appropriately** for robustness
4. **Implement lifecycle methods** for proper resource management
5. **Add appropriate configuration options** for your backend

### 5.2 Best Practices

1. **Efficient Query Implementation**: Implement query methods efficiently, considering:
   - Caching strategies
   - Batch operations
   - Connection pooling (for database backends)

2. **Error Handling**: Use try/except blocks and retries for robustness:
   
   ```python
   try:
       # Perform storage operation
   except Exception as e:
       logger.error(f"Error during operation: {str(e)}")
       # Implement appropriate error handling
   ```

3. **Resource Management**: Properly manage resources in lifecycle methods:
   
   ```python
   async def index_done_callback(self):
       # Save/commit changes after indexing
       
   async def query_done_callback(self):
       # Save/commit changes after querying
   ```

4. **Configuration Options**: Make your implementation configurable:
   
   ```python
   def __post_init__(self):
       # Access configuration from global_config
       self.connection_timeout = self.global_config.get("connection_timeout", 30)
   ```

## 6. Integration with MiniRAG

After implementing your storage backend, you need to integrate it with MiniRAG for use.

```mermaid
flowchart LR
    subgraph "Storage Implementation"
        ImplementBackend["1. Implement Backend Class"]
        TestBackend["2. Test Storage Operations"]
    end
    
    subgraph "Integration"
        ConfigureBackend["3. Configure Backend"]
        UseBackend["4. Use in MiniRAG"]
    end
    
    ImplementBackend --> TestBackend
    TestBackend --> ConfigureBackend
    ConfigureBackend --> UseBackend
```

### 6.1 Configuration Example

When configuring MiniRAG to use your custom storage backend, you'll need to provide the appropriate configuration:

```python
# Example configuration with custom graph storage
config = {
    "working_dir": "./data",
    "graph_storage": {
        "type": "MyCustomGraphStorage",
        "config": {
            # Custom configuration options for your storage backend
        }
    },
    # Other configuration options...
}

# Initialize MiniRAG with this configuration
rag = MiniRAG(config)
```

## 7. Testing Your Storage Backend

When developing a new storage backend, thoroughly test it to ensure it meets all requirements:

1. **Unit Tests**: Test each method individually
2. **Integration Tests**: Test interactions with MiniRAG
3. **Performance Tests**: Benchmark against other storage backends
4. **Error Handling Tests**: Verify robustness under failure conditions

## Conclusion

Adding custom storage backends to MiniRAG allows you to adapt the system to your specific requirements and infrastructure. By following the guidelines in this document and understanding the existing implementations, you can create efficient and reliable storage solutions that integrate seamlessly with MiniRAG.

For more information about using specific storage implementations, see [Vector Storage](#5.1), [Key-Value Storage](#5.2), [Graph Storage](#5.3), and [Document Status Storage](#5.4).

---

# Page: Custom LLM Integration

# Custom LLM Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [main.py](main.py)
- [minirag/llm/openai.py](minirag/llm/openai.py)
- [minirag/prompt.py](minirag/prompt.py)

</details>



This page explains how to integrate custom Language Models (LLMs) with MiniRAG, allowing you to use different LLM providers beyond the built-in OpenAI and HuggingFace implementations. MiniRAG supports streaming responses, automatic retry logic, and multiple API providers out of the box. For information about using custom embedding models, see page 10.3.

## Overview

MiniRAG provides a flexible LLM integration architecture through the `llm_model_func` parameter. The system uses LLMs for:

1. **Entity Extraction**: Identifying entities and relationships from text chunks during indexing
2. **Query Processing**: Extracting entities from user queries
3. **Response Generation**: Synthesizing final answers from retrieved context

### LLM Integration Architecture

```mermaid
graph TB
    subgraph "MiniRAG Core"
        MiniRAG["MiniRAG Class<br/>working_dir, llm_model_func"]
        Insert["insert() Method"]
        Query["query() Method"]
    end
    
    subgraph "LLM Function Interface"
        LLMFunc["llm_model_func<br/>async callable"]
        Cache["llm_response_cache<br/>BaseKVStorage"]
        Wrapper["limit_async_func_call<br/>Concurrency Control"]
    end
    
    subgraph "Built-in Providers"
        OpenAIComplete["openai_complete"]
        GPT4o["gpt_4o_mini_complete"]
        NvidiaComplete["nvidia_openai_complete"]
        OpenRouterComplete["openrouter_openai_complete"]
        HFComplete["hf_model_complete"]
    end
    
    subgraph "Custom Provider"
        CustomFunc["Your Custom Function<br/>async def custom_llm(...)"]
    end
    
    MiniRAG --> LLMFunc
    LLMFunc --> Wrapper
    Wrapper --> Cache
    
    Insert --> LLMFunc
    Query --> LLMFunc
    
    LLMFunc -.implements.-> OpenAIComplete
    LLMFunc -.implements.-> GPT4o
    LLMFunc -.implements.-> NvidiaComplete
    LLMFunc -.implements.-> OpenRouterComplete
    LLMFunc -.implements.-> HFComplete
    LLMFunc -.implements.-> CustomFunc
    
    style CustomFunc fill:#f9f9f9
    style LLMFunc fill:#e1f5ff
```

Sources: [minirag/llm/openai.py:93-241](), [main.py:58-72]()

## Function Signature Requirements

All LLM functions integrated with MiniRAG must conform to a specific asynchronous signature:

### Required Signature

```python
from typing import Union, List
from collections.abc import AsyncIterator

async def custom_llm_function(
    prompt: str, 
    system_prompt: str = None, 
    history_messages: List[dict] = [], 
    **kwargs
) -> Union[str, AsyncIterator[str]]:
    """
    Custom LLM function for MiniRAG integration.
    
    Args:
        prompt: The user's input text
        system_prompt: Optional system-level instruction
        history_messages: List of prior conversation messages
        **kwargs: Additional parameters (hashing_kv, keyword_extraction, etc.)
    
    Returns:
        Either a complete string response or an async iterator for streaming
    """
    # Your implementation here
    pass
```

### Function Behavior

| Aspect | Requirement |
|--------|-------------|
| **Execution** | Must be asynchronous (async def) |
| **Return Type** | `str` for complete responses, `AsyncIterator[str]` for streaming |
| **Error Handling** | Should handle API failures gracefully |
| **Parameters** | Must accept `prompt`, `system_prompt`, `history_messages`, and `**kwargs` |
| **Cache Support** | Will automatically receive `hashing_kv` in kwargs for caching |

Sources: [minirag/llm/openai.py:93-153](), [minirag/llm/openai.py:156-169]()

## Built-in LLM Providers

MiniRAG includes several pre-implemented LLM functions with retry logic and streaming support.

### OpenAI-Compatible Providers

#### Core Implementation: openai_complete_if_cache

The foundation for all OpenAI-compatible integrations is `openai_complete_if_cache`, which includes:

```mermaid
graph TB
    subgraph "openai_complete_if_cache Function"
        Input["prompt, system_prompt<br/>history_messages, kwargs"]
        Retry["@retry Decorator<br/>3 attempts, exponential backoff"]
        Client["AsyncOpenAI Client<br/>base_url configurable"]
        APICall{"API Call"}
        Streaming{"Streaming?"}
        ChunkIter["Async Iterator<br/>yields content chunks"]
        FullResp["Complete String<br/>response.choices[0].message.content"]
        UnicodeDecode["safe_unicode_decode<br/>Handle \\u sequences"]
    end
    
    Input --> Retry
    Retry --> Client
    Client --> APICall
    APICall --> Streaming
    Streaming -->|Yes| ChunkIter
    Streaming -->|No| FullResp
    ChunkIter --> UnicodeDecode
    FullResp --> UnicodeDecode
```

Sources: [minirag/llm/openai.py:81-153]()

The retry decorator configuration:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `stop` | `stop_after_attempt(3)` | Maximum 3 retry attempts |
| `wait` | `wait_exponential(multiplier=1, min=4, max=10)` | Exponential backoff: 4-10 seconds |
| `retry` | `RateLimitError, APIConnectionError, APITimeoutError` | Retries on these exceptions |

Sources: [minirag/llm/openai.py:81-87]()

### Provider-Specific Functions

#### 1. OpenAI Standard Models

```python
# Generic OpenAI interface
async def openai_complete(
    prompt, 
    system_prompt=None, 
    history_messages=[], 
    keyword_extraction=False, 
    **kwargs
) -> Union[str, AsyncIterator[str]]:
    # Uses model from kwargs["hashing_kv"].global_config["llm_model_name"]
    pass

# GPT-4o
async def gpt_4o_complete(prompt, system_prompt=None, history_messages=[], **kwargs) -> str:
    # Fixed model: "gpt-4o"
    pass

# GPT-4o-mini (recommended for MiniRAG)
async def gpt_4o_mini_complete(prompt, system_prompt=None, history_messages=[], **kwargs) -> str:
    # Fixed model: "gpt-4o-mini"
    pass
```

Sources: [minirag/llm/openai.py:156-199]()

#### 2. NVIDIA API Integration

```python
async def nvidia_openai_complete(
    prompt, 
    system_prompt=None, 
    history_messages=[], 
    keyword_extraction=False, 
    **kwargs
) -> str:
    # Model: "nvidia/llama-3.1-nemotron-70b-instruct"
    # Base URL: "https://integrate.api.nvidia.com/v1"
    # Context length: 128k tokens
    pass
```

Sources: [minirag/llm/openai.py:202-216]()

#### 3. OpenRouter Integration

```python
async def openrouter_openai_complete(
    prompt, 
    system_prompt=None, 
    history_messages=[], 
    keyword_extraction=False, 
    api_key: str = None, 
    **kwargs
) -> str:
    # Default model: "google/gemini-2.0-flash-001"
    # Base URL: "https://openrouter.ai/api/v1"
    # Supports custom api_key parameter
    pass
```

Sources: [minirag/llm/openai.py:218-241]()

### HuggingFace Models

For local or self-hosted models, MiniRAG supports HuggingFace Transformers:

```python
from minirag.llm.hf import hf_model_complete
from transformers import AutoModel, AutoTokenizer

# Example from main.py
rag = MiniRAG(
    working_dir="./LiHua-World",
    llm_model_func=hf_model_complete,
    llm_model_name="microsoft/Phi-3.5-mini-instruct",
    llm_model_max_token_size=200,
    # ... other config
)
```

Supported Small Language Models:
- `microsoft/Phi-3.5-mini-instruct`
- `THUDM/glm-edge-1.5b-chat`
- `openbmb/MiniCPM3-4B`
- `Qwen/Qwen2.5-3B-Instruct`

Sources: [main.py:35-72]()

## Implementing a Custom LLM Provider

### Step 1: Create Your Async Function

```python
import os
from typing import Union
from collections.abc import AsyncIterator

async def my_custom_llm(
    prompt: str,
    system_prompt: str = None,
    history_messages: list = [],
    **kwargs
) -> Union[str, AsyncIterator[str]]:
    """
    Custom LLM implementation example.
    """
    # Extract common kwargs
    hashing_kv = kwargs.get("hashing_kv")
    keyword_extraction = kwargs.get("keyword_extraction", False)
    
    # Build messages
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})
    
    # Your LLM API call here
    # Example: response = await my_api_client.generate(messages)
    
    return "Generated response text"
```

### Step 2: Add Retry Logic (Optional)

Use the `tenacity` library for automatic retries:

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError))
)
async def my_custom_llm_with_retry(prompt, system_prompt=None, history_messages=[], **kwargs):
    # Your implementation with automatic retry on specified exceptions
    pass
```

Sources: [minirag/llm/openai.py:81-87]()

### Step 3: Integrate with MiniRAG

```python
from minirag import MiniRAG, QueryParam
from minirag.utils import EmbeddingFunc

rag = MiniRAG(
    working_dir="./my_working_dir",
    llm_model_func=my_custom_llm,
    llm_model_name="my-custom-model-v1",
    llm_model_max_token_size=4096,
    llm_model_max_async=16,
    llm_model_kwargs={
        "temperature": 0.7,
        "top_p": 0.9,
        # Additional model-specific parameters
    },
    # ... embedding and storage config
)
```

Sources: [main.py:58-72]()

## Streaming Support

MiniRAG supports streaming responses for real-time output generation. Your custom LLM function can return an `AsyncIterator[str]` to enable streaming.

### Streaming Implementation Pattern

```python
from collections.abc import AsyncIterator

async def custom_streaming_llm(
    prompt: str,
    system_prompt: str = None,
    history_messages: list = [],
    **kwargs
) -> AsyncIterator[str]:
    """
    Example streaming LLM implementation.
    """
    # Check if streaming is requested (via kwargs or response format)
    if kwargs.get("stream", False):
        async def generate_stream():
            # Yield chunks as they arrive
            async for chunk in your_streaming_api_call():
                if chunk.content:
                    yield chunk.content
        
        return generate_stream()
    else:
        # Return complete response
        return "Complete response"
```

### Streaming in openai_complete_if_cache

The built-in OpenAI integration automatically handles streaming:

```mermaid
graph TD
    Response["API Response"]
    HasAiter{"hasattr(response,<br/>'__aiter__')"}
    CreateGen["Create async generator"]
    YieldChunks["Yield content chunks<br/>chunk.choices[0].delta.content"]
    SafeDecode["safe_unicode_decode<br/>Handle Unicode"]
    ReturnGen["Return generator"]
    DirectReturn["Return complete string<br/>response.choices[0].message.content"]
    
    Response --> HasAiter
    HasAiter -->|True<br/>Streaming| CreateGen
    HasAiter -->|False<br/>Complete| DirectReturn
    CreateGen --> YieldChunks
    YieldChunks --> SafeDecode
    SafeDecode --> ReturnGen
```

Sources: [minirag/llm/openai.py:131-153]()

## Error Handling and Retry Logic

### Built-in Retry Mechanism

All OpenAI-compatible functions use the `@retry` decorator with exponential backoff:

```mermaid
graph LR
    Attempt1["Attempt 1"]
    Fail1{"Exception?"}
    Wait1["Wait 4s"]
    Attempt2["Attempt 2"]
    Fail2{"Exception?"}
    Wait2["Wait 6-10s"]
    Attempt3["Attempt 3"]
    Fail3{"Exception?"}
    Success["Return Response"]
    FinalFail["Raise Exception"]
    
    Attempt1 --> Fail1
    Fail1 -->|RateLimitError<br/>APIConnectionError<br/>APITimeoutError| Wait1
    Fail1 -->|Success| Success
    Wait1 --> Attempt2
    Attempt2 --> Fail2
    Fail2 -->|Error| Wait2
    Fail2 -->|Success| Success
    Wait2 --> Attempt3
    Attempt3 --> Fail3
    Fail3 -->|Error| FinalFail
    Fail3 -->|Success| Success
```

### Exception Types

| Exception | Source | Retry Behavior |
|-----------|--------|----------------|
| `RateLimitError` | OpenAI API | Retry with exponential backoff |
| `APIConnectionError` | Network issues | Retry with exponential backoff |
| `APITimeoutError` | Request timeout | Retry with exponential backoff |
| Other exceptions | Various | Propagate immediately (no retry) |

Sources: [minirag/llm/openai.py:57-87]()

### Custom Error Handling

For your custom LLM function:

```python
async def robust_custom_llm(prompt, system_prompt=None, history_messages=[], **kwargs):
    try:
        # Your API call
        response = await your_api_client.generate(prompt)
        return response.text
    
    except RateLimitError:
        # Handle rate limiting
        logger.warning("Rate limit hit, consider implementing backoff")
        raise  # Let retry decorator handle it
    
    except Exception as e:
        # Log and handle unexpected errors
        logger.error(f"LLM call failed: {e}")
        return PROMPTS["fail_response"]  # Fallback response
```

Sources: [minirag/prompt.py:313]()

## Internal LLM Function Processing

When you provide a custom LLM function to MiniRAG, it undergoes several processing steps for optimization and control.

### Processing Pipeline

```mermaid
graph TB
    Input["Your llm_model_func"]
    
    subgraph "MiniRAG.__post_init__"
        Limit["limit_async_func_call<br/>max_async=llm_model_max_async"]
        Partial["functools.partial<br/>bind hashing_kv + kwargs"]
        Store["self.llm_model_func<br/>Wrapped function"]
    end
    
    subgraph "Query Execution Context"
        EntityExtract["Entity Extraction<br/>minirag/operate.py"]
        QueryProcess["Query Processing<br/>minirag/operate.py"]
        ResponseGen["Response Generation<br/>minirag/operate.py"]
    end
    
    subgraph "Caching Layer"
        CheckCache{"Cache Hit?"}
        ReturnCached["Return cached result"]
        CallLLM["Call LLM function"]
        SaveCache["Save to cache"]
    end
    
    Input --> Limit
    Limit --> Partial
    Partial --> Store
    
    Store --> EntityExtract
    Store --> QueryProcess
    Store --> ResponseGen
    
    EntityExtract --> CheckCache
    QueryProcess --> CheckCache
    ResponseGen --> CheckCache
    
    CheckCache -->|Yes| ReturnCached
    CheckCache -->|No| CallLLM
    CallLLM --> SaveCache
```

### Concurrency Control

The `limit_async_func_call` wrapper ensures that no more than `llm_model_max_async` concurrent requests are made:

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `llm_model_max_async` | 16 | Maximum concurrent LLM calls |
| Effect | Semaphore control | Prevents API rate limit exhaustion |

### Cache Integration

MiniRAG automatically caches LLM responses when `enable_llm_cache=True`:

```mermaid
graph LR
    LLMCall["LLM Function Call"]
    HashKey["Generate cache key<br/>hash(prompt + system_prompt)"]
    CheckKV{"Key exists in<br/>llm_response_cache?"}
    ReturnCache["Return cached value"]
    ExecuteLLM["Execute LLM"]
    SaveKV["Save response<br/>to cache"]
    Return["Return response"]
    
    LLMCall --> HashKey
    HashKey --> CheckKV
    CheckKV -->|Yes| ReturnCache
    CheckKV -->|No| ExecuteLLM
    ExecuteLLM --> SaveKV
    SaveKV --> Return
```

The cache uses `BaseKVStorage` (typically JSON-based) to persist responses across sessions.

Sources: [minirag/llm/openai.py:109]()

## Configuration Parameters

Configure LLM integration via the `MiniRAG` constructor:

### Core LLM Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `llm_model_func` | `Callable` | `gpt_4o_mini_complete` | Async function for LLM calls |
| `llm_model_name` | `str` | `"gpt-4o-mini"` | Model identifier for API calls |
| `llm_model_max_token_size` | `int` | `32768` | Maximum context window size |
| `llm_model_max_async` | `int` | `16` | Concurrent request limit |
| `llm_model_kwargs` | `dict` | `{}` | Additional model parameters |

### Cache and Performance

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_llm_cache` | `bool` | `True` | Enable response caching |
| `llm_response_cache` | `BaseKVStorage` | Auto-created | Cache storage backend |

### Example Configuration

```python
from minirag import MiniRAG
from minirag.llm.openai import openai_complete

rag = MiniRAG(
    working_dir="./my_rag_system",
    
    # LLM Configuration
    llm_model_func=openai_complete,
    llm_model_name="gpt-4o-mini",
    llm_model_max_token_size=128000,
    llm_model_max_async=32,
    llm_model_kwargs={
        "temperature": 0.7,
        "top_p": 0.95,
        "presence_penalty": 0.0,
        "frequency_penalty": 0.0,
    },
    
    # Cache Configuration
    enable_llm_cache=True,
    
    # Other parameters...
)
```

### Environment Variables

For OpenAI-compatible APIs:

| Variable | Purpose | Example |
|----------|---------|---------|
| `OPENAI_API_KEY` | Authentication | `"sk-..."` |
| `OPENAI_API_BASE` | Custom endpoint | `"https://api.openai.com/v1"` |
| `OPENROUTER_API_KEY` | OpenRouter auth | `"sk-or-v1-..."` |

Set via Python:

```python
import os
os.environ["OPENAI_API_KEY"] = "your-api-key"
os.environ["OPENAI_API_BASE"] = "https://your-custom-endpoint/v1"
```

Sources: [minirag/llm/openai.py:102-108](), [minirag/llm/openai.py:226-227](), [main.py:58-72]()

## Best Practices

When integrating custom LLMs with MiniRAG, consider the following best practices:

1. **Error Handling**: Implement robust error handling in your LLM function to manage API failures, rate limits, and other issues.

2. **Caching**: MiniRAG provides built-in caching for LLM responses. This is enabled by default and can significantly reduce costs and latency for repeated queries.

3. **Concurrency Control**: Use the `llm_model_max_async` parameter to control how many concurrent requests can be made to your LLM, preventing overwhelming the service.

4. **Model Selection**: Choose an appropriate model for each task. For entity extraction, you may need a model with strong analytical capabilities, while for final responses, you might prioritize fluency.

5. **Testing**: Test your custom LLM integration thoroughly, especially with different query types and edge cases.

Sources: [minirag/minirag.py:160-166](), [minirag/minirag.py:296-302]()

## Working with Ollama

For local deployment, you can integrate MiniRAG with Ollama. For more details, see [Ollama Compatibility](#6.3).

## Conclusion

Custom LLM integration in MiniRAG provides flexibility to use the language model that best fits your needs. By following the function signature requirements and best practices outlined in this guide, you can seamlessly integrate any LLM provider or model with MiniRAG.

For more advanced scenarios, consider using the `Model` and `MultiModel` classes to manage multiple LLMs or implement load balancing strategies.

Sources: [minirag/minirag.py:160-166](), [minirag/llm.py:5-33](), [minirag/llm.py:35-84]()

---

# Page: Custom Embedding Models

# Custom Embedding Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [minirag/__init__.py](minirag/__init__.py)
- [minirag/base.py](minirag/base.py)
- [minirag/utils.py](minirag/utils.py)

</details>



This page explains how to use and implement custom embedding models with MiniRAG. Embedding models convert text into vector representations that enable semantic search capabilities in MiniRAG's vector storage systems. For information about integrating custom language models (LLMs), see [Custom LLM Integration](#9.3).

## Overview of Embedding Models in MiniRAG

Embedding models are a core component of MiniRAG's retrieval system. They convert text chunks, entities, and relationships into vector representations that enable semantic similarity search. MiniRAG uses these embeddings for:

1. Semantic search of document chunks
2. Entity matching
3. Relationship similarity
4. Graph-enhanced retrieval

```mermaid
flowchart LR
    subgraph "Text Input"
        Documents["Raw Documents"]
        TextChunks["Text Chunks"]
        Entities["Extracted Entities"]
        Relationships["Relationships"]
        Query["User Query"]
    end

    subgraph "Embedding Process"
        EmbeddingFunc["EmbeddingFunc"]
    end

    subgraph "Vector Storage"
        ChunksVDB["chunks_vdb"]
        EntitiesVDB["entities_vdb"]
        EntityNameVDB["entity_name_vdb"]
        RelationshipsVDB["relationships_vdb"]
    end

    Documents --> TextChunks
    TextChunks --> EmbeddingFunc
    Entities --> EmbeddingFunc
    Relationships --> EmbeddingFunc
    Query --> EmbeddingFunc
    
    EmbeddingFunc --> ChunksVDB
    EmbeddingFunc --> EntitiesVDB
    EmbeddingFunc --> EntityNameVDB
    EmbeddingFunc --> RelationshipsVDB
```

Sources: [minirag/minirag.py:155-156](), [minirag/minirag.py:243-244](), [minirag/minirag.py:270-294]()

## EmbeddingFunc Class

At the core of MiniRAG's embedding system is the `EmbeddingFunc` class, which encapsulates the embedding function with metadata about its capabilities.

```mermaid
classDiagram
    class EmbeddingFunc {
        +embedding_dim: int
        +max_token_size: int
        +func: callable
        +__call__(text) async
    }
```

The `EmbeddingFunc` dataclass has three key attributes:
- `embedding_dim`: The dimensionality of the embedding vectors
- `max_token_size`: Maximum number of tokens the model can process
- `func`: The actual async function that performs embedding

When called, the `EmbeddingFunc` instance delegates to its internal function and returns numpy arrays representing the embeddings.

Sources: [minirag/utils.py:45-52]()

## Creating Custom Embedding Models

To create a custom embedding model for MiniRAG, you need to:

1. Implement an async function that converts text to embeddings
2. Wrap it with the `EmbeddingFunc` class or the `wrap_embedding_func_with_attrs` decorator

### Implementation Requirements

Your embedding function must:
- Be asynchronous (use `async def`)
- Accept text input
- Return a numpy array of embeddings
- Handle batching efficiently (for performance)

### Using the Decorator Approach

The `wrap_embedding_func_with_attrs` decorator provides a convenient way to create an `EmbeddingFunc`:

```python
from minirag.utils import wrap_embedding_func_with_attrs
import numpy as np

@wrap_embedding_func_with_attrs(embedding_dim=1536, max_token_size=8192)
async def my_custom_embedding_func(text_or_texts):
    # Your embedding logic here
    # Return numpy array of shape (embedding_dim,) or (batch_size, embedding_dim)
    return np.random.rand(1536)  # Replace with actual embedding logic
```

Sources: [minirag/utils.py:119-126]()

## Integrating Custom Embedding Models with MiniRAG

To use your custom embedding model with MiniRAG, set the `embedding_func` parameter when initializing the `MiniRAG` class:

```python
from minirag import MiniRAG

minirag = MiniRAG(
    embedding_func=my_custom_embedding_func,
    embedding_batch_num=32,  # Batch size for processing embeddings
    embedding_func_max_async=16,  # Maximum concurrent embedding operations
    # Other MiniRAG parameters...
)
```

MiniRAG automatically passes this embedding function to all its storage components that require vector representations:

```mermaid
flowchart TD
    subgraph "MiniRAG Initialization"
        direction TB
        Config["MiniRAG Configuration"]
        EmbeddingFunc["Custom EmbeddingFunc"]
        LimitAsyncWrapper["limit_async_func_call wrapper"]
    end
    
    subgraph "Storage Components"
        direction TB
        FullDocs["full_docs (KV Storage)"]
        TextChunks["text_chunks (KV Storage)"]
        ChunkEntityGraph["chunk_entity_relation_graph (Graph Storage)"]
        EntitiesVDB["entities_vdb (Vector Storage)"]
        EntityNameVDB["entity_name_vdb (Vector Storage)"]
        RelationshipsVDB["relationships_vdb (Vector Storage)"]
        ChunksVDB["chunks_vdb (Vector Storage)"]
    end
    
    Config --> EmbeddingFunc
    EmbeddingFunc --> LimitAsyncWrapper
    LimitAsyncWrapper --> FullDocs
    LimitAsyncWrapper --> TextChunks
    LimitAsyncWrapper --> ChunkEntityGraph
    LimitAsyncWrapper --> EntitiesVDB
    LimitAsyncWrapper --> EntityNameVDB
    LimitAsyncWrapper --> RelationshipsVDB
    LimitAsyncWrapper --> ChunksVDB
```

Sources: [minirag/minirag.py:243-294]()

## Performance Considerations

MiniRAG includes mechanisms to manage the performance of embedding operations:

1. **Concurrency Limits**: The `embedding_func_max_async` parameter (default: 16) limits the number of concurrent embedding operations to prevent overwhelming the embedding service.

2. **Batching**: The `embedding_batch_num` parameter (default: 32) controls the batch size for embedding operations.

3. **Limiting Mechanism**: The `limit_async_func_call` wrapper ensures that embedding operations are throttled to the specified concurrency limit.

These controls are important when using external embedding APIs that might have rate limits or when running on hardware with limited resources.

### Embedding Quantization

MiniRAG provides utility functions for quantizing embeddings to reduce storage space and improve memory efficiency:

| Function | Purpose | Parameters |
|----------|---------|------------|
| `quantize_embedding` | Converts float embeddings to 8-bit integers | `embedding`: numpy array or list<br/>`bits`: quantization bits (default: 8) |
| `dequantize_embedding` | Converts quantized embeddings back to floats | `quantized`: numpy array<br/>`min_val`, `max_val`: stored scaling factors<br/>`bits`: quantization bits (default: 8) |

Quantization process:
1. Calculate min/max values from the embedding
2. Scale values to 0-255 range (for 8-bit)
3. Round to nearest integer and convert to uint8
4. Store min_val and max_val for reconstruction

This can reduce storage by ~75% (from float32 to uint8) with minimal impact on retrieval quality.

Sources: [minirag/utils.py:97-116](), [minirag/utils.py:450-463]()

## Examples

### Using OpenAI Embeddings

Here's an example of how to implement and use OpenAI's embedding model with MiniRAG:

```python
import numpy as np
import openai
from minirag.utils import wrap_embedding_func_with_attrs
from minirag import MiniRAG

@wrap_embedding_func_with_attrs(embedding_dim=1536, max_token_size=8191)
async def openai_embedding_func(text_or_texts):
    # Handle batching
    is_batch = isinstance(text_or_texts, list)
    texts = text_or_texts if is_batch else [text_or_texts]
    
    # Call OpenAI API
    response = await openai.Embedding.acreate(
        input=texts,
        model="text-embedding-ada-002"
    )
    
    # Extract embeddings
    embeddings = [np.array(item["embedding"]) for item in response["data"]]
    
    # Return single embedding or batch
    if not is_batch:
        return embeddings[0]
    return embeddings

# Initialize MiniRAG with the custom embedding function
minirag = MiniRAG(
    embedding_func=openai_embedding_func,
    embedding_func_max_async=5,  # Limit concurrent API calls
    # Other parameters...
)
```

### Using Sentence Transformers

Here's an example using the popular Sentence Transformers library:

```python
import numpy as np
from sentence_transformers import SentenceTransformer
from minirag.utils import wrap_embedding_func_with_attrs
from minirag import MiniRAG

# Load model once at module level
model = SentenceTransformer('all-MiniLM-L6-v2')

@wrap_embedding_func_with_attrs(embedding_dim=384, max_token_size=512)
async def sentence_transformer_embedding_func(text_or_texts):
    # Convert to asynchronous operation
    import asyncio
    
    def _embed(texts):
        return model.encode(texts, convert_to_numpy=True)
    
    # Handle batching
    is_batch = isinstance(text_or_texts, list)
    texts = text_or_texts if is_batch else [text_or_texts]
    
    # Run in thread pool to not block the event loop
    embeddings = await asyncio.get_event_loop().run_in_executor(
        None, _embed, texts
    )
    
    # Return single embedding or batch
    if not is_batch:
        return embeddings[0]
    return embeddings

# Initialize MiniRAG with the custom embedding function
minirag = MiniRAG(
    embedding_func=sentence_transformer_embedding_func,
    embedding_func_max_async=10,
    # Other parameters...
)
```

### Using Quantized Embeddings

To save storage space, you can implement quantization in your embedding function:

```python
import numpy as np
from minirag.utils import wrap_embedding_func_with_attrs, quantize_embedding, dequantize_embedding
from minirag import MiniRAG

@wrap_embedding_func_with_attrs(embedding_dim=384, max_token_size=512)
async def quantized_embedding_func(text_or_texts):
    # Get original embeddings (your implementation)
    embeddings = await get_embeddings(text_or_texts)
    
    # Quantize to reduce storage
    quantized, min_val, max_val = quantize_embedding(embeddings, bits=8)
    
    # Store quantized values and scaling factors
    # You would typically store min_val and max_val alongside the quantized data
    
    # For immediate use, dequantize back to float32
    dequantized = dequantize_embedding(quantized, min_val, max_val, bits=8)
    
    return dequantized
```

This approach reduces embedding storage requirements by approximately 75% while maintaining retrieval quality.

## Integration with Storage Components

MiniRAG automatically integrates your custom embedding model with all storage components that require vector operations through the base storage classes. The `embedding_func` is stored in the following base classes:

```mermaid
graph TB
    EmbeddingFunc["EmbeddingFunc<br/>(embedding_dim, max_token_size, func)"]
    
    subgraph "Base Storage Classes"
        BaseVectorStorage["BaseVectorStorage<br/>embedding_func: EmbeddingFunc"]
        BaseKVStorage["BaseKVStorage<br/>embedding_func: EmbeddingFunc"]
        BaseGraphStorage["BaseGraphStorage<br/>embedding_func: EmbeddingFunc"]
    end
    
    subgraph "Storage Instances"
        ChunksVDB["chunks_vdb<br/>(BaseVectorStorage)"]
        EntitiesVDB["entities_vdb<br/>(BaseVectorStorage)"]
        EntityNameVDB["entity_name_vdb<br/>(BaseVectorStorage)"]
        RelationshipsVDB["relationships_vdb<br/>(BaseVectorStorage)"]
        FullDocs["full_docs<br/>(BaseKVStorage)"]
        TextChunks["text_chunks<br/>(BaseKVStorage)"]
        ChunkEntityGraph["chunk_entity_relation_graph<br/>(BaseGraphStorage)"]
    end
    
    EmbeddingFunc --> BaseVectorStorage
    EmbeddingFunc --> BaseKVStorage
    EmbeddingFunc --> BaseGraphStorage
    
    BaseVectorStorage --> ChunksVDB
    BaseVectorStorage --> EntitiesVDB
    BaseVectorStorage --> EntityNameVDB
    BaseVectorStorage --> RelationshipsVDB
    
    BaseKVStorage --> FullDocs
    BaseKVStorage --> TextChunks
    
    BaseGraphStorage --> ChunkEntityGraph
```

### Storage Class Attributes

| Storage Class | Embedding Attribute | Purpose |
|---------------|---------------------|---------|
| `BaseVectorStorage` | `embedding_func: EmbeddingFunc` | Vector similarity search operations |
| `BaseKVStorage` | `embedding_func: EmbeddingFunc` | Key-value storage with embedding support |
| `BaseGraphStorage` | `embedding_func: EmbeddingFunc` | Graph storage with optional node embeddings |

During initialization, MiniRAG passes your custom `embedding_func` to all storage instances that extend these base classes, ensuring consistency across:

1. **Vector Storages**: Document chunks, entity descriptions, entity names, and relationships
2. **Key-Value Storages**: Full document storage and text chunk storage
3. **Graph Storage**: The chunk-entity-relation graph structure

This integrated approach ensures all text-to-vector transformations use the same embedding model throughout the system.

Sources: [minirag/base.py:63-74](), [minirag/base.py:78-100](), [minirag/base.py:104-148]()

## Best Practices

1. **Dimensionality Consistency**: Ensure your embedding model's dimension is consistent with your vector database requirements.

2. **Async Implementation**: Always implement embedding functions as async to work with MiniRAG's asynchronous architecture.

3. **Batching Support**: Design your embedding function to efficiently handle both single texts and batches.

4. **Error Handling**: Include robust error handling in your embedding function, especially when using external APIs.

5. **Resource Management**: Set appropriate concurrency limits with `embedding_func_max_async` to prevent overwhelming resources.

6. **Cache Embeddings**: For production systems, consider implementing caching for frequent embedding operations.

7. **Model Size vs. Performance**: Balance embedding model size with performance requirements - larger models may provide better semantic understanding but at the cost of speed.

---

# Page: Community and Support

# Community and Support

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Communication.md](Communication.md)
- [README.md](README.md)

</details>



This document provides information on how to get help with MiniRAG, connect with other users and developers, contribute to the project, and properly acknowledge the work. It covers official communication channels, related projects in the HKUDS ecosystem, contribution guidelines, and citation information.

For technical documentation on extending MiniRAG with custom implementations, see [Extending MiniRAG](#10).

---

## Communication Channels

MiniRAG maintains active community discussion groups on two primary platforms for users to seek support, share experiences, and discuss implementation details.

### Official Discussion Groups

| Platform | Access Method | Purpose |
|----------|---------------|---------|
| **WeChat** | Scan QR code in [Communication.md](Communication.md:1-6)() | Real-time chat, quick questions, community updates |
| **Feishu** | Scan QR code in [Communication.md](Communication.md:1-6)() | Structured discussions, technical documentation sharing |

Both platforms are hosted by HKUDS (Hong Kong University Data Science Lab) and provide direct access to the development team and active community members.

**Communication Channels Overview**

```mermaid
graph TB
    User["User/Developer"]
    
    subgraph "Official Channels"
        WeChat["WeChat Group<br/>Communication.md"]
        Feishu["Feishu Group<br/>Communication.md"]
    end
    
    subgraph "Code Repository"
        GitHub["GitHub Repository<br/>github.com/HKUDS/MiniRAG"]
        Issues["GitHub Issues"]
        Discussions["GitHub Discussions"]
    end
    
    subgraph "Documentation"
        README["README.md"]
        READMECN["README_CN.md"]
        READMEJA["README_JA.md"]
        Wiki["Wiki Pages"]
    end
    
    User --> WeChat
    User --> Feishu
    User --> GitHub
    User --> README
    
    GitHub --> Issues
    GitHub --> Discussions
    README --> READMECN
    README --> READMEJA
    README --> Wiki
    
    WeChat -.community support.-> User
    Feishu -.community support.-> User
    Issues -.bug reports & features.-> User
    Discussions -.technical Q&A.-> User
```

Sources: [README.md:5-6](), [Communication.md:1-6]()

### Accessing the QR Codes

The QR codes for joining both WeChat and Feishu groups are available in the Communication.md file. The image is hosted at the HKUDS GitHub organization profile location and displays both platform options.

```bash
# View the communication guide
cat Communication.md
```

Sources: [Communication.md:1-6]()

---

## Related Projects

MiniRAG is part of a broader ecosystem of projects developed by the HKUDS team, focusing on efficient retrieval-augmented generation for various modalities and deployment scenarios.

### VideoRAG

**VideoRAG** is a related project released by the HKUDS team in February 2025 that extends RAG capabilities to extremely long-context video understanding scenarios.

| Project | Repository | Release Date | Focus Area |
|---------|-----------|--------------|------------|
| **MiniRAG** | [github.com/HKUDS/MiniRAG](https://github.com/HKUDS/MiniRAG) | January 2025 | Small model RAG for text |
| **VideoRAG** | [github.com/HKUDS/VideoRAG](https://github.com/HKUDS/VideoRAG) | February 2025 | Long-context video understanding |

The VideoRAG project applies similar principles of efficient retrieval and lightweight processing to video modality, addressing challenges in understanding extended video content.

Sources: [README.md:27]()

**MiniRAG Ecosystem and Related Projects**

```mermaid
graph TB
    subgraph "HKUDS Research Group"
        Team["HKUDS Team<br/>HKU Data Science Lab"]
    end
    
    subgraph "MiniRAG Project"
        MiniRAG["MiniRAG<br/>minirag.py"]
        
        subgraph "Core Components"
            Storage["Storage Layer<br/>base.py, storage.py"]
            LLM["LLM Integration<br/>llm.py"]
            Operate["RAG Operations<br/>operate.py"]
        end
        
        Paper["Paper<br/>arXiv:2501.06713"]
        Dataset["LiHua-World Dataset<br/>dataset/LiHua-World/"]
    end
    
    subgraph "Related Projects"
        VideoRAG["VideoRAG<br/>github.com/HKUDS/VideoRAG<br/>Video Understanding"]
    end
    
    subgraph "Foundation Projects"
        LightRAG["LightRAG<br/>github.com/HKUDS/LightRAG<br/>Base Framework"]
        NanoGraphRAG["nano-graphrag<br/>github.com/gusye1234/nano-graphrag<br/>Graph Processing"]
    end
    
    Team --> MiniRAG
    Team --> VideoRAG
    
    MiniRAG --> Storage
    MiniRAG --> LLM
    MiniRAG --> Operate
    
    MiniRAG --> Paper
    MiniRAG --> Dataset
    
    LightRAG -.code foundation.-> MiniRAG
    NanoGraphRAG -.graph utilities.-> MiniRAG
    
    MiniRAG -.techniques.-> VideoRAG
```

Sources: [README.md:27](), [README.md:158-160]()

---

## Contributing

MiniRAG welcomes contributions from the community. The project maintains a public contributor graph and acknowledges all participants.

### Contribution Overview

The project displays its contributor history using the contrib.rocks service, which automatically generates visual representations of all GitHub contributors.

**Contributor Recognition**

Contributors are publicly acknowledged in the README.md file at lines 149-155. The contributor graph is automatically generated from GitHub commit history and displays all individuals who have contributed code, documentation, or other improvements to the repository.

```markdown
# From README.md
<a href="https://github.com/HKUDS/MiniRAG/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=HKUDS/MiniRAG" />
</a>
```

### How to Contribute

1. **Fork the Repository**: Create a personal fork of [github.com/HKUDS/MiniRAG](https://github.com/HKUDS/MiniRAG)
2. **Create a Branch**: Work on features or fixes in dedicated branches
3. **Submit Pull Requests**: Submit PRs with clear descriptions of changes
4. **Follow Code Standards**: Maintain consistency with existing codebase patterns

For technical details on implementing custom storage backends, LLM providers, or embedding models, refer to [Extending MiniRAG](#10).

Sources: [README.md:149-155]()

---

## Acknowledgments

MiniRAG builds upon foundational work from two key open-source projects that provide core functionality for graph processing and RAG operations.

### Foundation Projects

| Project | Repository | Contribution to MiniRAG |
|---------|-----------|-------------------------|
| **LightRAG** | [github.com/HKUDS/LightRAG](https://github.com/HKUDS/LightRAG) | Base framework for RAG operations, storage abstractions, and query processing |
| **nano-graphrag** | [github.com/gusye1234/nano-graphrag](https://github.com/gusye1234/nano-graphrag) | Graph processing utilities and lightweight graph operations |

MiniRAG extends LightRAG's architecture with innovations specifically designed for Small Language Models (SLMs), including heterogeneous graph indexing and topology-enhanced retrieval. The relationship between these projects is evident in the codebase structure:

- MiniRAG can be installed via `pip install lightrag-hku` as noted in [README.md:52-55]()
- The storage abstraction layer in [minirag/base.py]() inherits architectural patterns from LightRAG
- Graph processing utilities leverage concepts from nano-graphrag

**Dependency and Acknowledgment Relationships**

```mermaid
graph TB
    subgraph "Foundation Layer"
        NanoGraphRAG["nano-graphrag<br/>gusye1234/nano-graphrag<br/>Graph utilities"]
        LightRAG["LightRAG<br/>HKUDS/LightRAG<br/>RAG framework"]
    end
    
    subgraph "MiniRAG Implementation"
        MiniRAGCore["minirag.py<br/>Main orchestrator"]
        
        subgraph "Inherited Components"
            BaseStorage["base.py<br/>BaseGraphStorage<br/>BaseVectorStorage<br/>BaseKVStorage"]
            OperateModule["operate.py<br/>Entity extraction<br/>Query processing"]
            UtilsModule["utils.py<br/>Text processing<br/>Graph utilities"]
        end
        
        subgraph "MiniRAG Innovations"
            HeteroGraph["Heterogeneous Graph Indexing<br/>Text chunks + Named entities"]
            TopoRetrieval["Topology-Enhanced Retrieval<br/>k-hop neighbor queries"]
        end
    end
    
    subgraph "Installation"
        PyPI["PyPI Package<br/>lightrag-hku<br/>minirag-hku"]
    end
    
    NanoGraphRAG -.graph processing.-> UtilsModule
    LightRAG -.framework base.-> BaseStorage
    LightRAG -.RAG operations.-> OperateModule
    
    BaseStorage --> MiniRAGCore
    OperateModule --> MiniRAGCore
    UtilsModule --> MiniRAGCore
    
    MiniRAGCore --> HeteroGraph
    MiniRAGCore --> TopoRetrieval
    
    LightRAG --> PyPI
    MiniRAGCore --> PyPI
```

Sources: [README.md:158-160](), [README.md:52-55]()

### Acknowledgment Text

The following acknowledgment appears in the README.md file:

> "You may refer to related work that serves as foundations for our framework and code repository, nano-graphrag and LightRAG. Thanks for their wonderful works."

This acknowledgment is located at [README.md:158-160]() and recognizes the technical contributions of both foundational projects.

Sources: [README.md:158-160]()

---

## Citation

When using MiniRAG in academic research or publications, please cite the original paper using the following BibTeX entry.

### BibTeX Citation

```bibtex
@article{fan2025minirag,
  title={MiniRAG: Towards Extremely Simple Retrieval-Augmented Generation},
  author={Fan, Tianyu and Wang, Jingyuan and Ren, Xubin and Huang, Chao},
  journal={arXiv preprint arXiv:2501.06713},
  year={2025}
}
```

### Paper Information

| Field | Value |
|-------|-------|
| **Title** | MiniRAG: Towards Extremely Simple Retrieval-Augmented Generation |
| **Authors** | Tianyu Fan, Jingyuan Wang, Xubin Ren, Chao Huang |
| **Venue** | arXiv preprint |
| **arXiv ID** | 2501.06713 |
| **Year** | 2025 |
| **Link** | [https://arxiv.org/abs/2501.06713](https://arxiv.org/abs/2501.06713) |

### Author Affiliations

The author information with links to their profiles is available in [README.md:12](). The corresponding author is Chao Huang, indicated by an asterisk in the author list.

**Research Team Structure**

```mermaid
graph TB
    subgraph "MiniRAG Research Team"
        Corresponding["Chao Huang*<br/>*Correspondence<br/>sites.google.com/view/chaoh"]
        
        subgraph "Co-Authors"
            TianyuFan["Tianyu Fan<br/>tianyufan0504.github.io"]
            JingyuanWang["Jingyuan Wang<br/>scholar.google.com"]
            XubinRen["Xubin Ren<br/>ren-xubin.github.io"]
        end
    end
    
    subgraph "Research Output"
        Paper["Paper<br/>arXiv:2501.06713"]
        Codebase["Codebase<br/>github.com/HKUDS/MiniRAG"]
        Dataset["Dataset<br/>LiHua-World"]
    end
    
    subgraph "Community"
        Contributors["Contributors<br/>contrib.rocks"]
        Users["Users & Adopters"]
    end
    
    Corresponding --> Paper
    TianyuFan --> Paper
    JingyuanWang --> Paper
    XubinRen --> Paper
    
    Paper --> Codebase
    Paper --> Dataset
    
    Codebase --> Contributors
    Codebase --> Users
    
    Contributors -.feedback.-> Corresponding
    Users -.questions.-> Contributors
```

Sources: [README.md:12](), [README.md:162-170]()

---

## Star History

MiniRAG tracks its GitHub star history to monitor community interest and adoption. The star history chart is automatically generated and embedded in the README.md file.

The project uses the star-history.com service to display growth over time, supporting both light and dark color schemes for accessibility.

Sources: [README.md:139-147]()

---

## Multi-Language Documentation

MiniRAG provides documentation in multiple languages to support its international user base:

| Language | File | Purpose |
|----------|------|---------|
| **English** | [README.md]() | Primary documentation for international audience |
| **Chinese (中文)** | [README_CN.md]() | 中文用户的完整文档 |
| **Japanese (日本語)** | [README_JA.md]() | 日本語ユーザー向けドキュメント |

These translations are maintained in the repository root and provide comprehensive coverage of installation, usage, and technical details in each respective language.

Sources: [README.md:18-20]()

---

## Getting Help

When seeking support for MiniRAG, follow this escalation path:

1. **Check Documentation**: Review the wiki pages and README files in your preferred language
2. **Search Issues**: Look through [GitHub Issues](https://github.com/HKUDS/MiniRAG/issues) for similar problems
3. **Join Discussion Groups**: Ask questions in WeChat or Feishu groups for community support
4. **Report Bugs**: Create a GitHub issue with reproduction steps and environment details
5. **Contact Team**: For research collaborations or specific inquiries, contact the corresponding author

For questions about specific implementations:
- Storage backends: See [Storage Implementations](#5)
- LLM integration: See [LLM and Embedding Integration](#6)
- Custom extensions: See [Extending MiniRAG](#10)

Sources: [README.md:5-6](), [Communication.md:1-6]()