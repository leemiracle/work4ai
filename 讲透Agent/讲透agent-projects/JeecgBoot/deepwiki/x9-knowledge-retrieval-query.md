<!-- source: DeepWiki mcp.deepwiki.com · repo jeecgboot/JeecgBoot · extra page Knowledge Retrieval & Query · fetched 2026-10-29 -->

# Knowledge Retrieval & Query

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [jeecg-boot/jeecg-boot-base-core/src/main/resources/config/default-spring-doc.properties](jeecg-boot/jeecg-boot-base-core/src/main/resources/config/default-spring-doc.properties)
- [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java](jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java)
- [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/service/impl/AiragKnowledgeDocServiceImpl.java](jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/service/impl/AiragKnowledgeDocServiceImpl.java)
- [jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/application-dev.yml](jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/application-dev.yml)
- [jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/application-dm8.yml](jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/application-dm8.yml)
- [jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/application-docker.yml](jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/application-docker.yml)
- [jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/application-kingbase8.yml](jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/application-kingbase8.yml)
- [jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/application-oracle.yml](jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/application-oracle.yml)
- [jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/application-postgresql.yml](jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/application-postgresql.yml)
- [jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/application-prod.yml](jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/application-prod.yml)
- [jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/application-sqlserver.yml](jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/application-sqlserver.yml)
- [jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/application-test.yml](jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/application-test.yml)
- [jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/logback-spring.xml](jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/logback-spring.xml)

</details>



## Purpose and Scope

This document describes the knowledge retrieval and query mechanisms in JeecgBoot's AI RAG system. It covers how user queries are converted to vector embeddings, how semantic search is performed against the pgvector database, and how results are ranked and filtered.

**Retrieval vs Ingestion:**
- **Ingestion** (covered in 3.3.1): Documents → Text Chunks → Embeddings → Storage
- **Retrieval** (this page): User Query → Query Embedding → Vector Search → Ranked Results

This document focuses on the retrieval phase of the RAG pipeline. The same embedding model used during document ingestion must be used for query embedding to ensure vector compatibility.

---

## Retrieval Architecture Overview

The knowledge retrieval system uses vector similarity search to find relevant document segments from one or more knowledge bases. The architecture leverages LangChain4j's embedding abstractions and PostgreSQL's pgvector extension.

### System Components

```mermaid
graph TB
    subgraph "Query Input"
        USER_QUERY["User Query Text"]
        KNOW_IDS["Knowledge Base IDs"]
        PARAMS["Search Parameters<br/>topNumber, similarity"]
    end
    
    subgraph "Embedding Layer"
        EMBED_MODEL["EmbeddingModel<br/>(LangChain4j)"]
        QUERY_EMBED["Query Embedding<br/>Vector"]
    end
    
    subgraph "Search Execution - EmbeddingHandler"
        SEARCH_METHOD["embeddingSearch()<br/>Multi-KB Entry Point"]
        SINGLE_SEARCH["searchEmbedding()<br/>Single KB Search"]
        QUERY_ROUTER["getQueryRouter()<br/>LangChain4j Integration"]
    end
    
    subgraph "Vector Store - PgVectorEmbeddingStore"
        SEARCH_REQUEST["EmbeddingSearchRequest<br/>maxResults<br/>minScore<br/>filter"]
        PGVECTOR_STORE["PgVectorEmbeddingStore"]
        FILTER["MetadataFilter<br/>knowledgeId, docId"]
    end
    
    subgraph "Database - PostgreSQL"
        EMBEDDINGS_TABLE["embeddings table<br/>id, embedding, metadata"]
        PGVECTOR_INDEX["IVFFlat Index<br/>Vector Similarity"]
    end
    
    subgraph "Result Processing"
        MATCHES["List&lt;EmbeddingMatch&gt;<br/>score, embedded, metadata"]
        SORT_RANK["Score-based Ranking<br/>Descending Order"]
        TOP_N["Top N Results<br/>Limited by topNumber"]
        KNOWLEDGE_RESULT["KnowledgeSearchResult<br/>data: String<br/>documents: List"]
    end
    
    USER_QUERY --> EMBED_MODEL
    KNOW_IDS --> SEARCH_METHOD
    PARAMS --> SEARCH_METHOD
    
    EMBED_MODEL --> QUERY_EMBED
    QUERY_EMBED --> SINGLE_SEARCH
    
    SEARCH_METHOD --> SINGLE_SEARCH
    SINGLE_SEARCH --> SEARCH_REQUEST
    SEARCH_REQUEST --> FILTER
    SEARCH_REQUEST --> PGVECTOR_STORE
    FILTER --> PGVECTOR_STORE
    
    PGVECTOR_STORE --> EMBEDDINGS_TABLE
    EMBEDDINGS_TABLE --> PGVECTOR_INDEX
    PGVECTOR_INDEX --> MATCHES
    
    MATCHES --> SORT_RANK
    SORT_RANK --> TOP_N
    TOP_N --> KNOWLEDGE_RESULT
```

**Sources:** [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:196-313]()

---

## Search Parameters

The retrieval system accepts three primary parameters that control search behavior:

| Parameter | Type | Default | Description | Code Reference |
|-----------|------|---------|-------------|----------------|
| `topNumber` | Integer | 5 | Maximum number of results to return per knowledge base | [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:200]() |
| `similarity` | Double | 0.75 | Minimum similarity score threshold (0.0-1.0) | [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:246]() |
| `knowIds` | List&lt;String&gt; | Required | List of knowledge base IDs to search | [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:197]() |

### Parameter Resolution

```mermaid
graph LR
    INPUT_PARAMS["Input Parameters<br/>topNumber, similarity"]
    MODEL_DEFAULTS["AiModelOptions<br/>topNumber: 5<br/>similarity: 0.75"]
    RESOLVED["Resolved Parameters<br/>oConvertUtils.getInteger/getDou"]
    
    INPUT_PARAMS -->|"if null"| MODEL_DEFAULTS
    MODEL_DEFAULTS --> RESOLVED
    INPUT_PARAMS -->|"if provided"| RESOLVED
```

**Default Value Logic:**
- `topNumber`: Falls back to `modelOptions.getTopNumber()` (default 5). [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:245]()
- `similarity`: Falls back to `modelOptions.getSimilarity()` (default 0.75). [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:246]()

**Sources:** [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:245-246]()

---

## Query Execution Flow

### Single Knowledge Base Retrieval

The `searchEmbedding` method executes retrieval against a single knowledge base:

```mermaid
sequenceDiagram
    participant Caller
    participant EmbeddingHandler
    participant AiModelFactory
    participant EmbeddingModel
    participant PgVectorStore
    participant PostgreSQL
    
    Caller->>EmbeddingHandler: searchEmbedding(knowId, queryText, topNumber, similarity)
    EmbeddingHandler->>EmbeddingHandler: Load AiragKnowledge by knowId
    EmbeddingHandler->>EmbeddingHandler: Get AiragModel (embed model)
    EmbeddingHandler->>EmbeddingHandler: buildModelOptions(model)
    EmbeddingHandler->>AiModelFactory: createEmbeddingModel(options)
    AiModelFactory-->>EmbeddingHandler: EmbeddingModel instance
    
    EmbeddingHandler->>EmbeddingModel: embed(queryText)
    EmbeddingModel-->>EmbeddingHandler: Embedding queryEmbedding
    
    EmbeddingHandler->>EmbeddingHandler: Build EmbeddingSearchRequest<br/>queryEmbedding<br/>maxResults=topNumber<br/>minScore=similarity<br/>filter=knowledgeId
    
    EmbeddingHandler->>EmbeddingHandler: getEmbedStore(model)
    EmbeddingHandler->>PgVectorStore: search(embeddingSearchRequest)
    PgVectorStore->>PostgreSQL: SELECT with vector similarity<br/><-> operator<br/>WHERE metadata->>'knowledgeId' = ?<br/>AND similarity >= minScore<br/>LIMIT maxResults
    PostgreSQL-->>PgVectorStore: Matching rows
    PgVectorStore-->>EmbeddingHandler: List<EmbeddingMatch<TextSegment>>
    
    EmbeddingHandler->>EmbeddingHandler: Map to result format<br/>{score, content, chunk, docName}
    EmbeddingHandler-->>Caller: List<Map<String, Object>>
```

**Key Methods:**
- `EmbeddingHandler.searchEmbedding()` [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:234-269]()
- `EmbeddingHandler.getEmbedStore()` [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:373-422]()
- `EmbeddingHandler.buildModelOptions()` [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:432-445]()

**Sources:** [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:234-269](), [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:373-422]()

---

## Multi-Knowledge Base Retrieval

When searching across multiple knowledge bases, the system aggregates results and re-ranks them globally:

### Aggregation and Ranking Algorithm

```mermaid
graph TB
    START["embeddingSearch(knowIds, query, topN, similarity)"]
    INIT["documents = new ArrayList()"]
    LOOP_START{"For each knowId"}
    SINGLE_SEARCH["searchResp = searchEmbedding(knowId, ...)"]
    CHECK_RESULTS{"searchResp<br/>not empty?"}
    ADD_RESULTS["documents.addAll(searchResp)"]
    
    SORT["Sort documents by score<br/>Descending order"]
    LIMIT["Take top topNumber results"]
    BUILD_DATA["Concatenate content:<br/>data.append(doc.content)"]
    RETURN["Return KnowledgeSearchResult<br/>(data, sortedDocuments)"]
    
    START --> INIT
    INIT --> LOOP_START
    LOOP_START -->|"Yes"| SINGLE_SEARCH
    SINGLE_SEARCH --> CHECK_RESULTS
    CHECK_RESULTS -->|"Yes"| ADD_RESULTS
    CHECK_RESULTS -->|"No"| LOOP_START
    ADD_RESULTS --> LOOP_START
    LOOP_START -->|"No more"| SORT
    SORT --> LIMIT
    LIMIT --> BUILD_DATA
    BUILD_DATA --> RETURN
```

**Implementation Details:**

The `embeddingSearch` method [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:196-221]() performs the following:

1. **Collection Phase**: Iterate through each knowledge base ID and collect all results.
2. **Re-ranking Phase**: Sort all collected results by score (descending) and take top N.
3. **Result Assembly**: Concatenate all content into a single string while preserving individual document metadata.

**Sources:** [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:196-221]()

---

## Metadata-Based Filtering

Vector searches use metadata filters to scope results to specific knowledge bases and documents:

### Filter Predicates

```mermaid
graph TB
    subgraph "Metadata Constants"
        KNOWLEDGE_ID["EMBED_STORE_METADATA_KNOWLEDGEID<br/>'knowledgeId'"]
        DOC_ID["EMBED_STORE_METADATA_DOCID<br/>'docId'"]
        DOC_NAME["EMBED_STORE_METADATA_DOCNAME<br/>'docName'"]
    end
    
    subgraph "Filter Construction"
        KB_FILTER["metadataKey('knowledgeId')<br/>.isEqualTo(knowId)"]
        DOC_FILTER["metadataKey('docId')<br/>.isIn(docIds)"]
    end
    
    subgraph "Use Cases"
        SEARCH["Search in KB<br/>Filter by knowledgeId"]
        DELETE_DOC["Delete Documents<br/>Filter by docId"]
        DELETE_KB["Delete KB<br/>Filter by knowledgeId"]
    end
    
    KNOWLEDGE_ID --> KB_FILTER
    DOC_ID --> DOC_FILTER
    
    KB_FILTER --> SEARCH
    DOC_FILTER --> DELETE_DOC
    KB_FILTER --> DELETE_KB
```

**Metadata Fields Stored:**
- `knowledgeId`: Links vector to source knowledge base. [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:118]()
- `docId`: Links vector to source document. [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:128]()
- `docName`: Human-readable document name. [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:133]()

**Sources:** [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:118-133](), [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:247-252]()

---

## Result Format and Structure

### KnowledgeSearchResult Class

The retrieval system returns results wrapped in a `KnowledgeSearchResult` object [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/common/vo/knowledge/KnowledgeSearchResult.java]():

| Field | Type | Description | Source |
|-------|------|-------------|--------|
| `data` | String | Concatenated content from all matching documents | [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:218]() |
| `documents` | List&lt;Map&gt; | Individual document metadata and content | [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:214]() |

**Sources:** [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:211-220]()

---

## Integration with LangChain4j QueryRouter

For advanced RAG pipelines, the system provides a `QueryRouter` that integrates with LangChain4j's retrieval abstractions:

### QueryRouter Construction

The `getQueryRouter` method [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:282-313]() builds a `DefaultQueryRouter` containing `EmbeddingStoreContentRetriever` instances for each specified knowledge base.

**Sources:** [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:282-313]()

---

## PgVectorEmbeddingStore Configuration

The vector store is initialized with specific PostgreSQL pgvector settings and cached for reuse.

### Database Connection Configuration

The system retrieves vector store credentials from `EmbedStoreConfigBean` [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/config/EmbedStoreConfigBean.java]().

Default configuration in `application-dev.yml`:
- **Host**: 127.0.0.1
- **Port**: 5432
- **Database**: vector_db
- **Table**: embeddings

**Sources:** [jeecg-boot/jeecg-module-system/jeecg-system-start/src/main/resources/application-dev.yml:245-248](), [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:373-422]()

### Dimension-Specific Tables

To prevent conflicts between embedding models with different dimensions, the system appends the dimension to the table name if it differs from the default 1536. [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:388-395]()

**Sources:** [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:388-395]()

---

## Error Handling and Edge Cases

### Missing Knowledge Base
If a knowledge base ID is invalid, the system throws a `JeecgBootException` with the message "知识库不存在". [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:170]()

### Empty Result Handling
If no matches are found, the `searchEmbedding` method returns an empty list rather than null. [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:256-269]()

**Sources:** [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:170](), [jeecg-boot/jeecg-boot-module/jeecg-boot-module-airag/src/main/java/org/jeecg/modules/airag/llm/handler/EmbeddingHandler.java:256-269]()

---

