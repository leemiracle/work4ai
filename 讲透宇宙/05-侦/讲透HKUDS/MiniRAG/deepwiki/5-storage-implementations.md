<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/MiniRAG · page 5 Storage Implementations · fetched 2026-11-09 -->

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

