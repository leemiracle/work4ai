<!-- source: DeepWiki mcp.deepwiki.com · repo linux-rdma/opensm · page 3 Network Discovery and Topology · fetched 2026-11-11 -->

# Network Discovery and Topology

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [include/opensm/osm_node.h](include/opensm/osm_node.h)
- [include/opensm/osm_port.h](include/opensm/osm_port.h)
- [opensm/osm_lid_mgr.c](opensm/osm_lid_mgr.c)
- [opensm/osm_link_mgr.c](opensm/osm_link_mgr.c)
- [opensm/osm_node.c](opensm/osm_node.c)
- [opensm/osm_node_info_rcv.c](opensm/osm_node_info_rcv.c)
- [opensm/osm_port.c](opensm/osm_port.c)
- [opensm/osm_port_info_rcv.c](opensm/osm_port_info_rcv.c)
- [opensm/osm_sw_info_rcv.c](opensm/osm_sw_info_rcv.c)
- [opensm/osm_trap_rcv.c](opensm/osm_trap_rcv.c)

</details>



This document explains how OpenSM discovers the InfiniBand fabric topology, including the identification of nodes, ports, and links. The discovery process builds a complete representation of the subnet that enables proper subnet management and routing decisions.

For information about routing algorithms that operate on the discovered topology, see [Routing Algorithms](#4.2). For details about subnet administration services that query the discovered topology, see [Subnet Administration (SA)](#5).

## Discovery Process Overview

OpenSM uses a systematic approach to discover the InfiniBand fabric topology through Management Datagram (MAD) exchanges. The discovery process consists of several interconnected phases that build up the subnet representation:

```mermaid
flowchart TD
    START["Discovery Start"] --> INIT["Initialize SM Port"]
    INIT --> NODE_DISC["Node Discovery<br/>(NodeInfo MADs)"]
    NODE_DISC --> PORT_DISC["Port Discovery<br/>(PortInfo MADs)"]
    PORT_DISC --> LINK_DISC["Link Discovery<br/>(DR Path Extension)"]
    LINK_DISC --> TOPO_BUILD["Topology Building<br/>(osm_node_link)"]
    TOPO_BUILD --> LID_ASSIGN["LID Assignment<br/>(osm_lid_mgr)"]
    LID_ASSIGN --> CONFIG["Port Configuration"]
    CONFIG --> MONITOR["Ongoing Monitoring<br/>(Trap Processing)"]
    
    MONITOR --> CHANGE_DETECT["Change Detection"]
    CHANGE_DETECT --> RESWEEP["Force Resweep"]
    RESWEEP --> NODE_DISC
```

Sources: [opensm/osm_node_info_rcv.c:1-825](), [opensm/osm_port_info_rcv.c:1-826](), [opensm/osm_trap_rcv.c:1-701]()

## Node Discovery Process

Node discovery begins when OpenSM sends `NodeInfo` MADs to discover devices in the fabric. The `osm_ni_rcv_process` function handles responses and builds the node representation:

```mermaid
flowchart TD
    NI_REQ["NodeInfo Request<br/>(via DR path)"] --> NI_RESP["NodeInfo Response"]
    NI_RESP --> NI_VALIDATE["Validate Response<br/>(osm_ni_rcv_process)"]
    NI_VALIDATE --> NODE_CHECK{"Node Exists?"}
    
    NODE_CHECK -->|No| CREATE_NODE["Create New Node<br/>(osm_node_new)"]
    NODE_CHECK -->|Yes| UPDATE_NODE["Update Existing Node"]
    
    CREATE_NODE --> INIT_PHYSP["Initialize Physical Ports<br/>(osm_node_init_physp)"]
    UPDATE_NODE --> CHECK_LINKS["Check for Link Changes<br/>(ni_rcv_set_links)"]
    
    INIT_PHYSP --> ADD_TO_DB["Add to node_guid_tbl"]
    CHECK_LINKS --> LINK_UPDATE["Update Link Topology"]
    ADD_TO_DB --> REQ_PORTINFO["Request PortInfo<br/>(ni_rcv_get_port_info)"]
    LINK_UPDATE --> REQ_PORTINFO
    
    REQ_PORTINFO --> NEXT_DISCOVERY["Continue Discovery"]
```

Key functions in node discovery:

- `osm_ni_rcv_process()` - Main entry point for NodeInfo processing at [opensm/osm_node_info_rcv.c:821-825]()
- `ni_rcv_set_links()` - Establishes links between discovered nodes at [opensm/osm_node_info_rcv.c:141-312]()
- `osm_node_new()` - Creates new node objects at [opensm/osm_node.c:74-130]()

Sources: [opensm/osm_node_info_rcv.c:141-312](), [opensm/osm_node_info_rcv.c:821-825](), [opensm/osm_node.c:74-130]()

## Port Discovery and Configuration

Port discovery follows node discovery and involves querying `PortInfo` attributes for each physical port. The process differs based on the node type:

```mermaid
flowchart TD
    PI_REQ["PortInfo Request"] --> PI_RESP["PortInfo Response<br/>(osm_pi_rcv_process)"]
    PI_RESP --> NODE_TYPE{"Node Type?"}
    
    NODE_TYPE -->|Switch Port 0| SW_PORT0["Process Switch Mgmt Port<br/>(pi_rcv_process_switch_port0)"]
    NODE_TYPE -->|Switch External| SW_EXT["Process Switch Ext Port<br/>(pi_rcv_process_switch_ext_port)"]
    NODE_TYPE -->|CA/Router| CA_ROUTER["Process CA/Router Port<br/>(pi_rcv_process_ca_or_router_port)"]
    
    SW_PORT0 --> CHECK_ESP0{"Enhanced SP0?"}
    CHECK_ESP0 -->|Yes| FULL_CONFIG["Full Port Configuration"]
    CHECK_ESP0 -->|No| BASIC_CONFIG["Basic SMSL Configuration"]
    
    SW_EXT --> LINK_STATE{"Link State?"}
    LINK_STATE -->|Active/Armed/Init| PROBE_REMOTE["Probe Remote End<br/>(NodeInfo Request)"]
    LINK_STATE -->|Down| UNLINK["Unlink Remote<br/>(osm_node_unlink)"]
    
    CA_ROUTER --> ENDPORT_PROC["Process Endpoint<br/>(pi_rcv_process_endport)"]
    
    FULL_CONFIG --> UPDATE_PHYSP["Update Physical Port<br/>(osm_physp_set_port_info)"]
    BASIC_CONFIG --> UPDATE_PHYSP
    PROBE_REMOTE --> UPDATE_PHYSP
    UNLINK --> UPDATE_PHYSP
    ENDPORT_PROC --> UPDATE_PHYSP
    
    UPDATE_PHYSP --> GET_TABLES["Get PKey/SLtoVL Tables<br/>(pi_rcv_get_pkey_slvl_vla_tables)"]
```

The port discovery process tracks several key attributes:

| Attribute | Purpose | Code Location |
|-----------|---------|---------------|
| Port State | Link status and configuration | [opensm/osm_port_info_rcv.c:292-402]() |
| MTU Capability | Maximum transmission unit | [opensm/osm_port_info_rcv.c:101-130]() |
| VL Capability | Virtual lane support | [opensm/osm_port_info_rcv.c:119-129]() |
| Speed/Width | Link physical characteristics | [opensm/osm_link_mgr.c:346-423]() |

Sources: [opensm/osm_port_info_rcv.c:642-825](), [opensm/osm_port_info_rcv.c:205-254](), [opensm/osm_port_info_rcv.c:259-443]()

## Link Discovery and Topology Building

Link discovery extends directed routes through active ports to discover the complete fabric topology. The process uses DR (Directed Route) path extension:

```mermaid
flowchart TD
    ACTIVE_PORT["Active Port Detected"] --> CHECK_REMOTE{"Remote End<br/>Discovered?"}
    CHECK_REMOTE -->|No| EXTEND_PATH["Extend DR Path<br/>(osm_dr_path_extend)"]
    CHECK_REMOTE -->|Yes| VERIFY_LINK["Verify Existing Link"]
    
    EXTEND_PATH --> SEND_NI["Send NodeInfo<br/>to Remote End"]
    SEND_NI --> REMOTE_RESP["Remote Response"]
    REMOTE_RESP --> CREATE_LINK["Create Link<br/>(osm_node_link)"]
    
    CREATE_LINK --> UPDATE_DB["Update Neighbor DB<br/>(osm_db_neighbor_set)"]
    VERIFY_LINK --> UPDATE_DB
    
    UPDATE_DB --> CACHE_UPDATE["Update Routing Cache<br/>(osm_ucast_cache_check_new_link)"]
    CACHE_UPDATE --> CONTINUE["Continue Discovery"]
    
    subgraph "Link Creation Details"
        L_START["osm_node_link()"] --> L_GET_PHYSP["Get Physical Ports"]
        L_GET_PHYSP --> L_LINK["Set Remote Pointers<br/>(osm_physp_link)"]
        L_LINK --> L_PERSIST["Persist to Database"]
    end
```

The topology building process maintains several key data structures:

- **Node Table** (`node_guid_tbl`) - Maps node GUIDs to `osm_node_t` objects
- **Port Table** (`port_guid_tbl`) - Maps port GUIDs to `osm_port_t` objects  
- **Switch Table** (`sw_guid_tbl`) - Maps switch GUIDs to `osm_switch_t` objects
- **Link Database** - Persistent neighbor relationships

Sources: [opensm/osm_port_info_rcv.c:358-393](), [opensm/osm_node_info_rcv.c:279-309](), [opensm/osm_node.c:158-173]()

## LID Assignment Process

LID (Local Identifier) assignment occurs after topology discovery and follows a sophisticated algorithm that balances persistence with fabric changes:

```mermaid
flowchart TD
    LID_START["LID Assignment Start<br/>(osm_lid_mgr_process)"] --> INIT_SWEEP["Initialize Sweep<br/>(lid_mgr_init_sweep)"]
    INIT_SWEEP --> LOAD_PERSISTENT["Load GUID-to-LID DB<br/>(osm_db_restore)"]
    LOAD_PERSISTENT --> VALIDATE_DB["Validate Persistent Data<br/>(lid_mgr_validate_db)"]
    
    VALIDATE_DB --> SCAN_PORTS["Scan All Ports"]
    SCAN_PORTS --> PORT_LOOP{"For Each Port"}
    
    PORT_LOOP --> GET_LID["Get Port LID<br/>(lid_mgr_get_port_lid)"]
    GET_LID --> LID_SOURCE{"LID Source?"}
    
    LID_SOURCE -->|Persistent DB| USE_PERSISTENT["Use Persistent LID"]
    LID_SOURCE -->|Current Config| VALIDATE_CURRENT["Validate Current LID"]
    LID_SOURCE -->|New Assignment| FIND_FREE["Find Free Range<br/>(lid_mgr_find_free_lid_range)"]
    
    USE_PERSISTENT --> SET_PORTINFO["Set PortInfo<br/>(lid_mgr_set_physp_pi)"]
    VALIDATE_CURRENT --> SET_PORTINFO
    FIND_FREE --> SET_PORTINFO
    
    SET_PORTINFO --> UPDATE_TABLES["Update LID Tables"]
    UPDATE_TABLES --> PORT_LOOP
    
    PORT_LOOP -->|Done| STORE_DB["Store GUID-to-LID DB<br/>(osm_db_store)"]
```

The LID manager maintains several data structures for efficient assignment:

| Structure | Purpose | File Location |
|-----------|---------|---------------|
| `used_lids[]` | Bitmap of assigned LIDs | [opensm/osm_lid_mgr.c:186-206]() |
| `free_ranges` | List of available LID ranges | [opensm/osm_lid_mgr.c:592-653]() |
| `port_lid_tbl` | Maps LIDs to ports | [opensm/osm_lid_mgr.c:779-781]() |
| GUID-to-LID DB | Persistent assignments | [opensm/osm_lid_mgr.c:774-777]() |

Sources: [opensm/osm_lid_mgr.c:290-571](), [opensm/osm_lid_mgr.c:680-785](), [opensm/osm_lid_mgr.c:802-1037]()

## Trap Handling and Dynamic Updates

OpenSM continuously monitors the fabric for changes through trap processing. Traps indicate dynamic events like link state changes, node additions/removals, and errors:

```mermaid
flowchart TD
    TRAP_RCV["Trap Received<br/>(osm_trap_rcv_process)"] --> VALIDATE["Validate Trap Source"]
    VALIDATE --> TRAP_TYPE{"Trap Type?"}
    
    TRAP_TYPE -->|128 Link State| LINK_CHANGE["Link State Change<br/>(force_heavy_sweep)"]
    TRAP_TYPE -->|129-131 Port Error| PORT_ERROR["Port Error Processing"]
    TRAP_TYPE -->|144 Local Change| NODE_CHANGE["Node Capability Change"]
    TRAP_TYPE -->|145 GUID Change| GUID_CHANGE["System GUID Change"]
    
    PORT_ERROR --> AGING_CHECK["Check Aging Tracker<br/>(cl_event_wheel_num_regs)"]
    AGING_CHECK --> THRESHOLD{"Error Count > Threshold?"}
    THRESHOLD -->|Yes| DISABLE_PORT["Disable Noisy Port<br/>(disable_port)"]
    THRESHOLD -->|No| MARK_UNHEALTHY["Mark Port Unhealthy<br/>(osm_physp_set_health)"]
    
    LINK_CHANGE --> FORCE_SWEEP["Force Heavy Sweep"]
    NODE_CHANGE --> UPDATE_NODE["Update Node Info"]
    GUID_CHANGE --> UPDATE_GUID["Update System GUID"]
    DISABLE_PORT --> FORCE_SWEEP
    MARK_UNHEALTHY --> FORCE_SWEEP
    
    FORCE_SWEEP --> TRIGGER_SM["Signal State Manager<br/>(osm_sm_signal)"]
    UPDATE_NODE --> CHECK_DESC["Update Node Description"]
    UPDATE_GUID --> TRIGGER_SM
    CHECK_DESC --> TRIGGER_SM
```

Key trap processing functions:

- `trap_rcv_process_request()` - Main trap processing logic at [opensm/osm_trap_rcv.c:372-681]()
- `shutup_noisy_port()` - Handles noisy port suppression at [opensm/osm_trap_rcv.c:331-370]()
- `aging_tracker_callback()` - Manages trap aging at [opensm/osm_trap_rcv.c:99-140]()

Sources: [opensm/osm_trap_rcv.c:372-681](), [opensm/osm_trap_rcv.c:331-370](), [opensm/osm_trap_rcv.c:99-140]()

## Key Data Structures

The discovery process builds and maintains several interconnected data structures that represent the fabric topology:

```mermaid
classDiagram
    class osm_subn_t {
        +cl_qmap_t node_guid_tbl
        +cl_qmap_t port_guid_tbl
        +cl_qmap_t sw_guid_tbl
        +cl_ptr_vector_t port_lid_tbl
        +osm_db_domain_t p_neighbor
    }
    
    class osm_node_t {
        +ib_node_info_t node_info
        +osm_physp_t physp_table[]
        +uint8_t physp_discovered[]
        +osm_switch_t sw
        +char print_desc
    }
    
    class osm_physp_t {
        +ib_port_info_t port_info
        +ib_net64_t port_guid
        +uint8_t port_num
        +osm_node_t p_node
        +osm_physp_t p_remote_physp
        +boolean_t healthy
        +osm_dr_path_t dr_path
        +osm_pkey_tbl_t pkeys
    }
    
    class osm_port_t {
        +ib_net64_t guid
        +ib_net16_t lid
        +osm_node_t p_node
        +osm_physp_t p_physp
        +uint32_t discovery_count
    }
    
    osm_subn_t --> osm_node_t : "contains"
    osm_subn_t --> osm_port_t : "contains"
    osm_node_t --> osm_physp_t : "owns"
    osm_port_t --> osm_physp_t : "references"
    osm_physp_t --> osm_physp_t : "p_remote_physp"
```

These structures form the core representation of the discovered topology, enabling efficient subnet management operations.

Sources: [include/opensm/osm_port.h:107-133](), [opensm/osm_node.c:94-129](), [opensm/osm_port.c:138-174]()

---

