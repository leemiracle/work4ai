<!-- source: DeepWiki mcp.deepwiki.com · repo OpenDCAI/DataFlow · extra page Database Connectors · fetched 2026-11-02 -->

# Database Connectors

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [dataflow/operators/text2sql/eval/sql_execution_classifier.py](dataflow/operators/text2sql/eval/sql_execution_classifier.py)
- [dataflow/operators/text2sql/filter/sql_execution_filter.py](dataflow/operators/text2sql/filter/sql_execution_filter.py)
- [dataflow/operators/text2sql/generate/sql_generator.py](dataflow/operators/text2sql/generate/sql_generator.py)
- [dataflow/operators/text2sql/generate/sql_variation_generator.py](dataflow/operators/text2sql/generate/sql_variation_generator.py)
- [dataflow/operators/text2sql/generate/text2sql_cot_generator.py](dataflow/operators/text2sql/generate/text2sql_cot_generator.py)
- [dataflow/operators/text2sql/generate/text2sql_prompt_generator.py](dataflow/operators/text2sql/generate/text2sql_prompt_generator.py)
- [dataflow/operators/text2sql/generate/text2sql_question_generator.py](dataflow/operators/text2sql/generate/text2sql_question_generator.py)
- [dataflow/prompts/text2sql.py](dataflow/prompts/text2sql.py)
- [dataflow/statics/pipelines/api_pipelines/text2vecsql_pipeline_gen.py](dataflow/statics/pipelines/api_pipelines/text2vecsql_pipeline_gen.py)
- [dataflow/utils/text2sql/base.py](dataflow/utils/text2sql/base.py)
- [dataflow/utils/text2sql/database_connector/mysql_connector.py](dataflow/utils/text2sql/database_connector/mysql_connector.py)
- [dataflow/utils/text2sql/database_connector/sqlite_connector.py](dataflow/utils/text2sql/database_connector/sqlite_connector.py)
- [dataflow/utils/text2sql/database_connector/sqlite_vec_connector.py](dataflow/utils/text2sql/database_connector/sqlite_vec_connector.py)
- [dataflow/utils/text2sql/database_manager.py](dataflow/utils/text2sql/database_manager.py)

</details>



Database Connectors provide a unified abstraction layer for interacting with different database systems in DataFlow's Text2SQL workflows [dataflow/utils/text2sql/base.py:26-76](). Each connector implements a common interface for connection management, query execution, and schema extraction, enabling operators like `SQLGenerator` [dataflow/operators/text2sql/generate/sql_generator.py:19-25]() and `SQLExecutionFilter` [dataflow/operators/text2sql/filter/sql_execution_filter.py:13-15]() to work seamlessly across SQLite, SQLite-Vec (with vector embeddings and `lembed()` support) [dataflow/utils/text2sql/database_connector/sqlite_vec_connector.py:14-47](), and MySQL databases [dataflow/utils/text2sql/database_manager.py:92-98]().

For information about how these connectors are used by the `DatabaseManager` for parallel query execution and result comparison, see [3.6.2 Query Execution and Comparison](). For the overall database management architecture, see [3.6 Database Management]().

---

## Connector Architecture

All database connectors inherit from `DatabaseConnectorABC` defined in [dataflow/utils/text2sql/base.py:26-76](), which enforces a standard interface for database operations. The concrete implementations are registered in the `DatabaseManager.CONNECTORS` dictionary [dataflow/utils/text2sql/database_manager.py:92-98]().

**Connector Class Hierarchy and Registration**

Title: Database Connector Class Structure
```mermaid
classDiagram
    class DatabaseConnectorABC {
        <<abstract>>
        +connect(connection_info Dict) Any*
        +execute_query(connection, sql str, params Tuple) QueryResult*
        +explain_query(connection, sql str, params Tuple) QueryResult*
        +get_schema_info(connection, db_id str) Dict*
        +discover_databases(config Dict) Dict*
        +get_number_of_special_column(connection) int*
        +validate_connection(connection) bool
        +close(connection) void
        +logger Logger
    }
    
    class SQLiteConnector {
        +connect(connection_info) sqlite3.Connection
        +execute_query(connection, sql, params) QueryResult
        +explain_query(connection, sql, params) QueryResult
        +get_schema_info(connection, db_id) Dict
        +discover_databases(config) Dict
        +get_number_of_special_column(connection) int
        -_get_table_info(connection, table_name) Dict
        -_get_db_details(schema, db_id) str
    }
    
    class SQLiteVecConnector {
        -_thread_local threading.local
        -_class_lock threading.Lock
        -_db_init_locks Dict[str, Lock]
        -_initialized_dbs set
        -_sqlite_vec module
        -_sqlite_lembed module
        +connect(connection_info) sqlite3.Connection
        +close(connection) void
        +execute_query(connection, sql, params) QueryResult
        +explain_query(connection, sql, params) QueryResult
        +get_schema_info(connection, db_id) Dict
        +discover_databases(config) Dict
        +get_number_of_special_column(connection) int
        -_ensure_vec_available() void
        -_ensure_lembed_available() void
        -_initialize_database_disk_state(connection_info) void
        -_ensure_trusted_schema_enabled(connection) void
    }
    
    class MySQLConnector {
        +logger Logger
        +connect(connection_info) pymysql.Connection
        +execute_query(connection, sql, params) QueryResult
        +explain_query(connection, sql, params) QueryResult
        +get_schema_info(connection, db_id) Dict
        +discover_databases(config) Dict
        +get_number_of_special_column(connection) int
    }
    
    class DatabaseManager {
        +CONNECTORS Dict[str, Type]
        +db_type str
        +connector DatabaseConnectorABC
        +databases Dict[str, DatabaseInfo]
        +cache CacheManager
        +embedding_serving LLMServingABC
        +get_connection(db_id) ContextManager
        +batch_execute_queries(queries) List[QueryResult]
        -_discover_databases() void
    }
    
    DatabaseConnectorABC <|-- SQLiteConnector : "implements"
    DatabaseConnectorABC <|-- SQLiteVecConnector : "implements"
    DatabaseConnectorABC <|-- MySQLConnector : "implements"
    DatabaseManager --> DatabaseConnectorABC : "instantiates via CONNECTORS registry"
```
Sources: [dataflow/utils/text2sql/base.py:26-76](), [dataflow/utils/text2sql/database_connector/sqlite_connector.py:12-113](), [dataflow/utils/text2sql/database_connector/sqlite_vec_connector.py:14-163](), [dataflow/utils/text2sql/database_manager.py:84-128]()

---

## Abstract Connector Interface

The `DatabaseConnectorABC` class defines six abstract methods that all concrete connectors must implement:

| Method | Purpose | Return Type |
|--------|---------|-------------|
| `connect()` | Establish connection to database [dataflow/utils/text2sql/base.py:33-35]() | Database-specific connection object |
| `execute_query()` | Execute SQL and return results [dataflow/utils/text2sql/base.py:37-41]() | `QueryResult` |
| `explain_query()` | Get query execution plan [dataflow/utils/text2sql/base.py:43-47]() | `QueryResult` |
| `get_schema_info()` | Extract complete schema information [dataflow/utils/text2sql/base.py:49-53]() | `Dict[str, Any]` |
| `discover_databases()` | Find available databases [dataflow/utils/text2sql/base.py:55-59]() | `Dict[str, DatabaseInfo]` |
| `get_number_of_special_column()` | Count columns with special semantics (e.g., embeddings) [dataflow/utils/text2sql/base.py:76]() | `int` |

Two additional non-abstract methods provide shared functionality:

- `validate_connection()`: Tests if a connection is still active by executing `SELECT 1` [dataflow/utils/text2sql/base.py:61-68]().
- `close()`: Safely closes a connection with error handling [dataflow/utils/text2sql/base.py:70-76]().

Sources: [dataflow/utils/text2sql/base.py:26-76]()

---

## Data Structures

### DatabaseInfo

Stores connection metadata for discovered databases:

```python
@dataclass
class DatabaseInfo:
    db_id: str                      # Unique identifier
    db_type: str                    # 'sqlite', 'sqlite-vec', or 'mysql'
    connection_info: Dict[str, Any] # Connector-specific parameters
    metadata: Dict[str, Any]        # Additional information (file path, size, etc.)
```
Sources: [dataflow/utils/text2sql/base.py:8-14]()

### QueryResult

Standardized format for all query results across all database connectors:

```python
@dataclass
class QueryResult:
    success: bool                    # Whether execution succeeded
    data: List[Dict[str, Any]]       # Result rows as dictionaries
    columns: List[str]               # Column names
    error: Optional[str]             # Error message if failed
    row_count: int                   # Number of rows returned
```
This structure enables uniform error handling and result processing across `DatabaseManager` batch execution methods [dataflow/utils/text2sql/base.py:17-23]().

Sources: [dataflow/utils/text2sql/base.py:17-23]()

---

## SQLite Connector

The `SQLiteConnector` provides standard SQLite database access with read-only enforcement and M-Schema generation.

### Connection Management

Connections are established with safety constraints:
- **Timeout**: 30-second connection timeout to prevent locking [dataflow/utils/text2sql/database_connector/sqlite_connector.py:16]().
- **Row Factory**: `sqlite3.Row` for dict-like access to query results [dataflow/utils/text2sql/database_connector/sqlite_connector.py:17]().
- **Read-Only Mode**: `PRAGMA query_only = ON` prevents unintended write operations during analysis [dataflow/utils/text2sql/database_connector/sqlite_connector.py:18]().

### Query Execution

The `execute_query()` method handles parameterized queries with defensive tuple wrapping and exception logging [dataflow/utils/text2sql/database_connector/sqlite_connector.py:21-58](). Results are converted into dictionaries using column metadata extracted from `cursor.description` [dataflow/utils/text2sql/database_connector/sqlite_connector.py:37-46]().

### Schema Extraction Formats

The connector generates schema information in multiple formats:
1. **DDL Format**: Retrieved directly from `sqlite_master` [dataflow/utils/text2sql/database_connector/sqlite_connector.py:97-108]().
2. **M-Schema Format**: Generated by `_get_db_details()` to structure table columns, types, nullability, primary keys, foreign keys, and sample rows for LLM prompt consumption [dataflow/utils/text2sql/database_connector/sqlite_connector.py:115-172]().

Sources: [dataflow/utils/text2sql/database_connector/sqlite_connector.py:12-181]()

---

## SQLiteVec Connector & Vector Databases with `lembed()` Support

The `SQLiteVecConnector` extends SQLite with vector similarity search capabilities via the `sqlite-vec` and `sqlite-lembed` extensions, supporting in-database model-based vector embedding generation through `lembed()` [dataflow/utils/text2sql/database_connector/sqlite_vec_connector.py:14-47]().

### Thread-Local Connection Architecture

Title: "SQLiteVecThreadSafeConnectionLifecycle"
```mermaid
graph TB
    subgraph "Connection Request Flow"
        A["connect(connection_info)"] --> B{"Connection exists<br/>in thread_local?"}
        B -->|Yes| C["Return existing<br/>connection"]
        B -->|No| D{"DB initialized<br/>in _initialized_dbs?"}
    end
    
    subgraph "One-Time Initialization (Class-Level Lock)"
        D -->|No| E["Acquire _class_lock"]
        E --> F["_initialize_database_disk_state(connection_info)"]
        F --> G["Load sqlite-vec extension"]
        G --> H["Load sqlite-lembed extension"]
        H --> I["Register model in<br/>main.lembed_models"]
        I --> J["Add to _initialized_dbs"]
        J --> K["Release _class_lock"]
    end
    
    subgraph "Per-Thread Setup (File Lock)"
        D -->|Yes| L["Create new sqlite3.Connection"]
        K --> L
        L --> M["Acquire FileLock"]
        M --> N["Enable load_extension"]
        N --> O["Load sqlite-vec"]
        O --> P["Load sqlite-lembed"]
        P --> Q["Enable trusted_schema"]
        Q --> R["Insert into temp.lembed_models<br/>OR<br/>Insert into main.lembed_models"]
        R --> S["Release FileLock"]
        S --> T["Store in _thread_local.connections"]
        T --> U["Return connection"]
    end
    
    C --> U
```
Sources: [dataflow/utils/text2sql/database_connector/sqlite_vec_connector.py:48-163]()

**Key Components:**
1. **Thread-Local Storage**: Each thread maintains its own connection dictionary via `self._thread_local.connections` [dataflow/utils/text2sql/database_connector/sqlite_vec_connector.py:21, 60-63]().
2. **Class-Level Tracking**: `_initialized_dbs` tracks databases that have completed disk-level setup [dataflow/utils/text2sql/database_connector/sqlite_vec_connector.py:17, 68-72]().
3. **File Locking**: `FileLock` ensures process-safe access during extension loading [dataflow/utils/text2sql/database_connector/sqlite_vec_connector.py:90-94]().

### Extension Loading and `lembed()` Support

The connector lazy-loads `sqlite_vec` and `sqlite_lembed` [dataflow/utils/text2sql/database_connector/sqlite_vec_connector.py:24-46](). When enabled via configuration (`enable_lembed`), it integrates model files (such as GGUF embedding models) directly into SQLite via `lembed_model_from_file()`, registering them into `main.lembed_models` or `temp.lembed_models` [dataflow/utils/text2sql/database_connector/sqlite_vec_connector.py:105-112, 151-159](). This allows executing SQL queries containing `lembed('model_name', 'text')` expressions to dynamically calculate embeddings in-database.

### Schema Extraction with Vector Tables

The `SQLiteVecConnector.get_schema_info()` method detects virtual vector tables by checking for `USING vec0` in CREATE statements [dataflow/utils/text2sql/database_connector/sqlite_vec_connector.py:472, 488]().

Title: "SQLiteVecVectorTableSchemaDetection"
```mermaid
graph TD
    A["get_schema_info(connection, db_id)"] --> B["Query sqlite_master for tables"]
    B --> C{"For each table"}
    C --> D["Get CREATE statement"]
    D --> E{"Is 'USING vec0' in<br/>create_statement?"}
    E -->|Yes| F["Set is_vec_table = True"]
    E -->|No| G["Set is_vec_table = False"]
    F --> H["_get_table_info(connection, table_name, create_statement)"]
    G --> H
    H --> I["Get PRAGMA table_info()"]
    I --> J{"is_vec_table?"}
    J -->|Yes| K["Skip sample data retrieval<br/>Skip foreign keys<br/>Return original CREATE VIRTUAL TABLE"]
    J -->|No| L["Get foreign keys from PRAGMA"]
    L --> M["Build columns_to_select list<br/>excluding '*_embedding' columns"]
    M --> N["SELECT columns FROM table LIMIT 3"]
    N --> O["Generate INSERT statements"]
    O --> P["Return table_info with samples"]
    K --> Q["Return table_info without samples"]
    P --> R["Aggregate all tables into schema"]
    Q --> R
    R --> S["Call _get_db_details(schema)"]
    S --> T["Return complete schema Dict"]
```
Sources: [dataflow/utils/text2sql/database_connector/sqlite_vec_connector.py:426-545]()

---

## MySQL Connector

The `MySQLConnector` provides enterprise MySQL connectivity with transaction safety. It enforces read-only access via `SET SESSION TRANSACTION READ ONLY` [dataflow/utils/text2sql/database_connector/mysql_connector.py:30]() and uses `pymysql.cursors.DictCursor` for dictionary results [dataflow/utils/text2sql/database_connector/mysql_connector.py:22](). It extracts schema details from `information_schema.columns` and `information_schema.key_column_usage` [dataflow/utils/text2sql/database_connector/mysql_connector.py:123-168]().

Sources: [dataflow/utils/text2sql/database_connector/mysql_connector.py:9-168]()

---

## Schema Information Flow

**Schema Extraction and Caching Architecture:**

Title: "DatabaseSchemaCachingFlow"
```mermaid
graph TB
    subgraph "Operator Layer"
        OpA["SQLByColumnGenerator.run()"]
        OpB["Text2SQLQuestionGenerator.run()"]
        OpC["Text2SQLPromptGenerator.run()"]
    end
    
    subgraph "DatabaseManager API"
        API1["get_create_statements_and_insert_statements(db_id)"]
        API2["get_db_details(db_id)"]
        PRIV["_get_schema(db_id)"]
    end
    
    subgraph "CacheManager"
        CG["cache.get('schema', db_id)"]
        CS["cache.set(schema, 'schema', db_id)"]
        CL["_cache Dict[str, Any]"]
    end
    
    subgraph "Connector Layer"
        CONN["connector.get_schema_info(conn, db_id)"]
        GTI["_get_table_info(connection, table_name)"]
    end
    
    subgraph "Database Queries"
        Q1["PRAGMA table_info(table_name)"]
        Q2["PRAGMA foreign_key_list(table_name)"]
        Q3["SELECT * FROM table LIMIT 2/3"]
    end
    
    OpA --> API1
    OpB --> API1
    OpC --> API2
    
    API1 --> PRIV
    API2 --> PRIV
    
    PRIV --> CG
    CG -->|Hit| PRIV
    CG -->|Miss| CONN
    
    CONN --> GTI
    GTI --> Q1
    GTI --> Q2
    GTI --> Q3
    
    CONN --> CS
    CS --> CL
```
Sources: [dataflow/utils/text2sql/database_manager.py:19-80, 315-355](), [dataflow/utils/text2sql/database_connector/sqlite_connector.py:93-187]()

**Cache Behavior:**

| Component | Class | TTL | Max Size |
|-----------|-------|-----|----------|
| `CacheManager` | `CacheManager` [dataflow/utils/text2sql/database_manager.py:19-27]() | 1800s | 100 entries |

Sources: [dataflow/utils/text2sql/database_manager.py:19-81]()

---

## Usage in Pipelines

The `Text2VecSQLGeneration_APIPipeline` demonstrates connector configuration within end-to-end vector SQL generation pipelines [dataflow/statics/pipelines/api_pipelines/text2vecsql_pipeline_gen.py:61-127]():

```python
database_manager = DatabaseManager(
    db_type="sqlite-vec",
    config={
        "root_path": self.db_root_path,
        "model_name": "all-MiniLM-L6-v2",
        "model_path": "./hf_cache/all-MiniLM-L6-v2.e4ce9877.q8_0.gguf",
        "enable_lembed": False
    },
    embedding_serving=embedding_serving
)
```

**Configuration Parameter Mapping:**

| Parameter | Purpose | Used By |
|-----------|---------|---------|
| `root_path` | Directory to search for database files | `DatabaseManager._discover_databases()` [dataflow/utils/text2sql/database_manager.py:125-127]() |
| `model_name` | Identifier for embedding model | `SQLiteVecConnector.connect()` [dataflow/utils/text2sql/database_connector/sqlite_vec_connector.py:84, 105-112]() |
| `enable_lembed` | Toggle in-database embedding via `lembed()` | `SQLiteVecConnector.connect()` [dataflow/utils/text2sql/database_connector/sqlite_vec_connector.py:86, 98-101]() |

Sources: [dataflow/statics/pipelines/api_pipelines/text2vecsql_pipeline_gen.py:118-127](), [dataflow/utils/text2sql/database_connector/sqlite_vec_connector.py:48-163](), [dataflow/utils/text2sql/database_manager.py:100-127]()

---

