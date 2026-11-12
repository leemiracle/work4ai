> 来源: [https://deepwiki.com/openharmony/distributeddatamgr_kv_store](https://deepwiki.com/openharmony/distributeddatamgr_kv_store)
> DeepWiki openharmony/distributeddatamgr_kv_store

# Overview

  Relevant source files 
 - [BUILD.gn](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/BUILD.gn)
 - [bundle.json](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/bundle.json)
 - [frameworks/common/BUILD.gn](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/common/BUILD.gn)
 - [frameworks/common/test/BUILD.gn](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/common/test/BUILD.gn)
 - [frameworks/innerkitsimpl/distributeddatafwk/test/BUILD.gn](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/innerkitsimpl/distributeddatafwk/test/BUILD.gn)
 - [frameworks/innerkitsimpl/kvdb/test/BUILD.gn](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/innerkitsimpl/kvdb/test/BUILD.gn)
 - [frameworks/libs/distributeddb/BUILD.gn](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/libs/distributeddb/BUILD.gn)
 - [frameworks/libs/distributeddb/distributeddb.gni](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/libs/distributeddb/distributeddb.gni)
 - [frameworks/libs/distributeddb/test/BUILD.gn](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/libs/distributeddb/test/BUILD.gn)
 - [frameworks/libs/distributeddb/test/moduletest/BUILD.gn](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/libs/distributeddb/test/moduletest/BUILD.gn)
 - [interfaces/inner_api/kv_store/BUILD.gn](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/interfaces/inner_api/kv_store/BUILD.gn)
 - [interfaces/innerkits/distributeddata/BUILD.gn](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/interfaces/innerkits/distributeddata/BUILD.gn)
 - [interfaces/innerkits/distributeddatamgr/BUILD.gn](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/interfaces/innerkits/distributeddatamgr/BUILD.gn)
 - [interfaces/jskits/distributeddata/BUILD.gn](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/interfaces/jskits/distributeddata/BUILD.gn)
 - [interfaces/jskits/distributedkvstore/BUILD.gn](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/interfaces/jskits/distributedkvstore/BUILD.gn)
 - [kv_store.gni](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/kv_store.gni)
 - [kvstoremock/interfaces/innerkits/distributeddata/BUILD.gn](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/kvstoremock/interfaces/innerkits/distributeddata/BUILD.gn)
 - [kvstoremock/interfaces/jskits/distributeddata/BUILD.gn](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/kvstoremock/interfaces/jskits/distributeddata/BUILD.gn)
 - [kvstoremock/interfaces/jskits/distributedkvstore/BUILD.gn](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/kvstoremock/interfaces/jskits/distributedkvstore/BUILD.gn)
 - [test/distributedtest/single_kvstore_client/BUILD.gn](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/test/distributedtest/single_kvstore_client/BUILD.gn)
 
  The DistributedDB KV Store is a distributed data management system within the OpenHarmony operating system that enables applications to store and synchronize key-value data across multiple devices. It provides a unified interface for both local and distributed data operations, supporting data consistency across devices while maintaining high performance and reliability.

 This document provides a technical overview of the DistributedDB KV Store architecture, its core components, and their interactions within the system. If you're looking for specific API usage information, see [JavaScript API](https://deepwiki.com/openharmony/distributeddatamgr_kv_store/5-javascript-api) or [Key-Value Store Implementation](https://deepwiki.com/openharmony/distributeddatamgr_kv_store/3-key-value-store-implementation) for detailed implementation information.

 The DistributedDB system supports:

 
 - Key-value data storage
 - Relational database operations
 - Peer-to-peer synchronization
 - Cloud synchronization
 - JavaScript and C++ application interfaces
 
 Sources: [bundle.json5-6](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/bundle.json#L5-L6) [frameworks/libs/distributeddb/distributeddb.gni18-19](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/libs/distributeddb/distributeddb.gni#L18-L19)

 
## System Architecture

 
```

```

 The architecture follows a layered design pattern where each layer provides specific functionality and interfaces for the layers above it. This design allows for modularity, flexibility, and clear separation of concerns.

 Sources: [interfaces/innerkits/distributeddata/BUILD.gn57-93](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/interfaces/innerkits/distributeddata/BUILD.gn#L57-L93) [frameworks/innerkitsimpl/kvdb/test/BUILD.gn61-77](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/innerkitsimpl/kvdb/test/BUILD.gn#L61-L77) [bundle.json84-96](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/bundle.json#L84-L96)

 
## Data Flow

 
```

```

 This diagram illustrates the typical data flows through the system, showing how applications interact with the database and how data synchronization works across devices.

 Sources: [frameworks/innerkitsimpl/kvdb/test/BUILD.gn40-93](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/innerkitsimpl/kvdb/test/BUILD.gn#L40-L93) [interfaces/innerkits/distributeddata/BUILD.gn117-146](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/interfaces/innerkits/distributeddata/BUILD.gn#L117-L146)

 
## Key Features and Capabilities

 
| Feature | Description |
|---|---|
| Key-Value Storage | Core storage mechanism supporting CRUD operations on key-value pairs |
| Relational Storage | Support for relational database operations and SQL queries |
| Distributed Sync | Data synchronization between devices in a distributed network |
| Cloud Sync | Data synchronization with cloud storage for backup and wider distribution |
| Schema Support | Ability to define and enforce data schemas |
| Query Support | Rich query capabilities including predicate-based searches |
| Batch Operations | Efficient batch processing for multiple data items |
| Transaction Support | ACID transaction guarantees for data operations |
| Observer Pattern | Notification mechanisms for data changes |
| Security | Encryption and access control mechanisms |

 Sources: [bundle.json38-41](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/bundle.json#L38-L41) [frameworks/libs/distributeddb/BUILD.gn49-65](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/libs/distributeddb/BUILD.gn#L49-L65)

 
# Core Components

 The DistributedDB KV Store consists of several core components that work together to provide its functionality. Here's a detailed breakdown of the main components and their responsibilities:

 
## DistributedKvDataManager

 The `DistributedKvDataManager` serves as the primary entry point for applications to interact with the distributed data management system. It manages the lifecycle of KV stores and provides methods for creating, obtaining, and closing KV store instances.

 Key responsibilities:

 
 - Creating and obtaining KV store instances
 - Managing KV store access permissions
 - Handling cross-device synchronization settings
 
 Sources: [frameworks/innerkitsimpl/distributeddatafwk/test/BUILD.gn47-51](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/innerkitsimpl/distributeddatafwk/test/BUILD.gn#L47-L51) [interfaces/innerkits/distributeddata/BUILD.gn63](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/interfaces/innerkits/distributeddata/BUILD.gn#L63-L63)

 
## Store Management Components

 
```

```

 This diagram shows the relationships between the core store management components of the system.

 Sources: [frameworks/innerkitsimpl/kvdb/test/BUILD.gn200-300](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/innerkitsimpl/kvdb/test/BUILD.gn#L200-L300) [interfaces/innerkits/distributeddata/BUILD.gn75-86](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/interfaces/innerkits/distributeddata/BUILD.gn#L75-L86)

 
### StoreManager

 The `StoreManager` is responsible for managing the lifecycle of store instances. It works closely with `StoreFactory` to create and manage KV store instances and interacts with `BackupManager` and `DevManager` for backup and device-related operations.

 Key responsibilities:

 
 - Managing store instances
 - Handling store lifecycle (open, close, delete)
 - Coordinating with backup and device management
 
 Sources: [frameworks/innerkitsimpl/kvdb/test/BUILD.gn86](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/innerkitsimpl/kvdb/test/BUILD.gn#L86-L86)

 
### StoreFactory

 The `StoreFactory` is responsible for creating store instances based on the provided options. It works with the `SecurityManager` to ensure proper access control.

 Key responsibilities:

 
 - Creating appropriate store instances based on options
 - Handling store initialization
 - Managing store security through `SecurityManager`
 
 Sources: [frameworks/innerkitsimpl/kvdb/test/BUILD.gn277-300](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/innerkitsimpl/kvdb/test/BUILD.gn#L277-L300) [frameworks/innerkitsimpl/kvdb/test/BUILD.gn85](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/innerkitsimpl/kvdb/test/BUILD.gn#L85-L85)

 
### SingleStoreImpl

 The `SingleStoreImpl` implements the core KV store functionality. It serves as the bridge between the application layer and the underlying database implementation.

 Key responsibilities:

 
 - Implementing CRUD operations (Put, Get, Delete)
 - Managing data subscriptions and notifications
 - Handling synchronization with other devices
 
 Sources: [frameworks/innerkitsimpl/kvdb/test/BUILD.gn119-126](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/innerkitsimpl/kvdb/test/BUILD.gn#L119-L126) [interfaces/innerkits/distributeddata/BUILD.gn82-84](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/interfaces/innerkits/distributeddata/BUILD.gn#L82-L84)

 
### Security and Backup Components

 The system includes dedicated components for security and backup:

 
 - **SecurityManager**: Handles permission checking and encryption key management
 - **BackupManager**: Manages database backup and restore operations
 - **DevManager**: Handles device discovery and management for synchronization
 
 Sources: [frameworks/innerkitsimpl/kvdb/test/BUILD.gn175-199](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/innerkitsimpl/kvdb/test/BUILD.gn#L175-L199) [frameworks/innerkitsimpl/kvdb/test/BUILD.gn200-223](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/innerkitsimpl/kvdb/test/BUILD.gn#L200-L223)

 
## Storage Implementations

 
```

```

 The system supports multiple storage implementations to cater to different use cases:

 
 - **SQLiteSingleVerNaturalStore**: Key-value storage implementation using SQLite
 - **RelationalSyncAbleStorage**: Relational database storage with synchronization capabilities
 - **RdSingleVerNaturalStore**: Storage implementation using GaussDB RD
 
 Sources: [frameworks/libs/distributeddb/distributeddb.gni21-273](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/libs/distributeddb/distributeddb.gni#L21-L273) [frameworks/libs/distributeddb/TEST.gn455-460](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/libs/distributeddb/TEST.gn#L455-L460)

 
## Synchronization System

 
```

```

 The synchronization system is responsible for keeping data consistent across devices and with cloud storage. It consists of several components:

 
 - **SingleVerSyncer/MultiVerSyncer/RelationalSyncer**: Handle peer-to-peer synchronization for different storage types
 - **CloudSyncer**: Manages synchronization with cloud storage
 - **SyncStateMachine**: Controls the synchronization process state transitions
 - **DataSync**: Handles the actual data synchronization operations
 - **Communicator**: Enables communication between devices for synchronization
 
 Sources: [frameworks/libs/distributeddb/distributeddb.gni258-274](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/libs/distributeddb/distributeddb.gni#L258-L274) [frameworks/libs/distributeddb/test/BUILD.gn525-533](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/libs/distributeddb/test/BUILD.gn#L525-L533)

 
# Implementation Details

 
## Key-Value Store Interface

 The system provides several key interfaces for applications to interact with the KV store:

 
```

```

 This diagram shows the main interfaces that applications use to interact with the KV store.

 Sources: [interfaces/innerkits/distributeddata/BUILD.gn102-116](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/interfaces/innerkits/distributeddata/BUILD.gn#L102-L116) [bundle.json101-113](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/bundle.json#L101-L113)

 
## Data Types and Storage

 The system supports various data types for both keys and values:

 
| Data Type | Description | Usage |
|---|---|---|
| Blob | Binary data container | Keys and values can be stored as Blob objects |
| String | Text data | Commonly used for keys and textual values |
| Integer | Numeric data | Used for numeric values and sometimes keys |
| Float | Floating-point data | Used for numeric values |
| Boolean | True/false values | Used for boolean flags |
| Array | Collection of values | Used for complex data structures |
| Object | JSON-like objects | Used for structured data |

 Sources: [bundle.json101-113](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/bundle.json#L101-L113) [interfaces/innerkits/distributeddata/BUILD.gn114](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/interfaces/innerkits/distributeddata/BUILD.gn#L114-L114)

 
## Synchronization Modes

 The system supports different synchronization modes:

 
| Mode | Description |
|---|---|
| PUSH | Push local data to remote devices |
| PULL | Pull data from remote devices to local |
| PUSH_PULL | Bidirectional synchronization |
| SYNC_ONLY | Sync only specific data |

 Sources: [frameworks/libs/distributeddb/test/moduletest/BUILD.gn80-126](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/libs/distributeddb/test/moduletest/BUILD.gn#L80-L126)

 
## Security Implementation

 The DistributedDB KV Store implements several security measures:

 
 - **Access control**: Permission checks based on user ID, app ID, and store ID
 - **Data encryption**: Encryption of data at rest using keys derived from user passwords
 - **Secure communication**: Encrypted data transmission during synchronization
 - **Identity verification**: Verification of device identity during synchronization
 
 Sources: [frameworks/innerkitsimpl/kvdb/test/BUILD.gn302-323](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/frameworks/innerkitsimpl/kvdb/test/BUILD.gn#L302-L323) [bundle.json66-77](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/bundle.json#L66-L77)

 
# JavaScript API Integration

 The system provides JavaScript API bindings to enable web and Node.js applications to use the KV store:

 
```

```

 The JavaScript API integration uses N-API (Node-API) to bridge between JavaScript and the native C++ implementation. This architecture allows JavaScript applications to seamlessly interact with the distributed data management system.

 Sources: [interfaces/jskits/distributedkvstore/BUILD.gn58-72](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/interfaces/jskits/distributedkvstore/BUILD.gn#L58-L72) [interfaces/jskits/distributeddata/BUILD.gn58-71](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/interfaces/jskits/distributeddata/BUILD.gn#L58-L71)

 
# Conclusion

 The DistributedDB KV Store provides a robust framework for distributed data management in OpenHarmony. Its layered architecture enables flexible storage options, efficient synchronization, and secure data operations across multiple devices. The system supports both key-value and relational data models, making it versatile for various application needs.

 Key strengths of the system include:

 
 - **Unified API** for both local and distributed data operations
 - **Multiple storage backends** supporting various use cases
 - **Robust synchronization** for peer-to-peer and cloud scenarios
 - **Security features** including access control and encryption
 - **JavaScript integration** enabling web application development
 
 For specific API usage, implementation details, or extension mechanisms, please refer to the related pages listed in the document.

 Sources: [bundle.json5-6](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/bundle.json#L5-L6) [bundle.json38-41](https://github.com/openharmony/distributeddatamgr_kv_store/blob/c5cb6990/bundle.json#L38-L41)
