> 来源: [https://deepwiki.com/openharmony/distributeddatamgr_relational_store/8-native-development-kit-%28ndk%29](https://deepwiki.com/openharmony/distributeddatamgr_relational_store/8-native-development-kit-%28ndk%29)
> DeepWiki openharmony/distributeddatamgr_relational_store

# Native Development Kit (NDK)

  Relevant source files 
 - [interfaces/ndk/include/data_asset.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/include/data_asset.h)
 - [interfaces/ndk/include/oh_cursor.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/include/oh_cursor.h)
 - [interfaces/ndk/include/oh_predicates.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/include/oh_predicates.h)
 - [interfaces/ndk/include/oh_values_bucket.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/include/oh_values_bucket.h)
 - [interfaces/ndk/include/relational_store.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/include/relational_store.h)
 - [interfaces/ndk/libnative_rdb.ndk.json](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/libnative_rdb.ndk.json)
 - [interfaces/ndk/src/relational_asset.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/src/relational_asset.cpp)
 - [interfaces/ndk/src/relational_asset.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/src/relational_asset.h)
 - [interfaces/ndk/src/relational_cursor.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/src/relational_cursor.cpp)
 - [interfaces/ndk/src/relational_cursor.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/src/relational_cursor.h)
 - [interfaces/ndk/src/relational_predicates.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/src/relational_predicates.cpp)
 - [interfaces/ndk/src/relational_store.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/src/relational_store.cpp)
 - [interfaces/ndk/src/relational_store_impl.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/src/relational_store_impl.h)
 - [interfaces/ndk/src/relational_values_bucket.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/src/relational_values_bucket.cpp)
 - [test/ndk/BUILD.gn](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/ndk/BUILD.gn)
 - [test/ndk/unittest/rdb_cursor_test.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/ndk/unittest/rdb_cursor_test.cpp)
 - [test/ndk/unittest/rdb_predicates_test.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/ndk/unittest/rdb_predicates_test.cpp)
 - [test/ndk/unittest/rdb_store_test.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/ndk/unittest/rdb_store_test.cpp)
 
  The Native Development Kit (NDK) provides C-style interfaces for accessing and managing relational databases in OpenHarmony applications using native C/C++ code. It serves as a bridge between native applications and the underlying relational database system, offering a comprehensive set of APIs for operations such as creating, querying, updating, and deleting data, as well as advanced features like transactions, backups, and distributed data synchronization.

 
## Overview

 The NDK layer sits between native applications and the core relational database implementation, providing a C-based API that closely mirrors the functionality available in the JavaScript API. This allows developers to work with relational databases in native code using familiar patterns.

 
```

```

 Sources: [interfaces/ndk/src/relational_store.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/src/relational_store.cpp) [interfaces/ndk/include/relational_store.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/include/relational_store.h) [interfaces/ndk/src/relational_store_impl.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/src/relational_store_impl.h)

 
## Key Components

 The NDK provides several key components for working with relational databases:

 
### Store Management

 The database store is represented by the `OH_Rdb_Store` structure, which provides access to all database operations. Before performing any operations, you must obtain a store instance using the configuration APIs.

 
```

```

 Sources: [interfaces/ndk/src/relational_store.cpp472-508](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/src/relational_store.cpp#L472-L508) [interfaces/ndk/include/relational_store.h461-535](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/include/relational_store.h#L461-L535)

 
### Data Operations

 The NDK provides CRUD (Create, Read, Update, Delete) operations for working with data:

 
```

```

 Sources: [interfaces/ndk/src/relational_store.cpp574-673](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/src/relational_store.cpp#L574-L673) [interfaces/ndk/include/relational_store.h536-634](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/include/relational_store.h#L536-L634)

 
### Transaction Management

 The NDK provides transaction support for maintaining data consistency:

 
```

```

 Sources: [interfaces/ndk/src/relational_store.cpp695-749](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/src/relational_store.cpp#L695-L749) [interfaces/ndk/include/relational_store.h635-680](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/include/relational_store.h#L635-L680)

 
## Data Types and Structures

 
### ValuesBucket and ValueObject

 The `OH_VBucket` structure stores field-value pairs for inserting or updating data, while `OH_VObject` stores values used in predicates for queries.

 
```

```

 Sources: [interfaces/ndk/src/relational_values_bucket.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/src/relational_values_bucket.cpp) [interfaces/ndk/include/oh_values_bucket.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/include/oh_values_bucket.h)

 
### Predicates

 The `OH_Predicates` structure is used to create SQL-like conditions for queries, updates, and deletes.

 
```

```

 Sources: [interfaces/ndk/src/relational_predicates.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/src/relational_predicates.cpp) [interfaces/ndk/include/oh_predicates.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/include/oh_predicates.h) [test/ndk/unittest/rdb_predicates_test.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/ndk/unittest/rdb_predicates_test.cpp)

 
### Cursor

 The `OH_Cursor` structure provides access to query results, allowing navigation and data retrieval.

 
```

```

 Sources: [interfaces/ndk/src/relational_cursor.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/src/relational_cursor.cpp) [interfaces/ndk/include/oh_cursor.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/include/oh_cursor.h) [interfaces/ndk/src/relational_cursor.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/src/relational_cursor.h) [test/ndk/unittest/rdb_cursor_test.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/ndk/unittest/rdb_cursor_test.cpp)

 
### Asset Data Type

 The `Data_Asset` structure represents asset information within the database.

 
```

```

 Sources: [interfaces/ndk/src/relational_asset.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/src/relational_asset.cpp) [interfaces/ndk/include/data_asset.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/include/data_asset.h) [interfaces/ndk/src/relational_asset.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/src/relational_asset.h)

 
## Common Usage Patterns

 
### Creating and Configuring a Database

 To work with a database, you first need to create and configure it:

 
 - Create a configuration using `OH_Rdb_Config` or `OH_Rdb_ConfigV2`
 - Set the configuration parameters (database path, name, encryption, etc.)
 - Open the database using `OH_Rdb_GetOrOpen` or `OH_Rdb_CreateOrOpen`
 
 
```

```

 Sources: [test/ndk/unittest/rdb_store_test.cpp40-49](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/ndk/unittest/rdb_store_test.cpp#L40-L49) [test/ndk/unittest/rdb_store_test.cpp83-90](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/ndk/unittest/rdb_store_test.cpp#L83-L90)

 
### Performing CRUD Operations

 The following pattern demonstrates common CRUD operations:

 
#### Insert Data

 
```

```

 Sources: [test/ndk/unittest/rdb_store_test.cpp108-118](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/ndk/unittest/rdb_store_test.cpp#L108-L118)

 
#### Query Data

 
```

```

 Sources: [test/ndk/unittest/rdb_store_test.cpp179-195](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/ndk/unittest/rdb_store_test.cpp#L179-L195) [test/ndk/unittest/rdb_predicates_test.cpp126-147](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/ndk/unittest/rdb_predicates_test.cpp#L126-L147)

 
#### Update Data

 
```

```

 Sources: [test/ndk/unittest/rdb_store_test.cpp163-177](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/ndk/unittest/rdb_store_test.cpp#L163-L177)

 
#### Delete Data

 
```

```

 Sources: [test/ndk/unittest/rdb_store_test.cpp237-244](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/ndk/unittest/rdb_store_test.cpp#L237-L244)

 
### Transaction Management

 When performing multiple operations that need to be atomic, use transactions:

 
```

```

 Sources: [test/ndk/unittest/rdb_store_test.cpp292-304](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/ndk/unittest/rdb_store_test.cpp#L292-L304) [test/ndk/unittest/rdb_store_test.cpp323-336](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/ndk/unittest/rdb_store_test.cpp#L323-L336)

 
## Implementation Details

 The NDK provides C interfaces that internally map to the C++ implementations of the OpenHarmony Relational Database system. Key implementation classes include:

 
| NDK Interface | Implementation Class | Description |
|---|---|---|
| OH_Rdb_Store | RelationalStore | Wraps the native RdbStore implementation |
| OH_Predicates | RelationalPredicate | Wraps the native RdbPredicates implementation |
| OH_VBucket | RelationalValuesBucket | Wraps the native ValuesBucket implementation |
| OH_Cursor | RelationalCursor | Wraps the native ResultSet implementation |
| OH_VObject | RelationalPredicatesObjects | Wraps the native ValueObject implementation |
| Data_Asset | Internal struct | Wraps the native AssetValue implementation |

 The NDK layer follows the adapter pattern, converting between C and C++ interfaces and handling memory management for native applications.

 
### Object Lifecycle Management

 All allocated objects through NDK APIs need to be destroyed using the appropriate destroy methods to prevent memory leaks:

 
 - `OH_Rdb_CloseStore(store)` for store instances
 - `predicates->destroy(predicates)` for predicates
 - `bucket->destroy(bucket)` for value buckets
 - `object->destroy(object)` for value objects
 - `cursor->destroy(cursor)` for cursors
 - `OH_Data_Asset_DestroyOne(asset)` or `OH_Data_Asset_DestroyMultiple(assets, count)` for assets
 
 Sources: [interfaces/ndk/src/relational_values_bucket.cpp74-83](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/src/relational_values_bucket.cpp#L74-L83) [interfaces/ndk/src/relational_predicates.cpp328-336](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/src/relational_predicates.cpp#L328-L336) [interfaces/ndk/src/relational_cursor.cpp165-177](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/src/relational_cursor.cpp#L165-L177)

 
## Extended Features

 
### Backup and Restore

 The NDK provides database backup and restore capabilities:

 
```

```

 Sources: [test/ndk/unittest/rdb_store_test.cpp361-383](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/ndk/unittest/rdb_store_test.cpp#L361-L383)

 
### Distributed Data Sync

 The NDK supports distributed data synchronization across devices:

 
```

```

 Sources: [test/ndk/unittest/rdb_store_test.cpp689-699](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/ndk/unittest/rdb_store_test.cpp#L689-L699) [interfaces/ndk/src/relational_store_impl.h71-74](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/ndk/src/relational_store_impl.h#L71-L74)

 
## Summary

 The NDK provides a comprehensive C interface for working with relational databases in native applications. It supports all standard database operations, transactions, and advanced features like backup/restore and distributed data synchronization. The interface is designed to be easy to use while providing full access to the underlying database capabilities.
