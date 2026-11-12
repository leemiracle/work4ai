<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/rag-from-scratch · page 8 Implementation Best Practices · fetched 2026-10-26 -->

# Implementation Best Practices

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [rag_from_scratch_10_and_11.ipynb](rag_from_scratch_10_and_11.ipynb)
- [rag_from_scratch_12_to_14.ipynb](rag_from_scratch_12_to_14.ipynb)
- [rag_from_scratch_15_to_18.ipynb](rag_from_scratch_15_to_18.ipynb)
- [rag_from_scratch_1_to_4.ipynb](rag_from_scratch_1_to_4.ipynb)
- [rag_from_scratch_5_to_9.ipynb](rag_from_scratch_5_to_9.ipynb)

</details>



This page outlines the key best practices for implementing Retrieval-Augmented Generation (RAG) systems based on the patterns and techniques demonstrated throughout the RAG-from-scratch repository. It focuses on practical recommendations for each component of the RAG pipeline, from document processing to evaluation, highlighting approaches that enhance performance, accuracy, and maintainability.

## Document Processing Best Practices

Effective document processing forms the foundation of any RAG system. The quality of your chunks directly impacts retrieval performance.

### Chunking Strategies

```mermaid
graph TD
    subgraph "Data Preparation Space"
    A["Raw Document"] -- "TextSplitter.split_documents()" --> B["Document Chunks"]
    B -- "Embeddings.embed_documents()" --> C["VectorStore (Chroma/FAISS)"]
    end

    subgraph "Code Entity Space"
    B1["RecursiveCharacterTextSplitter"]
    B2["CharacterTextSplitter"]
    C1["Chroma.from_documents()"]
    end

    B -- "implemented by" --> B1
    B -- "alternative" --> B2
    C -- "instantiated via" --> C1

    Sources: [rag_from_scratch_1_to_4.ipynb:55-75](), [rag_from_scratch_5_to_9.ipynb:10-30]()
```

**Chunk size optimization:**
- Balance chunk size against query specificity. Smaller chunks (e.g., `chunk_size=250`) work well for specific queries, while larger chunks preserve more context [rag_from_scratch_1_to_4.ipynb:55-65]().
- **Chunk overlap:** Implement overlap (e.g., `chunk_overlap=50`) to avoid losing context at boundaries [rag_from_scratch_1_to_4.ipynb:58-60]().

**Semantic chunking:**
- Use `RecursiveCharacterTextSplitter` to maintain structural integrity by splitting on natural delimiters like newlines and spaces [rag_from_scratch_1_to_4.ipynb:62-70]().

Sources: [rag_from_scratch_1_to_4.ipynb](), [rag_from_scratch_5_to_9.ipynb]()

## Advanced Retrieval Best Practices

Retrieval quality directly affects the accuracy of the generated content. Multiple techniques can be combined for optimal results.

### Multi-Query and Decomposition

```mermaid
sequenceDiagram
    participant U as "User Query"
    participant LLM as "LLM (ChatOpenAI)"
    participant R as "Retriever"
    participant V as "VectorStore (Chroma)"

    U->>LLM: "Generate variations of query"
    LLM-->>U: "List of 5 unique queries"
    loop For each query
        U->>R: "invoke(query)"
        R->>V: "similarity_search()"
        V-->>R: "Documents"
    end
    R-->>U: "Unique Union of Documents"

    Note over U,V: Multi-Query Retrieval Pattern
    Sources: [rag_from_scratch_5_to_9.ipynb:55-120]()
```

**Query Transformation:**
- **Multi-Query:** Use an LLM to generate multiple perspectives of a user query to overcome distance-based retrieval limitations [rag_from_scratch_5_to_9.ipynb:55-80]().
- **RAG-Fusion:** Apply Reciprocal Rank Fusion (RRF) to re-rank documents retrieved from multiple query variations [rag_from_scratch_5_to_9.ipynb:135-160]().
- **Decomposition:** For complex questions, decompose the query into sub-questions and solve them sequentially (Sub-query decomposition) [rag_from_scratch_5_to_9.ipynb:350-380]().

Sources: [rag_from_scratch_5_to_9.ipynb]()

## Indexing and Storage Best Practices

Efficiently mapping documents to vector space requires balancing granularity and context.

### Multi-Vector Indexing
- **Summary Indexing:** Instead of indexing raw chunks, index a summary of the chunk created by an LLM. This often captures the "essence" better for retrieval while the raw chunk is passed to the LLM for generation [rag_from_scratch_10_and_11.ipynb:50-100]().
- **Parent-Document Retrieval:** Index small "child" chunks for precise retrieval but return the larger "parent" document to the LLM to provide broader context [rag_from_scratch_10_and_11.ipynb:150-200]().

Sources: [rag_from_scratch_10_and_11.ipynb]()

## Context Assembly and Generation Best Practices

How information is presented to the LLM significantly impacts generation quality.

### Reranking and Filtering
- **Cohere Rerank:** Use a specialized reranker (like `CohereRerank`) after initial retrieval to narrow down the top-K documents based on true semantic relevance rather than just vector distance [rag_from_scratch_10_and_11.ipynb:400-450]().
- **Long-Context Handling:** When dealing with many documents, be mindful of the "lost in the middle" phenomenon. Place the most critical information at the beginning or end of the prompt [rag_from_scratch_12_to_14.ipynb:100-150]().

### Prompt Engineering
- **Clear Instructions:** Use templates that explicitly tell the LLM to use *only* the provided context to answer the question [rag_from_scratch_1_to_4.ipynb:110-125]().
- **Structured Output:** When integrating with downstream systems, use `Pydantic` or JSON mode to ensure the LLM returns parsable data [rag_from_scratch_15_to_18.ipynb:200-250]().

Sources: [rag_from_scratch_1_to_4.ipynb](), [rag_from_scratch_10_and_11.ipynb](), [rag_from_scratch_12_to_14.ipynb](), [rag_from_scratch_15_to_18.ipynb]()

## Evaluation and Optimization Best Practices

Systematic evaluation is crucial for measuring RAG performance.

**RAGAS Metrics:**
- **Faithfulness:** Does the answer come from the retrieved context? [rag_from_scratch_12_to_14.ipynb:500-550]()
- **Answer Relevance:** Does the answer actually address the user's query? [rag_from_scratch_12_to_14.ipynb:551-600]()
- **Context Precision:** Is the retrieved context actually useful for the query? [rag_from_scratch_12_to_14.ipynb:601-650]()

Sources: [rag_from_scratch_12_to_14.ipynb]()

## Summary Table

| Category | Best Practice | Key Code Entity / Function |
| :--- | :--- | :--- |
| **Indexing** | Use Recursive Splitting | `RecursiveCharacterTextSplitter` |
| **Retrieval** | Generate Multiple Queries | `MultiQueryRetriever` |
| **Retrieval** | Re-rank Results | `CohereRerank` |
| **Storage** | Multi-Vector Retrieval | `MultiVectorRetriever` |
| **Generation** | Context Compression | `ContextualCompressionRetriever` |
| **Evaluation** | Automated Testing | `ragas` library |

Sources: [rag_from_scratch_1_to_4.ipynb](), [rag_from_scratch_5_to_9.ipynb](), [rag_from_scratch_10_and_11.ipynb](), [rag_from_scratch_12_to_14.ipynb]()

---

