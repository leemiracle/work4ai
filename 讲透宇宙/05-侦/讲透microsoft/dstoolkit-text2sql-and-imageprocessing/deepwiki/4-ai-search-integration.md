<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/dstoolkit-text2sql-and-imageprocessing · page 4 AI Search Integration · fetched 2026-10-26 -->

# AI Search Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deploy_ai_search_indexes/README.md](deploy_ai_search_indexes/README.md)
- [text_2_sql/data_dictionary/README.md](text_2_sql/data_dictionary/README.md)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/ai_search.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/ai_search.py)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/open_ai.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/open_ai.py)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/cli.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/cli.py)

</details>



This document explains how Azure AI Search is integrated as a central component in both the Text-to-SQL and Image Processing systems. Azure AI Search powers semantic retrieval, vector search capabilities, and enables efficient caching across the solution.

For details on deploying AI Search indexes, see [AI Search Index Deployment](#4.1). For information about the Text-to-SQL system, see [Text-to-SQL System](#2).

## Overview

Azure AI Search serves as a critical infrastructure component that enables:

1. Schema selection for Text-to-SQL through semantic matching of user queries to database schemas
2. Query caching to improve performance and reduce costs
3. Column value storage for entity recognition and disambiguation
4. Storage and retrieval of processed documents with semantic chunking and image analysis

```mermaid
flowchart TD
    subgraph "Azure AI Search"
        SchemaStore["Schema Store Index"]
        ColumnValueStore["Column Value Store Index"]
        QueryCache["Query Cache Index"]
        DocumentStore["Document Store Index"]
    end

    subgraph "Text2SQL System"
        T2S["AutoGenText2SQL"]
        SchemaAgent["Schema Selection Agent"]
        CacheAgent["SQL Query Cache Agent"]
        ColumnLookup["Column Value Lookup"]
    end

    subgraph "Image Processing"
        LayoutAnalysis["Layout Analysis"]
        FigureAnalysis["Figure Analysis"]
        SemanticChunker["Semantic Text Chunker"]
        MarkUpCleaner["MarkUp Cleaner"]
    end

    T2S --> SchemaAgent
    SchemaAgent --> SchemaStore
    T2S --> CacheAgent
    CacheAgent --> QueryCache
    T2S --> ColumnLookup
    ColumnLookup --> ColumnValueStore

    LayoutAnalysis --> DocumentStore
    FigureAnalysis --> DocumentStore
    SemanticChunker --> DocumentStore
    MarkUpCleaner --> DocumentStore

    User(["User"]) -- "Natural Language Query" --> T2S
    User -- "Document Upload" --> LayoutAnalysis
```

Sources:
- [deploy_ai_search_indexes/src/deploy_ai_search_indexes/ai_search.py:34-131]()
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/ai_search.py:18-33]()

## AI Search Base Class

The system uses an extensible architecture based on the abstract `AISearch` class that provides common functionality for deploying and managing AI Search indexes. This class handles:

- Index creation and updates
- Skillset deployment for processing documents
- Data source configuration
- Indexer management
- Vector search configuration

```mermaid
classDiagram
    class AISearch {
        <<abstract>>
        +String indexer_type
        +String suffix
        +Boolean rebuild
        +Boolean test
        +AISearchEnvironment environment
        +SearchIndexerClient _search_indexer_client
        +SearchIndexClient _search_index_client
        +BlobIndexerParsingMode parsing_mode
        +String indexer_name
        +String skillset_name
        +String semantic_config_name
        +String index_name
        +String data_source_name
        +String vector_search_profile_name
        +String vectorizer_name
        +String algorithm_name
        +get_index_fields()* List~SearchableField~
        +get_semantic_search() SemanticSearch
        +get_skills() List
        +get_indexer() SearchIndexer
        +get_index_projections() SearchIndexerIndexProjection
        +get_synonym_map_names() List~String~
        +get_data_source() SearchIndexerDataSourceConnection
        +get_vector_search() VectorSearch
        +deploy_index()
        +deploy_skillset()
        +deploy_data_source()
        +deploy_indexer()
        +run_indexer()
        +reset_indexer()
        +deploy_synonym_map()
        +deploy()
    }

    class SchemaStoreIndexer {
        +get_index_fields()
        +get_semantic_search()
        +get_skills()
        +get_indexer()
    }

    class ColumnValueStoreIndexer {
        +get_index_fields()
        +get_semantic_search()
        +get_skills()
        +get_indexer()
    }

    class QueryCacheIndexer {
        +get_index_fields()
        +get_semantic_search()
        +get_skills()
        +get_indexer()
    }

    class DocumentStoreIndexer {
        +get_index_fields()
        +get_semantic_search()
        +get_skills()
        +get_indexer()
        +get_mark_up_cleaner_skill()
        +get_semantic_chunker_skill()
        +get_layout_analysis_skill()
        +get_figure_analysis_skill()
        +get_layout_and_figure_merger_skill()
    }

    AISearch <|-- SchemaStoreIndexer
    AISearch <|-- ColumnValueStoreIndexer
    AISearch <|-- QueryCacheIndexer
    AISearch <|-- DocumentStoreIndexer
```

Sources:
- [deploy_ai_search_indexes/src/deploy_ai_search_indexes/ai_search.py:35-131]()
- [deploy_ai_search_indexes/src/deploy_ai_search_indexes/ai_search.py:642-750]()

## Text-to-SQL AI Search Integration

Azure AI Search powers several critical features in the Text-to-SQL system:

### Schema Selection

The Schema Selection Agent uses AI Search to find the most relevant database tables and views based on the user's natural language query. This process involves:

1. Extracting query intent from natural language
2. Sending a semantic search request to the Schema Store Index
3. Retrieving relevant database objects with their schemas
4. Selecting the appropriate schema for SQL generation

```mermaid
sequenceDiagram
    participant User as "User"
    participant SchemaAgent as "Schema Selection Agent"
    participant AISearch as "AISearchConnector"
    participant SchemaStore as "Schema Store Index"
    
    User->>SchemaAgent: Natural language query
    SchemaAgent->>AISearch: get_entity_schemas(query)
    AISearch->>AISearch: Generate embeddings
    AISearch->>SchemaStore: Vector search query
    SchemaStore-->>AISearch: Relevant schemas
    AISearch-->>SchemaAgent: Schema objects
    SchemaAgent->>SchemaAgent: Select most relevant schemas
    SchemaAgent-->>User: Selected schemas
```

Sources:
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/ai_search.py:142-232]()

### Column Value Lookups

The system uses Azure AI Search to discover column values and entities in the database that match user queries. This allows:

- Entity disambiguation
- Entity recognition
- Value validation

These lookups are performed through the `get_column_values` method in the `AISearchConnector` class.

Sources:
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/ai_search.py:107-140]()

### Query Caching

The Query Cache uses AI Search to:

1. Store previously generated SQL queries with their natural language questions
2. Match new questions to similar previously asked questions
3. Retrieve and reuse SQL queries for similar questions

This caching mechanism improves performance and reduces costs by avoiding redundant SQL generation.

Sources:
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/ai_search.py:234-282]()

## Image Processing AI Search Integration

The Image Processing system uses Azure AI Search to index and retrieve document content with rich semantic understanding and image analysis.

### Document Processing Pipeline

The document processing pipeline consists of several key components integrated with AI Search:

1. **Layout Analysis**: Extracts structure from documents using Azure Document Intelligence
2. **Figure Analysis**: Processes images and diagrams with multimodal AI
3. **Semantic Text Chunking**: Splits content into semantically meaningful chunks
4. **MarkUp Cleaning**: Prepares content for indexing

```mermaid
flowchart TB
    subgraph "Document Processing Pipeline"
        Doc["Document File"] --> LayoutAnalysis
        LayoutAnalysis --> FigureExtraction
        FigureExtraction --> FigureAnalysis
        LayoutAnalysis --> SemanticChunker
        FigureAnalysis --> Merger["Layout & Figure Merger"]
        SemanticChunker --> Merger
        Merger --> MarkUpCleaner
    end

    subgraph "AI Search"
        skill1["Layout Analysis Skill"]
        skill2["Figure Analysis Skill"] 
        skill3["Semantic Chunker Skill"]
        skill4["Mark Up Cleaner Skill"]
        skill5["Vector Skill"]
        
        DSI["Document Store Index"]
    end

    LayoutAnalysis -.-> skill1
    FigureAnalysis -.-> skill2
    SemanticChunker -.-> skill3
    MarkUpCleaner -.-> skill4
    MarkUpCleaner -.-> skill5
    
    skill1 --> DSI
    skill2 --> DSI
    skill3 --> DSI
    skill4 --> DSI
    skill5 --> DSI
```

Sources:
- [deploy_ai_search_indexes/src/deploy_ai_search_indexes/ai_search.py:199-282]()
- [deploy_ai_search_indexes/src/deploy_ai_search_indexes/ai_search.py:354-486]()
- [image_processing/src/image_processing/layout_analysis.py:143-572]()

### Semantic Text Chunking

The `SemanticTextChunker` is a key component for document processing that creates semantically meaningful chunks for optimal retrieval. It:

1. Splits text into sentences
2. Groups tables and figures together
3. Merges semantically similar chunks
4. Assigns page numbers to chunks
5. Prepares content for vector embedding

The chunking process respects document structure while creating optimal-sized chunks for retrieval.

```mermaid
flowchart LR
    Text["Raw Document Text"] --> SplitSentences["Split into Sentences"]
    SplitSentences --> GroupFigures["Group Figures & Tables"]
    GroupFigures --> ForwardMerge["Forward Pass Merging"]
    ForwardMerge --> BackwardMerge["Backward Pass Merging"]
    BackwardMerge --> AssignPages["Assign Page Numbers"]
    AssignPages --> FinalChunks["Final Semantically Coherent Chunks"]
```

Sources:
- [image_processing/src/image_processing/semantic_text_chunker.py:13-468]()
- [deploy_ai_search_indexes/src/deploy_ai_search_indexes/ai_search.py:284-352]()

## Azure AI Search Queries

The system uses several types of queries to Azure AI Search:

### Vector Search Queries

Vector search uses embeddings to find semantically similar content. This is implemented in the `run_ai_search_query` method of the `AISearchConnector` class:

1. Generate embeddings for the user query
2. Create a `VectorizableTextQuery` with appropriate fields
3. Send the query to Azure AI Search
4. Process and return the results

Vector search is particularly effective for semantic matching of questions to schemas or documents.

### Keyword Search

The system also supports traditional keyword search for exact matching, especially useful for column value lookups where fuzzy matching is needed:

```python
# Example of fuzzy search in get_column_values
text = " ".join([f"{word}~" for word in text.split()])
```

### Authentication Methods

The system supports three authentication methods for Azure AI Search:

1. **API Key**: Using `AzureKeyCredential` with an API key
2. **System-Assigned Managed Identity**: Using `DefaultAzureCredential`
3. **User-Assigned Managed Identity**: Using `DefaultAzureCredential` with a specific identity

The authentication method is determined by the `IdentityType` enum and is handled automatically.

Sources:
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/ai_search.py:22-105]()
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/open_ai.py:14-28]()

## AI Search Skillsets

Azure AI Search skillsets are used to process and enrich document content during indexing. The system uses several custom skills:

1. **Layout Analysis Skill**: Extracts document structure using Azure Document Intelligence
2. **Figure Analysis Skill**: Processes images and diagrams
3. **Semantic Chunker Skill**: Splits content into semantically meaningful chunks
4. **Mark Up Cleaner Skill**: Prepares content for indexing
5. **Vector Skill**: Generates embeddings for vector search

These skills are defined as `WebApiSkill` objects for custom skills and `AzureOpenAIEmbeddingSkill` for embedding generation.

| Skill Name | Purpose | Input | Output |
|------------|---------|-------|--------|
| Layout Analysis Skill | Extract document structure | Document source | Layout with text and figures |
| Figure Analysis Skill | Process images and diagrams | Extracted figures | Figure descriptions |
| Semantic Chunker Skill | Split content into chunks | Document content | Semantically coherent chunks |
| Mark Up Cleaner Skill | Clean and prepare content | Chunks with markup | Clean text for indexing |
| Vector Skill | Generate embeddings | Cleaned text | Vector embeddings |

Sources:
- [deploy_ai_search_indexes/src/deploy_ai_search_indexes/ai_search.py:199-596]()

## Vector Search Configuration

Azure AI Search vector search is configured through several components:

1. **Algorithm Configuration**: Configures the HNSW algorithm for approximate nearest neighbor search
2. **Vector Search Profile**: Links the algorithm and vectorizer
3. **Vectorizer**: Configures Azure OpenAI for embedding generation

```mermaid
flowchart LR
    Index["SearchIndex"] --> VS["VectorSearch"]
    VS --> Algorithms["HnswAlgorithmConfiguration"]
    VS --> Profiles["VectorSearchProfile"]
    VS --> Vectorizers["AzureOpenAIVectorizer"]
    Vectorizers --> Parameters["AzureOpenAIVectorizerParameters"]
    Parameters --> Authentication["API Key or Managed Identity"]
```

Sources:
- [deploy_ai_search_indexes/src/deploy_ai_search_indexes/ai_search.py:598-640]()

## Deployment Process

The deployment process for AI Search components follows this sequence:

1. Deploy data source connection
2. Deploy synonym maps (if any)
3. Create or update the search index
4. Deploy skillsets
5. Create or update the indexer
6. Run the indexer to start processing data

This process is encapsulated in the `deploy()` method of the `AISearch` class.

Sources:
- [deploy_ai_search_indexes/src/deploy_ai_search_indexes/ai_search.py:742-750]()

---

