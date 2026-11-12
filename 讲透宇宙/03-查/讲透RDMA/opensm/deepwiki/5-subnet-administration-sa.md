<!-- source: DeepWiki mcp.deepwiki.com · repo linux-rdma/opensm · page 5 Subnet Administration (SA) · fetched 2026-11-11 -->

# Subnet Administration (SA)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [include/opensm/osm_sa.h](include/opensm/osm_sa.h)
- [opensm/osm_sa.c](opensm/osm_sa.c)
- [opensm/osm_sa_link_record.c](opensm/osm_sa_link_record.c)
- [opensm/osm_sa_mcmember_record.c](opensm/osm_sa_mcmember_record.c)
- [opensm/osm_sa_multipath_record.c](opensm/osm_sa_multipath_record.c)
- [opensm/osm_sa_path_record.c](opensm/osm_sa_path_record.c)
- [opensm/osm_sa_pkey_record.c](opensm/osm_sa_pkey_record.c)
- [opensm/osm_sa_portinfo_record.c](opensm/osm_sa_portinfo_record.c)
- [opensm/osm_sa_service_record.c](opensm/osm_sa_service_record.c)
- [opensm/osm_sa_slvl_record.c](opensm/osm_sa_slvl_record.c)
- [opensm/osm_sa_sminfo_record.c](opensm/osm_sa_sminfo_record.c)
- [opensm/osm_sa_vlarb_record.c](opensm/osm_sa_vlarb_record.c)

</details>



The Subnet Administration (SA) component provides a query and response service for InfiniBand subnet information. It processes client requests for various types of subnet records and returns appropriate responses, acting as the primary interface for subnet discovery and path resolution in the OpenSM subnet manager.

For information about subnet discovery and topology management, see [Network Discovery and Topology](#3). For details about routing path calculation, see [Routing Management](#4).

## Architecture Overview

The SA component is built around a central `osm_sa_t` structure that coordinates multiple specialized record processors. Each processor handles specific types of SA queries (PathRecord, MCMemberRecord, etc.) through a dispatcher-based architecture.

### SA Component Structure

```mermaid
graph TB
    subgraph "SA Core"
        SA[osm_sa_t<br/>Main SA Object]
        MADCTRL[osm_sa_mad_ctrl_t<br/>MAD Controller]
        DISP[cl_dispatcher_t<br/>Message Dispatcher]
        
        SA --> MADCTRL
        SA --> DISP
    end
    
    subgraph "Record Processors"
        PR[osm_pr_rcv_process<br/>Path Records]
        MCMR[osm_mcmr_rcv_process<br/>MCMember Records]
        PIR[osm_pir_rcv_process<br/>PortInfo Records]
        LR[osm_lr_rcv_process<br/>Link Records]
        SR[osm_sr_rcv_process<br/>Service Records]
        PKEY[osm_pkey_rec_rcv_process<br/>PKey Records]
        SLVL[osm_slvl_rec_rcv_process<br/>SLVL Records]
        VLARB[osm_vlarb_rec_rcv_process<br/>VLArb Records]
    end
    
    subgraph "Message Types"
        PR_MSG[OSM_MSG_MAD_PATH_RECORD]
        MCMR_MSG[OSM_MSG_MAD_MCMEMBER_RECORD]
        PIR_MSG[OSM_MSG_MAD_PORTINFO_RECORD]
        LR_MSG[OSM_MSG_MAD_LINK_RECORD]
        SR_MSG[OSM_MSG_MAD_SERVICE_RECORD]
        PKEY_MSG[OSM_MSG_MAD_PKEY_TBL_RECORD]
        SLVL_MSG[OSM_MSG_MAD_SLVL_TBL_RECORD]
        VLARB_MSG[OSM_MSG_MAD_VL_ARB_RECORD]
    end
    
    DISP --> PR_MSG
    DISP --> MCMR_MSG
    DISP --> PIR_MSG
    DISP --> LR_MSG
    DISP --> SR_MSG
    DISP --> PKEY_MSG
    DISP --> SLVL_MSG
    DISP --> VLARB_MSG
    
    PR_MSG --> PR
    MCMR_MSG --> MCMR
    PIR_MSG --> PIR
    LR_MSG --> LR
    SR_MSG --> SR
    PKEY_MSG --> PKEY
    SLVL_MSG --> SLVL
    VLARB_MSG --> VLARB
```

**Sources:** [opensm/osm_sa.c:192-289](), [include/opensm/osm_sa.h:183-221]()

### SA Initialization and Registration

```mermaid
graph LR
    subgraph "Initialization Flow"
        INIT[osm_sa_init]
        MADCTRL_INIT[osm_sa_mad_ctrl_init]
        REG_START[Register Dispatchers]
        
        INIT --> MADCTRL_INIT
        MADCTRL_INIT --> REG_START
    end
    
    subgraph "Dispatcher Registration"
        REG_PR[cl_disp_register<br/>PATH_RECORD]
        REG_MCMR[cl_disp_register<br/>MCMEMBER_RECORD]
        REG_PIR[cl_disp_register<br/>PORTINFO_RECORD]
        REG_LR[cl_disp_register<br/>LINK_RECORD]
        REG_SR[cl_disp_register<br/>SERVICE_RECORD]
        
        REG_START --> REG_PR
        REG_START --> REG_MCMR
        REG_START --> REG_PIR
        REG_START --> REG_LR
        REG_START --> REG_SR
    end
    
    subgraph "Handler Assignment"
        HANDLE_PR[p_sa->pr_disp_h]
        HANDLE_MCMR[p_sa->mcmr_disp_h]
        HANDLE_PIR[p_sa->pir_disp_h]
        HANDLE_LR[p_sa->lr_disp_h]
        HANDLE_SR[p_sa->sr_disp_h]
        
        REG_PR --> HANDLE_PR
        REG_MCMR --> HANDLE_MCMR
        REG_PIR --> HANDLE_PIR
        REG_LR --> HANDLE_LR
        REG_SR --> HANDLE_SR
    end
```

**Sources:** [opensm/osm_sa.c:159-325](), [opensm/osm_sa.c:218-289]()

## Core SA Data Structures

### Main SA Structure

The `osm_sa_t` structure serves as the central coordination point for all SA operations:

| Field | Type | Purpose |
|-------|------|---------|
| `state` | `osm_sa_state_t` | Current SA state (INIT/READY) |
| `p_subn` | `osm_subn_t*` | Pointer to subnet database |
| `mad_ctrl` | `osm_sa_mad_ctrl_t` | MAD communication controller |
| `p_disp` | `cl_dispatcher_t*` | Message dispatcher for GET requests |
| `p_set_disp` | `cl_dispatcher_t*` | Message dispatcher for SET requests |
| `sa_trans_id` | `atomic32_t` | Transaction ID counter |

**Sources:** [include/opensm/osm_sa.h:183-221]()

### SA Response Item Structure

The `osm_sa_item_t` structure provides a unified container for all SA response types:

```mermaid
graph TB
    subgraph "osm_sa_item_t Structure"
        ITEM[osm_sa_item_t]
        LIST[cl_list_item_t<br/>list_item]
        RESP[resp union]
        
        ITEM --> LIST
        ITEM --> RESP
    end
    
    subgraph "Response Union Types"
        PATH[ib_path_rec_t<br/>path_rec]
        MC[ib_member_rec_t<br/>mc_rec]
        PORT[ib_portinfo_record_t<br/>port_rec]
        LINK[ib_link_record_t<br/>link_rec]
        SERVICE[ib_service_record_t<br/>service_rec]
        PKEY[ib_pkey_table_record_t<br/>pkey_rec]
        
        RESP --> PATH
        RESP --> MC
        RESP --> PORT
        RESP --> LINK
        RESP --> SERVICE
        RESP --> PKEY
    end
```

**Sources:** [include/opensm/osm_sa.h:133-155]()

## Record Processors

### Path Record Processing

Path records provide routing information between source and destination ports. The path record processor calculates optimal paths considering MTU, rate, packet lifetime, and QoS constraints.

Key functions in path record processing:

| Function | Purpose |
|----------|---------|
| `osm_pr_rcv_process` | Main path record request handler |
| `pr_rcv_get_path_parms` | Calculate path parameters (MTU, rate, SL) |
| `pr_rcv_build_pr` | Build path record response |
| `osm_get_path_params` | Public API for path parameter calculation |

**Sources:** [opensm/osm_sa_path_record.c:145-849](), [opensm/osm_sa_path_record.c:875-884]()

### Multicast Member Record Processing

MCMember records manage multicast group membership and configuration:

```mermaid
graph LR
    subgraph "MCMember Operations"
        JOIN[Join Request]
        LEAVE[Leave Request]
        QUERY[Query Request]
        
        JOIN --> VALIDATE[validate_join_comp_mask]
        LEAVE --> VALIDATE_DEL[validate_delete]
        QUERY --> VALIDATE_MORE[validate_more_comp_fields]
    end
    
    subgraph "Group Management"
        CREATE[mcmr_rcv_create_new_mgrp]
        FIND[osm_get_mgrp_by_mgid]
        REMOVE[osm_mgrp_remove_port]
        
        VALIDATE --> CREATE
        VALIDATE --> FIND
        VALIDATE_DEL --> REMOVE
    end
    
    subgraph "MLID Management"
        GET_MLID[get_new_mlid]
        FREE_MLID[free_mlid]
        IPV6_SNM[find_ipv6_snm_mlid]
        
        CREATE --> GET_MLID
        REMOVE --> FREE_MLID
        GET_MLID --> IPV6_SNM
    end
```

**Sources:** [opensm/osm_sa_mcmember_record.c:156-183](), [opensm/osm_sa_mcmember_record.c:828-946](), [opensm/osm_sa_mcmember_record.c:970-1066]()

### Service Record Processing

Service records enable service discovery and registration in the subnet:

| Operation | Function | Description |
|-----------|----------|-------------|
| Register | `sr_rcv_new_sr` | Add new service record |
| Query | `sr_rcv_get_sr` | Retrieve matching service records |
| Delete | `sr_rcv_remove_sr` | Remove service record |
| Validate | `validate_sr` | Check PKey and name-key associations |

**Sources:** [opensm/osm_sa_service_record.c:161-195](), [opensm/osm_sa_service_record.c:197-214]()

## MAD Processing Flow

### Request Processing Pipeline

```mermaid
graph TB
    subgraph "Incoming MAD"
        MAD[SA MAD Request]
        ATTR[attr_id]
        METHOD[method]
        COMP_MASK[comp_mask]
        
        MAD --> ATTR
        MAD --> METHOD
        MAD --> COMP_MASK
    end
    
    subgraph "Dispatcher Routing"
        DISP[cl_dispatcher_t]
        ROUTE[Message Routing]
        HANDLER[Record Handler]
        
        ATTR --> DISP
        DISP --> ROUTE
        ROUTE --> HANDLER
    end
    
    subgraph "Record Processing"
        VALIDATE[Validate Request]
        SEARCH[Search Database]
        BUILD_RESP[Build Response]
        
        HANDLER --> VALIDATE
        VALIDATE --> SEARCH
        SEARCH --> BUILD_RESP
    end
    
    subgraph "Response Generation"
        RESP_LIST[cl_qlist_t response_list]
        SA_RESPOND[osm_sa_respond]
        SEND[osm_sa_send]
        
        BUILD_RESP --> RESP_LIST
        RESP_LIST --> SA_RESPOND
        SA_RESPOND --> SEND
    end
```

**Sources:** [opensm/osm_sa.c:422-534](), [opensm/osm_sa.c:345-359]()

### Response Building Pattern

All SA record processors follow a common pattern for building responses:

1. **Validation**: Check component mask and request parameters
2. **Database Search**: Query subnet database for matching records
3. **Response Building**: Create `osm_sa_item_t` objects for each match
4. **List Management**: Add items to response list
5. **Response Transmission**: Send response via `osm_sa_respond`

**Sources:** [opensm/osm_sa_path_record.c:875-884](), [opensm/osm_sa_portinfo_record.c:75-138]()

## Component Mask Processing

Component masks specify which fields in SA queries should be matched. Each record processor implements component mask validation:

```mermaid
graph LR
    subgraph "Component Mask Types"
        LID_MASK[IB_PR_COMPMASK_SLID<br/>IB_PR_COMPMASK_DLID]
        GID_MASK[IB_PR_COMPMASK_SGID<br/>IB_PR_COMPMASK_DGID]
        QOS_MASK[IB_PR_COMPMASK_MTU<br/>IB_PR_COMPMASK_RATE]
        PKEY_MASK[IB_PR_COMPMASK_PKEY]
    end
    
    subgraph "Validation Functions"
        CHECK_LID[Check LID Range]
        CHECK_GID[Validate GID Format]
        CHECK_QOS[Validate QoS Parameters]
        CHECK_PKEY[Verify PKey Access]
        
        LID_MASK --> CHECK_LID
        GID_MASK --> CHECK_GID
        QOS_MASK --> CHECK_QOS
        PKEY_MASK --> CHECK_PKEY
    end
    
    subgraph "Database Query"
        FILTER[Apply Filters]
        MATCH[Find Matches]
        RESULT[Build Results]
        
        CHECK_LID --> FILTER
        CHECK_GID --> FILTER
        CHECK_QOS --> FILTER
        CHECK_PKEY --> FILTER
        FILTER --> MATCH
        MATCH --> RESULT
    end
```

**Sources:** [opensm/osm_sa_path_record.c:487-608](), [opensm/osm_sa_portinfo_record.c:184-295]()

## Communication and Threading

### MAD Controller Integration

The SA integrates with the OpenSM MAD handling system through `osm_sa_mad_ctrl_t`:

| Function | Purpose |
|----------|---------|
| `osm_sa_mad_ctrl_init` | Initialize MAD controller |
| `osm_sa_mad_ctrl_bind` | Bind to InfiniBand port |
| `osm_sa_send` | Send SA response MAD |
| `osm_sa_send_error` | Send error response |

**Sources:** [opensm/osm_sa.c:327-343](), [opensm/osm_sa.c:361-420]()

### Dispatcher-Based Processing

The SA uses OpenSM's dispatcher system for concurrent request processing:

- **GET Requests**: Processed through main dispatcher (`p_disp`)
- **SET Requests**: Processed through dedicated dispatcher (`p_set_disp`)  
- **Message Routing**: Based on SA attribute ID (`attr_id`)
- **Handler Registration**: Each record type registers specific handler function

**Sources:** [opensm/osm_sa.c:192-319]()

The SA component provides the primary interface for subnet information queries in OpenSM, coordinating multiple specialized processors to handle the full range of InfiniBand SA record types while maintaining consistency with subnet state and enforcing proper access controls.

---

