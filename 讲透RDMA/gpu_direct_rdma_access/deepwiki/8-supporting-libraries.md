<!-- source: DeepWiki mcp.deepwiki.com · repo Mellanox/gpu_direct_rdma_access · page 8 Supporting Libraries · fetched 2026-11-11 -->

# Supporting Libraries

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ibv_helper.h](ibv_helper.h)
- [khash.h](khash.h)

</details>



This document covers the auxiliary libraries that provide foundational functionality to the GPU Direct RDMA Access system. These libraries handle generic data structures and InfiniBand-specific operations that are essential for the core RDMA engine's operation.

The supporting libraries consist of two main components: a generic hash table implementation for efficient address handle caching, and InfiniBand helper utilities for GID type detection and management. For information about the core RDMA functionality that uses these libraries, see [Core RDMA Engine](#3). For details about the main applications that benefit from these libraries, see [Client-Server Applications](#5).

## Hash Table Library

The hash table library provides a generic, high-performance hash table implementation used throughout the RDMA system for caching frequently accessed data structures. The library is implemented as a header-only C library that uses macro-based code generation to create type-specific hash table implementations.

### Architecture and Design

The hash table implementation uses several key design principles for optimal performance in the RDMA context:

```mermaid
graph TB
    subgraph "Hash Table Architecture"
        MACROS["KHASH_INIT Macros<br/>Code Generation"]
        
        subgraph "Core Data Structure"
            BUCKETS["n_buckets<br/>Hash Table Size"]
            FLAGS["flags Array<br/>Bucket State Tracking"]
            KEYS["keys Array<br/>Key Storage"]
            VALUES["vals Array<br/>Value Storage"]
        end
        
        subgraph "Hash Functions"
            INT_HASH["kh_int_hash_func<br/>Integer Hashing"]
            STR_HASH["__ac_X31_hash_string<br/>String Hashing"]
            WANG_HASH["__ac_Wang_hash<br/>Alternative Integer Hash"]
        end
        
        subgraph "Collision Resolution"
            QUAD_PROBE["Quadratic Probing<br/>i*(i+1)/2 Step Function"]
            CACHE_OPT["Cache Performance<br/>Power-of-2 Capacity"]
        end
        
        subgraph "Operations"
            PUT_OP["kh_put<br/>Insert/Update"]
            GET_OP["kh_get<br/>Lookup"]
            DEL_OP["kh_del<br/>Delete"]
            RESIZE_OP["kh_resize<br/>Dynamic Resizing"]
        end
    end
    
    MACROS --> BUCKETS
    MACROS --> FLAGS
    MACROS --> KEYS
    MACROS --> VALUES
    
    INT_HASH --> PUT_OP
    STR_HASH --> PUT_OP
    WANG_HASH --> PUT_OP
    
    QUAD_PROBE --> GET_OP
    CACHE_OPT --> GET_OP
    
    PUT_OP --> RESIZE_OP
    GET_OP --> DEL_OP
```

**Sources:** [khash.h:1-674]()

### Hash Table Types and Instantiation

The library supports multiple hash table configurations through macro-based instantiation:

| Macro | Key Type | Value Type | Use Case |
|-------|----------|------------|----------|
| `KHASH_SET_INIT_INT` | `khint32_t` | None (set) | Integer sets |
| `KHASH_MAP_INIT_INT` | `khint32_t` | User-defined | Integer-keyed maps |
| `KHASH_SET_INIT_INT64` | `khint64_t` | None (set) | 64-bit integer sets |
| `KHASH_MAP_INIT_INT64` | `khint64_t` | User-defined | 64-bit integer-keyed maps |
| `KHASH_SET_INIT_STR` | `const char*` | None (set) | String sets |
| `KHASH_MAP_INIT_STR` | `const char*` | User-defined | String-keyed maps |

The hash table structure is defined using the `__KHASH_TYPE` macro, which creates a structure containing bucket management fields, state flags, and separate arrays for keys and values.

**Sources:** [khash.h:197-203](), [khash.h:632-672]()

### Core Operations and Performance

The hash table provides a complete set of operations with performance optimizations specific to high-frequency RDMA operations:

```mermaid
graph TB
    subgraph "Hash Table Operations Flow"
        INIT["kh_init_name()<br/>Table Initialization"]
        
        subgraph "Insertion Path"
            PUT_START["kh_put_name()<br/>Insert Key"]
            HASH_CALC["Hash Calculation<br/>__hash_func(key)"]
            PROBE_SEQ["Quadratic Probing<br/>Find Empty Bucket"]
            RESIZE_CHECK["Load Factor Check<br/>n_occupied >= upper_bound"]
            DYNAMIC_RESIZE["kh_resize_name()<br/>Rehash All Elements"]
        end
        
        subgraph "Lookup Path"
            GET_START["kh_get_name()<br/>Find Key"]
            FAST_LOOKUP["Direct Hash Lookup<br/>key & mask"]
            PROBE_MATCH["Probe Until Match<br/>or Empty Bucket"]
        end
        
        subgraph "Memory Management"
            FLAG_BITS["Flag Bits Management<br/>2 bits per bucket"]
            EMPTY_BIT["Empty Flag<br/>Bit 1"]
            DEL_BIT["Deleted Flag<br/>Bit 0"]
        end
    end
    
    INIT --> PUT_START
    PUT_START --> HASH_CALC
    HASH_CALC --> PROBE_SEQ
    PROBE_SEQ --> RESIZE_CHECK
    RESIZE_CHECK --> DYNAMIC_RESIZE
    
    GET_START --> FAST_LOOKUP
    FAST_LOOKUP --> PROBE_MATCH
    
    PUT_START --> FLAG_BITS
    FLAG_BITS --> EMPTY_BIT
    FLAG_BITS --> DEL_BIT
```

The collision resolution uses quadratic probing with the step function `i*(i+1)/2`, which guarantees traversal of each bucket when the capacity is a power of 2. This approach provides better cache performance than double hashing while maintaining robustness against clustering.

**Sources:** [khash.h:244-256](), [khash.h:321-361](), [khash.h:48-76]()

### Integration with RDMA System

The hash table library is primarily used in the RDMA system for address handle caching, where it stores mappings between remote endpoints and their corresponding InfiniBand address handles. This caching mechanism is critical for performance in Dynamic Connect queue pair operations.

**Sources:** [khash.h:1-674]()

## InfiniBand Helpers

The InfiniBand helper library provides specialized utilities for querying and managing InfiniBand device properties, with particular focus on GID (Global Identifier) type detection and management. These utilities are essential for proper RoCE (RDMA over Converged Ethernet) operation and compatibility across different InfiniBand hardware generations.

### GID Type Management

The library defines and manages different GID types that correspond to various InfiniBand and RoCE protocol versions:

```mermaid
graph TB
    subgraph "GID Type Detection System"
        subgraph "GID Types"
            IB_ROCE_V1["IBV_GID_TYPE_IB_ROCE_V1<br/>Traditional IB/RoCE v1"]
            ROCE_V2["IBV_GID_TYPE_ROCE_V2<br/>RoCE v2 (IP-based)"]
        end
        
        subgraph "Detection Functions"
            QUERY_TYPE["ibv_query_gid_type()<br/>Read sysfs GID Attributes"]
            FIND_SGID["ibv_find_sgid_type()<br/>Locate Compatible Source GID"]
        end
        
        subgraph "System Interface"
            SYSFS_READ["ibv_read_sysfs_file()<br/>Kernel Interface"]
            PATH_BUILD["Device Path Construction<br/>ports/N/gid_attrs/types/M"]
        end
        
        subgraph "Fallback Handling"
            EINVAL_CASE["EINVAL Error<br/>Assume IB/RoCE v1"]
            ENOENT_CASE["ENOENT Error<br/>Old Kernel Detection"]
            DIR_CHECK["Directory Existence<br/>Kernel Capability Check"]
        end
    end
    
    QUERY_TYPE --> SYSFS_READ
    SYSFS_READ --> PATH_BUILD
    PATH_BUILD --> EINVAL_CASE
    PATH_BUILD --> ENOENT_CASE
    EINVAL_CASE --> DIR_CHECK
    
    FIND_SGID --> QUERY_TYPE
    IB_ROCE_V1 --> FIND_SGID
    ROCE_V2 --> FIND_SGID
```

**Sources:** [ibv_helper.h:39-42](), [ibv_helper.h:88-145]()

### System File Interface

The helper library interacts directly with the Linux kernel's sysfs interface to obtain InfiniBand device information:

| Function | Purpose | Sysfs Path Pattern |
|----------|---------|-------------------|
| `ibv_read_sysfs_file` | Generic sysfs file reader | `{device_path}/{file}` |
| `ibv_query_gid_type` | Query specific GID type | `ports/{port}/gid_attrs/types/{index}` |
| `ibv_find_sgid_type` | Find matching source GID | Iterates through GID table |

The system handles various kernel versions and hardware capabilities through robust error handling and fallback mechanisms. When GID attribute files don't exist, the system assumes compatibility with older IB/RoCE v1 protocols.

**Sources:** [ibv_helper.h:44-80](), [ibv_helper.h:88-145]()

### GID Type Detection Algorithm

The GID type detection process implements a comprehensive algorithm for determining protocol compatibility:

```mermaid
graph TB
    subgraph "GID Type Detection Flow"
        START["ibv_query_gid_type()"]
        
        subgraph "Sysfs Query"
            BUILD_PATH["Build sysfs Path<br/>ports/X/gid_attrs/types/Y"]
            READ_FILE["ibv_read_sysfs_file()<br/>Read Type String"]
        end
        
        subgraph "Error Handling"
            CHECK_ERRNO["Check errno Value"]
            EINVAL_PATH["errno == EINVAL<br/>IB Context"]
            ENOENT_PATH["errno == ENOENT<br/>Old Kernel"]
            DIR_EXISTS["Check gid_attrs<br/>Directory Existence"]
        end
        
        subgraph "String Matching"
            V1_MATCH["String == 'IB/RoCE v1'<br/>Set IBV_GID_TYPE_IB_ROCE_V1"]
            V2_MATCH["String == 'RoCE v2'<br/>Set IBV_GID_TYPE_ROCE_V2"]
            UNKNOWN["Unknown String<br/>Return ENOTSUP"]
        end
        
        subgraph "Result"
            SUCCESS["Return 0<br/>Type Set Successfully"]
            ERROR["Return -1<br/>Detection Failed"]
        end
    end
    
    START --> BUILD_PATH
    BUILD_PATH --> READ_FILE
    READ_FILE --> CHECK_ERRNO
    
    CHECK_ERRNO --> EINVAL_PATH
    CHECK_ERRNO --> ENOENT_PATH
    CHECK_ERRNO --> V1_MATCH
    
    EINVAL_PATH --> SUCCESS
    ENOENT_PATH --> DIR_EXISTS
    DIR_EXISTS --> SUCCESS
    DIR_EXISTS --> ERROR
    
    V1_MATCH --> SUCCESS
    READ_FILE --> V2_MATCH
    V2_MATCH --> SUCCESS
    READ_FILE --> UNKNOWN
    UNKNOWN --> ERROR
```

The detection algorithm handles three main scenarios: successful type detection from sysfs, fallback for IB-only contexts (EINVAL), and compatibility mode for older kernels (ENOENT). This robust approach ensures operation across diverse hardware and kernel configurations.

**Sources:** [ibv_helper.h:88-145](), [ibv_helper.h:86-87]()

### Source GID Selection

The `ibv_find_sgid_type` function implements an algorithm to locate appropriate source GIDs based on type and address family requirements:

```mermaid
graph TB
    subgraph "Source GID Selection Process"
        INIT["Initialize Index = 0<br/>Set Target Criteria"]
        
        subgraph "Iteration Loop"
            QUERY_GID["ibv_query_gid()<br/>Get GID at Index"]
            QUERY_TYPE_LOOP["ibv_query_gid_type()<br/>Get Type at Index"]
            CHECK_FAMILY["Determine Address Family<br/>IPv4 vs IPv6"]
        end
        
        subgraph "Match Criteria"
            TYPE_MATCH["gid_type == sgid_type"]
            FAMILY_MATCH["gid_family == sgid_family"]
            BOTH_MATCH["Both Criteria Met"]
        end
        
        subgraph "Result Handling"
            FOUND["Return Index<br/>Compatible GID Found"]
            INCREMENT["idx++<br/>Continue Search"]
            ERROR_RETURN["Return -1<br/>No Match Found"]
        end
    end
    
    INIT --> QUERY_GID
    QUERY_GID --> QUERY_TYPE_LOOP
    QUERY_TYPE_LOOP --> CHECK_FAMILY
    CHECK_FAMILY --> TYPE_MATCH
    TYPE_MATCH --> FAMILY_MATCH
    FAMILY_MATCH --> BOTH_MATCH
    
    BOTH_MATCH --> FOUND
    TYPE_MATCH --> INCREMENT
    FAMILY_MATCH --> INCREMENT
    INCREMENT --> QUERY_GID
```

The function iterates through the device's GID table, querying both the GID value and its type, then checking for compatibility with the requested criteria. Address family determination is based on the GID's raw bytes, where IPv4-mapped addresses have specific bit patterns in their prefix.

**Sources:** [ibv_helper.h:147-176]()

---

