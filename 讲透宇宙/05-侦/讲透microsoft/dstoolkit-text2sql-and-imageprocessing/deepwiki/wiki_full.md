# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [README.md](README.md)
- [deploy_ai_search_indexes/pyproject.toml](deploy_ai_search_indexes/pyproject.toml)
- [image_processing/pyproject.toml](image_processing/pyproject.toml)
- [pyproject.toml](pyproject.toml)
- [text_2_sql/GETTING_STARTED.md](text_2_sql/GETTING_STARTED.md)
- [text_2_sql/README.md](text_2_sql/README.md)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/postgres_sql.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/postgres_sql.py)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/postgres_data_dictionary_creator.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/postgres_data_dictionary_creator.py)

</details>



The DSToolkit Text2SQL and Image Processing repository provides accelerator components designed to enhance Retrieval-Augmented Generation (RAG) applications by enabling access to structured data sources and improving document processing capabilities. This repository contains two primary systems that can be integrated into new or existing RAG applications:

1. **Text-to-SQL System**: A sophisticated multi-agent system that converts natural language questions into SQL queries, allowing RAG applications to retrieve information from structured databases in real-time.

2. **Image Processing System**: A document processing pipeline that enhances RAG applications by extracting meaning from documents containing images, charts, and complex layouts.

This overview provides a high-level understanding of these systems and how they work together. For detailed setup instructions, see [Setup and Deployment Guide](#5).

## Repository Structure and Components

```mermaid
graph TD
    subgraph "Repository Components"
        T2S["Text-to-SQL System"] 
        IP["Image Processing System"]
        AISInt["AI Search Indexes"]
    end
    
    User([User]) --> |"Question"| T2S
    User --> |"Document"| IP
    
    T2S --> |"SQL Query"| DB[(Databases)]
    DB --> |"Results"| T2S
    IP --> |"Process"| Docs[(Documents)]
    
    T2S --> AISInt
    IP --> AISInt
    
    AISInt --> RAG["RAG Application"]
    RAG --> |"Answer"| User
```

The repository consists of these main components:

* **Text-to-SQL System** (`/text_2_sql`): Converts natural language questions into SQL queries using a multi-agent architecture. 

* **Image Processing System** (`/image_processing`): Processes documents with complex layouts, images, and charts using Azure Document Intelligence and multimodal models.

* **AI Search Integration** (`/deploy_ai_search_indexes`): Utilities for deploying Azure AI Search indexes for both systems, enabling efficient storage and retrieval of metadata, cached queries, and processed document content.

Sources: [README.md:1-17](), [text_2_sql/README.md:1-21](), [image_processing/pyproject.toml:1-51]()

## Text-to-SQL System Architecture

The Text-to-SQL system uses an agentic approach with multiple specialized components that work together to convert natural language questions into SQL queries and execute them against various database engines.

```mermaid
graph TD
    UserQ["User Question"] --> AutoGenText2Sql["AutoGenText2Sql"]
    
    subgraph "Agentic Pipeline"
        RewriteAgent["User Message Rewrite Agent"]
        QueryCacheAgent["SQL Query Cache Agent"]
        SchemaAgent["Schema Selection Agent"]
        SQLGenAgent["SQL Query Generation Agent"]
        CorrectionAgent["SQL Query Correction Agent"]
        AnswerAgent["Answer Agent"]
        
        AutoGenText2Sql --> RewriteAgent
        RewriteAgent --> QueryCacheAgent
        QueryCacheAgent -->|"cache miss"| SchemaAgent
        SchemaAgent --> SQLGenAgent
        SQLGenAgent --> CorrectionAgent
        CorrectionAgent --> AnswerAgent
        AnswerAgent --> Response["Response to User"]
    end
    
    subgraph "Database Connectors"
        ConnectorFactory["ConnectorFactory"] 
        TsqlConnector["TsqlConnector"]
        SnowflakeConnector["SnowflakeConnector"]
        DatabricksConnector["DatabricksConnector"]
        PostgresConnector["PostgresConnector"] 
        SQLiteConnector["SQLiteConnector"]
        
        ConnectorFactory --> TsqlConnector
        ConnectorFactory --> SnowflakeConnector
        ConnectorFactory --> DatabricksConnector
        ConnectorFactory --> PostgresConnector
        ConnectorFactory --> SQLiteConnector
    end
    
    subgraph "Storage Components"
        SchemaStore["SchemaStore"]
        QueryCache["QueryCache"]
        ColumnStore["ColumnValueStore"]
        StateStore["StateStore"]
    end
    
    AutoGenText2Sql --> ConnectorFactory
    AutoGenText2Sql --> StateStore
    
    SchemaAgent <--> SchemaStore
    QueryCacheAgent <--> QueryCache
    SchemaAgent <--> ColumnStore
    SQLGenAgent --> ConnectorFactory
    CorrectionAgent --> ConnectorFactory
```

Sources: [text_2_sql/README.md:37-49](), [text_2_sql/autogen/README.md:58-67]()

### Agent Types and Responsibilities

The Text-to-SQL system consists of the following specialized agents:

1. **Query Rewrite Agent**: Preprocesses questions by resolving relative dates (e.g., "last month" → "November 2024") and decomposing complex questions into simpler sub-questions.

2. **SQL Query Cache Agent**: Checks for previously asked similar questions in the cache to avoid redundant query generation.

3. **Schema Selection Agent**: Extracts key terms from the question and identifies relevant database schemas needed to answer it.

4. **SQL Disambiguation Agent**: Clarifies ambiguities in schema selection and ensures correct tables and columns are selected.

5. **SQL Query Generation Agent**: Generates SQL queries using the selected schemas to answer the question.

6. **SQL Query Correction Agent**: Verifies and corrects generated SQL queries, ensuring syntactic correctness and executing them against the database.

7. **Answer and Sources Agent**: Formats the final response with standardized output, formatted query results, and combined sources.

Sources: [text_2_sql/autogen/README.md:15-63](), [text_2_sql/README.md:58-69]()

### Data Dictionary and Schema Management

The Text-to-SQL system uses a data dictionary to provide metadata about database schemas to guide the LLM in generating accurate SQL queries.

```mermaid
graph TD
    subgraph "Data Dictionary Creation"
        DataDictionaryCreator["DataDictionaryCreator (abstract)"] 
        TsqlCreator["TsqlDataDictionaryCreator"]
        PostgresCreator["PostgresDataDictionaryCreator"]
        SnowflakeCreator["SnowflakeDataDictionaryCreator"]
        DatabricksCreator["DatabricksDataDictionaryCreator"]
        
        DataDictionaryCreator --> TsqlCreator
        DataDictionaryCreator --> PostgresCreator
        DataDictionaryCreator --> SnowflakeCreator
        DataDictionaryCreator --> DatabricksCreator
        
        TsqlCreator --> |"Extract Schema"| Database[(Database)]
        PostgresCreator --> |"Extract Schema"| Database
        
        TsqlCreator --> |"Generate"| EntitiesJSON["entities.json"]
    end
    
    subgraph "AI Search Indexing"
        EntitiesJSON --> SchemaIndexer["Schema Store Indexer"]
        EntitiesJSON --> ColumnIndexer["Column Value Store Indexer"]
        
        SchemaIndexer --> SchemaIndex["Schema Store Index"]
        ColumnIndexer --> ColumnIndex["Column Value Store Index"]
    end
    
    subgraph "Text2SQL Usage"
        SchemaAgent["Schema Selection Agent"] --> SchemaIndex
        SQLGenAgent["SQL Generation Agent"] --> SchemaIndex
        SQLGenAgent --> ColumnIndex
    end
```

The data dictionary (`entities.json`) includes:
- `Entity`: Fully qualified table/view name (e.g., "SalesLT.SalesOrderDetail")
- `Definition`: Detailed description of the entity's purpose and content
- `EntityName`: User-friendly name
- `Columns`: Array of column metadata (name, data type, definition, sample values)
- `EntityRelationships`: Foreign key relationships to other entities
- `CompleteEntityRelationshipsGraph`: Relationship paths for complex joins

Database-specific creator classes (`TsqlDataDictionaryCreator`, `PostgresDataDictionaryCreator`, etc.) generate this metadata automatically using SQL queries tailored to each database engine.

Sources: [text_2_sql/README.md:134-204](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/postgres_data_dictionary_creator.py:14-120]()

### Query Cache System

The query cache improves performance by storing previously asked questions and their corresponding SQL queries. When a user asks a similar question, the system can retrieve the cached query, potentially bypassing schema selection and query generation.

```mermaid
graph TD
    subgraph "Query Cache Management"
        Question["User Question"] --> Rewrite["Query Rewrite"]
        Rewrite --> CacheSearch["Cache Search"]
        CacheSearch --> |"Cache Hit"| ExecuteQuery["Execute Query"]
        CacheSearch --> |"Cache Miss"| GenerateSQL["Generate SQL"]
        GenerateSQL --> ExecuteQuery
        ExecuteQuery --> Answer["Generate Answer"]
        GenerateSQL --> UpdateCache["Update Cache"]
    end
    
    subgraph "Azure AI Search"
        UpdateCache --> CacheIndex["Query Cache Index"]
    end
```

Key features of the query cache:
- Stores questions and corresponding SQL queries, not results (to ensure real-time data)
- Significantly improves response time for similar questions
- Supports multiple caching strategies (pre-population, always update, positive indication)
- Preserves row and column level security by executing queries at runtime

Sources: [text_2_sql/README.md:41-82](), [text_2_sql/autogen/README.md:140-156]()

### Database Connectors

The Text-to-SQL system supports multiple database engines through a connector factory pattern:

| Database Engine | Connector Class | Key Methods |
|-----------------|----------------|-------------|
| Microsoft TSQL | `TsqlConnector` | `query_execution`, `get_entity_schemas` |
| PostgreSQL | `PostgresSqlConnector` | `query_execution`, `get_entity_schemas` |
| Snowflake | `SnowflakeConnector` | `query_execution`, `get_entity_schemas` |
| Databricks | `DatabricksConnector` | `query_execution`, `get_entity_schemas` |
| SQLite | `SQLiteConnector` | `query_execution`, `get_entity_schemas` |

Each connector implements database-specific query execution logic and SQL dialect rules, making the system adaptable to various database environments. The `ConnectorFactory` instantiates the appropriate connector based on configuration.

```mermaid
graph TD
    subgraph "Connector Architecture"
        Factory["ConnectorFactory"]
        AbstractConnector["SqlConnector (abstract)"]
        
        Factory --> AbstractConnector
        AbstractConnector --> TsqlConnector["TsqlConnector"]
        AbstractConnector --> PostgresConnector["PostgresSqlConnector"]
        AbstractConnector --> SnowflakeConnector["SnowflakeConnector"]
        AbstractConnector --> DatabricksConnector["DatabricksConnector"]
        AbstractConnector --> SQLiteConnector["SQLiteConnector"]
    end
    
    subgraph "Key Methods"
        AbstractConnector --> QueryExecution["query_execution()"]
        AbstractConnector --> GetSchemas["get_entity_schemas()"]
        AbstractConnector --> SanitizeIdentifier["sanitize_identifier()"]
        AbstractConnector --> EngineRules["engine_specific_rules"]
    end
```

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/postgres_sql.py:13-171](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sql.py](), [deploy_ai_search_indexes/pyproject.toml:33-45]()

## Image Processing System Architecture

The Image Processing system processes documents with images and charts to make them usable in RAG applications. It uses Azure Document Intelligence and multi-modal models to extract and interpret visual content.

```mermaid
graph TD
    Document["Document with Images"] --> FunctionApp["Azure Function App"]
    
    subgraph "Processing Pipeline"
        LayoutAnalysis["Layout Analysis"]
        FigureAnalysis["Figure Analysis"]
        Merger["Layout & Figure Merger"]
        TextChunker["Semantic Text Chunker"]
        MarkupCleaner["Markup Cleaner"]
        
        FunctionApp --> LayoutAnalysis
        LayoutAnalysis -->|"Extracted Figures"| FigureAnalysis
        LayoutAnalysis -->|"Text Content"| Merger
        FigureAnalysis -->|"Figure Descriptions"| Merger
        Merger -->|"Unified Content"| TextChunker
        TextChunker -->|"Chunked Content"| MarkupCleaner
    end
    
    subgraph "External Services"
        ADI["Azure Document Intelligence"]
        GPT4["GPT-4o-mini Model"]
        AISearch["Azure AI Search"]
    end
    
    LayoutAnalysis --> ADI
    FigureAnalysis --> GPT4
    MarkupCleaner --> AISearch
```

Sources: [image_processing/pyproject.toml:11-35](), [README.md:18]()

The Image Processing system consists of these main components:

1. **Layout Analysis**: Uses Azure Document Intelligence to analyze document structure, identifying text, figures, tables, and other elements.

2. **Figure Analysis**: Extracts figures and charts from documents and uses GPT-4o-mini to generate descriptions of these visual elements.

3. **Semantic Text Chunking**: Intelligently groups similar sentences while preserving the relationship between text and visual elements.

Sources: [README.md:13-15](), [image_processing/pyproject.toml:10-35]()

## Integration with Azure AI Search

Both systems integrate with Azure AI Search for storing and retrieving metadata, cached queries, and processed document content:

```mermaid
graph TD
    subgraph "Text-to-SQL Components"
        DD["Data Dictionary"] --> SchemaStore["Schema Store Index"]
        CVS["Column Value Store"] --> ValueStore["Column Value Store Index"] 
        QC["Query Cache"] --> CacheIndex["Query Cache Index"]
    end
    
    subgraph "Image Processing Components"
        DP["Document Processor"] --> DocIndex["Document Content Index"]
    end
    
    subgraph "Azure AI Search"
        SchemaStore --> AIS["Azure AI Search Service"]
        ValueStore --> AIS
        CacheIndex --> AIS
        DocIndex --> AIS
    end
    
    AIS --> RAG["RAG Application"]
```

The repository includes utilities in the `/deploy_ai_search_indexes` directory for deploying the required Azure AI Search indexes, indexers, and skillsets.

Key features:
- Schema Store Index: Stores metadata about database entities
- Column Value Store Index: Stores sample values for database columns
- Query Cache Index: Stores questions and corresponding SQL queries
- Document Content Index: Stores processed document content with figure descriptions

Sources: [deploy_ai_search_indexes/pyproject.toml:1-46](), [text_2_sql/GETTING_STARTED.md:1-27]()

## State Management

For managing conversational state across multiple interactions, the system provides state store implementations:

```mermaid
graph TD
    subgraph "State Store Options"
        InMem["InMemoryStateStore"] --> StateStore["StateStore Interface"]
        Cosmos["CosmosStateStore"] --> StateStore
    end
    
    StateStore --> Agents["Agentic System"]
    Agents --> |"Preserve Context"| Conversation["Conversation Thread"]
```

The state management allows:
- Preservation of conversation context across multiple turns
- Persistence of agent state for long-running conversations
- Thread-based conversation management

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/state_store.py:1-58](), [text_2_sql/autogen/README.md:124-127]()

## Key Benefits

The DSTK Text2SQL and Image Processing toolkit provides several key benefits for RAG applications:

1. **Real-time data access**: The Text-to-SQL system enables access to up-to-date structured data without pre-computing reports.

2. **Accurate numerical calculations**: Pushes numerical calculations to the database engine for accuracy.

3. **Complex query handling**: Supports aggregations, complex joins, and filtering in natural language.

4. **Rich document understanding**: Processes documents with images, charts, and complex layouts.

5. **Efficient performance**: Uses query caching and efficient indexing to improve response time.

For detailed implementation and deployment instructions, see [Setup and Deployment Guide](#5).

Sources: [text_2_sql/README.md:11-21](), [README.md:3-17]()

---

# Page: Text-to-SQL System

# Text-to-SQL System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [text_2_sql/.env.example](text_2_sql/.env.example)
- [text_2_sql/autogen/pyproject.toml](text_2_sql/autogen/pyproject.toml)
- [text_2_sql/autogen/src/autogen_text_2_sql/__init__.py](text_2_sql/autogen/src/autogen_text_2_sql/__init__.py)
- [text_2_sql/text_2_sql_core/pyproject.toml](text_2_sql/text_2_sql_core/pyproject.toml)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/factory.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/factory.py)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/payloads/__init__.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/payloads/__init__.py)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/utils/database.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/utils/database.py)
- [uv.lock](uv.lock)

</details>



The Text-to-SQL system transforms natural language questions into SQL queries that can be executed against various database engines. By leveraging a multi-agent architecture powered by the AutoGen framework, the system can understand user queries, identify relevant database schemas, generate appropriate SQL commands, and return results in a user-friendly format. This document describes the architecture, components, and functionality of the Text-to-SQL system.

The Text-to-SQL system is one of the core components in the repository, working alongside the [Image Processing System](#3) and integrated with [AI Search Indexes](#4) to enhance Retrieval-Augmented Generation applications.

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/__init__.py](), [text_2_sql/autogen/pyproject.toml]()

## System Architecture

The system employs an agentic approach that breaks down the complex task of natural language to SQL conversion into smaller, specialized components handled by different AI agents.

### High-Level Architecture

```mermaid
graph TD
    User[("User")] --> UserMsg["User Message"]
    UserMsg --> Text2SQL["AutoGenText2Sql"]
    
    subgraph "Agentic Pipeline"
        Text2SQL --> RewriteAgent["User Message Rewrite Agent"]
        RewriteAgent --> QueryCacheAgent["SQL Query Cache Agent"]
        QueryCacheAgent -->|"cache miss"| SchemaAgent["Schema Selection Agent"]
        SchemaAgent --> SQLGenAgent["SQL Query Generation Agent"]
        SQLGenAgent --> CorrectionAgent["SQL Query Correction Agent"]
        CorrectionAgent --> AnswerAgent["Answer Agent"]
        AnswerAgent --> Response["Response to User"]
    end
    
    subgraph "Database Connectors"
        ConnectorFactory["Connector Factory"] 
        TsqlConnector["TSQL Connector"]
        SnowflakeConnector["Snowflake Connector"]
        DatabricksConnector["Databricks Connector"]
        PostgresConnector["Postgres Connector"] 
        SQLiteConnector["SQLite Connector"]
        
        ConnectorFactory --> TsqlConnector
        ConnectorFactory --> SnowflakeConnector
        ConnectorFactory --> DatabricksConnector
        ConnectorFactory --> PostgresConnector
        ConnectorFactory --> SQLiteConnector
    end
    
    subgraph "Storage Components"
        SchemaStore["Schema Store"]
        QueryCache["Query Cache"]
        ColumnStore["Column Value Store"]
        StateStore["State Store"]
    end
    
    Text2SQL --> ConnectorFactory
    Text2SQL --> StateStore
    
    SchemaAgent <--> SchemaStore
    QueryCacheAgent <--> QueryCache
    SchemaAgent <--> ColumnStore
    SQLGenAgent --> ConnectorFactory
    CorrectionAgent --> ConnectorFactory
    
    Response --> User
```

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/autogen_text_2_sql.py](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/factory.py]()

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/autogen_text_2_sql.py](). [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/factory.py]()

## Core Components

The Text-to-SQL system is centered around the `AutoGenText2Sql` class, which orchestrates the entire natural language to SQL conversion process. This class integrates various components to form a complete pipeline from user question to formatted answer.

### Key Classes and Interfaces

| Component | Description | Source File |
|-----------|-------------|-------------|
| `AutoGenText2Sql` | Main orchestration class that manages the agent flow and interactions | autogen_text_2_sql/autogen_text_2_sql.py |
| `StateStore` | Interface for conversation state management with two implementations: `InMemoryStateStore` and `CosmosStateStore` | autogen_text_2_sql/state_store.py |
| `ConnectorFactory` | Factory that creates appropriate database, AI Search, and OpenAI connectors based on configuration | text_2_sql_core/connectors/factory.py |
| `DatabaseEngine` | Enum representing supported database engines (TSQL, Snowflake, Databricks, PostgreSQL, SQLite) | text_2_sql_core/utils/database.py |
| `InteractionPayload` | Base class for structured communication payloads between the system and user interface | text_2_sql_core/payloads/interaction_payloads.py |

The system depends on several key packages:
- AutoGen framework components (`autogen-agentchat`, `autogen-core`, `autogen-ext`)
- Database connectors specific to each supported database engine
- Azure services integration for state management and AI services
- NLP and SQL processing tools for query analysis and generation

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/__init__.py](), [text_2_sql/autogen/pyproject.toml](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/utils/database.py]()

## Agentic Flow

The system uses a multi-agent architecture powered by AutoGen to break down the natural language to SQL conversion process into specialized tasks. Each agent has a specific responsibility in the pipeline, allowing for complex problem decomposition and expert handling of each subtask.

```mermaid
flowchart TD
    Start(["User Question"]) --> UserMessageRewrite["UserMessageRewriteAgent\nReformats user question"]
    
    UserMessageRewrite --> QueryCache{"QueryCache\nEnabled?"}
    QueryCache -->|"Yes"| CacheCheck["SQL Query Cache Agent\nChecks for similar questions"]
    QueryCache -->|"No"| SchemaSelection
    
    CacheCheck --> CacheHit{"Cache\nHit?"}
    CacheHit -->|"Yes"| CachedResults["Return Cached Results"]
    CacheHit -->|"No"| SchemaSelection
    
    SchemaSelection["Schema Selection Agent\nIdentifies relevant tables and columns"]
    SchemaSelection --> ColumnLookup{"ColumnStore\nEnabled?"}
    
    ColumnLookup -->|"Yes"| ValueLookup["Retrieve sample column values\nfor better context"]
    ColumnLookup -->|"No"| DisambigCheck
    ValueLookup --> DisambigCheck
    
    DisambigCheck{"Disambiguation\nNeeded?"}
    
    DisambigCheck -->|"Yes"| DisambigAgent["Disambiguation Agent\nRequests clarification"]
    DisambigAgent --> User(["User"])
    User --> SchemaSelection
    
    DisambigCheck -->|"No"| SQLGeneration["SQL Generation Agent\nCreates SQL query"]
    SQLGeneration --> SQLCorrection["SQL Correction Agent\nVerifies SQL syntax"]
    SQLCorrection --> SQLExecution["Query Execution\nRuns against database"]
    SQLExecution --> AnswerFormatting["Answer Agent\nFormats results"]
    
    CachedResults --> AnswerFormatting
    
    AnswerFormatting --> FollowUpCheck{"Follow-Up\nEnabled?"}
    FollowUpCheck -->|"Yes"| FollowUp["Generate Follow-Up Suggestions"]
    FollowUp --> FinalAnswer(["Final Answer"])
    FollowUpCheck -->|"No"| FinalAnswer
```

The flow begins with a user question and proceeds through multiple specialized agents that each handle a different aspect of the process:

1. **User Message Rewrite Agent**: Reformats complex questions to be more amenable to SQL generation
2. **SQL Query Cache Agent**: Checks if similar questions have been processed before to avoid redundant computation
3. **Schema Selection Agent**: Identifies the relevant database tables and columns for the question
4. **SQL Generation Agent**: Creates a syntactically correct SQL query for the target database
5. **SQL Correction Agent**: Verifies and fixes any issues in the generated SQL
6. **Answer Agent**: Formats the query results into a natural language response for the user

The system also includes optional components that can be enabled or disabled via configuration:
- Query Cache for improved performance with similar questions
- Column Value Store to provide better context during schema selection
- Disambiguation handling for unclear or ambiguous questions
- Follow-up suggestion generation to enhance the conversational experience

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/autogen_text_2_sql.py](), [text_2_sql/.env.example:3-9]()

### Agent Configuration and Initialization

The agents are configured and initialized in the `AutoGenText2Sql` class, which manages the agent workflow. The configuration is driven by environment variables that control features like query caching, column value store usage, and follow-up suggestion generation.

```mermaid
classDiagram
    class AutoGenText2Sql {
        -_use_query_cache: bool
        -_pre_run_query_cache: bool
        -_use_column_value_store: bool
        -_generate_follow_up_suggestions: bool
        -_row_limit: int
        -state_store: StateStore
        -agentic_flow: AgentWorkflow
        +__init__(state_store, **kwargs)
        +get_all_agents()
        +process_user_message(thread_id, message_payload)
    }
    
    class StateStore {
        <<interface>>
        +save_state(thread_id, state)
        +get_state(thread_id)
    }
    
    class InMemoryStateStore {
        -_state_map: dict
        +save_state(thread_id, state)
        +get_state(thread_id)
    }
    
    class CosmosStateStore {
        -_cosmos_client
        -_container_client
        +save_state(thread_id, state)
        +get_state(thread_id)
    }
    
    StateStore <|-- InMemoryStateStore
    StateStore <|-- CosmosStateStore
    
    AutoGenText2Sql --> StateStore: uses
    AutoGenText2Sql --> "ConnectorFactory": uses
```

The system reads configuration from environment variables to determine which features to enable:

```
Text2Sql__UseQueryCache=True            # Enable/disable query caching
Text2Sql__PreRunQueryCache=True         # Pre-run cached queries for faster responses
Text2Sql__UseColumnValueStore=True      # Use column values for schema selection
Text2Sql__GenerateFollowUpSuggestions=True  # Generate follow-up question suggestions
Text2Sql__RowLimit=100                  # Maximum rows returned in results
```

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/__init__.py](), [text_2_sql/.env.example:3-9]()

## Database Support

The system supports multiple database engines through an extensible connector architecture. This design allows the same Text-to-SQL pipeline to work with various database backends with minimal changes.

```mermaid
classDiagram
    class ConnectorFactory {
        +get_database_connector() static
        +get_ai_search_connector() static
        +get_open_ai_connector() static
    }
    
    class SqlConnector {
        <<interface>>
        +execute_query(query: str) async
        +get_schema() async
        +get_column_values(column_name) async
    }
    
    SqlConnector <|-- TsqlSqlConnector
    SqlConnector <|-- SnowflakeSqlConnector
    SqlConnector <|-- DatabricksSqlConnector
    SqlConnector <|-- PostgresSqlConnector
    SqlConnector <|-- SQLiteSqlConnector
    
    ConnectorFactory ..> SqlConnector: creates
    
    class DatabaseEngine {
        <<enum>>
        DATABRICKS
        SNOWFLAKE
        TSQL
        POSTGRES
        SQLITE
    }
    
    class AISearchConnector {
        +search_schema(query) async
        +search_query_cache(query) async
        +search_column_values(query) async
    }
    
    class OpenAIConnector {
        +complete(prompt) async
    }
    
    ConnectorFactory ..> AISearchConnector: creates
    ConnectorFactory ..> OpenAIConnector: creates
```

The connector selection is implemented in the `get_database_connector` method of the `ConnectorFactory` class:

```python
@staticmethod
def get_database_connector():
    try:
        if os.environ["Text2Sql__DatabaseEngine"].upper() == "DATABRICKS":
            from text_2_sql_core.connectors.databricks_sql import DatabricksSqlConnector
            return DatabricksSqlConnector()
        elif os.environ["Text2Sql__DatabaseEngine"].upper() == "SNOWFLAKE":
            from text_2_sql_core.connectors.snowflake_sql import SnowflakeSqlConnector
            return SnowflakeSqlConnector()
        elif os.environ["Text2Sql__DatabaseEngine"].upper() == "TSQL":
            from text_2_sql_core.connectors.tsql_sql import TsqlSqlConnector
            return TsqlSqlConnector()
        elif os.environ["Text2Sql__DatabaseEngine"].upper() == "POSTGRES":
            from text_2_sql_core.connectors.postgres_sql import PostgresSqlConnector
            return PostgresSqlConnector()
        elif os.environ["Text2Sql__DatabaseEngine"].upper() == "SQLITE":
            from text_2_sql_core.connectors.sqlite_sql import SQLiteSqlConnector
            return SQLiteSqlConnector()
        else:
            raise ValueError(f"Database engine not found")
    except ImportError:
        raise ValueError("Failed to import SQL Connector. Check optional dependencies.")
```

Each database connector implements a common interface but handles the specifics of connecting to and querying its respective database system. Database-specific configuration options are provided through environment variables, as shown in the example configuration:

```
# Database Type Selection
Text2Sql__DatabaseEngine=TSQL  # TSQL, Postgres, Snowflake, Databricks, or SQLite

# Database-Specific Connection Details
# TSQL
Text2Sql__Tsql__ConnectionString=...
Text2Sql__Tsql__Database=...

# Postgres
Text2Sql__Postgres__ConnectionString=...
Text2Sql__Postgres__Database=...
Text2Sql__Postgres__User=...
# Additional Postgres configuration parameters...

# Snowflake
Text2Sql__Snowflake__User=...
Text2Sql__Snowflake__Password=...
# Additional Snowflake configuration parameters...

# Databricks
Text2Sql__Databricks__Catalog=...
Text2Sql__Databricks__ServerHostname=...
# Additional Databricks configuration parameters...
```

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/factory.py](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/utils/database.py](), [text_2_sql/.env.example:27-50](), [text_2_sql/text_2_sql_core/pyproject.toml:43-55]()

## Communication Payloads

The Text-to-SQL system uses structured payload objects for communication between components and with the user interface. These payloads provide a consistent and type-safe approach to message passing.

```mermaid
classDiagram
    class InteractionPayload {
        <<abstract>>
        +message_id: str
        +timestamp: datetime
        +payload_type: PayloadType
        +payload_source: PayloadSource
        +body: PayloadBodyBase
    }
    
    class UserMessagePayload {
        +body: Body
        +Body.user_message: str
        +Body.injected_parameters: dict
    }
    
    class ProcessingUpdatePayload {
        +body: Body
        +Body.title: str
        +Body.message: str
    }
    
    class DisambiguationRequestsPayload {
        +body: Body
        +Body.disambiguation_requests: list
        +Body.steps: list
    }
    
    class AnswerWithSourcesPayload {
        +body: Body
        +Body.answer: str
        +Body.sources: list[Source]
        +Body.steps: list
        +Body.follow_up_suggestions: list
    }
    
    InteractionPayload <|-- UserMessagePayload
    InteractionPayload <|-- ProcessingUpdatePayload
    InteractionPayload <|-- DisambiguationRequestsPayload
    InteractionPayload <|-- AnswerWithSourcesPayload
    
    class PayloadType {
        <<enum>>
        ANSWER_WITH_SOURCES
        DISAMBIGUATION_REQUESTS
        PROCESSING_UPDATE
        USER_MESSAGE
    }
    
    class PayloadSource {
        <<enum>>
        USER
        SYSTEM
    }
```

The system uses four main types of payloads:

1. **UserMessagePayload**: Contains the user's natural language question and any injected parameters
2. **ProcessingUpdatePayload**: Provides status updates during processing to inform the user of progress
3. **DisambiguationRequestsPayload**: Requests clarification from the user when a question is ambiguous
4. **AnswerWithSourcesPayload**: Delivers the final answer, including sources, processing steps, and optional follow-up suggestions

These payloads are exchanged asynchronously during the processing flow. The `process_user_message` method of `AutoGenText2Sql` takes a `UserMessagePayload` as input and yields various payloads as the processing progresses:

```python
async def process_user_message(
    self,
    thread_id: str,
    message_payload: UserMessagePayload,
) -> AsyncGenerator[InteractionPayload, None]:
    """Process a user message and yield interaction payloads."""
    
    # Load existing state if available
    state = self.state_store.get_state(thread_id)
    if state is not None:
        await self.agentic_flow.load_state(state)
    
    # Process the message through agents
    async for message in self.agentic_flow.run_stream(task=json.dumps(agent_input)):
        # Different message types generate different payloads
        if isinstance(message, TextMessage):
            # Progress updates based on which agent is active
            payload = ProcessingUpdatePayload(message="Processing...")
            
        elif isinstance(message, TaskResult):
            # Final results or disambiguation requests
            if "disambiguation_requests" in message.content:
                payload = DisambiguationRequestsPayload(...)
            else:
                payload = AnswerWithSourcesPayload(...)
        
        yield payload
    
    # Save state for future interactions
    assistant_state = await self.agentic_flow.save_state()
    self.state_store.save_state(thread_id, assistant_state)
```

This payload system enables the Text-to-SQL component to provide a rich, interactive experience with appropriate status updates, disambiguation capabilities, and detailed, formatted answers.

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/__init__.py:6-12](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/payloads/interaction_payloads.py]()

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/autogen_text_2_sql.py:277-368]()

## Processing Flow

The complete processing flow follows this sequence:

```mermaid
sequenceDiagram
    participant User
    participant AutoGenText2Sql as "AutoGenText2Sql"
    participant UMR as "UserMessageRewriteAgent"
    participant PQS as "ParallelQuerySolvingAgent"
    participant AA as "AnswerAgent"
    participant DB as "Database"
    
    User->>AutoGenText2Sql: process_user_message(UserMessagePayload)
    AutoGenText2Sql->>AutoGenText2Sql: Load state if exists
    AutoGenText2Sql->>UMR: Run (rewrite query)
    AutoGenText2Sql-->>User: ProcessingUpdatePayload
    
    UMR->>PQS: Rewritten query
    AutoGenText2Sql-->>User: ProcessingUpdatePayload
    
    alt Disambiguation Needed
        PQS->>AutoGenText2Sql: Disambiguation request
        AutoGenText2Sql-->>User: DismabiguationRequestsPayload
        User->>AutoGenText2Sql: Clarification
        AutoGenText2Sql->>PQS: Updated query
    else Clear Query
        PQS->>DB: Execute SQL query
        DB->>PQS: Query results
    end
    
    PQS->>AA: Pass results
    AutoGenText2Sql-->>User: ProcessingUpdatePayload
    
    AA->>AutoGenText2Sql: Formatted answer
    AutoGenText2Sql->>AutoGenText2Sql: Save state
    AutoGenText2Sql-->>User: AnswerWithSourcesPayload
```

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/autogen_text_2_sql.py:277-368]()

## Disambiguation Process

When a user's query is ambiguous, the system can request clarification through the disambiguation process:

```mermaid
graph TD
    Input["User Question"] --> Analysis["Question Analysis"]
    Analysis --> SchemaMapping["Schema Mapping"]
    
    SchemaMapping --> Clarity{"Is Mapping\nClear?"}
    
    Clarity -->|Yes| SQL["Generate SQL"]
    
    Clarity -->|No| AmbiguityType{"Type of\nAmbiguity"}
    
    AmbiguityType -->|No Schema Match| NoMatch["Request with explanation\nthat data may not be available"]
    
    AmbiguityType -->|Multiple Possible Mappings| MultipleOptions["Request with specific\noptions to choose from"]
    
    AmbiguityType -->|Unclear Question| Rephrase["Request user to\nrephrase question"]
    
    NoMatch --> User([User Response])
    MultipleOptions --> User
    Rephrase --> User
    
    User --> SchemaMapping
```

The disambiguation logic is implemented in the `extract_disambiguation_request` method:

```python
def extract_disambiguation_request(self, messages: list) -> DismabiguationRequestsPayload:
    """Extract the disambiguation request from the answer."""
    all_disambiguation_requests = self.parse_message_content(messages[-1].content)
    
    steps = self.extract_steps(messages)
    request_payload = DismabiguationRequestsPayload(steps=steps)
    
    for per_question_disambiguation_request in all_disambiguation_requests["disambiguation_requests"].values():
        for disambiguation_request in per_question_disambiguation_request:
            request = DismabiguationRequestsPayload.Body.DismabiguationRequest(
                assistant_question=disambiguation_request["assistant_question"],
                user_choices=disambiguation_request["user_choices"],
            )
            request_payload.body.disambiguation_requests.append(request)
    
    return request_payload
```

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/autogen_text_2_sql.py:181-204](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/disambiguation_and_sql_query_generation_agent.yaml:155-242]()

## SQL Query Generation

SQL query generation is primarily handled by the `ParallelQuerySolvingAgent`, which uses the following process:

1. Analyze the user question to identify entities, filters, and aggregations
2. Map these components to database schema elements (tables, columns)
3. Generate a syntactically correct SQL query for the target database engine
4. Execute the query against the database

The prompting system uses structured rules to guide the LLM:

```yaml
<sql_query_generation_rules>
  <engine_specific_rules>
      {{ engine_specific_rules }}
      Rows returned will be automatically limited to {{ row_limit }}.
  </engine_specific_rules>

  Your primary focus is on:
    1. Understanding what data the user wants to retrieve
    2. Identifying the necessary tables and their relationships
    3. Determining any required calculations or aggregations
    4. Specifying any filtering conditions based on the user's criteria
```

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/disambiguation_and_sql_query_generation_agent.yaml:103-153]()

## State Management

The system provides two state store implementations to maintain conversation context:

1. `InMemoryStateStore`: For testing or single-instance deployments
2. `CosmosStateStore`: For distributed deployments using Azure Cosmos DB

```python
async def process_user_message(self, thread_id: str, message_payload: UserMessagePayload):
    # Processing code...
    
    state = self.state_store.get_state(thread_id)
    if state is not None:
        await self.agentic_flow.load_state(state)
        
    # Processing continues...
    
    # Before returning final result
    assistant_state = await self.agentic_flow.save_state()
    self.state_store.save_state(thread_id, assistant_state)
```

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/autogen_text_2_sql.py:300-304](), [text_2_sql/autogen/src/autogen_text_2_sql/autogen_text_2_sql.py:362-364](), [text_2_sql/autogen/src/autogen_text_2_sql/__init__.py]()

## Dependencies

The system has dependencies on several key packages:

**Core Dependencies:**
- AutoGen framework components (`autogen-agentchat`, `autogen-core`, `autogen-ext`)
- Database connectors (specific to each database type)
- Azure services integration (`azure-cosmos`, `azure-search`)
- NLP and SQL processing tools (`nltk`, `sqlparse`, `sqlglot`)

**Database-Specific Dependencies:**
```toml
snowflake = ["snowflake-connector-python>=3.12.3"]
databricks = ["databricks-sql-connector>=3.0.1", "pyarrow>=14.0.2,<17"]
postgres = ["psycopg>=3.2.3"]
sqlite = ["aiosqlite>=0.19.0"]
```

Sources: [text_2_sql/autogen/pyproject.toml](), [text_2_sql/text_2_sql_core/pyproject.toml]()

## Conclusion

The Text-to-SQL system provides a powerful natural language interface to databases by leveraging a specialized multi-agent architecture. The system's key strengths include:

1. Support for multiple database engines (TSQL, Snowflake, Databricks, PostgreSQL, SQLite)
2. Sophisticated disambiguation capabilities for handling unclear questions
3. Stateful conversation management for context preservation
4. Extensible architecture for adding new database connectors

For more information about specific components, see:
- [Agentic Architecture](#2.1) for details on the agent system design
- [Data Dictionary](#2.3) for information on schema metadata management
- [Query Cache](#2.6) for details on the caching mechanism to improve performance

---

# Page: Agentic Architecture

# Agentic Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [text_2_sql/autogen/README.md](text_2_sql/autogen/README.md)
- [text_2_sql/autogen/src/autogen_text_2_sql/autogen_text_2_sql.py](text_2_sql/autogen/src/autogen_text_2_sql/autogen_text_2_sql.py)
- [text_2_sql/autogen/src/autogen_text_2_sql/state_store.py](text_2_sql/autogen/src/autogen_text_2_sql/state_store.py)
- [text_2_sql/previous_iterations/semantic_kernel/README.md](text_2_sql/previous_iterations/semantic_kernel/README.md)
- [text_2_sql/previous_iterations/semantic_kernel/plugins/vector_based_sql_plugin/vector_based_sql_plugin.py](text_2_sql/previous_iterations/semantic_kernel/plugins/vector_based_sql_plugin/vector_based_sql_plugin.py)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/payloads/interaction_payloads.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/payloads/interaction_payloads.py)

</details>



This document explains the multi-agent architecture that powers the Text-to-SQL system. The architecture consists of specialized, cooperating agents that work together to convert natural language questions into SQL queries, execute them against a database, and format the results into natural language answers.

For information about the specific agent types and their detailed responsibilities, see [Agent Types and Responsibilities](#2.2).

## Core Architecture Overview

The Text-to-SQL system implements a multi-agent architecture where specialized agents collaborate in a predefined flow to process user questions. Each agent is responsible for a specific task in the overall pipeline, allowing for separation of concerns and modular design.

```mermaid
graph TD
    User(["User"]) -->|"Question"| MessageRewrite["user_message_rewrite_agent"]
    
    MessageRewrite -->|"Rewritten Question"| ParallelQuery["parallel_query_solving_agent"]
    
    ParallelQuery -->|"SQL Results"| Answer{{"Follow-up Enabled?"}}
    
    Answer -->|"Yes"| FollowUp["answer_with_follow_up_suggestions_agent"]
    Answer -->|"No"| SimpleAnswer["answer_agent"]
    
    FollowUp -->|"Natural Language Answer"| User
    SimpleAnswer -->|"Natural Language Answer"| User
```

The system follows a sequential flow where each agent processes the output of the previous agent. The core flow as implemented in `get_all_agents()` is:

1. **User Message Rewrite Agent**: Processes the user's initial question, resolving relative dates and breaking down complex questions
2. **Parallel Query Solving Agent**: Coordinates schema selection, query generation, and execution across multiple specialized sub-agents
3. **Answer Agent**: Formats the results as a natural language response to the user, with optional follow-up suggestions

The choice between `answer_agent` and `answer_with_follow_up_suggestions_agent` is determined by the `_generate_follow_up_suggestions` configuration parameter, which is controlled by the `Text2Sql__GenerateFollowUpSuggestions` environment variable.

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/autogen_text_2_sql.py:56-78](), [text_2_sql/autogen/src/autogen_text_2_sql/autogen_text_2_sql.py:91-117](), [text_2_sql/autogen/README.md:5-15]()

## Agent Implementation and Creation

Agents in the system are implemented as specialized classes that extend from `BaseChatAgent` from the AutoGen framework. The system uses a factory pattern to create and configure agents, which allows for flexible agent configuration and reuse.

```mermaid
classDiagram
    class LLMAgentCreator {
        +create(name: str, **kwargs): AssistantAgent
        +load_agent_file(name: str): dict
        +get_tool(sql_helper, tool_name: str): FunctionTool
        +get_property_and_render_parameters(agent_file, property, parameters): str
    }
    
    class AssistantAgent {
        +name: str
        +tools: List[Tool]
        +model_client: LLMModelClient
        +description: str
        +system_message: str
    }
    
    class AutoGenText2Sql {
        -state_store: StateStore
        -kwargs: dict
        -_agentic_flow: SelectorGroupChat
        +get_all_agents(): List[BaseChatAgent]
        +process_user_message(thread_id, message_payload): AsyncGenerator
    }
    
    LLMAgentCreator --> AssistantAgent : creates
    AutoGenText2Sql --> LLMAgentCreator : uses
```

The `LLMAgentCreator` is a factory class that:
1. Loads prompt templates from YAML files
2. Creates and configures agents with the appropriate tools
3. Sets up model clients with the right LLM configurations
4. Renders agent system messages with the provided parameters

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/creators/llm_agent_creator.py:18-144]()

## Agent Orchestration

The agents are orchestrated using AutoGen's `SelectorGroupChat`, which provides a framework for agent communication and flow control. The selector function determines which agent should speak next based on the current state of the conversation.

```mermaid
graph TD
    subgraph "Agent Orchestration"
        Init["Initialize AutoGenText2Sql"] -->|"Create agents"| Flow["Create SelectorGroupChat"]
        Flow -->|"Define selector function"| Selector["unified_selector()"]
        Flow -->|"Define termination condition"| Term["termination_condition"]
        Selector --> Transition["Agent transition rules"]
        Term --> TC["SourceMatch | TextMention | MaxMessage"]
    end
    
    subgraph "Message Processing"
        UserM["User Message"] --> Process["process_user_message()"]
        Process -->|"Run agentic flow"| Stream["agentic_flow.run_stream()"]
        Stream -->|"Generate payload"| Result["Return payload to user"]
    end
```

The orchestration is defined in the `AutoGenText2Sql` class, which:
1. Initializes all the required agents
2. Creates a `SelectorGroupChat` with a custom selector function
3. Defines termination conditions for the conversation
4. Processes user messages through the agent flow
5. Tracks and manages conversation state between interactions

The agent flow is managed by a sophisticated selector function (`unified_selector`) that determines the next agent to act based on the current conversation state:

```mermaid
flowchart TD
    Start[["Start"]] --> User["User Message"]
    User --> Rewrite["user_message_rewrite_agent"]
    
    Rewrite --> ParallelQuery["parallel_query_solving_agent"]
    
    ParallelQuery --> |"Generate Results"| Answer{{"Answer Agent Selection"}}
    Answer --> |"Follow-up enabled"| FollowUp["answer_with_follow_up_suggestions_agent"]
    Answer --> |"Follow-up disabled"| Simple["answer_agent"]
    
    FollowUp --> End[["End"]]
    Simple --> End
```

The termination conditions for the conversation are defined in the `termination_condition` property to ensure the flow completes properly:
1. When either `answer_agent` or `answer_with_follow_up_suggestions_agent` has spoken (indicating a complete answer)
2. When a disambiguation request is detected via `TextMentionTermination("contains_disambiguation_requests")`
3. When a maximum message limit is reached via `MaxMessageTermination(5)`

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/autogen_text_2_sql.py:119-135](), [text_2_sql/autogen/src/autogen_text_2_sql/autogen_text_2_sql.py:80-117](), [text_2_sql/autogen/README.md:18-63]()

## Parallel Query Solving Process

The core of the system is the `ParallelQuerySolvingAgent`, which coordinates the complex process of converting natural language to SQL:

```mermaid
flowchart TD
    UserQ["Preprocessed Question"] --> Cache{{"Query Cache\nEnabled?"}}
    
    Cache -->|"Yes"| QueryCache["SQL Query Cache Agent"]
    Cache -->|"No"| SchemaSelect["Schema Selection Agent"]
    
    QueryCache -->|"Cache Hit"| SQLCorr["SQL Query Correction Agent"]
    QueryCache -->|"Cache Miss"| SchemaSelect
    
    SchemaSelect --> |"Relevant Schemas"| Disambig{{"Disambiguation\nNeeded?"}}
    
    Disambig -->|"Yes"| DisambigAgent["Disambiguation Agent"]
    Disambig -->|"No"| SQLGen["SQL Query Generation Agent"]
    
    DisambigAgent -->|"Disambiguated Query"| SQLGen
    
    SQLGen -->|"Generated SQL"| SQLCorr
    
    SQLCorr -->|"Needs Fixes"| SQLGen
    SQLCorr -->|"Ready to Execute"| Exec["Query Execution"]
    
    Exec -->|"Results"| Out["Database Results"]
```

This specialized agent encapsulates multiple sub-agents that work together:

1. **Query Cache Agent**: Checks if similar questions have been asked before
2. **Schema Selection Agent**: Identifies relevant database schemas using vector search
3. **Disambiguation Agent**: Clarifies any ambiguities in schema selection
4. **SQL Generation Agent**: Creates SQL queries based on selected schemas
5. **SQL Correction Agent**: Verifies and fixes the generated queries
6. **Query Execution**: Runs the queries against the database

The agent handles an iterative correction process, where generated SQL may be sent back to the generation agent if corrections are needed. This ensures high-quality SQL queries that are syntactically correct and properly optimized.

Based on the query execution results and cache status, the agent can follow different paths to reach the final answer as efficiently as possible.

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/custom_agents/parallel_query_solving_agent.py](), [text_2_sql/autogen/README.md:18-63](), [text_2_sql/autogen/README.md:72-94]()

## Payload Structure and Communication

The agents communicate with each other through structured payloads defined in the system. These payloads follow a consistent format and carry the required information between agents.

```mermaid
classDiagram
    class InteractionPayload {
        +root: PayloadBase
    }
    
    class PayloadBase {
        +message_id: str
        +timestamp: datetime
        +payload_type: PayloadType
        +payload_source: PayloadSource
        +body: PayloadAndBodyBase
    }
    
    class UserMessagePayload {
        +body: Body
    }
    
    class AnswerWithSourcesPayload {
        +body: Body
    }
    
    class DismabiguationRequestsPayload {
        +body: Body
    }
    
    class ProcessingUpdatePayload {
        +body: Body
    }
    
    PayloadBase <|-- UserMessagePayload
    PayloadBase <|-- AnswerWithSourcesPayload
    PayloadBase <|-- DismabiguationRequestsPayload
    PayloadBase <|-- ProcessingUpdatePayload
    
    InteractionPayload --> PayloadBase
```

The structured payload approach allows for:
1. Consistent communication between agents
2. Standard format for user and system messages
3. Clear differentiation between message types
4. Structured storage of query results and answers

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/payloads/interaction_payloads.py:1-189]()

## State Management

The architecture includes state management to maintain conversation context across multiple interactions. This allows for follow-up questions and multi-turn conversations.

```mermaid
sequenceDiagram
    participant User
    participant Text2SQL as "AutoGenText2Sql"
    participant StateStore
    participant Agents as "Agentic Flow"
    
    User->>Text2SQL: process_user_message(thread_id, message)
    Text2SQL->>StateStore: get_state(thread_id)
    StateStore-->>Text2SQL: state
    
    Text2SQL->>Agents: load_state(state)
    Text2SQL->>Agents: run_stream(task)
    
    loop Agent Processing
        Agents->>Agents: Process message
        Agents-->>Text2SQL: Updates
        Text2SQL-->>User: Processing updates
    end
    
    Agents-->>Text2SQL: Final result
    Text2SQL->>Agents: save_state()
    Agents-->>Text2SQL: assistant_state
    Text2SQL->>StateStore: save_state(thread_id, assistant_state)
    Text2SQL-->>User: Final payload
```

The system uses a pluggable state store interface with multiple implementations:

```mermaid
classDiagram
    class StateStore {
        <<Abstract>>
        +get_state(thread_id: str): dict
        +save_state(thread_id: str, state: dict): None
    }
    
    class InMemoryStateStore {
        -cache: TTLCache
        +get_state(thread_id: str): dict
        +save_state(thread_id: str, state: dict): None
    }
    
    class CosmosStateStore {
        -_db: CosmosContainerClient
        -partition_key: str
        -partition_key_name: str
        +get_state(thread_id: str): dict
        +save_state(thread_id: str, state: dict): None
    }
    
    StateStore <|-- InMemoryStateStore
    StateStore <|-- CosmosStateStore
```

State management involves:
1. Loading the conversation state at the beginning of processing
2. Running the agent flow with the loaded state
3. Saving the updated state at the end of processing
4. Using a pluggable state store interface for flexibility

The system provides two built-in state store implementations:

1. **InMemoryStateStore**: Uses a time-based cache (TTLCache) to store conversation state in memory with a default expiration time of 4 hours. This is suitable for testing and simple deployments.

2. **CosmosStateStore**: Stores conversation state in Azure Cosmos DB, providing persistence across application restarts. This is suitable for production deployments.

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/autogen_text_2_sql.py:277-368](), [text_2_sql/autogen/src/autogen_text_2_sql/state_store.py:1-57]()

## Tools and External Integrations

Agents are equipped with specialized tools that enable them to interact with databases and other external systems.

```mermaid
graph TD
    subgraph "Agent Tools"
        Tool1["sql_query_execution_tool"]
        Tool2["sql_get_entity_schemas_tool"]
        Tool3["sql_get_column_values_tool"]
    end
    
    subgraph "Database Connectors"
        Connect["ConnectorFactory"]
        TSQL["TSQL Connector"]
        Postgres["PostgreSQL Connector"]
        Snowflake["Snowflake Connector"]
        Databricks["Databricks Connector"]
        SQLite["SQLite Connector"]
    end
    
    Agent["AssistantAgent"] -->|"Uses"| Tool1
    Agent -->|"Uses"| Tool2
    Agent -->|"Uses"| Tool3
    
    Tool1 -->|"Executes Through"| Connect
    Tool2 -->|"Fetches Through"| Connect
    Tool3 -->|"Queries Through"| Connect
    
    Connect -->|"Creates"| TSQL
    Connect -->|"Creates"| Postgres
    Connect -->|"Creates"| Snowflake
    Connect -->|"Creates"| Databricks
    Connect -->|"Creates"| SQLite
```

The tools provide a way for agents to:
1. Execute SQL queries against the database
2. Retrieve schema information for tables and views
3. Fetch column values for better query formulation
4. Access database-specific functionality

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/creators/llm_agent_creator.py:33-60]()

## Practical Usage Example

The system can be easily instantiated and used through a simple API:

```mermaid
sequenceDiagram
    participant User as "User Code"
    participant T2S as "AutoGenText2Sql"
    participant Agents as "Agent System"
    participant DB as "Database"
    
    User->>T2S: AutoGenText2Sql(state_store, use_case="Analysing sales data")
    User->>T2S: process_user_message("1", UserMessagePayload("what are the total sales"))
    
    T2S->>Agents: Run agents
    Agents->>T2S: Processing update
    T2S->>User: ProcessingUpdatePayload
    
    Agents->>DB: Execute SQL query
    DB->>Agents: Return results
    
    Agents->>T2S: Final result
    T2S->>User: AnswerWithSourcesPayload
```

This simple interface allows developers to:
1. Create a Text-to-SQL instance with a specific use case
2. Send user messages with unique thread IDs
3. Receive processing updates during execution
4. Get structured answers with the SQL query and results

Sources: [text_2_sql/autogen/Iteration 5 - Agentic Vector Based Text2SQL.ipynb:65-108]()

## Component Interaction

The following diagram illustrates how the natural language processing components interact with database components:

```mermaid
graph TD
    subgraph "Natural Language Space"
        UserQ["User Question"]
        NLAnswer["Natural Language Answer"]
    end
    
    subgraph "Agentic Processing Layer"
        Rewrite["user_message_rewrite_agent"]
        Cache["sql_query_cache_agent"]
        Parallel["parallel_query_solving_agent"]
        Answer["answer_agent/answer_with_follow_up_suggestions_agent"]
    end
    
    subgraph "SQL Generation Layer"
        Schema["Schema Selection"]
        Disambig["Disambiguation"]
        Generation["SQL Generation"]
        Correction["SQL Correction"]
    end
    
    subgraph "Database Layer"
        Execution["Query Execution"]
        Schemas["Entity Schemas"]
        Values["Column Values"]
        Results["Query Results"]
    end
    
    UserQ --> Rewrite
    Rewrite --> Cache
    Cache -->|"Cache Miss"| Parallel
    Cache -->|"Cache Hit"| Answer
    
    Parallel --> Schema
    Schema --> Schemas
    Schema --> Disambig
    Disambig --> Generation
    Generation --> Correction
    Correction --> Execution
    
    Execution --> Results
    Results --> Parallel
    Parallel --> Answer
    Answer --> NLAnswer
```

This multi-layered architecture enables:
1. Clear separation between natural language and database interactions
2. Modular components that can be improved independently
3. Flexible processing flow with multiple checkpoints
4. Consistent data transformation between layers

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/autogen_text_2_sql.py:34-369]()

## Summary

The Text-to-SQL system uses a sophisticated agentic architecture where specialized agents collaborate in a structured flow to convert natural language questions into SQL queries and present the results as natural language answers. This architecture provides:

1. **Modularity**: Each agent has a specific responsibility, making the system easier to maintain and extend
2. **Flexibility**: Agents can be replaced or upgraded independently
3. **Robustness**: The system can handle disambiguation and error correction at multiple stages
4. **Extensibility**: New capabilities can be added by introducing new agents or enhancing existing ones
5. **Maintainability**: Clear interfaces between agents make the system easier to understand and modify

This approach enables a more reliable and accurate text-to-SQL conversion compared to single-agent approaches.

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/autogen_text_2_sql.py:34-369]()

---

# Page: Agent Types and Responsibilities

# Agent Types and Responsibilities

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [text_2_sql/autogen/src/autogen_text_2_sql/custom_agents/sql_schema_selection_agent.py](text_2_sql/autogen/src/autogen_text_2_sql/custom_agents/sql_schema_selection_agent.py)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/ai_search.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/ai_search.py)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/open_ai.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/open_ai.py)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/custom_agents/sql_query_cache_agent.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/custom_agents/sql_query_cache_agent.py)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/custom_agents/sql_schema_selection_agent.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/custom_agents/sql_schema_selection_agent.py)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/answer_agent.yaml](text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/answer_agent.yaml)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/disambiguation_and_sql_query_generation_agent.yaml](text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/disambiguation_and_sql_query_generation_agent.yaml)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/sql_query_correction_agent.yaml](text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/sql_query_correction_agent.yaml)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/sql_schema_selection_agent.yaml](text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/sql_schema_selection_agent.yaml)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/user_message_rewrite_agent.yaml](text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/user_message_rewrite_agent.yaml)

</details>



This document details the different agent types within the Text-to-SQL system and their specific responsibilities. It provides a technical overview of each agent's role in the pipeline, from processing user input to generating the final answer. For information on the overall multi-agent architecture, see [Agentic Architecture](#2.1). For details on SQL query generation, see [SQL Query Generation and Execution](#2.5).

## Overview of Agent System

The Text-to-SQL system employs a specialized multi-agent architecture where each agent performs a specific task in the pipeline. This approach enables complex natural language questions to be broken down into manageable steps, with specialized agents handling different aspects of the process.

```mermaid
flowchart TD
    User([User]) -->|"Natural Language Question"| RewriteAgent["User Message Rewrite Agent"]
    RewriteAgent -->|"Processed Question"| CacheDecision{"Cache Enabled?"}
    
    CacheDecision -->|"Yes"| CacheAgent["SQL Query Cache Agent"]
    CacheDecision -->|"No"| SchemaAgent["Schema Selection Agent"]
    
    CacheAgent -->|"Cache Hit"| AnswerAgent["Answer Agent"]
    CacheAgent -->|"Cache Miss"| SchemaAgent
    
    SchemaAgent -->|"Selected Schemas"| DisambigGenAgent["Disambiguation and SQL Query Generation Agent"]
    
    alt "Disambiguation Required"
        DisambigGenAgent -->|"Disambiguation Request"| User
        User -->|"Disambiguation Response"| DisambigGenAgent
    end
    
    DisambigGenAgent -->|"Generated SQL"| CorrectionAgent["SQL Query Correction Agent"]
    
    CorrectionAgent -->|"Validated SQL"| Database[(Database)]
    Database -->|"Query Results"| AnswerAgent
    
    AnswerAgent -->|"Answer"| User
```

*Diagram: Agent Flow in the Text-to-SQL System*

Sources:
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/user_message_rewrite_agent.yaml:1-182]()
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/custom_agents/sql_schema_selection_agent.py:1-99]()
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/custom_agents/sql_query_cache_agent.py:1-43]()
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/disambiguation_and_sql_query_generation_agent.yaml:1-278]()

## Agent Types and Code Mapping

The following diagram maps the agent types to their corresponding code implementations, showing the relationship between the conceptual agents and their actual code entities:

```mermaid
classDiagram
    class SqlQueryCacheAgentCustomAgent {
        +process_message(message, injected_parameters)
    }
    
    class SqlSchemaSelectionAgentCustomAgent {
        +process_message(message)
        -system_prompt
        -ai_search_connector
        -open_ai_connector
        -sql_connector
    }
    
    class SqlSchemaSelectionAgent {
        +on_messages(messages, cancellation_token)
        +on_messages_stream(messages, cancellation_token)
        +on_reset(cancellation_token)
    }
    
    class UserMessageRewriteAgent {
        +model: "4o-mini"
        +system_message
        +structured_output: true
        +context_size: 5
    }
    
    class DisambiguationAndSqlQueryGenerationAgent {
        +model: "4o-mini"
        +system_message
        +tools: [sql_get_entity_schemas_tool]
    }
    
    class SqlQueryCorrectionAgent {
        +model: "4o-mini"
        +system_message
        +tools: [sql_query_execution_tool, sql_get_entity_schemas_tool, sql_get_column_values_tool]
    }
    
    class AnswerAgent {
        +model: "4o-mini"
        +system_message
        +context_size: 8
    }
    
    class BaseChatAgent {
        +on_messages()
        +on_messages_stream()
        +on_reset()
    }
    
    class AISearchConnector {
        +run_ai_search_query()
        +get_column_values()
        +get_entity_schemas()
    }
    
    class OpenAIConnector {
        +run_completion_request()
    }
    
    BaseChatAgent <|-- SqlSchemaSelectionAgent
    SqlSchemaSelectionAgent --> SqlSchemaSelectionAgentCustomAgent
    SqlQueryCacheAgentCustomAgent --> ConnectorFactory
    SqlSchemaSelectionAgentCustomAgent --> ConnectorFactory
    SqlSchemaSelectionAgentCustomAgent --> OpenAIConnector
    SqlSchemaSelectionAgentCustomAgent --> AISearchConnector
    ConnectorFactory --> AISearchConnector
    ConnectorFactory --> OpenAIConnector
```

*Diagram: Agent Implementation Class Structure*

Sources:
- [text_2_sql/autogen/src/autogen_text_2_sql/custom_agents/sql_schema_selection_agent.py:1-63]()
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/custom_agents/sql_schema_selection_agent.py:1-99]()
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/custom_agents/sql_query_cache_agent.py:1-43]()
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/disambiguation_and_sql_query_generation_agent.yaml:1-280]()
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/sql_query_correction_agent.yaml:1-135]()
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/ai_search.py:1-283]()

## Agent Responsibilities

Each agent in the Text-to-SQL system has specific responsibilities and roles in processing user questions:

### User Message Rewrite Agent

The User Message Rewrite Agent preprocesses user inputs by analyzing and potentially restructuring complex queries.

**Key Responsibilities:**
- Breaking down complex queries into simpler steps that can be processed independently
- Filtering out malicious or unrelated queries based on allowed topics
- Determining if SQL queries are required to answer the question
- Resolving relative date references using the current date
- Maintaining the original intent of user questions while enhancing clarity

**Implementation:**
This agent is implemented as a prompt-based agent using GPT-4o-mini and returns a JSON structure with steps for processing.

Sources:
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/user_message_rewrite_agent.yaml:1-182]()

### SQL Query Cache Agent

The SQL Query Cache Agent checks for previously processed similar questions to avoid redundant processing.

**Key Responsibilities:**
- Checking if the current question is similar to previously processed questions
- Retrieving cached SQL queries and results when a match is found
- Passing cached results to the Answer Agent when appropriate

**Implementation:**
This agent is implemented in the `SqlQueryCacheAgentCustomAgent` class which uses connector factory to interact with database connectors.

```python
# Key methods
async def process_message(self, message: str, injected_parameters: dict) -> dict:
    # Fetch cached queries based on the question
    cached_query = await self.sql_connector.fetch_sql_queries_with_schemas_from_cache(message, injected_parameters)
    # Process and return results
```

Sources:
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/custom_agents/sql_query_cache_agent.py:1-43]()

### Schema Selection Agent

The Schema Selection Agent identifies the relevant database schemas needed to answer the user's question.

**Key Responsibilities:**
- Parsing the user's question to identify mentioned entities and filter conditions
- Retrieving relevant schemas from the database metadata
- Fetching column value information for potential filter conditions
- Selecting the most appropriate database when multiple options are available
- Providing schema information to downstream agents for SQL generation

**Implementation:**
This agent is implemented in both AutoGen-compatible (`SqlSchemaSelectionAgent`) and core (`SqlSchemaSelectionAgentCustomAgent`) classes.

Sources:
- [text_2_sql/autogen/src/autogen_text_2_sql/custom_agents/sql_schema_selection_agent.py:1-63]()
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/custom_agents/sql_schema_selection_agent.py:1-99]()

### Disambiguation and SQL Query Generation Agent

This agent combines disambiguation and SQL query generation capabilities in a single component. It specializes in disambiguating user questions and mapping them to database schemas before generating appropriate SQL queries.

**Key Responsibilities:**
- Disambiguating user questions by identifying unclear or ambiguous references
- Verifying mappings between user intent and available database schemas
- Requesting clarification from users when necessary through structured disambiguation requests
- Generating SQL queries once mappings are clear
- Mapping text filters, aggregations, and relationships to appropriate SQL constructs
- Following engine-specific SQL syntax rules

**Implementation:**
The agent is implemented as a YAML-defined prompt template using GPT-4o-mini and includes comprehensive instructions for:
- Understanding key database concepts
- Mapping question components to schema elements
- Generating proper SQL syntax for various operations
- Creating disambiguation requests when needed

```yaml
# Key disambiguation logic excerpt
<disambiguation_rules>
  Before carrying out disambiguation, ensure that you have checked all available database schemas 
  and filters for a most probable mapping...
  
  1. **No Match in Database Schemas or Uncertain Schema Availability**:
     - Generate a single disambiguation request with explanation
  
  2. **Multiple Possible Mappings**:
     - Generate disambiguation request with specific options for user choice
     - May generate multiple disambiguation requests for different ambiguities
  
  3. **Unclear or Ambiguous Question**:
     - Generate a single disambiguation request asking user to rephrase
</disambiguation_rules>
```

Sources:
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/disambiguation_and_sql_query_generation_agent.yaml:1-278]()

### SQL Query Correction Agent

The SQL Query Correction Agent specializes in SQL syntax correction and query execution for the target database engine.

**Key Responsibilities:**
- Converting standard SQL to engine-specific syntax
- Fixing syntax issues while preserving query logic
- Executing the corrected queries against the database
- Handling common error types and applying appropriate fixes
- Verifying that query results will answer all user questions

**Implementation:**
This agent is implemented as a YAML-defined prompt template using GPT-4o-mini with specialized tools for:
- SQL query execution
- Entity schema retrieval
- Column value retrieval

The agent follows a systematic workflow:
```
1. Initial Analysis:
   - Identify standard SQL patterns needing conversion
   - Check for engine-specific syntax requirements
   
2. Systematic Conversion:
   - Convert row limiting syntax
   - Convert date/time functions
   - Convert string functions
   - Convert aggregation syntax
   
3. Execution Process:
   - Try executing the converted query
   - Apply targeted fixes based on error type
   - Retry execution
   
4. Result Handling:
   - Format successful results
   - Include both original and converted queries
```

Sources:
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/sql_query_correction_agent.yaml:1-132]()

### Answer Agent

The Answer Agent formats the SQL query results into a natural language response for the user.

**Key Responsibilities:**
- Interpreting SQL query results to answer the user's question
- Formatting complex data in a human-readable format using Markdown
- Ensuring the response directly addresses all parts of the user's question
- Converting technical SQL results into business-friendly language

**Implementation:**
This agent is implemented as a prompt-based agent with a structured output format.

```yaml
# Key prompt elements
<role_and_objective>
  You are Senior Data Analyst, specializing in providing data driven answers to a user's question...
</role_and_objective>

<output>
  {
    "answer": "The response to the user's question.",
  }
</output>
```

Sources:
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/answer_agent.yaml:1-30]()

### Answer Agent

The Answer Agent formulates data-driven responses to the user's question based on the SQL query results.

**Key Responsibilities:**
- Providing clear and concise responses based on SQL query results
- Using Markdown formatting for better readability
- Ensuring responses directly address all parts of the user's question
- Taking a data-driven approach to generate accurate answers
- Explaining system capabilities when users ask about them

**Implementation:**
This agent is implemented as a YAML-defined prompt template using GPT-4o-mini with a context size of 8.

```yaml
# Key system information
<system_information>
  - You are part of an overall system that provides Text2SQL and subsequent data analysis functionality only.
  - You can assume that the SQL queries are correct and that the results are accurate.
  - You and the wider system can only generate SQL queries and process the results of these queries.
  - The main ability of the system is to perform natural language understanding and generate SQL queries.
</system_information>

<output>
  {
    "answer": "The response to the user's question."
  }
</output>
```

Sources:
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/answer_agent.yaml:1-29]()

## Agent Interaction Flow

The interaction between agents follows a specific flow, with decision points determining which agents are invoked:

```mermaid
sequenceDiagram
    participant User
    participant UMRA as User Message Rewrite Agent
    participant SQCA as SQL Query Cache Agent
    participant SSA as Schema Selection Agent
    participant DSQGA as Disambiguation and SQL Query Generation Agent
    participant SQCORA as SQL Query Correction Agent
    participant DB as Database
    participant AA as Answer Agent
    
    User->>UMRA: Natural language question
    UMRA->>UMRA: Preprocess and decompose complex queries
    
    alt Query Requires SQL
        UMRA->>SQCA: Processed question
        
        alt Cache Enabled and Hit
            SQCA->>AA: Cached query results
        else Cache Miss or Disabled
            SQCA->>SSA: Forward for schema selection
            SSA->>SSA: Identify relevant entities and filters
            SSA->>SSA: Retrieve schemas and column values
            SSA->>DSQGA: Question with schemas and column data
            
            alt Disambiguation Required
                DSQGA->>User: Disambiguation request
                User->>DSQGA: Clarification response
            end
            
            DSQGA->>SQCORA: Generated SQL query
            SQCORA->>SQCORA: Convert to engine-specific SQL
            SQCORA->>DB: Execute validated SQL query
            DB->>SQCORA: Raw query results
            SQCORA->>AA: Structured query results
        end
    else Query Doesn't Require SQL
        UMRA->>AA: Direct question (system capabilities)
    end
    
    AA->>User: Formatted answer
```

*Diagram: Agent Interaction Sequence*

The sequence shows the complete flow from user question to final answer, including:
1. Initial query preprocessing and decomposition
2. Cache checking for previously answered similar questions
3. Schema selection for relevant database tables and columns
4. Disambiguation when the user's intent is unclear
5. SQL generation, correction, and execution
6. Answer formulation based on query results

Sources:
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/user_message_rewrite_agent.yaml:1-182]()
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/custom_agents/sql_schema_selection_agent.py:1-99]()
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/custom_agents/sql_query_cache_agent.py:1-43]()
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/disambiguation_and_sql_query_generation_agent.yaml:1-278]()
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/sql_query_correction_agent.yaml:1-132]()
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/answer_agent.yaml:1-29]()

## Integration with AI Services

The agents in the Text-to-SQL system interact with various AI services, primarily through the OpenAI and AI Search connectors:

| Agent | AI Service Integrations | Tools/Connectors |
|-------|-------------------------|-----------------|
| User Message Rewrite Agent | OpenAI (GPT-4o-mini) | - |
| Schema Selection Agent | OpenAI (GPT-4o-mini), Azure AI Search | `AISearchConnector`, `ConnectorFactory` |
| SQL Query Cache Agent | Azure AI Search | `ConnectorFactory` |
| Disambiguation and SQL Query Generation Agent | OpenAI (GPT-4o-mini) | `sql_get_entity_schemas_tool` |
| SQL Query Correction Agent | OpenAI (GPT-4o-mini) | `sql_query_execution_tool`, `sql_get_entity_schemas_tool`, `sql_get_column_values_tool` |
| Answer Agent | OpenAI (GPT-4o-mini) | - |

The AI Search connector provides critical functionality for both schema retrieval and column value lookups:

```mermaid
flowchart TD
    Agent["Schema Selection Agent"] -->|"get_entity_schemas()"| AISearchConnector["AISearchConnector"]
    Agent -->|"get_column_values()"| AISearchConnector
    
    AISearchConnector -->|"run_ai_search_query()"| AzureAISearch[(Azure AI Search)]
    AISearchConnector -->|"run_embedding_request()"| OpenAIConnector["OpenAIConnector"]
    
    AzureAISearch --> SchemaIdx["Schema Store Index"]
    AzureAISearch --> ColumnIdx["Column Value Store"]
    AzureAISearch --> QueryIdx["Query Cache Index"]
    
    OpenAIConnector -->|"run_completion_request()"| Azure4o["Azure OpenAI (4o-mini)"]
```

*Diagram: AI Service Integration*

The `AISearchConnector` class offers these key methods:

1. `get_entity_schemas`: Retrieves database schema information based on natural language text
   ```python
   async def get_entity_schemas(
       self,
       text: str,
       excluded_entities: list[str] = [],
       engine_specific_fields: list[DatabaseEngineSpecificFields] = [],
   ) -> str:
       # Performs semantic and vector search to find schemas
       schemas = await self.run_ai_search_query(...)
       # Returns filtered schemas based on relevance
   ```

2. `get_column_values`: Retrieves sample column values to assist with query generation
   ```python
   async def get_column_values(self, text: str):
       # Adds tildes for fuzzy search
       text = " ".join([f"{word}~" for word in text.split()])
       # Gets column values from AI Search
       values = await self.run_ai_search_query(...)
       return values
   ```

Sources:
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/ai_search.py:107-141]()
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/ai_search.py:142-232]()
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/open_ai.py:30-76]()
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/disambiguation_and_sql_query_generation_agent.yaml:279-281]()
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/prompts/sql_query_correction_agent.yaml:132-136]()

## Agent Output Structures

The agents use structured outputs to ensure consistent communication between components:

| Agent | Output Structure | Key Fields |
|-------|------------------|------------|
| User Message Rewrite Agent | `UserMessageRewriteAgentOutput` | `steps`, `requires_sql_queries` |
| Schema Selection Agent | `SQLSchemaSelectionAgentOutput` | `entities`, `filter_conditions` |
| SQL Query Cache Agent | Dictionary | `cached_sql_queries_with_schemas_from_cache`, `contains_cached_sql_queries_with_schemas_from_cache_database_results` |
| Answer Agent | `AnswerAgentOutput` | `answer` |
| Answer With Follow-Up Agent | `AnswerWithFollowUpSuggestionsAgentOutput` | `answer`, `follow_up_suggestions` |

Sources:
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/structured_outputs/__init__.py:1-20]()
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/structured_outputs/answer_with_follow_up_suggestions_agent.py:1-11]()

---

# Page: Data Dictionary

# Data Dictionary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deploy_ai_search_indexes/README.md](deploy_ai_search_indexes/README.md)
- [text_2_sql/data_dictionary/README.md](text_2_sql/data_dictionary/README.md)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/cli.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/cli.py)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/data_dictionary_creator.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/data_dictionary_creator.py)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/databricks_data_dictionary_creator.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/databricks_data_dictionary_creator.py)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/snowflake_data_dictionary_creator.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/snowflake_data_dictionary_creator.py)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/tsql_data_dictionary_creator.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/tsql_data_dictionary_creator.py)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/utils/environment.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/utils/environment.py)

</details>



The Data Dictionary component serves as a critical metadata repository for the Text-to-SQL system, providing structured information about database schemas, relationships, and column values to enable accurate natural language to SQL query conversion. This document explains how the data dictionary is created, maintained, and utilized in the Text-to-SQL system.

For information about the broader Text-to-SQL system architecture, see [Text-to-SQL System](#2).

## Overview

The Data Dictionary is a fundamental component that powers the knowledge of Large Language Models (LLMs) in the Text-to-SQL system. Rather than having the LLM query the database at runtime to discover schema information, storing this metadata in structured files reduces system latency and allows for metadata enhancement through prompt engineering.

The Data Dictionary consists of two primary components:
1. **Schema Store** - JSON files containing metadata about database tables/views, columns, and relationships
2. **Column Value Store** - JSONL files containing dimension table values to provide context for user queries

```mermaid
graph TD
    subgraph "Natural Language Space"
        UserQuery["User Query: 'Show me sales for product VE-C304-S'"]
    end
    
    subgraph "Data Dictionary Components"
        DataDictionaryCreator["DataDictionaryCreator"]
        SchemaStore["Schema Store (EntityItem objects)"]
        ColumnValueStore["Column Value Store JSONL"]
        
        Database[(Database)] --> |"extract_entities_with_definitions()"| DataDictionaryCreator
        Database --> |"extract_entity_relationships()"| DataDictionaryCreator
        DataDictionaryCreator --> |"create_data_dictionary()"| SchemaStore
        DataDictionaryCreator --> |"extract_column_distinct_values()"| ColumnValueStore
    end
    
    subgraph "AI Search Indexes"
        SchemaIndex["SchemaStore Index"]
        ValueIndex["ColumnStore Index"]
        
        SchemaStore --> |"Text2SQLSchemaStoreAISearch"| SchemaIndex
        ColumnValueStore --> |"Text2SQLColumnValueStoreAISearch"| ValueIndex
    end
    
    subgraph "SQL Generation Space"
        SchemaAgent["SchemaAgent"]
        SQLGenAgent["SQLGenAgent"]
        SQLQuery["SQL Query"]
        
        SchemaAgent --> |"Selected Schemas"| SQLGenAgent
        SQLGenAgent --> SQLQuery
        SQLQuery --> |"Execution"| Database
    end
    
    UserQuery --> |"Question"| SchemaAgent
    SchemaAgent --> |"Vector Search"| SchemaIndex
    SchemaAgent --> |"Value Lookup"| ValueIndex
    Database --> |"Results"| UserQuery
```

Sources: [text_2_sql/data_dictionary/README.md:1-5](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/data_dictionary_creator.py:226-250]()

## Data Dictionary Structure

### Schema Store JSON

The Schema Store contains detailed metadata about database tables and views in JSON format. Each entity (table or view) is represented as a JSON object with comprehensive information about its structure and relationships.

Key components of a Schema Store entry include:

| Property | Description |
|----------|-------------|
| Entity | The actual name of the table/view used in SQL queries |
| EntityName | A human-readable name for the entity |
| Definition | A comprehensive description of what information the entity contains |
| Schema | The database schema the entity belongs to |
| Database | The database the entity belongs to |
| FQN | Fully Qualified Name of the entity |
| Columns | Array of column definitions with name, data type, definition, and sample values |
| EntityRelationships | Mapping of immediate relationships to other entities with foreign key details |
| CompleteEntityRelationshipsGraph | Directed graph showing how this entity relates to all others |

Here's a diagram illustrating the structure of a Schema Store entry:

```mermaid
classDiagram
    class EntityItem {
        String Entity
        String EntityName
        String Definition
        String Schema
        String Database
        String FQN
        Array Columns
        Array EntityRelationships
        Array CompleteEntityRelationshipsGraph
    }
    
    class ColumnItem {
        String Name
        String DataType
        String Definition
        Array SampleValues
        Array AllowedValues
    }
    
    class EntityRelationship {
        String ForeignEntity
        String ForeignSchema
        Array ForeignKeys
        String ForeignDatabase
        String FQN
        String ForeignFQN
    }
    
    class ForeignKeyRelationship {
        String Column
        String ForeignColumn
    }
    
    EntityItem "1" --> "*" ColumnItem: contains
    EntityItem "1" --> "*" EntityRelationship: has
    EntityRelationship "1" --> "*" ForeignKeyRelationship: contains
```

Sources: [text_2_sql/data_dictionary/README.md:3-160](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/data_dictionary_creator.py:125-194]()

### Column Value Store JSONL

The Column Value Store contains dimension table values in JSONL format. This helps the LLM understand the context of user questions by providing a searchable index of string-based values in the database.

Each line in the Column Value Store represents a single value in a dimension table column:

```
{"Entity": "Product", "Schema": "SalesLT", "Database": "text2sql-adventure-works", "FQN": "text2sql-adventure-works.SalesLT.Product.ProductNumber", "Column": "ProductNumber", "Value": "WB-H098", "Synonyms": []}
```

The Column Value Store is particularly useful for identifying specific values mentioned in user queries. For example, if a user asks "What are the total sales for VE-C304-S?", the system can use the Column Value Store to determine that "VE-C304-S" is a Product Number in the Product entity.

Sources: [text_2_sql/data_dictionary/README.md:177-202]()

## Automatic Generation

Manually creating a Data Dictionary is time-consuming. The Text-to-SQL system provides utilities to automatically generate the Data Dictionary from database metadata using a combination of SQL queries and LLM-powered descriptions.

```mermaid
flowchart TD
    subgraph "Data Dictionary Creation Process"
        Start([Start]) --> ConfigEnv["Configure Environment Variables"]
        ConfigEnv --> SelectCreator["Select Database-Specific Creator"]
        SelectCreator --> ExtractEntities["Extract Entities with Definitions"]
        ExtractEntities --> ExtractRelationships["Extract Entity Relationships"]
        ExtractRelationships --> BuildGraph["Build Entity Relationship Graph"]
        BuildGraph --> ProcessEntities["Process Each Entity"]
        
        subgraph "Process Entity"
            ExtractColumns["Extract Columns with Definitions"]
            ExtractValues["Extract Distinct Column Values"]
            GenerateDefinitions["Generate LLM-Powered Descriptions"]
            AddRelationships["Add Entity Relationships"]
            WriteToFile["Write Entity to File"]
            
            ExtractColumns --> ExtractValues
            ExtractValues --> GenerateDefinitions
            GenerateDefinitions --> AddRelationships
            AddRelationships --> WriteToFile
        end
        
        ProcessEntities --> WriteDict["Write Complete Data Dictionary"]
        WriteDict --> End([End])
    end
```

The `DataDictionaryCreator` is an abstract base class that provides the core functionality for extracting database metadata. Database-specific implementations are provided for:

- **TSQL**: `TsqlDataDictionaryCreator`
- **Postgres**: `PostgresDataDictionaryCreator`
- **Snowflake**: `SnowflakeDataDictionaryCreator`
- **Databricks**: `DatabricksDataDictionaryCreator`

This class hierarchy enables database-specific SQL queries while maintaining a consistent interface:

```mermaid
classDiagram
    class DataDictionaryCreator {
        <<abstract>>
        -entities: list[str]
        -excluded_entities: list[str]
        -excluded_schemas: list[str]
        -single_file: bool
        -generate_definitions: bool
        +extract_table_entities_sql_query(): str
        +extract_view_entities_sql_query(): str
        +extract_columns_sql_query(entity): str
        +extract_entity_relationships_sql_query(): str
        +create_data_dictionary()
        +extract_entities_with_definitions()
        +extract_entity_relationships()
        +build_entity_relationship_graph()
    }
    
    class TsqlDataDictionaryCreator {
        +extract_table_entities_sql_query(): str
        +extract_view_entities_sql_query(): str
        +extract_columns_sql_query(entity): str
        +extract_entity_relationships_sql_query(): str
    }
    
    class SnowflakeDataDictionaryCreator {
        +extract_table_entities_sql_query(): str
        +extract_view_entities_sql_query(): str
        +extract_columns_sql_query(entity): str
        +extract_entity_relationships_sql_query(): str
    }
    
    class DatabricksDataDictionaryCreator {
        +extract_table_entities_sql_query(): str
        +extract_view_entities_sql_query(): str
        +extract_columns_sql_query(entity): str
        +extract_entity_relationships_sql_query(): str
    }
    
    class PostgresDataDictionaryCreator {
        +extract_table_entities_sql_query(): str
        +extract_view_entities_sql_query(): str
        +extract_columns_sql_query(entity): str
        +extract_entity_relationships_sql_query(): str
    }
    
    DataDictionaryCreator <|-- TsqlDataDictionaryCreator
    DataDictionaryCreator <|-- SnowflakeDataDictionaryCreator
    DataDictionaryCreator <|-- DatabricksDataDictionaryCreator
    DataDictionaryCreator <|-- PostgresDataDictionaryCreator
```

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/data_dictionary_creator.py:226-250](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/tsql_data_dictionary_creator.py:13-32](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/snowflake_data_dictionary_creator.py:14-26](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/databricks_data_dictionary_creator.py:14-26]()

To generate a data dictionary, follow these steps:

1. Configure environment variables in a `.env` file based on the provided `.env.example` template
2. Run the data dictionary creator for your database engine with:
   ```
   uv run data_dictionary <DATABASE_ENGINE>
   ```
3. Optional command line arguments:
   - `--output-directory` or `-o`: Specify the output directory
   - `--single_file` or `-s`: Write all schemas to a single file
   - `--generate_definitions` or `-gen`: Use OpenAI to generate descriptions

For more control, you can directly use the code-based API and specify:
- `entities`: A list of entities to extract
- `excluded_entities`: A list of entities to exclude
- `excluded_schemas`: A list of schemas to exclude

Sources: [text_2_sql/data_dictionary/README.md:208-245](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/cli.py:16-139](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/data_dictionary_creator.py:226-828]()

## Indexing with Azure AI Search

Once the Data Dictionary is generated, it's indexed using Azure AI Search to make it searchable for the Text-to-SQL system. Two primary indexes are created:

1. **Schema Store Index**: Contains the database schema information
2. **Column Value Store Index**: Contains dimension table values

```mermaid
graph TD
    subgraph "Data Dictionary Indexing"
        SchemaStore["Schema Store JSON Files"] --> SchemaIndexer["Text2SQLSchemaStoreAISearch"]
        SchemaIndexer --> SchemaIndex["Schema Store AI Search Index"]
        
        ColumnValueStore["Column Value Store JSONL Files"] --> ValueIndexer["Text2SQLColumnValueStoreAISearch"]
        ValueIndexer --> ValueIndex["Column Value Store AI Search Index"]
        
        QueryCache["Query Cache JSON Files"] --> CacheIndexer["Text2SQLQueryCacheAISearch"]
        CacheIndexer --> CacheIndex["Query Cache AI Search Index"]
    end
    
    subgraph "Deployment Process"
        ConfigEnv["Configure .env File"]
        InstallDeps["Install Dependencies (uv sync)"]
        AdjustIndexer["Adjust Indexer Scripts"]
        RunDeployment["Run deploy.py with Arguments"]
        
        ConfigEnv --> InstallDeps
        InstallDeps --> AdjustIndexer
        AdjustIndexer --> RunDeployment
    end
    
    subgraph "Text2SQL Usage"
        UserQuestion["User Question"] --> Text2SQL["AutoGenText2Sql"]
        Text2SQL <--> |"SchemaAgent: Vector Search"| SchemaIndex
        Text2SQL <--> |"SchemaAgent: Value Lookup"| ValueIndex
        Text2SQL <--> |"QueryCacheAgent: Cache Lookup"| CacheIndex
        Text2SQL --> |"SQLGenAgent: Query Execution"| Database[(Database)]
    end
```

The indexing process is handled by deployment scripts in the `deploy_ai_search_indexes` directory:

- `text_2_sql_schema_store.py`: Deploys the Schema Store index
- `text_2_sql_column_value_store.py`: Deploys the Column Value Store index
- `text_2_sql_query_cache.py`: Deploys the Query Cache index (optional)

The deployment process involves these steps:

1. Configure environment variables in a `.env` file based on the provided `.env.example` template
2. Install dependencies using `uv sync` within the `deploy_ai_search_indexes` directory
3. Adjust the indexer scripts if needed to customize the skills pipeline
4. Run `uv run deploy.py` with appropriate arguments:
   - `index_type`: Specifies which type of index to deploy (e.g., `text_2_sql_schema_store`)
   - `rebuild`: Flag to delete and rebuild the index
   - `suffix`: Optional parameter to apply a suffix to the deployed index and indexer
   - Additional parameters specific to each index type

Sources: [deploy_ai_search_indexes/README.md:26-80]()

Sources: [text_2_sql/data_dictionary/README.md:204-207](), [deploy_ai_search_indexes/README.md:26-60]()

## Schema Selection Process

The Data Dictionary plays a crucial role in the schema selection phase of the Text-to-SQL pipeline. When a user asks a question, the system uses the Data Dictionary to identify the relevant tables and columns needed to construct the SQL query.

```mermaid
sequenceDiagram
    participant User
    participant SchemaAgent as "SchemaAgent"
    participant SchemaStore as "Schema Store Index"
    participant ColumnStore as "Column Value Store Index"
    participant SQLGenAgent as "SQLGenAgent"
    participant CorrectionAgent as "CorrectionAgent"
    participant Database as "Database"
    
    User->>SchemaAgent: "What are the sales for product VE-C304-S?"
    
    SchemaAgent->>SchemaStore: "schema_store.search(query)"
    SchemaStore-->>SchemaAgent: EntityItem objects
    
    SchemaAgent->>ColumnStore: "column_store.search('VE-C304-S')"
    ColumnStore-->>SchemaAgent: "ProductNumber in Product table"
    
    SchemaAgent->>SchemaAgent: "select_schemas()"
    
    SchemaAgent->>SQLGenAgent: Selected schemas
    SQLGenAgent->>CorrectionAgent: Generated SQL
    CorrectionAgent->>Database: Validated SQL
    Database-->>User: Results
```

Sources: [text_2_sql/data_dictionary/README.md:177-196]()

The Schema Selection Agent uses:
1. **Vector/Semantic Search**: To find relevant entities and columns based on the question semantics
2. **Value Recognition**: To identify specific values mentioned in the question and map them to database columns
3. **Relationship Analysis**: To understand how to join tables based on the entity relationships in the Data Dictionary

This two-step approach (schema selection followed by SQL generation) allows the system to focus the LLM's attention on relevant database objects, significantly improving accuracy and reducing hallucinations.

Sources: [text_2_sql/data_dictionary/README.md:5-6]()

## Impact on Query Accuracy

The quality and completeness of the Data Dictionary directly influences the accuracy of the Text-to-SQL system. Well-defined and comprehensive metadata helps the LLM:

1. **Select the correct tables and columns**: Accurate definitions help the system understand what data is available
2. **Interpret data correctly**: Sample values and data types guide the system in formulating correct WHERE clauses
3. **Create proper joins**: Entity relationship information ensures correct table joining
4. **Handle ambiguity**: Detailed definitions help resolve ambiguous terms in user questions

For example, if a column definition explains that a "status" field contains values like "active," "pending," or "cancelled" and describes what each means, the LLM can correctly map natural language references like "completed orders" to the appropriate SQL filter condition.

Sources: [text_2_sql/data_dictionary/README.md:173-175]()

## Conclusion

The Data Dictionary is a foundational component of the Text-to-SQL system that bridges the gap between natural language and database schema. By providing rich metadata about the database structure, it enables the LLM to accurately translate user questions into SQL queries.

The automated generation capabilities make it practical to implement even with large and complex databases, while the integration with Azure AI Search provides efficient retrieval of relevant schema information during query generation.

For teams implementing this system, investing time in refining the Data Dictionary definitions and ensuring comprehensive coverage of all relevant tables will yield significant improvements in query accuracy and system performance.

---

# Page: Database Connectors

# Database Connectors

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [text_2_sql/autogen/src/autogen_text_2_sql/custom_agents/parallel_query_solving_agent.py](text_2_sql/autogen/src/autogen_text_2_sql/custom_agents/parallel_query_solving_agent.py)
- [text_2_sql/autogen/src/autogen_text_2_sql/inner_autogen_text_2_sql.py](text_2_sql/autogen/src/autogen_text_2_sql/inner_autogen_text_2_sql.py)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/databricks_sql.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/databricks_sql.py)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/snowflake_sql.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/snowflake_sql.py)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sql.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sql.py)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/tsql_sql.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/tsql_sql.py)

</details>



## Purpose and Scope

This document details the database connector architecture in the Text-to-SQL system. The connector framework provides a standardized interface for interacting with various database engines while encapsulating database-specific logic. The architecture enables the Text-to-SQL system to execute SQL queries against different database backends without modifying the core query generation logic.

For information about how SQL queries are generated, see [SQL Query Generation and Execution](#2.5).

## Connector Architecture Overview

The database connector architecture follows an object-oriented design with an abstract base class and concrete implementations for specific database engines. This approach allows for consistent interface while accommodating the unique syntax and features of each database platform.

```mermaid
classDiagram
    class SqlConnector {
        <<abstract>>
        +engine_specific_rules(): str
        +invalid_identifiers(): list[str]
        +engine_specific_fields(): list[str]
        +query_execution(sql_query: str): list[dict]
        +sanitize_identifier(identifier: str): str
        +get_entity_schemas(text: str): str
        +query_validation(sql_query: str): tuple
        +clean_query(sql_query: str): str
    }
    
    class TsqlSqlConnector {
        +engine_specific_rules(): str
        +invalid_identifiers(): list[str]
        +engine_specific_fields(): list[str]
        +sanitize_identifier(identifier: str): str
        +query_execution(sql_query: str): list[dict]
        +get_entity_schemas(text: str): str
    }
    
    class SnowflakeSqlConnector {
        +engine_specific_rules(): str
        +invalid_identifiers(): list[str]
        +engine_specific_fields(): list[str]
        +sanitize_identifier(identifier: str): str
        +query_execution(sql_query: str): list[dict]
        +get_entity_schemas(text: str): str
    }
    
    class DatabricksSqlConnector {
        +engine_specific_rules(): str
        +invalid_identifiers(): list[str]
        +engine_specific_fields(): list[str]
        +sanitize_identifier(identifier: str): str
        +query_execution(sql_query: str): list[dict]
        +get_entity_schemas(text: str): str
    }
    
    class ConnectorFactory {
        +get_connector(database_engine: DatabaseEngine): SqlConnector
        +get_ai_search_connector(): AISearchConnector
    }
    
    SqlConnector <|-- TsqlSqlConnector
    SqlConnector <|-- SnowflakeSqlConnector
    SqlConnector <|-- DatabricksSqlConnector
    ConnectorFactory ..> SqlConnector : creates
    
    note for SqlConnector "Abstract base class that defines\nthe interface for all connectors"
    note for ConnectorFactory "Creates appropriate connector\nbased on configured database engine"
```

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sql.py:17-427](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/tsql_sql.py:13-158](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/snowflake_sql.py:14-192](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/databricks_sql.py:14-171]()

## Integration with Text-to-SQL Flow

The database connectors are integrated into the Text-to-SQL system's execution flow, serving as the bridge between the SQL queries generated by LLM agents and the actual database engines.

```mermaid
sequenceDiagram
    participant User as "User"
    participant AutoGenT2S as "AutoGenText2SQL"
    participant SchemaAgent as "SQL Schema Selection Agent"
    participant GenAgent as "SQL Query Generation Agent"
    participant CorrAgent as "SQL Query Correction Agent"
    participant Factory as "ConnectorFactory"
    participant SqlConn as "SqlConnector Instance"
    participant DB as "Database Engine"
    
    User->>AutoGenT2S: Natural language question
    AutoGenT2S->>SchemaAgent: Request relevant schemas
    SchemaAgent->>Factory: Get connector
    Factory->>SqlConn: Create appropriate connector
    SchemaAgent->>SqlConn: get_entity_schemas()
    SqlConn->>DB: Retrieve schema information
    DB->>SqlConn: Schema data
    SqlConn->>SchemaAgent: Formatted schema information
    SchemaAgent->>GenAgent: Provide schemas for query generation
    GenAgent->>CorrAgent: Generated SQL query
    CorrAgent->>SqlConn: query_validation()
    SqlConn->>CorrAgent: Validation results
    CorrAgent->>SqlConn: query_execution()
    SqlConn->>DB: Execute SQL query
    DB->>SqlConn: Query results
    SqlConn->>CorrAgent: Formatted results
    CorrAgent->>AutoGenT2S: Prepared answer
    AutoGenT2S->>User: Natural language answer
```

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/inner_autogen_text_2_sql.py:40-183](), [text_2_sql/autogen/src/autogen_text_2_sql/custom_agents/parallel_query_solving_agent.py:41-301]()

## Base SqlConnector

The `SqlConnector` is an abstract base class that defines the common interface for all database connectors. It handles cross-cutting concerns like:

1. Feature flag management
2. Query validation and sanitization
3. Result formatting
4. AI Search integration
5. Row limit enforcement
6. Column value retrieval

```python
class SqlConnector(ABC):
    # Abstract methods that must be implemented by specific connectors
    @abstractmethod
    def engine_specific_rules(self) -> str:
        """Get the engine specific rules."""
        
    @abstractmethod
    def invalid_identifiers(self) -> list[str]:
        """Get the invalid identifiers upon which a sql query is rejected."""
        
    @abstractmethod
    def engine_specific_fields(self) -> list[str]:
        """Get the engine specific fields."""
        
    @abstractmethod
    def sanitize_identifier(self, identifier: str) -> str:
        """Sanitize the identifier to ensure it is valid."""
        
    @abstractmethod
    async def query_execution(
        self,
        sql_query: str,
        cast_to: any = None,
        limit=None,
    ) -> list[dict]:
        """Run the SQL query against the database."""
        
    @abstractmethod
    async def get_entity_schemas(
        self,
        text: str,
        excluded_entities: list[str] = [],
        as_json: bool = True,
    ) -> str:
        """Gets the schema of views or tables based on semantic search."""
```

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sql.py:17-88](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sql.py:152-173]()

### Common Query Functionality

The base class implements several methods for query handling:

1. `clean_query`: Standardizes query formatting and sanitizes identifiers
2. `query_validation`: Validates SQL syntax and prevents unsafe operations
3. `query_execution_with_limit`: Executes queries with row limits
4. `get_column_values`: Retrieves column values through AI Search

The connector also enforces row limits for query results, which can be configured through environment variables.

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sql.py:175-221](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sql.py:223-251](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sql.py:253-344]()

## Database-Specific Connectors

The system implements specialized connectors for various database engines. Each connector handles the unique syntax, connection mechanisms, and query execution for a specific database technology.

### TSQL Connector

The `TsqlSqlConnector` class provides connectivity to Microsoft SQL Server databases. It uses the `aioodbc` library for asynchronous database connections.

Key implementation details:
- Sanitizes identifiers with square brackets (`[identifier]`)
- Uses TOP instead of LIMIT for row limiting
- Connects using an ODBC connection string
- Handles T-SQL specific reserved keywords

```python
# TSQL-specific sanitization
def sanitize_identifier(self, identifier: str) -> str:
    return f"[{identifier}]"
```

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/tsql_sql.py:13-158]()

### Snowflake Connector

The `SnowflakeSqlConnector` supports connections to Snowflake databases. It uses the official Snowflake Python connector.

Key implementation details:
- Sanitizes identifiers with double quotes (`"identifier"`)
- Enforces "NULLS LAST" in ORDER BY clauses
- Uses warehouse, database, schema hierarchy
- Handles Snowflake-specific reserved keywords

```python
# Snowflake-specific sanitization
def sanitize_identifier(self, identifier: str) -> str:
    return f'"{identifier}"'
```

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/snowflake_sql.py:14-192]()

### Databricks Connector

The `DatabricksSqlConnector` provides connectivity to Databricks SQL endpoints. It uses the Databricks SQL connector.

Key implementation details:
- Sanitizes identifiers with backticks (`` `identifier` ``)
- Uses catalog, schema, table hierarchy
- Handles Databricks-specific reserved keywords
- Connects using server hostname, HTTP path, and access token

```python
# Databricks-specific sanitization
def sanitize_identifier(self, identifier: str) -> str:
    return f"`{identifier}`"
```

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/databricks_sql.py:14-171]()

## Connector Selection and Factory Pattern

The system uses a factory pattern to create and return the appropriate connector based on the configured database engine. This is implemented through the `ConnectorFactory` class.

```mermaid
flowchart TD
    A["ConnectorFactory.get_connector()"] --> B{Database Engine?}
    B -->|"TSQL"| C["TsqlSqlConnector"]
    B -->|"Snowflake"| D["SnowflakeSqlConnector"]
    B -->|"Databricks"| E["DatabricksSqlConnector"]
    B -->|"Other"| F["Other Connectors..."]
    
    C --> G["Database Connection"]
    D --> G
    E --> G
    F --> G
    
    style A fill:white
    style B fill:white
    style C fill:white
    style D fill:white 
    style E fill:white
    style F fill:white
    style G fill:white
```

The factory is used in various parts of the system to obtain the correct connector:

1. During initialization of the `InnerAutoGenText2Sql` class
2. When the schema selection agent needs to retrieve database metadata
3. For query execution by the correction agent

The connector selection is based on environment variables, specifically `Text2Sql__DatabaseEngine`.

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sql.py:37-39](), [text_2_sql/autogen/src/autogen_text_2_sql/inner_autogen_text_2_sql.py:43]()

## Query Validation and Sanitization

One important aspect of the connector architecture is its query validation and sanitization functionality. This helps prevent SQL injection and execution of unsafe queries.

### Query Validation Process

```mermaid
flowchart TD
    A["Input SQL Query"] --> B["Clean Query"]
    B --> C["Parse with sqlglot"]
    C --> D{"Valid Syntax?"}
    D -->|"No"| E["Return Error"]
    D -->|"Yes"| F["Check for Invalid Identifiers"]
    F --> G{"Contains Invalid\nIdentifiers?"}
    G -->|"Yes"| E
    G -->|"No"| H["Check/Add Row Limit"]
    H --> I["Return Valid Query"]
    
    style A fill:white
    style B fill:white
    style C fill:white
    style D fill:white
    style E fill:white
    style F fill:white
    style G fill:white
    style H fill:white
    style I fill:white
```

The validation process:
1. Cleans the query using `clean_query()`
2. Parses the SQL using sqlglot
3. Checks for invalid/reserved identifiers
4. Ensures a row limit is applied
5. Returns the validated query or error messages

The returned query uses the appropriate dialect syntax for the target database engine.

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sql.py:253-344]()

### Identifier Sanitization

Each database engine has different rules for identifier quoting. The connectors handle this through the `sanitize_identifier` method:

| Database Engine | Quoting Style | Example |
|-----------------|---------------|---------|
| TSQL            | Square brackets | `[column name]` |
| Snowflake       | Double quotes | `"column name"` |
| Databricks      | Backticks | `` `column name` `` |

This sanitization is applied during query cleaning to ensure identifiers with spaces or special characters are properly quoted.

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/tsql_sql.py:68-79](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/snowflake_sql.py:75-86](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/databricks_sql.py:59-70]()

## Integration with AI Search

The connector architecture integrates with Azure AI Search for schema discovery and query caching. This integration is controlled through environment variables and can be disabled if needed.

### Schema Retrieval

When a user asks a question, the system needs to determine which database tables and views are relevant. This is done through the `get_entity_schemas` method, which uses AI Search to perform semantic search against the data dictionary.

```mermaid
sequenceDiagram
    participant Agent as "Schema Selection Agent"
    participant SqlConn as "SqlConnector"
    participant AISearch as "AI Search Connector"
    participant AIIndex as "Schema Store Index"
    
    Agent->>SqlConn: get_entity_schemas("sales information")
    SqlConn->>AISearch: get_entity_schemas()
    AISearch->>AIIndex: Semantic search for "sales information"
    AIIndex->>AISearch: Relevant schema entities
    AISearch->>SqlConn: Schema metadata
    SqlConn->>SqlConn: Format for specific engine
    SqlConn->>Agent: Formatted schema information
```

The retrieved schema information includes table and column metadata formatted specifically for the target database engine.

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sql.py:152-173](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/tsql_sql.py:122-158](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/snowflake_sql.py:148-192](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/databricks_sql.py:133-171]()

### Query Cache Integration

The connectors also integrate with the query cache system, allowing previously executed queries to be reused. This is implemented in the `fetch_sql_queries_with_schemas_from_cache` method.

When enabled, this feature:
1. Searches for similar questions in the cache
2. Retrieves associated SQL queries and schemas
3. Can pre-run cached queries with new parameters
4. Returns both the queries and results

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sql.py:346-427]()

## Using Database Connectors in the Text-to-SQL System

The database connectors are used throughout the Text-to-SQL flow:

1. **Schema Selection**: The Schema Selection Agent uses the connector to retrieve relevant table and column information
2. **Query Generation**: The SQL Generation Agent uses schema information to construct queries
3. **Query Correction**: The Correction Agent validates and executes queries through the connector
4. **Parallel Query Execution**: The Parallel Query Solving Agent executes multiple queries in parallel using the connector

For complex questions that require multiple queries, the system can execute them in parallel using the database connector.

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/custom_agents/parallel_query_solving_agent.py:41-301](), [text_2_sql/autogen/src/autogen_text_2_sql/inner_autogen_text_2_sql.py:40-183]()

## Configuration

The database connectors are configured through environment variables:

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| Text2Sql__DatabaseEngine | Target database engine (TSQL, SNOWFLAKE, DATABRICKS, etc.) | N/A |
| Text2Sql__UseQueryCache | Enable/disable query caching | True |
| Text2Sql__PreRunQueryCache | Enable/disable pre-running cached queries | True |
| Text2Sql__UseColumnValueStore | Enable/disable column value store | True |
| Text2Sql__UseAISearch | Enable/disable AI Search integration | True |
| Text2Sql__RowLimit | Maximum number of rows to return | 100 |

Each specific connector also requires its own connection variables:

- **TSQL**: `Text2Sql__Tsql__ConnectionString`
- **Snowflake**: `Text2Sql__Snowflake__User`, `Text2Sql__Snowflake__Password`, etc.
- **Databricks**: `Text2Sql__Databricks__ServerHostname`, `Text2Sql__Databricks__HttpPath`, etc.

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sql.py:17-41](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/tsql_sql.py:102](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/snowflake_sql.py:111-116](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/databricks_sql.py:95-98]()

---

# Page: SQL Query Generation and Execution

# SQL Query Generation and Execution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [text_2_sql/autogen/src/autogen_text_2_sql/autogen_text_2_sql.py](text_2_sql/autogen/src/autogen_text_2_sql/autogen_text_2_sql.py)
- [text_2_sql/autogen/src/autogen_text_2_sql/custom_agents/parallel_query_solving_agent.py](text_2_sql/autogen/src/autogen_text_2_sql/custom_agents/parallel_query_solving_agent.py)
- [text_2_sql/autogen/src/autogen_text_2_sql/inner_autogen_text_2_sql.py](text_2_sql/autogen/src/autogen_text_2_sql/inner_autogen_text_2_sql.py)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sql.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sql.py)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/payloads/interaction_payloads.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/payloads/interaction_payloads.py)

</details>



This document explains how the Text-to-SQL system generates SQL queries from natural language questions and executes them against various database engines. It covers the query generation process using LLMs, query validation and cleaning, and the execution flow for retrieving database results. For information about database connectors, see [Database Connectors](#2.4). For information about query caching, see [Query Cache](#2.6).

## Query Generation and Execution Overview

The SQL query generation and execution process transforms natural language questions into valid SQL queries, executes them against appropriate databases, and returns formatted results. This process involves two main orchestration classes (`AutoGenText2Sql` and `InnerAutoGenText2Sql`), multiple specialized agents, query validation, and database abstraction to support various SQL dialects.

```mermaid
flowchart TD
    subgraph "User Interaction"
        UserQ["User Question"] --> AutoGenT2S["AutoGenText2Sql"]
    end

    subgraph "High-Level Flow"
        AutoGenT2S --> RewriteAgent["User Message Rewrite Agent"]
        RewriteAgent --> ParallelAgent["ParallelQuerySolvingAgent"]
        ParallelAgent --> AnswerAgent["Answer Agent"]
    end

    subgraph "Per-Query Processing"
        ParallelAgent --> InnerT2S["InnerAutoGenText2Sql"]
        InnerT2S --> CacheAgent["SQL Query Cache Agent"]
        CacheAgent --> SchemaAgent["Schema Selection Agent"]
        SchemaAgent --> GenAgent["SQL Query Generation Agent"]
        GenAgent --> CorrectionAgent["SQL Query Correction Agent"]
    end

    subgraph "SQL Query Execution"
        CorrectionAgent --> |"SQL Query"| Validation["query_validation()"]
        Validation --> Cleaning["clean_query()"]
        Cleaning --> |"Cleaned SQL"| Execution["query_execution()"]
        Execution --> |"Results"| JSONFormatting["Format as JSON"]
    end

    subgraph "Database Connection"
        Execution --> DBConnector["Database-Specific Connector"]
        DBConnector --> Database[("Target Database")]
    end

    JSONFormatting --> ParallelAgent
    ParallelAgent --> |"Collected Results"| AnswerAgent
    AnswerAgent --> |"JSON Response Payload"| UserAnswer["Answer to User"]
```

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/autogen_text_2_sql.py:34-368](), [text_2_sql/autogen/src/autogen_text_2_sql/inner_autogen_text_2_sql.py:40-183]()

## Query Generation Process

The Text-to-SQL system uses a multi-agent architecture to transform natural language questions into SQL queries. The generation process is orchestrated by the `InnerAutoGenText2Sql` class, which manages the flow between specialized agents.

### Agent Orchestration

The system uses a two-level orchestration approach:

1. `AutoGenText2Sql` manages the high-level flow and user interaction
2. `InnerAutoGenText2Sql` handles the detailed SQL generation process for each query

This hierarchical structure enables efficient processing of both simple and complex multi-part questions.

```mermaid
sequenceDiagram
    participant User as "User"
    participant AutoGen as "AutoGenText2Sql"
    participant Rewrite as "User Message Rewrite Agent"
    participant Parallel as "ParallelQuerySolvingAgent"
    participant Inner as "InnerAutoGenText2Sql"
    participant Cache as "SQL Query Cache Agent"
    participant Schema as "Schema Selection Agent"
    participant Gen as "Disambiguation and SQL Gen Agent"
    participant Correction as "SQL Query Correction Agent"
    participant DB as "Database"
    participant Answer as "Answer Agent"
    
    User->>AutoGen: process_user_message(question)
    AutoGen->>Rewrite: Forward question
    Note over Rewrite: Rewrite complex questions into sub-questions
    
    Rewrite->>Parallel: Sequential steps JSON
    
    loop For each sub-question
        Parallel->>Inner: process_user_message(sub-question)
        Inner->>Cache: Check cache for similar questions
        
        Cache->>Schema: Forward for schema selection
        Schema->>Gen: Forward with relevant schemas
        Gen->>Correction: Forward generated SQL
        
        Correction->>DB: Execute SQL query
        DB->>Correction: Return results
        Correction->>Inner: Return formatted results
        Inner->>Parallel: Return results or disambiguation requests
    end
    
    Parallel->>Answer: Combine results into final answer
    Answer->>User: Return formatted response payload
```

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/autogen_text_2_sql.py:277-368](), [text_2_sql/autogen/src/autogen_text_2_sql/inner_autogen_text_2_sql.py:62-183]()

### Agent Selection Process

The system uses two levels of agent selection:

1. **High-Level Selection** in `AutoGenText2Sql` manages the flow between rewriting, parallel processing, and answer generation.
2. **Inner Selection** in `InnerAutoGenText2Sql` manages the detailed SQL generation flow.

#### High-Level Agent Selection
```mermaid
flowchart TD
    User["User Message"] --> Rewrite["user_message_rewrite_agent"]
    Rewrite --> Parallel["parallel_query_solving_agent"]
    Parallel --> Answer{"Use Follow-Up\nSuggestions?"}
    Answer -->|"Yes"| AnswerWithSug["answer_with_follow_up_suggestions_agent"]
    Answer -->|"No"| AnswerAgent["answer_agent"]
```

#### Inner Agent Selection
```mermaid
flowchart TD
    Start["User Question"] --> Cache{"Use Query\nCache?"}
    Cache -->|"Yes"| CacheAgent["sql_query_cache_agent"]
    Cache -->|"No"| SchemaAgent["sql_schema_selection_agent"]
    
    CacheAgent --> SchemaAgent
    SchemaAgent --> DisambigGen["disambiguation_and_sql_query_generation_agent"]
    DisambigGen --> Correction["sql_query_correction_agent"]
    Correction --> End["Return Results"]
```

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/autogen_text_2_sql.py:91-117](), [text_2_sql/autogen/src/autogen_text_2_sql/inner_autogen_text_2_sql.py:114-142]()

### Parallel Query Processing

For complex questions that require multiple SQL queries, the system uses the `ParallelQuerySolvingAgent` to orchestrate parallel processing:

1. The `UserMessageRewriteAgent` first decomposes questions into sequential steps with parallel sub-questions
2. The `ParallelQuerySolvingAgent` processes each sub-question using the full `InnerAutoGenText2Sql` flow
3. Results are collected into a `FilteredParallelMessagesCollection` structure
4. Disambiguation requests are handled before continuing to the next batch of sub-questions
5. Final results are combined and passed to the `AnswerAgent`

```mermaid
flowchart TD
    UserQ["User Question"] --> AutoGenT2S["AutoGenText2Sql"]
    AutoGenT2S --> Rewrite["UserMessageRewriteAgent"]
    Rewrite --> Steps["Sequential Steps JSON"]
    Steps --> Parallel["ParallelQuerySolvingAgent"]
    
    subgraph "Parallel Processing"
        Parallel --> Round1["Process Parallel Round 1"]
        
        Round1 --> SubQ1["Sub-Question 1"]
        Round1 --> SubQ2["Sub-Question 2"]
        Round1 --> SubQN["..."]
        
        SubQ1 --> Inner1["InnerAutoGenText2Sql"]
        SubQ2 --> Inner2["InnerAutoGenText2Sql"]
        SubQN --> InnerN["InnerAutoGenText2Sql"]
    end
    
    Inner1 --> ResultsColl["FilteredParallelMessagesCollection"]
    Inner2 --> ResultsColl
    InnerN --> ResultsColl
    
    ResultsColl --> CheckDisambig{"Disambiguation\nNeeded?"}
    CheckDisambig -->|"Yes"| ReturnDisambig["Return DisambiguationRequestsPayload"]
    CheckDisambig -->|"No"| NextRound{"More Rounds?"}
    
    NextRound -->|"Yes"| Round2["Process Next Round"]
    NextRound -->|"No"| ResultsObj["Return Database Results JSON"]
    
    ResultsObj --> AnswerAgent["Answer Agent"]
    AnswerAgent --> Answer["AnswerWithSourcesPayload"]
```

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/custom_agents/parallel_query_solving_agent.py:41-301](), [text_2_sql/autogen/src/autogen_text_2_sql/autogen_text_2_sql.py:277-305]()

## SQL Query Execution

Once a SQL query is generated, it goes through several processing steps before being executed against the database.

### Query Validation and Cleaning

The `SqlConnector` class provides methods to validate and clean queries before execution:

1. `clean_query()`: Sanitizes identifiers and formats the query
2. `query_validation()`: Parses and validates the SQL syntax
3. Adds row limits to protect against excessive data retrieval
4. Checks for invalid identifiers that might indicate SQL injection attempts

```mermaid
flowchart TD
    Query["Raw SQL Query"] --> Clean["clean_query()"]
    Clean --> Validate["query_validation()"]
    
    Validate --> ParseSQL["Parse with sqlglot"]
    ParseSQL --> CheckIdentifiers["Check for Invalid Identifiers"]
    CheckIdentifiers --> CheckLimit["Check for Existing LIMIT"]
    
    CheckLimit -->|"Has Limit"| ValidateLimit["Validate Limit Value"]
    CheckLimit -->|"No Limit"| AddLimit["Add LIMIT Clause"]
    
    ValidateLimit -->|"Limit ≤ row_limit"| Final["Final SQL Query"]
    ValidateLimit -->|"Limit > row_limit"| AddLimit
    AddLimit --> Final
    
    CheckIdentifiers -->|"Found Invalid"| Error["Return Error"]
```

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sql.py:223-251](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sql.py:253-344]()

### Database Connection Abstraction

The system uses an abstract `SqlConnector` class that defines common functionality, with database-specific implementations:

| Method | Purpose |
|--------|---------|
| `query_execution()` | Execute SQL against the database |
| `sanitize_identifier()` | Handle database-specific identifier rules |
| `get_entity_schemas()` | Retrieve database schema information |
| `query_execution_with_limit()` | Execute with row limit protection |
| `query_validation()` | Validate query syntax and structure |

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sql.py:17-42](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sql.py:68-87]()

### Row Limit Protection

The system enforces row limits to prevent excessive data retrieval:

1. Default limit is defined in environment variables (`Text2Sql__RowLimit`)
2. If a query has no LIMIT clause, one is added automatically
3. If a query has a LIMIT higher than the configured maximum, it's reduced

```mermaid
flowchart TD
    ParseQuery["Parse SQL Query"] --> HasLimit{"Has LIMIT\nClause?"}
    
    HasLimit -->|"Yes"| CheckLimit{"LIMIT ≤\nrow_limit?"}
    HasLimit -->|"No"| AddLimit["Add LIMIT row_limit"]
    
    CheckLimit -->|"Yes"| NoChange["Keep Original LIMIT"]
    CheckLimit -->|"No"| ReplaceLimit["Replace with row_limit"]
    
    NoChange --> FinalQuery["Final SQL Query"]
    ReplaceLimit --> FinalQuery
    AddLimit --> FinalQuery
```

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sql.py:308-337]()

## Integration with AI Search

The system leverages Azure AI Search for retrieving schema information and cached queries.

### Schema and Column Value Retrieval

The system uses AI Search indexes to retrieve relevant schema information and column values:

```mermaid
flowchart TD
    subgraph "Schema Selection"
        Question["User Question"] --> SchemaSearch["get_entity_schemas()"]
        SchemaSearch --> AISearch["AISearchConnector.run_ai_search_query()"]
        AISearch --> SchemaIndex["Schema Store Index"]
        SchemaIndex --> RelevantSchemas["Relevant Schemas"]
    end
    
    subgraph "Column Value Lookup"
        Question --> ColumnSearch["get_column_values()"]
        ColumnSearch --> AISearchCV["AISearchConnector.get_column_values()"]
        AISearchCV --> ColumnIndex["Column Value Store Index"]
        ColumnIndex --> SampleValues["Sample Column Values"]
    end
    
    RelevantSchemas --> QueryGen["SQL Generation"]
    SampleValues --> QueryGen
```

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/ai_search.py:142-232](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sql.py:102-150]()

### Query Cache Integration

The system can use previously cached queries for similar questions:

```mermaid
flowchart TD
    Question["User Question"] --> FetchCache["fetch_sql_queries_with_schemas_from_cache()"]
    FetchCache --> AISearch["AISearchConnector.run_ai_search_query()"]
    AISearch --> CacheIndex["Query Cache Index"]
    
    CacheIndex --> CacheHit{"Cache Hit with\nHigh Score?"}
    CacheHit -->|"Yes"| PreRun{"PreRunQueryCache\nEnabled?"}
    CacheHit -->|"No"| Continue["Continue to Schema Selection"]
    
    PreRun -->|"Yes"| ExecuteQueries["Execute Cached Queries"]
    PreRun -->|"No"| CacheToPrompt["Add Cache to Prompt"]
    
    ExecuteQueries --> ReturnResults["Return Pre-Run Results"]
    CacheToPrompt --> Continue
```

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sql.py:346-427]()

## Response Payloads and Results Formatting

The system uses structured payload types defined in `interaction_payloads.py` to standardize communications:

### SQL Query Results Formatting

During query execution, results are formatted as JSON for consistent internal processing:

| Format Field | Description |
|--------------|-------------|
| `type` | Indicates success or error (e.g., `query_execution_with_limit`) |
| `sql_query` | The executed SQL query |
| `sql_rows` | The query results (for successful queries) |
| `errors` | Error messages (for failed queries) |

### Final Response Payload Types

The final response to the user is structured as one of several payload types:

| Payload Type | Purpose | Key Fields |
|--------------|---------|------------|
| `AnswerWithSourcesPayload` | Final answer with sources | `answer`, `sources` (SQL queries and results), `follow_up_suggestions` |
| `DismabiguationRequestsPayload` | Request user to clarify | `disambiguation_requests` (questions and choices) |
| `ProcessingUpdatePayload` | Processing status updates | `message` (status message) |
| `UserMessagePayload` | Input message with parameters | `user_message`, `injected_parameters` |

```mermaid
flowchart TD
    SQL["SQL Query Results"] --> ParallelAgent["ParallelQuerySolvingAgent"]
    
    ParallelAgent --> CheckType{"Response\nType?"}
    
    CheckType -->|"Database Results"| DBResults["database_results JSON"]
    CheckType -->|"Disambiguation"| DisambigResults["disambiguation_requests JSON"]
    
    DBResults --> AnswerAgent["Answer Agent"]
    DisambigResults --> DisambigPayload["DismabiguationRequestsPayload"]
    
    AnswerAgent --> AnswerPayload["AnswerWithSourcesPayload"]
    
    AnswerPayload --> User["User"]
    DisambigPayload --> User
```

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sql.py:175-221](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/payloads/interaction_payloads.py:56-189](), [text_2_sql/autogen/src/autogen_text_2_sql/autogen_text_2_sql.py:206-275]()

## System Configuration

The SQL query generation and execution system is configurable through environment variables:

| Environment Variable | Purpose | Default |
|----------------------|---------|---------|
| `Text2Sql__UseQueryCache` | Enable/disable query caching | `True` |
| `Text2Sql__PreRunQueryCache` | Execute cached queries automatically | `True` |
| `Text2Sql__UseColumnValueStore` | Enable column value lookup | `True` |
| `Text2Sql__UseAISearch` | Enable AI Search integration | `True` |
| `Text2Sql__RowLimit` | Maximum rows to return | `100` |
| `Text2Sql__DatabaseEngine` | Target database engine | Required |

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sql.py:17-41](), [text_2_sql/autogen/src/autogen_text_2_sql/inner_autogen_text_2_sql.py:42-60]()

---

# Page: Query Cache

# Query Cache

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [text_2_sql/GETTING_STARTED.md](text_2_sql/GETTING_STARTED.md)
- [text_2_sql/README.md](text_2_sql/README.md)
- [text_2_sql/autogen/Iteration 5 - Agentic Vector Based Text2SQL.ipynb](text_2_sql/autogen/Iteration 5 - Agentic Vector Based Text2SQL.ipynb)
- [text_2_sql/autogen/src/autogen_text_2_sql/creators/llm_agent_creator.py](text_2_sql/autogen/src/autogen_text_2_sql/creators/llm_agent_creator.py)
- [text_2_sql/autogen/src/autogen_text_2_sql/custom_agents/sql_query_cache_agent.py](text_2_sql/autogen/src/autogen_text_2_sql/custom_agents/sql_query_cache_agent.py)

</details>



This document details the Query Cache mechanism within the Text-to-SQL system. The Query Cache improves performance and reduces token usage by storing and retrieving previously executed SQL queries for similar natural language questions. For information about database connectivity, see [Database Connectors](#2.4).

## Purpose and Benefits

The Query Cache serves several critical functions in the Text-to-SQL system:

1. **Performance Optimization**: Bypasses expensive LLM-powered schema selection, SQL generation, and verification steps for previously answered questions
2. **Cost Reduction**: Minimizes API calls to LLM services for repetitive questions
3. **Response Time Improvement**: Delivers faster responses by retrieving pre-generated SQL queries
4. **Consistency**: Ensures identical SQL queries for similar questions
5. **Real-time Data Access**: Maintains the ability to get near real-time information by executing cached queries against the latest data

The Query Cache is particularly valuable in production environments where users frequently ask similar or identical questions.

Sources: [text_2_sql/README.md:45-54](), [text_2_sql/README.md:77-83]()

## Architecture Overview

The Query Cache is implemented as an agent (`SqlQueryCacheAgent`) within the agentic architecture of the Text-to-SQL system. It sits between the User Message Rewrite Agent and the Schema Selection Agent in the processing pipeline, allowing for efficient retrieval of previously generated SQL queries.

The architecture diagram below shows how the Query Cache fits into the overall Text-to-SQL system:

```mermaid
flowchart TD
    UserQ["User Question"] --> RewriteAgent["User Message Rewrite Agent"]
    
    RewriteAgent --> CacheAgent["SQL Query Cache Agent"]
    
    CacheAgent --> CacheHit{"Cache Hit?"}
    CacheHit -->|"Yes"| CachedResults["Cached Query Results"]
    CacheHit -->|"No"| SchemaAgent
    
    SchemaAgent["Schema Selection Agent"] --> SQLGenAgent["SQL Query Generation Agent"]
    SQLGenAgent --> CorrectionAgent["SQL Query Correction Agent"]
    CorrectionAgent --> |"SQL Query"| Database[("Database")]
    
    Database --> |"Results"| AnswerAgent["Answer Agent"]
    CachedResults --> AnswerAgent
    
    AnswerAgent --> |"Answer"| User["User"]
    
    %% Cache update path
    CorrectionAgent -.-> |"Store successful query"| UpdateCache["Update Query Cache"]
    UpdateCache -.-> CacheStore[("Query Cache Store")]
```

This architecture enables the "Pre-Fetched Cache Results Path," which provides the quickest answer generation when a user asks a question similar to one that has been previously processed.

Sources: [text_2_sql/README.md:48-56](), [text_2_sql/autogen/src/autogen_text_2_sql/custom_agents/sql_query_cache_agent.py:15-64]()

## Cache Integration with AI Search

The Query Cache leverages Azure AI Search for efficient storage and retrieval of cached queries. This integration enables semantic matching of natural language questions against previously cached queries through vector embeddings.

Unlike a traditional cache that requires exact matches, the vector-based approach allows finding semantically similar questions, making the cache more robust to variations in natural language formulations.

```mermaid
graph TD
    subgraph "Query Cache System"
        UserQ["User Question"] --> Embedding["Vector Embedding"]
        Embedding --> CacheAgent["SqlQueryCacheAgent"]
        
        CacheAgent <--> AISearch["Azure AI Search"]
        AISearch <--> QueryCacheIdx["Query Cache Index"]
        
        CacheAgent --> |"Cache Hit"| CachedSQL["Cached SQL Query"]
        CacheAgent --> |"Cache Miss"| SchemaAgent["Schema Selection Agent"]
        
        CachedSQL --> |"Pre-Run if enabled"| PreRunResults["Up-to-date Results"]
        PreRunResults --> AnswerAgent["Answer Agent"]
    end
    
    subgraph "Cache Population"
        SuccessfulQuery["Successful SQL Query"] --> CacheWriter["Cache Update Process"]
        CacheWriter --> AISearch
    end
```

The diagram illustrates how user questions are converted to vector embeddings, which are then used to search the Query Cache Index for similar questions. If a match is found, the corresponding SQL query is retrieved and optionally executed to get the most up-to-date results.

Sources: [text_2_sql/README.md:45-56](), [text_2_sql/README.md:77-83]()

## SQL Query Cache Agent

The SQL Query Cache Agent is responsible for:

1. Receiving the rewritten user query from the User Message Rewrite Agent
2. Searching the cache index for semantically similar questions
3. Determining if a cache hit occurred
4. Returning either the cached SQL query or indicating a cache miss

The agent is implemented in the `SqlQueryCacheAgent` class which inherits from `BaseChatAgent` in the AutoGen framework.

```mermaid
classDiagram
    class BaseChatAgent {
        +name: string
        +description: string
        +on_messages(messages): Response
        +on_messages_stream(messages): AsyncGenerator
        +on_reset(cancellation_token): None
    }
    
    class SqlQueryCacheAgent {
        +name: "sql_query_cache_agent"
        +description: "An agent that fetches the queries from the cache based on the user message."
        -agent: SqlQueryCacheAgentCustomAgent
        +produced_message_types(): List[type[ChatMessage]]
        +on_messages(messages, cancellation_token): Response
        +on_messages_stream(messages, cancellation_token): AsyncGenerator
        +on_reset(cancellation_token): None
    }
    
    class TextMessage {
        +content: str
        +source: str
    }
    
    BaseChatAgent <|-- SqlQueryCacheAgent
    SqlQueryCacheAgent --> TextMessage : produces
```

The agent processes messages in JSON format containing the user message and injected parameters. It delegates the actual cache lookup to the `SqlQueryCacheAgentCustomAgent` and returns either cached results or an indication that no cache hit was found.

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/custom_agents/sql_query_cache_agent.py:16-64]()

## Configuration Options

The Query Cache can be configured through environment variables:

| Environment Variable | Description | Default |
|----------------------|-------------|---------|
| `Text2Sql__UseQueryCache` | Enables or disables the Query Cache functionality | `True` |
| `Text2Sql__PreRunQueryCache` | Determines if cached queries should be executed before returning results | `True` |

When `Text2Sql__PreRunQueryCache` is enabled, cached SQL queries are executed against the database before returning results, providing the most up-to-date data without regenerating the SQL.

Sources: [text_2_sql/.env.example:5-8]()

## Cache Index Structure

The Query Cache index in Azure AI Search is designed to efficiently store and retrieve questions and their corresponding SQL queries:

```mermaid
graph LR
    subgraph "Query Cache Index Structure"
        Question["Question Field"] 
        QueryText["SQL Query Field"]
        Parameters["Query Parameters"]
        Metadata["Metadata"]
        
        Question --> VectorEmbedding["Vector Embedding"]
        Question --> TextIndex["Text Index"]
        
        VectorEmbedding --> SimilaritySearch["Similarity Search"]
        TextIndex --> KeywordSearch["Keyword Search"]
    end
```

The index contains:
- Original natural language questions
- Generated SQL queries
- Database engine information
- Optional execution results (if pre-cached)
- Metadata for filtering and versioning

Sources: [deploy_ai_search_indexes/README.md:62-80]()

## Deploying the Query Cache Index

To deploy the Query Cache index:

1. Create a `.env` file based on the provided `.env.example`
2. Run the deployment script with appropriate parameters

```bash
uv run deploy.py index_type text_2_sql_query_cache rebuild [suffix] [enable_cache_indexer] [single_cache__file]
```

Where:
- `rebuild`: Whether to delete and rebuild the index
- `suffix`: Optional parameter to apply a suffix to deployed index names
- `enable_cache_indexer`: Optional parameter to enable the query cache indexer (default: False)
- `single_cache__file`: Controls whether to upload a single cache file or multiple files (default: False)

Sources: [deploy_ai_search_indexes/README.md:62-80]()

## Query Cache in Action

The following sequence diagram shows how the Query Cache operates within a complete Text-to-SQL request:

```mermaid
sequenceDiagram
    participant User
    participant AutoGenText2Sql as AutoGenText2Sql
    participant Rewrite as User Message Rewrite Agent
    participant Cache as SQL Query Cache Agent
    participant Schema as Schema Selection Agent
    participant Gen as SQL Generation Agent
    participant Correction as SQL Query Correction Agent
    participant Answer as Answer Agent
    participant DB as Database
    
    User->>AutoGenText2Sql: process_user_message(thread_id, message_payload)
    AutoGenText2Sql->>Rewrite: user_message
    Rewrite->>Rewrite: Reformat question
    Rewrite->>Cache: Send rewritten question with params
    
    Cache->>Cache: process_message(user_message, injected_parameters)
    
    alt Cache Hit
        Cache->>Cache: Retrieve cached SQL query
        
        alt PreRunQueryCache Enabled
            Cache->>DB: Execute cached SQL
            DB->>Cache: Return results
            Cache->>Answer: Forward results
        else PreRunQueryCache Disabled
            Cache->>Answer: Return cached SQL
        end
        
    else Cache Miss
        Cache->>Schema: Forward to schema selection
        Schema->>Schema: Identify relevant schemas
        Schema->>Gen: Forward schemas
        Gen->>Gen: Generate SQL query
        Gen->>Correction: Forward SQL query
        Correction->>DB: Execute and verify query
        DB->>Correction: Return results
        Correction->>Answer: Forward results
        
        note over Correction,DB: Cache is updated with new query
    end
    
    Answer->>Answer: Format response
    Answer->>User: Return answer
```

The diagram illustrates the flow of a user message through the system. The `SqlQueryCacheAgent` checks for cached queries that match the user's question semantically. On a cache hit, it can either execute the query (if pre-run is enabled) or simply return the cached query. On a cache miss, the request is forwarded to the Schema Selection Agent to continue the normal query generation flow.

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/custom_agents/sql_query_cache_agent.py:29-64](), [text_2_sql/autogen/Iteration 5 - Agentic Vector Based Text2SQL.ipynb:107-108]()

## Cache Update Strategy

The Query Cache can be populated using different strategies as described in the repository documentation:

1. **Pre-population**: Run an offline pipeline to generate SQL queries for known expected questions to prevent a 'cold start' problem
2. **Chat History Management Pipeline**: Run a real-time pipeline that logs chat history and analyzes Text2SQL questions to generate cache entries
3. **Positive Indication System**: Only update the cache when a user positively reacts to a question (e.g., thumbs up) or doesn't ask a follow-up question
4. **Always Update**: Add all questions into the cache when asked (implemented in the sample code)

The repository implementation uses the "Always Update" approach by default, but notes that this could lead to poor SQL queries reaching the cache. For production use, one of the other strategies is recommended.

Additionally, the cache can be populated in two ways:

1. **Direct Application Updates**: The application code writes directly to the cache index when successful queries are generated
2. **Indexer-Based Updates**: An optional indexer can be enabled to scan and index cache files from a storage location

The direct application update approach is recommended for most scenarios as it provides immediate cache updates without additional infrastructure requirements.

Sources: [text_2_sql/README.md:77-83]()

## Best Practices

For optimal Query Cache performance:

1. **Normalize Questions**: Use the User Message Rewrite Agent to standardize question formats
2. **Selective Caching**: Only cache successful and verified SQL queries
3. **Version Control**: Include database schema version in cache metadata to invalidate outdated entries
4. **Cache Pruning**: Implement strategies to remove outdated or low-value cache entries
5. **Monitoring**: Track cache hit rates to evaluate effectiveness

Sources: [text_2_sql/.env.example:5-8](), [deploy_ai_search_indexes/README.md:62-80]()

## Related Components

The Query Cache works closely with other components in the Text-to-SQL system:

1. **User Message Rewrite Agent**: Normalizes questions before cache lookup
2. **Schema Selection Agent**: Takes over when cache misses occur
3. **Data Dictionary**: Provides schema information for query generation when cache misses occur
4. **AI Search**: Stores and retrieves cached queries through vector and keyword search

For more information on these components, see [Data Dictionary](#2.3) and [Agentic Architecture](#2.1).

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/custom_agents/sql_query_cache_agent.py:15-64](), [text_2_sql/.env.example:5-8]()

---

# Page: Evaluation

# Evaluation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [text_2_sql/autogen/evaluate_autogen_text2sql.ipynb](text_2_sql/autogen/evaluate_autogen_text2sql.ipynb)
- [text_2_sql/autogen/src/autogen_text_2_sql/evaluation_utils.py](text_2_sql/autogen/src/autogen_text_2_sql/evaluation_utils.py)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sqlite_sql.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sqlite_sql.py)

</details>



This page documents how the Text-to-SQL system is evaluated for performance and accuracy. It provides detailed information about the evaluation methodology, metrics, and process using standardized benchmarks to assess the quality of SQL translation from natural language questions.

## Evaluation Approach Overview

The Text-to-SQL system uses the Spider benchmark, a widely-recognized standard for evaluating text-to-SQL translation capabilities. The evaluation quantitatively measures how accurately the system converts natural language questions into executable SQL queries across diverse database schemas.

```mermaid
flowchart TD
    subgraph "Evaluation Process"
        SpiderData["Spider Dataset"] --> |"Natural Language Questions"| AutoGenText2SQL
        AutoGenText2SQL --> |"Generate SQL"| SQLQuery["Generated SQL"]
        SQLQuery --> SQLiteConn["SQLite SQL Connector"]
        SQLiteConn --> |"Execute"| Database[(Spider SQLite DBs)]
        
        SpiderData --> |"Gold Standard SQL"| EvalScript["Spider Evaluation Script"]
        SQLQuery --> EvalScript
        EvalScript --> |"Calculate Scores"| Metrics["Evaluation Metrics:
        - Exact Match
        - Execution Accuracy"]
    end
```

Sources: [text_2_sql/autogen/evaluate_autogen_text2sql.ipynb:1-37]()

## Spider Benchmark Setup

The Spider benchmark consists of 1,000+ natural language questions mapped to SQL queries across 200+ databases spanning 138 domains. Using this benchmark provides a standardized way to compare the system against other text-to-SQL solutions.

### Required Components

To evaluate the system using Spider, two main components must be set up:

1. **Spider Test Suite Evaluation Scripts**
   - Clone the repository: `https://github.com/taoyds/test-suite-sql-eval`
   - Contains the official evaluation scripts that calculate metrics

2. **Spider Dataset**
   - Contains the following key components:
     - `database/`: Directory with all SQLite databases
     - `tables.json`: Schema information for all databases
     - `dev.json`: Development set with natural language questions and gold SQL queries

Sources: [text_2_sql/autogen/evaluate_autogen_text2sql.ipynb:7-35]()

## Evaluation Implementation

The evaluation system is implemented in the `evaluate_autogen_text2sql.ipynb` notebook, which orchestrates the entire evaluation process.

```mermaid
graph TD
    subgraph "Code Components"
        EvalNotebook["evaluate_autogen_text2sql.ipynb"]
        EvalUtils["evaluation_utils.py"]
        SQLiteConn["sqlite_sql.py"]
    end
    
    subgraph "Evaluation Functions"
        GenerateSQL["generate_sql()"]
        GeneratePred["generate_predictions()"]
        RunEval["run_evaluation()"]
        ExtractSQL["get_final_sql_query()"]
        ExecQuery["query_execution()"]
    end
    
    EvalNotebook --> |"contains"| GenerateSQL
    EvalNotebook --> |"contains"| GeneratePred
    EvalNotebook --> |"contains"| RunEval
    GenerateSQL --> |"calls"| ExtractSQL
    GeneratePred --> |"calls for each question"| GenerateSQL
    SQLiteConn --> |"implements"| ExecQuery
    EvalUtils --> |"provides"| ExtractSQL
    
    RunEval --> |"invokes"| SpiderEval["evaluation.py from Spider Test Suite"]
```

Sources: 
- [text_2_sql/autogen/evaluate_autogen_text2sql.ipynb:52-107]()
- [text_2_sql/autogen/src/autogen_text_2_sql/evaluation_utils.py:1-92]()

### SQL Generation Process

The evaluation process generates SQL queries for Spider test questions using the following steps:

1. Initialize `AutoGenText2Sql` with SQLite-specific syntax rules
2. For each question in the Spider dev set:
   - Set the appropriate database connection string
   - Process the question through `AutoGenText2Sql.process_user_message()`
   - Extract the final SQL query from the results
   - Save the query with its corresponding database ID

This is implemented in the `generate_sql()` and `generate_predictions()` functions:

```python
# Initialize with SQLite-specific rules
sqlite_rules = """
1. Use SQLite syntax
2. Do not use Azure SQL specific functions
3. Use strftime for date/time operations
"""

autogen_text2sql = AutoGenText2Sql(
    engine_specific_rules=sqlite_rules,
    use_case="Evaluating with Spider SQLite databases"
)
```

Sources: 
- [text_2_sql/autogen/evaluate_autogen_text2sql.ipynb:96-107]()
- [text_2_sql/autogen/evaluate_autogen_text2sql.ipynb:114-178]()

### SQL Query Extraction

The `evaluation_utils.py` module contains specialized functions for extracting SQL queries from the system output:

1. `extract_sql_queries_from_results()`: Extracts queries from the structured results dictionary by scanning through the nested results structure and identifying entries containing the `sql_query` key.
2. `extract_sql_queries_from_logs()`: Extracts queries from log output using two regex patterns:
   - Queries found after "Running query against" statements
   - Queries embedded in JSON results with the `sql_query` key
3. `get_final_sql_query()`: Selects the most appropriate query for evaluation by first checking results, then falling back to log extraction if needed.

The system implements specific heuristics to select the optimal query when multiple candidates are generated:

```python
# For questions about unique values, prefer queries with DISTINCT
question_lower = question.lower()
needs_distinct = any(word in question_lower for word in ['different', 'distinct', 'unique', 'all'])

for query in reversed(all_queries):  # Look at queries in reverse order
    if needs_distinct and 'DISTINCT' in query.upper():
        final_query = query
        break
```

This selection logic ensures that queries about uniqueness correctly include the `DISTINCT` keyword, even modifying the query to add it when needed but missing.

Sources:
- [text_2_sql/autogen/src/autogen_text_2_sql/evaluation_utils.py:7-92]()
- [text_2_sql/autogen/evaluate_autogen_text2sql.ipynb:162-178]()

### SQLite Connector for Evaluation

The `SQLiteSqlConnector` class provides the specialized database interface for the evaluation process:

```mermaid
graph TD
    subgraph "SQLiteSqlConnector"
        Init["__init__()"] --> Rules["engine_specific_rules()"]
        Rules --> QueryExec["query_execution()"]
        QueryExec --> Database[("SQLite Database")]
        Init --> GetSchema["get_entity_schemas()"]
        GetSchema --> TablesJSON["tables.json"]
        NormTerm["normalize_term()"] --> TermsMatch["terms_match()"]
        TermsMatch --> FindTables["find_matching_tables()"]
        FindTables --> GetSchema
    end
```

The connector implements:

1. **SQLite-specific rules**: Provides syntax guidelines for generating correct SQLite queries
   ```python
   # Engine-specific rules for SQLite
   def engine_specific_rules(self) -> list[str]:
       return [
           "Use SQLite syntax for queries",
           "Use double quotes for identifiers",
           "Use single quotes for string literals",
           "LIMIT clause comes after ORDER BY",
           # Additional syntax rules...
       ]
   ```

2. **Query execution**: Processes queries against Spider SQLite databases
   - Connects to the database specified in `Text2Sql__Tsql__ConnectionString` environment variable
   - Executes the query and returns results as dictionaries

3. **Schema retrieval**: Accesses schema information from Spider's `tables.json` file
   - Uses `SPIDER_DATA_DIR` environment variable to locate the schema file
   - Matches relevant tables using flexible matching algorithms

4. **Flexible matching**: Implements term normalization and matching rules
   - Removes underscores, spaces, and plurals
   - Performs exact and partial matching of table names
   - Handles compound table names by matching term subsets

This specialized connector allows the Text-to-SQL system to properly interact with Spider's database structure during evaluation.

Sources:
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sqlite_sql.py:15-37]()
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sqlite_sql.py:60-109]()
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sqlite_sql.py:111-167]()
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sqlite_sql.py:169-256]()

## Running the Evaluation

The evaluation process is executed in two main steps:

1. **Generate Predictions**
   ```python
   # Generate predictions for n samples
   await generate_predictions(num_samples=20)  # Process 20 samples (faster for testing)
   # Or generate predictions for the full dataset
   await generate_predictions()  # Process all samples in the dataset
   ```

2. **Run Evaluation Script**
   ```python
   # Run evaluation
   run_evaluation()
   ```

The `generate_predictions()` function:
- Reads natural language questions from the Spider `dev.json` file
- Processes each question through the AutoGenText2SQL system 
- Dynamically updates the database connection for each question
- Saves the generated SQL and gold standard SQL for each question

The `run_evaluation()` function executes the Spider evaluation script with these parameters:
- `--gold`: Path to gold queries file (contains correct SQL queries)
- `--pred`: Path to predictions file (contains system-generated SQL queries)
- `--db`: Path to database directory (contains SQLite databases)
- `--table`: Path to table schemas file (contains database structure information)
- `--etype`: Evaluation type ("all" for both exact match and execution accuracy)
- `--plug_value`: Enable value plugging for comparison (normalizes constant values)
- `--progress_bar_for_each_datapoint`: Show progress for each test case

The evaluation process tracks and reports timing information, making it easy to measure system performance across different sample sizes.

Sources:
- [text_2_sql/autogen/evaluate_autogen_text2sql.ipynb:187-235]()
- [text_2_sql/autogen/evaluate_autogen_text2sql.ipynb:243-296]()
- [text_2_sql/autogen/evaluate_autogen_text2sql.ipynb:284-285]()

## Evaluation Metrics

The Spider evaluation script calculates several metrics to assess system performance:

| Metric | Description |
|--------|-------------|
| **Exact Match** | Percentage of generated queries that match gold queries after normalization |
| **Execution Accuracy** | Percentage of queries that produce correct results when executed |
| **Component Accuracy** | Accuracy for specific SQL components (SELECT, WHERE, GROUP BY, etc.) |
| **Hardness Level** | Performance broken down by query complexity (easy, medium, hard, extra) |

### Interpreting Results

The evaluation results help identify:

1. Overall system accuracy and performance
2. Specific strengths and weaknesses in different SQL components
3. Performance across different types of questions and complexity levels
4. Opportunities for targeted improvements in the system

Sources:
- [text_2_sql/autogen/evaluate_autogen_text2sql.ipynb:265-275]()

## Limitations and Considerations

When evaluating the Text-to-SQL system with Spider, it's important to understand:

1. Spider focuses on cross-domain generalization rather than domain-specific optimization
2. The evaluation is based on academic databases that may differ from real-world enterprise schemas
3. Exact match metrics can be strict and may penalize semantically equivalent queries with different syntax
4. The system is specifically configured for SQLite syntax during evaluation, which may differ from other SQL dialects supported by the system

Sources:
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/sqlite_sql.py:20-35]()
- [text_2_sql/autogen/evaluate_autogen_text2sql.ipynb:96-107]()

---

# Page: Usage Examples

# Usage Examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [text_2_sql/autogen/Iteration 5 - Agentic Vector Based Text2SQL.ipynb](text_2_sql/autogen/Iteration 5 - Agentic Vector Based Text2SQL.ipynb)
- [text_2_sql/autogen/src/autogen_text_2_sql/creators/llm_agent_creator.py](text_2_sql/autogen/src/autogen_text_2_sql/creators/llm_agent_creator.py)
- [text_2_sql/autogen/src/autogen_text_2_sql/custom_agents/sql_query_cache_agent.py](text_2_sql/autogen/src/autogen_text_2_sql/custom_agents/sql_query_cache_agent.py)

</details>



This page provides practical examples of how to use the Text-to-SQL system within the DSToolkit. These examples demonstrate the integration of AutoGen agents with Azure OpenAI to convert natural language questions into SQL queries for database interaction. For information about image processing usage, see [Image Processing System](#3).

## Setting Up the Environment

Before using the Text-to-SQL system, you need to set up your environment with the necessary dependencies.

```mermaid
flowchart TD
    A["Environment Setup"] --> B["Install Dependencies"]
    B --> C["Configure Environment Variables"]
    C --> D["Initialize Text2SQL System"]
    
    B --> B1["Run 'uv sync'"]
    B --> B2["Optional: 'uv sync --extra <DATABASE ENGINE>'"]
    
    C --> C1["Load .env file"]
    
    D --> D1["Create AutoGenText2Sql instance"]
    D --> D2["Specify state store"]
    D --> D3["Define use case"]
```

To set up the environment:

1. Install dependencies by running `uv sync` in the autogen directory
2. For database engines other than TSQL, use `uv sync --extra <DATABASE ENGINE>`
3. Configure environment variables (typically in a .env file)
4. Initialize the Text2SQL system

Sources: [text_2_sql/autogen/Iteration 5 - Agentic Vector Based Text2SQL.ipynb:17-56]()

## Basic Usage Example

The following example demonstrates how to process a simple user query with the Text-to-SQL system:

```mermaid
sequenceDiagram
    participant "User" as U
    participant "AutoGenText2Sql" as AGTS
    participant "InMemoryStateStore" as IMSS
    participant "UserMessageRewriteAgent" as UMRA
    participant "SqlQueryCacheAgent" as SQCA
    participant "SchemaAgent" as SA
    participant "SQLGenAgent" as SGA
    participant "CorrectionAgent" as CA
    participant "AnswerAgent" as AA
    
    U->>AGTS: "process_user_message()"
    Note over AGTS: thread_id="1", message="what are the total sales"
    
    AGTS->>IMSS: "Store conversation state"
    AGTS->>UMRA: "Rewrite user message"
    UMRA-->>AGTS: "Rewritten message"
    
    AGTS->>SQCA: "Check query cache"
    
    alt Cache hit
        SQCA-->>AGTS: "Return cached query results"
    else Cache miss
        SQCA-->>AGTS: "No cached results"
        AGTS->>SA: "Select relevant schema"
        SA-->>AGTS: "Schema information"
        
        AGTS->>SGA: "Generate SQL query"
        SGA-->>AGTS: "Generated SQL query"
        
        AGTS->>CA: "Validate and correct query"
        CA-->>AGTS: "Validated SQL query"
        
        AGTS->>AA: "Format response"
        AA-->>AGTS: "Formatted answer"
    end
    
    AGTS-->>U: "Return response"
```

### Code Example

Here's a simple example of how to use the system:

```python
# Initialize the Text2SQL system
agentic_text_2_sql = AutoGenText2Sql(
    state_store=InMemoryStateStore(), 
    use_case="Analysing sales data"
)

# Process a user message
async for message in agentic_text_2_sql.process_user_message(
    thread_id="1", 
    message_payload=UserMessagePayload(user_message="what are the total sales")
):
    logging.info("Received %s Message from Text2SQL System", message)
```

Sources: [text_2_sql/autogen/Iteration 5 - Agentic Vector Based Text2SQL.ipynb:85-108]()

## Component Interaction During Query Processing

The following diagram illustrates how different components interact when processing a natural language query:

```mermaid
graph TD
    subgraph "Natural Language Space"
        UserQuery["User Query: 'what are the total sales'"]
        Response["Response: Total sales data and explanation"]
    end
    
    subgraph "Code Entity Space"
        AutoGenText2Sql["AutoGenText2Sql Class"]
        UserMessagePayload["UserMessagePayload Class"]
        StateStore["InMemoryStateStore Class"]
        
        subgraph "Agent Pipeline"
            UserMessageRewriteAgent["UserMessageRewriteAgent"]
            SqlQueryCacheAgent["SqlQueryCacheAgent"]
            SchemaAgent["SchemaAgent"]
            SQLGenAgent["SQLGenAgent"]
            CorrectionAgent["CorrectionAgent"]
            AnswerAgent["AnswerAgent"]
        end
        
        subgraph "Database Connection"
            ConnectorFactory["ConnectorFactory"]
            SqlConnector["SqlConnector"]
        end
    end
    
    UserQuery --> AutoGenText2Sql
    AutoGenText2Sql --> UserMessageRewriteAgent
    UserMessageRewriteAgent --> SqlQueryCacheAgent
    SqlQueryCacheAgent --> SchemaAgent
    SchemaAgent --> SQLGenAgent
    SQLGenAgent --> CorrectionAgent
    CorrectionAgent --> AnswerAgent
    SQLGenAgent --> ConnectorFactory
    CorrectionAgent --> ConnectorFactory
    ConnectorFactory --> SqlConnector
    AnswerAgent --> Response
```

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/custom_agents/sql_query_cache_agent.py:1-64](), [text_2_sql/autogen/src/autogen_text_2_sql/creators/llm_agent_creator.py:84-144]()

## Advanced Configuration

The Text-to-SQL system can be configured with various options to customize its behavior.

### Agent Creation and Configuration

Each agent in the Text-to-SQL system can be customized using the `LLMAgentCreator`:

```mermaid
flowchart TD
    subgraph "Agent Creation Process"
        A["LLMAgentCreator.create()"] --> B["Load agent configuration file"]
        B --> C["Get SQL connector"]
        C --> D["Add engine-specific rules"]
        D --> E["Create tools for agent"]
        E --> F["Set up structured output"]
        F --> G["Create AssistantAgent instance"]
        G --> H["Configure model context"]
    end
    
    subgraph "Available Tools"
        T1["sql_query_execution_tool"]
        T2["sql_get_entity_schemas_tool"]
        T3["sql_get_column_values_tool"]
    end
    
    E --> T1
    E --> T2
    E --> T3
```

To create a custom agent, you can use the following approach:

```python
# Create an agent with specific configuration
answer_agent = LLMAgentCreator.create(
    name="answer_agent",
    engine_specific_fields="SQL Server specific rules here"
)
```

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/creators/llm_agent_creator.py:18-144]()

### Available Tools

Agents have access to several tools for interacting with the database:

| Tool Name | Description | Function |
|-----------|-------------|----------|
| `sql_query_execution_tool` | Runs SQL queries against the database | `query_execution_with_limit` |
| `sql_get_entity_schemas_tool` | Retrieves schema information for relevant tables | `get_entity_schemas` |
| `sql_get_column_values_tool` | Gets sample values from columns | `get_column_values` |

Sources: [text_2_sql/autogen/src/autogen_text_2_sql/creators/llm_agent_creator.py:34-60]()

## State Management

The Text-to-SQL system uses a state store to maintain conversation context across interactions. By default, the system uses an `InMemoryStateStore`, but you can implement custom state stores for persistence.

```mermaid
classDiagram
    class StateStore {
        <<interface>>
        +get_state(thread_id: str)
        +set_state(thread_id: str, state: dict)
    }
    
    class InMemoryStateStore {
        -states: dict
        +get_state(thread_id: str)
        +set_state(thread_id: str, state: dict)
    }
    
    class CustomStateStore {
        +get_state(thread_id: str)
        +set_state(thread_id: str, state: dict)
    }
    
    StateStore <|.. InMemoryStateStore
    StateStore <|.. CustomStateStore
```

Example usage with state management:

```python
# Using the default in-memory state store
agentic_text_2_sql = AutoGenText2Sql(
    state_store=InMemoryStateStore(),
    use_case="Analysing sales data"
)

# Process multiple messages in the same thread to maintain context
async for message in agentic_text_2_sql.process_user_message(
    thread_id="conversation_1", 
    message_payload=UserMessagePayload(user_message="what are the total sales")
):
    # Process first response
    pass

# Later, in the same thread
async for message in agentic_text_2_sql.process_user_message(
    thread_id="conversation_1", 
    message_payload=UserMessagePayload(user_message="how does that compare to last year?")
):
    # The system will remember context from the previous question
    pass
```

Sources: [text_2_sql/autogen/Iteration 5 - Agentic Vector Based Text2SQL.ipynb:85-108]()

## Best Practices

When using the Text-to-SQL system, consider the following best practices:

1. **Provide specific use cases** when initializing the system to help it understand the context of questions
2. **Maintain thread IDs** for related questions to leverage conversation history
3. **Use database-specific connectors** for optimal performance with your database engine
4. **Monitor and log responses** to understand system behavior and troubleshoot issues

Example of logging responses:

```python
async for message in agentic_text_2_sql.process_user_message(
    thread_id="1", 
    message_payload=UserMessagePayload(user_message="what are the total sales")
):
    logging.info("Received %s Message from Text2SQL System", message)
    # You can further process or store the message here
```

Sources: [text_2_sql/autogen/Iteration 5 - Agentic Vector Based Text2SQL.ipynb:102-108]()

---

# Page: Image Processing System

# Image Processing System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [image_processing/README.md](image_processing/README.md)
- [image_processing/images/Image Based RAG.png](image_processing/images/Image Based RAG.png)
- [image_processing/src/image_processing/function_app.py](image_processing/src/image_processing/function_app.py)
- [image_processing/src/image_processing/layout_and_figure_merger.py](image_processing/src/image_processing/layout_and_figure_merger.py)
- [image_processing/src/image_processing/requirements.txt](image_processing/src/image_processing/requirements.txt)
- [image_processing/tests/image_processing/test_figure_app.py](image_processing/tests/image_processing/test_figure_app.py)
- [image_processing/tests/image_processing/test_layout_analysis.py](image_processing/tests/image_processing/test_layout_analysis.py)
- [image_processing/tests/image_processing/test_layout_holders.py](image_processing/tests/image_processing/test_layout_holders.py)
- [image_processing/tests/image_processing/test_semantic_text_chunker.py](image_processing/tests/image_processing/test_semantic_text_chunker.py)

</details>



## Purpose and Scope

The Image Processing System is designed to enhance Retrieval-Augmented Generation (RAG) applications by effectively processing documents that contain images, charts, and complex layouts. Traditional document indexing methods often extract only text content or use simple OCR, which works well for simple documents but loses valuable information contained in visual elements like charts and figures.

This system addresses this limitation using a pipeline approach that combines:
- **Layout analysis** using Azure Document Intelligence to extract structured document information
- **Figure analysis** with multi-modal models (GPT-4o-mini) to interpret visual elements
- **Semantic chunking** that preserves the context and meaning of both text and visual content
- **AI Search integration** for effective retrieval in RAG applications

The implementation is built as a series of Azure Functions that can be orchestrated by AI Search to process complex documents, ensuring that information from charts, tables, and figures is preserved during indexing.

This document covers the architecture, components, and implementation details of the Image Processing System within the DSToolkit Text2SQL and Image Processing repository. For information about the Text-to-SQL system, see [Text-to-SQL System](#2).

Sources: image_processing/README.md

## High-Level Architecture

The Image Processing System processes documents through a pipeline of specialized components that work together to extract and understand both textual and visual content.

```mermaid
flowchart TB
    Document["Document with Images"] --> LayoutAnalysis
    
    subgraph "Image Processing Pipeline"
        LayoutAnalysis["Layout Analysis"] --> |"Document Structure"| DocIntelligence["Azure Document Intelligence"]
        DocIntelligence --> |"Layout Information"| ProcessedLayout["Layout with Text and Figures"]
        
        ProcessedLayout --> FigureExtraction["Figure Extraction"]
        FigureExtraction --> |"Extracted Figures"| FigureAnalysis["Figure Analysis"]
        FigureAnalysis --> |"Using GPT-4o-mini"| FigureDescriptions["Figure Descriptions"]
        
        ProcessedLayout --> TextChunking["Semantic Text Chunker"]
        FigureDescriptions --> LayoutFigureMerger["Layout and Figure Merger"]
        TextChunking --> LayoutFigureMerger
        
        LayoutFigureMerger --> MarkUpCleaner["MarkUp Cleaner"]
    end
    
    MarkUpCleaner --> |"Clean Content"| AISearch[(AI Search Indexes)]
    AISearch --> |"Enables"| RAG["RAG Application"]
```

The system is implemented as a series of Azure Functions orchestrated by AI Search to process documents through custom skills. Each component is specialized for a specific task in the document processing pipeline.

Sources: image_processing/README.md, deploy_ai_search_indexes/src/deploy_ai_search_indexes/ai_search.py

## Core Components and Implementation

### Layout Analysis

The Layout Analysis component analyzes document structure using Azure Document Intelligence (ADI) and extracts both textual content and figure information.

```mermaid
classDiagram
    class LayoutAnalysis {
        -page_wise: bool
        -extract_figures: bool
        -record_id: int
        -source: str
        +analyse()
        +analyse_document(file_path)
        +process_figures_from_extracted_content(text_holder)
        +create_page_wise_content()
        +create_page_number_tracking_holder()
        +extract_file_info()
        +download_figure_image(figure_id)
    }
    
    class LayoutHolder {
        +content: str
        +page_number: int
        +page_offsets: int
        +figures: list[FigureHolder]
    }
    
    class FigureHolder {
        +figure_id: str
        +caption: str
        +offset: int
        +length: int
        +page_number: int
        +uri: str
        +description: str
        +data: str
        +markdown()
    }
    
    class PageWiseContentHolder {
        +page_wise_layout: list[LayoutHolder]
    }
    
    class NonPageWiseContentHolder {
        +layout: LayoutHolder
        +page_number_tracking_holders: list[PageNumberTrackingHolder]
    }
    
    class PageNumberTrackingHolder {
        +page_number: int
        +page_content: str
    }
    
    LayoutAnalysis --> LayoutHolder : "creates"
    LayoutHolder --> FigureHolder : "contains"
    LayoutAnalysis --> PageWiseContentHolder : "creates for page_wise=True"
    LayoutAnalysis --> NonPageWiseContentHolder : "creates for page_wise=False"
    NonPageWiseContentHolder --> PageNumberTrackingHolder : "contains"
```

The Layout Analysis process:
1. Takes a document from a specified source (blob storage path)
2. Uses Azure Document Intelligence to analyze document layout
3. Extracts textual content in Markdown format
4. Identifies and extracts figures
5. Stores extracted figures in blob storage
6. Returns structured layout information with content and figure references

The component supports two modes:
- **Page-wise**: Each page is processed as a separate chunk, returning a `PageWiseContentHolder` with multiple `LayoutHolder` objects
- **Non-page-wise**: The entire document is processed as continuous text (for later semantic chunking), returning a `NonPageWiseContentHolder` with a single `LayoutHolder` and `PageNumberTrackingHolder` objects to track page boundaries

Key implementation details:
- The `LayoutAnalysis` class downloads document files from blob storage, sends them to Azure Document Intelligence, processes the results, and handles figure extraction
- Figures are downloaded using the Document Intelligence API and uploaded to blob storage for later retrieval
- Page tracking is preserved to enable mapping content chunks back to their original page location
- Retry logic is implemented for figure downloads to handle transient failures
- `extract_file_info()` parses the blob URL to extract container and file information
- `process_figures_from_extracted_content()` processes figures identified by Azure Document Intelligence

Implementation files:
- `LayoutAnalysis` class in [image_processing/src/image_processing/layout_analysis.py:143-569]()
- `process_layout_analysis` function in [image_processing/src/image_processing/layout_analysis.py:575-613]()
- Data holders in [image_processing/src/image_processing/layout_holders.py:1-74]()

Sources: image_processing/src/image_processing/layout_analysis.py, image_processing/src/image_processing/layout_holders.py, image_processing/tests/image_processing/test_layout_analysis.py

### Figure Analysis

The Figure Analysis component interprets figures and charts extracted during layout analysis using GPT-4o-mini, a multimodal model.

```mermaid
flowchart LR
    ExtractedFigure["FigureHolder object"] --> FigureAnalysis["FigureAnalysis.analyse()"]
    FigureAnalysis --> |"Uses GPT-4o-mini"| OpenAI["OpenAI API"]
    OpenAI --> FigureDescription["Figure Description"]
    FigureDescription --> EnrichedFigure["Updated FigureHolder with Description"]
```

The Figure Analysis process:
1. Takes extracted figures (identified by `FigureId`) as base64-encoded images
2. Sends the figure image to GPT-4o-mini through the OpenAI API
3. Uses a specialized prompt to generate a detailed description of the figure
4. Adds the description to the figure metadata
5. Returns the enriched figure information with updated description

The goal is to generate sufficient context to enable retrieval when users query for information contained in charts or images. Rather than completely describing every aspect of the figure, it focuses on generating a technical analysis that would help with retrieval. The prompt instructs the model to provide:
- An overview of what the figure shows
- Analysis of axes and data representations
- Data interpretation and key insights
- Summary conclusions

The implementation is exposed through the `/figure_analysis` HTTP endpoint in the function app, which delegates to the `FigureAnalysis.analyse()` method. Error handling is implemented to handle failures during image analysis.

Implementation files:
- `FigureAnalysis` class in [image_processing/src/image_processing/figure_analysis.py]()
- `figure_analysis` function in [image_processing/src/image_processing/function_app.py:56-84]()

Sources: image_processing/README.md, image_processing/src/image_processing/function_app.py, image_processing/tests/image_processing/test_figure_app.py

### Semantic Text Chunking

The Semantic Text Chunker divides document content into semantically meaningful chunks for effective retrieval. This component is critical for RAG applications as the quality of chunking directly impacts retrieval performance.

```mermaid
classDiagram
    class SemanticTextChunker {
        -similarity_threshold: float
        -max_chunk_tokens: int
        -min_chunk_tokens: int
        -_nlp_model: spacy.language
        +chunk(text)
        +split_into_sentences(text)
        +group_figures_and_tables_into_sentences(sentences)
        +merge_chunks(sentences, is_table_or_figure_map, forwards_direction)
        +sentence_similarity(text_1, text_2)
        +assign_page_number_to_chunks(chunks, page_number_tracking_holders)
        +clean_new_lines(text)
        +filter_empty_figures(text)
        +remove_figures(text)
        +num_tokens_from_string(text)
    }
    
    class ChunkHolder {
        +mark_up: str
        +sections: list[str]
        +figures: list[FigureHolder]
        +cleaned_text: str
        +page_number: int
    }
    
    class process_semantic_text_chunker {
        <<function>>
    }
    
    SemanticTextChunker --> ChunkHolder : "creates"
    process_semantic_text_chunker --> SemanticTextChunker : "uses"
```

The chunking strategy:
1. Splits text into sentences using spaCy's NLP model
2. Groups sentences that contain figures and tables to maintain context
3. Performs special handling of Markdown elements (headings, tables, etc.)
4. Merges sentences into chunks based on semantic similarity:
   - Forward pass: Groups similar sentences from document start
   - Backward pass: Groups similar sentences from document end
5. Assigns page numbers to chunks based on `PageNumberTrackingHolder` objects

Key parameters (configurable via HTTP headers):
- `similarity_threshold`: Controls sentence similarity threshold for merging (default: 0.8)
- `max_chunk_tokens`: Maximum size of a chunk in tokens (default: 500)
- `min_chunk_tokens`: Minimum size of a chunk in tokens (default: 50)

Implementation details:
- Uses spaCy's `en_core_web_md` model for sentence segmentation
- Employs cosine similarity for comparing sentence embeddings
- Special handling for:
  - Tables and figures to keep them intact in chunks
  - Markdown headings (padding with newlines)
  - HTML comments and empty figures (removal)
  - Special characters and non-English content
- Error handling for empty content and chunking failures
- Page number assignment to preserve source context

The `chunk()` method implements the core algorithm:
1. Preprocesses text (cleaning, removing HTML comments)
2. Splits into sentences
3. Groups tables and figures
4. Merges sentences into semantic chunks
5. Returns a list of `ChunkHolder` objects

Implementation files:
- `SemanticTextChunker` class in [image_processing/src/image_processing/semantic_text_chunker.py:13-549]()
- `process_semantic_text_chunker` function in [image_processing/src/image_processing/semantic_text_chunker.py:552-608]()
- HTTP endpoint in [image_processing/src/image_processing/function_app.py:158-212]()

Sources: image_processing/src/image_processing/semantic_text_chunker.py, image_processing/README.md, image_processing/tests/image_processing/test_semantic_text_chunker.py

### Layout and Figure Merger

The Layout and Figure Merger component combines processed layout information with enriched figure descriptions to create a unified document representation.

```mermaid
flowchart LR
    Layout["LayoutHolder object"] --> Merger["LayoutAndFigureMerger.merge()"]
    FigureList["List of FigureHolder objects"] --> Merger
    Merger --> |"merge_figures_into_layout()"| MergingProcess["Merging Process"]
    MergingProcess --> |"Insert figures"| PositionedFigures["Insert figures at correct offsets"]
    PositionedFigures --> |"Remove irrelevant figures"| FilteredContent["Filter irrelevant content"]
    FilteredContent --> |"Clean HTML comments"| UnifiedContent["Unified LayoutHolder"]
```

This component:
1. Takes a `LayoutHolder` object with the document content
2. Takes a list of `FigureHolder` objects with enriched descriptions
3. Inserts each figure's markdown representation at the correct offset in the content
4. Removes irrelevant figures (marked as "Irrelevant Image")
5. Removes empty figures and HTML comments
6. Preserves document structure while integrating visual element descriptions
7. Returns an updated `LayoutHolder` with the unified content

Key implementation details:
- `insert_figure_description()` method handles the insertion of figure markdown at the correct offset
- Adjusts offsets of subsequent figures as the content length changes during insertion
- Uses regex patterns to clean up the resulting content:
  - `irrelevant_figure_pattern` removes figures marked as irrelevant
  - `empty_or_whitespace_figure_pattern` removes empty figure tags
  - `html_comments_pattern` removes HTML comments
- Error handling for invalid figure offsets or other merging failures

The implementation is exposed through the `/layout_and_figure_merger` HTTP endpoint in the function app, which delegates to the `LayoutAndFigureMerger.merge()` method.

Implementation files:
- `LayoutAndFigureMerger` class in [image_processing/src/image_processing/layout_and_figure_merger.py:10-158]()
- HTTP endpoint in [image_processing/src/image_processing/function_app.py:87-115]()

Sources: image_processing/src/image_processing/function_app.py, image_processing/src/image_processing/layout_and_figure_merger.py, image_processing/README.md

### MarkUp Cleaner

The MarkUp Cleaner prepares processed content for vectorization and indexing, ensuring it's clean, well-structured, and optimized for retrieval.

```mermaid
flowchart LR
    UnifiedContent["ChunkHolder/LayoutHolder object"] --> MarkUpCleaner["MarkUpCleaner.clean()"]
    MarkUpCleaner --> |"extract_headers()"| HeaderExtraction["Extract markdown headers"]
    MarkUpCleaner --> |"extract_figures()"| FigureExtraction["Extract figure content"]
    MarkUpCleaner --> |"clean_text()"| TextCleaning["Clean markup artifacts"]
    HeaderExtraction --> |"final_sections"| Sections["List of section headers"]
    FigureExtraction --> |"final_chunk_figures"| Figures["List of figure details"]
    TextCleaning --> |"final_cleaned_text"| CleanedText["Cleaned text for indexing"]
    UnifiedContent --> |"final_page_number"| PageNumbers["Page number"]
```

The MarkUp Cleaner:
1. Processes the merged content from either `ChunkHolder` or `LayoutHolder` objects
2. Extracts Markdown headers (e.g., `# Heading`) as sections for improved retrieval
3. Extracts figure information from the markup for proper indexing
4. Cleans up remaining markup artifacts:
   - Removes HTML comments
   - Removes table formatting while preserving content
   - Normalizes whitespace
   - Handles special characters
5. Preserves page number information for source attribution
6. Returns a structured output with:
   - `final_cleaned_text`: Clean text for vectorization
   - `final_sections`: List of extracted headers
   - `final_chunk_figures`: List of figures with properties
   - `final_page_number`: Page number for source tracking

Key implementation details:
- `extract_headers()` uses regex to identify and extract Markdown headings
- `extract_figures()` finds and extracts figure content with their attributes
- `clean_text()` removes markup artifacts while preserving content
- Error handling for parsing failures

The implementation is exposed through the `/mark_up_cleaner` HTTP endpoint in the function app, which delegates to the `MarkUpCleaner.clean()` method.

Implementation files:
- `MarkUpCleaner` class in [image_processing/src/image_processing/mark_up_cleaner.py]()
- HTTP endpoint in [image_processing/src/image_processing/function_app.py:118-154]()

Sources: image_processing/src/image_processing/function_app.py, image_processing/README.md, image_processing/tests/image_processing/test_figure_app.py

## Function App Implementation

The Image Processing System is implemented as Azure Functions exposing HTTP endpoints for each processing step, which are then orchestrated by AI Search as custom skills.

```mermaid
classDiagram
    class function_app {
        +layout_analysis(req: HttpRequest)
        +figure_analysis(req: HttpRequest)
        +layout_and_figure_merger(req: HttpRequest)
        +mark_up_cleaner(req: HttpRequest)
        +semantic_text_chunker(req: HttpRequest)
    }
    
    class LayoutAnalysis {
        +analyse()
    }
    
    class FigureAnalysis {
        +analyse()
    }
    
    class LayoutAndFigureMerger {
        +merge()
    }
    
    class MarkUpCleaner {
        +clean()
    }
    
    class SemanticTextChunker {
        +chunk()
    }
    
    function_app --> LayoutAnalysis : "calls"
    function_app --> FigureAnalysis : "calls"
    function_app --> LayoutAndFigureMerger : "calls"
    function_app --> MarkUpCleaner : "calls"
    function_app --> SemanticTextChunker : "calls"
```

Each function endpoint:
1. Processes HTTP requests in the AI Search custom skill format
2. Extracts configuration from headers
3. Delegates processing to specialized component classes
4. Returns results in the expected format

The function app provides the following endpoints:

| Endpoint | Description | Processor Class | Configuration Headers |
|----------|-------------|-----------------|----------------------|
| `/layout_analysis` | Analyzes document layout | `LayoutAnalysis` | `chunk_by_page`, `extract_figures` |
| `/figure_analysis` | Analyzes extracted figures | `FigureAnalysis` | - |
| `/layout_and_figure_merger` | Merges layout and figures | `LayoutAndFigureMerger` | - |
| `/mark_up_cleaner` | Cleans markup for indexing | `MarkUpCleaner` | - |
| `/semantic_text_chunker` | Performs semantic chunking | `SemanticTextChunker` | `similarity_threshold`, `max_chunk_tokens`, `min_chunk_tokens` |

Sources: image_processing/src/image_processing/function_app.py

## AI Search Integration

The Image Processing System integrates with Azure AI Search through custom skills to create enriched document indexes for RAG applications.

```mermaid
flowchart TB
    Document["Document with Images"] --> LayoutAnalysis
    
    subgraph "AI Search Indexing Pipeline"
        LayoutAnalysis["layout_analysis Skill"] --> FigureAnalysis["figure_analysis Skill"]
        FigureAnalysis --> LayoutFigureMerger["layout_and_figure_merger Skill"]
        
        direction LR
        subgraph "Chunking Strategy"
            PageWise["Page-wise Chunking"] 
            Semantic["Semantic Chunking"] --> SemanticChunker["semantic_text_chunker Skill"]
        end
        
        LayoutFigureMerger --> ChunkingStrategy{"Chunking\nStrategy"}
        ChunkingStrategy --> |"Page-wise"| PageWise
        ChunkingStrategy --> |"Semantic"| Semantic
        
        PageWise --> MarkUpCleaner["mark_up_cleaner Skill"]
        SemanticChunker --> MarkUpCleaner
        
        MarkUpCleaner --> VectorSkill["Vector Skill"]
    end
    
    VectorSkill --> |"Embedding"| AISearchIndex[(AI Search Index)]
```

The system supports two main indexing pipelines:

1. **Page-wise Chunking**:
   - Document → Layout Analysis → Figure Analysis → Layout/Figure Merger → MarkUp Cleaner → Vectorization → Indexing

2. **Semantic Chunking**:
   - Document → Layout Analysis → Figure Analysis → Layout/Figure Merger → Semantic Text Chunker → MarkUp Cleaner → Vectorization → Indexing

AI Search orchestrates these pipelines through a skillset that invokes the appropriate function endpoints in sequence.

Key implementation details:
- Custom skill integration in [deploy_ai_search_indexes/src/deploy_ai_search_indexes/ai_search.py:199-560]()
- Skillset deployment in [deploy_ai_search_indexes/src/deploy_ai_search_indexes/ai_search.py:660-680]()

Sources: deploy_ai_search_indexes/src/deploy_ai_search_indexes/ai_search.py, image_processing/README.md

## Processing Workflow

The complete document processing workflow combines all components into a coherent pipeline:

```mermaid
sequenceDiagram
    participant Doc as "Document"
    participant LAFunc as "layout_analysis Function"
    participant LA as "LayoutAnalysis"
    participant ADI as "Azure Document Intelligence"
    participant FAFunc as "figure_analysis Function"
    participant FA as "FigureAnalysis"
    participant GPT as "GPT-4o-mini"
    participant MFunc as "layout_and_figure_merger Function"
    participant M as "LayoutAndFigureMerger"
    participant SCFunc as "semantic_text_chunker Function"
    participant SC as "SemanticTextChunker"
    participant MCFunc as "mark_up_cleaner Function"
    participant MC as "MarkUpCleaner"
    participant AIS as "AI Search"
    
    Doc->>LAFunc: Document path
    LAFunc->>LA: Process document
    LA->>ADI: Analyze document layout
    ADI->>LA: Return layout analysis
    LA->>LA: Extract figures
    LA->>LAFunc: Return layout with figures
    
    LAFunc->>FAFunc: Extracted figures
    FAFunc->>FA: Process figures
    FA->>GPT: Analyze figure content
    GPT->>FA: Return figure descriptions
    FA->>FAFunc: Return enriched figures
    
    LAFunc->>MFunc: Layout information
    FAFunc->>MFunc: Figure descriptions
    MFunc->>M: Merge layout and figures
    M->>MFunc: Return merged content
    
    alt Semantic Chunking
        MFunc->>SCFunc: Merged content
        SCFunc->>SC: Chunk content
        SC->>SCFunc: Return semantic chunks
        SCFunc->>MCFunc: Semantic chunks
    else Page-wise Chunking
        MFunc->>MCFunc: Page-wise content
    end
    
    MCFunc->>MC: Clean content
    MC->>MCFunc: Return cleaned chunks
    MCFunc->>AIS: Clean chunks for indexing
    AIS->>AIS: Generate embeddings
    AIS->>AIS: Index content
```

The choice between page-wise and semantic chunking depends on document characteristics and retrieval requirements:

- **Page-wise Chunking**: Better for documents with natural page boundaries
- **Semantic Chunking**: Better for content where semantic relationships cross page boundaries

Sources: image_processing/README.md, image_processing/src/image_processing/function_app.py

## Performance and Production Considerations

When deploying the Image Processing System in production environments, several important considerations should be kept in mind:

1. **Document Type Quality Variance**:
   - Azure Document Intelligence output quality varies significantly by file type
   - PDF files generally produce richer outputs for figure detection compared to PPTX files
   - Consider pre-converting documents to PDF if figure extraction is critical

2. **Cost Considerations**:
   - Document Intelligence Layout model analysis is computationally expensive
   - GPT-4o-mini analysis of figures adds significant cost per image
   - Consider using selective processing based on document importance
   - For cost-sensitive deployments, consider:
     - Limiting figure extraction to specific document types
     - Implementing filtering to process only relevant figures
     - Batching documents for more efficient processing

3. **Processing Time**:
   - The complete pipeline can be time-intensive, especially with many figures
   - Figure analysis with GPT-4o-mini can take several seconds per image
   - Configure appropriate timeouts in the AI Search skillset and indexer
   - Consider implementing asynchronous processing for large document sets

4. **Storage Requirements**:
   - Extracted figures are stored in blob storage (`container-figures`)
   - Ensure sufficient storage capacity based on expected document volume
   - Implement lifecycle management policies for figure storage

5. **Error Handling**:
   - The system implements retry logic for transient failures (especially for figure downloads)
   - Failed document processing is properly reported to AI Search
   - Metadata updates track processing status on the original documents

Sources: image_processing/README.md, image_processing/src/image_processing/requirements.txt

## Example Output

Here's a simplified example showing how the system processes a document with figures, in this case from the Phi-3 Technical Report:

```
<table>
<caption>Table 1: Comparison results on RepoQA benchmark.</caption>
<tr>
<th>Model</th>
<th>Ctx Size</th>
<th>Python</th>
<th>Average</th>
</tr>
<tr>
<td>gpt-4O-2024-05-13</td>
<td>128k</td>
<td>95</td>
<td>90.6</td>
</tr>
<tr>
<td>Phi-3.5-MoE</td>
<td>128k</td>
<td>89</td>
<td>85</td>
</tr>
</table>

MMLU(5-shot) MultiLingual

Phi-3-mini
Phi-3.5-mini
Phi-3.5-MoE

<!-- FigureContent="**Technical Analysis of Figure 4: Comparison of phi-3-mini, phi-3.5-mini and phi-3.5-MoE on MMLU-Multilingual tasks**

1. **Overview:**
   - The image is a bar chart comparing the performance of three different models on MMLU-Multilingual tasks across various languages.

2. **Axes:**
   - The x-axis represents the languages: Arabic, Chinese, Dutch, French, German, Italian, Russian, Spanish, Ukrainian, Vietnamese, and English.
   - The y-axis represents performance scores from 0 to 90.

3. **Data Interpretation:**
   - Across all languages, the phi-3.5-MoE consistently outperforms the other two models.
   - The phi-3.5-mini shows better performance than phi-3-mini in most languages.

4. **Conclusion:**
   - The phi-3.5-MoE model consistently outperforms the phi-3-mini and phi-3.5-mini models across all MMLU-Multilingual tasks." -->

We evaluate the phi-3.5-mini and phi-3.5-MoE models on two long-context understanding tasks.
As shown in Tables 1 and 2, both phi-3.5-MoE and phi-3.5-mini outperform other open-source models.
```

In this example:
1. The table structure is preserved in Markdown format
2. The figure (a bar chart comparing model performance) has been analyzed
3. The figure description is included as an HTML comment, enabling retrieval of information contained in the chart
4. The original document flow and context are maintained

This enriched representation allows RAG applications to understand and retrieve information from both the textual content and the visual elements in the document.

Sources: image_processing/README.md

---

# Page: Layout Analysis

# Layout Analysis

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deploy_ai_search_indexes/src/deploy_ai_search_indexes/ai_search.py](deploy_ai_search_indexes/src/deploy_ai_search_indexes/ai_search.py)
- [image_processing/README.md](image_processing/README.md)
- [image_processing/images/Image Based RAG.png](image_processing/images/Image Based RAG.png)
- [image_processing/src/image_processing/function_app.py](image_processing/src/image_processing/function_app.py)
- [image_processing/src/image_processing/layout_analysis.py](image_processing/src/image_processing/layout_analysis.py)
- [image_processing/src/image_processing/layout_holders.py](image_processing/src/image_processing/layout_holders.py)
- [image_processing/src/image_processing/semantic_text_chunker.py](image_processing/src/image_processing/semantic_text_chunker.py)
- [image_processing/tests/image_processing/test_figure_app.py](image_processing/tests/image_processing/test_figure_app.py)
- [image_processing/tests/image_processing/test_layout_analysis.py](image_processing/tests/image_processing/test_layout_analysis.py)
- [image_processing/tests/image_processing/test_layout_holders.py](image_processing/tests/image_processing/test_layout_holders.py)
- [image_processing/tests/image_processing/test_semantic_text_chunker.py](image_processing/tests/image_processing/test_semantic_text_chunker.py)

</details>



## Purpose and Scope

This document explains how the Image Processing system analyzes document layout using Azure Document Intelligence (ADI). Layout Analysis is the first critical step in the document processing pipeline, converting complex documents with text, tables, and figures into a structured Markdown format that preserves the original layout while enabling further processing. For information about how extracted text is processed after layout analysis, see [Semantic Text Chunking](#3.2).

## Overview

When processing documents with images and charts, simply extracting text content is insufficient. Layout Analysis addresses this by using Azure Document Intelligence to:

1. Identify document structure (headings, paragraphs, tables)
2. Extract figures and their captions
3. Preserve layout information in Markdown format
4. Track page numbers for elements within the document

This structured output enables downstream processes to understand both the textual content and visual elements, significantly improving RAG application performance for documents with charts and figures.

Sources: [image_processing/README.md:13-27]()

## Architecture

### Layout Analysis in Document Processing Pipeline

```mermaid
flowchart TB
    subgraph "Document Processing Pipeline"
        direction TB
        Document[(Document with Images)]
        
        subgraph "Layout Analysis"
            direction TB
            DocIntel["Azure Document Intelligence"]
            ExtractLayout["Layout Extraction"]
            PageTracking["Page Number Tracking"]
            FigureExtract["Figure Extraction"]
        end
        
        Document --> ExtractLayout
        ExtractLayout --> DocIntel
        DocIntel --> PageTracking
        DocIntel --> FigureExtract
        
        FigureExtract --> FigAnal["Figure Analysis"]
        PageTracking --> TextChunk["Semantic Text Chunking"]
        FigAnal --> Merger["Layout & Figure Merger"]
        TextChunk --> Merger
        
        Merger --> Cleaner["MarkUp Cleaner"]
        Cleaner --> Index[("AI Search Index")]
    end

    class Document document;
    class Index database;
```

Sources: [image_processing/README.md:11-41]()

### Component Architecture

```mermaid
classDiagram
    class LayoutAnalysis {
        -page_wise: bool
        -extract_figures: bool
        -record_id: int
        -source: str
        -result
        -operation_id: str
        +extract_file_info()
        +analyse()
        +analyse_document(file_path)
        +download_figure_image(figure_id)
        +process_figures_from_extracted_content(text_holder)
        +create_page_wise_content()
        +create_page_number_tracking_holder()
        +get_document_intelligence_client()
        +get_storage_account_helper()
    }
    
    class StorageAccountHelper {
        +account_url: str
        +get_client()
        +add_metadata_to_blob(source, container, metadata, upsert)
        +upload_blob(container, blob, data, content_type)
        +download_blob_to_temp_dir(source, container, target_file_name)
    }
    
    class LayoutHolder {
        +content: str
        +page_number: int|None
        +page_offsets: int
        +figures: List[FigureHolder]
    }
    
    class FigureHolder {
        +figure_id: str
        +container: str|None
        +blob: str|None
        +caption: str|None
        +offset: int
        +length: int
        +page_number: int|None
        +uri: str
        +description: str|None
        +data: str|None
        +markdown(): str
    }
    
    class PageWiseContentHolder {
        +page_wise_layout: List[LayoutHolder]
    }
    
    class NonPageWiseContentHolder {
        +layout: LayoutHolder
        +page_number_tracking_holders: List[PageNumberTrackingHolder]
    }
    
    class PageNumberTrackingHolder {
        +page_number: int
        +page_content: str|None
    }
    
    LayoutAnalysis ..> LayoutHolder : creates
    LayoutAnalysis ..> FigureHolder : processes
    LayoutAnalysis ..> PageWiseContentHolder : creates for page-wise mode
    LayoutAnalysis ..> NonPageWiseContentHolder : creates for non-page-wise mode
    LayoutAnalysis ..> PageNumberTrackingHolder : creates
    LayoutAnalysis --> StorageAccountHelper : uses
    PageWiseContentHolder o-- LayoutHolder : contains
    NonPageWiseContentHolder o-- LayoutHolder : contains
    NonPageWiseContentHolder o-- PageNumberTrackingHolder : contains
    LayoutHolder o-- FigureHolder : contains
```

Sources: [image_processing/src/image_processing/layout_analysis.py:143-572](), [image_processing/src/image_processing/layout_holders.py:1-74]()

Sources: [image_processing/src/image_processing/layout_holders.py:1-74]()

## Processing Flow

Layout Analysis processes documents through the following key steps:

### Document Analysis Flow

```mermaid
sequenceDiagram
    participant Client as "AI Search Indexer"
    participant API as "layout_analysis Function"
    participant Process as "process_layout_analysis"
    participant LA as "LayoutAnalysis Class"
    participant SAH as "StorageAccountHelper"
    participant ADI as "Azure Document Intelligence"
    participant Blob as "Azure Blob Storage"

    Client->>API: HTTP POST with source URL
    Note over Client,API: Headers: chunk_by_page, extract_figures
    
    API->>Process: process values with page_wise and extract_figures flags
    Process->>LA: Create LayoutAnalysis instance
    LA->>LA: extract_file_info()
    
    LA->>SAH: get_storage_account_helper()
    LA->>SAH: download_blob_to_temp_dir(blob, container, target_file_name)
    SAH->>Blob: Download blob from source URL
    Blob-->>SAH: Document binary
    SAH-->>LA: temp_file_path, metadata
    
    LA->>LA: get_document_intelligence_client()
    LA->>ADI: begin_analyze_document(model_id="prebuilt-layout", ...)
    Note over LA,ADI: Using DocumentContentFormat.MARKDOWN
    ADI-->>LA: Analysis result and operation_id
    
    alt extract_figures is true
        loop For each figure in result.figures
            LA->>ADI: download_figure_image(figure_id)
            ADI-->>LA: Figure image binary
            LA->>SAH: upload_blob(container, blob, image_data, "image/png")
            SAH->>Blob: Upload figure to figures container
            LA->>LA: Add FigureHolder to text_holder.figures
        end
    end
    
    alt page_wise is true
        LA->>LA: create_page_wise_content()
        LA->>LA: Create PageWiseContentHolder
    else page_wise is false
        LA->>LA: create_page_number_tracking_holder()
        LA->>LA: Create NonPageWiseContentHolder
    end
    
    Note over LA: Handle errors with retry logic
    
    LA-->>Process: Return layout results (with recordId)
    Process-->>API: Return result
    API-->>Client: JSON response with layout data
```

Sources: [image_processing/src/image_processing/layout_analysis.py:458-571](), [image_processing/src/image_processing/layout_analysis.py:575-613](), [image_processing/src/image_processing/function_app.py:18-53]()

Sources: [image_processing/src/image_processing/layout_analysis.py:458-571](), [image_processing/src/image_processing/layout_analysis.py:575-613](), [image_processing/src/image_processing/function_app.py:18-53]()

## Key Components

### HTTP Function Endpoint

The system exposes the layout analysis functionality through an Azure Function HTTP endpoint at `/layout_analysis`. This endpoint accepts document references and configuration parameters and returns the analyzed layout.

```mermaid
flowchart LR
    Client["AI Search Indexer"] -->|"POST /layout_analysis"| Function["layout_analysis Function"]
    Function -->|"Extract request parameters"| Tasks["asyncio.create_task()"]
    Tasks -->|"For each document"| Process["process_layout_analysis()"]
    Process -->|"Create"| LayoutAnalysis["LayoutAnalysis(page_wise, extract_figures)"]
    LayoutAnalysis -->|"analyse()"| Response["Analysis Results"]
    Tasks -->|"asyncio.gather()"| Results["Aggregated Results"]
    Results --> Client
```

The HTTP endpoint processes the following parameters:
- `page_wise` (header): Whether to chunk by page (default: False)
- `extract_figures` (header): Whether to extract figures (default: True)
- Request body: Must contain a JSON object with a `values` array containing document references

Sources: [image_processing/src/image_processing/function_app.py:18-53]()

Sources: [image_processing/src/image_processing/function_app.py:18-53]()

### LayoutAnalysis Class

The `LayoutAnalysis` class is the core component responsible for:

1. Downloading document files from blob storage
2. Interacting with Azure Document Intelligence 
3. Processing figures (when extraction is enabled)
4. Creating layout holders based on the processing mode (page-wise or non-page-wise)

```python
class LayoutAnalysis:
    def __init__(
        self,
        page_wise: bool = False,
        extract_figures: bool = True,
        record_id: int = None,
        source: str = None,
    ):
        # Configuration and state properties
        self.page_wise = page_wise        # Process page-by-page
        self.extract_figures = extract_figures  # Extract figures from document
        self.record_id = record_id        # Unique identifier
        self.source = source              # URL to document
        self.result = None                # ADI analysis result
        self.operation_id = None          # ADI operation ID
```

Key methods:
- `extract_file_info()`: Parses source URL to extract blob and container information
- `analyse()`: Main orchestration method for document analysis
- `analyse_document()`: Sends document to Azure Document Intelligence for analysis
- `download_figure_image()`: Downloads figure images identified by ADI
- `process_figures_from_extracted_content()`: Processes and stores figures
- `create_page_wise_content()`: Creates page-by-page layout holders
- `create_page_number_tracking_holder()`: Creates page tracking information

Sources: [image_processing/src/image_processing/layout_analysis.py:143-195](), [image_processing/src/image_processing/layout_analysis.py:458-571]()

Sources: [image_processing/tests/image_processing/test_layout_analysis.py:117-142]()

### Data Models

The system uses several Pydantic models to represent the layout analysis results:

```mermaid
classDiagram
    class ChunkHolder {
        +mark_up: str
        +sections: list[str]
        +figures: list[FigureHolder]
        +cleaned_text: str|None
        +page_number: int|None
    }
    
    class FigureHolder {
        +figure_id: str
        +container: str|None
        +blob: str|None
        +caption: str|None
        +offset: int
        +length: int
        +page_number: int|None
        +uri: str
        +description: str|None
        +data: str|None
        +markdown(): str
    }
    
    class LayoutHolder {
        +content: str
        +page_number: int|None
        +page_offsets: int
        +figures: list[FigureHolder]
    }
    
    class PageWiseContentHolder {
        +page_wise_layout: list[LayoutHolder]
    }
    
    class NonPageWiseContentHolder {
        +layout: LayoutHolder
        +page_number_tracking_holders: list[PageNumberTrackingHolder]
    }
    
    class PageNumberTrackingHolder {
        +page_number: int
        +page_content: str|None
    }
    
    PageWiseContentHolder o-- LayoutHolder : contains
    NonPageWiseContentHolder o-- LayoutHolder : contains
    NonPageWiseContentHolder o-- PageNumberTrackingHolder : contains
    LayoutHolder o-- FigureHolder : contains
    ChunkHolder o-- FigureHolder : contains
```

| Model | Purpose | Key Properties |
|-------|---------|----------------|
| `LayoutHolder` | Stores document content with optional page information and figures | `content`, `page_number`, `page_offsets`, `figures` |
| `FigureHolder` | Represents an extracted figure with its metadata and content | `figure_id`, `offset`, `length`, `uri`, `caption`, `description`, `data` |
| `PageWiseContentHolder` | Contains multiple layout holders when processing by page | `page_wise_layout` list |
| `NonPageWiseContentHolder` | Contains a single layout holder and page tracking information | `layout`, `page_number_tracking_holders` list |
| `PageNumberTrackingHolder` | Tracks which content belongs to which page | `page_number`, `page_content` |
| `ChunkHolder` | Used in subsequent processing for chunked content | `mark_up`, `page_number`, `figures` |

Sources: [image_processing/src/image_processing/layout_holders.py:1-74]()

Sources: [image_processing/tests/image_processing/test_layout_holders.py:13-106]()

## Figure Processing

When `extract_figures` is enabled, Layout Analysis:

1. Identifies figures within the document using Azure Document Intelligence
2. Downloads each figure image using the Document Intelligence API with built-in retry logic
3. Uploads each figure to a dedicated container in blob storage
4. Creates `FigureHolder` objects with metadata about each figure
5. Preserves figure placement information (offset, length) for later processing

```mermaid
flowchart TD
    ADIResults["ADI Analysis Results"]
    
    subgraph "process_figures_from_extracted_content"
        direction TB
        ExtractFigures["Iterate through result.figures"]
        MatchPage["Match figure to current page (if page_wise)"]
        Download["download_figure_image(figure_id)"]
        Base64["Convert image to base64"]
        Upload["upload_blob to figures container"]
        CreateHolder["Create FigureHolder with metadata"]
        AddToLayout["Add FigureHolder to text_holder.figures"]
    end
    
    ADIResults --> ExtractFigures
    ExtractFigures --> MatchPage
    MatchPage --> Download
    Download --> Base64
    Base64 --> Upload
    Base64 --> CreateHolder
    Upload --> AddToLayout
    CreateHolder --> AddToLayout
```

The method uses `@retry` decorator with exponential backoff to handle transient failures when downloading figure images from Azure Document Intelligence. Each figure is stored in a container named `{original-container}-figures` with a path that preserves its relationship to the original document.

This extracted figure information is passed to Figure Analysis for content interpretation (see [Figure Analysis](#3.3)).

Sources: [image_processing/src/image_processing/layout_analysis.py:179-216](), [image_processing/src/image_processing/layout_analysis.py:217-315]()

Sources: [image_processing/src/image_processing/layout_analysis.py:179-216](), [image_processing/src/image_processing/layout_analysis.py:217-315]()

## Page Mode Processing

### Page-wise Processing

When `page_wise` is set to `true`, the document is processed page by page:

```python
if self.page_wise:
    cleaned_text_holders = []
    page_wise_text_holders = self.create_page_wise_content()
    content_with_figures_tasks = []

    for page_wise_text_holder in page_wise_text_holders:
        if self.extract_figures:
            content_with_figures_tasks.append(
                self.process_figures_from_extracted_content(
                    page_wise_text_holder
                )
            )

        if len(page_wise_text_holder.content) == 0:
            logging.error(
                "No content found in the cleaned result for slide %s.",
                page_wise_text_holder.page_number,
            )
        else:
            cleaned_text_holders.append(page_wise_text_holder)

    if self.extract_figures:
        await asyncio.gather(*content_with_figures_tasks)

    output_record = PageWiseContentHolder(
        page_wise_layout=cleaned_text_holders
    )
```

1. Each page is processed separately and its content is extracted via `create_page_wise_content()`
2. Figures are associated with their respective pages
3. The output is a `PageWiseContentHolder` containing multiple `LayoutHolder` objects (one per page)

This mode is useful for maintaining strict page boundaries and for documents where page context is important.

### Non-page-wise Processing

When `page_wise` is set to `false`, the document is processed as a whole:

```python
else:
    text_content = LayoutHolder(
        content=self.result.content, page_number=None, page_offsets=0
    )

    if self.extract_figures:
        await self.process_figures_from_extracted_content(text_content)

    page_number_tracking_holders = self.create_page_number_tracking_holder()

    output_record = NonPageWiseContentHolder(
        layout=text_content,
        page_number_tracking_holders=page_number_tracking_holders,
    )
```

1. The entire document content is extracted into a single layout holder
2. Page number tracking information is maintained separately through `create_page_number_tracking_holder()`
3. The output is a `NonPageWiseContentHolder` with a single `LayoutHolder` and a list of `PageNumberTrackingHolder` objects

This mode is better for documents where content flows across pages and semantic chunking will be applied later. The `page_number_tracking_holders` list contains information that helps associate content with page numbers even when the content is chunked in later processing.

Sources: [image_processing/src/image_processing/layout_analysis.py:506-547]()

Sources: [image_processing/src/image_processing/layout_analysis.py:506-547]()

## Integration with Other Components

Layout Analysis is the first step in a pipeline that includes:

```mermaid
flowchart TB
    Document[("Document in\nBlob Storage")]
    
    subgraph "AI Search Indexer Pipeline"
        direction TB
        LayoutAnalysis["layout_analysis\nExtract text and figures"]
        FigureAnalysis["figure_analysis\nUnderstand figure content"]
        Merger["layout_and_figure_merger\nCombine text and figures"]
        TextChunker["semantic_text_chunker\nChunk content semantically"]
        MarkUpCleaner["mark_up_cleaner\nPrepare for indexing"]
        
        LayoutAnalysis --> FigureAnalysis
        LayoutAnalysis --> Merger
        FigureAnalysis --> Merger
        Merger --> TextChunker
        TextChunker --> MarkUpCleaner
    end
    
    Document --> LayoutAnalysis
    MarkUpCleaner --> AISearch[("AI Search Index")]
```

1. **Layout Analysis** (`layout_analysis` function):
   - Extracts document structure using Azure Document Intelligence
   - Identifies and extracts figures
   - Creates either page-wise or document-wide layout holders

2. **Figure Analysis** (`figure_analysis` function):
   - Processes figures extracted during layout analysis
   - Uses multimodal models (GPT-4o-mini) to analyze figure content
   - Generates descriptions suitable for retrieval

3. **Layout and Figure Merger** (`layout_and_figure_merger` function):
   - Combines layout information with figure analysis results
   - Integrates figure descriptions into the document content

4. **Semantic Text Chunking** (`semantic_text_chunker` function):
   - Splits text into semantically meaningful chunks
   - Preserves figure and table contexts within chunks
   - Tracks page numbers for each chunk

5. **MarkUp Cleaner** (`mark_up_cleaner` function):
   - Cleans and prepares final content for indexing
   - Extracts sections and headers as additional metadata
   - Formats content for optimal retrieval

This pipeline ensures that both textual and visual elements of documents are properly processed for RAG applications. Each component is implemented as a separate Azure Function endpoint that can be called independently or as part of the AI Search skillset.

Sources: [image_processing/src/image_processing/function_app.py:1-213](), [image_processing/README.md:43-56]()

Sources: [image_processing/README.md:43-56]()

## Usage Example

Layout Analysis transforms complex documents with figures and tables into structured markdown that preserves layout and context. Here's an example from the Phi-3 Technical Report:

### Original Content
A complex page with table, text, and a figure bar chart comparing model performance across languages.

### After Layout Analysis Processing

```
\n<table>\n<caption>Table 1: Comparison results on RepoQA benchmark.</caption>\n<tr>\n<th>Model</th>\n<th>Ctx Size</th>\n<th>Python</th>\n<th>C++</th>\n<th>Rust</th>\n<th>Java</th>\n<th>TypeScript</th>\n<th>Average</th>\n</tr>\n<tr>\n<td>gpt-4O-2024-05-13</td>\n<td>128k</td>\n<td>95</td>\n<td>80</td>\n<td>85</td>\n<td>96</td>\n<td>97</td>\n<td>90.6</td>\n</tr>\n<tr>\n<td>gemini-1.5-flash-latest</td>\n<td>1000k</td>\n<td>93</td>\n<td>79</td>\n<td>87</td>\n<td>94</td>\n<td>97</td>\n<td>90</td>\n</tr>\n<tr>\n<td>Phi-3.5-MoE</td>\n<td>128k</td>\n<td>89</td>\n<td>74</td>\n<td>81</td>\n<td>88</td>\n<td>95</td>\n<td>85</td>\n</tr>\n<tr>\n<td>Phi-3.5-Mini</td>\n<td>128k</td>\n<td>86</td>\n<td>67</td>\n<td>73</td>\n<td>77</td>\n<td>82</td>\n<td>77</td>\n</tr>\n<tr>\n<td>Llama-3.1-8B-Instruct</td>\n<td>128k</td>\n<td>80</td>\n<td>65</td>\n<td>73</td>\n<td>76</td>\n<td>63</td>\n<td>71</td>\n</tr>\n<tr>\n<td>Mixtral-8x7B-Instruct-v0.1</td>\n<td>32k</td>\n<td>66</td>\n<td>65</td>\n<td>64</td>\n<td>71</td>\n<td>74</td>\n<td>68</td>\n</tr>\n<tr>\n<td>Mixtral-8x22B-Instruct-v0.1</td>\n<td>64k</td>\n<td>60</td>\n<td>67</td>\n<td>74</td>\n<td>83</td>\n<td>55</td>\n<td>67.8</td>\n</tr>\n</table>\n\n\nsuch as Arabic, Chinese, Russian, Ukrainian, and Vietnamese, with average MMLU-multilingual scores\nof 55.4 and 47.3, respectively. Due to its larger model capacity, phi-3.5-MoE achieves a significantly\nhigher average score of 69.9, outperforming phi-3.5-mini.\n\nMMLU(5-shot) MultiLingual\n\nPhi-3-mini\n\nPhi-3.5-mini\n\nPhi-3.5-MoE\n\n\n<!-- FigureContent=\"**Technical Analysis of Figure 4: Comparison of phi-3-mini, phi-3.5-mini and phi-3.5-MoE on MMLU-Multilingual tasks**\n...figure description...\n\" -->\n\n\n We evaluate the phi-3.5-mini and phi-3.5-MoE models on two long-context understanding tasks:
```

Key transformations:
1. Tables are properly formatted in Markdown with rows and columns preserved
2. Figures are identified and extracted as image files in blob storage
3. Figure placeholders are inserted with unique IDs (to be processed by Figure Analysis)
4. Page numbers are tracked for each content block
5. Document structure (headings, paragraphs) is preserved
6. The entire layout is converted to a consistent Markdown format

At this stage, figure content isn't yet analyzed - that happens in the subsequent Figure Analysis step. The Layout Analysis component focuses on extracting the document structure and preparing it for further processing.

Sources: [image_processing/README.md:64-72]()

Sources: [image_processing/README.md:64-72]()

## Production Considerations

### Performance and Scaling

```mermaid
flowchart LR
    subgraph "Performance Considerations"
        PDF["PDF Files\n(Best Quality)"] --- DOCX["DOCX Files\n(Good Quality)"]
        DOCX --- PPTX["PPTX Files\n(Variable Quality)"]
        
        SinglePage["Page-wise Chunking\n(Better for PPT)"] --- Semantic["Semantic Chunking\n(Better for PDFs)"]
        
        BatchSize["Batch Size\n(Default: 1)"] --- Parallelism["Parallelism\n(Default: 8)"]
    end
    
    Cost["Cost Management"] --- Filtering["Selective Processing"]
    Filtering --- QualityControl["Quality Validation"]
```

- **File Type Impact**: Azure Document Intelligence output quality varies significantly by file type
  - PDF produces the best output with most reliable figure detection
  - DOCX/PPTX files may have less reliable layout detection
  
- **Processing Efficiency**:
  - Layout analysis has configurable batch size (1 by default) and parallelism (8 by default)
  - For production deployments, consider adjusting these values based on throughput requirements
  
- **Cost Management**:
  - Document Intelligence and figure analysis (using GPT-4o-mini) can become expensive at scale
  - Consider selective processing for only certain document types or those that truly need image analysis
  - Use metadata tagging (`AzureSearch_Skip`) to mark documents that failed processing

- **Error Handling**:
  - The implementation includes retry logic for transient failures
  - Failed documents are tagged with metadata to prevent repeated processing attempts

- **Storage Requirements**:
  - Extracted figures are stored in a separate blob container (original-container-figures)
  - Plan for additional storage needs when processing documents with many figures

Sources: [image_processing/src/image_processing/layout_analysis.py:418-455](), [image_processing/README.md:107-112]()

Sources: [image_processing/README.md:107-112]()

---

# Page: Semantic Text Chunking

# Semantic Text Chunking

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deploy_ai_search_indexes/src/deploy_ai_search_indexes/ai_search.py](deploy_ai_search_indexes/src/deploy_ai_search_indexes/ai_search.py)
- [image_processing/README.md](image_processing/README.md)
- [image_processing/images/Image Based RAG.png](image_processing/images/Image Based RAG.png)
- [image_processing/src/image_processing/function_app.py](image_processing/src/image_processing/function_app.py)
- [image_processing/src/image_processing/layout_analysis.py](image_processing/src/image_processing/layout_analysis.py)
- [image_processing/src/image_processing/layout_holders.py](image_processing/src/image_processing/layout_holders.py)
- [image_processing/src/image_processing/semantic_text_chunker.py](image_processing/src/image_processing/semantic_text_chunker.py)
- [image_processing/tests/image_processing/test_figure_app.py](image_processing/tests/image_processing/test_figure_app.py)
- [image_processing/tests/image_processing/test_layout_analysis.py](image_processing/tests/image_processing/test_layout_analysis.py)
- [image_processing/tests/image_processing/test_layout_holders.py](image_processing/tests/image_processing/test_layout_holders.py)
- [image_processing/tests/image_processing/test_semantic_text_chunker.py](image_processing/tests/image_processing/test_semantic_text_chunker.py)

</details>



## Purpose and Scope

This document describes the Semantic Text Chunking component of the Image Processing system. Semantic Text Chunking intelligently divides document content into semantically coherent chunks while preserving contextual relationships. This is particularly important for effective Retrieval Augmented Generation (RAG) applications, as it ensures that related information remains together during indexing and retrieval.

Unlike page-wise chunking (covered in [Layout Analysis](#3.1)), the semantic text chunking approach creates chunks based on content similarity rather than physical page boundaries, which can result in more meaningful segments for AI processing.

## System Context

Semantic Text Chunking is a critical step in the document processing pipeline that feeds into AI Search for RAG applications. It processes content extracted by the Layout Analysis component after figures have been analyzed.

```mermaid
flowchart TD
    subgraph "Image Processing Pipeline"
        direction LR
        Document([Document with Images]) --> LayoutAnalysis["Layout Analysis"]
        LayoutAnalysis --> |Document structure| ProcessedLayout["Layout with Text and Figures"]
        
        ProcessedLayout --> FigureExtraction["Figure Extraction"]
        FigureExtraction --> |Extracted figures| FigureAnalysis["Figure Analysis"]
        FigureAnalysis --> |Using GPT-4o-mini| FigureDescriptions["Figure Descriptions"]
        
        ProcessedLayout --> LayoutFigureMerger["Layout and Figure Merger"]
        FigureDescriptions --> LayoutFigureMerger
        LayoutFigureMerger --> |Unified content| SemanticTextChunker["Semantic Text Chunker"]
        
        SemanticTextChunker --> MarkupCleaner["MarkUp Cleaner"]
        MarkupCleaner --> |Clean content| AISearch[(AI Search Indexes)]
    end
    
    AISearch --> |Enables| RAG["RAG Application"]
```

Sources: 
- `image_processing/README.md`
- `image_processing/src/image_processing/function_app.py`

## How Semantic Text Chunking Works

The semantic chunker takes a document's content as input and divides it into chunks by following these key principles:

1. Preserving structural elements (tables, figures)
2. Keeping semantically similar sentences together
3. Respecting natural content boundaries (headings, paragraphs)
4. Optimizing chunk size for effective embedding and retrieval

```mermaid
flowchart TD
    subgraph "SemanticTextChunker.chunk() process"
        direction TB
        InputContent["Document content"] --> SentenceSplitting["1. split_into_sentences()"]
        SentenceSplitting --> GroupTablesAndFigures["2. group_figures_and_tables_into_sentences()"]
        GroupTablesAndFigures --> ForwardPass["3. merge_chunks(forwards_direction=True)"]
        ForwardPass --> BackwardPass["4. merge_chunks(forwards_direction=False)"]
        BackwardPass --> CleanChunks["5. clean_chunks_and_map()"]
        CleanChunks --> PageMapping["6. assign_page_number_to_chunks()"]
        PageMapping --> OptimizedChunks["Return ChunkHolder objects"]
    end
```

Sources:
- [image_processing/src/image_processing/semantic_text_chunker.py:77-138]()
- [image_processing/README.md]()

### Key Processing Steps

The chunking process involves several sophisticated steps:

1. **Sentence Splitting**: Using spaCy, the document content is split into sentences while preserving markdown elements
2. **Structural Preservation**: Tables and figures are kept intact by grouping related sentences
3. **Two-Pass Merging**:
   - Forward pass: Starting from the beginning, sentences are grouped based on semantic similarity
   - Backward pass: Starting from the end, similar groups are further consolidated
4. **Page Number Mapping**: Each chunk is mapped to its original page number for source tracking

```mermaid
flowchart TD
    subgraph "Two-Pass Merging Strategy"
        direction TB
        Sentences["Sentences"] --> Forward["Forward Pass"]
        Forward --> |"Initial chunks"| Backward["Backward Pass"]
        Backward --> |"Optimized chunks"| FinalChunks["Final Chunks"]
        
        subgraph "merge_chunks(forwards_direction=true)"
            ForwardStart["Start from beginning"] --> ForwardProcess["Process each sentence"]
            ForwardProcess --> ForwardDecision{"Is semantically similar?"}
            ForwardDecision --> |"Yes"| ForwardAdd["Add to current chunk"]
            ForwardDecision --> |"No"| ForwardNewChunk["Start new chunk"]
        end
        
        subgraph "merge_chunks(forwards_direction=false)"
            BackwardStart["Start from end"] --> BackwardProcess["Process each sentence"]
            BackwardProcess --> BackwardDecision{"Is semantically similar?"}
            BackwardDecision --> |"Yes"| BackwardAdd["Add to current chunk"]
            BackwardDecision --> |"No"| BackwardNewChunk["Start new chunk"]
        end
    end
    
    subgraph "sentence_similarity() calculation"
        direction TB
        Text1["Text Segment 1"] --> Embedding1["model2vec.encode()"]
        Text2["Text Segment 2"] --> Embedding2["model2vec.encode()"]
        Embedding1 --> |"Vector 1"| CosineSimilarity["np.dot / (magnitudes)"]
        Embedding2 --> |"Vector 2"| CosineSimilarity
        CosineSimilarity --> |"Similarity Score"| CompareThreshold{"Compare to threshold"}
    end
```

Sources:
- [image_processing/src/image_processing/semantic_text_chunker.py:358-452]()
- [image_processing/src/image_processing/semantic_text_chunker.py:454-467]()

## Implementation Details

### Core Class and Component Structure

The semantic text chunking functionality is implemented through a core class that manages the chunking process and provides methods for different chunking stages.

```mermaid
classDiagram
    class SemanticTextChunker {
        +float similarity_threshold
        +int max_chunk_tokens
        +int min_chunk_tokens
        -StaticModel distilled_model
        -NLPModel _nlp_model
        +async chunk(text) list[ChunkHolder]
        +split_into_sentences(text) list[str]
        +group_figures_and_tables_into_sentences(sentences) tuple
        +merge_chunks(sentences, is_table_or_figure_map, forwards_direction) tuple
        +merge_similar_chunks(current_sentence, current_chunk, forwards_direction) tuple
        +sentence_similarity(text_1, text_2) float
        +assign_page_number_to_chunks(chunks, page_number_tracking_holders) list[ChunkHolder]
        +num_tokens_from_string(string) int
        +clean_chunks_and_map(chunks, is_table_or_figure_map) tuple
        +sentence_contains_figure_or_table(text) bool
    }
    
    class ChunkHolder {
        +str mark_up
        +list[str] sections
        +list[FigureHolder] figures
        +str cleaned_text
        +int page_number
    }
    
    class PageNumberTrackingHolder {
        +int page_number
        +str page_content
    }
    
    class FigureHolder {
        +str figure_id
        +str caption
        +int offset
        +int length
        +int page_number
        +str uri
        +str description
        +str data
        +markdown() str
    }
    
    SemanticTextChunker ..> ChunkHolder : creates
    SemanticTextChunker ..> PageNumberTrackingHolder : uses
    ChunkHolder ..> FigureHolder : contains
```

Sources:
- [image_processing/src/image_processing/semantic_text_chunker.py:13-468]()
- [image_processing/src/image_processing/layout_holders.py:66-74]()
- [image_processing/src/image_processing/layout_holders.py:50-55]()
- [image_processing/src/image_processing/layout_holders.py:8-33]()

### Algorithm Highlights

#### Sentence Splitting

The `split_into_sentences` method uses spaCy to intelligently split text into sentences, with special handling for:

- Markdown headings (ensuring they start with `\n\n` and end with `\n\n`)
- Figure and table tags (preserving them intact)
- Line breaks and whitespace management

The method first cleans newlines and empty figures using `clean_new_lines` and `filter_empty_figures`, then applies spaCy's sentence segmentation with specialized post-processing for HTML tags and markdown headings:

```mermaid
flowchart TD
    subgraph "split_into_sentences() flow"
        CleanNewLines["clean_new_lines()"] --> FilterEmptyFigures["filter_empty_figures()"]
        FilterEmptyFigures --> SpacyProcess["Apply spaCy sentence tokenization"]
        SpacyProcess --> TagSplitting["Split at tag junctions"]
        TagSplitting --> HeadingSplitting["Split on markdown headings"]
        HeadingSplitting --> FormattedSentences["Return formatted sentences"]
    end
```

Sources:
- [image_processing/src/image_processing/semantic_text_chunker.py:160-219]()
- [image_processing/src/image_processing/semantic_text_chunker.py:149-158]()
- [image_processing/src/image_processing/semantic_text_chunker.py:140-148]()

#### Figure and Table Grouping

To ensure that tables and figures are kept intact within chunks, the `group_figures_and_tables_into_sentences` method:

1. Detects sentences containing table or figure tags
2. Groups consecutive sentences that are part of the same table or figure
3. Creates a mapping of which sentences contain tables/figures for later processing

```mermaid
flowchart TD
    Start["Start with sentence list"] --> Loop["For each sentence"]
    Loop --> ContainsTag{"Contains figure/table tag?"}
    ContainsTag --> |"Yes"| IsComplete{"Is complete figure/table?"}
    ContainsTag --> |"No"| AddRegular["Add as regular sentence"]
    
    IsComplete --> |"Yes"| AddComplete["Add as complete figure/table"]
    IsComplete --> |"No"| StartGroup["Start grouping sentences"]
    
    StartGroup --> NextSentence["Process next sentence"]
    NextSentence --> HasEnding{"Has ending tag?"}
    HasEnding --> |"Yes"| CombineAndAdd["Combine sentences and add to result"]
    HasEnding --> |"No"| ContinueGrouping["Continue grouping"]
    
    CombineAndAdd --> UpdateMap["Mark as table/figure in map"]
    AddRegular --> UpdateMapRegular["Mark as regular in map"]
    AddComplete --> UpdateMapComplete["Mark as table/figure in map"]
    
    UpdateMap --> Continue["Continue processing"]
    UpdateMapRegular --> Continue
    UpdateMapComplete --> Continue
```

Sources:
- [image_processing/src/image_processing/semantic_text_chunker.py:221-260]()
- [image_processing/src/image_processing/semantic_text_chunker.py:32-46]()

#### Semantic Similarity Calculation

The chunker uses a pre-trained `model2vec` model to calculate the semantic similarity between text segments:

1. Text segments are encoded into vector representations using `distilled_model.encode()`
2. The cosine similarity between vectors is calculated using dot product and vector magnitudes
3. If the similarity is above the configured threshold, segments are merged
4. Additional checks ensure chunks don't exceed the maximum token limit

The vector similarity check is implemented in the `sentence_similarity` method:

```mermaid
flowchart LR
    subgraph "sentence_similarity() calculation"
        Text1["text_1"] --> Encode1["distilled_model.encode()"]
        Text2["text_2"] --> Encode2["distilled_model.encode()"]
        
        Encode1 --> |"vec1"| DotProduct["np.dot(vec1, vec2)"]
        Encode2 --> |"vec2"| DotProduct
        
        Encode1 --> |"vec1"| Magnitude["np.linalg.norm(vec1) * np.linalg.norm(vec2)"]
        Encode2 --> |"vec2"| Magnitude
        
        DotProduct --> |"dot_product"| Division["dot_product / magnitude"]
        Magnitude --> |"magnitude"| Division
        
        Division --> |"similarity"| Result["Return similarity score"]
    end
```

Sources:
- [image_processing/src/image_processing/semantic_text_chunker.py:454-467]()
- [image_processing/src/image_processing/semantic_text_chunker.py:268-353]()
- [image_processing/src/image_processing/semantic_text_chunker.py:24-25]()

#### Page Number Tracking

To maintain source attribution, each chunk is mapped to its original page number:

1. The first sentence of each page is recorded during layout analysis
2. During chunking, each chunk's first sentence is compared with these page markers
3. The page number is assigned based on the matching page marker

```
Sources:
- `image_processing/src/image_processing/semantic_text_chunker.py:468-549`
```

## Configuration Parameters

The semantic text chunker can be customized through several parameters to optimize chunking behavior for different types of documents:

| Parameter | Description | Default | Impact |
|-----------|-------------|---------|--------|
| `similarity_threshold` | Threshold for considering text segments as semantically related | 0.8 | Higher values create more chunks with tighter semantic coherence |
| `max_chunk_tokens` | Maximum size of a chunk in tokens | 500 | Controls the upper limit for chunk sizes |
| `min_chunk_tokens` | Minimum size of a chunk in tokens | 200 | Prevents creation of very small chunks |

These parameters can be adjusted via HTTP headers when calling the semantic text chunker endpoint:

```mermaid
flowchart TD
    subgraph "Configuration Flow"
        HttpRequest["HTTP Request"] --> |"Headers"| ExtractParams["Extract parameters"]
        ExtractParams --> InitChunker["Initialize SemanticTextChunker"]
        
        subgraph "Header Parameters"
            SimilarityThreshold["similarity_threshold: 0.8"]
            MaxTokens["max_chunk_tokens: 500"]
            MinTokens["min_chunk_tokens: 50"]
        end
        
        InitChunker --> ProcessContent["Process content"]
        ProcessContent --> ReturnChunks["Return chunked content"]
    end
```

Sources:
- [image_processing/src/image_processing/semantic_text_chunker.py:14-22]()
- [image_processing/src/image_processing/function_app.py:174-195]()

## Integration with AI Search

The Semantic Text Chunker is deployed as a custom skill in the AI Search enrichment pipeline. It's implemented as an Azure Function that can be called by AI Search during document processing.

```mermaid
flowchart TB
    subgraph "AI Search Enrichment Pipeline with Semantic Chunking"
        direction LR
        Document[(Document Blob)] --> LayoutAnalysis["layout_analysis() Skill"]
        LayoutAnalysis --> |"layout"| FigureAnalysis["figure_analysis() Skill"]
        FigureAnalysis --> |"updated_figure"| LayoutFigureMerger["layout_and_figure_merger() Skill"]
        LayoutFigureMerger --> |"layout_merged_content"| SemanticChunker["semantic_text_chunker() Skill"]
        SemanticChunker --> |"chunk_mark_ups"| MarkUpCleaner["mark_up_cleaner() Skill"]
        MarkUpCleaner --> |"final_mark_up"| VectorSkill["Vector Embedding Skill"]
        VectorSkill --> AISearchIndex[(AI Search Index)]
    end
```

The Semantic Text Chunker skill is configured in the AI Search deployment process with these parameters:

```mermaid
flowchart TD
    subgraph "get_semantic_chunker_skill() Configuration"
        SkillName["Semantic Chunker Skill"] --> Endpoint["/semantic_text_chunker Function URL"]
        Endpoint --> Timeout["Timeout: PT230S"]
        
        Parameters --> SimThreshold["similarity_threshold: 0.8"]
        Parameters --> MaxTokens["max_chunk_tokens: 500"]
        Parameters --> MinTokens["min_chunk_tokens: 150"]
        
        Inputs --> Content["source: /document/layout_merged_content"]
        Inputs --> PageTrackers["source: /document/page_number_tracking_holders"]
        
        Outputs --> Chunks["target: /document/chunk_mark_ups"]
        
        Performance --> BatchSize["batch_size: 8 (2 for testing)"]
        Performance --> Parallelism["degree_of_parallelism: 16 (2 for testing)"]
    end
```

Sources:
- [deploy_ai_search_indexes/src/deploy_ai_search_indexes/ai_search.py:284-352]()
- [image_processing/README.md]()
- [image_processing/src/image_processing/function_app.py:157-212]()

## Performance Considerations

### Token Usage Optimization

The chunker uses token counting to ensure chunks are appropriately sized for embedding models:

1. The `num_tokens_from_string` method uses the `cl100k_base` tokenizer to accurately count tokens
2. Chunks are optimized to balance size and semantic coherence
3. Configuration parameters allow fine-tuning for different document types and embedding models

```
Sources:
- `image_processing/src/image_processing/semantic_text_chunker.py:48-59`
```

### Processing Efficiency

For large documents, the chunking process includes several optimizations:

1. Using spaCy's efficient NLP pipeline with disabled unnecessary components
2. Configurable batch sizes and parallelism for function app processing
3. Two-pass strategy to minimize the number of chunks while preserving semantic relationships

```
Sources:
- `image_processing/src/image_processing/semantic_text_chunker.py:177-180`
- `deploy_ai_search_indexes/src/deploy_ai_search_indexes/ai_search.py:306-309`
```

## HTTP Endpoint Integration

The Semantic Text Chunker is exposed as an HTTP endpoint in the Function App, making it available for integration with AI Search or direct API calls:

```mermaid
flowchart LR
    subgraph "HTTP Endpoint Flow"
        AISearch["AI Search"] --> |"POST Request"| Endpoint["/semantic_text_chunker"]
        Endpoint --> Headers["Extract configuration from Headers"]
        Headers --> CreateChunker["Initialize SemanticTextChunker"]
        CreateChunker --> ProcessRecords["Process each record"]
        ProcessRecords --> |"Invoke process_semantic_text_chunker()"| ChunkText["chunk() Text"]
        ChunkText --> AssignPageNumbers["assign_page_number_to_chunks()"]
        AssignPageNumbers --> FormatResponse["Format JSON response"]
        FormatResponse --> ReturnChunks["Return Chunk Holders"]
    end
```

The endpoint accepts JSON payloads in the AI Search custom skill format:

```json
{
  "values": [
    {
      "recordId": "1",
      "data": {
        "content": "The document content to chunk...",
        "page_number_tracking_holders": [
          {"page_content": "First page content", "page_number": 1},
          {"page_content": "Second page content", "page_number": 2}
        ]
      }
    }
  ]
}
```

And returns chunks with preserved semantic relationships and structure:

```json
{
  "values": [
    {
      "recordId": "1",
      "data": {
        "chunks": [
          {
            "mark_up": "Semantically coherent chunk of content...",
            "page_number": 1
          },
          {
            "mark_up": "Another semantically coherent chunk...",
            "page_number": 2
          }
        ]
      }
    }
  ]
}
```

Sources:
- [image_processing/src/image_processing/function_app.py:158-212]()
- [image_processing/src/image_processing/semantic_text_chunker.py:552-608]()

## Conclusion

The Semantic Text Chunking component provides sophisticated document segmentation capabilities that go beyond simple page-based or fixed-length chunking. By preserving semantic relationships and structure, it enables more effective information retrieval and better RAG application performance when dealing with complex documents containing figures, tables, and varied content.

---

# Page: Figure Analysis and Processing

# Figure Analysis and Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [image_processing/README.md](image_processing/README.md)
- [image_processing/images/Image Based RAG.png](image_processing/images/Image Based RAG.png)
- [image_processing/src/image_processing/function_app.py](image_processing/src/image_processing/function_app.py)
- [image_processing/src/image_processing/layout_and_figure_merger.py](image_processing/src/image_processing/layout_and_figure_merger.py)
- [image_processing/src/image_processing/requirements.txt](image_processing/src/image_processing/requirements.txt)
- [image_processing/tests/image_processing/test_figure_app.py](image_processing/tests/image_processing/test_figure_app.py)
- [image_processing/tests/image_processing/test_layout_analysis.py](image_processing/tests/image_processing/test_layout_analysis.py)
- [image_processing/tests/image_processing/test_layout_holders.py](image_processing/tests/image_processing/test_layout_holders.py)
- [image_processing/tests/image_processing/test_semantic_text_chunker.py](image_processing/tests/image_processing/test_semantic_text_chunker.py)

</details>



## Purpose and Scope

This document details the Figure Analysis and Processing component of the Image Processing system, which is responsible for analyzing and understanding figures, charts, and images in documents using multimodal models. This component extracts visual information that would otherwise be lost in traditional text-only processing, making it accessible for retrieval in RAG applications.

For information about the overall Image Processing system architecture, see [Image Processing System](#3). For details on layout analysis, which handles the initial document structure extraction, see [Layout Analysis](#3.1).

Sources: [image_processing/README.md:22-28]()

## Architecture and Workflow

The Figure Analysis component operates within the broader document processing pipeline. After the Layout Analysis component extracts document structure and identifies figures, the Figure Analysis component processes these figures to extract meaningful insights from visual elements.

### Figure Analysis Pipeline

```mermaid
graph TD
    classDef component fill:#f9f9f9,stroke:#333,stroke-width:2px

    DocumentIntelligence["Azure Document Intelligence"] --> |"Extracts figures"| LayoutAnalysis["LayoutAnalysis Class"]
    LayoutAnalysis --> |"Identified Figures"| FigureAnalysis["FigureAnalysis Class"]
    FigureAnalysis --> |"API Calls"| GPT4oMini["GPT-4o-mini Model"]
    GPT4oMini --> |"Figure descriptions"| FigureAnalysis
    FigureAnalysis --> |"Processed Figures"| LayoutFigureMerger["LayoutAndFigureMerger Class"]
    LayoutAnalysis --> |"Document Layout"| LayoutFigureMerger
    LayoutFigureMerger --> |"Unified Content"| TextChunker["Semantic Text Chunker"]
    TextChunker --> |"Chunked Content"| MarkupCleaner["Markup Cleaner"]
    MarkupCleaner --> AISearch["Azure AI Search Index"]
    
    class LayoutAnalysis,FigureAnalysis,LayoutFigureMerger,TextChunker,MarkupCleaner component
```

Sources: [image_processing/README.md:10-28](), [image_processing/src/image_processing/function_app.py:56-84]()

### Function App Routes

The Figure Analysis component is implemented as part of an Azure Function App with multiple HTTP endpoints:

```mermaid
graph LR
    classDef route fill:#f9f9f9,stroke:#333,stroke-width:2px
    
    Client["Client Application"] --> |"POST"| LayoutRoute["/layout_analysis"]
    Client --> |"POST"| FigureRoute["/figure_analysis"]
    Client --> |"POST"| MergerRoute["/layout_and_figure_merger"]
    Client --> |"POST"| ChunkerRoute["/semantic_text_chunker"]
    Client --> |"POST"| CleanerRoute["/mark_up_cleaner"]
    
    LayoutRoute --> |"Calls"| LayoutAnalysis["process_layout_analysis()"]
    FigureRoute --> |"Calls"| FigureAnalysis["FigureAnalysis.analyse()"]
    MergerRoute --> |"Calls"| LayoutFigureMerger["LayoutAndFigureMerger.merge()"]
    ChunkerRoute --> |"Calls"| TextChunker["process_semantic_text_chunker()"]
    CleanerRoute --> |"Calls"| MarkupCleaner["MarkUpCleaner.clean()"]
    
    class LayoutRoute,FigureRoute,MergerRoute,ChunkerRoute,CleanerRoute route
```

Sources: [image_processing/src/image_processing/function_app.py:18-212](), [image_processing/tests/image_processing/test_figure_app.py:8-16]()

## FigureAnalysis Component

The `FigureAnalysis` class is the core component responsible for analyzing figures using the GPT-4o-mini multimodal model. It processes figures extracted during the layout analysis phase.

### Key Features

- Takes figure data extracted by the Layout Analysis component
- Connects to Azure OpenAI to access the GPT-4o-mini multimodal model
- Submits figure images to the model with specialized prompts
- Generates descriptive text and summaries of the visual information
- Formats the analysis into structured figure descriptions that can be indexed and searched

Sources: [image_processing/src/image_processing/function_app.py:56-84](), [image_processing/tests/image_processing/test_figure_app.py:97-120]()

### Figure Extraction Process

1. **Initial Extraction**: Azure Document Intelligence identifies figures in the document during layout analysis
2. **Figure Isolation**: Identified figures are extracted as image data
3. **Storage**: Figures are saved to Azure Blob Storage for later access
4. **Reference Creation**: Each figure gets a unique ID and URI for retrieval

Sources: [image_processing/README.md:25-28](), [image_processing/tests/image_processing/test_layout_analysis.py:243-268]()

## Multimodal Analysis with GPT-4o-mini

The Figure Analysis component leverages GPT-4o-mini's visual understanding capabilities to extract meaning from images, charts, and diagrams.

### Prompt Structure

The prompt is designed to generate comprehensive descriptions of figures with specific focus on:

1. Technical analysis of the figure
2. Overview of what the figure represents
3. Data interpretation for charts and graphs
4. Identification of key elements and relationships
5. Summary of key findings and insights

Importantly, the prompt focuses on generating retrievable descriptions rather than exhaustive details. This approach ensures that:

- Figure information can be found during vector searches
- The full figure can be presented during retrieval for detailed analysis
- The indexed description contains enough context to understand the figure's purpose

Sources: [image_processing/README.md:25-28](), [image_processing/README.md:62-72]()

### Sample Figure Description

Below is an example of how the system processes a figure from a technical document:

```
<!-- FigureContent="**Technical Analysis of Figure 4: Comparison of phi-3-mini, phi-3.5-mini and phi-3.5-MoE on MMLU-Multilingual tasks**

1. **Overview:**
   - The image is a bar chart comparing the performance of three different models—phi-3-mini, phi-3.5-mini, and phi-3.5-MoE—on MMLU-Multilingual tasks across various languages.

2. **Axes:**
   - The x-axis represents the languages in which the tasks were performed. The languages listed are: Arabic, Chinese, Dutch, French, German, Italian, Russian, Spanish, Ukrainian, Vietnamese, and English.
   - The y-axis represents the performance, likely measured in percentage or score, ranging from 0 to 90.

3. **Legend:**
   - The chart uses three different colors to represent the three models:
     - Orange bars represent the phi-3-mini model.
     - Green bars represent the phi-3.5-mini model.
     - Blue bars represent the phi-3.5-MoE model.

4. **Data Interpretation:**
   - Across all languages, the phi-3.5-MoE (blue bars) consistently outperforms the other two models, showing the highest bars.
   - The phi-3.5-mini (green bars) shows better performance than the phi-3-mini (orange bars) in most languages, but not at the level of phi-3.5-MoE.

5. **Language-specific Insights:**
   - **Arabic**: phi-3.5-MoE shows significantly higher performance compared to the other two models, with phi-3.5-mini outperforming phi-3-mini.
   - **Chinese**: A similar trend is observed as in Arabic, with phi-3.5-MoE leading by a wide margin.
   - **Dutch**: Performance is roughly similar between phi-3.5-mini and phi-3.5-MoE, with phi-3.5-MoE being slightly better.
   - **French**: A clear distinction in performance, with phi-3.5-MoE far exceeding the other two.
   - **German**: phi-3.5-MoE leads, followed by phi-3.5-mini, while phi-3-mini lags significantly behind.
   - **Italian**: The performance gap narrows between phi-3.5-mini and phi-3.5-MoE, but the latter is still superior.
   - **Russian**: phi-3.5-MoE shows noticeably higher performance.
   - **Spanish**: The performance trend is consistent with the previous languages, with phi-3.5-MoE leading.
   - **Ukrainian**: A substantial lead by phi-3.5-MoE.
   - **Vietnamese**: An anomaly where all models show closer performance, yet phi-3.5-MoE still leads.
   - **English**: The highest performance is seen in English, with phi-3.5-MoE nearly reaching the maximum score.

6. **Conclusion:**
   - The phi-3.5-MoE model consistently outperforms the phi-3-mini and phi-3.5-mini models across all MMLU-Multilingual tasks.
   - The phi-3.5-mini model shows a general improvement over the phi-3-mini, but the improvement is not as significant as phi-3.5-MoE.

This structured analysis provides a comprehensive understanding of the comparative performance of the mentioned models across multilingual tasks." -->
```

Sources: [image_processing/README.md:62-72]()

## Data Structures and Holders

The Figure Analysis component uses several data structures to handle figures and their processed information:

### FigureHolder Class

`FigureHolder` encapsulates figure metadata and content:

```mermaid
classDiagram
    class FigureHolder {
        +string figure_id
        +int offset
        +int length
        +string uri
        +string data
        +string description
        +string caption
        +string markdown
    }
    
    note for FigureHolder "Stores figure metadata and processed content\nA Pydantic model for validation and serialization"
```

### Key Fields:

- `figure_id`: Unique identifier for the figure
- `offset`: Position in the document where the figure appears
- `length`: Length of the figure content in the document
- `uri`: The URI where the figure image is stored
- `data`: Base64-encoded image data
- `description`: AI-generated description of the figure
- `caption`: Original caption from the document (if available)
- `markdown`: Figure formatted as markdown for insertion into the document

Sources: [image_processing/tests/image_processing/test_layout_holders.py:14-29]()

## LayoutAndFigureMerger Component

After figures are analyzed, the `LayoutAndFigureMerger` class integrates figure descriptions back into the document content.

### Key Methods

```mermaid
classDiagram
    class LayoutAndFigureMerger {
        +merge(record: dict) -> dict
        +merge_figures_into_layout(layout_holder: LayoutHolder, figures: List[FigureHolder]) -> LayoutHolder
        +insert_figure_description(layout_holder: LayoutHolder, figure_holder: FigureHolder) -> tuple
    }
    
    class LayoutHolder {
        +string content
        +int page_number
        +int page_offsets
        +List~FigureHolder~ figures
    }
    
    LayoutAndFigureMerger -- LayoutHolder: uses
```

Sources: [image_processing/src/image_processing/layout_and_figure_merger.py:10-158]()

### Figure Insertion Process

1. **Position Calculation**: Determines where in the document content to insert figure descriptions
2. **Content Replacement**: Replaces the original figure reference with the enriched figure description
3. **Offset Management**: Adjusts offsets to handle multiple figures
4. **Cleanup**: Removes irrelevant or empty figures and HTML comments

The merger process follows this sequence:

```mermaid
sequenceDiagram
    participant Azure as "AI Search Skillset"
    participant Merger as "LayoutAndFigureMerger"
    participant Layout as "LayoutHolder"
    participant Figures as "FigureHolders"
    
    Azure->>Merger: POST /layout_and_figure_merger
    Merger->>Merger: parse record data
    Merger->>Layout: create LayoutHolder
    Merger->>Figures: create FigureHolders
    
    loop For each figure
        Merger->>Merger: adjust figure offset
        Merger->>Merger: insert_figure_description()
        Merger->>Layout: update content
    end
    
    Merger->>Merger: Remove irrelevant/empty figures
    Merger->>Merger: Remove HTML comments
    Merger->>Azure: Return updated layout
```

Sources: [image_processing/src/image_processing/layout_and_figure_merger.py:55-118]()

## HTTP Function Interface

The Figure Analysis component exposes an HTTP endpoint for processing figures:

### `/figure_analysis` Endpoint

This endpoint handles figure analysis requests as part of the AI Search skillset:

- **Method**: POST
- **Request Format**: AI Search custom skill format
- **Request Body**: Contains figure data extracted from documents
- **Response**: Analysis results in AI Search compatible format

### Request/Response Flow

```mermaid
sequenceDiagram
    participant Client as "AI Search Skillset"
    participant Function as "/figure_analysis"
    participant Processor as "FigureAnalysis"
    participant OpenAI as "Azure OpenAI (GPT-4o-mini)"
    
    Client->>Function: POST with figure data
    Function->>Function: parse request body
    Function->>Processor: create FigureAnalysis
    
    loop For each figure record
        Function->>Processor: analyse(value)
        Processor->>OpenAI: submit figure for analysis
        OpenAI->>Processor: return figure description
        Processor->>Function: return processed result
    end
    
    Function->>Client: JSON response with analysis results
```

Sources: [image_processing/src/image_processing/function_app.py:56-84](), [image_processing/tests/image_processing/test_figure_app.py:97-120]()

## Integration with RAG Applications

The Figure Analysis component enables enhanced RAG capabilities by making visual information available for retrieval:

### Runtime RAG Flow

```mermaid
graph TD
    subgraph "Indexing Time"
        Doc["Document with Figures"] --> |"Upload"| LayoutAnalysis
        LayoutAnalysis["Layout Analysis"] --> |"Extract Figures"| FigureAnalysis["Figure Analysis"]
        FigureAnalysis --> |"Descriptions"| Merger["Layout & Figure Merger"]
        Merger --> |"Combined Content"| Chunker["Semantic Chunker"]
        Chunker --> |"Chunks"| AISearch["Azure AI Search"]
    end
    
    subgraph "Query Time"
        User["User"] --> |"Ask Question"| RAGSystem["RAG System"]
        RAGSystem --> |"Vector Search"| AISearch
        AISearch --> |"Relevant Chunks + Figure References"| RAGSystem
        RAGSystem --> |"Display Figure + Summary"| VisualModel["Visual Model (GPT-4o)"]
        VisualModel --> |"Comprehensive Answer"| User
    end
```

Sources: [image_processing/README.md:58-62]()

### Key Benefits

1. **Enhanced Information Retrieval**: Makes visual information searchable through text descriptions
2. **Context Preservation**: Maintains the relationship between figures and surrounding text
3. **Multimodal Understanding**: Enables systems to comprehend both textual and visual content
4. **Improved Response Quality**: Provides more comprehensive answers by including visual elements

Sources: [image_processing/README.md:11-15]()

## Production Considerations

When deploying the Figure Analysis component in production environments:

### Performance and Cost

- **File Type Impact**: PDF files produce richer figure detection outputs compared to other formats like PPTX
- **Processing Cost**: Using GPT-4o-mini for figure analysis can be expensive for large document collections
- **Selective Processing**: Consider only processing a subset of documents or figures if cost is a concern

### Optimization Strategies

1. **Filtering**: Process only figures above a certain size or importance threshold
2. **Caching**: Cache analyzed figures to avoid reprocessing
3. **Batch Processing**: Process figures in batches to optimize API calls
4. **Content Targeting**: Focus on documents where visual elements are critical to understanding

Sources: [image_processing/README.md:107-112]()

## Summary

The Figure Analysis and Processing component is a critical part of the Image Processing system that enables RAG applications to understand and retrieve information from visual elements in documents. By leveraging multimodal AI models like GPT-4o-mini, it converts visual information into searchable text descriptions that can be indexed alongside document content. This significantly enhances the quality and comprehensiveness of responses for documents containing charts, diagrams, and other visual elements.

---

# Page: AI Search Integration

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

# Page: AI Search Index Deployment

# AI Search Index Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deploy_ai_search_indexes/README.md](deploy_ai_search_indexes/README.md)
- [deploy_ai_search_indexes/src/deploy_ai_search_indexes/ai_search.py](deploy_ai_search_indexes/src/deploy_ai_search_indexes/ai_search.py)
- [image_processing/src/image_processing/layout_analysis.py](image_processing/src/image_processing/layout_analysis.py)
- [image_processing/src/image_processing/layout_holders.py](image_processing/src/image_processing/layout_holders.py)
- [image_processing/src/image_processing/semantic_text_chunker.py](image_processing/src/image_processing/semantic_text_chunker.py)
- [text_2_sql/data_dictionary/README.md](text_2_sql/data_dictionary/README.md)
- [text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/cli.py](text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/cli.py)

</details>



This page documents the process of deploying and configuring Azure AI Search indexes for both the Text-to-SQL and Image Processing systems. These indexes serve as the foundation for metadata retrieval, query caching, and content processing capabilities.

For information about how these indexes are used within the system, see [AI Search Integration](#4).

## Overview and Architecture

The project uses multiple Azure AI Search indexes to support different aspects of the system:

1. **Text-to-SQL Indexes**:
   - Schema Store Index - Contains database schema metadata
   - Column Value Store Index - Contains string values from dimension tables
   - Query Cache Index - Stores previous questions and their SQL queries

2. **Image Processing Index**:
   - Stores processed documents with extracted layout, figures, and semantic chunks

### System Integration Diagram

```mermaid
flowchart TD
    subgraph "Storage"
        BlobStorage["Azure Blob Storage Containers"] 
    end
    
    subgraph "AI Search Indexes"
        SchemaStoreIndex["text_2_sql_schema_store-index"]
        ColumnValueIndex["text_2_sql_column_value_store-index"]
        QueryCacheIndex["text_2_sql_query_cache-index"]
        ImageProcIndex["image_processing-index"]
    end
    
    subgraph "Text2SQL System"
        SchemaAgent["SchemaAgent"]
        QueryCacheAgent["QueryCacheAgent"]
        SchemaStore["SchemaStore"]
        ColumnStore["ColumnStore"]
        QueryCache["QueryCache"]
    end
    
    subgraph "Image Processing System"
        LayoutAnalysis["LayoutAnalysis"]
        FigureAnalysis["FigureAnalysis"]
        SemanticTextChunker["SemanticTextChunker"]
        MarkupCleaner["MarkupCleaner"]
    end

    BlobStorage -->|"entities.json"| SchemaStoreIndex
    BlobStorage -->|"column_values.jsonl"| ColumnValueIndex
    BlobStorage -->|"query_cache.jsonl"| QueryCacheIndex
    BlobStorage -->|"PDFs, PPTXs, etc."| ImageProcIndex
    
    SchemaStoreIndex --> SchemaStore
    ColumnValueIndex --> ColumnStore
    QueryCacheIndex --> QueryCache
    
    SchemaStore --> SchemaAgent
    ColumnStore --> SchemaAgent
    QueryCache --> QueryCacheAgent
    
    ImageProcIndex <--> LayoutAnalysis
    ImageProcIndex <--> FigureAnalysis
    ImageProcIndex <--> SemanticTextChunker
    ImageProcIndex <--> MarkupCleaner
```

Sources: [deploy_ai_search_indexes/README.md:1-84](), [text_2_sql/data_dictionary/README.md:1-176](), [image_processing/src/image_processing/semantic_text_chunker.py:13-138](), [image_processing/src/image_processing/layout_analysis.py:143-573]()

## Deployment Infrastructure

All index deployments are built on a common abstraction layer provided by the `AISearch` base class. This class handles the deployment of indexes, skillsets, data sources, and indexers, with specialized subclasses for each index type.

### AI Search Class Hierarchy

```mermaid
classDiagram
    AISearch <|-- Text2SQLSchemaStoreAISearch
    AISearch <|-- Text2SQLColumnValueStoreAISearch
    AISearch <|-- Text2SQLQueryCacheAISearch
    AISearch <|-- ImageProcessingAISearch
    
    class AISearch {
        #indexer_type
        #suffix
        #environment: AISearchEnvironment
        +indexer_name: str
        +skillset_name: str
        +semantic_config_name: str
        +index_name: str
        +data_source_name: str
        +vector_search_profile_name: str
        +get_index_fields()
        +get_semantic_search()
        +get_skills()
        +get_indexer()
        +get_data_source()
        +get_vector_skill()
        +get_vector_search()
        +deploy_index()
        +deploy_skillset()
        +deploy_data_source()
        +deploy_indexer()
        +run_indexer()
        +reset_indexer()
        +deploy()
    }
    
    class Text2SQLSchemaStoreAISearch {
        +get_index_fields()
        +get_skills()
        +get_indexer()
        +get_index_projections()
    }
    
    class Text2SQLColumnValueStoreAISearch {
        +get_index_fields()
        +get_skills()
        +get_indexer()
        +get_index_projections()
    }
    
    class Text2SQLQueryCacheAISearch {
        +get_index_fields()
        +get_skills()
        +get_indexer()
        +get_index_projections()
    }
    
    class ImageProcessingAISearch {
        +get_index_fields()
        +get_skills()
        +get_indexer()
        +get_index_projections()
        +get_semantic_chunker_skill()
        +get_layout_analysis_skill()
        +get_figure_analysis_skill()
        +get_layout_and_figure_merger_skill()
        +get_mark_up_cleaner_skill()
    }
```

The `AISearch` base class provides the core functionality for deploying all components of an AI Search pipeline. Each specialized subclass implements the abstract methods to define the specific fields, skills, and configuration needed for that particular index type.

Sources: [deploy_ai_search_indexes/src/deploy_ai_search_indexes/ai_search.py:35-751]()

## Text-to-SQL Indexes

### Schema Store Index

The Schema Store Index contains metadata about database tables, views, columns, relationships, and definitions. This information powers the LLM's understanding of the database structure.

**Content Example:**
```json
{
    "Entity": "SalesOrderDetail",
    "Definition": null,
    "Schema": "SalesLT",
    "EntityName": null,
    "Database": "text2sql-adventure-works",
    "EntityRelationships": [
        {
            "ForeignEntity": "Product",
            "ForeignSchema": "SalesLT",
            "ForeignKeys": [
                {
                    "Column": "ProductID",
                    "ForeignColumn": "ProductID"
                }
            ],
            "ForeignDatabase": "text2sql-adventure-works",
            "FQN": "text2sql-adventure-works.SalesLT.SalesOrderDetail",
            "ForeignFQN": "text2sql-adventure-works.SalesLT.Product"
        }
    ],
    "CompleteEntityRelationshipsGraph": [
        "text2sql-adventure-works.SalesLT.SalesOrderDetail -> text2sql-adventure-works.SalesLT.Product -> text2sql-adventure-works.SalesLT.ProductCategory -> Product",
        "text2sql-adventure-works.SalesLT.SalesOrderDetail -> text2sql-adventure-works.SalesLT.SalesOrderHeader -> SalesOrderDetail"
    ],
    "Columns": [
        {
            "Name": "SalesOrderID",
            "DataType": "int",
            "Definition": null,
            "SampleValues": [71898, 71831, 71899, 71796, 71946]
        }
    ],
    "FQN": "text2sql-adventure-works.SalesLT.SalesOrderDetail"
}
```

The Schema Store structure has several critical components:
- **EntityName**: A human-readable name for the entity
- **Entity**: The actual table/view name used in SQL queries
- **Definition**: Provides a comprehensive description of what the entity contains
- **Columns**: Contains details about each column including datatype and sample values
- **EntityRelationships**: Maps the immediate relationships to other entities
- **CompleteEntityRelationshipsGraph**: Contains a directed graph of all entity relationships

Sources: [text_2_sql/data_dictionary/README.md:3-175]()

**Deployment Steps:**

1. Generate data dictionary files using the `data_dictionary_creator.py` utility
2. Upload JSON files to the specified Azure Storage container
3. Deploy the Schema Store index and indexer

```mermaid
flowchart TD
    subgraph "Data Dictionary Creation"
        Creator["DataDictionaryCreator"] 
        Database[(Database)]
        DDFiles["data_dictionary/*.json"]
    end
    
    subgraph "AI Search Deployment"
        SchemaIndexer["text-2-sql-schema-store-indexer"]
        SchemaIndex["text-2-sql-schema-store-index"]
    end
    
    Creator -->|"Extract Schema"| Database
    Creator -->|"Generate Files"| DDFiles
    DDFiles -->|"Upload to Blob Storage"| SchemaIndexer
    SchemaIndexer -->|"Index Content"| SchemaIndex
```

Sources: [text_2_sql/data_dictionary/README.md:1-176](), [text_2_sql_core/src/text_2_sql_core/data_dictionary/cli.py:1-143](), [deploy_ai_search_indexes/README.md:25-42]()

### Column Value Store Index

The Column Value Store Index contains string values from dimension tables to help the LLM identify and disambiguate entities mentioned in user questions. This avoids having to index large fact tables while still allowing the Text2SQL system to recognize entity values mentioned by users.

**Content Example (JSONL format):**
```json
{"Entity": "Product", "Schema": "SalesLT", "Database": "text2sql-adventure-works", "FQN": "text2sql-adventure-works.SalesLT.Product.ProductNumber", "Column": "ProductNumber", "Value": "WB-H098", "Synonyms": []}
{"Entity": "Product", "Schema": "SalesLT", "Database": "text2sql-adventure-works", "FQN": "text2sql-adventure-works.SalesLT.Product.ProductNumber", "Column": "ProductNumber", "Value": "VE-C304-S", "Synonyms": []}
{"Entity": "Product", "Schema": "SalesLT", "Database": "text2sql-adventure-works", "FQN": "text2sql-adventure-works.SalesLT.Product.ProductNumber", "Column": "ProductNumber", "Value": "VE-C304-M", "Synonyms": []}
```

Each line represents a single column value with its metadata, enabling semantic search over the values when a user refers to them in a question (e.g., "What are the total sales for product VE-C304-S?").

**Deployment Steps:**

1. Generate column value JSONL files using the `data_dictionary_creator.py` utility
2. Upload JSONL files to the specified Azure Storage container
3. Deploy the Column Value Store index and indexer with:
   ```
   uv run deploy.py index_type text_2_sql_column_value_store [--rebuild] [--suffix <suffix>]
   ```

Sources: [text_2_sql/data_dictionary/README.md:177-202](), [deploy_ai_search_indexes/README.md:44-60]()

### Query Cache Index

The Query Cache Index stores previous questions, their corresponding SQL queries, and optionally the results, to improve performance for similar future questions.

**Deployment Steps:**

1. Deploy the Query Cache index using the deployment script
2. Enable the Query Cache indexer if using file-based caching
3. Configure the application to use the Query Cache index

Sources: [deploy_ai_search_indexes/README.md:62-80]()

## Image Processing Index

The Image Processing Index stores processed documents with extracted layout, figures, and semantic chunks. It enables rich document analysis and retrieval for RAG applications.

### Processing Pipeline Architecture

```mermaid
flowchart TD
    Document["Document with Images"] --> LayoutAnalysisSkill["LayoutAnalysis Skill"]
    LayoutAnalysisSkill -->|"extract_file_info()"| ADI["Azure Document Intelligence"]
    ADI -->|"analyse_document()"| ExtractedContent["layout.content"]
    
    ExtractedContent --> ProcessFigures["process_figures_from_extracted_content()"]
    ProcessFigures --> Figures["layout.figures[]"]
    
    ExtractedContent --> FigureAnalysisSkill["FigureAnalysis Skill"]
    Figures --> FigureAnalysisSkill
    
    FigureAnalysisSkill -->|"Updated Figures"| MergerSkill["Layout & Figure Merger Skill"]
    ExtractedContent --> MergerSkill
    
    MergerSkill -->|"layout_merged_content"| ChunkerSkill["SemanticTextChunker Skill"]
    ChunkerSkill -->|"chunk_mark_ups"| CleanerSkill["MarkUp Cleaner Skill"]
    
    CleanerSkill -->|"final_cleaned_text"| VectorSkill["Vector Skill"]
    CleanerSkill -->|"final_sections"| IndexStorage["image_processing-index"]
    CleanerSkill -->|"final_mark_up"| IndexStorage
    CleanerSkill -->|"final_chunk_figures"| IndexStorage
    CleanerSkill -->|"final_page_number"| IndexStorage
    VectorSkill -->|"vector"| IndexStorage
```

**Key Components:**

1. **Layout Analysis Skill** (`LayoutAnalysis` class):
   - Extracts document structure using Azure Document Intelligence
   - Downloads and processes the source document from blob storage
   - Creates `LayoutHolder` objects with page content and figure metadata
   - Tracks page numbers with `PageNumberTrackingHolder` objects

2. **Figure Analysis Skill**:
   - Processes extracted figures from documents
   - Uses GPT-4o-mini to generate descriptions of visual content
   - Stores figure data in `FigureHolder` objects

3. **Semantic Text Chunker Skill** (`SemanticTextChunker` class):
   - Splits documents into semantically coherent chunks
   - Parameters:
     - `similarity_threshold`: Controls when to split chunks (default: 0.8)
     - `max_chunk_tokens`: Maximum tokens per chunk (default: 500)
     - `min_chunk_tokens`: Minimum tokens per chunk (default: 200)
   - Uses semantic similarity to merge related content
   - Preserves tables, figures, and markdown headings during chunking
   - Creates `ChunkHolder` objects with processed content

4. **MarkUp Cleaner Skill**:
   - Cleans up markup for better indexing and retrieval
   - Processes the final output before embedding

5. **Vector Skill**:
   - Generates embeddings using Azure OpenAI models
   - Creates vector representations for semantic search

**Deployment Steps:**

1. Configure environment settings in `.env` file
2. Deploy the Image Processing index with:
   ```
   uv run deploy.py index_type image_processing [--enable_page_wise_chunking True|False] [--rebuild] [--suffix <suffix>]
   ```
3. Run the indexer to process documents in the source container

Sources: [deploy_ai_search_indexes/README.md:5-22](), [image_processing/src/image_processing/layout_analysis.py:143-614](), [image_processing/src/image_processing/semantic_text_chunker.py:13-138](), [image_processing/src/image_processing/layout_holders.py:8-74]()

## Environment Configuration

All index deployments require proper environment configuration. The main settings are defined in the `.env` file:

| Setting | Description | Example |
|---------|-------------|---------|
| `AIService__AzureSearchOptions__Endpoint` | AI Search endpoint | https://your-search.search.windows.net |
| `AIService__AzureSearchOptions__Key` | AI Search key (if using key auth) | your-key |
| `AIService__AzureSearchOptions__Text2SqlSchemaStore__Index` | Schema store index name | text-2-sql-schema-store-index |
| `AIService__AzureSearchOptions__Text2SqlColumnValueStore__Index` | Column value store index name | text-2-sql-column-value-store-index |
| `AIService__AzureSearchOptions__Text2SqlQueryCache__Index` | Query cache index name | text-2-sql-query-cache-index |
| `OpenAI__Endpoint` | Azure OpenAI endpoint | https://your-openai.openai.azure.com |
| `OpenAI__EmbeddingDeployment` | Azure OpenAI embedding model deployment | text-embedding-ada-002 |
| `StorageAccount__Name` | Storage account name | yourstorageaccount |

Sources: [text_2_sql/.env.example:1-51](), [deploy_ai_search_indexes/README.md:1-84]()

## Deployment Workflow

The deployment process for AI Search indexes follows a structured workflow implemented in the `AISearch.deploy()` method. Each specialized index type extends this workflow with its own implementation details.

### Deployment Process

```mermaid
flowchart TD
    EnvSetup["1. Environment Setup<br>.env configuration"] --> DataGen["2. Data Generation<br>Data Dictionary Creator"]
    DataGen --> StorageUpload["3. Upload to Blob Storage<br>JSON/JSONL files"]
    
    StorageUpload --> Deploy["4. Call AISearch.deploy()"]
    
    Deploy --> DataSource["5. deploy_data_source()<br>Create data source connection"]
    Deploy --> SynMap["6. deploy_synonym_map()<br>Setup synonym maps if needed"]
    Deploy --> Index["7. deploy_index()<br>Create or update index"]
    Deploy --> Skillset["8. deploy_skillset()<br>Configure processing pipeline"]
    Deploy --> Indexer["9. deploy_indexer()<br>Setup indexer"]
    
    Indexer --> RunIndexer["10. run_indexer()<br>Start indexing process"]
```

### Running Deployment Scripts

The deployment scripts are located in the `deploy_ai_search_indexes` directory and can be run for each index type:

```bash
# From the deploy_ai_search_indexes/src/deploy_ai_search_indexes directory
uv run deploy.py index_type <index_type> [options]
```

#### Index Types and Options

| Index Type | Description | Specific Options |
|------------|-------------|------------------|
| `text_2_sql_schema_store` | Deploys the schema store index | `--single_data_dictionary_file` |
| `text_2_sql_column_value_store` | Deploys the column value store index | None |
| `text_2_sql_query_cache` | Deploys the query cache index | `--enable_cache_indexer`, `--single_cache_file` |
| `image_processing` | Deploys the image processing index | `--enable_page_wise_chunking` |

#### Common Options

- `--rebuild`: Delete and rebuild the index completely
- `--suffix <suffix>`: Apply a suffix to the deployed resources for testing purposes
- `--run_indexer`: Automatically run the indexer after deployment

### AISearch Base Implementation

The core deployment logic in `AISearch.deploy()` handles:

1. Connecting to AI Search using the endpoint and credentials from environment
2. Creating or updating the data source configuration
3. Setting up synonym maps if specified
4. Deploying the index with vector search and semantic search capabilities
5. Creating the skillset with all processing steps
6. Configuring and deploying the indexer
7. Optionally running the indexer

Each specialized subclass implements the abstract methods to define the specific fields, skills, and indexer configuration required for that index type.

Sources: [deploy_ai_search_indexes/README.md:1-84](), [deploy_ai_search_indexes/src/deploy_ai_search_indexes/ai_search.py:742-751]()

## Data Dictionary Creator

The system includes a specialized command-line utility to automatically generate data dictionaries for various database engines. These data dictionaries are then uploaded to Azure Storage where they are indexed by the AI Search indexes.

### Data Dictionary Creator Architecture

```mermaid
flowchart TD
    subgraph "CLI Command"
        CLI["data_dictionary CLI"]
    end

    subgraph "Creator Classes"
        DDCreator["DataDictionaryCreator"]
        TsqlCreator["TsqlDataDictionaryCreator"]
        PostgresCreator["PostgresDataDictionaryCreator"]
        SnowflakeCreator["SnowflakeDataDictionaryCreator"]
        DatabricksCreator["DatabricksDataDictionaryCreator"]
        
        DDCreator --> TsqlCreator
        DDCreator --> PostgresCreator
        DDCreator --> SnowflakeCreator
        DDCreator --> DatabricksCreator
    end
    
    subgraph "Database Engines"
        TSQL[(TSQL)]
        Postgres[(PostgreSQL)]
        Snowflake[(Snowflake)]
        Databricks[(Databricks)]
    end
    
    subgraph "Output Files"
        EntityJSON["entities/*.json"]
        SingleJSON["entities.json"]
        ColumnValueJSONL["column_values.jsonl"]
    end
    
    CLI --> TsqlCreator
    CLI --> PostgresCreator
    CLI --> SnowflakeCreator
    CLI --> DatabricksCreator
    
    TsqlCreator <--> TSQL
    PostgresCreator <--> Postgres
    SnowflakeCreator <--> Snowflake
    DatabricksCreator <--> Databricks
    
    TsqlCreator --> EntityJSON
    TsqlCreator --> SingleJSON
    TsqlCreator --> ColumnValueJSONL
    
    PostgresCreator --> EntityJSON
    PostgresCreator --> SingleJSON
    PostgresCreator --> ColumnValueJSONL
    
    SnowflakeCreator --> EntityJSON
    SnowflakeCreator --> SingleJSON
    SnowflakeCreator --> ColumnValueJSONL
    
    DatabricksCreator --> EntityJSON
    DatabricksCreator --> SingleJSON
    DatabricksCreator --> ColumnValueJSONL
    
    subgraph "AI Search Index Deployment"
        EntityJSON --> SchemaStoreIndex["text_2_sql_schema_store-index"]
        SingleJSON --> SchemaStoreIndex
        ColumnValueJSONL --> ColumnStoreIndex["text_2_sql_column_value_store-index"]
    end
```

### Usage

To generate a data dictionary:

1. Configure your database connection in `.env`
2. Run the command from within the `text_2_sql_core` directory:
   ```
   uv run data_dictionary <DATABASE_ENGINE> [OPTIONS]
   ```

   Where `<DATABASE_ENGINE>` is one of:
   - `tsql` - Microsoft SQL Server
   - `postgres` - PostgreSQL
   - `snowflake` - Snowflake
   - `databricks` - Databricks

   Available options:
   - `--output-directory` or `-o`: Optional directory for output files
   - `--single_file` or `-s`: Write all schemas to a single file
   - `--generate_definitions` or `-gen`: Use OpenAI to generate descriptions

3. Upload the generated files to Azure Storage containers:
   - Upload `entities.json` (or the individual entity JSON files) to the schema store blob container
   - Upload `column_values.jsonl` to the column value store blob container

The data dictionary creator will extract schema information, table/column definitions, relationships, and sample data to create comprehensive metadata files that power the Text2SQL system.

Sources: [text_2_sql/data_dictionary/README.md:206-246](), [text_2_sql_core/src/text_2_sql_core/data_dictionary/cli.py:16-139]()

## References

The AI Search indexes are referenced by the following components:

1. **Text-to-SQL System**: Uses the Schema Store, Column Value Store, and Query Cache indexes
2. **Image Processing System**: Uses the Image Processing index for document analysis

For more details on how these systems utilize the indexes, see [Text-to-SQL System](#2) and [Image Processing System](#3).

---

# Page: Setup and Deployment Guide

# Setup and Deployment Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.devcontainer/Dockerfile](.devcontainer/Dockerfile)
- [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json)
- [.github/CODEOWNERS](.github/CODEOWNERS)
- [.github/dependabot.yaml](.github/dependabot.yaml)
- [.github/workflows/codeql-analysis.yaml](.github/workflows/codeql-analysis.yaml)
- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SUPPORT.md](SUPPORT.md)
- [text_2_sql/.env.example](text_2_sql/.env.example)
- [text_2_sql/GETTING_STARTED.md](text_2_sql/GETTING_STARTED.md)
- [text_2_sql/README.md](text_2_sql/README.md)

</details>



This guide provides comprehensive instructions for setting up and deploying the DSTToolkit Text2SQL and Image Processing systems. The guide covers prerequisite Azure resources, environment configurations, code installation, and deployment steps for both systems.

## Overview and Prerequisites

Before beginning the setup process, ensure you have the following:

1. An Azure subscription with permissions to create resources
2. Python 3.11 or higher installed
3. Git installed to clone the repository
4. Access to create and manage the following Azure resources:
   - Azure OpenAI with GPT-4o-mini model and embedding models
   - Azure SQL Server (or other supported database)
   - Azure AI Search service
   - Azure Storage Account
   - Azure Document Intelligence (for image processing)

Sources: [text_2_sql/README.md:3-5](), [text_2_sql/GETTING_STARTED.md:1-7](), [pyproject.toml:3-6]()

## Deployment Architecture

The setup involves deploying several interconnected components across both systems. Here's the high-level deployment architecture:

```mermaid
flowchart TD
    subgraph "Azure Resources"
        AOAI["Azure OpenAI Service"]
        AIS["Azure AI Search"]
        SA["Azure Storage Account"]
        DB[(Database)]
        ADI["Azure Document Intelligence"]
    end

    subgraph "Text2SQL Components"
        T2S["Text2SQL Core"]
        DD["Data Dictionary"]
        AGen["AutoGen Implementation"]
    end

    subgraph "Image Processing Components"
        IP["Image Processing Pipeline"]
    end

    subgraph "Local Dev Environment"
        DevCont["Dev Container / Local Setup"]
    end

    DevCont -->|1. Clone & Configure| T2S
    DevCont -->|1. Clone & Configure| IP
    DevCont -->|2. Deploy Indexes| AIS
    DevCont -->|3. Generate & Upload| DD
    DD -->|4. Store| SA
    SA -->|5. Index| AIS
    T2S -->|6. Connect| AOAI
    T2S -->|6. Connect| AIS
    T2S -->|6. Connect| DB
    AGen -->|7. Use| T2S
    IP -->|8. Connect| AOAI
    IP -->|8. Connect| ADI
    IP -->|8. Connect| AIS
    IP -->|8. Connect| SA
```

Sources: [text_2_sql/GETTING_STARTED.md:1-27](), [pyproject.toml:24-31]()

## 1. Repository Setup

Begin by cloning the repository and setting up your development environment.

### Local Setup

```bash
# Clone the repository
git clone https://github.com/microsoft/dstoolkit-text2sql-and-imageprocessing.git
cd dstoolkit-text2sql-and-imageprocessing
```

### Dev Container Setup (Optional)

The repository includes a development container configuration for Visual Studio Code:

1. Install Docker
2. Install the VS Code Remote Development extension
3. Open the repository in VS Code
4. When prompted, click "Reopen in Container"

The dev container includes all necessary tools and dependencies, including:
- Python 3.x
- ODBC drivers for SQL Server
- Azure CLI
- uv package manager

Sources: [.devcontainer/Dockerfile:1-20](), [.devcontainer/devcontainer.json:1-24]()

## 2. Azure Resources Deployment

Before continuing with code setup, you must provision the necessary Azure resources.

### Required Azure Resources

```mermaid
flowchart LR
    subgraph "Core Azure Resources"
        direction TB
        AOAI["Azure OpenAI Service"]
        AIS["Azure AI Search"]
        SA["Azure Storage Account"]
    end

    subgraph "Database Options"
        TSQL["Azure SQL Server"]
        PG["PostgreSQL"]
        SF["Snowflake"]
        DB["Databricks"]
        SL["SQLite"]
    end

    subgraph "Image Processing"
        ADI["Azure Document Intelligence"]
    end

    DEV["Developer"] -->|"Provision"| AOAI
    DEV -->|"Provision"| AIS
    DEV -->|"Provision"| SA
    DEV -->|"Provision (one or more)"| TSQL
    DEV -->|"Provision (one or more)"| PG
    DEV -->|"Provision (one or more)"| SF
    DEV -->|"Provision (one or more)"| DB
    DEV -->|"Provision (one or more)"| SL
    DEV -->|"Provision (for image processing)"| ADI
```

Sources: [text_2_sql/GETTING_STARTED.md:7-7](), [deploy_ai_search_indexes/pyproject.toml:10-17](), [image_processing/pyproject.toml:10-35]()

## 3. AI Search Indexes Deployment

The system requires several AI Search indexes for its operation. Follow these steps to deploy them:

```bash
# Navigate to the deploy_ai_search_indexes directory
cd deploy_ai_search_indexes

# Create a .env file from the example
cp .env.example .env

# Edit the .env file with your Azure resource information
# Install dependencies
uv sync

# Deploy the AI Search indexes
python -m deploy_ai_search_indexes.deploy
```

The deployment creates the following indexes:
- Schema Store Index - for database schema metadata 
- Column Value Store Index - for sample data values
- Query Cache Index - for caching previously executed queries

Sources: [text_2_sql/GETTING_STARTED.md:7-9](), [deploy_ai_search_indexes/pyproject.toml:10-17]()

## 4. Data Dictionary Generation and Upload

The Data Dictionary is crucial for the Text2SQL system to understand your database schema:

```mermaid
flowchart TD
    subgraph "Data Dictionary Generation"
        DC["Data Dictionary Creator"]
        DC -->|"Select Database Type"| Creators
        
        subgraph "Creators"
            TSQLC["TSQL Creator"]
            PGC["Postgres Creator"]
            SFC["Snowflake Creator"]
            DBC["Databricks Creator"]
            SQLC["SQLite Creator"]
        end
        
        TSQLC -->|"Generate"| Json["JSON Schema Files"]
        PGC -->|"Generate"| Json
        SFC -->|"Generate"| Json
        DBC -->|"Generate"| Json
        SQLC -->|"Generate"| Json
        
        Json -->|"Generate"| CVS["Column Value Store JSONL"]
    end
    
    subgraph "Upload & Index"
        Json -->|"Upload"| SA["Storage Account"]
        CVS -->|"Upload"| SA
        SA -->|"Index"| AIS["AI Search"]
    end
```

### Steps:

1. Set up your database connection in the `.env` file:

```bash
cd text_2_sql_core
cp .env.example .env
# Edit the .env file with your database connection details
```

2. Generate the data dictionary for your database:

```bash
# For SQL Server
python -m text_2_sql_core.data_dictionary.tsql_data_dictionary_creator

# For PostgreSQL
python -m text_2_sql_core.data_dictionary.postgres_data_dictionary_creator

# For other supported databases
# Use the corresponding creator module
```

3. Upload the generated files to Azure Storage Account containers, which will be automatically indexed.

Sources: [text_2_sql/README.md:134-204](), [text_2_sql/GETTING_STARTED.md:17-19](), [text_2_sql/text_2_sql_core/src/text_2_sql_core/data_dictionary/postgres_data_dictionary_creator.py:1-121]()

## 5. Text2SQL Core Setup

Set up the Text2SQL core component:

```bash
# Navigate to text_2_sql_core
cd text_2_sql_core

# Create environment file
cp .env.example .env
# Edit the .env file with your configuration

# Install dependencies
uv sync

# For additional database connectors, install optional dependencies
# For PostgreSQL
uv sync --extra postgres

# For Snowflake
uv sync --extra snowflake

# For Databricks
uv sync --extra databricks

# For SQLite
uv sync --extra sqlite
```

### Environment Configuration Options

The `.env` file contains various configuration options that allow you to customize the behavior of the Text2SQL system:

#### Authentication Options

```
IdentityType=<identityType>  # Can be system_assigned, user_assigned, or key
```

#### Text2SQL Core Options

```
Text2Sql__DatabaseEngine=<DatabaseEngine>  # TSQL, Postgres, Snowflake, Databricks, or SQLite
Text2Sql__UseQueryCache=<Boolean>  # Determines if the Query Cache will be used (default: True)
Text2Sql__PreRunQueryCache=<Boolean>  # Determines if results from Query Cache will be pre-run (default: True)
Text2Sql__UseColumnValueStore=<Boolean>  # Determines if Column Value Store will be used (default: True)
Text2Sql__GenerateFollowUpSuggestions=<Boolean>  # Determines if follow-up questions will be generated (default: True)
Text2Sql__RowLimit=<Integer>  # Maximum number of rows returned in a query (default: 100)
```

#### Azure OpenAI Configuration

```
OpenAI__CompletionDeployment=<openAICompletionDeploymentId>  # Used for data dictionary creator
OpenAI__MiniCompletionDeployment=<OpenAIMiniCompletionDeploymentId>  # Used for agentic text2sql
OpenAI__Endpoint=<openAIEndpoint>
OpenAI__ApiKey=<openAIKey>  # Only needed if not using identity-based authentication
OpenAI__ApiVersion=<openAIApiVersion>
```

#### Azure AI Search Configuration

```
AIService__AzureSearchOptions__Endpoint=<AI search endpoint>
AIService__AzureSearchOptions__Key=<AI search key>  # Only needed if not using identity-based authentication
AIService__AzureSearchOptions__Text2SqlSchemaStore__Index=<Schema store index name>
AIService__AzureSearchOptions__Text2SqlSchemaStore__SemanticConfig=<Schema store semantic config>
AIService__AzureSearchOptions__Text2SqlQueryCache__Index=<Query cache index name>
AIService__AzureSearchOptions__Text2SqlQueryCache__SemanticConfig=<Query cache semantic config>
AIService__AzureSearchOptions__Text2SqlColumnValueStore__Index=<Column value store index name>
```

Customize these options to tailor the Text2SQL system to your specific needs.

Sources: [text_2_sql/GETTING_STARTED.md:11-16](), [text_2_sql/.env.example:1-50]()

## 6. AutoGen Implementation Setup

The AutoGen implementation uses the Text2SQL core to provide an agentic approach:

```bash
# Navigate to autogen directory
cd autogen

# Install dependencies
uv sync

# For additional database connectors
uv sync --extra <DATABASE_ENGINE>
```

Once set up, you can test the implementation by running the provided notebook:
```bash
# Open and run the notebook
jupyter notebook "Iteration 5 - Agentic Vector Based Text2SQL.ipynb"
```

Sources: [text_2_sql/GETTING_STARTED.md:21-27](), [text_2_sql/README.md:38-56]()

## 7. Image Processing Setup

Set up the Image Processing component:

```bash
# Navigate to image_processing
cd image_processing

# Create environment file
cp .env.example .env
# Edit the .env file with your configuration

# Install dependencies
uv sync
```

The `.env` file should include configuration for:
- Azure OpenAI API key and endpoint
- Azure Document Intelligence key and endpoint
- Azure AI Search key and endpoint
- Azure Storage Account connection details

Sources: [image_processing/pyproject.toml:1-51]()

## 8. Database Connector Configuration

The system supports multiple database engines through a connector factory pattern. Configure the appropriate connector based on your database:

### TSQL (SQL Server)

Required environment variables:
```
Text2Sql__DatabaseEngine=TSQL
Text2Sql__Tsql__ConnectionString=your-connection-string
Text2Sql__Tsql__Database=your-database
```

### PostgreSQL

Required environment variables:
```
Text2Sql__DatabaseEngine=Postgres
# Option 1: Connection string
Text2Sql__Postgres__ConnectionString=postgresql://username:password@hostname:port/database

# Option 2: Individual parameters
Text2Sql__Postgres__Database=your-database
Text2Sql__Postgres__User=your-username
Text2Sql__Postgres__Password=your-password
Text2Sql__Postgres__Port=5432
Text2Sql__Postgres__ServerHostname=your-server-hostname
```

### Snowflake

Required environment variables:
```
Text2Sql__DatabaseEngine=Snowflake
Text2Sql__Snowflake__User=your-snowflake-user
Text2Sql__Snowflake__Password=your-snowflake-password
Text2Sql__Snowflake__Account=your-snowflake-account
Text2Sql__Snowflake__Warehouse=your-snowflake-warehouse
Text2Sql__Snowflake__Database=your-snowflake-database
```

### Databricks

Required environment variables:
```
Text2Sql__DatabaseEngine=Databricks
Text2Sql__Databricks__Catalog=your-databricks-catalog
Text2Sql__Databricks__ServerHostname=your-databricks-server-hostname
Text2Sql__Databricks__HttpPath=your-databricks-http-path
Text2Sql__Databricks__AccessToken=your-databricks-access-token
```

### SQLite

Required environment variables:
```
Text2Sql__DatabaseEngine=SQLite
Text2Sql__SQLite__ConnectionString=your-sqlite-connection-string
```

Sources: [text_2_sql/.env.example:4-50]()

## 9. Production Deployment Considerations

When deploying to production, consider the following:

### Security Recommendations

1. Use managed identities for Azure resources where possible
2. Limit database permissions to read-only for the Text2SQL service
3. Add validation of SQL queries before execution
4. Consider data masking for sensitive columns

```mermaid
flowchart LR
    subgraph "Security Considerations"
        direction TB
        MI["Managed Identities"]
        RP["Read-Only Permissions"]
        SQ["SQL Query Validation"]
        DM["Data Masking"]
        RLS["Row Level Security"]
    end

    User["End User"] -->|"Access"| App["Application"]
    App -->|"Uses"| T2S["Text2SQL"]
    T2S -->|"Executes"| SQ
    SQ -->|"Validates"| DB["Database"]
    DB -->|"Applies"| RLS
    DB -->|"Applies"| DM
    T2S -->|"Uses"| MI
    DB -->|"Grants"| RP
```

### Performance Optimization

1. Pre-populate the query cache with common questions
2. Implement an effective caching strategy
3. Use pre-assembled views to avoid complex joins
4. Consider scaling options for the Azure resources

Sources: [text_2_sql/README.md:220-229](), [text_2_sql/README.md:76-83]()

## 10. Troubleshooting

### Common Issues

| Issue | Possible Solution |
|-------|------------------|
| Connection errors to Azure resources | Verify network connectivity, check firewall settings, ensure correct connection strings |
| Data dictionary generation failures | Verify database permissions, check connection details |
| SQL query execution errors | Validate SQL syntax, check database permissions, verify column names |
| Image processing failures | Ensure Document Intelligence service is properly configured, check file format support |
| Cache indexing issues | Check storage account permissions, verify index definitions |

### Logging

The system uses Python's logging module. To enable detailed logging, set the log level in your environment variables:

```
LOGGING_LEVEL=DEBUG
```

Sources: [text_2_sql/text_2_sql_core/src/text_2_sql_core/connectors/postgres_sql.py:80-132]()

## 11. Development Tools

The repository includes several development tools:

1. **Pre-commit hooks**: Run quality checks before committing
   ```bash
   # Install pre-commit
   pip install pre-commit
   pre-commit install
   ```

2. **Dev Container**: Provides a consistent development environment

3. **UV Package Manager**: Used for dependency management
   ```bash
   # Update dependencies
   uv sync
   ```

4. **Code Formatting**: Uses Black and Ruff for code formatting

Sources: [.pre-commit-config.yaml:1-57]()

## Conclusion

This guide provides the essential steps to set up and deploy the DSTToolkit Text2SQL and Image Processing systems. Follow the steps in sequence to ensure a proper setup. For advanced configurations or customizations, refer to the source code and READMEs in the respective directories.

For issues or support, please refer to the [SUPPORT.md]() file or create an issue in the GitHub repository.