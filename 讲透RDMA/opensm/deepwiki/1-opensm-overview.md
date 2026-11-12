<!-- source: DeepWiki mcp.deepwiki.com · repo linux-rdma/opensm · page 1 OpenSM Overview · fetched 2026-11-11 -->

# OpenSM Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [include/iba/ib_types.h](include/iba/ib_types.h)
- [include/opensm/osm_base.h](include/opensm/osm_base.h)
- [include/opensm/osm_helper.h](include/opensm/osm_helper.h)
- [include/opensm/osm_opensm.h](include/opensm/osm_opensm.h)
- [include/opensm/osm_subnet.h](include/opensm/osm_subnet.h)
- [man/opensm.8.in](man/opensm.8.in)
- [opensm/main.c](opensm/main.c)
- [opensm/osm_console.c](opensm/osm_console.c)
- [opensm/osm_opensm.c](opensm/osm_opensm.c)
- [opensm/osm_sa_class_port_info.c](opensm/osm_sa_class_port_info.c)
- [opensm/osm_state_mgr.c](opensm/osm_state_mgr.c)
- [opensm/osm_subnet.c](opensm/osm_subnet.c)

</details>



## Purpose and Scope

OpenSM is an InfiniBand compliant Subnet Manager (SM) and Subnet Administration (SA) implementation that runs on top of OpenIB. This document provides an architectural overview of the OpenSM codebase, including its core components, data structures, and system interactions.

OpenSM serves as the central control entity for InfiniBand fabrics, responsible for subnet initialization, topology discovery, routing configuration, and ongoing fabric management. At least one SM instance must be running per InfiniBand subnet to initialize and manage the hardware.

For detailed information about specific subsystems, see:
- Core architecture and initialization: [Core Architecture](#2)
- Network discovery and topology management: [Network Discovery and Topology](#3) 
- Routing algorithms and forwarding tables: [Routing Management](#4)
- Client query handling: [Subnet Administration (SA)](#5)
- Configuration and deployment: [Configuration and Deployment](#8)

## OpenSM System Architecture

OpenSM follows a modular architecture centered around the main `osm_opensm_t` controller object, which coordinates specialized management components and routing engines.

```mermaid
graph TB
    subgraph "Application Layer"
        MAIN["main()"]
        CLI["Command Line Interface"]
        CONSOLE["osm_console_t<br/>Management Console"]
    end
    
    subgraph "OpenSM Core Controller"
        OPENSM["osm_opensm_t<br/>Main OpenSM Object"]
        CONFIG["Configuration<br/>osm_subn_opt_t"]
    end
    
    subgraph "Subnet Management Core"
        SUBNET["osm_subn_t<br/>Subnet State & Topology"]
        SM["osm_sm_t<br/>Subnet Manager"]
        SA["osm_sa_t<br/>Subnet Administration"]
        STATE_MGR["State Manager<br/>SM State Machine"]
    end
    
    subgraph "Specialized Managers"
        LID_MGR["osm_lid_mgr_t<br/>LID Assignment"]
        UCAST_MGR["osm_ucast_mgr_t<br/>Unicast Routing"]
        MCAST_MGR["osm_mcast_mgr_t<br/>Multicast Management"]
        PKEY_MGR["osm_pkey_mgr_t<br/>Partition Management"]
        PERFMGR["osm_perfmgr_t<br/>Performance Manager"]
        QOS_MGR["QoS Manager"]
    end
    
    subgraph "Routing Engine Layer"
        ROUTING_IF["Routing Engine Interface"]
        MINHOP["Min Hop Engine"]
        UPDN["Up/Down Engine"] 
        FTREE["Fat-Tree Engine"]
        LASH["LASH Engine"]
        TORUS["Torus-2QoS Engine"]
    end
    
    subgraph "Network Communication Layer"
        VENDOR["osm_vendor_t<br/>Vendor Abstraction"]
        MAD_POOL["osm_mad_pool_t<br/>MAD Memory Management"]
        VL15["osm_vl15intf_t<br/>VL15 Interface"]
    end
    
    subgraph "InfiniBand Hardware Layer"
        UMAD["UMAD Kernel Interface"]
        HW["InfiniBand HCAs & Switches"]
    end
    
    MAIN --> OPENSM
    CLI --> CONFIG
    OPENSM --> SUBNET
    OPENSM --> SM
    OPENSM --> SA
    OPENSM --> CONSOLE
    OPENSM --> PERFMGR
    
    SM --> STATE_MGR
    SM --> LID_MGR
    SM --> UCAST_MGR
    SM --> MCAST_MGR
    SM --> PKEY_MGR
    SM --> QOS_MGR
    
    UCAST_MGR --> ROUTING_IF
    ROUTING_IF --> MINHOP
    ROUTING_IF --> UPDN
    ROUTING_IF --> FTREE
    ROUTING_IF --> LASH
    ROUTING_IF --> TORUS
    
    OPENSM --> VENDOR
    VENDOR --> MAD_POOL
    VENDOR --> VL15
    VL15 --> UMAD
    UMAD --> HW
```

Sources: [opensm/main.c:1-700](), [include/opensm/osm_opensm.h:246-280](), [opensm/osm_opensm.c:1-300]()

## Core Data Structures and State Management

The `osm_subn_t` structure serves as the central repository for all subnet state information, containing topology maps, configuration options, and runtime data.

```mermaid
graph TB
    subgraph "Central Subnet State (osm_subn_t)"
        SUBN_CORE["osm_subn_t<br/>Core Subnet Object"]
        
        subgraph "Configuration"
            SUBN_OPT["osm_subn_opt_t<br/>Configuration Options"]
            QOS_OPT["QoS Options"]
            CC_OPT["Congestion Control Options"]
        end
        
        subgraph "Topology Data Structures"
            NODE_TBL["node_guid_tbl<br/>cl_qmap_t<br/>Node Objects by GUID"]
            PORT_TBL["port_guid_tbl<br/>cl_qmap_t<br/>Port Objects by GUID"] 
            SW_TBL["sw_guid_tbl<br/>cl_qmap_t<br/>Switch Objects by GUID"]
            LID_TBL["port_lid_tbl<br/>cl_ptr_vector_t<br/>Port Objects by LID"]
        end
        
        subgraph "Multicast & Partition Data"
            MGRP_TBL["mgrp_mgid_tbl<br/>cl_qmap_t<br/>Multicast Groups"]
            PRTN_TBL["prtn_pkey_tbl<br/>cl_qmap_t<br/>Partition Objects"]
        end
        
        subgraph "SA Records & Services"
            SA_INFR["sa_infr_list<br/>cl_qlist_t<br/>InformInfo Records"]
            SA_SR["sa_sr_list<br/>cl_qlist_t<br/>Service Records"]
            ALIAS_TBL["alias_port_guid_tbl<br/>cl_qmap_t<br/>Alias GUID Objects"]
        end
        
        subgraph "Remote SM Management"
            SM_TBL["sm_guid_tbl<br/>cl_qmap_t<br/>Remote SM Objects"]
        end
    end
    
    SUBN_CORE --> SUBN_OPT
    SUBN_CORE --> NODE_TBL
    SUBN_CORE --> PORT_TBL
    SUBN_CORE --> SW_TBL
    SUBN_CORE --> LID_TBL
    SUBN_CORE --> MGRP_TBL
    SUBN_CORE --> PRTN_TBL
    SUBN_CORE --> SA_INFR
    SUBN_CORE --> SA_SR
    SUBN_CORE --> ALIAS_TBL
    SUBN_CORE --> SM_TBL
```

Sources: [include/opensm/osm_subnet.h:1100-1400](), [opensm/osm_subnet.c:1-500]()

## Initialization and Runtime Flow

OpenSM follows a structured initialization and operational flow, transitioning through well-defined SM states during subnet discovery and configuration.

```mermaid
graph LR
    subgraph "Initialization Phase"
        START["main()"]
        PARSE_ARGS["Parse Arguments<br/>& Configuration"]
        INIT_OSM["osm_opensm_init()"]
        BIND_PORT["Bind to IB Port"]
    end
    
    subgraph "SM State Machine"
        DISCOVERING["IB_SMINFO_STATE_DISCOVERING<br/>Topology Discovery"]
        STANDBY["IB_SMINFO_STATE_STANDBY<br/>Waiting for Master"]
        MASTER["IB_SMINFO_STATE_MASTER<br/>Active Management"]
        NOTACTIVE["IB_SMINFO_STATE_NOTACTIVE<br/>Inactive"]
    end
    
    subgraph "Master SM Operations"
        HEAVY_SWEEP["Heavy Sweep<br/>state_mgr_sweep_hop_0()"]
        LIGHT_SWEEP["Light Sweep<br/>state_mgr_light_sweep_start()"]
        ROUTE_CALC["Routing Calculation<br/>osm_ucast_mgr_process()"]
        SA_SERVICE["SA Query Service<br/>osm_sa_t processing"]
    end
    
    subgraph "Runtime Management"
        TRAP_HANDLING["Trap Processing<br/>Network Events"]
        PERF_MGR["Performance Monitoring<br/>osm_perfmgr_t"]
        CONSOLE_MGT["Console Management<br/>osm_console_t"]
    end
    
    START --> PARSE_ARGS
    PARSE_ARGS --> INIT_OSM
    INIT_OSM --> BIND_PORT
    BIND_PORT --> DISCOVERING
    
    DISCOVERING --> STANDBY
    DISCOVERING --> MASTER
    STANDBY --> MASTER
    MASTER --> STANDBY
    MASTER --> NOTACTIVE
    
    MASTER --> HEAVY_SWEEP
    MASTER --> LIGHT_SWEEP
    MASTER --> ROUTE_CALC
    MASTER --> SA_SERVICE
    
    MASTER --> TRAP_HANDLING
    MASTER --> PERF_MGR
    MASTER --> CONSOLE_MGT
```

Sources: [opensm/main.c:600-1000](), [opensm/osm_state_mgr.c:82-300](), [opensm/osm_opensm.c:400-800]()

## InfiniBand Communication Stack

OpenSM communicates with the InfiniBand fabric through a layered communication stack that abstracts hardware-specific details while providing MAD (Management Datagram) processing capabilities.

```mermaid
graph TB
    subgraph "OpenSM Application Layer"
        SM_COMP["SM Components<br/>osm_sm_t, osm_sa_t"]
        MGRS["Specialized Managers<br/>LID, Routing, Multicast"]
    end
    
    subgraph "MAD Processing Layer"
        MAD_CTRL["MAD Controllers<br/>osm_sm_mad_ctrl_t<br/>osm_sa_mad_ctrl_t"]
        DISP["cl_dispatcher_t<br/>Message Dispatcher"]
        MAD_POOL["osm_mad_pool_t<br/>MAD Memory Pool"]
    end
    
    subgraph "VL15 Management Layer"
        VL15_IF["osm_vl15intf_t<br/>VL15 Interface Manager"]
        VL15_POLLER["VL15 Poller Thread"]
    end
    
    subgraph "Vendor Abstraction Layer"
        VENDOR_API["osm_vendor_t<br/>Vendor Interface"]
        BIND_MGT["Port Binding Management"]
    end
    
    subgraph "UMAD Interface Layer"
        UMAD_LIB["UMAD User Library<br/>umad_*() functions"]
        UMAD_SEND["umad_send()"]
        UMAD_RECV["umad_recv()"]
    end
    
    subgraph "Kernel Space"
        UMAD_KERN["UMAD Kernel Driver"]
        IB_DRIVERS["InfiniBand Kernel Drivers"]
    end
    
    subgraph "Hardware Layer"
        HCA["Host Channel Adapters"]
        SWITCHES["InfiniBand Switches"]
    end
    
    SM_COMP --> MAD_CTRL
    MGRS --> MAD_CTRL
    MAD_CTRL --> DISP
    MAD_CTRL --> MAD_POOL
    
    DISP --> VL15_IF
    MAD_POOL --> VL15_IF
    VL15_IF --> VL15_POLLER
    
    VL15_IF --> VENDOR_API
    VL15_POLLER --> VENDOR_API
    VENDOR_API --> BIND_MGT
    
    VENDOR_API --> UMAD_LIB
    UMAD_LIB --> UMAD_SEND
    UMAD_LIB --> UMAD_RECV
    
    UMAD_SEND --> UMAD_KERN
    UMAD_RECV --> UMAD_KERN
    UMAD_KERN --> IB_DRIVERS
    
    IB_DRIVERS --> HCA
    IB_DRIVERS --> SWITCHES
```

Sources: [include/opensm/osm_opensm.h:300-350](), [opensm/osm_vl15intf.c:1-200](), [vendor/osm_vendor_ibumad.c:1-300]()

## Routing Engine Architecture

OpenSM supports multiple routing algorithms through a pluggable routing engine interface, allowing selection of different routing strategies based on fabric topology and requirements.

```mermaid
graph TB
    subgraph "Routing Engine Interface"
        RE_IF["osm_routing_engine_t<br/>Common Interface"]
        RE_SETUP["setup() callback"]
        RE_BUILD["ucast_build_fwd_tables()"]
        RE_MATRICES["build_lid_matrices()"]
        RE_DESTROY["destroy() callback"]
    end
    
    subgraph "Built-in Routing Engines"
        MINHOP_RE["Min Hop Routing<br/>osm_ucast_minhop_setup()"]
        UPDN_RE["Up/Down Routing<br/>osm_ucast_updn_setup()"]
        FTREE_RE["Fat-Tree Routing<br/>osm_ucast_ftree_setup()"]
        LASH_RE["LASH Routing<br/>osm_ucast_lash_setup()"]
        TORUS_RE["Torus-2QoS Routing<br/>osm_ucast_torus2QoS_setup()"]
        FILE_RE["File-based Routing<br/>osm_ucast_file_setup()"]
        NUE_RE["Nue Routing<br/>osm_ucast_nue_setup()"]
        SSSP_RE["SSSP Routing<br/>osm_ucast_sssp_setup()"]
    end
    
    subgraph "External Routing Support"
        EXT_IF["external_routing_engine_module_t"]
        EXT_REG["osm_register_external_routing_engine()"]
    end
    
    subgraph "Routing Manager"
        UCAST_MGR["osm_ucast_mgr_t<br/>Unicast Manager"]
        ROUTE_CALC["Route Calculation Logic"]
        LFT_BUILD["Linear Forwarding Table Build"]
    end
    
    RE_IF --> RE_SETUP
    RE_IF --> RE_BUILD
    RE_IF --> RE_MATRICES
    RE_IF --> RE_DESTROY
    
    RE_IF --> MINHOP_RE
    RE_IF --> UPDN_RE
    RE_IF --> FTREE_RE
    RE_IF --> LASH_RE
    RE_IF --> TORUS_RE
    RE_IF --> FILE_RE
    RE_IF --> NUE_RE
    RE_IF --> SSSP_RE
    
    EXT_IF --> EXT_REG
    EXT_REG --> RE_IF
    
    UCAST_MGR --> ROUTE_CALC
    ROUTE_CALC --> RE_IF
    ROUTE_CALC --> LFT_BUILD
```

Sources: [include/opensm/osm_opensm.h:120-180](), [opensm/osm_opensm.c:72-200](), [opensm/osm_ucast_mgr.c:1-500]()

## Management and Configuration Interface

OpenSM provides multiple interfaces for configuration and runtime management, including configuration files, command-line options, and an interactive console.

| Interface Type | Component | Configuration Scope | Runtime Control |
|---|---|---|---|
| Command Line | `main.c` argument parsing | Initial configuration | Limited |
| Configuration File | `osm_subn_opt_t` loading | Complete configuration | Config reload |
| Interactive Console | `osm_console_t` | Runtime parameters | Full management |
| Performance Manager | `osm_perfmgr_t` | Performance monitoring | Statistics & control |
| Event Plugins | `osm_event_plugin_t` | Event handling | Custom extensions |

**Key Configuration Components:**

- **`osm_subn_opt_t`**: Central configuration structure containing all tunable parameters
- **`osm_console_t`**: Interactive management console with telnet/local access
- **`osm_perfmgr_t`**: Performance monitoring and statistics collection
- **Event Plugin Interface**: Extensibility for custom management logic

Sources: [opensm/main.c:129-600](), [include/opensm/osm_subnet.h:248-392](), [opensm/osm_console.c:60-150](), [opensm/osm_perfmgr.c:1-200]()

---

