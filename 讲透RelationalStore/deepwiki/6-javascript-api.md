> 来源: [https://deepwiki.com/openharmony/distributeddatamgr_relational_store/6-javascript-api](https://deepwiki.com/openharmony/distributeddatamgr_relational_store/6-javascript-api)
> DeepWiki openharmony/distributeddatamgr_relational_store

# JavaScript API

  Relevant source files 
 - [frameworks/js/napi/common/include/js_utils.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/common/include/js_utils.h)
 - [frameworks/js/napi/common/src/js_utils.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/common/src/js_utils.cpp)
 - [frameworks/js/napi/dataability/src/napi_data_ability_predicates.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/dataability/src/napi_data_ability_predicates.cpp)
 - [frameworks/js/napi/rdb/include/napi_async_call.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/include/napi_async_call.h)
 - [frameworks/js/napi/rdb/include/napi_rdb_error.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/include/napi_rdb_error.h)
 - [frameworks/js/napi/rdb/include/napi_rdb_predicates.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/include/napi_rdb_predicates.h)
 - [frameworks/js/napi/rdb/include/napi_rdb_store.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/include/napi_rdb_store.h)
 - [frameworks/js/napi/rdb/include/napi_rdb_store_helper.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/include/napi_rdb_store_helper.h)
 - [frameworks/js/napi/rdb/include/napi_result_set.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/include/napi_result_set.h)
 - [frameworks/js/napi/rdb/mock/include/napi_rdb_predicates.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/mock/include/napi_rdb_predicates.h)
 - [frameworks/js/napi/rdb/mock/include/napi_rdb_store.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/mock/include/napi_rdb_store.h)
 - [frameworks/js/napi/rdb/mock/include/napi_result_set.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/mock/include/napi_result_set.h)
 - [frameworks/js/napi/rdb/src/napi_async_call.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/src/napi_async_call.cpp)
 - [frameworks/js/napi/rdb/src/napi_rdb_predicates.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/src/napi_rdb_predicates.cpp)
 - [frameworks/js/napi/rdb/src/napi_rdb_store.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/src/napi_rdb_store.cpp)
 - [frameworks/js/napi/rdb/src/napi_rdb_store_helper.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/src/napi_rdb_store_helper.cpp)
 - [frameworks/js/napi/rdb/src/napi_result_set.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/src/napi_result_set.cpp)
 - [frameworks/js/napi/relationalstore/include/napi_async_call.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/include/napi_async_call.h)
 - [frameworks/js/napi/relationalstore/include/napi_rdb_js_utils.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/include/napi_rdb_js_utils.h)
 - [frameworks/js/napi/relationalstore/src/napi_async_call.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/src/napi_async_call.cpp)
 - [frameworks/js/napi/relationalstore/src/napi_rdb_js_utils.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/src/napi_rdb_js_utils.cpp)
 
  This page provides an overview of the JavaScript API for accessing the Relational Database (RDB) Store in OpenHarmony. The JavaScript API enables applications to interact with SQLite-based relational databases through a familiar Promise-based or callback-based asynchronous API.

 For details about the native implementation of the RDB Store, see [RDB Store Core](https://deepwiki.com/openharmony/distributeddatamgr_relational_store/2-rdb-store-core). For information about specific JavaScript API components, see [NAPI RdbStore](https://deepwiki.com/openharmony/distributeddatamgr_relational_store/6.1-napi-rdbstore), [NAPI Result Set](https://deepwiki.com/openharmony/distributeddatamgr_relational_store/6.2-napi-result-set), and [JavaScript Utilities](https://deepwiki.com/openharmony/distributeddatamgr_relational_store/6.3-javascript-utilities).

 
## API Architecture

 The JavaScript API for the RDB system follows a layered architecture pattern that bridges JavaScript applications with the native C++ implementation via the Node-API (NAPI) bindings.

 
```

```

 Sources:

 
 - [frameworks/js/napi/rdb/src/napi_rdb_store.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/src/napi_rdb_store.cpp)
 - [frameworks/js/napi/rdb/src/napi_result_set.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/src/napi_result_set.cpp)
 - [frameworks/js/napi/rdb/src/napi_rdb_predicates.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/src/napi_rdb_predicates.cpp)
 
 
## Key Components

 The JavaScript API consists of several key components that together provide a complete interface for database operations:

 
### RdbStore

 `RdbStore` is the main entry point for database operations. It provides methods for:

 
 - CRUD operations (insert, update, delete, query)
 - SQL execution
 - Transaction management
 - Database metadata access
 
 
```

```

 Sources:

 
 - [frameworks/js/napi/rdb/src/napi_rdb_store.cpp110-133](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/src/napi_rdb_store.cpp#L110-L133)
 
 
### ResultSet

 `ResultSet` provides methods to access and navigate query results. It allows traversing through result rows and accessing data in various formats.

 
```

```

 Sources:

 
 - [frameworks/js/napi/rdb/src/napi_result_set.cpp128-154](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/src/napi_result_set.cpp#L128-L154)
 
 
### RdbPredicates

 `RdbPredicates` is used to build query conditions for database operations. It supports various comparison operators and logical combinations.

 
```

```

 Sources:

 
 - [frameworks/js/napi/rdb/src/napi_rdb_predicates.cpp43-85](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/src/napi_rdb_predicates.cpp#L43-L85)
 
 
## JavaScript to Native Data Conversion

 One of the key functions of the API is converting between JavaScript data types and native C++ types. The `JSUtils` and related utility classes handle this conversion.

 
```

```

 The utility methods for data conversion include:

 
| JavaScript Type | C++ Type | Conversion Methods |
|---|---|---|
| String | std::string | Convert2Value, Convert2JSValue |
| Number (integer) | int32_t, int64_t | Convert2Value, Convert2JSValue |
| Number (float) | double | Convert2Value, Convert2JSValue |
| Boolean | bool | Convert2Value, Convert2JSValue |
| Array | std::vector | Convert2Value, Convert2JSValue |
| Object | std::map<K,V> | Convert2Value, Convert2JSValue |
| Uint8Array | std::vector<uint8_t> | Convert2Value, Convert2JSValue |
| Object | ValueObject | Convert2Value, Convert2JSValue |
| BigInt | BigInt | Convert2Value, Convert2JSValue |
| Date | Date | Convert2Value, Convert2JSValue |

 Sources:

 
 - [frameworks/js/napi/common/src/js_utils.cpp98-560](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/common/src/js_utils.cpp#L98-L560)
 - [frameworks/js/napi/relationalstore/src/napi_rdb_js_utils.cpp49-611](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/src/napi_rdb_js_utils.cpp#L49-L611)
 
 
## Asynchronous Operation Pattern

 The JavaScript API supports both Promise-based and callback-based asynchronous patterns. The following diagram illustrates the flow of an asynchronous database operation:

 
```

```

 The asynchronous pattern is implemented through a three-step process:

 
 - **Input Function**: Parses JavaScript arguments and converts them to native types
 - **Execute Function**: Performs the actual database operation in native code
 - **Output Function**: Converts the native result back to JavaScript types
 
 This pattern is encapsulated in the `AsyncCall` and `BaseContext` classes, which handle the creation and management of asynchronous work.

 Sources:

 
 - [frameworks/js/napi/rdb/src/napi_async_call.cpp25-170](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/src/napi_async_call.cpp#L25-L170)
 - [frameworks/js/napi/relationalstore/src/napi_async_call.cpp31-250](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/src/napi_async_call.cpp#L31-L250)
 
 
## RdbStore Creation Process

 The creation of an RdbStore instance follows a specific process, as illustrated below:

 
```

```

 The configuration options for creating an RdbStore include:

 
| Option | Type | Description |
|---|---|---|
| name | string | Database file name |
| securityLevel | number | Security level (S1-S4) |
| encrypt | boolean | Whether to encrypt the database |
| readOnly | boolean | Open in read-only mode |
| path | string | Custom database path |
| autoCleanDirtyData | boolean | Whether to clean dirty data automatically |

 Sources:

 
 - [frameworks/js/napi/rdb/src/napi_rdb_store_helper.cpp245-832](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/src/napi_rdb_store_helper.cpp#L245-L832)
 
 
## API Version Support

 The RDB JavaScript API supports multiple API versions, with version 9 (V9) enhancing the previous version 8 (V8) API with improved error handling and additional features. The version information is tracked in each proxy object and used for correctly handling error responses and API behavior.

 
```

```

 The system handles API version differences by:

 
 - Creating different constructors for each version
 - Tracking the API version in proxy objects
 - Using different error handling based on version
 - Maintaining backward compatibility
 
 Sources:

 
 - [frameworks/js/napi/rdb/src/napi_rdb_store.cpp142-148](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/src/napi_rdb_store.cpp#L142-L148)
 - [frameworks/js/napi/rdb/src/napi_result_set.cpp157-162](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/src/napi_result_set.cpp#L157-L162)
 - [frameworks/js/napi/rdb/src/napi_rdb_predicates.cpp96-102](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/src/napi_rdb_predicates.cpp#L96-L102)
 
 
## Error Handling

 The JavaScript API provides structured error handling through a hierarchy of error classes. Errors are propagated to JavaScript as either rejection reasons in Promises or as the first parameter in callbacks.

 
```

```

 Error codes used in the system:

 
| Error Code | Constant | Description |
|---|---|---|
| 401 | E_PARAM_ERROR | Parameter error |
| 14800000 | E_INNER_ERROR | Internal system error |
| 14800010 | E_DB_INVALID | Invalid database |
| 14800011 | E_DB_CORRUPTED | Database corrupted |
| 14800012 | E_RESULT_GOTO_ERROR | Error navigating in result set |
| 14800013 | E_RESULT_GET_ERROR | Error getting value from result set |

 Sources:

 
 - [frameworks/js/napi/rdb/include/napi_rdb_error.h15-199](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/rdb/include/napi_rdb_error.h#L15-L199)
 - [frameworks/js/napi/relationalstore/src/napi_async_call.cpp112-168](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/src/napi_async_call.cpp#L112-L168)
 
 
## Summary

 The JavaScript API for the Relational Database Store in OpenHarmony provides a comprehensive interface for database operations. It bridges JavaScript applications with the native RDB implementation through NAPI bindings, supporting both Promise-based and callback-based asynchronous patterns.

 The API consists of three main components:

 
 - **RdbStore**: For managing database operations
 - **ResultSet**: For accessing and navigating query results
 - **RdbPredicates**: For building query conditions
 
 The system handles data conversion between JavaScript and native types, manages asynchronous operations, and provides structured error handling. It supports multiple API versions with backward compatibility, allowing applications to use the most appropriate features for their needs.
