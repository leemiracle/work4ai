> 来源: [https://deepwiki.com/openharmony/distributeddatamgr_relational_store/2-rdb-store-core](https://deepwiki.com/openharmony/distributeddatamgr_relational_store/2-rdb-store-core)
> DeepWiki openharmony/distributeddatamgr_relational_store

# RDB Store Core

  Relevant source files 
 - [frameworks/js/napi/relationalstore/include/napi_rdb_store.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/include/napi_rdb_store.h)
 - [frameworks/js/napi/relationalstore/mock/include/napi_rdb_store.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/mock/include/napi_rdb_store.h)
 - [frameworks/js/napi/relationalstore/src/napi_rdb_store.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/src/napi_rdb_store.cpp)
 - [frameworks/native/rdb/include/rdb_store_impl.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/rdb_store_impl.h)
 - [frameworks/native/rdb/mock/include/rdb_store_impl.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/mock/include/rdb_store_impl.h)
 - [frameworks/native/rdb/src/rdb_store_impl.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp)
 - [interfaces/inner_api/rdb/include/rdb_store.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/rdb_store.h)
 
  The RDB Store Core is the central implementation of the relational database management functionality in the OpenHarmony distributed data management system. It provides core database capabilities including CRUD operations, transaction management, connection handling, SQL execution, and distributed data synchronization. This page describes the architecture and key components of the RDB Store Core subsystem, which serves as the foundation for both native C++ and JavaScript relational database access.

 For JavaScript API details, see [JavaScript API](https://deepwiki.com/openharmony/distributeddatamgr_relational_store/6-javascript-api). For connection management specifics, see [Connection Management](https://deepwiki.com/openharmony/distributeddatamgr_relational_store/3-connection-management).

 
## Core Architecture

 The RDB Store Core is built around the `RdbStore` interface and its implementation `RdbStoreImpl`, which orchestrates database operations while managing connections, transactions, security, and distributed features.

 
```

```

 Sources: [frameworks/native/rdb/include/rdb_store_impl.h88-283](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/rdb_store_impl.h#L88-L283) [interfaces/inner_api/rdb/include/rdb_store.h38-708](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/rdb_store.h#L38-L708) [frameworks/js/napi/relationalstore/include/napi_rdb_store.h38-155](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/include/napi_rdb_store.h#L38-L155)

 
## Key Components and Relationships

 The RDB Store Core operates through a set of interconnected components that handle different aspects of database operations. The following diagram shows the relationships between these components:

 
```

```

 Sources: [frameworks/native/rdb/include/rdb_store_impl.h88-283](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/rdb_store_impl.h#L88-L283) [frameworks/native/rdb/src/rdb_store_impl.cpp83-5300](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L83-L5300)

 
## Core Database Operations

 The RdbStore Core provides comprehensive database operations including insertion, updates, deletion, and querying. These operations are implemented in `RdbStoreImpl` which manages the connection pool and executes SQL statements against the database.

 
### Data Flow: Query Execution

 The following sequence diagram illustrates the data flow during a query operation:

 
```

```

 Sources: [frameworks/native/rdb/src/rdb_store_impl.cpp100-200](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L100-L200)

 
### Key Operations

 The RDB Store Core provides the following key operations:

 
 - **Data Manipulation**:

 
 - Insert: Add new records to a table
 - Update: Modify existing records
 - Delete: Remove records from a table
 - Query: Retrieve data with filtering, sorting, and projection
 - **Transaction Management**:

 
 - Begin Transaction: Start a new transaction
 - Commit: Persist changes made during a transaction
 - Rollback: Undo changes made during a transaction
 - **Database Management**:

 
 - Backup: Create a backup of the database
 - Restore: Restore a database from a backup
 - Attach/Detach: Connect/disconnect additional database files
 - Version Control: Get and set database version
 
 
## Connection Management

 RDB Store Core implements a connection pooling mechanism to efficiently manage database connections, improving performance and resource utilization.

 
```

```

 Key methods for connection management:

 
 - `GetConn(bool isRead)`: Acquires a connection from the pool based on the operation type (read/write)
 - `GetPool()`: Retrieves the connection pool
 - `Close()`: Closes all connections in the pool
 
 Sources: [frameworks/native/rdb/src/rdb_store_impl.cpp184-202](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L184-L202) [frameworks/native/rdb/include/rdb_store_impl.h238-239](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/rdb_store_impl.h#L238-L239)

 
## Transaction Management

 The RDB Store Core provides robust transaction support to ensure data integrity and atomicity of operations.

 
```

```

 Transaction methods:

 
 - `BeginTransaction()`: Starts a transaction in the traditional way
 - `BeginTrans()`: Starts a transaction and returns a transaction ID for enhanced control
 - `Commit(int64_t trxId)`: Commits changes made within the specified transaction
 - `RollBack(int64_t trxId)`: Reverts changes made within the specified transaction
 - `IsInTransaction()`: Checks if the current connection is in a transaction
 
 The transaction system allows for multiple transactions to be managed by tracking them through a list of weak pointers to `Transaction` objects.

 Sources: [frameworks/native/rdb/include/rdb_store_impl.h119-121](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/rdb_store_impl.h#L119-L121) [frameworks/native/rdb/src/rdb_store_impl.cpp83-89](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L83-L89)

 
## Security Features

 The RDB Store Core integrates with security mechanisms to protect database content:

 
 - **Encryption Support**: Databases can be encrypted using the RdbSecurityManager
 - **Key Management**: Secure handling of encryption keys
 - **Access Control**: Read-only mode and permission checks for database operations
 
 
```

```

 Sources: [frameworks/native/rdb/src/rdb_store_impl.cpp89-113](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L89-L113)

 
## Distributed Database Features

 The RDB Store Core includes sophisticated distributed database capabilities:

 
 - **Synchronization**: Sync data between devices using the `Sync()` method
 - **Distributed Tables**: Configure tables for distributed access with `SetDistributedTables()`
 - **Remote Queries**: Query data from remote devices with `RemoteQuery()`
 - **Observation Mechanism**: Subscribe to data changes with the observer pattern
 
 
```

```

 Key distributed methods:

 
 - `Sync()`: Synchronizes data between devices based on specified options and predicates
 - `SetDistributedTables()`: Designates tables for distributed operations
 - `RemoteQuery()`: Executes queries on remote devices
 - `Subscribe()/UnSubscribe()`: Register/unregister observers for data change notifications
 - `Notify()`: Trigger notifications for data changes
 
 Sources: [frameworks/native/rdb/src/rdb_store_impl.cpp337-736](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L337-L736)

 
## JavaScript Bridge

 The RDB Store Core is exposed to JavaScript applications through a bridge layer implemented by `RdbStoreProxy`. This allows JavaScript applications to utilize the full capabilities of the RDB Store Core with a JavaScript-friendly API.

 
```

```

 The JavaScript bridge includes methods that mirror the native functionality but are adapted for JavaScript usage patterns, type conversions, and error handling.

 Sources: [frameworks/js/napi/relationalstore/include/napi_rdb_store.h38-155](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/include/napi_rdb_store.h#L38-L155) [frameworks/js/napi/relationalstore/src/napi_rdb_store.cpp62-705](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/src/napi_rdb_store.cpp#L62-L705)

 
## Initialization and Configuration

 The RDB Store Core initialization process involves several steps:

 
 - Creating a configuration object (`RdbStoreConfig`)
 - Initializing the store implementation (`RdbStoreImpl`)
 - Setting up connection pools
 - Configuring security parameters
 - Registering observers if needed
 
 
```

```

 Sources: [frameworks/native/rdb/src/rdb_store_impl.cpp1007-1018](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L1007-L1018) [frameworks/native/rdb/src/rdb_store_impl.cpp89-113](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L89-L113) [frameworks/native/rdb/src/rdb_store_impl.cpp115-136](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L115-L136)

 
## Error Handling

 The RDB Store Core implements a comprehensive error handling mechanism:

 
 - Return codes for operation status
 - Error reporting through logs and Hiview system
 - Transaction rollback on errors
 - Proper resource cleanup
 
 Most methods return error codes or pairs containing both the error code and a result value, allowing callers to check for success or handle specific error conditions.

 
| Error Category | Description | Typical Error Codes |
|---|---|---|
| Connection Errors | Issues with database connections | E_ALREADY_CLOSED, E_DATABASE_BUSY |
| SQL Errors | Issues with SQL syntax or execution | SQLite error codes |
| Parameter Errors | Invalid input parameters | E_EMPTY_TABLE_NAME, E_ERROR |
| Security Errors | Issues with encryption or permissions | E_INVALID_SECRET_KEY |
| Distributed Errors | Issues with distributed operations | E_SERVICE_NOT_FOUND, E_NOT_SUPPORT |

 Sources: [frameworks/native/rdb/src/rdb_store_impl.cpp184-202](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L184-L202) [frameworks/native/rdb/src/rdb_store_impl.cpp1022-1047](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L1022-L1047)

 
## Summary

 The RDB Store Core provides a robust foundation for relational database operations in the OpenHarmony system. It offers a comprehensive set of features including:

 
 - Basic CRUD operations
 - Transaction management
 - Connection pooling
 - Security features
 - Distributed database capabilities
 - JavaScript integration
 
 Its architecture follows sound design principles with clear separation of concerns, making it both powerful and maintainable. The core is designed to be flexible enough to support various usage patterns while maintaining performance and security.

 Sources: [frameworks/native/rdb/include/rdb_store_impl.h88-283](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/rdb_store_impl.h#L88-L283) [interfaces/inner_api/rdb/include/rdb_store.h38-708](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/rdb_store.h#L38-L708)
