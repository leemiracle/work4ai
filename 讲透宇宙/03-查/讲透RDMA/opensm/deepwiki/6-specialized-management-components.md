<!-- source: DeepWiki mcp.deepwiki.com · repo linux-rdma/opensm · page 6 Specialized Management Components · fetched 2026-11-11 -->

# Specialized Management Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [doc/partition-config.txt](doc/partition-config.txt)
- [include/opensm/osm_madw.h](include/opensm/osm_madw.h)
- [include/opensm/osm_partition.h](include/opensm/osm_partition.h)
- [include/opensm/osm_perfmgr.h](include/opensm/osm_perfmgr.h)
- [include/opensm/osm_perfmgr_db.h](include/opensm/osm_perfmgr_db.h)
- [include/opensm/osm_pkey.h](include/opensm/osm_pkey.h)
- [include/opensm/osm_sm.h](include/opensm/osm_sm.h)
- [opensm/osm_perfmgr.c](opensm/osm_perfmgr.c)
- [opensm/osm_perfmgr_db.c](opensm/osm_perfmgr_db.c)
- [opensm/osm_pkey.c](opensm/osm_pkey.c)
- [opensm/osm_pkey_mgr.c](opensm/osm_pkey_mgr.c)
- [opensm/osm_prtn.c](opensm/osm_prtn.c)
- [opensm/osm_prtn_config.c](opensm/osm_prtn_config.c)
- [opensm/osm_qos.c](opensm/osm_qos.c)
- [opensm/osm_req.c](opensm/osm_req.c)
- [opensm/osm_sm.c](opensm/osm_sm.c)
- [opensm/osm_sm_state_mgr.c](opensm/osm_sm_state_mgr.c)

</details>



This document covers the specialized management components in OpenSM that handle specific aspects of subnet management beyond basic fabric discovery and routing. These components focus on performance monitoring, partition management, and quality of service configuration.

For information about the core subnet management functionality, see [Core Architecture](#2). For routing-specific components, see [Routing Management](#4). For subnet administration queries, see [Subnet Administration (SA)](#5).

## Overview

OpenSM employs several specialized management components that operate alongside the core subnet manager to provide advanced fabric management capabilities. These components are coordinated by the main SM state machine but maintain their own specialized logic and data structures.

**Specialized Management Components Architecture**
```mermaid
graph TB
    subgraph "SM Core"
        SM["osm_sm_t<br/>State Manager"]
        SWEEP["SM Sweep Process"]
    end
    
    subgraph "Specialized Managers"
        PERFMGR["osm_perfmgr_t<br/>Performance Manager"]
        PKEY_MGR["osm_pkey_mgr_t<br/>Partition Manager"]
        QOS_MGR["QoS Manager"]
    end
    
    subgraph "Supporting Components"
        PERFDB["perfmgr_db_t<br/>Performance Database"]
        PRTN["osm_prtn_t<br/>Partition Objects"]
        PKEY_TBL["osm_pkey_tbl_t<br/>P_Key Tables"]
    end
    
    SM --> PERFMGR
    SM --> PKEY_MGR
    SM --> QOS_MGR
    
    PERFMGR --> PERFDB
    PKEY_MGR --> PRTN
    PKEY_MGR --> PKEY_TBL
    
    SWEEP -.-> PERFMGR
    SWEEP -.-> PKEY_MGR
    SWEEP -.-> QOS_MGR
```

Sources: [opensm/osm_perfmgr.h:133-161](), [opensm/osm_pkey_mgr.c:810-906](), [opensm/osm_qos.c:451-564]()

## Performance Manager

The Performance Manager (`osm_perfmgr_t`) provides fabric health monitoring and performance statistics collection. It operates as a separate subsystem that periodically queries port counters and maintains historical performance data.

**Performance Manager Structure**
```mermaid
graph TB
    subgraph "Performance Manager Core"
        PERFMGR["osm_perfmgr_t<br/>Main Controller"]
        TIMER["sweep_timer<br/>Periodic Sweep Timer"]
        STATE["sweep_state<br/>SLEEP/ACTIVE/SUSPENDED"]
    end
    
    subgraph "Data Collection"
        MONITORED["monitored_map<br/>cl_qmap_t"]
        MON_NODE["monitored_node_t<br/>Node Tracking"]
        MON_PORT["monitored_port_t<br/>Port Tracking"]
    end
    
    subgraph "Database Storage"
        PERFDB["perfmgr_db_t<br/>Performance Database"]
        DB_NODE["db_node_t<br/>Node Records"]
        DB_PORT["db_port_t<br/>Port Records"]
    end
    
    subgraph "MAD Processing"
        BIND["bind_handle<br/>Vendor Binding"]
        MAD_POOL["mad_pool<br/>MAD Memory Pool"]
        QUERIES["outstanding_queries<br/>Query Throttling"]
    end
    
    PERFMGR --> TIMER
    PERFMGR --> STATE
    PERFMGR --> MONITORED
    PERFMGR --> PERFDB
    PERFMGR --> BIND
    
    MONITORED --> MON_NODE
    MON_NODE --> MON_PORT
    
    PERFDB --> DB_NODE
    DB_NODE --> DB_PORT
    
    BIND --> MAD_POOL
    BIND --> QUERIES
```

The Performance Manager operates through several key phases:

### Discovery and Monitoring Setup
The Performance Manager discovers nodes to monitor during SM sweeps by examining the subnet's node table and building a map of monitored nodes.

Key functions:
- `collect_guids()` - Builds the monitored node map from subnet discovery
- `osm_perfmgr_bind()` - Establishes MAD communication binding
- `perfmgr_query_counters()` - Executes periodic counter queries

### Counter Collection and Processing
The manager sends periodic `PortCounters` and `PortCountersExtended` MADs to collect performance data:

- **Port Counters**: Basic error and data counters
- **Port Counters Extended**: Extended 64-bit counters for high-speed links
- **Class Port Info**: Capability and redirection information

### Database Management
Performance data is stored in a specialized database (`perfmgr_db_t`) that maintains:
- Current and previous counter readings
- Error rate calculations
- Data throughput statistics
- Historical trends

Sources: [opensm/osm_perfmgr.c:1048-1129](), [opensm/osm_perfmgr.h:133-161](), [opensm/osm_perfmgr_db.c:58-87]()

## Partition Management

Partition management in OpenSM handles P_Key (Partition Key) distribution and partition membership control. This system ensures proper isolation between different user groups or applications sharing the InfiniBand fabric.

**Partition Management Architecture**
```mermaid
graph TB
    subgraph "Partition Manager"
        PKEY_MGR["osm_pkey_mgr_process()<br/>Main Processing"]
        PRTN_MAKE["osm_prtn_make_partitions()<br/>Partition Creation"]
    end
    
    subgraph "Partition Objects"
        PRTN_MAP["prtn_pkey_tbl<br/>Partition Map"]
        PRTN_OBJ["osm_prtn_t<br/>Partition Object"]
        FULL_TBL["full_guid_tbl<br/>Full Members"]
        PART_TBL["part_guid_tbl<br/>Limited Members"]
    end
    
    subgraph "P_Key Tables"
        PKEY_TBL["osm_pkey_tbl_t<br/>Port P_Key Table"]
        PENDING["pending<br/>Pending P_Keys"]
        BLOCKS["blocks<br/>P_Key Blocks"]
        ACCUM["accum_pkeys<br/>Accumulated P_Keys"]
    end
    
    subgraph "Configuration"
        CONFIG["Partition Config File"]
        PARSER["osm_prtn_config_parse_file()"]
    end
    
    PKEY_MGR --> PRTN_MAKE
    PRTN_MAKE --> PRTN_MAP
    PRTN_MAP --> PRTN_OBJ
    PRTN_OBJ --> FULL_TBL
    PRTN_OBJ --> PART_TBL
    
    PKEY_MGR --> PKEY_TBL
    PKEY_TBL --> PENDING
    PKEY_TBL --> BLOCKS
    PKEY_TBL --> ACCUM
    
    CONFIG --> PARSER
    PARSER --> PRTN_OBJ
```

### Partition Configuration Processing
The partition manager processes configuration from multiple sources:
1. **Configuration File**: `partitions.conf` parsed by `osm_prtn_config_parse_file()`
2. **Default Partition**: Automatically created with P_Key `0x7fff`
3. **Dynamic Creation**: Partitions created programmatically

### P_Key Distribution Process
The distribution process follows these steps:

1. **Partition Table Processing**: `pkey_mgr_process_partition_table()` iterates through each partition's member lists
2. **Pending P_Key Management**: `pkey_mgr_process_physical_port()` adds P_Keys to port pending lists
3. **P_Key Table Updates**: `pkey_mgr_update_port()` calculates final P_Key table layouts
4. **MAD Transmission**: P_Key table blocks sent via `pkey_mgr_update_pkey_entry()`

### Enforcement and Switch Configuration
For switch ports connected to end nodes, the manager:
- Copies P_Key tables to switch external ports
- Configures partition enforcement in switch `PortInfo`
- Handles inter-switch links (no enforcement)

Sources: [opensm/osm_pkey_mgr.c:810-906](), [opensm/osm_prtn.c:67-90](), [opensm/osm_prtn_config.c:216-267]()

## Quality of Service (QoS) Management

The QoS Manager configures Virtual Lane (VL) arbitration and Service Level to Virtual Lane (SL2VL) mappings to provide differentiated service levels across the fabric.

**QoS Configuration Flow**
```mermaid
graph LR
    subgraph "QoS Setup Process"
        SETUP["osm_qos_setup()"]
        CONFIG["QoS Configuration"]
        BUILD["qos_build_config()"]
    end
    
    subgraph "Configuration Types"
        CA_CFG["ca_config<br/>Channel Adapter"]
        SW0_CFG["sw0_config<br/>Switch Port 0"]
        SWE_CFG["swe_config<br/>Switch External"]
        RTR_CFG["rtr_config<br/>Router"]
    end
    
    subgraph "QoS Components"
        VLARB["VL Arbitration Tables"]
        SL2VL["SL2VL Mapping Tables"]
        VL_LIMIT["vl_high_limit"]
    end
    
    subgraph "MAD Generation"
        MAD_LIST["qos_mad_list_t"]
        MAD_ITEM["qos_mad_item_t"]
        SEND["osm_send_req_mad()"]
    end
    
    SETUP --> CONFIG
    CONFIG --> BUILD
    BUILD --> CA_CFG
    BUILD --> SW0_CFG
    BUILD --> SWE_CFG
    BUILD --> RTR_CFG
    
    CA_CFG --> VLARB
    SW0_CFG --> VLARB
    SWE_CFG --> VLARB
    RTR_CFG --> VLARB
    
    VLARB --> MAD_LIST
    SL2VL --> MAD_LIST
    VL_LIMIT --> MAD_LIST
    
    MAD_LIST --> MAD_ITEM
    MAD_ITEM --> SEND
```

### VL Arbitration Configuration
VL arbitration tables control bandwidth allocation between Virtual Lanes:
- **High Priority Table**: `vlarb_high[]` - Time-critical traffic
- **Low Priority Table**: `vlarb_low[]` - Best-effort traffic
- **VL High Limit**: Boundary between high/low priority VLs

### SL2VL Mapping
Service Level to Virtual Lane mapping determines which VL carries traffic for each SL:
- **Standard Mapping**: Per-port SL2VL tables
- **Optimized Mapping**: Switch-wide SL2VL for compatible ports
- **Routing Integration**: Routing engines can customize SL2VL per path

### Configuration Processing
The QoS manager processes different node types:
- `qos_endport_setup()` - End ports (HCAs, routers)
- `qos_extports_setup()` - Switch external ports
- Optimized vs. non-optimized switch configurations

Sources: [opensm/osm_qos.c:451-564](), [opensm/osm_qos.c:202-255](), [opensm/osm_qos.c:301-419]()

## Integration with SM Core

The specialized managers integrate with the SM core through well-defined interfaces and are coordinated during SM sweeps and state transitions.

**SM Integration Points**
```mermaid
graph TB
    subgraph "SM Core Coordination"
        SM_PROCESS["osm_state_mgr_process()"]
        SWEEP["SM Sweep States"]
        SIGNAL["osm_sm_signal()"]
    end
    
    subgraph "Manager Invocation"
        PERF_SIGNAL["OSM_SIGNAL_PERFMGR_SWEEP"]
        PKEY_CALL["osm_pkey_mgr_process()"]
        QOS_CALL["osm_qos_setup()"]
    end
    
    subgraph "Execution Context"
        THREAD["SM Thread Context"]
        LOCK["SM Lock (plock)"]
        SUBNET["Subnet State Access"]
    end
    
    SM_PROCESS --> SWEEP
    SWEEP --> PKEY_CALL
    SWEEP --> QOS_CALL
    
    SIGNAL --> PERF_SIGNAL
    PERF_SIGNAL --> PERFMGR
    
    PKEY_CALL --> THREAD
    QOS_CALL --> THREAD
    PERFMGR --> THREAD
    
    THREAD --> LOCK
    LOCK --> SUBNET
```

### Execution Coordination
- **P_Key Manager**: Called during normal SM sweeps after topology discovery
- **QoS Manager**: Invoked during configuration phase of SM sweeps  
- **Performance Manager**: Operates on independent timer with separate thread signaling

### State Management
All managers respect SM state transitions:
- **MASTER State**: Full operation enabled
- **STANDBY State**: Limited or suspended operation
- **State Transitions**: Managers adapt to SM role changes

### Error Handling
Managers implement robust error handling:
- MAD transmission failures are logged and retried
- Database errors are contained within manager scope
- Configuration errors are reported but don't halt SM operation

Sources: [opensm/osm_sm.c:84-92](), [opensm/osm_sm_state_mgr.c:77-142](), [opensm/osm_perfmgr.c:1135-1141]()

---

