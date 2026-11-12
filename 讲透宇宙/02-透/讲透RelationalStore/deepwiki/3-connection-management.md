> 来源: [https://deepwiki.com/openharmony/distributeddatamgr_relational_store/3-connection-management](https://deepwiki.com/openharmony/distributeddatamgr_relational_store/3-connection-management)
> DeepWiki openharmony/distributeddatamgr_relational_store

# Connection Management

  Relevant source files 
 - [frameworks/native/rdb/include/connection.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/connection.h)
 - [frameworks/native/rdb/include/connection_pool.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/connection_pool.h)
 - [frameworks/native/rdb/include/rd_connection.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/rd_connection.h)
 - [frameworks/native/rdb/include/sqlite_connection.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/sqlite_connection.h)
 - [frameworks/native/rdb/include/sqlite_statement.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/sqlite_statement.h)
 - [frameworks/native/rdb/src/connection.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/connection.cpp)
 - [frameworks/native/rdb/src/connection_pool.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/connection_pool.cpp)
 - [frameworks/native/rdb/src/rd_connection.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rd_connection.cpp)
 - [frameworks/native/rdb/src/rdb_store_config.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_config.cpp)
 - [frameworks/native/rdb/src/sqlite_connection.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/sqlite_connection.cpp)
 - [frameworks/native/rdb/src/sqlite_statement.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/sqlite_statement.cpp)
 - [interfaces/inner_api/rdb/include/rdb_store_config.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/rdb_store_config.h)
 - [interfaces/inner_api/rdb/mock/include/rdb_store_config.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/mock/include/rdb_store_config.h)
 - [test/native/rdb/unittest/rdb_double_write_test.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/native/rdb/unittest/rdb_double_write_test.cpp)
 - [test/native/rdb/unittest/rdb_execute_rd_test.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/native/rdb/unittest/rdb_execute_rd_test.cpp)
 
  This document explains how database connections are managed in the OpenHarmony Distributed Relational Database Management System (RDBMS). It covers the creation, configuration, pooling, and lifecycle of database connections, as well as specialized features like high availability and transaction management. For information about SQL execution and statement handling, see [SQL Query Building](https://deepwiki.com/openharmony/distributeddatamgr_relational_store/2.4-sql-query-building).

 
## Overview of Connection Management

 The connection management subsystem is responsible for:

 
 - Creating and configuring database connections to different backend types (SQLite and vector databases)
 - Pooling connections to optimize resource usage and performance
 - Managing different connection types (read vs. write connections)
 - Supporting high availability features through dual-write and replication
 - Handling database encryption and security
 
 The system uses an abstraction layer that allows for different database backend implementations while maintaining a consistent interface.

 
```

```

 Sources: [frameworks/native/rdb/include/connection.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/connection.h) [frameworks/native/rdb/src/connection.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/connection.cpp) [frameworks/native/rdb/include/sqlite_connection.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/sqlite_connection.h) [frameworks/native/rdb/include/rd_connection.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/rd_connection.h)

 
## Connection Types

 The system supports two types of database backends, each with a specialized connection implementation:

 
### SQLite Connection

 `SqliteConnection` is the primary connection implementation, handling SQLite databases. It manages:

 
 - SQLite database handles (`sqlite3*`)
 - Connection configuration (journal mode, encryption, etc.)
 - Statement creation and execution
 - Transaction management
 - High availability through slave connections
 
 
### Vector Database Connection

 `RdConnection` is a specialized connection implementation for vector databases. It supports:

 
 - Vector database operations
 - Configuration specific to vector databases
 - Different API calls for vector database operations
 - Encryption and backup capabilities
 
 Both connection types implement the common `Connection` interface, allowing the rest of the system to interact with either database type in a consistent manner.

 Sources: [frameworks/native/rdb/src/sqlite_connection.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/sqlite_connection.cpp) [frameworks/native/rdb/src/rd_connection.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rd_connection.cpp)

 
## Connection Pool

 The `ConnectionPool` manages database connections to optimize resource usage and performance. It maintains separate pools for different connection types:

 
```

```

 The connection pool maintains:

 
 - **Writers container**: For write connections (usually limited to 1)
 - **Readers container**: For read-only connections (configurable number)
 - **Trans container**: For transaction-specific connections
 
 Each container manages its own set of `ConnNode` objects, which wrap the actual database connections and track usage state.

 Sources: [frameworks/native/rdb/include/connection_pool.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/connection_pool.h) [frameworks/native/rdb/src/connection_pool.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/connection_pool.cpp)

 
## Connection Lifecycle

 Connections go through a standard lifecycle managed by the connection pool:

 
```

```

 The connection lifecycle key points:

 
 - Connections are acquired from the pool with a read/write flag
 - The pool either provides an existing available connection or creates a new one
 - When released, connections are returned to the pool for reuse
 - Connections are configured according to the RdbStoreConfig parameters
 - Connections are automatically closed when the pool is destroyed
 
 Sources: [frameworks/native/rdb/src/connection_pool.cpp246-250](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/connection_pool.cpp#L246-L250) [frameworks/native/rdb/src/sqlite_connection.cpp79-85](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/sqlite_connection.cpp#L79-L85) [frameworks/native/rdb/src/sqlite_connection.cpp186-198](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/sqlite_connection.cpp#L186-L198)

 
## Connection Configuration

 Connections are configured based on parameters from `RdbStoreConfig`, which controls numerous aspects of connection behavior:

 
| Setting | Description | Related Methods |
|---|---|---|
| Journal Mode | Controls how changes are logged (WAL, DELETE, etc.) | SetJournalMode() |
| Encryption | Configures database encryption | SetEncrypt(), SetEncryptKey() |
| Page Size | Sets the database page size | SetPageSize() |
| Sync Mode | Controls durability vs. performance | SetWalSyncMode() |
| Custom Functions | Adds user-defined SQL functions | SetCustomFunctions() |
| Locale | Sets collation locale | ConfigLocale() |
| Security Level | Sets security level (S1-S4) | Via RdbStoreConfig |
| High Availability | Controls dual-write and replication | Via HAMode setting |

 The configuration process is primarily handled in the `Configure` method for `SqliteConnection`, which applies these settings to the database connection.

 Sources: [frameworks/native/rdb/src/sqlite_connection.cpp373-432](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/sqlite_connection.cpp#L373-L432) [interfaces/inner_api/rdb/include/rdb_store_config.h267-284](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/rdb_store_config.h#L267-L284)

 
## High Availability Features

 The connection management system includes high availability features through two main mechanisms:

 
### Dual-Write Mode

 When the `HAMode` configuration is set to `MAIN_REPLICA` or `MANUAL_TRIGGER`, the system can maintain a slave database that mirrors the main database. This provides redundancy in case of database corruption.

 
```

```

 In dual-write mode, SQL operations executed on the master connection are mirrored to the slave database, ensuring that both databases remain in sync. This is particularly important for ensuring data availability and integrity.

 Sources: [frameworks/native/rdb/src/sqlite_connection.cpp143-194](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/sqlite_connection.cpp#L143-L194) [frameworks/native/rdb/src/sqlite_connection.cpp509-524](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/sqlite_connection.cpp#L509-L524)

 
### Backup and Recovery

 Connections support backup and restore operations for disaster recovery:

 
 - **Backup**: Creates a copy of the database using `Backup()` method
 - **Restore**: Restores the database from a backup using `Restore()` method
 - **Repair**: Attempts to repair a corrupted database using `Repair()` static method
 
 These operations are implemented in both `SqliteConnection` and `RdConnection` for their respective database types.

 Sources: [frameworks/native/rdb/src/sqlite_connection.cpp63-74](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/sqlite_connection.cpp#L63-L74) [frameworks/native/rdb/src/rd_connection.cpp63-101](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rd_connection.cpp#L63-L101)

 
## Transaction Management

 Transaction management is a specialized aspect of connection management. The `ConnectionPool` provides dedicated transaction connections through its `CreateTransConn()` method:

 
```

```

 Key aspects of transaction management:

 
 - Transaction connections are maintained in a separate pool
 - The system limits the number of concurrent transactions
 - Transactions can be committed or rolled back
 - Transaction connections are returned to the pool after use
 
 Sources: [frameworks/native/rdb/src/connection_pool.cpp232-244](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/connection_pool.cpp#L232-L244) [frameworks/native/rdb/src/connection_pool.cpp368-388](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/connection_pool.cpp#L368-L388)

 
## Security Features

 Connection management includes several security features:

 
### Encryption

 Database connections can be configured to use encryption through the `SetEncrypt()` method:

 
 - Supports multiple encryption algorithms (AES-256-GCM, AES-256-CBC)
 - Handles key management for secure key storage
 - Supports key rotation via `ReSetKey()`
 
 The encryption process is primarily implemented in the `SetEncrypt()` and `SetEncryptKey()` methods in `SqliteConnection`.

 
### Access Control

 Connections enforce access control based on configuration:

 
 - Read-only connections for restricted access
 - Write connections for full access
 - Role-based access control (OWNER, VISITOR, VISITOR_WRITE)
 
 Sources: [frameworks/native/rdb/src/sqlite_connection.cpp706-753](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/sqlite_connection.cpp#L706-L753) [frameworks/native/rdb/src/sqlite_connection.cpp654-672](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/sqlite_connection.cpp#L654-L672)

 
## Connection Management Implementation Details

 
### Connection Factory Pattern

 The system uses a factory pattern to create the appropriate connection type based on the database type configured in `RdbStoreConfig`:

 
```

```

 This pattern allows the system to support multiple database backends while providing a consistent interface.

 Sources: [frameworks/native/rdb/src/connection.cpp25-38](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/connection.cpp#L25-L38) [frameworks/native/rdb/src/sqlite_connection.cpp79-85](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/sqlite_connection.cpp#L79-L85) [frameworks/native/rdb/src/rd_connection.cpp40-61](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rd_connection.cpp#L40-L61)

 
### Connection Pooling Implementation

 The `ConnectionPool` uses a `Container` inner class to manage sets of connections. Each container:

 
 - Maintains a list of `ConnNode` objects that wrap connections
 - Handles connection acquisition and release
 - Manages connection recycling
 - Implements thread-safe connection management
 
 The pool implements connection acquisition with timeout support, allowing applications to wait for a connection to become available if all connections are in use.

 Sources: [frameworks/native/rdb/include/connection_pool.h83-121](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/connection_pool.h#L83-L121) [frameworks/native/rdb/src/connection_pool.cpp304-336](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/connection_pool.cpp#L304-L336)

 
## Best Practices for Connection Management

 
 - **Use the connection pool**: Always acquire connections through the connection pool rather than creating them directly
 - **Release connections promptly**: Return connections to the pool as soon as operations are complete
 - **Use read connections for read-only operations**: This allows better concurrency
 - **Configure appropriate limits**: Set connection pool sizes based on workload
 - **Use transactions for multi-step operations**: Helps ensure data consistency
 - **Configure high availability appropriately**: Use dual-write for critical data
 
 
## Conclusion

 Connection management in the OpenHarmony Distributed Relational Database Management System provides a robust and flexible way to interact with different types of databases. It offers features for performance optimization through connection pooling, high availability through dual-write and backup/restore capabilities, and security through encryption and access control.

 The system's architecture, with its abstract `Connection` interface and specialized implementations for different database types, allows for extensibility while maintaining a consistent programming model for applications.

 Sources: [frameworks/native/rdb/include/connection.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/connection.h) [frameworks/native/rdb/include/connection_pool.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/connection_pool.h) [frameworks/native/rdb/src/sqlite_connection.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/sqlite_connection.cpp) [frameworks/native/rdb/src/rd_connection.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rd_connection.cpp)
