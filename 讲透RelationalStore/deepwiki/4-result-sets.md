> 来源: [https://deepwiki.com/openharmony/distributeddatamgr_relational_store/4-result-sets](https://deepwiki.com/openharmony/distributeddatamgr_relational_store/4-result-sets)
> DeepWiki openharmony/distributeddatamgr_relational_store

# Result Sets

  Relevant source files 
 - [frameworks/js/napi/relationalstore/include/napi_result_set.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/include/napi_result_set.h)
 - [frameworks/js/napi/relationalstore/mock/include/napi_result_set.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/mock/include/napi_result_set.h)
 - [frameworks/js/napi/relationalstore/src/napi_result_set.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/src/napi_result_set.cpp)
 - [frameworks/native/rdb/include/sqlite_shared_result_set.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/sqlite_shared_result_set.h)
 - [frameworks/native/rdb/include/step_result_set.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/step_result_set.h)
 - [frameworks/native/rdb/src/abs_result_set.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/abs_result_set.cpp)
 - [frameworks/native/rdb/src/abs_shared_result_set.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/abs_shared_result_set.cpp)
 - [frameworks/native/rdb/src/sqlite_shared_result_set.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/sqlite_shared_result_set.cpp)
 - [frameworks/native/rdb/src/step_result_set.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/step_result_set.cpp)
 - [interfaces/inner_api/rdb/include/abs_result_set.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/abs_result_set.h)
 - [interfaces/inner_api/rdb/include/result_set.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/result_set.h)
 - [test/js/relationalstore/performance/src/SceneGetValuesBucketPerf.js](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/js/relationalstore/performance/src/SceneGetValuesBucketPerf.js)
 - [test/js/relationalstore/unittest/src/RdbStoreResultSetGetRow.test.js](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/js/relationalstore/unittest/src/RdbStoreResultSetGetRow.test.js)
 - [test/js/relationalstore/unittest/src/RdbStoreResultSetGetValue.test.js](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/js/relationalstore/unittest/src/RdbStoreResultSetGetValue.test.js)
 - [test/js/relationalstore/unittest/src/RdbStoreResultSetJsunit.test.js](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/js/relationalstore/unittest/src/RdbStoreResultSetJsunit.test.js)
 - [test/js/relationalstore/unittest/src/RdbStoreResultSetSyncJsunit.test.js](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/js/relationalstore/unittest/src/RdbStoreResultSetSyncJsunit.test.js)
 - [test/native/rdb/unittest/rdb_sqlite_shared_result_set_test.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/native/rdb/unittest/rdb_sqlite_shared_result_set_test.cpp)
 - [test/native/rdb/unittest/rdb_step_result_set_test.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/native/rdb/unittest/rdb_step_result_set_test.cpp)
 
  Result Sets are a critical component of the OpenHarmony Distributed Relational Database Management System (RDBMS). They provide structured access to data returned from database queries, allowing applications to navigate through and extract information from query results in an efficient manner.

 This document describes the Result Set architecture, implementations, lifecycle, and usage patterns within the OpenHarmony RDBMS. For information about executing queries that produce result sets, see [RDB Store Core](https://deepwiki.com/openharmony/distributeddatamgr_relational_store/2-rdb-store-core) and [SQL Query Building](https://deepwiki.com/openharmony/distributeddatamgr_relational_store/2.4-sql-query-building).

 
## Result Set Fundamentals

 In the OpenHarmony RDBMS, a Result Set is an object that provides access to the results of a database query. It acts as a cursor that can be moved to point to different rows in the result data, with methods to retrieve the values in each column of the current row.

 
```

```

 Sources: [interfaces/inner_api/rdb/include/abs_result_set.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/abs_result_set.h) [frameworks/native/rdb/src/abs_result_set.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/abs_result_set.cpp) [interfaces/inner_api/rdb/include/result_set.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/result_set.h)

 The Result Set is designed to provide forward and backward iteration capabilities, allowing applications to move through rows in any order and extract data in the type required by the application.

 
### Types of Result Sets

 The OpenHarmony RDBMS provides two primary implementations of Result Sets:

 
 - **StepResultSet**: A step-by-step result set that fetches rows one at a time from the database. It is memory-efficient but may require multiple database operations for navigation.
 - **SqliteSharedResultSet**: A shared-memory result set that loads chunks of data into a shared memory block. This enables faster navigation but may use more memory.
 
 
```

```

 Sources: [frameworks/native/rdb/src/step_result_set.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/step_result_set.cpp) [frameworks/native/rdb/src/abs_shared_result_set.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/abs_shared_result_set.cpp) [frameworks/native/rdb/src/sqlite_shared_result_set.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/sqlite_shared_result_set.cpp)

 
## Result Set Lifecycle

 The lifecycle of a Result Set is tightly managed to ensure proper resource utilization and database connection management.

 
```

```

 Sources: [frameworks/native/rdb/src/abs_result_set.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/abs_result_set.cpp) [frameworks/native/rdb/src/step_result_set.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/step_result_set.cpp)

 
### Creation

 A Result Set is typically created as the result of a query operation from an RdbStore instance. The query determines the initial state of the Result Set, including its column structure and row data.

 For example, in the `StepResultSet` implementation, the constructor takes a database connection, SQL query, and arguments and prepares the query for execution:

 
```
StepResultSet::StepResultSet(Time start, Conn conn, const std::string &sql, const Values &args, bool preCount, bool safe)
```

 Sources: [frameworks/native/rdb/src/step_result_set.cpp34-71](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/step_result_set.cpp#L34-L71)

 
### Navigation

 After creation, a Result Set must be positioned on a valid row before data can be retrieved. The initial position is typically before the first row, so applications must call a navigation method like `goToFirstRow()` to position the cursor.

 The primary navigation methods include:

 
 - `GoToFirstRow()`: Moves to the first row
 - `GoToLastRow()`: Moves to the last row
 - `GoToNextRow()`: Moves to the next row
 - `GoToPreviousRow()`: Moves to the previous row
 - `GoToRow(position)`: Moves to a specific row by position
 - `GoTo(offset)`: Moves relative to current position
 
 Each of these methods returns a status code indicating success or failure of the operation.

 Sources: [frameworks/native/rdb/src/abs_result_set.cpp286-320](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/abs_result_set.cpp#L286-L320) [frameworks/native/rdb/src/step_result_set.cpp178-260](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/step_result_set.cpp#L178-L260)

 
### Position Check Methods

 The Result Set provides methods to check its current position:

 
 - `IsStarted()`: Returns true if positioned on a row (not before the first row)
 - `IsEnded()`: Returns true if positioned after the last row
 - `IsAtFirstRow()`: Returns true if positioned on the first row
 - `IsAtLastRow()`: Returns true if positioned on the last row
 - `GetRowIndex()`: Returns the current row position (0-based)
 
 Sources: [frameworks/native/rdb/src/abs_result_set.cpp322-361](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/abs_result_set.cpp#L322-L361)

 
### Data Retrieval

 Once positioned on a valid row, data can be retrieved using various getter methods:

 
 - `GetString(columnIndex)`: Retrieves string data
 - `GetInt(columnIndex)`: Retrieves integer data
 - `GetLong(columnIndex)`: Retrieves long integer data
 - `GetDouble(columnIndex)`: Retrieves double-precision data
 - `GetBlob(columnIndex)`: Retrieves binary data
 - `GetAsset(columnIndex)`: Retrieves asset data (special type)
 - `GetAssets(columnIndex)`: Retrieves assets collection
 - `GetFloat32Array(columnIndex)`: Retrieves float array data
 - `GetRow()`: Retrieves the entire current row as a RowEntity
 
 Column indices can be obtained either by position (0-based) or by name using the `GetColumnIndex(columnName)` method.

 Sources: [frameworks/native/rdb/src/abs_result_set.cpp153-230](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/abs_result_set.cpp#L153-L230) [frameworks/native/rdb/src/step_result_set.cpp352-376](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/step_result_set.cpp#L352-L376)

 
### Closing

 When the application is finished with a Result Set, it should call `Close()` to release database resources. This is particularly important for `StepResultSet` as it maintains an active database connection.

 The `Close()` method releases all resources associated with the Result Set, making it unusable for further operations. The `IsClosed()` method can be used to check if a Result Set has been closed.

 Sources: [frameworks/native/rdb/src/abs_result_set.cpp437-451](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/abs_result_set.cpp#L437-L451) [frameworks/native/rdb/src/step_result_set.cpp262-276](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/step_result_set.cpp#L262-L276)

 
## Working with Result Sets

 This section details common operations and best practices for working with Result Sets.

 
### Determining Result Set Properties

 Before processing data, it's often useful to determine the structure of the Result Set:

 
 - `GetRowCount()`: Returns the total number of rows
 - `GetColumnCount()`: Returns the number of columns
 - `GetAllColumnNames()`: Returns a list of column names
 - `GetColumnName(columnIndex)`: Returns the name of a specific column
 - `GetColumnType(columnIndex)`: Returns the data type of a specific column
 
 Sources: [frameworks/native/rdb/src/abs_result_set.cpp90-150](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/abs_result_set.cpp#L90-L150) [frameworks/native/rdb/src/step_result_set.cpp127-149](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/step_result_set.cpp#L127-L149)

 
### Column Types in Result Sets

 The Result Set identifies different data types using the ColumnType enumeration:

 
```

```

 When retrieving data, it's important to match the column type with the appropriate getter method.

 Sources: [frameworks/native/rdb/src/step_result_set.cpp151-172](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/step_result_set.cpp#L151-L172) [frameworks/native/rdb/src/abs_shared_result_set.cpp79-92](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/abs_shared_result_set.cpp#L79-L92)

 
### Row Entity

 The `GetRow()` method returns a RowEntity object, which encapsulates an entire row of data. This can be more convenient than retrieving individual columns:

 
```

```

 Sources: [interfaces/inner_api/rdb/include/result_set.h28-40](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/result_set.h#L28-L40) [frameworks/native/rdb/src/abs_result_set.cpp32-74](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/abs_result_set.cpp#L32-L74)

 
### Batch Retrieval with GetRows

 For applications that need to process multiple rows at once, the `GetRows(maxCount, position)` method provides efficient batch retrieval:

 
```

```

 This method returns up to `maxCount` rows starting from the specified position, which can significantly reduce the number of method calls required to process a large result set.

 Sources: [frameworks/js/napi/relationalstore/src/napi_result_set.cpp616-655](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/src/napi_result_set.cpp#L616-L655)

 
## JavaScript Interface

 The OpenHarmony RDBMS provides a JavaScript API for working with Result Sets through the NAPI (Node.js API) bridge.

 
### ResultSetProxy

 The `ResultSetProxy` class serves as a bridge between JavaScript and the native Result Set implementation:

 
```

```

 Sources: [frameworks/js/napi/relationalstore/src/napi_result_set.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/src/napi_result_set.cpp) [frameworks/js/napi/relationalstore/include/napi_result_set.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/include/napi_result_set.h)

 
### JavaScript API Methods

 The JavaScript API provides methods mirroring the native interface, with some adaptations for JavaScript's type system:

 
| Category | Methods |
|---|---|
| Navigation | goToFirstRow(), goToLastRow(), goToNextRow(), goToPreviousRow(), goToRow(position), goTo(offset) |
| Position Check | isStarted, isEnded, isAtFirstRow, isAtLastRow, rowIndex, rowCount |
| Column Info | columnNames, columnCount, getColumnIndex(name), getColumnName(index), getColumnType(index) |
| Data Retrieval | getString(index), getInt(index), getLong(index), getDouble(index), getBlob(index), getRow(), getRows(maxCount, position) |
| Management | close(), isClosed |

 Sources: [frameworks/js/napi/relationalstore/src/napi_result_set.cpp732-768](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/src/napi_result_set.cpp#L732-L768) [test/js/relationalstore/unittest/src/RdbStoreResultSetJsunit.test.js](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/js/relationalstore/unittest/src/RdbStoreResultSetJsunit.test.js)

 
### Example JavaScript Usage

 Here's how you might use a Result Set in JavaScript:

 
```

```

 Sources: [test/js/relationalstore/unittest/src/RdbStoreResultSetJsunit.test.js132-153](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/js/relationalstore/unittest/src/RdbStoreResultSetJsunit.test.js#L132-L153) [test/js/relationalstore/unittest/src/RdbStoreResultSetGetRow.test.js122-148](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/js/relationalstore/unittest/src/RdbStoreResultSetGetRow.test.js#L122-L148)

 
## Result Set Implementations

 The OpenHarmony RDBMS provides two main Result Set implementations with different performance characteristics.

 
### StepResultSet

 The `StepResultSet` implementation processes query results one row at a time:

 
```

```

 Key characteristics of StepResultSet:

 
 - Lower memory usage as only one row is in memory at a time
 - May require more database calls for navigation operations
 - Better for large result sets where memory is a concern
 - Implementation details in [frameworks/native/rdb/src/step_result_set.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/step_result_set.cpp)
 
 Sources: [frameworks/native/rdb/include/step_result_set.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/step_result_set.h) [frameworks/native/rdb/src/step_result_set.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/step_result_set.cpp)

 
### SqliteSharedResultSet

 The `SqliteSharedResultSet` implementation uses shared memory to store chunks of result data:

 
```

```

 Key characteristics of SqliteSharedResultSet:

 
 - Uses shared memory to store multiple rows at once
 - Faster navigation for rows in the current memory block
 - Higher memory usage
 - Better for smaller result sets or when performance is critical
 - Implementation details in [frameworks/native/rdb/src/sqlite_shared_result_set.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/sqlite_shared_result_set.cpp)
 
 Sources: [frameworks/native/rdb/include/sqlite_shared_result_set.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/sqlite_shared_result_set.h) [frameworks/native/rdb/src/sqlite_shared_result_set.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/sqlite_shared_result_set.cpp)

 
## Performance Considerations

 When working with Result Sets, consider these performance guidelines:

 
 - **Close Result Sets when done**: Always call `close()` when finished to release database resources.
 - **Use appropriate getters**: Match the getter method to the column type for optimal performance.
 - **Batch processing**: For large result sets, consider using `getRows()` to retrieve multiple rows at once.
 - **Column indices**: Cache column indices retrieved from `getColumnIndex()` rather than looking them up repeatedly.
 - **Implementation choice**:

 
 - Use StepResultSet (via `queryByStep()`) for large result sets to minimize memory usage
 - Use SqliteSharedResultSet (via `query()`) for faster navigation with smaller result sets
 - **Avoid unnecessary navigation**: Plan your result set traversal to minimize navigation operations.
 
 Sources: [test/js/relationalstore/performance/src/SceneGetValuesBucketPerf.js](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/js/relationalstore/performance/src/SceneGetValuesBucketPerf.js) [test/native/rdb/unittest/rdb_step_result_set_test.cpp898-915](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/test/native/rdb/unittest/rdb_step_result_set_test.cpp#L898-L915)

 
## Error Handling

 Result Set operations return error codes to indicate success or failure. Common error codes include:

 
| Error Code | Meaning |
|---|---|
| E_OK | Operation successful |
| E_ALREADY_CLOSED | Result set has been closed |
| E_ROW_OUT_RANGE | Attempted to access a row outside the valid range |
| E_COLUMN_OUT_RANGE | Attempted to access a column outside the valid range |
| E_INVALID_OBJECT_TYPE | Type mismatch in data retrieval |

 It's important to check return values from navigation methods and handle errors appropriately.

 Sources: [frameworks/native/rdb/src/abs_result_set.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/abs_result_set.cpp) [frameworks/native/rdb/src/step_result_set.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/step_result_set.cpp)

 
## Summary

 Result Sets are the primary interface for accessing query results in the OpenHarmony Distributed RDBMS. They provide methods for navigating through rows, retrieving column data in various formats, and managing the lifecycle of query results.

 By understanding the different Result Set implementations and their performance characteristics, developers can optimize their database access patterns for their specific application needs.
