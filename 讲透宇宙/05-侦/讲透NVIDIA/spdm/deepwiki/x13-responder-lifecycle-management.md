<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/spdm · extra page Responder Lifecycle Management · fetched 2026-10-26 -->

# Responder Lifecycle Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [spdmd/spdmd.cpp](spdmd/spdmd.cpp)
- [spdmd/spdmd_app.hpp](spdmd/spdmd_app.hpp)

</details>



## Purpose and Scope

This page documents how the `spdmd` daemon manages the lifecycle of SPDM responder objects, from initial discovery through creation, priority-based replacement, and EID-based indexing. The lifecycle management ensures that the daemon maintains one active `Responder` object per discovered SPDM device, selecting the highest-priority transport path when multiple MCTP connections exist to the same device.

For information about how responders are discovered via MCTP and inventory correlation, see [MCTP Endpoint Discovery](#3.3). For details about the `Responder` class's D-Bus interfaces and SPDM protocol operations, see [D-Bus Responder Interface](#3.2).

---

## Lifecycle Overview

The responder lifecycle consists of four main stages:

| Stage | Trigger | Action | Key Method |
|-------|---------|--------|-----------|
| **Discovery** | MCTP endpoint or inventory signal | UUID and transport parameters recorded | `discoveryUpdateResponder()` |
| **Priority Evaluation** | New transport path discovered | Compare medium/binding priorities | `needRecreateResponder()` |
| **Creation/Recreation** | First discovery or higher priority path | Instantiate `Responder` object | `createResponder()` |
| **Initialization** | After creation | Optional serial number and measurements | `autoMeasure()` |

```mermaid
stateDiagram-v2
    [*] --> Discovery: "InterfacesAdded signal"
    Discovery --> UUIDCheck: "Extract UUID and transport params"
    
    UUIDCheck --> FirstDiscovery: "UUID not in resp_discovery"
    UUIDCheck --> ExistingDiscovery: "UUID already exists"
    
    FirstDiscovery --> CreateResponder: "Store in resp_discovery"
    
    ExistingDiscovery --> PriorityCheck: "needRecreateResponder()"
    PriorityCheck --> KeepExisting: "New priority <= current"
    PriorityCheck --> RecreateResponder: "New priority > current"
    
    RecreateResponder --> DestroyOld: "responders[eid].reset()"
    DestroyOld --> UpdateDiscovery: "Update resp_discovery"
    UpdateDiscovery --> CreateResponder
    
    CreateResponder --> ConstructPath: "Build D-Bus path"
    ConstructPath --> InstantiateObject: "new Responder(...)"
    InstantiateObject --> InitialMeasurement: "Optional autoMeasure()"
    InitialMeasurement --> [*]: "Ready for operations"
    
    KeepExisting --> [*]: "No action needed"
```

**Diagram: Responder Lifecycle State Machine**

Sources: [spdmd/spdmd.cpp:294-387]()

---

## Discovery and UUID Tracking

The daemon maintains two primary data structures for managing responder lifecycle:

| Data Structure | Type | Purpose | Key |
|----------------|------|---------|-----|
| `resp_discovery` | `std::map<std::string, ResponderArgs>` | Tracks discovered devices by UUID | Device UUID |
| `responders` | `std::vector<std::shared_ptr<Responder>>` | Active responder objects | EID (index) |

The `resp_discovery` map serves as the source of truth for which transport path is currently selected for each device, while `responders` provides EID-based access for packet routing.

```mermaid
graph TB
    subgraph "Discovery Phase"
        SIGNAL["InterfacesAdded Signal"]
        EXTRACT["Extract ResponderArgs<br/>- uuid<br/>- eid<br/>- medium<br/>- bindingType<br/>- inventoryPath<br/>- mctpPath<br/>- socketPath"]
    end
    
    subgraph "UUID Tracking: resp_discovery map"
        MAP["std::map<string, ResponderArgs>"]
        KEY1["UUID: '123e4567-...'"]
        VAL1["ResponderArgs{<br/>eid=5,<br/>medium='PCIe',<br/>...}"]
        KEY2["UUID: '789abcde-...'"]
        VAL2["ResponderArgs{<br/>eid=7,<br/>medium='SMBus',<br/>...}"]
    end
    
    subgraph "EID Indexing: responders vector"
        VEC["std::vector<shared_ptr<Responder>>"]
        IDX0["[0] nullptr"]
        IDX5["[5] Responder*"]
        IDX7["[7] Responder*"]
        IDX_N["[n] ..."]
    end
    
    SIGNAL --> EXTRACT
    EXTRACT --> MAP
    MAP --> KEY1 --> VAL1
    MAP --> KEY2 --> VAL2
    
    VAL1 -.->|"eid=5"| IDX5
    VAL2 -.->|"eid=7"| IDX7
    
    VEC --> IDX0
    VEC --> IDX5
    VEC --> IDX7
    VEC --> IDX_N
```

**Diagram: Discovery Data Structures**

The `discoveryUpdateResponder()` method is the entry point for all lifecycle management:

```mermaid
sequenceDiagram
    participant Discovery as MctpDiscovery
    participant App as SpdmdApp
    participant RespMap as resp_discovery map
    participant RespVec as responders vector
    
    Discovery->>App: discoveryUpdateResponder(respArg)
    App->>RespMap: find(respArg.uuid)
    
    alt UUID not found
        App->>App: reportNotice("Create first responder")
        App->>RespMap: emplace(uuid, respArg)
        App->>App: createResponder(respArg)
        App->>RespVec: responders[eid] = new Responder
    else UUID exists
        App->>App: needRecreateResponder(current, new)
        alt Higher priority
            App->>App: reportNotice("Recreate responder")
            App->>RespVec: responders[old_eid].reset()
            App->>RespMap: erase(uuid)
            App->>RespMap: emplace(uuid, new_respArg)
            App->>App: createResponder(new_respArg)
            App->>RespVec: responders[eid] = new Responder
        else Lower/equal priority
            App->>App: reportNotice("Lower priority, not creating")
        end
    end
```

**Diagram: discoveryUpdateResponder() Flow**

Sources: [spdmd/spdmd.cpp:294-334](), [spdmd/spdmd_app.hpp:166-169]()

---

## Priority-Based Selection Mechanism

When multiple transport paths connect to the same device (identified by UUID), the daemon selects the highest-priority path using a two-tier priority system:

### Priority Tables

The daemon uses two static priority maps defined in [spdmd/spdmd_app.hpp:54-73]():

**Medium Type Priorities (Primary):**
```
PCIe   = 0 (highest)
USB    = 1
SPI    = 2
I3C    = 3
KCS    = 4
Serial = 5
SMBus  = 6 (lowest)
```

**Binding Type Priorities (Secondary):**
```
PCIe   = 0 (highest)
USB    = 1
SPI    = 2
I3C    = 3
KCS    = 4
Serial = 5
SMBus  = 6 (lowest)
```

These priorities are based on expected bandwidth characteristics, with PCIe providing the highest throughput and lowest latency.

### Priority Comparison Algorithm

The `needRecreateResponder()` method implements the priority comparison logic:

```mermaid
graph TD
    START["needRecreateResponder(currMedium, newMedium,<br/>currBinding, newBinding)"]
    LOOKUP_CURR["Lookup currMediumPriority"]
    LOOKUP_NEW["Lookup newMediumPriority"]
    
    CHECK_FOUND{"Both priorities<br/>found in map?"}
    LOG_ERROR["Log error:<br/>'priority not found'"]
    RETURN_FALSE1["return false"]
    
    COMPARE_MEDIUM{"newMediumPriority <<br/>currMediumPriority?"}
    RETURN_TRUE1["return true<br/>(recreate)"]
    
    EQUAL_MEDIUM{"Medium priorities<br/>equal?"}
    LOOKUP_BINDING["Lookup binding priorities"]
    
    CHECK_BINDING_FOUND{"Both binding<br/>priorities found?"}
    LOG_ERROR2["Log error:<br/>'binding priority not found'"]
    RETURN_FALSE2["return false"]
    
    COMPARE_BINDING{"newBindingPriority <=<br/>currBindingPriority?"}
    RETURN_TRUE2["return true<br/>(recreate)"]
    RETURN_FALSE3["return false<br/>(keep existing)"]
    
    START --> LOOKUP_CURR
    LOOKUP_CURR --> LOOKUP_NEW
    LOOKUP_NEW --> CHECK_FOUND
    
    CHECK_FOUND -->|No| LOG_ERROR
    LOG_ERROR --> RETURN_FALSE1
    
    CHECK_FOUND -->|Yes| COMPARE_MEDIUM
    COMPARE_MEDIUM -->|Yes| RETURN_TRUE1
    COMPARE_MEDIUM -->|No| EQUAL_MEDIUM
    
    EQUAL_MEDIUM -->|Yes| LOOKUP_BINDING
    EQUAL_MEDIUM -->|No| RETURN_FALSE3
    
    LOOKUP_BINDING --> CHECK_BINDING_FOUND
    CHECK_BINDING_FOUND -->|No| LOG_ERROR2
    LOG_ERROR2 --> RETURN_FALSE2
    
    CHECK_BINDING_FOUND -->|Yes| COMPARE_BINDING
    COMPARE_BINDING -->|Yes| RETURN_TRUE2
    COMPARE_BINDING -->|No| RETURN_FALSE3
```

**Diagram: needRecreateResponder() Decision Logic**

### Priority Evaluation Examples

| Current | New | Decision | Reason |
|---------|-----|----------|--------|
| PCIe/PCIe (0/0) | USB/USB (1/1) | Keep existing | Lower medium priority |
| SMBus/SMBus (6/6) | PCIe/PCIe (0/0) | Recreate | Higher medium priority |
| PCIe/PCIe (0/0) | PCIe/USB (0/1) | Keep existing | Same medium, lower binding priority |
| PCIe/USB (0/1) | PCIe/PCIe (0/0) | Recreate | Same medium, higher binding priority |
| USB/SMBus (1/6) | USB/SMBus (1/6) | Recreate | Equal priority (inventory recreated) |

The last case (equal priority) triggers recreation to refresh the responder when inventory objects are recreated, as noted in [spdmd/spdmd.cpp:288-291]().

Sources: [spdmd/spdmd.cpp:225-292](), [spdmd/spdmd_app.hpp:54-73](), [spdmd/spdmd_app.hpp:128-151]()

---

## Responder Creation Process

The `createResponder()` method instantiates a new `Responder` object and registers it in the `responders` vector:

### EID-Based Array Sizing

The `responders` vector is dynamically resized to accommodate the EID:

```cpp
if (args.eid >= responders.size())
{
    responders.resize(args.eid + 1);
}
```

This ensures EID-based indexing works correctly, with sparse arrays for non-contiguous EIDs. Entries for unused EIDs remain as `nullptr`.

### D-Bus Object Path Construction

The D-Bus object path is constructed from the inventory path:

```
/xyz/openbmc_project/SPDM/{inventory_filename}
```

For example, if `inventoryPath = /xyz/openbmc_project/inventory/system/chassis/GPU0`, the SPDM object path becomes `/xyz/openbmc_project/SPDM/GPU0`. If the inventory path is empty (during local testing), the EID is used as a fallback.

### Responder Instantiation

```mermaid
graph LR
    START["createResponder(args)"]
    RESIZE["Resize responders vector<br/>if needed"]
    PATH["Construct D-Bus path<br/>from inventoryPath"]
    CHECK_MEDIUM{"args.medium<br/>not empty?"}
    INSTANTIATE["responders[eid] =<br/>new Responder(*this, path, eid,<br/>mctpPath, inventoryPath,<br/>medium, bindingType, socketPath)"]
    ERROR["Log error:<br/>'Unable to determine<br/>responder type'"]
    SERIAL["refreshSerialNumber()<br/>(if FETCH_SERIALNUMBER)"]
    AUTO["autoMeasure(eid)<br/>(if configured)"]
    END["Return"]
    
    START --> RESIZE
    RESIZE --> PATH
    PATH --> CHECK_MEDIUM
    CHECK_MEDIUM -->|Yes| INSTANTIATE
    CHECK_MEDIUM -->|No| ERROR
    INSTANTIATE --> SERIAL
    SERIAL --> AUTO
    AUTO --> END
    ERROR --> END
```

**Diagram: createResponder() Execution Flow**

The `Responder` constructor receives:
- `*this` - Reference to `SpdmdApp` for context access
- `path` - D-Bus object path
- `eid` - MCTP Endpoint ID
- `mctpPath` - D-Bus path to MCTP endpoint object
- `inventoryPath` - D-Bus path to inventory object
- `medium` - Transport medium type (e.g., "xyz.openbmc_project.MCTP.Endpoint.MediaTypes.PCIe")
- `bindingType` - MCTP binding type
- `socketPath` - Unix socket path (for non-kernel MCTP)

Sources: [spdmd/spdmd.cpp:336-387]()

---

## EID-Based Indexing and Packet Routing

The `responders` vector provides O(1) lookup for routing incoming MCTP packets to the correct responder:

```mermaid
sequenceDiagram
    participant MCTP as MCTP Socket
    participant App as SpdmdApp::mctpCallback()
    participant Peek as MctpTransportClass::peekEid()
    participant Vec as responders vector
    participant Resp as Responder[eid]
    
    MCTP->>App: EPOLLIN event
    App->>App: mctpIo.read(packetBuffer)
    App->>Peek: peekEid(packetBuffer)
    Peek-->>App: eid = 5
    
    App->>App: Check eid < responders.size()
    App->>Vec: responders[5]
    
    alt responders[5] != nullptr
        Vec-->>Resp: Get shared_ptr
        App->>Resp: handleEvent(EventReceiveClass)
        Resp->>Resp: Process packet
    else responders[5] == nullptr
        App->>App: Log error:<br/>"received message from EID=5<br/>while responder not created"
    end
```

**Diagram: EID-Based Packet Routing**

The `mctpCallback()` method extracts the EID from the packet header using `MctpTransportClass::peekEid()`, then dispatches the packet to the appropriate responder. If the EID is out of bounds or the responder slot is `nullptr`, the packet is logged and dropped.

Sources: [spdmd/spdmd.cpp:423-486]()

---

## Automatic Initialization

After a responder is created, two optional initialization steps may occur:

### Serial Number Retrieval

If the `FETCH_SERIALNUMBER_FROM_RESPONDER` compile-time option is enabled and set to a non-zero measurement index, the daemon automatically requests that measurement to populate the serial number property:

```cpp
#if FETCH_SERIALNUMBER_FROM_RESPONDER != 0
    responders[args.eid]->refreshSerialNumber();
#endif
```

This is implemented at [spdmd/spdmd.cpp:383-385]().

### Automatic Measurements

The `autoMeasure()` method is called immediately after responder creation if:
1. The `--cached_measurements` CLI option is enabled
2. The measurement delay has expired (or is zero)
3. The EID matches the configured filter (or "all" is specified)

```mermaid
graph TD
    CREATE["createResponder(args)"]
    AUTO["autoMeasure(eid)"]
    SHOULD{"shouldMeasureEID(eid)?"}
    DELAY{"measureOnDiscoveryActive?"}
    FILTER{"cachedMeasurements.empty() OR<br/>eid in cachedMeasurements?"}
    REFRESH["responders[eid]->refresh(0, {}, {}, 0)"]
    SKIP["Skip automatic measurement"]
    
    CREATE --> AUTO
    AUTO --> SHOULD
    SHOULD --> DELAY
    DELAY -->|No| SKIP
    DELAY -->|Yes| FILTER
    FILTER -->|No| SKIP
    FILTER -->|Yes| REFRESH
```

**Diagram: Automatic Measurement Decision Logic**

The measurement delay is controlled by the `--cached_measurements_delay` option (default 60 seconds) and uses a `boost::asio::steady_timer` to trigger `measurementDelayCallback()`, which sets `measureOnDiscoveryActive = true` and calls `autoMeasure()` for all existing responders.

Sources: [spdmd/spdmd.cpp:386-387](), [spdmd/spdmd.cpp:500-509](), [spdmd/spdmd.cpp:389-421](), [spdmd/spdmd.cpp:488-498]()

---

## Responder Destruction

When a responder is recreated due to a higher-priority transport path, the old responder is destroyed by resetting its `shared_ptr`:

```cpp
responders[it->second.eid].reset();
```

This occurs at [spdmd/spdmd.cpp:317](). The `Responder` destructor automatically:
1. Closes the D-Bus interfaces
2. Cancels any pending timers
3. Releases the `ConnectionClass` and associated transport resources

The EID slot in the vector becomes `nullptr`, ready for a new responder to be assigned.

---

## Key Data Structures Summary

| Structure | Location | Type | Purpose |
|-----------|----------|------|---------|
| `resp_discovery` | `SpdmdApp` | `std::map<std::string, ResponderArgs>` | UUID-indexed discovery state |
| `responders` | `SpdmdApp` | `std::vector<std::shared_ptr<Responder>>` | EID-indexed active responders |
| `mediumPriority` | `spdmd_app.hpp` | `std::unordered_map<std::string, int>` | MCTP medium priority mapping |
| `bindingPriority` | `spdmd_app.hpp` | `std::unordered_map<std::string, int>` | MCTP binding priority mapping |
| `ResponderArgs` | `dbus_impl_responder.hpp` | struct | Discovery parameters (uuid, eid, paths, etc.) |

Sources: [spdmd/spdmd_app.hpp:166-169](), [spdmd/spdmd_app.hpp:54-73]()

---

