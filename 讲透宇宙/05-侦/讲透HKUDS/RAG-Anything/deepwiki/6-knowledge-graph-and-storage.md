<!-- source: DeepWiki mcp.deepwiki.com · repo HKUDS/RAG-Anything · page 6 Knowledge Graph and Storage · fetched 2026-11-09 -->

# Knowledge Graph and Storage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [env.example](env.example)
- [examples/lmstudio_integration_example.py](examples/lmstudio_integration_example.py)
- [raganything/processor.py](raganything/processor.py)
- [tests/test_insert_content_list.py](tests/test_insert_content_list.py)

</details>



## Purpose and Scope

This page documents the knowledge graph construction and storage architecture in RAG-Anything. It covers how entities and relationships are extracted from both text and multimodal content, the dual-layer entity system with `belongs_to` relationships, and the multi-storage backend architecture.

For information about how multimodal content is processed before entering the knowledge graph, see [Multimodal Content Processing](#5). For query-time retrieval from the knowledge graph, see [Query System](#7).

---

## Knowledge Graph Architecture

RAG-Anything constructs a hierarchical knowledge graph that integrates both text-based entities and multimodal entities (images, tables, equations) into a unified structure.

### Dual-Layer Entity System

```mermaid
graph TB
    subgraph "Document Processing"
        Doc["Document content_list"]
        TextContent["Text Content"]
        MMContent["Multimodal Content<br/>(image, table, equation)"]
    end
    
    subgraph "Entity Layer 1: Main Modal Entities"
        ImgEntity["Image Entity<br/>'Figure_Analysis (image)'"]
        TblEntity["Table Entity<br/>'Performance_Table (table)'"]
        EqEntity["Equation Entity<br/>'Einstein_Equation (equation)'"]
    end
    
    subgraph "Entity Layer 2: Extracted Entities"
        TextEntity1["Text Entity<br/>'Neural Networks'"]
        TextEntity2["Text Entity<br/>'Accuracy'"]
        ImgExtracted["Extracted from Image<br/>'ResNet Architecture'"]
        TblExtracted["Extracted from Table<br/>'F1 Score'"]
        EqExtracted["Extracted from Equation<br/>'Mass-Energy Equivalence'"]
    end
    
    subgraph "Knowledge Graph (chunk_entity_relation_graph)"
        KG["NetworkX Graph<br/>Nodes: All Entities<br/>Edges: Relationships"]
    end
    
    Doc --> TextContent
    Doc --> MMContent
    
    TextContent --> TextEntity1
    TextContent --> TextEntity2
    
    MMContent --> ImgEntity
    MMContent --> TblEntity
    MMContent --> EqEntity
    
    ImgEntity -->|"extract_entities"| ImgExtracted
    TblEntity -->|"extract_entities"| TblExtracted
    EqEntity -->|"extract_entities"| EqExtracted
    
    ImgExtracted -.->|"belongs_to (weight=10)"| ImgEntity
    TblExtracted -.->|"belongs_to (weight=10)"| TblEntity
    EqExtracted -.->|"belongs_to (weight=10)"| EqEntity
    
    TextEntity1 --> KG
    TextEntity2 --> KG
    ImgEntity --> KG
    TblEntity --> KG
    EqEntity --> KG
    ImgExtracted --> KG
    TblExtracted --> KG
    EqExtracted --> KG
```

**Sources:** `ProcessorMixin` in [raganything/processor.py:32-33](), multimodal extraction logic in [raganything/processor.py:1205-1267](), and `BaseModalProcessor` logic in [raganything/modalprocessors.py:326-335]().

The system creates two layers of entities:

1. **Main Modal Entities** (Layer 1): Represent entire multimodal objects. These are created directly from parsed content (images, tables, equations) and named with the format: `"{descriptive_name} ({type})"`, e.g., `"Performance_Comparison (table)"`.
2. **Extracted Entities** (Layer 2): Domain-specific entities extracted via LLM analysis from both text chunks and modal content chunks. These are connected to their source modal entities via `"belongs_to"` relationships.

### Entity Creation Flow

```mermaid
flowchart TD
    subgraph "Stage 1: Modal Description Generation"
        MM["Multimodal Item"]
        Processor["Modal Processor<br/>(ImageModalProcessor,<br/>TableModalProcessor,<br/>EquationModalProcessor)"]
        Desc["generate_description_only()"]
        LLM["LLM/VLM Analysis"]
        EntityInfo["entity_info:<br/>{entity_name, entity_type, summary}"]
    end
    
    subgraph "Stage 2: Chunk & Main Entity Creation"
        ChunkTemplate["_apply_chunk_template()<br/>Format with prompt template"]
        ChunkContent["Formatted Chunk Content"]
        ChunkID["compute_mdhash_id()<br/>Generate chunk_id"]
        StoreChunk["Store to text_chunks<br/>& chunks_vdb"]
        MainEntityNode["Create Main Entity Node<br/>in chunk_entity_relation_graph"]
        EntityVDB["Store to entities_vdb"]
        FullEntities["Store to full_entities"]
    end
    
    subgraph "Stage 3: Entity Extraction"
        ExtractCall["extract_entities()<br/>(from LightRAG)"]
        ChunkResults["chunk_results:<br/>List[(maybe_nodes, maybe_edges)]"]
        ExtractedEnts["Extracted Entities<br/>from LLM analysis"]
    end
    
    subgraph "Stage 4: belongs_to Relations"
        BelongsToLogic["_batch_add_belongs_to_relations()"]
        BelongsToEdge["Create Edge:<br/>extracted_entity -> main_modal_entity<br/>weight=10.0, keywords='belongs_to'"]
        RelVDB["Store to relationships_vdb"]
    end
    
    subgraph "Stage 5: Graph Merge"
        MergeCall["merge_nodes_and_edges()"]
        FinalKG["chunk_entity_relation_graph<br/>Updated with all entities & relations"]
    end
    
    MM --> Processor
    Processor --> Desc
    Desc --> LLM
    LLM --> EntityInfo
    
    EntityInfo --> ChunkTemplate
    ChunkTemplate --> ChunkContent
    ChunkContent --> ChunkID
    ChunkID --> StoreChunk
    EntityInfo --> MainEntityNode
    MainEntityNode --> EntityVDB
    MainEntityNode --> FullEntities
    
    StoreChunk --> ExtractCall
    ExtractCall --> ChunkResults
    ChunkResults --> ExtractedEnts
    
    ExtractedEnts --> BelongsToLogic
    MainEntityNode --> BelongsToLogic
    BelongsToLogic --> BelongsToEdge
    BelongsToEdge --> RelVDB
    
    ChunkResults --> MergeCall
    BelongsToEdge --> MergeCall
    MergeCall --> FinalKG
```

**Sources:** `_process_multimodal_content` flow in [raganything/processor.py:706-881](), `_batch_add_belongs_to_relations` in [raganything/processor.py:1205-1267](), and modal processor description logic in [raganything/modalprocessors.py:465-545]().

---

## Entity Types and Naming

### Main Modal Entity Naming Convention

Main modal entities follow a consistent naming pattern that includes both a descriptive name and the content type: `{entity_name} ({entity_type})`. This naming convention is enforced in the modal processor response parsing.

**Sources:** `_parse_response` in [raganything/modalprocessors.py:1011-1013](), `_parse_table_response` in [raganything/modalprocessors.py:1205-1207](), and `_parse_equation_response` in [raganything/modalprocessors.py:1389-1391]().

### Entity Data Structure

Each entity stored in the knowledge graph contains metadata such as `entity_id`, `entity_type`, `description`, `source_id`, and `file_path`.

**Sources:** Entity structure in [raganything/modalprocessors.py:505-513]() and [raganything/processor.py:1084-1092]().

---

## Relationship Types

### Standard Entity Relationships

Standard relationships are extracted by LightRAG's `extract_entities()` function from chunk content. These capture semantic relationships between entities mentioned in the text.

**Sources:** [raganything/processor.py:1176-1203](), [raganything/modalprocessors.py:727-734]().

### belongs_to Relationships

The `"belongs_to"` relationship is unique to RAG-Anything's multimodal processing. It creates hierarchical connections from extracted entities to their source modal entities.

```mermaid
graph LR
    subgraph "Example: Table Processing"
        TblChunk["Table Chunk:<br/>'Performance_Table (table)'<br/>Contains accuracy metrics..."]
        
        ExtEntity1["Extracted Entity:<br/>'F1 Score'"]
        ExtEntity2["Extracted Entity:<br/>'Precision'"]
        ExtEntity3["Extracted Entity:<br/>'Recall'"]
        
        MainEntity["Main Modal Entity:<br/>'Model_Performance_Table (table)'"]
    end
    
    TblChunk -.->|"extract_entities()"| ExtEntity1
    TblChunk -.->|"extract_entities()"| ExtEntity2
    TblChunk -.->|"extract_entities()"| ExtEntity3
    
    ExtEntity1 -->|"belongs_to<br/>weight=10.0"| MainEntity
    ExtEntity2 -->|"belongs_to<br/>weight=10.0"| MainEntity
    ExtEntity3 -->|"belongs_to<br/>weight=10.0"| MainEntity
```

**Sources:** `_batch_add_belongs_to_relations` in [raganything/processor.py:1205-1267]() and [raganything/modalprocessors.py:738-770]().

---

## Storage Architecture

RAG-Anything uses a multi-storage architecture inherited from LightRAG, with distinct storage systems working together.

### Storage System Overview

```mermaid
graph TB
    subgraph "Storage Backends"
        TextChunks["text_chunks<br/>(KV Storage)<br/>Raw chunk content"]
        ChunksVDB["chunks_vdb<br/>(Vector DB)<br/>Chunk embeddings"]
        EntitiesVDB["entities_vdb<br/>(Vector DB)<br/>Entity embeddings"]
        RelationsVDB["relationships_vdb<br/>(Vector DB)<br/>Relation embeddings"]
        KG["chunk_entity_relation_graph<br/>(Graph Storage)<br/>NetworkX or Neo4j/AGE"]
        FullEntities["full_entities<br/>(KV Storage)<br/>Doc-level entity list"]
        FullRelations["full_relations<br/>(KV Storage)<br/>Doc-level relation list"]
        DocStatus["doc_status<br/>(KV Storage)<br/>Processing status"]
        ParseCache["parse_cache<br/>(KV Storage)<br/>Parsed content cache"]
    end
    
    subgraph "Data Types"
        Chunks["Chunks"]
        Entities["Entities"]
        Relations["Relationships"]
        Status["Metadata"]
    end
    
    Chunks --> TextChunks
    Chunks --> ChunksVDB
    
    Entities --> EntitiesVDB
    Entities --> KG
    Entities --> FullEntities
    
    Relations --> RelationsVDB
    Relations --> KG
    Relations --> FullRelations
    
    Status --> DocStatus
    Status --> ParseCache
```

**Sources:** `lightrag` storage access in [raganything/processor.py:1006-1022](), [raganything/processor.py:1099-1101](), and [raganything/modalprocessors.py:380-384]().

### Key Storage Components

- **text_chunks (KV Storage)**: Stores raw chunk content and multimodal flags [raganything/processor.py:911-924]().
- **chunks_vdb / entities_vdb / relationships_vdb**: Vector databases for semantic retrieval [raganything/processor.py:1015](), [raganything/processor.py:1099-1101]().
- **chunk_entity_relation_graph**: Graph storage for entity-relationship structure [raganything/processor.py:1095-1097]().
- **doc_status**: Tracks document processing state, including the `multimodal_processed` flag [raganything/processor.py:138-159](), [raganything/processor.py:189-200]().
- **parse_cache**: Caches parsed document results using a generated `cache_key` [raganything/processor.py:50-98](), [raganything/processor.py:212-278]().

---

## Storage Backend Options

RAG-Anything supports multiple storage backends configured via environment variables or `RAGAnythingConfig`.

| Storage Type | Options |
|--------------|---------|
| **KV Storage** | `JsonKVStorage`, `PGKVStorage`, `MongoDBStorage`, `RedisStorage` |
| **Vector DB** | `NanoVectorDBStorage`, `PGVectorStorage`, `MilvusVectorStorage`, `QdrantVectorStorage` |
| **Graph DB** | `NetworkXStorage`, `Neo4jStorage`, `AGEStorage`, `MongoDBGraphStorage` |

**Sources:** `env.example:152-212]()` and `RAGAnythingConfig` parameters.

For details, see [Storage Architecture](#6.2) and [Storage Backend Configuration](#8.3).

---

