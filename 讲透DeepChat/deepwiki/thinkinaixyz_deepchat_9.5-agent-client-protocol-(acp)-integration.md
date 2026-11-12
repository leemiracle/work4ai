> 来源: [https://deepwiki.com/thinkinaixyz/deepchat/8.5-agent-client-protocol-(acp)-integration](https://deepwiki.com/thinkinaixyz/deepchat/8.5-agent-client-protocol-(acp)-integration)（Wayback 快照 2026-03-06）
> DeepWiki deepchat/8.5-agent-client-protocol-(acp)-integration

# Similarity Search and Querying

  Relevant source files 
 - [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts)
 - [src/main/presenter/knowledgePresenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/knowledgePresenter/index.ts)
 - [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts)
 - [src/main/presenter/knowledgePresenter/knowledgeTaskPresenter.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/knowledgePresenter/knowledgeTaskPresenter.ts)
 - [src/main/utils/vector.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/utils/vector.ts)
 - [src/shared/dialog.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/shared/dialog.ts)
 
  
## Purpose and Scope

 This document describes the similarity search and querying system used to retrieve relevant information from knowledge bases. It covers the complete flow from query input to ranked results, including embedding generation, vector similarity search using DuckDB with HNSW indexing, distance metric selection, and confidence score normalization.

 For information about the overall knowledge base architecture and file processing, see [Knowledge Base Architecture](https://deepwiki.com/thinkinaixyz/deepchat/8.1-knowledge-base-architecture). For details about vector database schema and indexing, see [Vector Database and DuckDB](https://deepwiki.com/thinkinaixyz/deepchat/8.3-vector-database-and-duckdb).

 
---

 
## Query Flow Overview

 The similarity search process follows a multi-stage pipeline that transforms a text query into ranked results:

 
```

```

 **Sources:** [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts340-360](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L340-L360) [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts397-435](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts#L397-L435)

 
---

 
## Entry Point and Query Orchestration

 The `KnowledgePresenter` provides the top-level interface for similarity queries across all knowledge bases. The `similarityQuery` method delegates to the appropriate `KnowledgeStorePresenter` instance:

 
| Component | Responsibility |
|---|---|
| KnowledgePresenter.similarityQuery | Routes query to correct knowledge base |
| KnowledgeStorePresenter.similarityQuery | Manages query flow for single knowledge base |
| DuckDBPresenter.similarityQuery | Executes vector search against database |

 The query is identified by the knowledge base `id` and the search `key` (query text):

 
```

```

 **Sources:** [src/main/presenter/knowledgePresenter/index.ts349-352](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/knowledgePresenter/index.ts#L349-L352) [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts21-47](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L21-L47)

 
---

 
## Embedding Generation

 Before performing vector similarity search, the query text must be converted to an embedding vector using the same embedding model configured for the knowledge base.

 
### Text Sanitization

 Query text is sanitized using `sanitizeText` to remove problematic characters and normalize whitespace before embedding generation:

 
```

```

 
### Embedding Model Selection

 The embedding model is specified in the knowledge base configuration (`BuiltinKnowledgeConfig`) and consists of:

 
| Field | Description |
|---|---|
| embedding.providerId | LLM provider identifier (e.g., "openai") |
| embedding.modelId | Model identifier (e.g., "text-embedding-3-small") |
| dimensions | Expected vector dimensions |
| normalized | Whether embeddings are L2-normalized |

 The `LLMProviderPresenter.getEmbeddings` method generates the embedding vector:

 
```
embedding = await presenter.llmproviderPresenter.getEmbeddings(
  this.config.embedding.providerId,
  this.config.embedding.modelId,
  [sanitizeText(key)]
)
```

 **Sources:** [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts340-346](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L340-L346) [src/main/utils/strings.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/utils/strings.ts)

 
---

 
## Vector Similarity Search with DuckDB

 The core similarity search is performed by `DuckDBPresenter.similarityQuery`, which executes a SQL query against the vector table using HNSW indexing.

 
### Distance Function Selection

 DuckDB provides three distance functions, selected based on the `metric` parameter:

 
| Metric | Distance Function | Use Case |
|---|---|---|
| cosine | array_cosine_distance | Normalized vectors (L2 norm = 1) |
| ip | array_negative_inner_product | Non-normalized vectors |
| l2sq | array_distance | Euclidean distance (default) |

 The metric is determined by the `getMetric` utility function based on whether the knowledge base uses normalized embeddings:

 
```

```

 
### SQL Query Construction

 The similarity query SQL joins three tables to retrieve complete results:

 
```

```

 The SQL template (simplified):

 
```

```

 **Sources:** [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts397-435](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts#L397-L435) [src/main/utils/vector.ts96-102](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/utils/vector.ts#L96-L102)

 
---

 
## Query Options and Parameters

 The `QueryOptions` interface controls the search behavior:

 
| Option | Type | Description |
|---|---|---|
| topK | number | Maximum number of results to return |
| metric | MetricType | Distance metric ('cosine', 'ip', 'l2sq') |
| threshold | number? | Optional distance threshold for filtering |

 
### TopK Configuration

 The `topK` parameter is configured per knowledge base as `fragmentsNumber` and defaults to a reasonable limit to prevent overwhelming results:

 
```

```

 
### HNSW Index Parameters

 The HNSW index created during table initialization uses these parameters:

 
| Parameter | Default | Description |
|---|---|---|
| metric | 'cosine' | Distance metric for index |
| M | 16 | Maximum number of connections per layer |
| ef_construction | 200 | Size of dynamic candidate list during construction |

 **Sources:** [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts759-799](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts#L759-L799) [src/shared/presenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/shared/presenter/index.ts)

 
---

 
## Distance Normalization to Confidence Scores

 Raw distance values from DuckDB have different ranges and semantics depending on the metric. The `normalizeDistance` function converts these to intuitive confidence scores in the range [0, 1], where higher values indicate greater similarity.

 
### Normalization Algorithms

 
```

```

 
### Cosine Distance Normalization

 For normalized embeddings using cosine distance:

 
```
confidence = 1 - clamp(distance, 0, 1)
```

 
 - `distance = 0` → `confidence = 1` (identical vectors)
 - `distance = 1` → `confidence = 0` (orthogonal vectors)
 
 
### Inner Product Normalization

 For non-normalized embeddings using inner product:

 
```
sigmoid = 1 / (1 + exp(sign(distance) × distance² × k))
confidence = sigmoid
```

 Where `k = 0.04` is a scaling factor that controls the steepness of the sigmoid curve:

 
| Distance | Interpretation | Confidence (approx) |
|---|---|---|
| < 0 | Vectors point in similar direction | > 0.5 |
| = 0 | Vectors are orthogonal | ≈ 0.5 |
| > 0 | Vectors point in opposite directions | < 0.5 |

 The sigmoid transformation ensures smooth mapping and handles the unbounded nature of inner product distances.

 **Sources:** [src/main/utils/vector.ts66-93](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/utils/vector.ts#L66-L93) [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts352-354](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L352-L354)

 
---

 
## QueryResult Structure

 The `QueryResult` interface defines the structure of returned search results:

 
```

```

 
### Result Ranking

 Results are automatically ranked by similarity:

 
 - **Database-level ordering**: DuckDB returns results ordered by ascending distance (most similar first)
 - **Confidence normalization**: Distances are normalized to confidence scores where higher = more similar
 - **TopK limiting**: Only the top K results are returned based on `fragmentsNumber` configuration
 
 
```

```

 
### Metadata Enrichment

 The query joins with the `chunk` and `file` tables to enrich results with contextual metadata:

 
| Metadata Field | Source Table | Purpose |
|---|---|---|
| content | chunk.content | The actual text chunk that matched |
| from | file.name | Filename for display and reference |
| filePath | file.path | Full path for navigation and deduplication |

 **Sources:** [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts422-430](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts#L422-L430) [src/shared/presenter/index.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/shared/presenter/index.ts)

 
---

 
## Code Entity Mapping

 The following diagram maps the natural language concepts to their code implementations:

 
```

```

 **Sources:** [src/main/presenter/knowledgePresenter/index.ts349-352](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/knowledgePresenter/index.ts#L349-L352) [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts340-360](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L340-L360) [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts397-435](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts#L397-L435) [src/main/utils/vector.ts](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/utils/vector.ts)

 
---

 
## Error Handling

 The similarity query flow includes error handling at multiple levels:

 
| Layer | Error Type | Handling Strategy |
|---|---|---|
| KnowledgeStorePresenter | Embedding generation failure | Throws error with descriptive message |
| KnowledgeStorePresenter | Database query failure | Logs error and re-throws |
| DuckDBPresenter | SQL execution error | Logs SQL + parameters, throws error |
| DuckDBPresenter | Connection failure | Auto-reconnection attempted |

 
```

```

 **Sources:** [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts356-359](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L356-L359) [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts431-434](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts#L431-L434)

 
---

 
## Performance Considerations

 
### HNSW Index Efficiency

 The HNSW (Hierarchical Navigable Small World) index provides approximate nearest neighbor search with the following characteristics:

 
| Aspect | Value | Trade-off |
|---|---|---|
| Search complexity | O(log N) | Logarithmic with dataset size |
| Accuracy | ~99% (typical) | Trade recall for speed |
| Memory overhead | ~M × dimensions × 4 bytes per vector | Higher M = more memory but better recall |

 
### Query Optimization

 The system optimizes query performance through:

 
 - **Index-only scans**: The HNSW index allows direct distance computation without scanning all vectors
 - **Lazy metadata joins**: File and chunk metadata are joined only for the top-K results
 - **Result limiting**: The `LIMIT` clause prevents unnecessary result processing
 - **Connection pooling**: Single connection per knowledge base reduces overhead
 
 
### Recommended TopK Values

 
| Use Case | Recommended TopK | Rationale |
|---|---|---|
| Chat context | 3-5 fragments | Balance relevance and context window |
| Document search | 10-20 fragments | Provide diverse results |
| Exact match | 1-3 fragments | Find most similar content |

 **Sources:** [src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts759-799](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/knowledgePresenter/database/duckdbPresenter.ts#L759-L799) [src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts340-360](https://github.com/thinkinaixyz/deepchat/blob/b918a24b/src/main/presenter/knowledgePresenter/knowledgeStorePresenter.ts#L340-L360)
