<!-- source: DeepWiki mcp.deepwiki.com · repo linux-rdma/opensm · page 2 Core Architecture · fetched 2026-11-11 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [include/opensm/osm_opensm.h](include/opensm/osm_opensm.h)
- [include/opensm/osm_subnet.h](include/opensm/osm_subnet.h)
- [man/opensm.8.in](man/opensm.8.in)
- [opensm/main.c](opensm/main.c)
- [opensm/osm_opensm.c](opensm/osm_opensm.c)
- [opensm/osm_state_mgr.c](opensm/osm_state_mgr.c)
- [opensm/osm_subnet.c](opensm/osm_subnet.c)

</details>



This document describes the fundamental architecture of OpenSM, focusing on the main system components, their relationships, and the initialization flow. It covers the central data structures, the main controller object, and how the various subsystems integrate together.

For information about specific subnet management functions, see [State Management](#2.2). For details about network discovery processes, see [Network Discovery and Topology](#3). For routing-specific architecture, see [Routing Management](#4).

## Overview

OpenSM's core architecture is built around a central controller object (`osm_opensm_t`) that coordinates multiple specialized subsystems. The architecture follows a layered approach with clear separation between the main controller, subnet state management, specialized managers, and the underlying network communication layer.

## Main Controller Architecture

```mermaid
graph TB
    subgraph "Application Entry"
        MAIN["main()<br/>Command Line Processing"]
    end
    
    subgraph "Core Controller (osm_opensm_t)"
        OSM["osm_opensm_t<br/>Main Controller Object"]
        CONSTRUCT["osm_opensm_construct()"]
        INIT["osm_opensm_init()"]
        INIT_FINISH["osm_opensm_init_finish()"]
        
        MAIN --> CONSTRUCT
        CONSTRUCT --> INIT
        INIT --> INIT_FINISH
        INIT_FINISH --> OSM
    end
    
    subgraph "Core Subsystems"
        SUBN["osm_subn_t<br/>Subnet State"]
        SM["osm_sm_t<br/>State Manager"]
        SA["osm_sa_t<br/>Subnet Admin"]
        DB["osm_db_t<br/>Persistent Storage"]
        LOG["osm_log_t<br/>Logging System"]
        
        OSM --> SUBN
        OSM --> SM
        OSM --> SA
        OSM --> DB
        OSM --> LOG
    end
    
    subgraph "Infrastructure"
        VENDOR["osm_vendor_t<br/>Hardware Abstraction"]
        MADPOOL["osm_mad_pool_t<br/>MAD Memory Pool"]
        VL15["osm_vl15_t<br/>VL15 Interface"]
        DISP["cl_dispatcher_t<br/>Message Dispatcher"]
        
        OSM --> VENDOR
        OSM --> MADPOOL
        OSM --> VL15
        OSM --> DISP
    end
```

**OpenSM Main Controller Structure**

The `osm_opensm_t` structure serves as the central coordination point for all OpenSM functionality. It contains all major subsystems and provides the top-level interface for system operations.

Sources: [include/opensm/osm_opensm.h:246-274](), [opensm/osm_opensm.c:566-574](), [opensm/main.c:1-50]()

## Central Data Structures

```mermaid
graph TB
    subgraph "osm_opensm_t - Main Controller"
        OSM_VERSION["const char *osm_version"]
        SUBN_OBJ["osm_subn_t subn"]
        SM_OBJ["osm_sm_t sm"]
        SA_OBJ["osm_sa_t sa"]
        DB_OBJ["osm_db_t db"]
        VENDOR_PTR["osm_vendor_t *p_vendor"]
        LOG_OBJ["osm_log_t log"]
        LOCK["cl_plock_t lock"]
        ROUTING["routing_engine_list"]
    end
    
    subgraph "osm_subn_t - Subnet State"
        OSM_PTR["struct osm_opensm *p_osm"]
        SW_TBL["cl_qmap_t sw_guid_tbl"]
        NODE_TBL["cl_qmap_t node_guid_tbl"]
        PORT_TBL["cl_qmap_t port_guid_tbl"]
        ALIAS_TBL["cl_qmap_t alias_port_guid_tbl"]
        PRTN_TBL["cl_qmap_t prtn_pkey_tbl"]
        SM_TBL["cl_qmap_t sm_guid_tbl"]
        PORT_LID_TBL["cl_ptr_vector_t port_lid_tbl"]
        OPTIONS["osm_subn_opt_t opt"]
    end
    
    subgraph "osm_subn_opt_t - Configuration"
        GUID["ib_net64_t guid"]
        SUBNET_PREFIX["ib_net64_t subnet_prefix"]
        SM_KEY["ib_net64_t sm_key"]
        SWEEP_INTERVAL["uint32_t sweep_interval"]
        ROUTING_ENGINE["char *routing_engine_names"]
        LOG_FILE["char *log_file"]
        PRIORITY["uint8_t sm_priority"]
        LMC["uint8_t lmc"]
    end
    
    SUBN_OBJ --> SW_TBL
    SUBN_OBJ --> NODE_TBL
    SUBN_OBJ --> PORT_TBL
    SUBN_OBJ --> OPTIONS
    OPTIONS --> GUID
    OPTIONS --> ROUTING_ENGINE
    OSM_PTR --> OSM_VERSION
```

**Core Data Structure Relationships**

The architecture centers around three main data structures that hold the complete system state and configuration.

Sources: [include/opensm/osm_opensm.h:246-274](), [include/opensm/osm_subnet.h:777-814](), [include/opensm/osm_subnet.h:248-392]()

## Initialization Flow

```mermaid
sequenceDiagram
    participant Main as "main()"
    participant OSM as "osm_opensm_t"
    participant Subn as "osm_subn_t"
    participant SM as "osm_sm_t"
    participant SA as "osm_sa_t"
    participant Vendor as "osm_vendor_t"
    
    Main->>OSM: osm_opensm_construct()
    Note over OSM: Initialize basic structure
    
    Main->>OSM: osm_opensm_init(p_opt)
    OSM->>OSM: cl_plock_init()
    OSM->>OSM: cl_disp_init()
    OSM->>Subn: osm_subn_init()
    OSM->>Vendor: osm_vendor_new()
    
    Main->>OSM: osm_opensm_init_finish()
    OSM->>OSM: osm_opensm_construct_finish()
    OSM->>OSM: osm_mad_pool_init()
    OSM->>OSM: osm_vl15_init()
    OSM->>SM: osm_sm_init()
    OSM->>SA: osm_sa_init()
    OSM->>OSM: setup_routing_engines()
    
    Main->>OSM: osm_opensm_bind(guid)
    OSM->>SM: osm_sm_bind()
    OSM->>SA: osm_sa_bind()
    
    Note over OSM: System ready for operation
```

**OpenSM Initialization Sequence**

The initialization process follows a carefully orchestrated sequence to ensure all dependencies are satisfied before the system becomes operational.

Sources: [opensm/main.c:441-486](), [opensm/osm_opensm.c:724-806](), [opensm/osm_opensm.c:808-870]()

## State Management Architecture

The state management system coordinates subnet discovery, configuration, and monitoring through a centralized state machine and specialized managers.

```mermaid
graph TB
    subgraph "State Management Core"
        STATE_MGR["osm_sm_t<br/>State Manager"]
        SWEEP_ENGINE["Sweep Engine"]
        STATE_MACHINE["SM State Machine"]
        
        STATE_MGR --> SWEEP_ENGINE
        STATE_MGR --> STATE_MACHINE
    end
    
    subgraph "Discovery & Monitoring"
        HEAVY_SWEEP["Heavy Sweep<br/>state_mgr_sweep_hop_0()"]
        LIGHT_SWEEP["Light Sweep<br/>state_mgr_light_sweep_start()"]
        NODE_DISCOVERY["Node Discovery"]
        PORT_DISCOVERY["Port Discovery"]
        
        SWEEP_ENGINE --> HEAVY_SWEEP
        SWEEP_ENGINE --> LIGHT_SWEEP
        HEAVY_SWEEP --> NODE_DISCOVERY
        HEAVY_SWEEP --> PORT_DISCOVERY
    end
    
    subgraph "Configuration Managers"
        LID_MGR["LID Manager<br/>osm_lid_mgr_process()"]
        ROUTING_MGR["Routing Manager<br/>osm_ucast_mgr_process()"]
        MCAST_MGR["Multicast Manager<br/>osm_mcast_mgr_process()"]
        PKEY_MGR["Partition Manager<br/>osm_pkey_mgr_process()"]
        
        STATE_MACHINE --> LID_MGR
        STATE_MACHINE --> ROUTING_MGR
        STATE_MACHINE --> MCAST_MGR
        STATE_MACHINE --> PKEY_MGR
    end
    
    subgraph "Subnet State"
        SUBNET_STATE["osm_subn_t<br/>Central State Repository"]
        NODE_TABLES["Node/Port/Switch Tables"]
        ROUTING_TABLES["Routing & Forwarding Tables"]
        
        SUBNET_STATE --> NODE_TABLES
        SUBNET_STATE --> ROUTING_TABLES
        
        LID_MGR --> SUBNET_STATE
        ROUTING_MGR --> SUBNET_STATE
        NODE_DISCOVERY --> SUBNET_STATE
    end
```

**State Management System Architecture**

The state management system orchestrates all subnet management activities through a coordinated set of specialized managers that operate on the central subnet state.

Sources: [opensm/osm_state_mgr.c:82-95](), [opensm/osm_state_mgr.c:210-270](), [opensm/osm_state_mgr.c:790-862]()

## Message Processing Architecture

OpenSM uses a sophisticated message processing system to handle InfiniBand Management Datagrams (MADs) and coordinate responses across multiple subsystems.

```mermaid
graph LR
    subgraph "Network Layer"
        FABRIC["InfiniBand Fabric"]
        UMAD["UMAD Interface"]
        VENDOR_LAYER["osm_vendor_t<br/>Vendor Abstraction"]
    end
    
    subgraph "MAD Processing"
        MAD_POOL["osm_mad_pool_t<br/>MAD Memory Pool"]
        VL15_INTF["osm_vl15_t<br/>VL15 Interface"]
        DISPATCHER["cl_dispatcher_t<br/>Message Dispatcher"]
    end
    
    subgraph "Message Handlers"
        SM_MAD_CTRL["SM MAD Controller"]
        SA_MAD_CTRL["SA MAD Controller"]
        NODE_INFO_RCV["Node Info Receiver"]
        PORT_INFO_RCV["Port Info Receiver"]
        TRAP_RCV["Trap Receiver"]
    end
    
    subgraph "Processing Logic"
        SM_ENGINE["State Manager"]
        SA_ENGINE["Subnet Admin"]
        ROUTING_ENGINE["Routing Engines"]
    end
    
    FABRIC --> UMAD
    UMAD --> VENDOR_LAYER
    VENDOR_LAYER --> MAD_POOL
    MAD_POOL --> VL15_INTF
    VL15_INTF --> DISPATCHER
    
    DISPATCHER --> SM_MAD_CTRL
    DISPATCHER --> SA_MAD_CTRL
    SM_MAD_CTRL --> NODE_INFO_RCV
    SM_MAD_CTRL --> PORT_INFO_RCV
    SM_MAD_CTRL --> TRAP_RCV
    
    NODE_INFO_RCV --> SM_ENGINE
    PORT_INFO_RCV --> SM_ENGINE
    SA_MAD_CTRL --> SA_ENGINE
    SM_ENGINE --> ROUTING_ENGINE
```

**Message Processing Flow**

The message processing architecture provides a scalable framework for handling high-volume MAD traffic while maintaining proper sequencing and state consistency.

Sources: [opensm/osm_opensm.c:817-827](), [include/opensm/osm_opensm.h:258-266](), [opensm/osm_state_mgr.c:162-204]()

## Configuration System

The configuration system manages both runtime options and persistent state across OpenSM restarts.

| Component | Purpose | Key Data Structures |
|-----------|---------|-------------------|
| **Command Line Parsing** | Process startup arguments | `main()` argument processing |
| **Configuration Options** | Store runtime settings | `osm_subn_opt_t` |
| **Persistent Database** | Store state across restarts | `osm_db_t`, guid2lid, neighbors |
| **Option Validation** | Validate and apply settings | Option parsing functions |

**Configuration Management Components**

The configuration system ensures consistent settings across restarts and provides validation for all user-configurable parameters.

Sources: [opensm/main.c:129-439](), [include/opensm/osm_subnet.h:248-392](), [opensm/osm_subnet.c:762-928]()

## Threading and Concurrency Model

OpenSM employs a sophisticated threading model to handle concurrent operations while maintaining data consistency.

```mermaid
graph TB
    subgraph "Main Thread"
        MAIN_THREAD["Main Thread<br/>Initialization & Control"]
        SIGNAL_HANDLER["Signal Handlers<br/>SIGINT, SIGHUP, SIGUSR1"]
    end
    
    subgraph "Dispatcher Threads"
        MAIN_DISP["Main Dispatcher<br/>cl_dispatcher_t disp"]
        SA_SET_DISP["SA Set Dispatcher<br/>cl_dispatcher_t sa_set_disp"]
        WORKER_THREADS["Worker Thread Pool"]
        
        MAIN_DISP --> WORKER_THREADS
        SA_SET_DISP --> WORKER_THREADS
    end
    
    subgraph "Specialized Threads"
        SM_SWEEPER["SM Sweeper Thread"]
        VL15_THREAD["VL15 Processing Thread"]
        PERFMGR_THREAD["Performance Manager Thread"]
        CONSOLE_THREAD["Console Interface Thread"]
    end
    
    subgraph "Synchronization"
        MAIN_LOCK["cl_plock_t lock<br/>Main System Lock"]
        SM_LOCK["SM State Lock"]
        SUBNET_LOCK["Subnet Data Lock"]
    end
    
    MAIN_THREAD --> MAIN_DISP
    MAIN_THREAD --> SA_SET_DISP
    MAIN_THREAD --> SM_SWEEPER
    
    WORKER_THREADS -.-> MAIN_LOCK
    SM_SWEEPER -.-> SM_LOCK
    WORKER_THREADS -.-> SUBNET_LOCK
    
    SIGNAL_HANDLER --> MAIN_THREAD
```

**OpenSM Threading Architecture**

The threading model provides scalable processing while maintaining strict consistency through carefully designed locking strategies.

Sources: [opensm/main.c:96-127](), [opensm/osm_opensm.c:764-787](), [include/opensm/osm_opensm.h:266]()

This core architecture provides the foundation for all OpenSM operations, ensuring reliable subnet management through well-defined component boundaries and clear data flow patterns.

---

