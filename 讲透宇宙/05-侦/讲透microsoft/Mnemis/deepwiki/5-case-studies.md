<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/Mnemis · page 5 Case Studies · fetched 2026-10-26 -->

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

