<!-- source: DeepWiki mcp.deepwiki.com · repo vanna-ai/vanna · page 6 Database Connectors (SqlRunner) · fetched 2026-10-29 -->

# Database Connectors (SqlRunner)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/vanna/core/agent/config.py](src/vanna/core/agent/config.py)
- [src/vanna/integrations/__init__.py](src/vanna/integrations/__init__.py)
- [src/vanna/integrations/azureopenai/__init__.py](src/vanna/integrations/azureopenai/__init__.py)
- [src/vanna/integrations/azureopenai/llm.py](src/vanna/integrations/azureopenai/llm.py)
- [src/vanna/tools/run_sql.py](src/vanna/tools/run_sql.py)
- [tests/conftest.py](tests/conftest.py)
- [tests/test_agent_memory_sanity.py](tests/test_agent_memory_sanity.py)
- [tests/test_agents.py](tests/test_agents.py)
- [tests/test_azureopenai_llm.py](tests/test_azureopenai_llm.py)
- [tests/test_legacy_adapter.py](tests/test_legacy_adapter.py)
- [tox.ini](tox.ini)

</details>



This document describes the `SqlRunner` interface and its implementations, which provide database connectivity for SQL execution in Vanna agents. `SqlRunner` implementations enable the `RunSqlTool` to query databases and return results as pandas DataFrames.

For information about how `RunSqlTool` integrates `SqlRunner` into the agent workflow, see [Tool System](#6). For details on specific database implementations, see child pages [PostgreSQL](#7.1), [SQLite](#7.2), [Cloud Data Warehouses](#7.3), and [Other SQL Databases](#7.4).

## SqlRunner in the Tool Execution Flow

`SqlRunner` is the abstraction layer between the agent's tool execution system and database-specific connection logic. When an LLM generates a SQL query via tool calling, the following flow occurs:

```mermaid
sequenceDiagram
    participant Agent
    participant RunSqlTool
    participant SqlRunner as "SqlRunner Implementation<br/>(e.g., PostgresRunner)"
    participant Database as "SQL Database"
    
    Agent->>RunSqlTool: execute(tool_call, ToolContext)
    Note over RunSqlTool: Extract SQL from tool_call.arguments
    RunSqlTool->>RunSqlTool: Create RunSqlToolArgs(sql=...)
    RunSqlTool->>SqlRunner: run_sql(args, context)
    SqlRunner->>Database: Connect using connection params
    SqlRunner->>Database: Execute SQL query
    Database-->>SqlRunner: Query results
    SqlRunner->>SqlRunner: Convert results to DataFrame
    SqlRunner-->>RunSqlTool: pd.DataFrame
    RunSqlTool->>RunSqlTool: Format as ToolResult<br/>(table UI + text summary)
    RunSqlTool-->>Agent: ToolResult
    Agent-->>Agent: Stream UI component to user
```

**Sources:** [tests/test_agents.py:38-39](), [src/vanna/integrations/postgres/sql_runner.py:65-112]()

## SqlRunner Interface

The `SqlRunner` interface defines a single abstract method for executing SQL queries:

| Method | Signature | Description |
|--------|-----------|-------------|
| `run_sql` | `async def run_sql(args: RunSqlToolArgs, context: ToolContext) -> pd.DataFrame` | Execute SQL and return results as DataFrame |

### Method Parameters

- **`args: RunSqlToolArgs`**: Contains the SQL query string and optional execution parameters
- **`context: ToolContext`**: Provides access to user identity, agent memory, observability, and metadata

### Return Value

All `SqlRunner` implementations must return a `pd.DataFrame`:
- For `SELECT` queries: DataFrame contains query results with column names
- For `INSERT`/`UPDATE`/`DELETE`: DataFrame contains a `rows_affected` column
- For empty results: Returns empty DataFrame (`pd.DataFrame()`)

**Sources:** [src/vanna/integrations/postgres/sql_runner.py:65-74](), [src/vanna/integrations/postgres/sql_runner.py:93-108]()

## SqlRunner Implementation Structure

Each database connector follows a consistent implementation pattern:

```mermaid
classDiagram
    class SqlRunner {
        <<interface>>
        +run_sql(args, context) pd.DataFrame*
    }
    
    class PostgresRunner {
        -psycopg2
        -connection_string: Optional[str]
        -connection_params: Optional[dict]
        +__init__(connection_string, host, port, ...)
        +run_sql(args, context) pd.DataFrame
    }
    
    class SqliteRunner {
        -database_path: str
        +__init__(database_path)
        +run_sql(args, context) pd.DataFrame
    }
    
    class SnowflakeRunner {
        -account: str
        -warehouse: str
        -database: str
        +__init__(account, warehouse, ...)
        +run_sql(args, context) pd.DataFrame
    }
    
    class BigQueryRunner {
        -project_id: str
        -credentials
        +__init__(project_id, credentials, ...)
        +run_sql(args, context) pd.DataFrame
    }
    
    SqlRunner <|-- PostgresRunner
    SqlRunner <|-- SqliteRunner
    SqlRunner <|-- SnowflakeRunner
    SqlRunner <|-- BigQueryRunner
    
    note for PostgresRunner "Import path:\nvanna.integrations.postgres"
    note for SqliteRunner "Import path:\nvanna.integrations.sqlite"
    note for SnowflakeRunner "Import path:\nvanna.integrations.snowflake"
    note for BigQueryRunner "Import path:\nvanna.integrations.bigquery"
```

**Sources:** [tox.ini:124-231](), [src/vanna/integrations/postgres/sql_runner.py:10-113]()

## Connection Management Patterns

`SqlRunner` implementations handle database-specific connection management in their constructors:

### Constructor Patterns

**Option 1: Connection String**
```python
PostgresRunner(
    connection_string="postgresql://user:password@host:port/database"
)
```

**Option 2: Individual Parameters**
```python
PostgresRunner(
    host="localhost",
    port=5432,
    database="mydb",
    user="myuser",
    password="mypass"
)
```

### Connection Lifecycle

Each `SqlRunner` implementation manages connections according to its database client's best practices:

| Pattern | Databases | Behavior |
|---------|-----------|----------|
| **Per-Query Connections** | PostgreSQL, MySQL | New connection for each `run_sql` call, closed after query completion |
| **File-Based** | SQLite, DuckDB | Opens file on each query, no persistent connection |
| **Session-Based** | Snowflake, BigQuery | Long-lived session created in constructor, reused across queries |

**Sources:** [src/vanna/integrations/postgres/sql_runner.py:13-63](), [src/vanna/integrations/postgres/sql_runner.py:78-112]()

## Query Execution and Result Handling

The `run_sql` method implementation follows this pattern:

```mermaid
flowchart TD
    Start["run_sql(args, context)"] --> Connect["Establish database connection"]
    Connect --> Extract["Extract SQL from args.sql"]
    Extract --> Execute["Execute query"]
    Execute --> CheckType{"Query type?"}
    
    CheckType -->|SELECT| Fetch["Fetch all rows"]
    CheckType -->|INSERT/UPDATE/DELETE| Commit["Commit transaction<br/>Get rows affected"]
    
    Fetch --> ToDict["Convert rows to list[dict]"]
    ToDict --> DataFrame1["pd.DataFrame(results_data)"]
    
    Commit --> DataFrame2["pd.DataFrame({'rows_affected': [count]})"]
    
    DataFrame1 --> Close["Close connection"]
    DataFrame2 --> Close
    
    Close --> Return["Return DataFrame"]
    
    style Start fill:#f9f9f9
    style Return fill:#f9f9f9
```

**Sources:** [src/vanna/integrations/postgres/sql_runner.py:86-112]()

## Available SqlRunner Implementations

Vanna provides `SqlRunner` implementations for 11 database systems:

| Category | Database | Class Name | Import Path | Install Extra |
|----------|----------|------------|-------------|---------------|
| **Traditional RDBMS** | PostgreSQL | `PostgresRunner` | `vanna.integrations.postgres` | `postgres` |
| | MySQL | `MySQLRunner` | `vanna.integrations.mysql` | `mysql` |
| | Oracle | `OracleRunner` | `vanna.integrations.oracle` | `oracle` |
| | MS SQL Server | `MSSQLRunner` | `vanna.integrations.mssql` | `mssql` |
| **Embedded/Local** | SQLite | `SqliteRunner` | `vanna.integrations.sqlite` | _(none)_ |
| | DuckDB | `DuckDBRunner` | `vanna.integrations.duckdb` | `duckdb` |
| **Cloud Data Warehouses** | Snowflake | `SnowflakeRunner` | `vanna.integrations.snowflake` | `snowflake` |
| | BigQuery | `BigQueryRunner` | `vanna.integrations.bigquery` | `bigquery` |
| **OLAP/Analytics** | ClickHouse | `ClickHouseRunner` | `vanna.integrations.clickhouse` | `clickhouse` |
| | Presto | `PrestoRunner` | `vanna.integrations.presto` | `presto` |
| | Hive | `HiveRunner` | `vanna.integrations.hive` | `hive` |

### Installation

Install database-specific dependencies using pip extras:

```bash
# Single database
pip install 'vanna[postgres]'

# Multiple databases
pip install 'vanna[postgres,snowflake,bigquery]'
```

SQLite requires no extra dependencies as it is included in Python's standard library.

**Sources:** [tox.ini:124-231]()

## Integration with RunSqlTool

`SqlRunner` instances are passed to `RunSqlTool` during agent configuration:

```mermaid
graph LR
    subgraph "Agent Configuration"
        SqlRunner["SqlRunner instance<br/>(e.g., PostgresRunner)"]
        FileSystem["FileSystem instance<br/>(e.g., LocalFileSystem)"]
        
        SqlRunner --> RunSqlTool["RunSqlTool(sql_runner, file_system)"]
        FileSystem --> RunSqlTool
    end
    
    subgraph "Tool Registry"
        RunSqlTool --> Register["tools.register_local_tool(RunSqlTool, access_groups)"]
    end
    
    subgraph "Agent Initialization"
        Register --> Agent["Agent(tool_registry=tools, ...)"]
    end
    
    Agent --> Execution["Agent executes SQL queries<br/>via RunSqlTool"]
```

**Example from test suite:**

```python
# Create SqlRunner for database
sql_runner = SqliteRunner(database_path="Chinook.sqlite")

# Create RunSqlTool with SqlRunner
db_tool = RunSqlTool(
    sql_runner=sql_runner,
    file_system=LocalFileSystem()
)

# Register tool with access control
tools = ToolRegistry()
tools.register_local_tool(db_tool, access_groups=["user"])

# Create agent
agent = Agent(
    llm_service=llm,
    tool_registry=tools,
    ...
)
```

**Sources:** [tests/test_agents.py:37-39](), [tests/conftest.py:57-76]()

## Implementing a Custom SqlRunner

To support a new database, implement the `SqlRunner` interface:

### Implementation Checklist

1. **Import database client library** in `__init__` with appropriate error handling
2. **Store connection parameters** as instance attributes
3. **Implement `run_sql` method** with this structure:
   - Establish database connection
   - Execute `args.sql`
   - Differentiate SELECT vs modification queries
   - Convert results to `pd.DataFrame`
   - Close connection
   - Return DataFrame

### Template Structure

```python
from vanna.capabilities.sql_runner import SqlRunner, RunSqlToolArgs
from vanna.core.tool import ToolContext
import pandas as pd

class CustomRunner(SqlRunner):
    def __init__(self, connection_param1, connection_param2, **kwargs):
        try:
            import database_client_library
            self.client = database_client_library
        except Exception as e:
            raise ImportError(
                "database_client_library is required. "
                "Install with: pip install 'vanna[custom]'"
            ) from e
        
        self.connection_param1 = connection_param1
        self.connection_param2 = connection_param2
        # Store other parameters...
    
    async def run_sql(
        self, args: RunSqlToolArgs, context: ToolContext
    ) -> pd.DataFrame:
        # Connect to database
        conn = self.client.connect(...)
        cursor = conn.cursor()
        
        try:
            # Execute query
            cursor.execute(args.sql)
            
            # Determine query type
            query_type = args.sql.strip().upper().split()[0]
            
            if query_type == "SELECT":
                # Fetch results and convert to DataFrame
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return pd.DataFrame(rows, columns=columns)
            else:
                # Commit and return affected rows
                conn.commit()
                return pd.DataFrame({"rows_affected": [cursor.rowcount]})
        finally:
            cursor.close()
            conn.close()
```

**Sources:** [src/vanna/integrations/postgres/sql_runner.py:1-113]()

## Testing SqlRunner Implementations

The test suite includes sanity tests for all `SqlRunner` implementations:

| Test Environment | Purpose | Command |
|-----------------|---------|---------|
| `py311-postgres-sanity` | Verify PostgresRunner import and instantiation | `tox -e py311-postgres-sanity` |
| `py311-sqlite-sanity` | Verify SqliteRunner import and instantiation | `tox -e py311-sqlite-sanity` |
| `py311-snowflake-sanity` | Verify SnowflakeRunner import and instantiation | `tox -e py311-snowflake-sanity` |
| _(etc for all databases)_ | | |

These tests verify:
1. Database client library can be imported
2. `SqlRunner` class can be instantiated
3. Constructor accepts expected parameters

**Sources:** [tox.ini:124-231]()

## Error Handling

`SqlRunner` implementations should handle database-specific errors appropriately:

- **Connection errors**: Raised during `connect()` calls
- **Query syntax errors**: Raised during `execute()` calls
- **Permission errors**: Raised when user lacks database privileges
- **Timeout errors**: Raised when queries exceed database timeout settings

The `ToolContext` parameter provides access to `ObservabilityProvider` for logging errors and metrics. Implementations may use this for tracing and error reporting.

**Sources:** [src/vanna/integrations/postgres/sql_runner.py:76-77]()

---

