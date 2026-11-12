> 来源: [https://deepwiki.com/openharmony/communication_ipc](https://deepwiki.com/openharmony/communication_ipc)
> DeepWiki openharmony/communication_ipc

# Overview

  Relevant source files 
 - [BUILD.gn](https://github.com/openharmony/communication_ipc/blob/b41b47f3/BUILD.gn)
 - [bundle.json](https://github.com/openharmony/communication_ipc/blob/b41b47f3/bundle.json)
 - [config.gni](https://github.com/openharmony/communication_ipc/blob/b41b47f3/config.gni)
 - [interfaces/innerkits/ipc_core/BUILD.gn](https://github.com/openharmony/communication_ipc/blob/b41b47f3/interfaces/innerkits/ipc_core/BUILD.gn)
 - [interfaces/innerkits/ipc_core/include/ipc_object_proxy.h](https://github.com/openharmony/communication_ipc/blob/b41b47f3/interfaces/innerkits/ipc_core/include/ipc_object_proxy.h)
 - [interfaces/innerkits/ipc_core/include/ipc_object_stub.h](https://github.com/openharmony/communication_ipc/blob/b41b47f3/interfaces/innerkits/ipc_core/include/ipc_object_stub.h)
 - [interfaces/innerkits/ipc_napi_common/BUILD.gn](https://github.com/openharmony/communication_ipc/blob/b41b47f3/interfaces/innerkits/ipc_napi_common/BUILD.gn)
 - [interfaces/innerkits/ipc_single/BUILD.gn](https://github.com/openharmony/communication_ipc/blob/b41b47f3/interfaces/innerkits/ipc_single/BUILD.gn)
 - [interfaces/innerkits/libdbinder/BUILD.gn](https://github.com/openharmony/communication_ipc/blob/b41b47f3/interfaces/innerkits/libdbinder/BUILD.gn)
 - [interfaces/innerkits/rust/BUILD.gn](https://github.com/openharmony/communication_ipc/blob/b41b47f3/interfaces/innerkits/rust/BUILD.gn)
 - [interfaces/kits/js/napi/BUILD.gn](https://github.com/openharmony/communication_ipc/blob/b41b47f3/interfaces/kits/js/napi/BUILD.gn)
 - [ipc/native/src/core/BUILD.gn](https://github.com/openharmony/communication_ipc/blob/b41b47f3/ipc/native/src/core/BUILD.gn)
 - [ipc/native/test/unittest/common/BUILD.gn](https://github.com/openharmony/communication_ipc/blob/b41b47f3/ipc/native/test/unittest/common/BUILD.gn)
 - [ipc/native/test/unittest/common/binder_invoker_unittest.cpp](https://github.com/openharmony/communication_ipc/blob/b41b47f3/ipc/native/test/unittest/common/binder_invoker_unittest.cpp)
 - [ipc/native/test/unittest/common/buffer_object_unittest.cpp](https://github.com/openharmony/communication_ipc/blob/b41b47f3/ipc/native/test/unittest/common/buffer_object_unittest.cpp)
 - [ipc/native/test/unittest/common/dbinder_callback_stub_unittest.cpp](https://github.com/openharmony/communication_ipc/blob/b41b47f3/ipc/native/test/unittest/common/dbinder_callback_stub_unittest.cpp)
 - [ipc/native/test/unittest/common/dbinder_session_object_unittest.cpp](https://github.com/openharmony/communication_ipc/blob/b41b47f3/ipc/native/test/unittest/common/dbinder_session_object_unittest.cpp)
 - [ipc/native/test/unittest/common/ipc_binder_databus_invoker_unittest.cpp](https://github.com/openharmony/communication_ipc/blob/b41b47f3/ipc/native/test/unittest/common/ipc_binder_databus_invoker_unittest.cpp)
 - [ipc/native/test/unittest/common/ipc_connector_unittest.cpp](https://github.com/openharmony/communication_ipc/blob/b41b47f3/ipc/native/test/unittest/common/ipc_connector_unittest.cpp)
 - [ipc/native/test/unittest/common/ipc_core_unittest.cpp](https://github.com/openharmony/communication_ipc/blob/b41b47f3/ipc/native/test/unittest/common/ipc_core_unittest.cpp)
 - [ipc/native/test/unittest/common/ipc_object_proxy_unittest.cpp](https://github.com/openharmony/communication_ipc/blob/b41b47f3/ipc/native/test/unittest/common/ipc_object_proxy_unittest.cpp)
 - [ipc/native/test/unittest/common/ipc_object_stub_unittest.cpp](https://github.com/openharmony/communication_ipc/blob/b41b47f3/ipc/native/test/unittest/common/ipc_object_stub_unittest.cpp)
 - [ipc/native/test/unittest/common/ipc_process_skeleton_unittest.cpp](https://github.com/openharmony/communication_ipc/blob/b41b47f3/ipc/native/test/unittest/common/ipc_process_skeleton_unittest.cpp)
 - [ipc/native/test/unittest/common/message_parcel_unittest.cpp](https://github.com/openharmony/communication_ipc/blob/b41b47f3/ipc/native/test/unittest/common/message_parcel_unittest.cpp)
 - [ipc/native/test/unittest/common/process_skeleton_unittest.cpp](https://github.com/openharmony/communication_ipc/blob/b41b47f3/ipc/native/test/unittest/common/process_skeleton_unittest.cpp)
 
  The OpenHarmony Inter-Process Communication (IPC) system provides a comprehensive framework that enables communication between processes within the same device and across different devices. This page introduces the core components, architecture, and mechanisms of the IPC system.

 The IPC system serves as a fundamental communication infrastructure for OpenHarmony, allowing different components to interact securely and efficiently across process boundaries. It follows a proxy-stub pattern inspired by Android's Binder but extends it with distributed capabilities through the DBinder subsystem.

 
## Key Components

 
```

```

 Sources:

 
 - [bundle.json25-27](https://github.com/openharmony/communication_ipc/blob/b41b47f3/bundle.json#L25-L27)
 - [interfaces/innerkits/ipc_core/include/ipc_object_proxy.h](https://github.com/openharmony/communication_ipc/blob/b41b47f3/interfaces/innerkits/ipc_core/include/ipc_object_proxy.h)
 - [interfaces/innerkits/ipc_core/include/ipc_object_stub.h](https://github.com/openharmony/communication_ipc/blob/b41b47f3/interfaces/innerkits/ipc_core/include/ipc_object_stub.h)
 
 
## Architecture Overview

 The IPC system architecture consists of three main layers:

 
 - **Core Layer**: Provides fundamental IPC mechanisms including object proxying, message serialization, and process/thread management
 - **Distributed Layer**: Extends the core layer to support communication across different devices
 - **Language Binding Layer**: Makes the IPC system accessible from different programming languages
 
 
```

```

 Sources:

 
 - [interfaces/innerkits/ipc_single/BUILD.gn31-42](https://github.com/openharmony/communication_ipc/blob/b41b47f3/interfaces/innerkits/ipc_single/BUILD.gn#L31-L42)
 - [interfaces/innerkits/ipc_core/BUILD.gn](https://github.com/openharmony/communication_ipc/blob/b41b47f3/interfaces/innerkits/ipc_core/BUILD.gn)
 
 
## Communication Flow

 The IPC communication follows a client-server model, where:

 
 - The client (proxy) serializes parameters into a `MessageParcel`
 - The parcel is transmitted across process boundaries
 - The server (stub) deserializes the parameters and processes the request
 - The response follows the same path back to the client
 
 
```

```

 Sources:

 
 - [ipc/native/test/unittest/common/ipc_object_proxy_unittest.cpp78-88](https://github.com/openharmony/communication_ipc/blob/b41b47f3/ipc/native/test/unittest/common/ipc_object_proxy_unittest.cpp#L78-L88)
 - [ipc/native/test/unittest/common/ipc_object_stub_unittest.cpp211-239](https://github.com/openharmony/communication_ipc/blob/b41b47f3/ipc/native/test/unittest/common/ipc_object_stub_unittest.cpp#L211-L239)
 
 
## Core Components

 
### IRemoteObject Interface

 `IRemoteObject` serves as the foundation of the IPC object system. It defines the interface that both proxies and stubs must implement to participate in the IPC mechanism.

 Key methods include:

 
 - `SendRequest`: Transmits a request across process boundaries
 - `AddDeathRecipient`: Registers for notifications if the remote object dies
 - `IsProxyObject`: Identifies whether the object is a proxy (client) or stub (server)
 
 
### MessageParcel

 `MessageParcel` handles data serialization and deserialization for IPC. It provides methods to write and read various data types, including primitives, strings, arrays, file descriptors, and even other remote objects.

 
```

```

 Sources:

 
 - [ipc/native/test/unittest/common/message_parcel_unittest.cpp66-98](https://github.com/openharmony/communication_ipc/blob/b41b47f3/ipc/native/test/unittest/common/message_parcel_unittest.cpp#L66-L98)
 
 
### Proxy-Stub Pattern

 The IPC system implements a proxy-stub pattern:

 
 - **IPCObjectProxy** (client-side): Represents the remote object in the client process. When a method is called on the proxy, it serializes the parameters into a `MessageParcel` and sends the request to the server process.
 - **IPCObjectStub** (server-side): Represents the actual implementation in the server process. It receives requests from clients, deserializes the parameters, processes the request, and sends back the response.
 
 
```

```

 Sources:

 
 - [interfaces/innerkits/ipc_core/include/ipc_object_proxy.h42-46](https://github.com/openharmony/communication_ipc/blob/b41b47f3/interfaces/innerkits/ipc_core/include/ipc_object_proxy.h#L42-L46)
 - [interfaces/innerkits/ipc_core/include/ipc_object_stub.h29-40](https://github.com/openharmony/communication_ipc/blob/b41b47f3/interfaces/innerkits/ipc_core/include/ipc_object_stub.h#L29-L40)
 - [ipc/native/test/unittest/common/ipc_object_proxy_unittest.cpp113-195](https://github.com/openharmony/communication_ipc/blob/b41b47f3/ipc/native/test/unittest/common/ipc_object_proxy_unittest.cpp#L113-L195)
 - [ipc/native/test/unittest/common/ipc_object_stub_unittest.cpp90-117](https://github.com/openharmony/communication_ipc/blob/b41b47f3/ipc/native/test/unittest/common/ipc_object_stub_unittest.cpp#L90-L117)
 
 
## Process and Thread Management

 
### IPCProcessSkeleton

 `IPCProcessSkeleton` manages process-level IPC resources and serves as a container for all IPC-related objects in a process. It maintains registries of stub and proxy objects and provides methods to find, create, and manage these objects.

 Key responsibilities:

 
 - Maintaining stub and proxy object registries
 - Managing the thread pool for handling IPC requests
 - Providing access to the registry object (service manager)
 
 
### IPCThreadSkeleton

 `IPCThreadSkeleton` manages thread-level IPC resources and handles the actual transmission of IPC messages. Each thread that participates in IPC has its own `IPCThreadSkeleton` instance.

 Key responsibilities:

 
 - Managing thread-specific invokers for different protocols
 - Handling thread-specific context for IPC operations
 - Routing IPC requests to appropriate handlers
 
 
```

```

 Sources:

 
 - [ipc/native/test/unittest/common/ipc_process_skeleton_unittest.cpp64-106](https://github.com/openharmony/communication_ipc/blob/b41b47f3/ipc/native/test/unittest/common/ipc_process_skeleton_unittest.cpp#L64-L106)
 - [ipc/native/test/unittest/common/process_skeleton_unittest.cpp55-198](https://github.com/openharmony/communication_ipc/blob/b41b47f3/ipc/native/test/unittest/common/process_skeleton_unittest.cpp#L55-L198)
 
 
## Distributed Communication (DBinder)

 The DBinder system extends the IPC capabilities to distributed scenarios, allowing communication between processes on different devices.

 
### DBinderService

 `DBinderService` serves as the central component of the distributed IPC system. It manages remote object registrations and handles device discovery and connection.

 
### DBinderSessionObject

 `DBinderSessionObject` represents a session between two devices. It contains information about the service name, device ID, and other details needed for distributed communication.

 
```

```

 Sources:

 
 - [ipc/native/test/unittest/common/dbinder_session_object_unittest.cpp58-258](https://github.com/openharmony/communication_ipc/blob/b41b47f3/ipc/native/test/unittest/common/dbinder_session_object_unittest.cpp#L58-L258)
 - [ipc/native/test/unittest/common/ipc_binder_databus_invoker_unittest.cpp57-143](https://github.com/openharmony/communication_ipc/blob/b41b47f3/ipc/native/test/unittest/common/ipc_binder_databus_invoker_unittest.cpp#L57-L143)
 - [interfaces/innerkits/libdbinder/BUILD.gn51-57](https://github.com/openharmony/communication_ipc/blob/b41b47f3/interfaces/innerkits/libdbinder/BUILD.gn#L51-L57)
 
 
## Language Bindings

 The IPC system provides bindings for multiple programming languages, making it accessible from different environments.

 
### JavaScript/NAPI Bindings

 JavaScript applications can access the IPC system through NAPI (Node.js API) bindings, which provide JavaScript classes that map to the native IPC classes.

 Key components:

 
 - `rpc` module
 - `RemoteObject` class
 - `MessageParcel` class
 
 
### C API

 The C API provides access to the IPC system from C programs through a set of functions and structures.

 Key components:

 
 - `OH_IPCSkeleton` functions
 - `OH_IPCParcel` functions
 - `OH_IPCRemoteProxy` functions
 
 
### Rust Bindings

 The Rust bindings allow Rust applications to use the IPC system through idiomatic Rust interfaces.

 Key components:

 
 - `MsgParcel` struct
 - `IRemoteObject` trait
 - `IpcStatusCode` enum
 
 
```

```

 Sources:

 
 - [interfaces/kits/js/napi/BUILD.gn23-60](https://github.com/openharmony/communication_ipc/blob/b41b47f3/interfaces/kits/js/napi/BUILD.gn#L23-L60)
 - [interfaces/innerkits/ipc_napi_common/BUILD.gn25-75](https://github.com/openharmony/communication_ipc/blob/b41b47f3/interfaces/innerkits/ipc_napi_common/BUILD.gn#L25-L75)
 - [interfaces/innerkits/rust/BUILD.gn61-86](https://github.com/openharmony/communication_ipc/blob/b41b47f3/interfaces/innerkits/rust/BUILD.gn#L61-L86)
 
 
## Error Handling and Security

 The IPC system includes comprehensive error handling and security features:

 
 - **Error Codes**: Defined in `ipc_types.h`, these indicate various error conditions that might occur during IPC operations
 - **Death Notification**: Clients can register for notifications when a remote object becomes unavailable, allowing them to handle connection failures gracefully
 - **Access Control**: The system supports access tokens to control which processes can access which services
 - **Interface Verification**: Each IPC call includes an interface token that is verified by the recipient to ensure the client has the correct interface
 
 
```

```

 Sources:

 
 - [ipc/native/test/unittest/common/ipc_object_proxy_unittest.cpp506-563](https://github.com/openharmony/communication_ipc/blob/b41b47f3/ipc/native/test/unittest/common/ipc_object_proxy_unittest.cpp#L506-L563)
 - [ipc/native/test/unittest/common/ipc_core_unittest.cpp126-207](https://github.com/openharmony/communication_ipc/blob/b41b47f3/ipc/native/test/unittest/common/ipc_core_unittest.cpp#L126-L207)
 
 
## Build System Integration

 The IPC system is integrated into the OpenHarmony build system as part of the communication subsystem. It provides multiple components that can be included in different parts of the system:

 
| Component | Description | Used By |
|---|---|---|
| ipc_core | Core IPC functionality | System services, applications |
| ipc_single | Standalone IPC implementation | Core system components |
| libdbinder | Distributed IPC functionality | Distributed applications |
| ipc_rust | Rust language bindings | Rust applications |
| rpc | JavaScript bindings | JS applications |
| ipc_capi | C API bindings | C applications |

 Sources:

 
 - [BUILD.gn20-38](https://github.com/openharmony/communication_ipc/blob/b41b47f3/BUILD.gn#L20-L38)
 - [config.gni17-24](https://github.com/openharmony/communication_ipc/blob/b41b47f3/config.gni#L17-L24)
 
 
## Summary

 The OpenHarmony IPC system provides a robust framework for communication between processes, both on the same device and across different devices. It uses a proxy-stub pattern for object-oriented IPC and supports various language bindings to make it accessible from different programming environments.

 The system is designed to be efficient, secure, and flexible, supporting both synchronous and asynchronous communication patterns. The DBinder extension enables seamless distributed communication, allowing applications to interact with components on different devices as if they were local.
