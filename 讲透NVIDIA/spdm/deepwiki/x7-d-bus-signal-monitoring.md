<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/spdm · extra page D-Bus Signal Monitoring · fetched 2026-10-26 -->

# D-Bus Signal Monitoring

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [spdmd/mctp_endpoint_discovery.cpp](spdmd/mctp_endpoint_discovery.cpp)
- [spdmd/mctp_endpoint_discovery.hpp](spdmd/mctp_endpoint_discovery.hpp)

</details>



## Purpose and Scope

This page documents how the `MctpDiscovery` class monitors D-Bus signals to detect SPDM-capable endpoints. The discovery system relies on `InterfacesAdded` signals from both MCTP control services and inventory management services to identify new devices. For information about how discovered endpoints are correlated and prioritized, see [Discovery Modes](#3.3.1).

The signal monitoring subsystem is implemented in the `MctpDiscovery` constructor and associated handler methods. It establishes D-Bus signal matches that trigger callbacks when new MCTP endpoints or inventory items appear on the system bus.

**Sources:** [spdmd/mctp_endpoint_discovery.cpp:40-116](), [spdmd/mctp_endpoint_discovery.hpp:34-273]()

---

## Signal Handler Registration

The `MctpDiscovery` constructor registers up to three different D-Bus signal handlers depending on compile-time configuration:

| Signal Handler | D-Bus Rule | Condition | Purpose |
|----------------|-----------|-----------|---------|
| `mctpMatch` | `interfacesAdded` at `/xyz/openbmc_project/mctp` or `/au/com/codeconstruct/mctp1` | Always | Detect new MCTP endpoints |
| `inventoryMatch` | `interfacesAddedAtPath` at `/xyz/openbmc_project/inventory/system/chassis/` | `!DISCOVERY_ONLY_FROM_MCTP_CONTROL` | Detect new inventory SPDM responders |
| `ccsmChange` | `propertiesChanged` for CSM ready state | `CSM_SERVICE_ENABLED` | Monitor MCTP service readiness |

### Signal Handler Initialization Flow

```mermaid
graph TB
    Constructor["MctpDiscovery()"]
    InitCSM["initCsmStatus()"]
    
    CreateMCTPMatch["Create mctpMatch<br/>sdbusplus::bus::match_t"]
    MCTPCallback["Lambda callback:<br/>mctpNewObjectSignal()"]
    
    CreateInvMatch["Create inventoryMatch<br/>sdbusplus::bus::match_t"]
    InvCallback["Lambda callback:<br/>inventoryNewObjectSignal()"]
    
    CreateCSMMatch["Create ccsmChange<br/>sdbusplus::bus::match_t"]
    CSMCallback["Lambda callback:<br/>Update ccsmReady flag"]
    
    CheckCSM{CSM enabled?}
    CheckDiscMode{DISCOVERY_ONLY_FROM<br/>_MCTP_CONTROL?}
    
    Constructor --> InitCSM
    Constructor --> CreateMCTPMatch
    CreateMCTPMatch --> MCTPCallback
    
    Constructor --> CheckDiscMode
    CheckDiscMode -->|No| CreateInvMatch
    CreateInvMatch --> InvCallback
    
    Constructor --> CheckCSM
    CheckCSM -->|Yes| CreateCSMMatch
    CreateCSMMatch --> CSMCallback
    
    style CreateMCTPMatch fill:#f9f9f9
    style CreateInvMatch fill:#f9f9f9
    style CreateCSMMatch fill:#f9f9f9
```

The MCTP signal match uses `sdbusplus::bus::match::rules::interfacesAdded(mctpPath)` where `mctpPath` is `/xyz/openbmc_project/mctp` for userspace MCTP or `/au/com/codeconstruct/mctp1` for kernel MCTP. The inventory match targets the specific base path `/xyz/openbmc_project/inventory/system/chassis/`.

**Sources:** [spdmd/mctp_endpoint_discovery.cpp:40-116](), [spdmd/mctp_endpoint_discovery.hpp:165-169](), [spdmd/mctp_endpoint_discovery.hpp:134-139]()

---

## MCTP Endpoint Signal Monitoring

When a new MCTP endpoint is added to the system, the MCTP control daemon publishes an `InterfacesAdded` signal that triggers the `mctpMatch` handler. The handler extracts endpoint properties and initiates responder creation.

### MCTP Signal Processing Flow

```mermaid
sequenceDiagram
    participant MCTP as MCTP Control Daemon
    participant DBus as D-Bus System Bus
    participant Handler as mctpMatch Lambda
    participant Signal as mctpNewObjectSignal()
    participant Extract as Property Extractors
    participant App as SpdmdApp
    
    MCTP->>DBus: InterfacesAdded signal<br/>(objectPath, interfaces)
    DBus->>Handler: Signal delivery
    
    Handler->>Handler: Check ccsmReady flag
    
    alt ccsmReady is true
        Handler->>Handler: setupMCTPServices()
        Handler->>Signal: Call with objectPath, interfaces
        
        Signal->>Extract: getEid(interfaces)
        Extract-->>Signal: EidType (uint8_t or uint32_t)
        
        Signal->>Extract: getUUID(interfaces)
        Extract-->>Signal: std::string uuid
        
        Signal->>Extract: getMediumType(interfaces)
        Extract-->>Signal: std::string mediumType
        
        Signal->>Extract: getBindingType(interfaces)
        Extract-->>Signal: std::string bindingType
        
        alt !MCTP_IN_KERNEL
            Signal->>Extract: getTransportSocket(interfaces)
            Extract-->>Signal: std::string sockPath
            Signal->>Signal: tryConnectMCTP(sockPath)
        end
        
        alt DISCOVERY_ONLY_FROM_MCTP_CONTROL
            Signal->>App: discoveryUpdateResponder(args)
        else
            Signal->>Signal: getInventoryPathAsync(uuid)
            Signal->>App: discoveryUpdateResponder(args)
        end
    end
```

The `mctpNewObjectSignal()` method validates that the EID is valid (less than 0xFF) and that SPDM is listed in the `SupportedMessageTypes` property. In userspace MCTP mode, it also attempts to connect to the UNIX socket provided in the `xyz.openbmc_project.Common.UnixSocket` interface.

**Sources:** [spdmd/mctp_endpoint_discovery.cpp:277-494](), [spdmd/mctp_endpoint_discovery.cpp:259-275]()

---

## Inventory Item Signal Monitoring

When `DISCOVERY_ONLY_FROM_MCTP_CONTROL` is not defined, the daemon also monitors the inventory service for new SPDM responder objects. This enables bidirectional discovery where either the MCTP endpoint or the inventory item can appear first.

### Inventory Signal Processing Flow

```mermaid
sequenceDiagram
    participant Inv as Inventory Service
    participant DBus as D-Bus System Bus
    participant Handler as inventoryMatch Lambda
    participant Signal as inventoryNewObjectSignal()
    participant Async as getMCTPObjectAsync()
    participant App as SpdmdApp
    
    Inv->>DBus: InterfacesAdded at<br/>/xyz/openbmc_project/inventory/system/chassis/
    DBus->>Handler: Signal delivery
    Handler->>Handler: Check for SPDMResponder interface
    
    alt Has inventorySPDMResponderIntfName
        alt ccsmReady is true
            Handler->>Signal: Call with objectPath, interfaces
        else
            Handler->>Handler: Queue in inventorySignalQueue
            Note over Handler: Deferred until CSM ready
        end
    end
    
    Signal->>Signal: getUUID(interfaces)
    Signal->>Async: Search for MCTP object with UUID
    
    loop For each MCTP control service
        Async->>DBus: GetManagedObjects()
        DBus-->>Async: ObjectValueTree
        Async->>Async: Match UUID
    end
    
    Async-->>Signal: Object (path + interfaces)
    Signal->>Signal: Extract EID, mediumType,<br/>bindingType, transpSock
    
    alt !MCTP_IN_KERNEL
        Signal->>Signal: tryConnectMCTP(transpSock)
    end
    
    Signal->>App: discoveryUpdateResponder(args)
```

The inventory signal handler ensures the `xyz.openbmc_project.Inventory.Item.SPDMResponder` interface is present before processing. If CSM is not ready, the signal is queued in `inventorySignalQueue` and processed later when CSM becomes ready.

**Sources:** [spdmd/mctp_endpoint_discovery.cpp:42-67](), [spdmd/mctp_endpoint_discovery.cpp:497-626]()

---

## CSM State Monitoring

When `CSM_SERVICE_ENABLED` is defined, the discovery system waits for the Configurable State Manager (CSM) to signal that MCTP services are ready before processing endpoint discoveries.

### CSM Ready State Handling

```mermaid
graph TB
    Init["initCsmStatus()"]
    GetState["async_method_call Get<br/>csmFeatureReadyStateIntfName.State"]
    Handler["Handler callback"]
    
    CheckState{State ==<br/>'Enabled'?}
    SetReady["ccsmReady = true"]
    SetNotReady["ccsmReady = false"]
    
    Setup["setupMCTPServices()"]
    ProcessQueue["Process inventorySignalQueue"]
    
    PropChange["PropertiesChanged signal<br/>on ccsmChange match"]
    UpdateState["Update ccsmReady<br/>from State property"]
    
    Init --> GetState
    GetState --> Handler
    Handler --> CheckState
    
    CheckState -->|Yes| SetReady
    CheckState -->|No| SetNotReady
    
    SetReady --> Setup
    Setup --> ProcessQueue
    
    PropChange --> UpdateState
    UpdateState --> CheckState
    
    style SetReady fill:#f9f9f9
    style Setup fill:#f9f9f9
```

The CSM monitoring ensures that SPDM discovery doesn't begin until the MCTP infrastructure is fully initialized. The `ccsmChange` match monitors the property `State` on the interface `xyz.openbmc_project.State.FeatureReady` at path `/xyz/openbmc_project/state/configurableStateManager/MCTP`. When the state becomes `xyz.openbmc_project.State.FeatureReady.States.Enabled`, discovery proceeds.

**Sources:** [spdmd/mctp_endpoint_discovery.cpp:87-115](), [spdmd/mctp_endpoint_discovery.cpp:1133-1185]()

---

## Property Extraction Methods

The discovery handlers extract multiple properties from the D-Bus `InterfaceMap` to construct `ResponderArgs` for creating responder instances.

### Property Extraction Overview

| Property | Method | D-Bus Interface | D-Bus Property | Type |
|----------|--------|----------------|----------------|------|
| EID | `getEid()` | `xyz.openbmc_project.MCTP.Endpoint` | `EID` | `uint8_t` or `uint32_t` |
| UUID | `getUUID()` | `xyz.openbmc_project.MCTP.UUID` or `xyz.openbmc_project.Common.UUID` | `UUID` | `std::string` |
| Medium Type | `getMediumType()` | `xyz.openbmc_project.MCTP.Endpoint` | `MediumType` | `std::string` |
| Binding Type | `getBindingType()` | `xyz.openbmc_project.MCTP.Binding` | `BindingType` | `std::string` |
| Transport Socket | `getTransportSocket()` | `xyz.openbmc_project.Common.UnixSocket` | `Address` | `std::vector<uint8_t>` |

### EID Extraction Logic

The `getEid()` method handles both `uint8_t` and `uint32_t` EID types and validates SPDM support:

```mermaid
graph TB
    Start["getEid(interfaces)"]
    FindIntf["Find mctpEndpointIntfName"]
    
    CheckIntf{Interface found?}
    FindEID["Find EID property"]
    FindTypes["Find SupportedMessageTypes"]
    
    CheckTypes{Both properties<br/>exist?}
    
    ExtractEID["Extract EID value<br/>(try uint32_t, then uint8_t)"]
    ValidateEID{EID < 0xFF?}
    
    CheckSPDM["Check if SPDM (type 5)<br/>in SupportedMessageTypes"]
    ValidSPDM{SPDM supported?}
    
    ReturnEID["Return EidType with value"]
    ReturnNull["Return std::nullopt"]
    
    Start --> FindIntf
    FindIntf --> CheckIntf
    CheckIntf -->|No| ReturnNull
    CheckIntf -->|Yes| FindEID
    FindEID --> FindTypes
    FindTypes --> CheckTypes
    CheckTypes -->|No| ReturnNull
    CheckTypes -->|Yes| ExtractEID
    
    ExtractEID --> ValidateEID
    ValidateEID -->|No| ReturnNull
    ValidateEID -->|Yes| CheckSPDM
    CheckSPDM --> ValidSPDM
    ValidSPDM -->|No| ReturnNull
    ValidSPDM -->|Yes| ReturnEID
```

The EID extraction uses `std::variant<uint32_t, uint8_t>` to accommodate different MCTP control daemon implementations. The constant `mctpTypeSPDM = 5` is used to filter endpoints that support SPDM messages.

**Sources:** [spdmd/mctp_endpoint_discovery.cpp:629-726](), [spdmd/mctp_endpoint_discovery.hpp:117]()

---

## Asynchronous Property Resolution

Several property extraction operations require asynchronous D-Bus method calls to resolve cross-references between MCTP objects and inventory items.

### Inventory Path Resolution

```mermaid
graph TB
    Start["getInventoryPathAsync(uuid)"]
    GetSubTree["ObjectMapper.GetSubTree<br/>for SPDMResponder interface"]
    
    ProcessResp["Process response map"]
    BuildCandidates["Build candidates list<br/>(objectPath, serviceName, interface)"]
    
    CheckEmpty{candidates.empty()?}
    ReturnEmpty["callback(empty path)"]
    
    IterCandidates["Iterate candidates"]
    GetProp["getPropertyValueAsync<br/>Get UUID property"]
    
    CheckMatch{UUID matches?}
    ReturnPath["callback(objectPath)"]
    NextCandidate["Next candidate"]
    
    AllChecked{All checked?}
    
    Start --> GetSubTree
    GetSubTree --> ProcessResp
    ProcessResp --> BuildCandidates
    BuildCandidates --> CheckEmpty
    
    CheckEmpty -->|Yes| ReturnEmpty
    CheckEmpty -->|No| IterCandidates
    
    IterCandidates --> GetProp
    GetProp --> CheckMatch
    CheckMatch -->|Yes| ReturnPath
    CheckMatch -->|No| NextCandidate
    NextCandidate --> AllChecked
    AllChecked -->|No| GetProp
    AllChecked -->|Yes| ReturnEmpty
```

The `getInventoryPathAsync()` method searches the inventory tree for objects implementing `xyz.openbmc_project.Inventory.Item.SPDMResponder` and matching the provided UUID. It uses the ObjectMapper service to discover candidates and then queries each candidate's UUID property until a match is found.

**Sources:** [spdmd/mctp_endpoint_discovery.cpp:923-1057]()

### MCTP Object Resolution

```mermaid
graph TB
    Start["getMCTPObjectAsync(uuid)"]
    CheckServices{mctpControlServices<br/>empty?}
    ReturnEmpty1["callback(Object{})"]
    
    SetupCounters["Setup shared counters<br/>sharedCount, found"]
    
    LoopServices["For each MCTP control service"]
    GetManaged["GetManagedObjects()"]
    
    CheckFound1{found == true?}
    Return1["return early"]
    
    CheckError{error?}
    IncrCount1["++sharedCount"]
    CheckLast1{count == total<br/>&& !found?}
    ReturnEmpty2["callback(Object{})"]
    
    ParseTree["Parse ObjectValueTree"]
    IterObjects["Iterate objects"]
    CompareUUID{UUID matches?}
    
    SetFound["found = true"]
    ReturnObj["callback(Object)"]
    
    Continue["Continue iteration"]
    IncrCount2["++sharedCount"]
    CheckLast2{count == total<br/>&& !found?}
    ReturnEmpty3["callback(Object{})"]
    
    Start --> CheckServices
    CheckServices -->|Yes| ReturnEmpty1
    CheckServices -->|No| SetupCounters
    SetupCounters --> LoopServices
    LoopServices --> GetManaged
    GetManaged --> CheckFound1
    CheckFound1 -->|Yes| Return1
    CheckFound1 -->|No| CheckError
    
    CheckError -->|Yes| IncrCount1
    IncrCount1 --> CheckLast1
    CheckLast1 -->|Yes| ReturnEmpty2
    
    CheckError -->|No| ParseTree
    ParseTree --> IterObjects
    IterObjects --> CompareUUID
    CompareUUID -->|Yes| SetFound
    SetFound --> ReturnObj
    CompareUUID -->|No| Continue
    Continue --> IncrCount2
    IncrCount2 --> CheckLast2
    CheckLast2 -->|Yes| ReturnEmpty3
```

The `getMCTPObjectAsync()` method queries all registered MCTP control services in parallel using shared atomic counters to track completion. When a UUID match is found in any service, the callback is invoked immediately with the matching object.

**Sources:** [spdmd/mctp_endpoint_discovery.cpp:852-921]()

---

## MCTP Service Discovery

Before processing endpoint signals, the discovery system must identify available MCTP control services.

### MCTP Service Setup Flow

```mermaid
graph TB
    Start["setupMCTPServices()"]
    CheckReady{ccsmReady?}
    Return["return"]
    
    GetServices["getMCTPServicesAsync()"]
    Callback["Callback with service names"]
    
    CheckEmpty{svcNames.empty()?}
    LogError["Log error"]
    
    IterServices["For each service name"]
    CheckExists{Service already<br/>in mctpControlServices?}
    Skip["continue to next"]
    
    CreateHelper["Create ServiceHelper"]
    Store["Store in mctpControlServices map"]
    
    GetManaged["async_method_call<br/>GetManagedObjects"]
    ProcessObjs["For each object"]
    CallNewObj["mctpNewObjectSignal()"]
    
    Start --> CheckReady
    CheckReady -->|No| Return
    CheckReady -->|Yes| GetServices
    GetServices --> Callback
    Callback --> CheckEmpty
    CheckEmpty -->|Yes| LogError
    CheckEmpty -->|No| IterServices
    
    IterServices --> CheckExists
    CheckExists -->|Yes| Skip
    CheckExists -->|No| CreateHelper
    CreateHelper --> Store
    Store --> GetManaged
    GetManaged --> ProcessObjs
    ProcessObjs --> CallNewObj
```

The `getMCTPServicesAsync()` method queries the ObjectMapper at `/xyz/openbmc_project/object_mapper` using the `GetSubTree` method to find all services implementing the `xyz.openbmc_project.MCTP.Endpoint` interface. Each discovered service is wrapped in a `dbus::ServiceHelper` and stored in the `mctpControlServices` map for future queries.

**Sources:** [spdmd/mctp_endpoint_discovery.cpp:118-193](), [spdmd/mctp_endpoint_discovery.cpp:195-257]()

---

## Signal Queue Management

When CSM is not ready but signals arrive, they are queued for later processing.

### Inventory Signal Queuing

The `inventorySignalQueue` is a `std::deque` that stores `(objectPath, InterfaceMap)` pairs:

```mermaid
graph LR
    Signal["InterfacesAdded signal"]
    Check{ccsmReady?}
    Process["inventoryNewObjectSignal()"]
    Queue["inventorySignalQueue.emplace_back()"]
    
    CSMReady["CSM becomes ready"]
    Loop["while (!queue.empty())"]
    PopFront["queue.front()"]
    ProcessQueued["inventoryNewObjectSignal()"]
    PopQueue["queue.pop_front()"]
    
    Signal --> Check
    Check -->|Yes| Process
    Check -->|No| Queue
    
    CSMReady --> Loop
    Loop --> PopFront
    PopFront --> ProcessQueued
    ProcessQueued --> PopQueue
    PopQueue --> Loop
```

When CSM transitions to ready state (either in `initCsmStatus()` or via the `ccsmChange` signal), all queued inventory signals are processed in FIFO order.

**Sources:** [spdmd/mctp_endpoint_discovery.cpp:58-66](), [spdmd/mctp_endpoint_discovery.cpp:104-111](), [spdmd/mctp_endpoint_discovery.cpp:1154-1161]()

---

## Error Handling and Validation

Each property extraction method includes robust error handling for missing interfaces, malformed properties, and type mismatches.

### Common Error Patterns

| Scenario | Validation | Action |
|----------|-----------|--------|
| Missing interface | `interfaces.find() == end()` | Return empty/nullopt |
| Missing property | `properties.contains()` check | Return empty/nullopt |
| Type mismatch | `std::get_if<T>()` returns nullptr | Return empty/nullopt |
| Invalid EID | `eid >= invalidEid (0xFF)` | Log error, return nullopt |
| Empty UUID | `uuid.empty()` | Log error, skip processing |
| SPDM not supported | SPDM type not in `SupportedMessageTypes` | Return nullopt |

The `tryConnectMCTP()` method wraps socket connection attempts in a try-catch block. If the connection fails, the exception is re-thrown to crash the application rather than silently failing, ensuring MCTP connectivity issues are immediately visible.

**Sources:** [spdmd/mctp_endpoint_discovery.cpp:259-275](), [spdmd/mctp_endpoint_discovery.cpp:311-317](), [spdmd/mctp_endpoint_discovery.cpp:394-399]()

---

