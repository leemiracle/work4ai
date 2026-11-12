<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuCascade · page 4 Memory Management Subsystem · fetched 2026-10-26 -->

# Memory Management Subsystem

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [include/memory/memory_reservation_manager.hpp](include/memory/memory_reservation_manager.hpp)
- [src/memory/CMakeLists.txt](src/memory/CMakeLists.txt)
- [src/memory/memory_reservation_manager.cpp](src/memory/memory_reservation_manager.cpp)
- [test/memory/test_memory_reservation_manager.cpp](test/memory/test_memory_reservation_manager.cpp)

</details>



## Purpose and Scope

The Memory Management Subsystem provides heterogeneous memory orchestration across GPU, HOST, and DISK tiers in cuCascade. This subsystem is responsible for:

- Allocating and tracking memory reservations across multiple memory tiers
- Managing memory spaces with device-specific allocators (RMM for GPU, pinned memory for HOST)
- Implementing reservation strategies that abstract memory placement decisions
- Supporting NUMA-aware host memory allocation
- Coordinating memory pressure handling and tier transitions

This page provides an architectural overview of the memory management system. For detailed documentation of specific components, see:
- Memory Reservation Manager implementation details: [#4.1](#4.1)
- Memory space abstractions and resource types: [#4.2](#4.2)
- Hardware topology detection and NUMA configuration: [#4.3](#4.3)
- Data representation conversion that uses this subsystem: [#5](#5)

**Sources:** [include/memory/memory_reservation_manager.hpp:1-307](), [src/memory/memory_reservation_manager.cpp:1-368]()

---

## System Overview

The memory management subsystem consists of three primary architectural layers:

1. **Central Coordination Layer**: `memory_reservation_manager` coordinates reservation requests across all available memory spaces
2. **Memory Space Layer**: Individual `memory_space` instances represent specific memory resources (e.g., GPU device 0, HOST NUMA node 1)
3. **Allocation Strategy Layer**: `reservation_request_strategy` implementations define placement policies for memory reservations

```mermaid
graph TB
    subgraph "Application Layer"
        APP["Data Batch / Converter<br/>Requests memory"]
    end
    
    subgraph "Coordination Layer"
        MRM["memory_reservation_manager<br/>Central orchestrator"]
        STRAT["reservation_request_strategy<br/>Strategy pattern"]
    end
    
    subgraph "Memory Space Layer"
        GPU0["memory_space<br/>Tier::GPU, device=0"]
        GPU1["memory_space<br/>Tier::GPU, device=1"]
        HOST0["memory_space<br/>Tier::HOST, device=0"]
        DISK["memory_space<br/>Tier::DISK, device=0"]
    end
    
    subgraph "Resource Layer"
        RMM_RES["reservation_aware_resource_adaptor<br/>GPU allocator"]
        HOST_RES["fixed_size_host_memory_resource<br/>HOST allocator"]
    end
    
    APP -->|"request_reservation(strategy, size)"| MRM
    MRM -->|"get_candidates()"| STRAT
    STRAT -->|"returns memory_space*"| MRM
    MRM -->|"make_reservation()"| GPU0
    MRM -->|"make_reservation()"| GPU1
    MRM -->|"make_reservation()"| HOST0
    MRM -->|"make_reservation()"| DISK
    
    GPU0 -->|"wraps"| RMM_RES
    GPU1 -->|"wraps"| RMM_RES
    HOST0 -->|"wraps"| HOST_RES
    
    MRM -.waits on condition_variable.-> MRM
```

**Diagram: Memory Management Subsystem Architecture**

The `memory_reservation_manager` acts as a centralized coordinator that maintains a collection of `memory_space` instances. When a reservation is requested, a `reservation_request_strategy` determines which memory spaces are candidates. The manager attempts to create a reservation on one of the candidates, blocking if necessary until memory becomes available.

**Sources:** [include/memory/memory_reservation_manager.hpp:178-303](), [src/memory/memory_reservation_manager.cpp:122-148]()

---

## Core Components

### memory_reservation_manager

The `memory_reservation_manager` class is the central entry point for all memory allocation requests in cuCascade. It maintains a registry of all available memory spaces and coordinates reservation requests across them.

| Component | Type | Purpose |
|-----------|------|---------|
| `_memory_spaces` | `std::vector<std::unique_ptr<memory_space>>` | Owned storage of all memory spaces |
| `_memory_space_lookup` | `std::unordered_map<memory_space_id, memory_space*>` | Fast lookup by tier and device ID |
| `_tier_to_memory_spaces` | `std::unordered_map<Tier, std::vector<memory_space*>>` | Grouped by tier for tier-based strategies |
| `_wait_cv` | `std::condition_variable` | Coordination for blocking reservation requests |

```mermaid
classDiagram
    class memory_reservation_manager {
        -vector~unique_ptr~memory_space~~ _memory_spaces
        -unordered_map~memory_space_id, memory_space*~ _memory_space_lookup
        -unordered_map~Tier, vector~memory_space*~~ _tier_to_memory_spaces
        -condition_variable _wait_cv
        +memory_reservation_manager(vector~memory_space_config~)
        +request_reservation(reservation_request_strategy&, size_t) unique_ptr~reservation~
        +get_memory_space(Tier, int32_t) memory_space*
        +get_memory_spaces_for_tier(Tier) span~memory_space*~
        +get_available_memory_for_tier(Tier) size_t
        +get_total_reserved_memory() size_t
    }
    
    class memory_space_config {
        +Tier tier
        +int device_id
        +size_t memory_limit
        +float downgrade_tigger_threshold
        +float downgrade_stop_threshold
        +size_t memory_capacity
        +DeviceMemoryResourceFactoryFn mr_factory_fn
    }
    
    class memory_space {
        +get_tier() Tier
        +get_device_id() int32_t
        +get_available_memory() size_t
        +make_reservation(size_t) unique_ptr~reservation~
        +get_default_allocator() device_memory_resource*
    }
    
    class reservation {
        +tier() Tier
        +device_id() int32_t
        +size() size_t
        +get_memory_resource_of~T~() auto*
    }
    
    memory_reservation_manager "1" *-- "n" memory_space
    memory_reservation_manager ..> memory_space_config : constructs from
    memory_space ..> reservation : creates
```

**Diagram: Core Memory Management Classes**

**Sources:** [include/memory/memory_reservation_manager.hpp:178-303](), [src/memory/memory_reservation_manager.cpp:122-148]()

### memory_space

Each `memory_space` instance represents a single memory resource with a specific tier and device ID. It encapsulates:
- A device memory resource (e.g., `reservation_aware_resource_adaptor` for GPU, `fixed_size_host_memory_resource` for HOST)
- Memory accounting: available memory, reserved memory, active reservation count
- Reservation lifecycle management

Memory spaces are created during `memory_reservation_manager` initialization from `memory_space_config` objects.

**Sources:** [include/memory/memory_reservation_manager.hpp:191-212](), [src/memory/memory_reservation_manager.cpp:128-146]()

### reservation

A `reservation` represents an allocated chunk of memory within a specific `memory_space`. It provides:
- RAII semantics: memory is returned to the space when the reservation is destroyed
- Access to the underlying device memory resource for actual allocations
- Metadata: tier, device ID, and size

Reservations are returned as `std::unique_ptr<reservation>` to enforce single ownership.

**Sources:** [include/memory/memory_reservation_manager.hpp:237-238](), [test/memory/test_memory_reservation_manager.cpp:128-138]()

---

## Memory Tier Hierarchy

cuCascade organizes memory into three tiers, each with different performance and capacity characteristics:

```mermaid
graph LR
    subgraph "Tier::GPU - Highest Performance"
        GPU0["memory_space<br/>tier=GPU, device=0<br/>reservation_aware_resource_adaptor"]
        GPU1["memory_space<br/>tier=GPU, device=1<br/>reservation_aware_resource_adaptor"]
    end
    
    subgraph "Tier::HOST - Medium Performance"
        HOST0["memory_space<br/>tier=HOST, device=0<br/>fixed_size_host_memory_resource"]
        HOST1["memory_space<br/>tier=HOST, device=1<br/>NUMA node 1"]
    end
    
    subgraph "Tier::DISK - Archive Storage"
        DISK0["memory_space<br/>tier=DISK, device=0<br/>Serialized storage"]
    end
    
    GPU0 -.downgrade.-> HOST0
    GPU1 -.downgrade.-> HOST1
    HOST0 -.downgrade.-> DISK0
    HOST1 -.downgrade.-> DISK0
    
    HOST0 -.upgrade.-> GPU0
    HOST1 -.upgrade.-> GPU1
```

**Diagram: Three-Tier Memory Hierarchy**

| Tier | Characteristics | Typical Capacity | Allocator Type |
|------|----------------|------------------|----------------|
| `Tier::GPU` | Fastest access, limited capacity, one per GPU device | 2-80 GB per device | `reservation_aware_resource_adaptor` wrapping RMM |
| `Tier::HOST` | Medium speed, larger capacity, one per NUMA node | 4-512 GB per node | `fixed_size_host_memory_resource` with pinned memory |
| `Tier::DISK` | Slowest access, effectively unlimited | Terabytes | Serialization to filesystem |

Each tier consists of one or more `memory_space` instances identified by `(Tier, device_id)` pairs. The `device_id` represents:
- For `Tier::GPU`: CUDA device ID
- For `Tier::HOST`: NUMA node ID
- For `Tier::DISK`: Logical disk partition ID

**Sources:** [include/memory/common.hpp]() (implied from Tier enum usage), [test/memory/test_memory_reservation_manager.cpp:52-56]()

---

## Reservation Strategies

The subsystem uses the Strategy pattern to decouple reservation requests from memory placement decisions. All strategies inherit from `reservation_request_strategy`:

```mermaid
classDiagram
    class reservation_request_strategy {
        <<abstract>>
        #bool _strong_ordering
        +get_candidates(memory_reservation_manager&)* vector~memory_space*~
        +has_strong_ordering() bool
    }
    
    class any_memory_space_in_tier {
        +Tier tier
        +get_candidates() vector~memory_space*~
    }
    
    class any_memory_space_in_tier_with_preference {
        +Tier tier
        +optional~size_t~ preferred_device_id
        +get_candidates() vector~memory_space*~
    }
    
    class any_memory_space_in_tiers {
        +vector~Tier~ tiers
        +get_candidates() vector~memory_space*~
    }
    
    class specific_memory_space {
        +memory_space_id target_id
        +get_candidates() vector~memory_space*~
    }
    
    class any_memory_space_to_downgrade {
        +memory_space_id src_id
        +vector~Tier~ target_tiers
        +get_candidates() vector~memory_space*~
    }
    
    class any_memory_space_to_upgrade {
        +memory_space_id src_id
        +Tier target_tier
        +get_candidates() vector~memory_space*~
    }
    
    reservation_request_strategy <|-- any_memory_space_in_tier
    reservation_request_strategy <|-- any_memory_space_in_tier_with_preference
    reservation_request_strategy <|-- any_memory_space_in_tiers
    reservation_request_strategy <|-- specific_memory_space
    reservation_request_strategy <|-- any_memory_space_to_downgrade
    reservation_request_strategy <|-- any_memory_space_to_upgrade
```

**Diagram: Reservation Strategy Class Hierarchy**

### Strategy Types

| Strategy | Purpose | Strong Ordering | Example Usage |
|----------|---------|-----------------|---------------|
| `specific_memory_space` | Allocate on exact tier and device | Yes | Pin data to specific GPU |
| `any_memory_space_in_tier` | Any device within a tier | No | "Any GPU will do" |
| `any_memory_space_in_tier_with_preference` | Prefer specific device, fallback to others | Yes | Prefer local GPU, accept remote |
| `any_memory_space_in_tiers` | Try tiers in preference order | No | Try GPU first, fallback to HOST |
| `any_memory_space_to_downgrade` | Move data to lower tier | Yes | Free GPU memory under pressure |
| `any_memory_space_to_upgrade` | Move data to higher tier | Yes | Promote data to GPU for processing |

**Strong ordering** means the strategy defines a strict preference order that must be respected. When `_strong_ordering = true`, the manager will only try the first successful candidate. When `false`, it tries all candidates non-deterministically first (with `make_reservation_or_null`), then falls back to blocking attempts.

**Sources:** [include/memory/memory_reservation_manager.hpp:55-167](), [src/memory/memory_reservation_manager.cpp:64-116](), [src/memory/memory_reservation_manager.cpp:308-335]()

### Usage Example

```cpp
// Example from test suite
auto manager = createSingleDeviceMemoryManager();

// Strategy 1: Specific GPU device
auto gpu_res = manager->request_reservation(
    specific_memory_space(Tier::GPU, 0), 
    200 * 1024 * 1024  // 200 MB
);

// Strategy 2: Any HOST device
auto host_res = manager->request_reservation(
    any_memory_space_in_tier(Tier::HOST), 
    500 * 1024 * 1024  // 500 MB
);

// Strategy 3: Try multiple tiers with preference
std::vector<Tier> preferences = {Tier::GPU, Tier::HOST, Tier::DISK};
auto flexible_res = manager->request_reservation(
    any_memory_space_in_tiers(preferences),
    100 * 1024 * 1024  // 100 MB
);
```

**Sources:** [test/memory/test_memory_reservation_manager.cpp:114-208]()

---

## Reservation Request Flow

The following diagram shows the complete flow from a reservation request to allocation:

```mermaid
sequenceDiagram
    participant App as "Application"
    participant MRM as "memory_reservation_manager"
    participant Strat as "reservation_request_strategy"
    participant MS as "memory_space"
    participant Res as "reservation"
    
    App->>MRM: request_reservation(strategy, size)
    MRM->>Strat: get_candidates()
    Strat-->>MRM: vector<memory_space*>
    
    MRM->>MRM: select_memory_space_and_make_reservation()
    
    alt Fast Path: Memory Available
        MRM->>MS: make_reservation(size)
        MS->>MS: Check available memory
        MS->>Res: create reservation
        Res-->>MS: unique_ptr<reservation>
        MS-->>MRM: unique_ptr<reservation>
        MRM-->>App: unique_ptr<reservation>
    else Slow Path: Memory Unavailable
        MRM->>MS: make_reservation(size)
        MS-->>MRM: nullptr
        MRM->>MRM: wait on _wait_cv
        Note over MRM: Blocks until memory<br/>becomes available
        MRM->>MS: make_reservation(size) [retry]
        MS->>Res: create reservation
        Res-->>MS: unique_ptr<reservation>
        MS-->>MRM: unique_ptr<reservation>
        MRM-->>App: unique_ptr<reservation>
    end
    
    Note over App: Use reservation for<br/>allocations
    
    App->>Res: destroy reservation
    Res->>MS: release memory
    MS->>MRM: notify_one() on _wait_cv
```

**Diagram: Reservation Request Sequence**

The manager uses a two-phase approach:
1. **Fast path**: Immediately try to make a reservation on candidate spaces using `make_reservation_or_null()` (non-blocking)
2. **Slow path**: If fast path fails, acquire `_wait_mutex` and block on `_wait_cv` until another thread releases memory

When a reservation is destroyed, the underlying `memory_space` notifies the manager's condition variable, potentially waking blocked threads.

**Sources:** [src/memory/memory_reservation_manager.cpp:172-191](), [src/memory/memory_reservation_manager.cpp:308-335]()

---

## Configuration and Initialization

The `memory_reservation_manager` is constructed from a vector of `memory_space_config` objects. The configuration pattern allows fine-grained control over each memory space:

```mermaid
graph TB
    subgraph "Configuration Phase"
        CONFIG["reservation_manager_configurator<br/>Builder pattern"]
        TOPO["topology_discovery<br/>Detect hardware"]
        CONFIGS["vector~memory_space_config~<br/>Tier, device_id, limits"]
    end
    
    subgraph "Construction Phase"
        MRM["memory_reservation_manager<br/>constructor"]
        MS1["memory_space<br/>GPU device 0"]
        MS2["memory_space<br/>HOST NUMA 0"]
        MS3["memory_space<br/>DISK partition 0"]
    end
    
    subgraph "Runtime Phase"
        LOOKUP["_memory_space_lookup<br/>Fast access"]
        TIER_MAP["_tier_to_memory_spaces<br/>Tier-based queries"]
    end
    
    CONFIG -->|"build_with_topology()"| TOPO
    TOPO -->|"generate configs"| CONFIGS
    CONFIGS -->|"constructor arg"| MRM
    MRM -->|"create"| MS1
    MRM -->|"create"| MS2
    MRM -->|"create"| MS3
    MRM -->|"build_lookup_tables()"| LOOKUP
    MRM -->|"build_lookup_tables()"| TIER_MAP
```

**Diagram: Configuration and Initialization Flow**

### memory_space_config

Each configuration specifies:

| Field | Type | Description |
|-------|------|-------------|
| `tier` | `Tier` | Memory tier (GPU, HOST, or DISK) |
| `device_id` | `int` | Device identifier within tier |
| `memory_limit` | `size_t` | Maximum reservable memory |
| `memory_capacity` | `size_t` | Total device memory (defaults to limit) |
| `downgrade_tigger_threshold` | `float` | Usage ratio triggering downgrade (default 0.75) |
| `downgrade_stop_threshold` | `float` | Usage ratio to stop downgrade (default 0.65) |
| `mr_factory_fn` | `DeviceMemoryResourceFactoryFn` | Factory for creating allocators |

The `mr_factory_fn` is a callable that creates the appropriate memory resource type:
- For GPU: Returns `reservation_aware_resource_adaptor` wrapping RMM's CUDA memory resource
- For HOST: Returns `fixed_size_host_memory_resource` with NUMA-aware pinned allocations
- For DISK: Not typically used (disk I/O handles differently)

**Sources:** [include/memory/memory_reservation_manager.hpp:191-212](), [src/memory/memory_reservation_manager.cpp:150-170]()

### Example: Single-Device Configuration

```cpp
// From test suite
reservation_manager_configurator builder;
builder.set_gpu_usage_limit(2ULL << 30);  // 2 GB per GPU
builder.set_reservation_limit_ratio_per_gpu(0.75);
builder.set_capacity_per_numa_node(4ULL << 30);  // 4 GB per NUMA node
builder.set_host_id_to_numa_maps({{0, -1}});  // GPU 0 -> NUMA node -1 (auto)
builder.set_reservation_limit_ratio_per_numa_node(0.75);

auto space_configs = builder.build_with_topology();
auto manager = std::make_unique<memory_reservation_manager>(
    std::move(space_configs)
);
```

**Sources:** [test/memory/test_memory_reservation_manager.cpp:57-68]()

---

## Memory Accounting and Queries

The manager provides comprehensive memory accounting at both tier-level and system-wide granularity:

```mermaid
graph TB
    subgraph "Per-memory_space Queries"
        MS["memory_space"]
        MS_AVAIL["get_available_memory()"]
        MS_RESERVED["get_total_reserved_memory()"]
        MS_COUNT["get_active_reservation_count()"]
    end
    
    subgraph "Tier-Level Aggregations"
        TIER["memory_reservation_manager"]
        TIER_AVAIL["get_available_memory_for_tier(tier)"]
        TIER_RESERVED["get_total_reserved_memory_for_tier(tier)"]
        TIER_COUNT["get_active_reservation_count_for_tier(tier)"]
    end
    
    subgraph "System-Wide Aggregations"
        SYS["memory_reservation_manager"]
        SYS_AVAIL["get_total_available_memory()"]
        SYS_RESERVED["get_total_reserved_memory()"]
        SYS_COUNT["get_active_reservation_count()"]
    end
    
    MS --> MS_AVAIL
    MS --> MS_RESERVED
    MS --> MS_COUNT
    
    MS_AVAIL -.aggregates.-> TIER_AVAIL
    MS_RESERVED -.aggregates.-> TIER_RESERVED
    MS_COUNT -.aggregates.-> TIER_COUNT
    
    TIER_AVAIL -.aggregates.-> SYS_AVAIL
    TIER_RESERVED -.aggregates.-> SYS_RESERVED
    TIER_COUNT -.aggregates.-> SYS_COUNT
```

**Diagram: Memory Accounting Hierarchy**

### Query Methods

| Method | Scope | Returns |
|--------|-------|---------|
| `memory_space::get_available_memory()` | Single device | Free memory in bytes |
| `memory_space::get_total_reserved_memory()` | Single device | Reserved memory in bytes |
| `memory_space::get_active_reservation_count()` | Single device | Number of active reservations |
| `get_available_memory_for_tier(Tier)` | All devices in tier | Sum of available memory |
| `get_total_reserved_memory_for_tier(Tier)` | All devices in tier | Sum of reserved memory |
| `get_active_reservation_count_for_tier(Tier)` | All devices in tier | Sum of reservation counts |
| `get_total_available_memory()` | All devices | System-wide available memory |
| `get_total_reserved_memory()` | All devices | System-wide reserved memory |
| `get_active_reservation_count()` | All devices | System-wide reservation count |

**Sources:** [include/memory/memory_reservation_manager.hpp:244-274](), [src/memory/memory_reservation_manager.cpp:245-306]()

---

## Thread Safety and Concurrency

The memory management subsystem is designed for multi-threaded environments with the following guarantees:

### Reservation Request Synchronization

The `memory_reservation_manager` uses a mutex and condition variable for cross-space coordination:

```mermaid
graph TB
    subgraph "Thread A"
        A1["request_reservation()"]
        A2["Fast path: try immediate"]
        A3["Slow path: acquire _wait_mutex"]
        A4["wait on _wait_cv"]
        A5["Retry reservation"]
    end
    
    subgraph "Thread B"
        B1["request_reservation()"]
        B2["Success: get reservation"]
        B3["Use reservation"]
        B4["~reservation() destructor"]
        B5["Return memory to space"]
        B6["notify_one() on _wait_cv"]
    end
    
    A1 --> A2
    A2 -->|"No space available"| A3
    A3 --> A4
    
    B1 --> B2
    B2 --> B3
    B3 --> B4
    B4 --> B5
    B5 --> B6
    B6 -.wakes.-> A4
    A4 --> A5
```

**Diagram: Concurrent Reservation Coordination**

- **`_wait_mutex`**: Protects the condition variable and ensures only one thread blocks/wakes at a time
- **`_wait_cv`**: Allows threads to wait for memory availability without busy-waiting
- Each `memory_space` has internal synchronization for its reservation count and available memory

### Lock-Free Fast Path

When memory is available, `request_reservation()` completes without acquiring the wait mutex. This optimizes the common case where contention is low.

**Sources:** [include/memory/memory_reservation_manager.hpp:301-302](), [src/memory/memory_reservation_manager.cpp:172-191]()

---

## Integration with Other Subsystems

The Memory Management Subsystem serves as the foundation for higher-level cuCascade components:

```mermaid
graph TB
    subgraph "Data Representation Layer"
        HOST_REP["host_table_representation"]
        GPU_REP["gpu_table_representation"]
        CONV["representation_converter_registry"]
    end
    
    subgraph "Memory Management Layer"
        MRM["memory_reservation_manager"]
        RES["reservation"]
    end
    
    subgraph "Allocator Layer"
        GPU_MR["reservation_aware_resource_adaptor"]
        HOST_MR["fixed_size_host_memory_resource"]
    end
    
    CONV -->|"request_reservation()<br/>for conversions"| MRM
    HOST_REP -->|"allocate_multiple_blocks()"| HOST_MR
    GPU_REP -->|"allocate()<br/>on cuda_stream"| GPU_MR
    
    MRM -->|"returns"| RES
    RES -->|"get_memory_resource_of<Tier>()"| GPU_MR
    RES -->|"get_memory_resource_of<Tier>()"| HOST_MR
```

**Diagram: Integration with Data Representation Layer**

- **Data Representation Converters** ([#5.4](#5.4)): Request reservations when converting data between tiers
- **GPU Table Representation** ([#5.2](#5.2)): Uses GPU memory resources from reservations for cuDF table allocations
- **Host Table Representation** ([#5.3](#5.3)): Uses HOST memory resources for block-based allocations

**Sources:** [include/memory/memory_reservation_manager.hpp:1-307](), test usage patterns throughout [test/memory/test_memory_reservation_manager.cpp]()

---

## Source Files Overview

The Memory Management Subsystem is implemented across multiple source files:

| File | Purpose |
|------|---------|
| `include/memory/memory_reservation_manager.hpp` | Manager and strategy interfaces |
| `src/memory/memory_reservation_manager.cpp` | Manager implementation |
| `include/memory/memory_space.hpp` | Memory space abstraction |
| `src/memory/memory_space.cpp` | Memory space implementation |
| `include/memory/memory_reservation.hpp` | Reservation RAII wrapper |
| `src/memory/memory_reservation.cpp` | Reservation implementation |
| `src/memory/reservation_aware_resource_adaptor.cpp` | GPU allocator with reservation tracking |
| `src/memory/fixed_size_host_memory_resource.cpp` | HOST block-based allocator |
| `src/memory/numa_region_pinned_host_allocator.cpp` | NUMA-aware pinned memory |
| `src/memory/topology_discovery.cpp` | Hardware detection |
| `src/memory/reservation_manager_configurator.cpp` | Configuration builder |
| `src/memory/oom_handling_policy.cpp` | Out-of-memory policies |
| `test/memory/test_memory_reservation_manager.cpp` | Comprehensive test suite |

**Sources:** [src/memory/CMakeLists.txt:18-33]()

---

