> 来源: [https://deepwiki.com/openharmony/distributeddatamgr_relational_store/7-distributed-database](https://deepwiki.com/openharmony/distributeddatamgr_relational_store/7-distributed-database)
> DeepWiki openharmony/distributeddatamgr_relational_store

# Distributed Database

  Relevant source files 
 - [frameworks/js/napi/relationalstore/include/napi_rdb_store.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/include/napi_rdb_store.h)
 - [frameworks/js/napi/relationalstore/mock/include/napi_rdb_store.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/mock/include/napi_rdb_store.h)
 - [frameworks/js/napi/relationalstore/src/napi_rdb_store.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/src/napi_rdb_store.cpp)
 - [frameworks/native/rdb/include/rdb_service_proxy.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/rdb_service_proxy.h)
 - [frameworks/native/rdb/include/rdb_store_impl.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/rdb_store_impl.h)
 - [frameworks/native/rdb/include/rdb_types_util.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/rdb_types_util.h)
 - [frameworks/native/rdb/mock/include/rdb_store_impl.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/mock/include/rdb_store_impl.h)
 - [frameworks/native/rdb/src/rdb_service_proxy.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_service_proxy.cpp)
 - [frameworks/native/rdb/src/rdb_store_impl.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp)
 - [frameworks/native/rdb/src/rdb_types_util.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_types_util.cpp)
 - [interfaces/inner_api/rdb/include/distributeddata_relational_store_ipc_interface_code.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/distributeddata_relational_store_ipc_interface_code.h)
 - [interfaces/inner_api/rdb/include/rdb_service.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/rdb_service.h)
 - [interfaces/inner_api/rdb/include/rdb_store.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/rdb_store.h)
 - [interfaces/inner_api/rdb/include/rdb_types.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/rdb_types.h)
 
  The Distributed Database component of the OpenHarmony Relational Database Management System provides capabilities for synchronizing and accessing database data across multiple devices in a distributed network. It enables applications to work with consistent data regardless of the device being used, supporting both device-to-device synchronization and cloud synchronization.

 This page covers the distributed database capabilities provided by the relational database system. For information about basic RDBMS operations, see [RDB Store Core](https://deepwiki.com/openharmony/distributeddatamgr_relational_store/2-rdb-store-core). For connection management details, see [Connection Management](https://deepwiki.com/openharmony/distributeddatamgr_relational_store/3-connection-management).

 
## Architecture

 The Distributed Database component enables seamless data sharing across multiple devices by integrating with the RDB Store Core components and providing additional services for synchronizing data and managing distributed tables.

 
### Distributed Database Architecture

 
```

```

 Sources: [frameworks/native/rdb/src/rdb_store_impl.cpp](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp) [frameworks/native/rdb/include/rdb_service_proxy.h](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/rdb_service_proxy.h)

 
### Key Components

 
 - **RdbStoreImpl**: Extends the RdbStore interface to implement distributed database capabilities including synchronization, subscription, and remote querying.
 - **RdbServiceProxy**: Client-side proxy that communicates with the RdbService through IPC mechanisms to perform distributed operations.
 - **RdbNotifierStub**: Handles notifications for data changes and synchronization completion.
 - **RdbService**: Server-side service that manages distributed database operations, including table distribution, synchronization, and observer registration.
 - **SyncEngine**: Handles data synchronization between devices, detecting changes and resolving conflicts.
 
 Sources: [frameworks/native/rdb/include/rdb_store_impl.h130-156](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/rdb_store_impl.h#L130-L156) [interfaces/inner_api/rdb/include/rdb_service.h29-101](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/rdb_service.h#L29-L101)

 
## Distributed Tables

 Distributed tables are the foundation of the distributed database functionality. They are database tables that can be synchronized across devices and/or with cloud services.

 
### Setting Up Distributed Tables

 To make a table distributed, you must call the `SetDistributedTables` method on the RdbStore instance. This registers tables for synchronization and establishes the necessary metadata to track changes.

 
```

```

 Sources: [frameworks/native/rdb/src/rdb_store_impl.cpp376-437](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L376-L437)

 
### Distributed Table Types

 The system supports different types of distributed tables:

 
| Type | Constant | Description |
|---|---|---|
| Device Distribution | DISTRIBUTED_DEVICE | Tables synchronized between devices in a distributed network |
| Cloud Synchronization | DISTRIBUTED_CLOUD | Tables synchronized with cloud services |
| Search Distribution | DISTRIBUTED_SEARCH | Tables marked for distributed search capability |

 Sources: [interfaces/inner_api/rdb/include/rdb_types.h109-113](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/rdb_types.h#L109-L113)

 
### Obtaining Distributed Table Names

 When working with distributed tables, you may need to obtain the table name used on a remote device. The `ObtainDistributedTableName` method provides this capability:

 
```

```

 Sources: [frameworks/native/rdb/src/rdb_store_impl.cpp440-454](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L440-L454) [frameworks/native/rdb/src/rdb_service_proxy.cpp59-71](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_service_proxy.cpp#L59-L71)

 
## Data Synchronization

 The distributed database provides robust synchronization capabilities between devices and with cloud services.

 
### Synchronization Options

 The system offers different synchronization modes to support various use cases:

 
```

```

 Sources: [interfaces/inner_api/rdb/include/rdb_types.h95-107](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/rdb_types.h#L95-L107) [interfaces/inner_api/rdb/include/rdb_types.h152-158](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/rdb_types.h#L152-L158)

 
### Sync Process

 The synchronization process involves several steps to ensure data consistency across devices:

 
```

```

 Sources: [frameworks/native/rdb/src/rdb_store_impl.cpp456-509](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L456-L509) [frameworks/native/rdb/src/rdb_service_proxy.cpp119-186](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_service_proxy.cpp#L119-L186)

 
### Remote Query

 Remote query allows applications to query data on a remote device without synchronizing the entire table:

 
```

```

 Sources: [frameworks/native/rdb/src/rdb_store_impl.cpp336-358](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L336-L358) [frameworks/native/rdb/src/rdb_service_proxy.cpp289-316](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_service_proxy.cpp#L289-L316)

 
## Observer Pattern

 The distributed database implements an observer pattern to notify applications of data changes across devices.

 
### Subscription Types

 
```

```

 Sources: [interfaces/inner_api/rdb/include/rdb_types.h270-290](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/rdb_types.h#L270-L290) [interfaces/inner_api/rdb/include/rdb_types.h340-358](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/rdb_types.h#L340-L358)

 
### Subscription Process

 
```

```

 Sources: [frameworks/native/rdb/src/rdb_store_impl.cpp522-749](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L522-L749) [frameworks/native/rdb/src/rdb_service_proxy.cpp220-255](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_service_proxy.cpp#L220-L255)

 
### Data Change Notification

 When data changes occur, the system notifies the registered observers:

 
```

```

 Sources: [frameworks/native/rdb/src/rdb_store_impl.cpp751-780](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L751-L780) [frameworks/native/rdb/src/rdb_store_impl.cpp818-889](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L818-L889)

 
## JavaScript API Integration

 The distributed database capabilities are exposed to JavaScript applications through the NAPI (Node API) interface.

 
### JavaScript Integration Architecture

 
```

```

 Sources: [frameworks/js/napi/relationalstore/src/napi_rdb_store.cpp62-107](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/src/napi_rdb_store.cpp#L62-L107) [frameworks/js/napi/relationalstore/include/napi_rdb_store.h38-155](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/include/napi_rdb_store.h#L38-L155)

 
### JavaScript Distributed Methods

 The RdbStore JavaScript API exposes distributed functionality through the following methods:

 
| Method | Description |
|---|---|
| setDistributedTables | Registers tables for distributed synchronization |
| sync | Synchronizes data between devices or with the cloud |
| obtainDistributedTableName | Gets the distributed table name for a specific device |
| on('dataChange') | Subscribes to data change events |
| off('dataChange') | Unsubscribes from data change events |
| on('autoSyncProgress') | Subscribes to synchronization progress events |
| off('autoSyncProgress') | Unsubscribes from synchronization progress events |
| lockCloudContainer | Locks the cloud container for exclusive operations |
| unlockCloudContainer | Releases the lock on the cloud container |

 Sources: [frameworks/js/napi/relationalstore/src/napi_rdb_store.cpp142-172](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/src/napi_rdb_store.cpp#L142-L172) [frameworks/js/napi/relationalstore/include/napi_rdb_store.h76-96](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/js/napi/relationalstore/include/napi_rdb_store.h#L76-L96)

 
## Cloud Integration

 The distributed database supports synchronization with cloud services, allowing applications to maintain data consistency across both local devices and cloud storage.

 
### Cloud Container Operations

 
```

```

 Sources: [frameworks/native/rdb/src/rdb_store_impl.cpp958-1004](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L958-L1004)

 
### Cloud Synchronization Modes

 The system provides different synchronization strategies for cloud data:

 
| Mode | Description |
|---|---|
| TIME_FIRST | Prioritize records based on timestamp, newer records win during conflicts |
| NATIVE_FIRST | Prioritize local device records during conflict resolution |
| CLOUD_FIRST | Prioritize cloud records during conflict resolution |

 Sources: [interfaces/inner_api/rdb/include/rdb_types.h95-102](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/rdb_types.h#L95-L102)

 
## Row-Level Operations

 The distributed database supports row-level locking and modification operations to manage distributed data at a granular level.

 
### Row Locking

 
```

```

 Sources: [frameworks/native/rdb/src/rdb_store_impl.cpp929-956](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L929-L956)

 
### Getting Row Modification Time

 The database can track and provide information about when rows were last modified:

 
```

```

 Sources: [frameworks/native/rdb/src/rdb_store_impl.cpp229-295](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L229-L295)

 
## IPC Communication

 The distributed database relies on Inter-Process Communication (IPC) to enable communication between the client application and the database service running in another process.

 
### Service Interface Codes

 
```

```

 Sources: [interfaces/inner_api/rdb/include/distributeddata_relational_store_ipc_interface_code.h69-96](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/distributeddata_relational_store_ipc_interface_code.h#L69-L96) [interfaces/inner_api/rdb/include/distributeddata_relational_store_ipc_interface_code.h23-28](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/distributeddata_relational_store_ipc_interface_code.h#L23-L28)

 
### IPC Data Serialization

 To transmit data structures across process boundaries, the system provides serialization utilities in `rdb_types_util.h` and `rdb_types_util.cpp`. These utilities handle marshalling and unmarshalling of complex data structures such as:

 
 - RdbSyncerParam
 - RdbPredicatesMemo
 - SyncOption
 - SubscribeOption
 - Sync results and progress details
 
 Sources: [frameworks/native/rdb/include/rdb_types_util.h52-138](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/include/rdb_types_util.h#L52-L138) [frameworks/native/rdb/src/rdb_types_util.cpp1-268](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_types_util.cpp#L1-L268)

 
## Handling Data Changes

 The distributed database system tracks data changes to ensure consistent synchronization across devices and with the cloud.

 
### Change Tracking

 
```

```

 Sources: [frameworks/native/rdb/src/rdb_store_impl.cpp818-889](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L818-L889)

 
### RdbChangedData Structure

 Changes to database data are tracked in the `RdbChangedData` structure, which identifies:

 
 - Which tables have changes
 - Whether the changes are related to tracked data
 - Whether the changes should trigger P2P synchronization
 - Whether the changes are related to knowledge data
 
 Sources: [interfaces/inner_api/rdb/include/rdb_types.h377-380](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/rdb_types.h#L377-L380) [interfaces/inner_api/rdb/include/rdb_types.h372-376](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/rdb_types.h#L372-L376)

 
## Cleanup and Maintenance

 The distributed database provides mechanisms for cleaning up dirty data and maintaining consistency across distributed systems.

 
### Dirty Data Cleanup

 The CleanDirtyData method removes dirty or inconsistent data from the database up to a specified cursor position:

 
```

```

 Sources: [frameworks/native/rdb/src/rdb_store_impl.cpp297-311](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/frameworks/native/rdb/src/rdb_store_impl.cpp#L297-L311)

 
## Security Considerations

 
### Syncer Parameters

 When establishing distributed database connections, the system uses a comprehensive parameter structure to ensure proper security controls:

 
| Parameter | Description |
|---|---|
| bundleName | Application bundle identifier |
| hapName | HAP module name |
| storeName | Database store name |
| area | Storage area identifier |
| level | Security level |
| type | Distribution type |
| isEncrypt | Whether encryption is enabled |
| password | Encryption key |
| tokenIds | Access token identifiers |
| uids | User identifiers |
| permissionNames | Required permissions |

 Sources: [interfaces/inner_api/rdb/include/rdb_types.h61-87](https://github.com/openharmony/distributeddatamgr_relational_store/blob/e3b9e39f/interfaces/inner_api/rdb/include/rdb_types.h#L61-L87)

 
## Summary

 The Distributed Database component of the OpenHarmony Relational Database Management System provides a comprehensive set of capabilities for working with data across devices in a distributed network. Key features include:

 
 - Setting up distributed tables that can be synchronized across devices and with cloud services
 - Flexible data synchronization options with different conflict resolution strategies
 - Remote querying of data on other devices
 - Observer pattern for tracking data changes across the distributed system
 - Row-level locking for distributed concurrency control
 - Cloud integration for synchronizing with cloud services
 - JavaScript API for easy access from applications
 
 By leveraging these capabilities, applications can provide a seamless experience for users across multiple devices, with consistent data regardless of which device they are using.
