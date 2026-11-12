> 来源: [https://deepwiki.com/openharmony/distributeddatamgr_datamgr](https://deepwiki.com/openharmony/distributeddatamgr_datamgr)
> DeepWiki openharmony/distributeddatamgr_datamgr

# Overview

  Relevant source files 
 - [bundle.json](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/bundle.json)
 - [services/distributeddataservice/adapter/account/src/account_delegate_impl.cpp](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/adapter/account/src/account_delegate_impl.cpp)
 - [services/distributeddataservice/adapter/account/src/account_delegate_impl.h](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/adapter/account/src/account_delegate_impl.h)
 - [services/distributeddataservice/app/BUILD.gn](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/BUILD.gn)
 - [services/distributeddataservice/app/distributed_data.cfg](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/distributed_data.cfg)
 - [services/distributeddataservice/app/src/checker/BUILD.gn](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/checker/BUILD.gn)
 - [services/distributeddataservice/app/src/kvstore_account_observer.h](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/kvstore_account_observer.h)
 - [services/distributeddataservice/app/src/kvstore_app_manager.cpp](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/kvstore_app_manager.cpp)
 - [services/distributeddataservice/app/src/kvstore_app_manager.h](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/kvstore_app_manager.h)
 - [services/distributeddataservice/app/src/kvstore_data_service.cpp](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/kvstore_data_service.cpp)
 - [services/distributeddataservice/app/src/kvstore_data_service.h](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/kvstore_data_service.h)
 - [services/distributeddataservice/app/src/kvstore_meta_manager.cpp](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/kvstore_meta_manager.cpp)
 - [services/distributeddataservice/app/src/kvstore_meta_manager.h](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/kvstore_meta_manager.h)
 - [services/distributeddataservice/app/src/kvstore_user_manager.cpp](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/kvstore_user_manager.cpp)
 - [services/distributeddataservice/app/src/kvstore_user_manager.h](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/kvstore_user_manager.h)
 - [services/distributeddataservice/app/src/single_kvstore_impl.cpp](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/single_kvstore_impl.cpp)
 - [services/distributeddataservice/app/test/BUILD.gn](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/test/BUILD.gn)
 - [services/distributeddataservice/service/kvdb/executor_factory.h](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/service/kvdb/executor_factory.h)
 - [services/distributeddataservice/service/kvdb/user_delegate.cpp](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/service/kvdb/user_delegate.cpp)
 - [services/distributeddataservice/service/kvdb/user_delegate.h](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/service/kvdb/user_delegate.h)
 - [test/fuzztest/autolaunch_fuzzer/BUILD.gn](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/test/fuzztest/autolaunch_fuzzer/BUILD.gn)
 - [test/fuzztest/autolaunch_fuzzer/autolaunch_fuzzer.cpp](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/test/fuzztest/autolaunch_fuzzer/autolaunch_fuzzer.cpp)
 - [test/fuzztest/autolaunch_fuzzer/autolaunch_fuzzer.h](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/test/fuzztest/autolaunch_fuzzer/autolaunch_fuzzer.h)
 - [test/fuzztest/autolaunch_fuzzer/corpus/init](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/test/fuzztest/autolaunch_fuzzer/corpus/init)
 - [test/fuzztest/autolaunch_fuzzer/project.xml](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/test/fuzztest/autolaunch_fuzzer/project.xml)
 - [test/fuzztest/kvstore_fuzzer/BUILD.gn](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/test/fuzztest/kvstore_fuzzer/BUILD.gn)
 - [test/fuzztest/kvstore_fuzzer/corpus/init](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/test/fuzztest/kvstore_fuzzer/corpus/init)
 - [test/fuzztest/kvstore_fuzzer/kvstore_fuzzer.cpp](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/test/fuzztest/kvstore_fuzzer/kvstore_fuzzer.cpp)
 - [test/fuzztest/kvstoredisksize_fuzzer/BUILD.gn](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/test/fuzztest/kvstoredisksize_fuzzer/BUILD.gn)
 
  
## Purpose and Scope

 This document provides an introduction to the OpenHarmony Distributed Data Management Service (`distributeddatamgr_datamgr_service`), a system-level component that enables applications to store, synchronize, and manage data across multiple devices in a distributed environment. This overview covers the repository structure, primary data storage systems, architectural layers, and key components.

 For detailed information about specific subsystems:

 
 - KvStore hierarchical management and synchronization: See [KvStore System](https://deepwiki.com/openharmony/distributeddatamgr_datamgr/3-kvstore-system)
 - RDB distributed relational database operations: See [RDB System](https://deepwiki.com/openharmony/distributeddatamgr_datamgr/4-rdb-system)
 - Object Store distributed object management: See [Object Store System](https://deepwiki.com/openharmony/distributeddatamgr_datamgr/5-object-store-system)
 - Account and user lifecycle management: See [Account and User Management](https://deepwiki.com/openharmony/distributeddatamgr_datamgr/6-account-and-user-management)
 - Security, permissions, and encryption: See [Security and Permissions](https://deepwiki.com/openharmony/distributeddatamgr_datamgr/8-security-and-permissions)
 
 **Sources**: [bundle.json1-125](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/bundle.json#L1-L125) [services/distributeddataservice/app/distributed_data.cfg1-44](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/distributed_data.cfg#L1-L44)

 
---

 
## Three Main Data Storage Systems

 The repository provides three distinct distributed data storage capabilities, each exposed as a System Ability and accessible through framework APIs:

 
| System | System Ability | Purpose | Primary Use Cases |
|---|---|---|---|
| KvStore | KvStoreDataService (SA 1301) | Key-value storage with hierarchical management | Settings, preferences, caching, structured key-value data |
| RDB | RdbServiceImpl | Relational database with SQL support | Structured relational data, complex queries, transactions |
| Object Store | ObjectServiceImpl | Distributed object storage | Large objects, binary data, distributed state management |

 Each system supports automatic cross-device synchronization, encryption, backup/recovery, and multi-user isolation. They share common infrastructure for communication (SoftBusAdapter), metadata management (MetaDataManager), and DFX reporting (HiViewAdapter).

 **Sources**: [services/distributeddataservice/app/src/kvstore_data_service.h48-203](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/kvstore_data_service.h#L48-L203) [bundle.json40-43](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/bundle.json#L40-L43)

 
---

 
## Repository Structure

 
```
distributeddatamgr_datamgr_service/
├── services/distributeddataservice/
│   ├── app/                          # System Ability implementation
│   │   ├── src/
│   │   │   ├── kvstore_data_service.cpp      # Main SA (ID 1301)
│   │   │   ├── kvstore_user_manager.cpp      # Per-user store management
│   │   │   ├── kvstore_app_manager.cpp       # Per-app store management
│   │   │   ├── single_kvstore_impl.cpp       # Store instance implementation
│   │   │   ├── kvstore_meta_manager.cpp      # Metadata and encryption keys
│   │   │   └── checker/                      # Permission validation
│   │   └── distributed_data.cfg              # Service startup configuration
│   ├── framework/                    # IPC framework and stubs
│   ├── service/                      # Service implementation layer
│   │   ├── kvdb/                     # KvStore service components
│   │   ├── rdb/                      # RDB service components
│   │   ├── object/                   # Object Store service components
│   │   ├── bootstrap/                # Initialization and plugin loading
│   │   ├── config/                   # Configuration management
│   │   ├── crypto/                   # Encryption key management
│   │   ├── directory/                # Path and directory management
│   │   └── permission/               # Permission checking
│   └── adapter/                      # Platform adaptation layer
│       ├── account/                  # Account event subscriptions
│       ├── communicator/             # SoftBus integration
│       ├── broadcaster/              # Common event publishing
│       └── utils/                    # Utilities
└── test/                            # Tests and fuzzing
```

 **Sources**: [services/distributeddataservice/app/BUILD.gn1-155](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/BUILD.gn#L1-L155) [services/distributeddataservice/app/distributed_data.cfg1-44](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/distributed_data.cfg#L1-L44)

 
---

 
## Architectural Layers

 
```

```

 **Layer Descriptions**:

 
 - **Application Layer**: Native C++ or JavaScript applications using distributed data APIs
 - **Framework Layer**: Inner kits providing client-side proxies (`distributeddata_inner`) for IPC communication
 - **System Ability Layer**: `KvStoreDataService` (SA 1301) registered with `samgr`, running as user `ddms`
 - **Service Implementation**: Business logic for managing stores, synchronization, and metadata
 - **Distributed Database Engine**: Core storage engine from `kv_store/frameworks/innerkitsimpl/kvdb/distributeddb`
 - **Cross-Cutting Services**: Shared infrastructure for communication, accounts, permissions, and diagnostics
 
 **Sources**: [services/distributeddataservice/app/src/kvstore_data_service.cpp80-864](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/kvstore_data_service.cpp#L80-L864) [services/distributeddataservice/app/distributed_data.cfg22-42](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/distributed_data.cfg#L22-L42) [bundle.json94-116](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/bundle.json#L94-L116)

 
---

 
## Key Components and Code Entities

 
### System Ability Entry Point

 
```

```

 The service lifecycle begins with `distributed_data.cfg` defining the service execution environment. The `sa_main` process instantiates `KvStoreDataService` which registers itself as System Ability 1301. During `OnStart()`, it initializes the metadata manager, sets up inter-process communication, and subscribes to account events.

 **Key Classes**:

 
 - `KvStoreDataService`: Main orchestrator, inherits from `SystemAbility` and `KvStoreDataServiceStub`
 - `Bootstrap`: Loads plugins, directories, checkers, and network components
 - `KvStoreMetaManager`: Singleton managing metadata database and encryption keys
 - `AccountDelegate`: Subscribes to account lifecycle events (user add/remove/switch)
 
 **Sources**: [services/distributeddataservice/app/distributed_data.cfg22-42](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/distributed_data.cfg#L22-L42) [services/distributeddataservice/app/src/kvstore_data_service.cpp774-864](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/kvstore_data_service.cpp#L774-L864) [services/distributeddataservice/app/src/kvstore_meta_manager.cpp62-169](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/kvstore_meta_manager.cpp#L62-L169)

 
---

 
### Hierarchical Store Management

 
```

```

 The KvStore system uses a three-tier hierarchy:

 
 - **User Level** (`KvStoreUserManager`): Maps `userId` → app managers, stored in `deviceAccountMap_`
 - **App Level** (`KvStoreAppManager`): Maps `bundleName` → store instances, validated by `CheckerManager::GetAppId()`
 - **Store Level** (`SingleKvStoreImpl`): Individual store instances with `storeId`, delegate to `KvStoreNbDelegate`
 
 Each `KvStoreAppManager` maintains two `KvStoreDelegateManager` instances for different security paths:

 
 - `PATH_DE` (Device Encrypted): S0/S1 security levels, accessible before user login
 - `PATH_CE` (Credential Encrypted): S2/S3/S4 security levels, requires user credentials
 
 **Sources**: [services/distributeddataservice/app/src/kvstore_data_service.cpp157-209](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/kvstore_data_service.cpp#L157-L209) [services/distributeddataservice/app/src/kvstore_user_manager.h27-80](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/kvstore_user_manager.h#L27-L80) [services/distributeddataservice/app/src/kvstore_app_manager.cpp46-189](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/kvstore_app_manager.cpp#L46-L189)

 
---

 
### Metadata and Encryption Key Management

 
```

```

 **Key Management Flow**:

 
 - `KvStoreMetaManager::GetSecretKey()` retrieves or generates a 32-byte work key
 - `CryptoManager::Encrypt()` encrypts the work key with the root key (from HUKS)
 - Encrypted key is stored in both metadata database (as `SecretKeyMetaData`) and filesystem (as `.sig.key`)
 - Keys are validated yearly; outdated keys trigger `ReKey()` operation
 - `KvStoreMetaManager::RecoverSecretKeyFromFile()` recovers keys from filesystem if metadata is corrupted
 
 **Sources**: [services/distributeddataservice/app/src/kvstore_meta_manager.cpp240-313](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/kvstore_meta_manager.cpp#L240-L313) [services/distributeddataservice/app/src/kvstore_meta_manager.h61-85](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/kvstore_meta_manager.h#L61-L85) [services/distributeddataservice/app/src/kvstore_data_service.cpp240-285](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/kvstore_data_service.cpp#L240-L285)

 
---

 
### Service Configuration and Initialization

 The service is configured through `distributed_data.cfg` which defines:

 
```

```

 **Initialization Jobs** (`services:distributeddata`):

 
 - Create directory structure: `/data/service/el1/public/database/distributeddata/`
 - Set ownership: `ddms:ddms` with mode `02770` (setgid, group-writable)
 - Initialize subdirectories: `meta/`, `meta/backup/`, `kvdb/`
 - Create user-specific paths: `/data/misc_de/0/mdds`, `/data/misc_ce/0/mdds`
 
 **Sources**: [services/distributeddataservice/app/distributed_data.cfg1-44](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/distributed_data.cfg#L1-L44) [services/distributeddataservice/app/src/kvstore_data_service.cpp774-805](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/kvstore_data_service.cpp#L774-L805)

 
---

 
## Data Flow Example: GetSingleKvStore

 
```

```

 **Key Steps**:

 
 - **Permission Check**: `CheckerManager::GetAppId()` validates caller's `uid` and `tokenId` against bundle information
 - **Secret Key**: `GetSecretKey()` retrieves encrypted work key from `KvStoreMetaManager`, or generates new 32-byte key
 - **Hierarchy Traversal**: Navigate User → App → Store hierarchy, creating managers as needed
 - **Delegate Creation**: `KvStoreDelegateManager::GetKvStore()` opens the underlying DistributedDB database
 - **Metadata Persistence**: `MetaDataManager::SaveMeta()` stores `StoreMetaData` for future access and synchronization
 
 **Sources**: [services/distributeddataservice/app/src/kvstore_data_service.cpp157-209](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/kvstore_data_service.cpp#L157-L209) [services/distributeddataservice/app/src/kvstore_app_manager.cpp95-188](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/kvstore_app_manager.cpp#L95-L188) [services/distributeddataservice/app/src/single_kvstore_impl.cpp61-75](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/single_kvstore_impl.cpp#L61-L75)

 
---

 
## User and Account Management

 
```

```

 **Observer Priority Levels**:

 
 - **HIGH**: `UserDelegate::LocalUserObserver` updates user metadata before service cleanup
 - **LOW**: `KvStoreAccountObserver` triggers store cleanup after metadata is updated
 
 **Account Event Handling**:

 
 - `COMMON_EVENT_USER_REMOVED`: Close and delete all stores for removed user
 - `COMMON_EVENT_USER_SWITCHED`: Switch active user context
 - `COMMON_EVENT_PACKAGE_REMOVED`: Uninstall cleanup via `Uninstaller::GetInstance()`
 
 **Sources**: [services/distributeddataservice/adapter/account/src/account_delegate_impl.cpp33-76](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/adapter/account/src/account_delegate_impl.cpp#L33-L76) [services/distributeddataservice/service/kvdb/user_delegate.cpp39-213](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/service/kvdb/user_delegate.cpp#L39-L213) [services/distributeddataservice/app/src/kvstore_data_service.cpp1000-1082](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/kvstore_data_service.cpp#L1000-L1082)

 
---

 
## Communication and Device Discovery

 The system uses SoftBus for inter-device communication:

 
 - **SoftBusAdapter**: Integrates with distributed softbus, translates between NetworkId and UUID
 - **CommunicationProvider**: Singleton providing device discovery and session management
 - **ProcessCommunicatorImpl**: Implements `DistributedDB::IProcessCommunicator` for distributed database communication
 
 **Device ID Translation**:

 
 - Applications use **NetworkId** (user-facing, changeable)
 - Distributed database uses **UUID** (stable, device-unique)
 - `CommunicationProvider::GetLocalDevice()` and `GetRemoteDevices()` provide translation
 
 **Sources**: [services/distributeddataservice/adapter/communicator/src/softbus_adapter_standard.cpp (referenced in diagrams)](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/adapter/communicator/src/softbus_adapter_standard.cpp (referenced in diagrams)) [services/distributeddataservice/app/src/kvstore_data_service.cpp118-130](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/src/kvstore_data_service.cpp#L118-L130)

 
---

 
## Build and Dependencies

 The component is defined in `bundle.json` as `datamgr_service` under the `distributeddatamgr` subsystem. It declares three system capabilities:

 
 - `SystemCapability.DistributedDataManager.KVStore.Core`
 - `SystemCapability.DistributedDataManager.KVStore.Lite`
 - `SystemCapability.DistributedDataManager.KVStore.DistributedKVStore`
 
 **Key Dependencies**:

 
 - `common_event_service`: For account event subscriptions
 - `bundle_framework`: For application metadata queries
 - `samgr`: System Ability Manager integration
 - `dsoftbus`: Device communication
 - `device_auth`: Device authentication
 - `access_token`: Permission validation
 - `huks`: Hardware-backed key storage
 
 **Sub-components**:

 
 - `services/distributeddataservice/app:build_module` → System Ability binary
 - `services/distributeddataservice/framework:build_module` → IPC framework
 - `services/distributeddataservice/service:build_module` → Service implementation
 
 **Inner Kit**: `distributeddata_inner` provides client-side APIs defined in `kv_store/interfaces/innerkits/distributeddata`

 **Sources**: [bundle.json1-125](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/bundle.json#L1-L125) [services/distributeddataservice/app/BUILD.gn81-154](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/BUILD.gn#L81-L154)

 
---

 
## Testing Infrastructure

 The repository includes comprehensive testing:

 
 - **Unit Tests**: `services/distributeddataservice/app/test/` with `KvStoreDataServiceTest`, `KvStoreBackupTest`, etc.
 - **Fuzz Tests**: `test/fuzztest/` including `KvStoreFuzzTest`, `AutoLaunchFuzzTest`, `KvStoreDiskSizeFuzzTest`
 - **Test Utilities**: Mock implementations and test data generators
 
 Fuzz testing targets critical APIs like `Put()`, `Get()`, `GetEntries()`, `Sync()`, and metadata operations to ensure robustness against malformed inputs.

 **Sources**: [services/distributeddataservice/app/test/BUILD.gn61-122](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/services/distributeddataservice/app/test/BUILD.gn#L61-L122) [test/fuzztest/kvstore_fuzzer/kvstore_fuzzer.cpp1-225](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/test/fuzztest/kvstore_fuzzer/kvstore_fuzzer.cpp#L1-L225) [test/fuzztest/autolaunch_fuzzer/autolaunch_fuzzer.cpp1-77](https://github.com/openharmony/distributeddatamgr_datamgr/blob/82c3b0f6/test/fuzztest/autolaunch_fuzzer/autolaunch_fuzzer.cpp#L1-L77)

 
---

 
## Next Steps

 After understanding this overview, explore specific subsystems:

 
 - **[KvStore System](https://deepwiki.com/openharmony/distributeddatamgr_datamgr/3-kvstore-system)**: Detailed store lifecycle, synchronization mechanisms, and flow control
 - **[RDB System](https://deepwiki.com/openharmony/distributeddatamgr_datamgr/4-rdb-system)**: Relational database syncing, predicate queries, and remote query execution
 - **[Metadata Management](https://deepwiki.com/openharmony/distributeddatamgr_datamgr/3.3-metadata-management)**: In-depth coverage of metadata types, encryption, and recovery
 - **[Security and Permissions](https://deepwiki.com/openharmony/distributeddatamgr_datamgr/8-security-and-permissions)**: Permission validation, checker implementations, and encryption key management
 - **[Communication Layer](https://deepwiki.com/openharmony/distributeddatamgr_datamgr/9-communication-layer)**: SoftBus integration, device management, and session handling
