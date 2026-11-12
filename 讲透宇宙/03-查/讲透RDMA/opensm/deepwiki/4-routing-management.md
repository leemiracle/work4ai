<!-- source: DeepWiki mcp.deepwiki.com · repo linux-rdma/opensm · page 4 Routing Management · fetched 2026-11-11 -->

# Routing Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [include/opensm/osm_mcm_port.h](include/opensm/osm_mcm_port.h)
- [include/opensm/osm_multicast.h](include/opensm/osm_multicast.h)
- [include/opensm/osm_switch.h](include/opensm/osm_switch.h)
- [opensm/osm_drop_mgr.c](opensm/osm_drop_mgr.c)
- [opensm/osm_dump.c](opensm/osm_dump.c)
- [opensm/osm_mcast_mgr.c](opensm/osm_mcast_mgr.c)
- [opensm/osm_mcm_port.c](opensm/osm_mcm_port.c)
- [opensm/osm_multicast.c](opensm/osm_multicast.c)
- [opensm/osm_switch.c](opensm/osm_switch.c)
- [opensm/osm_ucast_mgr.c](opensm/osm_ucast_mgr.c)

</details>



## Purpose and Scope

This page provides a comprehensive overview of routing management in OpenSM, covering both unicast and multicast routing mechanisms. OpenSM's routing management is responsible for calculating and configuring forwarding tables in InfiniBand switches to establish optimal paths between all nodes in the subnet.

For detailed information about specific routing aspects, see:
- Unicast routing and LFT construction: [Unicast Routing](#4.1)
- Specific routing algorithms (FatTree, LASH, UpDn, Torus): [Routing Algorithms](#4.2)  
- Multicast group management and spanning tree construction: [Multicast Management](#4.3)

## Routing Management Architecture

OpenSM's routing management operates through a coordinated system of managers and engines that handle different aspects of path calculation and forwarding table configuration:

```mermaid
graph TB
    subgraph "Routing Control Flow"
        PROCESS["osm_ucast_mgr_process()"]
        SETUP["ucast_mgr_setup_all_switches()"]
        ROUTE["ucast_mgr_route()"]
        BUILD_LID["osm_ucast_mgr_build_lid_matrices()"]
        BUILD_LFT["ucast_mgr_build_lfts()"]
        SET_FWD["osm_ucast_mgr_set_fwd_tables()"]
    end
    
    subgraph "Routing Engines"
        ENGINE["osm_routing_engine"]
        MINHOP["MinHop Algorithm"]
        FTREE["FatTree Algorithm"]
        LASH["LASH Algorithm"]
        UPDN["UpDn Algorithm"]
        TORUS["Torus-2QoS Algorithm"]
        DOR["DOR Algorithm"]
    end
    
    subgraph "Switch Management"
        SWITCH["osm_switch_t"]
        LFT["Linear Forwarding Table"]
        NEW_LFT["new_lft[]"]
        HOPS["hops[][]"]
        MCAST_TBL["osm_mcast_tbl_t"]
    end
    
    subgraph "Multicast Management"
        MCAST_MGR["Multicast Manager"]
        MGRP_BOX["osm_mgrp_box_t"]
        MGRP["osm_mgrp_t"]
        MTREE["osm_mtree_node_t"]
    end
    
    PROCESS --> SETUP
    SETUP --> ROUTE
    ROUTE --> BUILD_LID
    BUILD_LID --> BUILD_LFT
    BUILD_LFT --> SET_FWD
    
    ROUTE --> ENGINE
    ENGINE --> MINHOP
    ENGINE --> FTREE
    ENGINE --> LASH
    ENGINE --> UPDN
    ENGINE --> TORUS
    ENGINE --> DOR
    
    BUILD_LFT --> SWITCH
    SWITCH --> LFT
    SWITCH --> NEW_LFT
    SWITCH --> HOPS
    SWITCH --> MCAST_TBL
    
    MCAST_MGR --> MGRP_BOX
    MGRP_BOX --> MGRP
    MGRP_BOX --> MTREE
```

Sources: [opensm/osm_ucast_mgr.c:1098-1153](), [opensm/osm_mcast_mgr.c:741-813](), [include/opensm/osm_switch.h:94-116]()

## Core Routing Components

### Unicast Manager (`osm_ucast_mgr_t`)

The unicast manager coordinates all unicast routing activities and serves as the central orchestrator for path calculation and forwarding table construction:

```mermaid
graph TB
    subgraph "Unicast Manager Structure"
        UCAST_MGR["osm_ucast_mgr_t"]
        SM_PTR["sm: osm_sm_t*"]
        SUBN_PTR["p_subn: osm_subn_t*"]
        LOG_PTR["p_log: osm_log_t*"]
        CACHE_VALID["cache_valid: boolean_t"]
        IS_DOR["is_dor: boolean_t"]
        MAX_LID["max_lid: uint16_t"]
        PORT_ORDER["port_order_list: cl_qlist_t"]
    end
    
    subgraph "Key Operations"
        PROCESS_FUNC["osm_ucast_mgr_process()"]
        BUILD_MATRICES["osm_ucast_mgr_build_lid_matrices()"]
        BUILD_LFTS["ucast_mgr_build_lfts()"]
        SET_FWD_TBLS["osm_ucast_mgr_set_fwd_tables()"]
        PROCESS_TBL["ucast_mgr_process_tbl()"]
        PROCESS_PORT["ucast_mgr_process_port()"]
    end
    
    subgraph "Switch Operations"
        RECOMMEND_PATH["osm_switch_recommend_path()"]
        SET_HOPS["osm_switch_set_hops()"]
        GET_LEAST_HOPS["osm_switch_get_least_hops()"]
        PREP_REBUILD["osm_switch_prepare_path_rebuild()"]
    end
    
    UCAST_MGR --> SM_PTR
    UCAST_MGR --> SUBN_PTR
    UCAST_MGR --> CACHE_VALID
    
    PROCESS_FUNC --> BUILD_MATRICES
    BUILD_MATRICES --> BUILD_LFTS
    BUILD_LFTS --> SET_FWD_TBLS
    
    BUILD_LFTS --> PROCESS_TBL
    PROCESS_TBL --> PROCESS_PORT
    PROCESS_PORT --> RECOMMEND_PATH
    
    BUILD_MATRICES --> SET_HOPS
    RECOMMEND_PATH --> GET_LEAST_HOPS
```

Sources: [opensm/osm_ucast_mgr.c:82-100](), [opensm/osm_ucast_mgr.c:596-675](), [opensm/osm_ucast_mgr.c:860-897]()

### Switch Routing State

Each InfiniBand switch maintains routing state through the `osm_switch_t` structure, which contains both current and calculated forwarding information:

| Component | Type | Purpose |
|-----------|------|---------|
| `lft` | `uint8_t*` | Current Linear Forwarding Table on switch |
| `new_lft` | `uint8_t*` | Newly calculated LFT to be programmed |
| `hops` | `uint8_t**` | Hop count matrix [lid][port] |
| `mcast_tbl` | `osm_mcast_tbl_t` | Multicast Forwarding Table |
| `p_prof` | `osm_port_profile_t*` | Port usage profiles for load balancing |
| `max_lid_ho` | `uint16_t` | Maximum LID accessible from this switch |

Sources: [include/opensm/osm_switch.h:94-116](), [opensm/osm_switch.c:604-663]()

## Routing Process Flow

The routing management process follows a structured sequence that builds hop count matrices, calculates optimal paths, and programs forwarding tables:

```mermaid
sequenceDiagram
    participant SM as "Subnet Manager"
    participant UMGR as "osm_ucast_mgr_t"
    participant ENGINE as "Routing Engine"
    participant SW as "osm_switch_t"
    
    SM->>UMGR: osm_ucast_mgr_process()
    UMGR->>SW: ucast_mgr_setup_all_switches()
    UMGR->>ENGINE: ucast_mgr_route()
    ENGINE->>UMGR: build_lid_matrices()
    
    loop For each switch
        UMGR->>SW: ucast_mgr_process_hop_0_1()
        UMGR->>SW: osm_switch_set_hops()
    end
    
    loop Until convergence
        UMGR->>SW: ucast_mgr_process_neighbors()
        SW->>SW: Update hop counts
    end
    
    ENGINE->>UMGR: ucast_build_fwd_tables()
    
    loop For each port
        UMGR->>SW: ucast_mgr_process_port()
        SW->>SW: osm_switch_recommend_path()
        SW->>SW: Update new_lft[]
    end
    
    UMGR->>SW: osm_ucast_mgr_set_fwd_tables()
    
    loop For each LFT block
        UMGR->>SW: set_lft_block()
    end
```

Sources: [opensm/osm_ucast_mgr.c:1098-1153](), [opensm/osm_ucast_mgr.c:1060-1096](), [opensm/osm_ucast_mgr.c:201-315]()

## Multicast Routing Integration

Multicast routing operates in parallel with unicast routing, managing multicast groups and constructing spanning trees for efficient multicast delivery:

```mermaid
graph LR
    subgraph "Multicast Groups"
        MBOX["osm_mgrp_box_t"]
        MGRP1["osm_mgrp_t (MGID1)"]
        MGRP2["osm_mgrp_t (MGID2)"]
        MLID["mlid: uint16_t"]
    end
    
    subgraph "Spanning Tree"
        ROOT["root: osm_mtree_node_t*"]
        SWITCH_NODES["Switch Nodes"]
        LEAF_PORTS["Leaf Ports"]
    end
    
    subgraph "Switch MFT"
        MFT["Multicast Forwarding Table"]
        MFT_BLOCKS["MFT Blocks"]
        PORT_MASK["Port Masks"]
    end
    
    MBOX --> MGRP1
    MBOX --> MGRP2
    MBOX --> MLID
    MBOX --> ROOT
    
    ROOT --> SWITCH_NODES
    SWITCH_NODES --> LEAF_PORTS
    
    ROOT --> MFT
    MFT --> MFT_BLOCKS
    MFT_BLOCKS --> PORT_MASK
```

Sources: [opensm/osm_mcast_mgr.c:741-813](), [include/opensm/osm_multicast.h:153-157](), [opensm/osm_multicast.c:118-148]()

## Path Recommendation Algorithm

The core path selection logic in `osm_switch_recommend_path()` considers multiple factors including hop counts, load balancing, and LMC (LID Mask Control) requirements:

| Factor | Implementation | Purpose |
|--------|----------------|---------|
| Least Hops | `osm_switch_get_least_hops()` | Minimize latency |
| Load Balancing | `osm_port_prof_path_count_get()` | Distribute traffic |
| LMC Support | Remote GUID tracking | Support multiple paths per destination |
| Port Health | `osm_physp_is_healthy()` | Avoid failed links |
| DOR Routing | `is_dor` flag | Dimension-ordered routing support |

Sources: [opensm/osm_switch.c:234-593](), [opensm/osm_ucast_mgr.c:201-315]()

## Routing Engine Interface

OpenSM supports multiple routing algorithms through a plugin-like routing engine interface. Each engine implements the standard interface while providing algorithm-specific optimizations:

```mermaid
graph TB
    subgraph "Routing Engine Interface"
        ENGINE_STRUCT["osm_routing_engine"]
        CONTEXT["context: void*"]
        BUILD_MATRICES["build_lid_matrices()"]
        BUILD_FWD_TABLES["ucast_build_fwd_tables()"]
        ENGINE_TYPE["type: osm_routing_engine_type_enum"]
    end
    
    subgraph "Algorithm Implementations"
        MINHOP_IMPL["osm_ucast_minhop_setup()"]
        DOR_IMPL["osm_ucast_dor_setup()"]
        EXTERNAL["External Algorithms"]
    end
    
    subgraph "Common Functions"
        BUILD_LID_COMMON["ucast_build_lid_matrices()"]
        BUILD_LFT_COMMON["ucast_build_lfts()"]
        BUILD_LFT_DOR["ucast_dor_build_lfts()"]
    end
    
    ENGINE_STRUCT --> CONTEXT
    ENGINE_STRUCT --> BUILD_MATRICES
    ENGINE_STRUCT --> BUILD_FWD_TABLES
    ENGINE_STRUCT --> ENGINE_TYPE
    
    BUILD_MATRICES --> BUILD_LID_COMMON
    BUILD_FWD_TABLES --> BUILD_LFT_COMMON
    BUILD_FWD_TABLES --> BUILD_LFT_DOR
    
    MINHOP_IMPL --> ENGINE_STRUCT
    DOR_IMPL --> ENGINE_STRUCT
    EXTERNAL --> ENGINE_STRUCT
```

Sources: [opensm/osm_ucast_mgr.c:1165-1191](), [opensm/osm_ucast_mgr.c:1155-1163](), [opensm/osm_ucast_mgr.c:1173-1183]()

---

