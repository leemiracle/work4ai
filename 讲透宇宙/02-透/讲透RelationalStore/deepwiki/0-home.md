> 来源: [https://deepwiki.com/openharmony/distributeddatamgr_relational_store](https://deepwiki.com/openharmony/distributeddatamgr_relational_store)
> DeepWiki openharmony/distributeddatamgr_relational_store 主页

# Overview

  Relevant source files 
 - [bundle.json](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/bundle.json)
 - [frameworks/js/napi/dataability/BUILD.gn](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/dataability/BUILD.gn)
 - [frameworks/js/napi/rdb/BUILD.gn](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/BUILD.gn)
 - [frameworks/js/napi/relationalstore/BUILD.gn](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/BUILD.gn)
 - [frameworks/js/napi/relationalstore/include/napi_rdb_store.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/include/napi_rdb_store.h)
 - [frameworks/js/napi/relationalstore/mock/include/napi_rdb_store.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/mock/include/napi_rdb_store.h)
 - [frameworks/js/napi/relationalstore/src/napi_rdb_store.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/src/napi_rdb_store.cpp)
 - [frameworks/native/rdb/include/rdb_store_impl.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/rdb_store_impl.h)
 - [frameworks/native/rdb/mock/include/rdb_store_impl.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/mock/include/rdb_store_impl.h)
 - [frameworks/native/rdb/src/rdb_store_impl.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp)
 - [interfaces/inner_api/appdatafwk/BUILD.gn](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/appdatafwk/BUILD.gn)
 - [interfaces/inner_api/dataability/BUILD.gn](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/dataability/BUILD.gn)
 - [interfaces/inner_api/rdb/BUILD.gn](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/BUILD.gn)
 - [interfaces/inner_api/rdb/include/rdb_store.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/rdb_store.h)
 - [interfaces/inner_api/rdb_data_ability_adapter/BUILD.gn](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb_data_ability_adapter/BUILD.gn)
 - [interfaces/inner_api/rdb_data_share_adapter/BUILD.gn](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb_data_share_adapter/BUILD.gn)
 
  The OpenHarmony Distributed Relational Database Management System (RDBMS) provides a comprehensive framework for applications to store, query, and manage structured data. Built on SQLite, it offers both local database operations and distributed capabilities that enable data synchronization across devices. This system serves as the foundation for persistent data storage in OpenHarmony applications.

 For information about specific components, see the related wiki pages:

 
 - For RDB Store implementation details, see [RDB Store Core](https://deepwiki.com/openharmony/distributeddatamgr_relational_store/2-rdb-store-core)
 - For JavaScript API usage, see [JavaScript API](https://deepwiki.com/openharmony/distributeddatamgr_relational_store/6-javascript-api)
 - For distributed features, see [Distributed Database](https://deepwiki.com/openharmony/distributeddatamgr_relational_store/7-distributed-database)
 
 
## System Architecture

 The RDBMS is organized in a layered architecture that provides different API levels for application developers while maintaining a consistent core implementation.

 
```

```

 Sources:

 
 - [frameworks/native/rdb/include/rdb_store_impl.h88-283](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/rdb_store_impl.h#L88-L283)
 - [interfaces/inner_api/rdb/include/rdb_store.h38-135](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/rdb_store.h#L38-L135)
 
 
## Data Flow: Query Execution

 The following sequence diagram illustrates the flow of a typical database query operation through the system components:

 
```

```

 Sources:

 
 - [frameworks/native/rdb/src/rdb_store_impl.cpp183-202](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L183-L202)
 - [frameworks/native/rdb/src/rdb_store_impl.cpp344-370](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L344-L370)
 
 
## Core Components

 
### RdbStore and RdbStoreImpl

 `RdbStore` is the main interface for database operations, while `RdbStoreImpl` is its concrete implementation. It provides methods for:

 
 - CRUD operations (Create, Read, Update, Delete)
 - Transaction management
 - SQL execution
 - Distributed database operations
 - Security management
 
 `RdbStoreImpl` manages connections through the connection pool and interfaces with other components such as the security manager for encryption and the distributed services for synchronization.

 
```

```

 Sources:

 
 - [frameworks/native/rdb/include/rdb_store_impl.h88-283](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/rdb_store_impl.h#L88-L283)
 - [frameworks/native/rdb/src/rdb_store_impl.cpp89-121](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L89-L121)
 
 
### Key Components and Their Roles

 
| Component | Description | Key Interfaces |
|---|---|---|
| RdbStore | Main interface for database operations | Insert, Update, Delete, Query, ExecuteSql, BeginTransaction |
| RdbStoreImpl | Implementation of RdbStore | Manages connections, handles transactions, implements distributed operations |
| ConnectionPool | Manages database connections | AcquireConnection, ReleaseConnection |
| SqliteConnection | Handles communication with SQLite | ExecuteSql, Prepare, CreateStatement |
| RdbPredicates | Builds query conditions | EqualTo, NotEqualTo, BeginsWith, OrderByAsc, Limit |
| ResultSet | Provides access to query results | GoToFirstRow, GoToNextRow, GetString, GetLong |
| Transaction | Manages database transactions | Begin, Commit, Rollback |
| RdbSecurityManager | Handles database encryption | SetCipher, EnableEncryption |

 Sources:

 
 - [interfaces/inner_api/rdb/include/rdb_store.h147-1000](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/rdb_store.h#L147-L1000)
 - [interfaces/inner_api/rdb/BUILD.gn17-54](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/BUILD.gn#L17-L54)
 
 
## JavaScript APIs

 OpenHarmony RDBMS provides JavaScript APIs for application developers through the `@ohos.data.relationalStore` module. These APIs are implemented using NAPI (Node.js API) to bridge JavaScript and the native implementations.

 The JavaScript layer consists of:

 
 - `RdbStore`: Main class for database operations
 - `ResultSet`: For accessing query results
 - `RdbPredicates`: For building query conditions
 - Helper functions for creating and opening databases
 
 The NAPI layer (`RdbStoreProxy`, `NapiResultSet`, etc.) bridges these JavaScript objects to their native counterparts.

 Sources:

 
 - [frameworks/js/napi/relationalstore/src/napi_rdb_store.cpp61-132](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/src/napi_rdb_store.cpp#L61-L132)
 - [frameworks/js/napi/relationalstore/include/napi_rdb_store.h38-155](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/include/napi_rdb_store.h#L38-L155)
 - [frameworks/js/napi/relationalstore/BUILD.gn44-63](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/BUILD.gn#L44-L63)
 
 
## Distributed Features

 The RDBMS system supports distributed database operations, enabling data synchronization across devices:

 
```

```

 Key distributed features include:

 
 - **Distributed Tables**: Tables can be designated for synchronization across devices using `SetDistributedTables()`
 - **Remote Query**: Query data from databases on other devices using `RemoteQuery()`
 - **Synchronization**: Synchronize data between devices using `Sync()` with various modes and options
 - **Subscription**: Subscribe to data changes using `Subscribe()` to receive notifications when data changes
 
 Sources:

 
 - [frameworks/native/rdb/src/rdb_store_impl.cpp336-358](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L336-L358)
 - [frameworks/native/rdb/src/rdb_store_impl.cpp456-508](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L456-L508)
 - [frameworks/native/rdb/src/rdb_store_impl.cpp376-437](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L376-L437)
 
 
## Security Features

 The RDBMS provides several security features:

 
 - **Encryption**: Database files can be encrypted using the `RdbSecurityManager`
 - **Security Levels**: Different security levels can be configured when creating a database
 - **Access Control**: Control mechanisms ensure only authorized applications can access databases
 - **Secure Connections**: Secure connections are used for distributed operations
 
 Sources:

 
 - [frameworks/native/rdb/src/rdb_store_impl.cpp97-113](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L97-L113)
 - [frameworks/native/rdb/include/rdb_store_impl.h241-283](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/rdb_store_impl.h#L241-L283)
 
 
## Build System and Dependencies

 The RDBMS is built using GN (Generate Ninja) build system and has the following key dependencies:

 
 - **SQLite**: Underlying database engine
 - **HUKS**: Huawei Universal Key Service for encryption
 - **IPC**: For inter-process communication in distributed scenarios
 - **HiLog**: For logging
 - **HiTrace**: For performance tracing
 
 The system is structured as several shared libraries and modules:

 
 - `native_rdb`: Core native implementation
 - `relationalstore`: JavaScript API module
 - `rdb_data_share_adapter`: Integration with data sharing
 
 Sources:

 
 - [interfaces/inner_api/rdb/BUILD.gn106-176](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/BUILD.gn#L106-L176)
 - [frameworks/js/napi/relationalstore/BUILD.gn44-63](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/BUILD.gn#L44-L63)
 - [bundle.json29-71](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/bundle.json#L29-L71)
 
 
## Conclusion

 The OpenHarmony Distributed Relational Database Management System provides a robust framework for applications to store and manage structured data. With its layered architecture, it offers both ease of use through high-level JavaScript APIs and performance through native C++ implementations. The distributed capabilities enable seamless data synchronization across devices, while security features ensure data protection.

 For more detailed information on specific components and usage, please refer to the linked wiki pages.
