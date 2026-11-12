<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/graphrag · page 7 Storage System · fetched 2026-10-26 -->

# Storage System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/graphrag-storage/COSMOS_TABLE_PROVIDER_DESIGN.md](packages/graphrag-storage/COSMOS_TABLE_PROVIDER_DESIGN.md)
- [packages/graphrag-storage/graphrag_storage/azure_cosmos_storage.py](packages/graphrag-storage/graphrag_storage/azure_cosmos_storage.py)
- [packages/graphrag-storage/graphrag_storage/tables/cosmos_table.py](packages/graphrag-storage/graphrag_storage/tables/cosmos_table.py)
- [packages/graphrag-storage/graphrag_storage/tables/cosmos_table_provider.py](packages/graphrag-storage/graphrag_storage/tables/cosmos_table_provider.py)
- [packages/graphrag-vectors/graphrag_vectors/azure_ai_search.py](packages/graphrag-vectors/graphrag_vectors/azure_ai_search.py)
- [packages/graphrag-vectors/graphrag_vectors/cosmosdb.py](packages/graphrag-vectors/graphrag_vectors/cosmosdb.py)
- [packages/graphrag-vectors/graphrag_vectors/lancedb.py](packages/graphrag-vectors/graphrag_vectors/lancedb.py)
- [packages/graphrag-vectors/graphrag_vectors/vector_store.py](packages/graphrag-vectors/graphrag_vectors/vector_store.py)

</details>



The Storage System provides a unified data persistence and retrieval layer for GraphRAG. It handles diverse data types, including pipeline artifacts (Parquet/CSV tables), vector embeddings, and intermediate processing results (caching). The system is built on an abstraction layer that allows switching between local file systems, memory, and Azure cloud services without changing application logic.

For detailed implementation specifics, see the child pages listed below.

## Storage Abstraction and Tables

At the core of the storage system is the `Storage` interface, which provides basic blob-like operations (`get`, `set`, `has`, `find`) [packages/graphrag-storage/graphrag_storage/storage.py:16-118](). Building on this, the `TableProvider` abstraction handles structured data serialization, primarily for Pandas DataFrames.

*   **`TableProvider`**: An abstract base class defining methods for reading and writing structured data [packages/graphrag-storage/graphrag_storage/tables/table_provider.py:14-103]().
*   **`ParquetTableProvider`**: The primary provider for production indexing, storing DataFrames as Parquet files for efficiency [packages/graphrag-storage/graphrag_storage/tables/parquet_table_provider.py:20-138]().
*   **`CSVTableProvider`**: A provider for human-readable exports and simpler integrations [packages/graphrag-storage/graphrag_storage/tables/csv_table_provider.py:21-140]().
*   **`CosmosTableProvider`**: A specialized implementation that stores DataFrames as native documents in Azure Cosmos DB. It eliminates Parquet serialization overhead and optimizes for single-partition performance via a `/namespace` partition key [packages/graphrag-storage/graphrag_storage/tables/cosmos_table_provider.py:48-212]().

For details on the interface and factory patterns, see **[Storage Architecture and Factory Pattern](#7.1)**.

### Table Storage Hierarchy

```mermaid
graph TD
    subgraph "DataStructures"
        DF["pd.DataFrame"]
        Row["Row Dictionary"]
    end

    subgraph "TableProviders"
        PTP["ParquetTableProvider"]
        CTP["CSVTableProvider"]
        CosTP["CosmosTableProvider"]
    end

    subgraph "StorageBackends"
        FS["FileStorage"]
        BS["BlobStorage"]
        MS["MemoryStorage"]
        CosDB["Azure Cosmos DB"]
    end

    DF --> PTP
    DF --> CTP
    DF --> CosTP
    PTP --> FS
    PTP --> BS
    CTP --> FS
    CosTP --> CosDB
    
    Sources: [packages/graphrag-storage/graphrag_storage/tables/parquet_table_provider.py:21-37](), [packages/graphrag-storage/graphrag_storage/tables/csv_table_provider.py:28-42](), [packages/graphrag-storage/graphrag_storage/tables/cosmos_table_provider.py:48-55]()
```

## Vector Store System

The Vector Store system provides specialized storage for high-dimensional embeddings generated during the indexing process. It supports similarity searches, metadata filtering, and document management.

*   **`VectorStore`**: The base abstract class defining the contract for all vector databases, including `similarity_search_by_vector` and `load_documents` [packages/graphrag-vectors/graphrag_vectors/vector_store.py:56-213]().
*   **Filtering**: A robust expression system (`FilterExpr`, `Condition`, `AndExpr`) allows for complex metadata filtering during retrieval [packages/graphrag-vectors/graphrag_vectors/vector_store.py:152-157]().

For the base architecture and search operations, see **[Vector Store Architecture](#7.4)**.

### Vector Store Implementations

GraphRAG supports multiple vector database backends:

| Implementation | Description | Use Case |
|----------------|-------------|----------|
| **LanceDB** | Serverless, disk-based vector store using Ivory/Lance format [packages/graphrag-vectors/graphrag_vectors/lancedb.py:27-117](). | Local development and high-performance local indexing. |
| **Azure AI Search** | Managed cloud search service with integrated vector capabilities [packages/graphrag-vectors/graphrag_vectors/azure_ai_search.py:48-188](). | Enterprise-grade cloud deployments. |
| **Cosmos DB** | Azure NoSQL database using DiskANN for vector indexing [packages/graphrag-vectors/graphrag_vectors/cosmosdb.py:28-186](). | Integrated data and vector storage in Azure. |

For implementation details, see **[LanceDB Vector Store](#7.5)**, **[Azure AI Search Vector Store](#7.6)**, and **[Cosmos DB Vector Store](#7.7)**.

## Mapping Code Entities to Storage Concepts

The following diagram bridges the gap between the storage abstractions used in the code and the physical storage types.

```mermaid
graph LR
    subgraph "NaturalLanguageSpace"
        Input["'input' storage"]
        Output["'output' storage"]
        VIndex["'vector_index'"]
        KVCache["'cache' storage"]
    end

    subgraph "CodeEntitySpace"
        StorageClass["Storage (ABC)"]
        TableProviderClass["TableProvider (ABC)"]
        VectorStoreClass["VectorStore (ABC)"]
        
        FileImpl["FileStorage"]
        ParquetImpl["ParquetTableProvider"]
        LanceImpl["LanceDBVectorStore"]
        CosmosKV["AzureCosmosStorage"]
    end

    Input -- "uses" --> FileImpl
    Output -- "managed by" --> ParquetImpl
    VIndex -- "implemented via" --> LanceImpl
    KVCache -- "stored in" --> CosmosKV
    
    FileImpl -- "implements" --> StorageClass
    ParquetImpl -- "implements" --> TableProviderClass
    LanceImpl -- "implements" --> VectorStoreClass
    CosmosKV -- "implements" --> StorageClass

    Sources: [packages/graphrag-storage/graphrag_storage/tables/parquet_table_provider.py:20-25](), [packages/graphrag-vectors/graphrag_vectors/lancedb.py:27-32](), [packages/graphrag-storage/graphrag_storage/tables/table_provider.py:14-16](), [packages/graphrag-storage/graphrag_storage/azure_cosmos_storage.py:34-43]()
```

## Cache and Resilience

To minimize LLM costs and improve pipeline resilience, GraphRAG includes a caching system. This system stores the results of expensive operations (like LLM completions and embedding generations) using the same underlying `Storage` abstractions. For example, `AzureCosmosStorage` provides a key-value store specifically for non-tabular data like LLM cache entries and pipeline state [packages/graphrag-storage/graphrag_storage/azure_cosmos_storage.py:4-11]().

For more information on the caching mechanisms, see **[Cache System](#7.8)**.

## Summary of Child Pages

*   **[Storage Architecture and Factory Pattern](#7.1)**: Deep dive into the `Storage` interface and how the system dynamically instantiates providers.
*   **[File and Memory Storage](#7.2)**: Details on local filesystem and transient in-memory storage.
*   **[Azure Storage Integration](#7.3)**: Documentation for Azure Blob Storage and the `CosmosTableProvider` for high-performance tabular storage in Cosmos DB.
*   **[Vector Store Architecture](#7.4)**: Explanation of the vector search API and the filtering engine.
*   **[LanceDB Vector Store](#7.5)**: Configuration and usage of the LanceDB backend.
*   **[Azure AI Search Vector Store](#7.6)**: Integration with Azure's managed search service.
*   **[Cosmos DB Vector Store](#7.7)**: Utilizing Cosmos DB's vector search features with DiskANN.
*   **[Cache System](#7.8)**: How GraphRAG caches LLM responses to optimize performance and cost.

---

